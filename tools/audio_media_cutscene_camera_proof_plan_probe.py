#!/usr/bin/env python3
"""Validate the Audio / Media / Cutscene / Camera proof plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "audio-media-cutscene-camera-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "audio-media-cutscene-camera-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "audio_media_cutscene_camera_proof_plan_2026-06-08.md"
AUDIO_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "audio-media-cutscene-static-review-2026-05-26.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

PLAN_LINK = "audio-media-cutscene-camera-proof-plan.md"

STATIC_TOKENS = (
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "Wave911 focused remains historical-retired/non-reconstructable",
)

ANCHOR_TOKENS = (
    "Audio / Media / Cutscene / Camera Proof Plan",
    "Status: active public-safe proof plan, not runtime proof",
    "audio-media-cutscene-camera-proof-plan",
    "audio-media-cutscene-static-review-wave908",
    "ogg-message-lifecycle-review-wave1015",
    "wave1179-input-audio-support-current-risk-review",
    "wave1219-final-score16-current-risk-review",
    "`171` function rows",
    "`26` selected owner families",
    "CSoundManager",
    "CPCSoundManager",
    "CMusic",
    "CWaveSoundRead",
    "COggLoader",
    "COggFileRead",
    "OggVorbisStream",
    "CBinkOpenThread",
    "CDXFMV",
    "CFMV",
    "CCutscene",
    "CRTCutscene",
    "CMovieCamera",
    "CPanCamera",
    "CGenericCamera",
    "CCamera",
    "CSoundManager__Init",
    "CSoundManager__CreateSample",
    "CSoundManager__PlaySample",
    "CSoundManager__FadeTo",
    "CSoundManager__LoadCompressedSampleBank",
    "CPCSoundManager__CreateSampleFromData",
    "CPCSoundManager__CreateSoundBuffer",
    "CPCSoundManager__DecodeADPCM",
    "CPCSoundManager__LoadSampleFromBuffer_StubFail",
    "CMusic__Init",
    "CMusic__UpdateStatus",
    "Audio__ReinitializeSoundAndRestoreMusic",
    "CWaveSoundRead__Open",
    "CWaveSoundRead__ScalarDeletingDestructor",
    "COggLoader__ThreadProc_ReadPathIntoBuffer",
    "COggFileRead__ReadDecodedPcm",
    "COggFileRead__scalar_deleting_dtor",
    "OggVorbisStream__ReadPcmSamples",
    "CBinkOpenThread__WorkerMain",
    "CDXFMV__ctor_base",
    "CDXFMV__VFunc_06_0053f180",
    "CFMV__PlayFullscreenWithLoadingGate",
    "CCutscene__Load",
    "CCutscene__Start",
    "CCutscene__Update",
    "CCutscene__SetTrackSlotByFlag",
    "CRTCutscene__BuildCurrentFrameOutputs",
    "CMovieCamera__GetPos",
    "CMovieCamera__GetOrientation",
    "CPanCamera__Update",
    "CGenericCamera__GetPos",
    "CCamera__GetAspectRatio",
    "copied profile or app-owned artifact root",
    "audio sample lifecycle",
    "reader framing",
    "FMV/cache",
    "cutscene sync",
    "camera behavior",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260526-113941_post_wave908_audio_media_cutscene_static_review_verified",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260531-192131_post_wave1015_ogg_message_lifecycle_review_verified",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified",
)

READINESS_TOKENS = (
    "Audio / Media / Cutscene / Camera Proof Plan Readiness Note",
    "proof plan complete, not runtime proof",
    "not a new static re-audit wave",
    "not a runtime test",
    "not a screenshot/capture proof",
    "not a DirectSound playback proof",
    "not an Ogg/WAV decode proof",
    "not a Bink/FMV playback proof",
    "not a BEA patch",
    "not a Godot slice",
    "not a rebuild parity claim",
    "No runtime DirectSound playback",
    "runtime Ogg/WAV decode behavior",
    "runtime Bink/FMV behavior",
    "runtime music switching",
    "runtime cutscene playback/sync",
    "runtime camera switching",
)

FORBIDDEN_PHRASES = (
    "runtime directsound playback proven",
    "runtime ogg/wav decode behavior proven",
    "runtime bink/fmv behavior proven",
    "runtime music switching proven",
    "runtime cutscene playback/sync proven",
    "runtime camera switching proven",
    "visual/audio qa complete",
    "exact source-body identity proven",
    "bea patching behavior proven",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
    "runtime proof complete",
)

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_plan(failures: list[str]) -> None:
    text = read_text(PLAN)
    lower = text.lower()
    for token in (*STATIC_TOKENS, *ANCHOR_TOKENS):
        require(token in text, f"plan missing token: {token}", failures)
    for phrase in FORBIDDEN_PHRASES:
        require(phrase not in lower, f"plan overclaims: {phrase}", failures)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"plan leaks public-forbidden token: {token}", failures)
    require(read_text(LORE_PLAN) == text, "lore proof-plan mirror mismatch", failures)


def check_readiness(failures: list[str]) -> None:
    text = read_text(READINESS)
    lower = text.lower()
    for token in (*STATIC_TOKENS, *READINESS_TOKENS):
        require(token in text, f"readiness missing token: {token}", failures)
    for token in (
        "audio-media-cutscene-static-review-wave908",
        "ogg-message-lifecycle-review-wave1015",
        "wave1179-input-audio-support-current-risk-review",
        "wave1219-final-score16-current-risk-review",
        "copied-profile or app-owned artifact-root work",
        "private media and resource bytes out of public release scope",
        "Stop on private media leakage risk",
    ):
        require(token in text, f"readiness missing anchor token: {token}", failures)
    for phrase in FORBIDDEN_PHRASES:
        require(phrase not in lower, f"readiness overclaims: {phrase}", failures)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"readiness leaks public-forbidden token: {token}", failures)


def check_front_doors(failures: list[str]) -> None:
    for path in (AUDIO_STATIC, BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        require(PLAN_LINK in text, f"{path.relative_to(ROOT)} missing proof-plan link", failures)
        for phrase in FORBIDDEN_PHRASES:
            require(phrase not in text.lower(), f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)

    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "transition backlog lore mirror mismatch", failures)
    require(read_text(MAPPED) == read_text(LORE_MAPPED), "mapped systems lore mirror mismatch", failures)
    require(read_text(BIN_INDEX) == read_text(LORE_BIN_INDEX), "binary index lore mirror mismatch", failures)
    require(read_text(RE_INDEX) == read_text(LORE_RE_INDEX), "RE index lore mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require("Audio / media / cutscene / camera proof plan" in backlog, "backlog missing audio/media active slice", failures)
    require("proof plan complete, not runtime proof" in backlog, "backlog missing audio/media proof-plan status", failures)
    require("Completed Save / options controller byte-preservation proof-plan slice" in backlog, "backlog missing completed save/options slice", failures)
    require("Do not broaden into DirectSound playback, Ogg/WAV decode, Bink/FMV playback, music switching, cutscene sync, camera switching, visual/audio QA, Godot, patching, broad runtime proof, or rebuild parity." in backlog, "backlog missing audio/media broadening boundary", failures)

    mapped = read_text(MAPPED)
    require("Active audio/media/cutscene/camera proof-plan slice" in mapped, "mapped systems missing active audio/media slice", failures)
    require("Completed Save / options controller byte-preservation proof-plan slice" in mapped, "mapped systems missing completed save/options slice", failures)
    require("Audio / media / camera" in mapped and PLAN_LINK in mapped, "mapped systems missing audio/media row link", failures)


def check_progress_unchanged(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total function mismatch", failures)
    require(quality["commentedFunctions"] == 6411, "progress commented function mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)

    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk reviewed mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1117, "live focused mismatch", failures)
    require(current["legacyAdditiveReviewedDeprecated"] == 1210, "legacy additive mismatch", failures)
    require(current["isWave911Reconstruction"] is False, "Wave911 reconstruction flag mismatch", failures)


def check_package(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    expected = r"py -3 tools\audio_media_cutscene_camera_proof_plan_probe.py --check"
    actual = package["scripts"].get("test:audio-media-cutscene-camera-proof-plan")
    require(actual == expected, "missing package Audio/media proof-plan script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_plan(failures)
    check_readiness(failures)
    check_front_doors(failures)
    check_progress_unchanged(failures)
    check_package(failures)

    if failures:
        print("Audio / Media / Cutscene / Camera proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Audio / Media / Cutscene / Camera proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
