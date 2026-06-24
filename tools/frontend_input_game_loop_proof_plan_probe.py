#!/usr/bin/env python3
"""Validate the Frontend / Input / Game Loop proof plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "frontend-input-game-loop-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "frontend-input-game-loop-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "frontend_input_game_loop_proof_plan_2026-06-08.md"
FRONTEND_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "frontend-input-game-loop-static-review-2026-05-26.md"
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

PLAN_LINK = "frontend-input-game-loop-proof-plan.md"

STATIC_TOKENS = (
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "Wave911 focused remains historical-retired/non-reconstructable",
)

ANCHOR_TOKENS = (
    "Frontend / Input / Game Loop Proof Plan",
    "Status: active public-safe proof plan, not runtime proof",
    "frontend-input-game-loop-proof-plan",
    "frontend-input-game-loop-static-review-wave907",
    "frontend-text-layout-review-wave922",
    "wave1179-input-audio-support-current-risk-review",
    "wave1197-fepbeconfig-frontend-residual-current-risk-review",
    "`436` selected function rows",
    "`33` families",
    "Frontend pages 176",
    "Game loop / player 69",
    "Frontend core / video render 54",
    "Menu widgets 51",
    "Input / controller 48",
    "Pause / message 38",
    "0x0046eee0 CGame__MainLoop",
    "0x0046e240 CGame__RunLevel",
    "0x0046f7e0 CGame__ReceiveButtonAction",
    "0x0046fb00 CGame__Pause",
    "0x0046fae0 CGame__UnPause",
    "0x0046cdf0 CGame__LoadLevel",
    "0x004d3080 CPlayer__AssignBattleEngine",
    "0x004684d0 CFrontEnd__Run",
    "0x00466ae0 CFrontEnd__SetPage",
    "0x004669a0 CFrontEnd__ReceiveButtonAction",
    "0x00468700 CFrontEnd__RenderCursorEndSceneAndAsyncSave",
    "0x00464c50 CFEPSaveGame__CreateSave",
    "0x00461e20 CFEPLoadGame__DoLoad",
    "0x0045d7e0 CFEPGoodies__Process",
    "CFEPBEConfig__Init",
    "TextLayout__WrapWideTextToFixedLines",
    "FrontEndText__GetLocalizedOrFallbackTextByToken",
    "0x0042db40 CController__DoMappings",
    "0x0042e4d0 CController__SendButtonAction",
    "0x00513120 PlatformInput__InitDirectInput",
    "0x00513370 PlatformInput__PollPadState",
    "0x00514760 CPCController__ReadControllerState",
    "0x0042da00 Input__UpdateCursorCenterWithWindowScale",
    "0x00523db0 Input__ResetMouseTransientState",
    "0x004cdd70 GameControllers__RelinquishControlForTarget",
    "0x004d06e0 CPauseMenu__ResumeGameAndPersistOptions",
    "0x004b7ea0 CMessageBox__StartVoiceOrFallbackTextReveal",
    "0x004b9ec0 CMessageLog__HandleInputCommand",
    "0x005412e0 CDXFrontEndVideo__Open",
    "0x00541790 CDXFrontEndVideo__Render",
    "game-loop route accounting",
    "frontend page transition design",
    "input/controller mapping design",
    "save/load/options menu handoff design",
    "pause/message lifecycle design",
    "frontend-video wrapper design",
    "Goodies/level/multiplayer page behavior design",
    r"G:\GhidraBackups\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified",
    r"G:\GhidraBackups\BEA_20260527-175851_post_wave922_frontend_text_layout_review_verified",
    r"G:\GhidraBackups\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified",
    r"G:\GhidraBackups\BEA_20260606-211310_post_wave1197_fepbeconfig_frontend_residual_current_risk_review_verified",
)

READINESS_TOKENS = (
    "Frontend / Input / Game Loop Proof Plan Readiness Note",
    "proof plan complete, not runtime proof",
    "not a new static re-audit wave",
    "not a runtime test",
    "not a screenshot/capture proof",
    "not a native input proof",
    "not a save/options mutation proof",
    "not a frontend-video playback proof",
    "not a BEA patch",
    "not a Godot slice",
    "not a rebuild parity claim",
    "No runtime menu navigation",
    "runtime input/controller behavior",
    "runtime pause/message behavior",
    "runtime save/load/defaultoptions behavior",
    "runtime frontend-video/Bink/FMV behavior",
)

FORBIDDEN_PHRASES = (
    "runtime menu navigation proven",
    "runtime input/controller behavior proven",
    "runtime pause/message behavior proven",
    "runtime save/load/defaultoptions behavior proven",
    "runtime goodies wall behavior proven",
    "runtime frontend-video behavior proven",
    "runtime bink behavior proven",
    "runtime fmv behavior proven",
    "runtime gameplay/game-loop outcomes proven",
    "visible frontend output proven",
    "visible hud output proven",
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
        "frontend-input-game-loop-static-review-wave907",
        "frontend-text-layout-review-wave922",
        "wave1179-input-audio-support-current-risk-review",
        "wave1197-fepbeconfig-frontend-residual-current-risk-review",
        "copied-profile, copied-file, or app-owned artifact-root work",
        "Stop on installed-game mutation need",
    ):
        require(token in text, f"readiness missing anchor token: {token}", failures)
    for phrase in FORBIDDEN_PHRASES:
        require(phrase not in lower, f"readiness overclaims: {phrase}", failures)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"readiness leaks public-forbidden token: {token}", failures)


def check_front_doors(failures: list[str]) -> None:
    for path in (FRONTEND_STATIC, BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        require(PLAN_LINK in text, f"{path.relative_to(ROOT)} missing proof-plan link", failures)
        for phrase in FORBIDDEN_PHRASES:
            require(phrase not in text.lower(), f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)

    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "transition backlog lore mirror mismatch", failures)
    require(read_text(MAPPED) == read_text(LORE_MAPPED), "mapped systems lore mirror mismatch", failures)
    require(read_text(BIN_INDEX) == read_text(LORE_BIN_INDEX), "binary index lore mirror mismatch", failures)
    require(read_text(RE_INDEX) == read_text(LORE_RE_INDEX), "RE index lore mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require("Completed Frontend / input / game-loop proof-plan slice" in backlog, "backlog missing completed frontend slice", failures)
    require("Completed Engine / platform / math / memory support proof-plan slice" in backlog, "backlog missing completed engine/platform slice", failures)
    require("Do not broaden into broad game-loop runtime, native input driving, save/options mutation, frontend-video playback, HUD visual proof, audio playback, Godot, patching, broad runtime proof, or rebuild parity." in backlog, "backlog missing frontend broadening boundary", failures)

    mapped = read_text(MAPPED)
    require("Completed frontend/input/game-loop proof-plan slice" in mapped, "mapped systems missing completed frontend slice", failures)
    require("Completed Engine / platform / math / memory support proof-plan slice" in mapped, "mapped systems missing completed engine/platform slice", failures)
    require("Frontend / Input / Game Loop Core" in mapped and PLAN_LINK in mapped, "mapped systems missing frontend row link", failures)


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
    expected = r"py -3 tools\frontend_input_game_loop_proof_plan_probe.py --check"
    actual = package["scripts"].get("test:frontend-input-game-loop-proof-plan")
    require(actual == expected, "missing package frontend/input proof-plan script", failures)


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
        print("Frontend / Input / Game Loop proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Frontend / Input / Game Loop proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
