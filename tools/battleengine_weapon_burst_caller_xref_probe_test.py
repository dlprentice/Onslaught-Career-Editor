#!/usr/bin/env python3
"""Tests for the BattleEngine burst-caller xref probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import battleengine_weapon_burst_caller_xref_probe as probe


XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"


XREF_ROWS = [
    "00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\t004fc0b7\t004fc080\tCUnitAI__TrySpawnOrFinalizeAttachedUnit\tUNCONDITIONAL_CALL",
    "00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\t004ded11\t004decc0\tCSentinel__UpdateFlamethrowers\tUNCONDITIONAL_CALL",
    "00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\t0044e093\t<none>\t<no_function>\tUNCONDITIONAL_CALL",
    "00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\t004f4bd6\t<none>\t<no_function>\tUNCONDITIONAL_CALL",
    "00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\t00411e0f\t00411bf0\tCEngine_Unk_0050a080__Wrapper_00411bf0\tUNCONDITIONAL_CALL",
    "00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\t00411e5b\t00411bf0\tCEngine_Unk_0050a080__Wrapper_00411bf0\tUNCONDITIONAL_CALL",
    "00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\t00413d5f\t00413cf0\tCGeneralVolume__UpdateCurrentEntryProgressAndRefresh\tUNCONDITIONAL_CALL",
    "00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\t00413e9a\t00413cf0\tCGeneralVolume__UpdateCurrentEntryProgressAndRefresh\tUNCONDITIONAL_CALL",
    "00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\t00411be4\t00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\tUNCONDITIONAL_CALL",
    "00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\t00413ce2\t00413cc0\tCGeneralVolume__ResetState588AndRefreshCurrentEntry\tUNCONDITIONAL_CALL",
]

INDEX_ROWS = [
    "0x004fc080\tCUnitAI__TrySpawnOrFinalizeAttachedUnit\tint __fastcall CUnitAI__TrySpawnOrFinalizeAttachedUnit(void * param_1)\tOK",
    "0x004decc0\tCSentinel__UpdateFlamethrowers\tundefined CSentinel__UpdateFlamethrowers(void)\tOK",
    "0x00411bf0\tCEngine_Unk_0050a080__Wrapper_00411bf0\tvoid __fastcall CEngine_Unk_0050a080__Wrapper_00411bf0(void * param_1)\tOK",
    "0x00413cf0\tCGeneralVolume__UpdateCurrentEntryProgressAndRefresh\tvoid __fastcall CGeneralVolume__UpdateCurrentEntryProgressAndRefresh(int param_1)\tOK",
    "0x00411b90\tCEngine_Unk_00506010__Wrapper_00411b90\tvoid __fastcall CEngine_Unk_00506010__Wrapper_00411b90(void * param_1)\tOK",
    "0x00413cc0\tCGeneralVolume__ResetState588AndRefreshCurrentEntry\tvoid __fastcall CGeneralVolume__ResetState588AndRefreshCurrentEntry(int param_1)\tOK",
]


def write_fixture(root: Path, *, add_weapon_named_caller: bool = False) -> tuple[Path, Path]:
    xrefs = root / "burst_caller_xrefs.tsv"
    rows = list(XREF_ROWS)
    if add_weapon_named_caller:
        rows.append(
            "00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\t00409999\t00409000\tCBattleEngine__WeaponFireBurstWrapper\tUNCONDITIONAL_CALL"
        )
    xrefs.write_text(XREF_HEADER + "\n".join(rows) + "\n", encoding="utf-8")

    index = root / "index.tsv"
    index.write_text(INDEX_HEADER + "\n".join(INDEX_ROWS) + "\n", encoding="utf-8")
    return xrefs, index


class BattleEngineWeaponBurstCallerXrefProbeTests(unittest.TestCase):
    def test_passes_for_current_shared_burst_caller_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            xrefs, index = write_fixture(Path(tmp))

            report = probe.build_report(xrefs_path=xrefs, caller_index_path=index)

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["candidateClassification"], "burst-caller-xrefs-shared-effect-path")
            self.assertEqual(report["xrefRowCount"], 10)
            self.assertEqual(report["namedCallerFunctionCount"], 6)
            self.assertEqual(report["rawNoFunctionCallsites"], ["0x0044e093", "0x004f4bd6"])
            self.assertEqual(report["weaponNamedCallerRows"], [])
            self.assertIn("CUnitAI__TrySpawnOrFinalizeAttachedUnit", report["namedCallerFunctions"])
            self.assertIn("CGeneralVolume__UpdateCurrentEntryProgressAndRefresh", report["namedCallerFunctions"])

    def test_fails_on_obvious_weapon_named_direct_caller(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            xrefs, index = write_fixture(Path(tmp), add_weapon_named_caller=True)

            report = probe.build_report(xrefs_path=xrefs, caller_index_path=index)

            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(len(report["weaponNamedCallerRows"]), 1)
            self.assertTrue(any("unexpected weapon-named caller" in item for item in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
