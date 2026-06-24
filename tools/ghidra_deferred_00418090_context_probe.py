#!/usr/bin/env python3
"""Verify deferred 0x00418090 Ghidra context and saved comment evidence."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "deferred-00418090" / "current"
DEFAULT_COMMENTS_DRY_LOG = BASE / "comments_dry.log"
DEFAULT_COMMENTS_APPLY_LOG = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_DECOMPILE_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_TABLE = BASE / "table_005d9000_96.tsv"
DEFAULT_TYPE_NAMES = BASE / "vtable_type_names.tsv"
DEFAULT_TYPE_NAMES_9080 = BASE / "vtable_type_names_9080.tsv"
DEFAULT_DATA_XREFS = BASE / "data_xrefs.tsv"
DEFAULT_OUT = BASE / "deferred-00418090-context.json"

ADDRESS = "0x00418090"
NAME = "FindAnimationIndex__Wrapper_00418090"
COMMENT_TOKENS = [
    "Opening-animation state callback candidate",
    "state field +0x254",
    "timer field +0x25c",
    "s_opening_00623ba4",
    "FindAnimationIndex call",
    "mixed table slot 0x005d9080",
    "runtime behavior remain provisional",
]
DECOMPILE_TOKENS = [
    "s_opening_00623ba4",
    "FindAnimationIndex",
    "+ 0x254",
    "+ 0x25c",
    "+ 0xf0",
]
OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "exact source identity proven",
    "owner proven",
]


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if not value or value in {"<none>", "<no_function>"}:
        return value
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_metadata(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"applied=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"applied": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "applied": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
    }


def find_row(rows: list[dict[str, str]], address_key: str, address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(address_key, "")) == wanted:
            return row
    return None


def find_decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    needle = normalize_address(address)[2:]
    matches = sorted(decompile_dir.glob(f"{needle}_*.c"))
    return matches[0] if matches else None


def has_comment_log_line(log_text: str, prefix: str) -> bool:
    return f"{prefix}: {ADDRESS} {NAME}" in log_text


def table_row_matches(row: dict[str, str], *, entry_addr: str, ptr: str, ptr_name: str | None = None) -> bool:
    if normalize_address(row.get("entry_addr", "")) != normalize_address(entry_addr):
        return False
    if normalize_address(row.get("ptr", "")) != normalize_address(ptr):
        return False
    return ptr_name is None or row.get("ptr_name") == ptr_name


def build_report(
    *,
    comments_dry_log_path: Path = DEFAULT_COMMENTS_DRY_LOG,
    comments_apply_log_path: Path = DEFAULT_COMMENTS_APPLY_LOG,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_DECOMPILE_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    table_path: Path = DEFAULT_TABLE,
    type_names_path: Path = DEFAULT_TYPE_NAMES,
    type_names_9080_path: Path = DEFAULT_TYPE_NAMES_9080,
    data_xrefs_path: Path = DEFAULT_DATA_XREFS,
) -> dict[str, object]:
    comments_dry_log_path = resolve(comments_dry_log_path)
    comments_apply_log_path = resolve(comments_apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    table_path = resolve(table_path)
    type_names_path = resolve(type_names_path)
    type_names_9080_path = resolve(type_names_9080_path)
    data_xrefs_path = resolve(data_xrefs_path)

    failures: list[str] = []
    for label, path in (
        ("comment dry log", comments_dry_log_path),
        ("comment apply log", comments_apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("pointer table", table_path),
        ("type-name resolver output", type_names_path),
        ("slot type-name resolver output", type_names_9080_path),
        ("data xref output", data_xrefs_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    comments_dry_text = read_text(comments_dry_log_path)
    comments_apply_text = read_text(comments_apply_log_path)
    metadata_rows = read_metadata(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xrefs = read_tsv(xrefs_path)
    table_rows = read_tsv(table_path)
    type_rows = read_tsv(type_names_path)
    type_9080_rows = read_tsv(type_names_9080_path)
    data_xrefs = read_tsv(data_xrefs_path)

    dry_summary = parse_summary(comments_dry_text)
    apply_summary = parse_summary(comments_apply_text)
    if dry_summary != {"applied": 0, "skipped": 1, "missing": 0, "bad": 0}:
        failures.append("comment dry log summary is not the expected clean dry-run shape")
    if apply_summary != {"applied": 1, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("comment apply log summary is not the expected clean apply shape")
    if not has_comment_log_line(comments_dry_text, "DRY"):
        failures.append(f"comment dry log missing expected target {ADDRESS} {NAME}")
    if not has_comment_log_line(comments_apply_text, "OK"):
        failures.append(f"comment apply log missing expected target {ADDRESS} {NAME}")

    metadata_row = find_row(metadata_rows, "address", ADDRESS)
    index_row = find_row(index_rows, "address", ADDRESS)
    decompile_file = find_decompile_file(decompile_dir, ADDRESS)
    decompile_text = read_text(decompile_file) if decompile_file else ""

    comment_tokens_present = False
    comment_boundary_present = False
    if metadata_row is None:
        failures.append(f"metadata read-back missing {ADDRESS}")
        function_readback = {"name": None, "status": None, "signature": None}
    else:
        comment = metadata_row.get("comment", "")
        comment_tokens_present = all(token in comment for token in COMMENT_TOKENS)
        comment_boundary_present = (
            "Owner/table boundary" in comment
            and "runtime behavior remain provisional" in comment
            and not any(token in comment for token in OVERCLAIM_TOKENS)
        )
        if metadata_row.get("name") != NAME or metadata_row.get("status") != "OK" or not comment_tokens_present:
            failures.append(f"metadata read-back for {ADDRESS} lacks expected name/status/comment tokens")
        if not comment_boundary_present:
            failures.append("metadata read-back comment is missing the conservative owner/runtime boundary")
        function_readback = {
            "name": metadata_row.get("name"),
            "status": metadata_row.get("status"),
            "signature": metadata_row.get("signature"),
        }

    if index_row is None:
        failures.append(f"decompile index missing {ADDRESS}")
    elif index_row.get("name") != NAME or index_row.get("status") != "OK":
        failures.append(f"decompile index for {ADDRESS} lacks expected name/status")
    if decompile_file is None:
        failures.append(f"decompile read-back missing {ADDRESS}")
    decompile_tokens_present = all(token in decompile_text for token in DECOMPILE_TOKENS)
    if not decompile_tokens_present:
        failures.append(f"decompile read-back for {ADDRESS} lacks expected opening-animation tokens")

    expected_xref = any(
        normalize_address(row.get("target_addr", "")) == ADDRESS
        and normalize_address(row.get("from_addr", "")) == "0x005d9080"
        and row.get("ref_type") == "DATA"
        for row in xrefs
    )
    if not expected_xref:
        failures.append("xref read-back does not show DATA xref from mixed table slot 0x005d9080")

    slot_present = any(table_row_matches(row, entry_addr="0x005d9080", ptr=ADDRESS, ptr_name=NAME) for row in table_rows)
    front_end_marker = any(row.get("ptr_name") == "CFrontEndPage__ActiveNotification_NoOp" for row in table_rows)
    float_markers = {
        normalize_address(row.get("entry_addr", "")): row.get("ptr", "").lower()
        for row in table_rows
        if normalize_address(row.get("entry_addr", "")) in {"0x005d9088", "0x005d908c"}
    }
    byte_sprite_marker = any(row.get("ptr_name") == "CByteSprite__scalar_deleting_dtor" for row in table_rows)
    cbuilding_nearby = any(row.get("demangled_type_name") == "CBuildingNamedMesh" for row in type_rows)
    slot_owner_unresolved = any(
        normalize_address(row.get("vtable", "")) == "0x005d9080" and not row.get("demangled_type_name", "").strip()
        for row in type_9080_rows
    )
    mixed_region_present = (
        slot_present
        and front_end_marker
        and float_markers.get("0x005d9088") == "3d23d70a"
        and float_markers.get("0x005d908c") == "39a3d70a"
        and byte_sprite_marker
        and cbuilding_nearby
        and slot_owner_unresolved
    )
    if not slot_present:
        failures.append("pointer table output does not show 0x005d9080 pointing to 0x00418090")
    if not mixed_region_present:
        failures.append("pointer/type outputs do not preserve the mixed-table and unresolved-owner context")

    data_xref_functions = {row.get("from_function") for row in data_xrefs}
    data_context_present = {"CWarspite__Init", "OID__CreateObject"}.issubset(data_xref_functions)
    if not data_context_present:
        failures.append("data xref output lacks expected nearby mixed data/type context")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-deferred-00418090-context.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "deferred-opening-animation-context-commented-owner-unproven"
        if status == "PASS"
        else "deferred-opening-animation-context-blocked",
        "target": {"address": ADDRESS, "name": NAME},
        "comments": {"drySummary": dry_summary, "applySummary": apply_summary},
        "readback": {
            "nameAndCommentPresent": metadata_row is not None and metadata_row.get("name") == NAME and comment_tokens_present,
            "commentTokensPresent": comment_tokens_present,
            "commentBoundaryPresent": comment_boundary_present,
            "decompileTokensPresent": decompile_tokens_present,
            "function": function_readback,
        },
        "xrefs": {"rows": len(xrefs), "mixedTableSlotDataXrefPresent": expected_xref},
        "tableContext": {
            "rows": len(table_rows),
            "slotPresent": slot_present,
            "frontEndMarkerPresent": front_end_marker,
            "floatMarkersPresent": float_markers.get("0x005d9088") == "3d23d70a"
            and float_markers.get("0x005d908c") == "39a3d70a",
            "byteSpriteMarkerPresent": byte_sprite_marker,
            "nearbyCBuildingNamedMeshTypePresent": cbuilding_nearby,
            "slotOwnerUnresolved": slot_owner_unresolved,
            "mixedRegionPresent": mixed_region_present,
        },
        "evidence": {
            "commentsDryLog": relative(comments_dry_log_path),
            "commentsApplyLog": relative(comments_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "table": relative(table_path),
            "typeNames": relative(type_names_path),
            "typeNames9080": relative(type_names_9080_path),
            "dataXrefs": relative(data_xrefs_path),
        },
        "notProven": [
            "Exact owner/table boundary and source method identity remain unproven.",
            "The current saved name remains a weak wrapper-style label pending future rename/type/tag work.",
            "This is saved Ghidra static evidence only; it does not prove runtime animation or opening-state behavior.",
        ],
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return non-zero when the probe fails.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Write JSON report to this path.")
    args = parser.parse_args(argv)

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))

    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
