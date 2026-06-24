#!/usr/bin/env python3
"""Validate Wave476 particle parent-transform owner/signature correction."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave476-particle-boundary-004c0150"

TARGET = "0x004c0150"
EXPECTED_NAME = "CParticle__ApplyParentTransformOrStoreLink"
EXPECTED_SIGNATURE = (
    "void __stdcall CParticle__ApplyParentTransformOrStoreLink"
    "(void * particle, void * parent_particle, int link_parent_only)"
)
EXPECTED_TAGS = {
    "comment-hardened",
    "owner-corrected",
    "parent-transform",
    "particle",
    "particle-parent-transform-wave476",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}
COMMENT_TOKENS = [
    "Wave476 owner/signature correction",
    "raw caller 0x004c524f",
    "particle pointer",
    "parent-particle pointer",
    "link-parent-only flag",
    "no current CUnitAI evidence",
    "particle +0x58",
    "+0xa0",
    "+0x38/+0x3c/+0x40",
    "runtime particle behavior",
    "rebuild parity remain unproven",
]
DECOMPILE_TOKENS = [
    "particle",
    "parent_particle",
    "link_parent_only",
    "particle + 0x58",
    "+ 0xa0",
    "Vec3__SetXYZ",
    "Mat34__SetRows",
    "Mat34__TransformVec3ByBasisToOut",
]
EXPECTED_XREF = (TARGET, "0x004c524f", "<no_function>")
EXPECTED_DRY = {
    "updated": 0,
    "skipped": 1,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 1,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 1,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 1,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 1,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
OVERCLAIMS = (
    "runtime particle behavior proven",
    "exact source identity proven",
    "raw caller boundary proven",
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


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    wanted = normalize_address(address)[2:]
    for path in directory.glob(f"{wanted}_*.c"):
        return read_text(path)
    return ""


def check_summary(path: Path, expected: dict[str, int], label: str, failures: list[str]) -> None:
    actual = parse_summary(path)
    if actual != expected:
        failures.append(f"{label}: expected summary {expected}, got {actual or '<missing>'}")
    if "REPORT: Save succeeded" not in read_text(path):
        failures.append(f"{label}: missing REPORT: Save succeeded")


def check_metadata(base: Path, failures: list[str]) -> None:
    row = row_by_address(read_tsv(base / "post_metadata.tsv"), TARGET)
    if row is None:
        failures.append(f"{TARGET}: missing metadata row")
        return
    if row.get("name") != EXPECTED_NAME:
        failures.append(f"{TARGET}: expected name {EXPECTED_NAME}, got {row.get('name')}")
    if row.get("signature") != EXPECTED_SIGNATURE:
        failures.append(f"{TARGET}: expected signature {EXPECTED_SIGNATURE}, got {row.get('signature')}")
    signature = row.get("signature", "")
    if "param_" in signature:
        failures.append(f"{TARGET}: signature still contains param_N")
    if "CUnitAI" in row.get("name", "") or "CUnitAI" in signature:
        failures.append(f"{TARGET}: metadata still contains CUnitAI")
    comment = row.get("comment", "")
    for token in COMMENT_TOKENS:
        if not token_present(comment, token):
            failures.append(f"{TARGET}: comment missing token {token!r}")
    for token in OVERCLAIMS:
        if token_present(comment, token):
            failures.append(f"{TARGET}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    row = row_by_address(read_tsv(base / "post_tags.tsv"), TARGET)
    if row is None:
        failures.append(f"{TARGET}: missing tag row")
        return
    tags = {tag for tag in row.get("tags", "").split(";") if tag}
    missing = sorted(EXPECTED_TAGS - tags)
    if missing:
        failures.append(f"{TARGET}: missing tags {missing}")


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
    if EXPECTED_XREF not in edges:
        failures.append(f"post_xrefs.tsv: missing xref edge {EXPECTED_XREF}")


def check_decompile(base: Path, failures: list[str]) -> None:
    text = decompile_text_for(base, TARGET)
    if not text:
        failures.append(f"{TARGET}: missing post decompile text")
        return
    for token in DECOMPILE_TOKENS:
        if not token_present(text, token):
            failures.append(f"{TARGET}: decompile missing token {token!r}")
    for token in OVERCLAIMS:
        if token_present(text, token):
            failures.append(f"{TARGET}: decompile contains overclaim token {token!r}")


def check_ranges(base: Path, failures: list[str]) -> None:
    caller_rows = read_tsv(base / "post_004c51e0_004c5290_caller_range.tsv")
    caller_by_addr = {normalize_address(row.get("address", "")): row for row in caller_rows}
    expected_caller = {
        "0x004c521f": ("CALL", "0x004cb5c0"),
        "0x004c524a": ("PUSH", "ECX"),
        "0x004c524b": ("PUSH", "EDX"),
        "0x004c524c": ("PUSH", "ESI"),
        "0x004c524f": ("CALL", "0x004c0150"),
    }
    for address, (mnemonic, operands) in expected_caller.items():
        row = caller_by_addr.get(address)
        if row is None:
            failures.append(f"{address}: missing caller-range row")
            continue
        if row.get("mnemonic") != mnemonic or row.get("operands") != operands:
            failures.append(f"{address}: expected {mnemonic} {operands}, got {row.get('mnemonic')} {row.get('operands')}")

    range_rows = read_tsv(base / "post_004c0000_004c036f_range.tsv")
    range_by_addr = {normalize_address(row.get("address", "")): row for row in range_rows}
    for address in ("0x004c016b", "0x004c035f"):
        row = range_by_addr.get(address)
        if row is None:
            failures.append(f"{address}: missing callee-range row")
        elif row.get("mnemonic") != "RET" or row.get("operands") != "0xc":
            failures.append(f"{address}: expected RET 0xc, got {row.get('mnemonic')} {row.get('operands')}")


def run(base: Path) -> list[str]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, "dry.log", failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, "apply.log", failures)
    check_summary(base / "verify_dry.log", EXPECTED_VERIFY_DRY, "verify_dry.log", failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_decompile(base, failures)
    check_ranges(base, failures)
    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true", help="Compatibility flag for npm verification scripts.")
    args = parser.parse_args(argv)

    failures = run(args.base)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: Wave476 particle parent-transform evidence validated at {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
