#!/usr/bin/env python3
"""Validate public-safe xref evidence for transform/HUD strings.

The probe consumes a TSV exported by ExportXrefsForAddresses.java. It records
string addresses, xref function names, and row counts only. It does not read or
write BEA.exe, launch the game, mutate a Ghidra project, or include private paths.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_XREF_TSV = ROOT / "subagents" / "battleengine-transform-xrefs" / "current" / "string-xrefs.tsv"
DEFAULT_OUT = ROOT / "subagents" / "battleengine-transform-xrefs" / "current" / "battleengine-transform-string-xrefs.json"


@dataclass(frozen=True)
class XrefExpectation:
    address: str
    label: str
    expected_functions: tuple[str, ...]


EXPECTATIONS: tuple[XrefExpectation, ...] = (
    XrefExpectation(
        "006234bc",
        "flytowalk",
        (
            "CGeneralVolume__BeginFlyToWalkTransition",
            "CUnit__FinishedPlayingCurrentAnimation",
            "CMonitor__UpdateFlightWalkerTransitionState",
        ),
    ),
    XrefExpectation(
        "006234b0",
        "walktofly",
        (
            "CGeneralVolume__BeginWalkToFlyTransition",
            "CUnit__FinishedPlayingCurrentAnimation",
            "CMonitor__UpdateFlightWalkerTransitionState",
        ),
    ),
    XrefExpectation(
        "0062331c",
        "hud_armour_low",
        (
            "CMonitor__Process",
        ),
    ),
    XrefExpectation(
        "00623304",
        "hud_energy_low",
        (
            "CMonitor__Process",
        ),
    ),
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def summarize(expectation: XrefExpectation, rows: list[dict[str, str]]) -> dict[str, object]:
    matches = [row for row in rows if row.get("target_addr", "").lower() == expectation.address.lower()]
    functions = sorted({row.get("from_function", "") for row in matches if row.get("from_function")})
    missing = [name for name in expectation.expected_functions if name not in functions]
    return {
        "address": "0x" + expectation.address,
        "label": expectation.label,
        "status": "PASS" if not missing and matches else "FAIL",
        "xrefCount": len(matches),
        "functions": functions,
        "missingFunctions": missing,
    }


def build_report(xref_tsv: Path) -> dict[str, object]:
    rows = read_rows(xref_tsv) if xref_tsv.is_file() else []
    results = [summarize(expectation, rows) for expectation in EXPECTATIONS]
    return {
        "schema": "battleengine-transform-string-xrefs.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "xrefTsv": relative(xref_tsv),
        "mutation": False,
        "stringsChecked": len(results),
        "stringsPassed": sum(1 for item in results if item["status"] == "PASS"),
        "results": results,
        "privacy": "Report stores string labels, public-safe string addresses, xref counts, and function names only; it does not include private paths, raw binary bytes, source excerpts, decompile excerpts, runtime captures, or mutation logs.",
        "proves": [
            "Current Ghidra xrefs for flytowalk and walktofly point at transition helper functions rather than proving the source CBattleEngine::Morph body",
            "Current Ghidra xrefs for HUD low-armour/low-energy strings point at CMonitor__Process",
        ],
        "doesNotProve": [
            "Exact source-to-retail identity for source CBattleEngine::Morph / the transform-morph flow",
            "Runtime transform or HUD-warning behavior",
            "Ghidra rename-map mutation",
            "Rebuildable open-source gameplay implementation",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate BattleEngine transform/HUD string xref evidence.")
    parser.add_argument("--xref-tsv", type=Path, default=DEFAULT_XREF_TSV)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_report(args.xref_tsv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine transform string xref probe")
        print(f"Output: {relative(args.out)}")
        print(f"Strings: {report['stringsPassed']}/{report['stringsChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['address']} {item['label']} xrefs={item['xrefCount']}")

    return 0 if not args.check or report["stringsPassed"] == report["stringsChecked"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
