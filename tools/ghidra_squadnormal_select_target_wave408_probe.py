#!/usr/bin/env python3
"""Validate the Wave408 SquadNormal select-target Ghidra hardening."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave408_squadnormal_select_target" / "current"
QUEUE_REPORT = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_squadnormal_select_target_wave408_2026-05-14.md"

ADDRESS = "0x00477cb0"
EXPECTED_NAME = "CSquadNormal__SelectBestEngagementTarget"
EXPECTED_SIGNATURE = "void * __stdcall CSquadNormal__SelectBestEngagementTarget(void * squad)"
EXPECTED_TAGS = {
    "static-reaudit",
    "squadnormal-select-target-wave408",
    "squad-normal",
    "ai-target-selection",
    "name-confirmed",
    "signature-hardened",
    "comment-hardened",
    "retail-binary-evidence",
}
EXPECTED_DRY = {"updated": 0, "skipped": 1, "would_update": 1, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 1, "skipped": 0, "would_update": 0, "missing": 0, "bad": 0}

COMMENT_TOKENS = (
    "CSquadNormal target-selection/scoring helper",
    "one stack argument (RET 0x4)",
    "no ECX thiscall setup",
    "squad state at +0x7c",
    "DAT_00855090/DAT_008550b0/DAT_008550c0",
    "vtable +0x120/+0x124",
    "flag/range/faction/support checks",
    "squad+0xa0 offsets",
    "0x158/0x164/0x168/0x16c/0x170/0x174/0x178/0x17c",
    "support/escort helpers",
    "candidate+0x148",
    "runtime AI behavior",
    "rebuild parity remain unproven",
)
DECOMPILE_TOKENS = (
    "CSquadNormal__SelectBestEngagementTarget",
    "DAT_00855090",
    "DAT_008550b0",
    "DAT_008550c0",
    "CSquadNormal__IsFactionCompatible",
    "CSquadNormal__IsValidLinkedSupportForTarget",
    "CSquadNormal__SelectBestSupportOrEscort",
    "CSquadNormal__GetSupportMinEngageDistance",
    "CSquadNormal__GetSupportMaxEngageDistance",
    "0x148",
)
INSTRUCTION_TOKENS = (
    ("MOV", "ESI, 0x855090"),
    ("MOV", "ESI, 0x8550b0"),
    ("MOV", "ESI, 0x8550c0"),
    ("CALL", "dword ptr [EAX + 0x120]"),
    ("CALL", "dword ptr [EDX + 0x124]"),
    ("CALL", "0x004e6680"),
    ("CALL", "0x004fb3d0"),
    ("CALL", "0x004fb840"),
    ("MOV", "EAX, dword ptr [EDI + 0x148]"),
    ("RET", "0x4"),
)
PUBLIC_NOTE_TOKENS = (
    ADDRESS,
    EXPECTED_NAME,
    EXPECTED_SIGNATURE,
    "RET 0x4",
    "DAT_00855090",
    "DAT_008550b0",
    "DAT_008550c0",
    "CSquadNormal__ScheduleTargetReaderRefresh",
    "0x004ea584",
    "no-function callsite",
    "does not prove exact CSquadNormal/source identity",
    "does not prove candidate struct layout",
    "does not prove global list semantics",
    "does not prove runtime AI behavior",
    "does not prove rebuild parity",
)
OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime AI behavior proven",
    "exact CSquadNormal/source identity proven",
    "candidate struct layout proven",
    "global list semantics proven",
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


def decompile_text_for(directory: Path, address: str, name: str) -> str:
    if not directory.is_dir():
        return ""
    normalized = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{normalized}_{name}.c"))
    if matches:
        return read_text(matches[0])
    fallback = sorted(directory.glob(f"{normalized}_*.c"))
    if fallback:
        return read_text(fallback[0])
    return ""


def parse_summary(path: Path) -> dict[str, int] | None:
    text = read_text(path)
    match = re.search(
        r"SUMMARY updated=(\d+) skipped=(\d+) would_update=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "would_update", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def has_instruction(rows: list[dict[str, str]], mnemonic: str, operands: str) -> bool:
    return any(row.get("mnemonic") == mnemonic and token_present(row.get("operands", ""), operands) for row in rows)


def validate(root: Path = ROOT, base: Path = BASE) -> ValidationResult:
    failures: list[str] = []

    before = row_by_address(read_tsv(base / "metadata_before.tsv"), ADDRESS)
    if before is None:
        failures.append(f"{ADDRESS} missing metadata_before row")
    else:
        if before.get("name") != EXPECTED_NAME:
            failures.append(f"{ADDRESS} expected saved name {EXPECTED_NAME}, found {before.get('name')}")
        before_sig = before.get("signature", "")
        if "param_1" not in before_sig or not before_sig.startswith("int * __stdcall"):
            failures.append(f"{ADDRESS} expected previous param_1/int-pointer signature debt, found {before_sig}")

    after = row_by_address(read_tsv(base / "metadata_after.tsv"), ADDRESS)
    if after is None:
        failures.append(f"{ADDRESS} missing metadata_after row")
    else:
        if after.get("name") != EXPECTED_NAME:
            failures.append(f"{ADDRESS} expected name {EXPECTED_NAME}, found {after.get('name')}")
        if after.get("signature") != EXPECTED_SIGNATURE:
            failures.append(f"{ADDRESS} expected signature {EXPECTED_SIGNATURE}, found {after.get('signature')}")
        comment = after.get("comment", "")
        for token in COMMENT_TOKENS:
            if not token_present(comment, token):
                failures.append(f"{ADDRESS} comment missing token: {token}")

    tags_row = row_by_address(read_tsv(base / "tags_after.tsv"), ADDRESS)
    if tags_row is None:
        failures.append(f"{ADDRESS} missing tags_after row")
    else:
        tags = {tag for tag in tags_row.get("tags", "").split(";") if tag}
        missing_tags = sorted(EXPECTED_TAGS - tags)
        if missing_tags:
            failures.append(f"{ADDRESS} missing tags: {', '.join(missing_tags)}")

    xrefs = read_tsv(base / "xrefs_after.tsv")
    schedule_hits = [
        row
        for row in xrefs
        if normalize_address(row.get("target_addr", "")) == ADDRESS
        and normalize_address(row.get("from_addr", "")) == "0x004e815a"
        and row.get("from_function") == "CSquadNormal__ScheduleTargetReaderRefresh"
        and row.get("ref_type") == "UNCONDITIONAL_CALL"
    ]
    no_function_hits = [
        row
        for row in xrefs
        if normalize_address(row.get("target_addr", "")) == ADDRESS
        and normalize_address(row.get("from_addr", "")) == "0x004ea584"
        and row.get("from_function") == "<no_function>"
        and row.get("ref_type") == "UNCONDITIONAL_CALL"
    ]
    if len(schedule_hits) != 1:
        failures.append(f"{ADDRESS} expected one xref from CSquadNormal__ScheduleTargetReaderRefresh at 0x004e815a, found {len(schedule_hits)}")
    if len(no_function_hits) != 1:
        failures.append(f"{ADDRESS} expected one no-function xref at 0x004ea584, found {len(no_function_hits)}")

    instructions = read_tsv(base / "instructions_after.tsv")
    for mnemonic, operands in INSTRUCTION_TOKENS:
        if not has_instruction(instructions, mnemonic, operands):
            failures.append(f"{ADDRESS} instructions missing {mnemonic} {operands}")

    decompile = decompile_text_for(base / "decompile_after", ADDRESS, EXPECTED_NAME)
    if not decompile:
        failures.append(f"{ADDRESS} missing decompile_after export")
    for token in DECOMPILE_TOKENS:
        if not token_present(decompile, token):
            failures.append(f"{ADDRESS} decompile missing token: {token}")

    dry = parse_summary(base / "apply_squadnormal_select_target_wave408_dry.log")
    apply = parse_summary(base / "apply_squadnormal_select_target_wave408_apply.log")
    if dry != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: expected {EXPECTED_DRY}, found {dry}")
    if apply != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: expected {EXPECTED_APPLY}, found {apply}")
    dry_log = read_text(base / "apply_squadnormal_select_target_wave408_dry.log")
    apply_log = read_text(base / "apply_squadnormal_select_target_wave408_apply.log")
    if "REPORT: Save succeeded" not in dry_log or "REPORT: Save succeeded" not in apply_log:
        failures.append("dry/apply logs must both include REPORT: Save succeeded")
    if "LockException" in dry_log or "LockException" in apply_log:
        failures.append("headless dry/apply log contains LockException")

    queue = {}
    queue_path = root / QUEUE_REPORT.relative_to(ROOT)
    if queue_path.is_file():
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        signals = queue.get("qualitySignals", {})
        if queue.get("totalFunctions") != 6028:
            failures.append(f"queue totalFunctions expected 6028, found {queue.get('totalFunctions')}")
        if signals.get("commentlessFunctionCount") != 4467:
            failures.append(f"queue commentlessFunctionCount expected 4467, found {signals.get('commentlessFunctionCount')}")
        if signals.get("undefinedSignatureCount") != 1909:
            failures.append(f"queue undefinedSignatureCount expected 1909, found {signals.get('undefinedSignatureCount')}")
        if signals.get("paramSignatureCount") != 1855:
            failures.append(f"queue paramSignatureCount expected 1855, found {signals.get('paramSignatureCount')}")
    else:
        failures.append(f"missing queue report: {queue_path}")

    note_path = root / PUBLIC_NOTE.relative_to(ROOT)
    note = read_text(note_path)
    for token in PUBLIC_NOTE_TOKENS:
        if not token_present(note, token):
            failures.append(f"public note missing token: {token}")
    lowered_note = note.lower()
    for token in OVERCLAIM_TOKENS:
        if token.lower() in lowered_note:
            failures.append(f"public note contains overclaim token: {token}")

    evidence = {
        "address": ADDRESS,
        "name": after.get("name") if after else None,
        "signature": after.get("signature") if after else None,
        "queue": {
            "totalFunctions": queue.get("totalFunctions"),
            "qualitySignals": queue.get("qualitySignals"),
        },
    }
    out_path = base / "squadnormal-select-target-wave408.json"
    if base.is_dir():
        out_path.write_text(
            json.dumps({"status": "PASS" if not failures else "FAIL", "failures": failures, "evidence": evidence}, indent=2) + "\n",
            encoding="utf-8",
        )
    return ValidationResult("PASS" if not failures else "FAIL", failures, evidence)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    result = validate()
    if args.json:
        print(json.dumps({"status": result.status, "failures": result.failures, "evidence": result.evidence}, indent=2))
    else:
        print("Ghidra Wave408 SquadNormal select-target probe")
        print(f"Status: {result.status}")
        print(f"Address: {ADDRESS}")
        print(f"Name: {result.evidence.get('name')}")
        print(f"Signature: {result.evidence.get('signature')}")
        for failure in result.failures:
            print(f"- {failure}")
    return 0 if result.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
