#!/usr/bin/env python3
"""Validate Wave835 CUnit ApplyDamage read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave835-cunit-apply-damage"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cunit_apply_damage_wave835_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
UNIT_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
UNIT_APPLY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "CUnit__ApplyDamage.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-003658_post_wave835_cunit_apply_damage_verified"
TARGET_ADDR = "0x004f9a90"
TARGET_NAME = "CUnit__ApplyDamage"
TARGET_SIGNATURE = (
    "void __thiscall CUnit__ApplyDamage(void * this, float damage_amount, "
    "void * damage_source, int apply_shields, int mesh_part_index)"
)
NEXT_HEAD = "0x004fa4b0 CUnit__SmoothEulerTowardTargetAndBuildMatrix"
ATTEMPT_ID = 20490

DATA_SLOTS = {
    "0x005dd828", "0x005dfa38", "0x005dfddc", "0x005e002c", "0x005e027c",
    "0x005e0724", "0x005e0980", "0x005e0bd0", "0x005e1080", "0x005e1530",
    "0x005e1c24", "0x005e232c", "0x005e257c", "0x005e2a1c", "0x005e3114",
    "0x005e3374", "0x005e3de0", "0x005e403c", "0x005e4298",
}

CALLSITES = {"0x004037be", "0x00417a16", "0x0048006d", "0x004898b0"}

COMMON_TAGS = {
    "static-reaudit",
    "cunit-apply-damage-wave835",
    "wave835-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "cunit",
    "unit-damage",
    "virtual-damage-handler",
    "shield-life-damage",
    "destructible-segments",
    "message-box-text",
    "unit-health",
    "weakpoint",
    "nexus",
    "death-dispatch",
    "particle-effect",
}

COMMENT_TOKENS = (
    "Wave835 static read-back",
    "important shared CUnit damage/lifetime infrastructure",
    "RET 0x10 at 0x004fa4a7",
    "0x004037be",
    "0x00417a16",
    "0x0048006d",
    "0x004898b0",
    "damage_amount",
    "damage_source",
    "apply_shields",
    "mesh_part_index",
    "s_nexus_00633af4",
    "s_weakpoint_00633ae8",
    "CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold",
    "this+0x100",
    "this+0xf8",
    "CMessageBox",
    "0x00633b6c",
    "0x44d",
)

DECOMPILE_TOKENS = (
    TARGET_SIGNATURE,
    "damage_amount",
    "damage_source",
    "apply_shields",
    "mesh_part_index",
    "CUnit__ResetDamageCooldownTimer",
    "s_nexus_00633af4",
    "s_weakpoint_00633ae8",
    "CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold",
    "CParticleManager__CreateEffect",
    "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance",
)

CORE_ANCHORS = (
    "Wave835 CUnit ApplyDamage",
    "cunit-apply-damage-wave835",
    TARGET_ADDR + " " + TARGET_NAME,
    TARGET_SIGNATURE,
    "RET 0x10",
    "0x004fa4a7",
    "0x004037be",
    "0x00417a16",
    "0x0048006d",
    "0x004898b0",
    "19 DATA",
    "s_nexus_00633af4",
    "s_weakpoint_00633ae8",
    "5657/6098 = 92.77%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "runtime damage behavior proven",
    "runtime shield behavior proven",
    "god mode proven by wave835",
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
        "pre-xrefs.tsv": 23,
        "pre-instructions.tsv": 261,
        "pre-target-deep-instructions.tsv": 901,
        "pre-xref-site-instructions.tsv": 164,
        "pre-data-ref-slots.tsv": 19,
        "pre-decompile/index.tsv": 1,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 23,
        "post-instructions.tsv": 261,
        "post-target-deep-instructions.tsv": 901,
        "post-xref-site-instructions.tsv": 164,
        "post-data-ref-slots.tsv": 19,
        "post-decompile/index.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    row = metadata.get(TARGET_ADDR)
    require(row is not None, "missing post metadata row", failures)
    if row is not None:
        require(row.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, f"target signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "metadata status mismatch", failures)
        comment = row.get("comment", "")
        for token in COMMENT_TOKENS:
            require(token in comment, f"missing comment token: {token}", failures)
        require("low-signal" not in comment.lower(), "comment contains low-signal wording", failures)

    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    tag_row = tags.get(TARGET_ADDR)
    require(tag_row is not None, "missing post tags row", failures)
    if tag_row is not None:
        actual = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual), f"missing tags: {COMMON_TAGS - actual}", failures)
        require(tag_row.get("status") == "OK", "tag status mismatch", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    actual_slots = {normalize_address(row["from_addr"]) for row in xrefs if row.get("ref_type") == "DATA"}
    actual_calls = {normalize_address(row["from_addr"]) for row in xrefs if row.get("ref_type") == "UNCONDITIONAL_CALL"}
    require(DATA_SLOTS == actual_slots, "DATA slot xref set mismatch", failures)
    require(CALLSITES == actual_calls, "callsite xref set mismatch", failures)

    slots = read_tsv(BASE / "post-data-ref-slots.tsv")
    for slot in slots:
        require(normalize_address(slot.get("pointer_addr", "")) == TARGET_ADDR, f"DATA slot pointer mismatch at {slot.get('vtable')}", failures)
        require(slot.get("function_name") == TARGET_NAME, f"DATA slot function mismatch at {slot.get('vtable')}", failures)
        require(slot.get("status") == "OK", f"DATA slot status mismatch at {slot.get('vtable')}", failures)

    deep = read_tsv(BASE / "post-target-deep-instructions.tsv")
    require(
        any(
            normalize_address(row.get("instruction_addr", "")) == "0x004fa4a7"
            and row.get("mnemonic") == "RET"
            and row.get("operands") == "0x10"
            for row in deep
        ),
        "missing RET 0x10 instruction evidence",
        failures,
    )

    call_rows = read_tsv(BASE / "post-xref-site-instructions.tsv")
    for callsite in CALLSITES:
        window = [row for row in call_rows if normalize_address(row.get("target_addr", "")) == callsite]
        require(any(row.get("role") == "TARGET" and row.get("mnemonic") == "CALL" and row.get("operands") == TARGET_ADDR for row in window), f"missing call row for {callsite}", failures)
        push_count = sum(1 for row in window if row.get("role") == "BEFORE" and row.get("mnemonic") == "PUSH" and -8 <= int(row.get("ordinal", "0")) <= -1)
        require(push_count >= 4, f"too few push rows before callsite {callsite}: {push_count}", failures)

    decompile = read_text(BASE / "post-decompile" / "004f9a90_CUnit__ApplyDamage.c")
    for token in DECOMPILE_TOKENS:
        require(token in decompile, f"missing decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 23 rows",
        "post-instructions.log": "Wrote 261 instruction rows",
        "post-target-deep-instructions.log": "Wrote 901 instruction rows",
        "post-xref-site-instructions.log": "Wrote 164 instruction rows",
        "post-data-ref-slots.log": "ExportVtableSlots complete: targets=19 rows=19",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5657",
        "queue-probe.log": "Commentless functions: 441",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave835.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave835_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BAD: readback", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 441, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5657, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5657, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and normalize_address(raw_commentless.get("address", "")) == "0x004fa4b0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CUnit__SmoothEulerTowardTargetAndBuildMatrix", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171838343, "backup byte count mismatch", failures)
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
        UNIT_INDEX,
        UNIT_APPLY_DOC,
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

    unit_text = read_text(UNIT_APPLY_DOC)
    unit_lower = unit_text.lower()
    for token in ("not throwaway tail code", "does not prove runtime damage", "does not prove exact player/god-mode behavior"):
        require(token in unit_lower, f"missing bounded Unit doc token: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-cunit-apply-damage-wave835") == r"py -3 tools\ghidra_cunit_apply_damage_wave835_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave835 CUnit ApplyDamage" for row in ledger_rows), "missing Wave835 ledger row", failures)
    require(any(row.get("task") == "Wave835 CUnit ApplyDamage" and row.get("attempt_id") == ATTEMPT_ID for row in attempts), "missing Wave835 attempt row", failures)


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
        print("Wave835 CUnit ApplyDamage probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave835 CUnit ApplyDamage probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
