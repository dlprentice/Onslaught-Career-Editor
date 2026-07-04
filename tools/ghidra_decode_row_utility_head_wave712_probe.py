#!/usr/bin/env python3
"""Validate Wave712 decode row utility head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave712-decode-row-utility-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_decode_row_utility_head_wave712_2026-05-21.md"
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
BACKUP_SUMMARY = BASE / "backup-summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "decode-row-utility-head-wave712",
    "wave712-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "decode-row-utility-head",
}

TARGETS = {
    "0x0059c070": (
        "CTexture__ProcessRowBatchesLinearStride",
        "void __stdcall CTexture__ProcessRowBatchesLinearStride(int param_1, int param_2)",
        ("RET 0x8", "hidden unaff_ESI", "callback slot [0xc]", "callback slot [0xd]"),
        COMMON_TAGS | {"comment-only-hidden-abi", "row-batch-hidden-esi", "linear-row-batches", "ret-0x8", "tranche-head"},
        True,
    ),
    "0x0059c110": (
        "CTexture__ProcessRowBatchesMcuStride128",
        "void __stdcall CTexture__ProcessRowBatchesMcuStride128(int param_1, int param_2)",
        ("RET 0x8", "hidden unaff_ESI", "0x80", "callback slot [0xc]"),
        COMMON_TAGS | {"comment-only-hidden-abi", "row-batch-hidden-esi", "mcu-row-batches", "ret-0x8"},
        True,
    ),
    "0x0059c630": (
        "CTexture__AllocJpegQuantTableDescriptor",
        "void __stdcall CTexture__AllocJpegQuantTableDescriptor(void * decode_state)",
        ("RET 0x4", "0x84 JPEG quantization-table descriptor", "descriptor +0x80"),
        COMMON_TAGS | {"signature-hardened", "jpeg-quant-table", "descriptor-allocation", "ret-0x4"},
        False,
    ),
    "0x0059c650": (
        "CTexture__AllocJpegHuffmanTableDescriptor",
        "void __stdcall CTexture__AllocJpegHuffmanTableDescriptor(void * decode_state)",
        ("RET 0x4", "0x118 JPEG Huffman-table descriptor", "descriptor +0x114"),
        COMMON_TAGS | {"signature-hardened", "jpeg-huffman-table", "descriptor-allocation", "ret-0x4"},
        False,
    ),
    "0x0059c670": (
        "CDXTexture__CeilDiv",
        "int __stdcall CDXTexture__CeilDiv(int value, int divisor)",
        ("RET 0x8", "integer ceiling-division", "MCU/layout geometry"),
        COMMON_TAGS | {"signature-hardened", "ceil-div", "geometry-helper", "ret-0x8"},
        False,
    ),
    "0x0059c690": (
        "CDXTexture__AlignUpToMultiple",
        "int __stdcall CDXTexture__AlignUpToMultiple(int value, int multiple)",
        ("RET 0x8", "integer align-up", "workspace layout"),
        COMMON_TAGS | {"signature-hardened", "align-up", "workspace-helper", "ret-0x8"},
        False,
    ),
    "0x0059c6b0": (
        "CTexture__CopyRowsFromPointerTable",
        "void __stdcall CTexture__CopyRowsFromPointerTable(void * src_row_table, int src_row_index, void * dst_row_table, int dst_row_index, int row_count, uint bytes_per_row)",
        ("RET 0x18", "row pointer tables", "tail bytes"),
        COMMON_TAGS | {"signature-hardened", "row-pointer-copy", "copy-helper", "ret-0x18"},
        False,
    ),
    "0x0059c700": (
        "CFastVB__CopyBlockRows128Bytes",
        "void __stdcall CFastVB__CopyBlockRows128Bytes(void * src, void * dst, int block_row_count)",
        ("RET 0xc", "0x005ac57f", "block_row_count << 7"),
        COMMON_TAGS | {"signature-hardened", "copy-128-byte-blocks", "copy-helper", "ret-0xc"},
        False,
    ),
    "0x0059c730": (
        "CDXTexture__ZeroBufferBytes",
        "void __stdcall CDXTexture__ZeroBufferBytes(void * buffer, uint byte_count)",
        ("RET 0x8", "byte_count bytes", "tail-byte stores"),
        COMMON_TAGS | {"signature-hardened", "zero-buffer", "clear-helper", "ret-0x8"},
        False,
    ),
    "0x0059c750": (
        "CDXTexture__BeginAsyncDecodeJob",
        "int __stdcall CDXTexture__BeginAsyncDecodeJob(void * decode_job)",
        ("RET 0x4", "returns -2", "CDXTexture__ResetDecodeWindowState"),
        COMMON_TAGS | {"signature-hardened", "async-decode-job", "decode-job-begin", "ret-0x4"},
        False,
    ),
    "0x0059c78f": (
        "CDXTexture__FinishAsyncDecodeJob",
        "int __stdcall CDXTexture__FinishAsyncDecodeJob(void * decode_job)",
        ("RET 0x4", "returns -2", "completion callback"),
        COMMON_TAGS | {"signature-hardened", "async-decode-job", "decode-job-finish", "ret-0x4", "tranche-tail"},
        False,
    ),
}

DOC_TOKENS = (
    "Wave712 decode row utility head",
    "decode-row-utility-head-wave712",
    "0x0059c070 CTexture__ProcessRowBatchesLinearStride",
    "0x0059c78f CDXTexture__FinishAsyncDecodeJob",
    "0x0059c110 CTexture__ProcessRowBatchesMcuStride128",
    "0x0059c7cc CDXTexture__InflateInitStateFromHeader",
    "0x0042f220 CSPtrSet__Clear",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260521-232045_post_wave712_decode_row_utility_head_verified",
)

OVERCLAIM_TOKENS = (
    "runtime jpeg/png/decode behavior proven",
    "runtime texture behavior proven",
    "row-batch descriptor layout proven",
    "callback abi proven",
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


def check_metadata(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-post" / "index.tsv")}

    expected_counts = {
        "pre-candidate-metadata.tsv": 11,
        "pre-candidate-tags.tsv": 11,
        "pre-candidate-xrefs.tsv": 57,
        "pre-candidate-instructions.tsv": 2651,
        "decompile-candidate-pre/index.tsv": 11,
        "pre-metadata.tsv": 11,
        "pre-tags.tsv": 11,
        "pre-xrefs.tsv": 57,
        "pre-instructions.tsv": 2651,
        "decompile-pre/index.tsv": 11,
        "post-metadata.tsv": 11,
        "post-tags.tsv": 11,
        "post-xrefs.tsv": 57,
        "post-instructions.tsv": 2651,
        "decompile-post/index.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for address, (name, signature, comment_tokens, expected_tags, comment_only) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave712 static read-back" in comment, f"missing Wave712 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            if comment_only:
                require("signature-hardened" not in actual_tags, f"comment-only row has signature tag: {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        decompile_file = BASE / "decompile-post" / f"{address[2:]}_{name}.c"
        require(decompile_file.is_file(), f"missing decompile file for {address}", failures)
        if decompile_file.is_file():
            text = read_text(decompile_file)
            if comment_only:
                require("param_1" in text and "param_2" in text, f"comment-only param tokens missing for {address}", failures)
                require("unaff_ESI" in text, f"comment-only hidden ABI token missing for {address}", failures)
            else:
                for token in ("param_", "unaff_", "in_stack_", "in_ECX"):
                    require(token not in text, f"{token} survived in post decompile for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=2 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=2 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "export-pre-candidate-metadata.log": "targets=11 found=11 missing=0",
        "export-pre-candidate-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "export-pre-candidate-xrefs.log": "Wrote 57 rows",
        "export-pre-candidate-instructions.log": "Wrote 2651 instruction rows",
        "export-pre-candidate-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "export-pre-metadata.log": "targets=11 found=11 missing=0",
        "export-pre-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "export-pre-xrefs.log": "Wrote 57 rows",
        "export-pre-instructions.log": "Wrote 2651 instruction rows",
        "export-pre-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "export-post-metadata.log": "targets=11 found=11 missing=0",
        "export-post-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "export-post-xrefs.log": "Wrote 57 rows",
        "export-post-instructions.log": "Wrote 2651 instruction rows",
        "export-post-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "export-queue-refresh.log": "total_functions=6098 commented_functions=4143",
    }
    for log_name, token in expected.items():
        text = read_text(BASE / log_name)
        require(token in text, f"missing log token in {log_name}: {token}", failures)
        require("LockException" not in text, f"LockException in {log_name}", failures)
        require("BADNAME:" not in text and "MISSING:" not in text and "FAIL:" not in text, f"bad marker in {log_name}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    require(signals.get("commentlessFunctionCount") == 1955, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1216, "queue undefined mismatch", failures)
    require(signals.get("paramSignatureCount") == 194, "queue param mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head["address"] == "0x0059c7cc", "high-signal head mismatch", failures)
    require(head["name"] == "CDXTexture__InflateInitStateFromHeader", "high-signal head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == r"[maintainer-local-ghidra-backup-root]\BEA_20260521-232045_post_wave712_decode_row_utility_head_verified", "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 165874567, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(package["scripts"].get("test:ghidra-decode-row-utility-head-wave712") == "py -3 tools\\ghidra_decode_row_utility_head_wave712_probe.py --check", "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        normalized_text = text.replace("\\\\", "\\")
        for token in DOC_TOKENS:
            require(token in normalized_text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path.relative_to(ROOT)} has overclaim token: {token}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        rows = read_jsonl(path)
        require(any(row.get("task") == "Wave712 decode row utility head" for row in rows), f"{path.relative_to(ROOT)} missing Wave712 row", failures)

    tracking = read_json(TRACKING)
    require("Wave712 decode row utility head" in read_text(TRACKING), "tracking missing Wave712", failures)
    require(tracking.get("counters", {}).get("ledger_rows") == 1108, "tracking ledger row count mismatch", failures)
    require(tracking.get("counters", {}).get("attempt_rows") == 20368, "tracking attempt row count mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_metadata(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave712 decode row utility head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave712 decode row utility head probe: PASS")
    print("Targets: 11")
    print("Queue: 6098 total, 4143 commented, 1955 commentless, 1216 undefined, 194 param_N")
    print("Backup: [maintainer-local-ghidra-backup-root]\\BEA_20260521-232045_post_wave712_decode_row_utility_head_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
