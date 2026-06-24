#!/usr/bin/env python3
"""Validate the Wave423 level-briefing/message-box saved-Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave423-level-briefing-messagebox" / "current"

COMMON_TAGS = {"static-reaudit", "level-briefing-messagebox-wave423", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x0048f540": {
        "name": "CLevelBriefingLog__ctor",
        "signature": "void * __thiscall CLevelBriefingLog__ctor(void * this)",
        "commentTokens": ["constructor", "0x005dc208", "+0x04/+0x08/+0x0c", "CTexture__FindTexture", "+0x10"],
        "decompileTokens": ["CTexture__FindTexture", "s_FrontEnd_v2_FE_Blank_tga_00629f68", "+ 0x10"],
        "tags": {"level-briefing-log", "constructor", "owner-corrected", "signature-hardened", "comment-hardened"},
        "xrefTokens": ["CGame__InitRestartLoop"],
    },
    "0x0048f5a0": {
        "name": "CLevelBriefingLog__scalar_deleting_dtor",
        "signature": "void * __thiscall CLevelBriefingLog__scalar_deleting_dtor(void * this, byte flags)",
        "commentTokens": ["scalar-deleting destructor", "CLevelBriefingLog__dtor", "flags bit 0", "OID__FreeObject", "RET 0x4"],
        "decompileTokens": ["CLevelBriefingLog__dtor", "OID__FreeObject", "flags"],
        "tags": {"level-briefing-log", "destructor", "owner-corrected", "signature-hardened", "comment-hardened"},
        "xrefTokens": ["DATA"],
    },
    "0x0048f5c0": {
        "name": "CLevelBriefingLog__dtor",
        "signature": "void __thiscall CLevelBriefingLog__dtor(void * this)",
        "commentTokens": ["destructor body", "0x005dc208", "+0x10", "CHud__DecrementCounter9C", "CMonitor__Shutdown"],
        "decompileTokens": ["CHud__DecrementCounter9C", "CMonitor__Shutdown", "+ 0x10"],
        "tags": {"level-briefing-log", "destructor", "owner-corrected", "signature-hardened", "comment-hardened"},
        "xrefTokens": ["CLevelBriefingLog__scalar_deleting_dtor"],
    },
    "0x0048ff90": {
        "name": "CMessageBox__ActivateWithFadeStep_0p1",
        "signature": "void __thiscall CMessageBox__ActivateWithFadeStep_0p1(void * this)",
        "commentTokens": ["activation helper", "+0x08", "+0x0c", "0.1f", "0x3dcccccd"],
        "decompileTokens": ["0x3dcccccd", "+ 0xc"],
        "tags": {"message-box", "activation", "signature-hardened", "comment-hardened"},
        "xrefTokens": ["CGameInterface__HandleMenuSelection", "CPauseMenu__ButtonPressed"],
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 4,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 3,
    "missing": 0,
    "bad": 0,
}

EXPECTED_APPLY = {
    "updated": 4,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 3,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

STALE_NAME_TOKENS = (
    "CLevelBriefingLog__ctor_like_0048f540",
    "CLevelBriefingLog__VFunc_01_0048f5a0",
    "CLevelBriefingLog__ctor_like_0048f5c0",
)

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime ui behavior proven",
    "runtime cleanup behavior proven",
    "complete object layout",
    "complete class layout",
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


def decompile_file_for(base: Path, address: str, name: str) -> Path:
    clean = address.lower().replace("0x", "")
    return base / "decompile_after" / f"{clean}_{name}.c"


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

    metadata_text = "\n".join(row.get("name", "") for row in metadata)
    for stale in STALE_NAME_TOKENS:
        if stale in metadata_text:
            failures.append(f"stale Wave423 name still present: {stale}")

    for address, expected in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')} != {expected['name']}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address}: signature mismatch {row.get('signature')} != {expected['signature']}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[union-attr]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: overclaim token present {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            actual_tags = {tag for tag in tag_row.get("tags", "").split(";") if tag}
            expected_tags = COMMON_TAGS | set(expected["tags"])  # type: ignore[arg-type]
            missing_tags = sorted(expected_tags - actual_tags)
            if missing_tags:
                failures.append(f"{address}: missing tags {', '.join(missing_tags)}")

        decompile_text = read_text(decompile_file_for(base, address, str(expected["name"])))
        if not decompile_text:
            failures.append(f"{address}: missing decompile after file")
        else:
            for token in expected["decompileTokens"]:  # type: ignore[union-attr]
                if not token_present(decompile_text, str(token)):
                    failures.append(f"{address}: missing decompile token {token!r}")

        xref_text = "\n".join("\t".join(row.values()) for row in rows_by_address(xrefs, address, key="target_addr"))
        if not xref_text:
            failures.append(f"{address}: missing xref row")
        else:
            for token in expected["xrefTokens"]:  # type: ignore[union-attr]
                if not token_present(xref_text, str(token)):
                    failures.append(f"{address}: missing xref token {token!r}")

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
    print("PASS: Wave423 level-briefing/message-box saved-Ghidra corrections validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
