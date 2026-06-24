#!/usr/bin/env python3
"""Validate Wave497 CRTTree static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave497-crttree-lifecycle-004ddfd0"

COMMON_TAGS = {"static-reaudit", "crttree-wave497", "retail-binary-evidence"}

TARGETS = {
    "0x004dd7b0": {
        "name": "CRTTree__Init",
        "signature_tokens": ("void", "__thiscall", "CRTTree__Init", "void * this", "void * init"),
        "tags": COMMON_TAGS | {"crttree", "boundary-recovered", "init", "render-resource", "vtable-slot-1"},
        "comment_tokens": (
            "CRTTree vtable 0x005deb9c slot 1 boundary",
            "calls CRenderThing__Init(this, init)",
            "init+0x408",
            "this+0x14/+0x18",
            "DAT_0089c9c8",
            "+0x170 refcount",
            "runtime tree rendering",
        ),
        "decompile_tokens": (
            "CRenderThing__Init",
            "CMesh__FindOrCreate",
            "CImposter__FindOrCreate",
            "DAT_0089c9c8",
            "+ 0x170",
            "g_MeshQualityDistance",
        ),
    },
    "0x004dd850": {
        "name": "CRTTree__VFuncSlot03_UpdateVisibilityState",
        "signature_tokens": ("void", "__fastcall", "CRTTree__VFuncSlot03_UpdateVisibilityState", "void * this"),
        "tags": COMMON_TAGS | {"crttree", "boundary-recovered", "visibility-state", "vtable-slot-3"},
        "comment_tokens": (
            "CRTTree vtable 0x005deb9c slot 3 boundary",
            "DAT_0083cd58",
            "tree/render helper through this+0x18",
            "marks this+0x20",
            "runtime visibility behavior",
        ),
        "decompile_tokens": (
            "DAT_0083cd58",
            "CDXEngine__RenderImposterBillboardSet",
            "+ 0x18",
            "+ 0x20",
        ),
    },
    "0x004dd960": {
        "name": "CRTTree__VFuncSlot02_BuildRenderOutputs",
        "signature_tokens": (
            "void",
            "__thiscall",
            "CRTTree__VFuncSlot02_BuildRenderOutputs",
            "void * this",
            "void * renderContext",
        ),
        "tags": COMMON_TAGS | {"crttree", "boundary-recovered", "render-output", "vtable-slot-2"},
        "comment_tokens": (
            "CRTTree vtable 0x005deb9c slot 2 boundary",
            "camera/context transforms",
            "resource/falling-tree state",
            "DAT_0083cd58",
            "CMap/CRender-style helpers",
            "runtime rendering behavior",
        ),
        "decompile_tokens": (
            "DAT_0083cd58",
            "_DAT_005d856c",
            "CDXEngine__SetWorldMatrixElements",
            "CSphere__RenderAnimatedRecursive",
        ),
    },
    "0x004ddfd0": {
        "name": "CRTTree__Destructor",
        "signature_tokens": ("void", "__fastcall", "CRTTree__Destructor", "void * this"),
        "tags": COMMON_TAGS | {"crttree", "comment-hardened", "destructor", "signature-corrected", "vtable-referenced"},
        "comment_tokens": (
            "resets the CRTTree vtable to 0x005deb9c",
            "CDXTrees__HideTree",
            "this+0x14 -> +0x170",
            "CRenderThing vtable 0x005deaac",
            "this+0x10",
            "runtime tree lifetime behavior",
        ),
        "decompile_tokens": (
            "CDXTrees__HideTree",
            "PTR_CRTTree__ScalarDeletingDestructor_005deb9c",
            "+ 0x170",
            "PTR_CRenderThing__scalar_deleting_dtor_005deaac",
            "+ 0x10",
        ),
        "xref_tokens": ("004de080", "CRTTree__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),
    },
    "0x004de050": {
        "name": "CRTTree__VFuncSlot06_GetResourceScalar164",
        "signature_tokens": ("float", "__fastcall", "CRTTree__VFuncSlot06_GetResourceScalar164", "void * this"),
        "tags": COMMON_TAGS | {"crttree", "boundary-recovered", "float-getter", "vtable-slot-6"},
        "comment_tokens": (
            "CRTTree vtable 0x005deb9c slot 6 boundary",
            "this+0x14",
            "resource+0x164",
            "runtime LOD/distance semantics",
        ),
        "decompile_tokens": ("+ 0x14", "+ 0x164"),
    },
    "0x004de060": {
        "name": "SharedVFunc__ReturnResourceField150_004de060",
        "signature_tokens": (
            "void *",
            "__fastcall",
            "SharedVFunc__ReturnResourceField150_004de060",
            "void * this",
        ),
        "tags": COMMON_TAGS | {"crttree", "rtmesh", "shared-vfunc", "boundary-recovered", "resource-getter"},
        "comment_tokens": (
            "shared CRTMesh/CRTTree vtable helper boundary",
            "this+0x14",
            "resource+0x150",
            "CRTMesh vtable 0x005deb1c",
            "CRTTree vtable 0x005deb9c",
        ),
        "decompile_tokens": ("+ 0x14", "+ 0x150"),
    },
    "0x004de080": {
        "name": "CRTTree__ScalarDeletingDestructor",
        "signature_tokens": (
            "void *",
            "__thiscall",
            "CRTTree__ScalarDeletingDestructor",
            "void * this",
            "byte flags",
        ),
        "tags": COMMON_TAGS
        | {"crttree", "name-corrected", "signature-corrected", "scalar-deleting-destructor", "vtable-slot-0"},
        "comment_tokens": (
            "CRTTree vtable 0x005deb9c slot 0 points here",
            "calls CRTTree__Destructor(this)",
            "CDXMemoryManager__Free",
            "flags bit 0",
            "returns this",
        ),
        "decompile_tokens": ("CRTTree__Destructor(this)", "CDXMemoryManager__Free", "flags & 1", "return this"),
    },
    "0x00516580": {
        "name": "PCRTID__CreateObject",
        "signature_tokens": ("void *", "__cdecl", "PCRTID__CreateObject", "int typeId"),
        "tags": COMMON_TAGS | {"pcrtid", "factory", "comment-hardened", "signature-corrected", "crttree"},
        "comment_tokens": (
            "switch factory for PCRTID.cpp render objects",
            "Type 1 allocates 0x50",
            "type 2 allocates 0x34",
            "CRTTree vtable 0x005deb9c",
            "type 4 allocates 0x5c",
            "type 5 allocates 0x28",
            "CRTCutscene__CRTCutscene",
        ),
        "decompile_tokens": (
            "OID__AllocObject(0x50",
            "OID__AllocObject(0x34",
            "PTR_CRTTree__ScalarDeletingDestructor_005deb9c",
            "OID__AllocObject(0x5c",
            "OID__AllocObject(0x28",
            "CRTCutscene__CRTCutscene",
        ),
    },
    "0x004dbd40": {
        "name": "SharedVFunc__ReturnFloat0Ret8_004dbd40",
        "signature_tokens": (
            "float",
            "__thiscall",
            "SharedVFunc__ReturnFloat0Ret8_004dbd40",
            "void * this",
            "void * arg0",
            "void * arg1",
        ),
        "tags": COMMON_TAGS | {"shared-vfunc", "boundary-recovered", "float-return", "vtable-referenced"},
        "comment_tokens": (
            "shared vtable helper boundary",
            "returns the float constant at 0x005d856c",
            "pops two stack arguments",
            "exact virtual contract",
        ),
        "decompile_tokens": ("_DAT_005d856c", "return _DAT_005d856c"),
    },
    "0x004d6a50": {
        "name": "SharedVFunc__WriteDefaultTransformOutputsRet16_004d6a50",
        "signature_tokens": (
            "void",
            "__thiscall",
            "SharedVFunc__WriteDefaultTransformOutputsRet16_004d6a50",
            "void * this",
            "void * outMatrix",
            "void * outVec3",
            "void * outScalar",
            "void * arg3",
        ),
        "tags": COMMON_TAGS | {"crenderthing", "crttree", "shared-vfunc", "boundary-recovered", "default-transform"},
        "comment_tokens": (
            "shared CRenderThing/CRTTree vtable helper boundary",
            "identity-like 3x4 transform",
            "zeros an outVec3 record",
            "0x42b40000",
            "four stack arguments",
        ),
        "decompile_tokens": ("outScalar", "0x42b40000"),
    },
    "0x004dbc00": {
        "name": "SharedVFunc__ReturnFalseRet4_004dbc00",
        "signature_tokens": (
            "byte",
            "__thiscall",
            "SharedVFunc__ReturnFalseRet4_004dbc00",
            "void * this",
            "void * arg0",
        ),
        "tags": COMMON_TAGS | {"shared-vfunc", "boundary-recovered", "return-false", "vtable-referenced"},
        "comment_tokens": (
            "broad shared vtable helper boundary",
            "clears AL",
            "returns false/0",
            "pops one stack argument",
        ),
        "decompile_tokens": ("return 0",),
    },
    "0x004db880": {
        "name": "CRenderThing__ForwardSlot26ToChildSlot68",
        "signature_tokens": (
            "void",
            "__thiscall",
            "CRenderThing__ForwardSlot26ToChildSlot68",
            "void * this",
            "void * arg0",
            "void * arg1",
        ),
        "tags": COMMON_TAGS | {"crenderthing", "shared-vfunc", "boundary-recovered", "child-forwarder"},
        "comment_tokens": (
            "shared render-object forwarding helper boundary",
            "child/owned pointer at this+0x10",
            "child vtable slot at +0x68",
            "CRTTree slot 26",
        ),
        "decompile_tokens": ("+ 0x10", "+ 0x68"),
    },
}

VTABLE_EXPECTATIONS = {
    ("005deb9c", "0"): ("004de080", "CRTTree__ScalarDeletingDestructor", "OK"),
    ("005deb9c", "1"): ("004dd7b0", "CRTTree__Init", "OK"),
    ("005deb9c", "2"): ("004dd960", "CRTTree__VFuncSlot02_BuildRenderOutputs", "OK"),
    ("005deb9c", "3"): ("004dd850", "CRTTree__VFuncSlot03_UpdateVisibilityState", "OK"),
    ("005deb9c", "4"): ("004de060", "SharedVFunc__ReturnResourceField150_004de060", "OK"),
    ("005deb9c", "6"): ("004de050", "CRTTree__VFuncSlot06_GetResourceScalar164", "OK"),
    ("005deb9c", "14"): ("004dbd40", "SharedVFunc__ReturnFloat0Ret8_004dbd40", "OK"),
    ("005deb9c", "17"): ("004d6a50", "SharedVFunc__WriteDefaultTransformOutputsRet16_004d6a50", "OK"),
    ("005deb9c", "20"): ("004dbc00", "SharedVFunc__ReturnFalseRet4_004dbc00", "OK"),
    ("005deb9c", "26"): ("004db880", "CRenderThing__ForwardSlot26ToChildSlot68", "OK"),
    ("005deb9c", "28"): ("00616840", "<no_function>", "NO_FUNCTION_AT_POINTER"),
}

XREF_EXPECTATIONS = (
    ("004ddfd0", "004de080", "CRTTree__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),
    ("004dd7b0", "005deba0", "<no_function>", "DATA"),
    ("004dd850", "005deba8", "<no_function>", "DATA"),
    ("004dd960", "005deba4", "<no_function>", "DATA"),
    ("004de050", "005debb4", "<no_function>", "DATA"),
    ("004de060", "005deb2c", "<no_function>", "DATA"),
    ("004de060", "005debac", "<no_function>", "DATA"),
    ("004de080", "005deb9c", "<no_function>", "DATA"),
    ("004dbd40", "005debd4", "<no_function>", "DATA"),
    ("004d6a50", "005debe0", "<no_function>", "DATA"),
    ("004dbc00", "005debec", "<no_function>", "DATA"),
    ("004db880", "005dec04", "<no_function>", "DATA"),
    ("00516580", "004f86d0", "CUnit__Init", "UNCONDITIONAL_CALL"),
    ("00516580", "00404dd0", "CBattleEngine__Init", "UNCONDITIONAL_CALL"),
    ("00516580", "004176c0", "CThing__InitRenderThingFromInitMeshName", "UNCONDITIONAL_CALL"),
    ("00516580", "004d7b10", "CRocket__Init", "UNCONDITIONAL_CALL"),
    ("00516580", "004df550", "CShell__VFunc_09_004df550", "UNCONDITIONAL_CALL"),
)

EXPECTED_LOG_SUMMARIES = {
    "apply_crttree_wave497_dry.log": {
        "updated": 0,
        "skipped": 3,
        "created": 0,
        "would_create": 9,
        "renamed": 0,
        "would_rename": 1,
        "missing": 0,
        "bad": 0,
    },
    "apply_crttree_wave497_apply.log": {
        "updated": 12,
        "skipped": 0,
        "created": 9,
        "would_create": 0,
        "renamed": 1,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_crttree_wave497_verify_dry.log": {
        "updated": 0,
        "skipped": 12,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}


def load_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing TSV: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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
    rows = load_tsv(base / "post_xrefs.tsv")
    for target, from_function_addr, from_function, ref_type in XREF_EXPECTATIONS:
        found = any(
            row["target_addr"].lower() == target.lower()
            and from_function_addr.lower() in {row["from_addr"].lower(), row["from_function_addr"].lower()}
            and row["from_function"] == from_function
            and row["ref_type"] == ref_type
            for row in rows
        )
        if not found:
            raise AssertionError(f"missing xref {target} from {from_function_addr} {from_function} {ref_type}")
    false_rows = [row for row in rows if row["target_addr"].lower() == "004dbc00"]
    if len(false_rows) < 20:
        raise AssertionError(f"expected broad 004dbc00 shared refs, found {len(false_rows)}")


def check_vtables(base: Path) -> None:
    rows = load_tsv(base / "post_vtable.tsv")
    by_slot = {(row["vtable"].lower(), row["slot_index"]): row for row in rows}
    for key, (pointer, name, status) in VTABLE_EXPECTATIONS.items():
        row = by_slot.get((key[0].lower(), key[1]))
        if row is None:
            raise AssertionError(f"missing vtable slot {key[0]} slot {key[1]}")
        if row["pointer_addr"].lower() != pointer.lower():
            raise AssertionError(f"{key[0]} slot {key[1]} pointer {row['pointer_addr']} != {pointer}")
        if row["function_name"] != name:
            raise AssertionError(f"{key[0]} slot {key[1]} name {row['function_name']} != {name}")
        if row["status"] != status:
            raise AssertionError(f"{key[0]} slot {key[1]} status {row['status']} != {status}")


def check_logs(base: Path) -> None:
    summary_re = re.compile(r"SUMMARY\s+(.+)")
    for name, expected in EXPECTED_LOG_SUMMARIES.items():
        path = base / name
        if not path.exists():
            raise AssertionError(f"missing log: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        if "REPORT: Save succeeded" not in text:
            raise AssertionError(f"{name} missing save success")
        match = summary_re.search(text)
        if not match:
            raise AssertionError(f"{name} missing SUMMARY line")
        actual = {}
        for token in match.group(1).split():
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            actual[key] = int(value)
        for key, expected_value in expected.items():
            actual_value = actual.get(key)
            if actual_value != expected_value:
                raise AssertionError(f"{name} {key} {actual_value} != {expected_value}")


def check(args: argparse.Namespace) -> int:
    base = Path(args.base).resolve()
    check_metadata(base)
    check_tags(base)
    check_decompiles(base)
    check_xrefs(base)
    check_vtables(base)
    check_logs(base)
    print(f"Wave497 CRTTree probe PASS ({len(TARGETS)} targets)")
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
