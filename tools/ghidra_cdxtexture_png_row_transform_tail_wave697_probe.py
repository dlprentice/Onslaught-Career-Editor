#!/usr/bin/env python3
"""Validate Wave697 CDXTexture PNG row-transform-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave697-cdxtexture-png-row-transform-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_png_row_transform_tail_wave697_2026-05-21.md"
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
    "cdxtexture-png-row-transform-tail-wave697",
    "wave697-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

TARGETS = {
    "0x00593d0b": (
        "CDXTexture__PngStrip16BitSamplesTo8Bit",
        "void __stdcall CDXTexture__PngStrip16BitSamplesTo8Bit(void * png_row_descriptor, void * row_buffer)",
        ("bit-depth byte at +0x9", "16-bit samples", "host-endian policy"),
        BASE_SIGNATURE_TAGS | {"png", "row-transform", "strip16", "expand-to-8bit", "tranche-head"},
    ),
    "0x00593d51": (
        "CDXTexture__PngInsertFillerChannel",
        "void __stdcall CDXTexture__PngInsertFillerChannel(void * png_row_descriptor, void * row_buffer, uint filler_sample_value, uint layout_flags)",
        ("filler_sample_value", "layout_flags bit 0x80", "filler enum"),
        BASE_SIGNATURE_TAGS | {"png", "row-transform", "filler-channel", "layout-flags"},
    ),
    "0x00593f8a": (
        "CDXTexture__PngApplyRowTransformLuts",
        "void __stdcall CDXTexture__PngApplyRowTransformLuts(void * png_row_descriptor, void * row_buffer, int byte_lut_table, void * word_lut_table, int word_lut_index_shift)",
        ("byte and 16-bit LUT tables", "word_lut_index_shift", "runtime gamma behavior"),
        BASE_SIGNATURE_TAGS | {"png", "row-transform", "gamma", "lut", "significant-bits"},
    ),
    "0x005942da": (
        "CDXTexture__ExpandIndexedRowToRgbOrRgba",
        "void __stdcall CDXTexture__ExpandIndexedRowToRgbOrRgba(void * png_row_descriptor, void * row_buffer, void * palette_rgb_table, void * palette_alpha_table, int palette_alpha_count)",
        ("indexed-color rows", "PLTE table", "tRNS semantics"),
        BASE_SIGNATURE_TAGS | {"png", "row-transform", "palette", "plte", "transparency"},
    ),
    "0x005944e3": (
        "CDXTexture__PngExpandTransparentColorToAlpha",
        "void __stdcall CDXTexture__PngExpandTransparentColorToAlpha(void * png_row_descriptor, void * row_buffer, void * transparent_color_record)",
        ("transparent_color_record", "gray+alpha", "tRNS record layout"),
        BASE_SIGNATURE_TAGS | {"png", "row-transform", "transparency", "trns", "alpha"},
    ),
    "0x00594836": (
        "CDXTexture__PngConvertRgbRowsToPaletteIndices",
        "void __stdcall CDXTexture__PngConvertRgbRowsToPaletteIndices(void * png_row_descriptor, void * row_buffer, void * rgb_to_palette_lut, void * index_remap_lut)",
        ("RGB-to-palette lookup", "index LUT", "RGB key packing"),
        BASE_SIGNATURE_TAGS | {"png", "row-transform", "palette", "rgb-to-index"},
    ),
    "0x00594945": (
        "CDXTexture__BuildPngGammaAndExpandTables",
        "void __stdcall CDXTexture__BuildPngGammaAndExpandTables(void * png_decode_state)",
        ("gamma or expand LUT", "+0x12c", "color-management policy"),
        BASE_SIGNATURE_TAGS | {"png", "gamma", "lut", "expand-table", "color-management"},
    ),
    "0x00594c48": (
        "CDXTexture__ApplyPngPostDecodeTransforms",
        "void __stdcall CDXTexture__ApplyPngPostDecodeTransforms(void * png_decode_state)",
        ("palette gamma adjustment", "PLTE RGB entries", "transform flag enum"),
        BASE_SIGNATURE_TAGS | {"png", "postprocess-layout", "gamma", "palette", "significant-bits"},
    ),
    "0x00594d5c": (
        "CDXTexture__ApplyPngRowTransforms",
        "void __stdcall CDXTexture__ApplyPngRowTransforms(void * png_decode_state)",
        ("dispatches PNG row transforms", "filler insertion", "transform order"),
        BASE_SIGNATURE_TAGS | {"png", "row-transform", "dispatcher", "transform-options", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave697 CDXTexture PNG row-transform tail",
    "cdxtexture-png-row-transform-tail-wave697",
    "0x00593d0b CDXTexture__PngStrip16BitSamplesTo8Bit",
    "0x00594d5c CDXTexture__ApplyPngRowTransforms",
    "0x00594ef8 CDXTexture__SetDecodeOptionFloat",
)

OVERCLAIM_TOKENS = (
    "runtime png transform behavior proven",
    "runtime row behavior proven",
    "png decoder layout proven",
    "row descriptor layout proven",
    "transform-option enum proven",
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
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


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
    decompile_index = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-post" / "index.tsv")}

    require(len(metadata) == len(TARGETS), f"metadata row count is {len(metadata)}", failures)
    require(len(tags) == len(TARGETS), f"tag row count is {len(tags)}", failures)
    require(len(decompile_index) == len(TARGETS), f"decompile index row count is {len(decompile_index)}", failures)
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 9, "post xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 333, "post instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata.tsv")) == 9, "pre metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags.tsv")) == 9, "pre tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs.tsv")) == 9, "pre xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions.tsv")) == 333, "pre instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-pre" / "index.tsv")) == 9, "pre decompile row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata-candidate.tsv")) == 17, "candidate metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags-candidate.tsv")) == 17, "candidate tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs-candidate.tsv")) == 27, "candidate xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-candidate.tsv")) == 629, "candidate instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")) == 17, "candidate decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave697 static read-back" in comment, f"missing Wave697 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}: {tag_row.get('status')}", failures)

        decompile_row = decompile_index.get(address)
        require(decompile_row is not None, f"missing decompile index for {address}", failures)
        if decompile_row is not None:
            require(decompile_row.get("signature") == expected_signature, f"decompile signature mismatch at {address}", failures)
            require(decompile_row.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "decompile-post" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-wave697-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=0 missing=0 bad=0",
        "apply-wave697-apply.log": "SUMMARY: updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=0 missing=0 bad=0",
        "apply-wave697-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "post-instructions.log": "Wrote 333 instruction rows",
        "post-xrefs.log": "Wrote 9 rows",
        "pre-metadata.log": "targets=9 found=9 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "pre-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "pre-instructions.log": "Wrote 333 instruction rows",
        "pre-xrefs.log": "Wrote 9 rows",
        "pre-metadata-candidate.log": "targets=17 found=17 missing=0",
        "pre-tags-candidate.log": "ExportFunctionTagsByAddress complete: rows=17 missing=0",
        "pre-decompile-candidate.log": "targets=17 dumped=17 missing=0 failed=0",
        "pre-instructions-candidate.log": "Wrote 629 instruction rows",
        "pre-xrefs-candidate.log": "Wrote 27 rows",
        "queue-refresh.log": "total_functions=6098 commented_functions=4008",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("Input file not found" not in text, f"bad input path found in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 2090, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 318, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x00594ef8", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CDXTexture__SetDecodeOptionFloat", f"next head name mismatch: {head}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup_path").replace("\\", "/") == "G:/GhidraBackups/BEA_20260521-154041_post_wave697_cdxtexture_png_row_transform_tail_verified", "backup path mismatch", failures)
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(backup.get("total_bytes")) == 165120903, f"backup bytes mismatch: {backup}", failures)
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
            require(token in text, f"{path.relative_to(ROOT)} missing {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path.relative_to(ROOT)} contains overclaim token {token}", failures)

    package = json.loads(read_text(PACKAGE_JSON))
    require(
        package.get("scripts", {}).get("test:ghidra-cdxtexture-png-row-transform-tail-wave697")
        == "py -3 tools\\ghidra_cdxtexture_png_row_transform_tail_wave697_probe.py --check",
        "package script missing/mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave697 CDXTexture PNG row-transform tail" for row in ledger_rows), "ledger missing Wave697", failures)
    require(any(row.get("task") == "Wave697 CDXTexture PNG row-transform tail" for row in attempt_rows), "attempt log missing Wave697", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20353, f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    require(any("Wave697 CDXTexture PNG row-transform tail" in note for note in tracking.get("notes", [])), "tracking notes missing Wave697", failures)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_metadata(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave697 CDXTexture PNG row-transform-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave697 CDXTexture PNG row-transform-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
