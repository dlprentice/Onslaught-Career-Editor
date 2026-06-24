#!/usr/bin/env python3
"""Validate the Wave415 CImposter/static-init Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave415-imposter-infantry" / "current"

COMMON_TAGS = {"static-reaudit", "imposter-wave415", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x004888f0": {
        "name": "CImposter__FindOrCreate",
        "signature": "void * __cdecl CImposter__FindOrCreate(char * name, int key_24, int key_40, int key_30, int key_44, int key_48, int key_34)",
        "commentTokens": [
            "find-or-create helper",
            "global imposter list 0x0067a678",
            "stricmp",
            "+0x24",
            "+0x30",
            "+0x34",
            "+0x40",
            "+0x44",
            "+0x48",
            "0x4c",
            "OID type 0x39",
            "imposter.cpp",
            "runtime rendering behavior",
            "rebuild parity unproven",
        ],
        "tags": {"imposter", "signature-hardened", "comment-hardened"},
        "xrefs": {"CRTMesh__Init"},
    },
    "0x00488a70": {
        "name": "CImposter__AddToList",
        "signature": "void __thiscall CImposter__AddToList(void * this)",
        "commentTokens": [
            "global singly linked list 0x0067a678",
            "clears the next pointer",
            "runtime rendering behavior",
            "rebuild parity remain unproven",
        ],
        "tags": {"imposter", "linked-list", "signature-hardened", "comment-hardened"},
        "xrefs": {"CDXImposter__Create"},
    },
    "0x00488aa0": {
        "name": "CImposter__GetFrameHeightForOwnerSlot",
        "signature": "float __thiscall CImposter__GetFrameHeightForOwnerSlot(void * this, void * owner)",
        "commentTokens": [
            "owner/signature correction from stale CIBuffer label",
            "CDXTrees__BuildTreeGeometry",
            "owner+0x08",
            "vtable slot +0x6c",
            "frame-table float",
            "this+0x3c",
            "+0x10",
            "index*0x18",
            "runtime tree rendering behavior remains unproven",
        ],
        "tags": {"imposter", "owner-corrected", "tree-rendering", "signature-corrected", "comment-hardened"},
        "xrefs": {"CDXTrees__BuildTreeGeometry"},
        "instructionEvidence": [("CALL", "[EDX + 0x6c]"), ("FLD", "[ECX + EAX*0x8 + 0x10]")],
    },
    "0x00488ac0": {
        "name": "ImposterGlobals__ClearTailSlots",
        "signature": "void __cdecl ImposterGlobals__ClearTailSlots(void)",
        "commentTokens": [
            "recovered static-init table function boundary",
            "data xref 0x006223b4",
            "0x0067a6b8",
            "0x0067a6c0",
            "exact source identity",
            "runtime rendering behavior remain unproven",
        ],
        "tags": {"imposter", "function-boundary", "static-init", "comment-hardened"},
        "xrefs": {"<no_function>"},
        "instructionEvidence": [("MOV", "[0x0067a6b8]")],
    },
    "0x00488ae0": {
        "name": "ImposterGlobals__InitDefaultFrameData",
        "signature": "void __cdecl ImposterGlobals__InitDefaultFrameData(void)",
        "commentTokens": [
            "recovered static-init table function boundary",
            "data xref 0x006223b8",
            "0x0067a688",
            "0x0067a6b4",
            "0.0 and 1.0 float patterns",
            "exact source identity",
            "runtime rendering behavior remain unproven",
        ],
        "tags": {"imposter", "function-boundary", "static-init", "comment-hardened"},
        "xrefs": {"<no_function>"},
        "instructionEvidence": [("MOV", "0x3f800000")],
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 3,
    "created": 0,
    "would_create": 2,
    "renamed": 0,
    "would_rename": 1,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 5,
    "skipped": 0,
    "created": 2,
    "would_create": 0,
    "renamed": 1,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime rendering behavior proven",
    "runtime tree rendering behavior proven",
    "source identity proven",
    "source body identity proven",
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
        for key in ("address", "target_addr", "from_function_addr", "function_entry"):
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


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return {
            "updated": -1,
            "skipped": -1,
            "created": -1,
            "would_create": -1,
            "renamed": -1,
            "would_rename": -1,
            "missing": -1,
            "bad": -1,
        }
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def compare_summary(failures: list[str], label: str, actual: dict[str, int], expected: dict[str, int]) -> None:
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            failures.append(f"{label} summary {key}: expected {expected_value}, got {actual_value}")


def check_instruction_evidence(
    failures: list[str],
    rows: list[dict[str, str]],
    address: str,
    evidence: list[tuple[str, str]],
) -> None:
    target_rows = [row for row in rows if normalize_address(row.get("target_addr", "")) == normalize_address(address)]
    for mnemonic, operand_token in evidence:
        if not any(row.get("mnemonic", "") == mnemonic and token_present(row.get("operands", ""), operand_token) for row in target_rows):
            failures.append(f"{address} missing instruction evidence {mnemonic} {operand_token}")


def check_targets(base: Path = BASE) -> list[str]:
    failures: list[str] = []
    metadata = read_tsv(base / "metadata_after.tsv")
    tags_rows = read_tsv(base / "tags_after.tsv")
    xrefs = read_tsv(base / "xrefs_after.tsv")
    instructions = read_tsv(base / "instructions_after.tsv")

    compare_summary(failures, "dry", parse_summary(read_text(base / "apply_dry.log")), EXPECTED_DRY)
    compare_summary(failures, "apply", parse_summary(read_text(base / "apply_apply.log")), EXPECTED_APPLY)

    if len(metadata) < len(TARGETS):
        failures.append(f"metadata_after.tsv expected at least {len(TARGETS)} rows, found {len(metadata)}")
    if len(tags_rows) < len(TARGETS):
        failures.append(f"tags_after.tsv expected at least {len(TARGETS)} rows, found {len(tags_rows)}")

    for address, expected in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address} missing metadata row")
            continue
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status expected OK, got {row.get('status')}")
        if row.get("name") != expected["name"]:
            failures.append(f"{address} name expected {expected['name']}, got {row.get('name')}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address} signature expected {expected['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address} comment missing token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address} comment contains overclaim token: {token}")

        tag_row = row_by_address(tags_rows, address)
        if tag_row is None:
            failures.append(f"{address} missing tag row")
        else:
            actual_tags = parse_tags(tag_row.get("tags", ""))
            expected_tags = COMMON_TAGS | set(expected["tags"])  # type: ignore[arg-type]
            missing = sorted(expected_tags - actual_tags)
            if missing:
                failures.append(f"{address} missing tags: {', '.join(missing)}")

        target_xrefs = [row for row in xrefs if normalize_address(row.get("target_addr", "")) == normalize_address(address)]
        observed_callers = {row.get("from_function", "") for row in target_xrefs}
        for expected_caller in expected.get("xrefs", set()):  # type: ignore[union-attr]
            if expected_caller not in observed_callers:
                failures.append(f"{address} missing xref caller: {expected_caller}")

        instruction_evidence = expected.get("instructionEvidence")
        if instruction_evidence:
            check_instruction_evidence(failures, instructions, address, instruction_evidence)  # type: ignore[arg-type]

    return failures


def build_report(base: Path = BASE) -> dict[str, object]:
    failures = check_targets(base)
    return {
        "schema": "ghidra-imposter-wave415.v1",
        "status": "PASS" if not failures else "FAIL",
        "targetCount": len(TARGETS),
        "createdFunctionBoundaries": ["0x00488ac0", "0x00488ae0"],
        "ownerCorrection": {
            "address": "0x00488aa0",
            "oldName": "CIBuffer__GetEntryHeightByOwnerSlot",
            "newName": "CImposter__GetFrameHeightForOwnerSlot",
        },
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra metadata for the Wave415 target set matches the expected CImposter names, signatures, comments, and tags.",
            "The stale CIBuffer owner label at 0x00488aa0 has been corrected to CImposter frame-height context.",
            "Two adjacent static-init table targets are formal Ghidra functions after Wave415.",
        ],
        "notProven": [
            "This does not prove runtime imposter or tree rendering behavior.",
            "This does not prove exact source-body identity because the matching source files are absent from the tracked Stuart source snapshot.",
            "This does not prove concrete CImposter/CDXTrees layouts, local variable types, or rebuild parity.",
        ],
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--out", type=Path, default=BASE / "imposter-wave415-report.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    report = build_report(args.base)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra imposter Wave415 probe")
        print(f"Status: {report['status']}")
        print(f"Targets: {report['targetCount']}")
        print(f"Output: {args.out}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
