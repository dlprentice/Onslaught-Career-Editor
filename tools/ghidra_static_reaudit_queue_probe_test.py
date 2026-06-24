#!/usr/bin/env python3
"""Tests for the full Ghidra static re-audit queue probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_static_reaudit_queue_probe as probe


HEADER = "address\tname\tsignature\tcomment\tstatus\n"


class GhidraStaticReauditQueueProbeTests(unittest.TestCase):
    def test_builds_comment_signature_and_name_queues(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "quality.tsv"
            path.write_text(
                HEADER
                + "0x00506930\tCWeapon__HandleFireBurstEvent\tundefined CWeapon__HandleFireBurstEvent(void * param_1)\tSaved proof-boundary comment\tOK\n"
                + "0x00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\tint __fastcall CGeneralVolume__SpawnBurstFromPresetWithFallback(void * param_1)\t\tOK\n"
                + "0x00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\tvoid __fastcall CEngine_Unk_00506010__Wrapper_00411b90(void * param_1)\t\tOK\n"
                + "0x0050b010\tCWorld__DispatchHelper_004bc480\tvoid __stdcall CWorld__DispatchHelper_004bc480(void * param_1)\t\tOK\n"
                + "0x005078b0\tCEngine__GetListEntryIdByIndex\tint __thiscall CEngine__GetListEntryIdByIndex(void * this, int index)\tStable behavior note\tOK\n",
                encoding="utf-8",
            )

            report = probe.build_report(snapshot_path=path)

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["totalFunctions"], 5)
        self.assertEqual(report["qualitySignals"]["commentlessFunctionCount"], 3)
        self.assertEqual(report["qualitySignals"]["undefinedSignatureCount"], 1)
        self.assertEqual(report["qualitySignals"]["paramSignatureCount"], 4)
        self.assertEqual(report["qualitySignals"]["uncertainOwnerNameCount"], 1)
        self.assertEqual(report["qualitySignals"]["helperAddressNameCount"], 1)
        self.assertEqual(report["qualitySignals"]["wrapperAddressNameCount"], 1)
        self.assertEqual(report["seedFunctionStatus"]["0x00506930"]["hasComment"], True)
        self.assertEqual(report["seedFunctionStatus"]["0x00506010"]["hasComment"], False)
        self.assertEqual(report["priorityQueues"]["commentlessHighSignal"][0]["address"], "0x00506010")
        self.assertEqual(report["priorityQueues"]["nameConfidence"][0]["address"], "0x00411b90")

    def test_fails_for_legacy_weak_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "quality.tsv"
            path.write_text(
                HEADER
                + "0x00401000\tFUN_00401000\tundefined FUN_00401000(void)\t\tOK\n",
                encoding="utf-8",
            )

            report = probe.build_report(snapshot_path=path)

        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["qualitySignals"]["legacyWeakNameCount"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
