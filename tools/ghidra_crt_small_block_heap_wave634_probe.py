#!/usr/bin/env python3
"""Validate Wave634 CRT small-block heap Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave634-crt-small-block-heap"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_small_block_heap_wave634_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CRT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "crt-seh.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"

TARGETS = {
    "0x00566294": (
        "CRT__InitializeHeapSubsystem",
        "int __cdecl CRT__InitializeHeapSubsystem(int useSerializedHeap)",
        ("heap bootstrap called from entry", "CRT__SelectHeapStrategy", "Static heap bootstrap evidence only"),
        ("crt-runtime", "heap", "heap-bootstrap"),
    ),
    "0x005662f1": (
        "CRT__InitSmallBlockHeap",
        "int __cdecl CRT__InitSmallBlockHeap(int smallBlockByteLimit)",
        ("strategy 3 small-block heap table", "0x140-byte", "Static table-initialization evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "heap-bootstrap"),
    ),
    "0x00566339": (
        "CRT__FindSmallBlockHeapEntryForPtr",
        "void * __cdecl CRT__FindSmallBlockHeapEntryForPtr(void * userPtr)",
        ("searches the strategy 3 region table", "0x100000-byte", "Static pointer-range evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "region-table"),
    ),
    "0x00566364": (
        "CRT__SmallBlockHeapFreeBlock",
        "void __cdecl CRT__SmallBlockHeapFreeBlock(void * heapEntry, void * userPtr)",
        ("frees a strategy 3 small-block allocation", "VirtualFree/HeapFree", "Static allocator evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "free"),
    ),
    "0x0056668d": (
        "CRT__SbHeapAllocBlock",
        "void * __cdecl CRT__SbHeapAllocBlock(uint byteCount)",
        ("allocates from the strategy 3 small-block heap", "splits the chosen free chunk", "Static allocation evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "allocation"),
    ),
    "0x00566996": (
        "CRT__SbHeapGrowRegionTable",
        "void * __cdecl CRT__SbHeapGrowRegionTable(void)",
        ("grows or appends a strategy 3 region-table entry", "0x100000-byte virtual address range", "Static region-table evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "region-table"),
    ),
    "0x00566a47": (
        "CRT__SbHeapCommitRegion",
        "int __cdecl CRT__SbHeapCommitRegion(void * heapEntry)",
        ("commits a page inside a strategy 3 reserved region", "0x8000-byte page", "Static page-commit evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "virtualalloc"),
    ),
    "0x00566b42": (
        "CRT__SmallBlockHeapReallocInPlace",
        "int __cdecl CRT__SmallBlockHeapReallocInPlace(void * heapEntry, void * userPtr, uint byteCount)",
        ("attempts an in-place strategy 3 small-block realloc", "original pointer can remain valid", "Static realloc evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "realloc"),
    ),
    "0x00566e38": (
        "CRT__SbHeapCreateRegionPool",
        "void * __cdecl CRT__SbHeapCreateRegionPool(void)",
        ("strategy 2 deferred small-block region pool", "0x400000-byte address range", "Static region-pool evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "region-pool"),
    ),
    "0x00566f7c": (
        "CRT__SmallBlockHeapReleaseRegion",
        "void __cdecl CRT__SmallBlockHeapReleaseRegion(void * regionHeader)",
        ("releases a strategy 2 region-pool header", "static sentinel state", "Static region-lifetime evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "region-pool"),
    ),
    "0x00566fd2": (
        "CRT__SmallBlockHeapDecommitPages",
        "void __cdecl CRT__SmallBlockHeapDecommitPages(int pageCount)",
        ("decommits up to pageCount free pages", "MEM_DECOMMIT", "Static page-decommit evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "virtualfree"),
    ),
    "0x00567094": (
        "CRT__SmallBlockHeapLocateBlock",
        "void * __cdecl CRT__SmallBlockHeapLocateBlock(void * userPtr, void * * outRegionHeader, void * * outPageBase)",
        ("locates a strategy 2 deferred small-block allocation", "writes the owning region header and page base", "Static locator evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "region-pool"),
    ),
    "0x005670eb": (
        "CRT__SbHeapReleasePageBlock",
        "void __cdecl CRT__SbHeapReleasePageBlock(void * regionHeader, void * pageBase, void * chunkHeader)",
        ("releases a strategy 2 page-local small-block chunk", "bounded decommit sweep", "Static page-free evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "free"),
    ),
    "0x00567130": (
        "CRT__SbHeapAllocDeferredBlock",
        "void * __cdecl CRT__SbHeapAllocDeferredBlock(uint requestedUnits)",
        ("allocates a strategy 2 deferred small-block chunk", "CRT__SbHeapAllocChunkFromRegion", "Static deferred-allocation evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "allocation"),
    ),
    "0x00567338": (
        "CRT__SbHeapAllocChunkFromRegion",
        "void * __cdecl CRT__SbHeapAllocChunkFromRegion(void * pageHeader, uint freeUnits, uint requestedUnits)",
        ("allocates a requested unit count", "byte-sized chunk markers", "Static page-local allocator evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "allocation", "name-corrected"),
    ),
    "0x0056745c": (
        "CRT__SbHeapResizeChunkInRegion",
        "int __cdecl CRT__SbHeapResizeChunkInRegion(void * regionHeader, void * pageBase, void * chunkHeader, uint requestedUnits)",
        ("resizes a page-local strategy 2 byte-map chunk", "following bytes are free", "Static page-local realloc evidence only"),
        ("crt-runtime", "heap", "small-block-heap", "realloc", "name-corrected"),
    ),
}

COMMON_TAGS = {"static-reaudit", "crt-small-block-heap-wave634", "retail-binary-evidence", "comment-hardened", "signature-hardened"}
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "crt identity proven",
    "crt version proven",
    "fully recovered",
    "fully reverse-engineered",
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


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        if token.replace("\\\\", "\\") not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY line")
        return {}
    values = {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-succeeded marker")
    if "LockException" in text:
        failures.append(f"{path.name} contains LockException")
    return values


def expect_summary(label: str, actual: dict[str, int], expected: dict[str, int], failures: list[str]) -> None:
    for key, value in expected.items():
        if actual.get(key) != value:
            failures.append(f"{label} expected {key}={value}, saw {actual.get(key)}")


def check_metadata(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-metadata.tsv")}
    if set(rows) != set(TARGETS):
        failures.append(f"post-metadata target set mismatch: {sorted(rows)}")
    for address, (name, signature, comment_tokens, _tags) in TARGETS.items():
        row = rows.get(address)
        if not row:
            continue
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        require_tokens(f"{address} comment", row["comment"], set(comment_tokens), failures)
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status is {row.get('status')}")


def check_tags(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-tags.tsv")}
    for address, (_name, _signature, _comment_tokens, tags) in TARGETS.items():
        row = rows.get(address)
        if not row:
            failures.append(f"{address} missing tag row")
            continue
        actual = {tag for tag in row["tags"].split(";") if tag}
        missing = (COMMON_TAGS | set(tags)) - actual
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")


def check_counts(failures: list[str]) -> None:
    checks = [
        (BASE / "post-metadata.tsv", 16, "metadata rows"),
        (BASE / "post-tags.tsv", 16, "tag rows"),
        (BASE / "post-xrefs.tsv", 31, "xref rows"),
        (BASE / "post-instructions.tsv", 1168, "instruction rows"),
    ]
    for path, expected, label in checks:
        rows = read_tsv_rows(path)
        if len(rows) != expected:
            failures.append(f"{label}: expected {expected}, saw {len(rows)}")
    decomp = read_text(BASE / "export-post-decompile.log")
    require_tokens("export-post-decompile.log", decomp, ("targets=16 dumped=16 missing=0 failed=0", "REPORT: Save succeeded"), failures)
    for address, (name, _signature, _comment_tokens, _tags) in TARGETS.items():
        file_name = f"{address[2:]}_{name}.c"
        if not (BASE / "post-decompile" / file_name).is_file():
            failures.append(f"missing decompile file: {file_name}")


def check_logs(failures: list[str]) -> None:
    dry = parse_log_summary(BASE / "apply-wave634-dry.log", failures)
    apply = parse_log_summary(BASE / "apply-wave634-apply.log", failures)
    final_dry = parse_log_summary(BASE / "apply-wave634-final-dry.log", failures)
    expect_summary(
        "dry",
        dry,
        {"updated": 0, "skipped": 16, "renamed": 0, "would_rename": 2, "signature_updated": 0, "varargs": 0, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "apply",
        apply,
        {"updated": 16, "skipped": 0, "renamed": 2, "would_rename": 0, "signature_updated": 16, "varargs": 0, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "final dry",
        final_dry,
        {"updated": 0, "skipped": 16, "renamed": 0, "would_rename": 0, "signature_updated": 0, "varargs": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    expected_quality = {
        "commentlessFunctionCount": 2723,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 926,
    }
    for key, value in expected_quality.items():
        if quality.get(key) != value:
            failures.append(f"queue {key} expected {value}, saw {quality.get(key)}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions expected 6093, saw {queue.get('totalFunctions')}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x00567505" or head["name"] != "CRT__WriteFdTextMode_Locking_00567505":
        failures.append(f"unexpected next queue head: {head}")

    backup = read_json(BASE / "backup-summary.json")
    require_tokens(
        "backup summary",
        json.dumps(backup),
        ("[maintainer-local-ghidra-backup-root]\\BEA_20260520-104156_post_wave634_crt_small_block_heap_verified",),
        failures,
    )
    if backup.get("fileCount") != 19:
        failures.append(f"backup file count unexpected: {backup}")
    if int(backup.get("totalBytes", -1)) != 162401159:
        failures.append(f"backup byte count unexpected: {backup}")
    if backup.get("diffCount") != 0:
        failures.append(f"backup diffCount is {backup.get('diffCount')}")


def check_docs(failures: list[str]) -> None:
    expected_tokens = (
        "Wave634",
        "CRT__InitializeHeapSubsystem",
        "CRT__SbHeapAllocBlock",
        "CRT__SbHeapCreateRegionPool",
        "CRT__SbHeapResizeChunkInRegion",
        "3370",
        "2723",
        "3316/6093 = 54.43%",
        "0x00567505 CRT__WriteFdTextMode_Locking_00567505",
        "[maintainer-local-ghidra-backup-root]\\BEA_20260520-104156_post_wave634_crt_small_block_heap_verified",
    )
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, CRT_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        require_tokens(path.name, text, expected_tokens, failures)
        for token in OVERCLAIM_TOKENS:
            if token in text.lower():
                failures.append(f"{path.name} contains overclaim token: {token}")
    require_tokens("package.json", read_text(PACKAGE_JSON), ("test:ghidra-crt-small-block-heap-wave634",), failures)
    require_tokens("ledger", read_text(LEDGER), ("Wave634 CRT small-block heap hardening", "3316/6093 = 54.43%"), failures)
    require_tokens("attempt log", read_text(ATTEMPT_LOG), ("\"attempt_id\":20289", "Wave634 CRT small-block heap hardening"), failures)
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20290:
        failures.append(f"tracking next_attempt_id expected 20290, saw {tracking.get('next_attempt_id')}")
    require_tokens("tracking", json.dumps(tracking), ("Wave634 CRT small-block heap hardening",), failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_metadata(failures)
    check_tags(failures)
    check_counts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Exit nonzero on validation failures.")
    args = parser.parse_args()

    failures = run_check()
    if failures:
        print("Wave634 CRT small-block heap probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave634 CRT small-block heap probe: PASS")
    print("Verified 16 saved metadata rows, 16 tag rows, 31 xref rows, 1168 instruction rows, 16 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
