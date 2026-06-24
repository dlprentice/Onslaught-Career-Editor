#!/usr/bin/env python3
"""Build a public-safe baseline for a full static Ghidra re-audit campaign.

The baseline deliberately separates "all function objects have names" from
"all function objects are confidently named and signed." It consumes an ignored
read-only `ExportWeakFunctionList.java` all-functions TSV export and writes a
small report under `subagents/`.
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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "current"
DEFAULT_FUNCTIONS = BASE / "functions_all.tsv"
DEFAULT_OUT = BASE / "static-reaudit-baseline.json"

LEGACY_WEAK_RE = re.compile(r"^(FUN_|Auto_)|__Unk_")
UNCERTAIN_OWNER_RE = re.compile(r"(^|_)Unk(_|$)")
ADDRESS_SUFFIX_RE = r"[0-9a-fA-F]{7,8}"
HELPER_ADDRESS_RE = re.compile(rf"Helper_{ADDRESS_SUFFIX_RE}")
WRAPPER_ADDRESS_RE = re.compile(rf"Wrapper_{ADDRESS_SUFFIX_RE}")
PARAM_RE = re.compile(r"\bparam_\d+\b")

SEED_REAUDIT_TARGETS = {
    "0x00506010": "Current exports call this CGeneralVolume__SpawnBurstFromPresetWithFallback, while older reference material records CGeneralVolume__Helper_00506010.",
    "0x005069f0": "Current exports call this CEngine__SpawnProjectileBurstFromCurrentPreset, but earlier waves tracked it as CEngine__Unk_005069f0 and exact source identity remains unproven.",
    "0x00506930": "Raw vtable slot-0 target; current all-function export does not list it as a normal function object.",
    "0x005078b0": "Currently named CEngine__GetListEntryIdByIndex; useful boundary-adjacent check target for the weapon/burst cluster.",
}


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


def read_functions(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def public_function(row: dict[str, str]) -> dict[str, str]:
    return {
        "address": normalize_address(row.get("address", "")),
        "name": row.get("name", ""),
        "signature": row.get("signature", ""),
    }


def first_examples(rows: list[dict[str, str]], count: int = 10) -> list[dict[str, str]]:
    return [public_function(row) for row in rows[:count]]


def build_report(*, functions_path: Path = DEFAULT_FUNCTIONS) -> dict[str, object]:
    functions_path = resolve(functions_path)
    failures: list[str] = []
    if not functions_path.is_file():
        failures.append(f"missing all-functions export: {relative(functions_path)}")

    rows = read_functions(functions_path)
    by_address = {normalize_address(row.get("address", "")): row for row in rows}

    legacy_weak = [row for row in rows if LEGACY_WEAK_RE.search(row.get("name", ""))]
    uncertain_owner = [row for row in rows if UNCERTAIN_OWNER_RE.search(row.get("name", ""))]
    helper_address = [row for row in rows if HELPER_ADDRESS_RE.search(row.get("name", ""))]
    wrapper_address = [row for row in rows if WRAPPER_ADDRESS_RE.search(row.get("name", ""))]
    param_signatures = [row for row in rows if PARAM_RE.search(row.get("signature", ""))]
    undefined_signatures = [row for row in rows if row.get("signature", "").startswith("undefined ")]

    seed_present = {
        address: public_function(by_address[address])
        for address in SEED_REAUDIT_TARGETS
        if address in by_address
    }
    seed_missing = [
        address
        for address in SEED_REAUDIT_TARGETS
        if address not in by_address
    ]

    if legacy_weak:
        failures.append(f"legacy weak names returned in all-functions export: {len(legacy_weak)}")
    if not rows:
        failures.append("all-functions export contained no rows")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-static-reaudit-baseline.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "functionsAll": relative(functions_path),
        },
        "totalFunctions": len(rows),
        "legacyWeakNameCount": len(legacy_weak),
        "qualitySignals": {
            "uncertainOwnerNameCount": len(uncertain_owner),
            "helperAddressNameCount": len(helper_address),
            "wrapperAddressNameCount": len(wrapper_address),
            "paramSignatureCount": len(param_signatures),
            "undefinedSignatureCount": len(undefined_signatures),
        },
        "examples": {
            "legacyWeakNames": first_examples(legacy_weak),
            "uncertainOwnerNames": first_examples(uncertain_owner),
            "helperAddressNames": first_examples(helper_address),
            "wrapperAddressNames": first_examples(wrapper_address),
            "paramSignatures": first_examples(param_signatures),
            "undefinedSignatures": first_examples(undefined_signatures),
        },
        "seedReauditTargets": {
            "presentFunctionObjects": seed_present,
            "missingFunctionObjects": seed_missing,
            "reasons": SEED_REAUDIT_TARGETS,
        },
        "failures": failures,
        "whatIsProven": [
            "The current Ghidra database can export a complete all-functions list through headless tooling.",
            "Legacy weak-name closure can be checked separately from broader name/signature confidence.",
            "The weapon/burst cluster has concrete seed targets for boundary and name-confidence re-audit.",
        ],
        "notProven": [
            "This does not prove every current Ghidra name is correct.",
            "This does not mutate names, signatures, comments, tags, or function boundaries.",
            "This does not prove exact source-to-retail identity for any seed target.",
            "This does not prove runtime behavior.",
        ],
        "privacy": "Report stores repo-relative filenames, function addresses, current names/signatures, aggregate counts, examples, and proof boundaries only; full TSV export remains ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--functions", type=Path, default=DEFAULT_FUNCTIONS)
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

    report = build_report(functions_path=args.functions)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        quality = report["qualitySignals"]
        print("Ghidra static re-audit baseline probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Total functions: {report['totalFunctions']}")
        print(f"Legacy weak names: {report['legacyWeakNameCount']}")
        print(f"Uncertain owner names: {quality['uncertainOwnerNameCount']}")
        print(f"Address-suffixed helpers: {quality['helperAddressNameCount']}")
        print(f"Address-suffixed wrappers: {quality['wrapperAddressNameCount']}")
        print(f"Param signatures: {quality['paramSignatureCount']}")
        print(f"Undefined signatures: {quality['undefinedSignatureCount']}")
        print(
            "Seed missing function objects: "
            + (", ".join(report["seedReauditTargets"]["missingFunctionObjects"]) or "<none>")
        )
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
