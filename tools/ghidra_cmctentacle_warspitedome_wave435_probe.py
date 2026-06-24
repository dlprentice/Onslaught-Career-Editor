#!/usr/bin/env python3
"""Validate Wave435 CMCTentacle / CMCWarspiteDome Ghidra corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave435-cmctentacle-current"

COMMON_TAGS = {"static-reaudit", "cmctentacle-warspitedome-wave435", "retail-binary-evidence"}


def target(name: str, signature: str, comment_tokens: list[str], tags: list[str], decompile_tokens: list[str] | None = None) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens or [],
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0049cad0": target(
        "CMCTentacle__Constructor",
        "void * __thiscall CMCTentacle__Constructor(void * this, void * owner_tentacle)",
        ["RET 0x4", "vtable 0x005dc450", "0xbf800000", "runtime tentacle motion behavior", "remain unproven"],
        ["cmctentacle", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["PTR_SharedVFunc__NoOpOneArg_004014c0_005dc450", "0xbf800000"],
    ),
    "0x0049cb20": target(
        "CMCTentacle__ScalarDeletingDestructor",
        "void * __thiscall CMCTentacle__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ["RET 0x4", "delete-flags", "CMCTentacle__Destructor", "runtime destruction behavior remain unproven"],
        ["cmctentacle", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CMCTentacle__Destructor", "OID__FreeObject"],
    ),
    "0x0049cb40": target(
        "CMCTentacle__Destructor",
        "void __fastcall CMCTentacle__Destructor(void * this)",
        ["register-only destructor", "vtable 0x005dc450", "+0xdc/+0xe0/+0xe4", "runtime cleanup behavior", "remain unproven"],
        ["cmctentacle", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["PTR_SharedVFunc__NoOpOneArg_004014c0_005dc450", "CMotionController__ctor_like_004bae50"],
    ),
    "0x0049cc40": target(
        "CMCTentacle__Init",
        "void __thiscall CMCTentacle__Init(void * this, void * mesh_model)",
        ["RET 0x4", "mesh_model+0x15c/+0x160", "tether/head/tethercp/headcp/tentacle/bone", "+0x2c initialized", "remain unproven"],
        ["cmctentacle", "init", "signature-corrected", "comment-hardened", "token-readback"],
        ["s_tether_0062e040", "s_tethercp_0062e00c", "s_headcp_0062e004", "s_tentacle_0062e02c"],
    ),
    "0x0049d280": target(
        "CMCTentacle__UpdateBone",
        "void __thiscall CMCTentacle__UpdateBone(void * this, float value_04, float value_08, float value_0c, float value_10, float value_14, float value_18, float value_1c, int value_20, float value_24, float value_28, float value_2c, int value_30, float value_34, float value_38, float value_3c, int value_40, int value_44, int value_48, int value_4c)",
        ["RET 0x4c", "nineteen stack dwords", "recursive", "runtime transform behavior", "remain unproven"],
        ["cmctentacle", "bone-transform", "recursive", "signature-corrected", "comment-hardened"],
        ["CMCTentacle__Init", "CMCTentacle__UpdateBone"],
    ),
    "0x0049dc90": target(
        "CMCTentacle__Factorial",
        "int __cdecl CMCTentacle__Factorial(int n)",
        ["cdecl", "one stack integer", "Bezier/spline coefficient", "overflow behavior", "remain unproven"],
        ["cmctentacle", "bezier-helper", "signature-corrected", "comment-hardened"],
        ["return", "n"],
    ),
    "0x0049dcb0": target(
        "CMCTentacle__Power",
        "float __cdecl CMCTentacle__Power(float base_value, int exponent)",
        ["cdecl", "float base", "integer exponent", "x87 float path", "remain unproven"],
        ["cmctentacle", "bezier-helper", "signature-corrected", "comment-hardened"],
        ["base_value", "exponent"],
    ),
    "0x0049dcd0": target(
        "CMCTentacle__UpdateSpline",
        "void __thiscall CMCTentacle__UpdateSpline(void * this, void * mesh_model)",
        ["RET 0x4", "cubic Bezier", "CMCTentacle__Factorial", "CMCTentacle__Power", "DAT_008a9e44", "remain unproven"],
        ["cmctentacle", "spline", "bezier", "signature-corrected", "comment-hardened"],
        ["CMCTentacle__Factorial", "CMCTentacle__Power", "CMCTentacle__BuildOrientationMatrix"],
    ),
    "0x0049e4b0": target(
        "CMCTentacle__BuildOrientationMatrix",
        "void __thiscall CMCTentacle__BuildOrientationMatrix(void * this, float dir_x, float dir_y, float dir_z, int dir_w, float up_x, float up_y, float up_z, int up_w)",
        ["RET 0x20", "eight stack dwords", "this receiver", "ECX output matrix pointer", "3x4-style basis", "remain unproven"],
        ["cmctentacle", "matrix-helper", "signature-corrected", "comment-hardened"],
        ["this", "dir_x", "up_x"],
    ),
    "0x0049e660": target(
        "CMCTentacle__VFunc_04_UpdateInterpolatedBoneTransform_0049e660",
        "void __thiscall CMCTentacle__VFunc_04_UpdateInterpolatedBoneTransform_0049e660(void * this, void * mesh_part, void * transform_a, void * transform_b, int context_value)",
        ["vtable 0x005dc450 slot 4", "RET 0x10", "CMCTentacle__UpdateSpline", "CMCTentacle__UpdateBone", "runtime tentacle transform behavior", "remain unproven"],
        ["cmctentacle", "function-boundary", "vtable-slot", "bone-transform", "signature-corrected", "comment-hardened"],
        ["CMCTentacle__UpdateSpline", "CMCTentacle__UpdateBone", "DAT_008a9e44"],
    ),
    "0x0049ead0": target(
        "CMCTentacle__VFunc_05_WriteInterpolatedBoneFloat_0049ead0",
        "void __thiscall CMCTentacle__VFunc_05_WriteInterpolatedBoneFloat_0049ead0(void * this, void * mesh_part, void * out_value)",
        ["vtable 0x005dc450 slot 5", "RET 0x8", "mesh_part+0x88", "DAT_008a9e44", "runtime bone-value behavior", "remain unproven"],
        ["cmctentacle", "function-boundary", "vtable-slot", "bone-value", "signature-corrected", "comment-hardened"],
        ["CMCTentacle__UpdateSpline", "CMCTentacle__UpdateBone"],
    ),
    "0x0049ec80": target(
        "CMCTentacle__VFunc_08_CheckCachedUpdateTime_0049ec80",
        "bool __fastcall CMCTentacle__VFunc_08_CheckCachedUpdateTime_0049ec80(void * this)",
        ["vtable 0x005dc450 slot 8", "0x00672fd0", "this+0x28", "remain unproven"],
        ["cmctentacle", "function-boundary", "vtable-slot", "state-flag", "signature-corrected", "comment-hardened"],
        ["return true", "return false"],
    ),
    "0x0049eca0": target(
        "CMeshPart__NameAvoidsTentacleOptimizationTokens",
        "bool __cdecl CMeshPart__NameAvoidsTentacleOptimizationTokens(void * mesh_part)",
        ["ESP+4", "tether/head/tethercp/headcp/tentacle", "prefix bone", "returns false", "optimization", "remain unproven"],
        ["mesh-filter", "tentacle-token-filter", "renamed", "signature-corrected", "comment-hardened", "token-readback"],
        ["s_tether_0062e040", "s_headcp_0062e004", "s_tentacle_0062e02c", "DAT_0062e090"],
    ),
    "0x0049ed30": target(
        "CMesh__HasTentacleBone",
        "bool __cdecl CMesh__HasTentacleBone(void * mesh_model)",
        ["mesh_model+0x15c", "+0x160 pointer table", "exact tentacle token", "optimization", "remain unproven"],
        ["mesh-filter", "tentacle-token-filter", "renamed", "signature-corrected", "comment-hardened", "token-readback"],
        ["s_tentacle_0062e02c", "return true", "return false"],
    ),
    "0x0049ef80": target(
        "CMCWarspiteDome__Constructor",
        "void * __thiscall CMCWarspiteDome__Constructor(void * this, void * owner_dome)",
        ["RET 0x4", "vtable 0x005dc484", "owner pointer at +0x08", "runtime dome motion behavior", "remain unproven"],
        ["cmcwarspitedome", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["PTR_SharedVFunc__NoOpOneArg_004014c0_005dc484"],
    ),
    "0x0049efa0": target(
        "CMCWarspiteDome__ScalarDeletingDestructor",
        "void * __thiscall CMCWarspiteDome__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ["RET 0x4", "delete-flags", "CMCWarspiteDome__Destructor", "runtime destruction behavior remain unproven"],
        ["cmcwarspitedome", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CMCWarspiteDome__Destructor", "OID__FreeObject"],
    ),
    "0x0049efc0": target(
        "CMCWarspiteDome__Destructor",
        "void __fastcall CMCWarspiteDome__Destructor(void * this)",
        ["register-only destructor", "vtable 0x005dc484", "clears +0x08", "runtime cleanup behavior", "remain unproven"],
        ["cmcwarspitedome", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["PTR_SharedVFunc__NoOpOneArg_004014c0_005dc484", "CMotionController__ctor_like_004bae50"],
    ),
    "0x0049efe0": target(
        "CMCWarspiteDome__VFunc_04_UpdateDomeTransform_0049efe0",
        "void __thiscall CMCWarspiteDome__VFunc_04_UpdateDomeTransform_0049efe0(void * this, void * mesh_part, void * transform_a, void * transform_b, int context_value)",
        ["vtable 0x005dc484 slot 4", "RET 0x10", "dome token", "DAT_008a9e44", "owner +0x250", "remain unproven"],
        ["cmcwarspitedome", "function-boundary", "vtable-slot", "dome-token", "signature-corrected", "comment-hardened"],
        ["DAT_0062e0cc", "DAT_008a9e44"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 14, "created": 0, "would_create": 4, "renamed": 0, "would_rename": 8, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 18, "skipped": 0, "created": 4, "would_create": 0, "renamed": 8, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_CORRECTION_APPLY = {"updated": 18, "skipped": 0, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_VERIFY_DRY = {"updated": 0, "skipped": 18, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

VTABLE_EXPECTED = {
    "0x0049e660": ("0x005dc450", "4"),
    "0x0049ead0": ("0x005dc450", "5"),
    "0x0049ec80": ("0x005dc450", "8"),
    "0x0049efe0": ("0x005dc484", "4"),
}

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

    for address, (vtable, slot) in VTABLE_EXPECTED.items():
        row = row_by_address(vtable_rows, address, key="pointer_addr")
        if row is None:
            failures.append(f"{address}: missing vtable slot row")
            continue
        if row.get("vtable") != normalize_address(vtable):
            failures.append(f"{address}: vtable mismatch {row.get('vtable')!r}")
        if row.get("slot_index") != slot:
            failures.append(f"{address}: slot mismatch {row.get('slot_index')!r}")
        if row.get("function_name") != TARGETS[address]["name"]:
            failures.append(f"{address}: vtable function mismatch {row.get('function_name')!r}")
        if row.get("status") != "OK":
            failures.append(f"{address}: vtable status mismatch {row.get('status')!r}")


def run(base: Path) -> dict[str, object]:
    failures: list[str] = []
    check_apply_log(base, "apply_dry.log", EXPECTED_DRY, failures)
    check_apply_log(base, "apply.log", EXPECTED_APPLY, failures)
    check_apply_log(base, "apply_correction.log", EXPECTED_CORRECTION_APPLY, failures)
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
