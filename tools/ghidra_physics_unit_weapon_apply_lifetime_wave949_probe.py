#!/usr/bin/env python3
"""Validate Wave949 PhysicsScript unit/weapon apply lifetime review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave949-physics-unit-weapon-apply-lifetime-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_physics_unit_weapon_apply_lifetime_wave949_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"G:\GhidraBackups\BEA_20260528-075331_post_wave949_physics_unit_weapon_apply_lifetime_review_verified"
SCRIPT_NAME = "test:ghidra-physics-unit-weapon-apply-lifetime-wave949"
SCRIPT_VALUE = r"py -3 tools\ghidra_physics_unit_weapon_apply_lifetime_wave949_probe.py --check"

TARGETS = {
    "0x00432c00": (
        "CUnitSoundMaterial__ApplyToUnitData",
        "void __thiscall CUnitSoundMaterial__ApplyToUnitData(void * this, void * unitData, void * context)",
        ("this +0x8", "+0xe4"),
    ),
    "0x00432c70": (
        "CUnitMaxLegsLifted__ApplyToUnitData",
        "void __thiscall CUnitMaxLegsLifted__ApplyToUnitData(void * this, void * unitData, void * context)",
        ("this +0x8", "+0x140"),
    ),
    "0x00434f20": (
        "CWeaponIconName__ApplyToWeaponByName",
        "void __thiscall CWeaponIconName__ApplyToWeaponByName(void * this, char * weaponName, void * context)",
        ("DAT_008553e8", "icon string", "this +0x8"),
    ),
    "0x00435840": (
        "CWeaponBasedOn__ApplyToWeaponByName",
        "void __thiscall CWeaponBasedOn__ApplyToWeaponByName(void * this, char * weaponName)",
        ("DAT_008553e8", "this+0x8", "selected weapon-record fields"),
    ),
    "0x00432a50": (
        "CUnitAlligence__scalar_deleting_dtor",
        "void * __thiscall CUnitAlligence__scalar_deleting_dtor(void * this, int flags)",
        ("CUnitAlligence__dtor", "OID__FreeObject"),
    ),
    "0x00432a70": (
        "CUnitAlligence__dtor",
        "void __fastcall CUnitAlligence__dtor(void * this)",
        ("child value pointer", "CPhysicsUnitValue base vtable"),
    ),
    "0x00432fa0": (
        "CUnitNavMap__scalar_deleting_dtor",
        "void * __thiscall CUnitNavMap__scalar_deleting_dtor(void * this, int flags)",
        ("CUnitNavMap__dtor", "OID__FreeObject"),
    ),
    "0x00432fc0": (
        "CUnitNavMap__dtor",
        "void __fastcall CUnitNavMap__dtor(void * this)",
        ("child statement pointer", "CPhysicsUnitValue base vtable"),
    ),
    "0x004330e0": (
        "CUnitBehaviour__scalar_deleting_dtor",
        "void * __thiscall CUnitBehaviour__scalar_deleting_dtor(void * this, int flags)",
        ("CUnitBehaviour__dtor", "OID__FreeObject"),
    ),
    "0x00433100": (
        "CUnitBehaviour__dtor",
        "void __fastcall CUnitBehaviour__dtor(void * this)",
        ("child statement pointer", "CPhysicsUnitValue base vtable"),
    ),
}

CONTEXT = {
    "0x00432a20": "CUnitAlligence__LoadFromMemBuffer",
    "0x00432ac0": "CPhysicsUnitValue__base_vtable_scalar_deleting_dtor",
    "0x00432bd0": "CUnitImportance__ApplyToUnitData",
    "0x00432f50": "CUnitNavMap__ApplyToUnitData",
    "0x00433010": "CUnitBehaviour__ApplyToUnitData",
    "0x00434930": "CWeaponConsumption__ApplyToWeaponByName",
    "0x00434de0": "CWeaponVersusAir__ApplyToWeaponByName",
    "0x004347b0": "CPhysicsWeaponValue__base_vtable_scalar_deleting_dtor",
    "0x00432f70": "CUnitNavMap__LoadFromMemBuffer",
    "0x004330b0": "CUnitBehaviour__LoadFromMemBuffer",
    "0x0043e630": "CFlexArray__SkipBytesFromMemBuffer",
    "0x00431bb0": "CPhysicsScriptStatements__CreateStatementType2",
    "0x0043ddc0": "CPhysicsScriptStatements__CreateStatementType12",
    "0x0043e310": "CPhysicsScriptStatements__CreateStatementType13",
    "0x0043e400": "CPhysicsScriptStatements__CreateStatementType14",
}

EXPECTED_XREFS = {
    ("0x00432c00", "0x005d9cdc", "<no_function>", "DATA"),
    ("0x00432c70", "0x005d9c14", "<no_function>", "DATA"),
    ("0x00434f20", "0x005d9f20", "<no_function>", "DATA"),
    ("0x00435840", "0x005da010", "<no_function>", "DATA"),
    ("0x00432a50", "0x005d9d28", "<no_function>", "DATA"),
    ("0x00432a70", "0x00432a53", "CUnitAlligence__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("0x00432fa0", "0x005d9b98", "<no_function>", "DATA"),
    ("0x00432fc0", "0x00432fa3", "CUnitNavMap__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("0x004330e0", "0x005d9d50", "<no_function>", "DATA"),
    ("0x00433100", "0x004330e3", "CUnitBehaviour__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
}

EXPECTED_VTABLE_ROWS = {
    ("0x005d9cd8", "1", "0x00432c00", "CUnitSoundMaterial__ApplyToUnitData"),
    ("0x005d9b98", "31", "0x00432c70", "CUnitMaxLegsLifted__ApplyToUnitData"),
    ("0x005d9f1c", "1", "0x00434f20", "CWeaponIconName__ApplyToWeaponByName"),
    ("0x005d9f80", "36", "0x00435840", "CWeaponBasedOn__ApplyToWeaponByName"),
    ("0x005d9d28", "0", "0x00432a50", "CUnitAlligence__scalar_deleting_dtor"),
    ("0x005d9b98", "0", "0x00432fa0", "CUnitNavMap__scalar_deleting_dtor"),
    ("0x005d9d50", "0", "0x004330e0", "CUnitBehaviour__scalar_deleting_dtor"),
}

DECOMPILE_TOKENS = {
    "pre-decompile/00432c00_CUnitSoundMaterial__ApplyToUnitData.c": ("ROUND", "0xe4"),
    "pre-decompile/00432c70_CUnitMaxLegsLifted__ApplyToUnitData.c": ("ROUND", "0x140"),
    "pre-decompile/00434f20_CWeaponIconName__ApplyToWeaponByName.c": ("DAT_008553e8", "CDXMemoryManager__Free", "CDXMemoryManager__Alloc"),
    "pre-decompile/00435840_CWeaponBasedOn__ApplyToWeaponByName.c": ("DAT_008553e8", "puVar4[9] = puVar5[9]", "puVar4[0x12] = puVar5[0x12]"),
    "pre-decompile/00432a70_CUnitAlligence__dtor.c": ("CUnitAlligence__scalar_deleting_dtor_005d9d28", "CPhysicsUnitValue__base_vtable_scalar_deleting_dtor"),
    "pre-decompile/00432fc0_CUnitNavMap__dtor.c": ("CUnitNavMap__scalar_deleting_dtor_005d9b98", "CPhysicsUnitValue__base_vtable_scalar_deleting_dtor"),
    "pre-decompile/00433100_CUnitBehaviour__dtor.c": ("CUnitBehaviour__scalar_deleting_dtor_005d9d50", "CPhysicsUnitValue__base_vtable_scalar_deleting_dtor"),
}

CORE_TOKENS = (
    "Wave949",
    "physics-unit-weapon-apply-lifetime-wave949",
    "0x00432c00 CUnitSoundMaterial__ApplyToUnitData",
    "0x00432c70 CUnitMaxLegsLifted__ApplyToUnitData",
    "0x00434f20 CWeaponIconName__ApplyToWeaponByName",
    "0x00435840 CWeaponBasedOn__ApplyToWeaponByName",
    "0x00432a50 CUnitAlligence__scalar_deleting_dtor",
    "0x004330e0 CUnitBehaviour__scalar_deleting_dtor",
    "257/1408 = 18.25%",
    "6150/6150 = 100.00%",
    BACKUP,
    "no mutation",
)

OVERCLAIMS = (
    "runtime physics-script behavior proven",
    "runtime weapon icon behavior proven",
    "runtime weapon inheritance behavior proven",
    "runtime gameplay behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalized(addr: str) -> str:
    value = (addr or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def row_by_addr(rows: list[dict[str, str]], addr: str) -> dict[str, str]:
    want = normalized(addr)
    for row in rows:
        got = row.get("address") or row.get("target_addr") or row.get("function_entry") or row.get("pointer_addr") or ""
        if normalized(got) == want:
            return row
    return {}


def check_counts_and_logs(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 10,
        "pre-instructions.tsv": 367,
        "pre-decompile/index.tsv": 10,
        "context-metadata.tsv": 15,
        "context-tags.tsv": 15,
        "context-xrefs.tsv": 16,
        "context-instructions.tsv": 1532,
        "context-decompile/index.tsv": 15,
        "vtables.tsv": 360,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    expected_logs = {
        "pre-metadata.log": "targets=10 found=10 missing=0",
        "pre-tags.log": "rows=10 missing=0",
        "pre-xrefs.log": "Wrote 10 rows",
        "pre-instructions.log": "Wrote 367 function-body instruction rows",
        "pre-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "context-metadata.log": "targets=15 found=15 missing=0",
        "context-tags.log": "rows=15 missing=0",
        "context-xrefs.log": "Wrote 16 rows",
        "context-instructions.log": "Wrote 1532 function-body instruction rows",
        "context-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
        "vtables.log": "ExportVtableSlots complete: targets=9 rows=360",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR:", "MISSING:", "FAIL:", "missing=1", "failed=1", "Invalid script"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_metadata(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "pre-metadata.tsv")
    tags = read_tsv(BASE / "pre-tags.tsv")
    decomp = read_tsv(BASE / "pre-decompile" / "index.tsv")
    context_metadata = read_tsv(BASE / "context-metadata.tsv")

    for addr, (name, signature, comment_tokens) in TARGETS.items():
        row = row_by_addr(metadata, addr)
        require(row.get("name") == name, f"metadata name mismatch for {addr}", failures)
        require(row.get("signature") == signature, f"metadata signature mismatch for {addr}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch for {addr}", failures)
        for token in comment_tokens:
            require(token in row.get("comment", ""), f"missing comment token for {addr}: {token}", failures)
        require(row_by_addr(tags, addr).get("status") == "OK", f"tag status mismatch for {addr}", failures)
        require(row_by_addr(decomp, addr).get("signature") == signature, f"decompile signature mismatch for {addr}", failures)

    for addr, name in CONTEXT.items():
        require(row_by_addr(context_metadata, addr).get("name") == name, f"context metadata mismatch for {addr}", failures)


def check_xrefs_and_vtables(failures: list[str]) -> None:
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    xref_set = {
        (normalized(row.get("target_addr", "")), normalized(row.get("from_addr", "")), row.get("from_function", ""), row.get("ref_type", ""))
        for row in xrefs
    }
    for target, from_addr, from_func, ref_type in EXPECTED_XREFS:
        require((target, from_addr, from_func, ref_type) in xref_set, f"missing xref {target} from {from_addr}", failures)

    vtables = read_tsv(BASE / "vtables.tsv")
    vtable_set = {
        (normalized(row.get("vtable", "")), row.get("slot_index", ""), normalized(row.get("pointer_addr", "")), row.get("function_name", ""))
        for row in vtables
    }
    for expected in EXPECTED_VTABLE_ROWS:
        require(expected in vtable_set, f"missing vtable row {expected}", failures)


def check_decompile_tokens(failures: list[str]) -> None:
    for relative, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing decompile token {token} in {relative}", failures)


def check_queue_backup_docs(failures: list[str]) -> None:
    queue = json.loads(read_text(QUEUE_JSON))
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6150, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    backup = json.loads(read_text(BACKUP_SUMMARY))
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173542279, "backup total bytes mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)

    package = json.loads(read_text(PACKAGE_JSON))
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "package script mismatch", failures)

    for path in [NOTE, CAMPAIGN, PHYSICS_DOC, *STATE_FILES]:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts_and_logs(failures)
    check_metadata(failures)
    check_xrefs_and_vtables(failures)
    check_decompile_tokens(failures)
    check_queue_backup_docs(failures)

    report = {"status": "PASS" if not failures else "FAIL", "failures": failures}
    report_path = BASE / "wave949-probe-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Ghidra Wave949 Physics unit/weapon apply lifetime probe")
    print(f"Status: {report['status']}")
    print(f"Output: {report_path.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
