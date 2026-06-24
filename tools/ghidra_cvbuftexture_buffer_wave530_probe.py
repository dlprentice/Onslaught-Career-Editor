#!/usr/bin/env python3
"""Validate Wave530 CVBufTexture buffer-management static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave530-cvbuftexture-buffer-005003f0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cvbuftexture_buffer_wave530_2026-05-18.md"
GHIDRA_REF = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
STATIC_CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"

COMMON_TAGS = {
    "comment-hardened",
    "cvbuftexture-buffer-wave530",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

TARGETS = {
    "0x005003f0": {
        "name": "CVBufTexture__CVBufTexture",
        "signature": "void __thiscall CVBufTexture__CVBufTexture(void * this, void * texture)",
        "comment_tokens": ("RET 0x4", "global list head 0x00854e00", "texture pointer at +0x00", "remain unproven"),
        "tags": {"buffer-management", "constructor", "cvbuftexture", "texture-reference"},
        "decompile_tokens": ("DAT_00854e00", "texture", "+ 0xa4"),
    },
    "0x00500460": {
        "name": "CVBufTexture__dtor",
        "signature": "void __thiscall CVBufTexture__dtor(void * this)",
        "comment_tokens": ("ECX-only destructor", "CHud__DecrementCounter9C", "global CVBufTexture list", "remain unproven"),
        "tags": {"buffer-management", "cvbuftexture", "destructor", "texture-reference"},
        "decompile_tokens": ("CHud__DecrementCounter9C", "CVBuffer__Unlock", "CIBuffer__Unlock"),
    },
    "0x00500540": {
        "name": "CVBufTexture__SetVBFormat",
        "signature": "void __thiscall CVBufTexture__SetVBFormat(void * this, int fvf_format, int usage_flags, int vertex_stride, int primitive_type, int pool_mode)",
        "comment_tokens": ("RET 0x14", "usage flags at +0x08", "0xfffffdf7", "remain unproven"),
        "tags": {"cvbuftexture", "direct3d", "format", "vertex-buffer"},
        "decompile_tokens": ("DAT_00854dec", "pool_mode = 1", "vertex_stride"),
    },
    "0x00500590": {
        "name": "CVBufTexture__SetIBFormat",
        "signature": "void __thiscall CVBufTexture__SetIBFormat(void * this, int index_format, int usage_flags, int reserved, int pool_mode)",
        "comment_tokens": ("RET 0x10", "third stack argument", "0xfffffdf7", "remain unproven"),
        "tags": {"cvbuftexture", "direct3d", "format", "index-buffer"},
        "decompile_tokens": ("index_format", "usage_flags", "pool_mode"),
    },
    "0x005005d0": {
        "name": "CVBufTexture__SetPersist",
        "signature": "void __thiscall CVBufTexture__SetPersist(void * this)",
        "comment_tokens": ("ECX-only", "persist byte +0x5c", "remain unproven"),
        "tags": {"cvbuftexture", "persist", "resource-lifetime"},
        "decompile_tokens": ("+ 0x5c", "= 1"),
    },
    "0x005005e0": {
        "name": "CVBufTexture__ResizeVertexBuffer",
        "signature": "void __thiscall CVBufTexture__ResizeVertexBuffer(void * this, int required_bytes)",
        "comment_tokens": ("RET 0x4", "rounds nonzero requests up from 0x400", "CVBuffer", "remain unproven"),
        "tags": {"cvbuftexture", "direct3d", "resize", "vertex-buffer"},
        "decompile_tokens": ("OID__AllocObject(0x2c,0x2c", "CVBuffer__ctor_base", "CVBuffer__CreateInternal", "CVBuffer__EnsureLock"),
    },
    "0x005007f0": {
        "name": "CVBufTexture__ResizeIndexBuffer",
        "signature": "void __thiscall CVBufTexture__ResizeIndexBuffer(void * this, int required_bytes)",
        "comment_tokens": ("RET 0x4", "rounds nonzero requests up from 0x400", "CIBuffer", "remain unproven"),
        "tags": {"cvbuftexture", "direct3d", "index-buffer", "resize"},
        "decompile_tokens": ("OID__AllocObject(0x24,0x2f", "CIBuffer__Constructor", "CIBuffer__CreateConfigured", "CIBuffer__LockDirect"),
    },
    "0x005009c0": {
        "name": "CVBufTexture__UnlockVB",
        "signature": "void __thiscall CVBufTexture__UnlockVB(void * this)",
        "comment_tokens": ("ECX-only", "vertex-lock byte +0x10", "+0x38", "remain unproven"),
        "tags": {"cvbuftexture", "lock-unlock", "vertex-buffer"},
        "decompile_tokens": ("CVBuffer__Unlock", "+ 0x10", "+ 0x38"),
    },
    "0x005009f0": {
        "name": "CVBufTexture__UnlockIB",
        "signature": "void __thiscall CVBufTexture__UnlockIB(void * this)",
        "comment_tokens": ("ECX-only", "index-lock byte +0x2c", "+0x3c", "remain unproven"),
        "tags": {"cvbuftexture", "index-buffer", "lock-unlock"},
        "decompile_tokens": ("CIBuffer__Unlock", "+ 0x2c", "+ 0x3c"),
    },
    "0x00500a10": {
        "name": "CVBufTexture__AddVertices",
        "signature": "int __thiscall CVBufTexture__AddVertices(void * this, void * vertices, int vertex_count)",
        "comment_tokens": ("RET 0x8", "vertex_count * stride", "returns the starting vertex index", "remain unproven"),
        "tags": {"append", "cvbuftexture", "lock-unlock", "vertex-buffer"},
        "decompile_tokens": ("CVBufTexture__ResizeVertexBuffer(this,iVar1)", "CVBuffer__EnsureLock", "HResultToString"),
    },
    "0x00500ac0": {
        "name": "CVBufTexture__AddIndices",
        "signature": "void __thiscall CVBufTexture__AddIndices(void * this, void * indices, int index_count)",
        "comment_tokens": ("RET 0x8", "index_count * 2", "FatalError_LocalizedStringId", "remain unproven"),
        "tags": {"append", "cvbuftexture", "index-buffer", "lock-unlock"},
        "decompile_tokens": ("CVBufTexture__ResizeIndexBuffer(this,iVar2)", "CIBuffer__LockDirect", "index_count * 2"),
    },
    "0x00500b40": {
        "name": "CVBufTexture__GetIndexPtr",
        "signature": "void * __thiscall CVBufTexture__GetIndexPtr(void * this, int index_count)",
        "comment_tokens": ("RET 0x4", "reserves index_count * 2 bytes", "old cursor", "remain unproven"),
        "tags": {"cvbuftexture", "index-buffer", "lock-unlock", "reserve"},
        "decompile_tokens": ("CVBufTexture__ResizeIndexBuffer(this,iVar1)", "CIBuffer__LockDirect", "return (void *)"),
    },
    "0x00500bb0": {
        "name": "CVBufTexture__GetVertexPtr",
        "signature": "int __thiscall CVBufTexture__GetVertexPtr(void * this, void * * out_vertex_ptr, int vertex_count)",
        "comment_tokens": ("RET 0x8", "out_vertex_ptr", "returns the starting vertex index", "remain unproven"),
        "tags": {"cvbuftexture", "lock-unlock", "reserve", "vertex-buffer"},
        "decompile_tokens": ("CVBufTexture__ResizeVertexBuffer(this,iVar1)", "CVBuffer__EnsureLock", "vertex_count"),
    },
    "0x00500c50": {
        "name": "CVBufTexture__GetIndexPrimitiveCount",
        "signature": "int __thiscall CVBufTexture__GetIndexPrimitiveCount(void * this)",
        "comment_tokens": ("ECX-only", "byte cursor +0x34", "primitive type +0x50", "remain unproven"),
        "tags": {"cvbuftexture", "index-buffer", "primitive-count", "rendering"},
        "decompile_tokens": ("+ 0x34", "+ 0x50", "return iVar2 / 3"),
    },
    "0x00500cb0": {
        "name": "CVBufTexture__GetVertexPrimitiveCount",
        "signature": "int __thiscall CVBufTexture__GetVertexPrimitiveCount(void * this)",
        "comment_tokens": ("ECX-only", "vertex byte cursor +0x1c", "stride +0x54", "remain unproven"),
        "tags": {"cvbuftexture", "primitive-count", "rendering", "vertex-buffer"},
        "decompile_tokens": ("+ 0x1c", "+ 0x54", "return iVar2 / 3"),
    },
}

EXPECTED_XREFS = {
    ("0x005003f0", "0x005012e5", "CVBufTexture__GetOrCreate", "UNCONDITIONAL_CALL"),
    ("0x00500460", "0x00501472", "CVBufTexture__ClearOut", "UNCONDITIONAL_CALL"),
    ("0x00500540", "0x004ae0f2", "CMesh__InitPartVBufTextureFormats", "UNCONDITIONAL_CALL"),
    ("0x00500590", "0x004ae102", "CMesh__InitPartVBufTextureFormats", "UNCONDITIONAL_CALL"),
    ("0x005005d0", "0x0055a4ef", "CDXTrees__BuildTreeGeometry", "UNCONDITIONAL_CALL"),
    ("0x005005e0", "0x00500a2f", "CVBufTexture__AddVertices", "UNCONDITIONAL_CALL"),
    ("0x005007f0", "0x00500add", "CVBufTexture__AddIndices", "UNCONDITIONAL_CALL"),
    ("0x005009c0", "0x005553e1", "CDXSnow__Init", "UNCONDITIONAL_CALL"),
    ("0x005009f0", "0x005553e9", "CDXSnow__Init", "UNCONDITIONAL_CALL"),
    ("0x00500a10", "0x00549871", "CMeshRenderer__RenderMeshCore", "UNCONDITIONAL_CALL"),
    ("0x00500ac0", "0x005498f1", "CMeshRenderer__RenderMeshCore", "UNCONDITIONAL_CALL"),
    ("0x00500b40", "0x005501bb", "DXParticleTexture__GetIndexBuffer", "UNCONDITIONAL_CALL"),
    ("0x00500bb0", "0x0055b49f", "CWaterRenderSystem__BuildGridVBuf", "UNCONDITIONAL_CALL"),
    ("0x00500c50", "0x00500ebf", "CVBufTexture__Render", "UNCONDITIONAL_CALL"),
    ("0x00500cb0", "0x005011f7", "CVBufTexture__RenderNonIndexed", "UNCONDITIONAL_CALL"),
}

EXPECTED_RETS = {
    ("0x00500454", "0x4", "CVBufTexture__CVBufTexture"),
    ("0x00500537", "", "CVBufTexture__dtor"),
    ("0x00500580", "0x14", "CVBufTexture__SetVBFormat"),
    ("0x005005b4", "0x10", "CVBufTexture__SetIBFormat"),
    ("0x005005d4", "", "CVBufTexture__SetPersist"),
    ("0x005007e7", "0x4", "CVBufTexture__ResizeVertexBuffer"),
    ("0x005009b6", "0x4", "CVBufTexture__ResizeIndexBuffer"),
    ("0x005009e2", "", "CVBufTexture__UnlockVB"),
    ("0x00500a0e", "", "CVBufTexture__UnlockIB"),
    ("0x00500ab0", "0x8", "CVBufTexture__AddVertices"),
    ("0x00500b3b", "0x8", "CVBufTexture__AddIndices"),
    ("0x00500b9e", "0x4", "CVBufTexture__GetIndexPtr"),
    ("0x00500c3e", "0x8", "CVBufTexture__GetVertexPtr"),
    ("0x00500ca0", "", "CVBufTexture__GetIndexPrimitiveCount"),
    ("0x00500cc1", "", "CVBufTexture__GetVertexPrimitiveCount"),
}

CALLSITE_TOKENS = (
    ("0x004ae0f2", ("PUSH 0x1", "PUSH 0x4", "PUSH 0x24", "PUSH 0x8", "PUSH 0x152", "CALL 0x00500540")),
    ("0x004ae102", ("PUSH 0x1", "PUSH 0x2", "PUSH 0x8", "PUSH 0x65", "CALL 0x00500590")),
    ("0x00500b58", ("PUSH EAX", "MOV ECX, ESI", "CALL 0x005007f0")),
    ("0x00500bcd", ("PUSH EAX", "MOV ECX, ESI", "CALL 0x005005e0")),
)

PUBLIC_NOTE_TOKENS = (
    "Wave530",
    "CVBufTexture__GetVertexPtr",
    "109 target xref rows",
    "1815 instruction rows",
    "runtime rendering behavior",
    "rebuild parity",
)

DOC_TOKENS = {
    GHIDRA_REF: ("Wave530", "CVBufTexture__GetVertexPtr", "1815 instruction rows"),
    STATIC_CAMPAIGN: ("Wave 530: CVBufTexture Buffer Management", "updated=15", "strict comment-plus-clean-signature proxy"),
    VBUFTEXTURE_DOC: ("Wave530", "CVBufTexture__GetVertexPtr", "buffer-management"),
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
        for key in ("address", "target_addr", "from_addr", "instruction_addr", "function_entry", "target_raw"):
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
        require("ApplyCVBufTextureBufferWave530.java> REPORT: Save succeeded" in text, f"{path.name}: missing script save report")
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
        base / "apply_cvbuftexture_buffer_wave530_dry.log",
        "SUMMARY updated=0 skipped=15 missing=0 bad=0",
    )
    check_log(
        base / "apply_cvbuftexture_buffer_wave530_apply.log",
        "SUMMARY updated=15 skipped=0 missing=0 bad=0",
        True,
    )
    check_log(
        base / "apply_cvbuftexture_buffer_wave530_verify_dry.log",
        "SUMMARY updated=0 skipped=15 missing=0 bad=0",
    )

    metadata = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")
    xrefs = read_tsv(base / "post_xrefs.tsv")
    instructions = read_tsv(base / "post_instructions.tsv")
    callsites = read_tsv(base / "pre_callsite_instructions.tsv")
    require(len(metadata) == len(TARGETS), f"metadata rows {len(metadata)} != {len(TARGETS)}")
    require(len(tags) == len(TARGETS), f"tag rows {len(tags)} != {len(TARGETS)}")
    require(len(xrefs) == 109, f"xref rows {len(xrefs)} != 109")
    require(len(instructions) == 1815, f"instruction rows {len(instructions)} != 1815")

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
        header = "\n".join(text.splitlines()[:14])
        require("undefined " not in header, f"{address} stale undefined signature in decompile header")
        require("param_1" not in header and "param_2" not in header, f"{address} stale param token in decompile header")

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

    for target, tokens in CALLSITE_TOKENS:
        text = "\n".join(
            f"{row['mnemonic']} {row['operands']}"
            for row in callsites
            if row.get("target_raw") == normalize_addr(target)
        )
        for token in tokens:
            require(token_present(text, token), f"callsite {target} missing {token!r}")

    target_index = read_tsv(base / "post_decomp" / "index.tsv")
    context_index = read_tsv(base / "post_context_decomp" / "index.tsv")
    require(len(target_index) == len(TARGETS), f"target decompile rows {len(target_index)} != {len(TARGETS)}")
    require(all(row["status"] == "OK" for row in target_index), "expected all target decompile rows OK")
    require(sum(1 for row in context_index if row["status"] == "OK") == 22, "expected 22 OK context decompile rows")
    require(sum(1 for row in context_index if row["status"] == "MISSING") == 6, "expected 6 missing mid-function context rows")

    check_docs()

    print("PASS Wave530 CVBufTexture buffer-management static RE evidence verified")
    if not args.check:
        print(f"base={base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
