# SPDX-License-Identifier: GPL-3.0-only
"""Checks the sample-bank walker and decoder on synthetic banks (no game bytes)."""
import struct
import unittest

import xap_bank_walk as walker


def bank(samples):
    """A PCXP bank of (name, pcm_bytes, adpcm bytes) samples."""
    data = b"PCXP" + struct.pack("<i", len(samples))
    for name, size, packed in samples:
        data += b"PSMP" + name.encode().ljust(64, b"\0") + struct.pack("<I", size) + packed
    return data


class BankTests(unittest.TestCase):
    def test_a_bank_parses_to_its_end(self):
        magic, samples = walker.read_bank(bank([("Hud\\beep", 8, bytes(2)), ("Hud\\boop", 4, bytes(1))]))
        self.assertEqual(magic, "PCXP")
        self.assertEqual([(n, s) for n, s, _ in samples], [("Hud\\beep", 8), ("Hud\\boop", 4)])

    def test_trailing_bytes_are_refused(self):
        with self.assertRaises(walker.BankError):
            walker.read_bank(bank([("a", 4, bytes(1))]) + b"\0")

    def test_a_sample_past_the_end_is_refused(self):
        with self.assertRaises(walker.BankError):
            walker.read_bank(bank([("a", 400, bytes(1))]))

    def test_the_high_nibble_decodes_first(self):
        # Code 4 then code 0: +7 (step 7, bit 2), index 2; then +1 (step 9 >> 3).
        pcm = walker.decode_ima(bytes([0x40]), 2)
        self.assertEqual(struct.unpack("<2h", pcm), (7, 8))

    def test_negative_codes_and_clamping(self):
        # Code 12 (sign + bit 2) from zero: -7, and the prediction never leaves 16 bits.
        self.assertEqual(struct.unpack("<h", walker.decode_ima(bytes([0xC0]), 1))[0], -7)
        loud = walker.decode_ima(bytes([0x77] * 400), 800)
        self.assertEqual(max(struct.unpack(f"<{800}h", loud)), 32767)


if __name__ == "__main__":
    unittest.main()
