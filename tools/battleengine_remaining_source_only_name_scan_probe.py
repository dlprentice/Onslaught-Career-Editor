#!/usr/bin/env python3
"""Validate public-safe direct-name triage for remaining source-only anchors.

This probe guards the current BattleEngine source-to-binary gap boundary. It
checks the ignored Ghidra all-functions name export for direct function-name
matches that would require updating the public evidence before keeping the
remaining anchors in source-only status. A zero-match result is triage only, not
absence proof.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FUNCTIONS = ROOT / "subagents" / "battleengine-function-name-scan" / "current" / "functions_all.tsv"
DEFAULT_OUT = ROOT / "subagents" / "battleengine-function-name-scan" / "current" / "remaining-source-only-name-scan.json"
GAP_PROBE = ROOT / "tools" / "battleengine_source_binary_gap_probe.py"


@dataclass(frozen=True)
class AnchorScan:
    key: str
    strict_name_pattern: str


REMAINING_SOURCE_ONLY_SCANS: tuple[AnchorScan, ...] = (
    AnchorScan(
        "weapon_fire_breaks_stealth",
        r"(WeaponFired|Stealth|Cloak|Decloak|Cloaked)",
    ),
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def import_gap_probe():
    spec = importlib.util.spec_from_file_location("battleengine_source_binary_gap_probe", GAP_PROBE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {GAP_PROBE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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


def scan_anchor(scan: AnchorScan, rows: list[dict[str, str]]) -> dict[str, object]:
    pattern = re.compile(scan.strict_name_pattern, re.IGNORECASE)
    matches = [
        row
        for row in rows
        if pattern.search(row["name"]) or pattern.search(row["signature"])
    ]
    return {
        "key": scan.key,
        "strictNamePattern": scan.strict_name_pattern,
        "strictNameMatches": matches,
    }


def build_report(functions_path: Path) -> dict[str, object]:
    gap_probe = import_gap_probe()
    gap_report = gap_probe.build_report()
    rows = read_function_rows(functions_path)
    scans = [scan_anchor(scan, rows) for scan in REMAINING_SOURCE_ONLY_SCANS]
    expected_keys = {scan.key for scan in REMAINING_SOURCE_ONLY_SCANS}
    actual_source_only_keys = {item["key"] for item in gap_report["sourceOnlyAnchors"]}

    failures: list[str] = []
    if not functions_path.is_file():
        failures.append(f"missing Ghidra function-name export: {relative(functions_path)}")
    missing_source_only = sorted(expected_keys - actual_source_only_keys)
    unexpected_source_only = sorted(actual_source_only_keys - expected_keys)
    failures.extend(f"expected source-only anchor missing from gap report: {key}" for key in missing_source_only)
    failures.extend(f"unexpected source-only anchor remains in gap report: {key}" for key in unexpected_source_only)
    for item in scans:
        if item["strictNameMatches"]:
            failures.append(
                f"strict direct-name matches exist for {item['key']}; update source/binary evidence before keeping it source-only"
            )

    return {
        "schema": "battleengine-remaining-source-only-name-scan.v1",
        "status": "pass" if not failures else "blocked",
        "functionNameExport": relative(functions_path),
        "functionRowsChecked": len(rows),
        "sourceOnlyAnchorsExpected": sorted(expected_keys),
        "sourceOnlyAnchorsActual": sorted(actual_source_only_keys),
        "anchorScans": scans,
        "failures": failures,
        "whatIsProven": [
            "The current BattleEngine source-to-binary gap report still classifies exactly the tracked weapon-fired stealth anchor as source-only pending retail-binary identity.",
            "The current ignored all-functions Ghidra name export contains no strict direct-name matches for that anchor pattern.",
        ],
        "notProven": [
            "Absence of a retail implementation for the remaining anchor.",
            "Candidate decompile/control-flow identity for the remaining anchor.",
            "Exact Steam retail function body for the remaining anchor.",
            "Ghidra rename-map mutation or read-back.",
            "Runtime gameplay behavior for weapon-fired stealth.",
        ],
        "privacy": "Report stores repo-relative filenames, public anchor keys, name patterns, function-name rows from an ignored Ghidra export, and counts only; no binaries, private paths, source excerpts, runtime captures, or Ghidra mutation logs.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check direct-name triage for remaining source-only BattleEngine anchors.")
    parser.add_argument("--check", action="store_true", help="run the remaining-anchor name scan")
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
        print("BattleEngine remaining source-only direct-name scan")
        print(f"Status: {report['status']}")
        print(f"Function rows checked: {report['functionRowsChecked']}")
        for item in report["anchorScans"]:
            print(f"- {item['key']}: strict direct-name matches {len(item['strictNameMatches'])}")
        if report["failures"]:
            for failure in report["failures"]:
                print(f"- FAIL: {failure}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
