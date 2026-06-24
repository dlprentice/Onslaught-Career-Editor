#!/usr/bin/env python3
"""Validate the Wave424 CInitThing load saved-Ghidra correction."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave424-initthing-load" / "current"

ADDRESS = "0x0040e280"
NAME = "CInitThing__LoadFromMemBuffer"
SIGNATURE = "void __thiscall CInitThing__LoadFromMemBuffer(void * this, int version, void * mem_buffer)"

COMMON_TAGS = {"static-reaudit", "initthing-load-wave424", "retail-binary-evidence"}
TARGET_TAGS = {
    "initthing",
    "load",
    "source-aligned",
    "signature-corrected",
    "comment-hardened",
}

COMMENT_TOKENS = (
    "CInitThing::Load(short inVersion, CMEMBUFFER &inFile)",
    "version-gated",
    "+0xac/+0x1ac/+0x2ac",
    "+0x3ac/+0x3b0",
    "runtime level-load behavior and rebuild parity remain unproven",
)

DECOMPILE_TOKENS = (
    "CDXMemBuffer__Read",
    "(short)version",
    "+ 0xac",
    "+ 0x1ac",
    "+ 0x2ac",
    "+ 0x3b0",
)

XREF_TOKENS = ("CSquadInitThing__LoadFromMemBuffer",)

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 1,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

EXPECTED_APPLY = {
    "updated": 1,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime level-load behavior proven",
    "exact retail level loading proven",
    "complete CInitThing layout",
    "complete object layout",
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
        for key in ("address", "target_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if row.get(key) == wanted:
            return row
    return None


def rows_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if row.get(key) == wanted]


def parse_summary(path: Path) -> dict[str, int] | None:
    text = read_text(path)
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+"
        r"renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def check_summary(base: Path, failures: list[str]) -> None:
    for filename, expected in (("apply_dry.log", EXPECTED_DRY), ("apply_apply.log", EXPECTED_APPLY)):
        actual = parse_summary(base / filename)
        if actual is None:
            failures.append(f"{filename}: missing SUMMARY")
        elif actual != expected:
            failures.append(f"{filename}: summary mismatch {actual} != {expected}")


def decompile_file_for(base: Path) -> Path:
    clean = ADDRESS.lower().replace("0x", "")
    return base / "decompile_after" / f"{clean}_{NAME}.c"


def check_targets(base: Path = BASE) -> list[str]:
    failures: list[str] = []
    check_summary(base, failures)

    metadata = read_tsv(base / "metadata_after.tsv")
    tags = read_tsv(base / "tags_after.tsv")
    xrefs = read_tsv(base / "xrefs_after.tsv")

    if not metadata:
        failures.append("metadata_after.tsv missing or empty")
    if not tags:
        failures.append("tags_after.tsv missing or empty")
    if not xrefs:
        failures.append("xrefs_after.tsv missing or empty")

    row = row_by_address(metadata, ADDRESS)
    if row is None:
        failures.append(f"{ADDRESS}: missing metadata row")
    else:
        if row.get("name") != NAME:
            failures.append(f"{ADDRESS}: name mismatch {row.get('name')} != {NAME}")
        if row.get("signature") != SIGNATURE:
            failures.append(f"{ADDRESS}: signature mismatch {row.get('signature')} != {SIGNATURE}")
        comment = row.get("comment", "")
        for token in COMMENT_TOKENS:
            if not token_present(comment, token):
                failures.append(f"{ADDRESS}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{ADDRESS}: overclaim token present {token!r}")

    tag_row = row_by_address(tags, ADDRESS)
    if tag_row is None:
        failures.append(f"{ADDRESS}: missing tag row")
    else:
        actual_tags = {tag for tag in tag_row.get("tags", "").split(";") if tag}
        missing_tags = sorted((COMMON_TAGS | TARGET_TAGS) - actual_tags)
        if missing_tags:
            failures.append(f"{ADDRESS}: missing tags {', '.join(missing_tags)}")

    decompile_text = read_text(decompile_file_for(base))
    if not decompile_text:
        failures.append(f"{ADDRESS}: missing decompile after file")
    else:
        for token in DECOMPILE_TOKENS:
            if not token_present(decompile_text, token):
                failures.append(f"{ADDRESS}: missing decompile token {token!r}")

    xref_text = "\n".join("\t".join(row.values()) for row in rows_by_address(xrefs, ADDRESS, key="target_addr"))
    if not xref_text:
        failures.append(f"{ADDRESS}: missing xref row")
    else:
        for token in XREF_TOKENS:
            if not token_present(xref_text, token):
                failures.append(f"{ADDRESS}: missing xref token {token!r}")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="Wave artifact directory to validate")
    parser.add_argument("--check", action="store_true", help="Return non-zero on validation failure")
    args = parser.parse_args(argv)

    failures = check_targets(args.base)
    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("PASS: Wave424 CInitThing load saved-Ghidra correction validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
