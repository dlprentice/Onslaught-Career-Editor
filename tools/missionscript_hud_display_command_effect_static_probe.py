#!/usr/bin/env python3
"""Validate the MissionScript HUD/display command-effect static proof."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect-static-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect-static-proof.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_hud_display_command_effect_static_proof_2026-06-08.md"

DESCRIPTOR_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-descriptor-schema.v1.json"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
PROOF_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
MESSAGE_AUDIO_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect-static-proof.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
LORE_ISCRIPT_DOC = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
MSL_DOC = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
LORE_MSL_DOC = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "msl-scripting.md"
MSL_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
LORE_MSL_COMMANDS = ROOT / "lore-book" / "reverse-engineering" / "quick-reference" / "msl-commands.md"
HUD_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "hud-frontend-overlay-static-contract.md"
LORE_HUD_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "hud-frontend-overlay-static-contract.md"
WORLD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "World.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"

MSL_ROOT = ROOT / "game" / "data" / "MissionScripts"
WAVE1219_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"

PROOF_LINK = "missionscript-hud-display-command-effect-static-proof.md"
SCHEMA_LINK = "missionscript-hud-display-command-effect.v1.json"

DESCRIPTOR_COMMANDS = {
    "HighlightHudPart": {
        "index": 33,
        "recordAddress": "0x0064d690",
        "rawEntryValue": "&LAB_00535d70",
        "shape": {"+0x14": "1", "+0x1c": "1", "+0x38": "1"},
    },
    "UnHighlightHudPart": {
        "index": 34,
        "recordAddress": "0x0064d6d0",
        "rawEntryValue": "&LAB_00535e60",
        "shape": {"+0x14": "1", "+0x1c": "1", "+0x38": "1"},
    },
    "InitVariable": {
        "index": 75,
        "recordAddress": "0x0064e110",
        "rawEntryValue": "&LAB_00536210",
        "shape": {"+0x14": "2", "+0x1c": "1", "+0x20": "1", "+0x38": "2"},
    },
    "SetVariable": {
        "index": 76,
        "recordAddress": "0x0064e150",
        "rawEntryValue": "&LAB_00536230",
        "shape": {"+0x14": "3", "+0x1c": "1", "+0x20": "2", "+0x24": "2", "+0x38": "2"},
    },
    "ShutdownVariable": {
        "index": 77,
        "recordAddress": "0x0064e190",
        "rawEntryValue": "&LAB_00536260",
        "shape": {"+0x14": "1", "+0x1c": "1", "+0x38": "2"},
    },
}

EXPECTED_COUNTS = {
    "HighlightHudPart": {"calls": 13, "files": 2},
    "UnHighlightHudPart": {"calls": 13, "files": 2},
    "InitVariable": {"calls": 77, "files": 41},
    "SetVariable": {"calls": 146, "files": 45},
    "ShutdownVariable": {"calls": 26, "files": 18},
}

HUD_CONSTANTS = {
    "HUD_HEALTH_BAR": 0,
    "HUD_ENERGY_BAR": 1,
    "HUD_COMPASS": 2,
    "HUD_BATTLE_LINE_MAP": 3,
    "HUD_RADAR": 4,
    "HUD_CURRENT_WEAPON": 5,
}

VARIABLE_TYPES = {
    "VARIABLE_NUMBER": 1,
    "VARIABLE_NUMBER_AND_THRESHOLD": 2,
    "VARIABLE_TIMER": 3,
    "VARIABLE_PERCENTAGE": 4,
    "VARIABLE_PERCENTAGE_AND_THRESHOLD": 5,
    "VARIABLE_TIME": 6,
}

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
    "runtime hud behavior proven",
    "visible flashing proven",
    "runtime variable display proven",
    "message overlay proven",
    "render ordering proven",
    "exact hud layout proven",
    "exact command descriptor layout proven",
    "exact descriptor layout proven",
    "exact datatype layout proven",
    "live script loading proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
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


def require_tokens(label: str, text: str, tokens: tuple[str, ...], failures: list[str]) -> None:
    for token in tokens:
        require(token in text, f"{label} missing token: {token}", failures)


def descriptor_records() -> dict[str, Any]:
    schema = read_json(DESCRIPTOR_SCHEMA)
    records = {record["commandName"]: record for record in schema["records"] if record.get("commandName")}
    result: dict[str, Any] = {}
    for command, expected in DESCRIPTOR_COMMANDS.items():
        record = records[command]
        raw = {item["offset"]: item["value"] for item in record["rawAssignments"]}
        result[command] = {
            "index": record["index"],
            "recordAddress": record["recordAddress"],
            "observedNameSymbol": record["observedNameSymbol"],
            "rawEntryValue": raw["+0x00"],
            "nonzeroRawShape": {offset: raw[offset] for offset in expected["shape"]},
            "boundary": "descriptor-row/raw-entry static evidence only; handler-body semantics, exact descriptor layout, exact arity, runtime HUD behavior, and runtime variable display remain unproven",
        }
    return result


def command_usage() -> dict[str, Any]:
    usage: dict[str, Any] = {
        command: {"calls": 0, "files": 0, "sampleRows": []}
        for command in DESCRIPTOR_COMMANDS
    }
    if not MSL_ROOT.is_dir():
        return {
            "source": "game/data/MissionScripts/**/*.msl",
            "directNonCommentCounts": usage,
            "boundary": "private loose-MSL scan unavailable in this workspace",
        }

    patterns = {
        command: re.compile(rf"(^|[^A-Za-z0-9_]){re.escape(command)}\s*\(")
        for command in DESCRIPTOR_COMMANDS
    }
    files_seen = {command: set() for command in DESCRIPTOR_COMMANDS}
    for path in sorted(MSL_ROOT.rglob("*.msl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue
            for command, pattern in patterns.items():
                if pattern.search(stripped):
                    usage[command]["calls"] += 1
                    files_seen[command].add(str(path.relative_to(ROOT)))
                    if len(usage[command]["sampleRows"]) < 8:
                        usage[command]["sampleRows"].append(f"{path.relative_to(ROOT)}:{line_number}:{stripped}")

    for command, seen in files_seen.items():
        usage[command]["files"] = len(seen)

    return {
        "source": "game/data/MissionScripts/**/*.msl",
        "directNonCommentCounts": usage,
        "boundary": "private loose-MSL scan only; command-token usage rows are static corpus context and do not prove live loose-MSL loading, packed-resource selection, runtime HUD behavior, or runtime variable display",
    }


def build_schema() -> dict[str, Any]:
    return {
        "schemaVersion": "missionscript-hud-display-command-effect.v1",
        "status": "PASS",
        "source": {
            "evidenceWaves": ["Wave584", "Wave903", "Wave1073", "Wave1158", "Wave1216", "Wave1219"],
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static MissionScript HUD/display descriptor, loose-corpus, HUD-contract, and world-text context bridge for clean-room planning",
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackup": WAVE1219_BACKUP,
        },
        "descriptorRecords": descriptor_records(),
        "hudConstants": HUD_CONSTANTS,
        "variableTypes": VARIABLE_TYPES,
        "looseMslUsage": command_usage(),
        "hudStaticBridge": {
            "contract": "hud-frontend-overlay-static-contract.md",
            "anchors": [
                "CHud__SetHudComponent",
                "CHud__RenderOverlayForViewpoint",
                "CHud__RenderBattleline",
                "CHud__RenderActiveHudComponentPass",
                "CHud__RenderTacticalRadarContacts",
                "CHud__RenderObjectiveStatusPanel",
                "CHudComponent__RenderPass",
                "this+0x1fc active HUD component slot",
                "this+0x200 pending HUD component slot",
            ],
            "boundary": "HUD component/render anchors are static planning context only; no static call path from the five descriptor raw entries into CHud render/component functions is claimed here",
        },
        "worldTextBridge": {
            "ownerDoc": "functions/World.cpp/_index.md",
            "anchors": [
                "CWorld__PushWorldTextSlot",
                "CWorld__UpdateWorldTextSlotTiming",
                "CWorld__ClearWorldTextSlot",
                "CWorld__GetWorldTextSlotTimerValue",
                "DAT_00855090",
            ],
            "boundary": "world-text helpers are adjacent static display context for variable-style commands; this schema does not prove the raw descriptor entries dispatch to those helpers or prove runtime display behavior",
        },
        "claims": [
            "The five selected command descriptor rows exist in the completed descriptor schema.",
            "The selected command names occur in the loose MissionScripts corpus with exact command-token counts.",
            "Public MSL docs expose HUD part constants and variable display command forms.",
            "HUD/frontend and CWorld world-text static contracts provide rebuild-planning context for later scoped runtime proof.",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime HUD behavior",
            "visible HUD flashing",
            "runtime variable display",
            "message overlay behavior",
            "render ordering",
            "live loose-MSL loading",
            "packed-vs-loose script selection",
            "handler-body semantics for the five raw entries",
            "static call path from the five raw entries into CHud functions",
            "exact command descriptor layout",
            "exact command arity",
            "exact datatype layout",
            "exact HUD layout",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
    }


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} contains forbidden public token: {token}", failures)
    for token in FORBIDDEN_OVERCLAIMS:
        require(token not in lower, f"{path.relative_to(ROOT)} contains overclaim token: {token}", failures)


def check_no_overclaims(path: Path, failures: list[str]) -> None:
    lower = read_text(path).lower()
    for token in FORBIDDEN_OVERCLAIMS:
        require(token not in lower, f"{path.relative_to(ROOT)} contains overclaim token: {token}", failures)


def check_schema(failures: list[str]) -> None:
    expected = build_schema()
    for path in (SCHEMA, LORE_SCHEMA):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} is not regenerated from current evidence", failures)
        for command, expected_count in EXPECTED_COUNTS.items():
            actual_count = actual["looseMslUsage"]["directNonCommentCounts"][command]
            require(actual_count["calls"] == expected_count["calls"], f"{command} call count mismatch", failures)
            require(actual_count["files"] == expected_count["files"], f"{command} file count mismatch", failures)
        check_no_bad_tokens(path, failures)


def check_descriptor_rows(failures: list[str]) -> None:
    schema = read_json(DESCRIPTOR_SCHEMA)
    records = {record["commandName"]: record for record in schema["records"] if record.get("commandName")}
    for command, expected in DESCRIPTOR_COMMANDS.items():
        record = records.get(command)
        require(record is not None, f"descriptor schema missing {command}", failures)
        if record is None:
            continue
        require(record["index"] == expected["index"], f"{command} index mismatch", failures)
        require(record["recordAddress"] == expected["recordAddress"], f"{command} record address mismatch", failures)
        raw = {item["offset"]: item["value"] for item in record["rawAssignments"]}
        require(raw["+0x00"] == expected["rawEntryValue"], f"{command} raw entry mismatch", failures)
        for offset, value in expected["shape"].items():
            require(raw[offset] == value, f"{command} raw {offset} mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        "MissionScript HUD / Display Command-Effect Static Proof",
        PROOF_LINK,
        SCHEMA_LINK,
        "Status: static HUD/display command-effect schema proof complete, not runtime proof",
        "HighlightHudPart",
        "UnHighlightHudPart",
        "InitVariable",
        "SetVariable",
        "ShutdownVariable",
        "0x0064d690",
        "0x0064d6d0",
        "0x0064e110",
        "0x0064e150",
        "0x0064e190",
        "&LAB_00535d70",
        "&LAB_00535e60",
        "&LAB_00536210",
        "&LAB_00536230",
        "&LAB_00536260",
        "13 / 13 / 77 / 146 / 26",
        "CHud__SetHudComponent",
        "CHud__RenderOverlayForViewpoint",
        "CHudComponent__RenderPass",
        "CWorld__PushWorldTextSlot",
        "CWorld__UpdateWorldTextSlotTiming",
        "CWorld__ClearWorldTextSlot",
        "CWorld__GetWorldTextSlotTimerValue",
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
        MESSAGE_AUDIO_PROOF,
        BACKLOG,
        LORE_BACKLOG,
        MAPPED,
        LORE_MAPPED,
        BIN_INDEX,
        LORE_BIN_INDEX,
        RE_INDEX,
        LORE_RE_INDEX,
        ISCRIPT_DOC,
        LORE_ISCRIPT_DOC,
        MSL_DOC,
        LORE_MSL_DOC,
        MSL_COMMANDS,
        LORE_MSL_COMMANDS,
        HUD_CONTRACT,
        LORE_HUD_CONTRACT,
        WORLD_DOC,
    )
    for path in front_door_docs:
        text = read_text(path)
        for token in (PROOF_LINK, SCHEMA_LINK, "MissionScript HUD / Display Command-Effect"):
            require(token in text, f"{path.relative_to(ROOT)} missing HUD/display proof token: {token}", failures)
        check_no_overclaims(path, failures)

    backlog_text = read_text(BACKLOG)
    require(
        "Completed MissionScript HUD / Display Command-Effect Static Proof" in backlog_text,
        "backlog does not record completed HUD/display proof",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript HUD / Display Command-Effect Static Proof" not in backlog_text,
        "backlog still has stale active HUD/display proof selection",
        failures,
    )

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\missionscript_hud_display_command_effect_static_probe.py --check"
    actual_script = package.get("scripts", {}).get("test:missionscript-hud-display-command-effect-static")
    require(actual_script == expected_script, "package script mismatch", failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_descriptor_rows(failures)
    check_schema(failures)
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
            print("MissionScript HUD/display command-effect static probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript HUD/display command-effect static probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
