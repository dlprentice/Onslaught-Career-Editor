#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks tools/content_inventory.py and its retail gate on an authored install (no game bytes): the byte account's
rules, what each reader claims and refuses, the joins that make a file or asset used, the independent decoder's
agreement rule, and that the gate fails when the run and the folder disagree."""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import os
import shutil
import stat
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cmsh_animation_usage_census_tests as mesh_fixtures
import content_catalog_tests as catalog_fixtures
import content_inventory as inv
import content_inventory_gate as gate
import game_tables_decode_tests as tables
import goodie_resource_walk_tests as goodie_fixtures
import media_readers_tests as media_fixtures
import particle_set_walk_tests as particle_fixtures

ROOT = Path(__file__).resolve().parents[1]

FAKE_DECODER = '''#!/usr/bin/env python3
import sys
path = sys.argv[sys.argv.index("-i") + 1]
if path.endswith("broken.ogg"):
    sys.stderr.write("error while decoding\\n")
    sys.exit(1)
print("#tb 0: 1/25")
if path.endswith(".ogg"):
    print("0,          0,          0,     4410,     8820, 0x00000000")
elif path.endswith(".vid"):
    print("0,          0,          0,        1,     9216, 0x00000000")
    print("0,          1,          1,        1,     9216, 0x00000000")
    print("1,          0,          0,     1024,     2048, 0x00000000")
'''


def physics_script() -> bytes:
    """A unit naming its mesh and an engine noise, an explosion naming a particle effect and a sound, a weapon naming
    an icon no texture carries."""
    def text(value: str) -> bytes:
        return value.encode("ascii") + b"\0"

    return media_fixtures_free_physics([
        (1, "Tank", [(8, struct.pack("<I", 3)), (9, text("authored.msh")), (54, text("Engine"))]),
        (8, "Rock", [(2, text("authored.msh"))]),
        (6, "Boom", [(2, text("Spark")), (10, text("engine")), (5, text("NoSuchEffect"))]),
        (2, "Gun", [(5, text("gun_icon"))]),
    ])


def media_fixtures_free_physics(statements) -> bytes:
    out = bytearray(struct.pack("<H", 18))
    for kind, name, values in statements:
        body = bytearray(name.encode("ascii") + b"\0")
        for number, (value_id, value) in enumerate(values):
            body += struct.pack("<II", value_id, len(value)) + value
            body += struct.pack("<i", -1 if number + 1 == len(values) else 0)
        out += struct.pack("<II", kind, len(body)) + body
    return bytes(out + struct.pack("<i", -1))


def pc_prefix() -> bytes:
    """LVLR, TARG and AYAD holding the documented PC build's words."""
    chunk = catalog_fixtures.chunk
    return b"".join(chunk(tag.encode("ascii"), struct.pack(f"<{len(words)}I", *words))
                    for tag, words in inv.PREFIX_VALUES.items())


def nested_imposters(*, views: bytes, label: bytes = b"authored.msh") -> bytes:
    """A level archive whose imposters are framed as retail frames them: IMPS holding IMPS, then DATA, the atlas
    texture and the IMPO list."""
    chunk = catalog_fixtures.chunk
    record = bytearray(76)
    record[4:4 + len(label)] = label
    impt = chunk(b"CIMP", bytes(record)) + chunk(b"IMSH", struct.pack("<i", 7)) + chunk(b"VIEW", views)
    inner = (chunk(b"DATA", bytes(8)) + catalog_fixtures.text_record("Imposters_101", tag=b"BTXT")
             + chunk(b"IMPO", struct.pack("<I", 1) + chunk(b"IMPT", impt)))
    return catalog_fixtures.aya(pc_prefix() + chunk(b"IMPS", chunk(b"IMPS", inner)))


def camd(name: str, mode: int, start: int, last: int, scaler: int, rate: float) -> bytes:
    """One 36-byte animation record: its name, mode, start, last frame, frame scaler and rate."""
    return name.encode("ascii").ljust(16, b"\0") + struct.pack("<4if", mode, start, last, scaler, rate)


# A mesh whose modes run forward, backward (a negative frame scaler: last below start), at a stored rate of 0 and at
# one below the smallest rate the game plays.
REVERSE_MODES = (("ahead", 1001, 0, 8, 8, 0.125), ("back", 1002, 20, 10, -10, 0.25), ("still", 1003, 0, 4, 4, 0.0),
                 ("tiny", 1004, 0, 2, 2, 0.00005))


def reverse_mesh() -> bytes:
    return mesh_fixtures._catalog_stream(name="reverse.msh", animations=b"".join(camd(*mode) for mode in REVERSE_MODES),
                                         animation_count=len(REVERSE_MODES))


def dds_file(layout: str, width: int, height: int, levels: list[bytes]) -> bytes:
    """A DDS storing the given format, whose mip levels are the given bytes, largest first."""
    flags = 0x1007 | 0x80000 | (0x20000 if len(levels) > 1 else 0)  # the required flags, linear size, mip count
    caps = 0x1000 | (0x400008 if len(levels) > 1 else 0)  # a texture, and a complex mipmapped one with levels
    if layout.startswith("DXT"):
        pixel = struct.pack("<2I", 32, 0x4) + layout.encode("ascii") + bytes(20)
    else:
        bits, masks = {"A1R5G5B5": (16, (0x7C00, 0x3E0, 0x1F, 0x8000)),
                       "A8R8G8B8": (32, (0xFF0000, 0xFF00, 0xFF, 0xFF000000))}[layout]
        pixel = struct.pack("<8I", 32, 0x41, 0, bits, *masks)
    head = (b"DDS " + struct.pack("<7I", 124, flags, height, width, len(levels[0]), 0, len(levels)) + bytes(44) + pixel
            + struct.pack("<2I", caps, 0) + bytes(12))
    assert len(head) == 128
    return head + b"".join(levels)


def graded_dxt2() -> bytes:
    """An 8 x 8 DXT2 with four levels whose top level's explicit alpha is half on."""
    block = struct.pack("<Q", 0x8888888888888888) + struct.pack("<HHI", 0xF800, 0x001F, 0)
    return dds_file("DXT2", 8, 8, [block * 4, block, block, block])


def binary_a8r8g8b8() -> bytes:
    """A 4 x 4 A8R8G8B8 with three levels whose top level is half transparent, half opaque."""
    top = bytes([10, 20, 30, 0]) * 8 + bytes([10, 20, 30, 255]) * 8
    return dds_file("A8R8G8B8", 4, 4, [top, bytes([1, 2, 3, 255]) * 4, bytes([1, 2, 3, 255])])


def stereo_ogg(granule: int = 88200) -> bytes:
    """Two channels at 44,100 Hz, two seconds long."""
    return (media_fixtures.page(2, 0, 0, [media_fixtures.identification(2, 44100)])
            + media_fixtures.page(0, 0, 1, [media_fixtures.comment(), media_fixtures.setup_header(2)])
            + media_fixtures.page(4, granule, 2, [b"\x00" * 300, b"\x01" * 40]))


def authored(game: Path) -> None:
    catalog_fixtures.authored_install(game)
    tables.write_tables(game)
    extra = {
        "data/default physics.dat": physics_script(),
        "data/language/english.dat": catalog_fixtures.authored_language(),
        "data/sounds/english/MessageBox/line.ogg": media_fixtures.ogg_file(),
        "data/video/intro.vid": media_fixtures.bink_file([([b"\x10" * 8], b"\x20" * 30), ([b"\x11" * 4], b"\x21" * 50)]),
        "data/textures/splash.tga": media_fixtures.tga_file(),
        "data/Dial.raw": bytes(512),
        "Manuals/English/English.htm": b'<html><img src="English_files/image001.png"></html>\r\n',
        "Manuals/English/English_files/image001.png": media_fixtures.png_file(),
        "Manuals/Images/orphan.png": media_fixtures.png_file(3, 1),
        "data/resources/101_res_PC.aya": nested_imposters(views=struct.pack("<6f", 0.0, 0.5, 0.0, 0.25, 8.0, 8.0) * 6),
        # The forms and formats the metadata readers and the gate's own readers must agree on.
        "data/resources/meshes/m_reverse.msh.aya": catalog_fixtures.aya(reverse_mesh()),
        "data/resources/dxtntextures/extra%graded.tga(0)DXT2.aya": catalog_fixtures.aya(graded_dxt2()),
        "data/resources/textures/mustbe_extra%binary.tga(0)A8R8G8B8.aya": catalog_fixtures.aya(binary_a8r8g8b8()),
        "data/resources/102_res_PC.aya": catalog_fixtures.aya(
            pc_prefix() + catalog_fixtures.chunk(b"DMKR", catalog_fixtures.dmkr_payload(2))),
        "data/music/track.ogg": stereo_ogg(),
        "Manuals/Images/photo.jpg": media_fixtures.jpeg_file(),
        "Setup.exe": media_fixtures.pe_file(icon_bits=32),
        "data/sounds/sounds_french_pc.xap": catalog_fixtures.xap_fixtures.bank([("Units\\long", 88200, bytes(22050))]),
    }
    for rel, data in extra.items():
        path = game / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def part_classes(row: dict) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for part in row["parts"]:
        out.setdefault(part["part"], set()).add(part["class"])
    return out


class AccountTests(unittest.TestCase):
    def test_a_gap_is_unknown_and_the_parts_sum(self):
        account = inv.Account(10)
        account.add(0, 4, inv.DECODED, "head")
        account.add(6, 2, inv.REFERENCED, "body")
        closed = account.close()
        self.assertEqual(closed["totals"], {inv.DECODED: 4, inv.REFERENCED: 2, inv.UNKNOWN: 4})
        self.assertEqual(closed["unknownSpans"], [[4, 6, "unclaimed"], [8, 10, "unclaimed"]])
        self.assertEqual(account.spans_of(inv.REFERENCED), [(6, 8)])

    def test_overlapping_or_outside_claims_are_refused(self):
        account = inv.Account(8)
        account.add(0, 4, inv.DECODED, "a")
        account.add(3, 2, inv.DECODED, "b")
        with self.assertRaises(inv.AccountError):
            account.close()
        with self.assertRaises(inv.AccountError):
            inv.Account(4).add(2, 3, inv.DECODED, "c")
        with self.assertRaises(inv.AccountError):
            inv.Account(4).add(0, 1, "guessed", "d")

    def test_file_classes(self):
        self.assertEqual(inv.file_class(0, {inv.DECODED: 0, inv.REFERENCED: 0, inv.UNKNOWN: 0}), inv.DECODED)
        self.assertEqual(inv.file_class(3, {inv.DECODED: 3, inv.REFERENCED: 0, inv.UNKNOWN: 0}), inv.DECODED)
        self.assertEqual(inv.file_class(3, {inv.DECODED: 0, inv.REFERENCED: 3, inv.UNKNOWN: 0}), inv.REFERENCED)
        self.assertEqual(inv.file_class(3, {inv.DECODED: 0, inv.REFERENCED: 0, inv.UNKNOWN: 3}), inv.UNKNOWN)
        self.assertEqual(inv.file_class(3, {inv.DECODED: 2, inv.REFERENCED: 0, inv.UNKNOWN: 1}), inv.PARTIAL)

    def test_a_pool_string_no_entry_reaches_is_referenced_and_a_fragment_unknown(self):
        pool = "lost\0kept\0".encode("utf-16le") + b"x\0"
        account = inv.Account(len(pool))
        inv.claim_strings(account, pool, 0, len(pool), [10], 2, "pool")
        closed = account.close()
        self.assertEqual(closed["totals"], {inv.DECODED: 10, inv.REFERENCED: 10, inv.UNKNOWN: 2})

    def test_the_sniff_reads_the_bytes_not_the_name(self):
        self.assertEqual(inv.sniff(media_fixtures.ogg_file()), "ogg")
        self.assertEqual(inv.sniff(media_fixtures.png_file()), "png")
        self.assertEqual(inv.sniff(catalog_fixtures.aya(b"LVLR")), "aya")
        self.assertEqual(inv.sniff(b"plain words\r\n"), "text")
        self.assertEqual(inv.sniff(b""), "empty")
        self.assertFalse(inv.sniff_agrees("ogg-voice", "png"))


class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.game = Path(cls.temp.name) / "game"
        authored(cls.game)
        cls.inventory = inv.build_inventory(cls.game)
        cls.rows = {row["path"]: row for row in cls.inventory["files"]}
        cls.items = cls.inventory["items"]
        cls.coverage = cls.inventory["coverage"]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def item(self, form: str, name: str) -> dict:
        return next(item for item in self.items if item["form"] == form and item["name"] == name)

    def test_every_file_is_accounted_once_and_the_bytes_sum(self):
        on_disk = sum(path.stat().st_size for path in self.game.rglob("*") if path.is_file())
        self.assertEqual(self.coverage["installBytes"], on_disk)
        self.assertEqual(len(self.rows), sum(1 for path in self.game.rglob("*") if path.is_file()))
        for row in self.rows.values():
            self.assertEqual(sum(row["bytes"].values()), row["logicalBytes"], row["path"])

    def test_an_archive_is_walked_chunk_by_chunk(self):
        parts = part_classes(self.rows["data/resources/100_res_PC.aya"])
        self.assertEqual(parts["TEXT"], {inv.DECODED})
        self.assertEqual(parts["MESH/reference"], {inv.DECODED})

    def test_imposters_framed_as_retail_frames_them(self):
        row = self.rows["data/resources/101_res_PC.aya"]
        parts = part_classes(row)
        self.assertEqual(parts["IMPS/label"], {inv.DECODED})
        self.assertEqual(parts["IMPS/views"], {inv.DECODED})
        self.assertEqual(parts["IMPS/atlas-texture"], {inv.DECODED})
        self.assertEqual(parts["IMPS/DATA"], {inv.REFERENCED})
        self.assertEqual(row["bytes"][inv.UNKNOWN], 0)
        self.assertEqual((parts["LVLR"], parts["TARG"], parts["AYAD"]), ({inv.DECODED},) * 3)
        self.assertEqual(row["problems"], [])

    def test_a_prefix_that_is_not_the_documented_pc_build_s_is_referenced(self):
        # The catalogue's authored archives carry zero AYAD guard words.
        row = self.rows["data/resources/100_res_PC.aya"]
        self.assertEqual(part_classes(row)["AYAD"], {inv.REFERENCED})
        self.assertIn("AYAD: its values are not the documented PC build's", row["problems"])
        chunk = catalog_fixtures.chunk
        short = catalog_fixtures.aya(chunk(b"LVLR", struct.pack("<H", 103)) + chunk(b"TARG", struct.pack("<I", 2)))
        reading = inv.read_archive(short, inv.Context(self.game), {"path": "data/resources/base_res_PC.aya"})
        self.assertEqual(reading.problems, ["LVLR: its size is not the documented PC build's",
                                            "TARG: its values are not the documented PC build's"])
        self.assertEqual(reading.account.close()["totals"][inv.DECODED], 0)

    def test_wdat_is_decoded_only_when_it_names_the_archive_s_own_level(self):
        world = catalog_fixtures.world_archive()  # WDAT names no base world and real world 200
        ctx = inv.Context(self.game)
        own = inv.read_archive(world, ctx, {"path": "data/resources/200_res_PC.aya"})
        other = inv.read_archive(world, ctx, {"path": "data/resources/201_res_PC.aya"})
        self.assertEqual(part_classes({"parts": own.account.close()["parts"]})["WRES/WDAT"], {inv.DECODED})
        self.assertFalse([p for p in own.problems if p.startswith("WRLD")])
        self.assertEqual(part_classes({"parts": other.account.close()["parts"]})["WRES/WDAT"], {inv.REFERENCED})
        self.assertIn("WRLD: the world layout does not close: WDAT", other.problems)

    def test_names_without_a_terminator_are_referenced(self):
        chunk = catalog_fixtures.chunk
        reference = b"n" * inv.MESH_NAME + struct.pack("<ii", 7, 0) + b"\0"
        mesh = catalog_fixtures.aya(pc_prefix() + chunk(b"MESH", chunk(b"PMSH", chunk(b"PMS2", reference))))
        reading = inv.read_archive(mesh, inv.Context(self.game), {"path": "data/resources/base_res_PC.aya"})
        self.assertEqual(part_classes({"parts": reading.account.close()["parts"]})["MESH/reference"], {inv.REFERENCED})
        self.assertEqual(reading.problems, ["MESH: the reference's name has no terminator"])
        views = struct.pack("<6f", 0.0, 0.5, 0.0, 0.25, 8.0, 8.0) * 6
        label = b"x" * (inv.IMPOSTER_LABEL[1] - inv.IMPOSTER_LABEL[0])
        reading = inv.read_archive(nested_imposters(views=views, label=label), inv.Context(self.game),
                                   {"path": "data/resources/101_res_PC.aya"})
        self.assertEqual(part_classes({"parts": reading.account.close()["parts"]})["IMPS/label"], {inv.REFERENCED})
        self.assertEqual(reading.problems, ["IMPS: an imposter's stored label has no terminator"])

    def test_imposters_without_their_inner_chunk_are_refused(self):
        # The catalogue's fixture frames IMPS flatly; the walk refuses it and leaves its bytes unknown.
        row = self.rows["data/resources/100_res_PC.aya"]
        self.assertIn("IMPS: IMPS does not hold its own IMPS chunk", row["problems"])
        self.assertGreater(row["bytes"][inv.UNKNOWN], 0)

    def test_views_that_are_not_atlas_rectangles_stay_framed(self):
        zero = inv.views_hold(bytes(144))
        good = inv.views_hold(struct.pack("<6f", 0.0, 0.5, 0.0, 0.25, 8.0, 8.0))
        self.assertEqual((zero, good, inv.views_hold(bytes(25))), (False, True, False))

    def test_media_without_a_decoder_stays_referenced(self):
        row = self.rows["data/sounds/english/MessageBox/line.ogg"]
        self.assertEqual(row["class"], inv.PARTIAL)
        self.assertEqual(part_classes(row)["ogg/audio-packets"], {inv.REFERENCED})
        self.assertEqual(row["facts"]["decoder"], "not run")
        self.assertIn("not run", self.coverage["mediaDecoder"])
        video = self.rows["data/video/intro.vid"]
        self.assertEqual(part_classes(video)["bink/video-packets"], {inv.REFERENCED})
        # What a reader here reads counts without the decoder: the Vorbis headers (the setup header field by field), the
        # Bink header and index. What only the decoder's demuxer reads does not: the audio track descriptors.
        self.assertEqual(part_classes(row)["ogg/vorbis-headers"], {inv.DECODED})
        self.assertEqual(part_classes(video)["bink/audio-track-descriptors"], {inv.REFERENCED})
        self.assertEqual((part_classes(video)["bink/header"], part_classes(video)["bink/frame-index"]),
                         ({inv.DECODED}, {inv.DECODED}))
        self.assertEqual((self.coverage["proofs"]["oggFilesWalked"], self.coverage["proofs"]["oggCodebooksRead"]), (2, 4))

    def test_a_file_its_reader_refuses_is_referenced_with_the_reason(self):
        row = self.rows["data/sounds/english/MessageBox/hello.ogg"]  # the catalogue's header-only fixture
        self.assertEqual(row["class"], inv.REFERENCED)
        self.assertTrue(row["problems"])
        self.assertEqual(self.rows["BEA.exe"]["class"], inv.REFERENCED)

    def test_images_are_decoded_and_a_page_link_uses_one(self):
        self.assertEqual(self.rows["data/textures/splash.tga"]["class"], inv.DECODED)
        linked = self.item("png", "image001.png")
        orphan = self.item("png", "orphan.png")
        self.assertTrue(linked["used"])
        self.assertIn("page:link", linked["usedBy"])
        self.assertFalse(orphan["used"])

    def test_a_manual_page_is_a_text_item(self):
        page = self.item("manual-page", "English.htm")
        self.assertEqual((page["kind"], page["status"], page["file"]), ("text", inv.DECODED, "Manuals/English/English.htm"))
        self.assertFalse(page["used"])  # nothing in the authored install links to the page itself

    def test_the_byte_sprite_proves_only_its_first_frame(self):
        row = self.rows["data/Dial.raw"]
        self.assertEqual(row["bytes"], {inv.DECODED: 256, inv.REFERENCED: 256, inv.UNKNOWN: 0})
        self.assertIn("loader:CByteSprite::Load", row["usedBy"])

    def test_physics_values_are_read_and_joined(self):
        self.assertEqual(self.rows["data/default physics.dat"]["class"], inv.DECODED)
        joins = self.coverage["physicsJoins"]
        self.assertEqual(joins["joins"]["sound-effect:resolved"], 2)  # Engine, and engine by stricmp
        self.assertEqual(joins["joins"]["particle-effect:resolved"], 1)
        self.assertEqual(joins["unresolvedNames"]["particle-effect"], ["NoSuchEffect"])
        self.assertEqual(joins["unresolvedNames"]["icon"], ["gun_icon"])
        mesh = self.rows["data/resources/meshes/m_authored.msh.aya"]
        self.assertIn("physics:mesh", mesh["usedBy"])

    def test_a_texture_nothing_loads_is_listed_unused(self):
        unused = [i for i in self.items if i["form"] == "dds-file" and i["file"].endswith("unused.tga(0)A1R5G5B5.aya")]
        self.assertEqual(len(unused), 1)
        self.assertFalse(unused[0]["used"])

    def test_a_mesh_the_loader_grammar_refuses_is_referenced_with_the_reason(self):
        # The catalogue's authored mesh fixture is shorter than the loader's vertex buffer record.
        row = self.rows["data/resources/meshes/m_authored.msh.aya"]
        self.assertEqual(row["class"], inv.REFERENCED)
        self.assertTrue(any(problem.startswith("CMSH: ") for problem in row["problems"]))

    def test_an_imposter_atlas_is_used_by_its_role(self):
        atlas = self.item("descriptor-imps", "Imposters_101")
        self.assertIn("imposter:atlas", atlas["usedBy"])

    def test_items_have_unique_ids_and_known_kinds(self):
        ids = [item["id"] for item in self.items]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertLessEqual({item["kind"] for item in self.items},
                             {"model", "texture", "image", "animation", "sound", "film", "text"})

    def test_a_level_archive_the_judge_cannot_read_leaves_no_level_source_decoded(self):
        # The authored level 200 archive is read by the inventory's archive reader, but its one member inflates past the
        # judge's limit: which scripts it ships, and for which folders, is not known, so no level folder's source counts.
        self.assertEqual(self.coverage["proofs"][inv.MSL_UNREAD], 1)
        archive = self.rows["data/resources/200_res_PC.aya"]
        self.assertTrue(any(p.startswith("the mission-script judge could not read this archive's worlds")
                            for p in archive["problems"]))
        for rel in ("data/MissionScripts/level100/main.msl", "data/MissionScripts/level200/main.msl"):
            row = self.rows[rel]
            self.assertEqual((row["class"], len(row["problems"])), (inv.REFERENCED, 1), rel)
        self.assertEqual(self.coverage["proofs"]["mslSourcesNotJudged"], 2)
        summary = "\n".join(inv.summary_lines(self.coverage))
        self.assertIn("level archives whose worlds the judge could not read=1", summary)

    def test_the_headline_gives_the_share_without_a_media_decoder(self):
        head = self.coverage["headline"]
        content = [f for f in self.coverage["families"] if f["content"]]
        self.assertEqual(head["contentLogicalBytes"], sum(f["logicalBytes"] for f in content))
        decoded = sum(f["logicalBytesByClass"][inv.DECODED] for f in content)
        self.assertEqual((head["withMediaDecoder"], head["withoutMediaDecoder"]["decodedBytes"],
                          head["decodedOnlyByTheMediaDecoder"]), (None, decoded, 0))
        self.assertIn("with no independent media decoder run", inv.summary_lines(self.coverage)[-1])

    def metadata(self, form: str, name: str | None = None, file: str | None = None) -> dict:
        return next(row for row in self.inventory["assets"] if row["form"] == form
                    and (name is None or row["name"] == name) and (file is None or row["identity"]["file"] == file))

    def test_every_texture_image_model_animation_sound_and_film_has_one_metadata_row(self):
        wanted = [item["id"] for item in self.items if item["kind"] in inv.METADATA_KINDS]
        self.assertEqual([row["id"] for row in self.inventory["assets"]], wanted)
        self.assertGreater(len(wanted), 0)
        self.assertFalse([row for row in self.inventory["assets"] if row["kind"] == "text"])
        summary = self.coverage["assetMetadata"]
        self.assertEqual(sum(kind["rows"] for kind in summary.values()), len(wanted))
        self.assertEqual(summary["texture"]["fieldsEstablished"]["width"],
                         sum(1 for row in self.inventory["assets"] if row["kind"] == "texture" and row["width"]))

    def test_a_dds_texture_s_metadata_comes_from_its_own_header(self):
        rel = "data/resources/dxtntextures/meshtex%skin.tga(0)A1R5G5B5.aya"
        row = self.metadata("dds-file", file=rel)
        dds = catalog_fixtures.dds_dxt1_4x4()
        self.assertEqual({field: row[field] for field in ("format", "width", "height", "mipLevels", "alpha", "channels")},
                         {"format": "DXT1", "width": 4, "height": 4, "mipLevels": 1, "alpha": "none", "channels": 3})
        identity = row["identity"]
        self.assertEqual((identity["envelope"], identity["offset"], identity["length"], identity["sha256"]),
                         ("aya-zlib-members(dds)", 0, len(dds), inv.cc.sha256(dds)))
        self.assertEqual(identity["fileSha256"], self.rows[rel]["sha256"])
        self.assertEqual(row["details"]["sourceFormatFromName"], "A1R5G5B5")  # the name's request, not the stored format
        descriptor = next(r for r in self.inventory["assets"] if r["form"] == "descriptor-text"
                          and r["name"] == "meshtex\\skin.tga")
        self.assertEqual(row["usedByRecords"], [descriptor["id"]])  # the texture record that takes its pixels
        self.assertEqual(descriptor["details"]["pixelsFrom"], [row["id"]])
        self.assertIn("mesh:data/resources/meshes/m_authored.msh.aya", descriptor["usedByRecords"])
        self.assertIsNotNone(row["upscale"])

    def test_image_sound_and_film_metadata(self):
        png = self.metadata("png", name="orphan.png")
        self.assertEqual((png["format"], png["width"], png["height"], png["channels"], png["alpha"]),
                         ("png", 3, 1, 3, "none"))
        self.assertEqual((png["identity"]["sha256Scope"], png["identity"]["sha256"]),
                         ("whole file", self.rows["Manuals/Images/orphan.png"]["sha256"]))
        tga = self.metadata("tga")
        self.assertEqual((tga["width"], tga["height"], tga["channels"], tga["alpha"]), (2, 2, 3, "none"))
        voice = self.metadata("voice", name="line")
        self.assertEqual((voice["format"], voice["channels"], voice["sampleRate"], voice["durationSeconds"]),
                         ("vorbis", 1, 22050, 0.2))
        film = self.metadata("video", name="intro")
        self.assertEqual((film["width"], film["height"], film["frames"]), (64, 48, 2))
        sprite = self.metadata("byte-sprite")
        self.assertEqual((sprite["width"], sprite["height"], sprite["frames"], sprite["details"]["framesEstablished"]),
                         (16, 16, None, 1))
        [num, den] = film["details"]["fpsRational"]
        self.assertEqual(film["durationSeconds"], round(2 * den / num, 3))
        music = self.metadata("music", name="track")
        self.assertEqual((music["format"], music["channels"], music["sampleRate"], music["durationSeconds"]),
                         ("vorbis", 2, 44100, 2.0))
        sample = self.metadata("bank-sample", name="Units\\long")
        self.assertEqual((sample["format"], sample["channels"], sample["sampleRate"], sample["durationSeconds"]),
                         ("ima-adpcm-4bit", 1, 44100, 1.0))
        jpeg = self.metadata("jpeg", name="photo.jpg")
        self.assertEqual((jpeg["format"], jpeg["width"], jpeg["height"], jpeg["channels"], jpeg["alpha"]),
                         ("jpeg", 5, 3, 1, "none"))
        icon = self.metadata("pe-icon", file="Setup.exe")
        self.assertEqual((icon["format"], icon["width"], icon["height"], icon["alpha"], icon["channels"]),
                         ("icon bitmap", 2, 2, "present", None))  # 32-bit colour holds alpha; below it, only a mask
        animation = self.metadata("animation", name="walk")
        self.assertEqual((animation["format"], animation["frames"], animation["durationSeconds"]), ("camd", 11, 0.5))
        self.assertEqual(animation["usedByRecords"], [animation["identity"]["owner"]])

    def test_an_animation_s_frames_count_either_way_and_its_duration_follows_its_rate(self):
        # back runs from frame 20 down to 10 (a negative frame scaler); still stores a rate of 0, which plays at 1.
        rows = {row["name"]: row for row in self.inventory["assets"]
                if row["form"] == "animation" and row["identity"]["file"] == "data/resources/meshes/m_reverse.msh.aya"}
        got = {name: (row["frames"], row["durationSeconds"], row["details"]["frameScaler"]) for name, row in rows.items()}
        self.assertEqual(got, {"ahead": (9, 0.4, 8), "back": (11, 0.2, -10), "still": (5, 0.05, 4),
                               "tiny": (3, 0.05, 2)})

    def test_texture_metadata_by_stored_and_named_format(self):
        graded = self.metadata("dds-file", file="data/resources/dxtntextures/extra%graded.tga(0)DXT2.aya")
        binary = self.metadata("dds-file", file="data/resources/textures/mustbe_extra%binary.tga(0)A8R8G8B8.aya")
        fields = ("format", "width", "height", "mipLevels", "alpha", "channels", "frames")
        self.assertEqual([graded[field] for field in fields], ["DXT2", 8, 8, 4, "graded", 4, None])
        self.assertEqual([binary[field] for field in fields], ["A8R8G8B8", 4, 4, 3, "binary", 4, None])
        self.assertEqual([mip["length"] for mip in graded["details"]["mips"]], [64, 16, 16, 16])
        # A texture record gives the format it names, which also names its pixel file; that DDS stores DXT1.
        record = next(row for row in self.inventory["assets"] if row["form"] == "descriptor-text"
                      and row["name"] == "meshtex\\skin.tga")
        self.assertEqual([record[field] for field in fields], ["A1R5G5B5", 4, 4, 1, None, 4, 1])
        self.assertEqual(record["details"]["occurrences"], 1)
        damage = self.metadata("damage-texture")
        self.assertEqual([damage[field] for field in fields], ["one byte per texel", 4, 4, 3, None, 1, None])

    def test_a_mixer_mip_s_identity_claims_no_coordinates(self):
        # Its item offset is the ERES payload's, not where the mip's bytes start.
        row = self.metadata("terrain-mixer-mip")
        self.assertEqual((row["identity"]["envelope"], row["identity"]["offset"]), ("lvlr-chunk(ERES)", None))
        self.assertEqual(len(row["identity"]["chunkPath"]), 1)

    def test_trailing_bytes_after_a_table_are_unknown(self):
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp) / "game"
            shutil.copytree(self.game, game)
            path = game / "data/language/english.dat"
            path.write_bytes(path.read_bytes() + b"tail")
            row = next(r for r in inv.build_inventory(game)["files"] if r["path"] == "data/language/english.dat")
            self.assertEqual(row["bytes"][inv.UNKNOWN], 4)
            self.assertEqual(row["class"], inv.PARTIAL)


def account_of(reading: inv.Reading) -> dict:
    closed = reading.account.close()
    return {"totals": closed["totals"], "parts": part_classes({"parts": closed["parts"]}),
            "class": inv.file_class(reading.account.size, closed["totals"])}


def language(text: bytes, text_offset_words: int = 0) -> bytes:
    """A one-entry language table whose text pool holds the given UTF-16 bytes and whose audio pool is empty."""
    return (struct.pack("<III", 0xFFFFFFBB, 3, 1) + struct.pack("<III", 123, text_offset_words, 0xFFFFFFFF)
            + struct.pack("<I", len(text)) + text + struct.pack("<I", 0))


class StrictReadingTests(unittest.TestCase):
    """What a reader must read before its bytes count as decoded, and how a file it cannot read is accounted."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.game = Path(self.temp.name)
        self.ctx = inv.Context(self.game)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def read(self, family: str, rel: str, data: bytes) -> dict:
        path = self.game / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        account, _items = inv.read_file(self.game, {"path": rel, "family": family}, self.ctx)
        return account

    def test_a_particle_set_is_read_value_by_value(self):
        fixtures = particle_fixtures
        data = fixtures.particle_set(fixtures.SPRITE, fixtures.COLOURS, fixtures.EMITTER, fixtures.WOBBLE)
        reading = inv.read_particle_set(data, self.ctx, {})
        account = account_of(reading)
        # The words after Velocity_Randomness's value are never read: referenced, not decoded.
        self.assertEqual(account["totals"], {inv.DECODED: len(data) - 5, inv.REFERENCED: 5, inv.UNKNOWN: 0})
        self.assertEqual(account["parts"]["particle-set/words-the-reader-skips"], {inv.REFERENCED})
        self.assertEqual((reading.facts["descriptors"], reading.problems), (4, []))

    def test_garbage_shuffled_or_trailing_particle_lines_are_not_decoded(self):
        fixtures = particle_fixtures
        garbage = fixtures.particle_set((1, "Spark", ["Radius zz NONE", "Life ?"]))
        lines = fixtures.particle_set(fixtures.SPRITE, fixtures.COLOURS).split(b"\r\n")
        shuffled = b"\r\n".join([lines[0]] + lines[1:-1][::-1] + [b""])
        for data in (garbage, shuffled):
            reading = inv.read_particle_set(data, self.ctx, {})
            self.assertEqual(account_of(reading)["class"], inv.REFERENCED)
            self.assertEqual(len(reading.problems), 1)
        tail = fixtures.particle_set(fixtures.COLOURS, tail="Life 3\r\n")
        self.assertEqual(account_of(inv.read_particle_set(tail, self.ctx, {}))["totals"][inv.UNKNOWN], len(b"Life 3\r\n"))

    def test_a_texture_whose_envelope_does_not_inflate_stays_unknown(self):
        broken = bytes(range(16))
        texture = self.read("dds-texture-dxtn", "data/resources/dxtntextures/broken.tga(0)DXT1.aya", broken)
        mesh = self.read("cmsh-mesh", "data/resources/meshes/m_broken.msh.aya", broken)
        for row in (texture, mesh):
            self.assertEqual((row["class"], row["logicalBytes"], row["bytes"][inv.UNKNOWN]), (inv.UNKNOWN, 16, 16))
            self.assertTrue(row["problems"])
        self.assertEqual(texture["stream"], "stored")

    def test_a_texture_that_inflates_to_no_valid_dds_is_referenced(self):
        row = self.read("dds-texture-dxtn", "data/resources/dxtntextures/blank.tga(0)DXT1.aya", catalog_fixtures.aya(bytes(200)))
        self.assertEqual((row["class"], row["stream"], row["logicalBytes"]), (inv.REFERENCED, "inflated", 200))
        self.assertTrue(row["problems"])
        valid = self.read("dds-texture-dxtn", "data/resources/dxtntextures/valid.tga(0)DXT1.aya",
                          catalog_fixtures.aya(catalog_fixtures.dds_dxt1_4x4()))
        self.assertEqual((valid["class"], valid["problems"]), (inv.DECODED, []))

    def test_a_reader_that_accounts_for_nothing_or_raises_leaves_the_file_unknown(self):
        def nothing(_data, _ctx, _row):
            return inv.Reading(inv.Account(0), "inflated", "authored")

        def raises(_data, _ctx, _row):
            raise ValueError("authored refusal")

        for reader, problem in ((nothing, "the reader's stream holds none of the file's bytes"),
                                (raises, "ValueError: authored refusal")):
            with patch.dict(inv.READERS, {"authored-family": reader}):
                row = self.read("authored-family", "data/authored.bin", b"twelve bytes")
            self.assertEqual((row["class"], row["bytes"][inv.UNKNOWN]), (inv.UNKNOWN, 12))
            self.assertIn(problem, row["problems"])
        with patch.dict(inv.READERS, {"authored-family": nothing}):
            row = self.read("authored-family", "data/empty.bin", b"")  # an empty file has nothing to lose
        self.assertEqual((row["class"], row["problems"]), (inv.DECODED, []))

    def test_an_unterminated_goodie_name_is_referenced(self):
        for mesh, klass, problems in (("f_be1.msh", inv.DECODED, []),
                                      ("m" * 300, inv.REFERENCED, ["GDIE: a texture or mesh reference's name has no terminator"])):
            goodie = goodie_fixtures.model(8, ["goodies\\bg.tga"], mesh)
            stream = pc_prefix() + goodie[goodie.index(b"GDIE"):]  # the documented prefix: only GDIE is in question
            reading = inv.read_archive(catalog_fixtures.aya(stream), self.ctx, {"path": "data/resources/goodie_08_res_PC.aya"})
            self.assertEqual(account_of(reading)["parts"]["GDIE"], {klass})
            self.assertEqual(reading.problems, problems)

    def test_language_entries_outside_their_pool_or_unterminated_are_problems(self):
        reading = inv.read_language_table(language("Hello\0".encode("utf-16le"), text_offset_words=100), self.ctx, {})
        self.assertEqual(reading.problems, ["language/text-pool: an entry points outside its pool"])
        reading = inv.read_language_table(language("Hello".encode("utf-16le")), self.ctx, {})
        self.assertEqual(reading.problems, ["language/text-pool: a string runs to the end of its pool without a terminator"])
        self.assertEqual(account_of(reading)["parts"]["language/text-pool (no terminator)"], {inv.REFERENCED})
        self.assertEqual(inv.read_language_table(language("Hello\0".encode("utf-16le")), self.ctx, {}).problems, [])

    def test_a_record_takes_the_class_of_its_own_bytes(self):
        row = {"class": inv.PARTIAL, "stream": "inflated", "logicalBytes": 100, "referencedSpans": [[10, 20]],
               "unknownSpans": [[50, 60, "unclaimed"]]}
        rows = {"data/resources/100_res_pc.aya": row}

        def record(kind: str, offset: int, length: int, *, envelope: str = "lvlr-chunk(MESH/PMSH/PMS2)",
                   status: str | None = None) -> dict:
            details = {} if status is None else {"status": status}
            return {"type": kind, kind: details, "source": {"container": "data/resources/100_res_PC.aya",
                                                            "envelope": envelope, "offset": offset, "length": length}}

        cases = [(record("animation", 0, 10), inv.DECODED), (record("animation", 10, 10), inv.REFERENCED),
                 (record("animation", 15, 10), inv.PARTIAL), (record("animation", 50, 5), inv.UNKNOWN),
                 (record("animation", 95, 10), inv.UNKNOWN),
                 (record("textureDescriptor", 0, 10, status="parsed"), inv.DECODED),
                 (record("textureDescriptor", 0, 10, status="malformed"), inv.REFERENCED),
                 (record("animation", 0, 10, envelope="xap(PCXP)"), inv.PARTIAL)]
        for asset, expected in cases:
            with self.subTest(asset=asset["source"], kind=asset["type"]):
                self.assertEqual(inv.record_status(asset, False, rows), expected)
        self.assertEqual(inv.record_status(record("animation", 0, 10), True, rows), inv.PARTIAL)
        self.assertEqual(inv.record_status(record("animation", 0, 10), False, {}), inv.UNKNOWN)

    def test_line_grammars_refuse_what_does_not_hold(self):
        text = inv.READERS["mission-text-txt"]
        good = b"; a comment\r\n[TEXT_ONE] note\r\n\"Hello\"\r\n\r\n[TEXT_TWO]\r\n\t\"World\"\r\n"
        self.assertEqual(account_of(text(good, self.ctx, {"family": "mission-text-txt"}))["class"], inv.DECODED)
        for data, problem in ((good + b"\xb5\xe9 soup \xff\r\n", "a line that is no [ID], string, comment or blank line"),
                              (b"[TEXT_ONE]\r\n\r\n\"late\"\r\n", "an [ID] line without its quoted string on the next line"),
                              (b"[text_one]\r\n\"lower case\"\r\n", "a line that is no [ID], string, comment or blank line")):
            reading = text(data, self.ctx, {"family": "mission-text-txt"})
            self.assertEqual((account_of(reading)["class"], reading.problems), (inv.REFERENCED, [problem]))
        defines = inv.READERS["stf-text-table"]
        self.assertEqual(account_of(defines(b"// x\r\n#define TEXT_ONE 12\r\n\r\n", self.ctx,
                                            {"family": "stf-text-table"}))["class"], inv.DECODED)
        reading = defines(b"#define 1TEXT 12\r\n#define TEXT 1 // trailing\r\n", self.ctx, {"family": "stf-text-table"})
        self.assertEqual(reading.problems, ["2 lines that are no #define, comment or blank line"])
        self.assertEqual(account_of(defines(b"", self.ctx, {"family": "stf-text-table"}))["class"], inv.DECODED)

    def test_the_career_block_is_referenced(self):
        save = (ROOT / "tests_shared" / "fixtures" / "gold_career_save.bin").read_bytes()  # the one tracked save
        account = account_of(inv.read_career_file(save, self.ctx, {}))
        self.assertEqual(account["parts"]["career/career-block"], {inv.REFERENCED})
        self.assertEqual(account["parts"]["career/options-entries"], {inv.DECODED})
        self.assertEqual(account["totals"][inv.REFERENCED], inv.options.OPTIONS_START)
        self.assertEqual(account["class"], inv.PARTIAL)

    def test_manual_pages_are_tokenized_and_file_lists_parsed(self):
        manual = lambda rel, data: inv.read_manual_file(data, self.ctx, {"path": rel, "family": "manual"})
        page = manual("Manuals/English/English.htm", media_fixtures.PAGE)
        self.assertEqual((account_of(page)["class"], page.items[0]["status"]), (inv.DECODED, inv.DECODED))
        soup = manual("Manuals/English/Soup.htm", bytes(v for v in range(32, 256) if v not in b"<&"))
        self.assertEqual((account_of(soup)["class"], soup.items[0]["status"]), (inv.REFERENCED, inv.REFERENCED))
        self.assertEqual(soup.problems, ["not one html element"])
        listing = manual("Manuals/English/English_files/filelist.xml", b'<xml><o:File HRef="a.png"/></xml>')
        self.assertEqual(account_of(listing)["class"], inv.DECODED)
        self.assertEqual(self.ctx.links["Manuals/English/English_files/filelist.xml"], ["a.png"])
        broken = manual("Manuals/English/English_files/broken.xml", b"<xml><o:File></xml>")
        self.assertEqual((account_of(broken)["class"], broken.problems), (inv.REFERENCED, ["not well-formed XML"]))

    def script(self, rel: str, data: bytes) -> inv.Reading:
        return inv.read_mission_script(data, self.ctx, {"path": rel, "family": "mission-script-msl"})

    def test_a_mission_script_counts_only_when_its_compile_reproduces_the_shipped_copy(self):
        script = self.script
        source = b"init()\r\n{\r\n\tPause(2);\r\n}\r\n"
        verdicts = {"exact": (inv.DECODED, []), "exact, assisted": (inv.DECODED, []), "stale source": (inv.REFERENCED, []),
                    "different": (inv.REFERENCED, ["1 of 1 shipped copies compiled from this source: different"])}
        for verdict, (klass, problems) in verdicts.items():
            rel = "data/MissionScripts/level100/" + verdict.replace(" ", "").replace(",", "") + ".msl"
            self.ctx.msl[rel.casefold()] = [verdict]
            reading = script(rel, source)
            self.assertEqual((account_of(reading)["class"], reading.problems), (klass, problems), verdict)
        self.assertEqual(account_of(script("data/MissionScripts/level999/alone.msl", source))["class"], inv.DECODED)
        self.assertEqual(self.ctx.msl_unread, {})  # every archive read: a source no level ships counts on its compile
        missing = b"#include data\\gone\\defs.msl\r\n" + source
        reading = script("data/MissionScripts/level999/missing.msl", missing)
        self.assertEqual((account_of(reading)["class"], reading.facts["compiled"]),
                         (inv.REFERENCED, "compiles only with a missing include read as empty"))
        reading = script("data/MissionScripts/level999/broken.msl", b"init(\r\n")
        self.assertEqual((account_of(reading)["class"], reading.facts["compiled"]), (inv.REFERENCED, "does not compile alone"))
        header = script("data/MissionScripts/textlist.h", b"// ids\r\n#define TEXT_ONE 12\r\n")
        self.assertEqual((account_of(header)["class"], header.facts["compiled"]), (inv.DECODED, "a header"))
        header = script("data/MissionScripts/textlist.h", b"int x;\r\n")
        self.assertEqual(account_of(header)["class"], inv.REFERENCED)

    def test_a_shipped_copy_a_source_does_not_reproduce_is_reported_beside_one_it_does(self):
        source = b"init()\r\n{\r\n\tPause(2);\r\n}\r\n"
        cases = {("exact", "different"): (inv.REFERENCED, ["1 of 2 shipped copies compiled from this source: different"]),
                 ("stale source", "different"): (inv.REFERENCED,
                                                 ["1 of 2 shipped copies compiled from this source: different"]),
                 ("exact", "refused", "refused"): (inv.REFERENCED,
                                                   ["2 of 3 shipped copies compiled from this source: refused"]),
                 ("exact", "stale source"): (inv.REFERENCED, []),
                 ("exact", "exact, assisted"): (inv.DECODED, [])}
        for number, (verdicts, (klass, problems)) in enumerate(cases.items()):
            rel = f"data/MissionScripts/level100/mixed{number}.msl"
            self.ctx.msl[rel.casefold()] = list(verdicts)
            reading = self.script(rel, source)
            self.assertEqual((account_of(reading)["class"], reading.problems), (klass, problems), verdicts)

    def test_no_level_folder_source_is_judged_when_a_level_archive_s_worlds_do_not_read(self):
        source = b"init()\r\n{\r\n\tPause(2);\r\n}\r\n"
        self.ctx.msl_unread["data/resources/300_res_PC.aya"] = "EncodeError: authored refusal"
        self.ctx.msl["data/missionscripts/level300/judged.msl"] = ["exact"]
        # A source with a verdict and one no readable archive ships are both in level folders: the unread archive's
        # base world could be either folder, so neither is decoded, and each says why.
        for rel in ("data/MissionScripts/level300/judged.msl", "data/MissionScripts/level301/alone.msl"):
            reading = self.script(rel, source)
            self.assertEqual((account_of(reading)["class"], len(reading.problems)), (inv.REFERENCED, 1), rel)
            self.assertIn("could not read 1 level archives' worlds", reading.problems[0])
        outside = self.script("data/MissionScripts/shared.msl", source)  # no level ships a source outside a level folder
        self.assertEqual((account_of(outside)["class"], outside.problems), (inv.DECODED, []))
        archive = inv.read_archive(catalog_fixtures.world_archive(), self.ctx, {"path": "data/resources/300_res_PC.aya"})
        self.assertIn("the mission-script judge could not read this archive's worlds (EncodeError: authored refusal)",
                      archive.problems)

    def test_image_metadata_reads_the_stored_alpha(self):
        png = inv.read_png(media_fixtures.png_file(colour=6), self.ctx, {"path": "Manuals/a.png", "family": "manual"})
        fields = png.items[0]["metadata"]["fields"]
        self.assertEqual((fields["alpha"], fields["channels"]), ("present", 4))
        tga = bytearray(media_fixtures.tga_file(bits=32))
        tga[17] = 0x28  # the image descriptor: eight alpha bits, the first row at the top
        meta = inv.read_tga(bytes(tga), self.ctx, {"path": "data/textures/a.tga", "family": "splash-tga"}).items[0]["metadata"]
        self.assertEqual((meta["fields"]["alpha"], meta["fields"]["channels"], meta["details"]["firstRowAtTop"]),
                         ("present", 4, True))
        plain = inv.read_tga(media_fixtures.tga_file(bits=32), self.ctx, {"path": "data/textures/b.tga",
                                                                          "family": "splash-tga"})
        self.assertEqual(plain.items[0]["metadata"]["fields"]["alpha"], "none")  # 32 bits, but no alpha bits declared

    def test_pe_resources_other_than_icons_stay_referenced_and_an_icon_has_its_size(self):
        row = {"path": "BEA.exe", "family": "executable-code"}
        [icon] = inv.read_pe(media_fixtures.pe_file(), self.ctx, row).items
        fields = icon["metadata"]["fields"]
        self.assertEqual((icon["status"], fields["format"], fields["width"], fields["height"], fields["alpha"]),
                         (inv.DECODED, "icon bitmap", 2, 2, "mask"))
        data = bytearray(media_fixtures.pe_file())  # the icon and its group retyped as a cursor and a version resource
        struct.pack_into("<I", data, 0x600 + 16, 1)
        struct.pack_into("<I", data, 0x600 + 24, 16)
        parts = account_of(inv.read_pe(bytes(data), self.ctx, row))["parts"]
        self.assertEqual((parts["pe/resource cursor (framed)"], parts["pe/resource version (framed)"]),
                         ({inv.REFERENCED}, {inv.REFERENCED}))
        self.assertFalse([part for part, classes in parts.items()
                          if part.startswith("pe/resource ") and inv.DECODED in classes])

    def test_a_folder_the_walk_cannot_list_is_refused_and_the_gate_names_it(self):
        game = self.game / "game"
        authored(game)
        out = self.game / "out"
        inv.write_outputs(out, game, inv.build_inventory(game))
        hidden = game / "data/sounds/english"
        hidden.chmod(0)
        try:
            try:
                os.listdir(hidden)
            except PermissionError:
                pass
            else:
                self.skipTest("this account can list a folder without permissions (root)")
            with self.assertRaisesRegex(inv.cc.CatalogInputError, "data/sounds/english: a folder the walk cannot list"):
                inv.build_inventory(game)
            failures = gate.run(game, out, compose=False).failures
            self.assertTrue(any(line.startswith("data/sounds/english: a folder the walk cannot list") for line in failures),
                            failures)
        finally:
            hidden.chmod(0o755)

    def test_a_folder_that_lists_its_names_but_cannot_be_searched_is_refused_and_the_gate_names_it(self):
        game = self.game / "game"
        authored(game)
        out = self.game / "out"
        inv.write_outputs(out, game, inv.build_inventory(game))
        closed = game / "data/music"  # mode 0444: its names list, its entries cannot be examined
        closed.chmod(0o444)
        try:
            try:
                (closed / "track.ogg").lstat()
            except PermissionError:
                pass
            else:
                self.skipTest("this account can search a folder without permissions (root)")
            with self.assertRaisesRegex(inv.cc.CatalogInputError, "data/music: a folder the walk cannot search"):
                inv.build_inventory(game)
            failures = gate.run(game, out, compose=False).failures
            self.assertTrue(any(line.startswith("data/music: a folder the walk cannot search") for line in failures),
                            failures)
        finally:
            closed.chmod(0o755)

    def test_an_install_holding_a_link_is_refused_and_the_gate_names_it(self):
        game = self.game / "game"
        authored(game)
        out = self.game / "out"
        inv.write_outputs(out, game, inv.build_inventory(game))
        outside = self.game / "authored-outside"
        outside.mkdir()
        (outside / "inside.txt").write_bytes(b"inside\n")
        try:
            (game / "data/linked").symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"creating a directory symlink is unavailable: {error}")
        with self.assertRaisesRegex(inv.AccountError, "data/linked: a link or special file"):
            inv.build_inventory(game)
        failures = gate.run(game, out, compose=False).failures
        self.assertIn("data/linked: a link or special file, which no account holds", failures)


class AnimationMetadataTests(unittest.TestCase):
    def record(self, start: int, last: int, scaler: int, rate: float | None) -> dict:
        return {"animation": {"mode": 1, "startFrame": start, "lastFrame": last, "frameScaler": scaler, "rate": rate,
                              "rateSemantics": "normalized-mode-increment-per-game-tick",
                              "skeleton": {"mesh": "mesh:authored", "animatedParts": []}}}

    def test_frames_count_either_way_and_a_rate_up_to_the_smallest_plays_at_one(self):
        cases = {(0, 10, 10, 0.1): (11, 0.5), (20, 10, -10, 0.1): (11, 0.5), (5, 5, 0, 0.5): (1, 0.1),
                 (0, 7, 8, 0.0001): (8, 0.05), (0, 7, 8, -2.0): (8, 0.05), (0, 3, 3, 0.00011): (4, 454.545),
                 (3, 0, -3, None): (4, None)}
        for (start, last, scaler, rate), wanted in cases.items():
            with self.subTest(start=start, last=last, rate=rate):
                fields, details = inv.animation_metadata(self.record(start, last, scaler, rate))
                self.assertEqual((fields["frames"], fields["durationSeconds"]), wanted)
                self.assertEqual((fields["format"], details["frameScaler"]), ("camd", scaler))

    def test_a_chained_mode_that_runs_backwards_counts_its_frames(self):
        reading = inv.Reading(inv.Account(0), "inflated", "authored")
        inv.chained_items([reverse_mesh()], "mesh:owner", "data/resources/meshes/m_owner.msh.aya",
                          "aya-zlib-members(cmsh)", reading)
        modes = {item["name"]: item["metadata"] for item in reading.items if item["form"] == "chained-animation"}
        got = {name: (meta["fields"]["frames"], meta["fields"]["durationSeconds"], meta["details"]["frameScaler"])
               for name, meta in modes.items()}
        self.assertEqual(got, {"ahead": (9, 0.4, 8), "back": (11, 0.2, -10), "still": (5, 0.05, 4),
                               "tiny": (3, 0.05, 2)})
        self.assertEqual({item["offset"] for item in reading.items}, {None})  # a chain's links carry no coordinates


class ChainedTextureTests(unittest.TestCase):
    def test_a_chained_mesh_slot_joins_within_its_parent_s_archives(self):
        def descriptor(ident: str, archive: str) -> dict:
            return {"id": ident, "type": "texture-descriptor", "name": "meshtex\\Skin.tga", "relationships": [],
                    "textureDescriptor": {"status": "parsed", "levels": -1, "requestedFormat": 1,
                                          "occurrences": [{"archive": archive}]}}

        catalog = {"assets": [
            descriptor("texture-descriptor:here", "data/resources/100_res_PC.aya"),
            descriptor("texture-descriptor:elsewhere", "data/resources/200_res_PC.aya"),
            {"id": "mesh:parent", "type": "mesh", "relationships": [
                {"type": "loaded-by-archive", "target": "archive:data/resources/100_res_pc.aya"}]}]}
        found = [{"form": "chained-mesh", "owner": "mesh:parent", "textureSlots": [
            ["MESHTEX\\skin.tga", "utf8-decoded", 1], ["", "empty", None], ["meshtex\\gone.tga", "utf8-decoded", 1],
            ["meshtex\\Skin.tga", "invalid-utf8", 1]]}]
        incoming: dict = __import__("collections").defaultdict(set)
        outcome = inv.join_chained_textures(found, catalog, incoming)
        self.assertEqual(dict(incoming), {"texture-descriptor:here": {"chained-mesh:uses-texture"}})
        self.assertEqual(outcome, {"slots joined": 1, "slots unresolved": 1, "slots without a joinable name": 2})
        self.assertNotIn("textureSlots", found[0])


class DecoderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.decoder = self.root / "fake-decoder"
        self.decoder.write_text(FAKE_DECODER, encoding="utf-8")
        self.decoder.chmod(self.decoder.stat().st_mode | stat.S_IXUSR)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_the_decoder_s_frame_lines_become_stream_counts(self):
        (self.root / "a.vid").write_bytes(b"x")
        result = inv.decode_media(self.root / "a.vid", str(self.decoder))
        self.assertTrue(result["clean"])
        self.assertEqual(result["streams"], {"0": {"frames": 2, "bytes": 18432}, "1": {"frames": 1, "bytes": 2048}})

    def test_an_error_is_not_clean(self):
        (self.root / "broken.ogg").write_bytes(b"x")
        self.assertFalse(inv.decode_media(self.root / "broken.ogg", str(self.decoder))["clean"])

    def test_agreement_needs_the_walk_s_own_counts(self):
        ogg = {"channels": 1, "samples": 4410}
        good = {"clean": True, "streams": {"0": {"frames": 3, "bytes": 8820}}}
        self.assertTrue(inv.decoder_agrees(good, ogg, "ogg-voice"))
        self.assertFalse(inv.decoder_agrees({**good, "streams": {"0": {"frames": 3, "bytes": 8818}}}, ogg, "ogg-voice"))
        self.assertFalse(inv.decoder_agrees({**good, "clean": False}, ogg, "ogg-voice"))
        bink = {"frames": 2, "audioTracks": 1}
        self.assertFalse(inv.decoder_agrees({"clean": True, "streams": {"0": {"frames": 2, "bytes": 1}}}, bink,
                                            "bink-video"))
        self.assertFalse(inv.decoder_agrees(None, bink, "bink-video"))

    def test_an_agreeing_decoder_turns_the_payload_decoded(self):
        game = self.root / "game"
        authored(game)
        rows = {r["path"]: r for r in inv.build_inventory(game, decoder=str(self.decoder), jobs=2)["files"]}
        self.assertEqual(rows["data/sounds/english/MessageBox/line.ogg"]["class"], inv.DECODED)
        self.assertEqual(rows["data/video/intro.vid"]["class"], inv.DECODED)
        self.assertEqual(rows["data/video/intro.vid"]["facts"]["decoder"], "agrees")

    def test_the_bytes_that_count_only_on_the_decoder_s_word_are_the_ones_no_reader_reads(self):
        game = self.root / "game"
        authored(game)
        rows = {r["path"]: r for r in inv.build_inventory(game, decoder=str(self.decoder), jobs=2)["files"]}
        # An Ogg's decoder-only bytes are its two audio packets (300 and 40 bytes): its setup header is read here.
        self.assertEqual(rows["data/sounds/english/MessageBox/line.ogg"]["facts"][inv.DECODER_ONLY], 340)
        # A Bink's are its one track's 12-byte descriptor, its audio packets (8 and 4) and its video packets (30 and 50).
        self.assertEqual(rows["data/video/intro.vid"]["facts"][inv.DECODER_ONLY], 12 + 12 + 80)

    def test_the_headline_gives_both_shares_and_the_one_without_matches_a_run_without(self):
        game = self.root / "game"
        authored(game)
        with_decoder = inv.build_inventory(game, decoder=str(self.decoder), jobs=2)["coverage"]
        without = inv.build_inventory(game)["coverage"]
        head = with_decoder["headline"]
        self.assertEqual(head["mediaDecoder"], with_decoder["mediaDecoder"])
        self.assertGreater(head["decodedOnlyByTheMediaDecoder"], 0)
        self.assertEqual(head["withoutMediaDecoder"], without["headline"]["withoutMediaDecoder"])
        self.assertEqual(head["withMediaDecoder"]["decodedBytes"] - head["decodedOnlyByTheMediaDecoder"],
                         head["withoutMediaDecoder"]["decodedBytes"])
        line = inv.summary_lines(with_decoder)[-1]
        self.assertIn(f"{head['withMediaDecoder']['percent']}% of {head['contentLogicalBytes']} logical bytes", line)
        self.assertIn(f"; {head['withoutMediaDecoder']['percent']}% ({head['withoutMediaDecoder']['decodedBytes']}) "
                      "without it", line)


class GateTests(unittest.TestCase):
    def test_an_archive_whose_worlds_do_not_read_is_recorded_not_fatal(self):
        unread: dict = {}
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp) / "game"
            authored(game)
            inv.judge_mission_scripts(game, unread)
        # The authored levels 100 and 101 hold no WRES, so they ship no script. Level 200's authored world is one zlib
        # member that inflates past world_resources_encode's member limit, which the inventory's own archive reader
        # does not have: the judge records it and the run goes on.
        self.assertEqual(list(unread), ["data/resources/200_res_PC.aya"])
        self.assertIn("member limit", unread["data/resources/200_res_PC.aya"])

    def test_the_gate_fails_while_the_judge_could_not_read_an_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp) / "game"
            authored(game)
            out = Path(temp) / "out"
            inv.write_outputs(out, game, inv.build_inventory(game))
            self.assertIn("the mission-script judge could not read 1 level archives' worlds",
                          gate.run(game, out, compose=False).failures)
            coverage = json.loads((out / "coverage.json").read_text(encoding="utf-8"))
            del coverage["proofs"][inv.MSL_UNREAD]
            (out / "coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
            self.assertIn("the run does not say whether the mission-script judge read every level archive's worlds",
                          gate.run(game, out, compose=False).failures)

    def test_the_gate_reports_what_disagrees(self):
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp) / "game"
            authored(game)
            out = Path(temp) / "out"
            inv.write_outputs(out, game, inv.build_inventory(game))
            report = gate.run(game, out, compose=False)
            text = "\n".join(report.failures)
            self.assertIn("BEA.exe: 1 reader problems", text)
            self.assertIn("the independent decoder did not agree (not run)", text)
            self.assertGreater(report.counts["records whose coordinates hash to their SHA-256"], 0)
            self.assertEqual(report.counts["accounts checked"], sum(1 for p in game.rglob("*") if p.is_file()))
            (game / "data/Dial.raw").write_bytes(bytes(511))
            (game / "added.txt").write_bytes(b"new\n")
            text = "\n".join(gate.run(game, out, compose=False).failures)
            self.assertIn("data/Dial.raw: the run's size differs from the folder's", text)
            self.assertIn("added.txt: in the folder only", text)

    def test_a_tampered_record_hash_is_caught(self):
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp) / "game"
            authored(game)
            out = Path(temp) / "out"
            inv.write_outputs(out, game, inv.build_inventory(game))
            lines = (out / "records.jsonl").read_text(encoding="utf-8").splitlines()
            rows = [json.loads(line) for line in lines]
            target = next(r for r in rows if gate.STREAM_ENVELOPE_RE.match(r["source"]["envelope"]))
            target["sha256"] = "0" * 64
            (out / "records.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
            text = "\n".join(gate.run(game, out, compose=False).failures)
            self.assertIn(f"{target['id']}: the bytes at its coordinates do not hash to its SHA-256", text)


class MetadataGateTests(unittest.TestCase):
    """The gate reads every asset-metadata row's fields again from its own bytes, and fails a row that disagrees, that
    it cannot place, or that breaks the schema."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.game = Path(cls.temp.name) / "game"
        authored(cls.game)
        cls.out = Path(cls.temp.name) / "out"
        inv.write_outputs(cls.out, cls.game, inv.build_inventory(cls.game))
        cls.report = gate.run(cls.game, cls.out, compose=False)
        cls.rows = [json.loads(line) for line in (cls.out / "asset-metadata.jsonl").read_text(encoding="utf-8").splitlines()]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def row(self, rows: list[dict], form: str, name: str | None = None, file: str | None = None) -> dict:
        return next(row for row in rows if row["form"] == form and (name is None or row["name"] == name)
                    and (file is None or row["identity"]["file"] == file))

    def failures_after(self, change) -> list[str]:
        """The gate's failures once change(rows) has edited a copy of the run's asset-metadata rows."""
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out"
            shutil.copytree(self.out, out)
            rows = copy.deepcopy(self.rows)
            change(rows)
            (out / "asset-metadata.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            return gate.run(self.game, out, compose=False).failures

    def test_every_row_is_read_again_and_agrees(self):
        ids = {row["id"] for row in self.rows}
        # The imposter atlas's catalogue record lies on the flatly framed IMPS the walk refuses: a records-check
        # failure of this authored install, not a metadata one.
        about_rows = [line for line in self.report.failures
                      if (line.split(": ")[0] in ids or line.startswith("asset-metadata.jsonl"))
                      and not line.endswith("it lies on bytes the account calls unknown")]
        self.assertEqual(about_rows, [])
        counts = self.report.counts
        self.assertEqual(counts["metadata rows whose every field equals the gate's reading"]
                         + counts["unplaced metadata rows whose fields follow their details"], len(self.rows))
        forms = {row["form"] for row in self.rows}
        self.assertLessEqual({"dds-file", "descriptor-text", "png", "tga", "jpeg", "byte-sprite", "pe-icon", "voice",
                              "music", "bank-sample", "video", "animation", "loose-mesh", "terrain-heightfield",
                              "surface-strips", "static-shadow-maps", "terrain-mixer-mip", "damage-texture"}, forms)

    def test_a_field_that_disagrees_with_the_bytes_fails(self):
        tampered: list[tuple[str, str]] = []

        def change(rows: list[dict]) -> None:
            edits = [(self.row(rows, "dds-file", file="data/resources/dxtntextures/extra%graded.tga(0)DXT2.aya"),
                      {"mipLevels": 1, "channels": 3}),
                     (self.row(rows, "dds-file", file="data/resources/dxtntextures/meshtex%skin.tga(0)A1R5G5B5.aya"),
                      {"format": "DXT5", "width": 5}),
                     (self.row(rows, "descriptor-text", name="meshtex\\skin.tga"), {"height": 8, "frames": None}),
                     (self.row(rows, "png", name="orphan.png"), {"channels": 4}),
                     (self.row(rows, "tga"), {"alpha": "present"}), (self.row(rows, "jpeg"), {"channels": None}),
                     (self.row(rows, "pe-icon", file="Setup.exe"), {"alpha": "mask"}),
                     (self.row(rows, "voice", name="line"), {"channels": 2}),
                     (self.row(rows, "music", name="track"), {"sampleRate": 22050}),
                     (self.row(rows, "bank-sample"), {"durationSeconds": 1.0}),
                     (self.row(rows, "video", name="intro"), {"durationSeconds": None, "frames": 3}),
                     (self.row(rows, "animation", name="walk"), {"frames": 10}),
                     (self.row(rows, "animation", name="back"), {"durationSeconds": 0.4}),
                     (self.row(rows, "loose-mesh"), {"format": None}),
                     (self.row(rows, "damage-texture"), {"width": None}),
                     (self.row(rows, "terrain-heightfield"), {"format": "cmsh"}),
                     (self.row(rows, "static-shadow-maps"), {"alpha": "none"}),
                     (self.row(rows, "terrain-mixer-mip"), {"format": "DXT1"}),
                     (self.row(rows, "byte-sprite"), {"channels": 3})]
            if gate.Image is not None:  # without Pillow the gate cannot read a DDS's alpha again, and says so
                edits.append((self.row(rows, "dds-file", file="data/resources/textures/mustbe_extra%binary.tga(0)"
                                                               "A8R8G8B8.aya"), {"alpha": "graded"}))
            for row, values in edits:
                row.update(values)
                tampered.extend((row["id"], field) for field in values)

        failures = self.failures_after(change)
        for asset_id, field in tampered:
            self.assertIn(f"{asset_id}: its {field} is not what the gate reads", failures)

    def test_details_that_disagree_with_the_bytes_fail(self):
        def change(rows: list[dict]) -> None:
            self.row(rows, "animation", name="ahead")["details"]["startFrame"] = 1
            self.row(rows, "animation", name="back")["details"]["frameScaler"] = 10
            self.row(rows, "dds-file", file="data/resources/dxtntextures/extra%graded.tga(0)DXT2.aya")["details"]["mips"][2][
                "sha256"] = "0" * 64
            self.row(rows, "descriptor-text", name="meshtex\\skin.tga")["details"]["mipLevelsPerFrame"] = [2]

        failures = self.failures_after(change)
        rows = self.rows
        for form, where, line in (("animation", {"name": "ahead"}, "its frame range, scaler or rate details are not its record's"),
                                  ("animation", {"name": "back"}, "its frame range, scaler or rate details are not its record's"),
                                  ("dds-file", {"file": "data/resources/dxtntextures/extra%graded.tga(0)DXT2.aya"},
                                   "its mip details are not its header's chain"),
                                  ("descriptor-text", {"name": "meshtex\\skin.tga"},
                                   "its mips per frame are not its frame records'")):
            self.assertIn(f"{self.row(rows, form, **where)['id']}: {line}", failures)

    def test_an_unplaced_row_follows_its_details(self):
        # No authored mesh chains (the authored meshes fail the loader grammar), so a chained mode's row is built here.
        fields, details = inv.animation_metadata({"animation": {
            "mode": 1, "startFrame": 20, "lastFrame": 10, "frameScaler": -10, "rate": 0.25,
            "rateSemantics": "normalized-mode-increment-per-game-tick",
            "skeleton": {"mesh": "mesh:owner", "animatedParts": []}}})
        mesh_file = {"sha256": "1" * 64, "family": "cmsh-mesh", "stream": "inflated"}
        asset = {"id": "animation:mesh:owner/chained#0/0", "kind": "animation", "form": "chained-animation",
                 "details": details, **fields,
                 "identity": {"fileSha256": "1" * 64, "envelope": "aya-zlib-members(cmsh)/chain#0", "offset": None,
                              "length": 36}}
        for frames, wanted, agreeing in ((11, [], 1), (-9, [f"{asset['id']}: its frames is not what the gate reads"], 0)):
            report = gate.Report()
            gate.check_metadata(gate.FileView(mesh_file, b"", b""), [dict(asset, frames=frames)], report, {})
            self.assertEqual(report.failures, wanted)
            self.assertEqual(report.counts["unplaced metadata rows whose fields follow their details"], agreeing)
        archive = {"sha256": "1" * 64, "family": "lvlr-resource-archive", "stream": "inflated"}
        mixer = {**asset, **dict.fromkeys(inv.METADATA_FIELDS), "id": "texture:mixer", "kind": "texture",
                 "form": "terrain-mixer-mip", "format": "one byte per texel",
                 "identity": {**asset["identity"], "envelope": "lvlr-chunk(ERES)"}}
        report = gate.Report()
        # The mixer mips' item offset is their ERES chunk's payload; nothing establishes a mixer mip's fields.
        gate.check_metadata(gate.FileView(archive, b"", catalog_fixtures.chunk(b"ERES", bytes(16))), [mixer], report,
                            {"texture:mixer": {"offset": 8}})
        self.assertEqual(report.failures, ["texture:mixer: its format is not what the gate reads"])
        report = gate.Report()
        gate.check_metadata(gate.FileView(archive, b"", catalog_fixtures.chunk(b"TEXT", bytes(16))),
                            [dict(mixer, format=None)], report, {"texture:mixer": {"offset": 8}})
        self.assertEqual(report.failures, ["texture:mixer: its item does not lie in an ERES chunk of the archive"])

    def test_a_row_the_gate_cannot_place_fails(self):
        def change(rows: list[dict]) -> None:
            self.row(rows, "video", name="intro")["identity"]["envelope"] = "film(bink)"
            self.row(rows, "dds-file", file="data/resources/dxtntextures/unused.tga(0)A1R5G5B5.aya")["identity"]["offset"] = None
            self.row(rows, "loose-mesh")["identity"]["length"] = 0
            self.row(rows, "pe-icon", file="Setup.exe")["identity"]["offset"] = None

        failures = self.failures_after(change)
        rows = self.rows
        self.assertIn(f"{self.row(rows, 'video', name='intro')['id']}: its envelope is not a video's in a bink-video file",
                      failures)
        for form, where in (("dds-file", {"file": "data/resources/dxtntextures/unused.tga(0)A1R5G5B5.aya"}),
                            ("loose-mesh", {}), ("pe-icon", {"file": "Setup.exe"})):
            self.assertIn(f"{self.row(rows, form, **where)['id']}: a {form} row without coordinates", failures)

    def test_identities_and_the_row_set_are_checked(self):
        added: dict = {}

        def change(rows: list[dict]) -> None:
            self.row(rows, "video", name="intro")["identity"]["sha256"] = "0" * 64
            self.row(rows, "descriptor-text", name="meshtex\\skin.tga")["identity"]["sha256"] = "0" * 64
            self.row(rows, "png", name="orphan.png")["identity"]["fileSha256"] = "0" * 64
            rows.append(copy.deepcopy(self.row(rows, "tga")))
            stray = copy.deepcopy(self.row(rows, "byte-sprite"))
            stray["id"] = "image:no-such-item"
            rows.append(stray)
            elsewhere = self.row(rows, "animation", name="still")
            elsewhere["identity"]["file"] = "data/resources/meshes/m_gone.msh.aya"
            added.update(stray=stray["id"])

        failures = self.failures_after(change)
        rows = self.rows
        for form, name, line in (("video", "intro", "the bytes at its coordinates do not hash to its SHA-256"),
                                 ("descriptor-text", "meshtex\\skin.tga",
                                  "the bytes at its coordinates do not hash to its SHA-256"),
                                 ("png", "orphan.png", "its file hash is not its file's"),
                                 ("tga", None, "2 asset-metadata rows")):
            self.assertIn(f"{self.row(rows, form, name=name)['id']}: {line}", failures)
        self.assertIn(f"{added['stray']}: an asset-metadata row for no texture, image, model, animation, sound or film "
                      "item", failures)
        self.assertIn("data/resources/meshes/m_gone.msh.aya: 1 asset-metadata rows for a file the gate did not check",
                      failures)
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out"
            shutil.copytree(self.out, out)
            (out / "asset-metadata.jsonl").unlink()
            self.assertIn("the run wrote no asset-metadata.jsonl", gate.run(self.game, out, compose=False).failures)

    def failures_after_items(self, change_rows, change_items=None, change_records=None) -> list[str]:
        """The gate's failures once change_rows has edited a copy of the run's asset-metadata rows and change_items
        (and change_records) the run's item (and catalogue record) rows, as one who tampers with every file would."""
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out"
            shutil.copytree(self.out, out)
            for name, change in (("asset-metadata.jsonl", change_rows), ("items.jsonl", change_items),
                                 ("records.jsonl", change_records)):
                if change is not None:
                    rows = [json.loads(line) for line in (out / name).read_text(encoding="utf-8").splitlines()]
                    change(rows)
                    (out / name).write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            return gate.run(self.game, out, compose=False).failures

    @staticmethod
    def blank(row: dict, **keep) -> None:
        for field in inv.METADATA_FIELDS:
            row[field] = keep.get(field)

    def named(self, failures: list[str], asset_id: str, line: str | None = None) -> bool:
        return any(failure.startswith(f"{asset_id}: ") and (line is None or failure == f"{asset_id}: {line}")
                   for failure in failures)

    def test_a_row_that_claims_to_be_another_form_or_unparsed_fails(self):
        """Single rows tampered with: a form claim that switched the placement and field checks off, and a status claim
        that dropped every field, each once passed the gate with no failure; so did a changed kind, status or use."""
        chosen: dict[str, tuple[str, str]] = {}

        def change(rows: list[dict]) -> None:
            dds = self.row(rows, "dds-file", file="data/resources/dxtntextures/extra%graded.tga(0)DXT2.aya")
            dds.update(form="chained-mesh")
            dds["identity"]["offset"] = None
            self.blank(dds, format="cmsh")
            chosen["a DDS row claims to be a mesh chain's link"] = (dds["id"], "its form is not its item's")
            voice = self.row(rows, "voice", name="line")
            voice.update(form="terrain-mixer-mip")
            voice["identity"]["offset"] = None
            self.blank(voice)
            chosen["a voice row claims to be a terrain mixer mip"] = (voice["id"], "its form is not its item's")
            icon = self.row(rows, "pe-icon", file="Setup.exe")
            icon.update(form="pe-bitmap")
            self.blank(icon)
            chosen["an icon row claims to be a bitmap"] = (icon["id"], "its form is not its item's")
            for form, selector, key, value, label in (
                    ("dds-file", {"file": "data/resources/textures/mustbe_extra%binary.tga(0)A8R8G8B8.aya"}, "ddsStatus",
                     "malformed", "a DDS"),
                    ("music", {"name": "track"}, "audioStatus", "refused", "a music track"),
                    ("video", {"name": "intro"}, "videoStatus", "refused", "a film"),
                    ("descriptor-text", {"name": "meshtex\\skin.tga"}, "descriptorStatus", "refused", "a texture record")):
                row = self.row(rows, form, **selector)
                row["details"][key] = value
                self.blank(row)
                chosen[f"{label} row says it was refused and drops every field"] = (
                    row["id"], f"its {key} calls bytes the gate reads unparsed")
            music = self.row(rows, "music", name="track")
            music["status"] = "referenced" if music["status"] == "decoded" else "decoded"
            chosen["a music row's status is flipped"] = (music["id"], "its status is not its item's")
            dds_two = self.row(rows, "dds-file", file="data/resources/dxtntextures/unused.tga(0)A1R5G5B5.aya")
            dds_two["kind"] = "image"
            chosen["a DDS row's kind is changed"] = (dds_two["id"], "its kind is not its item's")
            hello = self.row(rows, "voice", name="hello")
            hello["used"] = not hello["used"]
            hello["usedBy"] = []
            chosen["a voice row says nothing uses it"] = (hello["id"], "its used is not its item's")

        failures = self.failures_after(change)
        for label, (asset_id, line) in chosen.items():
            self.assertTrue(self.named(failures, asset_id, line), (label, [f for f in failures if asset_id in f]))

    def test_a_row_and_its_item_relabelled_together_still_fail_against_the_file(self):
        """Tampering with items.jsonl as well as the row leaves the file, which holds what it holds."""
        rows_file = {}

        def change_rows(rows: list[dict]) -> None:
            dds = self.row(rows, "dds-file", file="data/resources/dxtntextures/extra%graded.tga(0)DXT2.aya")
            dds.update(form="chained-mesh")
            dds["identity"].update(offset=None, envelope="aya-zlib-members(cmsh)/chain#0")
            self.blank(dds, format="cmsh")
            voice = self.row(rows, "voice", name="line")
            voice.update(form="terrain-mixer-mip")
            voice["identity"]["offset"] = None
            self.blank(voice)
            icon = self.row(rows, "pe-icon", file="Setup.exe")
            icon.update(form="pe-bitmap")
            icon["identity"]["envelope"] = "pe-resource(bitmap)"
            self.blank(icon)
            png = self.row(rows, "png", name="orphan.png")
            png.update(form="tga")
            png["identity"]["offset"] = 0
            rows_file.update(dds=dds["id"], voice=voice["id"], icon=icon["id"], png=png["id"])

        def change_items(rows: list[dict]) -> None:
            for item in rows:
                if item["id"] == rows_file["dds"]:
                    item.update(form="chained-mesh", offset=None)
                elif item["id"] == rows_file["voice"]:
                    item.update(form="terrain-mixer-mip")
                elif item["id"] == rows_file["icon"]:
                    item.update(form="pe-bitmap")
                elif item["id"] == rows_file["png"]:
                    item.update(form="tga")

        failures = self.failures_after_items(change_rows, change_items)
        for label, line in (("dds", "a chained-mesh is not held by a dds-texture-dxtn file"),
                            ("voice", "a terrain-mixer-mip is not held by a ogg-voice file"),
                            ("icon", "the executable's resource tree makes it a icon, not what its form says"),
                            ("png", "a tga is not held by a manual file")):
            self.assertTrue(self.named(failures, rows_file[label], line), (label, [f for f in failures if rows_file[label] in f]))

    def test_a_row_that_disagrees_with_the_catalogue_record_fails(self):
        target = {}

        def change_rows(rows: list[dict]) -> None:
            dds = self.row(rows, "dds-file", file="data/resources/dxtntextures/extra%graded.tga(0)DXT2.aya")
            dds["identity"]["envelope"] = "aya-zlib-members(dds)/other"
            dds["identity"]["chunkPath"] = [3]
            target["id"] = dds["id"]
            asset = self.row(rows, "voice", name="line")
            asset["identity"]["file"] = asset["identity"]["file"].replace("line", "Line")
            target["voice"] = asset["id"]

        failures = self.failures_after_items(change_rows)
        self.assertTrue(self.named(failures, target["id"], "its identity's envelope is not its catalogue record's"))
        self.assertTrue(self.named(failures, target["id"], "its identity's chunkPath is not its catalogue record's"))
        self.assertTrue(self.named(failures, target["voice"], "its identity's file is not its item's"))

        def drop_record(rows: list[dict]) -> None:
            rows[:] = [row for row in rows if row["id"] != target["id"]]

        self.assertTrue(self.named(self.failures_after_items(None, None, drop_record), target["id"],
                                   "a dds-file the catalogue does not list"))

    def test_the_forms_places_are_read_from_the_file_not_the_row(self):
        """Each rule of a form's home, on a handmade row: the family, the envelope, the stream, the whole stream, the
        magic and the archive chunk."""
        data = b"OggS" + bytes(20)

        def check(file_row: dict, asset: dict, raw: bytes | None = None, items: dict | None = None) -> list[str]:
            report = gate.Report()
            gate.check_metadata(gate.FileView(file_row, data, raw), [asset], report, items or {})
            return report.failures

        file_row = {"sha256": "2" * 64, "family": "ogg-voice", "stream": "stored", "path": "v.ogg"}
        identity = {"fileSha256": "2" * 64, "envelope": "ogg", "chunkPath": [], "offset": 0, "length": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(), "file": "v.ogg", "sha256Scope": "whole file"}
        asset = {"id": "sound:v", "kind": "sound", "form": "voice", "name": "v", "status": "decoded", "used": False,
                 "usedBy": [], "identity": identity, "details": {"audioStatus": "unparsed"},
                 **dict.fromkeys(inv.METADATA_FIELDS)}
        # These 24 bytes are no Ogg stream the gate can read, and the row says so and claims nothing: no failure.
        self.assertEqual(check(file_row, asset), [])
        # kind, family, envelope and stream
        self.assertEqual(check(file_row, dict(asset, kind="image"))[:1], ["sound:v: a voice is a sound, not a image"])
        self.assertIn("sound:v: a voice is not held by a ogg-music file", check(dict(file_row, family="ogg-music"), asset))
        for envelope in ("whole file", "ogg2", "xogg", "ogg/chain#0"):
            self.assertIn("sound:v: its envelope is not a voice's in a ogg-voice file",
                          check(file_row, dict(asset, identity=dict(identity, envelope=envelope))), envelope)
        self.assertIn("sound:v: a voice lies in a stored stream, which this file's is not",
                      check(dict(file_row, stream="inflated"), asset, raw=data))
        # the whole stream, and the magic
        short = dict(identity, length=8, sha256=hashlib.sha256(data[:8]).hexdigest())
        self.assertIn("sound:v: a voice covers its whole stream, which its coordinates do not",
                      check(file_row, dict(asset, identity=short)))
        wrong = b"RIFF" + data[4:]
        wrong_identity = dict(identity, sha256=hashlib.sha256(wrong).hexdigest())
        report = gate.Report()
        gate.check_metadata(gate.FileView(file_row, wrong, None), [dict(asset, identity=wrong_identity)], report, {})
        self.assertIn("sound:v: its bytes do not open as a voice's do", report.failures)
        # a texture record in the wrong archive chunk
        record = b"DXTX" + bytes(12)
        raw = catalog_fixtures.chunk(b"DMKR", record)
        archive = {"sha256": "2" * 64, "family": "lvlr-resource-archive", "stream": "inflated", "path": "a.aya"}
        text = {"id": "texture:t", "kind": "texture", "form": "descriptor-text", "name": "t", "status": "decoded",
                "used": False, "usedBy": [], "details": {"descriptorStatus": "unparsed"}, **dict.fromkeys(inv.METADATA_FIELDS),
                "identity": {"fileSha256": "2" * 64, "envelope": "lvlr-chunk(TEXT)", "chunkPath": [0], "offset": 8,
                             "length": len(record), "sha256": hashlib.sha256(record).hexdigest(), "file": "a.aya"}}
        report = gate.Report()
        gate.check_metadata(gate.FileView(archive, b"", raw), [text], report, {})
        self.assertIn("texture:t: its bytes do not lie in a TEXT chunk of the archive", report.failures)
        report = gate.Report()
        gate.check_metadata(gate.FileView(archive, b"", catalog_fixtures.chunk(b"TEXT", record)), [text], report, {})
        self.assertNotIn("texture:t: its bytes do not lie in a TEXT chunk of the archive", report.failures)

    def test_whether_bytes_can_be_read_is_the_gate_s_call_both_ways(self):
        def asset(**changes) -> dict:
            return {"id": "sound:v", "form": "voice", "details": {"audioStatus": "unparsed"},
                    **dict.fromkeys(inv.METADATA_FIELDS), **changes}

        def run(row: dict, reads) -> tuple[list[str], int]:
            report = gate.Report()
            gate.compare_fields(row, reads, report, "agreed")
            return report.failures, report.counts["rows neither the gate nor the row can read"]

        def unreadable():
            raise gate.Unreadable("not an Ogg stream")

        # Bytes the gate cannot read, and a row that says so and claims nothing: fine. A row that claims fields, or
        # calls them parsed, fails.
        self.assertEqual(run(asset(), unreadable), ([], 1))
        self.assertEqual(run(asset(channels=2), unreadable)[0], ["sound:v: the gate cannot read its fields: not an Ogg stream"])
        self.assertEqual(run(asset(details={"audioStatus": "parsed"}), unreadable)[0],
                         ["sound:v: the gate cannot read its fields: not an Ogg stream"])
        # Bytes the gate can read: a row that calls them unparsed fails, whatever fields it drops.
        readable = lambda: gate.expect({"samples": 1}, format="vorbis", channels=1, sampleRate=8000, durationSeconds=1.0)
        good = asset(details={"audioStatus": "parsed", "samples": 1}, format="vorbis", channels=1, sampleRate=8000,
                     durationSeconds=1.0)
        self.assertEqual(run(good, readable)[0], [])
        self.assertIn("sound:v: its audioStatus calls bytes the gate reads unparsed", run(asset(), readable)[0])
        self.assertIn("sound:v: its samples detail is not what the gate reads",
                      run(dict(good, details={"audioStatus": "parsed", "samples": 2}), readable)[0])
        # A form with no status of its own is read whatever the row says.
        self.assertEqual(run(asset(form="png", details={}), unreadable)[0],
                         ["sound:v: the gate cannot read its fields: not an Ogg stream"])

    def test_png_tga_jpeg_ogg_bink_animation_and_icon_details_are_read_from_their_bytes(self):
        rows = copy.deepcopy(self.rows)
        for form, name, key in (("png", "orphan.png", "bitDepth"), ("tga", None, "bitsPerPixel"), ("jpeg", None, "precision"),
                                ("voice", "line", "nominalBitrate"), ("music", "track", "samples"),
                                ("video", "intro", "fpsRational"), ("video", "intro", "fps"), ("animation", "ahead", "mode"),
                                ("pe-icon", None, "bitCount"), ("damage-texture", None, "levels"),
                                ("byte-sprite", None, "wholeFramesByLength")):
            row = self.row(rows, form, name=name)
            row["details"][key] = [9] if isinstance(row["details"].get(key), list) else (row["details"].get(key) or 0) + 9
            tampered = self.failures_after(lambda changed, target=row, k=key: self.row(changed, target["form"], name=target["name"],
                                                                                         file=target["identity"]["file"])["details"].update({k: target["details"][k]}))
            self.assertIn(f"{row['id']}: its {key} detail is not what the gate reads", tampered, (form, key))

    def test_a_catalogue_reader_that_refuses_every_file_is_caught_by_the_gate_reading_the_bytes(self):
        """A catalogue Ogg reader changed to refuse every file once left every sound row without a field and the retail
        gate with no failure, because a row that called itself unparsed was not read. The gate reads the bytes."""
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out"
            with patch.object(inv.cc, "ogg_metadata", side_effect=ValueError("refused")), \
                    patch.object(inv.cc, "bink_metadata", side_effect=ValueError("refused")):
                inv.write_outputs(out, self.game, inv.build_inventory(self.game))
            rows = [json.loads(line) for line in (out / "asset-metadata.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertTrue(all(row["details"]["audioStatus"] == "unparsed" for row in rows if row["form"] in ("voice", "music")))
            failures = gate.run(self.game, out, compose=False).failures
        for form, key in (("voice", "audioStatus"), ("music", "audioStatus"), ("video", "videoStatus")):
            for row in rows:
                if row["form"] == form and row["name"] in ("line", "track", "intro"):
                    self.assertTrue(self.named(failures, row["id"], f"its {key} calls bytes the gate reads unparsed"),
                                    (form, [f for f in failures if row["id"] in f]))

    def test_a_row_that_breaks_the_schema_fails_the_gate(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("jsonschema is not installed")
        self.assertEqual(self.report.counts["asset-metadata.jsonl rows checked against the schema"], len(self.rows))

        def change(rows: list[dict]) -> None:
            self.row(rows, "animation", name="back")["frames"] = -9  # what the retail reverse modes once gave

        back = self.row(self.rows, "animation", name="back")["id"]
        self.assertIn(f"asset-metadata.jsonl: {back}: frames fails the schema's minimum rule", self.failures_after(change))

    def test_a_file_the_gate_cannot_read_is_a_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp) / "game"
            shutil.copytree(self.game, game)
            locked = game / "data/Dial.raw"
            locked.chmod(0)
            try:
                try:
                    locked.read_bytes()
                except PermissionError:
                    pass
                else:
                    self.skipTest("this account can read a file without permissions (root)")
                failures = gate.run(game, self.out, compose=False).failures
            finally:
                locked.chmod(0o644)
        self.assertTrue(any(line.startswith("data/Dial.raw: a file the gate cannot read") for line in failures), failures)


class GateReaderTests(unittest.TestCase):
    """The gate's own readers on handmade bytes, for decisions no authored install's rows reach."""

    def test_floats_agree_to_a_nanosecond_and_no_nearer(self):
        self.assertTrue(gate.same(0.1 + 0.2, 0.3))
        self.assertTrue(gate.same(1, 1))
        self.assertFalse(gate.same(1.0, 1.0 + 1e-6))
        self.assertFalse(gate.same(0.5, None))
        self.assertFalse(gate.same(None, 0.5))
        self.assertFalse(gate.same(1, True))  # the same value in another type is another value

    def test_an_ogg_s_samples_and_duration_come_from_its_last_page(self):
        data = (media_fixtures.page(2, 0, 0, [media_fixtures.identification(1, 22050)])
                + media_fixtures.page(0, 0, 1, [media_fixtures.comment(), media_fixtures.setup_header()])
                + media_fixtures.page(0, 1000, 2, [b"\x00" * 50]) + media_fixtures.page(4, 4410, 3, [b"\x01" * 30]))
        fields = gate.ogg_fields({"details": {}}, data)
        self.assertEqual((fields["durationSeconds"], fields["_details"]["samples"]), (0.2, 4410))
        self.assertEqual((fields["channels"], fields["sampleRate"], fields["_details"]["nominalBitrate"]), (1, 22050, 64000))
        with self.assertRaises(gate.Unreadable):
            gate.ogg_fields({"details": {}}, data[:-3])  # the last page no longer ends at the end of the file

    def test_a_bank_sample_s_length_is_a_quarter_of_its_pcm_size_rounded_up(self):
        stream = struct.pack("<I", 100) + bytes(25)
        fields = gate.bank_sample_fields(stream, 4, 25)
        self.assertEqual((fields["format"], fields["channels"]), ("ima-adpcm-4bit", 1))
        self.assertEqual(gate.bank_sample_fields(struct.pack("<I", 101) + bytes(26), 4, 26)["format"], "ima-adpcm-4bit")
        for start, length in ((4, 24), (4, 26), (0, 25)):
            with self.assertRaises(gate.Unreadable):
                gate.bank_sample_fields(stream, start, length)

    def test_a_damage_texture_s_levels_fill_its_payload_exactly(self):
        fields = gate.damage_fields(struct.pack("<i", 2) + bytes(1 + 4 + 16))
        self.assertEqual((fields["width"], fields["height"], fields["mipLevels"], fields["_details"]), (4, 4, 3, {"levels": 2}))
        self.assertEqual(gate.damage_fields(struct.pack("<i", -1))["mipLevels"], 0)
        for payload in (struct.pack("<i", 2) + bytes(20), struct.pack("<i", 2) + bytes(22), struct.pack("<i", 16) + bytes(8)):
            with self.assertRaises(gate.Unreadable):
                gate.damage_fields(payload)

    def test_a_tga_has_alpha_when_its_descriptor_has_alpha_bits(self):
        plain = gate.tga_fields(media_fixtures.tga_file(2, 2, 24))
        self.assertEqual((plain["alpha"], plain["channels"], plain["_details"]["alphaBits"]), ("none", 3, 0))
        data = bytearray(media_fixtures.tga_file(2, 2, 32))
        data[17] = 0x28  # eight alpha bits, the first row at the top
        alpha = gate.tga_fields(bytes(data))
        self.assertEqual((alpha["alpha"], alpha["channels"], alpha["_details"]),
                         ("present", 4, {"bitsPerPixel": 32, "alphaBits": 8, "firstRowAtTop": True}))

    def test_a_form_the_gate_has_no_reader_for_fails(self):
        report = gate.Report()
        row = {"id": "x:1", "form": "mystery", "details": {}, **dict.fromkeys(inv.METADATA_FIELDS)}
        gate.compare_fields(row, lambda: gate.placed_fields(row, b"", 0, 0, report), report, "agreed")
        self.assertEqual(report.failures, ["x:1: a mystery row, which the gate has no reader for"])
        self.assertEqual(report.counts["agreed"], 0)

    def test_a_png_s_details_come_from_its_header_and_its_chunks(self):
        def png(depth: int, colour: int, interlace: int, chunks: bytes) -> bytes:
            header = struct.pack(">IIBBBBB", 5, 3, depth, colour, 0, 0, interlace)
            return inv.media.PNG_SIGNATURE + media_fixtures.png_chunk(b"IHDR", header) + chunks \
                + media_fixtures.png_chunk(b"IEND", b"")

        plain = gate.png_fields(png(8, 2, 0, b""))
        self.assertEqual(plain["_details"], {"bitDepth": 8, "colourType": 2, "interlace": 0, "transparencyChunk": False})
        self.assertEqual((plain["alpha"], plain["channels"]), ("none", 3))
        keyed = gate.png_fields(png(16, 0, 1, media_fixtures.png_chunk(b"tRNS", bytes(2))))
        self.assertEqual(keyed["_details"], {"bitDepth": 16, "colourType": 0, "interlace": 1, "transparencyChunk": True})
        self.assertEqual((keyed["alpha"], keyed["channels"]), ("present", 1))
        self.assertEqual(gate.png_fields(png(8, 6, 0, b""))["alpha"], "present")

    def test_a_jpeg_s_details_come_from_its_frame_header(self):
        baseline = gate.jpeg_fields(media_fixtures.jpeg_file())
        self.assertEqual(baseline["_details"], {"precision": 8, "process": "baseline"})
        progressive = gate.jpeg_fields(media_fixtures.jpeg_file(marker=0xC2))
        self.assertEqual(progressive["_details"]["process"], "progressive")
        arithmetic = gate.jpeg_fields(media_fixtures.jpeg_file(marker=0xC9))
        self.assertEqual(arithmetic["_details"]["process"], "other")
        twelve = bytearray(media_fixtures.jpeg_file())
        twelve[twelve.index(b"\xff\xc0") + 4] = 12
        self.assertEqual(gate.jpeg_fields(bytes(twelve))["_details"]["precision"], 12)

    def test_an_icon_resource_is_proved_only_when_it_holds_and_is_an_icon(self):
        holds = media_fixtures.pe_file(icon_bits=32)
        walk = inv.media.walk_pe(holds)
        icon = next(r for r in walk.facts["resources"] if r["type"] == "icon")
        body = holds[icon["offset"]:icon["offset"] + icon["length"]]
        proved = gate.icon_fields({"form": "pe-icon"}, body)
        self.assertEqual((proved["format"], proved["alpha"], proved["_details"]),
                         ("icon bitmap", "present", {"bitCount": 32, "resourceStatus": "decoded"}))
        for asset, data in (({"form": "pe-icon"}, body + b"x"), ({"form": "pe-icon"}, body[:20]),
                            ({"form": "pe-bitmap"}, body)):  # extra bytes, too few, and a bitmap whatever it looks like
            framed = gate.icon_fields(asset, data)
            self.assertEqual((framed["format"], framed["_details"]), (None, {"bitCount": None, "resourceStatus": "framed"}))

    def test_an_archive_chunk_holds_only_the_bytes_of_its_payload(self):
        chunks = catalog_fixtures.chunk(b"TEXT", bytes(10)) + catalog_fixtures.chunk(b"MESH", bytes(6))
        view = gate.FileView({"family": "lvlr-resource-archive", "stream": "inflated"}, b"", chunks)
        self.assertEqual(view.chunk_tag(8, 18), b"TEXT")
        self.assertEqual(view.chunk_tag(12, 14), b"TEXT")
        self.assertEqual(view.chunk_tag(26, 32), b"MESH")
        for start, end in ((4, 12), (0, 8), (8, 19), (17, 27), (18, 20), (32, 33), (100, 101)):
            self.assertIsNone(view.chunk_tag(start, end), (start, end))  # a header, a span across chunks, past the end
        self.assertIsNone(gate.FileView({"family": "ogg-voice", "stream": "stored"}, b"x", None).chunk_tag(0, 1))
        self.assertIsNone(gate.FileView({"family": "lvlr-resource-archive", "stream": "inflated"}, b"", b"TEXT\xff\xff\xff\xff")
                          .chunk_tag(8, 9))  # chunks that do not close are no chunks

    def test_a_pe_resource_is_found_by_its_offset_and_its_length_and_its_type(self):
        view = gate.FileView({"family": "executable-code", "stream": "stored"}, b"", None)
        view._resources = [{"type": "icon", "offset": 100, "length": 40, "status": "decoded"},
                           {"type": "bitmap", "offset": 100, "length": 80, "status": "framed"}]
        asset = {"id": "image:x", "form": "pe-icon"}
        for form, start, length, ok in (("pe-icon", 100, 40, True), ("pe-bitmap", 100, 80, True), ("pe-icon", 100, 80, False),
                                         ("pe-icon", 100, 41, False), ("pe-icon", 101, 40, False)):
            report = gate.Report()
            self.assertEqual(gate.check_resource(view, dict(asset, form=form), start, length, report), ok, (form, start, length))
            self.assertEqual(bool(report.failures), not ok)
        view._resources = None  # an executable whose resource tree does not read lists nothing
        self.assertFalse(gate.check_resource(view, asset, 100, 40, gate.Report()))

    def test_a_row_is_held_to_its_item_and_its_record_one_key_at_a_time(self):
        record = {"id": "texture:x", "type": "texture", "sha256": "a" * 64,
                  "source": {"envelope": "aya-zlib-members(dds)", "chunkPath": [], "offset": 0, "length": 70,
                             "container": "Data/T.aya"}}
        item = {"id": "texture:x", "kind": "texture", "form": "dds-file", "name": "t", "status": "decoded", "used": True,
                "usedBy": ["loaded-by-archive"], "file": "data/t.aya", "offset": 0, "length": 70, "sha256": "a" * 64}
        identity = {"file": "data/t.aya", "envelope": "aya-zlib-members(dds)", "chunkPath": [], "offset": 0, "length": 70,
                    "sha256": "a" * 64}
        asset = {"id": "texture:x", "kind": "texture", "form": "dds-file", "name": "t", "status": "decoded", "used": True,
                 "usedBy": ["loaded-by-archive"], "identity": identity}

        def failures(asset_changes=None, identity_changes=None, item_changes=None, with_record=True, record_changes=None):
            report = gate.Report()
            row = dict(asset, **(asset_changes or {}), identity=dict(identity, **(identity_changes or {})))
            if record_changes:
                source = {**record["source"], **record_changes.get("source", {})}
                changed = {**record, **{k: v for k, v in record_changes.items() if k != "source"}, "source": source}
            else:
                changed = record
            gate.check_against_item(row, dict(item, **(item_changes or {})), changed if with_record else None,
                                    {"texture:x": item, "mesh:m": {"file": "data/t.aya", "form": "loose-mesh"}}, report)
            return report.failures

        self.assertEqual(failures(), [])
        for key, value in (("kind", "image"), ("form", "png"), ("name", "u"), ("status", "unknown"), ("used", False),
                           ("usedBy", [])):
            self.assertIn(f"texture:x: its {key} is not its item's", failures({key: value}))
        for key, value in (("file", "data/u.aya"), ("length", 69), ("sha256", "b" * 64), ("owner", "mesh:m")):
            self.assertIn(f"texture:x: its identity's {key} is not its item's", failures(identity_changes={key: value}), key)
        self.assertIn("texture:x: its identity's offset is not its item's", failures(identity_changes={"offset": 4}))
        # an unplaced form is unplaced in both, and no other form is
        self.assertIn("texture:x: it places a chained-mesh, which no reader places",
                      failures({"form": "chained-mesh"}, item_changes={"form": "chained-mesh"}))
        self.assertIn("texture:x: it leaves a dds-file unplaced", failures(identity_changes={"offset": None}))
        self.assertEqual([f for f in failures({"form": "terrain-mixer-mip"}, {"offset": None},
                                              {"form": "terrain-mixer-mip", "offset": 8}, with_record=False)
                          if "unplaced" in f or "places" in f], [])
        # an owner is a mesh of the same file
        chained = dict(item_changes={"form": "chained-mesh", "owner": "mesh:m", "offset": None}, with_record=False)
        self.assertEqual([f for f in failures({"form": "chained-mesh"}, {"offset": None, "owner": "mesh:m"}, **chained)
                          if "owner" in f], [])
        for owner, others in (("mesh:gone", {}), ("texture:x", {}), ("mesh:m", {"file": "data/other.aya"})):
            report = gate.Report()
            by_id = {"texture:x": item, "mesh:m": {"file": "data/t.aya", "form": "loose-mesh", **others},
                     "mesh:gone": None}
            if owner == "mesh:gone":
                del by_id["mesh:gone"]
            gate.check_against_item(dict(asset, form="chained-mesh", identity=dict(identity, offset=None, owner=owner)),
                                    dict(item, form="chained-mesh", owner=owner, offset=None), None, by_id, report)
            self.assertIn("texture:x: its owner is not a mesh of the same file", report.failures, owner)
        # the catalogue: a form it lists must have its record, and a form it does not must not
        self.assertIn("texture:x: a dds-file the catalogue does not list", failures(with_record=False))
        self.assertIn("texture:x: the catalogue lists it, which a png is not",
                      failures({"form": "png"}, item_changes={"form": "png"}))
        self.assertIn("texture:x: the catalogue lists it as a mesh, not as a dds-file", failures(record_changes={"type": "mesh"}))
        for key, value in (("envelope", "other"), ("chunkPath", [1]), ("offset", 4), ("length", 3)):
            self.assertIn(f"texture:x: its identity's {key} is not its catalogue record's",
                          failures(record_changes={"source": {key: value}}), key)
        self.assertIn("texture:x: its identity's hash or file is not its catalogue record's",
                      failures(record_changes={"sha256": "c" * 64}))
        self.assertIn("texture:x: its identity's hash or file is not its catalogue record's",
                      failures(record_changes={"source": {"container": "data/else.aya"}}))
        self.assertEqual(failures(record_changes={"source": {"container": "DATA/T.AYA"}}), [])  # the catalogue folds case

    def test_every_form_the_inventory_writes_has_a_home(self):
        # The forms an authored install's rows carry are forms the gate knows where to find, and each form's kind is
        # one the metadata file lists.
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp) / "game"
            authored(game)
            built = inv.build_inventory(game)
        self.assertLessEqual({asset["form"] for asset in built["assets"]}, set(gate.FORM_HOMES))
        self.assertLessEqual({home.kind for home in gate.FORM_HOMES.values()}, set(inv.METADATA_KINDS))
        self.assertLessEqual(set(gate.UNPLACED_FORMS), set(gate.FORM_HOMES))
        self.assertLessEqual(set(gate.RECORD_TYPES), set(gate.FORM_HOMES))


class BoundaryTests(unittest.TestCase):
    def test_output_outside_ignored_local_data_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            if inv.cc.output_is_ignored_local_data(Path(temp) / "out"):
                self.skipTest("TMPDIR lies inside this checkout's ignored local-data, so a temporary folder is not outside it")
            game = Path(temp) / "game"
            authored(game)
            with patch.object(inv, "write_outputs") as write, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    inv.main(["--game", str(game), "--out", str(Path(temp) / "out"), "--no-media-decoder"])
            write.assert_not_called()

    def test_every_output_row_meets_the_schema(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema = json.loads((Path(inv.__file__).parent / "content_inventory.schema.json").read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp) / "game"
            authored(game)
            out = Path(temp) / "out"
            inv.write_outputs(out, game, inv.build_inventory(game))
            rows = [json.loads(line) for name in ("files.jsonl", "items.jsonl", "asset-metadata.jsonl")
                    for line in (out / name).read_text(encoding="utf-8").splitlines()]
            rows.append(json.loads((out / "coverage.json").read_text(encoding="utf-8")))
            self.assertTrue(any(row["schema"] == inv.METADATA_SCHEMA for row in rows))
            for row in rows:
                errors = sorted(validator.iter_errors(row), key=str)
                self.assertEqual(errors, [], row.get("id") or row.get("path") or "coverage")
            broken = dict(rows[0], **{"class": "guessed"})
            self.assertTrue(list(validator.iter_errors(broken)))
            asset = next(row for row in rows if row["schema"] == inv.METADATA_SCHEMA)
            self.assertTrue(list(validator.iter_errors(dict(asset, alpha="guessed"))))
            self.assertTrue(list(validator.iter_errors({k: v for k, v in asset.items() if k != "identity"})))

    def test_every_output_row_carries_the_retail_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp) / "game"
            authored(game)
            out = Path(temp) / "out"
            written = inv.write_outputs(out, game, inv.build_inventory(game))
            self.assertEqual({p.name for p in written},
                             {"manifest.json", "coverage.json", "files.jsonl", "items.jsonl", "records.jsonl",
                              "asset-metadata.jsonl"})
            for path in written:
                text = path.read_text(encoding="utf-8")
                rows = [json.loads(line) for line in text.splitlines()] if path.suffix == ".jsonl" else [json.loads(text)]
                self.assertTrue(all(row[inv.GENERATED_MARKER] for row in rows), path.name)


if __name__ == "__main__":
    os.environ.pop("DISPLAY", None)
    unittest.main()
