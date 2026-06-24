#!/usr/bin/env python3
"""Validate the MissionScript Level100 direct text-overlay correlation proof."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation-proof.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation.v1.json"
VISUAL_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage.v1.json"
SCREENSHOT_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json"
TEXT_SPEAKER_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution.v1.json"
WALKTHROUGH_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_text_overlay_correlation_2026-06-09.md"
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
BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Text Overlay Correlation Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Visual Frame Triage Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Capture Proof Plan"
FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Text Overlay Progression Correlation Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation-proof.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation.v1.json"

FORBIDDEN_PUBLIC_TOKENS = (
    "c:\\users",
    "c:/users",
    "%userprofile%",
    "program files",
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
    "exact visible text identity proven",
    "ocr identity proven",
    "runtime missionscript execution proven",
    "level100 script source selection proven",
    "runtime command effects proven",
    "runtime message display behavior proven",
    "runtime localized text selection proven",
    "runtime speaker portrait behavior proven",
    "runtime audio behavior proven",
    "runtime objective ui proven",
    "runtime hud timing proven",
    "visual correctness proven",
    "occlusion-free pixel correctness proven",
    "native input behavior proven",
    "debugger observation proven",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)

FALSE_GUARD_FLAGS = (
    "rawDialogueIncluded",
    "rawDialoguePublished",
    "visibleTextExcerptPublished",
    "exactTextOcrPerformed",
    "exactVisibleTokenIdentityClaim",
    "exactVisibleTokenIdentityProven",
    "runtimeMessageDisplayClaim",
    "runtimeMessageDisplayProven",
    "privateProofAssetPublished",
    "privateCaptureLocatorIncluded",
    "privateArtifactHashIncluded",
    "privateArtifactBytesIncluded",
    "privateWindowIdentifiersIncluded",
    "newLaunch",
    "newScreenshotCapture",
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
    proof = result["textOverlayCorrelationProof"]
    guard = result["guardSummary"]
    visual = read_json(VISUAL_RESULT)
    screenshot = read_json(SCREENSHOT_RESULT)
    text_speaker = read_json(TEXT_SPEAKER_RESULT)
    walkthrough = read_json(WALKTHROUGH_RESULT)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation.v1", "schema version mismatch", failures)
    require(result["status"] == "COMPLETE", "status mismatch", failures)
    require(result["directLevel100TextOverlayCorrelationStatus"] == "direct-level100-text-overlay-correlated-to-static-level100-token-surface", "status token mismatch", failures)
    require(result["staticContext"]["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(result["staticContext"]["currentRiskFocused"] == "1179/1179 = 100.00%", "current risk mismatch", failures)
    require(result["staticContext"]["latestGhidraBackup"] == BACKUP, "backup token mismatch", failures)

    require(visual["status"] == "COMPLETE", "visual parent status mismatch", failures)
    require(visual["directLevel100VisualFrameTriageStatus"] == "direct-level100-private-still-frame-visually-triaged", "visual parent status token mismatch", failures)
    require(visual["visualFrameTriageProof"]["bottomTutorialTextPanelVisible"] is True, "visual parent missing text panel", failures)
    require(visual["visualFrameTriageProof"]["tutorialTextGlyphsVisible"] is True, "visual parent missing text glyphs", failures)
    require(screenshot["status"] == "COMPLETE", "screenshot parent status mismatch", failures)
    require(screenshot["directLevel100ScreenshotCaptureStatus"] == "direct-level100-copied-profile-window-still-frame-captured", "screenshot parent status token mismatch", failures)
    require(text_speaker["status"] == "PASS", "text/speaker parent status mismatch", failures)
    require(text_speaker["resolution"]["relevantStaticTokenCount"] == 68, "text/speaker token denominator mismatch", failures)
    require(text_speaker["resolution"]["relevantStaticTokensWithSharedStfOrSharedEnglish"] == 68, "text/speaker resolved count mismatch", failures)
    require(text_speaker["resolution"]["missingReferenceTokens"] == [], "text/speaker missing tokens", failures)
    require(walkthrough["status"] == "PASS", "walkthrough parent status mismatch", failures)

    require(proof["profileId"] == PROFILE_ID, "profile id mismatch", failures)
    require(proof["sourceVisualFrameTriageProof"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage.v1.json", "visual source proof mismatch", failures)
    require(proof["sourceVisualFrameTriageStatus"] == "direct-level100-private-still-frame-visually-triaged", "visual source status mismatch", failures)
    require(proof["sourceCaptureStatus"] == "direct-level100-copied-profile-window-still-frame-captured", "capture source status mismatch", failures)
    require(proof["sourceStaticTextSpeakerStatus"] == "PASS", "static text/speaker source status mismatch", failures)
    require(proof["artifactRootClass"] == "repo-local-ignored-private-evidence-root", "artifact root class mismatch", failures)
    require(proof["privateFrameArtifactClass"] == "private-still-frame-png", "private frame artifact class mismatch", failures)
    require(proof["privateFrameReviewedByClass"] == "codex-root-private-visual-triage", "private frame reviewer mismatch", failures)
    require(proof["selectedRoute"] == "direct-level100-candidate", "selected route mismatch", failures)
    require(proof["launchArguments"] == ["-skipfmv", "-level", "100"], "launch args mismatch", failures)
    require(proof["sourceCaptureFrameCount"] == 1, "source capture frame count mismatch", failures)
    require(proof["triagedFrameCount"] == 1, "triaged frame count mismatch", failures)
    require(proof["correlatedFrameCount"] == 1, "correlated frame count mismatch", failures)
    require(proof["captureFrameCount"] == 1, "capture frame count mismatch", failures)
    require(proof["captureWidth"] == 656, "capture width mismatch", failures)
    require(proof["captureHeight"] == 539, "capture height mismatch", failures)
    require(proof["visibleStateClass"] == "in-level-visual-candidate", "visible state class mismatch", failures)
    require(proof["visualFrameReadable"] is True, "visual readable mismatch", failures)
    require(proof["visualFrameBlank"] is False, "visual blank mismatch", failures)
    require(proof["bottomTutorialTextPanelVisible"] is True, "bottom text panel mismatch", failures)
    require(proof["tutorialTextGlyphsVisible"] is True, "tutorial glyphs mismatch", failures)
    require(proof["textOverlayCorrelationMethod"] == "public-parent-schema-correlation-no-ocr", "correlation method mismatch", failures)
    require(proof["textOverlayCorrelationRows"] == 1, "correlation row count mismatch", failures)
    require(proof["tokenUniverseClass"] == "static-level100-message-help-objective-loss-speaker-token-surface", "token universe class mismatch", failures)
    require(proof["relevantStaticTokensResolved"] == "68/68", "resolved token count string mismatch", failures)
    require(proof["relevantStaticTokenCount"] == 68, "relevant static token count mismatch", failures)
    require(proof["missingReferenceTokens"] == 0, "missing token count mismatch", failures)
    require(proof["messageRows"] == 45, "message row count mismatch", failures)
    require(proof["messageUnique"] == 43, "message unique count mismatch", failures)
    require(proof["helpRows"] == 6, "help row count mismatch", failures)
    require(proof["helpUnique"] == 6, "help unique count mismatch", failures)
    require(proof["objectiveRows"] == 8, "objective row count mismatch", failures)
    require(proof["objectiveUnique"] == 4, "objective unique count mismatch", failures)
    require(proof["lossRows"] == 2, "loss row count mismatch", failures)
    require(proof["lossUnique"] == 1, "loss unique count mismatch", failures)
    require(proof["speakerRows"] == 45, "speaker row count mismatch", failures)
    require(proof["speakerUnique"] == 3, "speaker unique count mismatch", failures)
    require(proof["speakerTokens"] == ["P_TATIANA", "P_KRAMER", "P_TECHNICIAN"], "speaker token order mismatch", failures)
    require(proof["speakerCounts"] == {"P_TATIANA": 40, "P_KRAMER": 4, "P_TECHNICIAN": 1}, "speaker counts mismatch", failures)
    require(proof["generatedOnlyReferencedTextTokenCount"] == 13, "generated-only token count mismatch", failures)
    require(proof["levelLocalMessageTokenCount"] == 40, "level-local message token count mismatch", failures)
    for key in FALSE_GUARD_FLAGS:
        require(proof[key] is False, f"proof guard flag must be false: {key}", failures)
    require(proof["missionScriptRuntimeEvidenceRows"] == 0, "MissionScript runtime rows mismatch", failures)

    require(guard["directLevel100VisualFrameTriageProof"] is True, "guard visual proof mismatch", failures)
    require(guard["directLevel100ScreenshotCaptureProof"] is True, "guard screenshot proof mismatch", failures)
    require(guard["staticTextSpeakerResolutionProof"] is True, "guard text/speaker proof mismatch", failures)
    require(guard["staticWalkthroughProof"] is True, "guard walkthrough proof mismatch", failures)
    require(guard["sourceVisualFrameTriageStatus"] == "direct-level100-private-still-frame-visually-triaged", "guard visual status mismatch", failures)
    require(guard["sourceCaptureStatus"] == "direct-level100-copied-profile-window-still-frame-captured", "guard capture status mismatch", failures)
    require(guard["sourceStaticTextSpeakerStatus"] == "PASS", "guard text/speaker status mismatch", failures)
    require(guard["captureFrameCount"] == 1, "guard capture frame count mismatch", failures)
    require(guard["triagedFrameCount"] == 1, "guard triaged frame count mismatch", failures)
    require(guard["correlatedFrameCount"] == 1, "guard correlated frame count mismatch", failures)
    require(guard["bottomTutorialTextPanelVisible"] is True, "guard bottom text panel mismatch", failures)
    require(guard["tutorialTextGlyphsVisible"] is True, "guard tutorial glyphs mismatch", failures)
    require(guard["relevantStaticTokensResolved"] == "68/68", "guard resolved token count mismatch", failures)
    require(guard["missingReferenceTokens"] == 0, "guard missing token count mismatch", failures)
    for key in FALSE_GUARD_FLAGS:
        require(guard[key] is False, f"guard flag must be false: {key}", failures)
    require(guard["installedGameMutation"] is False, "guard installed mutation mismatch", failures)
    require(guard["originalExecutableMutation"] is False, "guard original mutation mismatch", failures)
    require(guard["missionScriptRuntimeEvidenceRows"] == 0, "guard MissionScript runtime rows mismatch", failures)
    require(guard["privatePathLeakCount"] == 0, "private path leak count mismatch", failures)
    require(guard["rawArtifactLeakCount"] == 0, "raw artifact leak count mismatch", failures)
    require(guard["rawDialogueLeakCount"] == 0, "raw dialogue leak count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    require(no_bea_process_running(), "BEA process still running after text-overlay correlation proof", failures)
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
        "directLevel100TextOverlayCorrelationStatus=direct-level100-text-overlay-correlated-to-static-level100-token-surface",
        "sourceVisualFrameTriageStatus=direct-level100-private-still-frame-visually-triaged",
        "sourceCaptureStatus=direct-level100-copied-profile-window-still-frame-captured",
        "sourceStaticTextSpeakerStatus=PASS",
        "selectedRoute=direct-level100-candidate",
        "launchArguments=-skipfmv -level 100",
        "sourceCaptureFrameCount=1",
        "triagedFrameCount=1",
        "correlatedFrameCount=1",
        "newLaunch=false",
        "newScreenshotCapture=false",
        "captureFrameCount=1",
        "captureWidth=656",
        "captureHeight=539",
        "bottomTutorialTextPanelVisible=true",
        "tutorialTextGlyphsVisible=true",
        "textOverlayCorrelationMethod=public-parent-schema-correlation-no-ocr",
        "textOverlayCorrelationRows=1",
        "tokenUniverseClass=static-level100-message-help-objective-loss-speaker-token-surface",
        "relevantStaticTokensResolved=68/68",
        "relevantStaticTokenCount=68",
        "missingReferenceTokens=0",
        "messageRows=45",
        "messageUnique=43",
        "helpRows=6",
        "helpUnique=6",
        "objectiveRows=8",
        "objectiveUnique=4",
        "lossRows=2",
        "lossUnique=1",
        "speakerRows=45",
        "speakerUnique=3",
        "speakerTokens=P_TATIANA/P_KRAMER/P_TECHNICIAN",
        "speakerCounts=P_TATIANA:40/P_KRAMER:4/P_TECHNICIAN:1",
        "generatedOnlyReferencedTextTokenCount=13",
        "levelLocalMessageTokenCount=40",
        "rawDialogueIncluded=false",
        "rawDialoguePublished=false",
        "visibleTextExcerptPublished=false",
        "exactTextOcrPerformed=false",
        "exactVisibleTokenIdentityClaim=false",
        "exactVisibleTokenIdentityProven=false",
        "runtimeMessageDisplayClaim=false",
        "runtimeMessageDisplayProven=false",
        "missionScriptRuntimeEvidenceRows=0",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "privateProofAssetPublished=false",
        "privateCaptureLocatorIncluded=false",
        "privateArtifactHashIncluded=false",
        "privateArtifactBytesIncluded=false",
        "privateWindowIdentifiersIncluded=false",
        "privatePathLeakCount=0",
        "rawArtifactLeakCount=0",
        "rawDialogueLeakCount=0",
        "publicLeakCheck=PASS",
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
        PROFILE_ID,
        "direct-level100-text-overlay-correlated-to-static-level100-token-surface",
        "sourceVisualFrameTriageStatus=direct-level100-private-still-frame-visually-triaged",
        "sourceCaptureStatus=direct-level100-copied-profile-window-still-frame-captured",
        "sourceStaticTextSpeakerStatus=PASS",
        "correlatedFrameCount=1",
        "bottomTutorialTextPanelVisible=true",
        "tutorialTextGlyphsVisible=true",
        "textOverlayCorrelationMethod=public-parent-schema-correlation-no-ocr",
        "relevantStaticTokensResolved=68/68",
        "missingReferenceTokens=0",
        "messageRows=45",
        "messageUnique=43",
        "speakerRows=45",
        "speakerTokens=P_TATIANA/P_KRAMER/P_TECHNICIAN",
        "rawDialoguePublished=false",
        "exactTextOcrPerformed=false",
        "exactVisibleTokenIdentityClaim=false",
        "runtimeMessageDisplayClaim=false",
        "missionScriptRuntimeEvidenceRows=0",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing text-overlay token: {token}", failures)

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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed text-overlay correlation slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed timed-frame set slice", failures)
    require(f"Completed {FOLLOW_UP_SLICE}" in backlog, "backlog missing completed timed-frame text-overlay progression slice", failures)
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Boundary Proof Plan" in backlog,
        "backlog missing active runtime message display boundary slice",
        failures,
    )
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks text-overlay correlation active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks timed-frame set active", failures)
    require(f"The selected active static-to-proof slice is {FOLLOW_UP_SLICE}. Status: selected" not in backlog, "backlog still marks timed-frame text-overlay progression active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_text_overlay_correlation_probe.py --check",
        "missing package direct Level100 text-overlay correlation test script",
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
        print("MissionScript Level100 direct text-overlay correlation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 direct text-overlay correlation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
