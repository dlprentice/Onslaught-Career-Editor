#!/usr/bin/env python3
"""Summarize Goodies 71-73 scalar references from a Ghidra TSV export.

The companion Ghidra script is read-only. This probe consumes its TSV output
and separates expected support functions from candidate functions that may need
manual review for hidden/direct selection paths.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TSV = (
    ROOT
    / "subagents"
    / "goodies-scalar-references"
    / "current"
    / "goodies-scalar-references.tsv"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "goodies-scalar-references"
    / "current"
    / "goodies-scalar-references.json"
)
TARGET_VALUES = {71, 72, 73}

# These functions are already expected to mention 71-73 as data/unlock/type or
# content-bucket support. Hits elsewhere are not automatically bugs; they are
# review candidates for hidden/direct reachability.
KNOWN_SUPPORT_FUNCTIONS = {
    "CCareer__UpdateGoodieStates",
    "CFEPGoodies__BuildStaticGoodieDataTable",
    "CFEPGoodies__StartLoadingGoody",
    "get_goodie_number",
}
GOODIES_ADJACENT_FUNCTION_RE = re.compile(
    r"(Goodie|Career|Script|FEP|FrontEnd|Cheat|Save)", re.IGNORECASE
)
TARGET_IMMEDIATE_OPERANDS = {"0x47", "0x48", "0x49"}


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def parse_int(value: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    try:
        return int(value, 0)
    except ValueError:
        return None


def read_rows(tsv_path: Path) -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    if not tsv_path.is_file():
        return [], ["missing scalar TSV"]

    with tsv_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)

    required = {
        "value_decimal",
        "value_hex",
        "instruction_addr",
        "function_addr",
        "function",
        "block",
        "mnemonic",
        "operand_index",
        "operand",
    }
    missing = sorted(required - set(rows[0].keys() if rows else []))
    if missing:
        failures.append("missing TSV columns: " + ",".join(missing))
    return rows, failures


def build_report(tsv_path: Path) -> dict[str, object]:
    rows, failures = read_rows(tsv_path)
    target_rows: list[dict[str, str]] = []
    malformed_rows: list[dict[str, str]] = []
    for row in rows:
        parsed = parse_int(row.get("value_decimal", ""))
        if parsed is None:
            malformed_rows.append(row)
            continue
        if parsed in TARGET_VALUES:
            target_rows.append(row)

    if malformed_rows:
        failures.append(f"malformed value rows: {len(malformed_rows)}")

    candidate_rows = [
        row
        for row in target_rows
        if row.get("function", "") not in KNOWN_SUPPORT_FUNCTIONS
    ]
    known_rows = [
        row for row in target_rows if row.get("function", "") in KNOWN_SUPPORT_FUNCTIONS
    ]

    value_counts = Counter(row.get("value_decimal", "") for row in target_rows)
    function_counts = Counter(row.get("function", "") for row in target_rows)
    candidate_function_counts = Counter(row.get("function", "") for row in candidate_rows)
    literal_immediate_candidate_rows = [
        row
        for row in candidate_rows
        if row.get("operand", "").strip().lower() in TARGET_IMMEDIATE_OPERANDS
    ]
    focused_candidate_rows = [
        row
        for row in literal_immediate_candidate_rows
        if GOODIES_ADJACENT_FUNCTION_RE.search(row.get("function", ""))
    ]
    focused_candidate_function_counts = Counter(
        row.get("function", "") for row in focused_candidate_rows
    )

    return {
        "schema": "goodies-scalar-references.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "scalarTsv": relative(tsv_path),
        "targetValues": sorted(TARGET_VALUES),
        "rowCount": len(target_rows),
        "knownSupportRowCount": len(known_rows),
        "candidateRowCount": len(candidate_rows),
        "literalImmediateCandidateRowCount": len(literal_immediate_candidate_rows),
        "focusedCandidateRowCount": len(focused_candidate_rows),
        "valueCounts": dict(sorted(value_counts.items())),
        "functionCounts": dict(sorted(function_counts.items())),
        "candidateFunctionCounts": dict(sorted(candidate_function_counts.items())),
        "focusedCandidateFunctionCounts": dict(
            sorted(focused_candidate_function_counts.items())
        ),
        "candidateRows": candidate_rows[:200],
        "literalImmediateCandidateRows": literal_immediate_candidate_rows[:200],
        "focusedCandidateRows": focused_candidate_rows[:200],
        "knownSupportFunctions": sorted(KNOWN_SUPPORT_FUNCTIONS),
        "currentClaims": [
            "The TSV was generated by a read-only Ghidra scalar search over instructions.",
            "Rows in known support functions are expected unlock/data/type/content-bucket evidence, not hidden selector proof by themselves.",
            "Rows outside known support functions are review candidates, not automatic proof of runtime reachability.",
            "Literal immediate candidate rows are more useful than stack/member offset hits; focused candidates additionally stay near Goodies, frontend, save, script, cheat, or career function names.",
        ],
        "notClaimed": [
            "This probe does not launch BEA.exe.",
            "This probe does not mutate Ghidra, saves, or executables.",
            "This probe does not prove candidate rows are hidden Goodies selectors.",
            "This probe does not prove Goodies 71-73 are unreachable.",
        ],
        "failures": failures,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsv", type=Path, default=DEFAULT_TSV)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if the TSV is missing or malformed.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(args.tsv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(args.out)}")
    print(
        "Goodies scalar refs: "
        f"rows={report['rowCount']} "
        f"knownSupport={report['knownSupportRowCount']} "
        f"candidates={report['candidateRowCount']} "
        f"literalImmediateCandidates={report['literalImmediateCandidateRowCount']} "
        f"focusedCandidates={report['focusedCandidateRowCount']}"
    )
    if report["focusedCandidateFunctionCounts"]:
        print(
            "focused candidate functions: "
            + ", ".join(
                f"{key}={value}"
                for key, value in report["focusedCandidateFunctionCounts"].items()
            )
        )
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
