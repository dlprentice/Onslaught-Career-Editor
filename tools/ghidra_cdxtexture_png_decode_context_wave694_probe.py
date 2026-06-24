#!/usr/bin/env python3
"""Validate Wave694 CDXTexture PNG decode-context read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave694-cdxtexture-png-decode-context"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_png_decode_context_wave694_2026-05-21.md"
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
    "cdxtexture-png-decode-context-wave694",
    "wave694-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

TARGETS = {
    "0x00592dc2": (
        "CDXTexture__CreatePngDecodeContext",
        "void * __stdcall CDXTexture__CreatePngDecodeContext(void * png_version_string, void * callback_context, void * error_callback, void * warning_callback)",
        ("0x2000 zlib input buffer", "version literal 1.1.4", "callback prototypes"),
        BASE_SIGNATURE_TAGS | {"png", "decode-context", "zlib", "callback-triplet", "tranche-head"},
    ),
    "0x00592eb6": (
        "CDXTexture__ParsePngHeadersUntilIdat",
        "void __stdcall CDXTexture__ParsePngHeadersUntilIdat(void * png_decode_state, void * png_image_context)",
        ("IHDR/PLTE/tRNS/gAMA/sRGB", "first IDAT byte count", "CRC contract"),
        BASE_SIGNATURE_TAGS | {"png", "signature-check", "chunk-dispatch", "idat-boundary", "crc"},
    ),
    "0x00593024": (
        "CDXTexture__PreparePngRowOutputLayout",
        "void __stdcall CDXTexture__PreparePngRowOutputLayout(void * png_decode_state, void * png_image_context)",
        ("pass geometry", "postprocess/output layout", "layout-flag enum"),
        BASE_SIGNATURE_TAGS | {"png", "row-output-layout", "pass-geometry", "postprocess-layout"},
    ),
    "0x00593043": (
        "CDXTexture__DecodePngPassRowsAndPostprocess",
        "void __stdcall CDXTexture__DecodePngPassRowsAndPostprocess(void * png_decode_state, void * previous_row_workspace, void * current_row_workspace)",
        ("IDAT chunks", "PNG scanline filter", "optional row callback at +0x16c"),
        BASE_SIGNATURE_TAGS | {"png", "row-decode", "idat", "zlib", "scanline-filter", "adam7"},
    ),
    "0x005933c6": (
        "CDXTexture__DecodePngRowsAcrossPasses",
        "void __stdcall CDXTexture__DecodePngRowsAcrossPasses(void * png_decode_state, int * row_workspace_pointer_table)",
        ("pass count", "row_workspace_pointer_table", "interlace behavior"),
        BASE_SIGNATURE_TAGS | {"png", "row-loop", "interlace", "adam7", "workspace-table"},
    ),
    "0x00593411": (
        "CDXTexture__ResetPngDecodeContext",
        "void __stdcall CDXTexture__ResetPngDecodeContext(void * png_decode_state, void * primary_row_workspace, void * secondary_row_workspace)",
        ("+0x9c/+0xdc/+0xd8", "preserved-header layout", "cleanup ABI"),
        BASE_SIGNATURE_TAGS | {"png", "decode-context-reset", "owned-buffer-release", "zlib-cleanup", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave694 CDXTexture PNG decode context",
    "cdxtexture-png-decode-context-wave694",
    "0x00592dc2 CDXTexture__CreatePngDecodeContext",
    "0x00593411 CDXTexture__ResetPngDecodeContext",
    "0x00593526 CDXTexture__ReleasePngDecodeContextHandles",
)

OVERCLAIM_TOKENS = (
    "runtime png decode behavior proven",
    "runtime png output behavior proven",
    "png decode-state layout proven",
    "callback prototypes proven",
    "zlib allocator abi proven",
    "image-context layout proven",
    "crc contract proven",
    "adam7 table semantics proven",
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
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 6, "post xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 630, "post instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata.tsv")) == 6, "pre metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags.tsv")) == 6, "pre tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs.tsv")) == 6, "pre xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions.tsv")) == 630, "pre instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-pre" / "index.tsv")) == 6, "pre decompile row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata-candidate.tsv")) == 18, "candidate metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags-candidate.tsv")) == 18, "candidate tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs-candidate.tsv")) == 20, "candidate xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-candidate.tsv")) == 1170, "candidate instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")) == 18, "candidate decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave694 static read-back" in comment, f"missing Wave694 comment at {address}", failures)
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
        "apply-wave694-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=0 missing=0 bad=0",
        "apply-wave694-apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=0 missing=0 bad=0",
        "apply-wave694-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "post-instructions.log": "Wrote 630 instruction rows",
        "post-xrefs.log": "Wrote 6 rows",
        "pre-metadata.log": "targets=6 found=6 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "pre-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "pre-instructions.log": "Wrote 630 instruction rows",
        "pre-xrefs.log": "Wrote 6 rows",
        "pre-metadata-candidate.log": "targets=18 found=18 missing=0",
        "pre-tags-candidate.log": "ExportFunctionTagsByAddress complete: rows=18 missing=0",
        "pre-decompile-candidate.log": "targets=18 dumped=18 missing=0 failed=0",
        "pre-instructions-candidate.log": "Wrote 1170 instruction rows",
        "pre-xrefs-candidate.log": "Wrote 20 rows",
        "queue-refresh.log": "total_functions=6098 commented_functions=3979",
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
    require(quality.get("commentlessFunctionCount") == 2119, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 347, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x00593526", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CDXTexture__ReleasePngDecodeContextHandles", f"next head name mismatch: {head}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup_path") == "G:/GhidraBackups/BEA_20260521-142452_post_wave694_cdxtexture_png_decode_context_verified", "backup path mismatch", failures)
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(backup.get("total_bytes")) == 164989831, f"backup bytes mismatch: {backup}", failures)
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
        package.get("scripts", {}).get("test:ghidra-cdxtexture-png-decode-context-wave694")
        == "py -3 tools\\ghidra_cdxtexture_png_decode_context_wave694_probe.py --check",
        "package script missing/mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave694 CDXTexture PNG decode context" for row in ledger_rows), "ledger missing Wave694", failures)
    require(any(row.get("task") == "Wave694 CDXTexture PNG decode context" for row in attempt_rows), "attempt log missing Wave694", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20350, f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    require(any("Wave694 CDXTexture PNG decode context" in note for note in tracking.get("notes", [])), "tracking notes missing Wave694", failures)


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
        print("Wave694 CDXTexture PNG decode-context probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave694 CDXTexture PNG decode-context probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
