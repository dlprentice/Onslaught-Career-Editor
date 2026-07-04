#!/usr/bin/env python3
"""Validate Wave730 aligned window prelude read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave730-aligned-window-prelude"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_aligned_window_prelude_wave730_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260522-085034_post_wave730_aligned_window_prelude_verified"

COMMON_TAGS = {
    "static-reaudit",
    "aligned-window-prelude-wave730",
    "wave730-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "aligned-window-prelude",
}

TARGETS = {
    "0x005b1c00": (
        "CDXTexture__AllocAligned16",
        "void * __stdcall CDXTexture__AllocAligned16(void * allocator_owner, uint requested_size_bytes)",
        ("aligned allocation callback", "requested_size_bytes + 0x10", "aligned_payload - 1"),
        COMMON_TAGS | {"tranche-head", "aligned-allocator", "decode-allocator-callback", "ret-0x8"},
    ),
    "0x005b1c30": (
        "CDXTexture__FreeAligned16",
        "void __stdcall CDXTexture__FreeAligned16(void * allocator_owner, void * aligned_payload, uint tracked_size_bytes)",
        ("reads the byte delta", "tracked byte count", "CRT__FreeBase"),
        COMMON_TAGS | {"aligned-free", "decode-allocator-callback", "ret-0xc"},
    ),
    "0x005b1c50": (
        "CDXTexture__GetBufferTailAvailable",
        "int __stdcall CDXTexture__GetBufferTailAvailable(void * allocator_owner, int row_count_hint, int minimum_chunk_bytes, int committed_size_bytes)",
        ("row-allocation prelude", "state +0x2c", "budget_or_cap - committed_size_bytes"),
        COMMON_TAGS | {"budget-tail-helper", "row-allocation-prelude", "ret-0x10"},
    ),
    "0x005b1d50": (
        "CDXTexture__InitHostIoCallbacks",
        "void __stdcall CDXTexture__InitHostIoCallbacks(void * decode_context, void * host_io_callbacks, uint window_size_bytes)",
        ("CRT__TmpFile_OpenUniqueBinaryStream", "callback table +0xc", "0x005b1c70"),
        COMMON_TAGS | {"host-io-callbacks", "temporary-stream", "decode-window", "ret-0xc"},
    ),
    "0x005b1da0": (
        "CDXTexture__GetDefaultDecodeBudgetBytes",
        "int __cdecl CDXTexture__GetDefaultDecodeBudgetBytes(void)",
        ("default decode allocator budget value 1000000", "CDXTexture__InitDecodeAllocatorVtable", "0x54-byte allocator state"),
        COMMON_TAGS | {"default-decode-budget", "allocator-budget", "constant-return"},
    ),
    "0x005b1db0": (
        "CDXTexture__ResetDecodeWindowState",
        "void __stdcall CDXTexture__ResetDecodeWindowState(void * inflate_state, void * host_io_state, void * previous_cookie_out)",
        ("async-decode begin", "modes 4/5", "state callback at +0x38"),
        COMMON_TAGS | {"tranche-tail", "decode-window-reset", "inflate-state", "ret-0xc"},
    ),
}

DOC_TOKENS = (
    "Wave730 aligned window prelude",
    "aligned-window-prelude-wave730",
    "0x005b1c00 CDXTexture__AllocAligned16",
    "0x005b1c30 CDXTexture__FreeAligned16",
    "0x005b1c50 CDXTexture__GetBufferTailAvailable",
    "0x005b1d50 CDXTexture__InitHostIoCallbacks",
    "0x005b1da0 CDXTexture__GetDefaultDecodeBudgetBytes",
    "0x005b1db0 CDXTexture__ResetDecodeWindowState",
    "0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime texture behavior proven",
    "runtime zlib/decode behavior proven",
    "runtime image decode behavior proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 15,
        "pre-instructions.tsv": 3246,
        "pre-decompile/index.tsv": 6,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 15,
        "post-instructions.tsv": 3246,
        "post-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave730 static read-back" in comment, f"missing Wave730 comment at {address}", failures)
        require("Static retail Ghidra metadata" in comment, f"missing static-evidence boundary at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "post-decompile" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=6 found=6 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "pre-xrefs.log": "Wrote 15 rows",
        "pre-instructions.log": "Wrote 3246 instruction rows",
        "pre-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 15 rows",
        "post-instructions.log": "Wrote 3246 instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}", failures)
        for bad_token in ("LockException", "MISSING:", "BADNAME", "FAIL:", "Invalid script", "Input file not found"):
            require(bad_token not in text, f"unexpected {bad_token} in {relative}", failures)

    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save evidence", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply-final-dry.log"), "missing final dry save evidence", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1802, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 81, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005b1e16", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CDXTexture__InflateBuildFixedHuffmanTables", "high-signal head name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    raw_head = next(row for row in rows if not row.get("comment", "").strip())
    require(commented == 4296, "commented count mismatch", failures)
    require(strict_clean == 4238, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    for address in TARGETS:
        row = next((item for item in rows if normalize_address(item["address"]) == address), None)
        require(row is not None, f"missing queue row {address}", failures)
        if row is not None:
            require(bool(row.get("comment", "").strip()), f"queue row still commentless {address}", failures)
            require(row["signature"] == TARGETS[address][1], f"queue signature mismatch {address}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 166693767, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_logs(failures: list[str]) -> None:
    paths = [PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG]
    for path in paths:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"missing doc token in {path}: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"overclaim token in {path}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package["scripts"].get("test:ghidra-aligned-window-prelude-wave730")
        == r"py -3 tools\ghidra_aligned_window_prelude_wave730_probe.py --check",
        "package script missing or mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave730 aligned window prelude" for row in ledger_rows), "missing Wave730 ledger row", failures)
    require(any(row.get("attempt_id") == 20385 and row.get("task") == "Wave730 aligned window prelude" for row in attempt_rows), "missing Wave730 attempt row", failures)

    tracking = read_json(TRACKING)
    require(tracking["counters"]["ledger_rows"] == 1126, "tracking ledger_rows mismatch", failures)
    require(tracking["counters"]["attempt_rows"] == 20386, "tracking attempt_rows mismatch", failures)
    require(tracking["counters"]["completed"] == 1117, "tracking completed mismatch", failures)
    require(tracking["next_attempt_id"] == 20386, "tracking next_attempt_id mismatch", failures)
    require("Wave730 aligned window prelude" in tracking.get("current_focus", ""), "tracking focus missing Wave730", failures)

    for state_path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(state_path)
        for token in ("Wave730 aligned window prelude", "0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables", BACKUP_PATH):
            escaped_token = token.replace("\\", "\\\\")
            require(token in text or escaped_token in text, f"state token missing in {state_path}: {token}", failures)


def run_check() -> int:
    failures: list[str] = []
    try:
        check_artifacts(failures)
        check_logs(failures)
        check_queue_and_backup(failures)
        check_docs_and_logs(failures)
    except Exception as exc:
        failures.append(f"exception: {exc}")

    if failures:
        print("Ghidra aligned window prelude Wave730 probe")
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Ghidra aligned window prelude Wave730 probe")
    print("Status: PASS")
    print("Targets: 6")
    print("Queue: 6098 total, 4296 commented, 1802 commentless, 1216 undefined, 81 param_N")
    print(f"Backup: {BACKUP_PATH}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")
    return run_check()


if __name__ == "__main__":
    raise SystemExit(main())
