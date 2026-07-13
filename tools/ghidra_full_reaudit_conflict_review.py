#!/usr/bin/env python3
"""Validate independent review of recovered full re-audit conflict variants."""

from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "onslaught-ghidra-full-reaudit-conflict-review.v1"
EXACT_KEYS = {
    "schemaVersion",
    "address",
    "variantCount",
    "conflictClass",
    "recoveredVerdicts",
    "disposition",
    "evidence",
    "rationale",
    "correction",
    "docFindings",
    "reviewer",
}
DISPOSITIONS = {"accepted", "correction-required", "research-required"}
REQUIRED_EVIDENCE = {"final-decompile", "final-instructions", "final-xrefs", "recovered-conflict"}
ACTION_FIELDS = (
    "nameBefore",
    "nameAfter",
    "verdict",
    "mutated",
    "proposedRename",
    "proposedComment",
)
CORRECTION_KEYS = {"proposedName", "proposedComment"}
ABSOLUTE_PATH = re.compile(r"(?i)(?:[a-z]:[\\/]|/(?:home|mnt|tmp|users?)/)")


class ConflictReviewError(ValueError):
    """Raised when recovered-conflict review evidence is incomplete."""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ConflictReviewError(f"{path.name}:{line_number} invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ConflictReviewError(f"{path.name}:{line_number} must be an object")
        rows.append(row)
    return rows


def load_conflicts(path: Path) -> dict[str, dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ConflictReviewError(f"{path.name} invalid JSON: {exc}") from exc
    if not isinstance(payload, list):
        raise ConflictReviewError("conflict artifact must be an array")
    result: dict[str, dict[str, Any]] = {}
    for item in payload:
        if not isinstance(item, dict):
            raise ConflictReviewError("conflict entry must be an object")
        address = str(item.get("address", "")).lower()
        variants = item.get("variants")
        if not address or not isinstance(variants, list) or len(variants) < 2:
            raise ConflictReviewError(f"invalid conflict entry: {address or '<missing-address>'}")
        if address in result:
            raise ConflictReviewError(f"duplicate conflict address: {address}")
        for variant in variants:
            row = variant.get("row") if isinstance(variant, dict) else None
            if not isinstance(row, dict) or str(row.get("address", "")).lower() != address:
                raise ConflictReviewError(f"{address} contains an invalid variant row")
        result[address] = item
    return result


def conflict_class(item: dict[str, Any]) -> str:
    rows = [variant["row"] for variant in item["variants"]]
    if len({row.get("verdict") for row in rows}) > 1:
        return "verdict-disagreement"
    action_keys = {
        tuple(json.dumps(row.get(field), sort_keys=True) for field in ACTION_FIELDS)
        for row in rows
    }
    if len(action_keys) > 1:
        return "mutation-disagreement"
    return "narrative-only"


def recovered_verdicts(item: dict[str, Any]) -> list[str]:
    return sorted({str(variant["row"].get("verdict")) for variant in item["variants"]})


def require_nonempty_string(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ConflictReviewError(f"{label} must be a non-empty string")


def validate_correction(address: str, disposition: str, correction: Any) -> None:
    if disposition != "correction-required":
        if correction is not None:
            raise ConflictReviewError(f"{address} correction must be null without correction-required")
        return
    if not isinstance(correction, dict) or not correction or not set(correction).issubset(CORRECTION_KEYS):
        raise ConflictReviewError(f"{address} correction payload is required")
    for key, value in correction.items():
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ConflictReviewError(f"{address} {key} must be a non-empty string or null")
    if not any(isinstance(correction.get(key), str) and correction[key].strip() for key in CORRECTION_KEYS):
        raise ConflictReviewError(f"{address} correction payload is required")


def validate_row(address: str, item: dict[str, Any], row: dict[str, Any]) -> None:
    if set(row) != EXACT_KEYS:
        raise ConflictReviewError(f"{address} review keys must match the exact schema")
    if row["schemaVersion"] != SCHEMA_VERSION or row["address"] != address:
        raise ConflictReviewError(f"{address} schema or canonical address mismatch")
    expected_count = len(item["variants"])
    if row["variantCount"] != expected_count:
        raise ConflictReviewError(f"{address} variantCount must be {expected_count}")
    expected_class = conflict_class(item)
    if row["conflictClass"] != expected_class:
        raise ConflictReviewError(f"{address} conflictClass must be {expected_class}")
    expected_verdicts = recovered_verdicts(item)
    if row["recoveredVerdicts"] != expected_verdicts:
        raise ConflictReviewError(f"{address} recoveredVerdicts mismatch")
    if row["disposition"] not in DISPOSITIONS:
        raise ConflictReviewError(f"{address} invalid disposition")

    evidence = row["evidence"]
    if not isinstance(evidence, list) or not all(isinstance(value, str) for value in evidence):
        raise ConflictReviewError(f"{address} evidence must be a string array")
    for token in sorted(REQUIRED_EVIDENCE):
        if token not in evidence:
            raise ConflictReviewError(f"{address} missing evidence: {token}")

    require_nonempty_string(row["rationale"], f"{address} rationale")
    require_nonempty_string(row["reviewer"], f"{address} reviewer")
    if not isinstance(row["docFindings"], list) or not all(isinstance(value, str) for value in row["docFindings"]):
        raise ConflictReviewError(f"{address} docFindings must be a string array")
    validate_correction(address, row["disposition"], row["correction"])
    if ABSOLUTE_PATH.search(json.dumps(row, ensure_ascii=True)):
        raise ConflictReviewError(f"{address} contains an absolute path")


def validate_review(
    conflicts: dict[str, dict[str, Any]],
    rows: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    by_address: dict[str, dict[str, Any]] = {}
    for row in rows:
        address = str(row.get("address", "")).lower()
        if address in by_address:
            raise ConflictReviewError(f"duplicate review address: {address}")
        by_address[address] = row
    if set(by_address) != set(conflicts):
        missing = sorted(set(conflicts) - set(by_address))
        extra = sorted(set(by_address) - set(conflicts))
        raise ConflictReviewError(f"review coverage mismatch: missing={len(missing)} extra={len(extra)}")
    for address in sorted(conflicts):
        validate_row(address, conflicts[address], by_address[address])
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewedAddressCount": len(by_address),
        "conflictClasses": dict(sorted(collections.Counter(row["conflictClass"] for row in by_address.values()).items())),
        "dispositions": dict(sorted(collections.Counter(row["disposition"] for row in by_address.values()).items())),
    }


def render_canonical_review(rows: Iterable[dict[str, Any]]) -> str:
    ordered = sorted(rows, key=lambda row: str(row.get("address", "")).lower())
    return "".join(
        json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        for row in ordered
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conflicts", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path, nargs="+")
    parser.add_argument("--canonical-ledger", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    try:
        rows: list[dict[str, Any]] = []
        for path in args.ledger:
            rows.extend(read_jsonl(path))
        summary = validate_review(load_conflicts(args.conflicts), rows)
        if args.canonical_ledger:
            args.canonical_ledger.parent.mkdir(parents=True, exist_ok=True)
            args.canonical_ledger.write_text(render_canonical_review(rows), encoding="utf-8")
        if args.summary:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (ConflictReviewError, OSError) as exc:
        print("Ghidra full re-audit conflict review: FAIL")
        print(f"- {exc}")
        return 1
    print(
        "Ghidra full re-audit conflict review: PASS "
        f"reviewed={summary['reviewedAddressCount']} dispositions={json.dumps(summary['dispositions'], sort_keys=True)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
