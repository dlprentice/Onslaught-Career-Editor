#!/usr/bin/env python3
"""Validate Wave513 texture/TGA static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = (
    ROOT
    / "subagents"
    / "ghidra-static-reaudit"
    / "wave513-texture-tga-004f27f0"
)
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_tga_wave513_2026-05-17.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "texture-tga-wave513",
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime rendering behavior proven",
    "runtime image loading proven",
    "source body identity proven",
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
    instruction_tokens: tuple[tuple[str, str], ...],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "comment_tokens": comment_tokens,
        "tags": COMMON_TAGS | tags,
        "decompile_tokens": decompile_tokens,
        "instruction_tokens": instruction_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004f27f0": target(
        "CTexture__FindTexture",
        "void * __cdecl CTexture__FindTexture(char * name, int texture_type, int load_arg, int required_mip_count, int allow_fallback, int load_flags)",
        ("global CTexture cache lookup/load helper", "DAT_0083d9b0", "0x158-byte CTexture", "DAT_0083d9b4", "forwarded loader argument semantics"),
        {"asset-loading", "cache", "fallback", "texture"},
        ("void * __cdecl", "texture_type", "required_mip_count", "allow_fallback", "CTexture__Release"),
        (("MOV", "[0x0083d9b0]"), ("CALL", "0x00568390"), ("CMP", "[ESI + 0xa8]")),
    ),
    "0x004f29c0": target(
        "CTexture__InitDefaultTextureResourcesAndStatus",
        "void __cdecl CTexture__InitDefaultTextureResourcesAndStatus(void)",
        ("default texture bootstrap/status helper", "meshtex/default.tga", "DAT_0083d9b4", "Loading texture resources"),
        {"console-status", "default-texture", "resource-bootstrap", "texture"},
        ("void __cdecl", "CTexture__FindTexture", "CConsole__Status", "CConsole__StatusDone"),
        (("CALL", "0x004f27f0"), ("MOV", "[0x0083d9b4]"), ("CALL", "0x0042b500")),
    ),
    "0x004f2a30": target(
        "CTexture__ClearOut",
        "void __cdecl CTexture__ClearOut(void)",
        ("texture shutdown clear-out helper", "DAT_0083d9b4", "DAT_0083d9b0", "leaked textures"),
        {"leak-report", "resource-lifecycle", "shutdown", "texture"},
        ("void __cdecl", "CTexture__Release", "Texture_resource_leaks", "No_texture_resource_leaks"),
        (("CALL", "0x00556f50"), ("MOV", "[0x0083d9b4], 0x0"), ("CALL", "0x0040c640")),
    ),
    "0x004f2b40": target(
        "CTexture__FreeLevelResources",
        "void __cdecl CTexture__FreeLevelResources(void)",
        ("end-of-level texture resource free helper", "DAT_0083d9b8", "DAT_0083d9b4", "end-of-level texture leaks"),
        {"leak-report", "level-unload", "resource-lifecycle", "texture"},
        ("void __cdecl", "DAT_0083d9b8 = 0", "CTexture__Release", "No_end_of_level_texture_resource"),
        (("MOV", "[0x0083d9b8], 0x0"), ("CALL", "0x00556f50"), ("CALL", "0x0040c640")),
    ),
    "0x004f2c60": target(
        "CTGALoader__CTGALoader",
        "void * __thiscall CTGALoader__CTGALoader(void * this, char * filename, void * status_out)",
        ("CTGALoader constructor", "RET 0x8", "CImageLoader__Constructor", "0x005df518", "this+0x118"),
        {"constructor", "imageloader", "tgaloader", "vtable"},
        ("void * __thiscall", "filename", "status_out", "PTR_CTGALoader__ScalarDeletingDestructor_005df518"),
        (("CALL", "0x00488620"), ("MOV", "0x5df518"), ("RET", "0x8")),
    ),
    "0x004f2c90": target(
        "CTGALoader__ScalarDeletingDestructor",
        "void * __thiscall CTGALoader__ScalarDeletingDestructor(void * this, byte flags)",
        ("scalar-deleting destructor wrapper", "RET 0x4", "flags&1", "CTGALoader__Destructor"),
        {"destructor", "scalar-deleting", "stale-name-corrected", "tgaloader"},
        ("void * __thiscall", "byte flags", "CTGALoader__Destructor", "CDXMemoryManager__Free"),
        (("CALL", "0x004f2cb0"), ("CALL", "0x00549220"), ("RET", "0x4")),
    ),
    "0x004f2cb0": target(
        "CTGALoader__Destructor",
        "void __thiscall CTGALoader__Destructor(void * this)",
        ("CTGALoader destructor body", "0x005df518", "CImageLoader__Destructor"),
        {"destructor", "imageloader", "stale-name-corrected", "tgaloader"},
        ("void __thiscall", "PTR_CTGALoader__ScalarDeletingDestructor_005df518", "CImageLoader__Destructor"),
        (("MOV", "0x5df518"), ("JMP", "0x00488700")),
    ),
    "0x004f2ce0": target(
        "CTGALoader__Load",
        "bool __thiscall CTGALoader__Load(void * this)",
        ("TGA decode body", "image types 2 and 10", "24-bit or 32-bit", "RLE packet data", "+0x14 buffer"),
        {"alpha", "image-loader", "rle", "tga", "tgaloader"},
        ("bool __thiscall", "CDXMemBuffer__InitFromFile", "OID__AllocObject", "0x77", "return true"),
        (("CALL", "0x00547d70"), ("CALL", "0x00547ec0"), ("CALL", "0x00548c00")),
    ),
    "0x004f3110": target(
        "ImageIO__WriteTGA24",
        "bool __cdecl ImageIO__WriteTGA24(char * path, void * pixels32, int width, int height, int pitch_bytes)",
        ("24-bit TGA writer", "18-byte TGA header", "pitch_bytes", "Save24BitWithPitch"),
        {"image-io", "screenshot", "tga-writer", "tgaloader"},
        ("bool __cdecl", "pitch_bytes", "fopen", "fwrite", "return true"),
        (("CALL", "0x0055e490"), ("MOV", "0x18"), ("MOV", "word ptr [ESP + 0x24]")),
    ),
}

EXPECTED_XREFS = {
    ("0x004f27f0", "0x004f29de", "CTexture__InitDefaultTextureResourcesAndStatus", "UNCONDITIONAL_CALL"),
    ("0x004f2c60", "0x004911ef", "CMapTex__LoadTexture", "UNCONDITIONAL_CALL"),
    ("0x004f2c60", "0x00440ca6", "CDamage__LoadDamageTexture", "UNCONDITIONAL_CALL"),
    ("0x004f2c90", "0x005df518", "<no_function>", "DATA"),
    ("0x004f2ce0", "0x00491203", "CMapTex__LoadTexture", "UNCONDITIONAL_CALL"),
    ("0x004f2ce0", "0x00440cb8", "CDamage__LoadDamageTexture", "UNCONDITIONAL_CALL"),
    ("0x004f2ce0", "0x005df51c", "<no_function>", "DATA"),
    ("0x004f3110", "0x005135c4", "CEngine__GrabScreenshot", "UNCONDITIONAL_CALL"),
    ("0x004f3110", "0x00558851", "CDXTexture__DumpTextureToRGBA", "UNCONDITIONAL_CALL"),
}

EXPECTED_VTABLE = {
    "0": ("0x004f2c90", "CTGALoader__ScalarDeletingDestructor"),
    "1": ("0x004f2ce0", "CTGALoader__Load"),
    "2": ("0x00488670", "CImageLoader__GetFilenamePtr"),
    "4": ("0x00488680", "CImageLoader__GetWidth"),
    "5": ("0x00488690", "CImageLoader__GetHeight"),
    "7": ("0x004de070", "SharedVFunc__ReturnField14_004de070"),
    "9": ("0x00488740", "CImageLoader__FreeWidthBuffer"),
    "10": ("0x00488760", "CImageLoader__FreeHeightBuffer"),
    "11": ("0x00488780", "CImageLoader__LoadWidthBuffer"),
    "12": ("0x004887c0", "CImageLoader__LoadHeightBuffer"),
}

EXPECTED_LOG_SUMMARIES = {
    "apply_wave513_dry.log": "SUMMARY updated=0 skipped=9 renamed=0 would_rename=2 missing=0 bad=0",
    "apply_wave513_apply.log": "SUMMARY updated=9 skipped=0 renamed=2 would_rename=0 missing=0 bad=0",
    "apply_wave513_verify_dry.log": "SUMMARY updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0",
}

PUBLIC_NOTE_TOKENS = (
    "Wave513",
    "9",
    "2 renames",
    "CTexture__FindTexture",
    "CTGALoader__Load",
    "ImageIO__WriteTGA24",
    "runtime rendering behavior",
    "runtime image loading",
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry", "pointer_addr"):
            if key in row and row[key]:
                row[key] = normalize_addr(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def find_decomp_file(decomp_dir: Path, address: str) -> Path:
    candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
    require(bool(candidates), f"missing decompile export for {address}")
    return candidates[0]


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str]:
    wanted = normalize_addr(address)
    for row in rows:
        if row.get(key) == wanted:
            return row
    raise AssertionError(f"missing row for {address}")


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
        text = find_decomp_file(decomp_dir, address).read_text(encoding="utf-8", errors="replace")
        for token in expected["decompile_tokens"]:
            require(token_present(text, str(token)), f"{address} decompile missing token {token!r}")


def validate_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_addr: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_addr.setdefault(row["target_addr"], []).append(row)
    for address, expected in TARGETS.items():
        text_rows = [row for row in by_addr.get(normalize_addr(address), []) if row["function_entry"] == normalize_addr(address)]
        require(text_rows, f"{address} missing function-entry instruction rows")
        for mnemonic, operand_token in expected["instruction_tokens"]:
            found = any(
                row["mnemonic"] == mnemonic and token_present(row["operands"], operand_token)
                for row in text_rows
            )
            require(found, f"{address} instruction token missing: {mnemonic} {operand_token!r}")


def validate_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    got = {
        (
            row["target_addr"],
            row["from_addr"],
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    missing = EXPECTED_XREFS - got
    require(not missing, f"missing expected xrefs: {sorted(missing)}")


def validate_vtable(base: Path) -> None:
    rows = read_tsv(base / "post_vtable_slots.tsv")
    for slot, (address, name) in EXPECTED_VTABLE.items():
        matches = [
            row
            for row in rows
            if row["slot_index"] == slot and row["pointer_addr"] == normalize_addr(address)
        ]
        require(len(matches) == 1, f"vtable slot {slot} expected pointer {address}, found {len(matches)}")
        row = matches[0]
        require(row["function_entry"] == normalize_addr(address), f"vtable slot {slot} function entry mismatch")
        require(row["function_name"] == name, f"vtable slot {slot} function name mismatch: {row['function_name']}")


def validate_logs(base: Path) -> None:
    for name, expected in EXPECTED_LOG_SUMMARIES.items():
        path = base / name
        require(path.exists(), f"missing mutation log: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        require(expected in text, f"{name} missing summary {expected!r}")
        require("LockException" not in text, f"{name} contains LockException")
        require("BADNAME:" not in text and "MISSING:" not in text, f"{name} contains failed mutation row")


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
    validate_instructions(base)
    validate_xrefs(base)
    validate_vtable(base)
    validate_logs(base)
    validate_public_note()
    print(f"PASS wave513 texture/TGA evidence: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
