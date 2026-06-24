#!/usr/bin/env python3
"""Check whether the current projectile helper decompile contains stealth reset writes.

This is a bounded static RE probe. It consumes ignored Ghidra decompile output
for the already named retail helper at 0x00406560, confirms projectile/targeting
tokens are present, and records that no source-style stealth reset write was
observed inside that helper. Absence in this one helper is narrowing evidence,
not proof that retail weapon fire never clears stealth elsewhere.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references" / "Onslaught" / "BattleEngine.cpp"
DEFAULT_DECOMPILE = ROOT / "subagents" / "battleengine-helper-ghidra-readback" / "current" / "decompile"
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "battleengine-projectile-helper-stealth-scan"
    / "current"
    / "projectile-helper-stealth-scan.json"
)

HELPER_ADDRESS = "0x00406560"
HELPER_NAME = "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles"
HELPER_FILE = "00406560_CBattleEngine__UpdateAutoTargetSetAndFireProjectiles.c"

SOURCE_TOKENS = (
    "CBattleEngine::WeaponFired",
    "mWalkerPart->WeaponFired(",
    "mJetPart->WeaponFired(",
    "mStealth=0.0f;",
)

REQUIRED_HELPER_TOKENS = (
    "CBattleEngine__GetIndexedEntry",
    "CBattleEngine__IsIndexedEntryUsable",
    "CGeneralVolume__ResolveCurrentOrFallbackEntry",
    "CBattleEngine__IsResolvedEntryUsable",
    "CBattleEngine__CalcUnitOverCrossHair",
    "CBattleEngine__IsWeaponModeCompatibleWithMountState",
    "CBattleEngine__DoesTargetMaskMatchProfileByDistance",
    "CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
    "CBattleEngine__AddProjectile",
    "CSPtrSet__Remove",
)

STEALTH_CONTEXT_TOKENS = (
    "_DAT_005d85fc",
    "CBattleEngine__GetProfileField9CByDistance",
)

STEALTH_WRITE_TOKENS = (
    "*(undefined4 *)(param_1 + 0x4ac) = 0",
    "*(undefined4 *)(param_1 + 0x5d4) = 0",
    "*(undefined4 *)(param_1 + 0x5d8) = 0",
    "*(undefined4 *)(param_1 + 0x5dc) = 0",
    "*(float *)(param_1 + 0x4ac) = 0",
    "*(float *)(param_1 + 0x5d4) = 0",
    "*(float *)(param_1 + 0x5d8) = 0",
    "*(float *)(param_1 + 0x5dc) = 0",
)

STEALTH_ADJACENT_OFFSET_TOKENS = (
    "param_1 + 0x4ac",
    "param_1 + 0x5d4",
    "param_1 + 0x5d8",
    "param_1 + 0x5dc",
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalized(text: str) -> str:
    return "".join(text.split())


def line_hits(path: Path, tokens: tuple[str, ...], *, normalize: bool = False) -> dict[str, list[int]]:
    if not path.is_file():
        return {token: [] for token in tokens}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if normalize:
        norm_lines = [normalized(line) for line in lines]
        return {
            token: [index + 1 for index, line in enumerate(norm_lines) if normalized(token) in line]
            for token in tokens
        }
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def read_index(decompile_dir: Path) -> list[dict[str, str]]:
    index_path = decompile_dir / "index.tsv"
    if not index_path.is_file():
        return []
    with index_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def helper_index_row(index_rows: list[dict[str, str]]) -> dict[str, str] | None:
    for row in index_rows:
        if row.get("address", "").lower() == HELPER_ADDRESS and row.get("name") == HELPER_NAME:
            return row
    return None


def nonempty_hits(hits: dict[str, list[int]]) -> dict[str, list[int]]:
    return {token: lines for token, lines in hits.items() if lines}


def build_report(decompile_dir: Path = DEFAULT_DECOMPILE, source: Path = SOURCE) -> dict[str, object]:
    decompile_dir = decompile_dir if decompile_dir.is_absolute() else ROOT / decompile_dir
    source = source if source.is_absolute() else ROOT / source
    helper_path = decompile_dir / HELPER_FILE
    index_rows = read_index(decompile_dir)
    index_row = helper_index_row(index_rows)

    source_hits = line_hits(source, SOURCE_TOKENS, normalize=True)
    helper_hits = line_hits(helper_path, REQUIRED_HELPER_TOKENS, normalize=True)
    stealth_context_hits = line_hits(helper_path, STEALTH_CONTEXT_TOKENS, normalize=True)
    stealth_write_hits = nonempty_hits(line_hits(helper_path, STEALTH_WRITE_TOKENS, normalize=True))
    stealth_adjacent_offset_hits = nonempty_hits(
        line_hits(helper_path, STEALTH_ADJACENT_OFFSET_TOKENS, normalize=True)
    )

    failures: list[str] = []
    if not source.is_file():
        failures.append(f"missing source file: {relative(source)}")
    if not helper_path.is_file():
        failures.append(f"missing decompile file: {relative(helper_path)}")
    if index_row is None:
        failures.append(f"missing index row for {HELPER_ADDRESS} {HELPER_NAME}")
    elif index_row.get("status") != "OK":
        failures.append(f"index row status is {index_row.get('status')}")
    elif HELPER_NAME not in index_row.get("signature", ""):
        failures.append("helper index signature does not contain current function name")

    failures.extend(f"missing source token: {token}" for token, lines in source_hits.items() if not lines)
    failures.extend(f"missing helper token: {token}" for token, lines in helper_hits.items() if not lines)
    failures.extend(
        f"missing stealth context token: {token}"
        for token, lines in stealth_context_hits.items()
        if not lines
    )
    failures.extend(
        f"source-style stealth write observed in projectile helper: {token}"
        for token in stealth_write_hits
    )

    return {
        "schema": "battleengine-projectile-helper-stealth-scan.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "sourceFile": relative(source),
        "decompileDir": relative(decompile_dir),
        "helper": {
            "address": HELPER_ADDRESS,
            "name": HELPER_NAME,
            "file": relative(helper_path),
            "indexStatus": None if index_row is None else index_row.get("status"),
            "signature": None if index_row is None else index_row.get("signature"),
        },
        "sourceTokenLineHits": source_hits,
        "helperTokenLineHits": helper_hits,
        "stealthContextTokenLineHits": stealth_context_hits,
        "stealthWriteTokenHits": stealth_write_hits,
        "stealthAdjacentOffsetHits": stealth_adjacent_offset_hits,
        "helperClassification": (
            "projectile-targeting-helper-no-stealth-reset-observed"
            if not failures and not stealth_write_hits
            else "blocked-or-stealth-write-observed"
        ),
        "failures": failures,
        "whatIsProven": [
            "Stuart source still contains a WeaponFired wrapper that checks walker and jet parts, then sets mStealth to 0.0f when either part fired.",
            "The current 0x00406560 retail decompile still contains target-entry resolution, target filtering, forward-target selection, tracked-set removal, and CBattleEngine__AddProjectile calls.",
            "The current 0x00406560 retail decompile still contains the known 0.01 stealth-style target-range context token.",
            "No source-style writes to the currently tracked stealth-adjacent offsets 0x4ac, 0x5d4, 0x5d8, or 0x5dc were observed inside the current 0x00406560 decompile.",
        ],
        "notProven": [
            "This does not identify the exact retail CBattleEngine::WeaponFired implementation.",
            "This does not prove retail weapon fire never clears stealth; the reset may be in a wrapper, callback, inlined part method, or runtime-only path outside 0x00406560.",
            "This does not prove runtime cloak activation, target-lock behavior, or weapon-fire decloak behavior.",
            "This does not mutate BEA.exe, launch the game, or mutate the Ghidra project.",
        ],
        "privacy": "Report stores repo-relative paths, public addresses, function names, token labels, and line numbers only; raw decompile remains ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}", file=sys.stderr)
        return 1

    report = build_report(args.decompile_dir, args.source)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine projectile helper stealth scan probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['helperClassification']}")
        print(f"Stealth write tokens observed: {len(report['stealthWriteTokenHits'])}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
