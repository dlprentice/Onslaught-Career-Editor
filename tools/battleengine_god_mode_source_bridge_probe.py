#!/usr/bin/env python3
"""Public-safe source/binary/runtime-document bridge probe for god mode.

This probe keeps the Steam-build boundary explicit: source ``CPlayer::SetIsGod``
tokens line up with vulnerability/infinite-energy behavior, and existing binary
docs plus runtime notes prove a cheat-gated Steam UI/effect path, but the exact
source-to-retail player toggle implementation remains unresolved.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "subagents" / "battleengine-god-mode-source-bridge" / "current" / "battleengine-god-mode-source-bridge.json"


@dataclass(frozen=True)
class TokenGroup:
    key: str
    file: str
    tokens: tuple[str, ...]
    summary: str


GROUPS: tuple[TokenGroup, ...] = (
    TokenGroup(
        "source_player_toggle",
        "references/Onslaught/Player.cpp",
        (
            "void\tCPlayer::SetIsGod(BOOL val)",
            "mBattleEngine->SetVulnerable(FALSE)",
            "mBattleEngine->SetInfinateEnergy(TRUE)",
            "mBattleEngine->SetVulnerable(TRUE)",
            "mBattleEngine->SetInfinateEnergy(FALSE)",
        ),
        "Source Player.cpp toggles BattleEngine vulnerability and infinite-energy state from CPlayer::SetIsGod.",
    ),
    TokenGroup(
        "steam_runtime_mechanism_note",
        "reverse-engineering/game-mechanics/god-mode.md",
        (
            "Maladim",
            "God OFF",
            "God ON",
            "normal combat damage no longer depleted shields",
            "strong mechanism inference",
            "not yet a direct vfunc-by-vfunc proof",
        ),
        "God-mode docs record Steam-build runtime behavior plus the explicit non-exact-mechanism boundary.",
    ),
    TokenGroup(
        "pause_menu_binary_note",
        "reverse-engineering/binary-analysis/functions/PauseMenu.cpp/PauseMenu__Init.md",
        (
            "IsCheatActive(3)",
            "g_bGodModeEnabled",
            "God OFF",
            "God ON",
            "gameplay retest confirmed",
        ),
        "Pause menu binary note records cheat-gated Steam UI exposure and toggle state use.",
    ),
    TokenGroup(
        "unit_damage_binary_note",
        "reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__ApplyDamage.md",
        (
            "Invincibility check",
            "God mode integration",
            "Player.cpp SetVulnerable() affects this",
            "Does not prove runtime damage",
        ),
        "Unit damage binary note records the damage-handler side of the vulnerability bridge and its boundary.",
    ),
)


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
    path = ROOT / group.file
    if not path.is_file():
        return {
            "key": group.key,
            "status": "FAIL",
            "file": group.file,
            "summary": f"Missing file: {group.file}",
            "tokens": list(group.tokens),
            "lineHits": {},
            "missingTokens": list(group.tokens),
        }
    hits = line_hits(path, group.tokens)
    missing = [token for token, lines in hits.items() if not lines]
    return {
        "key": group.key,
        "status": "PASS" if not missing else "FAIL",
        "file": relative(path),
        "summary": group.summary,
        "tokens": list(group.tokens),
        "lineHits": hits,
        "missingTokens": missing,
    }


def build_report() -> dict[str, object]:
    results = [summarize_group(group) for group in GROUPS]
    failures = [item for item in results if item["status"] != "PASS"]
    return {
        "schema": "battleengine-god-mode-source-bridge.v1",
        "status": "pass" if not failures else "blocked",
        "groupsChecked": len(results),
        "groupsPassed": sum(1 for item in results if item["status"] == "PASS"),
        "results": results,
        "privacy": "Report stores repo-relative source/doc filenames, token labels, and line numbers only; no source excerpts, binaries, private paths, runtime captures, screenshots, or mutation logs.",
        "proves": [
            "Source Player.cpp contains the checked SetIsGod vulnerability/infinite-energy toggles",
            "Steam-build docs record a cheat-gated Maladim UI/effect path",
            "Binary function notes record the pause-menu gating/toggle state and Unit damage-handler vulnerability bridge",
        ],
        "doesNotProve": [
            "Exact source-to-retail identity for CPlayer::SetIsGod",
            "A single direct Steam-build SetIsGod call path",
            "The exact runtime vfunc notification boundary for the toggle",
            "Environmental hazard behavior while god mode is enabled",
            "Ghidra mutation, runtime replay, or rebuildable gameplay parity",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate BattleEngine god-mode source/binary bridge evidence.")
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
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine god-mode source bridge probe")
        print(f"Status: {report['status']}")
        print(f"Groups: {report['groupsPassed']}/{report['groupsChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['key']} ({item['file']})")
            for token in item["missingTokens"]:
                print(f"  missing: {token}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
