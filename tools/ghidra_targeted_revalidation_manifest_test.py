import json
import tempfile
import unittest
from pathlib import Path

import ghidra_targeted_revalidation_manifest as manifest


class TargetedRevalidationManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def ledger(self, name: str, rows: list[dict]) -> Path:
        path = self.root / name
        path.write_text(
            "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows),
            encoding="utf-8",
        )
        return path

    def metadata(self, rows: list[dict]) -> Path:
        path = self.root / "metadata.tsv"
        header = "address\tname\tsignature\tprototype_key\n"
        body = "".join(
            f"{row['address']}\t{row['name']}\t{row['signature']}\t{row['prototype_key']}\n"
            for row in rows
        )
        path.write_text(header + body, encoding="utf-8")
        return path

    def covered_manifest(self, records: list[dict]) -> Path:
        path = self.root / "covered.json"
        path.write_text(
            json.dumps({"records": records}),
            encoding="utf-8",
        )
        return path

    @staticmethod
    def research(address: str, disposition: str, correction: dict | None) -> dict:
        return {
            "schemaVersion": "onslaught-ghidra-full-reaudit-research-review.v1",
            "address": address,
            "savedName": "ResearchName",
            "recoveryEvidence": "exact-row",
            "disposition": disposition,
            "confidence": "bounded-static",
            "evidence": ["final-instructions"],
            "sourceAlignment": None,
            "rationale": "Research rationale.",
            "correction": correction,
            "docFindings": ["reverse-engineering/binary-analysis/functions/Test.md"],
            "reviewer": "researcher",
        }

    @staticmethod
    def critical(address: str, disposition: str, correction: dict | None) -> dict:
        return {
            "schemaVersion": "onslaught-ghidra-critical-review.v1",
            "address": address,
            "savedName": "CriticalName",
            "disposition": disposition,
            "confidence": "high-static",
            "evidence": ["final-instructions", "source-body"],
            "sourceAlignment": "direct",
            "rationale": "Critical rationale.",
            "correction": correction,
            "docFindings": ["release/readiness/test.md"],
            "reviewer": "reviewer",
        }

    @staticmethod
    def conflict(address: str, disposition: str, correction: dict | None) -> dict:
        return {
            "schemaVersion": "onslaught-ghidra-full-reaudit-conflict-review.v1",
            "address": address,
            "conflictClass": "narrative-only",
            "variantCount": 2,
            "recoveredVerdicts": ["PASS_STATIC_OK_REBUILD_THIN"],
            "disposition": disposition,
            "evidence": ["final-instructions", "recovered-conflict"],
            "rationale": "Conflict rationale.",
            "correction": correction,
            "docFindings": [
                "reverse-engineering/binary-analysis/functions/Test.md should be reconciled."
            ],
            "reviewer": "conflict-reviewer",
        }

    def test_builds_only_correction_records_and_maps_all_fields(self) -> None:
        paths = [
            self.ledger(
                "research.jsonl",
                [
                    self.research("0x00500000", "accepted", None),
                    self.research(
                        "0x00500010",
                        "correction-required",
                        {"proposedComment": "Correct research comment."},
                    ),
                ],
            ),
            self.ledger(
                "critical.jsonl",
                [
                    self.critical(
                        "0x00400000",
                        "correction-required",
                        {
                            "proposedName": "CorrectName",
                            "proposedSignature": "void CorrectName(void)",
                            "proposedComment": "Correct critical comment.",
                        },
                    )
                ],
            ),
        ]

        metadata = manifest.load_metadata(
            self.metadata(
                [
                    {
                        "address": "0x00400000",
                        "name": "CriticalName",
                        "signature": "void CriticalName(void)",
                        "prototype_key": "cc=default|params=0",
                    },
                    {
                        "address": "0x00500010",
                        "name": "ResearchName",
                        "signature": "void ResearchName(void)",
                        "prototype_key": "cc=default|params=0",
                    },
                ]
            )
        )

        payload = manifest.build_manifest(
            manifest.load_ledgers(paths), "campaign", metadata=metadata
        )

        self.assertEqual(payload["recordCount"], 2)
        self.assertFalse(payload["prototypeOrBoundaryMutationAuthorized"])
        records = payload["records"]
        self.assertEqual([row["address"] for row in records], ["0x00400000", "0x00500010"])
        critical = records[0]
        self.assertEqual(critical["phase"], "runtime-critical")
        self.assertEqual(critical["correctedName"], "CorrectName")
        self.assertEqual(critical["correctedSignature"], "void CorrectName(void)")
        self.assertEqual(critical["correctedComment"], "Correct critical comment.")
        self.assertEqual(critical["correctedFields"], ["name", "signature", "comment"])
        self.assertEqual(critical["currentSignature"], "void CriticalName(void)")
        self.assertEqual(
            critical["signatureChangeClass"], "name-and-parameter-rendering-only"
        )
        self.assertEqual(critical["sourceAlignment"], "direct")
        research = records[1]
        self.assertEqual(research["phase"], "research-findings")
        self.assertEqual(research["correctedName"], "ResearchName")
        self.assertEqual(research["recoveryEvidence"], "exact-row")

    def test_rejects_duplicate_addresses_across_ledgers(self) -> None:
        row = self.research(
            "0x00500010", "correction-required", {"proposedComment": "Correct."}
        )
        ledgers = manifest.load_ledgers(
            [self.ledger("a.jsonl", [row]), self.ledger("b.jsonl", [row])]
        )

        with self.assertRaisesRegex(ValueError, "duplicate address"):
            manifest.build_manifest(ledgers, "campaign")

    def test_rejects_correction_without_proposed_field(self) -> None:
        path = self.ledger(
            "bad.jsonl",
            [self.critical("0x00400000", "correction-required", {})],
        )

        with self.assertRaisesRegex(ValueError, "no proposed field"):
            manifest.build_manifest(manifest.load_ledgers([path]), "campaign")

    def test_rejects_absolute_doc_findings(self) -> None:
        row = self.critical(
            "0x00400000", "correction-required", {"proposedName": "CorrectName"}
        )
        row["docFindings"] = ["C:/private/path.md"]
        path = self.ledger("bad-path.jsonl", [row])

        with self.assertRaisesRegex(ValueError, "absolute path"):
            manifest.build_manifest(manifest.load_ledgers([path]), "campaign")

    def test_adds_uncovered_conflict_correction_and_records_covered_overlap(self) -> None:
        ledgers = manifest.load_ledgers(
            [
                self.ledger(
                    "conflicts.jsonl",
                    [
                        self.conflict(
                            "0x00401000",
                            "correction-required",
                            {"proposedComment": "Uncovered correction."},
                        ),
                        self.conflict(
                            "0x00401010",
                            "correction-required",
                            {"proposedComment": "Already covered."},
                        ),
                    ],
                )
            ]
        )
        metadata = manifest.load_metadata(
            self.metadata(
                [
                    {
                        "address": "0x00401000",
                        "name": "ConflictA",
                        "signature": "void ConflictA(void)",
                        "prototype_key": "cc=default|params=0",
                    },
                    {
                        "address": "0x00401010",
                        "name": "ConflictB",
                        "signature": "void ConflictB(void)",
                        "prototype_key": "cc=default|params=0",
                    },
                ]
            )
        )
        covered = manifest.load_covered_manifest(
            self.covered_manifest(
                [
                    {
                        "address": "0x00401010",
                        "correctedFields": ["comment"],
                        "correctedName": "ConflictB",
                        "correctedComment": "Already covered.",
                    }
                ]
            )
        )

        payload = manifest.build_manifest(
            ledgers, "campaign", metadata=metadata, covered=covered
        )

        self.assertEqual(payload["reviewedAddressCount"], 2)
        self.assertEqual(payload["recordCount"], 1)
        self.assertEqual(payload["coveredByCursorDeltaCount"], 1)
        self.assertEqual(payload["coveredByCursorDeltaAddresses"], ["0x00401010"])
        record = payload["records"][0]
        self.assertEqual(record["phase"], "recovered-conflicts")
        self.assertEqual(record["currentName"], "ConflictA")
        self.assertEqual(
            record["docFindings"],
            ["reverse-engineering/binary-analysis/functions/Test.md"],
        )

    def test_nonidentical_cursor_overlap_is_emitted_as_superseding_record(self) -> None:
        row = self.conflict(
            "0x00401020",
            "correction-required",
            {"proposedComment": "More exact conflict correction."},
        )
        ledgers = manifest.load_ledgers([self.ledger("conflict.jsonl", [row])])
        metadata = manifest.load_metadata(
            self.metadata(
                [
                    {
                        "address": "0x00401020",
                        "name": "ConflictC",
                        "signature": "void ConflictC(void)",
                        "prototype_key": "cc=default|params=0",
                    }
                ]
            )
        )
        covered = manifest.load_covered_manifest(
            self.covered_manifest(
                [
                    {
                        "address": "0x00401020",
                        "correctedFields": ["comment"],
                        "correctedName": "ConflictC",
                        "correctedComment": "Less exact Cursor correction.",
                    }
                ]
            )
        )

        payload = manifest.build_manifest(
            ledgers, "campaign", metadata=metadata, covered=covered
        )

        self.assertEqual(payload["recordCount"], 1)
        self.assertEqual(payload["coveredByCursorDeltaCount"], 0)
        self.assertEqual(payload["supersedingCursorDeltaOverlapCount"], 1)
        self.assertEqual(
            payload["supersedingCursorDeltaOverlapAddresses"], ["0x00401020"]
        )
        self.assertTrue(payload["records"][0]["supersedesCursorDeltaRecord"])

    def test_classifies_actual_prototype_change(self) -> None:
        path = self.ledger(
            "critical.jsonl",
            [
                self.critical(
                    "0x00402000",
                    "correction-required",
                    {
                        "proposedSignature": "bool Load(void * this, int mode, int flags)",
                        "proposedComment": "Correct prototype.",
                    },
                )
            ],
        )
        metadata = manifest.load_metadata(
            self.metadata(
                [
                    {
                        "address": "0x00402000",
                        "name": "CriticalName",
                        "signature": "bool Load(void * this)",
                        "prototype_key": "cc=thiscall|params=1",
                    }
                ]
            )
        )

        payload = manifest.build_manifest(
            manifest.load_ledgers([path]), "campaign", metadata=metadata
        )

        self.assertEqual(
            payload["records"][0]["signatureChangeClass"],
            "structured-prototype-change",
        )

    def test_rejects_absolute_path_in_public_text_fields(self) -> None:
        row = self.critical(
            "0x00403000", "correction-required", {"proposedComment": "Correct."}
        )
        row["rationale"] = "See C:\\private\\evidence.txt"
        path = self.ledger("private-path.jsonl", [row])

        with self.assertRaisesRegex(ValueError, "absolute path"):
            manifest.build_manifest(manifest.load_ledgers([path]), "campaign")


if __name__ == "__main__":
    unittest.main()
