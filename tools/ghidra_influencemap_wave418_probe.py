#!/usr/bin/env python3
"""Validate the Wave418 CInfluenceMap saved-Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave418-influencemap" / "current"

COMMON_TAGS = {"static-reaudit", "influencemap-wave418", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x0048afb0": {
        "name": "CInfluenceMap__FreeObjectIfPresent",
        "signature": "void __fastcall CInfluenceMap__FreeObjectIfPresent(void * this)",
        "commentTokens": ["manager/map-owned object sets", "+0x08", "+0x18", "runtime influence behavior", "remain unproven"],
        "tags": {"influencemap", "cleanup", "signature-hardened", "comment-hardened"},
    },
    "0x0048b010": {
        "name": "CInfluenceMapManager__Load",
        "signature": "void __thiscall CInfluenceMapManager__Load(void * this, void * mem_buffer)",
        "commentTokens": ["versions 0/1", "0xc4-byte map nodes", "8-byte neighbor links", "runtime AI behavior remain unproven"],
        "tags": {"influencemap", "load", "signature-hardened", "comment-hardened"},
    },
    "0x0048b5f0": {
        "name": "CInfluenceMap__GetTypeName_0048b5f0",
        "signature": "char * __fastcall CInfluenceMap__GetTypeName_0048b5f0(void * this)",
        "commentTokens": ["vtable 0x005dc050 slot 7", "0x0062d658", "CInfluenceNode", "source virtual name remains unproven"],
        "tags": {"influencemap", "vtable-slot", "function-boundary", "string-return", "signature-hardened", "comment-hardened"},
        "instructionEvidence": [("MOV", "0x62d658"), ("RET", "")],
    },
    "0x0048b600": {
        "name": "CInfluenceMap__GetTypeId_0048b600",
        "signature": "int __fastcall CInfluenceMap__GetTypeId_0048b600(void * this)",
        "commentTokens": ["vtable 0x005dc050 slot 8", "0x1e", "source enum label remains unproven"],
        "tags": {"influencemap", "vtable-slot", "function-boundary", "type-id", "signature-hardened", "comment-hardened"},
        "instructionEvidence": [("MOV", "0x1e"), ("RET", "")],
    },
    "0x0048b610": {
        "name": "CInfluenceMap__GetInfluenceRadius_0048b610",
        "signature": "float __fastcall CInfluenceMap__GetInfluenceRadius_0048b610(void * this)",
        "commentTokens": ["vtable 0x005dc050 slot 16", "this+0x94", "nearest-map distance tests", "source field name remains unproven"],
        "tags": {"influencemap", "vtable-slot", "function-boundary", "radius-getter", "signature-hardened", "comment-hardened"},
        "instructionEvidence": [("FLD", "[ECX + 0x94]"), ("RET", "")],
    },
    "0x0048b620": {
        "name": "CInfluenceMap__ResetInfluence",
        "signature": "void __fastcall CInfluenceMap__ResetInfluence(void * this)",
        "commentTokens": ["+0x9c", "+0xa8", "+0xb8", "+0xac/+0xb0", "99999", "runtime AI behavior remain unproven"],
        "tags": {"influencemap", "reset", "signature-hardened", "comment-hardened"},
    },
    "0x0048b660": {
        "name": "CInfluenceMapManager__SkipLoad",
        "signature": "void __stdcall CInfluenceMapManager__SkipLoad(void * mem_buffer)",
        "commentTokens": ["versions 0/1", "without allocating", "file-format field names remain unproven"],
        "tags": {"influencemap", "load", "skip-load", "signature-hardened", "comment-hardened"},
    },
    "0x0048b7d0": {
        "name": "CInfluenceMapManager__PropagateDistances",
        "signature": "void __fastcall CInfluenceMapManager__PropagateDistances(void * this)",
        "commentTokens": ["0x14 passes", "event 0x3e9", "runtime AI behavior remains unproven"],
        "tags": {"influencemap", "distance-propagation", "event-scheduled", "signature-hardened", "comment-hardened"},
    },
    "0x0048b8e0": {
        "name": "CInfluenceMapManager__Update",
        "signature": "void __thiscall CInfluenceMapManager__Update(void * this, float event_time)",
        "commentTokens": ["reschedules event 1000", "10 passes", "0x14 passes", "runtime AI behavior", "remain unproven"],
        "tags": {"influencemap", "update", "event-scheduled", "signature-hardened", "comment-hardened"},
    },
    "0x0048bf70": {
        "name": "CInfluenceMapManager__DecayInfluence",
        "signature": "void __fastcall CInfluenceMapManager__DecayInfluence(void * this)",
        "commentTokens": ["manager+0x18", "frees depleted records", "event 0x3ea", "runtime influence behavior remains unproven"],
        "tags": {"influencemap", "temporary-influence", "event-scheduled", "signature-hardened", "comment-hardened"},
    },
    "0x0048c000": {
        "name": "CInfluenceMapManager__FindNearestMap",
        "signature": "void __thiscall CInfluenceMapManager__FindNearestMap(void * this, float x, float z, float influence_amount, int influence_channel)",
        "commentTokens": ["12-byte temporary influence record", "Manhattan distance", "manager+0x18", "runtime AI behavior remain unproven"],
        "tags": {"influencemap", "temporary-influence", "nearest-map", "signature-hardened", "comment-hardened"},
    },
    "0x0048c2d0": {
        "name": "CInfluenceMapManager__IsEmpty",
        "signature": "bool __fastcall CInfluenceMapManager__IsEmpty(void * this)",
        "commentTokens": ["manager+0x14", "less than one", "runtime AI behavior remains unproven"],
        "tags": {"influencemap", "predicate", "signature-hardened", "comment-hardened"},
    },
    "0x0048c2e0": {
        "name": "CInfluenceMap__scalar_deleting_dtor",
        "signature": "void * __thiscall CInfluenceMap__scalar_deleting_dtor(void * this, byte flags)",
        "commentTokens": ["scalar-deleting destructor", "flags bit 0", "OID__FreeObject", "runtime cleanup behavior remains unproven"],
        "tags": {"influencemap", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"},
    },
    "0x0048c300": {
        "name": "CInfluenceMap__dtor",
        "signature": "void __fastcall CInfluenceMap__dtor(void * this)",
        "commentTokens": ["neighbor set", "this+0x7c", "CComplexThing__dtor_base", "runtime cleanup behavior remains unproven"],
        "tags": {"influencemap", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"},
    },
    "0x0048c350": {
        "name": "CInfluenceMap__DetachNeighborLinks_0048c350",
        "signature": "void __fastcall CInfluenceMap__DetachNeighborLinks_0048c350(void * this)",
        "commentTokens": ["vtable 0x005dc050 slot 2", "this+0x7c", "OID__FreeObject", "source virtual name remains unproven"],
        "tags": {"influencemap", "vtable-slot", "function-boundary", "cleanup", "signature-hardened", "comment-hardened"},
        "instructionEvidence": [("CALL", "0x004e5bd0"), ("CALL", "0x00549220")],
    },
    "0x0048c390": {
        "name": "CInfluenceMap__InitFromComplexThingInit_0048c390",
        "signature": "void __thiscall CInfluenceMap__InitFromComplexThingInit_0048c390(void * this, void * init)",
        "commentTokens": ["not a list-removal body", "init+0x70", "this+0x2c", "CComplexThing__Init", "concrete init layout remains unproven"],
        "tags": {"influencemap", "vtable-slot", "init-wrapper", "owner-corrected", "signature-corrected", "comment-hardened"},
    },
    "0x0048c3b0": {
        "name": "CInfluenceMap__CalculateInfluence",
        "signature": "void __thiscall CInfluenceMap__CalculateInfluence(void * this, int smooth)",
        "commentTokens": ["+0x9c", "+0xa4", "+0xbc", "+0xb4", "+0xb8", "runtime AI behavior remains unproven"],
        "tags": {"influencemap", "influence-calculation", "signature-hardened", "comment-hardened"},
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 13,
    "created": 0,
    "would_create": 4,
    "renamed": 0,
    "would_rename": 3,
    "missing": 0,
    "bad": 0,
}

EXPECTED_APPLY = {
    "updated": 17,
    "skipped": 0,
    "created": 4,
    "would_create": 0,
    "renamed": 3,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

VTABLE_EXPECTED = {
    ("0x005dc050", "1"): ("0x0048c2e0", "CInfluenceMap__scalar_deleting_dtor"),
    ("0x005dc050", "2"): ("0x0048c350", "CInfluenceMap__DetachNeighborLinks_0048c350"),
    ("0x005dc050", "7"): ("0x0048b5f0", "CInfluenceMap__GetTypeName_0048b5f0"),
    ("0x005dc050", "8"): ("0x0048b600", "CInfluenceMap__GetTypeId_0048b600"),
    ("0x005dc050", "9"): ("0x0048c390", "CInfluenceMap__InitFromComplexThingInit_0048c390"),
    ("0x005dc050", "16"): ("0x0048b610", "CInfluenceMap__GetInfluenceRadius_0048b610"),
}

STALE_NAMES = {
    "CInfluenceMap__ScalarDelete",
    "CInfluenceMap__Destructor",
    "CInfluenceMap__RemoveFromList",
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime ai behavior proven",
    "runtime influence behavior proven",
    "runtime cleanup behavior proven",
    "exact source virtual name proven",
    "concrete layout proven",
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
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    if not match:
        return {key: -1 for key in keys}
    return {key: int(value) for key, value in zip(keys, match.groups())}


def check_targets(base: Path = BASE) -> list[str]:
    failures: list[str] = []

    dry_summary = parse_summary(read_text(base / "apply_dry.log"))
    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: {dry_summary} != {EXPECTED_DRY}")

    apply_summary = parse_summary(read_text(base / "apply_apply.log"))
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: {apply_summary} != {EXPECTED_APPLY}")

    metadata = read_tsv(base / "metadata_after.tsv")
    if not metadata:
        failures.append("metadata_after.tsv missing or empty")
    metadata_names = {row.get("name", "") for row in metadata}
    stale_seen = metadata_names & STALE_NAMES
    if stale_seen:
        failures.append(f"stale names still present: {sorted(stale_seen)}")

    tags_rows = read_tsv(base / "tags_after.tsv")
    instructions = read_tsv(base / "instructions_after.tsv")

    for address, expected in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address} missing from metadata_after.tsv")
            continue
        if row.get("status") != "OK":
            failures.append(f"{address} status {row.get('status')} != OK")
        if row.get("name") != expected["name"]:
            failures.append(f"{address} name {row.get('name')} != {expected['name']}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address} signature {row.get('signature')} != {expected['signature']}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address} missing comment token {token!r}")
        lower_comment = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lower_comment:
                failures.append(f"{address} has overclaim token {token!r}")

        tag_row = row_by_address(tags_rows, address)
        if tag_row is None:
            failures.append(f"{address} missing from tags_after.tsv")
        else:
            tags = parse_tags(tag_row.get("tags", ""))
            expected_tags = COMMON_TAGS | set(expected["tags"])  # type: ignore[arg-type]
            missing_tags = expected_tags - tags
            if missing_tags:
                failures.append(f"{address} missing tags {sorted(missing_tags)}")

        for mnemonic, operand in expected.get("instructionEvidence", []):  # type: ignore[union-attr]
            found = False
            for inst in instructions:
                if normalize_address(inst.get("target_addr", "")) != normalize_address(address):
                    continue
                if inst.get("mnemonic") != mnemonic:
                    continue
                if operand and not token_present(inst.get("operands", ""), str(operand)):
                    continue
                found = True
                break
            if not found:
                failures.append(f"{address} missing instruction evidence {mnemonic} {operand}")

    vtable_rows = read_tsv(base / "influencemap_vtable_slots_after.tsv")
    for (vtable, slot), (pointer, name) in VTABLE_EXPECTED.items():
        match = None
        for row in vtable_rows:
            if normalize_address(row.get("vtable", "")) == normalize_address(vtable) and row.get("slot_index") == slot:
                match = row
                break
        if match is None:
            failures.append(f"vtable slot {vtable}[{slot}] missing")
            continue
        if normalize_address(match.get("pointer_addr", "")) != normalize_address(pointer):
            failures.append(f"vtable slot {vtable}[{slot}] pointer mismatch: {match.get('pointer_addr')} != {pointer}")
        if match.get("function_name") != name:
            failures.append(f"vtable slot {vtable}[{slot}] name mismatch: {match.get('function_name')} != {name}")
        if match.get("status") != "OK":
            failures.append(f"vtable slot {vtable}[{slot}] status {match.get('status')} != OK")

    strings = read_tsv(base / "string_0062d658.tsv")
    if not strings or strings[0].get("cstring") != "CInfluenceNode":
        failures.append("0x0062d658 string read-back did not produce CInfluenceNode")

    decompile_index = read_tsv(base / "decompile_after" / "index.tsv")
    ok_decompile = {normalize_address(row.get("address", "")) for row in decompile_index if row.get("status") == "OK"}
    for address in TARGETS:
        if normalize_address(address) not in ok_decompile:
            failures.append(f"{address} missing OK decompile_after row")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    failures = check_targets(args.base)
    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1
    print("PASS ghidra_influencemap_wave418")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
