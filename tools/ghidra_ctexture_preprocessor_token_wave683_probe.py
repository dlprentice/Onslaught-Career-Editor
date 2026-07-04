#!/usr/bin/env python3
"""Validate Wave683 CTexture preprocessor-token read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave683-ctexture-preprocessor-token"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctexture_preprocessor_token_wave683_2026-05-21.md"
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
    "ctexture-preprocessor-token-wave683",
    "wave683-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

TARGETS = {
    "0x0058b1a0": (
        "CTexture__InitPreprocessorDefaultDefines",
        "int __thiscall CTexture__InitPreprocessorDefaultDefines(void * this, void * default_define_pairs)",
        ("DIRECT3D", "DIRECT3D_VERSION/D3DX_VERSION", "default-define pairs"),
        BASE_TAGS | {"preprocessor-defaults", "macro-symbol", "define-directive", "token-list", "preprocessor-directive"},
    ),
    "0x0058b3c7": (
        "CTexture__ExecuteDirectiveParserAction",
        "void __thiscall CTexture__ExecuteDirectiveParserAction(void * this, int action_id, uint operand_count)",
        ("directive-parser action dispatcher", "stack underflow", "divide-by-zero"),
        BASE_TAGS | {"directive-parser", "parser-action", "conditional-expression", "preprocessor-directive", "diagnostic-report"},
    ),
    "0x0058bd87": (
        "CTexture__GetNextTokenWithPreprocessor",
        "uint __thiscall CTexture__GetNextTokenWithPreprocessor(void * this, void * out_token)",
        ("__FILE__/__LINE__", "include-frame EOF", "disabled conditional"),
        BASE_TAGS | {"token-fetch", "directive-parser", "include-frame", "conditional-expression", "preprocessor-directive", "pushback-token"},
    ),
    "0x0058c08a": (
        "CTexture__Preprocessor_PopIncludeFrameAtEof",
        "int __fastcall CTexture__Preprocessor_PopIncludeFrameAtEof(void * preprocessor_context)",
        ("drains preprocessor tokens", "+0x48", "+0x80"),
        BASE_TAGS | {"include-frame", "eof-token", "preprocessor-context", "preprocessor-directive", "address-suffix-removed"},
    ),
    "0x0058c0ea": (
        "CTexture__TokenList_FreeChain",
        "void __fastcall CTexture__TokenList_FreeChain(void * list_head_slot)",
        ("singly linked allocation chain", "stores the next link", "until the list is empty"),
        BASE_TAGS | {"token-list", "list-free", "allocation", "preprocessor-directive", "address-suffix-removed"},
    ),
    "0x0058c107": (
        "CTexture__TokenList_PushAllocatedNode",
        "void * __thiscall CTexture__TokenList_PushAllocatedNode(void * this, int payload_size)",
        ("payload_size+4", "return value", "identifier/string-token callers"),
        BASE_TAGS | {"token-list", "list-push", "allocation", "return-pointer", "preprocessor-directive", "address-suffix-removed"},
    ),
    "0x0058c129": (
        "CTexture__TokenList_InitState",
        "void __fastcall CTexture__TokenList_InitState(void * token_list_state)",
        ("0x20-byte", "+0x10", "default flag/value"),
        BASE_TAGS | {"token-list", "state-init", "preprocessor-context", "preprocessor-directive", "address-suffix-removed"},
    ),
    "0x0058c149": (
        "CTexture__TokenList_ClearAndFreeBuffers",
        "void __fastcall CTexture__TokenList_ClearAndFreeBuffers(void * token_list_state)",
        ("+0x18 and +0x1c", "buffer/string", "frees the token-list node chain"),
        BASE_TAGS | {"token-list", "list-free", "buffer-free", "preprocessor-context", "preprocessor-directive", "address-suffix-removed"},
    ),
    "0x0058c2b9": (
        "CTexture__AppendDiagnosticTextLine",
        "int __thiscall CTexture__AppendDiagnosticTextLine(void * this, char * text_line)",
        ("diagnostic text line", "byte-count", "incoming NUL-terminated string"),
        BASE_TAGS | {"diagnostic-report", "text-list", "allocation", "preprocessor-directive"},
    ),
    "0x0058c30f": (
        "CTexture__TokenList_EmitConcatenatedText",
        "int __thiscall CTexture__TokenList_EmitConcatenatedText(void * this, void * out_stream_slot)",
        ("memory write stream", "linked text-node payloads", "NUL terminator"),
        BASE_TAGS | {"token-list", "text-list", "stream-output", "macro-replacement", "preprocessor-directive", "address-suffix-removed"},
    ),
    "0x0058c378": (
        "CTexture__TokenList_GetCount",
        "int __fastcall CTexture__TokenList_GetCount(void * token_list_state)",
        ("+0x08", "token-list state", "accumulated token/text list content"),
        BASE_TAGS | {"token-list", "count-field", "preprocessor-context", "preprocessor-directive", "address-suffix-removed"},
    ),
    "0x0058c37c": (
        "CTexture__TokenList_InitState_Extended",
        "void __fastcall CTexture__TokenList_InitState_Extended(void * preprocessor_span_state)",
        ("+0x1c", "extended preprocessor span", "logical line/counter"),
        BASE_TAGS | {"token-list", "state-init", "source-span", "preprocessor-context", "preprocessor-directive", "address-suffix-removed"},
    ),
    "0x0058c3fe": (
        "CTexture__SkipLineContinuationAndAdvance",
        "int __fastcall CTexture__SkipLineContinuationAndAdvance(void * source_cursor_state)",
        ("backslash-LF", "backslash-CRLF", "line counter"),
        BASE_TAGS | {"source-span", "line-continuation", "cursor-advance", "preprocessor-directive"},
    ),
}

DOC_TOKENS = (
    "Wave683 CTexture preprocessor token",
    "ctexture-preprocessor-token-wave683",
    "0x0058b1a0 CTexture__InitPreprocessorDefaultDefines",
    "0x0058c3fe CTexture__SkipLineContinuationAndAdvance",
    "0x0058c0e4 CFastVB__ResetConversionStatus",
)

OVERCLAIM_TOKENS = (
    "runtime macro expansion proven",
    "runtime preprocessor behavior proven",
    "exact token enum proven",
    "exact parser action enum proven",
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
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 31, "xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 585, "instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata.tsv")) == 13, "pre metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags.tsv")) == 13, "pre tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs.tsv")) == 31, "pre xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions.tsv")) == 585, "pre instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-wide.tsv")) == 14313, "pre wide instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-pre" / "index.tsv")) == 13, "pre decompile row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata-candidate.tsv")) == 18, "candidate metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags-candidate.tsv")) == 18, "candidate tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs-candidate.tsv")) == 40, "candidate xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-candidate.tsv")) == 810, "candidate instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")) == 18, "candidate decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave683 static read-back" in comment, f"missing Wave683 comment at {address}", failures)
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
        "apply-wave683-dry.log": "SUMMARY: updated=0 skipped=13 renamed=0 would_rename=8 signature_updated=13 varargs=0 missing=0 bad=0",
        "apply-wave683-apply.log": "SUMMARY: updated=13 skipped=0 renamed=8 would_rename=0 signature_updated=13 varargs=0 missing=0 bad=0",
        "apply-wave683-final-dry.log": "SUMMARY: updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0",
        "post-metadata.log": "targets=13 found=13 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "post-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "post-instructions.log": "targets=13 missing=0",
        "post-xrefs.log": "Wrote 31 rows",
        "pre-metadata.log": "targets=13 found=13 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "pre-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "pre-instructions.log": "targets=13 missing=0",
        "pre-instructions-wide.log": "Wrote 14313 instruction rows",
        "pre-xrefs.log": "Wrote 31 rows",
        "pre-metadata-candidate.log": "targets=18 found=18 missing=0",
        "pre-tags-candidate.log": "ExportFunctionTagsByAddress complete: rows=18 missing=0",
        "pre-decompile-candidate.log": "targets=18 dumped=18 missing=0 failed=0",
        "pre-instructions-candidate.log": "targets=18 missing=0",
        "pre-xrefs-candidate.log": "Wrote 40 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)
    require("Wrote 585 instruction rows" in read_text(BASE / "post-instructions.log"), "post instruction row count mismatch", failures)
    require("Wrote 585 instruction rows" in read_text(BASE / "pre-instructions.log"), "pre instruction row count mismatch", failures)
    require("Wrote 810 instruction rows" in read_text(BASE / "pre-instructions-candidate.log"), "candidate instruction row count mismatch", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 2207, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 430, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x0058c0e4", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CFastVB__ResetConversionStatus", f"next head name mismatch: {head}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("BackupPath") == "[maintainer-local-ghidra-backup-root]\\BEA_20260521-092456_post_wave683_ctexture_preprocessor_token_verified", "backup path mismatch", failures)
    require(backup.get("FileCount") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(backup.get("TotalBytes")) == 164531079, f"backup bytes mismatch: {backup}", failures)
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
        package.get("scripts", {}).get("test:ghidra-ctexture-preprocessor-token-wave683")
        == "py -3 tools\\ghidra_ctexture_preprocessor_token_wave683_probe.py --check",
        "package script missing/mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave683 CTexture preprocessor token" for row in ledger_rows), "ledger missing Wave683", failures)
    require(any(row.get("task") == "Wave683 CTexture preprocessor token" for row in attempt_rows), "attempt log missing Wave683", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20339, f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    require(any("Wave683 CTexture preprocessor token" in note for note in tracking.get("notes", [])), "tracking notes missing Wave683", failures)


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
        print("Wave683 CTexture preprocessor-token probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave683 CTexture preprocessor-token probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
