#!/usr/bin/env python3
"""Validate Wave492 CRocket static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave492-rocket-round-004d7b10"

TARGETS = {
    "0x004d7b10": {
        "name": "CRocket__Init",
        "signature": "void __thiscall CRocket__Init(void * this, void * init)",
        "tags": {
            "static-reaudit",
            "rocket-wave492",
            "rocket",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "name-corrected",
            "init",
            "render-resource",
        },
        "comment_tokens": (
            "CRocket vtable 0x005dd458 slot 9",
            "RET 0x4 plus ECX/stack use",
            "init+0x7c/init+0x80",
            "init+0x70 with 0x120",
            "m_rocket.msh",
            "PCRTID__CreateObject(1)",
            "this+0x30",
            "init+0xa8",
            "init+0x3ac",
            "this+0xe8 to 25.0",
            "CActor__Init",
            "runtime rocket launch/render behavior",
            "rebuild parity remain unproven",
        ),
        "decompile_tokens": (
            "m_rocket_msh",
            "PCRTID__CreateObject",
            "CActor__Init(this,init)",
            "CResourceDescriptor__ctor",
            "CResourceDescriptor__dtor",
            "init + 0x3ac",
            "this + 0xe8",
            "0x41c80000",
        ),
    },
    "0x004d8040": {
        "name": "CRocket__VFunc_22_CreateBigRocketEngineEffects",
        "signature": "void __fastcall CRocket__VFunc_22_CreateBigRocketEngineEffects(void * this)",
        "tags": {
            "static-reaudit",
            "rocket-wave492",
            "rocket",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "name-corrected",
            "engine-effect",
            "particle-effect",
        },
        "comment_tokens": (
            "CRocket vtable 0x005dd458 slot 22",
            "Register-only ECX receiver",
            "this+0xe4",
            "Big Rocket Engine Effect",
            "CWorldPhysicsManager__FindNodeByNameGE",
            "four particle effects",
            "CParticleManager__CreateEffect",
            "this+0xec",
            "0x0083cc48..0x0083cc54",
            "runtime engine-effect behavior",
            "rebuild parity remain unproven",
        ),
        "decompile_tokens": (
            "Big_Rocket_Engine_Effect",
            "CWorldPhysicsManager__FindNodeByNameGE",
            "CParticleManager__CreateEffect",
            "out_handle_slot",
            "iVar1 = 4",
            "DAT_0083cc48",
            "DAT_0083cc54",
        ),
    },
}

EXPECTED_SUMMARIES = {
    "apply_rocket_wave492_dry.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 2,
        "missing": 0,
        "bad": 0,
    },
    "apply_rocket_wave492_apply.log": {
        "updated": 2,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 2,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_rocket_wave492_verify_dry.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

XREFS = {
    "0x004d7b10": "0x005dd47c",
    "0x004d8040": "0x005dd4b0",
}

VTABLE_SLOTS = {
    "0x004d7b10": ("0x005dd458", "9", "0x005dd47c"),
    "0x004d8040": ("0x005dd458", "22", "0x005dd4b0"),
}

INSTRUCTION_TOKENS = (
    "0x004d7b2d 0x004d7b10 CRocket__Init MOV EBP, dword ptr [ESP + 0x440]",
    "0x004d7b42 0x004d7b10 CRocket__Init MOV dword ptr [EBP + 0x7c], EAX",
    "0x004d7b45 0x004d7b10 CRocket__Init OR ESI, 0x120",
    "0x004d7bc7 0x004d7b10 CRocket__Init CALL 0x00516580",
    "0x004d7bcf 0x004d7b10 CRocket__Init MOV dword ptr [EBX + 0x30], EAX",
    "0x004d7c0a 0x004d7b10 CRocket__Init MOV dword ptr [EBX + 0xe8], 0x41c80000",
    "0x004d7c14 0x004d7b10 CRocket__Init MOV dword ptr [EBX + 0xe0], 0x1",
    "0x004d7c1e 0x004d7b10 CRocket__Init CALL 0x004011e0",
    "0x004d7c5b 0x004d7b10 CRocket__Init RET 0x4",
    "0x004d8059 0x004d8040 CRocket__VFunc_22_CreateBigRocketEngineEffects CALL 0x004cd7a0",
    "0x004d8064 0x004d8040 CRocket__VFunc_22_CreateBigRocketEngineEffects ADD ESI, 0xec",
    "0x004d806a 0x004d8040 CRocket__VFunc_22_CreateBigRocketEngineEffects MOV EBX, 0x4",
    "0x004d80a2 0x004d8040 CRocket__VFunc_22_CreateBigRocketEngineEffects CALL 0x004cb3d0",
    "0x004d80ab 0x004d8040 CRocket__VFunc_22_CreateBigRocketEngineEffects JNZ 0x004d806f",
    "0x004d80b0 0x004d8040 CRocket__VFunc_22_CreateBigRocketEngineEffects RET",
)

OVERCLAIMS = (
    "fully re'ed",
    "runtime behavior proven",
    "source identity proven",
    "exact layout proven",
    "rebuild parity proven",
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


def has_token(text: str, token: str) -> bool:
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
        for key in ("address", "target_addr", "from_addr", "vtable", "slot_addr", "pointer_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def check_logs(base: Path, failures: list[str]) -> None:
    for filename, expected in EXPECTED_SUMMARIES.items():
        text = read_text(base / filename)
        if not text:
            failures.append(f"{filename}: missing")
            continue
        actual = parse_summary(text)
        if actual != expected:
            failures.append(f"{filename}: summary mismatch {actual} != {expected}")
        if "REPORT: Save succeeded" not in text:
            failures.append(f"{filename}: missing save-success marker")
        if filename.endswith("verify_dry.log"):
            for address, spec in TARGETS.items():
                if f"SKIP: {address} {spec['name']}" not in text:
                    failures.append(f"{filename}: missing idempotent SKIP marker for {address}")
        for bad in ("FAIL:", "MISSING:", "BADNAME:", "LockException"):
            if bad in text:
                failures.append(f"{filename}: unexpected token {bad!r}")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    for address, spec in TARGETS.items():
        row = next((item for item in rows if item.get("address") == address), None)
        if row is None:
            failures.append(f"{address}: missing metadata")
            continue
        if row.get("status") != "OK":
            failures.append(f"{address}: metadata status {row.get('status')} != OK")
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: name {row.get('name')} != {spec['name']}")
        if compact(row.get("signature", "")) != compact(str(spec["signature"])):
            failures.append(f"{address}: signature {row.get('signature')} != {spec['signature']}")
        comment = row.get("comment", "")
        for token in spec["comment_tokens"]:
            if not has_token(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIMS:
            if has_token(comment, token):
                failures.append(f"{address}: overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    for address, spec in TARGETS.items():
        row = next((item for item in rows if item.get("address") == address), None)
        if row is None:
            failures.append(f"{address}: missing tags")
            continue
        actual = {part.strip() for part in re.split(r"[;,]", row.get("tags", "")) if part.strip()}
        missing = set(spec["tags"]) - actual
        if missing:
            failures.append(f"{address}: missing tags {sorted(missing)}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, spec in TARGETS.items():
        filename = f"{address[2:]}_{spec['name']}.c"
        text = read_text(base / "post-decomp" / filename)
        if not text:
            failures.append(f"{address}: missing decompile {filename}")
            continue
        for token in spec["decompile_tokens"]:
            if not has_token(text, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")
        for token in OVERCLAIMS:
            if has_token(text, token):
                failures.append(f"{address}: decompile overclaim token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    for address, from_addr in XREFS.items():
        row = next(
            (
                item
                for item in rows
                if item.get("target_addr") == address
                and item.get("from_addr") == from_addr
                and item.get("ref_type") == "DATA"
            ),
            None,
        )
        if row is None:
            failures.append(f"{address}: missing vtable DATA xref from {from_addr}")


def check_vtable(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_vtable.tsv")
    for address, (vtable, slot_index, slot_addr) in VTABLE_SLOTS.items():
        spec = TARGETS[address]
        row = next(
            (
                item
                for item in rows
                if item.get("vtable") == vtable
                and item.get("slot_index") == slot_index
                and item.get("slot_addr") == slot_addr
            ),
            None,
        )
        if row is None:
            failures.append(f"{address}: missing vtable {vtable} slot {slot_index} row")
            continue
        if row.get("pointer_addr") != address or row.get("function_name") != spec["name"] or row.get("status") != "OK":
            failures.append(f"{address}: vtable slot mismatch {row}")


def check_instructions(base: Path, failures: list[str]) -> None:
    text = read_text(base / "post_instructions.tsv")
    for token in INSTRUCTION_TOKENS:
        if not has_token(text, token):
            failures.append(f"post_instructions.tsv missing token {token!r}")


def run(base: Path = DEFAULT_BASE) -> list[str]:
    failures: list[str] = []
    check_logs(base, failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_decompile(base, failures)
    check_xrefs(base, failures)
    check_vtable(base, failures)
    check_instructions(base, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = run(args.base)
    if failures:
        print("FAIL Wave492 CRocket probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS Wave492 CRocket probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
