#!/usr/bin/env python3
"""Validate the Wave414 CImageLoader/CIBuffer direct-lock Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave414_cimageloader_rendering" / "current"

COMMON_TAGS = {"static-reaudit", "cimageloader-wave414", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x004885e0": {
        "name": "CIBuffer__LockDirect",
        "signature": "int __thiscall CIBuffer__LockDirect(void * this, void * * out_data)",
        "commentTokens": ["direct CIBuffer D3D index-buffer lock helper", "+0x08", "+0x10", "0x2800", "0x800", "0x200", "CVBufTexture index-buffer callers", "runtime rendering behavior", "rebuild parity remain unproven"],
        "tags": {"ibuffer", "owner-corrected", "lock-unlock", "signature-corrected", "comment-hardened"},
        "decompileTokens": ["out_data", "0x2800", "0x800", "0x200"],
    },
    "0x00488620": {
        "name": "CImageLoader__Constructor",
        "signature": "void * __thiscall CImageLoader__Constructor(void * this, char * filename)",
        "commentTokens": ["CImageLoader constructor", "+0x04 through +0x14", "vtable 0x005dbedc", "filename to +0x18", "source body is absent", "runtime image loading", "remain unproven"],
        "tags": {"imageloader", "constructor", "signature-hardened", "comment-hardened"},
        "decompileTokens": ["filename", "005dbedc"],
    },
    "0x00488670": {
        "name": "CImageLoader__GetFilenamePtr",
        "signature": "char * __thiscall CImageLoader__GetFilenamePtr(void * this)",
        "commentTokens": ["recovered vtable function boundary", "this +0x18", "filename pointer", "runtime image loading", "remain unproven"],
        "tags": {"imageloader", "function-boundary", "vtable-slot", "getter", "comment-hardened"},
        "decompileTokens": ["0x18"],
        "instructionEvidence": ("LEA", "[ECX + 0x18]"),
    },
    "0x00488680": {
        "name": "CImageLoader__GetWidth",
        "signature": "int __thiscall CImageLoader__GetWidth(void * this)",
        "commentTokens": ["recovered vtable function boundary", "image width", "+0x08", "runtime image loading", "remain unproven"],
        "tags": {"imageloader", "function-boundary", "vtable-slot", "getter", "comment-hardened"},
        "decompileTokens": ["+8"],
        "instructionEvidence": ("MOV", "[ECX + 0x8]"),
    },
    "0x00488690": {
        "name": "CImageLoader__GetHeight",
        "signature": "int __thiscall CImageLoader__GetHeight(void * this)",
        "commentTokens": ["recovered vtable function boundary", "image height", "+0x0c", "runtime image loading", "remain unproven"],
        "tags": {"imageloader", "function-boundary", "vtable-slot", "getter", "comment-hardened"},
        "decompileTokens": ["0xc"],
        "instructionEvidence": ("MOV", "[ECX + 0xc]"),
    },
    "0x004886a0": {
        "name": "CImageLoader__ScalarDeletingDestructor",
        "signature": "void * __thiscall CImageLoader__ScalarDeletingDestructor(void * this, byte flags)",
        "commentTokens": ["scalar deleting destructor", "width and height buffers", "flags bit 0", "runtime image loading", "remain unproven"],
        "tags": {"imageloader", "destructor", "signature-hardened", "comment-hardened"},
    },
    "0x00488700": {
        "name": "CImageLoader__Destructor",
        "signature": "void __thiscall CImageLoader__Destructor(void * this)",
        "commentTokens": ["CImageLoader destructor", "width and height buffers", "runtime image loading", "remain unproven"],
        "tags": {"imageloader", "destructor", "signature-hardened", "comment-hardened"},
    },
    "0x00488740": {
        "name": "CImageLoader__FreeWidthBuffer",
        "signature": "void __thiscall CImageLoader__FreeWidthBuffer(void * this)",
        "commentTokens": ["width-buffer free helper", "+0x10", "runtime image loading", "remain unproven"],
        "tags": {"imageloader", "buffer-lifecycle", "signature-hardened", "comment-hardened"},
    },
    "0x00488760": {
        "name": "CImageLoader__FreeHeightBuffer",
        "signature": "void __thiscall CImageLoader__FreeHeightBuffer(void * this)",
        "commentTokens": ["height-buffer free helper", "+0x14", "runtime image loading", "remain unproven"],
        "tags": {"imageloader", "buffer-lifecycle", "signature-hardened", "comment-hardened"},
    },
    "0x00488780": {
        "name": "CImageLoader__LoadWidthBuffer",
        "signature": "bool __thiscall CImageLoader__LoadWidthBuffer(void * this, void * alloc_context)",
        "commentTokens": ["vtable slot +0x24", "0x80 bytes", "+0x10", "imageloader.cpp debug path line 0x2b", "runtime image loading", "remain unproven"],
        "tags": {"imageloader", "buffer-lifecycle", "signature-hardened", "comment-hardened"},
        "decompileTokens": ["alloc_context", "0x80", "0x2b"],
    },
    "0x004887c0": {
        "name": "CImageLoader__LoadHeightBuffer",
        "signature": "bool __thiscall CImageLoader__LoadHeightBuffer(void * this, void * alloc_context)",
        "commentTokens": ["vtable slot +0x28", "0x80 bytes", "+0x14", "imageloader.cpp debug path line 0x32", "runtime image loading", "remain unproven"],
        "tags": {"imageloader", "buffer-lifecycle", "signature-hardened", "comment-hardened"},
        "decompileTokens": ["alloc_context", "0x80", "0x32"],
    },
    "0x0052f540": {
        "name": "SharedVFunc__ReturnField04_0052f540",
        "signature": "void * __thiscall SharedVFunc__ReturnField04_0052f540(void * this)",
        "commentTokens": ["recovered shared vtable function boundary", "field +0x04", "ImageLoader", "other vtables", "runtime behavior", "remain unproven"],
        "tags": {"shared-vfunc", "function-boundary", "vtable-slot", "getter", "comment-hardened"},
        "decompileTokens": ["+4"],
        "instructionEvidence": ("MOV", "[ECX + 0x4]"),
    },
    "0x004de070": {
        "name": "SharedVFunc__ReturnField14_004de070",
        "signature": "void * __thiscall SharedVFunc__ReturnField14_004de070(void * this)",
        "commentTokens": ["recovered shared vtable function boundary", "field +0x14", "ImageLoader", "other vtables", "runtime behavior", "remain unproven"],
        "tags": {"shared-vfunc", "function-boundary", "vtable-slot", "getter", "comment-hardened"},
        "decompileTokens": ["0x14"],
        "instructionEvidence": ("MOV", "[ECX + 0x14]"),
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 8,
    "created": 0,
    "would_create": 5,
    "renamed": 0,
    "would_rename": 1,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 13,
    "skipped": 0,
    "created": 5,
    "would_create": 0,
    "renamed": 1,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime rendering behavior proven",
    "runtime image loading proven",
    "source body identity proven",
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
        "0": ("0x004886a0", "CImageLoader__ScalarDeletingDestructor"),
        "2": ("0x00488670", "CImageLoader__GetFilenamePtr"),
        "3": ("0x0052f540", "SharedVFunc__ReturnField04_0052f540"),
        "4": ("0x00488680", "CImageLoader__GetWidth"),
        "5": ("0x00488690", "CImageLoader__GetHeight"),
        "7": ("0x004de070", "SharedVFunc__ReturnField14_004de070"),
        "9": ("0x00488740", "CImageLoader__FreeWidthBuffer"),
        "10": ("0x00488760", "CImageLoader__FreeHeightBuffer"),
        "11": ("0x00488780", "CImageLoader__LoadWidthBuffer"),
        "12": ("0x004887c0", "CImageLoader__LoadHeightBuffer"),
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
        ("0x004885e0", "0x00500ac0", "CVBufTexture__AddIndices", "UNCONDITIONAL_CALL"),
        ("0x004885e0", "0x00546b40", "CDXLandscape__UpdateLOD", "UNCONDITIONAL_CALL"),
        ("0x00488670", "<none>", "<no_function>", "DATA"),
        ("0x0052f540", "<none>", "<no_function>", "DATA"),
        ("0x004de070", "<none>", "<no_function>", "DATA"),
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


def check_instruction_evidence(failures: list[str], rows: list[dict[str, str]]) -> None:
    for address, expected in TARGETS.items():
        instruction = expected.get("instructionEvidence")
        if not instruction:
            continue
        mnemonic, operand_token = instruction  # type: ignore[misc]
        target_rows = [row for row in rows if row.get("target_addr") == normalize_address(address)]
        if not target_rows:
            failures.append(f"{address} missing instruction rows")
            continue
        if not any(row.get("function_entry") == normalize_address(address) for row in target_rows):
            failures.append(f"{address} instruction rows do not resolve to recovered function entry")
        if not any(
            row.get("role") == "TARGET"
            and row.get("mnemonic") == mnemonic
            and token_present(row.get("operands", ""), str(operand_token))
            for row in target_rows
        ):
            failures.append(f"{address} missing instruction evidence {mnemonic} {operand_token}")


def check_targets(base: Path) -> list[str]:
    failures: list[str] = []
    metadata = read_tsv(base / "metadata_after.tsv")
    tags_rows = read_tsv(base / "tags_after.tsv")
    xrefs = read_tsv(base / "xrefs_after.tsv")
    vtable = read_tsv(base / "vtable_after.tsv")
    instructions = read_tsv(base / "instructions_after.tsv")
    decompile_dir = base / "decompile_after"

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

        text = decompile_text_for(decompile_dir, address)
        for token in expected.get("decompileTokens", []):  # type: ignore[assignment]
            if not text:
                failures.append(f"{address} missing decompile read-back")
                break
            if not token_present(text, str(token)):
                failures.append(f"{address} decompile missing token: {token}")

    check_vtable(failures, vtable)
    check_xrefs(failures, xrefs)
    check_instruction_evidence(failures, instructions)
    return failures


def write_report(base: Path, failures: list[str]) -> None:
    report = {
        "schema": "ghidra-cimageloader-wave414-probe.v1",
        "status": "PASS" if not failures else "FAIL",
        "targetCount": len(TARGETS),
        "failures": failures,
        "evidenceRoot": str(base.relative_to(ROOT)),
    }
    out_path = base / "cimageloader-wave414-probe.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="Wave414 evidence directory.")
    parser.add_argument("--check", action="store_true", help="Validate evidence and write the raw ignored report.")
    args = parser.parse_args(argv)

    failures = check_targets(args.base)
    if args.check:
        write_report(args.base, failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("PASS ghidra-cimageloader-wave414")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
