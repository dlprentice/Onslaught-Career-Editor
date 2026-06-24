#!/usr/bin/env python3
"""Validate Wave943 Unit/CWeapon gameplay read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave943-unit-weapon-gameplay-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_unit_weapon_gameplay_review_wave943_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"G:\GhidraBackups\BEA_20260528-043815_post_wave943_unit_weapon_gameplay_review_verified"
SCRIPT_NAME = "test:ghidra-unit-weapon-gameplay-review-wave943"
SCRIPT_VALUE = r"py -3 tools\ghidra_unit_weapon_gameplay_review_wave943_probe.py --check"

TARGETS = {
    "0x004f6fd0": (
        "CUnit__RenderWithDistanceFade",
        "bool __thiscall CUnit__RenderWithDistanceFade(void * this, uint render_flags)",
        ("Wave545", "OID__RenderWithState1BOverride", "0x0063012c", "RET 0x4"),
    ),
    "0x004fd230": (
        "CUnit__SpawnProfileDropPickup",
        "void __fastcall CUnit__SpawnProfileDropPickup(void * this)",
        ("Wave540", "CWorldPhysicsManager__CreatePickup", "profile +0xe8", "this+0x138"),
    ),
    "0x00505e00": (
        "CWeapon__ctor_base",
        "void * __thiscall CWeapon__ctor_base(void * this, void * weapon_data, int create_context)",
        ("Wave550", "CWorldPhysicsManager__CreateWeaponByIndex", "0x005dfc94", "RET 0x8"),
    ),
    "0x005061f0": (
        "CWeapon__DoesTargetMaskMatchDistanceProfile",
        "bool __thiscall CWeapon__DoesTargetMaskMatchDistanceProfile(void * this, void * target_unit)",
        ("Wave539", "BattleEngine firing callers", "DAT_008553ec", "target_unit+0x34"),
    ),
    "0x005068f0": (
        "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
        "void __fastcall CWeapon__AdvanceChargeProgressIfAnySlotAssigned(void * weapon)",
        ("Wave552", "CGeneralVolume__DispatchMode3BurstProgressAndSpawn", "weapon +0xa4", "DAT_005db358"),
    ),
    "0x0050ee90": (
        "CUnit__scalar_deleting_dtor",
        "void * __thiscall CUnit__scalar_deleting_dtor(void * this, byte flags)",
        ("Wave460", "CUnit__dtor_base_Thunk_004bfe00", "flags & 1", "RET 0x4"),
    ),
}

CONTEXT = {
    "0x004bfe00": "CUnit__dtor_base_Thunk_004bfe00",
    "0x004f84e0": "CUnit__dtor_base",
    "0x004f9490": "CUnit__SpawnConfiguredPickupIfAboveWater",
    "0x004fd040": "CUnit__ResetDeploymentGraphAndScheduleEvent",
    "0x004fd140": "CUnit__MarkDestroyedAndCleanupLinks",
    "0x004fd3d0": "CUnit__IsCandidateSideCompatibleForTargeting",
    "0x00505f90": "CWeapon__DetachFromSetAndShutdownMonitor",
    "0x00506350": "CWeapon__GetDistanceProfileField90",
    "0x00506440": "CWeapon__GetDistanceProfileField94",
    "0x00506530": "CWeapon__GetDistanceProfileFieldA8",
    "0x00506620": "CWeapon__GetDistanceProfileField98",
    "0x00506710": "CWeapon__GetDistanceProfileField9C",
    "0x00506800": "CWeapon__GetDistanceProfileFieldA0",
    "0x005078b0": "ProjectileBurstPreset__GetListEntryIdByIndex",
    "0x00509f70": "TargetProfileContext__IsEligibleByDistanceBucketOrRange",
}

EXPECTED_XREFS = {
    ("xrefs.tsv", "0x004f6fd0", "0x004bfac0", "OID__RenderWithState1BOverride", "UNCONDITIONAL_CALL"),
    ("xrefs.tsv", "0x004fd230", "0x004fd0dd", "CUnit__ResetDeploymentGraphAndScheduleEvent", "UNCONDITIONAL_CALL"),
    ("xrefs.tsv", "0x004fd230", "0x00428208", "CUnitAI__UpdateActivationStateAndSpawnPickup", "UNCONDITIONAL_CALL"),
    ("xrefs.tsv", "0x00505e00", "0x0050f782", "CWorldPhysicsManager__CreateWeaponByIndex", "UNCONDITIONAL_CALL"),
    ("xrefs.tsv", "0x005061f0", "0x00406918", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("xrefs.tsv", "0x005061f0", "0x00406dee", "CBattleEngine__SelectNearestForwardTargetFromGlobalSet", "UNCONDITIONAL_CALL"),
    ("xrefs.tsv", "0x005068f0", "0x00411d4b", "CGeneralVolume__DispatchMode3BurstProgressAndSpawn", "UNCONDITIONAL_CALL"),
    ("xrefs.tsv", "0x005068f0", "0x00413e04", "CBattleEngineWalkerPart__ChargeWeapon", "UNCONDITIONAL_CALL"),
    ("xrefs.tsv", "0x0050ee90", "0x005dfd40", "<no_function>", "DATA"),
    ("context-xrefs.tsv", "0x004bfe00", "0x0050ee93", "CUnit__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x004f84e0", "0x004bfe00", "CUnit__dtor_base_Thunk_004bfe00", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x004fd3d0", "0x00406902", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x00505f90", "0x00505f73", "CWeapon__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x00506350", "0x004067fc", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x005078b0", "0x00506b75", "ProjectileBurst__SpawnFromCurrentPreset", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x00509f70", "0x00406817", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
}

EXPECTED_INSTRUCTIONS = {
    ("instructions.tsv", "0x004f7029", "MOV", "0x0063012c", "CUnit__RenderWithDistanceFade"),
    ("instructions.tsv", "0x004f7033", "MOV", "0xff", "CUnit__RenderWithDistanceFade"),
    ("instructions.tsv", "0x004f7042", "RET", "0x4", "CUnit__RenderWithDistanceFade"),
    ("instructions.tsv", "0x00505e32", "PUSH", "0x456830", "CWeapon__ctor_base"),
    ("instructions.tsv", "0x00505f5e", "RET", "0x8", "CWeapon__ctor_base"),
    ("instructions.tsv", "0x0050628f", "MOV", "0x008553ec", "CWeapon__DoesTargetMaskMatchDistanceProfile"),
    ("instructions.tsv", "0x00506344", "RET", "0x4", "CWeapon__DoesTargetMaskMatchDistanceProfile"),
    ("instructions.tsv", "0x00506912", "FCOMP", "0x005db358", "CWeapon__AdvanceChargeProgressIfAnySlotAssigned"),
    ("instructions.tsv", "0x0050ee93", "CALL", "0x004bfe00", "CUnit__scalar_deleting_dtor"),
    ("instructions.tsv", "0x0050eead", "RET", "0x4", "CUnit__scalar_deleting_dtor"),
}

EXPECTED_VTABLE_SLOTS = {
    ("005dfc94", "0", "00506930", "CWeapon__HandleFireBurstEvent"),
    ("005dfc94", "1", "00505f70", "CWeapon__scalar_deleting_dtor"),
    ("005dfc94", "43", "0050ee90", "CUnit__scalar_deleting_dtor"),
    ("005dfc94", "82", "004f9a90", "CUnit__ApplyDamage"),
    ("005e1510", "8", "004f9a90", "CUnit__ApplyDamage"),
    ("005e1510", "18", "004fd140", "CUnit__MarkDestroyedAndCleanupLinks"),
    ("005e1510", "64", "004ef100", "CUnit__VFunc64_SpawnConfiguredPickupThreeTimes"),
}

DECOMPILE_TOKENS = {
    "decompile/004f6fd0_CUnit__RenderWithDistanceFade.c": ("0x0063012c", "CThing__Render"),
    "decompile/004fd230_CUnit__SpawnProfileDropPickup.c": ("CWorldPhysicsManager__CreatePickup", "this + 0x138"),
    "decompile/00505e00_CWeapon__ctor_base.c": ("0x005dfc94", "DAT_008553ec"),
    "decompile/005061f0_CWeapon__DoesTargetMaskMatchDistanceProfile.c": ("DAT_008553ec", "target_unit"),
    "decompile/005068f0_CWeapon__AdvanceChargeProgressIfAnySlotAssigned.c": ("_DAT_005db358", "weapon + 0x60"),
    "decompile/0050ee90_CUnit__scalar_deleting_dtor.c": ("CUnit__dtor_base_Thunk_004bfe00", "flags & 1"),
    "context-decompile/00505f90_CWeapon__DetachFromSetAndShutdownMonitor.c": ("CSPtrSet__Remove", "CMonitor__Shutdown"),
    "context-decompile/004fd3d0_CUnit__IsCandidateSideCompatibleForTargeting.c": ("candidate_side", "this + 0x138"),
}

CORE_TOKENS = (
    "Wave943",
    "unit-weapon-gameplay-review-wave943",
    "read-only review",
    "186/1408 = 13.21%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x004f6fd0 CUnit__RenderWithDistanceFade",
    "0x004fd230 CUnit__SpawnProfileDropPickup",
    "0x00505e00 CWeapon__ctor_base",
    "0x005061f0 CWeapon__DoesTargetMaskMatchDistanceProfile",
    "0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
    "0x0050ee90 CUnit__scalar_deleting_dtor",
    "0x004bfe00 CUnit__dtor_base_Thunk_004bfe00",
    "0x004f84e0 CUnit__dtor_base",
    "0x00505f90 CWeapon__DetachFromSetAndShutdownMonitor",
    "0x005dfc94",
    "0x005e1510",
)

OVERCLAIMS = (
    "runtime render fade behavior proven",
    "runtime pickup behavior proven",
    "runtime weapon targeting behavior proven",
    "runtime charge behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = (value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def normalize_raw_address(value: str) -> str:
    return normalize_address(value)[2:]


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row[key]): row for row in read_tsv(path)}


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def has_xref(expected: tuple[str, str, str, str, str]) -> bool:
    rel, target, from_addr, from_function, ref_type = expected
    for row in read_tsv(BASE / rel):
        if (
            normalize_address(row.get("target_addr", "")) == normalize_address(target)
            and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
            and row.get("from_function") == from_function
            and row.get("ref_type") == ref_type
        ):
            return True
    return False


def has_instruction(expected: tuple[str, str, str, str, str]) -> bool:
    rel, address, mnemonic, operand_token, function_name = expected
    for row in read_tsv(BASE / rel):
        if (
            normalize_address(row.get("instruction_addr", "")) == normalize_address(address)
            and row.get("mnemonic") == mnemonic
            and operand_token in row.get("operands", "")
            and row.get("function_name") == function_name
        ):
            return True
    return False


def has_vtable_slot(expected: tuple[str, str, str, str]) -> bool:
    vtable, slot, pointer, function_name = expected
    for row in read_tsv(BASE / "vtable-slots.tsv"):
        if (
            normalize_raw_address(row.get("vtable", "")) == normalize_raw_address(vtable)
            and row.get("slot_index") == slot
            and normalize_raw_address(row.get("pointer_addr", "")) == normalize_raw_address(pointer)
            and row.get("function_name") == function_name
            and row.get("status") == "OK"
        ):
            return True
    return False


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 6,
        "tags.tsv": 6,
        "xrefs.tsv": 37,
        "instructions.tsv": 394,
        "decompile/index.tsv": 6,
        "context-metadata.tsv": 15,
        "context-tags.tsv": 15,
        "context-xrefs.tsv": 133,
        "context-instructions.tsv": 1171,
        "context-decompile/index.tsv": 15,
        "vtable-slots.tsv": 192,
    }
    for rel, count in expected_counts.items():
        require(len(read_tsv(BASE / rel)) == count, f"{rel} row count mismatch", failures)

    metadata = row_map(BASE / "metadata.tsv")
    decomp = row_map(BASE / "decompile" / "index.tsv")
    tags = row_map(BASE / "tags.tsv")
    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token {address}: {token}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
        dec = decomp.get(address)
        require(
            dec is not None and dec.get("signature") == signature and dec.get("status") == "OK",
            f"decompile mismatch {address}",
            failures,
        )

    context_meta = row_map(BASE / "context-metadata.tsv")
    for address, name in CONTEXT.items():
        row = context_meta.get(address)
        require(row is not None and row.get("name") == name and row.get("status") == "OK", f"context metadata mismatch {address}", failures)

    for expected in EXPECTED_XREFS:
        require(has_xref(expected), f"missing xref {expected}", failures)
    for expected in EXPECTED_INSTRUCTIONS:
        require(has_instruction(expected), f"missing instruction {expected}", failures)
    for expected in EXPECTED_VTABLE_SLOTS:
        require(has_vtable_slot(expected), f"missing vtable slot {expected}", failures)
    for rel, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / rel)
        for token in tokens:
            require(token in text, f"missing decompile token {rel}: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_logs = {
        "metadata.log": "targets=6 found=6 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "xrefs.log": "Wrote 37 rows",
        "instructions.log": "Wrote 394 function-body instruction rows",
        "decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "context-metadata.log": "targets=15 found=15 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=15 missing=0",
        "context-xrefs.log": "Wrote 133 rows",
        "context-instructions.log": "Wrote 1171 function-body instruction rows",
        "context-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=2 rows=192",
    }
    for rel, token in expected_logs.items():
        text = read_text(BASE / rel)
        require(token in text, f"missing log token {rel}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save marker {rel}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIGNATURE:", "FAIL:", "failed=1", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected log failure {rel}: {bad}", failures)

    for mutation_log in ("apply-dry.log", "apply.log", "apply-final-dry.log"):
        require(not (BASE / mutation_log).exists(), f"unexpected mutation log present: {mutation_log}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173280135, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)

    docs = [NOTE, CAMPAIGN, GHIDRA_REFERENCE, UNIT_DOC, BATTLEENGINE_DOC, *STATE_FILES]
    for path in docs:
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
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave943 Unit/CWeapon gameplay review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave943 Unit/CWeapon gameplay review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
