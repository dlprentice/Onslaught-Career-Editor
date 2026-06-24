#!/usr/bin/env python3
"""Validate Wave681 CTexture directive-control read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave681-ctexture-directive-control"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctexture_directive_control_wave681_2026-05-21.md"
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
    "ctexture-directive-control-wave681",
    "wave681-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

TARGETS = {
    "0x00589bd6": (
        "CTexture__ReportDirectiveParseError",
        "void __cdecl CTexture__ReportDirectiveParseError(void * directive_parser_context, char * diagnostic_format, ...)",
        ("diagnostic helper", "cdecl varargs", "error flag"),
        BASE_TAGS | {"directive-parser-context", "diagnostic-report", "varargs", "preprocessor-directive", "error-state"},
    ),
    "0x00589c82": (
        "CTexture__SetCurrentSourceLocation",
        "int __thiscall CTexture__SetCurrentSourceLocation(void * this, int line_or_token_position, int source_location_value, int unused_context)",
        ("source-location fields", "this+0x54", "end-of-line"),
        BASE_TAGS | {"directive-parser-context", "source-location", "diagnostic-context", "preprocessor-directive"},
    ),
    "0x00589cab": (
        "CTexture__HandleDirective_Include",
        "int __fastcall CTexture__HandleDirective_Include(void * directive_parser_context)",
        ("#include handler", "0x70-byte include context", "parser context +0x50"),
        BASE_TAGS | {"directive-parser-context", "include-directive", "include-source", "preprocessor-directive", "allocation"},
    ),
    "0x00589e73": (
        "CTexture__HandleDirective_Error",
        "int __fastcall CTexture__HandleDirective_Error(void * directive_parser_context)",
        ("#error handler", "logical line", "parser error/status flags"),
        BASE_TAGS | {"directive-parser-context", "error-directive", "diagnostic-report", "preprocessor-directive", "error-state"},
    ),
    "0x00589f49": (
        "CTexture__PushConditionalFrame",
        "int __thiscall CTexture__PushConditionalFrame(void * this, int condition_value, void * unused_context)",
        ("conditional frame", "active include-context +0x38", "this+0x3c"),
        BASE_TAGS | {"directive-parser-context", "conditional-frame", "if-directive", "preprocessor-directive", "allocation"},
    ),
    "0x00589fa1": (
        "CTexture__HandleDirective_Elif",
        "int __thiscall CTexture__HandleDirective_Elif(void * this, int condition_value, int unused_context)",
        ("#elif handler", "#else", "branch-seen state"),
        BASE_TAGS | {"directive-parser-context", "elif-directive", "conditional-frame", "preprocessor-directive", "error-state"},
    ),
    "0x0058a014": (
        "CTexture__HandleDirective_Else",
        "int __fastcall CTexture__HandleDirective_Else(void * directive_parser_context)",
        ("#else handler", "duplicate-else", "active parent"),
        BASE_TAGS | {"directive-parser-context", "else-directive", "conditional-frame", "preprocessor-directive", "error-state"},
    ),
    "0x0058a076": (
        "CTexture__HandleDirective_Endif",
        "int __fastcall CTexture__HandleDirective_Endif(void * directive_parser_context)",
        ("#endif handler", "restores parser activity", "destroys it"),
        BASE_TAGS | {"directive-parser-context", "endif-directive", "conditional-frame", "preprocessor-directive", "recursive-cleanup"},
    ),
    "0x0058a0c6": (
        "CTexture__HandlePragma_PackMatrix",
        "int __fastcall CTexture__HandlePragma_PackMatrix(void * directive_parser_context)",
        ("#pragma pack_matrix", "+0x24", "+0x28"),
        BASE_TAGS | {"directive-parser-context", "pragma-pack-matrix", "pragma-directive", "preprocessor-directive", "parser-state"},
    ),
    "0x0058a1e3": (
        "CTexture__HandlePragma_Warning",
        "int __fastcall CTexture__HandlePragma_Warning(void * directive_parser_context)",
        ("#pragma warning", "CDXTexture__SetKeyEntryModeFlags", "temporary arrays"),
        BASE_TAGS | {"directive-parser-context", "pragma-warning", "warning-control", "pragma-directive", "preprocessor-directive"},
    ),
}

DOC_TOKENS = (
    "Wave681 CTexture directive control",
    "ctexture-directive-control-wave681",
    "0x00589bd6 CTexture__ReportDirectiveParseError",
    "0x0058a1e3 CTexture__HandlePragma_Warning",
    "0x0058a578 CTexture__GetSymbolNameLength",
)

OVERCLAIM_TOKENS = (
    "runtime preprocessor behavior proven",
    "exact conditional-frame layout proven",
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
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 14, "xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 370, "instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata.tsv")) == 10, "pre metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags.tsv")) == 10, "pre tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs.tsv")) == 14, "pre xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions.tsv")) == 370, "pre instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-pre" / "index.tsv")) == 10, "pre decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave681 static read-back" in comment, f"missing Wave681 comment at {address}", failures)
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
        "apply-wave681-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 varargs=0 missing=0 bad=0",
        "apply-wave681-apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 varargs=1 missing=0 bad=0",
        "apply-wave681-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-instructions.log": "targets=10 missing=0",
        "post-xrefs.log": "Wrote 14 rows",
        "pre-metadata.log": "targets=10 found=10 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "pre-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "pre-instructions.log": "targets=10 missing=0",
        "pre-xrefs.log": "Wrote 14 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)
    require("Wrote 370 instruction rows" in read_text(BASE / "post-instructions.log"), "post instruction row count mismatch", failures)
    require("Wrote 370 instruction rows" in read_text(BASE / "pre-instructions.log"), "pre instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-ctexture-directive-control-wave681" in package.get("scripts", {}), "package script missing", failures)
    require((ROOT / "tools" / "ApplyCTextureDirectiveControlWave681.java").is_file(), "apply script missing", failures)

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
        require("Wave681 CTexture directive control" in text, f"Wave681 missing from {path.relative_to(ROOT)}", failures)
        require("ctexture-directive-control-wave681" in text, f"Wave681 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("totalBytes", 0))) == 164465543, "backup totalBytes mismatch", failures)
    require("post_wave681_ctexture_directive_control_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2229, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1216, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 452, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x0058a578", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__GetSymbolNameLength", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave681 CTexture directive control", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave681 CTexture directive control", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20336, "attempt id mismatch", failures)
    require(len(ledger) == 1077, "ledger row count mismatch", failures)
    require(len(attempts) == 20337, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave681 CTexture directive control"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1077, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20337, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1068, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20337, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave681 CTexture directive control" in text, f"Wave681 missing from {path.name}", failures)
        require("ctexture-directive-control-wave681" in text, f"Wave681 tag missing from {path.name}", failures)


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
    print("Ghidra CTexture directive control Wave681 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
