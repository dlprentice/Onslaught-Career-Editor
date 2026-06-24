#!/usr/bin/env python3
"""Focused tests for curated release manifest generation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import release_curated_manifest as manifest
from release_profile_snapshot import Classification


class ReleaseCuratedManifestTests(unittest.TestCase):
    def test_filter_public_rows_excludes_non_r0_rows(self) -> None:
        rows = [
            ("safe.md", Classification("safe.md", "R0_ALLOW", "default")),
            (
                "private.md",
                Classification("private.md", "R4_DENY", "private-ghidra-backup-root"),
            ),
        ]

        public_rows, excluded_rows = manifest.filter_public_rows(rows)

        self.assertEqual([path for path, _cls in public_rows], ["safe.md"])
        self.assertEqual([path for path, _cls in excluded_rows], ["private.md"])

    def test_write_allowlist_uses_lf_newlines_on_windows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "public_candidate_allowlist.tsv"

            manifest.write_allowlist(
                out_path,
                [
                    (
                        "release/readiness/example.md",
                        Classification("release/readiness/example.md", "R0_ALLOW", "default"),
                    )
                ],
            )

            raw = out_path.read_bytes()

        self.assertIn(b"\n", raw)
        self.assertNotIn(b"\r\n", raw)

    def test_exclude_patterns_remove_included_paths_when_no_exact_override_exists(self) -> None:
        selected = manifest.select_manifest_files(
            ["tools/runtime-probes/example.py"],
            include_patterns=["tools/**"],
            exclude_patterns=["tools/runtime-probes/**"],
        )

        self.assertEqual(selected, [])


if __name__ == "__main__":
    unittest.main()
