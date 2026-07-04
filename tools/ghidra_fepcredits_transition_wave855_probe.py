#!/usr/bin/env python3
"""Validate Wave855 FEPCredits transition read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave855-fepcredits-transition"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_fepcredits_transition_wave855_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEPCREDITS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPCredits.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave855 FEPCredits transition"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-110750_post_wave855_fepcredits_transition_verified"
TARGET = "0x0051a970"
TARGET_NAME = "CFEPCredits__TransitionNotification"
TARGET_SIGNATURE = "void __fastcall CFEPCredits__TransitionNotification(void * this, int from_page)"
NEXT_HEAD = "0x0051aa90 CFEPDirectory__Init"

COMMON_TAGS = {
    "static-reaudit",
    "fepcredits-transition-wave855",
    "wave855-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "frontend",
    "fepcredits",
    "credits-page",
    "transition-notification",
    "vtable-slot",
    "timer-reset",
    "credits-music",
    "completion-flag-clear",
}

COMMENT_TOKENS = (
    "Wave855 static read-back",
    "FE credits-page transition-notification vtable slot 6",
    "0x005db898",
    "0x005db880",
    "PLATFORM__GetSysTimeFloat",
    "0x005d8ba0",
    "CMusic__PlaySelection",
    "DAT_00889a48",
    "this+0x04",
    "this+0x08",
    "RET 0x4",
    "CFEPCredits__Render",
    "CCredits__RenderCredits",
    "CFEPCredits__Process/ButtonPressed",
    "Static retail Ghidra evidence only",
)

CONTEXT_NAMES = {
    "CCredits__BuildDefaultEntries",
    "CCredits__WriteEntry_String",
    "CCredits__WriteEntry_TextId",
    "CCredits__RenderCredits",
    "CFEPCredits__ButtonPressed",
    "CFEPCredits__Process",
    "CFEPCredits__RenderPreCommon",
    "CFEPCredits__Render",
    "CFEPCredits__TransitionNotification",
    "CGame__RollCredits",
}

VTABLE_SLOTS = {
    2: "CFEPCredits__Process",
    3: "CFEPCredits__ButtonPressed",
    4: "CFEPCredits__RenderPreCommon",
    5: "CFEPCredits__Render",
    6: TARGET_NAME,
    7: "SharedVFunc__NoOpOneArg_004014c0",
    8: "CFrontEndPage__DeActiveNotification",
}

CORE_ANCHORS = (
    TASK,
    "fepcredits-transition-wave855",
    f"{TARGET} {TARGET_NAME}",
    "FE credits-page transition-notification vtable slot 6",
    "CFEPCredits__Render",
    "CCredits__RenderCredits",
    NEXT_HEAD,
    "5756/6098 = 94.39%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime frontend behavior proven",
    "exact cfecredits layout proven",
    "exact music-track semantics proven",
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
        "pre-instructions.tsv": 81,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 10,
        "pre-context-decompile/index.tsv": 10,
        "pre-vtable.tsv": 9,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions.tsv": 81,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 10,
        "post-context-decompile/index.tsv": 10,
        "post-vtable.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    row = metadata.get(TARGET)
    require(row is not None, "missing target metadata", failures)
    if row is not None:
        require(row.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, f"target signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "target metadata status mismatch", failures)
        for token in COMMENT_TOKENS:
            require(token in row.get("comment", ""), f"missing comment token: {token}", failures)

    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    tag_row = tags.get(TARGET)
    require(tag_row is not None, "missing target tags", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"tags missing: {COMMON_TAGS - actual_tags}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    require(len(xrefs) == 1, "xref row count mismatch", failures)
    if xrefs:
        xref = xrefs[0]
        require(normalize_address(xref.get("target_addr", "")) == TARGET, "xref target mismatch", failures)
        require(normalize_address(xref.get("from_addr", "")) == "0x005db898", "xref source mismatch", failures)
        require(xref.get("ref_type") == "DATA", "xref type mismatch", failures)

    decompile = read_text(BASE / "post-decompile" / "0051a970_CFEPCredits__TransitionNotification.c")
    for token in (
        "PLATFORM__GetSysTimeFloat",
        "CMusic__PlaySelection",
        "_DAT_005d8ba0",
        "DAT_00889a48",
        "*(float *)((int)this + 4)",
        "*(undefined4 *)((int)this + 8) = 0",
    ):
        require(token in decompile, f"missing decompile token: {token}", failures)

    context_names = {row.get("name", "") for row in read_tsv(BASE / "post-context-metadata.tsv")}
    for name in CONTEXT_NAMES:
        require(name in context_names, f"missing context metadata row: {name}", failures)

    vtable_rows = read_tsv(BASE / "post-vtable.tsv")
    vtable_by_slot = {int(row["slot_index"]): row for row in vtable_rows}
    for slot, name in VTABLE_SLOTS.items():
        slot_row = vtable_by_slot.get(slot)
        require(slot_row is not None, f"missing vtable slot {slot}", failures)
        if slot_row is not None:
            require(slot_row.get("vtable") == "005db880", f"vtable address mismatch at slot {slot}", failures)
            require(slot_row.get("function_name") == name, f"vtable function mismatch at slot {slot}", failures)
    target_slot = vtable_by_slot.get(6)
    if target_slot is not None:
        require(normalize_address(target_slot.get("slot_addr", "")) == "0x005db898", "target slot address mismatch", failures)
        require(normalize_address(target_slot.get("pointer_addr", "")) == TARGET, "target slot pointer mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions.log": "Wrote 81 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=10 found=10 missing=0",
        "post-context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-vtable.log": "targets=1 rows=9",
        "quality-refresh.log": "total_functions=6098 commented_functions=5756",
        "queue-probe.log": "Commentless functions: 342",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave855.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave855_queue_probe.log",
    }
    for relative, token in expected.items():
        text = read_text(log_aliases.get(relative, BASE / relative))
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 342, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue not empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue not empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue not empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5756, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5756, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0051aa90", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFEPDirectory__Init", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172166023, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        FEPCREDITS_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
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
    require(scripts.get("test:ghidra-fepcredits-transition-wave855") == r"py -3 tools\ghidra_fepcredits_transition_wave855_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave855 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20510 for row in attempts), "missing Wave855 attempt row", failures)


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
        print("Wave855 FEPCredits transition probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave855 FEPCredits transition probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
