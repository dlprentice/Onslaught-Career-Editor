#!/usr/bin/env python3
"""Validate the Unit targeting / active-reader proof plan and boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "unit-targeting-active-reader-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "unit-targeting-active-reader-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "unit_targeting_active_reader_proof_plan_2026-06-08.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
LORE_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

PLAN_LINK = "unit-targeting-active-reader-proof-plan.md"

STATIC_TOKENS = (
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "Wave911 focused remains historical-retired/non-reconstructable",
)

ANCHOR_TOKENS = (
    "Unit Targeting / Active-Reader Proof Plan",
    "Status: active public-safe proof plan, not runtime proof",
    "unit-battleengine-gameplay-static-contract.md",
    "target acquisition, candidate filtering/scoring, active-reader assignment, heading update, and iterator snapshot behavior",
    "wave1215-unit-targeting-combat-residual-current-risk-review",
    "5` primary targeting rows",
    "6` xref rows",
    "794` instruction rows",
    "5` decompile rows",
    "425` context xref rows",
    "1123` context instruction rows",
    "15` context decompile rows",
    "1` data-slot xref row",
    "cunit-active-reader-targeting-review-wave927",
    "23` xref rows",
    "464` instruction rows",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260607-090802_post_wave1215_unit_targeting_combat_residual_current_risk_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified",
    "0x004027c0 CAirGuide__AcquireNearestTargetReader",
    "0x00445070 CDiveBomber__SelectTarget",
    "0x0044e640 ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640",
    "0x00477cb0 CSquadNormal__SelectBestEngagementTarget",
    "0x004ea8d0 CRelaxedSquad__CreateIterator",
    "0x00428b50 CUnit__SetReaderAndComputeRelativeYaw",
    "0x00428bc0 CUnitAI__GetTargetHeadingWithOffset",
    "0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped",
    "0x004e97e0 CGenericActiveReader__SwapWithCandidateIfFormationCloser",
    "0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting",
    "0x004fb650 CUnit__ForwardAimTransformAndAttachTargetReader",
    "copied-profile guardrails",
    "Stop on crash, non-reproducible target, ambiguous unit/squad identity",
)

READINESS_TOKENS = (
    "Unit Targeting / Active-Reader Proof Plan Readiness Note",
    "proof plan complete, not runtime proof",
    "not a new static re-audit wave",
    "not a runtime test",
    "not a screenshot/capture proof",
    "not a BEA patch",
    "not a Godot slice",
    "not a rebuild parity claim",
    "No runtime targeting behavior, runtime squad AI behavior, runtime component behavior",
)

FORBIDDEN_PHRASES = (
    "runtime targeting behavior proven",
    "runtime squad ai behavior proven",
    "runtime component behavior proven",
    "runtime air-guide behavior proven",
    "runtime dive-bomber behavior proven",
    "runtime active-reader lifetime proven",
    "runtime heading behavior proven",
    "weapon fire proven",
    "weapon_fire_breaks_stealth proven",
    "exact layouts proven",
    "exact source-body identity proven",
    "bea patching behavior proven",
    "gameplay outcomes proven",
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
    for token in (*STATIC_TOKENS, *READINESS_TOKENS, *ANCHOR_TOKENS[2:30]):
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

    require(read_text(CONTRACT) == read_text(LORE_CONTRACT), "Unit/BattleEngine contract lore mirror mismatch", failures)
    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "transition backlog lore mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require("Unit targeting / active-reader proof plan" in backlog, "backlog missing unit targeting slice", failures)
    require("proof plan complete, not runtime proof" in backlog, "backlog missing unit targeting proof-plan status", failures)
    require("Do not broaden into weapon fire, damage, collision, morph/mode, cloak/stealth, or full Unit/BattleEngine runtime proof." in backlog, "backlog missing broadening boundary", failures)
    require("HUD / Frontend Overlay Visual Runtime Proof Plan" in backlog, "backlog dropped HUD plan", failures)
    require("Destroyable Segments Damage/Break Proof Plan" in backlog, "backlog dropped destroyable plan", failures)
    require("PhysicsScript Copied-Corpus Parser Proof" in backlog, "backlog dropped PhysicsScript result", failures)
    require("Texture/Mesh Material Sidecar Ledger Proof" in backlog, "backlog dropped texture/mesh material result", failures)

    mapped = read_text(MAPPED)
    require("Post-Wave1220 Transition Candidates" in mapped, "mapped systems missing transition candidates", failures)
    require("Active Unit targeting / active-reader proof-plan slice" in mapped, "mapped systems missing active Unit targeting slice", failures)


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
    expected = r"py -3 tools\unit_targeting_active_reader_proof_plan_probe.py --check"
    actual = package["scripts"].get("test:unit-targeting-active-reader-proof-plan")
    require(actual == expected, "missing package Unit targeting proof-plan script", failures)


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
        print("Unit targeting / active-reader proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Unit targeting / active-reader proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
