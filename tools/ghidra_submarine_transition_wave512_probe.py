#!/usr/bin/env python3
"""Validate Wave512 submarine/unit transition static RE evidence."""

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
    / "wave512-submarine-transition-004eec80"
)
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_submarine_transition_wave512_2026-05-17.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "submarine-transition-wave512",
}


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
    "0x004eec80": target(
        "CSubmarine__Init",
        "void __thiscall CSubmarine__Init(void * this, void * unit_init)",
        ("RET 0x4", "this+0x250", "0x60-byte CSubmarineAI-style", "0x20-byte CSubmarineGuide"),
        {"component-allocation", "init", "submarine", "unit-init"},
        ("void __thiscall CSubmarine__Init", "unit_init", "CUnit__Init", "CSubmarineGuide__CSubmarineGuide"),
        (("CALL", "0x004f86d0"), ("CALL", "0x005490e0"), ("CALL", "0x004ef570"), ("RET", "0x4")),
    ),
    "0x004eedc0": target(
        "CSubmarineAI__ScalarDeletingDestructor",
        "void * __thiscall CSubmarineAI__ScalarDeletingDestructor(void * this, byte flags)",
        ("scalar-deleting destructor", "RET 0x4", "flags&1", "CSubmarineAI__DestructorBody"),
        {"ai", "destructor", "scalar-deleting", "stale-vfunc-corrected", "submarine"},
        ("void * __thiscall CSubmarineAI__ScalarDeletingDestructor", "byte flags", "CSubmarineAI__DestructorBody", "CDXMemoryManager__Free"),
        (("CALL", "0x004eede0"), ("CALL", "0x00549220"), ("RET", "0x4")),
    ),
    "0x004eede0": target(
        "CSubmarineAI__DestructorBody",
        "void __fastcall CSubmarineAI__DestructorBody(void * this)",
        ("derived CSubmarineAI destructor body", "CUnitAI base vtable", "+0x28, +0x24, and +0x0c", "CMonitor__Shutdown"),
        {"ai", "destructor", "monitor", "sptrset", "stale-owner-corrected", "submarine"},
        ("void __fastcall CSubmarineAI__DestructorBody", "PTR_LAB_005d8d1c", "CSPtrSet__Remove", "CMonitor__Shutdown"),
        (("MOV", "0x5d8d1c"), ("CALL", "0x004e5bd0"), ("CALL", "0x004bac40"), ("RET", "")),
    ),
    "0x004ef000": target(
        "CUnit__SetTransitionState1AndNotifyChildren",
        "void __fastcall CUnit__SetTransitionState1AndNotifyChildren(void * this)",
        ("this+0x250 from 2 or 3 to 1", "this+0x19c", "vfunc +0x5c"),
        {"child-notify", "transition-state", "unit"},
        ("void __fastcall CUnit__SetTransitionState1AndNotifyChildren", "+ 0x250", "+ 0x19c", "+ 0x5c"),
        (("MOV", "[ECX + 0x250], 0x1"), ("CALL", "[EAX + 0x5c]"), ("RET", "")),
    ),
    "0x004ef050": target(
        "CUnit__SetTransitionState3_IfState0Or1",
        "void __fastcall CUnit__SetTransitionState3_IfState0Or1(void * this)",
        ("this+0x250 to 3", "prior value is 0 or 1"),
        {"state-setter", "transition-state", "unit"},
        ("void __fastcall CUnit__SetTransitionState3_IfState0Or1", "+ 0x250", "= 3"),
        (("MOV", "[ECX + 0x250], 0x3"), ("RET", "")),
    ),
    "0x004ef0f0": target(
        "CUnit__SetTransitionState2",
        "void __fastcall CUnit__SetTransitionState2(void * this)",
        ("this+0x250 to 2", "nearby state-machine body"),
        {"state-setter", "transition-state", "unit"},
        ("void __fastcall CUnit__SetTransitionState2", "+ 0x250", "= 2"),
        (("MOV", "[ECX + 0x250], 0x2"), ("RET", "")),
    ),
    "0x004ef120": target(
        "CMonitor__SpawnParticleEffectFromIndexedListInHeightBand",
        "void __fastcall CMonitor__SpawnParticleEffectFromIndexedListInHeightBand(void * this)",
        ("this+0x164/+0xec", "DAT_008553f8", "up to 100 samples", "particle effect within the global height band"),
        {"effect-spawn", "height-band", "monitor", "particle"},
        ("void __fastcall CMonitor__SpawnParticleEffectFromIndexedListInHeightBand", "DAT_008553f8", "local_28", "CParticleManager__CreateEffect"),
        (("MOV", "0x008553f8"), ("CALL", "dword ptr [EDX + 0x20]"), ("CALL", "0x004cb3d0"), ("RET", "")),
    ),
    "0x004ef570": target(
        "CSubmarineGuide__CSubmarineGuide",
        "void * __thiscall CSubmarineGuide__CSubmarineGuide(void * this, void * owner_submarine)",
        ("RET 0x4", "CGuide__ctor_base", "0x005df438", "returns this"),
        {"constructor", "guide", "submarine", "vtable"},
        ("void * __thiscall CSubmarineGuide__CSubmarineGuide", "owner_submarine", "CGuide__ctor_base", "PTR_SharedVFunc__NoOpOneArg_004014c0_005df438"),
        (("CALL", "0x0047e290"), ("MOV", "0x5df438"), ("RET", "0x4")),
    ),
}

EXPECTED_XREFS = {
    ("0x004eec80", "0x005e14b4", "<no_function>", "DATA"),
    ("0x004eedc0", "0x005df408", "<no_function>", "DATA"),
    ("0x004eede0", "0x004eedc3", "CSubmarineAI__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),
    ("0x004ef000", "0x005361fc", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004ef050", "0x0053621c", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004ef0f0", "0x004ef726", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004ef120", "0x004eeff0", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004ef570", "0x004eed8e", "CSubmarine__Init", "UNCONDITIONAL_CALL"),
}

EXPECTED_LOG_SUMMARIES = {
    "apply_wave512_dry.log": "SUMMARY updated=0 skipped=8 renamed=0 would_rename=2 missing=0 bad=0",
    "apply_wave512_apply.log": "SUMMARY updated=8 skipped=0 renamed=2 would_rename=0 missing=0 bad=0",
    "apply_wave512_verify_dry.log": "SUMMARY updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0",
}

PUBLIC_NOTE_TOKENS = (
    "Wave512",
    "8",
    "2 renames",
    "CSubmarineAI__ScalarDeletingDestructor",
    "CSubmarineAI__DestructorBody",
    "runtime submarine behavior",
    "runtime transition behavior",
    "runtime effect behavior",
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def find_decomp_file(decomp_dir: Path, address: str) -> Path:
    candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
    require(bool(candidates), f"missing decompile export for {address}")
    return candidates[0]


def validate_metadata(base: Path) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    by_addr = {normalize_addr(row["address"]): row for row in rows}
    require(set(TARGETS).issubset(by_addr), "post metadata missing one or more Wave512 targets")
    for address, expected in TARGETS.items():
        row = by_addr[address]
        require(row["name"] == expected["name"], f"{address} name mismatch: {row['name']}")
        require(row["signature"] == expected["signature"], f"{address} signature mismatch: {row['signature']}")
        comment = compact_text(row["comment"])
        for token in expected["comment_tokens"]:
            require(token in comment, f"{address} comment missing token {token!r}")


def validate_tags(base: Path) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    by_addr = {normalize_addr(row["address"]): row for row in rows}
    require(set(TARGETS).issubset(by_addr), "post tags missing one or more Wave512 targets")
    for address, expected in TARGETS.items():
        raw_tags = by_addr[address]["tags"].replace(",", ";")
        tags = {tag.strip() for tag in raw_tags.split(";") if tag.strip()}
        missing = expected["tags"] - tags
        require(not missing, f"{address} missing tags: {sorted(missing)}")


def validate_decompile(base: Path) -> None:
    decomp_dir = base / "post_decomp"
    require(decomp_dir.exists(), f"missing decompile dir: {decomp_dir}")
    for address, expected in TARGETS.items():
        text = find_decomp_file(decomp_dir, address).read_text(encoding="utf-8", errors="replace")
        for token in expected["decompile_tokens"]:
            require(token in text, f"{address} decompile missing token {token!r}")


def validate_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_addr: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_addr.setdefault(normalize_addr(row["target_addr"]), []).append(row)
    for address, expected in TARGETS.items():
        text_rows = by_addr.get(address, [])
        require(text_rows, f"{address} missing instruction rows")
        for mnemonic, operand_token in expected["instruction_tokens"]:
            found = any(
                row["mnemonic"] == mnemonic and operand_token in row["operands"]
                for row in text_rows
            )
            require(found, f"{address} instruction token missing: {mnemonic} {operand_token!r}")


def validate_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    got = {
        (
            normalize_addr(row["target_addr"]),
            normalize_addr(row["from_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    missing = EXPECTED_XREFS - got
    require(not missing, f"missing expected xrefs: {sorted(missing)}")


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
    validate_logs(base)
    validate_public_note()
    print(f"PASS wave512 submarine/transition evidence: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
