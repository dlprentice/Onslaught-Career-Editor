#!/usr/bin/env python3
"""Validate Wave559 WorldPhysicsManager cleanup/resolve Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave559-worldphysics-cleanup-resolve-00510e60"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_worldphysics_cleanup_resolve_wave559_2026-05-18.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
WORLD_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x00510e60": {
        "raw": "00510e60",
        "name": "CWorldPhysicsManager__FreeEntryOwnedPtrs_00_0C_20",
        "signature": "void __fastcall CWorldPhysicsManager__FreeEntryOwnedPtrs_00_0C_20(void * entry)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "definition-cleanup", "owned-pointer-free"},
        "comment_tokens": ("DAT_00855404", "entry+0x20", "entry+0x0c"),
        "decompile_tokens": ("CWorldPhysicsManager__FreeEntryOwnedPtrs_00_0C_20(void *entry)", "CDXMemoryManager__Free"),
    },
    "0x00510eb0": {
        "raw": "00510eb0",
        "name": "CWorldPhysicsManager__FreeRoundStatement",
        "signature": "void __fastcall CWorldPhysicsManager__FreeRoundStatement(void * round_statement)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "round", "definition-cleanup"},
        "comment_tokens": ("DAT_008553f0", "+0x18", "+0x14"),
        "decompile_tokens": ("CWorldPhysicsManager__FreeRoundStatement(void *round_statement)", "CDXMemoryManager__Free"),
    },
    "0x00510f10": {
        "raw": "00510f10",
        "name": "CWorldPhysicsManager__FreeWeaponModeStatement",
        "signature": "void __fastcall CWorldPhysicsManager__FreeWeaponModeStatement(void * weapon_mode_statement)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "weapon-mode", "embedded-set-clear"},
        "comment_tokens": ("DAT_008553ec", "+0x5c", "+0x4c"),
        "decompile_tokens": ("CWorldPhysicsManager__FreeWeaponModeStatement(void *weapon_mode_statement)", "CSPtrSet__Clear"),
    },
    "0x00511040": {
        "raw": "00511040",
        "name": "CWorldPhysicsManager__FreeWeaponStatement",
        "signature": "void __fastcall CWorldPhysicsManager__FreeWeaponStatement(void * weapon_statement)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "weapon", "definition-cleanup"},
        "comment_tokens": ("DAT_008553e8", "+0x00", "+0x04"),
        "decompile_tokens": ("CWorldPhysicsManager__FreeWeaponStatement(void *weapon_statement)", "CDXMemoryManager__Free"),
    },
    "0x00511070": {
        "raw": "00511070",
        "name": "CWorldPhysicsManager__FreeTagDefinitionEntry",
        "signature": "void __fastcall CWorldPhysicsManager__FreeTagDefinitionEntry(void * tag_definition)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "tag-definition", "definition-cleanup"},
        "comment_tokens": ("DAT_008553f8", "+0x30", "+0x18"),
        "decompile_tokens": ("CWorldPhysicsManager__FreeTagDefinitionEntry(void *tag_definition)", "CDXMemoryManager__Free"),
    },
    "0x005110f0": {
        "raw": "005110f0",
        "name": "CWorldPhysicsManager__FreeThingOrComponentDefinitionEntry",
        "signature": "void __fastcall CWorldPhysicsManager__FreeThingOrComponentDefinitionEntry(void * definition_entry)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "thing-definition", "component-definition"},
        "comment_tokens": ("DAT_008553fc", "DAT_00855400", "+0x6c"),
        "decompile_tokens": ("CWorldPhysicsManager__FreeThingOrComponentDefinitionEntry(void *definition_entry)", "CSPtrSet__Clear"),
    },
    "0x005113a0": {
        "raw": "005113a0",
        "name": "CWorldPhysicsManager__ClearEntryWorkSets_40_50",
        "signature": "void __fastcall CWorldPhysicsManager__ClearEntryWorkSets_40_50(void * definition_entry)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "embedded-set-clear"},
        "comment_tokens": ("definition_entry+0x50", "definition_entry+0x40"),
        "decompile_tokens": ("CWorldPhysicsManager__ClearEntryWorkSets_40_50(void *definition_entry)", "CSPtrSet__Clear"),
    },
    "0x00511440": {
        "raw": "00511440",
        "name": "CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName",
        "signature": "int __cdecl CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName(char * thing_name)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "allowlist-gate", "spawner"},
        "comment_tokens": ("CSpawnerThng__ProcessSpawnWave", "thing_name", "0x17"),
        "decompile_tokens": ("CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName(char *thing_name)", "DAT_008553fc"),
    },
    "0x005115b0": {
        "raw": "005115b0",
        "name": "CWorldPhysicsManager__MapGunOrSpawnerTagToIndex",
        "signature": "int __cdecl CWorldPhysicsManager__MapGunOrSpawnerTagToIndex(char * tag_name)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "tag-map", "gun-tag", "spawner-tag"},
        "comment_tokens": ("GunA..GunI", "SpawnerA..SpawnerE", "returning 0"),
        "decompile_tokens": ("CWorldPhysicsManager__MapGunOrSpawnerTagToIndex(char *tag_name)", "stricmp"),
    },
    "0x00511720": {
        "raw": "00511720",
        "name": "CWorldPhysicsManager__ResolveTagListNameToIndex_E8",
        "signature": "void __thiscall CWorldPhysicsManager__ResolveTagListNameToIndex_E8(void * this, char * tag_name)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "name-resolve", "phantom-param-removed"},
        "comment_tokens": ("prior extra Ghidra stack parameter was phantom", "this+0xe8", "DAT_008553f8"),
        "decompile_tokens": ("CWorldPhysicsManager__ResolveTagListNameToIndex_E8(void *this,char *tag_name)", "0xe8"),
    },
    "0x005117c0": {
        "raw": "005117c0",
        "name": "CWorldPhysicsManager__ResolveTagListNameToIndex_EC",
        "signature": "void __thiscall CWorldPhysicsManager__ResolveTagListNameToIndex_EC(void * this, char * tag_name)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "name-resolve", "phantom-param-removed"},
        "comment_tokens": ("prior extra Ghidra stack parameter was phantom", "this+0xec", "DAT_008553f8"),
        "decompile_tokens": ("CWorldPhysicsManager__ResolveTagListNameToIndex_EC(void *this,char *tag_name)", "0xec"),
    },
    "0x00511860": {
        "raw": "00511860",
        "name": "CWorldPhysicsManager__ResolveTagListNameToIndex_F0",
        "signature": "void __thiscall CWorldPhysicsManager__ResolveTagListNameToIndex_F0(void * this, char * tag_name)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "name-resolve", "phantom-param-removed"},
        "comment_tokens": ("prior extra Ghidra stack parameter was phantom", "this+0xf0", "DAT_008553f8"),
        "decompile_tokens": ("CWorldPhysicsManager__ResolveTagListNameToIndex_F0(void *this,char *tag_name)", "0xf0"),
    },
    "0x00511900": {
        "raw": "00511900",
        "name": "CWorldPhysicsManager__AddComponentByName",
        "signature": "void __thiscall CWorldPhysicsManager__AddComponentByName(void * this, int link_value, char * component_name)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "add-by-name", "component-definition"},
        "comment_tokens": ("component_name", "link_value", "this+0x5c"),
        "decompile_tokens": ("CWorldPhysicsManager__AddComponentByName(void *this,int link_value,char *component_name)", "CSPtrSet__AddToTail"),
    },
    "0x005119e0": {
        "raw": "005119e0",
        "name": "CWorldPhysicsManager__AddWeaponByName",
        "signature": "void __thiscall CWorldPhysicsManager__AddWeaponByName(void * this, char * weapon_name, char * tag_name, int link_value)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "add-by-name", "weapon", "tag-map"},
        "comment_tokens": ("weapon_name", "tag_name", "this+0x3c"),
        "decompile_tokens": ("CWorldPhysicsManager__AddWeaponByName(void *this,char *weapon_name,char *tag_name,int link_value)", "MapGunOrSpawnerTagToIndex"),
    },
    "0x00511ad0": {
        "raw": "00511ad0",
        "name": "CWorldPhysicsManager__AddSpawnerByName",
        "signature": "void __thiscall CWorldPhysicsManager__AddSpawnerByName(void * this, char * spawner_name, char * tag_name, int link_value)",
        "tags": {"worldphysics-cleanup-resolve-wave559", "add-by-name", "spawner", "tag-map"},
        "comment_tokens": ("spawner_name", "tag_name", "this+0x4c"),
        "decompile_tokens": ("CWorldPhysicsManager__AddSpawnerByName(void *this,char *spawner_name,char *tag_name,int link_value)", "MapGunOrSpawnerTagToIndex"),
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
        if row["status"] != "OK":
            failures.append(f"{address} metadata status is {row['status']}")
        if row["name"] != spec["name"]:
            failures.append(f"{address} name mismatch: {row['name']} != {spec['name']}")
        if row["signature"] != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row['signature']} != {spec['signature']}")
        require_tokens(f"{address} comment", row["comment"], spec["comment_tokens"], failures)

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            present = set(filter(None, tag_row["tags"].split(";")))
            missing_tags = set(spec["tags"]) - present
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")

        decomp_row = decomp_index.get(address)
        if decomp_row is None:
            failures.append(f"{address} missing from post_decompile index")
        elif decomp_row["status"] != "OK":
            failures.append(f"{address} decompile status is {decomp_row['status']}")
        else:
            decomp_file = next((BASE / "post_decompile").glob(f"{spec['raw']}_*.c"), None)
            if decomp_file is None:
                failures.append(f"{address} missing decompile file")
            else:
                require_tokens(f"{address} decompile", read_text(decomp_file), spec["decompile_tokens"], failures)

    require_tokens(
        "xrefs",
        xrefs,
        (
            "CWorldPhysicsManager__ClearAndFreeAllDefinitionLists",
            "CSpawnerThng__ProcessSpawnWave",
            "CDestroyableSegment__VFunc_08_HandleSegmentBreak",
            "CComponentValue02__ApplyToComponentByName",
            "CComponentValue13__ApplyToComponentByName",
        ),
        failures,
    )

    docs = {
        "public note": PUBLIC_NOTE,
        "function index": FUNCTION_INDEX,
        "world index": WORLD_INDEX,
        "ghidra reference": GHIDRA_REFERENCE,
        "campaign": CAMPAIGN,
        "backlog": BACKLOG,
        "ledger": LEDGER,
    }
    for label, path in docs.items():
        text = read_text(path)
        require_tokens(
            label,
            text,
            (
                "Wave559",
                "WorldPhysicsManager cleanup/resolve",
                "CWorldPhysicsManager__AddWeaponByName",
            ),
            failures,
        )
    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run checks and exit nonzero on failure")
    args = parser.parse_args(argv)
    failures = run_check()
    if failures:
        print("Wave559 WorldPhysics cleanup/resolve probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave559 WorldPhysics cleanup/resolve probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
