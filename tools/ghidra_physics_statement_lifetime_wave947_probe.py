#!/usr/bin/env python3
"""Validate Wave947 PhysicsScript lifetime/apply read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave947-physics-statement-lifetime-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_physics_statement_lifetime_wave947_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"G:\GhidraBackups\BEA_20260528-070755_post_wave947_physics_statement_lifetime_review_verified"
SCRIPT_NAME = "test:ghidra-physics-statement-lifetime-wave947"
SCRIPT_VALUE = r"py -3 tools\ghidra_physics_statement_lifetime_wave947_probe.py --check"

TARGETS = {
    "0x00432a20": (
        "CUnitAlligence__LoadFromMemBuffer",
        "void __thiscall CUnitAlligence__LoadFromMemBuffer(void * this, void * memBuffer)",
        "0x005d9d34",
        ("CreateStatementType13", "Alligence spelling"),
    ),
    "0x00432ac0": (
        "CPhysicsUnitValue__base_vtable_scalar_deleting_dtor",
        "void * __thiscall CPhysicsUnitValue__base_vtable_scalar_deleting_dtor(void * this, int flags)",
        "0x005d9e54",
        ("base vtable 0x005d9e54", "OID__FreeObject"),
    ),
    "0x004347b0": (
        "CPhysicsWeaponValue__base_vtable_scalar_deleting_dtor",
        "void * __thiscall CPhysicsWeaponValue__base_vtable_scalar_deleting_dtor(void * this, int flags)",
        "0x005d9f80",
        ("base vtable 0x005d9f80", "OID__FreeObject"),
    ),
    "0x00432bd0": (
        "CUnitImportance__ApplyToUnitData",
        "void __thiscall CUnitImportance__ApplyToUnitData(void * this, void * unitData)",
        "0x005d9cf0",
        ("+0xf8", "one stack argument"),
    ),
    "0x00432c60": (
        "CUnitStandingLegPlacementArea__ApplyToUnitData",
        "void __thiscall CUnitStandingLegPlacementArea__ApplyToUnitData(void * this, void * unitData)",
        "0x005d9c28",
        ("+0x150", "leg-placement"),
    ),
    "0x00432f10": (
        "CUnitStrafeChange__ApplyToUnitData",
        "void __thiscall CUnitStrafeChange__ApplyToUnitData(void * this, void * unitData)",
        "0x005d9bb0",
        ("+0x180", "strafe-change"),
    ),
    "0x00432f50": (
        "CUnitNavMap__ApplyToUnitData",
        "void __thiscall CUnitNavMap__ApplyToUnitData(void * this, void * unitData)",
        "0x005d9b9c",
        ("child value", "+0xfc"),
    ),
    "0x00433010": (
        "CUnitBehaviour__ApplyToUnitData",
        "void __thiscall CUnitBehaviour__ApplyToUnitData(void * this, void * unitData)",
        "0x005d9d54",
        ("behavior id", "+0xe0"),
    ),
    "0x00433150": (
        "CUnitUse__ApplyToUnitData",
        "void __thiscall CUnitUse__ApplyToUnitData(void * this, void * unitData)",
        "0x005d9d68",
        ("0x005119e0", "+0x108"),
    ),
    "0x00434930": (
        "CWeaponConsumption__ApplyToWeaponByName",
        "void __thiscall CWeaponConsumption__ApplyToWeaponByName(void * this, char * weaponName)",
        "0x005d9f34",
        ("DAT_008553e8", "weapon consumption"),
    ),
    "0x00434de0": (
        "CWeaponVersusAir__ApplyToWeaponByName",
        "void __thiscall CWeaponVersusAir__ApplyToWeaponByName(void * this, char * weaponName)",
        "0x005d9e6c",
        ("DAT_008553e8", "versus-air"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "physics-statement-lifetime-wave947",
    "wave947-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "signature-hardened",
    "comment-hardened",
    "physics-script",
}

CORE_TOKENS = (
    "Wave947",
    "physics-statement-lifetime-wave947",
    "wave947-readback-verified",
    "CUnitAlligence__LoadFromMemBuffer",
    "CPhysicsUnitValue__base_vtable_scalar_deleting_dtor",
    "CPhysicsWeaponValue__base_vtable_scalar_deleting_dtor",
    "CUnitImportance__ApplyToUnitData",
    "CUnitBehaviour__ApplyToUnitData",
    "CWeaponConsumption__ApplyToWeaponByName",
    "CWeaponVersusAir__ApplyToWeaponByName",
    "0x00432a20 CUnitAlligence__LoadFromMemBuffer",
    "0x00432ac0 CPhysicsUnitValue__base_vtable_scalar_deleting_dtor",
    "0x004347b0 CPhysicsWeaponValue__base_vtable_scalar_deleting_dtor",
    "0x00433010 CUnitBehaviour__ApplyToUnitData",
    "0x00434de0 CWeaponVersusAir__ApplyToWeaponByName",
    "6150/6150 = 100.00%",
    "243/1408 = 17.26%",
    BACKUP,
)

OVERCLAIMS = (
    "runtime physics behavior proven",
    "runtime lifetime behavior proven",
    "exact source method name proven",
    "exact concrete class layout proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = (value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def rows_by_address(path: Path, field: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row[field]): row for row in read_tsv(path)}


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 30,
        "tags.tsv": 30,
        "xrefs.tsv": 50,
        "instructions.tsv": 3009,
        "decompile/index.tsv": 30,
        "extra-metadata.tsv": 10,
        "extra-tags.tsv": 10,
        "extra-xrefs.tsv": 99,
        "extra-instructions.tsv": 114,
        "extra-decompile/index.tsv": 10,
        "vtable-candidates.tsv": 560,
        "vtable-types.tsv": 70,
        "vtable-slots.tsv": 104,
        "vtable-base-types.tsv": 13,
        "extra-vtable-types.tsv": 429,
        "typed-vtable-slots.tsv": 360,
        "created-targets.txt": 11,
        "post-metadata.tsv": 11,
        "post-tags.tsv": 11,
        "post-xrefs.tsv": 11,
        "post-instructions.tsv": 221,
        "post-decompile/index.tsv": 11,
        "post-vtable-slots.tsv": 104,
        "post-typed-vtable-slots.tsv": 360,
    }
    for rel, count in expected_counts.items():
        path = BASE / rel
        actual = len(read_text(path).splitlines()) if path.suffix == ".txt" else len(read_tsv(path))
        require(actual == count, f"{rel} row count mismatch: {actual} != {count}", failures)

    metadata = rows_by_address(BASE / "post-metadata.tsv")
    tags = rows_by_address(BASE / "post-tags.tsv")
    decompile = rows_by_address(BASE / "post-decompile" / "index.tsv")
    xrefs = rows_by_address(BASE / "post-xrefs.tsv", "target_addr")
    vtable_rows = read_tsv(BASE / "post-vtable-slots.tsv") + read_tsv(BASE / "post-typed-vtable-slots.tsv")

    for address, (name, signature, xref_from, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in ("Wave947", "Static retail Ghidra evidence only", *comment_tokens):
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing tags {address}: {COMMON_TAGS - actual_tags}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch {address}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref {address}", failures)
        if xref:
            require(normalize_address(xref.get("from_addr", "")) == xref_from, f"xref source mismatch {address}", failures)
            require(xref.get("ref_type") == "DATA", f"xref type mismatch {address}", failures)

        require(
            any(
                normalize_address(row.get("pointer_addr", "")) == address
                and row.get("function_name") == name
                and row.get("status") == "OK"
                for row in vtable_rows
            ),
            f"missing typed vtable slot for {address}",
            failures,
        )


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "apply.log": "SUMMARY: updated=11 skipped=0 created=11 would_create=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "post-metadata.log": "targets=11 found=11 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "post-xrefs.log": "Wrote 11 rows",
        "post-instructions.log": "Wrote 221 function-body instruction rows",
        "post-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=13 rows=104",
        "post-typed-vtable-slots.log": "ExportVtableSlots complete: targets=90 rows=360",
    }
    for rel, token in expected_logs.items():
        text = read_text(BASE / rel)
        require(token in text, f"missing log token {rel}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save marker {rel}", failures)
        for bad in ("LockException", "BADADDR:", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token {rel}: {bad}", failures)

    quality_log = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave947.log"
    queue_log = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave947_queue_probe.log"
    require("total_functions=6150 commented_functions=6150" in read_text(quality_log), "quality refresh mismatch", failures)
    require("Total functions: 6150" in read_text(queue_log), "queue probe total mismatch", failures)

    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6150, "queue total mismatch", failures)
    require(signals.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(signals.get("paramSignatureCount") == 0, "queue param mismatch", failures)
    require(len(read_tsv(QUEUE_TSV)) == 6150, "queue TSV row count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)

    docs = [NOTE, CAMPAIGN, GHIDRA_REFERENCE, FUNCTION_INDEX, PHYSICS_DOC, BACKLOG, *STATE_FILES]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave947 PhysicsScript statement lifetime review" for row in ledger_rows), "missing ledger row", failures)
    require(any(row.get("task") == "Wave947 PhysicsScript statement lifetime review" for row in attempt_rows), "missing attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_queue_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave947 PhysicsScript statement lifetime review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave947 PhysicsScript statement lifetime review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
