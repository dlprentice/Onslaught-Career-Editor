#!/usr/bin/env python3
"""Validate Wave560 queue-tail reference resolver Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave560-queue-tail-005113f0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_queue_tail_refs_wave560_2026-05-18.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
WORLD_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md"
CUNIT_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x005113f0": {
        "raw": "005113f0",
        "name": "CWeaponRound__SetReaderFromGlobalListByIndex",
        "signature": "void __thiscall CWeaponRound__SetReaderFromGlobalListByIndex(void * this, int round_index)",
        "tags": {"queue-tail-refs-wave560", "weapon-round", "phantom-param-removed"},
        "comment_tokens": ("DAT_008553f0", "round_index", "this+0x18", "CWeaponRound__ApplyToWeaponModeByName"),
        "decompile_tokens": ("CWeaponRound__SetReaderFromGlobalListByIndex(void *this,int round_index)", "DAT_008553f0"),
    },
    "0x00511510": {
        "raw": "00511510",
        "name": "CUnit__GetTypePriorityWeight",
        "signature": "int __cdecl CUnit__GetTypePriorityWeight(void * unit_or_definition)",
        "tags": {"queue-tail-refs-wave560", "unit", "spawn-accounting"},
        "comment_tokens": ("unit_or_definition+0xe0", "CSpawnerThng__UpdateSpawnCount", "CUnit__MarkDestroyedAndCleanupLinks"),
        "decompile_tokens": ("CUnit__GetTypePriorityWeight(void *unit_or_definition)", "0xe0"),
    },
    "0x00511bc0": {
        "raw": "00511bc0",
        "name": "CVBufTexture__FindListEntryByPair",
        "signature": "int * __thiscall CVBufTexture__FindListEntryByPair(void * this, int emitter_slot_tag, int cache_key)",
        "tags": {"queue-tail-refs-wave560", "unit-transform", "cache-lookup"},
        "comment_tokens": ("this+0x6c", "this+0x74", "emitter_slot_tag", "cache_key"),
        "decompile_tokens": ("CVBufTexture__FindListEntryByPair(void *this,int emitter_slot_tag,int cache_key)", "this+0x6c"),
    },
    "0x00511c10": {
        "raw": "00511c10",
        "name": "CFeatureTexture__SetTagListIndexOrMinusOne",
        "signature": "void __thiscall CFeatureTexture__SetTagListIndexOrMinusOne(void * this, char * tag_name)",
        "tags": {"queue-tail-refs-wave560", "feature-texture", "tag-definition", "renamed"},
        "comment_tokens": ("DAT_00855404", "DAT_008553f8", "this+0x8", "-1"),
        "decompile_tokens": ("CFeatureTexture__SetTagListIndexOrMinusOne(void *this,char *tag_name)", "DAT_008553f8"),
    },
    "0x00511ca0": {
        "raw": "00511ca0",
        "name": "CWorldPhysicsManager__ResolveWeaponModeStatementRefs",
        "signature": "void __fastcall CWorldPhysicsManager__ResolveWeaponModeStatementRefs(void * weapon_mode_statement)",
        "tags": {"queue-tail-refs-wave560", "weapon-mode", "definition-resolve", "renamed"},
        "comment_tokens": ("DAT_008553ec", "+0x1c", "+0x2c", "CSoundManager__GetEffectByName"),
        "decompile_tokens": ("CWorldPhysicsManager__ResolveWeaponModeStatementRefs(void *weapon_mode_statement)", "CSoundManager__GetEffectByName"),
    },
    "0x00511d20": {
        "raw": "00511d20",
        "name": "CWorldPhysicsManager__ResolveTagDefinitionRefs",
        "signature": "void __fastcall CWorldPhysicsManager__ResolveTagDefinitionRefs(void * tag_definition)",
        "tags": {"queue-tail-refs-wave560", "tag-definition", "definition-resolve", "renamed"},
        "comment_tokens": ("DAT_008553f8", "+0x18", "+0x2c", "CSoundManager__GetEffectByName"),
        "decompile_tokens": ("CWorldPhysicsManager__ResolveTagDefinitionRefs(void *tag_definition)", "CSoundManager__GetEffectByName"),
    },
    "0x00511db0": {
        "raw": "00511db0",
        "name": "CWorldPhysicsManager__ResolveThingOrComponentDefinitionRefs",
        "signature": "void __fastcall CWorldPhysicsManager__ResolveThingOrComponentDefinitionRefs(void * definition_entry)",
        "tags": {"queue-tail-refs-wave560", "thing-definition", "component-definition", "renamed"},
        "comment_tokens": ("DAT_008553fc", "DAT_00855400", "+0xa8", "+0xac"),
        "decompile_tokens": ("CWorldPhysicsManager__ResolveThingOrComponentDefinitionRefs(void *definition_entry)", "CSoundManager__GetEffectByName"),
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
            "CWeaponRound__ApplyToWeaponModeByName",
            "CSpawnerThng__UpdateSpawnCount",
            "CUnit__UpdateTransform",
            "CFeatureTexture__ApplyToFeatureByName",
            "CWorldPhysicsManager__ResolveLoadedDefinitionReferences",
        ),
        failures,
    )

    docs = {
        "public note": PUBLIC_NOTE,
        "function index": FUNCTION_INDEX,
        "world index": WORLD_INDEX,
        "cunit index": CUNIT_INDEX,
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
                "Wave560",
                "queue-tail reference resolver",
                "CWorldPhysicsManager__ResolveThingOrComponentDefinitionRefs",
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
        print("Wave560 queue-tail reference resolver probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave560 queue-tail reference resolver probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
