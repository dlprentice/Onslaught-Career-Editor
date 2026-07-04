#!/usr/bin/env python3
"""Validate Wave941 missile linked-object dispatch read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave941-missile-linked-object-dispatch-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_missile_linked_object_dispatch_review_wave941_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
MISSILE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Missile.cpp" / "_index.md"
ROUND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Round.cpp" / "_index.md"
WORLDPHYS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-034712_post_wave941_missile_linked_object_dispatch_review_verified"
SCRIPT_NAME = "test:ghidra-missile-linked-object-dispatch-review-wave941"
SCRIPT_VALUE = r"py -3 tools\ghidra_missile_linked_object_dispatch_review_wave941_probe.py --check"

TARGETS = {
    "0x004baae0": (
        "CMissile__Init",
        "void __thiscall CMissile__Init(void * this, void * init)",
        ("0x428", "OID type 0x61", "PCRTID__CreateObject", "this+0x30", "CRound__Init"),
    ),
    "0x004bac10": (
        "CMissile__DispatchLinkedObjectVFunc68AndPostHook",
        "void __thiscall CMissile__DispatchLinkedObjectVFunc68AndPostHook(void * this, int arg0, int arg1)",
        ("0x005e3cc0", "vfunc +0x68", "SharedVFunc__NoOp_Ret08", "Ret 0x8"),
    ),
    "0x0050f8b0": (
        "CMissile__scalar_deleting_dtor",
        "void * __thiscall CMissile__scalar_deleting_dtor(void * this, byte delete_flags)",
        ("0x005e3ba8", "CMissile__Destructor", "delete_flags", "RET 0x4"),
    ),
    "0x0050f8d0": (
        "CMissile__Destructor",
        "void __fastcall CMissile__Destructor(void * this)",
        ("this+0xec", "this+0xe8", "this+0xe0", "CActor__dtor_base"),
    ),
}

CONTEXT = {
    "0x00403f40": "CResourceDescriptor__ctor",
    "0x00403f80": "CResourceDescriptor__dtor",
    "0x00452da0": "SharedVFunc__NoOp_Ret08",
    "0x004d8410": "CRound__Init",
    "0x004d82a0": "VFuncSlot_15_004d82a0",
    "0x004d8350": "CRound__scalar_deleting_dtor",
    "0x004d8dc0": "VFuncSlot_02_004d8dc0",
    "0x004d9ef0": "CRound__UpdateRoundAndTriggerLaunchEffect",
    "0x004db630": "CRound__ArmProjectileAndSpawnTrailEffect",
    "0x0050f7a0": "CWorldPhysicsManager__CreateProjectile",
    "0x005164b0": "CResourceDescriptorTable__InstantiateChain",
    "0x00516580": "PCRTID__CreateObject",
}

EXPECTED_XREFS = {
    ("xrefs.tsv", "0x004baae0", "0x005e3bc8", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x004bac10", "0x005e3cc0", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x0050f8b0", "0x005e3ba8", "<no_function>", "DATA"),
    ("xrefs.tsv", "0x0050f8d0", "0x0050f8b3", "CMissile__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x00452da0", "0x004bac2b", "CMissile__DispatchLinkedObjectVFunc68AndPostHook", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x004d8410", "0x004babf6", "CMissile__Init", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x004d8410", "0x005de850", "<no_function>", "DATA"),
    ("context-xrefs.tsv", "0x004d8dc0", "0x005e3bac", "<no_function>", "DATA"),
    ("context-xrefs.tsv", "0x004d9ef0", "0x005e3cb8", "<no_function>", "DATA"),
    ("context-xrefs.tsv", "0x004db630", "0x004d9ef3", "CRound__UpdateRoundAndTriggerLaunchEffect", "UNCONDITIONAL_CALL"),
    ("context-xrefs.tsv", "0x00516580", "0x004babae", "CMissile__Init", "UNCONDITIONAL_CALL"),
}

EXPECTED_INSTRUCTIONS = {
    ("instructions.tsv", "0x004bab14", "PUSH", "0x6309c0", "CMissile__Init"),
    ("instructions.tsv", "0x004bab19", "PUSH", "0x61", "CMissile__Init"),
    ("instructions.tsv", "0x004bab1b", "PUSH", "0x428", "CMissile__Init"),
    ("instructions.tsv", "0x004babae", "CALL", "0x00516580", "CMissile__Init"),
    ("instructions.tsv", "0x004babbc", "MOV", "[EDX + 0x30]", "CMissile__Init"),
    ("instructions.tsv", "0x004babc7", "CALL", "[EDX + 0x4]", "CMissile__Init"),
    ("instructions.tsv", "0x004babf6", "CALL", "0x004d8410", "CMissile__Init"),
    ("instructions.tsv", "0x004bac1d", "MOV", "[ESI + 0x30]", "CMissile__DispatchLinkedObjectVFunc68AndPostHook"),
    ("instructions.tsv", "0x004bac24", "CALL", "[EAX + 0x68]", "CMissile__DispatchLinkedObjectVFunc68AndPostHook"),
    ("instructions.tsv", "0x004bac2b", "CALL", "0x00452da0", "CMissile__DispatchLinkedObjectVFunc68AndPostHook"),
    ("instructions.tsv", "0x004bac33", "RET", "0x8", "CMissile__DispatchLinkedObjectVFunc68AndPostHook"),
    ("instructions.tsv", "0x0050f8b3", "CALL", "0x0050f8d0", "CMissile__scalar_deleting_dtor"),
    ("instructions.tsv", "0x0050f8cd", "RET", "0x4", "CMissile__scalar_deleting_dtor"),
    ("instructions.tsv", "0x0050f90f", "CALL", "0x004e5bd0", "CMissile__Destructor"),
    ("instructions.tsv", "0x0050f933", "CALL", "0x004e5bd0", "CMissile__Destructor"),
    ("instructions.tsv", "0x0050f943", "CALL", "0x004cb050", "CMissile__Destructor"),
    ("instructions.tsv", "0x0050f952", "CALL", "0x004013d0", "CMissile__Destructor"),
}

EXPECTED_VTABLE_SLOTS = {
    ("005e3ba4", "1", "0050f8b0", "CMissile__scalar_deleting_dtor"),
    ("005e3ba4", "2", "004d8dc0", "VFuncSlot_02_004d8dc0"),
    ("005e3ba8", "0", "0050f8b0", "CMissile__scalar_deleting_dtor"),
    ("005e3ba8", "1", "004d8dc0", "VFuncSlot_02_004d8dc0"),
    ("005e3bc8", "0", "004baae0", "CMissile__Init"),
    ("005e3bc8", "6", "004d82a0", "VFuncSlot_15_004d82a0"),
    ("005e3cb8", "0", "004d9ef0", "CRound__UpdateRoundAndTriggerLaunchEffect"),
    ("005e3cb8", "2", "004bac10", "CMissile__DispatchLinkedObjectVFunc68AndPostHook"),
    ("005e3cc0", "0", "004bac10", "CMissile__DispatchLinkedObjectVFunc68AndPostHook"),
    ("005e3cc0", "7", "004de700", "Return1f"),
    ("005de82c", "1", "004d8350", "CRound__scalar_deleting_dtor"),
    ("005de82c", "2", "004d8dc0", "VFuncSlot_02_004d8dc0"),
}

DECOMPILE_TOKENS = {
    "decompile/004baae0_CMissile__Init.c": ("0x428", "PCRTID__CreateObject", "this + 0x30", "CRound__Init"),
    "decompile/004bac10_CMissile__DispatchLinkedObjectVFunc68AndPostHook.c": ("this + 0x30", "+ 0x68", "SharedVFunc__NoOp_Ret08"),
    "decompile/0050f8b0_CMissile__scalar_deleting_dtor.c": ("CMissile__Destructor", "delete_flags & 1"),
    "decompile/0050f8d0_CMissile__Destructor.c": ("this + 0xec", "this + 0xe8", "this + 0xe0", "CActor__dtor_base"),
    "context-decompile/0050f7a0_CWorldPhysicsManager__CreateProjectile.c": ("CRound__ctor", "PTR_LAB_005e3ba4"),
    "context-decompile/004d8410_CRound__Init.c": ("CActor__Init", "CRound__SelectBestTargetReaderAndSyncAimState"),
}

CORE_TOKENS = (
    "Wave941",
    "missile-linked-object-dispatch-review-wave941",
    "179/1408 = 12.71%",
    "6113/6113 = 100.00%",
    BACKUP,
    "read-only review",
    "0x004baae0 CMissile__Init",
    "0x004bac10 CMissile__DispatchLinkedObjectVFunc68AndPostHook",
    "0x0050f8b0 CMissile__scalar_deleting_dtor",
    "0x0050f8d0 CMissile__Destructor",
    "0x0050f7a0 CWorldPhysicsManager__CreateProjectile",
    "0x004d8410 CRound__Init",
    "0x00452da0 SharedVFunc__NoOp_Ret08",
    "0x005e3ba4",
    "0x005e3ba8",
    "0x005e3bc8",
    "0x005e3cb8",
    "0x005e3cc0",
    "0x005de82c",
    "0x005de850",
)

OVERCLAIMS = (
    "runtime missile payload behavior proven",
    "runtime projectile behavior proven",
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
        "metadata.tsv": 4,
        "tags.tsv": 4,
        "xrefs.tsv": 4,
        "instructions.tsv": 168,
        "decompile/index.tsv": 4,
        "context-metadata.tsv": 12,
        "context-tags.tsv": 12,
        "context-xrefs.tsv": 103,
        "context-instructions.tsv": 931,
        "context-decompile/index.tsv": 12,
        "vtable-slots.tsv": 48,
    }
    for rel, count in expected_counts.items():
        require(len(read_tsv(BASE / rel)) == count, f"{rel} row count mismatch", failures)

    metadata = row_map(BASE / "metadata.tsv")
    decomp = row_map(BASE / "decompile" / "index.tsv")
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
        "metadata.log": "targets=4 found=4 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "xrefs.log": "Wrote 4 rows",
        "instructions.log": "Wrote 168 function-body instruction rows",
        "decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "context-metadata.log": "targets=12 found=12 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "context-xrefs.log": "Wrote 103 rows",
        "context-instructions.log": "Wrote 931 function-body instruction rows",
        "context-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=6 rows=48",
    }
    for rel, token in expected_logs.items():
        text = read_text(BASE / rel)
        require(token in text, f"missing log token {rel}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIGNATURE:", "FAIL:", "failed=1", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected log failure {rel}: {bad}", failures)

    for mutation_log in ("apply-dry.log", "apply.log", "apply-final-dry.log"):
        require(not (BASE / mutation_log).exists(), f"unexpected mutation log present: {mutation_log}", failures)

    backup = json.loads(read_text(BASE / "backup-summary.json"))
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = json.loads(read_text(PACKAGE_JSON))
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)

    docs = [NOTE, CAMPAIGN, GHIDRA_REFERENCE, MISSILE_DOC, ROUND_DOC, WORLDPHYS_DOC, *STATE_FILES]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    reference = read_text(GHIDRA_REFERENCE)
    require("VTable_005e3cc0__Slot00_Dispatch68_AndPostHook" not in reference, "stale 0x004bac10 neutral table label remains", failures)
    require("CMissile__VFunc_01_0050f8b0" not in reference, "stale CMissile vfunc wrapper wording remains", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave941 missile linked-object dispatch review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave941 missile linked-object dispatch review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
