#!/usr/bin/env python3
"""Validate Wave554 target/profile gate Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave554-target-profile-gates-00509e40"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_target_profile_gates_wave554_2026-05-18.md"
GHIDRA_REF = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
STATIC_CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
SQUAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadNormal.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
PACKAGE_JSON = ROOT / "package.json"


TARGETS = {
    "0x00509e40": {
        "raw": "00509e40",
        "name": "TargetSet__GetEntryByIndex",
        "signature": "void * __cdecl TargetSet__GetEntryByIndex(int target_entry_index)",
        "tags": {
            "comment-hardened",
            "owner-neutral-correction",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "target-profile",
            "target-profile-gates-wave554",
            "target-set",
        },
        "comment_tokens": (
            "global target/profile set at DAT_008553ec",
            "target_entry_index",
            "GenericSPtrSet::At",
            "entry pointer or null",
            "remain unproven",
        ),
        "decompile_tokens": (
            "void * __cdecl TargetSet__GetEntryByIndex(int target_entry_index)",
            "DAT_008553ec[2]",
            "target_entry_index",
            "return (void *)0x0",
        ),
        "xref_functions": ("CBattleEngine__ComputeProjectileMetricFromTargetProfile",),
    },
    "0x00509e90": {
        "raw": "00509e90",
        "name": "ProjectileBurst__ResolvePresetByPercentBucketFallback",
        "signature": "void * __fastcall ProjectileBurst__ResolvePresetByPercentBucketFallback(void * burst_context)",
        "tags": {
            "comment-hardened",
            "owner-neutral-correction",
            "percent-bucket",
            "projectile-burst",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "target-profile",
            "target-profile-gates-wave554",
        },
        "comment_tokens": (
            "exclusive caller ProjectileBurst__SpawnFromPercentBucketFallback",
            "not a CEngine method",
            "burst_context +0x60",
            "+0xa4 bucket table",
            "DAT_008553ec",
        ),
        "decompile_tokens": (
            "void * __fastcall ProjectileBurst__ResolvePresetByPercentBucketFallback(void *burst_context)",
            "ROUND(*(float *)((int)burst_context + 0x60))",
            "return pvVar3",
            "return (void *)0x0",
        ),
        "forbidden_decompile_tokens": ("CEngine__ResolvePresetByPercentBucketFallback",),
        "xref_functions": ("ProjectileBurst__SpawnFromPercentBucketFallback",),
    },
    "0x00509f70": {
        "raw": "00509f70",
        "name": "TargetProfileContext__IsEligibleByDistanceBucketOrRange",
        "signature": "int __fastcall TargetProfileContext__IsEligibleByDistanceBucketOrRange(void * target_context)",
        "tags": {
            "comment-hardened",
            "owner-neutral-correction",
            "percent-bucket",
            "range-gate",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "target-profile",
            "target-profile-gates-wave554",
        },
        "comment_tokens": (
            "shared target/profile context gate",
            "rather than a CUnit-only method",
            "target_context +0xa0",
            "range time at +0x64",
            "DAT_008553ec fallback scan",
        ),
        "decompile_tokens": (
            "TargetProfileContext__IsEligibleByDistanceBucketOrRange(void *target_context)",
            "target_context + 0xa0",
            "target_context + 100",
            "target_context + 0xa4",
        ),
        "forbidden_decompile_tokens": ("CUnit__IsEligibleByDistanceBucketOrRange", "param_1"),
        "xref_functions": (
            "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
            "CUnit__UpdateDeployStateAndChargeEffects",
            "CSquadNormal__SelectBestSupportOrEscort",
            "CUnitAI__TrySpawnOrFinalizeAttachedUnit",
            "CSentinel__UpdateFlamethrowers",
            "CUnit__CanDeployNow",
            "ProjectileBurstCallerBoundary_0044e020",
            "ProjectileBurstCallerBoundary_004f4920",
        ),
    },
    "0x0050a080": {
        "raw": "0050a080",
        "name": "TargetProfileContext__CanProceedByTargetRangeGate",
        "signature": "int __fastcall TargetProfileContext__CanProceedByTargetRangeGate(void * target_context)",
        "tags": {
            "comment-hardened",
            "owner-neutral-correction",
            "range-gate",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "target-profile",
            "target-profile-gates-wave554",
        },
        "comment_tokens": (
            "CGeneralVolume__DispatchMode3BurstProgressAndSpawn",
            "CBattleEngineWalkerPart__ChargeWeapon",
            "target_context +0xa0",
            "DAT_00672fd0",
            "range-time gate",
        ),
        "decompile_tokens": (
            "TargetProfileContext__CanProceedByTargetRangeGate(void *target_context)",
            "target_context + 0xa0",
            "target_context + 100",
        ),
        "forbidden_decompile_tokens": ("CEngine__CanProceedByTargetRangeGate", "param_1"),
        "xref_functions": (
            "CGeneralVolume__DispatchMode3BurstProgressAndSpawn",
            "CBattleEngineWalkerPart__ChargeWeapon",
        ),
    },
    "0x0050a0b0": {
        "raw": "0050a0b0",
        "name": "CSquadNormal__HasActiveMaskMatchWithTarget",
        "signature": "uint __thiscall CSquadNormal__HasActiveMaskMatchWithTarget(void * this, void * target_unit)",
        "tags": {
            "comment-hardened",
            "mask-gate",
            "phantom-param-removed",
            "retail-binary-evidence",
            "signature-corrected",
            "squad",
            "static-reaudit",
            "support-targeting",
            "target-profile-gates-wave554",
        },
        "comment_tokens": (
            "RET 0x4",
            "one explicit target_unit argument",
            "older second explicit parameter was register carryover",
            "this +0xa8",
            "target_unit +0x34",
        ),
        "decompile_tokens": (
            "CSquadNormal__HasActiveMaskMatchWithTarget(void *this,void *target_unit)",
            "this + 0x9c",
            "this + 0xa8",
            "target_unit + 0x34",
        ),
        "forbidden_decompile_tokens": ("param_1", "param_2"),
        "xref_functions": (
            "CSquadNormal__SelectBestSupportOrEscort",
            "CSquadNormal__IsValidLinkedSupportForTarget",
        ),
    },
    "0x0050a0d0": {
        "raw": "0050a0d0",
        "name": "CUnit__HasMaskBitsA8",
        "signature": "uint __thiscall CUnit__HasMaskBitsA8(void * this, uint mask_bits)",
        "tags": {
            "comment-hardened",
            "cunit",
            "mask-gate",
            "phantom-param-removed",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "support-targeting",
            "target-profile-gates-wave554",
        },
        "comment_tokens": (
            "RET 0x4",
            "one explicit mask_bits argument",
            "older second explicit parameter was register carryover",
            "this +0xa8",
            "CSquadNormal__SelectBestSupportOrEscort",
        ),
        "decompile_tokens": (
            "CUnit__HasMaskBitsA8(void *this,uint mask_bits)",
            "this + 0xa8",
            "mask_bits",
        ),
        "forbidden_decompile_tokens": ("param_1", "param_2"),
        "xref_functions": ("CSquadNormal__SelectBestSupportOrEscort",),
    },
    "0x0050a0e0": {
        "raw": "0050a0e0",
        "name": "OID__ComputeForwardProjectedPointTowardTarget",
        "signature": "void __thiscall OID__ComputeForwardProjectedPointTowardTarget(void * this, void * out_point, void * target_unit)",
        "tags": {
            "comment-hardened",
            "oid",
            "phantom-param-removed",
            "projectile-ballistics",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "target-profile-gates-wave554",
            "target-projection",
        },
        "comment_tokens": (
            "RET 0x8",
            "two explicit stack arguments after ECX: out_point and target_unit",
            "older third explicit parameter was a decompiler artifact",
            "target velocity vfunc +0x6c",
            "DAT_005d857c",
        ),
        "decompile_tokens": (
            "OID__ComputeForwardProjectedPointTowardTarget(void *this,void *out_point,void *target_unit)",
            "target_unit + 0x168",
            "target_unit + 0x6c",
            "DAT_005d857c",
        ),
        "forbidden_decompile_tokens": ("param_1", "param_2", "param_3"),
        "xref_functions": (
            "OID__CanFireAtTarget_BallisticArcA",
            "OID__CanFireAtTarget_BallisticArcB",
        ),
    },
    "0x0050a290": {
        "raw": "0050a290",
        "name": "CUnit__IsTargetTimeoutBeforeProfileLimit",
        "signature": "int __fastcall CUnit__IsTargetTimeoutBeforeProfileLimit(void * unit)",
        "tags": {
            "comment-hardened",
            "cunit",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "target-profile",
            "target-profile-gates-wave554",
            "timeout-gate",
        },
        "comment_tokens": (
            "ECX-only predicate",
            "TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit",
            "unit +0xa0",
            "unit +0x6c",
            "profile +0x44",
        ),
        "decompile_tokens": (
            "CUnit__IsTargetTimeoutBeforeProfileLimit(void *unit)",
            "unit + 0xa0",
            "unit + 0x6c",
            "+ 0x44",
        ),
        "forbidden_decompile_tokens": ("param_1",),
        "xref_functions": (
            "TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit",
            "CUnit__HasAnyLinkedUnitBeforeTargetTimeout",
            "CSquadNormal__SelectBestSupportOrEscort",
        ),
    },
}


DOC_TOKENS = {
    PUBLIC_NOTE: (
        "Wave554",
        "TargetProfileContext__IsEligibleByDistanceBucketOrRange",
        "OID__ComputeForwardProjectedPointTowardTarget",
        "updated=8 skipped=0 renamed=4",
        "6089",
        "2680",
        "2626/6089 = 43.13%",
    ),
    GHIDRA_REF: (
        "Current Signature Caveat: Target/Profile Gates",
        "TargetSet__GetEntryByIndex",
        "ProjectileBurst__ResolvePresetByPercentBucketFallback",
        "TargetProfileContext__CanProceedByTargetRangeGate",
        "OID__ComputeForwardProjectedPointTowardTarget",
    ),
    STATIC_CAMPAIGN: (
        "Wave554 Target/Profile Gates",
        "ApplyTargetProfileGatesWave554.java",
        "updated=8 skipped=0 renamed=4",
        "Queue after Wave554",
    ),
    FUNCTION_INDEX: (
        "Static Re-Audit Wave554: target/profile gate cleanup",
        "TargetSet__GetEntryByIndex",
        "TargetProfileContext__IsEligibleByDistanceBucketOrRange",
        "CUnit__HasMaskBitsA8",
    ),
    UNIT_DOC: (
        "0x0050a0e0 | OID__ComputeForwardProjectedPointTowardTarget",
        "0x0050a290 | CUnit__IsTargetTimeoutBeforeProfileLimit",
        "Wave554 Target/Profile Gate Helpers",
    ),
    BATTLEENGINE_DOC: (
        "Target/Profile Gate Helpers (Wave554",
        "TargetSet__GetEntryByIndex",
        "TargetProfileContext__CanProceedByTargetRangeGate",
    ),
    SQUAD_DOC: (
        "Wave554 support-mask and target/profile gates",
        "CSquadNormal__HasActiveMaskMatchWithTarget",
        "CUnit__HasMaskBitsA8",
    ),
    BACKLOG: (
        "0x00509e40,0x00509e90,0x00509f70,0x0050a080,0x0050a0b0,0x0050a0d0,0x0050a0e0,0x0050a290",
        "Ghidra target/profile gate owner/signature/comment hardening",
        "updated=8 skipped=0 renamed=4",
    ),
    PACKAGE_JSON: ("test:ghidra-target-profile-gates-wave554",),
}


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise AssertionError(f"missing TSV: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def decompile_path(target: dict[str, object]) -> Path:
    raw = str(target["raw"])
    name = str(target["name"])
    return BASE / "post_decompile" / f"{raw}_{name}.c"


def check_metadata(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post_metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post_tags.tsv")}
    decomp_index = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post_decompile" / "index.tsv")}

    for address, target in TARGETS.items():
        row = rows.get(address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue
        if row.get("status") != "OK":
            failures.append(f"metadata status not OK for {address}: {row.get('status')}")
        for key in ("name", "signature"):
            if row.get(key) != target[key]:
                failures.append(f"metadata {key} mismatch for {address}: {row.get(key)!r}")
        comment = row.get("comment", "")
        for token in target["comment_tokens"]:
            if token not in comment:
                failures.append(f"comment token missing for {address}: {token}")

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"tags missing {address}")
        else:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            missing = set(target["tags"]) - actual_tags
            if missing:
                failures.append(f"tags missing for {address}: {sorted(missing)}")

        idx_row = decomp_index.get(address)
        if idx_row is None:
            failures.append(f"decompile index missing {address}")
        elif idx_row.get("signature") != target["signature"] or idx_row.get("status") != "OK":
            failures.append(f"decompile index mismatch for {address}: {idx_row}")


def check_decompiles(failures: list[str]) -> None:
    for address, target in TARGETS.items():
        text = read_text(decompile_path(target))
        for token in target["decompile_tokens"]:
            if token not in text:
                failures.append(f"decompile token missing for {address}: {token}")
        for token in target.get("forbidden_decompile_tokens", ()):
            if token in text:
                failures.append(f"forbidden decompile token present for {address}: {token}")


def check_xrefs(failures: list[str]) -> None:
    rows = read_tsv(BASE / "post_xrefs.tsv")
    by_target: dict[str, set[str]] = {}
    for row in rows:
        by_target.setdefault(normalize_address(row.get("target_addr", "")), set()).add(row.get("from_function", ""))
    for address, target in TARGETS.items():
        missing = set(target["xref_functions"]) - by_target.get(address, set())
        if missing:
            failures.append(f"xref functions missing for {address}: {sorted(missing)}")


def check_instructions(failures: list[str]) -> None:
    rows = read_tsv(BASE / "post_instructions.tsv")
    by_target: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_target.setdefault(normalize_address(row.get("target_addr", "")), []).append(row)

    def has_instruction(address: str, mnemonic: str, operands: str) -> bool:
        return any(
            row.get("mnemonic") == mnemonic and operands in row.get("operands", "")
            for row in by_target.get(address, [])
        )

    if not has_instruction("0x0050a0b0", "RET", "0x4"):
        failures.append("CSquadNormal mask helper RET 0x4 not found")
    if not has_instruction("0x0050a0d0", "RET", "0x4"):
        failures.append("CUnit mask helper RET 0x4 not found")
    if not has_instruction("0x0050a0e0", "RET", "0x8"):
        failures.append("OID projected-point helper RET 0x8 not found")
    if not has_instruction("0x0050a0e0", "FSTP", "[EAX]"):
        failures.append("OID projected-point helper out_point store not found")

    callsite_rows = read_tsv(BASE / "post_oid_forward_project_callsite_instructions.tsv")
    by_callsite: dict[str, list[dict[str, str]]] = {}
    for row in callsite_rows:
        by_callsite.setdefault(normalize_address(row.get("target_addr", "")), []).append(row)
    for callsite in ("0x00507c9d", "0x005089a8"):
        block = by_callsite.get(callsite, [])
        if not any(row.get("mnemonic") == "CALL" and "0x0050a0e0" in row.get("operands", "") for row in block):
            failures.append(f"OID projected-point callsite missing call for {callsite}")
        if not any(row.get("mnemonic") == "PUSH" and "EAX" in row.get("operands", "") for row in block):
            failures.append(f"OID projected-point callsite missing out buffer PUSH EAX for {callsite}")
        if not any(row.get("mnemonic") == "MOV" and "ECX, ESI" in row.get("operands", "") for row in block):
            failures.append(f"OID projected-point callsite missing MOV ECX, ESI for {callsite}")


def check_docs(failures: list[str]) -> None:
    for path, tokens in DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            if token not in text:
                failures.append(f"doc token missing in {path.relative_to(ROOT)}: {token}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="return nonzero on validation failure")
    args = parser.parse_args()

    failures: list[str] = []
    try:
        check_metadata(failures)
        check_decompiles(failures)
        check_xrefs(failures)
        check_instructions(failures)
        check_docs(failures)
    except AssertionError as exc:
        failures.append(str(exc))

    status = "PASS" if not failures else "FAIL"
    print(f"Ghidra target/profile gates Wave554 probe: {status}")
    print(f"Artifact root: {BASE.relative_to(ROOT)}")
    print(f"Targets checked: {len(TARGETS)}")
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
    if args.check and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
