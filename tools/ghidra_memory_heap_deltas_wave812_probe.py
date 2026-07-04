#!/usr/bin/env python3
"""Validate Wave812 memory-heap delta read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave812-cltshell-heap-deltas"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_memory_heap_deltas_wave812_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MEMORY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MemoryManager.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

ADDRESS = "0x004a25c0"
OLD_NAME = "CLTShell__ValidateAndRollHeapDeltas"
NAME = "CMemoryHeap__CalcAndShowDeltas"
SIGNATURE = "void __thiscall CMemoryHeap__CalcAndShowDeltas(void * this)"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-132640_post_wave812_memory_heap_deltas_verified"
NEXT_HEAD = "0x004a52b0 CMesh__ClearAllUsageMarkers"

COMMON_TAGS = {
    "static-reaudit",
    "memory-heap-deltas-wave812",
    "wave812-readback-verified",
    "retail-binary-evidence",
    "renamed",
    "signature-verified",
    "comment-hardened",
    "raw-commentless-tail",
    "memory-manager",
    "heap-deltas",
}

DOC_TOKENS = (
    "Wave812 memory heap deltas",
    "memory-heap-deltas-wave812",
    f"{ADDRESS} {NAME}",
    OLD_NAME,
    "0x0062f6d0",
    "Heap Delta",
    "0x009c2dd0",
    "0x005492e6",
    "this+0x214",
    "this+0xae0",
    "this+0x13ac",
    "5587/6098 = 91.62%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime trace/delta behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 3,
        "pre-instructions.tsv": 241,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 3,
        "pre-context-decompile/index.tsv": 3,
        "pre-caller-instructions.tsv": 81,
        "string-0062f6d0.tsv": 1,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 3,
        "post-instructions.tsv": 241,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 3,
        "post-context-decompile/index.tsv": 3,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre = read_tsv(BASE / "pre-metadata.tsv")[0]
    post = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(pre["address"]) == ADDRESS, "pre address mismatch", failures)
    require(pre["name"] == OLD_NAME, "pre name mismatch", failures)
    require(pre["signature"] == f"void __thiscall {OLD_NAME}(void * this)", "pre signature mismatch", failures)
    require(not pre.get("comment", "").strip(), "pre row should be commentless", failures)
    require(normalize_address(post["address"]) == ADDRESS, "post address mismatch", failures)
    require(post["name"] == NAME, "post name mismatch", failures)
    require(post["signature"] == SIGNATURE, "post signature mismatch", failures)
    require(post["status"] == "OK", "post status mismatch", failures)

    comment = post.get("comment", "")
    for token in (
        "Wave812 static read-back hardening",
        OLD_NAME,
        "this+0x214",
        "this+0xae0",
        "this+0x13ac",
        "0x81 memory-type counters",
        "0x009c2dd0",
        "0x0062f6d0",
        "Heap Delta",
        "runtime trace/delta behavior",
        "rebuild parity remain deferred",
    ):
        require(token in comment, f"missing post comment token: {token}", failures)

    tags = set(read_tsv(BASE / "post-tags.tsv")[0].get("tags", "").split(";"))
    require(COMMON_TAGS.issubset(tags), f"missing tags: {COMMON_TAGS - tags}", failures)

    string_row = read_tsv(BASE / "string-0062f6d0.tsv")[0]
    require(string_row.get("cstring") == r"Heap Delta: %-32s : %15d bytes : %15d blocks\x0a", "heap delta string mismatch", failures)

    decomp = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(decomp["name"] == NAME, "post decompile name mismatch", failures)
    require(decomp["signature"] == SIGNATURE, "post decompile signature mismatch", failures)
    require(decomp["status"] == "OK", "post decompile status mismatch", failures)
    decomp_text = read_text(BASE / "post-decompile" / "004a25c0_CMemoryHeap__CalcAndShowDeltas.c")
    for token in (
        "CMemoryHeap__CalcAndShowDeltas(void *this)",
        "&DAT_009c2dd0",
        "s_Heap_Delta",
        "DebugTrace(local_190)",
        "0x9c3df0",
        "iVar1 = 0x81",
    ):
        require(token in decomp_text, f"missing decompile token: {token}", failures)

    caller_text = read_text(BASE / "post-context-decompile" / "005492d0_CDXMemoryManager__CalcAndShowDeltas.c")
    for token in (
        "CMemoryHeap__CalcAndShowDeltas((void *)((int)this + 0x214))",
        "CMemoryHeap__CalcAndShowDeltas((void *)((int)this + 0xae0))",
        "CMemoryHeap__CalcAndShowDeltas((void *)((int)this + 0x13ac))",
    ):
        require(token in caller_text, f"missing caller decompile token: {token}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    xref_from = {normalize_address(row["from_addr"]) for row in xrefs}
    for addr in ("0x005492e6", "0x005492f1", "0x005492fc"):
        require(addr in xref_from, f"missing xref from {addr}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=1 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 3 rows",
        "post-instructions.log": "Wrote 241 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=3 found=3 missing=0",
        "post-context-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5587",
        "queue-probe.log": "Commentless functions: 511",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave812.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave812_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 511, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5587, "quality TSV commented count mismatch", failures)
    require(strict == 5587, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004a52b0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CMesh__ClearAllUsageMarkers", "raw commentless head name mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171346823 or backup.get("totalBytes") == 171346823.0, "backup byte count mismatch", failures)
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
        MEMORY_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-memory-heap-deltas-wave812") == r"py -3 tools\ghidra_memory_heap_deltas_wave812_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave812 memory heap deltas" for row in ledger_rows), "missing Wave812 ledger row", failures)
    require(any(row.get("task") == "Wave812 memory heap deltas" and row.get("attempt_id") == 20467 for row in attempts), "missing Wave812 attempt row", failures)


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
        print("Wave812 memory-heap-deltas probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave812 memory-heap-deltas probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
