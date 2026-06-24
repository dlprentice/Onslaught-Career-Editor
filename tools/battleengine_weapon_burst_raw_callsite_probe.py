#!/usr/bin/env python3
"""Check raw no-function callsites into the shared burst helper.

This bounded static RE probe consumes an ignored read-only Ghidra instruction
window export for the two raw no-function callsites into
`CGeneralVolume__SpawnBurstFromPresetWithFallback` at `0x00506010`.

It records whether the current instruction windows still look like unowned
shared-context paths rather than an obvious Weapon/BattleEngine function owner.
It does not mutate Ghidra and does not claim exact `CWeapon::Fire` or
`CBattleEngine::WeaponFired` identity.
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
BASE = ROOT / "subagents" / "battleengine-weapon-burst-raw-callsites" / "current"
DEFAULT_INSTRUCTIONS = BASE / "raw_callsite_instructions.tsv"
DEFAULT_OUT = BASE / "weapon-burst-raw-callsites.json"

TARGET_HELPER = "0x00506010"
EXPECTED_CALLSITES = ("0x0044e093", "0x004f4bd6")
WEAPON_NAME_TOKENS = ("weapon", "battleengine")

EXPECTED_SIGNALS = {
    "0x0044e093": {
        "precheckCall": "0x00509f70",
        "listField": "0x1a4",
        "rangeLow": "0x18",
        "rangeHigh": "0x1b",
    },
    "0x004f4bd6": {
        "optionalCall": "0x00492020",
        "thresholdGlobal": "0x005d8cc0",
        "entityField": "0x70",
        "lookupCall": "0x0050ff10",
        "setupCall": "0x0048dcf0",
    },
}


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value in {"", "<none>", "none"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def rows_for_target(rows: list[dict[str, str]], target: str) -> list[dict[str, str]]:
    normalized = normalize_address(target)
    return [row for row in rows if normalize_address(row.get("target_addr", "")) == normalized]


def row_text(row: dict[str, str]) -> str:
    return " ".join(
        [
            row.get("function_name", ""),
            row.get("mnemonic", ""),
            row.get("operands", ""),
        ]
    ).lower()


def contains(rows: list[dict[str, str]], token: str) -> bool:
    token = token.lower()
    return any(token in row_text(row) for row in rows)


def public_row(row: dict[str, str]) -> dict[str, str]:
    return {
        "targetAddress": normalize_address(row.get("target_addr", "")),
        "role": row.get("role", ""),
        "instructionAddress": normalize_address(row.get("instruction_addr", "")),
        "functionEntry": normalize_address(row.get("function_entry", "")),
        "functionName": row.get("function_name", ""),
        "mnemonic": row.get("mnemonic", ""),
        "operands": row.get("operands", ""),
    }


def signal_summary(target: str, rows: list[dict[str, str]]) -> dict[str, bool]:
    if target == "0x0044e093":
        expected = EXPECTED_SIGNALS[target]
        return {
            "hasPrecheckCall": contains(rows, expected["precheckCall"]),
            "hasListField1a4": contains(rows, expected["listField"]),
            "hasRangeLow18": contains(rows, expected["rangeLow"]),
            "hasRangeHigh1b": contains(rows, expected["rangeHigh"]),
        }
    expected = EXPECTED_SIGNALS[target]
    return {
        "hasFloatMath": any(row.get("mnemonic", "").upper() in {"FSQRT", "FCOMPP"} for row in rows),
        "hasOptionalCall": contains(rows, expected["optionalCall"]),
        "hasThresholdGlobal": contains(rows, expected["thresholdGlobal"]),
        "hasEntityField70": contains(rows, expected["entityField"]),
        "hasLookupCall": contains(rows, expected["lookupCall"]),
        "hasSetupCall": contains(rows, expected["setupCall"]),
    }


def build_report(*, instructions_path: Path = DEFAULT_INSTRUCTIONS) -> dict[str, object]:
    instructions_path = resolve(instructions_path)
    failures: list[str] = []
    if not instructions_path.is_file():
        failures.append(f"missing instruction export: {relative(instructions_path)}")

    rows = read_tsv(instructions_path)
    missing_targets: list[str] = []
    callsite_reports: dict[str, object] = {}
    target_callsite_count = 0
    owned_function_rows: list[dict[str, str]] = []
    weapon_named_rows: list[dict[str, str]] = []

    for row in rows:
        function_entry = normalize_address(row.get("function_entry", ""))
        function_name = row.get("function_name", "")
        if function_entry != "<none>" or function_name != "<no_function>":
            owned_function_rows.append(public_row(row))
        lowered = function_name.lower()
        if any(token in lowered for token in WEAPON_NAME_TOKENS):
            weapon_named_rows.append(public_row(row))

    for target in EXPECTED_CALLSITES:
        target_rows = rows_for_target(rows, target)
        if not target_rows:
            missing_targets.append(target)
            continue
        target_rows_at_call = [
            row
            for row in target_rows
            if row.get("role", "") == "TARGET"
            and normalize_address(row.get("instruction_addr", "")) == target
            and row.get("mnemonic", "").upper() == "CALL"
            and normalize_address(row.get("operands", "")) == TARGET_HELPER
        ]
        if not target_rows_at_call:
            failures.append(f"missing target CALL {target} -> {TARGET_HELPER}")
        else:
            target_callsite_count += 1

        signals = signal_summary(target, target_rows)
        missing_signals = sorted(name for name, observed in signals.items() if not observed)
        if missing_signals:
            failures.append(f"missing expected context signals for {target}: {missing_signals}")

        callsite_reports[target] = {
            "rowCount": len(target_rows),
            "hasTargetCallToHelper": bool(target_rows_at_call),
            "signals": signals,
            "functionNames": sorted({row.get("function_name", "") for row in target_rows}),
        }

    if missing_targets:
        failures.append(f"missing expected raw callsite targets: {missing_targets}")
    if owned_function_rows:
        failures.append(f"expected raw no-function rows only, found owned function rows: {len(owned_function_rows)}")
    if weapon_named_rows:
        failures.append(f"unexpected Weapon/BattleEngine-named rows: {len(weapon_named_rows)}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "battleengine-weapon-burst-raw-callsites.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "raw-callsites-unowned-shared-context"
        if status == "PASS"
        else "blocked-or-unexpected-raw-callsite-context",
        "inputs": {
            "instructions": relative(instructions_path),
        },
        "targetHelper": TARGET_HELPER,
        "expectedCallsites": list(EXPECTED_CALLSITES),
        "instructionRowCount": len(rows),
        "targetCallsiteCount": target_callsite_count,
        "ownedFunctionRows": len(owned_function_rows),
        "weaponNamedRows": weapon_named_rows,
        "callsites": callsite_reports,
        "failures": failures,
        "whatIsProven": [
            "The current read-only instruction-window export has both raw callsites into 0x00506010.",
            "Both checked callsite windows are currently outside Ghidra-owned function rows in this export.",
            "The checked windows contain shared context signals rather than an obvious Weapon- or BattleEngine-named owner.",
        ],
        "notProven": [
            "This does not create, rename, or mutate a Ghidra function boundary.",
            "This does not prove exact CWeapon::Fire or CBattleEngine::WeaponFired identity.",
            "This does not prove whether retail weapon fire clears stealth.",
            "This does not rule out indirect, virtual-dispatch, callback, inlined, or runtime-only weapon-fire behavior elsewhere.",
            "This does not patch or launch BEA.exe and does not prove runtime cloak/fire behavior.",
        ],
        "privacy": "Report stores repo-relative filenames, public addresses, instruction counts, current function names, and proof boundaries only; raw Ghidra exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
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

    report = build_report(instructions_path=args.instructions)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine weapon burst raw callsite probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        print(f"Instruction rows: {report['instructionRowCount']}")
        print(f"Target callsites: {report['targetCallsiteCount']}")
        print(f"Owned function rows: {report['ownedFunctionRows']}")
        print(f"Weapon/BattleEngine-named rows: {len(report['weaponNamedRows'])}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
