#!/usr/bin/env python3
"""Validate Wave792 signature-debt read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave792-signature-debt-candidates"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_signature_debt_wave792_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-031629_post_wave792_crt_runtime_signature_debt_verified"

TARGETS = {
    "0x0055e0c0": ("__aulldiv", "ulonglong __stdcall __aulldiv(uint dividend_low, uint dividend_high, uint divisor_low, uint divisor_high)", ("unsigned 64-bit division", "dividend_low")),
    "0x0055e128": ("__ftol", "longlong __cdecl __ftol(void)", ("x87", "ST0")),
    "0x0055e4d4": ("__fclose_lk", "int __cdecl __fclose_lk(void * stream)", ("locked fclose", "stream")),
    "0x0055fcc0": ("__alldiv", "longlong __stdcall __alldiv(uint dividend_low, int dividend_high, uint divisor_low, int divisor_high)", ("signed 64-bit division", "reapplies the sign")),
    "0x00560289": ("__amsg_exit", "void __cdecl __amsg_exit(int runtime_error_code)", ("runtime_error_code", "exit")),
    "0x005639d0": ("__allmul", "longlong __stdcall __allmul(uint left_low, int left_high, uint right_low, int right_high)", ("64-bit multiplication", "product")),
    "0x00569ec0": ("__aullrem", "ulonglong __stdcall __aullrem(uint dividend_low, uint dividend_high, uint divisor_low, uint divisor_high)", ("unsigned 64-bit remainder", "high-divisor normalization")),
    "0x0056b840": ("___free_lc_time", "void __cdecl ___free_lc_time(void * locale_time_block)", ("locale-time block", "locale-time cleanup")),
}

COMMON_TAGS = {
    "static-reaudit",
    "signature-debt-wave792",
    "wave792-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "param-name-hardened",
    "crt-runtime",
}

CORE_ANCHORS = (
    "Wave792 signature debt",
    "signature-debt-wave792",
    "0x0055e0c0 __aulldiv",
    "0x0055e128 __ftol",
    "0x0055e4d4 __fclose_lk",
    "0x0055fcc0 __alldiv",
    "0x00560289 __amsg_exit",
    "0x005639d0 __allmul",
    "0x00569ec0 __aullrem",
    "0x0056b840 ___free_lc_time",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime arithmetic behavior proven",
    "runtime fpu behavior proven",
    "runtime stream behavior proven",
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
        "pre-metadata.tsv": 40,
        "pre-tags.tsv": 40,
        "pre-xrefs.tsv": 195,
        "pre-instructions.tsv": 1480,
        "pre-decompile/index.tsv": 40,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 104,
        "post-instructions.tsv": 296,
        "post-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave792 signature-debt hardening", *tokens):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0",
        "apply-initial-readback-mismatch.log": "Read-back signature mismatch at 0x0055e128",
        "apply-dry-corrected.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply-readback.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 104 rows",
        "post-instructions.log": "Wrote 296 instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5544",
        "queue-probe.log": "Undefined signatures: 21",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave792.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave792_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        if relative != "apply-initial-readback-mismatch.log":
            for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
                require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 554, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 21, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 11, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5544, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5512, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 171281287, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:ghidra-signature-debt-wave792") == r"py -3 tools\ghidra_signature_debt_wave792_probe.py --check", "missing package script", failures)
    require(any(row.get("task") == "Wave792 signature debt" for row in read_jsonl(LEDGER)), "missing Wave792 ledger row", failures)
    require(any(row.get("task") == "Wave792 signature debt" and row.get("attempt_id") == 20447 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave792 attempt row", failures)


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
        print("Wave792 signature-debt probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave792 signature-debt probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
