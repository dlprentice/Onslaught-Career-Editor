#!/usr/bin/env python3
"""Validate Wave519 ThunderHead static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave519-thunderhead-004f4730"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_thunderhead_wave519_2026-05-18.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "thunderhead",
    "thunderhead-wave519",
}

OVERCLAIM_TOKENS = (
    "runtime targeting proven",
    "runtime combat ai proven",
    "runtime behavior proven",
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
    "0x004f4730": target(
        "CThunderHead__CreateLegMotion",
        "void __thiscall CThunderHead__CreateLegMotion(void * this, void * init_context)",
        ("vtable 0x005e11b0 slot 1", "LegMotion", "this+0x70", "3.4/0.99", "remain unproven"),
        {"factory", "leg-motion", "motion-controller", "vtable-slot"},
        ("s_LegMotion_00623074", "OID__AllocObject(0xf0,0x1b", "CMCMech__SetParams", "0x70"),
    ),
    "0x004f4830": target(
        "CThunderHead__CreateWarspite",
        "void __thiscall CThunderHead__CreateWarspite(void * this, void * init_context)",
        ("vtable 0x005e11b0 slot 2", "0x60-byte", "CWarspite__Init", "this+0x13c", "remain unproven"),
        {"factory", "vtable-slot", "warspite-style"},
        ("OID__AllocObject(0x60,0x16", "CWarspite__Init", "0x13c"),
    ),
    "0x004f48a0": target(
        "CThunderHead__CreateGuide",
        "void __fastcall CThunderHead__CreateGuide(void * this)",
        ("vtable 0x005e11b0 slot 3", "0x30-byte", "CThunderheadGuide__Init", "this+0x208", "remain unproven"),
        {"factory", "guide", "vtable-slot"},
        ("OID__AllocObject(0x30,0x17", "CThunderheadGuide__Init", "0x208"),
    ),
    "0x004f4e00": target(
        "CThunderheadGuide__Init",
        "void * __thiscall CThunderheadGuide__Init(void * this, void * owner_unit, int copied_state_0, int copied_state_4, int copied_state_8, int copied_state_c)",
        ("RET 0x14", "CGuide__ctor_base", "vtable 0x005df8d4", "this+0x20..this+0x2c", "remain unproven"),
        {"guide", "init", "name-corrected"},
        ("CGuide__ctor_base", "PTR_SharedVFunc__NoOpOneArg_004014c0_005df8d4", "copied_state_0", "this + 0x2c"),
    ),
    "0x004f4e40": target(
        "CThunderheadGuide__VFunc_03_004f4e40",
        "void __fastcall CThunderheadGuide__VFunc_03_004f4e40(void * this)",
        ("vtable 0x005df8d4 slot 3", "0x004f51b4", "owner flag gate", "slot +0x100", "remain unproven"),
        {"boundary-recovered", "function-boundary", "guide", "vtable-slot"},
        ("CThunderheadGuide__VFunc_03_004f4e40", "CUnitAI__IsDeployAnimationState", "slot +0x100", "0x14c"),
    ),
}

EXPECTED_XREFS = {
    ("0x004f4730", "0x005e11b4", "<no_function>", "DATA"),
    ("0x004f4830", "0x005e11b8", "<no_function>", "DATA"),
    ("0x004f48a0", "0x005e11bc", "<no_function>", "DATA"),
    ("0x004f4e00", "0x004f4900", "CThunderHead__CreateGuide", "UNCONDITIONAL_CALL"),
    ("0x004f4e40", "0x005df8e0", "<no_function>", "DATA"),
}

EXPECTED_VTABLE_SLOTS = {
    ("0x005e11b0", "1", "0x004f4730", "CThunderHead__CreateLegMotion", "OK"),
    ("0x005e11b0", "2", "0x004f4830", "CThunderHead__CreateWarspite", "OK"),
    ("0x005e11b0", "3", "0x004f48a0", "CThunderHead__CreateGuide", "OK"),
    ("0x005df8d4", "3", "0x004f4e40", "CThunderheadGuide__VFunc_03_004f4e40", "OK"),
}

EXPECTED_INSTRUCTIONS = {
    ("post_instructions.tsv", "0x004f4801", "RET", "0x4", "CThunderHead__CreateLegMotion"),
    ("post_instructions.tsv", "0x004f4894", "RET", "0x4", "CThunderHead__CreateWarspite"),
    ("post_instructions.tsv", "0x004f4e34", "RET", "0x14", "CThunderheadGuide__Init"),
    ("post_instructions.tsv", "0x004f4e40", "SUB", "ESP, 0x48", "CThunderheadGuide__VFunc_03_004f4e40"),
    ("post_boundary_probe_instructions.tsv", "0x004f51a8", "MOV", "[ECX]", "CThunderheadGuide__VFunc_03_004f4e40"),
    ("post_boundary_probe_instructions.tsv", "0x004f51b4", "RET", "", "CThunderheadGuide__VFunc_03_004f4e40"),
    ("post_boundary_probe_instructions.tsv", "0x004f51c0", "MOV", "0x0083e6a0", "<no_function>"),
}

PUBLIC_NOTE_TOKENS = (
    "Wave519",
    "CThunderHead__CreateLegMotion",
    "CThunderheadGuide__VFunc_03_004f4e40",
    "0x004f51b4",
    "runtime targeting behavior",
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
            "from_function_addr",
            "instruction_addr",
            "function_entry",
            "pointer_addr",
            "vtable",
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


def validate_vtable_slots(base: Path) -> None:
    rows = read_tsv(base / "post_vtable_slots.tsv")
    got = {
        (row["vtable"], row["slot_index"], row["pointer_addr"], row["function_name"], row["status"])
        for row in rows
    }
    missing = EXPECTED_VTABLE_SLOTS - got
    require(not missing, f"missing expected vtable slots: {sorted(missing)}")


def validate_instructions(base: Path) -> None:
    cached: dict[str, list[dict[str, str]]] = {}
    for filename, address, mnemonic, operand_token, function_name in EXPECTED_INSTRUCTIONS:
        rows = cached.setdefault(filename, read_tsv(base / filename))
        matches = [row for row in rows if row.get("instruction_addr") == normalize_addr(address)]
        require(matches, f"missing instruction row {filename}:{address}")
        row = matches[0]
        require(row["mnemonic"] == mnemonic, f"{address} mnemonic mismatch: {row['mnemonic']}")
        require(function_name == row["function_name"], f"{address} function mismatch: {row['function_name']}")
        if operand_token:
            require(token_present(row["operands"], operand_token), f"{address} operands missing {operand_token!r}")


def validate_counts(base: Path) -> None:
    require(len(read_tsv(base / "post_metadata.tsv")) == 5, "post metadata row count mismatch")
    require(len(read_tsv(base / "post_tags.tsv")) == 5, "post tags row count mismatch")
    require(len(read_tsv(base / "post_xrefs.tsv")) == 5, "post xref row count mismatch")
    require(len(read_tsv(base / "post_instructions.tsv")) >= 1400, "post instruction export unexpectedly small")
    require(len(read_tsv(base / "post_boundary_probe_instructions.tsv")) >= 300, "post boundary export unexpectedly small")
    decomp_index = read_tsv(base / "post_decomp" / "index.tsv")
    require(len(decomp_index) == 5, "post decompile index row count mismatch")
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
    validate_vtable_slots(base)
    validate_instructions(base)
    validate_counts(base)
    if args.check:
        validate_public_note()
    print(f"PASS wave519 ThunderHead evidence: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
