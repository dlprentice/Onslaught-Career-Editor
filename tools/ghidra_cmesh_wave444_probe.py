#!/usr/bin/env python3
"""Validate Wave444 CMesh / CMeshPart Ghidra metadata corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave444-cmesh-tail-current"

COMMON_TAGS = {"static-reaudit", "cmesh-wave444", "retail-binary-evidence"}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 11,
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
    "0x004aa3f0": target(
        "CMeshPart__CopyPrimaryAxesToOutVec3Triplet",
        "void __thiscall CMeshPart__CopyPrimaryAxesToOutVec3Triplet(void * this, void * out_vec3)",
        ["RET 0x4", "+0x00, +0x10, and +0x20", "rebuild parity remain unproven"],
        ["cmeshpart", "transform", "vector-copy", "signature-corrected", "comment-hardened"],
        ["out_vec3", "+ 0x20"],
    ),
    "0x004aa410": target(
        "CMesh__FindTextureByNameSuffixHint",
        "void * __cdecl CMesh__FindTextureByNameSuffixHint(void * texture_record)",
        ["warns on null texture names", "CTexture__FindTexture", "rebuild parity remain unproven"],
        ["cmesh", "texture-lookup", "signature-corrected", "comment-hardened"],
        ["CTexture__FindTexture", "s_Warning__Mesh_contains_a_null_te"],
    ),
    "0x004aa5a0": target(
        "CMesh__GetPartField40ByFlatIndex",
        "int __thiscall CMesh__GetPartField40ByFlatIndex(void * this, int flat_part_index)",
        ["part count at +0x1c", "field +0x40", "rebuild parity remain unproven"],
        ["cmesh", "part-lookup", "signature-corrected", "comment-hardened"],
        ["flat_part_index", "+ 0x40"],
    ),
    "0x004aa5e0": target(
        "CMesh__FindEntryByInclusiveRangeTable",
        "int __thiscall CMesh__FindEntryByInclusiveRangeTable(void * this, int lookup_value)",
        ["inclusive start/end range", "RET 0x4", "rebuild parity remain unproven"],
        ["cmesh", "range-table", "signature-corrected", "comment-hardened"],
        ["lookup_value", "piVar1[-1]"],
    ),
    "0x004aa630": target(
        "CMesh__FindAnimationIndexByName",
        "int __thiscall CMesh__FindAnimationIndexByName(void * this, char * animation_name)",
        ["animation/state table lookup", "returns record+0x10 or -1", "rebuild parity remain unproven"],
        ["cmesh", "animation-lookup", "renamed", "signature-corrected", "comment-hardened"],
        ["animation_name", "stricmp", "return -1"],
    ),
    "0x004aa680": target(
        "CMesh__FindEntryByPartId",
        "void * __thiscall CMesh__FindEntryByPartId(void * this, int part_id)",
        ["not CMCMech-specific", "returns the first record", "rebuild parity remain unproven"],
        ["cmesh", "part-lookup", "owner-corrected", "renamed", "signature-corrected", "comment-hardened"],
        ["part_id", "+ 0x10"],
    ),
    "0x004aa6e0": target(
        "CMesh__FindOrCreate",
        "void * __cdecl CMesh__FindOrCreate(char * mesh_name, void * load_context)",
        ["DAT_00704ad8/g_pMeshList", "+0x170", "rebuild parity remain unproven"],
        ["cmesh", "cache", "load-wrapper", "signature-corrected", "comment-hardened"],
        ["mesh_name", "CMesh__LoadByNameWithStatus", "DAT_00704ad8"],
    ),
    "0x004aa7e0": target(
        "CMesh__FindEntryValueByTypeId",
        "float __thiscall CMesh__FindEntryValueByTypeId(void * this, int type_id, int * out_index)",
        ["writes the matching record index", "returns the default float", "rebuild parity remain unproven"],
        ["cmesh", "entry-lookup", "float-return", "signature-corrected", "comment-hardened"],
        ["out_index", "_DAT_005d856c", "+ 0x20"],
    ),
    "0x004aa820": target(
        "CMesh__FindPartField40ByNameAndOwner",
        "int __thiscall CMesh__FindPartField40ByNameAndOwner(void * this, char * part_name, void * owner_part)",
        ["not CMCMech-specific", "record+0x4c", "record+0x14c", "rebuild parity remain unproven"],
        ["cmesh", "part-lookup", "owner-corrected", "renamed", "signature-corrected", "comment-hardened"],
        ["part_name", "owner_part", "+ 0x14c"],
    ),
    "0x004aa900": target(
        "CMesh__CreatePolyBucketsForAllParts",
        "void __thiscall CMesh__CreatePolyBucketsForAllParts(void * this)",
        ["part pointer table at +0x160", "CMeshPart__CreatePolyBucket", "rebuild parity remain unproven"],
        ["cmesh", "polybucket", "signature-corrected", "comment-hardened"],
        ["CMeshPart__CreatePolyBucket", "+ 0x160"],
    ),
    "0x004aa940": target(
        "CMesh__GetRandomVertexWeightedByPartArea",
        "void * __thiscall CMesh__GetRandomVertexWeightedByPartArea(void * this, void * out_vec3, void * out_part)",
        ["RET 0x8", "Random__NextLCGAbs", "rebuild parity remain unproven"],
        ["cmesh", "random-vertex", "polybucket", "signature-corrected", "comment-hardened"],
        ["Random__NextLCGAbs", "CMesh__GetRandomVertexFromPolyBucket", "s_WARNING__trying_to_get_random_ve"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004aa3f0", "CMesh__Load"),
    ("0x004aa410", "CMesh__Load"),
    ("0x004aa5a0", "CRTMesh__Init"),
    ("0x004aa630", "CMeshPart__HasWheelMotionAnimation"),
    ("0x004aa680", "CMCMech__Init"),
    ("0x004aa6e0", "CFrontEnd__LoadSharedResources"),
    ("0x004aa820", "CMCMech__Init"),
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

    check_verify_log(base, failures)
    check_metadata(base, failures)
    check_xrefs(base, failures)

    status = "PASS" if not failures else "FAIL"
    return status, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    base = args.base.resolve()
    status, failures = run_checks(base)
    result = {
        "schema": "ghidra-cmesh-wave444-probe.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "base": relative_or_absolute(base),
        "targets": len(TARGETS),
        "failures": failures,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Wave444 CMesh probe: {status}")
        print(f"Base: {relative_or_absolute(base)}")
        print(f"Targets: {len(TARGETS)}")
        for failure in failures:
            print(f"- {failure}")

    if args.check and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
