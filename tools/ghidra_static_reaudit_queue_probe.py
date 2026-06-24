#!/usr/bin/env python3
"""Build a public-safe queue for the full static Ghidra re-audit campaign."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current"
DEFAULT_SNAPSHOT = BASE / "functions_quality.tsv"
DEFAULT_OUT = BASE / "static-reaudit-queue.json"

LEGACY_WEAK_RE = re.compile(r"^(FUN_|Auto_)|__Unk_")
UNCERTAIN_OWNER_RE = re.compile(r"(^|_)Unk(_|$)")
ADDRESS_SUFFIX_RE = r"[0-9a-fA-F]{7,8}"
HELPER_ADDRESS_RE = re.compile(rf"Helper_{ADDRESS_SUFFIX_RE}")
WRAPPER_ADDRESS_RE = re.compile(rf"Wrapper_{ADDRESS_SUFFIX_RE}")
PARAM_RE = re.compile(r"\bparam_\d+\b")

SEED_TARGETS = ("0x00506930", "0x00505f70", "0x005069f0", "0x00506010")


def relative(path: Path) -> str:
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
    return "0x" + value.zfill(8)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
        row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def has_comment(row: dict[str, str]) -> bool:
    return bool(row.get("comment", "").strip())


def public_row(row: dict[str, str]) -> dict[str, object]:
    signature = row.get("signature", "")
    name = row.get("name", "")
    return {
        "address": row.get("address", ""),
        "name": name,
        "hasComment": has_comment(row),
        "hasParamSignature": bool(PARAM_RE.search(signature)),
        "hasUndefinedSignature": signature.startswith("undefined "),
        "hasUncertainOwnerName": bool(UNCERTAIN_OWNER_RE.search(name)),
        "hasAddressSuffixedHelperName": bool(HELPER_ADDRESS_RE.search(name)),
        "hasAddressSuffixedWrapperName": bool(WRAPPER_ADDRESS_RE.search(name)),
    }


def sort_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seed_order = {address: index for index, address in enumerate(SEED_TARGETS)}
    return sorted(
        rows,
        key=lambda row: (
            seed_order.get(row.get("address", ""), len(SEED_TARGETS)),
            row.get("address", ""),
            row.get("name", ""),
        ),
    )


def first_public(rows: list[dict[str, str]], count: int = 25) -> list[dict[str, object]]:
    return [public_row(row) for row in sort_rows(rows)[:count]]


def build_report(*, snapshot_path: Path = DEFAULT_SNAPSHOT) -> dict[str, object]:
    snapshot_path = resolve(snapshot_path)
    failures: list[str] = []
    if not snapshot_path.is_file():
        failures.append(f"missing quality snapshot: {relative(snapshot_path)}")

    rows = read_rows(snapshot_path)
    by_address = {row.get("address", ""): row for row in rows}

    legacy_weak = [row for row in rows if LEGACY_WEAK_RE.search(row.get("name", ""))]
    commentless = [row for row in rows if not has_comment(row)]
    undefined_signatures = [row for row in rows if row.get("signature", "").startswith("undefined ")]
    param_signatures = [row for row in rows if PARAM_RE.search(row.get("signature", ""))]
    uncertain_owner = [row for row in rows if UNCERTAIN_OWNER_RE.search(row.get("name", ""))]
    helper_address = [row for row in rows if HELPER_ADDRESS_RE.search(row.get("name", ""))]
    wrapper_address = [row for row in rows if WRAPPER_ADDRESS_RE.search(row.get("name", ""))]

    high_signal = [
        row
        for row in commentless
        if row in undefined_signatures
        or row in param_signatures
        or row in uncertain_owner
        or row in helper_address
        or row in wrapper_address
    ]
    signature_queue = sorted(set(id(row) for row in undefined_signatures + param_signatures))
    signature_by_id = {id(row): row for row in undefined_signatures + param_signatures}
    name_queue = sorted(set(id(row) for row in uncertain_owner + helper_address + wrapper_address))
    name_by_id = {id(row): row for row in uncertain_owner + helper_address + wrapper_address}

    if not rows:
        failures.append("quality snapshot contained no rows")
    if legacy_weak:
        failures.append(f"legacy weak names returned in quality snapshot: {len(legacy_weak)}")

    seed_status = {}
    for address in SEED_TARGETS:
        row = by_address.get(address)
        if row is None:
            seed_status[address] = {"present": False, "hasComment": False, "name": None}
        else:
            seed_status[address] = {
                "present": True,
                "hasComment": has_comment(row),
                "name": row.get("name", ""),
            }

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-static-reaudit-queue.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {"functionQualitySnapshot": relative(snapshot_path)},
        "totalFunctions": len(rows),
        "qualitySignals": {
            "legacyWeakNameCount": len(legacy_weak),
            "commentlessFunctionCount": len(commentless),
            "undefinedSignatureCount": len(undefined_signatures),
            "paramSignatureCount": len(param_signatures),
            "uncertainOwnerNameCount": len(uncertain_owner),
            "helperAddressNameCount": len(helper_address),
            "wrapperAddressNameCount": len(wrapper_address),
        },
        "seedFunctionStatus": seed_status,
        "priorityQueues": {
            "commentlessHighSignal": first_public(high_signal),
            "signature": first_public([signature_by_id[row_id] for row_id in signature_queue]),
            "nameConfidence": first_public([name_by_id[row_id] for row_id in name_queue]),
            "legacyWeakNames": first_public(legacy_weak),
        },
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra database can be exported into a full function quality snapshot with comments and signatures.",
            "The static re-audit queue can separate comment debt, signature debt, and name-confidence debt without exposing private decompile text.",
            "The weapon/burst seed status can be checked from the same all-function snapshot.",
        ],
        "notProven": [
            "This does not prove every current Ghidra name, signature, comment, or boundary is correct.",
            "This does not mutate Ghidra names, signatures, comments, tags, or function boundaries.",
            "This does not prove exact source-to-retail identity or runtime behavior.",
        ],
        "privacy": "Report stores repo-relative filenames, aggregate counts, public addresses, names, and boolean quality flags only; the full TSV snapshot remains ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
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

    report = build_report(snapshot_path=args.snapshot)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        quality = report["qualitySignals"]
        print("Ghidra static re-audit queue probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Total functions: {report['totalFunctions']}")
        print(f"Commentless functions: {quality['commentlessFunctionCount']}")
        print(f"Undefined signatures: {quality['undefinedSignatureCount']}")
        print(f"Param signatures: {quality['paramSignatureCount']}")
        print(f"Uncertain owner names: {quality['uncertainOwnerNameCount']}")
        print(f"Address-suffixed helpers: {quality['helperAddressNameCount']}")
        print(f"Address-suffixed wrappers: {quality['wrapperAddressNameCount']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
