#!/usr/bin/env python3
"""Public-safe source-anchor coverage probe for BattleEngine gameplay logic.

This is a read-only reverse-engineering coverage check. It scans the local
Stuart source reference tree and repo RE docs for specific mechanics anchors,
then writes a compact JSON report under ``subagents/``. It does not launch the
game, mutate BEA.exe, mutate Ghidra, or copy private assets.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "references" / "Onslaught"
DEFAULT_OUT = ROOT / "subagents" / "battleengine-logic-coverage" / "current" / "battleengine-logic-coverage.json"


@dataclass(frozen=True)
class Anchor:
    key: str
    file: str
    tokens: tuple[str, ...]
    summary: str


ANCHORS: tuple[Anchor, ...] = (
    Anchor(
        "damage_stat_fixed_point",
        "BattleEngine.cpp",
        ("PS_DAMAGETAKEN", "inAmount*256"),
        "Damage-taking stats use a x256 fixed-point increment in the source BattleEngine damage path.",
    ),
    Anchor(
        "damage_shield_efficiency",
        "BattleEngine.cpp",
        ("mShieldEfficiency/100.0f", "mShields-=shieldDamage", "mAugValue+=shieldDamage"),
        "Shield damage uses configured shield efficiency and charges augmentation from absorbed shield damage.",
    ),
    Anchor(
        "damage_walker_energy_tracks_shields",
        "BattleEngine.cpp",
        ("mState==BATTLE_ENGINE_STATE_WALKER", "mEnergy=mShields"),
        "Walker-mode energy is synchronized from shields after the damage path.",
    ),
    Anchor(
        "damage_invulnerability_restore",
        "BattleEngine.cpp",
        ("mVulnerable == FALSE", "mLife = lastLife", "mShields =lastshields", "mEnergy = lastenergy"),
        "Source-side invulnerability restores life, shields, and energy to pre-hit values after damage processing.",
    ),
    Anchor(
        "transform_reject_special_moves",
        "BattleEngine.cpp",
        ("GetIsDoingSpecialAirMove() == TRUE", "GetIsDoingSpecialWalkerMove() == TRUE"),
        "Transform requests are rejected while either air or walker special moves are active.",
    ),
    Anchor(
        "transform_morph_method_anchor",
        "BattleEngine.cpp",
        (
            "void CBattleEngine::Morph()",
            "BATTLE_ENGINE_STATE_MORPHING_INTO_WALKER",
            "BATTLE_ENGINE_STATE_MORPHING_INTO_JET",
            'SetAnimMode("flytowalk"',
            'SetAnimMode("walktofly"',
        ),
        "Source transform/morph requests are implemented by CBattleEngine::Morph, not a CBattleEngine::"
        "Transform method.",
    ),
    Anchor(
        "transform_jet_to_walker_event",
        "BattleEngine.cpp",
        ("BECOME_WALKER", "BATTLE_ENGINE_TRANSFORM_TIME", "BATTLE_ENGINE_STATE_MORPHING_INTO_WALKER"),
        "Jet-to-walker transform queues the walker event and enters the morphing-to-walker state.",
    ),
    Anchor(
        "transform_walker_to_jet_energy_gate",
        "BattleEngine.cpp",
        ("mEnergy>=mConfiguration->mMinTransformEnergy", "BATTLE_ENGINE_STATE_MORPHING_INTO_JET", "BECOME_JET"),
        "Walker-to-jet transform is gated by minimum transform energy and then queues/enters jet morphing.",
    ),
    Anchor(
        "jet_energy_cost",
        "BattleEngineJetPart.cpp",
        ("mMinAirEnergyCost", "mMaxAirEnergyCost", "mMainPart->mEnergy-=cost"),
        "Jet movement spends configured air energy cost unless infinite-energy mode is active.",
    ),
    Anchor(
        "jet_stall_forces_morph_to_walker",
        "BattleEngineJetPart.cpp",
        (
            "mMainPart->mTransformStartTime+2.5f<EVENT_MANAGER.GetTime()",
            "mMainPart->mVelocity.MagnitudeSq()<0.15f*0.15f",
            "mMainPart->mStalling=TRUE",
            "mMainPart->mStallTime=EVENT_MANAGER.GetTime()",
            "mMainPart->mVelocity.MagnitudeSq()>=0.15f*0.15f",
            "mMainPart->mStalling=FALSE",
            "mMainPart->mStallTime+2.5f<EVENT_MANAGER.GetTime()",
            "mMainPart->Morph();",
        ),
        "Jet mode enters a stall after sustained low speed, clears the stall on recovery, and calls Morph after a sustained stall window.",
    ),
    Anchor(
        "walker_recharge",
        "BattleEngineWalkerPart.cpp",
        ("mGroundEnergyIncrease", "mMainPart->mEnergy+=recharge", "mMainPart->mShields=mMainPart->mEnergy"),
        "Walker movement recharges energy and mirrors shields from energy during recharge.",
    ),
    Anchor(
        "cloak_energy_gate_burn_and_render",
        "BattleEngine.cpp",
        (
            "void CBattleEngine::HandleCloak()",
            "mEnergy>=mConfiguration->mMinTransformEnergy",
            "mEnergy-=mConfiguration->mMaxAirEnergyCost",
            "Decloak();",
            "mDesiredStealth=mConfiguration->mStealth",
            "RF_CLOAKED",
        ),
        "Cloak toggling is gated by transform energy, drains air-energy cost while active, force-decloaks at zero energy, and renders with cloaked alpha flags.",
    ),
    Anchor(
        "target_lock_modes_and_stealth_range",
        "BattleEngine.cpp",
        (
            "void    CBattleEngine::HandleLocks()",
            "weapon->ReadyToFire()",
            "case kDirectLockMode",
            "case kProximityLockMode",
            "case kSequenceLockMode",
            "CountLocks()>=weapon->GetMaxLocks()",
            "magnitudeSq=weapon->GetLockRange()*(1.0f-unit->GetStealth()/100.0f)",
            "StartLock(unit,weapon->GetLockTime(),TRUE)",
        ),
        "Target lock acquisition is gated by weapon readiness/max locks, has direct/proximity/sequence modes, and reduces effective range by target stealth.",
    ),
    Anchor(
        "augmented_weapon_charge_decay_and_reset",
        "BattleEngine.cpp",
        (
            "#define MAX_AUG_VALUE",
            "#define AUG_DECREASE_RATE",
            "mAugValue-=AUG_DECREASE_RATE",
            "else if (mAugValue>=MAX_AUG_VALUE)",
            "if ((!mAugActive) && (mWalkerPart->GetAugWeapon()))",
            "mAugValue+=shieldDamage",
            "void CBattleEngine::AugmentWeapon()",
            "mAugActive=TRUE",
            "void CBattleEngine::UnaugmentWeapon()",
            "mAugActive=FALSE",
        ),
        "The augmented weapon meter charges from shield absorption, clamps at a max value, activates the augmentation, decays while active, and resets when unaugmented.",
    ),
    Anchor(
        "weapon_fire_breaks_stealth",
        "BattleEngine.cpp",
        (
            "BOOL CBattleEngine::WeaponFired(",
            "if (mJetPart->WeaponFired(inWeapon))",
            "if (mWalkerPart->WeaponFired(inWeapon))",
            "mStealth=0.0f;",
        ),
        "Firing either jet or walker weapons clears BattleEngine stealth state in the source.",
    ),
    Anchor(
        "config_defaults",
        "BattleEngineDataManager.cpp",
        ("mEnergy=2.5f", "mMaxAirEnergyCost=0.3f", "mMinTransformEnergy=1.0f", "mShieldEfficiency=90.0f"),
        "Default BattleEngine configuration values include energy, air cost, transform energy, and shield efficiency.",
    ),
    Anchor(
        "player_god_mode_toggles",
        "Player.cpp",
        ("SetVulnerable(FALSE)", "SetInfinateEnergy(TRUE)", "SetVulnerable(TRUE)", "SetInfinateEnergy(FALSE)"),
        "Source player god-mode helpers toggle BattleEngine vulnerability and infinite-energy flags.",
    ),
)


DOC_CHECKS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    (
        "reverse-engineering/game-mechanics/god-mode.md",
        ("SetVulnerable", "SetInfinateEnergy", "Damage()", "Steam build"),
        "God-mode doc links source-side vulnerability/energy behavior to Steam-build runtime posture without claiming exact identity.",
    ),
    (
        "reverse-engineering/source-code/_index.md",
        ("BattleEngine.cpp", "BattleEngineJetPart.cpp", "BattleEngineWalkerPart.cpp"),
        "Source index names the BattleEngine source files used for mechanics reconstruction.",
    ),
    (
        "reverse-engineering/quick-reference/source-files.md",
        ("BattleEngine.cpp/h", "BattleEngineJetPart.cpp/h", "BattleEngineWalkerPart.cpp/h"),
        "Quick reference lists the BattleEngine source families.",
    ),
)


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def line_hits(path: Path, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    hits: dict[str, list[int]] = {}
    for token in tokens:
        hits[token] = [index + 1 for index, line in enumerate(lines) if token in line]
    return hits


def summarize_anchor(anchor: Anchor) -> dict[str, object]:
    path = SOURCE_ROOT / anchor.file
    if not path.is_file():
        return {
            "key": anchor.key,
            "status": "FAIL",
            "file": relative(path),
            "summary": f"Missing source file {anchor.file}.",
            "tokens": list(anchor.tokens),
            "lineHits": {},
        }
    hits = line_hits(path, anchor.tokens)
    missing = [token for token, lines in hits.items() if not lines]
    return {
        "key": anchor.key,
        "status": "PASS" if not missing else "FAIL",
        "file": relative(path),
        "summary": anchor.summary,
        "tokens": list(anchor.tokens),
        "lineHits": hits,
        "missingTokens": missing,
    }


def summarize_doc_check(doc_path: str, tokens: tuple[str, ...], summary: str) -> dict[str, object]:
    path = ROOT / doc_path
    if not path.is_file():
        return {
            "key": doc_path,
            "status": "FAIL",
            "file": doc_path,
            "summary": f"Missing documentation file {doc_path}.",
            "tokens": list(tokens),
            "lineHits": {},
        }
    hits = line_hits(path, tokens)
    missing = [token for token, lines in hits.items() if not lines]
    return {
        "key": doc_path,
        "status": "PASS" if not missing else "FAIL",
        "file": doc_path,
        "summary": summary,
        "tokens": list(tokens),
        "lineHits": hits,
        "missingTokens": missing,
    }


def build_report() -> dict[str, object]:
    source_results = [summarize_anchor(anchor) for anchor in ANCHORS]
    doc_results = [summarize_doc_check(*item) for item in DOC_CHECKS]
    failures = [item for item in source_results + doc_results if item["status"] != "PASS"]
    return {
        "schema": "battleengine-logic-coverage.v1",
        "status": "pass" if not failures else "blocked",
        "sourceRoot": "references/Onslaught",
        "sourceAnchorsChecked": len(source_results),
        "docAnchorsChecked": len(doc_results),
        "sourceAnchorsPassed": sum(1 for item in source_results if item["status"] == "PASS"),
        "docAnchorsPassed": sum(1 for item in doc_results if item["status"] == "PASS"),
        "sourceResults": source_results,
        "docResults": doc_results,
        "privacy": "Report stores repo-relative source/doc filenames, token names, and line numbers only; no source excerpts, private assets, runtime paths, or binaries.",
        "notProven": [
            "Steam retail binary function identity for these source anchors",
            "Ghidra rename-map mutation or read-back",
            "Runtime gameplay-state interpretation",
            "Continuous frame streaming",
            "Rebuildable open-source gameplay implementation",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public-safe BattleEngine source logic coverage anchors.")
    parser.add_argument("--check", action="store_true", help="run the coverage probe")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")
    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}")
        return 1
    report = build_report()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine logic coverage probe")
        print(f"Status: {report['status']}")
        print(f"Source anchors: {report['sourceAnchorsPassed']}/{report['sourceAnchorsChecked']}")
        print(f"Doc anchors: {report['docAnchorsPassed']}/{report['docAnchorsChecked']}")
        for item in report["sourceResults"]:
            print(f"- {item['status']}: {item['key']}: {item['file']}")
        for item in report["docResults"]:
            print(f"- {item['status']}: doc: {item['file']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
