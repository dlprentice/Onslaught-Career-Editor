#!/usr/bin/env python3
"""Tests for the sixth Ghidra name-confidence correction probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_tranche6_correction_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


def write_minimal_readback(root: Path, *, bad_comment: bool = False) -> None:
    decompile = root / "decompile"
    decompile.mkdir()
    metadata_rows = []
    index_rows = []
    xref_rows = []
    for address, rule in probe.RULES.items():
        comment = "Proof-boundary: exact source identity, signature, tags, and runtime behavior remain unproven."
        if address == "0x00411bf0":
            comment += " This does not prove weapon-fired stealth reset."
        else:
            comment += " signature/types remain unproven."
        if bad_comment and address == "0x00411bf0":
            comment = "This proves weapon-fired stealth reset."
        metadata_rows.append(
            f"{address}\t{rule['newName']}\tvoid __fastcall {rule['newName']}(void * param_1)\t{comment}\tOK\n"
        )
        index_rows.append(
            f"{address}\t{rule['newName']}\tvoid __fastcall {rule['newName']}(void * param_1)\tOK\n"
        )
        (decompile / f"{address[2:]}_{rule['newName']}.c").write_text(
            " ".join(rule["tokens"]),
            encoding="utf-8",
        )
        xref_rows.append(
            f"{address[2:]}\t{rule['newName']}\t00400000\t00400000\t{rule['expectedXrefFunctions'][0]}\tUNCONDITIONAL_CALL\n"
        )

    (root / "metadata.tsv").write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    (root / "xrefs.tsv").write_text(XREF_HEADER + "".join(xref_rows), encoding="utf-8")
    (root / "queue.json").write_text(
        json.dumps(
            {
                "status": "PASS",
                "totalFunctions": 5863,
                "qualitySignals": {
                    "commentlessFunctionCount": 5495,
                    "undefinedSignatureCount": 2087,
                    "paramSignatureCount": 2563,
                    "uncertainOwnerNameCount": 4,
                    "helperAddressNameCount": 0,
                    "wrapperAddressNameCount": 5,
                },
                "priorityQueues": {
                    "nameConfidence": [
                        {"address": address, "name": f"Deferred_{address}"}
                        for address in sorted(probe.REMAINING_NAME_CONFIDENCE_ADDRESSES)
                    ]
                },
            }
        ),
        encoding="utf-8",
    )


class GhidraNameConfidenceTranche6CorrectionProbeTests(unittest.TestCase):
    def test_accepts_saved_correction_readback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_readback(root)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "decompile" / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                queue_path=root / "queue.json",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 3)
        self.assertEqual(report["queue"]["qualitySignals"]["uncertainOwnerNameCount"], 4)
        self.assertEqual(report["queue"]["qualitySignals"]["wrapperAddressNameCount"], 5)

    def test_fails_when_comment_overclaims_runtime_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_readback(root, bad_comment=True)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "decompile" / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                queue_path=root / "queue.json",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x00411bf0" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
