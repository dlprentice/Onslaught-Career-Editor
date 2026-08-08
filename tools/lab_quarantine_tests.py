#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import lab_quarantine as quarantine


class LabQuarantineTests(unittest.TestCase):
    def quarantine_paths(self, root: Path):
        quarantine_root = root / "quarantine"
        quarantine_root.mkdir()
        return mock.patch.multiple(
            quarantine,
            QUARANTINE_ROOT=quarantine_root,
            MANIFEST=quarantine_root / "manifest.jsonl",
            PURGE_LOG=quarantine_root / "purge.log",
        )

    def test_stage_file_verifies_copy_records_receipt_and_removes_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source" / "marker.txt"
            source.parent.mkdir()
            source.write_bytes(b"recoverable evidence\n")

            with self.quarantine_paths(root):
                row = quarantine.stage(source, reason="test recovery")

                staged = Path(row["staged"])
                self.assertFalse(source.exists())
                self.assertEqual(b"recoverable evidence\n", staged.read_bytes())
                self.assertEqual(21, row["bytes"])
                self.assertEqual(
                    hashlib.sha256(b"recoverable evidence\n").hexdigest(),
                    row["sha256"],
                )
                recorded = [
                    json.loads(line)
                    for line in quarantine.MANIFEST.read_text(encoding="utf-8").splitlines()
                ]
                self.assertEqual([row], recorded)

    def test_stage_directory_then_restore_round_trips_exact_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source-tree"
            (source / "nested").mkdir(parents=True)
            (source / "a.bin").write_bytes(b"a")
            (source / "nested" / "b.bin").write_bytes(b"bc")
            expected_sha = quarantine.tree_sha256(source)

            with self.quarantine_paths(root):
                row = quarantine.stage(source, reason="test tree")
                self.assertFalse(source.exists())
                self.assertEqual(3, row["bytes"])
                self.assertEqual(expected_sha, row["sha256"])

                restored = quarantine.restore(row["id"])
                self.assertEqual(row, restored)
                self.assertTrue(source.is_dir())
                self.assertEqual(expected_sha, quarantine.tree_sha256(source))
                self.assertEqual("", quarantine.MANIFEST.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
