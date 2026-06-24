#!/usr/bin/env python3
"""Validate Wave441 CMenuItemDropdown/CMenuItemSlider Ghidra metadata."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave441-menuitem-dropdown-slider-current"

COMMON_TAGS = {"static-reaudit", "menuitem-wave441", "retail-binary-evidence"}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 14,
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
    "0x004a3b10": target(
        "CMenuItemDropdown__Init",
        "void * __thiscall CMenuItemDropdown__Init(void * this, int text_id, int item_id, byte defer_commit)",
        ["vtable 0x005dc578", "RET 0x0c", "source MenuItem.cpp body is absent"],
        ["cmenuitemdropdown", "frontend-menu", "dropdown", "init", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["PTR_VFuncSlot_00_004d0490_005dc578", "0xffd6d6d6"],
    ),
    "0x004a3b50": target(
        "CMenuItemDropdown__UpdateSelection",
        "void __thiscall CMenuItemDropdown__UpdateSelection(void * this)",
        ["vtable slot 12", "vtable+0x3c", "+0x1c"],
        ["cmenuitemdropdown", "frontend-menu", "dropdown", "selection", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["+ 0x3c", "((int)this + 0x1c)", "((int)this + 0x20)"],
    ),
    "0x004a3b60": target(
        "CMenuItemDropdown__InitVariant",
        "void * __thiscall CMenuItemDropdown__InitVariant(void * this, int text_id, int item_id, byte defer_commit)",
        ["vtable 0x005dc5c4", "Localization__GetYesNoString", "source MenuItem.cpp body is absent"],
        ["cmenuitemdropdown", "frontend-menu", "dropdown", "init", "variant", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["PTR_VFuncSlot_00_004d0490_005dc5c4", "0xffd6d6d6"],
    ),
    "0x004a3ba0": target(
        "CMenuItemDropdown__ClearPending",
        "void __cdecl CMenuItemDropdown__ClearPending(void)",
        ["DAT_0070486c", "CMenuItemRange__Render", "source MenuItem.cpp body is absent"],
        ["cmenuitemdropdown", "frontend-menu", "dropdown", "deferred-render", "signature-corrected", "comment-hardened", "source-absent"],
        ["DAT_0070486c = 0"],
    ),
    "0x004a3bb0": target(
        "CMenuItemDropdown__ProcessPending",
        "void __cdecl CMenuItemDropdown__ProcessPending(void)",
        ["DAT_0070486c", "queued-pass flag 1", "source MenuItem.cpp body is absent"],
        ["cmenuitemdropdown", "frontend-menu", "dropdown", "deferred-render", "signature-corrected", "comment-hardened", "source-absent"],
        ["CMenuItemDropdown__Render", "DAT_00704870", "DAT_00704874"],
    ),
    "0x004a3be0": target(
        "CMenuItemDropdown__RenderOrQueueDeferred",
        "void __thiscall CMenuItemDropdown__RenderOrQueueDeferred(void * this, float x, float y, int interactive)",
        ["vtable slot 4", "DAT_0070486c", "source MenuItem.cpp body is absent"],
        ["cmenuitemdropdown", "frontend-menu", "dropdown", "render", "deferred-render", "vtable-backed", "comment-hardened", "source-absent"],
        ["DAT_00704874 = x", "DAT_00704870 = y", "CMenuItemDropdown__Render"],
    ),
    "0x004a3c30": target(
        "CMenuItemDropdown__Render",
        "void __thiscall CMenuItemDropdown__Render(void * this, float x, float y, int queued_pass)",
        ["RET 0x0c", "queued-pass flag", "CFrontEnd__GetClickStateInRect"],
        ["cmenuitemdropdown", "frontend-menu", "dropdown", "render", "deferred-render", "mouse-input", "signature-corrected", "comment-hardened", "source-absent"],
        ["CFrontEnd__GetCursorStateInRect", "CFrontEnd__GetClickStateInRect", "queued_pass"],
    ),
    "0x004a40e0": target(
        "CMenuItemDropdown__IsExpanded",
        "byte __thiscall CMenuItemDropdown__IsExpanded(void * this)",
        ["vtable slots 8/9", "+0x24", "source MenuItem.cpp body is absent"],
        ["cmenuitemdropdown", "frontend-menu", "dropdown", "state-query", "vtable-backed", "comment-hardened", "source-absent"],
        ["return *(byte *)((int)this + 0x24)"],
    ),
    "0x004a40f0": target(
        "CMenuItemDropdown__CommitSelection",
        "void __thiscall CMenuItemDropdown__CommitSelection(void * this)",
        ["vtable slot 11", "vtable+0x38", "+0x1c"],
        ["cmenuitemdropdown", "frontend-menu", "dropdown", "selection", "commit", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["+ 0x38", "((int)this + 0x20)", "((int)this + 0x1c)"],
    ),
    "0x004a4110": target(
        "CMenuItemDropdown__ButtonPressed",
        "void __thiscall CMenuItemDropdown__ButtonPressed(void * this, int from_controller, int button)",
        ["vtable slot 1", "0x2a/0x36", "0x2e rollback"],
        ["cmenuitemdropdown", "frontend-menu", "dropdown", "input", "selection", "vtable-backed", "comment-hardened", "source-absent"],
        ["button", "0x2c", "0x2e"],
    ),
    "0x004a42f0": target(
        "CMenuItemDropdown__HasPendingSelectionChange",
        "bool __thiscall CMenuItemDropdown__HasPendingSelectionChange(void * this)",
        ["vtable slot 10", "+0x25", "+0x1c/+0x20"],
        ["cmenuitemdropdown", "frontend-menu", "dropdown", "selection", "state-query", "vtable-backed", "comment-hardened", "source-absent"],
        ["return true", "return false"],
    ),
    "0x004a4250": target(
        "CMenuItemSlider__Init",
        "void * __thiscall CMenuItemSlider__Init(void * this, void * linked_range)",
        ["vtable 0x005dc610", "linked range/list pointer", "source MenuItem.cpp body is absent"],
        ["cmenuitemslider", "frontend-menu", "slider", "init", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["PTR_VFuncSlot_00_004d0490_005dc610", "linked_range", "0xffd6d6d6"],
    ),
    "0x004a4290": target(
        "CMenuItemSlider__ButtonPressed",
        "void __thiscall CMenuItemSlider__ButtonPressed(void * this, int from_controller, int button)",
        ["vtable slot 1", "button 0x2c", "DAT_00704868"],
        ["cmenuitemslider", "frontend-menu", "slider", "input", "vtable-backed", "comment-hardened", "source-absent"],
        ["button == 0x2c", "DAT_00704868", "+ 0x2c"],
    ),
    "0x004a4310": target(
        "CMenuItemSlider__Render",
        "void __thiscall CMenuItemSlider__Render(void * this, float x, float y, int alpha)",
        ["vtable slot 4", "DAT_00704a88", "CMenuItem__Render"],
        ["cmenuitemslider", "frontend-menu", "slider", "render", "vtable-backed", "comment-hardened", "source-absent"],
        ["DAT_00704a88", "CMenuItem__Render"],
    ),
}

EXPECTED_VTABLE_EDGES = [
    ("0x005dc578", 1, "0x004a4110", "CMenuItemDropdown__ButtonPressed"),
    ("0x005dc578", 4, "0x004a3be0", "CMenuItemDropdown__RenderOrQueueDeferred"),
    ("0x005dc578", 8, "0x004a40e0", "CMenuItemDropdown__IsExpanded"),
    ("0x005dc578", 10, "0x004a42f0", "CMenuItemDropdown__HasPendingSelectionChange"),
    ("0x005dc578", 11, "0x004a40f0", "CMenuItemDropdown__CommitSelection"),
    ("0x005dc578", 12, "0x004a3b50", "CMenuItemDropdown__UpdateSelection"),
    ("0x005dc5c4", 17, "0x004a4220", "Localization__GetYesNoString"),
    ("0x005dc610", 1, "0x004a4290", "CMenuItemSlider__ButtonPressed"),
    ("0x005dc610", 4, "0x004a4310", "CMenuItemSlider__Render"),
]

EXPECTED_XREF_EDGES = [
    ("0x004a3b10", "PauseMenu__Init"),
    ("0x004a3b60", "PauseMenu__Init"),
    ("0x004a3ba0", "CMenuItemRange__Render"),
    ("0x004a3bb0", "CMenuItemRange__Render"),
    ("0x004a3c30", "CMenuItemDropdown__RenderOrQueueDeferred"),
    ("0x004a3c30", "CMenuItemDropdown__ProcessPending"),
    ("0x004a4250", "PauseMenu__Init"),
]

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
        for key in (
            "address",
            "target_addr",
            "from_addr",
            "from_function_addr",
            "vtable_addr",
            "target_address",
            "vtable",
            "pointer_addr",
            "function_entry",
            "containing_entry",
        ):
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
    directory = base / "post-decomp"
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


def relative_or_absolute(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


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


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")

    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing post_metadata row")
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
            failures.append(f"{address}: missing post_tags row")
        else:
            actual_tags = {item.strip() for item in re.split(r"[;,]", tag_row.get("tags", "")) if item.strip()}
            missing_tags = sorted(set(spec["tags"]) - actual_tags)  # type: ignore[arg-type]
            if missing_tags:
                failures.append(f"{address}: missing tags {missing_tags}")

        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing post-decomp export")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def check_vtables(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_vtable_slots.tsv")
    for vtable_addr, slot, target_addr, target_name in EXPECTED_VTABLE_EDGES:
        wanted_vtable = normalize_address(vtable_addr)
        wanted_target = normalize_address(target_addr)
        found = False
        for row in rows:
            try:
                row_slot = int(row.get("slot", row.get("slot_index", "-1")))
            except ValueError:
                row_slot = -1
            row_vtable = row.get("vtable_addr") or row.get("vtable")
            row_target = row.get("target_address") or row.get("function_entry")
            row_name = row.get("target_name") or row.get("function_name")
            if row_vtable == wanted_vtable and row_slot == slot and row_target == wanted_target and row_name == target_name:
                found = True
                break
        if not found:
            failures.append(f"post_vtable_slots.tsv: missing edge {vtable_addr} slot {slot} -> {target_addr} {target_name}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    if len(rows) < len(TARGETS):
        failures.append(f"post_xrefs.tsv: expected at least {len(TARGETS)} rows, got {len(rows)}")
    for target_addr, from_name in EXPECTED_XREF_EDGES:
        wanted = normalize_address(target_addr)
        if not any(row.get("target_addr") == wanted and row.get("from_function") == from_name for row in rows):
            failures.append(f"post_xrefs.tsv: missing edge {target_addr} from {from_name}")


def run(base: Path) -> dict[str, object]:
    failures: list[str] = []
    check_verify_log(base, failures)
    check_metadata(base, failures)
    check_vtables(base, failures)
    check_xrefs(base, failures)
    return {
        "status": "PASS" if not failures else "FAIL",
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "base": relative_or_absolute(base),
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
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ghidra_menuitem_dropdown_slider_wave441_probe: {result['status']} ({result['targetCount']} targets)")
        for failure in result["failures"]:
            print(f"FAIL: {failure}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
