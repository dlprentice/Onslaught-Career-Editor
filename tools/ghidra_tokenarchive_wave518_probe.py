#!/usr/bin/env python3
"""Validate Wave518 TokenArchive static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave518-tokenarchive-004f52b0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_tokenarchive_wave518_2026-05-17.md"

COMMON_TAGS = {
    "comment-hardened",
    "particle-config",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "tokenarchive-wave518",
}

OVERCLAIM_TOKENS = (
    "runtime parser proven",
    "runtime write coverage proven",
    "runtime particle parsing proven",
    "source-body identity proven",
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
    "0x004f52b0": target(
        "CTokenArchive__GetTokenName",
        "char * __cdecl CTokenArchive__GetTokenName(int token_id)",
        ("token_id 0..0x7b", "**Unknown Token**", "ReadNextToken", "writer helpers"),
        {"token-name", "token-table"},
        ("char * __cdecl", "token_id", "s____Unknown_Token"),
    ),
    "0x004f57b0": target(
        "CTokenArchive__ReadNextToken",
        "int __thiscall CTokenArchive__ReadNextToken(void * this, int * out_token_id, int * out_int_or_ref_index, float * out_float, char * out_string)",
        ("CTokenArchive__ReadLine", "out_token_id", "this+0x9c4c", "+0x8", "1/255"),
        {"parser", "reference-fixup", "token-reader"},
        ("int __thiscall", "out_token_id", "CTokenArchive__ReadLine", "0x9c4c", "_DAT_005df8fc"),
    ),
    "0x004f5b80": target(
        "CTokenArchive__RegisterReferenceFixup",
        "void __thiscall CTokenArchive__RegisterReferenceFixup(void * this, int ref_value, int slot_index, void * fixup_record)",
        ("ret 0x0c", "stale fourth parameter", "fixup_record", "this+0x0c"),
        {"reference-fixup", "stale-param-correction"},
        ("void __thiscall", "ref_value", "slot_index", "fixup_record"),
    ),
    "0x004f5ba0": target(
        "CTokenArchive__ResolveReferences",
        "void __thiscall CTokenArchive__ResolveReferences(void * this, void * list_head_ptr)",
        ("list_head_ptr", "CTokenArchive__BinarySearchByPredicate", "resets the pending-reference count", "+0x8"),
        {"reference-fixup", "resolver"},
        ("void __thiscall", "list_head_ptr", "CTokenArchive__BinarySearchByPredicate", "CDXMemoryManager__Free"),
    ),
    "0x004f5c90": target(
        "CTokenArchive__WriteInt",
        "void __stdcall CTokenArchive__WriteInt(int token_id, int value)",
        ("ret 0x8", "\"%s %d\"", "integer token output"),
        {"integer", "token-writer"},
        ("void __stdcall", "token_id", "value", "s__s__d"),
    ),
    "0x004f5cd0": target(
        "CTokenArchive__WriteFloat",
        "void __stdcall CTokenArchive__WriteFloat(int token_id, float value)",
        ("ret 0x8", "\"%s %f\"", "float token output"),
        {"float", "token-writer"},
        ("void __stdcall", "token_id", "value", "s__s__f"),
    ),
    "0x004f5d10": target(
        "CTokenArchive__WriteString",
        "void __stdcall CTokenArchive__WriteString(int token_id, char * value)",
        ("ret 0x8", "\"%s %s\"", "string token output"),
        {"string", "token-writer"},
        ("void __stdcall", "token_id", "value", "s__s__s"),
    ),
    "0x004f5d50": target(
        "CTokenArchive__WritePointer",
        "void __stdcall CTokenArchive__WritePointer(int token_id, void * named_object)",
        ("ret 0x8", "\"%s NONE\"", "named_object+4"),
        {"pointer-reference", "token-writer"},
        ("void __stdcall", "named_object", "s__s_NONE", "+ 4"),
    ),
    "0x004f5dc0": target(
        "CTokenArchive__WriteFloatPointer",
        "void __stdcall CTokenArchive__WriteFloatPointer(int token_id, void * value_ref_record)",
        ("ret 0x8", "\"%s %f NONE\"", "\"%s %f %s\"", "+4"),
        {"float", "pointer-reference", "token-writer"},
        ("void __stdcall", "value_ref_record", "s__s__f_NONE", "s__s__f__s"),
    ),
}

EXPECTED_XREFS = {
    ("0x004f52b0", "0x004f57eb", "CTokenArchive__ReadNextToken", "UNCONDITIONAL_CALL"),
    ("0x004f52b0", "0x004f5ca0", "CTokenArchive__WriteInt", "UNCONDITIONAL_CALL"),
    ("0x004f52b0", "0x004f5de5", "CTokenArchive__WriteFloatPointer", "UNCONDITIONAL_CALL"),
    ("0x004f57b0", "0x004cd86d", "CParticleSet__LoadFromArchive", "UNCONDITIONAL_CALL"),
    ("0x004f57b0", "0x004c576b", "CParticleDescriptor__Load", "UNCONDITIONAL_CALL"),
    ("0x004f5b80", "0x004c58e7", "CParticleDescriptor__Load", "UNCONDITIONAL_CALL"),
    ("0x004f5ba0", "0x004cd9cb", "CParticleSet__LoadFromArchive", "UNCONDITIONAL_CALL"),
    ("0x004f5c90", "0x004c081a", "CPDSimpleSprite__WriteTokenFields", "UNCONDITIONAL_CALL"),
}

PUBLIC_NOTE_TOKENS = (
    "Wave518",
    "CTokenArchive__ReadNextToken",
    "CTokenArchive__WriteFloatPointer",
    "6078",
    "3626",
    "1600",
    "1395",
    "runtime particle parsing",
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr"):
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


def find_decomp_file(decomp_dir: Path, address: str) -> Path:
    candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
    require(bool(candidates), f"missing decompile export for {address}")
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
        text = find_decomp_file(decomp_dir, address).read_text(encoding="utf-8", errors="replace")
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


def validate_counts(base: Path) -> None:
    require(len(read_tsv(base / "post_metadata.tsv")) == 9, "post metadata row count mismatch")
    require(len(read_tsv(base / "post_tags.tsv")) == 9, "post tags row count mismatch")
    require(len(read_tsv(base / "post_xrefs.tsv")) == 178, "post xref row count mismatch")
    require(len(read_tsv(base / "post_instructions.tsv")) >= 2500, "post instruction export unexpectedly small")
    decomp_index = read_tsv(base / "post_decomp" / "index.tsv")
    require(len(decomp_index) == 9, "post decompile index row count mismatch")
    for row in decomp_index:
        require(row["status"] == "OK", f"decompile failed for {row.get('address')}")


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
    validate_counts(base)
    if args.check:
        validate_public_note()
    print(f"PASS wave518 TokenArchive evidence: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
