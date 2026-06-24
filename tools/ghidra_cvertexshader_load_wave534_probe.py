#!/usr/bin/env python3
"""Validate Wave534 CVertexShader load/compile static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave534-cvertexshader-load-00501730"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cvertexshader_load_wave534_2026-05-18.md"
GHIDRA_REF = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
STATIC_CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
VERTEXSHADER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"

COMMON_TAGS = {
    "comment-hardened",
    "cvertexshader-load-wave534",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

TARGETS = {
    "0x00501730": {
        "name": "CVertexShader__ClearOut",
        "signature": "void __cdecl CVertexShader__ClearOut(void)",
        "comment_tokens": ("0x00854e68", "CLTShell shutdown", "CVBufTexture__ClearOut", "remain unproven"),
        "tags": {"cvertexshader", "global-list", "resource-lifetime", "shutdown"},
        "decompile_tokens": ("DAT_00854e68", "DebugTrace", "s_No_shader_leaks"),
    },
    "0x005019d0": {
        "name": "CVertexShader__QueryDeviceCapsAndSetGlobalSupportFlag",
        "signature": "void __cdecl CVertexShader__QueryDeviceCapsAndSetGlobalSupportFlag(void)",
        "comment_tokens": ("0x00854e6c", "0xfffe0101", "CDXMeshVB__BuildSkeletalVB", "remain unproven"),
        "tags": {"cvertexshader", "device-caps", "direct3d", "support-flag"},
        "decompile_tokens": ("DAT_00888c8c", "DAT_00854e6c", "0xfffe0101"),
    },
    "0x005022a0": {
        "name": "CVertexShader__LoadFromFile",
        "signature": "int __thiscall CVertexShader__LoadFromFile(void * this, char * shader_name, void * source_or_blob, int shader_type, int source_or_blob_size)",
        "comment_tokens": ("+0x0c", "source_or_blob_size is -1", "+0x50/+0x54", "0x80004005"),
        "tags": {"cvertexshader", "shader-load", "shader-source", "shader-bytecode"},
        "decompile_tokens": ("CVertexShader__LoadFromFile", "shader_name", "source_or_blob", "source_or_blob_size"),
    },
    "0x00502420": {
        "name": "CVertexShader__CompileShader",
        "signature": "void __thiscall CVertexShader__CompileShader(void * this)",
        "comment_tokens": ("vs.1.1", "dcl_position", "oFog.x", "remain unproven"),
        "tags": {"cvertexshader", "direct3d", "shader-compile", "shader-source"},
        "decompile_tokens": ("CVertexShader__CompileShader", "s_vs_1_0", "s_oFog_x", "D3DXAssembleShader"),
    },
    "0x005027f0": {
        "name": "CVertexShader__LoadCompiledShaderBlobFromVSOFile",
        "signature": "int __stdcall CVertexShader__LoadCompiledShaderBlobFromVSOFile(char * shader_name, int shader_token, void * device_shader_out)",
        "comment_tokens": ("RET 0x0c", "Shaders/%s.vso", "0x00501a10", "three stack arguments"),
        "tags": {"cvertexshader", "compiled-shader", "direct3d", "vtable-slot-2-caller"},
        "decompile_tokens": ("shader_name", "shader_token", "device_shader_out", "CreateFileA", "HeapFree"),
    },
    "0x00502920": {
        "name": "CVertexShader__ApplyCustomRenderStateShaderConstants",
        "signature": "void __thiscall CVertexShader__ApplyCustomRenderStateShaderConstants(void * this)",
        "comment_tokens": ("+0x40/+0x38", "Direct3D device vtable +0x178", "render-state", "remain unproven"),
        "tags": {"cvertexshader", "direct3d", "render-state", "shader-constants"},
        "decompile_tokens": ("CVertexShader__ApplyCustomRenderStateShaderConstants", "(int)this + 0x40", "CVBufTexture__DispatchTextureTransformThunk"),
    },
    "0x00503ac0": {
        "name": "CVertexShader__BuildAndCreateRenderInfoShader",
        "signature": "void * __cdecl CVertexShader__BuildAndCreateRenderInfoShader(void)",
        "comment_tokens": ("CVertexShader__Create", "CDXEngine__ApplyPendingRenderState", "EAX", "remain unproven"),
        "tags": {"cvertexshader", "factory", "render-info", "render-state"},
        "decompile_tokens": ("void * __cdecl CVertexShader__BuildAndCreateRenderInfoShader", "CVertexShader__Create", "return pvVar2"),
    },
    "0x00503dd0": {
        "name": "CVertexShader__AppendDeclarationNamesToDebugString",
        "signature": "void __cdecl CVertexShader__AppendDeclarationNamesToDebugString(char * out_buffer, void * declaration_tokens)",
        "comment_tokens": ("0x00634074..0x00634554", "0x00503f2f", "Unknown", "remain unproven"),
        "tags": {"cvertexshader", "debug-format", "declaration-tokens", "render-state"},
        "decompile_tokens": ("out_buffer", "declaration_tokens", "s_Unknown___d", "PTR_s_f_create_eyespace_vertex"),
    },
    "0x00503f90": {
        "name": "CVertexShader__Clone",
        "signature": "void * __cdecl CVertexShader__Clone(void * chunk_reader, int shader_index)",
        "comment_tokens": ("0x5c-byte", "shader%03d.i", "0x00662f35", "remain unproven"),
        "tags": {"cvertexshader", "chunk-reader", "clone", "shader-compile"},
        "decompile_tokens": ("chunk_reader", "shader_index", "CChunkReader__Read", "CVertexShader__CompileShader(outBuffer)", "return outBuffer"),
    },
}

EXPECTED_XREFS = {
    ("0x00501730", "0x004f01b5", "CLTShell__ShutdownRuntimeAndReleaseResources", "UNCONDITIONAL_CALL"),
    ("0x005019d0", "0x0054c9cd", "CDXMeshVB__BuildSkeletalVB", "UNCONDITIONAL_CALL"),
    ("0x005022a0", "0x00502194", "CVertexShader__Create", "UNCONDITIONAL_CALL"),
    ("0x00502420", "0x005042b1", "CVertexShader__Clone", "UNCONDITIONAL_CALL"),
    ("0x005027f0", "0x00501b23", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x00502920", "0x00501ced", "CVertexShader__ApplyRenderStateShaderConstants", "UNCONDITIONAL_CALL"),
    ("0x00503ac0", "0x00550f2d", "CDXEngine__ApplyPendingRenderState", "UNCONDITIONAL_CALL"),
    ("0x00503dd0", "0x00503f2f", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x00503f90", "0x00504355", "CVertexShader__DeserializeAll", "UNCONDITIONAL_CALL"),
}

EXPECTED_RETS = {
    ("0x005017f2", "", "CVertexShader__ClearOut"),
    ("0x00501a08", "", "CVertexShader__QueryDeviceCapsAndSetGlobalSupportFlag"),
    ("0x005022be", "0x10", "CVertexShader__LoadFromFile"),
    ("0x00502417", "0x10", "CVertexShader__LoadFromFile"),
    ("0x005027e7", "", "CVertexShader__CompileShader"),
    ("0x00502863", "0xc", "CVertexShader__LoadCompiledShaderBlobFromVSOFile"),
    ("0x0050291b", "0xc", "CVertexShader__LoadCompiledShaderBlobFromVSOFile"),
    ("0x00503abf", "", "CVertexShader__ApplyCustomRenderStateShaderConstants"),
    ("0x00503da2", "", "CVertexShader__BuildAndCreateRenderInfoShader"),
    ("0x00503ec9", "", "CVertexShader__AppendDeclarationNamesToDebugString"),
    ("0x005042ed", "", "CVertexShader__Clone"),
}

VTABLE_EXPECTED = {
    (0, "0x00501890", "CVertexShader__scalar_deleting_dtor", "OK"),
    (1, "0x005019c0", "VFuncSlot_09_005019c0", "OK"),
    (2, "0x00501a10", "<no_function>", "NO_FUNCTION_AT_POINTER"),
    (3, "0x00501b60", "CVertexShader__VFunc_03_00501b60", "OK"),
}

CALLSITE_TOKENS = (
    ("0x004f01b5", ("CALL 0x00501730", "CALL 0x00501450")),
    ("0x0054c9cd", ("CALL 0x005019d0", "CMP EDI, EBX")),
    ("0x00502194", ("MOV ECX, EBP", "CALL 0x005022a0", "TEST EAX, EAX")),
    ("0x00501b23", ("LEA ECX, [ESI + 0x28]", "PUSH ECX", "PUSH EAX", "PUSH EBX", "MOV ECX, ESI", "CALL 0x005027f0")),
    ("0x00501ced", ("CALL 0x00502920", "ADD ESP, 0x2b0")),
    ("0x00550f2d", ("CALL 0x00503ac0", "MOV dword ptr [EBP + 0xe54], EAX")),
    ("0x00503f2f", ("PUSH EAX", "PUSH ECX", "CALL 0x00503dd0", "ADD ESP, 0x8")),
    ("0x005042b1", ("MOV ECX, ESI", "CALL 0x00502420", "CALL dword ptr [EDX + 0x8]")),
    ("0x00504355", ("PUSH ESI", "PUSH EDI", "CALL 0x00503f90", "ADD ESP, 0x8")),
)

PUBLIC_NOTE_TOKENS = (
    "Wave534",
    "CVertexShader__LoadFromFile",
    "9 target xref rows",
    "8289 instruction rows",
    "vtable slot 2",
    "runtime shader behavior",
    "rebuild parity",
)

DOC_TOKENS = {
    GHIDRA_REF: ("Wave534", "CVertexShader__LoadCompiledShaderBlobFromVSOFile", "2544/6083 = 41.82%"),
    STATIC_CAMPAIGN: ("Wave 534: CVertexShader Load/Compile", "updated=9", "strict comment-plus-clean-signature proxy"),
    VERTEXSHADER_DOC: ("Wave534", "CVertexShader__Clone", "0x00501a10"),
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
    check_log(BASE / "apply_cvertexshader_load_wave534_dry.log", "SUMMARY updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0", expect_save=False)
    check_log(BASE / "apply_cvertexshader_load_wave534_apply.log", "SUMMARY updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0")
    check_log(BASE / "apply_cvertexshader_load_wave534_verify_dry.log", "SUMMARY updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0", expect_save=False)

    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    xrefs = read_tsv(BASE / "post_xrefs.tsv")
    instructions = read_tsv(BASE / "post_instructions_full.tsv")
    vtable = read_tsv(BASE / "post_vtable.tsv")
    callsites = read_tsv(BASE / "pre_callsite_instructions.tsv")

    require(len(metadata) == 9, f"expected 9 metadata rows, got {len(metadata)}")
    require(len(tags) == 9, f"expected 9 tag rows, got {len(tags)}")
    require(len(xrefs) == 9, f"expected 9 xref rows, got {len(xrefs)}")
    require(len(instructions) == 8289, f"expected 8289 instruction rows, got {len(instructions)}")
    require(len(vtable) == 4, f"expected 4 vtable rows, got {len(vtable)}")
    require(len(callsites) == 369, f"expected 369 callsite instruction rows, got {len(callsites)}")

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

    vtable_set = {
        (int(row["slot_index"]), normalize_addr(row["pointer_addr"]), row["function_name"], row["status"])
        for row in vtable
    }
    for expected in VTABLE_EXPECTED:
        slot, ptr, function_name, status = expected
        require((slot, normalize_addr(ptr), function_name, status) in vtable_set, f"missing vtable row {expected}")

    check_callsite_tokens(callsites)

    post_index = read_tsv(BASE / "post_decomp" / "index.tsv")
    require(len(post_index) == 9, f"expected 9 post decompile index rows, got {len(post_index)}")
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
    print("PASS Wave534 CVertexShader load/compile static RE evidence verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
