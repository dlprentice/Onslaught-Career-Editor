#!/usr/bin/env python3
"""Tests for the BattleEngine weapon slot-0 xref probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import battleengine_weapon_slot0_xref_probe as probe


XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"


def write_fixture(root: Path, *, add_direct_slot0_code_ref: bool = False) -> tuple[Path, Path]:
    xrefs = root / "slot0_xrefs.tsv"
    rows = [
        "00506930\t<no_function>\t005dfc94\t<none>\t<no_function>\tDATA",
        "005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\t00506143\t00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\tUNCONDITIONAL_CALL",
        "005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\t005069b6\t<none>\t<no_function>\tUNCONDITIONAL_CALL",
        "005078b0\tCEngine__GetListEntryIdByIndex\t00506b75\t005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\tUNCONDITIONAL_CALL",
    ]
    if add_direct_slot0_code_ref:
        rows.append(
            "00506930\t<no_function>\t00409999\t00409000\tCBattleEngine__UnexpectedDirectWeaponCaller\tUNCONDITIONAL_CALL"
        )
    xrefs.write_text(XREF_HEADER + "\n".join(rows) + "\n", encoding="utf-8")

    index = root / "index.tsv"
    index.write_text(
        INDEX_HEADER
        + "\n".join(
            [
                "0x00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\tint __fastcall CGeneralVolume__SpawnBurstFromPresetWithFallback(void * param_1)\tOK",
                "0x005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\tint __fastcall CEngine__SpawnProjectileBurstFromCurrentPreset(void * param_1)\tOK",
                "0x005078b0\tCEngine__GetListEntryIdByIndex\tint __thiscall CEngine__GetListEntryIdByIndex(void * this, int param_1, int param_2)\tOK",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return xrefs, index


class BattleEngineWeaponSlot0XrefProbeTests(unittest.TestCase):
    def test_passes_for_current_vtable_stub_and_burst_caller_xrefs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            xrefs, index = write_fixture(Path(tmp))

            report = probe.build_report(xrefs_path=xrefs, decompile_index_path=index)

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["candidateClassification"], "slot0-xrefs-vtable-stub-and-named-burst-caller")
            self.assertEqual(report["slot0Stub"]["dataRefCount"], 1)
            self.assertEqual(report["slot0Stub"]["directCodeRefCount"], 0)
            self.assertIn("0x00506010", report["innerBody"]["namedCallerFunctionAddresses"])
            self.assertIn("0x005069b6", report["innerBody"]["rawOuterStubCallsites"])
            self.assertIn("0x00506b75", report["postReturnHelper"]["innerBodyCallsites"])
            self.assertEqual(report["unexpectedDirectSlot0CodeRefs"], [])

    def test_fails_when_slot0_stub_has_direct_code_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            xrefs, index = write_fixture(Path(tmp), add_direct_slot0_code_ref=True)

            report = probe.build_report(xrefs_path=xrefs, decompile_index_path=index)

            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(len(report["unexpectedDirectSlot0CodeRefs"]), 1)
            self.assertTrue(any("unexpected direct code refs to slot0 stub" in item for item in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
