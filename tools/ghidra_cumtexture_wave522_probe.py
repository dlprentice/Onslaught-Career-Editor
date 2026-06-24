#!/usr/bin/env python3
"""Validate Wave522 CUMTexture static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave522-cumtexture-004f79d0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cumtexture_wave522_2026-05-18.md"

COMMON_TAGS = {
    "comment-hardened",
    "cumtexture",
    "cumtexture-wave522",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "texture-resource",
}

OVERCLAIM_TOKENS = (
    "runtime gpu behavior proven",
    "runtime texture lifetime behavior proven",
    "source identity proven",
    "exact class layout proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)


def target(
    name: str,
    signature: str,
    comment_tokens: tuple[str, ...],
    tags: set[str],
    decompile_tokens: tuple[str, ...],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "comment_tokens": comment_tokens,
        "tags": COMMON_TAGS | tags,
        "decompile_tokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004f79d0": target(
        "CUMTexture__ctor_base",
        "void * __fastcall CUMTexture__ctor_base(void * this)",
        ("vtable 0x005df908", "this+0x08", "shader/device-object base initializer", "remain unproven"),
        {"constructor", "lifecycle", "vtable"},
        ("PTR_CUMTexture__scalar_deleting_dtor_005df908", "CShaderBase__Init", "return this"),
    ),
    "0x004f7a20": target(
        "CUMTexture__scalar_deleting_dtor",
        "void * __thiscall CUMTexture__scalar_deleting_dtor(void * this, byte delete_flags)",
        ("vtable 0x005df908 slot 0", "RET 0x4", "delete_flags&1", "remain unproven"),
        {"destructor", "lifecycle", "owner-corrected", "vtable"},
        ("CUMTexture__dtor_base(this)", "delete_flags", "CDXMemoryManager__Free"),
    ),
    "0x004f7a40": target(
        "CUMTexture__dtor_base",
        "void __fastcall CUMTexture__dtor_base(void * this)",
        ("vtable 0x005df908", "unlinks the object", "base cleanup label at 0x00512d50", "remain unproven"),
        {"cleanup", "destructor", "lifecycle"},
        ("PTR_CUMTexture__scalar_deleting_dtor_005df908", "CDXLandscape__UnlinkNodeFromPrimaryAndSecondaryLists", "DeviceObject__ctor_like_00512d50"),
    ),
    "0x004f7ab0": target(
        "CUMTexture__ConfigureByMode",
        "int __thiscall CUMTexture__ConfigureByMode(void * this, void * texture_size, int mode, int texture_count_or_depth)",
        ("RET 0x0c", "mode selector", "this+0x0c/+0x10/+0x1c", "remain unproven"),
        {"configuration", "mode-selector"},
        ("texture_size", "texture_count_or_depth", "mode != 5", "*(int *)this + 8"),
    ),
    "0x004f7b60": target(
        "CUMTexture__RecreateTextureResource",
        "int __fastcall CUMTexture__RecreateTextureResource(void * this)",
        ("vtable 0x005df908 slot 2", "CLandscapeTexture__Reset", "CEngine__CreateTextureUnchecked", "remain unproven"),
        {"resource-create", "vtable"},
        ("CEngine__ReleaseField32FD4", "CEngine__TextureFormatIndexToD3D", "CEngine__CreateTextureUnchecked", "(int)this + 8"),
    ),
    "0x004f7bd0": target(
        "CUMTexture__VFunc_03_ReleaseTextureResource",
        "int __fastcall CUMTexture__VFunc_03_ReleaseTextureResource(void * this)",
        ("vtable 0x005df908 slot 3", "vtable 0x005dc1f0 slot 3", "returns 0", "remain unproven"),
        {"owner-corrected", "resource-release", "vtable"},
        ("piVar1", "*(undefined4 *)((int)this + 8) = 0", "return 0"),
    ),
}

EXPECTED_XREFS = {
    ("0x004f79d0", "0x0048e433", "CLandscapeTexture__ConstructorMip", "UNCONDITIONAL_CALL"),
    ("0x004f79d0", "0x00552198", "CDXShadows__Init", "UNCONDITIONAL_CALL"),
    ("0x004f79d0", "0x0054150e", "CDXFrontEndVideo__InitVideo", "UNCONDITIONAL_CALL"),
    ("0x004f7a20", "0x005df908", "<no_function>", "DATA"),
    ("0x004f7a40", "0x005d3123", "Unwind@005d3120", "UNCONDITIONAL_CALL"),
    ("0x004f7a40", "0x0048e4b9", "CLandscapeTexture__Destructor", "UNCONDITIONAL_CALL"),
    ("0x004f7a40", "0x004f7a23", "CUMTexture__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("0x004f7ab0", "0x0048e5b7", "CLandscapeTexture__Init", "UNCONDITIONAL_CALL"),
    ("0x004f7ab0", "0x005521b8", "CDXShadows__Init", "UNCONDITIONAL_CALL"),
    ("0x004f7ab0", "0x00541603", "CDXFrontEndVideo__InitVideo", "UNCONDITIONAL_CALL"),
    ("0x004f7ab0", "0x0048e77c", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004f7b60", "0x0048e614", "CLandscapeTexture__Reset", "UNCONDITIONAL_CALL"),
    ("0x004f7b60", "0x005df910", "<no_function>", "DATA"),
    ("0x004f7bd0", "0x005dc1fc", "<no_function>", "DATA"),
    ("0x004f7bd0", "0x005df914", "<no_function>", "DATA"),
}

EXPECTED_INSTRUCTIONS = {
    ("0x004f7a18", "RET", "", "CUMTexture__ctor_base"),
    ("0x004f7a3d", "RET", "0x4", "CUMTexture__scalar_deleting_dtor"),
    ("0x004f7aa8", "RET", "", "CUMTexture__dtor_base"),
    ("0x004f7ade", "RET", "0xc", "CUMTexture__ConfigureByMode"),
    ("0x004f7af8", "RET", "0xc", "CUMTexture__ConfigureByMode"),
    ("0x004f7b1a", "RET", "0xc", "CUMTexture__ConfigureByMode"),
    ("0x004f7b38", "RET", "0xc", "CUMTexture__ConfigureByMode"),
    ("0x004f7b56", "RET", "0xc", "CUMTexture__ConfigureByMode"),
    ("0x004f7bc6", "RET", "", "CUMTexture__RecreateTextureResource"),
    ("0x004f7bea", "RET", "", "CUMTexture__VFunc_03_ReleaseTextureResource"),
}

EXPECTED_VTABLES = {
    ("0x005df908", "0", "0x005df908", "0x004f7a20", "CUMTexture__scalar_deleting_dtor"),
    ("0x005df908", "2", "0x005df910", "0x004f7b60", "CUMTexture__RecreateTextureResource"),
    ("0x005df908", "3", "0x005df914", "0x004f7bd0", "CUMTexture__VFunc_03_ReleaseTextureResource"),
    ("0x005dc1f0", "3", "0x005dc1fc", "0x004f7bd0", "CUMTexture__VFunc_03_ReleaseTextureResource"),
}

EXPECTED_CONTEXT_TOKENS = {
    "0x0048e430": ("CUMTexture__ctor_base(this)",),
    "0x0048e4d0": ("CUMTexture__ConfigureByMode(this,DAT_0062d864,1,1)",),
    "0x0048e610": ("CUMTexture__RecreateTextureResource(this)",),
    "0x00541430": ("CUMTexture__ctor_base", "CUMTexture__ConfigureByMode", "5 - (uint)(DAT_008a9a54 != 0),1"),
    "0x005520f0": ("CUMTexture__ctor_base", "CUMTexture__ConfigureByMode(this,(void *)*piVar4,0,1)"),
}

PUBLIC_NOTE_TOKENS = (
    "Wave522",
    "CUMTexture__ConfigureByMode",
    "CUMTexture__RecreateTextureResource",
    "15 target xref rows",
    "runtime GPU behavior",
    "rebuild parity",
)


def normalize_addr(address: str) -> str:
    address = (address or "").strip().lower()
    if not address or address.startswith("<"):
        return address
    body = address[2:] if address.startswith("0x") else address
    return f"0x{int(body, 16):08x}"


def compact_text(value: str) -> str:
    return " ".join((value or "").replace("\t", " ").replace("\r", " ").replace("\n", " ").split())


def compact_token(value: str) -> str:
    return "".join(compact_text(value).lower().split())


def token_present(text: str, token: str) -> bool:
    return compact_token(token) in compact_token(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in (
            "address",
            "target_addr",
            "from_addr",
            "instruction_addr",
            "function_entry",
            "vtable",
            "slot_addr",
            "pointer_addr",
            "function_entry",
            "containing_entry",
        ):
            if key in row and row[key]:
                row[key] = normalize_addr(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str]:
    wanted = normalize_addr(address)
    for row in rows:
        if row.get(key) == wanted:
            return row
    raise AssertionError(f"missing row for {address}")


def find_decomp_file(decomp_dir: Path, address: str, expected_name: str) -> Path:
    candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
    require(bool(candidates), f"missing decompile export for {address}")
    named = [path for path in candidates if expected_name in path.name]
    if named:
        return named[0]
    return candidates[0]


def validate_metadata(base: Path) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        require(row["status"] == "OK", f"{address} status mismatch: {row['status']}")
        require(row["name"] == expected["name"], f"{address} name mismatch: {row['name']}")
        require(row["signature"] == expected["signature"], f"{address} signature mismatch: {row['signature']}")
        comment = compact_text(row["comment"])
        for token in expected["comment_tokens"]:
            require(token_present(comment, str(token)), f"{address} comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            require(not token_present(comment, token), f"{address} comment contains overclaim token {token!r}")


def validate_tags(base: Path) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        tags = {tag.strip() for tag in row["tags"].replace(",", ";").split(";") if tag.strip()}
        missing = expected["tags"] - tags
        require(not missing, f"{address} missing tags: {sorted(missing)}")


def validate_decompile(base: Path) -> None:
    decomp_dir = base / "post_decomp"
    require(decomp_dir.exists(), f"missing decompile dir: {decomp_dir}")
    for address, expected in TARGETS.items():
        text = find_decomp_file(decomp_dir, address, str(expected["name"])).read_text(encoding="utf-8", errors="replace")
        for token in expected["decompile_tokens"]:
            require(token_present(text, str(token)), f"{address} decompile missing token {token!r}")


def validate_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    got = {
        (row["target_addr"], row["from_addr"], row["from_function"], row["ref_type"])
        for row in rows
    }
    missing = EXPECTED_XREFS - got
    require(not missing, f"missing expected xrefs: {sorted(missing)}")


def validate_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    for address, mnemonic, operand_token, function_name in EXPECTED_INSTRUCTIONS:
        matches = [row for row in rows if row.get("instruction_addr") == normalize_addr(address)]
        require(matches, f"missing instruction row post_instructions.tsv:{address}")
        row = matches[0]
        require(row["mnemonic"] == mnemonic, f"{address} mnemonic mismatch: {row['mnemonic']}")
        require(function_name == row["function_name"], f"{address} function mismatch: {row['function_name']}")
        if operand_token:
            require(token_present(row["operands"], operand_token), f"{address} operands missing {operand_token!r}")


def validate_vtables(base: Path) -> None:
    rows = read_tsv(base / "post_vtable_slots.tsv")
    got = {
        (row["vtable"], row["slot_index"], row["slot_addr"], row["pointer_addr"], row["function_name"])
        for row in rows
    }
    missing = EXPECTED_VTABLES - got
    require(not missing, f"missing expected vtable slots: {sorted(missing)}")


def validate_context_decompile(base: Path) -> None:
    decomp_dir = base / "post_context_decomp"
    require(decomp_dir.exists(), f"missing context decompile dir: {decomp_dir}")
    for address, tokens in EXPECTED_CONTEXT_TOKENS.items():
        candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
        require(bool(candidates), f"missing context decompile export for {address}")
        text = candidates[0].read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            require(token_present(text, token), f"{address} context decompile missing token {token!r}")


def validate_counts(base: Path) -> None:
    require(len(read_tsv(base / "post_metadata.tsv")) == 6, "post metadata row count mismatch")
    require(len(read_tsv(base / "post_tags.tsv")) == 6, "post tags row count mismatch")
    require(len(read_tsv(base / "post_xrefs.tsv")) == 15, "post xref row count mismatch")
    require(len(read_tsv(base / "post_context_metadata.tsv")) == 6, "post context metadata row count mismatch")
    require(len(read_tsv(base / "post_instructions.tsv")) == 366, "post instruction export row count mismatch")
    require(len(read_tsv(base / "post_vtable_slots.tsv")) == 16, "post vtable row count mismatch")
    decomp_index = read_tsv(base / "post_decomp" / "index.tsv")
    require(len(decomp_index) == 6, "post decompile index row count mismatch")
    for row in decomp_index:
        require(row["status"] == "OK", f"decompile failed for {row.get('address')}")
    context_index = read_tsv(base / "post_context_decomp" / "index.tsv")
    require(len(context_index) == 6, "post context decompile index row count mismatch")
    for row in context_index:
        require(row["status"] == "OK", f"context decompile failed for {row.get('address')}")


def validate_public_note() -> None:
    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    text = PUBLIC_NOTE.read_text(encoding="utf-8", errors="replace")
    for token in PUBLIC_NOTE_TOKENS:
        require(token in text, f"public note missing token {token!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    base = args.base
    validate_metadata(base)
    validate_tags(base)
    validate_decompile(base)
    validate_xrefs(base)
    validate_instructions(base)
    validate_vtables(base)
    validate_context_decompile(base)
    validate_counts(base)
    if args.check:
        validate_public_note()
    print(f"PASS wave522 CUMTexture evidence: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
