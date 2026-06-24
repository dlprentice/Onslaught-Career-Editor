#!/usr/bin/env python3
"""Tests for the air-unit vfunc owner/name correction probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_airunit_vfunc_owner_correction_probe as probe


TARGET_ROWS = {
    "0x00402030": (
        "CActor__VFunc_18_SyncOldVectorAfterBaseCall",
        "void __thiscall CActor__VFunc_18_SyncOldVectorAfterBaseCall(void * this)",
        "CActor vtable slot 18 this+0x1c this+0x8c provisional",
        "CActor__VFunc_18_SyncOldVectorAfterBaseCall this 0x1c 0x8c",
    ),
    "0x00402fa0": (
        "CUnit__UpdateMotionAndTrailEffects",
        "void __thiscall CUnit__UpdateMotionAndTrailEffects(void * this)",
        "Unit motion/effects pass vtable slot 66 velocity trail low-altitude",
        "CUnit__UpdateMotionAndTrailEffects CUnit__UpdateMotionAttachmentsAndEffects 0x170",
    ),
    "0x00403730": (
        "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport",
        "void __thiscall CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport(void * this)",
        "Air-unit vtable slot 68 unit-data +0x11c Not a CExplosionInitThing",
        "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport CUnitAI__SetStateTimestampCCToNow 0x11c",
    ),
    "0x00403760": (
        "CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes",
        "void __thiscall CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes(void * this)",
        "Air-unit vtable slot 69 unit-data +0x11c/+0x124 duplicate CUnitAI",
        "CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes CUnit__ResetFieldD0ToGlobalThreshold 0x124",
    ),
    "0x00403a50": (
        "CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear",
        "int __thiscall CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear(void * this)",
        "Air-unit vtable slot 117 position components differ Not a CFrontEndPage",
        "CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear 0x8c 0x1c 0x2c",
    ),
    "0x004d20a0": (
        "CPlane__VFunc_68_CrashIfNoAirSupport",
        "void __thiscall CPlane__VFunc_68_CrashIfNoAirSupport(void * this)",
        "Plane-family vtable slot 68 CAirUnit slot-68 unit-data +0x11c",
        "CPlane__VFunc_68_CrashIfNoAirSupport CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport 0x11c",
    ),
    "0x0047bf60": (
        "CPlane__VFunc_69_CrashIfNoSupportModes",
        "void __thiscall CPlane__VFunc_69_CrashIfNoSupportModes(void * this)",
        "Plane-family vtable slot 69 CAirUnit slot-69 unit-data +0x11c/+0x124",
        "CPlane__VFunc_69_CrashIfNoSupportModes CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes 0x124",
    ),
}


def write_fixture(root: Path, *, stale: bool = False) -> dict[str, Path]:
    apply_dry = root / "apply_dry.log"
    apply = root / "apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    vtable_map = root / "vtable_owner_map_final.tsv"
    decompile.mkdir()

    apply_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=7 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\nupdated=7 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    rows = dict(TARGET_ROWS)
    if stale:
        rows["0x00403760"] = (
            "CUnitAI__ProcessAndCrashIfNoAirOrHoverSupport",
            "void __fastcall CUnitAI__ProcessAndCrashIfNoAirOrHoverSupport(void * param_1)",
            "stale duplicate owner",
            "CUnitAI__ProcessAndCrashIfNoAirOrHoverSupport param_1",
        )

    metadata.write_text(
        "address\tname\tsignature\tcomment\tstatus\n"
        + "".join(
            f"{address}\t{name}\t{signature}\t{comment}\tOK\n"
            for address, (name, signature, comment, _decompile) in rows.items()
        ),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        "address\tname\tsignature\tstatus\n"
        + "".join(f"{address}\t{name}\t{signature}\tOK\n" for address, (name, signature, _comment, _decompile) in rows.items()),
        encoding="utf-8",
    )
    for address, (name, signature, _comment, decompile_text) in rows.items():
        (decompile / f"{address[2:]}_{name}.c").write_text(signature + " " + decompile_text, encoding="utf-8")

    xrefs.write_text(
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        + "".join(f"{address[2:]}\t{name}\t005e0000\t<none>\t<no_function>\tDATA\n" for address, (name, *_rest) in rows.items()),
        encoding="utf-8",
    )
    instructions.write_text(
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        + "".join(f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{name}\tRET\t\t\tTERMINATOR\n" for address, (name, *_rest) in rows.items()),
        encoding="utf-8",
    )
    vtable_map.write_text(
        "target_addr\ttype\tslot\tdata_refs\n"
        "00402030\tCActor\t18\t1\n"
        "00403730\tCAirUnit\t68\t5\n"
        "00403760\tCAirUnit\t69\t5\n"
        "00403a50\tCAirUnit\t117\t9\n"
        "004d20a0\tCPlane\t68\t4\n"
        "0047bf60\tCPlane\t69\t4\n",
        encoding="utf-8",
    )
    return {
        "apply_dry": apply_dry,
        "apply": apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
        "vtable_map": vtable_map,
    }


class AirUnitVfuncOwnerCorrectionProbeTests(unittest.TestCase):
    def test_passes_for_corrected_airunit_vfunc_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                apply_dry_log_path=paths["apply_dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                vtable_map_path=paths["vtable_map"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 7)
        self.assertEqual(report["summary"]["staleNameTokenHits"], 0)

    def test_fails_for_stale_duplicate_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True)
            report = probe.build_report(
                apply_dry_log_path=paths["apply_dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                vtable_map_path=paths["vtable_map"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("name mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("stale name/signature token" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
