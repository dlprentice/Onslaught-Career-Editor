#!/usr/bin/env python3
"""Validate Wave507 CShell/unit-tail static RE evidence."""

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
    / "wave507-engine-shell-004df4c0"
)

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "shell-unit-tail-wave507",
    "signature-corrected",
    "static-reaudit",
}


def target(
    name: str,
    signature: str,
    comment_tokens: tuple[str, ...],
    tags: set[str],
    decompile_tokens: tuple[str, ...],
    instruction_tokens: tuple[tuple[str, str, str], ...],
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
    "0x004df4c0": target(
        "CShell__Constructor",
        "void * __thiscall CShell__Constructor(void * this)",
        (
            "CShell constructor-like body",
            "OID__CreateObject xref reaches this entry",
            "vtables at 0x005ded48 and 0x005decd0",
            "inline 0x100-byte resource/name buffer at this+0x110",
        ),
        {"cshell", "constructor", "projectile-burst-shell", "vtable-backed"},
        (
            "void * __thiscall CShell__Constructor",
            "CThing__ctor_like_004f3e10",
            "PTR_CActor__HandleEvent_005ded48",
            "PTR_CActor__GetRenderPos_005decd0",
            "+ 0x110",
        ),
        (
            ("0x004df4c4", "CALL", "0x004f3e10"),
            ("0x004df4d6", "MOV", "dword ptr [ESI], 0x5ded48"),
            ("0x004df4dc", "MOV", "dword ptr [ESI + 0x8], 0x5decd0"),
            ("0x004df4e3", "STOSD.REP", "ES:EDI"),
        ),
    ),
    "0x004df530": target(
        "CShell__CopyResourceNameToInlineBuffer",
        "void __thiscall CShell__CopyResourceNameToInlineBuffer(void * this, char * resource_name)",
        (
            "stale-owner correction",
            "direct CShell helper, not CEngine-owned logic",
            "RET 0x4 proves one explicit resource_name argument",
            "ProjectileBurst__SpawnFromCurrentPreset calls this",
            "this+0x110",
        ),
        {
            "cshell",
            "projectile-burst-shell",
            "rename-corrected",
            "resource-name",
            "stale-owner-corrected",
        },
        (
            "void __thiscall CShell__CopyResourceNameToInlineBuffer",
            "char *resource_name",
            "+ 0x110",
        ),
        (
            ("0x004df530", "MOV", "EDX, dword ptr [ESP + 0x4]"),
            ("0x004df53a", "ADD", "ECX, 0x110"),
            ("0x004df54b", "RET", "0x4"),
        ),
    ),
    "0x004df550": target(
        "CShell__Init",
        "void __thiscall CShell__Init(void * this, void * init)",
        (
            "CShell init vfunc",
            "vtable 0x005ded48 slot 9",
            "RET 0x4 proves one explicit init argument",
            "CResourceDescriptor",
            "event 2000",
        ),
        {
            "cshell",
            "event-2000",
            "init",
            "projectile-burst-shell",
            "resource-descriptor",
            "vtable-slot-9",
        },
        (
            "void __thiscall CShell__Init",
            "CResourceDescriptor__ctor",
            "PCRTID__CreateObject",
            "CActor__Init",
            "CSquadNormal__BuildOrientationMatrixFromEuler",
            "CEventManager__AddEvent_AtTime",
        ),
        (
            ("0x004df5ea", "CALL", "0x00516580"),
            ("0x004df613", "CALL", "0x004011e0"),
            ("0x004df6ac", "CALL", "0x004062d0"),
            ("0x004df6e8", "CALL", "0x0044b370"),
            ("0x004df725", "RET", "0x4"),
        ),
    ),
    "0x004dfce0": target(
        "CUnit__TryActivateAndEnableShadows",
        "bool __thiscall CUnit__TryActivateAndEnableShadows(void * this)",
        (
            "unit-family predicate/update helper",
            "CUnit__MarkDestroyedAndCleanupLinks(this)",
            "global static-shadow manager 0x009c8010",
            "table 0x005dfe04 slot 0",
            "0x005dfd84 slot 32",
        ),
        {"predicate", "static-shadows", "unit", "vtable-backed"},
        (
            "bool __thiscall CUnit__TryActivateAndEnableShadows",
            "CUnit__MarkDestroyedAndCleanupLinks",
            "CStaticShadows__UpdateVisibility",
            "return false",
            "return true",
        ),
        (
            ("0x004dfce3", "CALL", "0x004fd140"),
            ("0x004dfcf1", "MOV", "ECX, 0x9c8010"),
            ("0x004dfcf6", "CALL", "0x004ebfb0"),
            ("0x004dfd01", "RET", ""),
        ),
    ),
    "0x004dfd10": target(
        "CUnit__VFunc18_SyncOldVectorAndClampHeight",
        "void __thiscall CUnit__VFunc18_SyncOldVectorAndClampHeight(void * this)",
        (
            "unit-family vfunc-slot-18 override",
            "CActor__VFunc_18_SyncOldVectorAfterBaseCall(this)",
            "this+0x24",
            "this+0x94",
            "0x006fbdfc",
        ),
        {"height-clamp", "old-vector-sync", "rename-corrected", "unit", "vfunc-slot-18"},
        (
            "void __thiscall CUnit__VFunc18_SyncOldVectorAndClampHeight",
            "CActor__VFunc_18_SyncOldVectorAfterBaseCall",
            "DAT_006fbdfc",
            "+ 0x24",
            "+ 0x94",
        ),
        (
            ("0x004dfd13", "CALL", "0x00402030"),
            ("0x004dfd18", "FLD", "float ptr [0x006fbdfc]"),
            ("0x004dfd2e", "FSTP", "float ptr [ESI + 0x24]"),
            ("0x004dfd37", "FSTP", "float ptr [ESI + 0x94]"),
            ("0x004dfd3e", "RET", ""),
        ),
    ),
}

EXPECTED_XREFS = {
    ("0x004df4c0", "0x004bf4f6", "OID__CreateObject", "UNCONDITIONAL_CALL"),
    ("0x004df530", "0x005076dc", "ProjectileBurst__SpawnFromCurrentPreset", "UNCONDITIONAL_CALL"),
    ("0x004df550", "0x005ded6c", "<no_function>", "DATA"),
    ("0x004dfce0", "0x005dfe04", "<no_function>", "DATA"),
    ("0x004dfd10", "0x005d8efc", "<no_function>", "DATA"),
    ("0x004dfd10", "0x005dfd84", "<no_function>", "DATA"),
}

EXPECTED_VTABLE_SLOTS = {
    ("0x005ded48", "9", "0x004df550", "CShell__Init"),
    ("0x005dfe04", "0", "0x004dfce0", "CUnit__TryActivateAndEnableShadows"),
    ("0x005d8efc", "0", "0x004dfd10", "CUnit__VFunc18_SyncOldVectorAndClampHeight"),
    ("0x005dfd84", "0", "0x004dfd10", "CUnit__VFunc18_SyncOldVectorAndClampHeight"),
    ("0x005dfd84", "32", "0x004dfce0", "CUnit__TryActivateAndEnableShadows"),
}

EXPECTED_LOG_SUMMARIES = {
    "apply_wave507_dry.log": "SUMMARY updated=0 skipped=5 renamed=0 would_rename=4 missing=0 bad=0",
    "apply_wave507_apply.log": "SUMMARY updated=5 skipped=0 renamed=4 would_rename=0 missing=0 bad=0",
    "apply_wave507_verify_dry.log": "SUMMARY updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"Missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_decompile(base: Path, address: str, name: str) -> str:
    path = base / "post-decomp" / f"{address[2:]}_{name}.c"
    if not path.exists():
        raise AssertionError(f"Missing decompile: {path}")
    return path.read_text(encoding="utf-8")


def normalize_addr(address: str) -> str:
    address = address.lower()
    return address if address.startswith("0x") else f"0x{address}"


def check_metadata(base: Path) -> None:
    rows = {normalize_addr(row["address"]): row for row in read_tsv(base / "post_metadata.tsv")}
    missing = set(TARGETS) - set(rows)
    if missing:
        raise AssertionError(f"Missing metadata rows: {sorted(missing)}")
    for address, spec in TARGETS.items():
        row = rows[address]
        if row["name"] != spec["name"]:
            raise AssertionError(f"{address} name {row['name']!r} != {spec['name']!r}")
        if row["signature"] != spec["signature"]:
            raise AssertionError(f"{address} signature {row['signature']!r} != {spec['signature']!r}")
        comment = row.get("comment") or ""
        for token in spec["comment_tokens"]:  # type: ignore[index]
            if token not in comment:
                raise AssertionError(f"{address} comment missing token {token!r}")


def check_tags(base: Path) -> None:
    rows = {normalize_addr(row["address"]): row for row in read_tsv(base / "post_tags.tsv")}
    missing = set(TARGETS) - set(rows)
    if missing:
        raise AssertionError(f"Missing tag rows: {sorted(missing)}")
    for address, spec in TARGETS.items():
        tags = {tag for tag in rows[address].get("tags", "").replace(",", ";").split(";") if tag}
        expected = spec["tags"]  # type: ignore[assignment]
        missing_tags = set(expected) - tags
        if missing_tags:
            raise AssertionError(f"{address} missing tags: {sorted(missing_tags)}")


def check_decompile(base: Path) -> None:
    for address, spec in TARGETS.items():
        text = read_decompile(base, address, spec["name"])  # type: ignore[arg-type]
        for token in spec["decompile_tokens"]:  # type: ignore[index]
            if token not in text:
                raise AssertionError(f"{address} decompile missing token {token!r}")


def check_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    for address, spec in TARGETS.items():
        function_name = str(spec["name"])
        function_rows = [row for row in rows if row["function_name"] == function_name]
        if not function_rows:
            raise AssertionError(f"{address} missing instruction rows for {function_name}")
        for instr_addr, mnemonic, operands in spec["instruction_tokens"]:  # type: ignore[index]
            if not any(
                row["instruction_addr"].lower() == instr_addr
                and row["mnemonic"] == mnemonic
                and row["operands"] == operands
                for row in function_rows
            ):
                raise AssertionError(f"{address} missing instruction {instr_addr} {mnemonic} {operands}")


def check_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    found = {
        (
            normalize_addr(row["target_addr"]),
            normalize_addr(row["from_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    missing = EXPECTED_XREFS - found
    if missing:
        raise AssertionError(f"Missing xrefs: {sorted(missing)}")


def check_vtables(base: Path) -> None:
    rows = read_tsv(base / "post_vtables.tsv")
    if len(rows) < 200:
        raise AssertionError(f"Expected at least 200 vtable rows, found {len(rows)}")
    found = {
        (
            normalize_addr(row["vtable"]),
            row["slot_index"],
            normalize_addr(row["pointer_addr"]),
            row["function_name"],
        )
        for row in rows
    }
    missing = EXPECTED_VTABLE_SLOTS - found
    if missing:
        raise AssertionError(f"Missing vtable slots: {sorted(missing)}")


def check_logs(base: Path) -> None:
    for filename, summary in EXPECTED_LOG_SUMMARIES.items():
        path = base / filename
        if not path.exists():
            raise AssertionError(f"Missing log: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        if summary not in text:
            raise AssertionError(f"{filename} missing summary {summary!r}")
        if "REPORT: Save succeeded" not in text:
            raise AssertionError(f"{filename} missing save success")
        for forbidden in ("LockException", " MISSING ", " BADADDR ", " FAIL "):
            if forbidden in text:
                raise AssertionError(f"{filename} contains forbidden token {forbidden!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    base = args.base
    check_metadata(base)
    check_tags(base)
    check_decompile(base)
    check_instructions(base)
    check_xrefs(base)
    check_vtables(base)
    check_logs(base)
    print(f"Wave507 CShell/unit-tail probe OK: {len(TARGETS)} functions validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
