#!/usr/bin/env python3
"""Validate Wave442 CMenuItemRange/CMenuItemRangeVariant Ghidra metadata."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave442-menuitem-range-current"

COMMON_TAGS = {"static-reaudit", "menuitem-wave442", "retail-binary-evidence"}
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
    "0x004a45c0": target(
        "CMenuItemRange__Init",
        "void * __thiscall CMenuItemRange__Init(void * this, short * title_text, float x, float y, int panel_flag, int panel_arg)",
        ["vtable 0x005dc650", "+0x1c/+0x20", "source MenuItem.cpp body is absent"],
        ["cmenuitemrange", "frontend-menu", "range", "init", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["CSPtrSet__Init", "PTR_CMenuItemRange__ScalarDestructor_005dc650"],
    ),
    "0x004a4610": target(
        "CMenuItemRange__ScalarDestructor",
        "void * __thiscall CMenuItemRange__ScalarDestructor(void * this, byte flags)",
        ["CDXMemoryManager__Free", "flags bit 0", "source MenuItem.cpp body is absent"],
        ["cmenuitemrange", "frontend-menu", "range", "destructor", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["CMenuItemRange__Destructor", "CDXMemoryManager__Free"],
    ),
    "0x004a4630": target(
        "CMenuItemRange__ResetIterator",
        "void __thiscall CMenuItemRange__ResetIterator(void * this)",
        ["selected index +0x18", "vtable+0x30", "source MenuItem.cpp body is absent"],
        ["cmenuitemrange", "frontend-menu", "range", "iteration", "signature-corrected", "comment-hardened", "source-absent"],
        ["+ 0x30"],
    ),
    "0x004a4670": target(
        "CMenuItemRange__AddItem",
        "void __thiscall CMenuItemRange__AddItem(void * this, void * item)",
        ["CSPtrSet__AddToTail", "PauseMenu__Init", "source MenuItem.cpp body is absent"],
        ["cmenuitemrange", "frontend-menu", "range", "item-list", "signature-corrected", "comment-hardened", "source-absent"],
        ["CSPtrSet__AddToTail", "item"],
    ),
    "0x004a4680": target(
        "CMenuItemRange__Destructor",
        "void __thiscall CMenuItemRange__Destructor(void * this)",
        ["vtable 0x005dc650", "CHud__DecrementCounter9C", "source MenuItem.cpp body is absent"],
        ["cmenuitemrange", "frontend-menu", "range", "destructor", "resource-cleanup", "signature-corrected", "comment-hardened", "source-absent"],
        ["CHud__DecrementCounter9C", "CSPtrSet__Clear"],
    ),
    "0x004a4730": target(
        "CMenuItemRange__LoadTexture",
        "void __thiscall CMenuItemRange__LoadTexture(void * this)",
        ["FrontEnd_v2/FE_Blank.tga", "vtable+0x34", "source MenuItem.cpp body is absent"],
        ["cmenuitemrange", "frontend-menu", "range", "texture", "iteration", "signature-corrected", "comment-hardened", "source-absent"],
        ["CTexture__FindTexture", "+ 0x34"],
    ),
    "0x004a4790": target(
        "CMenuItemRange__SelectNext",
        "void __thiscall CMenuItemRange__SelectNext(void * this)",
        ["wraps only when item count +0x14 is at least 3", "vtable+0x0c", "CFrontEnd__PlaySound"],
        ["cmenuitemrange", "frontend-menu", "range", "selection", "input", "signature-corrected", "comment-hardened", "source-absent"],
        ["CFrontEnd__PlaySound", "+ 0xc"],
    ),
    "0x004a4810": target(
        "CMenuItemRange__Render",
        "int __thiscall CMenuItemRange__Render(void * this, void * binding_context)",
        ["CMenuItemDropdown__ClearPending", "DAT_00704a88", "CMenuItemDropdown__ProcessPending"],
        ["cmenuitemrange", "frontend-menu", "range", "render", "dropdown-deferred-render", "mouse-input", "signature-corrected", "comment-hardened", "source-absent"],
        ["CMenuItemDropdown__ClearPending", "CMenuItemDropdown__ProcessPending", "DAT_00704a88"],
    ),
    "0x004a4cd0": target(
        "CMenuItemRange__ProcessInput",
        "int __thiscall CMenuItemRange__ProcessInput(void * this, int from_controller, int button, int context)",
        ["vtable slot 2", "vtable+0x20", "returns 1 only after forwarding"],
        ["cmenuitemrange", "frontend-menu", "range", "input", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["+ 0x20", "from_controller,button,context"],
    ),
    "0x004a4d20": target(
        "CMenuItemRange__HandleKeyPress",
        "void __thiscall CMenuItemRange__HandleKeyPress(void * this, int from_controller, int button, int context)",
        ["button 0x2a", "button 0x2b", "vtable+0x04"],
        ["cmenuitemrange", "frontend-menu", "range", "input", "selection", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["button != 0x2b", "CMenuItemRange__SelectNext", "+ 4"],
    ),
    "0x004a4dd0": target(
        "CMenuItemRange__SetItemEnabled",
        "void __thiscall CMenuItemRange__SetItemEnabled(void * this, int item_id, int enabled)",
        ["item id at +0x08", "offset +0x10", "source MenuItem.cpp body is absent"],
        ["cmenuitemrange", "frontend-menu", "range", "item-list", "enabled-state", "signature-corrected", "comment-hardened", "source-absent"],
        ["item_id", "enabled"],
    ),
    "0x004a4e10": target(
        "CMenuItemRangeVariant__Init",
        "void * __thiscall CMenuItemRangeVariant__Init(void * this, short * title_text, float x, float y, int panel_flag, int panel_arg)",
        ["vtable 0x005dc664", "reuses the range input/process slots", "source MenuItem.cpp body is absent"],
        ["cmenuitemrangevariant", "frontend-menu", "range", "variant", "init", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["CSPtrSet__Init", "PTR_CMenuItemRangeVariant__ScalarDestructor_005dc664"],
    ),
    "0x004a4e60": target(
        "CMenuItemRangeVariant__ScalarDestructor",
        "void * __thiscall CMenuItemRangeVariant__ScalarDestructor(void * this, byte flags)",
        ["CDXMemoryManager__Free", "flags bit 0", "source MenuItem.cpp body is absent"],
        ["cmenuitemrangevariant", "frontend-menu", "range", "variant", "destructor", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["CMenuItemRangeVariant__Destructor", "CDXMemoryManager__Free"],
    ),
    "0x004a4e80": target(
        "CMenuItemRangeVariant__Destructor",
        "void __thiscall CMenuItemRangeVariant__Destructor(void * this)",
        ["same linked-child teardown", "variant-specific SEH unwind", "source MenuItem.cpp body is absent"],
        ["cmenuitemrangevariant", "frontend-menu", "range", "variant", "destructor", "resource-cleanup", "signature-corrected", "comment-hardened", "source-absent"],
        ["CHud__DecrementCounter9C", "CSPtrSet__Clear"],
    ),
}

EXPECTED_VTABLE_EDGES = [
    ("0x005dc650", 0, "0x004a4610", "CMenuItemRange__ScalarDestructor"),
    ("0x005dc650", 1, "0x004a4d20", "CMenuItemRange__HandleKeyPress"),
    ("0x005dc650", 2, "0x004a4cd0", "CMenuItemRange__ProcessInput"),
    ("0x005dc650", 3, "0x00453a80", "CMenuItem__DefaultFalseFlag"),
    ("0x005dc664", 0, "0x004a4e60", "CMenuItemRangeVariant__ScalarDestructor"),
    ("0x005dc664", 1, "0x004a4d20", "CMenuItemRange__HandleKeyPress"),
    ("0x005dc664", 2, "0x004a4cd0", "CMenuItemRange__ProcessInput"),
]

EXPECTED_XREF_EDGES = [
    ("0x004a45c0", "PauseMenu__Init"),
    ("0x004a4630", "CPauseMenu__ButtonPressed"),
    ("0x004a4670", "PauseMenu__Init"),
    ("0x004a4730", "CPauseMenu__LoadPauseTextures"),
    ("0x004a4810", "CEngine__RenderOverlayAndMenuTransitions"),
    ("0x004a4dd0", "CPauseMenu__InitPauseSession"),
    ("0x004a4e10", "CPauseMenu__ButtonPressed"),
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
        print(f"ghidra_menuitem_range_wave442_probe: {result['status']} ({result['targetCount']} targets)")
        for failure in result["failures"]:
            print(f"FAIL: {failure}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
