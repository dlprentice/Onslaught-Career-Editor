#!/usr/bin/env python3
"""Validate Wave452 render/sort static metadata hardening."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave452-render-sort-current"
COMMON_TAGS = {"static-reaudit", "render-sort-wave452", "retail-binary-evidence"}
EXPECTED_APPLY = {
    "updated": 8,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
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
    "0x004b5250": target(
        "CDXEngine__NormalizeCycleScalar",
        "float __cdecl CDXEngine__NormalizeCycleScalar(float cycle_scalar)",
        ["x87 scalar", "wrapping against", "0x005d8568", "consume ST0", "rebuild parity remain unproven"],
        ["render-sort", "x87-return", "signature-corrected", "comment-hardened"],
        ["CDXEngine__NormalizeCycleScalar", "_DAT_005d8568", "_DAT_005d856c"],
    ),
    "0x004b52a0": target(
        "Math__AbsDoubleFromSignedFloat",
        "float __cdecl Math__AbsDoubleFromSignedFloat(float value)",
        ["absolute-value", "x87 scalar", "FCHS", "leaving ST0 live", "rebuild parity remain unproven"],
        ["math", "x87-return", "signature-corrected", "comment-hardened"],
        ["Math__AbsDoubleFromSignedFloat", "_DAT_005d856c"],
    ),
    "0x004b52c0": target(
        "CDXEngine__PackVec3AndDepthToSortKey",
        "int __cdecl CDXEngine__PackVec3AndDepthToSortKey(void * position_vec3, float depth_scalar)",
        ["32-bit render sort key", "position_vec3", "depth_scalar", "three vec3 lanes", "rebuild parity remain unproven"],
        ["render-sort", "sort-key", "signature-corrected", "comment-hardened"],
        ["ROUND", "position_vec3", "depth_scalar", "_DAT_005dbc4c"],
    ),
    "0x004b5330": target(
        "CMeshPart__EvaluateAnimatedTransformCore",
        "int CMeshPart__EvaluateAnimatedTransformCore(void)",
        ["comment/tag hardening only", "animation-frame interpolation", "CMCMech__BuildInterpolatedPoseAndAnchor", "signature is intentionally deferred", "rebuild parity remain unproven"],
        ["meshpart", "animation", "transform", "signature-deferred", "comment-hardened"],
        ["CMeshPart__EvaluateAnimatedTransformCore", "CMCMech__BuildInterpolatedPoseAndAnchor"],
    ),
    "0x004b5ad0": target(
        "CMeshPart__RenderAnimatedRecursive",
        "int CMeshPart__RenderAnimatedRecursive(void)",
        ["comment/tag hardening only", "recursive mesh-part render", "CMeshPart__EvaluateAnimatedTransformCore", "CMeshRenderer__RenderMesh", "signature is intentionally deferred"],
        ["meshpart", "render", "recursive", "signature-deferred", "comment-hardened"],
        ["CMeshPart__EvaluateAnimatedTransformCore", "CMeshRenderer__RenderMesh", "CMeshPart__RenderAnimatedRecursive"],
    ),
    "0x004b5e80": target(
        "CSphere__RenderPartsWithOrientation",
        "int CSphere__RenderPartsWithOrientation(void)",
        ["comment/tag hardening only", "orientation transform", "sphere mesh-part table", "CMeshRenderer__RenderMesh", "signature is intentionally deferred"],
        ["sphere", "render", "orientation", "signature-deferred", "comment-hardened"],
        ["CSphere__RenderPartsWithOrientation", "CMeshRenderer__RenderMesh"],
    ),
    "0x004b6260": target(
        "CSphere__RenderAnimatedRecursive",
        "int CSphere__RenderAnimatedRecursive(void)",
        ["comment/tag hardening only", "cached-pose", "CSphere__RenderPartsWithOrientation", "CMeshPart__RenderAnimatedRecursive", "signature is intentionally deferred"],
        ["sphere", "render", "recursive", "signature-deferred", "comment-hardened"],
        ["CMeshPart__RefreshCachedPoseIfStale", "CSphere__RenderPartsWithOrientation", "CMeshPart__RenderAnimatedRecursive"],
    ),
    "0x004b6350": target(
        "CMeshRenderer__RenderMesh",
        "void __cdecl CMeshRenderer__RenderMesh(void * world_position_vec4, void * transform_matrix12, void * mesh_part, void * render_context, void * effect_owner, int render_slot_or_mode, byte render_flags)",
        ["top-level mesh render dispatcher", "seven observed stack arguments", "particle/effect setup", "debug volume overlays", "rebuild parity remain unproven"],
        ["mesh-renderer", "render", "particle-effects", "debug-overlay", "signature-corrected", "comment-hardened"],
        ["CMeshRenderer__RenderMeshCore", "CParticleManager__CreateEffect", "CThing__RenderDebugVolumeOverlay", "CDXEngine__SetWorldMatrixElements"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004b5250", "CHudComponent__RenderPassEntry"),
    ("0x004b52a0", "CHudComponent__RenderPassEntry"),
    ("0x004b52c0", "CDXEngine__BuildDirectionalSampleRing"),
    ("0x004b52c0", "CMeshRenderer__RenderMeshCore"),
    ("0x004b5330", "CMeshPart__PopulatePoseCacheRecursive"),
    ("0x004b5330", "CMeshPart__RenderAnimatedRecursive"),
    ("0x004b5ad0", "CSphere__RenderAnimatedRecursive"),
    ("0x004b5ad0", "CMeshPart__RenderAnimatedRecursive"),
    ("0x004b5e80", "CSphere__RenderAnimatedRecursive"),
    ("0x004b6260", "CHud__RenderTargetIndicatorOverlay"),
    ("0x004b6350", "CMeshPart__RenderAnimatedRecursive"),
    ("0x004b6350", "CSphere__RenderPartsWithOrientation"),
]

INSTRUCTION_TOKENS = {
    "0x004b5250": ["CDXEngine__NormalizeCycleScalar\tRET"],
    "0x004b52a0": ["Math__AbsDoubleFromSignedFloat\tFCHS", "Math__AbsDoubleFromSignedFloat\tRET"],
    "0x004b52c0": ["CDXEngine__PackVec3AndDepthToSortKey\tRET"],
    "0x004b5330": ["CMeshPart__EvaluateAnimatedTransformCore\tRET"],
    "0x004b5ad0": ["CMeshPart__RenderAnimatedRecursive\tRET"],
    "0x004b5e80": ["CSphere__RenderPartsWithOrientation\tRET"],
    "0x004b6260": ["CSphere__RenderAnimatedRecursive\tRET"],
    "0x004b6350": ["CMeshRenderer__RenderMesh\tRET"],
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry"):
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


def check_log(base: Path, filename: str, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(base / filename)
    if not text:
        failures.append(f"{filename}: missing or empty")
        return
    summary = parse_summary(text)
    if summary != expected:
        failures.append(f"{filename}: summary mismatch expected {expected}, got {summary}")
    for token in ("FAIL:", "Exception", "LockException"):
        if token in text:
            failures.append(f"{filename}: unexpected failure token {token!r}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{filename}: missing Ghidra save-success marker")


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
    text = read_text(base / "post_instructions_full.tsv") or read_text(base / "pre_instructions_full.tsv")
    if not text:
        failures.append("post_instructions_full.tsv/pre_instructions_full.tsv: missing instruction export")
        return
    for address, tokens in INSTRUCTION_TOKENS.items():
        for token in tokens:
            if not token_present(text, token):
                failures.append(f"{address}: missing instruction token {token!r}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_log(base, "apply.log", EXPECTED_APPLY, failures)
    check_log(base, "apply_verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_decompiles(base, failures)
    check_xrefs(base, failures)
    check_instruction_tokens(base, failures)
    return ("PASS" if not failures else "FAIL", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="Wave452 evidence directory")
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

    print(f"Wave452 render/sort probe: {status}")
    print(f"Base: {relative_or_absolute(args.base)}")
    print(f"Targets: {len(TARGETS)}")
    for failure in failures:
        print(f"- {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
