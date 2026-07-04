#!/usr/bin/env python3
"""Validate Wave725 JPEG scan/Huffman head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave725-jpeg-scan-huffman-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_jpeg_scan_huffman_head_wave725_2026-05-22.md"
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
    "jpeg-scan-huffman-head-wave725",
    "wave725-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "jpeg-scan-huffman",
}

COMMENT_TAGS = {
    "static-reaudit",
    "jpeg-scan-huffman-head-wave725",
    "wave725-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
    "hidden-register-context",
    "jpeg-scan-huffman",
}

TARGETS = {
    "0x005aba90": (
        "CDXTexture__SelectNextScanTableForProgress",
        "void __fastcall CDXTexture__SelectNextScanTableForProgress(void * decode_context)",
        ("selects/reset the next JPEG scan table progress state", "ECX texture/decode context", "context +0x1b0"),
        SIGNATURE_TAGS | {"scan-table", "scan-progress", "fastcall-ecx-context", "tranche-head"},
    ),
    "0x005ac180": (
        "CDXTexture__ValidateAndIndexQuantTables",
        "int CDXTexture__ValidateAndIndexQuantTables(void)",
        ("validates component quantization table availability", "hidden EBX texture/decode context", "current int(void) signature is intentionally retained"),
        COMMENT_TAGS | {"quant-table", "component-descriptor", "hidden-ebx-context"},
    ),
    "0x005ac930": (
        "CDXTexture__SelectColorConvertEntryPoint",
        "void __stdcall CDXTexture__SelectColorConvertEntryPoint(void * decode_context)",
        ("selects the color-conversion entry point", "RET 0x4 evidence", "LAB_005ac2d0"),
        SIGNATURE_TAGS | {"color-conversion", "callback-selector", "quant-table", "ret-0x4"},
    ),
    "0x005ac980": (
        "CDXTexture__InitColorConversionResources",
        "void __stdcall CDXTexture__InitColorConversionResources(void * decode_context)",
        ("initializes color-conversion resources", "hidden EBX remains a mode/context signal", "0x500-byte table block"),
        SIGNATURE_TAGS | {"color-conversion", "resource-init", "hidden-ebx-mode", "allocator", "ret-0x4"},
    ),
    "0x005acac0": (
        "CDXTexture__BuildJpegHuffmanDecodeTable",
        "void __stdcall CDXTexture__BuildJpegHuffmanDecodeTable(void * decode_context, int table_class, int table_index, void * decode_table_slot)",
        ("builds a JPEG Huffman decode lookup table", "RET 0x10 evidence", "0x590-byte table"),
        SIGNATURE_TAGS | {"huffman", "decode-table", "dht", "ret-0x10"},
    ),
    "0x005acd90": (
        "CDXTexture__BitstreamReadBitsWithJpegStuffing",
        "int __stdcall CDXTexture__BitstreamReadBitsWithJpegStuffing(void * bitstream_state, uint bit_buffer, int bit_count, int min_bits)",
        ("refills a JPEG entropy bitstream state", "0xff byte-stuffing", "marker detection"),
        SIGNATURE_TAGS | {"bitstream", "jpeg-stuffing", "marker-detection", "ret-0x10"},
    ),
    "0x005aceb0": (
        "CDXTexture__DecodeHuffmanSymbolFromBitstream",
        "uint __stdcall CDXTexture__DecodeHuffmanSymbolFromBitstream(void * bitstream_state, uint bit_buffer, int bit_count, void * huffman_table, int min_bits)",
        ("decodes one JPEG Huffman symbol", "RET 0x14 evidence", "error id 0x76"),
        SIGNATURE_TAGS | {"huffman", "bitstream", "symbol-decode", "ret-0x14"},
    ),
    "0x005acf90": (
        "CDXTexture__FinalizeScanBitstreamState",
        "int CDXTexture__FinalizeScanBitstreamState(void)",
        ("finalizes JPEG scan bitstream state", "hidden ESI texture/decode context", "current int(void) signature is intentionally retained"),
        COMMENT_TAGS | {"scan-bitstream", "finalize", "hidden-esi-context", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave725 JPEG scan/Huffman head",
    "jpeg-scan-huffman-head-wave725",
    "0x005aba90 CDXTexture__SelectNextScanTableForProgress",
    "0x005ac180 CDXTexture__ValidateAndIndexQuantTables",
    "0x005ac930 CDXTexture__SelectColorConvertEntryPoint",
    "0x005ac980 CDXTexture__InitColorConversionResources",
    "0x005acac0 CDXTexture__BuildJpegHuffmanDecodeTable",
    "0x005acd90 CDXTexture__BitstreamReadBitsWithJpegStuffing",
    "0x005aceb0 CDXTexture__DecodeHuffmanSymbolFromBitstream",
    "0x005acf90 CDXTexture__FinalizeScanBitstreamState",
    "0x005ad550 CTexture__InitDecodeCallbackTables",
    "0x0042f220 CSPtrSet__Clear",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260522-062642_post_wave725_jpeg_scan_huffman_head_verified",
)

OVERCLAIM_TOKENS = (
    "runtime jpeg decode behavior proven",
    "runtime image decode behavior proven",
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
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 34,
        "pre-instructions.tsv": 4328,
        "pre-decompile/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 34,
        "post-instructions.tsv": 4328,
        "post-decompile/index.tsv": 8,
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
        require("Wave725 static read-back" in comment, f"missing Wave725 comment at {address}", failures)
        require("Static retail Ghidra metadata" in comment, f"missing static-evidence boundary at {address}", failures)
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=2 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=2 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=8 found=8 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "pre-xrefs.log": "Wrote 34 rows",
        "pre-instructions.log": "Wrote 4328 instruction rows",
        "pre-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 34 rows",
        "post-instructions.log": "Wrote 4328 instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}", failures)
        require("LockException" not in text, f"unexpected LockException in {relative}", failures)
        require("MISSING:" not in text, f"unexpected MISSING in {relative}", failures)
        require("BADNAME" not in text, f"unexpected BADNAME in {relative}", failures)
        require("FAIL" not in text, f"unexpected FAIL in {relative}", failures)
        require("Input file not found" not in text, f"stale failed export in {relative}", failures)

    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save evidence", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply-final-dry.log"), "missing final dry save evidence", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1830, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 103, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005ad550", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CTexture__InitDecodeCallbackTables", "high-signal head name mismatch", failures)

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
    require(commented == 4268, "commented count mismatch", failures)
    require(strict_clean == 4210, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    by_address = {normalize_address(row["address"]): row for row in rows}
    for address in TARGETS:
        row = by_address.get(address)
        require(row is not None, f"missing queue row for {address}", failures)
        if row is None:
            continue
        require(bool(row.get("comment", "").strip()), f"queue row still commentless for {address}", failures)
        if address in {"0x005aba90", "0x005ac930", "0x005ac980", "0x005acac0", "0x005acd90", "0x005aceb0"}:
            require(re.search(r"\bparam_\d+\b", row.get("signature", "")) is None, f"queue row still has param_N for {address}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup["backup"] == r"[maintainer-local-ghidra-backup-root]\BEA_20260522-062642_post_wave725_jpeg_scan_huffman_head_verified", "backup destination mismatch", failures)
    require(backup["fileCount"] == 19, "backup file count mismatch", failures)
    require(int(backup["totalBytes"]) == 166595463, "backup byte count mismatch", failures)
    require(backup["diffCount"] == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            escaped = token.replace("\\", "\\\\")
            require(token in text or escaped in text, f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lower, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    require("test:ghidra-jpeg-scan-huffman-head-wave725" in read_text(PACKAGE_JSON), "missing package script", failures)

    ledgers = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave725 JPEG scan/Huffman head" for row in ledgers), "missing Wave725 ledger row", failures)
    require(any(row.get("attempt_id") == 20380 and row.get("task") == "Wave725 JPEG scan/Huffman head" for row in attempts), "missing Wave725 attempt row", failures)

    tracking = read_json(TRACKING)
    require(tracking["next_attempt_id"] == 20381, "tracking next_attempt_id mismatch", failures)
    require("Wave725 JPEG scan/Huffman head" in tracking.get("current_focus", ""), "tracking focus mismatch", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Return non-zero when validation fails.")
    args = parser.parse_args(argv)

    failures: list[str] = []
    for check in (check_artifacts, check_logs, check_queue_and_backup, check_docs_and_state):
        try:
            check(failures)
        except Exception as exc:  # pragma: no cover - diagnostic path
            failures.append(f"{check.__name__}: {exc}")

    if failures:
        print("Wave725 JPEG scan/Huffman head probe")
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0

    print("Wave725 JPEG scan/Huffman head probe")
    print("Status: PASS")
    print("Targets: 8")
    print("Queue: 6098 total, 4268 commented, 1830 commentless, 1216 undefined, 103 param_N")
    print(r"Backup: [maintainer-local-ghidra-backup-root]\BEA_20260522-062642_post_wave725_jpeg_scan_huffman_head_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
