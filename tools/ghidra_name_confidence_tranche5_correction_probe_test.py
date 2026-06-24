#!/usr/bin/env python3
"""Tests for the fifth Ghidra name-confidence correction probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_tranche5_correction_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


def write_queue(path: Path, *, wrapper_count: int = 8) -> None:
    path.write_text(
        json.dumps(
            {
                "status": "PASS",
                "totalFunctions": 5863,
                "qualitySignals": {
                    "commentlessFunctionCount": 5495,
                    "undefinedSignatureCount": 2087,
                    "paramSignatureCount": 2563,
                    "uncertainOwnerNameCount": 5,
                    "helperAddressNameCount": 0,
                    "wrapperAddressNameCount": wrapper_count,
                },
                "priorityQueues": {
                    "nameConfidence": [
                        {"address": address, "name": f"still_queued_{address}"}
                        for address in sorted(probe.REMAINING_NAME_CONFIDENCE_ADDRESSES)
                    ]
                },
            }
        ),
        encoding="utf-8",
    )


class GhidraNameConfidenceTranche5CorrectionProbeTests(unittest.TestCase):
    def test_accepts_saved_correction_readback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile = root / "decompile"
            decompile.mkdir()
            (root / "metadata.tsv").write_text(
                METADATA_HEADER
                + "0x00412650\tCBattleEngineJetPart__ResetConfiguration\tvoid __fastcall CBattleEngineJetPart__ResetConfiguration(void * param_1)\tSource-aligned candidate. Proof-boundary: saved name is source/decompile/xref backed and runtime behavior remains open.\tOK\n"
                + "0x00412ad0\tCMonitor__UpdateSurfaceAlignmentAngle\tvoid __fastcall CMonitor__UpdateSurfaceAlignmentAngle(int param_1)\tMonitor angle helper. Proof-boundary: exact source method identity and runtime behavior remain open.\tOK\n"
                + "0x004146b0\tCBattleEngineWalkerPart__ResetConfiguration\tvoid __fastcall CBattleEngineWalkerPart__ResetConfiguration(void * param_1)\tSource-aligned candidate. Proof-boundary: saved name is source/decompile/xref backed and runtime behavior remains open.\tOK\n"
                + "0x004d3080\tCPlayer__AssignBattleEngine\tvoid __thiscall CPlayer__AssignBattleEngine(void * this, void * param_1, void * param_2)\tPlayer assign helper. Proof-boundary: source parity supports the name and runtime behavior remains open.\tOK\n",
                encoding="utf-8",
            )
            (decompile / "index.tsv").write_text(
                INDEX_HEADER
                + "0x00412650\tCBattleEngineJetPart__ResetConfiguration\tvoid __fastcall CBattleEngineJetPart__ResetConfiguration(void * param_1)\tOK\n"
                + "0x00412ad0\tCMonitor__UpdateSurfaceAlignmentAngle\tvoid __fastcall CMonitor__UpdateSurfaceAlignmentAngle(int param_1)\tOK\n"
                + "0x004146b0\tCBattleEngineWalkerPart__ResetConfiguration\tvoid __fastcall CBattleEngineWalkerPart__ResetConfiguration(void * param_1)\tOK\n"
                + "0x004d3080\tCPlayer__AssignBattleEngine\tvoid __thiscall CPlayer__AssignBattleEngine(void * this, void * param_1, void * param_2)\tOK\n",
                encoding="utf-8",
            )
            (decompile / "00412650_CBattleEngineJetPart__ResetConfiguration.c").write_text(
                "CSPtrSet__Remove(param_1, item); CWorldPhysicsManager__CreateWeaponByIndex(i,0xffffffff); 0x50; CSPtrSet__AddToTail(param_1,item);",
                encoding="utf-8",
            )
            (decompile / "00412ad0_CMonitor__UpdateSurfaceAlignmentAngle.c").write_text(
                "ABS(f1); 0x24; _DAT_005d85e0; 0x6c;",
                encoding="utf-8",
            )
            (decompile / "004146b0_CBattleEngineWalkerPart__ResetConfiguration.c").write_text(
                "CSPtrSet__Remove(param_1, item); CWorldPhysicsManager__CreateWeaponByIndex(i,0xffffffff); 0x40; 0x60;",
                encoding="utf-8",
            )
            (decompile / "004d3080_CPlayer__AssignBattleEngine.c").write_text(
                "CGenericActiveReader__SetReader(this,param_1); 0x574; 0x154; 0xe0;",
                encoding="utf-8",
            )
            (root / "xrefs.tsv").write_text(
                XREF_HEADER
                + "00412650\tCBattleEngineJetPart__ResetConfiguration\t0040c695\t0040c650\tCBattleEngine__ApplyWeaponProfileByIndex\tUNCONDITIONAL_CALL\n"
                + "00412650\tCBattleEngineJetPart__ResetConfiguration\t00410268\t00410210\tCBattleEngine__InitTargetSetBucketState\tUNCONDITIONAL_CALL\n"
                + "00412ad0\tCMonitor__UpdateSurfaceAlignmentAngle\t00413a5a\t00413760\tCMonitor__ProcessTrackingAndSurfaceAlignment\tUNCONDITIONAL_CALL\n"
                + "004146b0\tCBattleEngineWalkerPart__ResetConfiguration\t0040c6a4\t0040c650\tCBattleEngine__ApplyWeaponProfileByIndex\tUNCONDITIONAL_CALL\n"
                + "004146b0\tCBattleEngineWalkerPart__ResetConfiguration\t00412c06\t00412bc0\tCBattleEngine__InitDashMoveParams\tUNCONDITIONAL_CALL\n"
                + "004d3080\tCPlayer__AssignBattleEngine\t0046d0dc\t0046d040\tCGame__PostLoadProcess\tUNCONDITIONAL_CALL\n"
                + "004d3080\tCPlayer__AssignBattleEngine\t0047034f\t00470120\tCGame__RespawnPlayer\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            write_queue(root / "queue.json")

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=decompile / "index.tsv",
                decompile_dir=decompile,
                xrefs_path=root / "xrefs.tsv",
                queue_path=root / "queue.json",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 4)
        self.assertEqual(report["queue"]["qualitySignals"]["wrapperAddressNameCount"], 8)

    def test_fails_when_queue_still_has_old_wrapper_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile = root / "decompile"
            decompile.mkdir()
            (root / "metadata.tsv").write_text(
                METADATA_HEADER
                + "0x004d3080\tCPlayer__AssignBattleEngine\tvoid __thiscall CPlayer__AssignBattleEngine(void * this, void * param_1, void * param_2)\tPlayer assign helper. Proof-boundary: source parity supports the name and runtime behavior remains open.\tOK\n",
                encoding="utf-8",
            )
            (decompile / "index.tsv").write_text(
                INDEX_HEADER
                + "0x004d3080\tCPlayer__AssignBattleEngine\tvoid __thiscall CPlayer__AssignBattleEngine(void * this, void * param_1, void * param_2)\tOK\n",
                encoding="utf-8",
            )
            (decompile / "004d3080_CPlayer__AssignBattleEngine.c").write_text(
                "CGenericActiveReader__SetReader(this,param_1); 0x574; 0x154; 0xe0;",
                encoding="utf-8",
            )
            (root / "xrefs.tsv").write_text(
                XREF_HEADER
                + "004d3080\tCPlayer__AssignBattleEngine\t0046d0dc\t0046d040\tCGame__PostLoadProcess\tUNCONDITIONAL_CALL\n"
                + "004d3080\tCPlayer__AssignBattleEngine\t0047034f\t00470120\tCGame__RespawnPlayer\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            write_queue(root / "queue.json", wrapper_count=12)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=decompile / "index.tsv",
                decompile_dir=decompile,
                xrefs_path=root / "xrefs.tsv",
                queue_path=root / "queue.json",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("wrapperAddressNameCount" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
