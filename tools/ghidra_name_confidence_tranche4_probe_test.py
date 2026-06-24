#!/usr/bin/env python3
"""Tests for the fourth Ghidra name-confidence tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_tranche4_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name"
    "\tmnemonic\toperands\tbytes\tflow_type\n"
)


class GhidraNameConfidenceTranche4ProbeTests(unittest.TestCase):
    def test_classifies_clean_saved_wrapper_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile = root / "decompile"
            decompile.mkdir()
            (root / "metadata.tsv").write_text(
                METADATA_HEADER
                + "0x00403ff0\tCFastVB_Unk_0055db0a__Wrapper_00403ff0\tvoid __fastcall CFastVB_Unk_0055db0a__Wrapper_00403ff0(int param_1)\tArray-destroy wrapper. Proof-boundary comment only: destructor/unwind context, not render-path proof.\tOK\n"
                + "0x00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\tvoid __fastcall CEngine_Unk_00506010__Wrapper_00411b90(void * param_1)\tBurst-dispatch list wrapper. Proof-boundary comment only: CEngine/_Unk wrapper name remains provisional and does not prove CWeapon::Fire/CBattleEngine::WeaponFired or stealth reset.\tOK\n",
                encoding="utf-8",
            )
            (decompile / "index.tsv").write_text(
                INDEX_HEADER
                + "0x00403ff0\tCFastVB_Unk_0055db0a__Wrapper_00403ff0\tvoid __fastcall CFastVB_Unk_0055db0a__Wrapper_00403ff0(int param_1)\tOK\n"
                + "0x00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\tvoid __fastcall CEngine_Unk_00506010__Wrapper_00411b90(void * param_1)\tOK\n",
                encoding="utf-8",
            )
            (decompile / "00403ff0_CFastVB_Unk_0055db0a__Wrapper_00403ff0.c").write_text(
                "CDXLandscape__DestroyArrayWithCallback(param_1 + 8,0x41c,1,CResourceDescriptor__dtor);",
                encoding="utf-8",
            )
            (decompile / "00411b90_CEngine_Unk_00506010__Wrapper_00411b90.c").write_text(
                "*(undefined4 *)(*(int *)((int)param_1 + 0x18) + 0x588) = 0; "
                "if (*(int *)((int)pvVar3 + 0x9c) != 0) { "
                "CGeneralVolume__SpawnBurstFromPresetWithFallback(pvVar3); }",
                encoding="utf-8",
            )
            (root / "xrefs.tsv").write_text(
                XREF_HEADER
                + "00403ff0\tCFastVB_Unk_0055db0a__Wrapper_00403ff0\t005d0fb6\t005d0fb0\tUnwind@005d0fb0\tUNCONDITIONAL_CALL\n"
                + "00403ff0\tCFastVB_Unk_0055db0a__Wrapper_00403ff0\t00515f30\t<none>\t<no_function>\tDATA\n"
                + "00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\t00409f6a\t00409f20\tCGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (root / "instructions.tsv").write_text(
                INSTRUCTION_HEADER
                + "0x00403ff0\t0x00403ff0\tAFTER\t5\t0x00404000\t0x00403ff0\tCFastVB_Unk_0055db0a__Wrapper_00403ff0\tCALL\t0x0055db0a\te8 05 9b 15 00\tUNCONDITIONAL_CALL\n"
                + "0x00411b90\t0x00411b90\tAFTER\t18\t0x00411bbe\t0x00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\tMOV\tEAX, dword ptr [EAX + 0x4]\t8b 40 04\tFALL_THROUGH\n",
                encoding="utf-8",
            )

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=decompile / "index.tsv",
                decompile_dir=decompile,
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        by_addr = {item["address"]: item for item in report["targets"]}
        self.assertEqual(by_addr["0x00403ff0"]["classification"], "resource-descriptor-array-destroy-wrapper")
        self.assertEqual(by_addr["0x00411b90"]["classification"], "general-volume-burst-list-dispatch-owner-correction")
        self.assertEqual(report["actionCounts"]["renameCandidate"], 1)
        self.assertEqual(report["actionCounts"]["ownerCorrectionCandidate"], 1)

    def test_fails_when_proof_boundary_comment_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile = root / "decompile"
            decompile.mkdir()
            (root / "metadata.tsv").write_text(
                METADATA_HEADER
                + "0x00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\tvoid __fastcall CEngine_Unk_00506010__Wrapper_00411b90(void * param_1)\tBurst dispatch fully proves stealth reset behavior.\tOK\n",
                encoding="utf-8",
            )
            (decompile / "index.tsv").write_text(
                INDEX_HEADER
                + "0x00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\tvoid __fastcall CEngine_Unk_00506010__Wrapper_00411b90(void * param_1)\tOK\n",
                encoding="utf-8",
            )
            (decompile / "00411b90_CEngine_Unk_00506010__Wrapper_00411b90.c").write_text(
                "CGeneralVolume__SpawnBurstFromPresetWithFallback(pvVar3); 0x588; 0x9c;",
                encoding="utf-8",
            )
            (root / "xrefs.tsv").write_text(
                XREF_HEADER
                + "00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\t00409f6a\t00409f20\tCGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (root / "instructions.tsv").write_text(INSTRUCTION_HEADER, encoding="utf-8")

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=decompile / "index.tsv",
                decompile_dir=decompile,
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("proof-boundary" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
