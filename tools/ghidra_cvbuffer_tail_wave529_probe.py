#!/usr/bin/env python3
"""Validate Wave529 CVBuffer tail static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave529-cvbuffer-tail-004fff00"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cvbuffer_tail_wave529_2026-05-18.md"
GHIDRA_REF = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
STATIC_CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
VBUFFER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuffer.cpp" / "_index.md"

COMMON_TAGS = {
    "comment-hardened",
    "cvbuffer-tail-wave529",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

TARGETS = {
    "0x004fff00": {
        "name": "CVBuffer__ctor_base",
        "signature": "void * __thiscall CVBuffer__ctor_base(void * this)",
        "comment_tokens": ("vtable at 0x005dfb8c", "+0x08", "+0x24", "remain unproven"),
        "tags": {"constructor", "cvbuffer", "direct3d", "vertex-buffer"},
        "decompile_tokens": ("CShaderBase__Init", "+ 0x24", "+ 0x28"),
    },
    "0x004fff60": {
        "name": "CVBuffer__scalar_deleting_dtor",
        "signature": "void * __thiscall CVBuffer__scalar_deleting_dtor(void * this, byte flags)",
        "comment_tokens": ("vtable slot 0", "flags bit 0", "CDXMemoryManager__Free", "remain unproven"),
        "tags": {"cvbuffer", "destructor", "scalar-deleting-destructor", "vtable-slot"},
        "decompile_tokens": ("CVBuffer__dtor_base(this)", "CDXMemoryManager__Free", "flags"),
    },
    "0x004fff80": {
        "name": "CVBuffer__dtor_base",
        "signature": "void __thiscall CVBuffer__dtor_base(void * this)",
        "comment_tokens": ("restores the CVBuffer vtable", "+0x08/+0x28", "+0x24", "remain unproven"),
        "tags": {"cvbuffer", "destructor", "direct3d", "vertex-buffer"},
        "decompile_tokens": ("CDXLandscape__UnlinkNodeFromPrimaryAndSecondaryLists", "PTR_CVBuffer__scalar_deleting_dtor_005dfb8c", "DeviceObject__ctor_like_00512d50"),
    },
    "0x00500020": {
        "name": "CVBuffer__CreateInternal",
        "signature": "int __thiscall CVBuffer__CreateInternal(void * this, int total_bytes, int usage_flags, int fvf_format, int pool_mode)",
        "comment_tokens": ("RET 0x10", "vtable slot 1", "slot 2 otherwise", "remain unproven"),
        "tags": {"create", "cvbuffer", "direct3d", "vtable-dispatch"},
        "decompile_tokens": ("pool_mode", "FatalError_LocalizedStringId", "*(int *)this + 8"),
    },
    "0x00500080": {
        "name": "CVBuffer__CreateDynamic",
        "signature": "bool __thiscall CVBuffer__CreateDynamic(void * this, int vertex_count, int vertex_stride, int fvf_format)",
        "comment_tokens": ("RET 0x0c", "usage flags 0x208", "default-pool mode 0", "remain unproven"),
        "tags": {"create", "cvbuffer", "direct3d", "dynamic-buffer"},
        "decompile_tokens": ("vertex_count", "vertex_stride", "*(int *)this + 8"),
    },
    "0x005000c0": {
        "name": "CVBuffer__Create",
        "signature": "bool __thiscall CVBuffer__Create(void * this, int vertex_count, int vertex_stride, int fvf_format)",
        "comment_tokens": ("RET 0x0c", "managed mode 1", "OID__AllocObject", "remain unproven"),
        "tags": {"create", "cvbuffer", "managed-buffer", "shadow-buffer"},
        "decompile_tokens": ("OID__AllocObject", "*(int *)this + 4", "vertex_count"),
    },
    "0x00500120": {
        "name": "CVBuffer__Restore",
        "signature": "int __thiscall CVBuffer__Restore(void * this)",
        "comment_tokens": ("vtable slot 1", "pool token 1", "flag 0x800", "remain unproven"),
        "tags": {"cvbuffer", "device-loss", "managed-buffer", "restore"},
        "decompile_tokens": ("CEngine__DeviceCall68_CheckError", "0x800", "return iVar1"),
    },
    "0x005001b0": {
        "name": "CVBuffer__Lock",
        "signature": "int __thiscall CVBuffer__Lock(void * this, void * * out_data)",
        "comment_tokens": ("RET 0x4", "out_data", "dirty byte +0x28", "remain unproven"),
        "tags": {"cvbuffer", "direct3d", "lock-unlock", "shadow-buffer"},
        "decompile_tokens": ("out_data", "+ 0x24", "0x800"),
    },
    "0x005001e0": {
        "name": "CVBuffer__Unlock",
        "signature": "int __thiscall CVBuffer__Unlock(void * this)",
        "comment_tokens": ("ECX-only", "dirty byte +0x28", "+0x10 bytes", "remain unproven"),
        "tags": {"cvbuffer", "direct3d", "lock-unlock", "shadow-buffer"},
        "decompile_tokens": ("CVBuffer__Unlock", "0x800", "+ 0x24"),
    },
    "0x00500250": {
        "name": "CVBuffer__CreateDefaultPoolVertexBuffer",
        "signature": "int __thiscall CVBuffer__CreateDefaultPoolVertexBuffer(void * this)",
        "comment_tokens": ("recovered function boundary", "0x005dfb94", "0x005e511c", "0x80004005"),
        "tags": {"create", "cvbuffer", "default-pool", "function-boundary", "vtable-slot"},
        "decompile_tokens": ("CEngine__DeviceCall68_CheckError", "return -0x7fffbffb", "+ 0x20"),
    },
    "0x00500280": {
        "name": "CVBuffer__Release",
        "signature": "int __thiscall CVBuffer__Release(void * this)",
        "comment_tokens": ("vtable slot 3", "mode 0", "returns 0", "remain unproven"),
        "tags": {"cvbuffer", "default-pool", "direct3d", "release"},
        "decompile_tokens": ("IUnknown__ReleaseIfNonNull_ReturnZero", "+ 0x20", "return 0"),
    },
    "0x005002b0": {
        "name": "CVBuffer__ReleaseManaged",
        "signature": "int __thiscall CVBuffer__ReleaseManaged(void * this)",
        "comment_tokens": ("vtable slot 4", "mode 1", "returns 0", "remain unproven"),
        "tags": {"cvbuffer", "direct3d", "managed-buffer", "release"},
        "decompile_tokens": ("IUnknown__ReleaseIfNonNull_ReturnZero", "+ 0x20", "return 0"),
    },
    "0x005002e0": {
        "name": "CVBuffer__EnsureLock",
        "signature": "int __thiscall CVBuffer__EnsureLock(void * this, void * * out_data)",
        "comment_tokens": ("RET 0x4", "0x2800", "0x800", "callers test"),
        "tags": {"cvbuffer", "direct3d", "dynamic-buffer", "lock-unlock"},
        "decompile_tokens": ("out_data", "0x2800", "return iVar2"),
    },
    "0x00500320": {
        "name": "CVBuffer__SetStreamSource",
        "signature": "void __thiscall CVBuffer__SetStreamSource(void * this, int stream_index)",
        "comment_tokens": ("RET 0x4", "0x009c73d4", "vtable offset 400", "remain unproven"),
        "tags": {"cvbuffer", "direct3d", "render-state", "stream-source"},
        "decompile_tokens": ("stream_index", "DAT_009c741c = 1", "+ 400"),
    },
    "0x00500360": {
        "name": "CVBuffer__SetStreamSourceSimple",
        "signature": "void __thiscall CVBuffer__SetStreamSourceSimple(void * this, int stream_index)",
        "comment_tokens": ("RET 0x4", "stream_index", "vtable offset 400", "remain unproven"),
        "tags": {"cvbuffer", "direct3d", "stream-source"},
        "decompile_tokens": ("stream_index", "+ 400", "+ 0x1c"),
    },
    "0x00500390": {
        "name": "CVBuffer__LockRange",
        "signature": "int __thiscall CVBuffer__LockRange(void * this, int offset_bytes, int size_bytes, void * * out_data, int lock_flags)",
        "comment_tokens": ("RET 0x10", "0x80004005", "vtable offset 0x2c", "remain unproven"),
        "tags": {"cvbuffer", "direct3d", "lock-unlock", "range-lock"},
        "decompile_tokens": ("offset_bytes", "size_bytes", "lock_flags"),
    },
}

EXPECTED_XREFS = {
    ("0x004fff00", "0x00500650", "CVBufTexture__ResizeVertexBuffer", "UNCONDITIONAL_CALL"),
    ("0x004fff60", "0x005dfb8c", "<no_function>", "DATA"),
    ("0x004fff80", "0x005503a0", "CDXPatch__Destructor_thunk", "UNCONDITIONAL_CALL"),
    ("0x00500020", "0x00500681", "CVBufTexture__ResizeVertexBuffer", "UNCONDITIONAL_CALL"),
    ("0x00500080", "0x0053a1cd", "CDXBattleLine__LoadTextures", "UNCONDITIONAL_CALL"),
    ("0x005000c0", "0x0053c0b1", "CDXCompass__Init", "UNCONDITIONAL_CALL"),
    ("0x00500120", "0x0048f324", "CDXPatch__RestoreAndRebuildIfDirty", "UNCONDITIONAL_CALL"),
    ("0x005001b0", "0x00544fd3", "CDXLandscape__BuildVertexBuffer", "UNCONDITIONAL_CALL"),
    ("0x005001e0", "0x0055aef2", "CDXTrees__HideTree", "UNCONDITIONAL_CALL"),
    ("0x00500250", "0x005dfb94", "<no_function>", "DATA"),
    ("0x00500250", "0x005e511c", "<no_function>", "DATA"),
    ("0x00500280", "0x005e5120", "<no_function>", "DATA"),
    ("0x005002b0", "0x005e5124", "<no_function>", "DATA"),
    ("0x005002e0", "0x005006b6", "CVBufTexture__ResizeVertexBuffer", "UNCONDITIONAL_CALL"),
    ("0x00500320", "0x00545a31", "CDXLandscape__RenderTerrain", "UNCONDITIONAL_CALL"),
    ("0x00500360", "0x00556aa5", "CDXSurf__Render", "UNCONDITIONAL_CALL"),
    ("0x00500390", "0x0055ae88", "CDXTrees__HideTree", "UNCONDITIONAL_CALL"),
}

EXPECTED_RETS = {
    ("0x004fff7d", "0x4", "CVBuffer__scalar_deleting_dtor"),
    ("0x00500071", "0x10", "CVBuffer__CreateInternal"),
    ("0x005000b4", "0xc", "CVBuffer__CreateDynamic"),
    ("0x00500111", "0xc", "CVBuffer__Create"),
    ("0x005001c3", "0x4", "CVBuffer__Lock"),
    ("0x0050027f", "", "CVBuffer__CreateDefaultPoolVertexBuffer"),
    ("0x00500306", "0x4", "CVBuffer__EnsureLock"),
    ("0x0050034e", "0x4", "CVBuffer__SetStreamSource"),
    ("0x0050037f", "0x4", "CVBuffer__SetStreamSourceSimple"),
    ("0x005003b1", "0x10", "CVBuffer__LockRange"),
}

EXPECTED_VTABLES = {
    ("005dfb8c", "0", "004fff60", "CVBuffer__scalar_deleting_dtor", "OK"),
    ("005dfb8c", "1", "00500120", "CVBuffer__Restore", "OK"),
    ("005dfb8c", "2", "00500250", "CVBuffer__CreateDefaultPoolVertexBuffer", "OK"),
    ("005dfb8c", "3", "00500280", "CVBuffer__Release", "OK"),
    ("005dfb8c", "4", "005002b0", "CVBuffer__ReleaseManaged", "OK"),
    ("005e5114", "2", "00500250", "CVBuffer__CreateDefaultPoolVertexBuffer", "OK"),
}

CONTEXT_TOKENS = (
    "CVBuffer__ctor_base(local_10)",
    "CVBuffer__CreateInternal",
    "CVBuffer__CreateDynamic(pvVar2,500,0x14,0x44)",
    "CVBuffer__EnsureLock(local_14,&local_10)",
    "CVBuffer__SetStreamSource(*(void **)(param_1 + 0x28),0)",
    "CVBuffer__SetStreamSourceSimple(pvVar3,0)",
    "CVBuffer__LockRange",
    "CVBuffer__Unlock",
)

PUBLIC_NOTE_TOKENS = (
    "Wave529",
    "CVBuffer__CreateDefaultPoolVertexBuffer",
    "90 target xref rows",
    "6736 instruction rows",
    "runtime rendering behavior",
    "rebuild parity",
)

DOC_TOKENS = {
    GHIDRA_REF: ("Wave529", "CVBuffer__CreateDefaultPoolVertexBuffer", "6736 instruction rows"),
    STATIC_CAMPAIGN: ("Wave 529: CVBuffer Tail", "created=1", "strict comment-plus-clean-signature proxy"),
    VBUFFER_DOC: ("Wave529", "CVBuffer__CreateDefaultPoolVertexBuffer", "vtable slot 2"),
}


def normalize_addr(value: str) -> str:
    value = (value or "").strip().lower()
    if not value or value.startswith("<"):
        return value
    body = value[2:] if value.startswith("0x") else value
    return f"0x{int(body, 16):08x}"


def compact(value: str) -> str:
    return "".join(" ".join((value or "").replace("`", "").split()).lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "instruction_addr", "function_entry", "pointer_addr"):
            if key in row and row[key]:
                row[key] = normalize_addr(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def row_by(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str]:
    wanted = normalize_addr(address)
    for row in rows:
        if row.get(key) == wanted:
            return row
    raise AssertionError(f"missing row for {address}")


def decomp_file(decomp_dir: Path, address: str, expected_name: str) -> Path:
    candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
    require(bool(candidates), f"missing decompile export for {address}")
    named = [path for path in candidates if expected_name in path.name]
    require(bool(named), f"decompile export for {address} does not contain {expected_name}")
    return named[0]


def check_log(path: Path, expected_summary: str, script_report: bool = False) -> None:
    require(path.exists(), f"missing log: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    require(expected_summary in text, f"{path.name}: missing summary {expected_summary}")
    require("REPORT: Save succeeded" in text, f"{path.name}: missing save success")
    if script_report:
        require("ApplyCVBufferTailWave529.java> REPORT: Save succeeded" in text, f"{path.name}: missing script save report")
    for bad in ("LockException", "MISSING:", "BADNAME:", "BADADDR:", "FAIL:"):
        require(bad not in text, f"{path.name}: contains {bad}")


def check_docs() -> None:
    for path, tokens in DOC_TOKENS.items():
        require(path.exists(), f"missing doc: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            require(token_present(text, token), f"{path.name}: missing {token!r}")
    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    public_text = PUBLIC_NOTE.read_text(encoding="utf-8", errors="replace")
    for token in PUBLIC_NOTE_TOKENS:
        require(token_present(public_text, token), f"public note missing {token!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    base = args.base

    check_log(
        base / "apply_cvbuffer_tail_wave529_dry.log",
        "SUMMARY updated=0 skipped=16 renamed=0 would_rename=3 created=0 would_create=1 missing=0 bad=0",
    )
    check_log(
        base / "apply_cvbuffer_tail_wave529_apply.log",
        "SUMMARY updated=16 skipped=0 renamed=3 would_rename=0 created=1 would_create=0 missing=0 bad=0",
        True,
    )
    check_log(
        base / "apply_cvbuffer_tail_wave529_verify_dry.log",
        "SUMMARY updated=0 skipped=16 renamed=0 would_rename=0 created=0 would_create=0 missing=0 bad=0",
    )

    metadata = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")
    xrefs = read_tsv(base / "post_xrefs.tsv")
    instructions = read_tsv(base / "post_instructions.tsv")
    vtables = read_tsv(base / "post_vtable_slots.tsv")
    require(len(metadata) == len(TARGETS), f"metadata rows {len(metadata)} != {len(TARGETS)}")
    require(len(tags) == len(TARGETS), f"tag rows {len(tags)} != {len(TARGETS)}")
    require(len(xrefs) == 90, f"xref rows {len(xrefs)} != 90")
    require(len(instructions) == 6736, f"instruction rows {len(instructions)} != 6736")
    require(len(vtables) == 20, f"vtable rows {len(vtables)} != 20")

    tags_by_addr = {normalize_addr(row["address"]): row for row in tags}
    for address, expected in TARGETS.items():
        row = row_by(metadata, address)
        require(row["status"] == "OK", f"{address} metadata status {row['status']}")
        require(row["name"] == expected["name"], f"{address} name {row['name']} != {expected['name']}")
        require(row["signature"] == expected["signature"], f"{address} signature mismatch: {row['signature']}")
        for token in expected["comment_tokens"]:
            require(token_present(row["comment"], token), f"{address} comment missing {token!r}")

        tag_row = tags_by_addr[normalize_addr(address)]
        actual_tags = {part.strip() for part in tag_row["tags"].split(";") if part.strip()}
        missing_tags = (COMMON_TAGS | expected["tags"]) - actual_tags
        require(not missing_tags, f"{address} missing tags: {sorted(missing_tags)}")

        path = decomp_file(base / "post_decomp", address, expected["name"])
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in expected["decompile_tokens"]:
            require(token_present(text, token), f"{address} decompile missing {token!r}")
        signature_lines = "\n".join(line for line in text.splitlines()[:12] if "signature:" in line or expected["name"] in line)
        for stale in ("undefined ", "param_1", "param_2", "param_3", "param_4", "param_5"):
            require(stale not in signature_lines, f"{address} stale signature token {stale!r} in decompile header")

    xref_set = {
        (row["target_addr"], row["from_addr"], row["from_function"], row["ref_type"])
        for row in xrefs
    }
    for target, from_addr, function, ref_type in EXPECTED_XREFS:
        normalized = (normalize_addr(target), normalize_addr(from_addr), function, ref_type)
        require(normalized in xref_set, f"missing xref {(target, from_addr, function, ref_type)}")

    for instruction_addr, operands, function_name in EXPECTED_RETS:
        hit = any(
            row["instruction_addr"] == normalize_addr(instruction_addr)
            and row["mnemonic"] == "RET"
            and row.get("operands", "") == operands
            and row.get("function_name", "") == function_name
            for row in instructions
        )
        require(hit, f"missing RET evidence {instruction_addr} {operands} {function_name}")

    vtable_set = {
        (row["vtable"], row["slot_index"], row["pointer_addr"][2:], row["function_name"], row["status"])
        for row in vtables
    }
    for expected in EXPECTED_VTABLES:
        require(expected in vtable_set, f"missing vtable slot {expected}")

    target_index = read_tsv(base / "post_decomp" / "index.tsv")
    context_index = read_tsv(base / "post_context_decomp" / "index.tsv")
    require(len(target_index) == len(TARGETS), f"target decompile rows {len(target_index)} != {len(TARGETS)}")
    require(all(row["status"] == "OK" for row in target_index), "expected all target decompile rows OK")
    require(len(context_index) == 18, f"context index rows {len(context_index)} != 18")
    require(all(row["status"] == "OK" for row in context_index), "expected all context decompile rows OK")
    context_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted((base / "post_context_decomp").glob("*.c"))
    )
    for token in CONTEXT_TOKENS:
        require(token_present(context_text, token), f"context decompile missing {token!r}")

    check_docs()

    print("PASS Wave529 CVBuffer tail static RE evidence verified")
    if not args.check:
        print(f"base={base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
