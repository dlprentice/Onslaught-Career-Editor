#!/usr/bin/env python3
"""Validate the MissionScript Level100 timed frame-set text-overlay progression correlation proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation-proof.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation.v1.json"
TIMED_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture.v1.json"
TEXT_OVERLAY_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation.v1.json"
TEXT_SPEAKER_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution.v1.json"
WALKTHROUGH_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_timed_frame_set_text_overlay_progression_correlation_2026-06-09.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Text Overlay Progression Correlation Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Capture Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Boundary Proof Plan"
CHECKLIST_TEMPLATE_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Template Proof Plan"
CHECKLIST_DRY_RUN_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Dry-Run Validation Proof Plan"
ACTIVE_AFTER_NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Arm Boundary Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation-proof.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation.v1.json"
STATUS_TOKEN = "direct-level100-timed-frame-set-text-overlay-progression-correlated-to-static-level100-token-surface"

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
    "runtime message display behavior proven",
    "message progressed from token",
    "speaker identity changed per frame",
    "exact visible text identity proven",
    "ocr identity proven",
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
    "privateProofAssetPublished",
    "privateCaptureLocatorIncluded",
    "privateArtifactHashIncluded",
    "privateArtifactBytesIncluded",
    "privateWindowIdentifiersIncluded",
    "newLaunch",
    "newScreenshotCapture",
    "newPrivateFrameReview",
    "timingCorrectnessClaim",
    "frameSetArtifactPublished",
    "rawDialogueIncluded",
    "rawDialoguePublished",
    "visibleTextExcerptPublished",
    "exactTextOcrPerformed",
    "exactVisibleTokenIdentityClaim",
    "exactVisibleTokenIdentityProven",
    "perFrameTokenIdentityClaim",
    "perFrameSpeakerIdentityClaim",
    "runtimeMessageDisplayClaim",
    "runtimeMessageDisplayProven",
    "sourceSelectionObserved",
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


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    proof = result["progressionCorrelationProof"]
    guard = result["guardSummary"]
    timed = read_json(TIMED_RESULT)
    timed_proof = timed["timedFrameSetCaptureProof"]
    text_overlay = read_json(TEXT_OVERLAY_RESULT)
    text_overlay_proof = text_overlay["textOverlayCorrelationProof"]
    text_speaker = read_json(TEXT_SPEAKER_RESULT)
    walkthrough = read_json(WALKTHROUGH_RESULT)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation.v1", "schema version mismatch", failures)
    require(result["status"] == "COMPLETE", "status mismatch", failures)
    require(result["directLevel100TimedFrameSetTextOverlayProgressionCorrelationStatus"] == STATUS_TOKEN, "status token mismatch", failures)
    require(result["staticContext"]["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(result["staticContext"]["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(result["staticContext"]["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(result["staticContext"]["currentRiskFocused"] == "1179/1179 = 100.00%", "current risk mismatch", failures)
    require(result["staticContext"]["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(result["staticContext"]["staticAccountingSource"] == "static-reaudit-measurement-register.md", "static accounting source mismatch", failures)
    require(result["staticContext"]["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)
    require(result["staticContext"]["legacyStaticCounterRejected"] == "6113/6113", "legacy static counter mismatch", failures)

    require(timed["status"] == "COMPLETE", "timed-frame parent status mismatch", failures)
    require(timed["directLevel100TimedFrameSetCaptureStatus"] == "direct-level100-copied-profile-timed-private-frame-set-captured", "timed-frame parent token mismatch", failures)
    require(text_overlay["status"] == "COMPLETE", "text-overlay parent status mismatch", failures)
    require(text_overlay["directLevel100TextOverlayCorrelationStatus"] == "direct-level100-text-overlay-correlated-to-static-level100-token-surface", "text-overlay parent token mismatch", failures)
    require(text_speaker["status"] == "PASS", "text/speaker parent status mismatch", failures)
    require(walkthrough["status"] == "PASS", "walkthrough parent status mismatch", failures)

    require(proof["profileIdClass"] == "level100-clean-materialized-copied-profile", "profile class mismatch", failures)
    require(proof["sourceTimedFrameSetCaptureStatus"] == timed["directLevel100TimedFrameSetCaptureStatus"], "source timed-frame status mismatch", failures)
    require(proof["sourceTextOverlayCorrelationStatus"] == text_overlay["directLevel100TextOverlayCorrelationStatus"], "source text-overlay status mismatch", failures)
    require(proof["sourceStaticTextSpeakerStatus"] == text_speaker["status"], "source text/speaker status mismatch", failures)
    require(proof["selectedRoute"] == "direct-level100-candidate", "selected route mismatch", failures)
    require(proof["launchArguments"] == ["-skipfmv", "-level", "100"], "launch args mismatch", failures)
    require(proof["requestedFrameCount"] == timed_proof["requestedFrameCount"] == 4, "requested frame count mismatch", failures)
    require(proof["capturedFrameCount"] == timed_proof["capturedFrameCount"] == 4, "captured frame count mismatch", failures)
    require(proof["frameScheduleClass"] == timed_proof["frameScheduleClass"], "frame schedule class mismatch", failures)
    require(proof["captureDurationSeconds"] == timed_proof["captureDurationSeconds"] == 25, "capture duration mismatch", failures)
    require(proof["captureWidth"] == timed_proof["captureWidth"] == 656, "capture width mismatch", failures)
    require(proof["captureHeight"] == timed_proof["captureHeight"] == 539, "capture height mismatch", failures)
    require(proof["frameDimensionClass"] == timed_proof["frameDimensionClass"] == "stable-656x539", "frame dimension class mismatch", failures)
    require(proof["visibleProgressionClassOnly"] is True, "visible progression class guard mismatch", failures)
    require(proof["textOverlayProgressionCorrelationMethod"] == "public-parent-schema-correlation-no-ocr", "correlation method mismatch", failures)
    require(proof["progressionCorrelationRows"] == timed_proof["visibleProgressionRows"] == 4, "progression row count mismatch", failures)
    require(proof["visibleProgressionRows"] == timed_proof["visibleProgressionRows"] == 4, "visible progression row count mismatch", failures)
    require(proof["nonblankFrameRows"] == timed_proof["nonblankFrameRows"] == 4, "nonblank frame count mismatch", failures)
    require(proof["inGameRenderedFrameRows"] == timed_proof["inGameRenderedFrameRows"] == 4, "in-game frame count mismatch", failures)
    require(proof["exteriorVehicleWorldFrameRows"] == timed_proof["exteriorVehicleWorldFrameRows"] == 1, "exterior row count mismatch", failures)
    require(proof["cockpitHudFrameRows"] == timed_proof["cockpitHudFrameRows"] == 3, "cockpit HUD row count mismatch", failures)
    require(proof["bottomTutorialTextPanelVisibleFrameRows"] == timed_proof["bottomTutorialTextPanelVisibleFrameRows"] == 3, "tutorial panel row count mismatch", failures)
    require(proof["tutorialTextGlyphsVisibleFrameRows"] == timed_proof["tutorialTextGlyphsVisibleFrameRows"] == 3, "tutorial glyph row count mismatch", failures)
    require(proof["speakerPortraitVisibleFrameRows"] == timed_proof["speakerPortraitVisibleFrameRows"] == 3, "speaker portrait row count mismatch", failures)
    require(proof["textOverlayChangedAcrossFrameSetClass"] is True, "text overlay change class mismatch", failures)
    require(proof["publicFrameClassBuckets"] == "exterior-world-no-tutorial-panel:1/cockpit-hud-tutorial-overlay:3", "public frame class bucket mismatch", failures)
    require(proof["timedFrameSetTextOverlayProgressionClass"] == "exterior-world-to-cockpit-hud-tutorial-overlay-change-class", "progression class mismatch", failures)
    require(proof["tokenUniverseClass"] == text_overlay_proof["tokenUniverseClass"], "token universe mismatch", failures)
    require(proof["relevantStaticTokensResolved"] == text_overlay_proof["relevantStaticTokensResolved"] == "68/68", "resolved token count mismatch", failures)
    require(proof["relevantStaticTokenCount"] == text_overlay_proof["relevantStaticTokenCount"] == text_speaker["resolution"]["relevantStaticTokenCount"] == 68, "static token count mismatch", failures)
    require(proof["missingReferenceTokens"] == text_overlay_proof["missingReferenceTokens"] == 0, "missing token count mismatch", failures)
    require(proof["messageRows"] == text_overlay_proof["messageRows"] == text_speaker["level100References"]["messageRows"] == 45, "message row count mismatch", failures)
    require(proof["messageUnique"] == text_overlay_proof["messageUnique"] == text_speaker["level100References"]["messageUnique"] == 43, "message unique count mismatch", failures)
    require(proof["helpRows"] == text_overlay_proof["helpRows"] == text_speaker["level100References"]["helpRows"] == 6, "help row count mismatch", failures)
    require(proof["objectiveUnique"] == text_overlay_proof["objectiveUnique"] == text_speaker["level100References"]["objectiveUnique"] == 4, "objective unique count mismatch", failures)
    require(proof["lossUnique"] == text_overlay_proof["lossUnique"] == text_speaker["level100References"]["lossUnique"] == 1, "loss unique count mismatch", failures)
    require(proof["speakerRows"] == text_overlay_proof["speakerRows"] == text_speaker["level100References"]["speakerRows"] == 45, "speaker row count mismatch", failures)
    require(proof["speakerUnique"] == text_overlay_proof["speakerUnique"] == text_speaker["level100References"]["speakerUnique"] == 3, "speaker unique count mismatch", failures)
    require(proof["speakerTokens"] == ["P_TATIANA", "P_KRAMER", "P_TECHNICIAN"], "speaker tokens mismatch", failures)
    require(proof["speakerCounts"] == {"P_TATIANA": 40, "P_KRAMER": 4, "P_TECHNICIAN": 1}, "speaker counts mismatch", failures)
    require(proof["missionScriptRuntimeEvidenceRows"] == 0, "MissionScript runtime row count mismatch", failures)
    for key in FALSE_GUARDS:
        require(proof[key] is False, f"proof guard must be false: {key}", failures)
    for key in ("monotonicCaptureTimestamps", "allFrameArtifactsPrivate"):
        require(proof[key] is True, f"proof guard must be true: {key}", failures)

    require(guard["directLevel100TimedFrameSetCaptureProof"] is True, "guard timed parent mismatch", failures)
    require(guard["directLevel100TextOverlayCorrelationProof"] is True, "guard text-overlay parent mismatch", failures)
    require(guard["staticTextSpeakerResolutionProof"] is True, "guard text/speaker parent mismatch", failures)
    require(guard["staticWalkthroughProof"] is True, "guard walkthrough parent mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    for key in FALSE_GUARDS:
        if key in guard:
            require(guard[key] is False, f"guard must be false: {key}", failures)
    for key in (
        "publicAbsolutePathLeakCount",
        "publicSha256ValueLeakCount",
        "publicWindowIdentifierLeakCount",
        "publicProcessIdentifierLeakCount",
        "privatePathLeakCount",
        "rawArtifactLeakCount",
        "rawDialogueLeakCount",
        "missionScriptRuntimeEvidenceRows",
    ):
        require(guard[key] == 0, f"guard count must be zero: {key}", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    require(no_bea_process_running(), "BEA process still running after progression correlation proof", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        PLAN_LINK,
        RESULT_LINK,
        f"directLevel100TimedFrameSetTextOverlayProgressionCorrelationStatus={STATUS_TOKEN}",
        "profileIdClass=level100-clean-materialized-copied-profile",
        "profileIdPublished=false",
        "sourceTimedFrameSetCaptureStatus=direct-level100-copied-profile-timed-private-frame-set-captured",
        "sourceTextOverlayCorrelationStatus=direct-level100-text-overlay-correlated-to-static-level100-token-surface",
        "sourceStaticTextSpeakerStatus=PASS",
        "selectedRoute=direct-level100-candidate",
        "launchArguments=-skipfmv -level 100",
        "newLaunch=false",
        "newScreenshotCapture=false",
        "newPrivateFrameReview=false",
        "requestedFrameCount=4",
        "capturedFrameCount=4",
        "frameScheduleClass=bounded-four-frame-schedule",
        "captureDurationSeconds=25",
        "monotonicCaptureTimestamps=true",
        "timingCorrectnessClaim=false",
        "captureWidth=656",
        "captureHeight=539",
        "frameDimensionClass=stable-656x539",
        "allFrameArtifactsPrivate=true",
        "frameSetArtifactPublished=false",
        "visibleProgressionClassOnly=true",
        "textOverlayProgressionCorrelationMethod=public-parent-schema-correlation-no-ocr",
        "progressionCorrelationRows=4",
        "visibleProgressionRows=4",
        "nonblankFrameRows=4",
        "inGameRenderedFrameRows=4",
        "exteriorVehicleWorldFrameRows=1",
        "cockpitHudFrameRows=3",
        "bottomTutorialTextPanelVisibleFrameRows=3",
        "tutorialTextGlyphsVisibleFrameRows=3",
        "speakerPortraitVisibleFrameRows=3",
        "textOverlayChangedAcrossFrameSetClass=true",
        "publicFrameClassBuckets=exterior-world-no-tutorial-panel:1/cockpit-hud-tutorial-overlay:3",
        "timedFrameSetTextOverlayProgressionClass=exterior-world-to-cockpit-hud-tutorial-overlay-change-class",
        "tokenUniverseClass=static-level100-message-help-objective-loss-speaker-token-surface",
        "relevantStaticTokensResolved=68/68",
        "relevantStaticTokenCount=68",
        "missingReferenceTokens=0",
        "messageRows=45",
        "messageUnique=43",
        "speakerTokens=P_TATIANA/P_KRAMER/P_TECHNICIAN",
        "speakerCounts=P_TATIANA:40/P_KRAMER:4/P_TECHNICIAN:1",
        "rawDialogueIncluded=false",
        "rawDialoguePublished=false",
        "visibleTextExcerptPublished=false",
        "exactTextOcrPerformed=false",
        "exactVisibleTokenIdentityClaim=false",
        "exactVisibleTokenIdentityProven=false",
        "perFrameTokenIdentityClaim=false",
        "perFrameSpeakerIdentityClaim=false",
        "runtimeMessageDisplayClaim=false",
        "runtimeMessageDisplayProven=false",
        "sourceSelectionObserved=false",
        "missionScriptRuntimeEvidenceRows=0",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "privateProofAssetPublished=false",
        "privateCaptureLocatorIncluded=false",
        "privateArtifactHashIncluded=false",
        "privateArtifactBytesIncluded=false",
        "privateWindowIdentifiersIncluded=false",
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
        CHECKLIST_TEMPLATE_SLICE,
        CHECKLIST_DRY_RUN_SLICE,
        ACTIVE_AFTER_NEXT_SLICE,
        STATUS_TOKEN,
        "profileIdClass=level100-clean-materialized-copied-profile",
        "profileIdPublished=false",
        "progressionCorrelationRows=4",
        "bottomTutorialTextPanelVisibleFrameRows=3",
        "textOverlayChangedAcrossFrameSetClass=true",
        "publicFrameClassBuckets=exterior-world-no-tutorial-panel:1/cockpit-hud-tutorial-overlay:3",
        "relevantStaticTokensResolved=68/68",
        "missingReferenceTokens=0",
        "exactTextOcrPerformed=false",
        "runtimeMessageDisplayClaim=false",
        "sourceSelectionObserved=false",
        "missionScriptRuntimeEvidenceRows=0",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing progression token: {token}", failures)

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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed progression slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed runtime message boundary slice", failures)
    require(f"Completed {CHECKLIST_TEMPLATE_SLICE}" in backlog, "backlog missing completed runtime message checklist-template slice", failures)
    require(f"Completed {CHECKLIST_DRY_RUN_SLICE}" in backlog, "backlog missing completed runtime message checklist dry-run slice", failures)
    require(
        f"The selected active static-to-proof slice is {ACTIVE_AFTER_NEXT_SLICE}" in backlog
        or f"Completed {ACTIVE_AFTER_NEXT_SLICE}" in backlog,
        "backlog missing active/completed private-frame arm-boundary slice",
        failures,
    )
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks progression slice active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks boundary slice active", failures)
    require(f"The selected active static-to-proof slice is {CHECKLIST_DRY_RUN_SLICE}. Status: selected" not in backlog, "backlog still marks checklist dry-run slice active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_timed_frame_set_text_overlay_progression_correlation_probe.py --check",
        "missing package direct Level100 timed frame-set text-overlay progression test script",
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
        print("MissionScript Level100 direct timed frame-set text-overlay progression correlation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 direct timed frame-set text-overlay progression correlation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
