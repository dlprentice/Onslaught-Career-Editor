#!/usr/bin/env python3
"""Tests for the Ghidra name-confidence tranche probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_tranche_probe as probe


INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


class GhidraNameConfidenceTrancheProbeTests(unittest.TestCase):
    def test_classifies_known_wrapper_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile = root / "decompile"
            decompile.mkdir()
            seeds = [
                {"address": "0x004026b0", "name": "SQRT__Wrapper_004026b0"},
                {"address": "0x00411b90", "name": "CEngine_Unk_00506010__Wrapper_00411b90"},
            ]
            (root / "seed_names.json").write_text(json.dumps(seeds), encoding="utf-8")
            (decompile / "index.tsv").write_text(
                INDEX_HEADER
                + "0x004026b0\tSQRT__Wrapper_004026b0\tdouble __fastcall SQRT__Wrapper_004026b0(void * param_1)\tOK\n"
                + "0x00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\tvoid __fastcall CEngine_Unk_00506010__Wrapper_00411b90(void * param_1)\tOK\n",
                encoding="utf-8",
            )
            (decompile / "004026b0_SQRT__Wrapper_004026b0.c").write_text(
                "return (double)SQRT(*(float *)((int)param_1 + 8) * *(float *)((int)param_1 + 8) + *(float *)((int)param_1 + 4) * *(float *)((int)param_1 + 4) + *(float *)param_1 * *(float *)param_1);",
                encoding="utf-8",
            )
            (decompile / "00411b90_CEngine_Unk_00506010__Wrapper_00411b90.c").write_text(
                "*(undefined4 *)(*(int *)((int)param_1 + 0x18) + 0x588) = 0; if (*(int *)((int)pvVar3 + 0x9c) != 0) CGeneralVolume__SpawnBurstFromPresetWithFallback(pvVar3);",
                encoding="utf-8",
            )
            (root / "xrefs.tsv").write_text(
                XREF_HEADER
                + "004026b0\tSQRT__Wrapper_004026b0\t0040b750\t0040b6d0\tCBattleEngine__HandleAutoAim\tUNCONDITIONAL_CALL\n"
                + "00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\t00409f6a\t00409f20\tCGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )

            report = probe.build_report(
                seed_path=root / "seed_names.json",
                decompile_index_path=decompile / "index.tsv",
                decompile_dir=decompile,
                xrefs_path=root / "xrefs.tsv",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 2)
        self.assertEqual(report["actionCounts"]["renameCandidate"], 1)
        self.assertEqual(report["actionCounts"]["commentCandidate"], 1)
        by_addr = {item["address"]: item for item in report["targets"]}
        self.assertEqual(by_addr["0x004026b0"]["classification"], "vector-length-sqrt-wrapper")
        self.assertEqual(by_addr["0x00411b90"]["classification"], "burst-dispatch-wrapper")

    def test_fails_when_expected_tokens_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile = root / "decompile"
            decompile.mkdir()
            (root / "seed_names.json").write_text(
                json.dumps([{"address": "0x004026b0", "name": "SQRT__Wrapper_004026b0"}]),
                encoding="utf-8",
            )
            (decompile / "index.tsv").write_text(
                INDEX_HEADER
                + "0x004026b0\tSQRT__Wrapper_004026b0\tdouble __fastcall SQRT__Wrapper_004026b0(void * param_1)\tOK\n",
                encoding="utf-8",
            )
            (decompile / "004026b0_SQRT__Wrapper_004026b0.c").write_text("return 0;", encoding="utf-8")
            (root / "xrefs.tsv").write_text(XREF_HEADER, encoding="utf-8")

            report = probe.build_report(
                seed_path=root / "seed_names.json",
                decompile_index_path=decompile / "index.tsv",
                decompile_dir=decompile,
                xrefs_path=root / "xrefs.tsv",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x004026b0" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
