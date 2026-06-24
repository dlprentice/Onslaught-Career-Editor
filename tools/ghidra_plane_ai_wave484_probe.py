#!/usr/bin/env python3
"""Validate Wave484 CPlaneAI destructor correction evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave484-plane-ai-vfunc01-004d1c10"

WRAPPER = "0x004d1c10"
BODY = "0x004d1c30"

EXPECTED_SUMMARIES = {
    "apply_plane_ai_wave484_dry.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 2,
        "missing": 0,
        "bad": 0,
    },
    "apply_plane_ai_wave484_apply.log": {
        "updated": 2,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 2,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_plane_ai_wave484_verify_dry.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

TARGETS = {
    WRAPPER: {
        "name": "CPlaneAI__scalar_deleting_dtor",
        "signature": "void * __thiscall CPlaneAI__scalar_deleting_dtor(void * this, byte flags)",
        "tags": {
            "comment-hardened",
            "cplane-ai",
            "destructor",
            "plane-ai-wave484",
            "renamed",
            "retail-binary-evidence",
            "scalar-deleting-dtor",
            "signature-corrected",
            "static-reaudit",
            "vtable-readback",
        },
        "comment_tokens": [
            "CPlaneAI vtable 0x005de73c slot 1",
            "RTTI COL resolves that table as CPlaneAI",
            "CPlaneAI__dtor_body at 0x004d1c30",
            "scalar-delete flags bit 0",
            "CDXMemoryManager__Free(&DAT_009c3df0, this)",
            "RET 0x4",
            "Plane.cpp/CPlaneAI source body is absent",
            "runtime AI destruction behavior",
            "rebuild parity remain unproven",
        ],
        "decompile_tokens": [
            "void * __thiscall CPlaneAI__scalar_deleting_dtor(void *this,byte flags)",
            "CPlaneAI__dtor_body(this)",
            "(flags & 1) != 0",
            "CDXMemoryManager__Free(&DAT_009c3df0,this)",
            "return this",
        ],
    },
    BODY: {
        "name": "CPlaneAI__dtor_body",
        "signature": "void __fastcall CPlaneAI__dtor_body(void * this)",
        "tags": {
            "comment-hardened",
            "cplane-ai",
            "destructor",
            "dtor-body",
            "plane-ai-wave484",
            "renamed",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "vtable-readback",
        },
        "comment_tokens": [
            "called only by CPlaneAI__scalar_deleting_dtor",
            "base CUnitAI vtable 0x005d8d1c",
            "this+0x28",
            "this+0x24",
            "this+0x0c",
            "CSPtrSet__Remove",
            "CMonitor__Shutdown",
            "Plane.cpp/CPlaneAI source body is absent",
            "exact CPlaneAI layout",
            "linked-set semantics",
            "runtime AI destruction behavior",
            "rebuild parity remain unproven",
        ],
        "decompile_tokens": [
            "void __fastcall CPlaneAI__dtor_body(void *this)",
            "*(undefined ***)this = &PTR_LAB_005d8d1c",
            "((int)this + 0x28)",
            "((int)this + 0x24)",
            "((int)this + 0xc)",
            "CSPtrSet__Remove",
            "CMonitor__Shutdown(this)",
            "ExceptionList = local_c",
        ],
    },
}

EXPECTED_INSTRUCTIONS = {
    "0x004d1c13": ("CALL", "0x004d1c30"),
    "0x004d1c18": ("TEST", "byte ptr [ESP + 0x8], 0x1"),
    "0x004d1c20": ("MOV", "ECX, 0x9c3df0"),
    "0x004d1c25": ("CALL", "0x00549220"),
    "0x004d1c2d": ("RET", "0x4"),
    "0x004d1c4d": ("MOV", "dword ptr [ESI], 0x5d8d1c"),
    "0x004d1c6f": ("CALL", "0x004e5bd0"),
}

STALE_NAMES = ("CPlaneAI__VFunc_01_004d1c10", "CUnitAI__ctor_like_004d1c30")

OVERCLAIMS = (
    "fully re'ed",
    "source identity proven",
    "runtime behavior proven",
    "allocator ownership proven",
    "exact class layout proven",
    "linked-set semantics proven",
    "rebuild parity proven",
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
            "function_entry",
            "vtable",
            "slot_addr",
            "pointer_addr",
            "instruction_addr",
        ):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"updated=(?P<updated>\d+)\s+skipped=(?P<skipped>\d+)\s+created=(?P<created>\d+)\s+"
        r"would_create=(?P<would_create>\d+)\s+renamed=(?P<renamed>\d+)\s+"
        r"would_rename=(?P<would_rename>\d+)\s+missing=(?P<missing>\d+)\s+bad=(?P<bad>\d+)",
        text,
    )
    if not match:
        return {}
    return {key: int(value) for key, value in match.groupdict().items()}


def check_summaries(base: Path, failures: list[str]) -> None:
    for filename, expected in EXPECTED_SUMMARIES.items():
        path = base / filename
        actual = parse_summary(path)
        if actual != expected:
            failures.append(f"{filename}: expected summary {expected}, got {actual or '<missing>'}")
        if "REPORT: Save succeeded" not in read_text(path):
            failures.append(f"{filename}: missing REPORT: Save succeeded")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    tag_rows = read_tsv(base / "post_tags.tsv")
    names = {row.get("name", "") for row in rows}
    stale = sorted(name for name in names if name in STALE_NAMES)
    if stale:
        failures.append(f"post_metadata.tsv: stale names remain {stale}")

    for address, expected in TARGETS.items():
        row = next((r for r in rows if r.get("address") == address), None)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: expected name {expected['name']}, got {row.get('name')}")
        if compact(row.get("signature", "")) != compact(expected["signature"]):
            failures.append(f"{address}: expected signature {expected['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in expected["comment_tokens"]:
            if not token_present(comment, token):
                failures.append(f"{address}: comment missing token {token!r}")
        for overclaim in OVERCLAIMS:
            if token_present(comment, overclaim):
                failures.append(f"{address}: comment contains overclaim {overclaim!r}")

        tag_row = next((r for r in tag_rows if r.get("address") == address), None)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            actual_tags = set(filter(None, re.split(r"[;,]\s*", tag_row.get("tags", ""))))
            missing_tags = expected["tags"] - actual_tags
            if missing_tags:
                failures.append(f"{address}: missing tags {sorted(missing_tags)}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, expected in TARGETS.items():
        path = base / "post-decomp" / f"{address[2:]}_{expected['name']}.c"
        text = read_text(path)
        if not text:
            failures.append(f"{address}: missing decompile file {path.name}")
            continue
        for token in expected["decompile_tokens"]:
            if not token_present(text, token):
                failures.append(f"{address}: decompile missing token {token!r}")
        for stale_name in STALE_NAMES:
            if token_present(text, stale_name):
                failures.append(f"{address}: stale decompile name {stale_name!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    wrapper_xref = next(
        (r for r in rows if r.get("target_addr") == WRAPPER and r.get("from_addr") == "0x005de740"),
        None,
    )
    if wrapper_xref is None:
        failures.append(f"{WRAPPER}: missing CPlaneAI vtable DATA xref from 0x005de740")
    elif wrapper_xref.get("ref_type") != "DATA":
        failures.append(f"{WRAPPER}: expected DATA xref from 0x005de740, got {wrapper_xref.get('ref_type')}")

    body_xref = next((r for r in rows if r.get("target_addr") == BODY and r.get("from_addr") == "0x004d1c13"), None)
    if body_xref is None:
        failures.append(f"{BODY}: missing wrapper call xref from 0x004d1c13")
    elif body_xref.get("from_function") != TARGETS[WRAPPER]["name"] or body_xref.get("ref_type") != "UNCONDITIONAL_CALL":
        failures.append(
            f"{BODY}: expected call from {TARGETS[WRAPPER]['name']}, "
            f"got {body_xref.get('from_function')} {body_xref.get('ref_type')}"
        )


def check_vtables(base: Path, failures: list[str]) -> None:
    slot_rows = read_tsv(base / "post_vtable_slots.tsv")
    type_rows = read_tsv(base / "post_vtable_types.tsv")
    cplane_slot = next(
        (
            r
            for r in slot_rows
            if r.get("vtable") == "0x005de73c" and r.get("slot_index") == "1" and r.get("pointer_addr") == WRAPPER
        ),
        None,
    )
    if cplane_slot is None:
        failures.append("0x005de73c slot 1: missing CPlaneAI scalar deleting destructor slot")
    elif cplane_slot.get("function_name") != TARGETS[WRAPPER]["name"]:
        failures.append(f"0x005de73c slot 1: expected {TARGETS[WRAPPER]['name']}, got {cplane_slot.get('function_name')}")

    cunit_slot = next(
        (
            r
            for r in slot_rows
            if r.get("vtable") == "0x005d8d1c" and r.get("slot_index") == "1" and r.get("pointer_addr") == "0x00415060"
        ),
        None,
    )
    if cunit_slot is None:
        failures.append("0x005d8d1c slot 1: missing base CUnitAI scalar deleting destructor slot")
    elif cunit_slot.get("function_name") != "CUnitAI__scalar_deleting_dtor":
        failures.append(f"0x005d8d1c slot 1: expected CUnitAI__scalar_deleting_dtor, got {cunit_slot.get('function_name')}")

    expected_types = {"0x005de73c": "CPlaneAI", "0x005d8d1c": "CUnitAI"}
    for vtable, expected_type in expected_types.items():
        row = next((r for r in type_rows if r.get("vtable") == vtable), None)
        if row is None:
            failures.append(f"{vtable}: missing RTTI type row")
        elif row.get("demangled_type_name") != expected_type:
            failures.append(f"{vtable}: expected RTTI type {expected_type}, got {row.get('demangled_type_name')}")


def check_instructions(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_addr = {row.get("instruction_addr"): row for row in rows}
    for address, (mnemonic, operand_token) in EXPECTED_INSTRUCTIONS.items():
        row = by_addr.get(address)
        if row is None:
            failures.append(f"{address}: missing instruction row")
            continue
        if row.get("mnemonic") != mnemonic or not token_present(row.get("operands", ""), operand_token):
            failures.append(f"{address}: expected {mnemonic} {operand_token}, got {row.get('mnemonic')} {row.get('operands')}")


def run(base: Path = DEFAULT_BASE) -> list[str]:
    failures: list[str] = []
    check_summaries(base, failures)
    check_metadata(base, failures)
    check_decompile(base, failures)
    check_xrefs(base, failures)
    check_vtables(base, failures)
    check_instructions(base, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = run(args.base)
    if failures:
        print("FAIL Wave484 plane AI probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS Wave484 plane AI probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
