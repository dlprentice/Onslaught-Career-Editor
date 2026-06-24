#!/usr/bin/env python3
"""Validate the MissionScript Level100 direct copied-profile screenshot capture proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture-proof.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json"
DIRECT_SMOKE_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_screenshot_capture_2026-06-09.md"
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
PRIVATE_PROOF_ROOT = PRIVATE_PROFILE_ROOT / "direct-level100-screenshot-capture.private"

PATCHED_SHA = "e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918"
EXPECTED_CLEAN_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Visual Frame Triage Proof Plan"
FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Text Overlay Correlation Proof Plan"
SECOND_FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Capture Proof Plan"
THIRD_FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Text Overlay Progression Correlation Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture-proof.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json"

FORBIDDEN_PUBLIC_TOKENS = (
    "c:\\users",
    "program files",
    "subagents\\",
    "processid",
    "hwnd",
    "capturesourcehint",
    "capturepath",
    "capturehash",
    ".private.png",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
    "<private_path_redacted>\\",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "level100 script source selection proven",
    "runtime command effects proven",
    "runtime event outcomes proven",
    "live loose-msl loading proven",
    "packed-vs-loose script selection proven",
    "runtime level100 mission outcome proven",
    "runtime objective ui proven",
    "runtime hud flashing proven",
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
        require(token not in lower, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
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
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def latest_private_summary() -> dict[str, Any]:
    summaries = sorted(
        PRIVATE_PROOF_ROOT.glob("attempt-*/direct-level100-screenshot-capture-summary.private.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not summaries:
        raise FileNotFoundError("missing private direct Level100 screenshot summary")
    return read_json(summaries[0])


def check_private_evidence(failures: list[str]) -> None:
    require(PRIVATE_EXE.is_file(), "missing copied-profile BEA.exe", failures)
    require(PRIVATE_BACKUP.is_file(), "missing copied-profile clean backup", failures)
    if PRIVATE_EXE.is_file():
        require(sha256(PRIVATE_EXE) == PATCHED_SHA, "copied-profile BEA.exe hash mismatch", failures)
    if PRIVATE_BACKUP.is_file():
        require(sha256(PRIVATE_BACKUP) == EXPECTED_CLEAN_SHA, "copied-profile clean backup hash mismatch", failures)

    summary = latest_private_summary()
    require(summary["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.private.v1", "private schema mismatch", failures)
    require(summary["status"] == "COMPLETE", "private status mismatch", failures)
    require(summary["profileId"] == PROFILE_ID, "private profile id mismatch", failures)
    require(summary["selectedRoute"] == "direct-level100-candidate", "private selected route mismatch", failures)
    require(summary["launchArguments"] == ["-skipfmv", "-level", "100"], "private launch args mismatch", failures)
    require(summary["processStarted"] is True, "private process started mismatch", failures)
    require(summary["processAliveAfterDelay"] is True, "private process alive mismatch", failures)
    require(summary["respondingAfterDelay"] is True, "private responding mismatch", failures)
    require(summary["observationDelaySeconds"] == 15, "private observation delay mismatch", failures)
    require(summary["windowScanStatus"] == "ready", "private window scan status mismatch", failures)
    require(summary["windowCandidateCount"] == 1, "private window candidate count mismatch", failures)
    require(summary["exactPidWindowCount"] == 1, "private exact process window count mismatch", failures)
    require(summary["exactPidWindowTitle"] == "BEA", "private window title mismatch", failures)
    require(summary["windowVisible"] is True, "private visible mismatch", failures)
    require(summary["windowNotMinimized"] is True, "private minimized mismatch", failures)
    require(summary["captureStatus"] == "captured", "private capture status mismatch", failures)
    require(summary["captureFrameCount"] == 1, "private capture frame count mismatch", failures)
    require(summary["captureWidth"] == 656, "private capture width mismatch", failures)
    require(summary["captureHeight"] == 539, "private capture height mismatch", failures)
    require(summary["captureOutputPathClass"] == "short-private-output-path", "private capture output path class mismatch", failures)
    require(summary["capturePathLength"] < 248, "private capture path length did not stay below GDI+ risk boundary", failures)
    capture_path = Path(summary["capturePath"])
    require(capture_path.is_file(), "private capture PNG missing", failures)
    if capture_path.is_file():
        require(capture_path.stat().st_size == summary["captureBytes"], "private capture byte count mismatch", failures)
        require(summary["captureBytes"] > 0, "private capture byte count is zero", failures)
        require(sha256(capture_path) == summary["captureHash"], "private capture hash mismatch", failures)
    require(len(summary["captureHash"]) == 64, "private capture hash shape mismatch", failures)
    require(summary["cleanupMethod"] == "CloseMainWindow", "private cleanup method mismatch", failures)
    require(summary["cleanupSucceeded"] is True, "private cleanup mismatch", failures)
    require(summary["beProcessesBefore"] == 0, "private BEA before count mismatch", failures)
    require(summary["beProcessesAfterCleanup"] == 0, "private BEA after count mismatch", failures)
    require(summary["hashesBefore"]["copiedTarget"] == PATCHED_SHA, "private copied target before hash mismatch", failures)
    require(summary["hashesAfter"]["copiedTarget"] == PATCHED_SHA, "private copied target after hash mismatch", failures)
    require(summary["hashesBefore"]["copiedBackup"] == EXPECTED_CLEAN_SHA, "private copied backup before hash mismatch", failures)
    require(summary["hashesAfter"]["copiedBackup"] == EXPECTED_CLEAN_SHA, "private copied backup after hash mismatch", failures)
    require(summary["hashesBefore"]["installedTarget"] == PATCHED_SHA, "private installed target before hash mismatch", failures)
    require(summary["hashesAfter"]["installedTarget"] == PATCHED_SHA, "private installed target after hash mismatch", failures)
    require(summary["hashesBefore"]["installedBackup"] == EXPECTED_CLEAN_SHA, "private installed backup before hash mismatch", failures)
    require(summary["hashesAfter"]["installedBackup"] == EXPECTED_CLEAN_SHA, "private installed backup after hash mismatch", failures)
    require(summary["copiedTargetHashStableDuringCapture"] is True, "private copied target stability mismatch", failures)
    require(summary["installedTargetHashStableDuringCapture"] is True, "private installed target stability mismatch", failures)
    require(summary["installedGameMutation"] is False, "private installed game mutation mismatch", failures)
    require(summary["originalExecutableMutation"] is False, "private original executable mutation mismatch", failures)
    require(summary["nativeInput"] is False, "private native input mismatch", failures)
    require(summary["debuggerAttachment"] is False, "private debugger mismatch", failures)
    require(summary["godotWork"] is False, "private Godot mismatch", failures)
    require(summary["missionScriptRuntimeEvidenceRows"] == 0, "private MissionScript runtime rows mismatch", failures)
    require(no_bea_process_running(), "BEA process still running after direct screenshot proof", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    proof = result["directLevel100ScreenshotCaptureProof"]
    guard = result["guardSummary"]
    direct_smoke = read_json(DIRECT_SMOKE_RESULT)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1", "public schema mismatch", failures)
    require(result["status"] == "COMPLETE", "public status mismatch", failures)
    require(result["directLevel100ScreenshotCaptureStatus"] == "direct-level100-copied-profile-window-still-frame-captured", "public status token mismatch", failures)
    require(result["staticContext"]["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(result["staticContext"]["currentRiskFocused"] == "1179/1179 = 100.00%", "current risk mismatch", failures)
    require(result["staticContext"]["latestGhidraBackup"] == BACKUP, "backup token mismatch", failures)
    require(direct_smoke["status"] == "COMPLETE", "direct smoke parent status mismatch", failures)

    require(proof["profileId"] == PROFILE_ID, "profile id mismatch", failures)
    require(proof["artifactRootClass"] == "repo-local-ignored-private-evidence-root", "artifact root class mismatch", failures)
    require(proof["targetExecutableClass"] == "copied-profile-BEA.exe", "target class mismatch", failures)
    require(proof["workingDirectoryClass"] == "copied-profile-root", "working directory class mismatch", failures)
    require(proof["privatePathIncluded"] is False, "private path included mismatch", failures)
    require(proof["rawArtifactIncluded"] is False, "raw artifact included mismatch", failures)
    require(proof["targetHashBefore"] == PATCHED_SHA, "target before hash mismatch", failures)
    require(proof["targetHashAfter"] == PATCHED_SHA, "target after hash mismatch", failures)
    require(proof["backupHashBefore"] == EXPECTED_CLEAN_SHA, "backup before hash mismatch", failures)
    require(proof["backupHashAfter"] == EXPECTED_CLEAN_SHA, "backup after hash mismatch", failures)
    require(proof["stablePatchRows"] == 4, "stable patch rows mismatch", failures)
    require(proof["skipAutoToggleArmed"] is False, "skip auto toggle mismatch", failures)
    require(proof["selectedRoute"] == "direct-level100-candidate", "selected route mismatch", failures)
    require(proof["launchArguments"] == ["-skipfmv", "-level", "100"], "launch args mismatch", failures)
    require(proof["directLevel100RouteStatus"] == "still-frame-captured-no-missionscript-proof", "route status mismatch", failures)
    require(proof["launchHelper"] == "tools/start_game_profile.ps1", "launch helper mismatch", failures)
    require(proof["windowScanHelper"] == "tools/list_game_windows.ps1", "window helper mismatch", failures)
    require(proof["captureHelper"] == "tools/capture_game_window.ps1", "capture helper mismatch", failures)
    require(proof["windowHelperPowerShellCompatibilityFix"] == "runningOnWindows-local-variable", "window helper compatibility token mismatch", failures)
    require(proof["launchArmed"] is True, "launch armed mismatch", failures)
    require(proof["beLaunch"] is True, "BEA launch mismatch", failures)
    require(proof["launchCommandExecuted"] is True, "launch command mismatch", failures)
    require(proof["processStarted"] is True, "process started mismatch", failures)
    require(proof["processAliveAfterDelay"] is True, "process alive mismatch", failures)
    require(proof["respondingAfterDelay"] is True, "responding mismatch", failures)
    require(proof["observationDelaySeconds"] == 15, "observation delay mismatch", failures)
    require(proof["windowScanStatus"] == "ready", "window scan mismatch", failures)
    require(proof["windowCandidateCount"] == 1, "window candidate mismatch", failures)
    require(proof["exactProcessWindowCount"] == 1, "exact window count mismatch", failures)
    require(proof["exactProcessWindowMatch"] is True, "exact window match mismatch", failures)
    require(proof["mainWindowTitleClass"] == "BEA", "window title class mismatch", failures)
    require(proof["windowVisible"] is True, "window visible mismatch", failures)
    require(proof["windowNotMinimized"] is True, "window minimized mismatch", failures)
    require(proof["captureFrameCount"] == 1, "capture frame count mismatch", failures)
    require(proof["captureStatus"] == "captured", "capture status mismatch", failures)
    require(proof["captureWidth"] == 656, "capture width mismatch", failures)
    require(proof["captureHeight"] == 539, "capture height mismatch", failures)
    require(proof["captureArtifactClass"] == "private-still-frame-png", "capture artifact class mismatch", failures)
    require(proof["captureArtifactBytesRecordedPrivately"] is True, "capture private byte flag mismatch", failures)
    require(proof["captureArtifactHashRecordedPrivately"] is True, "capture private hash flag mismatch", failures)
    require(proof["captureArtifactPublished"] is False, "capture published mismatch", failures)
    require(proof["captureOutputPathClass"] == "short-private-output-path", "capture output path class mismatch", failures)
    require(proof["pathLengthMitigation"] == "short-private-output-path-used-after-gdi-plus-long-path-save-failure", "path mitigation mismatch", failures)
    require(proof["processCleanup"] == "PASS", "cleanup mismatch", failures)
    require(proof["beProcessesAfterCleanup"] == 0, "BEA after cleanup mismatch", failures)
    require(proof["installedGameMutation"] is False, "installed mutation mismatch", failures)
    require(proof["originalExecutableMutation"] is False, "original mutation mismatch", failures)
    require(proof["nativeInput"] is False, "native input mismatch", failures)
    require(proof["debuggerAttachment"] is False, "debugger mismatch", failures)
    require(proof["godotWork"] is False, "Godot mismatch", failures)
    require(proof["windowSmokeObservationRows"] == 1, "window smoke rows mismatch", failures)
    require(proof["screenshotCaptureEvidenceRows"] == 1, "screenshot rows mismatch", failures)
    require(proof["missionScriptRuntimeEvidenceRows"] == 0, "MissionScript runtime rows mismatch", failures)

    require(guard["directLevel100ScreenshotCaptureProof"] is True, "guard screenshot proof mismatch", failures)
    require(guard["captureFrameCount"] == 1, "guard capture frame count mismatch", failures)
    require(guard["captureArtifactPublished"] is False, "guard capture published mismatch", failures)
    require(guard["privatePathLeakCount"] == 0, "private path leak count mismatch", failures)
    require(guard["rawArtifactLeakCount"] == 0, "raw artifact leak count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)

    public_text = read_text(RESULT)
    private = latest_private_summary()
    require(private["captureHash"] not in public_text, "public result leaks private capture hash", failures)
    require(str(private["captureBytes"]) not in public_text, "public result leaks private capture byte count", failures)
    require(Path(private["capturePath"]).name not in public_text, "public result leaks private capture file name", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        PLAN_LINK,
        RESULT_LINK,
        PROFILE_ID,
        "directLevel100ScreenshotCaptureStatus=direct-level100-copied-profile-window-still-frame-captured",
        "selectedRoute=direct-level100-candidate",
        "launchArguments=-skipfmv -level 100",
        "directLevel100RouteStatus=still-frame-captured-no-missionscript-proof",
        "windowScanStatus=ready",
        "windowCandidateCount=1",
        "exactProcessWindowCount=1",
        "captureFrameCount=1",
        "captureStatus=captured",
        "captureWidth=656",
        "captureHeight=539",
        "captureArtifactClass=private-still-frame-png",
        "captureArtifactBytesRecordedPrivately=true",
        "captureArtifactHashRecordedPrivately=true",
        "captureArtifactPublished=false",
        "captureOutputPathClass=short-private-output-path",
        "pathLengthMitigation=short-private-output-path-used-after-gdi-plus-long-path-save-failure",
        "processCleanup=PASS",
        "installedGameMutation=false",
        "originalExecutableMutation=false",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "missionScriptRuntimeEvidenceRows=0",
        "privatePathLeakCount=0",
        "rawArtifactLeakCount=0",
        "publicLeakCheck=PASS",
        "0x00539dc0",
        "0x00539ca0",
        "CDXMemBuffer__InitFromFile",
        BACKUP,
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
        PREVIOUS_SLICE,
        NEXT_SLICE,
        FOLLOW_UP_SLICE,
        SECOND_FOLLOW_UP_SLICE,
        PROFILE_ID,
        "direct-level100-copied-profile-window-still-frame-captured",
        "selectedRoute=direct-level100-candidate",
        "launchArguments=-skipfmv -level 100",
        "directLevel100RouteStatus=still-frame-captured-no-missionscript-proof",
        "captureFrameCount=1",
        "captureStatus=captured",
        "captureWidth=656",
        "captureHeight=539",
        "captureArtifactPublished=false",
        "missionScriptRuntimeEvidenceRows=0",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing direct screenshot token: {token}", failures)

    for source, mirror in (
        (PLAN, LORE_PLAN),
        (RESULT, LORE_RESULT),
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed direct screenshot slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed visual frame triage slice", failures)
    require(f"Completed {FOLLOW_UP_SLICE}" in backlog, "backlog missing completed text overlay correlation slice", failures)
    require(f"Completed {SECOND_FOLLOW_UP_SLICE}" in backlog, "backlog missing completed timed-frame set slice", failures)
    require(f"The selected active static-to-proof slice is {THIRD_FOLLOW_UP_SLICE}" in backlog, "backlog missing active timed-frame text-overlay progression slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks direct screenshot proof as selected active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_screenshot_capture_probe.py --check",
        "missing package direct Level100 screenshot capture test script",
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
        print("MissionScript Level100 direct screenshot capture probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 direct screenshot capture probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
