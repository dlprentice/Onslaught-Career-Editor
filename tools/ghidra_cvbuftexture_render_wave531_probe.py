#!/usr/bin/env python3
"""Validate Wave531 CVBufTexture render-tail static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave531-cvbuftexture-render-00500d10"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cvbuftexture_render_wave531_2026-05-18.md"
GHIDRA_REF = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
STATIC_CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"

COMMON_TAGS = {
    "comment-hardened",
    "cvbuftexture-render-wave531",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

TARGETS = {
    "0x00500d10": {
        "name": "CVBufTexture__RenderBatchList",
        "signature": "void __cdecl CVBufTexture__RenderBatchList(void * batch_list)",
        "comment_tokens": ("caller-cleaned RET C3", "0x24-byte batch records", "priority values 0..5", "remain unproven"),
        "tags": {"batch-list", "cvbuftexture", "direct3d", "rendering"},
        "decompile_tokens": ("CVBufTexture__Render(this,1)", "+ 0x88", "batch_list + iVar3"),
    },
    "0x00500d60": {
        "name": "CVBufTexture__ReleaseAllUnlocked",
        "signature": "void __cdecl CVBufTexture__ReleaseAllUnlocked(void)",
        "comment_tokens": ("global no-argument RET C3", "0x00854e00", "byte +0x5c", "remain unproven"),
        "tags": {"cvbuftexture", "lock-unlock", "rendering", "resource-lifetime"},
        "decompile_tokens": ("DAT_00854e00", "DebugTrace", "+ 0x64"),
    },
    "0x00500e70": {
        "name": "CVBufTexture__Render",
        "signature": "void __thiscall CVBufTexture__Render(void * this, int reset_after_render)",
        "comment_tokens": ("RET 0x4", "reset_after_render", "draws indexed primitives", "remain unproven"),
        "tags": {"cvbuftexture", "direct3d", "indexed-render", "rendering"},
        "decompile_tokens": ("CVBufTexture__GetIndexPrimitiveCount(this)", "CEngine__DrawIndexedPrimitives", "CVBufTexture__SetupRenderStates"),
    },
    "0x00500f80": {
        "name": "CVBufTexture__Reset",
        "signature": "void __thiscall CVBufTexture__Reset(void * this)",
        "comment_tokens": ("ECX-only reset helper", "+0x64", "0x00854e04", "remain unproven"),
        "tags": {"cvbuftexture", "double-buffering", "rendering", "reset"},
        "decompile_tokens": ("+ 0x1c", "+ 0x34", "DAT_00854e04"),
    },
    "0x00500fa0": {
        "name": "CVBufTexture__RenderIndexed",
        "signature": "void __thiscall CVBufTexture__RenderIndexed(void * this, int reset_after_render, int vertex_count_override, int primitive_count_override)",
        "comment_tokens": ("RET 0x0c", "ValidateDevice", "primitive_count_override", "remain unproven"),
        "tags": {"cvbuftexture", "direct3d", "indexed-render", "rendering", "validate-device"},
        "decompile_tokens": ("DAT_00854dd9", "CEngine__DeviceCall118_WithZeroOut", "CConsole__Printf"),
    },
    "0x005010e0": {
        "name": "CVBufTexture__RenderIndexedNoValidate",
        "signature": "void __thiscall CVBufTexture__RenderIndexedNoValidate(void * this, int reset_after_render, int vertex_count_override, int primitive_count_override)",
        "comment_tokens": ("RET 0x0c", "skips the ValidateDevice branch", "particle/tree/water callsites", "remain unproven"),
        "tags": {"cvbuftexture", "direct3d", "indexed-render", "no-validate", "rendering"},
        "decompile_tokens": ("CEngine__DrawIndexedPrimitives", "CVBufTexture__GetIndexPrimitiveCount", "+ 0x4c"),
    },
    "0x005011c0": {
        "name": "CVBufTexture__RenderNonIndexed",
        "signature": "void __thiscall CVBufTexture__RenderNonIndexed(void * this, int reset_after_render, int primitive_count_override)",
        "comment_tokens": ("RET 0x8", "DrawPrimitive", "primitive_count_override", "remain unproven"),
        "tags": {"cvbuftexture", "direct3d", "non-indexed-render", "rendering"},
        "decompile_tokens": ("CVBufTexture__GetVertexPrimitiveCount", "+ 0x144", "DAT_009c741c"),
    },
    "0x00501280": {
        "name": "CVBufTexture__GetOrCreate",
        "signature": "void * __cdecl CVBufTexture__GetOrCreate(void * texture, int force_new)",
        "comment_tokens": ("caller-cleaned RET C3", "texture field +0x140", "OID__AllocObject", "remain unproven"),
        "tags": {"cvbuftexture", "factory", "resource-lifetime", "texture-reference"},
        "decompile_tokens": ("OID__AllocObject(0x68,0x1f", "CVBufTexture__CVBufTexture", "+ 0x140"),
    },
}

EXPECTED_XREFS = {
    ("0x00500d10", "0x0054990b", "CMeshRenderer__RenderMeshCore", "UNCONDITIONAL_CALL"),
    ("0x00500d60", "0x0053ef68", "CDXEngine__PostRender", "UNCONDITIONAL_CALL"),
    ("0x00500e70", "0x00500d3e", "CVBufTexture__RenderBatchList", "UNCONDITIONAL_CALL"),
    ("0x00500f80", "0x0055b48d", "CWaterRenderSystem__BuildGridVBuf", "UNCONDITIONAL_CALL"),
    ("0x00500fa0", "0x00543b5b", "CDXImposter__RenderAll", "UNCONDITIONAL_CALL"),
    ("0x005010e0", "0x005502b7", "DXParticleTexture__Render", "UNCONDITIONAL_CALL"),
    ("0x005011c0", "0x005555e8", "CAtmosphericsProfile__RenderOverlay", "UNCONDITIONAL_CALL"),
    ("0x00501280", "0x004ae0d8", "CMesh__InitPartVBufTextureFormats", "UNCONDITIONAL_CALL"),
}

EXPECTED_RETS = {
    ("0x00500d58", "", "CVBufTexture__RenderBatchList"),
    ("0x00500e63", "", "CVBufTexture__ReleaseAllUnlocked"),
    ("0x00500f6f", "0x4", "CVBufTexture__Render"),
    ("0x00500f9e", "", "CVBufTexture__Reset"),
    ("0x005010d1", "0xc", "CVBufTexture__RenderIndexed"),
    ("0x005011b4", "0xc", "CVBufTexture__RenderIndexedNoValidate"),
    ("0x0050127d", "0x8", "CVBufTexture__RenderNonIndexed"),
    ("0x005012f6", "", "CVBufTexture__GetOrCreate"),
    ("0x0050130a", "", "CVBufTexture__GetOrCreate"),
}

CALLSITE_TOKENS = (
    ("0x0054990b", ("PUSH ECX", "CALL 0x00500d10")),
    ("0x00500d3e", ("PUSH 0x1", "MOV ECX, EAX", "CALL 0x00500e70")),
    ("0x00543b5b", ("PUSH 0x0", "PUSH 0x0", "PUSH EBX", "CALL 0x00500fa0")),
    ("0x005502b7", ("PUSH 0x0", "PUSH 0x0", "PUSH 0x1", "CALL 0x005010e0")),
    ("0x005555e8", ("PUSH EAX", "PUSH 0x0", "CALL 0x005011c0")),
    ("0x004ae0d8", ("PUSH 0x0", "PUSH EAX", "CALL 0x00501280", "ADD ESP, 0x8")),
)

PUBLIC_NOTE_TOKENS = (
    "Wave531",
    "CVBufTexture__RenderIndexedNoValidate",
    "39 target xref rows",
    "3528 instruction rows",
    "runtime rendering behavior",
    "rebuild parity",
)

DOC_TOKENS = {
    GHIDRA_REF: ("Wave531", "CVBufTexture__RenderIndexedNoValidate", "3528 instruction rows"),
    STATIC_CAMPAIGN: ("Wave 531: CVBufTexture Render Tail", "updated=8", "strict comment-plus-clean-signature proxy"),
    VBUFTEXTURE_DOC: ("Wave531", "CVBufTexture__RenderIndexedNoValidate", "render-tail"),
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
        for key in ("address", "target_addr", "from_addr", "instruction_addr", "function_entry", "target_raw", "target_addr"):
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


def check_log(path: Path, expected_summary: str) -> None:
    require(path.exists(), f"missing log: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    require(expected_summary in text, f"{path.name}: missing summary {expected_summary}")
    require("REPORT: Save succeeded" in text, f"{path.name}: missing save success")
    for bad in ("LockException", "MISSING:", "BADNAME:", "BADADDR:", "FAIL:"):
        require(bad not in text, f"{path.name}: contains {bad}")


def check_callsite_tokens(rows: list[dict[str, str]]) -> None:
    for target, tokens in CALLSITE_TOKENS:
        actual = [
            f"{row.get('mnemonic', '')} {row.get('operands', '')}".strip()
            for row in rows
            if row.get("target_raw") == normalize_addr(target)
        ]
        joined = "\n".join(actual)
        for token in tokens:
            require(token_present(joined, token), f"callsite {target}: missing {token}")


def check_docs() -> None:
    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    public_text = PUBLIC_NOTE.read_text(encoding="utf-8")
    for token in PUBLIC_NOTE_TOKENS:
        require(token_present(public_text, token), f"public note missing token: {token}")
    for path, tokens in DOC_TOKENS.items():
        require(path.exists(), f"missing doc: {path}")
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            require(token_present(text, token), f"{path}: missing token {token}")


def run_check() -> None:
    check_log(BASE / "apply_cvbuftexture_render_wave531_dry.log", "SUMMARY updated=0 skipped=8 missing=0 bad=0")
    check_log(BASE / "apply_cvbuftexture_render_wave531_apply.log", "SUMMARY updated=8 skipped=0 missing=0 bad=0")
    check_log(BASE / "apply_cvbuftexture_render_wave531_verify_dry.log", "SUMMARY updated=0 skipped=8 missing=0 bad=0")

    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    xrefs = read_tsv(BASE / "post_xrefs.tsv")
    instructions = read_tsv(BASE / "post_instructions_full.tsv")
    callsites = read_tsv(BASE / "pre_callsite_instructions.tsv")

    require(len(metadata) == 8, f"expected 8 metadata rows, got {len(metadata)}")
    require(len(tags) == 8, f"expected 8 tag rows, got {len(tags)}")
    require(len(xrefs) == 39, f"expected 39 xref rows, got {len(xrefs)}")
    require(len(instructions) == 3528, f"expected 3528 instruction rows, got {len(instructions)}")
    require(len(callsites) == 230, f"expected 230 callsite instruction rows, got {len(callsites)}")

    tag_rows = {normalize_addr(row["address"]): row for row in tags}
    for address, spec in TARGETS.items():
        row = row_by(metadata, address)
        require(row["name"] == spec["name"], f"{address}: name mismatch")
        require(row["signature"] == spec["signature"], f"{address}: signature mismatch: {row['signature']}")
        for token in spec["comment_tokens"]:
            require(token_present(row["comment"], token), f"{address}: comment missing {token}")
        tag_set = set(tag_rows[normalize_addr(address)]["tags"].split(";"))
        require(COMMON_TAGS.issubset(tag_set), f"{address}: missing common tags")
        require(spec["tags"].issubset(tag_set), f"{address}: missing specific tags")

        decomp = decomp_file(BASE / "post_decomp", address, spec["name"]).read_text(encoding="utf-8", errors="replace")
        for token in spec["decompile_tokens"]:
            require(token_present(decomp, token), f"{address}: decompile missing {token}")

    xref_set = {
        (normalize_addr(row["target_addr"]), normalize_addr(row["from_addr"]), row["from_function"], row["ref_type"])
        for row in xrefs
    }
    for expected in EXPECTED_XREFS:
        target, source, function_name, ref_type = expected
        require((normalize_addr(target), normalize_addr(source), function_name, ref_type) in xref_set, f"missing xref {expected}")

    ret_set = {
        (normalize_addr(row["instruction_addr"]), (row.get("operands") or "").lower(), row["function_name"])
        for row in instructions
        if row.get("mnemonic") == "RET"
    }
    for ret_addr, operand, function_name in EXPECTED_RETS:
        require((normalize_addr(ret_addr), operand, function_name) in ret_set, f"missing RET {ret_addr} {operand} {function_name}")

    check_callsite_tokens(callsites)

    post_index = read_tsv(BASE / "post_decomp" / "index.tsv")
    require(len(post_index) == 8, f"expected 8 post decompile index rows, got {len(post_index)}")
    require(all(row["status"] == "OK" for row in post_index), "post decompile index has non-OK rows")
    context_index = read_tsv(BASE / "post_context_decomp" / "index.tsv")
    require(len(context_index) == 8, f"expected 8 context decompile index rows, got {len(context_index)}")
    require(all(row["status"] == "OK" for row in context_index), "context decompile index has non-OK rows")

    check_docs()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Run validation checks")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")
    try:
        run_check()
    except AssertionError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    print("PASS Wave531 CVBufTexture render-tail static RE evidence verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
