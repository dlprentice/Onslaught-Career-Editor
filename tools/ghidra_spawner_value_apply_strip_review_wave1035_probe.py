#!/usr/bin/env python3
"""Validate Wave1035 spawner-value apply-strip read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1035-spawner-value-apply-strip-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_spawner_value_apply_strip_review_wave1035_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1035_recheck_2026-06-01.md"
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

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-061824_post_wave1035_spawner_value_apply_strip_review_verified"

TARGETS = {
    "0x0043a170": ("CSpawnerDelay__ApplyToSpawnerByName", "0x005da68c", "0x18", "ECX"),
    "0x0043a200": ("CSpawnerAmount__ApplyToSpawnerByName", "0x005da678", "0xc", "ECX"),
    "0x0043a290": ("CSpawnerConditions__ApplyToSpawnerByName", "0x005da59c", "0x14", "ECX"),
    "0x0043a320": ("CSpawnerSquadSize__ApplyToSpawnerByName", "0x005da664", "0x10", "ECX"),
    "0x0043a3b0": ("CSpawnerSquadDelay__ApplyToSpawnerByName", "0x005da650", "0x20", "ECX"),
    "0x0043a440": ("CSpawnerSeekDelay__ApplyToSpawnerByName", "0x005da63c", "0x1c", "ECX"),
    "0x0043a4d0": ("CSpawnerRecall__ApplyToSpawnerByName", "0x005da628", "0x28", "0x1"),
    "0x0043a570": ("CSpawnerMinRange__ApplyToSpawnerByName", "0x005da614", "0x2c", "ECX"),
    "0x0043a600": ("CSpawnerMaxRange__ApplyToSpawnerByName", "0x005da600", "0x30", "ECX"),
    "0x0043a690": ("CSpawnerPreSpawnDelay__ApplyToSpawnerByName", "0x005da5ec", "0x34", "ECX"),
    "0x0043a720": ("CSpawnerPostSpawnDelay__ApplyToSpawnerByName", "0x005da5d8", "0x38", "ECX"),
    "0x0043a7b0": ("CSpawnerInfinite__ApplyToSpawnerByName", "0x005da5b0", "0x24", "ECX"),
}

DOC_TOKENS = (
    "Wave1035",
    "spawner-value-apply-strip-review-wave1035",
    "0x0043a170 CSpawnerDelay__ApplyToSpawnerByName",
    "0x0043a4d0 CSpawnerRecall__ApplyToSpawnerByName",
    "0x0043a7b0 CSpawnerInfinite__ApplyToSpawnerByName",
    "DAT_008553f4",
    "672/1408 = 47.73%",
    "901/1493 = 60.35%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime physicsscript loading/application behavior proven",
    "runtime spawner behavior proven",
    "mission-script outcomes proven",
    "exact source-body identity proven",
    "exact layout proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 12,
        "tags.tsv": 12,
        "xrefs.tsv": 12,
        "instructions.tsv": 793,
        "decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "xrefs.tsv")}
    instructions = read_tsv(BASE / "instructions.tsv")

    for address, (name, xref_addr, record_offset, store_value) in TARGETS.items():
        signature = f"void __thiscall {name}(void * this, char * spawnerName)"
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("DAT_008553f4", "spawnerName", record_offset):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            tag_text = tag_row.get("tags", "")
            for token in ("static-reaudit", "physics-script", "physics-script-wave339", "spawner-apply", "spawner-value-tranche"):
                require(token in tag_text, f"missing tag at {address}: {token}", failures)
            if address == "0x0043a4d0":
                require("boolean-spawner-value" in tag_text, f"missing recall boolean tag at {address}", failures)
            else:
                require("numeric-spawner-value" in tag_text, f"missing numeric tag at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref at {address}", failures)
        if xref is not None:
            require(normalize_address(xref.get("from_addr", "")) == xref_addr, f"xref mismatch at {address}", failures)
            require(xref.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)

        store_rows = [
            instr
            for instr in instructions
            if normalize_address(instr.get("target_addr", "")) == address
            and instr.get("mnemonic") == "MOV"
            and f"[EDI + {record_offset}]" in instr.get("operands", "")
        ]
        require(store_rows, f"missing record store instruction at {address}", failures)
        if store_rows:
            operands = store_rows[-1].get("operands", "")
            require(store_value in operands, f"store value mismatch at {address}: {operands}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=12 found=12 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "xrefs.log": "Wrote 12 rows",
        "instructions.log": "Wrote 793 function-body instruction rows",
        "decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "FAIL:", "failed=1", "missing=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173968263, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash-diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
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
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIMS:
            require(token not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-spawner-value-apply-strip-review-wave1035")
        == r"py -3 tools\ghidra_spawner_value_apply_strip_review_wave1035_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1035-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1035 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1035 spawner value apply strip review" for row in ledger), "missing ledger row", failures)
    require(
        any(row.get("task") == "Wave1035 spawner value apply strip review" and row.get("attempt_id") == 20617 for row in attempts),
        "missing attempt row",
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
        print("Wave1035 spawner-value apply-strip review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1035 spawner-value apply-strip review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
