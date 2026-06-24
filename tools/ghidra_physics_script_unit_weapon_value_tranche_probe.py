#!/usr/bin/env python3
"""Validate the saved Ghidra PhysicsScript unit/weapon value tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "physics-script-unit-values-wave334" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave334",
    "physics-script",
    "unit-weapon-value-tranche",
    "retail-binary-evidence",
]

TARGETS: dict[str, dict[str, object]] = {
    "0x00432a50": {
        "name": "CUnitAlligence__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CUnitAlligence__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "CUnitAlligence__dtor", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00432a70": {
        "name": "CUnitAlligence__dtor",
        "signature": ["void", "__fastcall", "CUnitAlligence__dtor", "void * this"],
        "comment": ["destructor body", "+0x8", "child value", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00432c00": {
        "name": "CUnitSoundMaterial__ApplyToUnitData",
        "signature": ["void", "__thiscall", "CUnitSoundMaterial__ApplyToUnitData", "void * unitData"],
        "comment": ["sound-material", "+0xe4", "rounds the scalar", "remain unproven"],
        "tags": COMMON_TAGS + ["unit-data-apply"],
    },
    "0x00432c70": {
        "name": "CUnitMaxLegsLifted__ApplyToUnitData",
        "signature": ["void", "__thiscall", "CUnitMaxLegsLifted__ApplyToUnitData", "void * unitData"],
        "comment": ["leg-lift", "+0x140", "rounds the scalar", "remain unproven"],
        "tags": COMMON_TAGS + ["unit-data-apply"],
    },
    "0x00432cc0": {
        "name": "CPhysicsUnitValue__dtor_base",
        "signature": ["void", "__fastcall", "CPhysicsUnitValue__dtor_base", "void * this"],
        "comment": ["base destructor", "CPhysicsUnitValue", "base value vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "value-base"],
    },
    "0x00432f70": {
        "name": "CUnitNavMap__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CUnitNavMap__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["CreateStatementType14", "child statement", "+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-load"],
    },
    "0x00432fa0": {
        "name": "CUnitNavMap__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CUnitNavMap__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "CUnitNavMap__dtor", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00432fc0": {
        "name": "CUnitNavMap__dtor",
        "signature": ["void", "__fastcall", "CUnitNavMap__dtor", "void * this"],
        "comment": ["destructor body", "+0x8", "child statement", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x004330b0": {
        "name": "CUnitBehaviour__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CUnitBehaviour__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["CreateStatementType12", "child statement", "+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-load"],
    },
    "0x004330e0": {
        "name": "CUnitBehaviour__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CUnitBehaviour__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "CUnitBehaviour__dtor", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00433100": {
        "name": "CUnitBehaviour__dtor",
        "signature": ["void", "__fastcall", "CUnitBehaviour__dtor", "void * this"],
        "comment": ["destructor body", "+0x8", "child statement", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00434100": {
        "name": "CPhysicsUnitValue__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsUnitValue__scalar_deleting_dtor", "int flags"],
        "comment": ["shared scalar-deleting", "CPhysicsUnitValue__dtor_base", "unit value vtables", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "value-base"],
    },
    "0x00434300": {
        "name": "CPhysicsScriptStatements__CreateStatementType3",
        "signature": ["void *", "__cdecl", "CPhysicsScriptStatements__CreateStatementType3", "int valueType"],
        "comment": ["type-3/weapon value", "0x74", "0x81", "remain unproven"],
        "tags": COMMON_TAGS + ["value-factory"],
    },
    "0x00434770": {
        "name": "CWeaponChargeLevel__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CWeaponChargeLevel__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["charge level", "+0x108", "name string", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-load", "weapon-value"],
    },
    "0x004347a0": {
        "name": "CPhysicsWeaponValue__dtor_base",
        "signature": ["void", "__fastcall", "CPhysicsWeaponValue__dtor_base", "void * this"],
        "comment": ["base destructor", "CPhysicsWeaponValue", "base weapon value vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "weapon-value"],
    },
    "0x00434a80": {
        "name": "CPhysicsWeaponValue__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsWeaponValue__scalar_deleting_dtor", "int flags"],
        "comment": ["shared scalar-deleting", "CPhysicsWeaponValue__dtor_base", "weapon value vtables", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "weapon-value"],
    },
    "0x00434f20": {
        "name": "CWeaponIconName__ApplyToWeaponByName",
        "signature": ["void", "__thiscall", "CWeaponIconName__ApplyToWeaponByName", "char * weaponName"],
        "comment": ["CWeaponIconName", "DAT_008553e8", "icon string", "remain unproven"],
        "tags": COMMON_TAGS + ["weapon-value", "unit-data-apply"],
    },
}

STALE_NAMES = [
    "CUnitAlligence__VFunc_00_00432a50",
    "CUnitAlligence__ctor_like_00432a70",
    "CUnitSoundMaterial__VFunc_01_00432c00",
    "CUnitMaxLegsLifted__VFunc_01_00432c70",
    "CPhysicsUnitValue__ctor_like_00432cc0",
    "CUnitNavMap__VFunc_03_00432f70",
    "CUnitNavMap__VFunc_00_00432fa0",
    "CUnitNavMap__ctor_like_00432fc0",
    "CUnitBehaviour__VFunc_03_004330b0",
    "CUnitBehaviour__VFunc_00_004330e0",
    "CUnitBehaviour__ctor_like_00433100",
    "VFuncSlot_00_00434100",
    "CWeaponChargeLevel__VFunc_03_00434770",
    "CPhysicsWeaponValue__ctor_like_004347a0",
    "VFuncSlot_00_00434a80",
    "CWeaponIconName__VFunc_01_00434f20",
]

EXPECTED_XREFS = (
    ("0x00432a50", "<no_function>"),
    ("0x00432a70", "CUnitAlligence__scalar_deleting_dtor"),
    ("0x00432c00", "<no_function>"),
    ("0x00432c70", "<no_function>"),
    ("0x00432cc0", "CPhysicsUnitValue__scalar_deleting_dtor"),
    ("0x00432f70", "<no_function>"),
    ("0x00432fa0", "<no_function>"),
    ("0x00432fc0", "CUnitNavMap__scalar_deleting_dtor"),
    ("0x004330b0", "<no_function>"),
    ("0x004330e0", "<no_function>"),
    ("0x00433100", "CUnitBehaviour__scalar_deleting_dtor"),
    ("0x00434100", "<no_function>"),
    ("0x00434300", "CWeaponStatement__LoadFromMemBuffer"),
    ("0x00434300", "CPhysicsWeaponValueList__LoadFromMemBuffer"),
    ("0x00434770", "<no_function>"),
    ("0x004347a0", "CPhysicsWeaponValue__scalar_deleting_dtor"),
    ("0x00434a80", "<no_function>"),
    ("0x00434f20", "<no_function>"),
)


def norm_addr(value: str) -> str:
    value = value.strip().lower()
    if not value.startswith("0x"):
        value = "0x" + value
    return f"0x{int(value, 16):08x}"


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def decompile_file_exists(decompile_dir: Path, address: str, name: str) -> bool:
    stem = address[2:].lower()
    return any(path.name.lower().startswith(stem) and name.lower() in path.name.lower() for path in decompile_dir.glob("*.c"))


def build_report(
    *,
    metadata_final_path: Path,
    decompile_index_path: Path,
    decompile_dir: Path,
    xrefs_path: Path,
    instructions_path: Path,
    tags_path: Path,
) -> dict[str, object]:
    failures: list[str] = []
    metadata_rows = {norm_addr(row.get("address", "")): row for row in read_tsv(metadata_final_path)}
    decompile_rows = {norm_addr(row.get("address", "")): row for row in read_tsv(decompile_index_path)}
    instruction_rows: dict[str, int] = {}
    for row in read_tsv(instructions_path):
        addr = norm_addr(row.get("target_addr", ""))
        instruction_rows[addr] = instruction_rows.get(addr, 0) + 1
    tag_rows = {norm_addr(row.get("address", "")): row for row in read_tsv(tags_path)}
    xref_pairs = {(norm_addr(row.get("target_addr", "")), row.get("from_function", "")) for row in read_tsv(xrefs_path)}

    names_seen = {row.get("name", "") for row in metadata_rows.values()}
    for stale_name in STALE_NAMES:
        if stale_name in names_seen:
            failures.append(f"stale name still present: {stale_name}")

    for address, expected in TARGETS.items():
        row = metadata_rows.get(address)
        if row is None:
            failures.append(f"metadata missing: {address}")
            continue
        if row.get("status") != "OK":
            failures.append(f"metadata status not OK: {address} {row.get('status')}")
        if row.get("name") != expected["name"]:
            failures.append(f"name mismatch: {address} {row.get('name')} != {expected['name']}")
        signature = row.get("signature", "")
        for token in expected["signature"]:
            if str(token) not in signature:
                failures.append(f"signature token missing: {address} {token}")
        comment = row.get("comment", "")
        for token in expected["comment"]:
            if str(token) not in comment:
                failures.append(f"comment token missing: {address} {token}")
        tag_row = tag_rows.get(address)
        tag_text = tag_row.get("tags", "") if tag_row else ""
        for tag in expected["tags"]:
            if str(tag) not in tag_text.split(";"):
                failures.append(f"tag missing: {address} {tag}")
        drow = decompile_rows.get(address)
        if drow is None or drow.get("status") != "OK":
            failures.append(f"decompile index missing/not OK: {address}")
        elif not decompile_file_exists(decompile_dir, address, str(expected["name"])):
            failures.append(f"decompile file missing: {address} {expected['name']}")
        if instruction_rows.get(address, 0) == 0:
            failures.append(f"instruction read-back missing: {address}")

    for target, caller in EXPECTED_XREFS:
        if (target, caller) not in xref_pairs:
            failures.append(f"expected xref missing: {target} from {caller}")

    return {
        "schema": "ghidra-physics-script-unit-weapon-value-tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "targetCount": len(TARGETS),
        "metadataRows": len(metadata_rows),
        "decompileRows": len(decompile_rows),
        "xrefRows": len(read_tsv(xrefs_path)),
        "xrefChecks": len(EXPECTED_XREFS),
        "instructionTargets": len(instruction_rows),
        "tagRows": len(tag_rows),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    base = args.base
    report = build_report(
        metadata_final_path=base / "metadata_final.tsv",
        decompile_index_path=base / "decompile_final" / "index.tsv",
        decompile_dir=base / "decompile_final",
        xrefs_path=base / "xrefs_final.tsv",
        instructions_path=base / "instructions_final.tsv",
        tags_path=base / "tags_final.tsv",
    )
    out_path = base / "physics-script-unit-weapon-value-tranche.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Status: {report['status']}")
    print(f"Targets: {report['targetCount']}")
    print(f"Metadata rows: {report['metadataRows']}")
    print(f"Decompile rows: {report['decompileRows']}")
    print(f"Xref rows/checks: {report['xrefRows']}/{report['xrefChecks']}")
    print(f"Instruction targets: {report['instructionTargets']}")
    print(f"Tag rows: {report['tagRows']}")
    print(f"Report: {out_path}")
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
