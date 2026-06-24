#!/usr/bin/env python3
"""Validate Wave504 CSpawnerThng static RE evidence."""

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
    / "wave504-spawnerthng-004e3010"
)

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "spawn-system",
    "spawner",
    "spawnerthng-wave504",
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
    "0x004e3010": target(
        "CSpawnerThng__Init",
        "void __thiscall CSpawnerThng__Init(void * this, void * init)",
        (
            "CSpawnerThng initializer",
            "SpawnerThng.cpp debug path",
            "CSpawnerInitThing source fields",
            "scheduling the first spawn event",
            "runtime spawn behavior",
            "rebuild parity remain unproven",
        ),
        {"init", "source-parity", "spawn-config", "spawn-event"},
        (
            "void __thiscall CSpawnerThng__Init",
            "CComplexThing__Init",
            "CGenericActiveReader__SetReader",
        ),
        (
            ("0x004e3010", "PUSH", "EBX"),
            ("0x004e3021", "AND", "byte ptr [EBP + 0x2c], 0xfd"),
        ),
    ),
    "0x004e3330": target(
        "CSpawnerThng__Shutdown",
        "void __fastcall CSpawnerThng__Shutdown(void * this)",
        (
            "CSpawnerThng shutdown helper",
            "active-reader owned references",
            "spawner-owned strings/resources",
            "runtime shutdown ordering",
        ),
        {"shutdown", "active-reader", "resource-cleanup"},
        (
            "void __fastcall CSpawnerThng__Shutdown",
            "CGenericActiveReader__SetReader",
        ),
        (
            ("0x004e3330", "PUSH", "ESI"),
            ("0x004e333f", "CALL", "0x00549220"),
            ("0x004e3364", "CALL", "0x004f41b0"),
        ),
    ),
    "0x004e3370": target(
        "CSpawnerThng__Update",
        "void __fastcall CSpawnerThng__Update(void * this)",
        (
            "CSpawnerThng update loop",
            "resolves named spawners",
            "advances spawn timers",
            "runtime wave scheduling behavior",
        ),
        {"update-loop", "spawn-timing", "active-reader"},
        (
            "void __fastcall CSpawnerThng__Update",
            "CSpawnerThng__FindSpawnerByName",
            "CGenericActiveReader__SetReader",
        ),
        (
            ("0x004e3370", "SUB", "ESP, 0x89c"),
            ("0x004e3377", "MOV", "EBX, ECX"),
        ),
    ),
    "0x004e36c0": target(
        "CSpawnerThng__FindSpawnerByName",
        "int __cdecl CSpawnerThng__FindSpawnerByName(char * spawner_name)",
        (
            "name lookup over the global spawner type/name table",
            "returns the matching index or -1",
            "runtime mission data coverage",
        ),
        {"name-lookup", "spawn-type-table", "query"},
        (
            "int __cdecl CSpawnerThng__FindSpawnerByName",
            "DAT_008553fc",
            "return -1",
        ),
        (
            ("0x004e36c0", "PUSH", "EBX"),
            ("0x004e36cc", "MOV", "EDX, dword ptr [0x008553fc]"),
        ),
    ),
    "0x004e37f0": target(
        "CSpawnerThng__Constructor",
        "void * __thiscall CSpawnerThng__Constructor(void * this, void * spawner_init, void * owner_context)",
        (
            "CSpawnerThng constructor",
            "allocated 0x3f8-byte object",
            "ECX as this and two stack arguments",
            "owner-context type",
            "runtime allocation behavior",
        ),
        {"constructor", "source-parity", "vtable", "world-physics-create"},
        (
            "void * __thiscall CSpawnerThng__Constructor",
            "CInitThing__ctor",
            "CSpawnerThng__IsSpawnTypeAllowed",
        ),
        (
            ("0x004e37f0", "PUSH", "-0x1"),
            ("0x004e382c", "CALL", "0x0048dcf0"),
        ),
    ),
    "0x004e39f0": target(
        "CSpawnerThng__ScalarDeletingDestructor",
        "void * __thiscall CSpawnerThng__ScalarDeletingDestructor(void * this, byte flags)",
        (
            "MSVC scalar deleting destructor wrapper",
            "conditionally frees the object",
            "allocator identity",
        ),
        {"destructor", "scalar-deleting", "vtable"},
        (
            "void * __thiscall CSpawnerThng__ScalarDeletingDestructor",
            "CSpawnerThng__Destructor",
        ),
        (
            ("0x004e39f0", "PUSH", "ESI"),
            ("0x004e39f3", "CALL", "0x004e3a10"),
        ),
    ),
    "0x004e3a10": target(
        "CSpawnerThng__Destructor",
        "void __fastcall CSpawnerThng__Destructor(void * this)",
        (
            "real CSpawnerThng destructor",
            "unwinds owned active readers/resources",
            "runtime destruction ordering",
        ),
        {"destructor", "active-reader", "resource-cleanup"},
        (
            "void __fastcall CSpawnerThng__Destructor",
            "CGenericActiveReader__SetReader",
            "CMonitor__Shutdown",
        ),
        (
            ("0x004e3a10", "PUSH", "-0x1"),
            ("0x004e3a28", "MOV", "EDI, ECX"),
        ),
    ),
    "0x004e3aa0": target(
        "CSpawnerThng__CleanupAndDelete",
        "void __fastcall CSpawnerThng__CleanupAndDelete(void * this)",
        (
            "cleanup/delete helper",
            "updates spawn-count accounting",
            "exact virtual slot identity",
        ),
        {"cleanup-delete", "spawn-accounting", "vtable"},
        (
            "void __fastcall CSpawnerThng__CleanupAndDelete",
            "CSpawnerThng__UpdateSpawnCount",
        ),
        (
            ("0x004e3aa0", "PUSH", "ESI"),
            ("0x004e3aa3", "CALL", "0x004e3ac0"),
        ),
    ),
    "0x004e3ac0": target(
        "CSpawnerThng__UpdateSpawnCount",
        "void __fastcall CSpawnerThng__UpdateSpawnCount(void * this)",
        (
            "spawn-count accounting helper",
            "global/accounting state",
            "runtime spawn-count side effects",
        ),
        {"global-counter", "spawn-accounting", "unit-spawn-list"},
        (
            "void __fastcall CSpawnerThng__UpdateSpawnCount",
            "DAT_008a9b8c",
            "CUnit__GetTypePriorityWeight",
        ),
        (
            ("0x004e3ac0", "PUSH", "EBX"),
            ("0x004e3ac1", "MOV", "EBX, ECX"),
        ),
    ),
    "0x004e3c60": target(
        "CSpawnerThng__DoSpawn",
        "bool __fastcall CSpawnerThng__DoSpawn(void * this)",
        (
            "boolean spawn dispatcher",
            "callers pass the spawner in ECX and test EAX",
            "calls ProcessSpawnWave",
            "runtime spawn success semantics",
        ),
        {"active-reader", "boolean-return", "spawn-dispatch", "squad-spawn"},
        (
            "bool __fastcall CSpawnerThng__DoSpawn",
            "CSpawnerThng__IsSpawnComplete",
            "CSpawnerThng__ProcessSpawnWave",
        ),
        (
            ("0x004e3c60", "SUB", "ESP, 0x4d8"),
            ("0x004e3c9b", "CALL", "0x004e4430"),
            ("0x004e3ca0", "TEST", "EAX, EAX"),
        ),
    ),
    "0x004e3f90": target(
        "CSpawnerThng__ProcessSpawnWave",
        "void __fastcall CSpawnerThng__ProcessSpawnWave(void * this)",
        (
            "active spawn-wave processor",
            "validates spawn position clearance",
            "exact type enum mapping",
            "runtime scheduling behavior",
        ),
        {"event-scheduler", "position-clearance", "spawn-wave", "type-mapping"},
        (
            "void __fastcall CSpawnerThng__ProcessSpawnWave",
            "CSpawnerThng__IsSpawnPositionClear",
            "CSpawnerThng__SetCooldownState3",
        ),
        (
            ("0x004e3f90", "SUB", "ESP, 0x3d4"),
            ("0x004e3f9c", "MOV", "EAX, dword ptr [EBP + 0x3ec]"),
            ("0x004e3fc8", "CALL", "dword ptr [EAX + 0x160]"),
        ),
    ),
    "0x004e4430": target(
        "CSpawnerThng__IsSpawnComplete",
        "bool __fastcall CSpawnerThng__IsSpawnComplete(void * this)",
        (
            "boolean completion query",
            "compares spawned counts against configured amount",
            "runtime completion edge cases",
        ),
        {"boolean-return", "query", "spawn-completion"},
        (
            "bool __fastcall CSpawnerThng__IsSpawnComplete",
            "return false",
            "return true",
        ),
        (
            ("0x004e4430", "MOV", "EAX, dword ptr [ECX + 0x3d0]"),
            ("0x004e4451", "MOV", "EAX, 0x1"),
        ),
    ),
    "0x004e44d0": target(
        "CSpawnerThng__IsSpawnPositionClear",
        "bool __thiscall CSpawnerThng__IsSpawnPositionClear(void * this, float * spawn_position)",
        (
            "boolean spawn-position clearance query",
            "position pointer on the stack",
            "queries map occupancy within a fixed radius",
            "runtime collision behavior",
        ),
        {"boolean-return", "collision-query", "mapwho", "position-clearance"},
        (
            "bool __thiscall CSpawnerThng__IsSpawnPositionClear",
            "CMapWho__GetFirstEntryWithinRadius",
            "return false",
            "return true",
        ),
        (
            ("0x004e44d0", "PUSH", "EBX"),
            ("0x004e44d1", "MOV", "EBX, ECX"),
            ("0x004e44e3", "CALL", "0x00406d20"),
        ),
    ),
}

EXPECTED_XREFS = {
    ("004e3010", "005dd190", "<no_function>"),
    ("004e3330", "005dd174", "<no_function>"),
    ("004e3370", "004e37b5", "<no_function>"),
    ("004e36c0", "00536d36", "<no_function>"),
    ("004e36c0", "004e33d0", "CSpawnerThng__Update"),
    ("004e36c0", "0050a67e", "<no_function>"),
    ("004e37f0", "0050fa22", "CWorldPhysicsManager__CreateSpawner"),
    ("004e39f0", "005dee98", "<no_function>"),
    ("004e3a10", "004e39f3", "CSpawnerThng__ScalarDeletingDestructor"),
    ("004e3aa0", "005dee9c", "<no_function>"),
    ("004e3ac0", "004e3aa3", "CSpawnerThng__CleanupAndDelete"),
    ("004e3ac0", "004fdc6b", "CUnit__UpdateSpawnCountAccounting"),
    ("004e3c60", "004face8", "CUnit__UpdateMotionAttachmentsAndEffects"),
    ("004e3c60", "004fc0f4", "CUnitAI__TrySpawnOrFinalizeAttachedUnit"),
    ("004e3c60", "004fdbdd", "CUnit__TrySpawnMembersForTarget"),
    ("004e3f90", "004e3f67", "CSpawnerThng__DoSpawn"),
    ("004e3f90", "004e446c", "<no_function>"),
    ("004e4430", "004e3c9b", "CSpawnerThng__DoSpawn"),
    ("004e4430", "004fd7f8", "CUnitAI__AreSpawnedChildrenReady"),
    ("004e44d0", "004e414c", "CSpawnerThng__ProcessSpawnWave"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def norm_addr(value: str) -> str:
    text = value.lower()
    if text.startswith("0x"):
        text = text[2:]
    return f"0x{int(text, 16):08x}"


def file_for_decomp(base: Path, addr: str, name: str) -> Path:
    short = addr[2:]
    return base / "post-decomp" / f"{short}_{name}.c"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_log(path: Path, expected: str, errors: list[str]) -> None:
    text = read_text(path)
    require(expected in text, f"{path.name}: missing summary {expected!r}", errors)
    require("REPORT: Save succeeded" in text, f"{path.name}: missing save success", errors)
    for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:"):
        require(bad not in text, f"{path.name}: contains {bad}", errors)


def check_metadata(base: Path, errors: list[str]) -> None:
    rows = {norm_addr(row["address"]): row for row in read_tsv(base / "post_metadata.tsv")}
    require(set(rows) == set(TARGETS), f"metadata addresses mismatch: {sorted(rows)}", errors)
    for addr, spec in TARGETS.items():
        row = rows.get(addr, {})
        require(row.get("status") == "OK", f"{addr}: metadata status not OK", errors)
        require(row.get("name") == spec["name"], f"{addr}: name mismatch", errors)
        require(row.get("signature") == spec["signature"], f"{addr}: signature mismatch", errors)
        comment = row.get("comment", "")
        for token in spec["comment_tokens"]:
            require(str(token) in comment, f"{addr}: missing comment token {token!r}", errors)


def check_tags(base: Path, errors: list[str]) -> None:
    rows = {norm_addr(row["address"]): row for row in read_tsv(base / "post_tags.tsv")}
    require(set(rows) == set(TARGETS), f"tag addresses mismatch: {sorted(rows)}", errors)
    for addr, spec in TARGETS.items():
        row = rows.get(addr, {})
        require(row.get("status") == "OK", f"{addr}: tag status not OK", errors)
        actual = set(filter(None, row.get("tags", "").split(";")))
        missing = set(spec["tags"]) - actual
        require(not missing, f"{addr}: missing tags {sorted(missing)}", errors)


def check_xrefs(base: Path, errors: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    actual = {
        (row["target_addr"].lower(), row["from_addr"].lower(), row["from_function"])
        for row in rows
    }
    require(
        actual == EXPECTED_XREFS,
        f"xrefs mismatch: expected {sorted(EXPECTED_XREFS)}, got {sorted(actual)}",
        errors,
    )


def check_decompile(base: Path, errors: list[str]) -> None:
    for addr, spec in TARGETS.items():
        path = file_for_decomp(base, addr, str(spec["name"]))
        require(path.exists(), f"{addr}: missing decompile {path}", errors)
        if not path.exists():
            continue
        text = read_text(path)
        for token in spec["decompile_tokens"]:
            require(str(token) in text, f"{addr}: missing decompile token {token!r}", errors)


def check_instructions(base: Path, errors: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    for addr, spec in TARGETS.items():
        for ins_addr, mnemonic, operands in spec["instruction_tokens"]:
            matches = [
                row for row in rows
                if norm_addr(row["target_addr"]) == addr
                and norm_addr(row["instruction_addr"]) == norm_addr(ins_addr)
                and row["function_name"] == spec["name"]
                and row["mnemonic"] == mnemonic
                and row["operands"] == operands
            ]
            require(
                bool(matches),
                f"{addr}: missing instruction {ins_addr} {mnemonic} {operands!r}",
                errors,
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    base = args.base.resolve()
    errors: list[str] = []

    require(base.exists(), f"missing base directory: {base}", errors)
    if base.exists():
        check_log(
            base / "apply_spawnerthng_wave504_dry.log",
            "SUMMARY: updated=0 skipped=13 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0",
            errors,
        )
        check_log(
            base / "apply_spawnerthng_wave504_apply.log",
            "SUMMARY: updated=13 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0",
            errors,
        )
        check_log(
            base / "apply_spawnerthng_wave504_final_verify_dry.log",
            "SUMMARY: updated=0 skipped=13 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0",
            errors,
        )
        check_metadata(base, errors)
        check_tags(base, errors)
        check_xrefs(base, errors)
        check_decompile(base, errors)
        check_instructions(base, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Wave504 CSpawnerThng probe OK: 13 functions validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
