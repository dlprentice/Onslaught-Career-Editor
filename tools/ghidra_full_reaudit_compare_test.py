#!/usr/bin/env python3
"""Focused tests for trusted-snapshot Ghidra full re-audit comparison."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import ghidra_full_reaudit_compare as compare


AUDIT_FIELDS = (
    "address",
    "name",
    "signature",
    "comment",
    "status",
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


class GhidraFullReauditCompareTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="ghidra-reaudit-compare-")
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_tsv(self, name: str, rows: list[dict[str, str]]) -> Path:
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=AUDIT_FIELDS, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        return path

    @staticmethod
    def row(address: str, name: str, **updates: str) -> dict[str, str]:
        result = {
            "address": address,
            "name": name,
            "signature": f"void {name}(int value)",
            "comment": "old comment",
            "status": "OK",
            "body_ranges": f"{address[2:]}-{address[2:]}ff",
            "body_address_count": "256",
            "prototype_key": "cc=__cdecl|ret=void|params=int@Stack[0x4]",
            "calling_convention": "__cdecl",
            "var_args": "false",
            "custom_variable_storage": "false",
            "no_return": "false",
            "inline": "false",
            "thunk": "false",
            "thunk_target": "",
        }
        result.update(updates)
        return result

    def test_reports_name_rendering_only_and_comment_combinations(self) -> None:
        before = [
            self.row("0x00401000", "OldName"),
            self.row("0x00402000", "Stable", comment="before"),
        ]
        after = [
            self.row("0x00401000", "NewName", signature="void NewName(int value)", comment="new comment"),
            self.row("0x00402000", "Stable", comment="after"),
        ]

        result = compare.compare_snapshots(
            compare.load_snapshot(self.write_tsv("before.tsv", before)),
            compare.load_snapshot(self.write_tsv("after.tsv", after)),
        )

        self.assertEqual(result.address_count, 2)
        self.assertEqual(len(result.changed), 2)
        self.assertEqual(result.change_combinations, {"comment": 1, "name|signature|comment": 1})
        self.assertEqual(result.non_name_signature_changes, ())
        self.assertEqual(result.prototype_changes, ())
        self.assertEqual(result.boundary_changes, ())
        self.assertEqual(result.function_attribute_changes, ())

    def test_detects_real_signature_prototype_and_boundary_changes(self) -> None:
        before = [self.row("0x00401000", "Function")]
        after = [
            self.row(
                "0x00401000",
                "Function",
                signature="int Function(float value)",
                prototype_key="cc=__cdecl|ret=int|params=float@Stack[0x4]",
                body_ranges="00401000-0040107f",
                body_address_count="128",
                thunk="true",
                thunk_target="0x00402000",
            )
        ]

        result = compare.compare_snapshots(
            compare.load_snapshot(self.write_tsv("before.tsv", before)),
            compare.load_snapshot(self.write_tsv("after.tsv", after)),
        )

        self.assertEqual(result.non_name_signature_changes, ("0x00401000",))
        self.assertEqual(result.prototype_changes, ("0x00401000",))
        self.assertEqual(result.boundary_changes, ("0x00401000",))
        self.assertEqual(result.function_attribute_changes, ("0x00401000",))

    def test_rejects_duplicate_or_mismatched_address_sets_and_missing_fields(self) -> None:
        duplicate = [self.row("0x00401000", "One"), self.row("0x00401000", "Two")]
        with self.assertRaisesRegex(compare.ComparisonError, "duplicate"):
            compare.load_snapshot(self.write_tsv("duplicate.tsv", duplicate))

        before = compare.load_snapshot(self.write_tsv("one.tsv", [self.row("0x00401000", "One")]))
        after = compare.load_snapshot(self.write_tsv("two.tsv", [self.row("0x00402000", "Two")]))
        with self.assertRaisesRegex(compare.ComparisonError, "address sets"):
            compare.compare_snapshots(before, after)

        missing_path = self.root / "missing.tsv"
        missing_path.write_text("address\tname\n0x00401000\tOne\n", encoding="utf-8")
        with self.assertRaisesRegex(compare.ComparisonError, "missing columns"):
            compare.load_snapshot(missing_path)

    def test_exact_export_comparison_scopes_to_quality_fields(self) -> None:
        retained = [self.row("0x00401000", "One")]
        reexport = [self.row("0x00401000", "One", body_ranges="different")]

        differences = compare.compare_quality_fields(
            compare.load_snapshot(self.write_tsv("retained.tsv", retained)),
            compare.load_snapshot(self.write_tsv("reexport.tsv", reexport)),
        )

        self.assertEqual(differences, ())


if __name__ == "__main__":
    unittest.main()
