#!/usr/bin/env python3
"""Validate Wave944 Building/CBuildingNamedMesh lifecycle read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave944-building-namedmesh-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_building_namedmesh_lifecycle_review_wave944_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
BUILDING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Building.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"G:\GhidraBackups\BEA_20260528-050722_post_wave944_building_namedmesh_lifecycle_review_verified"
SCRIPT_NAME = "test:ghidra-building-namedmesh-lifecycle-review-wave944"
SCRIPT_VALUE = r"py -3 tools\ghidra_building_namedmesh_lifecycle_review_wave944_probe.py --check"

TARGETS = {
    "0x004176c0": (
        "CThing__InitRenderThingFromInitMeshName",
        "void __thiscall CThing__InitRenderThingFromInitMeshName(void * this, void * init)",
        ("ret 0x4", "%s.msh", "PCRTID__CreateObject", "this+0x30"),
    ),
    "0x00417870": (
        "CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward",
        "void __fastcall CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward(void * this)",
        ("CBuilding and CSimpleBuilding vtables", "world occupancy grid", "0x004f95d0"),
    ),
    "0x004178a0": (
        "CBuilding__ProcessClosingAndUnshuttingAnimations",
        "void __fastcall CBuilding__ProcessClosingAndUnshuttingAnimations(void * this)",
        ("closing/unshutting animation", "+0x254", "+0x264", "+0x268"),
    ),
    "0x00418120": (
        "CBuilding__AdvanceOpenCloseAnimationState",
        "int __fastcall CBuilding__AdvanceOpenCloseAnimationState(void * this)",
        ("open/close/shut animation-state", "vfunc +0x58", "vfunc +0xf0", "+0x254"),
    ),
    "0x004183d0": (
        "CBuildingNamedMesh__dtor_base",
        "void __fastcall CBuildingNamedMesh__dtor_base(void * this)",
        ("0x005d910c", "CActor__dtor_base"),
    ),
    "0x00418450": (
        "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh",
        "void __fastcall CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh(void * this)",
        ("0x005d9114", "CNamedMesh slot 2"),
    ),
}

CONTEXT = {
    "0x00417590": "CBuilding__dtor_body_00417590",
    "0x004176a0": "CBuilding__scalar_deleting_dtor",
    "0x00418430": "CBuildingNamedMesh__scalar_deleting_dtor",
    "0x004bbcd0": "CNamedMesh__VFunc_09_004bbcd0",
    "0x004bc050": "CNamedMesh__VFunc02_RemoveFromOccupancyAndForward",
    "0x004f95d0": "CUnit__VFunc02_CleanupWorldLinksAndForward",
}

EXPECTED_XREFS = {
    ("primary-xrefs.tsv", "0x004176c0", "0x005d8f3c", "<no_function>", "DATA"),
    ("primary-xrefs.tsv", "0x00417870", "0x005d8ebc", "<no_function>", "DATA"),
    ("primary-xrefs.tsv", "0x00417870", "0x005dfd44", "<no_function>", "DATA"),
    ("primary-xrefs.tsv", "0x004178a0", "0x005d8fbc", "<no_function>", "DATA"),
    ("primary-xrefs.tsv", "0x00418120", "0x005d8fa0", "<no_function>", "DATA"),
    ("primary-xrefs.tsv", "0x004183d0", "0x00418433", "CBuildingNamedMesh__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("primary-xrefs.tsv", "0x00418450", "0x005d9114", "<no_function>", "DATA"),
    ("context-xrefs.tsv", "0x00417590", "0x004176a3", "CBuilding__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x004176a0", "0x005d8eb8", "<no_function>", "DATA"),
    ("context-xrefs.tsv", "0x00418430", "0x005d9110", "<no_function>", "DATA"),
    ("context-xrefs.tsv", "0x004bc050", "0x00418460", "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x004bc050", "0x005dd5f8", "<no_function>", "DATA"),
    ("context-xrefs.tsv", "0x004f95d0", "0x0041788d", "CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward", "UNCONDITIONAL_CALL"),
}

EXPECTED_VTABLE_SLOTS = {
    ("005d8eb4", "1", "004176a0", "CBuilding__scalar_deleting_dtor"),
    ("005d8eb4", "2", "00417870", "CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward"),
    ("005d8eb4", "34", "004176c0", "CThing__InitRenderThingFromInitMeshName"),
    ("005dfd3c", "2", "00417870", "CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward"),
    ("005d910c", "1", "00418430", "CBuildingNamedMesh__scalar_deleting_dtor"),
    ("005d910c", "2", "00418450", "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh"),
    ("005dd5f0", "2", "004bc050", "CNamedMesh__VFunc02_RemoveFromOccupancyAndForward"),
    ("005dd5f0", "9", "004bbcd0", "CNamedMesh__VFunc_09_004bbcd0"),
}

DECOMPILE_TOKENS = {
    "primary-decompile/004176c0_CThing__InitRenderThingFromInitMeshName.c": ("PCRTID__CreateObject", "%s.msh"),
    "primary-decompile/00417870_CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward.c": (
        "CWorld__RemoveUnitFromOccupancyGrid_Thunk",
        "CUnit__VFunc02_CleanupWorldLinksAndForward",
    ),
    "primary-decompile/004178a0_CBuilding__ProcessClosingAndUnshuttingAnimations.c": ("0x254", "0x264", "0x268"),
    "primary-decompile/00418120_CBuilding__AdvanceOpenCloseAnimationState.c": ("0x254", "0x264"),
    "primary-decompile/004183d0_CBuildingNamedMesh__dtor_base.c": ("CActor__dtor_base",),
    "primary-decompile/00418450_CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh.c": (
        "CWorld__RemoveUnitFromOccupancyGrid_Thunk",
        "CNamedMesh__VFunc02_RemoveFromOccupancyAndForward",
    ),
    "context-decompile/00418430_CBuildingNamedMesh__scalar_deleting_dtor.c": ("CBuildingNamedMesh__dtor_base", "flags & 1"),
    "context-decompile/004bc050_CNamedMesh__VFunc02_RemoveFromOccupancyAndForward.c": (
        "CWorld__RemoveUnitFromOccupancyGrid_Thunk",
        "VFuncSlot_02_004f41b0",
    ),
}

CORE_TOKENS = (
    "Wave944",
    "building-namedmesh-lifecycle-review-wave944",
    "read-only review",
    "192/1408 = 13.64%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x004176c0 CThing__InitRenderThingFromInitMeshName",
    "0x00417870 CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward",
    "0x004178a0 CBuilding__ProcessClosingAndUnshuttingAnimations",
    "0x00418120 CBuilding__AdvanceOpenCloseAnimationState",
    "0x004183d0 CBuildingNamedMesh__dtor_base",
    "0x00418430 CBuildingNamedMesh__scalar_deleting_dtor",
    "0x00418450 CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh",
    "0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward",
    "0x005d8eb4",
    "0x005dfd3c",
    "0x005d910c",
    "0x005dd5f0",
)

OVERCLAIMS = (
    "runtime building animation behavior proven",
    "runtime namedmesh behavior proven",
    "exact cbuilding layout proven",
    "exact source virtual names proven",
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


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


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
        "primary-metadata.tsv": 6,
        "primary-tags.tsv": 6,
        "primary-xrefs.tsv": 7,
        "primary-instructions.tsv": 351,
        "primary-decompile/index.tsv": 6,
        "context-metadata.tsv": 6,
        "context-tags.tsv": 6,
        "context-xrefs.tsv": 28,
        "context-instructions.tsv": 288,
        "context-decompile/index.tsv": 6,
        "vtable-slots.tsv": 192,
    }
    for rel, count in expected_counts.items():
        require(len(read_tsv(BASE / rel)) == count, f"{rel} row count mismatch", failures)

    metadata = row_map(BASE / "primary-metadata.tsv")
    decomp = row_map(BASE / "primary-decompile" / "index.tsv")
    tags = row_map(BASE / "primary-tags.tsv")
    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token {address}: {token}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
        dec = decomp.get(address)
        require(
            dec is not None and dec.get("signature") == signature and dec.get("status") == "OK",
            f"decompile mismatch {address}",
            failures,
        )

    context_meta = row_map(BASE / "context-metadata.tsv")
    for address, name in CONTEXT.items():
        row = context_meta.get(address)
        require(row is not None and row.get("name") == name and row.get("status") == "OK", f"context metadata mismatch {address}", failures)

    for expected in EXPECTED_XREFS:
        require(has_xref(expected), f"missing xref {expected}", failures)
    for expected in EXPECTED_VTABLE_SLOTS:
        require(has_vtable_slot(expected), f"missing vtable slot {expected}", failures)
    for rel, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / rel)
        for token in tokens:
            require(token in text, f"missing decompile token {rel}: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_logs = {
        "primary-metadata.log": "targets=6 found=6 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "primary-xrefs.log": "Wrote 7 rows",
        "primary-instructions.log": "Wrote 351 function-body instruction rows",
        "primary-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "context-metadata.log": "targets=6 found=6 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "context-xrefs.log": "Wrote 28 rows",
        "context-instructions.log": "Wrote 288 function-body instruction rows",
        "context-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=4 rows=192",
    }
    for rel, token in expected_logs.items():
        text = read_text(BASE / rel)
        require(token in text, f"missing log token {rel}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save marker {rel}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "failed=1", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected log failure {rel}: {bad}", failures)

    for mutation_log in ("apply-dry.log", "apply.log", "apply-final-dry.log"):
        require(not (BASE / mutation_log).exists(), f"unexpected mutation log present: {mutation_log}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173280135, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)

    docs = [NOTE, CAMPAIGN, GHIDRA_REFERENCE, BUILDING_DOC, *STATE_FILES]
    for path in docs:
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
        print("Wave944 Building/CBuildingNamedMesh lifecycle review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave944 Building/CBuildingNamedMesh lifecycle review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
