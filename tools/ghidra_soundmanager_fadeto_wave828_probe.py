#!/usr/bin/env python3
"""Validate Wave828 SoundManager FadeTo read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave828-soundmanager-fade-sample"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_soundmanager_fadeto_wave828_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
SOUNDMANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SoundManager.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-210153_post_wave828_soundmanager_fadeto_verified"
TARGET = "0x004e1260"
TARGET_NAME = "CSoundManager__FadeTo"
TARGET_SIGNATURE = "void __thiscall CSoundManager__FadeTo(void * this, void * sample, float fade_value, float speed, void * owner)"
NEXT_HEAD = "0x004eb1e0 CGame__ResetRenderStateForWorldRender"

COMMON_TAGS = {
    "static-reaudit",
    "soundmanager-fadeto-wave828",
    "wave828-readback-verified",
    "retail-binary-evidence",
    "source-parity",
    "sound-manager",
    "sound-event-list",
    "fade",
    "name-corrected",
    "signature-hardened",
    "comment-hardened",
}

XREFS = {
    "0x00408d56": "CMonitor__Process",
    "0x00409ad8": "CMonitor__UpdateSoundEventPlaybackForReader",
    "0x00409b0b": "CMonitor__UpdateSoundEventPlaybackForReader",
    "0x00409b3a": "CMonitor__UpdateSoundEventPlaybackForReader",
    "0x0040a6aa": "CBattleEngine__Morph",
    "0x0040a878": "CBattleEngine__Morph",
    "0x0040ebd2": "CMonitor__FlushTrackedList_1D4",
}

CORE_ANCHORS = (
    "Wave828 SoundManager FadeTo",
    "soundmanager-fadeto-wave828",
    "0x004e1260 CSoundManager__FadeTo",
    "CSoundManager::FadeTo",
    "0x004081c0 CMonitor__Process",
    "0x00409950 CMonitor__UpdateSoundEventPlaybackForReader",
    "0x0040a580 CBattleEngine__Morph",
    "0x0040eb50 CMonitor__FlushTrackedList_1D4",
    "5641/6098 = 92.51%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime audio fade behavior proven",
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


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def count_strict_clean(rows: list[dict[str, str]]) -> int:
    return sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-context-metadata.tsv": 16,
        "pre-context-tags.tsv": 16,
        "pre-context-xrefs.tsv": 134,
        "pre-context-instructions.tsv": 592,
        "pre-context-decompile/index.tsv": 16,
        "pre-caller-metadata.tsv": 4,
        "pre-caller-decompile/index.tsv": 4,
        "post-context-metadata.tsv": 16,
        "post-context-tags.tsv": 16,
        "post-context-xrefs.tsv": 134,
        "post-context-instructions.tsv": 592,
        "post-context-decompile/index.tsv": 16,
        "post-caller-decompile/index.tsv": 4,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-context-metadata.tsv")}
    target = metadata.get(TARGET)
    require(target is not None, "missing post metadata target", failures)
    if target is not None:
        require(target.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(target.get("signature") == TARGET_SIGNATURE, "target signature mismatch", failures)
        require(target.get("status") == "OK", "target metadata status mismatch", failures)
        comment = target.get("comment", "")
        for token in (
            "Wave828 static read-back/name/signature correction",
            "CSoundManager::FadeTo",
            "not a CMonitor helper",
            "event+0x0c",
            "event+0x28",
            "event+0x24",
            "runtime audio fade behavior",
            "rebuild parity remain deferred",
        ):
            require(token in comment, f"missing target comment token: {token}", failures)

    tag_rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-context-tags.tsv")}
    tag_row = tag_rows.get(TARGET)
    require(tag_row is not None, "missing target tags", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"target tags missing: {COMMON_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "target tag status mismatch", failures)

    dec_rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-context-decompile" / "index.tsv")}
    require(dec_rows.get(TARGET, {}).get("signature") == TARGET_SIGNATURE, "target decompile signature mismatch", failures)
    decompile_text = read_text(BASE / "post-context-decompile" / "004e1260_CSoundManager__FadeTo.c")
    for token in ("CSoundManager__FadeTo", "piVar1[10]", "piVar1[9]", "0xc", "0x1d"):
        require(token in decompile_text, f"missing decompile token: {token}", failures)

    xref_rows = [
        row
        for row in read_tsv(BASE / "post-context-xrefs.tsv")
        if normalize_address(row.get("target_addr", "")) == TARGET
    ]
    require(len(xref_rows) == 7, "target xref count mismatch", failures)
    xref_by_from = {normalize_address(row["from_addr"]): row for row in xref_rows}
    for from_addr, function_name in XREFS.items():
        row = xref_by_from.get(from_addr)
        require(row is not None, f"missing xref {from_addr}", failures)
        if row is not None:
            require(row.get("target_name") == TARGET_NAME, f"xref target name mismatch at {from_addr}", failures)
            require(row.get("from_function") == function_name, f"xref function mismatch at {from_addr}", failures)
            require(row.get("ref_type") == "UNCONDITIONAL_CALL", f"xref type mismatch at {from_addr}", failures)

    callers = {
        "004081c0_CMonitor__Process.c": 1,
        "00409950_CMonitor__UpdateSoundEventPlaybackForReader.c": 3,
        "0040a580_CBattleEngine__Morph.c": 2,
        "0040eb50_CMonitor__FlushTrackedList_1D4.c": 1,
    }
    for relative, expected_calls in callers.items():
        text = read_text(BASE / "post-caller-decompile" / relative)
        require(text.count("CSoundManager__FadeTo") >= expected_calls, f"caller decompile call count mismatch: {relative}", failures)
        require("&DAT_00896988" in text, f"caller missing manager global: {relative}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply-clean-readback.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-context-metadata.log": "targets=16 found=16 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=16 missing=0",
        "post-context-xrefs.log": "Wrote 134 rows",
        "post-context-instructions.log": "Wrote 592 instruction rows",
        "post-context-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
        "post-caller-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    apply_text = read_text(BASE / "apply.log")
    require("READBACK_OK: 0x004e1260 CSoundManager__FadeTo" in apply_text, "missing apply readback", failures)
    require("Unable to lock due to active transaction" in apply_text, "missing documented first-apply redundant-save issue", failures)
    clean_text = read_text(BASE / "apply-clean-readback.log")
    require("ERROR REPORT SCRIPT ERROR" not in clean_text, "clean readback still has script error", failures)
    require("Unable to lock due to active transaction" not in clean_text, "clean readback still has lock issue", failures)

    quality_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave828.log")
    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave828_queue_probe.log")
    require("total_functions=6098 commented_functions=5641" in quality_log, "missing Wave828 quality export token", failures)
    require("Commentless functions: 457" in queue_log, "missing Wave828 queue probe token", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 457, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = count_strict_clean(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5641, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5641, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004eb1e0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CGame__ResetRenderStateForWorldRender", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171576199 or backup.get("totalBytes") == 171576199.0, "backup byte count mismatch", failures)
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
        SOUNDMANAGER_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-soundmanager-fadeto-wave828")
        == r"py -3 tools\ghidra_soundmanager_fadeto_wave828_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave828 SoundManager FadeTo" for row in ledger_rows), "missing Wave828 ledger row", failures)
    require(
        any(row.get("task") == "Wave828 SoundManager FadeTo" and row.get("attempt_id") == 20483 for row in attempts),
        "missing Wave828 attempt row",
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
        print("Wave828 SoundManager FadeTo probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave828 SoundManager FadeTo probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
