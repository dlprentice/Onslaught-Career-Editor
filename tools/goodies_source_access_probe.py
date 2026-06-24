#!/usr/bin/env python3
"""Validate source-level Goodies access paths.

This probe reads Stuart's source tree only. It does not launch the game, read or
write BEA.exe, mutate Ghidra, or touch save files. Source is architecture/name
evidence; retail binary and runtime proof remain authoritative for shipping
behavior.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "references" / "Onslaught"
DEFAULT_OUT = (
    ROOT / "subagents" / "goodies-source-access" / "current" / "goodies-source-access.json"
)

SOURCE_FILES = [
    SOURCE_ROOT / "Career.cpp",
    SOURCE_ROOT / "Career.h",
    SOURCE_ROOT / "FEPGoodies.cpp",
    SOURCE_ROOT / "game.cpp",
]


@dataclass(frozen=True)
class SourceHit:
    file: Path
    line: int
    text: str

    def to_json(self) -> dict[str, object]:
        return {
            "file": relative(self.file),
            "line": self.line,
            "text": self.text,
        }


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def find_line_hits(path: Path, pattern: re.Pattern[str]) -> list[SourceHit]:
    hits: list[SourceHit] = []
    for line_number, line in enumerate(read_text(path).splitlines(), start=1):
        if pattern.search(line):
            hits.append(SourceHit(path, line_number, line.strip()))
    return hits


def source_hit_summary(hits: list[SourceHit]) -> list[dict[str, object]]:
    return [hit.to_json() for hit in hits]


def build_report(source_root: Path) -> dict[str, object]:
    failures: list[str] = []
    for source_file in SOURCE_FILES:
        if not source_file.is_file():
            failures.append(f"missing source file: {relative(source_file)}")

    fep = source_root / "FEPGoodies.cpp"
    career = source_root / "Career.cpp"
    career_h = source_root / "Career.h"
    game = source_root / "game.cpp"

    set_state_lines = (
        find_line_hits(fep, re.compile(r"\bCAREER\.SetGoodieState\s*\("))
        + find_line_hits(game, re.compile(r"\bCAREER\.SetGoodieState\s*\("))
    )
    get_state_lines = (
        find_line_hits(fep, re.compile(r"\bCAREER\.GetGoodieState\s*\("))
        + find_line_hits(game, re.compile(r"\bCAREER\.GetGoodieState\s*\("))
    )
    coordinate_lines = find_line_hits(fep, re.compile(r"\bget_goodie_number\s*\("))
    inline_api_lines = (
        find_line_hits(career_h, re.compile(r"\bGetGoodieState\s*\("))
        + find_line_hits(career_h, re.compile(r"\bSetGoodieState\s*\("))
    )

    direct_71_73_api_lines: list[SourceHit] = []
    direct_71_73_patterns = [
        re.compile(r"\bCAREER\.SetGoodieState\s*\(\s*(71|72|73)\b"),
        re.compile(r"\bCAREER\.GetGoodieState\s*\(\s*(71|72|73)\b"),
        re.compile(r"\bmGoodies\s*\[\s*(71|72|73)\s*\]"),
    ]
    for source_file in SOURCE_FILES:
        for pattern in direct_71_73_patterns:
            direct_71_73_api_lines.extend(find_line_hits(source_file, pattern))

    career_tokens = {
        "SET_GOODIE_NEW(71)": "SET_GOODIE_NEW(71)" in read_text(career),
        "SET_GOODIE_NEW(72)": "SET_GOODIE_NEW(72)" in read_text(career),
        "SET_GOODIE_NEW(73)": "SET_GOODIE_NEW(73)" in read_text(career),
        "SET_GOODIE_INSTRUCTION(71)": "SET_GOODIE_INSTRUCTION(71)" in read_text(career),
        "SET_GOODIE_INSTRUCTION(72)": "SET_GOODIE_INSTRUCTION(72)" in read_text(career),
        "SET_GOODIE_INSTRUCTION(73)": "SET_GOODIE_INSTRUCTION(73)" in read_text(career),
    }

    mapping_returns = {
        "return(71)": "return(71)" in read_text(fep),
        "return(72)": "return(72)" in read_text(fep),
        "return(73)": "return(73)" in read_text(fep),
    }

    if len(set_state_lines) != 3:
        failures.append(f"unexpected CAREER.SetGoodieState source line count: {len(set_state_lines)}")
    if len(get_state_lines) != 3:
        failures.append(f"unexpected CAREER.GetGoodieState source line count: {len(get_state_lines)}")
    if direct_71_73_api_lines:
        failures.append("direct source API access to Goodies 71-73 was found")
    if not all(career_tokens.values()):
        failures.append("missing Career.cpp 71-73 unlock/instruction token")
    if any(mapping_returns.values()):
        failures.append("get_goodie_number appears to return 71, 72, or 73 directly")

    return {
        "schema": "goodies-source-access.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "sourceRoot": relative(source_root),
        "setGoodieStateLineCount": len(set_state_lines),
        "getGoodieStateLineCount": len(get_state_lines),
        "coordinateMapperLineCount": len(coordinate_lines),
        "inlineApiLines": source_hit_summary(inline_api_lines),
        "setGoodieStateLines": source_hit_summary(set_state_lines),
        "getGoodieStateLines": source_hit_summary(get_state_lines),
        "coordinateMapperLines": source_hit_summary(coordinate_lines),
        "direct71To73ApiLines": source_hit_summary(direct_71_73_api_lines),
        "careerUnlockTokens": career_tokens,
        "coordinateMapperDirectReturns": mapping_returns,
        "currentClaims": [
            "Source-level CAREER.SetGoodieState callers are limited to FEPGoodies coordinate-state wrapping and game FMV unlock paths.",
            "Source-level CAREER.GetGoodieState callers are limited to FEPGoodies coordinate-state wrapping and game FMV unlock checks.",
            "Source-level Goodies 71-73 support is currently represented by Career.cpp unlock/instruction tokens, not by direct Get/Set API calls or get_goodie_number coordinate returns.",
        ],
        "notClaimed": [
            "This probe does not prove Steam retail binary behavior.",
            "This probe does not prove runtime reachability for Goodies 71-73.",
            "This probe does not inspect indirect binary array access or runtime-only paths.",
        ],
        "failures": failures,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if the source access map no longer matches current expectations.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(args.source_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(args.out)}")
    print(
        "source Goodie API lines: "
        f"set={report['setGoodieStateLineCount']} "
        f"get={report['getGoodieStateLineCount']} "
        f"direct71to73={len(report['direct71To73ApiLines'])}"
    )
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
