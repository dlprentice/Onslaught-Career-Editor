#!/usr/bin/env python3
"""Validate Wave473 platform directory-path metadata hardening."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave473-platform-directory-path"

EXPECTED_SIGNATURES = {
    "0x004d2600": "void __stdcall Platform__CreateDirectoryPath(char * path, int strip_filename)",
    "0x0055f347": "int __cdecl Platform__CreateDirectoryWithErrno(char * path)",
}
EXPECTED_NAMES = {
    "0x004d2600": "Platform__CreateDirectoryPath",
    "0x0055f347": "Platform__CreateDirectoryWithErrno",
}
EXPECTED_TAGS = {
    "0x004d2600": {
        "static-reaudit",
        "platform-directory-wave473",
        "retail-binary-evidence",
        "signature-corrected",
        "comment-hardened",
        "platform",
        "directory-path",
        "recursive-directory-create",
        "ret-0x8",
    },
    "0x0055f347": {
        "static-reaudit",
        "platform-directory-wave473",
        "retail-binary-evidence",
        "signature-corrected",
        "comment-hardened",
        "platform",
        "directory-path",
        "createdirectorya-wrapper",
        "errno-bridge",
    },
}
COMMENT_TOKENS = {
    "0x004d2600": [
        "Wave473",
        "260-byte stack buffer",
        "strip_filename",
        "_strchr",
        "Platform__CreateDirectoryWithErrno",
        "RET 0x8",
        "CLIParams__ParseCommandLine",
        "runtime filesystem behavior",
    ],
    "0x0055f347": [
        "Wave473",
        "CreateDirectoryA",
        "GetLastError",
        "CRT__SetErrnoAndDosErrnoFromWinError_00567a35",
        "returns -1",
        "returns 0",
        "EnumerateSaveFiles_Main",
        "runtime filesystem behavior",
    ],
}
EXPECTED_XREFS = {
    ("0x004d2600", "0x00424091", "CLIParams__ParseCommandLine"),
    ("0x0055f347", "0x004d266b", "Platform__CreateDirectoryPath"),
    ("0x0055f347", "0x00514bfd", "EnumerateSaveFiles_Main"),
}
EXPECTED_DRY = {
    "updated": 0,
    "skipped": 2,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 2,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
OVERCLAIMS = (
    "runtime filesystem behavior proven",
    "path length safety proven",
    "exact caller intent proven",
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
            "instruction_addr",
            "function_entry",
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
    wanted = normalize_address(address)[2:]
    for path in directory.glob(f"{wanted}_*.c"):
        return read_text(path)
    return ""


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"SUMMARY updated=(?P<updated>\d+) skipped=(?P<skipped>\d+) created=(?P<created>\d+) "
        r"would_create=(?P<would_create>\d+) renamed=(?P<renamed>\d+) would_rename=(?P<would_rename>\d+) "
        r"missing=(?P<missing>\d+) bad=(?P<bad>\d+)",
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


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    if len(rows) != 2:
        failures.append(f"post_metadata.tsv: expected 2 rows, got {len(rows)}")
    for address, expected_signature in EXPECTED_SIGNATURES.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != EXPECTED_NAMES[address]:
            failures.append(f"{address}: expected name {EXPECTED_NAMES[address]}, got {row.get('name')}")
        if row.get("signature") != expected_signature:
            failures.append(f"{address}: expected signature {expected_signature}, got {row.get('signature')}")
        if "param_" in row.get("signature", ""):
            failures.append(f"{address}: signature still contains param_N")
        comment = row.get("comment", "")
        for token in COMMENT_TOKENS[address]:
            if not token_present(comment, token):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIMS:
            if token_present(comment, token):
                failures.append(f"{address}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    for address, expected in EXPECTED_TAGS.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing tag row")
            continue
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        missing = sorted(expected - tags)
        if missing:
            failures.append(f"{address}: missing tags {missing}")


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
    for edge in EXPECTED_XREFS:
        wanted = (normalize_address(edge[0]), normalize_address(edge[1]), edge[2])
        if wanted not in edges:
            failures.append(f"missing xref edge {wanted}")


def check_disassembly(base: Path, failures: list[str]) -> None:
    path_rows = read_tsv(base / "post_disasm_004d2600.tsv")
    by_addr = {normalize_address(row.get("address", "")): row for row in path_rows}
    if by_addr.get("0x004d2611", {}).get("operands") != "EDI, dword ptr [ESP + 0x110]":
        failures.append("0x004d2611: missing path stack-argument load")
    if by_addr.get("0x004d262b", {}).get("operands") != "EAX, dword ptr [ESP + 0x114]":
        failures.append("0x004d262b: missing strip_filename stack-argument load")
    if by_addr.get("0x004d2642", {}).get("mnemonic") != "CALL":
        failures.append("0x004d2642: missing _strrchr call")
    if by_addr.get("0x004d2655", {}).get("mnemonic") != "CALL":
        failures.append("0x004d2655: missing first _strchr call")
    if by_addr.get("0x004d266b", {}).get("operands") != "0x0055f347":
        failures.append("0x004d266b: missing directory-create wrapper call")
    ret = by_addr.get("0x004d268d", {})
    if ret.get("mnemonic") != "RET" or ret.get("operands") != "0x8":
        failures.append("0x004d268d: missing RET 0x8")

    wrapper_rows = read_tsv(base / "post_disasm_0055f347.tsv")
    by_addr = {normalize_address(row.get("address", "")): row for row in wrapper_rows}
    if by_addr.get("0x0055f34d", {}).get("mnemonic") != "CALL":
        failures.append("0x0055f34d: missing CreateDirectoryA import call")
    if by_addr.get("0x0055f357", {}).get("mnemonic") != "CALL":
        failures.append("0x0055f357: missing GetLastError import call")
    if by_addr.get("0x0055f366", {}).get("operands") != "0x00567a35":
        failures.append("0x0055f366: missing errno bridge call")
    if by_addr.get("0x0055f36c", {}).get("operands") != "EAX, 0xffffffff":
        failures.append("0x0055f36c: missing -1 return setup")
    if by_addr.get("0x0055f370", {}).get("mnemonic") != "XOR":
        failures.append("0x0055f370: missing zero return setup")


def check_callers(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_caller_instructions_wide.tsv")
    by_addr = {normalize_address(row.get("instruction_addr", "")): row for row in rows}
    if by_addr.get("0x0042403d", {}).get("operands") != "0x1":
        failures.append("0x0042403d: missing strip_filename push before Platform__CreateDirectoryPath")
    if by_addr.get("0x00424045", {}).get("operands") != "0x662cb0":
        failures.append("0x00424045: missing path-buffer push before Platform__CreateDirectoryPath")
    if by_addr.get("0x00424091", {}).get("operands") != "0x004d2600":
        failures.append("0x00424091: missing CLIParams call edge")
    if by_addr.get("0x00514bf8", {}).get("operands") != "0x63df94":
        failures.append("0x00514bf8: missing savegames-directory push before wrapper call")
    if by_addr.get("0x00514bfd", {}).get("operands") != "0x0055f347":
        failures.append("0x00514bfd: missing EnumerateSaveFiles_Main wrapper call")


def check_decompile(base: Path, failures: list[str]) -> None:
    text = decompile_text_for(base, "0x004d2600")
    for token in (
        "Platform__CreateDirectoryPath",
        "char * path",
        "int strip_filename",
        "Platform__CreateDirectoryWithErrno",
        "_strchr",
        "_strrchr",
    ):
        if not token_present(text, token):
            failures.append(f"0x004d2600 decompile missing token {token!r}")

    text = decompile_text_for(base, "0x0055f347")
    for token in (
        "Platform__CreateDirectoryWithErrno",
        "char * path",
        "CreateDirectoryA",
        "GetLastError",
        "CRT__SetErrnoAndDosErrnoFromWinError_00567a35",
    ):
        if not token_present(text, token):
            failures.append(f"0x0055f347 decompile missing token {token!r}")


def run(base: Path) -> list[str]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, "dry.log", failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, "apply.log", failures)
    check_summary(base / "verify_dry.log", EXPECTED_DRY, "verify_dry.log", failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_disassembly(base, failures)
    check_callers(base, failures)
    check_decompile(base, failures)
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
    print(f"PASS: Wave473 platform directory-path evidence validated at {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
