#!/usr/bin/env python3
"""Validate Wave533 CVertexShader core static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave533-cvertexshader-core-00501800"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cvertexshader_core_wave533_2026-05-18.md"
GHIDRA_REF = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
STATIC_CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
VERTEXSHADER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"

COMMON_TAGS = {
    "comment-hardened",
    "cvertexshader-core-wave533",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

TARGETS = {
    "0x00501800": {
        "name": "CVertexShader__CVertexShader",
        "signature": "void * __thiscall CVertexShader__CVertexShader(void * this)",
        "comment_tokens": ("vtable 0x005dfbc4", "0x00854e68", "+0x2c to 9", "remain unproven"),
        "tags": {"constructor", "cvertexshader", "global-list", "shader-lifetime"},
        "decompile_tokens": ("CShaderBase__Init((int)this)", "DAT_00854e68", "return this"),
    },
    "0x00501890": {
        "name": "CVertexShader__scalar_deleting_dtor",
        "signature": "void * __thiscall CVertexShader__scalar_deleting_dtor(void * this, byte delete_flags)",
        "comment_tokens": ("vtable slot 0", "RET 0x4", "delete_flags bit 0", "remain unproven"),
        "tags": {"cvertexshader", "destructor", "name-corrected", "scalar-deleting-destructor", "vtable-slot"},
        "decompile_tokens": ("CVertexShader__dtor(this)", "delete_flags & 1", "CDXMemoryManager__Free"),
    },
    "0x005018b0": {
        "name": "CVertexShader__dtor",
        "signature": "void __thiscall CVertexShader__dtor(void * this)",
        "comment_tokens": ("0x005dfbc4", "0x00854e68", "+0x28", "+0x50", "remain unproven"),
        "tags": {"cvertexshader", "destructor", "name-corrected", "resource-lifetime", "shader-lifetime"},
        "decompile_tokens": ("DAT_00854e68", "CDXMemoryManager__Free", "DeviceObject__ctor_like_00512d50"),
    },
    "0x00501b60": {
        "name": "CVertexShader__VFunc_03_00501b60",
        "signature": "int __thiscall CVertexShader__VFunc_03_00501b60(void * this)",
        "comment_tokens": ("vtable slot 3", "+0x28", "0x00501a10", "remain unproven"),
        "tags": {"cvertexshader", "device-shader", "release", "vtable-slot"},
        "decompile_tokens": ("this + 0x28", "return 0"),
    },
    "0x00501ba0": {
        "name": "CVertexShader__GetVertexDeclarationToken",
        "signature": "int __thiscall CVertexShader__GetVertexDeclarationToken(void * this)",
        "comment_tokens": ("+0x2c", "0x152", "0x15a", "0x142", "remain unproven"),
        "tags": {"cvertexshader", "direct3d", "render-state", "vertex-declaration"},
        "decompile_tokens": ("this + 0x2c", "return 0x152", "return 0x15a", "return 0x142"),
    },
    "0x00501cd0": {
        "name": "CVertexShader__ApplyRenderStateShaderConstants",
        "signature": "void __thiscall CVertexShader__ApplyRenderStateShaderConstants(void * this)",
        "comment_tokens": ("+0x34", "Direct3D vertex shader constants", "ShadowShader", "remain unproven"),
        "tags": {"cvertexshader", "direct3d", "render-state", "shader-constants"},
        "decompile_tokens": (
            "CVertexShader__ApplyCustomRenderStateShaderConstants((int)this)",
            "CDXEngine__GetProjectionWithDepthBias",
            "CVBufTexture__DispatchTextureTransformThunk",
            "s_ShadowShader",
        ),
    },
    "0x00502060": {
        "name": "CVertexShader__Create",
        "signature": "void * __cdecl CVertexShader__Create(char * shader_name, int shader_id, int shader_type, void * compiled_blob, int compiled_blob_size, int load_flags)",
        "comment_tokens": ("0x00854e68", "0x5c-byte", "0x0055512a", "0x0055b3e3", "remain unproven"),
        "tags": {"cvertexshader", "factory", "resource-cache", "shader-lifetime"},
        "decompile_tokens": ("DAT_0063c108", "stricmp", "OID__AllocObject(0x5c", "CVertexShader__CVertexShader", "local_10[0xc] = local_10[0xc] + 1"),
    },
    "0x00502290": {
        "name": "CVertexShader__DecrementLiveReferenceCount",
        "signature": "void __thiscall CVertexShader__DecrementLiveReferenceCount(void * this)",
        "comment_tokens": ("+0x30", "pending render-state", "atmospherics", "remain unproven"),
        "tags": {"cvertexshader", "refcount", "resource-lifetime", "shader-lifetime"},
        "decompile_tokens": ("this + 0x30", "- 1"),
    },
}

EXPECTED_XREFS = {
    ("0x00501800", "0x00503fda", "CVertexShader__Clone", "UNCONDITIONAL_CALL"),
    ("0x00501800", "0x0050215f", "CVertexShader__Create", "UNCONDITIONAL_CALL"),
    ("0x00501890", "0x005dfbc4", "<no_function>", "DATA"),
    ("0x005018b0", "0x00501893", "CVertexShader__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("0x00501b60", "0x005dfbd0", "<no_function>", "DATA"),
    ("0x00501ba0", "0x00513e55", "CEngine__SetShaderObject", "UNCONDITIONAL_CALL"),
    ("0x00501cd0", "0x005465f8", "CDXLandscape__RenderShadowMap", "UNCONDITIONAL_CALL"),
    ("0x00501cd0", "0x0054d5ee", "CMeshRenderer__RenderMeshWithLayerPasses", "UNCONDITIONAL_CALL"),
    ("0x00501cd0", "0x0054ffcf", "DXParticleTexture__RenderAll", "UNCONDITIONAL_CALL"),
    ("0x00501cd0", "0x00550ff5", "CDXEngine__ApplyPendingRenderState", "UNCONDITIONAL_CALL"),
    ("0x00501cd0", "0x0055b682", "CWaterRenderSystem__RenderShadowPass", "UNCONDITIONAL_CALL"),
    ("0x00501cd0", "0x0055b63f", "CWaterRenderSystem__BuildGridVBuf", "UNCONDITIONAL_CALL"),
    ("0x00501cd0", "0x0055bedd", "CWaterRenderSystem__RenderMainPass", "UNCONDITIONAL_CALL"),
    ("0x00502060", "0x00544c96", "CDXLandscape__Init", "UNCONDITIONAL_CALL"),
    ("0x00502060", "0x00503d92", "CVertexShader__BuildAndCreateRenderInfoShader", "UNCONDITIONAL_CALL"),
    ("0x00502060", "0x00503db2", "CVertexShader__BuildAndCreateRenderInfoShader", "UNCONDITIONAL_CALL"),
    ("0x00502060", "0x0054fe9f", "DXParticleTexture__RestoreAll", "UNCONDITIONAL_CALL"),
    ("0x00502060", "0x0055512a", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x00502060", "0x0055b3e3", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x00502290", "0x00550dcf", "CDXEngine__ApplyPendingRenderState", "UNCONDITIONAL_CALL"),
    ("0x00502290", "0x00544a9f", "CDXLandscape__Destructor", "UNCONDITIONAL_CALL"),
    ("0x00502290", "0x0054d4ac", "CDXMeshVB__VFunc_04_0054d3f0", "UNCONDITIONAL_CALL"),
    ("0x00502290", "0x00555452", "CAtmosphericsProfile__ReleaseResources", "UNCONDITIONAL_CALL"),
}

EXPECTED_RETS = {
    ("0x0050188b", "", "CVertexShader__CVertexShader"),
    ("0x005018ad", "0x4", "CVertexShader__scalar_deleting_dtor"),
    ("0x005019b9", "", "CVertexShader__dtor"),
    ("0x00501b7a", "", "CVertexShader__VFunc_03_00501b60"),
    ("0x00501bb4", "", "CVertexShader__GetVertexDeclarationToken"),
    ("0x00501bc6", "", "CVertexShader__GetVertexDeclarationToken"),
    ("0x00502059", "", "CVertexShader__ApplyRenderStateShaderConstants"),
    ("0x00502099", "", "CVertexShader__Create"),
    ("0x005021c2", "", "CVertexShader__Create"),
    ("0x00502266", "", "CVertexShader__Create"),
    ("0x00502284", "", "CVertexShader__Create"),
    ("0x00502293", "", "CVertexShader__DecrementLiveReferenceCount"),
}

VTABLE_EXPECTED = {
    (0, "0x00501890", "CVertexShader__scalar_deleting_dtor", "OK"),
    (1, "0x005019c0", "VFuncSlot_09_005019c0", "OK"),
    (2, "0x00501a10", "<no_function>", "NO_FUNCTION_AT_POINTER"),
    (3, "0x00501b60", "CVertexShader__VFunc_03_00501b60", "OK"),
}

CALLSITE_TOKENS = (
    ("0x0050215f", ("MOV ECX, EAX", "CALL 0x00501800")),
    ("0x00501893", ("CALL 0x005018b0", "TEST byte ptr [ESP + 0x8], 0x1", "RET 0x4")),
    ("0x00513e55", ("MOV ECX, EDI", "CALL 0x00501ba0", "CALL dword ptr [EBX + 0x164]")),
    ("0x005465f8", ("MOV ECX, dword ptr [ESI + 0x18]", "CALL 0x00501cd0")),
    ("0x00550dcf", ("MOV ECX, dword ptr [EBP + 0xe54]", "CALL 0x00502290")),
)

PUBLIC_NOTE_TOKENS = (
    "Wave533",
    "CVertexShader__scalar_deleting_dtor",
    "23 target xref rows",
    "4808 instruction rows",
    "runtime shader behavior",
    "rebuild parity",
)

DOC_TOKENS = {
    GHIDRA_REF: ("Wave533", "CVertexShader__Create", "4808 instruction rows"),
    STATIC_CAMPAIGN: ("Wave 533: CVertexShader Core", "updated=8", "strict comment-plus-clean-signature proxy"),
    VERTEXSHADER_DOC: ("Wave533", "CVertexShader__dtor", "0x00501a10"),
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
        for key in ("address", "target_addr", "from_addr", "instruction_addr", "function_entry", "target_raw", "pointer_addr"):
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


def check_log(path: Path, expected_summary: str, expect_save: bool = True) -> None:
    require(path.exists(), f"missing log: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    require(expected_summary in text, f"{path.name}: missing summary {expected_summary}")
    if expect_save:
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
    check_log(BASE / "apply_cvertexshader_core_wave533_dry.log", "SUMMARY updated=0 skipped=8 renamed=0 would_rename=2 missing=0 bad=0", expect_save=False)
    check_log(BASE / "apply_cvertexshader_core_wave533_apply.log", "SUMMARY updated=8 skipped=0 renamed=2 would_rename=0 missing=0 bad=0")
    check_log(BASE / "apply_cvertexshader_core_wave533_verify_dry.log", "SUMMARY updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0", expect_save=False)

    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    xrefs = read_tsv(BASE / "post_xrefs.tsv")
    instructions = read_tsv(BASE / "post_instructions_full.tsv")
    vtable = read_tsv(BASE / "post_vtable.tsv")
    callsites = read_tsv(BASE / "pre_callsite_instructions.tsv")

    require(len(metadata) == 8, f"expected 8 metadata rows, got {len(metadata)}")
    require(len(tags) == 8, f"expected 8 tag rows, got {len(tags)}")
    require(len(xrefs) == 23, f"expected 23 xref rows, got {len(xrefs)}")
    require(len(instructions) == 4808, f"expected 4808 instruction rows, got {len(instructions)}")
    require(len(vtable) == 8, f"expected 8 vtable rows, got {len(vtable)}")
    require(len(callsites) == 483, f"expected 483 callsite instruction rows, got {len(callsites)}")

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
    for target, source, function_name, ref_type in EXPECTED_XREFS:
        require((normalize_addr(target), normalize_addr(source), function_name, ref_type) in xref_set, f"missing xref {(target, source, function_name, ref_type)}")

    ret_set = {
        (normalize_addr(row["instruction_addr"]), (row.get("operands") or "").lower(), row["function_name"])
        for row in instructions
        if row.get("mnemonic") == "RET"
    }
    for ret_addr, operand, function_name in EXPECTED_RETS:
        require((normalize_addr(ret_addr), operand, function_name) in ret_set, f"missing RET {ret_addr} {operand} {function_name}")

    vtable_set = {
        (int(row["slot_index"]), normalize_addr(row["pointer_addr"]), row["function_name"], row["status"])
        for row in vtable
    }
    for expected in VTABLE_EXPECTED:
        slot, ptr, function_name, status = expected
        require((slot, normalize_addr(ptr), function_name, status) in vtable_set, f"missing vtable row {expected}")

    check_callsite_tokens(callsites)

    post_index = read_tsv(BASE / "post_decomp" / "index.tsv")
    require(len(post_index) == 8, f"expected 8 post decompile index rows, got {len(post_index)}")
    require(all(row["status"] == "OK" for row in post_index), "post decompile index has non-OK rows")

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
    print("PASS Wave533 CVertexShader core static RE evidence verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
