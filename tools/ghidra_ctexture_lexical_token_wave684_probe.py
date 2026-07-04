#!/usr/bin/env python3
"""Validate Wave684 CTexture lexical-token read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave684-ctexture-lexical-token"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctexture_lexical_token_wave684_2026-05-21.md"
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
    "ctexture-lexical-token-wave684",
    "wave684-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

TARGETS = {
    "0x0058c0e4": (
        "CFastVB__ResetConversionStatus",
        "void __fastcall CFastVB__ResetConversionStatus(void * conversion_status_slot)",
        ("conversion status slot", "CFastVB state", "status enum"),
        BASE_TAGS | {"fastvb-bridge", "conversion-status", "state-reset", "lexical-tranche-head"},
    ),
    "0x0058c178": (
        "CDXTexture__InsertOrFindKeyInSortedTable",
        "int __thiscall CDXTexture__InsertOrFindKeyInSortedTable(void * this, int key_value, uint * out_index, void * unused_context)",
        ("sorted key table", "out_index", "default value 1"),
        BASE_TAGS | {"cdxtexture", "sorted-key-table", "binary-search", "table-insert", "lexical-token-support"},
    ),
    "0x0058c457": (
        "CTexture__ParseFloatingLiteral",
        "int __thiscall CTexture__ParseFloatingLiteral(void * this, char * source_cursor, double * out_value, void * unused_context)",
        ("dot-digit floating literal", "CRT double parser", "consumed length"),
        BASE_TAGS | {"lexer", "floating-literal", "double-parse", "source-span", "literal-parser"},
    ),
    "0x0058c5d3": (
        "CTexture__ParseIdentifierToken",
        "uint __thiscall CTexture__ParseIdentifierToken(void * this, char * source_cursor, void * out_identifier_node, void * unused_context)",
        ("CRT character-class mask", "this+0x2c", "out_identifier_node"),
        BASE_TAGS | {"lexer", "identifier-token", "token-list", "allocation", "source-span"},
    ),
    "0x0058c652": (
        "CTexture__ParseOperatorToken",
        "int __thiscall CTexture__ParseOperatorToken(void * this, char * source_cursor, char * out_operator_text, void * unused_context)",
        ("operators and punctuators", "out_operator_text", "consumed length"),
        BASE_TAGS | {"lexer", "operator-token", "punctuator-token", "source-span", "parser-token"},
    ),
    "0x0058c75e": (
        "CTexture__ReadTypePrefixToken_FH",
        "int __thiscall CTexture__ReadTypePrefixToken_FH(void * this, char * source_cursor, void * out_token_kind, void * unused_context)",
        ("optional f or h suffix", "token-kind values 7", "suffix length"),
        BASE_TAGS | {"lexer", "type-prefix", "numeric-suffix", "float-token", "token-kind"},
    ),
    "0x0058c7a4": (
        "CTexture__ParseIntegerSuffix_UL",
        "int __thiscall CTexture__ParseIntegerSuffix_UL(void * this, char * source_cursor, void * out_token_kind, void * unused_context)",
        ("optional u and l", "unsigned-long", "suffix length"),
        BASE_TAGS | {"lexer", "integer-suffix", "numeric-suffix", "integer-token", "token-kind"},
    ),
    "0x0058c82b": (
        "CDXTexture__SetKeyEntryModeFlags",
        "void __thiscall CDXTexture__SetKeyEntryModeFlags(void * this, void * key_value, int mode_value, uint unused_context)",
        ("mode 0xff", "mode 0x10", "low nibble"),
        BASE_TAGS | {"cdxtexture", "sorted-key-table", "mode-flags", "flag-update", "lexical-token-support"},
    ),
    "0x0058c893": (
        "CTexture__AppendDiagnosticMessage",
        "void __cdecl CTexture__AppendDiagnosticMessage(void * diagnostic_accumulator, void * source_location, int diagnostic_id, char * diagnostic_format, ...)",
        ("varargs diagnostic formatter", "error X%u", "+0x08"),
        BASE_TAGS | {"diagnostic-report", "varargs", "text-list", "message-format", "lexer-diagnostic"},
    ),
    "0x0058c95c": (
        "CTexture__AppendDiagnosticMessageDedup",
        "int __cdecl CTexture__AppendDiagnosticMessageDedup(void * diagnostic_accumulator, void * source_location, int diagnostic_id, char * diagnostic_format, ...)",
        ("sorted diagnostic key table", "0x20 emitted flag", "warning accumulator"),
        BASE_TAGS | {"diagnostic-report", "diagnostic-dedup", "sorted-key-table", "varargs", "message-format"},
    ),
    "0x0058cabd": (
        "CTexture__LogUnexpectedTokenError",
        "void __thiscall CTexture__LogUnexpectedTokenError(void * this, int diagnostic_id, void * token_record, void * unused_context)",
        ("unexpected-token reporter", "string constant", "end of file"),
        BASE_TAGS | {"diagnostic-report", "unexpected-token", "parser-token", "lexer-diagnostic", "address-suffix-removed"},
    ),
    "0x0058cc00": (
        "CTexture__SkipWhitespaceAndComments",
        "int __fastcall CTexture__SkipWhitespaceAndComments(void * source_cursor_state)",
        ("semicolon comments", "+0x28 bit 1", "diagnostic id 0x3e9"),
        BASE_TAGS | {"lexer", "whitespace-skip", "comment-skip", "line-counter", "diagnostic-report"},
    ),
    "0x0058cd30": (
        "CTexture__ParseHexIntegerLiteral",
        "int __thiscall CTexture__ParseHexIntegerLiteral(void * this, char * source_cursor, uint * out_value, void * unused_context)",
        ("0x prefix", "diagnostic id 0x3ea", "consumed length"),
        BASE_TAGS | {"lexer", "integer-literal", "hex-literal", "diagnostic-report", "source-span"},
    ),
    "0x0058cdd5": (
        "CTexture__ParseOctalIntegerLiteral",
        "int __thiscall CTexture__ParseOctalIntegerLiteral(void * this, char * source_cursor, uint * out_value, void * unused_context)",
        ("leading-zero octal integer", "0xe0000000", "diagnostic id 0x3eb"),
        BASE_TAGS | {"lexer", "integer-literal", "octal-literal", "diagnostic-report", "source-span"},
    ),
    "0x0058ce51": (
        "CTexture__ParseDecimalIntegerLiteral",
        "int __thiscall CTexture__ParseDecimalIntegerLiteral(void * this, char * source_cursor, uint * out_value, void * unused_context)",
        ("0x19999999", "wraparound paths", "diagnostic id 0x3ec"),
        BASE_TAGS | {"lexer", "integer-literal", "decimal-literal", "diagnostic-report", "source-span"},
    ),
    "0x0058cef2": (
        "CTexture__ParseEscapedCharLiteral",
        "int __thiscall CTexture__ParseEscapedCharLiteral(void * this, char * source_cursor, int * out_char_value, void * unused_context)",
        ("C-style escape", "octal and hex escapes", "diagnostic id 0x3ef"),
        BASE_TAGS | {"lexer", "char-literal", "escape-sequence", "diagnostic-report", "source-span"},
    ),
    "0x0058d088": (
        "CTexture__ParseDottedFormatAndResolveDescriptor",
        "int __thiscall CTexture__ParseDottedFormatAndResolveDescriptor(void * this, char * source_cursor, void * out_format_descriptor, void * unused_context)",
        ("two-letter dotted format prefix", "named-format descriptor lookup", "out_format_descriptor"),
        BASE_TAGS | {"lexer", "format-descriptor", "dotted-format", "descriptor-lookup", "address-suffix-removed"},
    ),
    "0x0058d18b": (
        "CTexture__ParseCharLiteralToken",
        "int __thiscall CTexture__ParseCharLiteralToken(void * this, char * source_cursor, int * out_char_value, void * unused_context)",
        ("single-quoted character token", "escaped-character helper", "closing quote"),
        BASE_TAGS | {"lexer", "char-literal", "escape-sequence", "literal-parser", "source-span"},
    ),
    "0x0058d1ca": (
        "CTexture__ParseStringLiteralToken",
        "int __thiscall CTexture__ParseStringLiteralToken(void * this, char * source_cursor, void * out_string_node, void * unused_context)",
        ("angle-bracket include-style strings", "diagnostic ids 0x3ed and 0x3ee", "token-list context"),
        BASE_TAGS | {"lexer", "string-literal", "include-string", "token-list", "diagnostic-report"},
    ),
    "0x0058d2ad": (
        "CTexture__ReadNextLexToken",
        "int __thiscall CTexture__ReadNextLexToken(void * this, void * source_location, void * out_token_record, void * unused_context)",
        ("float, character, hex/octal/decimal integer", "out_token_record", "returns 0"),
        BASE_TAGS | {"lexer", "token-fetch", "literal-parser", "parser-token", "source-span"},
    ),
}

DOC_TOKENS = (
    "Wave684 CTexture lexical token",
    "ctexture-lexical-token-wave684",
    "0x0058c0e4 CFastVB__ResetConversionStatus",
    "0x0058d2ad CTexture__ReadNextLexToken",
    "0x0058d419 CTexture__ParseVertexSemanticUsageToken",
)

OVERCLAIM_TOKENS = (
    "runtime lexer behavior proven",
    "runtime texture compiler behavior proven",
    "exact token enum proven",
    "exact diagnostic catalog proven",
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
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 118, "xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 660, "instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata.tsv")) == 20, "pre metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags.tsv")) == 20, "pre tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs.tsv")) == 118, "pre xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions.tsv")) == 660, "pre instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-wide.tsv")) == 2020, "pre wide instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-pre" / "index.tsv")) == 20, "pre decompile row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata-candidate.tsv")) == 25, "candidate metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags-candidate.tsv")) == 25, "candidate tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs-candidate.tsv")) == 128, "candidate xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-candidate.tsv")) == 825, "candidate instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")) == 25, "candidate decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave684 static read-back" in comment, f"missing Wave684 comment at {address}", failures)
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
        "apply-wave684-dry.log": "SUMMARY: updated=0 skipped=20 renamed=0 would_rename=2 signature_updated=20 varargs=0 missing=0 bad=0",
        "apply-wave684-apply.log": "SUMMARY: updated=20 skipped=0 renamed=2 would_rename=0 signature_updated=20 varargs=2 missing=0 bad=0",
        "apply-wave684-final-dry.log": "SUMMARY: updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0",
        "post-metadata.log": "targets=20 found=20 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=20 missing=0",
        "post-decompile.log": "targets=20 dumped=20 missing=0 failed=0",
        "post-instructions.log": "Wrote 660 instruction rows",
        "post-xrefs.log": "Wrote 118 rows",
        "pre-metadata.log": "targets=20 found=20 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=20 missing=0",
        "pre-decompile.log": "targets=20 dumped=20 missing=0 failed=0",
        "pre-instructions.log": "Wrote 660 instruction rows",
        "pre-instructions-wide.log": "Wrote 2020 instruction rows",
        "pre-xrefs.log": "Wrote 118 rows",
        "pre-metadata-candidate.log": "targets=25 found=25 missing=0",
        "pre-tags-candidate.log": "ExportFunctionTagsByAddress complete: rows=25 missing=0",
        "pre-decompile-candidate.log": "targets=25 dumped=25 missing=0 failed=0",
        "pre-instructions-candidate.log": "Wrote 825 instruction rows",
        "pre-xrefs-candidate.log": "Wrote 128 rows",
        "queue-refresh.log": "total_functions=6098 commented_functions=3911",
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
    require(quality.get("commentlessFunctionCount") == 2187, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 410, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x0058d419", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__ParseVertexSemanticUsageToken", f"next head name mismatch: {head}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("BackupPath") == "[maintainer-local-ghidra-backup-root]\\BEA_20260521-095848_post_wave684_ctexture_lexical_token_verified", "backup path mismatch", failures)
    require(backup.get("FileCount") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(backup.get("TotalBytes")) == 164629383, f"backup bytes mismatch: {backup}", failures)
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
        package.get("scripts", {}).get("test:ghidra-ctexture-lexical-token-wave684")
        == "py -3 tools\\ghidra_ctexture_lexical_token_wave684_probe.py --check",
        "package script missing/mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave684 CTexture lexical token" for row in ledger_rows), "ledger missing Wave684", failures)
    require(any(row.get("task") == "Wave684 CTexture lexical token" for row in attempt_rows), "attempt log missing Wave684", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20340, f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    require(any("Wave684 CTexture lexical token" in note for note in tracking.get("notes", [])), "tracking notes missing Wave684", failures)


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
        print("Wave684 CTexture lexical-token probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave684 CTexture lexical-token probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
