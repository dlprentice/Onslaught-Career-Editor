#!/usr/bin/env python3
"""Validate the public-safe independent semantic review ledger."""

from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "onslaught-ghidra-full-reaudit-phase-a-review.v1"
CORRECTION_SCHEMA_VERSION = "onslaught-ghidra-full-reaudit-corrections.v1"
EXACT_KEYS = {
    "schemaVersion",
    "address",
    "changeClass",
    "disposition",
    "nameVerdict",
    "commentVerdict",
    "evidence",
    "rationale",
    "correction",
    "docFindings",
    "reviewer",
}
DISPOSITIONS = {"accepted", "correction-required", "research-required"}
FIELD_VERDICTS = {"accepted", "correction-required", "research-required", "not-changed"}
CORRECTION_KEYS = {"proposedName", "proposedComment"}
REQUIRED_FINAL_EVIDENCE = {"final-decompile", "final-instructions", "final-xrefs"}
RECOVERY_EVIDENCE = {"recovered-row", "recovered-conflict", "recovered-gap"}
ABSOLUTE_PATH = re.compile(r"(?i)(?:[a-z]:[\\/]|/(?:home|mnt|tmp|users?)/)")


class LedgerError(ValueError):
    """Raised when independent semantic review evidence is incomplete."""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LedgerError(f"{path.name}:{line_number} invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise LedgerError(f"{path.name}:{line_number} must be an object")
        rows.append(value)
    return rows


def load_delta(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(path):
        address = str(row.get("address", "")).lower()
        if not address:
            raise LedgerError("delta row missing address")
        if address in result:
            raise LedgerError(f"delta duplicate address: {address}")
        result[address] = row
    return result


def load_recovery_partition(root: Path) -> dict[str, str]:
    sources: tuple[tuple[str, list[str]], ...] = (
        (
            "recovered-row",
            [
                str(row.get("address", "")).lower()
                for row in read_jsonl(root / "review-ledger-unambiguous-recovered.jsonl")
            ],
        ),
        (
            "recovered-conflict",
            [
                str(row.get("address", "")).lower()
                for row in json.loads(
                    (root / "review-ledger-conflicts-recovered.json").read_text(encoding="utf-8-sig")
                )
            ],
        ),
        (
            "recovered-gap",
            [
                line.split("\t", 1)[0].strip().lower()
                for line in (root / "review-ledger-recovery-gaps.tsv")
                .read_text(encoding="utf-8-sig")
                .splitlines()[1:]
                if line.strip()
            ],
        ),
    )
    partition: dict[str, str] = {}
    for classification, addresses in sources:
        for address in addresses:
            if not address:
                raise LedgerError(f"{classification} recovery entry missing address")
            if address in partition:
                raise LedgerError(f"recovery partition duplicate address: {address}")
            partition[address] = classification
    return partition


def normalize_recovery_evidence(
    rows: Iterable[dict[str, Any]],
    partition: dict[str, str],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        address = str(row.get("address", "")).lower()
        classification = partition.get(address)
        if classification is None:
            raise LedgerError(f"{address or '<missing-address>'} absent from recovery partition")
        evidence = row.get("evidence")
        if not isinstance(evidence, list):
            raise LedgerError(f"{address} evidence must be a string array")
        normalized_row = dict(row)
        normalized_row["evidence"] = [
            *[token for token in evidence if token not in RECOVERY_EVIDENCE],
            classification,
        ]
        normalized.append(normalized_row)
    return normalized


def render_canonical_ledger(rows: Iterable[dict[str, Any]]) -> str:
    ordered = sorted(rows, key=lambda row: str(row.get("address", "")).lower())
    return "".join(
        json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        for row in ordered
    )


def apply_review_overrides(
    rows: Iterable[dict[str, Any]],
    overrides: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    original = list(rows)
    known: set[str] = set()
    for row in original:
        address = str(row.get("address", "")).lower()
        if address in known:
            raise LedgerError(f"ledger duplicate address: {address}")
        known.add(address)
    replacements: dict[str, dict[str, Any]] = {}
    for row in overrides:
        address = str(row.get("address", "")).lower()
        if address not in known:
            raise LedgerError(f"override references unknown address: {address or '<missing-address>'}")
        if address in replacements:
            raise LedgerError(f"override duplicate address: {address}")
        replacements[address] = row
    return [dict(replacements.get(str(row.get("address", "")).lower(), row)) for row in original]


def build_correction_manifest(
    delta: dict[str, dict[str, Any]],
    rows: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: str(item.get("address", "")).lower()):
        if row.get("disposition") != "correction-required":
            continue
        address = str(row.get("address", "")).lower()
        delta_row = delta.get(address)
        current = delta_row.get("after") if isinstance(delta_row, dict) else None
        correction = row.get("correction")
        if not isinstance(current, dict) or not isinstance(correction, dict):
            raise LedgerError(f"{address} cannot build correction manifest from incomplete evidence")
        current_name = current.get("name")
        current_comment = current.get("comment")
        if not isinstance(current_name, str) or not isinstance(current_comment, str):
            raise LedgerError(f"{address} current name/comment must be strings")
        corrected_name = correction.get("proposedName") or current_name
        corrected_comment = correction.get("proposedComment") or current_comment
        corrected_fields = [
            field
            for field, before, after in (
                ("name", current_name, corrected_name),
                ("comment", current_comment, corrected_comment),
            )
            if before != after
        ]
        if not corrected_fields:
            raise LedgerError(f"{address} correction does not change name or comment")
        records.append(
            {
                "address": address,
                "changeClass": row["changeClass"],
                "correctedFields": corrected_fields,
                "currentName": current_name,
                "currentComment": current_comment,
                "correctedName": corrected_name,
                "correctedComment": corrected_comment,
                "evidence": row["evidence"],
                "rationale": row["rationale"],
                "docFindings": row["docFindings"],
            }
        )
    return {
        "schemaVersion": CORRECTION_SCHEMA_VERSION,
        "sourceCampaign": "ghidra-full-reaudit-20260712",
        "recordCount": len(records),
        "prototypeOrBoundaryMutationAuthorized": False,
        "records": records,
    }


def expected_change_class(delta_row: dict[str, Any]) -> str:
    fields = set(delta_row.get("changedFields") or [])
    if "name" in fields and "comment" in fields:
        return "rename+comment"
    if "name" in fields:
        return "rename"
    if fields == {"comment"}:
        return "comment-only"
    raise LedgerError(f"unsupported delta field combination: {sorted(fields)}")


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LedgerError(f"{label} must be a non-empty string")
    return value


def validate_row(address: str, delta_row: dict[str, Any], row: dict[str, Any]) -> None:
    if set(row) != EXACT_KEYS:
        raise LedgerError(f"{address} ledger keys must match the exact schema")
    if row["schemaVersion"] != SCHEMA_VERSION:
        raise LedgerError(f"{address} schemaVersion mismatch")
    if row["address"] != address:
        raise LedgerError(f"{address} must be canonical lowercase")
    expected_class = expected_change_class(delta_row)
    if row["changeClass"] != expected_class:
        raise LedgerError(f"{address} changeClass must be {expected_class}")
    if row["disposition"] not in DISPOSITIONS:
        raise LedgerError(f"{address} invalid disposition")
    if row["nameVerdict"] not in FIELD_VERDICTS or row["commentVerdict"] not in FIELD_VERDICTS:
        raise LedgerError(f"{address} invalid field verdict")

    if expected_class == "comment-only" and row["nameVerdict"] != "not-changed":
        raise LedgerError(f"{address} comment-only nameVerdict must be not-changed")
    if expected_class == "rename" and row["commentVerdict"] != "not-changed":
        raise LedgerError(f"{address} rename commentVerdict must be not-changed")
    if expected_class.startswith("rename") and row["nameVerdict"] == "not-changed":
        raise LedgerError(f"{address} changed nameVerdict must not be not-changed")
    if expected_class != "rename" and row["commentVerdict"] == "not-changed":
        raise LedgerError(f"{address} changed commentVerdict must not be not-changed")

    field_verdicts = (row["nameVerdict"], row["commentVerdict"])
    if "correction-required" in field_verdicts:
        expected_disposition = "correction-required"
    elif "research-required" in field_verdicts:
        expected_disposition = "research-required"
    else:
        expected_disposition = "accepted"
    if row["disposition"] != expected_disposition:
        raise LedgerError(f"{address} disposition must be {expected_disposition}")

    evidence = row["evidence"]
    if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
        raise LedgerError(f"{address} evidence must be a string array")
    evidence_set = set(evidence)
    for token in sorted(REQUIRED_FINAL_EVIDENCE):
        if token not in evidence_set:
            raise LedgerError(f"{address} missing evidence: {token}")
    if not evidence_set.intersection(RECOVERY_EVIDENCE):
        raise LedgerError(f"{address} missing recovered-row/conflict/gap classification")
    if expected_class.startswith("rename"):
        for token in ("baseline-decompile", "baseline-instructions"):
            if token not in evidence_set:
                raise LedgerError(f"{address} missing evidence: {token}")

    require_string(row["rationale"], f"{address} rationale")
    require_string(row["reviewer"], f"{address} reviewer")
    if not isinstance(row["docFindings"], list) or not all(isinstance(item, str) for item in row["docFindings"]):
        raise LedgerError(f"{address} docFindings must be a string array")

    serialized = json.dumps(row, ensure_ascii=True)
    if ABSOLUTE_PATH.search(serialized):
        raise LedgerError(f"{address} contains an absolute path")

    correction_required = "correction-required" in (row["nameVerdict"], row["commentVerdict"])
    if correction_required:
        correction = row["correction"]
        if not isinstance(correction, dict) or not correction or not set(correction).issubset(CORRECTION_KEYS):
            raise LedgerError(f"{address} correction payload is required")
        for key, value in correction.items():
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise LedgerError(f"{address} {key} must be a non-empty string or null")
        if not any(isinstance(correction.get(key), str) and correction[key].strip() for key in CORRECTION_KEYS):
            raise LedgerError(f"{address} correction payload is required")
    elif row["correction"] is not None:
        raise LedgerError(f"{address} correction must be null without a correction verdict")


def validate_ledger(
    delta: dict[str, dict[str, Any]],
    rows: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    by_address: dict[str, dict[str, Any]] = {}
    for row in rows:
        address = str(row.get("address", "")).lower()
        if address in by_address:
            raise LedgerError(f"ledger duplicate address: {address}")
        by_address[address] = row
    if set(by_address) != set(delta):
        missing = sorted(set(delta) - set(by_address))
        extra = sorted(set(by_address) - set(delta))
        raise LedgerError(f"ledger coverage mismatch: missing={len(missing)} extra={len(extra)}")
    for address in sorted(delta):
        validate_row(address, delta[address], by_address[address])
    dispositions = collections.Counter(str(row["disposition"]) for row in by_address.values())
    classes = collections.Counter(str(row["changeClass"]) for row in by_address.values())
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewedAddressCount": len(by_address),
        "dispositions": dict(sorted(dispositions.items())),
        "changeClasses": dict(sorted(classes.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delta", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path, nargs="+")
    parser.add_argument("--override-ledger", type=Path, nargs="+")
    parser.add_argument("--recovery-dir", type=Path)
    parser.add_argument("--canonical-ledger", type=Path)
    parser.add_argument("--correction-manifest", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    try:
        rows: list[dict[str, Any]] = []
        for path in args.ledger:
            rows.extend(read_jsonl(path))
        if args.override_ledger:
            overrides: list[dict[str, Any]] = []
            for path in args.override_ledger:
                overrides.extend(read_jsonl(path))
            rows = apply_review_overrides(rows, overrides)
        if args.canonical_ledger and not args.recovery_dir:
            raise LedgerError("--canonical-ledger requires --recovery-dir")
        if args.recovery_dir:
            rows = normalize_recovery_evidence(rows, load_recovery_partition(args.recovery_dir))
        delta = load_delta(args.delta)
        summary = validate_ledger(delta, rows)
        summary["recoveryClasses"] = dict(
            sorted(
                collections.Counter(
                    next(token for token in row["evidence"] if token in RECOVERY_EVIDENCE)
                    for row in rows
                ).items()
            )
        )
        if args.canonical_ledger:
            args.canonical_ledger.parent.mkdir(parents=True, exist_ok=True)
            args.canonical_ledger.write_text(render_canonical_ledger(rows), encoding="utf-8")
        if args.correction_manifest:
            args.correction_manifest.parent.mkdir(parents=True, exist_ok=True)
            args.correction_manifest.write_text(
                json.dumps(build_correction_manifest(delta, rows), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        if args.summary:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (LedgerError, OSError) as exc:
        print("Ghidra full re-audit semantic ledger: FAIL")
        print(f"- {exc}")
        return 1
    print(
        "Ghidra full re-audit semantic ledger: PASS "
        f"reviewed={summary['reviewedAddressCount']} dispositions={json.dumps(summary['dispositions'], sort_keys=True)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
