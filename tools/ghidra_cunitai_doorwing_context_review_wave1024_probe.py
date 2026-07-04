#!/usr/bin/env python3
"""Validate Wave1024 CUnitAI door-wing context read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1024-cunitai-doorwing-context-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cunitai_doorwing_context_review_wave1024_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1024_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
UNITAI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "UnitAI.cpp" / "_index.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-001008_post_wave1024_cunitai_doorwing_context_review_verified"

TARGETS = {
    "0x00445ad0": ("CUnitAI__UpdateDoorWingEngagement_CloseRange", "double __fastcall CUnitAI__UpdateDoorWingEngagement_CloseRange(void * doorWingAI)", ("close-range", "open/close animation")),
    "0x00445f40": ("CUnitAI__UpdateDoorWingEngagement_MidRange", "double __fastcall CUnitAI__UpdateDoorWingEngagement_MidRange(void * doorWingAI)", ("mid-range", "attached-node readiness")),
    "0x00446150": ("CUnitAI__UpdateDoorWingEngagement_LongRange", "double __fastcall CUnitAI__UpdateDoorWingEngagement_LongRange(void * doorWingAI)", ("long-range", "CUnitAI__EnterDoorWingOpenTrackingState")),
    "0x00446400": ("CUnitAI__EnterDoorWingOpenTrackingState", "void __fastcall CUnitAI__EnterDoorWingOpenTrackingState(void * doorWingAI)", ("open tracking", "CUnitAI__PlayOpenAnimationIfState1Or3")),
    "0x00447b10": ("CUnitAI__PlayWingUnfoldedAnimationAndSetState5", "void __fastcall CUnitAI__PlayWingUnfoldedAnimationAndSetState5(void * unitAI)", ("wingunfolded", "+0x27c")),
    "0x00447b60": ("CUnitAI__HasReachedCachedAnchorPoint", "int __fastcall CUnitAI__HasReachedCachedAnchorPoint(void * unitAI)", ("cached anchor", "+0x290", "+0x280/+0x284")),
    "0x00447bb0": ("CUnitAI__GetOrGenerateCachedAnchorPoint", "void __thiscall CUnitAI__GetOrGenerateCachedAnchorPoint(void * this, void * outAnchorPoint)", ("RET 0x4", "outAnchorPoint", "CUnitAI__IsCachedAnchorPointValid")),
    "0x00447d50": ("CUnitAI__IsCachedAnchorPointValid", "int __fastcall CUnitAI__IsCachedAnchorPointValid(void * unitAI)", ("CMapWho", "occupancy")),
}

DOC_TOKENS = (
    "Wave1024",
    "cunitai-doorwing-context-review-wave1024",
    "0x00445ad0 CUnitAI__UpdateDoorWingEngagement_CloseRange",
    "0x00445f40 CUnitAI__UpdateDoorWingEngagement_MidRange",
    "0x00446150 CUnitAI__UpdateDoorWingEngagement_LongRange",
    "0x00446400 CUnitAI__EnterDoorWingOpenTrackingState",
    "0x00447b10 CUnitAI__PlayWingUnfoldedAnimationAndSetState5",
    "0x00447bb0 CUnitAI__GetOrGenerateCachedAnchorPoint",
    "0x00447d50 CUnitAI__IsCachedAnchorPointValid",
    "563/1408 = 39.99%",
    "792/1493 = 53.05%",
    "491/500 = 98.20%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OWNER_DOC_TOKENS = {
    UNITAI_DOC: ("Wave1024", "cunitai-doorwing-context-review-wave1024", "0x00445ad0 CUnitAI__UpdateDoorWingEngagement_CloseRange", "0x00447d50 CUnitAI__IsCachedAnchorPointValid", BACKUP_PATH),
    UNIT_DOC: ("Wave1024", "cunitai-doorwing-context-review-wave1024", "0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent", "0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent", BACKUP_PATH),
}

OVERCLAIMS = (
    "runtime door-wing behavior proven",
    "runtime targeting behavior proven",
    "exact source-body identity proven",
    "exact layout proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def rows_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(field, "")): row for row in rows}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 10,
        "instructions.tsv": 1093,
        "decompile/index.tsv": 8,
        "comparison-metadata.tsv": 9,
        "comparison-tags.tsv": 9,
        "comparison-xrefs.tsv": 11,
        "comparison-instructions.tsv": 317,
        "comparison-decompile/index.tsv": 9,
        "context-metadata.tsv": 2,
        "context-tags.tsv": 2,
        "context-xrefs.tsv": 13,
        "context-instructions.tsv": 36,
        "context-decompile/index.tsv": 2,
        "vtable-slots.tsv": 512,
        "dispatch-instructions.tsv": 69,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "decompile" / "index.tsv"), "address")
    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in tokens:
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail evidence tag {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    combined = "\n".join(
        read_text(BASE / path)
        for path in (
            "xrefs.tsv",
            "context-xrefs.tsv",
            "dispatch-instructions.tsv",
            "vtable-slots.tsv",
            "string-00623bb4.tsv",
            "string-006289e4.tsv",
            "string-00628ab0.tsv",
        )
    )
    for token in (
        "CUnit__ForwardAttachedNodeVFunc14IfPresent",
        "CUnit__ForwardAttachedNodeVFunc1CIfPresent",
        "CUnitAI__AdvanceOpenCloseShootAnimationState",
        "CUnitAI__AdvanceDoorWingAnimationState",
        "00445a7c",
        "00445a85",
        "00445a8e",
        "open",
        "close",
        "wingunfolded",
    ):
        require(token in combined, f"missing evidence token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "metadata.log": "targets=8 found=8 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "xrefs.log": "Wrote 10 rows",
        "instructions.log": "targets=8 missing=0",
        "decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "comparison-metadata.log": "targets=9 found=9 missing=0",
        "comparison-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "context-metadata.log": "targets=2 found=2 missing=0",
        "context-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "vtable-slots.log": "targets=2 rows=512",
        "dispatch-instructions.log": "targets=3 missing=0",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173968263, 173968263.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [NOTE, AGGREGATE_NOTE, GHIDRA_REFERENCE, CAMPAIGN, FUNCTION_INDEX, FUNCTION_COVERAGE, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE, TRACKING_STATE]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-cunitai-doorwing-context-review-wave1024")
        == r"py -3 tools\ghidra_cunitai_doorwing_context_review_wave1024_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1024-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1024 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1024 CUnitAI door-wing context review" for row in ledger), "missing Wave1024 ledger row", failures)
    require(any(row.get("task") == "Wave1024 CUnitAI door-wing context review" and row.get("attempt_id") == 20606 for row in attempts), "missing Wave1024 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue(failures)
    check_docs(failures)

    if failures:
        print("Wave1024 CUnitAI door-wing context review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1024 CUnitAI door-wing context review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
