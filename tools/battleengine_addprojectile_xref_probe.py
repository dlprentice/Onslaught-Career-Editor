#!/usr/bin/env python3
"""Check current Ghidra xrefs to CBattleEngine__AddProjectile.

This is a bounded static RE probe. It consumes an ignored read-only Ghidra xref
export for `CBattleEngine__AddProjectile` at 0x00406fc0 and records whether the
current callers are confined to the already named projectile/targeting helper at
0x00406560. That narrows the weapon-fired stealth search, but it is not proof
that retail weapon fire never clears stealth or that no inlined/runtime path
exists elsewhere.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_XREFS = (
    ROOT
    / "subagents"
    / "battleengine-addprojectile-xrefs"
    / "current"
    / "xrefs"
    / "addprojectile_xrefs.tsv"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "battleengine-addprojectile-xrefs"
    / "current"
    / "addprojectile-xref-probe.json"
)

TARGET_ADDRESS = "00406fc0"
TARGET_NAME = "CBattleEngine__AddProjectile"
EXPECTED_CALLER_ADDRESS = "00406560"
EXPECTED_CALLER_NAME = "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles"
EXPECTED_FROM_ADDRESSES = ("004068d9", "00406a51", "00406aae", "00406d06")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return value.zfill(8)


def read_xrefs(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def build_report(xrefs_path: Path = DEFAULT_XREFS) -> dict[str, object]:
    xrefs_path = xrefs_path if xrefs_path.is_absolute() else ROOT / xrefs_path
    rows = read_xrefs(xrefs_path)

    expected_from = {normalize_address(value) for value in EXPECTED_FROM_ADDRESSES}
    unexpected_rows: list[dict[str, str]] = []
    failures: list[str] = []

    if not xrefs_path.is_file():
        failures.append(f"missing xref export: {relative(xrefs_path)}")

    addprojectile_rows = [
        row
        for row in rows
        if normalize_address(row.get("target_addr", "")) == TARGET_ADDRESS
        and row.get("target_name") == TARGET_NAME
    ]

    for row in addprojectile_rows:
        caller_addr = normalize_address(row.get("from_function_addr", ""))
        caller_name = row.get("from_function", "")
        if caller_addr != EXPECTED_CALLER_ADDRESS or caller_name != EXPECTED_CALLER_NAME:
            unexpected_rows.append(row)

    observed_from = {normalize_address(row.get("from_addr", "")) for row in addprojectile_rows}
    missing_from = sorted(expected_from - observed_from)
    extra_from = sorted(observed_from - expected_from)

    if unexpected_rows:
        failures.append(f"unexpected AddProjectile caller rows: {len(unexpected_rows)}")
    if len(addprojectile_rows) != len(EXPECTED_FROM_ADDRESSES):
        failures.append(
            f"expected {len(EXPECTED_FROM_ADDRESSES)} AddProjectile xref rows, found {len(addprojectile_rows)}"
        )
    if missing_from:
        failures.append(f"missing expected AddProjectile callsites: {missing_from}")
    if extra_from:
        failures.append(f"unexpected AddProjectile callsites: {extra_from}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "battleengine-addprojectile-xrefs.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "xrefExport": relative(xrefs_path),
        "target": {
            "address": "0x00406fc0",
            "name": TARGET_NAME,
        },
        "expectedCaller": {
            "address": "0x00406560",
            "name": EXPECTED_CALLER_NAME,
        },
        "xrefRowCount": len(addprojectile_rows),
        "observedFromAddresses": sorted("0x" + value for value in observed_from),
        "unexpectedCallerRows": unexpected_rows,
        "callerClassification": (
            "addprojectile-xrefs-confined-to-projectile-helper"
            if status == "PASS"
            else "blocked-or-unexpected-addprojectile-caller"
        ),
        "failures": failures,
        "whatIsProven": [
            "The current read-only Ghidra xref export has four xrefs to CBattleEngine__AddProjectile at 0x00406fc0.",
            "All four current AddProjectile xrefs originate inside CBattleEngine__UpdateAutoTargetSetAndFireProjectiles at 0x00406560.",
            "The AddProjectile caller set does not currently expose a separate retail CWeapon::Fire or CBattleEngine::WeaponFired body.",
        ],
        "notProven": [
            "This does not prove retail weapon fire never clears stealth.",
            "This does not identify the exact retail CBattleEngine::WeaponFired implementation.",
            "This does not rule out an inlined, callback, virtual dispatch, or runtime-only weapon-fire path outside direct AddProjectile xrefs.",
            "This does not mutate Ghidra, patch BEA.exe, launch the game, or prove runtime cloak/fire behavior.",
        ],
        "privacy": "Report stores repo-relative paths, public addresses, function names, xref counts, and proof boundaries only; raw xref exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}", file=sys.stderr)
        return 1

    report = build_report(args.xrefs)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine AddProjectile xref probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['callerClassification']}")
        print(f"Xref rows: {report['xrefRowCount']}")
        print(f"Unexpected caller rows: {len(report['unexpectedCallerRows'])}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
