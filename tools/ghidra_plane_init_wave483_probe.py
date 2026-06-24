#!/usr/bin/env python3
"""Validate Wave483 CPlane init signature/comment hardening."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave483-plane-init-004d19d0"

TARGET = "0x004d19d0"
TARGET_NAME = "CPlane__Init"
EXPECTED_SIGNATURE = "void __thiscall CPlane__Init(void * this, void * init_thing)"

EXPECTED_SUMMARIES = {
    "apply_plane_init_wave483_dry.log": {
        "updated": 0,
        "skipped": 1,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_plane_init_wave483_commentfix_apply.log": {
        "updated": 1,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_plane_init_wave483_final_verify_dry.log": {
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
    "aircraft",
    "comment-hardened",
    "hardpoint",
    "init",
    "plane-init-wave483",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

COMMENT_TOKENS = [
    "init_thing+0x80",
    "CAirUnit__Init",
    "0x30 guide component",
    "this+0x208",
    "0x64 CWarspite component",
    "this+0x13c",
    "0x006243f8",
    "this+0x27c/this+0x280",
    "0x00622cec",
    "this+0x1d4",
    "this+0x284",
    "+/-0.8",
    "0x005e1954",
    "source body is absent",
    "runtime flight/launch behavior",
    "rebuild parity remain unproven",
]

DECOMPILE_TOKENS = [
    "void __thiscall CPlane__Init(void *this,void *init_thing)",
    "*(undefined4 *)((int)init_thing + 0x80) = 1",
    "CAirUnit__Init(this,init_thing)",
    "CAirGuide__ctor",
    "*(void **)((int)this + 0x208)",
    "CWarspite__Init(this,init_thing)",
    "*(undefined4 **)((int)this + 0x13c)",
    "s_launch_006243f8",
    "s_Engine_00622cec",
    "CSPtrSet__AddToTail((void *)((int)this + 0x1d4)",
    "Random__NextLCGAbs",
    "0x3f4ccccd",
    "0xbf4ccccd",
]

EXPECTED_INSTRUCTIONS = {
    "0x004d19e9": ("MOV", "EBX, dword ptr [ESP + 0x54]"),
    "0x004d19f0": ("MOV", "ESI, ECX"),
    "0x004d19f3": ("MOV", "[EBX + 0x80]"),
    "0x004d19fd": ("CALL", "0x00402ad0"),
    "0x004d1a28": ("CALL", "0x00402150"),
    "0x004d1a49": ("MOV", "[ESI + 0x208]"),
    "0x004d1a6a": ("CALL", "0x004fe710"),
    "0x004d1a82": ("MOV", "[ESI + 0x13c]"),
    "0x004d1a9c": ("PUSH", "0x6243f8"),
    "0x004d1b1e": ("PUSH", "0x622cec"),
    "0x004d1b9d": ("CALL", "0x004e5b20"),
    "0x004d1bae": ("CALL", "0x004de8d0"),
    "0x004d1bdc": ("MOV", "[ESI + 0x284], 0x3f4ccccd"),
    "0x004d1be8": ("MOV", "[ESI + 0x284], 0xbf4ccccd"),
    "0x004d1c04": ("RET", "0x4"),
}

OVERCLAIMS = (
    "source identity proven",
    "runtime flight behavior proven",
    "runtime launch behavior proven",
    "exact class layout proven",
    "cwarspite semantics proven",
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
        for key in ("address", "target_addr", "from_addr", "instruction_addr", "function_entry"):
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
    row = next((r for r in rows if r.get("address") == TARGET), None)
    if row is None:
        failures.append(f"{TARGET}: missing metadata row")
        return
    if row.get("name") != TARGET_NAME:
        failures.append(f"{TARGET}: expected name {TARGET_NAME}, got {row.get('name')}")
    if compact(row.get("signature", "")) != compact(EXPECTED_SIGNATURE):
        failures.append(f"{TARGET}: expected signature {EXPECTED_SIGNATURE}, got {row.get('signature')}")
    comment = row.get("comment", "")
    for token in COMMENT_TOKENS:
        if not token_present(comment, token):
            failures.append(f"{TARGET}: comment missing token {token!r}")
    if token_present(comment, "marks this+0x80"):
        failures.append(f"{TARGET}: comment contains stale this+0x80 flag claim")
    for overclaim in OVERCLAIMS:
        if token_present(comment, overclaim):
            failures.append(f"{TARGET}: comment contains overclaim {overclaim!r}")

    tag_rows = read_tsv(base / "post_tags.tsv")
    tag_row = next((r for r in tag_rows if r.get("address") == TARGET), None)
    if tag_row is None:
        failures.append(f"{TARGET}: missing tag row")
    else:
        actual_tags = set(filter(None, re.split(r"[;,]\s*", tag_row.get("tags", ""))))
        missing_tags = EXPECTED_TAGS - actual_tags
        if missing_tags:
            failures.append(f"{TARGET}: missing tags {sorted(missing_tags)}")


def check_decompile(base: Path, failures: list[str]) -> None:
    text = read_text(base / "post-decomp-final" / f"{TARGET[2:]}_{TARGET_NAME}.c")
    for token in DECOMPILE_TOKENS:
        if not token_present(text, token):
            failures.append(f"{TARGET}: decompile missing token {token!r}")
    if token_present(text, "((int)this + 0x80) = 1"):
        failures.append(f"{TARGET}: decompile has stale this+0x80 flag shape")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    row = next((r for r in rows if r.get("target_addr") == TARGET and r.get("from_addr") == "0x005e1954"), None)
    if row is None:
        failures.append(f"{TARGET}: missing data/table xref from 0x005e1954")
    elif row.get("ref_type") != "DATA":
        failures.append(f"{TARGET}: expected DATA xref from 0x005e1954, got {row.get('ref_type')}")


def check_instructions(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_addr = {row.get("instruction_addr"): row for row in rows}
    for address, (mnemonic, operand_token) in EXPECTED_INSTRUCTIONS.items():
        row = by_addr.get(address)
        if row is None:
            failures.append(f"{address}: missing instruction row")
            continue
        if row.get("mnemonic") != mnemonic or (operand_token and not token_present(row.get("operands", ""), operand_token)):
            failures.append(f"{address}: expected {mnemonic} {operand_token}, got {row.get('mnemonic')} {row.get('operands')}")


def run(base: Path = DEFAULT_BASE) -> list[str]:
    failures: list[str] = []
    check_summaries(base, failures)
    check_metadata(base, failures)
    check_decompile(base, failures)
    check_xrefs(base, failures)
    check_instructions(base, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = run(args.base)
    if failures:
        print("FAIL Wave483 plane init probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS Wave483 plane init probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
