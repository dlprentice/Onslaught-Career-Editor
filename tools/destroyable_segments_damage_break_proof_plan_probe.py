#!/usr/bin/env python3
"""Validate the destroyable-segments damage/break proof plan and boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "destroyable-segments-damage-break-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "destroyable-segments-damage-break-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "destroyable_segments_damage_break_proof_plan_2026-06-08.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "destroyable-segments-static-contract.md"
LORE_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "destroyable-segments-static-contract.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

PLAN_LINK = "destroyable-segments-damage-break-proof-plan.md"

STATIC_TOKENS = (
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "Wave911 focused remains historical-retired/non-reconstructable",
)

ANCHOR_TOKENS = (
    "Destroyable Segments Damage/Break Proof Plan",
    "Status: active public-safe proof plan, not runtime proof",
    "destroyable-segments-static-contract.md",
    "wave1205-destroyable-segment-current-risk-review",
    "G:\\GhidraBackups\\BEA_20260607-021737_post_wave1205_destroyable_segment_current_risk_review_verified",
    "0x00442700 CDestructableSegment__RegisterChild",
    "0x004433f0 CDestroyableCoreSegment__AreCoreChildrenDestroyed",
    "CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold",
    "0x00442960 CDestroyableSegment__VFunc_03_ApplyDamage",
    "0x004435f0 CDestroyableCoreSegment__VFunc_03_ApplyDamage",
    "0x00443780 CDestroyableSwapSegment__VFunc_03_ApplyDamage",
    "0x00442b20 CDestroyableSegment__VFunc_08_HandleSegmentBreak",
    "0x00443810 CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak",
    "0x00442f60 CDestroyableSegment__VFunc_10_SpawnRubbleEffects",
    "0x00442710 CDestroyableSegment__SpawnConfiguredPickup",
    "0x004442d0",
    "0x00444300",
    "0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric",
    "copied-profile guardrails",
    "Stop on crash, non-reproducible target, ambiguous object identity",
)

READINESS_TOKENS = (
    "Destroyable Segments Damage/Break Proof Plan Readiness Note",
    "gameplay-contract proof plan complete, not runtime proof",
    "not a new static re-audit wave",
    "not a runtime test",
    "not a BEA patch",
    "not a rebuild parity claim",
    "5` destroyable-segment rows",
    "9` xref rows",
    "96` instruction rows",
    "5` decompile rows",
    "No broad Unit/BattleEngine runtime proof, runtime destruction behavior, BEA patching behavior, visual QA, rebuild parity, or no-noticeable-difference parity claim.",
)

FORBIDDEN_PHRASES = (
    "runtime destroyable-segment damage behavior proven",
    "runtime break behavior proven",
    "runtime rubble behavior proven",
    "runtime pickup behavior proven",
    "exact event payload schema proven",
    "exact concrete c++ layouts proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
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

    require(read_text(CONTRACT) == read_text(LORE_CONTRACT), "destroyable contract lore mirror mismatch", failures)
    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "transition backlog lore mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require("Destroyable-segments damage/break micro-slice" in backlog, "backlog missing destroyable slice", failures)
    require("gameplay-contract proof plan complete, not runtime proof" in backlog, "backlog missing destroyable proof-plan status", failures)
    require("No broad Unit/BattleEngine runtime proof" in backlog, "backlog missing broad Unit/BattleEngine boundary", failures)
    require("PhysicsScript Copied-Corpus Parser Proof" in backlog, "backlog dropped PhysicsScript result", failures)
    require("Texture/Mesh Material Sidecar Ledger Proof" in backlog, "backlog dropped texture/mesh material result", failures)

    mapped = read_text(MAPPED)
    require("Post-Wave1220 Transition Candidates" in mapped, "mapped systems missing transition candidates", failures)
    require("gameplay-contract proof plan" in mapped, "mapped systems missing gameplay-contract proof plan wording", failures)


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
    expected = r"py -3 tools\destroyable_segments_damage_break_proof_plan_probe.py --check"
    actual = package["scripts"].get("test:destroyable-segments-damage-break-proof-plan")
    require(actual == expected, "missing package destroyable proof-plan script", failures)


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
        print("Destroyable-segments damage/break proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Destroyable-segments damage/break proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
