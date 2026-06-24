#!/usr/bin/env python3
"""Validate Wave825 StrCopyN helper read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave825-strcopyn-helper"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_strcopyn_helper_wave825_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
STRING_HELPERS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "string-helpers.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-193427_post_wave825_strcopyn_helper_verified"
NEXT_HEAD = "0x004daff0 CFearGrid__LookupFearWeightByArchetype"
TARGET_ADDRESS = "0x004d6240"
TARGET_NAME = "StrCopyN"
TARGET_SIGNATURE = "char * __cdecl StrCopyN(char * dst, char * src, int maxLen)"

COMMENT_TOKENS = (
    "Wave825 static read-back/comment hardening",
    "0x00441740 CConsole__Printf",
    "0x004418a0 CConsole__PrintfNoNewline",
    "returns the original dst pointer",
    "maxLen < 1",
    "does not zero-pad",
    "explicitly clear the final ring-entry byte",
)

COMMON_TAGS = {
    "static-reaudit",
    "strcopyn-helper-wave825",
    "wave825-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "string-helper",
    "console",
    "bounded-copy",
    "no-zero-padding",
    "console-ring-entry",
}

CORE_ANCHORS = (
    "Wave825 StrCopyN helper",
    "strcopyn-helper-wave825",
    "0x004d6240 StrCopyN",
    "0x00441740 CConsole__Printf",
    "0x004418a0 CConsole__PrintfNoNewline",
    "5633/6098 = 92.37%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime console output behavior proven",
    "runtime truncation policy proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 2,
        "pre-instructions.tsv": 241,
        "pre-decompile/index.tsv": 1,
        "pre-caller-metadata.tsv": 2,
        "pre-caller-instructions.tsv": 342,
        "pre-caller-decompile/index.tsv": 2,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 2,
        "post-instructions.tsv": 241,
        "post-decompile/index.tsv": 1,
        "post-caller-metadata.tsv": 2,
        "post-caller-instructions.tsv": 342,
        "post-caller-decompile/index.tsv": 2,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), set()).add(normalize_address(row["from_addr"]))

    row = metadata.get(TARGET_ADDRESS)
    require(row is not None, "missing StrCopyN metadata", failures)
    if row is not None:
        require(row.get("name") == TARGET_NAME, "StrCopyN name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, f"StrCopyN signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "StrCopyN metadata status mismatch", failures)
        comment = row.get("comment", "")
        for token in COMMENT_TOKENS:
            require(token in comment, f"missing StrCopyN comment token: {token}", failures)

    tag_row = tags.get(TARGET_ADDRESS)
    require(tag_row is not None, "missing StrCopyN tags", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"StrCopyN tags missing: {COMMON_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "StrCopyN tag status mismatch", failures)

    dec = decompile.get(TARGET_ADDRESS)
    require(dec is not None, "missing StrCopyN decompile index", failures)
    if dec is not None:
        require(dec.get("signature") == TARGET_SIGNATURE, "StrCopyN decompile signature mismatch", failures)
        require(dec.get("status") == "OK", "StrCopyN decompile status mismatch", failures)

    require({"0x0044185c", "0x00441998"}.issubset(xrefs.get(TARGET_ADDRESS, set())), "StrCopyN caller xrefs missing", failures)

    helper_decompile = read_text(BASE / "post-decompile" / "004d6240_StrCopyN.c")
    for token in ("while", "maxLen < 1", "cVar1 == '\\0'", "return pcVar2"):
        require(token in helper_decompile, f"missing helper decompile token: {token}", failures)

    caller_text = read_text(BASE / "post-caller-decompile" / "00441740_CConsole__Printf.c") + read_text(
        BASE / "post-caller-decompile" / "004418a0_CConsole__PrintfNoNewline.c"
    )
    for token in ("StrCopyN", "0x50", "0x58", "vsprintf"):
        require(token in caller_text, f"missing caller decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 2 rows",
        "post-instructions.log": "Wrote 241 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-caller-metadata.log": "targets=2 found=2 missing=0",
        "post-caller-instructions.log": "Wrote 342 instruction rows",
        "post-caller-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5633",
        "queue-probe.log": "Commentless functions: 465",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave825.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave825_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    apply_text = read_text(BASE / "apply.log")
    require("READBACK_OK: 0x004d6240 char * __cdecl StrCopyN(char * dst, char * src, int maxLen)" in apply_text, "missing apply readback token", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 465, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5633, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5633, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004daff0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFearGrid__LookupFearWeightByArchetype", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171576199 or backup.get("totalBytes") == 171576199.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        STRING_HELPERS_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-strcopyn-helper-wave825")
        == r"py -3 tools\ghidra_strcopyn_helper_wave825_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave825 StrCopyN helper" for row in ledger_rows), "missing Wave825 ledger row", failures)
    require(
        any(row.get("task") == "Wave825 StrCopyN helper" and row.get("attempt_id") == 20480 for row in attempts),
        "missing Wave825 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave825 StrCopyN helper probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave825 StrCopyN helper probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
