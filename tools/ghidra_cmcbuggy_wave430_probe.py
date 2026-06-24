#!/usr/bin/env python3
"""Validate the Wave430 CMCBuggy/wheel-motion Ghidra correction."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave430-cmcbuggy-current"

COMMON_TAGS = {"static-reaudit", "cmcbuggy-wave430", "retail-binary-evidence"}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
    xref_tokens: list[str] | None = None,
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "xrefTokens": xref_tokens or [],
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00493020": target(
        "CMCBuggy__CMCBuggy",
        "void * __thiscall CMCBuggy__CMCBuggy(void * this, void * owner_model)",
        ["RET 0x4", "vtable 0x005dc250", "+0x08", "-1.0f", "runtime wheel behavior", "rebuild parity unproven"],
        ["CMotionController__ctor_like_004bae30", "0x005dc250"],
        ["cmcbuggy", "constructor", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CGroundVehicle__Init"],
    ),
    "0x00493080": target(
        "CMCBuggy__scalar_deleting_destructor",
        "void * __thiscall CMCBuggy__scalar_deleting_destructor(void * this, byte delete_flags)",
        ["RET 0x4", "delete-flags", "CMCBuggy__destructor", "OID__FreeObject", "runtime destruction behavior remain unproven"],
        ["CMCBuggy__destructor", "OID__FreeObject"],
        ["cmcbuggy", "destructor", "signature-corrected", "comment-hardened"],
    ),
    "0x004930a0": target(
        "CMCBuggy__destructor",
        "void __fastcall CMCBuggy__destructor(void * this)",
        ["RET with no stack cleanup", "vtable 0x005dc250", "+0x0c/+0x10/+0x24/+0x28/+0x2c/+0x30/+0x34/+0x38", "base motion-controller destructor"],
        ["OID__FreeObject", "CMotionController__ctor_like_004bae50"],
        ["cmcbuggy", "destructor", "signature-corrected", "comment-hardened"],
        ["CMCBuggy__scalar_deleting_destructor"],
    ),
    "0x00493180": target(
        "CMCBuggy__SetFieldC0",
        "void __thiscall CMCBuggy__SetFieldC0(void * this, int field_c0_value)",
        ["RET 0x4", "writes that value to CMCBuggy offset +0xc0", "old SetC0 label", "field purpose", "unproven"],
        ["+ 0xc0"],
        ["cmcbuggy", "field-setter", "renamed", "signature-corrected", "comment-hardened"],
        ["CGroundVehicle__Init"],
    ),
    "0x00493190": target(
        "CMCBuggy__Init",
        "void __thiscall CMCBuggy__Init(void * this, void * mesh_model)",
        ["RET 0x4", "WheelBase", "WheelMotion", "-1.0f", "cached wheel motion pose data", "runtime wheel initialization", "rebuild parity remain unproven"],
        ["WheelBase", "WheelMotion", "CMCBuggy__Init"],
        ["cmcbuggy", "wheel-motion", "signature-corrected", "comment-hardened", "token-readback"],
        ["CMCBuggy__UpdateWheel"],
    ),
    "0x004934f0": target(
        "CMCBuggy__UpdateWheel",
        "void __thiscall CMCBuggy__UpdateWheel(void * this, float position_x, float position_y, float position_z, float position_w, float basis0_x, float basis0_y, float basis0_z, int basis0_w, float basis1_x, float basis1_y, float basis1_z, int basis1_w, float basis2_x, float basis2_y, float basis2_z, int basis2_w, void * owner_vehicle, void * mesh_part_owner, int wheel_index, int context_value)",
        ["RET 0x50", "twenty stack arguments", "WheelBase/WheelMotion", "heightfield normals", "recurses through child wheel parts", "runtime vehicle behavior", "rebuild parity remain unproven"],
        ["CMCBuggy__Init", "WheelBase", "WheelMotion", "CMCBuggy__UpdateWheel"],
        ["cmcbuggy", "wheel-motion", "signature-corrected", "comment-hardened", "token-readback"],
    ),
    "0x00494310": target(
        "CMCBuggy__ProfileEnd",
        "void __fastcall CMCBuggy__ProfileEnd(void * profile_scope)",
        ["RET with no stack cleanup", "rdtsc", "DAT_0082ce84", "DAT_0082d054", "runtime timing coverage remain unproven"],
        ["rdtsc", "DAT_0082ce84", "DAT_0082d054"],
        ["cmcbuggy", "profiling", "signature-corrected", "comment-hardened"],
    ),
    "0x00494350": target(
        "Mat34__InvertBasisToOut",
        "void __thiscall Mat34__InvertBasisToOut(void * this, void * out_matrix)",
        ["owner/name correction", "ECX/source matrix pointer", "CDXEngine", "CMCBuggy", "other mesh/math callers", "Vec3__DivideInPlaceByScalar", "singular-matrix behavior", "unproven"],
        ["Vec3__DivideInPlaceByScalar", "out_matrix", "this"],
        ["math-helper", "owner-corrected", "renamed", "signature-corrected", "comment-hardened", "multi-caller"],
        ["CDXEngine__BuildDirectionalSampleRing", "CMCBuggy__UpdateWheel"],
    ),
    "0x004944b0": target(
        "Vec3__DivideInPlaceByScalar",
        "void __thiscall Vec3__DivideInPlaceByScalar(void * this, float scalar)",
        ["owner/name correction", "ECX/vector pointer", "CMeshPart", "CMeshRenderer", "CMCMech", "CPDSimpleSprite", "shared vector helper", "divide-by-zero handling", "unproven"],
        ["this", "scalar", "/ scalar"],
        ["math-helper", "owner-corrected", "renamed", "signature-corrected", "comment-hardened", "multi-caller"],
        ["CMeshPart__Merge", "CMeshRenderer__RenderMeshCore", "CMCMech__UpdateBone"],
    ),
    "0x00494b00": target(
        "CMeshPart__NameAvoidsBodyAxleWheelTokens",
        "bool __cdecl CMeshPart__NameAvoidsBodyAxleWheelTokens(void * mesh_part)",
        ["Body", "Axle", "Wheel", "returns false", "older backward NameMatchesWheelTokenSet label", "optimization-policy meaning", "unproven"],
        ["Body", "Axle", "Wheel"],
        ["mesh-filter", "token-readback", "renamed", "signature-corrected", "comment-hardened"],
        ["CMeshPart__CanOptimizePart_Strict", "CMeshPart__CanMergeInOptimizePass"],
    ),
    "0x00494b50": target(
        "CMeshPart__HasWheelMotionAnimation",
        "bool __cdecl CMeshPart__HasWheelMotionAnimation(void * mesh_part)",
        ["[ESP+4]", "WheelMotion", "FindAnimationIndex", "RET with no stack cleanup", "animation-table layout", "unproven"],
        ["WheelMotion", "FindAnimationIndex"],
        ["mesh-filter", "wheel-motion", "token-readback", "renamed", "signature-corrected", "comment-hardened"],
        ["CMesh__HasSpecialOptimizationConstraints"],
    ),
    "0x00494c60": target(
        "CDestructableSegmentsMotionController__Ctor",
        "void * __thiscall CDestructableSegmentsMotionController__Ctor(void * this, void * segment_controller)",
        ["RET 0x4", "earlier two-stack-argument signature was too wide", "vtable 0x005dc27c", "CMCHiveBoss__ctor_like_00497090", "exact class ownership/layout", "unproven"],
        ["0x005dc27c", "+ 0xc", "+ 8"],
        ["destructable-segments", "constructor", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CMCHiveBoss__ctor_like_00497090"],
    ),
    "0x00494ca0": target(
        "CDestructableSegmentsMotionController__ScalarDeletingDestructor",
        "void * __thiscall CDestructableSegmentsMotionController__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ["RET 0x4", "0x005dc27c slot 1", "older CMCBuggy wheel-specific owner label was too narrow", "conditionally frees this", "exact class ownership", "unproven"],
        ["CDestructableSegmentsMotionController__Destructor", "OID__FreeObject"],
        ["destructable-segments", "destructor", "owner-corrected", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
    ),
    "0x00494cc0": target(
        "CDestructableSegmentsMotionController__Destructor",
        "void __fastcall CDestructableSegmentsMotionController__Destructor(void * this)",
        ["vtable 0x005dc27c", "clears +0x08/+0x0c", "older CMCBuggy wheel-specific owner label too narrow", "duplicated destructor-like body at 0x00497130", "unproven"],
        ["0x005dc27c", "CMotionController__ctor_like_004bae50"],
        ["destructable-segments", "destructor", "owner-corrected", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
    ),
    "0x00494ce0": target(
        "CDestructableSegmentsMotionController__ApplyRumbleTransform",
        "void __thiscall CDestructableSegmentsMotionController__ApplyRumbleTransform(void * this, void * state_context, void * segment_state, void * transform)",
        ["RET 0x10", "0x005dc27c slot 4", "trigonometric rotation", "Mat34 rows", "clears the pointed source flag", "runtime rumble behavior", "rebuild parity remain unproven"],
        ["Mat34__SetRows", "state_context", "segment_state", "transform"],
        ["destructable-segments", "rumble-transform", "owner-corrected", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 15, "renamed": 0, "would_rename": 9, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 15, "skipped": 0, "renamed": 9, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_FIX_DRY = {"updated": 0, "skipped": 15, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_FIX_APPLY = {"updated": 15, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

INSTRUCTION_RETURNS = {
    "0x00493020": "0x4",
    "0x00493080": "0x4",
    "0x004930a0": "",
    "0x00493180": "0x4",
    "0x00493190": "0x4",
    "0x004934f0": "0x50",
    "0x00494310": "",
    "0x00494350": "0x4",
    "0x004944b0": "0x4",
    "0x00494b00": "",
    "0x00494b50": "",
    "0x00494c60": "0x4",
    "0x00494ca0": "0x4",
    "0x00494ce0": "0x10",
}

EXPECTED_TAIL_CALLS = {
    "0x00494cc0": ("JMP", "0x004bae50"),
}

EXPECTED_STRINGS = {
    "0062dca0": "WheelBase",
    "0062cb54": "WheelMotion",
    "0062dcac": "Wheel",
    "0062dcb4": "Axle",
    "0062dcbc": "Body",
    "0062dc80": "C:\\dev\\ONSLAUGHT2\\MCBuggy.cpp",
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime wheel behavior proven",
    "runtime rumble behavior proven",
    "runtime destruction behavior proven",
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


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry"):
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


def rows_by_address(rows: list[dict[str, str]], address: str, key: str = "target_addr") -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get(key, "")) == wanted]


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "decompile_after"
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    return "\n".join(read_text(path) for path in matches)


def parse_summary(log_text: str) -> dict[str, int] | None:
    match = re.search(
        r"SUMMARY:\s+updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def check_apply_log(base: Path, filename: str, expected: dict[str, int], failures: list[str]) -> None:
    log_text = read_text(base / filename)
    if not log_text:
        failures.append(f"missing {filename}")
        return
    if "LockException" in log_text or "FAIL:" in log_text:
        failures.append(f"{filename} contains LockException or FAIL")
    summary = parse_summary(log_text)
    if summary != expected:
        failures.append(f"{filename} summary mismatch: expected {expected}, got {summary}")


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "metadata_after.tsv")
    tags = read_tsv(base / "tags_after.tsv")
    xrefs = read_tsv(base / "xrefs_before.tsv")

    if len(metadata) < len(TARGETS):
        failures.append(f"metadata_after.tsv has {len(metadata)} rows, expected at least {len(TARGETS)}")
    if len(tags) < len(TARGETS):
        failures.append(f"tags_after.tsv has {len(tags)} rows, expected at least {len(TARGETS)}")

    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"missing metadata row for {address}")
            continue
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status is {row.get('status')}")
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name mismatch: {row.get('name')} != {spec['name']}")
        if compact(row.get("signature", "")) != compact(str(spec["signature"])):
            failures.append(f"{address} signature mismatch: {row.get('signature')} != {spec['signature']}")

        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address} comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address} comment overclaims with token {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"missing tags row for {address}")
        else:
            tag_text = tag_row.get("tags", "")
            for tag in spec["tags"]:  # type: ignore[index]
                if tag not in tag_text:
                    failures.append(f"{address} missing tag {tag!r}")

        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"missing decompile_after text for {address}")
        else:
            for token in spec["decompileTokens"]:  # type: ignore[index]
                if not token_present(decompile, str(token)):
                    failures.append(f"{address} decompile missing token {token!r}")

        if spec["xrefTokens"]:  # type: ignore[index]
            xref_text = "\n".join(str(row) for row in rows_by_address(xrefs, address))
            for token in spec["xrefTokens"]:  # type: ignore[index]
                if not token_present(xref_text, str(token)):
                    failures.append(f"{address} xrefs missing token {token!r}")


def check_returns(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "instructions_before.tsv")
    updatewheel_rows = read_tsv(base / "instructions_updatewheel_full.tsv")
    combined = rows + updatewheel_rows
    for address, ret_operand in INSTRUCTION_RETURNS.items():
        wanted = normalize_address(address)
        ret_rows = [
            row for row in combined
            if row.get("function_entry") == wanted and row.get("mnemonic") == "RET"
        ]
        if not ret_rows:
            failures.append(f"{address} missing RET instruction evidence")
            continue
        if ret_operand and all(compact(row.get("operands", "")) != compact(ret_operand) for row in ret_rows):
            failures.append(f"{address} missing RET {ret_operand} evidence")

    for address, (mnemonic, operand) in EXPECTED_TAIL_CALLS.items():
        wanted = normalize_address(address)
        if not any(
            row.get("function_entry") == wanted
            and row.get("mnemonic") == mnemonic
            and compact(row.get("operands", "")) == compact(operand)
            for row in combined
        ):
            failures.append(f"{address} missing {mnemonic} {operand} tail-call evidence")


def check_tokens_and_vtables(base: Path, failures: list[str]) -> None:
    for address, expected_text in EXPECTED_STRINGS.items():
        rows = read_tsv(base / f"string_{address}.tsv")
        if not rows or not token_present(rows[0].get("cstring", ""), expected_text):
            failures.append(f"string_{address}.tsv missing {expected_text!r}")

    vtable_rows = read_tsv(base / "vtables_before.tsv")
    wanted_slots = {
        ("005dc250", "1", "00493080"),
        ("005dc250", "4", "004944d0"),
        ("005dc250", "5", "00494940"),
        ("005dc27c", "1", "00494ca0"),
        ("005dc27c", "4", "00494ce0"),
        ("005dc27c", "6", "00494fa0"),
        ("005dc27c", "8", "00495020"),
    }
    present = {
        (
            row.get("vtable", "").lower(),
            row.get("slot_index", ""),
            row.get("pointer_addr", "").lower(),
        )
        for row in vtable_rows
    }
    for slot in wanted_slots:
        if slot not in present:
            failures.append(f"missing vtable slot evidence {slot}")


def run(base: Path) -> dict[str, object]:
    failures: list[str] = []
    check_apply_log(base, "apply_dry.log", EXPECTED_DRY, failures)
    check_apply_log(base, "apply.log", EXPECTED_APPLY, failures)
    check_apply_log(base, "apply_fix_dry.log", EXPECTED_FIX_DRY, failures)
    check_apply_log(base, "apply_fix.log", EXPECTED_FIX_APPLY, failures)
    check_metadata(base, failures)
    check_returns(base, failures)
    check_tokens_and_vtables(base, failures)

    return {
        "schema": "ghidra-cmcbuggy-wave430-probe.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "base": str(base),
        "status": "PASS" if not failures else "FAIL",
        "targetCount": len(TARGETS),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run(args.base)
    out_path = args.base / "cmcbuggy-wave430-probe.json"
    args.base.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if args.check and result["status"] != "PASS":
        print(json.dumps(result, indent=2), file=sys.stderr)
        return 1

    print(f"{result['status']} ghidra-cmcbuggy-wave430 targetCount={result['targetCount']} failures={len(result['failures'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
