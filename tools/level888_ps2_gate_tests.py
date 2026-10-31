#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks tools/level888_ps2_gate.py, the independent gate of the builder that takes the disc's world, on authored files (no game bytes): that every check passes on a good
build, and that each kind of fault in the builder's output is found by the check that names it (and by that one): a world that is not the member's, a missing descriptor, a
changed donor chunk, a shadow chunk that is not the member's, a physics file edited anywhere else, a header or a script reference that is wrong, a report that does not
describe its files, its shadows or its stand-ins, a description that does not say what came from where, a builder that is not deterministic or that differs between the library and
the importer, a mod folder that is not what mod.json says, a game folder that changes, a member that is not the pinned
one or not level 888, and a folder to stage in that lies inside the repository.

The retail gate runs only when BEA_PS2_MEMBER names the extracted member (or BEA_PS2_IMAGE the player's own image), BEA_GAME the game folder and BEA_GATE_WORK a private folder
(all but the last read only); it prints nothing but the verdict:

    BEA_PS2_MEMBER=/path/to/888_res_PS2.aya BEA_GAME=/path/to/game BEA_GATE_WORK=/path/to/private python3 tools/level888_ps2_gate_tests.py
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import struct
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

import level888_build as lvl
import level888_ps2_gate as gate
import level888_ps2_import as imp
import level888_ps2_import_tests as itests
import world_resources_encode as enc

TOOL = Path(gate.__file__).resolve()
GOOD = {"Venturer", "Fenrir"}
KEPT = "the donor's chunks (terrain, lists, descriptors) are kept byte for byte and in order, its baked shadows replaced by the member's shadow chunk"
SHADOW_CHUNK = "the archive's one shadow chunk is the member's, byte for byte"
SHADOW_REPORT = "the report says the shadows are the PS2 copy's, with the sizes of both chunks and the counts the decoder reads in the member's"
STAND_INS = ("the report's stand-ins are the replacements the physics file shows: the unit definition, the mesh it named, the one it names now, the file through which, and how many of the "
             "world's units use it")
DESCRIPTION = "the mod's description says what came from the PS2 copy and what from this game, and calls the shadow chunk empty only if it is"


def gate_model(folder) -> dict:
    """The importer tests' disc world with the scripts its units name made real: the three units are called after scripts the world holds."""
    model = itests.disc_model(folder)
    names = iter(("Venturer", "Fenrir", "Venturer"))
    for thing in model["things"]:
        if thing["kind"] == "unit":
            name = next(names)
            thing["init"]["script"] = thing["init"]["name"] = name
    return model


class GateCase(itests.ImportCase):
    """An authored game folder, a disc world whose script names are the world's own, and the member pinned."""

    def setUp(self) -> None:
        super().setUp()
        self.model = gate_model(self.folder)
        self.body = enc.write_world_body(self.model)
        self.shadows = itests.EMPTY_SHADOWS
        self.member = itests.member_bytes(self.body, shadows=self.shadows)
        self.member_path.write_bytes(self.member)
        pinned = self.pin()
        pinned.start()
        self.addCleanup(pinned.stop)
        self.work = self.root / "work"

    def verdicts(self, **options) -> dict[str, tuple[bool, str]]:
        results = gate.run_gate(self.game, options.pop("source", self.member_path), self.work, **options)
        self.assertEqual(len(results), len({name for name, _, _ in results}), "every check has its own name")
        return {name: (ok, detail) for name, ok, detail in results}

    def failed(self, **options) -> set[str]:
        return {name for name, (ok, _) in self.verdicts(**options).items() if not ok}

    # -- gate_checks on a doctored build: only the check that names the fault may fail
    def good(self):
        install = lvl.Install(self.game)
        return install, lvl.build(install, world_body=self.body, shadows=self.shadows)

    def checks(self, build, *, install=None, body=None, shadows=None, moddir=None) -> set[str]:
        install = install or lvl.Install(self.game)
        if not install.reads:
            lvl.build(install, world_body=self.body, shadows=self.shadows)
        found: dict[str, bool] = {}
        gate.gate_checks(self.game, install, self.member, self.body if body is None else body, self.shadows if shadows is None else shadows, build, moddir, imp.MOD_ID,
                         lambda n, ok, d="": found.__setitem__(n, ok))
        return {name for name, ok in found.items() if not ok}

    def chunks_of(self, build) -> list[tuple[str, bytes]]:
        return gate.chunk_list(b"".join(enc.inflate(enc.read_members(build.files[lvl.ARCHIVE_PATH]))))

    def with_chunks(self, build, chunks) -> lvl.Build:
        """The build with its archive repacked from `chunks` and the report's figures for the archive brought into line, so that only the doctored thing is wrong."""
        raw = b"".join(lvl.chunk_bytes(tag, payload) for tag, payload in chunks)
        archive = lvl.pack(raw)
        report = copy.deepcopy(build.report)
        report["archive"].update(size=len(archive), sha256=gate.sha256(archive), unpackedSize=len(raw))
        return lvl.Build({**build.files, lvl.ARCHIVE_PATH: archive}, report, [])

    def with_body(self, build, body: bytes) -> lvl.Build:
        wres = lvl.chunk_bytes("WRLD", lvl.chunk_bytes("WDAT", struct.pack("<ii", -1, lvl.LEVEL)) + lvl.chunk_bytes("RLWD", body))
        return self.with_chunks(build, [(tag, wres if tag == "WRES" else payload) for tag, payload in self.chunks_of(build)])


# ---- a good build ---------------------------------------------------------------------------------------------------------
class GoodBuildTests(GateCase):
    def test_every_check_passes_on_the_authored_build_and_none_is_skipped(self) -> None:
        verdicts = self.verdicts()
        self.assertEqual([], [name for name, (ok, _) in verdicts.items() if not ok])
        self.assertGreaterEqual(len(verdicts), 44)
        for needed in ("the archive's RLWD is the member's world body, byte for byte", "deterministic: two builds from the same inputs give the same bytes",
                       "the archive's one shadow chunk is the member's, byte for byte", "the member has one shadow chunk, and the decoder reads it",
                       "the mod's description says what came from the PS2 copy and what from this game, and calls the shadow chunk empty only if it is",
                       "the staged mod folder is what mod.json says, file by file, and holds nothing else",
                       "it is the original with the Fenrir's mesh name replaced and not one other byte changed"):
            self.assertIn(needed, verdicts)

    def test_the_staged_copy_is_removed_unless_it_is_kept(self) -> None:
        self.assertEqual(set(), self.failed())
        self.assertEqual([], list(self.work.iterdir()), "the gate cleans up what it staged")
        self.assertEqual(set(), self.failed(keep=True))
        kept = [p for p in self.work.iterdir()]
        self.assertEqual(1, len(kept))
        self.assertTrue((kept[0] / imp.MOD_ID / "mod.json").is_file())

    def test_the_gate_reads_the_game_folder_and_the_member_and_changes_neither(self) -> None:
        before = {p: p.read_bytes() for p in list(self.game.rglob("*")) + [self.member_path] if p.is_file()}
        self.assertEqual(set(), self.failed())
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_a_good_gate_run_from_an_image_is_the_same_but_for_the_pins_of_an_authored_image(self) -> None:
        self.assertEqual({"reading the source raised no pin warning"}, self.failed(source=self.image()), "an authored image's index is not the disc's")

    def test_a_world_with_only_the_venturer_needs_no_fenrir_but_the_physics_edit_is_still_the_recipe(self) -> None:
        model = gate_model(self.folder)
        model["things"] = [t for t in model["things"] if t["kind"] != "unit" or t["definition"] == lvl.VENTURER]
        member = self.root / "venturer.aya"
        member.write_bytes(itests.member_bytes(enc.write_world_body(model)))
        digest = gate.sha256(member.read_bytes())
        with mock.patch.dict(itests.ps2_disc.MEMBER_SHA256, {itests.ps2_disc.fold_member_path(itests.ps2_disc.LEVEL_888_MEMBER): digest}):
            self.assertEqual(set(), self.failed(source=member))


# ---- faults in the output --------------------------------------------------------------------------------------------------
class FaultTests(GateCase):
    def test_a_world_that_is_not_the_members_is_found(self) -> None:
        install = lvl.Install(self.game)
        authored = lvl.build(install)                         # the generator's own authored world in the same donor
        found = self.checks(authored, install=install)
        self.assertIn("the archive's RLWD is the member's world body, byte for byte", found)

    def test_a_changed_world_body_is_found_by_the_byte_check_and_the_header_check_alone_when_it_is_the_header(self) -> None:
        install, build = self.good()
        model = enc.read_world_model(self.body)
        model["header"]["worldType"] = 1
        found = self.checks(self.with_body(build, enc.write_world_body(model)), install=install)
        self.assertEqual({"the archive's RLWD is the member's world body, byte for byte", "the world header is the worldheaders.dat record for 888",
                          "it is a versus world (world type 2)"}, found)

    def test_a_script_a_thing_names_that_the_world_does_not_hold_is_found(self) -> None:
        install, build = self.good()
        model = enc.read_world_model(self.body)
        model["scripts"] = [s for s in model["scripts"] if s["name"] != "Fenrir"]
        found = self.checks(self.with_body(build, enc.write_world_body(model)), install=install)
        self.assertIn("every script a thing names is one of the world's scripts", found)

    def test_a_missing_start_point_is_found(self) -> None:
        install, build = self.good()
        model = enc.read_world_model(self.body)
        model["things"] = [t for t in model["things"] if not (t["kind"] == "start" and t["init"]["start"]["playerNumber"] == 2)]
        self.assertIn("the start points are those of players 1 and 2", self.checks(self.with_body(build, enc.write_world_body(model)), install=install))

    def test_a_world_that_names_a_unit_the_physics_file_lacks_stops_the_checks_with_an_error_not_a_pass(self) -> None:
        install, build = self.good()
        model = enc.read_world_model(self.body)
        model["things"].append(itests.unit_thing(lvl.VENTURER, "Venturer", 5.0) | {"definition": "No Such Unit"})
        with self.assertRaises(lvl.BuildError):                 # the closure over a unit the file lacks cannot be computed; run_gate turns this into one failed check
            self.checks(self.with_body(build, enc.write_world_body(model)), install=install)

    def test_a_missing_mesh_descriptor_is_found_with_its_textures_and_ids(self) -> None:
        install, build = self.good()
        added = {entry["name"] for entry in build.report["added"]["mesh"]}
        chunks = self.chunks_of(build)
        gone = next(i for i, (tag, payload) in enumerate(chunks) if tag == "MESH" and lvl.logical_key("MESH", payload)[1] in added)
        found = self.checks(self.with_chunks(build, chunks[:gone] + chunks[gone + 1:]), install=install)
        self.assertIn("every mesh the units need has a descriptor", found)
        self.assertIn("the MESH descriptors gained are exactly the ones reported, and none of the donor's is lost", found)

    def test_a_missing_texture_descriptor_is_found(self) -> None:
        install, build = self.good()
        added = {entry["name"] for entry in build.report["added"]["text"]}
        chunks = self.chunks_of(build)
        gone = next(i for i, (tag, payload) in enumerate(chunks) if tag == "TEXT" and lvl.logical_key("TEXT", payload)[1] in added)
        found = self.checks(self.with_chunks(build, chunks[:gone] + chunks[gone + 1:]), install=install)
        self.assertIn("every texture those meshes ask for has a descriptor", found)

    def test_a_descriptor_of_the_donor_that_is_lost_or_a_runtime_id_twice_is_found(self) -> None:
        install, build = self.good()
        chunks = self.chunks_of(build)
        first_mesh = next(i for i, (tag, _) in enumerate(chunks) if tag == "MESH")
        lost = self.checks(self.with_chunks(build, chunks[:first_mesh] + chunks[first_mesh + 1:]), install=install)
        self.assertIn("the MESH descriptors gained are exactly the ones reported, and none of the donor's is lost", lost)
        ids = [i for i, (tag, _) in enumerate(chunks) if tag == "MESH"]
        twice = list(chunks)
        twice[ids[-1]] = ("MESH", lvl.with_mesh_id(twice[ids[-1]][1], lvl.mesh_id(twice[ids[0]][1])))
        self.assertIn("no MESH runtime id twice; the new ones follow the donor's highest", self.checks(self.with_chunks(build, twice), install=install))

    def test_a_donor_chunk_that_changed_or_moved_is_found(self) -> None:
        install, build = self.good()
        chunks = self.chunks_of(build)
        at = next(i for i, (tag, _) in enumerate(chunks) if tag not in ("TEXT", "MESH", "WRES"))
        changed = list(chunks)
        changed[at] = (changed[at][0], changed[at][1][:-1] + bytes([changed[at][1][-1] ^ 1]))
        key = KEPT
        self.assertIn(key, self.checks(self.with_chunks(build, changed), install=install))
        moved = list(chunks)
        other = next(i for i, (tag, _) in enumerate(chunks) if i > at and tag not in ("TEXT", "MESH", "WRES") and chunks[i] != chunks[at])
        moved[at], moved[other] = moved[other], moved[at]
        self.assertIn(key, self.checks(self.with_chunks(build, moved), install=install))

    def test_a_shadow_chunk_that_is_not_the_members_is_found(self) -> None:
        install, build = self.good()
        chunks = self.chunks_of(build)
        at = next(i for i, (tag, _) in enumerate(chunks) if tag == "SSHD")
        donor_shadows = next(p for t, p in lvl.unpack(install, lvl.DONOR) if t == "SSHD")
        for label, payload in (("the donor's own", donor_shadows), ("one byte off", self.shadows[:-1] + bytes([self.shadows[-1] ^ 1])), ("longer", self.shadows + b"\0")):
            doctored = list(chunks)
            doctored[at] = ("SSHD", payload)
            found = self.checks(self.with_chunks(build, doctored), install=install)
            self.assertEqual({SHADOW_CHUNK, KEPT}, found, label)
        two = chunks[:at + 1] + [("SSHD", self.shadows)] + chunks[at + 1:]
        self.assertIn(SHADOW_CHUNK, self.checks(self.with_chunks(build, two), install=install), "two shadow chunks")
        none = chunks[:at] + chunks[at + 1:]
        self.assertIn(SHADOW_CHUNK, self.checks(self.with_chunks(build, none), install=install), "no shadow chunk")
        moved = list(chunks)
        moved.insert(1, moved.pop(at))
        found = self.checks(self.with_chunks(build, moved), install=install)
        self.assertIn(KEPT, found, "the chunk is the member's but in another place")
        self.assertNotIn(SHADOW_CHUNK, found, "its bytes are the member's")

    def test_a_physics_file_changed_anywhere_but_the_stand_in_is_found(self) -> None:
        install, build = self.good()
        physics = lvl.Physics(build.files[lvl.PHYSICS_PATH])
        victim = next(s for s in physics.statements if s.name == "Air Fighter")
        node = victim.nodes[-1]
        data = bytearray(build.files[lvl.PHYSICS_PATH])
        data[node.at + 8] ^= 1                                  # one bit of a mesh name of another unit
        doctored = lvl.Build({**build.files, lvl.PHYSICS_PATH: bytes(data)}, copy.deepcopy(build.report), [])
        found = self.checks(doctored, install=install)
        self.assertIn("the physics file differs from the original in exactly one unit definition", found)
        self.assertIn("it is the original with the Fenrir's mesh name replaced and not one other byte changed", found)

    def test_a_physics_file_without_the_stand_in_or_with_a_size_word_left_alone_is_found(self) -> None:
        install, build = self.good()
        original = install.read(lvl.PHYSICS_PATH, lvl.LIMIT_SMALL)
        key = "it is the original with the Fenrir's mesh name replaced and not one other byte changed"
        self.assertIn(key, self.checks(lvl.Build({**build.files, lvl.PHYSICS_PATH: original}, copy.deepcopy(build.report), []), install=install))
        statement = next(s for s in lvl.Physics(original).statements if s.name == lvl.FENRIR)
        data = bytearray(build.files[lvl.PHYSICS_PATH])
        struct.pack_into("<I", data, statement.at + 4, statement.size)        # the statement's size word left at the original's value
        self.assertIn(key, self.checks(lvl.Build({**build.files, lvl.PHYSICS_PATH: bytes(data)}, copy.deepcopy(build.report), []), install=install))

    def test_a_report_that_does_not_describe_its_files_is_found(self) -> None:
        install, build = self.good()
        for path, key, value in ((("archive",), "sha256", "0" * 64), (("archive",), "size", 1), (("archive",), "unpackedSize", 1), (("physics",), "sha256", "0" * 64),
                                 (("physics",), "size", 1), (("physics",), "was", 1)):
            report = copy.deepcopy(build.report)
            report[path[0]][key] = value
            self.assertIn("the report's archive and physics figures are the files' own", self.checks(lvl.Build(build.files, report, []), install=install), f"{path} {key}")
        for mutate in (lambda r: r["archive"].update(things=1), lambda r: r["archive"].update(worldBodyBytes=1), lambda r: r["scripts"].pop(),
                       lambda r: r["scripts"][0].update(instructions=9999), lambda r: r["scripts"][0].update(handlers=9999)):
            report = copy.deepcopy(build.report)
            mutate(report)
            self.assertIn("the report counts the world's things and scripts, and its body", self.checks(lvl.Build(build.files, report, []), install=install))
        for mutate in (lambda r: r.update(world="authored"), lambda r: r.update(lives=3), lambda r: r.update(aiState=0)):
            report = copy.deepcopy(build.report)
            mutate(report)
            self.assertIn("the report says the world is the PS2 copy's and that lives and the AI state had no part", self.checks(lvl.Build(build.files, report, []), install=install))
        for mutate in (lambda r: r["physics"].update(unit="Other"), lambda r: r["physics"].update(mesh="a -> b")):
            report = copy.deepcopy(build.report)
            mutate(report)
            self.assertIn("the report names the stand-in", self.checks(lvl.Build(build.files, report, []), install=install))

    def test_a_report_whose_shadows_do_not_describe_the_chunks_is_found(self) -> None:
        install, build = self.good()
        self.assertEqual({"from": "ps2-copy", "bytes": len(self.shadows), "donorBytes": 1, "shadows": 0, "partMaps": 0, "shadowedMaps": 0, "cells": 0}, build.report["shadows"])
        for label, mutate in (("from the donor", lambda r: r["shadows"].update({"from": "donor"})), ("bytes", lambda r: r["shadows"].update(bytes=1)),
                              ("the donor's size", lambda r: r["shadows"].update(donorBytes=544156)), ("a count", lambda r: r["shadows"].update(cells=1)),
                              ("a count missing", lambda r: r["shadows"].pop("partMaps")), ("an extra key", lambda r: r["shadows"].update(extra=1)),
                              ("no shadows entry", lambda r: r.pop("shadows"))):
            report = copy.deepcopy(build.report)
            mutate(report)
            self.assertEqual({SHADOW_REPORT}, self.checks(lvl.Build(build.files, report, []), install=install), label)

    def test_a_report_whose_stand_ins_are_not_the_replacements_in_the_physics_file_is_found(self) -> None:
        install, build = self.good()
        entry = {"kind": "mesh", "unit definition": lvl.FENRIR, "named": lvl.FENRIR_FILELESS_MESH, "used instead": lvl.FENRIR_MESH, "through": lvl.PHYSICS_PATH, "unitsInWorld": 1}
        self.assertEqual([entry], build.report["standIns"])
        for label, mutate in (("none reported", lambda r: r.update(standIns=[])), ("no key", lambda r: r.pop("standIns")), ("twice", lambda r: r["standIns"].append(dict(entry))),
                              ("another unit definition", lambda r: r["standIns"][0].update({"unit definition": lvl.VENTURER})),
                              ("another mesh named", lambda r: r["standIns"][0].update(named="some-mesh.msh")),
                              ("another mesh used", lambda r: r["standIns"][0].update({"used instead": "air-fighter.msh"})),
                              ("another file through which", lambda r: r["standIns"][0].update(through="data/other.dat")), ("another kind", lambda r: r["standIns"][0].update(kind="texture")),
                              ("no unit count", lambda r: r["standIns"][0].pop("unitsInWorld")), ("a unit count of 0", lambda r: r["standIns"][0].update(unitsInWorld=0)),
                              ("a unit count of 2", lambda r: r["standIns"][0].update(unitsInWorld=2)), ("a unit count that is true", lambda r: r["standIns"][0].update(unitsInWorld=True)),
                              ("a unit count that is a word", lambda r: r["standIns"][0].update(unitsInWorld="1")), ("an old key left in", lambda r: r["standIns"][0].pop("named")),
                              ("not a list", lambda r: r.update(standIns=dict(entry))), ("not entries", lambda r: r.update(standIns=["x"]))):
            report = copy.deepcopy(build.report)
            mutate(report)
            self.assertEqual({STAND_INS}, self.checks(lvl.Build(build.files, report, []), install=install), label)

    def test_an_archive_the_loader_would_not_walk_is_found(self) -> None:
        install, build = self.good()
        wdat = lvl.chunk_bytes("WDAT", struct.pack("<ii", -1, 857))
        wres = lvl.chunk_bytes("WRLD", wdat + lvl.chunk_bytes("RLWD", self.body))
        wrong_level = [(tag, wres if tag == "WRES" else payload) for tag, payload in self.chunks_of(build)]
        found = self.checks(self.with_chunks(build, wrong_level), install=install)
        self.assertIn("it passes the loader's structure walk", found)
        self.assertIn("the world names level 888 alone (no base world)", found)
        broken = lvl.Build({**build.files, lvl.ARCHIVE_PATH: b"not an archive"}, copy.deepcopy(build.report), [])
        found = self.checks(broken, install=install)
        self.assertIn("the archive is packed like the game's reader needs", found)
        self.assertIn("it passes the loader's structure walk", found)

    def test_a_game_that_changed_while_the_gate_ran_and_a_pin_that_does_not_match_are_found(self) -> None:
        install, build = self.good()
        (self.game / lvl.WORLDHEADERS_PATH).write_bytes((self.game / lvl.WORLDHEADERS_PATH).read_bytes() + b"")   # unchanged: nothing found
        self.assertNotIn("the game folder's files were not changed during the run", self.checks(build, install=install))
        path = self.game / lvl.PHYSICS_PATH
        path.write_bytes(path.read_bytes() + b"\0")
        self.assertIn("the game folder's files were not changed during the run", self.checks(build, install=install))
        install.warnings.append("a pinned file is not the one")
        self.assertIn("every pinned file is the one the recipe was checked against", self.checks(build, install=install))


# ---- faults in the builders, and in what is staged ----------------------------------------------------------------------------
class RunFaultTests(GateCase):
    def test_a_builder_that_is_not_deterministic_is_found(self) -> None:
        real = lvl.build
        calls = []

        def drifting(install, **options):
            result = real(install, **options)
            calls.append(1)
            if len(calls) == 2:
                result = lvl.Build({**result.files, lvl.ARCHIVE_PATH: result.files[lvl.ARCHIVE_PATH] + b"\0"}, result.report, result.warnings)
            return result
        with mock.patch.object(lvl, "build", drifting):
            self.assertIn("deterministic: two builds from the same inputs give the same bytes", self.failed())

    def test_a_builder_whose_output_depends_on_lives_or_the_ai_state_is_found(self) -> None:
        real = lvl.build

        def listening(install, **options):
            result = real(install, **options)
            if options.get("lives") == 7:
                result = lvl.Build({**result.files, lvl.PHYSICS_PATH: result.files[lvl.PHYSICS_PATH] + b"\0"}, result.report, result.warnings)
            return result
        with mock.patch.object(lvl, "build", listening):
            self.assertIn("lives and the AI state have no part in the disc's world", self.failed())

    def test_a_builder_that_ignores_the_members_shadow_chunk_is_found_even_when_the_importer_agrees_with_it(self) -> None:
        real = lvl.build

        def forgetful(install, **options):
            options.pop("shadows", None)
            return real(install, **options)
        with mock.patch.object(lvl, "build", forgetful):
            found = self.failed()
        self.assertEqual({SHADOW_CHUNK, KEPT, SHADOW_REPORT}, found)

    def test_a_description_that_does_not_say_what_came_from_where_is_found(self) -> None:
        install, build = self.good()
        moddir = self.root / "mods" / imp.MOD_ID
        imp.build(self.member_path, self.game, self.root / "mods", ce_min="0.1.13")
        self.assertEqual(set(), self.checks(build, install=install, moddir=moddir))
        manifest = json.loads((moddir / "mod.json").read_bytes())
        description = manifest["description"]
        self.assertIn("FROM YOUR PS2 COPY", description)
        self.assertIn("FROM THIS GAME", description)
        for label, text in (("the earlier wording", lvl.description("0.1.13", None).split("EXPERIMENTAL. ")[0] + "EXPERIMENTAL. Adds data/resources/888_res_PC.aya."),
                            ("no PS2 copy part", description.replace("FROM YOUR PS2 COPY", "FROM SOMEWHERE")), ("no game part", description.replace("FROM THIS GAME", "FROM SOMEWHERE")),
                            ("empty", ""), ("not text", 5), ("claims shadows are not empty", description.replace("empty static-shadow chunk", "static-shadow chunk")),
                            ("claims an empty chunk the disc does not have", None)):
            changed = copy.deepcopy(manifest)
            if text is None:
                changed.pop("description")
            else:
                changed["description"] = text
            (moddir / "mod.json").write_text(json.dumps(changed))
            self.assertIn(DESCRIPTION, self.checks(build, install=install, moddir=moddir), label)

    def test_a_description_that_calls_the_chunk_empty_when_the_decoder_finds_shadows_in_it_is_found(self) -> None:
        install, build = self.good()
        moddir = self.root / "mods" / imp.MOD_ID
        imp.build(self.member_path, self.game, self.root / "mods", ce_min="0.1.13")
        self.assertNotIn(DESCRIPTION, self.checks(build, install=install, moddir=moddir))
        with mock.patch.object(gate, "shadow_counts", return_value={"shadows": 1, "partMaps": 0, "shadowedMaps": 0, "cells": 0}):
            self.assertIn(DESCRIPTION, self.checks(build, install=install, moddir=moddir))

    def test_an_importer_that_stages_other_bytes_than_the_library_builds_is_found(self) -> None:
        real = imp.build

        def other(source, game, out, **options):
            summary, report = real(source, game, out, **options)
            path = Path(summary["root"]) / lvl.ARCHIVE_PATH
            path.write_bytes(path.read_bytes() + b"\0")
            return summary, report
        with mock.patch.object(imp, "build", other):
            found = self.failed()
        self.assertIn("the importer's staged files are the library build's", found)
        self.assertIn("the staged mod folder is what mod.json says, file by file, and holds nothing else", found)

    def test_an_importer_report_that_differs_from_the_librarys_is_found(self) -> None:
        real = imp.build

        def other(source, game, out, **options):
            summary, report = real(source, game, out, **options)
            return summary, report | {"world": "authored"}
        with mock.patch.object(imp, "build", other):
            self.assertIn("the importer's report is the library's, plus the member", self.failed())

    def test_a_staged_folder_that_is_not_what_mod_json_says_is_found(self) -> None:
        install, build = self.good()
        moddir = self.root / "mods" / imp.MOD_ID
        imp.build(self.member_path, self.game, self.root / "mods", ce_min="0.1.13")
        key = "the staged mod folder is what mod.json says, file by file, and holds nothing else"
        self.assertEqual(set(), self.checks(build, install=install, moddir=moddir))
        (moddir / "extra.txt").write_bytes(b"x")
        self.assertIn(key, self.checks(build, install=install, moddir=moddir))
        (moddir / "extra.txt").unlink()
        manifest = json.loads((moddir / "mod.json").read_bytes())
        for edit in (lambda m: m["files"][0].update(sha256="0" * 64), lambda m: m["files"][0].update(size=1), lambda m: m["files"].pop(), lambda m: m.update(id="other")):
            changed = copy.deepcopy(manifest)
            edit(changed)
            (moddir / "mod.json").write_text(json.dumps(changed))
            self.assertIn(key, self.checks(build, install=install, moddir=moddir))
        (moddir / "mod.json").write_text(json.dumps(manifest))
        path = moddir / lvl.PHYSICS_PATH
        saved = path.read_bytes()
        path.write_bytes(saved + b"\0")
        self.assertIn(key, self.checks(build, install=install, moddir=moddir))
        path.unlink()
        self.assertIn(key, self.checks(build, install=install, moddir=moddir))
        path.write_bytes(saved)
        path.rename(moddir / "moved")
        path.symlink_to(moddir / "moved")
        self.assertIn(key, self.checks(build, install=install, moddir=moddir))

    def test_a_mod_folder_that_is_a_link_or_not_a_folder_is_a_problem(self) -> None:
        install, build = self.good()
        self.assertEqual(["the mod folder is not a plain folder"], gate.mod_folder_problems(self.root / "nowhere", build.files, imp.MOD_ID))
        link = self.root / "link"
        link.symlink_to(self.root)
        self.assertEqual(["the mod folder is not a plain folder"], gate.mod_folder_problems(link, build.files, imp.MOD_ID))
        empty = self.root / imp.MOD_ID
        empty.mkdir()
        self.assertEqual(["mod.json cannot be read"], gate.mod_folder_problems(empty, build.files, imp.MOD_ID))


# ---- faults in the source --------------------------------------------------------------------------------------------------
class SourceFaultTests(GateCase):
    def test_a_member_that_is_not_the_pinned_one_is_found_and_strict_pins_refuse_it(self) -> None:
        other = self.root / "other.aya"
        other.write_bytes(itests.member_bytes(self.body, extra_children=[(b"EXTR", b"x")]))
        verdicts = self.verdicts(source=other)
        self.assertFalse(verdicts["the member is the pinned one (SHA-256)"][0])
        self.assertIn("the source", {n for n, (ok, _) in self.verdicts(source=other, strict_pins=True).items() if not ok})

    def test_a_member_of_another_level_or_with_a_base_world_is_found(self) -> None:
        wrong = self.root / "857.aya"
        wrong.write_bytes(itests.member_bytes(self.body, level=857))
        self.assertIn("the member's world is level 888 alone, one RLWD, no base world", self.failed(source=wrong))
        based = self.root / "based.aya"
        based.write_bytes(itests.member_bytes(self.body, base=10, extra_children=[(b"BSWD", self.body)]))
        self.assertIn("the member's world is level 888 alone, one RLWD, no base world", self.failed(source=based))

    def test_a_member_with_no_readable_world_or_a_body_that_does_not_read_back_stops_the_gate_with_a_failed_check(self) -> None:
        none = self.root / "none.aya"
        none.write_bytes(b"LVLR" + bytes(60))
        self.assertIn("the member has a readable world", self.failed(source=none))
        junk = self.root / "junk.aya"
        junk.write_bytes(itests.member_bytes(b"not a world body at all"))
        self.assertIn("the member's world body reads back unchanged", self.failed(source=junk))

    def test_a_member_without_exactly_one_readable_shadow_chunk_stops_the_gate_with_a_failed_check(self) -> None:
        key = "the member has one shadow chunk, and the decoder reads it"
        for label, member in (("none", itests.member_bytes(self.body, shadows=None)), ("two", itests.member_bytes(self.body, extra_shadow_chunks=1)),
                              ("unreadable", itests.member_bytes(self.body, shadows=b"not shadows")), ("trailing bytes", itests.member_bytes(self.body, shadows=itests.EMPTY_SHADOWS + b"x"))):
            path = self.root / "shadow.aya"
            path.write_bytes(member)
            digest = gate.sha256(member)
            with mock.patch.dict(itests.ps2_disc.MEMBER_SHA256, {itests.ps2_disc.fold_member_path(itests.ps2_disc.LEVEL_888_MEMBER): digest}):
                verdicts = self.verdicts(source=path)
            self.assertFalse(verdicts[key][0], label)
            self.assertNotIn("build", verdicts, label)

    def test_a_source_that_cannot_be_read_is_one_failed_check(self) -> None:
        self.assertEqual({"the source"}, self.failed(source=self.root / "missing"))

    def test_a_build_the_game_cannot_take_is_one_failed_check(self) -> None:
        (self.game / lvl.ARCHIVE_PATH).write_bytes(b"x")
        self.assertIn("build", self.failed())

    def test_an_importer_that_cannot_build_is_one_failed_check_and_the_library_checks_still_ran(self) -> None:
        with mock.patch.object(imp, "build", side_effect=imp.ImportFailure("no")):
            verdicts = self.verdicts()
        self.assertFalse(verdicts["the importer's build"][0])
        self.assertTrue(verdicts["the archive's RLWD is the member's world body, byte for byte"][0])


# ---- the private folder -----------------------------------------------------------------------------------------------------
class PrivateFolderTests(unittest.TestCase):
    def test_a_folder_inside_the_repository_is_refused_except_under_local_data_and_local_lab(self) -> None:
        repo = gate.TOOLS.parent
        for bad in (repo / "tools" / "x", repo / "x", repo / "local-data" / ".." / "tools", repo):
            with self.assertRaises(gate.GateRefusal, msg=str(bad)):
                gate.private_folder(bad)
        for good in (repo / "local-data" / "x", repo / "local-lab" / "a" / "b", Path("/tmp/somewhere"), Path("/var/tmp/x")):
            gate.private_folder(good)

    def test_a_link_into_the_repository_does_not_get_a_folder_past_the_guard(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link"
            link.symlink_to(gate.TOOLS)
            with self.assertRaises(gate.GateRefusal):
                gate.private_folder(link / "x")

    def test_run_gate_refuses_before_reading_anything(self) -> None:
        with self.assertRaises(gate.GateRefusal):
            gate.run_gate(Path("/nowhere"), Path("/nowhere/member"), gate.TOOLS / "x")
        self.assertFalse((gate.TOOLS / "x").exists())


# ---- the command line -------------------------------------------------------------------------------------------------------
class CommandLineTests(GateCase):
    def run_main(self, *argv) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            return gate.main(list(argv)), out.getvalue()

    def test_a_good_run_prints_one_line_per_check_and_exits_zero(self) -> None:
        code, text = self.run_main("gate", str(self.member_path), "--game", str(self.game), "--work", str(self.work))
        self.assertEqual(0, code)
        lines = text.strip().splitlines()
        self.assertTrue(all(line.startswith("ok   ") for line in lines[:-1]))
        total = len(lines) - 1
        self.assertEqual(f"{total} of {total} checks passed", lines[-1])

    def test_a_failed_check_exits_one_and_names_it(self) -> None:
        wrong = self.root / "857.aya"
        wrong.write_bytes(itests.member_bytes(self.body, level=857))
        code, text = self.run_main("gate", str(wrong), "--game", str(self.game), "--work", str(self.work))
        self.assertEqual(1, code)
        self.assertIn("FAIL the member's world is level 888 alone", text)

    def test_a_finding_about_the_discs_world_is_a_note_and_leaves_the_exit_code_alone(self) -> None:
        model = gate_model(self.folder)
        next(t for t in model["things"] if t["kind"] == "level-script")["init"]["script"] = "a script the world does not hold"
        member = self.root / "finding.aya"
        member.write_bytes(itests.member_bytes(enc.write_world_body(model)))
        digest = gate.sha256(member.read_bytes())
        with mock.patch.dict(itests.ps2_disc.MEMBER_SHA256, {itests.ps2_disc.fold_member_path(itests.ps2_disc.LEVEL_888_MEMBER): digest}):
            code, text = self.run_main("gate", str(member), "--game", str(self.game), "--work", str(self.work))
        self.assertEqual(0, code)
        self.assertIn("note every script a thing names is one of the world's scripts", text)
        self.assertNotIn("FAIL", text)
        self.assertTrue(text.strip().splitlines()[-1].endswith("1 findings about the disc's world (not the builder's)"))

    def test_the_verdict_separates_faults_from_findings(self) -> None:
        results = [("a", True, ""), ("b", False, ""), ("it is a versus world (world type 2)", False, ""), ("the start points are those of players 1 and 2", True, "")]
        self.assertEqual((["b"], ["it is a versus world (world type 2)"]), gate.verdict(results))
        self.assertEqual(set(gate.FINDINGS), {"it is a versus world (world type 2)", "every script a thing names is one of the world's scripts", "the start points are those of players 1 and 2"})

    def test_the_output_names_no_asset_and_holds_no_bytes_of_the_member(self) -> None:
        _, text = self.run_main("gate", str(self.member_path), "--game", str(self.game), "--work", str(self.work))
        for what in (".msh", ".tga", "meshtex", "Chrome", "m_atf", "decoy", "Rock", "Unit0"):
            self.assertNotIn(what, text, what)

    def test_a_refusal_exits_two_with_one_line_and_no_traceback(self) -> None:
        done = subprocess.run([sys.executable, str(TOOL), "gate", str(self.member_path), "--game", str(self.game), "--work", str(gate.TOOLS / "x")],
                              capture_output=True, text=True, timeout=120)
        self.assertEqual(2, done.returncode)
        self.assertEqual("", done.stdout)
        self.assertEqual(1, len(done.stderr.strip().splitlines()))
        self.assertTrue(done.stderr.startswith("level 888 gate: "))
        self.assertNotIn("Traceback", done.stderr)

    def test_no_game_is_an_error(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "BEA_GAME"}
        done = subprocess.run([sys.executable, str(TOOL), "gate", str(self.member_path), "--work", str(self.work)], capture_output=True, text=True, timeout=120, env=env)
        self.assertEqual(2, done.returncode)


STAGE_DRY = "stage --dry-run changes nothing and names the line that starts the level"
STAGE_FRESH = "stage into a fresh folder puts the mod there byte for byte and a ce.ini that CE reads as naming it, and nothing else"
STAGE_TWICE = "a second stage of the same mod is refused and changes nothing"
STAGE_REPLACE = "stage --replace keeps the old copy aside and a backup of ce.ini, names the mod once and leaves nothing half-made"
STAGE_INI = "an existing ce.ini keeps its other settings, its line endings and the mods it already named, and is backed up"
STAGE_STAND_IN = "a ce.ini that names the stand-in mod too is said so in the plan, and both stay named"
STAGE_REAL = "the player's own CE folder, a link to it and a folder that holds it or lies inside it are refused, with or without the flag, and left as they were"
STAGE_FLAG = "with --into-my-real-folder only the mods line changes, the career stays, ce.ini is backed up and the launch line has no BEA_USER_DIR"
STAGE_NO_MODS = "a ce.ini that CE would read as no mods, or that is not a plain file, is refused and the folder is left as it was"
STAGE_LIMIT = "the mods= limit is exact: 2,047 bytes are accepted and CE reads them, 2,048 are refused"
STAGE_FAILURE = "a failure at the final ce.ini swap, or while the mod is copied, leaves the folder byte for byte as it was"
STAGE_UNTOUCHED = "no case touched the player's own CE folder (except the one allowed by the flag) or a bystander folder beside it"
STAGE_ALL = {STAGE_DRY, STAGE_FRESH, STAGE_TWICE, STAGE_REPLACE, STAGE_INI, STAGE_STAND_IN, STAGE_REAL, STAGE_FLAG, STAGE_NO_MODS, STAGE_LIMIT, STAGE_FAILURE, STAGE_UNTOUCHED}


# ---- stage ---------------------------------------------------------------------------------------------------------------------
class CeReadingTests(unittest.TestCase):
    """The gate's transcription of CE_SettingGetText (port/platform/common/ce.cpp) that it reads every staged ce.ini with."""

    def test_the_setting_is_read_the_way_ce_reads_it(self) -> None:
        read = gate.ce_setting_text
        for label, ini, want in (
                ("a plain line", b"mods=a\n", "a"), ("no final newline", b"mods=a", "a"), ("blanks and a CR around the value", b"mods= a , b \r\n", "a , b"),
                ("after other lines", b"x=1\r\nmods=a\nz=2\n", "a"), ("a tab around the value", b"mods=\ta\t\n", "a"),
                ("upper-case key", b"MODS=a\n", None), ("indented key", b" mods=a\n", None), ("blank before the equals sign", b"mods =a\n", None),
                ("another key that ends the same", b"xmods=a\n", None), ("a longer key", b"modsx=a\n", None), ("an empty value", b"mods=\n", None),
                ("only blanks", b"mods=  \r\n", None), ("two lines", b"mods=a\nmods=b\n", None), ("two lines, the second empty", b"mods=a\nmods=\n", None),
                ("a control byte", b"mods=a\x01b\n", None), ("a DEL", b"mods=a\x7fb\n", None), ("two CRs, one of them belongs to the value", b"mods=a\r\r\n", None),
                ("a CR inside the value", b"mods=a\rb\n", None), ("no such key", b"fullscreen=1\n", None), ("nothing", b"", None)):
            self.assertEqual(want, read(ini, "mods"), label)

    def test_the_limit_is_2047_bytes_of_value(self) -> None:
        self.assertEqual(2047, len(gate.ce_setting_text(b"mods=" + b"a" * 2047 + b"\n", "mods")))
        self.assertIsNone(gate.ce_setting_text(b"mods=" + b"a" * 2048 + b"\n", "mods"))
        self.assertEqual(3, len(gate.ce_setting_text(b"mods=abc\n", "mods", 4)))
        self.assertIsNone(gate.ce_setting_text(b"mods=abcd\n", "mods", 4))

    def test_the_snapshot_names_dirs_files_and_links_and_an_absent_root_is_empty(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory(dir="/var/tmp") as raw:
            root = Path(raw)
            (root / "d").mkdir()
            (root / "d" / "f").write_bytes(b"x")
            (root / "l").symlink_to("d")
            snap = gate.tree_snapshot(root)
            self.assertEqual({"d": ("dir",), "d/f": ("file", gate.sha256(b"x")), "l": ("link", "d")}, snap)
            self.assertEqual({}, gate.tree_snapshot(root / "absent"))

    def test_patched_puts_the_original_back_even_when_the_block_raises(self) -> None:
        class Owner:
            value = 1
        with self.assertRaises(RuntimeError), gate.patched(Owner, "value", 2):
            self.assertEqual(2, Owner.value)
            raise RuntimeError
        self.assertEqual(1, Owner.value)
        self.assertEqual("", gate.refused(lambda: None))
        self.assertEqual("no", gate.refused(self.fail_with, "no"))

    @staticmethod
    def fail_with(message):
        raise imp.ImportFailure(message)


class StageFaultTests(GateCase):
    """`stage` given a defect, one at a time: the stage section of the gate finds it by the check that names it."""

    def test_a_good_stage_passes_every_stage_check(self) -> None:
        verdicts = self.verdicts()
        self.assertTrue(STAGE_ALL <= set(verdicts), "every stage check is in the list")
        self.assertEqual([], [name for name in STAGE_ALL if not verdicts[name][0]])

    def test_a_stage_that_does_things_on_a_dry_run_is_found(self) -> None:
        real = imp.stage

        def doing(moddir, user_dir, **options):
            options["dry_run"] = False
            return real(moddir, user_dir, **options)
        with mock.patch.object(imp, "stage", doing):
            self.assertIn(STAGE_DRY, self.failed())

    def test_a_stage_that_writes_a_second_mods_line_is_found(self) -> None:
        real = imp.with_mod
        with mock.patch.object(imp, "with_mod", lambda ini, mod_id: (real(ini, mod_id)[0] + f"mods={mod_id}\n".encode(), real(ini, mod_id)[1])):
            failed = self.failed()
        self.assertIn(STAGE_FRESH, failed)
        self.assertIn(STAGE_INI, failed)

    def test_a_stage_that_does_not_refuse_a_second_copy_is_found(self) -> None:
        real = imp.stage

        def overwriting(moddir, user_dir, **options):
            options["replace"] = True
            return real(moddir, user_dir, **options)
        with mock.patch.object(imp, "stage", overwriting):
            failed = self.failed()
        self.assertIn(STAGE_TWICE, failed)
        self.assertTrue({STAGE_DRY, STAGE_FRESH, STAGE_REAL, STAGE_LIMIT} .isdisjoint(failed), failed)

    def test_a_stage_that_loses_the_line_endings_of_the_ini_is_found(self) -> None:
        real = imp.with_mod
        with mock.patch.object(imp, "with_mod", lambda ini, mod_id: (real(ini, mod_id)[0].replace(b"\r\n", b"\n"), real(ini, mod_id)[1])):
            self.assertIn(STAGE_INI, self.failed())

    def test_a_stage_that_forgets_the_mods_already_named_is_found(self) -> None:
        real = imp.with_mod
        with mock.patch.object(imp, "with_mod", lambda ini, mod_id: (b"mods=" + mod_id.encode() + b"\n", [])):
            failed = self.failed()
        self.assertTrue({STAGE_INI, STAGE_STAND_IN} <= failed, failed)
        self.assertIsNotNone(real)

    def test_a_stage_that_lets_the_players_folder_in_is_found(self) -> None:
        with mock.patch.object(imp, "real_conflict", return_value=None):
            failed = self.failed()
        self.assertIn(STAGE_REAL, failed)
        self.assertIn(STAGE_UNTOUCHED, failed)

    def test_a_limit_one_too_high_or_one_too_low_is_found(self) -> None:
        with mock.patch.object(imp, "MODS_VALUE_LIMIT", 2048):
            self.assertTrue({STAGE_LIMIT, STAGE_NO_MODS} <= self.failed())
        with mock.patch.object(imp, "MODS_VALUE_LIMIT", 2046):
            self.assertEqual({STAGE_LIMIT}, self.failed())

    def test_a_stage_that_leaves_its_scraps_after_a_failure_is_found(self) -> None:
        real = imp.stage

        def littering(moddir, user_dir, **options):
            try:
                return real(moddir, user_dir, **options)
            except imp.ImportFailure:
                if Path(user_dir).is_dir():
                    (Path(user_dir) / ".ce.ini.new-left-over").write_bytes(b"x")
                raise
        with mock.patch.object(imp, "stage", littering):
            failed = self.failed()
        self.assertTrue({STAGE_TWICE, STAGE_FAILURE, STAGE_NO_MODS} <= failed, failed)

    def test_a_stage_that_does_not_roll_back_a_failed_copy_is_found(self) -> None:
        with mock.patch.object(imp.shutil, "rmtree", lambda *a, **k: None):
            self.assertIn(STAGE_FAILURE, self.failed())

    def test_a_stage_that_forgets_the_ini_backup_is_found(self) -> None:
        real = imp.stage

        def unbacked(moddir, user_dir, **options):
            plan = real(moddir, user_dir, **options)
            for backup in Path(user_dir).glob("ce.ini.bak-*"):
                backup.unlink()
            return plan
        with mock.patch.object(imp, "stage", unbacked):
            failed = self.failed()
        self.assertTrue({STAGE_INI, STAGE_REPLACE, STAGE_FLAG} <= failed, failed)

    def test_a_stage_that_raises_something_unexpected_is_a_failed_check_not_a_crash_of_the_gate(self) -> None:
        with mock.patch.object(imp, "stage", side_effect=KeyError("boom")):
            self.assertIn("the stage checks ran to the end", self.failed())

    def test_the_stage_checks_do_not_use_the_callers_environment(self) -> None:
        with mock.patch.dict(os.environ, {"XDG_DATA_HOME": str(self.root / "callers-xdg"), "HOME": str(self.root / "callers-home"), "BEA_USER_DIR": str(self.root / "callers-user")}):
            self.assertEqual(set(), self.failed())
        self.assertFalse((self.root / "callers-xdg").exists() or (self.root / "callers-home").exists() or (self.root / "callers-user").exists())


# ---- the retail gate ----------------------------------------------------------------------------------------------------------
@unittest.skipUnless((os.environ.get("BEA_PS2_MEMBER") or os.environ.get("BEA_PS2_IMAGE")) and os.environ.get("BEA_GAME") and os.environ.get("BEA_GATE_WORK"),
                     "needs BEA_PS2_MEMBER (or BEA_PS2_IMAGE), BEA_GAME and BEA_GATE_WORK")
class RetailGate(unittest.TestCase):
    def test_the_players_own_member_and_game_pass_every_check_with_strict_pins(self) -> None:
        source = Path(os.environ.get("BEA_PS2_MEMBER") or os.environ["BEA_PS2_IMAGE"])
        results = gate.run_gate(Path(os.environ["BEA_GAME"]), source, Path(os.environ["BEA_GATE_WORK"]), strict_pins=True)
        faults, findings = gate.verdict(results)
        self.assertEqual([], faults)
        self.assertGreaterEqual(len(results), 44)
        print(f"retail gate: {len(results)} checks, {len(faults)} faults, {len(findings)} findings", file=sys.stderr)

    def test_the_members_shadow_chunk_is_the_one_the_game_itself_has_for_a_level_without_shadows(self) -> None:
        """The loader reads this chunk in the PC game's own archives of levels 331, 332, 741 and 742 (the builder's claim, here measured, counts only)."""
        source = Path(os.environ.get("BEA_PS2_MEMBER") or os.environ["BEA_PS2_IMAGE"])
        member, _ = imp.read_source(source)
        shadows = gate.member_shadows(member)
        self.assertIsNotNone(shadows)
        install = lvl.Install(Path(os.environ["BEA_GAME"]))
        equal, present = 0, 0
        for level in (331, 332, 741, 742):
            try:
                chunks = lvl.unpack(install, level)
            except lvl.BuildError:
                continue
            present += 1
            equal += [payload for tag, payload in chunks if tag == "SSHD"] == [shadows]
        print(f"retail gate: the member's shadow chunk ({len(shadows)} bytes) equals the game's own in {equal} of {present} archives of levels 331, 332, 741, 742", file=sys.stderr)
        self.assertGreaterEqual(present, 1)
        self.assertEqual(present, equal)


if __name__ == "__main__":
    unittest.main()
