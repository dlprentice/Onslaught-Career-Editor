#!/usr/bin/env python3
"""Tests for the second Ghidra name-confidence tranche probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_tranche2_probe as probe


INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


class GhidraNameConfidenceTranche2ProbeTests(unittest.TestCase):
    def test_classifies_weapon_and_nearest_lookup_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile = root / "decompile"
            decompile.mkdir()
            seeds = [
                {"address": "0x00414b30", "name": "CVBufTexture_Unk_0050a290__Wrapper_00414b30"},
                {"address": "0x00505c30", "name": "stricmp__Wrapper_00505c30"},
            ]
            (root / "seed_names.json").write_text(json.dumps(seeds), encoding="utf-8")
            (decompile / "index.tsv").write_text(
                INDEX_HEADER
                + "0x00414b30\tCVBufTexture_Unk_0050a290__Wrapper_00414b30\tint __fastcall CVBufTexture_Unk_0050a290__Wrapper_00414b30(void * param_1)\tOK\n"
                + "0x00505c30\tstricmp__Wrapper_00505c30\tint __cdecl stricmp__Wrapper_00505c30(void * param_1, void * param_2)\tOK\n",
                encoding="utf-8",
            )
            (decompile / "00414b30_CVBufTexture_Unk_0050a290__Wrapper_00414b30.c").write_text(
                "iVar2 = CUnit__IsTargetTimeoutBeforeProfileLimit(iVar2); if (iVar2 != 0) break; return 1;",
                encoding="utf-8",
            )
            (decompile / "00505c30_stricmp__Wrapper_00505c30.c").write_text(
                "iVar6 = stricmp(*(char **)(iVar7 + 4),param_1); DAT_00854fc8 = DAT_00854fc0; param_1 = (void *)0x4b18967f; fVar5 = *(float *)(iVar8 + 0x24);",
                encoding="utf-8",
            )
            (root / "xrefs.tsv").write_text(
                XREF_HEADER
                + "00414b30\tCVBufTexture_Unk_0050a290__Wrapper_00414b30\t0040657e\t00406560\tCBattleEngine__UpdateAutoTargetSetAndFireProjectiles\tUNCONDITIONAL_CALL\n"
                + "00505c30\tstricmp__Wrapper_00505c30\t00537d8c\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
                + "00505c30\tstricmp__Wrapper_00505c30\t00537e6b\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n",
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
        self.assertEqual(report["actionCounts"]["renameCandidate"], 2)
        by_addr = {item["address"]: item for item in report["targets"]}
        self.assertEqual(by_addr["0x00414b30"]["classification"], "target-set-timeout-scan")
        self.assertEqual(by_addr["0x00505c30"]["classification"], "named-entry-nearest-position-lookup")

    def test_fails_when_expected_xref_context_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile = root / "decompile"
            decompile.mkdir()
            (root / "seed_names.json").write_text(
                json.dumps([{"address": "0x00414b30", "name": "CVBufTexture_Unk_0050a290__Wrapper_00414b30"}]),
                encoding="utf-8",
            )
            (decompile / "index.tsv").write_text(
                INDEX_HEADER
                + "0x00414b30\tCVBufTexture_Unk_0050a290__Wrapper_00414b30\tint __fastcall CVBufTexture_Unk_0050a290__Wrapper_00414b30(void * param_1)\tOK\n",
                encoding="utf-8",
            )
            (decompile / "00414b30_CVBufTexture_Unk_0050a290__Wrapper_00414b30.c").write_text(
                "iVar2 = CUnit__IsTargetTimeoutBeforeProfileLimit(iVar2); return 1;",
                encoding="utf-8",
            )
            (root / "xrefs.tsv").write_text(XREF_HEADER, encoding="utf-8")

            report = probe.build_report(
                seed_path=root / "seed_names.json",
                decompile_index_path=decompile / "index.tsv",
                decompile_dir=decompile,
                xrefs_path=root / "xrefs.tsv",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("expected xref context" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
