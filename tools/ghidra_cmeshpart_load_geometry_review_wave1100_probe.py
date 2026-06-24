#!/usr/bin/env python3
"""Validate Wave1100 CMeshPart load/geometry read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1100-cmeshpart-load-geometry-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cmeshpart_load_geometry_review_wave1100_2026-06-04.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1100_recheck_2026-06-04.md"
PACKAGE_JSON = ROOT / "package.json"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
MESHPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshPart.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
README = ROOT / "README.MD"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
AGENTS = ROOT / "AGENTS.md"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified"
WAVE_TAG = "cmeshpart-load-geometry-review-wave1100"

TARGETS = {
    "0x004a51f0": (
        "CMeshPart__FreeResources",
        "void __thiscall CMeshPart__FreeResources(void * this)",
        ("Wave443", "0x004ae640", "free-owned-resource"),
    ),
    "0x004aa3f0": (
        "CMeshPart__CopyPrimaryAxesToOutVec3Triplet",
        "void __thiscall CMeshPart__CopyPrimaryAxesToOutVec3Triplet(void * this, void * out_vec3)",
        ("Wave444", "primary CMeshPart axis", "RET 0x4"),
    ),
    "0x004adff0": (
        "CMeshPart__SetVertexCount",
        "void __thiscall CMeshPart__SetVertexCount(void * this, int vertex_count)",
        ("Wave447", "vertex channel", "count*0x14"),
    ),
    "0x004ae110": (
        "CMeshPart__StartTriangleBucketSearch",
        "int __thiscall CMeshPart__StartTriangleBucketSearch(void * this, int search_key0, int search_key1, void * out_triangle_vertices, void * query_context)",
        ("Wave447", "CPolyBucket__StartSearch", "+0x100"),
    ),
    "0x004ae1a0": (
        "CMeshPart__GetNextTriangleFromBucketSearch",
        "int __thiscall CMeshPart__GetNextTriangleFromBucketSearch(void * this, void * out_triangle_vertices, void * query_context)",
        ("Wave447", "CPolyBucket__GetNextTriangle", "output triplet"),
    ),
    "0x004ae220": (
        "CMeshPart__StartLineTriangleBucketSearch",
        "int __thiscall CMeshPart__StartLineTriangleBucketSearch(void * this, int line_arg0, int line_arg1, void * out_triangle_vertices, void * query_context)",
        ("Wave447", "CPolyBucket__StartLineSearch", "+0x100"),
    ),
    "0x004ae2b0": (
        "CMeshPart__CreatePolyBucket",
        "void __fastcall CMeshPart__CreatePolyBucket(void * this)",
        ("Wave447", "0xb8-byte", "clones the mesh part", "optimizes the clone"),
    ),
    "0x004ae430": (
        "CMeshPart__GetNextLineTriangleFromBucketSearch",
        "int __thiscall CMeshPart__GetNextLineTriangleFromBucketSearch(void * this, void * out_triangle_vertices, void * line_search_context, void * query_context)",
        ("Wave447", "CPolyBucket__GetNextLineTriangle", "line/polybucket"),
    ),
    "0x004ae4b0": (
        "CMeshPart__Init",
        "void * __fastcall CMeshPart__Init(void * this)",
        ("Wave447", "0x28-byte helper", "0x128-byte CDXMeshVB"),
    ),
    "0x004ae640": (
        "CMeshPart__FreeOwnedResourcePointers",
        "void __thiscall CMeshPart__FreeOwnedResourcePointers(void * this)",
        ("Wave815", "0x004a51f0", "CPolyBucket__FreeBuffers", "+0x138"),
    ),
    "0x004ae860": (
        "CMeshPart__AllocateGeometry",
        "int __thiscall CMeshPart__AllocateGeometry(void * this, int dvertex_count, int pvertex_count, int triangle_count, int texcoord_count, int frame_count)",
        ("Wave447", "+0xa8/+0xac/+0xb0/+0xb8/+0xb4", "+0x134"),
    ),
    "0x004aea50": (
        "CMeshPart__ComputeLocalBoundsAndBoundingRadius",
        "void __fastcall CMeshPart__ComputeLocalBoundsAndBoundingRadius(void * this)",
        ("Wave447", "bounding radius", "+0xfc"),
    ),
    "0x004aede0": (
        "CMeshPart__LoadOldStyle_VersionA",
        "int __thiscall CMeshPart__LoadOldStyle_VersionA(void * this, void * mem_buffer, void * parent_mesh, void * mesh_resource_records, int material_index_limit, int legacy_flags_or_zero)",
        ("Wave815", "RET 0x14", "old-style", "RebuildPerVertexNormalsAndTangents"),
    ),
    "0x004af110": (
        "CMeshPart__LoadOldStyle_VersionB_WithExtraBlock",
        "int __thiscall CMeshPart__LoadOldStyle_VersionB_WithExtraBlock(void * this, void * mem_buffer, void * parent_mesh, void * mesh_resource_records, int material_index_limit, int legacy_flags_or_zero)",
        ("Wave815", "extra 4-byte block", "RET 0x14"),
    ),
    "0x004af470": (
        "CMeshPart__LoadVerticesAndTriangles",
        "void __thiscall CMeshPart__LoadVerticesAndTriangles(void * this, void * mem_buffer, void * part_table_entry, void * first_part_record, int part_index_limit, int unused_legacy_arg)",
        ("Wave449", "DVertex/PVertex/triangle", "ret 0x14"),
    ),
    "0x004afbb0": (
        "CMeshPart__LoadVerticesWithBones",
        "void __thiscall CMeshPart__LoadVerticesWithBones(void * this, void * mem_buffer, void * parent_mesh, int unused_arg3, int part_index_limit, int unused_arg5, int influence_count, int format_tag)",
        ("Wave449", "influence_count", "format_tag", "ret 0x1c"),
    ),
    "0x004b0800": (
        "CMeshPart__ApplyRootTransformRecursive",
        "void __thiscall CMeshPart__ApplyRootTransformRecursive(void * this, int parent_transform_dword00, int parent_transform_dword01, int parent_transform_dword02, int parent_transform_dword03, int parent_transform_dword04, int parent_transform_dword05, int parent_transform_dword06, int parent_transform_dword07, int parent_transform_dword08, int parent_transform_dword09, int parent_transform_dword10, int parent_transform_dword11, float origin_x, float origin_y, float origin_z, float origin_w, void * frame_override_part)",
        ("Wave448", "ret 0x44", "CopyPrimaryAxesToOutVec3Triplet"),
    ),
    "0x004b27a0": (
        "CMeshPart__LoadFromStream",
        "void * __cdecl CMeshPart__LoadFromStream(void * chunk_reader, void * mesh_part, void * parent_mesh)",
        ("Wave449", "0x13c CMeshPart", "chunk_reader", "CDXMeshVB"),
    ),
    "0x004b3180": (
        "CMeshPart__LoadMaterial",
        "void * __cdecl CMeshPart__LoadMaterial(void * chunk_reader, void * existing_material)",
        ("Wave449", "0x28-byte material", "reads two 0x10-byte blocks"),
    ),
    "0x004b31f0": (
        "CMeshPart__OptimizePolygons",
        "void __fastcall CMeshPart__OptimizePolygons(void * this)",
        ("Wave449", "0.2 threshold", "0.3", "removed vertices"),
    ),
    "0x004b3b70": (
        "CMeshPart__Clone",
        "void * __fastcall CMeshPart__Clone(void * this)",
        ("Wave449", "0x13c bytes", "CMeshPart__Init", "remapping triangle"),
    ),
    "0x004b4250": (
        "CMeshPart__Merge",
        "void __thiscall CMeshPart__Merge(void * this, void * source_part)",
        ("Wave449", "CMCMech__BuildInterpolatedPoseAndAnchor", "Ret 0x4"),
    ),
    "0x004bae70": (
        "CMeshPart__CanOptimizePart_Strict",
        "int __cdecl CMeshPart__CanOptimizePart_Strict(void * part)",
        ("Wave458", "CMesh__OptimizeParts", "wheel/body/axle", "tentacle"),
    ),
    "0x004bb040": (
        "CMeshPart__CanMergeInOptimizePass",
        "int __cdecl CMeshPart__CanMergeInOptimizePass(void * part)",
        ("Wave458", "CMesh__OptimizeParts", "buggy CORE/x1", "true-return helper"),
    ),
}

COMMON_DOC_TOKENS = (
    "Wave1100",
    WAVE_TAG,
    "0x004a51f0 CMeshPart__FreeResources",
    "0x004ae2b0 CMeshPart__CreatePolyBucket",
    "0x004ae860 CMeshPart__AllocateGeometry",
    "0x004aede0 CMeshPart__LoadOldStyle_VersionA",
    "0x004af470 CMeshPart__LoadVerticesAndTriangles",
    "0x004afbb0 CMeshPart__LoadVerticesWithBones",
    "0x004b27a0 CMeshPart__LoadFromStream",
    "0x004b31f0 CMeshPart__OptimizePolygons",
    "0x004b3b70 CMeshPart__Clone",
    "0x004b4250 CMeshPart__Merge",
    "0x004bae70 CMeshPart__CanOptimizePart_Strict",
    "0x004bb040 CMeshPart__CanMergeInOptimizePass",
    r"C:\dev\ONSLAUGHT2\MeshPart.cpp",
    "resfile_cmeshpartsize",
    "0x13c",
    "1560/1560 = 100.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6410/6410 = 100.00%",
    BACKUP_PATH,
    "read-only review",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "exact source-body identity proven",
    "exact source layout identity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 24,
        "pre-tags.tsv": 24,
        "pre-xrefs.tsv": 46,
        "pre-instructions.tsv": 6091,
        "pre-decompile/index.tsv": 24,
    }
    for relative, expected in expected_counts.items():
        rows = read_tsv(BASE / relative)
        require(len(rows) == expected, f"{relative} row count mismatch: {len(rows)} != {expected}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xref_targets = {normalize_address(row["target_addr"]) for row in read_tsv(BASE / "pre-xrefs.tsv")}
    instruction_targets = {normalize_address(row["target_addr"]) for row in read_tsv(BASE / "pre-instructions.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(contains_token(comment, token), f"missing comment token at {address}: {token}", failures)
            require("runtime" in comment.lower() or "rebuild parity" in comment.lower(), f"missing boundary language at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            actual_tags = {tag for tag in tag_row.get("tags", "").split(";") if tag}
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag at {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail evidence tag at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(address in instruction_targets, f"missing instruction rows for {address}", failures)

    require("0x004b27a0" in xref_targets, "missing xrefs for CMeshPart__LoadFromStream", failures)
    require("0x004ae2b0" in xref_targets, "missing xrefs for CMeshPart__CreatePolyBucket", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "pre-metadata.log": "targets=24 found=24 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=24 missing=0",
        "pre-xrefs.log": "Wrote 46 rows",
        "pre-instructions.log": "Wrote 6091 function-body instruction rows",
        "pre-decompile.log": "targets=24 dumped=24 missing=0 failed=0",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (175541127, 175541127.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        PROGRESS_JSON,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        MESHPART_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        README,
        CAPABILITIES,
        AGENTS,
    ]
    for path in docs:
        text = read_text(path)
        for token in COMMON_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-cmeshpart-load-geometry-review-wave1100")
        == r"py -3 tools\ghidra_cmeshpart_load_geometry_review_wave1100_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1100-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1100 --check",
        "missing aggregate package script",
        failures,
    )

    progress = read_json(PROGRESS_JSON)
    require(progress["latestWave"]["wave"] == "Wave1100 CMeshPart load geometry review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP_PATH, "progress backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6410, "progress total mismatch", failures)
    require(progress["functionQuality"]["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(progress["functionQuality"]["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(progress["functionQuality"]["paramSignatures"] == 0, "progress param mismatch", failures)
    require(progress["post100Reaudit"]["expandedStaticSurface"]["completed"] == 1560, "expanded count mismatch", failures)
    require(progress["post100Reaudit"]["wave911Focused"]["completed"] == 812, "wave911 focused mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1100 CMeshPart load geometry review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1100 CMeshPart load geometry review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
