#!/usr/bin/env python3
"""Tests for the third Ghidra name-confidence tranche probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_tranche3_probe as probe


INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name"
    "\tmnemonic\toperands\tbytes\tflow_type\n"
)


class GhidraNameConfidenceTranche3ProbeTests(unittest.TestCase):
    def test_classifies_world_and_ctype_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile = root / "decompile"
            decompile.mkdir()
            seeds = [
                {"address": "0x0050b010", "name": "CWorld__DispatchHelper_004bc480"},
                {"address": "0x0050b020", "name": "CWorld__DispatchHelper_004bc3e0"},
                {"address": "0x0056d21c", "name": "CRT__IsDigit_Wrapper_0056d21c"},
            ]
            (root / "seed_names.json").write_text(json.dumps(seeds), encoding="utf-8")
            (decompile / "index.tsv").write_text(
                INDEX_HEADER
                + "0x0050b010\tCWorld__DispatchHelper_004bc480\tvoid __stdcall CWorld__DispatchHelper_004bc480(void * param_1)\tOK\n"
                + "0x0050b020\tCWorld__DispatchHelper_004bc3e0\tvoid __stdcall CWorld__DispatchHelper_004bc3e0(void * param_1)\tOK\n"
                + "0x0056d21c\tCRT__IsDigit_Wrapper_0056d21c\tvoid __cdecl CRT__IsDigit_Wrapper_0056d21c(int param_1)\tOK\n",
                encoding="utf-8",
            )
            (decompile / "0050b010_CWorld__DispatchHelper_004bc480.c").write_text(
                "CWorld__AddUnitToOccupancyGridAndRebuildShadows(param_1);",
                encoding="utf-8",
            )
            (decompile / "0050b020_CWorld__DispatchHelper_004bc3e0.c").write_text(
                "CWorld__RemoveUnitFromOccupancyGrid(param_1);",
                encoding="utf-8",
            )
            (decompile / "0056d21c_CRT__IsDigit_Wrapper_0056d21c.c").write_text(
                "CRT__IsCharTypeMaskOrLeadByte_0056d22d(param_1,0,4);",
                encoding="utf-8",
            )
            (root / "xrefs.tsv").write_text(
                XREF_HEADER
                + "0050b010\tCWorld__DispatchHelper_004bc480\t00447ade\t00447ac0\tCUnitAI__PlayWingFoldedAnimationAndSetState3\tUNCONDITIONAL_CALL\n"
                + "0050b010\tCWorld__DispatchHelper_004bc480\t0044cb44\t0044ca30\tCFeature__VFunc_09_0044ca30\tUNCONDITIONAL_CALL\n"
                + "0050b010\tCWorld__DispatchHelper_004bc480\t0050494c\t005047e0\tCWarspiteDome__Init\tUNCONDITIONAL_CALL\n"
                + "0050b010\tCWorld__DispatchHelper_004bc480\t004bbd94\t004bbcd0\tCNamedMesh__VFunc_09_004bbcd0\tUNCONDITIONAL_CALL\n"
                + "0050b010\tCWorld__DispatchHelper_004bc480\t0041b32c\t0041b1a0\tCCannon__Init\tUNCONDITIONAL_CALL\n"
                + "0050b010\tCWorld__DispatchHelper_004bc480\t004dfa94\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
                + "0050b020\tCWorld__DispatchHelper_004bc3e0\t0041b459\t0041b450\tCCannon__Destructor\tUNCONDITIONAL_CALL\n"
                + "0050b020\tCWorld__DispatchHelper_004bc3e0\t004bc059\t004bc050\tCNamedMesh__VFunc_02_004bc050\tUNCONDITIONAL_CALL\n"
                + "0050b020\tCWorld__DispatchHelper_004bc3e0\t00447109\t00447100\tCDropship__VFunc_02_00447100\tUNCONDITIONAL_CALL\n"
                + "0050b020\tCWorld__DispatchHelper_004bc3e0\t00447b47\t00447b10\tCUnitAI__PlayWingUnfoldedAnimationAndSetState5\tUNCONDITIONAL_CALL\n"
                + "0050b020\tCWorld__DispatchHelper_004bc3e0\t0044cbf4\t0044cbe0\tCFeature__VFunc_02_0044cbe0\tUNCONDITIONAL_CALL\n"
                + "0050b020\tCWorld__DispatchHelper_004bc3e0\t0047e701\t0047e6e0\tCHazard__VFunc_02_0047e6e0\tUNCONDITIONAL_CALL\n"
                + "0056d21c\tCRT__IsDigit_Wrapper_0056d21c\t00568df1\t00568dc6\tCRT__ParseCommandLineToken\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (root / "instructions.tsv").write_text(
                INSTRUCTION_HEADER
                + "0x0056d21c\t0x0056d21c\tAFTER\t3\t0x0056d224\t0x0056d21c\tCRT__IsDigit_Wrapper_0056d21c\tCALL\t0x0056d22d\te8 04 00 00 00\tUNCONDITIONAL_CALL\n"
                + "0x0056d21c\t0x0056d21c\tAFTER\t4\t0x0056d229\t0x0056d21c\tCRT__IsDigit_Wrapper_0056d21c\tADD\tESP, 0xc\t83 c4 0c\tFALL_THROUGH\n"
                + "0x0056d21c\t0x0056d21c\tAFTER\t5\t0x0056d22c\t0x0056d21c\tCRT__IsDigit_Wrapper_0056d21c\tRET\t\tc3\tTERMINATOR\n",
                encoding="utf-8",
            )

            report = probe.build_report(
                seed_path=root / "seed_names.json",
                decompile_index_path=decompile / "index.tsv",
                decompile_dir=decompile,
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 3)
        by_addr = {item["address"]: item for item in report["targets"]}
        self.assertEqual(by_addr["0x0050b010"]["classification"], "world-occupancy-grid-add-wrapper")
        self.assertEqual(by_addr["0x0050b020"]["classification"], "world-occupancy-grid-remove-wrapper")
        self.assertEqual(by_addr["0x0056d21c"]["classification"], "ctype-digit-mask-return-wrapper")
        self.assertEqual(report["actionCounts"]["renameCandidate"], 3)

    def test_fails_when_expected_instruction_context_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile = root / "decompile"
            decompile.mkdir()
            (root / "seed_names.json").write_text(
                json.dumps([{"address": "0x0056d21c", "name": "CRT__IsDigit_Wrapper_0056d21c"}]),
                encoding="utf-8",
            )
            (decompile / "index.tsv").write_text(
                INDEX_HEADER
                + "0x0056d21c\tCRT__IsDigit_Wrapper_0056d21c\tvoid __cdecl CRT__IsDigit_Wrapper_0056d21c(int param_1)\tOK\n",
                encoding="utf-8",
            )
            (decompile / "0056d21c_CRT__IsDigit_Wrapper_0056d21c.c").write_text(
                "CRT__IsCharTypeMaskOrLeadByte_0056d22d(param_1,0,4);",
                encoding="utf-8",
            )
            (root / "xrefs.tsv").write_text(
                XREF_HEADER
                + "0056d21c\tCRT__IsDigit_Wrapper_0056d21c\t00568df1\t00568dc6\tCRT__ParseCommandLineToken\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (root / "instructions.tsv").write_text(INSTRUCTION_HEADER, encoding="utf-8")

            report = probe.build_report(
                seed_path=root / "seed_names.json",
                decompile_index_path=decompile / "index.tsv",
                decompile_dir=decompile,
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("instruction context" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
