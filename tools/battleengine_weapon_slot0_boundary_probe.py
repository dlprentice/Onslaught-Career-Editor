#!/usr/bin/env python3
"""Check the raw boundary shape around weapon vtable slot 0.

This bounded static RE probe consumes ignored read-only disassembly exports for
the weapon construction candidate. It verifies the current raw vtable slot-0
stub at `0x00506930`, its inner body call at `0x005069f0`, and the checked
inner body return/post-return boundary. It does not create or rename a Ghidra
function and does not claim exact `CWeapon::Fire` or `CBattleEngine::WeaponFired`
identity.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "battleengine-weapon-construction-candidates" / "current"
DEFAULT_STUB = BASE / "vtable" / "slot0_00506930_function_disasm.tsv"
DEFAULT_BODY = BASE / "vtable" / "slot0_005069f0_body_disasm.tsv"
DEFAULT_OUT = BASE / "weapon-slot0-boundary.json"

OUTER_START = "0x00506930"
INNER_START = "0x005069f0"
OUTER_RET_ADDRESSES = {"0x005069a3", "0x005069ed"}
INNER_TERMINAL_RET = "0x005078ab"
FIRST_POST_RET = "0x005078b0"
EXPECTED_INNER_CALL_TARGETS = {
    "0x0040c2e0": "CEngine__CanSpawnBurstForResolvedEntry",
    "0x0050f7a0": "CWorldPhysicsManager__CreateProjectile",
    "0x004daab0": "CEngine__SetProjectileTargetReader",
    "0x00407060": "CEngine__MoveBurstReaderToCooldownSet",
    "0x0040c340": "CEngine__RandomizeBurstOffsetsAndAccumulateRange",
}
EXPECTED_INNER_EXIT_TARGETS = {"0x0050787d", "0x00507891", "0x00507893"}
STEALTH_RESET_TOKENS = ("0x4ac", "0x5d4", "0x5d8", "0x5dc", "00406fc0", "00406560")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def row_by_address(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get("address", "")): row for row in rows}


def call_targets(rows: list[dict[str, str]]) -> list[str]:
    targets: list[str] = []
    for row in rows:
        if row.get("mnemonic", "").upper() != "CALL":
            continue
        match = re.search(r"0x[0-9a-fA-F]{8}", row.get("operands", ""))
        if match:
            targets.append(normalize_address(match.group(0)))
    return targets


def branch_targets(rows: list[dict[str, str]]) -> list[str]:
    targets: list[str] = []
    for row in rows:
        if not row.get("mnemonic", "").upper().startswith("J"):
            continue
        match = re.search(r"0x[0-9a-fA-F]{8}", row.get("operands", ""))
        if match:
            targets.append(normalize_address(match.group(0)))
    return targets


def addresses(rows: list[dict[str, str]]) -> list[str]:
    return [normalize_address(row.get("address", "")) for row in rows if row.get("address")]


def text_for_tokens(rows: list[dict[str, str]]) -> str:
    return "\n".join(
        "\t".join(row.get(key, "") for key in ("address", "bytes", "mnemonic", "operands"))
        for row in rows
    ).lower()


def build_report(
    *,
    stub_path: Path = DEFAULT_STUB,
    body_path: Path = DEFAULT_BODY,
) -> dict[str, object]:
    stub_path = resolve(stub_path)
    body_path = resolve(body_path)

    failures: list[str] = []
    if not stub_path.is_file():
        failures.append(f"missing outer stub disassembly: {relative(stub_path)}")
    if not body_path.is_file():
        failures.append(f"missing inner body disassembly: {relative(body_path)}")

    stub_rows = read_tsv(stub_path)
    body_rows = read_tsv(body_path)
    stub_map = row_by_address(stub_rows)
    body_map = row_by_address(body_rows)

    stub_addresses = addresses(stub_rows)
    body_addresses = addresses(body_rows)
    stub_call_targets = sorted(set(call_targets(stub_rows)))
    body_call_targets = sorted(set(call_targets(body_rows)))
    body_branch_targets = sorted(set(branch_targets(body_rows)))

    if OUTER_START not in stub_map:
        failures.append(f"missing outer slot0 start {OUTER_START}")
    for reg in ("EBX", "ESI", "EDI"):
        if not any(row.get("mnemonic", "").upper() == "PUSH" and row.get("operands", "") == reg for row in stub_rows):
            failures.append(f"missing outer stub PUSH {reg}")
    if not any("0x1389" in row.get("operands", "").lower() for row in stub_rows):
        failures.append("missing outer stub 0x1389 event/tag compare")
    if INNER_START not in stub_call_targets:
        failures.append("missing outer stub call to 0x005069f0")
    missing_outer_rets = sorted(OUTER_RET_ADDRESSES - set(stub_addresses))
    if missing_outer_rets:
        failures.append(f"missing outer stub return addresses: {missing_outer_rets}")

    if INNER_START not in body_map:
        failures.append(f"missing inner body start {INNER_START}")
    if body_map.get(INNER_START, {}).get("mnemonic", "").upper() != "MOV":
        failures.append("inner body start does not begin with expected SEH MOV prologue")
    for target, name in EXPECTED_INNER_CALL_TARGETS.items():
        if target not in body_call_targets:
            failures.append(f"missing inner body call target {target} ({name})")
    missing_exit_targets = sorted(EXPECTED_INNER_EXIT_TARGETS - set(body_branch_targets))
    if missing_exit_targets:
        failures.append(f"missing expected inner body branch-exit targets: {missing_exit_targets}")
    if body_map.get(INNER_TERMINAL_RET, {}).get("mnemonic", "").upper() != "RET":
        failures.append(f"missing inner body terminal RET at {INNER_TERMINAL_RET}")

    first_post_ret = ""
    if INNER_TERMINAL_RET in body_addresses:
        idx = body_addresses.index(INNER_TERMINAL_RET)
        if idx + 1 < len(body_addresses):
            first_post_ret = body_addresses[idx + 1]
    if first_post_ret != FIRST_POST_RET:
        failures.append(f"expected first post-RET row {FIRST_POST_RET}, got {first_post_ret or '<none>'}")

    combined_text = text_for_tokens(stub_rows + body_rows)
    unexpected_stealth_tokens = [token for token in STEALTH_RESET_TOKENS if token in combined_text]
    if unexpected_stealth_tokens:
        failures.append(f"unexpected stealth/AddProjectile token references in boundary rows: {unexpected_stealth_tokens}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "battleengine-weapon-slot0-boundary.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "raw-slot0-boundary-candidate"
        if status == "PASS"
        else "blocked-or-unexpected-raw-slot0-boundary",
        "inputs": {
            "outerStub": relative(stub_path),
            "innerBody": relative(body_path),
        },
        "outerStub": {
            "startAddress": OUTER_START,
            "innerCallTarget": INNER_START if INNER_START in stub_call_targets else "",
            "returnAddresses": sorted(OUTER_RET_ADDRESSES),
            "observedCallTargets": stub_call_targets,
        },
        "innerBody": {
            "startAddress": INNER_START,
            "terminalRetAddress": INNER_TERMINAL_RET
            if body_map.get(INNER_TERMINAL_RET, {}).get("mnemonic", "").upper() == "RET"
            else "",
            "firstPostRetAddress": first_post_ret,
            "expectedBranchExitTargets": sorted(EXPECTED_INNER_EXIT_TARGETS),
            "observedBranchTargets": body_branch_targets,
        },
        "innerBodyCallTargets": body_call_targets,
        "expectedInnerBodyCallTargets": EXPECTED_INNER_CALL_TARGETS,
        "unexpectedStealthResetTokens": unexpected_stealth_tokens,
        "failures": failures,
        "whatIsProven": [
            "The current read-only disassembly exports expose an outer raw slot-0 stub at 0x00506930.",
            "The outer stub calls an inner body at 0x005069f0 and has two observed RET 0x4 exits in the checked range.",
            "The inner body reaches the expected projectile creation/target helper-family calls and has a terminal RET at 0x005078ab before the first post-return row at 0x005078b0.",
            "The checked raw boundary rows do not contain direct CBattleEngine__AddProjectile/helper addresses or tracked stealth-adjacent offset tokens.",
        ],
        "notProven": [
            "This does not create, rename, or mutate a Ghidra function boundary.",
            "This does not prove exact CWeapon::Fire or CBattleEngine::WeaponFired identity.",
            "This does not prove retail weapon fire never clears stealth.",
            "This does not rule out an indirect, virtual-dispatch, callback, inlined, or runtime-only stealth reset elsewhere.",
            "This does not patch or launch BEA.exe and does not prove runtime cloak/fire behavior.",
        ],
        "privacy": "Report stores repo-relative filenames, public addresses, call targets, counts, and proof boundaries only; raw disassembly exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stub", type=Path, default=DEFAULT_STUB)
    parser.add_argument("--body", type=Path, default=DEFAULT_BODY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    out = resolve(args.out)
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}", file=sys.stderr)
        return 1

    report = build_report(stub_path=args.stub, body_path=args.body)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine weapon slot0 boundary probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        print(f"Outer stub inner call: {report['outerStub']['innerCallTarget'] or '<missing>'}")
        print(f"Inner terminal RET: {report['innerBody']['terminalRetAddress'] or '<missing>'}")
        print(f"First post-RET row: {report['innerBody']['firstPostRetAddress'] or '<missing>'}")
        print(f"Unexpected stealth/AddProjectile tokens: {len(report['unexpectedStealthResetTokens'])}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
