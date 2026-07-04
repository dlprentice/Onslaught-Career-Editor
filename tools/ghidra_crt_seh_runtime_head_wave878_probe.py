#!/usr/bin/env python3
"""Validate Wave878 CRT/SEH runtime-head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave878-crt-seh-runtime-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_seh_runtime_head_wave878_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
CRT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "crt-seh.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave878 CRT/SEH runtime head"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-221858_post_wave878_crt_seh_runtime_head_verified"
NEXT_HEAD = "0x0055dcb0 OID__AcosWrapper"
STRICT_PROXY = "5901/6113 = 96.53%"

TARGETS = {
    "0x0055d731": (
        "CRT__SehDispatchWithScopeTable_Thunk_0055d731",
        "int CRT__SehDispatchWithScopeTable_Thunk_0055d731(void)",
        ("CRT/SEH dispatch thunk", "CRT__SehDispatchWithScopeTable", "500-plus no-function callsites"),
    ),
    "0x0055d767": (
        "CRT__SehInvokeCallSettingFrame12",
        "int CRT__SehInvokeCallSettingFrame12(void)",
        ("CRT__SehCallback_Call_005602d2", "ExceptionList", "__CallSettingFrame_12", "0x005607bb"),
    ),
    "0x0055d7e0": (
        "CRT__CallExceptionTranslator",
        "int CRT__CallExceptionTranslator(void)",
        ("CRT__SehFilterCppException", "CRT__GetOrInitThreadLocalRecord", "offset +0x68", "0x00560547"),
    ),
    "0x0055da5e": (
        "CRT__SehStoreFrameGlobals",
        "void CRT__SehStoreFrameGlobals(void)",
        ("DAT_006532d8", "DAT_006532d4", "DAT_006532dc", "_longjmp"),
    ),
    "0x0055da76": (
        "CRT__InitRuntimeFromStoredFrameGlobals",
        "void CRT__InitRuntimeFromStoredFrameGlobals(void)",
        ("CRT__InitFloatConversionDispatchTable", "DAT_009d08b8", "CRT__InitFpuControlWord_0x10000_0x30000"),
    ),
    "0x0055da8d": (
        "CRT__InitFloatConversionDispatchTable",
        "void CRT__InitFloatConversionDispatchTable(void)",
        ("0x00653658", "__cfltcvt", "__fassign", "CRT__InsertDecimalSeparatorBeforeExponent"),
    ),
    "0x0055db72": (
        "CRT__EhVectorDestructorIterator_IfNoException",
        "void CRT__EhVectorDestructorIterator_IfNoException(void)",
        ("CRT__EhVectorDestructorIterator_WithUnwind", "EBP-0x1c", "eh_vector_destructor_iterator"),
    ),
    "0x0055dc8a": (
        "CRT__EhVectorConstructorIterator_Unwind",
        "void CRT__EhVectorConstructorIterator_Unwind(void)",
        ("eh_vector_constructor_iterator", "EBP-0x20", "partially constructed"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "crt-seh-runtime-head-wave878",
    "wave878-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "important-crt-runtime-infrastructure",
    "high-importance-low-local-evidence-density",
    "compiler-runtime",
    "crt-seh",
    "raw-commentless-head",
}

XREF_EXPECTATIONS = {
    "0x0055d731": ("0x005d0f2b", "<no_function>", "UNCONDITIONAL_CALL"),
    "0x0055d767": ("0x005607bb", "CRT__CallCatchBlock", "UNCONDITIONAL_CALL"),
    "0x0055d7e0": ("0x00560547", "CRT__ValidateCatchHandlersForThrow", "UNCONDITIONAL_CALL"),
    "0x0055da5e": ("0x005d0621", "_longjmp", "UNCONDITIONAL_CALL"),
    "0x0055da76": ("0x0055dd84", "CFastVB__RunStaticInitRangesWithOptionalCallback", "COMPUTED_CALL"),
    "0x0055da8d": ("0x0055da76", "CRT__InitRuntimeFromStoredFrameGlobals", "UNCONDITIONAL_CALL"),
    "0x0055db72": ("0x0055db5c", "CRT__EhVectorDestructorIterator_WithUnwind", "UNCONDITIONAL_CALL"),
    "0x0055dc8a": ("0x0055dc74", "eh_vector_constructor_iterator", "UNCONDITIONAL_CALL"),
}

CORE_ANCHORS = (
    TASK,
    "crt-seh-runtime-head-wave878",
    "0x0055d731 CRT__SehDispatchWithScopeTable_Thunk_0055d731",
    "0x0055d767 CRT__SehInvokeCallSettingFrame12",
    "0x0055d7e0 CRT__CallExceptionTranslator",
    "0x0055da5e CRT__SehStoreFrameGlobals",
    "0x0055da76 CRT__InitRuntimeFromStoredFrameGlobals",
    "0x0055da8d CRT__InitFloatConversionDispatchTable",
    "0x0055db72 CRT__EhVectorDestructorIterator_IfNoException",
    "0x0055dc8a CRT__EhVectorConstructorIterator_Unwind",
    "high-importance CRT/compiler runtime connector rows with low local evidence density, not low-importance filler",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime exception behavior proven",
    "runtime translator behavior proven",
    "runtime unwind behavior proven",
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
        "pre-xrefs.tsv": 522,
        "pre-instructions.tsv": 150,
        "pre-decompile/index.tsv": 8,
        "pre-context-metadata.tsv": 14,
        "pre-context-decompile/index.tsv": 14,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 522,
        "post-instructions.tsv": 150,
        "post-decompile/index.tsv": 8,
        "post-context-metadata.tsv": 14,
        "post-context-decompile/index.tsv": 14,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("Wave878 static read-back" in row.get("comment", ""), f"missing Wave878 comment at {address}", failures)
            for token in tokens:
                require(contains_token(row.get("comment", ""), token), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing post tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing post decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    xref_text = read_text(BASE / "post-xrefs.tsv")
    for address, (from_addr, from_function, ref_type) in XREF_EXPECTATIONS.items():
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == from_addr
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing xref {from_addr} -> {address}",
            failures,
        )
        require(from_function in xref_text, f"missing xref function token: {from_function}", failures)

    scope_thunk_xrefs = [
        row for row in xrefs if normalize_address(row.get("target_addr", "")) == "0x0055d731"
    ]
    require(len(scope_thunk_xrefs) == 512, "scope-dispatch thunk xref count mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 522 rows",
        "post-instructions.log": "Wrote 150 function-body instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-context-metadata.log": "targets=14 found=14 missing=0",
        "post-context-decompile.log": "targets=14 dumped=14 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=5901",
        "queue-probe.log": "Commentless functions: 212",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave878.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave878_queue_probe.log",
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
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 212, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0055dcb0", "raw head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "OID__AcosWrapper", "raw head name mismatch", failures)

    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 5901, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5901, "strict clean count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172690311 or backup.get("totalBytes") == 172690311.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        CRT_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-crt-seh-runtime-head-wave878")
        == r"py -3 tools\ghidra_crt_seh_runtime_head_wave878_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave878 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20533 for row in attempts), "missing Wave878 attempt row", failures)


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
        print("Wave878 CRT/SEH runtime-head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave878 CRT/SEH runtime-head probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
