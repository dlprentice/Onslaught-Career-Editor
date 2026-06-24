#!/usr/bin/env python3
"""Verify the deferred 0x00410c50 Ghidra correction pass."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "deferred-00410c50" / "current"
DEFAULT_RENAME_DRY_LOG = BASE / "rename_dry.log"
DEFAULT_RENAME_APPLY_LOG = BASE / "rename_apply.log"
DEFAULT_COMMENTS_DRY_LOG = BASE / "comments_dry.log"
DEFAULT_COMMENTS_APPLY_LOG = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_after.tsv"
DEFAULT_XREFS = BASE / "xrefs_after.tsv"
DEFAULT_OUT = BASE / "deferred-00410c50-correction.json"

ADDRESS = "0x00410c50"
OLD_NAME = "OID_Unk_005078f0__Wrapper_00410c50"
NEW_NAME = "CMonitor__UpdateMovementTransitionAndEffects"

COMMENT_TOKENS = [
    "CMonitor__Process",
    "CMonitor__UpdateTrackedRenderPair",
    "CMonitor__IntegrateMovementAgainstTerrain",
    "CMonitor__ComputeTerrainVelocityScalar",
    "CMonitor__SpawnGroundOrAirImpactEffect",
    "CMonitor__ApplyHostileEnvironmentPenalty",
    "No dedicated Monitor source file",
    "signature and parameter names deferred",
]
OVERCLAIM_TOKENS = [
    "Source-exact Monitor method identity is now proven",
    "exact source method identity proven",
    "runtime behavior proven",
]
MOVEMENT_HELPER_XREFS = [
    ("0x005078f0", NEW_NAME),
    ("0x00411630", NEW_NAME),
    ("0x00411aa0", NEW_NAME),
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


def has_rename_line(log_text: str, prefix: str) -> bool:
    return f"{prefix}: {ADDRESS} {OLD_NAME} -> {NEW_NAME}" in log_text


def has_comment_line(log_text: str, prefix: str) -> bool:
    return f"{prefix}: {ADDRESS} {NEW_NAME}" in log_text


def find_row(rows: list[dict[str, str]], address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get("address", "")) == wanted:
            return row
    return None


def has_xref(rows: list[dict[str, str]], target: str, source_function: str) -> bool:
    wanted = normalize_address(target).removeprefix("0x")
    for row in rows:
        target_addr = row.get("target_addr", "").strip().lower().removeprefix("0x").zfill(8)
        if target_addr == wanted and row.get("from_function") == source_function:
            return True
    return False


def build_report(
    *,
    rename_dry_log_path: Path = DEFAULT_RENAME_DRY_LOG,
    rename_apply_log_path: Path = DEFAULT_RENAME_APPLY_LOG,
    comments_dry_log_path: Path = DEFAULT_COMMENTS_DRY_LOG,
    comments_apply_log_path: Path = DEFAULT_COMMENTS_APPLY_LOG,
    metadata_path: Path = DEFAULT_METADATA,
    xrefs_path: Path = DEFAULT_XREFS,
) -> dict[str, object]:
    rename_dry_log_path = resolve(rename_dry_log_path)
    rename_apply_log_path = resolve(rename_apply_log_path)
    comments_dry_log_path = resolve(comments_dry_log_path)
    comments_apply_log_path = resolve(comments_apply_log_path)
    metadata_path = resolve(metadata_path)
    xrefs_path = resolve(xrefs_path)

    failures: list[str] = []
    for label, path in (
        ("rename dry log", rename_dry_log_path),
        ("rename apply log", rename_apply_log_path),
        ("comment dry log", comments_dry_log_path),
        ("comment apply log", comments_apply_log_path),
        ("metadata read-back", metadata_path),
        ("xref read-back", xrefs_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    rename_dry_text = read_text(rename_dry_log_path)
    rename_apply_text = read_text(rename_apply_log_path)
    comments_dry_text = read_text(comments_dry_log_path)
    comments_apply_text = read_text(comments_apply_log_path)
    metadata_rows = read_metadata(metadata_path)
    xref_rows = read_tsv(xrefs_path)

    rename_dry_summary = parse_summary(rename_dry_text)
    rename_apply_summary = parse_summary(rename_apply_text)
    comments_dry_summary = parse_summary(comments_dry_text)
    comments_apply_summary = parse_summary(comments_apply_text)

    if rename_dry_summary != {"applied": 0, "skipped": 1, "missing": 0, "bad": 0}:
        failures.append("rename dry log summary is not the expected clean dry-run shape")
    if rename_apply_summary != {"applied": 1, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("rename apply log summary is not the expected clean apply shape")
    if comments_dry_summary != {"applied": 0, "skipped": 1, "missing": 0, "bad": 0}:
        failures.append("comment dry log summary is not the expected clean dry-run shape")
    if comments_apply_summary != {"applied": 1, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("comment apply log summary is not the expected clean apply shape")

    if not has_rename_line(rename_dry_text, "DRY"):
        failures.append(f"rename dry log missing expected target {ADDRESS} {OLD_NAME} -> {NEW_NAME}")
    if not has_rename_line(rename_apply_text, "OK"):
        failures.append(f"rename apply log missing expected target {ADDRESS} {OLD_NAME} -> {NEW_NAME}")
    if not has_comment_line(comments_dry_text, "DRY"):
        failures.append(f"comment dry log missing expected target {ADDRESS} {NEW_NAME}")
    if not has_comment_line(comments_apply_text, "OK"):
        failures.append(f"comment apply log missing expected target {ADDRESS} {NEW_NAME}")

    row = find_row(metadata_rows, ADDRESS)
    name_and_comment_present = False
    comment_tokens_present = False
    source_boundary_present = False
    if row is None:
        failures.append(f"metadata read-back missing {ADDRESS}")
        readback = {"name": None, "status": None, "signature": None, "commentTokensPresent": False}
    else:
        comment = row.get("comment", "")
        comment_tokens_present = all(token in comment for token in COMMENT_TOKENS)
        source_boundary_present = (
            "No dedicated Monitor source file" in comment
            and "signature and parameter names deferred" in comment
            and not any(token in comment for token in OVERCLAIM_TOKENS)
        )
        name_and_comment_present = row.get("name") == NEW_NAME and row.get("status") == "OK" and comment_tokens_present
        readback = {
            "name": row.get("name"),
            "status": row.get("status"),
            "signature": row.get("signature"),
            "commentTokensPresent": comment_tokens_present,
            "sourceBoundaryPresent": source_boundary_present,
        }
        if row.get("name") != NEW_NAME or row.get("status") != "OK" or not comment_tokens_present:
            failures.append(f"metadata read-back for {ADDRESS} lacks expected name/status/comment tokens")
        if not source_boundary_present:
            failures.append("metadata read-back comment is missing the source boundary or overclaims source identity")

    process_calls_target = has_xref(xref_rows, ADDRESS, "CMonitor__Process")
    target_calls_movement_helpers = all(has_xref(xref_rows, target, source) for target, source in MOVEMENT_HELPER_XREFS)
    if not process_calls_target:
        failures.append("xref read-back does not show CMonitor__Process calling the corrected target")
    if not target_calls_movement_helpers:
        failures.append("xref read-back does not show the corrected target calling the expected movement helpers")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-deferred-00410c50-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "deferred-monitor-body-renamed-commented-signature-deferred"
        if status == "PASS"
        else "deferred-monitor-body-correction-blocked",
        "target": {"address": ADDRESS, "oldName": OLD_NAME, "name": NEW_NAME},
        "rename": {"drySummary": rename_dry_summary, "applySummary": rename_apply_summary},
        "comments": {"drySummary": comments_dry_summary, "applySummary": comments_apply_summary},
        "readback": {
            "nameAndCommentPresent": name_and_comment_present,
            "commentTokensPresent": comment_tokens_present,
            "sourceBoundaryPresent": source_boundary_present,
            "function": readback,
        },
        "xrefs": {
            "rows": len(xref_rows),
            "processCallsTarget": process_calls_target,
            "targetCallsMovementHelpers": target_calls_movement_helpers,
        },
        "evidence": {
            "renameDryLog": relative(rename_dry_log_path),
            "renameApplyLog": relative(rename_apply_log_path),
            "commentsDryLog": relative(comments_dry_log_path),
            "commentsApplyLog": relative(comments_apply_log_path),
            "metadata": relative(metadata_path),
            "xrefs": relative(xrefs_path),
        },
        "notProven": [
            "Exact source method identity remains unproven because references/Onslaught has no dedicated Monitor source file.",
            "Function signature, parameter names, object field names, and type model remain deferred.",
            "This is saved Ghidra static evidence only; it does not prove runtime movement, transition, or effects behavior.",
        ],
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when the correction evidence is incomplete")
    parser.add_argument("--json", action="store_true", help="print the report JSON")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="write report JSON here")
    args = parser.parse_args()

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"{report['status']}: {report['candidateClassification']}")
        print(f"wrote {relative(out_path)}")
        for failure in report["failures"]:
            print(f"FAIL: {failure}")

    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
