#!/usr/bin/env python3
"""Validate the saved Ghidra correction for the GeneralVolume axis helpers."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "general-volume-axis-correction" / "current"

DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_INSTRUCTIONS = BASE / "raw_callsite_instructions_readback.tsv"
DEFAULT_OUT = BASE / "general-volume-axis-correction.json"

RULES = {
    "0x00413660": {
        "oldName": "CGeneralVolume_Unk_00409e60__Wrapper_00413660",
        "newName": "CGeneralVolume__ApplyYawInputByWeaponClass",
        "classification": "general-volume-yaw-axis-helper-corrected",
        "axis": "yaw",
        "axisField": "+0x278",
        "fromAddr": "0x004d337b",
        "tokens": [
            "CGeneralVolume__ApplyYawInputByWeaponClass",
            "+0x278",
            "+0x4b0",
            "+0x18",
            "+0x2c8",
            "CGeneralVolume__ToDoubleIdentity",
        ],
        "commentTokens": ["Proof-boundary", "axis", "runtime behavior"],
        "scope": "Mode-2 GeneralVolume input helper that subtracts yaw-rate field +0x278 with profile-rate scaling.",
    },
    "0x004136e0": {
        "oldName": "CMonitor__ApplyYawInputByWeaponClass",
        "newName": "CGeneralVolume__ApplyPitchInputByWeaponClass",
        "classification": "stale-cmonitor-yaw-label-corrected-to-general-volume-pitch",
        "axis": "pitch",
        "axisField": "+0x280",
        "fromAddr": "0x004d3390",
        "tokens": [
            "CGeneralVolume__ApplyPitchInputByWeaponClass",
            "+0x280",
            "+0x2c8",
            "_DAT_005d8c90",
            "CGeneralVolume__ToDoubleIdentity",
        ],
        "commentTokens": ["Corrected from stale", "Proof-boundary", "runtime behavior"],
        "scope": "Adjacent mode-2 GeneralVolume input helper that subtracts pitch-rate field +0x280 with fixed-rate scaling.",
    },
}


def relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if not value or value in {"<none>", "<no_function>"}:
        return value
    return "0x" + value.zfill(8)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_metadata(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
        row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def read_index(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
    return {row["address"]: row for row in rows if row.get("address")}


def read_xrefs(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr_norm"] = normalize_address(row.get("target_addr", ""))
        row["from_addr_norm"] = normalize_address(row.get("from_addr", ""))
    return rows


def read_instructions(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr_norm"] = normalize_address(row.get("target_addr", ""))
        row["instruction_addr_norm"] = normalize_address(row.get("instruction_addr", ""))
        row["operands_norm"] = normalize_address(row.get("operands", ""))
    return rows


def compact(value: str) -> str:
    return "".join(value.lower().split())


def has_token(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def find_decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def build_report(
    *,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
) -> dict[str, object]:
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    metadata = {row["address"]: row for row in read_metadata(metadata_path)}
    decompile_index = read_index(decompile_index_path)
    xrefs = read_xrefs(xrefs_path)
    instructions = read_instructions(instructions_path)
    failures: list[str] = []
    function_reports: list[dict[str, object]] = []
    axis_fields: dict[str, str] = {}

    for address, rule in RULES.items():
        row = metadata.get(address)
        if not row:
            failures.append(f"{address}: missing metadata read-back row")
            continue

        name = row.get("name", "")
        comment = row.get("comment", "")
        decompile_file = find_decompile_file(decompile_dir, address)
        decompile_text = read_text(decompile_file)
        index_row = decompile_index.get(address)
        matching_xrefs = [
            row
            for row in xrefs
            if row.get("target_addr_norm") == address and row.get("from_addr_norm") == rule["fromAddr"]
        ]
        matching_instruction = [
            row
            for row in instructions
            if row.get("instruction_addr_norm") == rule["fromAddr"]
            and (
                row.get("operands_norm") == address
                or normalize_address(row.get("target_raw", "")) == address
                or normalize_address(row.get("target_addr", "")) == rule["fromAddr"]
            )
        ]

        if name != rule["newName"]:
            failures.append(f"{address}: expected {rule['newName']}, got {name or '<blank>'}")
        if rule["oldName"] == name:
            failures.append(f"{address}: stale name survived ({rule['oldName']})")
        if not index_row:
            failures.append(f"{address}: missing decompile index row")
        if not decompile_text:
            failures.append(f"{address}: missing decompile text")
        for token in rule["tokens"]:
            if not has_token(decompile_text, token):
                failures.append(f"{address}: decompile missing token {token!r}")
        for token in rule["commentTokens"]:
            if not has_token(comment, token):
                failures.append(f"{address}: comment missing token {token!r}")
        if not matching_xrefs:
            failures.append(f"{address}: missing xref from {rule['fromAddr']}")
        if not matching_instruction:
            failures.append(f"{address}: missing raw callsite instruction at {rule['fromAddr']}")

        axis_fields[address] = rule["axisField"]
        function_reports.append(
            {
                "address": address,
                "oldName": rule["oldName"],
                "newName": rule["newName"],
                "classification": rule["classification"],
                "axis": rule["axis"],
                "axisField": rule["axisField"],
                "fromAddr": rule["fromAddr"],
                "scope": rule["scope"],
                "decompileFile": relative(decompile_file),
                "xrefCount": len(matching_xrefs),
                "rawCallsiteInstructionCount": len(matching_instruction),
            }
        )

    return {
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "metadataPath": relative(metadata_path),
        "decompileIndexPath": relative(decompile_index_path),
        "decompileDir": relative(decompile_dir),
        "xrefsPath": relative(xrefs_path),
        "instructionsPath": relative(instructions_path),
        "correctedFunctionCount": len(RULES) if not failures else 0,
        "axisFields": axis_fields,
        "functions": function_reports,
        "failures": failures,
        "limits": [
            "Saved Ghidra name/comment correction only.",
            "Does not harden signatures, parameter names, local names, structures, tags, exact source identity, or runtime behavior.",
            "Does not prove broader GeneralVolume or CMonitor owner boundaries outside this two-function axis pair.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true", help="Exit non-zero on validation failure.")
    args = parser.parse_args(argv)

    report = build_report(
        metadata_path=args.metadata,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
    )

    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"status={report['status']}")
    print(f"out={relative(out_path)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
