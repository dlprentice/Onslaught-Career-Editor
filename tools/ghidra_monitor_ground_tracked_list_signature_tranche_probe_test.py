#!/usr/bin/env python3
"""Tests for the monitor/ground/tracked-list Ghidra signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_monitor_ground_tracked_list_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, stale_param: bool = False, overclaim: bool = False) -> dict[str, Path]:
    dry = root / "signature_dry.log"
    apply = root / "signature_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile.mkdir()

    dry.write_text("--- SUMMARY ---\nupdated=0 skipped=8 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\nupdated=8 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    signatures = {
        "0x0040e1b0": "void __thiscall VFuncSlot_00_0040e1b0(void * this, void * sourceObject)",
        "0x0040e840": "void __fastcall CMonitor__ToggleAttachedObjectFlag300(void * monitor)",
        "0x0040e860": "void __thiscall CGeneralVolume__OffsetPointByForwardScaled(void * this, void * point, void * unusedContext)",
        "0x0040e8e0": "float __fastcall CUnit__IsNearGroundByTerrainProbe(void * unit)",
        "0x0040e910": "float __fastcall CUnit__GetGroundedControlFactor(void * unit)",
        "0x0040e940": "void __fastcall CMonitor__UpdateTrackedList_59C(void * monitor)",
        "0x0040eb50": "void __fastcall CMonitor__FlushTrackedList_1D4(void * monitor)",
        "0x0040ebf0": "void __fastcall CMonitor__UpdateTrackedList_620(void * monitor)",
    }
    if stale_param:
        signatures["0x0040e840"] = "void __fastcall CMonitor__ToggleAttachedObjectFlag300(int param_1)"

    comments = {
        "0x0040e1b0": "Signature hardening: vfunc copy/clone boundary copies sourceObject fields +0x14..+0x3b0 into this. Exact owner unresolved; runtime behavior remain unproven.",
        "0x0040e840": "Signature hardening: monitor helper toggles attached object flag at +0x12c through monitor +0x528 attached object pointer. Exact runtime behavior remain unproven.",
        "0x0040e860": "Signature hardening: ret 0x8 keeps point and unusedContext stack slots; helper offsets point by forward vector from vcall +0x6c and optional +0x528 transform context. Exact runtime behavior remain unproven.",
        "0x0040e8e0": "Signature hardening: terrain/shadow height predicate calls CStaticShadows__SampleShadowHeightBilinear with unit +0x1c and compares against +0x24. Exact runtime behavior remain unproven.",
        "0x0040e910": "Signature hardening: grounded-control factor calls vtable +0x10c and HeightDelta__Below015_D4. Exact runtime behavior remain unproven.",
        "0x0040e940": "Signature hardening: tracked list update walks +0x1d4, uses +0x59c/+0x614 effect/sample context, and selector 0x1a. Exact runtime behavior remain unproven.",
        "0x0040eb50": "Signature hardening: flushes tracked list +0x1d4 when +0x1e4 is set and uses +0x59c sound-event context. Exact runtime behavior remain unproven.",
        "0x0040ebf0": "Signature hardening: secondary tracked list update walks +0x620 with +0x630/+0x634 mode state and selector 0x17. Exact runtime behavior remain unproven.",
    }
    if overclaim:
        comments["0x0040ebf0"] += " Runtime behavior proven."

    metadata.write_text(
        METADATA_HEADER
        + "".join(
            f"{addr}\t{probe.TARGETS[addr]['name']}\t{signatures[addr]}\t{comments[addr]}\tOK\n"
            for addr in probe.TARGETS
        ),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER
        + "".join(
            f"{addr}\t{probe.TARGETS[addr]['name']}\t{signatures[addr]}\tOK\n"
            for addr in probe.TARGETS
        ),
        encoding="utf-8",
    )

    decompile_tokens = {
        "0x0040e1b0": "sourceObject +0x3ac +0x3b0 +0xa0 +0xa4",
        "0x0040e840": "monitor +0x528 +0x12c",
        "0x0040e860": "point unusedContext _DAT_005d85ec +0x528 +0x6c",
        "0x0040e8e0": "unit CStaticShadows__SampleShadowHeightBilinear +0x1c +0x24",
        "0x0040e910": "unit +0x10c HeightDelta__Below015_D4",
        "0x0040e940": "monitor +0x1d4 +0x614 0x1a CMonitor__PlayRandomSampleFromChain",
        "0x0040eb50": "monitor +0x1d4 +0x1e4 CUnit__FinalizeLinkedUnitStateAndClear",
        "0x0040ebf0": "monitor +0x620 +0x630 +0x634 0x17 CMeshRenderer__CopyBasisAndRefreshTime",
    }
    for addr, expected in probe.TARGETS.items():
        (decompile / f"{addr[2:]}_{expected['name']}.c").write_text(
            f"{expected['name']} {signatures[addr]} {decompile_tokens[addr]}",
            encoding="utf-8",
        )

    xrefs.write_text(
        XREF_HEADER
        + "0040e1b0\tVFuncSlot_00_0040e1b0\t004e41a3\t004e3f90\tCSpawnerThng__ProcessSpawnWave\tUNCONDITIONAL_CALL\n"
        + "0040e1b0\tVFuncSlot_00_0040e1b0\t004e340d\t004e3370\tCSpawnerThng__Update\tUNCONDITIONAL_CALL\n"
        + "0040e1b0\tVFuncSlot_00_0040e1b0\t004e614c\t004e5e70\tCSquad__VFunc_09_004e5e70\tUNCONDITIONAL_CALL\n"
        + "0040e840\tCMonitor__ToggleAttachedObjectFlag300\t00533990\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
        + "0040e860\tCGeneralVolume__OffsetPointByForwardScaled\t004d8eda\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
        + "0040e8e0\tCUnit__IsNearGroundByTerrainProbe\t005d8b00\t<none>\t<no_function>\tDATA\n"
        + "0040e910\tCUnit__GetGroundedControlFactor\t005d8b04\t<none>\t<no_function>\tDATA\n"
        + "0040e940\tCMonitor__UpdateTrackedList_59C\t00409725\t004081c0\tCMonitor__Process\tUNCONDITIONAL_CALL\n"
        + "0040eb50\tCMonitor__FlushTrackedList_1D4\t0040972e\t004081c0\tCMonitor__Process\tUNCONDITIONAL_CALL\n"
        + "0040ebf0\tCMonitor__UpdateTrackedList_620\t00408236\t004081c0\tCMonitor__Process\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x0040e1b0\t0x0040e1b0\tAFTER\t59\t0x0040e272\t0x0040e1b0\tVFuncSlot_00_0040e1b0\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x0040e840\t0x0040e840\tAFTER\t8\t0x0040e85d\t0x0040e840\tCMonitor__ToggleAttachedObjectFlag300\tRET\t\tc3\tTERMINATOR\n"
        + "0x0040e860\t0x0040e860\tAFTER\t44\t0x0040e8dd\t0x0040e860\tCGeneralVolume__OffsetPointByForwardScaled\tRET\t0x8\tc2 08 00\tTERMINATOR\n"
        + "0x0040e8e0\t0x0040e8e0\tAFTER\t12\t0x0040e907\t0x0040e8e0\tCUnit__IsNearGroundByTerrainProbe\tRET\t\tc3\tTERMINATOR\n"
        + "0x0040e910\t0x0040e910\tAFTER\t12\t0x0040e931\t0x0040e910\tCUnit__GetGroundedControlFactor\tRET\t\tc3\tTERMINATOR\n"
        + "0x0040e940\t0x0040e940\tAFTER\t88\t0x0040eb4f\t0x0040e940\tCMonitor__UpdateTrackedList_59C\tRET\t\tc3\tTERMINATOR\n"
        + "0x0040eb50\t0x0040eb50\tAFTER\t40\t0x0040ebef\t0x0040eb50\tCMonitor__FlushTrackedList_1D4\tRET\t\tc3\tTERMINATOR\n"
        + "0x0040ebf0\t0x0040ebf0\tAFTER\t104\t0x0040ef1f\t0x0040ebf0\tCMonitor__UpdateTrackedList_620\tRET\t\tc3\tTERMINATOR\n",
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


class MonitorGroundTrackedListSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_hardened_tranche(self) -> None:
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
        self.assertEqual(report["summary"]["targets"], 8)
        self.assertEqual(report["summary"]["paramSignatureHits"], 0)
        self.assertEqual(report["summary"]["commentOverclaims"], 0)
        self.assertEqual(report["summary"]["retEvidenceHits"], 8)
        self.assertEqual(report["summary"]["xrefEvidenceHits"], 8)

    def test_fails_for_stale_param_signature_or_overclaim(self) -> None:
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
