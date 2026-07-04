#!/usr/bin/env python3
"""Validate Wave864 script-command-registry read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave864-script-command-registry"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_script_command_registry_wave864_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave864 script command registry"
ADDRESS = "0x0052ff30"
NAME = "ScriptCommandRegistry__InitBuiltins"
SIGNATURE = "void __cdecl ScriptCommandRegistry__InitBuiltins(void)"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-153044_post_wave864_script_command_registry_verified"
NEXT_HEAD = "0x0053df40 CDXEngine__RenderTexturedBeamQuad"
STRICT_PROXY = "5810/6105 = 95.17%"

COMMON_TAGS = {
    "static-reaudit",
    "script-command-registry-wave864",
    "wave864-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "important-connective-infrastructure",
    "mission-script",
    "command-registry",
    "iscript",
    "registry-initializer",
}

COMMENT_TOKENS = (
    "Wave864 static read-back",
    "144 contiguous 0x40-byte command descriptor records",
    "0x0064ce50 through 0x0064f210",
    "s_FollowWaypointWait_0064fa14",
    "s_IsOverWater_0064f234",
    "IScript__ScheduleEvent",
    "IScript__Create3PointPanCamera",
    "IScript__SetGoodieState",
    "SetStealth",
)

CORE_ANCHORS = (
    TASK,
    "script-command-registry-wave864",
    "0x0052ff30 ScriptCommandRegistry__InitBuiltins",
    "void __cdecl ScriptCommandRegistry__InitBuiltins(void)",
    "144 contiguous 0x40-byte command descriptor records",
    "s_FollowWaypointWait_0064fa14",
    "s_IsOverWater_0064f234",
    "IScript__ScheduleEvent",
    "IScript__SetSlotSave",
    "SetStealth",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime missionscript dispatch proven",
    "runtime script behavior proven",
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
        "pre-instructions.tsv": 2456,
        "pre-decompile/index.tsv": 1,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions.tsv": 2456,
        "post-decompile/index.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {(normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row["ref_type"]) for row in read_tsv(BASE / "post-xrefs.tsv")}
    instructions = read_tsv(BASE / "post-instructions.tsv")

    row = metadata.get(ADDRESS)
    require(row is not None, f"missing metadata for {ADDRESS}", failures)
    if row is not None:
        require(row.get("name") == NAME, "name mismatch", failures)
        require(row.get("signature") == SIGNATURE, f"signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "metadata status mismatch", failures)
        for token in COMMENT_TOKENS:
            require(contains_token(row.get("comment", ""), token), f"missing comment token: {token}", failures)

    tag_row = tags.get(ADDRESS)
    require(tag_row is not None, f"missing tags for {ADDRESS}", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"tags missing: {COMMON_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "tag status mismatch", failures)

    dec = decompile.get(ADDRESS)
    require(dec is not None, "missing decompile index row", failures)
    if dec is not None:
        require(dec.get("signature") == SIGNATURE, f"decompile signature mismatch: {dec.get('signature')}", failures)
        require(dec.get("status") == "OK", "decompile status mismatch", failures)

    require((ADDRESS, "0x0052ff20", "UNCONDITIONAL_CALL") in xrefs, "missing adjacent xref row", failures)
    require(instructions[0].get("instruction_addr") == ADDRESS, "first function-body instruction mismatch", failures)
    require(instructions[-1].get("instruction_addr") == "0x005333a4", "last function-body instruction mismatch", failures)
    require(instructions[-1].get("mnemonic") == "RET", "function-body export should end at RET", failures)

    decompile_text = read_text(BASE / "post-decompile" / "0052ff30_ScriptCommandRegistry__InitBuiltins.c")
    for token in ("s_FollowWaypointWait_0064fa14", "s_IsOverWater_0064f234", "IScript__SetSlotSave", "SetStealth"):
        require(token in decompile_text, f"missing decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions.log": "Wrote 2456 function-body instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6105 commented_functions=5810",
        "queue-probe.log": "Commentless functions: 295",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave864.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave864_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "READBACK_BAD", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require(read_text(BASE / "apply.log").count("READBACK_OK:") == 1, "apply readback count mismatch", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6105, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 295, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name in ("commentlessHighSignal", "signature", "nameConfidence"):
        require(queue["priorityQueues"][name] == [], f"{name} queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6105, "quality TSV row count mismatch", failures)
    require(commented == 5810, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5810, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0053df40", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CDXEngine__RenderTexturedBeamQuad", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172264327 or backup.get("totalBytes") == 172264327.0, "backup byte count mismatch", failures)
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
        ISCRIPT_DOC,
        ENGINE_DOC,
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
    require(scripts.get("test:ghidra-script-command-registry-wave864") == r"py -3 tools\ghidra_script_command_registry_wave864_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave864 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20519 for row in attempts), "missing Wave864 attempt row", failures)


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
        print("Wave864 script-command-registry probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave864 script-command-registry probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
