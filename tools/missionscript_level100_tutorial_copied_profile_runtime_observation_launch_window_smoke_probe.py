#!/usr/bin/env python3
"""Validate the MissionScript Level100 copied-profile launch-window smoke proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke-proof.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke.v1.json"
LAUNCH_COMMAND = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_launch_window_smoke_2026-06-08.md"
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
PRIVATE_PROOF_DIR = PRIVATE_PROFILE_ROOT / "launch-window-smoke.private"
PRIVATE_SUMMARY = PRIVATE_PROOF_DIR / "launch-window-smoke-summary.private.json"
PRIVATE_STDOUT = PRIVATE_PROOF_DIR / "start-game-profile.stdout.private.txt"
PRIVATE_PREVIEW = PRIVATE_PROOF_DIR / "start-game-profile-printonly.private.txt"

PATCHED_SHA = "e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918"
EXPECTED_CLEAN_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Window Smoke Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture Proof Plan"
DIRECT_LEVEL100_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan"
FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan"
VISUAL_FRAME_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Visual Frame Triage Proof Plan"
TEXT_OVERLAY_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Text Overlay Correlation Proof Plan"
TIMED_FRAME_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Capture Proof Plan"
TIMED_FRAME_TEXT_OVERLAY_PROGRESSION_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Text Overlay Progression Correlation Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke-proof.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke.v1.json"

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
    "<PRIVATE_PATH_REDACTED>\\",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "direct level100 route behavior proven",
    "runtime command effects proven",
    "runtime event outcomes proven",
    "live loose-msl loading proven",
    "packed-vs-loose script selection proven",
    "runtime level100 mission outcome proven",
    "runtime objective ui proven",
    "runtime message or audio output proven",
    "runtime hud flashing proven",
    "runtime spawnthing behavior proven",
    "runtime getthingref lookup behavior proven",
    "screenshot proof complete",
    "frame capture proof complete",
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


def check_private_evidence(failures: list[str]) -> None:
    require(PRIVATE_EXE.is_file(), "private copied BEA.exe missing", failures)
    require(PRIVATE_BACKUP.is_file(), "private clean backup missing", failures)
    require(PRIVATE_SUMMARY.is_file(), "private launch-window smoke summary missing", failures)
    require(PRIVATE_STDOUT.is_file(), "private launch helper stdout missing", failures)
    require(PRIVATE_PREVIEW.is_file(), "private launch helper print-only preview missing", failures)
    require(PRIVATE_EXE.stat().st_size == 2506752, "private copied BEA.exe byte size mismatch", failures)
    require(PRIVATE_BACKUP.stat().st_size == 2506752, "private clean backup byte size mismatch", failures)
    require(sha256(PRIVATE_EXE) == PATCHED_SHA, "private copied BEA.exe patched hash mismatch", failures)
    require(sha256(PRIVATE_BACKUP) == EXPECTED_CLEAN_SHA, "private backup clean hash mismatch", failures)

    summary = read_json(PRIVATE_SUMMARY)
    require(summary["schemaVersion"] == "missionscript-level100-launch-window-smoke.private.v1", "private summary schema mismatch", failures)
    require(summary["status"] == "COMPLETE", "private summary status mismatch", failures)
    require(summary["profileId"] == PROFILE_ID, "private profile mismatch", failures)
    require(Path(summary["profileRoot"]) == PRIVATE_PROFILE_ROOT, "private profile root mismatch", failures)
    require(Path(summary["targetExecutable"]) == PRIVATE_EXE, "private target path mismatch", failures)
    require(Path(summary["cleanBackup"]) == PRIVATE_BACKUP, "private backup path mismatch", failures)
    require(summary["targetHashBefore"] == PATCHED_SHA, "private target before hash mismatch", failures)
    require(summary["targetHashAfter"] == PATCHED_SHA, "private target after hash mismatch", failures)
    require(summary["backupHashBefore"] == EXPECTED_CLEAN_SHA, "private backup before hash mismatch", failures)
    require(summary["backupHashAfter"] == EXPECTED_CLEAN_SHA, "private backup after hash mismatch", failures)
    require(summary["targetBytes"] == 2506752, "private target bytes mismatch", failures)
    require(summary["backupBytes"] == 2506752, "private backup bytes mismatch", failures)
    require(summary["selectedRoute"] == "skip-fmv-copied-profile-launch", "private selected route mismatch", failures)
    require(summary["launchArguments"] == ["-skipfmv"], "private launch arguments mismatch", failures)
    require(summary["launchArm"]["launchArmed"] is True, "private launch arm mismatch", failures)
    require(summary["launchArm"]["acceptedRoute"] == "skip-fmv-copied-profile-launch", "private accepted route mismatch", failures)
    require(summary["beProcessesBefore"] == 0, "private beProcessesBefore mismatch", failures)
    require(summary["launchHelper"] == "tools/start_game_profile.ps1", "private launch helper mismatch", failures)
    require(summary["launchHelperSchema"] == "game-launch-process.v1", "private launch helper schema mismatch", failures)
    require(summary["launchCommandExecuted"] is True, "private launch command executed mismatch", failures)
    require(summary["processStarted"] is True, "private process started mismatch", failures)
    require(str(summary.get("processPath", "")).endswith("BEA.exe"), "private process path class mismatch", failures)
    require(summary["processAliveAfterDelay"] is True, "private process alive after delay mismatch", failures)
    require(summary["mainWindowHandleNonZero"] is True, "private window handle mismatch", failures)
    require(summary["mainWindowTitle"] == "BEA", "private window title mismatch", failures)
    require(summary["respondingAfterDelay"] is True, "private responding state mismatch", failures)
    require(summary["observationDelaySeconds"] == 8, "private observation delay mismatch", failures)
    require(summary["boundedProcessLifetime"] is True, "private bounded process lifetime mismatch", failures)
    require(summary["cleanupMethod"] == "CloseMainWindow", "private cleanup method mismatch", failures)
    require(summary["cleanupSucceeded"] is True, "private cleanup succeeded mismatch", failures)
    require(summary["processAliveAfterCleanup"] is False, "private process alive after cleanup mismatch", failures)
    require(summary["beProcessesAfterCleanup"] == 0, "private beProcessesAfterCleanup mismatch", failures)
    require(summary["installedTargetHashBefore"] == summary["installedTargetHashAfter"], "installed target hash changed", failures)
    require(summary["installedBackupHashBefore"] == summary["installedBackupHashAfter"], "installed backup hash changed", failures)
    require(summary["copiedTargetHashStableDuringSmoke"] is True, "copied target stability mismatch", failures)
    require(summary["copiedBackupHashStableDuringSmoke"] is True, "copied backup stability mismatch", failures)
    for key in ("installedGameMutation", "originalExecutableMutation", "screenshotCapture", "nativeInput", "debuggerAttachment", "godotWork"):
        require(summary[key] is False, f"private summary flag must be false: {key}", failures)
    require(no_bea_process_running(), "BEA process still running after smoke proof", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(result == read_json(LORE_RESULT), "lore launch-window smoke result mirror mismatch", failures)
    require(read_json(LAUNCH_COMMAND)["nextStaticSlice"] == THIS_SLICE, "launch-command result does not point to launch-window smoke lane", failures)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke.v1", "schemaVersion mismatch", failures)
    require(result["status"] == "COMPLETE", "status mismatch", failures)
    require(result["launchWindowSmokeStatus"] == "copied-profile-window-smoke-complete", "launchWindowSmokeStatus mismatch", failures)
    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function-quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(static["latestGhidraBackup"] == BACKUP, "latest Ghidra backup mismatch", failures)

    proof = result["launchWindowSmokeProof"]
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
    require(proof["directLevel100Route"] == "direct-level100-candidate", "direct Level100 route mismatch", failures)
    require(proof["directLevel100RouteStatus"] == "candidate-unproven-unarmed", "direct Level100 route status mismatch", failures)
    require(proof["launchHelper"] == "tools/start_game_profile.ps1", "launch helper mismatch", failures)
    require(proof["launchHelperSchema"] == "game-launch-process.v1", "launch helper schema mismatch", failures)
    require(proof["freshPrintOnlyPreviewChecked"] is True, "print-only preview check mismatch", failures)
    for key in ("launchArmed", "beLaunch", "launchCommandExecuted", "processStarted", "processAliveAfterDelay", "mainWindowHandleObserved", "respondingAfterDelay", "boundedProcessLifetime"):
        require(proof[key] is True, f"proof flag must be true: {key}", failures)
    require(proof["processPathClass"] == "copied-profile-BEA.exe", "process path class mismatch", failures)
    require(proof["beProcessesBefore"] == 0, "BEA process precheck mismatch", failures)
    require(proof["observationDelaySeconds"] == 8, "observation delay mismatch", failures)
    require(proof["mainWindowTitleClass"] == "BEA", "main window title class mismatch", failures)
    require(proof["cleanupMethod"] == "CloseMainWindow", "cleanup method mismatch", failures)
    require(proof["processCleanup"] == "PASS", "process cleanup mismatch", failures)
    require(proof["processAliveAfterCleanup"] is False, "process alive after cleanup mismatch", failures)
    require(proof["beProcessesAfterCleanup"] == 0, "BEA after cleanup mismatch", failures)
    require(proof["windowSmokeObservationRows"] == 1, "window smoke observation rows mismatch", failures)
    require(proof["missionScriptRuntimeEvidenceRows"] == 0, "MissionScript runtime rows mismatch", failures)
    for key in (
        "copiedTargetHashStableDuringSmoke",
        "copiedBackupHashStableDuringSmoke",
        "installedTargetHashStableDuringSmoke",
        "installedBackupHashStableDuringSmoke",
    ):
        require(proof[key] is True, f"hash stability flag must be true: {key}", failures)
    for key in ("installedGameMutation", "originalExecutableMutation"):
        require(proof[key] is False, f"mutation flag must be false: {key}", failures)

    guard = result["guardSummary"]
    for key in ("copiedExecutablePatch", "launchWindowSmokeProof", "beLaunch", "launchArmed", "launchCommandExecuted", "processStarted", "boundedProcessLifetime"):
        require(guard[key] is True, f"guard flag must be true: {key}", failures)
    require(guard["processCleanup"] == "PASS", "guard process cleanup mismatch", failures)
    for key in ("installedGameMutation", "originalExecutableMutation", "screenshotCapture", "nativeInput", "debuggerAttachment", "godotWork"):
        require(guard[key] is False, f"guard flag must be false: {key}", failures)
    require(guard["missionScriptRuntimeEvidenceRows"] == 0, "guard MissionScript runtime rows mismatch", failures)
    require(guard["privatePathLeakCount"] == 0, "private path leak count mismatch", failures)
    require(guard["rawArtifactLeakCount"] == 0, "raw artifact leak count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore launch-window smoke plan mirror mismatch", failures)
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore launch-window smoke result mirror mismatch", failures)

    core_tokens = (
        "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Window Smoke",
        "complete copied-profile launch-window smoke proof, not MissionScript/runtime behavior proof",
        PLAN_LINK,
        RESULT_LINK,
        PREVIOUS_SLICE,
        "status=COMPLETE",
        "launchWindowSmokeStatus=copied-profile-window-smoke-complete",
        f"profileId={PROFILE_ID}",
        "targetExecutableClass=copied-profile-BEA.exe",
        "workingDirectoryClass=copied-profile-root",
        "selectedRoute=skip-fmv-copied-profile-launch",
        "directLevel100Route=direct-level100-candidate",
        "directLevel100RouteStatus=candidate-unproven-unarmed",
        "launchHelper=tools/start_game_profile.ps1",
        "launchHelperSchema=game-launch-process.v1",
        "freshPrintOnlyPreviewChecked=true",
        "launchArmed=true",
        "beLaunch=true",
        "launchCommandExecuted=true",
        "processStarted=true",
        "processAliveAfterDelay=true",
        "mainWindowHandleObserved=true",
        "mainWindowTitleClass=BEA",
        "respondingAfterDelay=true",
        "observationDelaySeconds=8",
        "boundedProcessLifetime=true",
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
        "screenshotCapture=false",
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
        "copied-profile-window-smoke-complete",
        "selectedRoute=skip-fmv-copied-profile-launch",
        "launchArmed=true",
        "beLaunch=true",
        "processStarted=true",
        "mainWindowHandleObserved=true",
        "mainWindowTitleClass=BEA",
        "processCleanup=PASS",
        "missionScriptRuntimeEvidenceRows=0",
        "copied-profile-window-still-frame-captured",
        DIRECT_LEVEL100_SLICE,
        FOLLOW_UP_SLICE,
        VISUAL_FRAME_SLICE,
        TEXT_OVERLAY_SLICE,
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing launch-window smoke token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed launch-window smoke slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed screenshot capture slice", failures)
    require(f"Completed {DIRECT_LEVEL100_SLICE}" in backlog, "backlog missing completed direct Level100 launch smoke slice", failures)
    require(f"Completed {FOLLOW_UP_SLICE}" in backlog, "backlog missing completed direct Level100 screenshot slice", failures)
    require(f"Completed {VISUAL_FRAME_SLICE}" in backlog, "backlog missing completed direct Level100 visual frame triage slice", failures)
    require(f"Completed {TEXT_OVERLAY_SLICE}" in backlog, "backlog missing completed direct Level100 text overlay correlation slice", failures)
    require(f"Completed {TIMED_FRAME_SLICE}" in backlog, "backlog missing completed direct Level100 timed-frame set slice", failures)
    require(f"The selected active static-to-proof slice is {TIMED_FRAME_TEXT_OVERLAY_PROGRESSION_SLICE}" in backlog, "backlog missing active direct Level100 timed-frame text-overlay progression slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks launch-window smoke proof as selected active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_launch_window_smoke_probe.py --check",
        "missing package launch-window smoke test script",
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
        print("MissionScript Level100 launch-window smoke probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 launch-window smoke probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
