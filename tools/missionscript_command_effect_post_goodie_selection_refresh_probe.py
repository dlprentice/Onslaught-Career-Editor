#!/usr/bin/env python3
"""Validate the post-Goodie MissionScript command-effect selection refresh."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-post-goodie-selection-refresh.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-post-goodie-selection-refresh.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-post-goodie-selection-refresh.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-post-goodie-selection-refresh.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_command_effect_post_goodie_selection_refresh_2026-06-09.md"

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
GOODIES_DOC = ROOT / "reverse-engineering" / "save-file" / "goodies-system.md"
LORE_GOODIES_DOC = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "goodies-system.md"
SAVE_FORMAT = ROOT / "reverse-engineering" / "save-file" / "save-format.md"
LORE_SAVE_FORMAT = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "save-format.md"
PACKAGE_JSON = ROOT / "package.json"

FIXTURE_SELECTION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-selection.v1.json"
VECTOR_FIXTURE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1.json"
GOODIE_BOUNDARY = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness.v1.json"
CUTSCENE_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-command-effect.v1.json"

THIS_SLICE = "MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan"
THIS_STATUS = "missionscript-command-effect-post-goodie-selection-refresh-complete-cutscene-camera-position-selected"
PREVIOUS_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof"
NEXT_SLICE = "MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan"
NEXT_SCOPE = "missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan"
OLD_VECTOR_SLICE = "MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan"
GOODIE_STATUS = "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-complete-copied-real-baseline-boundary-corpus-not-runtime-proof"
VECTOR_STATUS = "missionscript-vector-range-deterministic-helper-fixture-proof-plan-complete-pure-helper-fixture-not-runtime-proof"
FIXTURE_SELECTION_STATUS = "missionscript-command-effect-fixture-selection-complete-slot-bitset-save-selected"

FALSE_GUARDS = (
    "runtimeExecution",
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
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimeCameraSwitchingProven",
    "runtimeCutscenePlaybackProven",
    "runtimeVisibleCameraOutputProven",
    "runtimeObjectIdentityProven",
    "runtimeObjectLookupByNameProven",
    "liveLooseMslLoading",
    "packedResourceScriptSelectionProven",
    "exactCommandDescriptorLayoutProven",
    "exactCommandArityProven",
    "exactArgumentTypeSchemaProven",
    "exactCPositionDataTypeLayoutProven",
    "exactCPanCameraLayoutProven",
    "exactCBSplineLayoutProven",
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
    "privateFrameRowsObserved",
    "rowObservationRows",
    "sourceObservedRows",
    "newLaunchRows",
    "captureRows",
    "ocrRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "productUiRows",
    "godotRows",
    "rebuildImplementationRows",
    "beProcessesAfterSelection",
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
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact descriptor layout proven",
    "exact command arity proven",
    "exact argument type schema proven",
    "exact cpositiondatatype layout proven",
    "exact cpancamera layout proven",
    "exact cbspline layout proven",
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


def check_no_bad_public_content(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    fixture = read_json(FIXTURE_SELECTION)
    vector = read_json(VECTOR_FIXTURE)
    goodie = read_json(GOODIE_BOUNDARY)
    cutscene = read_json(CUTSCENE_STATIC)

    require(result["schemaVersion"] == "missionscript-command-effect-post-goodie-selection-refresh.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "status mismatch", failures)
    require(result["selectionRefreshStatus"] == THIS_STATUS, "selection status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["selectedChildLane"] == NEXT_SLICE, "selected child lane mismatch", failures)
    require(result["selectedChildScope"] == NEXT_SCOPE, "selected child scope mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    accounting = result["selectionAccounting"]
    require(accounting["originalCandidateFamilyCount"] == 9, "original candidate count mismatch", failures)
    require(accounting["completedFamilyCount"] == 3, "completed family count mismatch", failures)
    require(accounting["remainingFamilyCount"] == 6, "remaining family count mismatch", failures)
    require(accounting["selectedOriginalRank"] == 3, "selected original rank mismatch", failures)
    require(accounting["selectedRemainingRank"] == 1, "selected remaining rank mismatch", failures)
    require(accounting["completedFamilies"] == ["slot-bitset-save", "vector-range-helpers", "goodie-state-save"], "completed family order mismatch", failures)
    require(accounting["remainingFamilies"][0] == "cutscene-camera-position", "remaining family head mismatch", failures)
    require(accounting["selectionFalseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["selectionZeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    require(fixture["fixtureSelectionStatus"] == FIXTURE_SELECTION_STATUS, "fixture selection status mismatch", failures)
    require(fixture["selectionAccounting"]["candidateFamilyCount"] == 9, "fixture candidate count mismatch", failures)
    require([row["family"] for row in fixture["candidateRanking"][:5]] == ["slot-bitset-save", "vector-range-helpers", "cutscene-camera-position", "objective-outcome", "goodie-state-save"], "fixture ranking source mismatch", failures)

    require(vector["missionScriptVectorRangeDeterministicHelperFixtureProofPlanStatus"] == VECTOR_STATUS, "vector fixture status mismatch", failures)
    require(vector["selectedFixtureFamily"] == "vector-range-helpers", "vector fixture family mismatch", failures)
    require(vector["guardSummary"]["falseGuards"]["runtimeExecution"] is False, "vector fixture runtime guard mismatch", failures)

    require(goodie["goodieStateSaveAppCoreCopiedBaselineBoundaryCorpusHarnessStatus"] == GOODIE_STATUS, "Goodie boundary status mismatch", failures)
    require(goodie["selectedNextSlice"] == THIS_SLICE, "Goodie boundary next-slice mismatch", failures)
    require(goodie["corpus"]["copiedBaselineBoundaryCorpusCaseCount"] == 632, "Goodie boundary corpus count mismatch", failures)
    require(goodie["negativeGuards"]["runtimeExecution"] is False, "Goodie boundary runtime guard mismatch", failures)

    require(len(cutscene["descriptorRecords"]) == 4, "cutscene descriptor count mismatch", failures)
    require(cutscene["descriptorRecords"]["CreatePosition"]["index"] == 65, "CreatePosition descriptor mismatch", failures)
    require(cutscene["descriptorRecords"]["Goto3PointPanCamera"]["recordAddress"] == "0x0064ea90", "Goto3 descriptor mismatch", failures)
    require(cutscene["positionDatatype"]["typeId"] == 6, "position datatype mismatch", failures)
    require(cutscene["positionDatatype"]["vtable"] == "0x005e4da4", "position vtable mismatch", failures)
    require(len(cutscene["cameraHandlers"]) == 2, "camera handler count mismatch", failures)
    require(cutscene["missionThingContext"]["cutsceneFenrirGetThingRefRows"] == 6, "Fenrir cutscene row mismatch", failures)

    guard = result["guardSummary"]
    for key in FALSE_GUARDS:
        require(guard["falseGuards"][key] is False, f"false guard not false: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guard["zeroCounters"][key] == 0, f"zero counter not zero: {key}", failures)

    require("the next selected non-runtime MissionScript command-effect fixture family is cutscene-camera-position" in result["claimBoundary"]["proves"], "claim boundary missing selected proof", failures)
    require("runtime camera switching" in result["claimBoundary"]["doesNotProve"], "claim boundary missing runtime camera boundary", failures)
    require(read_json(LORE_RESULT) == result, "lore schema mirror mismatch", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)

    required_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "missionscript-command-effect-post-goodie-selection-refresh.v1.json",
        "completedFamilyCount=3",
        "remainingFamilyCount=6",
        "selectedOriginalRank=3",
        "selectedRemainingRank=1",
        "completedFamilies=slot-bitset-save,vector-range-helpers,goodie-state-save",
        "remainingFamilies=cutscene-camera-position,objective-outcome,message-audio-console,hud-variable-display,thing-value-engine-helper,player-state-score",
        "selectionFalseGuardCount=31",
        "selectionZeroCounterCount=18",
        "publicLeakCheck=PASS",
        "CreatePosition",
        "Goto3PointPanCamera",
        "Goto4PointPanCamera",
        "GotoPlayerCamera",
        "CPositionDataType",
        "0x005e4da4",
        "0x00533b70 IScript__Create3PointPanCamera",
        "0x00533eb0 IScript__Create4PointPanCamera",
        "raw descriptor rows as context rows",
        "CBSpline",
        "CPanCamera",
        "CGame__SetCurrentCamera",
        "Fenrir",
        "level741",
        "level742",
        "runtimeExecution=false",
        "beLaunch=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
        "runtimeCameraSwitchingProven=false",
        "runtimeVisibleCameraOutputProven=false",
        "runtimeCameraRows=0",
        "beProcessesAfterSelection=0",
    )

    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    front_door_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        NEXT_SLICE,
        "missionscript-command-effect-post-goodie-selection-refresh.md",
        "missionscript-command-effect-post-goodie-selection-refresh.v1.json",
        "completedFamilyCount=3",
        "remainingFamilyCount=6",
        "selectedOriginalRank=3",
        "selectedRemainingRank=1",
        "cutscene-camera-position",
        "active next static child lane: MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, ISCRIPT_CONTRACT):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            "The selected active static-to-proof slice is MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks vector/range active",
            failures,
        )
        require(
            "active next static child lane: MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan" not in text,
            f"{path.relative_to(ROOT)} still points active child to vector/range",
            failures,
        )

    for path in (GOODIES_DOC, SAVE_FORMAT):
        text = read_text(path)
        require(THIS_SLICE in text, f"{path.relative_to(ROOT)} missing post-Goodie refresh token", failures)
        require(NEXT_SLICE in text, f"{path.relative_to(ROOT)} missing cutscene next-lane token", failures)
        require("selectedNextSlice=MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan" not in text, f"{path.relative_to(ROOT)} still has stale Goodie boundary next slice", failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (ISCRIPT_CONTRACT, LORE_ISCRIPT_CONTRACT),
        (GOODIES_DOC, LORE_GOODIES_DOC),
        (SAVE_FORMAT, LORE_SAVE_FORMAT),
    ):
        require(read_text(mirror) == read_text(source), f"lore mirror mismatch: {mirror.relative_to(ROOT)}", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-command-effect-post-goodie-selection-refresh")
        == r"py -3 tools\missionscript_command_effect_post_goodie_selection_refresh_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_result(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after post-Goodie selection refresh", failures)

    if failures:
        print("MissionScript command-effect post-Goodie selection refresh probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript command-effect post-Goodie selection refresh probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
