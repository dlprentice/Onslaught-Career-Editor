#!/usr/bin/env python3
"""Tests for the GeneralVolume / ChangeWeapon Ghidra signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_general_volume_changeweapon_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"


def write_fixture(root: Path, *, stale_param: bool = False, overclaim: bool = False) -> dict[str, Path]:
    dry = root / "signature_dry.log"
    apply = root / "signature_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile.mkdir()

    dry.write_text("--- SUMMARY ---\nupdated=0 skipped=6 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\nupdated=6 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    names = {
        "0x00409e80": "CGeneralVolume__SetParam2CC_ToOne",
        "0x00409e90": "CGeneralVolume__SetParam2CC_ToOne_IfCurrentState1",
        "0x00409ec0": "CGeneralVolume__SetParam2CC_ToPoint4_IfCurrentState1",
        "0x00409ef0": "CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0",
        "0x00409f20": "CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90",
        "0x00409f70": "CBattleEngine__ChangeWeapon",
    }
    signatures = {
        "0x00409e80": "void __fastcall CGeneralVolume__SetParam2CC_ToOne(void * generalVolume)",
        "0x00409e90": "void __fastcall CGeneralVolume__SetParam2CC_ToOne_IfCurrentState1(void * generalVolume)",
        "0x00409ec0": "void __fastcall CGeneralVolume__SetParam2CC_ToPoint4_IfCurrentState1(void * generalVolume)",
        "0x00409ef0": "void __fastcall CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0(void * generalVolume)",
        "0x00409f20": "void __fastcall CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90(void * generalVolume)",
        "0x00409f70": "void __fastcall CBattleEngine__ChangeWeapon(void * battleEngine)",
    }
    if stale_param:
        signatures["0x00409f70"] = "void __fastcall CBattleEngine__ChangeWeapon(int param_1)"

    comments = {
        "0x00409e80": "Signature hardening: writes float 1.0 to generalVolume +0x2cc. Current callers include CCockpit__CycleToNextUsableWeapon and CGeneralVolume__SelectNextEnabledEntry; runtime behavior remain unproven.",
        "0x00409e90": "Signature hardening: resolves a related state through the +0x1d4 vcall and writes float 1.0 to generalVolume +0x2cc only when nested state +0x34 equals 1. Runtime behavior remain unproven.",
        "0x00409ec0": "Signature hardening: resolves a related state through the +0x1d4 vcall and writes float 0.4 to generalVolume +0x2cc only when nested state +0x34 equals 1. Runtime behavior remain unproven.",
        "0x00409ef0": "Signature hardening: dispatches by generalVolume mode +0x260 to the mode-2 current-entry refresh at +0x578 or the mode-3 burst path at +0x57c. Runtime behavior remain unproven.",
        "0x00409f20": "Signature hardening: clears generalVolume +0x588, seeds +0x2b4 from +0x2a0 or +0x2b0, then dispatches selected-burst path. Runtime behavior remain unproven.",
        "0x00409f70": "Signature hardening/source bridge: retail body counts active weapons by mode +0x260, clears +0x588, timestamps +0x584, and matches Stuart CBattleEngine::ChangeWeapon. Runtime behavior remain unproven.",
    }
    if overclaim:
        comments["0x00409f70"] += " Runtime behavior proven."

    metadata.write_text(
        METADATA_HEADER + "".join(f"{addr}\t{names[addr]}\t{signatures[addr]}\t{comments[addr]}\tOK\n" for addr in names),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER + "".join(f"{addr}\t{names[addr]}\t{signatures[addr]}\tOK\n" for addr in names),
        encoding="utf-8",
    )
    decompile_tokens = {
        "0x00409e80": "generalVolume +0x2cc 0x3f800000",
        "0x00409e90": "generalVolume +0x1d4 +0x34 +0x2cc 0x3f800000",
        "0x00409ec0": "generalVolume +0x1d4 +0x34 +0x2cc 0x3ecccccd",
        "0x00409ef0": "generalVolume +0x260 +0x578 +0x57c CGeneralVolume__UpdateCurrentEntryProgressAndRefresh CGeneralVolume__DispatchMode3BurstProgressAndSpawn",
        "0x00409f20": "generalVolume +0x588 +0x2b4 +0x2a0 +0x2b0 CGeneralVolume__ResetState588AndRefreshCurrentEntry CGeneralVolume__DispatchSelectedBurstPreset",
        "0x00409f70": "battleEngine LinkedObjectList__CountFlag9C CGeneralVolume__SelectNextEnabledEntry CCockpit__CycleToNextUsableWeapon DAT_00672fd0 s_Vulcan_Cannon s_Rail_Gun CBattleEngine__AttachHudSoundEventListener",
    }
    for addr, name in names.items():
        (decompile / f"{addr[2:]}_{name}.c").write_text(
            f"{name} {signatures[addr]} {decompile_tokens[addr]}",
            encoding="utf-8",
        )
    xrefs.write_text(
        XREF_HEADER
        + "00409e80\tCGeneralVolume__SetParam2CC_ToOne\t00411fe5\t00411e70\tCCockpit__CycleToNextUsableWeapon\tUNCONDITIONAL_CALL\n"
        + "00409e80\tCGeneralVolume__SetParam2CC_ToOne\t00413ff9\t00413eb0\tCGeneralVolume__SelectNextEnabledEntry\tUNCONDITIONAL_CALL\n"
        + "00409e90\tCGeneralVolume__SetParam2CC_ToOne_IfCurrentState1\t004d32b8\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
        + "00409ec0\tCGeneralVolume__SetParam2CC_ToPoint4_IfCurrentState1\t004d32b1\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
        + "00409ef0\tCGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0\t004d32cd\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
        + "00409f20\tCGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90\t004d32d4\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
        + "00409f70\tCBattleEngine__ChangeWeapon\t004d32db\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00409e80\t0x00409e80\tAFTER\t4\t0x00409e8a\t0x00409e80\tCGeneralVolume__SetParam2CC_ToOne\tRET\t\tc3\tTERMINATOR\n"
        + "0x00409e90\t0x00409e90\tAFTER\t16\t0x00409eb6\t0x00409e90\tCGeneralVolume__SetParam2CC_ToOne_IfCurrentState1\tRET\t\tc3\tTERMINATOR\n"
        + "0x00409ec0\t0x00409ec0\tAFTER\t16\t0x00409ee6\t0x00409ec0\tCGeneralVolume__SetParam2CC_ToPoint4_IfCurrentState1\tRET\t\tc3\tTERMINATOR\n"
        + "0x00409ef0\t0x00409ef0\tAFTER\t16\t0x00409f16\t0x00409ef0\tCGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0\tRET\t\tc3\tTERMINATOR\n"
        + "0x00409f20\t0x00409f20\tAFTER\t48\t0x00409f6f\t0x00409f20\tCGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90\tRET\t\tc3\tTERMINATOR\n"
        + "0x00409f70\t0x00409f70\tAFTER\t256\t0x0040a340\t0x00409f70\tCBattleEngine__ChangeWeapon\tRET\t\tc3\tTERMINATOR\n",
        encoding="utf-8",
    )
    return {
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class GeneralVolumeChangeWeaponSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_corrected_general_volume_changeweapon_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 6)
        self.assertEqual(report["summary"]["paramSignatureHits"], 0)
        self.assertEqual(report["summary"]["commentOverclaims"], 0)
        self.assertEqual(report["summary"]["retEvidenceHits"], 6)

    def test_fails_for_stale_param_signature_or_runtime_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_param=True, overclaim=True)
            report = probe.build_report(
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("param_N signature remains" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
