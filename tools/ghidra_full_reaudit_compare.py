#!/usr/bin/env python3
"""Compare trusted Ghidra audit snapshots for the recovered full re-audit."""

from __future__ import annotations

import argparse
import csv
import dataclasses
import json
from collections import Counter
from pathlib import Path


QUALITY_FIELDS = ("address", "name", "signature", "comment", "status")
AUDIT_FIELDS = QUALITY_FIELDS + (
    "body_ranges",
    "body_address_count",
    "prototype_key",
    "calling_convention",
    "var_args",
    "custom_variable_storage",
    "no_return",
    "inline",
    "thunk",
    "thunk_target",
)
CHANGE_FIELDS = ("name", "signature", "comment")
FUNCTION_ATTRIBUTE_FIELDS = ("inline", "thunk", "thunk_target")


class ComparisonError(ValueError):
    """Raised when snapshot inputs are incomplete or not comparable."""


@dataclasses.dataclass(frozen=True)
class ChangedRow:
    address: str
    changed_fields: tuple[str, ...]
    signature_change_is_name_rendering_only: bool
    before: dict[str, str]
    after: dict[str, str]

    def to_json(self) -> dict[str, object]:
        return {
            "address": self.address,
            "changedFields": list(self.changed_fields),
            "signatureChangeIsNameRenderingOnly": self.signature_change_is_name_rendering_only,
            "before": self.before,
            "after": self.after,
        }


@dataclasses.dataclass(frozen=True)
class ComparisonResult:
    address_count: int
    changed: tuple[ChangedRow, ...]
    change_combinations: dict[str, int]
    non_name_signature_changes: tuple[str, ...]
    prototype_changes: tuple[str, ...]
    boundary_changes: tuple[str, ...]
    function_attribute_changes: tuple[str, ...]

    def to_json(self) -> dict[str, object]:
        return {
            "addressCount": self.address_count,
            "changedAddressCount": len(self.changed),
            "changeCombinations": self.change_combinations,
            "nonNameRenderedSignatureChanges": list(self.non_name_signature_changes),
            "prototypeChanges": list(self.prototype_changes),
            "boundaryChanges": list(self.boundary_changes),
            "functionAttributeChanges": list(self.function_attribute_changes),
            "changed": [row.to_json() for row in self.changed],
        }


def load_snapshot(path: Path, required_fields: tuple[str, ...] = AUDIT_FIELDS) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = tuple(reader.fieldnames or ())
        missing = sorted(set(required_fields) - set(fields))
        if missing:
            raise ComparisonError(f"snapshot missing columns: {', '.join(missing)}")
        result: dict[str, dict[str, str]] = {}
        for row in reader:
            address = (row.get("address") or "").lower()
            if not address:
                raise ComparisonError("snapshot contains an empty address")
            if address in result:
                raise ComparisonError(f"snapshot contains duplicate address: {address}")
            result[address] = {key: row.get(key, "") for key in fields}
    return result


def require_same_addresses(before: dict[str, dict[str, str]], after: dict[str, dict[str, str]]) -> None:
    if set(before) != set(after):
        missing = sorted(set(before) - set(after))
        extra = sorted(set(after) - set(before))
        raise ComparisonError(
            f"snapshot address sets differ: missing={len(missing)} extra={len(extra)}"
        )


def normalized_signature(row: dict[str, str]) -> str:
    name = row["name"]
    return row["signature"].replace(name, "<FUNCTION_NAME>", 1)


def compare_snapshots(
    before: dict[str, dict[str, str]],
    after: dict[str, dict[str, str]],
) -> ComparisonResult:
    require_same_addresses(before, after)
    changed: list[ChangedRow] = []
    combinations: Counter[str] = Counter()
    non_name_signature_changes: list[str] = []
    prototype_changes: list[str] = []
    boundary_changes: list[str] = []
    function_attribute_changes: list[str] = []

    for address in sorted(before):
        left = before[address]
        right = after[address]
        fields = tuple(field for field in CHANGE_FIELDS if left[field] != right[field])
        if fields:
            rendering_only = "signature" not in fields or normalized_signature(left) == normalized_signature(right)
            changed.append(ChangedRow(address, fields, rendering_only, left, right))
            combinations["|".join(fields)] += 1
            if "signature" in fields and not rendering_only:
                non_name_signature_changes.append(address)
        if left["prototype_key"] != right["prototype_key"]:
            prototype_changes.append(address)
        if (
            left["body_ranges"] != right["body_ranges"]
            or left["body_address_count"] != right["body_address_count"]
        ):
            boundary_changes.append(address)
        if any(left[field] != right[field] for field in FUNCTION_ATTRIBUTE_FIELDS):
            function_attribute_changes.append(address)

    return ComparisonResult(
        address_count=len(before),
        changed=tuple(changed),
        change_combinations=dict(sorted(combinations.items())),
        non_name_signature_changes=tuple(non_name_signature_changes),
        prototype_changes=tuple(prototype_changes),
        boundary_changes=tuple(boundary_changes),
        function_attribute_changes=tuple(function_attribute_changes),
    )


def compare_quality_fields(
    expected: dict[str, dict[str, str]],
    actual: dict[str, dict[str, str]],
) -> tuple[str, ...]:
    require_same_addresses(expected, actual)
    return tuple(
        address
        for address in sorted(expected)
        if any(expected[address][field] != actual[address][field] for field in QUALITY_FIELDS[1:])
    )


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-audit", required=True, type=Path)
    parser.add_argument("--final-audit", required=True, type=Path)
    parser.add_argument("--retained-final-quality", type=Path)
    parser.add_argument("--reexported-final-quality", type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--changed-addresses", required=True, type=Path)
    args = parser.parse_args()

    try:
        result = compare_snapshots(load_snapshot(args.baseline_audit), load_snapshot(args.final_audit))
        payload = result.to_json()
        if bool(args.retained_final_quality) != bool(args.reexported_final_quality):
            raise ComparisonError("provide both final quality snapshots or neither")
        if args.retained_final_quality:
            retained = load_snapshot(args.retained_final_quality, QUALITY_FIELDS)
            reexported = load_snapshot(args.reexported_final_quality, QUALITY_FIELDS)
            quality_differences = compare_quality_fields(retained, reexported)
            payload["retainedFinalQualityReexportDifferenceCount"] = len(quality_differences)
            payload["retainedFinalQualityReexportDifferences"] = list(quality_differences)
        write_json(args.summary, payload)
        args.changed_addresses.parent.mkdir(parents=True, exist_ok=True)
        args.changed_addresses.write_text(
            "".join(f"{row.address}\n" for row in result.changed),
            encoding="utf-8",
            newline="\n",
        )
    except (ComparisonError, OSError) as exc:
        print("Ghidra full re-audit comparison: FAIL")
        print(f"- {exc}")
        return 1

    print(
        "Ghidra full re-audit comparison: PASS "
        f"addresses={result.address_count} changed={len(result.changed)} "
        f"prototypeChanges={len(result.prototype_changes)} boundaryChanges={len(result.boundary_changes)} "
        f"functionAttributeChanges={len(result.function_attribute_changes)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
