#!/usr/bin/env python3
"""Validate Wave899 CDXTexture JPEG/decode-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave899-cdxtexture-jpeg-decode-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_jpeg_decode_tail_wave899_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-083306_post_wave899_cdxtexture_jpeg_decode_tail_verified"
COMMON_TAGS = {
    "static-reaudit",
    "cdxtexture-jpeg-decode-tail-wave899",
    "wave899-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "important-image-decode-infrastructure",
    "raw-commentless-tail",
    "jpeg-decode-tail",
}
TARGETS = {
    "0x005b7770": {
        "name": "CDXTexture__ValidateJpegFrameAndComputeMcuLayout",
        "signature": "void CDXTexture__ValidateJpegFrameAndComputeMcuLayout(void)",
        "tokens": ("Wave899 static read-back", "0x005b8142", "state+0xf0/+0xf4", "frame MCU-row count"),
        "xrefs": {"0x005b8142"},
        "extra_tags": {"jpeg-frame-validator", "mcu-layout", "hidden-esi-state", "scan-controller"},
    },
    "0x005b7920": {
        "name": "CDXTexture__ValidateJpegScanScript",
        "signature": "void CDXTexture__ValidateJpegScanScript(void)",
        "tokens": ("Wave899 static read-back", "0x005b814f", "progressive scan coverage", "0x2d"),
        "xrefs": {"0x005b814f"},
        "extra_tags": {"jpeg-scan-script", "progressive-jpeg", "hidden-esi-state", "scan-controller"},
    },
    "0x005b7c50": {
        "name": "CDXTexture__LoadCurrentJpegScanDescriptor",
        "signature": "void CDXTexture__LoadCurrentJpegScanDescriptor(void)",
        "tokens": ("Wave899 static read-back", "0x005b7f0f", "0x005b7f4f", "0x005b7fb5"),
        "xrefs": {"0x005b7f0f", "0x005b7f4f", "0x005b7fb5"},
        "extra_tags": {"jpeg-scan-descriptor", "scan-state-machine", "hidden-esi-state"},
    },
    "0x005b7d30": {
        "name": "CDXTexture__BuildCurrentScanMcuLayout",
        "signature": "uint CDXTexture__BuildCurrentScanMcuLayout(void)",
        "tokens": ("Wave899 static read-back", "0x005b7f14", "0x005b7f54", "0x005b7fba", "0xffff"),
        "xrefs": {"0x005b7f14", "0x005b7f54", "0x005b7fba"},
        "extra_tags": {"jpeg-current-scan-layout", "mcu-layout", "hidden-esi-state", "scan-state-machine"},
    },
    "0x005bce60": {
        "name": "CDXTexture__ConvertYCbCrToRgb24_Mmx",
        "signature": "int CDXTexture__ConvertYCbCrToRgb24_Mmx(void)",
        "tokens": ("Wave899 static read-back", "0x005afb05", "DAT_005f5000", "RGB24"),
        "xrefs": {"0x005afb05"},
        "extra_tags": {"ycbcr-to-rgb24", "mmx-converter", "locked-stack-abi", "raw-callsite-005afb05"},
    },
    "0x005bd53b": {
        "name": "CDXTexture__BuildInflateHuffmanTable",
        "signature": "int CDXTexture__BuildInflateHuffmanTable(void)",
        "tokens": ("Wave899 static read-back", "0x005bd8f6", "0x005bd982", "0x005bd9b9", "0x5a0"),
        "xrefs": {"0x005bd8f6", "0x005bd982", "0x005bd9b9"},
        "extra_tags": {"inflate-huffman-table", "dynamic-tree-helper", "hidden-eax-stack-abi", "zlib-style-status"},
    },
}
CORE_ANCHORS = (
    "Wave899 CDXTexture JPEG decode tail",
    "cdxtexture-jpeg-decode-tail-wave899",
    "0x005b7770 CDXTexture__ValidateJpegFrameAndComputeMcuLayout",
    "0x005b7920 CDXTexture__ValidateJpegScanScript",
    "0x005b7c50 CDXTexture__LoadCurrentJpegScanDescriptor",
    "0x005b7d30 CDXTexture__BuildCurrentScanMcuLayout",
    "0x005bce60 CDXTexture__ConvertYCbCrToRgb24_Mmx",
    "0x005bd53b CDXTexture__BuildInflateHuffmanTable",
    "0x005d04e6 RtlUnwind",
    "6106/6113 = 99.89%",
    BACKUP_PATH,
)
OVERCLAIM_TOKENS = (
    "runtime jpeg behavior proven",
    "runtime image decode behavior proven",
    "runtime decompression behavior proven",
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


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 12,
        "pre-instructions.tsv": 1046,
        "pre-decompile/index.tsv": 6,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 12,
        "post-instructions.tsv": 1046,
        "post-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    xrefs_by_target: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs_by_target.setdefault(normalize_address(row["target_addr"]), set()).add(normalize_address(row["from_addr"]))
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in expected["tokens"]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            needed = COMMON_TAGS | expected["extra_tags"]
            require(needed.issubset(actual_tags), f"tags missing at {address}: {needed - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        require(expected["xrefs"].issubset(xrefs_by_target.get(address, set())), f"xref anchors missing at {address}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 12 rows",
        "post-instructions.log": "Wrote 1046 function-body instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=6106",
        "queue-probe.log": "Commentless functions: 7",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave899.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave899_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "Invalid script", "MISSING:", "BADSIG:", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 7, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 6106, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6106, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005d04e6", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "RtlUnwind", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DXTEXTURE_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-cdxtexture-jpeg-decode-tail-wave899")
        == r"py -3 tools\ghidra_cdxtexture_jpeg_decode_tail_wave899_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave899 CDXTexture JPEG decode tail" for row in ledger_rows), "missing Wave899 ledger row", failures)
    require(
        any(row.get("task") == "Wave899 CDXTexture JPEG decode tail" and row.get("attempt_id") == 20554 for row in attempts),
        "missing Wave899 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave899 CDXTexture JPEG/decode-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave899 CDXTexture JPEG/decode-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
