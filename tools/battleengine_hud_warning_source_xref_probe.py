#!/usr/bin/env python3
"""Validate a public-safe source-to-retail string-xref bridge for HUD warning samples.

This probe connects Stuart source HUD warning sample anchors to already recorded
retail string-xref evidence and the current CMonitor process function note. It
does not launch the game, read or mutate BEA.exe, mutate Ghidra, or export source
snippets. Output stays under subagents/ and records repo-relative filenames,
token names, line numbers, and pass/fail state only.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "subagents" / "battleengine-hud-warning-source-xrefs" / "current" / "battleengine-hud-warning-source-xrefs.json"


@dataclass(frozen=True)
class Check:
    key: str
    file: str
    tokens: tuple[str, ...]
    summary: str


CHECKS: tuple[Check, ...] = (
    Check(
        "source_low_armour_hud_sample",
        "references/Onslaught/BattleEngine.cpp",
        (
            "mLife <= low_life",
            "mLowArmourStartTime",
            'PlayHudSample("hud_armour_low")',
            "15.0f",
        ),
        "Stuart source gates the low-armour HUD warning sample with threshold and repeat-timer state.",
    ),
    Check(
        "source_low_energy_hud_sample",
        "references/Onslaught/BattleEngine.cpp",
        (
            "mConfiguration->mEnergy / 4.0f",
            "mEnergy <= low_energy",
            "mLowEnergyStartTime",
            'PlayHudSample("hud_energy_low")',
            "15.0f",
        ),
        "Stuart source gates the low-energy HUD warning sample with energy threshold and repeat-timer state.",
    ),
    Check(
        "retail_string_xref_report",
        "release/readiness/battleengine_transform_string_xrefs_2026-05-06.md",
        (
            "`hud_armour_low`",
            "`hud_energy_low`",
            "`CMonitor__Process`",
        ),
        "Tracked public-safe string-xref evidence links both HUD warning strings to the current retail monitor process family.",
    ),
    Check(
        "retail_monitor_process_readback_report",
        "release/readiness/transition_hud_helper_ghidra_readback_2026-05-06.md",
        (
            "`CMonitor__Process`",
            "selected HUD-format",
            "HUD/sound/physics helpers",
        ),
        "Fresh transition/HUD helper read-back records the current monitor process body and selected HUD/sound/physics helper tokens.",
    ),
    Check(
        "monitor_process_function_note",
        "reverse-engineering/binary-analysis/functions/monitor.h/CMonitor__Process.md",
        (
            "hud_armour_low",
            "hud_energy_low",
            "s_hud__s_00623314",
            "Does not prove live HUD warning behavior.",
        ),
        "Function note keeps the source/string-xref bridge visible while preserving runtime-proof boundaries.",
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
        "schema": "battleengine-hud-warning-source-xrefs.v1",
        "status": "pass" if not failures else "blocked",
        "checksPassed": len(results) - len(failures),
        "checksTotal": len(results),
        "results": results,
        "privacy": "Report stores repo-relative filenames, token names, and line numbers only; no source excerpts, binaries, private paths, runtime captures, screenshots, or Ghidra mutation logs.",
        "whatIsProven": [
            "Stuart source contains low-armour and low-energy HUD warning sample anchors.",
            "Tracked retail string-xref evidence links the corresponding HUD strings to the current CMonitor process family.",
            "The current CMonitor process function note records this bridge while keeping runtime behavior unclaimed.",
        ],
        "notProven": [
            "Live HUD warning sample playback in a running mission.",
            "Exact source-to-retail control-flow identity for the full BattleEngine process loop.",
            "Runtime gameplay-state interpretation.",
            "Ghidra rename-map mutation or read-back.",
            "Rebuildable open-source gameplay implementation.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public-safe BattleEngine HUD warning source/xref bridge.")
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
        print("BattleEngine HUD warning source/xref bridge probe")
        print(f"Status: {report['status']}")
        print(f"Checks: {report['checksPassed']}/{report['checksTotal']}")
        for result in report["results"]:
            print(f"- {result['status']}: {result['key']}: {result['file']}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
