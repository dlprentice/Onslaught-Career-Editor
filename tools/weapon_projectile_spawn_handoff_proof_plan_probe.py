#!/usr/bin/env python3
"""Validate the Weapon / Projectile spawn handoff proof plan and boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "weapon-projectile-spawn-handoff-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "weapon-projectile-spawn-handoff-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "weapon_projectile_spawn_handoff_proof_plan_2026-06-08.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
LORE_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

PLAN_LINK = "weapon-projectile-spawn-handoff-proof-plan.md"

STATIC_TOKENS = (
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "Wave911 focused remains historical-retired/non-reconstructable",
)

ANCHOR_TOKENS = (
    "Weapon / Projectile Spawn Handoff Proof Plan",
    "Status: active public-safe proof plan, not runtime proof",
    "weapon-projectile-spawn-handoff-proof-plan",
    "unit-battleengine-gameplay-static-contract.md",
    "selected weapon path through WalkerPart or JetPart weapon state, `CWeapon` event/filtering helpers, `ProjectileBurst` preset/fallback dispatch, and `CRound` spawn/arming handoff",
    "wave1160-weapon-projectile-targeting-current-risk-review",
    "19` metadata rows",
    "19` tag rows",
    "51` xref rows",
    "3272` instruction rows",
    "19` decompile rows",
    "battleengine-walkerpart-weapon-spine-review-wave1027",
    "12` primary metadata rows",
    "39` xref rows",
    "704` body-instruction rows",
    "battleengine-jetpart-weapon-status-review-wave1029",
    "13` primary metadata rows",
    "790` body-instruction rows",
    "projectile-burst-spawn-spine-review-wave1020",
    "5` primary metadata rows",
    "22` xref rows",
    "1651` body-instruction rows",
    "48`-row pointer-table export",
    "G:\\GhidraBackups\\BEA_20260606-011357_post_wave1160_weapon_projectile_targeting_current_risk_review_verified",
    "G:\\GhidraBackups\\BEA_20260601-014543_post_wave1027_battleengine_walkerpart_weapon_spine_review_verified",
    "G:\\GhidraBackups\\BEA_20260601-025247_post_wave1029_battleengine_jetpart_weapon_status_review_verified",
    "G:\\GhidraBackups\\BEA_20260531-214433_post_wave1020_projectile_burst_spawn_spine_review_verified",
    "0x00406560 CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
    "not exact `CBattleEngine::WeaponFired` identity",
    "0x00413cc0 CBattleEngineWalkerPart__FireWeapon",
    "0x004140d0 CBattleEngineWalkerPart__WeaponFired",
    "0x00412050 CBattleEngineJetPart__WeaponFired",
    "0x00414030 CBattleEngineWalkerPart__GetCurrentWeapon",
    "0x005061f0 CWeapon__DoesTargetMaskMatchDistanceProfile",
    "0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
    "0x00506930 CWeapon__HandleFireBurstEvent",
    "not final source `CWeapon::Fire` identity",
    "0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback",
    "0x005069f0 ProjectileBurst__SpawnFromCurrentPreset",
    "0x005078b0 ProjectileBurstPreset__GetListEntryIdByIndex",
    "0x004dac90 CRound__SelectBestTargetReaderAndSyncAimState",
    "0x004db150 CRound__SpawnConfiguredProjectile",
    "0x004db630 CRound__ArmProjectileAndSpawnTrailEffect",
    "Wave1161/Wave1162 collision and terrain rows as context only",
    "copied-profile guardrails",
    "Stop on crash, non-reproducible weapon path, ambiguous weapon identity",
)

READINESS_TOKENS = (
    "Weapon / Projectile Spawn Handoff Proof Plan Readiness Note",
    "proof plan complete, not runtime proof",
    "not a new static re-audit wave",
    "not a runtime test",
    "not a screenshot/capture proof",
    "not a BEA patch",
    "not a Godot slice",
    "not a rebuild parity claim",
    "No runtime weapon fire behavior, runtime projectile behavior, runtime projectile collision behavior",
)

FORBIDDEN_PHRASES = (
    "runtime weapon fire behavior proven",
    "runtime projectile behavior proven",
    "runtime projectile collision behavior proven",
    "runtime terrain interaction proven",
    "runtime damage behavior proven",
    "runtime target kill behavior proven",
    "runtime stealth behavior proven",
    "runtime cloak behavior proven",
    "exact retail cbattleengine::weaponfired identity proven",
    "weapon_fire_breaks_stealth proven",
    "exact source cweapon::fire identity proven",
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
    for token in (*STATIC_TOKENS, *READINESS_TOKENS, *ANCHOR_TOKENS[2:44]):
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
    require("Weapon / projectile spawn handoff proof plan" in backlog, "backlog missing weapon/projectile slice", failures)
    require("proof plan complete, not runtime proof" in backlog, "backlog missing weapon/projectile proof-plan status", failures)
    require("Do not broaden into collision, terrain interaction, damage, target kill, cloak/stealth, exact CBattleEngine::WeaponFired, or full Unit/BattleEngine runtime proof." in backlog, "backlog missing weapon broadening boundary", failures)
    require("Unit Targeting / Active-Reader Proof Plan" in backlog, "backlog dropped Unit targeting plan", failures)
    require("HUD / Frontend Overlay Visual Runtime Proof Plan" in backlog, "backlog dropped HUD plan", failures)
    require("Destroyable Segments Damage/Break Proof Plan" in backlog, "backlog dropped destroyable plan", failures)
    require("PhysicsScript Copied-Corpus Parser Proof" in backlog, "backlog dropped PhysicsScript result", failures)
    require("Texture/Mesh Material Sidecar Ledger Proof" in backlog, "backlog dropped texture/mesh material result", failures)

    mapped = read_text(MAPPED)
    require("Post-Wave1220 Transition Candidates" in mapped, "mapped systems missing transition candidates", failures)
    require("Active weapon/projectile spawn handoff proof-plan slice" in mapped, "mapped systems missing active weapon/projectile slice", failures)


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
    expected = r"py -3 tools\weapon_projectile_spawn_handoff_proof_plan_probe.py --check"
    actual = package["scripts"].get("test:weapon-projectile-spawn-handoff-proof-plan")
    require(actual == expected, "missing package Weapon/projectile proof-plan script", failures)


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
        print("Weapon / Projectile spawn handoff proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Weapon / Projectile spawn handoff proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
