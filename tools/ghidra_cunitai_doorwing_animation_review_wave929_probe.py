#!/usr/bin/env python3
"""Validate Wave929 CUnitAI door-wing animation read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave929-cunitai-doorwing-animation-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cunitai_doorwing_animation_review_wave929_2026-05-27.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"G:\GhidraBackups\BEA_20260527-231046_post_wave929_cunitai_doorwing_animation_review_verified"
SCRIPT_NAME = "test:ghidra-cunitai-doorwing-animation-review-wave929"
SCRIPT_VALUE = r"py -3 tools\ghidra_cunitai_doorwing_animation_review_wave929_probe.py --check"

TARGETS = {
    "0x00445570": ("CUnitAI__PlayOpenAnimationIfState1Or3", "void __fastcall CUnitAI__PlayOpenAnimationIfState1Or3(void * unitAI)"),
    "0x004455c0": ("CUnitAI__PlayCloseAnimationIfState0Or2", "void __fastcall CUnitAI__PlayCloseAnimationIfState0Or2(void * unitAI)"),
    "0x00445610": ("CUnitAI__AdvanceOpenCloseShootAnimationState", "int __fastcall CUnitAI__AdvanceOpenCloseShootAnimationState(void * unitAI)"),
}

CONTEXT_TARGETS = {
    "0x00445ad0": ("CUnitAI__UpdateDoorWingEngagement_CloseRange", "double __fastcall CUnitAI__UpdateDoorWingEngagement_CloseRange(void * doorWingAI)"),
    "0x00445f40": ("CUnitAI__UpdateDoorWingEngagement_MidRange", "double __fastcall CUnitAI__UpdateDoorWingEngagement_MidRange(void * doorWingAI)"),
    "0x00446150": ("CUnitAI__UpdateDoorWingEngagement_LongRange", "double __fastcall CUnitAI__UpdateDoorWingEngagement_LongRange(void * doorWingAI)"),
    "0x00446400": ("CUnitAI__EnterDoorWingOpenTrackingState", "void __fastcall CUnitAI__EnterDoorWingOpenTrackingState(void * doorWingAI)"),
}

COMPARISON_TARGETS = {
    "0x00447fa0": ("CUnitAI__AdvanceDoorWingAnimationState", "int __fastcall CUnitAI__AdvanceDoorWingAnimationState(void * unitAI)"),
}

EXPECTED_XREFS = {
    "0x00445570": {
        ("0x00445d84", "CUnitAI__UpdateDoorWingEngagement_CloseRange", "UNCONDITIONAL_CALL"),
        ("0x00446445", "CUnitAI__EnterDoorWingOpenTrackingState", "UNCONDITIONAL_CALL"),
    },
    "0x004455c0": {
        ("0x00445c3a", "CUnitAI__UpdateDoorWingEngagement_CloseRange", "UNCONDITIONAL_CALL"),
        ("0x004462bb", "CUnitAI__UpdateDoorWingEngagement_LongRange", "UNCONDITIONAL_CALL"),
    },
    "0x00445610": {
        ("0x005e1328", "<no_function>", "DATA"),
    },
}

EXPECTED_CONTEXT_XREFS = {
    "0x00445ad0": {("0x00445a8e", "<no_function>", "UNCONDITIONAL_CALL")},
    "0x00445f40": {("0x00445a85", "<no_function>", "UNCONDITIONAL_CALL")},
    "0x00446150": {("0x00445a7c", "<no_function>", "UNCONDITIONAL_CALL")},
    "0x00446400": {("0x004463b6", "CUnitAI__UpdateDoorWingEngagement_LongRange", "UNCONDITIONAL_CALL")},
}

EXPECTED_COMPARISON_XREFS = {
    "0x00447fa0": {("0x005e1ec4", "<no_function>", "DATA")},
}

EXPECTED_VTABLE_SLOTS = {
    ("0x005e11b0", "94"): ("0x00445610", "CUnitAI__AdvanceOpenCloseShootAnimationState"),
    ("0x005e1e7c", "18"): ("0x00447fa0", "CUnitAI__AdvanceDoorWingAnimationState"),
}

STRING_EXPECTATIONS = {
    "string-00623bb4.tsv": "open",
    "string-006289e4.tsv": "close",
    "string-006289ec.tsv": "shoot",
    "string-0062359c.tsv": "fly",
}

DECOMPILE_TOKENS = {
    "0x00445570": ("0x280", "0xf0", "DAT_00623bb4"),
    "0x004455c0": ("0x280", "0xf0", "s_close_006289e4"),
    "0x00445610": ("0x280", "0xf0", "s_shoot_006289ec", "PTR_DAT_0062359c"),
}

CORE_TOKENS = (
    "Wave929",
    "cunitai-doorwing-animation-review-wave929",
    "111/1408 = 7.88%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x00445570",
    "0x004455c0",
    "0x00445610",
    "0x00445ad0",
    "0x00445f40",
    "0x00446150",
    "0x00446400",
    "0x00447fa0",
    "0x005e11b0",
    "0x005e1e7c",
)

OVERCLAIMS = (
    "runtime door-wing animation behavior proven",
    "runtime targeting behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "unified animation fsm proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalized(addr: str) -> str:
    value = (addr or "").lower().strip()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_addr(rows: list[dict[str, str]], addr: str) -> dict[str, str]:
    want = normalized(addr)
    for row in rows:
        got = row.get("address") or row.get("target_addr") or row.get("function_entry") or ""
        if normalized(got) == want:
            return row
    return {}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_function_rows(rows, decomp_rows, tags, expected, failures) -> None:
    for addr, (name, signature) in expected.items():
        mrow = row_by_addr(rows, addr)
        require(mrow.get("name") == name, f"metadata name mismatch for {addr}", failures)
        require(mrow.get("signature") == signature, f"metadata signature mismatch for {addr}", failures)
        require(mrow.get("status") == "OK", f"metadata status mismatch for {addr}", failures)
        drow = row_by_addr(decomp_rows, addr)
        require(drow.get("name") == name, f"decompile name mismatch for {addr}", failures)
        require(drow.get("signature") == signature, f"decompile signature mismatch for {addr}", failures)
        require(drow.get("status") == "OK", f"decompile status mismatch for {addr}", failures)
        require(row_by_addr(tags, addr).get("status") == "OK", f"tag status mismatch for {addr}", failures)


def check_xrefs(rows, expected, failures) -> None:
    actual: dict[str, set[tuple[str, str, str]]] = {}
    for row in rows:
        actual.setdefault(normalized(row.get("target_addr", "")), set()).add(
            (normalized(row.get("from_addr", "")), row.get("from_function", ""), row.get("ref_type", ""))
        )
    for addr, expected_rows in expected.items():
        want = {(normalized(from_addr), func, ref_type) for from_addr, func, ref_type in expected_rows}
        got = actual.get(normalized(addr), set())
        require(want.issubset(got), f"xref mismatch for {addr}: {want - got}", failures)


def check_strings(failures: list[str]) -> None:
    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(len(rows) == 1, f"{relative} row count mismatch", failures)
        if rows:
            require(rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)


def check_decompile_tokens(failures: list[str]) -> None:
    for addr, tokens in DECOMPILE_TOKENS.items():
        name = TARGETS[addr][0]
        decompile_path = BASE / "decompile" / f"{normalized(addr)[2:]}_{name}.c"
        text = read_text(decompile_path)
        for token in tokens:
            require(token in text, f"missing decompile token for {addr}: {token}", failures)

    comparison_text = read_text(BASE / "comparison-decompile" / "00447fa0_CUnitAI__AdvanceDoorWingAnimationState.c")
    for token in ("0x27c", "0xf0", "s_dooropening_00628a98", "s_doorclosing_00628a8c", "s_wingfolded_00628aa4"):
        require(token in comparison_text, f"missing comparison decompile token: {token}", failures)


def check_vtable_slots(failures: list[str]) -> None:
    rows = read_tsv(BASE / "vtable-slots.tsv")
    actual = {(normalized(row.get("vtable", "")), row.get("slot_index", "")): row for row in rows}
    for (vtable, slot), (entry, name) in EXPECTED_VTABLE_SLOTS.items():
        row = actual.get((normalized(vtable), slot), {})
        require(normalized(row.get("function_entry", "")) == entry, f"vtable function entry mismatch for {vtable} slot {slot}", failures)
        require(row.get("function_name") == name, f"vtable function name mismatch for {vtable} slot {slot}", failures)


def build_report() -> dict[str, object]:
    failures: list[str] = []
    metadata = read_tsv(BASE / "metadata.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    xrefs = read_tsv(BASE / "xrefs.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")
    decomp = read_tsv(BASE / "decompile" / "index.tsv")
    context_metadata = read_tsv(BASE / "context-metadata.tsv")
    context_tags = read_tsv(BASE / "context-tags.tsv")
    context_xrefs = read_tsv(BASE / "context-xrefs.tsv")
    context_instructions = read_tsv(BASE / "context-instructions.tsv")
    context_decomp = read_tsv(BASE / "context-decompile" / "index.tsv")
    comparison_metadata = read_tsv(BASE / "comparison-metadata.tsv")
    comparison_tags = read_tsv(BASE / "comparison-tags.tsv")
    comparison_xrefs = read_tsv(BASE / "comparison-xrefs.tsv")
    comparison_instructions = read_tsv(BASE / "comparison-instructions.tsv")
    comparison_decomp = read_tsv(BASE / "comparison-decompile" / "index.tsv")
    vtable_slots = read_tsv(BASE / "vtable-slots.tsv")
    summary = json.loads(read_text(BASE / "wave929-cunitai-doorwing-animation-review.json") or "{}")
    backup = json.loads(read_text(BASE / "backup-summary.json") or "{}")

    require(len(metadata) == 3, "metadata row count mismatch", failures)
    require(len(tags) == 3, "tag row count mismatch", failures)
    require(len(xrefs) == 5, "xref row count mismatch", failures)
    require(len(instructions) == 121, "instruction row count mismatch", failures)
    require(len(decomp) == 3, "decompile row count mismatch", failures)
    require(len(context_metadata) == 4, "context metadata row count mismatch", failures)
    require(len(context_tags) == 4, "context tag row count mismatch", failures)
    require(len(context_xrefs) == 4, "context xref row count mismatch", failures)
    require(len(context_instructions) == 770, "context instruction row count mismatch", failures)
    require(len(context_decomp) == 4, "context decompile row count mismatch", failures)
    require(len(comparison_metadata) == 1, "comparison metadata row count mismatch", failures)
    require(len(comparison_tags) == 1, "comparison tag row count mismatch", failures)
    require(len(comparison_xrefs) == 1, "comparison xref row count mismatch", failures)
    require(len(comparison_instructions) == 100, "comparison instruction row count mismatch", failures)
    require(len(comparison_decomp) == 1, "comparison decompile row count mismatch", failures)
    require(len(vtable_slots) == 256, "vtable slot row count mismatch", failures)

    check_function_rows(metadata, decomp, tags, TARGETS, failures)
    check_function_rows(context_metadata, context_decomp, context_tags, CONTEXT_TARGETS, failures)
    check_function_rows(comparison_metadata, comparison_decomp, comparison_tags, COMPARISON_TARGETS, failures)
    check_xrefs(xrefs, EXPECTED_XREFS, failures)
    check_xrefs(context_xrefs, EXPECTED_CONTEXT_XREFS, failures)
    check_xrefs(comparison_xrefs, EXPECTED_COMPARISON_XREFS, failures)
    check_strings(failures)
    check_decompile_tokens(failures)
    check_vtable_slots(failures)

    expected_logs = {
        "metadata.log": "targets=3 found=3 missing=0",
        "tags.log": "rows=3 missing=0",
        "xrefs.log": "Wrote 5 rows",
        "instructions.log": "Wrote 121 function-body instruction rows",
        "decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "context-metadata.log": "targets=4 found=4 missing=0",
        "context-tags.log": "rows=4 missing=0",
        "context-xrefs.log": "Wrote 4 rows",
        "context-instructions.log": "Wrote 770 function-body instruction rows",
        "context-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "comparison-metadata.log": "targets=1 found=1 missing=0",
        "comparison-tags.log": "rows=1 missing=0",
        "comparison-xrefs.log": "Wrote 1 rows",
        "comparison-instructions.log": "Wrote 100 function-body instruction rows",
        "comparison-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "vtable-slots.log": "targets=2 rows=256",
    }
    for log_name, token in expected_logs.items():
        text = read_text(BASE / log_name)
        require(token in text, f"missing log token in {log_name}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {log_name}: {bad}", failures)

    require(summary.get("progress") == "111/1408 = 7.88%", "summary progress mismatch", failures)
    require(summary.get("staticClosure") == "6113/6113 = 100.00%", "summary closure mismatch", failures)
    require(summary.get("mutation") == "none; read-only review", "summary mutation mismatch", failures)
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173247367, 173247367.0), "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)

    for path in [NOTE, CAMPAIGN, UNIT_DOC, *STATE_FILES]:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = json.loads(read_text(PACKAGE_JSON) or "{}")
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "package script mismatch", failures)

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "counts": {
            "metadata": len(metadata),
            "tags": len(tags),
            "xrefs": len(xrefs),
            "instructions": len(instructions),
            "decompile": len(decomp),
            "context_metadata": len(context_metadata),
            "context_tags": len(context_tags),
            "context_xrefs": len(context_xrefs),
            "context_instructions": len(context_instructions),
            "context_decompile": len(context_decomp),
            "comparison_metadata": len(comparison_metadata),
            "comparison_tags": len(comparison_tags),
            "comparison_xrefs": len(comparison_xrefs),
            "comparison_instructions": len(comparison_instructions),
            "comparison_decompile": len(comparison_decomp),
            "vtable_slots": len(vtable_slots),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    report = build_report()
    report_path = BASE / "wave929-probe-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Ghidra Wave929 CUnitAI door-wing animation review probe")
    print(f"Status: {report['status']}")
    print(f"Output: {report_path.relative_to(ROOT)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
