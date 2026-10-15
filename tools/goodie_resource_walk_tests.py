# SPDX-License-Identifier: MIT
"""Checks the Goodie resource walker on synthetic archives (no game bytes)."""
import struct
import unittest

import goodie_resource_walk as walk


def chunk(tag, payload):
    return tag + struct.pack("<I", len(payload)) + payload


def texture(name, texture_format=4, compressible=True, frames=1):
    record = bytearray(walk.TEXTURE_RECORD)
    record[8:8 + len(name)] = name.encode()
    struct.pack_into("<i", record, 172, 256)
    struct.pack_into("<h", record, 176, 128)
    struct.pack_into("<i", record, 312, frames)
    struct.pack_into("<i", record, 324, texture_format)
    record[340] = 1 if compressible else 0
    body = chunk(b"CTEX", bytes(record)) + b"".join(chunk(b"TFRM", struct.pack("<i", 1)) for _ in range(frames))
    return chunk(b"DXTX", body)


def stream(number, kind, content=b""):
    prefix = chunk(b"LVLR", struct.pack("<I", 103)) + chunk(b"TARG", struct.pack("<I", 1)) + chunk(b"AYAD", bytes(24))
    return prefix + chunk(b"GDIE", chunk(b"GDAT", struct.pack("<2i", number, kind) + content))


def model(number, names, mesh):
    textures = b"".join(chunk(b"TXTR", texture(name)) for name in names)
    reference = bytearray(walk.MESH_REFERENCE)
    reference[:len(mesh)] = mesh.encode()
    struct.pack_into("<2i", reference, 300, 10002, 0)
    meshes = chunk(b"MESH", chunk(b"PMSH", chunk(b"PMS2", bytes(reference))))
    return stream(number, walk.MODEL, chunk(b"MDAT", struct.pack("<i", len(names))) + textures + meshes)


class GoodieWalkTests(unittest.TestCase):
    def test_an_image_names_one_texture(self):
        goodie = walk.read_goodie(stream(3, walk.IMAGE, texture("goodies\\ca_x.tga")))
        self.assertEqual((goodie["number"], goodie["type"]), (3, walk.IMAGE))
        self.assertEqual(walk.texture_candidates(goodie["textures"][0]), ["dxtntextures/goodies%ca_x.tga(0)A8R8G8B8.aya"])

    def test_a_model_names_its_background_textures_and_mesh(self):
        goodie = walk.read_goodie(model(8, ["goodies\\bg.tga", "meshtex\\a.tga"], "f_be1.msh"))
        self.assertEqual([t["name"] for t in goodie["textures"]], ["goodies\\bg.tga", "meshtex\\a.tga"])
        self.assertEqual(goodie["mesh"]["name"], "f_be1.msh")

    def test_video_and_level_goodies_carry_nothing_and_map_by_number(self):
        self.assertEqual(walk.read_goodie(stream(201, walk.VIDEO))["textures"], [])
        self.assertEqual((walk.video_file(201), walk.video_file(232), walk.video_file(77)), ("cutscenes/01", "cutscenes/33", "UsTheMovie"))
        self.assertEqual((walk.level_number(66), walk.level_number(70)), (901, 905))

    def test_trailing_or_missing_bytes_are_refused(self):
        with self.assertRaises(walk.GoodieError):
            walk.read_goodie(stream(201, walk.VIDEO, b"\0"))
        with self.assertRaises(walk.GoodieError):
            walk.read_goodie(stream(3, walk.IMAGE, texture("x")[:-2]))
        with self.assertRaises(walk.GoodieError):
            walk.read_goodie(stream(3, walk.IMAGE, texture("x")) + b"\0")

    def test_the_type_rule_matches_the_game_by_number(self):
        expected = {0: 0, 7: 0, 8: 1, 12: 0, 24: 0, 36: 1, 57: 1, 58: 0, 66: 3, 70: 3, 71: 0, 74: 0, 75: 2, 76: 1, 77: 2,
                    78: 0, 200: 0, 201: 2, 232: 2}
        self.assertEqual({n: walk.goodie_type(n) for n in expected}, expected)

    def test_uncompressible_and_long_names_follow_the_path_rule(self):
        record = walk.texture_reference(walk.Chunks(texture("hud\\m.tga", compressible=False)))
        self.assertEqual(walk.texture_candidates(record), ["textures/mustbe_hud%m.tga(0)A8R8G8B8.aya"])
        long_name = "goodies\\" + "x" * 70 + ".tga"
        record = walk.texture_reference(walk.Chunks(texture(long_name)))
        candidate = walk.texture_candidates(record)[0]
        self.assertEqual(len(candidate) - len("dxtntextures/"), 65)
        self.assertTrue(candidate.endswith("xxxx.aya"))


if __name__ == "__main__":
    unittest.main()
