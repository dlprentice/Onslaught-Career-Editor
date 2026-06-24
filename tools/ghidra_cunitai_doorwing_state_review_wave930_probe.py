#!/usr/bin/env python3
"""Validate Wave930 CUnitAI door-wing state read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave930-cunitai-doorwing-state-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cunitai_doorwing_state_review_wave930_2026-05-27.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"G:\GhidraBackups\BEA_20260527-233937_post_wave930_cunitai_doorwing_state_review_verified"
SCRIPT_NAME = "test:ghidra-cunitai-doorwing-state-review-wave930"
SCRIPT_VALUE = r"py -3 tools\ghidra_cunitai_doorwing_state_review_wave930_probe.py --check"

TARGETS = {
    "0x00447a40": ("CUnitAI__SetDoorWingState2AndClampYawDelta", "void __fastcall CUnitAI__SetDoorWingState2AndClampYawDelta(void * unitAI)"),
    "0x00447ac0": ("CUnitAI__PlayWingFoldedAnimationAndSetState3", "void __fastcall CUnitAI__PlayWingFoldedAnimationAndSetState3(void * unitAI)"),
    "0x00447fa0": ("CUnitAI__AdvanceDoorWingAnimationState", "int __fastcall CUnitAI__AdvanceDoorWingAnimationState(void * unitAI)"),
    "0x00448110": ("CUnitAI__SetDoorWingState6", "void __fastcall CUnitAI__SetDoorWingState6(void * unitAI)"),
    "0x00448120": ("CUnitAI__SetDoorWingState7AndMirrorYawOffset", "void __fastcall CUnitAI__SetDoorWingState7AndMirrorYawOffset(void * unitAI)"),
}

CONTEXT_TARGETS = {
    "0x00447b10": ("CUnitAI__PlayWingUnfoldedAnimationAndSetState5", "void __fastcall CUnitAI__PlayWingUnfoldedAnimationAndSetState5(void * unitAI)"),
    "0x00447b60": ("CUnitAI__HasReachedCachedAnchorPoint", "int __fastcall CUnitAI__HasReachedCachedAnchorPoint(void * unitAI)"),
    "0x00447bb0": ("CUnitAI__GetOrGenerateCachedAnchorPoint", "void __thiscall CUnitAI__GetOrGenerateCachedAnchorPoint(void * this, void * outAnchorPoint)"),
    "0x00447d50": ("CUnitAI__IsCachedAnchorPointValid", "int __fastcall CUnitAI__IsCachedAnchorPointValid(void * unitAI)"),
    "0x004480c0": ("CUnitAI__CanContinueDoorWingTransition", "bool __fastcall CUnitAI__CanContinueDoorWingTransition(void * unitAi)"),
}

COMPARISON_TARGETS = {
    "0x00445610": ("CUnitAI__AdvanceOpenCloseShootAnimationState", "int __fastcall CUnitAI__AdvanceOpenCloseShootAnimationState(void * unitAI)"),
}

EXPECTED_XREFS = {
    "xrefs.tsv": {
        "0x00447a40": {("0x005e1fb0", "<no_function>", "DATA")},
        "0x00447ac0": {("0x005e1fb4", "<no_function>", "DATA")},
        "0x00447fa0": {("0x005e1ec4", "<no_function>", "DATA")},
        "0x00448110": {("0x004486dc", "<no_function>", "UNCONDITIONAL_CALL")},
        "0x00448120": {("0x00448737", "<no_function>", "UNCONDITIONAL_CALL")},
    },
    "context-xrefs.tsv": {
        "0x00447b10": {("0x005e1fb8", "<no_function>", "DATA")},
        "0x00447b60": {("0x0044866d", "<no_function>", "UNCONDITIONAL_CALL")},
        "0x00447bb0": {("0x00448690", "<no_function>", "UNCONDITIONAL_CALL")},
        "0x00447d50": {
            ("0x00447a57", "CUnitAI__SetDoorWingState2AndClampYawDelta", "UNCONDITIONAL_CALL"),
            ("0x00447c3d", "CUnitAI__GetOrGenerateCachedAnchorPoint", "UNCONDITIONAL_CALL"),
            ("0x00447cf7", "CUnitAI__GetOrGenerateCachedAnchorPoint", "UNCONDITIONAL_CALL"),
        },
        "0x004480c0": {("0x004486bf", "<no_function>", "UNCONDITIONAL_CALL")},
    },
    "comparison-xrefs.tsv": {
        "0x00445610": {("0x005e1328", "<no_function>", "DATA")},
    },
}

EXPECTED_VTABLE_SLOTS = {
    ("0x005e11b0", "94"): ("0x00445610", "CUnitAI__AdvanceOpenCloseShootAnimationState"),
    ("0x005e1e7c", "18"): ("0x00447fa0", "CUnitAI__AdvanceDoorWingAnimationState"),
    ("0x005e1e7c", "77"): ("0x00447a40", "CUnitAI__SetDoorWingState2AndClampYawDelta"),
    ("0x005e1e7c", "78"): ("0x00447ac0", "CUnitAI__PlayWingFoldedAnimationAndSetState3"),
    ("0x005e1e7c", "79"): ("0x00447b10", "CUnitAI__PlayWingUnfoldedAnimationAndSetState5"),
}

STRING_EXPECTATIONS = {
    "string-00628a98.tsv": "dooropening",
    "string-00628a8c.tsv": "doorclosing",
    "string-00628a80.tsv": "doorclosed",
    "string-00628aa4.tsv": "wingfolded",
    "string-00628ab0.tsv": "wingunfolded",
    "string-00628a74.tsv": "wingflat",
    "string-00628ac0.tsv": "dooropen",
    "string-00623bb4.tsv": "open",
    "string-006289e4.tsv": "close",
    "string-006289ec.tsv": "shoot",
    "string-0062359c.tsv": "fly",
}

DECOMPILE_TOKENS = {
    "decompile/00447a40_CUnitAI__SetDoorWingState2AndClampYawDelta.c": ("0x290", "0x294", "0x27c", "0x2a0", "CUnitAI__IsCachedAnchorPointValid"),
    "decompile/00447ac0_CUnitAI__PlayWingFoldedAnimationAndSetState3.c": ("0x27c", "0x290", "s_wingfolded_00628aa4", "0xf0"),
    "decompile/00447fa0_CUnitAI__AdvanceDoorWingAnimationState.c": (
        "s_dooropening_00628a98",
        "s_doorclosing_00628a8c",
        "s_doorclosed_00628a80",
        "s_wingfolded_00628aa4",
        "s_wingunfolded_00628ab0",
        "s_wingflat_00628a74",
        "s_dooropen_00628ac0",
        "0x27c",
        "0xf0",
    ),
    "decompile/00448110_CUnitAI__SetDoorWingState6.c": ("0x27c", "= 6"),
    "decompile/00448120_CUnitAI__SetDoorWingState7AndMirrorYawOffset.c": ("0x27c", "0x2a4", "_DAT_005d8568"),
    "context-decompile/00447b10_CUnitAI__PlayWingUnfoldedAnimationAndSetState5.c": ("s_wingunfolded_00628ab0", "0x27c", "0xf0"),
    "context-decompile/00447b60_CUnitAI__HasReachedCachedAnchorPoint.c": ("0x290", "0x280", "0x284", "SQRT"),
    "context-decompile/00447bb0_CUnitAI__GetOrGenerateCachedAnchorPoint.c": ("0x280", "0x284", "0x290", "CUnitAI__IsCachedAnchorPointValid"),
    "context-decompile/00447d50_CUnitAI__IsCachedAnchorPointValid.c": ("CMapWho__GetNextEntryWithinRadius", "CStaticShadows__SampleShadowHeightBilinear", "0x27c"),
    "context-decompile/004480c0_CUnitAI__CanContinueDoorWingTransition.c": ("0x294", "0x144"),
    "comparison-decompile/00445610_CUnitAI__AdvanceOpenCloseShootAnimationState.c": ("0x280", "s_shoot_006289ec", "s_close_006289e4", "PTR_DAT_0062359c", "0xf0"),
}

CORE_TOKENS = (
    "Wave930",
    "cunitai-doorwing-state-review-wave930",
    "116/1408 = 8.24%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x00447a40 CUnitAI__SetDoorWingState2AndClampYawDelta",
    "0x00447ac0 CUnitAI__PlayWingFoldedAnimationAndSetState3",
    "0x00447fa0 CUnitAI__AdvanceDoorWingAnimationState",
    "0x00448110 CUnitAI__SetDoorWingState6",
    "0x00448120 CUnitAI__SetDoorWingState7AndMirrorYawOffset",
    "0x00447b10 CUnitAI__PlayWingUnfoldedAnimationAndSetState5",
    "0x004480c0 CUnitAI__CanContinueDoorWingTransition",
    "0x00445610 CUnitAI__AdvanceOpenCloseShootAnimationState",
    "0x005e11b0",
    "0x005e1e7c",
)

OVERCLAIMS = (
    "runtime door-wing behavior proven",
    "runtime targeting behavior proven",
    "unified door-wing fsm proven",
    "unified animation fsm proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
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


def check_counts_and_logs(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 5,
        "tags.tsv": 5,
        "xrefs.tsv": 5,
        "instructions.tsv": 164,
        "decompile/index.tsv": 5,
        "context-metadata.tsv": 5,
        "context-tags.tsv": 5,
        "context-xrefs.tsv": 7,
        "context-instructions.tsv": 355,
        "context-decompile/index.tsv": 5,
        "comparison-metadata.tsv": 1,
        "comparison-tags.tsv": 1,
        "comparison-xrefs.tsv": 1,
        "comparison-instructions.tsv": 73,
        "comparison-decompile/index.tsv": 1,
        "vtable-slots.tsv": 256,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    expected_logs = {
        "metadata.log": "targets=5 found=5 missing=0",
        "tags.log": "rows=5 missing=0",
        "xrefs.log": "Wrote 5 rows",
        "instructions.log": "Wrote 164 function-body instruction rows",
        "decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "context-metadata.log": "targets=5 found=5 missing=0",
        "context-tags.log": "rows=5 missing=0",
        "context-xrefs.log": "Wrote 7 rows",
        "context-instructions.log": "Wrote 355 function-body instruction rows",
        "context-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "comparison-metadata.log": "targets=1 found=1 missing=0",
        "comparison-tags.log": "rows=1 missing=0",
        "comparison-xrefs.log": "Wrote 1 rows",
        "comparison-instructions.log": "Wrote 73 function-body instruction rows",
        "comparison-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=2 rows=256",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_metadata(target_file: str, expected: dict[str, tuple[str, str]], failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / target_file)}
    for address, (name, signature) in expected.items():
        row = rows.get(address)
        require(row is not None, f"missing metadata row {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch {address}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
        require(row.get("comment", "").strip(), f"missing comment {address}", failures)


def check_xrefs(failures: list[str]) -> None:
    for relative, expected_by_target in EXPECTED_XREFS.items():
        actual: dict[str, set[tuple[str, str, str]]] = {}
        for row in read_tsv(BASE / relative):
            key = normalize_address(row["target_addr"])
            actual.setdefault(key, set()).add((normalize_address(row["from_addr"]), row["from_function"], row["ref_type"]))
        for target, expected in expected_by_target.items():
            require(expected.issubset(actual.get(target, set())), f"xref mismatch for {target} in {relative}", failures)


def check_vtables_and_strings(failures: list[str]) -> None:
    rows = {
        (normalize_address(row["vtable"]), row["slot_index"]): row
        for row in read_tsv(BASE / "vtable-slots.tsv")
    }
    for key, (entry, name) in EXPECTED_VTABLE_SLOTS.items():
        row = rows.get((normalize_address(key[0]), key[1]))
        require(row is not None, f"missing vtable slot {key}", failures)
        if row is None:
            continue
        require(normalize_address(row.get("function_entry", "")) == entry, f"vtable entry mismatch {key}", failures)
        require(row.get("function_name") == name, f"vtable name mismatch {key}", failures)
        require(row.get("status") == "OK", f"vtable status mismatch {key}", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"string mismatch {relative}", failures)


def check_decompile_tokens(failures: list[str]) -> None:
    for relative, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / relative)
        require(text, f"missing decompile file {relative}", failures)
        for token in tokens:
            require(token in text, f"missing decompile token {relative}: {token}", failures)


def check_docs_and_state(failures: list[str]) -> None:
    package = json.loads(read_text(PACKAGE_JSON))
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)

    for path in [NOTE, CAMPAIGN, UNIT_DOC, *STATE_FILES]:
        text = read_text(path)
        require(text, f"missing doc/state file {path.relative_to(ROOT)}", failures)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    backup = json.loads(read_text(BASE / "backup-summary.json"))
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173247367, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts_and_logs(failures)
    check_metadata("metadata.tsv", TARGETS, failures)
    check_metadata("context-metadata.tsv", CONTEXT_TARGETS, failures)
    check_metadata("comparison-metadata.tsv", COMPARISON_TARGETS, failures)
    check_xrefs(failures)
    check_vtables_and_strings(failures)
    check_decompile_tokens(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave930 CUnitAI door-wing state review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave930 CUnitAI door-wing state review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
