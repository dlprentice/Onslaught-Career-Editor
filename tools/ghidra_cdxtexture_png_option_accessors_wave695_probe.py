#!/usr/bin/env python3
"""Validate Wave695 CDXTexture PNG option accessor read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave695-cdxtexture-png-option-accessors"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_png_option_accessors_wave695_2026-05-21.md"
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
    "cdxtexture-png-option-accessors-wave695",
    "wave695-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

TARGETS = {
    "0x00593526": (
        "CDXTexture__ReleasePngDecodeContextHandles",
        "void __stdcall CDXTexture__ReleasePngDecodeContextHandles(void * png_decode_context_slot, void * primary_row_workspace_slot, void * secondary_row_workspace_slot)",
        ("owned slot", "CDXTexture__ResetPngDecodeContext", "allocator ABI"),
        BASE_SIGNATURE_TAGS | {"png", "cleanup", "owned-slot-release", "row-workspace", "tranche-head"},
    ),
    "0x005935a3": (
        "CDXTexture__TestDecodeOptionFlagMask",
        "uint __stdcall CDXTexture__TestDecodeOptionFlagMask(void * png_decode_state, void * png_info_state, uint flag_mask)",
        ("info_state +0x8", "flag_mask", "flag enum identity"),
        BASE_SIGNATURE_TAGS | {"png", "option-flags", "info-state", "bitmask"},
    ),
    "0x005935c0": (
        "CDXTexture__GetDecodeRowStride",
        "int __stdcall CDXTexture__GetDecodeRowStride(void * png_decode_state, void * png_info_state)",
        ("info_state +0xc", "row-stride", "rowbytes type"),
        BASE_SIGNATURE_TAGS | {"png", "row-stride", "info-state", "accessor"},
    ),
    "0x005935d9": (
        "CDXTexture__GetOutputChannelCount",
        "int __stdcall CDXTexture__GetOutputChannelCount(void * png_decode_state, void * png_info_state)",
        ("info_state +0x1d", "channel count", "color-type relationship"),
        BASE_SIGNATURE_TAGS | {"png", "channel-count", "info-state", "accessor"},
    ),
    "0x005935f2": (
        "CDXTexture__GetOutputGamma",
        "int __stdcall CDXTexture__GetOutputGamma(void * png_decode_state, void * png_info_state, double * out_gamma)",
        ("valid-option bit 0x1", "output double", "color-management"),
        BASE_SIGNATURE_TAGS | {"png", "gamma", "info-state", "output-pointer", "accessor"},
    ),
    "0x0059361e": (
        "CDXTexture__GetRenderingIntent",
        "int __stdcall CDXTexture__GetRenderingIntent(void * png_decode_state, void * png_info_state, int * out_rendering_intent)",
        ("valid-option bit 0x800", "rendering-intent", "sRGB contract"),
        BASE_SIGNATURE_TAGS | {"png", "rendering-intent", "srgb", "info-state", "output-pointer"},
    ),
    "0x0059371d": (
        "CDXTexture__GetPaletteBufferInfo",
        "int __stdcall CDXTexture__GetPaletteBufferInfo(void * png_decode_state, void * png_info_state, void * out_palette_buffer, int * out_palette_count)",
        ("valid-option bit 0x8", "palette pointer", "palette count bounds"),
        BASE_SIGNATURE_TAGS | {"png", "palette", "plte", "info-state", "output-pointer"},
    ),
    "0x00593753": (
        "CDXTexture__GetTransparencyInfo",
        "int __stdcall CDXTexture__GetTransparencyInfo(void * png_decode_state, void * png_info_state, void * out_transparency_table, int * out_transparency_count, void * out_transparent_color)",
        ("valid-option bit 0x10", "color type byte +0x19", "tRNS structure layout"),
        BASE_SIGNATURE_TAGS | {"png", "transparency", "trns", "info-state", "output-pointer"},
    ),
    "0x005937bc": (
        "CDXTexture__EnableByteSwapTransform",
        "void __stdcall CDXTexture__EnableByteSwapTransform(void * png_decode_state)",
        ("transform flag bit 0x1", "png_decode_state +0x60", "runtime byte/channel swap"),
        BASE_SIGNATURE_TAGS | {"png", "transform-flags", "byte-swap"},
    ),
    "0x005937c7": (
        "CDXTexture__EnableSwap16TransformIfNeeded",
        "void __stdcall CDXTexture__EnableSwap16TransformIfNeeded(void * png_decode_state)",
        ("bit-depth byte", "transform flag bit 0x10", "16-bit sample"),
        BASE_SIGNATURE_TAGS | {"png", "transform-flags", "bit-depth", "swap16"},
    ),
    "0x005937db": (
        "CDXTexture__EnableExpandTo8Bit",
        "void __stdcall CDXTexture__EnableExpandTo8Bit(void * png_decode_state)",
        ("below 8", "output bit-depth byte", "packed-sample expansion"),
        BASE_SIGNATURE_TAGS | {"png", "transform-flags", "bit-depth", "expand-to-8bit"},
    ),
    "0x005937f6": (
        "CDXTexture__GetPngPassCountFromInterlace",
        "int __stdcall CDXTexture__GetPngPassCountFromInterlace(void * png_decode_state)",
        ("interlace byte", "returns seven passes", "Adam7"),
        BASE_SIGNATURE_TAGS | {"png", "interlace", "adam7", "pass-count", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave695 CDXTexture PNG option accessors",
    "cdxtexture-png-option-accessors-wave695",
    "0x00593526 CDXTexture__ReleasePngDecodeContextHandles",
    "0x005937f6 CDXTexture__GetPngPassCountFromInterlace",
    "0x00593812 CDXTexture__ConfigureFillerChannel",
)

OVERCLAIM_TOKENS = (
    "runtime png option behavior proven",
    "runtime png behavior proven",
    "png info-state layout proven",
    "slot ownership proven",
    "output pointer nullability proven",
    "transform-flag enum proven",
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
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 14, "post xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 444, "post instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata.tsv")) == 12, "pre metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags.tsv")) == 12, "pre tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs.tsv")) == 14, "pre xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions.tsv")) == 444, "pre instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-pre" / "index.tsv")) == 12, "pre decompile row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata-candidate.tsv")) == 20, "candidate metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags-candidate.tsv")) == 20, "candidate tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs-candidate.tsv")) == 23, "candidate xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-candidate.tsv")) == 740, "candidate instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")) == 20, "candidate decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave695 static read-back" in comment, f"missing Wave695 comment at {address}", failures)
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
        "apply-wave695-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 comment_only_updated=0 missing=0 bad=0",
        "apply-wave695-apply.log": "SUMMARY: updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 comment_only_updated=0 missing=0 bad=0",
        "apply-wave695-final-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=12 found=12 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "post-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "post-instructions.log": "Wrote 444 instruction rows",
        "post-xrefs.log": "Wrote 14 rows",
        "pre-metadata.log": "targets=12 found=12 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "pre-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "pre-instructions.log": "Wrote 444 instruction rows",
        "pre-xrefs.log": "Wrote 14 rows",
        "pre-metadata-candidate.log": "targets=20 found=20 missing=0",
        "pre-tags-candidate.log": "ExportFunctionTagsByAddress complete: rows=20 missing=0",
        "pre-decompile-candidate.log": "targets=20 dumped=20 missing=0 failed=0",
        "pre-instructions-candidate.log": "Wrote 740 instruction rows",
        "pre-xrefs-candidate.log": "Wrote 23 rows",
        "queue-refresh.log": "total_functions=6098 commented_functions=3991",
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
    require(quality.get("commentlessFunctionCount") == 2107, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 335, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x00593812", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CDXTexture__ConfigureFillerChannel", f"next head name mismatch: {head}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup_path") == "[maintainer-local-ghidra-backup-root]/BEA_20260521-150000_post_wave695_cdxtexture_png_option_accessors_verified", "backup path mismatch", failures)
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(backup.get("total_bytes")) == 165088135, f"backup bytes mismatch: {backup}", failures)
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
        package.get("scripts", {}).get("test:ghidra-cdxtexture-png-option-accessors-wave695")
        == "py -3 tools\\ghidra_cdxtexture_png_option_accessors_wave695_probe.py --check",
        "package script missing/mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave695 CDXTexture PNG option accessors" for row in ledger_rows), "ledger missing Wave695", failures)
    require(any(row.get("task") == "Wave695 CDXTexture PNG option accessors" for row in attempt_rows), "attempt log missing Wave695", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20351, f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    require(any("Wave695 CDXTexture PNG option accessors" in note for note in tracking.get("notes", [])), "tracking notes missing Wave695", failures)


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
        print("Wave695 CDXTexture PNG option accessor probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave695 CDXTexture PNG option accessor probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
