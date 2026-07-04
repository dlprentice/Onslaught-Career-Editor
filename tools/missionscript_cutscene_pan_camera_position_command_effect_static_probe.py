#!/usr/bin/env python3
"""Validate the MissionScript cutscene pan-camera/position command-effect static proof."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-command-effect.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-command-effect.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-command-effect-static-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-command-effect-static-proof.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_cutscene_pan_camera_position_command_effect_static_proof_2026-06-08.md"

DESCRIPTOR_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-descriptor-schema.v1.json"
DATATYPE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vm-datatype-opcode-schema.v1.json"
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
MSL_SCRIPTING = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
LORE_MSL_SCRIPTING = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "msl-scripting.md"
MISSION_THING = ROOT / "reverse-engineering" / "game-assets" / "mission-thing-usage.md"
MISSION_EVENTS = ROOT / "reverse-engineering" / "game-assets" / "mission-events-index.md"
MSL_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
LORE_MSL_COMMANDS = ROOT / "lore-book" / "reverse-engineering" / "quick-reference" / "msl-commands.md"
PACKAGE_JSON = ROOT / "package.json"

WAVE580 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave580-iscript-camera-objective-00533b70"
WAVE1219_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
WAVE580_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260519-044247_post_wave580_iscript_camera_objective_verified"

PROOF_LINK = "missionscript-cutscene-pan-camera-position-command-effect-static-proof.md"
SCHEMA_LINK = "missionscript-cutscene-pan-camera-position-command-effect.v1.json"

DESCRIPTOR_COMMANDS = {
    "CreatePosition": {"index": 65, "recordAddress": "0x0064de90", "symbol": "s_CreatePosition_0064f6c0"},
    "Goto3PointPanCamera": {"index": 113, "recordAddress": "0x0064ea90", "symbol": "s_Goto3PointPanCamera_0064f3dc"},
    "Goto4PointPanCamera": {"index": 114, "recordAddress": "0x0064ead0", "symbol": "s_Goto4PointPanCamera_0064f3c8"},
    "GotoPlayerCamera": {"index": 115, "recordAddress": "0x0064eb10", "symbol": "s_GotoPlayerCamera_0064f3b4"},
}

CAMERA_HANDLERS = [
    {
        "command": "Goto3PointPanCamera",
        "address": "0x00533b70",
        "name": "IScript__Create3PointPanCamera",
        "signature": "void __stdcall IScript__Create3PointPanCamera(void * script_args, void * unused_state, void * out_result)",
        "summary": "gets target thing via datatype slot +0x40, transforms three position/vector arguments via slot +0x44 through thing matrix or DAT_0083d9c0 fallback, builds CBSpline and CPanCamera, then calls CGame__SetCurrentCamera",
        "metadataTokens": ("Create3PointPanCamera", "CGame__SetCurrentCamera", "DAT_0083d9c0", "CPanCamera"),
        "decompile": "00533b70_IScript__Create3PointPanCamera.c",
        "decompileTokens": ("CGame__SetCurrentCamera", "CPanCamera__ctor", "CBSpline__ctor", "0x0064fa9c", "DAT_0083d9c0"),
    },
    {
        "command": "Goto4PointPanCamera",
        "address": "0x00533eb0",
        "name": "IScript__Create4PointPanCamera",
        "signature": "void __stdcall IScript__Create4PointPanCamera(void * script_args, void * unused_state, void * out_result)",
        "summary": "same pan-camera path with four position/vector arguments, null-thing diagnostic 0x0064fad8, and duration from datatype slot +0x34",
        "metadataTokens": ("Create4PointPanCamera", "CGame__SetCurrentCamera", "0x0064fad8", "CPanCamera"),
        "decompile": "00533eb0_IScript__Create4PointPanCamera.c",
        "decompileTokens": ("CGame__SetCurrentCamera", "CPanCamera__ctor", "CBSpline__ctor", "0x0064fad8", "DAT_0083d9c0"),
    },
]

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
    "runtime camera switching proven",
    "runtime cutscene behavior proven",
    "runtime cutscene playback proven",
    "visible camera output proven",
    "live loose-msl loading proven",
    "exact command descriptor layout proven",
    "exact cpositiondatatype layout proven",
    "exact cpancamera layout proven",
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


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tsv_by_address(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {row[key].lower(): row for row in read_tsv_rows(path)}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def require_tokens(label: str, text: str, tokens: tuple[str, ...], failures: list[str]) -> None:
    for token in tokens:
        require(token in text, f"{label} missing token: {token}", failures)


def parse_markdown_table(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in read_text(path).splitlines():
        if not line.startswith("| "):
            continue
        cells = [part.strip() for part in line.strip().strip("|").split("|")]
        if not cells or not cells[0].isdigit():
            continue
        rows.append(cells)
    return rows


def strip_ticks(value: str) -> str:
    return value.strip().strip("`")


def mission_thing_context() -> dict[str, Any]:
    rows = parse_markdown_table(MISSION_THING)
    fenrir_rows = [
        row for row in rows
        if len(row) >= 6 and row[0] in {"741", "742"} and strip_ticks(row[4]) == "Fenrir"
    ]
    cutscene_rows = [
        row for row in fenrir_rows
        if row[2] in {"Cutscene_Lost.msl", "Cutscene_Won.msl"}
    ]
    by_level: dict[str, int] = {}
    by_file: dict[str, int] = {}
    for row in cutscene_rows:
        by_level[row[0]] = by_level.get(row[0], 0) + 1
        by_file[row[2]] = by_file.get(row[2], 0) + 1
    return {
        "source": "reverse-engineering/game-assets/mission-thing-usage.md",
        "selectedLevels": ["level741", "level742"],
        "fenrirGetThingRefRowsInSelectedLevels": len(fenrir_rows),
        "cutsceneFenrirGetThingRefRows": len(cutscene_rows),
        "cutsceneRowsByLevel": by_level,
        "cutsceneRowsByFile": by_file,
        "thingName": "Fenrir",
        "spawnerCells": "all selected cutscene rows have empty spawner cells",
        "boundary": "loose MSL corpus rows only; runtime object identity and runtime lookup by name remain unproven",
    }


def mission_events_context() -> dict[str, Any]:
    text = read_text(MISSION_EVENTS)
    required = {
        "level741Summary": "| 741 | level741 | 21 | 0 | 1 | 0 | 0 | 1 | 1 | 0 |",
        "level742Summary": "| 742 | level742 | 25 | 0 | 2 | 0 | 0 | 2 | 1 | 0 |",
        "playerLost": "Player Lost",
        "levelLost": "Level Lost",
        "levelWon": "Level Won",
    }
    return {
        "source": "reverse-engineering/game-assets/mission-events-index.md",
        "selectedLevels": ["level741", "level742"],
        "level741Summary": required["level741Summary"] in text,
        "level742Summary": required["level742Summary"] in text,
        "containsPlayerLost": required["playerLost"] in text,
        "containsLevelLost": required["levelLost"] in text,
        "containsLevelWon": required["levelWon"] in text,
        "boundary": "event-name index only; runtime event dispatch and cutscene outcomes remain unproven",
    }


def msl_cutscene_example_context() -> dict[str, Any]:
    text = read_text(MSL_SCRIPTING)
    tokens = (
        "pos1 = CreatePosition(-80.0, 20.0, -30.0);",
        "pos2 = CreatePosition(0.0, 40.0, 60.0);",
        "pos3 = CreatePosition(100.0, 20.0, 40.0);",
        'Goto3PointPanCamera(GetThingRef("Fenrir"), pos1, pos2, pos3, 15.0);',
        "LevelLostString(_J2_742_STILL_INSIDE);",
    )
    return {
        "source": "reverse-engineering/game-assets/msl-scripting.md",
        "exampleName": "Cutscene Camera System",
        "createPositionCallsInExample": 3,
        "goto3PointPanCameraCallsInExample": 1,
        "targetThing": "Fenrir",
        "tokensPresent": {token: token in text for token in tokens},
        "boundary": "public MSL syntax/corpus example only; live loose-MSL loading and runtime camera output remain unproven",
    }


def evidence_counts() -> dict[str, int]:
    return {
        "wave580MetadataRows": len(read_tsv_rows(WAVE580 / "post_metadata.tsv")),
        "wave580TagRows": len(read_tsv_rows(WAVE580 / "post_tags.tsv")),
        "wave580XrefRows": len(read_tsv_rows(WAVE580 / "post_xrefs.tsv")),
        "wave580InstructionRows": len(read_tsv_rows(WAVE580 / "post_target_instructions.tsv")),
        "wave580DecompileRows": len(read_tsv_rows(WAVE580 / "post_decompile" / "index.tsv")),
        "wave580VtableRows": len(read_tsv_rows(WAVE580 / "post_vtables.tsv")),
    }


def descriptor_records() -> dict[str, Any]:
    descriptor = read_json(DESCRIPTOR_SCHEMA)
    records = {record["commandName"]: record for record in descriptor["records"] if record.get("commandName")}
    result: dict[str, Any] = {}
    for command, expected in DESCRIPTOR_COMMANDS.items():
        record = records[command]
        raw_assignments = {item["offset"]: item["value"] for item in record["rawAssignments"]}
        result[command] = {
            "index": record["index"],
            "recordAddress": record["recordAddress"],
            "observedNameSymbol": record["observedNameSymbol"],
            "rawEntryValue": raw_assignments["+0x00"],
            "rawShapeValues": {
                offset: raw_assignments.get(offset)
                for offset in ("+0x14", "+0x18", "+0x1c", "+0x20", "+0x24", "+0x28", "+0x2c", "+0x30", "+0x38")
                if raw_assignments.get(offset) is not None
            },
            "nameStatus": record["nameStatus"],
            "expectedSymbol": expected["symbol"],
        }
    return result


def position_datatype_record() -> dict[str, Any]:
    schema = read_json(DATATYPE_SCHEMA)
    for record in schema["datatypeCases"]:
        if record["typeId"] == 6:
            return record
    raise AssertionError("missing CPositionDataType type 6")


def build_schema() -> dict[str, Any]:
    return {
        "schemaVersion": "missionscript-cutscene-pan-camera-position-command-effect.v1",
        "status": "PASS",
        "source": {
            "evidenceWaves": ["Wave580", "Wave581", "Wave903"],
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static cutscene pan-camera command descriptor, position datatype, handler-body, and loose-corpus bridge mapping for clean-room planning",
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
        "descriptorRecords": descriptor_records(),
        "positionDatatype": position_datatype_record(),
        "cameraHandlers": [
            {key: value for key, value in handler.items() if key not in {"metadataTokens", "decompile", "decompileTokens"}}
            for handler in CAMERA_HANDLERS
        ],
        "missionThingContext": mission_thing_context(),
        "missionEventsContext": mission_events_context(),
        "mslCutsceneExample": msl_cutscene_example_context(),
        "staticBridge": [
            "CreatePosition descriptor index 65 at 0x0064de90 records CreatePosition name and raw type-shape values including three float-like type 2 inputs and type 6 context.",
            "CPositionDataType type id 6 uses vtable 0x005e4da4, size 20, reads three floats at +0x04/+0x08/+0x0c, and exposes value getter slot +0x44; +0x10 remains unproven.",
            "Goto3PointPanCamera descriptor index 113 at 0x0064ea90 records thing-ptr type 5, three position type 6 slots, and duration type 2 context as raw descriptor evidence.",
            "Wave580 IScript__Create3PointPanCamera gets the target thing through slot +0x40, reads three position/vector values through slot +0x44, reads duration through +0x34, constructs CBSpline/CPanCamera, and calls CGame__SetCurrentCamera.",
            "The public level741/level742 Fenrir cutscene corpus gives a concrete static planning example but does not prove live script loading or visible camera output.",
        ],
        "fieldMappingBoundary": "Descriptor names and raw shape values are preserved as static evidence, but this schema does not prove exact descriptor field layout, exact command arity, or one-to-one handler mapping for every row.",
        "claims": [
            "The static descriptor schema contains CreatePosition and Goto3PointPanCamera command names and record addresses.",
            "The static datatype schema contains CPositionDataType as type id 6 with three float payload reads and value getter slot +0x44.",
            "Wave580 saved IScript__Create3PointPanCamera and IScript__Create4PointPanCamera as fixed three-stack-argument command handlers.",
            "The Wave580 3-point pan-camera body statically bridges thing lookup, position values, duration, CBSpline, CPanCamera, and CGame__SetCurrentCamera.",
            "The loose MSL docs preserve a Fenrir cutscene example using three CreatePosition calls feeding Goto3PointPanCamera(GetThingRef(\"Fenrir\"), ...).",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime command effects",
            "runtime camera switching",
            "runtime cutscene playback",
            "runtime visible camera output",
            "runtime object identity",
            "runtime object lookup by name",
            "live loose-MSL loading",
            "packed-vs-loose script selection",
            "exact command descriptor layout",
            "exact command arity",
            "exact argument type schema",
            "exact CPositionDataType layout",
            "exact CPanCamera layout",
            "exact CBSpline layout",
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
        require(token not in text, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def check_no_overclaims(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def check_schema(failures: list[str]) -> None:
    expected = build_schema()
    for path in (SCHEMA, LORE_SCHEMA):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} does not match generated schema", failures)
        require(actual["descriptorRecords"]["CreatePosition"]["index"] == 65, "CreatePosition descriptor index mismatch", failures)
        require(actual["descriptorRecords"]["Goto3PointPanCamera"]["index"] == 113, "Goto3PointPanCamera descriptor index mismatch", failures)
        require(actual["positionDatatype"]["typeId"] == 6, "position datatype type id mismatch", failures)
        require(actual["positionDatatype"]["className"] == "CPositionDataType", "position datatype class mismatch", failures)
        require(actual["missionThingContext"]["cutsceneFenrirGetThingRefRows"] == 6, "Fenrir cutscene GetThingRef row count mismatch", failures)
        require(actual["missionThingContext"]["fenrirGetThingRefRowsInSelectedLevels"] == 17, "Fenrir selected-level row count mismatch", failures)
        require(actual["mslCutsceneExample"]["createPositionCallsInExample"] == 3, "CreatePosition example count mismatch", failures)
        require(all(actual["mslCutsceneExample"]["tokensPresent"].values()), "MSL cutscene example token missing", failures)
        check_no_bad_tokens(path, failures)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "wave580MetadataRows": 6,
        "wave580TagRows": 6,
        "wave580XrefRows": 6,
        "wave580InstructionRows": 5454,
        "wave580DecompileRows": 6,
        "wave580VtableRows": 36,
    }
    actual_counts = evidence_counts()
    for key, expected in expected_counts.items():
        require(actual_counts.get(key) == expected, f"{key} mismatch: {actual_counts.get(key)} != {expected}", failures)

    metadata = tsv_by_address(WAVE580 / "post_metadata.tsv")
    for handler in CAMERA_HANDLERS:
        row = metadata.get(handler["address"])
        require(row is not None, f"missing Wave580 metadata row {handler['address']}", failures)
        if row is not None:
            require(row["name"] == handler["name"], f"Wave580 name mismatch at {handler['address']}", failures)
            require(row["signature"] == handler["signature"], f"Wave580 signature mismatch at {handler['address']}", failures)
            require_tokens(f"Wave580 comment {handler['address']}", row["comment"], handler["metadataTokens"], failures)
        decompile = read_text(WAVE580 / "post_decompile" / handler["decompile"])
        require_tokens(f"Wave580 decompile {handler['address']}", decompile, handler["decompileTokens"], failures)

    instructions = read_text(WAVE580 / "post_target_instructions.tsv")
    require_tokens(
        "Wave580 instructions",
        instructions,
        (
            "CALL\t0x004198d0",
            "MOV\tECX, 0x8a9a98",
            "CALL\t0x004705e0",
            "MOV\tESI, 0x83d9c0",
            "CALL\tdword ptr [EDX + 0x44]",
        ),
        failures,
    )
    backup = read_json(WAVE580 / "wave580_backup_summary.json")
    require(backup.get("status") == "PASS", "Wave580 backup status mismatch", failures)
    require(backup.get("destination") == WAVE580_BACKUP, "Wave580 backup path mismatch", failures)
    require(backup.get("diffCount") == 0, "Wave580 backup diff mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        "MissionScript Cutscene Pan-Camera / Position Command-Effect Static Proof",
        PROOF_LINK,
        SCHEMA_LINK,
        "Status: static cutscene pan-camera/position command-effect schema proof complete, not runtime proof",
        "CreatePosition",
        "Goto3PointPanCamera",
        "Goto4PointPanCamera",
        "IScript__Create3PointPanCamera",
        "IScript__Create4PointPanCamera",
        "CPositionDataType",
        "0x0064de90",
        "0x0064ea90",
        "0x005e4da4",
        "0x00533b70",
        "0x00533eb0",
        "CGame__SetCurrentCamera",
        "CPanCamera",
        "CBSpline",
        "DAT_0083d9c0",
        "GetThingRef(\"Fenrir\")",
        "level741",
        "level742",
        "6 cutscene Fenrir GetThingRef rows",
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
        MSL_SCRIPTING,
        LORE_MSL_SCRIPTING,
        MISSION_THING,
        MISSION_EVENTS,
        MSL_COMMANDS,
        LORE_MSL_COMMANDS,
    )
    for path in front_door_docs:
        text = read_text(path)
        for token in (PROOF_LINK, SCHEMA_LINK, "MissionScript Cutscene Pan-Camera / Position Command-Effect"):
            require(token in text, f"{path.relative_to(ROOT)} missing cutscene camera proof token: {token}", failures)
        check_no_overclaims(path, failures)

    backlog_text = read_text(BACKLOG)
    require(
        "Completed MissionScript Cutscene Pan-Camera / Position Command-Effect Static Proof" in backlog_text,
        "backlog no longer records completed cutscene pan-camera proof",
        failures,
    )
    require(
        "The selected active static-to-proof slice is [World / Thing / Spawn GetThingRef Object-Reference Static Proof]" not in backlog_text,
        "backlog still has stale active GetThingRef proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is [MissionScript Cutscene Pan-Camera / Position Command-Effect Static Proof]" not in backlog_text,
        "backlog still has stale active cutscene proof slice",
        failures,
    )

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\missionscript_cutscene_pan_camera_position_command_effect_static_probe.py --check"
    actual_script = package.get("scripts", {}).get("test:missionscript-cutscene-pan-camera-position-command-effect-static")
    require(actual_script == expected_script, "package script mismatch", failures)


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
            print("MissionScript cutscene pan-camera/position command-effect static probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript cutscene pan-camera/position command-effect static probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
