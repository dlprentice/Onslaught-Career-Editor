#!/usr/bin/env python3
"""Validate MissionScript player-state/score fixture proof artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect-fixture-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect-fixture-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect-fixture-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_player_state_score_command_effect_fixture_proof_plan_2026-06-09.md"

PREVIOUS_FIXTURE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.v1.json"
PLAYER_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect.v1.json"
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

THIS_SLICE = "MissionScript Player-State / Score Command-Effect Fixture Proof Plan"
PREVIOUS_SLICE = "MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan"
NEXT_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
POST_ROLLUP_NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
STATUS_TOKEN = "missionscript-player-state-score-command-effect-fixture-proof-plan-complete-static-player-state-score-context-table-not-runtime-proof"
PREVIOUS_STATUS = "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan-complete-static-thing-engine-dispatch-table-not-runtime-proof"

DESCRIPTOR_ORDER = ("AddScore", "ToggleCockpit", "SetStealth")
DESCRIPTOR_INDICES = (84, 136, 137)
EXPECTED_CALL_COUNTS = {"AddScore": 15, "ToggleCockpit": 0, "SetStealth": 10}
EXPECTED_FILE_COUNTS = {"AddScore": 12, "ToggleCockpit": 0, "SetStealth": 4}
CASE_MODELS = {
    "AddScore": {
        "contextKind": "alias-boundary",
        "fixtureCaseId": "AddScore-descriptor-corpus-alias-boundary",
        "staticContextAnchors": ["0x00534410 IScript__SecondaryObjectiveComplete", "CGame::IncScore"],
        "boundary": "descriptor/name/corpus context only; raw entry collides with objective/outcome naming and no score handler-body proof is claimed",
    },
    "ToggleCockpit": {
        "contextKind": "raw-label-source-context",
        "fixtureCaseId": "ToggleCockpit-raw-descriptor-source-context",
        "staticContextAnchors": ["&LAB_00533950", "CBattleEngine::ToggleCockpit"],
        "boundary": "raw descriptor label plus source context only; no handler-body bridge or cockpit runtime behavior is claimed",
    },
    "SetStealth": {
        "contextKind": "raw-label-corpus-source-context",
        "fixtureCaseId": "SetStealth-raw-descriptor-corpus-source-context",
        "staticContextAnchors": ["&LAB_00533980", "CBattleEngine__HandleCloak", "mStealth", "mDesiredStealth"],
        "boundary": "raw descriptor label plus aggregate corpus/source context only; no handler-body bridge, stealth runtime behavior, or weapon-fire interaction is claimed",
    },
}

FALSE_GUARDS = (
    "programFilesInputUsed",
    "sourcePathsPublic",
    "rawMslRowsPublic",
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
    "runtimePlayerStateScoreBehaviorProven",
    "runtimeScoreBehaviorProven",
    "runtimeCockpitBehaviorProven",
    "runtimeStealthBehaviorProven",
    "runtimeWeaponFireStealthInteractionProven",
    "runtimeRankingBehaviorProven",
    "runtimeCareerSaveBehaviorProven",
    "runtimeGoodieStateBehaviorProven",
    "runtimeObjectiveOutcomeBehaviorProven",
    "runtimeHandlerBodyBridgeProven",
    "addScoreHandlerBodyProven",
    "toggleCockpitHandlerBodyProven",
    "setStealthHandlerBodyProven",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "exactTextOcrPerformed",
    "rawDialoguePublished",
    "visibleTextExcerptPublished",
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
    "exactDatatypeLayoutProven",
    "exactPlayerStateLayoutProven",
    "exactCGameLayoutProven",
    "exactBattleEngineLayoutProven",
    "exactSourceBodyIdentityProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimePlayerStateScoreRows",
    "runtimeScoreRows",
    "runtimeCockpitRows",
    "runtimeStealthRows",
    "runtimeWeaponFireStealthRows",
    "runtimeRankingRows",
    "runtimeCareerSaveRows",
    "runtimeHandlerBodyRows",
    "addScoreHandlerBodyRows",
    "toggleCockpitHandlerBodyRows",
    "setStealthHandlerBodyRows",
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
    (re.compile(r"(?i)game[\\/]+data[\\/]+missionscripts"), "private loose MSL row path"),
    (re.compile(r"(?i)sampleRows"), "raw private sample row field"),
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
    "runtime player-state behavior proven",
    "runtime score behavior proven",
    "runtime cockpit behavior proven",
    "runtime stealth behavior proven",
    "weapon-fire/stealth interaction proven",
    "runtime ranking/career/save behavior proven",
    "addscore handler-body proof complete",
    "togglecockpit handler-body proof complete",
    "setstealth handler-body proof complete",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact descriptor layout proven",
    "exact arity proven",
    "exact argument type schema proven",
    "exact player-state layout proven",
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


def fixture_selection_row(fixture_selection: dict[str, Any]) -> dict[str, Any]:
    return next(row for row in fixture_selection["candidateRanking"] if row["family"] == "player-state-score")


def aggregate_usage(player_static: dict[str, Any]) -> dict[str, dict[str, int]]:
    source_counts = player_static["looseMslUsage"]["directNonCommentCounts"]
    return {
        command: {
            "calls": int(source_counts[command]["calls"]),
            "files": int(source_counts[command]["files"]),
        }
        for command in DESCRIPTOR_ORDER
    }


def context_fixture_cases(player_static: dict[str, Any]) -> list[dict[str, Any]]:
    records = player_static["descriptorRecords"]
    usage = aggregate_usage(player_static)
    cases: list[dict[str, Any]] = []
    for command in DESCRIPTOR_ORDER:
        record = records[command]
        model = CASE_MODELS[command]
        cases.append(
            {
                "id": model["fixtureCaseId"],
                "command": command,
                "descriptorIndex": record["index"],
                "recordAddress": record["recordAddress"],
                "observedNameSymbol": record["observedNameSymbol"],
                "rawEntryValue": record["rawEntryValue"],
                "nonzeroRawShape": record["nonzeroRawShape"],
                "contextKind": model["contextKind"],
                "staticContextAnchors": model["staticContextAnchors"],
                "directNonCommentLooseMslRows": usage[command]["calls"],
                "directNonCommentLooseMslFiles": usage[command]["files"],
                "boundary": model["boundary"],
                "staticContextOnly": True,
                "handlerBodyProven": False,
                "runtimeCommandEffectProven": False,
                "runtimePlayerStateBehaviorProven": False,
                "exactPlayerStateLayoutProven": False,
            }
        )
    return cases


def build_schema() -> dict[str, Any]:
    previous = read_json(PREVIOUS_FIXTURE)
    player_static = read_json(PLAYER_STATIC)
    fixture_selection = read_json(FIXTURE_SELECTION)
    selection = fixture_selection_row(fixture_selection)
    usage = aggregate_usage(player_static)
    cases = context_fixture_cases(player_static)
    return {
        "schemaVersion": "missionscript-player-state-score-command-effect-fixture-proof-plan.v1",
        "status": "PASS",
        "missionScriptPlayerStateScoreCommandEffectFixtureProofPlanStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "player-state-score",
        "selectedFixturePath": "player-state-score-descriptor-alias-boundary-table",
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "fixtureAccounting": {
            "sourceSchemaCount": 3,
            "descriptorIndices": list(DESCRIPTOR_INDICES),
            "descriptorRecordCount": len(player_static["descriptorRecords"]),
            "descriptorContextCaseCount": len(cases),
            "staticContextFixtureCaseCount": len(cases),
            "deterministicFixtureCaseCount": len(cases),
            "aliasBoundaryCaseCount": sum(1 for row in cases if row["contextKind"] == "alias-boundary"),
            "rawLabelOnlyCaseCount": sum(1 for row in cases if row["contextKind"].startswith("raw-label")),
            "sourceContextFamilyCount": 3,
            "handlerBodyProvenCount": 0,
            "deterministicRuntimeEffectCaseCount": 0,
            "totalStaticCommandStepCount": len(cases),
            "effectAssertionCount": len(cases) * 3,
            "directNonCommentLooseMslRows": sum(row["calls"] for row in usage.values()),
            "directNonCommentLooseMslFiles": sum(row["files"] for row in usage.values()),
            "commandWithCorpusRows": sum(1 for row in usage.values() if row["calls"] > 0),
            "zeroCorpusCommandCount": sum(1 for row in usage.values() if row["calls"] == 0),
            "addScoreCallRows": usage["AddScore"]["calls"],
            "toggleCockpitCallRows": usage["ToggleCockpit"]["calls"],
            "setStealthCallRows": usage["SetStealth"]["calls"],
            "addScoreFileRows": usage["AddScore"]["files"],
            "toggleCockpitFileRows": usage["ToggleCockpit"]["files"],
            "setStealthFileRows": usage["SetStealth"]["files"],
            "sourceEvidenceWaveCount": len(player_static["source"]["evidenceWaves"]),
            "fixtureSelectionOriginalRank": selection["rank"],
            "fixtureSelectionOriginalDecision": selection["decision"],
            "previousFixtureStatus": previous["missionScriptThingValueEngineHelperCommandEffectFixtureProofPlanStatus"],
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "publicLeakCheck": "PASS",
        },
        "sourceEvidence": {
            "previousFixture": {
                "schema": "reverse-engineering/binary-analysis/missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.v1.json",
                "status": previous["missionScriptThingValueEngineHelperCommandEffectFixtureProofPlanStatus"],
                "selectedNextSlice": previous["selectedNextSlice"],
            },
            "playerStateScoreStaticProof": {
                "schema": "reverse-engineering/binary-analysis/missionscript-player-state-score-command-effect.v1.json",
                "status": player_static["status"],
                "descriptorIndices": list(DESCRIPTOR_INDICES),
                "descriptorTokens": list(DESCRIPTOR_ORDER),
                "looseMslUsageAggregate": usage,
                "aliasBoundary": player_static["aliasAndRawEntryBoundaries"]["AddScore"],
                "sourceContextFamilies": ["score", "cockpit", "stealth"],
                "boundary": "static descriptor/corpus/source-context bridge only; runtime player-state, score, cockpit, stealth, and handler-body behavior remains unproven",
            },
            "fixtureSelection": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-fixture-selection.v1.json",
                "originalRank": selection["rank"],
                "originalDecision": selection["decision"],
            },
        },
        "fixtureModel": {
            "playerStateScoreModel": "finite descriptor/corpus/source-context cases for score, cockpit, and stealth commands",
            "descriptorContextModel": "raw descriptor records remain context-only because exact descriptor layout and runtime effects are unproven",
            "selectedRuntimeCommands": list(DESCRIPTOR_ORDER),
            "excludedCases": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime score behavior",
                "runtime cockpit behavior",
                "runtime stealth behavior",
                "weapon-fire/stealth interaction",
                "runtime ranking/career/save behavior",
                "handler-body proof for AddScore, ToggleCockpit, or SetStealth",
                "live loose-MSL loading",
                "packed-resource script selection",
            ],
        },
        "contextFixtureCases": cases,
        "deferredProofGate": {
            "selectedNextSlice": NEXT_SLICE,
            "runtimeExecution": False,
            "beLaunch": False,
            "sourcePathsPublic": False,
            "rawMslRowsPublic": False,
            "liveLooseMslLoading": False,
            "packedResourceScriptSelectionProven": False,
            "sourceBaselineRead": False,
            "privateArtifactMaterialized": False,
            "copiedFileMutation": False,
            "ghidraMutation": False,
            "godotWork": False,
            "rebuildImplementation": False,
            "requiresSeparateProofForRuntimeCommandEffects": True,
            "requiresSeparateProofForHandlerBodyBridge": True,
            "requiresSeparateProofForWeaponFireStealthInteraction": True,
        },
        "guardSummary": {
            "falseGuards": {key: False for key in FALSE_GUARDS},
            "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        },
        "claimBoundary": {
            "proves": [
                "three finite static player-state/score context fixture cases tied to saved descriptor rows",
                "one AddScore alias-boundary fixture case preserving the 0x00534410 objective/outcome conflict",
                "two raw-label source-context fixture cases for ToggleCockpit and SetStealth",
                "aggregate command-token counts are preserved without publishing raw loose-MSL sample rows",
                "the fixture table is consolidated without runtime, Ghidra, patch, Godot, product UI, or rebuild claims",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime score behavior",
                "runtime cockpit behavior",
                "runtime stealth behavior",
                "weapon-fire/stealth interaction",
                "runtime ranking/career/save behavior",
                "AddScore handler-body proof",
                "ToggleCockpit handler-body proof",
                "SetStealth handler-body proof",
                "live loose-MSL loading",
                "packed-resource script selection",
                "exact command descriptor layout",
                "exact command arity",
                "exact argument type schema",
                "exact datatype layout",
                "exact player-state layout",
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
    require(actual == expected, "schema is not regenerated from current player-state/score fixture evidence", failures)
    accounting = actual["fixtureAccounting"]
    require(accounting["descriptorIndices"] == list(DESCRIPTOR_INDICES), "descriptor index list mismatch", failures)
    require(accounting["descriptorRecordCount"] == 3, "descriptor record count mismatch", failures)
    require(accounting["descriptorContextCaseCount"] == 3, "descriptor context count mismatch", failures)
    require(accounting["staticContextFixtureCaseCount"] == 3, "static context fixture count mismatch", failures)
    require(accounting["deterministicFixtureCaseCount"] == 3, "deterministic fixture count mismatch", failures)
    require(accounting["aliasBoundaryCaseCount"] == 1, "alias boundary count mismatch", failures)
    require(accounting["rawLabelOnlyCaseCount"] == 2, "raw-label count mismatch", failures)
    require(accounting["sourceContextFamilyCount"] == 3, "source context family count mismatch", failures)
    require(accounting["handlerBodyProvenCount"] == 0, "handler-body proven count mismatch", failures)
    require(accounting["deterministicRuntimeEffectCaseCount"] == 0, "runtime effect count mismatch", failures)
    require(accounting["totalStaticCommandStepCount"] == 3, "static command step count mismatch", failures)
    require(accounting["effectAssertionCount"] == 9, "effect assertion count mismatch", failures)
    require(accounting["directNonCommentLooseMslRows"] == 25, "loose MSL aggregate count mismatch", failures)
    require(accounting["directNonCommentLooseMslFiles"] == 16, "loose MSL file aggregate mismatch", failures)
    require(accounting["commandWithCorpusRows"] == 2, "command-with-corpus count mismatch", failures)
    require(accounting["zeroCorpusCommandCount"] == 1, "zero-corpus command count mismatch", failures)
    require(accounting["addScoreCallRows"] == 15, "AddScore row count mismatch", failures)
    require(accounting["toggleCockpitCallRows"] == 0, "ToggleCockpit row count mismatch", failures)
    require(accounting["setStealthCallRows"] == 10, "SetStealth row count mismatch", failures)
    require(accounting["addScoreFileRows"] == 12, "AddScore file count mismatch", failures)
    require(accounting["toggleCockpitFileRows"] == 0, "ToggleCockpit file count mismatch", failures)
    require(accounting["setStealthFileRows"] == 4, "SetStealth file count mismatch", failures)
    require(accounting["sourceEvidenceWaveCount"] == 5, "source evidence wave count mismatch", failures)
    require(accounting["fixtureSelectionOriginalRank"] == 9, "fixture selection rank mismatch", failures)
    require(accounting["fixtureSelectionOriginalDecision"] == "deferred", "fixture selection decision mismatch", failures)
    require(accounting["previousFixtureStatus"] == PREVIOUS_STATUS, "previous fixture status mismatch", failures)
    require(accounting["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    for case in actual["contextFixtureCases"]:
        require(case["command"] in DESCRIPTOR_ORDER, f"unknown context case command: {case['command']}", failures)
        require(case["descriptorIndex"] == actual["sourceEvidence"]["playerStateScoreStaticProof"]["descriptorIndices"][DESCRIPTOR_ORDER.index(case["command"])], f"descriptor index mismatch: {case['command']}", failures)
        require(case["directNonCommentLooseMslRows"] == EXPECTED_CALL_COUNTS[case["command"]], f"loose MSL count mismatch: {case['command']}", failures)
        require(case["directNonCommentLooseMslFiles"] == EXPECTED_FILE_COUNTS[case["command"]], f"loose MSL file count mismatch: {case['command']}", failures)
        require(case["staticContextOnly"] is True, f"static-context guard mismatch: {case['command']}", failures)
        require(case["handlerBodyProven"] is False, f"handler-body guard mismatch: {case['command']}", failures)
        require(case["runtimeCommandEffectProven"] is False, f"runtime effect guard mismatch: {case['command']}", failures)
        require(case["runtimePlayerStateBehaviorProven"] is False, f"player-state guard mismatch: {case['command']}", failures)
        require(case["exactPlayerStateLayoutProven"] is False, f"layout guard mismatch: {case['command']}", failures)

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
    previous = read_json(PREVIOUS_FIXTURE)
    player_static = read_json(PLAYER_STATIC)
    fixture_selection = read_json(FIXTURE_SELECTION)
    require(previous["missionScriptThingValueEngineHelperCommandEffectFixtureProofPlanStatus"] == PREVIOUS_STATUS, "previous fixture status mismatch", failures)
    require(previous["selectedNextSlice"] == THIS_SLICE, "previous fixture selected next slice mismatch", failures)
    require(player_static["status"] == "PASS", "player-state static schema status mismatch", failures)
    require(tuple(player_static["descriptorRecords"].keys()) == DESCRIPTOR_ORDER, "descriptor key order mismatch", failures)
    require(tuple(player_static["descriptorRecords"][key]["index"] for key in player_static["descriptorRecords"]) == DESCRIPTOR_INDICES, "descriptor index order mismatch", failures)
    usage = aggregate_usage(player_static)
    for command in DESCRIPTOR_ORDER:
        require(usage[command]["calls"] == EXPECTED_CALL_COUNTS[command], f"{command} direct count mismatch", failures)
        require(usage[command]["files"] == EXPECTED_FILE_COUNTS[command], f"{command} file count mismatch", failures)
    require(sum(row["calls"] for row in usage.values()) == 25, "loose MSL total mismatch", failures)
    selection = fixture_selection_row(fixture_selection)
    require(selection["rank"] == 9, "fixture selection rank mismatch", failures)
    require(selection["decision"] == "deferred", "fixture selection decision mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-player-state-score-command-effect-fixture-proof-plan.v1.json",
        f"missionScriptPlayerStateScoreCommandEffectFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=player-state-score",
        "selectedFixturePath=player-state-score-descriptor-alias-boundary-table",
        "descriptorIndices=84/136/137",
        "descriptorRecordCount=3",
        "descriptorContextCaseCount=3",
        "staticContextFixtureCaseCount=3",
        "deterministicFixtureCaseCount=3",
        "aliasBoundaryCaseCount=1",
        "rawLabelOnlyCaseCount=2",
        "sourceContextFamilyCount=3",
        "handlerBodyProvenCount=0",
        "deterministicRuntimeEffectCaseCount=0",
        "totalStaticCommandStepCount=3",
        "effectAssertionCount=9",
        "directNonCommentLooseMslRows=25",
        "directNonCommentLooseMslFiles=16",
        "commandWithCorpusRows=2",
        "zeroCorpusCommandCount=1",
        "addScoreCallRows=15",
        "toggleCockpitCallRows=0",
        "setStealthCallRows=10",
        "addScoreFileRows=12",
        "toggleCockpitFileRows=0",
        "setStealthFileRows=4",
        "fixtureSelectionOriginalRank=9",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "AddScore",
        "ToggleCockpit",
        "SetStealth",
        "0x0064e350",
        "0x0064f050",
        "0x0064f090",
        "IScript__Unk_00534410",
        "&LAB_00533950",
        "&LAB_00533980",
        "0x00534410 IScript__SecondaryObjectiveComplete",
        "CGame::IncScore",
        "CBattleEngine::ToggleCockpit",
        "CBattleEngine__HandleCloak",
        "mStealth",
        "mDesiredStealth",
        "runtimeExecution=false",
        "beLaunch=false",
        "sourcePathsPublic=false",
        "rawMslRowsPublic=false",
        "liveLooseMslLoading=false",
        "packedResourceScriptSelectionProven=false",
        "ghidraMutation=false",
        "godotWork=false",
        "rebuildImplementation=false",
        "runtimeObservationRows=0",
        "missionScriptRuntimeEvidenceRows=0",
        "runtimeCommandEffectRows=0",
        "runtimePlayerStateScoreRows=0",
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
        "missionscript-player-state-score-command-effect-fixture-proof-plan.md",
        "missionscript-player-state-score-command-effect-fixture-proof-plan.v1.json",
        f"missionScriptPlayerStateScoreCommandEffectFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=player-state-score",
        "selectedFixturePath=player-state-score-descriptor-alias-boundary-table",
        "selectedNextSlice=MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan",
        "descriptorContextCaseCount=3",
        "deterministicFixtureCaseCount=3",
        "aliasBoundaryCaseCount=1",
        "handlerBodyProvenCount=0",
        "directNonCommentLooseMslRows=25",
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
            f"{path.relative_to(ROOT)} still marks Player-State / Score fixture active",
            failures,
        )

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed Player-State / Score fixture lane", failures)
    require(
        f"Completed {NEXT_SLICE}" in backlog,
        "backlog missing completed fixture-family completion rollup follow-up lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog,
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
        scripts.get("test:missionscript-player-state-score-command-effect-fixture-proof-plan")
        == r"py -3 tools\missionscript_player_state_score_command_effect_fixture_proof_plan_probe.py --check",
        "missing package Player-State / Score fixture proof-plan test script",
        failures,
    )
    for script in (
        "test:missionscript-player-state-score-command-effect-static",
        "test:missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan",
        "test:missionscript-command-effect-fixture-selection",
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
        require(no_bea_process_running(), "BEA.exe process is running after Player-State / Score fixture proof", failures)
        if failures:
            print("MissionScript Player-State / Score fixture proof-plan probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript Player-State / Score fixture proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
