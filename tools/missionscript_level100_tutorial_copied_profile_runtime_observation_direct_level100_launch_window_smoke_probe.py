#!/usr/bin/env python3
"""Validate the MissionScript Level100 direct copied-profile launch-window smoke proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke-proof.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1.json"
SCREENSHOT_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_launch_window_smoke_2026-06-08.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"
LIST_WINDOWS = ROOT / "tools" / "list_game_windows.ps1"
CAPTURE_WINDOW = ROOT / "tools" / "capture_game_window.ps1"

PROFILE_ID = "level100-clean-materialized-20260608-214752"
PRIVATE_PROFILE_ROOT = ROOT / "subagents" / "static-to-proof" / "level100-copied-profile-materialization" / PROFILE_ID
PRIVATE_EXE = PRIVATE_PROFILE_ROOT / "BEA.exe"
PRIVATE_BACKUP = PRIVATE_PROFILE_ROOT / "BEA.exe.original.backup"
PRIVATE_PROOF_ROOT = PRIVATE_PROFILE_ROOT / "direct-level100-launch-window-smoke.private"

PATCHED_SHA = "e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918"
EXPECTED_CLEAN_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan"
FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Visual Frame Triage Proof Plan"
SECOND_FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Text Overlay Correlation Proof Plan"
THIRD_FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Capture Proof Plan"
FOURTH_FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Text Overlay Progression Correlation Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke-proof.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1.json"

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
    "<PRIVATE_PATH_REDACTED>\\",
    "processId",
    "hwnd",
    "captureSourceHint",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "level100 script source selection proven",
    "runtime command effects proven",
    "runtime event outcomes proven",
    "live loose-msl loading proven",
    "packed-vs-loose script selection proven",
    "runtime level100 mission outcome proven",
    "visual correctness proven",
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


def latest_private_summary() -> Path:
    attempts = sorted(path for path in PRIVATE_PROOF_ROOT.glob("attempt-*") if path.is_dir())
    if not attempts:
        raise FileNotFoundError(PRIVATE_PROOF_ROOT)
    return attempts[-1] / "direct-level100-launch-window-smoke-summary.private.json"


def check_private_evidence(failures: list[str]) -> None:
    require(PRIVATE_EXE.is_file(), "private copied BEA.exe missing", failures)
    require(PRIVATE_BACKUP.is_file(), "private clean backup missing", failures)
    require(PRIVATE_EXE.stat().st_size == 2506752, "private copied BEA.exe byte size mismatch", failures)
    require(PRIVATE_BACKUP.stat().st_size == 2506752, "private clean backup byte size mismatch", failures)
    require(sha256(PRIVATE_EXE) == PATCHED_SHA, "private copied BEA.exe patched hash mismatch", failures)
    require(sha256(PRIVATE_BACKUP) == EXPECTED_CLEAN_SHA, "private backup clean hash mismatch", failures)

    summary = read_json(latest_private_summary())
    require(summary["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.private.v1", "private summary schema mismatch", failures)
    require(summary["status"] == "COMPLETE", "private summary status mismatch", failures)
    require(summary["selectedRoute"] == "direct-level100-candidate", "private selected route mismatch", failures)
    require(summary["launchArguments"] == ["-skipfmv", "-level", "100"], "private launch arguments mismatch", failures)
    require(summary["beProcessesBefore"] == 0, "private BEA precheck mismatch", failures)
    require(summary["processStarted"] is True, "private processStarted mismatch", failures)
    require(summary["processAliveAfterDelay"] is True, "private processAliveAfterDelay mismatch", failures)
    require(summary["respondingAfterDelay"] is True, "private respondingAfterDelay mismatch", failures)
    require(summary["observationDelaySeconds"] == 15, "private observation delay mismatch", failures)
    require(summary["windowScanStatus"] == "ready", "private window scan status mismatch", failures)
    require(summary["windowCandidateCount"] == 1, "private window candidate count mismatch", failures)
    require(summary["exactPidWindowCount"] == 1, "private exact PID window count mismatch", failures)
    require(summary["exactPidWindowTitle"] == "BEA", "private exact PID window title mismatch", failures)
    require(summary["exactPidWindowVisible"] is True, "private exact PID window visible mismatch", failures)
    require(summary["exactPidWindowMinimized"] is False, "private exact PID window minimized mismatch", failures)
    require(summary["cleanupMethod"] == "CloseMainWindow", "private cleanup method mismatch", failures)
    require(summary["cleanupSucceeded"] is True, "private cleanup succeeded mismatch", failures)
    require(summary["beProcessesAfterCleanup"] == 0, "private cleanup process count mismatch", failures)
    require(summary["hashBefore"]["copiedTarget"] == PATCHED_SHA, "private target before hash mismatch", failures)
    require(summary["hashAfter"]["copiedTarget"] == PATCHED_SHA, "private target after hash mismatch", failures)
    require(summary["hashBefore"]["copiedBackup"] == EXPECTED_CLEAN_SHA, "private backup before hash mismatch", failures)
    require(summary["hashAfter"]["copiedBackup"] == EXPECTED_CLEAN_SHA, "private backup after hash mismatch", failures)
    require(summary["bytes"]["copiedTarget"] == 2506752, "private copied target byte count mismatch", failures)
    require(summary["bytes"]["copiedBackup"] == 2506752, "private copied backup byte count mismatch", failures)
    for key in ("copiedTargetHashStable", "copiedBackupHashStable", "installedTargetHashStable", "installedBackupHashStable"):
        require(summary[key] is True, f"private hash stability flag must be true: {key}", failures)
    for key in ("installedGameMutation", "originalExecutableMutation", "screenshotCapture", "nativeInput", "debuggerAttachment", "godotWork"):
        require(summary[key] is False, f"private guard flag must be false: {key}", failures)
    require(summary["missionScriptRuntimeEvidenceRows"] == 0, "private MissionScript runtime rows mismatch", failures)
    require(no_bea_process_running(), "BEA process still running after direct Level100 smoke proof", failures)


def check_helpers(failures: list[str]) -> None:
    for path in (LIST_WINDOWS, CAPTURE_WINDOW):
        text = read_text(path)
        require("$runningOnWindows" in text, f"{path.relative_to(ROOT)} missing compatibility-safe variable", failures)
        require("$isWindows" not in text, f"{path.relative_to(ROOT)} still contains PowerShell automatic-variable collision", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(result == read_json(LORE_RESULT), "lore direct Level100 result mirror mismatch", failures)
    require(read_json(SCREENSHOT_RESULT)["nextStaticSlice"] == THIS_SLICE, "screenshot result does not point to direct Level100 lane", failures)
    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1", "schemaVersion mismatch", failures)
    require(result["status"] == "COMPLETE", "status mismatch", failures)
    require(result["directLevel100LaunchWindowSmokeStatus"] == "direct-level100-copied-profile-window-smoke-complete", "direct smoke status mismatch", failures)
    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function-quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(static["latestGhidraBackup"] == BACKUP, "latest Ghidra backup mismatch", failures)

    proof = result["directLevel100LaunchWindowSmokeProof"]
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
    require(proof["selectedRoute"] == "direct-level100-candidate", "selected route mismatch", failures)
    require(proof["launchArguments"] == ["-skipfmv", "-level", "100"], "launch arguments mismatch", failures)
    require(proof["directLevel100RouteStatus"] == "window-smoke-complete-no-missionscript-proof", "direct Level100 route status mismatch", failures)
    require(proof["windowHelperPowerShellCompatibilityFix"] == "runningOnWindows-local-variable", "helper fix token mismatch", failures)
    for key in (
        "freshPrintOnlyPreviewChecked",
        "launchArmed",
        "beLaunch",
        "launchCommandExecuted",
        "processStarted",
        "processAliveAfterDelay",
        "respondingAfterDelay",
        "mainWindowHandleObserved",
        "windowVisible",
        "windowNotMinimized",
        "boundedProcessLifetime",
    ):
        require(proof[key] is True, f"proof flag must be true: {key}", failures)
    require(proof["beProcessesBefore"] == 0, "BEA process precheck mismatch", failures)
    require(proof["observationDelaySeconds"] == 15, "observation delay mismatch", failures)
    require(proof["windowScanStatus"] == "ready", "window scan status mismatch", failures)
    require(proof["windowCandidateCount"] == 1, "window candidate count mismatch", failures)
    require(proof["exactPidWindowCount"] == 1, "exact PID window count mismatch", failures)
    require(proof["mainWindowTitleClass"] == "BEA", "window title class mismatch", failures)
    require(proof["screenshotCapture"] is False, "screenshot capture flag mismatch", failures)
    require(proof["captureFrameCount"] == 0, "capture frame count mismatch", failures)
    require(proof["cleanupMethod"] == "CloseMainWindow", "cleanup method mismatch", failures)
    require(proof["processCleanup"] == "PASS", "process cleanup mismatch", failures)
    require(proof["processAliveAfterCleanup"] is False, "process alive after cleanup mismatch", failures)
    require(proof["beProcessesAfterCleanup"] == 0, "BEA after cleanup mismatch", failures)
    require(proof["windowSmokeObservationRows"] == 1, "window smoke rows mismatch", failures)
    require(proof["missionScriptRuntimeEvidenceRows"] == 0, "MissionScript runtime rows mismatch", failures)
    for key in ("copiedTargetHashStableDuringSmoke", "copiedBackupHashStableDuringSmoke", "installedTargetHashStableDuringSmoke", "installedBackupHashStableDuringSmoke"):
        require(proof[key] is True, f"hash stability flag must be true: {key}", failures)
    for key in ("installedGameMutation", "originalExecutableMutation", "nativeInput", "debuggerAttachment", "godotWork"):
        require(proof[key] is False, f"mutation/runtime guard flag must be false: {key}", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore direct Level100 plan mirror mismatch", failures)
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore direct Level100 result mirror mismatch", failures)
    core_tokens = (
        THIS_SLICE,
        "complete direct Level100 copied-profile launch-window smoke proof, not MissionScript/runtime behavior proof",
        PLAN_LINK,
        RESULT_LINK,
        PREVIOUS_SLICE,
        "status=COMPLETE",
        "directLevel100LaunchWindowSmokeStatus=direct-level100-copied-profile-window-smoke-complete",
        f"profileId={PROFILE_ID}",
        "selectedRoute=direct-level100-candidate",
        "launchArguments=-skipfmv -level 100",
        "directLevel100RouteStatus=window-smoke-complete-no-missionscript-proof",
        "windowHelperPowerShellCompatibilityFix=runningOnWindows-local-variable",
        "launchHelper=tools/start_game_profile.ps1",
        "windowScanHelper=tools/list_game_windows.ps1",
        "launchArmed=true",
        "processStarted=true",
        "processAliveAfterDelay=true",
        "respondingAfterDelay=true",
        "observationDelaySeconds=15",
        "windowScanStatus=ready",
        "windowCandidateCount=1",
        "exactPidWindowCount=1",
        "mainWindowTitleClass=BEA",
        "windowVisible=true",
        "windowNotMinimized=true",
        "screenshotCapture=false",
        "captureFrameCount=0",
        "cleanupMethod=CloseMainWindow",
        "processCleanup=PASS",
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
        "direct-level100-copied-profile-window-smoke-complete",
        "selectedRoute=direct-level100-candidate",
        "launchArguments=-skipfmv -level 100",
        "windowHelperPowerShellCompatibilityFix=runningOnWindows-local-variable",
        "observationDelaySeconds=15",
        "windowCandidateCount=1",
        "exactPidWindowCount=1",
        "screenshotCapture=false",
        "captureFrameCount=0",
        "missionScriptRuntimeEvidenceRows=0",
        FOLLOW_UP_SLICE,
        SECOND_FOLLOW_UP_SLICE,
        THIRD_FOLLOW_UP_SLICE,
        FOURTH_FOLLOW_UP_SLICE,
        "selected timed-frame text-overlay progression correlation proof candidate",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing direct Level100 token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed direct Level100 slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed direct Level100 screenshot slice", failures)
    require(f"Completed {FOLLOW_UP_SLICE}" in backlog, "backlog missing completed direct Level100 visual frame triage slice", failures)
    require(f"Completed {SECOND_FOLLOW_UP_SLICE}" in backlog, "backlog missing completed direct Level100 text overlay correlation slice", failures)
    require(f"Completed {THIRD_FOLLOW_UP_SLICE}" in backlog, "backlog missing completed direct Level100 timed-frame set slice", failures)
    require(f"The selected active static-to-proof slice is {FOURTH_FOLLOW_UP_SLICE}" in backlog, "backlog missing active direct Level100 timed-frame text-overlay progression slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks direct Level100 smoke as active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_launch_window_smoke_probe.py --check",
        "missing package direct Level100 launch-window smoke test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_private_evidence(failures)
    check_helpers(failures)
    check_result(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("MissionScript Level100 direct launch-window smoke probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 direct launch-window smoke probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
