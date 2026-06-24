#!/usr/bin/env python3
"""Validate the saved Ghidra PhysicsScript statement tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "physics-script-statements-wave331" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave331",
    "physics-script",
    "statement-tranche",
    "retail-binary-evidence",
]

TARGETS: dict[str, dict[str, object]] = {
    "0x0042ede0": {
        "name": "CUnitStatement__CreateUnitAndRecurse",
        "signature": ["void", "__fastcall", "CUnitStatement__CreateUnitAndRecurse", "void * this"],
        "comment": ["missing", "vtable slot +0x4", "UnitAI", "child statement", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "statement-update"],
    },
    "0x0042ee90": {
        "name": "CUnitAI__CreateAndRegisterByName",
        "signature": ["void", "__cdecl", "CUnitAI__CreateAndRegisterByName", "char * name"],
        "comment": ["0x1ac", "name at +0xb0", "CUnitAI__InitDefaults", "Fenrir", "remain unproven"],
        "tags": COMMON_TAGS + ["physics-object-registry"],
    },
    "0x0042efd0": {
        "name": "CUnitAI__InitDefaults",
        "signature": ["void", "__fastcall", "CUnitAI__InitDefaults", "void * unitAI"],
        "comment": ["default", "m_b_rubble", "float constants", "0x1a8", "remain unproven"],
        "tags": COMMON_TAGS + ["unitai-defaults"],
    },
    "0x0042f230": {
        "name": "CUnitStatement__GetSerializedSize",
        "signature": ["int", "__fastcall", "CUnitStatement__GetSerializedSize", "void * this"],
        "comment": ["missing", "name string", "value-list", "recursive", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "serialized-size"],
    },
    "0x0042f280": {
        "name": "CPhysicsUnitValueList__GetSerializedSize",
        "signature": ["int", "__fastcall", "CPhysicsUnitValueList__GetSerializedSize", "void * this"],
        "comment": ["CPhysicsUnitValueList", "recursive", "vtable slot +0x8", "not a UnitAI", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "serialized-size"],
    },
    "0x0042f2b0": {
        "name": "CUnitStatement__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CUnitStatement__LoadFromMemBuffer", "void * this", "void * memBuffer"],
        "comment": ["missing", "CDXMemBuffer", "CreateStatementType2", "skip", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "statement-load"],
    },
    "0x0042f3d0": {
        "name": "CPhysicsUnitValueList__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CPhysicsUnitValueList__LoadFromMemBuffer", "void * this", "void * memBuffer"],
        "comment": ["CPhysicsUnitValueList node", "CreateStatementType2", "recursive", "terminator", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "statement-load"],
    },
    "0x0042f4b0": {
        "name": "CPhysicsUnitValueList__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsUnitValueList__scalar_deleting_dtor", "void * this", "int flags"],
        "comment": ["scalar-delete", "child", "next-node", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "destructor"],
    },
    "0x0042f4f0": {
        "name": "CUnitStatement__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CUnitStatement__scalar_deleting_dtor", "void * this", "int flags"],
        "comment": ["scalar-delete", "CUnitStatement__dtor", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x0042f510": {
        "name": "CUnitStatement__dtor",
        "signature": ["void", "__fastcall", "CUnitStatement__dtor", "void * this"],
        "comment": ["destructor body", "child pointer at +0x10c", "base vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x0042f570": {
        "name": "CPhysicsScriptStatement__dtor",
        "signature": ["void", "__fastcall", "CPhysicsScriptStatement__dtor", "void * this"],
        "comment": ["base statement", "vtable at 0x005d9894", "unwind", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x0042f580": {
        "name": "CPhysicsScriptStatement__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsScriptStatement__scalar_deleting_dtor", "void * this", "int flags"],
        "comment": ["missing", "scalar-delete", "base vtable", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "destructor"],
    },
    "0x0042f5b0": {
        "name": "CWeaponStatement__CreateWeaponAndRecurse",
        "signature": ["void", "__fastcall", "CWeaponStatement__CreateWeaponAndRecurse", "void * this"],
        "comment": ["vtable slot +0x4", "creates/registers a weapon", "child statement", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-update"],
    },
    "0x0042f5f0": {
        "name": "CWeaponStatement__Create",
        "signature": ["void", "__cdecl", "CWeaponStatement__Create", "char * name"],
        "comment": ["0x4c", "DAT_008553e8", "name", "default", "remain unproven"],
        "tags": COMMON_TAGS + ["physics-object-registry"],
    },
    "0x0042f700": {
        "name": "CWeaponStatement__GetSerializedSize",
        "signature": ["int", "__fastcall", "CWeaponStatement__GetSerializedSize", "void * this"],
        "comment": ["missing", "name string", "weapon value-list", "recursive", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "serialized-size"],
    },
    "0x0042f750": {
        "name": "CPhysicsWeaponValueList__GetSerializedSize",
        "signature": ["int", "__fastcall", "CPhysicsWeaponValueList__GetSerializedSize", "void * this"],
        "comment": ["CPhysicsWeaponValueList", "recursive", "not the top-level CWeaponStatement", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "serialized-size"],
    },
    "0x0042f780": {
        "name": "CWeaponStatement__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CWeaponStatement__LoadFromMemBuffer", "void * this", "void * memBuffer"],
        "comment": ["missing", "CDXMemBuffer", "CreateStatementType3", "skip", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "statement-load"],
    },
    "0x0042f8a0": {
        "name": "CPhysicsWeaponValueList__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CPhysicsWeaponValueList__LoadFromMemBuffer", "void * this", "void * memBuffer"],
        "comment": ["CPhysicsWeaponValueList node", "CreateStatementType3", "recursive", "terminator", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "statement-load"],
    },
    "0x0042f980": {
        "name": "CPhysicsWeaponValueList__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsWeaponValueList__scalar_deleting_dtor", "void * this", "int flags"],
        "comment": ["scalar-delete", "child", "next-node", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "destructor"],
    },
    "0x0042f9c0": {
        "name": "CWeaponStatement__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CWeaponStatement__scalar_deleting_dtor", "void * this", "int flags"],
        "comment": ["scalar-delete", "CWeaponStatement__dtor", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x0042f9e0": {
        "name": "CWeaponStatement__dtor",
        "signature": ["void", "__fastcall", "CWeaponStatement__dtor", "void * this"],
        "comment": ["destructor body", "child pointer at +0x10c", "base vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x0042fa40": {
        "name": "CWeaponModeStatement__CreateWeaponModeAndRecurse",
        "signature": ["void", "__fastcall", "CWeaponModeStatement__CreateWeaponModeAndRecurse", "void * this"],
        "comment": ["vtable slot +0x4", "creates/registers a weapon mode", "child statement", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-update"],
    },
    "0x0042fa80": {
        "name": "CWeaponModeStatement__Create",
        "signature": ["void", "__cdecl", "CWeaponModeStatement__Create", "char * name"],
        "comment": ["0xc0", "DAT_008553ec", "name", "default", "remain unproven"],
        "tags": COMMON_TAGS + ["physics-object-registry"],
    },
    "0x0042fc20": {
        "name": "CWeaponModeStatement__GetSerializedSize",
        "signature": ["int", "__fastcall", "CWeaponModeStatement__GetSerializedSize", "void * this"],
        "comment": ["missing", "name string", "weapon-mode value-list", "recursive", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "serialized-size"],
    },
    "0x0042fc70": {
        "name": "CPhysicsWeaponModeValueList__GetSerializedSize",
        "signature": ["int", "__fastcall", "CPhysicsWeaponModeValueList__GetSerializedSize", "void * this"],
        "comment": ["CPhysicsWeaponModeValueList", "recursive", "not the top-level CWeaponModeStatement", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "serialized-size"],
    },
    "0x0042fca0": {
        "name": "CWeaponModeStatement__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CWeaponModeStatement__LoadFromMemBuffer", "void * this", "void * memBuffer"],
        "comment": ["missing", "CDXMemBuffer", "CreateStatementType4", "skip", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "statement-load"],
    },
    "0x0042fdc0": {
        "name": "CPhysicsWeaponModeValueList__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CPhysicsWeaponModeValueList__LoadFromMemBuffer", "void * this", "void * memBuffer"],
        "comment": ["CPhysicsWeaponModeValueList node", "CreateStatementType4", "recursive", "terminator", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "statement-load"],
    },
    "0x0042fea0": {
        "name": "CPhysicsWeaponModeValueList__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CPhysicsWeaponModeValueList__scalar_deleting_dtor", "void * this", "int flags"],
        "comment": ["scalar-delete", "child", "next-node", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "destructor"],
    },
    "0x0042fee0": {
        "name": "CWeaponModeStatement__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CWeaponModeStatement__scalar_deleting_dtor", "void * this", "int flags"],
        "comment": ["scalar-delete", "CWeaponModeStatement__dtor", "OID__FreeObject", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x0042ff00": {
        "name": "CWeaponModeStatement__dtor",
        "signature": ["void", "__fastcall", "CWeaponModeStatement__dtor", "void * this"],
        "comment": ["destructor body", "child pointer at +0x10c", "base vtable", "remain unproven"],
        "tags": COMMON_TAGS + ["destructor"],
    },
    "0x0042ff60": {
        "name": "CRoundStatement__CreateRoundAndRecurse",
        "signature": ["void", "__fastcall", "CRoundStatement__CreateRoundAndRecurse", "void * this"],
        "comment": ["vtable slot +0x4", "creates/registers a round", "child statement", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-update"],
    },
    "0x0042ffa0": {
        "name": "CRoundStatement__Create",
        "signature": ["void", "__cdecl", "CRoundStatement__Create", "char * name"],
        "comment": ["0xa8", "DAT_008553f0", "Stream_Laser", "Gill_M_Breath", "remain unproven"],
        "tags": COMMON_TAGS + ["physics-object-registry"],
    },
    "0x00430190": {
        "name": "CRoundStatement__GetSerializedSize",
        "signature": ["int", "__fastcall", "CRoundStatement__GetSerializedSize", "void * this"],
        "comment": ["missing", "name string", "round value-list", "recursive", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "serialized-size"],
    },
    "0x004301e0": {
        "name": "CPhysicsRoundValueList__GetSerializedSize",
        "signature": ["int", "__fastcall", "CPhysicsRoundValueList__GetSerializedSize", "void * this"],
        "comment": ["CPhysicsRoundValueList", "recursive", "not the top-level CRoundStatement", "remain unproven"],
        "tags": COMMON_TAGS + ["value-list", "serialized-size"],
    },
    "0x00430210": {
        "name": "CRoundStatement__LoadFromMemBuffer",
        "signature": ["void", "__thiscall", "CRoundStatement__LoadFromMemBuffer", "void * this", "void * memBuffer"],
        "comment": ["missing", "CDXMemBuffer", "CreateStatementType5", "skip", "remain unproven"],
        "tags": COMMON_TAGS + ["statement-boundary", "statement-load"],
    },
}

STALE_NAMES = [
    "CUnitAI__ComputeRecursiveNodeSize_Base8",
    "CPhysicsUnitValueList__ctor_like_0042f3d0",
    "CPhysicsUnitValueList__VFunc_00_0042f4b0",
    "CUnitStatement__VFunc_00_0042f4f0",
    "CUnitStatement__ctor_like_0042f510",
    "CPhysicsScriptStatement__ctor_like_0042f570",
    "CWeaponStatement__VFunc_01_0042f5b0",
    "CPhysicsWeaponValueList__ctor_like_0042f8a0",
    "CPhysicsWeaponValueList__VFunc_00_0042f980",
    "CWeaponStatement__VFunc_00_0042f9c0",
    "CWeaponStatement__ctor_like_0042f9e0",
    "CWeaponModeStatement__VFunc_01_0042fa40",
    "CPhysicsWeaponModeValueList__ctor_like_0042fdc0",
    "CPhysicsWeaponModeValueList__VFunc_00_0042fea0",
    "CWeaponModeStatement__VFunc_00_0042fee0",
    "CWeaponModeStatement__ctor_like_0042ff00",
    "CRoundStatement__VFunc_01_0042ff60",
]

EXPECTED_XREFS = (
    ("0x0042ee90", "CUnitStatement__CreateUnitAndRecurse"),
    ("0x0042f280", "CUnitStatement__GetSerializedSize"),
    ("0x0042f3d0", "CUnitStatement__LoadFromMemBuffer"),
    ("0x0042f5f0", "CWeaponStatement__CreateWeaponAndRecurse"),
    ("0x0042f750", "CWeaponStatement__GetSerializedSize"),
    ("0x0042f8a0", "CWeaponStatement__LoadFromMemBuffer"),
    ("0x0042fa80", "CWeaponModeStatement__CreateWeaponModeAndRecurse"),
    ("0x0042fc70", "CWeaponModeStatement__GetSerializedSize"),
    ("0x0042fdc0", "CWeaponModeStatement__LoadFromMemBuffer"),
    ("0x0042ffa0", "CRoundStatement__CreateRoundAndRecurse"),
    ("0x004301e0", "CRoundStatement__GetSerializedSize"),
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "rebuild parity proven",
)

DEFAULT_METADATA_FINAL = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_TAGS = BASE / "tags_final.tsv"
DEFAULT_OUT = BASE / "physics-script-statement-tranche.json"


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "function_entry", "target_raw", "from_function_addr"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def rows_for_address(rows: list[dict[str, str]], address: str, key: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get(key, "")) == wanted]


def decompile_text_for(directory: Path, address: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def build_report(
    *,
    metadata_final_path: Path = DEFAULT_METADATA_FINAL,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    tags_path: Path = DEFAULT_TAGS,
) -> dict[str, object]:
    metadata_final_path = resolve(metadata_final_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    tags_path = resolve(tags_path)

    failures: list[str] = []
    for path, label in (
        (metadata_final_path, "metadata_final"),
        (decompile_index_path, "decompile_index"),
        (xrefs_path, "xrefs"),
        (instructions_path, "instructions"),
        (tags_path, "tags"),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    metadata_rows = read_tsv(metadata_final_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    tag_rows = read_tsv(tags_path)

    metadata_ok = 0
    decompile_ok = 0
    tag_ok = 0
    for address, expected in TARGETS.items():
        row = row_by_address(metadata_rows, address)
        expected_name = str(expected["name"])
        if not row:
            failures.append(f"metadata missing {address}")
        else:
            if row.get("status") != "OK":
                failures.append(f"metadata status not OK for {address}: {row.get('status')}")
            if row.get("name") != expected_name:
                failures.append(f"name mismatch for {address}: {row.get('name')} != {expected_name}")
            for token in expected["signature"]:  # type: ignore[index]
                if not token_present(row.get("signature", ""), str(token)):
                    failures.append(f"signature token missing for {address}: {token}")
            for token in expected["comment"]:  # type: ignore[index]
                if not token_present(row.get("comment", ""), str(token)):
                    failures.append(f"comment token missing for {address}: {token}")
            if row.get("status") == "OK" and row.get("name") == expected_name:
                metadata_ok += 1

        index_row = row_by_address(index_rows, address)
        if not index_row:
            failures.append(f"decompile index missing {address}")
        else:
            if index_row.get("status") != "OK":
                failures.append(f"decompile index status not OK for {address}: {index_row.get('status')}")
            if index_row.get("name") != expected_name:
                failures.append(f"decompile name mismatch for {address}: {index_row.get('name')} != {expected_name}")
            text = decompile_text_for(decompile_dir, address)
            for token in expected["comment"]:  # type: ignore[index]
                if not token_present(text, str(token)):
                    failures.append(f"decompile comment token missing for {address}: {token}")
            for bad in OVERCLAIM_TOKENS:
                if token_present(text, bad):
                    failures.append(f"overclaim token present for {address}: {bad}")
            if index_row.get("status") == "OK" and text:
                decompile_ok += 1

        tag_row = row_by_address(tag_rows, address)
        if not tag_row:
            failures.append(f"tags missing {address}")
        else:
            tags = parse_tags(tag_row.get("tags", ""))
            for tag in expected["tags"]:  # type: ignore[index]
                if str(tag) not in tags:
                    failures.append(f"tag missing for {address}: {tag}")
            if all(str(tag) in tags for tag in expected["tags"]):  # type: ignore[index]
                tag_ok += 1

    observed_names = {row.get("name", "") for row in metadata_rows} | {row.get("name", "") for row in index_rows}
    for stale in STALE_NAMES:
        if stale in observed_names:
            failures.append(f"stale name still present in final target read-back: {stale}")

    for target, caller in EXPECTED_XREFS:
        rows = rows_for_address(xref_rows, target, "target_addr")
        if not any(row.get("from_function") == caller for row in rows):
            failures.append(f"expected xref missing: {target} from {caller}")

    named_instruction_entries = {
        row.get("function_entry")
        for row in instruction_rows
        if row.get("function_name") in {str(target["name"]) for target in TARGETS.values()}
    }
    for address in TARGETS:
        if normalize_address(address) not in named_instruction_entries:
            failures.append(f"instruction read-back missing function entry {address}")

    return {
        "schema": "ghidra-physics-script-statement-tranche-probe.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "targetCount": len(TARGETS),
        "metadataOk": metadata_ok,
        "decompileOk": decompile_ok,
        "tagOk": tag_ok,
        "xrefChecks": len(EXPECTED_XREFS),
        "instructionRows": len(instruction_rows),
        "failures": failures,
        "whatIsProven": [
            "The selected PhysicsScript statement-family entries have saved Ghidra names, signatures, comments, and tags matching the current retail read-back evidence.",
            "The tranche recovers missing function boundaries for statement update, load, and serialized-size bodies that were previously exported as no-function gaps.",
            "Several stale constructor/vfunc/UnitAI/top-level-size names were corrected to destructor, load, value-list, or top-level statement roles.",
        ],
        "notProven": [
            "This does not prove exact source body identity, complete concrete class layouts, local variable names, runtime physics behavior, or rebuild parity.",
            "This does not prove every PhysicsScript subtype or every adjacent statement/value-list helper.",
            "This does not launch or patch BEA.exe.",
        ],
        "privacy": "Public-safe summary only; raw exports stay under ignored subagents/.",
    }


def write_report(report: dict[str, object], path: Path) -> None:
    path = resolve(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata-final", type=Path, default=DEFAULT_METADATA_FINAL)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--tags", type=Path, default=DEFAULT_TAGS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        metadata_final_path=args.metadata_final,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        tags_path=args.tags,
    )
    write_report(report, args.out)
    print("Ghidra PhysicsScript statement tranche probe")
    print(f"status: {report['status']}")
    print(f"targets: {report['targetCount']}")
    print(f"metadata ok: {report['metadataOk']}")
    print(f"decompile ok: {report['decompileOk']}")
    print(f"tags ok: {report['tagOk']}")
    print(f"instruction rows: {report['instructionRows']}")
    if report["failures"]:
        print("failures:")
        for failure in report["failures"]:
            print(f"- {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
