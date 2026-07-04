#!/usr/bin/env python3
"""Validate Wave1049 end-level/objective progression read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1049-endlevel-objective-progression-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_endlevel_objective_progression_review_wave1049_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1049_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
CAREER_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "_index.md"
CAREER_RECALC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "CCareer__ReCalcLinks.md"
CAREER_UPDATE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "CCareer__Update.md"
ENDLEVEL_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "EndLevelData.cpp" / "_index.md"
ENDLEVEL_PREDICATE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "EndLevelData.cpp" / "CEndLevelData__IsAllSecondaryObjectivesComplete.md"
GAME_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-134936_post_wave1049_endlevel_objective_progression_review_verified"

TARGETS = {
    "0x004496e0": {
        "name": "CEndLevelData__IsAllSecondaryObjectivesComplete",
        "signature": "bool __fastcall CEndLevelData__IsAllSecondaryObjectivesComplete(void * this)",
        "comment_tokens": ("this+0x4d0", "returns false", "ERROR: No secondary objectives"),
        "xrefs": {"UNCONDITIONAL_CALL": 4},
    },
    "0x0046d470": {
        "name": "CGame__FillOutEndLevelData",
        "signature": "void __fastcall CGame__FillOutEndLevelData(void * this)",
        "comment_tokens": ("end-of-level snapshot", "objectives", "progression/grade"),
        "xrefs": {"UNCONDITIONAL_CALL": 1},
    },
    "0x00472670": {
        "name": "CGame__GetNumPrimaryObjectives",
        "signature": "int __fastcall CGame__GetNumPrimaryObjectives(void * this)",
        "comment_tokens": ("mPrimaryObjectives", "CGame+0x4c", "8-byte objective records"),
        "xrefs": {"UNCONDITIONAL_CALL": 1},
    },
    "0x00472690": {
        "name": "CGame__GetNumSecondaryObjectives",
        "signature": "int __fastcall CGame__GetNumSecondaryObjectives(void * this)",
        "comment_tokens": ("mSecondaryObjectives", "CGame+0x9c", "8-byte objective records"),
        "xrefs": {"UNCONDITIONAL_CALL": 1},
    },
    "0x0041bdf0": {
        "name": "CCareer__ReCalcLinks",
        "signature": "void __fastcall CCareer__ReCalcLinks(void * this)",
        "comment_tokens": ("END_LEVEL_DATA", "career +0x240c", "bits 29/30"),
        "xrefs": {"UNCONDITIONAL_CALL": 1},
    },
    "0x0046d9f0": {
        "name": "CGame__RunOutroFMV",
        "signature": "void __fastcall CGame__RunOutroFMV(void * this)",
        "comment_tokens": ("lookup types 1/2", "goodie unlock updates", "credits"),
        "xrefs": {"UNCONDITIONAL_CALL": 1},
    },
    "0x005343e0": {
        "name": "IScript__PrimaryObjectiveComplete",
        "signature": "void __stdcall IScript__PrimaryObjectiveComplete(void * script_args, void * unused_state, void * out_result)",
        "comment_tokens": ("DAT_008a9ae0", "DAT_008a9adc", "state 1"),
        "xrefs": {"DATA": 1},
    },
    "0x00534410": {
        "name": "IScript__SecondaryObjectiveComplete",
        "signature": "void __stdcall IScript__SecondaryObjectiveComplete(void * script_args, void * unused_state, void * out_result)",
        "comment_tokens": ("DAT_008a9b30", "DAT_008a9b2c", "state 1"),
        "xrefs": {"DATA": 1},
    },
    "0x00534440": {
        "name": "IScript__PrimaryObjectiveFailed",
        "signature": "void __stdcall IScript__PrimaryObjectiveFailed(void * script_args, void * unused_state, void * out_result)",
        "comment_tokens": ("DAT_008a9ae0", "DAT_008a9adc", "state 2"),
        "xrefs": {"DATA": 1},
    },
    "0x00534470": {
        "name": "IScript__SecondaryObjectiveFailed",
        "signature": "void __stdcall IScript__SecondaryObjectiveFailed(void * script_args, void * unused_state, void * out_result)",
        "comment_tokens": ("DAT_008a9b30", "DAT_008a9b2c", "state 2"),
        "xrefs": {"DATA": 1},
    },
}

CONTEXT_SIGNATURES = {
    "0x0041bd00": "void __fastcall CCareer__Update(void * this)",
    "0x0046d3a0": "void __thiscall CGame__SetSlot(void * this, int slot, int val)",
    "0x0046d410": "bool __thiscall CGame__GetSlot(void * this, int slot)",
    "0x004214e0": "void __thiscall CCareer__SetSlot(void * this, int slot_num, int val)",
    "0x005338d0": "void __stdcall IScript__SetSlot(void * script_args, void * unused_state, void * out_result)",
    "0x00533900": "void __stdcall IScript__SetSlotSave(void * script_args, void * unused_state, void * out_result)",
    "0x005339a0": "void __stdcall IScript__GetSlotBitValue(void * script_args, void * unused_state, void * out_result)",
}

DOC_TOKENS = (
    "Wave1049",
    "endlevel-objective-progression-review-wave1049",
    "0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete",
    "0x0046d470 CGame__FillOutEndLevelData",
    "0x0041bdf0 CCareer__ReCalcLinks",
    "0x0046d9f0 CGame__RunOutroFMV",
    "0x005343e0 IScript__PrimaryObjectiveComplete",
    "0x00534470 IScript__SecondaryObjectiveFailed",
    "CGame__SetSlot",
    "IScript__SetSlotSave",
    "IScript__GetSlotBitValue",
    "744/1408 = 52.84%",
    "1012/1509 = 67.06%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-layout identity proven",
    "exact source layout identity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
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


def read_json(path: Path) -> dict:
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
        "metadata.tsv": 10,
        "tags.tsv": 10,
        "xrefs.tsv": 13,
        "instructions.tsv": 761,
        "decompile/index.tsv": 10,
        "context-metadata.tsv": 12,
        "context-tags.tsv": 12,
        "context-xrefs.tsv": 23,
        "context-instructions.tsv": 6129,
        "context-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "xrefs.tsv")
    xref_counts = Counter((normalize_address(row["target_addr"]), row["ref_type"]) for row in xrefs)

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in expected["comment_tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        for ref_type, count in expected["xrefs"].items():
            require(xref_counts[(address, ref_type)] == count, f"xref count mismatch at {address} {ref_type}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, signature in CONTEXT_SIGNATURES.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("signature") == signature, f"context signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch at {address}", failures)

    decompile_tokens = {
        "decompile/004496e0_CEndLevelData__IsAllSecondaryObjectivesComplete.c": ("0x4d0", "ERROR: No secondary objectives"),
        "decompile/0046d470_CGame__FillOutEndLevelData.c": ("DAT_006728f8", "CEndLevelData__IsAllSecondaryObjectivesComplete", "0x308"),
        "decompile/0041bdf0_CCareer__ReCalcLinks.c": ("CEndLevelData__IsAllSecondaryObjectivesComplete", "0x240c", "DAT_006728f8"),
        "decompile/0046d9f0_CGame__RunOutroFMV.c": ("lookup_FMV", "CEndLevelData__IsAllSecondaryObjectivesComplete"),
        "context-decompile/0041bd00_CCareer__Update.c": ("CCareer__ReCalcLinks", "CCareer__UpdateGoodieStates"),
        "context-decompile/005338d0_IScript__SetSlot.c": ("CGame__SetSlot", "DAT_008a9a98"),
        "context-decompile/00533900_IScript__SetSlotSave.c": ("CGame__SetSlot", "CCareer__SetSlot"),
        "context-decompile/005339a0_IScript__GetSlotBitValue.c": ("CGame__GetSlot", "0x005e4d50"),
    }
    for relative, tokens in decompile_tokens.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing decompile token in {relative}: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=10 found=10 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "xrefs.log": "Wrote 13 rows",
        "instructions.log": "Wrote 761 function-body instruction rows",
        "decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "context-metadata.log": "targets=12 found=12 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "context-xrefs.log": "Wrote 23 rows",
        "context-instructions.log": "Wrote 6129 function-body instruction rows",
        "context-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save success in {relative}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174590855 or backup.get("totalBytes") == 174590855.0, "backup byte count mismatch", failures)
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
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        CAREER_INDEX: ("Wave1049", "endlevel-objective-progression-review-wave1049", "0x0041bdf0 CCareer__ReCalcLinks", "IScript__SetSlotSave", BACKUP_PATH),
        CAREER_RECALC: ("Wave1049", "endlevel-objective-progression-review-wave1049", "0x0041bdf0 CCareer__ReCalcLinks", "0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete", BACKUP_PATH),
        CAREER_UPDATE: ("Wave1049", "endlevel-objective-progression-review-wave1049", "CCareer__ReCalcLinks", "IScript__SetSlotSave", BACKUP_PATH),
        ENDLEVEL_INDEX: ("Wave1049", "endlevel-objective-progression-review-wave1049", "0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete", "0x0046d470 CGame__FillOutEndLevelData", BACKUP_PATH),
        ENDLEVEL_PREDICATE: ("Wave1049", "endlevel-objective-progression-review-wave1049", "0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete", "0x0041bdf0 CCareer__ReCalcLinks", BACKUP_PATH),
        GAME_INDEX: ("Wave1049", "endlevel-objective-progression-review-wave1049", "0x0046d470 CGame__FillOutEndLevelData", "0x0046d9f0 CGame__RunOutroFMV", "CGame__SetSlot", BACKUP_PATH),
        ISCRIPT_DOC: ("Wave1049", "endlevel-objective-progression-review-wave1049", "0x005343e0 IScript__PrimaryObjectiveComplete", "0x00534470 IScript__SecondaryObjectiveFailed", "IScript__SetSlotSave", BACKUP_PATH),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-endlevel-objective-progression-review-wave1049")
        == r"py -3 tools\ghidra_endlevel_objective_progression_review_wave1049_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1049-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1049 --check",
        "missing aggregate package script",
        failures,
    )

    task = "Wave1049 endlevel objective progression review"
    require(any(row.get("task") == task for row in read_jsonl(LEDGER)), "missing Wave1049 ledger row", failures)
    require(any(row.get("task") == task and row.get("attempt_id") == 20631 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave1049 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1049 end-level/objective progression review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1049 end-level/objective progression review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
