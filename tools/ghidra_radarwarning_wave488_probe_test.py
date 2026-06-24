#!/usr/bin/env python3
"""Tests for the Wave488 CRadarWarningReceiver probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_radarwarning_wave488_probe as probe


class RadarWarningWave488ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "log.txt"
            path.write_text(
                "updated=5 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n",
                encoding="utf-8",
            )
            self.assertEqual(
                probe.parse_summary(path),
                {
                    "updated": 5,
                    "skipped": 0,
                    "created": 1,
                    "would_create": 0,
                    "renamed": 0,
                    "would_rename": 0,
                    "missing": 0,
                    "bad": 0,
                },
            )

    def test_compact_token_present(self) -> None:
        text = "void __thiscall CRadarWarningReceiver__Init(void *this,void *config_record)"
        self.assertTrue(
            probe.token_present(
                text,
                "void __thiscall CRadarWarningReceiver__Init(void * this, void * config_record)",
            )
        )

    def test_overclaim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "post-decomp").mkdir()
            for filename, summary in probe.EXPECTED_SUMMARIES.items():
                (base / filename).write_text(
                    "REPORT: Save succeeded\n"
                    + "updated={updated} skipped={skipped} created={created} would_create={would_create} "
                    + "renamed={renamed} would_rename={would_rename} missing={missing} bad={bad}\n".format(**summary),
                    encoding="utf-8",
                )
            (base / "post_metadata.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x004d66b0\tCRadarWarningReceiver__Update\t"
                "void __fastcall CRadarWarningReceiver__Update(void * this)\t"
                "runtime behavior proven\tOK\n",
                encoding="utf-8",
            )
            failures: list[str] = []
            probe.check_metadata(base, failures)
            self.assertTrue(any("overclaim" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
