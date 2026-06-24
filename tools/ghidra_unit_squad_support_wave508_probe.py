#!/usr/bin/env python3
"""Validate Wave508 unit/squad support static RE evidence."""

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
    / "wave508-unit-squad-support-004e43d0"
)
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unit_squad_support_wave508_2026-05-17.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "unit-squad-support-wave508",
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
    "0x004e43d0": target(
        "CUnit__CanProvideSupportNow",
        "bool __fastcall CUnit__CanProvideSupportNow(void * this)",
        ("this+0x3f4", "this+0x3ec", "DAT_00672fd0", "profile+0xc", "profile+0x24"),
        {"predicate", "support-readiness", "unit"},
        ("bool __fastcall CUnit__CanProvideSupportNow", "+ 0x3f4", "+ 0x3e0", "DAT_00672fd0"),
        (("MOV", "[ECX + 0x3f4]"), ("FLD", "[0x00672fd0]"), ("MOV", "[ECX + 0x3d0]")),
    ),
    "0x004e4420": target(
        "CUnit__IsInBlockedSupportState",
        "bool __fastcall CUnit__IsInBlockedSupportState(void * this)",
        ("this+0x3ec", "Unit, UnitAI, and CSquadNormal support/deploy paths"),
        {"predicate", "support-readiness", "unit"},
        ("bool __fastcall CUnit__IsInBlockedSupportState", "+ 0x3ec"),
        (("MOV", "[ECX + 0x3ec]"), ("SETNZ", "AL"), ("RET", "")),
    ),
    "0x004e4480": target(
        "CUnit__IsSupportTargetMaskCompatible",
        "bool __thiscall CUnit__IsSupportTargetMaskCompatible(void * this, void * target)",
        ("stale-owner correction", "not a CSquadNormal object method", "target+0x34", "RET 0x4"),
        {"stale-owner-corrected", "support-readiness", "target-mask", "unit"},
        ("bool __thiscall CUnit__IsSupportTargetMaskCompatible", "+ 0x3f0", "target", "+ 0x34"),
        (("MOV", "[ECX + 0x3f0]"), ("TEST", "[ECX + 0x34]"), ("RET", "0x4")),
    ),
    "0x004e4d70": target(
        "CSphere__VFunc02_ResolveCollisionAsCylinder",
        "void __thiscall CSphere__VFunc02_ResolveCollisionAsCylinder(void * this, void * collision_arg0, void * collision_arg1, void * collision_arg2, int collision_flags)",
        ("CSphere vfunc-slot-2 collision proxy", "vtable 0x005d88cc", "this+0x14", "CCylinder__ResolveCollisionVFunc02", "0x005d95f0"),
        {"collision", "collision-proxy", "sphere", "vfunc-slot-2"},
        ("void __thiscall CSphere__VFunc02_ResolveCollisionAsCylinder", "CCylinder__ResolveCollisionVFunc02", "+ 0x14"),
        (("FLD", "[ECX + 0x14]"), ("MOV", "0x5d88cc"), ("CALL", "0x0043fe20"), ("RET", "0x10")),
    ),
    "0x004e5da0": target(
        "CSquad__Constructor",
        "void * __thiscall CSquad__Constructor(void * this)",
        ("CSquad constructor-like base body", "CThing__ctor_like_004f3e10", "0x005def1c", "0x005deea4"),
        {"constructor", "squad", "vtable-backed"},
        ("void * __thiscall CSquad__Constructor", "CThing__ctor_like_004f3e10", "PTR_CSquad__HandleEvent_005def1c"),
        (("CALL", "0x004f3e10"), ("MOV", "[ESI], 0x5def1c"), ("MOV", "[ESI + 0x8], 0x5deea4")),
    ),
    "0x004e5e50": target(
        "SharedComplexThing__ScalarDeletingDestructor",
        "void * __thiscall SharedComplexThing__ScalarDeletingDestructor(void * this, byte flags)",
        ("shared-wrapper correction", "CComplexThing__dtor_base_Thunk_004bff30", "flags bit 0", "RET 0x4"),
        {"complexthing", "scalar-deleting-destructor", "shared-vfunc"},
        ("void * __thiscall SharedComplexThing__ScalarDeletingDestructor", "CComplexThing__dtor_base_Thunk_004bff30", "CDXMemoryManager__Free"),
        (("CALL", "0x004bff30"), ("CALL", "0x00549220"), ("RET", "0x4")),
    ),
    "0x004e65b0": target(
        "CSquad__VFunc02_RemoveFromGlobalLists",
        "void __fastcall CSquad__VFunc02_RemoveFromGlobalLists(void * this)",
        ("DAT_008550c0", "DAT_008550b0", "DAT_008550a0", "VFuncSlot_02_004f41b0"),
        {"global-list", "squad", "vfunc-slot-2"},
        ("void __fastcall CSquad__VFunc02_RemoveFromGlobalLists", "CSPtrSet__Remove", "VFuncSlot_02_004f41b0"),
        (("CALL", "0x004e5bd0"), ("CALL", "0x004f41b0"), ("RET", "")),
    ),
    "0x004e65e0": target(
        "CSquad__HandleEvent",
        "void __thiscall CSquad__HandleEvent(void * this, void * event)",
        ("RET 0x4", "0xfa2", "CComplexThing__HandleEvent", "vtable +0x108"),
        {"event", "squad", "vfunc-slot-0"},
        ("void __thiscall CSquad__HandleEvent", "CComplexThing__HandleEvent", "0xfa2"),
        (("CMP", "0xfa2"), ("CALL", "0x004f4300"), ("CALL", "[EDX + 0x108]"), ("RET", "0x4")),
    ),
    "0x004e6660": target(
        "CUnit__ResetDamageCooldownTimer",
        "void __fastcall CUnit__ResetDamageCooldownTimer(void * this)",
        ("this+0x88", "DAT_00672fd0", "0x005d85d8", "CUnit__ApplyDamage"),
        {"damage-cooldown", "unit"},
        ("void __fastcall CUnit__ResetDamageCooldownTimer", "DAT_00672fd0", "+ 0x88"),
        (("FLD", "[0x00672fd0]"), ("FADD", "[0x005d85d8]"), ("FSTP", "[ECX + 0x88]")),
    ),
    "0x004e6680": target(
        "CSquadNormal__IsFactionCompatible",
        "bool __thiscall CSquadNormal__IsFactionCompatible(void * this, int candidate_faction_state)",
        ("RET 0x4", "this+0x7c", "0/1/6 compatibility", "CSquadNormal__SelectBestEngagementTarget"),
        {"faction-compatibility", "predicate", "squad-normal"},
        ("bool __thiscall CSquadNormal__IsFactionCompatible", "candidate_faction_state", "+ 0x7c"),
        (("MOV", "[ESP + 0x4]"), ("CMP", "0x6"), ("RET", "0x4")),
    ),
    "0x004e66e0": target(
        "CUnit__RenderWithIdentityWorldAndShadowProbe",
        "void __fastcall CUnit__RenderWithIdentityWorldAndShadowProbe(void * this)",
        ("DAT_0083d148", "CDXEngine__SetWorldMatrixElements", "vtable slot +0x40", "CStaticShadows__SampleShadowHeightBilinear"),
        {"render", "static-shadows", "unit"},
        ("void __fastcall CUnit__RenderWithIdentityWorldAndShadowProbe", "CDXEngine__SetWorldMatrixElements", "CStaticShadows__SampleShadowHeightBilinear"),
        (("MOV", "0x83d148"), ("CALL", "0x00550ca0"), ("CALL", "[EAX + 0x40]"), ("CALL", "0x0047eb80")),
    ),
    "0x004e6870": target(
        "CSquadNormal__Constructor",
        "void * __thiscall CSquadNormal__Constructor(void * this)",
        ("CSquad__Constructor", "this+0xa4", "OID__AllocObject", "0x005df0f4", "0x005df07c"),
        {"constructor", "squad-normal", "vtable-backed"},
        ("void * __thiscall CSquadNormal__Constructor", "CSquad__Constructor", "CSPtrSet__Init", "OID__AllocObject"),
        (("CALL", "0x004e5da0"), ("CALL", "0x004e5840"), ("MOV", "0x5df0f4"), ("MOV", "0x5df07c")),
    ),
    "0x004e6ac0": target(
        "CSquadNormal__ScalarDeletingDestructor",
        "void * __thiscall CSquadNormal__ScalarDeletingDestructor(void * this, byte flags)",
        ("CSquadNormal scalar-deleting destructor wrapper", "CSquadNormal__Destructor", "flags bit 0", "RET 0x4"),
        {"scalar-deleting-destructor", "squad-normal"},
        ("void * __thiscall CSquadNormal__ScalarDeletingDestructor", "CSquadNormal__Destructor", "CDXMemoryManager__Free"),
        (("CALL", "0x004e6ae0"), ("CALL", "0x00549220"), ("RET", "0x4")),
    ),
    "0x004e6ae0": target(
        "CSquadNormal__Destructor",
        "void __fastcall CSquadNormal__Destructor(void * this)",
        ("this+0xec", "this+0xe4", "this+0xc8", "this+0xc4", "this+0xa4", "CComplexThing__dtor_base"),
        {"destructor", "member-set", "squad-normal"},
        ("void __fastcall CSquadNormal__Destructor", "CDXMemoryManager__Free", "CSPtrSet__Clear", "CComplexThing__dtor_base"),
        (("CALL", "0x00549220"), ("CALL", "0x004e5bd0"), ("CALL", "0x004e5c60"), ("CALL", "0x004f3f00")),
    ),
    "0x004e6bb0": target(
        "CSquadNormal__Init",
        "void __thiscall CSquadNormal__Init(void * this, void * init)",
        ("RET 0x4", "static-shadow height", "CSquad__VFunc_09_004e5e70", "DAT_008550c0", "DAT_008550b0", "vtable +0x108"),
        {"global-list", "init", "squad-normal", "static-shadows"},
        ("void __thiscall CSquadNormal__Init", "CStaticShadows__SampleShadowHeightBilinear", "CSquad__VFunc_09_004e5e70", "CSquadNormal__ScheduleTargetReaderRefresh"),
        (("CALL", "0x0047eb80"), ("CALL", "0x004e5e70"), ("CALL", "0x004e5b20"), ("CALL", "0x004e8100"), ("RET", "0x4")),
    ),
    "0x004e6f70": target(
        "CSquadNormal__RemoveMember",
        "void __thiscall CSquadNormal__RemoveMember(void * this, void * member)",
        ("RET 0x4", "member+0x148", "this+0xa4", "CSquadNormal__SetReaderAndUnregisterFromFactionSets", "this+0xb4"),
        {"member-set", "remove-member", "squad-normal"},
        ("void __thiscall CSquadNormal__RemoveMember", "CSPtrSet__Remove", "CGenericActiveReader__dtor", "CSquadNormal__SetReaderAndUnregisterFromFactionSets"),
        (("MOV", "[ESP + 0x8]"), ("CALL", "0x004e5bd0"), ("CALL", "0x0044b1d0"), ("CALL", "0x004fe500"), ("RET", "0x4")),
    ),
    "0x004e6ff0": target(
        "CSquadNormal__SyncFromLeaderUnit",
        "void __thiscall CSquadNormal__SyncFromLeaderUnit(void * this, void * leader_unit)",
        ("leader vtable slots +0x44 and +0x1bc", "CUnit__GetGridMapByType", "this+0xd0", "this+0x104", "this+0x10c", "leader flags at +0x34"),
        {"formation", "leader-sync", "squad-normal"},
        ("void __thiscall CSquadNormal__SyncFromLeaderUnit", "leader_unit", "CUnit__GetGridMapByType", "+ 0x1bc"),
        (("CALL", "[EAX + 0x44]"), ("CALL", "0x004fd380"), ("CALL", "[EDX + 0x1bc]"), ("RET", "0x4")),
    ),
    "0x004e7cf0": target(
        "CSquadNormal__UpdateFormationAdvanceScale",
        "bool __fastcall CSquadNormal__UpdateFormationAdvanceScale(void * this)",
        ("this+0x10c", "this+0x108", "this+0xa4", "grid occupancy", "this+0x11c"),
        {"formation", "member-set", "predicate", "squad-normal"},
        ("bool __fastcall CSquadNormal__UpdateFormationAdvanceScale", "+ 0x108", "+ 0xa4", "+ 0x11c"),
        (("MOV", "[EBP + 0x10c]"), ("CALL", "0x00401ec0"), ("CALL", "0x00401ee0"), ("RET", "0x4")),
    ),
    "0x004e7f40": target(
        "CSquadNormal__IsLeaderNearFormationCentroid",
        "bool __fastcall CSquadNormal__IsLeaderNearFormationCentroid(void * this)",
        ("this+0xa4", "squad position", "this+0x1c/0x20", "this+0x10c", "0x005d857c"),
        {"formation", "member-set", "predicate", "squad-normal"},
        ("bool __fastcall CSquadNormal__IsLeaderNearFormationCentroid", "+ 0xa4", "+ 0x10c"),
        (("MOV", "[ECX + 0xa4]"), ("FSQRT", ""), ("MOV", "0x1"), ("RET", "")),
    ),
    "0x004e8100": target(
        "CSquadNormal__ScheduleTargetReaderRefresh",
        "void __fastcall CSquadNormal__ScheduleTargetReaderRefresh(void * this)",
        ("CSquadNormal__SelectBestEngagementTarget", "CGenericActiveReader__SetReader", "event 4000", "Random__NextLCGAbs"),
        {"active-reader", "event-4000", "squad-normal", "target-selection"},
        ("void __fastcall CSquadNormal__ScheduleTargetReaderRefresh", "CSquadNormal__SelectBestEngagementTarget", "CGenericActiveReader__SetReader", "CEventManager__AddEvent_AtTime"),
        (("CALL", "0x00477cb0"), ("CALL", "0x00401000"), ("CALL", "0x0044b370"), ("RET", "")),
    ),
}

EXPECTED_XREFS = {
    ("0x004e43d0", "0x004fbfb6", "CUnit__UpdateDeployStateAndChargeEffects", "UNCONDITIONAL_CALL"),
    ("0x004e43d0", "0x004fb9b1", "CSquadNormal__SelectBestSupportOrEscort", "UNCONDITIONAL_CALL"),
    ("0x004e4480", "0x004fb963", "CSquadNormal__SelectBestSupportOrEscort", "UNCONDITIONAL_CALL"),
    ("0x004e4480", "0x004fdbac", "CUnit__TrySpawnMembersForTarget", "UNCONDITIONAL_CALL"),
    ("0x004e4d70", "0x005d95f0", "<no_function>", "DATA"),
    ("0x004e5da0", "0x004e6891", "CSquadNormal__Constructor", "UNCONDITIONAL_CALL"),
    ("0x004e5e50", "0x005def20", "<no_function>", "DATA"),
    ("0x004e65b0", "0x005def24", "<no_function>", "DATA"),
    ("0x004e65e0", "0x005def1c", "<no_function>", "DATA"),
    ("0x004e6660", "0x004f9add", "CUnit__ApplyDamage", "UNCONDITIONAL_CALL"),
    ("0x004e6680", "0x00477e03", "CSquadNormal__SelectBestEngagementTarget", "UNCONDITIONAL_CALL"),
    ("0x004e6870", "0x0050f5a7", "CWorldPhysicsManager__CreateSquad", "UNCONDITIONAL_CALL"),
    ("0x004e6bb0", "0x005df118", "<no_function>", "DATA"),
    ("0x004e7cf0", "0x004e7889", "CSquadNormal__Process", "UNCONDITIONAL_CALL"),
    ("0x004e8100", "0x004e6cb3", "CSquadNormal__Init", "UNCONDITIONAL_CALL"),
}

EXPECTED_VTABLE_SLOTS = {
    ("0x005d95e8", "2", "0x004e4d70", "CSphere__VFunc02_ResolveCollisionAsCylinder"),
    ("0x005def1c", "0", "0x004e65e0", "CSquad__HandleEvent"),
    ("0x005def1c", "1", "0x004e5e50", "SharedComplexThing__ScalarDeletingDestructor"),
    ("0x005def1c", "2", "0x004e65b0", "CSquad__VFunc02_RemoveFromGlobalLists"),
    ("0x005df0f4", "1", "0x004e6ac0", "CSquadNormal__ScalarDeletingDestructor"),
    ("0x005df0f4", "9", "0x004e6bb0", "CSquadNormal__Init"),
    ("0x005df0f4", "68", "0x004e6ff0", "CSquadNormal__SyncFromLeaderUnit"),
}

EXPECTED_LOG_SUMMARIES = {
    "apply_wave508_dry.log": "SUMMARY updated=0 skipped=20 renamed=0 would_rename=7 missing=0 bad=0",
    "apply_wave508_apply.log": "SUMMARY updated=20 skipped=0 renamed=7 would_rename=0 missing=0 bad=0",
    "apply_wave508_verify_dry.log": "SUMMARY updated=0 skipped=20 renamed=0 would_rename=0 missing=0 bad=0",
}

PUBLIC_NOTE_TOKENS = (
    "20",
    "7 renames",
    "CUnit__IsSupportTargetMaskCompatible",
    "CSphere__VFunc02_ResolveCollisionAsCylinder",
    "SharedComplexThing__ScalarDeletingDestructor",
    "CSquadNormal__ScheduleTargetReaderRefresh",
    "runtime AI behavior",
    "rebuild parity remain unproven",
)


def normalize_addr(address: str) -> str:
    address = (address or "").strip().lower()
    if not address or address.startswith("<"):
        return address
    if address.startswith("0x"):
        address = address[2:]
    return "0x" + address.zfill(8)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"Missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_text(path: Path) -> str:
    if not path.exists():
        raise AssertionError(f"Missing file: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def row_addr(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        if row.get(key):
            return normalize_addr(row[key])
    return ""


def check_metadata(base: Path) -> None:
    rows = {row_addr(row, "address"): row for row in read_tsv(base / "post_metadata.tsv")}
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
    rows = {row_addr(row, "address"): row for row in read_tsv(base / "post_tags.tsv")}
    missing = set(TARGETS) - set(rows)
    if missing:
        raise AssertionError(f"Missing tag rows: {sorted(missing)}")
    for address, spec in TARGETS.items():
        tags = {tag for tag in rows[address].get("tags", "").replace(",", ";").split(";") if tag}
        missing_tags = set(spec["tags"]) - tags  # type: ignore[arg-type]
        if missing_tags:
            raise AssertionError(f"{address} missing tags: {sorted(missing_tags)}")


def check_decompile(base: Path) -> None:
    decomp_dir = base / "post-decomp"
    for address, spec in TARGETS.items():
        name = str(spec["name"])
        path = decomp_dir / f"{address[2:]}_{name}.c"
        text = read_text(path)
        for token in spec["decompile_tokens"]:  # type: ignore[index]
            if token not in text:
                raise AssertionError(f"{address} decompile missing token {token!r}")


def check_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_target: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        target = row_addr(row, "target_addr", "target_raw")
        by_target.setdefault(target, []).append(row)
    for address, spec in TARGETS.items():
        target_rows = by_target.get(address, [])
        if not target_rows:
            raise AssertionError(f"{address} missing instruction rows")
        for mnemonic, operand_token in spec["instruction_tokens"]:  # type: ignore[index]
            if not any(
                row.get("mnemonic") == mnemonic and operand_token in row.get("operands", "")
                for row in target_rows
            ):
                raise AssertionError(f"{address} missing instruction token {mnemonic} {operand_token!r}")


def check_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    observed = {
        (
            row_addr(row, "target_addr"),
            row_addr(row, "from_addr"),
            row.get("from_function", ""),
            row.get("ref_type", ""),
        )
        for row in rows
    }
    missing = sorted(EXPECTED_XREFS - observed)
    if missing:
        raise AssertionError(f"Missing xrefs: {missing}")


def check_vtables(base: Path) -> None:
    rows = read_tsv(base / "post_vtables.tsv")
    observed = {
        (
            row_addr(row, "vtable"),
            row.get("slot_index", ""),
            row_addr(row, "function_entry"),
            row.get("function_name", ""),
        )
        for row in rows
    }
    missing = sorted(EXPECTED_VTABLE_SLOTS - observed)
    if missing:
        raise AssertionError(f"Missing vtable slots: {missing}")


def check_logs(base: Path) -> None:
    for name, summary in EXPECTED_LOG_SUMMARIES.items():
        text = read_text(base / name)
        if summary not in text:
            raise AssertionError(f"{name} missing summary {summary!r}")
        if "REPORT: Save succeeded" not in text:
            raise AssertionError(f"{name} missing save-succeeded report")


def check_public_note(path: Path) -> None:
    text = read_text(path)
    for token in PUBLIC_NOTE_TOKENS:
        if token not in text:
            raise AssertionError(f"Public note missing token {token!r}")
    forbidden = (
        "runtime proof",
        "runtime AI behavior proven",
        "rebuild parity proven",
        "fully RE'd",
        "fully re'ed",
    )
    lowered = text.lower()
    for token in forbidden:
        if token.lower() in lowered:
            raise AssertionError(f"Public note overclaims: {token}")


def validate(base: Path) -> None:
    check_metadata(base)
    check_tags(base)
    check_decompile(base)
    check_instructions(base)
    check_xrefs(base)
    check_vtables(base)
    check_logs(base)
    check_public_note(PUBLIC_NOTE)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        validate(args.base)
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        return 1

    print(f"PASS: Wave508 unit/squad support evidence verified under {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
