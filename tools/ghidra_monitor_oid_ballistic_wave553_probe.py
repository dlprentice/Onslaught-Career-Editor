#!/usr/bin/env python3
"""Validate Wave553 monitor/OID ballistic Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave553-monitor-oid-ballistic-005078f0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_monitor_oid_ballistic_wave553_2026-05-18.md"
GHIDRA_REF = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
STATIC_CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
MONITOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "monitor.h" / "_index.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
SQUAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadNormal.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"

TARGETS = {
    "0x005078f0": {
        "raw": "005078f0",
        "name": "CMonitor__UpdateTrackedRenderPair",
        "signature": "void __thiscall CMonitor__UpdateTrackedRenderPair(void * this, int update_projected_volume)",
        "tags": {
            "comment-hardened",
            "monitor",
            "monitor-oid-ballistic-wave553",
            "phantom-param-removed",
            "projected-volume",
            "render-pair",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
        },
        "comment_tokens": (
            "RET 0x4",
            "one explicit update_projected_volume flag",
            "this +0x18/+0x20",
            "owner vfunc +300",
            "projected-volume orientation",
            "runtime render behavior",
            "remain unproven",
        ),
        "decompile_tokens": (
            "void __thiscall CMonitor__UpdateTrackedRenderPair(void *this,int update_projected_volume)",
            "if (update_projected_volume != 0)",
            "CMeshRenderer__CopyBasisAndRefreshTime",
            "Mat34__MultiplyBasisToOut",
        ),
        "xref_functions": (
            "CMonitor__UpdateMovementTransitionAndEffects",
            "CBattleEngineWalkerPart__Move",
        ),
    },
    "0x00507ab0": {
        "raw": "00507ab0",
        "name": "OID__CanFireAtTarget_BallisticArcA",
        "signature": "int __thiscall OID__CanFireAtTarget_BallisticArcA(void * this, void * target_unit, int ballistic_context)",
        "tags": {
            "comment-hardened",
            "fire-eligibility",
            "monitor-oid-ballistic-wave553",
            "oid",
            "phantom-param-removed",
            "projectile-ballistics",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
        },
        "comment_tokens": (
            "RET 0x8",
            "two explicit stack arguments",
            "older third explicit parameter was register carryover",
            "ballistic-arc statement state",
            "OID__TraceLineAndSelectBestTargetHit",
            "fire-eligibility boolean",
            "remain unproven",
        ),
        "decompile_tokens": (
            "OID__CanFireAtTarget_BallisticArcA(void *this,void *target_unit,int ballistic_context)",
            "CWeaponStatement__UsesBallisticArcNoLocks",
            "OID__TraceLineAndSelectBestTargetHit",
            "target_unit + 0x138",
            "ballistic_context == 0",
        ),
        "forbidden_decompile_tokens": ("param_3",),
        "xref_functions": ("CUnit__CanFireAtTarget_BallisticArcA",),
    },
    "0x005088b0": {
        "raw": "005088b0",
        "name": "OID__CanFireAtTarget_BallisticArcB",
        "signature": "int __thiscall OID__CanFireAtTarget_BallisticArcB(void * this, void * target_unit)",
        "tags": {
            "comment-hardened",
            "fire-eligibility",
            "monitor-oid-ballistic-wave553",
            "oid",
            "phantom-param-removed",
            "projectile-ballistics",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
        },
        "comment_tokens": (
            "RET 0x4",
            "one explicit target_unit argument",
            "older second explicit parameter was register carryover",
            "static-shadow fallback behavior",
            "OID__TraceLineAndSelectBestTargetHit",
            "fire-eligibility boolean",
            "remain unproven",
        ),
        "decompile_tokens": (
            "int __thiscall OID__CanFireAtTarget_BallisticArcB(void *this,void *target_unit)",
            "CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta",
            "OID__TraceLineAndSelectBestTargetHit",
            "target_unit + 0x138",
        ),
        "forbidden_decompile_tokens": ("param_2",),
        "xref_functions": ("CUnit__CanFireAtTarget_BallisticArcB",),
    },
    "0x00509140": {
        "raw": "00509140",
        "name": "OID__UpdateAimTransformAndAttachTargetReader",
        "signature": "void __thiscall OID__UpdateAimTransformAndAttachTargetReader(void * this, void * target_reader, void * target_transform)",
        "tags": {
            "active-reader",
            "aim-transform",
            "comment-hardened",
            "monitor-oid-ballistic-wave553",
            "oid",
            "phantom-param-removed",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
        },
        "comment_tokens": (
            "RET 0x8",
            "two explicit stack arguments",
            "older third explicit parameter was register carryover",
            "target_transform",
            "CGenericActiveReader__SetReader",
            "exact argument order at higher-level wrappers",
            "remain unproven",
        ),
        "decompile_tokens": (
            "OID__UpdateAimTransformAndAttachTargetReader(void *this,void *target_reader,void *target_transform)",
            "target_transform + 8",
            "target_reader",
            "CGenericActiveReader__SetReader",
        ),
        "forbidden_decompile_tokens": ("param_3",),
        "xref_functions": ("CUnit__ForwardAimTransformAndAttachTargetReader",),
    },
    "0x005094b0": {
        "raw": "005094b0",
        "name": "OID__SolveBallisticPitchToTarget",
        "signature": "double __thiscall OID__SolveBallisticPitchToTarget(void * this, float target_x, float target_y, float target_z, float target_w)",
        "tags": {
            "comment-hardened",
            "monitor-oid-ballistic-wave553",
            "oid",
            "pitch-solver",
            "projectile-ballistics",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "vector-target",
        },
        "comment_tokens": (
            "RET 0x10",
            "four explicit stack dwords",
            "target_x/target_y/target_z",
            "target_w is carried by the 16-byte vector convention",
            "direct acos fallback",
            "remain unproven",
        ),
        "decompile_tokens": (
            "float target_x,float target_y,float target_z,float target_w",
            "target_x - local_20",
            "target_y - local_1c",
            "target_z - local_18",
            "OID__AcosWrapper",
        ),
        "xref_functions": (
            "CUnit__UpdateFireControlYawAndQueueEvent",
            "CWarspiteDome__UpdateTrackedPitchWithClamp",
            "<no_function>",
        ),
    },
    "0x005096a0": {
        "raw": "005096a0",
        "name": "CUnit__ComputeMinBallisticTravelDistance",
        "signature": "double __thiscall CUnit__ComputeMinBallisticTravelDistance(void * this, float target_x, float target_y, float target_z, float target_w)",
        "tags": {
            "comment-hardened",
            "cunit",
            "monitor-oid-ballistic-wave553",
            "projectile-ballistics",
            "range-distance",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "vector-target",
        },
        "comment_tokens": (
            "RET 0x10",
            "four explicit vector dwords",
            "Non-ballistic statements return owner +0xa0 field +0x74",
            "minimum reachable travel distance",
            "remain unproven",
        ),
        "decompile_tokens": (
            "float target_x,float target_y,float target_z,float target_w",
            "CWeaponStatement__UsesBallisticArcNoLocks",
            "target_z",
            "return (double)*(float *)(*(int *)((int)this + 0xa0) + 0x74)",
        ),
        "forbidden_decompile_tokens": ("param_1",),
        "xref_functions": (
            "CBattleEngine__HandleAutoAim",
            "CUnit__ClassifyTargetRangeBand",
            "CSquadNormal__SelectBestSupportOrEscort",
            "CSquadNormal__GetSupportMinEngageDistance",
        ),
    },
    "0x005099a0": {
        "raw": "005099a0",
        "name": "CUnit__ComputeMaxBallisticTravelDistance",
        "signature": "double __thiscall CUnit__ComputeMaxBallisticTravelDistance(void * this, float target_x, float target_y, float target_z, float target_w)",
        "tags": {
            "comment-hardened",
            "cunit",
            "monitor-oid-ballistic-wave553",
            "projectile-ballistics",
            "range-distance",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "vector-target",
        },
        "comment_tokens": (
            "RET 0x10",
            "four explicit vector dwords",
            "Non-ballistic statements return owner +0xa0 field +0x78",
            "maximum reachable travel distance",
            "remain unproven",
        ),
        "decompile_tokens": (
            "float target_x,float target_y,float target_z,float target_w",
            "CWeaponStatement__UsesBallisticArcNoLocks",
            "target_z",
            "return (double)*(float *)(*(int *)((int)this + 0xa0) + 0x78)",
        ),
        "forbidden_decompile_tokens": ("param_1",),
        "xref_functions": (
            "CBattleEngine__HandleAutoAim",
            "CBattleEngine__ComputeProjectileMetricFromTargetProfile",
            "CUnit__ClassifyTargetRangeBand",
            "CSquadNormal__SelectBestSupportOrEscort",
            "ProjectileBurst__SpawnFromCurrentPreset",
            "CSquadNormal__GetSupportMaxEngageDistance",
            "ProjectileBurstCallerBoundary_004f4920",
        ),
    },
    "0x00509c80": {
        "raw": "00509c80",
        "name": "CBattleEngine__ComputeProjectileMetricFromTargetProfile",
        "signature": "double __thiscall CBattleEngine__ComputeProjectileMetricFromTargetProfile(void * this, float target_x, float target_y, float target_z, float target_w)",
        "tags": {
            "battleengine",
            "comment-hardened",
            "monitor-oid-ballistic-wave553",
            "projectile-ballistics",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "target-profile",
            "vector-target",
        },
        "comment_tokens": (
            "RET 0x10",
            "four explicit vector dwords",
            "CUnit__ComputeMaxBallisticTravelDistance",
            "DAT_008553ec",
            "target/profile entry",
            "remain unproven",
        ),
        "decompile_tokens": (
            "float target_x,float target_y,float target_z,float target_w",
            "CUnit__ComputeMaxBallisticTravelDistance",
            "DAT_008553ec",
            "CBattleEngine__GetTargetSetEntryByIndex",
        ),
        "forbidden_decompile_tokens": ("param_1",),
        "xref_functions": ("CBattleEngine__CalcUnitOverCrossHair",),
    },
}

RET_TOKENS = {
    "0x005078f0": "RET\t0x4",
    "0x00507ab0": "RET\t0x8",
    "0x005088b0": "RET\t0x4",
    "0x00509140": "RET\t0x8",
    "0x005094b0": "RET\t0x10",
    "0x005096a0": "RET\t0x10",
    "0x005099a0": "RET\t0x10",
    "0x00509c80": "RET\t0x10",
}

CALLSITE_TOKENS = (
    "0x00410c7f\t0x00410c50\tCMonitor__UpdateMovementTransitionAndEffects\tPUSH\t0x1",
    "0x00410c81\t0x00410c50\tCMonitor__UpdateMovementTransitionAndEffects\tCALL\t0x005078f0",
    "0x004137a4\t0x00413760\tCBattleEngineWalkerPart__Move\tPUSH\t0x0",
    "0x004137a6\t0x00413760\tCBattleEngineWalkerPart__Move\tCALL\t0x005078f0",
    "0x004fb576\t0x004fb500\tCUnit__CanFireAtTarget_BallisticArcA\tPUSH\tEAX",
    "0x004fb577\t0x004fb500\tCUnit__CanFireAtTarget_BallisticArcA\tPUSH\tEDI",
    "0x004fb578\t0x004fb500\tCUnit__CanFireAtTarget_BallisticArcA\tCALL\t0x00507ab0",
    "0x004fb628\t0x004fb5a0\tCUnit__CanFireAtTarget_BallisticArcB\tPUSH\tEDI",
    "0x004fb629\t0x004fb5a0\tCUnit__CanFireAtTarget_BallisticArcB\tCALL\t0x005088b0",
    "0x004fb662\t0x004fb650\tCUnit__ForwardAimTransformAndAttachTargetReader\tPUSH\tEAX",
    "0x004fb663\t0x004fb650\tCUnit__ForwardAimTransformAndAttachTargetReader\tPUSH\tEDX",
    "0x004fb664\t0x004fb650\tCUnit__ForwardAimTransformAndAttachTargetReader\tCALL\t0x00509140",
    "0x004fb2fd\t0x004fb280\tCUnit__UpdateFireControlYawAndQueueEvent\tCALL\t0x005094b0",
    "0x0040b7a9\t0x0040b6d0\tCBattleEngine__HandleAutoAim\tCALL\t0x005096a0",
    "0x0040b7d1\t0x0040b6d0\tCBattleEngine__HandleAutoAim\tCALL\t0x005099a0",
    "0x00509ce2\t0x00509c80\tCBattleEngine__ComputeProjectileMetricFromTargetProfile\tCALL\t0x005099a0",
    "0x0040ad64\t0x0040acc0\tCBattleEngine__CalcUnitOverCrossHair\tCALL\t0x00509c80",
)

CALLER_DECOMPILE_TOKENS = (
    "CMonitor__UpdateTrackedRenderPair(pvVar5,1);",
    "CMonitor__UpdateTrackedRenderPair(pvVar7,0);",
    "OID__CanFireAtTarget_BallisticArcA(*(void **)((int)this + 0x140),target_unit,ballistic_context);",
    "OID__CanFireAtTarget_BallisticArcB(*(void **)((int)this + 0x140),target_unit);",
    "OID__UpdateAimTransformAndAttachTargetReader",
    "OID__SolveBallisticPitchToTarget",
    "CUnit__ComputeMinBallisticTravelDistance",
    "CUnit__ComputeMaxBallisticTravelDistance",
    "CBattleEngine__ComputeProjectileMetricFromTargetProfile",
)

DOC_TOKENS = {
    PUBLIC_NOTE: (
        "Wave553",
        "CMonitor__UpdateTrackedRenderPair",
        "OID__CanFireAtTarget_BallisticArcA",
        "CUnit__ComputeMaxBallisticTravelDistance",
        "CBattleEngine__ComputeProjectileMetricFromTargetProfile",
        "updated=8",
        "runtime targeting/projectile/render behavior",
    ),
    GHIDRA_REF: (
        "Wave553",
        "CMonitor__UpdateTrackedRenderPair",
        "OID__CanFireAtTarget_BallisticArcA",
        "CUnit__ComputeMinBallisticTravelDistance",
        "CBattleEngine__ComputeProjectileMetricFromTargetProfile",
    ),
    STATIC_CAMPAIGN: (
        "Wave 553: Monitor/OID Ballistic Vector Cleanup",
        "updated=8",
        "strict comment-plus-clean-signature proxy",
    ),
    FUNCTION_INDEX: (
        "Wave553",
        "CMonitor__UpdateTrackedRenderPair",
        "OID__CanFireAtTarget_BallisticArcA",
        "CUnit__ComputeMaxBallisticTravelDistance",
    ),
    UNIT_DOC: (
        "Wave 553 Monitor/OID Ballistic Vector Cleanup",
        "OID__CanFireAtTarget_BallisticArcA",
        "CUnit__ComputeMinBallisticTravelDistance",
        "CUnit__ComputeMaxBallisticTravelDistance",
    ),
    MONITOR_DOC: (
        "Wave553",
        "CMonitor__UpdateTrackedRenderPair",
        "update_projected_volume",
    ),
    BATTLEENGINE_DOC: (
        "Wave553",
        "CBattleEngine__ComputeProjectileMetricFromTargetProfile",
        "DAT_008553ec",
    ),
    SQUAD_DOC: (
        "Wave553",
        "CUnit__ComputeMinBallisticTravelDistance",
        "CUnit__ComputeMaxBallisticTravelDistance",
    ),
    BACKLOG: (
        "Wave553",
        "0x005078f0",
        "0x00509c80",
        "monitor/OID ballistic",
    ),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime render behavior proven",
    "runtime targeting behavior proven",
    "runtime projectile behavior proven",
    "complete monitor system",
    "complete oid system",
    "complete cunit system",
    "complete battleengine system",
    "fully recovered",
    "concrete layout proven",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_text(path: Path) -> str:
    require(path.exists(), f"missing file: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def compact(value: str) -> str:
    return "".join(" ".join((value or "").replace("`", "").split()).lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_for(rows: list[dict[str, str]], key: str, address: str) -> dict[str, str]:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    raise AssertionError(f"missing row for {address} in {key}")


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"SUMMARY: mode=(dry|apply) updated=(\d+) skipped=(\d+) renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    require(match is not None, f"missing summary in {path}")
    keys = ("updated", "skipped", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups()[1:])}


def check_logs() -> None:
    dry = parse_summary(BASE / "wave553_dry.log")
    apply = parse_summary(BASE / "wave553_apply.log")
    verify = parse_summary(BASE / "wave553_verify_dry.log")
    require(dry == {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, f"dry summary mismatch {dry}")
    require(apply == {"updated": 8, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, f"apply summary mismatch {apply}")
    require(verify == {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, f"verify summary mismatch {verify}")
    for path in (BASE / "wave553_dry.log", BASE / "wave553_apply.log", BASE / "wave553_verify_dry.log"):
        text = read_text(path)
        require("REPORT: Save succeeded" in text, f"{path.name} missing save success")
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:"):
            require(bad not in text, f"{path.name} contains {bad}")


def check_metadata() -> None:
    rows = read_tsv(BASE / "post_metadata.tsv")
    require(len(rows) == 8, f"expected 8 metadata rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_for(rows, "address", address)
        require(row["name"] == expected["name"], f"{address} name mismatch {row['name']}")
        require(row["signature"] == expected["signature"], f"{address} signature mismatch {row['signature']}")
        require(row["status"] == "OK", f"{address} metadata status mismatch {row['status']}")
        for token in expected["comment_tokens"]:
            require(token_present(row["comment"], token), f"{address} comment missing {token!r}")
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{address} comment contains overclaim token {token}")


def check_tags() -> None:
    rows = read_tsv(BASE / "post_tags.tsv")
    require(len(rows) == 8, f"expected 8 tag rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_for(rows, "address", address)
        tags = set(filter(None, row["tags"].split(";")))
        require(expected["tags"].issubset(tags), f"{address} missing tags {sorted(expected['tags'] - tags)}")
        require(row["status"] == "OK", f"{address} tag status mismatch {row['status']}")


def check_xrefs() -> None:
    rows = read_tsv(BASE / "post_xrefs.tsv")
    require(len(rows) == 22, f"expected 22 xref rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        callers = {
            row["from_function"]
            for row in rows
            if normalize_address(row["target_addr"]) == normalize_address(address)
        }
        require(set(expected["xref_functions"]).issubset(callers), f"{address} xref callers mismatch {callers}")
        for row in rows:
            if normalize_address(row["target_addr"]) == normalize_address(address):
                require(row["target_name"] == expected["name"], f"{address} xref target name mismatch")
                require(row["ref_type"] == "UNCONDITIONAL_CALL", f"{address} xref type mismatch {row['ref_type']}")


def check_decompile() -> None:
    index_rows = read_tsv(BASE / "post_decomp" / "index.tsv")
    require(len(index_rows) == 8, f"expected 8 decompile index rows, got {len(index_rows)}")
    for address, expected in TARGETS.items():
        row = row_for(index_rows, "address", address)
        require(row["name"] == expected["name"], f"{address} decompile index name mismatch")
        require(row["signature"] == expected["signature"], f"{address} decompile index signature mismatch")
        require(row["status"] == "OK", f"{address} decompile index status mismatch {row['status']}")
        matches = list((BASE / "post_decomp").glob(f"{expected['raw']}_*.c"))
        require(len(matches) == 1, f"{address} expected one decompile export, got {len(matches)}")
        require(expected["name"] in matches[0].name, f"{address} decompile filename mismatch {matches[0].name}")
        text = read_text(matches[0])
        for token in expected["decompile_tokens"]:
            require(token_present(text, token), f"{address} decompile missing {token!r}")
        for token in expected.get("forbidden_decompile_tokens", ()):
            require(not token_present(text, token), f"{address} decompile still contains forbidden token {token!r}")

    caller_rows = read_tsv(BASE / "post_caller_decomp" / "index.tsv")
    require(len(caller_rows) == 15, f"expected 15 caller decompile index rows, got {len(caller_rows)}")
    caller_text = "\n".join(read_text(path) for path in (BASE / "post_caller_decomp").glob("*.c"))
    for token in CALLER_DECOMPILE_TOKENS:
        require(token_present(caller_text, token), f"caller decompile missing {token!r}")


def check_instructions() -> None:
    target_rows = read_tsv(BASE / "post_instructions.tsv")
    full_rows = read_tsv(BASE / "post_instructions_full.tsv")
    arc_a_full_rows = read_tsv(BASE / "post_instructions_00507ab0_full.tsv")
    callsite_rows = read_tsv(BASE / "post_callsite_instructions.tsv")
    require(len(target_rows) == 1448, f"expected 1448 focused instruction rows, got {len(target_rows)}")
    require(len(full_rows) == 4968, f"expected 4968 full instruction rows, got {len(full_rows)}")
    require(len(arc_a_full_rows) > 1000, f"expected large 00507ab0 full instruction export, got {len(arc_a_full_rows)}")
    require(len(callsite_rows) == 330, f"expected 330 callsite instruction rows, got {len(callsite_rows)}")

    full_text = "\n".join("\t".join(row.values()) for row in full_rows + arc_a_full_rows)
    for address, token in RET_TOKENS.items():
        function_name = TARGETS[address]["name"]
        require(token_present(full_text, function_name) and token_present(full_text, token), f"{address} missing return cleanup token {token}")

    callsite_text = "\n".join("\t".join(row.values()) for row in callsite_rows)
    for token in CALLSITE_TOKENS:
        require(token_present(callsite_text, token), f"callsite instructions missing {token!r}")


def check_docs() -> None:
    for path, tokens in DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(token_present(text, token), f"{path}: missing token {token}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    check_logs()
    check_metadata()
    check_tags()
    check_xrefs()
    check_decompile()
    check_instructions()
    check_docs()
    print("Wave553 monitor/OID ballistic probe PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
