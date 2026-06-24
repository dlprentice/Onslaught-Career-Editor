#!/usr/bin/env python3
"""Validate Wave447 CMeshPart Ghidra metadata hardening."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave447-cmeshpart-bucket-current"
COMMON_TAGS = {"static-reaudit", "cmeshpart-wave447", "retail-binary-evidence"}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 9,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004adff0": target(
        "CMeshPart__SetVertexCount",
        "void __thiscall CMeshPart__SetVertexCount(void * this, int vertex_count)",
        ["five-pointer vertex channel block", "count*0x14", "line 0x6b", "rebuild parity remain unproven"],
        ["meshpart", "vertex-count", "allocation", "signature-corrected", "comment-hardened"],
        ["vertex_count", "OID__AllocObject(vertex_count * 0x14", "+ 0x1c"],
    ),
    "0x004ae110": target(
        "CMeshPart__StartTriangleBucketSearch",
        "int __thiscall CMeshPart__StartTriangleBucketSearch(void * this, int search_key0, int search_key1, void * out_triangle_vertices, void * query_context)",
        ["polybucket triangle search", "CPolyBucket__StartSearch", "output triplet", "rebuild parity remain unproven"],
        ["meshpart", "polybucket", "triangle-search", "signature-corrected", "comment-hardened"],
        ["CPolyBucket__StartSearch(search_key0,search_key1)", "out_triangle_vertices", "+ 0x100"],
    ),
    "0x004ae1a0": target(
        "CMeshPart__GetNextTriangleFromBucketSearch",
        "int __thiscall CMeshPart__GetNextTriangleFromBucketSearch(void * this, void * out_triangle_vertices, void * query_context)",
        ["CPolyBucket__GetNextTriangle", "16-bit local indices", "output triplet", "rebuild parity remain unproven"],
        ["meshpart", "polybucket", "triangle-search", "signature-corrected", "comment-hardened"],
        ["CPolyBucket__GetNextTriangle()", "out_triangle_vertices", "+ 0x100"],
    ),
    "0x004ae220": target(
        "CMeshPart__StartLineTriangleBucketSearch",
        "int __thiscall CMeshPart__StartLineTriangleBucketSearch(void * this, int line_arg0, int line_arg1, void * out_triangle_vertices, void * query_context)",
        ["line/polybucket triangle search", "CPolyBucket__StartLineSearch", "first triangle's three 16-bit local indices", "rebuild parity remain unproven"],
        ["meshpart", "polybucket", "line-triangle-search", "signature-corrected", "comment-hardened"],
        ["CPolyBucket__StartLineSearch(line_arg0,line_arg1)", "out_triangle_vertices", "+ 0x100"],
    ),
    "0x004ae2b0": target(
        "CMeshPart__CreatePolyBucket",
        "void __fastcall CMeshPart__CreatePolyBucket(void * this)",
        ["0xb8-byte polybucket-style object", "mesh types 1 or 3", "boss_fenrir/tempbuilding3", "rebuild parity remain unproven"],
        ["meshpart", "polybucket", "allocation", "clone", "signature-corrected", "comment-hardened"],
        ["OID__AllocObject(0xb8,0x46", "CMeshPart__Clone()", "CPolyBucket__Build"],
    ),
    "0x004ae430": target(
        "CMeshPart__GetNextLineTriangleFromBucketSearch",
        "int __thiscall CMeshPart__GetNextLineTriangleFromBucketSearch(void * this, void * out_triangle_vertices, void * line_search_context, void * query_context)",
        ["CPolyBucket__GetNextLineTriangle", "local triangle indices", "caller output triplet", "rebuild parity remain unproven"],
        ["meshpart", "polybucket", "line-triangle-search", "signature-corrected", "comment-hardened"],
        ["CPolyBucket__GetNextLineTriangle(line_search_context)", "out_triangle_vertices", "+ 0x100"],
    ),
    "0x004ae4b0": target(
        "CMeshPart__Init",
        "void * __fastcall CMeshPart__Init(void * this)",
        ["4x3 basis block", "+0x12c = 0.5f", "CDXMeshVB-style object", "rebuild parity remain unproven"],
        ["meshpart", "initializer", "allocation", "signature-corrected", "comment-hardened"],
        ["OID__AllocObject(0x28", "OID__AllocObject(0x128", "CDXMeshVB__ctor_like_0054bf80"],
    ),
    "0x004ae860": target(
        "CMeshPart__AllocateGeometry",
        "int __thiscall CMeshPart__AllocateGeometry(void * this, int dvertex_count, int pvertex_count, int triangle_count, int texcoord_count, int frame_count)",
        ["DVertex/PVertex/triangle/texcoord/frame counts", "allocates DVertex storage", "allocates triangles", "rebuild parity remain unproven"],
        ["meshpart", "geometry-allocation", "vertex-buffer", "signature-corrected", "comment-hardened"],
        ["dvertex_count * 0x60", "pvertex_count", "triangle_count"],
    ),
    "0x004aea50": target(
        "CMeshPart__ComputeLocalBoundsAndBoundingRadius",
        "void __fastcall CMeshPart__ComputeLocalBoundsAndBoundingRadius(void * this)",
        ["min/max local bounds", "bounding radius", "helper +0x24", "rebuild parity remain unproven"],
        ["meshpart", "bounds", "bounding-radius", "signature-corrected", "comment-hardened"],
        ["SQRT(fVar5)", "+ 0x130", "+ 0x24"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004adff0", "CMesh__Load"),
    ("0x004adff0", "CMesh__InitSingleVertexPartDefaults"),
    ("0x004adff0", "CMesh__Deserialize"),
    ("0x004ae110", "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart"),
    ("0x004ae1a0", "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart"),
    ("0x004ae220", "CStaticShadows__BuildShadowMaps"),
    ("0x004ae220", "CMeshCollisionVolume__VFunc_04_004ad830"),
    ("0x004ae2b0", "CMesh__CreatePolyBucketsForAllParts"),
    ("0x004ae430", "CStaticShadows__BuildShadowMaps"),
    ("0x004ae430", "CMeshCollisionVolume__VFunc_04_004ad830"),
    ("0x004ae4b0", "CMesh__Load"),
    ("0x004ae4b0", "CMesh__Deserialize"),
    ("0x004ae4b0", "CMeshPart__Clone"),
    ("0x004ae860", "CMesh__Load"),
    ("0x004ae860", "CMeshPart__LoadFromStream"),
    ("0x004ae860", "CMeshPart__Clone"),
    ("0x004aea50", "CMesh__Load"),
]

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully re'ed",
)


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


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr"):
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


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    prefix = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{prefix}_*.c"))
    return read_text(matches[0]) if matches else ""


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ["updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def relative_or_absolute(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def check_verify_log(base: Path, failures: list[str]) -> None:
    text = read_text(base / "apply_verify_dry.log")
    if not text:
        failures.append("apply_verify_dry.log: missing or empty")
        return
    summary = parse_summary(text)
    if summary != EXPECTED_VERIFY_DRY:
        failures.append(f"apply_verify_dry.log: summary mismatch expected {EXPECTED_VERIFY_DRY}, got {summary}")
    for token in ("FAIL:", "Exception", "LockException"):
        if token in text:
            failures.append(f"apply_verify_dry.log: unexpected failure token {token!r}")
    if "REPORT: Save succeeded" not in text:
        failures.append("apply_verify_dry.log: missing Ghidra save-success marker")


def check_apply_log(base: Path, failures: list[str]) -> None:
    text = read_text(base / "apply.log")
    summary = parse_summary(text)
    expected = {
        "updated": 9,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    }
    if summary != expected:
        failures.append(f"apply.log: summary mismatch expected {expected}, got {summary}")
    if "REPORT: Save succeeded" not in text:
        failures.append("apply.log: missing Ghidra save-success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")
    if len(metadata) != len(TARGETS):
        failures.append(f"post_metadata.tsv: expected {len(TARGETS)} rows, got {len(metadata)}")
    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing post_metadata row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')!r}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: signature mismatch {row.get('signature')!r}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        lowered_comment = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered_comment:
                failures.append(f"{address}: overclaim token present {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing post_tags row")
        else:
            actual_tags = {item.strip() for item in re.split(r"[;,]", tag_row.get("tags", "")) if item.strip()}
            missing_tags = sorted(set(spec["tags"]) - actual_tags)  # type: ignore[arg-type]
            if missing_tags:
                failures.append(f"{address}: missing tags {missing_tags}")

        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing post-decomp export")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    if len(rows) < len(EXPECTED_XREF_EDGES):
        failures.append(f"post_xrefs.tsv: expected at least {len(EXPECTED_XREF_EDGES)} rows, got {len(rows)}")
    for target_addr, from_name in EXPECTED_XREF_EDGES:
        wanted = normalize_address(target_addr)
        if not any(row.get("target_addr") == wanted and row.get("from_function") == from_name for row in rows):
            failures.append(f"post_xrefs.tsv: missing edge {wanted} <- {from_name}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    if not base.is_dir():
        failures.append(f"base directory missing: {relative_or_absolute(base)}")
        return "FAIL", failures
    check_apply_log(base, failures)
    check_verify_log(base, failures)
    check_metadata(base, failures)
    check_xrefs(base, failures)
    return ("PASS" if not failures else "FAIL"), failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    base = args.base.resolve()
    status, failures = run_checks(base)
    result = {
        "schema": "ghidra-cmeshpart-wave447-probe.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "base": relative_or_absolute(base),
        "targets": len(TARGETS),
        "failures": failures,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Wave447 CMeshPart probe: {status}")
        print(f"Base: {relative_or_absolute(base)}")
        print(f"Targets: {len(TARGETS)}")
        for failure in failures:
            print(f"- {failure}")
    if args.check and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
