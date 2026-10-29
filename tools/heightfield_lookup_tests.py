#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks for tools/heightfield_lookup.py on authored terrain (no game bytes): the lookup is the game's rule (an 8.8 fixed-point
read of a biased float, four samples interpolated with arithmetic shifts, 0.0 outside 0 to 512), the ERES reader agrees with the
catalogue's decoder, and a damaged payload is refused."""
from __future__ import annotations

import math
import random
import struct
import unittest

import heightfield_lookup as hf
import world_resources_decode as wrd


def eres_with_heightfield(samples: list[int] | tuple[int, ...], scale: float, water: float = 0.0, mixer_data: bool = False) -> bytes:
    """
    An authored ERES payload (CEngine::Deserialize's layout) holding the given height samples. With mixer_data the one mixer mip and
    the one mixer slot that carry optional data (the loader reads it when their pointers are not 0) do: the second mip has two
    textures of 6 bytes and two extra 1,024-byte blocks, and the sixth slot has 3 entries of 81 bytes. A reader that gets a size or an
    offset of those wrong does not end where the payload ends.
    """
    assert len(samples) == hf.SAMPLE_COUNT
    header = lambda tag, size=0: tag + struct.pack("<I", size)
    out = header(b"ENGN") + struct.pack("<i", 7)
    for mip in range(7):
        carries = mixer_data and mip == 1
        out += header(b"MTEX") + header(b"DATA") + struct.pack("<IiIhxxiii6i6i", 1 if carries else 0, 0, 1 if carries else 0, 3, 6 if carries else 0, 2 if carries else 0, 0, *([0] * 12))
        if carries:
            out += header(b"TXDT") + bytes(2 * 6) + header(b"TXEX") + bytes(2 * 1024)
    out += header(b"MAP ") + struct.pack("<i", 7) + header(b"HFLD") + header(b"DATA")
    record = bytearray(wrd.HEIGHTFIELD_SIZE)
    struct.pack_into("<f", record, hf.SCALE_AT, scale)
    struct.pack_into("<f", record, hf.WATER_AT, water)
    record[0x1030] = 3
    record[0x1078 + 0x18], record[0x1078 + 0x1C], record[0x1078 + 0x1D] = 2, 1, 4
    out += bytes(record) + header(b"HGTS") + struct.pack(f"<{hf.SAMPLE_COUNT}h", *samples)
    out += header(b"MIXR")
    for slot in range(wrd.MIXER_MAP_SLOTS):
        carries = mixer_data and slot == 5
        entry = bytearray(wrd.MIXER_SLOT_SIZE)
        if carries:
            struct.pack_into("<iI", entry, 0, 3, 1)
        out += header(b"SLOT") + header(b"DATA") + bytes(entry)
        if carries:
            out += header(b"SDAT") + bytes(3 * 81)
    return out + header(b"MMAP") + bytes(wrd.MIXER_MAP_SIZE)


def at(tile_x: int, tile_y: int, row: int, column: int) -> int:
    """The index of a sample: tiles are X-major, a tile's rows run along Y and its columns along X."""
    return ((tile_x * hf.TILES + tile_y) * hf.TILE_SAMPLES + row) * hf.TILE_SAMPLES + column


def ramp_samples() -> list[int]:
    """Tile 0 holds 1000 x row + 10 x column; tile (1, 0) 7000 + column; tile (0, 1) 9000 + 10 x row; tile (5, 2) and (2, 5) differ."""
    samples = [0] * hf.SAMPLE_COUNT
    for row in range(9):
        for column in range(9):
            samples[at(0, 0, row, column)] = 1000 * row + 10 * column
            samples[at(1, 0, row, column)] = 7000 + column
            samples[at(0, 1, row, column)] = 9000 + 10 * row
            samples[at(5, 2, row, column)] = 100 * row + column
            samples[at(2, 5, row, column)] = -(100 * row + column)
    samples[at(0, 0, 0, 8)] = 5000  # the ninth column of tile 0
    samples[at(0, 0, 0, 0)], samples[at(0, 0, 0, 1)] = 100, 99  # a step down
    samples[at(63, 63, 8, 8)] = 4242  # the last sample of the last tile
    return samples


class MixerDataTests(unittest.TestCase):
    def test_optional_mixer_data_is_walked_to_the_same_terrain(self) -> None:
        plain = eres_with_heightfield(ramp_samples(), 0.5, -2.0)
        carrying = eres_with_heightfield(ramp_samples(), 0.5, -2.0, mixer_data=True)
        self.assertEqual(len(carrying) - len(plain), 2 * 6 + 2 * 1024 + 3 * 81 + 3 * 8)  # a mip's textures and extra blocks, a slot's entries, and their three headers
        self.assertEqual(hf.read_heightfield(carrying), hf.read_heightfield(plain))
        self.assertEqual(hf.read_heightfield(carrying).samples_sha256(), hf.read_heightfield(plain).samples_sha256())

    def test_a_texture_count_that_cannot_be_walked_is_refused(self) -> None:
        carrying = bytearray(eres_with_heightfield(ramp_samples(), 0.5, -2.0, mixer_data=True))
        # the second mip's map record starts after ENGN (8), the count (4), one plain mip (8 + 8 + 0x4C) and the MTEX and DATA headers (16)
        record = 12 + 8 + 8 + 0x4C + 16
        struct.pack_into("<i", carrying, record + 20, -5)
        with self.assertRaises(hf.DecodeError):
            hf.read_heightfield(bytes(carrying))
        struct.pack_into("<i", carrying, record + 20, 2)
        struct.pack_into("<i", carrying, record + 16, 7)  # a texture size that no longer matches the bytes that follow
        with self.assertRaises(hf.DecodeError):
            hf.read_heightfield(bytes(carrying))


class LookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scale = hf.f32(0.0009155273)
        cls.field = hf.Heightfield(tuple(ramp_samples()), cls.scale, hf.f32(-1.5))

    def test_the_bias_is_the_games_constant_and_turns_rounding_into_flooring(self) -> None:
        self.assertEqual(struct.unpack("<I", struct.pack("<f", hf.BIAS))[0], 0x3AFFFEB0)
        self.assertEqual(hf.packed(0.0), 0x47400000)
        rng = random.Random(1)
        for _ in range(2000):
            value = hf.f32(rng.uniform(0, 511.99))
            fraction = (value * 256) % 1
            if 0.99990 < fraction or fraction < 0.00002:
                continue  # the one place a round-to-nearest of the biased float is not a floor
            self.assertEqual(hf.packed(value) - 0x47400000, math.floor(value * 256), value)

    def test_whole_positions_read_one_sample_scaled(self) -> None:
        for x, y in ((0, 0), (3, 2), (7, 7), (6, 4)):
            samples = self.field.samples
            expected = hf.f32(float(samples[at(0, 0, y, x)]) * self.scale)
            self.assertEqual(hf.height_at(self.field, float(x), float(y)), expected, (x, y))
        self.assertEqual(hf.height_at(self.field, 3.0, 2.0), hf.f32(2030.0 * self.scale))

    def test_a_position_between_samples_interpolates_with_eight_bit_fractions(self) -> None:
        # Halfway along X at row 2 between 2030 and 2040; halfway along Y at column 3 between 2030 and 3030.
        self.assertEqual(hf.height_at(self.field, 3.5, 2.0), hf.f32(2035.0 * self.scale))
        self.assertEqual(hf.height_at(self.field, 3.0, 2.5), hf.f32(2530.0 * self.scale))
        # Both halves: top 2035, bottom 3035, so 2535.
        self.assertEqual(hf.height_at(self.field, 3.5, 2.5), hf.f32(2535.0 * self.scale))
        # A quarter and three quarters: 256ths round down in the shifts.
        self.assertEqual(hf.height_at(self.field, 3.25, 2.0), hf.f32(2032.0 * self.scale))  # 2030 + (10 * 64 >> 8) = 2032
        self.assertEqual(hf.height_at(self.field, 3.75, 2.0), hf.f32(2037.0 * self.scale))  # 2030 + (10 * 192 >> 8) = 2037

    def test_a_step_down_rounds_down(self) -> None:
        # Samples 100 then 99: halfway is 100 + (-1 * 128 >> 8) = 99, not 100 (an arithmetic shift of a negative step).
        self.assertEqual(hf.height_at(self.field, 0.5, 0.0), hf.f32(99.0 * self.scale))
        self.assertEqual(hf.interpolate(self.field.samples, hf.packed(0.5), hf.packed(0.0)), 99)

    def test_tiles_are_x_major_and_a_tile_has_nine_samples_a_side(self) -> None:
        self.assertEqual(hf.height_at(self.field, 8.0, 0.0), hf.f32(7000.0 * self.scale))  # tile (1, 0), sample (0, 0)
        self.assertEqual(hf.height_at(self.field, 0.0, 8.0), hf.f32(9000.0 * self.scale))  # tile (0, 1)
        self.assertEqual(hf.height_at(self.field, 41.0, 17.0), hf.f32(float(100 * 1 + 1) * self.scale))  # tile (5, 2), sample (row 1, column 1)
        self.assertEqual(hf.height_at(self.field, 17.0, 41.0), hf.f32(float(-(100 * 1 + 1)) * self.scale))  # tile (2, 5)
        # Inside tile 0 the ninth column is read for x between 7 and 8.
        self.assertEqual(hf.height_at(self.field, 7.5, 0.0), hf.f32(float(70 + ((5000 - 70) * 128 >> 8)) * self.scale))

    def test_the_square_is_zero_to_512_and_nothing_outside_it_is_read(self) -> None:
        # The last cell reads tile (63, 63) up to its ninth sample, 4242: at 511.99 (253 of 256 along each axis) that is
        # bottom = 4242 * 253 >> 8 = 4192, then 4192 * 253 >> 8 = 4142; at 511.998 (255 of 256) it is 4225 and then 4208.
        self.assertEqual(hf.height_at(self.field, 511.99, 511.99), hf.f32(4142.0 * self.scale))
        self.assertEqual(hf.packed(511.99) - 0x47400000, 131069)
        self.assertEqual(hf.packed(511.998) - 0x47400000, 131071)
        self.assertEqual(hf.height_at(self.field, 511.998, 511.998), hf.f32(4208.0 * self.scale))
        # Near 512 a float's own spacing (1/32768) is larger than the bias's margin, so a position exactly on a 256th can land on the
        # one before it; the port repeats that exactly.
        self.assertEqual(hf.packed(511.99609375) - 0x47400000, 131070)
        self.assertEqual(hf.height_at(self.field, 511.0, 511.0), 0.0)  # the sample at (511, 511) is 0: only the ninth is set
        for x, y in ((512.0, 0.0), (0.0, 512.0), (512.004, 100.0), (-0.001, 3.0), (3.0, -0.001), (-1.0, -1.0), (600.0, 600.0), (-512.0, 4.0)):
            self.assertEqual(hf.height_at(self.field, x, y), 0.0, (x, y))
        self.assertEqual(hf.height_at(self.field, -0.0, 0.0), hf.height_at(self.field, 0.0, 0.0))  # a negative zero is zero
        for bad in (math.nan, math.inf, -math.inf, 1e39):
            self.assertEqual(hf.height_at(self.field, bad, 5.0), 0.0)
            self.assertEqual(hf.height_at(self.field, 5.0, bad), 0.0)

    def test_the_height_bits_tell_a_negative_zero_from_a_zero(self) -> None:
        negative = hf.Heightfield(self.field.samples, hf.f32(-0.001), 0.0)
        self.assertEqual(hf.height_bits(negative, 3.0, 2.0), struct.unpack("<I", struct.pack("<f", hf.f32(2030.0 * hf.f32(-0.001))))[0])
        self.assertEqual(hf.height_bits(negative, 600.0, 0.0), 0)


class ReaderTests(unittest.TestCase):
    def test_the_reader_agrees_with_the_catalogues_decoder(self) -> None:
        samples = ramp_samples()
        payload = eres_with_heightfield(samples, hf.f32(0.0009155273), hf.f32(-1.5))
        field = hf.read_heightfield(payload)
        summary = wrd.parse_eres(payload)["heightField"]
        self.assertEqual(field.samples_sha256(), summary["samplesSha256"])
        self.assertEqual((field.scale, field.water), (summary["heightScale"], summary["waterLevel"]))
        self.assertEqual(list(field.samples), samples)

    def test_a_damaged_payload_is_refused(self) -> None:
        payload = eres_with_heightfield(ramp_samples(), 0.001)
        for damaged in (payload[:-1], payload + b"\0", b"XXXX" + payload[4:], payload[:100], b""):
            with self.assertRaises(hf.DecodeError):
                hf.read_heightfield(damaged)
        with self.assertRaises(hf.DecodeError):
            hf.read_heightfield(payload[:8] + struct.pack("<i", 6) + payload[12:])


if __name__ == "__main__":
    unittest.main()
