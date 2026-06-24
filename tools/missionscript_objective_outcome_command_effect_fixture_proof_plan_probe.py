#!/usr/bin/env python3
"""Validate MissionScript objective/outcome deterministic fixture proof artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect-fixture-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect-fixture-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect-fixture-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_objective_outcome_command_effect_fixture_proof_plan_2026-06-09.md"

CUTSCENE_FIXTURE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.v1.json"
OBJECTIVE_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect.v1.json"
ROLLUP = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.v1.json"
FIXTURE_SELECTION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-selection.v1.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
ISCRIPT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_ISCRIPT_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Objective/Outcome Command-Effect Fixture Proof Plan"
PREVIOUS_SLICE = "MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan"
NEXT_SLICE = "MissionScript Message/Audio Command-Effect Fixture Proof Plan"
HUD_DISPLAY_FIXTURE_SLICE = "MissionScript HUD / Display Command-Effect Fixture Proof Plan"
THING_VALUE_FIXTURE_SLICE = "MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan"
PLAYER_STATE_FIXTURE_SLICE = "MissionScript Player-State / Score Command-Effect Fixture Proof Plan"
COMPLETION_ROLLUP_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
POST_ROLLUP_NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
STATUS_TOKEN = "missionscript-objective-outcome-command-effect-fixture-proof-plan-complete-static-objective-outcome-effect-table-not-runtime-proof"
PREVIOUS_STATUS = "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan-complete-static-finite-camera-plan-not-runtime-proof"
OBJECTIVE_STATIC_STATUS = "PASS"

DESCRIPTOR_INDICES = (7, 8, 82, 83, 86, 87, 105)
OBJECTIVE_CASE_SEEDS = {
    "PrimaryObjectiveComplete": (0, 100),
    "SecondaryObjectiveComplete": (1, 200),
    "PrimaryObjectiveFailed": (2, 300),
    "SecondaryObjectiveFailed": (3, 400),
}
OUTCOME_MESSAGE_ID_SEED = 500

FALSE_GUARDS = (
    "programFilesInputUsed",
    "installedGameMutation",
    "originalExecutableMutation",
    "copiedFileMutation",
    "sourceBaselineRead",
    "privateArtifactMaterialized",
    "saveSynthesis",
    "liveLooseMslLoading",
    "packedResourceScriptSelectionProven",
    "runtimeExecution",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimeObjectiveStateWriteProven",
    "runtimeObjectiveUiBehaviorProven",
    "runtimeLevelOutcomeBehaviorProven",
    "runtimeSaveBehaviorProven",
    "runtimeCareerProgressionProven",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "sourceSelectionObserved",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "productUiWired",
    "rebuildImplementation",
    "exactCommandDescriptorLayoutProven",
    "exactCommandArityProven",
    "exactArgumentTypeSchemaProven",
    "exactCGameLayoutProven",
    "exactCCareerLayoutProven",
    "exactEndLevelDataLayoutProven",
    "objectiveIndexBoundsProven",
    "textIdResolutionProven",
    "messageIdResolutionProven",
    "eventOrderingProven",
    "missionSuccessFailureCriteriaProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeObjectiveRows",
    "runtimeOutcomeRows",
    "runtimeObjectiveUiRows",
    "runtimeSaveRows",
    "runtimeCareerRows",
    "privateFrameRowsObserved",
    "rowObservationRows",
    "sourceObservedRows",
    "sourceRuntimeObservationRows",
    "sourceRowStatusChangedCount",
    "newLaunchRows",
    "captureRows",
    "ocrRows",
    "rawDialogueRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "copiedFileMutationRows",
    "sourceBaselineReadRows",
    "privateArtifactRows",
    "rebuildImplementationRows",
    "godotProjectRows",
    "beProcessesAfterFixture",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawDialogueLeakCount",
)

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)g:[\\/]"), "private backup path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)subagents[\\/]"), "subagent artifact path"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framesha256|framebytelength"), "private frame locator/hash field"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime objective state write proven",
    "runtime objective ui behavior proven",
    "runtime level outcome behavior proven",
    "runtime save behavior proven",
    "runtime career progression proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact descriptor layout proven",
    "exact arity proven",
    "exact argument type schema proven",
    "exact cgame layout proven",
    "exact ccareer layout proven",
    "exact end_level_data layout proven",
    "objective index bounds proven",
    "text id resolution proven",
    "message id resolution proven",
    "event ordering proven",
    "mission success/failure criteria proven",
    "private-frame review complete",
    "source-selection observation complete",
    "visual qa complete",
    "godot parity proven",
    "ghidra mutation complete",
    "executable patching behavior proven",
    "product ui behavior proven",
    "rebuild implementation complete",
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


def no_bea_process_running() -> bool:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "if (Get-Process -Name BEA -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def objective_effect_cases(static_schema: dict[str, Any]) -> list[dict[str, Any]]:
    by_command = {row["command"]: row for row in static_schema["objectiveHandlers"]}
    cases: list[dict[str, Any]] = []
    for command, (objective_index, text_id) in OBJECTIVE_CASE_SEEDS.items():
        handler = by_command[command]
        cases.append(
            {
                "id": f"{command}-objective-{objective_index}-text-{text_id}",
                "command": command,
                "descriptorIndex": static_schema["descriptorSlots"][command]["index"],
                "recordAddress": static_schema["descriptorSlots"][command]["recordAddress"],
                "handlerAnchor": f"{handler['address']} {handler['name']}",
                "objectiveKind": handler["objectiveKind"],
                "objectiveIndexSeed": objective_index,
                "textIdSeed": text_id,
                "integerGetterSlot": "+0x30",
                "expectedTextStorage": f"{handler['textStorage']} with index={objective_index}",
                "expectedStateStorage": f"{handler['stateStorage']} with index={objective_index}",
                "expectedStateValue": handler["stateValue"],
                "expectedWriteCount": 2,
                "finiteIntegerOnly": True,
                "runtimeObjectiveStateWriteProven": False,
            }
        )
    return cases


def outcome_effect_cases(static_schema: dict[str, Any]) -> list[dict[str, Any]]:
    by_command = {row["command"]: row for row in static_schema["outcomeHandlers"]}
    cases: list[dict[str, Any]] = []
    for command in ("LevelWon", "LevelLost", "LevelLostString"):
        handler = by_command[command]
        case = {
            "id": command,
            "command": command,
            "descriptorIndex": static_schema["descriptorSlots"][command]["index"],
            "recordAddress": static_schema["descriptorSlots"][command]["recordAddress"],
            "handlerAnchor": f"{handler['address']} {handler['name']}",
            "expectedBridge": handler["bridge"],
            "expectedCallCount": 1,
            "finiteIntegerOnly": True,
            "runtimeLevelOutcomeBehaviorProven": False,
        }
        if command == "LevelLostString":
            case["messageIdSeed"] = OUTCOME_MESSAGE_ID_SEED
            case["integerGetterSlot"] = "+0x30"
            case["textOrMessageResolutionProven"] = False
        cases.append(case)
    return cases


def build_schema() -> dict[str, Any]:
    previous = read_json(CUTSCENE_FIXTURE)
    static_schema = read_json(OBJECTIVE_STATIC)
    rollup = read_json(ROLLUP)
    fixture_selection = read_json(FIXTURE_SELECTION)
    objective_cases = objective_effect_cases(static_schema)
    outcome_cases = outcome_effect_cases(static_schema)
    return {
        "schemaVersion": "missionscript-objective-outcome-command-effect-fixture-proof-plan.v1",
        "status": "PASS",
        "missionScriptObjectiveOutcomeCommandEffectFixtureProofPlanStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "objective-outcome",
        "selectedFixturePath": "objective-state-and-level-result-effect-table",
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "fixtureAccounting": {
            "sourceSchemaCount": 4,
            "corpusSourceCount": 2,
            "descriptorIndices": list(DESCRIPTOR_INDICES),
            "descriptorRecordCount": len(static_schema["descriptorSlots"]),
            "objectiveHandlerCount": len(static_schema["objectiveHandlers"]),
            "outcomeHandlerCount": len(static_schema["outcomeHandlers"]),
            "handlerAnchorCount": len(static_schema["objectiveHandlers"]) + len(static_schema["outcomeHandlers"]),
            "objectiveStateValueSet": [1, 2],
            "objectiveStorageFormulaCount": 4,
            "levelOutcomeCallCount": len(static_schema["outcomeHandlers"]),
            "integerGetterSlot": "+0x30",
            "wave580MetadataRows": static_schema["evidenceCounts"]["wave580MetadataRows"],
            "wave580TagRows": static_schema["evidenceCounts"]["wave580TagRows"],
            "wave580XrefRows": static_schema["evidenceCounts"]["wave580XrefRows"],
            "wave580InstructionRows": static_schema["evidenceCounts"]["wave580InstructionRows"],
            "wave580DecompileRows": static_schema["evidenceCounts"]["wave580DecompileRows"],
            "wave580VtableRows": static_schema["evidenceCounts"]["wave580VtableRows"],
            "wave585MetadataRows": static_schema["evidenceCounts"]["wave585MetadataRows"],
            "wave585TagRows": static_schema["evidenceCounts"]["wave585TagRows"],
            "wave585XrefRows": static_schema["evidenceCounts"]["wave585XrefRows"],
            "wave585InstructionRows": static_schema["evidenceCounts"]["wave585InstructionRows"],
            "wave585DecompileRows": static_schema["evidenceCounts"]["wave585DecompileRows"],
            "wave1049MetadataRows": static_schema["evidenceCounts"]["wave1049MetadataRows"],
            "wave1049XrefRows": static_schema["evidenceCounts"]["wave1049XrefRows"],
            "wave1049InstructionRows": static_schema["evidenceCounts"]["wave1049InstructionRows"],
            "wave1049DecompileRows": static_schema["evidenceCounts"]["wave1049DecompileRows"],
            "wave1049ContextMetadataRows": static_schema["evidenceCounts"]["wave1049ContextMetadataRows"],
            "wave1049ContextXrefRows": static_schema["evidenceCounts"]["wave1049ContextXrefRows"],
            "wave1049ContextInstructionRows": static_schema["evidenceCounts"]["wave1049ContextInstructionRows"],
            "wave1049ContextDecompileRows": static_schema["evidenceCounts"]["wave1049ContextDecompileRows"],
            "eventCorpusLevelRows": static_schema["missionEventCorpus"]["levelRows"],
            "eventCorpusEventCount": static_schema["missionEventCorpus"]["events"],
            "eventCorpusObjectiveIds": static_schema["missionEventCorpus"]["objectiveIds"],
            "eventCorpusPrimaryComplete": static_schema["missionEventCorpus"]["primaryComplete"],
            "eventCorpusSecondaryComplete": static_schema["missionEventCorpus"]["secondaryComplete"],
            "eventCorpusPrimaryFailed": static_schema["missionEventCorpus"]["primaryFailed"],
            "eventCorpusLevelWon": static_schema["missionEventCorpus"]["levelWon"],
            "eventCorpusLevelLost": static_schema["missionEventCorpus"]["levelLost"],
            "messageCorpusLevelRows": static_schema["missionMessageCorpus"]["levelRows"],
            "messageCorpusLevelLostFamily": static_schema["missionMessageCorpus"]["levelLostFamily"],
            "messageCorpusLevelWonFamily": static_schema["missionMessageCorpus"]["levelWonFamily"],
            "plannedObjectiveEffectCaseCount": len(objective_cases),
            "plannedOutcomeEffectCaseCount": len(outcome_cases),
            "deterministicFixtureCaseCount": len(objective_cases) + len(outcome_cases),
            "integerSeedCount": 9,
            "effectAssertionCount": sum(case["expectedWriteCount"] for case in objective_cases) + sum(case["expectedCallCount"] for case in outcome_cases),
            "rollupCommandFamilyCount": rollup["rollupAccounting"]["commandFamilyCount"],
            "fixtureSelectionOriginalRank": next(row["rank"] for row in fixture_selection["candidateRanking"] if row["family"] == "objective-outcome"),
            "previousFixtureStatus": previous["missionScriptCutscenePanCameraPositionDeterministicFixtureProofPlanStatus"],
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "publicLeakCheck": "PASS",
        },
        "sourceEvidence": {
            "previousFixture": {
                "schema": "reverse-engineering/binary-analysis/missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.v1.json",
                "status": previous["missionScriptCutscenePanCameraPositionDeterministicFixtureProofPlanStatus"],
                "selectedNextSlice": previous["selectedNextSlice"],
            },
            "objectiveOutcomeStaticProof": {
                "schema": "reverse-engineering/binary-analysis/missionscript-objective-outcome-command-effect.v1.json",
                "status": static_schema["status"],
                "descriptorIndices": list(DESCRIPTOR_INDICES),
                "objectiveHandlers": [row["name"] for row in static_schema["objectiveHandlers"]],
                "outcomeHandlers": [row["name"] for row in static_schema["outcomeHandlers"]],
                "bridgeContext": static_schema["bridgeContext"],
                "boundary": "static descriptor/body/corpus bridge only; runtime objective/outcome behavior remains unproven",
            },
            "rollup": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-rebuild-interface-rollup.v1.json",
                "commandFamilyCount": rollup["rollupAccounting"]["commandFamilyCount"],
                "descriptorRecordCount": rollup["rollupAccounting"]["descriptorRecordCount"],
                "duplicateDescriptorBoundary": "descriptor 105 LevelLostString also appears in vector-range context",
            },
            "fixtureSelection": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-fixture-selection.v1.json",
                "originalRank": next(row["rank"] for row in fixture_selection["candidateRanking"] if row["family"] == "objective-outcome"),
                "originalDecision": next(row["decision"] for row in fixture_selection["candidateRanking"] if row["family"] == "objective-outcome"),
            },
        },
        "fixtureModel": {
            "objectiveEffectModel": "objective_index/text_id integer seeds map to static text-array and state-array writes",
            "outcomeEffectModel": "LevelWon/LevelLost/LevelLostString map to static CGame level-result helper calls",
            "integerGetterSlot": "+0x30",
            "selectedRuntimeCommands": [
                "PrimaryObjectiveComplete",
                "SecondaryObjectiveComplete",
                "PrimaryObjectiveFailed",
                "SecondaryObjectiveFailed",
                "LevelWon",
                "LevelLost",
                "LevelLostString",
            ],
            "excludedCases": [
                "negative objective index bounds",
                "out-of-range objective index bounds",
                "text/message id resolution",
                "event ordering",
                "mission success/failure criteria",
                "career progression",
            ],
        },
        "deterministicObjectiveEffectCases": objective_cases,
        "deterministicOutcomeEffectCases": outcome_cases,
        "deferredProofGate": {
            "selectedNextSlice": NEXT_SLICE,
            "runtimeExecution": False,
            "beLaunch": False,
            "sourceBaselineRead": False,
            "privateArtifactMaterialized": False,
            "copiedFileMutation": False,
            "ghidraMutation": False,
            "godotWork": False,
            "rebuildImplementation": False,
            "requiresSeparateProofForRuntimeObjectiveUi": True,
            "requiresSeparateProofForRuntimeOutcomeBehavior": True,
            "requiresSeparateProofForRuntimeSaveCareerProgression": True,
        },
        "guardSummary": {
            "falseGuards": {key: False for key in FALSE_GUARDS},
            "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        },
        "claimBoundary": {
            "proves": [
                "four finite objective state/text write fixture cases tied to saved static objective handlers",
                "three finite level-result call fixture cases tied to saved static outcome handlers",
                "objective/outcome event and message corpus counts are preserved as static reference counts",
                "the objective/outcome fixture table is consolidated without runtime, Ghidra, patch, Godot, product UI, or rebuild claims",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime objective state writes",
                "runtime objective UI behavior",
                "runtime level outcome behavior",
                "runtime save behavior",
                "runtime career progression",
                "live loose-MSL loading",
                "packed-resource script selection",
                "exact command descriptor layout",
                "exact command arity",
                "exact argument type schema",
                "exact CGame layout",
                "exact CCareer layout",
                "exact END_LEVEL_DATA layout",
                "objective index bounds",
                "text id resolution",
                "message id resolution",
                "event ordering",
                "mission success/failure criteria",
                "source-selection observation",
                "private-frame review",
                "visual QA",
                "Godot parity",
                "Ghidra mutation",
                "executable patching",
                "product UI behavior",
                "rebuild implementation",
                "rebuild parity",
                "no-noticeable-difference parity",
            ],
        },
    }


def check_no_bad_public_content(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def assert_schema(actual: dict[str, Any], failures: list[str]) -> None:
    expected = build_schema()
    require(actual == expected, "schema is not regenerated from current objective/outcome fixture evidence", failures)
    accounting = actual["fixtureAccounting"]
    require(accounting["descriptorIndices"] == list(DESCRIPTOR_INDICES), "descriptor index list mismatch", failures)
    require(accounting["descriptorRecordCount"] == 7, "descriptor record count mismatch", failures)
    require(accounting["objectiveHandlerCount"] == 4, "objective handler count mismatch", failures)
    require(accounting["outcomeHandlerCount"] == 3, "outcome handler count mismatch", failures)
    require(accounting["handlerAnchorCount"] == 7, "handler anchor count mismatch", failures)
    require(accounting["objectiveStateValueSet"] == [1, 2], "objective state values mismatch", failures)
    require(accounting["integerGetterSlot"] == "+0x30", "integer getter slot mismatch", failures)
    require(accounting["eventCorpusLevelRows"] == 95, "event corpus level rows mismatch", failures)
    require(accounting["eventCorpusEventCount"] == 795, "event corpus event count mismatch", failures)
    require(accounting["eventCorpusObjectiveIds"] == 36, "event corpus objective id count mismatch", failures)
    require(accounting["eventCorpusPrimaryComplete"] == 115, "event corpus primary complete mismatch", failures)
    require(accounting["eventCorpusSecondaryComplete"] == 42, "event corpus secondary complete mismatch", failures)
    require(accounting["eventCorpusPrimaryFailed"] == 102, "event corpus primary failed mismatch", failures)
    require(accounting["eventCorpusLevelWon"] == 79, "event corpus LevelWon mismatch", failures)
    require(accounting["eventCorpusLevelLost"] == 13, "event corpus LevelLost mismatch", failures)
    require(accounting["messageCorpusLevelRows"] == 67, "message corpus level rows mismatch", failures)
    require(accounting["messageCorpusLevelLostFamily"] == 110, "message corpus LevelLost-family mismatch", failures)
    require(accounting["messageCorpusLevelWonFamily"] == 71, "message corpus LevelWon-family mismatch", failures)
    require(accounting["plannedObjectiveEffectCaseCount"] == 4, "objective effect case count mismatch", failures)
    require(accounting["plannedOutcomeEffectCaseCount"] == 3, "outcome effect case count mismatch", failures)
    require(accounting["deterministicFixtureCaseCount"] == 7, "deterministic fixture case count mismatch", failures)
    require(accounting["integerSeedCount"] == 9, "integer seed count mismatch", failures)
    require(accounting["effectAssertionCount"] == 11, "effect assertion count mismatch", failures)
    require(accounting["fixtureSelectionOriginalRank"] == 4, "fixture selection original rank mismatch", failures)
    require(accounting["previousFixtureStatus"] == PREVIOUS_STATUS, "previous fixture status mismatch", failures)
    require(accounting["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    for case in actual["deterministicObjectiveEffectCases"]:
        require(case["integerGetterSlot"] == "+0x30", f"objective getter slot mismatch: {case['id']}", failures)
        require(case["expectedWriteCount"] == 2, f"objective write count mismatch: {case['id']}", failures)
        require(case["finiteIntegerOnly"] is True, f"objective finite guard mismatch: {case['id']}", failures)
        require(case["runtimeObjectiveStateWriteProven"] is False, f"objective runtime guard mismatch: {case['id']}", failures)
    for case in actual["deterministicOutcomeEffectCases"]:
        require(case["expectedCallCount"] == 1, f"outcome call count mismatch: {case['id']}", failures)
        require(case["finiteIntegerOnly"] is True, f"outcome finite guard mismatch: {case['id']}", failures)
        require(case["runtimeLevelOutcomeBehaviorProven"] is False, f"outcome runtime guard mismatch: {case['id']}", failures)
    level_lost_string = next(case for case in actual["deterministicOutcomeEffectCases"] if case["command"] == "LevelLostString")
    require(level_lost_string["messageIdSeed"] == OUTCOME_MESSAGE_ID_SEED, "LevelLostString message id seed mismatch", failures)

    guards = actual["guardSummary"]
    for key in FALSE_GUARDS:
        require(guards["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guards["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    lore = read_json(LORE_RESULT)
    assert_schema(result, failures)
    require(lore == result, "lore schema mirror mismatch", failures)
    check_no_bad_public_content(RESULT, failures)


def check_source_prerequisites(failures: list[str]) -> None:
    previous = read_json(CUTSCENE_FIXTURE)
    static_schema = read_json(OBJECTIVE_STATIC)
    rollup = read_json(ROLLUP)
    fixture_selection = read_json(FIXTURE_SELECTION)

    require(previous["missionScriptCutscenePanCameraPositionDeterministicFixtureProofPlanStatus"] == PREVIOUS_STATUS, "previous fixture status mismatch", failures)
    require(previous["selectedNextSlice"] == THIS_SLICE, "previous fixture selected next slice mismatch", failures)
    require(static_schema["status"] == OBJECTIVE_STATIC_STATUS, "objective static schema status mismatch", failures)
    require(list(static_schema["descriptorSlots"].keys()) == ["LevelLost", "LevelWon", "PrimaryObjectiveComplete", "SecondaryObjectiveComplete", "PrimaryObjectiveFailed", "SecondaryObjectiveFailed", "LevelLostString"], "objective descriptor key order mismatch", failures)
    require([static_schema["descriptorSlots"][key]["index"] for key in static_schema["descriptorSlots"]] == list(DESCRIPTOR_INDICES), "objective descriptor index order mismatch", failures)
    require(len(static_schema["objectiveHandlers"]) == 4, "objective handler count mismatch", failures)
    require(len(static_schema["outcomeHandlers"]) == 3, "outcome handler count mismatch", failures)
    require(static_schema["missionEventCorpus"]["levelRows"] == 95, "event corpus level rows mismatch", failures)
    require(static_schema["missionMessageCorpus"]["levelRows"] == 67, "message corpus level rows mismatch", failures)
    require(rollup["rollupAccounting"]["commandFamilyCount"] == 9, "rollup command family count mismatch", failures)
    require(next(row["rank"] for row in fixture_selection["candidateRanking"] if row["family"] == "objective-outcome") == 4, "fixture selection rank mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-objective-outcome-command-effect-fixture-proof-plan.v1.json",
        f"missionScriptObjectiveOutcomeCommandEffectFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=objective-outcome",
        "selectedFixturePath=objective-state-and-level-result-effect-table",
        "descriptorIndices=7/8/82/83/86/87/105",
        "descriptorRecordCount=7",
        "objectiveHandlerCount=4",
        "outcomeHandlerCount=3",
        "handlerAnchorCount=7",
        "objectiveStateValueSet=1/2",
        "objectiveStorageFormulaCount=4",
        "levelOutcomeCallCount=3",
        "integerGetterSlot=+0x30",
        "wave580MetadataRows=6",
        "wave585MetadataRows=5",
        "wave1049MetadataRows=10",
        "eventCorpusLevelRows=95",
        "eventCorpusEventCount=795",
        "eventCorpusObjectiveIds=36",
        "eventCorpusPrimaryComplete=115",
        "eventCorpusSecondaryComplete=42",
        "eventCorpusPrimaryFailed=102",
        "eventCorpusLevelWon=79",
        "eventCorpusLevelLost=13",
        "messageCorpusLevelRows=67",
        "messageCorpusLevelLostFamily=110",
        "messageCorpusLevelWonFamily=71",
        "plannedObjectiveEffectCaseCount=4",
        "plannedOutcomeEffectCaseCount=3",
        "deterministicFixtureCaseCount=7",
        "integerSeedCount=9",
        "effectAssertionCount=11",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "PrimaryObjectiveComplete",
        "SecondaryObjectiveComplete",
        "PrimaryObjectiveFailed",
        "SecondaryObjectiveFailed",
        "LevelWon",
        "LevelLost",
        "LevelLostString",
        "0x005343e0 IScript__PrimaryObjectiveComplete",
        "0x00534410 IScript__SecondaryObjectiveComplete",
        "0x00534440 IScript__PrimaryObjectiveFailed",
        "0x00534470 IScript__SecondaryObjectiveFailed",
        "0x005381a0 IScript__LevelLost",
        "0x005381c0 IScript__LevelLostString",
        "0x005381e0 IScript__LevelWon",
        "DAT_008a9ae0",
        "DAT_008a9adc",
        "DAT_008a9b30",
        "DAT_008a9b2c",
        "CGame__DeclareLevelWon",
        "CGame__DeclareLevelLost",
        "CGame__FillOutEndLevelData",
        "CCareer__Update",
        "CEndLevelData__IsAllSecondaryObjectivesComplete",
        "runtimeExecution=false",
        "beLaunch=false",
        "sourceBaselineRead=false",
        "privateArtifactMaterialized=false",
        "copiedFileMutation=false",
        "ghidraMutation=false",
        "godotWork=false",
        "rebuildImplementation=false",
        "runtimeObservationRows=0",
        "missionScriptRuntimeEvidenceRows=0",
        "runtimeCommandEffectRows=0",
        "runtimeObjectiveRows=0",
        "runtimeOutcomeRows=0",
        "beProcessesAfterFixture=0",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)

    front_door_tokens = (
        THIS_SLICE,
        NEXT_SLICE,
        "missionscript-objective-outcome-command-effect-fixture-proof-plan.md",
        "missionscript-objective-outcome-command-effect-fixture-proof-plan.v1.json",
        f"missionScriptObjectiveOutcomeCommandEffectFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=objective-outcome",
        "selectedNextSlice=MissionScript Message/Audio Command-Effect Fixture Proof Plan",
        "plannedObjectiveEffectCaseCount=4",
        "plannedOutcomeEffectCaseCount=3",
        "deterministicFixtureCaseCount=7",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, ISCRIPT_CONTRACT):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks objective/outcome fixture active",
            failures,
        )

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed objective/outcome fixture lane", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed message/audio follow-up lane", failures)
    require(
        f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog,
        "backlog still marks message/audio follow-up lane active",
        failures,
    )
    require(
        f"Completed {HUD_DISPLAY_FIXTURE_SLICE}" in backlog,
        "backlog missing completed HUD/display follow-up lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {HUD_DISPLAY_FIXTURE_SLICE}. Status: selected" not in backlog,
        "backlog still marks HUD/display follow-up lane active",
        failures,
    )
    require(
        f"Completed {THING_VALUE_FIXTURE_SLICE}" in backlog
        or f"The selected active static-to-proof slice is {THING_VALUE_FIXTURE_SLICE}. Status: selected" in backlog,
        "backlog missing active-or-completed Thing Value / Engine Helper follow-up lane",
        failures,
    )
    require(
        f"Completed {COMPLETION_ROLLUP_SLICE}" in backlog,
        "backlog missing completed fixture-family completion rollup follow-up lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {COMPLETION_ROLLUP_SLICE}. Status: selected" not in backlog,
        "backlog still marks fixture-family completion rollup follow-up lane active",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {POST_ROLLUP_NEXT_SLICE}. Status: selected" in backlog,
        "backlog missing active post-rollup selection refresh lane",
        failures,
    )

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (ISCRIPT_CONTRACT, LORE_ISCRIPT_CONTRACT),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-objective-outcome-command-effect-fixture-proof-plan")
        == r"py -3 tools\missionscript_objective_outcome_command_effect_fixture_proof_plan_probe.py --check",
        "missing package objective/outcome fixture proof-plan test script",
        failures,
    )
    for script in (
        "test:missionscript-objective-outcome-command-effect-static",
        "test:missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan",
        "test:static-to-proof-transition-backlog",
    ):
        require(script in scripts, f"missing source package script: {script}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-schema", action="store_true")
    args = parser.parse_args()

    if args.write_schema:
        schema = build_schema()
        write_json(RESULT, schema)
        write_json(LORE_RESULT, schema)
        print(f"Wrote {RESULT.relative_to(ROOT)}")
        print(f"Wrote {LORE_RESULT.relative_to(ROOT)}")

    if args.check or not args.write_schema:
        failures: list[str] = []
        check_source_prerequisites(failures)
        check_result(failures)
        check_docs(failures)
        check_package(failures)
        require(no_bea_process_running(), "BEA.exe process is running after objective/outcome fixture proof", failures)
        if failures:
            print("MissionScript objective/outcome command-effect fixture proof-plan probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript objective/outcome command-effect fixture proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
