#!/usr/bin/env python3
"""Validate Wave893 CTexture directive-parser read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave893-ctexture-directive-parser-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctexture_directive_parser_tail_wave893_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave893 CTexture directive parser tail"
TAG = "ctexture-directive-parser-tail-wave893"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260526-055039_post_wave893_ctexture_directive_parser_tail_verified"
STRICT_PROXY = "6073/6113 = 99.35%"
NEXT_HEAD = "0x005913b0 CFastVB__JpegParser_ResetFrameState"

TARGETS = {
    "0x0058aacf": ("CTexture__HandleDirective_If", "int CTexture__HandleDirective_If(void)", ("0x0058bf56", "macro expansion", "##")),
    "0x0058b812": ("CTexture__RunDirectiveParser", "int CTexture__RunDirectiveParser(void)", ("DAT_009d1430", "DAT_00657b48", "CTexture__ExecuteDirectiveParserAction")),
    "0x0058bd25": ("CTexture__InitializePreprocessorStateFromMemorySpan", "int CTexture__InitializePreprocessorStateFromMemorySpan(void)", ("0x70-byte", "CTexture__PreprocessorContextCtor", "CTexture__InitPreprocessorDefaultDefines")),
    "0x0058c396": ("CTexture__InitBufferCursorRange", "int CTexture__InitBufferCursorRange(void)", ("CTexture__OpenIncludeSourceAndInitBuffer", "-0x7fffbffb", "source-buffer cursor")),
    "0x0058d821": ("CTexture__EmitParserMessageBySeverity", "int CTexture__EmitParserMessageBySeverity(void)", ("0x00590b1c", "5000", "CTexture__AppendDiagnosticMessageDedup")),
    "0x0058f34c": ("CTexture__ResolveOrCreateRegisterReference", "int CTexture__ResolveOrCreateRegisterReference(void)", ("0x0058fac0", "DAT_005ecd94", "0x7d5")),
    "0x0059020b": ("CTexture__ParseScriptWithYaccTables", "int CTexture__ParseScriptWithYaccTables(void)", ("DAT_009d2010", "DAT_00658438", "CTexture__ApplyParserReductionAction")),
    "0x00590da0": ("CTexture__DrainParserWorkQueue", "int CTexture__DrainParserWorkQueue(void)", ("0x00590f4c", "0xcc", "0xcd")),
}

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave893-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "texture-directive-parser",
    "important-texture-compiler-infrastructure",
    "raw-commentless-tail",
}

CORE_ANCHORS = (
    TASK,
    TAG,
    "0x0058aacf CTexture__HandleDirective_If",
    "0x0058b812 CTexture__RunDirectiveParser",
    "0x0058bd25 CTexture__InitializePreprocessorStateFromMemorySpan",
    "0x0058c396 CTexture__InitBufferCursorRange",
    "0x0058d821 CTexture__EmitParserMessageBySeverity",
    "0x0058f34c CTexture__ResolveOrCreateRegisterReference",
    "0x0059020b CTexture__ParseScriptWithYaccTables",
    "0x00590da0 CTexture__DrainParserWorkQueue",
    "DAT_009d1430",
    "DAT_00657b48",
    "DAT_009d2010",
    "DAT_00658438",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "exact grammar proven",
    "exact layout proven",
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
        "targets-snapshot.tsv": 8,
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 13,
        "pre-instructions.tsv": 1696,
        "pre-decompile/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 13,
        "post-instructions.tsv": 1696,
        "post-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave893 static read-back", "Static retail Ghidra evidence only", "remain unproven", *tokens):
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


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 13 rows",
        "post-instructions.log": "Wrote 1696 function-body instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=6073",
        "queue-probe.log": "Commentless functions: 40",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave893.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave893_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 40, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 6073, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6073, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005913b0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFastVB__JpegParser_ResetFrameState", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173149063, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        TEXTURE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-ctexture-directive-parser-tail-wave893")
        == r"py -3 tools\ghidra_ctexture_directive_parser_tail_wave893_probe.py --check",
        "missing package script",
        failures,
    )
    require(any(row.get("task") == TASK for row in read_jsonl(LEDGER)), "missing Wave893 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20548 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave893 attempt row", failures)


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
        print("Wave893 CTexture directive-parser probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave893 CTexture directive-parser probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
