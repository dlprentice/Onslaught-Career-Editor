#!/usr/bin/env python3
"""Validate Wave831 CText CopyFrom read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave831-ctext-copyfrom"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctext_copyfrom_wave831_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
TEXT_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "text.cpp" / "_index.md"
TEXT_COPY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "text.cpp" / "CText__CopyFrom.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TARGET = "0x004f2660"
TARGET_NAME = "CText__CopyFrom"
TARGET_SIGNATURE = "void __thiscall CText__CopyFrom(void * this, void * src)"
CALLER = "0x00466ab0"
CALLER_NAME = "CFrontEnd__SetLanguage"
NEXT_HEAD = "0x004f2710 CTextureBase__Init"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-224036_post_wave831_ctext_copyfrom_verified"

COMMON_TAGS = {
    "static-reaudit",
    "ctext-copyfrom-wave831",
    "wave831-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "text-localization",
    "frontend-language",
    "deep-copy",
    "buffer-copy",
    "g-text",
    "language-switch",
}

CORE_ANCHORS = (
    "Wave831 CText CopyFrom",
    "ctext-copyfrom-wave831",
    "0x004f2660 CText__CopyFrom",
    "CFrontEnd__SetLanguage",
    "0x00466ace",
    "g_Text",
    "CDXMemoryManager__Free",
    "CDXMemoryManager__Alloc",
    "0x00632dd8",
    "0x72",
    "0x155",
    "5652/6098 = 92.69%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime language-switch behavior proven",
    "runtime localization behavior proven",
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


def strict_clean_count(rows: list[dict[str, str]]) -> int:
    return sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 1,
        "pre-instructions.tsv": 161,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 9,
        "pre-context-decompile/index.tsv": 9,
        "pre-caller-metadata.tsv": 1,
        "pre-caller-instructions.tsv": 105,
        "pre-caller-decompile/index.tsv": 1,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions.tsv": 105,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 9,
        "post-context-decompile/index.tsv": 9,
        "post-caller-metadata.tsv": 1,
        "post-caller-instructions.tsv": 105,
        "post-caller-decompile/index.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    row = metadata.get(TARGET)
    require(row is not None, "missing target metadata", failures)
    if row is not None:
        require(row.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, "target signature mismatch", failures)
        require(row.get("status") == "OK", "target metadata status mismatch", failures)
        comment = row.get("comment", "")
        for token in (
            "Wave831 static read-back",
            "frontend-language CText deep-copy helper",
            "CFrontEnd__SetLanguage at 0x00466ace",
            "global g_Text",
            "CDXMemoryManager__Free",
            "CDXMemoryManager__Alloc",
            "0x00632dd8",
            "0x72",
            "0x155",
            "REP MOVSD/REP MOVSB",
            "this+0x08 and this+0x0c",
            "Static retail Ghidra evidence only",
        ):
            require(token in comment, f"missing target comment token: {token}", failures)

    tag_row = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}.get(TARGET)
    require(tag_row is not None, "missing target tags", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"tags missing: {COMMON_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "tag status mismatch", failures)

    xref = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}.get(TARGET)
    require(xref is not None, "missing target xref", failures)
    if xref is not None:
        require(normalize_address(xref.get("from_addr", "")) == "0x00466ace", "caller xref address mismatch", failures)
        require(normalize_address(xref.get("from_function_addr", "")) == CALLER, "caller function mismatch", failures)
        require(xref.get("from_function") == CALLER_NAME, "caller function name mismatch", failures)
        require(xref.get("ref_type") == "UNCONDITIONAL_CALL", "xref type mismatch", failures)

    dec = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}.get(TARGET)
    require(dec is not None, "missing target decompile index", failures)
    if dec is not None:
        require(dec.get("name") == TARGET_NAME, "target decompile name mismatch", failures)
        require(dec.get("signature") == TARGET_SIGNATURE, "target decompile signature mismatch", failures)
        require(dec.get("status") == "OK", "target decompile status mismatch", failures)

    target_text = read_text(BASE / "post-decompile" / "004f2660_CText__CopyFrom.c")
    for token in ("CDXMemoryManager__Free", "CDXMemoryManager__Alloc", "s_C__dev_ONSLAUGHT2_text_cpp_00632dd8", "0x155", "CText__CopyFrom"):
        require(token in target_text, f"missing target decompile token: {token}", failures)

    caller_text = read_text(BASE / "post-caller-decompile" / "00466ab0_CFrontEnd__SetLanguage.c")
    for token in ("CFEPOptions__Cleanup();", "CText__CopyFrom(&g_Text", "language_index * 3 + 0xbf4"):
        require(token in caller_text, f"missing caller decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions.log": "Wrote 105 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=9 found=9 missing=0",
        "post-context-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "post-caller-metadata.log": "targets=1 found=1 missing=0",
        "post-caller-instructions.log": "Wrote 105 instruction rows",
        "post-caller-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1", "LockException"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    apply_text = read_text(BASE / "apply.log")
    require("READBACK_OK: 0x004f2660 CText__CopyFrom" in apply_text, "missing apply read-back token", failures)
    require("REPORT: Save succeeded" in apply_text, "missing apply save token", failures)

    quality_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave831.log")
    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave831_queue_probe.log")
    require("total_functions=6098 commented_functions=5652" in quality_log, "missing Wave831 quality export token", failures)
    require("Commentless functions: 446" in queue_log, "missing Wave831 queue probe token", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 446, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = strict_clean_count(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5652, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5652, "strict clean count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004f2710", "raw commentless head address mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CTextureBase__Init", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171772807 or backup.get("totalBytes") == 171772807.0, "backup byte count mismatch", failures)
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
        TEXT_INDEX,
        TEXT_COPY_DOC,
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
        scripts.get("test:ghidra-ctext-copyfrom-wave831")
        == r"py -3 tools\ghidra_ctext_copyfrom_wave831_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave831 CText CopyFrom" for row in ledger_rows), "missing Wave831 ledger row", failures)
    require(
        any(row.get("task") == "Wave831 CText CopyFrom" and row.get("attempt_id") == 20486 for row in attempts),
        "missing Wave831 attempt row",
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
        print("Wave831 CText CopyFrom probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave831 CText CopyFrom probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
