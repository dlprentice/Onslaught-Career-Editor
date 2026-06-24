#!/usr/bin/env python3
"""Validate MissionScript HUD/display deterministic fixture proof artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect-fixture-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect-fixture-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect-fixture-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_hud_display_command_effect_fixture_proof_plan_2026-06-09.md"

PREVIOUS_FIXTURE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect-fixture-proof-plan.v1.json"
HUD_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect.v1.json"
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

THIS_SLICE = "MissionScript HUD / Display Command-Effect Fixture Proof Plan"
PREVIOUS_SLICE = "MissionScript Message/Audio Command-Effect Fixture Proof Plan"
NEXT_SLICE = "MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan"
NEXT_ACTIVE_SLICE = "MissionScript Player-State / Score Command-Effect Fixture Proof Plan"
COMPLETION_ROLLUP_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
POST_ROLLUP_NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
STATUS_TOKEN = "missionscript-hud-display-command-effect-fixture-proof-plan-complete-static-hud-variable-display-effect-table-not-runtime-proof"
PREVIOUS_STATUS = "missionscript-message-audio-command-effect-fixture-proof-plan-complete-static-message-audio-console-effect-table-not-runtime-proof"

DESCRIPTOR_ORDER = (
    "HighlightHudPart",
    "UnHighlightHudPart",
    "InitVariable",
    "SetVariable",
    "ShutdownVariable",
)
DESCRIPTOR_INDICES = (33, 34, 75, 76, 77)
EXPECTED_CALL_COUNTS = {
    "HighlightHudPart": 13,
    "UnHighlightHudPart": 13,
    "InitVariable": 77,
    "SetVariable": 146,
    "ShutdownVariable": 26,
}
EXPECTED_FILE_COUNTS = {
    "HighlightHudPart": 2,
    "UnHighlightHudPart": 2,
    "InitVariable": 41,
    "SetVariable": 45,
    "ShutdownVariable": 18,
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
    "runtimeHudBehaviorProven",
    "runtimeHudHighlightProven",
    "visibleHudFlashingProven",
    "runtimeVariableDisplayProven",
    "runtimeVariableLifecycleProven",
    "messageOverlayBehaviorProven",
    "renderOrderingProven",
    "runtimeTextLookupProven",
    "runtimeHudLayoutProven",
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
    "exactHudLayoutProven",
    "exactHudComponentLayoutProven",
    "exactVariableDisplayLayoutProven",
    "exactWorldTextLayoutProven",
    "handlerBodySemanticsProven",
    "staticCallPathToHudFunctionsProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeHudRows",
    "runtimeHudHighlightRows",
    "runtimeVariableDisplayRows",
    "runtimeVariableLifecycleRows",
    "visibleHudFlashRows",
    "messageOverlayRows",
    "renderOrderingRows",
    "runtimeTextLookupRows",
    "runtimeHudLayoutRows",
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
    "runtime hud behavior proven",
    "runtime hud highlight proven",
    "visible hud flashing proven",
    "runtime variable display proven",
    "runtime variable lifecycle proven",
    "message overlay behavior proven",
    "render ordering proven",
    "runtime text lookup proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "handler-body semantics proven",
    "static call path to hud functions proven",
    "exact descriptor layout proven",
    "exact arity proven",
    "exact argument type schema proven",
    "exact hud layout proven",
    "exact hud component layout proven",
    "exact variable display layout proven",
    "exact world text layout proven",
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


def descriptor_context_cases(static_schema: dict[str, Any]) -> list[dict[str, Any]]:
    records = static_schema["descriptorRecords"]
    return [
        {
            "command": command,
            "descriptorIndex": records[command]["index"],
            "recordAddress": records[command]["recordAddress"],
            "rawEntryValue": records[command]["rawEntryValue"],
            "nonzeroRawShape": records[command]["nonzeroRawShape"],
            "descriptorContextOnly": True,
            "handlerBodySemanticsProven": False,
            "runtimeHudBehaviorProven": False,
            "exactDescriptorLayoutProven": False,
            "exactCommandArityProven": False,
        }
        for command in DESCRIPTOR_ORDER
    ]


def hud_part_toggle_cases(static_schema: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": f"{name}-highlight-unhighlight-static-toggle",
            "hudPartConstant": name,
            "hudPartValue": value,
            "highlightDescriptorIndex": static_schema["descriptorRecords"]["HighlightHudPart"]["index"],
            "unhighlightDescriptorIndex": static_schema["descriptorRecords"]["UnHighlightHudPart"]["index"],
            "expectedCommandPair": ["HighlightHudPart", "UnHighlightHudPart"],
            "finiteEnumOnly": True,
            "runtimeHudHighlightProven": False,
            "visibleHudFlashingProven": False,
        }
        for name, value in static_schema["hudConstants"].items()
    ]


def variable_lifecycle_cases(static_schema: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for index, (name, value) in enumerate(static_schema["variableTypes"].items(), start=1):
        text_seed = 600 + index
        cases.append(
            {
                "id": f"{name}-init-set-shutdown-static-lifecycle",
                "variableType": name,
                "variableTypeValue": value,
                "textIdSeed": text_seed,
                "setValueSeed": value * 10,
                "thresholdSeed": 0,
                "initDescriptorIndex": static_schema["descriptorRecords"]["InitVariable"]["index"],
                "setDescriptorIndex": static_schema["descriptorRecords"]["SetVariable"]["index"],
                "shutdownDescriptorIndex": static_schema["descriptorRecords"]["ShutdownVariable"]["index"],
                "expectedCommandSequence": ["InitVariable", "SetVariable", "ShutdownVariable"],
                "finiteFixtureOnly": True,
                "runtimeVariableDisplayProven": False,
                "runtimeVariableLifecycleProven": False,
            }
        )
    return cases


def build_schema() -> dict[str, Any]:
    previous = read_json(PREVIOUS_FIXTURE)
    static_schema = read_json(HUD_STATIC)
    fixture_selection = read_json(FIXTURE_SELECTION)
    descriptor_cases = descriptor_context_cases(static_schema)
    hud_cases = hud_part_toggle_cases(static_schema)
    variable_cases = variable_lifecycle_cases(static_schema)
    usage = static_schema["looseMslUsage"]["directNonCommentCounts"]
    return {
        "schemaVersion": "missionscript-hud-display-command-effect-fixture-proof-plan.v1",
        "status": "PASS",
        "missionScriptHudDisplayCommandEffectFixtureProofPlanStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "hud-variable-display",
        "selectedFixturePath": "hud-part-variable-display-effect-table",
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
            "descriptorRecordCount": len(static_schema["descriptorRecords"]),
            "descriptorContextCaseCount": len(descriptor_cases),
            "hudConstantCount": len(static_schema["hudConstants"]),
            "variableTypeCount": len(static_schema["variableTypes"]),
            "plannedHudPartToggleCaseCount": len(hud_cases),
            "plannedVariableLifecycleCaseCount": len(variable_cases),
            "deterministicFixtureCaseCount": len(hud_cases) + len(variable_cases),
            "hudCommandStepCount": len(hud_cases) * 2,
            "variableCommandStepCount": len(variable_cases) * 3,
            "totalStaticCommandStepCount": len(hud_cases) * 2 + len(variable_cases) * 3,
            "effectAssertionCount": len(hud_cases) * 2 + len(variable_cases) * 3,
            "duplicateDescriptorBoundaryCount": 2,
            "highlightHudPartCallRows": usage["HighlightHudPart"]["calls"],
            "unhighlightHudPartCallRows": usage["UnHighlightHudPart"]["calls"],
            "initVariableCallRows": usage["InitVariable"]["calls"],
            "setVariableCallRows": usage["SetVariable"]["calls"],
            "shutdownVariableCallRows": usage["ShutdownVariable"]["calls"],
            "highlightHudPartFileCount": usage["HighlightHudPart"]["files"],
            "unhighlightHudPartFileCount": usage["UnHighlightHudPart"]["files"],
            "initVariableFileCount": usage["InitVariable"]["files"],
            "setVariableFileCount": usage["SetVariable"]["files"],
            "shutdownVariableFileCount": usage["ShutdownVariable"]["files"],
            "hudStaticAnchorCount": len(static_schema["hudStaticBridge"]["anchors"]),
            "worldTextAnchorCount": len(static_schema["worldTextBridge"]["anchors"]),
            "fixtureSelectionOriginalRank": next(row["rank"] for row in fixture_selection["candidateRanking"] if row["family"] == "hud-variable-display"),
            "previousFixtureStatus": previous["missionScriptMessageAudioCommandEffectFixtureProofPlanStatus"],
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "publicLeakCheck": "PASS",
        },
        "sourceEvidence": {
            "previousFixture": {
                "schema": "reverse-engineering/binary-analysis/missionscript-message-audio-command-effect-fixture-proof-plan.v1.json",
                "status": previous["missionScriptMessageAudioCommandEffectFixtureProofPlanStatus"],
                "selectedNextSlice": previous["selectedNextSlice"],
            },
            "hudDisplayStaticProof": {
                "schema": "reverse-engineering/binary-analysis/missionscript-hud-display-command-effect.v1.json",
                "status": static_schema["status"],
                "descriptorIndices": list(DESCRIPTOR_INDICES),
                "hudConstants": static_schema["hudConstants"],
                "variableTypes": static_schema["variableTypes"],
                "looseMslUsage": {
                    command: {
                        "calls": usage[command]["calls"],
                        "files": usage[command]["files"],
                    }
                    for command in DESCRIPTOR_ORDER
                },
                "boundary": "static descriptor/corpus/HUD-context bridge only; runtime HUD/display behavior remains unproven",
            },
            "fixtureSelection": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-fixture-selection.v1.json",
                "originalRank": next(row["rank"] for row in fixture_selection["candidateRanking"] if row["family"] == "hud-variable-display"),
                "originalDecision": next(row["decision"] for row in fixture_selection["candidateRanking"] if row["family"] == "hud-variable-display"),
            },
        },
        "fixtureModel": {
            "hudPartEffectModel": "finite HUD part constants map to static HighlightHudPart/UnHighlightHudPart descriptor-pair cases",
            "variableDisplayEffectModel": "finite variable type constants map to static InitVariable/SetVariable/ShutdownVariable lifecycle cases",
            "descriptorContextModel": "raw descriptor entries remain context-only because handler-body semantics and exact descriptor layout are unproven",
            "selectedRuntimeCommands": list(DESCRIPTOR_ORDER),
            "excludedCases": [
                "runtime HUD behavior",
                "visible HUD flashing",
                "runtime variable display",
                "message overlay behavior",
                "render ordering",
                "handler-body semantics",
                "static call path from descriptor raw entries into CHud functions",
            ],
        },
        "deterministicHudPartToggleCases": hud_cases,
        "deterministicVariableLifecycleCases": variable_cases,
        "descriptorContextCases": descriptor_cases,
        "deferredProofGate": {
            "selectedNextSlice": NEXT_SLICE,
            "runtimeExecution": False,
            "beLaunch": False,
            "sourcePathsPublic": False,
            "rawMslRowsPublic": False,
            "sourceBaselineRead": False,
            "privateArtifactMaterialized": False,
            "copiedFileMutation": False,
            "ghidraMutation": False,
            "godotWork": False,
            "rebuildImplementation": False,
            "requiresSeparateProofForRuntimeHudOutput": True,
            "requiresSeparateProofForRuntimeVariableDisplay": True,
            "requiresSeparateProofForVisualBehavior": True,
        },
        "guardSummary": {
            "falseGuards": {key: False for key in FALSE_GUARDS},
            "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        },
        "claimBoundary": {
            "proves": [
                "six finite HUD part toggle fixture cases tied to saved static HUD descriptor rows",
                "six finite variable display lifecycle fixture cases tied to saved static variable descriptor rows",
                "five descriptor context rows tied to the HUD/display static schema",
                "HUD/frontend and world-text anchors are preserved as static planning context",
                "the HUD/display fixture table is consolidated without runtime, Ghidra, patch, Godot, product UI, or rebuild claims",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime HUD behavior",
                "runtime HUD highlighting",
                "visible HUD flashing",
                "runtime variable display",
                "runtime variable lifecycle",
                "message overlay behavior",
                "render ordering",
                "runtime text lookup",
                "live loose-MSL loading",
                "packed-resource script selection",
                "handler-body semantics",
                "static call path from descriptor raw entries into CHud functions",
                "exact command descriptor layout",
                "exact command arity",
                "exact argument type schema",
                "exact HUD layout",
                "exact HUD component layout",
                "exact variable display layout",
                "exact world-text layout",
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
    require(actual == expected, "schema is not regenerated from current HUD/display fixture evidence", failures)
    accounting = actual["fixtureAccounting"]
    require(accounting["descriptorIndices"] == list(DESCRIPTOR_INDICES), "descriptor index list mismatch", failures)
    require(accounting["descriptorRecordCount"] == 5, "descriptor record count mismatch", failures)
    require(accounting["descriptorContextCaseCount"] == 5, "descriptor context count mismatch", failures)
    require(accounting["hudConstantCount"] == 6, "HUD constant count mismatch", failures)
    require(accounting["variableTypeCount"] == 6, "variable type count mismatch", failures)
    require(accounting["plannedHudPartToggleCaseCount"] == 6, "HUD toggle case count mismatch", failures)
    require(accounting["plannedVariableLifecycleCaseCount"] == 6, "variable lifecycle case count mismatch", failures)
    require(accounting["deterministicFixtureCaseCount"] == 12, "deterministic fixture count mismatch", failures)
    require(accounting["hudCommandStepCount"] == 12, "HUD command step count mismatch", failures)
    require(accounting["variableCommandStepCount"] == 18, "variable command step count mismatch", failures)
    require(accounting["totalStaticCommandStepCount"] == 30, "total static command step count mismatch", failures)
    require(accounting["effectAssertionCount"] == 30, "effect assertion count mismatch", failures)
    require(accounting["duplicateDescriptorBoundaryCount"] == 2, "duplicate descriptor boundary count mismatch", failures)
    require(accounting["highlightHudPartCallRows"] == 13, "HighlightHudPart row count mismatch", failures)
    require(accounting["unhighlightHudPartCallRows"] == 13, "UnHighlightHudPart row count mismatch", failures)
    require(accounting["initVariableCallRows"] == 77, "InitVariable row count mismatch", failures)
    require(accounting["setVariableCallRows"] == 146, "SetVariable row count mismatch", failures)
    require(accounting["shutdownVariableCallRows"] == 26, "ShutdownVariable row count mismatch", failures)
    require(accounting["highlightHudPartFileCount"] == 2, "HighlightHudPart file count mismatch", failures)
    require(accounting["unhighlightHudPartFileCount"] == 2, "UnHighlightHudPart file count mismatch", failures)
    require(accounting["initVariableFileCount"] == 41, "InitVariable file count mismatch", failures)
    require(accounting["setVariableFileCount"] == 45, "SetVariable file count mismatch", failures)
    require(accounting["shutdownVariableFileCount"] == 18, "ShutdownVariable file count mismatch", failures)
    require(accounting["hudStaticAnchorCount"] == 9, "HUD static anchor count mismatch", failures)
    require(accounting["worldTextAnchorCount"] == 5, "world-text anchor count mismatch", failures)
    require(accounting["fixtureSelectionOriginalRank"] == 7, "fixture selection original rank mismatch", failures)
    require(accounting["previousFixtureStatus"] == PREVIOUS_STATUS, "previous fixture status mismatch", failures)
    require(accounting["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    for case in actual["deterministicHudPartToggleCases"]:
        require(case["expectedCommandPair"] == ["HighlightHudPart", "UnHighlightHudPart"], f"HUD command pair mismatch: {case['id']}", failures)
        require(case["finiteEnumOnly"] is True, f"HUD finite guard mismatch: {case['id']}", failures)
        require(case["runtimeHudHighlightProven"] is False, f"HUD runtime guard mismatch: {case['id']}", failures)
        require(case["visibleHudFlashingProven"] is False, f"HUD visible guard mismatch: {case['id']}", failures)
    for case in actual["deterministicVariableLifecycleCases"]:
        require(case["expectedCommandSequence"] == ["InitVariable", "SetVariable", "ShutdownVariable"], f"variable sequence mismatch: {case['id']}", failures)
        require(case["finiteFixtureOnly"] is True, f"variable finite guard mismatch: {case['id']}", failures)
        require(case["runtimeVariableDisplayProven"] is False, f"variable display guard mismatch: {case['id']}", failures)
        require(case["runtimeVariableLifecycleProven"] is False, f"variable lifecycle guard mismatch: {case['id']}", failures)
    for case in actual["descriptorContextCases"]:
        require(case["descriptorContextOnly"] is True, f"descriptor context guard mismatch: {case['command']}", failures)
        require(case["handlerBodySemanticsProven"] is False, f"handler semantics guard mismatch: {case['command']}", failures)

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
    static_schema = read_json(HUD_STATIC)
    fixture_selection = read_json(FIXTURE_SELECTION)
    require(previous["missionScriptMessageAudioCommandEffectFixtureProofPlanStatus"] == PREVIOUS_STATUS, "previous fixture status mismatch", failures)
    require(previous["selectedNextSlice"] == THIS_SLICE, "previous fixture selected next slice mismatch", failures)
    require(static_schema["status"] == "PASS", "HUD/display static schema status mismatch", failures)
    require(tuple(static_schema["descriptorRecords"].keys()) == DESCRIPTOR_ORDER, "descriptor key order mismatch", failures)
    require(tuple(static_schema["descriptorRecords"][key]["index"] for key in static_schema["descriptorRecords"]) == DESCRIPTOR_INDICES, "descriptor index order mismatch", failures)
    for command, expected in EXPECTED_CALL_COUNTS.items():
        usage = static_schema["looseMslUsage"]["directNonCommentCounts"][command]
        require(usage["calls"] == expected, f"{command} call count mismatch", failures)
        require(usage["files"] == EXPECTED_FILE_COUNTS[command], f"{command} file count mismatch", failures)
    require(len(static_schema["hudConstants"]) == 6, "HUD constant prerequisite mismatch", failures)
    require(len(static_schema["variableTypes"]) == 6, "variable type prerequisite mismatch", failures)
    require(next(row["rank"] for row in fixture_selection["candidateRanking"] if row["family"] == "hud-variable-display") == 7, "fixture selection rank mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-hud-display-command-effect-fixture-proof-plan.v1.json",
        f"missionScriptHudDisplayCommandEffectFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=hud-variable-display",
        "selectedFixturePath=hud-part-variable-display-effect-table",
        "descriptorIndices=33/34/75/76/77",
        "descriptorRecordCount=5",
        "descriptorContextCaseCount=5",
        "hudConstantCount=6",
        "variableTypeCount=6",
        "plannedHudPartToggleCaseCount=6",
        "plannedVariableLifecycleCaseCount=6",
        "deterministicFixtureCaseCount=12",
        "hudCommandStepCount=12",
        "variableCommandStepCount=18",
        "totalStaticCommandStepCount=30",
        "effectAssertionCount=30",
        "duplicateDescriptorBoundaryCount=2",
        "highlightHudPartCallRows=13",
        "unhighlightHudPartCallRows=13",
        "initVariableCallRows=77",
        "setVariableCallRows=146",
        "shutdownVariableCallRows=26",
        "hudStaticAnchorCount=9",
        "worldTextAnchorCount=5",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "HighlightHudPart",
        "UnHighlightHudPart",
        "InitVariable",
        "SetVariable",
        "ShutdownVariable",
        "0x0064d690",
        "0x0064d6d0",
        "0x0064e110",
        "0x0064e150",
        "0x0064e190",
        "&LAB_00535d70",
        "&LAB_00535e60",
        "&LAB_00536210",
        "&LAB_00536230",
        "&LAB_00536260",
        "CHud__SetHudComponent",
        "CHud__RenderOverlayForViewpoint",
        "CHudComponent__RenderPass",
        "CWorld__PushWorldTextSlot",
        "CWorld__UpdateWorldTextSlotTiming",
        "CWorld__ClearWorldTextSlot",
        "CWorld__GetWorldTextSlotTimerValue",
        "runtimeExecution=false",
        "beLaunch=false",
        "sourcePathsPublic=false",
        "rawMslRowsPublic=false",
        "privateFrameReviewPerformed=false",
        "exactTextOcrPerformed=false",
        "rawDialoguePublished=false",
        "ghidraMutation=false",
        "godotWork=false",
        "rebuildImplementation=false",
        "runtimeObservationRows=0",
        "missionScriptRuntimeEvidenceRows=0",
        "runtimeCommandEffectRows=0",
        "runtimeHudRows=0",
        "runtimeVariableDisplayRows=0",
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
        "missionscript-hud-display-command-effect-fixture-proof-plan.md",
        "missionscript-hud-display-command-effect-fixture-proof-plan.v1.json",
        f"missionScriptHudDisplayCommandEffectFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=hud-variable-display",
        "selectedNextSlice=MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan",
        "plannedHudPartToggleCaseCount=6",
        "plannedVariableLifecycleCaseCount=6",
        "deterministicFixtureCaseCount=12",
        "hudCommandStepCount=12",
        "variableCommandStepCount=18",
        "totalStaticCommandStepCount=30",
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
            f"{path.relative_to(ROOT)} still marks HUD/display fixture active",
            failures,
        )

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed HUD/display fixture lane", failures)
    require(
        f"Completed {NEXT_SLICE}" in backlog
        or f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in backlog,
        "backlog missing active-or-completed Thing Value / Engine Helper follow-up lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {NEXT_ACTIVE_SLICE}. Status: selected" in backlog
        or f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in backlog
        or f"Completed {NEXT_ACTIVE_SLICE}" in backlog,
        "backlog missing active-or-completed Thing Value or Player-State / Score follow-up lane",
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
        scripts.get("test:missionscript-hud-display-command-effect-fixture-proof-plan")
        == r"py -3 tools\missionscript_hud_display_command_effect_fixture_proof_plan_probe.py --check",
        "missing package HUD/display fixture proof-plan test script",
        failures,
    )
    for script in (
        "test:missionscript-hud-display-command-effect-static",
        "test:missionscript-message-audio-command-effect-fixture-proof-plan",
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
        require(no_bea_process_running(), "BEA.exe process is running after HUD/display fixture proof", failures)
        if failures:
            print("MissionScript HUD/display command-effect fixture proof-plan probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript HUD/display command-effect fixture proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
