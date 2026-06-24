#!/usr/bin/env python3
"""Check direct xrefs into the shared burst/projectile helper at 0x00506010.

This bounded static RE probe consumes ignored read-only Ghidra xref and caller
index exports. It records whether `CGeneralVolume__SpawnBurstFromPresetWithFallback`
is reached by a broad shared effect/burst caller set rather than by an obvious
weapon-specific direct caller.

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
BASE = ROOT / "subagents" / "battleengine-weapon-burst-caller-xrefs" / "current"
DEFAULT_XREFS = BASE / "burst_caller_xrefs.tsv"
DEFAULT_CALLER_INDEX = BASE / "caller-decompile" / "index.tsv"
DEFAULT_OUT = BASE / "weapon-burst-caller-xrefs.json"

TARGET_ADDRESS = "0x00506010"
TARGET_NAME = "CGeneralVolume__SpawnBurstFromPresetWithFallback"
EXPECTED_ROW_COUNT = 10
EXPECTED_NAMED_CALLERS = {
    "0x004fc080": "CUnitAI__TrySpawnOrFinalizeAttachedUnit",
    "0x004decc0": "CSentinel__UpdateFlamethrowers",
    "0x00411bf0": "CEngine_Unk_0050a080__Wrapper_00411bf0",
    "0x00413cf0": "CGeneralVolume__UpdateCurrentEntryProgressAndRefresh",
    "0x00411b90": "CEngine_Unk_00506010__Wrapper_00411b90",
    "0x00413cc0": "CGeneralVolume__ResetState588AndRefreshCurrentEntry",
}
EXPECTED_RAW_CALLSITES = {"0x0044e093", "0x004f4bd6"}
WEAPON_NAME_TOKENS = ("weapon", "battleengine")


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


def public_row(row: dict[str, str]) -> dict[str, str]:
    return {
        "targetAddress": normalize_address(row.get("target_addr", "")),
        "targetName": row.get("target_name", ""),
        "fromAddress": normalize_address(row.get("from_addr", "")),
        "fromFunctionAddress": normalize_address(row.get("from_function_addr", "")),
        "fromFunction": row.get("from_function", ""),
        "refType": row.get("ref_type", ""),
    }


def decompile_names(rows: list[dict[str, str]]) -> dict[str, str]:
    names: dict[str, str] = {}
    for row in rows:
        address = normalize_address(row.get("address", ""))
        if address.startswith("0x"):
            names[address] = row.get("name", "")
    return names


def build_report(
    *,
    xrefs_path: Path = DEFAULT_XREFS,
    caller_index_path: Path = DEFAULT_CALLER_INDEX,
) -> dict[str, object]:
    xrefs_path = resolve(xrefs_path)
    caller_index_path = resolve(caller_index_path)

    failures: list[str] = []
    if not xrefs_path.is_file():
        failures.append(f"missing xref export: {relative(xrefs_path)}")
    if not caller_index_path.is_file():
        failures.append(f"missing caller decompile index: {relative(caller_index_path)}")

    xref_rows = [
        row
        for row in read_tsv(xrefs_path)
        if normalize_address(row.get("target_addr", "")) == TARGET_ADDRESS
        and row.get("target_name", "") == TARGET_NAME
    ]
    index_names = decompile_names(read_tsv(caller_index_path))

    named_callers: dict[str, str] = {}
    raw_callsites: set[str] = set()
    weapon_named_rows: list[dict[str, str]] = []

    for row in xref_rows:
        from_function_addr = normalize_address(row.get("from_function_addr", ""))
        from_function = row.get("from_function", "")
        if from_function_addr == "<none>":
            raw_callsites.add(normalize_address(row.get("from_addr", "")))
        else:
            named_callers[from_function_addr] = from_function
            lowered = from_function.lower()
            if any(token in lowered for token in WEAPON_NAME_TOKENS):
                weapon_named_rows.append(public_row(row))

    missing_named_callers = {
        address: name
        for address, name in EXPECTED_NAMED_CALLERS.items()
        if named_callers.get(address) != name or index_names.get(address) != name
    }
    missing_raw_callsites = sorted(EXPECTED_RAW_CALLSITES - raw_callsites)

    if len(xref_rows) != EXPECTED_ROW_COUNT:
        failures.append(f"expected {EXPECTED_ROW_COUNT} xref rows to {TARGET_ADDRESS}, found {len(xref_rows)}")
    if missing_named_callers:
        failures.append(f"missing expected named caller rows: {sorted(missing_named_callers)}")
    if missing_raw_callsites:
        failures.append(f"missing expected raw no-function callsites: {missing_raw_callsites}")
    if weapon_named_rows:
        failures.append(f"unexpected weapon-named caller rows: {len(weapon_named_rows)}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "battleengine-weapon-burst-caller-xrefs.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "burst-caller-xrefs-shared-effect-path"
        if status == "PASS"
        else "blocked-or-unexpected-burst-caller-xrefs",
        "inputs": {
            "xrefs": relative(xrefs_path),
            "callerIndex": relative(caller_index_path),
        },
        "target": {
            "address": TARGET_ADDRESS,
            "name": TARGET_NAME,
        },
        "xrefRowCount": len(xref_rows),
        "namedCallerFunctionCount": len(named_callers),
        "namedCallerFunctions": sorted(named_callers.values()),
        "namedCallerFunctionAddresses": sorted(named_callers),
        "rawNoFunctionCallsites": sorted(raw_callsites),
        "weaponNamedCallerRows": weapon_named_rows,
        "failures": failures,
        "whatIsProven": [
            "The current read-only xref export has ten direct xref rows to CGeneralVolume__SpawnBurstFromPresetWithFallback at 0x00506010.",
            "The checked direct named callers are spread across UnitAI, Sentinel, CEngine wrapper, and CGeneralVolume update/reset paths.",
            "The checked export also has two raw no-function callsites into 0x00506010.",
            "No obvious Weapon- or BattleEngine-named direct caller to 0x00506010 appears in the checked xref export.",
        ],
        "notProven": [
            "This does not create, rename, or mutate a Ghidra function boundary.",
            "This does not prove exact CWeapon::Fire or CBattleEngine::WeaponFired identity.",
            "This does not prove whether retail weapon fire clears stealth.",
            "This does not rule out indirect, virtual-dispatch, callback, inlined, or runtime-only weapon-fire behavior elsewhere.",
            "This does not patch or launch BEA.exe and does not prove runtime cloak/fire behavior.",
        ],
        "privacy": "Report stores repo-relative filenames, public addresses, current function names, xref counts, and proof boundaries only; raw Ghidra exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--caller-index", type=Path, default=DEFAULT_CALLER_INDEX)
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

    report = build_report(xrefs_path=args.xrefs, caller_index_path=args.caller_index)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine weapon burst caller xref probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        print(f"Xref rows: {report['xrefRowCount']}")
        print(f"Named caller functions: {report['namedCallerFunctionCount']}")
        print(f"Raw no-function callsites: {', '.join(report['rawNoFunctionCallsites']) or '<none>'}")
        print(f"Weapon-named caller rows: {len(report['weaponNamedCallerRows'])}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
