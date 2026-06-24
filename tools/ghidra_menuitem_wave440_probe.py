#!/usr/bin/env python3
"""Validate Wave440 CMenuItem base Ghidra metadata corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave440-menuitem-base-current"

COMMON_TAGS = {"static-reaudit", "menuitem-wave440", "retail-binary-evidence"}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 17,
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
    "0x004a3100": target(
        "CMenuItem__IsMouseInBounds",
        "int __cdecl CMenuItem__IsMouseInBounds(float x0, float y0, float x1, float y1)",
        ["CFrontEnd__GetCursorStateInRect", "source MenuItem.cpp body is absent", "rebuild parity remain unproven"],
        ["cmenuitem", "frontend-menu", "mouse-hit-test", "signature-corrected", "comment-hardened", "source-absent"],
        ["CFrontEnd__GetCursorStateInRect"],
    ),
    "0x004a3120": target(
        "CMenuItem__IsMouseClicked",
        "int __cdecl CMenuItem__IsMouseClicked(float x0, float y0, float x1, float y1)",
        ["CFrontEnd__GetClickStateInRect", "source MenuItem.cpp body is absent", "rebuild parity remain unproven"],
        ["cmenuitem", "frontend-menu", "mouse-click-test", "signature-corrected", "comment-hardened", "source-absent"],
        ["CFrontEnd__GetClickStateInRect"],
    ),
    "0x004a3140": target(
        "CMenuItem__Clone",
        "void * __thiscall CMenuItem__Clone(void * this)",
        ["0x005db440 slot 7", "0x1c-byte", "source MenuItem.cpp body is absent"],
        ["cmenuitem", "frontend-menu", "clone", "vtable-backed", "comment-hardened", "source-absent"],
        ["OID__AllocObject(0x1c", "PTR_CMenuItem__scalar_deleting_dtor_005db440"],
    ),
    "0x004a3190": target(
        "CMenuItem__GetText",
        "short * __thiscall CMenuItem__GetText(void * this)",
        ["vtable slot 2", "+0x8", "source MenuItem.cpp body is absent"],
        ["cmenuitem", "frontend-menu", "text", "vtable-backed", "comment-hardened", "source-absent"],
        ["CText__GetStringById", "Localization__GetStringById"],
    ),
    "0x004a3260": target(
        "CMenuItem__RenderCentered",
        "void __thiscall CMenuItem__RenderCentered(void * this, float x, float y, int alpha)",
        ["default ARGB color 0xffffffff", "RET 0x0c", "source MenuItem.cpp body is absent"],
        ["cmenuitem", "frontend-menu", "render", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["CMenuItem__Render", "0xffffffff"],
    ),
    "0x004a3290": target(
        "CMenuItem__RenderWithColor",
        "void __thiscall CMenuItem__RenderWithColor(void * this, float x, float y, int alpha, int argb_color)",
        ["custom-color render wrapper", "RET 0x10", "source MenuItem.cpp body is absent"],
        ["cmenuitem", "frontend-menu", "render", "color", "signature-corrected", "comment-hardened", "source-absent"],
        ["CMenuItem__Render", "argb_color"],
    ),
    "0x004a32c0": target(
        "CMenuItem__Render",
        "void __thiscall CMenuItem__Render(void * this, float x, float y, int alpha, int argb_color, short * text)",
        ["shared text render body", "RET 0x14", "CDXEngine__DrawTextScaledWithShadow"],
        ["cmenuitem", "frontend-menu", "render", "text", "signature-corrected", "comment-hardened", "source-absent"],
        ["CDXEngine__DrawTextScaledWithShadow", "CDXFont__GetTextExtent"],
    ),
    "0x004a3420": target(
        "CMenuItem__GetTextWidth",
        "int __thiscall CMenuItem__GetTextWidth(void * this)",
        ["width slot", "CDXFont__GetTextExtent", "source MenuItem.cpp body is absent"],
        ["cmenuitem", "frontend-menu", "text-width", "vtable-backed", "comment-hardened", "source-absent"],
        ["CDXFont__GetTextExtent", "return"],
    ),
    "0x004a3450": target(
        "CMenuItem__Clone",
        "void * __thiscall CMenuItem__Clone(void * this)",
        ["0x005dc520 slot 7", "0x38-byte", "CGenericActiveReader__SetReader"],
        ["cmenuitem", "frontend-menu", "clone", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["OID__AllocObject(0x38", "CGenericActiveReader__SetReader"],
    ),
    "0x004a3510": target(
        "CMenuItem__Init",
        "void * __thiscall CMenuItem__Init(void * this, int text_id, int item_id, float value_scale, void * owner, int max_value, byte notify_on_change)",
        ["0x38-byte CMenuItem initializer", "0xffd6d6d6", "+0x24/+0x28"],
        ["cmenuitem", "frontend-menu", "init", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["0xffd6d6d6", "CSPtrSet__AddToHead"],
    ),
    "0x004a3610": target(
        "CMenuItem__ScalarDestructor",
        "void * __thiscall CMenuItem__ScalarDestructor(void * this, byte flags)",
        ["scalar deleting destructor wrapper", "flags bit 0", "CDXMemoryManager__Free"],
        ["cmenuitem", "frontend-menu", "destructor", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["CMenuItem__Destructor", "CDXMemoryManager__Free"],
    ),
    "0x004a3630": target(
        "CMenuItem__InitWithIcon",
        "void * __thiscall CMenuItem__InitWithIcon(void * this, int icon_or_text_id, int item_id, float value_scale, void * owner, int max_value, byte notify_on_change)",
        ["alternate CMenuItem initializer", "+0x18", "0x005dc520"],
        ["cmenuitem", "frontend-menu", "init", "icon-or-localized-id", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["0xffd6d6d6", "CSPtrSet__AddToHead"],
    ),
    "0x004a3730": target(
        "CMenuItem__Destructor",
        "void __thiscall CMenuItem__Destructor(void * this)",
        ["decrements resource counters", "CSPtrSet__Remove", "source MenuItem.cpp body is absent"],
        ["cmenuitem", "frontend-menu", "destructor", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"],
        ["CHud__DecrementCounter9C", "CSPtrSet__Remove"],
    ),
    "0x004a37c0": target(
        "CMenuItem__RenderValueBar",
        "void __thiscall CMenuItem__RenderValueBar(void * this, float x, float y, int interactive)",
        ["value-bar renderer", "buttons 0x36/0x37", "source MenuItem.cpp body is absent"],
        ["cmenuitem", "frontend-menu", "render", "value-bar", "vtable-backed", "comment-hardened", "source-absent"],
        ["CFrontEnd__GetClickStateInRect", "CVBufTexture__DrawSpriteEx"],
    ),
    "0x004a43a0": target(
        "CMenuItem__ButtonPressed",
        "void __thiscall CMenuItem__ButtonPressed(void * this, int from_controller, int button)",
        ["button 0x2c", "0x36", "0x37"],
        ["cmenuitem", "frontend-menu", "input", "value-bar", "vtable-backed", "comment-hardened", "source-absent"],
        ["button == 0x2c", "button == 0x36", "button == 0x37"],
    ),
    "0x004a4450": target(
        "CMenuItem__GetWidth",
        "int __thiscall CMenuItem__GetWidth(void * this)",
        ["slot 5 width helper", "0x6a padding", "source MenuItem.cpp body is absent"],
        ["cmenuitem", "frontend-menu", "text-width", "vtable-backed", "comment-hardened", "source-absent"],
        ["CDXFont__GetTextExtent", "+ 0x6a"],
    ),
    "0x004a44c0": target(
        "CMenuItem__SetUserData",
        "void __thiscall CMenuItem__SetUserData(void * this, void * user_data)",
        ["writes the caller value to +0x20", "exact pointer/resource type", "source MenuItem.cpp body is absent"],
        ["cmenuitem", "frontend-menu", "setter", "signature-corrected", "comment-hardened", "source-absent"],
        ["+ 0x20"],
    ),
}

EXPECTED_VTABLE_EDGES = [
    ("0x005dc520", 0, "0x004a3610", "CMenuItem__ScalarDestructor"),
    ("0x005dc520", 1, "0x004a43a0", "CMenuItem__ButtonPressed"),
    ("0x005dc520", 2, "0x004a3190", "CMenuItem__GetText"),
    ("0x005dc520", 4, "0x004a37c0", "CMenuItem__RenderValueBar"),
    ("0x005dc520", 5, "0x004a4450", "CMenuItem__GetWidth"),
    ("0x005dc520", 7, "0x004a3450", "CMenuItem__Clone"),
    ("0x005db440", 2, "0x004a3190", "CMenuItem__GetText"),
    ("0x005db440", 4, "0x004a3260", "CMenuItem__RenderCentered"),
    ("0x005db440", 5, "0x004a3420", "CMenuItem__GetTextWidth"),
    ("0x005db440", 7, "0x004a3140", "CMenuItem__Clone"),
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
    expected_edges = [
        ("0x004a3100", "CMenuItemRange__Render"),
        ("0x004a3120", "CMenuItemRange__Render"),
        ("0x004a3290", "CControllerBackMenuItem__VFunc_04_004d0290"),
        ("0x004a3510", "PauseMenu__Init"),
        ("0x004a3630", "PauseMenu__Init"),
    ]
    for target_addr, from_name in expected_edges:
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
        print(f"ghidra_menuitem_wave440_probe: {result['status']} ({result['targetCount']} targets)")
        for failure in result["failures"]:
            print(f"FAIL: {failure}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
