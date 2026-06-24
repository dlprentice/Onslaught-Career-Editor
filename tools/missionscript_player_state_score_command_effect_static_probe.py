#!/usr/bin/env python3
"""Validate the MissionScript player-state/score command-effect static proof."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect-static-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect-static-proof.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_player_state_score_command_effect_static_proof_2026-06-08.md"

DESCRIPTOR_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-descriptor-schema.v1.json"
OBJECTIVE_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect-static-proof.md"
OBJECTIVE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect.v1.json"
GOODIE_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-command-effect-static-proof.md"
GOODIE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-command-effect.v1.json"
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
LORE_ISCRIPT_DOC = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
LORE_BATTLEENGINE_DOC = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
UNIT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
LORE_UNIT_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
MSL_DOC = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
LORE_MSL_DOC = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "msl-scripting.md"
MSL_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
LORE_MSL_COMMANDS = ROOT / "lore-book" / "reverse-engineering" / "quick-reference" / "msl-commands.md"
PACKAGE_JSON = ROOT / "package.json"

MSL_ROOT = ROOT / "game" / "data" / "MissionScripts"
WAVE1219_BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"

PROOF_LINK = "missionscript-player-state-score-command-effect-static-proof.md"
SCHEMA_LINK = "missionscript-player-state-score-command-effect.v1.json"
FIXTURE_PROOF_SLICE = "MissionScript Player-State / Score Command-Effect Fixture Proof Plan"
COMPLETION_ROLLUP_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"

DESCRIPTOR_COMMANDS = {
    "AddScore": {
        "index": 84,
        "recordAddress": "0x0064e350",
        "rawEntryValue": "IScript__Unk_00534410",
        "shape": {"+0x14": "1", "+0x1c": "1"},
    },
    "ToggleCockpit": {
        "index": 136,
        "recordAddress": "0x0064f050",
        "rawEntryValue": "&LAB_00533950",
        "shape": {},
    },
    "SetStealth": {
        "index": 137,
        "recordAddress": "0x0064f090",
        "rawEntryValue": "&LAB_00533980",
        "shape": {"+0x14": "1", "+0x1c": "2"},
    },
}

EXPECTED_COUNTS = {
    "AddScore": {"calls": 15, "files": 12},
    "ToggleCockpit": {"calls": 0, "files": 0},
    "SetStealth": {"calls": 10, "files": 4},
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
    "runtime score behavior proven",
    "runtime cockpit behavior proven",
    "runtime stealth behavior proven",
    "weapon-fire/stealth interaction proven",
    "runtime ranking/career/save behavior proven",
    "live script loading proven",
    "packed-vs-loose script selection proven",
    "exact player-state layout proven",
    "exact command descriptor layout proven",
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
            "boundary": "descriptor-row/raw-entry static evidence only; handler-body semantics, exact descriptor layout, runtime command effects, and exact player-state layout remain unproven",
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
                    if len(usage[command]["sampleRows"]) < 10:
                        usage[command]["sampleRows"].append(f"{path.relative_to(ROOT)}:{line_number}:{stripped}")

    for command, seen in files_seen.items():
        usage[command]["files"] = len(seen)

    return {
        "source": "game/data/MissionScripts/**/*.msl",
        "directNonCommentCounts": usage,
        "boundary": "private loose-MSL scan only; command-token usage rows are static corpus context and do not prove live loose-MSL loading, packed-resource selection, runtime score behavior, runtime cockpit behavior, or runtime stealth behavior",
    }


def build_schema() -> dict[str, Any]:
    return {
        "schemaVersion": "missionscript-player-state-score-command-effect.v1",
        "status": "PASS",
        "source": {
            "evidenceWaves": ["Wave579", "Wave864", "Wave903", "Wave1049", "Wave1219"],
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static MissionScript player-state/score descriptor, loose-corpus, source-context, and alias-boundary bridge for clean-room planning",
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
        "looseMslUsage": command_usage(),
        "aliasAndRawEntryBoundaries": {
            "AddScore": {
                "descriptorIndex": 84,
                "descriptorRecord": "0x0064e350",
                "rawEntryValue": "IScript__Unk_00534410",
                "conflictingCurrentObjectiveName": "0x00534410 IScript__SecondaryObjectiveComplete",
                "status": "descriptor/name/corpus context only; no AddScore handler-body bridge is claimed",
                "whyDeferred": "the descriptor raw entry collides with current objective/outcome evidence for SecondaryObjectiveComplete, so this proof preserves the conflict instead of renaming or claiming score mutation semantics",
            },
            "ToggleCockpit": {
                "descriptorIndex": 136,
                "descriptorRecord": "0x0064f050",
                "rawEntryValue": "&LAB_00533950",
                "status": "raw descriptor label plus source-context only; no handler-body bridge is claimed",
                "looseMslDirectRows": 0,
            },
            "SetStealth": {
                "descriptorIndex": 137,
                "descriptorRecord": "0x0064f090",
                "rawEntryValue": "&LAB_00533980",
                "status": "raw descriptor label plus loose-corpus/source-context only; no handler-body bridge or runtime stealth proof is claimed",
                "looseMslDirectRows": 10,
            },
        },
        "sourceAndStaticContext": {
            "score": [
                "Public MSL docs expose AddScore(points) and negative penalty examples.",
                "Stuart source exposes CGame::IncScore(SINT), but this proof does not bind the AddScore descriptor raw entry to that source helper.",
            ],
            "cockpit": [
                "Stuart source exposes CBattleEngine::ToggleCockpit().",
                "The retail descriptor row remains raw &LAB_00533950 and has zero direct non-comment loose-MSL rows in the copied corpus scan.",
            ],
            "stealth": [
                "SetStealth occurs in Carver loose-MSL scripts with 100, 75, and 0 values.",
                "Stuart source exposes mStealth/mDesiredStealth flow and CBattleEngine::HandleCloak context.",
                "Retail static docs anchor 0x0040d4d0 CBattleEngine__HandleCloak to cloak/desired-stealth context, but this proof does not bind SetStealth runtime behavior to that function.",
            ],
        },
        "claims": [
            "The three selected command descriptor rows exist in the completed descriptor schema.",
            "The copied loose-MSL scan has exact direct non-comment command-token counts for AddScore, ToggleCockpit, and SetStealth.",
            "AddScore is preserved as a descriptor/name/corpus alias-boundary case because its raw entry conflicts with current objective/outcome naming at 0x00534410.",
            "ToggleCockpit and SetStealth are preserved as raw descriptor labels with source/static context only until fresh handler-boundary evidence exists.",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime command effects",
            "runtime score behavior",
            "runtime cockpit behavior",
            "runtime stealth behavior",
            "weapon-fire/stealth interaction",
            "runtime ranking/career/save behavior",
            "live loose-MSL loading",
            "packed-vs-loose script selection",
            "AddScore handler-body proof",
            "ToggleCockpit handler-body proof",
            "SetStealth handler-body proof",
            "exact command descriptor layout",
            "exact command arity",
            "exact datatype layout",
            "exact player-state layout",
            "visual QA",
            "Godot parity",
            "BEA patching behavior",
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
        "MissionScript Player-State / Score Command-Effect Static Proof",
        PROOF_LINK,
        SCHEMA_LINK,
        "Status: static player-state/score command-effect schema proof complete, not runtime proof",
        "AddScore",
        "ToggleCockpit",
        "SetStealth",
        "0x0064e350",
        "0x0064f050",
        "0x0064f090",
        "IScript__Unk_00534410",
        "&LAB_00533950",
        "&LAB_00533980",
        "0x00534410 IScript__SecondaryObjectiveComplete",
        "15 / 0 / 10",
        "12 / 0 / 4",
        "CGame::IncScore",
        "CBattleEngine::ToggleCockpit",
        "CBattleEngine__HandleCloak",
        "descriptor/name/corpus context only",
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
        LORE_ISCRIPT_DOC,
        BATTLEENGINE_DOC,
        LORE_BATTLEENGINE_DOC,
        UNIT_CONTRACT,
        LORE_UNIT_CONTRACT,
        MSL_DOC,
        LORE_MSL_DOC,
        MSL_COMMANDS,
        LORE_MSL_COMMANDS,
    )
    for path in front_door_docs:
        text = read_text(path)
        for token in (PROOF_LINK, SCHEMA_LINK, "MissionScript Player-State / Score Command-Effect"):
            require(token in text, f"{path.relative_to(ROOT)} missing player-state/score proof token: {token}", failures)
        check_no_overclaims(path, failures)

    for path in (OBJECTIVE_PROOF, OBJECTIVE_SCHEMA, GOODIE_PROOF, GOODIE_SCHEMA):
        text = read_text(path)
        require("0x00534410" in text, f"{path.relative_to(ROOT)} missing AddScore conflict address context", failures)
        check_no_overclaims(path, failures)

    backlog_text = read_text(BACKLOG)
    require(
        "Completed MissionScript Player-State / Score Command-Effect Static Proof" in backlog_text,
        "backlog does not record completed player-state/score proof",
        failures,
    )
    require(
        "Completed MissionScript Packed-vs-Loose Script Selection Proof Plan" in backlog_text,
        "backlog does not record completed packed-vs-loose script-selection proof plan",
        failures,
    )
    require(
        "Completed MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan" in backlog_text,
        "backlog does not record completed Level100 tutorial static walkthrough proof plan",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan" not in backlog_text,
        "backlog still marks Level100 tutorial static walkthrough proof plan active",
        failures,
    )
    require(
        "Completed MissionScript Command-Effect Rebuild Fixture Selection Proof Plan" in backlog_text,
        "backlog does not record completed MissionScript fixture-selection proof plan",
        failures,
    )
    require(
        "Completed MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan" in backlog_text,
        "backlog does not record completed Thing Value / Engine Helper fixture proof plan",
        failures,
    )
    require(
        f"Completed {FIXTURE_PROOF_SLICE}" in backlog_text
        or f"The selected active static-to-proof slice is {FIXTURE_PROOF_SLICE}. Status: selected" in backlog_text,
        "backlog does not record active-or-completed Player-State / Score fixture proof plan",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {FIXTURE_PROOF_SLICE}. Status: selected" in backlog_text
        or f"The selected active static-to-proof slice is {COMPLETION_ROLLUP_SLICE}. Status: selected" in backlog_text,
        "backlog does not select the Player-State / Score fixture proof plan or completion rollup",
        failures,
    )

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\missionscript_player_state_score_command_effect_static_probe.py --check"
    actual_script = package.get("scripts", {}).get("test:missionscript-player-state-score-command-effect-static")
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
            print("MissionScript player-state/score command-effect static probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript player-state/score command-effect static probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
