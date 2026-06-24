#!/usr/bin/env python3
"""Validate Wave902 save/options static-review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave902-save-options-static-review"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BASELINE_JSON = BASE / "save-options-static-review-baseline.json"
ANCHORS_TSV = BASE / "save-options-function-anchors.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_save_options_static_review_wave902_2026-05-26.md"
REVIEW_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-static-review-2026-05-26.md"
STATIC_SYSTEM_REVIEW = ROOT / "reverse-engineering" / "binary-analysis" / "static-system-review-2026-05-26.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
SAVE_INDEX = ROOT / "reverse-engineering" / "save-file" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
PACKAGE_JSON = ROOT / "package.json"
APPCORE_PATCHER = ROOT / "OnslaughtCareerEditor.AppCore" / "BesFilePatcher.cs"
APPCORE_TESTS = ROOT / "OnslaughtCareerEditor.AppCore.Tests" / "SaveAnalyzerServiceTests.cs"
UI_SAVE_TESTS = ROOT / "OnslaughtCareerEditor.UiTests" / "SavePatchRegressionTests.cs"
UI_OPTIONS_TESTS = ROOT / "OnslaughtCareerEditor.UiTests" / "CliReadOnlyAndOptionsSafetyTests.cs"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-093817_post_wave902_save_options_static_review_verified"

EXPECTED_ANCHORS = {
    "CCareer__Load",
    "CCareer__Save",
    "CCareer__GetSaveSize",
    "CCareer__Update",
    "CCareer__ReCalcLinks",
    "CCareer__UpdateThingsKilled",
    "CCareer__CountGoodies",
    "CCareer__UpdateGoodieStates",
    "CCareer__GetGradeFromRanking",
    "CCareer__GetAndResetGoodieNewCount",
    "CCareer__GetAndResetFirstGoodie",
    "CCareer__GetKillCounterTopByte_23F4",
    "CCareer__GetKillCounterTopByte_23F8",
    "CCareer__SetKillCounterTopByte_23F4",
    "CCareer__SetKillCounterTopByte_23F8",
    "CCareer__GetGoodiePtr",
    "CCareer__NodeArrayAt",
    "OptionsTail_Write",
    "OptionsTail_Read",
    "OptionsEntries__FindById",
    "OptionsEntries__InitDefaultDualBindingsTable",
    "OptionsEntries__InitDefaultSingleBindingsTable",
    "OptionsEntries__SetBindingSlot",
    "Controls__ApplyPreset",
    "Controls__DispatchRemap",
    "ControlsUI__RenderBindingsList",
    "CFEPLoadGame__DoLoad",
    "CFEPOptions__WriteDefaultOptionsFile",
    "CFEPOptions__SaveDefaultOptions",
    "CPauseMenu__ResumeGameAndPersistOptions",
    "CFEPMain__Process",
    "Platform__AsyncSaveCareer",
}

CORE_ANCHORS = (
    "Wave902",
    "save-options-static-review-wave902",
    "static-closed save/options/career",
    "6113/6113 = 100.00%",
    "10004",
    "0x4BD1",
    "0x0002",
    "0x23F6",
    "0x24BE",
    "0x56",
    "CCareer__Load",
    "CCareer__Save",
    "OptionsTail_Write",
    "OptionsTail_Read",
    "CFEPOptions__WriteDefaultOptionsFile",
    "CPauseMenu__ResumeGameAndPersistOptions",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime save/load proven",
    "runtime controller behavior proven",
    "goodies wall runtime proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name, rows in queue["priorityQueues"].items():
        require(rows == [], f"priority queue not empty: {name}", failures)

    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV has commentless row", failures)
    require(not any(row.get("signature", "").startswith("undefined ") for row in rows), "quality TSV has undefined signature", failures)
    require(
        not any(re.search(r"\bparam_\d+\b", row.get("signature", "")) for row in rows),
        "quality TSV has param_N signature",
        failures,
    )


def check_evidence(failures: list[str]) -> None:
    baseline = read_json(BASELINE_JSON)
    require(baseline.get("wave") == "Wave902 save/options static review", "baseline wave mismatch", failures)
    require(baseline.get("tag") == "save-options-static-review-wave902", "baseline tag mismatch", failures)
    require(baseline.get("queue", {}).get("strictCleanSignatureProxy") == "6113/6113 = 100.00%", "baseline strict proxy mismatch", failures)

    save_format = baseline.get("saveFormat", {})
    expected_values = {
        "fileSizeBytes": 10004,
        "versionWord": "0x4BD1",
        "careerBase": "0x0002",
        "optionsEntriesStart": "0x24BE",
        "optionsEntryCount": 16,
        "optionsEntrySize": "0x20",
        "optionsTailBytes": "0x56 at EOF-0x56",
    }
    for key, expected in expected_values.items():
        require(save_format.get(key) == expected, f"baseline saveFormat mismatch for {key}", failures)
    for token in ("300 x 4 bytes", "233 displayable", "0x23F6", "0x2402", "0x2406"):
        require(token in json.dumps(save_format), f"missing saveFormat token: {token}", failures)

    anchors = read_tsv(ANCHORS_TSV)
    names = {row["name"] for row in anchors}
    require(len(anchors) == len(EXPECTED_ANCHORS), "anchor row count mismatch", failures)
    require(names == EXPECTED_ANCHORS, f"anchor name mismatch: {sorted(EXPECTED_ANCHORS - names)}", failures)
    for row in anchors:
        signature = row.get("signature", "")
        require(row.get("comment", "").strip() != "", f"anchor missing comment: {row.get('name')}", failures)
        require(not signature.startswith("undefined "), f"anchor undefined signature: {row.get('name')}", failures)
        require(re.search(r"\bparam_\d+\b", signature) is None, f"anchor param_N signature: {row.get('name')}", failures)
        require(row.get("status") == "OK", f"anchor status mismatch: {row.get('name')}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_product_alignment(failures: list[str]) -> None:
    patcher = read_text(APPCORE_PATCHER)
    for token in (
        "EXPECTED_FILE_SIZE = 10004",
        "CAREER_BASE = 0x0002",
        "GOODIE_COUNT = 300",
        "GOODIE_DISPLAYABLE_COUNT = 233",
        "VERSION_WORD = 0x4BD1",
        "CopyOptionsEntries",
        "CopyOptionsTail",
        "PatchResult.Fail",
    ):
        require(token in patcher, f"missing AppCore patcher token: {token}", failures)

    tests = "\n".join(read_text(path) for path in (APPCORE_TESTS, UI_SAVE_TESTS, UI_OPTIONS_TESTS))
    for token in (
        "0x249E",
        "0x23F6",
        "PatchFile_RejectsInPlaceOutputPath",
        "CliOptionsFile_BlocksCareerSectionsByDefault",
        "CliOptionsFile_SettingsOnlyMode_IsAllowed",
        "CopyOptionsTail",
        "OPTIONS (bindings + tail snapshot)",
    ):
        require(token in tests, f"missing test token: {token}", failures)


def check_docs(failures: list[str]) -> None:
    docs = (
        PUBLIC_NOTE,
        REVIEW_DOC,
        STATIC_SYSTEM_REVIEW,
        MAPPED_SYSTEMS,
        BINARY_INDEX,
        SAVE_INDEX,
        RE_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-save-options-static-review-wave902")
        == r"py -3 tools\ghidra_save_options_static_review_wave902_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_queue(failures)
    check_evidence(failures)
    check_product_alignment(failures)
    check_docs(failures)

    if failures:
        print("Wave902 save/options static-review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave902 save/options static-review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
