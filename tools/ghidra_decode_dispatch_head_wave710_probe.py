#!/usr/bin/env python3
"""Validate Wave710 decode-dispatch head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave710-decode-dispatch-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_decode_dispatch_head_wave710_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
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
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BASE_TAGS = {
    "static-reaudit",
    "decode-dispatch-head-wave710",
    "wave710-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "decode-dispatch-head",
}

TARGETS = {
    "0x0059aec0": (
        "CTexture__CanUseCompactDecodePath",
        "int __fastcall CTexture__CanUseCompactDecodePath(int unused_ecx, void * decode_state)",
        ("plain RET", "EDX loaded with the decode state", "compact path"),
        BASE_TAGS | {"compact-decode-gate", "fastcall-edx-state", "unused-ecx", "tranche-head"},
    ),
    "0x0059af40": (
        "CTexture__ComputeDecodeBlockGeometry",
        "void __stdcall CTexture__ComputeDecodeBlockGeometry(void * decode_state)",
        ("RET 0x4", "block dimensions", "CTexture__CanUseCompactDecodePath"),
        BASE_TAGS | {"block-geometry", "component-sampling", "ret-0x4"},
    ),
    "0x0059b370": (
        "CTexture__RunDecodeDispatchStage",
        "void __stdcall CTexture__RunDecodeDispatchStage(void * decode_state)",
        ("RET 0x4", "dispatch context at +0x1a8", "callback-context progress"),
        BASE_TAGS | {"dispatch-stage", "callback-progress", "ret-0x4"},
    ),
    "0x0059b4d0": (
        "CTexture__CreateDecodeDispatchContext",
        "void __stdcall CTexture__CreateDecodeDispatchContext(void * decode_state)",
        ("RET 0x4", "0x1c dispatch context", "hidden-register initializer ABI"),
        BASE_TAGS | {"dispatch-context", "allocator-context", "ret-0x4"},
    ),
    "0x0059b920": (
        "CDXTexture__DecodeState_RunPostFrameCallbacks",
        "void __stdcall CDXTexture__DecodeState_RunPostFrameCallbacks(void * decode_state)",
        ("RET 0x4", "observed slots at +0x1c0", "helper hidden-register ABIs"),
        BASE_TAGS | {"post-frame-callbacks", "callback-context", "ret-0x4"},
    ),
    "0x0059b960": (
        "CDXTexture__DecodeState_AdvanceFrame",
        "int __stdcall CDXTexture__DecodeState_AdvanceFrame(void * decode_state)",
        ("RET 0x4", "status return", "terminal flag"),
        BASE_TAGS | {"advance-frame", "ret-0x4", "status-return"},
    ),
    "0x0059ba20": (
        "CDXTexture__DecodeState_ResetCallbackContext",
        "void __stdcall CDXTexture__DecodeState_ResetCallbackContext(void * decode_state)",
        ("RET 0x4", "resets the callback context", "clears +0xa4"),
        BASE_TAGS | {"reset-callback-context", "callback-context", "ret-0x4"},
    ),
    "0x0059ba90": (
        "CDXTexture__DecodeState_CreateCallbackContext",
        "void __stdcall CDXTexture__DecodeState_CreateCallbackContext(void * decode_state)",
        ("RET 0x4", "0x1c callback context", "state words to 0/0/1"),
        BASE_TAGS | {"create-callback-context", "callback-context", "ret-0x4", "tranche-tail"},
    ),
}

DEFERRED_ABI = {
    "0x0059b150": ("CTexture__InitDecodeLookupScratchTables", "in_EAX"),
    "0x0059b1d0": ("CTexture__InitializeDecodePipelineFromHeader", "unaff_ESI"),
    "0x0059b510": ("CDXTexture__ValidateJpegFrameAndBuildScanLayout", "unaff_ESI"),
    "0x0059b6f0": ("CTexture__BuildComponentPlaneLayoutTables", "unaff_ESI"),
    "0x0059b880": ("CTexture__EnsureComponentDecodeScratchBlocks", "unaff_EBX"),
}

DOC_TOKENS = (
    "Wave710 decode dispatch head",
    "decode-dispatch-head-wave710",
    "0x0059aec0 CTexture__CanUseCompactDecodePath",
    "0x0059ba90 CDXTexture__DecodeState_CreateCallbackContext",
    "0x0059bae0 CDXTexture__AllocFromBank_SplitBlock",
    "0x0042f220 CSPtrSet__Clear",
)

OVERCLAIM_TOKENS = (
    "runtime image decode behavior proven",
    "runtime image fidelity proven",
    "decode-state layout proven",
    "callback abi proven",
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


def check_metadata(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-post" / "index.tsv")}

    expected_counts = {
        "pre-candidate-metadata.tsv": 13,
        "pre-candidate-tags.tsv": 13,
        "pre-candidate-xrefs.tsv": 17,
        "pre-candidate-instructions.tsv": 3133,
        "decompile-candidate-pre/index.tsv": 13,
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 12,
        "pre-instructions.tsv": 1928,
        "decompile-pre/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 12,
        "post-instructions.tsv": 1928,
        "decompile-post/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    candidate_index = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")}
    for address, (name, abi_token) in DEFERRED_ABI.items():
        require(address in candidate_index, f"deferred candidate missing from candidate index: {address}", failures)
        require(address not in metadata, f"deferred candidate unexpectedly appears in post metadata: {address}", failures)
        candidate_file = BASE / "decompile-candidate-pre" / f"{address[2:]}_{name}.c"
        require(candidate_file.is_file(), f"deferred candidate decompile missing: {address}", failures)
        if candidate_file.is_file():
            text = read_text(candidate_file)
            require(abi_token in text, f"deferred ABI token missing for {address}: {abi_token}", failures)

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave710 static read-back" in comment, f"missing Wave710 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        decompile_file = BASE / "decompile-post" / f"{address[2:]}_{name}.c"
        require(decompile_file.is_file(), f"missing decompile file for {address}", failures)
        if decompile_file.is_file():
            text = read_text(decompile_file)
            for token in ("param_", "unaff_", "in_stack_", "in_ECX"):
                require(token not in text, f"{token} survived in post decompile for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "export-pre-candidate-metadata.log": "targets=13 found=13 missing=0",
        "export-pre-candidate-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "export-pre-candidate-xrefs.log": "Wrote 17 rows",
        "export-pre-candidate-instructions.log": "Wrote 3133 instruction rows",
        "export-pre-candidate-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "export-pre-metadata.log": "targets=8 found=8 missing=0",
        "export-pre-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "export-pre-xrefs.log": "Wrote 12 rows",
        "export-pre-instructions.log": "Wrote 1928 instruction rows",
        "export-pre-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "export-post-metadata.log": "targets=8 found=8 missing=0",
        "export-post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "export-post-xrefs.log": "Wrote 12 rows",
        "export-post-instructions.log": "Wrote 1928 instruction rows",
        "export-post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("Input file not found" not in text, f"bad input path found in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BADNAME:" not in text and "MISSING:" not in text and "FAIL:" not in text, f"bad/missing marker found in {filename}", failures)

    queue_refresh = read_text(BASE / "export-queue-refresh.log")
    require("total_functions=6098 commented_functions=4125" in queue_refresh, "queue refresh count mismatch", failures)
    require("REPORT: Save succeeded" in queue_refresh, "queue refresh save report missing", failures)
    queue_probe = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave710_queue_probe.log")
    require('"status": "PASS"' in queue_probe or "Status: PASS" in queue_probe, "queue probe did not pass", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 1973, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 210, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    high_signal_head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(high_signal_head.get("address") == "0x0059bae0", f"high-signal head address mismatch: {high_signal_head}", failures)
    require(high_signal_head.get("name") == "CDXTexture__AllocFromBank_SplitBlock", f"high-signal head name mismatch: {high_signal_head}", failures)

    rows = read_tsv(QUALITY_TSV)
    param_re = re.compile(r"\bparam_\d+\b")
    clean = [
        row for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not param_re.search(row.get("signature", ""))
    ]
    require(len(clean) == 4071, f"strict clean proxy mismatch: {len(clean)}", failures)

    commentless = [row for row in rows if not row.get("comment", "").strip()]
    require(bool(commentless), "no commentless rows found", failures)
    if commentless:
        require(normalize_address(commentless[0].get("address", "")) == "0x0042f220", f"raw commentless head mismatch: {commentless[0]}", failures)
        require(commentless[0].get("name") == "CSPtrSet__Clear", f"raw commentless head name mismatch: {commentless[0]}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == "G:\\GhidraBackups\\BEA_20260521-221723_post_wave710_decode_dispatch_head_verified", "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, f"backup file count mismatch: {backup.get('fileCount')}", failures)
    require(int(backup.get("totalBytes", -1)) == 165514119, f"backup byte count mismatch: {backup.get('totalBytes')}", failures)
    require(backup.get("diffCount") == 0, f"backup diff count mismatch: {backup.get('diffCount')}", failures)


def check_docs(failures: list[str]) -> None:
    doc_paths = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in doc_paths:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"overclaim token found in {path.relative_to(ROOT)}: {token}", failures)

    public_note = read_text(PUBLIC_NOTE)
    require("deferred read-only" in public_note, "public note missing deferred language", failures)
    require("0x0059b150 CTexture__InitDecodeLookupScratchTables" in public_note, "public note missing deferred initializer anchor", failures)
    require("0x0059b880 CTexture__EnsureComponentDecodeScratchBlocks" in public_note, "public note missing deferred scratch anchor", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-decode-dispatch-head-wave710")
        == "py -3 tools\\ghidra_decode_dispatch_head_wave710_probe.py --check",
        "missing package script for Wave710 probe",
        failures,
    )


def check_logs_and_state(failures: list[str]) -> None:
    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(ledger_rows[-1].get("task") == "Wave710 decode dispatch head", "latest ledger row is not Wave710", failures)
    require(attempt_rows[-1].get("attempt_id") == 20365, "latest attempt id mismatch", failures)
    require(attempt_rows[-1].get("task") == "Wave710 decode dispatch head", "latest attempt row is not Wave710", failures)
    require(attempt_rows[-1].get("readback") == "verified", "latest attempt readback not verified", failures)
    require("subagents/ghidra-static-reaudit/wave710-decode-dispatch-head" in attempt_rows[-1].get("source", ""), "attempt source missing scratch path", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(counters.get("ledger_rows") == 1106, f"ledger row counter mismatch: {counters.get('ledger_rows')}", failures)
    require(counters.get("attempt_rows") == 20366, f"attempt row counter mismatch: {counters.get('attempt_rows')}", failures)
    require(counters.get("completed") == 1097, f"completed counter mismatch: {counters.get('completed')}", failures)
    require(counters.get("pending") == 9, f"pending counter mismatch: {counters.get('pending')}", failures)
    require(tracking.get("next_attempt_id") == 20366, f"next attempt id mismatch: {tracking.get('next_attempt_id')}", failures)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    try:
        check_metadata(failures)
        check_logs(failures)
        check_queue_and_backup(failures)
        check_docs(failures)
        check_logs_and_state(failures)
    except Exception as exc:  # pragma: no cover - command-line diagnostics
        failures.append(f"unexpected exception: {exc}")

    print("Wave710 decode dispatch head probe")
    if failures:
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Status: PASS")
    print("Verified 8 metadata rows, 8 tag rows, 12 xref rows, 1928 instruction rows, 8 decompile rows, 5 deferred hidden-ABI candidates, queue counts, docs, logs, and backup.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
