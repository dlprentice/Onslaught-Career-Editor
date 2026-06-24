#!/usr/bin/env python3
"""Validate bounded transform special-move lockout candidate evidence.

This probe checks source ``CBattleEngine::Morph()`` special-move rejection
tokens against a fresh read-only decompile of the retail transition helper.
The evidence is deliberately bounded: early retail transition lockout gates
look source-compatible, but exact jet/walker special-move method identity and
runtime behavior remain unproven.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references" / "Onslaught" / "BattleEngine.cpp"
DEFAULT_DECOMPILE = ROOT / "subagents" / "battleengine-transform-special-move-candidate" / "current" / "decompile"
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "battleengine-transform-special-move-candidate"
    / "current"
    / "transform-special-move-candidate.json"
)

SOURCE_TOKENS = (
    "void CBattleEngine::Morph()",
    "if (mJetPart->GetIsDoingSpecialAirMove() == TRUE) return ;",
    "if (mWalkerPart->GetIsDoingSpecialWalkerMove() == TRUE) return ;",
    "if (mState == BATTLE_ENGINE_STATE_MORPHING_INTO_JET) return ;",
    "if (mState == BATTLE_ENGINE_STATE_MORPHING_INTO_WALKER) return ;",
)

RETAIL_TOKENS = (
    "CGeneralVolume__IsStateMachineActive",
    "CGeneralVolume__IsDashLockoutActive",
    "CGeneralVolume__BeginFlyToWalkTransition",
    "CGeneralVolume__BeginWalkToFlyTransition",
    "s_flytowalk_006234bc",
    "s_walktofly_006234b0",
    "*(int *)((int)param_1 + 0x260) != 1",
    "*(int *)((int)param_1 + 0x260) != 0",
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalized(text: str) -> str:
    return "".join(text.split())


def token_hits(path: Path, tokens: tuple[str, ...], *, normalize: bool = False) -> dict[str, list[int]]:
    if not path.is_file():
        return {token: [] for token in tokens}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    hits: dict[str, list[int]] = {}
    if normalize:
        norm_lines = [normalized(line) for line in lines]
        for token in tokens:
            needle = normalized(token)
            hits[token] = [index + 1 for index, line in enumerate(norm_lines) if needle in line]
    else:
        for token in tokens:
            hits[token] = [index + 1 for index, line in enumerate(lines) if token in line]
    return hits


def read_index(decompile_dir: Path) -> list[dict[str, str]]:
    index = decompile_dir / "index.tsv"
    if not index.is_file():
        return []
    with index.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def first_hit(hits: dict[str, list[int]], token: str) -> int | None:
    lines = hits.get(token, [])
    return lines[0] if lines else None


def build_report(decompile_dir: Path) -> dict[str, object]:
    transition = decompile_dir / "0040a580_CMonitor__UpdateFlightWalkerTransitionState.c"
    index_rows = read_index(decompile_dir)
    source_hits = token_hits(SOURCE, SOURCE_TOKENS, normalize=True)
    retail_hits = token_hits(transition, RETAIL_TOKENS, normalize=True)

    failures: list[str] = []
    if not SOURCE.is_file():
        failures.append(f"missing source file: {relative(SOURCE)}")
    if not transition.is_file():
        failures.append(f"missing decompile file: {relative(transition)}")
    if not index_rows:
        failures.append(f"missing or empty decompile index: {relative(decompile_dir / 'index.tsv')}")
    else:
        matching_rows = [
            row
            for row in index_rows
            if row.get("address", "").lower() == "0x0040a580"
            and row.get("name") == "CMonitor__UpdateFlightWalkerTransitionState"
            and row.get("status") == "OK"
        ]
        if not matching_rows:
            failures.append("decompile index lacks OK row for 0x0040a580 CMonitor__UpdateFlightWalkerTransitionState")

    failures.extend(f"missing source token: {token}" for token, lines in source_hits.items() if not lines)
    failures.extend(f"missing retail token: {token}" for token, lines in retail_hits.items() if not lines)

    state_machine_line = first_hit(retail_hits, "CGeneralVolume__IsStateMachineActive")
    dash_lockout_line = first_hit(retail_hits, "CGeneralVolume__IsDashLockoutActive")
    fly_to_walk_line = first_hit(retail_hits, "CGeneralVolume__BeginFlyToWalkTransition")
    walk_to_fly_line = first_hit(retail_hits, "CGeneralVolume__BeginWalkToFlyTransition")
    if state_machine_line and fly_to_walk_line and state_machine_line >= fly_to_walk_line:
        failures.append("state-machine lockout check does not precede fly-to-walk transition")
    if state_machine_line and walk_to_fly_line and state_machine_line >= walk_to_fly_line:
        failures.append("state-machine lockout check does not precede walk-to-fly transition")
    if dash_lockout_line and fly_to_walk_line and dash_lockout_line >= fly_to_walk_line:
        failures.append("dash-lockout check does not precede fly-to-walk transition")
    if dash_lockout_line and walk_to_fly_line and dash_lockout_line >= walk_to_fly_line:
        failures.append("dash-lockout check does not precede walk-to-fly transition")

    return {
        "schema": "battleengine-transform-special-move-candidate.v1",
        "status": "pass" if not failures else "blocked",
        "sourceFile": relative(SOURCE),
        "decompileDir": relative(decompile_dir),
        "sourceTokenLineHits": source_hits,
        "retailTokenLineHits": retail_hits,
        "lineOrder": {
            "stateMachineLockout": state_machine_line,
            "dashLockout": dash_lockout_line,
            "flyToWalkTransition": fly_to_walk_line,
            "walkToFlyTransition": walk_to_fly_line,
        },
        "failures": failures,
        "whatIsProven": [
            "Source CBattleEngine::Morph() still rejects morphing during jet and walker special-move paths.",
            "Fresh read-only CMonitor__UpdateFlightWalkerTransitionState decompile contains early state-machine and dash-lockout gates before both transition branches.",
            "The same helper still contains fly-to-walk and walk-to-fly transition calls plus transition animation strings.",
        ],
        "notProven": [
            "Exact source-to-retail identity for GetIsDoingSpecialAirMove or GetIsDoingSpecialWalkerMove.",
            "Exact full CBattleEngine::Morph() body identity.",
            "Runtime transform rejection during special moves.",
            "Ghidra rename-map mutation.",
            "Rebuildable open-source gameplay implementation.",
        ],
        "privacy": "Report stores repo-relative paths, token names, public addresses, and line numbers only; raw decompile output remains ignored under subagents/.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BattleEngine transform special-move lockout candidate evidence.")
    parser.add_argument("--check", action="store_true", help="run the candidate probe")
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE, help="ignored Ghidra decompile export dir")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    decompile_dir = args.decompile_dir if args.decompile_dir.is_absolute() else ROOT / args.decompile_dir
    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}")
        return 1

    report = build_report(decompile_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine transform special-move candidate probe")
        print(f"Status: {report['status']}")
        print(f"Source tokens: {sum(1 for lines in report['sourceTokenLineHits'].values() if lines)}/{len(SOURCE_TOKENS)}")
        print(f"Retail tokens: {sum(1 for lines in report['retailTokenLineHits'].values() if lines)}/{len(RETAIL_TOKENS)}")
        if report["failures"]:
            for failure in report["failures"]:
                print(f"- FAIL: {failure}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
