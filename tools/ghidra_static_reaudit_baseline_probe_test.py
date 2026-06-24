#!/usr/bin/env python3
"""Tests for the static Ghidra re-audit baseline probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_static_reaudit_baseline_probe as probe


HEADER = "address\tname\tsignature\n"


class GhidraStaticReauditBaselineProbeTests(unittest.TestCase):
    def test_reports_named_coverage_and_quality_signals_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "functions.tsv"
            path.write_text(
                HEADER
                + "0x00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\tint __fastcall CGeneralVolume__SpawnBurstFromPresetWithFallback(void * param_1)\n"
                + "0x005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\tint __fastcall CEngine__SpawnProjectileBurstFromCurrentPreset(void * param_1)\n"
                + "0x005078b0\tCEngine__GetListEntryIdByIndex\tint __thiscall CEngine__GetListEntryIdByIndex(void * this, int param_1, int param_2)\n"
                + "0x00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\tvoid __fastcall CEngine_Unk_00506010__Wrapper_00411b90(void * param_1)\n"
                + "0x0050b010\tCWorld__DispatchHelper_004bc480\tvoid __stdcall CWorld__DispatchHelper_004bc480(void * param_1)\n"
                + "0x005d7f18\tUnwind@005d7f18\tundefined Unwind@005d7f18(void)\n",
                encoding="utf-8",
            )

            report = probe.build_report(functions_path=path)

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["totalFunctions"], 6)
        self.assertEqual(report["legacyWeakNameCount"], 0)
        self.assertEqual(report["qualitySignals"]["uncertainOwnerNameCount"], 1)
        self.assertEqual(report["qualitySignals"]["wrapperAddressNameCount"], 1)
        self.assertEqual(report["qualitySignals"]["helperAddressNameCount"], 1)
        self.assertEqual(report["qualitySignals"]["undefinedSignatureCount"], 1)
        self.assertEqual(report["qualitySignals"]["paramSignatureCount"], 5)
        self.assertIn("0x00506930", report["seedReauditTargets"]["missingFunctionObjects"])

    def test_fails_when_legacy_weak_names_return(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "functions.tsv"
            path.write_text(
                HEADER
                + "0x00401000\tFUN_00401000\tundefined FUN_00401000(void)\n"
                + "0x00402000\tAuto_00402000\tundefined Auto_00402000(void)\n",
                encoding="utf-8",
            )

            report = probe.build_report(functions_path=path)

        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["legacyWeakNameCount"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
