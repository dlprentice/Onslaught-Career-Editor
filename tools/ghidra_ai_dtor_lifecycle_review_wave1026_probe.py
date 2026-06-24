#!/usr/bin/env python3
"""Validate Wave1026 AI destructor lifecycle read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1026-ai-dtor-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_ai_dtor_lifecycle_review_wave1026_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1026_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
BOAT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Boat.cpp" / "_index.md"
BOMBER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Bomber.cpp" / "_index.md"
UNITAI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "UnitAI.cpp" / "_index.md"
BUILDING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Building.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-013000_post_wave1026_ai_dtor_lifecycle_review_verified"

TARGETS = {
    "0x00414fa0": ("CBoatAI__scalar_deleting_dtor", "void * __thiscall CBoatAI__scalar_deleting_dtor(void * this, int flags)", ("0x00414fc0", "scalar-delete flag")),
    "0x00414fc0": ("CBoatAI__dtor_body_00414fc0", "void __fastcall CBoatAI__dtor_body_00414fc0(void * this)", ("0x005d8d1c", "CSPtrSet__Remove", "CMonitor__Shutdown")),
    "0x00415060": ("CUnitAI__scalar_deleting_dtor", "void * __thiscall CUnitAI__scalar_deleting_dtor(void * this, int flags)", ("0x00415080", "scalar-delete flag")),
    "0x00415080": ("CUnitAI__dtor_body_00415080", "void __fastcall CUnitAI__dtor_body_00415080(void * this)", ("0x005d8d1c", "CSPtrSet__Remove", "CMonitor__Shutdown")),
    "0x004161a0": ("CBomberAI__scalar_deleting_dtor", "void * __thiscall CBomberAI__scalar_deleting_dtor(void * this, int flags)", ("0x004161c0", "Bomber.cpp source is missing")),
    "0x004161c0": ("CBomberAI__dtor_body_004161c0", "void __fastcall CBomberAI__dtor_body_004161c0(void * this)", ("0x005d8d1c", "Bomber.cpp source is missing", "CMonitor__Shutdown")),
    "0x00416260": ("CBomberGuide__scalar_deleting_dtor", "void * __thiscall CBomberGuide__scalar_deleting_dtor(void * this, int flags)", ("0x00416280", "Bomber.cpp source is missing")),
    "0x00416280": ("CBomberGuide__dtor_body_00416280", "void __fastcall CBomberGuide__dtor_body_00416280(void * this)", ("+0x2c", "CSPtrSet__Remove", "CMonitor__Shutdown")),
    "0x00417480": ("CRepairPadAI__scalar_deleting_dtor", "void * __thiscall CRepairPadAI__scalar_deleting_dtor(void * this, int flags)", ("0x004174a0", "scalar-delete flag")),
    "0x004174a0": ("CRepairPadAI__dtor_body_004174a0", "void __fastcall CRepairPadAI__dtor_body_004174a0(void * this)", ("0x005d8d1c", "CSPtrSet__Remove", "CMonitor__Shutdown")),
    "0x00417590": ("CBuilding__dtor_body_00417590", "void __fastcall CBuilding__dtor_body_00417590(void * this)", ("0x005d8eb4", "0x005d8e3c", "CUnit cleanup")),
    "0x004176a0": ("CBuilding__scalar_deleting_dtor", "void * __thiscall CBuilding__scalar_deleting_dtor(void * this, int flags)", ("0x00417590", "scalar-delete flag")),
}

XREF_TOKENS = (
    "005d8cec",
    "005d8d20",
    "005d8d8c",
    "005d8dc0",
    "005d8e0c",
    "005d8eb8",
    "00414fa3",
    "00415063",
    "004161a3",
    "00416263",
    "00417483",
    "004176a3",
)

DOC_TOKENS = (
    "Wave1026",
    "ai-dtor-lifecycle-review-wave1026",
    "0x00414fa0 CBoatAI__scalar_deleting_dtor",
    "0x00415080 CUnitAI__dtor_body_00415080",
    "0x004161c0 CBomberAI__dtor_body_004161c0",
    "0x00416280 CBomberGuide__dtor_body_00416280",
    "0x004174a0 CRepairPadAI__dtor_body_004174a0",
    "0x004176a0 CBuilding__scalar_deleting_dtor",
    "588/1408 = 41.76%",
    "817/1493 = 54.72%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OWNER_DOC_TOKENS = {
    BOAT_DOC: ("Wave1026", "ai-dtor-lifecycle-review-wave1026", "0x00414fa0 CBoatAI__scalar_deleting_dtor", "0x00415080 CUnitAI__dtor_body_00415080", BACKUP_PATH),
    BOMBER_DOC: ("Wave1026", "ai-dtor-lifecycle-review-wave1026", "0x004161c0 CBomberAI__dtor_body_004161c0", "0x00416280 CBomberGuide__dtor_body_00416280", BACKUP_PATH),
    UNITAI_DOC: ("Wave1026", "ai-dtor-lifecycle-review-wave1026", "0x00415060 CUnitAI__scalar_deleting_dtor", "0x00415080 CUnitAI__dtor_body_00415080", BACKUP_PATH),
    BUILDING_DOC: ("Wave1026", "ai-dtor-lifecycle-review-wave1026", "0x004174a0 CRepairPadAI__dtor_body_004174a0", "0x004176a0 CBuilding__scalar_deleting_dtor", BACKUP_PATH),
}

OVERCLAIMS = (
    "runtime cleanup behavior proven",
    "runtime boat behavior proven",
    "runtime bomber behavior proven",
    "exact source-body identity proven",
    "exact layout proven",
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
        "metadata.tsv": 12,
        "tags.tsv": 12,
        "xrefs.tsv": 14,
        "instructions.tsv": 301,
        "decompile/index.tsv": 12,
        "context-metadata.tsv": 4,
        "context-tags.tsv": 4,
        "context-xrefs.tsv": 4,
        "context-instructions.tsv": 215,
        "context-decompile/index.tsv": 4,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "decompile" / "index.tsv"), "address")
    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            comment = row.get("comment", "")
            for token in tokens:
                require(token in comment, f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    evidence = "\n".join(
        read_text(BASE / path)
        for path in (
            "xrefs.tsv",
            "context-xrefs.tsv",
            "instructions.tsv",
            "context-instructions.tsv",
        )
    )
    for token in XREF_TOKENS:
        require(token in evidence, f"missing xref/call token: {token}", failures)
    for token in ("CSPtrSet__Remove", "CMonitor__Shutdown", "CDXMemoryManager__Free", "CUnit__dtor_base"):
        require(token in read_text(BASE / "instructions.tsv") or token in read_text(BASE / "context-instructions.tsv") or token in "\n".join(read_text(path) for path in (BASE / "decompile").glob("*.c")), f"missing instruction/decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "metadata.log": "targets=12 found=12 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "xrefs.log": "Wrote 14 rows",
        "instructions.log": "targets=12 missing=0",
        "decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "context-metadata.log": "targets=4 found=4 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "context-xrefs.log": "Wrote 4 rows",
        "context-instructions.log": "targets=4 missing=0",
        "context-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173968263, 173968263.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-ai-dtor-lifecycle-review-wave1026") == r"py -3 tools\ghidra_ai_dtor_lifecycle_review_wave1026_probe.py --check", "missing Wave1026 package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1026-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1026 --check", "missing aggregate package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1026 AI destructor lifecycle review" for row in ledger_rows), "missing Wave1026 ledger row", failures)
    require(any(row.get("task") == "Wave1026 AI destructor lifecycle review" and row.get("attempt_id") == 20608 for row in attempts), "missing Wave1026 attempt row", failures)


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6238, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)
    check_queue(failures)

    if failures:
        print("Wave1026 AI destructor lifecycle review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1026 AI destructor lifecycle review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
