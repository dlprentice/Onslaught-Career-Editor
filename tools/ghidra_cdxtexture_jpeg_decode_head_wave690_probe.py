#!/usr/bin/env python3
"""Validate Wave690 CDXTexture JPEG decode-head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave690-cdxtexture-jpeg-decode-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_jpeg_decode_head_wave690_2026-05-21.md"
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
    "cdxtexture-jpeg-decode-head-wave690",
    "wave690-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

BASE_COMMENT_TAGS = {
    "static-reaudit",
    "cdxtexture-jpeg-decode-head-wave690",
    "wave690-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
}

TARGETS = {
    "0x00590e10": (
        "CDXTexture__FillInputBufferFromSource",
        "int __stdcall CDXTexture__FillInputBufferFromSource(void * jpeg_decode_state, void * destination_buffer, int requested_byte_count)",
        ("source read callback", "consumed-byte cursor", "JPEG input state"),
        BASE_SIGNATURE_TAGS | {"jpeg", "input-buffer", "source-callback", "byte-cursor", "tranche-head"},
    ),
    "0x00590ea0": (
        "CDXTexture__ProcessInputControllerState",
        "int __stdcall CDXTexture__ProcessInputControllerState(void * jpeg_decode_state)",
        ("input-controller callbacks", "parser work queue", "decode dispatch context"),
        BASE_SIGNATURE_TAGS | {"jpeg", "input-controller", "decode-dispatch", "parser-work-queue"},
    ),
    "0x00590f80": (
        "CDXTexture__InitJpegDecodeState",
        "void __stdcall CDXTexture__InitJpegDecodeState(void * jpeg_decode_state, int expected_header_size, int expected_context_size)",
        ("0x3e/0x1d8", "marker reader", "state machine at 0xc8"),
        BASE_SIGNATURE_TAGS | {"jpeg", "decode-state", "marker-reader", "allocator", "callback-context"},
    ),
    "0x00591050": (
        "CFastVB__ReleaseOwnedObjectAndReset",
        "void __stdcall CFastVB__ReleaseOwnedObjectAndReset(void * decode_state_header)",
        ("vtable slot +0x28", "owner pointer", "stage/status field"),
        BASE_SIGNATURE_TAGS | {"jpeg", "owned-object-release", "vtable-release", "cleanup"},
    ),
    "0x00591060": (
        "CDXTexture__SelectJpegOutputDefaults",
        "void CDXTexture__SelectJpegOutputDefaults(void)",
        ("ESI-held JPEG decode state", "0x6f/0x72", "Signature intentionally left unchanged"),
        BASE_COMMENT_TAGS | {"jpeg", "output-defaults", "color-transform", "register-context"},
    ),
    "0x005911d0": (
        "CDXTexture__AdvanceJpegDecodeState",
        "int __stdcall CDXTexture__AdvanceJpegDecodeState(void * jpeg_decode_state)",
        ("state machine", "output-default selection", "marker-controller ABI"),
        BASE_SIGNATURE_TAGS | {"jpeg", "state-machine", "output-defaults", "marker-reader"},
    ),
    "0x00591280": (
        "CDXTexture__DecodeJpegStream_PumpUntilReady",
        "int __stdcall CDXTexture__DecodeJpegStream_PumpUntilReady(void * jpeg_decode_state)",
        ("0xcd/0xce/0xcf/0xd2", "short-source", "allocator/stage setup"),
        BASE_SIGNATURE_TAGS | {"jpeg", "pump-until-ready", "allocator-stage", "end-of-stream"},
    ),
    "0x00591340": (
        "CDXTexture__PumpDecoderStreamAndFinalize",
        "int __stdcall CDXTexture__PumpDecoderStreamAndFinalize(void * jpeg_decode_state, int require_end_of_image)",
        ("strict end-of-image error 0x33", "decoder status", "strict-Eoi contract"),
        BASE_SIGNATURE_TAGS | {"jpeg", "decoder-finalize", "strict-eoi", "pump-wrapper", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave690 CDXTexture JPEG decode head",
    "cdxtexture-jpeg-decode-head-wave690",
    "0x00590e10 CDXTexture__FillInputBufferFromSource",
    "0x00591340 CDXTexture__PumpDecoderStreamAndFinalize",
    "0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame",
)

OVERCLAIM_TOKENS = (
    "runtime decode fidelity proven",
    "source-manager ABI proven",
    "decode-state layout proven",
    "state enum proven",
    "marker-controller ABI proven",
    "output color enum proven",
    "segment-parser semantics proven",
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
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 10, "post xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 728, "post instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata.tsv")) == 8, "pre metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags.tsv")) == 8, "pre tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs.tsv")) == 10, "pre xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions.tsv")) == 728, "pre instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-pre" / "index.tsv")) == 8, "pre decompile row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata-candidate.tsv")) == 13, "candidate metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags-candidate.tsv")) == 13, "candidate tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs-candidate.tsv")) == 16, "candidate xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-candidate.tsv")) == 1053, "candidate instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")) == 13, "candidate decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave690 static read-back" in comment, f"missing Wave690 comment at {address}", failures)
        require("Static metadata only" in comment or "Signature intentionally left unchanged" in comment, f"missing uncertainty clause at {address}", failures)
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
    expected_exact = {
        "apply-wave690-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=1 missing=0 bad=0",
        "apply-wave690-apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=1 missing=0 bad=0",
        "apply-wave690-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-instructions.log": "Wrote 728 instruction rows",
        "post-xrefs.log": "Wrote 10 rows",
        "pre-metadata.log": "targets=8 found=8 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "pre-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "pre-instructions.log": "Wrote 728 instruction rows",
        "pre-xrefs.log": "Wrote 10 rows",
        "pre-metadata-candidate.log": "targets=13 found=13 missing=0",
        "pre-tags-candidate.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "pre-decompile-candidate.log": "targets=13 dumped=13 missing=0 failed=0",
        "pre-instructions-candidate.log": "Wrote 1053 instruction rows",
        "pre-xrefs-candidate.log": "Wrote 16 rows",
        "queue-refresh.log": "total_functions=6098 commented_functions=3953",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 2145, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 368, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x00591460", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CDXTexture__DecodeJpegSegment_StartOfFrame", f"next head name mismatch: {head}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup_path") == "G:/GhidraBackups/BEA_20260521-123207_post_wave690_cdxtexture_jpeg_decode_head_verified", "backup path mismatch", failures)
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(backup.get("total_bytes")) == 164825991, f"backup bytes mismatch: {backup}", failures)
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
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"{path.relative_to(ROOT)} contains overclaim token {token}", failures)

    package = json.loads(read_text(PACKAGE_JSON))
    require(
        package.get("scripts", {}).get("test:ghidra-cdxtexture-jpeg-decode-head-wave690")
        == "py -3 tools\\ghidra_cdxtexture_jpeg_decode_head_wave690_probe.py --check",
        "package script missing/mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave690 CDXTexture JPEG decode head" for row in ledger_rows), "ledger missing Wave690", failures)
    require(any(row.get("task") == "Wave690 CDXTexture JPEG decode head" for row in attempt_rows), "attempt log missing Wave690", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20346, f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    require(any("Wave690 CDXTexture JPEG decode head" in note for note in tracking.get("notes", [])), "tracking notes missing Wave690", failures)


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
        print("Wave690 CDXTexture JPEG decode-head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave690 CDXTexture JPEG decode-head probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
