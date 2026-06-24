#!/usr/bin/env python3
"""Validate the MissionScript Level100 copied-profile screenshot capture proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture-proof.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.v1.json"
LAUNCH_WINDOW = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_screenshot_capture_2026-06-08.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

PROFILE_ID = "level100-clean-materialized-20260608-214752"
PRIVATE_PROFILE_ROOT = ROOT / "subagents" / "static-to-proof" / "level100-copied-profile-materialization" / PROFILE_ID
PRIVATE_EXE = PRIVATE_PROFILE_ROOT / "BEA.exe"
PRIVATE_BACKUP = PRIVATE_PROFILE_ROOT / "BEA.exe.original.backup"
PRIVATE_PROOF_DIR = PRIVATE_PROFILE_ROOT / "screenshot-capture.private"
PRIVATE_SUMMARY = PRIVATE_PROOF_DIR / "screenshot-capture-summary.private.json"
PRIVATE_PREVIEW = PRIVATE_PROOF_DIR / "start-game-profile-printonly.private.txt"
PRIVATE_WINDOW_SCAN = PRIVATE_PROOF_DIR / "window-scan.private.json"
PRIVATE_CAPTURE_JSON = PRIVATE_PROOF_DIR / "capture-helper.private.json"
PRIVATE_CAPTURE_PNG = PRIVATE_PROOF_DIR / "bea-window-capture.private.png"

PATCHED_SHA = "e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918"
EXPECTED_CLEAN_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PRIVATE_CAPTURE_SHA = "a2938f403ec8dded55f07f2cc6fd879aff135928b91095893dc6989052ce71c0"
BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Window Smoke Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan"
FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan"
VISUAL_FRAME_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Visual Frame Triage Proof Plan"
TEXT_OVERLAY_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Text Overlay Correlation Proof Plan"
TIMED_FRAME_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Capture Proof Plan"
TIMED_FRAME_TEXT_OVERLAY_PROGRESSION_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Text Overlay Progression Correlation Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture-proof.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.v1.json"

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
    "<PRIVATE_PATH_REDACTED>\\",
    PRIVATE_CAPTURE_SHA,
    "bea-window-capture.private.png",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "direct level100 route behavior proven",
    "runtime command effects proven",
    "runtime event outcomes proven",
    "live loose-msl loading proven",
    "packed-vs-loose script selection proven",
    "runtime level100 mission outcome proven",
    "visual correctness proven",
    "occlusion-free pixel correctness proven",
    "native input behavior proven",
    "debugger observation proven",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def no_bea_process_running() -> bool:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "if (Get-Process -Name BEA -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def check_private_evidence(failures: list[str]) -> None:
    for path, label in (
        (PRIVATE_EXE, "private copied BEA.exe"),
        (PRIVATE_BACKUP, "private clean backup"),
        (PRIVATE_SUMMARY, "private screenshot summary"),
        (PRIVATE_PREVIEW, "private launch preview"),
        (PRIVATE_WINDOW_SCAN, "private window scan"),
        (PRIVATE_CAPTURE_JSON, "private capture helper JSON"),
        (PRIVATE_CAPTURE_PNG, "private capture PNG"),
    ):
        require(path.is_file(), f"{label} missing", failures)

    require(PRIVATE_EXE.stat().st_size == 2506752, "private copied BEA.exe byte size mismatch", failures)
    require(PRIVATE_BACKUP.stat().st_size == 2506752, "private clean backup byte size mismatch", failures)
    require(sha256(PRIVATE_EXE) == PATCHED_SHA, "private copied BEA.exe patched hash mismatch", failures)
    require(sha256(PRIVATE_BACKUP) == EXPECTED_CLEAN_SHA, "private backup clean hash mismatch", failures)
    require(PRIVATE_CAPTURE_PNG.stat().st_size == 430347, "private capture PNG byte count mismatch", failures)
    require(sha256(PRIVATE_CAPTURE_PNG) == PRIVATE_CAPTURE_SHA, "private capture PNG hash mismatch", failures)

    summary = read_json(PRIVATE_SUMMARY)
    require(summary["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.private.v1", "private summary schema mismatch", failures)
    require(summary["status"] == "COMPLETE", "private summary status mismatch", failures)
    require(summary["selectedRoute"] == "skip-fmv-copied-profile-launch", "private selected route mismatch", failures)
    require(summary["directLevel100RouteStatus"] == "candidate-unproven-unarmed", "private direct route status mismatch", failures)
    require(summary["launchArguments"] == ["-skipfmv"], "private launch arguments mismatch", failures)
    require(summary["copiedTargetBefore"]["sha256"] == PATCHED_SHA, "private target before hash mismatch", failures)
    require(summary["copiedTargetAfter"]["sha256"] == PATCHED_SHA, "private target after hash mismatch", failures)
    require(summary["copiedBackupBefore"]["sha256"] == EXPECTED_CLEAN_SHA, "private backup before hash mismatch", failures)
    require(summary["copiedBackupAfter"]["sha256"] == EXPECTED_CLEAN_SHA, "private backup after hash mismatch", failures)
    require(summary["copiedTargetBefore"]["length"] == 2506752, "private target byte count mismatch", failures)
    require(summary["copiedBackupBefore"]["length"] == 2506752, "private backup byte count mismatch", failures)
    require(summary["observationDelaySeconds"] == 10, "private observation delay mismatch", failures)
    require(summary["captureExists"] is True, "private captureExists mismatch", failures)
    require(summary["capturePngBytes"] == 430347, "private capture byte count mismatch", failures)
    require(summary["capturePngSha256"] == PRIVATE_CAPTURE_SHA, "private capture hash mismatch", failures)
    require(summary["captureWidth"] == 656, "private capture width mismatch", failures)
    require(summary["captureHeight"] == 539, "private capture height mismatch", failures)
    require(summary["cleanupMethod"] == "CloseMainWindow", "private cleanup method mismatch", failures)
    require(summary["cleanupSucceeded"] is True, "private cleanup succeeded mismatch", failures)
    require(summary["beProcessesAfterCleanup"] == 0, "private cleanup process count mismatch", failures)
    for key in (
        "copiedTargetHashStableDuringCapture",
        "copiedBackupHashStableDuringCapture",
        "installedTargetHashStableDuringCapture",
        "installedBackupHashStableDuringCapture",
    ):
        require(summary[key] is True, f"private hash stability flag must be true: {key}", failures)
    for key in ("installedGameMutation", "originalExecutableMutation", "nativeInput", "debuggerAttachment", "godotWork"):
        require(summary[key] is False, f"private guard flag must be false: {key}", failures)
    require(summary["missionScriptRuntimeEvidenceRows"] == 0, "private MissionScript runtime rows mismatch", failures)

    scan = read_json(PRIVATE_WINDOW_SCAN)
    require(scan["schemaVersion"] == "game-window-scan-helper.v1", "window scan schema mismatch", failures)
    require(scan["status"] == "ready", "window scan status mismatch", failures)
    require(len(scan["windows"]) == 1, "window scan candidate count mismatch", failures)
    window = scan["windows"][0]
    require(window["title"] == "BEA", "window title mismatch", failures)
    require(window["visible"] is True, "window visible mismatch", failures)
    require(window["minimized"] is False, "window minimized mismatch", failures)
    require(window["bounds"]["width"] == 656, "window width mismatch", failures)
    require(window["bounds"]["height"] == 539, "window height mismatch", failures)

    capture = read_json(PRIVATE_CAPTURE_JSON)
    require(capture["schemaVersion"] == "game-window-capture-helper.v1", "capture helper schema mismatch", failures)
    require(capture["status"] == "captured", "capture helper status mismatch", failures)
    require(capture["bounds"]["width"] == 656, "capture helper width mismatch", failures)
    require(capture["bounds"]["height"] == 539, "capture helper height mismatch", failures)
    require(no_bea_process_running(), "BEA process still running after screenshot proof", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(result == read_json(LORE_RESULT), "lore screenshot result mirror mismatch", failures)
    require(read_json(LAUNCH_WINDOW)["nextStaticSlice"] == THIS_SLICE, "launch-window result does not point to screenshot lane", failures)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.v1", "schemaVersion mismatch", failures)
    require(result["status"] == "COMPLETE", "status mismatch", failures)
    require(result["screenshotCaptureStatus"] == "copied-profile-window-still-frame-captured", "screenshotCaptureStatus mismatch", failures)
    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function-quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(static["latestGhidraBackup"] == BACKUP, "latest Ghidra backup mismatch", failures)

    proof = result["screenshotCaptureProof"]
    require(proof["profileId"] == PROFILE_ID, "profile id mismatch", failures)
    require(proof["artifactRootClass"] == "repo-local-ignored-private-evidence-root", "artifact root class mismatch", failures)
    require(proof["targetExecutableClass"] == "copied-profile-BEA.exe", "target executable class mismatch", failures)
    require(proof["workingDirectoryClass"] == "copied-profile-root", "working directory class mismatch", failures)
    require(proof["privatePathIncluded"] is False, "private path flag mismatch", failures)
    require(proof["rawArtifactIncluded"] is False, "raw artifact flag mismatch", failures)
    require(proof["targetHashBefore"] == PATCHED_SHA, "target before hash mismatch", failures)
    require(proof["targetHashAfter"] == PATCHED_SHA, "target after hash mismatch", failures)
    require(proof["backupHashBefore"] == EXPECTED_CLEAN_SHA, "backup before hash mismatch", failures)
    require(proof["backupHashAfter"] == EXPECTED_CLEAN_SHA, "backup after hash mismatch", failures)
    require(proof["targetBytes"] == 2506752, "target byte count mismatch", failures)
    require(proof["backupBytes"] == 2506752, "backup byte count mismatch", failures)
    require(proof["patchStatus"] == "stable-copied-executable-patched", "patch status mismatch", failures)
    require(proof["stablePatchRows"] == 4, "stable patch rows mismatch", failures)
    require(proof["skipAutoToggleArmed"] is False, "skip auto toggle mismatch", failures)
    require(proof["selectedRoute"] == "skip-fmv-copied-profile-launch", "selected route mismatch", failures)
    require(proof["launchArguments"] == ["-skipfmv"], "launch arguments mismatch", failures)
    require(proof["directLevel100RouteStatus"] == "candidate-unproven-unarmed", "direct Level100 route status mismatch", failures)
    require(proof["launchHelper"] == "tools/start_game_profile.ps1", "launch helper mismatch", failures)
    require(proof["launchHelperSchema"] == "game-launch-process.v1", "launch helper schema mismatch", failures)
    require(proof["windowScanHelper"] == "tools/list_game_windows.ps1", "window scan helper mismatch", failures)
    require(proof["windowScanHelperSchema"] == "game-window-scan-helper.v1", "window scan schema mismatch", failures)
    require(proof["captureHelper"] == "tools/capture_game_window.ps1", "capture helper mismatch", failures)
    require(proof["captureHelperSchema"] == "game-window-capture-helper.v1", "capture helper schema mismatch", failures)
    for key in (
        "freshPrintOnlyPreviewChecked",
        "launchArmed",
        "beLaunch",
        "launchCommandExecuted",
        "processStarted",
        "processAliveAfterDelay",
        "exactPidHwndWindowMatch",
        "mainWindowHandleObserved",
        "windowVisible",
        "windowNotMinimized",
        "respondingAfterDelay",
        "boundedProcessLifetime",
    ):
        require(proof[key] is True, f"proof flag must be true: {key}", failures)
    require(proof["beProcessesBefore"] == 0, "BEA process precheck mismatch", failures)
    require(proof["observationDelaySeconds"] == 10, "observation delay mismatch", failures)
    require(proof["windowCandidateCount"] == 1, "window candidate count mismatch", failures)
    require(proof["mainWindowTitleClass"] == "BEA", "window title class mismatch", failures)
    require(proof["captureFrameCount"] == 1, "capture frame count mismatch", failures)
    require(proof["captureStatus"] == "captured", "capture status mismatch", failures)
    require(proof["captureWidth"] == 656, "capture width mismatch", failures)
    require(proof["captureHeight"] == 539, "capture height mismatch", failures)
    require(proof["captureArtifactClass"] == "private-still-frame-png", "capture artifact class mismatch", failures)
    require(proof["captureArtifactBytesRecordedPrivately"] is True, "capture byte recording flag mismatch", failures)
    require(proof["captureArtifactHashRecordedPrivately"] is True, "capture hash recording flag mismatch", failures)
    require(proof["captureArtifactPublished"] is False, "capture artifact publication flag mismatch", failures)
    require(proof["cleanupMethod"] == "CloseMainWindow", "cleanup method mismatch", failures)
    require(proof["processCleanup"] == "PASS", "process cleanup mismatch", failures)
    require(proof["processAliveAfterCleanup"] is False, "process alive after cleanup mismatch", failures)
    require(proof["beProcessesAfterCleanup"] == 0, "BEA after cleanup mismatch", failures)
    require(proof["windowSmokeObservationRows"] == 1, "window smoke rows mismatch", failures)
    require(proof["screenshotCaptureEvidenceRows"] == 1, "screenshot evidence rows mismatch", failures)
    require(proof["missionScriptRuntimeEvidenceRows"] == 0, "MissionScript runtime rows mismatch", failures)
    for key in (
        "copiedTargetHashStableDuringCapture",
        "copiedBackupHashStableDuringCapture",
        "installedTargetHashStableDuringCapture",
        "installedBackupHashStableDuringCapture",
    ):
        require(proof[key] is True, f"hash stability flag must be true: {key}", failures)
    for key in ("installedGameMutation", "originalExecutableMutation"):
        require(proof[key] is False, f"mutation flag must be false: {key}", failures)

    guard = result["guardSummary"]
    for key in (
        "copiedExecutablePatch",
        "launchWindowSmokeProof",
        "screenshotCaptureProof",
        "beLaunch",
        "launchArmed",
        "launchCommandExecuted",
        "processStarted",
        "exactPidHwndWindowMatch",
        "boundedProcessLifetime",
    ):
        require(guard[key] is True, f"guard flag must be true: {key}", failures)
    require(guard["captureFrameCount"] == 1, "guard capture frame count mismatch", failures)
    require(guard["captureStatus"] == "captured", "guard capture status mismatch", failures)
    require(guard["captureArtifactPublished"] is False, "guard capture publication mismatch", failures)
    require(guard["processCleanup"] == "PASS", "guard process cleanup mismatch", failures)
    for key in ("installedGameMutation", "originalExecutableMutation", "nativeInput", "debuggerAttachment", "godotWork"):
        require(guard[key] is False, f"guard flag must be false: {key}", failures)
    require(guard["missionScriptRuntimeEvidenceRows"] == 0, "guard MissionScript runtime rows mismatch", failures)
    require(guard["privatePathLeakCount"] == 0, "private path leak count mismatch", failures)
    require(guard["rawArtifactLeakCount"] == 0, "raw artifact leak count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore screenshot plan mirror mismatch", failures)
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore screenshot result mirror mismatch", failures)

    core_tokens = (
        "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture",
        "complete copied-profile screenshot capture proof, not MissionScript/runtime behavior or visual correctness proof",
        PLAN_LINK,
        RESULT_LINK,
        PREVIOUS_SLICE,
        "status=COMPLETE",
        "screenshotCaptureStatus=copied-profile-window-still-frame-captured",
        f"profileId={PROFILE_ID}",
        "targetExecutableClass=copied-profile-BEA.exe",
        "workingDirectoryClass=copied-profile-root",
        "selectedRoute=skip-fmv-copied-profile-launch",
        "directLevel100Route=direct-level100-candidate",
        "directLevel100RouteStatus=candidate-unproven-unarmed",
        "launchHelper=tools/start_game_profile.ps1",
        "launchHelperSchema=game-launch-process.v1",
        "windowScanHelper=tools/list_game_windows.ps1",
        "windowScanHelperSchema=game-window-scan-helper.v1",
        "captureHelper=tools/capture_game_window.ps1",
        "captureHelperSchema=game-window-capture-helper.v1",
        "freshPrintOnlyPreviewChecked=true",
        "launchArmed=true",
        "beLaunch=true",
        "launchCommandExecuted=true",
        "processStarted=true",
        "processAliveAfterDelay=true",
        "observationDelaySeconds=10",
        "windowCandidateCount=1",
        "exactPidHwndWindowMatch=true",
        "mainWindowHandleObserved=true",
        "mainWindowTitleClass=BEA",
        "windowVisible=true",
        "windowNotMinimized=true",
        "captureFrameCount=1",
        "captureStatus=captured",
        "captureWidth=656",
        "captureHeight=539",
        "captureArtifactClass=private-still-frame-png",
        "captureArtifactBytesRecordedPrivately=true",
        "captureArtifactHashRecordedPrivately=true",
        "captureArtifactPublished=false",
        "cleanupMethod=CloseMainWindow",
        "processCleanup=PASS",
        "processAliveAfterCleanup=false",
        "beProcessesBefore=0",
        "beProcessesAfterCleanup=0",
        f"targetHashBefore={PATCHED_SHA}",
        f"targetHashAfter={PATCHED_SHA}",
        f"backupHashBefore={EXPECTED_CLEAN_SHA}",
        f"backupHashAfter={EXPECTED_CLEAN_SHA}",
        "targetBytes=2506752",
        "backupBytes=2506752",
        "stablePatchRows=4",
        "skipAutoToggleArmed=false",
        "installedGameMutation=false",
        "originalExecutableMutation=false",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "windowSmokeObservationRows=1",
        "screenshotCaptureEvidenceRows=1",
        "missionScriptRuntimeEvidenceRows=0",
        "privatePathLeakCount=0",
        "rawArtifactLeakCount=0",
        "publicLeakCheck=PASS",
        "0x00539dc0",
        "0x00539ca0",
        "CDXMemBuffer__InitFromFile",
        BACKUP,
        NEXT_SLICE,
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_tokens(path, failures)

    front_door_tokens = (
        PLAN_LINK,
        RESULT_LINK,
        THIS_SLICE,
        NEXT_SLICE,
        PROFILE_ID,
        "copied-profile-window-still-frame-captured",
        "selectedRoute=skip-fmv-copied-profile-launch",
        "windowScanHelper=tools/list_game_windows.ps1",
        "captureHelper=tools/capture_game_window.ps1",
        "captureFrameCount=1",
        "captureStatus=captured",
        "captureWidth=656",
        "captureHeight=539",
        "captureArtifactPublished=false",
        "missionScriptRuntimeEvidenceRows=0",
        FOLLOW_UP_SLICE,
        VISUAL_FRAME_SLICE,
        TEXT_OVERLAY_SLICE,
        TIMED_FRAME_SLICE,
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing screenshot capture token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed screenshot capture slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed direct Level100 launch smoke slice", failures)
    require(f"Completed {FOLLOW_UP_SLICE}" in backlog, "backlog missing completed direct Level100 screenshot slice", failures)
    require(f"Completed {VISUAL_FRAME_SLICE}" in backlog, "backlog missing completed direct Level100 visual frame triage slice", failures)
    require(f"Completed {TEXT_OVERLAY_SLICE}" in backlog, "backlog missing completed direct Level100 text overlay correlation slice", failures)
    require(f"Completed {TIMED_FRAME_SLICE}" in backlog, "backlog missing completed direct Level100 timed-frame set slice", failures)
    require(f"The selected active static-to-proof slice is {TIMED_FRAME_TEXT_OVERLAY_PROGRESSION_SLICE}" in backlog, "backlog missing active direct Level100 timed-frame text-overlay progression slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks screenshot capture proof as selected active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_screenshot_capture_probe.py --check",
        "missing package screenshot capture test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_private_evidence(failures)
    check_result(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("MissionScript Level100 screenshot capture probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 screenshot capture probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
