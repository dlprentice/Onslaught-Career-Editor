#!/usr/bin/env python3
"""Validate Wave716 JPEG writer head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave716-jpeg-writer-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_jpeg_writer_head_wave716_2026-05-22.md"
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

SIGNATURE_TAGS = {
    "static-reaudit",
    "jpeg-writer-head-wave716",
    "wave716-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "jpeg-writer-head",
}

COMMENT_ONLY_TAGS = {
    "static-reaudit",
    "jpeg-writer-head-wave716",
    "wave716-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
    "jpeg-writer-head",
}

TARGETS = {
    "0x0059dfb2": (
        "CDXTexture__Crc32_Update",
        "uint __stdcall CDXTexture__Crc32_Update(uint crc_seed, void * source_bytes, uint byte_count)",
        ("CRC-32", "DAT_005f3ec0", "8-byte body loop"),
        SIGNATURE_TAGS | {"crc32", "texture-checksum", "table-driven", "tranche-head"},
    ),
    "0x0059e0b0": (
        "CDXTexture__WriteJpegMarkerByte",
        "void __stdcall CDXTexture__WriteJpegMarkerByte(int marker_byte)",
        ("0xff marker prefix", "marker_byte", "ESI-held"),
        SIGNATURE_TAGS | {"jpeg", "marker-writer", "output-buffer", "hidden-esi-context"},
    ),
    "0x0059e110": (
        "CDXTexture__WriteJpegQuantTable",
        "char __stdcall CDXTexture__WriteJpegQuantTable(int quant_table_index)",
        ("DQT marker 0xffdb", "zigzag", "0x34"),
        SIGNATURE_TAGS | {"jpeg", "quant-table", "DQT", "zigzag", "hidden-esi-context"},
    ),
    "0x0059e310": (
        "CDXTexture__WriteJpegHuffmanTable",
        "void __thiscall CDXTexture__WriteJpegHuffmanTable(void * this, void * param_1, int param_2)",
        ("DHT segment", "hidden EAX", "Signature intentionally left unchanged"),
        COMMENT_ONLY_TAGS | {"jpeg", "huffman-table", "DHT", "hidden-eax-context"},
    ),
    "0x0059e4a0": (
        "CDXTexture__WriteJpegRestartIntervalMarker",
        "void CDXTexture__WriteJpegRestartIntervalMarker(void)",
        ("DRI marker 0xffdd", "register-held context", "Signature intentionally left unchanged"),
        COMMENT_ONLY_TAGS | {"jpeg", "restart-interval", "DRI", "hidden-esi-context"},
    ),
    "0x0059e580": (
        "CDXTexture__WriteJpegFrameHeader",
        "void __fastcall CDXTexture__WriteJpegFrameHeader(void * jpeg_encoder_state)",
        ("frame-header", "hidden EAX marker", "0xffff"),
        SIGNATURE_TAGS | {"jpeg", "frame-header", "SOF", "hidden-eax-marker"},
    ),
    "0x0059e770": (
        "CDXTexture__WriteJpegScanHeader",
        "void CDXTexture__WriteJpegScanHeader(void)",
        ("SOS marker 0xffda", "spectral-selection", "Signature intentionally left unchanged"),
        COMMENT_ONLY_TAGS | {"jpeg", "scan-header", "SOS", "hidden-esi-context"},
    ),
    "0x0059e970": (
        "CDXTexture__WriteJpegApp0JfifSegment",
        "void CDXTexture__WriteJpegApp0JfifSegment(void)",
        ("APP0/JFIF", "0xffe0", "Signature intentionally left unchanged"),
        COMMENT_ONLY_TAGS | {"jpeg", "APP0", "JFIF", "hidden-esi-context"},
    ),
    "0x0059ebf0": (
        "CDXTexture__WriteJpegApp14AdobeMarker",
        "void CDXTexture__WriteJpegApp14AdobeMarker(void)",
        ("APP14/Adobe", "0xffee", "Signature intentionally left unchanged"),
        COMMENT_ONLY_TAGS | {"jpeg", "APP14", "Adobe-marker", "hidden-esi-context"},
    ),
    "0x0059ee20": (
        "CDXTexture__WriteJpegSegmentMarkerAndLength",
        "void __stdcall CDXTexture__WriteJpegSegmentMarkerAndLength(void * jpeg_encoder_state, int marker_byte, uint payload_byte_count)",
        ("0xfffd", "payload_byte_count plus two", "big-endian"),
        SIGNATURE_TAGS | {"jpeg", "segment-length", "marker-writer", "big-endian"},
    ),
    "0x0059eed0": (
        "CDXTexture__WriteJpegStartOfImageAndMetadata",
        "void __stdcall CDXTexture__WriteJpegStartOfImageAndMetadata(void * jpeg_encoder_state)",
        ("SOI bytes 0xffd8", "APP0/JFIF", "APP14/Adobe"),
        SIGNATURE_TAGS | {"jpeg", "SOI", "metadata", "APP0", "APP14"},
    ),
    "0x0059ef60": (
        "CDXTexture__WriteJpegQuantTablesAndFrame",
        "void __stdcall CDXTexture__WriteJpegQuantTablesAndFrame(void * jpeg_encoder_state)",
        ("CDXTexture__WriteJpegQuantTable", "error id 0x4b", "frame header"),
        SIGNATURE_TAGS | {"jpeg", "quant-table", "frame-header", "DQT", "SOF"},
    ),
    "0x0059f050": (
        "CDXTexture__WriteJpegHuffmanAndScanHeaders",
        "void __stdcall CDXTexture__WriteJpegHuffmanAndScanHeaders(void * jpeg_encoder_state)",
        ("hidden EBX", "restart interval", "scan header"),
        SIGNATURE_TAGS | {"jpeg", "huffman-table", "scan-header", "DHT", "SOS", "hidden-ebx-context"},
    ),
    "0x0059f110": (
        "CDXTexture__WriteJpegEndOfImage",
        "void __stdcall CDXTexture__WriteJpegEndOfImage(void * jpeg_encoder_state)",
        ("EOI bytes 0xffd9", "writer state layout"),
        SIGNATURE_TAGS | {"jpeg", "EOI", "tranche-end-marker"},
    ),
    "0x0059f260": (
        "CDXTexture__InitJpegWriterStageCallbacks",
        "void __stdcall CDXTexture__InitJpegWriterStageCallbacks(void * jpeg_encoder_state)",
        ("0x20-byte writer-stage callback table", "+0x164", "callback table"),
        SIGNATURE_TAGS | {"jpeg", "stage-callbacks", "writer-pipeline", "callback-table"},
    ),
    "0x0059f2b0": (
        "CDXTexture__InitializeJpegEncoderPipeline",
        "void __stdcall CDXTexture__InitializeJpegEncoderPipeline(void * jpeg_encoder_state)",
        ("JPEG encoder pipeline", "writer-stage callbacks", "Static metadata only"),
        SIGNATURE_TAGS | {"jpeg", "encoder-pipeline", "pipeline-init", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave716 JPEG writer head",
    "jpeg-writer-head-wave716",
    "0x0059dfb2 CDXTexture__Crc32_Update",
    "0x0059e110 CDXTexture__WriteJpegQuantTable",
    "0x0059e310 CDXTexture__WriteJpegHuffmanTable",
    "0xffdb",
    "0xffc4",
    "0xffd9",
    "0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360",
    "0x0042f220 CSPtrSet__Clear",
    r"G:\GhidraBackups\BEA_20260522-013644_post_wave716_jpeg_writer_head_verified",
)

OVERCLAIM_TOKENS = (
    "runtime jpeg output fidelity proven",
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
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    expected_counts = {
        "pre-metadata.tsv": 16,
        "pre-tags.tsv": 16,
        "pre-xrefs.tsv": 25,
        "pre-instructions.tsv": 1104,
        "pre-decompile/index.tsv": 16,
        "post-metadata.tsv": 16,
        "post-tags.tsv": 16,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 1104,
        "post-decompile/index.tsv": 16,
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
        require("Wave716 static read-back" in comment, f"missing Wave716 comment at {address}", failures)
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


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=5 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=16 skipped=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=5 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=16 found=16 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=16 missing=0",
        "pre-xrefs.log": "Wrote 25 rows",
        "pre-instructions.log": "Wrote 1104 instruction rows",
        "pre-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
        "post-metadata.log": "targets=16 found=16 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=16 missing=0",
        "post-xrefs.log": "Wrote 25 rows",
        "post-instructions.log": "Wrote 1104 instruction rows",
        "post-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
        "export-queue-refresh.log": "total_functions=6098 commented_functions=4183",
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
        "Commentless functions: 1915",
        "Undefined signatures: 1216",
        "Param signatures: 159",
    ):
        require(token in queue_probe, f"missing queue probe token: {token}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    require(signals.get("commentlessFunctionCount") == 1915, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1216, "queue undefined mismatch", failures)
    require(signals.get("paramSignatureCount") == 159, "queue param mismatch", failures)
    high = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high["address"] == "0x0059f360", "high-signal head mismatch", failures)
    require(high["name"] == "CFastVB__DispatchOp_TransformVec4_0059f360", "high-signal head name mismatch", failures)

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
    require(len(strict) == 4126, "strict clean-signature proxy mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    backup_path = backup.get("backup_path") or backup.get("backupPath")
    file_count = backup.get("file_count") or backup.get("fileCount")
    total_bytes = backup.get("total_bytes") or backup.get("totalBytes")
    diff_count = backup.get("diff_count") if "diff_count" in backup else backup.get("diffCount")
    require(backup_path == r"G:\GhidraBackups\BEA_20260522-013644_post_wave716_jpeg_writer_head_verified", "backup path mismatch", failures)
    require(file_count == 19, "backup file count mismatch", failures)
    require(int(total_bytes or 0) == 166103943, "backup byte count mismatch", failures)
    require(diff_count == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(
        package["scripts"].get("test:ghidra-jpeg-writer-head-wave716")
        == "py -3 tools\\ghidra_jpeg_writer_head_wave716_probe.py --check",
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
        require(any(row.get("task") == "Wave716 JPEG writer head" for row in rows), f"{path.relative_to(ROOT)} missing Wave716 row", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(counters.get("ledger_rows") == 1112, "tracking ledger row count mismatch", failures)
    require(counters.get("attempt_rows") == 20372, "tracking attempt row count mismatch", failures)
    require(counters.get("completed") == 1103, "tracking completed count mismatch", failures)
    require(tracking.get("next_attempt_id") == 20372, "tracking next attempt mismatch", failures)


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
        print("Wave716 JPEG writer head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave716 JPEG writer head probe: PASS")
    print("Targets: 16")
    print("Queue: 6098 total, 4183 commented, 1915 commentless, 1216 undefined, 159 param_N")
    print("Backup: G:\\GhidraBackups\\BEA_20260522-013644_post_wave716_jpeg_writer_head_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
