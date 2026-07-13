#!/usr/bin/env python3
"""Focused tests for the independent full re-audit semantic ledger."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import ghidra_full_reaudit_review_ledger as ledger


class GhidraFullReauditReviewLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="ghidra-review-ledger-")
        self.root = Path(self.temp_dir.name)
        self.delta_path = self.root / "delta.jsonl"
        self.delta_path.write_text(
            "\n".join(
                json.dumps(row)
                for row in (
                    {
                        "address": "0x00401000",
                        "changedFields": ["name", "signature", "comment"],
                        "after": {"name": "NewName", "comment": "new comment"},
                    },
                    {
                        "address": "0x00402000",
                        "changedFields": ["comment"],
                        "after": {"name": "StableName", "comment": "updated comment"},
                    },
                )
            )
            + "\n",
            encoding="utf-8",
        )
        self.valid_rows = [
            self.row(
                "0x00401000",
                "rename+comment",
                "accepted",
                "accepted",
                [
                    "final-decompile",
                    "final-instructions",
                    "final-xrefs",
                    "baseline-decompile",
                    "baseline-instructions",
                    "recovered-row",
                ],
            ),
            self.row(
                "0x00402000",
                "comment-only",
                "not-changed",
                "accepted",
                ["final-decompile", "final-instructions", "final-xrefs", "recovered-gap"],
            ),
        ]

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def row(
        address: str,
        change_class: str,
        name_verdict: str,
        comment_verdict: str,
        evidence: list[str],
    ) -> dict[str, object]:
        return {
            "schemaVersion": "onslaught-ghidra-full-reaudit-phase-a-review.v1",
            "address": address,
            "changeClass": change_class,
            "disposition": "accepted",
            "nameVerdict": name_verdict,
            "commentVerdict": comment_verdict,
            "evidence": evidence,
            "rationale": "Independent body and caller evidence supports the bounded metadata.",
            "correction": None,
            "docFindings": [],
            "reviewer": "codex-test",
        }

    def test_accepts_complete_exact_independent_ledger(self) -> None:
        summary = ledger.validate_ledger(ledger.load_delta(self.delta_path), self.valid_rows)

        self.assertEqual(summary["reviewedAddressCount"], 2)
        self.assertEqual(summary["dispositions"], {"accepted": 2})

    def test_rejects_duplicate_missing_wrong_class_or_missing_evidence(self) -> None:
        duplicate = [self.valid_rows[0], copy.deepcopy(self.valid_rows[0])]
        with self.assertRaisesRegex(ledger.LedgerError, "duplicate"):
            ledger.validate_ledger(ledger.load_delta(self.delta_path), duplicate)

        with self.assertRaisesRegex(ledger.LedgerError, "coverage"):
            ledger.validate_ledger(ledger.load_delta(self.delta_path), [self.valid_rows[0]])

        wrong_class = copy.deepcopy(self.valid_rows)
        wrong_class[0]["changeClass"] = "comment-only"
        with self.assertRaisesRegex(ledger.LedgerError, "changeClass"):
            ledger.validate_ledger(ledger.load_delta(self.delta_path), wrong_class)

        weak_evidence = copy.deepcopy(self.valid_rows)
        weak_evidence[0]["evidence"].remove("baseline-decompile")  # type: ignore[union-attr]
        with self.assertRaisesRegex(ledger.LedgerError, "baseline-decompile"):
            ledger.validate_ledger(ledger.load_delta(self.delta_path), weak_evidence)

    def test_rejects_absolute_paths_and_correction_without_payload(self) -> None:
        leaking = copy.deepcopy(self.valid_rows)
        leaking[0]["docFindings"] = [r"C:\private\file.md"]
        with self.assertRaisesRegex(ledger.LedgerError, "absolute path"):
            ledger.validate_ledger(ledger.load_delta(self.delta_path), leaking)

        correction = copy.deepcopy(self.valid_rows)
        correction[0]["disposition"] = "correction-required"
        correction[0]["nameVerdict"] = "correction-required"
        with self.assertRaisesRegex(ledger.LedgerError, "correction payload"):
            ledger.validate_ledger(ledger.load_delta(self.delta_path), correction)

    def test_rejects_disposition_field_verdict_and_correction_inconsistency(self) -> None:
        wrong_disposition = copy.deepcopy(self.valid_rows)
        wrong_disposition[0]["nameVerdict"] = "correction-required"
        wrong_disposition[0]["correction"] = {"proposedName": "CorrectedName"}
        with self.assertRaisesRegex(ledger.LedgerError, "disposition must be correction-required"):
            ledger.validate_ledger(ledger.load_delta(self.delta_path), wrong_disposition)

        skipped_changed_field = copy.deepcopy(self.valid_rows)
        skipped_changed_field[0]["nameVerdict"] = "not-changed"
        with self.assertRaisesRegex(ledger.LedgerError, "changed nameVerdict"):
            ledger.validate_ledger(ledger.load_delta(self.delta_path), skipped_changed_field)

        malformed_payload = copy.deepcopy(self.valid_rows)
        malformed_payload[0]["disposition"] = "correction-required"
        malformed_payload[0]["nameVerdict"] = "correction-required"
        malformed_payload[0]["correction"] = {"proposedName": ["not", "a", "string"]}
        with self.assertRaisesRegex(ledger.LedgerError, "proposedName"):
            ledger.validate_ledger(ledger.load_delta(self.delta_path), malformed_payload)

    def test_normalizes_recovery_evidence_without_mutating_raw_rows(self) -> None:
        raw_rows = copy.deepcopy(self.valid_rows)
        raw_rows[0]["evidence"] = [
            "final-decompile",
            "final-instructions",
            "final-xrefs",
            "baseline-decompile",
            "baseline-instructions",
            "recovered-gap",
        ]

        normalized = ledger.normalize_recovery_evidence(
            raw_rows,
            {
                "0x00401000": "recovered-row",
                "0x00402000": "recovered-gap",
            },
        )

        self.assertIn("recovered-row", normalized[0]["evidence"])
        self.assertNotIn("recovered-gap", normalized[0]["evidence"])
        self.assertIn("recovered-gap", raw_rows[0]["evidence"])

    def test_loads_complete_disjoint_recovery_partition(self) -> None:
        recovery_dir = self.root / "recovery"
        recovery_dir.mkdir()
        (recovery_dir / "review-ledger-unambiguous-recovered.jsonl").write_text(
            json.dumps({"address": "0x00401000"}) + "\n",
            encoding="utf-8",
        )
        (recovery_dir / "review-ledger-conflicts-recovered.json").write_text(
            json.dumps([{"address": "0x00402000", "variants": [{}, {}]}]) + "\n",
            encoding="utf-8",
        )
        (recovery_dir / "review-ledger-recovery-gaps.tsv").write_text(
            "address\treason\n0x00403000\tmissing\n",
            encoding="utf-8",
        )

        partition = ledger.load_recovery_partition(recovery_dir)

        self.assertEqual(
            partition,
            {
                "0x00401000": "recovered-row",
                "0x00402000": "recovered-conflict",
                "0x00403000": "recovered-gap",
            },
        )

    def test_renders_canonical_ledger_in_address_order(self) -> None:
        rendered = ledger.render_canonical_ledger(list(reversed(self.valid_rows)))

        lines = rendered.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["address"], "0x00401000")
        self.assertEqual(json.loads(lines[1])["address"], "0x00402000")
        self.assertTrue(rendered.endswith("\n"))

    def test_applies_root_overrides_without_changing_raw_rows(self) -> None:
        raw_rows = copy.deepcopy(self.valid_rows)
        override = copy.deepcopy(raw_rows[0])
        override["rationale"] = "Root review resolved a cross-row contradiction from raw instructions."

        merged = ledger.apply_review_overrides(raw_rows, [override])

        self.assertEqual(merged[0]["rationale"], override["rationale"])
        self.assertNotEqual(raw_rows[0]["rationale"], override["rationale"])

        unknown = copy.deepcopy(override)
        unknown["address"] = "0x00403000"
        with self.assertRaisesRegex(ledger.LedgerError, "unknown address"):
            ledger.apply_review_overrides(raw_rows, [unknown])

    def test_builds_exact_public_safe_correction_manifest(self) -> None:
        rows = copy.deepcopy(self.valid_rows)
        rows[0]["disposition"] = "correction-required"
        rows[0]["nameVerdict"] = "correction-required"
        rows[0]["correction"] = {"proposedName": "CorrectedName"}
        delta = ledger.load_delta(self.delta_path)

        manifest = ledger.build_correction_manifest(delta, rows)

        self.assertEqual(manifest["recordCount"], 1)
        self.assertFalse(manifest["prototypeOrBoundaryMutationAuthorized"])
        record = manifest["records"][0]
        self.assertEqual(record["address"], "0x00401000")
        self.assertEqual(record["currentName"], "NewName")
        self.assertEqual(record["correctedName"], "CorrectedName")
        self.assertEqual(record["correctedFields"], ["name"])


if __name__ == "__main__":
    unittest.main()
