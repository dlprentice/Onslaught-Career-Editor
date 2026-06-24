#!/usr/bin/env python3
"""Validate the saved Ghidra feature-value tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "feature-values-wave341" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave341",
    "physics-script",
    "feature-value-tranche",
    "retail-binary-evidence",
]

TARGETS: dict[str, dict[str, object]] = {
    "0x0043b990": {
        "name": "CPhysicsScriptStatements__CreateStatementType8",
        "signature": ["void *", "__cdecl", "CPhysicsScriptStatements__CreateStatementType8", "int valueType"],
        "comment": ["type-8", "feature-value", "0x005da804", "0x005da87c", "remain unproven"],
        "tags": COMMON_TAGS + ["value-factory", "feature-value"],
    },
    "0x0043bb30": {
        "name": "CFeatureScalar18__ApplyToFeatureByName",
        "signature": ["void", "__thiscall", "CFeatureScalar18__ApplyToFeatureByName", "char * featureName"],
        "comment": ["Recovered function boundary", "DAT_00855404", "record+0x18", "this+0x8", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "feature-apply", "offset-backed-scalar"],
    },
    "0x0043bbc0": {
        "name": "CPhysicsFeatureValue__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsFeatureValue__scalar_deleting_dtor", "int flags"],
        "comment": ["Recovered function boundary", "0x005da890", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "destructor", "value-base"],
    },
    "0x0043bbf0": {
        "name": "CFeatureScalar1C__ApplyToFeatureByName",
        "signature": ["void", "__thiscall", "CFeatureScalar1C__ApplyToFeatureByName", "char * featureName"],
        "comment": ["Recovered function boundary", "DAT_00855404", "record+0x1c", "this+0x8", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "feature-apply", "offset-backed-scalar"],
    },
    "0x0043bc80": {
        "name": "CFeatureFlag10__ApplyToFeatureByName",
        "signature": ["void", "__thiscall", "CFeatureFlag10__ApplyToFeatureByName", "char * featureName"],
        "comment": ["Recovered function boundary", "DAT_00855404", "record+0x10", "nonzero", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "feature-apply", "offset-backed-flag"],
    },
    "0x0043bd40": {
        "name": "CFeatureFlag14__ApplyToFeatureByName",
        "signature": ["void", "__thiscall", "CFeatureFlag14__ApplyToFeatureByName", "char * featureName"],
        "comment": ["Recovered function boundary", "DAT_00855404", "record+0x14", "nonzero", "not yet proven"],
        "tags": COMMON_TAGS + ["function-boundary", "feature-apply", "offset-backed-flag"],
    },
    "0x0043be00": {
        "name": "CPhysicsFeatureValue__dtor_base",
        "signature": ["void", "__fastcall", "CPhysicsFeatureValue__dtor_base", "void * this"],
        "comment": ["destructor body", "0x005da890", "0x0043bbc0", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "value-base"],
    },
    "0x0043be10": {
        "name": "CFeatureMesh__ApplyToFeatureByName",
        "signature": ["void", "__thiscall", "CFeatureMesh__ApplyToFeatureByName", "char * featureName"],
        "comment": ["DAT_00855404", "owned mesh string", "record+0x0", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["feature-apply", "owned-string-copy"],
    },
    "0x0043bf00": {
        "name": "CFeatureNoise__ApplyToFeatureByName",
        "signature": ["void", "__thiscall", "CFeatureNoise__ApplyToFeatureByName", "char * featureName"],
        "comment": ["DAT_00855404", "owned noise string", "record+0xc", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["feature-apply", "owned-string-copy"],
    },
    "0x0043bff0": {
        "name": "CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor", "int flags"],
        "comment": ["shared", "0x0043be00", "OID__FreeObject", "leaf", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "shared-vtable-slot"],
    },
    "0x0043c010": {
        "name": "CFeatureTexture__ApplyToFeatureByName",
        "signature": ["void", "__thiscall", "CFeatureTexture__ApplyToFeatureByName", "char * featureName"],
        "comment": ["Recovered function boundary", "DAT_00855404", "CVBufTexture__SetNameListIndexOrMinusOne", "this+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "feature-apply", "texture-name"],
    },
}

STALE_NAMES = [
    "CPhysicsFeatureValue__ctor_like_0043be00",
    "CFeatureMesh__VFunc_01_0043be10",
    "CFeatureNoise__VFunc_01_0043bf00",
    "VFuncSlot_00_0043bff0",
]

EXPECTED_XREFS = [
    ("0x0043b990", "0x00431516"),
    ("0x0043b990", "0x004315ec"),
    ("0x0043bb30", "0x005da880"),
    ("0x0043bbc0", "0x005da890"),
    ("0x0043bbf0", "0x005da808"),
    ("0x0043bc80", "0x005da830"),
    ("0x0043bd40", "0x005da81c"),
    ("0x0043be00", "0x0043bff3"),
    ("0x0043be10", "0x005da86c"),
    ("0x0043bf00", "0x005da844"),
    ("0x0043bff0", "0x005da804"),
    ("0x0043c010", "0x005da858"),
]

EXPECTED_VTABLE_SLOTS = [
    ("0x005da890", "0", "CPhysicsFeatureValue__scalar_deleting_dtor"),
    ("0x005da87c", "0", "CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor"),
    ("0x005da87c", "1", "CFeatureScalar18__ApplyToFeatureByName"),
    ("0x005da87c", "2", "CPhysicsScriptValue__GetScalarSerializedSize4"),
    ("0x005da87c", "3", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer"),
    ("0x005da868", "0", "CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor"),
    ("0x005da868", "1", "CFeatureMesh__ApplyToFeatureByName"),
    ("0x005da868", "2", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize"),
    ("0x005da868", "3", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer"),
    ("0x005da854", "1", "CFeatureTexture__ApplyToFeatureByName"),
    ("0x005da82c", "1", "CFeatureFlag10__ApplyToFeatureByName"),
    ("0x005da840", "1", "CFeatureNoise__ApplyToFeatureByName"),
    ("0x005da818", "1", "CFeatureFlag14__ApplyToFeatureByName"),
    ("0x005da804", "1", "CFeatureScalar1C__ApplyToFeatureByName"),
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
        "schema": "ghidra-feature-value-tranche.v1",
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
    parser.add_argument("--out", type=Path, default=BASE / "feature-value-tranche.json")
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
