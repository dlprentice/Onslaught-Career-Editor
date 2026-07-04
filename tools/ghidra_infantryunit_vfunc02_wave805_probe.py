#!/usr/bin/env python3
"""Validate Wave805 InfantryUnit vfunc02 read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave805-infantryunit-vfunc02"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_infantryunit_vfunc02_wave805_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
INFANTRY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Infantry.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-094441_post_wave805_infantryunit_vfunc02_verified"
OLD_NAME = "CInfantryUnit__VFunc_02_00488f60"
NEW_NAME = "CInfantryUnit__VFunc02_ClearParticleLinkAndForward"
SIGNATURE = f"void __fastcall {NEW_NAME}(void * this)"

COMMON_TAGS = {
    "static-reaudit",
    "infantryunit-vfunc02-wave805",
    "wave805-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "infantry-unit",
    "vfunc02",
    "vtable-slot",
    "particle-effect-link",
    "cleanup-forward",
    "signature-hardened",
    "renamed",
    "tranche-head",
}

CORE_ANCHORS = (
    "Wave805 InfantryUnit vfunc02",
    "infantryunit-vfunc02-wave805",
    "0x00488f60 CInfantryUnit__VFunc02_ClearParticleLinkAndForward",
    "0x005e2730",
    "0x005e2734",
    "ParticleEffectLink__SetHandleStateAndClear",
    "CUnit__VFunc02_CleanupWorldLinksAndForward",
    "0x0048ddf0 thunk_DXMemBuffer__Close",
    "5577/6098 = 91.46%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime cleanup order proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "exact source virtual name proven",
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
        "pre-instructions.tsv": 121,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 11,
        "pre-context-instructions.tsv": 451,
        "pre-context-decompile/index.tsv": 11,
        "pre-vtable-slots.tsv": 16,
        "pre-helper-metadata.tsv": 2,
        "pre-helper-decompile/index.tsv": 2,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions.tsv": 121,
        "post-decompile/index.tsv": 1,
        "post-vtable-slots.tsv": 16,
        "post-helper-metadata.tsv": 2,
        "post-helper-decompile/index.tsv": 2,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre = read_tsv(BASE / "pre-metadata.tsv")[0]
    require(pre.get("name") == OLD_NAME, "pre metadata old name mismatch", failures)
    require(pre.get("signature") == f"void {OLD_NAME}(void)", "pre signature mismatch", failures)
    require(not pre.get("comment", "").strip(), "pre target unexpectedly commented", failures)

    row = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(row["address"]) == "0x00488f60", "post address mismatch", failures)
    require(row.get("name") == NEW_NAME, "post name mismatch", failures)
    require(row.get("signature") == SIGNATURE, f"post signature mismatch: {row.get('signature')}", failures)
    require(row.get("status") == "OK", "post metadata status mismatch", failures)
    for token in ("Wave805 static read-back", "0x005e2730", "0x005e2734", "this+0x270", "ParticleEffectLink__SetHandleStateAndClear", "CUnit__VFunc02_CleanupWorldLinksAndForward"):
        require(token in row.get("comment", ""), f"missing comment token: {token}", failures)

    tag_row = read_tsv(BASE / "post-tags.tsv")[0]
    require(tag_row.get("name") == NEW_NAME, "post tag name mismatch", failures)
    actual_tags = set(tag_row.get("tags", "").split(";"))
    require(COMMON_TAGS.issubset(actual_tags), f"missing tags: {COMMON_TAGS - actual_tags}", failures)

    xref = read_tsv(BASE / "post-xrefs.tsv")[0]
    require(normalize_address(xref.get("target_addr", "")) == "0x00488f60", "xref target mismatch", failures)
    require(normalize_address(xref.get("from_addr", "")) == "0x005e2734", "xref from mismatch", failures)
    require(xref.get("ref_type") == "DATA", "xref type mismatch", failures)

    slots = read_tsv(BASE / "post-vtable-slots.tsv")
    slot1 = next((slot for slot in slots if slot.get("slot_index") == "1"), None)
    require(slot1 is not None, "missing vtable slot 1", failures)
    if slot1 is not None:
        require(normalize_address(slot1.get("vtable", "")) == "0x005e2730", "slot vtable mismatch", failures)
        require(normalize_address(slot1.get("slot_addr", "")) == "0x005e2734", "slot addr mismatch", failures)
        require(slot1.get("function_name") == NEW_NAME, "slot function name mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    require("ParticleEffectLink__SetHandleStateAndClear" in helper_names, "missing particle helper metadata", failures)
    require("CUnit__VFunc02_CleanupWorldLinksAndForward" in helper_names, "missing unit vfunc helper metadata", failures)

    decompile = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(decompile.get("name") == NEW_NAME, "post decompile name mismatch", failures)
    require(decompile.get("signature") == SIGNATURE, "post decompile signature mismatch", failures)
    require(decompile.get("status") == "OK", "post decompile status mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions.log": "Wrote 121 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=16",
        "post-helper-metadata.log": "targets=2 found=2 missing=0",
        "post-helper-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5577",
        "queue-probe.log": "Commentless functions: 521",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave805.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave805_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADNAME:", "MISSING:", "FAIL:", "missing=1", "bad=1", "failed=1", "Input file not found"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 521, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    target = next((row for row in rows if normalize_address(row.get("address", "")) == "0x00488f60"), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5577, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5577, "strict clean-signature count mismatch", failures)
    require(target is not None and target.get("name") == NEW_NAME, "quality target name mismatch", failures)
    require(target is not None and target.get("signature") == SIGNATURE, "quality target signature mismatch", failures)
    require(target is not None and target.get("comment", "").strip(), "quality target comment missing", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0048ddf0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "thunk_DXMemBuffer__Close", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171314055 or backup.get("totalBytes") == 171314055.0, "backup byte count mismatch", failures)
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
        INFANTRY_DOC,
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
    require(scripts.get("test:ghidra-infantryunit-vfunc02-wave805") == r"py -3 tools\ghidra_infantryunit_vfunc02_wave805_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave805 InfantryUnit vfunc02" for row in ledger_rows), "missing Wave805 ledger row", failures)
    require(any(row.get("task") == "Wave805 InfantryUnit vfunc02" and row.get("attempt_id") == 20460 for row in attempts), "missing Wave805 attempt row", failures)


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
        print("Wave805 InfantryUnit vfunc02 probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave805 InfantryUnit vfunc02 probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
