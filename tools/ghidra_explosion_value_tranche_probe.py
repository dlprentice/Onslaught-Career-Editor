#!/usr/bin/env python3
"""Validate the saved Ghidra explosion-value tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "explosion-values-wave340" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave340",
    "physics-script",
    "explosion-value-tranche",
    "retail-binary-evidence",
]

TARGETS: dict[str, dict[str, object]] = {
    "0x0043a860": {
        "name": "CPhysicsScriptStatements__CreateStatementType7",
        "signature": ["void *", "__cdecl", "CPhysicsScriptStatements__CreateStatementType7", "int valueType"],
        "comment": ["type-7", "explosion-value", "0x005da6c4", "0x005da7dc", "remain unproven"],
        "tags": COMMON_TAGS + ["value-factory", "explosion-value"],
    },
    "0x0043abd0": {
        "name": "CExplosionBasedOn__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionBasedOn__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["DAT_008553f8", "source/base", "owned effect/sound", "scalar fields", "remain unproven"],
        "tags": COMMON_TAGS + ["explosion-apply", "based-on-copy", "owned-string-copy"],
    },
    "0x0043aea0": {
        "name": "CExplosionBasedOn__CopySoundString28",
        "signature": ["void", "__thiscall", "CExplosionBasedOn__CopySoundString28", "char * sourceString"],
        "comment": ["CExplosionBasedOn", "+0x28", "CExplosionSound", "remains unproven"],
        "tags": COMMON_TAGS + ["explosion-apply", "based-on-copy", "owned-string-copy"],
    },
    "0x0043af10": {
        "name": "CExplosionBasedOn__CopyWaterSoundString2C",
        "signature": ["void", "__thiscall", "CExplosionBasedOn__CopyWaterSoundString2C", "char * sourceString"],
        "comment": ["CExplosionBasedOn", "+0x2c", "CExplosionWaterSound", "remains unproven"],
        "tags": COMMON_TAGS + ["explosion-apply", "based-on-copy", "owned-string-copy"],
    },
    "0x0043af80": {
        "name": "CPhysicsExplosionValue__dtor_base",
        "signature": ["void", "__fastcall", "CPhysicsExplosionValue__dtor_base", "void * this"],
        "comment": ["destructor body", "0x005da7f0", "0x0043af90", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "value-base"],
    },
    "0x0043af90": {
        "name": "CPhysicsExplosionValue__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsExplosionValue__scalar_deleting_dtor", "int flags"],
        "comment": ["Recovered function boundary", "0x005da7f0", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "destructor", "value-base"],
    },
    "0x0043afc0": {
        "name": "CExplosionAirEffect__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionAirEffect__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["DAT_008553f8", "+0x18", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["explosion-apply", "owned-string-copy"],
    },
    "0x0043b0b0": {
        "name": "CExplosionGroundEffect__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionGroundEffect__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["DAT_008553f8", "+0x20", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["explosion-apply", "owned-string-copy"],
    },
    "0x0043b1c0": {
        "name": "CExplosionWaterEffect__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionWaterEffect__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["DAT_008553f8", "+0x1c", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["explosion-apply", "owned-string-copy"],
    },
    "0x0043b2b0": {
        "name": "CExplosionUnitEffect__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionUnitEffect__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["DAT_008553f8", "+0x24", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["explosion-apply", "owned-string-copy"],
    },
    "0x0043b3a0": {
        "name": "CExplosionScalar34__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionScalar34__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["Recovered function boundary", "+0x34", "offset-backed scalar", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "explosion-apply", "offset-backed-scalar"],
    },
    "0x0043b430": {
        "name": "CExplosionScalar38__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionScalar38__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["Recovered function boundary", "+0x38", "offset-backed scalar", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "explosion-apply", "offset-backed-scalar"],
    },
    "0x0043b4c0": {
        "name": "CExplosionScalar3C__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionScalar3C__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["Recovered function boundary", "+0x3c", "offset-backed scalar", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "explosion-apply", "offset-backed-scalar"],
    },
    "0x0043b550": {
        "name": "CExplosionScalar44__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionScalar44__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["Recovered function boundary", "+0x44", "offset-backed scalar", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "explosion-apply", "offset-backed-scalar"],
    },
    "0x0043b5e0": {
        "name": "CExplosionScalar48__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionScalar48__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["Recovered function boundary", "+0x48", "offset-backed scalar", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "explosion-apply", "offset-backed-scalar"],
    },
    "0x0043b670": {
        "name": "CExplosionScalar4C__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionScalar4C__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["Recovered function boundary", "+0x4c", "offset-backed scalar", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "explosion-apply", "offset-backed-scalar"],
    },
    "0x0043b700": {
        "name": "CExplosionScalar40__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionScalar40__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["Recovered function boundary", "+0x40", "offset-backed scalar", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "explosion-apply", "offset-backed-scalar"],
    },
    "0x0043b790": {
        "name": "CExplosionSound__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionSound__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["DAT_008553f8", "+0x28", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["explosion-apply", "owned-string-copy"],
    },
    "0x0043b880": {
        "name": "CExplosionWaterSound__ApplyToExplosionByName",
        "signature": ["void", "__thiscall", "CExplosionWaterSound__ApplyToExplosionByName", "char * explosionName"],
        "comment": ["DAT_008553f8", "+0x2c", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["explosion-apply", "owned-string-copy"],
    },
    "0x0043b970": {
        "name": "CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor", "int flags"],
        "comment": ["shared", "0x0043af80", "OID__FreeObject", "leaf", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "shared-vtable-slot"],
    },
}

STALE_NAMES = [
    "CExplosionBasedOn__VFunc_01_0043abd0",
    "CExplosionBasedOn__ReallocateObjectSlot",
    "CExplosionBasedOn__ReallocateObjectSlot_0043af10",
    "CPhysicsExplosionValue__ctor_like_0043af80",
    "CExplosionAirEffect__VFunc_01_0043afc0",
    "CExplosionGroundEffect__VFunc_01_0043b0b0",
    "CExplosionWaterEffect__VFunc_01_0043b1c0",
    "CExplosionUnitEffect__VFunc_01_0043b2b0",
    "CExplosionSound__VFunc_01_0043b790",
    "CExplosionWaterSound__VFunc_01_0043b880",
    "VFuncSlot_00_0043b970",
]

EXPECTED_XREFS = [
    ("0x0043a860", "0x00430bd6"),
    ("0x0043a860", "0x00430cac"),
    ("0x0043abd0", "0x005da7e0"),
    ("0x0043aea0", "0x0043ae6d"),
    ("0x0043af10", "0x0043ae78"),
    ("0x0043af80", "0x0043b973"),
    ("0x0043af90", "0x005da7f0"),
    ("0x0043afc0", "0x005da7cc"),
    ("0x0043b0b0", "0x005da7b8"),
    ("0x0043b1c0", "0x005da7a4"),
    ("0x0043b2b0", "0x005da790"),
    ("0x0043b3a0", "0x005da768"),
    ("0x0043b430", "0x005da77c"),
    ("0x0043b4c0", "0x005da754"),
    ("0x0043b550", "0x005da718"),
    ("0x0043b5e0", "0x005da6f0"),
    ("0x0043b670", "0x005da704"),
    ("0x0043b700", "0x005da740"),
    ("0x0043b790", "0x005da72c"),
    ("0x0043b880", "0x005da6c8"),
    ("0x0043b970", "0x005da6c4"),
]

EXPECTED_VTABLE_SLOTS = [
    ("0x005da7f0", "0", "CPhysicsExplosionValue__scalar_deleting_dtor"),
    ("0x005da7dc", "0", "CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor"),
    ("0x005da7dc", "1", "CExplosionBasedOn__ApplyToExplosionByName"),
    ("0x005da7c8", "1", "CExplosionAirEffect__ApplyToExplosionByName"),
    ("0x005da764", "1", "CExplosionScalar34__ApplyToExplosionByName"),
    ("0x005da778", "1", "CExplosionScalar38__ApplyToExplosionByName"),
    ("0x005da7b4", "1", "CExplosionGroundEffect__ApplyToExplosionByName"),
    ("0x005da7a0", "1", "CExplosionWaterEffect__ApplyToExplosionByName"),
    ("0x005da78c", "1", "CExplosionUnitEffect__ApplyToExplosionByName"),
    ("0x005da750", "1", "CExplosionScalar3C__ApplyToExplosionByName"),
    ("0x005da73c", "1", "CExplosionScalar40__ApplyToExplosionByName"),
    ("0x005da728", "1", "CExplosionSound__ApplyToExplosionByName"),
    ("0x005da714", "1", "CExplosionScalar44__ApplyToExplosionByName"),
    ("0x005da700", "1", "CExplosionScalar4C__ApplyToExplosionByName"),
    ("0x005da6ec", "1", "CExplosionScalar48__ApplyToExplosionByName"),
    ("0x005da6d8", "1", "SharedVFunc__NoOpOneArg_004014c0"),
    ("0x005da6c4", "1", "CExplosionWaterSound__ApplyToExplosionByName"),
    ("0x005da7dc", "2", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize"),
    ("0x005da7dc", "3", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer"),
    ("0x005da764", "2", "CPhysicsScriptValue__GetScalarSerializedSize4"),
    ("0x005da764", "3", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer"),
]


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
    vtable_slots_path: Path,
) -> dict[str, object]:
    failures: list[str] = []
    metadata_rows = {norm_addr(row.get("address", "")): row for row in read_tsv(metadata_final_path)}
    decompile_rows = {norm_addr(row.get("address", "")): row for row in read_tsv(decompile_index_path)}
    tag_rows = {norm_addr(row.get("address", "")): row for row in read_tsv(tags_path)}
    xref_pairs = {(norm_addr(row.get("target_addr", "")), norm_addr(row.get("from_addr", ""))) for row in read_tsv(xrefs_path)}
    slot_rows = {
        (norm_addr(row.get("vtable", "")), row.get("slot_index", "")): row
        for row in read_tsv(vtable_slots_path)
    }

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

    for target, from_addr in EXPECTED_XREFS:
        if (target, from_addr) not in xref_pairs:
            failures.append(f"expected xref missing: {target} from {from_addr}")

    for vtable, slot, expected_name in EXPECTED_VTABLE_SLOTS:
        row = slot_rows.get((vtable, slot))
        if row is None:
            failures.append(f"vtable slot missing: {vtable} slot {slot}")
            continue
        if row.get("function_name") != expected_name:
            failures.append(
                f"vtable slot function mismatch: {vtable} slot {slot} {row.get('function_name')} != {expected_name}"
            )

    return {
        "schema": "ghidra-explosion-value-tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "targetCount": len(TARGETS),
        "metadataRows": len(metadata_rows),
        "decompileRows": len(decompile_rows),
        "xrefRows": len(read_tsv(xrefs_path)),
        "xrefChecks": len(EXPECTED_XREFS),
        "instructionTargets": len(instruction_rows),
        "tagRows": len(tag_rows),
        "vtableSlotChecks": len(EXPECTED_VTABLE_SLOTS),
        "failures": failures,
    }


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def write_report(report: dict[str, object], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-final", type=Path, default=BASE / "metadata_final.tsv")
    parser.add_argument("--decompile-index", type=Path, default=BASE / "decompile_final" / "index.tsv")
    parser.add_argument("--decompile-dir", type=Path, default=BASE / "decompile_final")
    parser.add_argument("--xrefs", type=Path, default=BASE / "xrefs_final.tsv")
    parser.add_argument("--instructions", type=Path, default=BASE / "instructions_final.tsv")
    parser.add_argument("--tags", type=Path, default=BASE / "tags_final.tsv")
    parser.add_argument("--vtable-slots", type=Path, default=BASE / "vtable_slots_final.tsv")
    parser.add_argument("--out", type=Path, default=BASE / "explosion-value-tranche.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(
        metadata_final_path=resolve(args.metadata_final),
        decompile_index_path=resolve(args.decompile_index),
        decompile_dir=resolve(args.decompile_dir),
        xrefs_path=resolve(args.xrefs),
        instructions_path=resolve(args.instructions),
        tags_path=resolve(args.tags),
        vtable_slots_path=resolve(args.vtable_slots),
    )
    write_report(report, resolve(args.out))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if (report["status"] == "PASS" or not args.check) else 1


if __name__ == "__main__":
    raise SystemExit(main())
