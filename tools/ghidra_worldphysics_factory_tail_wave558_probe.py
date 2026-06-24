#!/usr/bin/env python3
"""Validate Wave558 WorldPhysicsManager factory-tail Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave558-worldphysics-factory-tail-0050f610"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_worldphysics_factory_tail_wave558_2026-05-18.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
WORLD_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x0050f610": {
        "raw": "0050f610",
        "name": "CRelaxedSquad__scalar_deleting_dtor",
        "signature": "void * __thiscall CRelaxedSquad__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"worldphysics-factory-tail-wave558", "relaxed-squad", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e39d0", "CRelaxedSquad__Destructor", "RET 0x4"),
        "decompile_tokens": ("CRelaxedSquad__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050f630": {
        "raw": "0050f630",
        "name": "CRelaxedSquad__Destructor",
        "signature": "void __fastcall CRelaxedSquad__Destructor(void * this)",
        "tags": {"worldphysics-factory-tail-wave558", "relaxed-squad", "destructor-body"},
        "comment_tokens": ("this+0xa4", "CComplexThing__dtor_base"),
        "decompile_tokens": ("CRelaxedSquad__Destructor(void *this)", "CSPtrSet__Clear"),
    },
    "0x0050f6d0": {
        "raw": "0050f6d0",
        "name": "CWorldPhysicsManager__CreateWeaponByIndex",
        "signature": "void * __cdecl CWorldPhysicsManager__CreateWeaponByIndex(int weapon_index, int create_context)",
        "tags": {"worldphysics-factory-tail-wave558", "world-physics-manager", "weapon", "factory"},
        "comment_tokens": ("DAT_008553e8", "0xb0 CWeapon", "create_context"),
        "decompile_tokens": ("CWorldPhysicsManager__CreateWeaponByIndex(int weapon_index,int create_context)", "CWeapon__ctor_base", "create_context"),
    },
    "0x0050f7a0": {
        "raw": "0050f7a0",
        "name": "CWorldPhysicsManager__CreateProjectile",
        "signature": "void * __cdecl CWorldPhysicsManager__CreateProjectile(void * round_definition)",
        "tags": {"worldphysics-factory-tail-wave558", "world-physics-manager", "projectile", "factory"},
        "comment_tokens": ("round_definition+0x70", "0x134 CRound", "missile-style"),
        "decompile_tokens": ("CWorldPhysicsManager__CreateProjectile(void *round_definition)", "CRound__ctor", "round_definition"),
    },
    "0x0050f8b0": {
        "raw": "0050f8b0",
        "name": "CMissile__scalar_deleting_dtor",
        "signature": "void * __thiscall CMissile__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"worldphysics-factory-tail-wave558", "missile", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e3ba8", "CMissile__Destructor", "RET 0x4"),
        "decompile_tokens": ("CMissile__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050f8d0": {
        "raw": "0050f8d0",
        "name": "CMissile__Destructor",
        "signature": "void __fastcall CMissile__Destructor(void * this)",
        "tags": {"worldphysics-factory-tail-wave558", "missile", "destructor-body"},
        "comment_tokens": ("this+0xec", "this+0xe8", "CActor__dtor_base"),
        "decompile_tokens": ("CMissile__Destructor(void *this)", "CActor__dtor_base"),
    },
    "0x0050f970": {
        "raw": "0050f970",
        "name": "CWorldPhysicsManager__CreateSpawner",
        "signature": "void * __cdecl CWorldPhysicsManager__CreateSpawner(int spawner_index, void * spawn_context)",
        "tags": {"worldphysics-factory-tail-wave558", "world-physics-manager", "spawner", "factory"},
        "comment_tokens": ("DAT_008553f4", "0x3f8 CSpawnerThng", "spawn_context"),
        "decompile_tokens": ("CWorldPhysicsManager__CreateSpawner(int spawner_index,void *spawn_context)", "CSpawnerThng__Constructor", "spawn_context"),
    },
    "0x0050fa40": {
        "raw": "0050fa40",
        "name": "CWorldPhysicsManager__CreateCharacter",
        "signature": "void * __cdecl CWorldPhysicsManager__CreateCharacter(int component_index)",
        "tags": {"worldphysics-factory-tail-wave558", "world-physics-manager", "character", "factory"},
        "comment_tokens": ("DAT_00855400", "Gill_M_Head", "0x310"),
        "decompile_tokens": ("CWorldPhysicsManager__CreateCharacter(int component_index)", "s_Gill_M_Head_0063d9b4", "component_index"),
    },
    "0x0050fd30": {
        "raw": "0050fd30",
        "name": "CGillMHead__scalar_deleting_dtor",
        "signature": "void * __thiscall CGillMHead__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"worldphysics-factory-tail-wave558", "gillm-head", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e41fc", "CGillMHead__Destructor_VFunc01", "RET 0x4"),
        "decompile_tokens": ("CGillMHead__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050fd50": {
        "raw": "0050fd50",
        "name": "CTentacle__scalar_deleting_dtor",
        "signature": "void * __thiscall CTentacle__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"worldphysics-factory-tail-wave558", "tentacle", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e3fa0", "CTentacle__Destructor", "RET 0x4"),
        "decompile_tokens": ("CTentacle__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050fd70": {
        "raw": "0050fd70",
        "name": "CComponent__scalar_deleting_dtor",
        "signature": "void * __thiscall CComponent__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"worldphysics-factory-tail-wave558", "component", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e3d44", "CComponent__Destructor", "RET 0x4"),
        "decompile_tokens": ("CComponent__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050fd90": {
        "raw": "0050fd90",
        "name": "CComponent__Destructor",
        "signature": "void __fastcall CComponent__Destructor(void * this)",
        "tags": {"worldphysics-factory-tail-wave558", "component", "destructor-body"},
        "comment_tokens": ("this+0x26c", "this+0x258", "CUnit__dtor_base"),
        "decompile_tokens": ("CComponent__Destructor(void *this)", "CUnit__dtor_base"),
    },
    "0x0050fe10": {
        "raw": "0050fe10",
        "name": "CGillMHead__Destructor_VFunc01",
        "signature": "void __fastcall CGillMHead__Destructor_VFunc01(void * this)",
        "tags": {"worldphysics-factory-tail-wave558", "gillm-head", "destructor-body"},
        "comment_tokens": ("this+0x26c", "this+0x258", "CUnit__dtor_base"),
        "decompile_tokens": ("CGillMHead__Destructor_VFunc01(void *this)", "CUnit__dtor_base"),
    },
    "0x0050fe90": {
        "raw": "0050fe90",
        "name": "CTentacle__Destructor",
        "signature": "void __fastcall CTentacle__Destructor(void * this)",
        "tags": {"worldphysics-factory-tail-wave558", "tentacle", "destructor-body"},
        "comment_tokens": ("this+0x26c", "this+0x258", "CUnit__dtor_base"),
        "decompile_tokens": ("CTentacle__Destructor(void *this)", "CUnit__dtor_base"),
    },
    "0x0050ff10": {
        "raw": "0050ff10",
        "name": "CWorldPhysicsManager__CreatePickup",
        "signature": "void * __cdecl CWorldPhysicsManager__CreatePickup(int pickup_type)",
        "tags": {"worldphysics-factory-tail-wave558", "world-physics-manager", "pickup", "factory"},
        "comment_tokens": ("0x94", "pickup_type", "field+0x90"),
        "decompile_tokens": ("CWorldPhysicsManager__CreatePickup(int pickup_type)", "CComplexThing__ctor_base"),
    },
    "0x0050ffd0": {
        "raw": "0050ffd0",
        "name": "CExplosion__scalar_deleting_dtor",
        "signature": "void * __thiscall CExplosion__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"worldphysics-factory-tail-wave558", "explosion", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e4458", "CExplosion__Destructor", "RET 0x4"),
        "decompile_tokens": ("CExplosion__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050fff0": {
        "raw": "0050fff0",
        "name": "CExplosion__Destructor",
        "signature": "void __fastcall CExplosion__Destructor(void * this)",
        "tags": {"worldphysics-factory-tail-wave558", "explosion", "destructor-body"},
        "comment_tokens": ("this+0x90", "CComplexThing__dtor_base"),
        "decompile_tokens": ("CExplosion__Destructor(void *this)", "CComplexThing__dtor_base"),
    },
    "0x00510060": {
        "raw": "00510060",
        "name": "CWorldPhysicsManager__CreateEffect",
        "signature": "void * __cdecl CWorldPhysicsManager__CreateEffect(int effect_type)",
        "tags": {"worldphysics-factory-tail-wave558", "world-physics-manager", "effect", "factory"},
        "comment_tokens": ("0xf4", "effect_type", "effect class tables"),
        "decompile_tokens": ("CWorldPhysicsManager__CreateEffect(int effect_type)", "CComplexThing__ctor_base"),
    },
    "0x00510150": {
        "raw": "00510150",
        "name": "CWorldPhysicsManager__CreateTrigger",
        "signature": "void * __cdecl CWorldPhysicsManager__CreateTrigger(int trigger_type)",
        "tags": {"worldphysics-factory-tail-wave558", "world-physics-manager", "trigger", "factory"},
        "comment_tokens": ("0x88", "trigger_type", "PushNodeGlobalList"),
        "decompile_tokens": ("CWorldPhysicsManager__CreateTrigger(int trigger_type)", "CWorldPhysicsManager__PushNodeGlobalList"),
    },
    "0x00510230": {
        "raw": "00510230",
        "name": "CHazard__scalar_deleting_dtor",
        "signature": "void * __thiscall CHazard__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"worldphysics-factory-tail-wave558", "hazard", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e4780", "CHazard__Destructor", "RET 0x4"),
        "decompile_tokens": ("CHazard__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x00510250": {
        "raw": "00510250",
        "name": "CHazard__Destructor",
        "signature": "void __fastcall CHazard__Destructor(void * this)",
        "tags": {"worldphysics-factory-tail-wave558", "hazard", "destructor-body", "signature-recovered"},
        "comment_tokens": ("one-argument fastcall", "this+0x80", "CComplexThing__dtor_base"),
        "decompile_tokens": ("CHazard__Destructor(void *this)", "CComplexThing__dtor_base"),
    },
    "0x005102a0": {
        "raw": "005102a0",
        "name": "CWorldPhysicsManager__InitializeLists",
        "signature": "void __cdecl CWorldPhysicsManager__InitializeLists(void)",
        "tags": {"worldphysics-factory-tail-wave558", "world-physics-manager", "list-initializer"},
        "comment_tokens": ("nine 0x10 CSPtrSet", "DAT_008553e8", "DAT_00855408"),
        "decompile_tokens": ("CWorldPhysicsManager__InitializeLists(void)", "CSPtrSet__Init", "DAT_00855408"),
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
    xrefs = read_text(BASE / "post_xrefs.tsv")

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
        for forbidden in ("param_1", "param_2", "VFunc_01_0050"):
            if forbidden in decomp_text:
                failures.append(f"{address} forbidden decompile token remained: {forbidden}")

    require_tokens(
        "xrefs",
        xrefs,
        (
            "CRelaxedSquad__scalar_deleting_dtor",
            "CWorldPhysicsManager__CreateWeaponByIndex",
            "ProjectileBurst__SpawnFromCurrentPreset",
            "CWorldPhysicsManager__CreatePickup",
            "CWorldPhysicsManager__InitializeLists",
        ),
        failures,
    )

    docs = {
        "public note": (read_text(PUBLIC_NOTE), ("Wave558", "CWorldPhysicsManager__CreateWeaponByIndex", "CHazard__scalar_deleting_dtor")),
        "function index": (read_text(FUNCTION_INDEX), ("Wave558", "CWorldPhysicsManager__CreateProjectile", "CWorldPhysicsManager__InitializeLists")),
        "WorldPhysicsManager index": (read_text(WORLD_INDEX), ("Wave558", "CMissile__scalar_deleting_dtor", "nine 0x10 CSPtrSet")),
        "GHIDRA reference": (read_text(GHIDRA_REFERENCE), ("Wave558", "WorldPhysicsManager factory tail", "CreateWeaponByIndex")),
        "static campaign": (read_text(CAMPAIGN), ("Wave 558", "WorldPhysicsManager factory tail", "22 adjacent")),
        "mutation backlog": (read_text(BACKLOG), ("Wave558", "CRelaxedSquad__scalar_deleting_dtor", "CWorldPhysicsManager__InitializeLists")),
        "mutation ledger": (read_text(LEDGER), ("Wave558", "WorldPhysicsManager factory tail", "22 targets")),
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
        print(f"Wave558 WorldPhysicsManager factory-tail probe failed to run: {exc}", file=sys.stderr)
        return 1

    if failures:
        print("Wave558 WorldPhysicsManager factory-tail probe FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave558 WorldPhysicsManager factory-tail probe PASS")
    print(f"Validated {len(TARGETS)} targets and docs evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
