#!/usr/bin/env python3
"""Validate a public-safe name-table triage for weapon-fired stealth reset.

This probe checks the Stuart source anchor and the current ignored Ghidra
function-name export. The result is intentionally bounded: the current function
name table has no named WeaponFired/Stealth/Cloak candidate, but that is not a
proof that no retail implementation exists.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FUNCTIONS = ROOT / "subagents" / "battleengine-function-name-scan" / "current" / "functions_all.tsv"
DEFAULT_OUT = ROOT / "subagents" / "battleengine-function-name-scan" / "current" / "weapon-stealth-name-scan.json"
SOURCE_FILE = ROOT / "references" / "Onslaught" / "BattleEngine.cpp"
SOURCE_NOTE = ROOT / "release" / "readiness" / "battleengine_weapon_stealth_source_anchor_2026-05-07.md"
STRICT_NAME_RE = re.compile(r"(WeaponFired|Stealth|Cloak|Decloak|Cloaked)", re.IGNORECASE)

SOURCE_TOKENS = (
    "BOOL CBattleEngine::WeaponFired(",
    "mJetPart->WeaponFired(inWeapon)",
    "mWalkerPart->WeaponFired(inWeapon)",
    "mStealth=0.0f;",
)

SOURCE_NOTE_TOKENS = (
    "weapon_fire_breaks_stealth",
    "source-only pending retail-binary identity",
    "strict WeaponFired/Stealth/Cloak/Decloak",
    "not retail Steam binary identity proof",
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def token_hits(path: Path, tokens: tuple[str, ...]) -> dict[str, list[int]]:
    if not path.is_file():
        return {token: [] for token in tokens}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def read_function_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            rows.append(
                {
                    "address": row.get("address", ""),
                    "name": row.get("name", ""),
                    "signature": row.get("signature", ""),
                }
            )
    return rows


def build_report(functions_path: Path) -> dict[str, object]:
    source_hits = token_hits(SOURCE_FILE, SOURCE_TOKENS)
    source_note_hits = token_hits(SOURCE_NOTE, SOURCE_NOTE_TOKENS)
    source_missing = [token for token, hits in source_hits.items() if not hits]
    source_note_missing = [token for token, hits in source_note_hits.items() if not hits]
    rows = read_function_rows(functions_path)
    strict_matches = [
        row
        for row in rows
        if STRICT_NAME_RE.search(row["name"]) or STRICT_NAME_RE.search(row["signature"])
    ]
    failures: list[str] = []
    if not functions_path.is_file():
        failures.append(f"missing Ghidra function-name export: {relative(functions_path)}")
    failures.extend(f"missing source token: {token}" for token in source_missing)
    failures.extend(f"missing source-note token: {token}" for token in source_note_missing)
    if strict_matches:
        failures.append("strict WeaponFired/Stealth/Cloak function-name matches exist; update the public evidence before keeping this negative triage claim")

    return {
        "schema": "battleengine-weapon-stealth-name-scan.v1",
        "status": "pass" if not failures else "blocked",
        "sourceFile": relative(SOURCE_FILE),
        "sourceNote": relative(SOURCE_NOTE),
        "functionNameExport": relative(functions_path),
        "functionRowsChecked": len(rows),
        "strictNamePattern": STRICT_NAME_RE.pattern,
        "strictNameMatches": strict_matches,
        "sourceTokenLineHits": source_hits,
        "sourceNoteTokenLineHits": source_note_hits,
        "failures": failures,
        "whatIsProven": [
            "The source WeaponFired anchor still clears stealth for both jet and walker fired-weapon paths.",
            "The current public source-anchor note still classifies this as source-only pending retail-binary identity.",
            "The current ignored all-functions Ghidra name export contains no strict WeaponFired/Stealth/Cloak/Decloak named candidate.",
        ],
        "notProven": [
            "Absence of a retail implementation.",
            "Exact Steam retail function body for weapon-fired stealth reset.",
            "Candidate decompile identity.",
            "Ghidra rename-map mutation or read-back.",
            "Runtime firing or stealth behavior.",
        ],
        "privacy": "Report stores repo-relative filenames, token names, line numbers, function names/signatures from ignored Ghidra export, and counts only; no binaries, private paths, source excerpts, runtime captures, or Ghidra mutation logs.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public-safe weapon-fired stealth name-scan evidence.")
    parser.add_argument("--check", action="store_true", help="run the name-scan probe")
    parser.add_argument("--functions", type=Path, default=DEFAULT_FUNCTIONS, help="ignored all-functions TSV from ExportWeakFunctionList.java mode=all")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    functions_path = args.functions if args.functions.is_absolute() else ROOT / args.functions
    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}")
        return 1

    report = build_report(functions_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine weapon-fired stealth name-scan probe")
        print(f"Status: {report['status']}")
        print(f"Function rows checked: {report['functionRowsChecked']}")
        print(f"Strict name matches: {len(report['strictNameMatches'])}")
        if report["failures"]:
            for failure in report["failures"]:
                print(f"- FAIL: {failure}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
