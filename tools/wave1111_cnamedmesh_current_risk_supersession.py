#!/usr/bin/env python3
"""Validate Wave1111 CNamedMesh current-risk supersession evidence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
WAVE1108_DIR = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank"
FOCUSED_TSV = WAVE1108_DIR / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
WAVE458_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave458-mesh-optimization-current"
WAVE944_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave944-building-namedmesh-lifecycle-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1111-cnamedmesh-current-risk-supersession.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1111-cnamedmesh-current-risk-supersession.md"
READINESS = ROOT / "release" / "readiness" / "wave1111_cnamedmesh_current_risk_supersession_2026-06-04.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
BUILDING_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Building.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

ADDRESS = "0x004bc050"
NAME = "CNamedMesh__VFunc02_RemoveFromOccupancyAndForward"
SIGNATURE = "void __fastcall CNamedMesh__VFunc02_RemoveFromOccupancyAndForward(void * this)"
WAVE458_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260516-162849_post_wave458_mesh_optimization_verified"
WAVE944_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-050722_post_wave944_building_namedmesh_lifecycle_review_verified"
LATEST_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified"

DOC_TOKENS = (
    "Wave1111",
    "wave1111-cnamedmesh-current-risk-supersession",
    "25/1179 = 2.12%",
    "1 row",
    "current focused candidates: 1179",
    "Wave458",
    "mesh-optimization-wave458",
    "Wave944",
    "building-namedmesh-lifecycle-review-wave944",
    "0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward",
    "0x00418450 CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh",
    "0x005dd5f0",
    WAVE458_BACKUP,
    WAVE944_BACKUP,
    LATEST_BACKUP,
    "no new Ghidra export",
    "no mutation",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime namedmesh behavior proven",
    "exact layout proven",
    "exact source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def normalize_raw_address(address: str) -> str:
    return normalize_address(address)[2:]


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(key, "")): row for row in read_tsv(path)}


def check_wave1108_membership(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    focused = row_map(FOCUSED_TSV)
    require(len(focused) == 1179, "Wave1108 focused row count mismatch", failures)
    row = focused.get(ADDRESS)
    require(row is not None, f"Wave1108 focused row missing: {ADDRESS}", failures)
    if row is not None:
        require(row.get("name") == NAME, "Wave1108 CNamedMesh name mismatch", failures)
        require(row.get("score") == "31", "Wave1108 CNamedMesh score mismatch", failures)
        for signal in (
            "stale_or_corrected",
            "exact_layout_deferred",
            "source_identity_deferred",
            "runtime_or_rebuild_deferred",
            "generic_name_shape",
        ):
            require(signal in row.get("signals", ""), f"Wave1108 missing signal: {signal}", failures)


def check_current_queue(failures: list[str]) -> None:
    queue = row_map(QUEUE_TSV)
    row = queue.get(ADDRESS)
    require(row is not None, f"current queue row missing: {ADDRESS}", failures)
    if row is not None:
        require(row.get("name") == NAME, "current queue name mismatch", failures)
        require(row.get("signature") == SIGNATURE, "current queue signature mismatch", failures)
        require(row.get("status") == "OK", "current queue status mismatch", failures)
        comment = row.get("comment", "")
        for token in (
            "Wave458",
            "CWorld__RemoveUnitFromOccupancyGrid_Thunk",
            "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh",
            "0x005dd5f0 slot 2",
            "Runtime NamedMesh cleanup behavior",
            "rebuild parity remain unproven",
        ):
            require(token in comment, f"current queue missing comment token: {token}", failures)


def has_xref(path: Path, target: str, from_addr: str, from_function: str, ref_type: str) -> bool:
    for row in read_tsv(path):
        if (
            normalize_address(row.get("target_addr", "")) == normalize_address(target)
            and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
            and row.get("from_function") == from_function
            and row.get("ref_type") == ref_type
        ):
            return True
    return False


def has_vtable_slot(path: Path, vtable: str, slot: str, pointer: str, function_name: str) -> bool:
    for row in read_tsv(path):
        if (
            normalize_raw_address(row.get("vtable", "")) == normalize_raw_address(vtable)
            and row.get("slot_index") == slot
            and normalize_raw_address(row.get("pointer_addr", "")) == normalize_raw_address(pointer)
            and row.get("function_name") == function_name
            and row.get("status") == "OK"
        ):
            return True
    return False


def check_wave458_artifacts(failures: list[str]) -> None:
    metadata = row_map(WAVE458_BASE / "post_metadata.tsv")
    tags = row_map(WAVE458_BASE / "post_tags.tsv")
    row = metadata.get(ADDRESS)
    require(row is not None, "Wave458 metadata row missing", failures)
    if row is not None:
        require(row.get("name") == NAME, "Wave458 metadata name mismatch", failures)
        require(row.get("signature") == SIGNATURE, "Wave458 metadata signature mismatch", failures)
        for token in ("Wave458", "CWorld__RemoveUnitFromOccupancyGrid_Thunk", "0x005dd5f0 slot 2"):
            require(token in row.get("comment", ""), f"Wave458 metadata missing token: {token}", failures)
    tag_row = tags.get(ADDRESS)
    require(tag_row is not None, "Wave458 tag row missing", failures)
    if tag_row is not None:
        for tag in ("static-reaudit", "mesh-optimization-wave458", "named-mesh", "occupancy", "vtable-slot"):
            require(tag in tag_row.get("tags", ""), f"Wave458 tag missing: {tag}", failures)
    require(
        has_xref(WAVE458_BASE / "post_xrefs.tsv", ADDRESS, "0x00418460", "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh", "UNCONDITIONAL_CALL"),
        "Wave458 missing CBuildingNamedMesh xref",
        failures,
    )
    require(
        has_xref(WAVE458_BASE / "post_xrefs.tsv", ADDRESS, "0x005dd5f8", "<no_function>", "DATA"),
        "Wave458 missing vtable DATA xref",
        failures,
    )
    require(
        has_vtable_slot(WAVE458_BASE / "post_vtable_slots.tsv", "0x005dd5f0", "2", ADDRESS, NAME),
        "Wave458 vtable slot 2 mismatch",
        failures,
    )
    expected_logs = {
        "apply_dry.log": "SUMMARY updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0",
        "apply.log": "SUMMARY updated=5 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0",
        "apply_verify_dry.log": "SUMMARY updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0",
        "post_metadata.log": "targets=5 found=5 missing=0",
        "post_tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "post_xrefs.log": "Wrote 10 rows",
        "post_vtable_slots.log": "ExportVtableSlots complete: targets=1 rows=16",
    }
    for relative, token in expected_logs.items():
        text = read_text(WAVE458_BASE / relative)
        require(token in text, f"Wave458 missing log token in {relative}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"Wave458 missing save marker in {relative}", failures)


def check_wave944_artifacts(failures: list[str]) -> None:
    metadata = row_map(WAVE944_BASE / "context-metadata.tsv")
    tags = row_map(WAVE944_BASE / "context-tags.tsv")
    row = metadata.get(ADDRESS)
    require(row is not None, "Wave944 context metadata row missing", failures)
    if row is not None:
        require(row.get("name") == NAME, "Wave944 context name mismatch", failures)
        require(row.get("signature") == SIGNATURE, "Wave944 context signature mismatch", failures)
        require(row.get("status") == "OK", "Wave944 context status mismatch", failures)
    tag_row = tags.get(ADDRESS)
    require(tag_row is not None and tag_row.get("status") == "OK", "Wave944 context tag row mismatch", failures)
    if tag_row is not None:
        for tag in ("static-reaudit", "mesh-optimization-wave458", "named-mesh", "occupancy", "vtable-slot"):
            require(tag in tag_row.get("tags", ""), f"Wave944 tag missing: {tag}", failures)
    require(
        has_xref(WAVE944_BASE / "context-xrefs.tsv", ADDRESS, "0x00418460", "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh", "UNCONDITIONAL_CALL"),
        "Wave944 missing CBuildingNamedMesh xref",
        failures,
    )
    require(
        has_xref(WAVE944_BASE / "context-xrefs.tsv", ADDRESS, "0x005dd5f8", "<no_function>", "DATA"),
        "Wave944 missing vtable DATA xref",
        failures,
    )
    require(
        has_vtable_slot(WAVE944_BASE / "vtable-slots.tsv", "0x005dd5f0", "2", ADDRESS, NAME),
        "Wave944 vtable slot 2 mismatch",
        failures,
    )
    decompile = read_text(WAVE944_BASE / "context-decompile" / "004bc050_CNamedMesh__VFunc02_RemoveFromOccupancyAndForward.c")
    for token in ("CWorld__RemoveUnitFromOccupancyGrid_Thunk", "CComplexThing__Shutdown", "VFuncSlot_02_004f41b0"):
        require(token in decompile, f"Wave944 decompile missing token: {token}", failures)
    backup = read_json(WAVE944_BASE / "backup-summary.json")
    require(backup.get("backupPath") == WAVE944_BACKUP, "Wave944 backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "Wave944 backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173280135, "Wave944 backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "Wave944 backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = {
        "wave1111 note": read_text(NOTE),
        "wave1111 readiness": read_text(READINESS),
        "mapped systems": read_text(MAPPED_SYSTEMS),
        "campaign": read_text(CAMPAIGN),
        "binary index": read_text(BINARY_INDEX),
        "RE index": read_text(RE_INDEX),
        "progress": read_text(PROGRESS),
        "Building index": read_text(BUILDING_INDEX),
        "developer state": read_text(DEVELOPER_STATE),
        "documentation state": read_text(DOCUMENTATION_STATE),
        "re state": read_text(RE_STATE),
    }
    for name, text in docs.items():
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {name}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {name}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave1111 note mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "static progress mirror mismatch", failures)
    current = read_json(PROGRESS).get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 25, "progress focusedReviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "2.12%", "progress focusedReviewedPercent mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1111-cnamedmesh-current-risk-supersession")
        == r"py -3 tools\wave1111_cnamedmesh_current_risk_supersession.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_membership(failures)
    check_current_queue(failures)
    check_wave458_artifacts(failures)
    check_wave944_artifacts(failures)
    check_docs(failures)

    if failures:
        print("Wave1111 CNamedMesh current-risk supersession probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1111 CNamedMesh current-risk supersession probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
