#!/usr/bin/env python3
"""Validate Wave693 CDXTexture parser-context diagnostic read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave693-cdxtexture-parser-context-diagnostics"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_parser_context_diagnostics_wave693_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
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

SIGNATURE_TAGS = {
    "static-reaudit",
    "cdxtexture-parser-context-diagnostics-wave693",
    "wave693-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

COMMENT_ONLY_TAGS = {
    "static-reaudit",
    "cdxtexture-parser-context-diagnostics-wave693",
    "wave693-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
}

TARGETS = {
    "0x00592b00": (
        "CFastVB__ParserContext_Shutdown",
        "void __stdcall CFastVB__ParserContext_Shutdown(void * parser_context)",
        ("parser-context owned object", "CRT__CExit(1)", "callback-table ABI"),
        SIGNATURE_TAGS | {"parser-context", "shutdown", "callback-table", "owned-object-release", "tranche-head"},
    ),
    "0x00592c50": (
        "CFastVB__ParserContext_Init",
        "void __stdcall CFastVB__ParserContext_Init(void * parser_context)",
        ("callback slots", "bogus-message-code", "diagnostic id 0x7b"),
        SIGNATURE_TAGS | {"parser-context", "init", "callback-table", "diagnostic-default", "bogus-message-code"},
    ),
    "0x00592ca0": (
        "CDXTexture__FormatChunkTagForDiagnostics",
        "void __thiscall CDXTexture__FormatChunkTagForDiagnostics(void * this, int param_1, int param_2, void * param_3)",
        ("PNG chunk tag", "bracketed uppercase hex", "Signature intentionally left unchanged"),
        COMMENT_ONLY_TAGS | {"png", "chunk-tag", "diagnostic-format", "hex-escape", "stack-message"},
    ),
    "0x00592d29": (
        "CTexture__SetDecodeContextTriplet",
        "void __stdcall CTexture__SetDecodeContextTriplet(void * decode_context, void * callback_context, void * error_callback, void * warning_callback)",
        ("callback_context at +0x48", "error_callback at +0x40", "warning_callback at +0x44"),
        SIGNATURE_TAGS | {"decode-context", "callback-triplet", "error-callback", "warning-callback"},
    ),
    "0x00592d45": (
        "CDXTexture__ThrowDecodeError",
        "void __stdcall CDXTexture__ThrowDecodeError(void * decode_context, int message_or_code)",
        ("error callback at +0x40", "_longjmp(decode_context, 1)", "non-return contract"),
        SIGNATURE_TAGS | {"decode-context", "error-callback", "longjmp", "decode-error"},
    ),
    "0x00592d63": (
        "CDXTexture__ReportDecodeWarning",
        "void __stdcall CDXTexture__ReportDecodeWarning(void * decode_context, int message_or_code)",
        ("warning callback at +0x44", "without a longjmp", "warning policy"),
        SIGNATURE_TAGS | {"decode-context", "warning-callback", "decode-warning"},
    ),
    "0x00592d7a": (
        "CDXTexture__LogChunkTagDiagnostic",
        "void __stdcall CDXTexture__LogChunkTagDiagnostic(void * png_decode_state, void * optional_message_text)",
        ("stack diagnostic string", "CDXTexture__FormatChunkTagForDiagnostics", "CDXTexture__ThrowDecodeError"),
        SIGNATURE_TAGS | {"png", "chunk-tag", "diagnostic-format", "decode-error", "stack-message"},
    ),
    "0x00592d9e": (
        "CDXTexture__WarnPngChunkWithFormattedTag",
        "void __stdcall CDXTexture__WarnPngChunkWithFormattedTag(void * png_decode_state, void * optional_message_text)",
        ("stack diagnostic string", "CDXTexture__FormatChunkTagForDiagnostics", "CDXTexture__ReportDecodeWarning"),
        SIGNATURE_TAGS | {"png", "chunk-tag", "diagnostic-format", "decode-warning", "stack-message", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave693 CDXTexture parser-context diagnostics",
    "cdxtexture-parser-context-diagnostics-wave693",
    "0x00592b00 CFastVB__ParserContext_Shutdown",
    "0x00592d9e CDXTexture__WarnPngChunkWithFormattedTag",
    "0x00592dc2 CDXTexture__CreatePngDecodeContext",
)

OVERCLAIM_TOKENS = (
    "runtime png decode fidelity proven",
    "runtime jpeg decode fidelity proven",
    "parser-context layout proven",
    "callback-table abi proven",
    "diagnostic table ownership proven",
    "output-buffer capacity proven",
    "chunk-state layout proven",
    "callback prototypes proven",
    "payload type proven",
    "non-return contract proven",
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
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 65, "post xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 296, "post instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata.tsv")) == 8, "pre metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags.tsv")) == 8, "pre tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs.tsv")) == 65, "pre xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions.tsv")) == 296, "pre instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-pre" / "index.tsv")) == 8, "pre decompile row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata-candidate.tsv")) == 14, "candidate metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags-candidate.tsv")) == 14, "candidate tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs-candidate.tsv")) == 71, "candidate xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-candidate.tsv")) == 518, "candidate instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")) == 14, "candidate decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave693 static read-back" in comment, f"missing Wave693 comment at {address}", failures)
        require("Static metadata only" in comment or "Signature intentionally left unchanged" in comment, f"missing uncertainty clause at {address}", failures)
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
    expected = {
        "apply-wave693-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=1 missing=0 bad=0",
        "apply-wave693-apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=1 missing=0 bad=0",
        "apply-wave693-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-instructions.log": "Wrote 296 instruction rows",
        "post-xrefs.log": "Wrote 65 rows",
        "pre-metadata.log": "targets=8 found=8 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "pre-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "pre-instructions.log": "Wrote 296 instruction rows",
        "pre-xrefs.log": "Wrote 65 rows",
        "pre-metadata-candidate.log": "targets=14 found=14 missing=0",
        "pre-tags-candidate.log": "ExportFunctionTagsByAddress complete: rows=14 missing=0",
        "pre-decompile-candidate.log": "targets=14 dumped=14 missing=0 failed=0",
        "pre-instructions-candidate.log": "Wrote 518 instruction rows",
        "pre-xrefs-candidate.log": "Wrote 71 rows",
        "queue-refresh.log": "total_functions=6098 commented_functions=3973",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("Input file not found" not in text, f"bad input path found in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 2125, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 353, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x00592dc2", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CDXTexture__CreatePngDecodeContext", f"next head name mismatch: {head}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup_path") == "[maintainer-local-ghidra-backup-root]/BEA_20260521-135916_post_wave693_cdxtexture_parser_context_diagnostics_verified", "backup path mismatch", failures)
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(backup.get("total_bytes")) == 164957063, f"backup bytes mismatch: {backup}", failures)
    require(backup.get("diff_count") == 0, f"backup diff mismatch: {backup}", failures)


def check_docs(failures: list[str]) -> None:
    for path in (
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        FASTVB_DOC,
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
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path.relative_to(ROOT)} contains overclaim token {token}", failures)

    package = json.loads(read_text(PACKAGE_JSON))
    require(
        package.get("scripts", {}).get("test:ghidra-cdxtexture-parser-context-diagnostics-wave693")
        == "py -3 tools\\ghidra_cdxtexture_parser_context_diagnostics_wave693_probe.py --check",
        "package script missing/mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave693 CDXTexture parser-context diagnostics" for row in ledger_rows), "ledger missing Wave693", failures)
    require(any(row.get("task") == "Wave693 CDXTexture parser-context diagnostics" for row in attempt_rows), "attempt log missing Wave693", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20349, f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    require(any("Wave693 CDXTexture parser-context diagnostics" in note for note in tracking.get("notes", [])), "tracking notes missing Wave693", failures)


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
        print("Wave693 CDXTexture parser-context diagnostics probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave693 CDXTexture parser-context diagnostics probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
