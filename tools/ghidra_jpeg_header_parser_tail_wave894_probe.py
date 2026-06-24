#!/usr/bin/env python3
"""Validate Wave894 JPEG header-parser read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave894-jpeg-header-parser-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_jpeg_header_parser_tail_wave894_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave894 JPEG header parser tail"
TAG = "jpeg-header-parser-tail-wave894"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-062021_post_wave894_jpeg_header_parser_tail_verified"
STRICT_PROXY = "6077/6113 = 99.41%"
NEXT_HEAD = "0x00598390 CFastVB__DetectCpuFeatureMask"

TARGETS = {
    "0x005913b0": (
        "CFastVB__JpegParser_ResetFrameState",
        "int CFastVB__JpegParser_ResetFrameState(void)",
        ("0x00592617", "hidden ESI", "0x66", "+0x0c"),
    ),
    "0x00591720": (
        "CFastVB__JpegParser_ParseSOFComponents",
        "int CFastVB__JpegParser_ParseSOFComponents(void)",
        ("0x0059274a", "hidden EBX/ESI", "state+0xdc", "0x15-dword"),
    ),
    "0x0059364c": (
        "CDXTexture__GetImageHeaderInfo",
        "int CDXTexture__GetImageHeaderInfo(void)",
        ("0x0057ba81", "CDXTexture__DecodePngFromMemory", "0x5eea60", "0x7fffffff"),
    ),
    "0x00594f15": (
        "CTexture__FinalizeDecodeFormatDescriptor",
        "int CTexture__FinalizeDecodeFormatDescriptor(void)",
        ("0x0059d86d", "CDXTexture__ParsePngChunk_IHDR", "0x5eeaec", "row-byte"),
    ),
}

EXPECTED_XREFS = {
    "0x005913b0": ("0x00592617", "<no_function>", "UNCONDITIONAL_CALL"),
    "0x00591720": ("0x0059274a", "<no_function>", "UNCONDITIONAL_CALL"),
    "0x0059364c": ("0x0057ba81", "CDXTexture__DecodePngFromMemory", "UNCONDITIONAL_CALL"),
    "0x00594f15": ("0x0059d86d", "CDXTexture__ParsePngChunk_IHDR", "UNCONDITIONAL_CALL"),
}

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave894-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "jpeg-decode-header",
    "important-image-decode-infrastructure",
    "raw-commentless-tail",
}

CORE_ANCHORS = (
    TASK,
    TAG,
    "0x005913b0 CFastVB__JpegParser_ResetFrameState",
    "0x00591720 CFastVB__JpegParser_ParseSOFComponents",
    "0x0059364c CDXTexture__GetImageHeaderInfo",
    "0x00594f15 CTexture__FinalizeDecodeFormatDescriptor",
    "0x0057ba81",
    "0x0059d86d",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "exact layout proven",
    "exact descriptor schema proven",
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
        "targets-snapshot.tsv": 4,
        "pre-metadata.tsv": 4,
        "pre-tags.tsv": 4,
        "pre-xrefs.tsv": 4,
        "pre-instructions.tsv": 422,
        "pre-decompile/index.tsv": 4,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 4,
        "post-instructions.tsv": 422,
        "post-decompile/index.tsv": 4,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave894 static read-back", "Static retail Ghidra evidence only", "remain unproven", *tokens):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref = xrefs.get(address)
        expected_from, expected_function, expected_type = EXPECTED_XREFS[address]
        require(xref is not None, f"missing xref for {address}", failures)
        if xref is not None:
            require(normalize_address(xref.get("from_addr", "")) == expected_from, f"xref source mismatch at {address}", failures)
            require(xref.get("from_function") == expected_function, f"xref owner mismatch at {address}", failures)
            require(xref.get("ref_type") == expected_type, f"xref type mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-xrefs.log": "Wrote 4 rows",
        "post-instructions.log": "Wrote 422 function-body instruction rows",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=6077",
        "queue-probe.log": "Commentless functions: 36",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave894.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave894_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BAD:", "MISSING:", "BADNAME:", "BADSIG:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 36, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 6077, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6077, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00598390", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFastVB__DetectCpuFeatureMask", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173149063, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        DXTEXTURE_DOC: ("Wave894 JPEG header parser tail", TAG, "0x0059364c CDXTexture__GetImageHeaderInfo", "0x00594f15 CTexture__FinalizeDecodeFormatDescriptor", "0x0057ba81", "0x0059d86d", BACKUP_PATH),
        TEXTURE_DOC: ("Wave894 JPEG header parser tail", TAG, "0x005913b0 CFastVB__JpegParser_ResetFrameState", "0x00591720 CFastVB__JpegParser_ParseSOFComponents", "0x00594f15 CTexture__FinalizeDecodeFormatDescriptor", BACKUP_PATH),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-jpeg-header-parser-tail-wave894")
        == r"py -3 tools\ghidra_jpeg_header_parser_tail_wave894_probe.py --check",
        "missing package script",
        failures,
    )
    require(any(row.get("task") == TASK for row in read_jsonl(LEDGER)), "missing Wave894 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20549 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave894 attempt row", failures)


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
        print("Wave894 JPEG header-parser probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave894 JPEG header-parser probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
