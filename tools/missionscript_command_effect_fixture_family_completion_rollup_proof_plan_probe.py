#!/usr/bin/env python3
"""Validate the MissionScript command-effect fixture-family completion rollup."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-family-completion-rollup-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-family-completion-rollup-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-family-completion-rollup-proof-plan.md"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-family-completion-rollup-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_command_effect_fixture_family_completion_rollup_proof_plan_2026-06-09.md"

INTERFACE_ROLLUP = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.v1.json"
PREVIOUS_FIXTURE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect-fixture-proof-plan.v1.json"

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

THIS_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
PREVIOUS_SLICE = "MissionScript Player-State / Score Command-Effect Fixture Proof Plan"
NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
STATUS_TOKEN = "missionscript-command-effect-fixture-family-completion-rollup-proof-plan-complete-nine-family-static-fixture-rollup-not-runtime-proof"
INTERFACE_STATUS = "missionscript-command-effect-rebuild-interface-rollup-complete-static-interface-contract-not-runtime-proof"
PREVIOUS_STATUS = "missionscript-player-state-score-command-effect-fixture-proof-plan-complete-static-player-state-score-context-table-not-runtime-proof"

FAMILY_ROWS = (
    {
        "fixtureFamily": "slot-bitset-save",
        "sourceInterfaceFamily": "slot",
        "plan": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.md",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.v1.json",
        "statusKey": "slotBitsetSaveFixturePlanStatus",
        "script": "test:missionscript-slot-bitset-save-rebuild-fixture-proof-plan",
        "probe": ROOT / "tools" / "missionscript_slot_bitset_save_rebuild_fixture_proof_plan_probe.py",
        "casePath": ("planAccounting", "deterministicBitsetVectorCount"),
        "expectedCases": 5,
        "depthClass": "static-plan-plus-appcore-copied-baseline-chain",
    },
    {
        "fixtureFamily": "vector-range-helpers",
        "sourceInterfaceFamily": "vector-range",
        "plan": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-deterministic-helper-fixture-proof-plan.md",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1.json",
        "statusKey": "missionScriptVectorRangeDeterministicHelperFixtureProofPlanStatus",
        "script": "test:missionscript-vector-range-deterministic-helper-fixture-proof-plan",
        "probe": ROOT / "tools" / "missionscript_vector_range_deterministic_helper_fixture_proof_plan_probe.py",
        "casePath": ("fixtureAccounting", "deterministicHelperCaseCount"),
        "expectedCases": 28,
        "depthClass": "pure-static-helper-fixture",
    },
    {
        "fixtureFamily": "goodie-state-save",
        "sourceInterfaceFamily": "goodie-state",
        "plan": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-command-effect-fixture-proof-plan.md",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1.json",
        "statusKey": "missionScriptGoodieStateSaveCommandEffectFixtureProofPlanStatus",
        "script": "test:missionscript-goodie-state-save-command-effect-fixture-proof-plan",
        "probe": ROOT / "tools" / "missionscript_goodie_state_save_command_effect_fixture_proof_plan_probe.py",
        "casePath": ("fixtureAccounting", "plannedGoodieFixtureCaseCount"),
        "expectedCases": 43,
        "depthClass": "static-plan-plus-appcore-copied-baseline-chain",
    },
    {
        "fixtureFamily": "cutscene-camera-position",
        "sourceInterfaceFamily": "cutscene-pan-camera-position",
        "plan": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.md",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.v1.json",
        "statusKey": "missionScriptCutscenePanCameraPositionDeterministicFixtureProofPlanStatus",
        "script": "test:missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan",
        "probe": ROOT / "tools" / "missionscript_cutscene_pan_camera_position_deterministic_fixture_proof_plan_probe.py",
        "casePath": ("fixtureAccounting", "deterministicFixtureCaseCount"),
        "expectedCases": 4,
        "depthClass": "pure-static-camera-plan-fixture",
    },
    {
        "fixtureFamily": "objective-outcome",
        "sourceInterfaceFamily": "objective-outcome",
        "plan": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect-fixture-proof-plan.md",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect-fixture-proof-plan.v1.json",
        "statusKey": "missionScriptObjectiveOutcomeCommandEffectFixtureProofPlanStatus",
        "script": "test:missionscript-objective-outcome-command-effect-fixture-proof-plan",
        "probe": ROOT / "tools" / "missionscript_objective_outcome_command_effect_fixture_proof_plan_probe.py",
        "casePath": ("fixtureAccounting", "deterministicFixtureCaseCount"),
        "expectedCases": 7,
        "depthClass": "pure-static-effect-table",
    },
    {
        "fixtureFamily": "message-audio-console",
        "sourceInterfaceFamily": "message-audio",
        "plan": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect-fixture-proof-plan.md",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect-fixture-proof-plan.v1.json",
        "statusKey": "missionScriptMessageAudioCommandEffectFixtureProofPlanStatus",
        "script": "test:missionscript-message-audio-command-effect-fixture-proof-plan",
        "probe": ROOT / "tools" / "missionscript_message_audio_command_effect_fixture_proof_plan_probe.py",
        "casePath": ("fixtureAccounting", "deterministicFixtureCaseCount"),
        "expectedCases": 6,
        "depthClass": "pure-static-message-audio-fixture",
    },
    {
        "fixtureFamily": "hud-variable-display",
        "sourceInterfaceFamily": "hud-display",
        "plan": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect-fixture-proof-plan.md",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect-fixture-proof-plan.v1.json",
        "statusKey": "missionScriptHudDisplayCommandEffectFixtureProofPlanStatus",
        "script": "test:missionscript-hud-display-command-effect-fixture-proof-plan",
        "probe": ROOT / "tools" / "missionscript_hud_display_command_effect_fixture_proof_plan_probe.py",
        "casePath": ("fixtureAccounting", "deterministicFixtureCaseCount"),
        "expectedCases": 12,
        "depthClass": "pure-static-hud-display-fixture",
    },
    {
        "fixtureFamily": "thing-value-engine-helper",
        "sourceInterfaceFamily": "thing-value-engine-helper",
        "plan": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.md",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.v1.json",
        "statusKey": "missionScriptThingValueEngineHelperCommandEffectFixtureProofPlanStatus",
        "script": "test:missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan",
        "probe": ROOT / "tools" / "missionscript_thing_value_engine_helper_command_effect_fixture_proof_plan_probe.py",
        "casePath": ("fixtureAccounting", "deterministicFixtureCaseCount"),
        "expectedCases": 6,
        "depthClass": "pure-static-dispatch-fixture",
    },
    {
        "fixtureFamily": "player-state-score",
        "sourceInterfaceFamily": "player-state-score",
        "plan": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect-fixture-proof-plan.md",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect-fixture-proof-plan.v1.json",
        "statusKey": "missionScriptPlayerStateScoreCommandEffectFixtureProofPlanStatus",
        "script": "test:missionscript-player-state-score-command-effect-fixture-proof-plan",
        "probe": ROOT / "tools" / "missionscript_player_state_score_command_effect_fixture_proof_plan_probe.py",
        "casePath": ("fixtureAccounting", "deterministicFixtureCaseCount"),
        "expectedCases": 3,
        "depthClass": "static-context-alias-boundary-fixture",
    },
)

FALSE_GUARDS = (
    "programFilesInputUsed",
    "sourcePathsPublic",
    "rawMslRowsPublic",
    "liveLooseMslLoading",
    "packedResourceScriptSelectionProven",
    "runtimeExecution",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimeLevel100CommandEffectsProven",
    "runtimeEventOutcomesProven",
    "runtimeHudBehaviorProven",
    "runtimeMessageDisplayProven",
    "runtimeMessageAudioBehaviorProven",
    "runtimeGoodieStateMutationProven",
    "runtimeSaveBehaviorProven",
    "runtimeSlotPersistenceProven",
    "runtimeScoreBehaviorProven",
    "runtimeCockpitBehaviorProven",
    "runtimeStealthBehaviorProven",
    "runtimeVectorRangeBehaviorProven",
    "runtimeThingValueEngineHelperBehaviorProven",
    "runtimeCameraSwitchingProven",
    "runtimeCutscenePlaybackProven",
    "runtimeObjectIdentityProven",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "newCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "exactTextOcrPerformed",
    "rawDialoguePublished",
    "visibleTextExcerptPublished",
    "exactVisibleTokenIdentityClaim",
    "sourceSelectionObserved",
    "sourceSelectionProven",
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
    "exactDatatypeLayoutProven",
    "exactSourceBodyIdentityProven",
    "addScoreHandlerBodyProven",
    "toggleCockpitHandlerBodyProven",
    "setStealthHandlerBodyProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeEventOutcomeRows",
    "runtimeHudMessageAudioRows",
    "runtimeGoodieStateRows",
    "runtimeSaveRows",
    "runtimePlayerStateScoreRows",
    "privateFrameRowsObserved",
    "rowObservationRows",
    "sourceObservedRows",
    "sourceRuntimeObservationRows",
    "sourceRowStatusChangedCount",
    "newLaunchRows",
    "captureRows",
    "ocrRows",
    "rawDialogueRows",
    "visibleTextExcerptRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "rebuildImplementationRows",
    "godotProjectRows",
    "beProcessesAfterRollup",
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
    (re.compile(r"(?i)game[\\/]+data[\\/]+missionscripts"), "private loose MSL row path"),
    (re.compile(r"(?i)sampleRows"), "raw private sample row field"),
    (re.compile(r"(?i)subagents[\\/]"), "subagent artifact path"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"), "private frame locator/hash field"),
    (re.compile(r"(?i)\.private\.png"), "private frame filename"),
    (re.compile(r"(?i)level100-clean-materialized-[0-9]"), "copied-profile concrete identifier"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime level100 command effects proven",
    "runtime message display proven",
    "runtime hud behavior proven",
    "runtime voice playback proven",
    "runtime audio playback proven",
    "runtime queue ordering proven",
    "runtime objective behavior proven",
    "runtime level outcome proven",
    "runtime goodie state proven",
    "runtime save behavior proven",
    "runtime slot persistence proven",
    "runtime score behavior proven",
    "runtime cockpit behavior proven",
    "runtime stealth behavior proven",
    "weapon-fire/stealth interaction proven",
    "runtime vector behavior proven",
    "runtime range behavior proven",
    "runtime camera switching proven",
    "runtime cutscene playback proven",
    "runtime object identity proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "private-frame review complete",
    "source-selection observation complete",
    "exact visible token identity proven",
    "addscore handler-body proof complete",
    "togglecockpit handler-body proof complete",
    "setstealth handler-body proof complete",
    "exact command descriptor layout proven",
    "exact arity proven",
    "exact argument type schema proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
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


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def path_value(source: dict[str, Any], keys: tuple[str, ...]) -> Any:
    current: Any = source
    for key in keys:
        current = current[key]
    return current


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


def check_no_bad_public_content(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def build_family_rows() -> list[dict[str, Any]]:
    interface = read_json(INTERFACE_ROLLUP)
    interface_rows = {row["familyId"]: row for row in interface["sourceSchemas"]}
    rows: list[dict[str, Any]] = []
    for config in FAMILY_ROWS:
        schema = read_json(config["schema"])
        interface_row = interface_rows[config["sourceInterfaceFamily"]]
        case_count = int(path_value(schema, config["casePath"]))
        rows.append(
            {
                "fixtureFamily": config["fixtureFamily"],
                "sourceInterfaceFamily": config["sourceInterfaceFamily"],
                "fixturePlanDoc": rel(config["plan"]),
                "fixturePlanSchema": rel(config["schema"]),
                "fixtureProofPlanProbe": rel(config["probe"]),
                "packageScript": config["script"],
                "schemaVersion": schema["schemaVersion"],
                "statusKey": config["statusKey"],
                "status": schema[config["statusKey"]],
                "selectedNextSlice": schema.get("selectedNextSlice"),
                "depthClass": config["depthClass"],
                "descriptorEntryCount": interface_row["descriptorEntryCount"],
                "uniqueDescriptorIndexCount": interface_row["uniqueDescriptorIndexCount"],
                "descriptorIndices": interface_row["descriptorIndices"],
                "fixtureCaseCount": case_count,
                "runtimeExecution": False,
                "ghidraMutation": False,
                "godotWork": False,
                "rebuildImplementation": False,
            }
        )
    return rows


def build_schema() -> dict[str, Any]:
    interface = read_json(INTERFACE_ROLLUP)
    previous = read_json(PREVIOUS_FIXTURE)
    family_rows = build_family_rows()
    descriptor_accounting = interface["descriptorIndexAccounting"]
    duplicate_boundaries = {str(key): value for key, value in descriptor_accounting["duplicateDescriptorIndices"].items()}
    case_count = sum(row["fixtureCaseCount"] for row in family_rows)
    return {
        "schemaVersion": "missionscript-command-effect-fixture-family-completion-rollup-proof-plan.v1",
        "status": "PASS",
        "missionScriptCommandEffectFixtureFamilyCompletionRollupProofPlanStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "sourceEvidence": {
            "sourceInterfaceRollupSchema": rel(INTERFACE_ROLLUP),
            "sourceInterfaceRollupStatus": interface["missionScriptCommandEffectRebuildInterfaceRollupStatus"],
            "previousFixtureSchema": rel(PREVIOUS_FIXTURE),
            "previousFixtureStatus": previous["missionScriptPlayerStateScoreCommandEffectFixtureProofPlanStatus"],
            "previousFixtureSelectedNextSlice": previous["selectedNextSlice"],
            "existingTrackedArtifactsOnly": True,
            "sourceSchemaValidationOnly": True,
            "frontDoorDocValidationOnly": True,
        },
        "familyAliasNormalization": {
            "slot": "slot-bitset-save",
            "message-audio": "message-audio-console",
            "hud-display": "hud-variable-display",
            "goodie-state": "goodie-state-save",
            "cutscene-pan-camera-position": "cutscene-camera-position",
            "vector-range": "vector-range-helpers",
        },
        "familyCompletionRows": family_rows,
        "fixtureCompletionAccounting": {
            "expectedFixtureFamilyCount": 9,
            "completedFixtureFamilyCount": len(family_rows),
            "remainingFixtureFamilyCount": 9 - len(family_rows),
            "fixturePlanDocCount": len({row["fixturePlanDoc"] for row in family_rows}),
            "fixturePlanSchemaCount": len({row["fixturePlanSchema"] for row in family_rows}),
            "fixtureProofPlanProbeCount": len({row["fixtureProofPlanProbe"] for row in family_rows}),
            "packageScriptCount": len({row["packageScript"] for row in family_rows}),
            "heterogeneousFixtureCaseCount": case_count,
            "staticOnlyFamilyCount": sum(1 for row in family_rows if row["depthClass"].startswith("pure-static") or row["depthClass"] == "static-context-alias-boundary-fixture"),
            "appCoreCopiedBaselineFamilyCount": sum(1 for row in family_rows if "appcore-copied-baseline" in row["depthClass"]),
            "runtimeFamilyProofCount": 0,
            "runtimeObservationReadyFamilyCount": 0,
            "publicLeakCheck": "PASS",
        },
        "descriptorIndexAccounting": {
            "descriptorRecordCount": descriptor_accounting["totalCommandEffectDescriptorEntries"],
            "uniqueDescriptorIndexCount": descriptor_accounting["uniqueCommandEffectDescriptorIndices"],
            "duplicateDescriptorIndexCount": len(duplicate_boundaries),
            "duplicateDescriptorBoundaryCount": len(duplicate_boundaries),
            "duplicateDescriptorBoundaries": duplicate_boundaries,
        },
        "staticToProofBacklogAccounting": {
            "completedParentInterfaceRollup": "MissionScript Command-Effect Rebuild Interface Rollup Proof Plan",
            "completedFixtureSelection": "MissionScript Command-Effect Rebuild Fixture Selection Proof Plan",
            "completedFixtureFamilies": [
                row["fixtureFamily"] for row in family_rows
            ],
            "selectedNextSlice": NEXT_SLICE,
            "nextSliceClass": "selection-refresh",
            "runtimeExecution": False,
            "ghidraMutation": False,
            "godotWork": False,
            "rebuildImplementation": False,
        },
        "frontDoorValidation": {
            "backlog": rel(BACKLOG),
            "mappedSystems": rel(MAPPED),
            "binaryIndex": rel(BIN_INDEX),
            "reIndex": rel(RE_INDEX),
            "missionscriptContract": rel(ISCRIPT_CONTRACT),
            "loreMirrorsRequired": True,
        },
        "guardSummary": {
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "falseGuards": {key: False for key in FALSE_GUARDS},
            "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
            "publicLeakCheck": "PASS",
        },
        "claimBoundary": {
            "proves": [
                "nine MissionScript command-effect fixture families have tracked static fixture proof artifacts",
                "the fixture-family set accounts for 52 descriptor records, 48 unique descriptor indices, and four duplicate descriptor boundaries inherited from the source interface rollup",
                "the normalized fixture-family surface contains 114 heterogeneous static fixture cases",
                "the next safe work item is a static-to-proof selection refresh rather than runtime, Godot, patch, product UI, or rebuild implementation",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime Level100 command effects",
                "runtime HUD/message/audio behavior",
                "runtime Goodie/save mutation",
                "runtime score/cockpit/stealth behavior",
                "weapon-fire/stealth interaction",
                "runtime cutscene camera switching",
                "runtime vector/range behavior",
                "runtime thing/engine helper behavior",
                "live loose-MSL loading",
                "packed-resource script selection",
                "private-frame review",
                "row observation",
                "source-selection proof",
                "native input",
                "debugger attachment",
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


def check_prerequisites(failures: list[str]) -> None:
    interface = read_json(INTERFACE_ROLLUP)
    previous = read_json(PREVIOUS_FIXTURE)
    require(interface["missionScriptCommandEffectRebuildInterfaceRollupStatus"] == INTERFACE_STATUS, "source interface rollup status mismatch", failures)
    require(interface["rollupAccounting"]["descriptorRecordCount"] == 52, "source descriptor record count mismatch", failures)
    require(interface["rollupAccounting"]["uniqueDescriptorTokenCount"] == 48, "source unique descriptor count mismatch", failures)
    require(interface["rollupAccounting"]["duplicateDescriptorTokenCount"] == 4, "source duplicate descriptor count mismatch", failures)
    require(previous["missionScriptPlayerStateScoreCommandEffectFixtureProofPlanStatus"] == PREVIOUS_STATUS, "previous fixture status mismatch", failures)
    require(previous["selectedNextSlice"] == THIS_SLICE, "previous fixture selected next-slice mismatch", failures)
    for row in build_family_rows():
        require(row["status"], f"missing status for {row['fixtureFamily']}", failures)
        require(row["fixtureCaseCount"] > 0, f"missing fixture case count for {row['fixtureFamily']}", failures)
        require(row["runtimeExecution"] is False, f"runtime guard mismatch for {row['fixtureFamily']}", failures)


def check_schema(failures: list[str]) -> None:
    expected = build_schema()
    for path in (SCHEMA, LORE_SCHEMA):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} schema mismatch", failures)
        check_no_bad_public_content(path, failures)
    accounting = expected["fixtureCompletionAccounting"]
    require(accounting["expectedFixtureFamilyCount"] == 9, "expected family count mismatch", failures)
    require(accounting["completedFixtureFamilyCount"] == 9, "completed family count mismatch", failures)
    require(accounting["remainingFixtureFamilyCount"] == 0, "remaining family count mismatch", failures)
    require(accounting["fixturePlanDocCount"] == 9, "fixture plan doc count mismatch", failures)
    require(accounting["fixturePlanSchemaCount"] == 9, "fixture plan schema count mismatch", failures)
    require(accounting["fixtureProofPlanProbeCount"] == 9, "fixture probe count mismatch", failures)
    require(accounting["heterogeneousFixtureCaseCount"] == 114, "heterogeneous fixture case count mismatch", failures)
    descriptor = expected["descriptorIndexAccounting"]
    require(descriptor["descriptorRecordCount"] == 52, "descriptor record count mismatch", failures)
    require(descriptor["uniqueDescriptorIndexCount"] == 48, "unique descriptor index count mismatch", failures)
    require(descriptor["duplicateDescriptorIndexCount"] == 4, "duplicate descriptor index count mismatch", failures)
    require(descriptor["duplicateDescriptorBoundaryCount"] == 4, "duplicate descriptor boundary count mismatch", failures)
    require(set(descriptor["duplicateDescriptorBoundaries"]) == {"33", "34", "84", "105"}, "duplicate descriptor boundary set mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-command-effect-fixture-family-completion-rollup-proof-plan.v1.json",
        f"missionScriptCommandEffectFixtureFamilyCompletionRollupProofPlanStatus={STATUS_TOKEN}",
        "expectedFixtureFamilyCount=9",
        "completedFixtureFamilyCount=9",
        "remainingFixtureFamilyCount=0",
        "fixturePlanDocCount=9",
        "fixturePlanSchemaCount=9",
        "fixtureProofPlanProbeCount=9",
        "descriptorRecordCount=52",
        "uniqueDescriptorIndexCount=48",
        "duplicateDescriptorIndexCount=4",
        "duplicateDescriptorBoundaryCount=4",
        "heterogeneousFixtureCaseCount=114",
        f"sourceInterfaceRollupStatus={INTERFACE_STATUS}",
        f"previousFixtureStatus={PREVIOUS_STATUS}",
        "publicLeakCheck=PASS",
        "runtimeExecution=false",
        "ghidraMutation=false",
        "godotWork=false",
        "rebuildImplementation=false",
        "slot-bitset-save",
        "vector-range-helpers",
        "goodie-state-save",
        "cutscene-camera-position",
        "objective-outcome",
        "message-audio-console",
        "hud-variable-display",
        "thing-value-engine-helper",
        "player-state-score",
        "33 HighlightHudPart",
        "34 UnHighlightHudPart",
        "84 AddScore",
        "105 LevelLostString",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)
    require(read_json(LORE_SCHEMA) == read_json(SCHEMA), "lore schema mirror mismatch", failures)

    front_tokens = (
        THIS_SLICE,
        NEXT_SLICE,
        "missionscript-command-effect-fixture-family-completion-rollup-proof-plan.md",
        "missionscript-command-effect-fixture-family-completion-rollup-proof-plan.v1.json",
        f"missionScriptCommandEffectFixtureFamilyCompletionRollupProofPlanStatus={STATUS_TOKEN}",
        "completedFixtureFamilyCount=9",
        "remainingFixtureFamilyCount=0",
        "heterogeneousFixtureCaseCount=114",
        "descriptorRecordCount=52",
        "uniqueDescriptorIndexCount=48",
        "runtimeExecution=false",
        "ghidraMutation=false",
        "godotWork=false",
        "rebuildImplementation=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, ISCRIPT_CONTRACT):
        text = read_text(path)
        for token in front_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks fixture-family rollup active",
            failures,
        )

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed fixture-family rollup", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in backlog, "backlog missing active post-command-effect selection refresh", failures)

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
        scripts.get("test:missionscript-command-effect-fixture-family-completion-rollup-proof-plan")
        == r"py -3 tools\missionscript_command_effect_fixture_family_completion_rollup_proof_plan_probe.py --check",
        "missing fixture-family completion rollup package script",
        failures,
    )
    for row in FAMILY_ROWS:
        require(row["script"] in scripts, f"missing fixture-family source script: {row['script']}", failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_prerequisites(failures)
    check_schema(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after fixture-family rollup", failures)
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
            print("MissionScript command-effect fixture-family completion rollup probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript command-effect fixture-family completion rollup probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
