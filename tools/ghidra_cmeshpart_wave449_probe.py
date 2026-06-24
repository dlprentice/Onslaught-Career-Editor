#!/usr/bin/env python3
"""Validate Wave449 CMeshPart load/optimize metadata hardening."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave449-cmeshpart-load-optimize-current"
COMMON_TAGS = {"static-reaudit", "cmeshpart-wave449", "retail-binary-evidence"}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 8,
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
    "0x004af470": target(
        "CMeshPart__LoadVerticesAndTriangles",
        "void __thiscall CMeshPart__LoadVerticesAndTriangles(void * this, void * mem_buffer, void * part_table_entry, void * first_part_record, int part_index_limit, int unused_legacy_arg)",
        ["ret 0x14", "five stack arguments", "part_index_limit", "unused_legacy_arg", "rebuild parity remain unproven"],
        ["meshpart", "mesh-load", "vertices", "triangles", "signature-corrected", "comment-hardened"],
        ["mem_buffer", "part_index_limit", "CMeshPart__RebuildPerVertexNormalsAndTangents"],
    ),
    "0x004afbb0": target(
        "CMeshPart__LoadVerticesWithBones",
        "void __thiscall CMeshPart__LoadVerticesWithBones(void * this, void * mem_buffer, void * parent_mesh, int unused_arg3, int part_index_limit, int unused_arg5, int influence_count, int format_tag)",
        ["ret 0x1c", "seven stack arguments", "influence_count", "format_tag", "rebuild parity remain unproven"],
        ["meshpart", "mesh-load", "skinned", "bones", "signature-corrected", "comment-hardened"],
        ["parent_mesh", "influence_count", "format_tag", "CMeshPart__RebuildPerVertexNormalsAndTangents"],
    ),
    "0x004b25d0": target(
        "CMesh__GetRandomVertexFromPolyBucket",
        "void __thiscall CMesh__GetRandomVertexFromPolyBucket(void * this, void * out_vec4)",
        ["out_vec4", "CPolyBucket__GetRandomTriangle", "Ret 0x4", "phantom third argument", "rebuild parity remain unproven"],
        ["mesh", "meshpart", "polybucket", "random-vertex", "signature-corrected", "comment-hardened"],
        ["out_vec4", "CPolyBucket__GetRandomTriangle", "Random__NextLCGAbs"],
    ),
    "0x004b27a0": target(
        "CMeshPart__LoadFromStream",
        "void * __cdecl CMeshPart__LoadFromStream(void * chunk_reader, void * mesh_part, void * parent_mesh)",
        ["0x13c CMeshPart", "CMeshPart__LoadMaterial", "CPolyBucket__Load", "rebuild parity remain unproven"],
        ["meshpart", "deserialize", "chunk-reader", "signature-corrected", "comment-hardened"],
        ["chunk_reader", "mesh_part", "parent_mesh", "CMeshPart__LoadMaterial"],
    ),
    "0x004b3180": target(
        "CMeshPart__LoadMaterial",
        "void * __cdecl CMeshPart__LoadMaterial(void * chunk_reader, void * existing_material)",
        ["0x28-byte material", "+0x20/+0x24", "rebuild parity remain unproven"],
        ["meshpart", "material", "chunk-reader", "signature-corrected", "comment-hardened"],
        ["existing_material", "OID__AllocObject(0x28", "CChunkReader__Read"],
    ),
    "0x004b31f0": target(
        "CMeshPart__OptimizePolygons",
        "void __fastcall CMeshPart__OptimizePolygons(void * this)",
        ["PVertex count at +0xac", "0.2 threshold", "0.3 above 300", "rebuild parity remain unproven"],
        ["meshpart", "optimize", "polygons", "signature-corrected", "comment-hardened"],
        ["CMeshPart__OptimizePolygons", "0.2", "0.3", "OID__AllocObject"],
    ),
    "0x004b3b70": target(
        "CMeshPart__Clone",
        "void * __fastcall CMeshPart__Clone(void * this)",
        ["0x13c bytes", "CMeshPart__Init", "deep-clones", "rebuild parity remain unproven"],
        ["meshpart", "clone", "deep-copy", "signature-corrected", "comment-hardened"],
        ["CMeshPart__Clone", "CMeshPart__Init", "OID__AllocObject(0x13c"],
    ),
    "0x004b4250": target(
        "CMeshPart__Merge",
        "void __thiscall CMeshPart__Merge(void * this, void * source_part)",
        ["source_part", "CMCMech__BuildInterpolatedPoseAndAnchor", "Ret 0x4", "rebuild parity remain unproven"],
        ["meshpart", "merge", "geometry", "signature-corrected", "comment-hardened"],
        ["source_part", "CMCMech__BuildInterpolatedPoseAndAnchor", "MathMatrix3x3__Determinant"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004af470", "CMesh__Load"),
    ("0x004afbb0", "CMesh__Load"),
    ("0x004b25d0", "CMesh__GetRandomVertexWeightedByPartArea"),
    ("0x004b27a0", "CMesh__Deserialize"),
    ("0x004b3180", "CMesh__Deserialize"),
    ("0x004b3180", "CMeshPart__LoadFromStream"),
    ("0x004b31f0", "CMeshPart__CreatePolyBucket"),
    ("0x004b3b70", "CMeshPart__CreatePolyBucket"),
    ("0x004b4250", "CMesh__OptimizeParts"),
]

INSTRUCTION_TOKENS = {
    "0x004af470": ["CMeshPart__LoadVerticesAndTriangles\tRET\t0x14"],
    "0x004afbb0": ["CMeshPart__LoadVerticesWithBones\tRET\t0x1c"],
    "0x004b25d0": ["CMesh__GetRandomVertexFromPolyBucket\tRET\t0x4"],
    "0x004b27a0": ["CMeshPart__LoadFromStream\tRET"],
    "0x004b3180": ["CMeshPart__LoadMaterial\tRET"],
    "0x004b31f0": ["CMeshPart__OptimizePolygons\tRET"],
    "0x004b3b70": ["CMeshPart__Clone\tRET"],
    "0x004b4250": ["CMeshPart__Merge\tRET\t0x4"],
}

CALLSITE_TOKENS = [
    "0x004a8f5c\t0x004a8f5c\tBEFORE\t-25\t0x004a8f1f\t0x004a5b70\tCMesh__Load\tPUSH\t0x0",
    "0x004a8f5c\t0x004a8f5c\tTARGET\t0\t0x004a8f5c\t0x004a5b70\tCMesh__Load\tCALL\t0x004af470",
    "0x004a841d\t0x004a841d\tBEFORE\t-9\t0x004a8411\t0x004a5b70\tCMesh__Load\tPUSH\tEAX",
    "0x004a841d\t0x004a841d\tTARGET\t0\t0x004a841d\t0x004a5b70\tCMesh__Load\tCALL\t0x004afbb0",
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
        "updated": 8,
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
            if token not in comment:
                failures.append(f"{address}: missing comment token {token!r}")
        lowered = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: overclaim token in comment {token!r}")
        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
            continue
        actual_tags = {tag.strip() for tag in re.split(r"[;,]", tag_row.get("tags", "")) if tag.strip()}
        missing_tags = set(spec["tags"]) - actual_tags  # type: ignore[arg-type]
        if missing_tags:
            failures.append(f"{address}: missing tags {sorted(missing_tags)}")


def check_decompiles(base: Path, failures: list[str]) -> None:
    for address, spec in TARGETS.items():
        text = decompile_text_for(base, address)
        if not text:
            failures.append(f"{address}: missing post-decomp text")
            continue
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(text, str(token)):
                failures.append(f"{address}: missing decompile token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    if len(rows) < len(EXPECTED_XREF_EDGES):
        failures.append(f"post_xrefs.tsv: expected at least {len(EXPECTED_XREF_EDGES)} rows, got {len(rows)}")
    found = {(row.get("target_addr", ""), row.get("from_function", "")) for row in rows}
    for edge in EXPECTED_XREF_EDGES:
        if edge not in found:
            failures.append(f"post_xrefs.tsv: missing edge {edge}")


def check_instruction_tokens(base: Path, failures: list[str]) -> None:
    text = read_text(base / "post_instructions_xwide.tsv") or read_text(base / "post_instructions_wide.tsv")
    if not text:
        failures.append("post_instructions_xwide.tsv/post_instructions_wide.tsv: missing instruction export")
        return
    for address, tokens in INSTRUCTION_TOKENS.items():
        for token in tokens:
            if not token_present(text, token):
                failures.append(f"{address}: missing instruction token {token!r}")


def check_callsite_tokens(base: Path, failures: list[str]) -> None:
    text = read_text(base / "callsite_instructions.tsv")
    if not text:
        failures.append("callsite_instructions.tsv: missing callsite evidence")
        return
    for token in CALLSITE_TOKENS:
        if not token_present(text, token):
            failures.append(f"callsite_instructions.tsv: missing token {token!r}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_apply_log(base, failures)
    check_verify_log(base, failures)
    check_metadata(base, failures)
    check_decompiles(base, failures)
    check_xrefs(base, failures)
    check_instruction_tokens(base, failures)
    check_callsite_tokens(base, failures)
    return ("PASS" if not failures else "FAIL", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="Wave449 evidence directory")
    parser.add_argument("--check", action="store_true", help="Fail nonzero on validation failures")
    parser.add_argument("--json", type=Path, help="Optional JSON report path")
    args = parser.parse_args(argv)

    status, failures = run_checks(args.base)
    report = {
        "status": status,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "base": relative_or_absolute(args.base),
        "targetCount": len(TARGETS),
        "failures": failures,
    }

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Wave449 CMeshPart probe: {status}")
    print(f"Base: {relative_or_absolute(args.base)}")
    print(f"Targets: {len(TARGETS)}")
    for failure in failures:
        print(f"- {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
