#!/usr/bin/env python3
"""Validate Wave526 Unit core-tail/static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave526-unit-core-tail-004f84c0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unit_core_tail_wave526_2026-05-18.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "unit-core-tail-wave526",
}

OVERCLAIM_TOKENS = (
    "runtime unit behavior proven",
    "runtime motion/effect behavior proven",
    "runtime cleanup behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)

TARGETS = {
    "0x004f84c0": {
        "name": "CUnit__VFunc01_ScalarDeletingDtor",
        "signature": "void * __thiscall CUnit__VFunc01_ScalarDeletingDtor(void * this, byte flags)",
        "comment_tokens": ("RET 0x4", "CUnit__dtor_base", "flags bit 0", "remain unproven"),
        "tags": {"scalar-deleting-dtor", "unit-lifecycle", "vfunc-slot-01"},
        "decompile_tokens": ("CUnit__dtor_base", "CDXMemoryManager__Free", "flags"),
    },
    "0x004f86d0": {
        "name": "CUnit__Init",
        "signature": "void __thiscall CUnit__Init(void * this, void * init)",
        "comment_tokens": ("RET 0x4", "this+0x164", "CActor__Init", "remain unproven"),
        "tags": {"event-scheduler", "profile-driven", "unit-init"},
        "decompile_tokens": ("CActor__Init", "CWorldPhysicsManager__CreateWeaponByIndex", "CUnit__UpdateFireControlYawAndQueueEvent"),
    },
    "0x004f9430": {
        "name": "CUnit__ApplyRandomDestructibleDamageBurst",
        "signature": "void __fastcall CUnit__ApplyRandomDestructibleDamageBurst(void * this)",
        "comment_tokens": ("this+0x178", "this+0xf8", "LCG-derived", "remain unproven"),
        "tags": {"destructible-segment", "randomized", "unit-damage"},
        "decompile_tokens": ("CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold", "Random__NextLCGAbs", "0xf8"),
    },
    "0x004f9490": {
        "name": "CUnit__SpawnConfiguredPickupIfAboveWater",
        "signature": "void __fastcall CUnit__SpawnConfiguredPickupIfAboveWater(void * this)",
        "comment_tokens": ("CreatePickup", "profile field +0xec", "DAT_006fbdfc", "remain unproven"),
        "tags": {"owner-corrected", "profile-driven", "unit-pickup"},
        "decompile_tokens": ("CWorldPhysicsManager__CreatePickup", "DAT_006fbdfc", "0xec"),
    },
    "0x004f95d0": {
        "name": "CUnit__VFunc02_CleanupWorldLinksAndForward",
        "signature": "void __fastcall CUnit__VFunc02_CleanupWorldLinksAndForward(void * this)",
        "comment_tokens": ("kills sound samples", "+0x17c/+0x18c/+0x19c", "CComplexThing__Shutdown", "remain unproven"),
        "tags": {"active-reader", "particle-effect", "unit-lifecycle", "vfunc-slot-02"},
        "decompile_tokens": ("CSoundManager__KillSamplesForThing", "ParticleEffectLink__SetHandleStateAndClear", "CComplexThing__Shutdown"),
    },
    "0x004f9820": {
        "name": "CUnit__HandleEvent",
        "signature": "void __thiscall CUnit__HandleEvent(void * this, void * event)",
        "comment_tokens": ("RET 0x4", "0xfa1", "0xfa5", "remain unproven"),
        "tags": {"event-scheduler", "unit-event", "vfunc-slot-00"},
        "decompile_tokens": ("CActor__HandleEvent", "CEventManager__AddEvent_TimeFromNow", "0xfa3"),
    },
    "0x004f99b0": {
        "name": "CUnit__PlayRespawnVoiceCueIfAvailable",
        "signature": "void __fastcall CUnit__PlayRespawnVoiceCueIfAvailable(void * this)",
        "comment_tokens": ("profile pointer this+0x164", "profile+0x34", "CSoundManager__PlayEffect", "remain unproven"),
        "tags": {"owner-corrected", "profile-driven", "unit-audio"},
        "decompile_tokens": ("CSoundManager__PlayEffect", "0x34", "0x164"),
    },
    "0x004f99f0": {
        "name": "CUnit__GetCurrentHealthOrSubtreeHealth",
        "signature": "double __fastcall CUnit__GetCurrentHealthOrSubtreeHealth(void * this)",
        "comment_tokens": ("this+0x178", "this+0xf8", "HUD/compass", "remain unproven"),
        "tags": {"destructible-segment", "owner-corrected", "query", "unit-health"},
        "decompile_tokens": ("CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive", "0xf8", "0x178"),
    },
    "0x004f9a40": {
        "name": "CUnit__GetRootSubtreeHealthIfAnyActive",
        "signature": "double __fastcall CUnit__GetRootSubtreeHealthIfAnyActive(void * this)",
        "comment_tokens": ("this+0x178", "root-subtree health", "this+0xf8", "remain unproven"),
        "tags": {"destructible-segment", "owner-corrected", "query", "unit-health"},
        "decompile_tokens": ("CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive", "0xf8", "0x178"),
    },
    "0x004f9a60": {
        "name": "CUnit__RemoveLinkedObjectFromSpawnerSet",
        "signature": "void __thiscall CUnit__RemoveLinkedObjectFromSpawnerSet(void * this, void * linked_object)",
        "comment_tokens": ("RET 0x4", "this+0x18c", "vfunc +0x4", "remain unproven"),
        "tags": {"destructible-segment", "owner-corrected", "unit-spawner-set"},
        "decompile_tokens": ("linked_object", "CSPtrSet__Remove", "0x18c"),
    },
    "0x004fa800": {
        "name": "CUnit__UpdateClosingAndUnshuttingState",
        "signature": "void __fastcall CUnit__UpdateClosingAndUnshuttingState(void * this)",
        "comment_tokens": ("this+0x168", "DAT_00672fd0", "this+0x1e8", "remain unproven"),
        "tags": {"motion-update", "transform", "unit-state"},
        "decompile_tokens": ("DAT_00672fd0", "0x168", "0x1e8"),
    },
    "0x004fa8d0": {
        "name": "CUnit__UpdateMotionAttachmentsAndEffects",
        "signature": "void __fastcall CUnit__UpdateMotionAttachmentsAndEffects(void * this)",
        "comment_tokens": ("CUnit__UpdateClosingAndUnshuttingState", "CActor__Move", "support-loop audio", "remain unproven"),
        "tags": {"audio-loop", "deploy-animation", "particle-effect", "unit-motion"},
        "decompile_tokens": ("CUnit__UpdateClosingAndUnshuttingState", "CActor__Move", "CThing__UpdatePosition"),
    },
}

EXPECTED_XREFS = {
    ("0x004f86d0", "0x00402af9", "CAirUnit__Init", "UNCONDITIONAL_CALL"),
    ("0x004f86d0", "0x004054c6", "CBattleEngine__Init", "UNCONDITIONAL_CALL"),
    ("0x004f9490", "0x004ef10b", "CUnit__RunTransitionStepThreeTimes", "UNCONDITIONAL_CALL"),
    ("0x004f95d0", "0x0041b460", "CCannon__VFuncSlot_02_RemoveFromWorldAndForward", "UNCONDITIONAL_CALL"),
    ("0x004f95d0", "0x004ba4c3", "CMine__VFunc02_CleanupLinkedParticleAndForward", "UNCONDITIONAL_CALL"),
    ("0x004f9820", "0x005df998", "<no_function>", "DATA"),
    ("0x004f99b0", "0x0046e086", "CGame__RestartLoopRunLevel", "UNCONDITIONAL_CALL"),
    ("0x004f99f0", "0x0042768e", "CDXCompass__Render", "UNCONDITIONAL_CALL"),
    ("0x004f9a60", "0x00442ced", "CDestroyableSegment__VFunc_08_HandleSegmentBreak", "UNCONDITIONAL_CALL"),
    ("0x004fa800", "0x004fa914", "CUnit__UpdateMotionAttachmentsAndEffects", "UNCONDITIONAL_CALL"),
    ("0x004fa8d0", "0x004d3633", "CPod__VFunc_66_UpdateMotionAndAccumulateScalar", "UNCONDITIONAL_CALL"),
}

EXPECTED_RETS = {
    ("0x004f84dd", "RET", "0x4", "CUnit__VFunc01_ScalarDeletingDtor"),
    ("0x004f91ef", "RET", "0x4", "CUnit__Init"),
    ("0x004f9813", "RET", "", "CUnit__VFunc02_CleanupWorldLinksAndForward"),
    ("0x004f9851", "RET", "0x4", "CUnit__HandleEvent"),
    ("0x004f9985", "RET", "0x4", "CUnit__HandleEvent"),
    ("0x004f99ea", "RET", "", "CUnit__PlayRespawnVoiceCueIfAvailable"),
    ("0x004f9a07", "RET", "", "CUnit__GetCurrentHealthOrSubtreeHealth"),
    ("0x004f9a52", "RET", "", "CUnit__GetRootSubtreeHealthIfAnyActive"),
    ("0x004f9a7f", "RET", "0x4", "CUnit__RemoveLinkedObjectFromSpawnerSet"),
    ("0x004fa8c6", "RET", "", "CUnit__UpdateClosingAndUnshuttingState"),
}

PUBLIC_NOTE_TOKENS = (
    "Wave526",
    "CUnit__Init",
    "CUnit__HandleEvent",
    "120 target xref rows",
    "runtime motion/effect behavior",
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
        require("ApplyUnitCoreTailWave526.java> REPORT: Save succeeded" in text, f"{path.name}: missing script save report")
    for bad in ("LockException", "MISSING:", "BADNAME:", "BADADDR:", "FAIL:"):
        require(bad not in text, f"{path.name}: contains {bad}")


def check_logs(base: Path) -> None:
    check_log(
        base / "apply_unit_core_tail_wave526_dry.log",
        "SUMMARY updated=0 skipped=12 renamed=0 would_rename=8 missing=0 bad=0",
        False,
    )
    check_log(
        base / "apply_unit_core_tail_wave526_apply.log",
        "SUMMARY updated=12 skipped=0 renamed=8 would_rename=0 missing=0 bad=0",
        True,
    )
    check_log(
        base / "apply_unit_core_tail_wave526_verify_dry.log",
        "SUMMARY updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0",
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
        tags = set(filter(None, row.get("tags", "").split(";")))
        missing = (COMMON_TAGS | set(expected["tags"])) - tags
        require(not missing, f"{address} tags missing {sorted(missing)}")


def check_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    require(len(rows) == 120, f"expected 120 xref rows, got {len(rows)}")
    actual = {
        (row["target_addr"], row["from_addr"], row["from_function"], row["ref_type"])
        for row in rows
    }
    for expected in EXPECTED_XREFS:
        normalized = (normalize_addr(expected[0]), normalize_addr(expected[1]), expected[2], expected[3])
        require(normalized in actual, f"missing xref {expected}")


def check_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    require(len(rows) == 5052, f"expected 5052 instruction rows, got {len(rows)}")
    init_rows = read_tsv(base / "post_instructions_init_full.tsv")
    require(len(init_rows) == 3601, f"expected 3601 init instruction rows, got {len(init_rows)}")
    actual = {
        (row["instruction_addr"], row["mnemonic"], row["operands"], row["function_name"])
        for row in rows + init_rows
    }
    for expected in EXPECTED_RETS:
        normalized = (normalize_addr(expected[0]), expected[1], expected[2], expected[3])
        require(normalized in actual, f"missing instruction {expected}")


def check_decomp(base: Path) -> None:
    index_rows = read_tsv(base / "post_decomp" / "index.tsv")
    require(len(index_rows) == len(TARGETS), f"expected {len(TARGETS)} decompile rows, got {len(index_rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(index_rows, address)
        require(row["status"] == "OK", f"{address} decompile status is {row['status']}")
        path = find_decomp_file(base / "post_decomp", address, expected["name"])
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in expected["decompile_tokens"]:
            require(token_present(text, token), f"{address} decompile missing token {token!r}")


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true", help="run checks and print PASS")
    args = parser.parse_args()

    try:
        run_checks(args.base)
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("Wave526 unit core tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
