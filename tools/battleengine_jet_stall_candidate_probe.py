#!/usr/bin/env python3
"""Validate a public-safe jet energy/stall retail candidate bridge.

This read-only probe checks Stuart-source jet movement anchors against a fresh
ignored Ghidra decompile export for CMonitor__Process plus a private read-only
constant scan. The result is intentionally partial: it supports a retail
candidate cluster, not exact source method identity.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references" / "Onslaught" / "BattleEngineJetPart.cpp"
DEFAULT_DECOMPILE = ROOT / "subagents" / "battleengine-jet-stall-candidate" / "current" / "decompile"
DEFAULT_CONSTANTS = ROOT / "subagents" / "battleengine-jet-stall-candidate" / "current" / "constants.json"
DEFAULT_OUT = ROOT / "subagents" / "battleengine-jet-stall-candidate" / "current" / "jet-stall-candidate.json"

SOURCE_TOKENS = (
    "mMinAirEnergyCost",
    "mMaxAirEnergyCost",
    "mMainPart->mEnergy-=cost",
    "mMainPart->mTransformStartTime+2.5f<EVENT_MANAGER.GetTime()",
    "mMainPart->mVelocity.MagnitudeSq()<0.15f*0.15f",
    "mMainPart->mStallTime+2.5f<EVENT_MANAGER.GetTime()",
    "mMainPart->Morph();",
)

DECOMPILE_TOKENS = (
    "CMonitor__UpdateFlightWalkerTransitionState(param_1)",
    "_DAT_005d8c30 < *(float *)((int)param_1 + 0x118)",
    "*(float *)((int)param_1 + 0x280) = *(float *)((int)param_1 + 0x280) - _DAT_005d8c2c",
    "if (_DAT_005d8570 <=",
    "*(undefined4 *)((int)param_1 + 0x310) = 0",
    "*(int *)((int)param_1 + 0x310) + 1",
    "if (5 < iVar10)",
    "*(int *)param_1 + 0x110",
)

EXPECTED_CONSTANTS = {
    "energy_cost_subtract": ("0x005d8c2c", 0.015),
    "energy_gate_compare": ("0x005d8c30", -0.03),
    "stall_speed_squared_threshold": ("0x005d8570", 0.0001),
}


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalized(text: str) -> str:
    return "".join(text.split())


def token_hits(path: Path, tokens: tuple[str, ...], *, normalize: bool = False) -> dict[str, list[int]]:
    if not path.is_file():
        return {token: [] for token in tokens}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    hits: dict[str, list[int]] = {}
    if normalize:
        norm_lines = [normalized(line) for line in lines]
        for token in tokens:
            needle = normalized(token)
            hits[token] = [index + 1 for index, line in enumerate(norm_lines) if needle in line]
    else:
        for token in tokens:
            hits[token] = [index + 1 for index, line in enumerate(lines) if token in line]
    return hits


def read_index(decompile_dir: Path) -> list[dict[str, str]]:
    index = decompile_dir / "index.tsv"
    if not index.is_file():
        return []
    with index.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def find_decompile(decompile_dir: Path) -> Path:
    candidates = sorted(decompile_dir.glob("004081c0_CMonitor__Process.c"))
    return candidates[0] if candidates else decompile_dir / "004081c0_CMonitor__Process.c"


def load_constants(path: Path) -> dict[str, dict[str, object]]:
    if not path.is_file():
        return {}
    report = json.loads(path.read_text(encoding="utf-8"))
    return {item["name"]: item for item in report.get("values", [])}


def build_report(decompile_dir: Path, constants_path: Path) -> dict[str, object]:
    decompile = find_decompile(decompile_dir)
    index_rows = read_index(decompile_dir)
    source_hits = token_hits(SOURCE, SOURCE_TOKENS, normalize=True)
    decompile_hits = token_hits(decompile, DECOMPILE_TOKENS, normalize=True)
    constants = load_constants(constants_path)

    failures: list[str] = []
    if not SOURCE.is_file():
        failures.append(f"missing source file: {relative(SOURCE)}")
    if not decompile.is_file():
        failures.append(f"missing decompile file: {relative(decompile)}")
    if not index_rows:
        failures.append(f"missing or empty decompile index: {relative(decompile_dir / 'index.tsv')}")
    else:
        ok_rows = [
            row
            for row in index_rows
            if row.get("address", "").lower() == "0x004081c0"
            and row.get("name") == "CMonitor__Process"
            and row.get("status") == "OK"
        ]
        if not ok_rows:
            failures.append("decompile index lacks OK row for 0x004081c0 CMonitor__Process")
    failures.extend(f"missing source token: {token}" for token, lines in source_hits.items() if not lines)
    failures.extend(f"missing decompile token: {token}" for token, lines in decompile_hits.items() if not lines)
    for name, (expected_va, expected_float) in EXPECTED_CONSTANTS.items():
        item = constants.get(name)
        if not item:
            failures.append(f"missing constant: {name}")
            continue
        actual_va = str(item.get("va", "")).lower()
        actual_float = float(item.get("float", math.nan))
        if actual_va != expected_va:
            failures.append(f"{name} VA mismatch: expected {expected_va}, got {actual_va}")
        if not math.isfinite(actual_float) or abs(actual_float - expected_float) > 0.00001:
            failures.append(f"{name} float mismatch: expected {expected_float}, got {actual_float}")

    return {
        "schema": "battleengine-jet-stall-candidate.v1",
        "status": "pass" if not failures else "blocked",
        "sourceFile": relative(SOURCE),
        "decompileDir": relative(decompile_dir),
        "decompileFile": relative(decompile),
        "constantsFile": relative(constants_path),
        "sourceTokenLineHits": source_hits,
        "decompileTokenLineHits": decompile_hits,
        "constantChecks": {
            name: constants.get(name, {})
            for name in EXPECTED_CONSTANTS
        },
        "failures": failures,
        "whatIsProven": [
            "The source jet movement anchor still contains min/max air-energy cost, energy subtraction, low-speed stall entry, stall timer, and Morph fallback tokens.",
            "Fresh read-only Ghidra decompile for CMonitor__Process contains an energy-like subtract from offset 0x280 gated by _DAT_005d8c30 and _DAT_005d8c2c.",
            "Fresh read-only Ghidra decompile for CMonitor__Process contains a velocity-threshold path that resets or increments offset 0x310 and calls the vfunc at offset 0x110 after the counter exceeds 5.",
            "The read-only constant scan maps _DAT_005d8c2c to 0.015 and _DAT_005d8570 to approximately 0.0001 in .rdata.",
        ],
        "notProven": [
            "Exact source-to-retail identity for BattleEngineJetPart movement methods.",
            "Whether the retail CMonitor__Process cluster exactly corresponds to the source jet-energy/stall methods or an inlined/reorganized equivalent.",
            "Walker recharge source-to-retail identity.",
            "Runtime flight, stall, or forced walker transition behavior.",
            "Ghidra rename-map mutation.",
            "Rebuildable open-source gameplay implementation.",
        ],
        "privacy": "Report stores repo-relative paths, source token names, decompile token names, public addresses, constants, and line numbers only; raw decompile and constant JSON remain ignored under subagents/.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BattleEngine jet energy/stall candidate read-back evidence.")
    parser.add_argument("--check", action="store_true", help="run the candidate probe")
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE, help="ignored Ghidra decompile export dir")
    parser.add_argument("--constants", type=Path, default=DEFAULT_CONSTANTS, help="ignored read-only constant JSON")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    decompile_dir = args.decompile_dir if args.decompile_dir.is_absolute() else ROOT / args.decompile_dir
    constants_path = args.constants if args.constants.is_absolute() else ROOT / args.constants
    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}")
        return 1

    report = build_report(decompile_dir, constants_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine jet energy/stall candidate probe")
        print(f"Status: {report['status']}")
        print(f"Source tokens: {sum(1 for lines in report['sourceTokenLineHits'].values() if lines)}/{len(SOURCE_TOKENS)}")
        print(f"Decompile tokens: {sum(1 for lines in report['decompileTokenLineHits'].values() if lines)}/{len(DECOMPILE_TOKENS)}")
        if report["failures"]:
            for failure in report["failures"]:
                print(f"- FAIL: {failure}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
