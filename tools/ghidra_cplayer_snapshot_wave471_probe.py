#!/usr/bin/env python3
"""Validate Wave471 CPlayer snapshot-helper static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave471-cplayer-snapshot-current"
COMMON_TAGS = {"static-reaudit", "cplayer-snapshot-wave471", "retail-binary-evidence", "source-bridge"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 4,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 4,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 4,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004d2a70": target(
        "CPlayer__GetCurrentViewPoint",
        "void __thiscall CPlayer__GetCurrentViewPoint(void * this, void * out_current_view_point)",
        ["Wave471", "CPlayer::GetCurrentViewPoint", "16-byte", "RET 0x4", "runtime camera behavior"],
        ["cplayer", "camera-view", "snapshot", "view-point", "signature-corrected", "comment-hardened"],
        ["out_current_view_point", "DAT_008a9d58", "0x2c"],
    ),
    "0x004d2ae0": target(
        "CPlayer__GetCurrentViewOrientation",
        "void __thiscall CPlayer__GetCurrentViewOrientation(void * this, void * out_current_view_orientation)",
        ["Wave471", "CPlayer::GetCurrentViewOrientation", "DAT_0082b5c0", "12 dwords", "RET 0x4"],
        ["cplayer", "camera-view", "snapshot", "view-orientation", "signature-corrected", "comment-hardened"],
        ["out_current_view_orientation", "DAT_0082b5c0", "DAT_008a9d58"],
    ),
    "0x004d2b40": target(
        "CPlayer__GetOldCurrentViewPoint",
        "void __thiscall CPlayer__GetOldCurrentViewPoint(void * this, void * out_old_view_point)",
        ["Wave471", "CPlayer::GetOldCurrentViewPoint", "slot +0x8", "16-byte", "RET 0x4"],
        ["cplayer", "camera-view", "snapshot", "old-view-point", "signature-corrected", "comment-hardened"],
        ["out_old_view_point", "DAT_008a9d58", "0x2c"],
    ),
    "0x004d2bb0": target(
        "CPlayer__GetOldCurrentViewOrientation",
        "void __thiscall CPlayer__GetOldCurrentViewOrientation(void * this, void * out_old_view_orientation)",
        ["Wave471", "CPlayer::GetOldCurrentViewOrientation", "DAT_0082b5c0", "0x004d2c02", "RET 0x4"],
        ["cplayer", "camera-view", "snapshot", "old-view-orientation", "signature-corrected", "comment-hardened"],
        ["out_old_view_orientation", "DAT_0082b5c0", "DAT_008a9d58"],
    ),
}

EXPECTED_XREF_EDGES = {
    ("0x004d2a70", "0x0040d7d5", "CBattleEngine__GetInterpolatedAutoAimPos"),
    ("0x004d2a70", "0x0040ad8d", "CBattleEngine__CalcUnitOverCrossHair"),
    ("0x004d2ae0", "0x0040d7e8", "CBattleEngine__GetInterpolatedAutoAimPos"),
    ("0x004d2ae0", "0x0040ada0", "CBattleEngine__CalcUnitOverCrossHair"),
    ("0x004d2b40", "0x0040d7f8", "CBattleEngine__GetInterpolatedAutoAimPos"),
    ("0x004d2bb0", "0x0040d808", "CBattleEngine__GetInterpolatedAutoAimPos"),
}

EXPECTED_RETURNS = {
    ("004d2ad9", "RET", "0x4", "C2 04 00"),
    ("004d2b32", "RET", "0x4", "C2 04 00"),
    ("004d2baa", "RET", "0x4", "C2 04 00"),
    ("004d2c02", "RET", "0x4", "C2 04 00"),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime camera behavior proven",
    "exact layout proven",
    "camera-table indexing proven",
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry", "instruction_addr"):
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
    if len(rows) != len(TARGETS):
        failures.append(f"post_metadata.tsv: expected {len(TARGETS)} rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: expected name {expected['name']}, got {row.get('name')}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address}: expected signature {expected['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    if len(rows) != len(TARGETS):
        failures.append(f"post_tags.tsv: expected {len(TARGETS)} rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing tag row")
            continue
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        for tag in expected["tags"]:  # type: ignore[index]
            if str(tag) not in tags:
                failures.append(f"{address}: missing tag {tag!r}")


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
    for edge in EXPECTED_XREF_EDGES:
        wanted = (normalize_address(edge[0]), normalize_address(edge[1]), edge[2])
        if wanted not in edges:
            failures.append(f"missing xref edge {wanted}")


def check_disassembly(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_disasm_range.tsv")
    evidence = {
        (
            row.get("address", "").lower().removeprefix("0x"),
            row.get("mnemonic", ""),
            row.get("operands", ""),
            row.get("bytes", ""),
        )
        for row in rows
    }
    for expected in EXPECTED_RETURNS:
        if expected not in evidence:
            failures.append(f"missing return evidence {expected}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, expected in TARGETS.items():
        text = decompile_text_for(base, address)
        if not text:
            failures.append(f"{address}: missing decompile export")
            continue
        for token in expected["decompileTokens"]:  # type: ignore[index]
            if not token_present(text, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def run_checks(base: Path = BASE) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, "dry.log", failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, "apply.log", failures)
    check_summary(base / "verify_dry.log", EXPECTED_VERIFY_DRY, "verify_dry.log", failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_disassembly(base, failures)
    check_decompile(base, failures)
    return ("PASS" if not failures else "FAIL", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true", help="return non-zero on failure")
    args = parser.parse_args()

    status, failures = run_checks(args.base)
    print(f"STATUS {status}")
    for failure in failures:
        print(f"- {failure}")
    if args.check and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
