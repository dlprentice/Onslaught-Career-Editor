#!/usr/bin/env python3
"""Validate Wave1042 memory-heap allocator review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1042-memory-heap-allocator-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_memory_heap_allocator_review_wave1042_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1042_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
MEMORY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MemoryManager.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-094520_post_wave1042_memory_heap_allocator_review_verified"

TARGETS = {
    "0x004a13b0": ("CMemoryHeap__Init", "int __thiscall CMemoryHeap__Init(void * this, uint heap_size, uint tiny_heap_size, char * name, int support_small_allocs)"),
    "0x004a15a0": ("CMemoryHeap__ReallocTiny", "int __thiscall CMemoryHeap__ReallocTiny(void * this, void * mem, uint new_size, void * * out_result)"),
    "0x004a1640": ("CMemoryHeap__Cleanup", "void __thiscall CMemoryHeap__Cleanup(void * this, int needs_mutex)"),
    "0x004a1810": ("CMemoryHeap__Alloc", "void * __thiscall CMemoryHeap__Alloc(void * this, uint size, int memory_type, char * filename, uint line)"),
    "0x004a1c40": ("CMemoryHeap__ReAlloc", "void * __thiscall CMemoryHeap__ReAlloc(void * this, void * block, uint new_size)"),
    "0x004a1ca0": ("CMemoryHeap__Free", "void __thiscall CMemoryHeap__Free(void * this, void * block)"),
    "0x004a1d60": ("CMemoryHeap__AddToFreeList", "void __thiscall CMemoryHeap__AddToFreeList(void * this, void * block)"),
    "0x004a1ea0": ("CMemoryHeap__SetMerge", "void __thiscall CMemoryHeap__SetMerge(void * this, int merge_enabled)"),
}

CONTEXT_TARGETS = {
    "0x00548f90": "CDXMemoryManager__Init",
    "0x005490e0": "CDXMemoryManager__Alloc",
    "0x005491b0": "CDXMemoryManager__ReAlloc",
    "0x00549220": "CDXMemoryManager__Free",
    "0x00549270": "MEM_MANAGER__Cleanup",
    "0x00549400": "CMemoryManager__DeleteTagList",
    "0x004f00e0": "CLTShell__ShutdownRuntimeAndReleaseResources",
    "0x0046c990": "CGame__Shutdown",
}

DOC_TOKENS = (
    "Wave1042",
    "memory-heap-allocator-review-wave1042",
    "0x004a13b0 CMemoryHeap__Init",
    "0x004a1810 CMemoryHeap__Alloc",
    "0x004a1ca0 CMemoryHeap__Free",
    "0x004a1ea0 CMemoryHeap__SetMerge",
    "DAT_009c3df0",
    "0x4f69ea21",
    "0x00548f90 CDXMemoryManager__Init",
    "0x005490e0 CDXMemoryManager__Alloc",
    "735/1408 = 52.20%",
    "968/1493 = 64.84%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime allocator behavior proven",
    "runtime out-of-memory behavior proven",
    "complete concrete cmemoryheap layout proven",
    "complete concrete cmemoryblock layout proven",
    "complete concrete cdxmemorymanager layout proven",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
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


def read_json(path: Path):
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 28,
        "instructions.tsv": 934,
        "decompile/index.tsv": 8,
        "context-metadata.tsv": 8,
        "context-tags.tsv": 8,
        "context-xrefs.tsv": 2260,
        "context-instructions.tsv": 376,
        "context-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    instructions_text = read_text(BASE / "instructions.tsv")
    xref_text = read_text(BASE / "xrefs.tsv")

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave438", "source parity", "rebuild parity"):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            tag_set = set(tag_row.get("tags", "").split(";"))
            for tag in ("cmemoryheap", "memorymanager-wave438", "retail-binary-evidence", "source-parity", "static-reaudit"):
                require(tag in tag_set, f"missing tag at {address}: {tag}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)

    for token in (
        "DAT_009c3df0",
        "0x4f69ea21",
        "CMemoryHeap__Alloc",
        "CMemoryHeap__Cleanup",
        "CMemoryHeap__AddToFreeList",
        "CMemoryManager__DumpMemory",
        "Out_of_memory",
    ):
        require(token in instructions_text or token in read_text(BASE / "decompile" / "004a1810_CMemoryHeap__Alloc.c"), f"missing instruction/decompile token: {token}", failures)

    for token in (
        "00548f90\tCDXMemoryManager__Init",
        "005490e0\tCDXMemoryManager__Alloc",
        "005491b0\tCDXMemoryManager__ReAlloc",
        "00549220\tCDXMemoryManager__Free",
        "00549270\tMEM_MANAGER__Cleanup",
        "0046c990\tCGame__Shutdown",
        "004f00e0\tCLTShell__ShutdownRuntimeAndReleaseResources",
    ):
        require(token in xref_text, f"missing xref token: {token}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None and row.get("name") == name, f"context metadata mismatch at {address}", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected_logs = {
        "metadata.log": "targets=8 found=8 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "xrefs.log": "Wrote 28 rows",
        "instructions.log": "Wrote 934 function-body instruction rows",
        "decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "context-metadata.log": "targets=8 found=8 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "context-xrefs.log": "Wrote 2260 rows",
        "context-instructions.log": "Wrote 376 function-body instruction rows",
        "context-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "failed=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    quality_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1042.log")
    require("total_functions=6238 commented_functions=6238" in quality_log, "quality refresh token mismatch", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", -1)) == 174263175, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        MEMORY_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        lowered = text.lower()
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-memory-heap-allocator-review-wave1042")
        == r"py -3 tools\ghidra_memory_heap_allocator_review_wave1042_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1042-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1042 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1042 memory heap allocator review" for row in ledger_rows), "missing ledger row", failures)
    require(
        any(row.get("task") == "Wave1042 memory heap allocator review" and row.get("attempt_id") == 20624 for row in attempt_rows),
        "missing attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_queue(failures)
    check_docs(failures)

    if failures:
        print("Wave1042 memory-heap allocator review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1042 memory-heap allocator review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
