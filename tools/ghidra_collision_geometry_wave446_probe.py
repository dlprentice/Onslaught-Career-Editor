#!/usr/bin/env python3
"""Validate Wave446 collision/geometry Ghidra metadata corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave446-collision-geometry-current"
COMMON_TAGS = {"static-reaudit", "collision-geometry-wave446", "retail-binary-evidence"}
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
    "0x004262e0": target(
        "CMeshCollisionVolume__VFunc_05_004262e0",
        "int __thiscall CMeshCollisionVolume__VFunc_05_004262e0(void * this, void * query_arg0, void * query_arg1, void * delegate_object, void * query_arg3)",
        ["vtable slot 5", "0x005d95dc", "RET 0x10", "rebuild parity remain unproven"],
        ["mesh-collision-volume", "vtable-forwarder", "signature-corrected", "comment-hardened"],
        ["delegate_object", "query_arg3", "vtable slot 5"],
    ),
    "0x00426320": target(
        "CSphere__VFunc_01_00426320",
        "int __thiscall CSphere__VFunc_01_00426320(void * this, void * query_arg0, void * query_arg1, void * delegate_object, void * query_arg3)",
        ["0x005d95e8/0x005d95fc", "vtable slot +0x0c", "RET 0x10", "rebuild parity remain unproven"],
        ["sphere-collision", "vtable-forwarder", "signature-corrected", "comment-hardened"],
        ["delegate_object", "query_arg3", "CSphere__VFunc_01_00426320"],
    ),
    "0x00477ba0": target(
        "Vec3__MagnitudeSquared",
        "double __fastcall Vec3__MagnitudeSquared(void * this)",
        ["x*x + y*y + z*z", "Geometry__NoOpHook", "rebuild parity remain unproven"],
        ["vector-math", "magnitude-squared", "owner-corrected", "renamed", "signature-corrected", "comment-hardened"],
        ["Vec3__MagnitudeSquared", "return (double)", "*(float *)((int)this + 8)"],
    ),
    "0x00478160": target(
        "Geometry__ClipSegmentAgainstAABB3D",
        "int __cdecl Geometry__ClipSegmentAgainstAABB3D(float * start_x, float * start_y, float * start_z, float * end_x, float * end_y, float * end_z, float * bounds_minmax)",
        ["six scalar pointers", "minX, minY, maxX, maxY, minZ, maxZ", "rebuild parity remain unproven"],
        ["geometry", "aabb-clip", "signature-corrected", "comment-hardened"],
        ["bounds_minmax", "start_x", "end_z"],
    ),
    "0x00478510": target(
        "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
        "int __cdecl CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore(void * triangle_vertex0, void * triangle_vertex1, void * triangle_vertex2, void * sphere_start, void * sweep_delta, float sphere_radius, void * contact_record)",
        ["swept sphere", "Vec3__MagnitudeSquared", "contact point", "rebuild parity remain unproven"],
        ["mesh-collision-volume", "swept-sphere", "triangle", "signature-corrected", "comment-hardened"],
        ["Vec3__MagnitudeSquared(sweep_delta)", "Geometry__RaySphereEntryDistance", "contact_record + 0xc4"],
    ),
    "0x00478c20": target(
        "Geometry__IntersectSegmentTriangleAndStoreHit",
        "int __cdecl Geometry__IntersectSegmentTriangleAndStoreHit(void * triangle_vertex0, void * triangle_vertex1, void * triangle_vertex2, void * segment_start, void * segment_end, void * contact_record)",
        ["segment time in [0,1]", "edge-side tests", "contact record", "rebuild parity remain unproven"],
        ["geometry", "segment-triangle", "contact-record", "signature-corrected", "comment-hardened"],
        ["contact_record", "segment_start", "Vec3__Dot"],
    ),
    "0x004ac6e0": target(
        "CMeshCollisionVolume__VFunc_03_004ac6e0",
        "int __thiscall CMeshCollisionVolume__VFunc_03_004ac6e0(void * this, void * query_arg0, float * motion_record, void * query_arg2, void * contact_record)",
        ["function-boundary recovery", "vtable slot 3", "0x005d95d4", "rebuild parity remain unproven"],
        ["mesh-collision-volume", "function-boundary-recovered", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["CMeshCollisionVolume__TestSweptSphereAgainstBounds", "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart", "motion_record"],
    ),
    "0x004ad830": target(
        "CMeshCollisionVolume__VFunc_04_004ad830",
        "int __thiscall CMeshCollisionVolume__VFunc_04_004ad830(void * this, void * query_arg0, void * state_record, void * segment_offsets, void * contact_record)",
        ["function-boundary recovery", "vtable slot 4", "0x005d95d8", "rebuild parity remain unproven"],
        ["mesh-collision-volume", "function-boundary-recovered", "vtable-slot", "segment-triangle", "signature-corrected", "comment-hardened"],
        ["CMeshPart__StartLineTriangleBucketSearch", "Geometry__IntersectSegmentTriangleAndStoreHit", "segment_offsets"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004262e0", "<no_function>"),
    ("0x00426320", "<no_function>"),
    ("0x00477ba0", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore"),
    ("0x00478160", "CMapWho__GetFirstEntryWithinLine"),
    ("0x00478160", "CPolyBucket__StartLineSearch"),
    ("0x00478510", "CMeshCollisionVolume__TestSweptSphereAgainstBounds"),
    ("0x00478510", "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart"),
    ("0x00478c20", "CMeshCollisionVolume__VFunc_04_004ad830"),
    ("0x004ac6e0", "<no_function>"),
    ("0x004ad830", "<no_function>"),
]

FORBIDDEN_DECOMPILE_TOKENS = {
    "0x00478510": ["Geometry__NoOpHook", "extraout_ST0"],
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


def check_create_outputs(base: Path, failures: list[str]) -> None:
    dry = read_tsv(base / "create_functions_dry.tsv")
    applied = read_tsv(base / "create_functions_apply.tsv")
    if [row.get("status") for row in dry] != ["would_create", "would_create"]:
        failures.append("create_functions_dry.tsv: expected two would_create rows")
    if [row.get("status") for row in applied] != ["created", "created"]:
        failures.append("create_functions_apply.tsv: expected two created rows")
    for address in ("0x004ac6e0", "0x004ad830"):
        row = row_by_address(applied, address)
        if row is None:
            failures.append(f"create_functions_apply.tsv: missing {address}")


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


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")
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
        for token in FORBIDDEN_DECOMPILE_TOKENS.get(address, []):
            if token_present(decompile, token):
                failures.append(f"{address}: forbidden decompile token still present {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    if len(rows) < len(TARGETS):
        failures.append(f"post_xrefs.tsv: expected at least {len(TARGETS)} rows, got {len(rows)}")
    for target_addr, from_name in EXPECTED_XREF_EDGES:
        wanted = normalize_address(target_addr)
        if not any(row.get("target_addr") == wanted and row.get("from_function") == from_name for row in rows):
            failures.append(f"post_xrefs.tsv: missing edge {wanted} <- {from_name}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    if not base.is_dir():
        failures.append(f"base directory missing: {relative_or_absolute(base)}")
        return "FAIL", failures
    check_create_outputs(base, failures)
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
        "schema": "ghidra-collision-geometry-wave446-probe.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "base": relative_or_absolute(base),
        "targets": len(TARGETS),
        "failures": failures,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Wave446 collision/geometry probe: {status}")
        print(f"Base: {relative_or_absolute(base)}")
        print(f"Targets: {len(TARGETS)}")
        for failure in failures:
            print(f"- {failure}")
    if args.check and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
