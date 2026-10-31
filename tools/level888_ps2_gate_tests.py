#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks tools/level888_ps2_gate.py, the independent gate of the builder that takes the disc's world, on authored files (no game bytes): that every check passes on a good
build, and that each kind of fault in the builder's output is found by the check that names it (and by that one): a world that is not the member's, a missing descriptor, a
changed donor chunk, a physics file edited anywhere else, a header or a script reference that is wrong, a report that does not describe its files, a builder that is not
deterministic or that differs between the library and the importer, a mod folder that is not what mod.json says, a game folder that changes, a member that is not the pinned
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
        self.member = itests.member_bytes(self.body)
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
        return install, lvl.build(install, world_body=self.body)

    def checks(self, build, *, install=None, body=None, moddir=None) -> set[str]:
        install = install or lvl.Install(self.game)
        if not install.reads:
            lvl.build(install, world_body=self.body)
        found: dict[str, bool] = {}
        gate.gate_checks(self.game, install, self.member, self.body if body is None else body, build, moddir, imp.MOD_ID, lambda n, ok, d="": found.__setitem__(n, ok))
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
        self.assertGreaterEqual(len(verdicts), 38)
        for needed in ("the archive's RLWD is the member's world body, byte for byte", "deterministic: two builds from the same inputs give the same bytes",
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
        key = "the donor's chunks (terrain, lists, descriptors) are kept byte for byte and in order"
        self.assertIn(key, self.checks(self.with_chunks(build, changed), install=install))
        moved = list(chunks)
        other = next(i for i, (tag, _) in enumerate(chunks) if i > at and tag not in ("TEXT", "MESH", "WRES") and chunks[i] != chunks[at])
        moved[at], moved[other] = moved[other], moved[at]
        self.assertIn(key, self.checks(self.with_chunks(build, moved), install=install))

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


# ---- the retail gate ----------------------------------------------------------------------------------------------------------
@unittest.skipUnless((os.environ.get("BEA_PS2_MEMBER") or os.environ.get("BEA_PS2_IMAGE")) and os.environ.get("BEA_GAME") and os.environ.get("BEA_GATE_WORK"),
                     "needs BEA_PS2_MEMBER (or BEA_PS2_IMAGE), BEA_GAME and BEA_GATE_WORK")
class RetailGate(unittest.TestCase):
    def test_the_players_own_member_and_game_pass_every_check_with_strict_pins(self) -> None:
        source = Path(os.environ.get("BEA_PS2_MEMBER") or os.environ["BEA_PS2_IMAGE"])
        results = gate.run_gate(Path(os.environ["BEA_GAME"]), source, Path(os.environ["BEA_GATE_WORK"]), strict_pins=True)
        faults, findings = gate.verdict(results)
        self.assertEqual([], faults)
        self.assertGreaterEqual(len(results), 38)
        print(f"retail gate: {len(results)} checks, {len(faults)} faults, {len(findings)} findings", file=sys.stderr)


if __name__ == "__main__":
    unittest.main()
