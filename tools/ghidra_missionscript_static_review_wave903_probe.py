#!/usr/bin/env python3
"""Validate Wave903 MissionScript/IScript static-review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave903-missionscript-static-review"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BASELINE_JSON = BASE / "missionscript-static-review-baseline.json"
ANCHORS_TSV = BASE / "missionscript-function-anchors.tsv"
FAMILY_TSV = BASE / "missionscript-family-summary.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_missionscript_static_review_wave903_2026-05-26.md"
REVIEW_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-static-review-2026-05-26.md"
STATIC_SYSTEM_REVIEW = ROOT / "reverse-engineering" / "binary-analysis" / "static-system-review-2026-05-26.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"
MSL_SCRIPTING = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
MSL_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
MISSION_EVENTS = ROOT / "reverse-engineering" / "game-assets" / "mission-events-index.md"
MISSION_SLOTS = ROOT / "reverse-engineering" / "game-assets" / "mission-slot-usage.md"
MISSION_THINGS = ROOT / "reverse-engineering" / "game-assets" / "mission-thing-usage.md"
SCRIPT_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Script.cpp" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
PACKAGE_JSON = ROOT / "package.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260526-095411_post_wave903_missionscript_static_review_verified"

EXPECTED_FAMILIES = {
    "IScript": 49,
    "CScriptObjectCode": 22,
    "CMissionScriptObjectCode": 7,
    "CScriptEventNB": 13,
    "CEventFunction": 5,
    "CDataType": 37,
    "CAsmInstruction": 19,
    "ScriptRegistry": 1,
    "CStatementChain": 1,
    "ScriptSlots": 3,
    "CEventManager": 12,
}

REQUIRED_ANCHORS = {
    "ScriptCommandRegistry__InitBuiltins",
    "IScript__ScheduleEvent",
    "IScript__SetSlotSave",
    "IScript__LevelWon",
    "IScript__LevelLostString",
    "IScript__PrimaryObjectiveComplete",
    "IScript__SecondaryObjectiveComplete",
    "IScript__SetGoodieState",
    "IScript__Create3PointPanCamera",
    "CScriptObjectCode__Run",
    "CScriptObjectCode__CallEvent",
    "CScriptObjectCode__GotoInstruction",
    "CScriptEventNB__PostEvent",
    "CScriptEventNB__RegisterEventListener",
    "CMissionScriptObjectCode__LoadAsync",
    "CMissionScriptObjectCode__StartLoadAsync",
    "CEventFunction__Execute",
    "CAsmInstruction__SpawnFromOpcode",
    "CAsmInstruction__ExecuteCall",
    "CInstructionOP_JMPFALSE__VFunc_00_0052e950",
    "CDataType__CreateFromType",
    "CGame__SetSlot",
    "CGame__GetSlot",
    "CCareer__SetSlot",
    "CEventManager__AddEvent_TimeFromNow",
}

CORE_ANCHORS = (
    "Wave903",
    "missionscript-static-review-wave903",
    "static-coherent MissionScript/IScript core",
    "6113/6113 = 100.00%",
    "ScriptCommandRegistry__InitBuiltins",
    "144",
    "0x0064ce50",
    "0x0064f210",
    "IScript__ScheduleEvent",
    "IScript__SetSlotSave",
    "IScript__LevelWon",
    "CScriptObjectCode__Run",
    "CScriptEventNB__PostEvent",
    "CMissionScriptObjectCode__LoadAsync",
    "795",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime missionscript behavior proven",
    "runtime mission-script behavior proven",
    "all command semantics proven",
    "descriptor schema fully proven",
    "live loose-msl loading proven",
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
    require(baseline.get("wave") == "Wave903 MissionScript/IScript static review", "baseline wave mismatch", failures)
    require(baseline.get("tag") == "missionscript-static-review-wave903", "baseline tag mismatch", failures)
    require(baseline.get("queue", {}).get("strictCleanSignatureProxy") == "6113/6113 = 100.00%", "baseline strict proxy mismatch", failures)
    registry = baseline.get("registry", {})
    require(registry.get("initializer") == "ScriptCommandRegistry__InitBuiltins", "registry initializer mismatch", failures)
    require(registry.get("descriptorRecords") == 144, "registry descriptor count mismatch", failures)
    require(registry.get("descriptorBytes") == "0x40", "registry descriptor size mismatch", failures)
    require("0x0064ce50" in registry.get("descriptorRange", ""), "registry start missing", failures)
    require("0x0064f210" in registry.get("descriptorRange", ""), "registry end missing", failures)

    assets = baseline.get("missionAssetIndexes", {})
    expected_assets = {
        "eventIndexLevels": 95,
        "levelsWithEvents": 74,
        "totalEventNames": 795,
        "primaryCompleteCalls": 115,
        "secondaryCompleteCalls": 42,
        "primaryFailedCalls": 102,
        "levelWonCalls": 79,
        "levelLostCalls": 13,
        "slotSummaryRows": 24,
        "thingSummaryRows": 701,
    }
    for key, expected in expected_assets.items():
        require(assets.get(key) == expected, f"asset metric mismatch for {key}", failures)

    family_rows = {row["family"]: row for row in read_tsv(FAMILY_TSV)}
    require(len(family_rows) == len(EXPECTED_FAMILIES), "family summary row count mismatch", failures)
    for family, count in EXPECTED_FAMILIES.items():
        row = family_rows.get(family)
        require(row is not None, f"missing family row: {family}", failures)
        if row:
            require(int(row.get("count", -1)) == count, f"family count mismatch: {family}", failures)
            require(int(row.get("commented", -1)) == count, f"family commented mismatch: {family}", failures)
            require(int(row.get("cleanSignatures", -1)) == count, f"family clean-signature mismatch: {family}", failures)

    anchors = read_tsv(ANCHORS_TSV)
    require(len(anchors) == 169, "anchor row count mismatch", failures)
    names = {row["name"] for row in anchors}
    for name in REQUIRED_ANCHORS:
        require(name in names, f"missing anchor: {name}", failures)
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


def check_docs(failures: list[str]) -> None:
    docs = (
        PUBLIC_NOTE,
        REVIEW_DOC,
        STATIC_SYSTEM_REVIEW,
        MAPPED_SYSTEMS,
        BINARY_INDEX,
        GAME_ASSETS_INDEX,
        MSL_SCRIPTING,
        MSL_COMMANDS,
        MISSION_EVENTS,
        MISSION_SLOTS,
        MISSION_THINGS,
        SCRIPT_INDEX,
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
        scripts.get("test:ghidra-missionscript-static-review-wave903")
        == r"py -3 tools\ghidra_missionscript_static_review_wave903_probe.py --check",
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
    check_docs(failures)

    if failures:
        print("Wave903 MissionScript static-review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave903 MissionScript static-review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
