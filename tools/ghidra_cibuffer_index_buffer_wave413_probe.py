#!/usr/bin/env python3
"""Validate the Wave413 CIBuffer/index-buffer Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave413_cibuffer_index_buffer" / "current"

COMMON_TAGS = {"static-reaudit", "cibuffer-index-buffer-wave413", "retail-binary-evidence", "ibuffer"}

TARGETS: dict[str, dict[str, object]] = {
    "0x00488210": {
        "name": "CIBuffer__Constructor",
        "signature": "void * __thiscall CIBuffer__Constructor(void * this)",
        "commentTokens": ["CIBuffer constructor", "vtable 0x005dbec4", "+0x1c", "+0x20", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"constructor", "signature-hardened", "comment-hardened"},
    },
    "0x00488270": {
        "name": "CIBuffer__ScalarDeletingDestructor",
        "signature": "void * __thiscall CIBuffer__ScalarDeletingDestructor(void * this, byte flags)",
        "commentTokens": ["scalar deleting destructor wrapper", "CIBuffer__Destructor", "flags bit 0", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"destructor", "signature-hardened", "comment-hardened"},
    },
    "0x00488290": {
        "name": "CIBuffer__Destructor",
        "signature": "void __thiscall CIBuffer__Destructor(void * this)",
        "commentTokens": ["CIBuffer destructor", "releases the D3D index-buffer interface", "+0x08", "+0x1c", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"destructor", "signature-hardened", "comment-hardened"},
    },
    "0x00488330": {
        "name": "CIBuffer__CreateConfigured",
        "signature": "int __thiscall CIBuffer__CreateConfigured(void * this, int size_bytes, int usage_flags, int index_format, int buffer_type)",
        "commentTokens": ["configured CIBuffer create", "size_bytes at +0x0c", "usage_flags at +0x10", "index_format at +0x14", "buffer_type at +0x18", "vtable slot +0x04", "vtable slot +0x08", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"create", "signature-corrected", "comment-hardened"},
        "decompileTokens": ["size_bytes", "usage_flags", "index_format", "buffer_type"],
    },
    "0x00488380": {
        "name": "CIBuffer__Create",
        "signature": "int __thiscall CIBuffer__Create(void * this, int index_count)",
        "commentTokens": ["default CIBuffer create", "index_count*2 bytes", "ibuffer.cpp debug path", "dynamic create vtable slot", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"create", "shadow-buffer", "signature-hardened", "comment-hardened"},
        "decompileTokens": ["index_count", "0x65"],
    },
    "0x004883f0": {
        "name": "CIBuffer__Unlock",
        "signature": "int __thiscall CIBuffer__Unlock(void * this)",
        "commentTokens": ["CIBuffer unlock", "0x800", "+0x0c bytes", "shadow storage +0x1c", "clears +0x20", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"lock-unlock", "shadow-buffer", "signature-hardened", "comment-hardened"},
        "decompileTokens": ["0x800", "0x1c", "0x20"],
    },
    "0x00488460": {
        "name": "CIBuffer__CreateDynamic",
        "signature": "int __thiscall CIBuffer__CreateDynamic(void * this)",
        "commentTokens": ["recovered function boundary", "dynamic-create vtable slot 1", "+0x18 == 1", "0x005137d0", "0x80004005", "shadow buffer", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"function-boundary", "vtable-slot", "create", "dynamic-buffer", "comment-hardened"},
    },
    "0x004884f0": {
        "name": "CIBuffer__CreateStatic",
        "signature": "int __thiscall CIBuffer__CreateStatic(void * this)",
        "commentTokens": ["recovered function boundary", "static-create vtable slot 2", "+0x18 == 0", "0x005137d0", "0x80004005", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"function-boundary", "vtable-slot", "create", "static-buffer", "comment-hardened"},
    },
    "0x00488520": {
        "name": "CIBuffer__ReleaseStatic",
        "signature": "int __thiscall CIBuffer__ReleaseStatic(void * this)",
        "commentTokens": ["static-release vtable slot", "+0x18 is static zero", "+0x08", "returns zero", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"vtable-slot", "release", "static-buffer", "signature-hardened", "comment-hardened"},
    },
    "0x00488550": {
        "name": "CIBuffer__ReleaseDynamic",
        "signature": "int __thiscall CIBuffer__ReleaseDynamic(void * this)",
        "commentTokens": ["dynamic-release vtable slot", "+0x18 is dynamic one", "+0x08", "returns zero", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"vtable-slot", "release", "dynamic-buffer", "signature-hardened", "comment-hardened"},
    },
    "0x00488580": {
        "name": "CIBuffer__Lock",
        "signature": "int __thiscall CIBuffer__Lock(void * this, void * * out_data)",
        "commentTokens": ["CIBuffer lock", "out_data", "+0x1c", "+0x20", "0x2800", "0x800", "0x200", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"lock-unlock", "shadow-buffer", "signature-hardened", "comment-hardened"},
        "decompileTokens": ["out_data", "0x2800", "0x800", "0x200"],
    },
    "0x0048e350": {
        "name": "CIBuffer__Destructor_thunk",
        "signature": "void __thiscall CIBuffer__Destructor_thunk(void * this)",
        "commentTokens": ["destructor thunk", "thiscall receiver", "CIBuffer__Destructor", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"destructor", "thunk", "signature-hardened", "comment-hardened"},
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 10,
    "created": 0,
    "would_create": 2,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 12,
    "skipped": 0,
    "created": 2,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime rendering behavior proven",
    "source identity proven",
    "concrete cibuffer layout proven",
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
        for key in ("address", "target_addr", "from_function_addr", "function_entry", "pointer_addr", "containing_entry"):
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


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return {
            "updated": -1,
            "skipped": -1,
            "created": -1,
            "would_create": -1,
            "renamed": -1,
            "would_rename": -1,
            "missing": -1,
            "bad": -1,
        }
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def compare_summary(failures: list[str], label: str, actual: dict[str, int], expected: dict[str, int]) -> None:
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            failures.append(f"{label} summary {key}: expected {expected_value}, got {actual_value}")


def decompile_text_for(directory: Path, address: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def check_vtable(failures: list[str], rows: list[dict[str, str]]) -> None:
    expected = {
        "0": ("0x00488270", "CIBuffer__ScalarDeletingDestructor"),
        "1": ("0x00488460", "CIBuffer__CreateDynamic"),
        "2": ("0x004884f0", "CIBuffer__CreateStatic"),
        "3": ("0x00488520", "CIBuffer__ReleaseStatic"),
        "4": ("0x00488550", "CIBuffer__ReleaseDynamic"),
    }
    for slot, (address, name) in expected.items():
        matches = [row for row in rows if row.get("slot_index") == slot and row.get("pointer_addr") == normalize_address(address)]
        if len(matches) != 1:
            failures.append(f"vtable slot {slot} expected pointer {address}, found {len(matches)}")
            continue
        row = matches[0]
        if row.get("function_entry") != normalize_address(address):
            failures.append(f"vtable slot {slot} function_entry expected {address}, got {row.get('function_entry')}")
        if row.get("function_name") != name:
            failures.append(f"vtable slot {slot} function_name expected {name}, got {row.get('function_name')}")


def check_xrefs(failures: list[str], rows: list[dict[str, str]]) -> None:
    expected = [
        ("0x00488210", "0x005007f0", "CVBufTexture__ResizeIndexBuffer", "UNCONDITIONAL_CALL"),
        ("0x00488330", "0x005007f0", "CVBufTexture__ResizeIndexBuffer", "UNCONDITIONAL_CALL"),
        ("0x00488380", "0x0051a510", "CFastVB__Render", "UNCONDITIONAL_CALL"),
        ("0x004883f0", "0x005009f0", "CVBufTexture__UnlockIB", "UNCONDITIONAL_CALL"),
        ("0x00488460", "<none>", "<no_function>", "DATA"),
        ("0x004884f0", "<none>", "<no_function>", "DATA"),
        ("0x00488580", "0x0051a510", "CFastVB__Render", "UNCONDITIONAL_CALL"),
        ("0x0048e350", "<none>", "<no_function>", "UNCONDITIONAL_CALL"),
    ]
    for target, from_function_addr, from_function, ref_type in expected:
        matches = [
            row
            for row in rows
            if row.get("target_addr") == normalize_address(target)
            and row.get("from_function_addr") == normalize_address(from_function_addr)
            and row.get("from_function") == from_function
            and row.get("ref_type") == ref_type
        ]
        if not matches:
            failures.append(f"{target} expected xref from {from_function} ({from_function_addr}) type {ref_type}")


def check_create_slot_instructions(failures: list[str], rows: list[dict[str, str]]) -> None:
    evidence = {
        "0x00488460": [
            ("TARGET", "PUSH", "ECX"),
            ("AFTER", "CALL", "0x005137d0"),
            ("AFTER", "MOV", "0x80004005"),
            ("AFTER", "MOVSD.REP", "ES:EDI, ESI"),
        ],
        "0x004884f0": [
            ("TARGET", "MOV", "[ECX + 0x18]"),
            ("AFTER", "CALL", "0x005137d0"),
            ("AFTER", "MOV", "0x80004005"),
        ],
    }
    for target, expected_rows in evidence.items():
        target_rows = [row for row in rows if row.get("target_addr") == normalize_address(target)]
        for role, mnemonic, operand_token in expected_rows:
            if not any(
                row.get("role") == role
                and row.get("mnemonic") == mnemonic
                and token_present(row.get("operands", ""), operand_token)
                for row in target_rows
            ):
                failures.append(f"{target} missing instruction evidence {role} {mnemonic} {operand_token}")
        if not any(row.get("function_entry") == normalize_address(target) for row in target_rows):
            failures.append(f"{target} create-slot instruction rows do not resolve to recovered function entry")


def check_targets(base: Path) -> list[str]:
    failures: list[str] = []
    metadata = read_tsv(base / "metadata_after.tsv")
    tags_rows = read_tsv(base / "tags_after.tsv")
    xrefs = read_tsv(base / "xrefs_after.tsv")
    vtable = read_tsv(base / "vtable_after.tsv")
    decompile_dir = base / "decompile_after"
    create_slot_instructions = read_tsv(base / "create_slot_instructions_after.tsv")

    compare_summary(failures, "dry", parse_summary(read_text(base / "apply_dry.log")), EXPECTED_DRY)
    compare_summary(failures, "apply", parse_summary(read_text(base / "apply_apply.log")), EXPECTED_APPLY)

    for address, expected in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address} missing metadata row")
            continue
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status expected OK, got {row.get('status')}")
        if row.get("name") != expected["name"]:
            failures.append(f"{address} name expected {expected['name']}, got {row.get('name')}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address} signature expected {expected['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address} comment missing token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address} comment contains overclaim token: {token}")

        tags_row = row_by_address(tags_rows, address)
        if tags_row is None:
            failures.append(f"{address} missing tags row")
        else:
            tags = parse_tags(tags_row.get("tags", ""))
            expected_tags = COMMON_TAGS | set(expected["tags"])  # type: ignore[arg-type]
            missing_tags = sorted(expected_tags - tags)
            if missing_tags:
                failures.append(f"{address} missing tags: {', '.join(missing_tags)}")

        decompile_tokens = expected.get("decompileTokens", [])
        if decompile_tokens:
            text = decompile_text_for(decompile_dir, address)
            if not text:
                failures.append(f"{address} missing decompile read-back")
            for token in decompile_tokens:  # type: ignore[assignment]
                if not token_present(text, str(token)):
                    failures.append(f"{address} decompile missing token: {token}")

    check_vtable(failures, vtable)
    check_xrefs(failures, xrefs)
    check_create_slot_instructions(failures, create_slot_instructions)
    return failures


def write_report(base: Path, failures: list[str]) -> None:
    report = {
        "schema": "ghidra-cibuffer-index-buffer-wave413-probe.v1",
        "status": "PASS" if not failures else "FAIL",
        "targetCount": len(TARGETS),
        "failures": failures,
        "evidenceRoot": str(base.relative_to(ROOT)),
    }
    import json

    out_path = base / "cibuffer-index-buffer-wave413-probe.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="Wave413 evidence directory.")
    parser.add_argument("--check", action="store_true", help="Validate evidence and write the raw ignored report.")
    args = parser.parse_args(argv)

    failures = check_targets(args.base)
    if args.check:
        write_report(args.base, failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("PASS ghidra-cibuffer-index-buffer-wave413")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
