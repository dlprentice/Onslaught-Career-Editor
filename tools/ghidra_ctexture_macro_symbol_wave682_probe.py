#!/usr/bin/env python3
"""Validate Wave682 CTexture macro-symbol read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave682-ctexture-macro-symbol"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctexture_macro_symbol_wave682_2026-05-21.md"
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
    "ctexture-macro-symbol-wave682",
    "wave682-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

TARGETS = {
    "0x0058a578": (
        "CTexture__GetSymbolNameLength",
        "int __stdcall CTexture__GetSymbolNameLength(char * symbol_name)",
        ("zero bucket/index", "current-name", "NUL terminator"),
        BASE_TAGS | {"macro-symbol", "symbol-name", "bucket-index", "current-name-retained", "preprocessor-directive"},
    ),
    "0x0058a58d": (
        "CTexture__InsertOrReplaceMacroSymbol",
        "int __thiscall CTexture__InsertOrReplaceMacroSymbol(void * this, void * macro_symbol_node)",
        ("this+0x4c", "replaces an existing", "first greater name"),
        BASE_TAGS | {"macro-symbol", "macro-insert", "macro-replace", "sorted-list", "preprocessor-directive", "recursive-cleanup"},
    ),
    "0x0058a60a": (
        "CTexture__FindMacroSymbol",
        "int __thiscall CTexture__FindMacroSymbol(void * this, char * symbol_name, void * out_macro_value, void * out_macro_payload)",
        ("this+0x4c", "+0x04/+0x08", "sorted chain"),
        BASE_TAGS | {"macro-symbol", "macro-lookup", "sorted-list", "output-slot", "preprocessor-directive"},
    ),
    "0x0058a67b": (
        "CTexture__EscapeQuotedStringInPlace",
        "void __stdcall CTexture__EscapeQuotedStringInPlace(char * source_text, int source_length, char * destination_text)",
        ("quote-state", "backslash", "destination is null"),
        BASE_TAGS | {"quoted-string", "escape-copy", "macro-expression", "preprocessor-directive", "current-name-retained"},
    ),
    "0x0058a6e0": (
        "CTexture__NormalizeConditionalResultOrReport",
        "int __thiscall CTexture__NormalizeConditionalResultOrReport(void * this, int condition_result)",
        ("conditional-expression result", "+0x2c", "diagnostic"),
        BASE_TAGS | {"conditional-expression", "diagnostic-report", "error-state", "preprocessor-directive"},
    ),
    "0x0058a713": (
        "CTexture__HandleDirective_Define",
        "int __thiscall CTexture__HandleDirective_Define(void * this, char * macro_name, int has_parameter_list)",
        ("#define handler", "0x10-byte macro-symbol node", "replacement tokens"),
        BASE_TAGS | {"define-directive", "macro-symbol", "macro-parameters", "macro-replacement", "preprocessor-directive", "allocation"},
    ),
    "0x0058a981": (
        "CTexture__RemoveMacroSymbol",
        "int __thiscall CTexture__RemoveMacroSymbol(void * this, char * symbol_name)",
        ("this+0x4c", "unlinks the matching node", "destroys it"),
        BASE_TAGS | {"undef-directive", "macro-symbol", "macro-remove", "sorted-list", "recursive-cleanup", "preprocessor-directive"},
    ),
    "0x0058a9ef": (
        "CTexture__HandleDirective_Pragma",
        "int __fastcall CTexture__HandleDirective_Pragma(void * directive_parser_context)",
        ("pack_matrix", "warning", "+0x28"),
        BASE_TAGS | {"pragma-directive", "pragma-dispatch", "directive-parser-context", "preprocessor-directive", "line-skip"},
    ),
    "0x0058aa69": (
        "CTexture__HandleDirective_IfdefIfndef",
        "int __thiscall CTexture__HandleDirective_IfdefIfndef(void * this, char * symbol_name)",
        ("#ifdef/#ifndef", "kind range 2..4", "+0x18"),
        BASE_TAGS | {"ifdef-directive", "ifndef-directive", "macro-lookup", "conditional-expression", "preprocessor-directive", "diagnostic-report"},
    ),
}

DOC_TOKENS = (
    "Wave682 CTexture macro symbol",
    "ctexture-macro-symbol-wave682",
    "0x0058a578 CTexture__GetSymbolNameLength",
    "0x0058aa69 CTexture__HandleDirective_IfdefIfndef",
    "0x0058b1a0 CTexture__InitPreprocessorDefaultDefines",
)

OVERCLAIM_TOKENS = (
    "runtime macro expansion proven",
    "runtime preprocessor behavior proven",
    "exact macro node layout proven",
    "exact ifdef/ifndef polarity proven",
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
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 21, "xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 333, "instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata.tsv")) == 9, "pre metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags.tsv")) == 9, "pre tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs.tsv")) == 21, "pre xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions.tsv")) == 333, "pre instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-wide.tsv")) == 3249, "pre wide instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-pre" / "index.tsv")) == 9, "pre decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave682 static read-back" in comment, f"missing Wave682 comment at {address}", failures)
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
        "apply-wave682-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=9 varargs=0 missing=0 bad=0",
        "apply-wave682-apply.log": "SUMMARY: updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 varargs=0 missing=0 bad=0",
        "apply-wave682-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "post-instructions.log": "targets=9 missing=0",
        "post-xrefs.log": "Wrote 21 rows",
        "pre-metadata.log": "targets=9 found=9 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "pre-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "pre-instructions.log": "targets=9 missing=0",
        "pre-instructions-wide.log": "Wrote 3249 instruction rows",
        "pre-xrefs.log": "Wrote 21 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)
    require("Wrote 333 instruction rows" in read_text(BASE / "post-instructions.log"), "post instruction row count mismatch", failures)
    require("Wrote 333 instruction rows" in read_text(BASE / "pre-instructions.log"), "pre instruction row count mismatch", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 2220, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 443, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x0058b1a0", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__InitPreprocessorDefaultDefines", f"next head name mismatch: {head}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("BackupPath") == "[maintainer-local-ghidra-backup-root]\\BEA_20260521-085906_post_wave682_ctexture_macro_symbol_verified", "backup path mismatch", failures)
    require(backup.get("FileCount") == 19, f"backup file count mismatch: {backup}", failures)
    require(backup.get("TotalBytes") == 164498311, f"backup bytes mismatch: {backup}", failures)
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
        package.get("scripts", {}).get("test:ghidra-ctexture-macro-symbol-wave682")
        == "py -3 tools\\ghidra_ctexture_macro_symbol_wave682_probe.py --check",
        "package script missing/mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave682 CTexture macro symbol" for row in ledger_rows), "ledger missing Wave682", failures)
    require(any(row.get("task") == "Wave682 CTexture macro symbol" for row in attempt_rows), "attempt log missing Wave682", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20338, f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    require(any("Wave682 CTexture macro symbol" in note for note in tracking.get("notes", [])), "tracking notes missing Wave682", failures)


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
        print("Wave682 CTexture macro-symbol probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave682 CTexture macro-symbol probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
