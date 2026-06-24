#!/usr/bin/env python3
"""Validate Wave520 CTree static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave520-tree-004f5f60"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctree_wave520_2026-05-18.md"

COMMON_TAGS = {
    "comment-hardened",
    "ctree",
    "ctree-wave520",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

OVERCLAIM_TOKENS = (
    "runtime tree behavior proven",
    "runtime physics proven",
    "runtime particle behavior proven",
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
    "0x004f5f60": target(
        "CTree__InitFallingTreeData",
        "void * __thiscall CTree__InitFallingTreeData(void * this, void * tree_type_matrix, float scale, void * impact_vector)",
        ("RET 0x0c", "12-dword tree-type matrix", "impact/direction vector", "0x3ca3d70a", "remain unproven"),
        {"falling-tree", "initializer", "matrix-copy"},
        ("CTree__InitFallingTreeData", "tree_type_matrix", "impact_vector", "0x3ca3d70a"),
    ),
    "0x004f63c0": target(
        "CTree__dtor_base",
        "void __fastcall CTree__dtor_base(void * this)",
        ("destructor body", "CTree__scalar_deleting_dtor", "this+0x48", "CThing__dtor_base", "remain unproven"),
        {"destructor", "falling-tree", "name-corrected"},
        ("CTree__dtor_base", "CDXMemoryManager__Free", "CThing__dtor_base"),
    ),
    "0x004f6430": target(
        "CTree__ComputeLodBucket",
        "int __fastcall CTree__ComputeLodBucket(void * this)",
        ("CEngine__InitDamageSystem", "virtual slot +0x54", "clamps the result to bucket 6", "remain unproven"),
        {"lod", "resource-scalar"},
        ("CTree__ComputeLodBucket", "0x54", "bStack_8 = 6"),
    ),
    "0x004f68e0": target(
        "CTree__VFunc_28_CreateFallingTreeAfterDelay",
        "void __thiscall CTree__VFunc_28_CreateFallingTreeAfterDelay(void * this, float elapsed_time, void * other_thing, int unused_arg2, int unused_arg3)",
        ("vtable 0x005dd9d8 slot 40", "RET 0x10", "this+0x44", "CTree__CreateFallingTree", "remain unproven"),
        {"boundary-recovered", "falling-tree", "timer-gate", "vtable-slot"},
        ("CTree__VFunc_28_CreateFallingTreeAfterDelay", "elapsed_time", "other_thing", "CTree__CreateFallingTree"),
    ),
    "0x004f69b0": target(
        "CTree__CreateFallingTree",
        "void __thiscall CTree__CreateFallingTree(void * this, void * impact_vector)",
        ("RET 0x4", "DAT_008406b8", "0xc0-byte falling-tree", "event 0xbb9", "remain unproven"),
        {"allocator", "event-scheduled", "falling-tree"},
        ("DAT_008406b8", "OID__AllocObject(0xc0", "CTree__InitFallingTreeData", "CTree__UpdateFallingTree"),
    ),
    "0x004f6aa0": target(
        "CTree__VFunc_27_CreateFallingTreeFromThing",
        "void __thiscall CTree__VFunc_27_CreateFallingTreeFromThing(void * this, void * other_thing, int unused_context)",
        ("vtable 0x005dd9d8 slot 39", "RET 0x8", "other_thing flags", "CTree__CreateFallingTree", "remain unproven"),
        {"boundary-recovered", "collision-gate", "falling-tree", "vtable-slot"},
        ("CTree__VFunc_27_CreateFallingTreeFromThing", "other_thing", "0x1000000", "CTree__CreateFallingTree"),
    ),
    "0x004f6b80": target(
        "CTree__UpdateFallingTree",
        "void __fastcall CTree__UpdateFallingTree(void * this)",
        ("Tree Ground Hit Effect", "event 0x7d2", "rescheduling event 3000", "runtime particle/physics behavior", "remain unproven"),
        {"event-scheduled", "falling-tree", "particle-effect", "physics-update"},
        ("CHeightField__TraceLineAgainstHeightfield", "s_Tree_Ground_Hit_Effect_00633aa0", "0x7d2", "CEventManager__AddEvent_AtTime"),
    ),
    "0x004f7050": target(
        "CTree__HandleEvent",
        "void __thiscall CTree__HandleEvent(void * this, void * event)",
        ("vtable 0x005dd9d8 slot 0", "RET 0x4", "3000/3001", "CThing event handler", "remain unproven"),
        {"boundary-recovered", "event-handler", "falling-tree", "vtable-slot"},
        ("CTree__HandleEvent", "CTree__UpdateFallingTree", "CThing__HandleEvent", "CCollisionSeekingRound__SetCollisionMask"),
    ),
}

EXPECTED_XREFS = {
    ("0x004f5f60", "0x004f6a38", "CTree__CreateFallingTree", "UNCONDITIONAL_CALL"),
    ("0x004f63c0", "0x004bfce3", "CTree__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("0x004f6430", "0x0044a15e", "CEngine__InitDamageSystem", "UNCONDITIONAL_CALL"),
    ("0x004f68e0", "0x005dda78", "<no_function>", "DATA"),
    ("0x004f69b0", "0x004f699c", "CTree__VFunc_28_CreateFallingTreeAfterDelay", "UNCONDITIONAL_CALL"),
    ("0x004f69b0", "0x004f6b6f", "CTree__VFunc_27_CreateFallingTreeFromThing", "UNCONDITIONAL_CALL"),
    ("0x004f6aa0", "0x005dda74", "<no_function>", "DATA"),
    ("0x004f6b80", "0x004f7078", "CTree__HandleEvent", "UNCONDITIONAL_CALL"),
    ("0x004f7050", "0x005dd9d8", "<no_function>", "DATA"),
}

EXPECTED_VTABLE_SLOTS = {
    ("0x005dd9d8", "0", "0x004f7050", "CTree__HandleEvent", "OK"),
    ("0x005dd9d8", "1", "0x004bfce0", "CTree__scalar_deleting_dtor", "OK"),
    ("0x005dd9d8", "39", "0x004f6aa0", "CTree__VFunc_27_CreateFallingTreeFromThing", "OK"),
    ("0x005dd9d8", "40", "0x004f68e0", "CTree__VFunc_28_CreateFallingTreeAfterDelay", "OK"),
}

EXPECTED_INSTRUCTIONS = {
    ("post_boundary_probe_instructions.tsv", "0x004f68e0", "MOV", "[ECX + 0x48]", "CTree__VFunc_28_CreateFallingTreeAfterDelay"),
    ("post_boundary_probe_instructions.tsv", "0x004f699c", "CALL", "0x004f69b0", "CTree__VFunc_28_CreateFallingTreeAfterDelay"),
    ("post_boundary_probe_instructions.tsv", "0x004f69a4", "RET", "0x10", "CTree__VFunc_28_CreateFallingTreeAfterDelay"),
    ("post_boundary_probe_instructions.tsv", "0x004f6aa0", "MOV", "[ESP + 0x4]", "CTree__VFunc_27_CreateFallingTreeFromThing"),
    ("post_boundary_probe_instructions.tsv", "0x004f6b6f", "CALL", "0x004f69b0", "CTree__VFunc_27_CreateFallingTreeFromThing"),
    ("post_boundary_probe_instructions.tsv", "0x004f6b77", "RET", "0x8", "CTree__VFunc_27_CreateFallingTreeFromThing"),
    ("post_boundary_probe_instructions.tsv", "0x004f7050", "MOV", "[ESP + 0x4]", "CTree__HandleEvent"),
    ("post_boundary_probe_instructions.tsv", "0x004f7078", "CALL", "0x004f6b80", "CTree__HandleEvent"),
    ("post_boundary_probe_instructions.tsv", "0x004f707d", "RET", "0x4", "CTree__HandleEvent"),
}

PUBLIC_NOTE_TOKENS = (
    "Wave520",
    "CTree__CreateFallingTree",
    "CTree__VFunc_27_CreateFallingTreeFromThing",
    "CTree__HandleEvent",
    "6082",
    "runtime falling-tree physics",
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
    require(len(read_tsv(base / "post_metadata.tsv")) == 8, "post metadata row count mismatch")
    require(len(read_tsv(base / "post_tags.tsv")) == 8, "post tags row count mismatch")
    require(len(read_tsv(base / "post_xrefs.tsv")) == 12, "post xref row count mismatch")
    require(len(read_tsv(base / "post_instructions.tsv")) >= 1500, "post instruction export unexpectedly small")
    require(len(read_tsv(base / "post_boundary_probe_instructions.tsv")) >= 1100, "post boundary export unexpectedly small")
    require(len(read_tsv(base / "post_vtable_slots.tsv")) == 144, "post vtable slot row count mismatch")
    decomp_index = read_tsv(base / "post_decomp" / "index.tsv")
    require(len(decomp_index) == 8, "post decompile index row count mismatch")
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
    print(f"PASS wave520 CTree evidence: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
