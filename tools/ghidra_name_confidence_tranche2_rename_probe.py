#!/usr/bin/env python3
"""Verify the second Ghidra name-confidence rename-candidate correction pass."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "name-confidence-tranche2-rename" / "current"
DEFAULT_RENAME_DRY_LOG = BASE / "rename_dry.log"
DEFAULT_RENAME_APPLY_LOG = BASE / "rename_apply.log"
DEFAULT_COMMENTS_DRY_LOG = BASE / "comment_dry.log"
DEFAULT_COMMENTS_APPLY_LOG = BASE / "comment_apply.log"
DEFAULT_METADATA = BASE / "metadata_after.tsv"
DEFAULT_DECOMPILE_INDEX = BASE / "decompile_after" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_after"
DEFAULT_XREFS = BASE / "xrefs_after.tsv"
DEFAULT_OUT = BASE / "name-confidence-tranche2-rename.json"

TARGETS = [
    {
        "address": "0x00414b30",
        "oldName": "CVBufTexture_Unk_0050a290__Wrapper_00414b30",
        "name": "TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit",
        "commentTokens": [
            "Behavior-backed rename from weak CVBufTexture wrapper",
            "CUnit__IsTargetTimeoutBeforeProfileLimit",
            "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
            "runtime behavior remain deferred",
        ],
        "decompileTokens": ["CUnit__IsTargetTimeoutBeforeProfileLimit", "return 1"],
        "expectedXrefFunctions": ["CBattleEngine__UpdateAutoTargetSetAndFireProjectiles"],
        "note": "Scans a linked target/unit set and returns true when any entry passes the timeout/profile-limit predicate.",
    },
    {
        "address": "0x00505c30",
        "oldName": "stricmp__Wrapper_00505c30",
        "name": "NamedEntryList__FindNearestChildByNameAndPosition",
        "commentTokens": [
            "Behavior-backed rename from weak stricmp wrapper",
            "case-insensitive string compare",
            "nearest child point by squared 3D distance",
            "runtime behavior remain deferred",
        ],
        "decompileTokens": ["stricmp", "DAT_00854fc8", "0x4b18967f", "+ 0x24"],
        "expectedXrefRows": 2,
        "note": "Looks up a named entry case-insensitively and returns the nearest child position by squared distance.",
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


def read_xrefs(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr"] = normalize_address(row.get("target_addr", ""))
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


def build_report(
    *,
    rename_dry_log_path: Path = DEFAULT_RENAME_DRY_LOG,
    rename_apply_log_path: Path = DEFAULT_RENAME_APPLY_LOG,
    comments_dry_log_path: Path = DEFAULT_COMMENTS_DRY_LOG,
    comments_apply_log_path: Path = DEFAULT_COMMENTS_APPLY_LOG,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_DECOMPILE_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
) -> dict[str, object]:
    rename_dry_log_path = resolve(rename_dry_log_path)
    rename_apply_log_path = resolve(rename_apply_log_path)
    comments_dry_log_path = resolve(comments_dry_log_path)
    comments_apply_log_path = resolve(comments_apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)

    failures: list[str] = []
    for label, path in (
        ("rename dry log", rename_dry_log_path),
        ("rename apply log", rename_apply_log_path),
        ("comment dry log", comments_dry_log_path),
        ("comment apply log", comments_apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    rename_dry_text = read_text(rename_dry_log_path)
    rename_apply_text = read_text(rename_apply_log_path)
    comments_dry_text = read_text(comments_dry_log_path)
    comments_apply_text = read_text(comments_apply_log_path)
    metadata_rows = read_metadata(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xrefs = read_xrefs(xrefs_path)
    xrefs_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in xrefs:
        xrefs_by_target[row["target_addr"]].append(row)

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
    all_present = True
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

        metadata_row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        decompile_file = find_decompile_file(decompile_dir, address)
        decompile_text = read_text(decompile_file) if decompile_file else ""
        target_xrefs = xrefs_by_target[normalize_address(address)]

        comment_tokens_present = False
        metadata_ok = False
        if metadata_row is None:
            failures.append(f"metadata read-back missing {address}")
        else:
            comment = metadata_row.get("comment", "")
            comment_tokens_present = all(token in comment for token in target["commentTokens"])
            metadata_ok = metadata_row.get("name") == name and metadata_row.get("status") == "OK" and comment_tokens_present
            if not metadata_ok:
                failures.append(f"metadata read-back for {address} lacks expected name/status/comment tokens")

        index_ok = False
        if index_row is None:
            failures.append(f"decompile index missing {address}")
        else:
            index_ok = index_row.get("name") == name and index_row.get("status") == "OK"
            if not index_ok:
                failures.append(f"decompile index for {address} lacks expected name/status")

        decompile_tokens_present = bool(decompile_text) and all(token in decompile_text for token in target["decompileTokens"])
        if not decompile_tokens_present:
            failures.append(f"decompile read-back for {address} lacks expected behavior tokens")

        expected_rows = int(target.get("expectedXrefRows", 0))
        expected_functions = set(target.get("expectedXrefFunctions", []))
        xref_ok = True
        if expected_rows and len(target_xrefs) < expected_rows:
            failures.append(f"{address} expected xref rows >= {expected_rows}, found {len(target_xrefs)}")
            xref_ok = False
        if expected_functions:
            observed = {row.get("from_function", "") for row in target_xrefs}
            missing = sorted(expected_functions - observed)
            if missing:
                failures.append(f"{address} missing expected xref context: {', '.join(missing)}")
                xref_ok = False

        target_ok = metadata_ok and index_ok and decompile_tokens_present and xref_ok
        all_present = all_present and target_ok
        readback[address] = {
            "name": metadata_row.get("name") if metadata_row else None,
            "status": metadata_row.get("status") if metadata_row else None,
            "signature": metadata_row.get("signature") if metadata_row else None,
            "commentTokensPresent": comment_tokens_present,
            "decompileTokensPresent": decompile_tokens_present,
            "xrefRows": len(target_xrefs),
            "decompile": relative(decompile_file) if decompile_file else None,
        }

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-name-confidence-tranche2-rename.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "tranche2-rename-candidates-renamed-commented"
        if status == "PASS"
        else "tranche2-rename-candidate-correction-blocked",
        "targetCount": expected_count,
        "targets": [
            {"address": target["address"], "oldName": target["oldName"], "name": target["name"], "note": target["note"]}
            for target in TARGETS
        ],
        "rename": {"drySummary": rename_dry_summary, "applySummary": rename_apply_summary},
        "comments": {"drySummary": comments_dry_summary, "applySummary": comments_apply_summary},
        "readback": {"allNamesCommentsAndContextPresent": all_present, "functions": readback, "xrefRows": len(xrefs)},
        "inputs": {
            "renameDryLog": relative(rename_dry_log_path),
            "renameApplyLog": relative(rename_apply_log_path),
            "commentsDryLog": relative(comments_dry_log_path),
            "commentsApplyLog": relative(comments_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
        },
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra project has behavior-backed names for the two second-tranche rename candidates.",
            "Read-back metadata confirms proof-boundary comments for the target-set timeout scan and named-entry nearest-position lookup.",
            "Decompile and xref read-backs preserve the behavior/caller context that justified the two names.",
        ],
        "notProven": [
            "This does not change signatures, parameter names, local names, tags, structures, or data types.",
            "This does not prove exact source-to-retail identity or final owner/class boundaries.",
            "This does not prove runtime behavior.",
            "This does not complete the broader Ghidra static re-audit queue.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, command summaries, counts, and proof boundaries only; raw Ghidra logs, xrefs, metadata, and decompile exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--rename-dry-log", type=Path, default=DEFAULT_RENAME_DRY_LOG)
    parser.add_argument("--rename-apply-log", type=Path, default=DEFAULT_RENAME_APPLY_LOG)
    parser.add_argument("--comments-dry-log", type=Path, default=DEFAULT_COMMENTS_DRY_LOG)
    parser.add_argument("--comments-apply-log", type=Path, default=DEFAULT_COMMENTS_APPLY_LOG)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_DECOMPILE_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
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
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra name-confidence tranche 2 rename probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        print(f"Targets: {report['targetCount']}")
        print(f"Rename: {report['rename']}")
        print(f"Comments: {report['comments']}")
        print(f"All names/comments/context present: {report['readback']['allNamesCommentsAndContextPresent']}")
        if report["failures"]:
            print("Failures:")
            for failure in report["failures"]:
                print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
