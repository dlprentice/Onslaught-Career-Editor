#!/usr/bin/env python3
"""Validate the Wave403 FEPBEConfig selected-entry Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "fepbeconfig-selected-entry-wave403" / "current"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_fepbeconfig_selected_entry_wave403_2026-05-14.md"

ADDRESS = "0x00451a40"
EXPECTED_NAME = "FEPBEConfig__FindSelectedEntryByGlobalId"
EXPECTED_SIGNATURE = "int * __fastcall FEPBEConfig__FindSelectedEntryByGlobalId(void * list_state)"
EXPECTED_TAGS = {
    "static-reaudit",
    "fepbeconfig-selected-entry-wave403",
    "fepbeconfig",
    "list-lookup",
    "global-selector",
    "owner-corrected",
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
    "would_rename": 1,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 1,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 1,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

COMMENT_TOKENS = (
    "Owner correction from CUnitAI to FEPBEConfig selected-entry list helper",
    "0x0089da14",
    "DAT_0089d94c",
    "list head +0x20",
    "iterator cursor at +0x28",
    "link nodes through +0x4",
    "runtime frontend behavior",
    "rebuild parity remain unproven",
)
DECOMPILE_TOKENS = (
    "DAT_0089d94c",
    "list_state + 0x20",
    "list_state + 0x28",
)
INSTRUCTION_TOKENS = (
    "MOV\tEAX, dword ptr [ECX + 0x20]",
    "MOV\tEDX, dword ptr [0x0089d94c]",
    "MOV\tEAX, dword ptr [EAX + 0x4]",
    "RET",
)
CALLER_TOKENS = (
    "FEPBEConfig__FindSelectedEntryByGlobalId(&DAT_0089da14)",
    "CFEPBEConfig__Render",
)
PUBLIC_NOTE_TOKENS = (
    ADDRESS,
    EXPECTED_NAME,
    "CFEPBEConfig__Render",
    "0x0089da14",
    "DAT_0089d94c",
    "CUnitAI owner label superseded",
    "FEPBEConfig source file is present only as page-shell evidence in the current Stuart source snapshot",
    "does not prove runtime frontend behavior",
    "does not prove exact source identity",
    "does not prove rebuild parity",
)
OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime frontend behavior proven",
    "source identity proven",
    "exact source identity proven",
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
    note_path = root / "release" / "readiness" / "ghidra_fepbeconfig_selected_entry_wave403_2026-05-14.md"

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
    render_xrefs = [row for row in xrefs if normalize_address(row.get("target_addr", "")) == ADDRESS and row.get("from_function") == "CFEPBEConfig__Render"]
    if len(render_xrefs) != 3:
        failures.append(f"{ADDRESS} expected 3 CFEPBEConfig__Render xrefs, found {len(render_xrefs)}")

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

    caller_text = read_text(base / "caller_decompile_after" / "004505b0_CFEPBEConfig__Render.c")
    if not caller_text:
        caller_text = read_text(base / "caller_decompile_before" / "004505b0_CFEPBEConfig__Render.c")
    for token in CALLER_TOKENS:
        if not token_present(caller_text, token):
            failures.append(f"caller decompile missing token: {token}")

    dry = parse_summary(base / "apply_fepbeconfig_selected_entry_wave403_dry.log")
    apply = parse_summary(base / "apply_fepbeconfig_selected_entry_wave403_apply.log")
    if dry != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: expected {EXPECTED_DRY}, found {dry}")
    if apply != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: expected {EXPECTED_APPLY}, found {apply}")
    apply_log = read_text(base / "apply_fepbeconfig_selected_entry_wave403_apply.log")
    if "REPORT: Save succeeded" not in apply_log:
        failures.append("apply log missing REPORT: Save succeeded")
    if "LockException" in apply_log or "LockException" in read_text(base / "apply_fepbeconfig_selected_entry_wave403_dry.log"):
        failures.append("headless apply/dry log contains LockException")

    note = read_text(note_path)
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
        "metadataRows": len(metadata),
        "xrefsRows": len(xrefs),
        "renderXrefs": len(render_xrefs),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    return ValidationResult(status=status, failures=failures, evidence=evidence)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate the current Wave403 evidence bundle.")
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--out", type=Path, default=BASE / "fepbeconfig-selected-entry-wave403.json")
    args = parser.parse_args()

    if not args.check:
        parser.print_help()
        return 2

    result = validate(base=args.base)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps({"status": result.status, "failures": result.failures, "evidence": result.evidence}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result.status, "target_count": 1, "failure_count": len(result.failures)}, indent=2))
    if result.failures:
        for failure in result.failures:
            print(f"- {failure}", file=sys.stderr)
    return 0 if result.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
