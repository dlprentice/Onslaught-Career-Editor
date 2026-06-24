#!/usr/bin/env python3
"""Validate Wave698 CDXTexture PNG decode-option-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave698-cdxtexture-png-decode-option-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_png_decode_option_tail_wave698_2026-05-21.md"
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

BASE_TAGS = {
    "static-reaudit",
    "cdxtexture-png-decode-option-tail-wave698",
    "wave698-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

TARGETS = {
    "0x00594ef8": (
        "CDXTexture__SetDecodeOptionFloat",
        "void __stdcall CDXTexture__SetDecodeOptionFloat(void * png_decode_state, void * png_info_state, double option_value)",
        ("gAMA parsing", "info-state valid-option bitmask", "gamma policy"),
        BASE_TAGS | {"png", "decode-options", "info-state", "gamma", "tranche-head"},
    ),
    "0x00594fb6": (
        "CTexture__SetDecodeScanParameters",
        "void __stdcall CTexture__SetDecodeScanParameters(void * png_decode_state, void * png_info_state, void * scan_parameter_table, int scan_parameter_count)",
        ("PLTE parsing", "scan_parameter_table", "palette semantics"),
        BASE_TAGS | {"png", "decode-options", "info-state", "plte", "palette"},
    ),
    "0x00594fdc": (
        "CDXTexture__SetDecodeOptionByte",
        "void __stdcall CDXTexture__SetDecodeOptionByte(void * png_decode_state, void * png_info_state, int option_byte_value)",
        ("option_byte_value", "byte option identity", "info-state layout"),
        BASE_TAGS | {"png", "decode-options", "info-state", "byte-option"},
    ),
    "0x00594ff9": (
        "CDXTexture__SetDecodeOptionByteWithDefaultFloat",
        "void __stdcall CDXTexture__SetDecodeOptionByteWithDefaultFloat(void * png_decode_state, void * png_info_state, int option_byte_value)",
        ("sRGB parsing", "default value meaning", "sRGB/gamma policy"),
        BASE_TAGS | {"png", "decode-options", "info-state", "srgb", "default-gamma"},
    ),
    "0x00595030": (
        "CDXTexture__SetDecodeOptionParams",
        "void __stdcall CDXTexture__SetDecodeOptionParams(void * png_decode_state, void * png_info_state, void * parameter_table, int parameter_count, void * parameter_record)",
        ("10-byte parameter_record", "tRNS/record layout", "parameter_count"),
        BASE_TAGS | {"png", "decode-options", "info-state", "trns", "record-copy"},
    ),
    "0x00595079": (
        "CDXTexture__ReadFromSource",
        "void __stdcall CDXTexture__ReadFromSource(void * png_decode_state, void * destination_buffer, uint requested_byte_count)",
        ("source callback", "destination_buffer", "runtime stream behavior"),
        BASE_TAGS | {"png", "source-read", "read-callback", "decode-state"},
    ),
    "0x005950a2": (
        "CDXTexture__SetReadFunction",
        "void __stdcall CDXTexture__SetReadFunction(void * png_decode_state, void * read_context, void * read_callback)",
        ("read_context", "read_callback", "buffered-read state layout"),
        BASE_TAGS | {"png", "source-read", "read-callback", "decode-state"},
    ),
    "0x005950e0": (
        "CDXTexture__ComparePngSignatureBytes",
        "int __stdcall CDXTexture__ComparePngSignatureBytes(void * signature_buffer, uint start_offset, uint bytes_to_check)",
        ("8-byte PNG signature", "caller-selected slice", "bytes_to_check"),
        BASE_TAGS | {"png", "signature-check", "png-signature", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave698 CDXTexture PNG decode-option tail",
    "cdxtexture-png-decode-option-tail-wave698",
    "0x00594ef8 CDXTexture__SetDecodeOptionFloat",
    "0x005950e0 CDXTexture__ComparePngSignatureBytes",
    "0x0059512b CDXTexture__AllocZeroedDecodeBuffer",
)

OVERCLAIM_TOKENS = (
    "runtime png behavior proven",
    "runtime stream behavior proven",
    "png decoder layout proven",
    "info-state layout proven",
    "callback abi proven",
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
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 18,
        "pre-instructions.tsv": 296,
        "decompile-pre/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 18,
        "post-instructions.tsv": 296,
        "decompile-post/index.tsv": 8,
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
        require("Wave698 static read-back" in comment, f"missing Wave698 comment at {address}", failures)
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
        "apply-wave698-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0",
        "apply-wave698-apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0",
        "apply-wave698-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=8 found=8 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "pre-xrefs.log": "Wrote 18 rows",
        "pre-instructions.log": "Wrote 296 instruction rows",
        "pre-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 18 rows",
        "post-instructions.log": "Wrote 296 instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "queue-refresh.log": "total_functions=6098 commented_functions=4016",
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
    require(quality.get("commentlessFunctionCount") == 2082, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 310, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x0059512b", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CDXTexture__AllocZeroedDecodeBuffer", f"next head name mismatch: {head}", failures)

    rows = read_tsv(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv")
    param_re = re.compile(r"\bparam_\d+\b")
    clean = [
        row for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not param_re.search(row.get("signature", ""))
    ]
    require(len(clean) == 3962, f"strict clean proxy mismatch: {len(clean)}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup_path").replace("\\", "/") == "G:/GhidraBackups/BEA_20260521-160619_post_wave698_cdxtexture_png_decode_option_tail_verified", "backup path mismatch", failures)
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(backup.get("total_bytes")) == 165186439, f"backup bytes mismatch: {backup}", failures)
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
        package.get("scripts", {}).get("test:ghidra-cdxtexture-png-decode-option-tail-wave698")
        == "py -3 tools\\ghidra_cdxtexture_png_decode_option_tail_wave698_probe.py --check",
        "package script missing or mismatched",
        failures,
    )

    attempt = [row for row in read_jsonl(ATTEMPT_LOG) if row.get("task") == "Wave698 CDXTexture PNG decode-option tail"]
    ledger = [row for row in read_jsonl(LEDGER) if row.get("task") == "Wave698 CDXTexture PNG decode-option tail"]
    require(len(attempt) == 1 and attempt[0].get("attempt_id") == 20353, "Wave698 attempt log row missing/mismatched", failures)
    require(len(ledger) == 1 and ledger[0].get("status") == "completed", "Wave698 ledger row missing/mismatched", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20354, "tracking next_attempt_id mismatch", failures)


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
        print("Wave698 CDXTexture PNG decode-option tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave698 CDXTexture PNG decode-option tail probe: PASS")
    print("Targets: 8")
    print("Queue: 6098 total, 4016 commented, 2082 commentless, 1216 exact-undefined, 310 param_N")
    print("Strict clean-signature proxy: 3962/6098 = 64.97%")
    print("Next head: 0x0059512b CDXTexture__AllocZeroedDecodeBuffer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
