#!/usr/bin/env python3
"""Validate the MissionScript Level100 direct timed frame-set capture proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture-proof.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture.v1.json"
TEXT_OVERLAY_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation.v1.json"
VISUAL_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage.v1.json"
SCREENSHOT_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json"
SMOKE_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_timed_frame_set_capture_2026-06-09.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

PRIVATE_PROFILE_ROOT = ROOT / "subagents" / "static-to-proof" / "level100-copied-profile-materialization" / "level100-clean-materialized-20260608-214752"
PRIVATE_PROOF_ROOT = PRIVATE_PROFILE_ROOT / "direct-level100-timed-frame-set.private"

THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Capture Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Text Overlay Correlation Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Text Overlay Progression Correlation Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture-proof.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture.v1.json"
PROFILE_CLASS = "level100-clean-materialized-copied-profile"

FORBIDDEN_PUBLIC_TOKENS = (
    "c:\\users",
    "c:/users",
    "g:\\",
    "program files",
    "steamapps",
    "subagents\\",
    "subagents/",
    "private_runtime_evidence",
    "hwnd",
    "capturesourcehint",
    "capture source hint",
    "outputpath",
    "executablepath",
    "commandpreview",
    "capturepath",
    "framepath",
    "capturehash",
    "framehash",
    "framesha256",
    "framebytelength",
    ".private.png",
    "frame-05s",
    "frame-10s",
    "frame-15s",
    "frame-25s",
    "20260609-",
    "level100-clean-materialized-20260608-214752",
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
    "exact visible text identity proven",
    "ocr identity proven",
    "runtime message display behavior proven",
    "timing correctness proven",
    "visual correctness proven",
    "native input behavior proven",
    "debugger observation proven",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)

FALSE_GUARDS = (
    "profileIdPublished",
    "executableHashValuePublished",
    "privatePathIncluded",
    "rawArtifactIncluded",
    "timingCorrectnessClaim",
    "frameSetArtifactPublished",
    "privateFrameFileNamesIncluded",
    "privateCaptureLocatorIncluded",
    "privateArtifactHashIncluded",
    "privateArtifactBytesIncluded",
    "privateWindowIdentifiersIncluded",
    "rawDialogueIncluded",
    "rawDialoguePublished",
    "visibleTextExcerptPublished",
    "exactTextOcrPerformed",
    "exactVisibleTokenIdentityClaim",
    "exactVisibleTokenIdentityProven",
    "runtimeMessageDisplayClaim",
    "runtimeMessageDisplayProven",
    "sourceSelectionObserved",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "installedGameMutation",
    "originalExecutableMutation",
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


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in lower, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)
    require(re.search(r"\b[a-fA-F0-9]{64}\b", text) is None, f"{path.relative_to(ROOT)} leaks a raw SHA-256-like value", failures)
    require(re.search(r"\b[A-Za-z]:[\\/]", text) is None, f"{path.relative_to(ROOT)} leaks a machine-local absolute path", failures)


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
        PRIVATE_PROOF_ROOT.glob("*/timed-frame-set-summary.private.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not summaries:
        raise FileNotFoundError("missing private timed-frame-set summary")
    return read_json(summaries[0])


def check_private_evidence(failures: list[str]) -> None:
    summary = latest_private_summary()
    require(summary["schemaVersion"] == "direct-level100-timed-frame-set-private-summary.v1", "private summary schema mismatch", failures)
    require(summary["status"] == "PASS", "private summary status mismatch", failures)
    require(summary["profileId"] == "level100-clean-materialized-20260608-214752", "private profile id mismatch", failures)
    require(summary["selectedRoute"] == "direct-level100-candidate", "private selected route mismatch", failures)
    require(summary["launchArguments"] == ["-skipfmv", "-level", "100"], "private launch args mismatch", failures)
    require(summary["frameScheduleSeconds"] == [5, 10, 15, 25], "private frame schedule mismatch", failures)
    require(summary["frameCount"] == 4, "private frame count mismatch", failures)
    require(summary["captureStatuses"] == ["captured", "captured", "captured", "captured"], "private capture statuses mismatch", failures)
    require(summary["captureWidths"] == [656, 656, 656, 656], "private capture widths mismatch", failures)
    require(summary["captureHeights"] == [539, 539, 539, 539], "private capture heights mismatch", failures)
    require(all(value > 0 for value in summary["frameByteLengths"]), "private frame byte lengths not positive", failures)
    require(summary["copiedTargetHashStableDuringCapture"] is True, "private copied target hash stability mismatch", failures)
    require(summary["copiedBackupHashStableDuringCapture"] is True, "private copied backup hash stability mismatch", failures)
    require(summary["installedTargetHashStableDuringCapture"] is True, "private installed target hash stability mismatch", failures)
    require(summary["installedBackupHashStableDuringCapture"] is True, "private installed backup hash stability mismatch", failures)
    require(summary["processCleanup"] == "PASS", "private process cleanup mismatch", failures)
    require(summary["beProcessesAfterCleanup"] == 0, "private BEA process cleanup count mismatch", failures)

    private_rows = summary["privateFrameRows"]
    scan_rows = summary["privateScanRows"]
    require(len(private_rows) == 4, "private frame rows mismatch", failures)
    require(len(scan_rows) == 4, "private scan rows mismatch", failures)
    for row in private_rows:
        frame_path = Path(row["privateFramePath"])
        require(frame_path.is_file(), f"private frame missing: {frame_path.name}", failures)
        require(row["captureStatus"] == "captured", f"private frame capture status mismatch: {row['second']}", failures)
        require(row["frameWidth"] == 656, f"private frame width mismatch: {row['second']}", failures)
        require(row["frameHeight"] == 539, f"private frame height mismatch: {row['second']}", failures)
        if frame_path.is_file():
            require(frame_path.stat().st_size == row["frameByteLength"], f"private frame byte length mismatch: {row['second']}", failures)
    for row in scan_rows:
        require(row["scanStatus"] == "ready", f"private scan status mismatch: {row['second']}", failures)
        require(row["windowCandidateCount"] == 1, f"private window candidate mismatch: {row['second']}", failures)
        require(row["exactProcessWindowCount"] == 1, f"private exact window count mismatch: {row['second']}", failures)
        require(row["mainWindowTitle"] == "BEA", f"private window title mismatch: {row['second']}", failures)
        require(row["visible"] is True, f"private window visibility mismatch: {row['second']}", failures)
        require(row["minimized"] is False, f"private window minimized mismatch: {row['second']}", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    proof = result["timedFrameSetCaptureProof"]
    guard = result["guardSummary"]
    text_overlay = read_json(TEXT_OVERLAY_RESULT)
    visual = read_json(VISUAL_RESULT)
    screenshot = read_json(SCREENSHOT_RESULT)
    smoke = read_json(SMOKE_RESULT)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture.v1", "schema version mismatch", failures)
    require(result["status"] == "COMPLETE", "status mismatch", failures)
    require(result["directLevel100TimedFrameSetCaptureStatus"] == "direct-level100-copied-profile-timed-private-frame-set-captured", "status token mismatch", failures)
    require(result["staticContext"]["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(result["staticContext"]["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(result["staticContext"]["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(result["staticContext"]["currentRiskFocused"] == "1179/1179 = 100.00%", "current risk mismatch", failures)
    require(result["staticContext"]["staticAccountingSource"] == "static-reaudit-measurement-register.md", "static accounting source mismatch", failures)
    require(result["staticContext"]["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)
    require(result["staticContext"]["legacyStaticCounterRejected"] == "6113/6113", "legacy static counter rejection mismatch", failures)

    require(text_overlay["status"] == "COMPLETE", "text-overlay parent status mismatch", failures)
    require(text_overlay["directLevel100TextOverlayCorrelationStatus"] == "direct-level100-text-overlay-correlated-to-static-level100-token-surface", "text-overlay parent token mismatch", failures)
    require(visual["status"] == "COMPLETE", "visual parent status mismatch", failures)
    require(screenshot["status"] == "COMPLETE", "screenshot parent status mismatch", failures)
    require(smoke["status"] == "COMPLETE", "smoke parent status mismatch", failures)

    require(proof["profileIdClass"] == PROFILE_CLASS, "profile class mismatch", failures)
    require(proof["artifactRootClass"] == "repo-local-ignored-private-evidence-root", "artifact root class mismatch", failures)
    require(proof["targetExecutableClass"] == "copied-profile-BEA.exe", "target executable class mismatch", failures)
    require(proof["workingDirectoryClass"] == "copied-profile-root", "working directory class mismatch", failures)
    require(proof["frameSetCaptureMethod"] == "codex-root-bounded-private-window-capture", "capture method mismatch", failures)
    require(proof["selectedRoute"] == "direct-level100-candidate", "selected route mismatch", failures)
    require(proof["launchArguments"] == ["-skipfmv", "-level", "100"], "launch args mismatch", failures)
    require(proof["requestedFrameCount"] == 4, "requested frame count mismatch", failures)
    require(proof["capturedFrameCount"] == 4, "captured frame count mismatch", failures)
    require(proof["requestedFrameOffsetsSeconds"] == [5, 10, 15, 25], "frame offset schedule mismatch", failures)
    require(proof["captureDurationSeconds"] == 25, "capture duration mismatch", failures)
    require(proof["captureStatusesClass"] == "all-captured", "capture status class mismatch", failures)
    require(proof["captureWidth"] == 656, "capture width mismatch", failures)
    require(proof["captureHeight"] == 539, "capture height mismatch", failures)
    require(proof["frameDimensionClass"] == "stable-656x539", "frame dimension class mismatch", failures)
    require(proof["windowScanStatus"] == "ready", "window scan status mismatch", failures)
    require(proof["windowScanRows"] == 4, "window scan row count mismatch", failures)
    require(proof["windowCandidateCountPerScan"] == [1, 1, 1, 1], "window candidate counts mismatch", failures)
    require(proof["exactProcessWindowCountPerScan"] == [1, 1, 1, 1], "exact process window counts mismatch", failures)
    require(proof["sameProcessWindowAcrossFrames"] is True, "same process/window guard mismatch", failures)
    require(proof["windowTitleClass"] == "BEA", "window title class mismatch", failures)
    require(proof["windowVisibleAllFrames"] is True, "window visible guard mismatch", failures)
    require(proof["windowNotMinimizedAllFrames"] is True, "window minimized guard mismatch", failures)
    require(proof["allFrameArtifactsPrivate"] is True, "private frame artifact guard mismatch", failures)
    require(proof["visibleProgressionClassOnly"] is True, "visible progression class guard mismatch", failures)
    require(proof["visualFrameSetTriageRows"] == 4, "visual frame-set row count mismatch", failures)
    require(proof["visibleProgressionRows"] == 4, "visible progression row count mismatch", failures)
    require(proof["nonblankFrameRows"] == 4, "nonblank row count mismatch", failures)
    require(proof["inGameRenderedFrameRows"] == 4, "in-game rendered row count mismatch", failures)
    require(proof["exteriorVehicleWorldFrameRows"] == 1, "exterior vehicle/world row count mismatch", failures)
    require(proof["cockpitHudFrameRows"] == 3, "cockpit HUD row count mismatch", failures)
    require(proof["reticleVisibleFrameRows"] == 3, "reticle row count mismatch", failures)
    require(proof["radarHudVisibleFrameRows"] == 3, "radar HUD row count mismatch", failures)
    require(proof["bottomTutorialTextPanelVisibleFrameRows"] == 3, "tutorial panel row count mismatch", failures)
    require(proof["tutorialTextGlyphsVisibleFrameRows"] == 3, "tutorial glyph row count mismatch", failures)
    require(proof["speakerPortraitVisibleFrameRows"] == 3, "speaker portrait row count mismatch", failures)
    require(proof["textOverlayChangedAcrossFrameSetClass"] is True, "text overlay change class mismatch", failures)
    require(proof["missionScriptRuntimeEvidenceRows"] == 0, "MissionScript runtime row count mismatch", failures)
    require(proof["processCleanup"] == "PASS", "process cleanup mismatch", failures)
    require(proof["beProcessesAfterCleanup"] == 0, "BEA process cleanup count mismatch", failures)
    for key in FALSE_GUARDS:
        require(proof[key] is False, f"proof guard must be false: {key}", failures)
    for key in (
        "copiedTargetHashStableDuringCapture",
        "copiedBackupHashStableDuringCapture",
        "installedTargetHashStableDuringCapture",
        "installedBackupHashStableDuringCapture",
        "boundedProcessLifetime",
        "monotonicCaptureTimestamps",
    ):
        require(proof[key] is True, f"proof guard must be true: {key}", failures)

    require(guard["directLevel100TextOverlayCorrelationProof"] is True, "guard text-overlay parent mismatch", failures)
    require(guard["directLevel100VisualFrameTriageProof"] is True, "guard visual parent mismatch", failures)
    require(guard["directLevel100ScreenshotCaptureProof"] is True, "guard screenshot parent mismatch", failures)
    require(guard["directLevel100LaunchWindowSmokeProof"] is True, "guard smoke parent mismatch", failures)
    require(guard["publicLeakCheckMode"] == "regex-and-field-scan", "public leak check mode mismatch", failures)
    require(guard["forbiddenPublicRegexesChecked"] is True, "forbidden regex guard mismatch", failures)
    require(guard["requestedFrameCount"] == 4, "guard requested frame count mismatch", failures)
    require(guard["capturedFrameCount"] == 4, "guard captured frame count mismatch", failures)
    require(guard["publicAbsolutePathLeakCount"] == 0, "public absolute path leak count mismatch", failures)
    require(guard["publicSha256ValueLeakCount"] == 0, "public sha leak count mismatch", failures)
    require(guard["publicWindowIdentifierLeakCount"] == 0, "public window id leak count mismatch", failures)
    require(guard["publicProcessIdentifierLeakCount"] == 0, "public process id leak count mismatch", failures)
    require(guard["privatePathLeakCount"] == 0, "private path leak count mismatch", failures)
    require(guard["rawArtifactLeakCount"] == 0, "raw artifact leak count mismatch", failures)
    require(guard["rawDialogueLeakCount"] == 0, "raw dialogue leak count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    for key in FALSE_GUARDS:
        if key in guard:
            require(guard[key] is False, f"guard must be false: {key}", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    require(no_bea_process_running(), "BEA process still running after timed frame-set proof", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        PLAN_LINK,
        RESULT_LINK,
        "directLevel100TimedFrameSetCaptureStatus=direct-level100-copied-profile-timed-private-frame-set-captured",
        "profileIdClass=level100-clean-materialized-copied-profile",
        "profileIdPublished=false",
        "selectedRoute=direct-level100-candidate",
        "launchArguments=-skipfmv -level 100",
        "requestedFrameCount=4",
        "capturedFrameCount=4",
        "frameScheduleClass=bounded-four-frame-schedule",
        "requestedFrameOffsetsSeconds=5/10/15/25",
        "captureDurationSeconds=25",
        "monotonicCaptureTimestamps=true",
        "timingCorrectnessClaim=false",
        "captureStatusRows=4",
        "captureStatusesClass=all-captured",
        "captureWidth=656",
        "captureHeight=539",
        "frameDimensionClass=stable-656x539",
        "windowScanStatus=ready",
        "windowScanRows=4",
        "sameProcessWindowAcrossFrames=true",
        "windowTitleClass=BEA",
        "windowVisibleAllFrames=true",
        "windowNotMinimizedAllFrames=true",
        "allFrameArtifactsPrivate=true",
        "frameArtifactClass=private-still-frame-png",
        "frameSetArtifactPublished=false",
        "privateFrameFileNamesIncluded=false",
        "privateCaptureLocatorIncluded=false",
        "privateArtifactHashIncluded=false",
        "privateArtifactBytesIncluded=false",
        "privateWindowIdentifiersIncluded=false",
        "visibleProgressionClassOnly=true",
        "visualFrameSetTriageRows=4",
        "visibleProgressionRows=4",
        "nonblankFrameRows=4",
        "inGameRenderedFrameRows=4",
        "exteriorVehicleWorldFrameRows=1",
        "cockpitHudFrameRows=3",
        "reticleVisibleFrameRows=3",
        "radarHudVisibleFrameRows=3",
        "bottomTutorialTextPanelVisibleFrameRows=3",
        "tutorialTextGlyphsVisibleFrameRows=3",
        "speakerPortraitVisibleFrameRows=3",
        "textOverlayChangedAcrossFrameSetClass=true",
        "rawDialogueIncluded=false",
        "rawDialoguePublished=false",
        "visibleTextExcerptPublished=false",
        "exactTextOcrPerformed=false",
        "exactVisibleTokenIdentityClaim=false",
        "exactVisibleTokenIdentityProven=false",
        "runtimeMessageDisplayClaim=false",
        "runtimeMessageDisplayProven=false",
        "sourceSelectionObserved=false",
        "missionScriptRuntimeEvidenceRows=0",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "processCleanup=PASS",
        "beProcessesAfterCleanup=0",
        "copiedTargetHashStableDuringCapture=true",
        "copiedBackupHashStableDuringCapture=true",
        "installedTargetHashStableDuringCapture=true",
        "installedBackupHashStableDuringCapture=true",
        "installedGameMutation=false",
        "originalExecutableMutation=false",
        "publicLeakCheckMode=regex-and-field-scan",
        "forbiddenPublicRegexesChecked=true",
        "publicMachinePathIncluded=false",
        "publicAbsolutePathLeakCount=0",
        "publicSha256ValueLeakCount=0",
        "publicWindowIdentifierLeakCount=0",
        "publicProcessIdentifierLeakCount=0",
        "privatePathLeakCount=0",
        "rawArtifactLeakCount=0",
        "rawDialogueLeakCount=0",
        "publicLeakCheck=PASS",
        "staticAccountingSource=static-reaudit-measurement-register.md",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "legacyStaticCounterRejected=6113/6113",
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
        "direct-level100-copied-profile-timed-private-frame-set-captured",
        "profileIdClass=level100-clean-materialized-copied-profile",
        "profileIdPublished=false",
        "requestedFrameCount=4",
        "capturedFrameCount=4",
        "frameScheduleClass=bounded-four-frame-schedule",
        "captureDurationSeconds=25",
        "captureStatusesClass=all-captured",
        "frameDimensionClass=stable-656x539",
        "sameProcessWindowAcrossFrames=true",
        "allFrameArtifactsPrivate=true",
        "visibleProgressionClassOnly=true",
        "visualFrameSetTriageRows=4",
        "nonblankFrameRows=4",
        "cockpitHudFrameRows=3",
        "bottomTutorialTextPanelVisibleFrameRows=3",
        "textOverlayChangedAcrossFrameSetClass=true",
        "exactTextOcrPerformed=false",
        "runtimeMessageDisplayClaim=false",
        "sourceSelectionObserved=false",
        "missionScriptRuntimeEvidenceRows=0",
        "publicSha256ValueLeakCount=0",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing timed-frame token: {token}", failures)

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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed timed-frame set slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed text-overlay progression slice", failures)
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Boundary Proof Plan" in backlog,
        "backlog missing active runtime message display boundary slice",
        failures,
    )
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks timed-frame set active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks text-overlay progression active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_timed_frame_set_capture_probe.py --check",
        "missing package direct Level100 timed frame-set test script",
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
        print("MissionScript Level100 direct timed frame-set capture probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 direct timed frame-set capture probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
