#!/usr/bin/env python3
"""Public-safe read-back probe for the BattleEngine morph event bridge.

This probe compares the source ``CBattleEngine::Morph`` anchors with a fresh
retail decompile of the currently named transition-state helper. It records only
token labels and line numbers. It does not launch the game, read or write
BEA.exe directly, mutate a Ghidra project, or apply a rename map.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "references" / "Onslaught" / "BattleEngine.cpp"
DEFAULT_DECOMPILE_DIR = (
    ROOT / "subagents" / "transition-hud-helper-ghidra-readback" / "current" / "decompile"
)
DEFAULT_OUT = (
    ROOT / "subagents" / "battleengine-morph-event-readback" / "current" / "battleengine-morph-event-readback.json"
)


@dataclass(frozen=True)
class TokenGroup:
    key: str
    file: Path
    tokens: tuple[str, ...]
    summary: str


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def line_hits(path: Path, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def summarize_group(group: TokenGroup) -> dict[str, object]:
    if not group.file.is_file():
        return {
            "key": group.key,
            "status": "FAIL",
            "file": relative(group.file),
            "summary": f"Missing file: {relative(group.file)}",
            "tokens": list(group.tokens),
            "lineHits": {},
            "missingTokens": list(group.tokens),
        }

    hits = line_hits(group.file, group.tokens)
    missing = [token for token, lines in hits.items() if not lines]
    return {
        "key": group.key,
        "status": "PASS" if not missing else "FAIL",
        "file": relative(group.file),
        "summary": group.summary,
        "tokens": list(group.tokens),
        "lineHits": hits,
        "missingTokens": missing,
    }


def build_report(decompile_dir: Path) -> dict[str, object]:
    retail_file = decompile_dir / "0040a580_CMonitor__UpdateFlightWalkerTransitionState.c"
    groups = (
        TokenGroup(
            "source_morph_branch",
            SOURCE_FILE,
            (
                "void CBattleEngine::Morph()",
                "BATTLE_ENGINE_STATE_MORPHING_INTO_WALKER",
                "BATTLE_ENGINE_STATE_MORPHING_INTO_JET",
                "mEnergy>=mConfiguration->mMinTransformEnergy",
                "BECOME_WALKER",
                "BECOME_JET",
                'SetAnimMode("flytowalk"',
                'SetAnimMode("walktofly"',
            ),
            "Source Morph branch names the event IDs, energy gate, morphing states, and transition animation strings.",
        ),
        TokenGroup(
            "retail_transition_event_bridge",
            retail_file,
            (
                "CMonitor__UpdateFlightWalkerTransitionState",
                "CEventManager__AddEvent_AtTime",
                "0x1771",
                "6000",
                "CGeneralVolume__BeginFlyToWalkTransition",
                "CGeneralVolume__BeginWalkToFlyTransition",
                "CBattleEngine__SwapPrimarySecondaryPartReadersForState",
                "s_flytowalk_006234bc",
                "s_walktofly_006234b0",
                "param_1 + 0x260) == 3",
                "param_1 + 0x4b0) + 0x2c",
                "param_1 + 0xfc",
            ),
            "Retail transition helper decompile contains both morph event IDs, transition helpers, animation strings, reader swap, state gate, and energy gate tokens.",
        ),
    )
    results = [summarize_group(group) for group in groups]
    failures = [item for item in results if item["status"] != "PASS"]
    return {
        "schema": "battleengine-morph-event-readback.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if not failures else "blocked",
        "decompileDir": relative(decompile_dir),
        "groupsChecked": len(results),
        "groupsPassed": sum(1 for item in results if item["status"] == "PASS"),
        "results": results,
        "privacy": "Report stores repo-relative source/decompile filenames, token labels, and line numbers only; no source excerpts, decompile excerpts, binaries, runtime captures, private paths, or mutation logs.",
        "proves": [
            "Source CBattleEngine::Morph carries the event, energy-gate, state, and animation-string anchors checked by this probe",
            "Current retail read-back for CMonitor__UpdateFlightWalkerTransitionState carries matching event IDs, transition helpers, animation strings, reader-swap, state-gate, and energy-gate tokens",
            "The retail helper is now a stronger candidate bridge for the source Morph transform branch than string xrefs alone",
        ],
        "doesNotProve": [
            "Complete source-to-retail identity for the full CBattleEngine::Morph body",
            "Correct final owner/name for 0x0040a580",
            "Runtime transform behavior in a running mission",
            "Ghidra rename-map mutation or read-back",
            "Rebuildable open-source gameplay implementation",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate BattleEngine Morph event read-back evidence.")
    parser.add_argument("--check", action="store_true", help="run the read-back probe")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
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
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine Morph event read-back probe")
        print(f"Status: {report['status']}")
        print(f"Groups: {report['groupsPassed']}/{report['groupsChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['key']} ({item['file']})")
            for token in item["missingTokens"]:
                print(f"  missing: {token}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
