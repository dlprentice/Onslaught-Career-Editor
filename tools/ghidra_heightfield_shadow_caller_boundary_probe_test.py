#!/usr/bin/env python3
"""Tests for the heightfield-shadow caller-boundary Ghidra recovery probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_heightfield_shadow_caller_boundary_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)
POINTER_TABLE_HEADER = "slot\tentry_addr\tptr\tptr_name\tptr_signature\n"
CREATE_HEADER = "address\tstatus\tname\tsignature\tnote\n"


def write_fixture(root: Path, *, missing_boundary_name: bool = False) -> None:
    target_decompile = root / "target_decompile"
    caller_decompile = root / "caller_decompile"
    target_decompile.mkdir()
    caller_decompile.mkdir()

    caller_name = probe.CALLER_NAME
    if missing_boundary_name:
        caller_name = "FUN_00447120"

    target_sig = f"int __fastcall {probe.TARGET_NAME}(void * param_1)"
    caller_sig = f"void __fastcall {caller_name}(void * param_1)"
    target_comment = (
        "Shadow/heightfield corner test. Samples eight bounds corners with "
        "CStaticShadows__SampleShadowHeightBilinear. Proof-boundary: owner/signature and runtime "
        "shadow behavior remain provisional."
    )
    caller_comment = (
        "Recovered virtual-table caller boundary. Referenced from data table slot 0x005e1ee0; "
        "calls ShadowHeightfield__AnyBoundsCornerAboveSampledHeight. Proof-boundary: table owner, "
        "signature, source identity, and runtime behavior remain provisional."
    )

    (root / "metadata.tsv").write_text(
        METADATA_HEADER
        + f"{probe.TARGET_ADDRESS}\t{probe.TARGET_NAME}\t{target_sig}\t{target_comment}\tOK\n"
        + f"{probe.CALLER_ADDRESS}\t{caller_name}\t{caller_sig}\t{caller_comment}\tOK\n",
        encoding="utf-8",
    )
    (target_decompile / "index.tsv").write_text(
        INDEX_HEADER + f"{probe.TARGET_ADDRESS}\t{probe.TARGET_NAME}\t{target_sig}\tOK\n",
        encoding="utf-8",
    )
    (target_decompile / f"{probe.TARGET_ADDRESS[2:]}_{probe.TARGET_NAME}.c").write_text(
        " ".join([probe.TARGET_NAME, "CStaticShadows__SampleShadowHeightBilinear", "DAT_006fbdfc", "return 1", "return 0"]),
        encoding="utf-8",
    )
    (caller_decompile / "index.tsv").write_text(
        INDEX_HEADER + f"{probe.CALLER_ADDRESS}\t{caller_name}\t{caller_sig}\tOK\n",
        encoding="utf-8",
    )
    (caller_decompile / f"{probe.CALLER_ADDRESS[2:]}_{caller_name}.c").write_text(
        " ".join([caller_name, probe.TARGET_NAME, "0x0047eb80", "0x0050ff10", "0x424"]),
        encoding="utf-8",
    )
    (root / "target_xrefs.tsv").write_text(
        XREF_HEADER
        + f"{probe.TARGET_ADDRESS[2:]}\t{probe.TARGET_NAME}\t004478a3\t{probe.CALLER_ADDRESS[2:]}\t{caller_name}\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    (root / "caller_xrefs.tsv").write_text(
        XREF_HEADER
        + f"{probe.CALLER_ADDRESS[2:]}\t{caller_name}\t005e1ee0\t<none>\t<no_function>\tDATA\n",
        encoding="utf-8",
    )
    (root / "caller_instructions.tsv").write_text(
        INSTRUCTION_HEADER
        + f"{probe.CALLER_ADDRESS}\t{probe.CALLER_ADDRESS}\tTARGET\t0\t{probe.CALLER_ADDRESS}\t{probe.CALLER_ADDRESS}\t{caller_name}\tSUB\tESP, 0x424\t81 ec 24 04 00 00\tFALL_THROUGH\n"
        + f"{probe.CALLER_ADDRESS}\t{probe.CALLER_ADDRESS}\tAFTER\t1\t0x004478a3\t{probe.CALLER_ADDRESS}\t{caller_name}\tCALL\t{probe.TARGET_ADDRESS}\te8 28 b5 fb ff\tUNCONDITIONAL_CALL\n"
        + f"{probe.CALLER_ADDRESS}\t{probe.CALLER_ADDRESS}\tAFTER\t2\t0x00447a38\t{probe.CALLER_ADDRESS}\t{caller_name}\tRET\t\tc3\tTERMINATOR\n",
        encoding="utf-8",
    )
    (root / "pointer_table.tsv").write_text(
        POINTER_TABLE_HEADER
        + f"28\t005e1ee0\t{probe.CALLER_ADDRESS[2:]}\t{caller_name}\t{caller_sig}\n",
        encoding="utf-8",
    )
    (root / "create_apply.tsv").write_text(
        CREATE_HEADER
        + f"{probe.CALLER_ADDRESS[2:]}\tcreated\t{caller_name}\t{caller_sig}\tdisassemble+create succeeded; renamed\n",
        encoding="utf-8",
    )


class GhidraHeightfieldShadowCallerBoundaryProbeTests(unittest.TestCase):
    def test_accepts_recovered_boundary_and_shadow_helper_rename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                target_decompile_index_path=root / "target_decompile" / "index.tsv",
                target_decompile_dir=root / "target_decompile",
                caller_decompile_index_path=root / "caller_decompile" / "index.tsv",
                caller_decompile_dir=root / "caller_decompile",
                target_xrefs_path=root / "target_xrefs.tsv",
                caller_xrefs_path=root / "caller_xrefs.tsv",
                caller_instructions_path=root / "caller_instructions.tsv",
                pointer_table_path=root / "pointer_table.tsv",
                create_apply_path=root / "create_apply.tsv",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["callerName"], probe.CALLER_NAME)
        self.assertEqual(report["targetName"], probe.TARGET_NAME)
        self.assertEqual(report["targetCallerFunction"], probe.CALLER_NAME)

    def test_fails_when_boundary_keeps_generic_function_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, missing_boundary_name=True)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                target_decompile_index_path=root / "target_decompile" / "index.tsv",
                target_decompile_dir=root / "target_decompile",
                caller_decompile_index_path=root / "caller_decompile" / "index.tsv",
                caller_decompile_dir=root / "caller_decompile",
                target_xrefs_path=root / "target_xrefs.tsv",
                caller_xrefs_path=root / "caller_xrefs.tsv",
                caller_instructions_path=root / "caller_instructions.tsv",
                pointer_table_path=root / "pointer_table.tsv",
                create_apply_path=root / "create_apply.tsv",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(probe.CALLER_ADDRESS in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
