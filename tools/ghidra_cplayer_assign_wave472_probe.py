#!/usr/bin/env python3
"""Validate Wave472 CPlayer AssignBattleEngine metadata correction."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave472-cplayer-assign-battleengine"
ADDRESS = "0x004d3080"
EXPECTED_NAME = "CPlayer__AssignBattleEngine"
EXPECTED_SIGNATURE = "void __thiscall CPlayer__AssignBattleEngine(void * this, void * battle_engine)"
COMMON_TAGS = {"static-reaudit", "cplayer-assign-wave472", "retail-binary-evidence", "source-bridge"}
EXPECTED_TAGS = sorted(
    COMMON_TAGS
    | {
        "cplayer",
        "battleengine-reader",
        "assign-battleengine",
        "god-mode-bridge",
        "signature-corrected",
        "comment-hardened",
    }
)
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
EXPECTED_VERIFY_DRY = EXPECTED_DRY

COMMENT_TOKENS = [
    "Wave472",
    "CPlayer::AssignBattleEngine",
    "[ESP+4]",
    "battle_engine",
    "this+0x1c",
    "battle_engine+0x574",
    "this+0x20",
    "RET 0x4",
    "four caller callsites",
    "runtime god/vulnerability behavior",
]
DECOMPILE_TOKENS = [
    "CPlayer__AssignBattleEngine",
    "battle_engine",
    "CGenericActiveReader__SetReader",
    "0x574",
    "0xe0",
    "0x154",
]
EXPECTED_XREF_EDGES = {
    ("0x004d3080", "0x0046d0dc", "CGame__PostLoadProcess"),
    ("0x004d3080", "0x0046d1ac", "CGame__PostLoadProcess"),
    ("0x004d3080", "0x0047034f", "CGame__RespawnPlayer"),
    ("0x004d3080", "0x004703cb", "CGame__RespawnPlayer"),
}
EXPECTED_CALLSITES = {
    "0x0046d0dc",
    "0x0046d1ac",
    "0x0047034f",
    "0x004703cb",
}
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime god/vulnerability behavior proven",
    "exact layout proven",
    "exact virtual method identities proven",
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
            "target_addr",
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
    if len(rows) != 1:
        failures.append(f"post_metadata.tsv: expected 1 row, got {len(rows)}")
    row = row_by_address(rows, ADDRESS)
    if row is None:
        failures.append(f"{ADDRESS}: missing metadata row")
        return
    if row.get("name") != EXPECTED_NAME:
        failures.append(f"{ADDRESS}: expected name {EXPECTED_NAME}, got {row.get('name')}")
    if row.get("signature") != EXPECTED_SIGNATURE:
        failures.append(f"{ADDRESS}: expected signature {EXPECTED_SIGNATURE}, got {row.get('signature')}")
    if "param_" in row.get("signature", ""):
        failures.append(f"{ADDRESS}: signature still contains param_N")
    comment = row.get("comment", "")
    for token in COMMENT_TOKENS:
        if not token_present(comment, token):
            failures.append(f"{ADDRESS}: comment missing token {token!r}")
    for token in OVERCLAIM_TOKENS:
        if token_present(comment, token):
            failures.append(f"{ADDRESS}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    row = row_by_address(rows, ADDRESS)
    if row is None:
        failures.append(f"{ADDRESS}: missing tag row")
        return
    tags = {tag for tag in row.get("tags", "").split(";") if tag}
    for tag in EXPECTED_TAGS:
        if tag not in tags:
            failures.append(f"{ADDRESS}: missing tag {tag!r}")


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
    by_addr = {normalize_address(row.get("address", "")): row for row in rows}
    entry = by_addr.get("0x004d3080", {})
    if entry.get("mnemonic") != "MOV" or "[ESP + 0x4]" not in entry.get("operands", ""):
        failures.append("0x004d3080: missing [ESP+4] argument load")
    ret = by_addr.get("0x004d30c2", {})
    if ret.get("mnemonic") != "RET" or "0x4" not in ret.get("operands", "") or ret.get("bytes", "").upper() != "C2 04 00":
        failures.append("0x004d30c2: missing RET 0x4 evidence")
    required_tokens = [
        ("0x004d308e", "CALL", "0x00401000"),
        ("0x004d309c", "CALL", "0x00401000"),
        ("0x004d30ae", "CALL", "0xe0"),
        ("0x004d30ba", "CALL", "0x154"),
    ]
    for address, mnemonic, operand_token in required_tokens:
        row = by_addr.get(address, {})
        if row.get("mnemonic") != mnemonic or operand_token.lower() not in row.get("operands", "").lower():
            failures.append(f"{address}: missing instruction evidence {mnemonic} {operand_token}")


def check_callers(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_caller_instructions.tsv")
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(normalize_address(row.get("target_addr", "")), []).append(row)
    for callsite in EXPECTED_CALLSITES:
        group = grouped.get(normalize_address(callsite), [])
        target = next((row for row in group if row.get("role") == "TARGET"), None)
        if target is None or target.get("mnemonic") != "CALL" or "0x004d3080" not in target.get("operands", ""):
            failures.append(f"{callsite}: missing call to {ADDRESS}")
            continue
        before_rows = [row for row in group if row.get("role") == "BEFORE" and -3 <= int(row.get("ordinal", "0")) <= -1]
        pushes = [row for row in before_rows if row.get("mnemonic") == "PUSH"]
        if len(pushes) != 1:
            failures.append(f"{callsite}: expected one nearby pushed BattleEngine argument, got {len(pushes)}")
        all_before_rows = [row for row in group if row.get("role") == "BEFORE"]
        if not any(row.get("mnemonic") == "MOV" and "ECX" in row.get("operands", "") for row in all_before_rows):
            failures.append(f"{callsite}: missing nearby ECX receiver setup")


def check_decompile(base: Path, failures: list[str]) -> None:
    text = decompile_text_for(base, ADDRESS)
    if not text:
        failures.append(f"{ADDRESS}: missing post decompile text")
        return
    for token in DECOMPILE_TOKENS:
        if not token_present(text, token):
            failures.append(f"{ADDRESS}: decompile missing token {token!r}")
    if "param_" in text:
        failures.append(f"{ADDRESS}: post decompile still contains param_N")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, "dry.log", failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, "apply.log", failures)
    check_summary(base / "verify_dry.log", EXPECTED_VERIFY_DRY, "verify_dry.log", failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_disassembly(base, failures)
    check_callers(base, failures)
    check_decompile(base, failures)
    return ("PASS" if not failures else "FAIL", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    status, failures = run_checks(args.base)
    print(f"ghidra_cplayer_assign_wave472_probe: {status} base={args.base}")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
