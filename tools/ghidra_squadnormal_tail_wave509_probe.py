#!/usr/bin/env python3
"""Validate Wave509 CSquadNormal tail static RE evidence."""

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
    / "wave509-squadnormal-tail-004e5e70"
)
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_squadnormal_tail_wave509_2026-05-17.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "squadnormal-tail-wave509",
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
    "0x004e5e70": target(
        "CSquad__Init",
        "void __thiscall CSquad__Init(void * this, void * init)",
        ("vtable 0x005def1c slot 9", "DAT_008553fc", "CWorldPhysicsManager__CreateThingByType", "DAT_008550a0"),
        {"init", "spawn", "squad", "vfunc-slot-9"},
        ("void __thiscall CSquad__Init", "CWorldPhysicsManager__CreateThingByType", "CComplexThing__Init", "DAT_008550a0"),
        (("MOV", "[EDI + 0x9c]"), ("MOV", "[EBP + 0x4c0]"), ("MOV", "[0x008553fc]")),
    ),
    "0x004e6610": target(
        "SharedState__IsTimer88PendingAndState7CZero",
        "bool __fastcall SharedState__IsTimer88PendingAndState7CZero(void * this)",
        ("DAT_00672fd0", "this+0x88", "this+0x7c", "previous CExplosionInitThing owner"),
        {"predicate", "shared-state", "stale-owner-corrected", "timer-predicate"},
        ("bool __fastcall SharedState__IsTimer88PendingAndState7CZero", "DAT_00672fd0", "+ 0x88", "+ 0x7c"),
        (("FLD", "[ECX + 0x88]"), ("FCOMP", "[0x00672fd0]"), ("RET", "")),
    ),
    "0x004e66d0": target(
        "SharedVFunc__ForwardProcessNoOp",
        "void __thiscall SharedVFunc__ForwardProcessNoOp(void * this, void * process_arg)",
        ("RET 0x4", "process_arg", "0x00452b60", "old CWaypoint-specific owner"),
        {"forwarder", "process", "shared-vfunc", "stale-owner-corrected"},
        ("void __thiscall SharedVFunc__ForwardProcessNoOp", "CFrontEndPage__Process_NoOp"),
        (("CALL", "0x00452b60"), ("RET", "0x4")),
    ),
    "0x004e7110": target(
        "CSquadNormal__Process",
        "int __thiscall CSquadNormal__Process(void * this, void * process_arg)",
        ("pursuit/target mode", "column versus attack formation", "spawn/split", "averages live member positions"),
        {"formation", "member-set", "process", "squad-normal"},
        ("int __thiscall CSquadNormal__Process", "CSquadNormal__BuildColumnFormation", "CSquadNormal__BuildAttackFormation", "CSquadNormal__SpawnMembers"),
        (("SUB", "0xbc"), ("CALL", "0x004e81d0"), ("CALL", "[EAX + 0x124]")),
    ),
    "0x004e81d0": target(
        "CSquadNormal__EvaluateLeaderTargetPursuitMode",
        "int __fastcall CSquadNormal__EvaluateLeaderTargetPursuitMode(void * this)",
        ("support/escort candidates", "CUnit__CanFireAtTarget_BallisticArcB", "small mode value"),
        {"pursuit-mode", "squad-normal", "target-selection"},
        ("int __fastcall CSquadNormal__EvaluateLeaderTargetPursuitMode", "CSquadNormal__SelectBestSupportOrEscort", "CUnit__CanFireAtTarget_BallisticArcB"),
        (("CALL", "0x004fb840"), ("CALL", "0x004fb5a0"), ("RET", "")),
    ),
    "0x004e83b0": target(
        "CSquadNormal__PruneDeadMembersAndReschedule",
        "void __thiscall CSquadNormal__PruneDeadMembersAndReschedule(void * this, int schedule_event)",
        ("RET 0x4", "event 0xfa1", "this+0xb4", "this+0xbc"),
        {"event-0xfa1", "formation", "member-set", "squad-normal"},
        ("void __thiscall CSquadNormal__PruneDeadMembersAndReschedule", "CSPtrSet__Remove", "CEventManager__AddEvent_AtTime", "0xfa1"),
        (("CALL", "0x004e84e0"), ("PUSH", "0xfa1"), ("RET", "0x4")),
    ),
    "0x004e84e0": target(
        "CSquadNormal__ResolveFormationSlotConflicts",
        "bool __fastcall CSquadNormal__ResolveFormationSlotConflicts(void * this)",
        ("reader nodes at this+0xa4", "CGenericActiveReader__SwapWithCandidateIfFormationCloser", "returns true when no swap"),
        {"formation", "member-set", "predicate", "squad-normal"},
        ("bool __fastcall CSquadNormal__ResolveFormationSlotConflicts", "CGenericActiveReader__SwapWithCandidateIfFormationCloser", "return bVar7"),
        (("CALL", "0x004e97e0"), ("RET", "")),
    ),
    "0x004e8730": target(
        "CSquadNormal__BuildColumnFormation",
        "void __fastcall CSquadNormal__BuildColumnFormation(void * this)",
        ("column offsets", "this+0xbc", "vfunc +0xf4"),
        {"column-formation", "formation", "member-set", "squad-normal"},
        ("void __fastcall CSquadNormal__BuildColumnFormation", "CSquadNormal__PruneDeadMembersAndReschedule", "CSquadNormal__ResolveFormationSlotConflicts"),
        (("CALL", "0x004e83b0"), ("CALL", "0x004e84e0"), ("RET", "")),
    ),
    "0x004e8930": target(
        "CSquadNormal__BuildAttackFormation",
        "void __fastcall CSquadNormal__BuildAttackFormation(void * this)",
        ("attack offsets", "target/support readers", "vfunc +0xf4"),
        {"attack-formation", "formation", "member-set", "squad-normal"},
        ("void __fastcall CSquadNormal__BuildAttackFormation", "CSquadNormal__PruneDeadMembersAndReschedule", "CSquadNormal__ResolveFormationSlotConflicts"),
        (("CALL", "0x004e83b0"), ("CALL", "0x004e84e0"), ("RET", "")),
    ),
    "0x004e8dd0": target(
        "CSquadNormal__ShouldSwitchToAttackFormation",
        "bool __fastcall CSquadNormal__ShouldSwitchToAttackFormation(void * this)",
        ("vtable +0x128", "+0x3c", "this+0x9c"),
        {"attack-formation", "formation", "predicate", "squad-normal"},
        ("bool __fastcall CSquadNormal__ShouldSwitchToAttackFormation", "+ 0x128", "+ 0x9c"),
        (("CALL", "[EAX + 0x128]"), ("RET", "")),
    ),
    "0x004e8ed0": target(
        "CSquadNormal__CreateIterator",
        "void * __fastcall CSquadNormal__CreateIterator(void * this)",
        ("0x10-byte CSPtrSet", "this+0xa4", "this+0xac", "returns that set pointer"),
        {"iterator", "member-set", "squad-normal", "undefined-signature-corrected"},
        ("void * __fastcall CSquadNormal__CreateIterator", "OID__AllocObject(0x10", "CSPtrSet__AddToHead", "+ 0xac"),
        (("CALL", "0x005490e0"), ("CALL", "0x004e5840"), ("RET", "")),
    ),
    "0x004e8f80": target(
        "CSquadNormal__TryMergeWithNearbySquad",
        "void __thiscall CSquadNormal__TryMergeWithNearbySquad(void * this, int force_merge)",
        ("RET 0x4", "force_merge", "DAT_008550a0", "transfers them through the target squad vfunc +0x10c"),
        {"global-list", "member-set", "merge", "squad-normal"},
        ("void __thiscall CSquadNormal__TryMergeWithNearbySquad", "DAT_008550a0", "CSquadNormal__RemoveMember"),
        (("MOV", "[EBP + 0xc4]"), ("CALL", "[EDX + 0x10c]"), ("RET", "0x4")),
    ),
    "0x004e91f0": target(
        "CSquadNormal__SpawnMembers",
        "void __fastcall CSquadNormal__SpawnMembers(void * this)",
        ("allocating a new CSquadNormal", "CInitThing", "removing the member", "static-shadow height"),
        {"member-set", "spawn", "squad-normal", "undefined-signature-corrected"},
        ("void __fastcall CSquadNormal__SpawnMembers", "CSquadNormal__Constructor", "CInitThing__ctor", "CStaticShadows__SampleShadowHeightBilinear"),
        (("CALL", "0x004e6870"), ("CALL", "0x004e6f70"), ("RET", "")),
    ),
    "0x004e9570": target(
        "CSquadNormal__SetFactionAndRefreshGlobalLists",
        "void __thiscall CSquadNormal__SetFactionAndRefreshGlobalLists(void * this, int faction_state)",
        ("faction_state at this+0x7c", "DAT_008550c0", "DAT_008550b0", "state values 0, 1, and 6"),
        {"faction", "global-list", "member-set", "squad-normal"},
        ("void __thiscall CSquadNormal__SetFactionAndRefreshGlobalLists", "CUnit__SetFactionForHierarchy", "DAT_008550c0", "DAT_008550b0"),
        (("MOV", "[ESI + 0x7c]"), ("CALL", "0x004fd830"), ("CALL", "0x004e5bd0")),
    ),
    "0x004e97e0": target(
        "CGenericActiveReader__SwapWithCandidateIfFormationCloser",
        "bool __thiscall CGenericActiveReader__SwapWithCandidateIfFormationCloser(void * this, void * candidate_reader)",
        ("active-reader slot-swap helper", "RET 0x4", "CGenericActiveReader__SetReader", "candidate pairing is closer"),
        {"active-reader", "formation", "predicate", "stale-owner-corrected"},
        ("bool __thiscall CGenericActiveReader__SwapWithCandidateIfFormationCloser", "CGenericActiveReader__SetReader"),
        (("CALL", "0x00401ec0"), ("CALL", "0x0040d2c0")),
    ),
}

EXPECTED_XREFS = {
    ("0x004e5e70", "0x005def40", "<no_function>", "DATA"),
    ("0x004e5e70", "0x004e6c50", "CSquadNormal__Init", "UNCONDITIONAL_CALL"),
    ("0x004e6610", "0x00414d1c", "CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices", "UNCONDITIONAL_CALL"),
    ("0x004e66d0", "0x005defe8", "<no_function>", "DATA"),
    ("0x004e7110", "0x004e7079", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004e81d0", "0x004e720e", "CSquadNormal__Process", "UNCONDITIONAL_CALL"),
    ("0x004e83b0", "0x004e873b", "CSquadNormal__BuildColumnFormation", "UNCONDITIONAL_CALL"),
    ("0x004e83b0", "0x004e8942", "CSquadNormal__BuildAttackFormation", "UNCONDITIONAL_CALL"),
    ("0x004e84e0", "0x004e8473", "CSquadNormal__PruneDeadMembersAndReschedule", "UNCONDITIONAL_CALL"),
    ("0x004e8730", "0x004e7c79", "CSquadNormal__Process", "UNCONDITIONAL_CALL"),
    ("0x004e8930", "0x004e7bc2", "CSquadNormal__Process", "UNCONDITIONAL_CALL"),
    ("0x004e8ed0", "0x005df238", "<no_function>", "DATA"),
    ("0x004e8f80", "0x004e7c06", "CSquadNormal__Process", "UNCONDITIONAL_CALL"),
    ("0x004e91f0", "0x004e7bfd", "CSquadNormal__Process", "UNCONDITIONAL_CALL"),
    ("0x004e9570", "0x005df250", "<no_function>", "DATA"),
    ("0x004e97e0", "0x004e8640", "CSquadNormal__ResolveFormationSlotConflicts", "UNCONDITIONAL_CALL"),
}

EXPECTED_VTABLE_SLOTS = {
    ("0x005def1c", "9", "0x004e5e70", "CSquad__Init"),
    ("0x005def1c", "51", "0x004e66d0", "SharedVFunc__ForwardProcessNoOp"),
    ("0x005df07c", "111", "0x004e8ed0", "CSquadNormal__CreateIterator"),
    ("0x005df07c", "112", "0x004e8dd0", "CSquadNormal__ShouldSwitchToAttackFormation"),
    ("0x005df07c", "117", "0x004e9570", "CSquadNormal__SetFactionAndRefreshGlobalLists"),
    ("0x005df0f4", "81", "0x004e8ed0", "CSquadNormal__CreateIterator"),
    ("0x005df0f4", "82", "0x004e8dd0", "CSquadNormal__ShouldSwitchToAttackFormation"),
    ("0x005df0f4", "87", "0x004e9570", "CSquadNormal__SetFactionAndRefreshGlobalLists"),
}

EXPECTED_LOG_SUMMARIES = {
    "apply_wave509_dry.log": "SUMMARY updated=0 skipped=15 renamed=0 would_rename=4 missing=0 bad=0",
    "apply_wave509_apply.log": "SUMMARY updated=15 skipped=0 renamed=4 would_rename=0 missing=0 bad=0",
    "apply_wave509_verify_dry.log": "SUMMARY updated=0 skipped=15 renamed=0 would_rename=0 missing=0 bad=0",
}

PUBLIC_NOTE_TOKENS = (
    "15",
    "4 renames",
    "CSquad__Init",
    "SharedState__IsTimer88PendingAndState7CZero",
    "SharedVFunc__ForwardProcessNoOp",
    "CGenericActiveReader__SwapWithCandidateIfFormationCloser",
    "runtime AI behavior",
    "rebuild parity",
)


def normalize_addr(address: str) -> str:
    address = (address or "").strip().lower()
    if not address or address.startswith("<"):
        return address
    if address.startswith("0x"):
        body = address[2:]
    else:
        body = address
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
    require(set(TARGETS).issubset(by_addr), "post metadata missing one or more Wave509 targets")
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
    require(set(TARGETS).issubset(by_addr), "post tags missing one or more Wave509 targets")
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
        bad_tokens = ("MISSING:", "BADNAME:", "Exception", "LockException")
        for token in bad_tokens:
            require(token not in text, f"{filename} contains {token}")


def validate_public_note() -> None:
    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    text = PUBLIC_NOTE.read_text(encoding="utf-8", errors="replace")
    for token in PUBLIC_NOTE_TOKENS:
        require(token in text, f"public note missing token {token!r}")


def validate_queue(base: Path) -> None:
    path = base / "queue_after_wave509.txt"
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

    print(f"PASS: Wave509 CSquadNormal tail evidence validated at {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
