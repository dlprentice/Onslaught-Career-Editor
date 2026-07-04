#!/usr/bin/env python3
"""Validate Wave733 JPEG entropy/frequency head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave733-jpeg-entropy-frequency-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_jpeg_entropy_frequency_head_wave733_2026-05-22.md"
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

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260522-103248_post_wave733_jpeg_entropy_frequency_head_verified"

COMMON_TAGS = {
    "static-reaudit",
    "jpeg-entropy-frequency-head-wave733",
    "wave733-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "jpeg-entropy-frequency-head",
}

TARGETS = {
    "0x005b3840": (
        "CDXTexture__AccumulateJpegHuffmanFrequenciesFromBlock",
        "void __stdcall CDXTexture__AccumulateJpegHuffmanFrequenciesFromBlock(void * jpeg_encoder_state, void * coeff_block, void * ac_frequency_counts)",
        ("hidden ECX", "hidden EAX", "DAT_005f37fc"),
        COMMON_TAGS | {"signature-hardened", "hidden-ecx-previous-dc", "hidden-eax-dc-table", "jpeg-huffman-frequency", "ret-0xc", "tranche-head"},
    ),
    "0x005b3920": (
        "CDXTexture__EncodeMcuBlocksForScan",
        "int __stdcall CDXTexture__EncodeMcuBlocksForScan(void * jpeg_encoder_state, void * coeff_block_table)",
        ("frequency-count pass", "restart-interval", "DC predictors"),
        COMMON_TAGS | {"signature-hardened", "jpeg-mcu-frequency-pass", "jpeg-scan-components", "dc-predictor-update", "ret-0x8"},
    ),
    "0x005b39d0": (
        "CDXTexture__BuildCanonicalHuffmanCodes",
        "void __stdcall CDXTexture__BuildCanonicalHuffmanCodes(void * jpeg_encoder_state, void * out_huffman_descriptor, void * frequency_counts)",
        ("canonical JPEG Huffman", "0x101", "descriptor +0x114"),
        COMMON_TAGS | {"signature-hardened", "jpeg-canonical-huffman", "huffman-frequency-counts", "jpeg-length-limit", "ret-0xc"},
    ),
    "0x005b3e80": (
        "CDXTexture__InitJpegEntropyEncoderState",
        "void __stdcall CDXTexture__InitJpegEntropyEncoderState(void * jpeg_encoder_state)",
        ("0x6c-byte controller", "encoder state +0x174", "0x005b3d20"),
        COMMON_TAGS | {"signature-hardened", "encoder-controller", "jpeg-entropy-state", "ret-0x4"},
    ),
    "0x005b3ec0": (
        "CDXTexture__WriteEntropyBitsWithByteStuffing",
        "void __stdcall CDXTexture__WriteEntropyBitsWithByteStuffing(uint bit_value)",
        ("hidden EAX", "hidden ESI", "0xff"),
        COMMON_TAGS | {"signature-hardened", "hidden-eax-esi", "jpeg-entropy-bit-writer", "byte-stuffing", "ret-0x4"},
    ),
    "0x005b3fd0": (
        "CDXTexture__FlushEntropyBitWriter",
        "void CDXTexture__FlushEntropyBitWriter(void)",
        ("hidden EAX", "Comment/tag-only", "frequency-collection mode"),
        COMMON_TAGS | {"comment-only", "hidden-eax-writer", "jpeg-entropy-flush", "unknown-locked-calling-convention"},
    ),
    "0x005b4080": (
        "CDXTexture__EmitRestartMarkerAndReset",
        "void __stdcall CDXTexture__EmitRestartMarkerAndReset(int restart_marker_code)",
        ("hidden EAX", "0xff marker", "DC predictors"),
        COMMON_TAGS | {"signature-hardened", "hidden-eax-writer", "jpeg-restart-marker", "dc-predictor-reset", "ret-0x4"},
    ),
    "0x005b44c0": (
        "CDXTexture__WriteEncodedBlockWithRestartControl",
        "int __stdcall CDXTexture__WriteEncodedBlockWithRestartControl(void * jpeg_encoder_state, void * coeff_block_table)",
        ("restart-interval control", "output cursor", "modulo 8"),
        COMMON_TAGS | {"signature-hardened", "jpeg-encoded-block-restart", "restart-control", "output-cursor-snapshot", "ret-0x8"},
    ),
    "0x005b4ae0": (
        "CDXTexture__InitJpegEncoderScanScriptState",
        "void __stdcall CDXTexture__InitJpegEncoderScanScriptState(void * jpeg_encoder_state)",
        ("scan-script", "0x6c-byte controller", "0x005b4950"),
        COMMON_TAGS | {"signature-hardened", "encoder-controller", "jpeg-scan-script-state", "ret-0x4", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave733 JPEG entropy/frequency head",
    "jpeg-entropy-frequency-head-wave733",
    "0x005b3840 CDXTexture__AccumulateJpegHuffmanFrequenciesFromBlock",
    "0x005b3920 CDXTexture__EncodeMcuBlocksForScan",
    "0x005b39d0 CDXTexture__BuildCanonicalHuffmanCodes",
    "0x005b3e80 CDXTexture__InitJpegEntropyEncoderState",
    "0x005b3ec0 CDXTexture__WriteEntropyBitsWithByteStuffing",
    "0x005b3fd0 CDXTexture__FlushEntropyBitWriter",
    "0x005b4080 CDXTexture__EmitRestartMarkerAndReset",
    "0x005b44c0 CDXTexture__WriteEncodedBlockWithRestartControl",
    "0x005b4ae0 CDXTexture__InitJpegEncoderScanScriptState",
    "0x005b5b80 CDXTexture__InitJpegDctQuantPipeline",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime jpeg output behavior proven",
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
        "pre-metadata.tsv": 9,
        "pre-tags.tsv": 9,
        "pre-xrefs.tsv": 36,
        "pre-instructions.tsv": 3069,
        "pre-decompile/index.tsv": 9,
        "caller-decompile/index.tsv": 5,
        "xref-site-instructions.tsv": 713,
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 36,
        "post-instructions.tsv": 3069,
        "post-decompile/index.tsv": 9,
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
        require("Wave733 static read-back" in comment, f"missing Wave733 comment at {address}", failures)
        require("static retail ghidra metadata" in comment.lower(), f"missing static-evidence boundary at {address}", failures)
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=1 missing=0 bad=0",
        "apply-initial-failed.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=1 missing=0 bad=1",
        "apply-reconcile-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=8 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=9 found=9 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "pre-xrefs.log": "Wrote 36 rows",
        "pre-instructions.log": "Wrote 3069 instruction rows",
        "pre-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "caller-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "xref-site-instructions.log": "Wrote 713 instruction rows",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-xrefs.log": "Wrote 36 rows",
        "post-instructions.log": "Wrote 3069 instruction rows",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}", failures)
        require("REPORT: Save succeeded" in text, f"missing save evidence in {relative}", failures)
        require("LockException" not in text, f"unexpected LockException in {relative}", failures)
        require("MISSING:" not in text, f"unexpected MISSING in {relative}", failures)
        require("BADNAME" not in text, f"unexpected BADNAME in {relative}", failures)
        require("Invalid script" not in text, f"unexpected Invalid script in {relative}", failures)
        require("Input file not found" not in text, f"unexpected missing input in {relative}", failures)

    failed_text = read_text(BASE / "apply-initial-failed.log")
    require("FAIL: 0x005b3840" in failed_text, "initial failed log missing expected 0x005b3840 failure", failures)
    require("SCRIPT ERROR" in failed_text, "initial failed log missing expected script error", failures)
    require("__thiscall" in failed_text and "Read-back signature mismatch" in failed_text, "initial failed log missing expected mismatch text", failures)
    for relative in ("apply-dry.log", "apply-reconcile-dry.log", "apply.log", "apply-final-dry.log"):
        text = read_text(BASE / relative)
        require("FAIL:" not in text, f"unexpected FAIL in accepted log {relative}", failures)
        require("SCRIPT ERROR" not in text, f"unexpected SCRIPT ERROR in accepted log {relative}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1782, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 62, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005b5b80", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CDXTexture__InitJpegDctQuantPipeline", "high-signal head name mismatch", failures)

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
    require(commented == 4316, "commented count mismatch", failures)
    require(strict_clean == 4258, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    for address in TARGETS:
        row = next((item for item in rows if normalize_address(item["address"]) == address), None)
        require(row is not None, f"missing queue row {address}", failures)
        if row is not None:
            require(bool(row.get("comment", "").strip()), f"queue row still commentless {address}", failures)
            require(row["signature"] == TARGETS[address][1], f"queue signature mismatch {address}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("Destination") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("SourceFileCount") == 19, "backup source file count mismatch", failures)
    require(backup.get("DestinationFileCount") == 19, "backup destination file count mismatch", failures)
    require(int(backup.get("SourceBytes", 0)) == 166857607, "backup source byte count mismatch", failures)
    require(int(backup.get("DestinationBytes", 0)) == 166857607, "backup destination byte count mismatch", failures)
    require(backup.get("DiffCount") == 0, "backup diff count mismatch", failures)


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
        package["scripts"].get("test:ghidra-jpeg-entropy-frequency-head-wave733")
        == r"py -3 tools\ghidra_jpeg_entropy_frequency_head_wave733_probe.py --check",
        "package script missing or mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave733 JPEG entropy/frequency head" for row in ledger_rows), "missing Wave733 ledger row", failures)
    require(
        any(row.get("attempt_id") == 20388 and row.get("task") == "Wave733 JPEG entropy/frequency head" for row in attempt_rows),
        "missing Wave733 attempt row",
        failures,
    )

    tracking = read_json(TRACKING)
    require(tracking["counters"]["ledger_rows"] == 1129, "tracking ledger_rows mismatch", failures)
    require(tracking["counters"]["attempt_rows"] == 20389, "tracking attempt_rows mismatch", failures)
    require(tracking["counters"]["completed"] == 1120, "tracking completed mismatch", failures)
    require(tracking["counters"]["pending"] == 9, "tracking pending mismatch", failures)
    require(tracking["next_attempt_id"] == 20389, "tracking next_attempt_id mismatch", failures)
    require("Wave733 JPEG entropy/frequency head" in tracking.get("current_focus", ""), "tracking focus missing Wave733", failures)

    for state_path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(state_path)
        for token in ("Wave733 JPEG entropy/frequency head", "0x005b5b80 CDXTexture__InitJpegDctQuantPipeline", BACKUP_PATH):
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
        print("Ghidra JPEG entropy/frequency head Wave733 probe")
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Ghidra JPEG entropy/frequency head Wave733 probe")
    print("Status: PASS")
    print("Targets: 9")
    print("Queue: 6098 total, 4316 commented, 1782 commentless, 1216 undefined, 62 param_N")
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
