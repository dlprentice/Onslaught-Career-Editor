#!/usr/bin/env python3
"""Check the source-visible weapon-fire path for the remaining stealth gap."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "references" / "Onslaught"


@dataclass(frozen=True)
class TokenCheck:
    path: str
    label: str
    token: str


TOKEN_CHECKS = (
    TokenCheck("Player.cpp", "player fire input", "BUTTON_MECH_FIRE_GUN_POD"),
    TokenCheck("Player.cpp", "player calls BattleEngine fire", "mBattleEngine->FireWeapon()"),
    TokenCheck("Player.cpp", "player cloak input", "BUTTON_MECH_CLOAK"),
    TokenCheck("Player.cpp", "player calls BattleEngine cloak", "mBattleEngine->HandleCloak()"),
    TokenCheck("BattleEngine.cpp", "BattleEngine FireWeapon method", "CBattleEngine::FireWeapon"),
    TokenCheck("BattleEngine.cpp", "walker part fire delegation", "mWalkerPart->FireWeapon();"),
    TokenCheck("BattleEngine.cpp", "jet part fire delegation", "mJetPart->FireWeapon();"),
    TokenCheck("BattleEngine.cpp", "BattleEngine WeaponFired wrapper", "CBattleEngine::WeaponFired"),
    TokenCheck("BattleEngine.cpp", "stealth reset on fired weapon", "mStealth=0.0f;"),
    TokenCheck("BattleEngineJetPart.cpp", "jet part weapon fire", "weapon->Fire();"),
    TokenCheck("BattleEngineJetPart.cpp", "jet part fired classifier", "CBattleEngineJetPart::WeaponFired"),
    TokenCheck("BattleEngineWalkerPart.cpp", "walker part weapon fire", "weapon->Fire();"),
    TokenCheck("BattleEngineWalkerPart.cpp", "walker part fired classifier", "CBattleEngineWalkerPart::WeaponFired"),
)

EXPECTED_WEAPON_FIRED_OCCURRENCES = {
    "BattleEngine.cpp": 3,
    "BattleEngine.h": 1,
    "BattleEngineJetPart.cpp": 1,
    "BattleEngineJetPart.h": 1,
    "BattleEngineWalkerPart.cpp": 1,
    "BattleEngineWalkerPart.h": 1,
}


def read_source(relative_path: str) -> str:
    return (SOURCE_ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def source_files() -> list[Path]:
    return [path for path in SOURCE_ROOT.rglob("*") if path.is_file()]


def check_tokens() -> list[str]:
    errors: list[str] = []
    for check in TOKEN_CHECKS:
        text = read_source(check.path)
        if check.token not in text:
            errors.append(f"{check.path}: missing {check.label}: {check.token}")
    return errors


def weapon_fired_occurrences() -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in source_files():
        if path.suffix.lower() not in {".cpp", ".h"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        count = text.count("WeaponFired")
        if count:
            counts[path.relative_to(SOURCE_ROOT).as_posix()] = count
    return counts


def check_weapon_fired_shape() -> list[str]:
    errors: list[str] = []
    counts = weapon_fired_occurrences()
    if counts != EXPECTED_WEAPON_FIRED_OCCURRENCES:
        errors.append(f"WeaponFired occurrence map changed: {counts}")
    return errors


def check_weapon_dependency_gap() -> list[str]:
    errors: list[str] = []
    weapon_header_refs = []
    for path in source_files():
        if path.suffix.lower() not in {".cpp", ".h"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if '#include "Weapon.h"' in text:
            weapon_header_refs.append(path.relative_to(SOURCE_ROOT).as_posix())

    if sorted(weapon_header_refs) != [
        "BattleEngine.cpp",
        "BattleEngineJetPart.cpp",
        "BattleEngineWalkerPart.cpp",
    ]:
        errors.append(f"Unexpected Weapon.h include map: {sorted(weapon_header_refs)}")

    matching_weapon_headers = [path.relative_to(SOURCE_ROOT).as_posix() for path in SOURCE_ROOT.rglob("Weapon.h")]
    matching_weapon_impls = [path.relative_to(SOURCE_ROOT).as_posix() for path in SOURCE_ROOT.rglob("Weapon.cpp")]
    if matching_weapon_headers or matching_weapon_impls:
        errors.append(
            "Weapon source dependency is now present; update runtime/static proof plan before relying on this gap: "
            f"headers={matching_weapon_headers} impls={matching_weapon_impls}"
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Return non-zero if expectations fail.")
    args = parser.parse_args()

    errors = []
    errors.extend(check_tokens())
    errors.extend(check_weapon_fired_shape())
    errors.extend(check_weapon_dependency_gap())

    counts = weapon_fired_occurrences()
    print("BattleEngine weapon-fire source path probe")
    print(f"Status: {'fail' if errors else 'pass'}")
    print(f"Token checks: {len(TOKEN_CHECKS)}")
    print(f"WeaponFired files: {len(counts)}")
    print(f"WeaponFired occurrences: {sum(counts.values())}")
    print("Weapon source dependency: referenced but not present in this checkout")
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1 if args.check else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
