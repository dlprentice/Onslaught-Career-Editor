#!/usr/bin/env python3
"""Validate Wave1044 Career/Controller residual review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1044-career-controller-residual-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_career_controller_residual_review_wave1044_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1044_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
CAREER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "_index.md"
CONTROLLER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Controller.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-103855_post_wave1044_career_controller_residual_review_verified"

TARGETS = {
    "0x0041b740": ("CCareerNode__Blank", "void __fastcall CCareerNode__Blank(void * this)"),
    "0x0041c180": ("CCareer__UpdateThingsKilled", "void __fastcall CCareer__UpdateThingsKilled(void * this)"),
    "0x0041c470": ("CCareer__UpdateGoodieStates", "void __fastcall CCareer__UpdateGoodieStates(void * this)"),
    "0x004214e0": ("CCareer__SetSlot", "void __thiscall CCareer__SetSlot(void * this, int slot_num, int val)"),
    "0x0042d640": (
        "CController__Init",
        "void * __thiscall CController__Init(void * this, void * player, int input_device, int controller_config)",
    ),
    "0x0042d8a0": ("CController__StartRecording", "void __thiscall CController__StartRecording(void * this, char * filename)"),
    "0x0042d8c0": ("CController__StartPlayback", "void __thiscall CController__StartPlayback(void * this, char * filename)"),
    "0x0042d8e0": ("CController__dtor", "void __fastcall CController__dtor(void * this)"),
    "0x004f00d0": ("CController__dtor_Thunk", "void __fastcall CController__dtor_Thunk(void * this)"),
}

COMMENT_TOKENS = {
    "0x0041b740": ("CCareerNode::Blank", "Source: Career.cpp"),
    "0x0041c180": ("CCareer::UpdateThingsKilled", "Source: Career.cpp"),
    "0x0041c470": ("CCareer::UpdateGoodieStates", "Source: Career.cpp"),
    "0x004214e0": ("CCareer::SetSlot", "mSlots[slot >> 5]"),
    "0x0042d640": ("Initializes a CController instance", "player+0x04", "recording/playback"),
    "0x0042d8a0": ("StartRecording", "DXMemBuffer__OpenWrite"),
    "0x0042d8c0": ("StartPlayback", "DXMemBuffer__OpenRead"),
    "0x0042d8e0": ("CController::~CController", "monitor unlink helper", "CChunker"),
    "0x004f00d0": ("Direct thunk", "CController__dtor"),
}

DECOMPILE_TOKENS = {
    "0x0041b740": ("0xffffffff", "0xbf800000", "iVar1 = 9"),
    "0x0041c180": ("DAT_00672e18 != 100", "g_LevelKillCounts", "0x23f4", "0xffffff"),
    "0x0041c470": ("0x1f44", "CCareer__GetGradeForWorld", "CGrade__operator_gte", "CCareer__GetNodeFromWorld"),
    "0x004214e0": ("0xff < slot_num", "0x2408", "val == 1", "CConsole__Printf"),
    "0x0042d640": ("CSPtrSet__Init", "CDXMemBuffer__ctor", "CSPtrSet__AddToHead", "0x16c", "0x174"),
    "0x0042d8a0": ("0x160", "CDXMemBuffer__OpenWrite"),
    "0x0042d8c0": ("0x161", "CDXMemBuffer__InitFromFile"),
    "0x0042d8e0": ("CDXMemBuffer__Close", "CMonitor__DeleteDeletionEvent", "CDXMemoryManager__Free", "CDXMemBuffer__dtor_base"),
    "0x004f00d0": ("CController__dtor(this)",),
}

CONTEXT_TARGETS = {
    "0x0041b7c0": "CCareer__Blank",
    "0x0041bd00": "CCareer__Update",
    "0x0041bdf0": "CCareer__ReCalcLinks",
    "0x00421200": "CCareer__Load",
    "0x00421350": "CCareer__Save",
    "0x0042d780": "CController__scalar_deleting_dtor",
    "0x0042d9d0": "CController__Flush",
    "0x0042db40": "CController__DoMappings",
    "0x005145f0": "CController__ctor",
    "0x00514720": "CPCController__RecordControllerState",
    "0x00514760": "CPCController__ReadControllerState",
}

DOC_TOKENS = (
    "Wave1044",
    "career-controller-residual-review-wave1044",
    "0x0041b740 CCareerNode__Blank",
    "0x0041c180 CCareer__UpdateThingsKilled",
    "0x0041c470 CCareer__UpdateGoodieStates",
    "0x004214e0 CCareer__SetSlot",
    "0x0042d640 CController__Init",
    "0x0042d8a0 CController__StartRecording",
    "0x0042d8c0 CController__StartPlayback",
    "0x0042d8e0 CController__dtor",
    "0x004f00d0 CController__dtor_Thunk",
    "CCareer__GetGradeForWorld",
    "CGrade__operator_gte",
    "CDXMemBuffer__OpenWrite",
    "CDXMemBuffer__InitFromFile",
    "CMonitor__DeleteDeletionEvent",
    "735/1408 = 52.20%",
    "977/1493 = 65.44%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime save/progression behavior proven",
    "runtime goodies unlock behavior proven",
    "runtime controller/input behavior proven",
    "exact source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path):
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 9,
        "tags.tsv": 9,
        "xrefs.tsv": 14,
        "instructions.tsv": 5815,
        "decompile/index.tsv": 9,
        "context-metadata.tsv": 11,
        "context-tags.tsv": 11,
        "context-xrefs.tsv": 25,
        "context-instructions.tsv": 1259,
        "context-decompile/index.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    xrefs = read_text(BASE / "xrefs.tsv")

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag row/status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
        text = read_text(BASE / "decompile" / f"{address[2:]}_{name}.c")
        for token in DECOMPILE_TOKENS[address]:
            require(token in text, f"missing decompile token at {address}: {token}", failures)

    for token in (
        "CCareer__StaticInitDefaults",
        "CCareer__Update",
        "CCareer__Blank",
        "IScript__SetSlotSave",
        "CGame__PostLoadProcess",
        "CLTShell__InitializeRuntimeAndLoadCoreResources",
        "Unwind@005d5030",
        "CPCController__scalar_deleting_dtor",
    ):
        require(token in xrefs, f"missing xref token: {token}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None and row.get("name") == name, f"context name mismatch at {address}", failures)
        require(row is not None and row.get("status") == "OK", f"context status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=9 found=9 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "xrefs.log": "Wrote 14 rows",
        "instructions.log": "Wrote 5815 function-body instruction rows",
        "decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "context-metadata.log": "targets=11 found=11 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "context-xrefs.log": "Wrote 25 rows",
        "context-instructions.log": "Wrote 1259 function-body instruction rows",
        "context-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6238, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined signature count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174263175, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        CAREER_DOC: (
            "Wave1044",
            "career-controller-residual-review-wave1044",
            "0x0041b740 CCareerNode__Blank",
            "0x0041c180 CCareer__UpdateThingsKilled",
            "0x0041c470 CCareer__UpdateGoodieStates",
            "0x004214e0 CCareer__SetSlot",
            "CCareer__GetGradeForWorld",
            "CGrade__operator_gte",
            "735/1408 = 52.20%",
            "977/1493 = 65.44%",
            BACKUP_PATH,
            "no mutation",
        ),
        CONTROLLER_DOC: (
            "Wave1044",
            "career-controller-residual-review-wave1044",
            "0x0042d640 CController__Init",
            "0x0042d8a0 CController__StartRecording",
            "0x0042d8c0 CController__StartPlayback",
            "0x0042d8e0 CController__dtor",
            "0x004f00d0 CController__dtor_Thunk",
            "CDXMemBuffer__OpenWrite",
            "CDXMemBuffer__InitFromFile",
            "CMonitor__DeleteDeletionEvent",
            "735/1408 = 52.20%",
            "977/1493 = 65.44%",
            BACKUP_PATH,
            "no mutation",
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-career-controller-residual-review-wave1044")
        == r"py -3 tools\ghidra_career_controller_residual_review_wave1044_probe.py --check",
        "missing Wave1044 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1044-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1044 --check",
        "missing Wave1044 aggregate recheck package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1044 career/controller residual review" for row in ledger_rows), "missing Wave1044 ledger row", failures)
    require(any(row.get("task") == "Wave1044 career/controller residual review" for row in attempt_rows), "missing Wave1044 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1044 Career/Controller residual review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave1044 Career/Controller residual review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
