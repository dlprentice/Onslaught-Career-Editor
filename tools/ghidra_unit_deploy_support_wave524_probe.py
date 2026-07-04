#!/usr/bin/env python3
"""Validate Wave524 Unit deploy/support static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave524-unit-deploy-support-004fb780"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unit_deploy_support_wave524_2026-05-18.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "unit-deploy-support-wave524",
}

OVERCLAIM_TOKENS = (
    "runtime deploy behavior proven",
    "runtime squad ai behavior proven",
    "runtime particle behavior proven",
    "source identity proven",
    "exact enum names proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)


TARGETS = {
    "0x004fb780": {
        "name": "CSquadNormal__GetSupportMinEngageDistance",
        "signature": "float __thiscall CSquadNormal__GetSupportMinEngageDistance(void * this, void * ballistic_context, float aim_x, float aim_y, float aim_z)",
        "comment_tokens": ("RET 0x10", "CUnit__ComputeMinBallisticTravelDistance", "profile +0x2c", "remain unproven"),
        "tags": {"range-helper", "squad-support"},
        "decompile_tokens": ("ballistic_context", "aim_x", "CUnit__ComputeMinBallisticTravelDistance"),
    },
    "0x004fb7e0": {
        "name": "CSquadNormal__GetSupportMaxEngageDistance",
        "signature": "float __thiscall CSquadNormal__GetSupportMaxEngageDistance(void * this, void * ballistic_context, float aim_x, float aim_y, float aim_z)",
        "comment_tokens": ("RET 0x10", "CUnit__ComputeMaxBallisticTravelDistance", "profile +0x30", "remain unproven"),
        "tags": {"range-helper", "squad-support"},
        "decompile_tokens": ("ballistic_context", "aim_x", "CUnit__ComputeMaxBallisticTravelDistance"),
    },
    "0x004fb840": {
        "name": "CSquadNormal__SelectBestSupportOrEscort",
        "signature": "void __thiscall CSquadNormal__SelectBestSupportOrEscort(void * this, void * target_unit)",
        "comment_tokens": ("RET 0x4", "target_unit", "this+0x18c", "this+0x17c"),
        "tags": {"selection-helper", "squad-support"},
        "decompile_tokens": ("target_unit", "CUnit__IsSupportTargetMaskCompatible", "CUnit__ComputeMinBallisticTravelDistance"),
    },
    "0x004fbc90": {
        "name": "CWarspite__GetMountedUnitPitchOrZero",
        "signature": "float __thiscall CWarspite__GetMountedUnitPitchOrZero(void * this)",
        "comment_tokens": ("ECX-only", "this+0x140", "CWarspite__Update", "remain unproven"),
        "tags": {"support-profile", "warspite-context"},
        "decompile_tokens": ("this", "0xa0", "0x88"),
    },
    "0x004fbcb0": {
        "name": "CUnit__UpdateDeployStateAndChargeEffects",
        "signature": "int __thiscall CUnit__UpdateDeployStateAndChargeEffects(void * this)",
        "comment_tokens": ("ECX-only", "+0x168/+0x16c/+0x1e8/+0x1ec", "deploying", "remain unproven"),
        "tags": {"support-profile", "unit-deploy"},
        "decompile_tokens": ("0x168", "0x1e8", "deploying", "CParticleManager__CreateEffect"),
    },
    "0x004fc000": {
        "name": "CUnit__CanDeployNow",
        "signature": "int __thiscall CUnit__CanDeployNow(void * this)",
        "comment_tokens": ("ECX-only", "profile flag +0x110", "CUnit__IsEligibleByDistanceBucketOrRange", "remain unproven"),
        "tags": {"support-profile", "unit-deploy"},
        "decompile_tokens": ("CUnit__IsInBlockedSupportState", "CUnit__IsEligibleByDistanceBucketOrRange"),
    },
    "0x004fc080": {
        "name": "CUnitAI__TrySpawnOrFinalizeAttachedUnit",
        "signature": "int __thiscall CUnitAI__TrySpawnOrFinalizeAttachedUnit(void * this)",
        "comment_tokens": ("ECX-only", "CSpawnerThng__DoSpawn", "projectile burst fallback", "remain unproven"),
        "tags": {"spawn-helper", "support-profile", "unit-ai"},
        "decompile_tokens": ("CSpawnerThng__DoSpawn", "ProjectileBurst__SpawnFromPercentBucketFallback"),
    },
    "0x004fc170": {
        "name": "CUnitAI__FinalizeSpawnAndAdvanceState",
        "signature": "void __thiscall CUnitAI__FinalizeSpawnAndAdvanceState(void * this)",
        "comment_tokens": ("ECX-only", "recursively spawns component effects", "+0x8c", "remain unproven"),
        "tags": {"spawn-helper", "support-profile", "unit-ai"},
        "decompile_tokens": ("CUnit__SpawnComponentEffectsRecursive", "0x8c"),
    },
    "0x004fc220": {
        "name": "CUnit__SpawnComponentEffectsRecursive",
        "signature": "void __thiscall CUnit__SpawnComponentEffectsRecursive(void * this)",
        "comment_tokens": ("ECX-only", "recursive component-effect", "+0x1c4", "+0x19c"),
        "tags": {"recursive-helper", "unit-effects"},
        "decompile_tokens": ("CParticleManager__CreateEffect", "CMeshRenderer__CopyBasisAndRefreshTime", "CUnit__SpawnComponentEffectsRecursive"),
    },
    "0x004fc4e0": {
        "name": "CUnit__UpdateTransform",
        "signature": "void __thiscall CUnit__UpdateTransform(void * this, int emitter_slot_tag, int cache_key, void * out_position4, void * out_basis3x4)",
        "comment_tokens": ("RET 0x10", "cached emitter transform", "CUnit__FindEmitterIndexBySlotTag", "older docs"),
        "tags": {"unit-emitter-transform"},
        "decompile_tokens": ("emitter_slot_tag", "cache_key", "out_position4", "out_basis3x4"),
    },
    "0x004fc6e0": {
        "name": "CUnit__FindEmitterIndexBySlotTag",
        "signature": "int __thiscall CUnit__FindEmitterIndexBySlotTag(void * this, int emitter_slot_tag, int cache_key, void * out_position4, void * out_basis3x4, int flag_a, int flag_b)",
        "comment_tokens": ("RET 0x18", "SpawnerA-E", "WaypointA-E", "Charge"),
        "tags": {"slot-map", "unit-emitter-transform"},
        "decompile_tokens": ("SpawnerA", "WaypointA", "Component", "Engine", "Charge"),
    },
}

EXPECTED_XREFS = {
    ("0x004fb780", "0x00477eed", "CSquadNormal__SelectBestEngagementTarget", "UNCONDITIONAL_CALL"),
    ("0x004fb7e0", "0x004e8319", "CSquadNormal__EvaluateLeaderTargetPursuitMode", "UNCONDITIONAL_CALL"),
    ("0x004fb840", "0x0047aff6", "CGillMHeadAI__UpdateAimTransformAndTargetReader", "UNCONDITIONAL_CALL"),
    ("0x004fb840", "0x004ffde5", "CSquadNormal__SetReaderAndRefreshSupportSelection", "UNCONDITIONAL_CALL"),
    ("0x004fbc90", "0x004ff275", "CWarspite__Update", "UNCONDITIONAL_CALL"),
    ("0x004fbcb0", "0x0047a8d7", "CGillMHeadAI__TryTransitionIdleToOpen", "UNCONDITIONAL_CALL"),
    ("0x004fc080", "0x00489062", "CUnitAI__TryPlayActivateAnimation", "UNCONDITIONAL_CALL"),
    ("0x004fc170", "0x0047d424", "CUnitAI__QueueFiringOrPostfireAnimation", "UNCONDITIONAL_CALL"),
    ("0x004fc220", "0x004fc1b5", "CUnitAI__FinalizeSpawnAndAdvanceState", "UNCONDITIONAL_CALL"),
    ("0x004fc4e0", "0x00428338", "CUnitAI__UpdateActivationStateAndSpawnPickup", "UNCONDITIONAL_CALL"),
    ("0x004fc6e0", "0x004fc573", "CUnit__UpdateTransform", "UNCONDITIONAL_CALL"),
}

EXPECTED_RETS = {
    ("0x004fb7b1", "RET", "0x10", "CSquadNormal__GetSupportMinEngageDistance"),
    ("0x004fb811", "RET", "0x10", "CSquadNormal__GetSupportMaxEngageDistance"),
    ("0x004fbc88", "RET", "0x4", "CSquadNormal__SelectBestSupportOrEscort"),
    ("0x004fbca6", "RET", "", "CWarspite__GetMountedUnitPitchOrZero"),
    ("0x004fbd13", "RET", "", "CUnit__UpdateDeployStateAndChargeEffects"),
    ("0x004fc026", "RET", "", "CUnit__CanDeployNow"),
    ("0x004fc0d7", "RET", "", "CUnitAI__TrySpawnOrFinalizeAttachedUnit"),
    ("0x004fc204", "RET", "", "CUnitAI__FinalizeSpawnAndAdvanceState"),
    ("0x004fc39f", "RET", "", "CUnit__SpawnComponentEffectsRecursive"),
    ("0x004fc6b6", "RET", "0x10", "CUnit__UpdateTransform"),
    ("0x004fc71b", "RET", "0x18", "CUnit__FindEmitterIndexBySlotTag"),
}

EXPECTED_CONTEXT_TOKENS = {
    "0x004ffdd0": ("CSquadNormal__SelectBestSupportOrEscort",),
    "0x004fef40": (
        "CSquadNormal__SelectBestSupportOrEscort",
        "CWarspite__GetMountedUnitPitchOrZero",
        "CUnit__ForwardAimTransformAndAttachTargetReader",
    ),
    "0x00489040": ("CUnitAI__TrySpawnOrFinalizeAttachedUnit",),
    "0x00428110": ("CUnit__UpdateTransform",),
}

PUBLIC_NOTE_TOKENS = (
    "Wave524",
    "CSquadNormal__SelectBestSupportOrEscort",
    "RET 0x4",
    "203 target xref rows",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260518-005140_post_wave524_unit_deploy_support_corrected_verified",
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
    require(len(rows) == 203, f"expected 203 xref rows, got {len(rows)}")
    actual = {
        (row["target_addr"], row["from_addr"], row["from_function"], row["ref_type"])
        for row in rows
    }
    for expected in EXPECTED_XREFS:
        normalized = (normalize_addr(expected[0]), normalize_addr(expected[1]), expected[2], expected[3])
        require(normalized in actual, f"missing xref {expected}")


def check_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    require(len(rows) == 2651, f"expected 2651 instruction rows, got {len(rows)}")
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
        text = path.read_text(encoding="utf-8")
        for token in expected["decompile_tokens"]:
            require(token_present(text, token), f"{address} decompile missing token {token!r}")


def check_context(base: Path) -> None:
    metadata_rows = read_tsv(base / "post_context_metadata.tsv")
    require(len(metadata_rows) == 12, f"expected 12 context metadata rows, got {len(metadata_rows)}")
    index_rows = read_tsv(base / "post_context_decomp" / "index.tsv")
    require(len(index_rows) == 12, f"expected 12 context decompile rows, got {len(index_rows)}")
    for address, tokens in EXPECTED_CONTEXT_TOKENS.items():
        row = row_by_address(index_rows, address)
        require(row["status"] == "OK", f"{address} context decompile status is {row['status']}")
        candidates = sorted((base / "post_context_decomp").glob(f"{normalize_addr(address)[2:]}_*.c"))
        require(bool(candidates), f"missing context decompile file for {address}")
        text = candidates[0].read_text(encoding="utf-8")
        for token in tokens:
            require(token_present(text, token), f"{address} context decompile missing token {token!r}")


def check_public_note() -> None:
    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    text = PUBLIC_NOTE.read_text(encoding="utf-8")
    for token in PUBLIC_NOTE_TOKENS:
        require(token_present(text, token), f"public note missing token {token!r}")
    for token in OVERCLAIM_TOKENS:
        require(not token_present(text, token), f"public note overclaims with {token!r}")


def run_checks(base: Path) -> None:
    check_metadata(base)
    check_tags(base)
    check_xrefs(base)
    check_instructions(base)
    check_decomp(base)
    check_context(base)
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
    print("Wave524 unit deploy/support probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
