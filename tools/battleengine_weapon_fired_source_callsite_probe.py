#!/usr/bin/env python3
"""Validate source-side callsite evidence for BattleEngine WeaponFired.

The source defines CBattleEngine::WeaponFired and part-level WeaponFired helpers,
but current static source scanning shows no direct callsite outside those
definitions/declarations. This does not prove runtime behavior or retail
absence; it explains why a retail source-method identity may be hard to find.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "references" / "Onslaught"
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "battleengine-weapon-fired-stealth-candidate"
    / "current"
    / "source-callsite"
    / "weapon-fired-source-callsite.json"
)

EXPECTED_OCCURRENCES = {
    ("BattleEngine.cpp", 2713, "BOOL CBattleEngine::WeaponFired("),
    ("BattleEngine.cpp", 2716, "if (mJetPart->WeaponFired(inWeapon))"),
    ("BattleEngine.cpp", 2722, "if (mWalkerPart->WeaponFired(inWeapon))"),
    ("BattleEngine.h", 200, "WeaponFired("),
    ("BattleEngineJetPart.cpp", 776, "BOOL\tCBattleEngineJetPart::WeaponFired("),
    ("BattleEngineJetPart.h", 60, "WeaponFired(CWeapon *inWeapon);"),
    ("BattleEngineWalkerPart.cpp", 686, "BOOL\tCBattleEngineWalkerPart::WeaponFired("),
    ("BattleEngineWalkerPart.h", 62, "WeaponFired("),
}


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def iter_source_files() -> list[Path]:
    return sorted(
        path
        for path in SOURCE_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".cpp", ".h", ".hpp", ".inl"}
    )


def normalize_line(line: str) -> str:
    return " ".join(line.strip().split())


def find_occurrences() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in iter_source_files():
        rel = path.relative_to(SOURCE_ROOT).as_posix()
        for index, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if "WeaponFired" not in line:
                continue
            rows.append(
                {
                    "file": rel,
                    "line": index,
                    "text": normalize_line(line),
                }
            )
    return rows


def is_expected(row: dict[str, object]) -> bool:
    file = str(row["file"])
    line = int(row["line"])
    text = str(row["text"])
    for exp_file, exp_line, exp_text in EXPECTED_OCCURRENCES:
        if file == exp_file and line == exp_line and normalize_line(exp_text) in text:
            return True
    return False


def build_report() -> dict[str, object]:
    occurrences = find_occurrences()
    unexpected = [row for row in occurrences if not is_expected(row)]
    missing_expected = []
    occurrence_keys = {(str(row["file"]), int(row["line"])) for row in occurrences}
    for exp_file, exp_line, exp_text in sorted(EXPECTED_OCCURRENCES):
        if (exp_file, exp_line) not in occurrence_keys:
            missing_expected.append({"file": exp_file, "line": exp_line, "expected": normalize_line(exp_text)})

    failures: list[str] = []
    if unexpected:
        failures.append("unexpected WeaponFired source occurrences exist; update callsite evidence")
    if missing_expected:
        failures.append("expected WeaponFired source occurrences are missing")

    return {
        "schema": "battleengine-weapon-fired-source-callsite.v1",
        "status": "pass" if not failures else "blocked",
        "sourceRoot": relative(SOURCE_ROOT),
        "occurrences": occurrences,
        "occurrenceCount": len(occurrences),
        "unexpectedOccurrences": unexpected,
        "missingExpected": missing_expected,
        "failures": failures,
        "whatIsProven": [
            "The checked Stuart source tree contains only the expected WeaponFired declarations/definitions and the two part-delegation calls inside CBattleEngine::WeaponFired itself.",
            "No direct source callsite outside those expected occurrences is currently present.",
        ],
        "notProven": [
            "Steam retail absence of weapon-fired stealth reset behavior.",
            "Exact Steam retail function body identity for CBattleEngine::WeaponFired.",
            "Whether retail removed, inlined, reorganized, or changed this source behavior.",
            "Runtime stealth behavior after firing a weapon.",
            "Ghidra mutation, rename-map apply, or read-back.",
        ],
        "privacy": "Report stores repo-relative source filenames, line numbers, normalized source lines, and proof boundaries only; no binaries, private paths, runtime captures, screenshots, or mutation logs.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BattleEngine WeaponFired source callsite evidence.")
    parser.add_argument("--check", action="store_true", help="run the source callsite probe")
    parser.add_argument("--json", action="store_true", help="print the full JSON report")
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
        print("BattleEngine WeaponFired source callsite probe")
        print(f"Status: {report['status']}")
        print(f"Occurrences: {report['occurrenceCount']}")
        print(f"Unexpected occurrences: {len(report['unexpectedOccurrences'])}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
