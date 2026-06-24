#!/usr/bin/env python3
"""Validate Wave479 controller-target release helper correction."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave479-controller-audio-queue-head-004cdd70"

TARGET_ADDR = "0x004cdd70"
OLD_NAME = "CRocket__RelinquishControllerOwnership"
NEW_NAME = "GameControllers__RelinquishControlForTarget"
EXPECTED_SIGNATURE = "void __fastcall GameControllers__RelinquishControlForTarget(void * controlled_target)"

EXPECTED_SUMMARIES = {
    "apply_controller_target_wave479_dry.log": {
        "updated": 0,
        "skipped": 1,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 1,
        "missing": 0,
        "bad": 0,
    },
    "apply_controller_target_wave479_apply.log": {
        "updated": 1,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 1,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_controller_target_wave479_verify_dry.log": {
        "updated": 0,
        "skipped": 1,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

EXPECTED_TAGS = {
    "comment-hardened",
    "control-stack",
    "controller",
    "controller-target-wave479",
    "owner-corrected",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

COMMENT_TOKENS = [
    "Wave479 owner/signature correction",
    "not rocket-specific",
    "ECX is the controlled_target",
    "controller indices 0..1",
    "CGame__GetController(&DAT_008a9a98, index)",
    "CController__GetToControl(controller)",
    "CController__RelinquishControl(controller)",
    "CMessageLog__HandleInputCommand",
    "0x0048ffcc",
    "runtime input/menu behavior",
    "rebuild parity remain unproven",
]

DECOMPILE_TOKENS = [
    NEW_NAME,
    "void *controlled_target",
    "CGame__GetController(&DAT_008a9a98,number)",
    "CController__GetToControl(pvVar1)",
    "controlled_target",
    "CController__RelinquishControl(pvVar1)",
    "number < 2",
]

EXPECTED_XREFS = {
    (TARGET_ADDR, "0x0048ffcc", "<no_function>"),
    (TARGET_ADDR, "0x004b9ef5", "CMessageLog__HandleInputCommand"),
}

EXPECTED_INSTRUCTION_ROWS = {
    "0x004cdd72": ("MOV", "EDI, ECX"),
    "0x004cdd7c": ("CALL", "0x004705d0"),
    "0x004cdd92": ("CALL", "0x0042e4b0"),
    "0x004cdd97": ("CMP", "EAX, EDI"),
    "0x004cdda8": ("CALL", "0x0042e6e0"),
    "0x004cddae": ("CMP", "ESI, 0x2"),
    "0x004cddb5": ("RET", ""),
}

EXPECTED_RAW_CALLSITE_ROWS = {
    "0x0048ffa0": ("MOV", "EAX, dword ptr [ESP + 0x8]"),
    "0x0048ffa5": ("CMP", "EAX, 0x2e"),
    "0x0048ffca": ("MOV", "ECX, ESI"),
    "0x0048ffcc": ("CALL", "0x004cdd70"),
}

EXPECTED_CONTEXT_ROWS = {
    "0x004b9ef5": ("CALL", "0x004cdd70"),
    "0x004705d0": ("MOV", "EAX, dword ptr [ESP + 0x4]"),
    "0x0042e4b0": ("MOV", "EAX, dword ptr [ECX + 0x4]"),
    "0x0042e6e0": ("MOV", "EAX, dword ptr [ECX + 0x4]"),
}

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime input/menu behavior proven",
    "exact source identity proven",
    "concrete control-target type proven",
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "instruction_addr", "function_entry"):
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


def check_summary(path: Path, expected: dict[str, int], label: str, failures: list[str]) -> None:
    actual = parse_summary(path)
    if actual != expected:
        failures.append(f"{label}: expected summary {expected}, got {actual or '<missing>'}")
    if "REPORT: Save succeeded" not in read_text(path):
        failures.append(f"{label}: missing REPORT: Save succeeded")


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    wanted = normalize_address(address)[2:]
    for path in directory.glob(f"{wanted}_*.c"):
        return read_text(path)
    return ""


def strip_c_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//.*", "", text)


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    row = row_by_address(rows, TARGET_ADDR)
    if row is None:
        failures.append(f"{TARGET_ADDR}: missing metadata row")
        return
    if row.get("name") != NEW_NAME:
        failures.append(f"{TARGET_ADDR}: expected name {NEW_NAME}, got {row.get('name')}")
    signature = row.get("signature", "")
    if signature != EXPECTED_SIGNATURE:
        failures.append(f"{TARGET_ADDR}: expected signature {EXPECTED_SIGNATURE}, got {signature}")
    if "param_" in signature:
        failures.append(f"{TARGET_ADDR}: signature still contains generated parameter naming")
    combined = "\n".join([row.get("name", ""), signature, row.get("comment", "")])
    if OLD_NAME in combined:
        failures.append(f"{TARGET_ADDR}: metadata still contains stale name {OLD_NAME}")
    comment = row.get("comment", "")
    for token in COMMENT_TOKENS:
        if not token_present(comment, token):
            failures.append(f"{TARGET_ADDR}: comment missing token {token!r}")
    for token in OVERCLAIMS:
        if token_present(comment, token):
            failures.append(f"{TARGET_ADDR}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    row = row_by_address(rows, TARGET_ADDR)
    if row is None:
        failures.append(f"{TARGET_ADDR}: missing tag row")
        return
    tags = {tag for tag in row.get("tags", "").split(";") if tag}
    missing = sorted(EXPECTED_TAGS - tags)
    if missing:
        failures.append(f"{TARGET_ADDR}: missing tags {missing}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    edges = {
        (
            normalize_address(row.get("target_addr", "")),
            normalize_address(row.get("from_addr", "")),
            row.get("from_function", ""),
        )
        for row in rows
    }
    for edge in sorted(EXPECTED_XREFS):
        if edge not in edges:
            failures.append(f"post_xrefs.tsv: missing xref edge {edge}")


def check_decompile(base: Path, failures: list[str]) -> None:
    text = decompile_text_for(base, TARGET_ADDR)
    if not text:
        failures.append(f"{TARGET_ADDR}: missing post decompile text")
        return
    for token in DECOMPILE_TOKENS:
        if not token_present(text, token):
            failures.append(f"{TARGET_ADDR}: decompile missing token {token!r}")
    body = strip_c_comments(text)
    if "param_1" in body:
        failures.append(f"{TARGET_ADDR}: decompile body still contains param_1")
    if OLD_NAME in text:
        failures.append(f"{TARGET_ADDR}: decompile still contains stale name {OLD_NAME}")
    for token in OVERCLAIMS:
        if token_present(text, token):
            failures.append(f"{TARGET_ADDR}: decompile contains overclaim token {token!r}")


def check_rows(path: Path, expected_rows: dict[str, tuple[str, str]], label: str, failures: list[str]) -> None:
    rows = read_tsv(path)
    by_addr = {normalize_address(row.get("address", "")): row for row in rows}
    for address, (mnemonic, operands) in expected_rows.items():
        row = by_addr.get(normalize_address(address))
        if row is None:
            failures.append(f"{label}: missing row {address}")
            continue
        if row.get("mnemonic") != mnemonic or row.get("operands") != operands:
            failures.append(f"{label}: {address} expected {mnemonic} {operands}, got {row.get('mnemonic')} {row.get('operands')}")


def check_instruction_context(base: Path, failures: list[str]) -> None:
    check_rows(base / "controller_target_post_range.tsv", EXPECTED_INSTRUCTION_ROWS, "target range", failures)
    check_rows(base / "raw_callsite_0048ff80_00490010.tsv", EXPECTED_RAW_CALLSITE_ROWS, "raw callsite range", failures)

    rows = read_tsv(base / "controller_context_instructions.tsv")
    by_addr = {normalize_address(row.get("instruction_addr", "")): row for row in rows}
    for address, (mnemonic, operands) in EXPECTED_CONTEXT_ROWS.items():
        row = by_addr.get(normalize_address(address))
        if row is None:
            failures.append(f"context instructions: missing row {address}")
            continue
        if row.get("mnemonic") != mnemonic or row.get("operands") != operands:
            failures.append(f"context instructions: {address} expected {mnemonic} {operands}, got {row.get('mnemonic')} {row.get('operands')}")


def run(base: Path) -> list[str]:
    failures: list[str] = []
    for filename, expected in EXPECTED_SUMMARIES.items():
        check_summary(base / filename, expected, filename, failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_decompile(base, failures)
    check_instruction_context(base, failures)
    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")
    base = args.base if args.base.is_absolute() else ROOT / args.base
    failures = run(base)
    if failures:
        print("Wave479 controller-target probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave479 controller-target probe: PASS")
    print(f"Base: {base.relative_to(ROOT)}")
    print("Checked: dry/apply/readback summaries, metadata, tags, xrefs, decompile tokens, and focused disassembly context.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
