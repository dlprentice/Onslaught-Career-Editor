#!/usr/bin/env python3
"""Validate the saved Ghidra seek/behaviour/navmap/state tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "seek-behavior-state-wave344" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave344",
    "physics-script",
    "seek-behavior-state-tranche",
    "retail-binary-evidence",
]


def target(name: str, signature: list[str], comment: list[str], tags: list[str]) -> dict[str, object]:
    return {"name": name, "signature": signature, "comment": comment, "tags": COMMON_TAGS + tags}


def factory(name: str, family: str, ids: str) -> dict[str, object]:
    return target(
        name,
        ["void *", "__cdecl", name, "int valueType"],
        ["Hardened", family, ids, "Exact value semantics", "remain unproven"],
        ["value-factory", family],
    )


def leaf(name: str, base: str, family: str) -> dict[str, object]:
    return target(
        name,
        ["void *", "__thiscall", name, "int flags"],
        ["Shared scalar-deleting destructor", base, "OID__FreeObject", "Runtime behavior remains unproven"],
        ["destructor", "shared-vtable-slot", family],
    )


def base_dtor(name: str, vtable: str, family: str) -> dict[str, object]:
    return target(
        name,
        ["void *", "__thiscall", name, "int flags"],
        ["Recovered base scalar-deleting destructor", vtable, "OID__FreeObject", "class layout remains unproven"],
        ["destructor", "function-boundary", family],
    )


def dtor_base(name: str, vtable: str, family: str) -> dict[str, object]:
    return target(
        name,
        ["void", "__fastcall", name, "void * this"],
        ["Destructor base body", vtable, "Corrects earlier constructor-like naming", "layout remains unproven"],
        ["destructor", "value-base", family],
    )


TARGETS: dict[str, dict[str, object]] = {
    "0x0043dcd0": factory("CPhysicsScriptStatements__CreateStatementType11", "type-11-seek", "1..3"),
    "0x0043dd60": base_dtor("CPhysicsSeekType__scalar_deleting_dtor", "0x005dab20", "type-11-seek"),
    "0x0043dd90": leaf("CPhysicsSeekTypeLeaf__shared_scalar_deleting_dtor", "CPhysicsSeekType__dtor_base", "type-11-seek"),
    "0x0043ddb0": dtor_base("CPhysicsSeekType__dtor_base", "0x005dab20", "type-11-seek"),
    "0x0043ddc0": factory("CPhysicsScriptStatements__CreateStatementType12", "type-12-behaviour", "0x1..0x19"),
    "0x0043e2b0": leaf("CPhysicsBehaviourTypeLeaf__shared_scalar_deleting_dtor", "CPhysicsBehaviourType__dtor_base", "type-12-behaviour"),
    "0x0043e2d0": base_dtor("CPhysicsBehaviourType__scalar_deleting_dtor", "0x005dac58", "type-12-behaviour"),
    "0x0043e300": dtor_base("CPhysicsBehaviourType__dtor_base", "0x005dac58", "type-12-behaviour"),
    "0x0043e310": factory("CPhysicsScriptStatements__CreateStatementType13", "type-13-alligence", "1..3"),
    "0x0043e3a0": leaf("CPhysicsAlligenceTypeLeaf__shared_scalar_deleting_dtor", "CPhysicsAlligenceType__dtor_base", "type-13-alligence"),
    "0x0043e3c0": dtor_base("CPhysicsAlligenceType__dtor_base", "0x005dac88", "type-13-alligence"),
    "0x0043e3d0": base_dtor("CPhysicsAlligenceType__scalar_deleting_dtor", "0x005dac88", "type-13-alligence"),
    "0x0043e400": factory("CPhysicsScriptStatements__CreateStatementType14", "type-14-navmap", "1..4"),
    "0x0043e4e0": leaf("CPhysicsNavMapTypeLeaf__shared_scalar_deleting_dtor", "CPhysicsNavMapType__dtor_base", "type-14-navmap"),
    "0x0043e500": base_dtor("CPhysicsNavMapType__scalar_deleting_dtor", "0x005dacc4", "type-14-navmap"),
    "0x0043e530": dtor_base("CPhysicsNavMapType__dtor_base", "0x005dacc4", "type-14-navmap"),
    "0x0043e540": factory("CPhysicsScriptStatements__CreateStatementType15", "type-15-state", "1..3"),
    "0x0043e5d0": leaf("CPhysicsStateTypeLeaf__shared_scalar_deleting_dtor", "CPhysicsStateType__dtor_base", "type-15-state"),
    "0x0043e5f0": base_dtor("CPhysicsStateType__scalar_deleting_dtor", "0x005dacf4", "type-15-state"),
    "0x0043e620": dtor_base("CPhysicsStateType__dtor_base", "0x005dacf4", "type-15-state"),
    "0x0043e630": target(
        "CFlexArray__SkipBytesFromMemBuffer",
        ["void", "__cdecl", "CFlexArray__SkipBytesFromMemBuffer", "void * memBuffer", "int byteCount"],
        ["Skips byteCount bytes", "CDXMemBuffer__Read", "shared serialization helper"],
        ["shared-serialization", "byte-skip-helper"],
    ),
}

STALE_NAMES = [
    "VFuncSlot_00_0043dd90",
    "CPhysicsSeekType__ctor_like_0043ddb0",
    "CPhysicsBehaviourType__ctor_like_0043e300",
    "VFuncSlot_00_0043e3a0",
    "CPhysicsAlligenceType__ctor_like_0043e3c0",
    "VFuncSlot_00_0043e4e0",
    "CPhysicsNavMapType__ctor_like_0043e530",
    "VFuncSlot_00_0043e5d0",
    "CPhysicsStateType__ctor_like_0043e620",
]

EXPECTED_XREFS = [
    ("0x0043dcd0", "0x00439598"),
    ("0x0043dd60", "0x005dab20"),
    ("0x0043dd90", "0x005daafc"),
    ("0x0043dd90", "0x005dab14"),
    ("0x0043ddc0", "0x004330c8"),
    ("0x0043e2b0", "0x005dab2c"),
    ("0x0043e2b0", "0x005dac4c"),
    ("0x0043e310", "0x00432a38"),
    ("0x0043e3a0", "0x005dac64"),
    ("0x0043e400", "0x00432f88"),
    ("0x0043e4e0", "0x005dac94"),
    ("0x0043e540", "0x00439ab8"),
    ("0x0043e5d0", "0x005dacd0"),
    ("0x0043e630", "0x0042ea21"),
]

EXPECTED_VTABLE_SLOT0 = [
    ("0x005daafc", "CPhysicsSeekTypeLeaf__shared_scalar_deleting_dtor"),
    ("0x005dab08", "CPhysicsSeekTypeLeaf__shared_scalar_deleting_dtor"),
    ("0x005dab14", "CPhysicsSeekTypeLeaf__shared_scalar_deleting_dtor"),
    ("0x005dab20", "CPhysicsSeekType__scalar_deleting_dtor"),
    ("0x005dab2c", "CPhysicsBehaviourTypeLeaf__shared_scalar_deleting_dtor"),
    ("0x005dac4c", "CPhysicsBehaviourTypeLeaf__shared_scalar_deleting_dtor"),
    ("0x005dac58", "CPhysicsBehaviourType__scalar_deleting_dtor"),
    ("0x005dac64", "CPhysicsAlligenceTypeLeaf__shared_scalar_deleting_dtor"),
    ("0x005dac7c", "CPhysicsAlligenceTypeLeaf__shared_scalar_deleting_dtor"),
    ("0x005dac88", "CPhysicsAlligenceType__scalar_deleting_dtor"),
    ("0x005dac94", "CPhysicsNavMapTypeLeaf__shared_scalar_deleting_dtor"),
    ("0x005dacb8", "CPhysicsNavMapTypeLeaf__shared_scalar_deleting_dtor"),
    ("0x005dacc4", "CPhysicsNavMapType__scalar_deleting_dtor"),
    ("0x005dacd0", "CPhysicsStateTypeLeaf__shared_scalar_deleting_dtor"),
    ("0x005dace8", "CPhysicsStateTypeLeaf__shared_scalar_deleting_dtor"),
    ("0x005dacf4", "CPhysicsStateType__scalar_deleting_dtor"),
]


def norm_addr(value: str) -> str:
    value = value.strip().lower()
    if not value:
        return "0x00000000"
    if not value.startswith("0x"):
        value = "0x" + value
    return f"0x{int(value, 16):08x}"


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def decompile_file_exists(decompile_dir: Path, address: str, name: str) -> bool:
    stem = address[2:].lower()
    return any(path.name.lower().startswith(stem) and name.lower() in path.name.lower() for path in decompile_dir.glob("*.c"))


def contains_all(haystack: str, tokens: list[str]) -> bool:
    lowered = haystack.lower()
    return all(token.lower() in lowered for token in tokens)


def run_check(base: Path) -> tuple[list[str], dict[str, object]]:
    metadata = read_tsv(base / "metadata.tsv")
    tags = read_tsv(base / "tags.tsv")
    xrefs = read_tsv(base / "xrefs.tsv")
    vtable_slots = read_tsv(base / "vtable_slots.tsv")
    decompile_dir = base / "decompile"

    failures: list[str] = []
    metadata_by_addr = {norm_addr(row.get("address", "")): row for row in metadata}
    tags_by_addr = {norm_addr(row.get("address", "")): row for row in tags}
    xref_pairs = {(norm_addr(row.get("target_addr", "")), norm_addr(row.get("from_addr", ""))) for row in xrefs}
    slot0 = {
        (norm_addr(row.get("vtable", "")), row.get("slot_index", "")): row.get("function_name", "")
        for row in vtable_slots
    }

    for address, spec in TARGETS.items():
        address = norm_addr(address)
        row = metadata_by_addr.get(address)
        if not row:
            failures.append(f"missing metadata row for {address}")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name {row.get('name')} != {spec['name']}")
        if not contains_all(row.get("signature", ""), spec["signature"]):  # type: ignore[arg-type]
            failures.append(f"{address} signature missing tokens: {spec['signature']}")
        if not contains_all(row.get("comment", ""), spec["comment"]):  # type: ignore[arg-type]
            failures.append(f"{address} comment missing tokens: {spec['comment']}")
        tag_row = tags_by_addr.get(address)
        if not tag_row or not contains_all(tag_row.get("tags", ""), spec["tags"]):  # type: ignore[arg-type]
            failures.append(f"{address} tags missing tokens: {spec['tags']}")
        if not decompile_file_exists(decompile_dir, address, str(spec["name"])):
            failures.append(f"{address} decompile file missing expected name {spec['name']}")

    names = {row.get("name", "") for row in metadata}
    for stale in STALE_NAMES:
        if stale in names:
            failures.append(f"stale name still present: {stale}")

    for target_addr, from_addr in EXPECTED_XREFS:
        pair = (norm_addr(target_addr), norm_addr(from_addr))
        if pair not in xref_pairs:
            failures.append(f"missing xref pair {pair[1]} -> {pair[0]}")

    for vtable, expected_name in EXPECTED_VTABLE_SLOT0:
        actual = slot0.get((norm_addr(vtable), "0"))
        if actual != expected_name:
            failures.append(f"{vtable} slot0 {actual} != {expected_name}")

    summary = {
        "status": "PASS" if not failures else "FAIL",
        "targets": len(TARGETS),
        "metadata_rows": len(metadata),
        "tag_rows": len(tags),
        "xref_rows": len(xrefs),
        "vtable_slot_rows": len(vtable_slots),
        "decompile_files": len(list(decompile_dir.glob("*.c"))) if decompile_dir.exists() else 0,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "failures": failures,
    }
    return failures, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    failures, summary = run_check(args.base)
    out = args.json_out or args.base / "seek-behaviour-state-tranche.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
