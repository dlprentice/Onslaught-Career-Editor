#!/usr/bin/env python3
"""Validate the saved Ghidra round value tail tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "round-values-tail-wave338" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave338",
    "physics-script",
    "round-value-tail-tranche",
    "retail-binary-evidence",
]

TARGETS: dict[str, dict[str, object]] = {
    "0x00437fe0": {
        "name": "CPhysicsRoundValue__SetOwnedAuxStringAt0C",
        "signature": ["void", "__thiscall", "CPhysicsRoundValue__SetOwnedAuxStringAt0C", "char * sourceString"],
        "comment": ["+0xc", "OID__AllocObject", "0x23c", "remain unproven"],
        "tags": COMMON_TAGS + ["owned-string-copy", "round-value"],
    },
    "0x00438050": {
        "name": "CPhysicsRoundValue__SetOwnedValueStringAt08",
        "signature": ["void", "__thiscall", "CPhysicsRoundValue__SetOwnedValueStringAt08", "char * sourceString"],
        "comment": ["stale CUnitAI", "+0x8", "owned value string", "remain unproven"],
        "tags": COMMON_TAGS + ["owned-string-copy", "round-value", "supersedes-stale-unitai-owner"],
    },
    "0x004380c0": {
        "name": "CPhysicsRoundValue__dtor_base",
        "signature": ["void", "__fastcall", "CPhysicsRoundValue__dtor_base", "void * this"],
        "comment": ["destructor body", "0x005da584", "0x004380d0", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "round-value"],
    },
    "0x004380d0": {
        "name": "CPhysicsRoundValue__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsRoundValue__scalar_deleting_dtor", "int flags"],
        "comment": ["Recovered function boundary", "0x005da584", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "destructor", "round-value"],
    },
    "0x00438400": {
        "name": "CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor", "int flags"],
        "comment": ["shared", "leaf", "0x004380c0", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "round-value", "shared-vtable-slot"],
    },
    "0x00438b40": {
        "name": "CRoundGridOfFear__ApplyToRoundByName",
        "signature": ["void", "__thiscall", "CRoundGridOfFear__ApplyToRoundByName", "char * roundName"],
        "comment": ["DAT_008553f0", "+0x58", "ROUND", "remain unproven"],
        "tags": COMMON_TAGS + ["round-apply", "numeric-round-value"],
    },
    "0x004394e0": {
        "name": "CRoundSeek__ApplyToRoundByName",
        "signature": ["void", "__thiscall", "CRoundSeek__ApplyToRoundByName", "char * roundName"],
        "comment": ["Recovered function boundary", "+0x48", "child value", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "round-apply", "nested-round-value"],
    },
    "0x00439580": {
        "name": "CRoundSeek__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CRoundSeek__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["CDXMemBuffer", "CreateStatementType11", "+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-load", "nested-round-value"],
    },
    "0x004395b0": {
        "name": "CRoundSeek__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CRoundSeek__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "0x004395d0", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "nested-round-value"],
    },
    "0x004395d0": {
        "name": "CRoundSeek__dtor_base",
        "signature": ["void", "__fastcall", "CRoundSeek__dtor_base", "void * this"],
        "comment": ["destructor body", "+0x8", "base vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "nested-round-value"],
    },
    "0x00439620": {
        "name": "CRoundMesh__ApplyToRoundByName",
        "signature": ["void", "__thiscall", "CRoundMesh__ApplyToRoundByName", "char * roundName"],
        "comment": ["DAT_008553f0", "+0xc", "owned", "remain unproven"],
        "tags": COMMON_TAGS + ["round-apply", "owned-string-copy"],
    },
    "0x00439710": {
        "name": "CRoundEffect__ApplyToRoundByName",
        "signature": ["void", "__thiscall", "CRoundEffect__ApplyToRoundByName", "char * roundName"],
        "comment": ["DAT_008553f0", "+0x10", "owned", "remain unproven"],
        "tags": COMMON_TAGS + ["round-apply", "owned-string-copy"],
    },
    "0x00439800": {
        "name": "CRoundWaterEffect__ApplyToRoundByName",
        "signature": ["void", "__thiscall", "CRoundWaterEffect__ApplyToRoundByName", "char * roundName"],
        "comment": ["DAT_008553f0", "+0x14", "owned", "remain unproven"],
        "tags": COMMON_TAGS + ["round-apply", "owned-string-copy"],
    },
    "0x00439910": {
        "name": "CRoundExplosion__ApplyToRoundByName",
        "signature": ["void", "__thiscall", "CRoundExplosion__ApplyToRoundByName", "char * roundName"],
        "comment": ["DAT_008553f0", "+0x8", "owned", "remain unproven"],
        "tags": COMMON_TAGS + ["round-apply", "owned-string-copy"],
    },
    "0x00439a00": {
        "name": "CRoundTreeCollision__ApplyToRoundByName",
        "signature": ["void", "__thiscall", "CRoundTreeCollision__ApplyToRoundByName", "char * roundName"],
        "comment": ["Recovered function boundary", "+0xa4", "child value", "remain unproven"],
        "tags": COMMON_TAGS + ["function-boundary", "round-apply", "nested-round-value"],
    },
    "0x00439aa0": {
        "name": "CRoundTreeCollision__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CRoundTreeCollision__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["CDXMemBuffer", "CreateStatementType15", "+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-load", "nested-round-value"],
    },
    "0x00439ad0": {
        "name": "CRoundTreeCollision__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CRoundTreeCollision__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "0x00439af0", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "nested-round-value"],
    },
    "0x00439af0": {
        "name": "CRoundTreeCollision__dtor_base",
        "signature": ["void", "__fastcall", "CRoundTreeCollision__dtor_base", "void * this"],
        "comment": ["destructor body", "+0x8", "base vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor", "nested-round-value"],
    },
}

STALE_NAMES = [
    "CPhysicsScriptStatements__SetOwnedString",
    "CUnitAI__SetOwnedDebugString",
    "CPhysicsRoundValue__ctor_like_004380c0",
    "VFuncSlot_00_00438400",
    "CRoundGridOfFear__VFunc_01_00438b40",
    "CRoundSeek__VFunc_03_00439580",
    "CRoundSeek__VFunc_00_004395b0",
    "CRoundSeek__ctor_like_004395d0",
    "CRoundMesh__VFunc_01_00439620",
    "CRoundEffect__VFunc_01_00439710",
    "CRoundWaterEffect__VFunc_01_00439800",
    "CRoundExplosion__VFunc_01_00439910",
    "CRoundTreeCollision__VFunc_03_00439aa0",
    "CRoundTreeCollision__VFunc_00_00439ad0",
    "CRoundTreeCollision__ctor_like_00439af0",
]

EXPECTED_XREFS = (
    ("0x00437fe0", "<no_function>"),
    ("0x00438050", "<no_function>"),
    ("0x004380c0", "CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor"),
    ("0x004380d0", "<no_function>"),
    ("0x00438400", "<no_function>"),
    ("0x004394e0", "<no_function>"),
    ("0x00439580", "<no_function>"),
    ("0x00439a00", "<no_function>"),
    ("0x00439aa0", "<no_function>"),
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
        "schema": "ghidra-round-value-tail-tranche.v1",
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
    out_path = base / "round-value-tail-tranche.json"
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
