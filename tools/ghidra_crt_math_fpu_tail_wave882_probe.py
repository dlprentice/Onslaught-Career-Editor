#!/usr/bin/env python3
"""Validate Wave882 CRT math/FPU tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave882-crt-math-fpu-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_math_fpu_tail_wave882_2026-05-26.md"
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

TASK = "Wave882 CRT math/FPU tail"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-002800_post_wave882_crt_math_fpu_tail_verified"
NEXT_HEAD = "0x00563ad3 CRT__FpuTransDispatch2_ClearStatusAndHandle"
STRICT_PROXY = "5943/6113 = 97.22%"

TARGETS = {
    "0x00561530": ("CRT__ReportMathErrorAndRestoreControlWord_00561530", "int CRT__ReportMathErrorAndRestoreControlWord_00561530(void)", ("CRT__HandleFloatingPointException", "control-word", "CRT__PowCoreWithFpuGuards")),
    "0x00561590": ("CRT__Exp2FromFpuCore_00561590", "int CRT__Exp2FromFpuCore_00561590(void)", ("FRNDINT", "F2XM1", "FSCALE")),
    "0x005615a5": ("CRT__SetFpuControlWordMasked_005615a5", "void CRT__SetFpuControlWordMasked_005615a5(void)", ("0x300", "0x7f", "FLDCW")),
    "0x005615bc": ("CRT__MapExponentFlagToClassCode_005615bc", "int CRT__MapExponentFlagToClassCode_005615bc(void)", ("0x80000", "0x005e5bf0", "class code")),
    "0x005621b9": ("CRT__UnlockByIndex9_005621b9", "void CRT__UnlockByIndex9_005621b9(void)", ("CRT__UnlockByIndex(9)", "CRT__ReallocBase")),
    "0x00562307": ("CRT__UnlockByIndex9_00562307", "void CRT__UnlockByIndex9_00562307(void)", ("CRT__UnlockByIndex(9)", "CRT__ReallocBase")),
    "0x005623c7": ("CRT__UnlockHeap9_SbHeapMsizePath", "void CRT__UnlockHeap9_SbHeapMsizePath(void)", ("CRT__UnlockByIndex(9)", "CRT__MsizeByPointer")),
    "0x00562442": ("CRT__UnlockHeap9_DeferredMsizePath", "void CRT__UnlockHeap9_DeferredMsizePath(void)", ("CRT__UnlockByIndex(9)", "CRT__MsizeByPointer")),
    "0x0056249f": ("CRT__HandleFloatingPointExceptionByFlags", "int CRT__HandleFloatingPointExceptionByFlags(void)", ("CRT__AdjustFloatingPointForFormatFlags", "CRT__RaiseFloatingPointException", "CRT__GetFpuControlWord")),
    "0x00562537": ("CRT__RaiseFloatingPointException", "int CRT__RaiseFloatingPointException(void)", ("RaiseException", "0xc000008f", "0xc0000093", "0xc0000091", "0xc000008e", "0xc0000090")),
    "0x00562c59": ("CRT__FpuStatusWordToInt_00562c59", "int CRT__FpuStatusWordToInt_00562c59(void)", ("FPU status word", "0x0056262d")),
    "0x00562c67": ("CRT__FpuStatusWordToInt_00562c67", "int CRT__FpuStatusWordToInt_00562c67(void)", ("FPU status word", "0x0056273d")),
    "0x00562c76": ("CRT__GetFpuControlWord", "int CRT__GetFpuControlWord(void)", ("FPU control word", "CRT__RoundDoubleWithFpuChecks", "CRT__HandleFloatingPointException")),
    "0x00562c99": ("CRT__ReturnVoid", "void CRT__ReturnVoid(void)", ("return-only", "CRT__AdjustFloatingPointForFormatFlags")),
}

COMMON_TAGS = {
    "static-reaudit",
    "crt-math-fpu-tail-wave882",
    "wave882-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "important-crt-runtime-infrastructure",
    "high-importance-low-local-evidence-density",
    "compiler-runtime",
    "crt-runtime",
    "fpu-runtime",
    "math-exception-runtime",
    "raw-commentless-head",
}

XREF_COUNTS = {
    "0x00561530": 2,
    "0x00561590": 1,
    "0x005615a5": 3,
    "0x005615bc": 2,
    "0x005621b9": 1,
    "0x00562307": 1,
    "0x005623c7": 1,
    "0x00562442": 1,
    "0x0056249f": 2,
    "0x00562537": 2,
    "0x00562c59": 1,
    "0x00562c67": 1,
    "0x00562c76": 11,
    "0x00562c99": 5,
}

CORE_ANCHORS = (
    TASK,
    "crt-math-fpu-tail-wave882",
    "0x00561530 CRT__ReportMathErrorAndRestoreControlWord_00561530",
    "0x00561590 CRT__Exp2FromFpuCore_00561590",
    "0x005615a5 CRT__SetFpuControlWordMasked_005615a5",
    "0x005615bc CRT__MapExponentFlagToClassCode_005615bc",
    "0x0056249f CRT__HandleFloatingPointExceptionByFlags",
    "0x00562537 CRT__RaiseFloatingPointException",
    "0x00562c76 CRT__GetFpuControlWord",
    "0x00562c99 CRT__ReturnVoid",
    "0xc000008f",
    "0xc0000093",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime floating-point behavior proven",
    "runtime exception behavior proven",
    "runtime heap-lock behavior proven",
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
        "pre-metadata.tsv": 14,
        "pre-tags.tsv": 14,
        "pre-xrefs.tsv": 34,
        "pre-instructions.tsv": 434,
        "pre-decompile/index.tsv": 14,
        "pre-context-metadata.tsv": 12,
        "pre-context-decompile/index.tsv": 12,
        "post-metadata.tsv": 14,
        "post-tags.tsv": 14,
        "post-xrefs.tsv": 34,
        "post-instructions.tsv": 434,
        "post-decompile/index.tsv": 14,
        "post-context-metadata.tsv": 12,
        "post-context-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    xref_counts: dict[str, int] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        address = normalize_address(row["target_addr"])
        xref_counts[address] = xref_counts.get(address, 0) + 1

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("Wave882 static read-back" in comment, f"missing Wave882 comment at {address}", failures)
            for token in comment_tokens:
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

        require(xref_counts.get(address) == XREF_COUNTS[address], f"xref count mismatch at {address}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-context-decompile" / "index.tsv")}
    require(context.get("0x0055fa62", {}).get("status") == "FAILED", "expected pow-core context decompile-limit failure missing", failures)
    for address in (
        "0x00561679",
        "0x0055dccd",
        "0x0055f39d",
        "0x0056202e",
        "0x0056235d",
        "0x0055dfe7",
        "0x0055eb3d",
        "0x0056244b",
        "0x005627ea",
        "0x00562a01",
        "0x00569cc1",
    ):
        require(context.get(address, {}).get("status") == "OK", f"context decompile missing at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=14 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=14 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=14 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=14 found=14 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=14 missing=0",
        "post-xrefs.log": "Wrote 34 rows",
        "post-instructions.log": "Wrote 434 function-body instruction rows",
        "post-decompile.log": "targets=14 dumped=14 missing=0 failed=0",
        "post-context-metadata.log": "targets=12 found=12 missing=0",
        "post-context-decompile.log": "targets=12 dumped=11 missing=0 failed=1",
        "quality-refresh.log": "total_functions=6113 commented_functions=5943",
        "queue-probe.log": "Commentless functions: 170",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave882.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave882_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BAD:"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 170, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 5943, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5943, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00563ad3", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CRT__FpuTransDispatch2_ClearStatusAndHandle", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172755847 or backup.get("totalBytes") == 172755847.0, "backup byte count mismatch", failures)
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
        CRT_DOC,
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
        scripts.get("test:ghidra-crt-math-fpu-tail-wave882") == r"py -3 tools\ghidra_crt_math_fpu_tail_wave882_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave882 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20537 for row in attempts), "missing Wave882 attempt row", failures)


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
        print("Wave882 CRT math/FPU tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave882 CRT math/FPU tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
