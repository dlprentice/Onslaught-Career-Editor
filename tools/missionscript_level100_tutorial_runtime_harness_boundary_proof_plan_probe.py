#!/usr/bin/env python3
"""Validate the MissionScript Level100 runtime-harness boundary proof plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-runtime-harness-boundary.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-runtime-harness-boundary.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_runtime_harness_boundary_proof_plan_2026-06-08.md"

WALKTHROUGH_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough-proof-plan.md"
LORE_WALKTHROUGH_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough-proof-plan.md"
WALKTHROUGH_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough.v1.json"
LORE_WALKTHROUGH_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough.v1.json"
TEXT_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md"
LORE_TEXT_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md"
TEXT_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution.v1.json"
LORE_TEXT_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution.v1.json"
PACKED_LOOSE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection-proof-plan.md"
LORE_PACKED_LOOSE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection-proof-plan.md"
MISSIONSCRIPT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_MISSIONSCRIPT_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
EVENT_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle-proof.md"
LORE_EVENT_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-event-object-code-lifecycle-proof.md"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"

MISSION_SCRIPTS = ROOT / "reverse-engineering" / "game-assets" / "mission-scripts-index.md"
LORE_MISSION_SCRIPTS = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-scripts-index.md"
MISSION_EVENTS = ROOT / "reverse-engineering" / "game-assets" / "mission-events-index.md"
LORE_MISSION_EVENTS = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-events-index.md"
MISSION_MESSAGES = ROOT / "reverse-engineering" / "game-assets" / "mission-message-usage.md"
LORE_MISSION_MESSAGES = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-message-usage.md"
MISSION_TEXT = ROOT / "reverse-engineering" / "game-assets" / "mission-text-index.md"
LORE_MISSION_TEXT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "mission-text-index.md"
MSL_SCRIPTING = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
LORE_MSL_SCRIPTING = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "msl-scripting.md"

PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
PLAN_LINK = "missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md"
SCHEMA_LINK = "missionscript-level100-tutorial-runtime-harness-boundary.v1.json"
WALKTHROUGH_LINK = "missionscript-level100-tutorial-static-walkthrough-proof-plan.md"
TEXT_LINK = "missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md"
PACKED_LINK = "missionscript-packed-vs-loose-script-selection-proof-plan.md"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Boundary Planning Proof Plan"
FOLLOWUP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Artifact Manifest Proof Plan"

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
    "runtime level100 mission outcome proven",
    "runtime text/audio behavior proven",
    "runtime message display proven",
    "runtime hud flashing proven",
    "runtime object identity proven",
    "runtime spawnthing behavior proven",
    "runtime getthingref behavior proven",
    "bea launch proof complete",
    "bea launch authorized",
    "runtime observation proof complete",
    "runtime observation proven",
    "screenshot proof complete",
    "native input proof complete",
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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def build_schema() -> dict[str, Any]:
    progress = read_json(PROGRESS)
    walk = read_json(WALKTHROUGH_SCHEMA)
    text = read_json(TEXT_SCHEMA)
    quality = progress["functionQuality"]
    current = progress["post100Reaudit"]["currentRiskRank"]
    commands = walk["commandFamilies"]

    return {
        "schemaVersion": "missionscript-level100-tutorial-runtime-harness-boundary.v1",
        "status": "PASS",
        "source": {
            "runtimeExecution": False,
            "ghidraMutation": False,
            "beLaunch": False,
            "executablePatch": False,
            "screenshotCapture": False,
            "nativeInput": False,
            "godotWork": False,
            "rawDialogueIncluded": False,
            "privatePathsIncluded": False,
            "schemaPurpose": "static boundary plan for a later copied-profile Level100 runtime observation proof",
        },
        "staticContext": {
            "staticFunctionQuality": f"{quality['commentedFunctions']}/{quality['totalFunctions']} = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": f"{current['focusedReviewed']}/1179 = 100.00%",
            "remainingActiveFocusedWork": current["remainingFocusedAfterLatestReview"],
            "latestGhidraBackup": BACKUP,
        },
        "upstreamProofs": [
            WALKTHROUGH_LINK,
            TEXT_LINK,
            PACKED_LINK,
            "missionscript-iscript-static-contract.md",
            "missionscript-event-object-code-lifecycle-proof.md",
        ],
        "selectedMission": {
            "mission": "level100",
            "entryScript": "LevelScript.msl",
            "fileCount": walk["level100Corpus"]["fileCount"],
            "extraScriptCount": walk["level100Corpus"]["extraScriptCount"],
            "totalMslLines": walk["level100Corpus"]["totalMslLines"],
        },
        "sourceSelectionBoundary": {
            "anchors": [
                "0x00539dc0 CMissionScriptObjectCode__StartLoadAsync",
                "0x00539ca0 CMissionScriptObjectCode__LoadAsync",
                "this+0x20",
                "this+0x124",
                "CDXMemBuffer__InitFromFile",
            ],
            "packedLoosePlanningCounts": {
                "looseScriptFiles": 733,
                "goodieStateCalls": 32,
                "targetScriptIndices": "72-74",
                "levelRows": 95,
                "looseEventNameCounts": 795,
                "topLevelAyaArchives": 301,
                "inflateErrors": 0,
                "literalGoodieApiTokenHits": 0,
            },
            "claimBoundary": "static source-selection planning only; no live loose-MSL loading or packed-vs-loose selection proof",
        },
        "eventObjectCodeBoundary": {
            "anchors": [
                "0x005383c0 IScript__ScheduleEvent",
                "0x00538b70 CScriptEventNB__PostEvent",
                "0x0052fda0 CEventFunction__Execute",
                "0x00539a60 CScriptObjectCode__CallEventDirect",
                "0x00539b00 CScriptObjectCode__Run",
                "0x0064ce50",
                "144",
                "0x0052ea40",
                "0x0052ec60",
            ],
            "claimBoundary": "static event/object-code anchors only; no runtime event outcome or command-effect proof",
        },
        "commandFamilyBoundaries": {
            "getSlot": commands["slotPersistence"]["getSlot"],
            "setSlotSave": commands["slotPersistence"]["setSlotSave"],
            "playCharMessageCombined": commands["messageAudio"]["combinedPlayCharMessage"],
            "messageTokens": commands["messageAudio"]["messageTokens"],
            "addHelpMessage": commands["messageAudio"]["addHelpMessage"],
            "highlightHudPart": commands["hudDisplay"]["highlightHudPart"],
            "unhighlightHudPart": commands["hudDisplay"]["unhighlightHudPart"],
            "getThingRefRaw": commands["thingSpawn"]["getThingRefRaw"],
            "getThingRefUnique": commands["thingSpawn"]["getThingRefUnique"],
            "spawnThingRaw": commands["thingSpawn"]["spawnThingRaw"],
            "claimBoundary": "static command-family accounting only; no runtime command effects",
        },
        "textSpeakerBoundary": {
            "objectiveTokens": text["tokenSets"]["objectiveTokens"],
            "lossTokens": text["tokenSets"]["lossTokens"],
            "speakerTokens": text["tokenSets"]["speakerTokens"],
            "relevantStaticTokens": text["resolution"]["relevantStaticTokenCount"],
            "missingReferences": text["resolution"]["missingReferenceTokens"],
            "claimBoundary": "static token/speaker resolution only; no runtime text/audio/message display proof",
        },
        "inputStaticEvidence": {
            "walkthroughSchema": WALKTHROUGH_LINK,
            "textSpeakerSchema": TEXT_LINK,
            "packedVsLooseBoundary": PACKED_LINK,
            "levelScript": "LevelScript.msl",
            "level100FileCount": walk["level100Corpus"]["fileCount"],
            "extraScriptCount": walk["level100Corpus"]["extraScriptCount"],
            "totalMslLines": walk["level100Corpus"]["totalMslLines"],
            "uniqueEventNames": walk["eventWalkthrough"]["uniqueEventNames"],
            "eventHandlerDeclarations": walk["eventWalkthrough"]["eventHandlerDeclarations"],
            "postEventCallsites": walk["eventWalkthrough"]["postEventCallsites"],
            "mismatchedPostedEvents": walk["eventWalkthrough"]["mismatchedPostedEvents"],
            "messageRows": commands["messageAudio"]["combinedPlayCharMessage"],
            "messageUnique": commands["messageAudio"]["messageTokens"],
            "helpTokens": len(commands["messageAudio"]["helpTokens"]),
            "speakerCounts": commands["messageAudio"]["speakerCounts"],
            "objectiveTokens": len(commands["objectiveOutcome"]["objectives"]),
            "slotRefs": commands["slotPersistence"]["slotRefs"],
            "hudParts": commands["hudDisplay"]["hudParts"],
            "getThingRefRaw": commands["thingSpawn"]["getThingRefRaw"],
            "getThingRefUnique": commands["thingSpawn"]["getThingRefUnique"],
            "spawnThingRaw": commands["thingSpawn"]["spawnThingRaw"],
            "spawnThingTypes": commands["thingSpawn"]["spawnThingTypes"],
            "textRelevantStaticTokens": text["resolution"]["relevantStaticTokenCount"],
            "missingTextReferences": text["resolution"]["missingReferenceTokens"],
            "generatedOnlyReferencedTextTokens": text["tokenSets"]["generatedOnlyReferencedTextTokens"],
        },
        "allowedFutureInputs": [
            "copied profile root",
            "copied BEA.exe specimen only if a later proof explicitly requires launch",
            "copied real save/options baselines when needed",
            "app-owned logs, frame captures, debugger logs, and manifests",
            "sanitized public summaries derived from private proof artifacts",
        ],
        "forbiddenDuringThisSlice": [
            "launch BEA",
            "patch any executable",
            "capture screenshots or frames",
            "drive native input",
            "attach a debugger",
            "load a live mission",
            "mutate the installed Steam game",
            "start Godot work",
            "claim runtime behavior",
        ],
        "laterRuntimeObservationPlan": [
            "select one copied-profile Level100 launch target",
            "verify specimen bytes before any future patch candidate",
            "record source-selection expectations separately from live proof",
            "observe only a narrow tutorial path or abort as inconclusive",
            "capture private artifacts under app-owned or ignored roots",
            "publish only sanitized counts and bounded conclusions",
        ],
        "requiredFutureArtifacts": [
            "copied profile manifest",
            "specimen hash and byte-check report",
            "launch command manifest",
            "source-selection observation log",
            "bounded event/message/HUD/object observation checklist",
            "private artifact inventory",
            "public-safe result summary",
        ],
        "stopConditions": [
            "installed game or original executable would be touched",
            "runtime source selection is ambiguous",
            "script behavior differs from static expectation",
            "event mismatch blocks interpretation",
            "text/audio/HUD output cannot be observed without broadening scope",
            "private raw dialogue, save data, screenshots, or paths would leak",
            "patching or native input is needed before the later proof explicitly arms it",
            "Godot/rebuild work is required to make the claim",
        ],
        "claims": [
            "The Level100 static walkthrough and text/speaker slices are strong enough to define a copied-profile runtime-harness boundary.",
            "The boundary plan selects allowed future inputs, required artifacts, and stop conditions without executing runtime proof.",
            "Runtime MissionScript, source-selection, text/audio, HUD, object, patch, visual, Godot, rebuild, and no-noticeable-difference claims remain separate.",
        ],
        "notClaimed": [
            "runtime MissionScript execution",
            "runtime command effects",
            "runtime event outcomes",
            "live loose-MSL loading",
            "packed-vs-loose script selection",
            "runtime Level100 mission outcome",
            "runtime objective UI",
            "runtime message or audio output",
            "runtime HUD flashing",
            "runtime object identity",
            "runtime SpawnThing behavior",
            "runtime GetThingRef lookup behavior",
            "BEA launch behavior",
            "BEA patching behavior",
            "screenshot/capture proof",
            "native input behavior",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
        "progressCheck": {
            "focusedReviewed": current["focusedReviewed"],
            "remainingFocusedAfterLatestReview": current["remainingFocusedAfterLatestReview"],
            "liveFocusedCandidatesAfterLatestReview": current["liveFocusedCandidatesAfterLatestReview"],
            "isWave911Reconstruction": current["isWave911Reconstruction"],
        },
        "nextStaticSlice": NEXT_SLICE,
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
    for path in (SCHEMA, LORE_SCHEMA):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} does not match generated schema", failures)
        require(actual["source"]["runtimeExecution"] is False, "schema runtimeExecution must be false", failures)
        require(actual["source"]["beLaunch"] is False, "schema beLaunch must be false", failures)
        require(actual["source"]["executablePatch"] is False, "schema executablePatch must be false", failures)
        require(actual["source"]["screenshotCapture"] is False, "schema screenshotCapture must be false", failures)
        require(actual["source"]["nativeInput"] is False, "schema nativeInput must be false", failures)
        require(actual["source"]["godotWork"] is False, "schema godotWork must be false", failures)
        require(actual["source"]["rawDialogueIncluded"] is False, "schema rawDialogueIncluded must be false", failures)
        require(actual["source"]["privatePathsIncluded"] is False, "schema privatePathsIncluded must be false", failures)
        require(actual["inputStaticEvidence"]["level100FileCount"] == 25, "Level100 file count mismatch", failures)
        require(actual["inputStaticEvidence"]["uniqueEventNames"] == 26, "unique event count mismatch", failures)
        require(actual["inputStaticEvidence"]["messageRows"] == 45, "message row count mismatch", failures)
        require(actual["inputStaticEvidence"]["textRelevantStaticTokens"] == 68, "text token count mismatch", failures)
        require(actual["inputStaticEvidence"]["missingTextReferences"] == [], "missing text references mismatch", failures)
        check_no_bad_tokens(path, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore runtime-harness boundary proof mirror mismatch", failures)

    core_tokens = (
        "MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan",
        "Status: runtime-harness boundary proof plan complete, not runtime proof",
        PLAN_LINK,
        SCHEMA_LINK,
        WALKTHROUGH_LINK,
        TEXT_LINK,
        PACKED_LINK,
        "level100",
        "LevelScript.msl",
        "25",
        "24",
        "1469",
        "26",
        "34",
        "41",
        "Destroyed Friendly Building",
        "Friendly Building Destroyed",
        "45",
        "43",
        "68/68",
        "0 missing",
        "4` `GetSlot",
        "4` `SetSlotSave",
        "7` `HighlightHudPart",
        "7` `UnHighlightHudPart",
        "18` raw `GetThingRef",
        "15` unique object names",
        "20` `SpawnThing",
        "P_TATIANA",
        "P_KRAMER",
        "P_TECHNICIAN",
        "0x005383c0",
        "0x00538b70",
        "0x0052fda0",
        "0x00539a60",
        "0x00539b00",
        "0x0064ce50",
        "144",
        "0x0052ea40",
        "0x0052ec60",
        "0x00539dc0",
        "0x00539ca0",
        "this+0x20",
        "this+0x124",
        "CDXMemBuffer__InitFromFile",
        "733",
        "32",
        "72-74",
        "95",
        "795",
        "301",
        "0` inflate errors",
        "0` literal Goodie API/token hits",
        "HUD_BATTLE_LINE_MAP",
        "HUD_RADAR",
        "SpawnThing",
        "GetThingRef",
        "copied profile manifest",
        "specimen hash and byte-check report",
        "source-selection observation log",
        "bounded event/message/HUD/object observation checklist",
        "private artifact inventory",
        "public-safe result summary",
        BACKUP,
        NEXT_SLICE,
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_tokens(path, failures)

    linked_paths = (
        BACKLOG,
        MAPPED,
        BIN_INDEX,
        RE_INDEX,
        MISSION_SCRIPTS,
        MISSION_EVENTS,
        MISSION_MESSAGES,
        MISSION_TEXT,
        MSL_SCRIPTING,
        WALKTHROUGH_PROOF,
        TEXT_PROOF,
        PACKED_LOOSE,
        MISSIONSCRIPT_CONTRACT,
        EVENT_PROOF,
    )
    for path in linked_paths:
        text = read_text(path)
        for token in (PLAN_LINK, SCHEMA_LINK, "MissionScript Level100 Tutorial Runtime Harness Boundary"):
            require(token in text, f"{path.relative_to(ROOT)} missing runtime-harness boundary token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (MISSION_SCRIPTS, LORE_MISSION_SCRIPTS),
        (MISSION_EVENTS, LORE_MISSION_EVENTS),
        (MISSION_MESSAGES, LORE_MISSION_MESSAGES),
        (MISSION_TEXT, LORE_MISSION_TEXT),
        (MSL_SCRIPTING, LORE_MSL_SCRIPTING),
        (WALKTHROUGH_PROOF, LORE_WALKTHROUGH_PROOF),
        (WALKTHROUGH_SCHEMA, LORE_WALKTHROUGH_SCHEMA),
        (TEXT_PROOF, LORE_TEXT_PROOF),
        (TEXT_SCHEMA, LORE_TEXT_SCHEMA),
        (PACKED_LOOSE, LORE_PACKED_LOOSE),
        (MISSIONSCRIPT_CONTRACT, LORE_MISSIONSCRIPT_CONTRACT),
        (EVENT_PROOF, LORE_EVENT_PROOF),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require("Completed MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan" in backlog, "backlog missing completed runtime-harness boundary slice", failures)
    require(
        f"The selected active static-to-proof slice is {NEXT_SLICE}" in backlog
        or f"Completed {NEXT_SLICE}" in backlog,
        "backlog missing copied-profile runtime observation boundary handoff",
        failures,
    )
    if f"Completed {NEXT_SLICE}" in backlog:
        require(
            f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}" in backlog,
            "backlog missing copied-profile runtime observation artifact manifest follow-up slice",
            failures,
        )
    require("The selected active static-to-proof slice is MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan" not in backlog, "backlog still marks boundary slice active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-runtime-harness-boundary-proof-plan")
        == r"py -3 tools\missionscript_level100_tutorial_runtime_harness_boundary_proof_plan_probe.py --check",
        "missing package Level100 runtime-harness boundary test script",
        failures,
    )


def run_check() -> list[str]:
    failures: list[str] = []
    check_schema(failures)
    check_docs(failures)
    check_package(failures)
    return failures


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

    if args.check or not args.write_schema:
        failures = run_check()
        if failures:
            print("MissionScript Level100 tutorial runtime-harness boundary probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript Level100 tutorial runtime-harness boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
