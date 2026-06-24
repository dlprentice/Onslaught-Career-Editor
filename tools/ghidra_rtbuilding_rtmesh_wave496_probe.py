#!/usr/bin/env python3
"""Validate Wave496 CRTBuilding/CRTMesh static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave496-rtbuilding-rtmesh-004db850"

COMMON_TAGS = {
    "static-reaudit",
    "rtbuilding-rtmesh-wave496",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x004db850": {
        "name": "CRTBuilding__Destructor",
        "signature_tokens": (
            "void",
            "__fastcall",
            "CRTBuilding__Destructor",
            "void * this",
        ),
        "tags": COMMON_TAGS | {"rtbuilding", "rtmesh", "destructor", "vtable-referenced"},
        "comment_tokens": (
            "Wave496 signature/comment hardening",
            "resets the CRTBuilding vtable to 0x005de9c0",
            "this+0x54 -> +0x170",
            "CRTMesh__Destructor",
            "runtime render-building behavior",
            "rebuild parity remain unproven",
        ),
        "decompile_tokens": (
            "CRTMesh__Destructor",
            "PTR_CRTBuilding__ScalarDeletingDestructor_005de9c0",
            "+ 0x170",
        ),
        "xref_tokens": ("004db8d0", "CRTBuilding__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),
    },
    "0x004db8d0": {
        "name": "CRTBuilding__ScalarDeletingDestructor",
        "signature_tokens": (
            "void *",
            "__thiscall",
            "CRTBuilding__ScalarDeletingDestructor",
            "void * this",
            "byte flags",
        ),
        "tags": COMMON_TAGS
        | {"rtbuilding", "scalar-deleting-destructor", "vtable-slot-0", "name-corrected"},
        "comment_tokens": (
            "CRTBuilding vtable 0x005de9c0 slot 0 points here",
            "calls CRTBuilding__Destructor(this)",
            "flags bit 0",
            "CDXMemoryManager__Free",
            "returns this",
        ),
        "decompile_tokens": (
            "CRTBuilding__Destructor(this)",
            "CDXMemoryManager__Free",
            "flags & 1",
        ),
        "vtable": ("005de9c0", "0", "004db8d0", "CRTBuilding__ScalarDeletingDestructor"),
    },
    "0x004dba40": {
        "name": "CRTBuilding__VFuncSlot10_PickRandomLinkedEntry",
        "signature_tokens": (
            "void *",
            "__fastcall",
            "CRTBuilding__VFuncSlot10_PickRandomLinkedEntry",
            "void * this",
        ),
        "tags": COMMON_TAGS
        | {"rtbuilding", "vtable-slot-10", "name-corrected", "linked-list", "random-selection"},
        "comment_tokens": (
            "CRTBuilding vtable 0x005de9c0 slot 10 points here",
            "this+0x58 count",
            "rand() % count",
            "this+0x54",
            "entry+0x08 next pointer",
        ),
        "decompile_tokens": (
            "_rand()",
            "+ 0x58",
            "+ 0x54",
            "+ 8",
        ),
        "vtable": ("005de9c0", "10", "004dba40", "CRTBuilding__VFuncSlot10_PickRandomLinkedEntry"),
    },
    "0x004dc370": {
        "name": "CRTMesh__Init",
        "signature_tokens": (
            "void",
            "__thiscall",
            "CRTMesh__Init",
            "void * this",
            "void * init",
        ),
        "tags": COMMON_TAGS
        | {"rtmesh", "init", "vtable-slot-1", "console-vars", "mesh-pose", "imposter", "particle-effects"},
        "comment_tokens": (
            "CRTMesh vtable 0x005deb1c slot 1 points here",
            "one-time registers",
            "resolves or falls back to a CMesh",
            "mesh-pose arrays",
            "underscore-prefixed material effect arrays",
            "optionally creates an imposter",
        ),
        "decompile_tokens": (
            "CRenderThing__Init",
            "CConsole__RegisterVariable",
            "CMesh__FindOrCreate",
            "OID__AllocObject",
            "CImposter__FindOrCreate",
        ),
        "vtable": ("005deb1c", "1", "004dc370", "CRTMesh__Init"),
    },
    "0x004dc950": {
        "name": "CRTMesh__Destructor",
        "signature_tokens": (
            "void",
            "__fastcall",
            "CRTMesh__Destructor",
            "void * this",
        ),
        "tags": COMMON_TAGS
        | {"rtmesh", "destructor", "linked-list", "particle-effects", "resource-free"},
        "comment_tokens": (
            "resets the CRTMesh vtable to 0x005deb1c",
            "DAT_0083cd5c/DAT_0083cd60",
            "active particle effect handles",
            "CRTMesh__FreePoseData",
            "mesh+0x170",
            "CRenderThing vtable",
        ),
        "decompile_tokens": (
            "PTR_CRTMesh__ScalarDeletingDestructor_005deb1c",
            "DAT_0083cd5c",
            "ParticleEffectLink__SetHandleStateAndClear",
            "CRTMesh__FreePoseData",
            "PTR_CRenderThing__scalar_deleting_dtor_005deaac",
        ),
        "xref_tokens": ("004dcb70", "CRTMesh__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),
    },
    "0x004dcb00": {
        "name": "CRTMesh__FreePoseData",
        "signature_tokens": (
            "void",
            "__fastcall",
            "CRTMesh__FreePoseData",
            "void * poseData",
        ),
        "tags": COMMON_TAGS | {"rtmesh", "mesh-pose", "resource-free"},
        "comment_tokens": (
            "register-only poseData helper",
            "+0x00/+0x04/+0x08/+0x0c",
            "CDXMemoryManager__Free",
            "nulling each slot",
            "meshpose structure layout",
        ),
        "decompile_tokens": (
            "CDXMemoryManager__Free",
            "poseData",
            "+ 4",
            "+ 8",
            "+ 0xc",
        ),
        "xref_tokens": ("004dc950", "CRTMesh__Destructor", "UNCONDITIONAL_CALL"),
    },
    "0x004dcb70": {
        "name": "CRTMesh__ScalarDeletingDestructor",
        "signature_tokens": (
            "void *",
            "__thiscall",
            "CRTMesh__ScalarDeletingDestructor",
            "void * this",
            "byte flags",
        ),
        "tags": COMMON_TAGS | {"rtmesh", "scalar-deleting-destructor", "vtable-slot-0"},
        "comment_tokens": (
            "CRTMesh vtable 0x005deb1c slot 0 points here",
            "calls CRTMesh__Destructor(this)",
            "flags bit 0",
            "CDXMemoryManager__Free",
            "returns this",
        ),
        "decompile_tokens": (
            "CRTMesh__Destructor(this)",
            "CDXMemoryManager__Free",
            "flags & 1",
        ),
        "vtable": ("005deb1c", "0", "004dcb70", "CRTMesh__ScalarDeletingDestructor"),
    },
    "0x004dd0c0": {
        "name": "CRTMesh__CleanupAllEffects",
        "signature_tokens": (
            "void",
            "CRTMesh__CleanupAllEffects",
            "(void)",
        ),
        "tags": COMMON_TAGS | {"rtmesh", "static-helper", "linked-list", "particle-effects", "resource-free"},
        "comment_tokens": (
            "static no-argument cleanup",
            "DAT_0083cd5c",
            "DAT_0083cd60",
            "ParticleEffectLink__SetHandleStateAndClear",
            "CParticleManager__RemoveFromGlobalList",
            "runtime render-loop behavior",
        ),
        "decompile_tokens": (
            "DAT_0083cd5c",
            "DAT_0083cd60",
            "ParticleEffectLink__SetHandleStateAndClear",
            "CParticleManager__RemoveFromGlobalList",
        ),
        "xref_tokens": ("0053e2e0", "CDXEngine__Render", "UNCONDITIONAL_CALL"),
    },
    "0x004dd6b0": {
        "name": "CRTMesh__SetQualityLevel",
        "signature_tokens": (
            "void",
            "CRTMesh__SetQualityLevel",
            "int qualityLevel",
        ),
        "tags": COMMON_TAGS | {"rtmesh", "static-helper", "quality-level", "lod"},
        "comment_tokens": (
            "static quality setter",
            "levels 0, 1, and 2",
            "g_MeshQualityDistance",
            "g_MeshLodBias",
            "_g_MeshQualityScaleFactor",
            "runtime visual behavior",
        ),
        "decompile_tokens": (
            "qualityLevel == 0",
            "qualityLevel == 1",
            "qualityLevel == 2",
            "g_MeshQualityDistance",
            "g_MeshLodBias",
            "CVar__SetValueRounded",
        ),
        "xref_tokens": ("004cef50", "CTreeDetail__SetQualityLevel", "UNCONDITIONAL_CALL"),
    },
    "0x004dd770": {
        "name": "CRTMesh__GetQualityLevel",
        "signature_tokens": (
            "int",
            "CRTMesh__GetQualityLevel",
            "(void)",
        ),
        "tags": COMMON_TAGS | {"rtmesh", "static-helper", "quality-level", "lod"},
        "comment_tokens": (
            "static no-argument getter",
            "g_MeshQualityDistance",
            "returns 0",
            "otherwise 2",
            "PauseMenu/CPauseMenu quality UI paths",
            "runtime visual behavior",
        ),
        "decompile_tokens": (
            "g_MeshQualityDistance",
            "return 0",
            "iVar1 = 2",
            "iVar1 = 1",
        ),
        "xref_tokens": ("004cde60", "PauseMenu__Init", "UNCONDITIONAL_CALL"),
    },
}


def load_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing TSV: {path}")
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


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
    text = (base / "post_xrefs.tsv").read_text(encoding="utf-8", errors="replace")
    for address, spec in TARGETS.items():
        tokens = spec.get("xref_tokens")
        if tokens:
            require_tokens(text, (address[2:],) + tokens, f"{address} xrefs")


def check_vtables(base: Path) -> None:
    rows = load_tsv(base / "post_vtable.tsv")
    by_slot = {
        (row["vtable"].lower(), row["slot_index"], row["pointer_addr"].lower()): row
        for row in rows
    }
    for address, spec in TARGETS.items():
        expected = spec.get("vtable")
        if not expected:
            continue
        vtable, slot, pointer, name = expected
        row = by_slot.get((vtable.lower(), slot, pointer.lower()))
        if row is None:
            raise AssertionError(f"missing vtable slot {vtable} slot {slot} -> {pointer}")
        if row["function_name"] != name:
            raise AssertionError(f"{vtable} slot {slot} name {row['function_name']} != {name}")


def check(args: argparse.Namespace) -> int:
    base = Path(args.base).resolve()
    check_metadata(base)
    check_tags(base)
    check_decompiles(base)
    check_xrefs(base)
    check_vtables(base)
    print(f"Wave496 CRTBuilding/CRTMesh probe PASS ({len(TARGETS)} targets)")
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
