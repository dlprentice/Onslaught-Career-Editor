#!/usr/bin/env python3
"""Validate Wave482 global tint render-state signature/comment hardening."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave482-global-tint-004d1710"

TARGET = "0x004d1710"
TARGET_NAME = "CDXEngine__SetGlobalTintColorOpaque"
EXPECTED_SIGNATURE = "void __cdecl CDXEngine__SetGlobalTintColorOpaque(uint tint_payload)"

EXPECTED_SUMMARIES = {
    "apply_global_tint_wave482_dry.log": {
        "updated": 0,
        "skipped": 1,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_global_tint_wave482_apply.log": {
        "updated": 1,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_global_tint_wave482_verify_dry.log": {
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
    "global-tint-wave482",
    "global-write",
    "render-state",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

COMMENT_TOKENS = [
    "0x0082b494",
    "0x0082b4ec",
    "0xff",
    "0xf6",
    "OptionsTail_Read",
    "0xe5/0xe6",
    "CD3DApplication__Initialize3DEnvironment",
    "0xe7",
    "CRenderQueue/CDXEngine multipass",
    "runtime visual behavior",
    "rebuild parity remain unproven",
]

DECOMPILE_TOKENS = [
    TARGET_NAME,
    "uint tint_payload",
    "_DAT_0082b4ec = 0xff",
    "_DAT_0082b494 = tint_payload",
]

EXPECTED_XREFS = {
    ("0x0042115a", "OptionsTail_Read"),
    ("0x0052b36d", "CD3DApplication__Initialize3DEnvironment"),
    ("0x0052b3f5", "CD3DApplication__Initialize3DEnvironment"),
    ("0x00552a7e", "CRenderQueue__RenderAll"),
    ("0x00553856", "CRenderQueue__RenderAll"),
    ("0x00553f9b", "CDXEngine__RenderMultipassLayerA"),
    ("0x0055415b", "CDXEngine__RenderMultipassLayerA"),
    ("0x0055455e", "CDXEngine__RenderMultipassLayerB"),
}

EXPECTED_CALLSITE_PUSHES = {
    "0x0042115a": "0xf6",
    "0x0052b36d": "0xe5",
    "0x0052b3f5": "0xe6",
    "0x00552a7e": "0xe7",
    "0x00553856": "0xe7",
    "0x00553f9b": "0xe7",
    "0x0055415b": "0xe7",
    "0x0055455e": "0xe7",
}

OVERCLAIMS = (
    "runtime visual behavior proven",
    "palette/color packing proven",
    "exact global layout proven",
    "consumer path proven",
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
    text = read_text(base / "post-decomp" / f"{TARGET[2:]}_{TARGET_NAME}.c")
    for token in DECOMPILE_TOKENS:
        if not token_present(text, token):
            failures.append(f"{TARGET}: decompile missing token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    actual = {(row.get("from_addr", ""), row.get("from_function", "")) for row in rows if row.get("target_addr") == TARGET}
    for expected in EXPECTED_XREFS:
        if expected not in actual:
            failures.append(f"missing xref {expected}")


def check_instructions(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_addr = {row.get("instruction_addr"): row for row in rows}
    expected = {
        "0x004d1710": ("MOV", "EAX, dword ptr [ESP + 0x4]"),
        "0x004d1714": ("MOV", "0x0082b4ec"),
        "0x004d171e": ("MOV", "0x0082b494"),
        "0x004d1723": ("RET", ""),
    }
    for address, (mnemonic, operand_token) in expected.items():
        row = by_addr.get(address)
        if row is None:
            failures.append(f"{address}: missing instruction row")
            continue
        if row.get("mnemonic") != mnemonic or (operand_token and not token_present(row.get("operands", ""), operand_token)):
            failures.append(f"{address}: expected {mnemonic} {operand_token}, got {row.get('mnemonic')} {row.get('operands')}")

    callsite_rows = read_tsv(base / "callsite_instructions.tsv")
    for call_addr, pushed_value in EXPECTED_CALLSITE_PUSHES.items():
        call_row = next(
            (row for row in callsite_rows if row.get("instruction_addr") == call_addr and row.get("mnemonic") == "CALL" and token_present(row.get("operands", ""), TARGET)),
            None,
        )
        if call_row is None:
            failures.append(f"{call_addr}: missing callsite CALL {TARGET}")
        push_row = next(
            (
                row
                for row in callsite_rows
                if row.get("target_raw") == call_addr and row.get("mnemonic") == "PUSH" and token_present(row.get("operands", ""), pushed_value)
            ),
            None,
        )
        if push_row is None:
            failures.append(f"{call_addr}: missing pushed value {pushed_value}")

    global_refs = read_tsv(base / "global_operand_refs.tsv")
    refs = {(row.get("instruction_addr"), row.get("operands", "")) for row in global_refs}
    for address, token in (("0x004d1714", "0x0082b4ec"), ("0x004d171e", "0x0082b494")):
        if not any(addr == address and token_present(operands, token) for addr, operands in refs):
            failures.append(f"{address}: missing exact global operand ref {token}")


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
        print("FAIL Wave482 global tint probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS Wave482 global tint probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
