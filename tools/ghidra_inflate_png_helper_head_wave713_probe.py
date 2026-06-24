#!/usr/bin/env python3
"""Validate Wave713 inflate / PNG helper head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave713-inflate-png-helper-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_inflate_png_helper_head_wave713_2026-05-21.md"
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
    "inflate-png-helper-head-wave713",
    "wave713-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "inflate-png-helper-head",
}

TARGETS = {
    "0x0059c7cc": (
        "CDXTexture__InflateInitStateFromHeader",
        "int __stdcall CDXTexture__InflateInitStateFromHeader(void * inflate_stream, int window_bits, void * version_text, int stream_struct_size)",
        ("RET 0x10", "window-bits", "0x38 stream struct-size", "fixed Huffman tables"),
        COMMON_TAGS | {"inflate", "zlib", "state-init", "window-bits", "ret-0x10", "tranche-head"},
    ),
    "0x0059c8ab": (
        "CDXTexture__InflateInit_WindowBits15",
        "int __stdcall CDXTexture__InflateInit_WindowBits15(void * inflate_stream, void * version_text, int stream_struct_size)",
        ("RET 0xc", "fixed window bits 15", "CDXTexture__InflateInitStateFromHeader"),
        COMMON_TAGS | {"inflate", "zlib", "window-bits-15", "wrapper", "ret-0xc"},
    ),
    "0x0059c8c1": (
        "CDXTexture__InflateStream_ProcessZlibState",
        "int __stdcall CDXTexture__InflateStream_ProcessZlibState(void * inflate_stream, int flush_mode)",
        ("RET 0x8", "PNG IDAT/pass-row xrefs", "extraout_EAX", "zlib-style status values"),
        COMMON_TAGS | {"inflate", "zlib", "state-machine", "png-idat", "extraout-eax-gap", "ret-0x8"},
    ),
    "0x0059cc24": (
        "CDXTexture__AllocZeroedDecodeState",
        "void * __stdcall CDXTexture__AllocZeroedDecodeState(int state_class)",
        ("RET 0x4", "class 1 as 0x19c bytes", "class 2 as 0x40 bytes", "zeroes"),
        COMMON_TAGS | {"decode-state", "allocation", "zero-init", "state-class", "ret-0x4"},
    ),
    "0x0059cc68": (
        "CDXTexture__FreeDecodeState",
        "void __stdcall CDXTexture__FreeDecodeState(void * decode_state)",
        ("RET 0x4", "CRT__FreeBase", "ReleasePngDecodeContextHandles"),
        COMMON_TAGS | {"decode-state", "allocation", "cleanup", "free", "ret-0x4"},
    ),
    "0x0059cc7c": (
        "CDXTexture__AllocOrThrow",
        "void * __stdcall CDXTexture__AllocOrThrow(void * png_decode_state, uint byte_count)",
        ("RET 0x8", "mallocs byte_count", "CDXTexture__ThrowDecodeError"),
        COMMON_TAGS | {"png", "allocation", "decode-error", "malloc", "ret-0x8"},
    ),
    "0x0059ccf3": (
        "CDXTexture__MemsetByte",
        "void * __stdcall CDXTexture__MemsetByte(void * unused_context, void * destination_buffer, int fill_byte, uint byte_count)",
        ("RET 0x10", "destination_buffer", "unused", "dword and tail-byte loops"),
        COMMON_TAGS | {"memset", "png", "buffer-fill", "unused-context", "ret-0x10"},
    ),
    "0x0059cd26": (
        "CDXTexture__ReadU32BigEndian",
        "uint __stdcall CDXTexture__ReadU32BigEndian(void * source_buffer)",
        ("RET 0x4", "big-endian uint32", "PNG headers", "gAMA"),
        COMMON_TAGS | {"png", "big-endian", "chunk-read", "u32-read", "ret-0x4"},
    ),
    "0x0059cd4b": (
        "CDXTexture__ReadChunkBytesAndUpdateCrc",
        "void __stdcall CDXTexture__ReadChunkBytesAndUpdateCrc(void * png_decode_state, void * destination_buffer, uint byte_count)",
        ("RET 0xc", "PNG source", "running chunk CRC"),
        COMMON_TAGS | {"png", "chunk-read", "crc", "source-read", "ret-0xc"},
    ),
    "0x0059cd62": (
        "CDXTexture__IsPngChunkCrcInvalid",
        "bool __stdcall CDXTexture__IsPngChunkCrcInvalid(void * png_decode_state)",
        ("RET 0x4", "stored CRC dword", "decode_state +0x100", "chunk CRC is invalid"),
        COMMON_TAGS | {"png", "crc", "chunk-validation", "bool-return", "ret-0x4"},
    ),
    "0x0059cdbe": (
        "CDXTexture__ValidateChunkTagAsciiOrLog",
        "void __stdcall CDXTexture__ValidateChunkTagAsciiOrLog(void * png_decode_state, void * chunk_type_bytes)",
        ("RET 0x8", "ASCII ranges", "invalid chunk type", "CDXTexture__LogChunkTagDiagnostic"),
        COMMON_TAGS | {"png", "chunk-tag", "diagnostic", "ascii-validation", "ret-0x8", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave713 inflate / PNG helper head",
    "inflate-png-helper-head-wave713",
    "0x0059c7cc CDXTexture__InflateInitStateFromHeader",
    "0x0059cdbe CDXTexture__ValidateChunkTagAsciiOrLog",
    "0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState",
    "extraout_EAX",
    "0x0059ce20 CDXTexture__ExpandPackedPixelsToScanline",
    "0x0042f220 CSPtrSet__Clear",
    r"G:\GhidraBackups\BEA_20260521-234937_post_wave713_inflate_png_helper_head_verified",
)

OVERCLAIM_TOKENS = (
    "runtime png behavior proven",
    "runtime inflate behavior proven",
    "zlib source identity proven",
    "runtime image fidelity proven",
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
        "candidate-metadata.tsv": 11,
        "candidate-tags.tsv": 11,
        "candidate-xrefs.tsv": 44,
        "candidate-instructions.tsv": 2871,
        "decompile-candidate-pre/index.tsv": 11,
        "pre-metadata.tsv": 11,
        "pre-tags.tsv": 11,
        "pre-xrefs.tsv": 44,
        "pre-instructions.tsv": 2871,
        "decompile-pre/index.tsv": 11,
        "post-metadata.tsv": 11,
        "post-tags.tsv": 11,
        "post-xrefs.tsv": 44,
        "post-instructions.tsv": 2871,
        "decompile-post/index.tsv": 11,
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
        require("Wave713 static read-back" in comment, f"missing Wave713 comment at {address}", failures)
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
        decompile_file = BASE / "decompile-post" / f"{address[2:]}_{name}.c"
        require(decompile_file.is_file(), f"missing decompile file for {address}", failures)
        if decompile_file.is_file():
            text = read_text(decompile_file)
            for token in ("param_", "unaff_", "in_stack_", "in_ECX"):
                require(token not in text, f"{token} survived in post decompile for {address}", failures)
            if address == "0x0059c8c1":
                require("extraout_EAX" in text, "expected extraout_EAX gap missing for 0x0059c8c1", failures)
            else:
                require("extraout_" not in text, f"unexpected extraout_ token survived for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "export-candidate-metadata.log": "targets=11 found=11 missing=0",
        "export-candidate-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "export-candidate-xrefs.log": "Wrote 44 rows",
        "export-candidate-instructions.log": "Wrote 2871 instruction rows",
        "export-candidate-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "export-pre-metadata.log": "targets=11 found=11 missing=0",
        "export-pre-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "export-pre-xrefs.log": "Wrote 44 rows",
        "export-pre-instructions.log": "Wrote 2871 instruction rows",
        "export-pre-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "export-post-metadata.log": "targets=11 found=11 missing=0",
        "export-post-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "export-post-xrefs.log": "Wrote 44 rows",
        "export-post-instructions.log": "Wrote 2871 instruction rows",
        "export-post-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "export-queue-refresh.log": "total_functions=6098 commented_functions=4154",
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
    require(signals.get("commentlessFunctionCount") == 1944, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1216, "queue undefined mismatch", failures)
    require(signals.get("paramSignatureCount") == 183, "queue param mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head["address"] == "0x0059ce20", "high-signal head mismatch", failures)
    require(head["name"] == "CDXTexture__ExpandPackedPixelsToScanline", "high-signal head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    backup_path = backup.get("backup_path") or backup.get("backupPath")
    file_count = backup.get("file_count") or backup.get("fileCount")
    total_bytes = backup.get("total_bytes") or backup.get("totalBytes")
    diff_count = backup.get("diff_count") if "diff_count" in backup else backup.get("diffCount")
    require(backup_path == r"G:\GhidraBackups\BEA_20260521-234937_post_wave713_inflate_png_helper_head_verified", "backup path mismatch", failures)
    require(file_count == 19, "backup file count mismatch", failures)
    require(int(total_bytes or 0) == 165972871, "backup byte count mismatch", failures)
    require(diff_count == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(package["scripts"].get("test:ghidra-inflate-png-helper-head-wave713") == "py -3 tools\\ghidra_inflate_png_helper_head_wave713_probe.py --check", "package script missing", failures)

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
        require(any(row.get("task") == "Wave713 inflate / PNG helper head" for row in rows), f"{path.relative_to(ROOT)} missing Wave713 row", failures)

    tracking = read_json(TRACKING)
    require(tracking.get("counters", {}).get("ledger_rows") == 1109, "tracking ledger row count mismatch", failures)
    require(tracking.get("counters", {}).get("attempt_rows") == 20369, "tracking attempt row count mismatch", failures)
    require(tracking.get("next_attempt_id") == 20369, "tracking next attempt mismatch", failures)


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
        print("Wave713 inflate / PNG helper head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave713 inflate / PNG helper head probe: PASS")
    print("Targets: 11")
    print("Queue: 6098 total, 4154 commented, 1944 commentless, 1216 undefined, 183 param_N")
    print("Backup: G:\\GhidraBackups\\BEA_20260521-234937_post_wave713_inflate_png_helper_head_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
