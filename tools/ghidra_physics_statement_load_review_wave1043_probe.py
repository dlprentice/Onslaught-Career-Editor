#!/usr/bin/env python3
"""Validate Wave1043 PhysicsScript statement load review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1043-physics-statement-load-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_physics_statement_load_review_wave1043_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1043_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-100128_post_wave1043_physics_statement_load_review_verified"

TARGETS = {
    "0x0042f2b0": ("CUnitStatement__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType2", "0x005d9884"),
    "0x0042f780": ("CWeaponStatement__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType3", "0x005d985c"),
    "0x0042fca0": ("CWeaponModeStatement__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType4", "0x005d9870"),
    "0x0042f3d0": ("CPhysicsUnitValueList__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType2", ""),
    "0x0042f8a0": ("CPhysicsWeaponValueList__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType3", ""),
    "0x0042fdc0": ("CPhysicsWeaponModeValueList__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType4", ""),
    "0x00430210": ("CRoundStatement__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType5", "0x005d9848"),
    "0x00430330": ("CPhysicsRoundValueList__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType5", ""),
    "0x004306e0": ("CSpawnerStatement__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType6", "0x005d9834"),
    "0x00430800": ("CPhysicsSpawnerValueList__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType6", ""),
    "0x00430b60": ("CExplosionStatement__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType7", "0x005d9820"),
    "0x00430c80": ("CPhysicsExplosionValueList__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType7", ""),
    "0x00431050": ("CComponentStatement__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType10", "0x005d980c"),
    "0x00431170": ("CPhysicsComponentValueList__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType10", ""),
    "0x004314a0": ("CFeatureStatement__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType8", "0x005d97f8"),
    "0x004315c0": ("CPhysicsFeatureValueList__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType8", ""),
    "0x004318f0": ("CHazardStatement__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType9", "0x005d97e4"),
    "0x00431a10": ("CPhysicsHazardValueList__LoadFromMemBuffer", "CPhysicsScriptStatements__CreateStatementType9", ""),
}

CONTEXT_TARGETS = {
    "0x0042e950": "CPhysicsScript__Load",
    "0x0042eb90": "CPhysicsScript__CreateStatement",
    "0x0042ede0": "CUnitStatement__CreateUnitAndRecurse",
    "0x0042f4b0": "CPhysicsUnitValueList__scalar_deleting_dtor",
    "0x0042f980": "CPhysicsWeaponValueList__scalar_deleting_dtor",
    "0x0042fea0": "CPhysicsWeaponModeValueList__scalar_deleting_dtor",
    "0x00430410": "CPhysicsRoundValueList__scalar_deleting_dtor",
    "0x00549220": "CDXMemoryManager__Free",
}

DOC_TOKENS = (
    "Wave1043",
    "physics-statement-load-review-wave1043",
    "0x0042f2b0 CUnitStatement__LoadFromMemBuffer",
    "0x0042f780 CWeaponStatement__LoadFromMemBuffer",
    "0x0042fca0 CWeaponModeStatement__LoadFromMemBuffer",
    "0x00430210 CRoundStatement__LoadFromMemBuffer",
    "0x004306e0 CSpawnerStatement__LoadFromMemBuffer",
    "0x00431050 CComponentStatement__LoadFromMemBuffer",
    "0x004318f0 CHazardStatement__LoadFromMemBuffer",
    "CPhysicsScriptStatements__CreateStatementType2",
    "CPhysicsScriptStatements__CreateStatementType10",
    "CDXMemBuffer__Read",
    "CDXMemoryManager__Alloc",
    "735/1408 = 52.20%",
    "968/1493 = 64.84%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime physicsscript behavior proven",
    "runtime physics-script behavior proven",
    "serialized physics-script format complete",
    "serialized file-format completeness proven",
    "mission-script outcomes proven",
    "exact source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
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


def read_json(path: Path):
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
        "metadata.tsv": 18,
        "tags.tsv": 18,
        "xrefs.tsv": 45,
        "instructions.tsv": 1701,
        "decompile/index.tsv": 18,
        "context-metadata.tsv": 8,
        "context-tags.tsv": 8,
        "context-xrefs.tsv": 862,
        "context-instructions.tsv": 421,
        "context-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "xrefs.tsv")}

    for address, (name, factory, vtable_ref) in TARGETS.items():
        signature = f"void __thiscall {name}(void * this, void * memBuffer)"
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("correction", factory.split("__")[-1], "unproven"):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            tag_set = set(tag_row.get("tags", "").split(";"))
            for tag in ("physics-script", "statement-load", "statement-tranche", "static-reaudit", "retail-binary-evidence"):
                require(tag in tag_set, f"missing tag at {address}: {tag}", failures)
            if "ValueList__" in name:
                require("value-list" in tag_set, f"missing value-list tag at {address}", failures)
            else:
                require("statement-boundary" in tag_set, f"missing statement-boundary tag at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)

        text = read_text(BASE / "decompile" / f"{address[2:]}_{name}.c")
        for token in ("CDXMemBuffer__Read", "CDXMemoryManager__Alloc", factory, "LoadFromMemBuffer"):
            require(token in text, f"missing decompile token at {address}: {token}", failures)

        if vtable_ref:
            xref = xrefs.get(address)
            require(xref is not None, f"missing vtable DATA xref at {address}", failures)
            if xref is not None:
                require(normalize_address(xref.get("from_addr", "")) == vtable_ref, f"vtable DATA xref mismatch at {address}", failures)
                require(xref.get("ref_type") == "DATA", f"vtable xref type mismatch at {address}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None and row.get("name") == name, f"context metadata mismatch at {address}", failures)


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_logs = {
        "metadata.log": "targets=18 found=18 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=18 missing=0",
        "xrefs.log": "Wrote 45 rows",
        "instructions.log": "Wrote 1701 function-body instruction rows",
        "decompile.log": "targets=18 dumped=18 missing=0 failed=0",
        "context-metadata.log": "targets=8 found=8 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "context-xrefs.log": "Wrote 862 rows",
        "context-instructions.log": "Wrote 421 function-body instruction rows",
        "context-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "failed=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    quality_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1043.log")
    require("total_functions=6238 commented_functions=6238" in quality_log, "quality refresh token mismatch", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", -1)) == 174263175, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        PHYSICS_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        lower = text.lower()
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-physics-statement-load-review-wave1043")
        == r"py -3 tools\ghidra_physics_statement_load_review_wave1043_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1043-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1043 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1043 physics statement load review" for row in ledger_rows), "missing ledger row", failures)
    require(
        any(row.get("task") == "Wave1043 physics statement load review" and row.get("attempt_id") == 20625 for row in attempt_rows),
        "missing attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_queue_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1043 physics statement load review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1043 physics statement load review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
