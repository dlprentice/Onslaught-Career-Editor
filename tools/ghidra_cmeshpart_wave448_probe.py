#!/usr/bin/env python3
"""Validate Wave448 CMeshPart transform/cache metadata hardening."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave448-cmeshpart-transform-cache-current"
COMMON_TAGS = {"static-reaudit", "cmeshpart-wave448", "retail-binary-evidence"}
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
    "0x004b0800": target(
        "CMeshPart__ApplyRootTransformRecursive",
        "void __thiscall CMeshPart__ApplyRootTransformRecursive(void * this, int parent_transform_dword00, int parent_transform_dword01, int parent_transform_dword02, int parent_transform_dword03, int parent_transform_dword04, int parent_transform_dword05, int parent_transform_dword06, int parent_transform_dword07, int parent_transform_dword08, int parent_transform_dword09, int parent_transform_dword10, int parent_transform_dword11, float origin_x, float origin_y, float origin_z, float origin_w, void * frame_override_part)",
        ["ret 0x44", "12-dword parent transform block", "frame-override part pointer", "rebuild parity remain unproven"],
        ["meshpart", "transform", "recursive", "stack-block-signature", "signature-corrected", "comment-hardened"],
        ["parent_transform_dword00", "origin_w", "frame_override_part", "CMeshPart__GetBasisX"],
    ),
    "0x004b0c00": target(
        "CMeshPart__GetBasisX",
        "void * __thiscall CMeshPart__GetBasisX(void * this, void * out_vec3)",
        ["+0x04", "+0x14", "+0x24", "ret 0x4", "rebuild parity remain unproven"],
        ["meshpart", "basis-vector", "signature-corrected", "comment-hardened"],
        ["out_vec3", "+ 0x24"],
    ),
    "0x004b0c20": target(
        "CMeshPart__GetBasisY",
        "void * __thiscall CMeshPart__GetBasisY(void * this, void * out_vec3)",
        ["+0x08", "+0x18", "+0x28", "ret 0x4", "rebuild parity remain unproven"],
        ["meshpart", "basis-vector", "signature-corrected", "comment-hardened"],
        ["out_vec3", "+ 0x28"],
    ),
    "0x004b0c40": target(
        "CMeshPart__FindNearestVertexIndex",
        "int __thiscall CMeshPart__FindNearestVertexIndex(void * this, float query_x, float query_y, float query_z, float query_w_unused)",
        ["first per-frame PVertex array", "+0xac vertices", "ret 0x10", "fourth stack float", "rebuild parity remain unproven"],
        ["meshpart", "vertex-search", "signature-corrected", "comment-hardened"],
        ["query_x", "query_y", "query_z", "99999.0"],
    ),
    "0x004b1a40": target(
        "CMeshPart__CacheFrameData",
        "void __fastcall CMeshPart__CacheFrameData(void * this)",
        ["cached frame count at +0x118", "+0x120/+0x11c", "CMCMech__BuildInterpolatedPoseAndAnchor", "rebuild parity remain unproven"],
        ["meshpart", "frame-cache", "allocation", "signature-corrected", "comment-hardened"],
        ["CMeshPart__CacheFrameData", "OID__AllocObject", "CMCMech__BuildInterpolatedPoseAndAnchor"],
    ),
    "0x004b1d30": target(
        "CMeshPart__LinkDamagedPartVariantsBySuffix",
        "void __fastcall CMeshPart__LinkDamagedPartVariantsBySuffix(void * this)",
        ["_damaged suffix", "optional decimal damage number", "+0x9c/+0xa0", "rebuild parity remain unproven"],
        ["meshpart", "damaged-variants", "suffix-scan", "signature-corrected", "comment-hardened"],
        ["s__damaged", "CSoundManager__ParseDecimalToken", "+ 0xa4"],
    ),
    "0x004b1eb0": target(
        "CMeshPart__RebuildPerVertexNormalsAndTangents",
        "void __thiscall CMeshPart__RebuildPerVertexNormalsAndTangents(void * this, int update_primary_normal)",
        ["10001-DVertex guard", "low byte of update_primary_normal", "fallback axis vectors", "rebuild parity remain unproven"],
        ["meshpart", "normals", "tangents", "signature-corrected", "comment-hardened"],
        ["update_primary_normal", "SQRT", "+ 0x134"],
    ),
    "0x004b24d0": target(
        "CMeshPart__ResolveWrappedFrameIndexAndLerp",
        "int __thiscall CMeshPart__ResolveWrappedFrameIndexAndLerp(void * this, float frame_delta, int frame_table_index, void * out_lerp, void * frame_adjuster)",
        ["frame_table_index and frame_delta", "frame_adjuster vfunc +0x14", "fractional lerp", "rebuild parity remain unproven"],
        ["meshpart", "frame-resolve", "animation", "signature-corrected", "comment-hardened"],
        ["frame_delta", "frame_table_index", "out_lerp", "frame_adjuster"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004b0800", "CMesh__Load"),
    ("0x004b0800", "CMeshPart__ApplyRootTransformRecursive"),
    ("0x004b0c00", "CMeshPart__ApplyRootTransformRecursive"),
    ("0x004b0c00", "CSoundManager__UpdateSoundPosition"),
    ("0x004b0c20", "CMeshPart__ApplyRootTransformRecursive"),
    ("0x004b0c40", "CMesh__Load"),
    ("0x004b1a40", "CMesh__Load"),
    ("0x004b1d30", "CMesh__Load"),
    ("0x004b1eb0", "CMeshPart__LoadVerticesAndTriangles"),
    ("0x004b1eb0", "CMeshPart__LoadVerticesWithBones"),
    ("0x004b24d0", "CMeshPart__EvaluatePoseTransformForFrame"),
    ("0x004b24d0", "PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300"),
]

INSTRUCTION_TOKENS = {
    "0x004b0800": ["CMeshPart__ApplyRootTransformRecursive\tRET\t0x44"],
    "0x004b0c00": ["CMeshPart__GetBasisX\tRET\t0x4"],
    "0x004b0c20": ["CMeshPart__GetBasisY\tRET\t0x4"],
    "0x004b0c40": ["CMeshPart__FindNearestVertexIndex\tRET\t0x10"],
    "0x004b1d30": ["CMeshPart__LinkDamagedPartVariantsBySuffix\tRET"],
    "0x004b1eb0": ["CMeshPart__RebuildPerVertexNormalsAndTangents\tRET\t0x4"],
    "0x004b24d0": ["CMeshPart__ResolveWrappedFrameIndexAndLerp\tRET\t0x10"],
}

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
    text = read_text(base / "post_instructions_wide.tsv") or read_text(base / "post_instructions.tsv")
    if not text:
        failures.append("post_instructions_wide.tsv/post_instructions.tsv: missing instruction export")
        return
    for address, tokens in INSTRUCTION_TOKENS.items():
        for token in tokens:
            if not token_present(text, token):
                failures.append(f"{address}: missing instruction token {token!r}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_apply_log(base, failures)
    check_verify_log(base, failures)
    check_metadata(base, failures)
    check_decompiles(base, failures)
    check_xrefs(base, failures)
    check_instruction_tokens(base, failures)
    return ("PASS" if not failures else "FAIL", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="Wave448 evidence directory")
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

    print(f"Wave448 CMeshPart probe: {status}")
    print(f"Base: {relative_or_absolute(args.base)}")
    print(f"Targets: {len(TARGETS)}")
    for failure in failures:
        print(f"- {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
