#!/usr/bin/env python3
"""Validate the MissionScript Level100 direct copied-profile visual-frame triage proof."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage-proof.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage.v1.json"
SCREENSHOT_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_visual_frame_triage_2026-06-09.md"
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
BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Visual Frame Triage Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Text Overlay Correlation Proof Plan"
FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Capture Proof Plan"
SECOND_FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Text Overlay Progression Correlation Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage-proof.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage.v1.json"

FORBIDDEN_PUBLIC_TOKENS = (
    "c:\\users",
    "c:/users",
    "%userprofile%",
    "program files",
    "steam",
    "steamapps",
    "subagents\\",
    "subagents/",
    "private_runtime_evidence",
    "game/",
    "media/",
    "processid",
    "hwndhex",
    "hwnd",
    "capturesourcehint",
    "outputpath",
    "executablepath",
    "commandpreview",
    "capturepath",
    "framepath",
    "capturehash",
    "framehash",
    "capturebytes",
    "framebytes",
    ".private.png",
    "attempt-",
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
    "visual correctness proven",
    "occlusion-free pixel correctness proven",
    "exact text identity proven",
    "ocr identity proven",
    "native input behavior proven",
    "debugger observation proven",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)

TRUE_VISUAL_FLAGS = (
    "beWindowFrameVisible",
    "inGameRenderedFrameVisible",
    "sceneNotBlackOrBlank",
    "terrainSkyLightingVisible",
    "cockpitHudVisible",
    "centralReticleVisible",
    "leftRadarHudVisible",
    "rightCircularHudVisible",
    "bottomTutorialTextPanelVisible",
    "tutorialTextGlyphsVisible",
)

GUARD_TRUE_VISUAL_FLAGS = (
    "beWindowFrameVisible",
    "inGameRenderedFrameVisible",
    "sceneNotBlackOrBlank",
    "bottomTutorialTextPanelVisible",
    "tutorialTextGlyphsVisible",
)

FALSE_GUARD_FLAGS = (
    "menuOnlyOrDesktopOnlyFrame",
    "crashDialogVisible",
    "blankFrameVisible",
    "visualCorrectnessProven",
    "visualCorrectnessClaim",
    "pixelCorrectnessClaim",
    "exactTextOcrPerformed",
    "visibleTextExcerptPublished",
    "newLaunch",
    "newScreenshotCapture",
    "privateProofAssetPublished",
    "privateCaptureLocatorIncluded",
    "privateArtifactHashIncluded",
    "privateArtifactBytesIncluded",
    "privateWindowIdentifiersIncluded",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
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


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    proof = result["visualFrameTriageProof"]
    guard = result["guardSummary"]
    screenshot = read_json(SCREENSHOT_RESULT)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage.v1", "public schema mismatch", failures)
    require(result["status"] == "COMPLETE", "public status mismatch", failures)
    require(result["directLevel100VisualFrameTriageStatus"] == "direct-level100-private-still-frame-visually-triaged", "public status token mismatch", failures)
    require(result["staticContext"]["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(result["staticContext"]["currentRiskFocused"] == "1179/1179 = 100.00%", "current risk mismatch", failures)
    require(result["staticContext"]["latestGhidraBackup"] == BACKUP, "backup token mismatch", failures)
    require(screenshot["status"] == "COMPLETE", "screenshot parent status mismatch", failures)
    require(screenshot["directLevel100ScreenshotCaptureStatus"] == "direct-level100-copied-profile-window-still-frame-captured", "screenshot parent status token mismatch", failures)

    require(proof["profileId"] == PROFILE_ID, "profile id mismatch", failures)
    require(proof["sourceCaptureProof"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json", "source capture proof mismatch", failures)
    require(proof["sourceCaptureStatus"] == "direct-level100-copied-profile-window-still-frame-captured", "source capture status mismatch", failures)
    require(proof["artifactRootClass"] == "repo-local-ignored-private-evidence-root", "artifact root class mismatch", failures)
    require(proof["captureArtifactClass"] == "private-still-frame-png", "capture artifact class mismatch", failures)
    require(proof["privateFrameArtifactClass"] == "private-still-frame-png", "private frame artifact class mismatch", failures)
    require(proof["privateFrameReviewedByClass"] == "codex-root-private-visual-triage", "private frame reviewer class mismatch", failures)
    require(proof["privatePathIncluded"] is False, "private path included mismatch", failures)
    require(proof["rawArtifactIncluded"] is False, "raw artifact included mismatch", failures)
    require(proof["captureArtifactPublished"] is False, "capture artifact published mismatch", failures)
    require(proof["selectedRoute"] == "direct-level100-candidate", "selected route mismatch", failures)
    require(proof["launchArguments"] == ["-skipfmv", "-level", "100"], "launch args mismatch", failures)
    require(proof["sourceCaptureFrameCount"] == 1, "source capture frame count mismatch", failures)
    require(proof["triagedFrameCount"] == 1, "triaged frame count mismatch", failures)
    require(proof["captureFrameCount"] == 1, "capture frame count mismatch", failures)
    require(proof["captureWidth"] == 656, "capture width mismatch", failures)
    require(proof["captureHeight"] == 539, "capture height mismatch", failures)
    require(proof["visualTriageMethod"] == "codex-root-private-still-frame-review", "triage method mismatch", failures)
    require(proof["visibleStateClass"] == "in-level-visual-candidate", "visible state class mismatch", failures)
    require(proof["visualFrameReadable"] is True, "visual frame readable mismatch", failures)
    require(proof["visualFrameBlank"] is False, "visual frame blank mismatch", failures)
    require(proof["visualFrameOcclusionClass"] == "unknown", "visual frame occlusion class mismatch", failures)
    require(proof["visibleSurfaceClassRows"] == ["be-window-frame", "in-game-rendered-frame", "terrain-sky-lighting", "cockpit-hud", "central-reticle", "left-radar-hud", "right-circular-hud", "bottom-tutorial-text-panel", "tutorial-text-glyphs"], "visible surface class rows mismatch", failures)
    require(proof["visualFrameTriageRows"] == 1, "visual frame triage rows mismatch", failures)
    for key in TRUE_VISUAL_FLAGS:
        require(proof[key] is True, f"visual flag must be true: {key}", failures)
    for key in FALSE_GUARD_FLAGS:
        require(proof[key] is False, f"guard flag must be false: {key}", failures)
    require(proof["missionScriptRuntimeEvidenceRows"] == 0, "MissionScript runtime rows mismatch", failures)

    require(guard["directLevel100ScreenshotCaptureProof"] is True, "guard screenshot proof mismatch", failures)
    require(guard["directLevel100VisualFrameTriageProof"] is True, "guard visual triage proof mismatch", failures)
    require(guard["sourceCaptureStatus"] == "direct-level100-copied-profile-window-still-frame-captured", "guard source capture mismatch", failures)
    require(guard["captureFrameCount"] == 1, "guard capture frame count mismatch", failures)
    require(guard["triagedFrameCount"] == 1, "guard triaged frame count mismatch", failures)
    require(guard["captureArtifactPublished"] is False, "guard capture published mismatch", failures)
    require(guard["visibleStateClass"] == "in-level-visual-candidate", "guard visible state class mismatch", failures)
    require(guard["visualFrameReadable"] is True, "guard visual frame readable mismatch", failures)
    require(guard["visualFrameBlank"] is False, "guard visual frame blank mismatch", failures)
    require(guard["visualFrameOcclusionClass"] == "unknown", "guard visual frame occlusion class mismatch", failures)
    for key in GUARD_TRUE_VISUAL_FLAGS:
        require(guard[key] is True, f"guard visual flag must be true: {key}", failures)
    for key in FALSE_GUARD_FLAGS:
        require(guard[key] is False, f"guard flag must be false: {key}", failures)
    require(guard["installedGameMutation"] is False, "guard installed mutation mismatch", failures)
    require(guard["originalExecutableMutation"] is False, "guard original mutation mismatch", failures)
    require(guard["missionScriptRuntimeEvidenceRows"] == 0, "guard MissionScript runtime rows mismatch", failures)
    require(guard["privatePathLeakCount"] == 0, "private path leak count mismatch", failures)
    require(guard["rawArtifactLeakCount"] == 0, "raw artifact leak count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    require(no_bea_process_running(), "BEA process still running after visual triage proof", failures)
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
        "directLevel100VisualFrameTriageStatus=direct-level100-private-still-frame-visually-triaged",
        "sourceCaptureStatus=direct-level100-copied-profile-window-still-frame-captured",
        "selectedRoute=direct-level100-candidate",
        "launchArguments=-skipfmv -level 100",
        "captureFrameCount=1",
        "captureWidth=656",
        "captureHeight=539",
        "visualTriageMethod=codex-root-private-still-frame-review",
        "sourceCaptureProof=missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json",
        "sourceCaptureFrameCount=1",
        "triagedFrameCount=1",
        "newLaunch=false",
        "newScreenshotCapture=false",
        "captureArtifactClass=private-still-frame-png",
        "privateFrameArtifactClass=private-still-frame-png",
        "privateFrameReviewedByClass=codex-root-private-visual-triage",
        "privateProofAssetPublished=false",
        "privateCaptureLocatorIncluded=false",
        "privateArtifactHashIncluded=false",
        "privateArtifactBytesIncluded=false",
        "privateWindowIdentifiersIncluded=false",
        "visibleStateClass=in-level-visual-candidate",
        "visualFrameReadable=true",
        "visualFrameBlank=false",
        "visualFrameOcclusionClass=unknown",
        "visualFrameTriageRows=1",
        "visibleTextExcerptPublished=false",
        "visualCorrectnessClaim=false",
        "pixelCorrectnessClaim=false",
        "captureArtifactPublished=false",
        "beWindowFrameVisible=true",
        "inGameRenderedFrameVisible=true",
        "sceneNotBlackOrBlank=true",
        "terrainSkyLightingVisible=true",
        "cockpitHudVisible=true",
        "centralReticleVisible=true",
        "leftRadarHudVisible=true",
        "rightCircularHudVisible=true",
        "bottomTutorialTextPanelVisible=true",
        "tutorialTextGlyphsVisible=true",
        "menuOnlyOrDesktopOnlyFrame=false",
        "crashDialogVisible=false",
        "blankFrameVisible=false",
        "visualCorrectnessProven=false",
        "exactTextOcrPerformed=false",
        "missionScriptRuntimeEvidenceRows=0",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
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
        PROFILE_ID,
        "direct-level100-private-still-frame-visually-triaged",
        "sourceCaptureStatus=direct-level100-copied-profile-window-still-frame-captured",
        "captureFrameCount=1",
        "captureWidth=656",
        "captureHeight=539",
        "visibleStateClass=in-level-visual-candidate",
        "triagedFrameCount=1",
        "beWindowFrameVisible=true",
        "inGameRenderedFrameVisible=true",
        "bottomTutorialTextPanelVisible=true",
        "tutorialTextGlyphsVisible=true",
        "captureArtifactPublished=false",
        "visualCorrectnessProven=false",
        "exactTextOcrPerformed=false",
        "missionScriptRuntimeEvidenceRows=0",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing visual triage token: {token}", failures)

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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed visual triage slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed text-overlay correlation slice", failures)
    require(f"Completed {FOLLOW_UP_SLICE}" in backlog, "backlog missing completed timed-frame set slice", failures)
    require(f"The selected active static-to-proof slice is {SECOND_FOLLOW_UP_SLICE}" in backlog, "backlog missing active timed-frame text-overlay progression slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks visual triage proof as selected active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_visual_frame_triage_probe.py --check",
        "missing package direct Level100 visual frame triage test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_result(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("MissionScript Level100 direct visual frame triage probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 direct visual frame triage probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
