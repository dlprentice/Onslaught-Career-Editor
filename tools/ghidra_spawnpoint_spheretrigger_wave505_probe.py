#!/usr/bin/env python3
"""Validate Wave505 CSpawnPoint / CSphereTrigger static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = (
    ROOT
    / "subagents"
    / "ghidra-static-reaudit"
    / "wave505-spawnpoint-trigger-004e43d0"
)

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "spawnpoint-spheretrigger-wave505",
    "static-reaudit",
}


def target(
    name: str,
    signature: str,
    comment_tokens: tuple[str, ...],
    tags: set[str],
    decompile_tokens: tuple[str, ...],
    instruction_tokens: tuple[tuple[str, str, str], ...],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "comment_tokens": comment_tokens,
        "tags": COMMON_TAGS | tags,
        "decompile_tokens": decompile_tokens,
        "instruction_tokens": instruction_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004e46c0": target(
        "CSpawnPoint__Init",
        "void __thiscall CSpawnPoint__Init(void * this, void * init)",
        (
            "CSpawnPoint init helper",
            "RET 0x4 proves one explicit init argument",
            "global spawn-point set DAT_00855110",
            "runtime respawn behavior",
        ),
        {"spawnpoint", "init", "respawn", "static-shadow", "global-list", "rename-corrected"},
        (
            "void __thiscall CSpawnPoint__Init",
            "CStaticShadows__SampleShadowHeightBilinear",
            "CComplexThing__Init",
            "CSPtrSet__AddToHead",
            "DAT_00855110",
        ),
        (("0x004e46c0", "PUSH", "EBX"),),
    ),
    "0x004e47c0": target(
        "CSpawnPoint__VFuncSlot02_RemoveFromSpawnPointList",
        "void __fastcall CSpawnPoint__VFuncSlot02_RemoveFromSpawnPointList(void * this)",
        (
            "CSpawnPoint vtable slot 2 cleanup wrapper",
            "removes this from the global spawn-point set DAT_00855110",
            "VFuncSlot_02_004f41b0",
        ),
        {"spawnpoint", "cleanup", "global-list", "vtable", "rename-corrected"},
        (
            "void __fastcall CSpawnPoint__VFuncSlot02_RemoveFromSpawnPointList",
            "CSPtrSet__Remove",
            "VFuncSlot_02_004f41b0",
            "DAT_00855110",
        ),
        (("0x004e47c0", "PUSH", "ESI"),),
    ),
    "0x004e47e0": target(
        "CSpawnPoint__SpawnBattleEngine",
        "void * __thiscall CSpawnPoint__SpawnBattleEngine(void * this, int play_effect)",
        (
            "stale-owner correction",
            "CSpawnPoint/CStart-style SpawnBattleEngine helper",
            "RET 0x4 proves one explicit play_effect argument",
            "BE_Respawn_Ground_Effect",
            "BE_Respawn_Air_Effect",
        ),
        {
            "spawnpoint",
            "respawn",
            "battleengine",
            "particle-effect",
            "stale-owner-corrected",
            "rename-corrected",
        },
        (
            "void * __thiscall CSpawnPoint__SpawnBattleEngine",
            "OID__CreateObject",
            "BE_Respawn_Ground_Effect",
            "BE_Respawn_Air_Effect",
            "CParticleManager__CreateEffect",
        ),
        (("0x004e47e0", "MOV", "EAX, FS:[0x0]"),),
    ),
    "0x004e49f0": target(
        "CSpawnPoint__Available",
        "bool __fastcall CSpawnPoint__Available(void * this)",
        (
            "stale-owner correction",
            "CSpawnPoint availability predicate",
            "CGame__RespawnPlayer spawn-point selection",
            "CMapWho entries",
        ),
        {"spawnpoint", "respawn", "availability", "mapwho", "stale-owner-corrected", "rename-corrected"},
        (
            "bool __fastcall CSpawnPoint__Available",
            "CMapWho__GetFirstEntryWithinRadius",
            "CMapWhoEntry__GetOwner",
            "CMapWho__GetNextEntryWithinRadius",
        ),
        (("0x004e49f0", "MOV", "EAX, dword ptr [ECX + 0x448]"),),
    ),
    "0x004e5540": target(
        "CSphereTrigger__OnTriggered",
        "void __fastcall CSphereTrigger__OnTriggered(void * this)",
        (
            "CSphereTrigger triggered-effect helper",
            "Sphere_Trigger_Effect",
            "particle-effect link",
            "runtime trigger behavior",
        ),
        {"sphere-trigger", "trigger-effect", "particle-effect"},
        (
            "void __fastcall CSphereTrigger__OnTriggered",
            "ParticleEffectLink__SetHandleStateAndClear",
            "Sphere_Trigger_Effect",
            "CParticleManager__CreateEffect",
        ),
        (("0x004e5540", "PUSH", "ESI"),),
    ),
    "0x004e5700": target(
        "CSphereTrigger__Hit",
        "void __thiscall CSphereTrigger__Hit(void * this, void * other_thing, void * collision_report)",
        (
            "stale-name correction",
            "hit/contact override",
            "CComplexThing__Hit(this, other_thing, collision_report)",
            "this+0x8c",
        ),
        {"sphere-trigger", "hit", "active-reader", "monitor", "stale-name-corrected", "rename-corrected"},
        (
            "void __thiscall CSphereTrigger__Hit",
            "CComplexThing__Hit",
            "CGenericActiveReader__dtor",
            "CSPtrSet__Clear",
            "CSPtrSet__AddToHead",
            "CSPtrSet__AddToTail",
        ),
        (("0x004e5700", "PUSH", "-0x1"),),
    ),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"Missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_decompile(base: Path, address: str, name: str) -> str:
    path = base / "post-decomp" / f"{address[2:]}_{name}.c"
    if not path.exists():
        raise AssertionError(f"Missing decompile: {path}")
    return path.read_text(encoding="utf-8")


def normalize_addr(address: str) -> str:
    address = address.lower()
    return address if address.startswith("0x") else f"0x{address}"


def check_metadata(base: Path) -> None:
    rows = {normalize_addr(row["address"]): row for row in read_tsv(base / "post_metadata.tsv")}
    missing = set(TARGETS) - set(rows)
    if missing:
        raise AssertionError(f"Missing metadata rows: {sorted(missing)}")
    for address, spec in TARGETS.items():
        row = rows[address]
        if row["name"] != spec["name"]:
            raise AssertionError(f"{address} name {row['name']!r} != {spec['name']!r}")
        if row["signature"] != spec["signature"]:
            raise AssertionError(f"{address} signature {row['signature']!r} != {spec['signature']!r}")
        comment = row.get("comment") or ""
        for token in spec["comment_tokens"]:  # type: ignore[index]
            if token not in comment:
                raise AssertionError(f"{address} comment missing token {token!r}")


def check_tags(base: Path) -> None:
    rows = {normalize_addr(row["address"]): row for row in read_tsv(base / "post_tags.tsv")}
    missing = set(TARGETS) - set(rows)
    if missing:
        raise AssertionError(f"Missing tag rows: {sorted(missing)}")
    for address, spec in TARGETS.items():
        tags = {tag for tag in rows[address].get("tags", "").replace(",", ";").split(";") if tag}
        expected = spec["tags"]  # type: ignore[assignment]
        missing_tags = set(expected) - tags
        if missing_tags:
            raise AssertionError(f"{address} missing tags: {sorted(missing_tags)}")


def check_decompile(base: Path) -> None:
    for address, spec in TARGETS.items():
        text = read_decompile(base, address, spec["name"])  # type: ignore[arg-type]
        for token in spec["decompile_tokens"]:  # type: ignore[index]
            if token not in text:
                raise AssertionError(f"{address} decompile missing token {token!r}")


def check_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_target = {}
    for row in rows:
        by_target.setdefault(normalize_addr(row["target_raw"]), []).append(row)
    for address, spec in TARGETS.items():
        target_rows = by_target.get(address, [])
        for instr_addr, mnemonic, operands in spec["instruction_tokens"]:  # type: ignore[index]
            if not any(
                row["instruction_addr"].lower() == instr_addr
                and row["mnemonic"] == mnemonic
                and row["operands"] == operands
                for row in target_rows
            ):
                raise AssertionError(f"{address} missing instruction {instr_addr} {mnemonic} {operands}")


def check_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    targets = {normalize_addr(row["target_addr"]) for row in rows}
    for address in TARGETS:
        if address not in targets:
            raise AssertionError(f"{address} missing xref rows")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    base = args.base
    check_metadata(base)
    check_tags(base)
    check_decompile(base)
    check_instructions(base)
    check_xrefs(base)
    print(f"Wave505 CSpawnPoint/CSphereTrigger probe OK: {len(TARGETS)} functions validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
