#!/usr/bin/env python3
"""Validate Wave731 inflate utility head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave731-inflate-utility-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_inflate_utility_head_wave731_2026-05-22.md"
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

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260522-092519_post_wave731_inflate_utility_head_verified"

COMMON_TAGS = {
    "static-reaudit",
    "inflate-utility-head-wave731",
    "wave731-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "inflate-utility-head",
}

TARGETS = {
    "0x005b1e16": (
        "CDXTexture__InflateBuildFixedHuffmanTables",
        "void * __stdcall CDXTexture__InflateBuildFixedHuffmanTables(void * inflate_stream, void * state_callback, uint window_size_bytes)",
        ("fixed-Huffman/window state", "0x5a0-byte fixed Huffman table", "state pointer or null"),
        COMMON_TAGS | {"tranche-head", "fixed-huffman-tables", "inflate-state-allocation", "ret-0xc"},
    ),
    "0x005b1e94": (
        "CDXTexture__InflateProcessBlockHeader",
        "int __stdcall CDXTexture__InflateProcessBlockHeader(void * inflate_state, void * inflate_stream, int status_code)",
        ("block-state machine", "returned EAX zlib-style status", "extraout_EAX"),
        COMMON_TAGS | {"inflate-block-state-machine", "dynamic-huffman", "stored-fixed-dynamic-blocks", "ret-0xc"},
    ),
    "0x005b25e0": (
        "CDXTexture__CloseAsyncDecodeHandles",
        "int __stdcall CDXTexture__CloseAsyncDecodeHandles(void * inflate_state, void * inflate_stream)",
        ("releases inflate/window allocations", "frees the window buffer", "returns 0"),
        COMMON_TAGS | {"inflate-state-release", "async-decode-cleanup", "ret-0x8"},
    ),
    "0x005b2613": (
        "CDXTexture__Adler32_Update",
        "uint __stdcall CDXTexture__Adler32_Update(uint adler, void * source_buffer, uint byte_count)",
        ("Adler-32 checksum", "0x15b0", "0xfff1"),
        COMMON_TAGS | {"adler32", "zlib-checksum", "mod-0xfff1", "ret-0xc"},
    ),
    "0x005b272e": (
        "CDXTexture__InflateDefaultAllocCallback",
        "void * __stdcall CDXTexture__InflateDefaultAllocCallback(void * opaque, uint item_count, uint item_size)",
        ("default inflate allocator callback", "HeapAlloc flag 8", "returns the allocated pointer in EAX"),
        COMMON_TAGS | {"tranche-tail", "inflate-allocator-callback", "heapalloc", "ret-0xc"},
    ),
}

DOC_TOKENS = (
    "Wave731 inflate utility head",
    "inflate-utility-head-wave731",
    "0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables",
    "0x005b1e94 CDXTexture__InflateProcessBlockHeader",
    "0x005b25e0 CDXTexture__CloseAsyncDecodeHandles",
    "0x005b2613 CDXTexture__Adler32_Update",
    "0x005b272e CDXTexture__InflateDefaultAllocCallback",
    "0x005b2860 CDXTexture__InitJpegEncoderComponentBuffers",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime inflate behavior proven",
    "runtime decode behavior proven",
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
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 6,
        "pre-instructions.tsv": 2705,
        "pre-decompile/index.tsv": 5,
        "caller-instructions.tsv": 1143,
        "caller-decompile/index.tsv": 3,
        "post-metadata.tsv": 5,
        "post-tags.tsv": 5,
        "post-xrefs.tsv": 6,
        "post-instructions.tsv": 2705,
        "post-decompile/index.tsv": 5,
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
        require("Wave731 static read-back" in comment, f"missing Wave731 comment at {address}", failures)
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=5 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=5 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=5 found=5 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "pre-xrefs.log": "Wrote 6 rows",
        "pre-instructions.log": "Wrote 2705 instruction rows",
        "pre-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "caller-instructions.log": "Wrote 1143 instruction rows",
        "caller-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "post-metadata.log": "targets=5 found=5 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "post-xrefs.log": "Wrote 6 rows",
        "post-instructions.log": "Wrote 2705 instruction rows",
        "post-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
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
    require(quality["commentlessFunctionCount"] == 1797, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 76, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005b2860", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CDXTexture__InitJpegEncoderComponentBuffers", "high-signal head name mismatch", failures)

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
    require(commented == 4301, "commented count mismatch", failures)
    require(strict_clean == 4243, "strict clean-signature proxy mismatch", failures)
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
    require(backup.get("totalBytes") == 166726535, "backup byte count mismatch", failures)
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
        package["scripts"].get("test:ghidra-inflate-utility-head-wave731")
        == r"py -3 tools\ghidra_inflate_utility_head_wave731_probe.py --check",
        "package script missing or mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave731 inflate utility head" for row in ledger_rows), "missing Wave731 ledger row", failures)
    require(any(row.get("attempt_id") == 20386 and row.get("task") == "Wave731 inflate utility head" for row in attempt_rows), "missing Wave731 attempt row", failures)

    tracking = read_json(TRACKING)
    require(tracking["counters"]["ledger_rows"] == 1127, "tracking ledger_rows mismatch", failures)
    require(tracking["counters"]["attempt_rows"] == 20387, "tracking attempt_rows mismatch", failures)
    require(tracking["counters"]["completed"] == 1118, "tracking completed mismatch", failures)
    require(tracking["counters"]["pending"] == 9, "tracking pending mismatch", failures)
    require(tracking["next_attempt_id"] == 20387, "tracking next_attempt_id mismatch", failures)
    require("Wave731 inflate utility head" in tracking.get("current_focus", ""), "tracking focus missing Wave731", failures)

    for state_path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(state_path)
        for token in ("Wave731 inflate utility head", "0x005b2860 CDXTexture__InitJpegEncoderComponentBuffers", BACKUP_PATH):
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
        print("Ghidra inflate utility head Wave731 probe")
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Ghidra inflate utility head Wave731 probe")
    print("Status: PASS")
    print("Targets: 5")
    print("Queue: 6098 total, 4301 commented, 1797 commentless, 1216 undefined, 76 param_N")
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
