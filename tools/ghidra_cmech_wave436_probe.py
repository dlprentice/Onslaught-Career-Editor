#!/usr/bin/env python3
"""Validate Wave436 CMech / mesh-part Ghidra corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave436-cmech-current"

COMMON_TAGS = {"static-reaudit", "cmech-wave436", "retail-binary-evidence"}


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
    "0x0049f600": target(
        "CMeshPart__NameAvoidsBarrelSpinnerOptimizationTokens",
        "bool __cdecl CMeshPart__NameAvoidsBarrelSpinnerOptimizationTokens(void * mesh_part)",
        ["ESP+4", "barrel/spinner", "returns false", "optimization callers", "runtime mesh behavior", "remain unproven"],
        ["mesh-filter", "barrel-spinner-token", "renamed", "signature-corrected", "comment-hardened", "token-readback"],
        ["s_barrel_0062dd18", "s_spinner_0062e0c4", "return false"],
    ),
    "0x0049f670": target(
        "CMeshPart__AnyChildNameMatchesBarrelSpinnerOptimizationTokens",
        "bool __cdecl CMeshPart__AnyChildNameMatchesBarrelSpinnerOptimizationTokens(void * mesh_part)",
        ["+0x15c", "+0x160", "returns true", "protected child name", "remain unproven"],
        ["mesh-filter", "barrel-spinner-token", "renamed", "signature-corrected", "comment-hardened", "token-readback"],
        ["0x15c", "0x160", "s_spinner_0062e0c4"],
    ),
    "0x0049f820": target(
        "SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820",
        "void __thiscall SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820(void * this, void * init_context)",
        ["RET 0x4", "CGroundUnit__Init", "vtable slots 117/118/119", "0x005e0684", "0x005e3074", "remain unproven"],
        ["shared-ground-unit", "vtable-slot", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"],
        ["CGroundUnit__Init", "CDestroyableSegment__FindChildByNameI", "0x1d8", "0x1d4"],
    ),
    "0x0049f940": target(
        "CMech__InitLegMotion",
        "void __thiscall CMech__InitLegMotion(void * this, void * init_context)",
        ["RET 0x4", "LegMotion", "0xf0", "CMCMech__SetParams", "0.4/0.9", "remain unproven"],
        ["cmech", "leg-motion", "signature-corrected", "comment-hardened", "source-path-evidence"],
        ["s_LegMotion_00623074", "CMCMech__SetParams"],
    ),
    "0x0049fa30": target(
        "CMech__InitCockpit",
        "void __thiscall CMech__InitCockpit(void * this, void * init_context)",
        ["RET 0x4", "vtable 0x005e3074 slot 118", "CMechAI__ctor_like_004a02e0", "this+0x13c", "remain unproven"],
        ["cmech", "cockpit", "ai", "vtable-slot", "signature-corrected", "comment-hardened", "source-path-evidence"],
        ["CMechAI__ctor_like_004a02e0", "0x13c"],
    ),
    "0x0049faa0": target(
        "CMech__InitTargeting",
        "void __fastcall CMech__InitTargeting(void * this)",
        ["register-only", "slot 119", "CMechGuide__ctor_like_004a0a20", "this+0x208", "remain unproven"],
        ["cmech", "targeting", "guide", "vtable-slot", "signature-corrected", "comment-hardened", "source-path-evidence"],
        ["CMechGuide__ctor_like_004a0a20", "0x208"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 6, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 3, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 6, "skipped": 0, "created": 0, "would_create": 0, "renamed": 3, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_VERIFY_DRY = {"updated": 0, "skipped": 6, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

VTABLE_EXPECTED = {
    "0x0049f820": [("0x005e0684", "9"), ("0x005e3074", "9")],
    "0x0049f940": [("0x005e0684", "117"), ("0x005e3074", "117")],
    "0x0049fa30": [("0x005e3074", "118")],
    "0x0049faa0": [("0x005e0684", "119"), ("0x005e3074", "119")],
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


def check_vtable_rows(rows: list[dict[str, str]], address: str, failures: list[str]) -> None:
    expected_pairs = {(normalize_address(vtable), slot) for vtable, slot in VTABLE_EXPECTED.get(address, [])}
    if not expected_pairs:
        return
    name = str(TARGETS[address]["name"])
    actual_pairs: set[tuple[str, str]] = set()
    for row in rows:
        if normalize_address(row.get("pointer_addr", "")) != normalize_address(address):
            continue
        if row.get("function_name") != name:
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

        check_vtable_rows(vtable_rows, address, failures)


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
