#!/usr/bin/env python3
"""Validate Wave691 CDXTexture JPEG segment-parser read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave691-cdxtexture-jpeg-segment-parsers"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_jpeg_segment_parsers_wave691_2026-05-21.md"
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
    "cdxtexture-jpeg-segment-parsers-wave691",
    "wave691-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

BASE_COMMENT_TAGS = {
    "static-reaudit",
    "cdxtexture-jpeg-segment-parsers-wave691",
    "wave691-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
}

TARGETS = {
    "0x00591460": (
        "CDXTexture__DecodeJpegSegment_StartOfFrame",
        "int __fastcall CDXTexture__DecodeJpegSegment_StartOfFrame(int param_1)",
        ("JPEG start-of-frame segment", "component descriptor table", "Signature intentionally left unchanged"),
        BASE_COMMENT_TAGS | {"jpeg", "start-of-frame", "component-descriptors", "sampling-factors", "quant-table-selector", "tranche-head"},
    ),
    "0x005919e0": (
        "CDXTexture__DecodeJpegSegment_HuffmanTables",
        "int CDXTexture__DecodeJpegSegment_HuffmanTables(void)",
        ("DHT/Huffman-table segment", "sixteen code-length counts", "locked parameter storage"),
        BASE_COMMENT_TAGS | {"jpeg", "dht", "huffman-table", "code-length-counts", "symbol-budget", "locked-storage"},
    ),
    "0x00591cb0": (
        "CDXTexture__DecodeJpegSegment_QuantizationTables",
        "int __stdcall CDXTexture__DecodeJpegSegment_QuantizationTables(void * jpeg_decode_state)",
        ("DQT/quantization-table segment", "DAT_005f37f8", "8-bit and 16-bit coefficient forms"),
        BASE_SIGNATURE_TAGS | {"jpeg", "dqt", "quantization-table", "coefficient-reader", "descriptor-allocation", "zigzag-table"},
    ),
    "0x00591ef0": (
        "CDXTexture__DecodeJpegSegment_RestartInterval",
        "int __stdcall CDXTexture__DecodeJpegSegment_RestartInterval(void * jpeg_decode_state)",
        ("DRI/restart-interval segment", "observed +0x118 slot", "diagnostic 0x0b"),
        BASE_SIGNATURE_TAGS | {"jpeg", "dri", "restart-interval", "restart-marker", "interval-field", "marker-reader"},
    ),
    "0x00591fc0": (
        "CDXTexture__ParseJfifApp0Header",
        "void __fastcall CDXTexture__ParseJfifApp0Header(int param_1)",
        ("APP0 JFIF/JFXX header", "density units", "Signature intentionally left unchanged"),
        BASE_COMMENT_TAGS | {"jpeg", "app0", "jfif", "jfxx", "density-fields", "thumbnail-dimensions"},
    ),
    "0x005921a0": (
        "CDXTexture__ParseAdobeApp14Header",
        "void __thiscall CDXTexture__ParseAdobeApp14Header(void * this, uint param_1, int param_2)",
        ("APP14 Adobe header", "transform byte at the observed +0x12c slot", "Ghidra's thiscall shape"),
        BASE_COMMENT_TAGS | {"jpeg", "app14", "adobe", "transform-byte", "color-transform", "register-context", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave691 CDXTexture JPEG segment parsers",
    "cdxtexture-jpeg-segment-parsers-wave691",
    "0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame",
    "0x005921a0 CDXTexture__ParseAdobeApp14Header",
    "0x00592380 CTexture__ReadJpegSegmentLengthAndEmitMarker",
)

OVERCLAIM_TOKENS = (
    "runtime decode fidelity proven",
    "sof marker enum proven",
    "frame-header layout proven",
    "component descriptor layout proven",
    "huffman descriptor layout proven",
    "quant descriptor layout proven",
    "restart-marker behavior proven",
    "app0 offset contract proven",
    "app14 offset contract proven",
    "color-transform policy proven",
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
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 7, "post xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 546, "post instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata.tsv")) == 6, "pre metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags.tsv")) == 6, "pre tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs.tsv")) == 7, "pre xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions.tsv")) == 546, "pre instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-pre" / "index.tsv")) == 6, "pre decompile row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata-candidate.tsv")) == 12, "candidate metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags-candidate.tsv")) == 12, "candidate tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs-candidate.tsv")) == 17, "candidate xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-candidate.tsv")) == 1092, "candidate instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")) == 12, "candidate decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave691 static read-back" in comment, f"missing Wave691 comment at {address}", failures)
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
        "apply-wave691-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0",
        "apply-wave691-apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0",
        "apply-wave691-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "post-instructions.log": "Wrote 546 instruction rows",
        "post-xrefs.log": "Wrote 7 rows",
        "pre-metadata.log": "targets=6 found=6 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "pre-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "pre-instructions.log": "Wrote 546 instruction rows",
        "pre-xrefs.log": "Wrote 7 rows",
        "pre-metadata-candidate.log": "targets=12 found=12 missing=0",
        "pre-tags-candidate.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "pre-decompile-candidate.log": "targets=12 dumped=12 missing=0 failed=0",
        "pre-instructions-candidate.log": "Wrote 1092 instruction rows",
        "pre-xrefs-candidate.log": "Wrote 17 rows",
        "queue-refresh.log": "total_functions=6098 commented_functions=3959",
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
    require(quality.get("commentlessFunctionCount") == 2139, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 366, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x00592380", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__ReadJpegSegmentLengthAndEmitMarker", f"next head name mismatch: {head}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup_path") == "[maintainer-local-ghidra-backup-root]/BEA_20260521-130107_post_wave691_cdxtexture_jpeg_segment_parsers_verified", "backup path mismatch", failures)
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(backup.get("total_bytes")) == 164891527, f"backup bytes mismatch: {backup}", failures)
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
            require(token not in text.lower(), f"{path.relative_to(ROOT)} contains overclaim token {token}", failures)

    package = json.loads(read_text(PACKAGE_JSON))
    require(
        package.get("scripts", {}).get("test:ghidra-cdxtexture-jpeg-segment-parsers-wave691")
        == "py -3 tools\\ghidra_cdxtexture_jpeg_segment_parsers_wave691_probe.py --check",
        "package script missing/mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave691 CDXTexture JPEG segment parsers" for row in ledger_rows), "ledger missing Wave691", failures)
    require(any(row.get("task") == "Wave691 CDXTexture JPEG segment parsers" for row in attempt_rows), "attempt log missing Wave691", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20347, f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    require(any("Wave691 CDXTexture JPEG segment parsers" in note for note in tracking.get("notes", [])), "tracking notes missing Wave691", failures)


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
        print("Wave691 CDXTexture JPEG segment-parser probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave691 CDXTexture JPEG segment-parser probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
