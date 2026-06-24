#!/usr/bin/env python3
"""Validate Wave470 CPlayer lifecycle/view static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave470-cplayer-view-current"
COMMON_TAGS = {"static-reaudit", "cplayer-view-wave470", "retail-binary-evidence", "source-bridge"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 7,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 3,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 7,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 3,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 7,
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
    "0x004d2780": target(
        "CPlayer__ctor",
        "void * __thiscall CPlayer__ctor(void * this, int player_number)",
        ["Wave470", "CPlayer constructor", "0x005de770", "Player.cpp CPlayer::CPlayer(int number)", "CAREER-adjacent per-player flag"],
        ["cplayer", "constructor", "camera-view", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CGenericActiveReader__SetReader", "0x2c", "0x24", "0x28"],
    ),
    "0x004d2810": target(
        "CPlayer__scalar_deleting_dtor",
        "void * __thiscall CPlayer__scalar_deleting_dtor(void * this, byte flags)",
        ["Wave470", "scalar-deleting destructor", "0x005de770", "ret 0x4", "CDXMemoryManager"],
        ["cplayer", "destructor", "scalar-deleting-dtor", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CPlayer__dtor_base", "flags", "CDXMemoryManager__Free", "return this"],
    ),
    "0x004d2830": target(
        "CPlayer__dtor_base",
        "void __fastcall CPlayer__dtor_base(void * this)",
        ["Wave470", "destructor-base cleanup", "active BattleEngine reader", "CMonitor__Shutdown"],
        ["cplayer", "destructor", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CSPtrSet__Remove", "CMonitor__Shutdown", "0x1c"],
    ),
    "0x004d28a0": target(
        "CPlayer__Init",
        "void __fastcall CPlayer__Init(void * this)",
        ["Wave470", "CPlayer::Init", "CPlayer__GotoFPView", "PLATFORM__GetSysTimeFloat", "+0x4c"],
        ["cplayer", "camera-view", "signature-corrected", "comment-hardened"],
        ["CPlayer__GotoFPView", "PLATFORM__GetSysTimeFloat", "0x4c"],
    ),
    "0x004d28c0": target(
        "CPlayer__GotoFPView",
        "void __fastcall CPlayer__GotoFPView(void * this)",
        ["Wave470", "CPlayer::GotoFPView", "view mode 1", "CGame__SetCurrentCamera", "runtime camera behavior"],
        ["cplayer", "camera-view", "first-person-view", "signature-corrected", "comment-hardened"],
        ["CGame__SetCurrentCamera", "0x24) = 1", "OID__AllocObject(8"],
    ),
    "0x004d29c0": target(
        "CPlayer__Goto3rdPersonView",
        "void __fastcall CPlayer__Goto3rdPersonView(void * this)",
        ["Wave470", "CPlayer::Goto3rdPersonView", "view mode 2", "CThing3rdPersonCamera__ctor", "runtime camera behavior"],
        ["cplayer", "camera-view", "third-person-view", "signature-corrected", "comment-hardened"],
        ["CThing3rdPersonCamera__ctor", "CGame__SetCurrentCamera", "0x24) = 2"],
    ),
    "0x004d2a50": target(
        "CPlayer__GotoControlView",
        "void __fastcall CPlayer__GotoControlView(void * this)",
        ["Wave470", "CPlayer::GotoControlView", "preferred control view mode", "CPlayer__GotoFPView", "CPlayer__Goto3rdPersonView"],
        ["cplayer", "camera-view", "control-view", "signature-corrected", "comment-hardened"],
        ["CPlayer__GotoFPView", "CPlayer__Goto3rdPersonView", "0x28"],
    ),
}

EXPECTED_XREF_EDGES = {
    ("0x004d2780", "0x0046cf1a", "CGame__LoadLevel"),
    ("0x004d2810", "0x005de774", "<no_function>"),
    ("0x004d2830", "0x004d2813", "CPlayer__scalar_deleting_dtor"),
    ("0x004d28a0", "0x0046d1b3", "CGame__PostLoadProcess"),
    ("0x004d28c0", "0x004d28a3", "CPlayer__Init"),
    ("0x004d28c0", "0x004d2a59", "CPlayer__GotoControlView"),
    ("0x004d29c0", "0x004d2a66", "CPlayer__GotoControlView"),
    ("0x004d2a50", "0x00408bcd", "CMonitor__Process"),
}

EXPECTED_INSTRUCTIONS = {
    ("0x004d2780", "0x004d27b6", "MOV", "dword ptr [ESI + 0x2c], EDX", "89 56 2c"),
    ("0x004d2780", "0x004d27d0", "MOV", "dword ptr [ESI + 0x24], 0x1", "c7 46 24 01 00 00 00"),
    ("0x004d2780", "0x004d27d7", "MOV", "dword ptr [ESI + 0x28], 0x1", "c7 46 28 01 00 00 00"),
    ("0x004d2780", "0x004d280c", "RET", "0x4", "c2 04 00"),
    ("0x004d2810", "0x004d2813", "CALL", "0x004d2830", "e8 18 00 00 00"),
    ("0x004d2810", "0x004d2818", "TEST", "byte ptr [ESP + 0x8], 0x1", "f6 44 24 08 01"),
    ("0x004d2810", "0x004d282d", "RET", "0x4", "c2 04 00"),
    ("0x004d2830", "0x004d286f", "CALL", "0x004e5bd0", "e8 5c 33 01 00"),
    ("0x004d2830", "0x004d287e", "CALL", "0x004bac40", "e8 bd 83 fe ff"),
    ("0x004d28a0", "0x004d28a3", "CALL", "0x004d28c0", "e8 18 00 00 00"),
    ("0x004d28a0", "0x004d28ad", "CALL", "0x005159e0", "e8 2e 31 04 00"),
    ("0x004d28c0", "0x004d28f7", "MOV", "dword ptr [EBP + 0x24], 0x1", "c7 45 24 01 00 00 00"),
    ("0x004d28c0", "0x004d29a0", "CALL", "0x004705e0", "e8 3b dc f9 ff"),
    ("0x004d29c0", "0x004d29f0", "MOV", "dword ptr [ESI + 0x24], 0x2", "c7 46 24 02 00 00 00"),
    ("0x004d29c0", "0x004d2a12", "CALL", "0x00418ef0", "e8 d9 64 f4 ff"),
    ("0x004d2a50", "0x004d2a53", "CMP", "dword ptr [ESI + 0x28], 0x1", "83 7e 28 01"),
    ("0x004d2a50", "0x004d2a59", "CALL", "0x004d28c0", "e8 62 fe ff ff"),
    ("0x004d2a50", "0x004d2a66", "CALL", "0x004d29c0", "e8 55 ff ff ff"),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime camera behavior proven",
    "exact layout proven",
    "exact career field proven",
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
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return {}
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def check_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    actual = parse_summary(path)
    if not actual:
        failures.append(f"{path.name}: missing SUMMARY line")
        return
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            failures.append(f"{path.name}: {key} expected {expected_value}, got {actual_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name}: missing Ghidra save success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    if len(rows) < len(TARGETS):
        failures.append(f"post_metadata.tsv: expected at least {len(TARGETS)} rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("status") != "OK":
            failures.append(f"{address}: metadata status {row.get('status')!r}")
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: expected name {expected['name']!r}, got {row.get('name')!r}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address}: expected signature {expected['signature']!r}, got {row.get('signature')!r}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[index]
            if token not in comment:
                failures.append(f"{address}: comment missing token {token!r}")
        lowered = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    seen: dict[str, set[str]] = {}
    for row in rows:
        address = normalize_address(row.get("address", ""))
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        seen[address] = tags
    for address, expected in TARGETS.items():
        actual = seen.get(normalize_address(address), set())
        for tag in expected["tags"]:  # type: ignore[index]
            if tag not in actual:
                failures.append(f"{address}: missing tag {tag!r}; actual={sorted(actual)!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    edges = {(row.get("target_addr", ""), row.get("from_addr", ""), row.get("from_function", "")) for row in rows}
    for edge in EXPECTED_XREF_EDGES:
        if edge not in edges:
            failures.append(f"post_xrefs.tsv: missing xref edge {edge!r}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, expected in TARGETS.items():
        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing post decompile export")
            continue
        for token in expected["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, token):
                failures.append(f"{address}: decompile missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token in decompile.lower():
                failures.append(f"{address}: decompile contains overclaim token {token!r}")


def check_instructions(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    seen = {
        (
            normalize_address(row.get("target_addr", "")),
            normalize_address(row.get("instruction_addr", "")),
            row.get("mnemonic", ""),
            row.get("operands", ""),
            row.get("bytes", ""),
        )
        for row in rows
    }
    for expected in EXPECTED_INSTRUCTIONS:
        if expected not in seen:
            failures.append(f"post_instructions.tsv: missing instruction evidence {expected!r}")


def run_checks(base: Path = BASE) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, failures)
    check_summary(base / "verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_decompile(base, failures)
    check_instructions(base, failures)
    return ("PASS" if not failures else "FAIL", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    status, failures = run_checks(args.base)
    print(f"STATUS {status}")
    for failure in failures:
        print(f"FAIL {failure}")
    if args.check and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
