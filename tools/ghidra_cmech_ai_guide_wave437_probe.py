#!/usr/bin/env python3
"""Validate Wave437 CMechAI/CMechGuide Ghidra corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave437-cmech-ai-guide-current"

COMMON_TAGS = {"static-reaudit", "cmech-ai-guide-wave437", "retail-binary-evidence"}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 11,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str] | None = None,
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens or [],
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00499e30": target(
        "CMCMech__UpdateBone",
        "void __thiscall CMCMech__UpdateBone(void * this, float * position, float * matrix, void * mesh_part, void * pose_arg_a, void * pose_arg_b, float blend_a, float blend_b)",
        ["CMCMech__Reset", "mesh_part+0x128", "pose/matrix caches", "remain unproven"],
        ["cmcmech", "bone-update", "signature-corrected", "comment-hardened"],
        ["CMCMech__UpdateBone", "float * position", "mesh_part"],
    ),
    "0x0049fc10": target(
        "SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10",
        "void __fastcall SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10(void * this)",
        ["0x005e0684", "0x005e3074", "slot 66", "creates a pickup", "remain unproven"],
        ["shared-ground-unit", "vtable-slot-66", "owner-corrected", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CGroundUnit__UpdateLinkedEffectsByHeightClearance", "CWorldPhysicsManager__CreatePickup"],
    ),
    "0x0049fdb0": target(
        "SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0",
        "void __fastcall SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0(void * this)",
        ["slot 71", "0x005e0fe0", "Generic Mesh", "CMCMech__BuildInterpolatedPoseAndAnchor", "remain unproven"],
        ["shared-ground-unit", "vtable-slot-71", "mesh-effects", "owner-corrected", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["s_Generic_Mesh", "CMCMech__BuildInterpolatedPoseAndAnchor"],
    ),
    "0x004a02e0": target(
        "CMechAI__ctor",
        "void * __thiscall CMechAI__ctor(void * this, void * owner_unit, void * init_context, int reserved_arg)",
        ["CMech__InitCockpit", "0x64", "0x005dc4c0", "+0x60", "remain unproven"],
        ["cmech-ai", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CMechAI__ctor", "Random__NextLCGAbs"],
    ),
    "0x004a0390": target(
        "CMechAI__scalar_deleting_dtor",
        "void * __thiscall CMechAI__scalar_deleting_dtor(void * this, byte flags)",
        ["0x005dc4c0 slot 1", "CUnitAI__dtor_base", "flags byte", "remain unproven"],
        ["cmech-ai", "destructor", "scalar-deleting-dtor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CUnitAI__dtor_base", "OID__FreeObject"],
    ),
    "0x004a03b0": target(
        "CUnitAI__dtor_base",
        "void __fastcall CUnitAI__dtor_base(void * this)",
        ["0x005d8d1c", "+0x28", "+0x24", "+0x0c", "remain unproven"],
        ["unit-ai", "destructor", "dtor-base", "renamed", "signature-corrected", "comment-hardened"],
        ["CSPtrSet__Remove", "CMonitor__Shutdown"],
    ),
    "0x004a0a20": target(
        "CMechGuide__ctor",
        "void * __thiscall CMechGuide__ctor(void * this, void * owner_unit, void * reserved_arg)",
        ["CMech__InitTargeting", "0x48", "0x005dc4f4", "event 2000", "remain unproven"],
        ["cmech-guide", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CGuide__ctor_base", "CEventManager__AddEvent_AtTime"],
    ),
    "0x004a0b10": target(
        "CMechGuide__scalar_deleting_dtor",
        "void * __thiscall CMechGuide__scalar_deleting_dtor(void * this, byte flags)",
        ["0x005dc4f4 slot 1", "CMechGuide__dtor_base", "flags byte", "remain unproven"],
        ["cmech-guide", "destructor", "scalar-deleting-dtor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CMechGuide__dtor_base", "OID__FreeObject"],
    ),
    "0x004a0b30": target(
        "CMechGuide__dtor_base",
        "void __fastcall CMechGuide__dtor_base(void * this)",
        ["+0x44", "+0x3c", "+0x34", "CMonitor__Shutdown", "remain unproven"],
        ["cmech-guide", "destructor", "dtor-base", "renamed", "signature-corrected", "comment-hardened"],
        ["CSPtrSet__Remove", "OID__FreeObject"],
    ),
    "0x004a0bc0": target(
        "CMechGuide__VFunc_03_UpdateGuidanceState_004a0bc0",
        "void __fastcall CMechGuide__VFunc_03_UpdateGuidanceState_004a0bc0(void * this)",
        ["0x005dc4f4 slot 3", "+0x44", "owner+0x13c", "+0x34/+0x3c", "remain unproven"],
        ["cmech-guide", "vtable-slot-03", "guidance", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CExplosionInitThing__ClearCostGridBoundsAndBuildPath", "CMechGuide__VFunc_03_UpdateGuidanceState_004a0bc0"],
    ),
    "0x004a1270": target(
        "CMechGuide__SelectNearestHostileTargetReader",
        "void __fastcall CMechGuide__SelectNearestHostileTargetReader(void * this)",
        ["+0x44", "CMapWho", "nearest hostile reader", "remain unproven"],
        ["cmech-guide", "target-selection", "active-reader", "renamed", "signature-corrected", "comment-hardened"],
        ["CMapWho__GetFirstEntryWithinRadius", "CGenericActiveReader__SetReader"],
    ),
}

VTABLE_EXPECTED = {
    "0x0049fc10": [("0x005e0684", "66"), ("0x005e3074", "66")],
    "0x0049fdb0": [("0x005e0684", "71"), ("0x005e3074", "71"), ("0x005e0fe0", "71"), ("0x005e0b30", "71")],
    "0x004a0390": [("0x005dc4c0", "1")],
    "0x004a0b10": [("0x005dc4f4", "1")],
    "0x004a0bc0": [("0x005dc4f4", "3")],
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully re'ed",
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
        for key in ("address", "vtable", "pointer_addr", "function_entry"):
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
    return read_text(matches[0]) if matches else ""


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ["updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def check_verify_log(base: Path, failures: list[str]) -> None:
    text = read_text(base / "apply_verify_dry.log")
    if not text:
        failures.append("apply_verify_dry.log: missing or empty")
        return
    summary = parse_summary(text)
    if summary != EXPECTED_VERIFY_DRY:
        failures.append(f"apply_verify_dry.log: summary mismatch expected {EXPECTED_VERIFY_DRY}, got {summary}")
    for token in ("FAIL:", "Exception", "LockException"):
        if token in text:
            failures.append(f"apply_verify_dry.log: unexpected failure token {token!r}")
    if "REPORT: Save succeeded" not in text:
        failures.append("apply_verify_dry.log: missing Ghidra save-success marker")


def check_vtable_rows(rows: list[dict[str, str]], address: str, failures: list[str]) -> None:
    expected_pairs = {(normalize_address(vtable), slot) for vtable, slot in VTABLE_EXPECTED.get(address, [])}
    if not expected_pairs:
        return
    expected_name = str(TARGETS[address]["name"])
    actual_pairs: set[tuple[str, str]] = set()
    for row in rows:
        if normalize_address(row.get("pointer_addr", "")) != normalize_address(address):
            continue
        if row.get("function_name") != expected_name:
            failures.append(f"{address}: vtable function mismatch {row.get('function_name')!r}")
        if row.get("status") != "OK":
            failures.append(f"{address}: vtable status mismatch {row.get('status')!r}")
        actual_pairs.add((normalize_address(row.get("vtable", "")), row.get("slot_index", "")))
    missing = sorted(expected_pairs - actual_pairs)
    if missing:
        failures.append(f"{address}: missing vtable rows {missing}")


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "metadata_after.tsv")
    tags = read_tsv(base / "tags_after.tsv")
    vtable_rows = read_tsv(base / "vtable_slots_ground_after.tsv") + read_tsv(base / "vtable_slots_ai_guide_after.tsv")

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
            missing_tags = sorted(set(spec["tags"]) - actual_tags)  # type: ignore[arg-type]
            if missing_tags:
                failures.append(f"{address}: missing tags {missing_tags}")

        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing decompile_after")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")

        check_vtable_rows(vtable_rows, address, failures)


def run(base: Path) -> dict[str, object]:
    failures: list[str] = []
    check_verify_log(base, failures)
    check_metadata(base, failures)
    return {
        "status": "PASS" if not failures else "FAIL",
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "base": str(base.relative_to(ROOT)) if base.is_relative_to(ROOT) else str(base),
        "targetCount": len(TARGETS),
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    base = args.base if args.base.is_absolute() else ROOT / args.base
    result = run(base)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Wave437 CMechAI/CMechGuide probe: {result['status']}")
        print(f"Base: {result['base']}")
        print(f"Targets: {result['targetCount']}")
        for failure in result["failures"]:  # type: ignore[index]
            print(f"- {failure}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
