#!/usr/bin/env python3
"""Tests for the Wave487 CPolyBucket probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_polybucket_wave487_probe as probe


class PolyBucketWave487ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "log.txt"
            path.write_text(
                "updated=17 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n",
                encoding="utf-8",
            )
            self.assertEqual(
                probe.parse_summary(path),
                {
                    "updated": 17,
                    "skipped": 0,
                    "created": 0,
                    "would_create": 0,
                    "renamed": 0,
                    "would_rename": 0,
                    "missing": 0,
                    "bad": 0,
                },
            )

    def test_compact_token_present(self) -> None:
        text = "void * __thiscall CPolyBucket__StartLineSearch(void *this,float *start,float *end)"
        self.assertTrue(
            probe.token_present(
                text,
                "void * __thiscall CPolyBucket__StartLineSearch(void * this, float * start, float * end)",
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
                "0x004d3ce0\tCPolyBucket__TriangleInBucket\t"
                "int __thiscall CPolyBucket__TriangleInBucket(void * this, float * triangle_vertices, int bucket_x, int bucket_y)\t"
                "runtime behavior proven\tOK\n",
                encoding="utf-8",
            )
            failures: list[str] = []
            probe.check_metadata(base, failures)
            self.assertTrue(any("overclaim" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
