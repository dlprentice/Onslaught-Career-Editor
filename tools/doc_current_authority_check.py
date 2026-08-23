#!/usr/bin/env python3
"""Reject volatile authority restatements in living documentation owners.

The exact campaign generation, READY/reducer pins, and next-valid generation are
owned by developer_state.json -> current_re_authority. The rolling Ghidra state,
including population/body counts and live selectors, is owned by
reverse-engineering/ghidra/README.md plus fresh inspection. Living front doors
must point to those owners rather than copy values that immediately age. Dated
findings and explicitly historical tables may keep exact values, but must label
them as dated/frozen instead of promoting them back to current state.
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
    (
        "EXPLICIT_CURRENT_POPULATION",
        re.compile(
            r"(?is)\bcurrent\s+(?:saved\s+|tracked\s+|live\s+|discovered\s+){0,2}"
            r"\d[\d,]*(?:-(?:row|entry)|\s+(?:functions?|rows?|entries?))\b"
        ),
    ),
    (
        "CURRENT_COUNT_TABLE",
        re.compile(
            r"(?im)^[ \t]*\|\s*[^|\r\n]+\|\s*current\s+count\s*\|[^\r\n]*\|[ \t]*$"
        ),
    ),
    (
        "EXPLICIT_CURRENT_ACCOUNTING",
        re.compile(
            r"(?is)\bcurrent\s+(?:saved-body\s+)?(?:`?\.text`?\s+)?"
            r"(?:body\s+|function\s+)?(?:ownership|coverage|population|census|accounting)\b"
            r".{0,180}?\b\d[\d,]*(?:\.\d+)?%?\b"
        ),
    ),
    (
        "EXPLICIT_ROLLING_COUNT",
        re.compile(
            r"(?is)\brolling\s+(?:census|state|count|accounting)\b"
            r".{0,120}?\b(?:db\.)?\d[\d,]*\b"
        ),
    ),
    (
        "STALE_LIVE_SELECTOR",
        re.compile(
            r"(?im)^(?:[ \t]*[|>*-][ \t]*)*(?:latest\s+live\s+readback|"
            r"current\s+tracked\s+name\s+projection|current\s+live\s+Ghidra\s+readback)\b"
        ),
    ),
    (
        "SOLE_NAMED_CAMPAIGN_PARENT",
        re.compile(
            r"(?is)\bsole\s+campaign\s+parent\s*\([^\n)]*\bgeneration-\d+[^\n)]*\)"
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
        "current function count fails": ("Drive every one of the current 8,329 functions.\n", 1),
        "current row count fails": ("Current 8,329-row internal-function metadata.\n", 1),
        "rolling census fails": ("The rolling census is now 8,329.\n", 1),
        "rolling state fails": ("The rolling state advances to 8,329/db.18618.\n", 1),
        "contextual current-count table fails": (
            "The current layers must remain separate:\n\n"
            "| Population | Current count | Meaning |\n"
            "| --- | ---: | --- |\n"
            "| Saved Ghidra function entries | 8,329 | Exact 2026-08-14 live/tracked readback |\n"
            "| Reviewed 79-row structural cohort still outside Ghidra | 0 | Completed admission |\n"
            "| Defensible saved census/lower bound | **8,329** | Not a final ceiling |\n",
            1,
        ),
        "frozen historical count table passes": (
            "This is a frozen 2026-08-14 historical snapshot, not current authority:\n\n"
            "| Population | Frozen 2026-08-14 count | Historical meaning |\n"
            "| --- | ---: | --- |\n"
            "| Saved Ghidra function entries | 8,329 | Dated readback |\n"
            "| Defensible saved census/lower bound | **8,329** | Historical lower bound |\n",
            0,
        ),
        "current ownership fails": (
            "Current saved-body `.text` ownership is 1,811,691 / 1,929,117 bytes.\n",
            1,
        ),
        "current accounting fails": (
            "The current accounting supersedes it: 8,329 saved functions.\n",
            1,
        ),
        "multiline current ownership fails": (
            "Current `.text` body ownership supersedes the old metric for present use:\n"
            "8,329 saved functions and 8,459 exact ranges own 1,811,691 bytes.\n",
            1,
        ),
        "multiline current accounting fails": (
            "The current accounting supersedes it for present use:\n"
            "8,329 saved functions / 8,459 ranges own 1,811,691 bytes.\n",
            1,
        ),
        "latest readback selector fails": (
            "| Latest live readback | local-lab/example/functions.tsv |\n",
            1,
        ),
        "tracked projection selector fails": (
            "| Current tracked name projection | dated-table.tsv |\n",
            1,
        ),
        "live Ghidra selector fails": (
            "| Current live Ghidra readback | local-lab/example/functions.tsv |\n",
            1,
        ),
        "named sole parent fails": (
            "The sole campaign parent (`generation-31-current-8329-db18624-v2`) is pinned.\n",
            1,
        ),
        "dated population passes": (
            "The dated 2026-08-14 readback contained 8,329 functions.\n",
            0,
        ),
        "frozen accounting passes": (
            "Frozen 2026-08-14 body accounting was 1,811,691 bytes.\n",
            0,
        ),
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
