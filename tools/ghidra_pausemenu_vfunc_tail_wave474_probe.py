#!/usr/bin/env python3
"""Validate Wave474 pause/simple-game-menu vfunc tail hardening."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave474-pausemenu-vfunc-tail"

EXPECTED_SIGNATURES = {
    "0x004d15d0": "void __thiscall CPauseMenu__VFunc_03_HandleMenuControlInput(void * this, void * control_context, int button_id, int button_context)",
    "0x004d1730": "void * __thiscall CSimpleGameMenu__scalar_deleting_dtor(void * this, int flags)",
    "0x004d1750": "void __fastcall CSimpleGameMenu__dtor_base(void * simple_game_menu)",
}
EXPECTED_NAMES = {
    "0x004d15d0": "CPauseMenu__VFunc_03_HandleMenuControlInput",
    "0x004d1730": "CSimpleGameMenu__scalar_deleting_dtor",
    "0x004d1750": "CSimpleGameMenu__dtor_base",
}
EXPECTED_TAGS = {
    "0x004d15d0": {
        "static-reaudit",
        "pausemenu-vfunc-tail-wave474",
        "retail-binary-evidence",
        "pause-menu",
        "control-input",
        "vtable-slot",
        "name-corrected",
        "signature-corrected",
        "comment-hardened",
    },
    "0x004d1730": {
        "static-reaudit",
        "pausemenu-vfunc-tail-wave474",
        "retail-binary-evidence",
        "simple-game-menu",
        "destructor",
        "name-corrected",
        "signature-corrected",
        "comment-hardened",
    },
    "0x004d1750": {
        "static-reaudit",
        "pausemenu-vfunc-tail-wave474",
        "retail-binary-evidence",
        "simple-game-menu",
        "destructor",
        "name-corrected",
        "signature-corrected",
        "comment-hardened",
    },
}
COMMENT_TOKENS = {
    "0x004d15d0": [
        "Wave474",
        "timestamp at this+0x2c",
        "this+0x14/this+0x24",
        "button 0x33",
        "button 0x2e",
        "RET 0x0c",
        "runtime UI behavior",
    ],
    "0x004d1730": [
        "Wave474",
        "scalar-deleting destructor wrapper",
        "CSimpleGameMenu__dtor_base",
        "flags bit 0",
        "RET 0x4",
        "runtime UI behavior",
    ],
    "0x004d1750": [
        "Wave474",
        "destructor body",
        "shared no-op vtable",
        "+0x3c",
        "CMenuItemRange",
        "CMonitor",
        "runtime UI behavior",
    ],
}
EXPECTED_XREFS = {
    ("0x004d15d0", "0x005de708", "<no_function>"),
    ("0x004d1730", "0x005de720", "<no_function>"),
    ("0x004d1750", "0x004d1733", "CSimpleGameMenu__scalar_deleting_dtor"),
}
EXPECTED_DRY = {
    "updated": 0,
    "skipped": 3,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 3,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 3,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 3,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY = {
    "updated": 0,
    "skipped": 3,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
OVERCLAIMS = (
    "runtime UI behavior proven",
    "exact layout proven",
    "source identity proven",
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
        r"updated=(?P<updated>\d+) skipped=(?P<skipped>\d+) created=(?P<created>\d+) "
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
    if len(rows) != 3:
        failures.append(f"post_metadata.tsv: expected 3 rows, got {len(rows)}")
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
    pause_rows = read_tsv(base / "post_disasm_004d15d0.tsv")
    by_addr = {normalize_address(row.get("address", "")): row for row in pause_rows}
    for addr in ("0x004d1647", "0x004d166e", "0x004d16f3"):
        row = by_addr.get(addr, {})
        if row.get("mnemonic") != "RET" or row.get("operands") != "0xc":
            failures.append(f"{addr}: missing RET 0x0c evidence")
    if by_addr.get("0x004d1665", {}).get("operands") != "0x004d0810":
        failures.append("0x004d1665: missing CPauseMenu__ButtonPressed call")
    if by_addr.get("0x004d1676", {}).get("operands") != "0x004d16f6":
        failures.append("0x004d1676: missing resume branch evidence")

    dtor_rows = read_tsv(base / "post_disasm_004d1730_1750.tsv")
    by_addr = {normalize_address(row.get("address", "")): row for row in dtor_rows}
    if by_addr.get("0x004d1733", {}).get("operands") != "0x004d1750":
        failures.append("0x004d1733: missing destructor-body call")
    if by_addr.get("0x004d1738", {}).get("operands") != "byte ptr [ESP + 0x8], 0x1":
        failures.append("0x004d1738: missing flags bit-0 test")
    if by_addr.get("0x004d174d", {}).get("operands") != "0x4":
        failures.append("0x004d174d: missing RET 0x4")
    if by_addr.get("0x004d176f", {}).get("operands") != "dword ptr [EBX], 0x5de71c":
        failures.append("0x004d176f: missing vtable restore")
    if by_addr.get("0x004d179c", {}).get("operands") != "0x0044b1d0":
        failures.append("0x004d179c: missing active-reader destructor call")
    if by_addr.get("0x004d17ef", {}).get("operands") != "0x004bac40":
        failures.append("0x004d17ef: missing CMonitor__Shutdown call")
    if by_addr.get("0x004d1805", {}).get("mnemonic") != "RET":
        failures.append("0x004d1805: missing destructor-body RET")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, tokens in {
        "0x004d15d0": (
            "CPauseMenu__VFunc_03_HandleMenuControlInput",
            "button_id",
            "CPauseMenu__ButtonPressed",
            "CPauseMenu__ResumeGameAndPersistOptions",
            "Controls__FindFirstFreeBindingSlot",
            "CMenuItemRange__ResetIterator",
        ),
        "0x004d1730": (
            "CSimpleGameMenu__scalar_deleting_dtor",
            "CSimpleGameMenu__dtor_base",
            "flags",
            "CDXMemoryManager__Free",
        ),
        "0x004d1750": (
            "CSimpleGameMenu__dtor_base",
            "CGenericActiveReader__dtor",
            "CSPtrSet__Clear",
            "CMenuItemRange__Destructor",
            "CMonitor__Shutdown",
        ),
    }.items():
        text = decompile_text_for(base, address)
        for token in tokens:
            if not token_present(text, token):
                failures.append(f"{address} decompile missing token {token!r}")


def run(base: Path) -> list[str]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, "dry.log", failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, "apply.log", failures)
    check_summary(base / "verify_dry.log", EXPECTED_VERIFY, "verify_dry.log", failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_disassembly(base, failures)
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
    print(f"PASS: Wave474 pause/simple-game-menu vfunc-tail evidence validated at {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
