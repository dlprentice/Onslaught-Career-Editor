#!/usr/bin/env python3
"""Validate a public-safe bridge between BattleEngine weapon source anchors and helper read-back.

This probe checks source augmented-weapon and weapon-fired stealth anchors,
their public source-anchor evidence notes, existing weapon-helper Ghidra
read-back evidence, and current function notes. The claim is deliberately
bounded: related weapon-helper read-back exists, but exact retail identity for
the source augmented-meter and stealth-reset paths remains unproven.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "battleengine-weapon-source-readback-bridge"
    / "current"
    / "battleengine-weapon-source-readback-bridge.json"
)


@dataclass(frozen=True)
class Check:
    key: str
    file: str
    tokens: tuple[str, ...]
    summary: str


CHECKS: tuple[Check, ...] = (
    Check(
        "source_augmented_weapon_anchor",
        "references/Onslaught/BattleEngine.cpp",
        (
            "#define MAX_AUG_VALUE",
            "#define AUG_DECREASE_RATE",
            "mAugValue-=AUG_DECREASE_RATE",
            "mAugValue+=shieldDamage",
            "void CBattleEngine::AugmentWeapon()",
            "void CBattleEngine::UnaugmentWeapon()",
        ),
        "Stuart source augmented-weapon path records meter constants, shield-damage gain, active decay, augment, and reset anchors.",
    ),
    Check(
        "source_weapon_stealth_anchor",
        "references/Onslaught/BattleEngine.cpp",
        (
            "BOOL CBattleEngine::WeaponFired(",
            "if (mJetPart->WeaponFired(inWeapon))",
            "if (mWalkerPart->WeaponFired(inWeapon))",
            "mStealth=0.0f;",
        ),
        "Stuart source weapon-fired path clears stealth after either jet or walker weapon fire reports success.",
    ),
    Check(
        "augmented_source_anchor_evidence",
        "release/readiness/battleengine_augmented_weapon_source_anchor_2026-05-07.md",
        (
            "augmented_weapon_charge_decay_and_reset",
            "source-only pending retail-binary identity",
            "This is not Ghidra mutation or read-back.",
        ),
        "Public source-anchor evidence records augmented-weapon behavior as source-only pending retail-binary identity.",
    ),
    Check(
        "weapon_stealth_source_anchor_evidence",
        "release/readiness/battleengine_weapon_stealth_source_anchor_2026-05-07.md",
        (
            "weapon_fire_breaks_stealth",
            "source-only pending retail-binary identity",
            "This is not Ghidra mutation or read-back.",
        ),
        "Public source-anchor evidence records weapon-fired stealth reset as source-only pending retail-binary identity.",
    ),
    Check(
        "weapon_helper_readback_evidence",
        "release/readiness/battleengine_weapon_helper_ghidra_readback_2026-05-07.md",
        (
            "`CBattleEngine__UpdateWeaponEffect`",
            "`CBattleEngine__AddProjectile`",
            "weapon-effect and projectile helper functions",
            "stealth, augmented-weapon behavior",
        ),
        "Existing weapon-helper read-back evidence covers current helper functions while explicitly leaving stealth and augmented behavior unproven.",
    ),
    Check(
        "update_weapon_effect_function_note",
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__UpdateWeaponEffect.md",
        (
            "Weapon-source bridge boundary",
            "augmented meter",
            "stealth reset",
            "does not prove exact source-to-retail identity",
        ),
        "Function note keeps the weapon-source bridge boundary visible for the weapon-effect helper.",
    ),
    Check(
        "add_projectile_function_note",
        "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__AddProjectile.md",
        (
            "Weapon-source bridge boundary",
            "augmented meter",
            "stealth reset",
            "does not prove exact source-to-retail identity",
        ),
        "Function note keeps the weapon-source bridge boundary visible for the projectile helper.",
    ),
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def line_hits(path: Path, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def summarize(check: Check) -> dict[str, object]:
    path = ROOT / check.file
    if not path.is_file():
        return {
            "key": check.key,
            "status": "FAIL",
            "file": check.file,
            "summary": f"Missing file: {check.file}",
            "tokenLineHits": {},
            "missingTokens": list(check.tokens),
        }

    hits = line_hits(path, check.tokens)
    missing = [token for token, token_hits in hits.items() if not token_hits]
    return {
        "key": check.key,
        "status": "PASS" if not missing else "FAIL",
        "file": relative(path),
        "summary": check.summary,
        "tokenLineHits": hits,
        "missingTokens": missing,
    }


def build_report() -> dict[str, object]:
    results = [summarize(check) for check in CHECKS]
    failures = [result for result in results if result["status"] != "PASS"]
    return {
        "schema": "battleengine-weapon-source-readback-bridge.v1",
        "status": "pass" if not failures else "blocked",
        "checksPassed": len(results) - len(failures),
        "checksTotal": len(results),
        "results": results,
        "privacy": "Report stores repo-relative filenames, token names, and line numbers only; no source excerpts, binaries, private paths, runtime captures, screenshots, or Ghidra mutation logs.",
        "whatIsProven": [
            "Selected Stuart source augmented-weapon and weapon-fired stealth anchors are present.",
            "Public source-anchor evidence records both source anchors as pending retail-binary identity.",
            "Existing retail weapon-helper read-back evidence records current weapon-effect and projectile helper tokens.",
            "The current function notes document related weapon-helper evidence without claiming augmented-meter or stealth-reset identity.",
        ],
        "notProven": [
            "Exact augmented-meter control-flow identity in Steam retail.",
            "Exact weapon-fired stealth reset control-flow identity in Steam retail.",
            "Runtime weapon firing, projectile behavior, augmented-weapon behavior, or stealth behavior.",
            "Ghidra rename-map mutation or read-back.",
            "Rebuildable open-source gameplay implementation.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public-safe BattleEngine weapon source/read-back bridge.")
    parser.add_argument("--check", action="store_true", help="run the bridge probe")
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
        print("BattleEngine weapon source/read-back bridge probe")
        print(f"Status: {report['status']}")
        print(f"Checks: {report['checksPassed']}/{report['checksTotal']}")
        for result in report["results"]:
            print(f"- {result['status']}: {result['key']}: {result['file']}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
