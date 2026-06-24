#!/usr/bin/env python3
"""Validate the MissionScript packed-vs-loose script-selection proof plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection-proof-plan.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "missionscript_packed_vs_loose_script_selection_proof_plan_2026-06-08.md"

CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
PROOF_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
LORE_PROOF_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
EVENT_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle-proof.md"
EVENT_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle.v1.json"
SCRIPT_OBJECT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ScriptObjectCode.cpp.md"
LORE_SCRIPT_OBJECT_DOC = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "ScriptObjectCode.cpp.md"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"

MSL_DOC = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
LORE_MSL_DOC = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "msl-scripting.md"
MISSION_INDEX = ROOT / "reverse-engineering" / "game-assets" / "mission-scripts-index.md"
LORE_MISSION_INDEX = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-scripts-index.md"
MISSION_EVENTS = ROOT / "reverse-engineering" / "game-assets" / "mission-events-index.md"
LORE_MISSION_EVENTS = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-events-index.md"

GOODIES_REPORT = ROOT / "subagents" / "goodies-script-corpus" / "current" / "goodies-script-corpus.json"
GOODIES_READINESS = ROOT / "release" / "readiness" / "goodies_packed_script_probe_2026-05-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

WAVE588 = ROOT / "subagents" / "ghidra-static-reaudit" / "wave588-cmission-script-object-code-00539c80"
LOAD_ASYNC_DECOMPILE = WAVE588 / "post" / "decompile" / "00539ca0_CMissionScriptObjectCode__LoadAsync.c"
START_LOAD_ASYNC_DECOMPILE = WAVE588 / "post" / "decompile" / "00539dc0_CMissionScriptObjectCode__StartLoadAsync.c"

BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
PROOF_LINK = "missionscript-packed-vs-loose-script-selection-proof-plan.md"
SCHEMA_LINK = "missionscript-packed-vs-loose-script-selection.v1.json"
NEXT_SLICE = "MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan"
BOUNDARY_SLICE = "Completed MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan"
BOUNDARY_PROOF_LINK = "missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md"
BOUNDARY_SCHEMA_LINK = "missionscript-level100-tutorial-runtime-harness-boundary.v1.json"
FOLLOWUP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Boundary Planning Proof Plan"

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
    "runtime event outcomes proven",
    "live loose-msl loading proven",
    "packed-vs-loose script selection proven",
    "packed scripts absent proven",
    "compiled bytecode equivalence proven",
    "exact object-code layout proven",
    "exact async-cache layout proven",
    "exact source identity proven",
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


def build_schema() -> dict[str, Any]:
    goodies = read_json(GOODIES_REPORT)
    packed = goodies["packedResourceScan"]
    events = read_json(EVENT_SCHEMA)
    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]

    return {
        "schemaVersion": "missionscript-packed-vs-loose-script-selection.v1",
        "status": "PASS",
        "source": {
            "runtimeExecution": False,
            "ghidraMutation": False,
            "schemaPurpose": "static proof plan for separating loose MissionScript corpus evidence, packed-resource literal scan evidence, and object-code load anchors before runtime selection proof",
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackup": BACKUP,
        },
        "looseCorpusEvidence": {
            "sourceDocs": [
                "reverse-engineering/game-assets/mission-scripts-index.md",
                "reverse-engineering/game-assets/mission-events-index.md",
                "reverse-engineering/game-assets/mission-slot-usage.md",
                "reverse-engineering/game-assets/mission-thing-usage.md",
                "reverse-engineering/game-assets/mission-message-usage.md",
            ],
            "scriptFileCount": goodies["scriptFileCount"],
            "goodieStateCallCount": goodies["callCount"],
            "goodieStateCallCounts": goodies["callCounts"],
            "targetScriptIndices": goodies["targetScriptIndices"],
            "targetHitCount": goodies["targetHitCount"],
            "levelRows": events["corpusContext"]["levelRows"],
            "looseEventNameCounts": events["corpusContext"]["looseEventNameCounts"],
            "primaryCompleteCalls": events["corpusContext"]["primaryCompleteCalls"],
            "secondaryCompleteCalls": events["corpusContext"]["secondaryCompleteCalls"],
            "primaryFailedCalls": events["corpusContext"]["primaryFailedCalls"],
            "levelWonCalls": events["corpusContext"]["levelWonCalls"],
            "levelLostCalls": events["corpusContext"]["levelLostCalls"],
            "exampleLevelScriptCounts": {
                "level100": 25,
                "level500": 24,
                "level741": 17,
                "level742": 19,
            },
            "boundary": "loose corpus/reference evidence only until copied/app-owned proof establishes live loading or selection",
        },
        "packedResourceLiteralScanEvidence": {
            "source": "subagents/goodies-script-corpus/current/goodies-script-corpus.json",
            "readinessNote": "release/readiness/goodies_packed_script_probe_2026-05-07.md",
            "archiveCount": packed["archiveCount"],
            "inflateErrorCount": packed["inflateErrorCount"],
            "tokenFileCount": packed["tokenFileCount"],
            "callCount": packed["callCount"],
            "targetHitCount": packed["targetHitCount"],
            "boundary": "top-level inflated AYA archive literal Goodie API/token scan only; not a compiled bytecode, indirect script, runtime-generated script, or general packed-vs-loose selection proof",
        },
        "objectCodeLoadAnchors": [
            {
                "function": "0x00539dc0 CMissionScriptObjectCode__StartLoadAsync",
                "evidence": "waits for the current worker, copies filename into this+0x20, stores buffer_size at this+0x124, then calls CBinkOpenThread__StartAsync",
                "boundary": "path-buffer async start anchor only; not proof of source selection, precedence, or runtime loaded path",
            },
            {
                "function": "0x00539ca0 CMissionScriptObjectCode__LoadAsync",
                "evidence": "closes prior buffer at this+0x1c, allocates CDXMemBuffer, sets buffer size from this+0x124, calls CDXMemBuffer__InitFromFile on this+0x20, and clears the first path byte",
                "boundary": "path-buffer load anchor only; not proof of loose file selection, packed fallback, or runtime MissionScript execution",
            },
            {
                "function": "0x00539f40 CMissionScriptObjectCode__ClearFields / 0x004f7440 CMissionScriptObjectCode__FreeObjectIfPresent",
                "evidence": "clears object-code/HUD field-block pointers and frees object-code record slots",
                "boundary": "static teardown anchor only; exact layouts and runtime lifetime remain unproven",
            },
        ],
        "lifecycleDependencies": {
            "schema": "missionscript-event-object-code-lifecycle.v1.json",
            "anchors": [
                "IScript__Constructor",
                "IScript__ScheduleEvent",
                "CScriptEventNB__PostEvent",
                "CEventFunction__Execute",
                "CScriptObjectCode__CallEvent",
                "CScriptObjectCode__CallEventDirect",
                "CScriptObjectCode__Run",
                "CMissionScriptObjectCode__LoadAsync",
                "script_object_code+0x68",
                "DAT_00855190",
                "DAT_0089c590",
            ],
            "boundary": "static event/object-code lifecycle accounting only; no runtime event dispatch, live mission, or loaded script-source claim",
        },
        "requiredFutureProofLanes": [
            "copied/app-owned MissionScripts corpus inventory with casing/path preservation",
            "copied/app-owned resource archive inventory for the selected mission/resource set",
            "static path-argument/xref map around CMissionScriptObjectCode__StartLoadAsync callsites",
            "copied-profile runtime observation only after the selected static lane defines expected artifacts and stop conditions",
        ],
        "stopConditions": [
            "installed-game or original executable mutation would be required",
            "private raw assets or private paths would be exposed to public artifacts",
            "selection precedence is ambiguous from static evidence",
            "proof would require live mission execution before copied/app-owned guardrails exist",
            "packed-resource scan is being treated as compiled-bytecode equivalence",
            "exact object-code, async-cache, or source-body identity would be needed for the claim",
        ],
        "claims": [
            "A public-safe static plan now separates loose MissionScript corpus evidence, narrow packed-resource literal scan evidence, object-code load anchors, and future copied/app-owned runtime selection proof requirements.",
            "The checked loose corpus and top-level inflated packed-resource Goodie token scan are usable bounded inputs for planning, but neither is a runtime selection proof.",
            "The saved Ghidra load anchors prove a path-buffer async load shape, not which script source the retail game selects at runtime.",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime command effects",
            "runtime event outcomes",
            "live loose-MSL loading",
            "packed-vs-loose script selection",
            "compiled bytecode equivalence",
            "all packed scripts absent",
            "exact object-code layout",
            "exact async-cache layout",
            "exact source identity",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
        "nextStaticSlice": FOLLOWUP_SLICE,
        "progressCheck": {
            "focusedReviewed": current["focusedReviewed"],
            "remainingFocusedAfterLatestReview": current["remainingFocusedAfterLatestReview"],
            "liveFocusedCandidatesAfterLatestReview": current["liveFocusedCandidatesAfterLatestReview"],
            "isWave911Reconstruction": current["isWave911Reconstruction"],
        },
    }


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def check_no_overclaims(path: Path, failures: list[str]) -> None:
    lower = read_text(path).lower()
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def check_evidence_tokens(failures: list[str]) -> None:
    load = read_text(LOAD_ASYNC_DECOMPILE)
    for token in (
        "CDXMemBuffer__InitFromFile",
        "this+0x20",
        "this+0x124",
        "this+0x1c",
        "*filename = '\\0'",
        "runtime file-load behavior",
    ):
        require(token in load, f"LoadAsync decompile missing token: {token}", failures)

    start = read_text(START_LOAD_ASYNC_DECOMPILE)
    for token in (
        "CBinkOpenThread__WaitForThread",
        "CBinkOpenThread__StartAsync",
        "filename",
        "buffer_size",
        "this+0x124",
        "runtime Goodie/script loading",
    ):
        require(token in start, f"StartLoadAsync decompile missing token: {token}", failures)

    report = read_json(GOODIES_REPORT)
    packed = report["packedResourceScan"]
    require(report["schema"] == "goodies-script-corpus.v2", "Goodies corpus schema mismatch", failures)
    require(report["scriptFileCount"] == 733, "Goodies corpus loose script count mismatch", failures)
    require(report["callCount"] == 32, "Goodies corpus call count mismatch", failures)
    require(packed["archiveCount"] == 301, "packed archive count mismatch", failures)
    require(packed["inflateErrorCount"] == 0, "packed inflate error count mismatch", failures)
    require(packed["tokenFileCount"] == 0, "packed token file count mismatch", failures)
    require(packed["callCount"] == 0, "packed call count mismatch", failures)


def check_schema(failures: list[str]) -> None:
    expected = build_schema()
    stored = read_json(SCHEMA)
    require(stored == expected, "packed-vs-loose schema is not regenerated from current evidence", failures)
    require(read_json(LORE_SCHEMA) == stored, "lore packed-vs-loose schema mirror mismatch", failures)
    serialized = json.dumps(stored, sort_keys=True)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in serialized, f"schema leaks public-forbidden token: {token}", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore packed-vs-loose proof mirror mismatch", failures)

    core_tokens = (
        "MissionScript Packed-vs-Loose Script Selection Proof Plan",
        "Status: static proof plan complete, not runtime proof",
        PROOF_LINK,
        SCHEMA_LINK,
        "733",
        "32",
        "301",
        "0` inflate errors",
        "0` literal Goodie API/token hits",
        "95",
        "795",
        "0x00539dc0 CMissionScriptObjectCode__StartLoadAsync",
        "0x00539ca0 CMissionScriptObjectCode__LoadAsync",
        "this+0x20",
        "this+0x124",
        "CDXMemBuffer__InitFromFile",
        "script_object_code+0x68",
        "DAT_00855190",
        "DAT_0089c590",
        "loose corpus/reference evidence only",
        "top-level inflated AYA archive literal Goodie API/token scan only",
        "not runtime proof",
        BACKUP,
        NEXT_SLICE,
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_tokens(path, failures)

    linked_paths = (
        CONTRACT,
        PROOF_PLAN,
        EVENT_PROOF,
        SCRIPT_OBJECT_DOC,
        BACKLOG,
        MAPPED,
        BIN_INDEX,
        RE_INDEX,
        MSL_DOC,
        MISSION_INDEX,
        MISSION_EVENTS,
    )
    for path in linked_paths:
        text = read_text(path)
        require(PROOF_LINK in text, f"{path.relative_to(ROOT)} missing packed-vs-loose proof link", failures)
        require(SCHEMA_LINK in text, f"{path.relative_to(ROOT)} missing packed-vs-loose schema link", failures)
        check_no_overclaims(path, failures)

    for source, mirror in (
        (CONTRACT, LORE_CONTRACT),
        (PROOF_PLAN, LORE_PROOF_PLAN),
        (SCRIPT_OBJECT_DOC, LORE_SCRIPT_OBJECT_DOC),
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (MSL_DOC, LORE_MSL_DOC),
        (MISSION_INDEX, LORE_MISSION_INDEX),
        (MISSION_EVENTS, LORE_MISSION_EVENTS),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require("Completed MissionScript Packed-vs-Loose Script Selection Proof Plan" in backlog, "backlog missing completed packed-vs-loose slice", failures)
    require("Completed MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan" in backlog, "backlog missing completed text/speaker slice", failures)
    require(BOUNDARY_SLICE in backlog, "backlog missing completed runtime-harness boundary slice", failures)
    require(BOUNDARY_PROOF_LINK in backlog, "backlog missing runtime-harness boundary proof link", failures)
    require(BOUNDARY_SCHEMA_LINK in backlog, "backlog missing runtime-harness boundary schema link", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}" in backlog, "backlog missing copied-profile runtime-observation planning slice", failures)
    require("selected planning candidate, not runtime execution" in backlog, "backlog missing next active slice status", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}" not in backlog, "backlog still marks runtime-harness boundary active", failures)
    require("The selected active static-to-proof slice is MissionScript Packed-vs-Loose Script Selection Proof Plan" not in backlog, "backlog still marks packed-vs-loose as active", failures)
    require("The selected active static-to-proof slice is MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan" not in backlog, "backlog still marks text/speaker active", failures)

    mapped = read_text(MAPPED)
    require("Completed MissionScript Packed-vs-Loose Script Selection Proof Plan" in mapped, "mapped systems missing completed packed-vs-loose slice", failures)
    require("MissionScript Packed-vs-Loose Script Selection" in mapped, "mapped systems missing packed-vs-loose row label", failures)

    readiness = read_text(GOODIES_READINESS)
    require("archives=301" in readiness, "Goodies readiness missing packed archive count", failures)
    require("tokenFiles=0" in readiness, "Goodies readiness missing packed token count", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-packed-vs-loose-script-selection")
        == r"py -3 tools\missionscript_packed_vs_loose_script_selection_probe.py --check",
        "missing package packed-vs-loose script-selection test",
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
    check_package(failures)

    if failures:
        print("MissionScript packed-vs-loose script-selection probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript packed-vs-loose script-selection probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
