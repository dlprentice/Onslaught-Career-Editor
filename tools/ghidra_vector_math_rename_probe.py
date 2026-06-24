#!/usr/bin/env python3
"""Verify the Ghidra vector math helper rename read-back.

This probe checks a small saved Ghidra rename tranche for two generic Vec3
helpers from the name-confidence queue. It intentionally keeps the claim to
math-helper behavior and saved symbol names, not final type/signature recovery
or exact source method identity.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "vector-math-rename" / "current"
DEFAULT_DRY_LOG = BASE / "rename_dry.log"
DEFAULT_APPLY_LOG = BASE / "rename_apply.log"
DEFAULT_DECOMPILE_INDEX = BASE / "decompile_after" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_after"
DEFAULT_XREFS = BASE / "xrefs_after.tsv"
DEFAULT_OUT = BASE / "vector-math-rename.json"

MAG_ADDR = "0x004026b0"
NORM_ADDR = "0x00406d50"
MAG_OLD = "SQRT__Wrapper_004026b0"
NORM_OLD = "SQRT__Wrapper_00406d50"
MAG_NEW = "Vec3__Magnitude"
NORM_NEW = "Vec3__NormalizeInPlace"

TARGETS = [
    {
        "address": MAG_ADDR,
        "oldName": MAG_OLD,
        "newName": MAG_NEW,
        "tokens": ["SQRT(", "+ 8", "+ 4", "param_1"],
    },
    {
        "address": NORM_ADDR,
        "oldName": NORM_OLD,
        "newName": NORM_NEW,
        "tokens": ["SQRT(", "_DAT_005d8568 / fVar1", "+ 8", "param_1"],
    },
]


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value in {"", "<none>", "<no_function>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def find_row(rows: list[dict[str, str]], key: str, address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"applied=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"applied": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "applied": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
    }


def has_rename_line(log_text: str, prefix: str, address: str, old: str, new: str) -> bool:
    return f"{prefix}: {address} {old} -> {new}" in log_text


def find_decompile_file(decompile_dir: Path, address: str, name: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    needle = normalize_address(address)[2:]
    matches = sorted(decompile_dir.glob(f"{needle}_{name}.c"))
    return matches[0] if matches else None


def xref_target_names(rows: list[dict[str, str]], address: str) -> set[str]:
    wanted = normalize_address(address)
    names: set[str] = set()
    for row in rows:
        if normalize_address(row.get("target_addr", "")) == wanted:
            names.add(row.get("target_name", ""))
    return names


def build_report(
    *,
    dry_log_path: Path = DEFAULT_DRY_LOG,
    apply_log_path: Path = DEFAULT_APPLY_LOG,
    decompile_index_path: Path = DEFAULT_DECOMPILE_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)

    failures: list[str] = []
    for label, path in (
        ("dry rename log", dry_log_path),
        ("apply rename log", apply_log_path),
        ("decompile read-back index", decompile_index_path),
        ("decompile read-back dir", decompile_dir),
        ("xref read-back", xrefs_path),
    ):
        if label == "decompile read-back dir":
            if not path.is_dir():
                failures.append(f"missing {label}: {relative(path)}")
        elif not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    dry_text = read_text(dry_log_path)
    apply_text = read_text(apply_log_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)

    dry_summary = parse_summary(dry_text)
    apply_summary = parse_summary(apply_text)
    expected_count = len(TARGETS)
    if dry_summary != {"applied": 0, "skipped": expected_count, "missing": 0, "bad": 0}:
        failures.append("dry rename log does not show the expected clean dry-run summary")
    if apply_summary != {"applied": expected_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("apply rename log does not show the expected clean apply summary")

    readback: dict[str, object] = {}
    evidence: dict[str, bool] = {}
    renames: list[dict[str, str]] = []

    for target in TARGETS:
        address = target["address"]
        old = target["oldName"]
        new = target["newName"]
        renames.append({"address": address, "oldName": old, "newName": new})

        if not has_rename_line(dry_text, "DRY", address, old, new):
            failures.append(f"dry rename log missing {address} {old} -> {new}")
        if not has_rename_line(apply_text, "OK", address, old, new):
            failures.append(f"apply rename log missing {address} {old} -> {new}")

        index_row = find_row(index_rows, "address", address)
        renamed = index_row is not None and index_row.get("name") == new and index_row.get("status") == "OK"
        if not renamed:
            failures.append(f"missing decompile read-back for {address} as {new}")

        decompile_file = find_decompile_file(decompile_dir, address, new)
        decompile_text = read_text(decompile_file) if decompile_file else ""
        missing_tokens = [token for token in target["tokens"] if token not in decompile_text]
        shape_present = not missing_tokens
        if missing_tokens:
            failures.append(f"{new} decompile missing expected shape tokens: {', '.join(missing_tokens)}")

        names = xref_target_names(xref_rows, address)
        xrefs_updated = new in names and old not in names
        if not xrefs_updated:
            failures.append(f"xref read-back for {address} does not use {new} cleanly")

        key = "magnitude" if address == MAG_ADDR else "normalizeInPlace"
        readback[f"{key}Renamed"] = renamed
        readback[f"{key}XrefsUpdated"] = xrefs_updated
        evidence[f"{key}ShapePresent"] = shape_present

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-vector-math-rename.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "vector-math-helpers-renamed" if status == "PASS" else "vector-math-rename-blocked",
        "renames": renames,
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "readback": readback,
        "evidence": evidence,
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
        },
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra names for 0x004026b0 and 0x00406d50 were changed after a clean dry-run and clean apply.",
            "Read-back shows 0x004026b0 as Vec3__Magnitude and 0x00406d50 as Vec3__NormalizeInPlace.",
            "The post-rename decompile shapes still match 3-float vector magnitude and in-place normalization behavior.",
            "Post-rename xref export reports the updated target names for the checked addresses.",
        ],
        "notProven": [
            "This does not harden parameter types, return types, calling conventions, local names, or data types.",
            "This does not prove exact source FVector method identity.",
            "This does not prove runtime behavior beyond static retail decompile/xref read-back.",
            "This does not complete the broader Ghidra static re-audit queue.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, command summaries, counts, and proof boundaries only; raw Ghidra logs, xrefs, and decompiles remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY_LOG)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY_LOG)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_DECOMPILE_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    out = resolve(args.out)
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}", file=sys.stderr)
        return 1

    report = build_report(
        dry_log_path=args.dry_log,
        apply_log_path=args.apply_log,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra vector math rename probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        for rename in report["renames"]:
            print(f"Rename: {rename['address']} {rename['oldName']} -> {rename['newName']}")
        print(f"Dry summary: {report['drySummary']}")
        print(f"Apply summary: {report['applySummary']}")
        print(f"Read-back: {report['readback']}")
        print(f"Evidence: {report['evidence']}")
        if report["failures"]:
            print("Failures:")
            for failure in report["failures"]:
                print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
