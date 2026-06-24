#!/usr/bin/env python3
"""Validate the HUD/frontend overlay visual/runtime proof plan and boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "hud-frontend-overlay-visual-runtime-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "hud-frontend-overlay-visual-runtime-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "hud_frontend_overlay_visual_runtime_proof_plan_2026-06-08.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "hud-frontend-overlay-static-contract.md"
LORE_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "hud-frontend-overlay-static-contract.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

PLAN_LINK = "hud-frontend-overlay-visual-runtime-proof-plan.md"

STATIC_TOKENS = (
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "Wave911 focused remains historical-retired/non-reconstructable",
)

ANCHOR_TOKENS = (
    "HUD / Frontend Overlay Visual Runtime Proof Plan",
    "Status: active public-safe proof plan, not runtime proof",
    "hud-frontend-overlay-static-contract.md",
    "visual/runtime proof plan only",
    "No screenshot or runtime claim until app-owned capture is run.",
    "wave1158-hud-render-component-current-risk-review",
    "20` HUD rows",
    "24` xref rows",
    "7335` instruction rows",
    "wave1216-render-resource-texture-hud-tail-current-risk-review",
    "Wave1141",
    "HudRenderState__ApplyOverlaySpriteState",
    "CDXCompass__ApplyRenderStateModulate",
    "CDXCompass__ApplyRenderStateAdditive",
    "frontend-input-game-loop",
    "G:\\GhidraBackups\\BEA_20260606-002152_post_wave1158_hud_render_component_current_risk_review_verified",
    "G:\\GhidraBackups\\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified",
    "0x00481400 CHud__ctor_base",
    "0x00481450 CHud__Init",
    "0x00481650 CHud__LoadTextures",
    "0x00481f40 CHud__SetHudComponent",
    "0x00482050 CHud__PromotePendingHudComponent",
    "0x004879e0 CHud__RenderOverlayForViewpoint",
    "0x00487d10 CHud__RenderBattleline",
    "0x00488090 CHud__RenderActiveHudComponentPass",
    "0x0054b800 CHudComponent__RenderPassEntry",
    "0x00484c50 CHud__RenderTacticalRadarContacts",
    "0x00485d50 CHud__RenderObjectiveStatusPanel",
    "0x00482590 CHud__RenderTargetIndicatorOverlay",
    "copied-profile guardrails",
    "Stop on crash, non-reproducible state, ambiguous viewpoint/object identity",
)

READINESS_TOKENS = (
    "HUD / Frontend Overlay Visual Runtime Proof Plan Readiness Note",
    "visual/runtime proof plan complete, not runtime proof",
    "not a new static re-audit wave",
    "not a runtime test",
    "not a screenshot/capture proof",
    "not a BEA patch",
    "not a rebuild parity claim",
    "20` HUD rows",
    "24` xref rows",
    "7335` instruction rows",
    "20` decompile rows",
    "No screenshot/capture proof, broad frontend/game-loop runtime proof, runtime HUD behavior, BEA patching behavior, visual QA, rebuild parity, or no-noticeable-difference parity claim.",
)

FORBIDDEN_PHRASES = (
    "runtime hud behavior proven",
    "runtime frontend behavior proven",
    "runtime menu behavior proven",
    "runtime render ordering proven",
    "visible hud output proven",
    "target/radar/objective/battleline visual correctness proven",
    "runtime texture behavior proven",
    "gpu upload behavior proven",
    "exact concrete chud layouts proven",
    "exact layouts proven",
    "exact source-body identity proven",
    "bea patching behavior proven",
    "screenshot proof complete",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
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
    for token in (*STATIC_TOKENS, *READINESS_TOKENS, *ANCHOR_TOKENS[2:19]):
        require(token in text, f"readiness missing token: {token}", failures)
    for phrase in FORBIDDEN_PHRASES:
        require(phrase not in lower, f"readiness overclaims: {phrase}", failures)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"readiness leaks public-forbidden token: {token}", failures)


def check_front_doors(failures: list[str]) -> None:
    for path in (CONTRACT, BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        require(PLAN_LINK in text, f"{path.relative_to(ROOT)} missing proof-plan link", failures)
        for phrase in FORBIDDEN_PHRASES:
            require(phrase not in text.lower(), f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)

    require(read_text(CONTRACT) == read_text(LORE_CONTRACT), "HUD contract lore mirror mismatch", failures)
    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "transition backlog lore mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require("HUD/frontend overlay proof plan" in backlog, "backlog missing HUD slice", failures)
    require("visual/runtime proof plan complete, not runtime proof" in backlog, "backlog missing HUD proof-plan status", failures)
    require("No screenshot or runtime claim until app-owned capture is run." in backlog, "backlog missing screenshot/runtime boundary", failures)
    require("Destroyable Segments Damage/Break Proof Plan" in backlog, "backlog dropped destroyable plan", failures)
    require("PhysicsScript Copied-Corpus Parser Proof" in backlog, "backlog dropped PhysicsScript result", failures)
    require("Texture/Mesh Material Sidecar Ledger Proof" in backlog, "backlog dropped texture/mesh material result", failures)

    mapped = read_text(MAPPED)
    require("Post-Wave1220 Transition Candidates" in mapped, "mapped systems missing transition candidates", failures)
    require("visual/runtime proof plan" in mapped, "mapped systems missing visual/runtime proof plan wording", failures)


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
    expected = r"py -3 tools\hud_frontend_overlay_visual_runtime_proof_plan_probe.py --check"
    actual = package["scripts"].get("test:hud-frontend-overlay-visual-runtime-proof-plan")
    require(actual == expected, "missing package HUD proof-plan script", failures)


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
        print("HUD/frontend overlay visual/runtime proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HUD/frontend overlay visual/runtime proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
