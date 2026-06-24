#!/usr/bin/env python3
"""Validate the saved Ghidra component-value tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "component-values-wave343" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave343",
    "physics-script",
    "component-value-tranche",
    "retail-binary-evidence",
]


def target(
    name: str,
    signature: list[str],
    comment: list[str],
    tags: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "comment": comment,
        "tags": COMMON_TAGS + tags,
    }


def scalar(name: str, record_offset: str) -> dict[str, object]:
    return target(
        name,
        ["void", "__thiscall", name, "char * componentName"],
        ["Recovered function boundary", "DAT_00855400", f"record+{record_offset}", "this+0x8", "scalar"],
        ["function-boundary", "component-apply", "offset-backed-scalar"],
    )


def flag(name: str, record_offset: str) -> dict[str, object]:
    return target(
        name,
        ["void", "__thiscall", name, "char * componentName"],
        ["Recovered function boundary", "DAT_00855400", f"record+{record_offset}", "positive", "remain unproven"],
        ["function-boundary", "component-apply", "offset-backed-flag"],
    )


TARGETS: dict[str, dict[str, object]] = {
    "0x004175b0": target(
        "CPhysicsScriptValue__GetTwoScalarSerializedSize8",
        ["int", "__fastcall", "CPhysicsScriptValue__GetTwoScalarSerializedSize8", "void * this"],
        ["shared serialization", "fixed serialized size 8", "0x005da96c", "remain unproven"],
        ["function-boundary", "shared-serialization", "two-scalar-value"],
    ),
    "0x00433170": target(
        "CComponentValue02__LoadFromMemBuffer",
        ["void", "__thiscall", "CComponentValue02__LoadFromMemBuffer", "void * memBuffer"],
        ["type-10", "id 0x2", "CDXMemBuffer", "this+0x8", "remain unproven"],
        ["function-boundary", "component-value", "statement-load"],
    ),
    "0x004331e0": target(
        "CComponentValue13__GetSerializedSize",
        ["int", "__fastcall", "CComponentValue13__GetSerializedSize", "void * this"],
        ["type-10", "id 0x13", "serialized-size", "compound", "remain unproven"],
        ["function-boundary", "component-value", "serialized-size"],
    ),
    "0x00433220": target(
        "CComponentValue13__LoadFromMemBuffer",
        ["void", "__thiscall", "CComponentValue13__LoadFromMemBuffer", "void * memBuffer"],
        ["type-10", "id 0x13", "CDXMemBuffer", "compound", "remain unproven"],
        ["function-boundary", "component-value", "statement-load"],
    ),
    "0x0043c500": target(
        "CPhysicsScriptStatements__CreateStatementType10",
        ["void *", "__cdecl", "CPhysicsScriptStatements__CreateStatementType10", "int valueType"],
        ["type-10", "component-value", "0x005da908", "0x005daad4", "remain unproven"],
        ["value-factory", "component-value"],
    ),
    "0x0043ca70": scalar("CComponentScalarD8__ApplyToComponentByName", "0xd8"),
    "0x0043cb40": scalar("CComponentScalarDC__ApplyToComponentByName", "0xdc"),
    "0x0043cbe0": scalar("CComponentScalarC0__ApplyToComponentByName", "0xc0"),
    "0x0043cc80": scalar("CComponentScalar158__ApplyToComponentByName", "0x158"),
    "0x0043cd20": scalar("CComponentScalarB8__ApplyToComponentByName", "0xb8"),
    "0x0043cdc0": scalar("CComponentScalarBC__ApplyToComponentByName", "0xbc"),
    "0x0043ce60": flag("CComponentFlag124__ApplyToComponentByName", "0x124"),
    "0x0043cf20": flag("CComponentFlag128__ApplyToComponentByName", "0x128"),
    "0x0043cfe0": flag("CComponentFlag12C__ApplyToComponentByName", "0x12c"),
    "0x0043d0a0": flag("CComponentFlag198__ApplyToComponentByName", "0x198"),
    "0x0043d160": flag("CComponentFlag114__ApplyToComponentByName", "0x114"),
    "0x0043d220": flag("CComponentFlag19C__ApplyToComponentByName", "0x19c"),
    "0x0043d2e0": flag("CComponentFlag134__ApplyToComponentByName", "0x134"),
    "0x0043d3a0": flag("CComponentFlag108__ApplyToComponentByName", "0x108"),
    "0x0043d460": scalar("CComponentScalar160__ApplyToComponentByName", "0x160"),
    "0x0043d500": target(
        "CComponentIndexedScalar164__ApplyToComponentByName",
        ["void", "__thiscall", "CComponentIndexedScalar164__ApplyToComponentByName", "char * componentName"],
        ["DAT_00855400", "record+0x164", "this+0x8", "this+0xc", "remain unproven"],
        ["function-boundary", "component-apply", "indexed-scalar"],
    ),
    "0x0043d5a0": target(
        "CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor",
        ["void *", "__thiscall", "CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor", "int flags"],
        ["shared scalar-deleting destructor", "0x0043dcc0", "OID__FreeObject", "leaf", "remain unproven"],
        ["destructor", "shared-vtable-slot"],
    ),
    "0x0043d5c0": target(
        "CComponentValue02__ApplyToComponentByName",
        ["void", "__thiscall", "CComponentValue02__ApplyToComponentByName", "char * componentName"],
        ["type-10", "id 0x2", "DAT_00855400", "this+0x108", "remain unproven"],
        ["function-boundary", "component-apply", "compound-component-value"],
    ),
    "0x0043d670": target(
        "CComponentValue02__GetSerializedSize",
        ["int", "__fastcall", "CComponentValue02__GetSerializedSize", "void * this"],
        ["type-10", "id 0x2", "serialized-size", "compound", "remain unproven"],
        ["function-boundary", "component-value", "serialized-size"],
    ),
    "0x0043d6b0": target(
        "CComponentValue13__ApplyToComponentByName",
        ["void", "__thiscall", "CComponentValue13__ApplyToComponentByName", "char * componentName"],
        ["type-10", "id 0x13", "DAT_00855400", "compound", "remain unproven"],
        ["function-boundary", "component-apply", "compound-component-value"],
    ),
    "0x0043d760": target(
        "CComponentMesh__ApplyToComponentByName",
        ["void", "__thiscall", "CComponentMesh__ApplyToComponentByName", "char * componentName"],
        ["DAT_00855400", "owned mesh string", "record+0x2c", "this+0x8", "remain unproven"],
        ["component-apply", "owned-string-copy"],
    ),
    "0x0043d850": target(
        "CComponentValue04__ApplyToComponentByName",
        ["void", "__thiscall", "CComponentValue04__ApplyToComponentByName", "char * componentName"],
        ["type-10", "id 0x4", "0x00511720", "owned-string", "remain unproven"],
        ["function-boundary", "component-apply", "owned-string-helper"],
    ),
    "0x0043d8f0": target(
        "CComponentVent__ApplyToComponentByName",
        ["void", "__thiscall", "CComponentVent__ApplyToComponentByName", "char * componentName"],
        ["DAT_00855400", "owned vent string", "record+0x98", "this+0x8", "remain unproven"],
        ["component-apply", "owned-string-copy"],
    ),
    "0x0043d9f0": target(
        "CComponentValue0E__ApplyToComponentByName",
        ["void", "__thiscall", "CComponentValue0E__ApplyToComponentByName", "char * componentName"],
        ["type-10", "id 0xe", "0x005117c0", "owned-string", "remain unproven"],
        ["function-boundary", "component-apply", "owned-string-helper"],
    ),
    "0x0043da90": target(
        "CComponentNoise__ApplyToComponentByName",
        ["void", "__thiscall", "CComponentNoise__ApplyToComponentByName", "char * componentName"],
        ["DAT_00855400", "owned noise string", "record+0xa8", "this+0x8", "remain unproven"],
        ["component-apply", "owned-string-copy"],
    ),
    "0x0043db90": target(
        "CComponentBasedOn__ApplyToComponentByName",
        ["void", "__thiscall", "CComponentBasedOn__ApplyToComponentByName", "char * componentName"],
        ["DAT_00855400", "based-on source", "CComponentBasedOn__CopyFrom", "source/null", "remain unproven"],
        ["component-apply", "based-on-copy"],
    ),
    "0x0043dcc0": target(
        "CPhysicsComponentValue__dtor_base",
        ["void", "__fastcall", "CPhysicsComponentValue__dtor_base", "void * this"],
        ["base destructor", "0x005daae8", "0x0043d5a0", "remain unproven"],
        ["destructor", "value-base"],
    ),
}

STALE_NAMES = [
    "VFuncSlot_00_0043d5a0",
    "CComponentMesh__VFunc_01_0043d760",
    "CComponentVent__VFunc_01_0043d8f0",
    "CComponentNoise__VFunc_01_0043da90",
    "CComponentBasedOn__VFunc_01_0043db90",
    "CPhysicsComponentValue__ctor_like_0043dcc0",
]

EXPECTED_XREFS = [
    ("0x004175b0", "0x005da974"),
    ("0x00433170", "0x005daa7c"),
    ("0x004331e0", "0x005daa64"),
    ("0x00433220", "0x005daa68"),
    ("0x0043c500", "0x004310c6"),
    ("0x0043c500", "0x0043119c"),
    ("0x0043d5a0", "0x005da908"),
    ("0x0043d5a0", "0x005daad4"),
    ("0x0043d760", "0x005daad8"),
    ("0x0043db90", "0x005daa24"),
    ("0x0043dcc0", "0x0043d5a3"),
]

VTABLES: list[tuple[str, str, str, str, str]] = [
    ("0x005da908", "CComponentVent__ApplyToComponentByName", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer", "0x00611e78"),
    ("0x005da91c", "CComponentFlag134__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00611f18"),
    ("0x005da930", "CComponentFlag19C__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00611fb8"),
    ("0x005da944", "CComponentFlag114__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00612008"),
    ("0x005da958", "CComponentFlag198__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00611b58"),
    ("0x005da96c", "CComponentIndexedScalar164__ApplyToComponentByName", "CPhysicsScriptValue__GetTwoScalarSerializedSize8", "CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer", "0x00612058"),
    ("0x005da980", "CComponentFlag12C__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00611bf8"),
    ("0x005da994", "CComponentScalar160__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00611ce8"),
    ("0x005da9a8", "CComponentFlag108__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00611c48"),
    ("0x005da9bc", "CComponentValue0E__ApplyToComponentByName", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer", "0x006120f8"),
    ("0x005da9d0", "CComponentFlag128__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00611a18"),
    ("0x005da9e4", "CComponentFlag124__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00612160"),
    ("0x005da9f8", "CComponentNoise__ApplyToComponentByName", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer", "0x00611a68"),
    ("0x005daa0c", "CComponentScalarBC__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x006120a8"),
    ("0x005daa20", "CComponentBasedOn__ApplyToComponentByName", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer", "0x00611b08"),
    ("0x005daa34", "CComponentScalarB8__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00611dd8"),
    ("0x005daa48", "CComponentValue04__ApplyToComponentByName", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer", "0x00611f68"),
    ("0x005daa5c", "CComponentValue13__ApplyToComponentByName", "CComponentValue13__GetSerializedSize", "CComponentValue13__LoadFromMemBuffer", "0x00611ab8"),
    ("0x005daa70", "CComponentValue02__ApplyToComponentByName", "CComponentValue02__GetSerializedSize", "CComponentValue02__LoadFromMemBuffer", "0x00611ba8"),
    ("0x005daa84", "CComponentScalar158__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00611c98"),
    ("0x005daa98", "CComponentScalarC0__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00611d88"),
    ("0x005daaac", "CComponentScalarDC__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00611e28"),
    ("0x005daac0", "CComponentScalarD8__ApplyToComponentByName", "CPhysicsScriptValue__GetScalarSerializedSize4", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "0x00611ec8"),
    ("0x005daad4", "CComponentMesh__ApplyToComponentByName", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer", "0x00612190"),
]

EXPECTED_VTABLE_SLOTS = [
    (vtable, "0", "CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor")
    for vtable, _slot1, _slot2, _slot3, _slot4 in VTABLES
]
EXPECTED_VTABLE_SLOTS += [
    (vtable, str(slot), name)
    for vtable, slot1, slot2, slot3, _slot4 in VTABLES
    for slot, name in ((1, slot1), (2, slot2), (3, slot3))
]

EXPECTED_SLOT4_POINTERS = [(vtable, "4", pointer) for vtable, _slot1, _slot2, _slot3, pointer in VTABLES]


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

    for target_addr, from_addr in EXPECTED_XREFS:
        if (target_addr, from_addr) not in xref_pairs:
            failures.append(f"expected xref missing: {target_addr} from {from_addr}")

    for vtable, slot, expected_name in EXPECTED_VTABLE_SLOTS:
        row = slot_rows.get((vtable, slot))
        if row is None:
            failures.append(f"vtable slot missing: {vtable} slot {slot}")
            continue
        if row.get("function_name") != expected_name:
            failures.append(
                f"vtable slot function mismatch: {vtable} slot {slot} {row.get('function_name')} != {expected_name}"
            )

    for vtable, slot, expected_pointer in EXPECTED_SLOT4_POINTERS:
        row = slot_rows.get((vtable, slot))
        if row is None:
            failures.append(f"vtable slot4 pointer missing: {vtable}")
            continue
        if norm_addr(row.get("pointer_addr", "")) != norm_addr(expected_pointer):
            failures.append(
                f"vtable slot4 pointer mismatch: {vtable} {row.get('pointer_addr')} != {expected_pointer}"
            )

    return {
        "schema": "ghidra-component-value-tranche.v1",
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
        "vtableSlot4PointerChecks": len(EXPECTED_SLOT4_POINTERS),
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
    parser.add_argument("--out", type=Path, default=BASE / "component-value-tranche-probe.json")
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
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
