#!/usr/bin/env python3
"""Validate Wave940 line/cylinder dispatch read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave940-line-cylinder-dispatch-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_line_cylinder_dispatch_review_wave940_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
CYLINDER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "cylinder.cpp" / "_index.md"
MCV_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshCollisionVolume.cpp" / "_index.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mesh.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"G:\GhidraBackups\BEA_20260528-030741_post_wave940_line_cylinder_dispatch_review_verified"
SCRIPT_NAME = "test:ghidra-line-cylinder-dispatch-review-wave940"
SCRIPT_VALUE = r"py -3 tools\ghidra_line_cylinder_dispatch_review_wave940_probe.py --check"

TARGETS = {
    "0x004014c0": (
        "SharedVFunc__NoOpOneArg_004014c0",
        "void __thiscall SharedVFunc__NoOpOneArg_004014c0(void * this, int arg0)",
    ),
    "0x00405930": (
        "SharedVFunc__ReturnZero_00405930",
        "int __thiscall SharedVFunc__ReturnZero_00405930(void * this)",
    ),
    "0x00405940": (
        "SharedVFunc__ReturnZeroRet4_00405940",
        "int __thiscall SharedVFunc__ReturnZeroRet4_00405940(void * this, void * arg0)",
    ),
    "0x004059a0": (
        "CCylinder__VFunc_01_004059a0",
        "int __thiscall CCylinder__VFunc_01_004059a0(void * this, void * forwardedA, void * forwardedB, void * dispatchObject, void * forwardedC)",
    ),
    "0x004098c0": (
        "CLine__VFunc_01_004098c0",
        "int __thiscall CLine__VFunc_01_004098c0(void * this, void * arg0, void * arg1, void * dispatch_target, void * arg3)",
    ),
    "0x004098e0": (
        "CLine__ctor_copy",
        "void __thiscall CLine__ctor_copy(void * this, void * sourceLine)",
    ),
    "0x00426340": (
        "CLine__ScalarDeletingDestructor_00426340",
        "void * __thiscall CLine__ScalarDeletingDestructor_00426340(void * this, int deleteFlags)",
    ),
    "0x00426360": (
        "CLine__SetBaseVtable_00426360",
        "void __fastcall CLine__SetBaseVtable_00426360(void * this)",
    ),
}

CONTEXT = {
    "0x0040d470": "CLine__ctor_fromEndpoints",
    "0x004014a0": "SharedVFunc__Return1_004014a0",
    "0x004059c0": "SharedVFunc__Return2_004059c0",
    "0x00426320": "CSphere__VFunc_01_00426320",
    "0x0043fde0": "CCylinder__ctor",
    "0x0043fe20": "CCylinder__ResolveCollisionVFunc02",
    "0x00452da0": "SharedVFunc__NoOp_Ret08",
    "0x00453ac0": "SharedVFunc__NoOp_Ret0C",
    "0x00478510": "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
    "0x00479020": "CMeshCollisionVolume__IsDirectionInsideTrianglePrism",
    "0x004acde0": "CMeshCollisionVolume__InitContactOutputRecord",
    "0x004ad830": "CMeshCollisionVolume__VFunc_04_004ad830",
    "0x004e4d70": "CSphere__VFunc02_ResolveCollisionAsCylinder",
}

COMMENT_TOKENS = {
    "0x004059a0": ("ret 0x10", "dispatchObject vfunc +0x8"),
    "0x004098c0": ("vtable-slot wrapper", "dispatch_target vfunc", "+0x10"),
    "0x004098e0": ("CGeneralVolume", "CLine RTTI"),
    "0x00426340": ("scalar-deleting destructor", "delete flag"),
    "0x00426360": ("vtable reset", "unwind thunks"),
}

EXPECTED_XREFS = {
    ("xrefs.tsv", "0x004059a0", "0x005d88d0", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x004059a0", "0x005d88d8", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x004059a0", "0x005d88e0", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x004098c0", "0x005d8c00", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x004098c0", "0x005d8c04", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x004098c0", "0x005d8c08", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x004098c0", "0x005d8c10", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x00426340", "0x005d88cc", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x00426340", "0x005d8bfc", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x00426340", "0x005d95e8", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x00426360", "0x00426343", "CLine__ScalarDeletingDestructor_00426340", "UNCONDITIONAL_CALL"),
    ("xrefs.tsv", "0x00426360", "0x005d3943", "Unwind@005d3940", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x00426320", "0x005d95ec", "<no_function>", "DATA"),
    ("context-xrefs.tsv", "0x00426320", "0x005d95fc", "<no_function>", "DATA"),
    ("context-xrefs.tsv", "0x0043fe20", "0x004e4de0", "CSphere__VFunc02_ResolveCollisionAsCylinder", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x0043fe20", "0x005d88d4", "<no_function>", "DATA"),
    ("context-xrefs.tsv", "0x004e4d70", "0x005d95f0", "<no_function>", "DATA"),
    ("context-xrefs.tsv", "0x00478510", "0x004ac454", "CMeshCollisionVolume__TestSweptSphereAgainstBounds", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x00479020", "0x004788e2", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x004acde0", "0x004acd22", "CMeshCollisionVolume__VFunc_03_004ac6e0", "CONDITIONAL_JUMP"),
    ("context-xrefs.tsv", "0x004ad830", "0x005d95d8", "<no_function>", "DATA"),
}

EXPECTED_INSTRUCTIONS = {
    ("instructions.tsv", "0x004059b9", "CALL", "[EDX + 0x8]", "CCylinder__VFunc_01_004059a0"),
    ("instructions.tsv", "0x004059bd", "RET", "0x10", "CCylinder__VFunc_01_004059a0"),
    ("instructions.tsv", "0x004098d9", "CALL", "[EDX + 0x10]", "CLine__VFunc_01_004098c0"),
    ("instructions.tsv", "0x004098dd", "RET", "0x10", "CLine__VFunc_01_004098c0"),
    ("instructions.tsv", "0x00409902", "MOV", "0x5d892c", "CLine__ctor_copy"),
    ("instructions.tsv", "0x00409942", "MOV", "0x5d8bfc", "CLine__ctor_copy"),
    ("instructions.tsv", "0x00426343", "CALL", "0x00426360", "CLine__ScalarDeletingDestructor_00426340"),
    ("instructions.tsv", "0x00426355", "CALL", "0x00549220", "CLine__ScalarDeletingDestructor_00426340"),
    ("instructions.tsv", "0x00426360", "MOV", "0x5d892c", "CLine__SetBaseVtable_00426360"),
    ("context-instructions.tsv", "0x0040d482", "MOV", "0x5d892c", "CLine__ctor_fromEndpoints"),
    ("context-instructions.tsv", "0x0040d4bd", "MOV", "0x5d8bfc", "CLine__ctor_fromEndpoints"),
    ("context-instructions.tsv", "0x0043fdf1", "MOV", "0x5d88cc", "CCylinder__ctor"),
    ("context-instructions.tsv", "0x004e4de0", "CALL", "0x0043fe20", "CSphere__VFunc02_ResolveCollisionAsCylinder"),
}

EXPECTED_VTABLE_SLOTS = {
    ("005d88cc", "0", "00426340", "CLine__ScalarDeletingDestructor_00426340"),
    ("005d88cc", "1", "004059a0", "CCylinder__VFunc_01_004059a0"),
    ("005d88cc", "2", "0043fe20", "CCylinder__ResolveCollisionVFunc02"),
    ("005d88cc", "3", "004059a0", "CCylinder__VFunc_01_004059a0"),
    ("005d88cc", "5", "004059a0", "CCylinder__VFunc_01_004059a0"),
    ("005d88cc", "6", "004059c0", "SharedVFunc__Return2_004059c0"),
    ("005d8bfc", "0", "00426340", "CLine__ScalarDeletingDestructor_00426340"),
    ("005d8bfc", "1", "004098c0", "CLine__VFunc_01_004098c0"),
    ("005d8bfc", "2", "004098c0", "CLine__VFunc_01_004098c0"),
    ("005d8bfc", "3", "004098c0", "CLine__VFunc_01_004098c0"),
    ("005d8bfc", "5", "004098c0", "CLine__VFunc_01_004098c0"),
    ("005d8bfc", "6", "004014a0", "SharedVFunc__Return1_004014a0"),
    ("005d95e8", "0", "00426340", "CLine__ScalarDeletingDestructor_00426340"),
    ("005d95e8", "1", "00426320", "CSphere__VFunc_01_00426320"),
    ("005d95e8", "2", "004e4d70", "CSphere__VFunc02_ResolveCollisionAsCylinder"),
    ("005d95e8", "5", "00426320", "CSphere__VFunc_01_00426320"),
    ("005d95e8", "6", "00405930", "SharedVFunc__ReturnZero_00405930"),
}

DECOMPILE_TOKENS = {
    "decompile/004059a0_CCylinder__VFunc_01_004059a0.c": ("dispatchObject + 8", "forwardedB,forwardedA,this,forwardedC"),
    "decompile/004098c0_CLine__VFunc_01_004098c0.c": ("dispatch_target + 0x10", "arg1,arg0,this,arg3"),
    "decompile/004098e0_CLine__ctor_copy.c": ("PTR_LAB_005d892c", "PTR_CLine__ScalarDeletingDestructor_00426340_005d8bfc"),
    "decompile/00426340_CLine__ScalarDeletingDestructor_00426340.c": ("CLine__SetBaseVtable_00426360", "deleteFlags"),
    "decompile/00426360_CLine__SetBaseVtable_00426360.c": ("PTR_LAB_005d892c",),
    "context-decompile/004e4d70_CSphere__VFunc02_ResolveCollisionAsCylinder.c": ("CCylinder__ResolveCollisionVFunc02", "PTR_CLine__ScalarDeletingDestructor_00426340_005d88cc"),
}

CORE_TOKENS = (
    "Wave940",
    "line-cylinder-dispatch-review-wave940",
    "178/1408 = 12.64%",
    "6113/6113 = 100.00%",
    BACKUP,
    "read-only review",
    "0x004059a0 CCylinder__VFunc_01_004059a0",
    "0x004098c0 CLine__VFunc_01_004098c0",
    "0x004098e0 CLine__ctor_copy",
    "0x00426340 CLine__ScalarDeletingDestructor_00426340",
    "0x00426360 CLine__SetBaseVtable_00426360",
    "0x00426320 CSphere__VFunc_01_00426320",
    "0x005d88cc",
    "0x005d8bfc",
    "0x005d95e8",
)

OVERCLAIMS = (
    "runtime collision behavior proven",
    "runtime primitive dispatch behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = (value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def normalize_raw_address(value: str) -> str:
    return normalize_address(value)[2:]


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row[key]): row for row in read_tsv(path)}


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def has_xref(expected: tuple[str, str, str, str, str]) -> bool:
    rel, target, from_addr, from_function, ref_type = expected
    for row in read_tsv(BASE / rel):
        if (
            normalize_address(row.get("target_addr", "")) == normalize_address(target)
            and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
            and row.get("from_function") == from_function
            and row.get("ref_type") == ref_type
        ):
            return True
    return False


def has_instruction(expected: tuple[str, str, str, str, str]) -> bool:
    rel, address, mnemonic, operand_token, function_name = expected
    for row in read_tsv(BASE / rel):
        if (
            normalize_address(row.get("instruction_addr", "")) == normalize_address(address)
            and row.get("mnemonic") == mnemonic
            and operand_token in row.get("operands", "")
            and row.get("function_name") == function_name
        ):
            return True
    return False


def has_vtable_slot(expected: tuple[str, str, str, str]) -> bool:
    vtable, slot, pointer, function_name = expected
    for row in read_tsv(BASE / "vtable-slots.tsv"):
        if (
            normalize_raw_address(row.get("vtable", "")) == normalize_raw_address(vtable)
            and row.get("slot_index") == slot
            and normalize_raw_address(row.get("pointer_addr", "")) == normalize_raw_address(pointer)
            and row.get("function_name") == function_name
            and row.get("status") == "OK"
        ):
            return True
    return False


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 1462,
        "instructions.tsv": 85,
        "decompile/index.tsv": 8,
        "context-metadata.tsv": 13,
        "context-tags.tsv": 13,
        "context-xrefs.tsv": 528,
        "context-instructions.tsv": 1830,
        "context-decompile/index.tsv": 13,
        "vtable-slots.tsv": 24,
    }
    for rel, count in expected_counts.items():
        require(len(read_tsv(BASE / rel)) == count, f"{rel} row count mismatch", failures)

    metadata = row_map(BASE / "metadata.tsv")
    decomp = row_map(BASE / "decompile" / "index.tsv")
    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in COMMENT_TOKENS.get(address, ()):
                require(token in comment, f"missing comment token {address}: {token}", failures)
        dec = decomp.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch {address}", failures)

    context_meta = row_map(BASE / "context-metadata.tsv")
    for address, name in CONTEXT.items():
        row = context_meta.get(address)
        require(row is not None and row.get("name") == name and row.get("status") == "OK", f"context metadata mismatch {address}", failures)

    for expected in EXPECTED_XREFS:
        require(has_xref(expected), f"missing xref {expected}", failures)
    for expected in EXPECTED_INSTRUCTIONS:
        require(has_instruction(expected), f"missing instruction {expected}", failures)
    for expected in EXPECTED_VTABLE_SLOTS:
        require(has_vtable_slot(expected), f"missing vtable slot {expected}", failures)
    for rel, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / rel)
        for token in tokens:
            require(token in text, f"missing decompile token {rel}: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_logs = {
        "metadata.log": "targets=8 found=8 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "xrefs.log": "Wrote 1462 rows",
        "instructions.log": "Wrote 85 function-body instruction rows",
        "decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "context-metadata.log": "targets=13 found=13 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "context-xrefs.log": "Wrote 528 rows",
        "context-instructions.log": "Wrote 1830 function-body instruction rows",
        "context-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=3 rows=24",
    }
    for rel, token in expected_logs.items():
        text = read_text(BASE / rel)
        require(token in text, f"missing log token {rel}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIGNATURE:", "FAIL:", "failed=1", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected log failure {rel}: {bad}", failures)

    for mutation_log in ("apply-dry.log", "apply.log", "apply-final-dry.log"):
        require(not (BASE / mutation_log).exists(), f"unexpected mutation log present: {mutation_log}", failures)

    backup = json.loads(read_text(BASE / "backup-summary.json"))
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = json.loads(read_text(PACKAGE_JSON))
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)

    for path in [NOTE, CAMPAIGN, CYLINDER_DOC, MCV_DOC, MESH_DOC, *STATE_FILES]:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave940 line/cylinder dispatch review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave940 line/cylinder dispatch review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
