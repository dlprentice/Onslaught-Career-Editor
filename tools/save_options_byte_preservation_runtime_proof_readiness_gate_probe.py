#!/usr/bin/env python3
"""Validate Save / Options byte-preservation runtime-readiness gate."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-runtime-proof-readiness-gate.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-runtime-proof-readiness-gate.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-runtime-proof-readiness-gate.md"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-runtime-proof-readiness-gate.v1.json"
READINESS = ROOT / "release" / "readiness" / "save_options_byte_preservation_runtime_proof_readiness_gate_2026-06-09.md"

APPCORE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-appcore-implementation-contract.v1.json"
COPIED_FILE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-copied-file.v1.json"
PROOF_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-proof-plan.md"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
SAVE_INDEX = ROOT / "reverse-engineering" / "save-file" / "_index.md"
LORE_SAVE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "_index.md"
SAVE_FORMAT = ROOT / "reverse-engineering" / "save-file" / "save-format.md"
LORE_SAVE_FORMAT = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "save-format.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "Save / Options Byte-Preservation Runtime-Proof Readiness Gate"
THIS_STATUS = "save-options-byte-preservation-runtime-proof-readiness-gate-complete-runtime-deferred-no-launch"
PREVIOUS_SLICE = "Save / Options Byte-Preservation AppCore Implementation Contract Proof"
PREVIOUS_STATUS = "save-options-byte-preservation-appcore-implementation-contract-complete-copied-real-baseline-services-not-runtime-proof"
NEXT_SLICE = "Save / Options Byte-Preservation AppCore Fixture Matrix Proof Plan"
SCHEMA_NAME = "save-options-byte-preservation-runtime-proof-readiness-gate.v1.json"
PROOF_NAME = "save-options-byte-preservation-runtime-proof-readiness-gate.md"

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
    "runtime save/load behavior proven",
    "runtime defaultoptions boot behavior proven",
    "runtime menu behavior proven",
    "runtime controller remap/input behavior proven",
    "runtime goodies wall behavior proven",
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
        "schemaVersion": "save-options-byte-preservation-runtime-proof-readiness-gate.v1",
        "status": "PASS",
        "saveOptionsBytePreservationRuntimeProofReadinessGateStatus": THIS_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "decision": {
            "runtimeReadinessGateComplete": True,
            "runtimeObservationReadyNow": False,
            "runtimeDeferred": True,
            "deferReason": "explicit-runtime-observation-arm-and-private-output-review-absent-continue-non-runtime-appcore-fixture-matrix-proof",
            "nextLaneClass": "non-runtime AppCore fixture matrix proof",
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
            "appCoreImplementationContractStatus": PREVIOUS_STATUS,
            "copiedFileBytePreservationStatus": "save-options-controller-byte-preservation-copied-file.v1",
            "proofPlan": "save-options-controller-byte-preservation-proof-plan.md",
            "appCoreServicesUsed": True,
            "appCoreServiceProofCaseCount": 8,
            "copiedArtifactCount": 10,
            "sourcePathsPublic": False,
            "sourceHashesPublic": False,
            "artifactPathsPublic": False,
            "artifactHashesPublic": False,
            "rawBytesPublic": False,
            "copyBeforeWrite": True,
            "sourceAndOutputPathsDistinct": True,
            "careerSourceUnchanged": True,
            "defaultOptionsSourceUnchanged": True,
            "careerSourceToInputDiffCount": 0,
            "defaultOptionsSourceToInputDiffCount": 0,
            "optionsLikeInputRejected": True,
            "inPlaceRejected": True,
            "metadataBytePreserved": True,
            "lower24Changed": True,
            "legacyTrapHitCount": 0,
            "techSlotsRangeUnchanged": True,
            "optionsEntriesUnchanged": True,
            "optionsTailUnchanged": True,
            "slotCodecFileIo": False,
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
            "runtimeSaveLoadBehaviorProven": False,
            "runtimeDefaultoptionsBehaviorProven": False,
            "runtimeMenuBehaviorProven": False,
            "runtimeControllerBehaviorProven": False,
            "runtimeGoodiesWallBehaviorProven": False,
            "rebuildParityProven": False,
            "noNoticeableDifferenceParityProven": False,
            "runtimeObservationRows": 0,
            "runtimeSaveRows": 0,
            "runtimeDefaultOptionsRows": 0,
            "publicAbsolutePathLeakCount": 0,
            "publicSha256ValueLeakCount": 0,
            "publicWindowIdentifierLeakCount": 0,
            "publicProcessIdentifierLeakCount": 0,
            "privatePathLeakCount": 0,
            "rawArtifactLeakCount": 0,
            "publicLeakCheck": "PASS",
        },
        "nextNonRuntimeSlice": {
            "selectedNextSlice": NEXT_SLICE,
            "reason": "expand AppCore save/options byte-preservation coverage across representative career, defaultoptions, controller, slot, no-op, rejection, and legacy-trap fixture cases while runtime observation remains deferred",
            "runtimeExecution": False,
            "beLaunch": False,
            "ghidraMutation": False,
            "executablePatching": False,
            "godotWork": False,
            "rebuildImplementation": False,
        },
        "claimBoundary": {
            "proves": [
                "the save/options byte-preservation runtime-proof path has a public-safe readiness gate",
                "the upstream copied-file and AppCore implementation-contract proof stack is sufficient for non-runtime AppCore fixture-matrix continuation",
                "runtime save/load/defaultoptions observation is deferred until an explicit runtime-observation arm and copied-profile safety packet exist",
                "the next selected safe slice is a non-runtime AppCore fixture matrix proof plan",
            ],
            "doesNotProve": [
                "runtime save/load behavior",
                "runtime defaultoptions boot behavior",
                "runtime menu behavior",
                "runtime controller remap/input behavior",
                "runtime Goodies wall behavior",
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
    appcore = read_json(APPCORE_SCHEMA)
    copied = read_json(COPIED_FILE_SCHEMA)
    plan = read_text(PROOF_PLAN)

    require(appcore["saveOptionsBytePreservationAppCoreImplementationContractStatus"] == PREVIOUS_STATUS, "AppCore prerequisite status mismatch", failures)
    require(appcore["selectedNextSlice"] == "Save / Options Byte-Preservation Runtime-Proof Readiness Gate Plan", "AppCore prerequisite next-slice mismatch", failures)
    require(appcore["implementation"]["appCoreServicesUsed"] is True, "AppCore service-use prerequisite mismatch", failures)
    require(appcore["appCoreServiceProof"]["appCoreServiceProofCaseCount"] == 8, "AppCore service case count mismatch", failures)
    require(appcore["privateEvidence"]["copyBeforeWrite"] is True, "AppCore copy-before-write mismatch", failures)
    require(appcore["negativeGuards"]["runtimeExecution"] is False, "AppCore runtime guard mismatch", failures)
    require(appcore["negativeGuards"]["beLaunch"] is False, "AppCore launch guard mismatch", failures)
    require(appcore["negativeGuards"]["runtimeSaveLoadProof"] is False, "AppCore runtime save/load guard mismatch", failures)
    require(appcore["negativeGuards"]["runtimeDefaultOptionsProof"] is False, "AppCore runtime defaultoptions guard mismatch", failures)

    require(copied["status"] == "PASS", "copied-file prerequisite status mismatch", failures)
    require(copied["source"]["runtimeExecution"] is False, "copied-file runtime guard mismatch", failures)
    require(copied["source"]["gameLaunch"] is False, "copied-file launch guard mismatch", failures)
    require(copied["baselineEvidence"]["copiedArtifactCount"] == 5, "copied-file artifact count mismatch", failures)
    require(copied["scopedCareerEdit"]["legacyTrapHitCount"] == 0, "copied-file legacy trap mismatch", failures)
    require(copied["scopedCareerEdit"]["metadataBytePreserved"] is True, "copied-file metadata mismatch", failures)
    require("copied real `.bes` and `defaultoptions.bea` buffers" in plan, "proof plan missing copied-baseline guardrails", failures)
    require("Stop conditions" in plan, "proof plan missing stop conditions", failures)


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
        "deferReason=explicit-runtime-observation-arm-and-private-output-review-absent-continue-non-runtime-appcore-fixture-matrix-proof",
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
        "runtimeSaveRows=0",
        "runtimeDefaultOptionsRows=0",
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
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, SAVE_INDEX, SAVE_FORMAT):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            "The selected active static-to-proof slice is Save / Options Byte-Preservation Runtime-Proof Readiness Gate Plan. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks runtime-readiness gate active",
            failures,
        )
        require(
            f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in text
            or f"active next static child lane: {NEXT_SLICE}" in text,
            f"{path.relative_to(ROOT)} missing next AppCore fixture matrix lane",
            failures,
        )

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (SAVE_INDEX, LORE_SAVE_INDEX),
        (SAVE_FORMAT, LORE_SAVE_FORMAT),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:save-options-byte-preservation-runtime-proof-readiness-gate")
        == r"py -3 tools\save_options_byte_preservation_runtime_proof_readiness_gate_probe.py --check",
        "missing runtime-proof readiness gate package script",
        failures,
    )
    require("test:save-options-byte-preservation-appcore-implementation-contract" in scripts, "missing AppCore prerequisite script", failures)
    require("test:save-options-controller-byte-preservation-copied-file" in scripts, "missing copied-file prerequisite script", failures)


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
        print("Save / Options runtime-proof readiness gate probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Save / Options runtime-proof readiness gate probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
