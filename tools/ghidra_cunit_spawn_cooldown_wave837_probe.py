#!/usr/bin/env python3
"""Validate Wave837 CUnit spawn-cooldown read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave837-spawner-cooldown"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cunit_spawn_cooldown_wave837_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
SPAWNER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SpawnerThng.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

ADDRESS = "0x004fc3a0"
NAME = "CUnit__SetSpawnCooldownState3"
OLD_NAME = "CSpawnerThng__SetCooldownState3"
SIGNATURE = "void __thiscall CUnit__SetSpawnCooldownState3(void * this, float cooldown_delay)"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-013914_post_wave837_cunit_spawn_cooldown_verified"

COMMON_TAGS = {
    "static-reaudit",
    "cunit-spawn-cooldown-wave837",
    "wave837-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "name-corrected",
    "cunit",
    "spawn-system",
    "spawn-cooldown",
    "spawner-callsite",
    "created-object",
    "state3",
    "global-time",
    "ret-4",
    "owner-corrected",
}

CORE_ANCHORS = (
    "Wave837 CUnit Spawn Cooldown",
    "cunit-spawn-cooldown-wave837",
    ADDRESS,
    NAME,
    OLD_NAME,
    SIGNATURE,
    "0x004e430f",
    "CSpawnerThng__ProcessSpawnWave",
    "0x004fc3b0",
    "0x004fc3ba",
    "DAT_00672fd0 + cooldown_delay",
    "0x004fce40 CUnitAI__CallAttachedNodeVFunc14IfPresent",
    "5659/6098 = 92.80%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime spawn activation/cooldown behavior proven",
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
        "pre-instructions.tsv": 121,
        "pre-target-deep-instructions.tsv": 381,
        "pre-xref-site-instructions.tsv": 69,
        "pre-context-metadata.tsv": 16,
        "pre-context-decompile/index.tsv": 16,
        "pre-decompile/index.tsv": 1,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions.tsv": 121,
        "post-target-deep-instructions.tsv": 381,
        "post-xref-site-instructions.tsv": 69,
        "post-context-metadata.tsv": 16,
        "post-context-decompile/index.tsv": 16,
        "post-decompile/index.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre = read_tsv(BASE / "pre-metadata.tsv")[0]
    require(pre.get("name") == OLD_NAME, "pre old name mismatch", failures)
    require("unused_scale" in pre.get("signature", ""), "pre stale signature missing unused_scale", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(metadata.get("address", "")) == ADDRESS, "post address mismatch", failures)
    require(metadata.get("name") == NAME, "post name mismatch", failures)
    require(metadata.get("signature") == SIGNATURE, "post signature mismatch", failures)
    require(metadata.get("status") == "OK", "post metadata status mismatch", failures)
    for token in (
        "Wave837 static read-back/signature/name correction",
        "0x004e430f",
        "CWorldPhysicsManager__CreateThingByType",
        "vfunc +0x24",
        "RET 0x4",
        "0x004fc3ba",
        "FADD [ESP+0x4]",
        "0x004fc3b0",
        OLD_NAME,
        "this+0x168",
        "DAT_00672fd0 + cooldown_delay",
        "this+0x16c",
        "runtime spawn activation/cooldown behavior",
    ):
        require(token in metadata.get("comment", ""), f"missing metadata comment token: {token}", failures)

    tags = set(read_tsv(BASE / "post-tags.tsv")[0].get("tags", "").split(";"))
    require(COMMON_TAGS.issubset(tags), f"missing tags: {COMMON_TAGS - tags}", failures)

    xref = read_tsv(BASE / "post-xrefs.tsv")[0]
    require(normalize_address(xref.get("target_addr", "")) == ADDRESS, "xref target mismatch", failures)
    require(normalize_address(xref.get("from_addr", "")) == "0x004e430f", "xref from mismatch", failures)
    require(xref.get("from_function") == "CSpawnerThng__ProcessSpawnWave", "xref function mismatch", failures)
    require(xref.get("ref_type") == "UNCONDITIONAL_CALL", "xref type mismatch", failures)

    decompile = read_text(BASE / "post-decompile" / "004fc3a0_CUnit__SetSpawnCooldownState3.c")
    for token in (
        SIGNATURE,
        "*(undefined4 *)((int)this + 0x168) = 3",
        "*(float *)((int)this + 0x16c) = DAT_00672fd0 + cooldown_delay",
    ):
        require(token in decompile, f"missing decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions.log": "Wrote 121 instruction rows",
        "post-target-deep-instructions.log": "Wrote 381 instruction rows",
        "post-xref-site-instructions.log": "Wrote 69 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=16 found=16 missing=0",
        "post-context-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5659",
        "queue-probe.log": "Commentless functions: 439",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave837.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave837_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BAD:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 439, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5659, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5659, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004fce40", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CUnitAI__CallAttachedNodeVFunc14IfPresent", "raw commentless head name mismatch", failures)

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
        UNIT_DOC,
        SPAWNER_DOC,
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
        scripts.get("test:ghidra-cunit-spawn-cooldown-wave837")
        == r"py -3 tools\ghidra_cunit_spawn_cooldown_wave837_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave837 CUnit Spawn Cooldown" for row in ledger_rows), "missing Wave837 ledger row", failures)
    require(any(row.get("task") == "Wave837 CUnit Spawn Cooldown" and row.get("attempt_id") == 20492 for row in attempts), "missing Wave837 attempt row", failures)


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
        print("Wave837 CUnit spawn-cooldown probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave837 CUnit spawn-cooldown probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
