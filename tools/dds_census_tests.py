# SPDX-License-Identifier: MIT
"""Checks the texture census on synthetic DDS files in an AYA envelope (no game bytes)."""
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

import dds_census as census


def dds(width, height, fourcc="DXT1", mips=1, payload=None, pitch=None, caps1=None):
    flags = 0x1007 | 0x80000 | (0x20000 if mips > 1 else 0)
    chain = census.chain({"flags": flags, "mips": mips, "width": width, "height": height, "layout": fourcc})
    top = chain[0][2]
    head = b"DDS " + struct.pack("<7I", 124, flags, height, width, top if pitch is None else pitch, 0, mips)
    head += bytes(44) + struct.pack("<2I", 32, 4) + fourcc.encode() + bytes(20)
    head += struct.pack("<2I", (0x1000 | (0x400008 if mips > 1 else 0)) if caps1 is None else caps1, 0) + bytes(12)
    assert len(head) == 128
    body = bytes(sum(size for _, _, size in chain)) if payload is None else payload
    return head + body


def aya(data):
    member = zlib.compress(data)
    return struct.pack("<I", len(member)) + member


class CensusTests(unittest.TestCase):
    def run_census(self, data):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "t.aya"
            path.write_bytes(aya(data))
            return census.census(path)

    def test_a_full_chain_matches_its_payload(self):
        row = self.run_census(dds(8, 4, mips=4))
        self.assertEqual((row["layout"], row["levels"], row["problems"]), ("DXT1", 4, []))
        self.assertTrue(row["full_chain"])

    def test_a_short_payload_is_reported(self):
        row = self.run_census(dds(8, 8, mips=1, payload=bytes(10)))
        self.assertTrue(any("payload" in p for p in row["problems"]))

    def test_a_wrong_linear_size_is_reported(self):
        row = self.run_census(dds(8, 8, pitch=7))
        self.assertTrue(any("linear size" in p for p in row["problems"]))

    def test_a_mipmap_cap_without_mips_is_reported(self):
        row = self.run_census(dds(8, 8, caps1=0x401008))
        self.assertTrue(any("mipmap cap" in p for p in row["problems"]))

    def test_dxt1_transparent_blocks_count_as_binary_alpha(self):
        # c0 <= c1 with a selector of 3 is DXT1's transparent texel.
        block = struct.pack("<HHI", 0, 1, 0xFFFFFFFF)
        self.assertEqual(census.alpha_use("DXT1", block, 4, 4), "binary")
        self.assertEqual(census.alpha_use("DXT1", struct.pack("<HHI", 1, 0, 0xFFFFFFFF), 4, 4), "none")

    def test_dxt2_alpha_is_classified(self):
        opaque = b"\xff" * 8 + bytes(8)
        graded = bytes([0x7F] * 8) + bytes(8)
        self.assertEqual(census.alpha_use("DXT2", opaque, 4, 4), "none")
        self.assertEqual(census.alpha_use("DXT2", graded, 4, 4), "graded")


if __name__ == "__main__":
    unittest.main()
