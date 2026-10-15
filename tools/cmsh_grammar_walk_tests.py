# SPDX-License-Identifier: MIT
"""Checks the CMSH grammar walker on small synthetic streams (no game bytes)."""
import collections
import struct
import unittest
import zlib

import cmsh_grammar_walk as walker


def chunk(tag: str, payload: bytes = b"", size: int | None = None) -> bytes:
    return tag.encode() + struct.pack("<I", len(payload) if size is None else size) + payload


def record(size: int, fields: dict[int, int]) -> bytes:
    data = bytearray(size)
    for offset, value in fields.items():
        struct.pack_into("<i", data, offset, value)
    return bytes(data)


def box() -> bytes:
    inner = chunk("BBOX", bytes(40))
    return chunk("BBOX", inner)


def part(pieces: int = 0) -> bytes:
    fields = {0xB8: 2, 0xBC: 1, 0x10C: 1, 0xC8: 1}  # two virtual frames, one frame with orientation and position
    body = chunk("CMSP", record(walker.PART_RECORD, fields))
    body += box()
    body += chunk("VHFM", bytes(2)) + chunk("HORI", bytes(48)) + chunk("HPOS", bytes(16))
    vb = record(walker.VB_RECORD, {0x108: pieces, 0x114: 36})
    inner = chunk("CMVB", vb)
    for piece in range(pieces):
        inner += chunk("MMPT", struct.pack("<6i", 108, 8, 4, 3, 2, 1))
        inner += chunk("IBUF", struct.pack("<4H", 0, 1, 2, 2))
        inner += chunk("VBUF", bytes(36 * 3))
        inner += chunk("TEXR", struct.pack("<6i", 0, -1, -1, -1, -1, -1))
    body += chunk("PMVB", inner)
    return chunk("MESP", body)


def mesh(parts: int = 1, pieces: int = 0) -> bytes:
    stream = chunk("CMSH", record(walker.MESH_RECORD, {0x15C: parts})) + chunk("CMST")
    stream += b"".join(part(pieces) for _ in range(parts))
    return stream + box()


def animated_mesh(cached_child_position: tuple[float, float, float]) -> bytes:
    """A root part keyed at (1, 0, 0) and a child turned 90 degrees about Z, keyed at (0, 2, 0) relative to it."""
    rotate = struct.pack("<12f", 0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0)
    identity = struct.pack("<12f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0)

    def keyed(orientation: bytes, position: tuple, parent: int | None, cached: tuple) -> bytes:
        fields = {0xB8: 1, 0xBC: 1, 0x10C: 1, 0xC8: 1, 0x104: 1, 0x118: 1}
        if parent is not None:
            fields[0x98] = 1
        body = chunk("CMSP", record(walker.PART_RECORD, fields))
        if parent is not None:
            body += chunk("PRNT", struct.pack("<i", parent))
        body += box() + chunk("VHFM", bytes(1)) + chunk("HORI", orientation)
        body += chunk("HPOS", struct.pack("<4f", *position, 0)) + chunk("CPOS", struct.pack("<4f", *cached, 0))
        body += chunk("PMVB", chunk("CMVB", record(walker.VB_RECORD, {})))
        return chunk("MESP", body)

    stream = chunk("CMSH", record(walker.MESH_RECORD, {0x15C: 2})) + chunk("CMST")
    stream += keyed(rotate, (1, 0, 0), None, (1, 0, 0))
    stream += keyed(identity, (0, 2, 0), 0, cached_child_position)
    return stream + box()


class WalkTests(unittest.TestCase):
    def walk(self, data: bytes) -> dict:
        slots = collections.defaultdict(collections.Counter)
        walker.walk_stream(data, slots)
        return slots

    def test_minimal_mesh_parses_to_the_end(self):
        slots = self.walk(mesh())
        self.assertEqual(slots["part"]["CMSP"], 1)
        self.assertEqual(slots["frame orientations"]["HORI"], 1)

    def test_pieces_after_the_first_skip_their_vertices(self):
        slots = self.walk(mesh(parts=2, pieces=2))
        self.assertEqual(slots["piece vertices"]["VBUF"], 4)

    def test_trailing_bytes_are_refused(self):
        with self.assertRaises(walker.GrammarError):
            self.walk(mesh() + b"\0" * 8)

    def test_a_truncated_stream_is_refused(self):
        with self.assertRaises(walker.GrammarError):
            self.walk(mesh()[:-10])

    def test_an_unexpected_orientation_tag_is_refused(self):
        with self.assertRaises(walker.GrammarError):
            self.walk(mesh().replace(b"HORI", b"XORI"))

    def test_aya_members_concatenate(self):
        data = mesh()
        members = b"".join(struct.pack("<I", len(z)) + z for z in (zlib.compress(data[:50]), zlib.compress(data[50:])))
        self.assertEqual(walker.inflate_aya(members), data)

    def test_cached_frames_match_the_composed_keys(self):
        totals, worst = collections.Counter(), [0.0, 0.0]
        # The child's model-space position is the root's (1, 0, 0) plus the root's rotation applied to (0, 2, 0).
        walker.check_caches(walker.walk_stream(animated_mesh((-1, 0, 0)), collections.defaultdict(collections.Counter)),
                            totals, worst)
        self.assertEqual(totals["position frames"], 2)
        self.assertEqual(totals["position mismatches"], 0)

    def test_a_cache_that_does_not_compose_is_reported(self):
        totals, worst = collections.Counter(), [0.0, 0.0]
        walker.check_caches(walker.walk_stream(animated_mesh((1, 2, 0)), collections.defaultdict(collections.Counter)),
                            totals, worst)
        self.assertEqual(totals["position mismatches"], 1)

    def test_the_game_folder_must_be_named(self):
        with self.assertRaises(SystemExit):
            walker.main([])


if __name__ == "__main__":
    unittest.main()
