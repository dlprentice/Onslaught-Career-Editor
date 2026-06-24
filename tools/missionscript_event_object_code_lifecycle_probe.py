#!/usr/bin/env python3
"""Validate the MissionScript event/object-code lifecycle static schema."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle-proof.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_event_object_code_lifecycle_2026-06-08.md"
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
SCRIPT_OBJECT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ScriptObjectCode.cpp.md"
SCRIPT_EVENT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ScriptEventNB.cpp.md"
EVENT_FUNCTION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "EventFunction.cpp.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
EVENTS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "mission-events-index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

WAVE546 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave546-cmission-script-free-object-004f7440"
WAVE577 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave577-eventfunction-tail-0052f9a0"
WAVE585 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave585-iscript-level-event-00537fd0"
WAVE586 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave586-scripteventnb-core-00538470"
WAVE587 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave587-scriptobjectcode-core-00538ea0"
WAVE588 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave588-cmission-script-object-code-00539c80"
WAVE926 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave926-iscript-lifecycle-review"
WAVE1189 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1189-missionscript-bytecode-iscript-current-risk-review"

EVENT_EXECUTE_DECOMPILE = WAVE577 / "post_decompile" / "0052fda0_CEventFunction__Execute.c"
SCHEDULE_EVENT_DECOMPILE = WAVE585 / "post" / "decompile" / "005383c0_IScript__ScheduleEvent.c"
POST_EVENT_DECOMPILE = WAVE586 / "post" / "decompile" / "00538b70_CScriptEventNB__PostEvent.c"
CALL_EVENT_DECOMPILE = WAVE587 / "post" / "decompile" / "00539990_CScriptObjectCode__CallEvent.c"
CALL_EVENT_DIRECT_DECOMPILE = WAVE587 / "post" / "decompile" / "00539a60_CScriptObjectCode__CallEventDirect.c"
LOAD_ASYNC_DECOMPILE = WAVE588 / "post" / "decompile" / "00539ca0_CMissionScriptObjectCode__LoadAsync.c"
START_LOAD_ASYNC_DECOMPILE = WAVE588 / "post" / "decompile" / "00539dc0_CMissionScriptObjectCode__StartLoadAsync.c"
CLEAR_FIELDS_DECOMPILE = WAVE588 / "post" / "decompile" / "00539f40_CMissionScriptObjectCode__ClearFields.c"
FREE_OBJECT_DECOMPILE = WAVE546 / "post_decomp" / "004f7440_CMissionScriptObjectCode__FreeObjectIfPresent.c"
ISCRIPT_CTOR_DECOMPILE = WAVE926 / "decompile" / "005333b0_IScript__Constructor.c"
ISCRIPT_DTOR_DECOMPILE = WAVE926 / "decompile" / "00533450_IScript__Destructor.c"

BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
PROOF_LINK = "missionscript-event-object-code-lifecycle-proof.md"
SCHEMA_LINK = "missionscript-event-object-code-lifecycle.v1.json"

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
    "runtime event outcomes proven",
    "runtime command effects proven",
    "runtime opcode behavior proven",
    "live loose-msl loading proven",
    "exact event payload layout proven",
    "exact listener layout proven",
    "exact object-code layout proven",
    "exact async-cache layout proven",
    "exact source identity proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)

LIFECYCLE_STEPS: list[dict[str, Any]] = [
    {
        "step": "script-owner-link",
        "function": "0x005333b0 IScript__Constructor",
        "evidence": "stores owner/script pointers, writes IScript back-pointer at script_object_code+0x68, initializes listener/state set at this+0x28",
        "boundary": "exact IScript concrete layout and runtime script startup behavior remain unproven",
    },
    {
        "step": "post-event-command-payload",
        "function": "0x005383c0 IScript__ScheduleEvent",
        "evidence": "registered PostEvent handler allocates a 0x0c-byte payload, reads the event name/reference through datatype getter +0x48, links through DAT_00855190, and schedules CEventManager__AddEvent_AtTime(...,2000,&DAT_0089c590,-1.0,0,payload,0)",
        "boundary": "exact event payload layout and runtime scheduler timing remain unproven",
    },
    {
        "step": "listener-registration",
        "function": "0x00538960 CScriptEventNB__RegisterEventListener",
        "evidence": "matches listener names with datatype/string vtable getter +0x38, allocates listener/function wrapper nodes, and stores CEventFunction references in listener lists",
        "boundary": "exact listener node layout and string lifetime remain unproven",
    },
    {
        "step": "listener-post-dispatch",
        "function": "0x00538b70 CScriptEventNB__PostEvent",
        "evidence": "warns when no listener is available unless event_name is game playing, matches event names, marks matching listener entries, and calls CEventFunction__Execute",
        "boundary": "runtime posted-event delivery and mission outcome behavior remain unproven",
    },
    {
        "step": "event-function-dispatch",
        "function": "0x0052fda0 CEventFunction__Execute",
        "evidence": "walks event parameter wrappers, stages up to the observed local 10-slot array, and calls CScriptObjectCode__CallEventDirect",
        "boundary": "exact parameter payload semantics and parameter-count safety remain unproven",
    },
    {
        "step": "object-code-event-call",
        "function": "0x00539990 CScriptObjectCode__CallEvent",
        "evidence": "looks up event instruction pointers from script_object_code+0x14+event_index*4, pushes parameters when present, and calls CScriptObjectCode__Run",
        "boundary": "exact event table layout and runtime VM behavior remain unproven",
    },
    {
        "step": "object-code-direct-call",
        "function": "0x00539a60 CScriptObjectCode__CallEventDirect",
        "evidence": "pushes supplied parameters, writes runtime_state+0x214 with the direct instruction index, and calls CScriptObjectCode__Run",
        "boundary": "exact event-function parameter ownership remains unproven",
    },
    {
        "step": "async-object-code-load",
        "function": "0x00539dc0 CMissionScriptObjectCode__StartLoadAsync / 0x00539ca0 CMissionScriptObjectCode__LoadAsync",
        "evidence": "waits for the existing worker, copies filename to this+0x20, stores buffer_size at this+0x124, starts the worker, then LoadAsync creates a CDXMemBuffer and initializes it from the stored path",
        "boundary": "exact async-cache ownership and live script-loading behavior remain unproven",
    },
    {
        "step": "object-code-field-teardown",
        "function": "0x00539f40 CMissionScriptObjectCode__ClearFields / 0x004f7440 CMissionScriptObjectCode__FreeObjectIfPresent",
        "evidence": "clears the HUD/object-code field block, frees object-code pointer slots through the memory manager, releases auxiliary slots, and nulls fields as they are released",
        "boundary": "exact HUD field-block and object-code-record layouts remain unproven",
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def evidence_counts() -> dict[str, int]:
    return {
        "wave546MetadataRows": len(read_tsv(WAVE546 / "post_metadata.tsv")),
        "wave546InstructionRows": len(read_tsv(WAVE546 / "post_instructions.tsv")),
        "wave546DecompileRows": len(read_tsv(WAVE546 / "post_decomp" / "index.tsv")),
        "wave577MetadataRows": len(read_tsv(WAVE577 / "post_metadata.tsv")),
        "wave577XrefRows": len(read_tsv(WAVE577 / "post_xrefs.tsv")),
        "wave577InstructionRows": len(read_tsv(WAVE577 / "post_target_instructions.tsv")),
        "wave577DecompileRows": len(read_tsv(WAVE577 / "post_decompile" / "index.tsv")),
        "wave577VtableRows": len(read_tsv(WAVE577 / "post_vtables.tsv")),
        "wave585MetadataRows": len(read_tsv(WAVE585 / "post" / "metadata.tsv")),
        "wave585XrefRows": len(read_tsv(WAVE585 / "post" / "xrefs.tsv")),
        "wave585InstructionRows": len(read_tsv(WAVE585 / "post" / "instructions.tsv")),
        "wave585DecompileRows": len(read_tsv(WAVE585 / "post" / "decompile" / "index.tsv")),
        "wave586MetadataRows": len(read_tsv(WAVE586 / "post" / "metadata.tsv")),
        "wave586XrefRows": len(read_tsv(WAVE586 / "post" / "xrefs.tsv")),
        "wave586InstructionRows": len(read_tsv(WAVE586 / "post" / "instructions.tsv")),
        "wave586DecompileRows": len(read_tsv(WAVE586 / "post" / "decompile" / "index.tsv")),
        "wave586VtableRows": len(read_tsv(WAVE586 / "post" / "vtables.tsv")),
        "wave587MetadataRows": len(read_tsv(WAVE587 / "post" / "metadata.tsv")),
        "wave587XrefRows": len(read_tsv(WAVE587 / "post" / "xrefs.tsv")),
        "wave587InstructionRows": len(read_tsv(WAVE587 / "post" / "instructions.tsv")),
        "wave587DecompileRows": len(read_tsv(WAVE587 / "post" / "decompile" / "index.tsv")),
        "wave587VtableRows": len(read_tsv(WAVE587 / "post" / "vtables.tsv")),
        "wave588MetadataRows": len(read_tsv(WAVE588 / "post" / "metadata.tsv")),
        "wave588XrefRows": len(read_tsv(WAVE588 / "post" / "xrefs.tsv")),
        "wave588InstructionRows": len(read_tsv(WAVE588 / "post" / "instructions.tsv")),
        "wave588DecompileRows": len(read_tsv(WAVE588 / "post" / "decompile" / "index.tsv")),
        "wave588VtableRows": len(read_tsv(WAVE588 / "post" / "vtables.tsv")),
        "wave926MetadataRows": len(read_tsv(WAVE926 / "metadata.tsv")),
        "wave926XrefRows": len(read_tsv(WAVE926 / "xrefs.tsv")),
        "wave926InstructionRows": len(read_tsv(WAVE926 / "instructions.tsv")),
        "wave926DecompileRows": len(read_tsv(WAVE926 / "decompile" / "index.tsv")),
        "wave1189MetadataRows": len(read_tsv(WAVE1189 / "post-metadata.tsv")),
        "wave1189InstructionRows": len(read_tsv(WAVE1189 / "post-instructions.tsv")),
        "wave1189DecompileRows": len(read_tsv(WAVE1189 / "post-decompile" / "index.tsv")),
    }


def build_schema() -> dict[str, Any]:
    return {
        "schemaVersion": "missionscript-event-object-code-lifecycle.v1",
        "status": "PASS",
        "source": {
            "evidenceWaves": ["Wave546", "Wave577", "Wave585", "Wave586", "Wave587", "Wave588", "Wave926", "Wave1189"],
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static event/object-code lifecycle mapping for clean-room planning, not runtime proof",
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackup": BACKUP,
        },
        "familyCounts": {
            "CEventFunction": 5,
            "IScriptLevelEventHandlers": 5,
            "CScriptEventNB": 13,
            "CScriptObjectCode": 22,
            "CMissionScriptObjectCode": 6,
            "IScriptLifecycle": 2,
            "objectCodeCleanupHelper": 1,
        },
        "evidenceCounts": evidence_counts(),
        "lifecycleSteps": LIFECYCLE_STEPS,
        "corpusContext": {
            "levelRows": 95,
            "looseEventNameCounts": 795,
            "primaryCompleteCalls": 115,
            "secondaryCompleteCalls": 42,
            "primaryFailedCalls": 102,
            "levelWonCalls": 79,
            "levelLostCalls": 13,
            "source": "reverse-engineering/game-assets/mission-events-index.md",
            "boundary": "loose corpus evidence only until packed-vs-loose selection and live loading are proven",
        },
        "claims": [
            "The saved static event/object-code lifecycle has a bounded chain from IScript owner linkage through PostEvent scheduling, CScriptEventNB listener dispatch, CEventFunction execution, CScriptObjectCode event-call helpers, and CMissionScriptObjectCode async load/teardown helpers.",
            "The schema preserves lifecycle anchors and row counts from saved Ghidra exports without mutating Ghidra or executing BEA.",
            "The schema keeps exact event payload, listener, async-cache, object-code, VM, and source layouts outside the static claim.",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime event outcomes",
            "runtime command effects",
            "runtime opcode behavior",
            "live loose-MSL loading",
            "packed-resource script selection",
            "exact event payload layout",
            "exact listener layout",
            "exact object-code layout",
            "exact async-cache layout",
            "exact VM layout",
            "exact source identity",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
    }


def check_evidence_tokens(failures: list[str]) -> None:
    checks = {
        EVENT_EXECUTE_DECOMPILE: ("CScriptObjectCode__CallEventDirect", "local_28 [10]", "0x005e4d50", "EventFunction.cpp line 0x96"),
        SCHEDULE_EVENT_DECOMPILE: ("CEventManager__AddEvent_AtTime", "DAT_00855190", "2000", "s_PostEvent_0064f9e8"),
        POST_EVENT_DECOMPILE: ("CEventFunction__Execute", "s_Warning__No_listeners_for_posted_0064fecc", "game playing", "vtable getter +0x38"),
        CALL_EVENT_DECOMPILE: ("CScriptObjectCode__Run", "script_object_code+0x14+event_index*4", "s_FATAL_ERROR__stack_not_empty_on_c_00650160", "0x21c"),
        CALL_EVENT_DIRECT_DECOMPILE: ("CScriptObjectCode__Push", "CScriptObjectCode__Run", "0x214", "instruction_index"),
        LOAD_ASYNC_DECOMPILE: ("CDXMemBuffer__Close", "DXMemBuffer__SetBufferSize", "CDXMemBuffer__InitFromFile", "this+0x20", "this+0x124"),
        START_LOAD_ASYNC_DECOMPILE: ("CBinkOpenThread__WaitForThread", "CBinkOpenThread__StartAsync", "filename", "buffer_size", "this+0x124"),
        CLEAR_FIELDS_DECOMPILE: ("CMissionScriptObjectCode__FreeObjectIfPresent", "CDXMemoryManager__Free", "CHud__DecrementCounter9C", "field_block"),
        FREE_OBJECT_DECOMPILE: ("CMissionScriptObjectCode__FreeObjectIfPresent", "object-code record", "CDXMemoryManager__Free", "object_code"),
        ISCRIPT_CTOR_DECOMPILE: ("script_object_code+0x68", "0x005e4f08", "CSPtrSet__Init", "owner_complex_thing"),
        ISCRIPT_DTOR_DECOMPILE: ("CSPtrSet__Clear", "CMonitor__Shutdown", "this+0x28", "runtime mission-script teardown behavior"),
    }
    for path, tokens in checks.items():
        text = read_text(path)
        for token in tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing evidence token: {token}", failures)


def check_schema(failures: list[str]) -> None:
    expected = build_schema()
    stored = read_json(SCHEMA)
    require(stored == expected, "event/object-code lifecycle schema does not match rebuilt static evidence", failures)
    require(read_json(LORE_SCHEMA) == stored, "lore event/object-code lifecycle schema mirror mismatch", failures)

    counts = stored["evidenceCounts"]
    require(counts["wave577MetadataRows"] == 5, "Wave577 metadata count mismatch", failures)
    require(counts["wave585MetadataRows"] == 5, "Wave585 metadata count mismatch", failures)
    require(counts["wave586MetadataRows"] == 13, "Wave586 metadata count mismatch", failures)
    require(counts["wave587MetadataRows"] == 22, "Wave587 metadata count mismatch", failures)
    require(counts["wave588MetadataRows"] == 6, "Wave588 metadata count mismatch", failures)
    require(counts["wave926MetadataRows"] == 2, "Wave926 metadata count mismatch", failures)
    require(stored["familyCounts"]["CEventFunction"] == 5, "CEventFunction count mismatch", failures)
    require(stored["familyCounts"]["CScriptEventNB"] == 13, "CScriptEventNB count mismatch", failures)
    require(stored["familyCounts"]["CScriptObjectCode"] == 22, "CScriptObjectCode count mismatch", failures)
    require(stored["familyCounts"]["CMissionScriptObjectCode"] == 6, "CMissionScriptObjectCode count mismatch", failures)
    require(len(stored["lifecycleSteps"]) == 9, "lifecycle step count mismatch", failures)
    require(stored["corpusContext"]["looseEventNameCounts"] == 795, "loose event count mismatch", failures)

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
        "MissionScript Event / Object-Code Lifecycle Proof",
        "Status: static event/object-code lifecycle schema proof complete, not runtime proof",
        SCHEMA_LINK,
        "CEventFunction__Execute",
        "IScript__ScheduleEvent",
        "CScriptEventNB__PostEvent",
        "CScriptObjectCode__CallEvent",
        "CScriptObjectCode__CallEventDirect",
        "CMissionScriptObjectCode__StartLoadAsync",
        "CMissionScriptObjectCode__LoadAsync",
        "CMissionScriptObjectCode__ClearFields",
        "IScript__Constructor",
        "script_object_code+0x68",
        "DAT_00855190",
        "DAT_0089c590",
        "0x0064ce50",
        "795",
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
        SCRIPT_OBJECT_DOC,
        SCRIPT_EVENT_DOC,
        EVENT_FUNCTION_DOC,
        ISCRIPT_DOC,
        EVENTS_INDEX,
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
        scripts.get("test:missionscript-event-object-code-lifecycle")
        == r"py -3 tools\missionscript_event_object_code_lifecycle_probe.py --check",
        "missing package event/object-code lifecycle script",
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
        print("MissionScript event/object-code lifecycle probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript event/object-code lifecycle probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
