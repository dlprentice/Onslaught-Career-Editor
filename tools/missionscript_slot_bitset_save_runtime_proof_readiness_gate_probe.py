#!/usr/bin/env python3
"""Validate MissionScript slot bitset/save runtime-proof readiness gate."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-runtime-proof-readiness-gate.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-runtime-proof-readiness-gate.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-runtime-proof-readiness-gate.md"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-runtime-proof-readiness-gate.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_slot_bitset_save_runtime_proof_readiness_gate_2026-06-09.md"

HARNESS_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness.v1.json"
CLEAN_ROOM_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-clean-room-codec-interface.v1.json"
COPIED_FILE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-copied-file-byte-diff.v1.json"
DETERMINISTIC_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-deterministic-codec-proof-plan.v1.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Slot Bitset/Save Runtime-Proof Readiness Gate"
THIS_STATUS = "missionscript-slot-bitset-save-runtime-proof-readiness-gate-complete-runtime-deferred-no-launch"
PREVIOUS_SLICE = "MissionScript Slot Bitset/Save AppCore Copied-Baseline Codec Harness Proof"
PREVIOUS_STATUS = "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-complete-appcore-copied-real-baseline-byte-preservation-not-runtime-proof"
NEXT_SLICE = "MissionScript Slot Bitset/Save AppCore Boundary-Slot Corpus Proof Plan"
ACTIVE_AFTER_NEXT_SLICE = "Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan"

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
    "runtime slot persistence proven",
    "runtime save/load behavior proven",
    "runtime defaultoptions behavior proven",
    "tutorial progression proven",
    "source selection proven",
    "private-frame review complete",
    "screenshot interpretation complete",
    "installed game mutation proven",
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
        "schemaVersion": "missionscript-slot-bitset-save-runtime-proof-readiness-gate.v1",
        "status": "PASS",
        "slotBitsetSaveRuntimeProofReadinessGateStatus": THIS_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "slot-bitset-save",
        "selectedFixturePath": "slot-bitset-save-core-handler-and-career-bridge",
        "decision": {
            "runtimeReadinessGateComplete": True,
            "runtimeObservationReadyNow": False,
            "runtimeDeferred": True,
            "deferReason": "explicit-runtime-observation-arm-absent-continue-non-runtime-code-test-proof",
            "nextLaneClass": "non-runtime AppCore code/test proof",
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
            "cleanRoomCodecInterfaceStatus": "missionscript-slot-bitset-save-clean-room-codec-interface-complete-appcore-pure-buffer-contract-not-runtime-proof",
            "copiedFileByteDiffStatus": "missionscript-slot-bitset-save-copied-file-byte-diff-complete-copied-real-baseline-not-runtime-proof",
            "deterministicCodecProofPlanStatus": "missionscript-slot-bitset-save-deterministic-codec-proof-plan-complete-pure-codec-not-runtime-proof",
            "slotCommandFixtureFamily": "slot-bitset-save",
            "appCoreCodecUsed": True,
            "manualSlotDwordWriteInHarness": False,
            "sourcePathsPublic": False,
            "sourceHashesPublic": False,
            "artifactPathsPublic": False,
            "artifactHashesPublic": False,
            "rawBeforeAfterDwordsPublic": False,
            "copyBeforeWrite": True,
            "sourceAndOutputPathsDistinct": True,
            "sourceToNewBaselineDiffCount": 0,
            "sourceUnchanged": True,
            "observedDwordXorMask": "0x60000000",
            "baselineToSetChangedOffsets": ["0x2411"],
            "clearToBaselineDiffCount": 0,
        },
        "laterRuntimeArmRequirements": {
            "explicitRuntimeObservationArmRequired": True,
            "copiedProfileRequired": True,
            "copiedExecutableRequired": True,
            "appOwnedArtifactRootRequired": True,
            "runtimeSpecimenAuthorityRequired": True,
            "patchCatalogVerificationRequired": True,
            "windowedPatchAllowedOnlyOnCopiedProfile": True,
            "privateOutputReviewAvailabilityRequired": True,
            "publicSafeRedactionRequired": True,
            "stopConditionsRequired": True,
        },
        "negativeGuards": {
            "runtimeExecution": False,
            "beLaunch": False,
            "newLaunch": False,
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
            "ghidraMutation": False,
            "executablePatching": False,
            "godotWork": False,
            "productUiWired": False,
            "rebuildImplementation": False,
            "runtimeMissionScriptExecutionProven": False,
            "runtimeCommandEffectsProven": False,
            "runtimeSlotPersistenceProven": False,
            "runtimeSaveLoadBehaviorProven": False,
            "runtimeDefaultoptionsBehaviorProven": False,
            "rebuildParityProven": False,
            "noNoticeableDifferenceParityProven": False,
            "runtimeObservationRows": 0,
            "missionScriptRuntimeEvidenceRows": 0,
            "runtimeCommandEffectRows": 0,
            "runtimeSaveRows": 0,
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
            "reason": "expand the AppCore slot bitset/save proof across representative slot boundary cases while runtime observation remains deferred",
            "runtimeExecution": False,
            "beLaunch": False,
            "ghidraMutation": False,
            "executablePatching": False,
            "godotWork": False,
            "rebuildImplementation": False,
        },
        "claimBoundary": {
            "proves": [
                "the MissionScript slot bitset/save runtime-proof path has a public-safe readiness gate",
                "the upstream AppCore and copied-baseline proof stack is sufficient for non-runtime code/test continuation",
                "runtime observation is deferred until an explicit runtime-observation arm and copied-profile safety packet exist",
                "the next selected safe slice is a non-runtime AppCore boundary-slot corpus proof plan",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime slot persistence",
                "runtime save/load behavior",
                "runtime defaultoptions behavior",
                "tutorial progression",
                "live loose-MSL loading",
                "packed-resource script selection",
                "source selection",
                "private-frame review",
                "screenshot or frame interpretation",
                "native input",
                "debugger behavior",
                "installed game mutation",
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
    copied = read_json(COPIED_FILE_SCHEMA)
    deterministic = read_json(DETERMINISTIC_SCHEMA)
    require(harness["slotBitsetSaveAppCoreCopiedBaselineCodecHarnessStatus"] == PREVIOUS_STATUS, "harness prerequisite status mismatch", failures)
    require(harness["selectedNextSlice"] == "MissionScript Slot Bitset/Save Runtime-Proof Readiness Gate Plan", "harness prerequisite next-slice mismatch", failures)
    require(harness["implementation"]["appCoreCodecUsed"] is True, "harness prerequisite AppCore use mismatch", failures)
    require(harness["implementation"]["manualSlotDwordWriteInHarness"] is False, "harness prerequisite manual write guard mismatch", failures)
    require(harness["privateEvidence"]["copyBeforeWrite"] is True, "harness prerequisite copy-before-write mismatch", failures)
    require(harness["privateEvidence"]["sourcePathsPublic"] is False, "harness source disclosure mismatch", failures)
    require(harness["slotWrite"]["observedDwordXorMask"] == "0x60000000", "harness observed XOR mismatch", failures)
    require(harness["noOpAndRoundTrip"]["clearToBaselineDiffCount"] == 0, "harness clear roundtrip mismatch", failures)
    require(clean["slotBitsetSaveCleanRoomCodecInterfaceStatus"] == expected_schema()["upstreamProofs"]["cleanRoomCodecInterfaceStatus"], "clean-room status mismatch", failures)
    require(copied["slotBitsetSaveCopiedFileByteDiffStatus"] == expected_schema()["upstreamProofs"]["copiedFileByteDiffStatus"], "copied-file status mismatch", failures)
    require(deterministic["slotBitsetSaveDeterministicCodecProofPlanStatus"] == expected_schema()["upstreamProofs"]["deterministicCodecProofPlanStatus"], "deterministic status mismatch", failures)


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
        "missionscript-slot-bitset-save-runtime-proof-readiness-gate.v1.json",
        "runtimeReadinessGateComplete=true",
        "runtimeObservationReadyNow=false",
        "runtimeDeferred=true",
        "deferReason=explicit-runtime-observation-arm-absent-continue-non-runtime-code-test-proof",
        "explicitRuntimeObservationArmPresent=false",
        "operatorPrivateOutputReviewAvailable=false",
        "copiedProfileRequired=true",
        "copiedExecutableRequired=true",
        "appOwnedArtifactRootRequired=true",
        "runtimeSpecimenAuthorityRequired=true",
        "patchCatalogVerificationRequired=true",
        "windowedPatchAllowedOnlyOnCopiedProfile=true",
        "installedGameMutationAllowed=false",
        "originalExecutableMutationAllowed=false",
        "runtimeExecution=false",
        "beLaunch=false",
        "newLaunch=false",
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
        "runtimeSaveRows=0",
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
        "missionscript-slot-bitset-save-runtime-proof-readiness-gate.md",
        "missionscript-slot-bitset-save-runtime-proof-readiness-gate.v1.json",
        f"selectedNextSlice={NEXT_SLICE}",
        "runtimeObservationReadyNow=false",
        "runtimeDeferred=true",
        "explicitRuntimeObservationArmPresent=false",
        "beLaunch=false",
        "runtimeObservationRows=0",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            "The selected active static-to-proof slice is MissionScript Slot Bitset/Save Runtime-Proof Readiness Gate Plan. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks readiness gate as active",
            failures,
        )
        require(
            f"The selected active static-to-proof slice is {ACTIVE_AFTER_NEXT_SLICE}. Status: selected" in text
            or f"active next static child lane: {ACTIVE_AFTER_NEXT_SLICE}" in text,
            f"{path.relative_to(ROOT)} missing active copied-baseline boundary corpus harness lane",
            failures,
        )

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-slot-bitset-save-runtime-proof-readiness-gate")
        == r"py -3 tools\missionscript_slot_bitset_save_runtime_proof_readiness_gate_probe.py --check",
        "missing runtime-proof readiness gate package script",
        failures,
    )
    require("test:missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness" in scripts, "missing harness prerequisite script", failures)


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
        print("MissionScript slot bitset/save runtime-proof readiness gate probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript slot bitset/save runtime-proof readiness gate probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
