#!/usr/bin/env python3
"""Validate the saved Ghidra hazard-value tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "hazard-values-wave342" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave342",
    "physics-script",
    "hazard-value-tranche",
    "retail-binary-evidence",
]

TARGETS: dict[str, dict[str, object]] = {
    "0x0043c0b0": {
        "name": "CPhysicsScriptStatements__CreateStatementType9",
        "signature": ["void *", "__cdecl", "CPhysicsScriptStatements__CreateStatementType9", "int valueType"],
        "comment": ["type-9", "hazard-value", "0x005da8a4", "0x005da8e0", "remain unproven"],
        "tags": COMMON_TAGS + ["value-factory", "hazard-value"],
    },
    "0x0043c1a0": {
        "name": "CHazardScalar14__ApplyToHazardByName",
        "signature": ["void", "__thiscall", "CHazardScalar14__ApplyToHazardByName", "char * hazardName"],
        "comment": ["Recovered function boundary", "DAT_00855408", "record+0x14", "this+0x8", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "hazard-apply", "offset-backed-scalar"],
    },
    "0x0043c230": {
        "name": "CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor", "int flags"],
        "comment": ["shared", "0x0043c310", "OID__FreeObject", "leaf", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "shared-vtable-slot"],
    },
    "0x0043c250": {
        "name": "CPhysicsHazardValue__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsHazardValue__scalar_deleting_dtor", "int flags"],
        "comment": ["Recovered function boundary", "0x005da8f4", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "destructor", "value-base"],
    },
    "0x0043c280": {
        "name": "CHazardScalar18__ApplyToHazardByName",
        "signature": ["void", "__thiscall", "CHazardScalar18__ApplyToHazardByName", "char * hazardName"],
        "comment": ["Recovered function boundary", "DAT_00855408", "record+0x18", "this+0x8", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "hazard-apply", "offset-backed-scalar"],
    },
    "0x0043c310": {
        "name": "CPhysicsHazardValue__dtor_base",
        "signature": ["void", "__fastcall", "CPhysicsHazardValue__dtor_base", "void * this"],
        "comment": ["destructor body", "0x005da8f4", "0x0043c250", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "value-base"],
    },
    "0x0043c320": {
        "name": "CHazardNoise__ApplyToHazardByName",
        "signature": ["void", "__thiscall", "CHazardNoise__ApplyToHazardByName", "char * hazardName"],
        "comment": ["DAT_00855408", "owned noise string", "record+0xc", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["hazard-apply", "owned-string-copy"],
    },
    "0x0043c410": {
        "name": "CHazardEffect__ApplyToHazardByName",
        "signature": ["void", "__thiscall", "CHazardEffect__ApplyToHazardByName", "char * hazardName"],
        "comment": ["DAT_00855408", "owned effect string", "record+0x8", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["hazard-apply", "owned-string-copy"],
    },
}

STALE_NAMES = [
    "VFuncSlot_00_0043c230",
    "CPhysicsHazardValue__ctor_like_0043c310",
    "CHazardNoise__VFunc_01_0043c320",
    "CHazardEffect__VFunc_01_0043c410",
]

EXPECTED_XREFS = [
    ("0x0043c0b0", "0x00431966"),
    ("0x0043c0b0", "0x00431a3c"),
    ("0x0043c1a0", "0x005da8e4"),
    ("0x0043c230", "0x005da8a4"),
    ("0x0043c230", "0x005da8b8"),
    ("0x0043c230", "0x005da8cc"),
    ("0x0043c230", "0x005da8e0"),
    ("0x0043c250", "0x005da8f4"),
    ("0x0043c280", "0x005da8d0"),
    ("0x0043c310", "0x0043c233"),
    ("0x0043c320", "0x005da8a8"),
    ("0x0043c410", "0x005da8bc"),
]

EXPECTED_VTABLE_SLOTS = [
    ("0x005da8f4", "0", "CPhysicsHazardValue__scalar_deleting_dtor"),
    ("0x005da8a4", "0", "CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor"),
    ("0x005da8a4", "1", "CHazardNoise__ApplyToHazardByName"),
    ("0x005da8a4", "2", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize"),
    ("0x005da8a4", "3", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer"),
    ("0x005da8b8", "0", "CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor"),
    ("0x005da8b8", "1", "CHazardEffect__ApplyToHazardByName"),
    ("0x005da8b8", "2", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize"),
    ("0x005da8b8", "3", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer"),
    ("0x005da8cc", "0", "CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor"),
    ("0x005da8cc", "1", "CHazardScalar18__ApplyToHazardByName"),
    ("0x005da8cc", "2", "CPhysicsScriptValue__GetScalarSerializedSize4"),
    ("0x005da8cc", "3", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer"),
    ("0x005da8e0", "0", "CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor"),
    ("0x005da8e0", "1", "CHazardScalar14__ApplyToHazardByName"),
    ("0x005da8e0", "2", "CPhysicsScriptValue__GetScalarSerializedSize4"),
    ("0x005da8e0", "3", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer"),
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
        "schema": "ghidra-hazard-value-tranche.v1",
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
    parser.add_argument("--out", type=Path, default=BASE / "hazard-value-tranche-probe.json")
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
    return 0 if report["status"] == "PASS" or not args.check else 1


if __name__ == "__main__":
    raise SystemExit(main())
