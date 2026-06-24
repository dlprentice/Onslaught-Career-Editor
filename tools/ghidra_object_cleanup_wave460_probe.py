#!/usr/bin/env python3
"""Validate Wave460 object cleanup static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave460-object-cleanup-current"
COMMON_TAGS = {"static-reaudit", "object-cleanup-wave460", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 10,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 10,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 10,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 10,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 10,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(name: str, signature: str, comment_tokens: list[str], tags: list[str], decompile_tokens: list[str]) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004bfe00": target(
        "CUnit__dtor_base_Thunk_004bfe00",
        "void __fastcall CUnit__dtor_base_Thunk_004bfe00(void * this)",
        ["jump thunk", "CUnit__dtor_base", "unwind cleanup paths", "Runtime unit cleanup"],
        ["cunit", "dtor-base", "thunk", "signature-corrected", "comment-hardened"],
        ["CUnit__dtor_base"],
    ),
    "0x004bfe10": target(
        "CRocket__dtor_base",
        "void __fastcall CRocket__dtor_base(void * this)",
        ["CRocket destructor-base", "+0xec", "DestroyArrayWithCallback", "CActor__dtor_base", "Runtime rocket cleanup"],
        ["rocket", "dtor-base", "signature-corrected", "comment-hardened"],
        ["DestroyArrayWithCallback", "CActor__dtor_base"],
    ),
    "0x004bfe70": target(
        "CWaypoint__dtor_base",
        "void __fastcall CWaypoint__dtor_base(void * this)",
        ["CWaypoint destructor-base", "+0x3c", "CSPtrSet__Remove", "CThing__ctor_like_004f3640", "Runtime waypoint cleanup"],
        ["waypoint", "dtor-base", "signature-corrected", "comment-hardened"],
        ["CSPtrSet__Remove", "CThing__ctor_like_004f3640"],
    ),
    "0x004bfed0": target(
        "CSpawnerThing__dtor_base",
        "void __fastcall CSpawnerThing__dtor_base(void * this)",
        ["CSpawnerThing destructor-base", "+0x7c", "CSPtrSet__Remove", "CComplexThing__dtor_base", "Runtime spawner cleanup"],
        ["spawner-thing", "dtor-base", "signature-corrected", "comment-hardened"],
        ["CSPtrSet__Remove", "CComplexThing__dtor_base"],
    ),
    "0x004bff30": target(
        "CComplexThing__dtor_base_Thunk_004bff30",
        "void __fastcall CComplexThing__dtor_base_Thunk_004bff30(void * this)",
        ["jump thunk", "CComplexThing__dtor_base", "Unwind", "VFuncSlot_01_004e5e50", "Runtime complex-thing cleanup"],
        ["complex-thing", "dtor-base", "thunk", "signature-corrected", "comment-hardened"],
        ["CComplexThing__dtor_base"],
    ),
    "0x004bff40": target(
        "CSphereTrigger__dtor_base",
        "void __fastcall CSphereTrigger__dtor_base(void * this)",
        ["CSphereTrigger destructor-base", "+0x8c CSPtrSet", "+0x7c", "CParticleManager__RemoveFromGlobalList"],
        ["sphere-trigger", "dtor-base", "signature-corrected", "comment-hardened"],
        ["CSPtrSet__Clear", "CParticleManager__RemoveFromGlobalList", "CComplexThing__dtor_base"],
    ),
    "0x004bffa0": target(
        "CWingmanStart__dtor_base",
        "void __fastcall CWingmanStart__dtor_base(void * this)",
        ["CWingmanStart destructor-base", "+0x7c", "CSPtrSet__Remove", "CComplexThing__dtor_base", "Runtime wingman-start cleanup"],
        ["wingman-start", "dtor-base", "signature-corrected", "comment-hardened"],
        ["CSPtrSet__Remove", "CComplexThing__dtor_base"],
    ),
    "0x004c0000": target(
        "CEscapePod__dtor_base",
        "void __fastcall CEscapePod__dtor_base(void * this)",
        ["CEscapePod destructor-base", "+0xe0", "CParticleManager__RemoveFromGlobalList", "CActor__dtor_base", "Runtime escape-pod cleanup"],
        ["escape-pod", "dtor-base", "signature-corrected", "comment-hardened"],
        ["CParticleManager__RemoveFromGlobalList", "CActor__dtor_base"],
    ),
    "0x004f84e0": target(
        "CUnit__dtor_base",
        "void __fastcall CUnit__dtor_base(void * this)",
        ["CUnit destructor-base", "CActor__dtor_base", "CSPtrSet-style lists", "linked unit", "Runtime unit cleanup"],
        ["cunit", "dtor-base", "signature-corrected", "comment-hardened"],
        ["CActor__dtor_base", "CSPtrSet__Clear", "CUnit__FinalizeLinkedUnitStateAndClear"],
    ),
    "0x0050ee90": target(
        "CUnit__scalar_deleting_dtor",
        "void * __thiscall CUnit__scalar_deleting_dtor(void * this, byte flags)",
        ["CUnit vtable slot 1", "CUnit__dtor_base_Thunk_004bfe00", "flags & 1", "CDXMemoryManager__Free", "Runtime unit cleanup"],
        ["cunit", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["CUnit__dtor_base_Thunk_004bfe00", "CDXMemoryManager__Free"],
    ),
}

EXPECTED_XREF_EDGES = {
    ("0x004bfe00", "0x0050ee93", "CUnit__scalar_deleting_dtor"),
    ("0x004bfe10", "0x004bfd43", "CRocket__scalar_deleting_dtor"),
    ("0x004bfe70", "0x004bfd63", "CWaypoint__scalar_deleting_dtor"),
    ("0x004bfed0", "0x004bfd83", "CSpawnerThing__scalar_deleting_dtor"),
    ("0x004bff30", "0x004e5e53", "VFuncSlot_01_004e5e50"),
    ("0x004bff40", "0x004bfda3", "CSphereTrigger__scalar_deleting_dtor"),
    ("0x004bffa0", "0x004bfdc3", "CWingmanStart__scalar_deleting_dtor"),
    ("0x004c0000", "0x004bfde3", "CEscapePod__scalar_deleting_dtor"),
}

INSTRUCTION_TOKENS = {
    "0x004bfe00": ["CUnit__dtor_base_Thunk_004bfe00\tJMP\t0x004f84e0"],
    "0x004bfe10": ["CRocket__dtor_base\tCALL\t0x0055db0a", "CRocket__dtor_base\tCALL\t0x004013d0"],
    "0x004bfe70": ["CWaypoint__dtor_base\tCALL\t0x004e5bd0", "CWaypoint__dtor_base\tCALL\t0x004f3640"],
    "0x004bfed0": ["CSpawnerThing__dtor_base\tCALL\t0x004e5bd0", "CSpawnerThing__dtor_base\tCALL\t0x004f3f00"],
    "0x004bff30": ["CComplexThing__dtor_base_Thunk_004bff30\tJMP\t0x004f3f00"],
    "0x004bff40": ["CSphereTrigger__dtor_base\tCALL\t0x004e5c60", "CSphereTrigger__dtor_base\tCALL\t0x004cb050", "CSphereTrigger__dtor_base\tCALL\t0x004f3f00"],
    "0x004bffa0": ["CWingmanStart__dtor_base\tCALL\t0x004e5bd0", "CWingmanStart__dtor_base\tCALL\t0x004f3f00"],
    "0x004c0000": ["CEscapePod__dtor_base\tCALL\t0x004cb050", "CEscapePod__dtor_base\tCALL\t0x004013d0"],
    "0x004f84e0": ["CUnit__dtor_base\tMOV\tdword ptr [ESI]", "CUnit__dtor_base\tCALL\tdword ptr [EAX + 0x4]"],
    "0x0050ee90": ["CUnit__scalar_deleting_dtor\tCALL\t0x004bfe00", "CUnit__scalar_deleting_dtor\tCALL\t0x00549220", "CUnit__scalar_deleting_dtor\tRET\t0x4"],
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime cleanup proven",
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry"):
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
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=(\d+)", match.group(1))}


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
    edges = {(row.get("target_addr", ""), row.get("from_addr", ""), row.get("from_function", "")) for row in rows}
    for edge in EXPECTED_XREF_EDGES:
        if edge not in edges:
            failures.append(f"post_xrefs.tsv: missing edge {edge}")


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
    check_decompile_and_instructions(base, failures)
    return ("FAIL" if failures else "PASS", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Accepted for npm-script consistency")
    parser.add_argument("--base", type=Path, default=BASE, help="Wave460 artifact directory")
    args = parser.parse_args()

    status, failures = run_checks(args.base)
    print(f"STATUS {status}")
    for failure in failures:
        print(f"FAIL {failure}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
