#!/usr/bin/env python3
"""Validate Wave818 message voice pump read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave818-message-voice-pump"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_message_voice_pump_wave818_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
SOUNDMANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SoundManager.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-161634_post_wave818_message_voice_pump_verified"
TARGET_ADDRESS = "0x004b7d90"
TARGET_NAME = "CGame__PumpBinkVoiceSampleQueue"
TARGET_SIGNATURE = "void __thiscall CGame__PumpBinkVoiceSampleQueue(void * this)"
NEXT_HEAD = "0x004bc2d0 CWorld__ClearDynamicOccupancySet"

COMMON_TAGS = {
    "static-reaudit",
    "message-voice-pump-wave818",
    "wave818-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

COMMENT_TOKENS = (
    "Wave818 static read-back/signature hardening",
    "CGame__Update",
    "0x0046ea77",
    "DAT_008a9ac4",
    "DAT_008a9ac0",
    "DAT_00704e74",
    "CBinkOpenThread__IsRunning",
    "CPCSoundManager__CreateSampleFromData",
    "CSoundManager__PlaySample",
)

HELPER_NAMES = {
    "CBinkOpenThread__IsRunning",
    "CBinkOpenThread__Lock",
    "CBinkOpenThread__Unlock",
    "CPCSoundManager__CreateSampleFromData",
    "CSoundManager__PlaySample",
    "FatalError__ExitWithLocalizedPrefix_A",
    "CGenericActiveReader__SetReader",
}

CORE_ANCHORS = (
    "Wave818 message voice pump",
    "message-voice-pump-wave818",
    "0x004b7d90 CGame__PumpBinkVoiceSampleQueue",
    TARGET_SIGNATURE,
    "0x0046ea77",
    "DAT_008073d0",
    "DAT_0080738c",
    "DAT_00704e74",
    "CBinkOpenThread__IsRunning",
    "CPCSoundManager__CreateSampleFromData",
    "CSoundManager__PlaySample",
    "5606/6098 = 91.93%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime bink behavior proven",
    "runtime voice playback behavior proven",
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


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 1,
        "pre-instructions.tsv": 69,
        "pre-callsite-instructions.tsv": 56,
        "pre-helper-metadata.tsv": 7,
        "pre-decompile/index.tsv": 1,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions.tsv": 69,
        "post-callsite-instructions.tsv": 56,
        "post-helper-metadata.tsv": 7,
        "post-decompile/index.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}
    instructions = read_tsv(BASE / "post-instructions.tsv")
    helpers = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}

    row = metadata.get(TARGET_ADDRESS)
    require(row is not None, "missing target metadata", failures)
    if row:
        require(row.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, f"target signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "target metadata status mismatch", failures)
        for token in COMMENT_TOKENS:
            require(token in row.get("comment", ""), f"missing comment token: {token}", failures)

    tag_row = tags.get(TARGET_ADDRESS)
    require(tag_row is not None, "missing target tags", failures)
    if tag_row:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"tags missing: {COMMON_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "target tag status mismatch", failures)

    dec = decompile.get(TARGET_ADDRESS)
    require(dec is not None, "missing target decompile index", failures)
    if dec:
        require(dec.get("signature") == TARGET_SIGNATURE, f"decompile signature mismatch: {dec.get('signature')}", failures)
        require(dec.get("status") == "OK", "decompile status mismatch", failures)

    xref = xrefs.get(TARGET_ADDRESS)
    require(xref is not None, "missing target xref", failures)
    if xref:
        require(normalize_address(xref.get("from_addr", "")) == "0x0046ea77", "xref caller mismatch", failures)
        require(xref.get("from_function") == "CGame__Update", "xref caller function mismatch", failures)
        require(xref.get("ref_type") == "UNCONDITIONAL_CALL", "xref type mismatch", failures)

    require(instructions[-1].get("instruction_addr") == "0x004b7e9a", "target instruction tail mismatch", failures)
    require(instructions[-1].get("mnemonic") == "RET", "target instruction tail mnemonic mismatch", failures)
    require({row.get("function_entry") for row in instructions} == {TARGET_ADDRESS}, "target instructions include another function", failures)
    require(HELPER_NAMES.issubset(helpers), f"missing helper metadata: {HELPER_NAMES - helpers}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions.log": "Wrote 69 instruction rows",
        "post-callsite-instructions.log": "Wrote 56 instruction rows",
        "post-helper-metadata.log": "targets=7 found=7 missing=0",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5606",
        "queue-probe.log": "Commentless functions: 492",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave818.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave818_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save success", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 492, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5606, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5606, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004bc2d0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CWorld__ClearDynamicOccupancySet", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171379591 or backup.get("totalBytes") == 171379591.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        GAME_DOC,
        SOUNDMANAGER_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-message-voice-pump-wave818") == r"py -3 tools\ghidra_message_voice_pump_wave818_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave818 message voice pump" for row in ledger_rows), "missing Wave818 ledger row", failures)
    require(
        any(row.get("task") == "Wave818 message voice pump" and row.get("attempt_id") == 20473 for row in attempts),
        "missing Wave818 attempt row",
        failures,
    )


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
        print("Wave818 message voice pump probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave818 message voice pump probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
