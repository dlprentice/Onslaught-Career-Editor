#!/usr/bin/env python3
"""Validate Wave950 physics statement destructor read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave950-physics-statement-destructor-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_physics_statement_destructor_wave950_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-081335_post_wave950_physics_statement_destructor_review_verified"

TARGETS = {
    "0x0042f4f0": ("CUnitStatement__scalar_deleting_dtor", "void * __thiscall CUnitStatement__scalar_deleting_dtor(void * this, int flags)"),
    "0x0042f510": ("CUnitStatement__dtor", "void __fastcall CUnitStatement__dtor(void * this)"),
    "0x0042f570": ("CPhysicsScriptStatement__dtor", "void __fastcall CPhysicsScriptStatement__dtor(void * this)"),
    "0x0042f9c0": ("CWeaponStatement__scalar_deleting_dtor", "void * __thiscall CWeaponStatement__scalar_deleting_dtor(void * this, int flags)"),
    "0x0042f9e0": ("CWeaponStatement__dtor", "void __fastcall CWeaponStatement__dtor(void * this)"),
    "0x0042fee0": ("CWeaponModeStatement__scalar_deleting_dtor", "void * __thiscall CWeaponModeStatement__scalar_deleting_dtor(void * this, int flags)"),
    "0x0042ff00": ("CWeaponModeStatement__dtor", "void __fastcall CWeaponModeStatement__dtor(void * this)"),
    "0x00430450": ("CRoundStatement__scalar_deleting_dtor", "void * __thiscall CRoundStatement__scalar_deleting_dtor(void * this, int flags)"),
    "0x00430470": ("CRoundStatement__dtor", "void __fastcall CRoundStatement__dtor(void * this)"),
    "0x00430920": ("CSpawnerStatement__scalar_deleting_dtor", "void * __thiscall CSpawnerStatement__scalar_deleting_dtor(void * this, int flags)"),
    "0x00430940": ("CSpawnerStatement__dtor", "void __fastcall CSpawnerStatement__dtor(void * this)"),
    "0x00430da0": ("CExplosionStatement__scalar_deleting_dtor", "void * __thiscall CExplosionStatement__scalar_deleting_dtor(void * this, int flags)"),
    "0x00430dc0": ("CExplosionStatement__dtor", "void __fastcall CExplosionStatement__dtor(void * this)"),
    "0x00431290": ("CComponentStatement__scalar_deleting_dtor", "void * __thiscall CComponentStatement__scalar_deleting_dtor(void * this, int flags)"),
    "0x004312b0": ("CComponentStatement__dtor", "void __fastcall CComponentStatement__dtor(void * this)"),
    "0x004316e0": ("CFeatureStatement__scalar_deleting_dtor", "void * __thiscall CFeatureStatement__scalar_deleting_dtor(void * this, int flags)"),
    "0x00431700": ("CFeatureStatement__dtor", "void __fastcall CFeatureStatement__dtor(void * this)"),
    "0x00431b30": ("CHazardStatement__scalar_deleting_dtor", "void * __thiscall CHazardStatement__scalar_deleting_dtor(void * this, int flags)"),
    "0x00431b50": ("CHazardStatement__dtor", "void __fastcall CHazardStatement__dtor(void * this)"),
}

SCALAR_XREFS = {
    "0x0042f4f0": "0x005d9878",
    "0x0042f9c0": "0x005d9850",
    "0x0042fee0": "0x005d9864",
    "0x00430450": "0x005d983c",
    "0x00430920": "0x005d9828",
    "0x00430da0": "0x005d9814",
    "0x00431290": "0x005d9800",
    "0x004316e0": "0x005d97ec",
    "0x00431b30": "0x005d97d8",
}

DTOR_CALL_XREFS = {
    "0x0042f510": "0x0042f4f3",
    "0x0042f9e0": "0x0042f9c3",
    "0x0042ff00": "0x0042fee3",
    "0x00430470": "0x00430453",
    "0x00430940": "0x00430923",
    "0x00430dc0": "0x00430da3",
    "0x004312b0": "0x00431293",
    "0x00431700": "0x004316e3",
    "0x00431b50": "0x00431b33",
}

PAIR_TOKENS = {
    "0x0042f4f0": "CUnitStatement__dtor",
    "0x0042f9c0": "CWeaponStatement__dtor",
    "0x0042fee0": "CWeaponModeStatement__dtor",
    "0x00430450": "CRoundStatement__dtor",
    "0x00430920": "CSpawnerStatement__dtor",
    "0x00430da0": "CExplosionStatement__dtor",
    "0x00431290": "CComponentStatement__dtor",
    "0x004316e0": "CFeatureStatement__dtor",
    "0x00431b30": "CHazardStatement__dtor",
}

CORE_TOKENS = (
    "Wave950",
    "physics-statement-destructor-wave950",
    "0x0042f4f0 CUnitStatement__scalar_deleting_dtor",
    "0x0042f510 CUnitStatement__dtor",
    "0x0042f570 CPhysicsScriptStatement__dtor",
    "0x0042f9c0 CWeaponStatement__scalar_deleting_dtor",
    "0x0042ff00 CWeaponModeStatement__dtor",
    "0x00430470 CRoundStatement__dtor",
    "0x00430940 CSpawnerStatement__dtor",
    "0x00430dc0 CExplosionStatement__dtor",
    "0x004312b0 CComponentStatement__dtor",
    "0x00431700 CFeatureStatement__dtor",
    "0x00431b50 CHazardStatement__dtor",
    "266/1408 = 18.89%",
    "6150/6150 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime physics-script behavior proven",
    "runtime allocator behavior proven",
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
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "pre-metadata.tsv": 19,
        "pre-tags.tsv": 19,
        "pre-xrefs.tsv": 27,
        "pre-instructions.tsv": 308,
        "pre-decompile/index.tsv": 19,
        "context-metadata.tsv": 31,
        "context-tags.tsv": 31,
        "context-xrefs.tsv": 66,
        "context-instructions.tsv": 4566,
        "context-decompile/index.tsv": 31,
        "vtables.tsv": 520,
    }
    for relative, expected in counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count mismatch: {actual} != {expected}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile_index = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row["ref_type"])
        for row in read_tsv(BASE / "pre-xrefs.tsv")
    }
    vtable_targets = {
        (normalize_address(row["pointer_addr"]), row["function_name"], normalize_address(row["slot_addr"]))
        for row in read_tsv(BASE / "vtables.tsv")
        if row.get("status") == "OK"
    }

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("destructor" in row.get("comment", "").lower(), f"missing destructor comment token at {address}", failures)
        dec = decompile_index.get(address)
        require(dec is not None and dec.get("status") == "OK", f"decompile index missing/failed at {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)

    for address, from_addr in SCALAR_XREFS.items():
        require((address, from_addr, "DATA") in xrefs, f"missing scalar DATA xref {from_addr}->{address}", failures)
        name = TARGETS[address][0]
        require(any(ptr == address and fn == name for ptr, fn, _slot in vtable_targets), f"missing vtable slot for {name}", failures)

    for address, from_addr in DTOR_CALL_XREFS.items():
        require((address, from_addr, "UNCONDITIONAL_CALL") in xrefs, f"missing dtor call xref {from_addr}->{address}", failures)

    base_refs = [row for row in read_tsv(BASE / "pre-xrefs.tsv") if normalize_address(row["target_addr"]) == "0x0042f570"]
    require(len(base_refs) >= 9, "base CPhysicsScriptStatement dtor unwind xref count too low", failures)

    for address, paired in PAIR_TOKENS.items():
        name = TARGETS[address][0]
        text = read_text(BASE / "pre-decompile" / f"{address[2:]}_{name}.c")
        require(paired in text, f"missing paired dtor token in {name}", failures)
        require("CDXMemoryManager__Free" in text, f"missing free token in {name}", failures)

    for address in DTOR_CALL_XREFS:
        name = TARGETS[address][0]
        text = read_text(BASE / "pre-decompile" / f"{address[2:]}_{name}.c")
        require("+ 0x10c" in text or "+0x10c" in text, f"missing child +0x10c token in {name}", failures)
        require("005d9894" in text, f"missing base vtable token in {name}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=19 found=19 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=19 missing=0",
        "pre-xrefs.log": "Wrote 27 rows",
        "pre-instructions.log": "Wrote 308 function-body instruction rows",
        "pre-decompile.log": "targets=19 dumped=19 missing=0 failed=0",
        "context-metadata.log": "targets=31 found=31 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=31 missing=0",
        "context-xrefs.log": "Wrote 66 rows",
        "context-instructions.log": "Wrote 4566 function-body instruction rows",
        "context-decompile.log": "targets=31 dumped=31 missing=0 failed=0",
        "vtables.log": "ExportVtableSlots complete: targets=13 rows=520",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [NOTE, CAMPAIGN, PHYSICS_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = json.loads(read_text(PACKAGE_JSON))
    require(
        package["scripts"].get("test:ghidra-physics-statement-destructor-wave950")
        == r"py -3 tools\ghidra_physics_statement_destructor_wave950_probe.py --check",
        "missing package script",
        failures,
    )

    queue = json.loads(read_text(QUEUE_JSON))
    require(queue.get("totalFunctions") == 6150, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(signals.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    backup = json.loads(read_text(BACKUP_SUMMARY))
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173542279, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_docs_and_state(failures)
    if failures:
        print("Ghidra Wave950 Physics statement destructor probe")
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Ghidra Wave950 Physics statement destructor probe")
    print("Status: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
