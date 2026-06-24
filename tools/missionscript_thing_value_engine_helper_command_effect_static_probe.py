#!/usr/bin/env python3
"""Validate the MissionScript thing-value/engine-helper command-effect static proof."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect-static-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect-static-proof.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_thing_value_engine_helper_command_effect_static_proof_2026-06-08.md"

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
MSL_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
LORE_MSL_COMMANDS = ROOT / "lore-book" / "reverse-engineering" / "quick-reference" / "msl-commands.md"
PACKAGE_JSON = ROOT / "package.json"

WAVE582 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave582-iscript-thing-value-00534fb0"
MSL_ROOT = ROOT / "game" / "data" / "MissionScripts"
WAVE1219_BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
WAVE582_BACKUP = r"G:\GhidraBackups\BEA_20260519-082352_post_wave582_iscript_thing_value_verified"

PROOF_LINK = "missionscript-thing-value-engine-helper-command-effect-static-proof.md"
SCHEMA_LINK = "missionscript-thing-value-engine-helper-command-effect.v1.json"

DESCRIPTOR_COMMANDS = {
    "SetWindVector": {"index": 41, "recordAddress": "0x0064d890", "handler": "IScript__SetThingRefViaCUnitHelper4FD830_FromArg"},
    "DisableWeapon": {"index": 98, "recordAddress": "0x0064e6d0", "handler": "IScript__SetThingValueViaVFunc198_FromArg"},
    "EnableFlightMode": {"index": 99, "recordAddress": "0x0064e710", "handler": "IScript__SetThingValueViaVFunc19C_FromArg"},
    "TeleportOrientation": {"index": 138, "recordAddress": "0x0064f0d0", "handler": "IScript__SetThingFloatViaVFunc1C8_FromArg"},
    "DisableSpawner": {"index": 140, "recordAddress": "0x0064f150", "handler": "IScript__SetThingValueViaEngineHelper4FE390_FromArg"},
    "SetName": {"index": 141, "recordAddress": "0x0064f190", "handler": "IScript__SetThingValueViaEngineHelper4FE3F0_FromArg"},
}

DIRECT_MSL_TOKENS = tuple(DESCRIPTOR_COMMANDS.keys())

THING_HANDLERS = [
    {
        "address": "0x00534fb0",
        "name": "IScript__SetThingValueViaVFunc198_FromArg",
        "signature": "void __thiscall IScript__SetThingValueViaVFunc198_FromArg(void * this, void * script_args, void * unused_state, void * out_result)",
        "summary": "guards on context flag +0x34 & 0x10, reads the first script argument through datatype getter slot +0x38, and dispatches selected thing vfunc slot +0x198",
        "commentTokens": ("+0x34 & 0x10", "+0x38", "+0x198", "ScriptCommandRegistry__InitBuiltins"),
        "decompile": "00534fb0_IScript__SetThingValueViaVFunc198_FromArg.c",
        "decompileTokens": ("+ 0x38", "+ 0x198", "*(int **)((int)this + 0x10) + 0xd"),
    },
    {
        "address": "0x00534fe0",
        "name": "IScript__SetThingValueViaVFunc19C_FromArg",
        "signature": "void __thiscall IScript__SetThingValueViaVFunc19C_FromArg(void * this, void * script_args, void * unused_state, void * out_result)",
        "summary": "guards on context flag +0x34 & 0x10, reads the first script argument through datatype getter slot +0x38, and dispatches selected thing vfunc slot +0x19c",
        "commentTokens": ("+0x34 & 0x10", "+0x38", "+0x19c", "ScriptCommandRegistry__InitBuiltins"),
        "decompile": "00534fe0_IScript__SetThingValueViaVFunc19C_FromArg.c",
        "decompileTokens": ("+ 0x38", "+ 0x19c", "*(int **)((int)this + 0x10) + 0xd"),
    },
    {
        "address": "0x00535010",
        "name": "IScript__SetThingValueViaEngineHelper4FE390_FromArg",
        "signature": "void __thiscall IScript__SetThingValueViaEngineHelper4FE390_FromArg(void * this, void * script_args, void * unused_state, void * out_result)",
        "summary": "guards on context flag +0x34 & 0x10, reads the first script argument through datatype getter slot +0x38, and calls CEngine__EnableThingByNameFlag(context+0x10, thing_name)",
        "commentTokens": ("+0x34 & 0x10", "+0x38", "CEngine__EnableThingByNameFlag", "ScriptCommandRegistry__InitBuiltins"),
        "decompile": "00535010_IScript__SetThingValueViaEngineHelper4FE390_FromArg.c",
        "decompileTokens": ("+ 0x38", "CEngine__EnableThingByNameFlag", "+ 0x34"),
    },
    {
        "address": "0x00535040",
        "name": "IScript__SetThingValueViaEngineHelper4FE3F0_FromArg",
        "signature": "void __thiscall IScript__SetThingValueViaEngineHelper4FE3F0_FromArg(void * this, void * script_args, void * unused_state, void * out_result)",
        "summary": "guards on context flag +0x34 & 0x10, reads the first script argument through datatype getter slot +0x38, and calls CEngine__DisableThingByNameFlag(context+0x10, thing_name)",
        "commentTokens": ("+0x34 & 0x10", "+0x38", "CEngine__DisableThingByNameFlag", "ScriptCommandRegistry__InitBuiltins"),
        "decompile": "00535040_IScript__SetThingValueViaEngineHelper4FE3F0_FromArg.c",
        "decompileTokens": ("+ 0x38", "CEngine__DisableThingByNameFlag", "+ 0x34"),
    },
    {
        "address": "0x00535530",
        "name": "IScript__SetThingFloatViaVFunc1C8_FromArg",
        "signature": "void __thiscall IScript__SetThingFloatViaVFunc1C8_FromArg(void * this, void * script_args, void * unused_state, void * out_result)",
        "summary": "guards on context flag +0x34 & 0x10, reads a float through datatype getter slot +0x34, and dispatches selected thing vfunc slot +0x1c8",
        "commentTokens": ("+0x34 & 0x10", "+0x34", "+0x1c8", "ScriptCommandRegistry__InitBuiltins"),
        "decompile": "00535530_IScript__SetThingFloatViaVFunc1C8_FromArg.c",
        "decompileTokens": ("+ 0x34", "+ 0x1c8", "(float)fVar2"),
    },
    {
        "address": "0x00535560",
        "name": "IScript__SetThingRefViaCUnitHelper4FD830_FromArg",
        "signature": "void __thiscall IScript__SetThingRefViaCUnitHelper4FD830_FromArg(void * this, void * script_args, void * unused_state, void * out_result)",
        "summary": "guards on context flag +0x34 & 0x10, reads an integer/faction-like state through datatype getter slot +0x30, and calls CUnit__SetFactionForHierarchy(context+0x10, faction_state)",
        "commentTokens": ("+0x34 & 0x10", "+0x30", "CUnit__SetFactionForHierarchy", "ScriptCommandRegistry__InitBuiltins"),
        "decompile": "00535560_IScript__SetThingRefViaCUnitHelper4FD830_FromArg.c",
        "decompileTokens": ("+ 0x30", "CUnit__SetFactionForHierarchy", "faction_state"),
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
    "runtime disableweapon proven",
    "runtime enableflightmode proven",
    "runtime disablespawner proven",
    "exact command descriptor layout proven",
    "exact thing vfunc semantics proven",
    "exact thing layout proven",
    "exact unit faction enum proven",
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


def normalize_address(value: str) -> str:
    value = value.lower().strip()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def tsv_by_address(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row[key]): row for row in read_tsv_rows(path)}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def require_tokens(label: str, text: str, tokens: tuple[str, ...], failures: list[str]) -> None:
    for token in tokens:
        require(token in text, f"{label} missing token: {token}", failures)


def evidence_counts() -> dict[str, int]:
    return {
        "wave582MetadataRows": len(read_tsv_rows(WAVE582 / "post_metadata.tsv")),
        "wave582TagRows": len(read_tsv_rows(WAVE582 / "post_tags.tsv")),
        "wave582XrefRows": len(read_tsv_rows(WAVE582 / "post_xrefs.tsv")),
        "wave582InstructionRows": len(read_tsv_rows(WAVE582 / "post_target_instructions.tsv")),
        "wave582DecompileRows": len(read_tsv_rows(WAVE582 / "post_decompile" / "index.tsv")),
        "wave582VtableRows": len(read_tsv_rows(WAVE582 / "post_vtables.tsv")),
    }


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
            "postWave582HandlerName": expected["handler"],
            "rawShapeValues": {
                offset: raw.get(offset)
                for offset in ("+0x14", "+0x18", "+0x1c", "+0x20", "+0x24", "+0x28", "+0x2c", "+0x30", "+0x38")
                if raw.get(offset) is not None
            },
            "boundary": "raw static descriptor record only; exact descriptor field layout, exact command arity, and runtime command effect remain unproven",
        }
    return result


def direct_msl_usage() -> dict[str, Any]:
    counts = {token: 0 for token in DIRECT_MSL_TOKENS}
    examples: list[str] = []
    if MSL_ROOT.is_dir():
        for path in MSL_ROOT.rglob("*.msl"):
            for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
                stripped = line.strip()
                if not stripped or stripped.startswith("//"):
                    continue
                for token in DIRECT_MSL_TOKENS:
                    if token in stripped:
                        counts[token] += 1
                        if len(examples) < 20:
                            examples.append(f"{path.relative_to(ROOT)}:{number}:{stripped}")
    return {
        "source": "game/data/MissionScripts/**/*.msl",
        "directNonCommentCounts": counts,
        "sampleRows": examples,
        "boundary": "private loose-MSL scan only; command-name usage rows are static corpus context and do not prove live loose-MSL loading or runtime command effects",
    }


def build_schema() -> dict[str, Any]:
    return {
        "schemaVersion": "missionscript-thing-value-engine-helper-command-effect.v1",
        "status": "PASS",
        "source": {
            "evidenceWaves": ["Wave582", "Wave864", "Wave903"],
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static MissionScript thing-value, engine-helper, vfunc-slot, descriptor-context, and loose-corpus command-name mapping for clean-room planning",
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
        "handlers": [
            {key: value for key, value in handler.items() if key not in {"commentTokens", "decompile", "decompileTokens"}}
            for handler in THING_HANDLERS
        ],
        "dispatchContext": {
            "guard": "+0x34 & 0x10",
            "argumentGetterSlots": ["+0x38", "+0x34", "+0x30"],
            "thingVfuncSlots": ["+0x198", "+0x19c", "+0x1c8"],
            "engineHelpers": ["CEngine__EnableThingByNameFlag", "CEngine__DisableThingByNameFlag"],
            "unitHelper": "CUnit__SetFactionForHierarchy",
            "boundary": "thing vfunc slots and helper names are static dispatch evidence; exact slot meanings, exact enums, and runtime command effects remain unproven",
        },
        "looseMslUsage": direct_msl_usage(),
        "verifiedBackups": {
            "wave582": WAVE582_BACKUP,
            "latestStaticCloseout": WAVE1219_BACKUP,
        },
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime command effects",
            "runtime DisableWeapon behavior",
            "runtime EnableFlightMode behavior",
            "runtime DisableSpawner behavior",
            "runtime SetName behavior",
            "runtime TeleportOrientation behavior",
            "runtime SetWindVector behavior",
            "live loose-MSL loading",
            "exact command descriptor layout",
            "exact command arity",
            "exact thing vfunc semantics",
            "exact thing layout",
            "exact unit faction enum",
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
        require(actual["evidenceCounts"]["wave582InstructionRows"] == 534, "Wave582 instruction count mismatch", failures)
        require(actual["looseMslUsage"]["directNonCommentCounts"]["DisableWeapon"] == 15, "DisableWeapon count mismatch", failures)
        require(actual["looseMslUsage"]["directNonCommentCounts"]["EnableFlightMode"] == 1, "EnableFlightMode count mismatch", failures)
        require(actual["looseMslUsage"]["directNonCommentCounts"]["DisableSpawner"] == 2, "DisableSpawner count mismatch", failures)
        require(actual["looseMslUsage"]["directNonCommentCounts"]["SetName"] == 4, "SetName count mismatch", failures)
        require(actual["looseMslUsage"]["directNonCommentCounts"]["TeleportOrientation"] == 5, "TeleportOrientation count mismatch", failures)
        require(actual["looseMslUsage"]["directNonCommentCounts"]["SetWindVector"] == 0, "SetWindVector count mismatch", failures)
        check_no_bad_tokens(path, failures)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "wave582MetadataRows": 6,
        "wave582TagRows": 6,
        "wave582XrefRows": 6,
        "wave582InstructionRows": 534,
        "wave582DecompileRows": 6,
        "wave582VtableRows": 32,
    }
    actual_counts = evidence_counts()
    for key, expected in expected_counts.items():
        require(actual_counts.get(key) == expected, f"{key} mismatch: {actual_counts.get(key)} != {expected}", failures)

    metadata = tsv_by_address(WAVE582 / "post_metadata.tsv")
    tags = tsv_by_address(WAVE582 / "post_tags.tsv")
    xrefs = tsv_by_address(WAVE582 / "post_xrefs.tsv", "target_addr")
    for handler in THING_HANDLERS:
        row = metadata.get(handler["address"])
        require(row is not None, f"missing Wave582 metadata row {handler['address']}", failures)
        if row is not None:
            require(row["name"] == handler["name"], f"Wave582 name mismatch at {handler['address']}", failures)
            require(row["signature"] == handler["signature"], f"Wave582 signature mismatch at {handler['address']}", failures)
            require_tokens(f"Wave582 comment {handler['address']}", row["comment"], handler["commentTokens"], failures)
        tag_row = tags.get(handler["address"])
        require(tag_row is not None, f"missing Wave582 tags row {handler['address']}", failures)
        if tag_row is not None:
            require("iscript-thing-value-wave582" in tag_row["tags"], f"Wave582 tag missing at {handler['address']}", failures)
            require("script-context-abi" in tag_row["tags"], f"script-context-abi tag missing at {handler['address']}", failures)
        xref = xrefs.get(handler["address"])
        require(xref is not None, f"missing Wave582 xref row {handler['address']}", failures)
        if xref is not None:
            require(xref["from_function"] == "ScriptCommandRegistry__InitBuiltins", f"xref owner mismatch at {handler['address']}", failures)
            require(xref["ref_type"] == "DATA", f"xref type mismatch at {handler['address']}", failures)
        decompile = read_text(WAVE582 / "post_decompile" / handler["decompile"])
        require_tokens(f"Wave582 decompile {handler['address']}", decompile, handler["decompileTokens"], failures)

    instructions = read_text(WAVE582 / "post_target_instructions.tsv")
    require_tokens(
        "Wave582 instructions",
        instructions,
        (
            "CALL\tdword ptr [EDX + 0x38]",
            "CALL\tdword ptr [EDI + 0x198]",
            "CALL\tdword ptr [EDI + 0x19c]",
            "CALL\t0x004fe390",
            "CALL\t0x004fe3f0",
            "CALL\tdword ptr [EDX + 0x34]",
            "CALL\tdword ptr [EDI + 0x1c8]",
            "CALL\tdword ptr [EDX + 0x30]",
            "CALL\t0x004fd830",
            "TEST\tbyte ptr [EAX + 0x34], 0x10",
            "RET\t0xc",
        ),
        failures,
    )

    backup = read_json(WAVE582 / "wave582_backup_summary.json")
    require(backup.get("status") == "PASS", "Wave582 backup status mismatch", failures)
    require(backup.get("destination") == WAVE582_BACKUP, "Wave582 backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "Wave582 backup file count mismatch", failures)
    require(backup.get("diffCount") == 0, "Wave582 backup diff mismatch", failures)
    require(backup.get("manifestSha256") == backup.get("destinationManifestSha256"), "Wave582 backup manifest mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        "MissionScript Thing Value / Engine Helper Command-Effect Static Proof",
        PROOF_LINK,
        SCHEMA_LINK,
        "Status: static thing-value/engine-helper command-effect schema proof complete, not runtime proof",
        "IScript__SetThingValueViaVFunc198_FromArg",
        "IScript__SetThingValueViaVFunc19C_FromArg",
        "IScript__SetThingValueViaEngineHelper4FE390_FromArg",
        "IScript__SetThingValueViaEngineHelper4FE3F0_FromArg",
        "IScript__SetThingFloatViaVFunc1C8_FromArg",
        "IScript__SetThingRefViaCUnitHelper4FD830_FromArg",
        "0x00534fb0",
        "0x00534fe0",
        "0x00535010",
        "0x00535040",
        "0x00535530",
        "0x00535560",
        "+0x38",
        "+0x34",
        "+0x30",
        "+0x198",
        "+0x19c",
        "+0x1c8",
        "CEngine__EnableThingByNameFlag",
        "CEngine__DisableThingByNameFlag",
        "CUnit__SetFactionForHierarchy",
        "DisableWeapon",
        "EnableFlightMode",
        "DisableSpawner",
        "SetName",
        "TeleportOrientation",
        "SetWindVector",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1560/1560 = 100.00%",
        "1179/1179 = 100.00%",
        WAVE1219_BACKUP,
        WAVE582_BACKUP,
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
        MSL_COMMANDS,
        LORE_MSL_COMMANDS,
    )
    for path in front_door_docs:
        text = read_text(path)
        for token in (PROOF_LINK, SCHEMA_LINK, "MissionScript Thing Value / Engine Helper Command-Effect"):
            require(token in text, f"{path.relative_to(ROOT)} missing thing-value proof token: {token}", failures)
        check_no_overclaims(path, failures)

    backlog_text = read_text(BACKLOG)
    require(
        "Completed MissionScript Thing Value / Engine Helper Command-Effect Static Proof" in backlog_text,
        "backlog no longer records completed thing-value/engine-helper proof",
        failures,
    )
    require(
        "The selected active static-to-proof slice is [MissionScript Thing Value / Engine Helper Command-Effect Static Proof]" not in backlog_text,
        "backlog still has stale active thing-value/engine-helper proof slice",
        failures,
    )
    require(
        "Completed MissionScript HUD / Display Command-Effect Static Proof" in backlog_text,
        "backlog no longer records completed HUD/display proof",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript HUD / Display Command-Effect Static Proof" not in backlog_text,
        "backlog still marks HUD/display proof active",
        failures,
    )
    require(
        "Completed MissionScript Command-Effect Rebuild Fixture Selection Proof Plan" in backlog_text,
        "backlog no longer records completed fixture-selection proof",
        failures,
    )
    require(
        "Completed MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan" in backlog_text
        or "The selected active static-to-proof slice is MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan. Status: selected" in backlog_text,
        "backlog missing active-or-completed thing-value/engine-helper fixture proof",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Player-State / Score Command-Effect Fixture Proof Plan. Status: selected" in backlog_text
        or "The selected active static-to-proof slice is MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan. Status: selected" in backlog_text,
        "backlog active slice was not advanced to Thing Value or Player-State fixture proof",
        failures,
    )
    require(
        "Completed MissionScript Vector/Range Command-Effect Static Proof" in backlog_text,
        "backlog no longer records completed vector/range proof",
        failures,
    )
    require(
        "The selected active static-to-proof slice is [MissionScript Vector/Range Command-Effect Static Proof]" not in backlog_text,
        "backlog still has stale active vector/range proof slice",
        failures,
    )

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\missionscript_thing_value_engine_helper_command_effect_static_probe.py --check"
    actual_script = package.get("scripts", {}).get("test:missionscript-thing-value-engine-helper-command-effect-static")
    require(actual_script == expected_script, "package script mismatch", failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_artifacts(failures)
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
            print("MissionScript thing-value/engine-helper command-effect static probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript thing-value/engine-helper command-effect static probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
