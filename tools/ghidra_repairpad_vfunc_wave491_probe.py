#!/usr/bin/env python3
"""Validate Wave491 RepairPadAI vfunc static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave491-repairpad-vfunc-004d6d10"

TARGET = "0x004d6d10"
NAME = "CRepairPadAI__VFunc_11_UpdateDockCandidateReader"
SIGNATURE = "void * __fastcall CRepairPadAI__VFunc_11_UpdateDockCandidateReader(void * this)"
TAGS = {
    "static-reaudit",
    "repairpad-wave491",
    "repairpad-ai",
    "repairpad-dock-candidate",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "name-corrected",
}

EXPECTED_SUMMARIES = {
    "apply_repairpad_vfunc_wave491_dry.log": {
        "updated": 0,
        "skipped": 1,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 1,
        "missing": 0,
        "bad": 0,
    },
    "apply_repairpad_vfunc_wave491_apply.log": {
        "updated": 1,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 1,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_repairpad_vfunc_wave491_verify_dry.log": {
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

COMMENT_TOKENS = (
    "CRepairPadAI vtable 0x005d8e08 slot 11",
    "Register-only ECX receiver",
    "this+0x0c",
    "this+0x18/+0x1c",
    "radius 8.0",
    "candidate owner flag bit 0x08",
    "CRepairPadAI__IsCompatibleDockCandidate",
    "horizontal distance",
    "vertical-window",
    "this+0x10",
    "runtime repair/docking behavior",
    "rebuild parity remain unproven",
)

DECOMPILE_TOKENS = (
    "CGenericActiveReader__SetReader",
    "CMapWho__GetFirstEntryWithinRadius",
    "CMapWhoEntry__GetOwner",
    "CRepairPadAI__IsCompatibleDockCandidate",
    "CMapWho__GetNextEntryWithinRadius",
    "8.0",
    "_DAT_005d8cc0",
    "_DAT_005d85d8",
    "this + 0x18",
    "this + 0x1c",
    "this + 0x10",
)

INSTRUCTION_TOKENS = (
    "0x004d6d14\t0x004d6d10\tCRepairPadAI__VFunc_11_UpdateDockCandidateReader\tMOV\tEDI, ECX",
    "0x004d6d19\t0x004d6d10\tCRepairPadAI__VFunc_11_UpdateDockCandidateReader\tLEA\tEBP, [EDI + 0xc]",
    "0x004d6d1e\t0x004d6d10\tCRepairPadAI__VFunc_11_UpdateDockCandidateReader\tCALL\t0x00401000",
    "0x004d6d54\t0x004d6d10\tCRepairPadAI__VFunc_11_UpdateDockCandidateReader\tCALL\t0x00491ea0",
    "0x004d6d77\t0x004d6d10\tCRepairPadAI__VFunc_11_UpdateDockCandidateReader\tCALL\t0x004d6e00",
    "0x004d6dcf\t0x004d6d10\tCRepairPadAI__VFunc_11_UpdateDockCandidateReader\tCALL\t0x00401000",
    "0x004d6de4\t0x004d6d10\tCRepairPadAI__VFunc_11_UpdateDockCandidateReader\tCALL\t0x00492020",
    "0x004d6dfb\t0x004d6d10\tCRepairPadAI__VFunc_11_UpdateDockCandidateReader\tRET",
)

OVERCLAIMS = (
    "fully re'ed",
    "runtime behavior proven",
    "source identity proven",
    "exact layout proven",
    "rebuild parity proven",
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


def has_token(text: str, token: str) -> bool:
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
        for key in ("address", "target_addr", "from_addr", "vtable", "slot_addr", "pointer_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def check_logs(base: Path, failures: list[str]) -> None:
    for filename, expected in EXPECTED_SUMMARIES.items():
        text = read_text(base / filename)
        if not text:
            failures.append(f"{filename}: missing")
            continue
        if parse_summary(text) != expected:
            failures.append(f"{filename}: summary mismatch {parse_summary(text)} != {expected}")
        if "REPORT: Save succeeded" not in text:
            failures.append(f"{filename}: missing save-success marker")
        if filename.endswith("verify_dry.log") and "SKIP: 0x004d6d10" not in text:
            failures.append(f"{filename}: missing idempotent SKIP marker")
        for bad in ("FAIL:", "LockException", "Exception:"):
            if bad in text:
                failures.append(f"{filename}: unexpected token {bad!r}")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    row = next((item for item in rows if item.get("address") == TARGET), None)
    if row is None:
        failures.append(f"{TARGET}: missing metadata")
        return
    if row.get("status") != "OK":
        failures.append(f"{TARGET}: metadata status {row.get('status')} != OK")
    if row.get("name") != NAME:
        failures.append(f"{TARGET}: name {row.get('name')} != {NAME}")
    if compact(row.get("signature", "")) != compact(SIGNATURE):
        failures.append(f"{TARGET}: signature {row.get('signature')} != {SIGNATURE}")
    comment = row.get("comment", "")
    for token in COMMENT_TOKENS:
        if not has_token(comment, token):
            failures.append(f"{TARGET}: comment missing token {token!r}")
    for token in OVERCLAIMS:
        if has_token(comment, token):
            failures.append(f"{TARGET}: overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    row = next((item for item in rows if item.get("address") == TARGET), None)
    if row is None:
        failures.append(f"{TARGET}: missing tags")
        return
    actual = {part.strip() for part in re.split(r"[;,]", row.get("tags", "")) if part.strip()}
    missing = TAGS - actual
    if missing:
        failures.append(f"{TARGET}: missing tags {sorted(missing)}")


def check_decompile(base: Path, failures: list[str]) -> None:
    text = read_text(base / "post-decomp" / f"{TARGET[2:]}_{NAME}.c")
    if not text:
        failures.append(f"{TARGET}: missing decompile")
        return
    for token in DECOMPILE_TOKENS:
        if not has_token(text, token):
            failures.append(f"{TARGET}: decompile missing token {token!r}")
    for token in OVERCLAIMS:
        if has_token(text, token):
            failures.append(f"{TARGET}: decompile overclaim token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    call = next(
        (
            row
            for row in rows
            if row.get("target_addr") == "0x004d6e00"
            and row.get("from_addr") == "0x004d6d77"
            and row.get("from_function") == NAME
        ),
        None,
    )
    if call is None:
        failures.append("missing compatibility-gate call xref from 0x004d6d77")
    data = next(
        (
            row
            for row in rows
            if row.get("target_addr") == TARGET
            and row.get("from_addr") == "0x005d8e34"
            and row.get("ref_type") == "DATA"
        ),
        None,
    )
    if data is None:
        failures.append("missing vtable DATA xref from 0x005d8e34")


def check_vtable(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_vtable.tsv")
    row = next(
        (
            item
            for item in rows
            if item.get("vtable") == "0x005d8e08"
            and item.get("slot_index") == "11"
            and item.get("slot_addr") == "0x005d8e34"
        ),
        None,
    )
    if row is None:
        failures.append("missing vtable 0x005d8e08 slot 11 row")
        return
    if row.get("pointer_addr") != TARGET or row.get("function_name") != NAME or row.get("status") != "OK":
        failures.append(f"vtable slot 11 mismatch: {row}")


def check_instructions(base: Path, failures: list[str]) -> None:
    text = read_text(base / "post_instructions.tsv")
    for token in INSTRUCTION_TOKENS:
        if token not in text:
            failures.append(f"post_instructions.tsv missing token {token!r}")


def run(base: Path = DEFAULT_BASE) -> list[str]:
    failures: list[str] = []
    check_logs(base, failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_decompile(base, failures)
    check_xrefs(base, failures)
    check_vtable(base, failures)
    check_instructions(base, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = run(args.base)
    if failures:
        print("FAIL Wave491 RepairPadAI vfunc probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS Wave491 RepairPadAI vfunc probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
