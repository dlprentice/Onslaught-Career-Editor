#!/usr/bin/env python3
"""Verify saved Ghidra recovery of the weapon slot-0 function boundary.

This probe consumes ignored dry-run/apply/read-back artifacts for the raw
weapon vtable slot-0 candidate at `0x00506930`. It checks that the dry-run
predicted a safe create, the apply result created the function with a
conservative vfunc name, and the saved Ghidra database reads the boundary back
through decompile, all-functions, xref, and instruction-ownership exports.

It does not claim exact source identity for `CWeapon::Fire` or
`CBattleEngine::WeaponFired`.
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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "boundary-00506930" / "current"
DEFAULT_DRY = BASE / "create_function_dry.tsv"
DEFAULT_APPLY = BASE / "create_function_apply.tsv"
DEFAULT_DECOMPILE_INDEX = BASE / "decompile_after" / "index.tsv"
DEFAULT_FUNCTIONS_ALL = BASE / "functions_all_after.tsv"
DEFAULT_XREFS_AFTER = BASE / "xrefs_after.tsv"
DEFAULT_INSTRUCTIONS_AFTER = BASE / "instructions_after.tsv"
DEFAULT_OUT = BASE / "slot0-function-recovery.json"

TARGET = "0x00506930"
INNER_BODY = "0x005069f0"
INNER_CALLSITE = "0x005069b6"
VTABLE_ENTRY = "0x005dfc94"
EXPECTED_NAME = "CWeapon__VFunc_00_00506930"
LEGACY_WEAK_RE = re.compile(r"^(FUN_|Auto_)|__Unk_")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value in {"", "<none>", "<no_function>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def find_address(rows: list[dict[str, str]], key: str, address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def find_create_row(rows: list[dict[str, str]], address: str) -> dict[str, str] | None:
    return find_address(rows, "address", address)


def name_is_legacy_weak(name: str) -> bool:
    return bool(LEGACY_WEAK_RE.search(name or ""))


def build_report(
    *,
    dry_path: Path = DEFAULT_DRY,
    apply_path: Path = DEFAULT_APPLY,
    decompile_index_path: Path = DEFAULT_DECOMPILE_INDEX,
    functions_all_path: Path = DEFAULT_FUNCTIONS_ALL,
    xrefs_after_path: Path = DEFAULT_XREFS_AFTER,
    instructions_after_path: Path = DEFAULT_INSTRUCTIONS_AFTER,
) -> dict[str, object]:
    dry_path = resolve(dry_path)
    apply_path = resolve(apply_path)
    decompile_index_path = resolve(decompile_index_path)
    functions_all_path = resolve(functions_all_path)
    xrefs_after_path = resolve(xrefs_after_path)
    instructions_after_path = resolve(instructions_after_path)

    failures: list[str] = []
    for label, path in (
        ("dry-run result", dry_path),
        ("apply result", apply_path),
        ("decompile index", decompile_index_path),
        ("all-functions read-back", functions_all_path),
        ("xref read-back", xrefs_after_path),
        ("instruction ownership read-back", instructions_after_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    dry_rows = read_tsv(dry_path)
    apply_rows = read_tsv(apply_path)
    decompile_rows = read_tsv(decompile_index_path)
    functions_rows = read_tsv(functions_all_path)
    xref_rows = read_tsv(xrefs_after_path)
    instruction_rows = read_tsv(instructions_after_path)

    dry_row = find_create_row(dry_rows, TARGET)
    apply_row = find_create_row(apply_rows, TARGET)
    decompile_row = find_address(decompile_rows, "address", TARGET)
    functions_row = find_address(functions_rows, "address", TARGET)
    instruction_row = find_address(instruction_rows, "instruction_addr", TARGET)

    dry_status = dry_row.get("status", "") if dry_row else ""
    apply_status = apply_row.get("status", "") if apply_row else ""

    if dry_row is None:
        failures.append(f"missing dry-run row for {TARGET}")
    elif dry_status != "would_create":
        failures.append(f"expected dry-run status would_create for {TARGET}, got {dry_status or '<blank>'}")

    if apply_row is None:
        failures.append(f"missing apply result row for {TARGET}")
    else:
        if apply_status != "created":
            failures.append(f"expected apply status created for {TARGET}, got {apply_status or '<blank>'}")
        if apply_row.get("name", "") != EXPECTED_NAME:
            failures.append(
                f"expected apply name {EXPECTED_NAME}, got {apply_row.get('name', '') or '<blank>'}"
            )

    decompile_ok = (
        decompile_row is not None
        and decompile_row.get("name", "") == EXPECTED_NAME
        and decompile_row.get("status", "") == "OK"
    )
    if not decompile_ok:
        failures.append(f"missing OK decompile read-back for {TARGET} as {EXPECTED_NAME}")

    present_in_all = functions_row is not None and functions_row.get("name", "") == EXPECTED_NAME
    if not present_in_all:
        failures.append(f"missing all-functions read-back for {TARGET} as {EXPECTED_NAME}")

    legacy_weak_names = [
        row
        for row in functions_rows
        if name_is_legacy_weak(row.get("name", ""))
    ]
    if legacy_weak_names:
        failures.append(f"legacy weak names present after function recovery: {len(legacy_weak_names)}")

    vtable_ref_present = any(
        normalize_address(row.get("target_addr", "")) == TARGET
        and row.get("target_name", "") == EXPECTED_NAME
        and normalize_address(row.get("from_addr", "")) == VTABLE_ENTRY
        and row.get("ref_type", "") == "DATA"
        for row in xref_rows
    )
    if not vtable_ref_present:
        failures.append(f"missing vtable DATA xref read-back from {VTABLE_ENTRY} to {TARGET}")

    inner_call_owned = any(
        normalize_address(row.get("target_addr", "")) == INNER_BODY
        and normalize_address(row.get("from_addr", "")) == INNER_CALLSITE
        and normalize_address(row.get("from_function_addr", "")) == TARGET
        and row.get("from_function", "") == EXPECTED_NAME
        and row.get("ref_type", "") == "UNCONDITIONAL_CALL"
        for row in xref_rows
    )
    if not inner_call_owned:
        failures.append(f"missing inner body call ownership from {INNER_CALLSITE} under {EXPECTED_NAME}")

    instruction_owned = (
        instruction_row is not None
        and normalize_address(instruction_row.get("function_entry", "")) == TARGET
        and instruction_row.get("function_name", "") == EXPECTED_NAME
    )
    if not instruction_owned:
        failures.append(f"missing instruction-ownership read-back for {TARGET} under {EXPECTED_NAME}")

    target_signature = ""
    if decompile_row is not None:
        target_signature = decompile_row.get("signature", "")
    elif functions_row is not None:
        target_signature = functions_row.get("signature", "")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "battleengine-weapon-slot0-function-recovery.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "slot0-function-boundary-recovered"
        if status == "PASS"
        else "slot0-function-boundary-recovery-blocked",
        "target": TARGET,
        "functionName": EXPECTED_NAME,
        "createDryStatus": dry_status,
        "createApplyStatus": apply_status,
        "signature": target_signature,
        "legacyWeakNameCount": len(legacy_weak_names),
        "readback": {
            "decompileOk": decompile_ok,
            "presentInAllFunctions": present_in_all,
            "vtableDataRefPresent": vtable_ref_present,
            "innerCallOwnedByRecoveredFunction": inner_call_owned,
            "instructionOwnedByRecoveredFunction": instruction_owned,
        },
        "inputs": {
            "createDry": relative(dry_path),
            "createApply": relative(apply_path),
            "decompileIndex": relative(decompile_index_path),
            "functionsAllAfter": relative(functions_all_path),
            "xrefsAfter": relative(xrefs_after_path),
            "instructionsAfter": relative(instructions_after_path),
        },
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra database now has a function object at 0x00506930 with conservative name CWeapon__VFunc_00_00506930.",
            "The dry-run artifact predicted function creation before the apply artifact created and named the boundary.",
            "Read-back exports show the vtable DATA reference targets the recovered function and the 0x005069b6 call to 0x005069f0 is now owned by the recovered function.",
            "The all-functions read-back includes the recovered function without reintroducing legacy FUN_/Auto_/__Unk_ weak names.",
        ],
        "notProven": [
            "This does not prove exact source CWeapon::Fire or CBattleEngine::WeaponFired identity.",
            "This does not prove retail weapon fire clears or preserves stealth.",
            "This does not refine the recovered function signature beyond Ghidra's current decompiler output.",
            "This does not prove runtime cloak activation, projectile behavior, or fire-while-cloaked behavior.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, signatures, xref/read-back booleans, and proof boundaries only; raw decompile and TSV exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry", type=Path, default=DEFAULT_DRY)
    parser.add_argument("--apply", type=Path, default=DEFAULT_APPLY)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_DECOMPILE_INDEX)
    parser.add_argument("--functions-all", type=Path, default=DEFAULT_FUNCTIONS_ALL)
    parser.add_argument("--xrefs-after", type=Path, default=DEFAULT_XREFS_AFTER)
    parser.add_argument("--instructions-after", type=Path, default=DEFAULT_INSTRUCTIONS_AFTER)
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

    report = build_report(
        dry_path=args.dry,
        apply_path=args.apply,
        decompile_index_path=args.decompile_index,
        functions_all_path=args.functions_all,
        xrefs_after_path=args.xrefs_after,
        instructions_after_path=args.instructions_after,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine weapon slot0 function recovery probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        print(f"Function: {report['target']} {report['functionName']}")
        print(f"Dry-run status: {report['createDryStatus'] or '<missing>'}")
        print(f"Apply status: {report['createApplyStatus'] or '<missing>'}")
        print(f"Legacy weak names after recovery: {report['legacyWeakNameCount']}")
        readback = report["readback"]
        print(f"Decompile read-back OK: {readback['decompileOk']}")
        print(f"Inner call owned by recovered function: {readback['innerCallOwnedByRecoveredFunction']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
