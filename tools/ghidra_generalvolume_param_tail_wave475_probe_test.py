#!/usr/bin/env python3
"""Tests for ghidra_generalvolume_param_tail_wave475_probe.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_generalvolume_param_tail_wave475_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class GeneralVolumeParamTailWave475ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dry.log"
            write(
                path,
                "REPORT: Save succeeded\n"
                "updated=0 skipped=7 created=0 would_create=0 renamed=0 "
                "would_rename=0 missing=0 bad=0\n",
            )
            self.assertEqual(probe.parse_summary(path), probe.EXPECTED_DRY)

    def test_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for name, summary in (
                ("dry.log", "updated=0 skipped=7"),
                ("apply.log", "updated=7 skipped=0"),
                ("verify_dry.log", "updated=0 skipped=7"),
            ):
                write(
                    base / name,
                    "REPORT: Save succeeded\n"
                    f"{summary} created=0 would_create=0 renamed=0 "
                    "would_rename=0 missing=0 bad=0\n",
                )

            write(
                base / "post_metadata.tsv",
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x00411b90\tCGeneralVolume__DispatchSelectedBurstPreset\t"
                "void __fastcall CGeneralVolume__DispatchSelectedBurstPreset(void * general_volume)\t"
                "Wave475 CGeneralVolume-like list context +0x588 +0x10 +0x9c runtime weapon behavior\tOK\n"
                "0x00411bf0\tCGeneralVolume__DispatchMode3BurstProgressAndSpawn\t"
                "void __fastcall CGeneralVolume__DispatchMode3BurstProgressAndSpawn(void * general_volume)\t"
                "Wave475 mode-3 burst progress +0x52c +0x544 +0x55c +0x588 runtime weapon behavior\tOK\n"
                "0x00412240\tCGeneralVolume__GetMode3CurrentEntryRoundedSlotValue\t"
                "int __fastcall CGeneralVolume__GetMode3CurrentEntryRoundedSlotValue(void * general_volume)\t"
                "Wave475 +0x24 +0x55c +0x52c FISTP runtime HUD behavior\tOK\n"
                "0x00412420\tCGeneralVolume__GetMode3CurrentEntryDisplayString\t"
                "short * __fastcall CGeneralVolume__GetMode3CurrentEntryDisplayString(void * general_volume)\t"
                "Wave475 CText__GetStringById entry +0xa4 +0x3c runtime HUD behavior\tOK\n"
                "0x00412830\tCGeneralVolume__DisableLinkedEntriesByNameAndReselect\t"
                "void __thiscall CGeneralVolume__DisableLinkedEntriesByNameAndReselect(void * this, char * entry_name)\t"
                "Wave475 RET 0x4 entry_name +0xa4 +0x9c 0x00411e70 exact helper identity\tOK\n"
                "0x00413660\tCGeneralVolume__ApplyYawInputByWeaponClass\t"
                "void __thiscall CGeneralVolume__ApplyYawInputByWeaponClass(void * this, int axis_input)\t"
                "Wave475 RET 0x4 0x004d337b axis_input +0x278 DAT_005d8cd8 runtime control behavior\tOK\n"
                "0x004136e0\tCGeneralVolume__ApplyPitchInputByWeaponClass\t"
                "void __thiscall CGeneralVolume__ApplyPitchInputByWeaponClass(void * this, int axis_input)\t"
                "Wave475 RET 0x4 0x004d3390 axis_input +0x280 DAT_005d8c90 runtime control behavior\tOK\n",
            )
            write(
                base / "post_tags.tsv",
                "address\tname\ttags\n"
                "0x00411b90\tCGeneralVolume__DispatchSelectedBurstPreset\t"
                "static-reaudit;generalvolume-param-tail-wave475;retail-binary-evidence;general-volume;"
                "mode3-burst;selected-entry;signature-corrected;comment-hardened\n"
                "0x00411bf0\tCGeneralVolume__DispatchMode3BurstProgressAndSpawn\t"
                "static-reaudit;generalvolume-param-tail-wave475;retail-binary-evidence;general-volume;"
                "mode3-burst;progress;signature-corrected;comment-hardened\n"
                "0x00412240\tCGeneralVolume__GetMode3CurrentEntryRoundedSlotValue\t"
                "static-reaudit;generalvolume-param-tail-wave475;retail-binary-evidence;general-volume;"
                "mode3-burst;hud-value;signature-corrected;comment-hardened\n"
                "0x00412420\tCGeneralVolume__GetMode3CurrentEntryDisplayString\t"
                "static-reaudit;generalvolume-param-tail-wave475;retail-binary-evidence;general-volume;"
                "mode3-burst;hud-string;signature-corrected;comment-hardened\n"
                "0x00412830\tCGeneralVolume__DisableLinkedEntriesByNameAndReselect\t"
                "static-reaudit;generalvolume-param-tail-wave475;retail-binary-evidence;general-volume;"
                "entry-selection;string-compare;signature-corrected;comment-hardened\n"
                "0x00413660\tCGeneralVolume__ApplyYawInputByWeaponClass\t"
                "static-reaudit;generalvolume-param-tail-wave475;retail-binary-evidence;general-volume;"
                "axis-input;yaw;signature-corrected;comment-hardened\n"
                "0x004136e0\tCGeneralVolume__ApplyPitchInputByWeaponClass\t"
                "static-reaudit;generalvolume-param-tail-wave475;retail-binary-evidence;general-volume;"
                "axis-input;pitch;signature-corrected;comment-hardened\n",
            )
            write(
                base / "post_xrefs.tsv",
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                "00411b90\tCGeneralVolume__DispatchSelectedBurstPreset\t00409f6a\t00409f20\tCGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90\tCALL\n"
                "00411bf0\tCGeneralVolume__DispatchMode3BurstProgressAndSpawn\t00409f11\t00409ef0\tCGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0\tCALL\n"
                "00412240\tCGeneralVolume__GetMode3CurrentEntryRoundedSlotValue\t0040c47a\t0040c460\tCBattleEngine__GetWeaponAmmoCount\tCALL\n"
                "00412420\tCGeneralVolume__GetMode3CurrentEntryDisplayString\t0040c56a\t0040c550\tCBattleEngine__GetWeaponName\tCALL\n"
                "00412830\tCGeneralVolume__DisableLinkedEntriesByNameAndReselect\t0040dc7b\t0040dc60\tCBattleEngine__DisableVolumeEntryGroupsByNameAndReselect\tCALL\n"
                "00413660\tCGeneralVolume__ApplyYawInputByWeaponClass\t004d337b\t<none>\t<no_function>\tCALL\n"
                "004136e0\tCGeneralVolume__ApplyPitchInputByWeaponClass\t004d3390\t<none>\t<no_function>\tCALL\n",
            )
            write(
                base / "post_00412830_range.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                "0041285a\t\tMOV\tEAX, dword ptr [ESP + 0x18]\n"
                "004128f7\t\tRET\t0x4\n",
            )
            write(
                base / "post_004d337b_axis_calls.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                "004d3374\t\tPUSH\tECX\n"
                "004d337b\t\tCALL\t0x00413660\n"
                "004d338f\t\tPUSH\tEDX\n"
                "004d3390\t\tCALL\t0x004136e0\n",
            )
            write(
                base / "post_instructions.tsv",
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                "0x00413660\t0x00413660\tAFTER\t31\t0x004136d7\t0x00413660\tCGeneralVolume__ApplyYawInputByWeaponClass\tRET\t0x4\t\t\n"
                "0x004136e0\t0x004136e0\tAFTER\t29\t0x0041374e\t0x004136e0\tCGeneralVolume__ApplyPitchInputByWeaponClass\tRET\t0x4\t\t\n",
            )
            for address, name in probe.EXPECTED_NAMES.items():
                tokens = " ".join(probe.DECOMPILE_TOKENS[address])
                write(base / "post-decomp" / f"{address[2:]}_{name}.c", tokens)

            self.assertEqual(probe.run(base), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
