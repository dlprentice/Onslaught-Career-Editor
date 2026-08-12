#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_ghidra_name_projection.py"
SPEC = importlib.util.spec_from_file_location("re_ghidra_name_projection", TOOL)
assert SPEC and SPEC.loader
projection = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(projection)


HEADER = "address\tname\tbodyMin\tbodyMax\n"


class ProjectionTests(unittest.TestCase):
    def write_inventory(self, root: Path, body: str) -> tuple[Path, str]:
        path = root / "functions.tsv"
        raw = (HEADER + body).encode("utf-8")
        path.write_bytes(raw)
        return path, hashlib.sha256(raw).hexdigest()

    def render(self, inventory: Path, digest: str) -> bytes:
        return projection.projection_bytes(
            inventory,
            expected_inventory_sha256=digest,
            source_label="sealed/functions.tsv",
            projection_date="2026-08-12",
            specimen_sha256="74" * 32,
        )

    def test_projection_is_sorted_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            inventory, digest = self.write_inventory(
                Path(raw_root),
                "0x00401000\tFirst\t0x00401000\t0x00401003\n"
                "0x00401010\tSecond\t0x00401010\t0x0040101f\n",
            )
            first = self.render(inventory, digest)
            second = self.render(inventory, digest)
            self.assertEqual(first, second)
            self.assertIn(b"# Rows    : 2 internal functions", first)
            self.assertTrue(first.endswith(b"0x00401010\tSecond\t0x00401010\t0x0040101f\n"))

    def test_wrong_inventory_digest_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            inventory, _ = self.write_inventory(
                Path(raw_root), "0x00401000\tFirst\t0x00401000\t0x00401003\n"
            )
            with self.assertRaisesRegex(projection.ProjectionError, "SHA-256 differs"):
                self.render(inventory, "00" * 32)

    def test_duplicate_or_unsorted_addresses_are_refused(self) -> None:
        cases = (
            "0x00401000\tFirst\t0x00401000\t0x00401003\n"
            "0x00401000\tAgain\t0x00401000\t0x00401003\n",
            "0x00401010\tSecond\t0x00401010\t0x0040101f\n"
            "0x00401000\tFirst\t0x00401000\t0x00401003\n",
        )
        for body in cases:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as raw_root:
                inventory, digest = self.write_inventory(Path(raw_root), body)
                with self.assertRaises(projection.ProjectionError):
                    self.render(inventory, digest)

    def test_entry_outside_body_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            inventory, digest = self.write_inventory(
                Path(raw_root), "0x00401010\tBad\t0x00401000\t0x0040100f\n"
            )
            with self.assertRaisesRegex(projection.ProjectionError, "outside body"):
                self.render(inventory, digest)


if __name__ == "__main__":
    unittest.main()
