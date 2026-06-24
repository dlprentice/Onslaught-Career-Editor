#!/usr/bin/env python3
"""Validate Wave498 CSentinel static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave498-sentinel-safeside-004de1d0"

COMMON_TAGS = {"static-reaudit", "sentinel-wave498", "retail-binary-evidence"}

TARGETS = {
    "0x004dea50": {
        "name": "CSentinel__Init",
        "signature_tokens": ("void", "__thiscall", "CSentinel__Init", "void * this", "void * init_data"),
        "tags": COMMON_TAGS | {"sentinel", "init", "boundary-recovered", "vtable-slot-0", "name-corrected"},
        "comment_tokens": (
            "CSentinel primary table 0x005e0904 slot 0",
            "RET 0x4 confirms one init_data",
            "delegates to CGroundUnit__Init",
            "CMCSentinel motion control at this+0x70",
            "this+0x208 and this+0x13c",
            "runtime sentinel behavior",
        ),
        "decompile_tokens": (
            "CGroundUnit__Init(this,init_data)",
            "CMCSentinel__Constructor",
            "CTerrainGuide__ctor_like_004f1ec0",
            "CWarspite__Init(this,init_data)",
            "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk",
            "return;",
        ),
    },
    "0x004dec00": {
        "name": "CSentinel__ScalarDeletingDestructor",
        "signature_tokens": (
            "void *",
            "__thiscall",
            "CSentinel__ScalarDeletingDestructor",
            "void * this",
            "byte flags",
        ),
        "tags": COMMON_TAGS
        | {"sentinel", "scalar-deleting-destructor", "vtable-slot-0", "name-corrected", "signature-corrected"},
        "comment_tokens": (
            "secondary Sentinel table 0x005deca0 slot 0",
            "calls CSentinel__Destructor(this)",
            "CDXMemoryManager__Free",
            "flags bit 0",
            "returns this",
        ),
        "decompile_tokens": (
            "CSentinel__Destructor(this)",
            "flags & 1",
            "CDXMemoryManager__Free",
            "return this",
        ),
    },
    "0x004dec20": {
        "name": "CSentinel__Destructor",
        "signature_tokens": ("void", "__fastcall", "CSentinel__Destructor", "void * this"),
        "tags": COMMON_TAGS | {"sentinel", "destructor", "signature-corrected", "comment-hardened"},
        "comment_tokens": (
            "base CMonitor-style vtable 0x005d8d1c",
            "this+0x28",
            "this+0x24",
            "this+0x0c",
            "CMonitor__Shutdown",
        ),
        "decompile_tokens": ("PTR_LAB_005d8d1c", "CSPtrSet__Remove", "CMonitor__Shutdown(this)"),
    },
    "0x004decc0": {
        "name": "CSentinel__UpdateFlamethrowers",
        "signature_tokens": ("void", "__fastcall", "CSentinel__UpdateFlamethrowers", "void * this"),
        "tags": COMMON_TAGS
        | {"sentinel", "flamethrower", "vtable-slot-57", "signature-corrected", "comment-hardened"},
        "comment_tokens": (
            "Sentinel table 0x005e0904 slot 57",
            "this+0x17c linked list",
            "Sentinel Flamethrower",
            "CSentinel__CheckWeaponSlot",
            "spawns a projectile burst",
        ),
        "decompile_tokens": (
            "CGroundUnit__UpdateLinkedEffectsByHeightClearance(this)",
            "s_Sentinel_Flamethrower_00632248",
            "CUnit__IsEligibleByDistanceBucketOrRange",
            "CSentinel__CheckWeaponSlot(this,weapon_context)",
            "ProjectileBurst__SpawnFromPercentBucketFallback",
        ),
    },
    "0x004ded30": {
        "name": "CSentinel__Activate",
        "signature_tokens": ("void", "__fastcall", "CSentinel__Activate", "void * this"),
        "tags": COMMON_TAGS
        | {"sentinel", "activate", "animation", "vtable-slot-13", "signature-corrected", "comment-hardened"},
        "comment_tokens": (
            "Sentinel table 0x005e0904 slot 13",
            "activate animation",
            "animation index",
            "vtable slot at +0xf0",
        ),
        "decompile_tokens": ("s_activate_00632260", "CMesh__FindAnimationIndexByName", "+ 0xf0"),
    },
    "0x004ded60": {
        "name": "CSentinel__Deactivate",
        "signature_tokens": ("int", "__fastcall", "CSentinel__Deactivate", "void * this"),
        "tags": COMMON_TAGS
        | {"sentinel", "deactivate", "animation", "vtable-slot-50", "signature-corrected", "comment-hardened"},
        "comment_tokens": (
            "Sentinel table 0x005e0904 slot 50",
            "current animation state",
            "activate animation index",
            "looping inactive animation",
            "returns 0",
        ),
        "decompile_tokens": ("s_activate_00632260", "s_inactive_0063223c", "VFuncSlot_22_004fd6a0", "return 0"),
    },
    "0x004dee00": {
        "name": "CSentinel__CheckWeaponSlot",
        "signature_tokens": (
            "int",
            "__thiscall",
            "CSentinel__CheckWeaponSlot",
            "void * this",
            "void * weapon_context",
        ),
        "tags": COMMON_TAGS
        | {"sentinel", "weapon-slot", "flamethrower", "signature-corrected", "comment-hardened"},
        "comment_tokens": (
            "weapon_context+0xac values 2..9",
            "slot ids 9..16",
            "this+0x19c linked list",
            "+0x270 matching that slot",
            "runtime firing behavior",
        ),
        "decompile_tokens": (
            "weapon_context + 0xac",
            "this + 0x19c",
            "+ 0x270",
            "return 0",
            "return 1",
        ),
    },
}

VTABLE_EXPECTATIONS = {
    ("005e0904", "0"): ("004dea50", "CSentinel__Init", "OK"),
    ("005e0904", "13"): ("004ded30", "CSentinel__Activate", "OK"),
    ("005e0904", "50"): ("004ded60", "CSentinel__Deactivate", "OK"),
    ("005e0904", "57"): ("004decc0", "CSentinel__UpdateFlamethrowers", "OK"),
    ("005deca0", "0"): ("004dec00", "CSentinel__ScalarDeletingDestructor", "OK"),
}

XREF_EXPECTATIONS = (
    ("004dea50", "005e0904", "<no_function>", "DATA"),
    ("004dec00", "005deca0", "<no_function>", "DATA"),
    ("004dec20", "004dec00", "CSentinel__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),
    ("004decc0", "005e09e8", "<no_function>", "DATA"),
    ("004ded30", "005e0938", "<no_function>", "DATA"),
    ("004ded60", "005e09cc", "<no_function>", "DATA"),
    ("004dee00", "004decc0", "CSentinel__UpdateFlamethrowers", "UNCONDITIONAL_CALL"),
)

EXPECTED_LOG_SUMMARIES = {
    "apply_sentinel_dry.log": {
        "updated": 0,
        "skipped": 6,
        "created": 0,
        "would_create": 1,
        "renamed": 0,
        "would_rename": 1,
        "missing": 0,
        "bad": 0,
    },
    "apply_sentinel_apply.log": {
        "updated": 7,
        "skipped": 0,
        "created": 1,
        "would_create": 0,
        "renamed": 1,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_sentinel_void_apply.log": {
        "updated": 1,
        "skipped": 6,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_sentinel_int_apply.log": {
        "updated": 1,
        "skipped": 6,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_sentinel_final_verify_dry.log": {
        "updated": 0,
        "skipped": 7,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}


def load_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing TSV: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def addr_key(value: str) -> str:
    value = value.strip().lower()
    if not value.startswith("0x"):
        value = "0x" + value
    return value


def require_tokens(text: str, tokens: tuple[str, ...], label: str) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise AssertionError(f"{label} missing tokens: {missing}")


def decompile_text(base: Path, address: str, expected_name: str) -> str:
    stem = address[2:].lower()
    decomp_dir = base / "post-decomp"
    preferred = sorted(decomp_dir.glob(f"{stem}_{expected_name}*.c"))
    candidates = preferred or sorted(decomp_dir.glob(f"{stem}_*.c"))
    if not candidates:
        raise AssertionError(f"missing post-decompile for {address}")
    return candidates[0].read_text(encoding="utf-8", errors="replace")


def check_metadata(base: Path) -> None:
    rows = {addr_key(row["address"]): row for row in load_tsv(base / "post_metadata.tsv")}
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if row is None:
            raise AssertionError(f"missing metadata row for {address}")
        if row["status"] != "OK":
            raise AssertionError(f"{address} metadata status {row['status']}")
        if row["name"] != spec["name"]:
            raise AssertionError(f"{address} name {row['name']} != {spec['name']}")
        require_tokens(row["signature"], spec["signature_tokens"], f"{address} signature")
        require_tokens(row["comment"], spec["comment_tokens"], f"{address} comment")


def check_tags(base: Path) -> None:
    rows = {addr_key(row["address"]): row for row in load_tsv(base / "post_tags.tsv")}
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if row is None:
            raise AssertionError(f"missing tag row for {address}")
        tags = set(filter(None, row["tags"].split(";")))
        missing = sorted(spec["tags"] - tags)
        if missing:
            raise AssertionError(f"{address} missing tags: {missing}")


def check_decompiles(base: Path) -> None:
    for address, spec in TARGETS.items():
        text = decompile_text(base, address, spec["name"])
        require_tokens(text, spec["decompile_tokens"], f"{address} decompile")


def check_xrefs(base: Path) -> None:
    rows = load_tsv(base / "post_xrefs.tsv")
    for target, from_function_addr, from_function, ref_type in XREF_EXPECTATIONS:
        found = any(
            row["target_addr"].lower() == target.lower()
            and from_function_addr.lower() in {row["from_addr"].lower(), row["from_function_addr"].lower()}
            and row["from_function"] == from_function
            and row["ref_type"] == ref_type
            for row in rows
        )
        if not found:
            raise AssertionError(f"missing xref {target} from {from_function_addr} {from_function} {ref_type}")


def check_vtables(base: Path) -> None:
    rows = load_tsv(base / "post_vtable.tsv")
    by_slot = {(row["vtable"].lower(), row["slot_index"]): row for row in rows}
    for key, (pointer, name, status) in VTABLE_EXPECTATIONS.items():
        row = by_slot.get((key[0].lower(), key[1]))
        if row is None:
            raise AssertionError(f"missing vtable slot {key[0]} slot {key[1]}")
        if row["pointer_addr"].lower() != pointer.lower():
            raise AssertionError(f"{key[0]} slot {key[1]} pointer {row['pointer_addr']} != {pointer}")
        if row["function_name"] != name:
            raise AssertionError(f"{key[0]} slot {key[1]} name {row['function_name']} != {name}")
        if row["status"] != status:
            raise AssertionError(f"{key[0]} slot {key[1]} status {row['status']} != {status}")


def check_logs(base: Path) -> None:
    summary_re = re.compile(r"SUMMARY:?\s+(.+)")
    for name, expected in EXPECTED_LOG_SUMMARIES.items():
        path = base / name
        if not path.exists():
            raise AssertionError(f"missing log: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        if "REPORT: Save succeeded" not in text:
            raise AssertionError(f"{name} missing save success")
        match = summary_re.search(text)
        if not match:
            raise AssertionError(f"{name} missing SUMMARY line")
        actual = {}
        for token in match.group(1).split():
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            actual[key] = int(value)
        for key, expected_value in expected.items():
            actual_value = actual.get(key)
            if actual_value != expected_value:
                raise AssertionError(f"{name} {key} {actual_value} != {expected_value}")


def check(args: argparse.Namespace) -> int:
    base = Path(args.base).resolve()
    check_metadata(base)
    check_tags(base)
    check_decompiles(base)
    check_xrefs(base)
    check_vtables(base)
    check_logs(base)
    print(f"Wave498 Sentinel probe PASS ({len(TARGETS)} targets)")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=str(DEFAULT_BASE))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("use --check")
    return check(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
