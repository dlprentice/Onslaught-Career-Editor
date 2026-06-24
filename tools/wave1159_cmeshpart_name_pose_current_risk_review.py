#!/usr/bin/env python3
"""Validate Wave1159 CMeshPart name/load/pose current-risk review evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1159-cmeshpart-name-pose-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1159-cmeshpart-name-pose-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1159-cmeshpart-name-pose-current-risk-review.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
READINESS = ROOT / "release" / "readiness" / "wave1159_cmeshpart_name_pose_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260606-004711_post_wave1159_cmeshpart_name_pose_current_risk_review_verified"
EXPECTED_SOURCE_ROOT = str(Path.home() / "Ghidra" / "Projects")

TARGETS = {
    "0x004950f0": ("CMeshPart__AnySubPartNameStartsWithCore", "bool __cdecl CMeshPart__AnySubPartNameStartsWithCore(void * partContainer)"),
    "0x004957d0": ("CMeshPart__AnySubPartNameIsTurretOrStartsWithBarrel", "bool __cdecl CMeshPart__AnySubPartNameIsTurretOrStartsWithBarrel(void * partContainer)"),
    "0x00496250": ("CMeshPart__NameDoesNotStartWithDoor", "bool __cdecl CMeshPart__NameDoesNotStartWithDoor(void * meshPart)"),
    "0x00496270": ("CMeshPart__HasDoorOpeningOrClosingAnimation", "bool __cdecl CMeshPart__HasDoorOpeningOrClosingAnimation(void * animationSet)"),
    "0x004aa8a0": ("CMesh__FindPartByNameI", "void * __thiscall CMesh__FindPartByNameI(void * this, char * part_name)"),
    "0x004aede0": ("CMeshPart__LoadOldStyle_VersionA", "int __thiscall CMeshPart__LoadOldStyle_VersionA(void * this, void * mem_buffer, void * parent_mesh, void * mesh_resource_records, int material_index_limit, int legacy_flags_or_zero)"),
    "0x004af110": ("CMeshPart__LoadOldStyle_VersionB_WithExtraBlock", "int __thiscall CMeshPart__LoadOldStyle_VersionB_WithExtraBlock(void * this, void * mem_buffer, void * parent_mesh, void * mesh_resource_records, int material_index_limit, int legacy_flags_or_zero)"),
    "0x004b0800": ("CMeshPart__ApplyRootTransformRecursive", "void __thiscall CMeshPart__ApplyRootTransformRecursive(void * this, int parent_transform_dword00, int parent_transform_dword01, int parent_transform_dword02, int parent_transform_dword03, int parent_transform_dword04, int parent_transform_dword05, int parent_transform_dword06, int parent_transform_dword07, int parent_transform_dword08, int parent_transform_dword09, int parent_transform_dword10, int parent_transform_dword11, float origin_x, float origin_y, float origin_z, float origin_w, void * frame_override_part)"),
    "0x004b1eb0": ("CMeshPart__RebuildPerVertexNormalsAndTangents", "void __thiscall CMeshPart__RebuildPerVertexNormalsAndTangents(void * this, int update_primary_normal)"),
    "0x004b4ba0": ("CMeshPart__PopulatePoseCacheRecursive", "int __thiscall CMeshPart__PopulatePoseCacheRecursive(void * this, float anchor_x, float anchor_y, float anchor_z, float anchor_w, int transform_dword00, int transform_dword01, int transform_dword02, int transform_dword03, int transform_dword04, int transform_dword05, int transform_dword06, int transform_dword07, int transform_dword08, int transform_dword09, int transform_dword10, int transform_dword11, void * mesh_part, int frame_arg0, int frame_arg1, int cache_value)"),
    "0x004b4cd0": ("CMeshPart__RefreshCachedPoseIfStale", "int __thiscall CMeshPart__RefreshCachedPoseIfStale(void * this, void * mesh_context, void * pose_controller, int unused_stack_arg2, int force_refresh)"),
    "0x004b4de0": ("CMeshPart__EvaluatePoseTransformForFrame", "int __cdecl CMeshPart__EvaluatePoseTransformForFrame(void * animation_context, void * pose_controller, void * mesh_part, float * out_anchor_vec4, float * out_transform_3x4, int skip_controller_transform, int unused_stack_arg6)"),
}

EXPECTED_CALL_XREFS = {
    "0x004950f0": {"0x004bae9e", "0x004bb06e"},
    "0x004957d0": {"0x004baec0", "0x004baee2", "0x004baf6a", "0x004bb090", "0x004bb0b2", "0x004bb13a"},
    "0x00496250": {"0x004baf11"},
    "0x00496270": {"0x004baf04", "0x004bb0d4"},
    "0x004aa8a0": {"0x0044446e", "0x004444ce", "0x0044453e", "0x004445ce", "0x0049f914", "0x004a0161"},
    "0x004aede0": {"0x004a8f05"},
    "0x004af110": {"0x004a8f49"},
    "0x004b0800": {"0x004a9503", "0x004b0854"},
    "0x004b1eb0": {"0x004af101", "0x004af456", "0x004afb96", "0x004b07e1"},
    "0x004b4ba0": {"0x004b4dbc", "0x004b4ca1"},
    "0x004b4cd0": {"0x004b6296", "0x004b4e81"},
    "0x004b4de0": {"0x00445130", "0x004ad70a", "0x004dd1cf", "0x004dede9"},
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence"}

DOCS = [
    NOTE,
    NOTE_MIRROR,
    CONTRACT,
    CONTRACT_MIRROR,
    READINESS,
    PROGRESS,
    PROGRESS_MIRROR,
    ROOT / "README.md",
    ROOT / "CURRENT_CAPABILITIES.md",
    ROOT / "AGENTS.md",
    ROOT / "reverse-engineering" / "RE-INDEX.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshPart.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mesh.cpp" / "_index.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

DOC_TOKENS = (
    "Wave1159",
    "wave1159-cmeshpart-name-pose-current-risk-review",
    "497/1179 = 42.15%",
    "12 CMeshPart name/load/pose current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 682",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consults used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "33 xref rows",
    "1790 instruction rows",
    "CMeshPart__LoadOldStyle_VersionA",
    "CMeshPart__RebuildPerVertexNormalsAndTangents",
    "CMeshPart__PopulatePoseCacheRecursive",
    "CMeshPart__EvaluatePoseTransformForFrame",
    "CMesh__FindPartByNameI",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime mesh behavior proven",
    "runtime pose-cache behavior proven",
    "visible render output proven",
    "rebuild parity proven",
    "exact layout proven",
    "source identity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 12,
        "pre-tags.tsv": 12,
        "pre-xrefs.tsv": 33,
        "pre-instructions.tsv": 1790,
        "pre-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    xrefs_by_target: dict[str, list[dict[str, str]]] = {}
    for row in xrefs:
        xrefs_by_target.setdefault(normalize_address(row.get("target_addr", "")), []).append(row)

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in ("Static retail", "runtime", "rebuild parity"):
                require(token in comment, f"missing comment boundary token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        actual_calls = {normalize_address(xref.get("from_addr", "")) for xref in xrefs_by_target.get(address, []) if xref.get("ref_type") == "UNCONDITIONAL_CALL"}
        require(EXPECTED_CALL_XREFS[address].issubset(actual_calls), f"call xrefs missing at {address}", failures)

    actual_ref_types = {row.get("ref_type") for row in xrefs}
    require(actual_ref_types == {"UNCONDITIONAL_CALL"}, f"unexpected xref types: {actual_ref_types}", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=12 found=12 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "pre-xrefs.log": "Wrote 33 rows",
        "pre-instructions.log": "Wrote 1790 function-body instruction rows",
        "pre-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("sourceRoot") == EXPECTED_SOURCE_ROOT, "backup source root mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6411, "quality TSV row count mismatch", failures)
    require(commented == 6411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6411, "strict clean-signature count mismatch", failures)
    require(read_json(RISK_JSON).get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(read_json(FOCUSED_JSON).get("candidateFunctions") == 1178, "focused candidate mismatch", failures)


def check_docs_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(latest.get("wave") == "Wave1159 CMeshPart name/pose current-risk review", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1159-cmeshpart-name-pose-current-risk-review", "latest tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest backup mismatch", failures)
    require(current.get("focusedReviewed") == 497, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "42.15%", "progress focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 682, "progress remaining mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, "progress live focused mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1159 CMeshPart name/pose current-risk review", "progress latest review mismatch", failures)

    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1159 note mirror mismatch", failures)
    require(read_text(CONTRACT) == read_text(CONTRACT_MIRROR), "mesh contract mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    require(
        read_json(PACKAGE_JSON).get("scripts", {}).get("test:wave1159-cmeshpart-name-pose-current-risk-review")
        == r"py -3 tools\wave1159_cmeshpart_name_pose_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_queue(failures)
    check_docs_progress(failures)
    if failures:
        print("Wave1159 CMeshPart name/pose current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1159 CMeshPart name/pose current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
