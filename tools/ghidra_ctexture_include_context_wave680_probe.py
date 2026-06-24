#!/usr/bin/env python3
"""Validate Wave680 CTexture include-context read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave680-ctexture-include-context"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctexture_include_context_wave680_2026-05-21.md"
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
    "ctexture-include-context-wave680",
    "wave680-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
}

TARGETS = {
    "0x00589367": (
        "CTexture__ReleaseIncludeNodeTreeRecursive",
        "void __fastcall CTexture__ReleaseIncludeNodeTreeRecursive(void * include_node)",
        ("include-node release helper", "+0x0c", "payload ownership"),
        BASE_TAGS | {"signature-hardened", "include-node", "payload-release", "recursive-cleanup"},
    ),
    "0x0058939b": (
        "CTexture__IncludeNodeDtor",
        "void * __thiscall CTexture__IncludeNodeDtor(void * this, int delete_flags, int unused_context)",
        ("scalar-deleting destructor wrapper", "delete_flags bit 0", "allocation provenance"),
        BASE_TAGS | {"signature-hardened", "include-node", "scalar-deleting-destructor", "recursive-cleanup"},
    ),
    "0x005893b7": (
        "CTexture__IncludeNodeCtor",
        "void __thiscall CTexture__IncludeNodeCtor(void * this, void * primary_payload, int secondary_payload, int unused_context)",
        ("include-node constructor", "primary_payload", "payload type"),
        BASE_TAGS | {"signature-hardened", "include-node", "payload-slots", "constructor"},
    ),
    "0x005893d1": (
        "CTexture__FreeChildIncludeNodeChainRecursive",
        "void __fastcall CTexture__FreeChildIncludeNodeChainRecursive(void * include_node)",
        ("child-chain cleanup", "+0x0c child link", "ownership split"),
        BASE_TAGS | {"signature-hardened", "include-node-chain", "child-link", "recursive-cleanup"},
    ),
    "0x005893e9": (
        "CTexture__IncludeNodeChain_scalar_deleting_dtor",
        "void * __thiscall CTexture__IncludeNodeChain_scalar_deleting_dtor(void * this, int delete_flags, int unused_context)",
        ("scalar-deleting destructor wrapper", "child-only include-node chains", "ownership split"),
        BASE_TAGS | {"signature-hardened", "include-node-chain", "scalar-deleting-destructor", "recursive-cleanup"},
    ),
    "0x00589405": (
        "CTexture__PreprocessorContextCtor",
        "void * __fastcall CTexture__PreprocessorContextCtor(void * preprocessor_context)",
        ("preprocessor-context constructor", "mapped-file context", "source-provider contract"),
        BASE_TAGS | {"signature-hardened", "preprocessor-context", "mapped-file-context", "gdi-record", "constructor"},
    ),
    "0x00589438": (
        "CTexture__CleanupIncludeContextRecursive",
        "void __fastcall CTexture__CleanupIncludeContextRecursive(void * preprocessor_context)",
        ("recursive include-context cleanup", "GDI object", "provider ABI"),
        BASE_TAGS | {"signature-hardened", "preprocessor-context", "mapped-file-context", "gdi-record", "recursive-cleanup"},
    ),
    "0x0058948d": (
        "CTexture__IncludeContextDtor",
        "void * __thiscall CTexture__IncludeContextDtor(void * this, int delete_flags, int unused_context)",
        ("scalar-deleting destructor wrapper", "include contexts", "context allocation ownership"),
        BASE_TAGS | {"signature-hardened", "preprocessor-context", "scalar-deleting-destructor", "recursive-cleanup"},
    ),
    "0x005894a9": (
        "CTexture__OpenIncludeSourceAndInitBuffer",
        "int CTexture__OpenIncludeSourceAndInitBuffer(void)",
        ("locked-storage include-source open helper", "provider-backed input", "Signature is preserved"),
        BASE_TAGS | {"signature-preserved", "ghidra-locked-storage", "include-source", "mapped-file-context", "provider-backed-buffer"},
    ),
    "0x00589650": (
        "CTexture__InitBufferFromMemorySpan",
        "int CTexture__InitBufferFromMemorySpan(void)",
        ("locked-storage memory-span helper", "caller buffer pointer/count", "Signature is preserved"),
        BASE_TAGS | {"signature-preserved", "ghidra-locked-storage", "memory-span", "buffer-cursor"},
    ),
    "0x00589689": (
        "CTexture__FreeIncludeFileChainRecursive",
        "void __fastcall CTexture__FreeIncludeFileChainRecursive(void * include_file_node)",
        ("include-file chain cleanup", "next link", "allocation ownership"),
        BASE_TAGS | {"signature-hardened", "include-file-chain", "recursive-cleanup"},
    ),
    "0x005896a1": (
        "CTexture__IncludeFileChainDtor",
        "void * __thiscall CTexture__IncludeFileChainDtor(void * this, int delete_flags, int unused_context)",
        ("scalar-deleting destructor wrapper", "include-file chains", "include-file node layout"),
        BASE_TAGS | {"signature-hardened", "include-file-chain", "scalar-deleting-destructor", "recursive-cleanup"},
    ),
    "0x005896bd": (
        "CTexture__DirectiveParserContextCtor",
        "void * __fastcall CTexture__DirectiveParserContextCtor(void * directive_parser_context)",
        ("directive-parser context constructor", "LC_NUMERIC locale", "floating-point control word"),
        BASE_TAGS | {"signature-hardened", "directive-parser-context", "locale-state", "fpu-control", "constructor"},
    ),
    "0x00589762": (
        "CTexture__DirectiveParserContextDtor",
        "void __fastcall CTexture__DirectiveParserContextDtor(void * directive_parser_context)",
        ("directive-parser context destructor", "restores saved locale", "floating-point control word"),
        BASE_TAGS | {"signature-hardened", "directive-parser-context", "locale-state", "fpu-control", "destructor", "recursive-cleanup"},
    ),
    "0x00589802": (
        "CTexture__PushPreprocessorStateNode",
        "int __thiscall CTexture__PushPreprocessorStateNode(void * this, int state_value, int unused_context)",
        ("preprocessor state node", "context +0x48", "state enum"),
        BASE_TAGS | {"signature-hardened", "preprocessor-state", "conditional-frame", "allocation"},
    ),
    "0x00589846": (
        "CTexture__GetCurrentSourceLocation",
        "int __thiscall CTexture__GetCurrentSourceLocation(void * this, void * out_primary_location, void * out_secondary_location, void * unused_context)",
        ("source-location fields", "active include context", "diagnostic behavior"),
        BASE_TAGS | {"signature-hardened", "preprocessor-context", "source-location", "diagnostic-context"},
    ),
    "0x0058986b": (
        "CTexture__GetActiveIncludeRange",
        "int __thiscall CTexture__GetActiveIncludeRange(void * this, void * out_range_start, void * out_range_length, void * unused_context)",
        ("terminal child include context", "guarded length", "range semantics"),
        BASE_TAGS | {"signature-hardened", "include-context", "source-range", "diagnostic-context"},
    ),
    "0x005898a4": (
        "CTexture__MapLexTokenToPreprocessorToken",
        "int __fastcall CTexture__MapLexTokenToPreprocessorToken(void * directive_parser_context)",
        ("lexical token record", "directive keywords", "token enum"),
        BASE_TAGS | {"signature-hardened", "directive-parser-context", "preprocessor-token", "token-map", "conditional-frame"},
    ),
}

DOC_TOKENS = (
    "Wave680 CTexture include context",
    "ctexture-include-context-wave680",
    "0x00589367 CTexture__ReleaseIncludeNodeTreeRecursive",
    "0x005898a4 CTexture__MapLexTokenToPreprocessorToken",
    "0x00589bd6 CTexture__ReportDirectiveParseError",
)

OVERCLAIM_TOKENS = (
    "runtime preprocessor behavior proven",
    "exact node layout proven",
    "exact parser layout proven",
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
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 33, "xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 1458, "instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-context-metadata.tsv")) == 18, "pre-context metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-context-tags.tsv")) == 18, "pre-context tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-context-xrefs.tsv")) == 33, "pre-context xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-context-instructions.tsv")) == 1458, "pre-context instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-context-pre" / "index.tsv")) == 18, "pre-context decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave680 static read-back" in comment, f"missing Wave680 comment at {address}", failures)
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
        "apply-wave680-dry.log": "SUMMARY: updated=0 skipped=18 renamed=0 would_rename=0 signature_updated=16 missing=0 bad=0",
        "apply-wave680-apply.log": "SUMMARY: updated=18 skipped=0 renamed=0 would_rename=0 signature_updated=16 missing=0 bad=0",
        "apply-wave680-final-dry.log": "SUMMARY: updated=0 skipped=18 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=18 found=18 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=18 missing=0",
        "post-decompile.log": "targets=18 dumped=18 missing=0 failed=0",
        "post-instructions.log": "targets=18 missing=0",
        "post-xrefs.log": "Wrote 33 rows",
        "pre-context-metadata.log": "targets=18 found=18 missing=0",
        "pre-context-tags.log": "ExportFunctionTagsByAddress complete: rows=18 missing=0",
        "pre-context-decompile.log": "targets=18 dumped=18 missing=0 failed=0",
        "pre-context-instructions.log": "targets=18 missing=0",
        "pre-context-xrefs.log": "Wrote 33 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)
    require("Wrote 1458 instruction rows" in read_text(BASE / "post-instructions.log"), "post instruction row count mismatch", failures)
    require("Wrote 1458 instruction rows" in read_text(BASE / "pre-context-instructions.log"), "pre-context instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-ctexture-include-context-wave680" in package.get("scripts", {}), "package script missing", failures)
    require((ROOT / "tools" / "ApplyCTextureIncludeContextWave680.java").is_file(), "apply script missing", failures)

    docs = (PUBLIC_NOTE, FUNCTION_INDEX, TEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG)
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave680 CTexture include context" in text, f"Wave680 missing from {path.relative_to(ROOT)}", failures)
        require("ctexture-include-context-wave680" in text, f"Wave680 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 164465543, "backup byteCount mismatch", failures)
    require("post_wave680_ctexture_include_context_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2239, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1216, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 462, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00589bd6", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__ReportDirectiveParseError", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave680 CTexture include context", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave680 CTexture include context", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20335, "attempt id mismatch", failures)
    require(len(ledger) == 1076, "ledger row count mismatch", failures)
    require(len(attempts) == 20336, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave680 CTexture include context"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1076, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20336, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1067, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20336, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave680 CTexture include context" in text, f"Wave680 missing from {path.name}", failures)
        require("ctexture-include-context-wave680" in text, f"Wave680 tag missing from {path.name}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="return non-zero on validation failure")
    args = parser.parse_args()

    failures: list[str] = []
    try:
        check_metadata(failures)
        check_logs(failures)
        check_docs(failures)
        check_state(failures)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{type(exc).__name__}: {exc}")

    status = "PASS" if not failures else "FAIL"
    print("Ghidra CTexture include context Wave680 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
