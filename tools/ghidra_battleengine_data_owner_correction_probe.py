#!/usr/bin/env python3
"""Verify the BattleEngineData owner-correction Ghidra pass."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "battleengine-data-owner-correction" / "current"
DEFAULT_RENAME_DRY_LOG = BASE / "rename_dry.log"
DEFAULT_RENAME_APPLY_LOG = BASE / "rename_apply.log"
DEFAULT_COMMENTS_DRY_LOG = BASE / "comments_dry.log"
DEFAULT_COMMENTS_APPLY_LOG = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_after.tsv"
DEFAULT_XREFS = BASE / "xrefs_after.tsv"
DEFAULT_OUT = BASE / "battleengine-data-owner-correction.json"

TARGETS = [
    {
        "address": "0x0040f590",
        "oldName": "CBattleEngineDataManager__Init",
        "name": "CBattleEngineData__Initialise",
        "commentTokens": [
            "CBattleEngineData::Initialise",
            "Standard",
            "Vulcan Cannon 1",
            "cockpit2.msh",
            "signature and parameter names deferred",
        ],
    },
    {
        "address": "0x0040f890",
        "oldName": "CBattleEngineDataManager__Clear",
        "name": "CBattleEngineData__Shutdown",
        "commentTokens": [
            "CBattleEngineData::Shutdown",
            "mConfigurationName",
            "mJetWeapons",
            "mWalkerWeapons",
            "signature and parameter names deferred",
        ],
    },
    {
        "address": "0x0040f980",
        "oldName": "CBattleEngineDataManager__Load",
        "name": "CBattleEngineData__LoadFromMemBuffer",
        "commentTokens": [
            "CBattleEngineData::Load(CMEMBUFFER&)",
            "CBattleEngineData__Shutdown",
            "DXMemBuffer__ReadBytes",
            "version fallback defaults",
            "signature and parameter names deferred",
        ],
    },
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


def has_rename_line(log_text: str, prefix: str, address: str, old_name: str, new_name: str) -> bool:
    return f"{prefix}: {address} {old_name} -> {new_name}" in log_text


def has_comment_line(log_text: str, prefix: str, address: str, name: str) -> bool:
    return f"{prefix}: {address} {name}" in log_text


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

    expected_count = len(TARGETS)
    rename_dry_summary = parse_summary(rename_dry_text)
    rename_apply_summary = parse_summary(rename_apply_text)
    comments_dry_summary = parse_summary(comments_dry_text)
    comments_apply_summary = parse_summary(comments_apply_text)

    if rename_dry_summary != {"applied": 0, "skipped": expected_count, "missing": 0, "bad": 0}:
        failures.append("rename dry log summary is not the expected clean dry-run shape")
    if rename_apply_summary != {"applied": expected_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("rename apply log summary is not the expected clean apply shape")
    if comments_dry_summary != {"applied": 0, "skipped": expected_count, "missing": 0, "bad": 0}:
        failures.append("comment dry log summary is not the expected clean dry-run shape")
    if comments_apply_summary != {"applied": expected_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("comment apply log summary is not the expected clean apply shape")

    readback: dict[str, object] = {}
    all_names_and_comments_present = True
    for target in TARGETS:
        address = target["address"]
        old_name = target["oldName"]
        name = target["name"]

        if not has_rename_line(rename_dry_text, "DRY", address, old_name, name):
            failures.append(f"rename dry log missing expected target {address} {old_name} -> {name}")
        if not has_rename_line(rename_apply_text, "OK", address, old_name, name):
            failures.append(f"rename apply log missing expected target {address} {old_name} -> {name}")
        if not has_comment_line(comments_dry_text, "DRY", address, name):
            failures.append(f"comment dry log missing expected target {address} {name}")
        if not has_comment_line(comments_apply_text, "OK", address, name):
            failures.append(f"comment apply log missing expected target {address} {name}")

        row = find_row(metadata_rows, address)
        if row is None:
            failures.append(f"metadata read-back missing {address}")
            readback[address] = {"name": None, "status": None, "commentTokensPresent": False}
            all_names_and_comments_present = False
            continue

        row_name = row.get("name", "")
        comment = row.get("comment", "")
        tokens_present = all(token in comment for token in target["commentTokens"])
        row_ok = row_name == name and row.get("status") == "OK" and tokens_present
        readback[address] = {
            "name": row_name,
            "status": row.get("status"),
            "signature": row.get("signature"),
            "commentTokensPresent": tokens_present,
        }
        if not row_ok:
            failures.append(f"metadata read-back for {address} lacks expected name/status/comment tokens")
            all_names_and_comments_present = False

    load_calls_shutdown = has_xref(xref_rows, "0x0040f890", "CBattleEngineData__LoadFromMemBuffer")
    reload_calls_initialise = has_xref(xref_rows, "0x0040f590", "CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData")
    reload_calls_load = has_xref(xref_rows, "0x0040f980", "CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData")
    if not load_calls_shutdown:
        failures.append("xref read-back does not show CBattleEngineData__LoadFromMemBuffer calling CBattleEngineData__Shutdown")
    if not reload_calls_initialise:
        failures.append("xref read-back does not show world-physics reload calling CBattleEngineData__Initialise")
    if not reload_calls_load:
        failures.append("xref read-back does not show world-physics reload calling CBattleEngineData__LoadFromMemBuffer")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-battleengine-data-owner-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "battleengine-data-owner-names-corrected"
        if status == "PASS"
        else "battleengine-data-owner-correction-blocked",
        "targetCount": expected_count,
        "targets": [
            {"address": target["address"], "oldName": target["oldName"], "name": target["name"]}
            for target in TARGETS
        ],
        "rename": {"drySummary": rename_dry_summary, "applySummary": rename_apply_summary},
        "comments": {"drySummary": comments_dry_summary, "applySummary": comments_apply_summary},
        "readback": {"allNamesAndCommentsPresent": all_names_and_comments_present, "functions": readback},
        "xrefs": {
            "rows": len(xref_rows),
            "loadCallsShutdown": load_calls_shutdown,
            "reloadCallsInitialise": reload_calls_initialise,
            "reloadCallsLoad": reload_calls_load,
        },
        "inputs": {
            "renameDryLog": relative(rename_dry_log_path),
            "renameApplyLog": relative(rename_apply_log_path),
            "commentsDryLog": relative(comments_dry_log_path),
            "commentsApplyLog": relative(comments_apply_log_path),
            "metadata": relative(metadata_path),
            "xrefs": relative(xrefs_path),
        },
        "failures": failures,
        "whatIsProven": [
            "Three saved BattleEngineData functions now use source-aligned CBattleEngineData owner names.",
            "Read-back metadata confirms proof-boundary comments for default initialise, shutdown cleanup, and CMemBuffer load identities.",
            "Xref read-back confirms the renamed CMemBuffer load function calls the renamed shutdown function.",
        ],
        "notProven": [
            "This does not change signatures, parameter names, local names, tags, structures, or data types.",
            "This does not prove source-build identity beyond the checked source/decompile/xref alignment.",
            "This does not prove runtime behavior.",
            "This does not complete the broader Ghidra static re-audit queue.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, command summaries, counts, and proof boundaries only; raw Ghidra logs and metadata exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--rename-dry-log", type=Path, default=DEFAULT_RENAME_DRY_LOG)
    parser.add_argument("--rename-apply-log", type=Path, default=DEFAULT_RENAME_APPLY_LOG)
    parser.add_argument("--comments-dry-log", type=Path, default=DEFAULT_COMMENTS_DRY_LOG)
    parser.add_argument("--comments-apply-log", type=Path, default=DEFAULT_COMMENTS_APPLY_LOG)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    out = resolve(args.out)
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}", file=sys.stderr)
        return 1

    report = build_report(
        rename_dry_log_path=args.rename_dry_log,
        rename_apply_log_path=args.rename_apply_log,
        comments_dry_log_path=args.comments_dry_log,
        comments_apply_log_path=args.comments_apply_log,
        metadata_path=args.metadata,
        xrefs_path=args.xrefs,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra BattleEngineData owner correction probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        print(f"Targets: {report['targetCount']}")
        print(f"Rename: {report['rename']}")
        print(f"Comments: {report['comments']}")
        print(f"All names/comments present: {report['readback']['allNamesAndCommentsPresent']}")
        print(f"Load calls shutdown: {report['xrefs']['loadCallsShutdown']}")
        if report["failures"]:
            print("Failures:")
            for failure in report["failures"]:
                print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
