#!/usr/bin/env python3
"""Validate Wave939 MeshCollisionVolume swept-sphere query review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave939-meshcollisionvolume-swept-sphere-query-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_meshcollisionvolume_swept_sphere_query_review_wave939_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
MCV_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshCollisionVolume.cpp" / "_index.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mesh.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"G:\GhidraBackups\BEA_20260528-024426_post_wave939_meshcollisionvolume_swept_sphere_query_review_verified"
SCRIPT_NAME = "test:ghidra-meshcollisionvolume-swept-sphere-query-review-wave939"
SCRIPT_VALUE = r"py -3 tools\ghidra_meshcollisionvolume_swept_sphere_query_review_wave939_probe.py --check"

TARGETS = {
    "0x004ac6e0": (
        "CMeshCollisionVolume__VFunc_03_004ac6e0",
        "int __thiscall CMeshCollisionVolume__VFunc_03_004ac6e0(void * this, void * query_arg0, float * motion_record, void * query_arg2, void * contact_record)",
    ),
    "0x004abe50": (
        "CMeshCollisionVolume__VFunc_02_004abe50",
        "int __thiscall CMeshCollisionVolume__VFunc_02_004abe50(void * this, void * query_arg0, void * query_arg1, void * source_sphere_record, void * contact_record)",
    ),
    "0x004ac000": (
        "CMeshCollisionVolume__InitDirectionLookupTable",
        "void __cdecl CMeshCollisionVolume__InitDirectionLookupTable(void)",
    ),
    "0x004ac140": (
        "CMeshCollisionVolume__TestSweptSphereAgainstBounds",
        "int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstBounds(void * part_context, void * bounds_record, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)",
    ),
    "0x004ac4a0": (
        "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart",
        "int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstMeshPart(void * part_context, void * mesh_part, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)",
    ),
    "0x004acf30": (
        "CMeshCollisionVolume__ResolveContactNormalAndPlane",
        "int __stdcall CMeshCollisionVolume__ResolveContactNormalAndPlane(float * contact_record, float hit_x, float hit_y, float hit_z, float hit_w, float normal_x, float normal_y, float normal_z, float normal_w, float unused_source_w, float * out_contact_point, float * out_contact_normal)",
    ),
    "0x004ad600": (
        "CMeshCollisionVolume__SetPartBounds",
        "void __thiscall CMeshCollisionVolume__SetPartBounds(void * this, void * mesh, int part_index, float bounds_status)",
    ),
}

CONTEXT = {
    "0x00478510": "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
    "0x00479020": "CMeshCollisionVolume__IsDirectionInsideTrianglePrism",
    "0x004ad830": "CMeshCollisionVolume__VFunc_04_004ad830",
    "0x004acde0": "CMeshCollisionVolume__InitContactOutputRecord",
    "0x004262e0": "CMeshCollisionVolume__VFunc_05_004262e0",
    "0x0043fe20": "CCylinder__ResolveCollisionVFunc02",
    "0x00477ba0": "Vec3__MagnitudeSquared",
    "0x00478160": "Geometry__ClipSegmentAgainstAABB3D",
    "0x00478c20": "Geometry__IntersectSegmentTriangleAndStoreHit",
    "0x00479200": "Geometry__SelectClosestPointOnTriangleEdges",
}

EXPECTED_XREFS = {
    ("0x004ac6e0", "0x005d95d4", "<no_function>", "DATA"),
    ("0x004abe50", "0x005d95d0", "<no_function>", "DATA"),
    ("0x004ac000", "0x004ac14c", "CMeshCollisionVolume__TestSweptSphereAgainstBounds", "UNCONDITIONAL_CALL"),
    ("0x004ac140", "0x004aca03", "CMeshCollisionVolume__VFunc_03_004ac6e0", "UNCONDITIONAL_CALL"),
    ("0x004ac4a0", "0x004aca31", "CMeshCollisionVolume__VFunc_03_004ac6e0", "UNCONDITIONAL_CALL"),
    ("0x004acf30", "0x004acd1b", "CMeshCollisionVolume__VFunc_03_004ac6e0", "UNCONDITIONAL_CALL"),
    ("0x004ad600", "0x004ac8b1", "CMeshCollisionVolume__VFunc_03_004ac6e0", "UNCONDITIONAL_CALL"),
    ("0x004ad600", "0x004ad9a8", "CMeshCollisionVolume__VFunc_04_004ad830", "UNCONDITIONAL_CALL"),
}

EXPECTED_CONTEXT_XREFS = {
    ("0x00478510", "0x004ac454", "CMeshCollisionVolume__TestSweptSphereAgainstBounds", "UNCONDITIONAL_CALL"),
    ("0x00478510", "0x004ac690", "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart", "UNCONDITIONAL_CALL"),
    ("0x00479020", "0x004788e2", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore", "UNCONDITIONAL_CALL"),
    ("0x004ad830", "0x005d95d8", "<no_function>", "DATA"),
    ("0x004acde0", "0x004acd22", "CMeshCollisionVolume__VFunc_03_004ac6e0", "CONDITIONAL_JUMP"),
    ("0x004262e0", "0x005d95dc", "<no_function>", "DATA"),
    ("0x0043fe20", "0x004e4de0", "CSphere__VFunc02_ResolveCollisionAsCylinder", "UNCONDITIONAL_CALL"),
    ("0x00477ba0", "0x00478b37", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore", "UNCONDITIONAL_CALL"),
    ("0x00478160", "0x0049216a", "CMapWho__GetFirstEntryWithinLine", "UNCONDITIONAL_CALL"),
    ("0x00478c20", "0x004adc5d", "CMeshCollisionVolume__VFunc_04_004ad830", "UNCONDITIONAL_CALL"),
    ("0x00479200", "0x00478902", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore", "UNCONDITIONAL_CALL"),
}

EXPECTED_INSTRUCTIONS = {
    ("post-instructions.tsv", "0x004abed9", "CALL", "[EAX + 0xc]", "CMeshCollisionVolume__VFunc_02_004abe50"),
    ("post-instructions.tsv", "0x004ac14c", "CALL", "0x004ac000", "CMeshCollisionVolume__TestSweptSphereAgainstBounds"),
    ("post-instructions.tsv", "0x004ac454", "CALL", "0x00478510", "CMeshCollisionVolume__TestSweptSphereAgainstBounds"),
    ("post-instructions.tsv", "0x004ac46b", "CMP", "EBP, 0x704c5c", "CMeshCollisionVolume__TestSweptSphereAgainstBounds"),
    ("post-instructions.tsv", "0x004ac690", "CALL", "0x00478510", "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart"),
    ("post-instructions.tsv", "0x004ac8b1", "CALL", "0x004ad600", "CMeshCollisionVolume__VFunc_03_004ac6e0"),
    ("post-instructions.tsv", "0x004aca03", "CALL", "0x004ac140", "CMeshCollisionVolume__VFunc_03_004ac6e0"),
    ("post-instructions.tsv", "0x004aca31", "CALL", "0x004ac4a0", "CMeshCollisionVolume__VFunc_03_004ac6e0"),
    ("post-instructions.tsv", "0x004acd1b", "CALL", "0x004acf30", "CMeshCollisionVolume__VFunc_03_004ac6e0"),
    ("post-instructions.tsv", "0x004acd22", "JZ", "0x004acde0", "CMeshCollisionVolume__VFunc_03_004ac6e0"),
    ("post-instructions.tsv", "0x004acd6e", "CMP", "ECX, 0x6", "CMeshCollisionVolume__VFunc_03_004ac6e0"),
    ("context-instructions.tsv", "0x004788e2", "CALL", "0x00479020", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore"),
    ("context-instructions.tsv", "0x00478902", "CALL", "0x00479200", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore"),
    ("context-instructions.tsv", "0x00478b37", "CALL", "0x00477ba0", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore"),
    ("context-instructions.tsv", "0x004adc5d", "CALL", "0x00478c20", "CMeshCollisionVolume__VFunc_04_004ad830"),
}

DECOMPILE_TOKENS = {
    "post-decompile/004abe50_CMeshCollisionVolume__VFunc_02_004abe50.c": ("CMeshCollisionVolume__VFunc_02_004abe50", "0x10"),
    "post-decompile/004ac140_CMeshCollisionVolume__TestSweptSphereAgainstBounds.c": ("CMeshCollisionVolume__InitDirectionLookupTable", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore"),
    "post-decompile/004ac4a0_CMeshCollisionVolume__TestSweptSphereAgainstMeshPart.c": ("CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore", "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart"),
    "post-decompile/004ac6e0_CMeshCollisionVolume__VFunc_03_004ac6e0.c": ("CMeshCollisionVolume__SetPartBounds", "CMeshCollisionVolume__ResolveContactNormalAndPlane"),
    "post-decompile/004acf30_CMeshCollisionVolume__ResolveContactNormalAndPlane.c": ("CMeshCollisionVolume__ResolveContactNormalAndPlane",),
    "post-decompile/004ad600_CMeshCollisionVolume__SetPartBounds.c": ("CMeshCollisionVolume__SetPartBounds",),
    "context-decompile/004acde0_CMeshCollisionVolume__InitContactOutputRecord.c": ("CMeshCollisionVolume__InitContactOutputRecord", "EBX"),
}

CORE_TOKENS = (
    "Wave939",
    "meshcollisionvolume-swept-sphere-query-review-wave939",
    "173/1408 = 12.29%",
    "6113/6113 = 100.00%",
    BACKUP,
    "comment-only mutation",
    "24-entry direction-pointer table as 8 triangle tests",
    "0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50",
    "0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0",
    "0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds",
    "0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart",
    "0x004acf30 CMeshCollisionVolume__ResolveContactNormalAndPlane",
    "0x004ad600 CMeshCollisionVolume__SetPartBounds",
    "0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
    "0x004acde0 CMeshCollisionVolume__InitContactOutputRecord",
)

OVERCLAIMS = (
    "runtime collision correctness proven",
    "runtime swept-sphere behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = (value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


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


def has_xref(path: str, expected: tuple[str, str, str, str]) -> bool:
    target, from_addr, from_func, ref_type = expected
    for row in read_tsv(BASE / path):
        if (
            normalize_address(row.get("target_addr", "")) == normalize_address(target)
            and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
            and row.get("from_function") == from_func
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 7,
        "tags.tsv": 7,
        "xrefs.tsv": 14,
        "instructions.tsv": 1747,
        "decompile/index.tsv": 7,
        "context-metadata.tsv": 10,
        "context-tags.tsv": 10,
        "context-xrefs.tsv": 18,
        "context-instructions.tsv": 2743,
        "context-decompile/index.tsv": 10,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 14,
        "post-instructions.tsv": 1747,
        "post-decompile/index.tsv": 7,
    }
    for rel, count in expected_counts.items():
        require(len(read_tsv(BASE / rel)) == count, f"{rel} row count mismatch", failures)

    metadata = row_map(BASE / "post-metadata.tsv")
    tags = row_map(BASE / "post-tags.tsv")
    decomp = row_map(BASE / "post-decompile" / "index.tsv")
    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
        dec = decomp.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch {address}", failures)

    context_meta = row_map(BASE / "context-metadata.tsv")
    for address, name in CONTEXT.items():
        row = context_meta.get(address)
        require(row is not None and row.get("name") == name and row.get("status") == "OK", f"context metadata mismatch {address}", failures)

    bounds = metadata.get("0x004ac140", {})
    comment = bounds.get("comment", "")
    require("24-entry direction-pointer table as 8 triangle tests" in comment, "normalized bounds comment missing", failures)
    require("24 direction-table triangle faces" not in comment, "old 24-face wording still present", failures)
    tag_row = tags.get("0x004ac140", {})
    tag_set = set(tag_row.get("tags", "").split(";"))
    for tag in ("meshcollisionvolume-swept-sphere-query-review-wave939", "wave939-readback-verified", "comment-normalized"):
        require(tag in tag_set, f"missing Wave939 tag {tag}", failures)

    for expected in EXPECTED_XREFS:
        require(has_xref("post-xrefs.tsv", expected), f"missing primary xref {expected}", failures)
    for expected in EXPECTED_CONTEXT_XREFS:
        require(has_xref("context-xrefs.tsv", expected), f"missing context xref {expected}", failures)
    for expected in EXPECTED_INSTRUCTIONS:
        require(has_instruction(expected), f"missing instruction {expected}", failures)
    for rel, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / rel)
        for token in tokens:
            require(token in text, f"missing decompile token {rel}: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_logs = {
        "metadata.log": "targets=7 found=7 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "xrefs.log": "Wrote 14 rows",
        "instructions.log": "Wrote 1747 function-body instruction rows",
        "decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "context-metadata.log": "targets=10 found=10 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "context-xrefs.log": "Wrote 18 rows",
        "context-instructions.log": "Wrote 2743 function-body instruction rows",
        "context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "apply-dry.log": "SUMMARY updated=0 would_update=1 skipped=0 missing=0 bad=0",
        "apply.log": "SUMMARY updated=1 would_update=0 skipped=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY updated=0 would_update=0 skipped=1 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-xrefs.log": "Wrote 14 rows",
        "post-instructions.log": "Wrote 1747 function-body instruction rows",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    for rel, token in expected_logs.items():
        text = read_text(BASE / rel)
        require(token in text, f"missing log token {rel}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIGNATURE:", "FAIL:", "failed=1", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected log failure {rel}: {bad}", failures)

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

    for path in [NOTE, CAMPAIGN, MCV_DOC, MESH_DOC, *STATE_FILES]:
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
        print("Wave939 MeshCollisionVolume swept-sphere query probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave939 MeshCollisionVolume swept-sphere query probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
