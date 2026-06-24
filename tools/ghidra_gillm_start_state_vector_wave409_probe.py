#!/usr/bin/env python3
"""Validate the Wave409 CGillM state-vector Ghidra correction."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave409_explosion_start_state1_motion" / "current"
QUEUE_REPORT = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_gillm_start_state_vector_wave409_2026-05-14.md"

ADDRESS = "0x0047a160"
OLD_NAME = "CExplosionInitThing__StartState1WithStoredMotionVector"
EXPECTED_NAME = "CGillM__StartState1WithStoredMotionVector"
EXPECTED_SIGNATURE = "void __thiscall CGillM__StartState1WithStoredMotionVector(void * this)"
EXPECTED_TAGS = {
    "static-reaudit",
    "gillm-start-state-vector-wave409",
    "cgillm",
    "vtable-slot",
    "state-transition",
    "motion-vector",
    "owner-corrected",
    "signature-hardened",
    "comment-hardened",
    "retail-binary-evidence",
}
EXPECTED_DRY = {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 1, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 1, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0}

COMMENT_TOKENS = (
    "Wave409 owner/signature correction",
    "older CExplosionInitThing label",
    "CGillM RTTI vtable 0x005e0b30 slot 100",
    "state field +0x244",
    "already 1 or 2",
    "four-dword motion vector at +0x278",
    "vtable +0xf4",
    "zero flag",
    "sets +0x244 to 1",
    "runtime movement behavior",
    "rebuild parity remain unproven",
)
DECOMPILE_TOKENS = (
    EXPECTED_NAME,
    "0x244",
    "0x278",
    "0xf4",
)
INSTRUCTION_TOKENS = (
    ("MOV", "ESI, ECX"),
    ("CMP", "EAX, 0x1"),
    ("CMP", "EAX, 0x2"),
    ("PUSH", "0x0"),
    ("LEA", "ECX, [ESI + 0x278]"),
    ("CALL", "dword ptr [EAX + 0xf4]"),
    ("MOV", "dword ptr [ESI + 0x244], 0x1"),
)
PUBLIC_NOTE_TOKENS = (
    ADDRESS,
    EXPECTED_NAME,
    "CGillM RTTI vtable",
    "0x005e0b30",
    "slot 100",
    "0x005e0cc0",
    "older CExplosionInitThing label",
    "vtable +0xf4",
    "+0x244",
    "+0x278",
    "does not prove exact source virtual name",
    "does not prove concrete CGillM layout",
    "does not prove runtime movement behavior",
    "does not prove rebuild parity",
)
OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime movement behavior proven",
    "exact source virtual name proven",
    "concrete cgillm layout proven",
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
        for key in (
            "address",
            "target_addr",
            "from_addr",
            "from_function_addr",
            "function_entry",
            "containing_entry",
            "pointer_addr",
            "instruction_addr",
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
        r"SUMMARY updated=(\d+) skipped=(\d+) renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def has_instruction(rows: list[dict[str, str]], mnemonic: str, operands: str) -> bool:
    return any(row.get("mnemonic") == mnemonic and token_present(row.get("operands", ""), operands) for row in rows)


def validate(root: Path = ROOT, base: Path = BASE) -> ValidationResult:
    failures: list[str] = []

    before = row_by_address(read_tsv(base / "metadata_before.tsv"), ADDRESS)
    if before is None:
        failures.append(f"{ADDRESS} missing metadata_before row")
    else:
        if before.get("name") != OLD_NAME:
            failures.append(f"{ADDRESS} expected previous owner debt {OLD_NAME}, found {before.get('name')}")
        if "param_1" not in before.get("signature", ""):
            failures.append(f"{ADDRESS} expected previous param_1 signature debt, found {before.get('signature')}")

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
    data_xrefs = [
        row
        for row in xrefs
        if normalize_address(row.get("target_addr", "")) == ADDRESS
        and normalize_address(row.get("from_addr", "")) == "0x005e0cc0"
        and row.get("ref_type") == "DATA"
    ]
    if len(data_xrefs) != 1:
        failures.append(f"{ADDRESS} expected one DATA xref from CGillM vtable slot address 0x005e0cc0, found {len(data_xrefs)}")

    vtable = read_tsv(base / "cgillm_vtable_slots_after.tsv")
    slot100 = [
        row
        for row in vtable
        if normalize_address(row.get("vtable", "")) == "0x005e0b30"
        and row.get("slot_index") == "100"
        and normalize_address(row.get("slot_addr", "")) == "0x005e0cc0"
        and normalize_address(row.get("pointer_addr", "")) == ADDRESS
        and row.get("function_name") == EXPECTED_NAME
        and row.get("status") == "OK"
    ]
    if len(slot100) != 1:
        failures.append(f"{ADDRESS} expected CGillM vtable 0x005e0b30 slot 100 read-back, found {len(slot100)}")
    for slot, name in (("66", "CGillM__UpdateGroundedVerticalDrift"), ("117", "CGillM__InitLegMotion"), ("118", "CGillM__InitGillMAIComponent"), ("119", "CGillM__InitTerrainGuideComponent")):
        if not any(row.get("slot_index") == slot and row.get("function_name") == name for row in vtable):
            failures.append(f"missing neighboring CGillM vtable slot evidence: slot {slot} {name}")

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

    dry = parse_summary(base / "apply_gillm_start_state_vector_wave409_dry.log")
    apply = parse_summary(base / "apply_gillm_start_state_vector_wave409_apply.log")
    if dry != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: expected {EXPECTED_DRY}, found {dry}")
    if apply != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: expected {EXPECTED_APPLY}, found {apply}")
    dry_log = read_text(base / "apply_gillm_start_state_vector_wave409_dry.log")
    apply_log = read_text(base / "apply_gillm_start_state_vector_wave409_apply.log")
    if "REPORT: Save succeeded" not in dry_log or "REPORT: Save succeeded" not in apply_log:
        failures.append("dry/apply logs must both include REPORT: Save succeeded")
    if "LockException" in dry_log or "LockException" in apply_log:
        failures.append("headless dry/apply log contains LockException")

    queue = {}
    queue_path = root / QUEUE_REPORT.relative_to(ROOT)
    if queue_path.is_file():
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        signals = queue.get("qualitySignals", {})
        if queue.get("totalFunctions") != 6222:
            failures.append(f"current queue totalFunctions expected 6222, found {queue.get('totalFunctions')}")
        if signals.get("commentlessFunctionCount") != 0:
            failures.append(f"current queue commentlessFunctionCount expected 0, found {signals.get('commentlessFunctionCount')}")
        if signals.get("undefinedSignatureCount") != 0:
            failures.append(f"current queue undefinedSignatureCount expected 0, found {signals.get('undefinedSignatureCount')}")
        if signals.get("paramSignatureCount") != 0:
            failures.append(f"current queue paramSignatureCount expected 0, found {signals.get('paramSignatureCount')}")
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
    out_path = base / "gillm-start-state-vector-wave409.json"
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
        print("Ghidra Wave409 CGillM state-vector probe")
        print(f"Status: {result.status}")
        print(f"Address: {ADDRESS}")
        print(f"Name: {result.evidence.get('name')}")
        print(f"Signature: {result.evidence.get('signature')}")
        for failure in result.failures:
            print(f"- {failure}")
    return 0 if result.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
