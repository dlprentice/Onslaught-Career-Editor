#!/usr/bin/env python3
"""Validate the MissionScript command descriptor schema proof."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DECOMPILE = (
    ROOT
    / "reverse-engineering"
    / "binary-analysis"
    / "scratch"
    / "deep_semantic_tail_2026-02-26"
    / "pass2_semantic_wave10"
    / "verify_decomp"
    / "0052ff30_ScriptCommandRegistry__InitBuiltins.c"
)
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-descriptor-schema.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-command-descriptor-schema.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-descriptor-schema-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-command-descriptor-schema-proof.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_command_descriptor_schema_2026-06-08.md"
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
MSL_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
LORE_MSL_COMMANDS = ROOT / "lore-book" / "reverse-engineering" / "quick-reference" / "msl-commands.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
ASM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AsmInstruction.cpp.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

SCHEMA_LINK = "missionscript-command-descriptor-schema.v1.json"
PROOF_LINK = "missionscript-command-descriptor-schema-proof.md"
BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
TABLE_START = 0x0064CE50
STRIDE = 0x40
SLOT_COUNT = 144

EXPECTED_EXAMPLES = {
    0: "FollowWaypointWait",
    2: "SpawnThing",
    4: "PostEvent",
    8: "LevelWon",
    113: "Goto3PointPanCamera",
    118: "SetGoodieState",
    119: "GetGoodieState",
    122: "SetSlot",
    132: "SetSlotSave",
    136: "ToggleCockpit",
    137: "SetStealth",
    142: "IsOverWater",
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
    "exact descriptor layout proven",
    "exact command descriptor schema proven",
    "runtime command dispatch proven",
    "runtime command effects proven",
    "runtime missionscript execution proven",
    "runtime mission behavior proven",
    "full command semantics proven",
    "exact arity proven",
    "exact argument type schema proven",
    "exact vm layout proven",
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
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def addr(value: int) -> str:
    return f"0x{value:08x}"


def command_name(symbol: str | None) -> str | None:
    if not symbol:
        return None
    match = re.fullmatch(r"s_(.+)_0064[0-9a-f]{4}", symbol)
    if match:
        return match.group(1)
    return None


def parse_assignments() -> dict[int, str]:
    assignments: dict[int, str] = {}
    for line in read_text(DECOMPILE).splitlines():
        match = re.match(r"\s*_DAT_([0-9a-fA-F]{8})\s*=\s*(.+?);\s*$", line)
        if match:
            assignments[int(match.group(1), 16)] = match.group(2)
    return assignments


def build_schema() -> dict[str, Any]:
    assignments = parse_assignments()
    records: list[dict[str, Any]] = []
    observed_names = 0

    for index in range(SLOT_COUNT):
        base = TABLE_START + index * STRIDE
        raw_assignments: list[dict[str, str]] = []
        for offset in range(0, STRIDE, 4):
            absolute = base + offset
            value = assignments.get(absolute)
            if value is not None:
                raw_assignments.append(
                    {
                        "offset": f"+0x{offset:02x}",
                        "address": addr(absolute),
                        "value": value,
                    }
                )

        name_symbol = assignments.get(base + 0x10)
        name = command_name(name_symbol)
        if name_symbol is not None:
            observed_names += 1

        records.append(
            {
                "index": index,
                "recordAddress": addr(base),
                "assignmentCount": len(raw_assignments),
                "nameFieldAddress": addr(base + 0x10),
                "observedNameSymbol": name_symbol,
                "commandName": name,
                "nameStatus": "observed-symbol" if name_symbol else "not-written-in-decompile",
                "rawAssignments": raw_assignments,
            }
        )

    return {
        "schemaVersion": "missionscript-command-descriptor-schema.v1",
        "status": "PASS",
        "source": {
            "decompilePath": "reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave10/verify_decomp/0052ff30_ScriptCommandRegistry__InitBuiltins.c",
            "function": "0x0052ff30 ScriptCommandRegistry__InitBuiltins",
            "runtimeExecution": False,
            "ghidraMutation": False,
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackup": BACKUP,
        },
        "descriptorTable": {
            "startAddress": addr(TABLE_START),
            "strideBytes": STRIDE,
            "declaredSlots": SLOT_COUNT,
            "lastDeclaredSlotAddress": addr(TABLE_START + (SLOT_COUNT - 1) * STRIDE),
            "slotsWithAssignments": sum(1 for record in records if record["assignmentCount"] > 0),
            "observedNameAssignments": observed_names,
            "firstObservedName": {
                "index": 0,
                "recordAddress": addr(TABLE_START),
                "name": "FollowWaypointWait",
                "symbol": "s_FollowWaypointWait_0064fa14",
            },
            "lastObservedName": {
                "index": 142,
                "recordAddress": addr(TABLE_START + 142 * STRIDE),
                "name": "IsOverWater",
                "symbol": "s_IsOverWater_0064f234",
            },
            "finalSlotBoundary": {
                "index": 143,
                "recordAddress": addr(TABLE_START + 143 * STRIDE),
                "assignmentCount": records[143]["assignmentCount"],
                "nameStatus": records[143]["nameStatus"],
            },
        },
        "selectedExamples": [
            {
                "index": index,
                "recordAddress": records[index]["recordAddress"],
                "commandName": records[index]["commandName"],
                "observedNameSymbol": records[index]["observedNameSymbol"],
            }
            for index in EXPECTED_EXAMPLES
        ],
        "records": records,
        "claims": [
            "ScriptCommandRegistry__InitBuiltins writes a 144-slot static descriptor table at 0x0064ce50 with 0x40-byte stride.",
            "All 144 declared slots have at least one observed assignment in the saved decompile.",
            "143 name-field assignments are observed; the first observed command name is FollowWaypointWait and the last observed command name is IsOverWater.",
            "The final declared slot at 0x0064f210 is preserved as an assigned slot with no observed name-field assignment in this decompile.",
        ],
        "notClaimed": [
            "exact descriptor field layout",
            "exact command arity",
            "exact argument type schema",
            "runtime command dispatch",
            "runtime command effects",
            "runtime MissionScript execution",
            "full command semantics",
            "exact VM/datatype/opcode layout",
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


def check_schema(failures: list[str]) -> None:
    expected = build_schema()
    stored = read_json(SCHEMA)
    require(stored == expected, "descriptor schema does not match rebuilt decompile evidence", failures)
    require(read_json(LORE_SCHEMA) == stored, "lore descriptor schema mirror mismatch", failures)

    table = stored["descriptorTable"]
    require(table["declaredSlots"] == 144, "declared slot count mismatch", failures)
    require(table["strideBytes"] == 64, "stride mismatch", failures)
    require(table["slotsWithAssignments"] == 144, "slots-with-assignments mismatch", failures)
    require(table["observedNameAssignments"] == 143, "name assignment count mismatch", failures)
    require(stored["records"][143]["commandName"] is None, "final slot unexpectedly named", failures)
    require(stored["records"][143]["nameStatus"] == "not-written-in-decompile", "final slot name status mismatch", failures)

    examples = {row["index"]: row["commandName"] for row in stored["selectedExamples"]}
    for index, name in EXPECTED_EXAMPLES.items():
        require(examples.get(index) == name, f"selected example mismatch at {index}: {examples.get(index)}", failures)

    serialized = json.dumps(stored, sort_keys=True)
    for token in ("Program Files", "C:\\Users", ".env", "password", "token="):
        require(token not in serialized, f"schema leaks forbidden token: {token}", failures)
    for token in ("exact descriptor field layout", "runtime command dispatch", "rebuild parity"):
        require(token in stored["notClaimed"], f"schema missing non-claim: {token}", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)
    proof_tokens = (
        "MissionScript Command Descriptor Schema Proof",
        "Status: static descriptor schema proof complete, not runtime proof",
        SCHEMA_LINK,
        "ScriptCommandRegistry__InitBuiltins",
        "0x0052ff30",
        "144",
        "0x40",
        "0x0064ce50",
        "0x0064f210",
        "143",
        "FollowWaypointWait",
        "IsOverWater",
        "PostEvent",
        "SpawnThing",
        "SetSlotSave",
        "LevelWon",
        "ToggleCockpit",
        "SetStealth",
        "exact descriptor field layout",
        "runtime command dispatch",
        "runtime command effects",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1560/1560 = 100.00%",
        "1179/1179 = 100.00%",
        BACKUP,
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in proof_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_tokens(path, failures)

    linked_paths = (
        CONTRACT,
        PROOF_PLAN,
        BACKLOG,
        MAPPED,
        BIN_INDEX,
        RE_INDEX,
        MSL_COMMANDS,
        ISCRIPT_DOC,
        ASM_DOC,
    )
    for path in linked_paths:
        text = read_text(path)
        require(PROOF_LINK in text, f"{path.relative_to(ROOT)} missing proof link", failures)
        require(SCHEMA_LINK in text, f"{path.relative_to(ROOT)} missing schema link", failures)
        check_no_bad_tokens(path, failures)

    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "transition backlog lore mirror mismatch", failures)
    require(read_text(MAPPED) == read_text(LORE_MAPPED), "mapped systems lore mirror mismatch", failures)
    require(read_text(BIN_INDEX) == read_text(LORE_BIN_INDEX), "binary index lore mirror mismatch", failures)
    require(read_text(RE_INDEX) == read_text(LORE_RE_INDEX), "RE index lore mirror mismatch", failures)
    require(read_text(MSL_COMMANDS) == read_text(LORE_MSL_COMMANDS), "MSL command lore mirror mismatch", failures)


def check_progress_and_package(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total mismatch", failures)
    require(quality["commentedFunctions"] == 6411, "progress commented mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk focused mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-command-descriptor-schema")
        == r"py -3 tools\missionscript_command_descriptor_schema_probe.py --check",
        "missing package descriptor schema script",
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
    check_progress_and_package(failures)

    if failures:
        print("MissionScript command descriptor schema probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript command descriptor schema probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
