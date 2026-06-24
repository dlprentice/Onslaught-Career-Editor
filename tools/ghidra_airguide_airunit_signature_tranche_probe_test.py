#!/usr/bin/env python3
"""Tests for the AirGuide/AirUnit signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_airguide_airunit_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


TARGETS = {
    "0x00402150": (
        "CAirGuide__ctor",
        "void * __thiscall CAirGuide__ctor(void * this, void * guideTarget)",
        "AirGuide constructor evidence. Delegates to CGuide constructor, clears active-reader/cache fields, installs the AirGuide vtable, and schedules 2000/0x7d1 events at -1.0. Not concrete class layout, exact source identity, or runtime AI proof.",
    ),
    "0x00402200": (
        "CAirGuide__scalar_deleting_dtor",
        "void * __thiscall CAirGuide__scalar_deleting_dtor(void * this, byte flags)",
        "AirGuide scalar-deleting destructor. Calls CAirGuide__ShutdownAndUnlink, conditionally frees when flags&1, and returns this. Not allocator ownership or destructor completeness proof.",
    ),
    "0x004026e0": (
        "CAirGuide__HandleEvent",
        "void __thiscall CAirGuide__HandleEvent(void * this, void * event)",
        "AirGuide event handler evidence. Event 2000 refreshes ground-clearance cache; event 0x7d1 refreshes nearest-target reader; both paths reschedule randomized timers. Not runtime AI behavior proof.",
    ),
    "0x004027c0": (
        "CAirGuide__AcquireNearestTargetReader",
        "void __fastcall CAirGuide__AcquireNearestTargetReader(void * this)",
        "AirGuide nearest-target reader refresh. Clears reader at +0x2c, scans mapwho around the owner, excludes owner/flagged entries, and picks the nearest threshold candidate. Not concrete layout or runtime targeting proof.",
    ),
    "0x004028e0": (
        "CAirGuide__UpdateGroundClearanceCache",
        "void __fastcall CAirGuide__UpdateGroundClearanceCache(void * this)",
        "AirGuide ground-clearance cache update. Rounds owner x/y, caches grid coordinates at +0x24/+0x28, samples world height in +/-0x14 steps, and stores a minimum clearance-like value at +0x20. Not physics/runtime proof.",
    ),
    "0x00402ad0": (
        "CAirUnit__Init",
        "void __thiscall CAirUnit__Init(void * this, void * init)",
        "AirUnit init evidence. Delegates to CUnit__Init, reads init/profile config at +0x3bc, seeds speed/accel-like fields, builds Trail/Engine particle-node lists, and links into the air-unit set. Not concrete layout, exact source identity, or runtime flight proof.",
    ),
    "0x00402d30": (
        "CAirUnit__dtor_base",
        "void __fastcall CAirUnit__dtor_base(void * this)",
        "AirUnit destructor-base evidence. Removes from the air-unit set, finalizes linked state, drains Trail/Engine particle-node lists, removes particles, frees nodes, and delegates base cleanup. Not destructor completeness or runtime proof.",
    ),
}


def write_fixture(root: Path, *, stale_name: bool = False, overclaim: bool = False) -> dict[str, Path]:
    rename_dry = root / "rename_dry.log"
    rename_apply = root / "rename_apply.log"
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_readback.tsv"
    decompile = root / "decompile_readback"
    xrefs = root / "xrefs_readback.tsv"
    instructions = root / "instructions_readback.tsv"
    decompile.mkdir()

    rename_dry.write_text("--- SUMMARY ---\napplied=0 skipped=6 missing=0 bad=0\n", encoding="utf-8")
    rename_apply.write_text("--- SUMMARY ---\napplied=6 skipped=0 missing=0 bad=0\n", encoding="utf-8")
    signature_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=7 missing=0 bad=0\n", encoding="utf-8")
    signature_apply.write_text("--- SUMMARY ---\nupdated=7 skipped=0 missing=0 bad=0\n", encoding="utf-8")
    comments_dry.write_text("--- SUMMARY ---\napplied=0 skipped=7 missing=0 bad=0\n", encoding="utf-8")
    comments_apply.write_text("--- SUMMARY ---\napplied=7 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    metadata_rows = []
    index_rows = []
    for address, (name, signature, comment) in TARGETS.items():
        if stale_name and address == "0x004026e0":
            name = "VFuncSlot_00_004026e0"
        if overclaim and address == "0x004027c0":
            comment = comment.replace("Not concrete layout or runtime targeting proof", "runtime behavior proven")
        metadata_rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{name}\t{signature}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name} CGuide__ctor_like_0047e290 CEventManager__AddEvent_AtTime "
            "CAirGuide__ShutdownAndUnlink OID__FreeObject Random__NextLCGAbs "
            "CAirGuide__UpdateGroundClearanceCache CAirGuide__AcquireNearestTargetReader "
            "CMapWho__GetFirstEntryWithinRadius CMapWho__GetNextEntryWithinRadius "
            "CGenericActiveReader__SetReader CWorld__GetHeightSamplePacked16 ROUND 0x14 "
            "+ 0x20 CUnit__Init s_Trail_00622d14 s_Engine_00622cec CSPtrSet__AddToTail "
            "CSPtrSet__AddToHead CSPtrSet__Remove CUnit__FinalizeLinkedUnitStateAndClear "
            "CParticleManager__RemoveFromGlobalList VFuncSlot_02_004f95d0 return this 0x7d1 "
            "2000 0xbf800000",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    xrefs.write_text(
        XREF_HEADER
        + "004026e0\tCAirGuide__HandleEvent\t005d8594\t<none>\t<no_function>\tDATA\n"
        + "004027c0\tCAirGuide__AcquireNearestTargetReader\t004026fa\t004026e0\tCAirGuide__HandleEvent\tUNCONDITIONAL_CALL\n"
        + "004028e0\tCAirGuide__UpdateGroundClearanceCache\t00402757\t004026e0\tCAirGuide__HandleEvent\tUNCONDITIONAL_CALL\n"
        + "00402ad0\tCAirUnit__Init\t004d19fd\t004d19d0\tCPlane__Init\tUNCONDITIONAL_CALL\n"
        + "00402d30\tCAirUnit__dtor_base\t005e352c\t<none>\t<no_function>\tDATA\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00402150\t0x00402150\tTARGET\t0\t0x00402172\t0x00402150\tCAirGuide__ctor\tCALL\t0x0047e290\te8 19 c1 07 00\tUNCONDITIONAL_CALL\n"
        + "0x00402150\t0x00402150\tTARGET\t1\t0x004021f8\t0x00402150\tCAirGuide__ctor\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00402200\t0x00402200\tTARGET\t0\t0x00402208\t0x00402200\tCAirGuide__scalar_deleting_dtor\tTEST\tbyte ptr [ESP + 0x8], 0x1\tf6 44 24 08 01\tFALL_THROUGH\n"
        + "0x00402200\t0x00402200\tTARGET\t1\t0x0040221d\t0x00402200\tCAirGuide__scalar_deleting_dtor\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x004026e0\t0x004026e0\tTARGET\t0\t0x00402752\t0x004026e0\tCAirGuide__HandleEvent\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x004027c0\t0x004027c0\tTARGET\t0\t0x004028d3\t0x004027c0\tCAirGuide__AcquireNearestTargetReader\tRET\t\tc3\tTERMINATOR\n"
        + "0x004028e0\t0x004028e0\tTARGET\t0\t0x004029dd\t0x004028e0\tCAirGuide__UpdateGroundClearanceCache\tRET\t\tc3\tTERMINATOR\n"
        + "0x00402ad0\t0x00402ad0\tTARGET\t0\t0x00402d1b\t0x00402ad0\tCAirUnit__Init\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00402d30\t0x00402d30\tTARGET\t0\t0x00402dc3\t0x00402d30\tCAirUnit__dtor_base\tCALL\t0x004f95d0\te8 08 68 0f 00\tUNCONDITIONAL_CALL\n"
        + "0x00402d30\t0x00402d30\tTARGET\t1\t0x00402dcb\t0x00402d30\tCAirUnit__dtor_base\tRET\t\tc3\tTERMINATOR\n",
        encoding="utf-8",
    )
    return {
        "rename_dry": rename_dry,
        "rename_apply": rename_apply,
        "signature_dry": signature_dry,
        "signature_apply": signature_apply,
        "comments_dry": comments_dry,
        "comments_apply": comments_apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class AirGuideAirUnitSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_saved_airguide_airunit_corrections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["renamedTargets"], 6)
        self.assertEqual(report["summary"]["signatureHardenedTargets"], 7)

    def test_fails_for_stale_name_or_runtime_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_name=True, overclaim=True)
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("metadata name mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
