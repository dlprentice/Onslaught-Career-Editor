#!/usr/bin/env python3
"""Unit tests for the Wave483 CPlane init probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_plane_init_wave483_probe as probe


class PlaneInitWave483ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.log"
            path.write_text(
                "updated=1 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n",
                encoding="utf-8",
            )
            self.assertEqual(
                probe.parse_summary(path),
                {
                    "updated": 1,
                    "skipped": 0,
                    "created": 0,
                    "would_create": 0,
                    "renamed": 0,
                    "would_rename": 0,
                    "missing": 0,
                    "bad": 0,
                },
            )

    def test_stale_this_flag_claim_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for filename, expected in probe.EXPECTED_SUMMARIES.items():
                base.joinpath(filename).write_text(
                    "REPORT: Save succeeded\n"
                    f"updated={expected['updated']} skipped={expected['skipped']} created={expected['created']} "
                    f"would_create={expected['would_create']} renamed={expected['renamed']} "
                    f"would_rename={expected['would_rename']} missing={expected['missing']} bad={expected['bad']}\n",
                    encoding="utf-8",
                )
            base.joinpath("post_metadata.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                f"{probe.TARGET}\t{probe.TARGET_NAME}\t{probe.EXPECTED_SIGNATURE}\t"
                "marks this+0x80 before CAirUnit__Init and rebuild parity remain unproven\tOK\n",
                encoding="utf-8",
            )
            failures: list[str] = []
            probe.check_metadata(base, failures)
            self.assertTrue(any("stale this+0x80" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main(verbosity=2)
