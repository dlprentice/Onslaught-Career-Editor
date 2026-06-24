#!/usr/bin/env python3
"""Validate MissionScript cutscene camera/position deterministic fixture proof artifacts."""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_cutscene_pan_camera_position_deterministic_fixture_proof_plan_2026-06-09.md"

POST_GOODIE_SELECTION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-post-goodie-selection-refresh.v1.json"
CUTSCENE_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-command-effect.v1.json"
ROLLUP = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.v1.json"
FIXTURE_SELECTION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-selection.v1.json"
GETTHINGREF_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-getthingref-object-reference-static.v1.json"

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

THIS_SLICE = "MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan"
PREVIOUS_SLICE = "MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan"
NEXT_SLICE = "MissionScript Objective/Outcome Command-Effect Fixture Proof Plan"
STATUS_TOKEN = "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan-complete-static-finite-camera-plan-not-runtime-proof"
POST_GOODIE_STATUS = "missionscript-command-effect-post-goodie-selection-refresh-complete-cutscene-camera-position-selected"
STATIC_PROOF_SLICE = "MissionScript Cutscene Pan-Camera / Position Command-Effect Static Proof"
THING_VALUE_FIXTURE_SLICE = "MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan"
PLAYER_STATE_FIXTURE_SLICE = "MissionScript Player-State / Score Command-Effect Fixture Proof Plan"
COMPLETION_ROLLUP_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
POST_ROLLUP_NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"

DESCRIPTOR_INDICES = (65, 113, 114, 115)
DESCRIPTOR_ROWS = ("0x0064de90", "0x0064ea90", "0x0064ead0", "0x0064eb10")
HANDLER_ANCHORS = (
    "0x00533b70 IScript__Create3PointPanCamera",
    "0x00533eb0 IScript__Create4PointPanCamera",
)

POSITION_CASES = (
    ("fenrir-cutscene-pos1", "pos1", [-80.0, 20.0, -30.0]),
    ("fenrir-cutscene-pos2", "pos2", [0.0, 40.0, 60.0]),
    ("fenrir-cutscene-pos3", "pos3", [100.0, 20.0, 40.0]),
)

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
    "runtimeCameraSwitchingProven",
    "runtimeCutscenePlaybackProven",
    "runtimeVisibleCameraOutputProven",
    "runtimeObjectIdentityProven",
    "runtimeObjectLookupByNameProven",
    "runtimeCreatePositionBehaviorProven",
    "runtimePanCameraBehaviorProven",
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
    "exactCPositionDataTypeLayoutProven",
    "exactCPanCameraLayoutProven",
    "exactCBSplineLayoutProven",
    "exactCameraAbiProven",
    "goto4PointRuntimeHandlerMappingProven",
    "gotoPlayerCameraRuntimeHandlerMappingProven",
    "nanInfinityBehaviorProven",
    "signedZeroBehaviorProven",
    "subnormalBehaviorProven",
    "overflowBehaviorProven",
    "exactX87OrCrtRoundingParityProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeCameraRows",
    "runtimeCutsceneRows",
    "runtimeObjectLookupRows",
    "runtimeCreatePositionRows",
    "runtimePanCameraRows",
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
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"), "private frame locator/hash field"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime camera switching proven",
    "runtime cutscene playback proven",
    "runtime visible camera output proven",
    "runtime object identity proven",
    "runtime object lookup by name proven",
    "runtime createposition behavior proven",
    "runtime pancamera behavior proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact descriptor layout proven",
    "exact arity proven",
    "exact argument type schema proven",
    "exact cpositiondatatype layout proven",
    "exact cpancamera layout proven",
    "exact cbspline layout proven",
    "goto4pointpancamera runtime handler mapping proven",
    "gotoplayercamera runtime handler mapping proven",
    "nan/infinity behavior proven",
    "signed-zero behavior proven",
    "subnormal behavior proven",
    "overflow behavior proven",
    "exact x87/crt rounding parity proven",
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


def is_finite_vector(values: list[float]) -> bool:
    return all(math.isfinite(value) for value in values)


def position_cases() -> list[dict[str, Any]]:
    return [
        {
            "id": case_id,
            "sourceToken": token,
            "command": "CreatePosition",
            "descriptorIndex": 65,
            "recordAddress": "0x0064de90",
            "position": {"x": vector[0], "y": vector[1], "z": vector[2]},
            "expectedPayload": vector,
            "expectedPayloadReads": ["+0x04", "+0x08", "+0x0c"],
            "finiteOnly": is_finite_vector(vector),
        }
        for case_id, token, vector in POSITION_CASES
    ]


def camera_plan_cases() -> list[dict[str, Any]]:
    return [
        {
            "id": "fenrir-goto3point-pan-camera",
            "command": "Goto3PointPanCamera",
            "descriptorIndex": 113,
            "recordAddress": "0x0064ea90",
            "handlerAnchor": "0x00533b70 IScript__Create3PointPanCamera",
            "targetThingName": "Fenrir",
            "positionCaseIds": [case_id for case_id, _token, _vector in POSITION_CASES],
            "pointCount": 3,
            "durationSeconds": 15.0,
            "durationGetterSlot": "+0x34",
            "positionGetterSlot": "+0x44",
            "targetThingGetterSlot": "+0x40",
            "staticBridge": [
                "GetThingRef context only",
                "0x00416d10 CBSpline__ctor",
                "0x004198d0 CPanCamera__ctor",
                "0x004705e0 CGame__SetCurrentCamera",
            ],
            "finiteOnly": True,
            "runtimeCameraSwitchingProven": False,
            "runtimeVisibleCameraOutputProven": False,
        }
    ]


def context_only_descriptor_rows() -> list[dict[str, Any]]:
    return [
        {
            "command": "Goto4PointPanCamera",
            "descriptorIndex": 114,
            "recordAddress": "0x0064ead0",
            "rawEntryValue": "IScript__Create3PointPanCamera",
            "contextOnly": True,
            "reason": "raw descriptor context preserved; no deterministic 4-point public corpus case is claimed here",
        },
        {
            "command": "GotoPlayerCamera",
            "descriptorIndex": 115,
            "recordAddress": "0x0064eb10",
            "rawEntryValue": "IScript__Create4PointPanCamera",
            "contextOnly": True,
            "reason": "raw descriptor context preserved; no runtime player-camera handler mapping is claimed here",
        },
    ]


def build_schema() -> dict[str, Any]:
    selection = read_json(POST_GOODIE_SELECTION)
    cutscene = read_json(CUTSCENE_STATIC)
    rollup = read_json(ROLLUP)
    fixture = read_json(FIXTURE_SELECTION)
    getthingref = read_json(GETTHINGREF_STATIC)
    positions = position_cases()
    camera_cases = camera_plan_cases()
    position_float_assertions = len(positions) * 3
    camera_plan_assertions = 6
    return {
        "schemaVersion": "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.v1",
        "status": "PASS",
        "missionScriptCutscenePanCameraPositionDeterministicFixtureProofPlanStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "cutscene-camera-position",
        "selectedFixturePath": "cutscene-position-finite-camera-plan",
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "fixtureAccounting": {
            "sourceProofCount": 5,
            "descriptorIndices": list(DESCRIPTOR_INDICES),
            "descriptorRecordCount": len(cutscene["descriptorRecords"]),
            "positionDatatypeTypeId": cutscene["positionDatatype"]["typeId"],
            "positionDatatypeSizeBytes": cutscene["positionDatatype"]["sizeBytes"],
            "positionPayloadReadCount": len(cutscene["positionDatatype"]["payloadReads"]),
            "positionGetterSlot": cutscene["positionDatatype"]["observedValueGetterSlot"],
            "positionOpenBoundary": cutscene["positionDatatype"]["openBoundary"],
            "handlerAnchorCount": len(cutscene["cameraHandlers"]),
            "wave580MetadataRows": cutscene["evidenceCounts"]["wave580MetadataRows"],
            "wave580TagRows": cutscene["evidenceCounts"]["wave580TagRows"],
            "wave580XrefRows": cutscene["evidenceCounts"]["wave580XrefRows"],
            "wave580DecompileRows": cutscene["evidenceCounts"]["wave580DecompileRows"],
            "wave580InstructionRows": cutscene["evidenceCounts"]["wave580InstructionRows"],
            "wave580VtableRows": cutscene["evidenceCounts"]["wave580VtableRows"],
            "fenrirGetThingRefRowsInSelectedLevels": cutscene["missionThingContext"]["fenrirGetThingRefRowsInSelectedLevels"],
            "cutsceneFenrirGetThingRefRows": cutscene["missionThingContext"]["cutsceneFenrirGetThingRefRows"],
            "cutsceneRowsByLevelCount": len(cutscene["missionThingContext"]["cutsceneRowsByLevel"]),
            "cutsceneRowsByFileCount": len(cutscene["missionThingContext"]["cutsceneRowsByFile"]),
            "plannedPositionCaseCount": len(positions),
            "plannedPositionFloatAssertionCount": position_float_assertions,
            "plannedCameraPlanCaseCount": len(camera_cases),
            "plannedCameraPlanAssertionCount": camera_plan_assertions,
            "deterministicFixtureCaseCount": len(positions) + len(camera_cases),
            "finiteOnlyCaseCount": len(positions) + len(camera_cases),
            "contextOnlyDescriptorCount": len(context_only_descriptor_rows()),
            "selectionCompletedFamilyCount": selection["selectionAccounting"]["completedFamilyCount"],
            "selectionRemainingFamilyCount": selection["selectionAccounting"]["remainingFamilyCount"],
            "fixtureSelectionOriginalRank": next(row["rank"] for row in fixture["candidateRanking"] if row["family"] == "cutscene-camera-position"),
            "rollupCommandFamilyCount": rollup["rollupAccounting"]["commandFamilyCount"],
            "getThingRefStaticSchemaStatus": getthingref["status"],
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "publicLeakCheck": "PASS",
        },
        "sourceEvidence": {
            "postGoodieSelection": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-post-goodie-selection-refresh.v1.json",
                "status": selection["selectionRefreshStatus"],
                "selectedChildLane": selection["selectedChildLane"],
                "selectedChildScope": selection["selectedChildScope"],
            },
            "cutsceneStaticProof": {
                "schema": "reverse-engineering/binary-analysis/missionscript-cutscene-pan-camera-position-command-effect.v1.json",
                "descriptorRecords": list(DESCRIPTOR_ROWS),
                "descriptorIndices": list(DESCRIPTOR_INDICES),
                "positionTypeId": cutscene["positionDatatype"]["typeId"],
                "positionVtable": cutscene["positionDatatype"]["vtable"],
                "positionPayloadReads": cutscene["positionDatatype"]["payloadReads"],
                "handlerAnchors": list(HANDLER_ANCHORS),
                "fenrirCutsceneRows": cutscene["missionThingContext"]["cutsceneFenrirGetThingRefRows"],
                "descriptorBoundary": "raw static descriptor context only; exact descriptor layout, exact arity, and exact argument type schema remain unproven",
            },
            "getThingRefStaticProof": {
                "schema": "reverse-engineering/binary-analysis/world-thing-spawn-getthingref-object-reference-static.v1.json",
                "status": getthingref["status"],
                "boundary": "GetThingRef is static object-reference context only; runtime object lookup and object identity remain unproven",
            },
            "rollup": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-rebuild-interface-rollup.v1.json",
                "commandFamilyCount": rollup["rollupAccounting"]["commandFamilyCount"],
                "descriptorRecordCount": rollup["rollupAccounting"]["descriptorRecordCount"],
                "uniqueDescriptorTokenCount": rollup["rollupAccounting"]["uniqueDescriptorTokenCount"],
            },
            "fixtureSelection": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-fixture-selection.v1.json",
                "candidateFamilyCount": fixture["selectionAccounting"]["candidateFamilyCount"],
                "originalRank": next(row["rank"] for row in fixture["candidateRanking"] if row["family"] == "cutscene-camera-position"),
            },
        },
        "fixtureModel": {
            "createPositionModel": "finite (x,y,z) payload copied into a position fixture record",
            "cameraPlanModel": "target thing label plus ordered position case ids plus duration as static camera-plan skeleton",
            "selectedRuntimeCommand": "Goto3PointPanCamera",
            "targetThingName": "Fenrir",
            "durationSeconds": 15.0,
            "finiteOnly": True,
            "excludedNumericCases": [
                "NaN",
                "infinity",
                "signed zero parity",
                "subnormal values",
                "overflow",
                "exact x87/CRT rounding parity",
            ],
            "contextOnlyCommands": ["Goto4PointPanCamera", "GotoPlayerCamera"],
            "sourceStaticCameraAnchors": [
                "0x00416d10 CBSpline__ctor",
                "0x004198d0 CPanCamera__ctor",
                "0x004705e0 CGame__SetCurrentCamera",
            ],
        },
        "deterministicPositionCases": positions,
        "deterministicCameraPlanCases": camera_cases,
        "contextOnlyDescriptorRows": context_only_descriptor_rows(),
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
            "requiresNewSelectionIfRuntimeNeeded": True,
            "requiresSeparateProofForRuntimeCameraSwitching": True,
            "requiresSeparateProofForGoto4AndPlayerCameraRuntimeMapping": True,
        },
        "guardSummary": {
            "falseGuards": {key: False for key in FALSE_GUARDS},
            "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        },
        "claimBoundary": {
            "proves": [
                "finite CreatePosition fixture payloads for the three public Fenrir cutscene positions",
                "one static Goto3PointPanCamera camera-plan skeleton linking Fenrir, three position cases, duration 15.0, and the saved Wave580 handler/context anchors",
                "Goto4PointPanCamera and GotoPlayerCamera remain descriptor-context-only rows in this fixture lane",
                "the static source anchors for the cutscene camera/position fixture are consolidated without runtime, Ghidra, patch, Godot, product UI, or rebuild claims",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime camera switching",
                "runtime cutscene playback",
                "runtime visible camera output",
                "runtime object identity",
                "runtime object lookup by name",
                "runtime CreatePosition behavior",
                "runtime PanCamera behavior",
                "live loose-MSL loading",
                "packed-resource script selection",
                "exact descriptor layout",
                "exact command arity",
                "exact argument type schema",
                "exact CPositionDataType layout",
                "exact CPanCamera layout",
                "exact CBSpline layout",
                "Goto4PointPanCamera runtime handler mapping",
                "GotoPlayerCamera runtime handler mapping",
                "NaN/infinity behavior",
                "signed-zero behavior",
                "subnormal behavior",
                "overflow behavior",
                "exact x87/CRT rounding parity",
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
    require(actual == expected, "schema is not regenerated from current cutscene fixture evidence", failures)
    accounting = actual["fixtureAccounting"]
    require(accounting["descriptorIndices"] == list(DESCRIPTOR_INDICES), "descriptor index list mismatch", failures)
    require(accounting["descriptorRecordCount"] == 4, "descriptor record count mismatch", failures)
    require(accounting["positionDatatypeTypeId"] == 6, "position datatype type id mismatch", failures)
    require(accounting["positionDatatypeSizeBytes"] == 20, "position datatype size mismatch", failures)
    require(accounting["positionPayloadReadCount"] == 3, "position payload read count mismatch", failures)
    require(accounting["positionGetterSlot"] == "+0x44", "position getter slot mismatch", failures)
    require(accounting["handlerAnchorCount"] == 2, "handler anchor count mismatch", failures)
    require(accounting["wave580MetadataRows"] == 6, "Wave580 metadata count mismatch", failures)
    require(accounting["wave580TagRows"] == 6, "Wave580 tag count mismatch", failures)
    require(accounting["wave580XrefRows"] == 6, "Wave580 xref count mismatch", failures)
    require(accounting["wave580DecompileRows"] == 6, "Wave580 decompile count mismatch", failures)
    require(accounting["wave580InstructionRows"] == 5454, "Wave580 instruction count mismatch", failures)
    require(accounting["wave580VtableRows"] == 36, "Wave580 vtable count mismatch", failures)
    require(accounting["fenrirGetThingRefRowsInSelectedLevels"] == 17, "selected-level Fenrir row count mismatch", failures)
    require(accounting["cutsceneFenrirGetThingRefRows"] == 6, "cutscene Fenrir row count mismatch", failures)
    require(accounting["plannedPositionCaseCount"] == 3, "position case count mismatch", failures)
    require(accounting["plannedPositionFloatAssertionCount"] == 9, "position float assertion count mismatch", failures)
    require(accounting["plannedCameraPlanCaseCount"] == 1, "camera plan case count mismatch", failures)
    require(accounting["plannedCameraPlanAssertionCount"] == 6, "camera plan assertion count mismatch", failures)
    require(accounting["deterministicFixtureCaseCount"] == 4, "deterministic fixture case count mismatch", failures)
    require(accounting["finiteOnlyCaseCount"] == 4, "finite-only case count mismatch", failures)
    require(accounting["contextOnlyDescriptorCount"] == 2, "context-only descriptor count mismatch", failures)
    require(accounting["selectionCompletedFamilyCount"] == 3, "selection completed family count mismatch", failures)
    require(accounting["selectionRemainingFamilyCount"] == 6, "selection remaining family count mismatch", failures)
    require(accounting["fixtureSelectionOriginalRank"] == 3, "fixture selection original rank mismatch", failures)
    require(accounting["rollupCommandFamilyCount"] == 9, "rollup family count mismatch", failures)
    require(accounting["getThingRefStaticSchemaStatus"] == "PASS", "GetThingRef static schema status mismatch", failures)
    require(accounting["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    for case in actual["deterministicPositionCases"]:
        require(case["finiteOnly"] is True, f"position case not finite-only: {case['id']}", failures)
        payload = case["expectedPayload"]
        require(payload == [case["position"]["x"], case["position"]["y"], case["position"]["z"]], f"position payload mismatch: {case['id']}", failures)
        require(is_finite_vector(payload), f"position payload has non-finite value: {case['id']}", failures)
    for case in actual["deterministicCameraPlanCases"]:
        require(case["finiteOnly"] is True, f"camera plan not finite-only: {case['id']}", failures)
        require(case["targetThingName"] == "Fenrir", f"camera target mismatch: {case['id']}", failures)
        require(case["pointCount"] == 3, f"camera point count mismatch: {case['id']}", failures)
        require(case["durationSeconds"] == 15.0, f"camera duration mismatch: {case['id']}", failures)
        require(case["runtimeCameraSwitchingProven"] is False, f"camera runtime guard mismatch: {case['id']}", failures)
        require(case["runtimeVisibleCameraOutputProven"] is False, f"camera output guard mismatch: {case['id']}", failures)
    for row in actual["contextOnlyDescriptorRows"]:
        require(row["contextOnly"] is True, f"context-only descriptor guard mismatch: {row['command']}", failures)

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
    selection = read_json(POST_GOODIE_SELECTION)
    cutscene = read_json(CUTSCENE_STATIC)
    rollup = read_json(ROLLUP)
    fixture = read_json(FIXTURE_SELECTION)
    getthingref = read_json(GETTHINGREF_STATIC)

    require(selection["selectionRefreshStatus"] == POST_GOODIE_STATUS, "post-Goodie selection status mismatch", failures)
    require(selection["selectedChildLane"] == THIS_SLICE, "post-Goodie selected lane mismatch", failures)
    require(selection["selectionAccounting"]["completedFamilyCount"] == 3, "completed family count mismatch", failures)
    require(selection["selectionAccounting"]["remainingFamilyCount"] == 6, "remaining family count mismatch", failures)

    require(cutscene["status"] == "PASS", "cutscene static schema status mismatch", failures)
    require(len(cutscene["descriptorRecords"]) == 4, "cutscene descriptor record count mismatch", failures)
    require(
        [record["index"] for record in cutscene["descriptorRecords"].values()] == list(DESCRIPTOR_INDICES),
        "cutscene descriptor index list mismatch",
        failures,
    )
    require(cutscene["positionDatatype"]["typeId"] == 6, "position type id mismatch", failures)
    require(cutscene["positionDatatype"]["vtable"] == "0x005e4da4", "position vtable mismatch", failures)
    require(cutscene["positionDatatype"]["sizeBytes"] == 20, "position size mismatch", failures)
    require(cutscene["positionDatatype"]["payloadReads"] == ["+0x04 float", "+0x08 float", "+0x0c float"], "position payload read mismatch", failures)
    require(cutscene["positionDatatype"]["observedValueGetterSlot"] == "+0x44", "position getter slot mismatch", failures)
    require(len(cutscene["cameraHandlers"]) == 2, "camera handler count mismatch", failures)
    require(cutscene["missionThingContext"]["fenrirGetThingRefRowsInSelectedLevels"] == 17, "selected-level Fenrir rows mismatch", failures)
    require(cutscene["missionThingContext"]["cutsceneFenrirGetThingRefRows"] == 6, "cutscene Fenrir rows mismatch", failures)
    require(cutscene["mslCutsceneExample"]["createPositionCallsInExample"] == 3, "CreatePosition corpus call count mismatch", failures)
    require(cutscene["mslCutsceneExample"]["goto3PointPanCameraCallsInExample"] == 1, "Goto3PointPanCamera corpus call count mismatch", failures)
    require(cutscene["mslCutsceneExample"]["targetThing"] == "Fenrir", "cutscene target mismatch", failures)
    require(all(cutscene["mslCutsceneExample"]["tokensPresent"].values()), "cutscene example token missing", failures)

    require(rollup["rollupAccounting"]["commandFamilyCount"] == 9, "rollup family count mismatch", failures)
    require(rollup["rollupAccounting"]["descriptorRecordCount"] == 52, "rollup descriptor count mismatch", failures)
    require(next(row["rank"] for row in fixture["candidateRanking"] if row["family"] == "cutscene-camera-position") == 3, "fixture selection original rank mismatch", failures)
    require(getthingref["status"] == "PASS", "GetThingRef static proof status mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.v1.json",
        f"missionScriptCutscenePanCameraPositionDeterministicFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=cutscene-camera-position",
        "selectedFixturePath=cutscene-position-finite-camera-plan",
        "sourceProofCount=5",
        "descriptorIndices=65/113/114/115",
        "descriptorRecordCount=4",
        "positionDatatypeTypeId=6",
        "positionDatatypeSizeBytes=20",
        "positionPayloadReadCount=3",
        "positionGetterSlot=+0x44",
        "handlerAnchorCount=2",
        "wave580MetadataRows=6",
        "wave580TagRows=6",
        "wave580XrefRows=6",
        "wave580DecompileRows=6",
        "wave580InstructionRows=5454",
        "wave580VtableRows=36",
        "fenrirGetThingRefRowsInSelectedLevels=17",
        "cutsceneFenrirGetThingRefRows=6",
        "plannedPositionCaseCount=3",
        "plannedPositionFloatAssertionCount=9",
        "plannedCameraPlanCaseCount=1",
        "plannedCameraPlanAssertionCount=6",
        "deterministicFixtureCaseCount=4",
        "finiteOnlyCaseCount=4",
        "contextOnlyDescriptorCount=2",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "CreatePosition",
        "Goto3PointPanCamera",
        "Goto4PointPanCamera",
        "GotoPlayerCamera",
        "0x0064de90",
        "0x0064ea90",
        "0x0064ead0",
        "0x0064eb10",
        "0x00533b70 IScript__Create3PointPanCamera",
        "0x00533eb0 IScript__Create4PointPanCamera",
        "CPositionDataType",
        "0x005e4da4",
        "0x00416d10 CBSpline__ctor",
        "0x004198d0 CPanCamera__ctor",
        "0x004705e0 CGame__SetCurrentCamera",
        "GetThingRef context only",
        "Fenrir",
        "durationSeconds=15.0",
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
        "runtimeCameraRows=0",
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
        "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.md",
        "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.v1.json",
        f"missionScriptCutscenePanCameraPositionDeterministicFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=cutscene-camera-position",
        "selectedNextSlice=MissionScript Objective/Outcome Command-Effect Fixture Proof Plan",
        "plannedPositionCaseCount=3",
        "plannedCameraPlanCaseCount=1",
        "deterministicFixtureCaseCount=4",
        "contextOnlyDescriptorCount=2",
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
            f"{path.relative_to(ROOT)} still marks cutscene fixture active",
            failures,
        )

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed cutscene fixture lane", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed objective/outcome follow-up lane", failures)
    require(
        f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog,
        "backlog still marks objective/outcome follow-up lane active",
        failures,
    )
    require("Completed MissionScript Message/Audio Command-Effect Fixture Proof Plan" in backlog, "backlog missing completed message/audio follow-up lane", failures)
    require(
        "The selected active static-to-proof slice is MissionScript Message/Audio Command-Effect Fixture Proof Plan. Status: selected" not in backlog,
        "backlog still marks message/audio follow-up lane active",
        failures,
    )
    require("Completed MissionScript HUD / Display Command-Effect Fixture Proof Plan" in backlog, "backlog missing completed HUD/display follow-up lane", failures)
    require(
        "The selected active static-to-proof slice is MissionScript HUD / Display Command-Effect Fixture Proof Plan. Status: selected" not in backlog,
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
        scripts.get("test:missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan")
        == r"py -3 tools\missionscript_cutscene_pan_camera_position_deterministic_fixture_proof_plan_probe.py --check",
        "missing package cutscene deterministic fixture proof-plan test script",
        failures,
    )
    for script in (
        "test:missionscript-cutscene-pan-camera-position-command-effect-static",
        "test:missionscript-command-effect-post-goodie-selection-refresh",
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
        require(no_bea_process_running(), "BEA.exe process is running after cutscene fixture proof", failures)
        if failures:
            print("MissionScript cutscene pan-camera/position deterministic fixture proof-plan probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript cutscene pan-camera/position deterministic fixture proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
