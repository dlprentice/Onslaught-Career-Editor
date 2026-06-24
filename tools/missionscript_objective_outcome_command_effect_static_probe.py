#!/usr/bin/env python3
"""Validate the MissionScript objective/outcome command-effect static proof."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect-static-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect-static-proof.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_objective_outcome_command_effect_static_proof_2026-06-08.md"

DESCRIPTOR_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-descriptor-schema.v1.json"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
PROOF_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
EVENTS_DOC = ROOT / "reverse-engineering" / "game-assets" / "mission-events-index.md"
MESSAGES_DOC = ROOT / "reverse-engineering" / "game-assets" / "mission-message-usage.md"
MSL_SCRIPTING = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
MSL_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
GAME_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
CAREER_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "_index.md"
ENDLEVEL_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "EndLevelData.cpp" / "_index.md"
CGAME_FILL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "CGame__FillOutEndLevelData.md"
CGAME_WON_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "CGame__DeclareLevelWon.md"
CGAME_LOST_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "CGame__DeclareLevelLost.md"
CCAREER_UPDATE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "CCareer__Update.md"
ENDLEVEL_SECONDARY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "EndLevelData.cpp" / "CEndLevelData__IsAllSecondaryObjectivesComplete.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

WAVE580 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave580-iscript-camera-objective-00533b70"
WAVE585 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave585-iscript-level-event-00537fd0"
WAVE1049 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1049-endlevel-objective-progression-review"

WAVE1219_BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
WAVE580_BACKUP = r"G:\GhidraBackups\BEA_20260519-044247_post_wave580_iscript_camera_objective_verified"
WAVE585_BACKUP = r"G:\GhidraBackups\BEA_20260519-094217_post_wave585_iscript_level_event_verified"
WAVE1049_BACKUP = r"G:\GhidraBackups\BEA_20260601-134936_post_wave1049_endlevel_objective_progression_review_verified"

SCHEMA_LINK = "missionscript-objective-outcome-command-effect.v1.json"
PROOF_LINK = "missionscript-objective-outcome-command-effect-static-proof.md"

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime objective behavior proven",
    "runtime level outcome proven",
    "runtime save behavior proven",
    "live loose-msl loading proven",
    "exact command descriptor layout proven",
    "exact cgame layout proven",
    "exact ccareer layout proven",
    "exact end_level_data layout proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)

DESCRIPTOR_SLOTS = {
    "LevelLost": {"index": 7, "recordAddress": "0x0064d010", "symbol": "s_LevelLost_0064f9c8"},
    "LevelWon": {"index": 8, "recordAddress": "0x0064d050", "symbol": "s_LevelWon_0064f9bc"},
    "PrimaryObjectiveComplete": {"index": 82, "recordAddress": "0x0064e2d0", "symbol": "s_PrimaryObjectiveComplete_0064f5ec"},
    "SecondaryObjectiveComplete": {"index": 83, "recordAddress": "0x0064e310", "symbol": "s_SecondaryObjectiveComplete_0064f5d0"},
    "PrimaryObjectiveFailed": {"index": 86, "recordAddress": "0x0064e3d0", "symbol": "s_PrimaryObjectiveFailed_0064f5a4"},
    "SecondaryObjectiveFailed": {"index": 87, "recordAddress": "0x0064e410", "symbol": "s_SecondaryObjectiveFailed_0064f588"},
    "LevelLostString": {"index": 105, "recordAddress": "0x0064e890", "symbol": "s_LevelLostString_0064f478"},
}

OBJECTIVE_HANDLERS: list[dict[str, Any]] = [
    {
        "command": "PrimaryObjectiveComplete",
        "address": "0x005343e0",
        "name": "IScript__PrimaryObjectiveComplete",
        "objectiveKind": "primary",
        "stateValue": 1,
        "textStorage": "DAT_008a9ae0 + index*8",
        "stateStorage": "DAT_008a9adc + index*8",
        "metadataTokens": ("PrimaryObjectiveComplete(objective_index,text_id)", "DAT_008a9ae0", "state 1"),
        "decompile": "005343e0_IScript__PrimaryObjectiveComplete.c",
        "decompileTokens": ("DAT_008a9ae0", "DAT_008a9adc", "= 1"),
    },
    {
        "command": "SecondaryObjectiveComplete",
        "address": "0x00534410",
        "name": "IScript__SecondaryObjectiveComplete",
        "objectiveKind": "secondary",
        "stateValue": 1,
        "textStorage": "DAT_008a9b30 + index*8",
        "stateStorage": "DAT_008a9b2c + index*8",
        "metadataTokens": ("SecondaryObjectiveComplete(objective_index,text_id)", "DAT_008a9b30", "state 1"),
        "decompile": "00534410_IScript__SecondaryObjectiveComplete.c",
        "decompileTokens": ("DAT_008a9b30", "DAT_008a9b2c", "= 1"),
    },
    {
        "command": "PrimaryObjectiveFailed",
        "address": "0x00534440",
        "name": "IScript__PrimaryObjectiveFailed",
        "objectiveKind": "primary",
        "stateValue": 2,
        "textStorage": "DAT_008a9ae0 + index*8",
        "stateStorage": "DAT_008a9adc + index*8",
        "metadataTokens": ("PrimaryObjectiveFailed(objective_index,text_id)", "DAT_008a9ae0", "state 2"),
        "decompile": "00534440_IScript__PrimaryObjectiveFailed.c",
        "decompileTokens": ("DAT_008a9ae0", "DAT_008a9adc", "= 2"),
    },
    {
        "command": "SecondaryObjectiveFailed",
        "address": "0x00534470",
        "name": "IScript__SecondaryObjectiveFailed",
        "objectiveKind": "secondary",
        "stateValue": 2,
        "textStorage": "DAT_008a9b30 + index*8",
        "stateStorage": "DAT_008a9b2c + index*8",
        "metadataTokens": ("SecondaryObjectiveFailed(objective_index,text_id)", "DAT_008a9b30", "state 2"),
        "decompile": "00534470_IScript__SecondaryObjectiveFailed.c",
        "decompileTokens": ("DAT_008a9b30", "DAT_008a9b2c", "= 2"),
    },
]

OUTCOME_HANDLERS: list[dict[str, Any]] = [
    {
        "command": "LevelLost",
        "address": "0x005381a0",
        "name": "IScript__LevelLost",
        "bridge": "CGame__DeclareLevelLost(&DAT_008a9a98,0,0)",
        "metadataTokens": ("LevelLost()", "CGame__DeclareLevelLost(0,0)", "no-message non-death loss"),
        "decompile": "005381a0_IScript__LevelLost.c",
        "decompileTokens": ("CGame__DeclareLevelLost", "DAT_008a9a98", ",0,0"),
    },
    {
        "command": "LevelLostString",
        "address": "0x005381c0",
        "name": "IScript__LevelLostString",
        "bridge": "CGame__DeclareLevelLost(&DAT_008a9a98,message_id,0)",
        "metadataTokens": ("LevelLostString(message_id)", "vtable slot +0x30", "message_id"),
        "decompile": "005381c0_IScript__LevelLostString.c",
        "decompileTokens": ("CGame__DeclareLevelLost", "message", "0x30"),
    },
    {
        "command": "LevelWon",
        "address": "0x005381e0",
        "name": "IScript__LevelWon",
        "bridge": "CGame__DeclareLevelWon(&DAT_008a9a98)",
        "metadataTokens": ("LevelWon()", "CGame__DeclareLevelWon", "DAT_008a9a98"),
        "decompile": "005381e0_IScript__LevelWon.c",
        "decompileTokens": ("CGame__DeclareLevelWon", "DAT_008a9a98"),
    },
]


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tsv_by_address(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {row[key].lower(): row for row in read_tsv_rows(path)}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def parse_markdown_table(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in read_text(path).splitlines():
        if not line.startswith("| "):
            continue
        if line.startswith("|---") or line.startswith("| Level ") or line.startswith("|------"):
            continue
        cells = [part.strip() for part in line.strip().strip("|").split("|")]
        if cells and cells[0].isdigit():
            rows.append(cells)
    return rows


def mission_event_corpus() -> dict[str, Any]:
    rows = parse_markdown_table(EVENTS_DOC)
    totals = {
        "levelRows": len(rows),
        "events": sum(int(row[2]) for row in rows),
        "objectiveIds": sum(int(row[3]) for row in rows),
        "primaryComplete": sum(int(row[4]) for row in rows),
        "secondaryComplete": sum(int(row[5]) for row in rows),
        "objectiveComplete": sum(int(row[6]) for row in rows),
        "primaryFailed": sum(int(row[7]) for row in rows),
        "levelWon": sum(int(row[8]) for row in rows),
        "levelLost": sum(int(row[9]) for row in rows),
        "nonzeroOutcomeRows": sum(1 for row in rows if any(int(row[index]) for index in (4, 5, 6, 7, 8, 9))),
    }
    return {
        "source": "reverse-engineering/game-assets/mission-events-index.md",
        **totals,
        "boundary": "loose MSL corpus event/objective/outcome counts only; live loose-MSL loading and packed-vs-loose script selection remain unproven",
    }


def mission_message_corpus() -> dict[str, Any]:
    rows = parse_markdown_table(MESSAGES_DOC)
    totals = {
        "levelRows": len(rows),
        "playCharMessage": sum(int(row[2]) for row in rows),
        "addHelpMessage": sum(int(row[3]) for row in rows),
        "levelLostFamily": sum(int(row[4]) for row in rows),
        "levelWonFamily": sum(int(row[5]) for row in rows),
        "nonzeroOutcomeRows": sum(1 for row in rows if int(row[4]) or int(row[5])),
    }
    return {
        "source": "reverse-engineering/game-assets/mission-message-usage.md",
        **totals,
        "boundary": "message/outcome call-family corpus counts only; voice/audio/HUD output and mission outcomes remain unproven",
    }


def evidence_counts() -> dict[str, int]:
    return {
        "wave580MetadataRows": len(read_tsv_rows(WAVE580 / "post_metadata.tsv")),
        "wave580TagRows": len(read_tsv_rows(WAVE580 / "post_tags.tsv")),
        "wave580XrefRows": len(read_tsv_rows(WAVE580 / "post_xrefs.tsv")),
        "wave580InstructionRows": len(read_tsv_rows(WAVE580 / "post_target_instructions.tsv")),
        "wave580DecompileRows": len(read_tsv_rows(WAVE580 / "post_decompile" / "index.tsv")),
        "wave580VtableRows": len(read_tsv_rows(WAVE580 / "post_vtables.tsv")),
        "wave585MetadataRows": len(read_tsv_rows(WAVE585 / "post" / "metadata.tsv")),
        "wave585TagRows": len(read_tsv_rows(WAVE585 / "post" / "tags.tsv")),
        "wave585XrefRows": len(read_tsv_rows(WAVE585 / "post" / "xrefs.tsv")),
        "wave585InstructionRows": len(read_tsv_rows(WAVE585 / "post" / "instructions.tsv")),
        "wave585DecompileRows": len(read_tsv_rows(WAVE585 / "post" / "decompile" / "index.tsv")),
        "wave1049MetadataRows": len(read_tsv_rows(WAVE1049 / "metadata.tsv")),
        "wave1049XrefRows": len(read_tsv_rows(WAVE1049 / "xrefs.tsv")),
        "wave1049InstructionRows": len(read_tsv_rows(WAVE1049 / "instructions.tsv")),
        "wave1049DecompileRows": len(read_tsv_rows(WAVE1049 / "decompile" / "index.tsv")),
        "wave1049ContextMetadataRows": len(read_tsv_rows(WAVE1049 / "context-metadata.tsv")),
        "wave1049ContextXrefRows": len(read_tsv_rows(WAVE1049 / "context-xrefs.tsv")),
        "wave1049ContextInstructionRows": len(read_tsv_rows(WAVE1049 / "context-instructions.tsv")),
        "wave1049ContextDecompileRows": len(read_tsv_rows(WAVE1049 / "context-decompile" / "index.tsv")),
    }


def descriptor_records() -> dict[str, Any]:
    descriptor = read_json(DESCRIPTOR_SCHEMA)
    records = {record["commandName"]: record for record in descriptor["records"] if record.get("commandName")}
    result: dict[str, Any] = {}
    for command, expected in DESCRIPTOR_SLOTS.items():
        record = records[command]
        result[command] = {
            "index": record["index"],
            "recordAddress": record["recordAddress"],
            "observedNameSymbol": record["observedNameSymbol"],
            "nameStatus": record["nameStatus"],
            "expectedSymbol": expected["symbol"],
        }
    return result


def build_schema() -> dict[str, Any]:
    return {
        "schemaVersion": "missionscript-objective-outcome-command-effect.v1",
        "status": "PASS",
        "source": {
            "evidenceWaves": ["Wave580", "Wave585", "Wave903", "Wave1049"],
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static objective/outcome command-effect bridge mapping for clean-room planning, not runtime proof",
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackup": WAVE1219_BACKUP,
        },
        "evidenceCounts": evidence_counts(),
        "descriptorSlots": descriptor_records(),
        "missionEventCorpus": mission_event_corpus(),
        "missionMessageCorpus": mission_message_corpus(),
        "objectiveHandlers": [
            {key: value for key, value in handler.items() if key not in {"metadataTokens", "decompile", "decompileTokens"}}
            for handler in OBJECTIVE_HANDLERS
        ],
        "outcomeHandlers": [
            {key: value for key, value in handler.items() if key not in {"metadataTokens", "decompile", "decompileTokens"}}
            for handler in OUTCOME_HANDLERS
        ],
        "bridgeContext": {
            "gameSnapshot": "0x0046d470 CGame__FillOutEndLevelData copies objective/slot/end-level summary state into END_LEVEL_DATA context",
            "winTransition": "0x0046f2f0 CGame__DeclareLevelWon marks the game's level-won transition path",
            "lossTransition": "0x0046f430 CGame__DeclareLevelLost records loss reason/player_died flag and marks the level-lost transition path",
            "careerUpdate": "0x0041bd00 CCareer__Update consumes END_LEVEL_DATA on won-level paths and calls CCareer__ReCalcLinks",
            "secondaryObjectivePredicate": "0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete scans secondary objective status slots",
            "claimBoundary": "static call/field-role bridge only; runtime mission outcomes and exact layouts remain unproven",
        },
        "claims": [
            "The static objective handlers map Primary/Secondary Objective Complete/Failed commands to text-id and state writes in primary/secondary CGame objective arrays.",
            "The static outcome handlers map LevelWon, LevelLost, and LevelLostString descriptor names through IScript handlers into CGame level-result transition helpers.",
            "The loose MSL indexes provide reproducible event/message corpus counts while remaining separate from live script-loading and runtime outcome proof.",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime command effects",
            "runtime objective UI behavior",
            "runtime level outcome behavior",
            "runtime save behavior",
            "runtime career progression",
            "live loose-MSL loading",
            "packed-vs-loose script selection",
            "exact command descriptor layout",
            "exact arity",
            "exact argument type schema",
            "exact CGame layout",
            "exact CCareer layout",
            "exact END_LEVEL_DATA layout",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
    }


def require_tokens(label: str, text: str, tokens: tuple[str, ...], failures: list[str]) -> None:
    for token in tokens:
        require(token in text, f"{label} missing token: {token}", failures)


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def check_schema(failures: list[str]) -> None:
    expected = build_schema()
    for path in (SCHEMA, LORE_SCHEMA):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} does not match generated schema", failures)
        require(actual["missionEventCorpus"]["levelRows"] == 95, "event corpus level-row mismatch", failures)
        require(actual["missionEventCorpus"]["events"] == 795, "event corpus event-count mismatch", failures)
        require(actual["missionEventCorpus"]["primaryComplete"] == 115, "primary complete count mismatch", failures)
        require(actual["missionEventCorpus"]["secondaryComplete"] == 42, "secondary complete count mismatch", failures)
        require(actual["missionEventCorpus"]["primaryFailed"] == 102, "primary failed count mismatch", failures)
        require(actual["missionEventCorpus"]["levelWon"] == 79, "event level-won count mismatch", failures)
        require(actual["missionEventCorpus"]["levelLost"] == 13, "event level-lost count mismatch", failures)
        require(actual["missionMessageCorpus"]["levelLostFamily"] == 110, "message level-lost family count mismatch", failures)
        require(actual["missionMessageCorpus"]["levelWonFamily"] == 71, "message level-won family count mismatch", failures)
        for command, expected_slot in DESCRIPTOR_SLOTS.items():
            record = actual["descriptorSlots"].get(command)
            require(record is not None, f"missing descriptor slot for {command}", failures)
            if record is not None:
                require(record["index"] == expected_slot["index"], f"{command} descriptor index mismatch", failures)
                require(record["recordAddress"] == expected_slot["recordAddress"], f"{command} descriptor address mismatch", failures)
                require(record["observedNameSymbol"] == expected_slot["symbol"], f"{command} descriptor symbol mismatch", failures)
        check_no_bad_tokens(path, failures)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "wave580MetadataRows": 6,
        "wave580TagRows": 6,
        "wave580XrefRows": 6,
        "wave580InstructionRows": 5454,
        "wave580DecompileRows": 6,
        "wave580VtableRows": 36,
        "wave585MetadataRows": 5,
        "wave585TagRows": 5,
        "wave585XrefRows": 5,
        "wave585InstructionRows": 1845,
        "wave585DecompileRows": 5,
        "wave1049MetadataRows": 10,
        "wave1049XrefRows": 13,
        "wave1049InstructionRows": 761,
        "wave1049DecompileRows": 10,
        "wave1049ContextMetadataRows": 12,
        "wave1049ContextXrefRows": 23,
        "wave1049ContextInstructionRows": 6129,
        "wave1049ContextDecompileRows": 12,
    }
    actual_counts = evidence_counts()
    for key, expected in expected_counts.items():
        require(actual_counts.get(key) == expected, f"{key} mismatch: {actual_counts.get(key)} != {expected}", failures)

    wave580_metadata = tsv_by_address(WAVE580 / "post_metadata.tsv")
    for handler in OBJECTIVE_HANDLERS:
        row = wave580_metadata.get(handler["address"])
        require(row is not None, f"missing Wave580 metadata row {handler['address']}", failures)
        if row is not None:
            require(row["name"] == handler["name"], f"Wave580 name mismatch at {handler['address']}", failures)
            require_tokens(f"Wave580 comment {handler['address']}", row["comment"], handler["metadataTokens"], failures)
        decompile = read_text(WAVE580 / "post_decompile" / handler["decompile"])
        require_tokens(f"Wave580 decompile {handler['address']}", decompile, handler["decompileTokens"], failures)

    wave585_metadata = tsv_by_address(WAVE585 / "post" / "metadata.tsv")
    for handler in OUTCOME_HANDLERS:
        row = wave585_metadata.get(handler["address"])
        require(row is not None, f"missing Wave585 metadata row {handler['address']}", failures)
        if row is not None:
            require(row["name"] == handler["name"], f"Wave585 name mismatch at {handler['address']}", failures)
            require_tokens(f"Wave585 comment {handler['address']}", row["comment"], handler["metadataTokens"], failures)
        decompile = read_text(WAVE585 / "post" / "decompile" / handler["decompile"])
        require_tokens(f"Wave585 decompile {handler['address']}", decompile, handler["decompileTokens"], failures)

    wave580_backup = read_json(WAVE580 / "wave580_backup_summary.json")
    require(wave580_backup.get("destination") == WAVE580_BACKUP, "Wave580 backup path mismatch", failures)
    require(wave580_backup.get("status") == "PASS", "Wave580 backup status mismatch", failures)
    require(wave580_backup.get("diffCount") == 0, "Wave580 backup diff mismatch", failures)

    wave585_backup = read_json(WAVE585 / "backup_summary.json")
    require(wave585_backup.get("backupPath") == WAVE585_BACKUP, "Wave585 backup path mismatch", failures)
    require(wave585_backup.get("diffCount") == 0, "Wave585 backup diff mismatch", failures)

    wave1049_backup = read_json(WAVE1049 / "backup-summary.json")
    require(wave1049_backup.get("backupPath") == WAVE1049_BACKUP, "Wave1049 backup path mismatch", failures)
    require(wave1049_backup.get("diffCount") == 0, "Wave1049 backup diff mismatch", failures)
    require(wave1049_backup.get("hashDiffCount") == 0, "Wave1049 backup hash diff mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        "MissionScript Objective/Outcome Command-Effect Static Proof",
        PROOF_LINK,
        SCHEMA_LINK,
        "Status: static objective/outcome command-effect schema proof complete, not runtime proof",
        "PrimaryObjectiveComplete",
        "SecondaryObjectiveComplete",
        "PrimaryObjectiveFailed",
        "SecondaryObjectiveFailed",
        "LevelWon",
        "LevelLost",
        "LevelLostString",
        "IScript__PrimaryObjectiveComplete",
        "IScript__SecondaryObjectiveFailed",
        "IScript__LevelLostString",
        "CGame__FillOutEndLevelData",
        "CGame__DeclareLevelWon",
        "CGame__DeclareLevelLost",
        "CCareer__Update",
        "CEndLevelData__IsAllSecondaryObjectivesComplete",
        "DAT_008a9adc",
        "DAT_008a9b2c",
        "115 primary-complete",
        "42 secondary-complete",
        "102 primary-failed",
        "79 LevelWon",
        "13 LevelLost",
        "110 LevelLost-family",
        "71 LevelWon-family",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1560/1560 = 100.00%",
        "1179/1179 = 100.00%",
        WAVE1219_BACKUP,
    )
    for path in (PROOF, LORE_PROOF, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_tokens(path, failures)

    front_door_docs = (
        CONTRACT,
        PROOF_PLAN,
        BACKLOG,
        LORE_BACKLOG,
        MAPPED,
        LORE_MAPPED,
        BIN_INDEX,
        LORE_BIN_INDEX,
        RE_INDEX,
        LORE_RE_INDEX,
        ISCRIPT_DOC,
        EVENTS_DOC,
        MESSAGES_DOC,
        MSL_SCRIPTING,
        MSL_COMMANDS,
        GAME_INDEX,
        CAREER_INDEX,
        ENDLEVEL_INDEX,
        CGAME_FILL_DOC,
        CGAME_WON_DOC,
        CGAME_LOST_DOC,
        CCAREER_UPDATE_DOC,
        ENDLEVEL_SECONDARY_DOC,
    )
    for path in front_door_docs:
        text = read_text(path)
        for token in (PROOF_LINK, SCHEMA_LINK, "MissionScript Objective/Outcome Command-Effect"):
            require(token in text, f"{path.relative_to(ROOT)} missing objective/outcome proof token: {token}", failures)
        check_no_bad_tokens(path, failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\missionscript_objective_outcome_command_effect_static_probe.py --check"
    actual_script = package.get("scripts", {}).get("test:missionscript-objective-outcome-command-effect-static")
    require(actual_script == expected_script, "package script mismatch", failures)

    progress = read_json(PROGRESS)
    require(progress["functionQuality"]["commentedFunctions"] == 6411, "static progress commented count mismatch", failures)
    current_risk = progress["post100Reaudit"]["currentRiskRank"]
    require(current_risk["focusedReviewed"] == 1179, "current-risk progress mismatch", failures)
    require(current_risk["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining count mismatch", failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_schema(failures)
    check_artifacts(failures)
    check_docs(failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate existing artifacts")
    parser.add_argument("--write-schema", action="store_true", help="write generated schema JSON artifacts")
    args = parser.parse_args()

    if args.write_schema:
        schema = build_schema()
        write_json(SCHEMA, schema)
        write_json(LORE_SCHEMA, schema)
        print(f"Wrote {SCHEMA.relative_to(ROOT)}")
        print(f"Wrote {LORE_SCHEMA.relative_to(ROOT)}")

    if args.check or not args.write_schema:
        failures = run_check()
        if failures:
            print("MissionScript objective/outcome command-effect static probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript objective/outcome command-effect static probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
