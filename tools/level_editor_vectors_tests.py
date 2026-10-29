#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks the vector generator for the Companion's level data layer (tools/level_editor_vectors.py): the committed C# vector
file is what the generator writes, the reference dump has the format the C# dump reproduces, the refused bodies are refused
by the reference and every proper prefix of a body is too, an edit changes only the bytes of the edited field, and the
retail table lists a game's world bodies by hash. Authored data only; no game bytes."""
from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import json
import re
import struct
import tempfile
import unittest
import zlib
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import content_catalog_tests as fixtures
import level_editor_vectors as gen
import world_resources_decode as wrd
import world_resources_encode as enc


MAIN_SOURCE = ('FollowWaypoint("Path A", 0);\r\nGetThingRef("Tank 1");  // "skipped" text\r\nPostEvent("Go"); Print("nothing" \r\n"unterminated\r\n'
               'GetThingRef("unit-2"); GetThingRef("UNIT-2");\r\nFollowWaypointWait( "path a" ); GetThingRef("path a"); FollowWaypointX("path a");')


class VectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = gen.build()
        cls.by_name = {v["name"]: v for v in cls.data["valids"]}

    def test_the_committed_c_sharp_file_is_what_the_generator_writes(self) -> None:
        self.assertEqual(gen.canonical(gen.OUTPUT.read_text(encoding="utf-8")), gen.canonical(gen.render(self.data)))

    def test_the_vector_sets_hold_what_the_c_sharp_tests_require(self) -> None:
        self.assertGreaterEqual(len(self.data["valids"]), 25)
        self.assertGreaterEqual(len(self.data["refused"]), 19)
        self.assertGreaterEqual(len(self.data["edits"]), 8)
        self.assertGreaterEqual(len(self.data["archives"]), 10)
        self.assertGreaterEqual(len(self.data["badArchives"]), 22)
        self.assertGreaterEqual(len(self.data["stages"]), 14)
        self.assertGreaterEqual(len(self.data["badStages"]), 45)
        self.assertGreaterEqual(len(self.data["coordinates"]), 110)
        names = [v["name"] for v in self.data["valids"]]
        self.assertEqual(len(names), len(set(names)))
        for version in range(43, 51):
            self.assertIn(f"authored-v{version}", names)

    def test_every_valid_vector_round_trips_in_the_reference_and_covers_each_world_version(self) -> None:
        versions = set()
        for v in self.data["valids"]:
            with self.subTest(v["name"]):
                model = enc.read_world_model(v["body"])
                self.assertEqual(enc.write_world_body(model), v["body"])
                lines = gen.dump_lines(model)
                self.assertEqual(lines, sorted(lines))
                self.assertEqual((len(lines), gen.dump_hash(lines)), (v["lines"], v["hash"]))
                versions.add(model["version"])
        self.assertEqual(versions, set(range(43, 51)))

    def test_the_vectors_reach_every_branch_of_the_reader(self) -> None:
        models = [enc.read_world_model(v["body"]) for v in self.data["valids"]]
        kinds = {t["oid"] for m in models for t in m["things"]}
        self.assertEqual(kinds, set(gen.READABLE_OIDS))
        self.assertEqual({m["header"]["headerVersion"] for m in models}, {0, 1, 2, 3})
        self.assertEqual({m["influenceMap"]["version"] for m in models}, {0, 1})
        self.assertEqual({g["version"] for m in models for g in m.get("occupancyGrids", [])}, {0, 1, 2})
        dtypes = {s["dataType"] for m in models for sc in m["scripts"] for s in sc["code"]["symbols"]}
        self.assertEqual(dtypes, {0, 1, 2, 3, 4, 5, 6})
        self.assertTrue(any(isinstance(x, dict) for m in models for t in m["things"] for x in t["init"]["position"]))
        self.assertEqual(max(len(m["things"]) for m in models), 1000)

    def test_the_dump_format(self) -> None:
        model = enc.read_world_model(fixtures.world_body())
        model["things"][0]["init"]["position"] = [{"f32bits": "0100c07f"}, -0.0, 10.0]
        model["things"][0]["init"]["name"] = 'a"b\\c\xe9\x00'.replace("\x00", "")
        lines = gen.dump_lines(model)
        self.assertIn("version = 50", lines)
        self.assertIn("things[0].init.position[0] = f32:0100c07f", lines)
        self.assertIn("things[0].init.position[1] = f32:00000080", lines)
        self.assertIn("things[0].init.position[2] = f32:00002041", lines)
        self.assertIn('things[0].init.name = "a\\x22b\\x5cc\\xe9"', lines)
        self.assertIn("things[0].kind = \"unit\"", lines)
        self.assertTrue(any(line.startswith("scripts[0].trailer = bytes(10):") for line in lines))
        self.assertTrue(any(line.startswith("occupancyGrids[0].data = bytes(0):") for line in lines))
        self.assertFalse(any(line.startswith("format") for line in lines))
        self.assertEqual(len(lines), len(set(lines)), "a path appears once")
        self.assertEqual(gen.quote("\x7f\xff Z"), '"\\x7f\\xff Z"')

    def test_every_refused_body_is_refused_and_so_is_every_proper_prefix_of_a_body(self) -> None:
        for v in self.data["refused"]:
            with self.subTest(v["name"]), self.assertRaises((wrd.DecodeError, enc.EncodeError, struct.error)):
                enc.read_world_model(v["body"])
        for name in ("authored-v50", "authored-v43", "kinds-v43", "kinds-v46"):
            body = self.by_name[name]["body"]
            for length in range(len(body)):
                with self.subTest(name=name, length=length), self.assertRaises((wrd.DecodeError, enc.EncodeError, struct.error)):
                    enc.read_world_model(body[:length])

    def test_each_refused_body_is_a_valid_body_with_one_thing_wrong(self) -> None:
        """Putting back the one patched field gives the valid body the reference reads: each refusal is that field's own."""
        base, v43, empty, rich = (self.by_name[n]["body"] for n in ("authored-v50", "authored-v43", "empty-v50", "scripts-rich"))
        refused = {v["name"]: v["body"] for v in self.data["refused"]}
        parsed = wrd.parse_world_body(base, gen.PHYSICS, base=False)
        waypoint, last, first = parsed["things"][2]["offset"], parsed["things"][-1], parsed["things"][0]
        tree_groups_at = last["offset"] + last["length"]
        name_at = first["offset"] + 4 + 6 * 4 + 3 * 4
        config_at = base.index(b"\x07Paladin")
        dtype_at = rich.index(struct.pack("<i", 4) + b"none" + struct.pack("<i", 0)) + 8

        def put(at: int, data: bytes, size: int | None = None):
            return lambda b: b[:at] + data + b[at + (len(data) if size is None else size):]

        undo = {
            "version-42": (v43, put(0, struct.pack("<H", 43))),
            "version-51": (base, put(0, struct.pack("<H", 50))),
            "trailing-byte": (base, lambda b: b[:-1]),
            "config-count-negative": (empty, put(14, struct.pack("<i", 0))),
            "config-count-over-limit": (empty, lambda b: b[:14] + struct.pack("<i", 0) + b[18 + (1 << 20) + 1:]),
            "config-count-huge": (empty, put(14, struct.pack("<i", 0))),
            "unknown-oid": (base, put(waypoint, struct.pack("<i", 18))),
            "wall-oid": (base, put(waypoint, struct.pack("<i", 18))),
            "influence-version-2": (base, put(tree_groups_at + 6, struct.pack("<H", 0))),
            "script-dtype-unknown": (rich, put(dtype_at, struct.pack("<i", 0))),
            "script-dtype-negative": (rich, put(dtype_at, struct.pack("<i", 0))),
            "script-name-negative": (base, put(parsed["scripts"][0]["offset"], struct.pack("<i", 4))),
            "cstring-unterminated": (base, put(name_at, b"main\0", 300)),
            "cstring-256": (base, put(name_at, b"main\0", 257)),
            "lstring-negative": (base, put(config_at, b"\x07Paladin", 1 + 128)),
            "tree-group-count-negative": (base, put(tree_groups_at, struct.pack("<h", 0))),
            "path-count-negative": (empty, put(52, struct.pack("<h", 0))),
        }
        self.assertEqual(set(undo) | {"empty-input", "grid-short"}, set(refused))
        for name, (original, restore) in undo.items():
            with self.subTest(name):
                repaired = restore(refused[name])
                self.assertEqual(repaired, original)
                enc.read_world_model(repaired)

    def test_an_edit_changes_only_the_bytes_of_the_field_it_edits(self) -> None:
        before = self.by_name["authored-v50"]["body"]
        edits = {e["name"]: e for e in self.data["edits"]}
        parsed = wrd.parse_world_body(before, gen.PHYSICS, base=False)
        after = edits["move-v50"]["body"]
        at = parsed["things"][0]["offset"] + 4
        changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
        self.assertEqual(len(before), len(after))
        self.assertTrue(changed and at <= min(changed) and max(changed) < at + 12)
        self.assertEqual(struct.unpack_from("<3f", after, at), (12.5, -40.0, 3.0))
        renamed = edits["rename-v50"]["body"]
        self.assertGreater(len(renamed), len(before))
        self.assertEqual(enc.read_world_model(renamed)["things"][0]["init"]["name"], "A much longer name than the old one")

    def test_the_archives_hold_what_the_reference_finds(self) -> None:
        archives = {a["name"]: a for a in self.data["archives"]}
        both = archives["base-and-real"]["info"]
        self.assertEqual((both["baseLevel"], both["realLevel"]), (100, 200))
        self.assertEqual(set(both["bodies"]), {"BSWD", "RLWD"})
        self.assertEqual(both["bodies"]["RLWD"], hashlib.sha256(self.by_name["authored-v50"]["body"]).hexdigest())
        self.assertEqual(len(enc.read_members(archives["three-members"]["file"])), 3)
        self.assertEqual(set(archives["real-only"]["info"]["bodies"]), {"RLWD"})
        self.assertEqual(archives["wdat-longer"]["info"]["baseLevel"], 7)
        for v in self.data["badArchives"]:
            with self.subTest(v["name"]):
                try:
                    worlds = enc.level_worlds(b"".join(enc.inflate(enc.read_members(v["file"]))))
                except (enc.EncodeError, struct.error):
                    continue
                self.assertNotIn("baseLevel", worlds)  # the one the reference accepts without level numbers

    def test_the_member_vectors_are_refused_for_the_members_own_fault(self) -> None:
        bad = {v["name"]: v["file"] for v in self.data["badArchives"]}
        good = {v["name"]: v["file"] for v in self.data["archives"]}

        def refusal(file: bytes) -> str:
            with self.assertRaises(enc.EncodeError) as caught:
                enc.inflate(enc.read_members(file))
            return str(caught.exception)

        # A complete zlib stream with bytes after it, the last four of them its own Adler-32: "the last four bytes are the
        # checksum of what the member inflates to" holds, and the member is still not one zlib stream.
        for name in ("member-adler-repeated", "member-adler-after-gap", "member-adler-after-junk"):
            with self.subTest(name):
                member = enc.read_members(bad[name])[0]
                decoder = zlib.decompressobj()
                inflated = decoder.decompress(member)
                self.assertTrue(decoder.eof)
                self.assertGreaterEqual(len(decoder.unused_data), 4)
                self.assertEqual(member[-4:], struct.pack(">I", zlib.adler32(inflated)))
                self.assertIn("trailing data after zlib stream", refusal(bad[name]))
        # A stream cut short that ends in the Adler-32 of everything it inflated to: the same check passes, the stream is not complete.
        member = enc.read_members(bad["member-cut-short-before-adler"])[0]
        decoder = zlib.decompressobj()
        inflated = decoder.decompress(member)
        self.assertFalse(decoder.eof)
        self.assertEqual(member[-4:], struct.pack(">I", zlib.adler32(inflated)))
        self.assertIn("truncated zlib stream", refusal(bad["member-cut-short-before-adler"]))
        # The bound on what one member inflates to: exactly the bound is read, one byte more is not.
        self.assertEqual([len(block) for block in enc.inflate(enc.read_members(good["member-exactly-1mib"]))], [enc.MAX_INFLATED_MEMBER_BYTES])
        self.assertEqual(len(zlib.decompress(enc.read_members(bad["member-1mib-plus-one"])[0])), enc.MAX_INFLATED_MEMBER_BYTES + 1)
        self.assertIn("inflated archive/member limit", refusal(bad["member-1mib-plus-one"]))
        self.assertEqual(enc.MAX_INFLATED_MEMBER_BYTES, 1 << 20)
        # The bound on a member's compressed bytes (the game's pack buffer): exactly that many are read, one byte more is not.
        self.assertEqual([len(m) for m in enc.read_members(good["member-exactly-pack-buffer"])], [enc.PACK_BUFFER_SIZE])
        self.assertEqual([len(m) for m in enc.read_members(good["member-one-under-pack-buffer"])], [enc.PACK_BUFFER_SIZE - 1])
        self.assertEqual(struct.unpack_from("<I", bad["member-pack-buffer-plus-one"])[0], enc.PACK_BUFFER_SIZE + 1)
        self.assertIn("implausible .aya member length", refusal(bad["member-pack-buffer-plus-one"]))
        for name in ("member-exactly-pack-buffer", "member-one-under-pack-buffer"):
            self.assertLessEqual(len(zlib.decompress(enc.read_members(good[name])[0])), enc.MAX_INFLATED_MEMBER_BYTES)
        # A zlib stream whose header asks for a preset dictionary: the reference's decompressor cannot read it.
        needy = enc.read_members(bad["member-needs-dictionary"])[0]
        self.assertTrue(needy[1] & 0x20)
        with self.assertRaises(zlib.error):
            zlib.decompressobj().decompress(needy)
        self.assertIn("invalid zlib data", refusal(bad["member-needs-dictionary"]))

    def test_the_coordinate_vectors_are_what_the_move_tool_makes_of_them(self) -> None:
        vectors = {v["text"]: v for v in self.data["coordinates"]}
        self.assertEqual(len(vectors), len(self.data["coordinates"]))

        def nearest_float32(text: str) -> bytes:
            """The float32 nearest the decimal in one step (exact arithmetic, a tie to the even mantissa), as four little-endian bytes."""
            exact = Fraction(Decimal(text))
            bits = struct.unpack("<I", struct.pack("<f", float(exact)))[0]
            candidates = [(abs(Fraction(struct.unpack("<f", struct.pack("<I", b))[0]) - exact), b & 1, b) for b in (bits - 1, bits, bits + 1)
                          if 0 <= b <= 0xFFFFFFFF and (b & 0x7FFFFFFF) < 0x7F800000]
            return struct.pack("<I", min(candidates)[2])

        for text, v in vectors.items():
            with self.subTest(text):
                if not v["ok"]:
                    self.assertEqual((v["hex"], v["rounded"], v["exact"]), ("", False, ""))
                    continue
                stored = struct.unpack("<f", bytes.fromhex(v["hex"]))[0]
                self.assertEqual(v["exact"], format(Decimal(stored), "f"))
                self.assertEqual(v["rounded"], Decimal(stored) != Decimal(text))
        # The acceptance edit's coordinates, and a negative zero kept as one.
        for text in ("276.49", "265.07", "-12.1"):
            self.assertEqual(vectors[text]["hex"], struct.pack("<f", float(text)).hex())
            self.assertTrue(vectors[text]["rounded"])
        self.assertEqual((vectors["-0"]["hex"], vectors["-0"]["rounded"], vectors["-0"]["exact"]), ("00000080", False, "-0"))
        self.assertEqual((vectors["0"]["hex"], vectors["0"]["exact"]), ("00000000", "0"))
        self.assertEqual(vectors["276.49"]["exact"], "276.489990234375")
        # The tool rounds to a double and then to float32: the vectors beside float32 midpoints go where a one-step parser would not.
        beside = [text for text in self.gen_double_rounding() if vectors[text]["ok"]]
        self.assertGreaterEqual(len(beside), 10)
        self.assertGreaterEqual(sum(1 for text in beside if vectors[text]["hex"] != nearest_float32(text).hex()), 5)
        # The page reads a form of text that is narrower than the tool's, never wider.
        outside = [v for v in vectors.values() if v["ok"] and not v["grammar"]]
        self.assertGreaterEqual(len(outside), 10)
        for text in ("1_000", "\u0663", "\uff11\uff12", "\t7", "\u00a07", "7\n", "1e-1000000000000000000"):
            self.assertTrue(vectors[text]["ok"] and not vectors[text]["grammar"], text)
        for v in vectors.values():
            if v["grammar"]:
                self.assertTrue(v["text"].isascii() and "_" not in v["text"], v["text"])
        self.assertTrue(all(vectors[text]["grammar"] for text in ("276.49", "  7  ", "-.5e1", "5.", "1e+0000000000000000000005", "0e999999999999999999")))
        self.assertFalse(vectors["1" * 129]["grammar"] or vectors[" " * 128 + "7"]["grammar"] or vectors["1e1000000000000000000"]["grammar"])
        self.assertTrue(vectors["1" * 128]["grammar"] and vectors[" " * 127 + "7"]["grammar"])

    @staticmethod
    def gen_double_rounding() -> list[str]:
        return gen.double_rounding_texts()

    def test_the_staged_mods_are_what_the_reference_stager_wrote(self) -> None:
        bodies = {v["name"]: v["body"] for v in self.data["valids"]}
        edited = {e["name"]: e["body"] for e in self.data["edits"]}
        for v in self.data["stages"]:
            with self.subTest(v["name"]):
                worlds = gen.spec_worlds(v, bodies, edited)
                files = {gen.stager.world_path(level): body for level, body in worlds.items()}
                self.assertEqual(v["manifest"], gen.stager.build_manifest(v["id"], v["modName"], v["version"], files, author=v["author"],
                                                                         description=v["description"], ce_min=v["ceMin"], ce_max=v["ceMax"]))
                manifest = json.loads(v["manifest"])
                self.assertEqual((manifest["schema"], manifest["id"], manifest["name"], manifest["version"]), (1, v["id"], v["modName"], v["version"]))
                self.assertEqual([f["path"] for f in manifest["files"]], sorted(files))
                self.assertEqual([(f["path"], f["size"], f["sha256"]) for f in manifest["files"]], [tuple(f) for f in v["files"]])
                self.assertEqual("author" in manifest, bool(v["author"]))
                self.assertEqual("description" in manifest, bool(v["description"]))
                self.assertEqual(("ce_min" in manifest, "ce_max" in manifest), (v["ceMin"] is not None, v["ceMax"] is not None))
                self.assertTrue(v["manifest"].endswith(b"\n") and v["manifest"].isascii())
        by_name = {v["name"]: v for v in self.data["stages"]}
        self.assertEqual(json.loads(by_name["quotes-and-backslash"]["manifest"])["name"], 'Say "hi" \\ bye')
        self.assertEqual(len(json.loads(by_name["max-lengths"]["manifest"])["description"]), 1024)
        self.assertEqual(by_name["world-of-4-mib"]["files"][0][1], 4 << 20)
        self.assertEqual([f[0] for f in by_name["worlds-sorted-by-path"]["files"]],
                         ["data/worlds/world007.wrd", "data/worlds/world100.wrd", "data/worlds/world999.wrd"])

    def test_every_refused_staging_is_refused_before_anything_is_written(self) -> None:
        bodies = {v["name"]: v["body"] for v in self.data["valids"]}
        edited = {e["name"]: e["body"] for e in self.data["edits"]}
        for v in self.data["badStages"]:
            with self.subTest(v["name"]), tempfile.TemporaryDirectory() as tmp:
                parent, game = Path(tmp) / "mods", Path(tmp) / "game"
                parent.mkdir()
                game.mkdir()
                with self.assertRaises(gen.stager.ModStageError):
                    gen.stager.stage_mod(parent, game, v["id"], gen.spec_worlds(v, bodies, edited), name=v["modName"], version=v["version"],
                                         author=v["author"], description=v["description"], ce_min=v["ceMin"], ce_max=v["ceMax"])
                self.assertEqual(list(parent.iterdir()), [])

    def test_canonical_does_not_depend_on_the_compressor_and_notices_a_change(self) -> None:
        text = gen.render(self.data)
        first = next(iter(re.finditer(r'"""\n(.*?)\n\s*"""', text, flags=re.S)))
        data = zlib.decompress(base64.b64decode("".join(first.group(1).split())))
        other = base64.b64encode(zlib.compress(data, 1)).decode()
        rows = "\n".join(other[i:i + 100] for i in range(0, len(other), 100))
        recompressed = text[:first.start(1)] + rows + text[first.end(1):]
        self.assertNotEqual(recompressed, text)
        self.assertEqual(gen.canonical(recompressed), gen.canonical(text))
        self.assertNotEqual(gen.canonical(text.replace('"authored-v50"', '"authored-v5O"', 1)), gen.canonical(text))

    def test_check_fails_for_a_stale_file_and_write_then_check_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(gen, "OUTPUT", Path(tmp) / "LevelVectors.g.cs"):
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(gen.main(["--check"]), 1, "a missing file is stale")
                self.assertEqual(gen.main(["--write"]), 0)
                self.assertEqual(gen.main(["--check"]), 0)
                gen.OUTPUT.write_text(gen.OUTPUT.read_text().replace("authored-v50", "authored-v5O", 1))
                self.assertEqual(gen.main(["--check"]), 1)

    def test_the_retail_table_lists_each_world_body_by_hash(self) -> None:
        archives = {a["name"]: a for a in self.data["archives"]}
        with tempfile.TemporaryDirectory() as tmp:
            resources = Path(tmp) / "data" / "resources"
            resources.mkdir(parents=True)
            (resources / "100_res_PC.aya").write_bytes(archives["base-and-real"]["file"])
            (resources / "200_res_PC.aya").write_bytes(archives["real-only"]["file"])
            (resources / "300_res_PC.aya").write_bytes(archives["level-100-terrain"]["file"])  # a terrain the reader accepts
            (resources / "goodie_03_res_PC.aya").write_bytes(b"not a level")
            # Script sources: the real world of 100's archive (and of 200's) is level 200's, 100's base world is level 100's, 300's own world is level 100's.
            (Path(tmp) / "data" / "MissionScripts" / "Level200").mkdir(parents=True)
            (Path(tmp) / "data" / "MissionScripts" / "Level200" / "Main.MSL").write_bytes(MAIN_SOURCE.encode("latin-1"))
            (Path(tmp) / "data" / "MissionScripts" / "level100").mkdir()
            (Path(tmp) / "data" / "MissionScripts" / "level100" / "main.msl").write_bytes(b"c")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(gen.cmd_gate_table(SimpleNamespace(stdout=True, game=Path(tmp))), 0)
            rows = [line.split("\t") for line in out.getvalue().splitlines()]
        self.assertEqual(rows[0], ["level", "tag", "bytes", "sha256", "dumpLines", "dumpSha256"])
        self.assertEqual([(r[0], r[1]) for r in rows[1:]], [("100", "BSWD"), ("100", "RLWD"), ("100", "SCRIPTS"), ("100", "NAMES"), ("100", "PATHS"), ("100", "TERRAIN"),
                                                             ("200", "RLWD"), ("200", "SCRIPTS"), ("200", "NAMES"), ("200", "PATHS"), ("200", "TERRAIN"),
                                                             ("300", "RLWD"), ("300", "SCRIPTS"), ("300", "NAMES"), ("300", "PATHS"), ("300", "TERRAIN")])
        real = self.by_name["authored-v50"]
        self.assertEqual(rows[2][2:], [str(len(real["body"])), hashlib.sha256(real["body"]).hexdigest(), str(real["lines"]), real["hash"]])
        # The terrain rows: an ERES chunk the reader refuses says "refused" (the C# gate must refuse it too), a readable one lists its scale and water bits, samples digest and probe digest.
        self.assertEqual([r[2] for r in (rows[6], rows[11])], ["refused", "refused"])
        terrain = gen.authored_terrain()
        field = gen.heights.read_heightfield(terrain.eres)
        self.assertEqual(rows[16][2:4], [f"{gen.float_bits(field.scale):08x}:{gen.float_bits(field.water):08x}", field.samples_sha256()])
        self.assertEqual(int(rows[16][4]), 33 * 33 + len(gen.enc.read_world_model(real["body"])["things"]))  # the grid, then every thing's position
        # The SCRIPTS rows: the authored body's one script, worked out here by hand (15 instructions, one named handler "Go", five natives called once
        # each in this order, named by the object in row 0), as the own world and as the base world (whose objects are not listed, so no users).
        own = 'own|main|15|event "Go"|SpawnThing:1,PlayCharMessage:1,FollowWaypoint:1,SetObjective:1,GetThingRef:1|0:script'
        base = 'base|main|15|event "Go"|SpawnThing:1,PlayCharMessage:1,FollowWaypoint:1,SetObjective:1,GetThingRef:1|'
        sha = lambda text: hashlib.sha256(text.encode("latin-1")).hexdigest()
        normal = MAIN_SOURCE.replace("\r\n", "\n")
        self.assertEqual(rows[3][2:], ["1:1", gen.dump_hash([own, base]), "2/2", gen.dump_hash([f"own|main|{sha(normal)}", f"base|main|{sha('c')}"])])
        self.assertEqual(rows[8][2:], ["1:0", gen.dump_hash([own]), "1/1", gen.dump_hash([f"own|main|{sha(normal)}"])])
        self.assertEqual(rows[13][2:], ["1:0", gen.dump_hash([own]), "1/1", gen.dump_hash([f"own|main|{sha('c')}"])])
        # The NAMES rows: the nine quoted texts of the authored source (outside the comment, one never closed) resolved by hand against the authored world: the path
        # "Path A" is path 0, the object named "Tank 1" is row 0, "Go" is the event the authored script handles (twice over for archive 100, whose base world has the
        # same script), "unit-2" is the third object of archive 100's base world (exactly, then in another letter case) and of no world of the others, two texts name
        # nothing, "path a" is path 0 in another letter case where it is the argument of FollowWaypointWait (blanks around it do not matter) and nothing as an
        # argument of GetThingRef or of FollowWaypointX. A path argument takes the game's first match: archive 100's base world has the same path "Path A", and the
        # game's one list holds the base world's paths first, so there both path arguments name the base world's path (`basepath:0`).
        self.assertEqual(rows[4][2:], ["10", gen.dump_hash(["main|0|Path A|basepath:0", "main|1|Tank 1|object:0", "main|2|Go|handler:0,handler:1", "main|2|nothing|", "main|3|unterminated|",
                                                            "main|4|unit-2|baseobject:2", "main|4|UNIT-2|baseobject:2:case", "main|5|path a|basepath:0:case", "main|5|path a|", "main|5|path a|"]), "6", "-"])
        self.assertEqual(rows[9][2:], ["10", gen.dump_hash(["main|0|Path A|path:0", "main|1|Tank 1|object:0", "main|2|Go|handler:0", "main|2|nothing|", "main|3|unterminated|",
                                                             "main|4|unit-2|", "main|4|UNIT-2|", "main|5|path a|path:0:case", "main|5|path a|", "main|5|path a|"]), "4", "-"])
        self.assertEqual(rows[14][2:], ["0", gen.dump_hash([]), "0", "-"])
        # The PATHS rows: the authored world's one path "Path A" names slots 1, 2 and 0: a unit, a waypoint and a unit. The loader keeps only the waypoint, row 2.
        kept = ["0|Path A|3|2"]
        for index in (5, 10, 15):
            self.assertEqual(rows[index][2:], ["1", gen.dump_hash(kept), "1", "3"], rows[index][0])
        with self.assertRaises(SystemExit):
            gen.cmd_gate_table(SimpleNamespace(stdout=False, game=Path(".")))

    def test_the_loader_keeps_only_the_slots_that_are_waypoints(self) -> None:
        """kept_path_rows is CWaypointPath::Load's test on each slot: in range, and a thing that is a waypoint."""
        things = [{"kind": kind} for kind in ("unit", "waypoint", "spawner", "waypoint", "start", "waypoint")]
        model = {"things": things, "waypointPaths": [{"name": "A", "slots": [1, 0, 3, 2, 5, 3]}, {"name": "B", "slots": [4, 9, -1, 6, 1]}, {"name": "C", "slots": []}]}
        self.assertEqual([gen.kept_path_rows(model, path) for path in model["waypointPaths"]], [[1, 3, 5, 3], [1], []])
        row = gen.paths_gate_row(7, model).split("\t")
        self.assertEqual(row[:3] + row[4:], ["007", "PATHS", "3", "5", "11"])
        self.assertEqual(row[3], gen.dump_hash(["0|A|6|1,3,5,3", "1|B|5|1", "2|C|0|"]))

    def test_a_follow_waypoint_argument_is_found_by_what_precedes_its_quote(self) -> None:
        line = lambda text: gen.follows_path_call(text, text.index('"'))
        self.assertTrue(line('FollowWaypoint("a", 0);'))
        self.assertTrue(line('\tFollowWaypointWait( \t"a" );'))
        self.assertTrue(line('x = FollowWaypoint   ("a");'))
        self.assertFalse(line('FollowWaypoint(0, "a");'))  # the second argument
        self.assertFalse(line('FollowWaypoint(GetThingRef("a"));'))  # the argument of another call
        self.assertFalse(line('FollowWaypointX("a");'))
        self.assertFalse(line('xFollowWaypoint("a");'))
        self.assertFalse(line('Follow_Waypoint("a");'))
        self.assertFalse(line('followwaypoint("a");'))  # the language is case-sensitive about its functions
        self.assertFalse(line('Print("a");'))
        self.assertFalse(line('"a"'))
        sites = gen.source_literal_sites('A("x"); // "no"\nB( "y" "z")')
        self.assertEqual(sites, [(0, "x", 'A("x"); // "no"', 2), (1, "y", 'B( "y" "z")', 3), (1, "z", 'B( "y" "z")', 7)])

    def test_the_literal_finder_and_the_resolver_follow_the_companions_rules(self) -> None:
        """source_literals and resolve_name are the reference the C# ScriptNames is held to on a game."""
        self.assertEqual(gen.source_literals('a("x"); // "no"\n"y" "z"\nb("q""r") "open\n"'), [(0, "x"), (1, "y"), (1, "z"), (2, "q"), (2, "r"), (2, "open"), (3, "")])
        self.assertEqual(gen.source_literals("// only a comment\n"), [])
        model = {"things": [{"init": {"name": "Tank 1"}}, {"init": {"name": "tank 1"}}, {"init": {"name": "Tank 1"}}, {"init": {"name": ""}}],
                 "waypointPaths": [{"name": "Path A"}, {"name": "Path A"}]}
        scripts = [("alpha", False, ['event "go"']), ("beta", False, ["init"]), ("alpha", True, ['event "go"', 'event "Go"'])]
        resolve = lambda text: gen.resolve_name(text, model, scripts)
        base = {"things": [{"init": {"name": "Tank 1"}}, {"init": {"name": "tank 1"}}, {"init": {"name": "Base Hut"}}, {"init": {"name": ""}}], "waypointPaths": [{"name": "Base Path"}]}
        resolve_with_base = lambda text: gen.resolve_name(text, model, scripts, base)
        self.assertEqual(resolve("Tank 1"), ["object:0", "object:2"])
        self.assertEqual(resolve("TANK 1"), ["object:0:case", "object:1:case", "object:2:case"])
        self.assertEqual(resolve("Path A"), ["path:0", "path:1"])
        self.assertEqual(resolve("alpha"), ["script:0", "script:2"])
        self.assertEqual(resolve("go"), ["handler:0", "handler:2"])
        self.assertEqual(resolve("Go"), ["handler:2"])
        self.assertEqual((resolve(""), resolve("none")), ([], []))
        # The base world's objects come right after the level's own, by the same rule, each world on its own (an exact name in one does not
        # silence the other-case matches of the other); its paths and scripts are not names to follow here.
        self.assertEqual(resolve_with_base("Tank 1"), ["object:0", "object:2", "baseobject:0"])
        self.assertEqual(resolve_with_base("TANK 1"), ["object:0:case", "object:1:case", "object:2:case", "baseobject:0:case", "baseobject:1:case"])
        self.assertEqual(resolve_with_base("Base Hut"), ["baseobject:2"])
        self.assertEqual(resolve_with_base("base hut"), ["baseobject:2:case"])
        self.assertEqual(resolve_with_base("tank 1"), ["object:1", "baseobject:1"])
        self.assertEqual(resolve_with_base("Base Path"), [])
        self.assertEqual((resolve_with_base(""), resolve("Base Hut")), ([], []))
        # A waypoint path's name is matched exactly, except where the game compares ignoring letter case: it takes the first path of its one list (the base
        # world's paths, then the level's own) whose name matches in any case, so one path is named, marked when its case differs.
        paths = {"things": [], "waypointPaths": [{"name": "Route"}, {"name": "route"}, {"name": "ROUTE 2"}]}
        self.assertEqual(gen.resolve_name("route", paths, []), ["path:1"])
        self.assertEqual(gen.resolve_name("route", paths, [], None, True), ["path:0:case"])
        self.assertEqual(gen.resolve_name("ROUTE", paths, [], None, True), ["path:0:case"])
        self.assertEqual(gen.resolve_name("Route", paths, [], None, True), ["path:0"])
        self.assertEqual(gen.resolve_name("Route", paths, []), ["path:0"])
        self.assertEqual(gen.resolve_name("rout", paths, [], None, True), [])
        self.assertEqual(gen.resolve_name("route 2", paths, [], None, True), ["path:2:case"])
        base = {"things": [], "waypointPaths": [{"name": "Shared"}, {"name": "ROUTE"}]}
        self.assertEqual(gen.resolve_name("route", paths, [], base, True), ["basepath:1:case"])  # the base world's path comes first, whatever the case
        self.assertEqual(gen.resolve_name("Route", paths, [], base, True), ["basepath:1:case"])  # even when the level's own path is an exact match
        self.assertEqual(gen.resolve_name("ROUTE", paths, [], base, True), ["basepath:1"])
        self.assertEqual(gen.resolve_name("shared", paths, [], base, True), ["basepath:0:case"])
        self.assertEqual(gen.resolve_name("Route 2", paths, [], base, True), ["path:2:case"])  # nothing of that name in the base world: the level's own
        self.assertEqual(gen.resolve_name("Route", paths, [], base), ["path:0"])  # not a path argument: exact, the level's own paths only
        self.assertEqual(gen.resolve_name("Shared", paths, [], base), [])
        accented = {"things": [], "waypointPaths": [{"name": "à-ROUTE"}]}
        accented_base = {"things": [], "waypointPaths": [{"name": "À-ROUTE"}]}
        self.assertEqual(gen.resolve_name("à-route", accented, [], accented_base, True), ["path:0:case"])
        self.assertEqual(gen.resolve_name("À-route", accented, [], accented_base, True), ["basepath:0:case"])
        accented_base["waypointPaths"][0]["name"] = "Route\0stored suffix"
        self.assertEqual(gen.resolve_name("route", accented, [], accented_base, True), ["basepath:0:case"])
        self.assertEqual(gen.resolve_name("Route\0query suffix", accented, [], accented_base, True), ["basepath:0"])

    def test_the_source_finder_matches_the_companions(self) -> None:
        """tools/level_editor_vectors.py's source_text is the reference the C# ScriptSources is held to on a game: any case, the exact spelling
        first, links and big files ignored, Latin-1 text with \\n line ends."""
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp) / "game"
            folder = game / "data" / "MissionScripts" / "Level007"
            folder.mkdir(parents=True)
            (folder / "Foo.MSL").write_bytes(b"x\r\ny\rz\n")
            (folder / "Accent.msl").write_bytes(b"c\xe9")
            (folder / "Dup.msl").write_bytes(b"lower")
            (folder / "DUP.MSL").write_bytes(b"upper")
            (folder / "Big.msl").write_bytes(bytes((1 << 20) + 1))
            (folder / "Max.msl").write_bytes(bytes(1 << 20))
            (folder / "Link.msl").symlink_to(folder / "Foo.MSL")
            (game / "data" / "MissionScripts" / "level008").symlink_to(folder, target_is_directory=True)
            find = lambda level, name: gen.source_text(game, level, name)
            self.assertEqual(find(7, "Foo"), "x\ny\nz\n")
            self.assertEqual(find(7, "Accent"), "c\u00e9")
            self.assertEqual((find(7, "Dup"), find(7, "DUP")), ("lower", "upper"))
            self.assertEqual((find(7, "Big"), len(find(7, "Max"))), (None, 1 << 20))
            self.assertEqual((find(7, "Link"), find(8, "Foo"), find(9, "Foo"), find(7, "Missing"), find(7, "")), (None, None, None, None, None))
            self.assertIsNone(gen.source_text(Path(tmp) / "empty", 7, "Foo"))


if __name__ == "__main__":
    unittest.main()
