#!/usr/bin/env python3
"""Validate Wave734 JPEG DCT/component/upsampler head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave734-jpeg-dct-component-upsampler-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_jpeg_dct_component_upsampler_head_wave734_2026-05-22.md"
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

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260522-110534_post_wave734_jpeg_dct_component_upsampler_head_verified"

COMMON_TAGS = {
    "static-reaudit",
    "jpeg-dct-component-upsampler-head-wave734",
    "wave734-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "jpeg-dct-component-upsampler-head",
    "signature-hardened",
}

TARGETS = {
    "0x005b5b80": (
        "CDXTexture__InitJpegDctQuantPipeline",
        "void __stdcall CDXTexture__InitJpegDctQuantPipeline(void * jpeg_codec_state)",
        ("DCT/quant pipeline", "state +0x170", "error id 0x30"),
        COMMON_TAGS | {"encoder-controller", "jpeg-dct-quant-pipeline", "jpeg-mode-dispatch", "ret-0x4", "tranche-head"},
    ),
    "0x005b60a0": (
        "CDXTexture__BuildComponentWorkBufferViews",
        "void __stdcall CDXTexture__BuildComponentWorkBufferViews(void * jpeg_codec_state)",
        ("per-component row/work-buffer view", "allocator callback +8", "0x54-byte"),
        COMMON_TAGS | {"component-sample-buffers", "component-work-buffer-views", "ret-0x4", "row-table-views"},
    ),
    "0x005b61e0": (
        "CDXTexture__InitComponentSampleBuffers",
        "void __stdcall CDXTexture__InitComponentSampleBuffers(void * jpeg_codec_state, int sample_buffer_mode)",
        ("sample-buffer controller", "error id 4", "CDXTexture__BuildComponentWorkBufferViews"),
        COMMON_TAGS | {"allocator-callbacks", "component-sample-buffers", "controller-init", "ret-0x8"},
    ),
    "0x005b6290": (
        "CDXTexture__PadRowsWithLastSample",
        "void __stdcall CDXTexture__PadRowsWithLastSample(void * row_table, int row_count, int valid_width_bytes, int padded_width_bytes)",
        ("repeating the row's last valid byte", "valid_width_bytes - 1", "trailing byte repeats"),
        COMMON_TAGS | {"last-sample-fill", "ret-0x10", "row-padding", "row-table-helper"},
    ),
    "0x005b6500": (
        "CDXTexture__UpsampleHorizontal_Average2_Scalar",
        "void __fastcall CDXTexture__UpsampleHorizontal_Average2_Scalar(void * source_row_table, void * component_descriptor, void * output_row_table)",
        ("scalar horizontal average-2", "hidden EAX", "half-pixel rounding"),
        COMMON_TAGS | {"average2", "hidden-eax-jpeg-state", "horizontal-upsampler", "row-table-helper", "scalar-kernel"},
    ),
    "0x005b65a0": (
        "CDXTexture__UpsampleHorizontal_Average2_Sse",
        "void __fastcall CDXTexture__UpsampleHorizontal_Average2_Sse(void * component_descriptor, void * jpeg_codec_state, void * source_row_table, void * output_row_table)",
        ("packed/SSE horizontal average-2", "DAT_005f4c00", "DAT_005f4bf0"),
        COMMON_TAGS | {"alignment-gated", "average2", "horizontal-upsampler", "row-table-helper", "sse-kernel"},
    ),
    "0x005b6650": (
        "CDXTexture__UpsampleBilinear2x2_Scalar",
        "void __fastcall CDXTexture__UpsampleBilinear2x2_Scalar(void * source_row_table, void * component_descriptor, void * output_row_table)",
        ("scalar bilinear 2x2", "hidden EAX", "alternating rounding bias"),
        COMMON_TAGS | {"2x2-average", "bilinear-upsampler", "hidden-eax-jpeg-state", "row-table-helper", "scalar-kernel"},
    ),
    "0x005b6720": (
        "CDXTexture__UpsampleBilinear2x2_Sse",
        "void __fastcall CDXTexture__UpsampleBilinear2x2_Sse(void * component_descriptor, void * jpeg_codec_state, void * source_row_table, void * output_row_table)",
        ("packed/SSE bilinear 2x2", "DAT_005f4c10", "DAT_005f4c08"),
        COMMON_TAGS | {"2x2-average", "alignment-gated", "bilinear-upsampler", "row-table-helper", "sse-kernel"},
    ),
    "0x005b6c30": (
        "CDXTexture__UpsampleDispatchHorizontal",
        "void __stdcall CDXTexture__UpsampleDispatchHorizontal(void * jpeg_codec_state, void * component_descriptor, void * source_row_table, void * output_row_table)",
        ("horizontal average-2 upsampling", "error id 2", "state +0xc4"),
        COMMON_TAGS | {"horizontal-upsampler-dispatch", "jpeg-mode-5-6", "ret-0x10", "sse-alignment-gate"},
    ),
    "0x005b6c90": (
        "CDXTexture__UpsampleDispatchBilinear",
        "void __stdcall CDXTexture__UpsampleDispatchBilinear(void * jpeg_codec_state, void * component_descriptor, void * source_row_table, void * output_row_table)",
        ("bilinear 2x2 upsampling", "error id 2", "state +0xc4"),
        COMMON_TAGS | {"bilinear-upsampler-dispatch", "jpeg-mode-5-6", "ret-0x10", "sse-alignment-gate"},
    ),
    "0x005b6cf0": (
        "CDXTexture__InitUpsamplerDispatch",
        "void __stdcall CDXTexture__InitUpsamplerDispatch(void * jpeg_codec_state)",
        ("upsampler dispatch/controller table", "0x34-byte controller", "sampling ratios"),
        COMMON_TAGS | {"component-sampling-ratio", "dispatch-table", "ret-0x4", "tranche-tail", "upsampler-dispatch-init"},
    ),
}

DOC_TOKENS = (
    "Wave734 JPEG DCT/component/upsampler head",
    "jpeg-dct-component-upsampler-head-wave734",
    "0x005b5b80 CDXTexture__InitJpegDctQuantPipeline",
    "0x005b60a0 CDXTexture__BuildComponentWorkBufferViews",
    "0x005b61e0 CDXTexture__InitComponentSampleBuffers",
    "0x005b6290 CDXTexture__PadRowsWithLastSample",
    "0x005b6500 CDXTexture__UpsampleHorizontal_Average2_Scalar",
    "0x005b65a0 CDXTexture__UpsampleHorizontal_Average2_Sse",
    "0x005b6650 CDXTexture__UpsampleBilinear2x2_Scalar",
    "0x005b6720 CDXTexture__UpsampleBilinear2x2_Sse",
    "0x005b6c30 CDXTexture__UpsampleDispatchHorizontal",
    "0x005b6c90 CDXTexture__UpsampleDispatchBilinear",
    "0x005b6cf0 CDXTexture__InitUpsamplerDispatch",
    "0x005b71b0 CDXTexture__ConvertRgbRowsToGrayscale",
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
        "pre-metadata.tsv": 11,
        "pre-tags.tsv": 11,
        "pre-xrefs.tsv": 17,
        "pre-instructions.tsv": 1595,
        "pre-decompile/index.tsv": 11,
        "caller-decompile/index.tsv": 5,
        "xref-site-instructions.tsv": 765,
        "post-metadata.tsv": 11,
        "post-tags.tsv": 11,
        "post-xrefs.tsv": 17,
        "post-instructions.tsv": 1595,
        "post-decompile/index.tsv": 11,
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
        require("Wave734 static read-back" in comment, f"missing Wave734 comment at {address}", failures)
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=11 found=11 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "pre-xrefs.log": "Wrote 17 rows",
        "pre-instructions.log": "Wrote 1595 instruction rows",
        "pre-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "caller-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "xref-site-instructions.log": "Wrote 765 instruction rows",
        "post-metadata.log": "targets=11 found=11 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "post-xrefs.log": "Wrote 17 rows",
        "post-instructions.log": "Wrote 1595 instruction rows",
        "post-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
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

    for relative in ("apply-dry.log", "apply.log", "apply-final-dry.log"):
        text = read_text(BASE / relative)
        require("FAIL:" not in text, f"unexpected FAIL in accepted log {relative}", failures)
        require("SCRIPT ERROR" not in text, f"unexpected SCRIPT ERROR in accepted log {relative}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1771, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 51, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005b71b0", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CDXTexture__ConvertRgbRowsToGrayscale", "high-signal head name mismatch", failures)

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
    require(commented == 4327, "commented count mismatch", failures)
    require(strict_clean == 4269, "strict clean-signature proxy mismatch", failures)
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
    require(int(backup.get("SourceBytes", 0)) == 166890375, "backup source byte count mismatch", failures)
    require(int(backup.get("DestinationBytes", 0)) == 166890375, "backup destination byte count mismatch", failures)
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
        package["scripts"].get("test:ghidra-jpeg-dct-component-upsampler-head-wave734")
        == r"py -3 tools\ghidra_jpeg_dct_component_upsampler_head_wave734_probe.py --check",
        "package script missing or mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave734 JPEG DCT/component/upsampler head" for row in ledger_rows), "missing Wave734 ledger row", failures)
    require(
        any(row.get("attempt_id") == 20389 and row.get("task") == "Wave734 JPEG DCT/component/upsampler head" for row in attempt_rows),
        "missing Wave734 attempt row",
        failures,
    )

    tracking = read_json(TRACKING)
    require(tracking["counters"]["ledger_rows"] == 1130, "tracking ledger_rows mismatch", failures)
    require(tracking["counters"]["attempt_rows"] == 20390, "tracking attempt_rows mismatch", failures)
    require(tracking["counters"]["completed"] == 1121, "tracking completed mismatch", failures)
    require(tracking["counters"]["pending"] == 9, "tracking pending mismatch", failures)
    require(tracking["next_attempt_id"] == 20390, "tracking next_attempt_id mismatch", failures)
    require("Wave734 JPEG DCT/component/upsampler head" in tracking.get("current_focus", ""), "tracking focus missing Wave734", failures)

    for state_path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(state_path)
        for token in ("Wave734 JPEG DCT/component/upsampler head", "0x005b71b0 CDXTexture__ConvertRgbRowsToGrayscale", BACKUP_PATH):
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
        print("Ghidra JPEG DCT/component/upsampler head Wave734 probe")
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Ghidra JPEG DCT/component/upsampler head Wave734 probe")
    print("Status: PASS")
    print("Targets: 11")
    print("Queue: 6098 total, 4327 commented, 1771 commentless, 1216 undefined, 51 param_N")
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
