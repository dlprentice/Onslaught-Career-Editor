import struct
import tempfile
import unittest
from pathlib import Path

import patcher
from tests_shared.fixture_paths import REPO_ROOT, SAVE_FIXTURE


def _read_u32(buf: bytes, offset: int) -> int:
    return struct.unpack_from("<I", buf, offset)[0]


class SavePatchRegressionTests(unittest.TestCase):
    def test_tail_settings_offsets_and_boolean_polarity(self):
        self.assertTrue(SAVE_FIXTURE.exists(), f"Missing fixture: {SAVE_FIXTURE}")

        with tempfile.TemporaryDirectory(prefix="onslaught-py-regression-") as td:
            td_path = Path(td)
            input_path = td_path / "input.bes"
            output_path = td_path / "output.bes"
            input_path.write_bytes(SAVE_FIXTURE.read_bytes())

            patcher.patch_file(
                input_path=input_path,
                output_path=output_path,
                patch_nodes=False,
                patch_links=False,
                patch_goodies=False,
                patch_kills=False,
                invert_y_p1=True,
                invert_y_p2=False,
                invert_flight_p1=False,
                invert_flight_p2=True,
                vibration_p1=True,
                vibration_p2=False,
                controller_config_p1=123,
                controller_config_p2=456,
            )

            buf = output_path.read_bytes()
            self.assertEqual(_read_u32(buf, 0x249E), 0)  # Flight P1 OFF
            self.assertEqual(_read_u32(buf, 0x24A2), 1)  # Flight P2 ON
            self.assertEqual(_read_u32(buf, 0x24A6), 1)  # Walker P1 ON
            self.assertEqual(_read_u32(buf, 0x24AA), 0)  # Walker P2 OFF
            self.assertEqual(_read_u32(buf, 0x24AE), 1)  # Vibration P1 ON
            self.assertEqual(_read_u32(buf, 0x24B2), 0)  # Vibration P2 OFF
            self.assertEqual(_read_u32(buf, 0x24B6), 123)
            self.assertEqual(_read_u32(buf, 0x24BA), 456)

    def test_level_rank_parser_is_zero_based(self):
        valid_ranks = set(patcher.RANK_FLOAT_BITS.keys())
        parsed, warnings = patcher.parse_level_rank_entries(["1:S", "43:E"], valid_ranks)
        self.assertFalse(warnings)
        self.assertIsNotNone(parsed)
        self.assertIn(0, parsed)
        self.assertIn(42, parsed)
        self.assertEqual(parsed[0], "S")
        self.assertEqual(parsed[42], "E")

    def test_goodies_patch_includes_slot_232_and_preserves_reserved_slots(self):
        self.assertTrue(SAVE_FIXTURE.exists(), f"Missing fixture: {SAVE_FIXTURE}")

        with tempfile.TemporaryDirectory(prefix="onslaught-py-goodies-") as td:
            td_path = Path(td)
            input_path = td_path / "input.bes"
            output_path = td_path / "output.bes"
            input_path.write_bytes(SAVE_FIXTURE.read_bytes())
            before = input_path.read_bytes()

            patcher.patch_file(
                input_path=input_path,
                output_path=output_path,
                patch_nodes=False,
                patch_links=False,
                patch_goodies=True,
                patch_kills=False,
                new_goodies=False,
            )

            after = output_path.read_bytes()
            slot_232_off = patcher.GOODIE_BASE + (232 * 4)
            self.assertEqual(_read_u32(after, slot_232_off), patcher.GOODIE_OLD)

            for idx in range(patcher.GOODIE_DISPLAYABLE_COUNT, patcher.GOODIE_COUNT):
                off = patcher.GOODIE_BASE + (idx * 4)
                self.assertEqual(
                    _read_u32(after, off),
                    _read_u32(before, off),
                    f"Reserved goodie slot {idx} was modified unexpectedly",
                )

    def test_kill_patch_preserves_meta_high_byte(self):
        self.assertTrue(SAVE_FIXTURE.exists(), f"Missing fixture: {SAVE_FIXTURE}")

        with tempfile.TemporaryDirectory(prefix="onslaught-py-killmeta-") as td:
            td_path = Path(td)
            input_path = td_path / "input.bes"
            output_path = td_path / "output.bes"
            buf = bytearray(SAVE_FIXTURE.read_bytes())

            seeded_meta = [0xA1, 0xB2, 0xC3, 0xD4, 0xE5]
            for i, meta in enumerate(seeded_meta):
                off = patcher.KILLS_BASE + (i * 4)
                struct.pack_into("<I", buf, off, (meta << 24) | 7)
            input_path.write_bytes(bytes(buf))

            patcher.patch_file(
                input_path=input_path,
                output_path=output_path,
                patch_nodes=False,
                patch_links=False,
                patch_goodies=False,
                patch_kills=True,
                kill_count=123,
            )

            after = output_path.read_bytes()
            for i, meta in enumerate(seeded_meta):
                off = patcher.KILLS_BASE + (i * 4)
                raw = _read_u32(after, off)
                self.assertEqual((raw >> 24) & 0xFF, meta, f"Meta byte changed for kill slot {i}")
                self.assertEqual(raw & 0x00FFFFFF, 123, f"Kill payload mismatch for slot {i}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
