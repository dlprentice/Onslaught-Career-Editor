#!/usr/bin/env python3
"""Validate Wave557 air-unit lifecycle Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave557-air-unit-lifecycle-0050ed60"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_air_unit_lifecycle_wave557_2026-05-18.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"

DOCS = {
    "WorldPhysicsManager.cpp index": (
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md",
        ("Wave557", "CBigAirUnit__ctor_base", "CWorldPhysicsManager__CreateSquad"),
    ),
    "AirUnit.cpp index": (
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AirUnit.cpp" / "_index.md",
        ("Wave557", "CAirUnit__ctor_base", "CAirUnit__scalar_deleting_dtor"),
    ),
    "Bomber.cpp index": (
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Bomber.cpp" / "_index.md",
        ("Wave557", "CBomber__scalar_deleting_dtor", "CBomber__ClearPtrSetsRemoveFromGlobalListAndDestruct"),
    ),
    "Carrier.cpp index": (
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Carrier.cpp" / "_index.md",
        ("Wave557", "CCarrier__scalar_deleting_dtor", "CCarrier__Destructor"),
    ),
    "GroundAttackAircraft.cpp index": (
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GroundAttackAircraft.cpp" / "_index.md",
        ("Wave557", "CGroundAttackAircraft__scalar_deleting_dtor", "CGroundAttackAircraft__Destructor_VFunc01"),
    ),
    "Infantry.cpp index": (
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Infantry.cpp" / "_index.md",
        ("Wave557", "CInfantryUnit__scalar_deleting_dtor", "CInfantryUnit__Destructor_VFunc01"),
    ),
    "Plane.cpp index": (
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Plane.cpp" / "_index.md",
        ("Wave557", "CPlane__scalar_deleting_dtor", "CPlane__Destructor_VFunc01"),
    ),
    "DiveBomber.cpp index": (
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DiveBomber.cpp" / "_index.md",
        ("Wave557", "CDiveBomber__scalar_deleting_dtor", "CDiveBomber__Destructor_VFunc01"),
    ),
    "Dropship.cpp index": (
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Dropship.cpp" / "_index.md",
        ("Wave557", "CDropship__scalar_deleting_dtor", "CDropship__Destructor_VFunc01"),
    ),
}


TARGETS = {
    "0x0050ed60": {
        "raw": "0050ed60",
        "name": "CBomber__scalar_deleting_dtor",
        "signature": "void * __thiscall CBomber__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"air-unit-lifecycle-wave557", "bomber", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("CBomber primary vtable slot 1", "RET 0x4", "delete_flags bit 0"),
        "decompile_tokens": ("CBomber__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050ed80": {
        "raw": "0050ed80",
        "name": "CBigAirUnit__ctor_base",
        "signature": "void * __fastcall CBigAirUnit__ctor_base(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "big-air-unit", "constructor", "world-physics-manager"},
        "comment_tokens": ("CWorldPhysicsManager__CreateThingByType", "this+0x254", "this+0x26c"),
        "decompile_tokens": ("CBigAirUnit__ctor_base(void *this)", "CUnit__ctor_base"),
    },
    "0x0050ee10": {
        "raw": "0050ee10",
        "name": "CGroundAttackAircraft__scalar_deleting_dtor",
        "signature": "void * __thiscall CGroundAttackAircraft__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"air-unit-lifecycle-wave557", "ground-attack-aircraft", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e2bd0", "RET 0x4", "delete_flags bit 0"),
        "decompile_tokens": ("CGroundAttackAircraft__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050ee30": {
        "raw": "0050ee30",
        "name": "CInfantryUnit__scalar_deleting_dtor",
        "signature": "void * __thiscall CInfantryUnit__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"air-unit-lifecycle-wave557", "infantry-unit", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e2730", "CInfantryUnit__Destructor_VFunc01", "RET 0x4"),
        "decompile_tokens": ("CInfantryUnit__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050ee50": {
        "raw": "0050ee50",
        "name": "CCarrier__scalar_deleting_dtor",
        "signature": "void * __thiscall CCarrier__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"air-unit-lifecycle-wave557", "carrier", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e203c", "CCarrier__Destructor", "delete_flags bit 0"),
        "decompile_tokens": ("CCarrier__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050ee70": {
        "raw": "0050ee70",
        "name": "CDropship__scalar_deleting_dtor",
        "signature": "void * __thiscall CDropship__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"air-unit-lifecycle-wave557", "dropship", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e1ddc", "CDropship__Destructor_VFunc01", "RET 0x4"),
        "decompile_tokens": ("CDropship__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050eeb0": {
        "raw": "0050eeb0",
        "name": "CPlane__scalar_deleting_dtor",
        "signature": "void * __thiscall CPlane__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"air-unit-lifecycle-wave557", "plane", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e1934", "CPlane__Destructor_VFunc01", "RET 0x4"),
        "decompile_tokens": ("CPlane__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050eed0": {
        "raw": "0050eed0",
        "name": "CDiveBomber__scalar_deleting_dtor",
        "signature": "void * __thiscall CDiveBomber__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"air-unit-lifecycle-wave557", "dive-bomber", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e1240", "CDiveBomber__Destructor_VFunc01", "RET 0x4"),
        "decompile_tokens": ("CDiveBomber__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050eef0": {
        "raw": "0050eef0",
        "name": "CCarver__scalar_deleting_dtor",
        "signature": "void * __thiscall CCarver__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"air-unit-lifecycle-wave557", "carver", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e0d90", "CCarver__Destructor_VFunc01", "RET 0x4"),
        "decompile_tokens": ("CCarver__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050ef10": {
        "raw": "0050ef10",
        "name": "CFenrir__scalar_deleting_dtor",
        "signature": "void * __thiscall CFenrir__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"air-unit-lifecycle-wave557", "fenrir", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e0434", "CFenrir__Destructor_VFunc01", "RET 0x4"),
        "decompile_tokens": ("CFenrir__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050ef30": {
        "raw": "0050ef30",
        "name": "CCarrier__Destructor",
        "signature": "void __fastcall CCarrier__Destructor(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "carrier", "destructor-body"},
        "comment_tokens": ("direct xref", "this+0x26c", "CUnit__dtor_base"),
        "decompile_tokens": ("CCarrier__Destructor(void *this)", "CUnit__dtor_base"),
    },
    "0x0050efa0": {
        "raw": "0050efa0",
        "name": "CBomber__ClearPtrSetsRemoveFromGlobalListAndDestruct",
        "signature": "void __fastcall CBomber__ClearPtrSetsRemoveFromGlobalListAndDestruct(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "bomber", "destructor-body"},
        "comment_tokens": ("direct xref", "this+0x26c", "CUnit__dtor_base"),
        "decompile_tokens": ("CBomber__ClearPtrSetsRemoveFromGlobalListAndDestruct(void *this)", "CUnit__dtor_base"),
    },
    "0x0050f010": {
        "raw": "0050f010",
        "name": "CBigAirUnit__scalar_deleting_dtor",
        "signature": "void * __thiscall CBigAirUnit__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"air-unit-lifecycle-wave557", "big-air-unit", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e3528", "CBigAirUnit__Destructor", "RET 0x4"),
        "decompile_tokens": ("CBigAirUnit__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050f030": {
        "raw": "0050f030",
        "name": "CBigAirUnit__Destructor",
        "signature": "void __fastcall CBigAirUnit__Destructor(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "big-air-unit", "destructor-body"},
        "comment_tokens": ("direct xref", "this+0x26c", "CUnit__dtor_base"),
        "decompile_tokens": ("CBigAirUnit__Destructor(void *this)", "CUnit__dtor_base"),
    },
    "0x0050f0a0": {
        "raw": "0050f0a0",
        "name": "CAirUnit__ctor_base",
        "signature": "void * __fastcall CAirUnit__ctor_base(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "air-unit", "constructor", "factory"},
        "comment_tokens": ("multiple aircraft variants", "this+0x254", "this+0x26c"),
        "decompile_tokens": ("CAirUnit__ctor_base(void *this)", "CUnit__ctor_base"),
    },
    "0x0050f130": {
        "raw": "0050f130",
        "name": "CGroundAttackAircraft__Destructor_VFunc01",
        "signature": "void __fastcall CGroundAttackAircraft__Destructor_VFunc01(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "ground-attack-aircraft", "destructor-body"},
        "comment_tokens": ("direct xref", "this+0x26c", "CUnit__dtor_base"),
        "decompile_tokens": ("CGroundAttackAircraft__Destructor_VFunc01(void *this)", "CUnit__dtor_base"),
    },
    "0x0050f1a0": {
        "raw": "0050f1a0",
        "name": "CInfantryUnit__Destructor_VFunc01",
        "signature": "void __fastcall CInfantryUnit__Destructor_VFunc01(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "infantry-unit", "destructor-body", "signature-recovered"},
        "comment_tokens": ("locked no-parameter signature", "this+0x270", "CUnit__dtor_base"),
        "decompile_tokens": ("CInfantryUnit__Destructor_VFunc01(void *this)", "CUnit__dtor_base"),
    },
    "0x0050f1f0": {
        "raw": "0050f1f0",
        "name": "CDropship__Destructor_VFunc01",
        "signature": "void __fastcall CDropship__Destructor_VFunc01(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "dropship", "destructor-body"},
        "comment_tokens": ("direct xref", "this+0x26c", "CUnit__dtor_base"),
        "decompile_tokens": ("CDropship__Destructor_VFunc01(void *this)", "CUnit__dtor_base"),
    },
    "0x0050f260": {
        "raw": "0050f260",
        "name": "CPlane__Destructor_VFunc01",
        "signature": "void __fastcall CPlane__Destructor_VFunc01(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "plane", "destructor-body"},
        "comment_tokens": ("direct xref", "this+0x26c", "CUnit__dtor_base"),
        "decompile_tokens": ("CPlane__Destructor_VFunc01(void *this)", "CUnit__dtor_base"),
    },
    "0x0050f2d0": {
        "raw": "0050f2d0",
        "name": "CDiveBomber__Destructor_VFunc01",
        "signature": "void __fastcall CDiveBomber__Destructor_VFunc01(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "dive-bomber", "destructor-body"},
        "comment_tokens": ("direct xref", "this+0x26c", "CUnit__dtor_base"),
        "decompile_tokens": ("CDiveBomber__Destructor_VFunc01(void *this)", "CUnit__dtor_base"),
    },
    "0x0050f340": {
        "raw": "0050f340",
        "name": "CCarver__Destructor_VFunc01",
        "signature": "void __fastcall CCarver__Destructor_VFunc01(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "carver", "destructor-body"},
        "comment_tokens": ("direct xref", "this+0x26c", "CUnit__dtor_base"),
        "decompile_tokens": ("CCarver__Destructor_VFunc01(void *this)", "CUnit__dtor_base"),
    },
    "0x0050f3b0": {
        "raw": "0050f3b0",
        "name": "CFenrir__Destructor_VFunc01",
        "signature": "void __fastcall CFenrir__Destructor_VFunc01(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "fenrir", "destructor-body"},
        "comment_tokens": ("direct xref", "this+0x26c", "CUnit__dtor_base"),
        "decompile_tokens": ("CFenrir__Destructor_VFunc01(void *this)", "CUnit__dtor_base"),
    },
    "0x0050f420": {
        "raw": "0050f420",
        "name": "CAirUnit__scalar_deleting_dtor",
        "signature": "void * __thiscall CAirUnit__scalar_deleting_dtor(void * this, byte delete_flags)",
        "tags": {"air-unit-lifecycle-wave557", "air-unit", "scalar-deleting-dtor", "vtable-slot-1"},
        "comment_tokens": ("0x005e377c", "RET 0x4", "delete_flags bit 0"),
        "decompile_tokens": ("CAirUnit__scalar_deleting_dtor(void *this,byte delete_flags)", "delete_flags & 1"),
    },
    "0x0050f440": {
        "raw": "0050f440",
        "name": "CAirUnit__ClearPtrSetsRemoveFromGlobalListAndDestruct",
        "signature": "void __fastcall CAirUnit__ClearPtrSetsRemoveFromGlobalListAndDestruct(void * this)",
        "tags": {"air-unit-lifecycle-wave557", "air-unit", "destructor-body"},
        "comment_tokens": ("direct xref", "this+0x26c", "CUnit__dtor_base"),
        "decompile_tokens": ("CAirUnit__ClearPtrSetsRemoveFromGlobalListAndDestruct(void *this)", "CUnit__dtor_base"),
    },
    "0x0050f4b0": {
        "raw": "0050f4b0",
        "name": "CWorldPhysicsManager__CreateSquad",
        "signature": "void * __cdecl CWorldPhysicsManager__CreateSquad(int squad_type)",
        "tags": {"air-unit-lifecycle-wave557", "world-physics-manager", "squad", "factory", "signature-recovered"},
        "comment_tokens": ("squad_type value", "0xb4 CSquad-style", "0x144 CSquadNormal"),
        "decompile_tokens": ("CWorldPhysicsManager__CreateSquad(int squad_type)", "switch(squad_type)"),
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
    vtables = read_text(BASE / "post_vtable_slots.tsv")

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
        for forbidden in ("param_1", "param_2", "ctor_like", "VFunc_01_0050"):
            if forbidden in decomp_text:
                failures.append(f"{address} forbidden decompile token remained: {forbidden}")

    require_tokens(
        "xrefs",
        xrefs,
        (
            "CBomber__scalar_deleting_dtor",
            "CInfantryUnit__scalar_deleting_dtor",
            "CInfantryUnit__Destructor_VFunc01",
            "CWorldPhysicsManager__CreateSquad",
            "CSpawnerThng__Update",
        ),
        failures,
    )
    require_tokens(
        "vtable slots",
        vtables,
        (
            "005e2e20\t1\t005e2e24",
            "005e272c\t1\t005e2730",
            "CAirUnit__scalar_deleting_dtor",
        ),
        failures,
    )

    docs = {
        "public note": (read_text(PUBLIC_NOTE), ("Wave557", "CBomber__scalar_deleting_dtor", "CWorldPhysicsManager__CreateSquad")),
        "function index": (read_text(FUNCTION_INDEX), ("Wave557", "CBigAirUnit__ctor_base", "CAirUnit__ctor_base")),
        "GHIDRA reference": (read_text(GHIDRA_REFERENCE), ("Wave557", "air-unit lifecycle", "CInfantryUnit__Destructor_VFunc01")),
        "static campaign": (read_text(CAMPAIGN), ("Wave 557", "air-unit lifecycle", "25 adjacent")),
        "mutation backlog": (read_text(BACKLOG), ("Wave557", "CBigAirUnit__ctor_base", "CWorldPhysicsManager__CreateSquad")),
        "mutation ledger": (read_text(LEDGER), ("Wave557", "scalar-deleting destructor", "CreateSquad")),
    }
    for label, (path, tokens) in DOCS.items():
        docs[label] = (read_text(path), tokens)
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
        print(f"Wave557 air-unit lifecycle probe failed to run: {exc}", file=sys.stderr)
        return 1

    if failures:
        print("Wave557 air-unit lifecycle probe FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave557 air-unit lifecycle probe PASS")
    print(f"Validated {len(TARGETS)} targets and docs evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
