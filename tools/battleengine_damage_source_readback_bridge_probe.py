#!/usr/bin/env python3
"""Validate a public-safe bridge between BattleEngine damage source anchors and retail damage read-back.

This probe checks that selected Stuart source damage anchors, the existing
source-coverage evidence, the fresh retail `CUnit__ApplyDamage` read-back
evidence, and the current function note all agree on the bounded claim: related
damage-family evidence exists, but exact source-to-retail control-flow identity
and runtime behavior are still unproven.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "subagents" / "battleengine-damage-source-readback-bridge" / "current" / "battleengine-damage-source-readback-bridge.json"


@dataclass(frozen=True)
class Check:
    key: str
    file: str
    tokens: tuple[str, ...]
    summary: str


CHECKS: tuple[Check, ...] = (
    Check(
        "source_damage_core",
        "references/Onslaught/BattleEngine.cpp",
        (
            "PS_DAMAGETAKEN",
            "inAmount*256",
            "mShieldEfficiency/100.0f",
            "mShields-=shieldDamage",
            "mAugValue+=shieldDamage",
        ),
        "Stuart source damage path records fixed-point damage stats and shield-efficiency absorption.",
    ),
    Check(
        "source_damage_restore_and_energy",
        "references/Onslaught/BattleEngine.cpp",
        (
            "mState==BATTLE_ENGINE_STATE_WALKER",
            "mEnergy=mShields",
            "mVulnerable == FALSE",
            "mLife = lastLife",
            "mShields =lastshields",
            "mEnergy = lastenergy",
        ),
        "Stuart source damage path mirrors walker energy from shields and restores state when vulnerability is disabled.",
    ),
    Check(
        "source_coverage_evidence",
        "release/readiness/battleengine_logic_coverage_2026-05-06.md",
        (
            "damage_stat_fixed_point",
            "damage_shield_efficiency",
            "damage_walker_energy_tracks_shields",
            "damage_invulnerability_restore",
        ),
        "Source coverage evidence records the selected damage anchors as source-level mechanics coverage.",
    ),
    Check(
        "retail_damage_readback_evidence",
        "release/readiness/battleengine_mechanics_ghidra_readback_2026-05-06.md",
        (
            "`CUnit__ApplyDamage`",
            "cooldown, destructible-segment, particle-effect, weakpoint, and nexus tokens",
            "does not prove damage",
        ),
        "Fresh retail read-back records selected current decompile tokens for the named `CUnit__ApplyDamage` damage handler.",
    ),
    Check(
        "unit_apply_damage_function_note",
        "reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__ApplyDamage.md",
        (
            "Fresh read-back",
            "damage-family bridge",
            "Does not prove exact `CBattleEngine::Damage` identity.",
        ),
        "Function note keeps the damage-family bridge visible without overclaiming exact identity.",
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
        "schema": "battleengine-damage-source-readback-bridge.v1",
        "status": "pass" if not failures else "blocked",
        "checksPassed": len(results) - len(failures),
        "checksTotal": len(results),
        "results": results,
        "privacy": "Report stores repo-relative filenames, token names, and line numbers only; no source excerpts, binaries, private paths, runtime captures, screenshots, or Ghidra mutation logs.",
        "whatIsProven": [
            "Selected Stuart source damage anchors are present.",
            "Existing source-coverage evidence records the selected damage anchors.",
            "Fresh retail read-back evidence records selected `CUnit__ApplyDamage` damage-handler tokens.",
            "The current function note documents the bridge without claiming exact identity.",
        ],
        "notProven": [
            "Exact `CBattleEngine::Damage` to `CUnit__ApplyDamage` control-flow identity.",
            "Damage, shield, energy, or invulnerability behavior in a running mission.",
            "Runtime gameplay-state interpretation.",
            "Ghidra rename-map mutation or read-back.",
            "Rebuildable open-source gameplay implementation.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public-safe BattleEngine damage source/read-back bridge.")
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
        print("BattleEngine damage source/read-back bridge probe")
        print(f"Status: {report['status']}")
        print(f"Checks: {report['checksPassed']}/{report['checksTotal']}")
        for result in report["results"]:
            print(f"- {result['status']}: {result['key']}: {result['file']}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
