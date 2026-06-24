#!/usr/bin/env python3
"""Validate the saved Ghidra PhysicsScript statement tranche 3."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "physics-script-statements-wave333" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave333",
    "physics-script",
    "statement-tranche",
    "retail-binary-evidence",
]

TARGETS: dict[str, dict[str, object]] = {
    "0x00431290": {
        "name": "CComponentStatement__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CComponentStatement__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "CComponentStatement__dtor", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x004312b0": {
        "name": "CComponentStatement__dtor",
        "signature": ["void", "__fastcall", "CComponentStatement__dtor", "void * this"],
        "comment": ["destructor body", "+0x10c", "base vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00431310": {
        "name": "CFeatureStatement__CreateFeatureAndRecurse",
        "signature": ["void", "__fastcall", "CFeatureStatement__CreateFeatureAndRecurse", "void * this"],
        "comment": ["vtable slot +0x4", "feature data", "child statement", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-update"],
    },
    "0x00431350": {
        "name": "CFeatureStatement__CreateAndRegisterByName",
        "signature": ["void", "__cdecl", "CFeatureStatement__CreateAndRegisterByName", "char * name"],
        "comment": ["0x24", "DAT_00855404", "feature-like", "remain unproven"],
        "tags": COMMON_TAGS + ["physics-object-registry"],
    },
    "0x00431420": {
        "name": "CFeatureStatement__GetSerializedSize",
        "signature": ["int", "__fastcall", "CFeatureStatement__GetSerializedSize", "void * this"],
        "comment": ["missing top-level", "name string", "feature value-list", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "serialized-size"],
    },
    "0x00431470": {
        "name": "CPhysicsFeatureValueList__GetSerializedSize",
        "signature": ["int", "__fastcall", "CPhysicsFeatureValueList__GetSerializedSize", "void * this"],
        "comment": ["not a UnitAI", "CPhysicsFeatureValueList", "recursive", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "serialized-size"],
    },
    "0x004314a0": {
        "name": "CFeatureStatement__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CFeatureStatement__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["missing", "CDXMemBuffer", "CreateStatementType8", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "statement-load"],
    },
    "0x004315c0": {
        "name": "CPhysicsFeatureValueList__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CPhysicsFeatureValueList__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["CreateStatementType8", "recursively loads", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "statement-load"],
    },
    "0x004316a0": {
        "name": "CPhysicsFeatureValueList__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsFeatureValueList__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "next-node", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "destructor"],
    },
    "0x004316e0": {
        "name": "CFeatureStatement__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CFeatureStatement__scalar_deleting_dtor", "int flags"],
        "comment": ["CFeatureStatement__dtor", "scalar-delete", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00431700": {
        "name": "CFeatureStatement__dtor",
        "signature": ["void", "__fastcall", "CFeatureStatement__dtor", "void * this"],
        "comment": ["destructor body", "+0x10c", "base vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00431760": {
        "name": "CHazardStatement__CreateHazardAndRecurse",
        "signature": ["void", "__fastcall", "CHazardStatement__CreateHazardAndRecurse", "void * this"],
        "comment": ["vtable slot +0x4", "hazard data", "child statement", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-update"],
    },
    "0x004317a0": {
        "name": "CHazardStatement__CreateAndRegisterByName",
        "signature": ["void", "__cdecl", "CHazardStatement__CreateAndRegisterByName", "char * name"],
        "comment": ["0x1c", "DAT_00855408", "hazard-like", "remain unproven"],
        "tags": COMMON_TAGS + ["physics-object-registry"],
    },
    "0x00431870": {
        "name": "CHazardStatement__GetSerializedSize",
        "signature": ["int", "__fastcall", "CHazardStatement__GetSerializedSize", "void * this"],
        "comment": ["missing top-level", "name string", "hazard value-list", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "serialized-size"],
    },
    "0x004318c0": {
        "name": "CPhysicsHazardValueList__GetSerializedSize",
        "signature": ["int", "__fastcall", "CPhysicsHazardValueList__GetSerializedSize", "void * this"],
        "comment": ["not a UnitAI", "CPhysicsHazardValueList", "recursive", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "serialized-size"],
    },
    "0x004318f0": {
        "name": "CHazardStatement__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CHazardStatement__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["missing", "CDXMemBuffer", "CreateStatementType9", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "statement-load"],
    },
    "0x00431a10": {
        "name": "CPhysicsHazardValueList__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CPhysicsHazardValueList__LoadFromMemBuffer", "void * memBuffer"],
        "comment": ["CreateStatementType9", "recursively loads", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "statement-load"],
    },
    "0x00431af0": {
        "name": "CPhysicsHazardValueList__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsHazardValueList__scalar_deleting_dtor", "int flags"],
        "comment": ["scalar-deleting", "next-node", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "destructor"],
    },
    "0x00431b30": {
        "name": "CHazardStatement__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CHazardStatement__scalar_deleting_dtor", "int flags"],
        "comment": ["CHazardStatement__dtor", "scalar-delete", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00431b50": {
        "name": "CHazardStatement__dtor",
        "signature": ["void", "__fastcall", "CHazardStatement__dtor", "void * this"],
        "comment": ["destructor body", "+0x10c", "base vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x00431bb0": {
        "name": "CPhysicsScriptStatements__CreateStatementType2",
        "signature": ["void *", "__cdecl", "CPhysicsScriptStatements__CreateStatementType2", "int valueType"],
        "comment": ["type-2/unit value", "0x46", "returns null", "remain unproven"],
        "tags": COMMON_TAGS + ["value-factory"],
    },
}

STALE_NAMES = [
    "CComponentStatement__VFunc_00_00431290",
    "CComponentStatement__ctor_like_004312b0",
    "CFeatureStatement__VFunc_01_00431310",
    "CFeatureStatement__AllocObjectAndAddToSet",
    "CUnitAI__ComputeRecursiveNodeSize_NodeTreeB",
    "CPhysicsFeatureValueList__ctor_like_004315c0",
    "CPhysicsFeatureValueList__VFunc_00_004316a0",
    "CFeatureStatement__VFunc_00_004316e0",
    "CFeatureStatement__ctor_like_00431700",
    "CHazardStatement__VFunc_01_00431760",
    "CHazardStatement__AllocObjectAndAddToSet",
    "CUnitAI__ComputeRecursiveNodeSize_NodeTreeC",
    "CPhysicsHazardValueList__ctor_like_00431a10",
    "CPhysicsHazardValueList__VFunc_00_00431af0",
    "CHazardStatement__VFunc_00_00431b30",
    "CHazardStatement__ctor_like_00431b50",
]

EXPECTED_XREFS = (
    ("0x00431290", "<no_function>"),
    ("0x004312b0", "CComponentStatement__scalar_deleting_dtor"),
    ("0x00431310", "<no_function>"),
    ("0x00431350", "CFeatureStatement__CreateFeatureAndRecurse"),
    ("0x00431420", "<no_function>"),
    ("0x00431470", "CFeatureStatement__GetSerializedSize"),
    ("0x00431470", "CPhysicsFeatureValueList__GetSerializedSize"),
    ("0x004314a0", "<no_function>"),
    ("0x004315c0", "CFeatureStatement__LoadFromMemBuffer"),
    ("0x004315c0", "CPhysicsFeatureValueList__LoadFromMemBuffer"),
    ("0x004316a0", "<no_function>"),
    ("0x004316e0", "<no_function>"),
    ("0x00431700", "CFeatureStatement__scalar_deleting_dtor"),
    ("0x00431760", "<no_function>"),
    ("0x004317a0", "CHazardStatement__CreateHazardAndRecurse"),
    ("0x00431870", "<no_function>"),
    ("0x004318c0", "CHazardStatement__GetSerializedSize"),
    ("0x004318c0", "CPhysicsHazardValueList__GetSerializedSize"),
    ("0x004318f0", "<no_function>"),
    ("0x00431a10", "CHazardStatement__LoadFromMemBuffer"),
    ("0x00431a10", "CPhysicsHazardValueList__LoadFromMemBuffer"),
    ("0x00431af0", "<no_function>"),
    ("0x00431b30", "<no_function>"),
    ("0x00431b50", "CHazardStatement__scalar_deleting_dtor"),
    ("0x00431bb0", "CUnitStatement__LoadFromMemBuffer"),
    ("0x00431bb0", "CPhysicsUnitValueList__LoadFromMemBuffer"),
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
        "schema": "ghidra-physics-script-statement-tranche3.v1",
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
    out_path = base / "physics-script-statement-tranche3.json"
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
