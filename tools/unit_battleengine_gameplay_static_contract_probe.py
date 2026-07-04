#!/usr/bin/env python3
"""Validate the Unit/BattleEngine/gameplay static contract surfaces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
READINESS = ROOT / "release" / "readiness" / "unit_battleengine_gameplay_static_contract_wave1105_2026-06-04.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"


CORE_TOKENS = (
    "Unit / BattleEngine / Gameplay Static Contract",
    "unit-battleengine-gameplay-static-contract-wave1105",
    "633",
    "75",
    "0x004f9a90 CUnit__ApplyDamage",
    "0x004dfa40 CUnit__VFunc08_InitAndAddToWorld",
    "0x00404dd0 CBattleEngine__Init",
    "0x00406560 CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
    "0x00406da0 CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
    "0x0040c180 CBattleEngine__HandleEvent",
    "0x00412bc0 CBattleEngineWalkerPart__ctor",
    "0x00413cc0 CBattleEngineWalkerPart__FireWeapon",
    "0x00412050 CBattleEngineJetPart__WeaponFired",
    "0x00505e00 CWeapon__ctor_base",
    "0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
    "0x00415140 CUnitAI__HandleLandedStateTransition",
    "0x00428b50 CUnit__SetReaderAndComputeRelativeYaw",
    "0x004ff330 SharedUnitAI__HandleEventAndMaybeFire_004ff330",
    "0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound",
    "0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse",
    "0x00489ed0 CInfantryUnitVFunc__ReturnFlag24Float005d856cOr005d8568_00489ed0",
    "0x004d35d0 CPodVFunc__FlagArg70AndSeedMotion250_004d35d0",
    "1580",
    "20",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260526-105331_post_wave906_unit_battleengine_gameplay_static_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260528-013432_post_wave936_battleengine_init_morph_volume_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260528-043815_post_wave943_unit_weapon_gameplay_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260601-014543_post_wave1027_battleengine_walkerpart_weapon_spine_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260601-025247_post_wave1029_battleengine_jetpart_weapon_status_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260602-060358_post_wave1075_cunit_vfunc08_boundary_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260604-130410_post_wave1089_unit_family_residual_vtable_final_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260604-182217_post_wave1097_cunit_dtor_thunk_lifecycle_review_verified",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260606-011357_post_wave1160_weapon_projectile_targeting_current_risk_review_verified",
    "6411/6411 = 100.00%",
    "1560/1560 = 100.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "weapon_fire_breaks_stealth",
)

BOUNDARY_TOKENS = (
    "Runtime damage",
    "Exact object layouts",
    "Exact retail `CBattleEngine::WeaponFired` identity",
    "BEA patching behavior",
    "Clean-room rebuild parity",
)

OVERCLAIM_TOKENS = (
    "runtime damage proven",
    "runtime weapon behavior proven",
    "weapon_fire_breaks_stealth closed",
    "exact retail cbattleengine::weaponfired identity proven",
    "clean-room rebuild parity proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_contract(failures: list[str]) -> None:
    text = read_text(CONTRACT)
    for token in CORE_TOKENS + BOUNDARY_TOKENS:
        require(contains_token(text, token), f"contract missing token: {token}", failures)
    for bad in OVERCLAIM_TOKENS:
        require(bad not in text.lower(), f"contract overclaim token present: {bad}", failures)


def check_readiness(failures: list[str]) -> None:
    text = read_text(READINESS)
    for token in (
        "Unit / BattleEngine / Gameplay Static Contract Wave1105 Readiness Note",
        "unit-battleengine-gameplay-static-contract-wave1105",
        "no Ghidra export",
        "no Ghidra mutation",
        "0x004f9a90 CUnit__ApplyDamage",
        "0x00404dd0 CBattleEngine__Init",
        "0x00413cc0 CBattleEngineWalkerPart__FireWeapon",
        "0x00412050 CBattleEngineJetPart__WeaponFired",
        "0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound",
        "0x00489ed0 CInfantryUnitVFunc__ReturnFlag24Float005d856cOr005d8568_00489ed0",
        "6410/6410 = 100.00%",
        "1560/1560 = 100.00%",
        "812/1408 = 57.67%",
        "Runtime damage",
        "Exact object layouts",
        "weapon_fire_breaks_stealth",
        "clean-room rebuild parity",
    ):
        require(contains_token(text, token), f"readiness missing token: {token}", failures)


def check_navigation(failures: list[str]) -> None:
    docs = {
        "mapped-systems.md": read_text(MAPPED_SYSTEMS),
        "_index.md": read_text(INDEX),
        "RE-INDEX.md": read_text(RE_INDEX),
        "static-reaudit-campaign.md": read_text(CAMPAIGN),
        "developer_agent_state.json": read_text(DEVELOPER_STATE),
        "documentation_agent_state.json": read_text(DOCUMENTATION_STATE),
        "re_orchestrator_state.json": read_text(RE_STATE),
    }
    for name, text in docs.items():
        require("unit-battleengine-gameplay-static-contract.md" in text, f"{name} missing contract link token", failures)
        if name in {"developer_agent_state.json", "documentation_agent_state.json", "re_orchestrator_state.json"}:
            require("wave1160-weapon-projectile-targeting-current-risk-review" in text, f"{name} missing Wave1160 tag", failures)
        else:
            require("unit-battleengine-gameplay-static-contract-wave1105" in text, f"{name} missing Wave1105 tag", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"{name} overclaim token present: {bad}", failures)

    mapped = docs["mapped-systems.md"]
    require("Unit/BattleEngine gameplay static contract" in mapped, "mapped systems missing contract label", failures)
    require("runtime gameplay behavior" in mapped, "mapped systems missing runtime boundary", failures)

    campaign = docs["static-reaudit-campaign.md"]
    require("Wave1160 current-risk update" in campaign, "campaign current continuation not Wave1160", failures)
    require("516/1179 = 43.77%" in campaign, "campaign missing Wave1160 current-risk progress", failures)
    require("CBattleEngine__UpdateAutoTargetSetAndFireProjectiles" in campaign, "campaign missing BattleEngine anchor", failures)
    require("CUnit__VFunc08_InitAndAddToWorld" in campaign, "campaign missing CUnit vfunc08 anchor", failures)


def check_mirror(failures: list[str]) -> None:
    require(read_text(CONTRACT) == read_text(CONTRACT_MIRROR), "Unit/BattleEngine contract lore mirror mismatch", failures)


def check_package_script(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    expected = r"py -3 tools\unit_battleengine_gameplay_static_contract_probe.py --check"
    require(scripts.get("test:unit-battleengine-gameplay-static-contract") == expected, "missing package Unit/BattleEngine contract script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_contract(failures)
    check_readiness(failures)
    check_navigation(failures)
    check_mirror(failures)
    check_package_script(failures)

    if failures:
        print("Unit/BattleEngine gameplay static contract probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Unit/BattleEngine gameplay static contract probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
