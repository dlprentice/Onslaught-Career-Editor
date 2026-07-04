#!/usr/bin/env python3
"""Validate Wave1019 PhysicsScript manager lifecycle read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1019-physics-script-manager-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_physics_script_manager_lifecycle_review_wave1019_2026-05-31.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1019_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
CPHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScript.cpp.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-211749_post_wave1019_physics_script_manager_lifecycle_review_verified"

TARGETS = {
    "0x0042e880": ("CPhysicsScript__Create", "void __cdecl CPhysicsScript__Create(void)"),
    "0x0042e8f0": ("CPhysicsScript__Destroy", "void __cdecl CPhysicsScript__Destroy(void)"),
    "0x0042e950": ("CPhysicsScript__Load", "bool __cdecl CPhysicsScript__Load(void * memBuffer)"),
    "0x0042ea60": ("CPhysicsScript__Update", "void __cdecl CPhysicsScript__Update(void)"),
    "0x0042eb90": ("CPhysicsScript__CreateStatement", "void * __cdecl CPhysicsScript__CreateStatement(int statementType)"),
}

COMMENT_TOKENS = {
    "0x0042e880": ("allocates 0x10", "g_pPhysicsScript", "runtime physics-script behavior"),
    "0x0042e8f0": ("statement list", "vtable slot 0", "g_pPhysicsScript"),
    "0x0042e950": ("0x12", "CreateStatement", "slot +0xc", "skips bytes"),
    "0x0042ea60": ("statement list", "slot +0x4", "Null-singleton"),
    "0x0042eb90": ("1..9", "0x110", "0x11..0x19", "statement-specific vtables"),
}

CONTEXT_TARGETS = {
    "0x0042f570": "CPhysicsScriptStatement__dtor",
    "0x0042f2b0": "CUnitStatement__LoadFromMemBuffer",
    "0x00430210": "CRoundStatement__LoadFromMemBuffer",
    "0x004306e0": "CSpawnerStatement__LoadFromMemBuffer",
    "0x00431a10": "CPhysicsHazardValueList__LoadFromMemBuffer",
    "0x00430510": "CSpawnerData__CreateAndRegisterByName",
    "0x0043e630": "CFlexArray__SkipBytesFromMemBuffer",
    "0x0043abd0": "CExplosionBasedOn__ApplyToExplosionByName",
}

DOC_TOKENS = (
    "Wave1019",
    "physics-script-manager-lifecycle-review-wave1019",
    "0x0042e880 CPhysicsScript__Create",
    "0x0042e8f0 CPhysicsScript__Destroy",
    "0x0042e950 CPhysicsScript__Load",
    "0x0042ea60 CPhysicsScript__Update",
    "0x0042eb90 CPhysicsScript__CreateStatement",
    "523/1408 = 37.14%",
    "752/1493 = 50.37%",
    "452/500 = 90.40%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime physics-script behavior proven",
    "runtime physics behavior proven",
    "exact statement layout proven",
    "exact source-body identity proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def rows_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(field, "")): row for row in rows}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 5,
        "tags.tsv": 5,
        "xrefs.tsv": 5,
        "instructions.tsv": 321,
        "decompile/index.tsv": 5,
        "context-metadata.tsv": 8,
        "context-xrefs.tsv": 19,
        "context-instructions.tsv": 776,
        "context-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "decompile" / "index.tsv"), "address")
    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            require("Signature/comment/tag hardening" in row.get("comment", ""), f"missing Wave330 comment anchor {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            for token in ("static-reaudit", "physics-script", "physics-script-wave330", "retail-binary-evidence", "signature-hardened"):
                require(token in actual_tags, f"missing tag {address}: {token}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    context = rows_by(read_tsv(BASE / "context-metadata.tsv"), "address")
    context_decompile = rows_by(read_tsv(BASE / "context-decompile" / "index.tsv"), "address")
    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}: {row.get('name')}", failures)
            require(row.get("status") == "OK", f"context status mismatch {address}", failures)
        dec = context_decompile.get(address)
        require(dec is not None, f"missing context decompile {address}", failures)
        if dec:
            require(dec.get("status") == "OK", f"context decompile status mismatch {address}", failures)

    xref_text = read_text(BASE / "xrefs.tsv") + "\n" + read_text(BASE / "context-xrefs.tsv")
    for token in (
        "CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData",
        "0042e9b0",
        "0042e9f7",
        "CPhysicsScript__Load",
        "0043e630",
        "CFlexArray__SkipBytesFromMemBuffer",
        "005d9884",
        "005d9848",
        "005d9834",
        "DATA",
    ):
        require(token in xref_text, f"missing xref token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "metadata.log": "targets=5 found=5 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "xrefs.log": "Wrote 5 rows",
        "instructions.log": "Wrote 321 function-body instruction rows",
        "decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "context-metadata.log": "targets=8 found=8 missing=0",
        "context-xrefs.log": "Wrote 19 rows",
        "context-instructions.log": "Wrote 776 function-body instruction rows",
        "context-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173968263, 173968263.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    quality_rows = rows_by(read_tsv(QUALITY_TSV), "address")
    for address, (name, signature) in TARGETS.items():
        row = quality_rows.get(address)
        require(row is not None, f"missing quality row {address}", failures)
        if row:
            require(row.get("name") == name, f"quality name mismatch {address}", failures)
            require(row.get("signature") == signature, f"quality signature mismatch {address}", failures)
            require(row.get("comment", "").strip(), f"quality comment missing {address}", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        CPHYSICS_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-physics-script-manager-lifecycle-review-wave1019")
        == r"py -3 tools\ghidra_physics_script_manager_lifecycle_review_wave1019_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1019-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1019 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1019 PhysicsScript manager lifecycle review" for row in ledger), "missing Wave1019 ledger row", failures)
    require(
        any(row.get("task") == "Wave1019 PhysicsScript manager lifecycle review" and row.get("attempt_id") == 20601 for row in attempts),
        "missing Wave1019 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue(failures)
    check_docs(failures)

    if failures:
        print("Wave1019 PhysicsScript manager lifecycle review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1019 PhysicsScript manager lifecycle review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
