#!/usr/bin/env python3
"""Validate the MissionScript Level100 tutorial static walkthrough proof plan."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

LEVEL_DIR = ROOT / "game" / "data" / "MissionScripts" / "level100"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough-proof-plan.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_static_walkthrough_proof_plan_2026-06-08.md"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"

MSL_DOC = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
LORE_MSL_DOC = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "msl-scripting.md"
MISSION_INDEX = ROOT / "reverse-engineering" / "game-assets" / "mission-scripts-index.md"
LORE_MISSION_INDEX = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-scripts-index.md"
MISSION_EVENTS = ROOT / "reverse-engineering" / "game-assets" / "mission-events-index.md"
LORE_MISSION_EVENTS = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-events-index.md"
MISSION_THINGS = ROOT / "reverse-engineering" / "game-assets" / "mission-thing-usage.md"
LORE_MISSION_THINGS = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-thing-usage.md"
MISSION_SLOTS = ROOT / "reverse-engineering" / "game-assets" / "mission-slot-usage.md"
LORE_MISSION_SLOTS = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-slot-usage.md"
MISSION_MESSAGES = ROOT / "reverse-engineering" / "game-assets" / "mission-message-usage.md"
LORE_MISSION_MESSAGES = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-message-usage.md"
MISSION_MESSAGE_CALLSITES = ROOT / "reverse-engineering" / "game-assets" / "mission-message-usage-callsites-1.md"
LORE_MISSION_MESSAGE_CALLSITES = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-message-usage-callsites-1.md"
MISSION_SPEAKERS = ROOT / "reverse-engineering" / "game-assets" / "mission-speaker-index.md"
LORE_MISSION_SPEAKERS = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-speaker-index.md"

MISSIONSCRIPT_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
LORE_MISSIONSCRIPT_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
MISSIONSCRIPT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_MISSIONSCRIPT_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
PACKED_LOOSE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection-proof-plan.md"
LORE_PACKED_LOOSE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection-proof-plan.md"
EVENT_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle-proof.md"
LORE_EVENT_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle-proof.md"
TEXT_SPEAKER_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md"
LORE_TEXT_SPEAKER_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md"
TEXT_SPEAKER_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution.v1.json"
LORE_TEXT_SPEAKER_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution.v1.json"

PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
PROOF_LINK = "missionscript-level100-tutorial-static-walkthrough-proof-plan.md"
SCHEMA_LINK = "missionscript-level100-tutorial-static-walkthrough.v1.json"
TEXT_SPEAKER_PROOF_LINK = "missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md"
TEXT_SPEAKER_SCHEMA_LINK = "missionscript-level100-tutorial-text-speaker-resolution.v1.json"
NEXT_SLICE = "MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan"
BOUNDARY_SLICE = "Completed MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan"
BOUNDARY_PROOF_LINK = "missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md"
BOUNDARY_SCHEMA_LINK = "missionscript-level100-tutorial-runtime-harness-boundary.v1.json"
FOLLOWUP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Boundary Planning Proof Plan"

COMMANDS = (
    "PostEvent",
    "PrimaryObjectiveFailed",
    "PrimaryObjectiveComplete",
    "LevelWon",
    "LevelLost",
    "LevelLostString",
    "GetSlot",
    "SetSlotSave",
    "PlayCharMessage",
    "PlayCharMessageWait",
    "AddHelpMessage",
    "HighlightHudPart",
    "UnHighlightHudPart",
    "GetThingRef",
    "SpawnThing",
    "DisableWeapon",
    "EnableWeapon",
    "DisableFlightMode",
    "EnableFlightMode",
    "AddScore",
    "SetObjective",
    "UnsetObjective",
    "Activate",
    "Deactivate",
)

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
    "runtime event outcomes proven",
    "live loose-msl loading proven",
    "packed-vs-loose script selection proven",
    "level100 runtime proven",
    "tutorial runtime proven",
    "visual qa complete",
    "godot parity proven",
    "bea patching behavior proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def strip_line_comment(line: str) -> str:
    return line.split("//", 1)[0]


def parse_level100_corpus() -> dict[str, Any]:
    files = sorted(LEVEL_DIR.glob("*.msl"))
    summary: dict[str, Any] = {
        "fileCount": len(files),
        "files": [path.name for path in files],
        "totalLines": 0,
        "eventDefinitions": [],
        "postEvents": [],
        "commandCounts": dict.fromkeys(COMMANDS, 0),
        "getThingRefs": [],
        "spawnThings": [],
        "slotRefs": [],
        "objectiveTokens": [],
        "messageTokens": [],
        "helpTokens": [],
        "hudParts": [],
    }
    summary["commandCounts"] = {command: 0 for command in COMMANDS}

    for path in files:
        lines = read_text(path).splitlines()
        summary["totalLines"] += len(lines)
        for line_number, line in enumerate(lines, start=1):
            code = strip_line_comment(line)
            for command in COMMANDS:
                summary["commandCounts"][command] += len(re.findall(r"\b" + re.escape(command) + r"\s*\(", code))
            for match in re.finditer(r'event\s*\(\s*"([^"]+)"\s*\)', code):
                summary["eventDefinitions"].append({"file": path.name, "line": line_number, "event": match.group(1)})
            for match in re.finditer(r'PostEvent\s*\(\s*"([^"]+)"\s*\)', code):
                summary["postEvents"].append({"file": path.name, "line": line_number, "event": match.group(1)})
            for match in re.finditer(r'GetThingRef\s*\(\s*"([^"]+)"\s*\)', code):
                summary["getThingRefs"].append({"file": path.name, "line": line_number, "thing": match.group(1)})
            for match in re.finditer(r'SpawnThing\s*\(\s*"([^"]+)"\s*,\s*"([^"]*)"\s*,\s*([^,]+)\s*,\s*"([^"]+)"', code):
                summary["spawnThings"].append(
                    {
                        "file": path.name,
                        "line": line_number,
                        "thing": match.group(1),
                        "spawner": match.group(2),
                        "count": match.group(3).strip(),
                        "script": match.group(4),
                    }
                )
            for match in re.finditer(r"\b(GetSlot|SetSlotSave)\s*\(\s*([A-Z0-9_]+)", code):
                summary["slotRefs"].append(
                    {"file": path.name, "line": line_number, "call": match.group(1), "slot": match.group(2)}
                )
            for match in re.finditer(r"\b(PrimaryObjectiveFailed|PrimaryObjectiveComplete)\s*\([^,]+,\s*([A-Z0-9_]+)\s*\)", code):
                summary["objectiveTokens"].append(
                    {"file": path.name, "line": line_number, "call": match.group(1), "objective": match.group(2)}
                )
            for match in re.finditer(r"\b(PlayCharMessageWait|PlayCharMessage)\s*\(\s*([^,]+)\s*,\s*([^,\)]+)", code):
                summary["messageTokens"].append(
                    {
                        "file": path.name,
                        "line": line_number,
                        "call": match.group(1),
                        "speaker": match.group(2).strip(),
                        "token": match.group(3).strip(),
                    }
                )
            for match in re.finditer(r"AddHelpMessage\s*\(\s*([A-Z0-9_]+)\s*\)", code):
                summary["helpTokens"].append({"file": path.name, "line": line_number, "token": match.group(1)})
            for match in re.finditer(r"\b(HighlightHudPart|UnHighlightHudPart)\s*\(\s*([A-Z0-9_]+)\s*\)", code):
                summary["hudParts"].append(
                    {"file": path.name, "line": line_number, "call": match.group(1), "part": match.group(2)}
                )

    add_unique(summary, "eventDefinitions", "event")
    add_unique(summary, "postEvents", "event")
    add_unique(summary, "getThingRefs", "thing")
    add_unique(summary, "slotRefs", "slot")
    add_unique(summary, "objectiveTokens", "objective")
    add_unique(summary, "messageTokens", "token")
    add_unique(summary, "helpTokens", "token")
    add_unique(summary, "hudParts", "part")

    summary["speakerCounts"] = dict(Counter(row["speaker"] for row in summary["messageTokens"]))
    summary["spawnThingTypes"] = sorted(set(row["thing"] for row in summary["spawnThings"]))
    summary["spawnScripts"] = sorted(set(row["script"] for row in summary["spawnThings"]))
    summary["mismatchedPostedEvents"] = sorted(
        set(summary["postEventsUnique"]) - set(summary["eventDefinitionsUnique"])
    )
    return summary


def add_unique(summary: dict[str, Any], key: str, value_key: str) -> None:
    values = [row[value_key] for row in summary[key]]
    summary[f"{key}Count"] = len(values)
    summary[f"{key}UniqueCount"] = len(set(values))
    summary[f"{key}Unique"] = sorted(set(values))


def build_schema() -> dict[str, Any]:
    corpus = parse_level100_corpus()
    command_counts = corpus["commandCounts"]
    return {
        "schemaVersion": "missionscript-level100-tutorial-static-walkthrough.v1",
        "status": "PASS",
        "source": {
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static Level100 tutorial mission walkthrough tying loose corpus rows to existing MissionScript command/event/object-reference schemas",
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackup": BACKUP,
        },
        "level100Corpus": {
            "directory": "game/data/MissionScripts/level100",
            "fileCount": corpus["fileCount"],
            "extraScriptCount": 24,
            "totalMslLines": corpus["totalLines"],
            "files": corpus["files"],
            "englishTokenBlocks": 52,
            "globalTextPresent": True,
            "levelTextStfPresent": True,
            "levelTextStfEmpty": True,
            "boundary": "loose corpus/reference evidence only; raw game corpus remains private/release-deny and this schema records aggregate/token-level facts",
        },
        "eventWalkthrough": {
            "uniqueEventNames": corpus["eventDefinitionsUniqueCount"],
            "eventHandlerDeclarations": corpus["eventDefinitionsCount"],
            "postEventCallsites": corpus["postEventsCount"],
            "postEventUniqueNames": corpus["postEventsUniqueCount"],
            "events": corpus["eventDefinitionsUnique"],
            "mismatchedPostedEvents": corpus["mismatchedPostedEvents"],
            "keyPath": [
                "LevelScript.msl:init",
                "Reached Target Zone 1",
                "Reached Firing Range",
                "Activate Static Targets",
                "Static Target Destroyed",
                "Activate Static Targets 2",
                "Static Target 2 Destroyed",
                "Activate Moving Targets",
                "Moving Target Destroyed",
                "Trainer Attack",
                "Cease Trainer Attack",
                "Reached Target Zone 2",
                "Activate Airborne Targets 1",
                "Airborne Target 1 Destroyed",
                "Reached Target Zone 3",
                "Activate Airborne Targets 2",
                "Airborne Target 2 Destroyed",
                "Reached Target Zone 4",
                "LevelWon",
            ],
            "sourceBoundary": "event strings are preserved exactly; mismatched posted events are not normalized or treated as runtime behavior",
        },
        "commandFamilies": {
            "objectiveOutcome": {
                "primaryObjectiveFailed": command_counts["PrimaryObjectiveFailed"],
                "primaryObjectiveComplete": command_counts["PrimaryObjectiveComplete"],
                "levelWon": command_counts["LevelWon"],
                "levelLost": command_counts["LevelLost"],
                "levelLostString": command_counts["LevelLostString"],
                "objectives": corpus["objectiveTokensUnique"],
            },
            "slotPersistence": {
                "getSlot": command_counts["GetSlot"],
                "setSlotSave": command_counts["SetSlotSave"],
                "slotRefs": corpus["slotRefsUnique"],
                "slotRefRows": corpus["slotRefsCount"],
            },
            "messageAudio": {
                "playCharMessage": command_counts["PlayCharMessage"],
                "playCharMessageWait": command_counts["PlayCharMessageWait"],
                "combinedPlayCharMessage": command_counts["PlayCharMessage"] + command_counts["PlayCharMessageWait"],
                "addHelpMessage": command_counts["AddHelpMessage"],
                "messageTokens": corpus["messageTokensUniqueCount"],
                "speakerCounts": corpus["speakerCounts"],
                "helpTokens": corpus["helpTokensUnique"],
            },
            "hudDisplay": {
                "highlightHudPart": command_counts["HighlightHudPart"],
                "unhighlightHudPart": command_counts["UnHighlightHudPart"],
                "hudParts": corpus["hudPartsUnique"],
            },
            "thingSpawn": {
                "getThingRefRaw": command_counts["GetThingRef"],
                "getThingRefUnique": corpus["getThingRefsUniqueCount"],
                "getThingRefs": corpus["getThingRefsUnique"],
                "spawnThingRaw": command_counts["SpawnThing"],
                "spawnThingTypes": corpus["spawnThingTypes"],
                "spawnScripts": corpus["spawnScripts"],
            },
            "playerThingControl": {
                "disableWeapon": command_counts["DisableWeapon"],
                "enableWeapon": command_counts["EnableWeapon"],
                "disableFlightMode": command_counts["DisableFlightMode"],
                "enableFlightMode": command_counts["EnableFlightMode"],
                "addScore": command_counts["AddScore"],
                "setObjective": command_counts["SetObjective"],
                "unsetObjective": command_counts["UnsetObjective"],
                "activate": command_counts["Activate"],
                "deactivate": command_counts["Deactivate"],
            },
        },
        "staticDependencies": {
            "descriptorRegistry": {
                "descriptorTable": "0x0064ce50",
                "declaredSlots": 144,
                "registryInitializer": "0x0052ff30 ScriptCommandRegistry__InitBuiltins",
            },
            "vmDatatypeOpcode": {
                "callBridge": "0x0052ea40 CAsmInstruction__ExecuteCall",
                "datatypeFactory": "0x0052ec60 CDataType__CreateFromType",
                "runLoop": "0x00539b00 CScriptObjectCode__Run",
                "scriptStateStack": "script_state+0x218",
                "scriptObjectCodeStack": "script_object_code+0x68",
            },
            "eventLifecycle": [
                "0x005383c0 IScript__ScheduleEvent",
                "0x00538b70 CScriptEventNB__PostEvent",
                "0x0052fda0 CEventFunction__Execute",
                "0x00539a60 CScriptObjectCode__CallEventDirect",
                "0x00539b00 CScriptObjectCode__Run",
            ],
            "sourceSelectionBoundary": [
                "0x00539dc0 CMissionScriptObjectCode__StartLoadAsync",
                "0x00539ca0 CMissionScriptObjectCode__LoadAsync",
                "this+0x20",
                "this+0x124",
                "CDXMemBuffer__InitFromFile",
            ],
            "commandEffectProofs": [
                "missionscript-slot-command-effect-static-proof.md",
                "missionscript-objective-outcome-command-effect-static-proof.md",
                "missionscript-message-audio-command-effect-static-proof.md",
                "missionscript-hud-display-command-effect-static-proof.md",
                "missionscript-thing-value-engine-helper-command-effect-static-proof.md",
                "missionscript-player-state-score-command-effect-static-proof.md",
                "world-thing-spawn-spawner-handoff-static-proof.md",
                "world-thing-spawn-getthingref-object-reference-static-proof.md",
            ],
        },
        "claims": [
            "Level100 now has a public-safe static walkthrough map tying the loose tutorial corpus to existing MissionScript command, event, VM, and object-reference static schemas.",
            "The proof preserves exact event/string token boundaries, including the mismatched posted event Destroyed Friendly Building versus declared Friendly Building Destroyed.",
            "The walkthrough is strong enough to plan a later copied/app-owned Level100 runtime or rebuild slice without widening static claims into runtime behavior.",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime command effects",
            "runtime event outcomes",
            "live loose-MSL loading",
            "packed-vs-loose script selection",
            "runtime Level100 mission outcome",
            "runtime objective UI",
            "runtime message or audio output",
            "runtime HUD flashing",
            "runtime object identity",
            "runtime SpawnThing behavior",
            "runtime GetThingRef lookup behavior",
            "exact descriptor/datatype/object-code layout",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
        "nextStaticSlice": FOLLOWUP_SLICE,
    }


def check_schema(failures: list[str]) -> None:
    expected = build_schema()
    stored = read_json(SCHEMA)
    require(stored == expected, "Level100 walkthrough schema is not regenerated from current corpus evidence", failures)
    require(read_json(LORE_SCHEMA) == stored, "lore Level100 walkthrough schema mirror mismatch", failures)
    serialized = json.dumps(stored, sort_keys=True)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in serialized, f"schema leaks public-forbidden token: {token}", failures)


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore Level100 walkthrough proof mirror mismatch", failures)

    core_tokens = (
        "MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan",
        "Status: static walkthrough proof plan complete, not runtime proof",
        PROOF_LINK,
        SCHEMA_LINK,
        "level100",
        "LevelScript.msl",
        "25",
        "24",
        "1469",
        "26",
        "34",
        "41",
        "Destroyed Friendly Building",
        "Friendly Building Destroyed",
        "_100_OBJECTIVE_1",
        "_100_OBJECTIVE_4",
        "4` `GetSlot`",
        "4` `SetSlotSave`",
        "45",
        "6",
        "43",
        "P_TATIANA",
        "P_KRAMER",
        "P_TECHNICIAN",
        "7` `HighlightHudPart`",
        "7` `UnHighlightHudPart`",
        "18",
        "15",
        "20",
        "Target Drone",
        "Air Trainer",
        "Target Tank",
        "Target Truck",
        "AddScore",
        "0x005383c0 IScript__ScheduleEvent",
        "0x00538b70 CScriptEventNB__PostEvent",
        "0x0052fda0 CEventFunction__Execute",
        "0x00539a60 CScriptObjectCode__CallEventDirect",
        "0x00539b00 CScriptObjectCode__Run",
        "0x0064ce50",
        "144",
        "0x0052ea40",
        "0x0052ec60",
        "0x00539dc0 CMissionScriptObjectCode__StartLoadAsync",
        "0x00539ca0 CMissionScriptObjectCode__LoadAsync",
        "this+0x20",
        "this+0x124",
        "CDXMemBuffer__InitFromFile",
        BACKUP,
        TEXT_SPEAKER_PROOF_LINK,
        TEXT_SPEAKER_SCHEMA_LINK,
        "68/68",
        "0 missing",
        NEXT_SLICE,
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_tokens(path, failures)

    linked_paths = (
        BACKLOG,
        MAPPED,
        BIN_INDEX,
        RE_INDEX,
        MSL_DOC,
        MISSION_INDEX,
        MISSION_EVENTS,
        MISSION_THINGS,
        MISSION_SLOTS,
        MISSION_MESSAGES,
        MISSION_MESSAGE_CALLSITES,
        MISSION_SPEAKERS,
        MISSIONSCRIPT_PLAN,
        MISSIONSCRIPT_CONTRACT,
        PACKED_LOOSE,
        EVENT_PROOF,
        TEXT_SPEAKER_PROOF,
    )
    for path in linked_paths:
        text = read_text(path)
        require(PROOF_LINK in text, f"{path.relative_to(ROOT)} missing Level100 walkthrough proof link", failures)
        require(SCHEMA_LINK in text, f"{path.relative_to(ROOT)} missing Level100 walkthrough schema link", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (MSL_DOC, LORE_MSL_DOC),
        (MISSION_INDEX, LORE_MISSION_INDEX),
        (MISSION_EVENTS, LORE_MISSION_EVENTS),
        (MISSION_THINGS, LORE_MISSION_THINGS),
        (MISSION_SLOTS, LORE_MISSION_SLOTS),
        (MISSION_MESSAGES, LORE_MISSION_MESSAGES),
        (MISSION_MESSAGE_CALLSITES, LORE_MISSION_MESSAGE_CALLSITES),
        (MISSION_SPEAKERS, LORE_MISSION_SPEAKERS),
        (MISSIONSCRIPT_PLAN, LORE_MISSIONSCRIPT_PLAN),
        (MISSIONSCRIPT_CONTRACT, LORE_MISSIONSCRIPT_CONTRACT),
        (PACKED_LOOSE, LORE_PACKED_LOOSE),
        (EVENT_PROOF, LORE_EVENT_PROOF),
        (TEXT_SPEAKER_PROOF, LORE_TEXT_SPEAKER_PROOF),
        (TEXT_SPEAKER_SCHEMA, LORE_TEXT_SPEAKER_SCHEMA),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require("Completed MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan" in backlog, "backlog missing completed Level100 slice", failures)
    require("Completed MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan" in backlog, "backlog missing completed text/speaker slice", failures)
    require(BOUNDARY_SLICE in backlog, "backlog missing completed runtime-harness boundary slice", failures)
    require(BOUNDARY_PROOF_LINK in backlog, "backlog missing runtime-harness boundary proof link", failures)
    require(BOUNDARY_SCHEMA_LINK in backlog, "backlog missing runtime-harness boundary schema link", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}" in backlog, "backlog missing copied-profile runtime-observation planning slice", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}" not in backlog, "backlog still marks runtime-harness boundary active", failures)
    require("The selected active static-to-proof slice is MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan" not in backlog, "backlog still marks Level100 walkthrough active", failures)
    require("The selected active static-to-proof slice is MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan" not in backlog, "backlog still marks text/speaker active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-static-walkthrough")
        == r"py -3 tools\missionscript_level100_tutorial_static_walkthrough_probe.py --check",
        "missing package Level100 walkthrough test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-schema", action="store_true")
    args = parser.parse_args()

    if args.write_schema:
        schema = build_schema()
        write_json(SCHEMA, schema)
        write_json(LORE_SCHEMA, schema)
        print(f"Wrote {SCHEMA.relative_to(ROOT)}")
        print(f"Wrote {LORE_SCHEMA.relative_to(ROOT)}")
        return 0

    failures: list[str] = []
    check_schema(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("MissionScript Level100 tutorial static walkthrough probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 tutorial static walkthrough probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
