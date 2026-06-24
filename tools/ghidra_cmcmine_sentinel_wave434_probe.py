#!/usr/bin/env python3
"""Validate Wave434 CMCMine / CMCSentinel Ghidra corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave434-cmcmine-current"

COMMON_TAGS = {"static-reaudit", "cmcmine-sentinel-wave434", "retail-binary-evidence"}


def target(name: str, signature: str, comment_tokens: list[str], tags: list[str], decompile_tokens: list[str] | None = None) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens or [],
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0049c3e0": target(
        "CMCMine__Constructor",
        "void * __thiscall CMCMine__Constructor(void * this, void * owner_mine)",
        ["RET 0x4", "vtable 0x005dc3f4", "owner pointer at +0x08", "runtime mine motion behavior", "remain unproven"],
        ["cmcmine", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["PTR_SharedVFunc__NoOpOneArg_004014c0_005dc3f4"],
    ),
    "0x0049c400": target(
        "CMCMine__ScalarDeletingDestructor",
        "void * __thiscall CMCMine__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ["RET 0x4", "delete-flags", "CMCMine__Destructor", "runtime destruction behavior remain unproven"],
        ["cmcmine", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CMCMine__Destructor", "OID__FreeObject"],
    ),
    "0x0049c420": target(
        "CMCMine__Destructor",
        "void __fastcall CMCMine__Destructor(void * this)",
        ["register-only destructor", "vtable 0x005dc3f4", "0xc7c34ff3", "runtime cleanup behavior", "remain unproven"],
        ["cmcmine", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["0xc7c34ff3", "CMotionController__ctor_like_004bae50"],
    ),
    "0x0049c440": target(
        "CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440",
        "void __thiscall CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440(void * this, void * mesh_part, void * transform_a, void * transform_b, int context_value)",
        ["vtable 0x005dc3f4 slot 4", "RET 0x10", "+0x250/+0x254", "runtime mine height behavior", "remain unproven"],
        ["cmcmine", "vtable-slot", "height-cache", "renamed", "signature-corrected", "comment-hardened"],
        ["0x254", "0x250"],
    ),
    "0x0049c4b0": target(
        "CMCMine__VFunc_08_CheckCachedHeightState_0049c4b0",
        "bool __fastcall CMCMine__VFunc_08_CheckCachedHeightState_0049c4b0(void * this)",
        ["recovered function boundary", "vtable 0x005dc3f4 slot 8", "owner +0x250", "runtime state semantics", "remain unproven"],
        ["cmcmine", "function-boundary", "vtable-slot", "height-cache", "signature-corrected", "comment-hardened"],
        ["0x250", "return false"],
    ),
    "0x0049c5d0": target(
        "CMCSentinel__Constructor",
        "void * __thiscall CMCSentinel__Constructor(void * this, void * owner_sentinel)",
        ["RET 0x4", "vtable 0x005dc420", "0xc479c000", "runtime sentinel motion behavior", "remain unproven"],
        ["cmcsentinel", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["PTR_SharedVFunc__NoOpOneArg_004014c0_005dc420", "0xc479c000"],
    ),
    "0x0049c600": target(
        "CMCSentinel__ScalarDeletingDestructor",
        "void * __thiscall CMCSentinel__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ["RET 0x4", "delete-flags", "CMCSentinel__Destructor", "runtime destruction behavior remain unproven"],
        ["cmcsentinel", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CMCSentinel__Destructor", "OID__FreeObject"],
    ),
    "0x0049c620": target(
        "CMCSentinel__Destructor",
        "void __fastcall CMCSentinel__Destructor(void * this)",
        ["register-only destructor", "vtable 0x005dc420", "runtime cleanup behavior", "remain unproven"],
        ["cmcsentinel", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["PTR_SharedVFunc__NoOpOneArg_004014c0_005dc420", "CMotionController__ctor_like_004bae50"],
    ),
    "0x0049c640": target(
        "CMCSentinel__VFunc_04_UpdateX1TurretOrBarrelTransform_0049c640",
        "void __thiscall CMCSentinel__VFunc_04_UpdateX1TurretOrBarrelTransform_0049c640(void * this, void * mesh_part, void * transform_a, void * transform_b, int context_value)",
        ["recovered function boundary", "vtable 0x005dc420 slot 4", "RET 0x10", "X1 turret", "X1 barrel", "runtime sentinel transform behavior", "remain unproven"],
        ["cmcsentinel", "function-boundary", "vtable-slot", "x1-turret-token", "x1-barrel-token", "signature-corrected", "comment-hardened"],
        ["s_X1_turret_0062dfc8", "s_X1_barrel_0062dfbc", "CMCBuggy__StrnICmpWithLocaleLock"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 7, "created": 0, "would_create": 2, "renamed": 0, "would_rename": 7, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 9, "skipped": 0, "created": 2, "would_create": 0, "renamed": 7, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_VERIFY_DRY = {"updated": 0, "skipped": 9, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

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

    for address in ("0x0049c4b0", "0x0049c640"):
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
