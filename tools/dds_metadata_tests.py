# SPDX-License-Identifier: GPL-3.0-only
"""Bounded texture metadata checks using authored bytes only; no game corpus is read."""
from __future__ import annotations

import hashlib
import os
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

import dds_census as census
from dds_census_tests import aya, dds


def change_u32(data: bytes, offset: int, value: int) -> bytes:
    return data[:offset] + struct.pack("<I", value) + data[offset + 4:]


def rgb_dds(layout: str, width: int, height: int, payload: bytes) -> bytes:
    bits, masks = (16, (0x7C00, 0x3E0, 0x1F, 0x8000)) if layout == "A1R5G5B5" else (32, (0xFF0000, 0xFF00, 0xFF, 0xFF000000))
    raw = dds(width, height)
    raw = change_u32(raw, 8, 0x100F)  # required flags plus a tight row pitch
    raw = change_u32(raw, 20, width * bits // 8)
    return raw[:80] + struct.pack("<7I", 0x41, 0, bits, *masks) + raw[108:128] + payload


class TextureMetadataTests(unittest.TestCase):
    def test_complete_dds_and_every_mip_have_exact_byte_identities(self):
        raw = dds(8, 4, mips=4)
        result = census.texture_metadata(raw)
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["source"], {"envelope": "dds", "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        self.assertEqual(result["dds"], {"size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        self.assertEqual(result["stored_format"], "DXT1")
        expected = [(8, 4, 128, 16), (4, 2, 144, 8), (2, 1, 152, 8), (1, 1, 160, 8)]
        self.assertEqual([(m["width"], m["height"], m["offset"], m["length"]) for m in result["mips"]], expected)
        for index, mip in enumerate(result["mips"]):
            self.assertEqual(mip["index"], index)
            self.assertEqual(mip["sha256"], hashlib.sha256(raw[mip["offset"]:mip["offset"] + mip["length"]]).hexdigest())

    def test_a_changed_lower_mip_changes_only_its_mip_identity(self):
        raw = dds(8, 4, mips=4)
        changed = raw[:154] + b"\x01" + raw[155:]
        a, b = census.texture_metadata(raw), census.texture_metadata(changed)
        self.assertNotEqual(a["dds"], b["dds"])
        self.assertEqual([m["sha256"] == n["sha256"] for m, n in zip(a["mips"], b["mips"])], [True, True, False, True])

    def test_member_framing_and_recompression_keep_both_source_and_dds_identity(self):
        raw = dds(8, 4, mips=4)
        envelopes = [aya(raw), aya(raw[:90]) + aya(raw[90:])]
        results = [census.texture_metadata(value, envelope="aya") for value in envelopes]
        self.assertTrue(all(r["status"] == "valid" for r in results))
        self.assertNotEqual(results[0]["source"]["sha256"], results[1]["source"]["sha256"])
        self.assertEqual(results[0]["dds"], results[1]["dds"])
        self.assertEqual(results[0]["mips"], results[1]["mips"])

    def test_all_admitted_stored_formats_have_mip_ranges(self):
        for layout in ("DXT1", "DXT2", "DXT3", "DXT4", "DXT5"):
            with self.subTest(layout=layout):
                result = census.texture_metadata(dds(4, 4, fourcc=layout))
                self.assertEqual(result["status"], "valid")
                self.assertEqual(result["stored_format"], layout)
                self.assertEqual(result["mips"][0]["length"], 8 if layout == "DXT1" else 16)

    def test_tight_rgb_layouts_have_correct_metadata_and_alpha(self):
        for layout, raw, classification in (
            ("A1R5G5B5", rgb_dds("A1R5G5B5", 2, 1, struct.pack("<HH", 0x8000, 0)), "binary"),
            ("A8R8G8B8", rgb_dds("A8R8G8B8", 2, 1, bytes([1, 2, 3, 255, 4, 5, 6, 128])), "graded"),
        ):
            with self.subTest(layout=layout):
                result = census.texture_metadata(raw)
                self.assertEqual((result["status"], result["stored_format"]), ("valid", layout))
                self.assertEqual(result["alpha"]["classification"], classification)
                self.assertEqual(result["header"]["pixel_format"]["bits"], 16 if layout == "A1R5G5B5" else 32)

    def test_alpha_never_counts_dxt1_edge_padding_as_visible_pixels(self):
        # Pixel 0 is opaque, the other 15 stored block texels are transparent.
        raw = dds(1, 1, payload=struct.pack("<HHI", 0, 1, 0xFFFFFFFC))
        result = census.texture_metadata(raw)
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["alpha"]["classification"], "none")
        transparent = dds(1, 1, payload=struct.pack("<HHI", 0, 1, 0xFFFFFFFF))
        self.assertEqual(census.texture_metadata(transparent)["alpha"]["classification"], "binary")

    def test_alpha_never_counts_dxt2_or_dxt3_edge_padding(self):
        for layout in ("DXT2", "DXT3"):
            raw = dds(1, 1, fourcc=layout, payload=bytes([0x7F]) + bytes([0x77]) * 7 + bytes(8))
            with self.subTest(layout=layout):
                self.assertEqual(census.texture_metadata(raw)["alpha"]["classification"], "none")

    def test_dxt2_alpha_dispositions_distinguish_binary_and_graded(self):
        for alpha_bytes, expected in ((bytes([0xFF]) * 8, "none"), (bytes([0xF0]) * 8, "binary"), (bytes([0xF7]) * 8, "graded")):
            raw = dds(4, 4, fourcc="DXT2", payload=alpha_bytes + bytes(8))
            self.assertEqual(census.texture_metadata(raw)["alpha"]["classification"], expected)

    def test_admitted_metadata_does_not_claim_unimplemented_alpha_decoding(self):
        for layout in ("DXT4", "DXT5"):
            result = census.texture_metadata(dds(4, 4, fourcc=layout))
            self.assertEqual(result["status"], "valid")
            self.assertEqual(result["alpha"]["classification"], "unknown")
            self.assertIn("not admitted", result["alpha"]["reason"])

    def test_alpha_work_budget_does_not_discard_valid_stored_metadata(self):
        result = census.texture_metadata(dds(8, 8), limits=census.TextureMetadataLimits(alpha_pixels=16))
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["alpha"]["classification"], "unknown")
        self.assertIn("budget", result["alpha"]["reason"])
        self.assertEqual(len(result["mips"]), 1)

    def assert_bad(self, raw: bytes, message: str, *, envelope: str = "dds"):
        result = census.texture_metadata(raw, envelope=envelope)
        self.assertEqual(result["status"], "malformed", result)
        self.assertEqual(result["mips"], [])
        self.assertEqual(result["source"]["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertTrue(any(message in reason for reason in result["problems"]), result)
        return result

    def test_truncated_magic_header_and_payload_are_malformed(self):
        for raw in (b"", b"DDS ", dds(4, 4)[:100], b"BAD!" + dds(4, 4)[4:]):
            with self.subTest(length=len(raw)):
                self.assert_bad(raw, "DDS")
        self.assert_bad(dds(4, 4)[:-1], "payload")

    def test_trailing_dds_bytes_are_not_hidden(self):
        self.assert_bad(dds(4, 4) + b"extra", "payload")

    def test_required_header_flags_and_capability_are_checked(self):
        raw = dds(4, 4)
        self.assert_bad(change_u32(raw, 8, 0), "required")
        self.assert_bad(change_u32(raw, 108, 0), "required")

    def test_zero_dimensions_and_bad_mip_declarations_are_malformed(self):
        raw = dds(4, 4)
        self.assert_bad(change_u32(raw, 16, 0), "zero")
        self.assert_bad(change_u32(change_u32(raw, 8, 0xA1007), 28, 0), "zero")
        self.assert_bad(change_u32(raw, 28, 2), "flag")
        self.assert_bad(change_u32(change_u32(raw, 8, 0xA1007), 28, 4), "below 1x1")

    def test_payload_and_pitch_capability_inconsistencies_are_malformed(self):
        raw = dds(8, 8, mips=4)
        self.assert_bad(change_u32(raw, 20, 7), "linear size")
        self.assert_bad(change_u32(raw, 108, 0x1000), "capability")
        self.assert_bad(change_u32(raw, 108, 0x401000), "capability")
        rgb = rgb_dds("A8R8G8B8", 2, 1, bytes(8))
        self.assert_bad(change_u32(rgb, 20, 7), "pitch")

    def test_unsupported_formats_and_surfaces_retain_header_and_hash_but_no_mips(self):
        raw = dds(4, 4)
        cases = (raw[:84] + b"DX10" + raw[88:], change_u32(raw, 112, 0x200), change_u32(raw, 24, 2))
        for changed in cases:
            with self.subTest(changed=changed[84:88]):
                result = census.texture_metadata(changed)
                self.assertEqual(result["status"], "unsupported")
                self.assertIsNotNone(result["header"])
                self.assertEqual(result["dds"]["sha256"], hashlib.sha256(changed).hexdigest())
                self.assertEqual(result["mips"], [])

    def test_lowered_dimension_and_mip_limits_are_explicit_unsupported_records(self):
        for limits in (census.TextureMetadataLimits(dimension=4), census.TextureMetadataLimits(mip_levels=2)):
            result = census.texture_metadata(dds(8, 4, mips=4), limits=limits)
            self.assertEqual(result["status"], "unsupported")
            self.assertEqual(result["mips"], [])

    def test_aya_rejects_short_lengths_zero_members_truncated_streams_and_trailing_stream_bytes(self):
        for source, reason in ((b"", "empty"), (b"\x01", "length"), (bytes(4), "length"), (struct.pack("<I", 50) + b"short", "length")):
            self.assert_bad(source, reason, envelope="aya")
        member = zlib.compress(dds(4, 4))
        for altered in (member[:-1], member + b"extra", member + member):
            self.assert_bad(struct.pack("<I", len(altered)) + altered, "member", envelope="aya")
        self.assert_bad(struct.pack("<I", 4) + b"bad!", "zlib", envelope="aya")

    def test_member_count_and_expansion_limits_fail_closed(self):
        source = aya(dds(4, 4)[:64]) + aya(dds(4, 4)[64:])
        result = census.texture_metadata(source, envelope="aya", limits=census.TextureMetadataLimits(members=1))
        self.assertEqual(result["status"], "unsupported")
        self.assertIn("member-count", result["problems"][0])
        bomb = aya(bytes(4096))
        result = census.texture_metadata(bomb, envelope="aya", limits=census.TextureMetadataLimits(dds_bytes=256))
        self.assertEqual(result["status"], "unsupported")
        self.assertIsNone(result["dds"])
        self.assertEqual(result["mips"], [])

    def test_exact_expansion_bound_is_accepted(self):
        raw = dds(4, 4)
        for source, envelope in ((raw, "dds"), (aya(raw), "aya")):
            result = census.texture_metadata(source, envelope=envelope, limits=census.TextureMetadataLimits(dds_bytes=len(raw)))
            self.assertEqual(result["status"], "valid")

    def test_invocation_limits_are_bounded_and_inputs_must_be_immutable(self):
        with self.assertRaises(census.TextureError):
            census.texture_metadata(dds(4, 4), limits=census.TextureMetadataLimits(source_bytes=32))
        for kwargs in ({"dimension": 16385}, {"mip_levels": True}, {"source_bytes": 0}):
            with self.assertRaises(ValueError):
                census.TextureMetadataLimits(**kwargs)
        with self.assertRaises(TypeError):
            census.texture_metadata(bytearray(dds(4, 4)))
        with self.assertRaises(ValueError):
            census.texture_metadata(dds(4, 4), envelope="auto")


class TextureMetadataFileTests(unittest.TestCase):
    def test_same_named_sources_keep_distinct_variants_and_unicode_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            a, b = root / "色彩" / "same.aya", root / "other" / "same.aya"
            a.parent.mkdir()
            b.parent.mkdir()
            raw = dds(4, 4)
            a.write_bytes(aya(raw))
            b.write_bytes(aya(raw[:-1] + b"\x01"))
            left, right = census.read_texture_metadata(a), census.read_texture_metadata(b)
            self.assertEqual((left["status"], right["status"]), ("valid", "valid"))
            self.assertNotEqual(left["source"]["sha256"], right["source"]["sha256"])
            self.assertNotEqual(left["dds"]["sha256"], right["dds"]["sha256"])

    def test_final_symlinks_and_special_files_are_refused_without_reading(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target, link, fifo = root / "target", root / "link", root / "fifo"
            target.write_bytes(aya(dds(4, 4)))
            link.symlink_to(target)
            os.mkfifo(fifo)
            for path in (link, fifo, root):
                with self.subTest(path=path.name), self.assertRaises(census.TextureError):
                    census.read_texture_metadata(path)

    def test_file_source_bound_is_enforced_before_read(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "texture.dds"
            path.write_bytes(dds(4, 4))
            with patch.object(census.os, "read", side_effect=AssertionError("must not read")):
                with self.assertRaises(census.TextureError):
                    census.read_texture_metadata(path, envelope="dds", limits=census.TextureMetadataLimits(source_bytes=32))

    def test_changed_bytes_while_fd_is_open_are_refused_even_with_restored_mtime(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "texture.dds"
            original = dds(4, 4)
            path.write_bytes(original)
            before = path.stat()
            real_read = os.read
            changed = False

            def read_then_change(fd, size):
                nonlocal changed
                value = real_read(fd, size)
                if not changed:
                    changed = True
                    path.write_bytes(original[:-1] + b"\x01")
                    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
                return value

            with patch.object(census.os, "read", side_effect=read_then_change), self.assertRaises(census.TextureError):
                census.read_texture_metadata(path, envelope="dds")

    def test_path_replacement_during_inspection_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path, replacement = root / "texture.dds", root / "replacement.dds"
            path.write_bytes(dds(4, 4))
            replacement.write_bytes(dds(4, 4))
            real_inspect = census.texture_metadata

            def inspect_then_replace(*args, **kwargs):
                result = real_inspect(*args, **kwargs)
                replacement.replace(path)
                return result

            with patch.object(census, "texture_metadata", side_effect=inspect_then_replace), self.assertRaises(census.TextureError):
                census.read_texture_metadata(path, envelope="dds")


if __name__ == "__main__":
    unittest.main()
