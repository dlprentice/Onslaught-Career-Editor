#!/usr/bin/env python3
"""Validate Wave510 start/respawn static RE evidence."""

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
    / "wave510-start-respawn-004ea8d0"
)
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_start_respawn_wave510_2026-05-17.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "start-respawn-wave510",
    "static-reaudit",
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
    "0x004ea8d0": target(
        "CRelaxedSquad__CreateIterator",
        "void * __fastcall CRelaxedSquad__CreateIterator(void * this)",
        ("CRelaxedSquad member iterator", "0x10-byte CSPtrSet", "this+0xa4", "CSquadNormal iterator pattern"),
        {"iterator", "member-set", "relaxed-squad", "stale-purpose-corrected"},
        ("void * __fastcall CRelaxedSquad__CreateIterator", "CSPtrSet__AddToHead", "+ 0xa4"),
        (("CALL", "0x005490e0"), ("CALL", "0x004e5840"), ("RET", "")),
    ),
    "0x004eacc0": target(
        "CStart__Constructor",
        "void * __thiscall CStart__Constructor(void * this)",
        ("CStart constructor-like body", "active-reader cell at this+0x7c", "embedded CStartInitThing", "0x005df2ec"),
        {"constructor", "init-thing", "respawn", "start"},
        ("void * __thiscall CStart__Constructor", "CGenericActiveReader__SetReader", "PTR_CComplexThing__HandleEvent_005df2ec", "PTR_LAB_005df274"),
        (("CALL", "0x004f3e10"), ("CALL", "0x00401000"), ("MOV", "[ESI], 0x5df2ec")),
    ),
    "0x004ead70": target(
        "CStart__ScalarDeletingDestructor",
        "void * __thiscall CStart__ScalarDeletingDestructor(void * this, byte flags)",
        ("scalar-deleting destructor wrapper", "RET 0x4", "CDXMemoryManager__Free", "flags&1"),
        {"destructor", "scalar-deleting", "start", "vfunc-slot-1"},
        ("void * __thiscall CStart__ScalarDeletingDestructor", "CStart__Destructor", "CDXMemoryManager__Free"),
        (("CALL", "0x004ead90"), ("CALL", "0x00549220"), ("RET", "0x4")),
    ),
    "0x004ead90": target(
        "CStart__Destructor",
        "void __fastcall CStart__Destructor(void * this)",
        ("removes this from the global start set DAT_00855100", "unregisters the active-reader cell", "CComplexThing__dtor_base"),
        {"active-reader", "destructor", "global-list", "start"},
        ("void __fastcall CStart__Destructor", "CSPtrSet__Remove(&DAT_00855100", "CComplexThing__dtor_base"),
        (("CALL", "0x004e5bd0"), ("CALL", "0x004f3f00"), ("RET", "")),
    ),
    "0x004eae10": target(
        "CStart__Init",
        "void __thiscall CStart__Init(void * this, void * init)",
        ("vtable 0x005df2ec slot 9", "CStaticShadows__SampleShadowHeightBilinear", "DAT_00855100", "CStart__SpawnBattleEngine(play_effect=0)"),
        {"init", "respawn", "start", "static-shadows", "vfunc-slot-9"},
        ("void __thiscall CStart__Init", "CStaticShadows__SampleShadowHeightBilinear", "CStart__SpawnBattleEngine", "DAT_00855100"),
        (("CALL", "0x0047eb80"), ("CALL", "0x004eaf20"), ("RET", "0x4")),
    ),
    "0x004eaf20": target(
        "CStart__SpawnBattleEngine",
        "void * __thiscall CStart__SpawnBattleEngine(void * this, int play_effect)",
        ("used by CStart init and CGame::RespawnPlayer fallback", "OID type 3", "BE_Respawn_Ground_Effect", "BE_Respawn_Air_Effect"),
        {"respawn", "spawn-battleengine", "stale-owner-corrected", "start"},
        ("void * __thiscall CStart__SpawnBattleEngine", "OID__CreateObject", "BE_Respawn_Ground_Effect", "BE_Respawn_Air_Effect"),
        (("CALL", "0x004bf090"), ("CALL", "0x00401000"), ("RET", "0x4")),
    ),
    "0x004eb130": target(
        "CStart__Available",
        "bool __fastcall CStart__Available(void * this)",
        ("CGame::RespawnPlayer", "CMapWho", "nearby hostile", "returns true when the start is clear"),
        {"availability", "predicate", "respawn", "stale-owner-corrected", "start"},
        ("bool __fastcall CStart__Available", "CMapWho__GetFirstEntryWithinRadius", "return true"),
        (("CALL", "0x00491ea0"), ("RET", "")),
    ),
}

EXPECTED_XREFS = {
    ("0x004ea8d0", "0x005e3b10", "<no_function>", "DATA"),
    ("0x004eacc0", "0x004bf324", "OID__CreateObject", "UNCONDITIONAL_CALL"),
    ("0x004ead70", "0x005df2f0", "<no_function>", "DATA"),
    ("0x004ead90", "0x004ead73", "CStart__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),
    ("0x004eae10", "0x005df310", "<no_function>", "DATA"),
    ("0x004eaf20", "0x004eaf0f", "CStart__Init", "UNCONDITIONAL_CALL"),
    ("0x004eaf20", "0x004703a0", "CGame__RespawnPlayer", "UNCONDITIONAL_CALL"),
    ("0x004eb130", "0x00470393", "CGame__RespawnPlayer", "UNCONDITIONAL_CALL"),
}

EXPECTED_VTABLE_SLOTS = {
    ("0x005e3ad0", "16", "0x004ea8d0", "CRelaxedSquad__CreateIterator"),
    ("0x005e3b10", "0", "0x004ea8d0", "CRelaxedSquad__CreateIterator"),
    ("0x005df2ec", "1", "0x004ead70", "CStart__ScalarDeletingDestructor"),
    ("0x005df2ec", "9", "0x004eae10", "CStart__Init"),
    ("0x005df274", "31", "0x004ead70", "CStart__ScalarDeletingDestructor"),
    ("0x005df274", "39", "0x004eae10", "CStart__Init"),
}

EXPECTED_LOG_SUMMARIES = {
    "apply_wave510_dry.log": "SUMMARY updated=0 skipped=7 renamed=0 would_rename=7 missing=0 bad=0",
    "apply_wave510_apply.log": "SUMMARY updated=7 skipped=0 renamed=7 would_rename=0 missing=0 bad=0",
    "apply_wave510_verify_dry.log": "SUMMARY updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0",
}

PUBLIC_NOTE_TOKENS = (
    "7",
    "7 renames",
    "CRelaxedSquad__CreateIterator",
    "CStart__SpawnBattleEngine",
    "CStart__Available",
    "CGame::RespawnPlayer",
    "runtime respawn behavior",
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


def find_decomp_file(decomp_dir: Path, address: str, expected_name: str) -> Path:
    candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
    if not candidates:
        candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:].lstrip('0')}_*.c"))
    require(bool(candidates), f"missing decompile export for {address} {expected_name}")
    return candidates[0]


def validate_metadata(base: Path) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    by_addr = {normalize_addr(row["address"]): row for row in rows}
    require(set(TARGETS).issubset(by_addr), "post metadata missing one or more Wave510 targets")
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
    require(set(TARGETS).issubset(by_addr), "post tags missing one or more Wave510 targets")
    for address, expected in TARGETS.items():
        raw_tags = by_addr[address]["tags"].replace(",", ";")
        tags = {tag.strip() for tag in raw_tags.split(";") if tag.strip()}
        missing = expected["tags"] - tags
        require(not missing, f"{address} missing tags: {sorted(missing)}")


def validate_decompile(base: Path) -> None:
    decomp_dir = base / "post-decomp"
    require(decomp_dir.exists(), f"missing decompile dir: {decomp_dir}")
    for address, expected in TARGETS.items():
        path = find_decomp_file(decomp_dir, address, str(expected["name"]))
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in expected["decompile_tokens"]:
            require(token in text, f"{address} decompile missing token {token!r}")


def validate_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_addr: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_addr.setdefault(normalize_addr(row["target_addr"]), []).append(row)
    for address, expected in TARGETS.items():
        rows_for_target = by_addr.get(address, [])
        require(rows_for_target, f"{address} missing instruction rows")
        for mnemonic, operand_token in expected["instruction_tokens"]:
            found = any(
                row["mnemonic"] == mnemonic and operand_token in compact_text(row.get("operands", ""))
                for row in rows_for_target
            )
            require(found, f"{address} missing instruction token {mnemonic} {operand_token!r}")


def validate_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    actual = {
        (
            normalize_addr(row["target_addr"]),
            normalize_addr(row["from_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    missing = EXPECTED_XREFS - actual
    require(not missing, f"missing xrefs: {sorted(missing)}")


def validate_vtables(base: Path) -> None:
    rows = read_tsv(base / "post_vtables.tsv")
    actual = {
        (
            normalize_addr(row["vtable"]),
            row["slot_index"],
            normalize_addr(row["function_entry"]),
            row["function_name"],
        )
        for row in rows
    }
    missing = EXPECTED_VTABLE_SLOTS - actual
    require(not missing, f"missing vtable slots: {sorted(missing)}")


def validate_logs(base: Path) -> None:
    for filename, expected in EXPECTED_LOG_SUMMARIES.items():
        path = base / filename
        require(path.exists(), f"missing log: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        require(expected in text, f"{filename} missing summary {expected!r}")
        require("REPORT: Save succeeded" in text, f"{filename} missing save success")
        for token in ("MISSING:", "BADNAME:", "Exception", "LockException"):
            require(token not in text, f"{filename} contains {token}")


def validate_public_note() -> None:
    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    text = PUBLIC_NOTE.read_text(encoding="utf-8", errors="replace")
    for token in PUBLIC_NOTE_TOKENS:
        require(token in text, f"public note missing token {token!r}")


def validate_queue(base: Path) -> None:
    path = base / "queue_after_wave510.txt"
    require(path.exists(), f"missing queue snapshot: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in ("Total functions:", "Commentless functions:", "Undefined signatures:", "Param signatures:"):
        require(token in text, f"queue snapshot missing {token}")


def run_check(base: Path) -> None:
    validate_metadata(base)
    validate_tags(base)
    validate_decompile(base)
    validate_instructions(base)
    validate_xrefs(base)
    validate_vtables(base)
    validate_logs(base)
    validate_public_note()
    validate_queue(base)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    try:
        run_check(args.base)
    except AssertionError as exc:
        if args.check:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1
        raise

    print(f"PASS: Wave510 start/respawn evidence validated at {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
