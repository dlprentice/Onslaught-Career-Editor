#!/usr/bin/env python3
"""Validate the MissionScript vector/range command-effect static proof."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-command-effect.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-command-effect.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-command-effect-static-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-command-effect-static-proof.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_vector_range_command_effect_static_proof_2026-06-08.md"

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

WAVE581 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave581-iscript-vector-range-005345d0"
MSL_ROOT = ROOT / "game" / "data" / "MissionScripts"
WAVE1219_BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
WAVE581_BACKUP = r"G:\GhidraBackups\BEA_20260519-075959_post_wave581_iscript_vector_range_verified"

PROOF_LINK = "missionscript-vector-range-command-effect-static-proof.md"
SCHEMA_LINK = "missionscript-vector-range-command-effect.v1.json"

DESCRIPTOR_INDICES = (56, 57, 58, 59, 60, 61, 104, 105, 108)
DIRECT_MSL_TOKENS = ("GetVectorLength", "CheckValueInRange", "GetVectorX", "GetVectorY", "GetVectorZ", "Magnitude")

VECTOR_HANDLERS = [
    {
        "address": "0x005345d0",
        "name": "IScript__GetVectorLength",
        "signature": "void __stdcall IScript__GetVectorLength(void * script_args, void * unused_state, void * out_result)",
        "summary": "reads a vector through datatype slot +0x44, computes sqrt(x*x+y*y+z*z), and returns a CFloatDataType result via vtable 0x005e4ea4",
        "commentTokens": ("GetVectorLength", "+0x44", "sqrt(x*x+y*y+z*z)", "0x005e4ea4"),
        "decompile": "005345d0_IScript__GetVectorLength.c",
        "decompileTokens": ("SQRT", "+ 0x44", "PTR_CDataType__ScalarDeletingDestructor_005e4ea4"),
    },
    {
        "address": "0x005347b0",
        "name": "IScript__CheckValueInRange",
        "signature": "void __stdcall IScript__CheckValueInRange(void * script_args, void * unused_state, void * out_result)",
        "summary": "reads value/min/max through float getter slot +0x34, accepts ascending or descending bounds, and returns a CBoolDataType-style byte result through vtable 0x005e4d50 context",
        "commentTokens": ("CheckValueInRange", "+0x34", "ascending and descending bounds", "boolean result"),
        "decompile": "005347b0_IScript__CheckValueInRange.c",
        "decompileTokens": ("+ 0x34", "CEventFunctionParam__vtable", "out_result"),
    },
    {
        "address": "0x00534b80",
        "name": "IScript__GetVectorX",
        "signature": "void __stdcall IScript__GetVectorX(void * script_args, void * unused_state, void * out_result)",
        "summary": "reads a vector through datatype slot +0x44, copies component offset +0, and returns a float result via vtable 0x005e4ea4",
        "commentTokens": ("GetVectorX", "+0", "+0x44", "0x005e4ea4"),
        "decompile": "00534b80_IScript__GetVectorX.c",
        "decompileTokens": ("+ 0x44", "PTR_CDataType__ScalarDeletingDestructor_005e4ea4", "*puVar3"),
    },
    {
        "address": "0x00534c10",
        "name": "IScript__GetVectorY",
        "signature": "void __stdcall IScript__GetVectorY(void * script_args, void * unused_state, void * out_result)",
        "summary": "reads a vector through datatype slot +0x44, copies component offset +4, and returns a float result via vtable 0x005e4ea4",
        "commentTokens": ("GetVectorY", "+4", "+0x44", "0x005e4ea4"),
        "decompile": "00534c10_IScript__GetVectorY.c",
        "decompileTokens": ("+ 0x44", "iVar3 + 4", "PTR_CDataType__ScalarDeletingDestructor_005e4ea4"),
    },
    {
        "address": "0x00534ca0",
        "name": "IScript__GetVectorZ",
        "signature": "void __stdcall IScript__GetVectorZ(void * script_args, void * unused_state, void * out_result)",
        "summary": "reads a vector through datatype slot +0x44, copies component offset +8, and returns a float result via vtable 0x005e4ea4",
        "commentTokens": ("GetVectorZ", "+8", "+0x44", "0x005e4ea4"),
        "decompile": "00534ca0_IScript__GetVectorZ.c",
        "decompileTokens": ("+ 0x44", "iVar3 + 8", "PTR_CDataType__ScalarDeletingDestructor_005e4ea4"),
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
    "runtime vector behavior proven",
    "runtime range behavior proven",
    "live loose-msl loading proven",
    "exact command descriptor layout proven",
    "exact vector layout proven",
    "exact datatype layout proven",
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
        "wave581MetadataRows": len(read_tsv_rows(WAVE581 / "post_metadata.tsv")),
        "wave581TagRows": len(read_tsv_rows(WAVE581 / "post_tags.tsv")),
        "wave581XrefRows": len(read_tsv_rows(WAVE581 / "post_xrefs.tsv")),
        "wave581InstructionRows": len(read_tsv_rows(WAVE581 / "post_target_instructions.tsv")),
        "wave581DecompileRows": len(read_tsv_rows(WAVE581 / "post_decompile" / "index.tsv")),
        "wave581VtableRows": len(read_tsv_rows(WAVE581 / "post_vtables.tsv")),
    }


def descriptor_records() -> list[dict[str, Any]]:
    schema = read_json(DESCRIPTOR_SCHEMA)
    by_index = {record["index"]: record for record in schema["records"]}
    records: list[dict[str, Any]] = []
    for index in DESCRIPTOR_INDICES:
        record = by_index[index]
        raw = {item["offset"]: item["value"] for item in record["rawAssignments"]}
        records.append(
            {
                "index": index,
                "recordAddress": record["recordAddress"],
                "commandName": record.get("commandName"),
                "observedNameSymbol": record.get("observedNameSymbol"),
                "rawEntryValue": raw.get("+0x00"),
                "rawShapeValues": {
                    offset: raw.get(offset)
                    for offset in ("+0x14", "+0x18", "+0x1c", "+0x20", "+0x24", "+0x28", "+0x2c", "+0x30", "+0x38")
                    if raw.get(offset) is not None
                },
                "boundary": "raw static descriptor record only; exact descriptor field layout and exact command arity remain unproven",
            }
        )
    return records


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
        "boundary": "private loose-MSL scan only; no direct non-comment vector/range command rows were found in the copied loose corpus during this proof",
    }


def build_schema() -> dict[str, Any]:
    return {
        "schemaVersion": "missionscript-vector-range-command-effect.v1",
        "status": "PASS",
        "source": {
            "evidenceWaves": ["Wave581", "Wave864", "Wave903"],
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static vector/range descriptor, datatype-vtable, handler-body, and loose-corpus absence mapping for clean-room MissionScript planning",
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
        "vectorHandlers": [
            {key: value for key, value in handler.items() if key not in {"commentTokens", "decompile", "decompileTokens"}}
            for handler in VECTOR_HANDLERS
        ],
        "datatypeContext": {
            "floatVtable": "0x005e4ea4",
            "boolVtable": "0x005e4d50",
            "vectorGetterSlot": "+0x44",
            "floatGetterSlot": "+0x34",
            "componentOffsets": {"x": "+0", "y": "+4", "z": "+8"},
            "boundary": "datatype vtables and getter slots are observed static evidence; exact concrete datatype/vector layouts remain unproven",
        },
        "looseMslUsage": direct_msl_usage(),
        "verifiedBackups": {
            "wave581": WAVE581_BACKUP,
            "latestStaticCloseout": WAVE1219_BACKUP,
        },
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime command effects",
            "runtime vector or range behavior",
            "live loose-MSL loading",
            "exact command descriptor layout",
            "exact datatype/vector layout",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
    }


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} contains forbidden public token: {token}", failures)


def check_no_overclaims(path: Path, failures: list[str]) -> None:
    text = read_text(path).lower()
    for token in FORBIDDEN_OVERCLAIMS:
        require(token not in text, f"{path.relative_to(ROOT)} contains overclaim token: {token}", failures)


def check_schema(failures: list[str]) -> None:
    expected = build_schema()
    for path in (SCHEMA, LORE_SCHEMA):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} is not regenerated from current evidence", failures)
        require(actual["evidenceCounts"]["wave581InstructionRows"] == 3545, "Wave581 instruction count mismatch", failures)
        require(actual["looseMslUsage"]["directNonCommentCounts"] == {token: 0 for token in DIRECT_MSL_TOKENS}, "direct MSL vector/range counts changed", failures)
        check_no_bad_tokens(path, failures)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "wave581MetadataRows": 5,
        "wave581TagRows": 5,
        "wave581XrefRows": 5,
        "wave581InstructionRows": 3545,
        "wave581DecompileRows": 5,
        "wave581VtableRows": 24,
    }
    actual_counts = evidence_counts()
    for key, expected in expected_counts.items():
        require(actual_counts.get(key) == expected, f"{key} mismatch: {actual_counts.get(key)} != {expected}", failures)

    metadata = tsv_by_address(WAVE581 / "post_metadata.tsv")
    xrefs = tsv_by_address(WAVE581 / "post_xrefs.tsv", "target_addr")
    for handler in VECTOR_HANDLERS:
        row = metadata.get(handler["address"])
        require(row is not None, f"missing Wave581 metadata row {handler['address']}", failures)
        if row is not None:
            require(row["name"] == handler["name"], f"Wave581 name mismatch at {handler['address']}", failures)
            require(row["signature"] == handler["signature"], f"Wave581 signature mismatch at {handler['address']}", failures)
            require_tokens(f"Wave581 comment {handler['address']}", row["comment"], handler["commentTokens"], failures)
        xref = xrefs.get(handler["address"])
        require(xref is not None, f"missing Wave581 xref row {handler['address']}", failures)
        if xref is not None:
            require(xref["from_function"] == "ScriptCommandRegistry__InitBuiltins", f"xref owner mismatch at {handler['address']}", failures)
        decompile = read_text(WAVE581 / "post_decompile" / handler["decompile"])
        require_tokens(f"Wave581 decompile {handler['address']}", decompile, handler["decompileTokens"], failures)

    instructions = read_text(WAVE581 / "post_target_instructions.tsv")
    require_tokens(
        "Wave581 instructions",
        instructions,
        (
            "CALL\tdword ptr [EDX + 0x44]",
            "CALL\tdword ptr [EAX + 0x34]",
            "FSQRT",
            "RET\t0xc",
        ),
        failures,
    )
    vtables = read_text(WAVE581 / "post_vtables.tsv")
    require_tokens("Wave581 vtables", vtables, ("005e4ea4", "CFloatDataType__Add", "005e4d50", "CBoolDataType__Assign"), failures)

    backup = read_json(WAVE581 / "wave581_backup_summary.json")
    require(backup.get("status") == "PASS", "Wave581 backup status mismatch", failures)
    require(backup.get("destination") == WAVE581_BACKUP, "Wave581 backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "Wave581 backup file count mismatch", failures)
    require(backup.get("diffCount") == 0, "Wave581 backup diff mismatch", failures)
    require(backup.get("manifestSha256") == backup.get("destinationManifestSha256"), "Wave581 backup manifest mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        "MissionScript Vector/Range Command-Effect Static Proof",
        PROOF_LINK,
        SCHEMA_LINK,
        "Status: static vector/range command-effect schema proof complete, not runtime proof",
        "IScript__GetVectorLength",
        "IScript__CheckValueInRange",
        "IScript__GetVectorX",
        "IScript__GetVectorY",
        "IScript__GetVectorZ",
        "0x005345d0",
        "0x005347b0",
        "0x00534b80",
        "0x00534c10",
        "0x00534ca0",
        "0x005e4ea4",
        "0x005e4d50",
        "+0x44",
        "+0x34",
        "no direct non-comment loose-MSL rows",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1560/1560 = 100.00%",
        "1179/1179 = 100.00%",
        WAVE1219_BACKUP,
        WAVE581_BACKUP,
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
        for token in (PROOF_LINK, SCHEMA_LINK, "MissionScript Vector/Range Command-Effect"):
            require(token in text, f"{path.relative_to(ROOT)} missing vector/range proof token: {token}", failures)
        check_no_overclaims(path, failures)

    backlog_text = read_text(BACKLOG)
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
    require(
        "The selected active static-to-proof slice is [MissionScript Cutscene Pan-Camera / Position Command-Effect Static Proof]" not in backlog_text,
        "backlog still has stale active cutscene proof slice",
        failures,
    )

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\missionscript_vector_range_command_effect_static_probe.py --check"
    actual_script = package.get("scripts", {}).get("test:missionscript-vector-range-command-effect-static")
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
            print("MissionScript vector/range command-effect static probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript vector/range command-effect static probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
