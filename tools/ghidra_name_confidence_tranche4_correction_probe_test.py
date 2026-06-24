#!/usr/bin/env python3
"""Tests for the fourth Ghidra name-confidence correction probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_tranche4_correction_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


class GhidraNameConfidenceTranche4CorrectionProbeTests(unittest.TestCase):
    def test_accepts_saved_correction_readback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile = root / "decompile"
            decompile.mkdir()
            (root / "metadata.tsv").write_text(
                METADATA_HEADER
                + "0x00403ff0\tCDXLandscape__DestroyResourceDescriptorArray_Thunk\tvoid __fastcall CDXLandscape__DestroyResourceDescriptorArray_Thunk(int param_1)\tResource-descriptor array destroy thunk. Proof-boundary: destructor/unwind context does not prove render-path ownership, source identity, signature, tags, or runtime behavior.\tOK\n"
                + "0x0040dcc0\tCMonitor__ResetTransitionFlagAndUpdateIfState3_Thunk\tvoid __fastcall CMonitor__ResetTransitionFlagAndUpdateIfState3_Thunk(void * param_1)\tMonitor transition-state thunk. Proof-boundary: owner/source identity and runtime behavior remain unproven.\tOK\n"
                + "0x00410670\tCGeneralVolume__DrainLinkedObjectFromVelocity\tvoid __fastcall CGeneralVolume__DrainLinkedObjectFromVelocity(int param_1)\tGeneral-volume drain body. Proof-boundary: energy/drain semantics and runtime behavior remain provisional.\tOK\n"
                + "0x00411b90\tCGeneralVolume__DispatchSelectedBurstPreset\tvoid __fastcall CGeneralVolume__DispatchSelectedBurstPreset(void * param_1)\tGeneral-volume selected-burst dispatch body. Proof-boundary: corrects current owner confidence away from CEngine/_Unk, but does not prove CWeapon::Fire, CBattleEngine::WeaponFired, weapon-fired stealth reset, signature, or runtime behavior.\tOK\n",
                encoding="utf-8",
            )
            (decompile / "index.tsv").write_text(
                INDEX_HEADER
                + "0x00403ff0\tCDXLandscape__DestroyResourceDescriptorArray_Thunk\tvoid __fastcall CDXLandscape__DestroyResourceDescriptorArray_Thunk(int param_1)\tOK\n"
                + "0x0040dcc0\tCMonitor__ResetTransitionFlagAndUpdateIfState3_Thunk\tvoid __fastcall CMonitor__ResetTransitionFlagAndUpdateIfState3_Thunk(void * param_1)\tOK\n"
                + "0x00410670\tCGeneralVolume__DrainLinkedObjectFromVelocity\tvoid __fastcall CGeneralVolume__DrainLinkedObjectFromVelocity(int param_1)\tOK\n"
                + "0x00411b90\tCGeneralVolume__DispatchSelectedBurstPreset\tvoid __fastcall CGeneralVolume__DispatchSelectedBurstPreset(void * param_1)\tOK\n",
                encoding="utf-8",
            )
            (decompile / "00403ff0_CDXLandscape__DestroyResourceDescriptorArray_Thunk.c").write_text(
                "CDXLandscape__DestroyArrayWithCallback(param_1 + 8,0x41c,1,CResourceDescriptor__dtor);",
                encoding="utf-8",
            )
            (decompile / "0040dcc0_CMonitor__ResetTransitionFlagAndUpdateIfState3_Thunk.c").write_text(
                "0x58c; 0x260; CMonitor__UpdateFlightWalkerTransitionState(param_1);",
                encoding="utf-8",
            )
            (decompile / "00410670_CGeneralVolume__DrainLinkedObjectFromVelocity.c").write_text(
                "CGeneralVolume__ToDoubleIdentity(x); 0x280; 0x588; 0x520;",
                encoding="utf-8",
            )
            (decompile / "00411b90_CGeneralVolume__DispatchSelectedBurstPreset.c").write_text(
                "CGeneralVolume__SpawnBurstFromPresetWithFallback(pvVar3); 0x588; 0x9c;",
                encoding="utf-8",
            )
            (root / "xrefs.tsv").write_text(
                XREF_HEADER
                + "00403ff0\tCDXLandscape__DestroyResourceDescriptorArray_Thunk\t005d0fb6\t005d0fb0\tUnwind@005d0fb0\tUNCONDITIONAL_CALL\n"
                + "00411b90\tCGeneralVolume__DispatchSelectedBurstPreset\t00409f6a\t00409f20\tCGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (root / "queue.json").write_text(
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
                            "wrapperAddressNameCount": 12,
                        },
                    }
                ),
                encoding="utf-8",
            )

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=decompile / "index.tsv",
                decompile_dir=decompile,
                xrefs_path=root / "xrefs.tsv",
                queue_path=root / "queue.json",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 4)
        self.assertEqual(report["queue"]["qualitySignals"]["wrapperAddressNameCount"], 12)

    def test_fails_when_burst_comment_overclaims_weapon_stealth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile = root / "decompile"
            decompile.mkdir()
            (root / "metadata.tsv").write_text(
                METADATA_HEADER
                + "0x00411b90\tCGeneralVolume__DispatchSelectedBurstPreset\tvoid __fastcall CGeneralVolume__DispatchSelectedBurstPreset(void * param_1)\tThis proves CWeapon::Fire and weapon-fired stealth reset.\tOK\n",
                encoding="utf-8",
            )
            (decompile / "index.tsv").write_text(
                INDEX_HEADER
                + "0x00411b90\tCGeneralVolume__DispatchSelectedBurstPreset\tvoid __fastcall CGeneralVolume__DispatchSelectedBurstPreset(void * param_1)\tOK\n",
                encoding="utf-8",
            )
            (decompile / "00411b90_CGeneralVolume__DispatchSelectedBurstPreset.c").write_text(
                "CGeneralVolume__SpawnBurstFromPresetWithFallback(pvVar3); 0x588; 0x9c;",
                encoding="utf-8",
            )
            (root / "xrefs.tsv").write_text(
                XREF_HEADER
                + "00411b90\tCGeneralVolume__DispatchSelectedBurstPreset\t00409f6a\t00409f20\tCGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (root / "queue.json").write_text(
                json.dumps({"status": "PASS", "qualitySignals": {"uncertainOwnerNameCount": 5, "wrapperAddressNameCount": 12}}),
                encoding="utf-8",
            )

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=decompile / "index.tsv",
                decompile_dir=decompile,
                xrefs_path=root / "xrefs.tsv",
                queue_path=root / "queue.json",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("proof-boundary" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
