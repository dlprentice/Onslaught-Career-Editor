#!/usr/bin/env python3
"""Validate Wave532 VBufTexture resource-tail static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave532-vbuftexture-resource-tail-00501310"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_vbuftexture_resource_tail_wave532_2026-05-18.md"
GHIDRA_REF = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
STATIC_CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "vbuftexture-resource-wave532",
}

TARGETS = {
    "0x00501310": {
        "name": "CDXEngine__DecrementResourceRefCount",
        "signature": "void __fastcall CDXEngine__DecrementResourceRefCount(void * resource)",
        "comment_tokens": ("ECX-only", "+0x60", "CVBufTexture__GetOrCreate", "remain unproven"),
        "tags": {"cvbuftexture", "refcount", "resource-lifetime"},
        "decompile_tokens": ("resource + 0x60", "- 1"),
    },
    "0x00501320": {
        "name": "CScreenFx__FindTexture",
        "signature": "void __cdecl CScreenFx__FindTexture(char * texture_name, int texture_find_arg)",
        "comment_tokens": ("caller-cleaned RET C3", "CTexture__FindTexture", "CVBufTexture__GetOrCreate(texture,0)", "remain unproven"),
        "tags": {"cvbuftexture", "resource-lifetime", "screenfx", "texture-reference"},
        "decompile_tokens": ("CTexture__FindTexture", "CHud__DecrementCounter9C", "CVBufTexture__GetOrCreate(texture,0)"),
    },
    "0x00501360": {
        "name": "CWaypoint__CleanupEndLevelVBufTextures",
        "signature": "void __cdecl CWaypoint__CleanupEndLevelVBufTextures(void)",
        "comment_tokens": ("global no-argument RET C3", "0x00854e00", "+0x60", "end-of-level", "remain unproven"),
        "tags": {"cvbuftexture", "leak-report", "resource-lifetime", "waypoint"},
        "decompile_tokens": ("DAT_00854e00", "CVBufTexture__dtor", "CDXMemoryManager__Free", "DebugTrace"),
    },
    "0x00501450": {
        "name": "CVBufTexture__ClearOut",
        "signature": "void __cdecl CVBufTexture__ClearOut(void)",
        "comment_tokens": ("CLTShell shutdown", "CVertexShader__ClearOut", "shutdown resource leak", "remain unproven"),
        "tags": {"cvbuftexture", "leak-report", "resource-lifetime", "shutdown"},
        "decompile_tokens": ("DAT_00854e00", "CVBufTexture__dtor", "CDXMemoryManager__Free", "DebugTrace"),
    },
    "0x00501540": {
        "name": "CDXEngine__ResizeLargestIdleVertexBuffer",
        "signature": "void __cdecl CDXEngine__ResizeLargestIdleVertexBuffer(void)",
        "comment_tokens": ("0x00633d2c", "largest shrink opportunity", "CVBufTexture__ResizeVertexBuffer", "remain unproven"),
        "tags": {"buffer-trim", "cvbuftexture", "post-render", "resource-pool"},
        "decompile_tokens": ("DAT_00633d2c", "DAT_00854e00", "CVBufTexture__ResizeVertexBuffer"),
    },
    "0x005015c0": {
        "name": "CEngine__TrimVbIbPoolCapacitiesPow2",
        "signature": "void __cdecl CEngine__TrimVbIbPoolCapacitiesPow2(void)",
        "comment_tokens": ("0x400-based powers of two", "CVBufTexture__ResizeIndexBuffer", "CGame restart", "remain unproven"),
        "tags": {"buffer-trim", "cvbuftexture", "engine-shutdown", "resource-pool"},
        "decompile_tokens": ("DAT_00854e00", "CVBufTexture__ResizeVertexBuffer", "CVBufTexture__ResizeIndexBuffer"),
    },
}

EXPECTED_XREFS = {
    ("0x00501310", "0x004adfd6", "CMesh__ReleaseEmbeddedResources", "UNCONDITIONAL_CALL"),
    ("0x00501310", "0x0055015b", "DXParticleTexture__Release", "UNCONDITIONAL_CALL"),
    ("0x00501310", "0x0053e20c", "CDXEngine__RenderTexturedBeamQuad", "UNCONDITIONAL_CALL"),
    ("0x00501320", "0x00551cca", "CScreenFx__LoadZoomTextures", "UNCONDITIONAL_CALL"),
    ("0x00501320", "0x00551d04", "CScreenFx__LoadZoomTextures", "UNCONDITIONAL_CALL"),
    ("0x00501360", "0x00469292", "CFrontEnd__ReleaseParticleHudWaypointResources", "UNCONDITIONAL_CALL"),
    ("0x00501360", "0x0046ca18", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x00501450", "0x004f01ba", "CLTShell__ShutdownRuntimeAndReleaseResources", "UNCONDITIONAL_CALL"),
    ("0x00501540", "0x0053efea", "CDXEngine__PostRender", "UNCONDITIONAL_CALL"),
    ("0x005015c0", "0x0046e1d5", "CGame__RestartLoopRunLevel", "UNCONDITIONAL_CALL"),
    ("0x005015c0", "0x0053effb", "CDXEngine__PostRender", "UNCONDITIONAL_CALL"),
    ("0x005015c0", "0x004499c7", "CEngine__Shutdown", "UNCONDITIONAL_CALL"),
}

EXPECTED_RETS = {
    ("0x00501313", "", "CDXEngine__DecrementResourceRefCount"),
    ("0x00501351", "", "CScreenFx__FindTexture"),
    ("0x0050142e", "", "CWaypoint__CleanupEndLevelVBufTextures"),
    ("0x00501443", "", "CWaypoint__CleanupEndLevelVBufTextures"),
    ("0x0050151e", "", "CVBufTexture__ClearOut"),
    ("0x00501533", "", "CVBufTexture__ClearOut"),
    ("0x005015b9", "", "CDXEngine__ResizeLargestIdleVertexBuffer"),
    ("0x0050162b", "", "CEngine__TrimVbIbPoolCapacitiesPow2"),
}

CALLSITE_TOKENS = (
    ("0x00551cca", ("PUSH 0x1", "PUSH 0x652218", "CALL 0x00501320", "ADD ESP, 0x8")),
    ("0x00551d04", ("PUSH 0x1", "PUSH 0x652200", "CALL 0x00501320", "ADD ESP, 0x8")),
    ("0x00469292", ("CALL 0x004a5430", "CALL 0x00501360")),
    ("0x004f01ba", ("CALL 0x00501730", "CALL 0x00501450")),
    ("0x0053efea", ("CALL 0x00501540", "CALL 0x005015c0")),
    ("0x0053effb", ("CALL 0x00501540", "CALL 0x005015c0")),
    ("0x004499c7", ("CALL 0x004f27e0", "CALL 0x005015c0")),
)

PUBLIC_NOTE_TOKENS = (
    "Wave532",
    "CDXEngine__DecrementResourceRefCount",
    "25 target xref rows",
    "2646 instruction rows",
    "runtime cleanup behavior",
    "rebuild parity",
)

DOC_TOKENS = {
    GHIDRA_REF: ("Wave532", "CVBufTexture__ClearOut", "2646 instruction rows"),
    STATIC_CAMPAIGN: ("Wave 532: VBufTexture Resource Tail", "updated=6", "strict comment-plus-clean-signature proxy"),
    VBUFTEXTURE_DOC: ("Wave532", "CEngine__TrimVbIbPoolCapacitiesPow2", "resource-tail"),
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
    check_log(BASE / "apply_vbuftexture_resource_tail_wave532_dry.log", "SUMMARY updated=0 skipped=6 missing=0 bad=0")
    check_log(BASE / "apply_vbuftexture_resource_tail_wave532_apply.log", "SUMMARY updated=6 skipped=0 missing=0 bad=0")
    check_log(BASE / "apply_vbuftexture_resource_tail_wave532_verify_dry.log", "SUMMARY updated=0 skipped=6 missing=0 bad=0")

    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    xrefs = read_tsv(BASE / "post_xrefs.tsv")
    instructions = read_tsv(BASE / "post_instructions_full.tsv")
    callsites = read_tsv(BASE / "pre_callsite_instructions.tsv")

    require(len(metadata) == 6, f"expected 6 metadata rows, got {len(metadata)}")
    require(len(tags) == 6, f"expected 6 tag rows, got {len(tags)}")
    require(len(xrefs) == 25, f"expected 25 xref rows, got {len(xrefs)}")
    require(len(instructions) == 2646, f"expected 2646 instruction rows, got {len(instructions)}")
    require(len(callsites) == 525, f"expected 525 callsite instruction rows, got {len(callsites)}")

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
    require(len(post_index) == 6, f"expected 6 post decompile index rows, got {len(post_index)}")
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
    print("PASS Wave532 VBufTexture resource-tail static RE evidence verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
