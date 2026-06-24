#!/usr/bin/env python3
"""Validate Wave793 signature-debt read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave793-crt-runtime-signature-debt"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_signature_debt_wave793_2026-05-24.md"
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

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-034246_post_wave793_crt_runtime_signature_debt_verified"

TARGETS = {
    "0x0055f7a3": ("___timet_from_ft", "int __cdecl ___timet_from_ft(void * file_time)", ("FILETIME-to-time_t", "CRT__SystemTimeToUnixTimestampLocal")),
    "0x00560ae0": ("__CallSettingFrame@12", "void __stdcall __CallSettingFrame@12(int frame_arg0, int frame_arg1, int nlg_destination)", ("non-local-goto", "__NLG_Notify1")),
    "0x00561339": ("__seh_longjmp_unwind@4", "void __stdcall __seh_longjmp_unwind@4(void * longjmp_registration)", ("SEH longjmp unwind", "__local_unwind2")),
    "0x005615d5": ("__fload_withFB", "uint __fastcall __fload_withFB(int dispatch_cookie, void * floating_record)", ("floating-load", "floating_record")),
    "0x0056163b": ("__math_exit", "void __cdecl __math_exit(void)", ("math-exit", "__startOneArgErrorHandling")),
    "0x0056d4c7": ("___add_12", "void __cdecl ___add_12(uint * accumulator, uint * addend)", ("12-byte addition", "accumulator")),
    "0x0059ccce": ("Memcpy", "void * __thiscall Memcpy(void * this, void * destination, void * source, uint byte_count)", ("implicit this", "owner-ambiguous")),
    "0x005d0983": ("init_namebuf", "void __cdecl init_namebuf(int temp_name_selector)", ("temporary-name buffer", "temporary-file helper")),
}

COMMON_TAGS = {
    "static-reaudit",
    "signature-debt-wave793",
    "wave793-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "param-name-hardened",
    "crt-runtime",
}

CORE_ANCHORS = (
    "Wave793 signature debt",
    "signature-debt-wave793",
    "0x0055f7a3 ___timet_from_ft",
    "0x00560ae0 __CallSettingFrame@12",
    "0x00561339 __seh_longjmp_unwind@4",
    "0x005615d5 __fload_withFB",
    "0x0056163b __math_exit",
    "0x0056d4c7 ___add_12",
    "0x0059ccce Memcpy",
    "0x005d0983 init_namebuf",
    "0x0042f220 CSPtrSet__Clear",
    "0x004acde0 CMeshCollisionVolume__InitContactOutputRecord",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime time-conversion behavior proven",
    "runtime seh behavior proven",
    "runtime fpu behavior proven",
    "runtime arithmetic behavior proven",
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
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 19,
        "pre-instructions.tsv": 296,
        "pre-decompile/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 19,
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
            for token in ("Wave793 signature-debt hardening", *tokens):
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
        "apply-initial-thiscall-mismatch.log": "Read-back signature mismatch at 0x0059ccce",
        "apply-dry-after-thiscall-fix.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=7 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 19 rows",
        "post-instructions.log": "Wrote 296 instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5544",
        "queue-probe.log": "Undefined signatures: 13",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave793.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave793_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        if relative != "apply-initial-thiscall-mismatch.log":
            for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
                require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 554, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 13, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 11, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    first_signature_debt = queue["priorityQueues"]["signature"][0]
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5544, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5520, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(first_signature_debt.get("address") == "0x004acde0", "signature-debt head mismatch", failures)

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
    require(scripts.get("test:ghidra-signature-debt-wave793") == r"py -3 tools\ghidra_signature_debt_wave793_probe.py --check", "missing package script", failures)
    require(any(row.get("task") == "Wave793 signature debt" for row in read_jsonl(LEDGER)), "missing Wave793 ledger row", failures)
    require(any(row.get("task") == "Wave793 signature debt" and row.get("attempt_id") == 20448 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave793 attempt row", failures)


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
        print("Wave793 signature-debt probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave793 signature-debt probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
