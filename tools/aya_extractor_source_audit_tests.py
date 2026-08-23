#!/usr/bin/env python3
"""Focused tests for the deterministic AYA extractor source audit."""
from __future__ import annotations

import csv
from pathlib import Path
import subprocess
import tempfile
import unittest

import aya_extractor_source_audit as audit


class AyaExtractorSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.contract = (
            cls.repo_root
            / "reverse-engineering"
            / "source-code"
            / "aya-resource-extractor-contract.tsv"
        )

    def test_complete_inventory_function_and_claim_denominators(self) -> None:
        report = audit.build_report(self.repo_root, self.contract)
        self.assertEqual(audit.SCHEMA, report["schemaVersion"])
        self.assertEqual(audit.EXTRACTOR_PIN, report["extractorPin"])
        self.assertEqual(audit.UPSTREAM_PIN, report["upstreamPin"])
        self.assertEqual(audit.ONSLAUGHT_PIN, report["onslaughtComparison"]["pin"])
        format_hits = report["onslaughtComparison"]["formatTokenHits"]
        self.assertEqual(29, report["onslaughtComparison"]["formatTokenCount"])
        self.assertEqual(29, len(format_hits))
        self.assertIn("CCUS", format_hits)
        self.assertIn("CAMD", format_hits)
        self.assertTrue(all(not hits for hits in format_hits.values()))
        thematic = report["onslaughtComparison"]["thematicTokenHits"]
        self.assertTrue(thematic["CChunkReader"])
        self.assertTrue(thematic["D3DPT_TRIANGLESTRIP"])
        self.assertFalse(thematic["meshtex%"])
        self.assertFalse(thematic["dxtntextures"])
        self.assertEqual(73, report["trackedFileCount"])
        self.assertEqual(40, report["firstPartyRoutineDenominator"]["count"])
        self.assertEqual(92, report["contract"]["rowCount"])
        self.assertEqual(0, report["contract"]["unclassifiedRows"])
        self.assertEqual(
            {
                "CONTRADICTED": 2,
                "CURRENTLY_CORROBORATED": 23,
                "CURRENT_TOOL_STRONGER": 39,
                "EXPORT_CONVENTION_ONLY": 19,
                "EXTRACTOR_ONLY": 3,
                "UNKNOWN": 6,
            },
            report["contract"]["classificationCounts"],
        )
        inventory = report["inventory"]
        self.assertEqual((9, 1181), (inventory["firstPartyHandwrittenCSharp"]["fileCount"], inventory["firstPartyHandwrittenCSharp"]["physicalLines"]))
        self.assertEqual((2, 287), (inventory["firstPartyGeneratedCSharp"]["fileCount"], inventory["firstPartyGeneratedCSharp"]["physicalLines"]))
        self.assertEqual((2, 97), (inventory["firstPartyNativeGlue"]["fileCount"], inventory["firstPartyNativeGlue"]["physicalLines"]))
        self.assertEqual((28, 23581), (inventory["thirdPartyZlib"]["fileCount"], inventory["thirdPartyZlib"]["physicalLines"]))
        self.assertEqual((2, 739), (inventory["thirdPartyDdsReaderFreeImage"]["fileCount"], inventory["thirdPartyDdsReaderFreeImage"]["physicalLines"]))
        self.assertEqual((14, 1854), (inventory["thirdPartyFbxHamishMilne"]["fileCount"], inventory["thirdPartyFbxHamishMilne"]["physicalLines"]))

    def test_render_is_byte_deterministic(self) -> None:
        first = audit.render_report(audit.build_report(self.repo_root, self.contract))
        second = audit.render_report(audit.build_report(self.repo_root, self.contract))
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))

    def test_inventory_render_ignores_clean_lf_and_crlf_materializations(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        extractor = Path(temporary.name) / "extractor"
        extractor.mkdir()
        relative = "Code/AyaResourceExtractor/AyaFileUncompressor.cs"
        source = extractor / relative
        source.parent.mkdir(parents=True)
        (extractor / ".gitattributes").write_bytes(b"* text=auto\n")
        source.write_bytes(
            b"class Fixture\n{\n    public void Uncompress()\n    {\n    }\n}\n"
        )

        def git(*args: str) -> str:
            completed = subprocess.run(
                ["git", "-C", str(extractor), *args],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            )
            return completed.stdout.strip()

        git("init")
        git("add", ".gitattributes", relative)
        git("-c", "user.name=AYA audit test", "-c", "user.email=aya-audit@example.invalid", "commit", "-m", "fixture")
        expected_blob = git("rev-parse", f"HEAD:{relative}")

        def materialize(eol: str) -> tuple[bytes, dict[str, object], bytes]:
            git("config", "core.autocrlf", "false")
            git("config", "core.eol", eol)
            source.unlink()
            git("checkout", "--", relative)
            self.assertEqual("", git("status", "--porcelain"))
            inventory = audit._inventory_file(extractor, relative)
            rendered = audit.render_report(
                {
                    "inventory": inventory,
                    "routines": audit._scan_functions(extractor, relative),
                }
            )
            return source.read_bytes(), inventory, rendered

        lf_bytes, lf_inventory, lf_rendered = materialize("lf")
        crlf_bytes, crlf_inventory, crlf_rendered = materialize("crlf")
        self.assertNotIn(b"\r\n", lf_bytes)
        self.assertIn(b"\r\n", crlf_bytes)
        self.assertEqual(lf_rendered, crlf_rendered)
        self.assertEqual(expected_blob, lf_inventory["gitBlobSha1"])
        self.assertEqual(expected_blob, crlf_inventory["gitBlobSha1"])

    def _mutated_contract(self, mutate) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        destination = Path(temporary.name) / "contract.tsv"
        with self.contract.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            fieldnames = list(reader.fieldnames or ())
            rows = list(reader)
        mutate(rows)
        with destination.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        return destination

    def test_blank_classification_is_rejected(self) -> None:
        contract = self._mutated_contract(lambda rows: rows[0].__setitem__("classification", ""))
        with self.assertRaisesRegex(audit.AuditError, "blank contract field"):
            audit.build_report(self.repo_root, contract)

    def test_missing_claim_is_rejected(self) -> None:
        contract = self._mutated_contract(lambda rows: rows.pop())
        with self.assertRaisesRegex(audit.AuditError, "contract denominator drift"):
            audit.build_report(self.repo_root, contract)

    def test_out_of_range_reference_is_rejected(self) -> None:
        contract = self._mutated_contract(
            lambda rows: rows[0].__setitem__(
                "current_evidence", "reverse-engineering/asset-formats/aya-container.md:L99999"
            )
        )
        with self.assertRaisesRegex(audit.AuditError, "out-of-range line reference"):
            audit.build_report(self.repo_root, contract)


if __name__ == "__main__":
    unittest.main(verbosity=2)
