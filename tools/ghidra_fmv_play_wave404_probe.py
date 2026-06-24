#!/usr/bin/env python3
"""Validate the Wave404 FMV console-command Ghidra metadata tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "fmv-play-wave404" / "current"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_fmv_play_wave404_2026-05-14.md"

ADDRESS = "0x004655d0"
EXPECTED_NAME = "con_fmv_play"
EXPECTED_SIGNATURE = "void __cdecl con_fmv_play(char * command_line)"
EXPECTED_TAGS = {
    "static-reaudit",
    "fmv-play-wave404",
    "console-command",
    "frontend-video",
    "fmv",
    "signature-corrected",
    "comment-hardened",
    "retail-binary-evidence",
}

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

COMMENT_TOKENS = (
    "Console command handler for fmv_play <filename>",
    "9-byte prefix",
    "DAT_006630cc",
    "DAT_0089d69c",
    "0x0089d690",
    "vtable slot +0x2c",
    "command_line+9",
    "CConsole__AddString",
    "runtime playback behavior",
    "rebuild parity remain unproven",
)
DECOMPILE_TOKENS = (
    "con_fmv_play(char * command_line)",
    "DAT_0089d69c",
    "DAT_006630cc",
    "CController__SetNonInteractiveSection(true)",
    "command_line + 9",
    "DAT_0089d690 + 0x2c",
    "CController__SetNonInteractiveSection(false)",
    "CConsole__AddString",
)
INSTRUCTION_TOKENS = (
    "CMP\tECX, 0x9",
    "MOV\t[0x0089d69c], EAX",
    "CALL\t0x0042d7d0",
    "MOV\tEAX, [0x0089d690]",
    "ADD\tESI, 0x9",
    "CALL\tdword ptr [EAX + 0x2c]",
    "PUSH\t0x629abc",
)
PUBLIC_NOTE_TOKENS = (
    ADDRESS,
    EXPECTED_NAME,
    EXPECTED_SIGNATURE,
    "fmv_play <filename>",
    "DATA xref",
    "0x004656b5",
    "DAT_006630cc",
    "DAT_0089d69c",
    "0x0089d690",
    "CController__SetNonInteractiveSection",
    "CConsole__AddString",
    "does not prove runtime playback behavior",
    "does not prove exact frontend video object type/layout",
    "does not prove rebuild parity",
)
OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime playback behavior proven",
    "frontend video object type proven",
    "exact frontend video object type/layout proven",
    "source identity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)


@dataclass
class ValidationResult:
    status: str
    failures: list[str]
    evidence: dict[str, object]


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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry", "entry_addr"):
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


def decompile_text_for(directory: Path, address: str, name: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_{name}.c"))
    if matches:
        return read_text(matches[0])
    fallback = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if fallback:
        return read_text(fallback[0])
    return ""


def parse_summary(path: Path) -> dict[str, int] | None:
    text = read_text(path)
    match = re.search(
        r"SUMMARY updated=(\d+) skipped=(\d+) created=(\d+) would_create=(\d+) "
        r"renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def validate(root: Path = ROOT, base: Path = BASE) -> ValidationResult:
    failures: list[str] = []

    metadata = read_tsv(base / "metadata_after.tsv")
    row = row_by_address(metadata, ADDRESS)
    if row is None:
        failures.append(f"missing metadata row for {ADDRESS}")
    else:
        if row.get("name") != EXPECTED_NAME:
            failures.append(f"{ADDRESS} expected name {EXPECTED_NAME}, found {row.get('name')}")
        if row.get("signature") != EXPECTED_SIGNATURE:
            failures.append(f"{ADDRESS} expected signature {EXPECTED_SIGNATURE}, found {row.get('signature')}")
        comment = row.get("comment", "")
        for token in COMMENT_TOKENS:
            if not token_present(comment, token):
                failures.append(f"{ADDRESS} comment missing token: {token}")

    decompile = decompile_text_for(base / "decompile_after", ADDRESS, EXPECTED_NAME)
    if not decompile:
        failures.append(f"{ADDRESS} missing decompile_after export")
    for token in DECOMPILE_TOKENS:
        if not token_present(decompile, token):
            failures.append(f"{ADDRESS} decompile missing token: {token}")

    xrefs = read_tsv(base / "xrefs_after.tsv")
    command_table_xrefs = [
        row
        for row in xrefs
        if normalize_address(row.get("target_addr", "")) == ADDRESS
        and normalize_address(row.get("from_addr", "")) == "0x004656b5"
        and row.get("ref_type") == "DATA"
    ]
    if len(command_table_xrefs) != 1:
        failures.append(f"{ADDRESS} expected one command-table DATA xref at 0x004656b5, found {len(command_table_xrefs)}")

    tags_row = row_by_address(read_tsv(base / "tags_after.tsv"), ADDRESS)
    if tags_row is None:
        failures.append(f"{ADDRESS} missing tags row")
    else:
        tags = {tag for tag in tags_row.get("tags", "").split(";") if tag}
        missing_tags = sorted(EXPECTED_TAGS - tags)
        if missing_tags:
            failures.append(f"{ADDRESS} missing tags: {', '.join(missing_tags)}")

    instruction_text = read_text(base / "instructions_after.tsv")
    for token in INSTRUCTION_TOKENS:
        if not token_present(instruction_text, token):
            failures.append(f"{ADDRESS} instructions missing token: {token}")

    dry = parse_summary(base / "apply_fmv_play_wave404_dry.log")
    apply = parse_summary(base / "apply_fmv_play_wave404_apply.log")
    if dry != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: expected {EXPECTED_DRY}, found {dry}")
    if apply != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: expected {EXPECTED_APPLY}, found {apply}")
    apply_log = read_text(base / "apply_fmv_play_wave404_apply.log")
    dry_log = read_text(base / "apply_fmv_play_wave404_dry.log")
    if "REPORT: Save succeeded" not in apply_log:
        failures.append("apply log missing REPORT: Save succeeded")
    if "LockException" in apply_log or "LockException" in dry_log:
        failures.append("headless apply/dry log contains LockException")

    note = read_text(root / "release" / "readiness" / "ghidra_fmv_play_wave404_2026-05-14.md")
    for token in PUBLIC_NOTE_TOKENS:
        if not token_present(note, token):
            failures.append(f"public note missing token: {token}")
    for token in OVERCLAIM_TOKENS:
        if token_present(note, token):
            failures.append(f"public note overclaim token present: {token}")

    status = "PASS" if not failures else "FAIL"
    evidence = {
        "target": ADDRESS,
        "name": EXPECTED_NAME,
        "signature": EXPECTED_SIGNATURE,
        "command_table_xrefs": len(command_table_xrefs),
        "metadata_rows": len(metadata),
        "tags_expected": sorted(EXPECTED_TAGS),
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    return ValidationResult(status=status, failures=failures, evidence=evidence)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return non-zero on validation failure.")
    parser.add_argument("--base", type=Path, default=BASE, help="Wave evidence directory.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root.")
    args = parser.parse_args()

    result = validate(root=args.root, base=args.base)
    print(json.dumps({"status": result.status, "failures": result.failures, "evidence": result.evidence}, indent=2))
    if args.check and result.failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
