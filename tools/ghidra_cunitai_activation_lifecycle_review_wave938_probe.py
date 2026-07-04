#!/usr/bin/env python3
"""Validate Wave938 CUnitAI activation/lifecycle read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave938-cunitai-activation-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cunitai_activation_lifecycle_review_wave938_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
UNITAI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "UnitAI.cpp" / "_index.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-021545_post_wave938_cunitai_activation_lifecycle_review_verified"
SCRIPT_NAME = "test:ghidra-cunitai-activation-lifecycle-review-wave938"
SCRIPT_VALUE = r"py -3 tools\ghidra_cunitai_activation_lifecycle_review_wave938_probe.py --check"

TARGETS = {
    "0x00428110": (
        "CUnitAI__UpdateActivationStateAndSpawnPickup",
        "void __fastcall CUnitAI__UpdateActivationStateAndSpawnPickup(void * this)",
        ("Activate", "Deactivated", "Gill_M_Claw_Hit", "CWorldPhysicsManager__CreatePickup"),
    ),
    "0x00428500": (
        "CUnitAI__RefreshCachedComponentTransform",
        "void __fastcall CUnitAI__RefreshCachedComponentTransform(void * this)",
        ("this+0x278", "DAT_008a9aac", "this+0x250/0x254", "Mat34__SetRows"),
    ),
    "0x00428800": (
        "CUnitAI__HandleTriggerEventAndMoveToOffset",
        "bool __fastcall CUnitAI__HandleTriggerEventAndMoveToOffset(void * this)",
        ("marks the unit destroyed", "resets deployment graph state", "releases child units"),
    ),
    "0x004289b0": (
        "CUnitAI__AdvanceActivationAnimationState",
        "bool __fastcall CUnitAI__AdvanceActivationAnimationState(void * this)",
        ("Hit/retract/normal/Activate/Activated/Deactivated", "falls back to deploy/fire animation completion"),
    ),
    "0x00428cb0": (
        "CUnitAI__PlayHitAnimationAndSetFlag",
        "void __fastcall CUnitAI__PlayHitAnimationAndSetFlag(void * this)",
        ("Hit", "+0x2bc", "prior ExplosionInitThing owner"),
    ),
}

CONTEXT = {
    "0x00428d50": (
        "CUnitAI__PlayActivateAnimationOrFinalizeActivated",
        "void __fastcall CUnitAI__PlayActivateAnimationOrFinalizeActivated(void * this)",
        ("Activate animation token", "vtable slot 0xf0"),
    ),
    "0x00428b50": (
        "CUnit__SetReaderAndComputeRelativeYaw",
        "void __thiscall CUnit__SetReaderAndComputeRelativeYaw(void * this, void * reader, void * readerContext, int unusedMode)",
        ("active-reader setter", "flag 0x100000", "third observed stack argument is unused"),
    ),
    "0x004fa8d0": (
        "CUnit__UpdateMotionAttachmentsAndEffects",
        "void __fastcall CUnit__UpdateMotionAttachmentsAndEffects(void * this)",
        ("CUnit__UpdateClosingAndUnshuttingState", "CActor__Move", "support-loop audio"),
    ),
    "0x004fcfe0": (
        "CUnit__ReleaseChildUnits",
        "void __fastcall CUnit__ReleaseChildUnits(void * this)",
        ("+0x19c", "vfunc +0x8 or +0xc8", "destroyed flag bit 2"),
    ),
    "0x004fd040": (
        "CUnit__ResetDeploymentGraphAndScheduleEvent",
        "void __fastcall CUnit__ResetDeploymentGraphAndScheduleEvent(void * this)",
        ("CExplosionInitThing__ctor_like_004fd230", "script event id 3/reset", "schedules event 2000"),
    ),
    "0x004fd140": (
        "CUnit__MarkDestroyedAndCleanupLinks",
        "int __fastcall CUnit__MarkDestroyedAndCleanupLinks(void * this)",
        ("destroyed flag bit 2", "script event id 5", "drains +0x18c"),
    ),
}

EXPECTED_XREFS = {
    ("0x00428110", "0x005e4300", "<no_function>", "DATA"),
    ("0x00428110", "0x005e3e48", "<no_function>", "DATA"),
    ("0x00428110", "0x004f0b84", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x00428500", "0x00428740", "CUnitAI__GetRenderPosFromActorOrCache", "UNCONDITIONAL_CALL"),
    ("0x00428500", "0x004287a0", "CUnitAI__GetRenderOrientationFromActorOrCache", "UNCONDITIONAL_CALL"),
    ("0x00428500", "0x004284d1", "CUnitAI__UpdateActivationStateAndSpawnPickup", "UNCONDITIONAL_CALL"),
    ("0x00428800", "0x005e42c0", "<no_function>", "DATA"),
    ("0x00428800", "0x005e3e08", "<no_function>", "DATA"),
    ("0x004289b0", "0x005e4088", "<no_function>", "DATA"),
    ("0x004289b0", "0x005e3e2c", "<no_function>", "DATA"),
    ("0x00428cb0", "0x00479eb6", "CGillM__TriggerRandomArmHitAnimationIfReady", "UNCONDITIONAL_CALL"),
}

EXPECTED_CONTEXT_XREFS = {
    ("0x00428d50", "0x005e4250", "<no_function>", "DATA"),
    ("0x00428d50", "0x005e3d98", "<no_function>", "DATA"),
    ("0x00428d50", "0x004f0e6a", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x00428b50", "0x004f8d7c", "CUnit__Init", "UNCONDITIONAL_CALL"),
    ("0x004fa8d0", "0x00428496", "CUnitAI__UpdateActivationStateAndSpawnPickup", "UNCONDITIONAL_CALL"),
    ("0x004fa8d0", "0x00403159", "CUnit__UpdateMotionAndTrailEffects", "UNCONDITIONAL_CALL"),
    ("0x004fcfe0", "0x00428850", "CUnitAI__HandleTriggerEventAndMoveToOffset", "UNCONDITIONAL_CALL"),
    ("0x004fd040", "0x0042882d", "CUnitAI__HandleTriggerEventAndMoveToOffset", "UNCONDITIONAL_CALL"),
    ("0x004fd040", "0x004d38d0", "CUnit__TryDestroyedCleanupAndResetDeploymentGraph", "UNCONDITIONAL_CALL"),
    ("0x004fd140", "0x00428822", "CUnitAI__HandleTriggerEventAndMoveToOffset", "UNCONDITIONAL_CALL"),
    ("0x004fd140", "0x0042883e", "CUnitAI__HandleTriggerEventAndMoveToOffset", "UNCONDITIONAL_CALL"),
    ("0x004fd140", "0x004d38c3", "CUnit__TryDestroyedCleanupAndResetDeploymentGraph", "UNCONDITIONAL_CALL"),
}

EXPECTED_INSTRUCTIONS = {
    ("instructions.tsv", "0x0042811e", "TEST", "[EDI + 0x2c]", "CUnitAI__UpdateActivationStateAndSpawnPickup"),
    ("instructions.tsv", "0x004282da", "CMP", "[EDI + 0x2bc]", "CUnitAI__UpdateActivationStateAndSpawnPickup"),
    ("instructions.tsv", "0x00428496", "CALL", "0x004fa8d0", "CUnitAI__UpdateActivationStateAndSpawnPickup"),
    ("instructions.tsv", "0x004284d1", "CALL", "0x00428500", "CUnitAI__UpdateActivationStateAndSpawnPickup"),
    ("instructions.tsv", "0x0042850f", "MOV", "[EBX + 0x278]", "CUnitAI__RefreshCachedComponentTransform"),
    ("instructions.tsv", "0x00428537", "MOV", "[EBX + 0x254]", "CUnitAI__RefreshCachedComponentTransform"),
    ("instructions.tsv", "0x004286cf", "CALL", "0x00401ec0", "CUnitAI__RefreshCachedComponentTransform"),
    ("instructions.tsv", "0x004286fa", "MOV", "[EBX + 0x278]", "CUnitAI__RefreshCachedComponentTransform"),
    ("instructions.tsv", "0x00428822", "CALL", "0x004fd140", "CUnitAI__HandleTriggerEventAndMoveToOffset"),
    ("instructions.tsv", "0x0042882d", "CALL", "0x004fd040", "CUnitAI__HandleTriggerEventAndMoveToOffset"),
    ("instructions.tsv", "0x00428850", "CALL", "0x004fcfe0", "CUnitAI__HandleTriggerEventAndMoveToOffset"),
    ("instructions.tsv", "0x00428997", "CALL", "0x0044b370", "CUnitAI__HandleTriggerEventAndMoveToOffset"),
    ("instructions.tsv", "0x00428a0d", "MOV", "[ESI + 0x2bc]", "CUnitAI__AdvanceActivationAnimationState"),
    ("instructions.tsv", "0x00428abc", "CALL", "0x004fd6a0", "CUnitAI__AdvanceActivationAnimationState"),
    ("instructions.tsv", "0x00428b33", "CALL", "0x004fdeb0", "CUnitAI__AdvanceActivationAnimationState"),
    ("instructions.tsv", "0x00428cc4", "CALL", "[EAX + 0x24]", "CUnitAI__PlayHitAnimationAndSetFlag"),
    ("instructions.tsv", "0x00428cd1", "CALL", "[EDI + 0xf0]", "CUnitAI__PlayHitAnimationAndSetFlag"),
    ("instructions.tsv", "0x00428cd7", "MOV", "[ESI + 0x2bc]", "CUnitAI__PlayHitAnimationAndSetFlag"),
    ("context-instructions.tsv", "0x00428d5d", "CALL", "[EAX + 0x24]", "CUnitAI__PlayActivateAnimationOrFinalizeActivated"),
    ("context-instructions.tsv", "0x00428d88", "CALL", "[EDX + 0xf0]", "CUnitAI__PlayActivateAnimationOrFinalizeActivated"),
    ("context-instructions.tsv", "0x00428b86", "CALL", "[EDX + 0x160]", "CUnit__SetReaderAndComputeRelativeYaw"),
    ("context-instructions.tsv", "0x00428b96", "MOV", "0x100000", "CUnit__SetReaderAndComputeRelativeYaw"),
    ("context-instructions.tsv", "0x004fcfe5", "LEA", "[EBP + 0x19c]", "CUnit__ReleaseChildUnits"),
    ("context-instructions.tsv", "0x004fd005", "CALL", "[EAX + 0xc8]", "CUnit__ReleaseChildUnits"),
    ("context-instructions.tsv", "0x004fd0dd", "CALL", "0x004fd230", "CUnit__ResetDeploymentGraphAndScheduleEvent"),
    ("context-instructions.tsv", "0x004fd12d", "CALL", "0x0044b370", "CUnit__ResetDeploymentGraphAndScheduleEvent"),
    ("context-instructions.tsv", "0x004fd143", "TEST", "[ESI + 0x2c]", "CUnit__MarkDestroyedAndCleanupLinks"),
    ("context-instructions.tsv", "0x004fd15e", "OR", "[ESI + 0x2c]", "CUnit__MarkDestroyedAndCleanupLinks"),
    ("context-instructions.tsv", "0x004fd225", "RET", "", "CUnit__MarkDestroyedAndCleanupLinks"),
}

DECOMPILE_TOKENS = {
    "decompile/00428110_CUnitAI__UpdateActivationStateAndSpawnPickup.c": ("s_Activate", "s_Deactivated", "s_Gill_M_Claw_Hit", "CWorldPhysicsManager__CreatePickup", "CUnit__UpdateMotionAttachmentsAndEffects"),
    "decompile/00428500_CUnitAI__RefreshCachedComponentTransform.c": ("DAT_008a9aac", "Mat34__SetRows", "0x278"),
    "decompile/00428800_CUnitAI__HandleTriggerEventAndMoveToOffset.c": ("CUnit__MarkDestroyedAndCleanupLinks", "CUnit__ResetDeploymentGraphAndScheduleEvent", "CUnit__ReleaseChildUnits"),
    "decompile/004289b0_CUnitAI__AdvanceActivationAnimationState.c": ("s_Activated", "s_Deactivated", "CUnitAI__HandleDeployAndFireAnimationCompletion"),
    "decompile/00428cb0_CUnitAI__PlayHitAnimationAndSetFlag.c": ("CUnitAI__PlayHitAnimationAndSetFlag", "0x2bc"),
    "context-decompile/00428d50_CUnitAI__PlayActivateAnimationOrFinalizeActivated.c": ("s_Activate", "CUnit__VFunc22_ActivateLinkedTargetsAndChildren"),
    "context-decompile/00428b50_CUnit__SetReaderAndComputeRelativeYaw.c": ("CUnit__SetReaderAndComputeRelativeYaw", "0x100000"),
    "context-decompile/004fa8d0_CUnit__UpdateMotionAttachmentsAndEffects.c": ("CUnit__UpdateMotionAttachmentsAndEffects", "CActor__Move"),
    "context-decompile/004fcfe0_CUnit__ReleaseChildUnits.c": ("CUnit__ReleaseChildUnits", "0x19c"),
    "context-decompile/004fd040_CUnit__ResetDeploymentGraphAndScheduleEvent.c": ("CExplosionInitThing__ctor_like_004fd230", "0x18c"),
    "context-decompile/004fd140_CUnit__MarkDestroyedAndCleanupLinks.c": ("CUnit__MarkDestroyedAndCleanupLinks", "0x2c"),
}

CORE_TOKENS = (
    "Wave938",
    "cunitai-activation-lifecycle-review-wave938",
    "166/1408 = 11.79%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x00428110 CUnitAI__UpdateActivationStateAndSpawnPickup",
    "0x00428500 CUnitAI__RefreshCachedComponentTransform",
    "0x00428800 CUnitAI__HandleTriggerEventAndMoveToOffset",
    "0x004289b0 CUnitAI__AdvanceActivationAnimationState",
    "0x00428cb0 CUnitAI__PlayHitAnimationAndSetFlag",
    "0x00428d50 CUnitAI__PlayActivateAnimationOrFinalizeActivated",
    "0x00428b50 CUnit__SetReaderAndComputeRelativeYaw",
    "0x004fa8d0 CUnit__UpdateMotionAttachmentsAndEffects",
    "0x004fcfe0 CUnit__ReleaseChildUnits",
    "0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent",
    "0x004fd140 CUnit__MarkDestroyedAndCleanupLinks",
    "no mutation",
)

OVERCLAIMS = (
    "runtime activation behavior proven",
    "runtime pickup behavior proven",
    "runtime trigger behavior proven",
    "runtime movement behavior proven",
    "runtime destruction behavior proven",
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
    variants = (token, token.replace("\\", "\\\\"))
    lower_text = text.lower()
    return any(variant in text or variant.lower() in lower_text for variant in variants)


def row_by_address(rows: list[dict[str, str]], address: str) -> dict[str, str]:
    want = normalize_address(address)
    for row in rows:
        if normalize_address(row.get("address", "")) == want:
            return row
    return {}


def check_counts_and_logs(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 5,
        "tags.tsv": 5,
        "xrefs.tsv": 11,
        "instructions.tsv": 726,
        "decompile/index.tsv": 5,
        "context-metadata.tsv": 6,
        "context-tags.tsv": 6,
        "context-xrefs.tsv": 35,
        "context-instructions.tsv": 964,
        "context-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    expected_logs = {
        "metadata.log": "targets=5 found=5 missing=0",
        "tags.log": "rows=5 missing=0",
        "xrefs.log": "Wrote 11 rows",
        "instructions.log": "Wrote 726 function-body instruction rows",
        "decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "context-metadata.log": "targets=6 found=6 missing=0",
        "context-tags.log": "rows=6 missing=0",
        "context-xrefs.log": "Wrote 35 rows",
        "context-instructions.log": "Wrote 964 function-body instruction rows",
        "context-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
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
        tag_row = row_by_address(tags, address)
        require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
        require("static-reaudit" in tag_row.get("tags", ""), f"missing static-reaudit tag at {address}", failures)

    for address, (name, signature, comment_tokens) in CONTEXT.items():
        row = row_by_address(context_metadata, address)
        require(row.get("name") == name, f"context name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"context signature mismatch at {address}", failures)
        require(row.get("status") == "OK", f"context metadata status mismatch at {address}", failures)
        for token in comment_tokens:
            require(token in row.get("comment", ""), f"missing context comment token at {address}: {token}", failures)
        drow = row_by_address(context_decompile, address)
        require(drow.get("name") == name, f"context decompile name mismatch at {address}", failures)
        require(drow.get("signature") == signature, f"context decompile signature mismatch at {address}", failures)
        require(drow.get("status") == "OK", f"context decompile status mismatch at {address}", failures)
        require(row_by_address(context_tags, address).get("status") == "OK", f"context tag status mismatch at {address}", failures)


def xref_set(path: Path) -> set[tuple[str, str, str, str]]:
    return {
        (
            normalize_address(row["target_addr"]),
            normalize_address(row["from_addr"]),
            row.get("from_function", ""),
            row.get("ref_type", ""),
        )
        for row in read_tsv(path)
    }


def check_xrefs_instructions_and_decompiles(failures: list[str]) -> None:
    xrefs = xref_set(BASE / "xrefs.tsv")
    context_xrefs = xref_set(BASE / "context-xrefs.tsv")

    for expected in EXPECTED_XREFS:
        require((normalize_address(expected[0]), normalize_address(expected[1]), expected[2], expected[3]) in xrefs, f"missing xref: {expected}", failures)
    for expected in EXPECTED_CONTEXT_XREFS:
        require((normalize_address(expected[0]), normalize_address(expected[1]), expected[2], expected[3]) in context_xrefs, f"missing context xref: {expected}", failures)

    instruction_cache: dict[str, list[dict[str, str]]] = {}
    for relative, address, mnemonic, operand_token, function_name in EXPECTED_INSTRUCTIONS:
        rows = instruction_cache.setdefault(relative, read_tsv(BASE / relative))
        found = any(
            normalize_address(row.get("instruction_addr", "")) == normalize_address(address)
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
    for path in [NOTE, CAMPAIGN, UNITAI_DOC, UNIT_DOC, *STATE_FILES]:
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
        print("Wave938 CUnitAI activation/lifecycle review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave938 CUnitAI activation/lifecycle review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
