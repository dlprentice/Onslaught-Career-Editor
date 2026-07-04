#!/usr/bin/env python3
"""Validate Wave715 PNG chunk parser head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave715-png-chunk-parser-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_png_chunk_parser_head_wave715_2026-05-22.md"
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

COMMON_TAGS = {
    "static-reaudit",
    "png-chunk-parser-head-wave715",
    "wave715-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "png-chunk-parser-head",
}

TARGETS = {
    "0x0059d699": (
        "CDXTexture__ParsePngChunk_IHDR",
        "void __stdcall CDXTexture__ParsePngChunk_IHDR(void * png_decode_state, void * png_image_context, uint chunk_data_length)",
        ("RET 0xc", "13-byte payload", "format descriptor", "IHDR handler"),
        COMMON_TAGS | {"png", "chunk-parser", "IHDR", "format-descriptor", "ret-0xc", "tranche-head"},
    ),
    "0x0059d879": (
        "CDXTexture__ParsePngChunk_PLTE",
        "void __stdcall CDXTexture__ParsePngChunk_PLTE(void * png_decode_state, void * png_image_context, uint chunk_data_length)",
        ("RET 0xc", "IHDR-before-PLTE", "3-byte palette entries", "tRNS counts disagree"),
        COMMON_TAGS | {"png", "chunk-parser", "PLTE", "palette", "scan-parameters", "ret-0xc"},
    ),
    "0x0059d992": (
        "CDXTexture__ParsePngChunk_IEND",
        "void __stdcall CDXTexture__ParsePngChunk_IEND(void * png_decode_state, void * png_image_context, uint chunk_data_length)",
        ("RET 0xc", "49 45 4e 44", "IEND handler", "terminal chunk"),
        COMMON_TAGS | {"png", "chunk-parser", "IEND", "terminal-chunk", "chunk-tag-constant", "rename-hardened", "ret-0xc"},
    ),
    "0x0059d9d8": (
        "CDXTexture__ParsePngChunk_gAMA",
        "void __stdcall CDXTexture__ParsePngChunk_gAMA(void * png_decode_state, void * png_image_context, uint chunk_data_length)",
        ("RET 0xc", "big-endian gamma", "decode_state +0x130", "sRGB/gAMA"),
        COMMON_TAGS | {"png", "chunk-parser", "gAMA", "gamma", "decode-option", "ret-0xc"},
    ),
    "0x0059dad9": (
        "CDXTexture__ParsePngChunk_sRGB",
        "void __stdcall CDXTexture__ParsePngChunk_sRGB(void * png_decode_state, void * png_image_context, uint chunk_data_length)",
        ("RET 0xc", "rendering intent", "intents above 3", "default-gamma helper"),
        COMMON_TAGS | {"png", "chunk-parser", "sRGB", "rendering-intent", "decode-option", "ret-0xc"},
    ),
    "0x0059dbbb": (
        "CDXTexture__ParsePngChunk_tRNS",
        "void __stdcall CDXTexture__ParsePngChunk_tRNS(void * png_decode_state, void * png_image_context, uint chunk_data_length)",
        ("RET 0xc", "74 52 4e 53", "big-endian 16-bit", "transparency counts"),
        COMMON_TAGS | {"png", "chunk-parser", "tRNS", "transparency", "chunk-tag-constant", "rename-hardened", "ret-0xc"},
    ),
    "0x0059dd5c": (
        "CDXTexture__HandlePngChunkAfterIdat",
        "void __stdcall CDXTexture__HandlePngChunkAfterIdat(void * png_decode_state, void * png_image_context, uint chunk_data_length)",
        ("RET 0xc", "generic PNG chunk handler", "unknown critical chunks", "drains/finalizes"),
        COMMON_TAGS | {"png", "chunk-parser", "fallback", "unknown-chunk", "ret-0xc"},
    ),
    "0x0059dda2": (
        "CDXTexture__ProcessIdatChunkDataAndQueueDecode",
        "void __stdcall CDXTexture__ProcessIdatChunkDataAndQueueDecode(void * png_decode_state)",
        ("RET 0x4", "prologue pushes ECX", "zlib stream", "async decode job"),
        COMMON_TAGS | {"png", "chunk-parser", "IDAT", "zlib", "async-decode-job", "ret-0x4", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave715 PNG chunk parser head",
    "png-chunk-parser-head-wave715",
    "0x0059d992 CDXTexture__ParsePngChunk_IEND",
    "0x0059dbbb CDXTexture__ParsePngChunk_tRNS",
    "49 45 4e 44",
    "74 52 4e 53",
    "CDXTexture__ProcessIdatChunkDataAndQueueDecode(png_decode_state_00)",
    "0x0059dfb2 CDXTexture__Crc32_Update",
    "0x0042f220 CSPtrSet__Clear",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260522-005631_post_wave715_png_chunk_parser_head_verified",
)

OVERCLAIM_TOKENS = (
    "runtime png behavior proven",
    "runtime decode/image fidelity proven",
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
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    expected_counts = {
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 9,
        "pre-instructions.tsv": 488,
        "pre-decompile/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 9,
        "post-instructions.tsv": 4584,
        "post-decompile/index.tsv": 8,
        "caller-decompile/index.tsv": 2,
        "caller-post-decompile/index.tsv": 2,
        "idat-callsite-instructions.tsv": 1731,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave715 static read-back" in comment, f"missing Wave715 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)
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
        decompile_file = BASE / "post-decompile" / f"{address[2:]}_{name}.c"
        require(decompile_file.is_file(), f"missing decompile file for {address}", failures)
        if decompile_file.is_file():
            text = read_text(decompile_file)
            for token in ("param_", "unaff_", "in_stack_", "in_ECX", "extraout_"):
                require(token not in text, f"{token} survived in post decompile for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=2 signature_updated=8 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=8 skipped=0 renamed=2 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=8 found=8 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "pre-xrefs.log": "Wrote 9 rows",
        "pre-instructions.log": "Wrote 488 instruction rows",
        "pre-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 9 rows",
        "post-instructions.log": "Wrote 4584 instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "caller-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "caller-post-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "idat-callsite-instructions.log": "Wrote 1731 instruction rows",
        "export-queue-refresh.log": "total_functions=6098 commented_functions=4167",
    }
    for log_name, token in expected.items():
        text = read_text(BASE / log_name)
        require(token in text, f"missing log token in {log_name}: {token}", failures)
        require("LockException" not in text, f"LockException in {log_name}", failures)
        require("BADNAME:" not in text and "MISSING:" not in text and "FAIL:" not in text, f"bad marker in {log_name}", failures)

    queue_probe = read_text(BASE / "queue-probe-after-refresh.log")
    for token in (
        "Status: PASS",
        "Total functions: 6098",
        "Commentless functions: 1931",
        "Undefined signatures: 1216",
        "Param signatures: 170",
    ):
        require(token in queue_probe, f"missing queue probe token: {token}", failures)


def check_dispatch_and_callers(failures: list[str]) -> None:
    constants = read_text(BASE / "png-chunk-dispatch-constants.txt")
    require("005ee8e4 49 45 4e 44 IEND" in constants, "missing IEND dispatch constant", failures)
    require("005ee904 74 52 4e 53 tRNS" in constants, "missing tRNS dispatch constant", failures)

    caller_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (BASE / "caller-post-decompile").glob("*.c"))
    for token in (
        "CDXTexture__ParsePngChunk_IEND",
        "CDXTexture__ParsePngChunk_tRNS",
        "CDXTexture__ProcessIdatChunkDataAndQueueDecode(png_decode_state_00)",
    ):
        require(token in caller_text, f"caller post-decompile missing token: {token}", failures)
    for token in ("extraout_", "unaff_", "in_ECX", "param_"):
        require(token not in caller_text, f"{token} survived in caller post-decompile", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    require(signals.get("commentlessFunctionCount") == 1931, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1216, "queue undefined mismatch", failures)
    require(signals.get("paramSignatureCount") == 170, "queue param mismatch", failures)
    high = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high["address"] == "0x0059dfb2", "high-signal head mismatch", failures)
    require(high["name"] == "CDXTexture__Crc32_Update", "high-signal head name mismatch", failures)

    quality_rows = read_tsv(QUEUE_TSV)
    raw_head = next(row for row in quality_rows if not row.get("comment", "").strip())
    require(raw_head["address"] == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)
    strict = [
        row for row in quality_rows
        if row.get("comment", "").strip()
        and not re.search(r"\bundefined\b", row.get("signature", ""))
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    ]
    require(len(strict) == 4111, "strict clean-signature proxy mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    backup_path = backup.get("backup_path") or backup.get("backupPath")
    file_count = backup.get("file_count") or backup.get("fileCount")
    total_bytes = backup.get("total_bytes") or backup.get("totalBytes")
    diff_count = backup.get("diff_count") if "diff_count" in backup else backup.get("diffCount")
    require(backup_path == r"[maintainer-local-ghidra-backup-root]\BEA_20260522-005631_post_wave715_png_chunk_parser_head_verified", "backup path mismatch", failures)
    require(file_count == 19, "backup file count mismatch", failures)
    require(int(total_bytes or 0) == 166038407, "backup byte count mismatch", failures)
    require(diff_count == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(
        package["scripts"].get("test:ghidra-png-chunk-parser-head-wave715")
        == "py -3 tools\\ghidra_png_chunk_parser_head_wave715_probe.py --check",
        "package script missing",
        failures,
    )

    doc_paths = (
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING,
    )
    for path in doc_paths:
        text = read_text(path)
        normalized_text = text.replace("\\\\", "\\")
        for token in DOC_TOKENS:
            require(token in normalized_text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path.relative_to(ROOT)} has overclaim token: {token}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        rows = read_jsonl(path)
        require(any(row.get("task") == "Wave715 PNG chunk parser head" for row in rows), f"{path.relative_to(ROOT)} missing Wave715 row", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(counters.get("ledger_rows") == 1111, "tracking ledger row count mismatch", failures)
    require(counters.get("attempt_rows") == 20371, "tracking attempt row count mismatch", failures)
    require(counters.get("completed") == 1102, "tracking completed count mismatch", failures)
    require(tracking.get("next_attempt_id") == 20371, "tracking next attempt mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_metadata(failures)
    check_logs(failures)
    check_dispatch_and_callers(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave715 PNG chunk parser head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave715 PNG chunk parser head probe: PASS")
    print("Targets: 8")
    print("Queue: 6098 total, 4167 commented, 1931 commentless, 1216 undefined, 170 param_N")
    print("Backup: [maintainer-local-ghidra-backup-root]\\BEA_20260522-005631_post_wave715_png_chunk_parser_head_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
