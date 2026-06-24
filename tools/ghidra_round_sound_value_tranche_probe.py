#!/usr/bin/env python3
"""Validate the saved Ghidra round/sound value tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "round-sound-values-wave337" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave337",
    "physics-script",
    "round-sound-value-tranche",
    "retail-binary-evidence",
]

TARGETS: dict[str, dict[str, object]] = {
    "0x004359c0": {
        "name": "CPhysicsWeaponModeValue__dtor_base",
        "signature": ["void", "__fastcall", "CPhysicsWeaponModeValue__dtor_base", "void * this"],
        "comment": ["scalar-deleting", "0x00437080", "vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "value-base", "weapon-mode-value", "supersedes-wave336-ctor-label"],
    },
    "0x00437080": {
        "name": "CPhysicsWeaponModeValue__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsWeaponModeValue__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "0x004359c0", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "value-base", "weapon-mode-value"],
    },
    "0x004370a0": {
        "name": "CWeaponRound__ApplyToWeaponModeByName",
        "signature": ["void", "__thiscall", "CWeaponRound__ApplyToWeaponModeByName", "char * weaponModeName"],
        "comment": ["DAT_008553ec", "DAT_008553f0", "+0x18", "SetReader"],
        "tags": COMMON_TAGS + ["round-value", "weapon-mode-apply"],
    },
    "0x004371c0": {
        "name": "CWeaponLaunchSound__ApplyToWeaponModeByName",
        "signature": ["void", "__thiscall", "CWeaponLaunchSound__ApplyToWeaponModeByName", "char * weaponModeName"],
        "comment": ["DAT_008553ec", "+0x24", "owned", "string", "remain unproven"],
        "tags": COMMON_TAGS + ["sound-value", "weapon-mode-apply", "owned-string-copy"],
    },
    "0x004372b0": {
        "name": "CWeaponPreFireSound__ApplyToWeaponModeByName",
        "signature": ["void", "__thiscall", "CWeaponPreFireSound__ApplyToWeaponModeByName", "char * weaponModeName"],
        "comment": ["DAT_008553ec", "+0x28", "owned", "string", "remain unproven"],
        "tags": COMMON_TAGS + ["sound-value", "weapon-mode-apply", "owned-string-copy"],
    },
    "0x004373a0": {
        "name": "CWeaponPostFireSound__ApplyToWeaponModeByName",
        "signature": ["void", "__thiscall", "CWeaponPostFireSound__ApplyToWeaponModeByName", "char * weaponModeName"],
        "comment": ["DAT_008553ec", "+0x2c", "owned", "string", "remain unproven"],
        "tags": COMMON_TAGS + ["sound-value", "weapon-mode-apply", "owned-string-copy"],
    },
    "0x00437490": {
        "name": "CPhysicsScriptStatements__CreateStatementType5",
        "signature": ["void *", "__cdecl", "CPhysicsScriptStatements__CreateStatementType5", "int valueType"],
        "comment": ["type-5/round value", "0x1", "0x26", "remain unproven"],
        "tags": COMMON_TAGS + ["value-factory", "round-value"],
    },
}

STALE_NAMES = [
    "CPhysicsWeaponModeValue__ctor_base",
    "CPhysicsWeaponModeValue__ctor_like_004359c0",
    "VFuncSlot_00_00437080",
    "CWeaponRound__VFunc_01_004370a0",
    "CWeaponLaunchSound__VFunc_01_004371c0",
    "CWeaponPreFireSound__VFunc_01_004372b0",
    "CWeaponPostFireSound__VFunc_01_004373a0",
]

EXPECTED_XREFS = (
    ("0x004359c0", "CPhysicsWeaponModeValue__scalar_deleting_dtor"),
    ("0x00437080", "<no_function>"),
    ("0x004370a0", "<no_function>"),
    ("0x004371c0", "<no_function>"),
    ("0x004372b0", "<no_function>"),
    ("0x004373a0", "<no_function>"),
    ("0x00437490", "CRoundStatement__LoadFromMemBuffer"),
    ("0x00437490", "CPhysicsRoundValueList__LoadFromMemBuffer"),
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
        "schema": "ghidra-round-sound-value-tranche.v1",
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
    out_path = base / "round-sound-value-tranche.json"
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
