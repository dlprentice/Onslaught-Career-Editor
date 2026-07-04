#!/usr/bin/env python3
"""Validate Wave936 BattleEngine init/morph/volume read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave936-battleengine-init-morph-volume-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_battleengine_init_morph_volume_review_wave936_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-013432_post_wave936_battleengine_init_morph_volume_review_verified"
SCRIPT_NAME = "test:ghidra-battleengine-init-morph-volume-review-wave936"
SCRIPT_VALUE = r"py -3 tools\ghidra_battleengine_init_morph_volume_review_wave936_probe.py --check"

TARGETS = {
    "0x00404dd0": ("CBattleEngine__Init", "void __thiscall CBattleEngine__Init(void * this, void * init)", ("CBattleEngine init", "+0x5d4/+0x5d8/+0x5dc", "weapon_fire_breaks_stealth")),
    "0x00406da0": ("CBattleEngine__SelectNearestForwardTargetFromGlobalSet", "void * __thiscall CBattleEngine__SelectNearestForwardTargetFromGlobalSet(void * this, void * profile, float originX, float originY, float originZ, float originW, float rangeScale)", ("DAT_008550d0", "+0x294", "originW")),
    "0x0040d0f0": ("CWeaponStatement__UsesBallisticArcNoLocks", "int __thiscall CWeaponStatement__UsesBallisticArcNoLocks(void * this, void * weaponStatement)", ("projectile gravity", "+0x50/+0x6c", "stealth")),
    "0x0040dc30": ("CBattleEngine__EnableVolumeEntryGroupsByName", "void __thiscall CBattleEngine__EnableVolumeEntryGroupsByName(void * this, void * entryName)", ("+0x578", "CGeneralVolume__EnableEntriesByName", "+0x57c")),
    "0x0040dc60": ("CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect", "void __thiscall CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect(void * this, void * entryName)", ("+0x578", "CGeneralVolume__DisableEntriesByNameAndReselect", "+0x57c")),
    "0x0040dcc0": ("CBattleEngine__ClearFlag58CAndMorphIfState3", "void __thiscall CBattleEngine__ClearFlag58CAndMorphIfState3(void * this)", ("+0x58c", "+0x260", "CBattleEngine__Morph")),
}

CONTEXT = {
    "0x00406460": ("CBattleEngine__SwapPrimarySecondaryPartReadersForState", "void __fastcall CBattleEngine__SwapPrimarySecondaryPartReadersForState(void * this)"),
    "0x00406560": ("CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "void __fastcall CBattleEngine__UpdateAutoTargetSetAndFireProjectiles(void * this)"),
    "0x0040dcb0": ("CBattleEngine__SetFlag58CEnabled", "void __thiscall CBattleEngine__SetFlag58CEnabled(void * this)"),
    "0x0040dc90": ("CBattleEngine__CountFlag9CBySelectionMode", "int __thiscall CBattleEngine__CountFlag9CBySelectionMode(void * this)"),
    "0x0040de40": ("CBattleEngine__AugmentWeapon", "void __thiscall CBattleEngine__AugmentWeapon(void * this)"),
    "0x00411b70": ("CBattleEngineJetPart__IsStateMachineActive", "int __thiscall CBattleEngineJetPart__IsStateMachineActive(void * this)"),
    "0x004fb650": ("CUnit__ForwardAimTransformAndAttachTargetReader", "void __thiscall CUnit__ForwardAimTransformAndAttachTargetReader(void * this, void * target_transform, void * target_reader)"),
}

EXPECTED_XREFS = {
    ("0x00404dd0", "0x005d89e8", "<no_function>", "DATA"),
    ("0x00406da0", "0x004068bf", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("0x00406da0", "0x00406a8b", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("0x00406da0", "0x00406b0c", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("0x0040d0f0", "0x005096c1", "CUnit__ComputeMinBallisticTravelDistance", "UNCONDITIONAL_CALL"),
    ("0x0040d0f0", "0x005099c1", "CUnit__ComputeMaxBallisticTravelDistance", "UNCONDITIONAL_CALL"),
    ("0x0040d0f0", "0x00507dd4", "OID__CanFireAtTarget_BallisticArcA", "UNCONDITIONAL_CALL"),
    ("0x0040d0f0", "0x0050919a", "OID__UpdateAimTransformAndAttachTargetReader", "UNCONDITIONAL_CALL"),
    ("0x0040dc30", "0x005d8b5c", "<no_function>", "DATA"),
    ("0x0040dc60", "0x005d8b60", "<no_function>", "DATA"),
    ("0x0040dcc0", "0x00535099", "<no_function>", "UNCONDITIONAL_CALL"),
}

EXPECTED_CONTEXT_XREFS = {
    ("0x00406460", "0x00405863", "CBattleEngine__Init", "UNCONDITIONAL_CALL"),
    ("0x00406460", "0x0040a75d", "CBattleEngine__Morph", "UNCONDITIONAL_CALL"),
    ("0x00406560", "0x00408b84", "CMonitor__Process", "UNCONDITIONAL_CALL"),
    ("0x0040dcb0", "0x00535079", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x0040dc90", "0x00485d60", "CHud__RenderObjectiveStatusPanel", "UNCONDITIONAL_CALL"),
    ("0x0040de40", "0x00408582", "CMonitor__Process", "UNCONDITIONAL_CALL"),
    ("0x00411b70", "0x0040a5bf", "CBattleEngine__Morph", "UNCONDITIONAL_CALL"),
    ("0x004fb650", "0x0047b061", "CGillMHeadAI__UpdateAimTransformAndTargetReader", "UNCONDITIONAL_CALL"),
}

EXPECTED_INSTRUCTIONS = {
    ("instructions.tsv", "0x004058f7", "RET", "0x4", "CBattleEngine__Init"),
    ("instructions.tsv", "0x00406fae", "RET", "0x18", "CBattleEngine__SelectNearestForwardTargetFromGlobalSet"),
    ("instructions.tsv", "0x0040d119", "RET", "", "CWeaponStatement__UsesBallisticArcNoLocks"),
    ("instructions.tsv", "0x0040dc52", "RET", "0x4", "CBattleEngine__EnableVolumeEntryGroupsByName"),
    ("instructions.tsv", "0x0040dc82", "RET", "0x4", "CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect"),
    ("instructions.tsv", "0x0040dcc6", "MOV", "0x58c", "CBattleEngine__ClearFlag58CAndMorphIfState3"),
    ("instructions.tsv", "0x0040dcd5", "JMP", "0x0040a580", "CBattleEngine__ClearFlag58CAndMorphIfState3"),
    ("context-instructions.tsv", "0x00406568", "MOV", "0x260", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles"),
    ("context-instructions.tsv", "0x004068bf", "CALL", "0x00406da0", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles"),
    ("context-instructions.tsv", "0x0040dcb0", "MOV", "0x58c", "CBattleEngine__SetFlag58CEnabled"),
    ("context-instructions.tsv", "0x0040dc90", "CMP", "0x260", "CBattleEngine__CountFlag9CBySelectionMode"),
    ("context-instructions.tsv", "0x0040df06", "MOV", "0x300", "CBattleEngine__AugmentWeapon"),
    ("context-instructions.tsv", "0x004fb669", "RET", "0x8", "CUnit__ForwardAimTransformAndAttachTargetReader"),
}

DECOMPILE_TOKENS = {
    "decompile/00404dd0_CBattleEngine__Init.c": ("CBattleEngine__Init", "0x578", "0x57c", "0x58c", "0x260", "CBattleEngine__SwapPrimarySecondaryPartReadersForState"),
    "decompile/00406da0_CBattleEngine__SelectNearestForwardTargetFromGlobalSet.c": ("DAT_008550d0", "CUnit__IsCandidateSideCompatibleForTargeting", "CWeapon__GetDistanceProfileField98"),
    "decompile/0040d0f0_CWeaponStatement__UsesBallisticArcNoLocks.c": ("CWeaponStatement__UsesBallisticArcNoLocks", "0x50", "0x6c"),
    "decompile/0040dc30_CBattleEngine__EnableVolumeEntryGroupsByName.c": ("CGeneralVolume__EnableEntriesByName", "CGeneralVolume__EnableLinkedEntriesByName"),
    "decompile/0040dc60_CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect.c": ("CGeneralVolume__DisableEntriesByNameAndReselect", "CGeneralVolume__DisableLinkedEntriesByNameAndReselect"),
    "decompile/0040dcc0_CBattleEngine__ClearFlag58CAndMorphIfState3.c": ("0x58c", "0x260", "CBattleEngine__Morph"),
    "context-decompile/00406560_CBattleEngine__UpdateAutoTargetSetAndFireProjectiles.c": ("CBattleEngine__SelectNearestForwardTargetFromGlobalSet", "CBattleEngine__AddProjectile", "0x294"),
    "context-decompile/0040de40_CBattleEngine__AugmentWeapon.c": ("DAT_00672fd0", "hud_weapon_augmented", "0x300", "0x30c"),
    "context-decompile/004fb650_CUnit__ForwardAimTransformAndAttachTargetReader.c": ("OID__UpdateAimTransformAndAttachTargetReader", "target_transform", "target_reader"),
}

CORE_TOKENS = (
    "Wave936",
    "battleengine-init-morph-volume-review-wave936",
    "154/1408 = 10.94%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x00404dd0 CBattleEngine__Init",
    "0x00406da0 CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
    "0x0040d0f0 CWeaponStatement__UsesBallisticArcNoLocks",
    "0x0040dc30 CBattleEngine__EnableVolumeEntryGroupsByName",
    "0x0040dc60 CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect",
    "0x0040dcc0 CBattleEngine__ClearFlag58CAndMorphIfState3",
    "0x00406460 CBattleEngine__SwapPrimarySecondaryPartReadersForState",
    "0x00406560 CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
    "0x0040dcb0 CBattleEngine__SetFlag58CEnabled",
    "0x0040dc90 CBattleEngine__CountFlag9CBySelectionMode",
    "0x0040de40 CBattleEngine__AugmentWeapon",
    "0x00411b70 CBattleEngineJetPart__IsStateMachineActive",
    "0x004fb650 CUnit__ForwardAimTransformAndAttachTargetReader",
    "no mutation",
)

OVERCLAIMS = (
    "runtime morph behavior proven",
    "runtime targeting behavior proven",
    "runtime volume behavior proven",
    "fire-while-cloaked proven",
    "weapon_fire_breaks_stealth closed",
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def row_by_address(rows: list[dict[str, str]], address: str) -> dict[str, str]:
    want = normalize_address(address)
    for row in rows:
        if normalize_address(row.get("address", "")) == want:
            return row
    return {}


def check_counts_and_logs(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 6,
        "tags.tsv": 6,
        "xrefs.tsv": 12,
        "instructions.tsv": 938,
        "decompile/index.tsv": 6,
        "context-metadata.tsv": 7,
        "context-tags.tsv": 7,
        "context-xrefs.tsv": 22,
        "context-instructions.tsv": 828,
        "context-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    expected_logs = {
        "metadata.log": "targets=6 found=6 missing=0",
        "tags.log": "rows=6 missing=0",
        "xrefs.log": "Wrote 12 rows",
        "instructions.log": "Wrote 938 function-body instruction rows",
        "decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "context-metadata.log": "targets=7 found=7 missing=0",
        "context-tags.log": "rows=7 missing=0",
        "context-xrefs.log": "Wrote 22 rows",
        "context-instructions.log": "Wrote 828 function-body instruction rows",
        "context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_metadata_and_decompile(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "metadata.tsv")
    decompile = read_tsv(BASE / "decompile" / "index.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    context_metadata = read_tsv(BASE / "context-metadata.tsv")
    context_decompile = read_tsv(BASE / "context-decompile" / "index.tsv")
    context_tags = read_tsv(BASE / "context-tags.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        for token in comment_tokens:
            require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)
        drow = row_by_address(decompile, address)
        require(drow.get("name") == name, f"decompile name mismatch at {address}", failures)
        require(drow.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
        require(drow.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require(row_by_address(tags, address).get("status") == "OK", f"tag status mismatch at {address}", failures)

    for address, (name, signature) in CONTEXT.items():
        row = row_by_address(context_metadata, address)
        require(row.get("name") == name, f"context name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"context signature mismatch at {address}", failures)
        require(row.get("status") == "OK", f"context metadata status mismatch at {address}", failures)
        drow = row_by_address(context_decompile, address)
        require(drow.get("name") == name, f"context decompile name mismatch at {address}", failures)
        require(drow.get("signature") == signature, f"context decompile signature mismatch at {address}", failures)
        require(drow.get("status") == "OK", f"context decompile status mismatch at {address}", failures)
        require(row_by_address(context_tags, address).get("status") == "OK", f"context tag status mismatch at {address}", failures)


def check_xrefs_instructions_and_decompiles(failures: list[str]) -> None:
    xrefs = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row.get("from_function", ""), row.get("ref_type", ""))
        for row in read_tsv(BASE / "xrefs.tsv")
    }
    context_xrefs = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row.get("from_function", ""), row.get("ref_type", ""))
        for row in read_tsv(BASE / "context-xrefs.tsv")
    }

    for expected in EXPECTED_XREFS:
        require(expected in xrefs, f"missing xref: {expected}", failures)
    for expected in EXPECTED_CONTEXT_XREFS:
        require(expected in context_xrefs, f"missing context xref: {expected}", failures)

    instruction_cache: dict[str, list[dict[str, str]]] = {}
    for relative, address, mnemonic, operand_token, function_name in EXPECTED_INSTRUCTIONS:
        rows = instruction_cache.setdefault(relative, read_tsv(BASE / relative))
        found = any(
            normalize_address(row.get("instruction_addr", "")) == address
            and row.get("mnemonic", "") == mnemonic
            and row.get("function_name", "") == function_name
            and (not operand_token or operand_token in row.get("operands", ""))
            for row in rows
        )
        require(found, f"missing instruction: {relative} {address} {mnemonic} {operand_token} {function_name}", failures)

    for relative, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing decompile token in {relative}: {token}", failures)


def check_backup(failures: list[str]) -> None:
    backup = json.loads(read_text(BASE / "backup-summary.json"))
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", -1)) == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    for path in [NOTE, CAMPAIGN, BATTLEENGINE_DOC, *STATE_FILES]:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = json.loads(read_text(PACKAGE_JSON))
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts_and_logs(failures)
    check_metadata_and_decompile(failures)
    check_xrefs_instructions_and_decompiles(failures)
    check_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave936 BattleEngine init/morph/volume review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave936 BattleEngine init/morph/volume review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
