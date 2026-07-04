#!/usr/bin/env python3
"""Validate Wave927 CUnit active-reader targeting read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave927-cunit-active-reader-targeting-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cunit_active_reader_targeting_review_wave927_2026-05-27.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
SQUAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadNormal.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified"
SCRIPT_NAME = "test:ghidra-cunit-active-reader-targeting-review-wave927"
SCRIPT_VALUE = r"py -3 tools\ghidra_cunit_active_reader_targeting_review_wave927_probe.py --check"

TARGETS = {
    "0x00428b50": (
        "CUnit__SetReaderAndComputeRelativeYaw",
        "void __thiscall CUnit__SetReaderAndComputeRelativeYaw(void * this, void * reader, void * readerContext, int unusedMode)",
    ),
    "0x00428bc0": (
        "CUnitAI__GetTargetHeadingWithOffset",
        "double __fastcall CUnitAI__GetTargetHeadingWithOffset(void * this)",
    ),
    "0x00429270": (
        "CUnitAI__UpdateHeadingTowardTargetClamped",
        "void __fastcall CUnitAI__UpdateHeadingTowardTargetClamped(void * turnContext)",
    ),
    "0x004e97e0": (
        "CGenericActiveReader__SwapWithCandidateIfFormationCloser",
        "bool __thiscall CGenericActiveReader__SwapWithCandidateIfFormationCloser(void * this, void * candidate_reader)",
    ),
    "0x004fd3d0": (
        "CUnit__IsCandidateSideCompatibleForTargeting",
        "bool __thiscall CUnit__IsCandidateSideCompatibleForTargeting(void * this, int candidate_side)",
    ),
}

CONTEXT_TARGET = {
    "0x004fb650": (
        "CUnit__ForwardAimTransformAndAttachTargetReader",
        "void __thiscall CUnit__ForwardAimTransformAndAttachTargetReader(void * this, void * target_transform, void * target_reader)",
    )
}

EXPECTED_XREFS = {
    "0x00428b50": {("0x004f8d7c", "CUnit__Init", "UNCONDITIONAL_CALL")},
    "0x00428bc0": {("0x004292c7", "CUnitAI__UpdateHeadingTowardTargetClamped", "UNCONDITIONAL_CALL")},
    "0x00429270": {("0x005d9660", "<no_function>", "DATA")},
    "0x004e97e0": {("0x004e8640", "CSquadNormal__ResolveFormationSlotConflicts", "UNCONDITIONAL_CALL")},
    "0x004fd3d0": {
        ("0x0040b8c2", "CBattleEngine__HandleAutoAim", "UNCONDITIONAL_CALL"),
        ("0x00406902", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
        ("0x004dae48", "CRound__SelectBestTargetReaderAndSyncAimState", "UNCONDITIONAL_CALL"),
        ("0x004fe05c", "CUnit__TriggerEffect", "UNCONDITIONAL_CALL"),
    },
}

EXPECTED_CONTEXT_XREFS = {
    "0x004fb650": {
        ("0x0047b061", "CGillMHeadAI__UpdateAimTransformAndTargetReader", "UNCONDITIONAL_CALL"),
        ("0x004ff18b", "CWarspite__Update", "UNCONDITIONAL_CALL"),
    }
}

CORE_TOKENS = (
    "Wave927",
    "cunit-active-reader-targeting-review-wave927",
    "103/1408 = 7.32%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x00428b50",
    "0x00428bc0",
    "0x00429270",
    "0x004e97e0",
    "0x004fd3d0",
    "0x004fb650",
)

OVERCLAIMS = (
    "runtime targeting behavior proven",
    "runtime steering behavior proven",
    "runtime formation behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
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


def check_function_rows(
    rows: list[dict[str, str]],
    decomp_rows: list[dict[str, str]],
    tags: list[dict[str, str]],
    expected: dict[str, tuple[str, str]],
    failures: list[str],
) -> None:
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


def actual_xrefs(rows: list[dict[str, str]]) -> dict[str, set[tuple[str, str, str]]]:
    result: dict[str, set[tuple[str, str, str]]] = {}
    for row in rows:
        target = normalized(row.get("target_addr", ""))
        result.setdefault(target, set()).add(
            (normalized(row.get("from_addr", "")), row.get("from_function", ""), row.get("ref_type", ""))
        )
    return result


def check_xrefs(
    rows: list[dict[str, str]],
    expected: dict[str, set[tuple[str, str, str]]],
    failures: list[str],
) -> None:
    actual = actual_xrefs(rows)
    for addr, expected_rows in expected.items():
        want = {(normalized(from_addr), func, ref_type) for from_addr, func, ref_type in expected_rows}
        got = actual.get(normalized(addr), set())
        require(want.issubset(got), f"xref mismatch for {addr}: {want - got}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=5 found=5 missing=0",
        "tags.log": "rows=5 missing=0",
        "xrefs.log": "Wrote 23 rows",
        "instructions.log": "Wrote 464 function-body instruction rows",
        "decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "context-metadata.log": "targets=1 found=1 missing=0",
        "context-tags.log": "rows=1 missing=0",
        "context-xrefs.log": "Wrote 13 rows",
        "context-instructions.log": "Wrote 9 function-body instruction rows",
        "context-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
    }
    for log_name, token in expected.items():
        text = read_text(BASE / log_name)
        require(token in text, f"missing log token in {log_name}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {log_name}: {bad}", failures)


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
    summary = json.loads(read_text(BASE / "wave927-cunit-active-reader-targeting-review.json") or "{}")
    backup = json.loads(read_text(BASE / "backup-summary.json") or "{}")

    require(len(metadata) == 5, "metadata row count mismatch", failures)
    require(len(tags) == 5, "tag row count mismatch", failures)
    require(len(xrefs) == 23, "xref row count mismatch", failures)
    require(len(instructions) == 464, "instruction row count mismatch", failures)
    require(len(decomp) == 5, "decompile row count mismatch", failures)
    require(len(context_metadata) == 1, "context metadata row count mismatch", failures)
    require(len(context_tags) == 1, "context tag row count mismatch", failures)
    require(len(context_xrefs) == 13, "context xref row count mismatch", failures)
    require(len(context_instructions) == 9, "context instruction row count mismatch", failures)
    require(len(context_decomp) == 1, "context decompile row count mismatch", failures)

    check_function_rows(metadata, decomp, tags, TARGETS, failures)
    check_function_rows(context_metadata, context_decomp, context_tags, CONTEXT_TARGET, failures)
    check_xrefs(xrefs, EXPECTED_XREFS, failures)
    check_xrefs(context_xrefs, EXPECTED_CONTEXT_XREFS, failures)
    check_logs(failures)

    require(summary.get("progress") == "103/1408 = 7.32%", "summary progress mismatch", failures)
    require(summary.get("staticClosure") == "6113/6113 = 100.00%", "summary closure mismatch", failures)
    require(summary.get("mutation") == "none; read-only review", "summary mutation mismatch", failures)
    counts = summary.get("evidenceCounts", {})
    require(counts.get("primaryInstructionRows") == 464, "summary primary instruction count mismatch", failures)
    require(counts.get("contextInstructionRows") == 9, "summary context instruction count mismatch", failures)

    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173247367, 173247367.0), "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)

    for path in [NOTE, CAMPAIGN, UNIT_DOC, SQUAD_DOC, *STATE_FILES]:
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
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    report = build_report()
    report_path = BASE / "wave927-probe-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Ghidra Wave927 CUnit active-reader targeting review probe")
    print(f"Status: {report['status']}")
    print(f"Output: {report_path.relative_to(ROOT)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
