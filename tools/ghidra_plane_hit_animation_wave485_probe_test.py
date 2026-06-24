#!/usr/bin/env python3
"""Unit tests for the Wave485 CPlane hit/animation probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_plane_hit_animation_wave485_probe as probe


class PlaneHitAnimationWave485ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.log"
            path.write_text(
                "updated=4 skipped=0 created=0 would_create=0 renamed=4 would_rename=0 missing=0 bad=0\n",
                encoding="utf-8",
            )
            self.assertEqual(
                probe.parse_summary(path),
                {
                    "updated": 4,
                    "skipped": 0,
                    "created": 0,
                    "would_create": 0,
                    "renamed": 4,
                    "would_rename": 0,
                    "missing": 0,
                    "bad": 0,
                },
            )

    def test_stale_name_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            base.joinpath("post_metadata.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                f"{probe.HIT}\tCUnitAI__Hit_CheckFatalDamageAndDie\t"
                f"{probe.TARGETS[probe.HIT]['signature']}\t"
                "CPlane vtable 0x005e1930 slot 39 and rebuild parity remain unproven\tOK\n",
                encoding="utf-8",
            )
            base.joinpath("post_tags.tsv").write_text(
                "address\tname\ttags\tstatus\n"
                f"{probe.HIT}\tCUnitAI__Hit_CheckFatalDamageAndDie\t\tOK\n",
                encoding="utf-8",
            )
            failures: list[str] = []
            probe.check_metadata(base, failures)
            self.assertTrue(any("stale names remain" in failure for failure in failures))
            self.assertTrue(any("expected name CPlane__Hit_CheckFatalDamageAndDie" in failure for failure in failures))

    def test_sibling_slot_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            base.joinpath("post_vtable_slots.tsv").write_text(
                "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\t"
                "containing_entry\tcontaining_name\tstatus\n"
                "005e1930\t39\t005e19cc\t0x004d1f10\t004d1f10\t004d1f10\t"
                "CPlane__Hit_CheckFatalDamageAndDie\t004d1f10\tCPlane__Hit_CheckFatalDamageAndDie\tOK\n"
                "005e1930\t59\t005e1a1c\t0x004d2010\t004d2010\t004d2010\t"
                "CPlane__UpdateAttackLaunchAnimationState\t004d2010\tCPlane__UpdateAttackLaunchAnimationState\tOK\n"
                "005e1930\t68\t005e1a40\t0x004d20a0\t004d20a0\t004d20a0\t"
                "CPlane__VFunc_68_CrashIfNoAirSupport\t004d20a0\tCPlane__VFunc_68_CrashIfNoAirSupport\tOK\n"
                "005e1930\t69\t005e1a44\t0x0047bf60\t0047bf60\t0047bf60\t"
                "CPlane__VFunc_69_CrashIfNoSupportModes\t0047bf60\tCPlane__VFunc_69_CrashIfNoSupportModes\tOK\n"
                "005e123c\t39\t005e12d8\t0x00403ba0\t00403ba0\t00403ba0\t"
                "CPlane__Hit_CheckFatalDamageAndDie\t00403ba0\tCPlane__Hit_CheckFatalDamageAndDie\tOK\n"
            )
            base.joinpath("post_vtable_types.tsv").write_text(
                "vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\t"
                "raw_type_name\tdemangled_type_name\n"
                "005e1930\t005e192c\t00617930\t0x00000000\t0\t0\t0x0063d5a8\t0x00617920\t"
                ".?AVCPlane@@\tCPlane\n"
                "005e123c\t005e1238\t00617590\t0x00000000\t0\t0\t0x0063d508\t0x00617580\t"
                ".?AVCDiveBomber@@\tCDiveBomber\n"
                "005e2bcc\t005e2bc8\t00617e50\t0x00000000\t0\t0\t0x0063d700\t0x00617e40\t"
                ".?AVCGroundAttackAircraft@@\tCGroundAttackAircraft\n"
                "005e2e20\t005e2e1c\t00617508\t0x00000000\t0\t0\t0x0063d4f0\t0x006174f8\t"
                ".?AVCBomber@@\tCBomber\n"
                "005d8d1c\t005d8d18\t0060c850\t0x00000000\t0\t0\t0x00623960\t0x0060c840\t"
                ".?AVCUnitAI@@\tCUnitAI\n",
                encoding="utf-8",
            )
            failures: list[str] = []
            probe.check_vtables(base, failures)
            self.assertTrue(any("expected sibling CThing__Hit_TriggerDieOnUnitOrTypeMask02100000" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main(verbosity=2)
