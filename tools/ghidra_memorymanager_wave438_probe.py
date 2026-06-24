#!/usr/bin/env python3
"""Validate Wave438 MemoryManager/CMemoryHeap Ghidra corrections."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave438-memorymanager-current"

COMMON_TAGS = {"static-reaudit", "memorymanager-wave438", "retail-binary-evidence"}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 10,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str] | None = None,
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens or [],
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004a13b0": target(
        "CMemoryHeap__Init",
        "int __thiscall CMemoryHeap__Init(void * this, uint heap_size, uint tiny_heap_size, char * name, int support_small_allocs)",
        ["CMemoryHeap::Init", "MEM_MANAGER__Init", "DAT_009c3df0", "0x4f69ea21", "remain unproven"],
        ["cmemoryheap", "allocator-init", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CMemoryHeap__Alloc(this,tiny_heap_size", "0x4f69ea21"],
    ),
    "0x004a15a0": target(
        "CMemoryHeap__ReallocTiny",
        "int __thiscall CMemoryHeap__ReallocTiny(void * this, void * mem, uint new_size, void * * out_result)",
        ["CMemoryHeap::ReallocTiny", "CPolyBucket__ReallocFromPool", "+0x8c0..+0x8c8", "out_result", "remain unproven"],
        ["cmemoryheap", "tiny-heap", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["void **out_result", "CMemoryHeap__Alloc(this,new_size"],
    ),
    "0x004a1640": target(
        "CMemoryHeap__Cleanup",
        "void __thiscall CMemoryHeap__Cleanup(void * this, int needs_mutex)",
        ["CMemoryHeap::Cleanup", "needs_mutex", "CMemoryHeap__SetMerge", "MEM_MANAGER__Cleanup", "remain unproven"],
        ["cmemoryheap", "cleanup-coalesce", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["ReleaseMutex((HANDLE)((int)this + 0x8bc))"],
    ),
    "0x004a17b0": target(
        "CMemoryHeap__Shutdown",
        "void __fastcall CMemoryHeap__Shutdown(void * this)",
        ["CMemoryHeap::Shutdown", "CDXEngine__ResetLandscapeCellManager", "DAT_009c3df0", "+0x8bc", "remain unproven"],
        ["cmemoryheap", "shutdown", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CRT__FreeBase", "ReleaseMutex(*(HANDLE *)((int)this + 0x8bc))"],
    ),
    "0x004a1810": target(
        "CMemoryHeap__Alloc",
        "void * __thiscall CMemoryHeap__Alloc(void * this, uint size, int memory_type, char * filename, uint line)",
        ["CMemoryHeap::Alloc", "+0x8bc", "Out of memory", "CMemoryHeap__Cleanup", "remain unproven"],
        ["cmemoryheap", "allocator", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CMemoryHeap__Cleanup(this,0)", "CConsole__Printf", "CMemoryHeap__AddToFreeList(this"],
    ),
    "0x004a1c30": target(
        "CMemoryHeap__ReleaseMutexUnwindCleanup",
        "void __fastcall CMemoryHeap__ReleaseMutexUnwindCleanup(void * * mutex_handle_ptr)",
        ["EH unwind cleanup helper", "0x005d3540", "0x005d3560", "not a source-level", "remain unproven"],
        ["cmemoryheap", "eh-cleanup", "mutex-release", "renamed", "signature-corrected", "comment-hardened"],
        ["ReleaseMutex(*mutex_handle_ptr)"],
    ),
    "0x004a1c40": target(
        "CMemoryHeap__ReAlloc",
        "void * __thiscall CMemoryHeap__ReAlloc(void * this, void * block, uint new_size)",
        ["CMemoryHeap::ReAlloc", "CPolyBucket__ReallocFromPool", "block+0x10", "CMemoryHeap__Free", "remain unproven"],
        ["cmemoryheap", "realloc", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CMemoryHeap__Alloc(this,new_size", "CMemoryHeap__Free(this,block)"],
    ),
    "0x004a1ca0": target(
        "CMemoryHeap__Free",
        "void __thiscall CMemoryHeap__Free(void * this, void * block)",
        ["CMemoryHeap::Free", "OID__FreeObject", "CMemoryHeap__AddToFreeList", "releases the mutex", "remain unproven"],
        ["cmemoryheap", "free", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CMemoryHeap__AddToFreeList(this,block)", "ReleaseMutex(hHandle)"],
    ),
    "0x004a1d60": target(
        "CMemoryHeap__AddToFreeList",
        "void __thiscall CMemoryHeap__AddToFreeList(void * this, void * block)",
        ["CMemoryHeap::AddToFreeList", "0x100", "mMerge", "reinserts by block size", "remain unproven"],
        ["cmemoryheap", "free-list", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CMemoryHeap__AddToFreeList", "void * block"],
    ),
    "0x004a1ea0": target(
        "CMemoryHeap__SetMerge",
        "void __thiscall CMemoryHeap__SetMerge(void * this, int merge_enabled)",
        ["CMemoryHeap::SetMerge", "CLTShell shutdown", "CMemoryHeap__Cleanup", "+0x874", "remain unproven"],
        ["cmemoryheap", "set-merge", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CMemoryHeap__Cleanup(this,1)", "merge_enabled"],
    ),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully re'ed",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "decompile_after"
    if not directory.is_dir():
        return ""
    prefix = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{prefix}_*.c"))
    return read_text(matches[0]) if matches else ""


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ["updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def check_verify_log(base: Path, failures: list[str]) -> None:
    text = read_text(base / "apply_verify_dry.log")
    if not text:
        failures.append("apply_verify_dry.log: missing or empty")
        return
    summary = parse_summary(text)
    if summary != EXPECTED_VERIFY_DRY:
        failures.append(f"apply_verify_dry.log: summary mismatch expected {EXPECTED_VERIFY_DRY}, got {summary}")
    for token in ("FAIL:", "Exception", "LockException"):
        if token in text:
            failures.append(f"apply_verify_dry.log: unexpected failure token {token!r}")
    if "REPORT: Save succeeded" not in text:
        failures.append("apply_verify_dry.log: missing Ghidra save-success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "metadata_after.tsv")
    tags = read_tsv(base / "tags_after.tsv")

    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing metadata_after row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')!r}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: signature mismatch {row.get('signature')!r}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        lowered_comment = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered_comment:
                failures.append(f"{address}: overclaim token present {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing tags_after row")
        else:
            actual_tags = {item.strip() for item in re.split(r"[;,]", tag_row.get("tags", "")) if item.strip()}
            missing_tags = sorted(set(spec["tags"]) - actual_tags)  # type: ignore[arg-type]
            if missing_tags:
                failures.append(f"{address}: missing tags {missing_tags}")

        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing decompile_after")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def run(base: Path) -> dict[str, object]:
    failures: list[str] = []
    check_verify_log(base, failures)
    check_metadata(base, failures)
    return {
        "status": "PASS" if not failures else "FAIL",
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "base": str(base.relative_to(ROOT)) if base.is_relative_to(ROOT) else str(base),
        "targetCount": len(TARGETS),
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    base = args.base if args.base.is_absolute() else ROOT / args.base
    result = run(base)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Wave438 MemoryManager probe: {result['status']}")
        print(f"Base: {result['base']}")
        print(f"Targets: {result['targetCount']}")
        for failure in result["failures"]:  # type: ignore[index]
            print(f"- {failure}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
