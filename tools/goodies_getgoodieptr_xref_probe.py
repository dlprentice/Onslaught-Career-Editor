#!/usr/bin/env python3
"""Validate read-only Ghidra xrefs relevant to Goodies 71-73.

The probe consumes a TSV exported by ``ExportXrefsForAddresses.java``. It does
not launch the game, read or write BEA.exe directly, mutate a Ghidra project, or
apply a rename map.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_XREF_TSV = (
    ROOT
    / "subagents"
    / "goodies-getgoodieptr-xrefs"
    / "current"
    / "getgoodieptr-xrefs.tsv"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "goodies-getgoodieptr-xrefs"
    / "current"
    / "goodies-getgoodieptr-xrefs.json"
)
DEFAULT_DATA_XREF_TSV = (
    ROOT
    / "subagents"
    / "goodies-71-73-data-xrefs"
    / "current"
    / "goodies-71-73-data-xrefs.tsv"
)
EXPECTED_TARGET = "CCareer__GetGoodiePtr"
EXPECTED_CALLER = "CCareer__UpdateGoodieStates"
EXPECTED_ROW_COUNT = 423
EXPECTED_DATA_TARGETS = {
    "00662680": "g_Career_mGoodies[71]",
    "00662684": "g_Career_mGoodies[72]",
    "00662688": "g_Career_mGoodies[73]",
}


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def summarize_getgoodieptr_xrefs(xref_tsv: Path) -> dict[str, object]:
    rows = read_rows(xref_tsv)
    callers = Counter(row.get("from_function", "") for row in rows)
    targets = Counter(row.get("target_name", "") for row in rows)
    ref_types = Counter(row.get("ref_type", "") for row in rows)

    failures: list[str] = []
    if not xref_tsv.is_file():
        failures.append("missing xref TSV")
    if len(rows) != EXPECTED_ROW_COUNT:
        failures.append(f"expected {EXPECTED_ROW_COUNT} rows, found {len(rows)}")
    if set(targets) != {EXPECTED_TARGET}:
        failures.append("unexpected xref target names")
    if set(callers) != {EXPECTED_CALLER}:
        failures.append("unexpected GetGoodiePtr caller functions")
    if set(ref_types) != {"UNCONDITIONAL_CALL"}:
        failures.append("unexpected reference types")

    return {
        "status": "PASS" if not failures else "FAIL",
        "xrefFile": relative(xref_tsv),
        "rowCount": len(rows),
        "targetCounts": dict(sorted(targets.items())),
        "callerCounts": dict(sorted(callers.items())),
        "refTypeCounts": dict(sorted(ref_types.items())),
        "failures": failures,
    }


def summarize_data_xrefs(data_xref_tsv: Path) -> dict[str, object]:
    rows = read_rows(data_xref_tsv)
    targets = {row.get("target_addr", ""): row for row in rows}
    referenced_rows = [
        row
        for row in rows
        if row.get("from_addr") not in {"", "<none>"}
        or row.get("from_function") not in {"", "<none>"}
        or row.get("ref_type") not in {"", "<none>"}
    ]

    failures: list[str] = []
    if not data_xref_tsv.is_file():
        failures.append("missing data xref TSV")
    if set(targets) != set(EXPECTED_DATA_TARGETS):
        failures.append("unexpected Goodies 71-73 data target set")
    if referenced_rows:
        failures.append("direct data references to Goodies 71-73 were found")

    return {
        "status": "PASS" if not failures else "FAIL",
        "xrefFile": relative(data_xref_tsv),
        "rowCount": len(rows),
        "targets": [
            {
                "address": address,
                "label": EXPECTED_DATA_TARGETS[address],
                "fromAddress": targets.get(address, {}).get("from_addr", ""),
                "fromFunction": targets.get(address, {}).get("from_function", ""),
                "referenceType": targets.get(address, {}).get("ref_type", ""),
            }
            for address in sorted(EXPECTED_DATA_TARGETS)
        ],
        "referencedRowCount": len(referenced_rows),
        "failures": failures,
    }


def build_report(xref_tsv: Path, data_xref_tsv: Path) -> dict[str, object]:
    getgoodieptr = summarize_getgoodieptr_xrefs(xref_tsv)
    data_xrefs = summarize_data_xrefs(data_xref_tsv)
    failures = list(getgoodieptr["failures"]) + list(data_xrefs["failures"])
    return {
        "schema": "goodies-71-73-xrefs.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "getGoodiePtrXrefs": getgoodieptr,
        "dataXrefs": data_xrefs,
        "currentClaims": [
            "Ghidra xrefs to CCareer__GetGoodiePtr currently resolve only to CCareer__UpdateGoodieStates.",
            "This supports the current static model that GetGoodiePtr is an unlock-recomputation helper, not a frontend direct-selection path.",
            "Ghidra reports no direct data xrefs to the concrete g_Career_mGoodies[71..73] addresses in this project.",
        ],
        "notClaimed": [
            "This probe does not launch BEA.exe.",
            "This probe does not mutate the Ghidra project or any executable.",
            "This probe does not prove no indirect array access or runtime-only path can select Goodies 71-73.",
            "This probe does not prove normal Goodies wall reachability for 71-73.",
        ],
        "failures": failures,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xref-tsv", type=Path, default=DEFAULT_XREF_TSV)
    parser.add_argument("--data-xref-tsv", type=Path, default=DEFAULT_DATA_XREF_TSV)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero when the xref summary does not match expectations.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(args.xref_tsv, args.data_xref_tsv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(args.out)}")
    print(
        f"GetGoodiePtr rows: {report['getGoodiePtrXrefs']['rowCount']}; callers: "
        + ", ".join(
            f"{key}={value}"
            for key, value in report["getGoodiePtrXrefs"]["callerCounts"].items()
        )
    )
    print(
        "Goodies 71-73 direct data references: "
        f"{report['dataXrefs']['referencedRowCount']}"
    )
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
