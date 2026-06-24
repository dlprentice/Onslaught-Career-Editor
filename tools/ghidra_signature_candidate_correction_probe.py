#!/usr/bin/env python3
"""Verify the first Ghidra signature-candidate correction pass.

This probe checks the saved rename/comment correction for three functions that
the name-confidence tranche originally classified as signature candidates. The
pass corrects weak wrapper names to source-aligned identities and records why
signature/parameter hardening remains deferred.
"""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "signature-candidate-corrections" / "current"
DEFAULT_RENAME_DRY_LOG = BASE / "rename_dry.log"
DEFAULT_RENAME_APPLY_LOG = BASE / "rename_apply.log"
DEFAULT_COMMENTS_DRY_LOG = BASE / "comments_dry.log"
DEFAULT_COMMENTS_APPLY_LOG = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_after.tsv"
DEFAULT_OUT = BASE / "signature-candidate-corrections.json"

TARGETS = [
    {
        "address": "0x0040e280",
        "oldName": "DXMemBuffer_ReadBytes__Wrapper_0040e280",
        "name": "CInitThing__LoadFromMemBuffer",
        "commentTokens": [
            "CInitThing::Load(short, CMEMBUFFER&)",
            "CSquadInitThing__VFunc_01_0048d8d0",
            "signature and parameter names deferred",
        ],
    },
    {
        "address": "0x0040f140",
        "oldName": "OID_FreeObject__Wrapper_0040f140",
        "name": "BattleEngineConfigurations__ShutDown",
        "commentTokens": [
            "UBattleEngineConfigurations::ShutDown",
            "0x00660250",
            "0x00660200",
            "signature and parameter names deferred",
        ],
    },
    {
        "address": "0x0040f520",
        "oldName": "CSPtrSet_Init__Wrapper_0040f520",
        "name": "CBattleEngineData__ctor",
        "commentTokens": [
            "CBattleEngineData constructor",
            "+0x40/+0x50",
            "Initialise/Load",
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


def read_metadata(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
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


def build_report(
    *,
    rename_dry_log_path: Path = DEFAULT_RENAME_DRY_LOG,
    rename_apply_log_path: Path = DEFAULT_RENAME_APPLY_LOG,
    comments_dry_log_path: Path = DEFAULT_COMMENTS_DRY_LOG,
    comments_apply_log_path: Path = DEFAULT_COMMENTS_APPLY_LOG,
    metadata_path: Path = DEFAULT_METADATA,
) -> dict[str, object]:
    rename_dry_log_path = resolve(rename_dry_log_path)
    rename_apply_log_path = resolve(rename_apply_log_path)
    comments_dry_log_path = resolve(comments_dry_log_path)
    comments_apply_log_path = resolve(comments_apply_log_path)
    metadata_path = resolve(metadata_path)

    failures: list[str] = []
    for label, path in (
        ("rename dry log", rename_dry_log_path),
        ("rename apply log", rename_apply_log_path),
        ("comment dry log", comments_dry_log_path),
        ("comment apply log", comments_apply_log_path),
        ("metadata read-back", metadata_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    rename_dry_text = read_text(rename_dry_log_path)
    rename_apply_text = read_text(rename_apply_log_path)
    comments_dry_text = read_text(comments_dry_log_path)
    comments_apply_text = read_text(comments_apply_log_path)
    metadata_rows = read_metadata(metadata_path)

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

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-signature-candidate-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "signature-candidates-renamed-commented-signatures-deferred"
        if status == "PASS"
        else "signature-candidate-correction-blocked",
        "targetCount": expected_count,
        "targets": [
            {"address": target["address"], "oldName": target["oldName"], "name": target["name"]}
            for target in TARGETS
        ],
        "rename": {"drySummary": rename_dry_summary, "applySummary": rename_apply_summary},
        "comments": {"drySummary": comments_dry_summary, "applySummary": comments_apply_summary},
        "readback": {"allNamesAndCommentsPresent": all_names_and_comments_present, "functions": readback},
        "inputs": {
            "renameDryLog": relative(rename_dry_log_path),
            "renameApplyLog": relative(rename_apply_log_path),
            "commentsDryLog": relative(comments_dry_log_path),
            "commentsApplyLog": relative(comments_apply_log_path),
            "metadata": relative(metadata_path),
        },
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra project has source-aligned names for three formerly weak signature-candidate wrappers.",
            "Read-back metadata confirms proof-boundary comments on CInitThing load, BattleEngineConfigurations shutdown, and CBattleEngineData constructor identities.",
            "The comments explicitly preserve the boundary that signature and parameter hardening was deferred.",
        ],
        "notProven": [
            "This does not change signatures, parameter names, local names, tags, structures, or data types.",
            "This does not prove the current decompiler parameter storage is final.",
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
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra signature-candidate correction probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        print(f"Targets: {report['targetCount']}")
        print(f"Rename: {report['rename']}")
        print(f"Comments: {report['comments']}")
        print(f"All names/comments present: {report['readback']['allNamesAndCommentsPresent']}")
        if report["failures"]:
            print("Failures:")
            for failure in report["failures"]:
                print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
