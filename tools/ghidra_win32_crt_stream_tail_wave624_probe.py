#!/usr/bin/env python3
"""Validate Wave624 Win32/CRT stream-tail Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave624-win32-crt-stream-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_win32_crt_stream_tail_wave624_2026-05-20.md"
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
    "0x0055f5ee": (
        "Win32__FindFirstFileWithMeta",
        "int __cdecl Win32__FindFirstFileWithMeta(char * pattern, void * outFindMeta)",
        ("FindFirstFileA wrapper", "save-file enumeration", "CRT errno"),
        ("win32-find", "crt-errno", "save-enumeration"),
    ),
    "0x0055f6bb": (
        "Win32__FindNextFileWithMeta",
        "int __cdecl Win32__FindNextFileWithMeta(int findHandle, void * outFindMeta)",
        ("FindNextFileA wrapper", "same file metadata buffer", "CRT errno"),
        ("win32-find", "crt-errno", "save-enumeration"),
    ),
    "0x0055f783": (
        "Win32__FindCloseWithErrno",
        "int __cdecl Win32__FindCloseWithErrno(int findHandle)",
        ("FindClose wrapper", "errno 0x16", "save-file enumeration cleanup"),
        ("win32-find", "crt-errno", "save-enumeration"),
    ),
    "0x0055f807": (
        "CRT__MbsNcpy_LocaleLock",
        "char * __cdecl CRT__MbsNcpy_LocaleLock(char * dest, char * src, uint maxBytes)",
        ("multibyte strncpy-style", "locale route 0x19", "PCPlatform async music stream setup"),
        ("crt-runtime", "multibyte-string", "locale-lock"),
    ),
    "0x0055f8a1": (
        "CRT__MbsIcmp_LocaleLock",
        "int __cdecl CRT__MbsIcmp_LocaleLock(char * lhs, char * rhs)",
        ("multibyte case-insensitive compare", "CRT__LCMapStringA_Compat", "PCPlatform async music stream setup"),
        ("crt-runtime", "multibyte-string", "locale-lock"),
    ),
    "0x0055fa62": (
        "CRT__PowCoreWithFpuGuards",
        "double __cdecl CRT__PowCoreWithFpuGuards(int baseLowWord, uint baseHighWord, int exponentLowWord, uint exponentHighWord)",
        ("pow core", "overlapping input varnodes", "instruction-backed"),
        ("crt-runtime", "math-helper", "fpu-control", "name-corrected", "decompile-limited"),
    ),
    "0x0055fc5d": (
        "CD3DApplication__ReadLineFromStreamLocked",
        "char * __cdecl CD3DApplication__ReadLineFromStreamLocked(char * buffer, int maxChars, void * stream)",
        ("fgets-style locked stream line reader", "cardid/vendor-tweak loading", "unlocks on exit"),
        ("crt-runtime", "stream-io", "cd3dapplication"),
    ),
    "0x0055fe26": (
        "CRT__LockRouteByAddress",
        "void __cdecl CRT__LockRouteByAddress(void * streamOrLockAddress)",
        ("indexed CRT lock table", "DAT_006533c0", "locked stream read/tell/seek helpers"),
        ("crt-runtime", "stream-lock", "lock-route"),
    ),
    "0x0055fe55": (
        "CRT__LockRouteByIndex",
        "void __cdecl CRT__LockRouteByIndex(int streamIndex, void * stream)",
        ("small CRT stream index", "streamIndex+0x1c", "critical section"),
        ("crt-runtime", "stream-lock", "lock-route"),
    ),
    "0x0055fe78": (
        "CRT__UnlockRouteByAddress",
        "void __cdecl CRT__UnlockRouteByAddress(void * streamOrLockAddress)",
        ("unlock companion", "DAT_006533c0", "locked stream read/tell/seek helpers"),
        ("crt-runtime", "stream-lock", "lock-route"),
    ),
    "0x0055fea7": (
        "CRT__UnlockRouteByIndex",
        "void __cdecl CRT__UnlockRouteByIndex(int streamIndex, void * stream)",
        ("unlock companion", "streamIndex+0x1c", "critical section"),
        ("crt-runtime", "stream-lock", "lock-route"),
    ),
    "0x0055feca": (
        "CRT__FTellWithRouteLock",
        "int __cdecl CRT__FTellWithRouteLock(void * stream)",
        ("locked ftell wrapper", "CRT__FTellAdjusted", "CDXEngine landscape texture cache"),
        ("crt-runtime", "stream-io", "stream-lock"),
    ),
    "0x0055feec": (
        "CRT__FTellAdjusted",
        "int __cdecl CRT__FTellAdjusted(void * stream)",
        ("ftell core", "text-mode newline expansion", "CRT__FSeek_UnlockedCore"),
        ("crt-runtime", "stream-io"),
    ),
    "0x0056004d": (
        "CDXTexture__AsciiToLowerInPlace",
        "char * __cdecl CDXTexture__AsciiToLowerInPlace(char * pathText)",
        ("in-place path/text lowercase", "ASCII A-Z folding", "LCMapStringA"),
        ("cdxtexture", "ascii-lowercase", "locale-lock"),
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
        "apply-wave624-dry.log": {
            "updated": 0,
            "skipped": 14,
            "renamed": 0,
            "would_rename": 1,
            "missing": 0,
            "bad": 0,
        },
        "apply-wave624-apply.log": {
            "updated": 14,
            "skipped": 0,
            "renamed": 1,
            "would_rename": 0,
            "missing": 0,
            "bad": 0,
        },
        "apply-wave624-final-dry.log": {
            "updated": 0,
            "skipped": 14,
            "renamed": 0,
            "would_rename": 0,
            "missing": 0,
            "bad": 0,
        },
    }
    for name, expected in expectations.items():
        require_clean_log_summary(BASE / name, expected, failures)

    expected_log_tokens = {
        "post-context-metadata.log": ("targets=14 found=14 missing=0",),
        "post-context-tags.log": ("rows=14 missing=0",),
        "post-context-xrefs.log": ("Wrote 51 rows",),
        "post-context-instructions.log": ("Wrote 1470 instruction rows", "targets=14 missing=0"),
        "post-context-decompile.log": ("targets=14 dumped=13 missing=0 failed=1",),
        "post-function-quality.log": ("total_functions=6093 commented_functions=3270",),
        "queue-probe.log": ("Status: PASS", "Commentless functions: 2823", "Param signatures: 1010"),
    }
    for log_name, tokens in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, tokens, failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_tags_decompile_and_edges(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-context-metadata.tsv")
    if len(rows) != 14:
        failures.append(f"post-context-metadata row count mismatch: {len(rows)} != 14")
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
    if len(tag_rows) != 14:
        failures.append(f"post-context-tags row count mismatch: {len(tag_rows)} != 14")
    tags_by_address = {
        normalize_address(row["address"]): set(filter(None, row["tags"].split(";")))
        for row in tag_rows
        if row.get("status") == "OK"
    }
    for address, (_, _, _, tag_tokens) in TARGETS.items():
        tags = tags_by_address.get(address, set())
        for token in ("static-reaudit", "retail-binary-evidence", "comment-hardened", "signature-hardened", "win32-crt-stream-tail-wave624", *tag_tokens):
            if token not in tags:
                failures.append(f"{address} missing tag {token}")

    decompile_rows = read_tsv_rows(BASE / "post-decompile" / "index.tsv")
    if len(decompile_rows) != 14:
        failures.append(f"post-decompile index row count mismatch: {len(decompile_rows)} != 14")
    decompile_by_address = {normalize_address(row["address"]): row for row in decompile_rows}
    for address in TARGETS:
        row = decompile_by_address.get(address)
        if not row:
            failures.append(f"post-decompile index missing {address}")
            continue
        expected_status = "FAILED" if address == "0x0055fa62" else "OK"
        if row["status"] != expected_status:
            failures.append(f"{address} decompile status mismatch: {row['status']} != {expected_status}")

    xrefs = read_text(BASE / "post-context-xrefs.tsv")
    for token in (
        "0055f5ee\tWin32__FindFirstFileWithMeta\t005149d6\t005149c0\tEnumerateSaveFiles_1",
        "0055f6bb\tWin32__FindNextFileWithMeta\t00514d29\t00514be0\tEnumerateSaveFiles_Main",
        "0055f783\tWin32__FindCloseWithErrno\t00514d5c\t00514be0\tEnumerateSaveFiles_Main",
        "0055f807\tCRT__MbsNcpy_LocaleLock\t00528591\t00528540\tPCPlatform__KickAsyncMusicStreamRead",
        "0055f8a1\tCRT__MbsIcmp_LocaleLock\t0052857a\t00528540\tPCPlatform__KickAsyncMusicStreamRead",
        "0055fa62\tCRT__PowCoreWithFpuGuards\t0055fa50\t0055fa40\tCRT__PowDispatch_ST0_ST1",
        "0055fc5d\tCD3DApplication__ReadLineFromStreamLocked\t00528769\t005286e0\tCD3DApplication__LoadCardIdAndApplyVendorTweaks",
        "0055fe26\tCRT__LockRouteByAddress\t0055fed1\t0055feca\tCRT__FTellWithRouteLock",
        "0055fe55\tCRT__LockRouteByIndex\t00564daa\t00564d79\tCRT__AcquireFileStreamSlot",
        "0055fe78\tCRT__UnlockRouteByAddress\t0055fedf\t0055feca\tCRT__FTellWithRouteLock",
        "0055fea7\tCRT__UnlockRouteByIndex\t00564dc2\t00564d79\tCRT__AcquireFileStreamSlot",
        "0055feca\tCRT__FTellWithRouteLock\t005479ac\t00547860\tCDXEngine__BuildLandscapeTextureCache",
        "0055feec\tCRT__FTellAdjusted\t005d084a\t005d0820\tCRT__FSeek_UnlockedCore",
        "0056004d\tCDXTexture__AsciiToLowerInPlace\t00557d1e\t00557a90\tCDXTexture__LoadTextureFromFile_Core",
    ):
        if token not in xrefs:
            failures.append(f"post-context-xrefs missing token: {token}")


def check_queue_backup_and_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2823,
        "undefinedSignatureCount": 1218,
        "paramSignatureCount": 1010,
    }
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head.get("address") != "0x00560181" or head.get("name") != "entry":
        failures.append(f"queue head mismatch: {head}")

    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupPath") != "G:\\GhidraBackups\\BEA_20260520-054923_post_wave624_win32_crt_stream_verified":
        failures.append(f"backupPath mismatch: {backup.get('backupPath')}")
    if backup.get("fileCount") != 19 or int(backup.get("totalBytes", 0)) != 161942407 or backup.get("diffCount") != 0:
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
        "package.json": ("test:ghidra-win32-crt-stream-tail-wave624",),
        "public note": ("Ghidra Win32/CRT Stream Tail Wave624", "0x0055fa62 CRT__PowCoreWithFpuGuards", "decompile-limited", "2823", "1010"),
        "functions index": ("Wave624 Win32/CRT stream-tail hardening", "0x00560181 entry"),
        "crt doc": ("Wave624 Static Read-Back Note", "CRT__PowCoreWithFpuGuards", "CDXTexture__AsciiToLowerInPlace"),
        "ghidra reference": ("Wave624 Win32/CRT Stream Tail Read-Back", "CRT__PowCoreWithFpuGuards", "decompile-limited"),
        "campaign": ("ghidra_win32_crt_stream_tail_wave624_2026-05-20.md", "0x00560181 entry"),
        "backlog": ("Ghidra Win32/CRT stream-tail Wave624 signature/comment hardening", "DiffCount=0"),
        "ledger": ("Ghidra Win32/CRT stream-tail Wave624 signature/comment hardening", "strict clean-signature proxy 3218/6093 = 52.81%"),
        "attempt log": ("attempt_id\":20279", "headless_java_apply_signature_comment_tags_with_one_rename_no_boundary_change"),
        "tracking": ("Wave624 hardened fourteen adjacent Win32 find", "next_attempt_id\": 20280"),
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
    check_metadata_tags_decompile_and_edges(failures)
    check_queue_backup_and_docs(failures)

    if failures:
        print("Wave624 Win32/CRT stream-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave624 Win32/CRT stream-tail probe: PASS")
    print("Verified 14 saved metadata rows, 14 tag rows, 51 xref rows, 1470 instruction rows, 13 clean decompile rows plus one expected decompile-limited row, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
