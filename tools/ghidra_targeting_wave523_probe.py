#!/usr/bin/env python3
"""Validate Wave523 Unit/Squad targeting static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave523-unit-targeting-004fb280"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_targeting_wave523_2026-05-18.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "targeting-wave523",
    "unit-targeting",
}

OVERCLAIM_TOKENS = (
    "runtime targeting behavior proven",
    "runtime weapon behavior proven",
    "source identity proven",
    "exact enum names proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)


TARGETS = {
    "0x004fb280": {
        "name": "CUnit__UpdateFireControlYawAndQueueEvent",
        "signature": "void __thiscall CUnit__UpdateFireControlYawAndQueueEvent(void * this, void * event_context)",
        "comment_tokens": ("RET 0x4", "event_context", "event 0xfa1", "remain unproven"),
        "tags": {"ballistic-targeting", "event-scheduler"},
        "decompile_tokens": ("event_context", "CEventManager__AddEvent_AtTime", "0xfa1"),
    },
    "0x004fb3d0": {
        "name": "CSquadNormal__IsValidLinkedSupportForTarget",
        "signature": "int __thiscall CSquadNormal__IsValidLinkedSupportForTarget(void * this, void * target_unit)",
        "comment_tokens": ("RET 0x4", "target_unit", "this+0x18c", "profile offsets +0x6c/+0x70"),
        "tags": {"squadnormal", "support-targeting"},
        "decompile_tokens": ("target_unit", "CUnit__IsSupportTargetMaskCompatible", "CHeightField__GetHeightSamplePacked16"),
    },
    "0x004fb500": {
        "name": "CUnit__CanFireAtTarget_BallisticArcA",
        "signature": "int __thiscall CUnit__CanFireAtTarget_BallisticArcA(void * this, void * target_unit, int ballistic_context)",
        "comment_tokens": ("RET 0x8", "ballistic_context", "OID__CanFireAtTarget_BallisticArcA", "remain unproven"),
        "tags": {"ballistic-targeting", "range-gate"},
        "decompile_tokens": ("target_unit", "ballistic_context", "CUnit__ClassifyTargetRangeBand(this,target_unit)"),
    },
    "0x004fb5a0": {
        "name": "CUnit__CanFireAtTarget_BallisticArcB",
        "signature": "int __thiscall CUnit__CanFireAtTarget_BallisticArcB(void * this, void * target_unit)",
        "comment_tokens": ("RET 0x4", "target_unit", "OID__CanFireAtTarget_BallisticArcB", "remain unproven"),
        "tags": {"ballistic-targeting", "range-gate"},
        "decompile_tokens": ("target_unit", "CUnit__ClassifyTargetRangeBand(this,target_unit)", "OID__CanFireAtTarget_BallisticArcB"),
    },
    "0x004fb650": {
        "name": "CUnit__ForwardAimTransformAndAttachTargetReader",
        "signature": "void __thiscall CUnit__ForwardAimTransformAndAttachTargetReader(void * this, void * target_transform, void * target_reader)",
        "comment_tokens": ("renamed from the Warspite-specific label", "RET 0x8", "target_transform", "target_reader"),
        "tags": {"aim-transform", "owner-corrected"},
        "decompile_tokens": ("target_transform", "target_reader", "OID__UpdateAimTransformAndAttachTargetReader"),
    },
    "0x004fb670": {
        "name": "CUnit__ClassifyTargetRangeBand",
        "signature": "int __thiscall CUnit__ClassifyTargetRangeBand(void * this, void * target_unit)",
        "comment_tokens": ("RET 0x4", "returns 2", "returns 1", "returns 0"),
        "tags": {"ballistic-targeting", "range-gate"},
        "decompile_tokens": ("target_unit", "CUnit__ComputeMinBallisticTravelDistance", "CUnit__ComputeMaxBallisticTravelDistance"),
    },
}

EXPECTED_XREFS = {
    ("0x004fb280", "0x004f90ce", "CUnit__Init", "UNCONDITIONAL_CALL"),
    ("0x004fb280", "0x004f9847", "VFuncSlot_00_004f9820", "UNCONDITIONAL_CALL"),
    ("0x004fb3d0", "0x00477e15", "CSquadNormal__SelectBestEngagementTarget", "UNCONDITIONAL_CALL"),
    ("0x004fb500", "0x0047b0dd", "CGillMHeadAI__UpdateTargetBallisticArcFlags", "UNCONDITIONAL_CALL"),
    ("0x004fb5a0", "0x004e8332", "CSquadNormal__EvaluateLeaderTargetPursuitMode", "UNCONDITIONAL_CALL"),
    ("0x004fb650", "0x0047b061", "CGillMHeadAI__UpdateAimTransformAndTargetReader", "UNCONDITIONAL_CALL"),
    ("0x004fb650", "0x004ff18b", "CWarspite__Update", "UNCONDITIONAL_CALL"),
    ("0x004fb670", "0x004fb509", "CUnit__CanFireAtTarget_BallisticArcA", "UNCONDITIONAL_CALL"),
    ("0x004fb670", "0x004fb5a9", "CUnit__CanFireAtTarget_BallisticArcB", "UNCONDITIONAL_CALL"),
    ("0x004fb670", "0x00422c38", "CCarverAI__UpdateAttackAndReschedule", "UNCONDITIONAL_CALL"),
}

EXPECTED_RETS = {
    ("0x004fb3ca", "RET", "0x4", "CUnit__UpdateFireControlYawAndQueueEvent"),
    ("0x004fb468", "RET", "0x4", "CSquadNormal__IsValidLinkedSupportForTarget"),
    ("0x004fb516", "RET", "0x8", "CUnit__CanFireAtTarget_BallisticArcA"),
    ("0x004fb5b6", "RET", "0x4", "CUnit__CanFireAtTarget_BallisticArcB"),
    ("0x004fb669", "RET", "0x8", "CUnit__ForwardAimTransformAndAttachTargetReader"),
    ("0x004fb728", "RET", "0x4", "CUnit__ClassifyTargetRangeBand"),
}

EXPECTED_CONTEXT_TOKENS = {
    "0x0047b090": (
        "CUnit__CanFireAtTarget_BallisticArcB",
        "CUnit__CanFireAtTarget_BallisticArcA",
    ),
    "0x004fef40": (
        "CUnit__ForwardAimTransformAndAttachTargetReader",
        "CSquadNormal__SelectBestSupportOrEscort",
    ),
    "0x004e81d0": ("CUnit__CanFireAtTarget_BallisticArcB",),
}

PUBLIC_NOTE_TOKENS = (
    "Wave523",
    "CUnit__ClassifyTargetRangeBand",
    "CUnit__ForwardAimTransformAndAttachTargetReader",
    "46 target xref rows",
    "runtime weapon behavior",
    "rebuild parity",
)


def normalize_addr(address: str) -> str:
    address = (address or "").strip().lower()
    if not address or address.startswith("<"):
        return address
    body = address[2:] if address.startswith("0x") else address
    return f"0x{int(body, 16):08x}"


def compact_text(value: str) -> str:
    return " ".join((value or "").replace("\t", " ").replace("\r", " ").replace("\n", " ").split())


def compact_token(value: str) -> str:
    return "".join(compact_text(value).lower().split())


def token_present(text: str, token: str) -> bool:
    return compact_token(token) in compact_token(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "instruction_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_addr(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str]:
    wanted = normalize_addr(address)
    for row in rows:
        if row.get(key) == wanted:
            return row
    raise AssertionError(f"missing row for {address}")


def find_decomp_file(decomp_dir: Path, address: str, expected_name: str) -> Path:
    candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
    require(bool(candidates), f"missing decompile export for {address}")
    named = [path for path in candidates if expected_name in path.name]
    require(bool(named), f"decompile export for {address} does not contain {expected_name}: {candidates}")
    return named[0]


def check_metadata(base: Path) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    require(len(rows) == len(TARGETS), f"expected {len(TARGETS)} metadata rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        require(row["status"] == "OK", f"{address} metadata status is {row['status']}")
        require(row["name"] == expected["name"], f"{address} name mismatch: {row['name']}")
        require(row["signature"] == expected["signature"], f"{address} signature mismatch: {row['signature']}")
        comment = row["comment"]
        for token in expected["comment_tokens"]:
            require(token_present(comment, token), f"{address} comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            require(not token_present(comment, token), f"{address} comment overclaims with {token!r}")


def check_tags(base: Path) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    require(len(rows) == len(TARGETS), f"expected {len(TARGETS)} tag rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        tags = set(filter(None, row.get("tags", "").split(";")))
        wanted = COMMON_TAGS | set(expected["tags"])
        missing = wanted - tags
        require(not missing, f"{address} tags missing {sorted(missing)}")


def check_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    require(len(rows) == 46, f"expected 46 xref rows, got {len(rows)}")
    actual = {
        (row["target_addr"], row["from_addr"], row["from_function"], row["ref_type"])
        for row in rows
    }
    for expected in EXPECTED_XREFS:
        normalized = (normalize_addr(expected[0]), normalize_addr(expected[1]), expected[2], expected[3])
        require(normalized in actual, f"missing xref {expected}")


def check_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    require(len(rows) == 1566, f"expected 1566 instruction rows, got {len(rows)}")
    actual = {
        (row["instruction_addr"], row["mnemonic"], row["operands"], row["function_name"])
        for row in rows
        if row.get("function_entry") == row.get("target_addr")
    }
    for expected in EXPECTED_RETS:
        normalized = (normalize_addr(expected[0]), expected[1], expected[2], expected[3])
        require(normalized in actual, f"missing instruction {expected}")


def check_decomp(base: Path) -> None:
    index_rows = read_tsv(base / "post_decomp" / "index.tsv")
    require(len(index_rows) == len(TARGETS), f"expected {len(TARGETS)} decompile rows, got {len(index_rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(index_rows, address)
        require(row["status"] == "OK", f"{address} decompile status is {row['status']}")
        path = find_decomp_file(base / "post_decomp", address, expected["name"])
        text = path.read_text(encoding="utf-8")
        for token in expected["decompile_tokens"]:
            require(token_present(text, token), f"{address} decompile missing token {token!r}")


def check_context(base: Path) -> None:
    metadata_rows = read_tsv(base / "post_context_metadata.tsv")
    require(len(metadata_rows) == 6, f"expected 6 context metadata rows, got {len(metadata_rows)}")
    index_rows = read_tsv(base / "post_context_decomp" / "index.tsv")
    require(len(index_rows) == 6, f"expected 6 context decompile rows, got {len(index_rows)}")
    for address, tokens in EXPECTED_CONTEXT_TOKENS.items():
        row = row_by_address(index_rows, address)
        require(row["status"] == "OK", f"{address} context decompile status is {row['status']}")
        candidates = sorted((base / "post_context_decomp").glob(f"{normalize_addr(address)[2:]}_*.c"))
        require(bool(candidates), f"missing context decompile file for {address}")
        text = candidates[0].read_text(encoding="utf-8")
        for token in tokens:
            require(token_present(text, token), f"{address} context decompile missing token {token!r}")


def check_public_note() -> None:
    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    text = PUBLIC_NOTE.read_text(encoding="utf-8")
    for token in PUBLIC_NOTE_TOKENS:
        require(token_present(text, token), f"public note missing token {token!r}")
    for token in OVERCLAIM_TOKENS:
        require(not token_present(text, token), f"public note overclaims with {token!r}")


def run_checks(base: Path) -> None:
    check_metadata(base)
    check_tags(base)
    check_xrefs(base)
    check_instructions(base)
    check_decomp(base)
    check_context(base)
    check_public_note()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true", help="run checks and print PASS")
    args = parser.parse_args()

    try:
        run_checks(args.base)
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("Wave523 targeting probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
