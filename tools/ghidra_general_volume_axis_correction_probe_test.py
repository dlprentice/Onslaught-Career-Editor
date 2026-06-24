#!/usr/bin/env python3
"""Tests for the GeneralVolume axis correction probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_general_volume_axis_correction_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_minimal_readback(root: Path, *, stale_pitch_name: bool = False) -> None:
    decompile = root / "decompile"
    decompile.mkdir()

    metadata_rows: list[str] = []
    index_rows: list[str] = []
    xref_rows: list[str] = []
    instruction_rows: list[str] = []

    for address, rule in probe.RULES.items():
        name = rule["newName"]
        if stale_pitch_name and address == "0x004136e0":
            name = rule["oldName"]
        signature = f"void __thiscall {name}(void * this, int param_1, float param_2)"
        comment = "Corrected from stale axis/owner boundary. Proof-boundary: exact source identity and runtime behavior remain provisional."
        metadata_rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{name}\t{signature}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(" ".join(rule["tokens"]), encoding="utf-8")
        xref_rows.append(
            f"{address[2:]}\t{name}\t{rule['fromAddr'][2:]}\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
        )
        instruction_rows.append(
            f"{address}\t{rule['fromAddr']}\tTARGET\t0\t{rule['fromAddr']}\t<none>\t<no_function>\tCALL\t{address}\t\tUNCONDITIONAL_CALL\n"
        )

    (root / "metadata.tsv").write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    (root / "xrefs.tsv").write_text(XREF_HEADER + "".join(xref_rows), encoding="utf-8")
    (root / "instructions.tsv").write_text(INSTRUCTION_HEADER + "".join(instruction_rows), encoding="utf-8")


class GhidraGeneralVolumeAxisCorrectionProbeTests(unittest.TestCase):
    def test_accepts_axis_and_owner_corrections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_readback(root)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "decompile" / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["correctedFunctionCount"], 2)
        self.assertEqual(report["axisFields"]["0x00413660"], "+0x278")
        self.assertEqual(report["axisFields"]["0x004136e0"], "+0x280")

    def test_fails_when_stale_pitch_name_survives(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_readback(root, stale_pitch_name=True)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "decompile" / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x004136e0" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
