#!/usr/bin/env python3
"""Validate Wave685 CTexture parser-symbol-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave685-ctexture-parser-symbol-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctexture_parser_symbol_tail_wave685_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
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
    "ctexture-parser-symbol-tail-wave685",
    "wave685-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

TARGETS = {
    "0x0058d419": (
        "CTexture__ParseVertexSemanticUsageToken",
        "int __thiscall CTexture__ParseVertexSemanticUsageToken(void * this, char * semantic_text, void * out_semantic_kind, void * out_usage_index)",
        ("vertex semantic string", "usage below 16", "HRESULT-style"),
        BASE_TAGS | {"parser-symbol", "vertex-semantic", "semantic-usage", "hresult", "tranche-head"},
    ),
    "0x0058d6b4": (
        "CTexture__HashIdentifierMod7",
        "uint __stdcall CTexture__HashIdentifierMod7(char * identifier_text)",
        ("hash = hash * 0x13", "modulo seven", "null or empty"),
        BASE_TAGS | {"parser-symbol", "identifier-hash", "hash-bucket-count-7", "case-fold", "symbol-table-support"},
    ),
    "0x0058d6f0": (
        "CTexture__FindIdentifierInHashTable",
        "void * __thiscall CTexture__FindIdentifierInHashTable(void * this, char * identifier_text)",
        ("one of seven buckets", "offset +0x20", "lstrcmpiA"),
        BASE_TAGS | {"parser-symbol", "identifier-hash", "hash-bucket-count-7", "symbol-lookup", "linked-list"},
    ),
    "0x0058d722": (
        "CDXTexture__CollectHashBucketsToArray",
        "void __thiscall CDXTexture__CollectHashBucketsToArray(void * this, void * out_node_array)",
        ("seven hash buckets", "node offset +0x20", "out_node_array"),
        BASE_TAGS | {"parser-symbol", "hash-bucket-count-7", "symbol-table-flatten", "linked-list", "cdxtexture"},
    ),
    "0x0058d747": (
        "CTexture__ResetParserSemanticValue",
        "void __fastcall CTexture__ResetParserSemanticValue(void * semantic_value)",
        ("0x00, 0x04, 0x08", "0x58, 0x5c, 0x60", "0x78"),
        BASE_TAGS | {"parser-symbol", "semantic-value-reset", "yacc-parser", "state-clear", "parser-support"},
    ),
    "0x0058d763": (
        "CTexture__ReportYaccSyntaxError",
        "void __cdecl CTexture__ReportYaccSyntaxError(void * parser_state, char * message_format, ...)",
        ("parser error flag", "unexpected-token diagnostic", "cdecl"),
        BASE_TAGS | {"parser-symbol", "yacc-syntax-error", "diagnostic-report", "varargs", "parser-error-flag"},
    ),
    "0x0058d88d": (
        "CTexture__NormalizeParserResultOrReport",
        "int __thiscall CTexture__NormalizeParserResultOrReport(void * this, void * reduction_result)",
        ("production failed", "+0x4c", "+0x50"),
        BASE_TAGS | {"parser-symbol", "reduction-result", "diagnostic-report", "parser-error-flag", "yacc-parser"},
    ),
    "0x0058d8c2": (
        "CTexture__ParseShaderSemanticToken",
        "uint __thiscall CTexture__ParseShaderSemanticToken(void * this, void * token_record)",
        ("token_record+0x08", "state +0x38", "0x10d"),
        BASE_TAGS | {"parser-symbol", "shader-semantic-token", "semantic-modifier", "shader-version-table", "parser-token"},
    ),
}

DOC_TOKENS = (
    "Wave685 CTexture parser symbol tail",
    "ctexture-parser-symbol-tail-wave685",
    "0x0058d419 CTexture__ParseVertexSemanticUsageToken",
    "0x0058d8c2 CTexture__ParseShaderSemanticToken",
    "0x0058e256 CTexture__ParseChannelMaskStrict",
)

OVERCLAIM_TOKENS = (
    "runtime texture compiler behavior proven",
    "shader semantic table schema proven",
    "symbol-node structure proven",
    "yacc state layout proven",
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
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 17, "xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 264, "instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata.tsv")) == 8, "pre metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags.tsv")) == 8, "pre tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs.tsv")) == 17, "pre xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions.tsv")) == 264, "pre instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-pre" / "index.tsv")) == 8, "pre decompile row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata-candidate.tsv")) == 15, "candidate metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags-candidate.tsv")) == 15, "candidate tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs-candidate.tsv")) == 30, "candidate xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-candidate.tsv")) == 495, "candidate instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")) == 15, "candidate decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave685 static read-back" in comment, f"missing Wave685 comment at {address}", failures)
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
    expected_exact = {
        "apply-wave685-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 varargs=0 missing=0 bad=0",
        "apply-wave685-apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 varargs=1 missing=0 bad=0",
        "apply-wave685-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-instructions.log": "Wrote 264 instruction rows",
        "post-xrefs.log": "Wrote 17 rows",
        "pre-metadata.log": "targets=8 found=8 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "pre-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "pre-instructions.log": "Wrote 264 instruction rows",
        "pre-xrefs.log": "Wrote 17 rows",
        "pre-metadata-candidate.log": "targets=15 found=15 missing=0",
        "pre-tags-candidate.log": "ExportFunctionTagsByAddress complete: rows=15 missing=0",
        "pre-decompile-candidate.log": "targets=15 dumped=15 missing=0 failed=0",
        "pre-instructions-candidate.log": "Wrote 495 instruction rows",
        "pre-xrefs-candidate.log": "Wrote 30 rows",
        "queue-refresh.log": "total_functions=6098 commented_functions=3919",
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
    require(quality.get("commentlessFunctionCount") == 2179, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 402, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x0058e256", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__ParseChannelMaskStrict", f"next head name mismatch: {head}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("BackupPath") == "[maintainer-local-ghidra-backup-root]\\BEA_20260521-102431_post_wave685_ctexture_parser_symbol_tail_verified", "backup path mismatch", failures)
    require(backup.get("FileCount") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(backup.get("TotalBytes")) == 164662151, f"backup bytes mismatch: {backup}", failures)
    require(backup.get("DiffCount") == 0, f"backup diff mismatch: {backup}", failures)


def check_docs(failures: list[str]) -> None:
    for path in (
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        TEXTURE_DOC,
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
        package.get("scripts", {}).get("test:ghidra-ctexture-parser-symbol-tail-wave685")
        == "py -3 tools\\ghidra_ctexture_parser_symbol_tail_wave685_probe.py --check",
        "package script missing/mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave685 CTexture parser symbol tail" for row in ledger_rows), "ledger missing Wave685", failures)
    require(any(row.get("task") == "Wave685 CTexture parser symbol tail" for row in attempt_rows), "attempt log missing Wave685", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20341, f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    require(any("Wave685 CTexture parser symbol tail" in note for note in tracking.get("notes", [])), "tracking notes missing Wave685", failures)


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
        print("Wave685 CTexture parser-symbol-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave685 CTexture parser-symbol-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
