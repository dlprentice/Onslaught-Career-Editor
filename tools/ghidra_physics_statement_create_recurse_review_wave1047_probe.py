#!/usr/bin/env python3
"""Validate Wave1047 PhysicsScript statement create/recurse artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1047-physics-statement-create-recurse-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_physics_statement_create_recurse_review_wave1047_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1047_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PHYSICS_STATEMENTS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-124915_post_wave1047_physics_statement_create_recurse_review_verified"

TARGETS = {
    "0x0042ede0": (
        "CUnitStatement__CreateUnitAndRecurse",
        "void __fastcall CUnitStatement__CreateUnitAndRecurse(void * this)",
        "0x005d987c",
        ("CUnitAI__CreateAndRegisterByName", "DAT_008553fc", "resolved UnitAI context"),
    ),
    "0x0042f5b0": (
        "CWeaponStatement__CreateWeaponAndRecurse",
        "void __fastcall CWeaponStatement__CreateWeaponAndRecurse(void * this)",
        "0x005d9854",
        ("CWeaponStatement__Create", "statement name/string context", "not a returned registry object"),
    ),
    "0x0042fa40": (
        "CWeaponModeStatement__CreateWeaponModeAndRecurse",
        "void __fastcall CWeaponModeStatement__CreateWeaponModeAndRecurse(void * this)",
        "0x005d9868",
        ("CWeaponModeStatement__Create", "statement name/string context", "not a returned registry object"),
    ),
    "0x0042ff60": (
        "CRoundStatement__CreateRoundAndRecurse",
        "void __fastcall CRoundStatement__CreateRoundAndRecurse(void * this)",
        "0x005d9840",
        ("CRoundStatement__Create", "statement name/string context", "not a returned registry object"),
    ),
    "0x004304d0": (
        "CSpawnerStatement__CreateSpawnerAndRecurse",
        "void __fastcall CSpawnerStatement__CreateSpawnerAndRecurse(void * this)",
        "0x005d982c",
        ("CSpawnerData__CreateAndRegisterByName", "statement name/string context", "not a returned registry object"),
    ),
    "0x004309a0": (
        "CExplosionStatement__CreateExplosionAndRecurse",
        "void __fastcall CExplosionStatement__CreateExplosionAndRecurse(void * this)",
        "0x005d9818",
        ("CExplosionStatement__Create", "statement name/string context", "not a returned registry object"),
    ),
    "0x00430e20": (
        "CComponentStatement__CreateComponentAndRecurse",
        "void __fastcall CComponentStatement__CreateComponentAndRecurse(void * this)",
        "0x005d9804",
        ("CComponentStatement__CreateAndRegisterByName", "statement name/string context", "not a returned registry object"),
    ),
    "0x00431310": (
        "CFeatureStatement__CreateFeatureAndRecurse",
        "void __fastcall CFeatureStatement__CreateFeatureAndRecurse(void * this)",
        "0x005d97f0",
        ("CFeatureStatement__CreateAndRegisterByName", "statement name/string context", "not a returned registry object"),
    ),
    "0x00431760": (
        "CHazardStatement__CreateHazardAndRecurse",
        "void __fastcall CHazardStatement__CreateHazardAndRecurse(void * this)",
        "0x005d97dc",
        ("CHazardStatement__CreateAndRegisterByName", "statement name/string context", "not a returned registry object"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "physics-statement-create-recurse-review-wave1047",
    "wave1047-readback-verified",
    "retail-binary-evidence",
    "physics-script",
    "statement-tranche",
    "statement-create-recurse",
    "comment-corrected",
}

DOC_TOKENS = (
    "Wave1047",
    "physics-statement-create-recurse-review-wave1047",
    "0x0042ede0 CUnitStatement__CreateUnitAndRecurse",
    "0x0042f5b0 CWeaponStatement__CreateWeaponAndRecurse",
    "0x0042fa40 CWeaponModeStatement__CreateWeaponModeAndRecurse",
    "0x0042ff60 CRoundStatement__CreateRoundAndRecurse",
    "0x004304d0 CSpawnerStatement__CreateSpawnerAndRecurse",
    "0x004309a0 CExplosionStatement__CreateExplosionAndRecurse",
    "0x00430e20 CComponentStatement__CreateComponentAndRecurse",
    "0x00431310 CFeatureStatement__CreateFeatureAndRecurse",
    "0x00431760 CHazardStatement__CreateHazardAndRecurse",
    "DAT_008553fc",
    "CStatementChain__InvokeVFunc04OnNodes",
    "740/1408 = 52.56%",
    "998/1509 = 66.14%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "comment/tag correction",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-layout identity proven",
    "exact source layout identity proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-primary-metadata.tsv": 9,
        "pre-primary-tags.tsv": 9,
        "pre-primary-xrefs.tsv": 9,
        "pre-primary-instructions.tsv": 250,
        "pre-primary-decompile/index.tsv": 9,
        "post-primary-metadata.tsv": 9,
        "post-primary-tags.tsv": 9,
        "post-primary-xrefs.tsv": 9,
        "post-primary-instructions.tsv": 250,
        "post-primary-decompile/index.tsv": 9,
        "context-metadata.tsv": 18,
        "context-tags.tsv": 18,
        "context-xrefs.tsv": 26,
        "context-instructions.tsv": 1708,
        "context-decompile/index.tsv": 18,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-primary-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-primary-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-primary-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-primary-xrefs.tsv")}

    for address, (name, signature, xref, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave1047 static re-audit correction", xref, "+0x4", "CStatementChain__InvokeVFunc04OnNodes", *comment_tokens):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref_row = xrefs.get(address)
        require(xref_row is not None, f"missing xref for {address}", failures)
        if xref_row is not None:
            require(normalize_address(xref_row.get("from_addr", "")) == xref, f"xref mismatch at {address}", failures)
            require(xref_row.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)

    unit_decompile = read_text(BASE / "post-primary-decompile" / "0042ede0_CUnitStatement__CreateUnitAndRecurse.c")
    spawner_decompile = read_text(BASE / "post-primary-decompile" / "004304d0_CSpawnerStatement__CreateSpawnerAndRecurse.c")
    for token in ("CUnitAI__CreateAndRegisterByName", "DAT_008553fc", "context"):
        require(token in unit_decompile, f"missing unit decompile token: {token}", failures)
    for token in ("CSpawnerData__CreateAndRegisterByName", "CStatementChain__InvokeVFunc04OnNodes", "name"):
        require(token in spawner_decompile, f"missing spawner decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=9 tags_added=36 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=9 tags_added=36 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-primary-metadata.log": "targets=9 found=9 missing=0",
        "post-primary-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-primary-xrefs.log": "Wrote 9 rows",
        "post-primary-instructions.log": "Wrote 250 function-body instruction rows",
        "post-primary-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "context-metadata.log": "targets=18 found=18 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=18 missing=0",
        "context-xrefs.log": "Wrote 26 rows",
        "context-instructions.log": "Wrote 1708 function-body instruction rows",
        "context-decompile.log": "targets=18 dumped=18 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save success in {relative}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174590855 or backup.get("totalBytes") == 174590855.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        PHYSICS_STATEMENTS_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-physics-statement-create-recurse-review-wave1047")
        == r"py -3 tools\ghidra_physics_statement_create_recurse_review_wave1047_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1047-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1047 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    task = "Wave1047 physics statement create recurse review"
    require(any(row.get("task") == task for row in ledger_rows), "missing Wave1047 ledger row", failures)
    require(any(row.get("task") == task and row.get("attempt_id") == 20629 for row in attempts), "missing Wave1047 attempt row", failures)


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
        print("Wave1047 physics statement create/recurse probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1047 physics statement create/recurse probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
