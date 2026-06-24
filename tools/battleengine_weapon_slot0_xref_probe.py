#!/usr/bin/env python3
"""Check current xrefs around the weapon vtable slot-0 raw candidate.

This bounded static RE probe consumes ignored read-only Ghidra xref and
decompile-index exports for the current slot-0 candidate. It checks whether
`0x00506930` is only directly referenced as the vtable slot value, whether the
inner body at `0x005069f0` is reached by the raw outer stub and a named burst
caller, and whether `0x005078b0` remains a helper called from the inner body.

It does not mutate Ghidra and does not claim exact `CWeapon::Fire` or
`CBattleEngine::WeaponFired` identity.
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
BASE = ROOT / "subagents" / "battleengine-weapon-slot0-xrefs" / "current"
DEFAULT_XREFS = BASE / "slot0_xrefs.tsv"
DEFAULT_DECOMPILE_INDEX = BASE / "decompile" / "index.tsv"
DEFAULT_OUT = BASE / "weapon-slot0-xrefs.json"

SLOT0_STUB = "0x00506930"
VTABLE_SLOT0_ENTRY = "0x005dfc94"
INNER_BODY = "0x005069f0"
INNER_NAMED_CALLER = "0x00506010"
INNER_NAMED_CALLER_NAME = "CGeneralVolume__SpawnBurstFromPresetWithFallback"
INNER_BODY_NAME = "CEngine__SpawnProjectileBurstFromCurrentPreset"
RAW_OUTER_CALLSITE = "0x005069b6"
POST_RETURN_HELPER = "0x005078b0"
POST_RETURN_HELPER_NAME = "CEngine__GetListEntryIdByIndex"
POST_RETURN_CALLSITE = "0x00506b75"


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value in {"", "<none>", "none"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def rows_for_target(rows: list[dict[str, str]], target: str) -> list[dict[str, str]]:
    normalized = normalize_address(target)
    return [row for row in rows if normalize_address(row.get("target_addr", "")) == normalized]


def decompile_names(rows: list[dict[str, str]]) -> dict[str, str]:
    names: dict[str, str] = {}
    for row in rows:
        address = normalize_address(row.get("address", ""))
        if address.startswith("0x"):
            names[address] = row.get("name", "")
    return names


def public_row(row: dict[str, str]) -> dict[str, str]:
    return {
        "targetAddress": normalize_address(row.get("target_addr", "")),
        "targetName": row.get("target_name", ""),
        "fromAddress": normalize_address(row.get("from_addr", "")),
        "fromFunctionAddress": normalize_address(row.get("from_function_addr", "")),
        "fromFunction": row.get("from_function", ""),
        "refType": row.get("ref_type", ""),
    }


def build_report(
    *,
    xrefs_path: Path = DEFAULT_XREFS,
    decompile_index_path: Path = DEFAULT_DECOMPILE_INDEX,
) -> dict[str, object]:
    xrefs_path = resolve(xrefs_path)
    decompile_index_path = resolve(decompile_index_path)

    failures: list[str] = []
    if not xrefs_path.is_file():
        failures.append(f"missing xref export: {relative(xrefs_path)}")
    if not decompile_index_path.is_file():
        failures.append(f"missing decompile index: {relative(decompile_index_path)}")

    xref_rows = read_tsv(xrefs_path)
    index_rows = read_tsv(decompile_index_path)
    names = decompile_names(index_rows)

    slot0_rows = rows_for_target(xref_rows, SLOT0_STUB)
    inner_rows = rows_for_target(xref_rows, INNER_BODY)
    post_return_rows = rows_for_target(xref_rows, POST_RETURN_HELPER)

    slot0_data_refs = [
        row
        for row in slot0_rows
        if normalize_address(row.get("from_addr", "")) == VTABLE_SLOT0_ENTRY and row.get("ref_type", "") == "DATA"
    ]
    unexpected_direct_slot0_code_refs = [
        public_row(row) for row in slot0_rows if row.get("ref_type", "") != "DATA"
    ]

    named_inner_callers = [
        row
        for row in inner_rows
        if normalize_address(row.get("from_function_addr", "")) == INNER_NAMED_CALLER
        and row.get("from_function", "") == INNER_NAMED_CALLER_NAME
    ]
    raw_outer_callsites = [
        normalize_address(row.get("from_addr", ""))
        for row in inner_rows
        if normalize_address(row.get("from_addr", "")) == RAW_OUTER_CALLSITE
        and normalize_address(row.get("from_function_addr", "")) == "<none>"
    ]
    post_return_inner_callsites = [
        normalize_address(row.get("from_addr", ""))
        for row in post_return_rows
        if normalize_address(row.get("from_addr", "")) == POST_RETURN_CALLSITE
        and normalize_address(row.get("from_function_addr", "")) == INNER_BODY
    ]

    if len(slot0_data_refs) != 1:
        failures.append(f"expected one DATA ref from vtable slot entry {VTABLE_SLOT0_ENTRY} to {SLOT0_STUB}")
    if unexpected_direct_slot0_code_refs:
        failures.append(f"unexpected direct code refs to slot0 stub: {len(unexpected_direct_slot0_code_refs)}")
    if not named_inner_callers:
        failures.append(f"missing named caller {INNER_NAMED_CALLER_NAME} ({INNER_NAMED_CALLER}) to {INNER_BODY}")
    if RAW_OUTER_CALLSITE not in raw_outer_callsites:
        failures.append(f"missing raw outer-stub callsite {RAW_OUTER_CALLSITE} to {INNER_BODY}")
    if POST_RETURN_CALLSITE not in post_return_inner_callsites:
        failures.append(f"missing inner-body callsite {POST_RETURN_CALLSITE} to post-return helper {POST_RETURN_HELPER}")
    if names.get(INNER_BODY) != INNER_BODY_NAME:
        failures.append(f"expected current name {INNER_BODY_NAME} at {INNER_BODY}, got {names.get(INNER_BODY, '<missing>')}")
    if names.get(POST_RETURN_HELPER) != POST_RETURN_HELPER_NAME:
        failures.append(
            f"expected current name {POST_RETURN_HELPER_NAME} at {POST_RETURN_HELPER}, got {names.get(POST_RETURN_HELPER, '<missing>')}"
        )

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "battleengine-weapon-slot0-xrefs.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "slot0-xrefs-vtable-stub-and-named-burst-caller"
        if status == "PASS"
        else "blocked-or-unexpected-slot0-xrefs",
        "inputs": {
            "xrefs": relative(xrefs_path),
            "decompileIndex": relative(decompile_index_path),
        },
        "slot0Stub": {
            "address": SLOT0_STUB,
            "targetName": slot0_rows[0].get("target_name", "") if slot0_rows else "",
            "vtableEntry": VTABLE_SLOT0_ENTRY,
            "xrefRowCount": len(slot0_rows),
            "dataRefCount": len(slot0_data_refs),
            "directCodeRefCount": len(unexpected_direct_slot0_code_refs),
        },
        "innerBody": {
            "address": INNER_BODY,
            "currentName": names.get(INNER_BODY, ""),
            "xrefRowCount": len(inner_rows),
            "namedCallerFunctionAddresses": sorted(
                {normalize_address(row.get("from_function_addr", "")) for row in named_inner_callers}
            ),
            "namedCallerFunctions": sorted({row.get("from_function", "") for row in named_inner_callers}),
            "rawOuterStubCallsites": sorted(set(raw_outer_callsites)),
        },
        "postReturnHelper": {
            "address": POST_RETURN_HELPER,
            "currentName": names.get(POST_RETURN_HELPER, ""),
            "xrefRowCount": len(post_return_rows),
            "innerBodyCallsites": sorted(set(post_return_inner_callsites)),
        },
        "unexpectedDirectSlot0CodeRefs": unexpected_direct_slot0_code_refs,
        "failures": failures,
        "whatIsProven": [
            "The current read-only xref export has one direct DATA reference to 0x00506930 from vtable entry 0x005dfc94.",
            "No direct code reference to the raw 0x00506930 slot-0 stub appears in the checked xref export.",
            "The current read-only xref export shows 0x005069f0 is called by the raw outer-stub callsite 0x005069b6 and by CGeneralVolume__SpawnBurstFromPresetWithFallback at 0x00506010.",
            "The current decompile index names 0x005069f0 as CEngine__SpawnProjectileBurstFromCurrentPreset and 0x005078b0 as CEngine__GetListEntryIdByIndex.",
            "The post-return helper 0x005078b0 is called from the checked inner body at 0x00506b75.",
        ],
        "notProven": [
            "This does not create, rename, or mutate a Ghidra function boundary.",
            "This does not prove exact CWeapon::Fire or CBattleEngine::WeaponFired identity.",
            "This does not prove whether retail weapon fire clears stealth.",
            "This does not rule out indirect, virtual-dispatch, callback, inlined, or runtime-only weapon-fire behavior elsewhere.",
            "This does not patch or launch BEA.exe and does not prove runtime cloak/fire behavior.",
        ],
        "privacy": "Report stores repo-relative filenames, public addresses, current function names, xref counts, and proof boundaries only; raw Ghidra exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_DECOMPILE_INDEX)
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

    report = build_report(xrefs_path=args.xrefs, decompile_index_path=args.decompile_index)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine weapon slot0 xref probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        print(f"Slot0 DATA refs: {report['slot0Stub']['dataRefCount']}")
        print(f"Slot0 direct code refs: {report['slot0Stub']['directCodeRefCount']}")
        print(f"Inner named callers: {', '.join(report['innerBody']['namedCallerFunctions']) or '<none>'}")
        print(f"Inner raw outer-stub callsites: {', '.join(report['innerBody']['rawOuterStubCallsites']) or '<none>'}")
        print(f"Post-return helper inner callsites: {', '.join(report['postReturnHelper']['innerBodyCallsites']) or '<none>'}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
