#!/usr/bin/env python3
"""Validate the saved Ghidra weapon-mode value tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "weapon-mode-values-wave336" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave336",
    "physics-script",
    "weapon-mode-value-tranche",
    "retail-binary-evidence",
]

TARGETS: dict[str, dict[str, object]] = {
    "0x00435010": {
        "name": "CPhysicsScriptStatements__CreateStatementType4",
        "signature": ["void *", "__cdecl", "CPhysicsScriptStatements__CreateStatementType4", "int valueType"],
        "comment": ["type-4/weapon-mode value", "0x1", "0x26", "remain unproven"],
        "tags": COMMON_TAGS + ["value-factory", "weapon-mode-value"],
    },
    "0x00435840": {
        "name": "CWeaponBasedOn__ApplyToWeaponByName",
        "signature": ["void", "__thiscall", "CWeaponBasedOn__ApplyToWeaponByName", "char * weaponName"],
        "comment": ["DAT_008553e8", "base/source name", "+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["weapon-value", "weapon-apply"],
    },
    "0x004359c0": {
        "name": "CPhysicsWeaponModeValue__ctor_base",
        "signature": ["void", "__fastcall", "CPhysicsWeaponModeValue__ctor_base", "void * this"],
        "comment": ["base constructor", "CPhysicsWeaponModeValue", "vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["constructor", "value-base", "weapon-mode-value"],
    },
    "0x00435b20": {
        "name": "CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer",
        "signature": ["void", "__thiscall", "CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer", "void * memBuffer"],
        "comment": ["shared load helper", "+0x8", "+0xc", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-load", "shared-helper", "weapon-mode-value"],
    },
    "0x00435c90": {
        "name": "CWeaponLaunchAngle__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CWeaponLaunchAngle__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["launch-angle", "+0x8", "+0x10", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-load", "weapon-mode-value"],
    },
    "0x00436130": {
        "name": "CWeaponVolleySize__ApplyToWeaponModeByName",
        "signature": ["void", "__thiscall", "CWeaponVolleySize__ApplyToWeaponModeByName", "char * weaponModeName"],
        "comment": ["DAT_008553ec", "+0x30", "+0x48", "remain unproven"],
        "tags": COMMON_TAGS + ["weapon-mode-apply"],
    },
    "0x00436320": {
        "name": "CWeaponPreFireEffect__ApplyToWeaponModeByName",
        "signature": ["void", "__thiscall", "CWeaponPreFireEffect__ApplyToWeaponModeByName", "char * weaponModeName"],
        "comment": ["pre-fire effect", "+0x20", "owned string", "remain unproven"],
        "tags": COMMON_TAGS + ["weapon-mode-apply", "owned-string-copy"],
    },
    "0x00436410": {
        "name": "CWeaponMuzzleEffect__ApplyToWeaponModeByName",
        "signature": ["void", "__thiscall", "CWeaponMuzzleEffect__ApplyToWeaponModeByName", "char * weaponModeName"],
        "comment": ["muzzle effect", "+0x1c", "owned string", "remain unproven"],
        "tags": COMMON_TAGS + ["weapon-mode-apply", "owned-string-copy"],
    },
    "0x00436500": {
        "name": "CWeaponClip__ApplyToWeaponModeByName",
        "signature": ["void", "__thiscall", "CWeaponClip__ApplyToWeaponModeByName", "char * weaponModeName"],
        "comment": ["clip string", "+0x30", "owned string", "remain unproven"],
        "tags": COMMON_TAGS + ["weapon-mode-apply", "owned-string-copy"],
    },
}

STALE_NAMES = [
    "CWeaponBasedOn__VFunc_01_00435840",
    "CPhysicsWeaponModeValue__ctor_like_004359c0",
    "VFuncSlot_03_00435b20",
    "CWeaponLaunchAngle__VFunc_03_00435c90",
    "CWeaponVolleySize__VFunc_01_00436130",
    "CWeaponPreFireEffect__VFunc_01_00436320",
    "CWeaponMuzzleEffect__VFunc_01_00436410",
    "CWeaponClip__VFunc_01_00436500",
]

EXPECTED_XREFS = (
    ("0x00435010", "CWeaponModeStatement__LoadFromMemBuffer"),
    ("0x00435010", "CPhysicsWeaponModeValueList__LoadFromMemBuffer"),
    ("0x00435840", "<no_function>"),
    ("0x004359c0", "VFuncSlot_00_00437080"),
    ("0x00435b20", "<no_function>"),
    ("0x00435c90", "<no_function>"),
    ("0x00436130", "<no_function>"),
    ("0x00436320", "<no_function>"),
    ("0x00436410", "<no_function>"),
    ("0x00436500", "<no_function>"),
)


def norm_addr(value: str) -> str:
    value = value.strip().lower()
    if not value:
        return "0x00000000"
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
    tag_rows = {norm_addr(row.get("address", "")): row for row in read_tsv(tags_path)}
    xref_pairs = {(norm_addr(row.get("target_addr", "")), row.get("from_function", "")) for row in read_tsv(xrefs_path)}

    instruction_rows: dict[str, int] = {}
    for row in read_tsv(instructions_path):
        addr = norm_addr(row.get("target_addr", ""))
        instruction_rows[addr] = instruction_rows.get(addr, 0) + 1

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
        "schema": "ghidra-weapon-mode-value-tranche.v1",
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
    out_path = base / "weapon-mode-value-tranche.json"
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
