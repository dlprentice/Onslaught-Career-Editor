#!/usr/bin/env python3
"""Validate the Wave416 CInfantry / CUnitAI lifecycle Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave416-infantry-lifecycle" / "current"

COMMON_TAGS = {"static-reaudit", "infantry-wave416", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x00488bb0": {
        "name": "CInfantry__Init",
        "signature": "void __thiscall CInfantry__Init(void * this, void * infantryInit)",
        "commentTokens": [
            "Infantry init",
            "infantry init pointer",
            "allocates collision seeking and guide helpers",
            "4.0/1.0 scale context",
            "CGroundUnit__Init",
            "runtime infantry behavior",
            "rebuild parity unproven",
        ],
        "tags": {"infantry", "lifecycle", "signature-hardened", "comment-hardened"},
        "xrefs": {"<no_function>"},
    },
    "0x00488dc0": {
        "name": "CInfantryAI__scalar_deleting_dtor",
        "signature": "void * __thiscall CInfantryAI__scalar_deleting_dtor(void * this, byte flags)",
        "commentTokens": [
            "scalar-deleting destructor wrapper",
            "CInfantryAI__dtor_body_00488de0",
            "flags bit 0",
            "OID__FreeObject",
            "returns this",
            "runtime cleanup behavior unproven",
        ],
        "tags": {"infantry", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"},
        "xrefs": {"<no_function>"},
        "instructionEvidence": [("TEST", "[ESP + 0x8]"), ("RET", "0x4")],
    },
    "0x00488de0": {
        "name": "CInfantryAI__dtor_body_00488de0",
        "signature": "void __fastcall CInfantryAI__dtor_body_00488de0(void * this)",
        "commentTokens": [
            "destructor body reached by CInfantryAI scalar deleting destructor",
            "CUnitAI base vtable 0x005d8d1c",
            "+0x28/+0x24/+0x0c",
            "CSPtrSet__Remove",
            "CMonitor__Shutdown",
            "runtime cleanup behavior unproven",
        ],
        "tags": {"infantry", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"},
        "xrefs": {"CInfantryAI__scalar_deleting_dtor"},
        "instructionEvidence": [("MOV", "0x5d8d1c")],
    },
    "0x00488e80": {
        "name": "CCollisionSeekingInfantryBloke__scalar_deleting_dtor",
        "signature": "void * __thiscall CCollisionSeekingInfantryBloke__scalar_deleting_dtor(void * this, byte flags)",
        "commentTokens": [
            "scalar-deleting destructor wrapper",
            "CCollisionSeekingInfantryBloke__dtor_body_00488ea0",
            "flags bit 0",
            "OID__FreeObject",
            "returns this",
            "runtime collision behavior unproven",
        ],
        "tags": {"collision", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"},
        "xrefs": {"<no_function>"},
        "instructionEvidence": [("TEST", "[ESP + 0x8]"), ("RET", "0x4")],
    },
    "0x00488ea0": {
        "name": "CCollisionSeekingInfantryBloke__dtor_body_00488ea0",
        "signature": "void __fastcall CCollisionSeekingInfantryBloke__dtor_body_00488ea0(void * this)",
        "commentTokens": [
            "destructor body reached by the collision-seeking infantry bloke scalar wrapper",
            "monitor at this+0x24",
            "CCollisionSeekingRound__Destructor",
            "runtime collision behavior unproven",
        ],
        "tags": {"collision", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"},
        "xrefs": {"CCollisionSeekingInfantryBloke__scalar_deleting_dtor"},
    },
    "0x00488ef0": {
        "name": "CCollisionSeekingThing__ctor_base",
        "signature": "void __fastcall CCollisionSeekingThing__ctor_base(void * this)",
        "commentTokens": [
            "constructor-base helper",
            "field +0x04",
            "0x005d9608",
            "exact source identity",
            "rebuild parity remain unproven",
        ],
        "tags": {"collision", "constructor", "signature-corrected", "comment-hardened"},
        "xrefs": {"CInfantry__Init", "CRound__Init"},
    },
    "0x00488f00": {
        "name": "CHLCollisionDetector__ctor_base",
        "signature": "void __fastcall CHLCollisionDetector__ctor_base(void * this)",
        "commentTokens": [
            "constructor-base helper",
            "field +0x04",
            "CHLCollisionDetector vtable 0x005dbf78",
            "exact source identity",
            "rebuild parity remain unproven",
        ],
        "tags": {"collision", "constructor", "signature-corrected", "comment-hardened"},
        "xrefs": {"CInfantry__Init", "CRound__Init"},
        "instructionEvidence": [("MOV", "0x5dbf78")],
    },
    "0x00489040": {
        "name": "CUnitAI__TryPlayActivateAnimation",
        "signature": "int __fastcall CUnitAI__TryPlayActivateAnimation(void * this)",
        "commentTokens": [
            "activation-animation helper",
            "+0x140/+0x26c/+0x2c",
            "CUnitAI__TrySpawnOrFinalizeAttachedUnit",
            "+0x268",
            "0x12",
            "runtime AI behavior unproven",
        ],
        "tags": {"unitai", "animation", "signature-hardened", "comment-hardened"},
        "xrefs": {"<no_function>"},
    },
    "0x00489de0": {
        "name": "CUnitAI__PromoteDieAnimationToDeadVariant",
        "signature": "int __fastcall CUnitAI__PromoteDieAnimationToDeadVariant(void * this)",
        "commentTokens": [
            "die_up/die_back/die_left/die_right",
            "dead_up/dead_back/dead_left/dead_right",
            "dead_forward",
            "runtime death behavior unproven",
        ],
        "tags": {"unitai", "death-animation", "signature-hardened", "comment-hardened"},
        "xrefs": {"<no_function>"},
        "instructionEvidence": [("PUSH", "0x62d560")],
    },
    "0x00489ef0": {
        "name": "CUnitAI__ForceDeadForwardAndResetDeathState",
        "signature": "void __fastcall CUnitAI__ForceDeadForwardAndResetDeathState(void * this)",
        "commentTokens": [
            "death flag bit +0x2c",
            "dead_forward",
            "clears +0x26c",
            "state timestamp",
            "runtime death behavior unproven",
        ],
        "tags": {"unitai", "death-animation", "signature-hardened", "comment-hardened"},
        "xrefs": {"<no_function>"},
        "instructionEvidence": [("MOV", "[ESI + 0x26c]")],
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 10,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 6,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 10,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 6,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime cleanup behavior proven",
    "runtime collision behavior proven",
    "runtime infantry behavior proven",
    "runtime ai behavior proven",
    "runtime death behavior proven",
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
            failures.append(f"{address} missing tags row")
        else:
            actual_tags = parse_tags(tag_row.get("tags", ""))
            expected_tags = COMMON_TAGS | set(expected["tags"])  # type: ignore[arg-type]
            missing = sorted(expected_tags - actual_tags)
            if missing:
                failures.append(f"{address} tags missing {missing}")

        expected_xrefs = set(expected.get("xrefs", set()))  # type: ignore[arg-type]
        actual_xrefs = {
            row.get("from_function", "")
            for row in xrefs
            if normalize_address(row.get("target_addr", "")) == normalize_address(address)
        }
        missing_xrefs = sorted(expected_xrefs - actual_xrefs)
        if missing_xrefs:
            failures.append(f"{address} missing xref from {missing_xrefs}")

        instruction_evidence = expected.get("instructionEvidence")
        if instruction_evidence:
            check_instruction_evidence(failures, instructions, address, instruction_evidence)  # type: ignore[arg-type]

    stale_rows = [
        row
        for row in metadata
        if row.get("name") in {"CInfantryAI__VFunc_01_00488dc0", "CCollisionSeekingInfantryBloke__VFunc_01_00488e80", "CUnitAI__ctor_like_00488de0"}
    ]
    if stale_rows:
        failures.append("stale lifecycle names remain in metadata_after.tsv")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="Wave416 artifact directory")
    parser.add_argument("--check", action="store_true", help="Return non-zero when validation fails")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    failures = check_targets(args.base)
    result = {
        "status": "PASS" if not failures else "FAIL",
        "base": str(args.base),
        "target_count": len(TARGETS),
        "failures": failures,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Status: {result['status']}")
        print(f"Targets: {result['target_count']}")
        if failures:
            print("Failures:")
            for failure in failures:
                print(f"- {failure}")
    if failures and args.check:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
