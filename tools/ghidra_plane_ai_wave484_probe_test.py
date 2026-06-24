#!/usr/bin/env python3
"""Unit tests for the Wave484 CPlaneAI destructor probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_plane_ai_wave484_probe as probe


class PlaneAIWave484ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.log"
            path.write_text(
                "updated=2 skipped=0 created=0 would_create=0 renamed=2 would_rename=0 missing=0 bad=0\n",
                encoding="utf-8",
            )
            self.assertEqual(
                probe.parse_summary(path),
                {
                    "updated": 2,
                    "skipped": 0,
                    "created": 0,
                    "would_create": 0,
                    "renamed": 2,
                    "would_rename": 0,
                    "missing": 0,
                    "bad": 0,
                },
            )

    def test_stale_wrapper_name_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            base.joinpath("post_metadata.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                f"{probe.WRAPPER}\tCPlaneAI__VFunc_01_004d1c10\t"
                f"{probe.TARGETS[probe.WRAPPER]['signature']}\t"
                "CPlaneAI vtable 0x005de73c slot 1 and rebuild parity remain unproven\tOK\n",
                encoding="utf-8",
            )
            base.joinpath("post_tags.tsv").write_text(
                "address\tname\ttags\tstatus\n"
                f"{probe.WRAPPER}\tCPlaneAI__VFunc_01_004d1c10\t\tOK\n",
                encoding="utf-8",
            )
            failures: list[str] = []
            probe.check_metadata(base, failures)
            self.assertTrue(any("stale names remain" in failure for failure in failures))
            self.assertTrue(any("expected name CPlaneAI__scalar_deleting_dtor" in failure for failure in failures))

    def test_vtable_type_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            base.joinpath("post_vtable_slots.tsv").write_text(
                "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\t"
                "containing_entry\tcontaining_name\tstatus\n"
                "005de73c\t1\t005de740\t0x004d1c10\t004d1c10\t004d1c10\t"
                "CPlaneAI__scalar_deleting_dtor\t004d1c10\tCPlaneAI__scalar_deleting_dtor\tOK\n"
                "005d8d1c\t1\t005d8d20\t0x00415060\t00415060\t00415060\t"
                "CUnitAI__scalar_deleting_dtor\t00415060\tCUnitAI__scalar_deleting_dtor\tOK\n",
                encoding="utf-8",
            )
            base.joinpath("post_vtable_types.tsv").write_text(
                "vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\t"
                "raw_type_name\tdemangled_type_name\n"
                "005de73c\t005de738\t006164c8\t0x00000000\t0\t0\t0x00631618\t0x006164b8\t"
                ".?AVCPlaneAI@@\tCUnitAI\n"
                "005d8d1c\t005d8d18\t0060c850\t0x00000000\t0\t0\t0x00623960\t0x0060c840\t"
                ".?AVCUnitAI@@\tCUnitAI\n",
                encoding="utf-8",
            )
            failures: list[str] = []
            probe.check_vtables(base, failures)
            self.assertTrue(any("expected RTTI type CPlaneAI" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main(verbosity=2)
