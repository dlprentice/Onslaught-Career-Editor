#!/usr/bin/env python3
"""Validate the Wave419 InitThing saved-Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave419-initthing-influencemap-init" / "current"

COMMON_TAGS = {"static-reaudit", "initthing-wave419", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x0040e1b0": {
        "name": "CInitThing__CopyFrom",
        "signature": "void __thiscall CInitThing__CopyFrom(void * this, void * source_init)",
        "commentTokens": [
            "CInitThing::Copy",
            "+0xac/+0x1ac/+0x2ac",
            "shared CInitThing vtable slot 0",
            "runtime spawn behavior remains unproven",
        ],
        "decompileTokens": ["+ 0xac", "+ 0x1ac", "+ 0x2ac", "+ 0x3ac", "+ 0x3b0"],
        "tags": {"initthing", "copy-vfunc", "owner-corrected", "signature-corrected", "comment-hardened"},
    },
    "0x0048c650": {
        "name": "InitThing__CreateThingByType",
        "signature": "void * __cdecl InitThing__CreateThingByType(int object_id)",
        "commentTokens": [
            "SpawnInitThing",
            "MT_INIT_THING",
            "InitThing.cpp",
            "CInitThing__ctor",
            "runtime level-load behavior remains unproven",
        ],
        "decompileTokens": ["OID__AllocObject", "s_C__dev_ONSLAUGHT2_InitThing_cpp", "0x005dc1b0", "0x005dc1cc"],
        "tags": {"initthing", "factory", "source-aligned", "signature-hardened", "comment-hardened"},
    },
    "0x0048d8d0": {
        "name": "CSquadInitThing__LoadFromMemBuffer",
        "signature": "void __thiscall CSquadInitThing__LoadFromMemBuffer(void * this, int version, void * mem_buffer)",
        "commentTokens": [
            "CSquadInitThing::Load",
            "+0x3bc",
            "+0x4c0",
            "version > 28",
            "runtime squad spawn behavior remains unproven",
        ],
        "decompileTokens": ["CInitThing__LoadFromMemBuffer", "+ 0x3bc", "+ 0x4c0", "0x1c"],
        "tags": {"initthing", "squad-init", "load", "owner-corrected", "signature-corrected", "comment-hardened"},
    },
    "0x0048dcf0": {
        "name": "CInitThing__ctor",
        "signature": "void * __thiscall CInitThing__ctor(void * this)",
        "commentTokens": [
            "CInitThing::CInitThing",
            "0x005dc1cc",
            "DAT_0067a790",
            "not an InfluenceMap initializer",
            "runtime object construction behavior remains unproven",
        ],
        "decompileTokens": ["DAT_0067a790", "PTR_CInitThing__CopyFrom_005dc1cc", "0xbf800000"],
        "tags": {"initthing", "constructor", "owner-corrected", "signature-corrected", "comment-hardened"},
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 4,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 3,
    "missing": 0,
    "bad": 0,
}

EXPECTED_APPLY = {
    "updated": 4,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 3,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

VTABLE_EXPECTED = {
    ("0x005dc1cc", "0"): ("0x0040e1b0", "CInitThing__CopyFrom"),
    ("0x005dc1cc", "1"): ("0x0040e280", "CInitThing__LoadFromMemBuffer"),
    ("0x005dc1b0", "1"): ("0x0048d8d0", "CSquadInitThing__LoadFromMemBuffer"),
}

STALE_NAMES = {
    "VFuncSlot_00_0040e1b0",
    "CSquadInitThing__VFunc_01_0048d8d0",
    "CInfluenceMap__Init",
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime level-load behavior proven",
    "runtime squad spawn behavior proven",
    "runtime object construction behavior proven",
    "exact retail gameplay behavior proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "function_entry", "vtable", "pointer_addr"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if row.get(key) == wanted:
            return row
    return None


def parse_summary(path: Path) -> dict[str, int] | None:
    text = read_text(path)
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+"
        r"renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def check_summary(base: Path, failures: list[str]) -> None:
    for filename, expected in (("apply_dry.log", EXPECTED_DRY), ("apply_apply.log", EXPECTED_APPLY)):
        actual = parse_summary(base / filename)
        if actual is None:
            failures.append(f"{filename}: missing SUMMARY")
        elif actual != expected:
            failures.append(f"{filename}: summary mismatch {actual} != {expected}")


def decompile_file_for(base: Path, address: str, name: str) -> Path:
    clean = address.lower().replace("0x", "")
    return base / "decompile_after" / f"{clean}_{name}.c"


def check_targets(base: Path = BASE) -> list[str]:
    failures: list[str] = []
    check_summary(base, failures)

    metadata = read_tsv(base / "metadata_after.tsv")
    tags = read_tsv(base / "tags_after.tsv")
    vtable = read_tsv(base / "vtable_slots_after.tsv")

    if not metadata:
        failures.append("metadata_after.tsv missing or empty")
    if not tags:
        failures.append("tags_after.tsv missing or empty")
    if not vtable:
        failures.append("vtable_slots_after.tsv missing or empty")

    all_metadata_names = {row.get("name", "") for row in metadata}
    stale_present = sorted(name for name in STALE_NAMES if name in all_metadata_names)
    if stale_present:
        failures.append("stale names still present: " + ", ".join(stale_present))

    for address, expected in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')} != {expected['name']}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address}: signature mismatch {row.get('signature')} != {expected['signature']}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[union-attr]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: overclaim token present {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            actual_tags = {tag for tag in tag_row.get("tags", "").split(";") if tag}
            expected_tags = COMMON_TAGS | set(expected["tags"])  # type: ignore[arg-type]
            missing_tags = sorted(expected_tags - actual_tags)
            if missing_tags:
                failures.append(f"{address}: missing tags {', '.join(missing_tags)}")

        decompile_text = read_text(decompile_file_for(base, address, str(expected["name"])))
        if not decompile_text:
            failures.append(f"{address}: missing decompile after file")
        else:
            for token in expected["decompileTokens"]:  # type: ignore[union-attr]
                if not token_present(decompile_text, str(token)):
                    failures.append(f"{address}: missing decompile token {token!r}")

    for (vtable_addr, slot), (pointer, name) in VTABLE_EXPECTED.items():
        match = None
        for row in vtable:
            if row.get("vtable") == normalize_address(vtable_addr) and row.get("slot_index") == slot:
                match = row
                break
        if match is None:
            failures.append(f"vtable slot {vtable_addr}[{slot}] missing")
            continue
        if match.get("pointer_addr") != normalize_address(pointer):
            failures.append(f"vtable slot {vtable_addr}[{slot}] pointer mismatch {match.get('pointer_addr')} != {pointer}")
        if match.get("function_name") != name:
            failures.append(f"vtable slot {vtable_addr}[{slot}] name mismatch {match.get('function_name')} != {name}")
        if match.get("status") != "OK":
            failures.append(f"vtable slot {vtable_addr}[{slot}] status mismatch {match.get('status')} != OK")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    failures = check_targets(args.base)
    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
