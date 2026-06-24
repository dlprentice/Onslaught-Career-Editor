#!/usr/bin/env python3
"""Validate Wave433 CMCMech Ghidra corrections."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave433-cmcmech-current"

COMMON_TAGS = {"static-reaudit", "cmcmech-wave433", "retail-binary-evidence"}


def target(name: str, signature: str, comment_tokens: list[str], tags: list[str], decompile_tokens: list[str] | None = None) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens or [],
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00498080": target(
        "CMeshPart__NameIsNotAnyMechCylinderBone",
        "bool __cdecl CMeshPart__NameIsNotAnyMechCylinderBone(void * mesh_part)",
        ["24 observed mech hydraulic-cylinder", "returns false", "runtime mech rendering behavior", "remain unproven"],
        ["mesh-filter", "mech-cylinder-token", "renamed", "signature-corrected", "comment-hardened"],
        ["Nmidoutcyl", "Sbotincyl"],
    ),
    "0x00498270": target(
        "CMeshPart__AnyChildNameIsNmidoutcyl",
        "bool __cdecl CMeshPart__AnyChildNameIsNmidoutcyl(void * mesh_part)",
        ["child count", "+0x15c", "child pointer table", "Nmidoutcyl", "runtime child-bone behavior", "remain unproven"],
        ["mesh-filter", "mech-cylinder-token", "renamed", "signature-corrected", "comment-hardened"],
        ["Nmidoutcyl", "0x15c", "0x160"],
    ),
    "0x004983b0": target(
        "CMCMech__Constructor",
        "void * __thiscall CMCMech__Constructor(void * this, float initial_value)",
        ["RET 0x4", "vtable 0x005dc3b4", "3000 tick event", "global list 0x00704650", "runtime leg-motion behavior", "remain unproven"],
        ["cmcmech", "constructor", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["PTR_CMCMech__VFunc_00_OnTimedResetEvent_00498870_005dc3b4", "EVENT_MANAGER", "DAT_00704650"],
    ),
    "0x00498510": target(
        "CMCMech__ScalarDeletingDestructor",
        "void * __thiscall CMCMech__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ["RET 0x4", "delete-flags", "CMCMech__Destructor", "runtime destruction behavior", "remain unproven"],
        ["cmcmech", "destructor", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CMCMech__Destructor", "OID__FreeObject"],
    ),
    "0x00498530": target(
        "CMCMech__Destructor",
        "void __fastcall CMCMech__Destructor(void * this)",
        ["vtable 0x005dc3b4", "global list 0x00704650", "+0xe4 shared block", "runtime cleanup behavior", "remain unproven"],
        ["cmcmech", "destructor", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["PTR_CMCMech__VFunc_00_OnTimedResetEvent_00498870_005dc3b4", "DAT_00704650", "OID__FreeObject"],
    ),
    "0x00498870": target(
        "CMCMech__VFunc_00_OnTimedResetEvent_00498870",
        "void __thiscall CMCMech__VFunc_00_OnTimedResetEvent_00498870(void * this, void * event_record)",
        ["recovered function boundary", "vtable 0x005dc3b4 slot 0", "0x0bb8", "CMCMech__Reset", "runtime scheduling behavior", "remain unproven"],
        ["cmcmech", "function-boundary", "vtable-slot", "timed-event", "signature-corrected", "comment-hardened"],
        ["3000", "CMCMech__Reset"],
    ),
    "0x004988b0": target(
        "CMCMech__Reset",
        "void __thiscall CMCMech__Reset(void * this, int start_pose_flag, int reserved_cleaned_arg)",
        ["RET 0x8", "start-pose reset branch", "+0x50/+0x54/+0xcc", "CMCMech__UpdateBone", "runtime leg reset behavior", "remain unproven"],
        ["cmcmech", "reset", "signature-corrected", "comment-hardened"],
        ["CMCMech__UpdateBone", "CMCMech__UpdateBoneHierarchyRecursive"],
    ),
    "0x00498bf0": target(
        "CMCMech__SetParams",
        "void __thiscall CMCMech__SetParams(void * this, float value_98, float value_9c, float value_a0, float value_0c, float value_10, float value_a4, float value_c4)",
        ["RET 0x1c", "seven stack dwords", "+0x98", "+0xc4", "runtime tuning behavior", "remain unproven"],
        ["cmcmech", "parameters", "signature-corrected", "comment-hardened"],
        ["0x98", "0xc4"],
    ),
    "0x00498c40": target(
        "CMCMech__Init",
        "void __thiscall CMCMech__Init(void * this, void * mesh_model)",
        ["RET 0x4", "mesh_model", "Footbase", "toestop", "ToeMotion/LegMotion", "runtime leg IK behavior", "remain unproven"],
        ["cmcmech", "init", "signature-corrected", "comment-hardened", "source-path-evidence"],
        ["s_C__dev_ONSLAUGHT2_MCMech_cpp", "OID__AllocObject", "FindAnimationIndex"],
    ),
    "0x00499bc0": target(
        "CMCMech__GetFootHeight",
        "float __thiscall CMCMech__GetFootHeight(void * this, void * position_vec4, void * trace_context, int shadow_only_flag)",
        ["RET 0x0c", "ECX height context", "static-shadow height", "CLine trace", "OID__TraceLineAndSelectBestTargetHit", "runtime foot placement behavior", "remain unproven"],
        ["cmcmech", "terrain-height", "signature-corrected", "comment-hardened"],
        ["CStaticShadows__SampleShadowHeightBilinear", "OID__TraceLineAndSelectBestTargetHit"],
    ),
    "0x00499d60": target(
        "CMCMech__TranslatePositions",
        "void __thiscall CMCMech__TranslatePositions(void * this, void * translation_vec3)",
        ["RET 0x4", "translation_vec3", "+0x14/+0x24", "+0x34", "runtime translation behavior", "remain unproven"],
        ["cmcmech", "translation", "signature-corrected", "comment-hardened"],
        ["translation_vec3", "0x15c"],
    ),
    "0x0049bbb0": target(
        "MathMatrix3x3__DivideByScalarInPlace",
        "void __thiscall MathMatrix3x3__DivideByScalarInPlace(void * this, float scalar)",
        ["RET 0x4", "one scalar stack float", "3x3 matrix entries", "runtime math behavior", "remain unproven"],
        ["matrix3x3", "signature-corrected", "comment-hardened"],
        ["scalar"],
    ),
    "0x0049bc10": target(
        "MathMatrix3x3__TransposeInPlace",
        "void __fastcall MathMatrix3x3__TransposeInPlace(void * matrix3x3)",
        ["register-only helper", "off-diagonal", "runtime math behavior", "remain unproven"],
        ["matrix3x3", "signature-corrected", "comment-hardened"],
        ["matrix3x3"],
    ),
    "0x0049bc40": target(
        "MathMatrix3x3__Determinant",
        "double __fastcall MathMatrix3x3__Determinant(void * matrix3x3)",
        ["3x3 determinant", "x87 path", "double", "runtime math behavior", "remain unproven"],
        ["matrix3x3", "signature-corrected", "comment-hardened"],
        ["matrix3x3"],
    ),
    "0x0049bc80": target(
        "MathMatrix3x3__BuildCofactorMatrix",
        "void __thiscall MathMatrix3x3__BuildCofactorMatrix(void * this, void * out_matrix3x3)",
        ["RET 0x4", "out_matrix3x3", "cofactors", "runtime math behavior", "remain unproven"],
        ["matrix3x3", "signature-corrected", "comment-hardened"],
        ["out_matrix3x3"],
    ),
    "0x0049be00": target(
        "CMCMech__VFunc_04_UpdateInterpolatedBoneTransform_0049be00",
        "void __thiscall CMCMech__VFunc_04_UpdateInterpolatedBoneTransform_0049be00(void * this, void * mesh_part, void * transform_a, void * transform_b, int context_value)",
        ["recovered function boundary", "vtable 0x005dc3b4 slot 4", "RET 0x10", "MathMatrix3x3", "runtime bone-transform behavior", "remain unproven"],
        ["cmcmech", "function-boundary", "vtable-slot", "bone-transform", "signature-corrected", "comment-hardened"],
        ["CMCMech__Reset", "MathMatrix3x3__BuildCofactorMatrix", "MathMatrix3x3__Determinant"],
    ),
    "0x0049c1d0": target(
        "CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0",
        "void __thiscall CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0(void * this, void * mesh_part, void * out_value)",
        ["vtable 0x005dc3b4 slot 5", "RET 0x8", "DAT_008a9e44", "out_value", "runtime bone-value behavior", "remain unproven"],
        ["cmcmech", "vtable-slot", "bone-value", "renamed", "signature-corrected", "comment-hardened"],
        ["DAT_008a9e44", "out_value"],
    ),
    "0x0049c240": target(
        "CMCMech__VFunc_08_GetUpdateStateFlag_0049c240",
        "int __fastcall CMCMech__VFunc_08_GetUpdateStateFlag_0049c240(void * this)",
        ["recovered function boundary", "vtable 0x005dc3b4 slot 8", "this+0xc8", "runtime behavior", "remain unproven"],
        ["cmcmech", "function-boundary", "vtable-slot", "state-flag", "signature-corrected", "comment-hardened"],
        ["0xc8"],
    ),
    "0x0049c250": target(
        "CMeshPart__NameAvoidsMechOptimizationTokens",
        "bool __cdecl CMeshPart__NameAvoidsMechOptimizationTokens(void * mesh_part)",
        ["token 0x0062dcbc", "0x0062df3c/0x0062df34/0x0062df30", "0x0062dd20", "runtime mesh behavior", "remain unproven"],
        ["mesh-filter", "mech-token-filter", "renamed", "signature-corrected", "comment-hardened"],
        ["DAT_0062dcbc", "DAT_0062dd20"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 16, "created": 0, "would_create": 3, "renamed": 0, "would_rename": 4, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 19, "skipped": 0, "created": 3, "would_create": 0, "renamed": 4, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_CORRECTIVE_APPLY = {"updated": 19, "skipped": 0, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_VERIFY_DRY = {"updated": 0, "skipped": 19, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime behavior proven",
    "concrete layout proven",
    "source identity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
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


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "vtable", "pointer_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "decompile_after"
    if not directory.is_dir():
        return ""
    prefix = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{prefix}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ["updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def check_apply_log(base: Path, name: str, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(base / name)
    if not text:
        failures.append(f"{name}: missing or empty")
        return
    summary = parse_summary(text)
    if summary != expected:
        failures.append(f"{name}: summary mismatch expected {expected}, got {summary}")
    for token in ("FAIL:", "Exception", "LockException"):
        if token in text:
            failures.append(f"{name}: unexpected failure token {token!r}")
    if name != "apply_dry.log" and "REPORT: Save succeeded" not in text:
        failures.append(f"{name}: missing Ghidra save-success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "metadata_after.tsv")
    tags = read_tsv(base / "tags_after.tsv")
    vtable_rows = read_tsv(base / "vtable_slots_after.tsv")

    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing metadata_after row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')!r}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: signature mismatch {row.get('signature')!r}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        lowered_comment = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered_comment:
                failures.append(f"{address}: overclaim token present {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing tags_after row")
        else:
            actual_tags = {item.strip() for item in re.split(r"[;,]", tag_row.get("tags", "")) if item.strip()}
            missing = sorted(set(spec["tags"]) - actual_tags)  # type: ignore[arg-type]
            if missing:
                failures.append(f"{address}: missing tags {missing}")

        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing decompile_after")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")

    for address in ("0x00498870", "0x0049be00", "0x0049c1d0", "0x0049c240"):
        row = row_by_address(vtable_rows, address, key="pointer_addr")
        if row is None:
            failures.append(f"{address}: missing vtable slot row")
            continue
        if row.get("function_name") != TARGETS[address]["name"]:
            failures.append(f"{address}: vtable function mismatch {row.get('function_name')!r}")
        if row.get("status") != "OK":
            failures.append(f"{address}: vtable status mismatch {row.get('status')!r}")


def run(base: Path) -> dict[str, object]:
    failures: list[str] = []
    check_apply_log(base, "apply_dry.log", EXPECTED_DRY, failures)
    check_apply_log(base, "apply.log", EXPECTED_APPLY, failures)
    check_apply_log(base, "apply_corrective_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_apply_log(base, "apply_corrective.log", EXPECTED_CORRECTIVE_APPLY, failures)
    check_apply_log(base, "apply_verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    return {
        "status": "PASS" if not failures else "FAIL",
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "base": str(base),
        "targets": sorted(TARGETS),
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    result = run(args.base)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
