#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks tools/content_inventory.py and its retail gate on an authored install (no game bytes): the byte account's
rules, what each reader claims and refuses, the joins that make a file or asset used, the independent decoder's
agreement rule, and that the gate fails when the run and the folder disagree."""
from __future__ import annotations

import contextlib
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

    def test_a_mission_script_counts_only_when_its_compile_reproduces_the_shipped_copy(self):
        script = lambda rel, data: inv.read_mission_script(data, self.ctx, {"path": rel, "family": "mission-script-msl"})
        source = b"init()\r\n{\r\n\tPause(2);\r\n}\r\n"
        verdicts = {"exact": (inv.DECODED, []), "exact, assisted": (inv.DECODED, []), "stale source": (inv.REFERENCED, []),
                    "different": (inv.REFERENCED, ["no compiled copy reproduces a shipped script"])}
        for verdict, (klass, problems) in verdicts.items():
            rel = "data/MissionScripts/level100/" + verdict.replace(" ", "").replace(",", "") + ".msl"
            self.ctx.msl[rel.casefold()] = [verdict]
            reading = script(rel, source)
            self.assertEqual((account_of(reading)["class"], reading.problems), (klass, problems), verdict)
        self.assertEqual(account_of(script("data/MissionScripts/level999/alone.msl", source))["class"], inv.DECODED)
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


class GateTests(unittest.TestCase):
    def test_an_archive_without_a_world_is_counted_not_fatal(self):
        unread = __import__("collections").Counter()
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp) / "game"
            authored(game)
            inv.judge_mission_scripts(game, unread)
        # The authored levels 100 and 101 have no WRES; level 200's authored world exceeds world_resources_encode's
        # member limit. None of the three stops the run.
        self.assertEqual(unread["mslArchivesWithoutReadableWorlds"], 3)

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


class BoundaryTests(unittest.TestCase):
    def test_output_outside_ignored_local_data_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
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
            rows = [json.loads(line) for name in ("files.jsonl", "items.jsonl")
                    for line in (out / name).read_text(encoding="utf-8").splitlines()]
            rows.append(json.loads((out / "coverage.json").read_text(encoding="utf-8")))
            for row in rows:
                errors = sorted(validator.iter_errors(row), key=str)
                self.assertEqual(errors, [], row.get("id") or row.get("path") or "coverage")
            broken = dict(rows[0], **{"class": "guessed"})
            self.assertTrue(list(validator.iter_errors(broken)))

    def test_every_output_row_carries_the_retail_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp) / "game"
            authored(game)
            out = Path(temp) / "out"
            written = inv.write_outputs(out, game, inv.build_inventory(game))
            self.assertEqual({p.name for p in written},
                             {"manifest.json", "coverage.json", "files.jsonl", "items.jsonl", "records.jsonl"})
            for path in written:
                text = path.read_text(encoding="utf-8")
                rows = [json.loads(line) for line in text.splitlines()] if path.suffix == ".jsonl" else [json.loads(text)]
                self.assertTrue(all(row[inv.GENERATED_MARKER] for row in rows), path.name)


if __name__ == "__main__":
    os.environ.pop("DISPLAY", None)
    unittest.main()
