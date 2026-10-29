#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks tools/level888_build.py on an authored game folder (no game bytes), and its retail gate when a game folder is given.

The authored folder has the shape the recipe reads: a donor archive and four source archives of TEXT/MESH descriptors, a physics
file with a unit that is based on another, components, spawners and a unit whose mesh has no file, a worldheaders.dat, and the
loose mesh files that name textures. Every expectation is worked out from that folder, not from the output: the closure from
the physics statements, the added descriptors from which archive holds what, the world from the donor model. The retail gate
(the `gate` command) runs the same checks on the game's own files; here it is exercised when BEA_GAME names a folder, and is a
named SKIP otherwise. The stager side (the loader's rules for the archive and the physics file) is checked in
world_mod_stage_tests.py; the mod this tool writes is also held to that oracle here."""
from __future__ import annotations

import collections
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

import content_catalog_tests as fixtures
import level888_build as lvl
import msl_compile as msl
import world_mod_stage as stage
import world_mod_stage_tests as stager_tests
import world_resources_encode as enc
import worldheaders_decode as headers
from aya_cross_platform_compare import logical_key

TOOLS = Path(__file__).resolve().parent


# ---- authored game folder ----------------------------------------------------------------------------------------------
def s(text: str) -> bytes:
    return text.encode("ascii") + b"\0"


def physics_file(*statements) -> bytes:
    """default physics.dat: the 0x12 header word, statements (kind, size as the real file declares it, name, nodes), then -1."""
    out = bytearray(struct.pack("<H", 0x12))
    for kind, name, nodes in statements:
        body = name.encode("ascii") + b"\0"
        for index, (field, value) in enumerate(nodes):
            body += struct.pack("<II", field, len(value)) + value + struct.pack("<i", -1 if index == len(nodes) - 1 else 0)
        out += struct.pack("<II", kind, len(name) + 1 + sum(8 + len(value) for _, value in nodes)) + body
    return bytes(out + struct.pack("<i", -1))


def physics_statements():
    return [
        (1, "Base Air Unit", [(8, struct.pack("<I", 2))]),
        (1, "Air Fighter", [(39, s("Base Air Unit")), (9, s("FA_F24.msh"))]),
        (1, "Advanced Fighter", [(39, s("Base Air Unit")), (9, s("m_atf.msh"))]),
        (5, "Carrier Spawner", [(1, s("Air Fighter"))]),
        (5, "Fenrir Spawner", [(1, s("Advanced Fighter"))]),
        (7, "Carrier Pad", [(3, s("f_pad.msh"))]),
        (7, "Fenrir Gun", [(3, s("m_fbossgt.msh"))]),
        (7, "Plane Launcher", [(3, s("m_launcher.msh")), (19, s("Fenrir Spawner"))]),
        (1, "Aircarrier Multiplayer", [(9, s("f_ventura.msh")), (27, s("Carrier Pad")), (27, s("Carrier Pad")), (18, s("Carrier Spawner"))]),
        (1, "Fenrir Multiplayer", [(9, s("fenrir-multiplayer.msh")), (27, s("Fenrir Gun")), (27, s("Plane Launcher"))]),
        (1, "Unused Decoy", [(9, s("decoy.msh"))]),
        (8, "Rock", [(3, s("rock.msh"))]),
    ]


def cmsh_stream(name: str, textures: list[str]) -> bytes:
    """A loose mesh file as the game's is framed up to its texture list: CMSH header, CMST bindings, one MSHT/TEXB per texture."""
    head = bytearray(380)
    head[:4] = b"CMSH"
    struct.pack_into("<I", head, 12, len(textures))
    head[44:44 + len(name)] = name.encode("ascii")
    out = bytes(head) + b"CMST" + struct.pack("<I", 36 * len(textures)) + bytes(36 * len(textures))
    for texture in textures:
        out += b"MSHT" + struct.pack("<I", 156) + b"TEXB" + struct.pack("<I", 148) + bytes(20) + texture.encode("ascii").ljust(128, b"\0")
    return out + b"MESP" + bytes(8)


LOOSE = {   # mesh name as the physics file spells it -> the textures its loose file asks for
    "f_ventura.msh": ["meshtex\\f_ventura01.tga", "meshtex\\Chrome3.tga"],
    "f_pad.msh": ["meshtex\\f_ventura01.tga"],
    "FA_F24.msh": ["meshtex\\FA_XF24.tga", "meshtex\\Chrome3.tga"],
    "boss-fenrir.msh": ["meshtex\\BOSSfenrir.tga", "meshtex\\BOSSfenrir-int.tga"],
    "m_fbossgt.msh": ["meshtex\\BOSSfenrir.tga"],
    "m_launcher.msh": ["meshtex\\BOSSfenrir-int.tga"],
    "m_atf.msh": ["meshtex\\M_atf.tga"],
}
DONOR_TEXTS = ["meshtex\\f_ventura01.tga", "meshtex\\Chrome3.tga", "meshtex\\fa_xf24.tga", "particle\\fireball.tga", "particle\\fireball.tga"]
DONOR_MESHES = ["f_ventura.msh", "f_pad.msh", "fa_f24.msh"]
SOURCE_TEXTS = {731: ["meshtex\\BOSSfenrir.tga", "meshtex\\M_atf.tga", "meshtex\\decoy.tga"], 732: ["meshtex\\BOSSfenrir.tga"],
                741: ["meshtex\\BOSSfenrir-int.tga"], 742: ["meshtex\\BOSSfenrir-int.tga"]}
SOURCE_MESHES = {731: ["boss-fenrir.msh", "m_atf.msh", "m_decoy.msh"], 732: ["boss-fenrir.msh"], 741: ["m_launcher.msh"],
                 742: ["m_fbossgt.msh", "m_launcher.msh"]}


def point(oid, kind, x, y, *, definition=None, start=None, script="", allegiance=0):
    thing = {"oid": oid, "kind": kind, "init": {"position": [x, y, 0.0], "orientation": [0.0, 0.0, 0.0], "meshNumber": 0,
                                                "allegiance": allegiance, "target": -1, "script": script, "name": "", "spawnScript": "",
                                                "active": 1, "attachScriptsToUnits": 0}}
    if start is not None:
        thing["init"]["start"] = {"planeMode": 1, "playerNumber": start}
    if definition is not None:
        thing.update(definition=definition, diesOn=-1)
    return thing


def donor_model(payload_size: int, extra_things=(), *, starts=(1, 2), level_scripts=1) -> dict:
    model = enc.read_world_model(fixtures.world_body())
    model["header"] = {"headerVersion": 3, "unused": [payload_size, lvl.DONOR], "battleEngineConfigurations": ["Standard", "Sniper"],
                       "v2Words": [1, 0, 0], "worldType": 2}
    model["baseLevel"] = 10
    things = [point(35, "feature", 10.0, 20.0, definition="Rock"), point(35, "feature", 30.0, 40.0, definition="Rock"),
              point(18, "waypoint", 5.0, 5.0)]
    things += [point(15, "start", 100.0 + n, 50.0, start=n, allegiance=n - 1) for n in starts]
    things += [point(41, "spawn-point", 200.0, 60.0 + n, start=1, allegiance=0) for n in range(2)]
    things += [point(27, "level-script", 1.0, 2.0, script="LevelScript", allegiance=2) for _ in range(level_scripts)]
    model["things"] = things + list(extra_things)
    return model


class Folder:
    """An authored game folder that the recipe can read, built under a temporary directory."""

    def __init__(self, root: Path, *, model_options=None, skip=(), physics=None) -> None:
        self.root = root
        self.records = {857: (["Standard", "Sniper"], [1, 0, 0, 2]), 888: (["Standard", "Laser"], [0, 1, 1, 2])}
        self.payload = {w: 24 + sum(1 + len(c) for c in cfg) for w, (cfg, _) in self.records.items()}
        model = donor_model(self.payload[857], **(model_options or {}))
        self.body = enc.write_world_body(model)
        self.write("data/default physics.dat", physics_file(*(physics or physics_statements())), skip)
        recs = [headers.WorldHeaderRecord(0, 3, self.payload[w], w, cfg, tr) for w, (cfg, tr) in sorted(self.records.items())]
        self.write("data/worldheaders.dat", headers.encode_worldheaders(headers.WorldHeaders(1, len(recs), recs)), skip)
        self.write("data/resources/857_res_PC.aya", self.archive(857, DONOR_TEXTS, DONOR_MESHES, 260, base=10), skip)
        for level in lvl.SOURCES:
            self.write(f"data/resources/{level}_res_PC.aya", self.archive(level, SOURCE_TEXTS[level], SOURCE_MESHES[level], 400 + level), skip)
        for mesh, textures in LOOSE.items():
            self.write(f"data/resources/meshes/m_{mesh}.aya", stager_tests.packed(cmsh_stream(mesh, textures)), skip)

    def write(self, rel: str, data: bytes, skip=()) -> None:
        if rel in skip:
            return
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def archive(self, level, texts, meshes, first_id, *, base=-1) -> bytes:
        children = [(b"WDAT", struct.pack("<ii", base, level))] + ([(b"BSWD", self.body)] if base != -1 else []) + [(b"RLWD", self.body)]
        chunks = stager_tests.level_chunks(level, texts=(), meshes=(), children=children)
        head, tail = chunks[:3], chunks[3:]
        return stager_tests.packed(stager_tests.level_stream(
            head + [(b"TEXT", stager_tests.text_descriptor(t)) for t in texts]
            + [(b"MESH", stager_tests.mesh_descriptor(m, first_id + i)) for i, m in enumerate(meshes)] + tail))


class FolderTest(unittest.TestCase):
    def setUp(self) -> None:
        pins = patch.dict(lvl.PINS, {}, clear=True)   # the authored files are not the game's, so nothing is pinned unless a test says
        pins.start()
        self.addCleanup(pins.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.game = self.root / "game"
        self.folder = Folder(self.game)

    def build(self, **options) -> lvl.Build:
        return lvl.build(lvl.Install(self.game), **options)

    def unpacked(self, result: lvl.Build) -> list[tuple[str, bytes]]:
        raw = b"".join(enc.inflate(enc.read_members(result.files[lvl.ARCHIVE_PATH])))
        return [(tag, raw[at:at + size]) for tag, at, size in enc.chunks(raw)]


# ---- the authored scripts ----------------------------------------------------------------------------------------------
class ScriptTests(unittest.TestCase):
    def test_the_scripts_compile_to_the_handlers_the_level_needs(self) -> None:
        records = {r["name"]: r for r in lvl.compile_scripts(lvl.script_sources())}
        self.assertEqual(["Fenrir", "Venturer", "world888script"], list(records))
        for ship in ("Fenrir", "Venturer"):
            code = records[ship]["code"]
            self.assertEqual({"died"}, {msl.FIXED_EVENTS[i] for i, pc in enumerate(code["eventPCs"]) if pc != -1})
            self.assertEqual([], code["eventFunctions"])
            self.assertIn(f"{ship} Died", {sym["value"] for sym in code["symbols"] if sym["dataType"] == 3})
        world = records["world888script"]["code"]
        self.assertEqual({"init"}, {msl.FIXED_EVENTS[i] for i, pc in enumerate(world["eventPCs"]) if pc != -1})
        self.assertEqual(2, len(world["eventFunctions"]), "one handler for each of the two death events")
        strings = [sym["value"] for sym in world["symbols"] if sym["dataType"] == 3]
        self.assertEqual({"Fenrir Died", "Venturer Died"}, set(strings))
        ints = [sym["value"] for sym in world["symbols"] if sym["dataType"] == 1]
        self.assertEqual([1, lvl.DEFAULT_LIVES, 2, lvl.DEFAULT_LIVES, 1, 2], ints)
        natives = [lvl.wrd.SCRIPT_NATIVES[attr & 0xFF][0] for op, attr in world["instructions"] if msl.OPCODES[op] == "OP_CALL"]
        self.assertEqual(["SetPlayerLives", "SetPlayerLives", "MPDeclarePlayerWon", "MPDeclarePlayerWon"], natives)

    def test_lives_and_the_ai_state_reach_the_source_and_are_range_checked(self) -> None:
        sources = lvl.script_sources(lives=5, ai_state=4)
        self.assertIn("SetPlayerLives(1, 5);", sources["world888script"])
        self.assertIn("SetPlayerLives(2, 5);", sources["world888script"])
        for ship in ("Fenrir", "Venturer"):
            self.assertIn('event("game playing")', sources[ship])
            self.assertIn("SetAIState(4);", sources[ship])
            self.assertNotIn("SetAIState", lvl.script_sources()[ship])
        records = {r["name"]: r for r in lvl.compile_scripts(sources)}
        self.assertEqual(1, len(records["Fenrir"]["code"]["eventFunctions"]))
        for lives in (0, 10, -1, True, 3.0, "3", None):
            with self.subTest(lives=lives), self.assertRaisesRegex(lvl.BuildError, "lives"):
                lvl.script_sources(lives=lives)
        for state in (5, -1, True, 2.0, "4"):
            with self.subTest(ai_state=state), self.assertRaisesRegex(lvl.BuildError, "ai-state"):
                lvl.script_sources(ai_state=state)
        for state in range(5):
            lvl.compile_scripts(lvl.script_sources(ai_state=state))

    def test_the_sources_are_authored_and_hold_no_include(self) -> None:
        for name, text in lvl.script_sources().items():
            with self.subTest(name):
                self.assertNotIn("#include", text)
                self.assertLess(len(text), 600)
                self.assertTrue(text.startswith("// Level 888"), "an authored header comment")
        with self.assertRaises(lvl.BuildError):
            lvl.compile_scripts({"x": "#include \"nothing.h\"\ninit() { }\n"})
        with self.assertRaisesRegex(lvl.BuildError, "does not compile"):
            lvl.compile_scripts({"x": "init() { NoSuchNative(); }\n"})
        self.assertEqual({"Fenrir Died", "Venturer Died", "game playing"}, lvl.authored_strings(lvl.script_sources(ai_state=0)))


# ---- default physics.dat -----------------------------------------------------------------------------------------------------
class PhysicsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = physics_file(*physics_statements())
        self.physics = lvl.Physics(self.data)

    def test_the_statements_and_nodes_are_read_with_their_offsets(self) -> None:
        statements = lvl.parse_physics(self.data)
        self.assertEqual([name for _, name, _ in physics_statements()], [st.name for st in statements])
        fighter = statements[1]
        self.assertEqual([(39, b"Base Air Unit\0"), (9, b"FA_F24.msh\0")], [(n.field, n.value) for n in fighter.nodes])
        self.assertEqual(1, fighter.kind)
        self.assertEqual(len("Air Fighter") + 1 + 8 + 14 + 8 + 11, fighter.size)
        self.assertEqual(struct.pack("<II", 39, 14), self.data[fighter.nodes[0].at:fighter.nodes[0].at + 8])
        self.assertEqual(struct.pack("<II", 1, fighter.size), self.data[fighter.at:fighter.at + 8])

    def test_the_closure_follows_based_on_components_and_spawners(self) -> None:
        units, meshes = self.physics.closure("Aircarrier Multiplayer")
        self.assertEqual(["Aircarrier Multiplayer", "Air Fighter"], units)
        self.assertEqual(["f_ventura.msh", "f_pad.msh", "FA_F24.msh"], meshes, "a component used twice counts once; the fighter's mesh overrides its base")
        units, meshes = self.physics.closure("Fenrir Multiplayer")
        self.assertEqual(["Fenrir Multiplayer", "Advanced Fighter"], units)
        self.assertEqual(["fenrir-multiplayer.msh", "m_fbossgt.msh", "m_launcher.msh", "m_atf.msh"], meshes,
                         "a component's spawner (19) brings the unit it spawns")
        self.assertEqual((["Base Air Unit"], []), self.physics.closure("Base Air Unit"), "a unit with no mesh has none")
        self.assertNotIn("decoy.msh", self.physics.closure("Fenrir Multiplayer")[1], "a unit nobody reaches stays out")

    def test_based_on_applies_where_it_stands_among_the_nodes(self) -> None:
        def mesh_of(*nodes):
            data = physics_file((1, "Base", [(9, s("base.msh"))]), (1, "Mid", [(39, s("Base")), (9, s("mid.msh"))]), (1, "Late", list(nodes)))
            return lvl.Physics(data).values(1, "Late")[0]
        self.assertEqual("base.msh", mesh_of((39, s("Base"))))
        self.assertEqual("mid.msh", mesh_of((39, s("Base")), (39, s("Mid"))), "the later base wins")
        self.assertEqual("own.msh", mesh_of((39, s("Mid")), (9, s("own.msh"))), "an own mesh after the base overrides it")
        self.assertEqual("mid.msh", mesh_of((9, s("own.msh")), (39, s("Mid"))), "a base after the own mesh overrides it")
        self.assertEqual("base.msh", mesh_of((9, s("own.msh")), (39, s("Base"))))

    def test_what_cannot_be_followed_is_refused(self) -> None:
        for label, unit, statements, words in (
                ("an unknown component", "U", [(1, "U", [(27, s("Nothing"))])], "no component named 'Nothing'"),
                ("an unknown spawner", "U", [(1, "U", [(18, s("Nothing"))])], "no spawner named 'Nothing'"),
                ("an unknown base", "U", [(1, "U", [(39, s("Nothing"))])], "no unit named 'Nothing'"),
                ("a cycle", "A", [(1, "A", [(39, s("B"))]), (1, "B", [(39, s("A"))])], "based on itself"),
                ("a spawner that makes an unknown unit", "U", [(5, "S", [(1, s("Nothing"))]), (1, "U", [(18, s("S"))])], "no unit named 'Nothing'"),
                ("a mesh that is not text", "U", [(1, "U", [(9, b"\x01\x02\0")])], "not a printable string"),
                ("a mesh with no NUL", "U", [(1, "U", [(9, b"abc")])], "not a printable string"),
                ("a unit that is not defined", "Z", [(1, "U", [(9, s("a.msh"))])], "no unit named 'Z'")):
            with self.subTest(label), self.assertRaisesRegex(lvl.BuildError, words):
                lvl.Physics(physics_file(*statements)).closure(unit)

    def test_names_are_matched_exactly_as_the_game_matches_them(self) -> None:
        with self.assertRaises(lvl.BuildError):
            self.physics.closure("aircarrier multiplayer")
        data = physics_file((1, "Twin", [(9, s("first.msh"))]), (1, "Twin", [(9, s("second.msh"))]))
        self.assertEqual("first.msh", lvl.Physics(data).values(1, "Twin")[0], "the first definition stands")

    @staticmethod
    def with_link_word(value: int) -> bytes:
        data = bytearray(physics_file((1, "U", [(9, s("a")), (9, s("b"))])))
        first = lvl.parse_physics(bytes(data))[0].nodes[0]
        struct.pack_into("<i", data, first.at + 8 + len(first.value), value)
        return bytes(data)

    def test_framing_that_does_not_end_exactly_is_refused(self) -> None:
        good = self.data
        for label, data, words in (
                ("another header word", struct.pack("<H", 0x13) + good[2:], "framing"),
                ("no terminal marker", good[:-4], "terminal marker|bad node framing|header is cut"),
                ("bytes after the end", good + b"\0", "bytes after"),
                ("a link word of 2", self.with_link_word(2), "link word"),
                ("a name with no NUL", struct.pack("<H", 0x12) + struct.pack("<II", 1, 5) + b"abcde", "not terminated"),
                ("a node past the end", struct.pack("<H", 0x12) + struct.pack("<II", 1, 5) + b"a\0" + struct.pack("<II", 9, 500) + b"x", "past the end"),
                ("empty", b"", "framing")):
            with self.subTest(label), self.assertRaisesRegex(lvl.BuildError, words):
                lvl.parse_physics(data)

    def test_redirecting_a_unit_changes_one_node_and_two_size_words(self) -> None:
        out = lvl.redirect_unit_mesh(self.data, "Fenrir Multiplayer", "fenrir-multiplayer.msh", "boss-fenrir.msh")
        before, after = lvl.parse_physics(self.data), lvl.parse_physics(out)
        delta = len("boss-fenrir.msh") - len("fenrir-multiplayer.msh")
        self.assertEqual(len(self.data) + delta, len(out))
        for a, b in zip(before, after):
            if a.name != "Fenrir Multiplayer":
                self.assertEqual((a.kind, a.name, a.size, [(n.field, n.value) for n in a.nodes]),
                                 (b.kind, b.name, b.size, [(n.field, n.value) for n in b.nodes]))
            else:
                self.assertEqual(a.size + delta, b.size)
                self.assertEqual([(n.field, n.value) for n in a.nodes][1:], [(n.field, n.value) for n in b.nodes][1:])
                self.assertEqual((9, b"boss-fenrir.msh\0"), (b.nodes[0].field, b.nodes[0].value))
                self.assertEqual(len(a.name) + 1 + sum(8 + len(n.value) for n in b.nodes), b.size, "the size word still sums the nodes")
        # byte for byte: the original with the statement's size word, the node's length word and the node's value changed
        statement, node, new = before[9], before[9].nodes[0], b"boss-fenrir.msh\0"
        expected = (self.data[:statement.at + 4] + struct.pack("<I", statement.size + delta) + self.data[statement.at + 8:node.at + 4]
                    + struct.pack("<I", len(new)) + new + self.data[node.at + 8 + len(node.value):])
        self.assertEqual(expected, out)
        self.assertEqual("boss-fenrir.msh", lvl.Physics(out).closure("Fenrir Multiplayer")[1][0])

    def test_redirect_refuses_what_it_does_not_expect(self) -> None:
        for unit, old, words in (("Nothing", "x", "defines no unit"), ("Fenrir Multiplayer", "other.msh", "names the mesh"),
                                 ("Base Air Unit", "x", "exactly one mesh node")):
            with self.subTest(unit=unit), self.assertRaisesRegex(lvl.BuildError, words):
                lvl.redirect_unit_mesh(self.data, unit, old, "boss-fenrir.msh")
        two = physics_file((1, "Two", [(9, s("a.msh")), (9, s("b.msh"))]))
        with self.assertRaisesRegex(lvl.BuildError, "exactly one mesh node"):
            lvl.redirect_unit_mesh(two, "Two", "a.msh", "c.msh")
        # the old name is compared without regard to case, as the game compares mesh names
        lvl.redirect_unit_mesh(self.data, "Fenrir Multiplayer", "FENRIR-MULTIPLAYER.MSH", "boss-fenrir.msh")


# ---- loose meshes ------------------------------------------------------------------------------------------------------------
class MeshTests(unittest.TestCase):
    def test_texture_names_are_read_in_file_order(self) -> None:
        names = ["meshtex\\a.tga", "meshtex\\B.tga", "meshtex\\a.tga"]
        self.assertEqual(names, lvl.texture_names(cmsh_stream("m.msh", names)))
        self.assertEqual([], lvl.texture_names(cmsh_stream("m.msh", [])))
        self.assertEqual(["x" * 127], lvl.texture_names(cmsh_stream("m.msh", ["x" * 127])))

    def test_the_reader_agrees_with_the_toolkits_own_mesh_probe(self) -> None:
        import aya_archive_inventory as inventory
        names = ["meshtex\\a.tga", "meshtex\\B.tga"]
        stream = cmsh_stream("m.msh", names)
        probe = inventory._probe_importer_mesh_body(stream)
        self.assertTrue(probe["plausible"], probe)
        self.assertEqual(names, probe["first_texture_names"])
        self.assertEqual(names, lvl.texture_names(stream))

    def test_a_stream_that_is_not_a_cmsh_texture_list_is_refused(self) -> None:
        good = cmsh_stream("m.msh", ["meshtex\\a.tga", "meshtex\\b.tga"])
        broken = {
            "not CMSH": b"XXXX" + good[4:],
            "no CMST": good[:380] + b"XXXX" + good[384:],
            "a CMST size that disagrees": good[:384] + struct.pack("<I", 35) + good[388:],
            "too many textures": good[:12] + struct.pack("<I", 5000) + good[16:],
            "a count past the data": good[:12] + struct.pack("<I", 9) + good[16:],
            "no MSHT": good[:388 + 72] + b"XXXX" + good[388 + 76:],
            "no TEXB": good[:388 + 72 + 8] + b"XXXX" + good[388 + 72 + 12:],
            "a TEXB size that disagrees": good[:388 + 72 + 12] + struct.pack("<I", 100) + good[388 + 72 + 16:],
            "a cut name": good[:388 + 72 + 100],
            "an empty name": good[:388 + 72 + 36] + bytes(128) + good[388 + 72 + 36 + 128:],
            "a name that is not ASCII": good[:388 + 72 + 36] + b"\xe9" + good[388 + 72 + 37:],
            "too short": good[:100],
        }
        for label, stream in broken.items():
            with self.subTest(label), self.assertRaises(lvl.BuildError):
                lvl.texture_names(stream)


# ---- descriptors ------------------------------------------------------------------------------------------------------------
def framed_mesh(name: str, size: int) -> bytes:
    """A MESH payload of exactly `size` bytes with right PMSH and PMS2 framing (the larger embedded meshes look like this)."""
    return b"PMSH" + struct.pack("<I", size - 8) + b"PMS2" + struct.pack("<I", size - 16) + name.encode("ascii").ljust(size - 16, b"\0")


def chunks_of(texts, meshes, first_id):
    return ([("LVLR", struct.pack("<I", 103)), ("TARG", struct.pack("<I", 1)), ("AYAD", bytes(24))]
            + [("TEXT", stager_tests.text_descriptor(t)) for t in texts] + [("MESH", stager_tests.mesh_descriptor(m, first_id + i)) for i, m in enumerate(meshes)]
            + [("IMPS", b"i"), ("WRES", b"w")])


class MergeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.donor = chunks_of(["a.tga", "b.tga", "b.tga"], ["a.msh", "b.msh"], 10)
        self.sources = {731: chunks_of(["c.tga", "d.tga"], ["c.msh", "d.msh", "e.msh"], 100),
                        732: chunks_of(["c.tga", "e.tga"], ["c.msh", "f.msh"], 200),
                        741: chunks_of([], [], 0), 742: chunks_of(["z.tga"], ["z.msh"], 300)}

    def test_descriptors_missing_from_the_donor_come_from_the_first_source_that_holds_them(self) -> None:
        merged, log = lvl.merge_descriptors(self.donor, self.sources, ["B.msh", "e.msh", "d.msh", "c.msh", "f.msh", "z.msh"],
                                            ["A.tga", "e.tga", "c.TGA", "z.tga"])
        self.assertEqual([("c.msh", 731, 12), ("d.msh", 731, 13), ("e.msh", 731, 14), ("f.msh", 732, 15), ("z.msh", 742, 16)],
                         [(m["name"], m["from"], m["id"]) for m in log["mesh"]], "name order, ids after the donor's highest (11)")
        self.assertEqual([("c.tga", 731), ("e.tga", 732), ("z.tga", 742)], [(t["name"], t["from"]) for t in log["text"]])
        tags = [tag for tag, _ in merged]
        # added descriptors sit behind the donor's last TEXT and last MESH chunk, before IMPS and WRES
        self.assertEqual(["LVLR", "TARG", "AYAD"] + ["TEXT"] * 6 + ["MESH"] * 7 + ["IMPS", "WRES"], tags)
        added = [logical_key("MESH", p)[0] for t, p in merged if t == "MESH"]
        self.assertEqual(["a.msh", "b.msh", "c.msh", "d.msh", "e.msh", "f.msh", "z.msh"], added)
        ids = [struct.unpack_from("<i", p, 316)[0] for t, p in merged if t == "MESH"]
        self.assertEqual([10, 11, 12, 13, 14, 15, 16], ids)
        added = [payload for _, payload in merged if (_, payload) not in self.donor]
        self.assertEqual(8, len(added))
        self.assertEqual(self.donor, [chunk for chunk in merged if chunk[1] not in added], "the donor's chunks are kept, in order")
        # the copied MESH payload differs from its source only in the runtime id
        source_payload = dict((logical_key("MESH", p)[0], p) for t, p in self.sources[732] if t == "MESH")["f.msh"]
        copied = dict((logical_key("MESH", p)[0], p) for t, p in merged if t == "MESH")["f.msh"]
        self.assertEqual(source_payload[:316] + source_payload[320:], copied[:316] + copied[320:])

    def test_nothing_missing_changes_nothing(self) -> None:
        merged, log = lvl.merge_descriptors(self.donor, self.sources, ["a.msh", "B.MSH"], ["a.tga", "B.tga"])
        self.assertEqual(self.donor, merged)
        self.assertEqual({"mesh": [], "text": []}, log)

    def test_a_descriptor_no_source_holds_is_refused(self) -> None:
        with self.assertRaisesRegex(lvl.BuildError, "holds the MESH descriptor 'nowhere.msh'"):
            lvl.merge_descriptors(self.donor, self.sources, ["nowhere.msh"], [])
        with self.assertRaisesRegex(lvl.BuildError, "holds the TEXT descriptor 'nowhere.tga'"):
            lvl.merge_descriptors(self.donor, self.sources, [], ["nowhere.tga"])

    def test_descriptors_of_another_size_are_refused(self) -> None:
        sources = dict(self.sources)
        sources[731] = self.sources[731][:3] + [("MESH", framed_mesh("x.msh", 326))] + self.sources[731][3:]
        with self.assertRaisesRegex(lvl.BuildError, "MESH x.msh in archive 731 is 326 bytes, not the 325 of a descriptor"):
            lvl.merge_descriptors(self.donor, sources, ["x.msh"], [])
        text = stager_tests.text_descriptor("x.tga")
        odd_text = [("TEXT", b"DXTX" + struct.pack("<I", 373 - 8) + text[8:] + b"\0")]
        sources[731] = self.sources[731][:3] + odd_text + self.sources[731][3:]
        with self.assertRaisesRegex(lvl.BuildError, "TEXT x.tga in archive 731 is 373 bytes, not the 372 of a descriptor"):
            lvl.merge_descriptors(self.donor, sources, [], ["x.tga"])

    def test_a_donor_that_cannot_take_new_runtime_ids_is_refused(self) -> None:
        twice = chunks_of(["a.tga"], ["a.msh", "b.msh"], 10)
        twice[-3] = ("MESH", stager_tests.mesh_descriptor("b.msh", 10))
        with self.assertRaisesRegex(lvl.BuildError, "distinct runtime ids"):
            lvl.merge_descriptors(twice, self.sources, ["c.msh"], [])
        short = [c for c in self.donor if c[0] != "MESH"]
        with self.assertRaisesRegex(lvl.BuildError, "no TEXT or no MESH"):
            lvl.merge_descriptors(short, self.sources, [], [])
        embedded = self.donor[:5] + [("MESH", framed_mesh("x.msh", 959))] + self.donor[5:]
        with self.assertRaisesRegex(lvl.BuildError, "325-byte"):
            lvl.merge_descriptors(embedded, self.sources, [], [])

    def test_a_descriptor_that_is_not_one_is_refused(self) -> None:
        bad = self.donor[:3] + [("TEXT", b"not a descriptor")] + self.donor[3:]
        with self.assertRaisesRegex(lvl.BuildError, "not a descriptor this recipe reads"):
            lvl.merge_descriptors(bad, self.sources, [], [])


# ---- the world --------------------------------------------------------------------------------------------------------------
class WorldTests(unittest.TestCase):
    def records(self):
        cfg_donor, tr_donor = ["Standard", "Sniper"], [1, 0, 0, 2]
        cfg_new, tr_new = ["Standard", "Laser"], [0, 1, 1, 2]
        mk = lambda wid, cfg, tr: headers.WorldHeaderRecord(0, 3, 24 + sum(1 + len(c) for c in cfg), wid, cfg, tr)
        return mk(888, cfg_new, tr_new), mk(857, cfg_donor, tr_donor)

    def donor(self, **options):
        record, donor = self.records()
        return enc.write_world_body(donor_model(donor.payload_size, **options)), record, donor

    def test_the_world_keeps_features_and_starts_and_adds_the_ships_and_the_level_script(self) -> None:
        body, record, donor = self.donor()
        scripts = lvl.compile_scripts(lvl.script_sources())
        out, model = lvl.build_world(body, record, donor, scripts)
        self.assertEqual(json.dumps(model, sort_keys=True), json.dumps(enc.read_world_model(out), sort_keys=True))
        kinds = collections.Counter(t["kind"] for t in model["things"])
        self.assertEqual({"feature": 2, "start": 2, "spawn-point": 2, "level-script": 1, "unit": 2}, dict(kinds))
        self.assertEqual(-1, model["baseLevel"])
        self.assertEqual([], model["waypointPaths"])
        self.assertEqual(["Fenrir", "Venturer", "world888script"], [sc["name"] for sc in model["scripts"]])
        header = model["header"]
        self.assertEqual({"headerVersion": 3, "unused": [record.payload_size, 888], "battleEngineConfigurations": ["Standard", "Laser"],
                          "v2Words": [0, 1, 1], "worldType": 2}, header)
        level_script = [t for t in model["things"] if t["kind"] == "level-script"][0]
        self.assertEqual(("world888script", ""), (level_script["init"]["script"], level_script["init"]["name"]))
        ships = {t["init"]["name"]: t for t in model["things"] if t["kind"] == "unit"}
        self.assertEqual({"Venturer", "Fenrir"}, set(ships))
        self.assertEqual((lvl.VENTURER, "Venturer", 0), (ships["Venturer"]["definition"], ships["Venturer"]["init"]["script"], ships["Venturer"]["init"]["allegiance"]))
        self.assertEqual((lvl.FENRIR, "Fenrir", 1), (ships["Fenrir"]["definition"], ships["Fenrir"]["init"]["script"], ships["Fenrir"]["init"]["allegiance"]))
        self.assertEqual([float(c) for c in lvl.VENTURER_PLACEMENT["position"]], ships["Venturer"]["init"]["position"])
        self.assertEqual(lvl.f32(3.14159265), ships["Venturer"]["init"]["orientation"][0])
        self.assertEqual([1, 2], sorted(t["init"]["start"]["playerNumber"] for t in model["things"] if t["kind"] == "start"))

    def test_the_donor_is_not_changed_and_the_result_is_deterministic(self) -> None:
        body, record, donor = self.donor()
        scripts = lvl.compile_scripts(lvl.script_sources())
        first, _ = lvl.build_world(body, record, donor, scripts)
        second, _ = lvl.build_world(body, record, donor, scripts)
        self.assertEqual(first, second)
        self.assertEqual(body, self.donor()[0])

    def test_donors_that_do_not_match_the_recipe_are_refused(self) -> None:
        record, donor_record = self.records()
        scripts = lvl.compile_scripts(lvl.script_sources())
        for label, options, words in (("a second level script", {"level_scripts": 2}, "exactly one level script"),
                                      ("no level script", {"level_scripts": 0}, "exactly one level script"),
                                      ("three start points", {"starts": (1, 2, 3)}, "players 1 and 2"),
                                      ("only one start point", {"starts": (1,)}, "players 1 and 2"),
                                      ("two starts of player 1", {"starts": (1, 1)}, "players 1 and 2")):
            with self.subTest(label), self.assertRaisesRegex(lvl.BuildError, words):
                body, _, _ = self.donor(**options)
                lvl.build_world(body, record, donor_record, scripts)
        body, _, _ = self.donor()
        for label, change in (("configs", lambda r: setattr(r, "configs", ["Other"])), ("trailing", lambda r: setattr(r, "trailing", [9, 9, 9, 9])),
                              ("the skipped words", lambda r: setattr(r, "payload_size", r.payload_size + 1))):
            with self.subTest(label):
                wrong = self.records()[1]
                change(wrong)
                with self.assertRaisesRegex(lvl.BuildError, "disagrees with its worldheaders.dat record"):
                    lvl.build_world(body, record, wrong, scripts)
        short = self.records()[0]
        short.trailing = [0, 1, 1]
        with self.assertRaisesRegex(lvl.BuildError, "four trailing words"):
            lvl.header_from_record(short)

    def test_an_archive_is_the_donors_chunks_with_one_world_of_level_888(self) -> None:
        chunks = chunks_of(["a.tga"], ["a.msh"], 1)
        body = b"\x32\x00" + bytes(10)
        raw = lvl.assemble(chunks, body)
        worlds = enc.level_worlds(raw)
        self.assertEqual((-1, 888, ["RLWD"], body), (worlds["baseLevel"], worlds["realLevel"], sorted(worlds["bodies"]), worlds["bodies"]["RLWD"]))
        self.assertEqual([tag for tag, _ in chunks], [tag for tag, _, _ in enc.chunks(raw)])
        self.assertEqual(lvl.chunk_bytes("LVLR", chunks[0][1]), raw[:12])
        # packing: 1 MiB blocks that the loader's reader takes back to the same bytes
        big = b"".join(os.urandom(100) * 10000 for _ in range(3))
        problem, back = stage.check_packed(lvl.pack(big), unpack=True)
        self.assertEqual((None, big), (problem, back))
        self.assertEqual(3, len(enc.read_members(lvl.pack(big))))
        self.assertEqual(lvl.pack(big), lvl.pack(big))


# ---- the build --------------------------------------------------------------------------------------------------------------
class BuildTests(FolderTest):
    def test_the_build_makes_the_archive_and_the_physics_file_the_recipe_describes(self) -> None:
        result = self.build()
        self.assertEqual({lvl.ARCHIVE_PATH, lvl.PHYSICS_PATH}, set(result.files))
        report = result.report
        self.assertEqual(["Aircarrier Multiplayer", "Air Fighter", "Fenrir Multiplayer", "Advanced Fighter"], report["closure"]["units"])
        self.assertEqual(["f_ventura.msh", "f_pad.msh", "FA_F24.msh", "boss-fenrir.msh", "m_fbossgt.msh", "m_launcher.msh", "m_atf.msh"],
                         report["closure"]["meshes"])
        self.assertEqual(["meshtex\\f_ventura01.tga", "meshtex\\Chrome3.tga", "meshtex\\FA_XF24.tga", "meshtex\\BOSSfenrir.tga",
                          "meshtex\\BOSSfenrir-int.tga", "meshtex\\M_atf.tga"], report["closure"]["textures"])
        self.assertEqual([("boss-fenrir.msh", 731, 263), ("m_atf.msh", 731, 264), ("m_fbossgt.msh", 742, 265), ("m_launcher.msh", 741, 266)],
                         [(m["name"], m["from"], m["id"]) for m in report["added"]["mesh"]], "ids follow the donor's highest (262), names in order")
        self.assertEqual([("meshtex\\BOSSfenrir-int.tga", 741), ("meshtex\\BOSSfenrir.tga", 731), ("meshtex\\M_atf.tga", 731)],
                         [(t["name"], t["from"]) for t in report["added"]["text"]])
        chunks = self.unpacked(result)
        self.assertEqual(["LVLR", "TARG", "AYAD"] + ["TEXT"] * (5 + 3) + ["MESH"] * (3 + 4) + ["IMPS", "LNDS", "SURF", "ERES", "SSHD", "WRES"],
                         [tag for tag, _ in chunks])
        self.assertEqual(report["archive"]["chunks"], len(chunks))
        kept = collections.Counter(c for c in lvl.unpack(lvl.Install(self.game), lvl.DONOR) if c[0] != "WRES")
        self.assertEqual(collections.Counter(), kept - collections.Counter(chunks))
        # the physics file is the original with one node changed
        original = (self.game / "data/default physics.dat").read_bytes()
        self.assertEqual(original.replace(b"fenrir-multiplayer.msh", b"boss-fenrir.msh").count(b"boss-fenrir.msh"), 1)
        self.assertEqual(len(original) - len("fenrir-multiplayer.msh") + len("boss-fenrir.msh"), len(result.files[lvl.PHYSICS_PATH]))
        self.assertEqual("boss-fenrir.msh", lvl.Physics(result.files[lvl.PHYSICS_PATH]).values(1, "Fenrir Multiplayer")[0])
        # the loader's own rules, through the oracle: stage it as a mod and ask
        out = self.root / "mods"
        lvl.stage_build(result, self.game, out, ce_min="0.1.13")
        self.assertEqual([], stager_tests.LoaderRules.problems(out / lvl.MOD_ID, self.game))

    def test_the_build_is_deterministic_and_reads_the_folder_only(self) -> None:
        before = {p: p.read_bytes() for p in self.game.rglob("*") if p.is_file()}
        stamps = {p: p.stat().st_mtime_ns for p in before}
        first, second = self.build(), self.build()
        self.assertEqual(first.files, second.files)
        self.assertEqual(first.report, second.report)
        self.assertEqual(before, {p: p.read_bytes() for p in self.game.rglob("*") if p.is_file()})
        self.assertEqual(stamps, {p: p.stat().st_mtime_ns for p in before})
        report = first.report
        self.assertEqual({"data/default physics.dat", "data/worldheaders.dat", *(f"data/resources/{n:03d}_res_PC.aya" for n in (857, *lvl.SOURCES)),
                          *(f"data/resources/meshes/m_{m}.aya" for m in report["closure"]["meshes"])}, set(report["inputs"]))
        for rel, info in report["inputs"].items():
            self.assertEqual(lvl.sha256((self.game / rel).read_bytes()), info["sha256"])

    def test_lives_and_the_ai_state_change_only_the_scripts(self) -> None:
        plain = self.build()
        other = self.build(lives=5, ai_state=4)
        self.assertEqual(plain.files[lvl.PHYSICS_PATH], other.files[lvl.PHYSICS_PATH])
        self.assertNotEqual(plain.files[lvl.ARCHIVE_PATH], other.files[lvl.ARCHIVE_PATH])
        a, b = self.unpacked(plain), self.unpacked(other)
        self.assertEqual([c for c in a if c[0] != "WRES"], [c for c in b if c[0] != "WRES"])
        self.assertEqual((5, 4), (other.report["lives"], other.report["aiState"]))
        model = enc.read_world_model(enc.level_worlds(b"".join(lvl.chunk_bytes(t, p) for t, p in b))["bodies"]["RLWD"])
        self.assertEqual(1, len([s for s in model["scripts"] if s["name"] == "Fenrir"][0]["code"]["eventFunctions"]))

    def test_a_game_that_already_has_the_archive_is_refused(self) -> None:
        (self.game / "data/resources/888_res_PC.aya").write_bytes(b"x")
        with self.assertRaisesRegex(lvl.BuildError, "already has data/resources/888_res_PC.aya"):
            self.build()

    def test_a_game_the_recipe_cannot_be_applied_to_is_refused(self) -> None:
        cases = (("no physics file", "data/default physics.dat", "no such file"), ("no donor", "data/resources/857_res_PC.aya", "no such file"),
                 ("a source missing", "data/resources/742_res_PC.aya", "no such file"), ("no worldheaders", "data/worldheaders.dat", "no such file"),
                 ("a loose mesh missing", "data/resources/meshes/m_m_atf.msh.aya", "no mesh file for 'm_atf.msh'"))
        for label, rel, words in cases:
            with self.subTest(label):
                root = self.root / label.replace(" ", "-")
                Folder(root, skip=(rel,))
                with self.assertRaisesRegex(lvl.BuildError, words):
                    lvl.build(lvl.Install(root))

    def test_a_worldheaders_file_without_a_record_for_a_level_is_refused(self) -> None:
        for kept, level in ((857, 888), (888, 857)):
            with self.subTest(missing=level):
                cfg, trailing = self.folder.records[kept]
                records = [headers.WorldHeaderRecord(0, 3, self.folder.payload[kept], kept, cfg, trailing)]
                (self.game / "data/worldheaders.dat").write_bytes(headers.encode_worldheaders(headers.WorldHeaders(1, 1, records)))
                with self.assertRaisesRegex(lvl.BuildError, f"no record for level {level}"):
                    self.build()

    def test_a_physics_file_in_which_the_fenrir_already_has_a_file_is_refused(self) -> None:
        root = self.root / "named"
        statements = [(kind, name, [(f, s("another-name.msh")) if (name, f) == ("Fenrir Multiplayer", 9) else (f, v) for f, v in nodes])
                      for kind, name, nodes in physics_statements()]
        Folder(root, physics=statements)
        with self.assertRaisesRegex(lvl.BuildError, "names the mesh 'another-name.msh', not 'fenrir-multiplayer.msh'"):
            lvl.build(lvl.Install(root))

    def test_a_texture_no_archive_holds_is_refused(self) -> None:
        root = self.root / "notexture"
        Folder(root)
        (root / "data/resources/meshes/m_m_atf.msh.aya").write_bytes(
            stager_tests.packed(cmsh_stream("m_atf.msh", ["meshtex\\Nowhere.tga"])))
        with self.assertRaises(lvl.BuildError) as caught:
            lvl.build(lvl.Install(root))
        self.assertIn("holds the TEXT descriptor", str(caught.exception))
        self.assertIn("nowhere.tga", str(caught.exception))

    def test_pins_warn_by_default_and_refuse_when_strict(self) -> None:
        clean = self.build()
        self.assertEqual([], clean.warnings, "the authored files are not pinned, so nothing warns")
        pins = {rel.lower(): lvl.sha256((self.game / rel).read_bytes()) for rel in clean.report["inputs"] if "/meshes/" not in rel}
        with patch.dict(lvl.PINS, pins, clear=True):
            self.assertEqual([], self.build().warnings, "files that match their pins do not warn")
            wrong = dict(pins)
            wrong["data/default physics.dat"] = "0" * 64
            wrong["data/resources/857_res_pc.aya"] = "f" * 64
            with patch.dict(lvl.PINS, wrong, clear=True):
                warned = self.build()
                self.assertEqual(2, len(warned.warnings))
                self.assertTrue(any("default physics.dat" in w and "000000000000" in w for w in warned.warnings))
                self.assertEqual(warned.warnings, warned.report["warnings"])
                self.assertEqual(clean.files, warned.files, "a warning does not change what is built")
                with self.assertRaisesRegex(lvl.BuildError, "--strict-pins"):
                    lvl.build(lvl.Install(self.game, strict_pins=True))

    def test_the_install_reader_finds_without_case_and_reads_bounded_and_unlinked(self) -> None:
        install = lvl.Install(self.game)
        self.assertEqual(self.game / "data/default physics.dat", install.find("DATA/Default PHYSICS.dat"))
        self.assertIsNone(install.find("data/nothing"))
        self.assertFalse(install.has("data"))
        self.assertTrue(install.has("data/worldheaders.dat"))
        with self.assertRaisesRegex(lvl.BuildError, "larger than 10 bytes"):
            install.read("data/worldheaders.dat", 10)
        (self.game / "data/link.dat").symlink_to(self.game / "data/worldheaders.dat")
        with self.assertRaisesRegex(lvl.BuildError, "cannot be opened"):
            install.read("data/link.dat", 1 << 20)
        (self.game / "data/folder.dat").mkdir()
        with self.assertRaises(lvl.BuildError):
            install.read("data/folder.dat", 1 << 20)


class RecipeConstantsTests(unittest.TestCase):
    def test_the_pinned_files_are_the_ones_named_in_the_recipe(self) -> None:
        self.assertEqual({"data/resources/857_res_pc.aya", *(f"data/resources/{n}_res_pc.aya" for n in lvl.SOURCES), "data/default physics.dat",
                          "data/worldheaders.dat"}, set(lvl.PINS))
        for rel, digest in lvl.PINS.items():
            self.assertEqual(rel, rel.lower())
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(7, len(set(lvl.PINS.values())))

    def test_the_placements_and_names_are_the_ones_the_level_was_played_with(self) -> None:
        self.assertEqual((888, 857, (731, 732, 741, 742)), (lvl.LEVEL, lvl.DONOR, lvl.SOURCES))
        self.assertEqual(("Aircarrier Multiplayer", "Fenrir Multiplayer"), (lvl.VENTURER, lvl.FENRIR))
        self.assertEqual(("fenrir-multiplayer.msh", "boss-fenrir.msh"), (lvl.FENRIR_FILELESS_MESH, lvl.FENRIR_MESH))
        self.assertEqual(("data/resources/888_res_PC.aya", "data/default physics.dat"), (lvl.ARCHIVE_PATH, lvl.PHYSICS_PATH))
        self.assertEqual(3, lvl.DEFAULT_LIVES)
        self.assertEqual((0, 1), (lvl.VENTURER_PLACEMENT["allegiance"], lvl.FENRIR_PLACEMENT["allegiance"]), "the ships are on opposite sides")


# ---- the gate --------------------------------------------------------------------------------------------------------------
class GateTests(FolderTest):
    def gate(self, **options):
        return lvl.run_gate(self.game, **options)

    def failed(self, results) -> list[str]:
        return [name for name, ok, _ in results if not ok]

    def test_every_check_passes_on_the_authored_folder(self) -> None:
        results = self.gate()
        self.assertEqual([], self.failed(results), results)
        self.assertGreaterEqual(len(results), 20)
        self.assertEqual(len(results), len({name for name, _, _ in results}), "each check has its own name")

    def test_each_kind_of_fault_is_found(self) -> None:
        real_merge, real_pack, real_redirect, real_build = lvl.merge_descriptors, lvl.pack, lvl.redirect_unit_mesh, lvl.build

        def drop_added_textures(donor, sources, meshes, textures):
            return real_merge(donor, sources, meshes, [])

        def second_level_differs(raw):
            second_level_differs.calls += 1
            if second_level_differs.calls % 2:
                return real_pack(raw)
            blocks = (zlib.compress(raw[i:i + (1 << 20)], 1) for i in range(0, len(raw), 1 << 20))
            return b"".join(struct.pack("<I", len(block)) + block for block in blocks)
        second_level_differs.calls = 0

        def also_edits_another_unit(data, unit, old, new):
            out = real_redirect(data, unit, old, new)
            return real_redirect(out, "Unused Decoy", "decoy.msh", "other.msh")

        def touches_the_folder(install, **options):
            result = real_build(install, **options)
            touches_the_folder.calls += 1
            if touches_the_folder.calls == 2:   # after the second build, so the first build's record is out of date
                with open(self.game / "data/default physics.dat", "ab") as handle:
                    handle.write(b"\0")
            return result
        touches_the_folder.calls = 0

        for label, target, replacement, expect in (
                ("a texture the meshes ask for is not carried", "merge_descriptors", drop_added_textures, "every texture those meshes ask for has a descriptor"),
                ("two builds differ", "pack", second_level_differs, "deterministic"),
                ("a second unit definition is changed", "redirect_unit_mesh", also_edits_another_unit, "differs from the original in exactly one unit definition"),
                ("the folder changes during the run", "build", touches_the_folder, "files were not changed during the run")):
            with self.subTest(label):
                shutil.rmtree(self.game)
                self.folder = Folder(self.game)
                with patch.object(lvl, target, replacement):
                    failed = self.failed(self.gate())
                self.assertTrue(any(expect in name for name in failed), (label, failed))

    def test_a_pin_that_does_not_match_fails_the_gate_but_only_that_check(self) -> None:
        with patch.dict(lvl.PINS, {"data/default physics.dat": "0" * 64}, clear=True):
            failed = self.failed(self.gate())
            self.assertEqual(["every pinned file is the one the recipe was checked against"], failed)
            results = self.gate(strict_pins=True)
            self.assertEqual(["build"], self.failed(results))

    def test_a_build_the_checks_cannot_read_is_failed_checks_not_a_crash(self) -> None:
        real_build = lvl.build

        def garbage(install, **options):
            result = real_build(install, **options)
            result.files[lvl.ARCHIVE_PATH] = b"garbage"
            return result
        with patch.object(lvl, "build", garbage):
            results = self.gate()
        failed = self.failed(results)
        for expected in ("packed like the game's reader needs", "passes the loader's structure walk", "the checks ran to the end"):
            self.assertIn(expected, failed)
        self.assertEqual("build", results[0][0])
        self.assertTrue(results[0][1])

    def test_a_build_that_cannot_be_made_is_one_failed_check(self) -> None:
        (self.game / "data/resources/888_res_PC.aya").write_bytes(b"x")
        results = self.gate()
        self.assertEqual([("build", False)], [(name, ok) for name, ok, _ in results])
        self.assertIn("already has", results[0][2])


# ---- the command line -------------------------------------------------------------------------------------------------------
class CommandLineTests(FolderTest):
    def run_tool(self, *args: str):
        return subprocess.run([sys.executable, "-I", "-B", str(TOOLS / "level888_build.py"), *args], capture_output=True, timeout=120,
                              env={k: v for k, v in os.environ.items() if k != "BEA_GAME"})

    def test_build_writes_a_mod_the_loader_admits(self) -> None:
        out = self.root / "mods"
        result = self.run_tool("build", "--game", str(self.game), "--out", str(out), "--ce-min", "0.1.13")
        self.assertEqual(0, result.returncode, result.stderr)
        text = result.stdout.decode()
        self.assertIn("staged CE mod 'flagship-duel'", text)
        self.assertIn("mods=flagship-duel", text)
        for words in ("replaces data/default physics.dat", "refuses mods on Windows", "replays", "network sessions"):
            self.assertIn(words, text.replace("The mod replaces", "replaces"))
        mod = out / "flagship-duel"
        self.assertEqual(["data", "mod.json"], sorted(p.name for p in mod.iterdir()))
        manifest = json.loads((mod / "mod.json").read_text())
        self.assertEqual(["data/default physics.dat", "data/resources/888_res_PC.aya"], [f["path"] for f in manifest["files"]])
        self.assertEqual("0.1.13", manifest["ce_min"])
        self.assertIn("REPLACES data/default physics.dat", manifest["description"])
        self.assertIn("conflicts with any other mod", manifest["description"])
        self.assertIn(f"Each player has {lvl.DEFAULT_LIVES} lives", manifest["description"])
        self.assertLessEqual(len(manifest["description"]), 1024)
        self.assertEqual([], stager_tests.LoaderRules.problems(mod, self.game))
        # the files are what an in-process build makes
        direct = self.build()
        self.assertEqual(direct.files[lvl.ARCHIVE_PATH], (mod / lvl.ARCHIVE_PATH).read_bytes())
        self.assertEqual(direct.files[lvl.PHYSICS_PATH], (mod / lvl.PHYSICS_PATH).read_bytes())
        # a second run into the same folder is refused and leaves the first alone
        again = self.run_tool("build", "--game", str(self.game), "--out", str(out), "--ce-min", "0.1.13")
        self.assertEqual(2, again.returncode)
        self.assertIn("already holds", again.stderr.decode())
        self.assertEqual(manifest, json.loads((mod / "mod.json").read_text()))

    def test_build_options_reach_the_mod(self) -> None:
        out = self.root / "options"
        result = self.run_tool("build", "--game", str(self.game), "--out", str(out), "--ce-min", "0.1.13", "--ce-max", "0.2", "--id", "duel2",
                               "--name", "Duel two", "--version", "7", "--author", "me", "--lives", "5", "--ai-state", "4")
        self.assertEqual(0, result.returncode, result.stderr)
        manifest = json.loads((out / "duel2/mod.json").read_text())
        self.assertEqual(("duel2", "Duel two", "7", "me", "0.2"), (manifest["id"], manifest["name"], manifest["version"], manifest["author"], manifest["ce_max"]))
        self.assertEqual(self.build(lives=5, ai_state=4).files[lvl.ARCHIVE_PATH], (out / "duel2" / lvl.ARCHIVE_PATH).read_bytes())
        self.assertIn("Each player has 5 lives", manifest["description"])

    def test_refusals_exit_2_and_write_nothing(self) -> None:
        out = self.root / "mods"
        cases = (("inside the game", ["--out", str(self.game / "mods"), "--ce-min", "0.1.13"], "refused"),
                 ("a bad ce-min", ["--out", str(out), "--ce-min", "x"], "ce_min"),
                 ("lives of 0", ["--out", str(out), "--ce-min", "0.1.13", "--lives", "0"], "lives"),
                 ("an ai-state of 9", ["--out", str(out), "--ce-min", "0.1.13", "--ai-state", "9"], "ai-state"),
                 ("a bad id", ["--out", str(out), "--ce-min", "0.1.13", "--id", "Duel"], "mod id"),
                 ("ce-min after ce-max", ["--out", str(out), "--ce-min", "2", "--ce-max", "1"], "is after ce_max"))
        for label, args, words in cases:
            with self.subTest(label):
                result = self.run_tool("build", "--game", str(self.game), *args)
                self.assertEqual(2, result.returncode, result.stdout)
                self.assertIn(words, result.stderr.decode())
                self.assertFalse(out.exists())
                self.assertFalse((self.game / "mods").exists())
        missing = self.run_tool("build", "--game", str(self.game), "--out", str(out))
        self.assertEqual(2, missing.returncode)
        self.assertIn("--ce-min", missing.stderr.decode())
        self.assertFalse(out.exists())

    def test_gate_and_closure_report(self) -> None:
        # the authored files are not the game's, so the pin check is the one check that fails (the gate exits 1 for it)
        result = self.run_tool("gate", "--game", str(self.game))
        text = result.stdout.decode()
        self.assertEqual(1, result.returncode, text + result.stderr.decode())
        failed = [line for line in text.splitlines() if line.startswith("FAIL")]
        self.assertEqual(1, len(failed), text)
        self.assertTrue(failed[0].startswith("FAIL every pinned file is the one the recipe was checked against"), failed)
        self.assertRegex(text, r"(\d+) of (\d+) checks passed")
        strict = self.run_tool("gate", "--game", str(self.game), "--strict-pins")
        self.assertEqual(1, strict.returncode)
        self.assertIn("FAIL build", strict.stdout.decode())
        self.assertIn("--strict-pins", strict.stdout.decode())
        closure = self.run_tool("closure", "--game", str(self.game))
        self.assertEqual(0, closure.returncode, closure.stderr)
        report = json.loads(closure.stdout)
        self.assertEqual(["Aircarrier Multiplayer", "Air Fighter", "Fenrir Multiplayer", "Advanced Fighter"], report["units"])
        self.assertEqual(4, len(report["added"]["mesh"]))
        self.assertEqual(report["warnings"], [w for w in report["warnings"] if "SHA-256" in w])
        (self.game / "data/default physics.dat").write_bytes(b"bad")
        failed = self.run_tool("gate", "--game", str(self.game))
        self.assertEqual(1, failed.returncode)
        self.assertIn("FAIL build", failed.stdout.decode())

    def test_no_game_is_an_error(self) -> None:
        result = self.run_tool("gate")
        self.assertEqual(2, result.returncode)
        self.assertIn("--game", result.stderr.decode())
        result = self.run_tool("closure", "--game", str(self.root / "nothing"))
        self.assertEqual(2, result.returncode)
        self.assertIn("no such file", result.stderr.decode())
        result = self.run_tool("gate", "--game", str(self.root / "nothing"))
        self.assertEqual(1, result.returncode, "a build that cannot be made is a failed gate, not a usage error")


# ---- the retail gate --------------------------------------------------------------------------------------------------------
@unittest.skipUnless(os.environ.get("BEA_GAME"), "the retail gate needs BEA_GAME to name a game folder (read only)")
class RetailGate(unittest.TestCase):
    def test_the_recipe_applies_to_the_games_own_files(self) -> None:
        results = lvl.run_gate(Path(os.environ["BEA_GAME"]), strict_pins=True)
        failed = [(name, detail) for name, ok, detail in results if not ok]
        self.assertEqual([], failed)
        self.assertGreaterEqual(len(results), 20)
        print(f"retail gate: {len(results)} checks passed", file=sys.stderr)

    def test_the_retail_build_matches_what_was_played(self) -> None:
        build = lvl.build(lvl.Install(Path(os.environ["BEA_GAME"]), strict_pins=True))
        report = build.report
        self.assertEqual(["Aircarrier Multiplayer", "Air Fighter", "Fenrir Multiplayer", "Muspell Advanced Fighter"], report["closure"]["units"])
        self.assertEqual(10, len(report["added"]["mesh"]))
        self.assertEqual(5, len(report["added"]["text"]))
        self.assertEqual([295 + n for n in range(10)], [m["id"] for m in report["added"]["mesh"]])
        self.assertEqual(175596, report["physics"]["size"])
        self.assertEqual(0, len(build.warnings))


if __name__ == "__main__":
    unittest.main()
