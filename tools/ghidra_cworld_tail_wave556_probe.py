#!/usr/bin/env python3
"""Validate Wave556 CWorld tail / WorldMeshList Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave556-cworld-tail-0050d680"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cworld_tail_wave556_2026-05-18.md"
WORLD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "World.cpp" / "_index.md"
WORLD_MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldMeshList.cpp" / "_index.md"
WORLD_PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x0050d680": {
        "raw": "0050d680",
        "name": "CWorld__ReleaseSubObject_AndMaybeFree",
        "signature": "void * __thiscall CWorld__ReleaseSubObject_AndMaybeFree(void * this, uint flags)",
        "tags": {"cworld-tail-wave556", "lod", "occupancy", "phantom-param-removed"},
        "comment_tokens": ("world +0x200", "flags=1", "older second explicit parameter"),
        "decompile_tokens": ("CWorld__ReleaseSubObject_AndMaybeFree(void *this,uint flags)", "flags & 1"),
        "forbidden": ("param_1", "param_2"),
    },
    "0x0050d6a0": {
        "raw": "0050d6a0",
        "name": "CWorld__PushWorldTextSlot",
        "signature": "void __thiscall CWorld__PushWorldTextSlot(void * this, int text_id, int slot_state)",
        "tags": {"cworld-tail-wave556", "world-text", "script-wrapper", "phantom-param-removed"},
        "comment_tokens": ("CText__GetStringById", "this +0x20c", "text_id/string/state"),
        "decompile_tokens": ("CWorld__PushWorldTextSlot(void *this,int text_id,int slot_state)", "CText__GetStringById"),
        "forbidden": ("param_1", "param_2", "param_3"),
    },
    "0x0050d720": {
        "raw": "0050d720",
        "name": "CWorld__UpdateWorldTextSlotTiming",
        "signature": "void __thiscall CWorld__UpdateWorldTextSlotTiming(void * this, int text_id, float primary_time, float secondary_time)",
        "tags": {"cworld-tail-wave556", "world-text", "timing", "phantom-param-removed"},
        "comment_tokens": ("primary/secondary timing", "DAT_00672fd0", "slot state 3"),
        "decompile_tokens": (
            "CWorld__UpdateWorldTextSlotTiming(void *this,int text_id,float primary_time,float secondary_time)",
            "primary_time",
            "secondary_time",
        ),
        "forbidden": ("param_1", "param_2", "param_3", "param_4"),
    },
    "0x0050d760": {
        "raw": "0050d760",
        "name": "CWorld__GetWorldTextSlotTimerValue",
        "signature": "double __thiscall CWorld__GetWorldTextSlotTimerValue(void * this, int slot_index)",
        "tags": {"cworld-tail-wave556", "world-text", "hud", "owner-corrected"},
        "comment_tokens": ("not ExplosionInitThing", "slot_index*4", "clamps state-3 absolute expiry"),
        "decompile_tokens": ("CWorld__GetWorldTextSlotTimerValue(void *this,int slot_index)", "DAT_00672fd0"),
        "forbidden": ("CExplosionInitThing", "param_1", "param_2"),
    },
    "0x0050d7a0": {
        "raw": "0050d7a0",
        "name": "CWorld__ClearWorldTextSlot",
        "signature": "void __thiscall CWorld__ClearWorldTextSlot(void * this, int text_id)",
        "tags": {"cworld-tail-wave556", "world-text", "script-wrapper", "phantom-param-removed"},
        "comment_tokens": ("passes one text_id", "this +0x21c", "older second explicit parameter"),
        "decompile_tokens": ("CWorld__ClearWorldTextSlot(void *this,int text_id)", "text_id"),
        "forbidden": ("param_1", "param_2"),
    },
    "0x0050d7d0": {
        "raw": "0050d7d0",
        "name": "CWorld__IsMultiplayerMode",
        "signature": "int __fastcall CWorld__IsMultiplayerMode(void * world)",
        "tags": {"cworld-tail-wave556", "mode", "multiplayer"},
        "comment_tokens": ("world +0x27c", "1 or 2", "CGame__LoadLevel"),
        "decompile_tokens": ("CWorld__IsMultiplayerMode(void *world)", "world + 0x27c"),
        "forbidden": ("param_1",),
    },
    "0x0050d7f0": {
        "raw": "0050d7f0",
        "name": "CWorld__ClearLinkedObjectPairSet",
        "signature": "void __fastcall CWorld__ClearLinkedObjectPairSet(void * pair_set)",
        "tags": {"cworld-tail-wave556", "pair-set", "script-events", "cleanup"},
        "comment_tokens": ("world +0x120", "both pointer fields", "CSPtrSet"),
        "decompile_tokens": ("CWorld__ClearLinkedObjectPairSet(void *pair_set)", "CSPtrSet__Clear"),
        "forbidden": ("param_1",),
    },
    "0x0050d9a0": {
        "raw": "0050d9a0",
        "name": "CWorldMeshList__Clear",
        "signature": "void __cdecl CWorldMeshList__Clear(void)",
        "tags": {"cworld-tail-wave556", "world-mesh-list", "cleanup"},
        "comment_tokens": ("DAT_00855358", "mesh-name string", "8-byte list node"),
        "decompile_tokens": ("CWorldMeshList__Clear(void)", "DAT_00855358"),
    },
    "0x0050d9e0": {
        "raw": "0050d9e0",
        "name": "CWorldMeshList__Add",
        "signature": "void __cdecl CWorldMeshList__Add(char * mesh_name)",
        "tags": {"cworld-tail-wave556", "world-mesh-list", "recursive", "signature-recovered"},
        "comment_tokens": ("recursive self-calls", "DAT_008553fc +0xb0", "DAT_008553f4"),
        "decompile_tokens": ("CWorldMeshList__Add(char *mesh_name)", "CWorldMeshList__Add"),
        "forbidden": ("param_1",),
    },
    "0x0050dc20": {
        "raw": "0050dc20",
        "name": "CWorldMeshList__MarkUsed",
        "signature": "void __cdecl CWorldMeshList__MarkUsed(char * mesh_name)",
        "tags": {"cworld-tail-wave556", "world-mesh-list", "used-flag", "signature-recovered"},
        "comment_tokens": ("CUnit__Init", "used flag at +0x04", "mesh_name"),
        "decompile_tokens": ("CWorldMeshList__MarkUsed(char *mesh_name)", "mesh_name"),
        "forbidden": ("param_1",),
    },
    "0x0050dcb0": {
        "raw": "0050dcb0",
        "name": "CWorld__SpawnInitialThings",
        "signature": "void __cdecl CWorld__SpawnInitialThings(void)",
        "tags": {"cworld-tail-wave556", "world-mesh-list", "spawn", "signature-recovered"},
        "comment_tokens": ("unused DAT_00855358", "init thing type 8", "default 256/256/0"),
        "decompile_tokens": ("CWorld__SpawnInitialThings(void)", "CWorldPhysicsManager__CreateThingByType"),
    },
    "0x0050df80": {
        "raw": "0050df80",
        "name": "CWorldPhysicsManager__CreateThingByType",
        "signature": "void * __cdecl CWorldPhysicsManager__CreateThingByType(int thing_type_index)",
        "tags": {"cworld-tail-wave556", "world-physics-manager", "factory", "signature-recovered"},
        "comment_tokens": ("thing_type_index", "definition type enum at +0xe0", "returns the created object"),
        "decompile_tokens": ("CWorldPhysicsManager__CreateThingByType(int thing_type_index)", "thing_type_index"),
        "forbidden": ("param_1",),
    },
}


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {normalize_address(row["address"]): row for row in rows}


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing token: {token}")


def run_check() -> list[str]:
    failures: list[str] = []
    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    decomp_index = read_tsv(BASE / "post_decompile" / "index.tsv")

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing from post_metadata.tsv")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name mismatch: {row.get('name')}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row.get('signature')}")
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status mismatch: {row.get('status')}")
        require_tokens(f"{address} comment", row.get("comment", ""), spec["comment_tokens"], failures)

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            missing_tags = set(spec["tags"]) - actual_tags
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")

        idx_row = decomp_index.get(address)
        if idx_row is None or idx_row.get("status") != "OK":
            failures.append(f"{address} decompile index not OK")
        decomp_file = BASE / "post_decompile" / f"{spec['raw']}_{spec['name']}.c"
        decomp_text = read_text(decomp_file)
        require_tokens(f"{address} decompile", decomp_text, spec["decompile_tokens"], failures)
        for token in spec.get("forbidden", ()):
            if token in decomp_text:
                failures.append(f"{address} forbidden decompile token remained: {token}")

    docs = {
        "public note": (
            read_text(PUBLIC_NOTE),
            ("Wave556", "CWorld__GetWorldTextSlotTimerValue", "CWorldMeshList__Add", "CWorldPhysicsManager__CreateThingByType"),
        ),
        "World.cpp index": (
            read_text(WORLD_DOC),
            ("Wave556", "CWorld__GetWorldTextSlotTimerValue", "CWorldMeshList__Add", "CWorldPhysicsManager__CreateThingByType"),
        ),
        "WorldMeshList.cpp index": (
            read_text(WORLD_MESH_DOC),
            ("Wave556", "CWorldMeshList__Add", "CWorldMeshList__MarkUsed"),
        ),
        "WorldPhysicsManager.cpp index": (
            read_text(WORLD_PHYSICS_DOC),
            ("Wave556", "CWorldPhysicsManager__CreateThingByType", "thing_type_index"),
        ),
        "function index": (
            read_text(FUNCTION_INDEX),
            ("Wave556", "CWorld__GetWorldTextSlotTimerValue", "CWorldMeshList__Add", "CWorldPhysicsManager__CreateThingByType"),
        ),
        "mutation backlog": (
            read_text(BACKLOG),
            ("Wave556", "CWorld__GetWorldTextSlotTimerValue", "CWorldMeshList__Add", "CWorldPhysicsManager__CreateThingByType"),
        ),
        "mutation ledger": (
            read_text(LEDGER),
            ("Wave556", "CExplosionInitThing ownership", "CWorldPhysicsManager__CreateThingByType"),
        ),
    }
    for label, (text, tokens) in docs.items():
        require_tokens(label, text, tokens, failures)

    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    try:
        failures = run_check()
    except Exception as exc:
        print(f"Wave556 CWorld tail probe failed to run: {exc}", file=sys.stderr)
        return 1

    if failures:
        print("Wave556 CWorld tail probe FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave556 CWorld tail probe PASS")
    print(f"Validated {len(TARGETS)} targets and docs evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
