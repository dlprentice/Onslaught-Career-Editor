#!/usr/bin/env python3
"""Validate Wave487 CPolyBucket static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave487-polybucket-004d3ce0"

TARGET_ORDER = [
    "0x004d3b10",
    "0x004d3ce0",
    "0x004d40d0",
    "0x004d4aa0",
    "0x004d4b30",
    "0x004d4b90",
    "0x004d4bc0",
    "0x004d4c00",
    "0x004d4f00",
    "0x004d50d0",
    "0x004d5650",
    "0x004d57c0",
    "0x004d5930",
    "0x004d59f0",
    "0x004d5e30",
    "0x004d61b0",
    "0x004d6210",
]

EXPECTED_SUMMARIES = {
    "apply_polybucket_wave487_dry.log": {
        "updated": 0,
        "skipped": 17,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_polybucket_wave487_apply.log": {
        "updated": 17,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_polybucket_wave487_verify_dry.log": {
        "updated": 0,
        "skipped": 17,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

COMMON_TAGS = {
    "comment-hardened",
    "polybucket",
    "polybucket-wave487",
    "retail-binary-evidence",
    "static-reaudit",
}

TARGETS = {
    "0x004d3b10": {
        "name": "CPolyBucket__AABBIntersectsSegment2D",
        "signature": "int __cdecl CPolyBucket__AABBIntersectsSegment2D(float rect_x, float rect_y, float rect_w, float rect_h, float * seg_p0, float * seg_p1)",
        "tags": COMMON_TAGS | {"aabb", "line-search", "signature-preserved"},
        "comment_tokens": ["preserved-signature helper", "2D segment", "AABB", "CPolyBucket__AdvanceLineSearch", "runtime collision behavior", "rebuild parity remain unproven"],
        "decompile_tokens": ["int __cdecl", "CPolyBucket__AABBIntersectsSegment2D", "float *seg_p0", "float *seg_p1"],
    },
    "0x004d3ce0": {
        "name": "CPolyBucket__TriangleInBucket",
        "signature": "int __thiscall CPolyBucket__TriangleInBucket(void * this, float * triangle_vertices, int bucket_x, int bucket_y)",
        "tags": COMMON_TAGS | {"bucket-overlap", "signature-corrected", "triangle-placement"},
        "comment_tokens": ["triangle vertex float block", "bucket X/Y", "cell corners", "Returns 1", "winding tolerance", "rebuild parity remain unproven"],
        "decompile_tokens": ["int __thiscall CPolyBucket__TriangleInBucket(void *this,float *triangle_vertices,int bucket_x,int bucket_y)", "return 1", "bucket_x", "bucket_y"],
    },
    "0x004d40d0": {
        "name": "CPolyBucket__Build",
        "signature": "int __thiscall CPolyBucket__Build(void * this, void * mesh_part)",
        "tags": COMMON_TAGS | {"builder", "mesh-part", "signature-corrected", "static-shadows"},
        "comment_tokens": ["CMeshPart__CreatePolyBucket", "CStaticShadows__BuildShadowMaps", "height masks", "CPolyBucket__TriangleInBucket", "concrete CPolyBucket/CMeshPart layouts", "rebuild parity remain unproven"],
        "decompile_tokens": ["int __thiscall CPolyBucket__Build(void *this,void *mesh_part)", "CPolyBucket__TriangleInBucket", "CPolyBucket__VertexToCompressed", "CPolyBucket__ResizeVertexBuffer"],
    },
    "0x004d4aa0": {
        "name": "CPolyBucket__VertexToCompressed",
        "signature": "void __thiscall CPolyBucket__VertexToCompressed(void * this, float * world_vertex, float * bucket_context)",
        "tags": COMMON_TAGS | {"helper-ecx", "signature-corrected", "vertex-compression"},
        "comment_tokens": ["saved this/ECX", "output compressed vertex", "signed-short scale", "rounding behavior", "concrete context layout", "rebuild parity remain unproven"],
        "decompile_tokens": ["void __thiscall CPolyBucket__VertexToCompressed(void *this,float *world_vertex,float *bucket_context)", "this", "world_vertex", "bucket_context"],
    },
    "0x004d4b30": {
        "name": "CPolyBucket__CompressedToVertex",
        "signature": "void __thiscall CPolyBucket__CompressedToVertex(void * this, float * out_world_vertex, float * bucket_context)",
        "tags": COMMON_TAGS | {"helper-ecx", "signature-corrected", "vertex-compression"},
        "comment_tokens": ["saved this/ECX", "compressed vertex pointer", "world-space vertex", "decompression precision", "concrete context layout", "rebuild parity remain unproven"],
        "decompile_tokens": ["void __thiscall CPolyBucket__CompressedToVertex(void *this,float *out_world_vertex,float *bucket_context)", "this", "out_world_vertex", "bucket_context"],
    },
    "0x004d4b90": {
        "name": "CPolyBucket__NormalizeVector",
        "signature": "void __thiscall CPolyBucket__NormalizeVector(void * this, float * out_vec3, float scale)",
        "tags": COMMON_TAGS | {"helper-ecx", "signature-corrected", "vector-normalize"},
        "comment_tokens": ["saved this/ECX", "divides the input xyz", "CPolyBucket__Build", "scale semantics", "runtime collision behavior", "rebuild parity remain unproven"],
        "decompile_tokens": ["void __thiscall CPolyBucket__NormalizeVector(void *this,float *out_vec3,float scale)", "out_vec3", "scale"],
    },
    "0x004d4bc0": {
        "name": "CPolyBucket__VertexEquals",
        "signature": "int __thiscall CPolyBucket__VertexEquals(void * this, float * vec_b)",
        "tags": COMMON_TAGS | {"helper-ecx", "signature-corrected", "vertex-dedup"},
        "comment_tokens": ["saved this/ECX", "first vec3 pointer", "exact equality", "compressed-vertex deduplication", "equality policy", "rebuild parity remain unproven"],
        "decompile_tokens": ["int __thiscall CPolyBucket__VertexEquals(void *this,float *vec_b)", "this", "vec_b", "return 1"],
    },
    "0x004d4c00": {
        "name": "CPolyBucket__StartSearch",
        "signature": "void * __thiscall CPolyBucket__StartSearch(void * this, float * position, float radius)",
        "tags": COMMON_TAGS | {"point-search", "query-state", "signature-corrected"},
        "comment_tokens": ["CMeshPart__StartTriangleBucketSearch", "point/radius query", "search generation", "CPolyBucket__GetNextTriangle", "caller contract", "rebuild parity remain unproven"],
        "decompile_tokens": ["void * __thiscall CPolyBucket__StartSearch(void *this,float *position,float radius)", "CPolyBucket__GetNextTriangle(this)", "position", "radius"],
    },
    "0x004d4f00": {
        "name": "CPolyBucket__GetNextTriangle",
        "signature": "void * __fastcall CPolyBucket__GetNextTriangle(void * this)",
        "tags": COMMON_TAGS | {"iterator", "point-search", "signature-corrected"},
        "comment_tokens": ["point-query iterator", "height mask", "current generation", "triangle record pointer", "search-state layout", "rebuild parity remain unproven"],
        "decompile_tokens": ["void * __fastcall CPolyBucket__GetNextTriangle(void *this)", "return", "this"],
    },
    "0x004d50d0": {
        "name": "CPolyBucket__StartLineSearch",
        "signature": "void * __thiscall CPolyBucket__StartLineSearch(void * this, float * start, float * end)",
        "tags": COMMON_TAGS | {"line-search", "query-state", "signature-corrected"},
        "comment_tokens": ["CMeshPart__StartLineTriangleBucketSearch", "segment-query initializer", "clips the segment", "line stepping globals", "CPolyBucket__GetNextLineTriangle", "rebuild parity remain unproven"],
        "decompile_tokens": ["void * __thiscall CPolyBucket__StartLineSearch(void *this,float *start,float *end)", "Geometry__ClipSegmentAgainstAABB3D", "CPolyBucket__GetNextLineTriangle(this,0)"],
    },
    "0x004d5650": {
        "name": "CPolyBucket__AdvanceLineSearch",
        "signature": "int __fastcall CPolyBucket__AdvanceLineSearch(void * this)",
        "tags": COMMON_TAGS | {"aabb", "iterator", "line-search", "signature-corrected"},
        "comment_tokens": ["line-search stepper", "global line-search cursor", "CPolyBucket__AABBIntersectsSegment2D", "updates current cell fields", "edge-case clipping behavior", "rebuild parity remain unproven"],
        "decompile_tokens": ["int __fastcall CPolyBucket__AdvanceLineSearch(void *this)", "CPolyBucket__AABBIntersectsSegment2D", "return 1"],
    },
    "0x004d57c0": {
        "name": "CPolyBucket__GetNextLineTriangle",
        "signature": "void * __thiscall CPolyBucket__GetNextLineTriangle(void * this, int stop_after_current_cell)",
        "tags": COMMON_TAGS | {"iterator", "line-search", "signature-corrected"},
        "comment_tokens": ["line-query iterator", "height-mask filters", "CPolyBucket__AdvanceLineSearch", "stop_after_current_cell", "flag semantics", "rebuild parity remain unproven"],
        "decompile_tokens": ["void * __thiscall CPolyBucket__GetNextLineTriangle(void *this,int stop_after_current_cell)", "CPolyBucket__AdvanceLineSearch(this)", "stop_after_current_cell"],
    },
    "0x004d5930": {
        "name": "CPolyBucket__GetRandomTriangle",
        "signature": "int __thiscall CPolyBucket__GetRandomTriangle(void * this, int * out_vertex_triplet)",
        "tags": COMMON_TAGS | {"effects-adjacent", "random-triangle", "signature-corrected"},
        "comment_tokens": ["CMesh__GetRandomVertexFromPolyBucket", "1000 random bucket selections", "Random__NextLCGAbs", "compressed-vertex pointers", "random distribution", "rebuild parity remain unproven"],
        "decompile_tokens": ["int __thiscall CPolyBucket__GetRandomTriangle(void *this,int *out_vertex_triplet)", "Random__NextLCGAbs", "out_vertex_triplet"],
    },
    "0x004d59f0": {
        "name": "CPolyBucket__Load",
        "signature": "void * __cdecl CPolyBucket__Load(int * chunk_reader)",
        "tags": COMMON_TAGS | {"deserialize", "mesh-part", "signature-corrected"},
        "comment_tokens": ["CMeshPart__LoadFromStream", "0xb8-byte", "serialized size of 0xb8", "compressed 6-byte vertices", "stream/chunk contract", "rebuild parity remain unproven"],
        "decompile_tokens": ["void * __cdecl CPolyBucket__Load(int *chunk_reader)", "0xb8", "chunk_reader"],
    },
    "0x004d5e30": {
        "name": "CPolyBucket__DebugRender",
        "signature": "void __fastcall CPolyBucket__DebugRender(void * this)",
        "tags": COMMON_TAGS | {"debug-render", "rendering", "signature-corrected"},
        "comment_tokens": ["CMeshRenderer__RenderMesh", "debug renderer", "meshtex_default.tga", "decompresses vertices", "runtime visual behavior", "rebuild parity remain unproven"],
        "decompile_tokens": ["void __fastcall CPolyBucket__DebugRender(void *this)", "meshtex_default.tga", "this"],
    },
    "0x004d61b0": {
        "name": "CPolyBucket__AddVertex",
        "signature": "int __thiscall CPolyBucket__AddVertex(void * this, void * compressed_vertex)",
        "tags": COMMON_TAGS | {"helper-ecx", "signature-corrected", "vertex-store"},
        "comment_tokens": ["saved this/ECX", "vertex-store record", "CPolyBucket__ReallocFromPool", "6-byte compressed vertex", "allocator ownership", "rebuild parity remain unproven"],
        "decompile_tokens": ["int __thiscall CPolyBucket__AddVertex(void *this,void *compressed_vertex)", "CPolyBucket__ReallocFromPool", "compressed_vertex"],
    },
    "0x004d6210": {
        "name": "CPolyBucket__ResizeVertexBuffer",
        "signature": "void __thiscall CPolyBucket__ResizeVertexBuffer(void * this, int new_capacity)",
        "tags": COMMON_TAGS | {"helper-ecx", "signature-corrected", "vertex-store"},
        "comment_tokens": ["saved this/ECX", "new_capacity * 6", "CPolyBucket__ReallocFromPool", "failure semantics", "allocator ownership", "rebuild parity remain unproven"],
        "decompile_tokens": ["void __thiscall CPolyBucket__ResizeVertexBuffer(void *this,int new_capacity)", "CPolyBucket__ReallocFromPool", "new_capacity * 6"],
    },
}

XREF_EXPECTATIONS = {
    "0x004d3b10": {("0x004d5775", "CPolyBucket__AdvanceLineSearch", "UNCONDITIONAL_CALL")},
    "0x004d3ce0": {("0x004d491b", "CPolyBucket__Build", "UNCONDITIONAL_CALL")},
    "0x004d40d0": {
        ("0x004ae3b3", "CMeshPart__CreatePolyBucket", "UNCONDITIONAL_CALL"),
        ("0x004ec4d7", "CStaticShadows__BuildShadowMaps", "UNCONDITIONAL_CALL"),
    },
    "0x004d4c00": {("0x004ae12d", "CMeshPart__StartTriangleBucketSearch", "UNCONDITIONAL_CALL")},
    "0x004d50d0": {("0x004ae23d", "CMeshPart__StartLineTriangleBucketSearch", "UNCONDITIONAL_CALL")},
    "0x004d5930": {("0x004b2637", "CMesh__GetRandomVertexFromPolyBucket", "UNCONDITIONAL_CALL")},
    "0x004d59f0": {("0x004b2f2a", "CMeshPart__LoadFromStream", "UNCONDITIONAL_CALL")},
    "0x004d5e30": {("0x004b6a18", "CMeshRenderer__RenderMesh", "UNCONDITIONAL_CALL")},
}

OVERCLAIMS = (
    "fully re'ed",
    "source identity proven",
    "runtime behavior proven",
    "exact layout proven",
    "rebuild parity proven",
)

STALE_SIGNATURE_TOKENS = (
    "undefined CPolyBucket__",
    "param_1",
    "param_2",
    "param_3",
    "param_4",
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
        for key in (
            "address",
            "target_addr",
            "from_addr",
            "function_entry",
            "instruction_addr",
        ):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"updated=(?P<updated>\d+)\s+skipped=(?P<skipped>\d+)\s+created=(?P<created>\d+)\s+"
        r"would_create=(?P<would_create>\d+)\s+renamed=(?P<renamed>\d+)\s+"
        r"would_rename=(?P<would_rename>\d+)\s+missing=(?P<missing>\d+)\s+bad=(?P<bad>\d+)",
        text,
    )
    if not match:
        return {}
    return {key: int(value) for key, value in match.groupdict().items()}


def check_summaries(base: Path, failures: list[str]) -> None:
    for filename, expected in EXPECTED_SUMMARIES.items():
        path = base / filename
        actual = parse_summary(path)
        if actual != expected:
            failures.append(f"{filename}: expected summary {expected}, got {actual or '<missing>'}")
        if "REPORT: Save succeeded" not in read_text(path):
            failures.append(f"{filename}: missing REPORT: Save succeeded")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    tag_rows = read_tsv(base / "post_tags.tsv")
    for address in TARGET_ORDER:
        expected = TARGETS[address]
        row = next((r for r in rows if r.get("address") == address), None)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: expected name {expected['name']}, got {row.get('name')}")
        if compact(row.get("signature", "")) != compact(expected["signature"]):
            failures.append(f"{address}: expected signature {expected['signature']}, got {row.get('signature')}")
        if "undefined" in row.get("signature", "").lower():
            failures.append(f"{address}: signature still contains undefined")
        comment = row.get("comment", "")
        for token in expected["comment_tokens"]:
            if not token_present(comment, token):
                failures.append(f"{address}: comment missing token {token!r}")
        for overclaim in OVERCLAIMS:
            if token_present(comment, overclaim):
                failures.append(f"{address}: comment contains overclaim {overclaim!r}")
        tag_row = next((r for r in tag_rows if r.get("address") == address), None)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            actual_tags = set(filter(None, re.split(r"[;,]\s*", tag_row.get("tags", ""))))
            missing_tags = expected["tags"] - actual_tags
            if missing_tags:
                failures.append(f"{address}: missing tags {sorted(missing_tags)}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address in TARGET_ORDER:
        expected = TARGETS[address]
        path = base / "post-decomp" / f"{address[2:]}_{expected['name']}.c"
        text = read_text(path)
        if not text:
            failures.append(f"{address}: missing decompile file {path.name}")
            continue
        for token in expected["decompile_tokens"]:
            if not token_present(text, token):
                failures.append(f"{address}: decompile missing token {token!r}")
        header = "\n".join(text.splitlines()[:20])
        for stale in STALE_SIGNATURE_TOKENS:
            if token_present(header, stale):
                failures.append(f"{address}: stale signature token remains in header: {stale!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    for target, refs in XREF_EXPECTATIONS.items():
        for from_addr, from_fn, ref_type in refs:
            row = next((r for r in rows if r.get("target_addr") == target and r.get("from_addr") == from_addr), None)
            if row is None:
                failures.append(f"{target}: missing xref from {from_addr}")
                continue
            if row.get("from_function") != from_fn:
                failures.append(f"{target}: xref {from_addr} expected function {from_fn}, got {row.get('from_function')}")
            if row.get("ref_type") != ref_type:
                failures.append(f"{target}: xref {from_addr} expected {ref_type}, got {row.get('ref_type')}")


def check_instruction_tokens(base: Path, failures: list[str]) -> None:
    text = read_text(base / "post_instructions.tsv")
    for token in (
        "0x004d3b10",
        "RET\t0x18",
        "CPolyBucket__TriangleInBucket",
        "0x004d4aa0",
        "0x004d4b30",
        "0x004d4c00",
        "0x004d50d0",
        "0x004d61b0",
        "0x004d6210",
    ):
        if token not in text:
            failures.append(f"post_instructions.tsv missing token {token!r}")


def run(base: Path = DEFAULT_BASE) -> list[str]:
    failures: list[str] = []
    check_summaries(base, failures)
    check_metadata(base, failures)
    check_decompile(base, failures)
    check_xrefs(base, failures)
    check_instruction_tokens(base, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = run(args.base)
    if failures:
        print("FAIL Wave487 CPolyBucket probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS Wave487 CPolyBucket probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
