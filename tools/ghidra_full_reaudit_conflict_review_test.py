#!/usr/bin/env python3
"""Focused tests for recovered full re-audit conflict review."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import ghidra_full_reaudit_conflict_review as review


class GhidraFullReauditConflictReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="ghidra-conflict-review-")
        self.root = Path(self.temp_dir.name)
        self.conflicts_path = self.root / "conflicts.json"
        self.conflicts_path.write_text(
            json.dumps(
                [
                    self.conflict(
                        "0x00401000",
                        [
                            self.variant("PASS_STATIC_OK_REBUILD_THIN", reasoning="first wording"),
                            self.variant("PASS_STATIC_OK_REBUILD_THIN", reasoning="second wording"),
                        ],
                    ),
                    self.conflict(
                        "0x00402000",
                        [
                            self.variant("FAIL_NEEDS_MUTATION", proposed_comment="first"),
                            self.variant("FAIL_NEEDS_MUTATION", proposed_comment="second"),
                        ],
                    ),
                    self.conflict(
                        "0x00403000",
                        [
                            self.variant("PASS_STATIC_OK_REBUILD_THIN"),
                            self.variant("FAIL_NEEDS_MUTATION", proposed_comment="fix"),
                        ],
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        self.valid_rows = [
            self.row("0x00401000", 2, "narrative-only", ["PASS_STATIC_OK_REBUILD_THIN"]),
            self.row("0x00402000", 2, "mutation-disagreement", ["FAIL_NEEDS_MUTATION"]),
            self.row(
                "0x00403000",
                2,
                "verdict-disagreement",
                ["FAIL_NEEDS_MUTATION", "PASS_STATIC_OK_REBUILD_THIN"],
            ),
        ]

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def variant(verdict: str, *, reasoning: str = "reason", proposed_comment: str | None = None) -> dict[str, object]:
        return {
            "row": {
                "campaignId": "ghidra-full-reaudit-20260712",
                "address": "placeholder",
                "nameBefore": "Function",
                "nameAfter": "Function",
                "verdict": verdict,
                "mutated": proposed_comment is not None,
                "proposedRename": None,
                "proposedComment": proposed_comment,
                "reasoning": reasoning,
            },
            "occurrenceCount": 1,
            "sources": [],
        }

    @staticmethod
    def conflict(address: str, variants: list[dict[str, object]]) -> dict[str, object]:
        for variant in variants:
            variant["row"]["address"] = address  # type: ignore[index]
        return {"address": address, "variants": variants}

    @staticmethod
    def row(address: str, count: int, conflict_class: str, verdicts: list[str]) -> dict[str, object]:
        return {
            "schemaVersion": "onslaught-ghidra-full-reaudit-conflict-review.v1",
            "address": address,
            "variantCount": count,
            "conflictClass": conflict_class,
            "recoveredVerdicts": verdicts,
            "disposition": "accepted",
            "evidence": ["final-decompile", "final-instructions", "final-xrefs", "recovered-conflict"],
            "rationale": "Independent static evidence resolves the recovered variants.",
            "correction": None,
            "docFindings": [],
            "reviewer": "codex-test",
        }

    def test_classifies_and_accepts_complete_conflict_review(self) -> None:
        conflicts = review.load_conflicts(self.conflicts_path)

        summary = review.validate_review(conflicts, self.valid_rows)

        self.assertEqual(summary["reviewedAddressCount"], 3)
        self.assertEqual(
            summary["conflictClasses"],
            {"mutation-disagreement": 1, "narrative-only": 1, "verdict-disagreement": 1},
        )

    def test_rejects_coverage_metadata_evidence_and_correction_mismatch(self) -> None:
        conflicts = review.load_conflicts(self.conflicts_path)
        with self.assertRaisesRegex(review.ConflictReviewError, "coverage"):
            review.validate_review(conflicts, self.valid_rows[:2])

        wrong_class = copy.deepcopy(self.valid_rows)
        wrong_class[0]["conflictClass"] = "verdict-disagreement"
        with self.assertRaisesRegex(review.ConflictReviewError, "conflictClass"):
            review.validate_review(conflicts, wrong_class)

        wrong_count = copy.deepcopy(self.valid_rows)
        wrong_count[0]["variantCount"] = 3
        with self.assertRaisesRegex(review.ConflictReviewError, "variantCount"):
            review.validate_review(conflicts, wrong_count)

        weak = copy.deepcopy(self.valid_rows)
        weak[0]["evidence"].remove("final-instructions")  # type: ignore[union-attr]
        with self.assertRaisesRegex(review.ConflictReviewError, "final-instructions"):
            review.validate_review(conflicts, weak)

        correction = copy.deepcopy(self.valid_rows)
        correction[0]["disposition"] = "correction-required"
        with self.assertRaisesRegex(review.ConflictReviewError, "correction payload"):
            review.validate_review(conflicts, correction)

    def test_renders_canonical_conflict_review_in_address_order(self) -> None:
        rendered = review.render_canonical_review(list(reversed(self.valid_rows)))

        lines = rendered.splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(json.loads(lines[0])["address"], "0x00401000")
        self.assertEqual(json.loads(lines[-1])["address"], "0x00403000")
        self.assertTrue(rendered.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
