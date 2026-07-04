#!/usr/bin/env python3
"""Validate the MissionScript VM/datatype/opcode schema proof."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vm-datatype-opcode-schema.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-vm-datatype-opcode-schema.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vm-datatype-opcode-schema-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-vm-datatype-opcode-schema-proof.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_vm_datatype_opcode_schema_2026-06-08.md"
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
ASM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AsmInstruction.cpp.md"
DATATYPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DataType.cpp.md"
SCRIPT_OBJECT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ScriptObjectCode.cpp.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

WAVE573 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave573-script-datatype-head-0052d040"
WAVE574 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave574-script-opcode-bool-head-0052e0f0"
WAVE575 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave575-datatype-factory-float-head-0052ec60"
WAVE587 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave587-scriptobjectcode-core-00538ea0"
WAVE1189 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1189-missionscript-bytecode-iscript-current-risk-review"

SPAWN_DECOMPILE = WAVE573 / "post_decompile" / "0052d3d0_CAsmInstruction__SpawnFromOpcode.c"
DATATYPE_DECOMPILE = WAVE575 / "post_decompile" / "0052ec60_CDataType__CreateFromType.c"
RUN_DECOMPILE = WAVE587 / "post" / "decompile" / "00539b00_CScriptObjectCode__Run.c"
CALL_DECOMPILE = WAVE574 / "post_decompile" / "0052ea40_CAsmInstruction__ExecuteCall.c"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
PROOF_LINK = "missionscript-vm-datatype-opcode-schema-proof.md"
SCHEMA_LINK = "missionscript-vm-datatype-opcode-schema.v1.json"

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
    "runtime opcode behavior proven",
    "exact vm layout proven",
    "exact datatype layout proven",
    "exact opcode layout proven",
    "exact instruction object layout proven",
    "exact descriptor field layout proven",
    "exact source identity proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


OPCODES: list[dict[str, Any]] = [
    {"opcode": 0x00, "label": "NOOP_0", "vtable": "0x005e4d40", "executor": "SharedVFunc__NoOp_Ret0C", "executorAddress": "0x00453ac0", "status": "observed-shared-noop"},
    {"opcode": 0x01, "label": "PLUS", "vtable": "0x005e4d30", "executor": "CInstructionOP_PLUS__VFunc_00_0052e180", "executorAddress": "0x0052e180", "datatypeSlot": "+0x04", "stackEffect": "pop2-dispatch-push1"},
    {"opcode": 0x02, "label": "MINUS", "vtable": "0x005e4d20", "executor": "CInstructionOP_MINUS__VFunc_00_0052e1d0", "executorAddress": "0x0052e1d0", "datatypeSlot": "+0x08", "stackEffect": "pop2-dispatch-push1"},
    {"opcode": 0x03, "label": "MULTIPLY", "vtable": "0x005e4d10", "executor": "CInstructionOP_MULTIPLY__VFunc_00_0052e220", "executorAddress": "0x0052e220", "datatypeSlot": "+0x0c", "stackEffect": "pop2-dispatch-push1"},
    {"opcode": 0x04, "label": "DIVIDE", "vtable": "0x005e4d00", "executor": "CInstructionOP_DIVIDE__VFunc_00_0052e270", "executorAddress": "0x0052e270", "datatypeSlot": "+0x10", "stackEffect": "pop2-dispatch-push1"},
    {"opcode": 0x05, "label": "PUSH", "vtable": "0x005e4cf0", "executor": "CInstructionOP_PUSH__VFunc_00_0052e2c0", "executorAddress": "0x0052e2c0", "stackEffect": "push attribute datatype"},
    {"opcode": 0x06, "label": "UNPROMOTED_06", "vtable": "0x005e4ce0", "executor": None, "status": "vtable-pointer-observed-no-function-at-pointer"},
    {"opcode": 0x07, "label": "OR", "vtable": "0x005e4cd0", "executor": "CAsmInstruction__ExecuteOr", "executorAddress": "0x0052e4d0", "stackEffect": "pop2-bool-or-push1"},
    {"opcode": 0x08, "label": "AND", "vtable": "0x005e4cc0", "executor": "CAsmInstruction__ExecuteAnd", "executorAddress": "0x0052e580", "stackEffect": "pop2-bool-and-push1"},
    {"opcode": 0x09, "label": "GREATER_THAN", "vtable": "0x005e4cb0", "executor": "CAsmInstruction__ExecuteGreaterThan", "executorAddress": "0x0052e630", "datatypeSlot": "+0x24", "stackEffect": "pop2-compare-push-bool"},
    {"opcode": 0x0A, "label": "LESS_THAN", "vtable": "0x005e4ca0", "executor": "CAsmInstruction__ExecuteLessThan", "executorAddress": "0x0052e6d0", "datatypeSlot": "+0x20", "stackEffect": "pop2-compare-push-bool"},
    {"opcode": 0x0B, "label": "GREATER_OR_EQUAL", "vtable": "0x005e4c90", "executor": "CAsmInstruction__ExecuteGreaterOrEqual", "executorAddress": "0x0052e770", "datatypeSlot": "+0x2c", "stackEffect": "pop2-compare-push-bool"},
    {"opcode": 0x0C, "label": "LESS_OR_EQUAL", "vtable": "0x005e4c80", "executor": "CAsmInstruction__ExecuteLessOrEqual", "executorAddress": "0x0052e810", "datatypeSlot": "+0x28", "stackEffect": "pop2-compare-push-bool"},
    {"opcode": 0x0D, "label": "NOOP_0D", "vtable": "0x005e4c70", "executor": "SharedVFunc__NoOp_Ret0C", "executorAddress": "0x00453ac0", "status": "observed-shared-noop"},
    {"opcode": 0x0E, "label": "UNPROMOTED_0E", "vtable": "0x005e4c60", "executor": None, "status": "vtable-pointer-observed-no-function-at-pointer"},
    {"opcode": 0x0F, "label": "CMP", "vtable": "0x005e4c50", "executor": "CInstructionOP_CMP__VFunc_00_0052e330", "executorAddress": "0x0052e330", "datatypeSlot": "+0x18", "stackEffect": "peek2-set-script_state+0x218"},
    {"opcode": 0x10, "label": "COMPARE_EQUAL", "vtable": "0x005e4c40", "executor": "CAsmInstruction__ExecuteCompareEqual", "executorAddress": "0x0052e380", "datatypeSlot": "+0x18", "stackEffect": "pop2-compare-push-bool"},
    {"opcode": 0x11, "label": "COMPARE_NOT_EQUAL", "vtable": "0x005e4c30", "executor": "CAsmInstruction__ExecuteCompareNotEqual", "executorAddress": "0x0052e8b0", "datatypeSlot": "+0x1c", "stackEffect": "pop2-compare-push-bool"},
    {"opcode": 0x12, "label": "UNPROMOTED_12", "vtable": "0x005e4c20", "executor": None, "status": "vtable-pointer-observed-no-function-at-pointer"},
    {"opcode": 0x13, "label": "JMPFALSE", "vtable": "0x005e4c10", "executor": "CInstructionOP_JMPFALSE__VFunc_00_0052e950", "executorAddress": "0x0052e950", "stackEffect": "pop1-branch-if-false"},
    {"opcode": 0x14, "label": "UNPROMOTED_14", "vtable": "0x005e4c00", "executor": None, "status": "vtable-pointer-observed-no-function-at-pointer"},
    {"opcode": 0x15, "label": "UNPROMOTED_15", "vtable": "0x005e4bf0", "executor": None, "status": "vtable-pointer-observed-no-function-at-pointer"},
    {"opcode": 0x16, "label": "UNPROMOTED_16", "vtable": "0x005e4be0", "executor": None, "status": "vtable-pointer-observed-no-function-at-pointer"},
    {"opcode": 0x17, "label": "POP_OR_STOP", "vtable": "0x005e4bd0", "executor": "CAsmInstruction__ExecutePop", "executorAddress": "0x0052e0f0", "stackEffect": "pop1-set-ip/status; VM loop also treats opcode 0x17 as stop candidate"},
    {"opcode": 0x18, "label": "CALL", "vtable": "0x005e4bc0", "executor": "CAsmInstruction__ExecuteCall", "executorAddress": "0x0052ea40", "stackEffect": "pop arguments-dispatch-descriptor-push result"},
    {"opcode": 0x19, "label": "UNPROMOTED_19", "vtable": "0x005e4bb0", "executor": None, "status": "vtable-pointer-observed-no-function-at-pointer"},
    {"opcode": 0x1A, "label": "UNPROMOTED_1A", "vtable": "0x005e4ba0", "executor": None, "status": "vtable-pointer-observed-no-function-at-pointer"},
]

DATATYPES: list[dict[str, Any]] = [
    {"typeId": 1, "label": "int", "className": "CIntDataType", "vtable": "0x005e4af8", "sizeBytes": 8, "payloadReads": ["+0x04 dword"], "observedValueGetterSlot": "+0x30"},
    {"typeId": 2, "label": "float", "className": "CFloatDataType", "vtable": "0x005e4ea4", "sizeBytes": 8, "payloadReads": ["+0x04 dword/float"], "observedValueGetterSlot": "+0x34"},
    {"typeId": 3, "label": "string", "className": "CStringDataType", "vtable": "0x005e4e4c", "sizeBytes": 8, "payloadReads": ["length dword", "heap string copy plus NUL"], "observedValueGetterSlot": "+0x38"},
    {"typeId": 4, "label": "bool", "className": "CBoolDataType", "vtable": "0x005e4d50", "sizeBytes": 8, "payloadReads": ["+0x04 dword/byte-like bool"], "observedValueGetterSlot": "+0x3c"},
    {"typeId": 5, "label": "thing-ptr", "className": "CThingPtrDataType", "vtable": "0x005e4df8", "sizeBytes": 8, "payloadReads": ["serialized token read into local; stored pointer zeroed"], "observedValueGetterSlot": "+0x40", "openBoundary": "exact serialized thing-pointer token semantics remain unproven"},
    {"typeId": 6, "label": "position", "className": "CPositionDataType", "vtable": "0x005e4da4", "sizeBytes": 20, "payloadReads": ["+0x04 float", "+0x08 float", "+0x0c float"], "observedValueGetterSlot": "+0x44", "openBoundary": "+0x10 field role remains unproven"},
]

VM_STATE_OFFSETS: list[dict[str, str]] = [
    {"owner": "runtime_state", "offset": "+0x08", "role": "active script/object-code context pointer source"},
    {"owner": "runtime_state", "offset": "+0x0c", "role": "data-stack base passed to opcode executors"},
    {"owner": "runtime_state", "offset": "+0x20c", "role": "data-stack count"},
    {"owner": "runtime_state", "offset": "+0x210", "role": "running/recursive-run guard"},
    {"owner": "runtime_state", "offset": "+0x214", "role": "instruction pointer"},
    {"owner": "runtime_state", "offset": "+0x218", "role": "flags field modified by CMP"},
    {"owner": "runtime_state", "offset": "+0x21c", "role": "expected/saved stack size checked at run end"},
    {"owner": "runtime_state", "offset": "+0x220", "role": "abort flag set by instruction-limit path"},
    {"owner": "runtime_state", "offset": "+0x224", "role": "call-depth / stop gating counter"},
    {"owner": "script_object_code", "offset": "+0x04", "role": "instruction pointer array source in Run"},
    {"owner": "script_object_code", "offset": "+0x58", "role": "context argument passed to opcode executor slot 0"},
    {"owner": "script_object_code", "offset": "+0x60", "role": "debug trace flag checked by Run"},
    {"owner": "script_object_code", "offset": "+0x68", "role": "IScript back-pointer written by IScript constructor"},
]


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def evidence_counts() -> dict[str, int]:
    return {
        "wave573MetadataRows": len(read_tsv(WAVE573 / "post_metadata.tsv")),
        "wave574MetadataRows": len(read_tsv(WAVE574 / "post_metadata.tsv")),
        "wave574DispatchSlotRows": len(read_tsv(WAVE574 / "post_dispatch_table_slots.tsv")),
        "wave575MetadataRows": len(read_tsv(WAVE575 / "post_metadata.tsv")),
        "wave575DatatypeVtableRows": len(read_tsv(WAVE575 / "post_datatype_vtables.tsv")),
        "wave587MetadataRows": len(read_tsv(WAVE587 / "post" / "metadata.tsv")),
        "wave587VtableRows": len(read_tsv(WAVE587 / "post" / "vtables.tsv")),
        "wave1189MetadataRows": len(read_tsv(WAVE1189 / "post-metadata.tsv")),
    }


def build_schema() -> dict[str, Any]:
    counts = evidence_counts()
    proven = [row for row in OPCODES if row.get("executor")]
    unpromoted = [row for row in OPCODES if not row.get("executor")]
    return {
        "schemaVersion": "missionscript-vm-datatype-opcode-schema.v1",
        "status": "PASS",
        "source": {
            "evidenceWaves": ["Wave573", "Wave574", "Wave575", "Wave587", "Wave1189"],
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static clean-room interpreter planning, not runtime proof",
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackup": BACKUP,
        },
        "evidenceCounts": counts,
        "opcodeFactory": {
            "function": "0x0052d3d0 CAsmInstruction__SpawnFromOpcode",
            "serializedOpcodeRange": "0x00..0x1a",
            "declaredOpcodeCases": len(OPCODES),
            "instructionAllocationBytes": 12,
            "attributeRead": "second dword from bytecode_reader stored at instruction+0x04",
            "unknownOpcodeBehavior": "prints fatal unknown-instruction diagnostic and returns null",
            "provenExecutorCases": len(proven),
            "unpromotedCases": len(unpromoted),
        },
        "opcodeCases": OPCODES,
        "datatypeFactory": {
            "function": "0x0052ec60 CDataType__CreateFromType",
            "serializedTypeRange": "1..6",
            "declaredTypeCases": len(DATATYPES),
            "unknownTypeBehavior": "prints fatal unknown-data-type diagnostic and returns null",
        },
        "datatypeCases": DATATYPES,
        "vmRunLoop": {
            "function": "0x00539b00 CScriptObjectCode__Run",
            "dispatchShape": "instruction vtable slot 0 called with runtime_state, runtime_state+0x0c data stack, and script_object_code+0x58 context argument",
            "opcodeGetterShape": "instruction vtable slot +0x08 returns opcode for loop stop checks",
            "stopOpcode": "0x17 when call-depth at runtime_state+0x224 is <= 0",
            "instructionLimit": 10000,
            "stateOffsets": VM_STATE_OFFSETS,
        },
        "callDescriptorBridge": {
            "function": "0x0052ea40 CAsmInstruction__ExecuteCall",
            "descriptorTable": "0x0064ce50",
            "descriptorStrideBytes": 64,
            "schemaDependency": "missionscript-command-descriptor-schema.v1.json",
            "instructionFields": [
                "this+0x04 low byte indexes the descriptor table",
                "this+0x04 high bits participate in return-value expectation checks",
                "this+0x05 carries the observed argument count",
            ],
            "scratchArray": "0x0089c300 argument scratch array",
            "notClaimed": "exact descriptor field layout, exact arity, and runtime command effects",
        },
        "claims": [
            "The saved opcode factory has 27 serialized opcode cases, 0x00 through 0x1a.",
            "The saved datatype factory has 6 serialized datatype cases, 1 through 6.",
            "The saved VM run loop dispatches instruction vtable slot 0 and observes opcode 0x17 as the stop candidate when call depth is not positive.",
            "The saved CALL executor bridges opcode execution to the 0x0064ce50 command descriptor table and the 0x0089c300 scratch argument array.",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime command effects",
            "runtime opcode behavior",
            "exact VM layout",
            "exact datatype layout",
            "exact opcode layout",
            "exact instruction object layout",
            "exact descriptor field layout",
            "exact source identity",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
    }


def check_evidence_tokens(failures: list[str]) -> None:
    spawn = read_text(SPAWN_DECOMPILE)
    datatype = read_text(DATATYPE_DECOMPILE)
    run = read_text(RUN_DECOMPILE)
    call = read_text(CALL_DECOMPILE)

    for token in ("case 0x1a", "PTR_CAsmInstruction__ExecuteCall_005e4bc0", "s_FATAL_ERROR__uknown_instruction_i_0064cab8"):
        require(token in spawn, f"SpawnFromOpcode decompile missing token: {token}", failures)
    for token in ("case 6", "PTR_CDataType__ScalarDeletingDestructor_005e4da4", "s_FATAL_ERROR__unknown_data_type_t_0064cc58"):
        require(token in datatype, f"CreateFromType decompile missing token: {token}", failures)
    for token in ("0x210", "0x218", "0x224", "10000", "CScriptObjectCode__RemoveTop"):
        require(token in run, f"Run decompile missing token: {token}", failures)
    for token in ("0x0089c300", "DAT_0064ce58", "DAT_0064ce5c", "&DAT_0064ce50", "this + 5"):
        require(token in call, f"ExecuteCall decompile missing token: {token}", failures)


def check_schema(failures: list[str]) -> None:
    expected = build_schema()
    stored = read_json(SCHEMA)
    require(stored == expected, "VM/datatype/opcode schema does not match rebuilt static evidence", failures)
    require(read_json(LORE_SCHEMA) == stored, "lore VM/datatype/opcode schema mirror mismatch", failures)

    require(stored["opcodeFactory"]["declaredOpcodeCases"] == 27, "opcode case count mismatch", failures)
    require(stored["opcodeFactory"]["provenExecutorCases"] == 19, "proven executor case count mismatch", failures)
    require(stored["opcodeFactory"]["unpromotedCases"] == 8, "unpromoted opcode count mismatch", failures)
    require(stored["datatypeFactory"]["declaredTypeCases"] == 6, "datatype case count mismatch", failures)
    require(stored["vmRunLoop"]["stopOpcode"].startswith("0x17"), "stop opcode mismatch", failures)
    require(stored["callDescriptorBridge"]["descriptorTable"] == "0x0064ce50", "descriptor bridge table mismatch", failures)
    require(stored["evidenceCounts"]["wave573MetadataRows"] == 14, "Wave573 metadata count mismatch", failures)
    require(stored["evidenceCounts"]["wave574MetadataRows"] == 15, "Wave574 metadata count mismatch", failures)
    require(stored["evidenceCounts"]["wave575MetadataRows"] == 12, "Wave575 metadata count mismatch", failures)
    require(stored["evidenceCounts"]["wave587MetadataRows"] == 22, "Wave587 metadata count mismatch", failures)
    require(stored["evidenceCounts"]["wave1189MetadataRows"] == 7, "Wave1189 metadata count mismatch", failures)

    serialized = json.dumps(stored, sort_keys=True)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in serialized, f"schema leaks forbidden token: {token}", failures)


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)
    proof_tokens = (
        "MissionScript VM / Datatype / Opcode Schema Proof",
        "Status: static VM/datatype/opcode schema proof complete, not runtime proof",
        SCHEMA_LINK,
        "CAsmInstruction__SpawnFromOpcode",
        "CDataType__CreateFromType",
        "CScriptObjectCode__Run",
        "CAsmInstruction__ExecuteCall",
        "0x0052d3d0",
        "0x0052ec60",
        "0x00539b00",
        "0x0052ea40",
        "27",
        "0x00..0x1a",
        "6",
        "1..6",
        "0x17",
        "0x0064ce50",
        "0x0089c300",
        "script_state+0x218",
        "script_object_code+0x68",
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
        ASM_DOC,
        DATATYPE_DOC,
        SCRIPT_OBJECT_DOC,
        ISCRIPT_DOC,
    )
    for path in linked_paths:
        text = read_text(path)
        require(PROOF_LINK in text, f"{path.relative_to(ROOT)} missing proof link", failures)
        require(SCHEMA_LINK in text, f"{path.relative_to(ROOT)} missing schema link", failures)

    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "transition backlog lore mirror mismatch", failures)
    require(read_text(MAPPED) == read_text(LORE_MAPPED), "mapped systems lore mirror mismatch", failures)
    require(read_text(BIN_INDEX) == read_text(LORE_BIN_INDEX), "binary index lore mirror mismatch", failures)
    require(read_text(RE_INDEX) == read_text(LORE_RE_INDEX), "RE index lore mirror mismatch", failures)


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
        scripts.get("test:missionscript-vm-datatype-opcode-schema")
        == r"py -3 tools\missionscript_vm_datatype_opcode_schema_probe.py --check",
        "missing package VM/datatype/opcode schema script",
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
    check_evidence_tokens(failures)
    check_schema(failures)
    check_docs(failures)
    check_progress_and_package(failures)

    if failures:
        print("MissionScript VM/datatype/opcode schema probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript VM/datatype/opcode schema probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
