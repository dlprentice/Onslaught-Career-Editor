#!/usr/bin/env python3
"""Validate MissionScript Goodie-state/save command-effect fixture proof-plan artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-command-effect-fixture-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-command-effect-fixture-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_goodie_state_save_command_effect_fixture_proof_plan_2026-06-09.md"

GOODIE_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-command-effect.v1.json"
PLAYER_SCORE_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect.v1.json"
ROLLUP = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.v1.json"
VECTOR_FIXTURE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1.json"
COPIED_FILE_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-copied-file.v1.json"
GOODIES_DOC = ROOT / "reverse-engineering" / "save-file" / "goodies-system.md"
SAVE_FORMAT = ROOT / "reverse-engineering" / "save-file" / "save-format.md"
SAVE_GOODIES_QUICK = ROOT / "reverse-engineering" / "quick-reference" / "save-goodies.md"
APP_CORE_PATCHER = ROOT / "OnslaughtCareerEditor.AppCore" / "BesFilePatcher.cs"
APP_CORE_TESTS = ROOT / "OnslaughtCareerEditor.AppCore.Tests" / "SaveAnalyzerServiceTests.cs"

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
SAVE_GOODIES_LORE = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "goodies-system.md"
SAVE_FORMAT_LORE = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "save-format.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Goodie State / Save Command-Effect Fixture Proof Plan"
PREVIOUS_SLICE = "MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan"
NEXT_SLICE = "MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof Plan"
NEXT_ACTIVE_SLICE = "MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan"
COMPLETION_ROLLUP_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
POST_ROLLUP_NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
COMPLETED_GOODIE_CLEAN_ROOM_SLICE = "MissionScript Goodie State / Save Clean-Room Codec Interface Proof"
COMPLETED_GOODIE_BOUNDARY_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof"
POST_GOODIE_SELECTION_SLICE = "MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan"
STATUS_TOKEN = "missionscript-goodie-state-save-command-effect-fixture-proof-plan-complete-static-offset-state-fixture-plan-not-runtime-proof"
VECTOR_STATUS = "missionscript-vector-range-deterministic-helper-fixture-proof-plan-complete-pure-helper-fixture-not-runtime-proof"

GOODIE_BASE = 0x1F46
GOODIE_COUNT = 300
DISPLAYABLE_COUNT = 233
EXPECTED_SIZE = 10004
VERSION_WORD = "0x4BD1"

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
    "runtimeGoodieStateMutationProven",
    "runtimeSaveBehaviorProven",
    "runtimeGoodiesWallBehaviorProven",
    "runtimeScoreBehaviorProven",
    "runtimeDefaultOptionsProof",
    "runtimeGoodies71To73ReachabilityProven",
    "hiddenGoodiesUnreachableProven",
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
    "exactCCareerLayoutProven",
    "exactSourceBodyIdentityProven",
    "addScoreHandlerBodyProven",
    "beaPatchingBehaviorProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeGoodieStateRows",
    "runtimeGoodieMutationRows",
    "runtimeSaveRows",
    "runtimeDefaultOptionsRows",
    "runtimeGoodiesWallRows",
    "runtimeScoreRows",
    "runtimeGoodies71To73Rows",
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
    "productUiRows",
    "godotProjectRows",
    "rebuildImplementationRows",
    "beProcessesAfterFixture",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "rawSaveByteLeakCount",
)

SCRIPT_INDEX_CASE_INPUTS = (
    (1, "first-displayable-goodie"),
    (51, "known-script-call-displayable"),
    (53, "known-script-call-displayable"),
    (68, "known-script-call-race-displayable"),
    (69, "known-script-call-race-displayable"),
    (70, "known-script-call-race-displayable"),
    (71, "known-script-call-race-displayable"),
    (233, "last-displayable-goodie"),
    (234, "first-reserved-preserve-goodie"),
    (300, "last-reserved-preserve-goodie"),
    (0, "invalid-underflow-guard"),
    (301, "invalid-overflow-kill-counter-overlap-guard"),
)

STATE_CASES = (
    (0, "GS_UNKNOWN", "Locked"),
    (1, "GS_INSTRUCTIONS", "Instructions"),
    (2, "GS_NEW", "New"),
    (3, "GS_OLD", "Old"),
)

CORPUS_CASES = (
    (51, "present-known-call"),
    (53, "present-known-call"),
    (68, "present-known-race-call"),
    (69, "present-known-race-call"),
    (70, "present-known-race-call"),
    (71, "present-known-race-call"),
    (72, "zero-call-hidden-wall-gap-guard"),
    (73, "zero-call-hidden-wall-gap-guard"),
    (74, "zero-call-hidden-wall-gap-guard"),
)

APP_CORE_SAFETY_CASES = (
    "copied-bes-validation",
    "copied-defaultoptions-validation",
    "no-op-preservation",
    "analyze-save-300-goodie-rows",
    "scripted-single-write-through-true-view-offset",
    "scripted-multi-write-through-true-view-offsets",
    "displayable-boundary-232-accepted",
    "reserved-233-through-299-preserved",
    "reserved-write-rejected",
    "invalid-state-rejected",
    "wrong-size-rejected",
    "wrong-version-rejected",
    "in-place-write-rejected",
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
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"), "private frame locator/hash field"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime goodie state mutation proven",
    "runtime save behavior proven",
    "runtime goodies wall behavior proven",
    "runtime score behavior proven",
    "addscore handler-body proof complete",
    "exact descriptor layout proven",
    "exact command arity proven",
    "exact argument type schema proven",
    "exact ccareer layout proven",
    "hidden goodies unreachable proven",
    "goodies 71-73 reachability proven",
    "source-selection observation complete",
    "private-frame review complete",
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


def goodie_offset(script_index: int) -> int:
    return GOODIE_BASE + (script_index - 1) * 4


def offset_hex(value: int) -> str:
    return f"0x{value:04X}"


def script_index_cases() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for script_index, role in SCRIPT_INDEX_CASE_INPUTS:
        save_index = script_index - 1
        valid_storage = 1 <= script_index <= GOODIE_COUNT
        valid_displayable = 1 <= script_index <= DISPLAYABLE_COUNT
        valid_reserved = DISPLAYABLE_COUNT < script_index <= GOODIE_COUNT
        rows.append(
            {
                "scriptIndex": script_index,
                "saveGoodieIndex": save_index,
                "fileOffset": offset_hex(goodie_offset(script_index)),
                "fixtureRole": role,
                "validStorageIndex": valid_storage,
                "displayableInCleanRoomFixture": valid_displayable,
                "reservedPreserveInCleanRoomFixture": valid_reserved,
                "cleanRoomFixtureRejects": not valid_storage,
                "retailRejectionProven": False if not valid_storage else None,
            }
        )
    return rows


def descriptor_boundary_cases(goodie: dict[str, Any]) -> list[dict[str, Any]]:
    records = goodie["descriptorRecords"]
    handlers = {row["command"]: row for row in goodie["handlerReadback"]}
    return [
        {
            "id": "descriptor-set-goodie-state",
            "kind": "descriptor",
            "command": "SetGoodieState",
            "descriptorIndex": records["SetGoodieState"]["index"],
            "recordAddress": records["SetGoodieState"]["recordAddress"],
            "rawEntryValue": records["SetGoodieState"]["rawEntryValue"],
        },
        {
            "id": "descriptor-get-goodie-state",
            "kind": "descriptor",
            "command": "GetGoodieState",
            "descriptorIndex": records["GetGoodieState"]["index"],
            "recordAddress": records["GetGoodieState"]["recordAddress"],
            "rawEntryValue": records["GetGoodieState"]["rawEntryValue"],
        },
        {
            "id": "descriptor-add-score-alias-boundary",
            "kind": "alias-boundary",
            "command": "AddScore",
            "descriptorIndex": records["AddScore"]["index"],
            "recordAddress": records["AddScore"]["recordAddress"],
            "rawEntryValue": records["AddScore"]["rawEntryValue"],
            "aliasBoundary": records["AddScore"]["aliasBoundary"],
            "handlerBodyClaimed": False,
        },
        {
            "id": "handler-set-goodie-state",
            "kind": "handler",
            "command": "SetGoodieState",
            "address": handlers["SetGoodieState"]["address"],
            "name": handlers["SetGoodieState"]["name"],
            "summary": handlers["SetGoodieState"]["summary"],
        },
        {
            "id": "handler-get-goodie-state",
            "kind": "handler",
            "command": "GetGoodieState",
            "address": handlers["GetGoodieState"]["address"],
            "name": handlers["GetGoodieState"]["name"],
            "summary": handlers["GetGoodieState"]["summary"],
        },
    ]


def state_cases() -> list[dict[str, Any]]:
    return [
        {
            "rawState": value,
            "enumName": enum_name,
            "appCoreLabel": label,
            "cleanRoomFixtureAccepts": True,
        }
        for value, enum_name, label in STATE_CASES
    ]


def corpus_cases() -> list[dict[str, Any]]:
    return [
        {
            "scriptIndex": script_index,
            "saveGoodieIndex": script_index - 1,
            "corpusBoundary": boundary,
            "countsTowardLooseGoodieStateCallTotal": boundary.startswith("present"),
        }
        for script_index, boundary in CORPUS_CASES
    ]


def app_core_safety_cases() -> list[dict[str, Any]]:
    return [
        {
            "id": case_id,
            "plannedForNextSlice": True,
            "requiresCopiedRealBaseline": case_id
            in {
                "copied-bes-validation",
                "copied-defaultoptions-validation",
                "no-op-preservation",
                "scripted-single-write-through-true-view-offset",
                "scripted-multi-write-through-true-view-offsets",
            },
        }
        for case_id in APP_CORE_SAFETY_CASES
    ]


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


def build_schema() -> dict[str, Any]:
    goodie = read_json(GOODIE_STATIC)
    player_score = read_json(PLAYER_SCORE_STATIC)
    rollup = read_json(ROLLUP)
    vector_fixture = read_json(VECTOR_FIXTURE)
    copied_file = read_json(COPIED_FILE_PROOF)

    descriptor_cases = descriptor_boundary_cases(goodie)
    offset_cases = script_index_cases()
    states = state_cases()
    corpus = corpus_cases()
    safety = app_core_safety_cases()
    planned_total = len(descriptor_cases) + len(offset_cases) + len(states) + len(corpus) + len(safety)
    return {
        "schemaVersion": "missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1",
        "status": "PASS",
        "missionScriptGoodieStateSaveCommandEffectFixtureProofPlanStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "goodie-state-save",
        "selectedFixturePath": "goodie-state-save-index-state-byte-preservation",
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "fixtureAccounting": {
            "sourceProofCount": 6,
            "selectedFixtureFamily": "goodie-state-save",
            "selectedFixturePath": "goodie-state-save-index-state-byte-preservation",
            "fixtureFamilyCount": 5,
            "plannedGoodieFixtureCaseCount": planned_total,
            "descriptorBoundaryCaseCount": len(descriptor_cases),
            "scriptIndexOffsetCaseCount": len(offset_cases),
            "stateValueCaseCount": len(states),
            "corpusBoundaryCaseCount": len(corpus),
            "appCoreCopiedSaveSafetyCaseCount": len(safety),
            "descriptorRecordCount": len(goodie["descriptorRecords"]),
            "uniqueDescriptorIndexCount": 3,
            "descriptorIndices": [84, 118, 119],
            "handlerReadbackCount": len(goodie["handlerReadback"]),
            "handlerAnchorCount": len(goodie["handlerReadback"]),
            "wave579MetadataRows": goodie["evidenceCounts"]["wave579MetadataRows"],
            "wave579TagRows": goodie["evidenceCounts"]["wave579TagRows"],
            "wave579XrefRows": goodie["evidenceCounts"]["wave579XrefRows"],
            "wave579InstructionRows": goodie["evidenceCounts"]["wave579InstructionRows"],
            "wave579DecompileRows": goodie["evidenceCounts"]["wave579DecompileRows"],
            "wave579VtableRows": goodie["evidenceCounts"]["wave579VtableRows"],
            "goodieStorageEntryCount": GOODIE_COUNT,
            "displayableGoodieCount": DISPLAYABLE_COUNT,
            "reservedPreserveEntryCount": GOODIE_COUNT - DISPLAYABLE_COUNT,
            "trueViewGoodieBase": offset_hex(GOODIE_BASE),
            "knownScriptGoodieCallIndexCount": 6,
            "looseGoodieStateCallCount": 32,
            "zeroTargetScriptIndexCount": 3,
            "addScoreCorpusCallCount": player_score["looseMslUsage"]["directNonCommentCounts"]["AddScore"]["calls"],
            "copiedFileProofExpectedSize": copied_file["container"]["expectedSize"],
            "copiedFileProofVersionWord": copied_file["container"]["versionWord"],
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "publicLeakCheck": "PASS",
        },
        "sourceEvidence": {
            "previousVectorRangeFixture": {
                "schema": "reverse-engineering/binary-analysis/missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1.json",
                "status": vector_fixture["missionScriptVectorRangeDeterministicHelperFixtureProofPlanStatus"],
                "selectedNextSlice": vector_fixture["selectedNextSlice"],
            },
            "goodieStaticProof": {
                "schema": "reverse-engineering/binary-analysis/missionscript-goodie-state-command-effect.v1.json",
                "proof": "reverse-engineering/binary-analysis/missionscript-goodie-state-command-effect-static-proof.md",
                "descriptorRecords": goodie["descriptorRecords"],
                "handlerReadback": goodie["handlerReadback"],
                "saveMapping": goodie["saveMapping"],
                "addScoreBoundary": goodie["addScoreBoundary"],
            },
            "playerStateScoreStaticProof": {
                "schema": "reverse-engineering/binary-analysis/missionscript-player-state-score-command-effect.v1.json",
                "addScoreDirectNonCommentCalls": player_score["looseMslUsage"]["directNonCommentCounts"]["AddScore"]["calls"],
                "addScoreAliasBoundary": player_score["descriptorRecords"]["AddScore"]["boundary"],
            },
            "rollup": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-rebuild-interface-rollup.v1.json",
                "goodieStateFamilyPresent": any(row["familyId"] == "goodie-state" for row in rollup["sourceSchemas"]),
                "goodieStateSaveInterfacePresent": any(row["id"] == "goodie-state-save" for row in rollup["interfaceFamilies"]),
            },
            "saveDocs": {
                "goodiesSystem": "reverse-engineering/save-file/goodies-system.md",
                "saveFormat": "reverse-engineering/save-file/save-format.md",
                "quickReference": "reverse-engineering/quick-reference/save-goodies.md",
            },
            "copiedFileProofAndAppCore": {
                "copiedFileProof": "reverse-engineering/binary-analysis/save-options-controller-byte-preservation-copied-file.v1.json",
                "appCorePatcher": "OnslaughtCareerEditor.AppCore/BesFilePatcher.cs",
                "appCoreTests": "OnslaughtCareerEditor.AppCore.Tests/SaveAnalyzerServiceTests.cs",
                "expectedSize": copied_file["container"]["expectedSize"],
                "versionWord": copied_file["container"]["versionWord"],
                "appCoreWritesTrueViewOffsets": True,
                "appCoreRejectsInPlaceOutput": True,
                "appCoreRejectsReservedGoodieSlots": True,
                "appCoreRejectsInvalidGoodieStates": True,
            },
        },
        "descriptorBoundaryCases": descriptor_cases,
        "scriptIndexOffsetCases": offset_cases,
        "stateValueCases": states,
        "corpusBoundaryCases": corpus,
        "appCoreCopiedSaveSafetyCases": safety,
        "futureCopiedBaselineGate": {
            "selectedNextSlice": NEXT_SLICE,
            "requiresCopiedRealBesBaseline": True,
            "requiresCopiedRealDefaultOptionsBaseline": True,
            "expectedSize": EXPECTED_SIZE,
            "versionWord": VERSION_WORD,
            "copyBeforeWrite": True,
            "sourceAndOutputPathsDistinct": True,
            "sourceBaselinesUnchanged": True,
            "reservedGoodiesUnchangedUnlessExplicitFutureSliceArmsThem": True,
            "synthesizedSaveBuffersAreNotAcceptedAsAuthority": True,
            "publicSchemaMustOmitSourcePathsHashesAndRawBytes": True,
        },
        "guardSummary": {
            "falseGuards": {key: False for key in FALSE_GUARDS},
            "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        },
        "claimBoundary": {
            "proves": [
                "public-safe static/codec fixture plan for Goodie command descriptors",
                "handler anchors for SetGoodieState and GetGoodieState",
                "one-based script-index to true-view save-offset mapping for selected boundary cases",
                "state enum vocabulary 0..3",
                "corpus presence/absence guard for known Goodie-state script indices and 72..74",
                "copied-save AppCore safety gates required before byte-diff proof",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime Goodie state mutation",
                "runtime save behavior",
                "runtime defaultoptions behavior",
                "runtime Goodies wall behavior",
                "runtime score behavior",
                "AddScore handler-body semantics",
                "hidden Goodies unreachable",
                "Goodies 71-73 runtime reachability",
                "exact descriptor layout",
                "exact command arity",
                "exact argument type schema",
                "exact CCareer layout",
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
    require(actual == expected, "schema is not regenerated from current source evidence and offset fixtures", failures)
    accounting = actual["fixtureAccounting"]
    require(accounting["sourceProofCount"] == 6, "source proof count mismatch", failures)
    require(accounting["fixtureFamilyCount"] == 5, "fixture family count mismatch", failures)
    require(accounting["plannedGoodieFixtureCaseCount"] == 43, "planned Goodie fixture case count mismatch", failures)
    require(accounting["descriptorBoundaryCaseCount"] == 5, "descriptor boundary case count mismatch", failures)
    require(accounting["scriptIndexOffsetCaseCount"] == 12, "script index offset case count mismatch", failures)
    require(accounting["stateValueCaseCount"] == 4, "state value case count mismatch", failures)
    require(accounting["corpusBoundaryCaseCount"] == 9, "corpus boundary case count mismatch", failures)
    require(accounting["appCoreCopiedSaveSafetyCaseCount"] == 13, "AppCore copied-save safety case count mismatch", failures)
    require(accounting["descriptorRecordCount"] == 3, "descriptor record count mismatch", failures)
    require(accounting["uniqueDescriptorIndexCount"] == 3, "unique descriptor count mismatch", failures)
    require(accounting["descriptorIndices"] == [84, 118, 119], "descriptor index list mismatch", failures)
    require(accounting["handlerReadbackCount"] == 2, "handler read-back count mismatch", failures)
    require(accounting["handlerAnchorCount"] == 2, "handler anchor count mismatch", failures)
    require(accounting["wave579MetadataRows"] == 6, "Wave579 metadata count mismatch", failures)
    require(accounting["wave579TagRows"] == 6, "Wave579 tag count mismatch", failures)
    require(accounting["wave579XrefRows"] == 6, "Wave579 xref count mismatch", failures)
    require(accounting["wave579InstructionRows"] == 1326, "Wave579 instruction count mismatch", failures)
    require(accounting["wave579DecompileRows"] == 6, "Wave579 decompile count mismatch", failures)
    require(accounting["wave579VtableRows"] == 24, "Wave579 vtable count mismatch", failures)
    require(accounting["goodieStorageEntryCount"] == 300, "Goodie storage entry count mismatch", failures)
    require(accounting["displayableGoodieCount"] == 233, "displayable Goodie count mismatch", failures)
    require(accounting["reservedPreserveEntryCount"] == 67, "reserved Goodie count mismatch", failures)
    require(accounting["trueViewGoodieBase"] == "0x1F46", "true-view Goodie base mismatch", failures)
    require(accounting["knownScriptGoodieCallIndexCount"] == 6, "known script index count mismatch", failures)
    require(accounting["looseGoodieStateCallCount"] == 32, "loose Goodie-state call count mismatch", failures)
    require(accounting["zeroTargetScriptIndexCount"] == 3, "zero target script index count mismatch", failures)
    require(accounting["addScoreCorpusCallCount"] == 15, "AddScore corpus count mismatch", failures)
    require(accounting["copiedFileProofExpectedSize"] == EXPECTED_SIZE, "copied-file expected size mismatch", failures)
    require(accounting["copiedFileProofVersionWord"] == VERSION_WORD, "copied-file version word mismatch", failures)
    require(accounting["falseGuardCount"] == 41, "false guard count mismatch", failures)
    require(accounting["zeroCounterCount"] == 31, "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    seen_cases = {(row["scriptIndex"], row["fileOffset"]) for row in actual["scriptIndexOffsetCases"]}
    expected_offsets = {
        (1, "0x1F46"),
        (51, "0x200E"),
        (53, "0x2016"),
        (68, "0x2052"),
        (69, "0x2056"),
        (70, "0x205A"),
        (71, "0x205E"),
        (233, "0x22E6"),
        (234, "0x22EA"),
        (300, "0x23F2"),
        (0, "0x1F42"),
        (301, "0x23F6"),
    }
    require(seen_cases == expected_offsets, "script index offset fixture cases mismatch", failures)
    for row in actual["scriptIndexOffsetCases"]:
        require(row["fileOffset"] == offset_hex(goodie_offset(row["scriptIndex"])), f"offset formula mismatch for script index {row['scriptIndex']}", failures)
        if row["scriptIndex"] in (0, 301):
            require(row["cleanRoomFixtureRejects"] is True, f"invalid script index not rejected: {row['scriptIndex']}", failures)
            require(row["retailRejectionProven"] is False, f"invalid retail rejection overclaim: {row['scriptIndex']}", failures)

    require([row["rawState"] for row in actual["stateValueCases"]] == [0, 1, 2, 3], "state values mismatch", failures)
    require([row["enumName"] for row in actual["stateValueCases"]] == ["GS_UNKNOWN", "GS_INSTRUCTIONS", "GS_NEW", "GS_OLD"], "state enum names mismatch", failures)
    require([row["scriptIndex"] for row in actual["corpusBoundaryCases"]] == [51, 53, 68, 69, 70, 71, 72, 73, 74], "corpus boundary index list mismatch", failures)
    require(sum(1 for row in actual["corpusBoundaryCases"] if row["countsTowardLooseGoodieStateCallTotal"]) == 6, "present corpus case count mismatch", failures)
    require(sum(1 for row in actual["corpusBoundaryCases"] if not row["countsTowardLooseGoodieStateCallTotal"]) == 3, "zero corpus guard count mismatch", failures)
    require(len(actual["appCoreCopiedSaveSafetyCases"]) == 13, "AppCore safety case list mismatch", failures)

    guards = actual["guardSummary"]
    for key in FALSE_GUARDS:
        require(guards["falseGuards"].get(key) is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guards["zeroCounters"].get(key) == 0, f"zero counter mismatch: {key}", failures)


def check_source_prerequisites(failures: list[str]) -> None:
    goodie = read_json(GOODIE_STATIC)
    player_score = read_json(PLAYER_SCORE_STATIC)
    rollup = read_json(ROLLUP)
    vector_fixture = read_json(VECTOR_FIXTURE)
    copied_file = read_json(COPIED_FILE_PROOF)

    require(goodie["schemaVersion"] == "missionscript-goodie-state-command-effect.v1", "Goodie static schema version mismatch", failures)
    require(goodie["status"] == "PASS", "Goodie static status mismatch", failures)
    require(goodie["descriptorRecords"]["SetGoodieState"]["index"] == 118, "SetGoodieState descriptor index mismatch", failures)
    require(goodie["descriptorRecords"]["GetGoodieState"]["index"] == 119, "GetGoodieState descriptor index mismatch", failures)
    require(goodie["descriptorRecords"]["AddScore"]["index"] == 84, "AddScore descriptor index mismatch", failures)
    require(goodie["descriptorRecords"]["AddScore"]["aliasBoundary"] == "0x00534410 IScript__SecondaryObjectiveComplete", "AddScore alias boundary mismatch", failures)
    require({row["address"] for row in goodie["handlerReadback"]} == {"0x00533a70", "0x00533aa0"}, "Goodie handler address set mismatch", failures)
    require(goodie["saveMapping"]["trueViewFileBase"] == "0x1F46", "Goodie save true-view base mismatch", failures)
    require(goodie["saveMapping"]["entryCount"] == GOODIE_COUNT, "Goodie entry count mismatch", failures)
    require(goodie["saveMapping"]["stateValues"] == {"0": "GS_UNKNOWN", "1": "GS_INSTRUCTIONS", "2": "GS_NEW", "3": "GS_OLD"}, "Goodie state value map mismatch", failures)
    require(goodie["scriptCorpusContext"]["knownScriptGoodieCalls"] == "documented 1-based calls for indices 51, 53, and 68-71", "Goodie corpus context mismatch", failures)

    require(player_score["descriptorRecords"]["AddScore"]["index"] == 84, "player-state AddScore descriptor mismatch", failures)
    require(player_score["looseMslUsage"]["directNonCommentCounts"]["AddScore"]["calls"] == 15, "AddScore direct call count mismatch", failures)
    require(rollup["rollupAccounting"]["commandFamilyCount"] == 9, "rollup family count mismatch", failures)
    require(any(row["familyId"] == "goodie-state" for row in rollup["sourceSchemas"]), "rollup missing Goodie state family", failures)
    require(any(row["id"] == "goodie-state-save" for row in rollup["interfaceFamilies"]), "rollup missing Goodie-state-save interface family", failures)
    require(vector_fixture["missionScriptVectorRangeDeterministicHelperFixtureProofPlanStatus"] == VECTOR_STATUS, "previous vector fixture status mismatch", failures)
    require(vector_fixture["selectedNextSlice"] == THIS_SLICE, "previous vector fixture next slice mismatch", failures)
    require(copied_file["container"]["expectedSize"] == EXPECTED_SIZE, "copied-file expected size mismatch", failures)
    require(copied_file["container"]["versionWord"] == VERSION_WORD, "copied-file version word mismatch", failures)
    require(copied_file["source"]["runtimeExecution"] is False, "copied-file runtime guard mismatch", failures)
    require(copied_file["source"]["saveSynthesis"] is False, "copied-file synthesis guard mismatch", failures)

    docs = {
        GOODIES_DOC: ("0x1F46", "script_index = save_goodie_index + 1", "script_index = 0", "32 Goodie state calls", "zero calls for 72-74", "Goodie 228"),
        SAVE_FORMAT: ("10004", "0x4BD1", "0x1F46", "`300` Goodie entries", "indices `0-232`", "`233-299`"),
        SAVE_GOODIES_QUICK: ("Base (true dword view): 0x1F46", "indices 0-232", "71-73", "zero calls for 72-74", "Goodie 228"),
        APP_CORE_PATCHER: ("EXPECTED_FILE_SIZE = 10004", "VERSION_WORD = 0x4BD1", "PatchGoodieStates", "GOODIE_BASE + index * 4", "Refusing to patch in place", "displayable Goodie index", "must be 0, 1, 2, or 3"),
        APP_CORE_TESTS: ("AnalyzeSave_CapturesPerSlotGoodieStatesFromTrueDwordView", "PatchGoodieStates_WritesOnlyRequestedHiddenGoodiesThroughTrueDwordView", "PatchGoodieStates_RejectsReservedGoodieSlots", "0x1F46"),
    }
    for path, tokens in docs.items():
        text = read_text(path)
        for token in tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing prerequisite token: {token}", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    lore = read_json(LORE_RESULT)
    assert_schema(result, failures)
    require(lore == result, "lore schema mirror mismatch", failures)
    check_no_bad_public_content(RESULT, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1.json",
        f"missionScriptGoodieStateSaveCommandEffectFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=goodie-state-save",
        "selectedFixturePath=goodie-state-save-index-state-byte-preservation",
        "selectedNextSlice=MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof Plan",
        "sourceProofCount=6",
        "fixtureFamilyCount=5",
        "plannedGoodieFixtureCaseCount=43",
        "descriptorBoundaryCaseCount=5",
        "scriptIndexOffsetCaseCount=12",
        "stateValueCaseCount=4",
        "corpusBoundaryCaseCount=9",
        "appCoreCopiedSaveSafetyCaseCount=13",
        "descriptorRecordCount=3",
        "uniqueDescriptorIndexCount=3",
        "descriptorIndices=84/118/119",
        "handlerReadbackCount=2",
        "handlerAnchorCount=2",
        "wave579MetadataRows=6",
        "wave579TagRows=6",
        "wave579XrefRows=6",
        "wave579InstructionRows=1326",
        "wave579DecompileRows=6",
        "wave579VtableRows=24",
        "goodieStorageEntryCount=300",
        "displayableGoodieCount=233",
        "reservedPreserveEntryCount=67",
        "trueViewGoodieBase=0x1F46",
        "knownScriptGoodieCallIndexCount=6",
        "looseGoodieStateCallCount=32",
        "zeroTargetScriptIndexCount=3",
        "addScoreCorpusCallCount=15",
        "copiedFileProofExpectedSize=10004",
        "copiedFileProofVersionWord=0x4BD1",
        "script index `1 -> 0x1F46`",
        "script index `51 -> 0x200E`",
        "script index `53 -> 0x2016`",
        "script index `68 -> 0x2052`",
        "script index `71 -> 0x205E`",
        "script index `233 -> 0x22E6`",
        "script index `234 -> 0x22EA`",
        "script index `300 -> 0x23F2`",
        "script index `301 -> 0x23F6`",
        "script index `0 -> 0x1F42`",
        "GS_UNKNOWN",
        "GS_INSTRUCTIONS",
        "GS_NEW",
        "GS_OLD",
        "0x00533a70 IScript__SetGoodieState",
        "0x00533aa0 IScript__GetGoodieState",
        "0x00662564",
        "0x0064e350",
        "0x0064ebd0",
        "0x0064ec10",
        "0x00534410 IScript__SecondaryObjectiveComplete",
        "falseGuardCount=41",
        "zeroCounterCount=31",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "runtimeExecution=false",
        "runtimeGoodieStateMutationProven=false",
        "runtimeSaveBehaviorProven=false",
        "runtimeGoodiesWallBehaviorProven=false",
        "runtimeScoreBehaviorProven=false",
        "addScoreHandlerBodyProven=false",
        "sourceBaselineRead=false",
        "copiedFileMutation=false",
        "ghidraMutation=false",
        "godotWork=false",
        "productUiWired=false",
        "rebuildImplementation=false",
        "runtimeObservationRows=0",
        "missionScriptRuntimeEvidenceRows=0",
        "runtimeCommandEffectRows=0",
        "runtimeGoodieStateRows=0",
        "runtimeSaveRows=0",
        "runtimeGoodiesWallRows=0",
        "runtimeScoreRows=0",
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
        "missionscript-goodie-state-save-command-effect-fixture-proof-plan.md",
        "missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1.json",
        f"missionScriptGoodieStateSaveCommandEffectFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=goodie-state-save",
        "selectedFixturePath=goodie-state-save-index-state-byte-preservation",
        "selectedNextSlice=MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof Plan",
        "plannedGoodieFixtureCaseCount=43",
        "descriptorBoundaryCaseCount=5",
        "scriptIndexOffsetCaseCount=12",
        "stateValueCaseCount=4",
        "corpusBoundaryCaseCount=9",
        "appCoreCopiedSaveSafetyCaseCount=13",
        "trueViewGoodieBase=0x1F46",
        "looseGoodieStateCallCount=32",
        "zeroTargetScriptIndexCount=3",
        "addScoreCorpusCallCount=15",
        "falseGuardCount=41",
        "zeroCounterCount=31",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, ISCRIPT_CONTRACT, GOODIES_DOC, SAVE_FORMAT):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks Goodie fixture lane active",
            failures,
        )
    require(
        f"Completed {NEXT_SLICE}" in read_text(BACKLOG),
        "backlog missing completed copied-baseline byte-diff fixture lane",
        failures,
    )
    require(
        f"Completed {COMPLETED_GOODIE_CLEAN_ROOM_SLICE}" in read_text(BACKLOG),
        "backlog missing completed Goodie clean-room codec interface lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Goodie State / Save Clean-Room Codec Interface Proof Plan. Status: selected" not in read_text(BACKLOG),
        "backlog still marks Goodie clean-room codec interface lane active",
        failures,
    )
    require(
        f"Completed {COMPLETED_GOODIE_BOUNDARY_SLICE}" in read_text(BACKLOG),
        "backlog missing completed Goodie copied-baseline boundary corpus harness lane",
        failures,
    )
    require(
        f"Completed {POST_GOODIE_SELECTION_SLICE}" in read_text(BACKLOG),
        "backlog missing completed post-Goodie selection refresh lane",
        failures,
    )
    require(
        f"Completed {NEXT_ACTIVE_SLICE}" in read_text(BACKLOG),
        "backlog missing completed cutscene pan-camera/position fixture lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {NEXT_ACTIVE_SLICE}. Status: selected" not in read_text(BACKLOG),
        "backlog still marks cutscene pan-camera/position fixture lane active",
        failures,
    )
    require(
        f"Completed {COMPLETION_ROLLUP_SLICE}" in read_text(BACKLOG),
        "backlog missing completed fixture-family completion rollup lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {POST_ROLLUP_NEXT_SLICE}. Status: selected" in read_text(BACKLOG),
        "backlog missing active post-rollup selection refresh lane",
        failures,
    )

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (ISCRIPT_CONTRACT, LORE_ISCRIPT_CONTRACT),
        (GOODIES_DOC, SAVE_GOODIES_LORE),
        (SAVE_FORMAT, SAVE_FORMAT_LORE),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-goodie-state-save-command-effect-fixture-proof-plan")
        == r"py -3 tools\missionscript_goodie_state_save_command_effect_fixture_proof_plan_probe.py --check",
        "missing package Goodie-state/save fixture proof-plan test script",
        failures,
    )
    for script in (
        "test:missionscript-goodie-state-command-effect-static",
        "test:missionscript-vector-range-deterministic-helper-fixture-proof-plan",
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
        require(no_bea_process_running(), "BEA.exe process is running after Goodie-state/save fixture proof plan", failures)
        if failures:
            print("MissionScript Goodie-state/save fixture proof-plan probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript Goodie-state/save fixture proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
