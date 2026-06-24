#!/usr/bin/env python3
"""Validate Wave432 CMCGroundAttack / CMCHiveBoss Ghidra corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave432-cmcgroundattack-hiveboss-current"

COMMON_TAGS = {"static-reaudit", "cmcgroundattack-hiveboss-wave432", "retail-binary-evidence"}


def target(name: str, signature: str, comment_tokens: list[str], tags: list[str], decompile_tokens: list[str] | None = None) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens or [],
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004964d0": target(
        "CMCGroundAttack__Constructor",
        "void * __thiscall CMCGroundAttack__Constructor(void * this, void * owner_aircraft)",
        ["RET 0x4", "vtable 0x005dc330", "owner pointer at +0x08", "runtime ground-attack motion behavior", "remain unproven"],
        ["cmcgroundattack", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["0xc479c000", "PTR_SharedVFunc__NoOpOneArg_004014c0_005dc330"],
    ),
    "0x00496500": target(
        "CMCGroundAttack__ScalarDeletingDestructor",
        "void * __thiscall CMCGroundAttack__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ["RET 0x4", "delete-flags", "CMCGroundAttack__Destructor", "runtime destruction behavior remain unproven"],
        ["cmcgroundattack", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CMCGroundAttack__Destructor", "OID__FreeObject"],
    ),
    "0x00496520": target(
        "CMCGroundAttack__Destructor",
        "void __fastcall CMCGroundAttack__Destructor(void * this)",
        ["register-only destructor", "vtable 0x005dc330", "clears", "+0x08", "runtime cleanup behavior", "remain unproven"],
        ["cmcgroundattack", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["PTR_SharedVFunc__NoOpOneArg_004014c0_005dc330", "CMotionController__ctor_like_004bae50"],
    ),
    "0x00496540": target(
        "CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540",
        "void __thiscall CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540(void * this, void * mesh_part, void * transform_a, void * transform_b, int context_value)",
        ["recovered function boundary", "vtable 0x005dc330 slot 4", "RET 0x10", "turret", "runtime transform behavior", "remain unproven"],
        ["cmcgroundattack", "function-boundary", "vtable-slot", "turret-token", "signature-corrected", "comment-hardened"],
        ["DAT_0062dd20", "Vec3__NormalizeInPlace", "CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540"],
    ),
    "0x004968a0": target(
        "CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0",
        "bool __fastcall CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0(void * this)",
        ["recovered function boundary", "vtable 0x005dc330 slot 8", "compares owner fields", "this+0x0c/+0x10", "runtime state semantics", "remain unproven"],
        ["cmcgroundattack", "function-boundary", "vtable-slot", "state-cache", "signature-corrected", "comment-hardened"],
        ["0x284", "0x10", "return false"],
    ),
    "0x004968f0": target(
        "CMeshPart__NameIsNotTurret",
        "bool __cdecl CMeshPart__NameIsNotTurret(void * mesh_part)",
        ["token at 0x0062dd20", "turret", "name at +0xdc", "optimization-policy meaning", "runtime behavior", "remain unproven"],
        ["mesh-filter", "turret-token", "renamed", "signature-corrected", "comment-hardened"],
        ["DAT_0062dd20", "stricmp"],
    ),
    "0x00496910": target(
        "CMeshPart__AnySubPartNameIsTurret",
        "bool __cdecl CMeshPart__AnySubPartNameIsTurret(void * mesh_part)",
        ["token at 0x0062dd20", "child count", "+0x15c", "child pointer table", "+0x160", "optimization-policy meaning", "runtime behavior", "remain unproven"],
        ["mesh-filter", "turret-token", "renamed", "signature-corrected", "comment-hardened"],
        ["0x15c", "0x160", "DAT_0062dd20"],
    ),
    "0x00496f60": target(
        "CMeshPart__NameAvoidsTurretAndBarrelPrefix",
        "bool __cdecl CMeshPart__NameAvoidsTurretAndBarrelPrefix(void * mesh_part)",
        ["turret", "barrel", "strn", "optimization-policy meaning", "runtime behavior", "remain unproven"],
        ["mesh-filter", "turret-token", "barrel-token", "renamed", "signature-corrected", "comment-hardened"],
        ["s_barrel_0062dd18", "DAT_0062dd20"],
    ),
    "0x00497090": target(
        "CMCHiveBoss__Constructor",
        "void * __thiscall CMCHiveBoss__Constructor(void * this, void * owner_hiveboss)",
        ["RET 0x4", "owner_hiveboss+0x178", "vtable 0x005dc388", "runtime HiveBoss motion behavior", "remain unproven"],
        ["cmchiveboss", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CDestructableSegmentsMotionController__Ctor", "PTR_SharedVFunc__NoOpOneArg_004014c0_005dc388"],
    ),
    "0x00497110": target(
        "CMCHiveBoss__ScalarDeletingDestructor",
        "void * __thiscall CMCHiveBoss__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ["RET 0x4", "delete-flags", "DestructorThunk", "runtime destruction behavior remain unproven"],
        ["cmchiveboss", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CDestructableSegmentsMotionController__DestructorThunk_00497130", "OID__FreeObject"],
    ),
    "0x004976d0": target(
        "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0",
        "void __thiscall CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0(void * this, void * mesh_part, void * transform_a, void * transform_b, int context_value)",
        ["recovered function boundary", "vtable 0x005dc388 slot 4", "RET 0x10", "CacheNamedCollisionCylinders", "ApplyRumbleTransform", "runtime cylinder behavior", "remain unproven"],
        ["cmchiveboss", "function-boundary", "vtable-slot", "collision-cylinder-cache", "signature-corrected", "comment-hardened"],
        ["CDestructableSegmentsMotionController__CacheNamedCollisionCylinders", "CDestructableSegmentsMotionController__ApplyRumbleTransform", "Mat34__OrthonormalizeAxes"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 8, "created": 0, "would_create": 3, "renamed": 0, "would_rename": 8, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 11, "skipped": 0, "created": 3, "would_create": 0, "renamed": 8, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_VERIFY_DRY = {"updated": 0, "skipped": 11, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

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

    for address in ("0x00496540", "0x004968a0", "0x004976d0"):
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
