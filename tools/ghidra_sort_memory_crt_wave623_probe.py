#!/usr/bin/env python3
"""Validate Wave623 sort/memory/CRT Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave623-sort-memory-crt-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_sort_memory_crt_wave623_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CRT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "crt-seh.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

TARGETS = {
    "0x0055e7ae": (
        "Sort__QuickSortGeneric",
        "void __cdecl Sort__QuickSortGeneric(void * base, uint count, uint elemSize, void * compareFn)",
        ("qsort-style generic sorter", "Sort__ShortSortGeneric", "display-device sorting"),
        ("sort-memory-crt-wave623", "sort-generic", "crt-runtime"),
    ),
    "0x0055e902": (
        "Sort__ShortSortGeneric",
        "void __cdecl Sort__ShortSortGeneric(void * lo, void * hi, uint elemSize, void * compareFn)",
        ("old CDXEngine owner/insertion wording", "algorithmically misleading", "Memory__SwapByteRange"),
        ("sort-memory-crt-wave623", "sort-generic", "name-corrected", "crt-runtime"),
    ),
    "0x0055e950": (
        "Memory__SwapByteRange",
        "void __cdecl Memory__SwapByteRange(void * lhs, void * rhs, int byteCount)",
        ("byte-swap helper", "generic qsort", "short-sort"),
        ("sort-memory-crt-wave623", "sort-generic", "byte-swap"),
    ),
    "0x0055eb00": (
        "CRT__WcsNcpyZeroPad",
        "short * __cdecl CRT__WcsNcpyZeroPad(short * destWide, short * srcWide, int maxWideChars)",
        ("wide strncpy-style", "zero-pads", "virtual keyboard"),
        ("sort-memory-crt-wave623", "crt-runtime", "wide-string"),
    ),
    "0x0055eb3d": (
        "CRT__RoundToIntegerRespectingControlWord",
        "double __cdecl CRT__RoundToIntegerRespectingControlWord(double value)",
        ("FPU control-word", "FRNDINT", "world occupancy"),
        ("sort-memory-crt-wave623", "crt-runtime", "fpu-control", "math-helper"),
    ),
    "0x0055ec4a": (
        "CRT__HeapAllocBase",
        "void * __cdecl CRT__HeapAllocBase(uint byteCount)",
        ("small-block heap", "HeapAlloc", "__nh_malloc"),
        ("sort-memory-crt-wave623", "crt-runtime", "heap-helper"),
    ),
    "0x0055ed50": (
        "CRT__MemMoveOverlapSafe",
        "void * __cdecl CRT__MemMoveOverlapSafe(void * dest, void * src, uint byteCount)",
        ("memmove-style", "overlapping src-before-dest", "returning dest"),
        ("sort-memory-crt-wave623", "crt-runtime", "memory-copy"),
    ),
    "0x0055f085": (
        "CRT__FreeBase",
        "void __cdecl CRT__FreeBase(void * ptr)",
        ("ignores null", "small-block heap release", "HeapFree"),
        ("sort-memory-crt-wave623", "crt-runtime", "heap-helper"),
    ),
    "0x0055f19d": (
        "CRT__FWriteCore",
        "uint __cdecl CRT__FWriteCore(void * buffer, uint elemSize, uint elemCount, void * stream)",
        ("core fwrite helper", "fd text-mode writes", "completed element count"),
        ("sort-memory-crt-wave623", "crt-runtime", "stream-io"),
    ),
    "0x0055f2e8": (
        "CRT__WcsCmp",
        "int __cdecl CRT__WcsCmp(short * lhsWide, short * rhsWide)",
        ("wide strcmp-style", "16-bit code units", "message-box portrait"),
        ("sort-memory-crt-wave623", "crt-runtime", "wide-string"),
    ),
    "0x0055f39d": (
        "CRT__AcosCoreWithFpuGuards",
        "double __cdecl CRT__AcosCoreWithFpuGuards(int lowWord, uint highWord)",
        ("CRT__AcosClassifyAndDispatch", "fpatan/sqrt", "math error/exit"),
        ("sort-memory-crt-wave623", "crt-runtime", "math-helper", "fpu-control"),
    ),
    "0x0055f506": (
        "CRT__FReadCore",
        "uint __cdecl CRT__FReadCore(void * buffer, uint elemSize, uint elemCount, void * stream)",
        ("core fread helper", "byte-at-a-time refill", "EOF/error stream flags"),
        ("sort-memory-crt-wave623", "crt-runtime", "stream-io"),
    ),
}

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
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        token = token.replace("\\\\", "\\")
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}


def require_clean_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in (
        "LockException",
        "Input file not found",
        "BADADDR",
        "ERROR REPORT SCRIPT ERROR",
        "BAD:",
        "BADNAME:",
        "Read-back mismatch",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    expectations = {
        "apply-wave623-dry.log": {
            "updated": 0,
            "skipped": 12,
            "renamed": 0,
            "would_rename": 1,
            "missing": 0,
            "bad": 0,
        },
        "apply-wave623-apply.log": {
            "updated": 12,
            "skipped": 0,
            "renamed": 1,
            "would_rename": 0,
            "missing": 0,
            "bad": 0,
        },
        "apply-wave623-final-dry.log": {
            "updated": 0,
            "skipped": 12,
            "renamed": 0,
            "would_rename": 0,
            "missing": 0,
            "bad": 0,
        },
    }
    for name, expected in expectations.items():
        require_clean_log_summary(BASE / name, expected, failures)

    expected_log_tokens = {
        "post-context-metadata.log": ("targets=12 found=12 missing=0",),
        "post-context-tags.log": ("rows=12 missing=0",),
        "post-context-xrefs.log": ("Wrote 147 rows",),
        "post-context-instructions.log": ("Wrote 1260 instruction rows", "targets=12 missing=0"),
        "post-context-decompile.log": ("targets=12 dumped=12 missing=0 failed=0",),
        "post-function-quality.log": ("total_functions=6093 commented_functions=3256",),
        "queue-probe.log": ("Status: PASS", "Commentless functions: 2837", "Param signatures: 1024"),
    }
    for log_name, tokens in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, tokens, failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_tags_and_edges(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-context-metadata.tsv")
    if len(rows) != 12:
        failures.append(f"post-context-metadata row count mismatch: {len(rows)} != 12")
    by_address = {normalize_address(row["address"]): row for row in rows}

    for address, (name, signature, comment_tokens, tag_tokens) in TARGETS.items():
        row = by_address.get(address)
        if not row:
            failures.append(f"post-context-metadata missing {address}")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} status mismatch: {row['status']}")
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        require_tokens(f"{address} comment", row["comment"], comment_tokens, failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

    tag_rows = read_tsv_rows(BASE / "post-context-tags.tsv")
    tags_by_address = {
        normalize_address(row["address"]): set(filter(None, row["tags"].split(";")))
        for row in tag_rows
        if row.get("status") == "OK"
    }
    for address, (_, _, _, tag_tokens) in TARGETS.items():
        tags = tags_by_address.get(address, set())
        for token in ("static-reaudit", "retail-binary-evidence", "comment-hardened", "signature-hardened", *tag_tokens):
            if token not in tags:
                failures.append(f"{address} missing tag {token}")

    xrefs = read_text(BASE / "post-context-xrefs.tsv")
    for token in (
        "0055e7ae\tSort__QuickSortGeneric\t005297ad\t00529350\tCD3DApplication__BuildDeviceList",
        "0055e902\tSort__ShortSortGeneric\t0055e804\t0055e7ae\tSort__QuickSortGeneric",
        "0055e950\tMemory__SwapByteRange\t0055e93b\t0055e902\tSort__ShortSortGeneric",
        "0055eb00\tCRT__WcsNcpyZeroPad\t0052118f\t00521100\tCFEPVirtualKeyboard__Render",
        "0055eb3d\tCRT__RoundToIntegerRespectingControlWord\t004bce07\t004bcd60\tCWorld__RebuildOccupancyGridFromDynamicSet",
        "0055ec4a\tCRT__HeapAllocBase\t0055ec29\t0055ec1e\t__nh_malloc",
        "0055ed50\tCRT__MemMoveOverlapSafe\t005243cb\t00524180\tOggVorbisStream__ReadPcmSamples",
        "0055f085\tCRT__FreeBase\t0055dade\t0055dac5\ttype_info__dtor",
        "0055f19d\tCRT__FWriteCore\t0055f186\t0055f16e\tfwrite",
        "0055f2e8\tCRT__WcsCmp\t004b7ad6\t004b7ab0\tCMessageBox__SelectPortraitIndex",
        "0055f39d\tCRT__AcosCoreWithFpuGuards\t0055f38b\t0055f380\tCRT__AcosClassifyAndDispatch",
        "0055f506\tCRT__FReadCore\t0055f4ef\t0055f4d7\tfread",
    ):
        if token not in xrefs:
            failures.append(f"post-context-xrefs missing token: {token}")


def check_queue_backup_and_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2837,
        "undefinedSignatureCount": 1218,
        "paramSignatureCount": 1024,
    }
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head.get("address") != "0x0055f5ee" or head.get("name") != "Win32__FindFirstFileWithMeta":
        failures.append(f"queue head mismatch: {head}")

    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupPath") != "[maintainer-local-ghidra-backup-root]\\BEA_20260520-052133_post_wave623_sort_memory_crt_verified":
        failures.append(f"backupPath mismatch: {backup.get('backupPath')}")
    if backup.get("fileCount") != 19 or int(backup.get("totalBytes", 0)) != 161909639 or backup.get("diffCount") != 0:
        failures.append(f"backup summary mismatch: {backup}")

    docs = {
        "package.json": read_text(PACKAGE_JSON),
        "public note": read_text(PUBLIC_NOTE),
        "functions index": read_text(FUNCTION_INDEX),
        "crt doc": read_text(CRT_DOC),
        "ghidra reference": read_text(GHIDRA_REFERENCE),
        "campaign": read_text(CAMPAIGN),
        "backlog": read_text(BACKLOG),
        "ledger": read_text(LEDGER),
        "attempt log": read_text(ATTEMPT_LOG),
        "tracking": read_text(TRACKING),
    }
    expected_doc_tokens = {
        "package.json": ("test:ghidra-sort-memory-crt-wave623",),
        "public note": ("Ghidra Sort/Memory/CRT Wave623", "0x0055e902 Sort__ShortSortGeneric", "2837", "1024"),
        "functions index": ("Wave623 sort/memory/CRT hardening", "0x0055f5ee Win32__FindFirstFileWithMeta"),
        "crt doc": ("Wave623 Static Read-Back Note", "Sort__ShortSortGeneric", "CRT__FReadCore"),
        "ghidra reference": ("Wave623 Sort/Memory/CRT Read-Back", "Sort__ShortSortGeneric", "Ghidra Wave623 correction"),
        "campaign": ("ghidra_sort_memory_crt_wave623_2026-05-20.md", "0x0055f5ee Win32__FindFirstFileWithMeta"),
        "backlog": ("Ghidra sort/memory/CRT Wave623 signature/comment hardening", "DiffCount=0"),
        "ledger": ("Ghidra sort/memory/CRT Wave623 signature/comment hardening", "strict clean-signature proxy 3204/6093 = 52.58%"),
        "attempt log": ("attempt_id\":20278", "headless_java_apply_signature_comment_tags_with_one_rename_no_boundary_change"),
        "tracking": ("Wave623 hardened twelve adjacent sort/memory/CRT helper rows", "next_attempt_id\": 20279"),
    }
    for label, tokens in expected_doc_tokens.items():
        require_tokens(label, docs[label], tokens, failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="run validation")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_logs(failures)
    check_metadata_tags_and_edges(failures)
    check_queue_backup_and_docs(failures)

    if failures:
        print("Wave623 sort/memory/CRT probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave623 sort/memory/CRT probe: PASS")
    print("Verified 12 saved metadata rows, 12 tag rows, 147 xref rows, 1260 instruction rows, 12 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
