#!/usr/bin/env python3
"""Validate Wave700 CTexture JPEG compression-defaults read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave700-ctexture-jpeg-deflate-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctexture_jpeg_compression_defaults_wave700_2026-05-21.md"
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

BASE_SIGNATURE_TAGS = {
    "static-reaudit",
    "ctexture-jpeg-compression-defaults-wave700",
    "wave700-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

BASE_COMMENT_ONLY_TAGS = {
    "static-reaudit",
    "ctexture-jpeg-compression-defaults-wave700",
    "wave700-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
}

TARGETS = {
    "0x00595350": (
        "CTexture__ProcessDecodeStateMachineStep",
        "void __stdcall CTexture__ProcessDecodeStateMachineStep(void * jpeg_compress_context)",
        ("pass controller", "0x65/0x66/0x67", "CDXTexture__PumpDecodeAllocatorAndSetStage"),
        BASE_SIGNATURE_TAGS | {"jpeg", "libjpeg", "pass-controller", "component-loop", "tranche-head"},
    ),
    "0x00595430": (
        "CTexture__ResetDecodePipelineForNextChunk",
        "void __stdcall CTexture__ResetDecodePipelineForNextChunk(void * jpeg_compress_context, int reset_sent_table_flags)",
        ("CTexture__SetDecodeTableEpoch", "+0xe8", "0x65 or 0x66"),
        BASE_SIGNATURE_TAGS | {"jpeg", "libjpeg", "pipeline-reset", "sent-table-state", "encoder-state"},
    ),
    "0x005954a0": (
        "CTexture__ReadDecodeInputBytes",
        "void __stdcall CTexture__ReadDecodeInputBytes(void * jpeg_compress_context, void * destination_buffer, uint requested_byte_count)",
        ("diagnostic 0x7b", "destination_buffer", "+0x158 +4"),
        BASE_SIGNATURE_TAGS | {"jpeg", "libjpeg", "source-manager", "input-read", "progress-callback"},
    ),
    "0x00595550": (
        "CTexture__LoadAndScaleQuantizationTable",
        "void __stdcall CTexture__LoadAndScaleQuantizationTable(void * jpeg_compress_context, int table_index, void * source_quant_table, int quality_scale_percent, int force_baseline_range)",
        ("table_index 0..3", "quality_scale_percent", "baseline"),
        BASE_SIGNATURE_TAGS | {"jpeg", "libjpeg", "quantization-table", "quality-scale", "baseline-clamp"},
    ),
    "0x00595820": (
        "CTexture__LoadHuffmanTableDefinition",
        "void __stdcall CTexture__LoadHuffmanTableDefinition(void * jpeg_compress_context, void * huff_values_table)",
        ("register-held bits/count header", "symbol budget", "huff_values_table"),
        BASE_SIGNATURE_TAGS | {"jpeg", "libjpeg", "huffman-table", "symbol-budget", "register-context"},
    ),
    "0x005958e0": (
        "CTexture__LoadDefaultHuffmanTables",
        "void CTexture__LoadDefaultHuffmanTables(void)",
        ("Signature intentionally left unchanged", "hidden ESI", "DAT_005eef80"),
        BASE_COMMENT_ONLY_TAGS | {"jpeg", "libjpeg", "huffman-table", "default-tables", "locked-storage"},
    ),
    "0x00595930": (
        "CTexture__DeflateConfig_SetPreset",
        "void __stdcall CTexture__DeflateConfig_SetPreset(void * jpeg_compress_context, int scan_script_preset)",
        ("despite the existing Deflate name", "JPEG scan-script", "RGB/CMYK/YCCK"),
        BASE_SIGNATURE_TAGS | {"jpeg", "libjpeg", "scan-script", "color-space-selectors", "legacy-deflate-name"},
    ),
    "0x00595c10": (
        "CTexture__ConfigureDeflatePresetByCompressionMode",
        "void __stdcall CTexture__ConfigureDeflatePresetByCompressionMode(void * jpeg_compress_context)",
        ("despite the existing Deflate name", "compression/color-mode", "diagnostic 0x09"),
        BASE_SIGNATURE_TAGS | {"jpeg", "libjpeg", "scan-script", "compression-mode", "legacy-deflate-name"},
    ),
    "0x00595da0": (
        "CTexture__InitializeJpegCompressionDefaults",
        "void __stdcall CTexture__InitializeJpegCompressionDefaults(void * jpeg_compress_context)",
        ("0x348-byte", "0x5eecd8/0x5eebd8", "default Huffman tables"),
        BASE_SIGNATURE_TAGS | {"jpeg", "libjpeg", "compression-defaults", "quantization-table", "huffman-table", "scan-script", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave700 CTexture JPEG compression defaults",
    "ctexture-jpeg-compression-defaults-wave700",
    "0x00595350 CTexture__ProcessDecodeStateMachineStep",
    "0x00595da0 CTexture__InitializeJpegCompressionDefaults",
    "0x005960c1 CDXTexture__FastReciprocalSqrtScalar",
)

OVERCLAIM_TOKENS = (
    "runtime jpeg encoder behavior proven",
    "runtime entropy-table behavior proven",
    "runtime image fidelity proven",
    "zlib deflate proven",
    "libjpeg source identity proven",
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
        "pre-metadata.tsv": 9,
        "pre-tags.tsv": 9,
        "pre-xrefs.tsv": 15,
        "pre-instructions.tsv": 333,
        "decompile-pre/index.tsv": 9,
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 15,
        "post-instructions.tsv": 333,
        "decompile-post/index.tsv": 9,
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
        require("Wave700 static read-back" in comment, f"missing Wave700 comment at {address}", failures)
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
        require((BASE / "decompile-post" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-wave700-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=1 missing=0 bad=0",
        "apply-wave700-apply.log": "SUMMARY: updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=1 missing=0 bad=0",
        "apply-wave700-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=9 found=9 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "pre-xrefs.log": "Wrote 15 rows",
        "pre-instructions.log": "Wrote 333 instruction rows",
        "pre-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-xrefs.log": "Wrote 15 rows",
        "post-instructions.log": "Wrote 333 instruction rows",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "queue-refresh.log": "total_functions=6098 commented_functions=4033",
        "queue-probe-after-refresh.log": "Status: PASS",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text or filename == "queue-probe-after-refresh.log", f"save report missing in {filename}", failures)
        require("Input file not found" not in text, f"bad input path found in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 2065, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 293, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x005960c1", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CDXTexture__FastReciprocalSqrtScalar", f"next head name mismatch: {head}", failures)

    rows = read_tsv(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv")
    param_re = re.compile(r"\bparam_\d+\b")
    clean = [
        row for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not param_re.search(row.get("signature", ""))
    ]
    require(len(clean) == 3979, f"strict clean proxy mismatch: {len(clean)}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(
        backup.get("backup_path").replace("\\", "/")
        == "[maintainer-local-ghidra-backup-root]/BEA_20260521-165600_post_wave700_ctexture_jpeg_compression_defaults_verified",
        "backup path mismatch",
        failures,
    )
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(float(backup.get("total_bytes"))) == 165219207, f"backup bytes mismatch: {backup}", failures)
    require(backup.get("diff_count") == 0, f"backup diff mismatch: {backup}", failures)


def check_docs(failures: list[str]) -> None:
    for path in (
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        lower = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lower, f"{path.relative_to(ROOT)} contains overclaim token: {token}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-ctexture-jpeg-compression-defaults-wave700")
        == "py -3 tools\\ghidra_ctexture_jpeg_compression_defaults_wave700_probe.py --check",
        "package script missing or mismatched",
        failures,
    )

    attempt = [row for row in read_jsonl(ATTEMPT_LOG) if row.get("task") == "Wave700 CTexture JPEG compression defaults"]
    ledger = [row for row in read_jsonl(LEDGER) if row.get("task") == "Wave700 CTexture JPEG compression defaults"]
    require(len(attempt) == 1 and attempt[0].get("attempt_id") == 20355, "Wave700 attempt log row missing/mismatched", failures)
    require(len(ledger) == 1 and ledger[0].get("status") == "completed", "Wave700 ledger row missing/mismatched", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20356, "tracking next_attempt_id mismatch", failures)


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
        print("Wave700 CTexture JPEG compression defaults probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave700 CTexture JPEG compression defaults probe: PASS")
    print("Targets: 9")
    print("Queue: 6098 total, 4033 commented, 2065 commentless, 1216 exact-undefined, 293 param_N")
    print("Strict clean-signature proxy: 3979/6098 = 65.25%")
    print("Next head: 0x005960c1 CDXTexture__FastReciprocalSqrtScalar")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
