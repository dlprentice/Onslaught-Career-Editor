#!/usr/bin/env python3
"""Validate the MissionScript Goodie-state command-effect static proof."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-command-effect.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-command-effect.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-command-effect-static-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-command-effect-static-proof.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_goodie_state_command_effect_static_proof_2026-06-08.md"

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
LORE_ISCRIPT_DOC = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
CAREER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "_index.md"
LORE_CAREER_DOC = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "_index.md"
GOODIES_DOC = ROOT / "reverse-engineering" / "save-file" / "goodies-system.md"
MSL_SCRIPTING = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
MSL_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
SAVE_FORMAT = ROOT / "reverse-engineering" / "save-file" / "save-format.md"
PACKAGE_JSON = ROOT / "package.json"

WAVE579 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave579-iscript-slot-goodie-005338a0"
WAVE1219_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
WAVE579_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260519-041839_post_wave579_iscript_slot_goodie_verified"

PROOF_LINK = "missionscript-goodie-state-command-effect-static-proof.md"
SCHEMA_LINK = "missionscript-goodie-state-command-effect.v1.json"

DESCRIPTOR_COMMANDS = {
    "AddScore": {"index": 84, "recordAddress": "0x0064e350", "symbol": "s_AddScore_0064f5c4"},
    "SetGoodieState": {"index": 118, "recordAddress": "0x0064ebd0", "symbol": "s_SetGoodieState_0064f380"},
    "GetGoodieState": {"index": 119, "recordAddress": "0x0064ec10", "symbol": "s_GetGoodieState_0064f370"},
}

GOODIE_HANDLERS = [
    {
        "command": "SetGoodieState",
        "address": "0x00533a70",
        "name": "IScript__SetGoodieState",
        "signature": "void __stdcall IScript__SetGoodieState(void * script_args, void * unused_state, void * out_result)",
        "summary": "reads a 1-based script Goodie index and state, then writes g_Career_mGoodies[index-1]",
        "metadataTokens": ("SetGoodieState(index,state)", "g_Career_mGoodies[index-1]", "index 0 would underflow"),
        "decompile": "00533a70_IScript__SetGoodieState.c",
        "decompileTokens": ("DAT_00662560", "script_args", "0x30"),
    },
    {
        "command": "GetGoodieState",
        "address": "0x00533aa0",
        "name": "IScript__GetGoodieState",
        "signature": "void __stdcall IScript__GetGoodieState(void * script_args, void * unused_state, void * out_result)",
        "summary": "allocates an 8-byte integer result, reads g_Career_mGoodies[index-1], installs vtable 0x005e4af8, and writes out_result",
        "metadataTokens": ("GetGoodieState(index)", "0x005e4af8", "out_result"),
        "decompile": "00533aa0_IScript__GetGoodieState.c",
        "decompileTokens": ("OID__AllocObject(8", "g_Career_mGoodies", "out_result"),
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
    "runtime goodie state proven",
    "runtime save behavior proven",
    "runtime goodie wall behavior proven",
    "live loose-msl loading proven",
    "exact command descriptor layout proven",
    "exact ccareer layout proven",
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


def evidence_counts() -> dict[str, int]:
    return {
        "wave579MetadataRows": len(read_tsv_rows(WAVE579 / "post_metadata.tsv")),
        "wave579TagRows": len(read_tsv_rows(WAVE579 / "post_tags.tsv")),
        "wave579XrefRows": len(read_tsv_rows(WAVE579 / "post_xrefs.tsv")),
        "wave579InstructionRows": len(read_tsv_rows(WAVE579 / "post_target_instructions.tsv")),
        "wave579DecompileRows": len(read_tsv_rows(WAVE579 / "post_decompile" / "index.tsv")),
        "wave579VtableRows": len(read_tsv_rows(WAVE579 / "post_vtables.tsv")),
    }


def descriptor_records() -> dict[str, Any]:
    descriptor = read_json(DESCRIPTOR_SCHEMA)
    records = {record["commandName"]: record for record in descriptor["records"] if record.get("commandName")}
    result: dict[str, Any] = {}
    for command, expected in DESCRIPTOR_COMMANDS.items():
        record = records[command]
        raw_entry = next(item["value"] for item in record["rawAssignments"] if item["offset"] == "+0x00")
        result[command] = {
            "index": record["index"],
            "recordAddress": record["recordAddress"],
            "observedNameSymbol": record["observedNameSymbol"],
            "rawEntryValue": raw_entry,
            "nameStatus": record["nameStatus"],
            "expectedSymbol": expected["symbol"],
        }
        if command == "AddScore":
            result[command]["aliasBoundary"] = "0x00534410 IScript__SecondaryObjectiveComplete"
    return result


def build_schema() -> dict[str, Any]:
    return {
        "schemaVersion": "missionscript-goodie-state-command-effect.v1",
        "status": "PASS",
        "source": {
            "evidenceWaves": ["Wave579", "Wave864", "Wave903"],
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static Goodie state command descriptor, handler-body, and save-offset bridge mapping for clean-room planning",
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
        "handlerReadback": [
            {key: value for key, value in handler.items() if key not in {"metadataTokens", "decompile", "decompileTokens"}}
            for handler in GOODIE_HANDLERS
        ],
        "saveMapping": {
            "careerGlobal": "0x00660620",
            "goodieArraySymbol": "g_Career_mGoodies",
            "goodieArrayAddress": "0x00662564",
            "entryCount": 300,
            "displayableEntries": "0-232",
            "reservedPreserveEntries": "233-299",
            "trueViewFileBase": "0x1F46",
            "scriptIndexing": "1-based; script index N maps to save Goodie index N-1",
            "fileOffsetFormula": "0x1F46 + (script_index - 1) * 4",
            "stateValues": {
                "0": "GS_UNKNOWN",
                "1": "GS_INSTRUCTIONS",
                "2": "GS_NEW",
                "3": "GS_OLD",
            },
            "zeroIndexBoundary": "script index 0 would underflow before g_Career_mGoodies[0]",
        },
        "scriptCorpusContext": {
            "source": "reverse-engineering/save-file/goodies-system.md",
            "knownScriptGoodieCalls": "documented 1-based calls for indices 51, 53, and 68-71",
            "corpusProbeSummary": "existing Goodies docs record 32 Goodie state calls and zero calls for 72-74 in repo-local and installed loose corpora",
            "boundary": "loose corpus and doc context only; live loose-MSL loading and packed-vs-loose script selection remain unproven",
        },
        "addScoreBoundary": {
            "descriptorIndex": 84,
            "descriptorRecord": "0x0064e350",
            "observedNameSymbol": "s_AddScore_0064f5c4",
            "rawEntryValue": "IScript__Unk_00534410",
            "conflictingCurrentObjectiveName": "0x00534410 IScript__SecondaryObjectiveComplete",
            "status": "descriptor/name context only in this proof",
            "whyDeferred": "existing docs expose AddScore as an MSL command and descriptor row, but this slice does not promote a saved handler-body bridge for AddScore; the raw entry is preserved as an alias-boundary conflict with current objective/outcome evidence",
        },
        "claims": [
            "The static descriptor schema contains SetGoodieState and GetGoodieState command names and record addresses.",
            "Wave579 saved IScript__SetGoodieState and IScript__GetGoodieState as fixed three-stack-argument command handlers.",
            "The Goodie handlers statically bridge MissionScript 1-based indices to g_Career_mGoodies[index-1].",
            "The save docs map the same Goodie array to true-view file offset 0x1F46 with 300 4-byte entries.",
            "AddScore is preserved as descriptor-adjacent context only and is not claimed as a handler-body proof in this slice.",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime command effects",
            "runtime Goodie state mutation",
            "runtime save behavior",
            "runtime Goodies wall behavior",
            "live loose-MSL loading",
            "packed-vs-loose script selection",
            "exact command descriptor layout",
            "exact command arity",
            "exact argument type schema",
            "exact CCareer layout",
            "AddScore handler-body proof",
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
        require(actual["saveMapping"]["entryCount"] == 300, "Goodie entry count mismatch", failures)
        require(actual["saveMapping"]["trueViewFileBase"] == "0x1F46", "Goodie true-view base mismatch", failures)
        require(actual["descriptorRecords"]["SetGoodieState"]["index"] == 118, "SetGoodieState descriptor index mismatch", failures)
        require(actual["descriptorRecords"]["GetGoodieState"]["index"] == 119, "GetGoodieState descriptor index mismatch", failures)
        require(actual["addScoreBoundary"]["status"] == "descriptor/name context only in this proof", "AddScore boundary mismatch", failures)
        check_no_bad_tokens(path, failures)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "wave579MetadataRows": 6,
        "wave579TagRows": 6,
        "wave579XrefRows": 6,
        "wave579InstructionRows": 1326,
        "wave579DecompileRows": 6,
        "wave579VtableRows": 24,
    }
    actual_counts = evidence_counts()
    for key, expected in expected_counts.items():
        require(actual_counts.get(key) == expected, f"{key} mismatch: {actual_counts.get(key)} != {expected}", failures)

    metadata = tsv_by_address(WAVE579 / "post_metadata.tsv")
    for handler in GOODIE_HANDLERS:
        row = metadata.get(handler["address"])
        require(row is not None, f"missing Wave579 metadata row {handler['address']}", failures)
        if row is not None:
            require(row["name"] == handler["name"], f"Wave579 name mismatch at {handler['address']}", failures)
            require(row["signature"] == handler["signature"], f"Wave579 signature mismatch at {handler['address']}", failures)
            require_tokens(f"Wave579 comment {handler['address']}", row["comment"], handler["metadataTokens"], failures)
        decompile = read_text(WAVE579 / "post_decompile" / handler["decompile"])
        require_tokens(f"Wave579 decompile {handler['address']}", decompile, handler["decompileTokens"], failures)

    instructions = read_text(WAVE579 / "post_target_instructions.tsv")
    require_tokens("Wave579 instructions", instructions, ("0x662560", "0x662564", "0x5e4af8"), failures)
    vtables = read_text(WAVE579 / "post_vtables.tsv")
    require_tokens("Wave579 vtables", vtables, ("005e4af8", "CIntDataType__Add"), failures)
    backup = read_json(WAVE579 / "wave579_backup_summary.json")
    require(backup.get("status") == "PASS", "Wave579 backup status mismatch", failures)
    backup_destination = backup.get("destinationRoot") or backup.get("destination")
    require(backup_destination == WAVE579_BACKUP, "Wave579 backup path mismatch", failures)
    require(backup.get("diffCount") == 0, "Wave579 backup diff mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        "MissionScript Goodie State Command-Effect Static Proof",
        PROOF_LINK,
        SCHEMA_LINK,
        "Status: static Goodie state command-effect schema proof complete, not runtime proof",
        "SetGoodieState",
        "GetGoodieState",
        "IScript__SetGoodieState",
        "IScript__GetGoodieState",
        "g_Career_mGoodies[index-1]",
        "0x00662564",
        "0x1F46",
        "300",
        "script index N maps to save Goodie index N-1",
        "AddScore",
        "descriptor/name context only",
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
        CAREER_DOC,
        LORE_CAREER_DOC,
        GOODIES_DOC,
        MSL_SCRIPTING,
        MSL_COMMANDS,
        SAVE_FORMAT,
    )
    for path in front_door_docs:
        text = read_text(path)
        for token in (PROOF_LINK, SCHEMA_LINK, "MissionScript Goodie State Command-Effect"):
            require(token in text, f"{path.relative_to(ROOT)} missing Goodie-state proof token: {token}", failures)
        check_no_overclaims(path, failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\missionscript_goodie_state_command_effect_static_probe.py --check"
    actual_script = package.get("scripts", {}).get("test:missionscript-goodie-state-command-effect-static")
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
            print("MissionScript Goodie-state command-effect static probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript Goodie-state command-effect static probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
