#!/usr/bin/env python3
"""Reject volatile authority restatements in living documentation owners.

The exact campaign generation, READY/reducer pins, and next-valid generation are
owned by developer_state.json -> current_re_authority. The rolling Ghidra state
is owned by reverse-engineering/ghidra/README.md plus fresh inspection. Living
front doors must point to those owners rather than copy values that immediately
age. Dated findings and explicitly historical tables are outside this gate.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    Path("GOAL.md"),
    Path("CURRENT_CAPABILITIES.md"),
    Path("DOCUMENTATION.md"),
    Path("reverse-engineering/RE-INDEX.md"),
    Path("reverse-engineering/ghidra-functions.md"),
    Path("reverse-engineering/parity-lab.md"),
    Path("reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md"),
)

RULES = (
    (
        "EXPLICIT_CURRENT_GENERATION",
        re.compile(
            r"(?is)\b(?:current|canonical|sole)\s+(?:complete-RE\s+|replay\s+|campaign\s+|semantic\s+)?"
            r"authority\b.{0,120}?\b(?:Generation|Gen)\s*\*{0,2}\d+\b"
        ),
    ),
    (
        "EXPLICIT_CURRENT_GENERATION",
        re.compile(
            r"(?is)\b(?:campaign\s+authority\s+is|use\s+canonical)\s+(?:Generation|Gen)\s*\*{0,2}\d+\b"
        ),
    ),
    (
        "SOLE_NUMBERED_PARENT",
        re.compile(r"(?is)\bGeneration\s+\d+\s+is\s+the\s+sole\s+campaign\s+parent\b"),
    ),
    (
        "EXPLICIT_NEXT_GENERATION",
        re.compile(r"(?is)\bnext\s+valid\s+(?:campaign\s+)?generation\s+is\s+\*{0,2}\d+\b"),
    ),
    (
        "EXPLICIT_CURRENT_GHIDRA_DB",
        re.compile(
            r"(?is)\b(?:current|latest)\s+(?:live\s+|tracked\s+|saved\s+|Ghidra\s+|project\s+){0,2}"
            r"[^.\n]{0,100}?\bdb\.\d+\b"
        ),
    ),
)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def scan_text(text: str) -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    seen: set[tuple[str, int, str]] = set()
    for code, pattern in RULES:
        for match in pattern.finditer(text):
            snippet = " ".join(match.group(0).split())[:180]
            row = (code, line_number(text, match.start()), snippet)
            if row not in seen:
                seen.add(row)
                hits.append(row)
    return sorted(hits, key=lambda row: (row[1], row[0], row[2]))


def self_test() -> int:
    cases = {
        "pointer passes": (
            "Current authority: read `developer_state.json` -> `current_re_authority`.\n",
            0,
        ),
        "historical next passes": ("At that freeze the next valid generation was 30.\n", 0),
        "current generation fails": ("Current authority is Generation 32.\n", 1),
        "canonical shorthand fails": ("Use canonical Gen29 for campaign state.\n", 1),
        "next generation fails": ("The next valid campaign generation is 33.\n", 1),
        "current database fails": ("The current tracked Ghidra state is db.18627.\n", 1),
    }
    failed = False
    for name, (text, expected) in cases.items():
        actual = len(scan_text(text))
        ok = (actual == expected) if expected == 0 else (actual >= expected)
        print(f"  [{'ok' if ok else 'FAIL':4}] {name}: hits={actual}")
        failed |= not ok
    print("SELF-TEST PASS" if not failed else "SELF-TEST FAIL")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    violations: list[tuple[Path, str, int, str]] = []
    for relative in TARGETS:
        path = ROOT / relative
        if not path.is_file():
            violations.append((relative, "MISSING_TARGET", 0, "required living document is missing"))
            continue
        text = path.read_text(encoding="utf-8")
        if "current_re_authority" not in text:
            violations.append((relative, "MISSING_AUTHORITY_POINTER", 0, "no current_re_authority pointer"))
        for code, line, snippet in scan_text(text):
            violations.append((relative, code, line, snippet))

    if violations:
        for path, code, line, detail in violations:
            where = f"{path}:{line}" if line else str(path)
            print(f"{where}: {code}: {detail}")
        print(f"FAIL: {len(violations)} volatile authority restatement(s)")
        return 1

    print(f"PASS: {len(TARGETS)} living documents point to dynamic authority owners without volatile restatements")
    return 0


if __name__ == "__main__":
    sys.exit(main())
