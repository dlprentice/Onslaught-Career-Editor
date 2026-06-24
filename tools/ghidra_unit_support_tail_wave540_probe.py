#!/usr/bin/env python3
"""Validate Wave540 Unit support-tail Ghidra read-back."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave540-unit-support-tail-004fd230"
COMMON_TAGS = {
    "static-reaudit",
    "unit-support-tail-wave540",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004fd230": target(
        "CUnit__SpawnProfileDropPickup",
        "void __fastcall CUnit__SpawnProfileDropPickup(void * this)",
        ["profile +0xe8", "CWorldPhysicsManager__CreatePickup", "this+0x138", "this+0x1c..0x28"],
        ["unit-pickup", "profile-driven", "owner-corrected", "renamed"],
        ["CWorldPhysicsManager__CreatePickup", "CInitThing__ctor", "HeightDelta__Below025_D0", "this + 0x164"],
    ),
    "0x004fd3d0": target(
        "CUnit__IsCandidateSideCompatibleForTargeting",
        "bool __thiscall CUnit__IsCandidateSideCompatibleForTargeting(void * this, int candidate_side)",
        ["RET 0x4", "candidate_side", "this+0x138", "this+0x164->0x128"],
        ["unit-targeting", "side-team-filter", "owner-corrected", "renamed"],
        ["candidate_side == 0", "candidate_side == 1", "candidate_side != 6", "return true"],
    ),
    "0x004fd500": target(
        "CUnit__ApplyRenderPositionDeltaToVector",
        "void __thiscall CUnit__ApplyRenderPositionDeltaToVector(void * this, void * inout_position)",
        ["RET 0x4", "inout_position", "CActor__GetRenderPos", "vfunc +0x78"],
        ["unit-render-position", "hud-target-marker", "owner-corrected", "renamed"],
        ["CActor__GetRenderPos", "inout_position", "*(int *)this + 0x168", "*(int *)this + 0x78"],
    ),
    "0x004fd570": target(
        "CSquadNormal__HasAnyLinkedUnitWithField94",
        "bool __fastcall CSquadNormal__HasAnyLinkedUnitWithField94(void * this)",
        ["this+0x17c", "+0x94", "CSquadNormal prune/build-formation"],
        ["squad-normal", "linked-unit-list", "query"],
        ["this + 0x17c", "iVar2 + 0x94", "return true"],
    ),
    "0x004fd5e0": target(
        "CUnit__VFunc26_GetRecentSegmentDamageMeter",
        "int __thiscall CUnit__VFunc26_GetRecentSegmentDamageMeter(void * this, int segment_index)",
        ["RET 0x4", "slot 26", "segment_index", "this-8 vfunc +0x1ac", "0..100"],
        ["unit-vfunc-slot-26", "destructible-segment", "damage-meter", "renamed"],
        ["CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex", "segment_index", "this + -8", "return 100"],
    ),
    "0x004fd6a0": target(
        "CUnit__VFunc22_ActivateLinkedTargetsAndChildren",
        "void __fastcall CUnit__VFunc22_ActivateLinkedTargetsAndChildren(void * this)",
        ["slot-22", "this+0x214", "this+0x148", "this+0x19c", "vfunc +0x58"],
        ["unit-vfunc-slot-22", "activation", "linked-reader", "renamed"],
        ["this + 0x214", "this + 0x148", "this + 0x19c", "+ 0x58"],
    ),
    "0x004fd700": target(
        "CUnit__VFunc23_DeactivateLinkedTargetsAndChildren",
        "void __fastcall CUnit__VFunc23_DeactivateLinkedTargetsAndChildren(void * this)",
        ["slot-23", "this+0x214", "this+0x148", "this+0x19c", "vfunc +0x5c"],
        ["unit-vfunc-slot-23", "deactivation", "linked-reader", "renamed"],
        ["this + 0x214", "this + 0x148", "this + 0x19c", "+ 0x5c"],
    ),
    "0x004fd760": target(
        "CUnit__HasAnyLinkedUnitBeforeTargetTimeout",
        "bool __fastcall CUnit__HasAnyLinkedUnitBeforeTargetTimeout(void * this)",
        ["this+0x17c", "CUnit__IsTargetTimeoutBeforeProfileLimit", "CVBufTexture owner prefix is stale"],
        ["unit-targeting", "linked-unit-list", "timeout-filter", "owner-corrected", "renamed"],
        ["this + 0x17c", "CUnit__IsTargetTimeoutBeforeProfileLimit", "return true"],
    ),
}

EXPECTED_XREFS = {
    ("004fd230", "CUnit__SpawnProfileDropPickup", "004fd0dd", "004fd040", "CUnit__ResetDeploymentGraphAndScheduleEvent", "UNCONDITIONAL_CALL"),
    ("004fd230", "CUnit__SpawnProfileDropPickup", "00428208", "00428110", "CUnitAI__UpdateActivationStateAndSpawnPickup", "UNCONDITIONAL_CALL"),
    ("004fd230", "CUnit__SpawnProfileDropPickup", "004f9974", "004f9820", "CUnit__HandleEvent", "UNCONDITIONAL_CALL"),
    ("004fd3d0", "CUnit__IsCandidateSideCompatibleForTargeting", "00406902", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("004fd3d0", "CUnit__IsCandidateSideCompatibleForTargeting", "00406ddc", "00406da0", "CBattleEngine__SelectNearestForwardTargetFromGlobalSet", "UNCONDITIONAL_CALL"),
    ("004fd3d0", "CUnit__IsCandidateSideCompatibleForTargeting", "004dae48", "004dac90", "CRound__SelectBestTargetReaderAndSyncAimState", "UNCONDITIONAL_CALL"),
    ("004fd500", "CUnit__ApplyRenderPositionDeltaToVector", "00484b13", "00484340", "CHud__RenderTargetMarkers3D", "UNCONDITIONAL_CALL"),
    ("004fd500", "CUnit__ApplyRenderPositionDeltaToVector", "00486f47", "00486e00", "CHud__RenderWorldTargetSprites", "UNCONDITIONAL_CALL"),
    ("004fd570", "CSquadNormal__HasAnyLinkedUnitWithField94", "004e8456", "004e83b0", "CSquadNormal__PruneDeadMembersAndReschedule", "UNCONDITIONAL_CALL"),
    ("004fd570", "CSquadNormal__HasAnyLinkedUnitWithField94", "004e8bd5", "004e8930", "CSquadNormal__BuildAttackFormation", "UNCONDITIONAL_CALL"),
    ("004fd6a0", "CUnit__VFunc22_ActivateLinkedTargetsAndChildren", "00428abc", "004289b0", "CUnitAI__AdvanceActivationAnimationState", "UNCONDITIONAL_CALL"),
    ("004fd700", "CUnit__VFunc23_DeactivateLinkedTargetsAndChildren", "00428b26", "004289b0", "CUnitAI__AdvanceActivationAnimationState", "UNCONDITIONAL_CALL"),
    ("004fd760", "CUnit__HasAnyLinkedUnitBeforeTargetTimeout", "0047a963", "0047a900", "CGillMHeadAI__AdvanceOpenAttackCloseState", "UNCONDITIONAL_CALL"),
    ("004fd760", "CUnit__HasAnyLinkedUnitBeforeTargetTimeout", "00504cf3", "00504cf0", "CVBufTexture__ShouldSkipUpdateByStateFlags", "UNCONDITIONAL_CALL"),
}

EXPECTED_APPLY = {
    "updated": 8,
    "skipped": 0,
    "renamed": 7,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 8,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

CALLER_TOKENS = [
    "CUnit__SpawnProfileDropPickup",
    "CUnit__IsCandidateSideCompatibleForTargeting",
    "CUnit__ApplyRenderPositionDeltaToVector",
    "CUnit__VFunc22_ActivateLinkedTargetsAndChildren",
    "CUnit__VFunc23_DeactivateLinkedTargetsAndChildren",
    "CUnit__HasAnyLinkedUnitBeforeTargetTimeout",
]

VTABLE_TOKENS = [
    "CUnit__VFunc26_GetRecentSegmentDamageMeter",
    "CUnit__VFunc22_ActivateLinkedTargetsAndChildren",
    "CUnit__VFunc23_DeactivateLinkedTargetsAndChildren",
    "CUnit__HandleEvent",
    "CUnit__VFunc02_CleanupWorldLinksAndForward",
]

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise AssertionError(f"missing TSV: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"SUMMARY updated=(\d+) skipped=(\d+) renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    require(match is not None, f"missing SUMMARY in {path}")
    keys = ["updated", "skipped", "renamed", "would_rename", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups())}


def decompile_text(address: str, expected_name: str) -> str:
    normalized = normalize_address(address)[2:]
    for path in (BASE / "post_decomp").glob(f"{normalized}_*.c"):
        if expected_name in path.name:
            return read_text(path)
    raise AssertionError(f"missing decompile output for {address} {expected_name}")


def check_metadata() -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post_metadata.tsv")}
    require(set(rows) == set(TARGETS), f"metadata target mismatch: {sorted(rows)}")
    for address, spec in TARGETS.items():
        row = rows[address]
        require(row["status"] == "OK", f"{address} metadata status {row['status']}")
        require(row["name"] == spec["name"], f"{address} name {row['name']}")
        require(unescape(row["signature"]) == spec["signature"], f"{address} signature {row['signature']}")
        comment = unescape(row["comment"])
        for token in spec["commentTokens"]:  # type: ignore[index]
            require(token_present(comment, token), f"{address} missing comment token {token!r}")
        lowered = comment.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{address} overclaim token in comment: {token}")


def check_tags() -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post_tags.tsv")}
    for address, spec in TARGETS.items():
        row = rows.get(address)
        require(row is not None and row["status"] == "OK", f"{address} tag row missing/failed")
        tags = set(filter(None, row["tags"].split(";")))
        expected = set(spec["tags"])  # type: ignore[arg-type]
        require(expected.issubset(tags), f"{address} missing tags {sorted(expected - tags)}")


def check_xrefs() -> None:
    actual = {
        (
            row["target_addr"].lower(),
            row["target_name"],
            row["from_addr"].lower(),
            row["from_function_addr"].lower(),
            row["from_function"],
            row["ref_type"],
        )
        for row in read_tsv(BASE / "post_xrefs.tsv")
    }
    missing = EXPECTED_XREFS - actual
    require(not missing, f"missing expected xrefs: {sorted(missing)}")


def check_decompile() -> None:
    index = read_tsv(BASE / "post_decomp" / "index.tsv")
    ok = {normalize_address(row["address"]) for row in index if row["status"] == "OK"}
    require(ok == set(TARGETS), f"decompile OK mismatch: {sorted(ok)}")
    for address, spec in TARGETS.items():
        text = decompile_text(address, spec["name"])  # type: ignore[arg-type]
        for token in spec["decompileTokens"]:  # type: ignore[index]
            require(token_present(text, token), f"{address} missing decompile token {token!r}")


def check_callers() -> None:
    text = "\n".join(read_text(path) for path in (BASE / "post_caller_decomp").glob("*.c"))
    require(text, "missing post caller decompile text")
    for token in CALLER_TOKENS:
        require(token_present(text, token), f"missing caller token {token!r}")


def check_vtables() -> None:
    text = read_text(BASE / "post_vtables.tsv")
    require(text, "missing post vtable export")
    for token in VTABLE_TOKENS:
        require(token_present(text, token), f"missing vtable token {token!r}")


def check_logs() -> None:
    require(parse_summary(BASE / "apply_unit_support_tail_wave540_apply.log") == EXPECTED_APPLY, "apply summary mismatch")
    require(
        parse_summary(BASE / "apply_unit_support_tail_wave540_verify_dry.log") == EXPECTED_VERIFY_DRY,
        "verify dry summary mismatch",
    )
    apply_text = read_text(BASE / "apply_unit_support_tail_wave540_apply.log")
    require("REPORT: Save succeeded" in apply_text, "apply log missing save report")


def check_docs_when_present() -> None:
    docs = [
        ROOT / "release" / "readiness" / "ghidra_unit_support_tail_wave540_2026-05-18.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md",
    ]
    for path in docs:
        if not path.is_file():
            continue
        text = read_text(path)
        if "Wave540" not in text:
            continue
        for address, spec in TARGETS.items():
            require(spec["name"] in text, f"{path} missing {spec['name']}")  # type: ignore[index]
            require(address in text, f"{path} missing {address}")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path} contains overclaim token {token}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run Wave540 checks")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    check_metadata()
    check_tags()
    check_xrefs()
    check_decompile()
    check_callers()
    check_vtables()
    check_logs()
    check_docs_when_present()
    print("Wave540 Unit support-tail probe PASS: 8 functions, caller/vtable/read-back evidence verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
