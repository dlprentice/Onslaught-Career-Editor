#!/usr/bin/env python3
"""Validate the MissionScript slot command-effect static proof."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-command-effect.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-command-effect.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-command-effect-static-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-command-effect-static-proof.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_slot_command_effect_static_proof_2026-06-08.md"

DESCRIPTOR_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-descriptor-schema.v1.json"
EVENT_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle.v1.json"
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
CGAME_SET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Script.cpp" / "CGame__SetSlot.md"
CGAME_GET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Script.cpp" / "CGame__GetSlot.md"
CCAREER_SLOT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "CCareer__SetSlot.md"
GAME_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
CAREER_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "_index.md"
MISSION_SLOT_DOC = ROOT / "reverse-engineering" / "game-assets" / "mission-slot-usage.md"
MSL_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
MSL_SCRIPTING = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

WAVE579 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave579-iscript-slot-goodie-005338a0"
WAVE803 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave803-game-slot-helpers"

WAVE1219_BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
WAVE579_BACKUP = r"G:\GhidraBackups\BEA_20260519-041839_post_wave579_iscript_slot_goodie_verified"
WAVE803_BACKUP = r"G:\GhidraBackups\BEA_20260524-084656_post_wave803_game_slot_helpers_verified"

SCHEMA_LINK = "missionscript-slot-command-effect.v1.json"
PROOF_LINK = "missionscript-slot-command-effect-static-proof.md"

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
    "runtime save behavior proven",
    "runtime slot persistence proven",
    "runtime mission outcome proven",
    "tutorial progression proven",
    "level500 branch proven",
    "fenrir state proven",
    "live loose-msl loading proven",
    "exact command descriptor layout proven",
    "exact arity proven",
    "exact argument type schema proven",
    "exact cgame layout proven",
    "exact ccareer layout proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)

DESCRIPTOR_SLOTS = {
    "SetSlot": {"index": 122, "recordAddress": "0x0064ecd0", "symbol": "s_SetSlot_0064f340"},
    "GetSlot": {"index": 123, "recordAddress": "0x0064ed10", "symbol": "s_GetSlot_0064f338"},
    "SetSlotSave": {"index": 132, "recordAddress": "0x0064ef50", "symbol": "s_SetSlotSave_0064f2c0"},
}

HANDLERS: list[dict[str, Any]] = [
    {
        "command": "SetSlot",
        "address": "0x005338d0",
        "name": "IScript__SetSlot",
        "bridge": "runtime-slot",
        "evidence": "reads slot through datatype getter +0x30, reads bool-like value through getter +0x3c, and calls CGame__SetSlot on DAT_008a9a98",
        "boundary": "session/runtime slot mutation only; runtime command execution remains unproven",
        "metadataTokens": ("SetSlot(slot,val)", "runtime script/game slot bitset only", "does not persist"),
        "decompile": "005338d0_IScript__SetSlot.c",
        "decompileTokens": ("CGame__SetSlot", "DAT_008a9a98", "0x3c"),
    },
    {
        "command": "SetSlotSave",
        "address": "0x00533900",
        "name": "IScript__SetSlotSave",
        "bridge": "runtime-plus-career-slot",
        "evidence": "calls CGame__SetSlot, then re-reads slot/value and calls CCareer__SetSlot on CAREER at 0x00660620",
        "boundary": "static persistent-slot bridge only; runtime save/write behavior remains unproven",
        "metadataTokens": ("SetSlotSave(slot,val)", "CCareer__SetSlot", "0x00660620"),
        "decompile": "00533900_IScript__SetSlotSave.c",
        "decompileTokens": ("CGame__SetSlot", "CCareer__SetSlot", "CAREER"),
    },
    {
        "command": "GetSlot",
        "address": "0x005339a0",
        "name": "IScript__GetSlotBitValue",
        "bridge": "runtime-slot-query",
        "evidence": "allocates an 8-byte bool result, calls CGame__GetSlot, installs vtable 0x005e4d50, and writes through out_result",
        "boundary": "static result-object bridge only; runtime query result behavior remains unproven",
        "metadataTokens": ("GetSlot(slot)", "0x005e4d50", "out_result"),
        "decompile": "005339a0_IScript__GetSlotBitValue.c",
        "decompileTokens": ("OID__AllocObject(8", "CGame__GetSlot", "out_result"),
    },
]

CGAME_HELPERS: list[dict[str, Any]] = [
    {
        "address": "0x0046d3a0",
        "name": "CGame__SetSlot",
        "evidence": "range-checks slot 0..255, computes slot>>5 and 1<<(slot&31), and mutates runtime CGame slot array at this+0x308",
        "metadataTokens": ("Wave803 static read-back", "this+0x308", "IScript__SetSlot", "IScript__SetSlotSave"),
    },
    {
        "address": "0x0046d410",
        "name": "CGame__GetSlot",
        "evidence": "range-checks slot 0..255, computes slot>>5 and 1<<(slot&31), reads this+0x308, and returns false on out-of-range input",
        "metadataTokens": ("Wave803 static read-back", "this+0x308", "IScript__GetSlotBitValue", "returning false"),
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


def parse_slot_call(call: str) -> tuple[str, str]:
    match = re.match(r"([A-Za-z0-9_]+)\((.*)\)", call)
    if not match:
        raise ValueError(call)
    return match.group(1), match.group(2).strip()


def mission_slot_corpus() -> dict[str, Any]:
    text = read_text(MISSION_SLOT_DOC)
    detailed = text.split("## Detailed Call Sites", 1)[1]
    rows: list[dict[str, Any]] = []
    for line in detailed.splitlines():
        if not line.startswith("| ") or " | `" not in line or line.startswith("|------"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) != 4:
            continue
        level, directory, filename, raw_call = parts
        call = raw_call.strip("`")
        command, slot_expression = parse_slot_call(call)
        rows.append(
            {
                "level": int(level),
                "dir": directory,
                "file": filename,
                "command": command,
                "slotExpression": slot_expression,
                "call": call,
                "occurrence": sum(1 for prior in rows if prior["call"] == call and prior["dir"] == directory and prior["file"] == filename) + 1,
            }
        )

    command_counts = {
        "GetSlot": sum(row["command"] == "GetSlot" for row in rows),
        "SetSlot": sum(row["command"] == "SetSlot" for row in rows),
        "SetSlotSave": sum(row["command"] == "SetSlotSave" for row in rows),
    }
    return {
        "source": "reverse-engineering/game-assets/mission-slot-usage.md",
        "levelRows": 6,
        "detailedCallRows": len(rows),
        "commandCounts": command_counts,
        "dirs": sorted({row["dir"] for row in rows}, key=lambda value: (value.lower(), value)),
        "slotExpressions": ["SLOT_TUTORIAL_1", "SLOT_TUTORIAL_2", "SLOT_TUTORIAL_3", "SLOT_TUTORIAL_4", "61", "62", "n", "n + 29"],
        "calls": rows,
        "boundary": "loose corpus evidence only; live loose-MSL loading and packed-vs-loose script selection remain unproven",
    }


def evidence_counts() -> dict[str, int]:
    return {
        "wave579MetadataRows": len(read_tsv_rows(WAVE579 / "post_metadata.tsv")),
        "wave579TagRows": len(read_tsv_rows(WAVE579 / "post_tags.tsv")),
        "wave579XrefRows": len(read_tsv_rows(WAVE579 / "post_xrefs.tsv")),
        "wave579InstructionRows": len(read_tsv_rows(WAVE579 / "post_target_instructions.tsv")),
        "wave579DecompileRows": len(read_tsv_rows(WAVE579 / "post_decompile" / "index.tsv")),
        "wave579VtableRows": len(read_tsv_rows(WAVE579 / "post_vtables.tsv")),
        "wave803MetadataRows": len(read_tsv_rows(WAVE803 / "post-metadata.tsv")),
        "wave803TagRows": len(read_tsv_rows(WAVE803 / "post-tags.tsv")),
        "wave803XrefRows": len(read_tsv_rows(WAVE803 / "post-xrefs.tsv")),
        "wave803InstructionRows": len(read_tsv_rows(WAVE803 / "post-instructions.tsv")),
        "wave803DecompileRows": len(read_tsv_rows(WAVE803 / "post-decompile" / "index.tsv")),
    }


def descriptor_records() -> dict[str, Any]:
    descriptor = read_json(DESCRIPTOR_SCHEMA)
    records = {record["commandName"]: record for record in descriptor["records"] if record.get("commandName")}
    return {
        command: {
            "index": record["index"],
            "recordAddress": record["recordAddress"],
            "observedNameSymbol": record["observedNameSymbol"],
            "nameStatus": record["nameStatus"],
        }
        for command, record in records.items()
        if command in DESCRIPTOR_SLOTS
    }


def build_schema() -> dict[str, Any]:
    return {
        "schemaVersion": "missionscript-slot-command-effect.v1",
        "status": "PASS",
        "source": {
            "evidenceWaves": ["Wave579", "Wave803", "Wave903"],
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static slot command-effect bridge mapping for clean-room planning, not runtime proof",
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
        "missionSlotCorpus": mission_slot_corpus(),
        "bridges": {
            "runtimeSlotArray": "CGame::mSlots at CGame+0x308, accessed by CGame__SetSlot and CGame__GetSlot",
            "persistentCareerSlots": "SetSlotSave also calls CCareer__SetSlot; on-disk true-view offset for CCareer.mSlots[0] is 0x240A",
            "commandDescriptorDependency": "ScriptCommandRegistry__InitBuiltins descriptor table at 0x0064ce50 registers SetSlot, GetSlot, and SetSlotSave",
        },
        "handlers": [
            {key: value for key, value in handler.items() if key not in {"metadataTokens", "decompile", "decompileTokens"}}
            for handler in HANDLERS
        ],
        "cgameHelpers": [
            {key: value for key, value in helper.items() if key != "metadataTokens"}
            for helper in CGAME_HELPERS
        ],
        "claims": [
            "The static slot command bridge separates runtime CGame slot bits from immediate persistent CCareer slot writes.",
            "The loose slot corpus contains 6 slot-using level rows and 18 detailed call rows: 6 GetSlot calls, 8 SetSlot calls, and 4 SetSlotSave calls.",
            "The schema maps descriptor names, IScript slot handlers, CGame slot helpers, and the CCareer slot persistence helper without claiming runtime command effects.",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime command effects",
            "runtime save behavior",
            "runtime slot persistence",
            "runtime mission outcome",
            "tutorial progression",
            "Level500 branch behavior",
            "Fenrir state behavior",
            "live loose-MSL loading",
            "packed-vs-loose script selection",
            "exact command descriptor layout",
            "exact arity",
            "exact argument type schema",
            "exact CGame layout",
            "exact CCareer layout",
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
        corpus = actual["missionSlotCorpus"]
        require(corpus["levelRows"] == 6, "slot level-row count mismatch", failures)
        require(corpus["detailedCallRows"] == 18, "slot detailed call count mismatch", failures)
        require(corpus["commandCounts"] == {"GetSlot": 6, "SetSlot": 8, "SetSlotSave": 4}, "slot command counts mismatch", failures)
        for command, expected_slot in DESCRIPTOR_SLOTS.items():
            record = actual["descriptorSlots"].get(command)
            require(record is not None, f"missing descriptor slot for {command}", failures)
            if record is not None:
                require(record["index"] == expected_slot["index"], f"{command} descriptor index mismatch", failures)
                require(record["recordAddress"] == expected_slot["recordAddress"], f"{command} descriptor address mismatch", failures)
                require(record["observedNameSymbol"] == expected_slot["symbol"], f"{command} descriptor symbol mismatch", failures)
        check_no_bad_tokens(path, failures)


def check_artifacts(failures: list[str]) -> None:
    counts = evidence_counts()
    expected_counts = {
        "wave579MetadataRows": 6,
        "wave579TagRows": 6,
        "wave579XrefRows": 6,
        "wave579InstructionRows": 1326,
        "wave579DecompileRows": 6,
        "wave579VtableRows": 24,
        "wave803MetadataRows": 2,
        "wave803TagRows": 2,
        "wave803XrefRows": 3,
        "wave803InstructionRows": 170,
        "wave803DecompileRows": 2,
    }
    for key, expected in expected_counts.items():
        require(counts.get(key) == expected, f"{key} mismatch: {counts.get(key)} != {expected}", failures)

    wave579_metadata = tsv_by_address(WAVE579 / "post_metadata.tsv")
    for handler in HANDLERS:
        row = wave579_metadata.get(handler["address"])
        require(row is not None, f"missing Wave579 metadata row {handler['address']}", failures)
        if row is not None:
            require(row["name"] == handler["name"], f"Wave579 name mismatch at {handler['address']}", failures)
            require_tokens(f"Wave579 comment {handler['address']}", row["comment"], handler["metadataTokens"], failures)
        decompile = read_text(WAVE579 / "post_decompile" / handler["decompile"])
        require_tokens(f"Wave579 decompile {handler['address']}", decompile, handler["decompileTokens"], failures)

    wave803_metadata = tsv_by_address(WAVE803 / "post-metadata.tsv")
    for helper in CGAME_HELPERS:
        row = wave803_metadata.get(helper["address"])
        require(row is not None, f"missing Wave803 metadata row {helper['address']}", failures)
        if row is not None:
            require(row["name"] == helper["name"], f"Wave803 name mismatch at {helper['address']}", failures)
            require_tokens(f"Wave803 comment {helper['address']}", row["comment"], helper["metadataTokens"], failures)

    wave579_backup = read_json(WAVE579 / "wave579_backup_summary.json")
    require(wave579_backup.get("destination") == WAVE579_BACKUP, "Wave579 backup path mismatch", failures)
    require(wave579_backup.get("status") == "PASS", "Wave579 backup status mismatch", failures)
    require(wave579_backup.get("diffCount") == 0, "Wave579 backup diff mismatch", failures)

    wave803_backup = read_json(WAVE803 / "backup-summary.json")
    require(wave803_backup.get("backupPath") == WAVE803_BACKUP, "Wave803 backup path mismatch", failures)
    require(wave803_backup.get("diffCount") == 0, "Wave803 backup diff mismatch", failures)

    event_schema = read_json(EVENT_SCHEMA)
    require(event_schema["status"] == "PASS", "event/object-code schema prerequisite is not PASS", failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        "MissionScript Slot Command-Effect Static Proof",
        PROOF_LINK,
        SCHEMA_LINK,
        "Status: static slot command-effect schema proof complete, not runtime proof",
        "SetSlot",
        "GetSlot",
        "SetSlotSave",
        "IScript__SetSlot",
        "IScript__SetSlotSave",
        "IScript__GetSlotBitValue",
        "CGame__SetSlot",
        "CGame__GetSlot",
        "CCareer__SetSlot",
        "CGame+0x308",
        "0x240A",
        "6 slot-using level rows",
        "18 detailed slot call rows",
        "6 GetSlot",
        "8 SetSlot",
        "4 SetSlotSave",
        "0x0064ecd0",
        "0x0064ed10",
        "0x0064ef50",
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
        MISSION_SLOT_DOC,
        MSL_COMMANDS,
        MSL_SCRIPTING,
        CGAME_SET_DOC,
        CGAME_GET_DOC,
        CCAREER_SLOT_DOC,
        GAME_INDEX,
        CAREER_INDEX,
    )
    for path in front_door_docs:
        text = read_text(path)
        for token in (PROOF_LINK, SCHEMA_LINK, "MissionScript Slot Command-Effect"):
            require(token in text, f"{path.relative_to(ROOT)} missing slot proof token: {token}", failures)
        check_no_bad_tokens(path, failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\missionscript_slot_command_effect_static_probe.py --check"
    actual_script = package.get("scripts", {}).get("test:missionscript-slot-command-effect-static")
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
            print("MissionScript slot command-effect static probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript slot command-effect static probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
