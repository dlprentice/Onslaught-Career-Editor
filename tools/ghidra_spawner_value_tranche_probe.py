#!/usr/bin/env python3
"""Validate the saved Ghidra spawner-value tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "spawner-values-wave339" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave339",
    "physics-script",
    "spawner-value-tranche",
    "retail-binary-evidence",
]

TARGETS: dict[str, dict[str, object]] = {
    "0x004014c0": {
        "name": "SharedVFunc__NoOpOneArg_004014c0",
        "signature": ["void", "__thiscall", "SharedVFunc__NoOpOneArg_004014c0", "void * this", "int arg0"],
        "comment": ["supersedes", "CFrontEndPage", "shared", "ret 0x4", "remain unproven"],
        "tags": COMMON_TAGS + ["shared-vtable-slot", "no-op"],
    },
    "0x00405930": {
        "name": "SharedVFunc__ReturnZero_00405930",
        "signature": ["int", "__thiscall", "SharedVFunc__ReturnZero_00405930", "void * this"],
        "comment": ["supersedes", "CControllerDefinition", "shared", "returns 0", "remain unproven"],
        "tags": COMMON_TAGS + ["shared-vtable-slot", "return-zero"],
    },
    "0x00434b60": {
        "name": "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer",
        "signature": ["void", "__thiscall", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "void * memBuffer"],
        "comment": ["shared", "CDXMemBuffer", "4-byte", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["shared-serialization", "scalar-value"],
    },
    "0x004398f0": {
        "name": "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize",
        "signature": ["int", "__fastcall", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize", "void * this"],
        "comment": ["shared", "owned string", "this+0x8", "terminator", "remain unproven"],
        "tags": COMMON_TAGS + ["shared-serialization", "owned-string-size"],
    },
    "0x00439b40": {
        "name": "CPhysicsScriptStatements__CreateStatementType6",
        "signature": ["void *", "__cdecl", "CPhysicsScriptStatements__CreateStatementType6", "int valueType"],
        "comment": ["type-6", "spawner value", "0x005da598", "0x005da6b0", "remain unproven"],
        "tags": COMMON_TAGS + ["value-factory", "spawner-value"],
    },
    "0x00439e70": {
        "name": "CSpawnerBasedOn__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerBasedOn__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["DAT_008553f4", "source/base", "this+0x8", "copies", "remain unproven"],
        "tags": COMMON_TAGS + ["spawner-apply", "based-on-copy"],
    },
    "0x0043a040": {
        "name": "CPhysicsSpawnerValue__dtor_base",
        "signature": ["void", "__fastcall", "CPhysicsSpawnerValue__dtor_base", "void * this"],
        "comment": ["destructor body", "0x005da6b0", "0x0043a050", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "value-base"],
    },
    "0x0043a050": {
        "name": "CPhysicsSpawnerValue__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsSpawnerValue__scalar_deleting_dtor", "int flags"],
        "comment": ["Recovered function boundary", "0x005da6b0", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "destructor", "value-base"],
    },
    "0x0043a080": {
        "name": "CSpawnerUnit__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerUnit__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["DAT_008553f4", "owned unit string", "this+0x8", "record+0x4", "remain unproven"],
        "tags": COMMON_TAGS + ["spawner-apply", "owned-string-copy"],
    },
    "0x0043a170": {
        "name": "CSpawnerDelay__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerDelay__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["Recovered function boundary", "record+0x18", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "spawner-apply", "numeric-spawner-value"],
    },
    "0x0043a200": {
        "name": "CSpawnerAmount__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerAmount__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["Recovered function boundary", "record+0xc", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "spawner-apply", "numeric-spawner-value"],
    },
    "0x0043a290": {
        "name": "CSpawnerConditions__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerConditions__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["Recovered function boundary", "record+0x14", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "spawner-apply", "numeric-spawner-value"],
    },
    "0x0043a320": {
        "name": "CSpawnerSquadSize__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerSquadSize__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["Recovered function boundary", "record+0x10", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "spawner-apply", "numeric-spawner-value"],
    },
    "0x0043a3b0": {
        "name": "CSpawnerSquadDelay__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerSquadDelay__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["Recovered function boundary", "record+0x20", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "spawner-apply", "numeric-spawner-value"],
    },
    "0x0043a440": {
        "name": "CSpawnerSeekDelay__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerSeekDelay__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["Recovered function boundary", "record+0x1c", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "spawner-apply", "numeric-spawner-value"],
    },
    "0x0043a4d0": {
        "name": "CSpawnerRecall__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerRecall__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["Recovered function boundary", "record+0x28", "constant 1", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "spawner-apply", "boolean-spawner-value"],
    },
    "0x0043a570": {
        "name": "CSpawnerMinRange__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerMinRange__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["Recovered function boundary", "record+0x2c", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "spawner-apply", "numeric-spawner-value"],
    },
    "0x0043a600": {
        "name": "CSpawnerMaxRange__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerMaxRange__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["Recovered function boundary", "record+0x30", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "spawner-apply", "numeric-spawner-value"],
    },
    "0x0043a690": {
        "name": "CSpawnerPreSpawnDelay__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerPreSpawnDelay__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["Recovered function boundary", "record+0x34", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "spawner-apply", "numeric-spawner-value"],
    },
    "0x0043a720": {
        "name": "CSpawnerPostSpawnDelay__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerPostSpawnDelay__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["Recovered function boundary", "record+0x38", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "spawner-apply", "numeric-spawner-value"],
    },
    "0x0043a7b0": {
        "name": "CSpawnerInfinite__ApplyToSpawnerByName",
        "signature": ["void", "__thiscall", "CSpawnerInfinite__ApplyToSpawnerByName", "char * spawnerName"],
        "comment": ["Recovered function boundary", "record+0x24", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "spawner-apply", "numeric-spawner-value"],
    },
    "0x0043a840": {
        "name": "CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor", "int flags"],
        "comment": ["shared", "0x0043a040", "OID__FreeObject", "leaf", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "shared-vtable-slot"],
    },
    "0x0043b1a0": {
        "name": "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer",
        "signature": ["void", "__thiscall", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer", "void * memBuffer"],
        "comment": ["shared", "CDXMemBuffer", "owned string", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["shared-serialization", "owned-string-load"],
    },
    "0x004db8c0": {
        "name": "CPhysicsScriptValue__GetScalarSerializedSize4",
        "signature": ["int", "__fastcall", "CPhysicsScriptValue__GetScalarSerializedSize4", "void * this"],
        "comment": ["shared", "fixed serialized size 4", "scalar", "remain unproven"],
        "tags": COMMON_TAGS + ["shared-serialization", "scalar-value"],
    },
}

STALE_NAMES = [
    "CFrontEndPage__ActiveNotification_NoOp",
    "CControllerDefinition__VFunc_03_00405930",
    "CSpawnerBasedOn__VFunc_01_00439e70",
    "CPhysicsSpawnerValue__ctor_like_0043a040",
    "CSpawnerUnit__VFunc_01_0043a080",
    "VFuncSlot_00_0043a840",
]

EXPECTED_XREFS = [
    ("0x004014c0", "0x005da630"),
    ("0x00405930", "0x005da62c"),
    ("0x00434b60", "0x005da5b8"),
    ("0x004398f0", "0x005da5c8"),
    ("0x00439b40", "0x00430756"),
    ("0x00439e70", "0x005da5c4"),
    ("0x0043a050", "0x005da6b0"),
    ("0x0043a080", "0x005da6a0"),
    ("0x0043a170", "0x005da68c"),
    ("0x0043a200", "0x005da678"),
    ("0x0043a290", "0x005da59c"),
    ("0x0043a320", "0x005da664"),
    ("0x0043a3b0", "0x005da650"),
    ("0x0043a440", "0x005da63c"),
    ("0x0043a4d0", "0x005da628"),
    ("0x0043a570", "0x005da614"),
    ("0x0043a600", "0x005da600"),
    ("0x0043a690", "0x005da5ec"),
    ("0x0043a720", "0x005da5d8"),
    ("0x0043a7b0", "0x005da5b0"),
    ("0x0043a840", "0x005da598"),
    ("0x0043b1a0", "0x005da5cc"),
    ("0x004db8c0", "0x005da5b4"),
]

EXPECTED_VTABLE_SLOTS = [
    ("0x005da598", "0", "CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor"),
    ("0x005da598", "1", "CSpawnerConditions__ApplyToSpawnerByName"),
    ("0x005da5ac", "1", "CSpawnerInfinite__ApplyToSpawnerByName"),
    ("0x005da5c0", "1", "CSpawnerBasedOn__ApplyToSpawnerByName"),
    ("0x005da5d4", "1", "CSpawnerPostSpawnDelay__ApplyToSpawnerByName"),
    ("0x005da5e8", "1", "CSpawnerPreSpawnDelay__ApplyToSpawnerByName"),
    ("0x005da5fc", "1", "CSpawnerMaxRange__ApplyToSpawnerByName"),
    ("0x005da610", "1", "CSpawnerMinRange__ApplyToSpawnerByName"),
    ("0x005da624", "1", "CSpawnerRecall__ApplyToSpawnerByName"),
    ("0x005da624", "2", "SharedVFunc__ReturnZero_00405930"),
    ("0x005da624", "3", "SharedVFunc__NoOpOneArg_004014c0"),
    ("0x005da638", "1", "CSpawnerSeekDelay__ApplyToSpawnerByName"),
    ("0x005da64c", "1", "CSpawnerSquadDelay__ApplyToSpawnerByName"),
    ("0x005da660", "1", "CSpawnerSquadSize__ApplyToSpawnerByName"),
    ("0x005da674", "1", "CSpawnerAmount__ApplyToSpawnerByName"),
    ("0x005da688", "1", "CSpawnerDelay__ApplyToSpawnerByName"),
    ("0x005da69c", "1", "CSpawnerUnit__ApplyToSpawnerByName"),
    ("0x005da69c", "2", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize"),
    ("0x005da69c", "3", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer"),
    ("0x005da6b0", "0", "CPhysicsSpawnerValue__scalar_deleting_dtor"),
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
        "schema": "ghidra-spawner-value-tranche.v1",
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
    parser.add_argument("--out", type=Path, default=BASE / "spawner-value-tranche.json")
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
