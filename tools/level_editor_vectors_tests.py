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
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import content_catalog_tests as fixtures
import level_editor_vectors as gen
import world_resources_decode as wrd
import world_resources_encode as enc


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
        self.assertGreaterEqual(len(self.data["archives"]), 7)
        self.assertGreaterEqual(len(self.data["badArchives"]), 15)
        self.assertGreaterEqual(len(self.data["stages"]), 14)
        self.assertGreaterEqual(len(self.data["badStages"]), 45)
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
            (resources / "goodie_03_res_PC.aya").write_bytes(b"not a level")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(gen.cmd_gate_table(SimpleNamespace(stdout=True, game=Path(tmp))), 0)
            rows = [line.split("\t") for line in out.getvalue().splitlines()]
        self.assertEqual(rows[0], ["level", "tag", "bytes", "sha256", "dumpLines", "dumpSha256"])
        self.assertEqual([(r[0], r[1]) for r in rows[1:]], [("100", "BSWD"), ("100", "RLWD"), ("200", "RLWD")])
        real = self.by_name["authored-v50"]
        self.assertEqual(rows[2][2:], [str(len(real["body"])), hashlib.sha256(real["body"]).hexdigest(), str(real["lines"]), real["hash"]])
        with self.assertRaises(SystemExit):
            gen.cmd_gate_table(SimpleNamespace(stdout=False, game=Path(".")))


if __name__ == "__main__":
    unittest.main()
