#!/usr/bin/env python3
"""Validate Wave459 OID/object-init static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave459-oid-object-current"
COMMON_TAGS = {"static-reaudit", "oid-object-wave459", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 12,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 8,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 12,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 8,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 12,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004bf090": target(
        "OID__CreateObject",
        "void * __cdecl OID__CreateObject(int object_id)",
        [
            "main OID object factory",
            "object_id switch",
            "OID__AllocObject",
            "[maintainer-local-source-export-root]\\oids.cpp",
            "Runtime object construction",
        ],
        ["oid", "factory", "signature-corrected", "comment-hardened"],
        ["switch(object_id)", "OID__AllocObject", "OID__InitTargetData", "OID__InitBaseObject"],
    ),
    "0x004bfa60": target(
        "OID__InitTargetData",
        "void __fastcall OID__InitTargetData(void * target_data)",
        [
            "target tracking data",
            "0xffffffff",
            "0xbf800000",
            "-1.0f",
            "Runtime targeting behavior",
        ],
        ["oid", "target-data", "signature-corrected", "comment-hardened"],
        ["0xffffffff", "0xbf800000"],
    ),
    "0x004bfab0": target(
        "OID__RenderWithState1BOverride",
        "void __thiscall OID__RenderWithState1BOverride(void * this, uint render_flags)",
        [
            "render state 0x1b",
            "one stack render_flags argument",
            "CUnit__RenderWithDistanceFade",
            "CThing__Render",
            "Runtime rendering behavior",
        ],
        ["oid", "render", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["RenderState_Set(0x1b,0)", "CThing__Render", "CUnit__RenderWithDistanceFade"],
    ),
    "0x004bfce0": target(
        "CTree__scalar_deleting_dtor",
        "void * __thiscall CTree__scalar_deleting_dtor(void * this, byte flags)",
        [
            "CTree vtable slot 1",
            "scalar-deleting destructor wrapper",
            "CTree__scalar_deleting_dtor_004f63c0",
            "flags & 1",
            "Runtime tree cleanup behavior",
        ],
        ["ctree", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["CTree__scalar_deleting_dtor_004f63c0", "CDXMemoryManager__Free"],
    ),
    "0x004bfd00": target(
        "CActorBase__shared_scalar_deleting_dtor_004bfd00",
        "void * __thiscall CActorBase__shared_scalar_deleting_dtor_004bfd00(void * this, byte flags)",
        [
            "shared vtable slot 1",
            "CActor__dtor_base",
            "three vtable DATA xrefs",
            "flags & 1",
            "Runtime shared cleanup behavior",
        ],
        ["actor-base", "shared-wrapper", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["CActor__dtor_base", "CDXMemoryManager__Free"],
    ),
    "0x004bfd20": target(
        "OID__InitBaseObject",
        "void * __fastcall OID__InitBaseObject(void * object)",
        [
            "base object initializer",
            "CThing__ctor_like_004f3e10",
            "CActor__HandleEvent",
            "CActor__GetRenderPos",
            "Runtime base-object behavior",
        ],
        ["oid", "base-object", "signature-corrected", "comment-hardened"],
        ["CThing__ctor_like_004f3e10", "PTR_CActor__HandleEvent", "PTR_CActor__GetRenderPos"],
    ),
    "0x004bfd40": target(
        "CRocket__scalar_deleting_dtor",
        "void * __thiscall CRocket__scalar_deleting_dtor(void * this, byte flags)",
        [
            "CRocket vtable slot 1",
            "CRocket__DestroyArrayWithCallback",
            "flags & 1",
            "optionally frees",
            "Runtime rocket cleanup behavior",
        ],
        ["rocket", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["CRocket__DestroyArrayWithCallback", "CDXMemoryManager__Free"],
    ),
    "0x004bfd60": target(
        "CWaypoint__scalar_deleting_dtor",
        "void * __thiscall CWaypoint__scalar_deleting_dtor(void * this, byte flags)",
        [
            "CWaypoint vtable slot 1",
            "CWaypoint__RemoveOwnerLinkAndResetBaseThing",
            "flags & 1",
            "optionally frees",
            "Runtime waypoint cleanup behavior",
        ],
        ["waypoint", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["CWaypoint__RemoveOwnerLinkAndResetBaseThing", "CDXMemoryManager__Free"],
    ),
    "0x004bfd80": target(
        "CSpawnerThing__scalar_deleting_dtor",
        "void * __thiscall CSpawnerThing__scalar_deleting_dtor(void * this, byte flags)",
        [
            "CSpawnerThing vtable slot 1",
            "CSpawnerThing__RemoveOwnerLinkAndResetComplexThing",
            "flags & 1",
            "optionally frees",
            "Runtime spawner cleanup behavior",
        ],
        ["spawner-thing", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["CSpawnerThing__RemoveOwnerLinkAndResetComplexThing", "CDXMemoryManager__Free"],
    ),
    "0x004bfda0": target(
        "CSphereTrigger__scalar_deleting_dtor",
        "void * __thiscall CSphereTrigger__scalar_deleting_dtor(void * this, byte flags)",
        [
            "CSphereTrigger vtable slot 1",
            "CSphereTrigger__ClearTrackedSetRemoveGlobalAndResetBase",
            "flags & 1",
            "optionally frees",
            "Runtime sphere-trigger cleanup behavior",
        ],
        ["sphere-trigger", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["CSphereTrigger__ClearTrackedSetRemoveGlobalAndResetBase", "CDXMemoryManager__Free"],
    ),
    "0x004bfdc0": target(
        "CWingmanStart__scalar_deleting_dtor",
        "void * __thiscall CWingmanStart__scalar_deleting_dtor(void * this, byte flags)",
        [
            "CWingmanStart vtable slot 1",
            "CWingmanStart__RemoveOwnerLinkAndResetComplexThing",
            "flags & 1",
            "optionally frees",
            "Runtime wingman-start cleanup behavior",
        ],
        ["wingman-start", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["CWingmanStart__RemoveOwnerLinkAndResetComplexThing", "CDXMemoryManager__Free"],
    ),
    "0x004bfde0": target(
        "CEscapePod__scalar_deleting_dtor",
        "void * __thiscall CEscapePod__scalar_deleting_dtor(void * this, byte flags)",
        [
            "CEscapePod vtable slot 1",
            "CEscapePod__RemoveGlobalAndResetActorBase",
            "flags & 1",
            "optionally frees",
            "Runtime escape-pod cleanup behavior",
        ],
        ["escape-pod", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["CEscapePod__RemoveGlobalAndResetActorBase", "CDXMemoryManager__Free"],
    ),
}

EXPECTED_XREF_EDGES = {
    ("0x004bfa60", "0x004bf183", "OID__CreateObject"),
    ("0x004bfd20", "0x004bf2d1", "OID__CreateObject"),
    ("0x004bfd20", "0x004bf36a", "OID__CreateObject"),
    ("0x004bfab0", "0x005dda68", "<no_function>"),
    ("0x004bfce0", "0x005dd9dc", "<no_function>"),
    ("0x004bfd00", "0x005dd5f4", "<no_function>"),
    ("0x004bfd00", "0x005ded4c", "<no_function>"),
    ("0x004bfd00", "0x005e45e4", "<no_function>"),
    ("0x004bfd40", "0x005dd45c", "<no_function>"),
    ("0x004bfd60", "0x005dd2f4", "<no_function>"),
    ("0x004bfd80", "0x005dd170", "<no_function>"),
    ("0x004bfda0", "0x005dce68", "<no_function>"),
    ("0x004bfdc0", "0x005dcb5c", "<no_function>"),
    ("0x004bfde0", "0x005dc834", "<no_function>"),
}

INSTRUCTION_TOKENS = {
    "0x004bf090": ["OID__CreateObject\tCALL\t0x005490e0", "OID__CreateObject\tCALL\t0x004bfa60", "OID__CreateObject\tCALL\t0x004bfd20"],
    "0x004bfab0": ["OID__RenderWithState1BOverride\tCALL\t0x00513bc0", "OID__RenderWithState1BOverride\tCALL\t0x004f36d0", "OID__RenderWithState1BOverride\tRET\t0x4"],
    "0x004bfce0": ["CTree__scalar_deleting_dtor\tCALL\t0x004f63c0", "CTree__scalar_deleting_dtor\tCALL\t0x00549220", "CTree__scalar_deleting_dtor\tRET\t0x4"],
    "0x004bfd00": ["CActorBase__shared_scalar_deleting_dtor_004bfd00\tCALL\t0x004df520", "CActorBase__shared_scalar_deleting_dtor_004bfd00\tCALL\t0x00549220", "CActorBase__shared_scalar_deleting_dtor_004bfd00\tRET\t0x4"],
    "0x004bfd40": ["CRocket__scalar_deleting_dtor\tCALL\t0x004bfe10", "CRocket__scalar_deleting_dtor\tCALL\t0x00549220", "CRocket__scalar_deleting_dtor\tRET\t0x4"],
    "0x004bfd60": ["CWaypoint__scalar_deleting_dtor\tCALL\t0x004bfe70", "CWaypoint__scalar_deleting_dtor\tCALL\t0x00549220", "CWaypoint__scalar_deleting_dtor\tRET\t0x4"],
    "0x004bfd80": ["CSpawnerThing__scalar_deleting_dtor\tCALL\t0x004bfed0", "CSpawnerThing__scalar_deleting_dtor\tCALL\t0x00549220", "CSpawnerThing__scalar_deleting_dtor\tRET\t0x4"],
    "0x004bfda0": ["CSphereTrigger__scalar_deleting_dtor\tCALL\t0x004bff40", "CSphereTrigger__scalar_deleting_dtor\tCALL\t0x00549220", "CSphereTrigger__scalar_deleting_dtor\tRET\t0x4"],
    "0x004bfdc0": ["CWingmanStart__scalar_deleting_dtor\tCALL\t0x004bffa0", "CWingmanStart__scalar_deleting_dtor\tCALL\t0x00549220", "CWingmanStart__scalar_deleting_dtor\tRET\t0x4"],
    "0x004bfde0": ["CEscapePod__scalar_deleting_dtor\tCALL\t0x004c0000", "CEscapePod__scalar_deleting_dtor\tCALL\t0x00549220", "CEscapePod__scalar_deleting_dtor\tRET\t0x4"],
}

VTABLE_EXPECTED = {
    ("0x005dda64", "1", "0x004bfab0", "OID__RenderWithState1BOverride"),
    ("0x005dd9d8", "1", "0x004bfce0", "CTree__scalar_deleting_dtor"),
    ("0x005dd5f0", "1", "0x004bfd00", "CActorBase__shared_scalar_deleting_dtor_004bfd00"),
    ("0x005ded48", "1", "0x004bfd00", "CActorBase__shared_scalar_deleting_dtor_004bfd00"),
    ("0x005e45e0", "1", "0x004bfd00", "CActorBase__shared_scalar_deleting_dtor_004bfd00"),
    ("0x005dd458", "1", "0x004bfd40", "CRocket__scalar_deleting_dtor"),
    ("0x005dd2f0", "1", "0x004bfd60", "CWaypoint__scalar_deleting_dtor"),
    ("0x005dd16c", "1", "0x004bfd80", "CSpawnerThing__scalar_deleting_dtor"),
    ("0x005dce64", "1", "0x004bfda0", "CSphereTrigger__scalar_deleting_dtor"),
    ("0x005dcb58", "1", "0x004bfdc0", "CWingmanStart__scalar_deleting_dtor"),
    ("0x005dc830", "1", "0x004bfde0", "CEscapePod__scalar_deleting_dtor"),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime object construction proven",
    "runtime rendering behavior proven",
    "runtime cleanup behavior proven",
    "source identity proven",
    "exact layout proven",
    "exact class proven",
    "fully re'ed",
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


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry", "vtable", "pointer_addr"):
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


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    wanted = normalize_address(address)[2:]
    for path in directory.glob(f"{wanted}_*.c"):
        return read_text(path)
    return ""


def parse_summary(text: str) -> dict[str, int]:
    match = re.search(r"SUMMARY\s+(.+)", text)
    if not match:
        return {}
    result: dict[str, int] = {}
    for key, value in re.findall(r"([a-z_]+)=(\d+)", match.group(1)):
        result[key] = int(value)
    return result


def check_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    actual = parse_summary(read_text(path))
    if not actual:
        failures.append(f"{path.name}: missing SUMMARY")
        return
    for key, value in expected.items():
        if actual.get(key) != value:
            failures.append(f"{path.name}: expected {key}={value}, got {actual.get(key)}")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    if len(rows) < len(TARGETS):
        failures.append(f"post_metadata.tsv: expected at least {len(TARGETS)} rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"post_metadata.tsv: missing {address}")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: name {row.get('name')} != {expected['name']}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address}: signature {row.get('signature')} != {expected['signature']}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    seen: dict[str, set[str]] = {}
    for row in rows:
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        seen.setdefault(row.get("address", ""), set()).update(tags)
    for address, expected in TARGETS.items():
        actual = seen.get(normalize_address(address), set())
        for tag in expected["tags"]:
            if tag not in actual:
                failures.append(f"{address}: missing tag {tag}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    edges = {
        (
            row.get("target_addr", ""),
            row.get("from_addr", ""),
            row.get("from_function", ""),
        )
        for row in rows
    }
    for edge in EXPECTED_XREF_EDGES:
        if edge not in edges:
            failures.append(f"post_xrefs.tsv: missing edge {edge}")


def check_vtables(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_vtable_slots.tsv")
    slots = {
        (
            row.get("vtable", ""),
            row.get("slot_index", ""),
            row.get("pointer_addr", ""),
            row.get("function_name", ""),
        )
        for row in rows
    }
    for expected in VTABLE_EXPECTED:
        if expected not in slots:
            failures.append(f"post_vtable_slots.tsv: missing slot {expected}")


def check_decompile_and_instructions(base: Path, failures: list[str]) -> None:
    instruction_text = read_text(base / "post_instructions.tsv")
    for address, tokens in INSTRUCTION_TOKENS.items():
        for token in tokens:
            if not token_present(instruction_text, token):
                failures.append(f"{address}: post_instructions.tsv missing token {token!r}")
    for address, expected in TARGETS.items():
        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing post decompile export")
            continue
        for token in expected["decompileTokens"]:
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, failures)
    check_summary(base / "verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_vtables(base, failures)
    check_decompile_and_instructions(base, failures)
    return ("FAIL" if failures else "PASS", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Accepted for npm-script consistency")
    parser.add_argument("--base", type=Path, default=BASE, help="Wave459 artifact directory")
    args = parser.parse_args()

    status, failures = run_checks(args.base)
    print(f"STATUS {status}")
    for failure in failures:
        print(f"FAIL {failure}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
