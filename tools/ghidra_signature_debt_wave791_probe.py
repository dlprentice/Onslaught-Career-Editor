#!/usr/bin/env python3
"""Validate Wave791 signature-debt read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave791-crt-seh-signature-debt"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_signature_debt_wave791_2026-05-24.md"
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

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-025245_post_wave791_crt_seh_signature_debt_verified"

TARGETS = {
    "0x0055d6a0": ("CRT__SehPopExceptionFrameAndJump", "void __stdcall CRT__SehPopExceptionFrameAndJump(void * continuation_target)", ("continuation_target", "CRT__SehUnwindAndResumeSearch")),
    "0x0055d6d4": ("CRT__InvokeCallbackWithLockGuards", "void __stdcall CRT__InvokeCallbackWithLockGuards(int transfer_cookie, void * callback_target)", ("callback_target", "CRT__BuildCatchObject")),
    "0x0055d6db": ("CRT__SehLockUnlockAndJump", "void __stdcall CRT__SehLockUnlockAndJump(int transfer_cookie, void * callback_target)", ("callback_target", "CRT__BuildCatchObject")),
    "0x0055d6e2": ("CRT__SehRtlUnwindAndRestoreFrame", "void __stdcall CRT__SehRtlUnwindAndRestoreFrame(void * target_frame, void * exception_record)", ("RtlUnwind(target_frame", "exception_record")),
    "0x0055d7bb": ("CRT__SehCallback_Call_005602d2", "void __cdecl CRT__SehCallback_Call_005602d2(int callback_arg0, int callback_arg1, int callback_arg2)", ("callback wrapper", "Parameter names stay conservative")),
    "0x0055d896": ("CRT__SehFilterCppException", "int __cdecl CRT__SehFilterCppException(void * exception_record, void * seh_frame, void * dispatcher_context)", ("exception_record", "seh_frame")),
    "0x0055d90b": ("CRT__GetRangeOfTryBlocksForState", "int __cdecl CRT__GetRangeOfTryBlocksForState(void * eh_func_info, int try_nesting_index, int current_state, int * out_low_try, int * out_high_try)", ("eh_func_info", "out_low_try")),
    "0x0055d988": ("__global_unwind2", "void __cdecl __global_unwind2(void * target_frame)", ("Visual C++ library-matched", "RtlUnwind(target_frame")),
    "0x0055d9ca": ("__local_unwind2", "void __cdecl __local_unwind2(void * registration_frame, int stop_state)", ("Visual C++ library-matched", "stop_state")),
    "0x0055da55": ("__NLG_Notify1", "void __fastcall __NLG_Notify1(int nlg_destination)", ("Visual C++ library-matched", "nlg_destination")),
}

COMMON_TAGS = {
    "static-reaudit",
    "signature-debt-wave791",
    "wave791-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "param-name-hardened",
    "crt-seh",
}

CORE_ANCHORS = (
    "Wave791 signature debt",
    "signature-debt-wave791",
    "0x0055d6a0 CRT__SehPopExceptionFrameAndJump",
    "0x0055d6e2 CRT__SehRtlUnwindAndRestoreFrame",
    "0x0055d896 CRT__SehFilterCppException",
    "0x0055d90b CRT__GetRangeOfTryBlocksForState",
    "0x0055d988 __global_unwind2",
    "0x0055d9ca __local_unwind2",
    "0x0055da55 __NLG_Notify1",
    "commentless high-signal queue",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
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
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 18,
        "pre-instructions.tsv": 1050,
        "pre-decompile/index.tsv": 10,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 18,
        "post-instructions.tsv": 1050,
        "post-decompile/index.tsv": 10,
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
            require("Wave791 signature-debt hardening" in comment, f"missing Wave791 comment token at {address}", failures)
            for token in tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 18 rows",
        "post-instructions.log": "Wrote 1050 instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5544",
        "queue-probe.log": "Param signatures: 12",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave791.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave791_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 554, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 28, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 12, "param_N count mismatch", failures)
    require(not queue["priorityQueues"]["commentlessHighSignal"], "commentless high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5544, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5504, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (171215751, 171215751.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in ("runtime behavior proven", "fully reverse-engineered", "rebuild parity proven"):
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(package.get("scripts", {}).get("test:ghidra-signature-debt-wave791") == r"py -3 tools\ghidra_signature_debt_wave791_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave791 signature debt" for row in ledger_rows), "missing Wave791 ledger row", failures)
    require(any(row.get("task") == "Wave791 signature debt" and row.get("attempt_id") == 20446 for row in attempts), "missing Wave791 attempt row", failures)


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
        print("Wave791 signature-debt probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave791 signature-debt probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
