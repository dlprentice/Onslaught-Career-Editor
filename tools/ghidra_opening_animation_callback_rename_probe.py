#!/usr/bin/env python3
"""Validate the saved 0x00418090 opening-animation callback rename."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "opening-animation-callback-rename" / "current"

ADDRESS = "0x00418090"
OLD_NAME = "FindAnimationIndex__Wrapper_00418090"
NEW_NAME = "OpeningAnimationStateCallback__StartOpeningIfPending"
TABLE_SLOT = "0x005d9080"

DEFAULT_RENAME_DRY = BASE / "rename_dry.log"
DEFAULT_RENAME_APPLY = BASE / "rename_apply.log"
DEFAULT_COMMENTS_DRY = BASE / "comments_dry.log"
DEFAULT_COMMENTS_APPLY = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_MIXED_TABLE = BASE / "table_005d8f80_160.tsv"
DEFAULT_UNRESOLVED_TYPES = BASE / "vtable_type_names.tsv"
DEFAULT_COCKPIT_TYPES = BASE / "ccockpit_vtable_type_names.tsv"
DEFAULT_COCKPIT_TABLE_A = BASE / "table_005d94ac_64.tsv"
DEFAULT_COCKPIT_TABLE_B = BASE / "table_005d9524_40.tsv"
DEFAULT_OUT = BASE / "opening-animation-callback-rename.json"

COMMENT_TOKENS = [
    "Opening-animation state callback semantic rename",
    "state field +0x254",
    "timer field +0x25c",
    "s_opening_00623ba4",
    "FindAnimationIndex call",
    "mixed table slot 0x005d9080",
    "table owner remains unresolved",
    "resolved CCockpit RTTI vtables",
    "runtime behavior remain unproven",
]
DECOMPILE_TOKENS = [
    NEW_NAME,
    "s_opening_00623ba4",
    "FindAnimationIndex",
    "+ 0x254",
    "+ 0x25c",
    "+ 0xf0",
]
OWNER_OVERCLAIM_TOKENS = [
    "owner is proven",
    "owner proven",
    "exact owner proven",
    "source identity proven",
    "runtime behavior proven",
]


def relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value in {"", "<none>", "<no_function>", "<no_instruction>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def has_token(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_metadata(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
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
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def contains_pointer(rows: list[dict[str, str]], ptr: str) -> bool:
    wanted = normalize_address(ptr)
    return any(normalize_address(row.get("ptr", "")) == wanted for row in rows)


def build_report(
    *,
    rename_dry_log_path: Path = DEFAULT_RENAME_DRY,
    rename_apply_log_path: Path = DEFAULT_RENAME_APPLY,
    comments_dry_log_path: Path = DEFAULT_COMMENTS_DRY,
    comments_apply_log_path: Path = DEFAULT_COMMENTS_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    mixed_table_path: Path = DEFAULT_MIXED_TABLE,
    unresolved_type_names_path: Path = DEFAULT_UNRESOLVED_TYPES,
    cockpit_type_names_path: Path = DEFAULT_COCKPIT_TYPES,
    cockpit_table_a_path: Path = DEFAULT_COCKPIT_TABLE_A,
    cockpit_table_b_path: Path = DEFAULT_COCKPIT_TABLE_B,
) -> dict[str, object]:
    rename_dry_log_path = resolve(rename_dry_log_path)
    rename_apply_log_path = resolve(rename_apply_log_path)
    comments_dry_log_path = resolve(comments_dry_log_path)
    comments_apply_log_path = resolve(comments_apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    mixed_table_path = resolve(mixed_table_path)
    unresolved_type_names_path = resolve(unresolved_type_names_path)
    cockpit_type_names_path = resolve(cockpit_type_names_path)
    cockpit_table_a_path = resolve(cockpit_table_a_path)
    cockpit_table_b_path = resolve(cockpit_table_b_path)

    failures: list[str] = []
    for label, path in (
        ("rename dry log", rename_dry_log_path),
        ("rename apply log", rename_apply_log_path),
        ("comment dry log", comments_dry_log_path),
        ("comment apply log", comments_apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("mixed pointer table", mixed_table_path),
        ("unresolved slot type output", unresolved_type_names_path),
        ("CCockpit type output", cockpit_type_names_path),
        ("CCockpit table 0x005d94ac", cockpit_table_a_path),
        ("CCockpit table 0x005d9524", cockpit_table_b_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    rename_dry = read_text(rename_dry_log_path)
    rename_apply = read_text(rename_apply_log_path)
    comments_dry = read_text(comments_dry_log_path)
    comments_apply = read_text(comments_apply_log_path)
    metadata_rows = read_metadata(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xrefs = read_tsv(xrefs_path)
    mixed_table = read_tsv(mixed_table_path)
    unresolved_types = read_tsv(unresolved_type_names_path)
    cockpit_types = read_tsv(cockpit_type_names_path)
    cockpit_table_a = read_tsv(cockpit_table_a_path)
    cockpit_table_b = read_tsv(cockpit_table_b_path)

    rename_dry_summary = parse_summary(rename_dry)
    rename_apply_summary = parse_summary(rename_apply)
    comments_dry_summary = parse_summary(comments_dry)
    comments_apply_summary = parse_summary(comments_apply)
    if rename_dry_summary != {"applied": 0, "skipped": 1, "missing": 0, "bad": 0}:
        failures.append("rename dry log summary is not clean")
    if rename_apply_summary != {"applied": 1, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("rename apply log summary is not clean")
    if comments_dry_summary != {"applied": 0, "skipped": 1, "missing": 0, "bad": 0}:
        failures.append("comment dry log summary is not clean")
    if comments_apply_summary != {"applied": 1, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("comment apply log summary is not clean")
    if f"{OLD_NAME} -> {NEW_NAME}" not in rename_dry or f"{OLD_NAME} -> {NEW_NAME}" not in rename_apply:
        failures.append("rename logs do not show the expected old-name to new-name transition")
    if f"DRY: {ADDRESS} {NEW_NAME}" not in comments_dry or f"OK: {ADDRESS} {NEW_NAME}" not in comments_apply:
        failures.append("comment logs do not guard against the post-rename target name")

    metadata_row = find_row(metadata_rows, "address", ADDRESS)
    comment = metadata_row.get("comment", "") if metadata_row else ""
    comment_tokens_present = all(token in comment for token in COMMENT_TOKENS)
    owner_boundary_present = "table owner remains unresolved" in comment and "runtime behavior remain unproven" in comment
    owner_overclaim_present = any(token in comment.lower() for token in OWNER_OVERCLAIM_TOKENS)
    if metadata_row is None:
        failures.append(f"metadata read-back missing {ADDRESS}")
        function = {"name": None, "status": None, "signature": None}
    else:
        function = {
            "name": metadata_row.get("name"),
            "status": metadata_row.get("status"),
            "signature": metadata_row.get("signature"),
        }
        if metadata_row.get("name") != NEW_NAME or metadata_row.get("status") != "OK":
            failures.append(f"metadata read-back for {ADDRESS} does not have expected saved name/status")
        if metadata_row.get("name") == OLD_NAME:
            failures.append(f"metadata read-back still has stale wrapper name {OLD_NAME}")
        if not comment_tokens_present:
            failures.append("metadata comment is missing required semantic-rename proof tokens")
        if not owner_boundary_present or owner_overclaim_present:
            failures.append("metadata comment does not preserve the unresolved owner boundary")

    index_row = find_row(index_rows, "address", ADDRESS)
    if index_row is None or index_row.get("name") != NEW_NAME or index_row.get("status") != "OK":
        failures.append("decompile index does not confirm the saved target name")
    decompile_file = find_decompile_file(decompile_dir, ADDRESS)
    decompile_text = read_text(decompile_file) if decompile_file else ""
    if decompile_file is None:
        failures.append(f"decompile read-back missing {ADDRESS}")
    missing_decompile_tokens = [token for token in DECOMPILE_TOKENS if not has_token(decompile_text, token)]
    if missing_decompile_tokens:
        failures.append(f"decompile read-back missing tokens: {', '.join(missing_decompile_tokens)}")
    if OLD_NAME in decompile_text:
        failures.append("decompile read-back still contains the stale wrapper name")

    xref_present = any(
        normalize_address(row.get("target_addr", "")) == ADDRESS
        and normalize_address(row.get("from_addr", "")) == TABLE_SLOT
        and row.get("ref_type") == "DATA"
        for row in xrefs
    )
    if not xref_present:
        failures.append(f"xref read-back does not show DATA xref from {TABLE_SLOT}")

    mixed_slot_present = any(
        normalize_address(row.get("entry_addr", "")) == TABLE_SLOT
        and normalize_address(row.get("ptr", "")) == ADDRESS
        and row.get("ptr_name") == NEW_NAME
        for row in mixed_table
    )
    front_end_marker = any(row.get("ptr_name") == "CFrontEndPage__ActiveNotification_NoOp" for row in mixed_table)
    byte_sprite_marker = any(row.get("ptr_name") == "CByteSprite__scalar_deleting_dtor" for row in mixed_table)
    adjacent_cockpit_state_helper = any(
        normalize_address(row.get("ptr", "")) == "0x00418120"
        and row.get("ptr_name") == "CCockpit__AdvanceOpenCloseAnimationState"
        for row in mixed_table
    )
    slot_owner_unresolved = any(
        normalize_address(row.get("vtable", "")) == TABLE_SLOT and not row.get("demangled_type_name", "").strip()
        for row in unresolved_types
    )
    if not mixed_slot_present:
        failures.append("mixed pointer table does not show the renamed 0x005d9080 slot")
    if not slot_owner_unresolved:
        failures.append("unresolved type output no longer records the 0x005d9080 owner as unresolved")

    cockpit_type_vtables = {normalize_address(row.get("vtable", "")) for row in cockpit_types if row.get("demangled_type_name") == "CCockpit"}
    resolved_cockpit_types_present = {"0x005d94ac", "0x005d9524"}.issubset(cockpit_type_vtables)
    target_absent_from_cockpit_tables = not contains_pointer(cockpit_table_a, ADDRESS) and not contains_pointer(cockpit_table_b, ADDRESS)
    if not resolved_cockpit_types_present:
        failures.append("resolved CCockpit RTTI vtable evidence is missing")
    if not target_absent_from_cockpit_tables:
        failures.append("0x00418090 unexpectedly appears in a resolved CCockpit table")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-opening-animation-callback-rename.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "classification": "opening-animation-callback-semantic-rename-owner-unresolved"
        if status == "PASS"
        else "opening-animation-callback-rename-blocked",
        "target": {
            "address": ADDRESS,
            "oldName": OLD_NAME,
            "name": function["name"],
            "expectedName": NEW_NAME,
            "signature": function["signature"],
        },
        "mutationLogs": {
            "renameDrySummary": rename_dry_summary,
            "renameApplySummary": rename_apply_summary,
            "commentsDrySummary": comments_dry_summary,
            "commentsApplySummary": comments_apply_summary,
        },
        "readback": {
            "metadataNamePresent": metadata_row is not None and metadata_row.get("name") == NEW_NAME,
            "commentTokensPresent": comment_tokens_present,
            "ownerBoundaryPresent": owner_boundary_present and not owner_overclaim_present,
            "decompileTokensPresent": not missing_decompile_tokens,
            "xrefPresent": xref_present,
        },
        "tableContext": {
            "mixedSlot": TABLE_SLOT,
            "mixedSlotPresent": mixed_slot_present,
            "frontEndMarkerPresent": front_end_marker,
            "byteSpriteMarkerPresent": byte_sprite_marker,
            "adjacentCockpitStateHelperPresent": adjacent_cockpit_state_helper,
            "slotOwnerUnresolved": slot_owner_unresolved,
        },
        "cockpitBoundary": {
            "resolvedCockpitTypesPresent": resolved_cockpit_types_present,
            "targetAbsentFromResolvedCockpitTables": target_absent_from_cockpit_tables,
        },
        "inputs": {
            "renameDryLog": relative(rename_dry_log_path),
            "renameApplyLog": relative(rename_apply_log_path),
            "commentsDryLog": relative(comments_dry_log_path),
            "commentsApplyLog": relative(comments_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "mixedTable": relative(mixed_table_path),
            "unresolvedTypeNames": relative(unresolved_type_names_path),
            "cockpitTypeNames": relative(cockpit_type_names_path),
            "cockpitTableA": relative(cockpit_table_a_path),
            "cockpitTableB": relative(cockpit_table_b_path),
        },
        "whatIsProven": [
            f"{ADDRESS} was renamed from {OLD_NAME} to {NEW_NAME} in saved Ghidra state.",
            "The function body starts the opening animation when state field +0x254 is pending state 3, using the opening token, FindAnimationIndex, animation-start vcall +0xf0, and timer field +0x25c.",
            "The only checked owner reference remains a mixed DATA table slot at 0x005d9080, while resolved CCockpit RTTI tables do not prove that slot.",
        ],
        "notProven": [
            "This does not prove exact table owner, class owner, source method identity, signature/types, tags, locals, or structure layout.",
            "This does not prove runtime opening-animation behavior.",
            "This does not certify adjacent historical CCockpit names as final.",
        ],
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit non-zero when the report fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="write JSON report")
    args = parser.parse_args(argv)

    report = build_report()
    out = resolve(args.out)
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("Ghidra opening-animation callback rename probe")
    print(f"Status: {report['status']}")
    print(f"Output: {relative(out)}")
    print(f"Target: {ADDRESS} {report['target']['oldName']} -> {report['target']['name']}")
    for failure in report["failures"]:
        print(f"- {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
