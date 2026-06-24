#!/usr/bin/env python3
"""Validate Wave527 Unit faction/spawn static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave527-unit-faction-spawn-004fd830"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unit_faction_spawn_wave527_2026-05-18.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "unit-faction-spawn-wave527",
}

OVERCLAIM_TOKENS = (
    "runtime spawn behavior proven",
    "runtime ai behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)

TARGETS = {
    "0x004fd830": {
        "name": "CUnit__SetFactionForHierarchy",
        "signature": "void __thiscall CUnit__SetFactionForHierarchy(void * this, int faction_state)",
        "comment_tokens": ("RET 0x4", "this+0x138", "DAT_008550c0/DAT_008550b0", "remain unproven"),
        "tags": {"child-recursive", "global-unit-set", "unit-faction"},
        "decompile_tokens": ("CSPtrSet__Remove", "DAT_008550c0", "faction_state"),
    },
    "0x004fd8d0": {
        "name": "CUnit__FindChildReaderByField270",
        "signature": "void * __thiscall CUnit__FindChildReaderByField270(void * this, int field270_value)",
        "comment_tokens": ("owner Unit pointer", "this+0x19c", "RET 0x4", "remain unproven"),
        "tags": {"destructible-segment", "owner-corrected", "unit-child-list"},
        "decompile_tokens": ("field270_value", "0x270", "this + 0x19c"),
    },
    "0x004fd910": {
        "name": "CUnit__FindNearestFactionAnchor",
        "signature": "void __thiscall CUnit__FindNearestFactionAnchor(void * this, void * out_position4)",
        "comment_tokens": ("RET 0x4", "DAT_00855160", "vfunc +0x108", "remain unproven"),
        "tags": {"anchor-search", "position-output", "unit-faction"},
        "decompile_tokens": ("DAT_00855160", "out_position4", "SQRT"),
    },
    "0x004fda10": {
        "name": "CUnit__GetProfileState120",
        "signature": "int __fastcall CUnit__GetProfileState120(void * this)",
        "comment_tokens": ("attached Unit pointers", "this+0x164 -> +0x120", "remain unproven"),
        "tags": {"owner-corrected", "query", "unit-profile"},
        "decompile_tokens": ("this + 0x164", "0x120", "return"),
    },
    "0x004fda20": {
        "name": "CUnit__PropagateTargetUnitToHierarchy",
        "signature": "void __thiscall CUnit__PropagateTargetUnitToHierarchy(void * this, void * target_unit)",
        "comment_tokens": ("RET 0x4", "target_unit+0x148", "recursively", "remain unproven"),
        "tags": {"child-recursive", "script-attack", "unit-target"},
        "decompile_tokens": ("CSquadNormal__SetReaderAndRefreshSupportSelection", "CUnit__PropagateTargetUnitToHierarchy", "target_unit"),
    },
    "0x004fdad0": {
        "name": "CUnit__TrySpawnMembersForTarget",
        "signature": "void __thiscall CUnit__TrySpawnMembersForTarget(void * this, void * target_unit)",
        "comment_tokens": ("RET 0x4", "CUnit__CanProvideSupportNow", "CSpawnerThng__DoSpawn", "remain unproven"),
        "tags": {"support-selection", "target-gated", "unit-spawn"},
        "decompile_tokens": ("CUnit__CanProvideSupportNow", "CUnit__IsSupportTargetMaskCompatible", "CSpawnerThng__DoSpawn"),
    },
    "0x004fdc20": {
        "name": "CUnit__UpdateSpawnCountAccounting",
        "signature": "void __fastcall CUnit__UpdateSpawnCountAccounting(void * this)",
        "comment_tokens": ("DAT_008a9b8c", "CUnit__GetTypePriorityWeight", "CSpawnerThng__UpdateSpawnCount", "remain unproven"),
        "tags": {"global-counter", "unit-spawn", "vtable-target"},
        "decompile_tokens": ("DAT_008a9b8c", "CUnit__GetTypePriorityWeight", "CSpawnerThng__UpdateSpawnCount"),
    },
    "0x004fdcb0": {
        "name": "CUnit__SetEngagementModeAndMaybeClearTargetReader",
        "signature": "void __thiscall CUnit__SetEngagementModeAndMaybeClearTargetReader(void * this, int engagement_mode)",
        "comment_tokens": ("RET 0x4", "this+0x210", "CGenericActiveReader__SetReader", "remain unproven"),
        "tags": {"active-reader", "unit-engagement", "vtable-target"},
        "decompile_tokens": ("CGenericActiveReader__SetReader", "engagement_mode", "0x210"),
    },
}

EXPECTED_XREFS = {
    ("0x004fd830", "0x004e9597", "CSquadNormal__SetFactionAndRefreshGlobalLists", "UNCONDITIONAL_CALL"),
    ("0x004fd830", "0x0053557b", "IScript__SetThingRefViaCUnitHelper4FD830_FromArg", "UNCONDITIONAL_CALL"),
    ("0x004fd8d0", "0x00444750", "CDestructableSegmentsController__Init", "UNCONDITIONAL_CALL"),
    ("0x004fda10", "0x00422d3a", "CCarverAI__UpdateAttackAndReschedule", "UNCONDITIONAL_CALL"),
    ("0x004fda10", "0x00445f20", "CUnitAI__UpdateDoorWingEngagement_CloseRange", "UNCONDITIONAL_CALL"),
    ("0x004fda20", "0x00536011", "IScript__Attack", "UNCONDITIONAL_CALL"),
    ("0x004fdad0", "0x004ff68c", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004fdc20", "0x005d8aa0", "<no_function>", "DATA"),
    ("0x004fdcb0", "0x005d8a9c", "<no_function>", "DATA"),
    ("0x004fdcb0", "0x0047a9ca", "<no_function>", "UNCONDITIONAL_CALL"),
}

EXPECTED_RETS = {
    ("0x004fd8c8", "RET", "0x4", "CUnit__SetFactionForHierarchy"),
    ("0x004fd90b", "RET", "0x4", "CUnit__FindChildReaderByField270"),
    ("0x004fda0d", "RET", "0x4", "CUnit__FindNearestFactionAnchor"),
    ("0x004fda1c", "RET", "", "CUnit__GetProfileState120"),
    ("0x004fda8a", "RET", "0x4", "CUnit__PropagateTargetUnitToHierarchy"),
    ("0x004fdbfe", "RET", "0x4", "CUnit__TrySpawnMembersForTarget"),
    ("0x004fdc84", "RET", "", "CUnit__UpdateSpawnCountAccounting"),
    ("0x004fdce2", "RET", "0x4", "CUnit__SetEngagementModeAndMaybeClearTargetReader"),
}

PUBLIC_NOTE_TOKENS = (
    "Wave527",
    "CUnit__FindChildReaderByField270",
    "CUnit__GetProfileState120",
    "85 target xref rows",
    "runtime spawn behavior",
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
        for key in ("address", "target_addr", "from_addr", "instruction_addr", "function_entry"):
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
    require(bool(named), f"decompile export for {address} does not contain {expected_name}: {candidates}")
    return named[0]


def check_log(path: Path, expected_summary: str, require_script_report: bool) -> None:
    require(path.exists(), f"missing log: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    require(expected_summary in text, f"{path.name}: missing summary {expected_summary!r}")
    require("REPORT: Save succeeded" in text, f"{path.name}: missing save success")
    if require_script_report:
        require("ApplyUnitFactionSpawnWave527.java> REPORT: Save succeeded" in text, f"{path.name}: missing script save report")
    for bad in ("LockException", "MISSING:", "BADNAME:", "BADADDR:", "FAIL:"):
        require(bad not in text, f"{path.name}: contains {bad}")


def check_logs(base: Path) -> None:
    check_log(
        base / "apply_unit_faction_spawn_wave527_dry.log",
        "SUMMARY updated=0 skipped=8 renamed=0 would_rename=2 missing=0 bad=0",
        False,
    )
    check_log(
        base / "apply_unit_faction_spawn_wave527_apply.log",
        "SUMMARY updated=8 skipped=0 renamed=2 would_rename=0 missing=0 bad=0",
        True,
    )
    check_log(
        base / "apply_unit_faction_spawn_wave527_verify_dry.log",
        "SUMMARY updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0",
        False,
    )


def check_metadata(base: Path) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    require(len(rows) == len(TARGETS), f"expected {len(TARGETS)} metadata rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        require(row["status"] == "OK", f"{address} metadata status is {row['status']}")
        require(row["name"] == expected["name"], f"{address} name mismatch: {row['name']}")
        require(row["signature"] == expected["signature"], f"{address} signature mismatch: {row['signature']}")
        comment = row["comment"]
        for token in expected["comment_tokens"]:
            require(token_present(comment, token), f"{address} comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            require(not token_present(comment, token), f"{address} comment overclaims with {token!r}")


def check_tags(base: Path) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    require(len(rows) == len(TARGETS), f"expected {len(TARGETS)} tag rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        tags = {tag for tag in row["tags"].split(";") if tag}
        missing = (COMMON_TAGS | expected["tags"]) - tags
        require(not missing, f"{address} missing tags: {sorted(missing)}")


def check_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    require(len(rows) == 85, f"expected 85 xref rows, got {len(rows)}")
    actual = {
        (
            row["target_addr"],
            row["from_addr"],
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    expected = {(normalize_addr(t), normalize_addr(f), n, r) for t, f, n, r in EXPECTED_XREFS}
    missing = expected - actual
    require(not missing, f"missing xrefs: {sorted(missing)}")


def check_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    require(len(rows) == 3368, f"expected 3368 instruction rows, got {len(rows)}")
    actual = {
        (
            row["instruction_addr"],
            row["mnemonic"],
            row["operands"],
            row["function_name"],
        )
        for row in rows
    }
    expected = {(normalize_addr(a), m, o, f) for a, m, o, f in EXPECTED_RETS}
    missing = expected - actual
    require(not missing, f"missing RET evidence: {sorted(missing)}")


def check_decomp(base: Path) -> None:
    index_rows = read_tsv(base / "post_decomp" / "index.tsv")
    require(len(index_rows) == len(TARGETS), f"expected {len(TARGETS)} decompile index rows, got {len(index_rows)}")
    for address, expected in TARGETS.items():
        index_row = row_by_address(index_rows, address)
        require(index_row["name"] == expected["name"], f"{address} decompile index name mismatch")
        require(index_row["signature"] == expected["signature"], f"{address} decompile index signature mismatch")
        require(index_row["status"] == "OK", f"{address} decompile status {index_row['status']}")
        text = find_decomp_file(base / "post_decomp", address, expected["name"]).read_text(
            encoding="utf-8", errors="replace"
        )
        for token in expected["decompile_tokens"]:
            require(token_present(text, token), f"{address} decompile missing token {token!r}")
        for stale in ("param_1", "param_2", "CDestructableSegmentsController__FindMemberByField270", "CUnitAI__GetWeaponNodeState120"):
            require(not token_present(text, stale), f"{address} decompile contains stale token {stale!r}")


def check_public_note() -> None:
    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    text = PUBLIC_NOTE.read_text(encoding="utf-8", errors="replace")
    for token in PUBLIC_NOTE_TOKENS:
        require(token_present(text, token), f"public note missing token {token!r}")
    for token in OVERCLAIM_TOKENS:
        require(not token_present(text, token), f"public note overclaims with {token!r}")


def run_checks(base: Path) -> None:
    check_logs(base)
    check_metadata(base)
    check_tags(base)
    check_xrefs(base)
    check_instructions(base)
    check_decomp(base)
    check_public_note()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true", help="run validation checks")
    args = parser.parse_args()
    if not args.check:
        parser.print_help()
        return 0
    run_checks(args.base)
    print("Wave527 unit faction/spawn probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
