#!/usr/bin/env python3
"""Tests for the sixth Ghidra name-confidence tranche classifier."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_tranche6_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTIONS_HEADER = "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"


def write_minimal_exports(root: Path, *, omit_token: bool = False) -> None:
    decompile = root / "decompile"
    caller_decompile = root / "caller_decompile"
    decompile.mkdir()
    caller_decompile.mkdir()
    metadata_rows = []
    index_rows = []
    xref_rows = []
    instruction_rows = []
    for address, rule in probe.RULES.items():
        metadata_rows.append(
            f"{address}\t{rule['currentName']}\tvoid __fastcall {rule['currentName']}(void * param_1)\tProof-boundary comment only: owner, source identity, and runtime behavior remain provisional.\tOK\n"
        )
        index_rows.append(
            f"{address}\t{rule['currentName']}\tvoid __fastcall {rule['currentName']}(void * param_1)\tOK\n"
        )
        token_text = " ".join(rule["tokens"])
        if omit_token and address == "0x00412240":
            token_text = token_text.replace(rule["tokens"][0], "")
        (decompile / f"{address[2:]}_{rule['currentName']}.c").write_text(token_text, encoding="utf-8")
        xref_function = rule.get("expectedXrefFunction", "<no_function>")
        ref_type = rule.get("expectedRefType", "UNCONDITIONAL_CALL")
        xref_rows.append(
            f"{address[2:]}\t{rule['currentName']}\t00400000\t00400000\t{xref_function}\t{ref_type}\n"
        )
        instruction_rows.append(
            f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{rule['currentName']}\tCALL\t0x00400000\t00\tUNCONDITIONAL_CALL\n"
        )

    (root / "metadata.tsv").write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    (root / "xrefs.tsv").write_text(XREF_HEADER + "".join(xref_rows), encoding="utf-8")
    (root / "instructions.tsv").write_text(INSTRUCTIONS_HEADER + "".join(instruction_rows), encoding="utf-8")
    (root / "xref_context_instructions.tsv").write_text(INSTRUCTIONS_HEADER, encoding="utf-8")
    (caller_decompile / "index.tsv").write_text(INDEX_HEADER, encoding="utf-8")


class GhidraNameConfidenceTranche6ProbeTests(unittest.TestCase):
    def test_classifies_expected_remaining_queue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_exports(root)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "decompile" / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
                caller_index_path=root / "caller_decompile" / "index.tsv",
                xref_context_instructions_path=root / "xref_context_instructions.tsv",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 8)
        self.assertEqual(report["actionCounts"]["renameCandidate"], 2)
        self.assertEqual(report["actionCounts"]["ownerCorrectionCandidate"], 1)
        self.assertEqual(report["actionCounts"]["deferRawCallerBoundary"], 3)
        self.assertEqual(report["actionCounts"]["deferOwnerIdentity"], 1)
        self.assertEqual(report["actionCounts"]["deferTableOwner"], 1)

    def test_fails_when_expected_decompile_token_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_exports(root, omit_token=True)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "decompile" / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
                caller_index_path=root / "caller_decompile" / "index.tsv",
                xref_context_instructions_path=root / "xref_context_instructions.tsv",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x00412240" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
