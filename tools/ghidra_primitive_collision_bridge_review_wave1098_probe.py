#!/usr/bin/env python3
"""Validate Wave1098 primitive collision bridge review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1098-primitive-collision-bridge-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_primitive_collision_bridge_review_wave1098_2026-06-04.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1098_recheck_2026-06-04.md"
PACKAGE_JSON = ROOT / "package.json"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
CYLINDER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "cylinder.cpp" / "_index.md"
MESH_COLLISION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshCollisionVolume.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
README = ROOT / "README.MD"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
AGENTS = ROOT / "AGENTS.md"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified"
WAVE_TAG = "primitive-collision-bridge-review-wave1098"

TARGETS = {
    "0x004059a0": ("CCylinder__VFunc_01_004059a0", "int __thiscall CCylinder__VFunc_01_004059a0(void * this, void * forwardedA, void * forwardedB, void * dispatchObject, void * forwardedC)"),
    "0x004098c0": ("CLine__VFunc_01_004098c0", "int __thiscall CLine__VFunc_01_004098c0(void * this, void * arg0, void * arg1, void * dispatch_target, void * arg3)"),
    "0x004098e0": ("CLine__ctor_copy", "void __thiscall CLine__ctor_copy(void * this, void * sourceLine)"),
    "0x0040d470": ("CLine__ctor_fromEndpoints", "void __thiscall CLine__ctor_fromEndpoints(void * this, void * startPoint, void * endPoint)"),
    "0x00426320": ("CSphere__VFunc_01_00426320", "int __thiscall CSphere__VFunc_01_00426320(void * this, void * query_arg0, void * query_arg1, void * delegate_object, void * query_arg3)"),
    "0x00426340": ("CLine__ScalarDeletingDestructor_00426340", "void * __thiscall CLine__ScalarDeletingDestructor_00426340(void * this, int deleteFlags)"),
    "0x00426360": ("CLine__SetBaseVtable_00426360", "void __fastcall CLine__SetBaseVtable_00426360(void * this)"),
    "0x0043fde0": ("CCylinder__ctor", "void __thiscall CCylinder__ctor(void * this, void * sourceCylinder)"),
    "0x0043fe20": ("CCylinder__ResolveCollisionVFunc02", "int __thiscall CCylinder__ResolveCollisionVFunc02(void * this, void * movingStateA, void * movingStateB, void * radiusContext, void * contactOut)"),
    "0x004e4d70": ("CSphere__VFunc02_ResolveCollisionAsCylinder", "void __thiscall CSphere__VFunc02_ResolveCollisionAsCylinder(void * this, void * collision_arg0, void * collision_arg1, void * collision_arg2, int collision_flags)"),
    "0x004abe50": ("CMeshCollisionVolume__VFunc_02_004abe50", "int __thiscall CMeshCollisionVolume__VFunc_02_004abe50(void * this, void * query_arg0, void * query_arg1, void * source_sphere_record, void * contact_record)"),
    "0x004ac140": ("CMeshCollisionVolume__TestSweptSphereAgainstBounds", "int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstBounds(void * part_context, void * bounds_record, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)"),
    "0x004ac4a0": ("CMeshCollisionVolume__TestSweptSphereAgainstMeshPart", "int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstMeshPart(void * part_context, void * mesh_part, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)"),
    "0x004ac6e0": ("CMeshCollisionVolume__VFunc_03_004ac6e0", "int __thiscall CMeshCollisionVolume__VFunc_03_004ac6e0(void * this, void * query_arg0, float * motion_record, void * query_arg2, void * contact_record)"),
    "0x00478510": ("CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore", "int __cdecl CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore(void * triangle_vertex0, void * triangle_vertex1, void * triangle_vertex2, void * sphere_start, void * sweep_delta, float sphere_radius, void * contact_record)"),
    "0x00478c20": ("Geometry__IntersectSegmentTriangleAndStoreHit", "int __cdecl Geometry__IntersectSegmentTriangleAndStoreHit(void * triangle_vertex0, void * triangle_vertex1, void * triangle_vertex2, void * segment_start, void * segment_end, void * contact_record)"),
    "0x00479020": ("CMeshCollisionVolume__IsDirectionInsideTrianglePrism", "int __cdecl CMeshCollisionVolume__IsDirectionInsideTrianglePrism(void * vertex0, void * vertex1, void * vertex2, void * vertex3, void * direction)"),
    "0x00479200": ("Geometry__SelectClosestPointOnTriangleEdges", "void __cdecl Geometry__SelectClosestPointOnTriangleEdges(void * outClosest, void * vertexA, void * vertexB, void * vertexC, void * queryPoint)"),
    "0x00479630": ("Geometry__RaySphereEntryDistance", "double __cdecl Geometry__RaySphereEntryDistance(void * rayStart, void * rayEnd, float radius)"),
    "0x004acde0": ("CMeshCollisionVolume__InitContactOutputRecord", "void CMeshCollisionVolume__InitContactOutputRecord(void)"),
    "0x004ad830": ("CMeshCollisionVolume__VFunc_04_004ad830", "int __thiscall CMeshCollisionVolume__VFunc_04_004ad830(void * this, void * query_arg0, void * state_record, void * segment_offsets, void * contact_record)"),
}

COMMON_TAGS = {
    "static-reaudit",
    WAVE_TAG,
    "wave1098-readback-verified",
    "retail-binary-evidence",
    "tag-normalized",
    "comment-hardened",
    "primitive-collision",
    "collision-geometry",
}

COMMON_DOC_TOKENS = (
    "Wave1098",
    WAVE_TAG,
    "0x004059a0 CCylinder__VFunc_01_004059a0",
    "0x004098c0 CLine__VFunc_01_004098c0",
    "0x004098e0 CLine__ctor_copy",
    "0x00426320 CSphere__VFunc_01_00426320",
    "0x0043fe20 CCylinder__ResolveCollisionVFunc02",
    "0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50",
    "0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds",
    "0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart",
    "0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0",
    "0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
    "0x00478c20 Geometry__IntersectSegmentTriangleAndStoreHit",
    "0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830",
    "1560/1560 = 100.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6410/6410 = 100.00%",
    BACKUP_PATH,
    "tag-only normalization",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime collision correctness proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
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
        "pre-metadata.tsv": 21,
        "pre-tags.tsv": 21,
        "pre-xrefs.tsv": 79,
        "pre-instructions.tsv": 3707,
        "pre-decompile/index.tsv": 21,
        "pre-vtable-slots.tsv": 64,
        "post-metadata.tsv": 21,
        "post-tags.tsv": 21,
        "post-xrefs.tsv": 79,
        "post-instructions.tsv": 3707,
        "post-decompile/index.tsv": 21,
        "post-vtable-slots.tsv": 64,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {sorted(COMMON_TAGS - actual_tags)}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

    slots = read_tsv(BASE / "post-vtable-slots.tsv")
    slot_map = {(normalize_address(row["vtable"]), int(row["slot_index"])): row for row in slots}
    expected_slots = {
        ("0x005d88cc", 1): "CCylinder__VFunc_01_004059a0",
        ("0x005d88cc", 2): "CCylinder__ResolveCollisionVFunc02",
        ("0x005d8bfc", 1): "CLine__VFunc_01_004098c0",
        ("0x005d8bfc", 2): "CLine__VFunc_01_004098c0",
        ("0x005d95e8", 0): "CLine__ScalarDeletingDestructor_00426340",
        ("0x005d95e8", 1): "CSphere__VFunc_01_00426320",
        ("0x005d95d0", 0): "CMeshCollisionVolume__VFunc_02_004abe50",
        ("0x005d95d0", 1): "CMeshCollisionVolume__VFunc_03_004ac6e0",
        ("0x005d95d0", 2): "CMeshCollisionVolume__VFunc_04_004ad830",
        ("0x005d95d0", 7): "CSphere__VFunc_01_00426320",
        ("0x005d95d0", 8): "CSphere__VFunc02_ResolveCollisionAsCylinder",
    }
    for key, expected_name in expected_slots.items():
        row = slot_map.get(key)
        require(row is not None, f"missing vtable slot {key}", failures)
        if row is not None:
            require(row.get("function_name") == expected_name, f"vtable slot {key} mismatch", failures)
            require(row.get("status") == "OK", f"vtable slot {key} status mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=180 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=21 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=180 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=21 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=21 found=21 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=21 missing=0",
        "post-xrefs.log": "Wrote 79 rows",
        "post-instructions.log": "Wrote 3707 function-body instruction rows",
        "post-decompile.log": "targets=21 dumped=21 missing=0 failed=0",
        "post-vtable-slots.log": "targets=4 rows=64",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_backup_and_progress(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175541127, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)

    progress = read_json(PROGRESS_JSON)
    require(progress["latestWave"]["wave"] == "Wave1098 primitive collision bridge review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["tag"] == WAVE_TAG, "progress tag mismatch", failures)
    require(progress["functionQuality"]["strictCleanSignatureProxy"] == "6410/6410 = 100.00%", "progress closure mismatch", failures)
    require(progress["post100Reaudit"]["expandedStaticSurface"]["percent"] == "100.00%", "expanded progress mismatch", failures)
    require(progress["post100Reaudit"]["wave911Focused"]["percent"] == "57.67%", "Wave911 focused progress mismatch", failures)
    require(progress["latestSample"]["ok"] == 21 and progress["latestSample"]["total"] == 21, "latest sample mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        CYLINDER_DOC,
        MESH_COLLISION_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        README,
        CAPABILITIES,
        AGENTS,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in COMMON_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-primitive-collision-bridge-review-wave1098") == r"py -3 tools\ghidra_primitive_collision_bridge_review_wave1098_probe.py --check", "missing focused package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1098-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1098 --check", "missing aggregate package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_backup_and_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1098 primitive collision bridge review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1098 primitive collision bridge review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
