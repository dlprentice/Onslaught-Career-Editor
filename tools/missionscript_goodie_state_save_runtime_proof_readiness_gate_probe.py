#!/usr/bin/env python3
"""Validate MissionScript Goodie state/save runtime-proof readiness gate."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-runtime-proof-readiness-gate.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-runtime-proof-readiness-gate.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-runtime-proof-readiness-gate.md"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-runtime-proof-readiness-gate.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_goodie_state_save_runtime_proof_readiness_gate_2026-06-09.md"

HARNESS_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness.v1.json"
CLEAN_ROOM_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-clean-room-codec-interface-proof.v1.json"
COPIED_BASELINE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.v1.json"
FIXTURE_PLAN_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
MISSIONSCRIPT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_MISSIONSCRIPT_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
GOODIES_SYSTEM = ROOT / "reverse-engineering" / "save-file" / "goodies-system.md"
LORE_GOODIES_SYSTEM = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "goodies-system.md"
SAVE_FORMAT = ROOT / "reverse-engineering" / "save-file" / "save-format.md"
LORE_SAVE_FORMAT = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "save-format.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Goodie State / Save Runtime-Proof Readiness Gate"
THIS_STATUS = "missionscript-goodie-state-save-runtime-proof-readiness-gate-complete-runtime-deferred-no-launch"
PREVIOUS_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Codec Harness Proof"
PREVIOUS_STATUS = "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-complete-appcore-copied-real-baseline-byte-preservation-not-runtime-proof"
NEXT_SLICE = "MissionScript Goodie State / Save AppCore Boundary-Corpus Fixture Matrix Proof Plan"
NEXT_ACTIVE_SLICE = "MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan"
COMPLETED_GOODIE_BOUNDARY_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof"
POST_GOODIE_SELECTION_SLICE = "MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan"
SCHEMA_NAME = "missionscript-goodie-state-save-runtime-proof-readiness-gate.v1.json"
PROOF_NAME = "missionscript-goodie-state-save-runtime-proof-readiness-gate.md"

PUBLIC_FORBIDDEN_TOKENS = (
    "C:\\Users",
    "C:/Users",
    "G:\\",
    "Program Files",
    "steamapps",
    "save-attempts",
    "subagents/",
    "subagents\\",
    "game\\savegames",
    "private_runtime_evidence",
    "onslaught_codex_directive",
    "capturePath",
    "framePath",
    "frameSha256",
    "frameByteLength",
    "HWND",
    "window handle",
    "process id",
    "password",
    "token=",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime goodie mutation proven",
    "runtime goodie state mutation proven",
    "runtime save/load behavior proven",
    "runtime defaultoptions behavior proven",
    "runtime goodies wall behavior proven",
    "runtime score behavior proven",
    "source selection proven",
    "private-frame review complete",
    "screenshot interpretation complete",
    "installed game mutation proven",
    "original executable mutation proven",
    "product ui behavior proven",
    "visual qa complete",
    "godot parity proven",
    "ghidra mutation complete",
    "executable patching behavior proven",
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


def check_no_public_leaks(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in PUBLIC_FORBIDDEN_TOKENS:
        require(token.lower() not in lower, f"{path.relative_to(ROOT)} leaks forbidden public token category: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)
    require(re.search(r"\b[a-f0-9]{64}\b", lower) is None, f"{path.relative_to(ROOT)} leaks raw 64-hex digest", failures)


def expected_schema() -> dict[str, Any]:
    return {
        "schemaVersion": "missionscript-goodie-state-save-runtime-proof-readiness-gate.v1",
        "status": "PASS",
        "missionScriptGoodieStateSaveRuntimeProofReadinessGateStatus": THIS_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "goodie-state-save",
        "selectedFixturePath": "goodie-state-save-index-state-byte-preservation",
        "decision": {
            "runtimeReadinessGateComplete": True,
            "runtimeObservationReadyNow": False,
            "runtimeDeferred": True,
            "deferReason": "explicit-runtime-observation-arm-and-private-output-review-absent-continue-non-runtime-appcore-boundary-corpus-fixture-proof",
            "nextLaneClass": "non-runtime AppCore boundary-corpus fixture matrix proof",
            "explicitRuntimeObservationArmPresent": False,
            "operatorPrivateOutputReviewAvailable": False,
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "upstreamProofs": {
            "appCoreHarnessStatus": PREVIOUS_STATUS,
            "cleanRoomCodecInterfaceStatus": "missionscript-goodie-state-save-clean-room-codec-interface-proof-complete-pure-appcore-buffer-codec-not-runtime-proof",
            "copiedBaselineByteDiffStatus": "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof-complete-copied-real-baseline-appcore-byte-diff-not-runtime-proof",
            "commandEffectFixturePlanStatus": "missionscript-goodie-state-save-command-effect-fixture-proof-plan-complete-static-offset-state-fixture-plan-not-runtime-proof",
            "goodieCommandFixtureFamily": "goodie-state-save",
            "appCoreCodecUsed": True,
            "appCorePatcherUsed": False,
            "manualGoodieDwordWriteInHarness": False,
            "sourcePathsPublic": False,
            "sourceHashesPublic": False,
            "artifactPathsPublic": False,
            "artifactHashesPublic": False,
            "rawSaveBytesPublic": False,
            "copyBeforeWrite": True,
            "sourceAndOutputPathsDistinct": True,
            "careerSourceToInputDiffCount": 0,
            "defaultOptionsSourceToInputDiffCount": 0,
            "careerSourceUnchanged": True,
            "defaultOptionsSourceUnchanged": True,
            "expectedSize": 10004,
            "versionWord": "0x4BD1",
            "trueViewGoodieBase": "0x1F46",
            "scriptIndexing": "1-based",
            "mappingFormula": "save_goodie_index = script_index - 1",
            "offsetFormula": "0x1F46 + (script_index - 1) * 4",
            "reservedWritePolicy": "displayable-only-default-rejects-reserved",
            "scriptIndices": [1, 51, 53, 68, 71, 233],
            "saveGoodieIndices": [0, 50, 52, 67, 70, 232],
            "changedOffsets": ["0x1F46", "0x200E", "0x2016", "0x2052", "0x205E", "0x22E6"],
            "targetReadbackMismatchCount": 0,
            "unexpectedDiffCount": 0,
            "legacyTrapHitCount": 0,
            "roundtripToBaselineDiffCount": 0,
            "nonTargetGoodiesUnchanged": True,
            "reservedGoodiesUnchanged": True,
            "killCountersUnchanged": True,
            "techSlotsUnchanged": True,
            "optionsEntriesUnchanged": True,
            "optionsTailUnchanged": True,
        },
        "laterRuntimeArmRequirements": {
            "explicitRuntimeObservationArmRequired": True,
            "copiedProfileRequired": True,
            "copiedExecutableRequired": True,
            "copiedSaveBaselineRequired": True,
            "copiedDefaultOptionsBaselineRequired": True,
            "appOwnedArtifactRootRequired": True,
            "runtimeSpecimenAuthorityRequired": True,
            "patchCatalogVerificationRequired": True,
            "windowedPatchAllowedOnlyOnCopiedProfile": True,
            "installedGameReadOnlyRequired": True,
            "originalExecutableReadOnlyRequired": True,
            "baselineSaveSynthesisForbidden": True,
            "privateOutputReviewAvailabilityRequired": True,
            "publicSafeRedactionRequired": True,
            "stopConditionsRequired": True,
        },
        "negativeGuards": {
            "runtimeExecution": False,
            "beLaunch": False,
            "newLaunch": False,
            "copiedProfileMaterialization": False,
            "copiedExecutablePatchApplied": False,
            "screenshotCapture": False,
            "privateFrameReviewPerformed": False,
            "rowObservation": False,
            "exactTextOcrPerformed": False,
            "rawDialoguePublished": False,
            "visibleTextExcerptPublished": False,
            "sourceSelectionObserved": False,
            "sourceSelectionProven": False,
            "nativeInput": False,
            "debuggerAttachment": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
            "defaultoptionsMutation": False,
            "saveSynthesis": False,
            "ghidraMutation": False,
            "executablePatching": False,
            "godotWork": False,
            "productUiWired": False,
            "rebuildImplementation": False,
            "runtimeMissionScriptExecutionProven": False,
            "runtimeCommandEffectsProven": False,
            "runtimeGoodieStateMutationProven": False,
            "runtimeSaveLoadBehaviorProven": False,
            "runtimeDefaultoptionsBehaviorProven": False,
            "runtimeGoodiesWallBehaviorProven": False,
            "runtimeScoreBehaviorProven": False,
            "liveLooseMslLoadingProven": False,
            "packedResourceScriptSelectionProven": False,
            "addScoreHandlerBodyProven": False,
            "hiddenGoodiesUnreachableProven": False,
            "runtimeGoodies71To73ReachabilityProven": False,
            "rebuildParityProven": False,
            "noNoticeableDifferenceParityProven": False,
            "runtimeObservationRows": 0,
            "missionScriptRuntimeEvidenceRows": 0,
            "runtimeCommandEffectRows": 0,
            "runtimeGoodieStateRows": 0,
            "runtimeSaveRows": 0,
            "runtimeDefaultOptionsRows": 0,
            "runtimeGoodiesWallRows": 0,
            "runtimeScoreRows": 0,
            "publicAbsolutePathLeakCount": 0,
            "publicSha256ValueLeakCount": 0,
            "publicWindowIdentifierLeakCount": 0,
            "publicProcessIdentifierLeakCount": 0,
            "privatePathLeakCount": 0,
            "rawArtifactLeakCount": 0,
            "rawDialogueLeakCount": 0,
            "publicLeakCheck": "PASS",
        },
        "nextNonRuntimeSlice": {
            "selectedNextSlice": NEXT_SLICE,
            "reason": "expand AppCore Goodie state/save boundary/corpus fixture matrix coverage across displayable boundary, reserved-preserve, known script-index corpus, no-op, rejection, idempotence, legacy-trap, and documented static/runtime-deferred guard cases while runtime observation remains deferred",
            "runtimeExecution": False,
            "beLaunch": False,
            "ghidraMutation": False,
            "executablePatching": False,
            "godotWork": False,
            "rebuildImplementation": False,
        },
        "claimBoundary": {
            "proves": [
                "the MissionScript Goodie state/save runtime-proof path has a public-safe readiness gate",
                "the upstream AppCore and copied-baseline proof stack is sufficient for non-runtime boundary/corpus continuation",
                "runtime observation is deferred until an explicit runtime-observation arm and copied-profile safety packet exist",
                "the next selected safe slice is a non-runtime AppCore boundary-corpus fixture matrix proof plan",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime Goodie mutation",
                "runtime save/load behavior",
                "runtime defaultoptions behavior",
                "runtime Goodies wall behavior",
                "runtime score behavior",
                "live loose-MSL loading",
                "packed-resource script selection",
                "source selection",
                "private-frame review",
                "screenshot or frame interpretation",
                "native input",
                "debugger behavior",
                "installed game mutation",
                "original executable mutation",
                "product UI behavior",
                "Ghidra mutation",
                "executable patching",
                "Godot parity",
                "rebuild implementation",
                "rebuild parity",
                "no-noticeable-difference parity",
            ],
        },
    }


def check_prerequisites(failures: list[str]) -> None:
    harness = read_json(HARNESS_SCHEMA)
    clean = read_json(CLEAN_ROOM_SCHEMA)
    copied = read_json(COPIED_BASELINE_SCHEMA)
    fixture = read_json(FIXTURE_PLAN_SCHEMA)
    expected = expected_schema()

    require(harness["goodieStateSaveAppCoreCopiedBaselineCodecHarnessStatus"] == PREVIOUS_STATUS, "harness prerequisite status mismatch", failures)
    require(harness["selectedNextSlice"] == "MissionScript Goodie State / Save Runtime-Proof Readiness Gate Plan", "harness prerequisite next-slice mismatch", failures)
    require(harness["implementation"]["appCoreCodecUsed"] is True, "harness AppCore codec-use mismatch", failures)
    require(harness["implementation"]["appCorePatcherUsed"] is False, "harness patcher guard mismatch", failures)
    require(harness["implementation"]["manualGoodieDwordWriteInHarness"] is False, "harness manual write guard mismatch", failures)
    require(harness["privateEvidence"]["copyBeforeWrite"] is True, "harness copy-before-write mismatch", failures)
    require(harness["privateEvidence"]["sourcePathsPublic"] is False, "harness source disclosure mismatch", failures)
    require(harness["operation"]["changedOffsets"] == expected["upstreamProofs"]["changedOffsets"], "harness changed offsets mismatch", failures)
    require(harness["operation"]["targetReadbackMismatchCount"] == 0, "harness readback mismatch", failures)
    require(harness["operation"]["legacyTrapHitCount"] == 0, "harness legacy trap mismatch", failures)
    require(harness["noOpAndRoundTrip"]["roundtripToBaselineDiffCount"] == 0, "harness roundtrip mismatch", failures)
    require(harness["preservation"]["reservedGoodiesUnchanged"] is True, "harness reserved Goodies preservation mismatch", failures)
    require(harness["negativeGuards"]["runtimeExecution"] is False, "harness runtime guard mismatch", failures)
    require(harness["negativeGuards"]["beLaunch"] is False, "harness launch guard mismatch", failures)
    require(harness["negativeGuards"]["runtimeGoodieStateMutationProven"] is False, "harness runtime Goodie mutation guard mismatch", failures)

    require(clean["missionScriptGoodieStateSaveCleanRoomCodecInterfaceProofStatus"] == expected["upstreamProofs"]["cleanRoomCodecInterfaceStatus"], "clean-room status mismatch", failures)
    require(clean["validation"]["xunitTestCaseCount"] == 249, "clean-room test count mismatch", failures)
    require(copied["missionScriptGoodieStateSaveCopiedBaselineByteDiffFixtureProofStatus"] == expected["upstreamProofs"]["copiedBaselineByteDiffStatus"], "copied-baseline status mismatch", failures)
    require(copied["byteDiff"]["unexpectedDiffCount"] == 0, "copied-baseline unexpected diff mismatch", failures)
    require(copied["byteDiff"]["legacyTrapHitCount"] == 0, "copied-baseline legacy trap mismatch", failures)
    require(fixture["missionScriptGoodieStateSaveCommandEffectFixtureProofPlanStatus"] == expected["upstreamProofs"]["commandEffectFixturePlanStatus"], "fixture-plan status mismatch", failures)
    require(fixture["fixtureAccounting"]["plannedGoodieFixtureCaseCount"] == 43, "fixture-plan case count mismatch", failures)


def check_schema(failures: list[str]) -> None:
    expected = expected_schema()
    for path in (SCHEMA, LORE_SCHEMA):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} schema mismatch", failures)
        check_no_public_leaks(path, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        SCHEMA_NAME,
        "runtimeReadinessGateComplete=true",
        "runtimeObservationReadyNow=false",
        "runtimeDeferred=true",
        "deferReason=explicit-runtime-observation-arm-and-private-output-review-absent-continue-non-runtime-appcore-boundary-corpus-fixture-proof",
        "explicitRuntimeObservationArmPresent=false",
        "operatorPrivateOutputReviewAvailable=false",
        "copiedProfileRequired=true",
        "copiedExecutableRequired=true",
        "copiedSaveBaselineRequired=true",
        "copiedDefaultOptionsBaselineRequired=true",
        "appOwnedArtifactRootRequired=true",
        "runtimeSpecimenAuthorityRequired=true",
        "patchCatalogVerificationRequired=true",
        "windowedPatchAllowedOnlyOnCopiedProfile=true",
        "installedGameReadOnlyRequired=true",
        "originalExecutableReadOnlyRequired=true",
        "baselineSaveSynthesisForbidden=true",
        "installedGameMutationAllowed=false",
        "originalExecutableMutationAllowed=false",
        "runtimeExecution=false",
        "beLaunch=false",
        "newLaunch=false",
        "copiedProfileMaterialization=false",
        "copiedExecutablePatchApplied=false",
        "screenshotCapture=false",
        "nativeInput=false",
        "debuggerAttachment=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "godotWork=false",
        "rebuildImplementation=false",
        "runtimeObservationRows=0",
        "missionScriptRuntimeEvidenceRows=0",
        "runtimeCommandEffectRows=0",
        "runtimeGoodieStateRows=0",
        "runtimeSaveRows=0",
        "runtimeDefaultOptionsRows=0",
        "runtimeGoodiesWallRows=0",
        "runtimeScoreRows=0",
        "liveLooseMslLoadingProven=false",
        "packedResourceScriptSelectionProven=false",
        "addScoreHandlerBodyProven=false",
        "hiddenGoodiesUnreachableProven=false",
        "runtimeGoodies71To73ReachabilityProven=false",
        "publicLeakCheck=PASS",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_public_leaks(path, failures)
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)
    require(read_json(LORE_SCHEMA) == read_json(SCHEMA), "lore schema mirror mismatch", failures)

    front_door_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PROOF_NAME,
        SCHEMA_NAME,
        f"selectedNextSlice={NEXT_SLICE}",
        "runtimeObservationReadyNow=false",
        "runtimeDeferred=true",
        "explicitRuntimeObservationArmPresent=false",
        "beLaunch=false",
        "runtimeObservationRows=0",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, MISSIONSCRIPT_CONTRACT, GOODIES_SYSTEM, SAVE_FORMAT):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            "The selected active static-to-proof slice is MissionScript Goodie State / Save Runtime-Proof Readiness Gate Plan. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks runtime-readiness gate active",
            failures,
        )
        require(
            f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in text
            or f"active next static child lane: {NEXT_SLICE}" in text
            or f"Completed {NEXT_SLICE.replace(' Plan', '')}" in text
            or "missionScriptGoodieStateSaveAppCoreBoundaryCorpusFixtureMatrixStatus=" in text,
            f"{path.relative_to(ROOT)} missing completed AppCore boundary-corpus fixture matrix lane",
            failures,
        )
        require(
            f"Completed {COMPLETED_GOODIE_BOUNDARY_SLICE}" in text
            or "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-complete" in text,
            f"{path.relative_to(ROOT)} missing completed Goodie boundary corpus harness lane",
            failures,
        )
        require(
            f"Completed {POST_GOODIE_SELECTION_SLICE}" in text
            or "missionscript-command-effect-post-goodie-selection-refresh-complete-cutscene-camera-position-selected" in text,
            f"{path.relative_to(ROOT)} missing completed post-Goodie selection refresh lane",
            failures,
        )
        require(
            f"The selected active static-to-proof slice is {NEXT_ACTIVE_SLICE}. Status: selected" in text
            or f"active next static child lane: {NEXT_ACTIVE_SLICE}" in text,
            f"{path.relative_to(ROOT)} missing active cutscene pan-camera/position fixture lane",
            failures,
        )

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (MISSIONSCRIPT_CONTRACT, LORE_MISSIONSCRIPT_CONTRACT),
        (GOODIES_SYSTEM, LORE_GOODIES_SYSTEM),
        (SAVE_FORMAT, LORE_SAVE_FORMAT),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-goodie-state-save-runtime-proof-readiness-gate")
        == r"py -3 tools\missionscript_goodie_state_save_runtime_proof_readiness_gate_probe.py --check",
        "missing runtime-proof readiness gate package script",
        failures,
    )
    require("test:missionscript-goodie-state-save-appcore-copied-baseline-codec-harness" in scripts, "missing AppCore harness prerequisite script", failures)
    require("test:missionscript-goodie-state-save-clean-room-codec-interface" in scripts, "missing clean-room prerequisite script", failures)
    require("test:missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof" in scripts, "missing copied-baseline prerequisite script", failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_prerequisites(failures)
    check_schema(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after readiness gate", failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    failures = run_check()
    if failures:
        print("MissionScript Goodie state/save runtime-proof readiness gate probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Goodie state/save runtime-proof readiness gate probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
