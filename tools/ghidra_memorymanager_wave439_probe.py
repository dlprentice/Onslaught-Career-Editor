#!/usr/bin/env python3
"""Validate Wave439 MemoryManager tail Ghidra corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave439-memorymanager-tail-current"

COMMON_TAGS = {"static-reaudit", "memorymanager-wave439", "retail-binary-evidence"}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 13,
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
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004a1390": target(
        "CMemoryHeap__ctor",
        "void * __thiscall CMemoryHeap__ctor(void * this)",
        ["CMemoryHeap constructor", "CDXMemoryManager__ctor", "+0x8bc", "remain unproven"],
        ["cmemoryheap", "constructor", "mutex", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CreateMutexA", "+0x8bc"],
    ),
    "0x004a1570": target(
        "CMemoryHeap__FreeTiny",
        "int __thiscall CMemoryHeap__FreeTiny(void * this, void * mem)",
        ["CMemoryHeap::FreeTiny", "+0x8c0..+0x8c8", "+0x8c4", "remain unproven"],
        ["cmemoryheap", "tiny-heap", "free", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CMemoryHeap__FreeTiny", "+0x8c4"],
    ),
    "0x004a1f60": target(
        "CMemoryHeap__OutputStats",
        "void __thiscall CMemoryHeap__OutputStats(void * this, char * filename)",
        ["CMemoryHeap::OutputStats", "data\\Memory", "CDXMemBuffer", "remain unproven"],
        ["cmemoryheap", "stats", "file-output", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["DXMemBuffer__WriteBytes", "data_Memory__s"],
    ),
    "0x004a2190": target(
        "CMemoryHeap__PrintStats",
        "void __thiscall CMemoryHeap__PrintStats(void * this)",
        ["CMemoryHeap::PrintStats", "debug font", "CDXMemoryManager__PrintStats", "remain unproven"],
        ["cmemoryheap", "stats", "debug-font", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CDXFont__DrawText", "CPlatform__Font"],
    ),
    "0x004a2460": target(
        "CMemoryHeap__LogStats",
        "void __thiscall CMemoryHeap__LogStats(void * this)",
        ["CMemoryHeap::LogStats", "CDXMemoryManager__LogDebugStats", "nonzero per-type", "remain unproven"],
        ["cmemoryheap", "stats", "debug-log", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CConsole__Printf", "DebugTrace"],
    ),
    "0x004a2660": target(
        "CMemoryHeap__DumpMap",
        "void __thiscall CMemoryHeap__DumpMap(void * this, void * mem_buffer, int heap_index)",
        ["CMemoryHeap::DumpMap", "CMemoryManager__DumpMemory", "block validity", "remain unproven"],
        ["cmemoryheap", "dump-map", "memory-dump", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["DXMemBuffer__WriteBytes", "0x4f69ea21"],
    ),
    "0x004a2a20": target(
        "CMemoryManager__FlagAsBaseSet",
        "void __thiscall CMemoryManager__FlagAsBaseSet(void * this)",
        ["CMemoryManager::FlagAsBaseSet", "base-set bit", "CLTShell", "remain unproven"],
        ["cmemorymanager", "base-set", "debug-memory", "renamed", "signature-corrected", "comment-hardened", "source-parity"],
        ["| 2", "CMemoryManager__FlagAsBaseSet"],
    ),
    "0x004a2a80": target(
        "CMemoryManager__DumpMemory",
        "void __thiscall CMemoryManager__DumpMemory(void * this, char * trace_name)",
        ["CMemoryManager::DumpMemory", "MemoryDumps", "trace.no", "remain unproven"],
        ["cmemorymanager", "memory-dump", "renamed", "signature-corrected", "comment-hardened", "source-parity"],
        ["CMemoryHeap__DumpMap", "MemoryDumps_dump_d_mem"],
    ),
    "0x004a2ff0": target(
        "CMemoryBlock__SetBaseSet",
        "void __thiscall CMemoryBlock__SetBaseSet(void * this, int base_set)",
        ["CMemoryBlock::SetBaseSet", "bit 1", "CMemoryHeap__Alloc", "remain unproven"],
        ["cmemoryblock", "base-set", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["| 2", "0xfffffffd"],
    ),
    "0x00548d70": target(
        "CDXMemoryManager__ctor",
        "void * __thiscall CDXMemoryManager__ctor(void * this)",
        ["CDXMemoryManager::CDXMemoryManager", "CMemoryHeap__ctor", "129 type slots", "remain unproven"],
        ["cdxmemorymanager", "constructor", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CMemoryHeap__ctor", "DAT_0062e140"],
    ),
    "0x00549220": target(
        "CDXMemoryManager__Free",
        "void __thiscall CDXMemoryManager__Free(void * this, void * mem)",
        ["CDXMemoryManager::Free", "not OID object freeing", "CMemoryHeap__Free", "remain unproven"],
        ["cdxmemorymanager", "free", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CMemoryHeap__FreeTiny", "CMemoryHeap__Free"],
    ),
    "0x00549290": target(
        "CDXMemoryManager__PrintStats",
        "void __thiscall CDXMemoryManager__PrintStats(void * this)",
        ["CDXMemoryManager::PrintStats", "heapnr", "CMemoryHeap__PrintStats", "remain unproven"],
        ["cdxmemorymanager", "stats", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CMemoryHeap__PrintStats", "DAT_009c2bc8"],
    ),
    "0x005492b0": target(
        "CDXMemoryManager__OutputStats",
        "void __thiscall CDXMemoryManager__OutputStats(void * this, char * filename)",
        ["CDXMemoryManager::OutputStats", "CMemoryHeap__OutputStats", "remain unproven"],
        ["cdxmemorymanager", "stats", "file-output", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"],
        ["CMemoryHeap__OutputStats", "filename"],
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
    directory = base / "post-decomp"
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


def relative_or_absolute(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


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
    metadata = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")

    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing post_metadata row")
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
            failures.append(f"{address}: missing post_tags row")
        else:
            actual_tags = {item.strip() for item in re.split(r"[;,]", tag_row.get("tags", "")) if item.strip()}
            missing_tags = sorted(set(spec["tags"]) - actual_tags)  # type: ignore[arg-type]
            if missing_tags:
                failures.append(f"{address}: missing tags {missing_tags}")

        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing post-decomp export")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    if len(rows) < len(TARGETS):
        failures.append(f"post_xrefs.tsv: expected at least {len(TARGETS)} rows, got {len(rows)}")
    expected_edges = [
        ("0x004a1570", "CDXMemoryManager__Free"),
        ("0x004a2190", "CDXMemoryManager__PrintStats"),
        ("0x004a2660", "CMemoryManager__DumpMemory"),
        ("0x00549220", "CMemoryManager__DumpMemory"),
    ]
    for target_addr, from_name in expected_edges:
        wanted = normalize_address(target_addr)
        if not any(row.get("target_addr") == wanted and row.get("from_function") == from_name for row in rows):
            failures.append(f"post_xrefs.tsv: missing edge {target_addr} from {from_name}")


def run(base: Path) -> dict[str, object]:
    failures: list[str] = []
    check_verify_log(base, failures)
    check_metadata(base, failures)
    check_xrefs(base, failures)
    return {
        "status": "PASS" if not failures else "FAIL",
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "base": relative_or_absolute(base),
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
        print(f"Wave439 MemoryManager probe: {result['status']}")
        print(f"Base: {result['base']}")
        print(f"Targets: {result['targetCount']}")
        for failure in result["failures"]:  # type: ignore[index]
            print(f"- {failure}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
