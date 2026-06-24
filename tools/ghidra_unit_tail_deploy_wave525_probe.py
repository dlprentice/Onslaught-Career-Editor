#!/usr/bin/env python3
"""Validate Wave525 Unit tail deploy/static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave525-unit-tail-deploy-004fcdc0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unit_tail_deploy_wave525_2026-05-18.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "unit-tail-deploy-wave525",
}

OVERCLAIM_TOKENS = (
    "runtime deploy behavior proven",
    "runtime animation behavior proven",
    "runtime collision behavior proven",
    "source identity proven",
    "exact state enum names proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)


TARGETS = {
    "0x004fcdc0": {
        "name": "CUnit__SetCollisionAndDamageFlags",
        "signature": "void __thiscall CUnit__SetCollisionAndDamageFlags(void * this, int base_flags)",
        "comment_tokens": ("RET 0x4", "base_flags | 0x80200013", "base_flags | 0x80000013", "remain unproven"),
        "tags": {"damage-collision", "unit-flags"},
        "decompile_tokens": ("base_flags", "0x80200013", "0x80000013"),
    },
    "0x004fcf00": {
        "name": "CUnit__ResetKinematicsAndNotifyController",
        "signature": "void __fastcall CUnit__ResetKinematicsAndNotifyController(void * this)",
        "comment_tokens": ("+0x14c", "+0x7c", "this+0x208", "remain unproven"),
        "tags": {"controller-forwarder", "unit-kinematics"},
        "decompile_tokens": ("this", "0x14c", "0x208"),
    },
    "0x004fcfa0": {
        "name": "CUnit__ClearSpawnerSet",
        "signature": "void __fastcall CUnit__ClearSpawnerSet(void * this)",
        "comment_tokens": ("+0x144", "+0x18c", "vfunc +0x8", "remain unproven"),
        "tags": {"active-reader", "unit-spawner-set"},
        "decompile_tokens": ("CGenericActiveReader__SetReader", "CSPtrSet__Remove", "0x18c"),
    },
    "0x004fcfe0": {
        "name": "CUnit__ReleaseChildUnits",
        "signature": "void __fastcall CUnit__ReleaseChildUnits(void * this)",
        "comment_tokens": ("+0x19c", "this+0x2c", "active reader", "remain unproven"),
        "tags": {"active-reader", "lifecycle", "unit-child-units"},
        "decompile_tokens": ("0x19c", "CGenericActiveReader__dtor", "CDXMemoryManager__Free"),
    },
    "0x004fd040": {
        "name": "CUnit__ResetDeploymentGraphAndScheduleEvent",
        "signature": "void __fastcall CUnit__ResetDeploymentGraphAndScheduleEvent(void * this)",
        "comment_tokens": ("event 2000", "DAT_00672fd0", "script event id 3", "remain unproven"),
        "tags": {"active-reader", "event-scheduler", "unit-deploy"},
        "decompile_tokens": ("CEventManager__AddEvent_AtTime", "DAT_00672fd0", "IScript__CallEventId3_OrReset"),
    },
    "0x004fd140": {
        "name": "CUnit__MarkDestroyedAndCleanupLinks",
        "signature": "int __fastcall CUnit__MarkDestroyedAndCleanupLinks(void * this)",
        "comment_tokens": ("destroyed flag bit 2", "kills sounds for this", "script event id 5", "remain unproven"),
        "tags": {"active-reader", "counter-update", "unit-destruction"},
        "decompile_tokens": ("CSoundManager__KillSamplesForThing", "CDestructableSegmentsController__TriggerCoreCascadeIfEligible", "IScript__CallEventId5_OrReset"),
    },
    "0x004fd380": {
        "name": "CUnit__GetGridMapByType",
        "signature": "void * __fastcall CUnit__GetGridMapByType(void * this)",
        "comment_tokens": ("+0xfc", "DAT_00855290", "DAT_00855298", "remain unproven"),
        "tags": {"query", "unit-grid-map"},
        "decompile_tokens": ("DAT_00855290", "DAT_00855294", "DAT_00855298"),
    },
    "0x004fd5b0": {
        "name": "CUnit__IsActiveAndNotInState12",
        "signature": "bool __stdcall CUnit__IsActiveAndNotInState12(void * unit)",
        "comment_tokens": ("RET 0x4", "+0x244", "neither 1 nor 2", "remain unproven"),
        "tags": {"predicate", "unit-state"},
        "decompile_tokens": ("unit", "0x244", "return true"),
    },
    "0x004fd7a0": {
        "name": "CUnit__HasAnyReadySpawner",
        "signature": "bool __fastcall CUnit__HasAnyReadySpawner(void * this)",
        "comment_tokens": ("+0x18c", "CUnit__IsInBlockedSupportState", "saved name predates", "remain unproven"),
        "tags": {"predicate", "unit-spawner-set"},
        "decompile_tokens": ("CUnit__IsInBlockedSupportState", "return true", "return false"),
    },
    "0x004fd7e0": {
        "name": "CUnitAI__AreSpawnedChildrenReady",
        "signature": "bool __fastcall CUnitAI__AreSpawnedChildrenReady(void * this)",
        "comment_tokens": ("CSpawnerThng__IsSpawnComplete", "CUnit__IsInBlockedSupportState", "returns false", "remain unproven"),
        "tags": {"predicate", "spawn-helper", "unit-ai"},
        "decompile_tokens": ("CSpawnerThng__IsSpawnComplete", "CUnit__IsInBlockedSupportState", "return true"),
    },
    "0x004fde10": {
        "name": "CUnitAI__IsDeployAnimationState",
        "signature": "bool __fastcall CUnitAI__IsDeployAnimationState(void * this)",
        "comment_tokens": ("+0x244", "3, 4, or 5", "remain unproven"),
        "tags": {"deploy-animation", "predicate", "unit-ai"},
        "decompile_tokens": ("0x244", "return true", "return false"),
    },
    "0x004fde30": {
        "name": "CUnit__BeginDeployAnimationIfIdle",
        "signature": "void __fastcall CUnit__BeginDeployAnimationIfIdle(void * this)",
        "comment_tokens": ("+0x244 is 0", "deploying", "vfunc +0xf0", "remain unproven"),
        "tags": {"deploy-animation", "unit-deploy"},
        "decompile_tokens": ("s_deploying_006239cc", "CMesh__FindAnimationIndexByName", "0xf0"),
    },
    "0x004fdeb0": {
        "name": "CUnitAI__HandleDeployAndFireAnimationCompletion",
        "signature": "int __fastcall CUnitAI__HandleDeployAndFireAnimationCompletion(void * this)",
        "comment_tokens": ("deploying", "undeploying", "prefire", "CComplexThing__FinishedPlayingCurrentAnimation"),
        "tags": {"deploy-animation", "fire-animation", "unit-ai"},
        "decompile_tokens": ("s_deploying_006239cc", "s_prefirehold_00633c70", "CComplexThing__FinishedPlayingCurrentAnimation"),
    },
}

EXPECTED_XREFS = {
    ("0x004fcfe0", "0x00428850", "CUnitAI__HandleTriggerEventAndMoveToOffset", "UNCONDITIONAL_CALL"),
    ("0x004fd040", "0x0041b5a0", "CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph", "UNCONDITIONAL_CALL"),
    ("0x004fd140", "0x004d38c3", "CUnit__TryDestroyedCleanupAndResetDeploymentGraph", "UNCONDITIONAL_CALL"),
    ("0x004fd380", "0x004e409f", "CSpawnerThng__ProcessSpawnWave", "UNCONDITIONAL_CALL"),
    ("0x004fd7e0", "0x004480d6", "CUnitAI__CanContinueDoorWingTransition", "UNCONDITIONAL_CALL"),
    ("0x004fde10", "0x0047cdfc", "CGroundUnit__UpdateLinkedEffectsByHeightClearance", "UNCONDITIONAL_CALL"),
    ("0x004fdeb0", "0x00415a30", "CUnitAI__HandleDeployUndeployAnimationCompletion", "UNCONDITIONAL_CALL"),
}

EXPECTED_RETS = {
    ("0x004fcde5", "RET", "0x4", "CUnit__SetCollisionAndDamageFlags"),
    ("0x004fcf90", "RET", "", "CUnit__ResetKinematicsAndNotifyController"),
    ("0x004fcfd6", "RET", "", "CUnit__ClearSpawnerSet"),
    ("0x004fd031", "RET", "", "CUnit__ReleaseChildUnits"),
    ("0x004fd139", "RET", "", "CUnit__ResetDeploymentGraphAndScheduleEvent"),
    ("0x004fd14c", "RET", "", "CUnit__MarkDestroyedAndCleanupLinks"),
    ("0x004fd3a1", "RET", "", "CUnit__GetGridMapByType"),
    ("0x004fd5d3", "RET", "0x4", "CUnit__IsActiveAndNotInState12"),
    ("0x004fd7d4", "RET", "", "CUnit__HasAnyReadySpawner"),
    ("0x004fd826", "RET", "", "CUnitAI__AreSpawnedChildrenReady"),
    ("0x004fde27", "RET", "", "CUnitAI__IsDeployAnimationState"),
    ("0x004fde6d", "RET", "", "CUnit__BeginDeployAnimationIfIdle"),
    ("0x004fe02d", "RET", "", "CUnitAI__HandleDeployAndFireAnimationCompletion"),
}

PUBLIC_NOTE_TOKENS = (
    "Wave525",
    "CUnit__SetCollisionAndDamageFlags",
    "CUnitAI__HandleDeployAndFireAnimationCompletion",
    "116 target xref rows",
    "runtime deploy behavior",
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
        require("ApplyUnitTailDeployWave525.java> REPORT: Save succeeded" in text, f"{path.name}: missing script save report")
    for bad in ("LockException", "MISSING:", "BADNAME:", "BADADDR:", "FAIL:"):
        require(bad not in text, f"{path.name}: contains {bad}")


def check_logs(base: Path) -> None:
    check_log(
        base / "apply_unit_tail_deploy_wave525_dry.log",
        "SUMMARY updated=0 skipped=13 missing=0 bad=0",
        False,
    )
    check_log(
        base / "apply_unit_tail_deploy_wave525_apply.log",
        "SUMMARY updated=13 skipped=0 missing=0 bad=0",
        True,
    )
    check_log(
        base / "apply_unit_tail_deploy_wave525_verify_dry.log",
        "SUMMARY updated=0 skipped=13 missing=0 bad=0",
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
        wanted = COMMON_TAGS | set(expected["tags"])
        missing = wanted - tags
        require(not missing, f"{address} tags missing {sorted(missing)}")


def check_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    require(len(rows) == 116, f"expected 116 xref rows, got {len(rows)}")
    actual = {
        (row["target_addr"], row["from_addr"], row["from_function"], row["ref_type"])
        for row in rows
    }
    for expected in EXPECTED_XREFS:
        normalized = (normalize_addr(expected[0]), normalize_addr(expected[1]), expected[2], expected[3])
        require(normalized in actual, f"missing xref {expected}")


def check_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    require(len(rows) == 3133, f"expected 3133 instruction rows, got {len(rows)}")
    actual = {
        (row["instruction_addr"], row["mnemonic"], row["operands"], row["function_name"])
        for row in rows
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
    print("Wave525 unit tail deploy probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
