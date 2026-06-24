#!/usr/bin/env python3
"""Validate the saved Ghidra PhysicsScript statement tranche 2."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "physics-script-statements-wave332" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave332",
    "physics-script",
    "statement-tranche",
    "retail-binary-evidence",
]

TARGETS: dict[str, dict[str, object]] = {
    "0x00430330": {
        "name": "CPhysicsRoundValueList__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CPhysicsRoundValueList__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["CreateStatementType5", "recursively loads", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "statement-load"],
    },
    "0x00430410": {
        "name": "CPhysicsRoundValueList__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsRoundValueList__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "next-node", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "destructor"],
    },
    "0x00430450": {
        "name": "CRoundStatement__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CRoundStatement__scalar_deleting_dtor", "int flags"],
        "comment": ["CRoundStatement__dtor", "scalar-delete", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00430470": {
        "name": "CRoundStatement__dtor",
        "signature": ["void", "__fastcall", "CRoundStatement__dtor", "void * this"],
        "comment": ["destructor body", "+0x10c", "base vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x004304d0": {
        "name": "CSpawnerStatement__CreateSpawnerAndRecurse",
        "signature": ["void", "__fastcall", "CSpawnerStatement__CreateSpawnerAndRecurse", "void * this"],
        "comment": ["vtable slot +0x4", "spawner data", "child statement", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-update"],
    },
    "0x00430510": {
        "name": "CSpawnerData__CreateAndRegisterByName",
        "signature": ["void", "__cdecl", "CSpawnerData__CreateAndRegisterByName", "char * name"],
        "comment": ["0x3c", "DAT_008553f4", "default spawner", "remain unproven"],
        "tags": COMMON_TAGS + ["physics-object-registry"],
    },
    "0x00430610": {
        "name": "CSpawnerData__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CSpawnerData__scalar_deleting_dtor", "int flags"],
        "comment": ["spawner-data", "+0x4", "+0x8", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00430660": {
        "name": "CSpawnerStatement__GetSerializedSize",
        "signature": ["int", "__fastcall", "CSpawnerStatement__GetSerializedSize", "void * this"],
        "comment": ["missing top-level", "name string", "spawner value-list", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "serialized-size"],
    },
    "0x004306b0": {
        "name": "CPhysicsSpawnerValueList__GetSerializedSize",
        "signature": ["int", "__fastcall", "CPhysicsSpawnerValueList__GetSerializedSize", "void * this"],
        "comment": ["CPhysicsSpawnerValueList", "not the top-level", "recursive", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "serialized-size"],
    },
    "0x004306e0": {
        "name": "CSpawnerStatement__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CSpawnerStatement__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["missing", "CDXMemBuffer", "CreateStatementType6", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "statement-load"],
    },
    "0x00430800": {
        "name": "CPhysicsSpawnerValueList__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CPhysicsSpawnerValueList__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["CreateStatementType6", "recursively loads", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "statement-load"],
    },
    "0x004308e0": {
        "name": "CPhysicsSpawnerValueList__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsSpawnerValueList__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "next-node", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "destructor"],
    },
    "0x00430920": {
        "name": "CSpawnerStatement__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CSpawnerStatement__scalar_deleting_dtor", "int flags"],
        "comment": ["CSpawnerStatement__dtor", "scalar-delete", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00430940": {
        "name": "CSpawnerStatement__dtor",
        "signature": ["void", "__fastcall", "CSpawnerStatement__dtor", "void * this"],
        "comment": ["destructor body", "+0x10c", "base vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x004309a0": {
        "name": "CExplosionStatement__CreateExplosionAndRecurse",
        "signature": ["void", "__fastcall", "CExplosionStatement__CreateExplosionAndRecurse", "void * this"],
        "comment": ["vtable slot +0x4", "explosion data", "child statement", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-update"],
    },
    "0x004309e0": {
        "name": "CExplosionStatement__Create",
        "signature": ["void", "__cdecl", "CExplosionStatement__Create", "char * name"],
        "comment": ["0x50", "DAT_008553f8", "explosion-like", "remain unproven"],
        "tags": COMMON_TAGS + ["physics-object-registry"],
    },
    "0x00430ae0": {
        "name": "CExplosionStatement__GetSerializedSize",
        "signature": ["int", "__fastcall", "CExplosionStatement__GetSerializedSize", "void * this"],
        "comment": ["missing top-level", "name string", "explosion value-list", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "serialized-size"],
    },
    "0x00430b30": {
        "name": "CPhysicsExplosionValueList__GetSerializedSize",
        "signature": ["int", "__fastcall", "CPhysicsExplosionValueList__GetSerializedSize", "void * this"],
        "comment": ["not a UnitAI", "CPhysicsExplosionValueList", "recursive", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "serialized-size"],
    },
    "0x00430b60": {
        "name": "CExplosionStatement__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CExplosionStatement__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["missing", "CDXMemBuffer", "CreateStatementType7", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "statement-load"],
    },
    "0x00430c80": {
        "name": "CPhysicsExplosionValueList__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CPhysicsExplosionValueList__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["CreateStatementType7", "recursively loads", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "statement-load"],
    },
    "0x00430d60": {
        "name": "CPhysicsExplosionValueList__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsExplosionValueList__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "next-node", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "destructor"],
    },
    "0x00430da0": {
        "name": "CExplosionStatement__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CExplosionStatement__scalar_deleting_dtor", "int flags"],
        "comment": ["CExplosionStatement__dtor", "scalar-delete", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00430dc0": {
        "name": "CExplosionStatement__dtor",
        "signature": ["void", "__fastcall", "CExplosionStatement__dtor", "void * this"],
        "comment": ["destructor body", "+0x10c", "base vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00430e20": {
        "name": "CComponentStatement__CreateComponentAndRecurse",
        "signature": ["void", "__fastcall", "CComponentStatement__CreateComponentAndRecurse", "void * this"],
        "comment": ["vtable slot +0x4", "component data", "child statement", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-update"],
    },
    "0x00430e60": {
        "name": "CComponentStatement__CreateAndRegisterByName",
        "signature": ["void", "__cdecl", "CComponentStatement__CreateAndRegisterByName", "char * name"],
        "comment": ["0x1ac", "DAT_00855400", "Fenrir", "remain unproven"],
        "tags": COMMON_TAGS + ["physics-object-registry"],
    },
    "0x00430fa0": {
        "name": "CStatementChain__InvokeVFunc04OnNodes",
        "signature": ["void", "__thiscall", "CStatementChain__InvokeVFunc04OnNodes", "void * context"],
        "comment": ["walks chained", "vtable slot +0x4", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-chain"],
    },
    "0x00430fd0": {
        "name": "CComponentStatement__GetSerializedSize",
        "signature": ["int", "__fastcall", "CComponentStatement__GetSerializedSize", "void * this"],
        "comment": ["missing top-level", "name string", "component value-list", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "serialized-size"],
    },
    "0x00431020": {
        "name": "CPhysicsComponentValueList__GetSerializedSize",
        "signature": ["int", "__fastcall", "CPhysicsComponentValueList__GetSerializedSize", "void * this"],
        "comment": ["CPhysicsComponentValueList", "not the top-level", "recursive", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "serialized-size"],
    },
    "0x00431050": {
        "name": "CComponentStatement__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CComponentStatement__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["missing", "CDXMemBuffer", "CreateStatementType10", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "statement-load"],
    },
    "0x00431170": {
        "name": "CPhysicsComponentValueList__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CPhysicsComponentValueList__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["CreateStatementType10", "recursively loads", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "statement-load"],
    },
    "0x00431250": {
        "name": "CPhysicsComponentValueList__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsComponentValueList__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "next-node", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "destructor"],
    },
}

STALE_NAMES = [
    "CPhysicsRoundValueList__ctor_like_00430330",
    "CPhysicsRoundValueList__VFunc_00_00430410",
    "CRoundStatement__VFunc_00_00430450",
    "CRoundStatement__ctor_like_00430470",
    "CSpawnerStatement__VFunc_01_004304d0",
    "CSpawnerData__ctor_like_00430510",
    "CSpawnerData__VFunc_00_00430610",
    "CPhysicsSpawnerValueList__ctor_like_00430800",
    "CPhysicsSpawnerValueList__VFunc_00_004308e0",
    "CSpawnerStatement__VFunc_00_00430920",
    "CSpawnerStatement__ctor_like_00430940",
    "CExplosionStatement__VFunc_01_004309a0",
    "CExplosionStatement__AllocObjectAndAddToSet",
    "CUnitAI__ComputeRecursiveNodeSize_NodeTreeA",
    "CPhysicsExplosionValueList__ctor_like_00430c80",
    "CPhysicsExplosionValueList__VFunc_00_00430d60",
    "CExplosionStatement__VFunc_00_00430da0",
    "CExplosionStatement__ctor_like_00430dc0",
    "CComponentStatement__VFunc_01_00430e20",
    "CComponentStatement__AllocObjectAndAddToSet",
    "CPhysicsComponentValueList__ctor_like_00431170",
    "CPhysicsComponentValueList__VFunc_00_00431250",
]

EXPECTED_XREFS = (
    ("0x00430660", "<no_function>"),
    ("0x004306b0", "CSpawnerStatement__GetSerializedSize"),
    ("0x004306e0", "<no_function>"),
    ("0x00430800", "CSpawnerStatement__LoadFromMemBuffer"),
    ("0x00430ae0", "<no_function>"),
    ("0x00430b30", "CExplosionStatement__GetSerializedSize"),
    ("0x00430b60", "<no_function>"),
    ("0x00430c80", "CExplosionStatement__LoadFromMemBuffer"),
    ("0x00430fa0", "CComponentStatement__CreateComponentAndRecurse"),
    ("0x00430fd0", "<no_function>"),
    ("0x00431020", "CComponentStatement__GetSerializedSize"),
    ("0x00431050", "<no_function>"),
    ("0x00431170", "CComponentStatement__LoadFromMemBuffer"),
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
        "schema": "ghidra-physics-script-statement-tranche2.v1",
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
    out_path = base / "physics-script-statement-tranche2.json"
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
