#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks tools/level888_ps2_import.py and the generator's disc-world hook on authored files (no game bytes): the member from an extracted file, from an authored
image and from a zip of it; the disc's world taken as it is into the built archive (the same bytes, the loader's walk accepting it, the header, the ships and the
base level held to the recipe); and `stage` into an authored CE folder (ce.ini kept first, one mods= line, nothing overwritten, nothing outside the folder).

The retail gate runs only when BEA_PS2_IMAGE names the player's own image and BEA_GAME the game folder (both read only):

    BEA_PS2_IMAGE=/path/to/image BEA_GAME=/path/to/game python3 tools/level888_ps2_import_tests.py
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import level888_build as lvl
import level888_build_tests as built
import level888_ps2_import as imp
import ps2_disc
import ps2_disc_tests as disc_tests
import world_mod_stage as stage
import world_mod_stage_tests as stager_tests
import world_resources_encode as enc
import worldheaders_decode as headers

TOOL = Path(imp.__file__).resolve()


def unit_thing(definition: str, name: str, x: float) -> dict:
    return {"oid": lvl.wrd.OID_UNIT, "kind": "unit", "definition": definition, "diesOn": -1,
            "init": {"position": [x, 100.0, -60.0], "orientation": [0.0, 0.0, 0.0], "meshNumber": 0, "allegiance": 1, "target": -1, "script": name, "name": name,
                     "spawnScript": "", "active": 1, "attachScriptsToUnits": 0}}


def disc_model(folder: built.Folder, *, world_type: int | None = None, definitions=(lvl.VENTURER, lvl.FENRIR, lvl.VENTURER), base: int = -1) -> dict:
    """A world as the disc holds level 888's: two starts, a level script, three units of the two flagships' definitions, waypoints, three scripts and no base."""
    record = headers.parse_worldheaders((folder.root / "data/worldheaders.dat").read_bytes()).by_world(lvl.LEVEL)
    model = enc.read_world_model(folder.body)
    model["header"].update(lvl.header_from_record(record))
    if world_type is not None:
        model["header"]["worldType"] = world_type
    model["baseLevel"] = base
    model["scripts"] = lvl.compile_scripts(lvl.script_sources())
    level_script = built.point(27, "level-script", 1.0, 2.0, script="world888script", allegiance=2)
    things = [built.point(15, "start", 100.0 + n, 50.0, start=n, allegiance=n - 1) for n in (1, 2)] + [level_script]
    things += [unit_thing(d, f"Unit{n}", 10.0 * n) for n, d in enumerate(definitions)]
    things += [built.point(18, "waypoint", float(n), 5.0) for n in range(16)]
    model["things"] = things
    model["waypointPaths"] = []
    return model


EMPTY_SHADOWS = struct.pack("<4sI", b"SSHD", 0) + struct.pack("<4sI", b"SHDW", 0) + struct.pack("<i", 0) + struct.pack("<4sI", b"SLST", 0)


def member_bytes(body: bytes, *, level: int = lvl.LEVEL, base: int = -1, extra_children=(), shadows: bytes | None = EMPTY_SHADOWS, extra_shadow_chunks: int = 0) -> bytes:
    children = [(b"WDAT", struct.pack("<ii", base, level))] + list(extra_children) + [(b"RLWD", body)]
    chunks = stager_tests.level_chunks(level, texts=("a.tga",), meshes=("a.msh",), children=children)
    chunks = [(tag, shadows if tag == b"SSHD" else payload) for tag, payload in chunks if not (tag == b"SSHD" and shadows is None)]
    chunks += [(b"SSHD", EMPTY_SHADOWS)] * extra_shadow_chunks
    return stager_tests.level_stream(chunks)


class ImportCase(built.FolderTest):
    """An authored game folder, a world of level 888 as the disc would hold it, and the image and member files around it."""

    def setUp(self) -> None:
        super().setUp()
        self.model = disc_model(self.folder)
        self.body = enc.write_world_body(self.model)
        self.member = member_bytes(self.body)
        self.member_path = self.root / "888_res_PS2.aya"
        self.member_path.write_bytes(self.member)

    def image(self, member: bytes | None = None, *, zipped: bool = False) -> Path:
        package = disc_tests.package([(disc_tests.TARGET, self.member if member is None else member), ("\\data\\language\\english.dat", b"x" * 100)])
        data = bytes(disc_tests.Image(files=[(b"DATA0.NYO;1", package)]).bytes)
        path = self.root / ("image.zip" if zipped else "image.iso")
        if zipped:
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("Battle Engine Aquila (Test).iso", data)
        else:
            path.write_bytes(data)
        return path

    def pin(self) -> mock._patch:
        """The authored member is not the game's: pin its own digest for the checks that want a pinned member."""
        return mock.patch.dict(ps2_disc.MEMBER_SHA256, {ps2_disc.fold_member_path(ps2_disc.LEVEL_888_MEMBER): hashlib.sha256(self.member).hexdigest()})


# ---- the member ---------------------------------------------------------------------------------------------------------
class SourceTests(ImportCase):
    def test_a_member_file_an_iso_and_a_zip_give_the_same_bytes(self) -> None:
        for label, source in (("member", self.member_path), ("iso", self.image()), ("zip", self.image(zipped=True))):
            with self.subTest(label):
                data, record = imp.read_source(source)
                self.assertEqual(self.member, data)
                self.assertEqual(hashlib.sha256(self.member).hexdigest(), record["sha256"])
                self.assertEqual(len(self.member), record["bytes"])
                self.assertEqual("member" if label == "member" else "image", record["from"])

    def test_an_unpinned_member_warns_and_strict_pins_refuse_it(self) -> None:
        for source in (self.member_path, self.image()):
            with self.subTest(source.name):
                self.assertTrue(imp.read_source(source)[1]["warnings"])
                with self.assertRaises(imp.ImportFailure):
                    imp.read_source(source, strict_pins=True)

    def test_a_pinned_member_has_no_warning_from_a_member_file(self) -> None:
        with self.pin():
            self.assertEqual([], imp.read_source(self.member_path, strict_pins=True)[1]["warnings"])

    def test_a_file_that_is_not_readable_or_not_an_image_is_refused_by_name(self) -> None:
        for path, fragment in ((self.root / "missing", "cannot read"), (self.write("junk.bin", b"not an image" * 400), "")):
            with self.subTest(path.name), self.assertRaises(imp.ImportFailure) as caught:
                imp.read_source(path)
            self.assertIn(fragment, str(caught.exception))

    def test_a_member_file_over_the_ceiling_is_refused_without_being_read_whole(self) -> None:
        with mock.patch.object(ps2_disc, "MAX_MEMBER_BYTES", len(self.member) - 1), self.assertRaisesRegex(imp.ImportFailure, "ceiling"):
            imp.read_source(self.member_path)

    def write(self, name: str, data: bytes) -> Path:
        path = self.root / name
        path.write_bytes(data)
        return path


class WorldTests(ImportCase):
    def test_the_world_of_a_member_is_its_one_rlwd_body(self) -> None:
        self.assertEqual(self.body, imp.world_body(self.member))

    def test_a_world_of_another_level_a_base_level_or_a_second_body_is_refused(self) -> None:
        cases = {
            "another level": (member_bytes(self.body, level=857), "level 857"),
            "a base level": (member_bytes(self.body, base=10, extra_children=[(b"BSWD", self.body)]), "base 10"),
            "a base body with no base level": (member_bytes(self.body, extra_children=[(b"BSWD", self.body)]), "BSWD"),
            "no world at all": (b"LVLR" + struct.pack("<I", 4) + struct.pack("<I", 103), ""),
        }
        for label, (data, fragment) in cases.items():
            with self.subTest(label), self.assertRaises(imp.ImportFailure) as caught:
                imp.world_body(data)
            self.assertIn(fragment, str(caught.exception))

    def test_inspect_gives_counts_and_nothing_that_names_or_holds_the_content(self) -> None:
        report = imp.inspect(self.member)
        self.assertEqual({"AYAD": 1, "ERES": 1, "IMPS": 1, "LNDS": 1, "LVLR": 1, "MESH": 1, "SSHD": 1, "SURF": 1, "TARG": 1, "TEXT": 1, "WRES": 1}, report["chunksByTag"])
        self.assertTrue(report["everyByteAccounted"])
        world = report["world"]
        self.assertEqual({"start": 2, "level-script": 1, "unit": 3, "waypoint": 16}, world["thingsByKind"])
        self.assertEqual((22, 3, 0, 2, True), (world["things"], world["scripts"], world["waypointPaths"], world["worldType"], world["readsBackUnchanged"]))
        text = json.dumps(report)
        for name in (lvl.VENTURER, lvl.FENRIR, "world888script", "Fenrir"):
            self.assertNotIn(name, text, "counts only: no definition, script or thing name")


# ---- the build ----------------------------------------------------------------------------------------------------------
class BuildTests(ImportCase):
    def built(self, **more):
        return lvl.build(lvl.Install(self.game), world_body=self.body, **more)

    def test_the_archive_holds_the_discs_world_body_byte_for_byte_and_the_loader_walk_accepts_it(self) -> None:
        result = self.built()
        raw = b"".join(enc.inflate(enc.read_members(result.files[lvl.ARCHIVE_PATH])))
        self.assertIsNone(stage.check_level_archive(raw, lvl.LEVEL))
        worlds = enc.level_worlds(raw)
        self.assertEqual((lvl.LEVEL, -1, ["RLWD"]), (worlds["realLevel"], worlds["baseLevel"], sorted(worlds["bodies"])))
        self.assertEqual(self.body, worlds["bodies"]["RLWD"])
        self.assertEqual("ps2-copy", result.report["world"])
        self.assertEqual((None, None), (result.report["lives"], result.report["aiState"]))
        self.assertEqual({"Fenrir", "Venturer", "world888script"}, {s["name"] for s in result.report["scripts"]})
        self.assertEqual(len(self.model["things"]), result.report["archive"]["things"])

    def test_the_closure_is_computed_from_the_units_the_world_names(self) -> None:
        only_venturer = disc_model(self.folder, definitions=(lvl.VENTURER,))
        result = lvl.build(lvl.Install(self.game), world_body=enc.write_world_body(only_venturer))
        self.assertNotIn(lvl.FENRIR, result.report["closure"]["units"])
        both = self.built()
        self.assertIn(lvl.FENRIR, both.report["closure"]["units"])
        self.assertLess(len(result.report["closure"]["meshes"]), len(both.report["closure"]["meshes"]))

    def test_the_authored_world_is_not_made_and_its_scripts_are_not_compiled(self) -> None:
        with mock.patch.object(lvl, "build_world", side_effect=AssertionError("authored world")), \
                mock.patch.object(lvl, "compile_scripts", side_effect=AssertionError("authored scripts")):
            self.built()

    def test_the_fenrir_mesh_the_pc_game_lacks_still_goes_through_the_physics_edit(self) -> None:
        result = self.built()
        text = result.files[lvl.PHYSICS_PATH]
        self.assertNotIn(lvl.FENRIR_FILELESS_MESH.encode(), text)
        self.assertIn(lvl.FENRIR_MESH.encode(), text)

    def test_a_header_that_disagrees_with_worldheaders_dat_is_refused(self) -> None:
        wrong = enc.write_world_body(disc_model(self.folder, world_type=1))
        with self.assertRaisesRegex(lvl.BuildError, "worldType"):
            lvl.build(lvl.Install(self.game), world_body=wrong)

    def test_a_world_with_a_base_level_no_units_or_a_unit_the_physics_file_lacks_is_refused(self) -> None:
        with self.assertRaisesRegex(lvl.BuildError, "base level"):
            lvl.build(lvl.Install(self.game), world_body=enc.write_world_body(disc_model(self.folder, base=10)))
        with self.assertRaisesRegex(lvl.BuildError, "no unit"):
            lvl.build(lvl.Install(self.game), world_body=enc.write_world_body(disc_model(self.folder, definitions=())))
        with self.assertRaises(lvl.BuildError):
            lvl.build(lvl.Install(self.game), world_body=enc.write_world_body(disc_model(self.folder, definitions=("No Such Unit",))))

    def test_a_body_that_does_not_read_back_unchanged_is_refused(self) -> None:
        with mock.patch.object(enc, "write_world_body", return_value=b"other"), self.assertRaisesRegex(lvl.BuildError, "read back unchanged"):
            lvl.disc_world(self.body, headers.parse_worldheaders((self.game / "data/worldheaders.dat").read_bytes()).by_world(lvl.LEVEL))

    def test_the_donors_baked_shadows_are_replaced_by_the_members_shadow_chunk(self) -> None:
        plain = self.built()
        self.assertEqual("donor", plain.report["shadows"]["from"])
        shadowless = lvl.build(lvl.Install(self.game), world_body=self.body, shadows=EMPTY_SHADOWS)
        self.assertEqual({"from": "ps2-copy", "bytes": 28, "donorBytes": 1, "shadows": 0, "partMaps": 0, "shadowedMaps": 0, "cells": 0}, shadowless.report["shadows"])
        chunks = {tag: payload for tag, payload in self.unpacked(shadowless)}
        self.assertEqual(EMPTY_SHADOWS, chunks["SSHD"])
        before, after = self.unpacked(plain), self.unpacked(shadowless)
        self.assertEqual([t for t, _ in before], [t for t, _ in after], "the same chunks in the same order")
        self.assertEqual([(t, p) for t, p in before if t != "SSHD"], [(t, p) for t, p in after if t != "SSHD"], "nothing else changes")

    def test_a_shadow_chunk_the_decoder_cannot_read_or_a_donor_without_exactly_one_is_refused(self) -> None:
        for label, payload in (("garbage", b"not shadows"), ("empty", b""), ("trailing bytes", EMPTY_SHADOWS + b"x")):
            with self.subTest(label), self.assertRaisesRegex(lvl.BuildError, "shadow chunk cannot be read"):
                lvl.build(lvl.Install(self.game), world_body=self.body, shadows=payload)

    def test_the_importer_hands_the_members_shadow_chunk_to_the_build_and_refuses_a_member_without_exactly_one(self) -> None:
        summary, report = imp.build(self.member_path, self.game, self.root / "shadow-mods", ce_min="0.1.13")
        self.assertEqual("ps2-copy", report["shadows"]["from"])
        raw = b"".join(enc.inflate(enc.read_members((Path(summary["root"]) / lvl.ARCHIVE_PATH).read_bytes())))
        self.assertEqual(EMPTY_SHADOWS, next(raw[at:at + size] for tag, at, size in enc.chunks(raw) if tag == "SSHD"))
        for label, member in (("none", member_bytes(self.body, shadows=None)), ("two", member_bytes(self.body, extra_shadow_chunks=1))):
            with self.subTest(label), self.assertRaisesRegex(imp.ImportFailure, "shadow chunks"):
                imp.shadow_chunk(member)
        self.assertEqual(28, imp.inspect(self.member)["world"]["shadowBytes"])

    def test_the_authored_world_path_is_unchanged_by_the_hook(self) -> None:
        result = lvl.build(lvl.Install(self.game))
        self.assertEqual(("authored", lvl.DEFAULT_LIVES), (result.report["world"], result.report["lives"]))
        self.assertIn("lives", lvl.description("0.1.13"))
        self.assertNotIn("PS2", lvl.description("0.1.13"))

    def test_the_description_of_a_disc_world_says_it_is_built_from_the_players_own_ps2_copy(self) -> None:
        text = lvl.description("0.1.13", None)
        self.assertIn("from your own PS2 copy", text)
        self.assertIn("0.1.13", text)
        self.assertTrue(text.isascii())
        self.assertLessEqual(len(text), 1024)

    def test_the_whole_build_stages_a_mod_the_loader_oracle_accepts(self) -> None:
        out = self.root / "mods"
        summary, report = imp.build(self.member_path, self.game, out, ce_min="0.1.13")
        folder = out / imp.MOD_ID
        self.assertEqual(str(folder), summary["root"])
        manifest = imp.check_mod_folder(folder)
        self.assertEqual(imp.MOD_ID, manifest["id"])
        self.assertEqual({lvl.ARCHIVE_PATH, lvl.PHYSICS_PATH}, {f["path"] for f in manifest["files"]})
        self.assertEqual("member", report["member"]["from"])
        self.assertTrue(report["member"]["warnings"], "the authored member is not pinned")
        for entry in manifest["files"]:
            self.assertEqual(hashlib.sha256((folder / entry["path"]).read_bytes()).hexdigest(), entry["sha256"])

    def test_the_whole_build_from_an_image_gives_the_same_archive_as_from_the_member(self) -> None:
        a = imp.build(self.member_path, self.game, self.root / "a", ce_min="0.1.13")[0]
        b = imp.build(self.image(zipped=True), self.game, self.root / "b", ce_min="0.1.13")[0]
        self.assertEqual([f["sha256"] for f in a["files"]], [f["sha256"] for f in b["files"]], "the same inputs, the same bytes")

    def test_a_build_is_refused_when_the_game_already_has_the_archive_or_the_source_is_wrong(self) -> None:
        (self.game / lvl.ARCHIVE_PATH).write_bytes(b"x")
        with self.assertRaises(imp.ImportFailure):
            imp.build(self.member_path, self.game, self.root / "c", ce_min="0.1.13")
        (self.game / lvl.ARCHIVE_PATH).unlink()
        with self.assertRaises(imp.ImportFailure):
            imp.build(self.root / "missing", self.game, self.root / "d", ce_min="0.1.13")
        self.assertFalse((self.root / "c").exists() or (self.root / "d").exists(), "a refused build leaves no folder")


# ---- stage ----------------------------------------------------------------------------------------------------------------
class StageTests(ImportCase):
    def setUp(self) -> None:
        super().setUp()
        imp.build(self.member_path, self.game, self.root / "mods", ce_min="0.1.13")
        self.mod = self.root / "mods" / imp.MOD_ID
        self.ce = self.root / "ce-user"                # an existing folder that is not the player's own
        self.ce.mkdir()
        self.ini = self.ce / "ce.ini"
        self.ini.write_bytes(b"sharp_text=1\nwidescreen=1\n")
        self.env = {"XDG_DATA_HOME": str(self.root / "xdg")}          # so the player's own folder is root/xdg/onslaught-ce, which no test touches
        self.real = self.root / "xdg" / "onslaught-ce"
        self.clock = lambda: (2026, 10, 30, 23, 45, 30, 0, 0, 0)

    def stage(self, **more) -> dict:
        return imp.stage(self.mod, self.ce, clock=self.clock, env=self.env, **more)

    def make_real(self) -> None:
        (self.real / "savegames").mkdir(parents=True)
        (self.real / "savegames" / "Career.bes").write_bytes(b"career")
        (self.real / "ce.ini").write_bytes(b"widescreen=1\n")

    def test_the_mod_is_copied_ce_ini_is_kept_and_one_mods_line_is_added(self) -> None:
        plan = self.stage()
        target = self.ce / "mods" / imp.MOD_ID
        self.assertEqual(imp.check_mod_folder(self.mod), imp.check_mod_folder(target))
        self.assertEqual(b"sharp_text=1\nwidescreen=1\n", (self.ce / "ce.ini.bak-20261030T234530Z").read_bytes())
        self.assertEqual(b"sharp_text=1\nwidescreen=1\nmods=" + imp.MOD_ID.encode() + b"\n", self.ini.read_bytes())
        self.assertEqual([], plan["modsBefore"])
        self.assertFalse(plan["dryRun"])
        self.assertEqual(sorted(["ce.ini", "ce.ini.bak-20261030T234530Z", "mods"]), sorted(p.name for p in self.ce.iterdir()), "nothing else is left behind")

    def test_a_dry_run_says_what_would_happen_and_changes_nothing(self) -> None:
        before = sorted(str(p) for p in self.ce.rglob("*")), self.ini.read_bytes()
        plan = self.stage(dry_run=True)
        self.assertTrue(plan["dryRun"])
        self.assertEqual(before, (sorted(str(p) for p in self.ce.rglob("*")), self.ini.read_bytes()))

    def test_an_existing_mods_line_gets_the_id_at_its_end_and_keeps_its_line_ending(self) -> None:
        self.ini.write_bytes(b"a=1\r\nmods=first, second\r\nb=2\r\n")
        plan = self.stage()
        self.assertEqual(["first", "second"], plan["modsBefore"])
        self.assertEqual(b"a=1\r\nmods=first,second," + imp.MOD_ID.encode() + b"\r\nb=2\r\n", self.ini.read_bytes())

    def test_the_id_is_not_added_twice_and_moves_to_the_end(self) -> None:
        self.ini.write_bytes(b"mods=" + imp.MOD_ID.encode() + b",other\n")
        self.stage()
        self.assertEqual(b"mods=other," + imp.MOD_ID.encode() + b"\n", self.ini.read_bytes())

    def test_a_missing_ce_ini_is_made_without_a_backup(self) -> None:
        self.ini.unlink()
        plan = self.stage()
        self.assertIsNone(plan["iniBackup"])
        self.assertEqual(b"mods=" + imp.MOD_ID.encode() + b"\n", self.ini.read_bytes())

    def test_an_existing_folder_is_refused_unless_replace_moves_it_aside(self) -> None:
        self.stage()
        with self.assertRaisesRegex(imp.ImportFailure, "exists already"):
            self.stage()
        marker = self.ce / "mods" / imp.MOD_ID / "marker"
        marker.write_bytes(b"old")
        with self.assertRaises(imp.ImportFailure):          # a changed folder is also refused without --replace
            self.stage()
        self.clock = lambda: (2026, 10, 30, 23, 46, 0, 0, 0, 0)
        plan = self.stage(replace=True)
        self.assertEqual(b"old", (self.ce / "mods" / f"{imp.MOD_ID}.old-20261030T234600Z" / "marker").read_bytes())
        self.assertFalse((self.ce / "mods" / imp.MOD_ID / "marker").exists())
        self.assertEqual(str(self.ce / "mods" / f"{imp.MOD_ID}.old-20261030T234600Z"), plan["movedAside"])

    def test_the_generators_stand_in_on_the_mods_line_is_reported_and_only_then(self) -> None:
        self.ini.write_bytes(b"mods=" + imp.STAND_IN_ID.encode() + b"\n")
        self.assertTrue(self.stage(dry_run=True)["standInAlsoNamed"])
        self.ini.write_bytes(b"mods=other\n")
        self.assertFalse(self.stage(dry_run=True)["standInAlsoNamed"])

    def test_a_folder_that_is_not_there_is_made_as_a_fresh_ce_folder_and_the_launch_line_names_it(self) -> None:
        fresh = self.root / "a fresh 'folder'"
        plan = imp.stage(self.mod, fresh, clock=self.clock, env=self.env)
        self.assertTrue(plan["created"])
        self.assertFalse(plan["intoRealFolder"])
        self.assertEqual(sorted(["ce.ini", "mods"]), sorted(p.name for p in fresh.iterdir()))
        self.assertEqual(b"mods=" + imp.MOD_ID.encode() + b"\n", (fresh / "ce.ini").read_bytes())
        self.assertEqual(imp.check_mod_folder(self.mod), imp.check_mod_folder(fresh / "mods" / imp.MOD_ID))
        self.assertEqual("BEA_USER_DIR='" + str(fresh).replace("'", "'\"'\"'") + "' onslaught-ce -level 888", plan["launch"], "quoted for a shell, whatever the folder's name")
        self.assertFalse(self.real.exists(), "the player's own folder is never made or touched")

    def test_a_dry_run_makes_no_folder_at_all(self) -> None:
        fresh = self.root / "fresh"
        plan = imp.stage(self.mod, fresh, dry_run=True, clock=self.clock, env=self.env)
        self.assertTrue(plan["created"] and plan["dryRun"])
        self.assertFalse(fresh.exists())

    def test_the_players_own_ce_folder_is_refused_however_it_is_named_and_nothing_is_written(self) -> None:
        self.make_real()
        before = sorted(str(p) for p in self.real.rglob("*")), (self.real / "ce.ini").read_bytes()
        link = self._link(self.root / "link-to-real", self.real)
        inside = self.real / "somewhere"
        other = self.root / "other-real"
        other.mkdir()
        cases = {"the folder": (self.real, self.env), "a link to it": (link, self.env), "a folder inside it": (inside, self.env),
                 "the folder BEA_USER_DIR names": (other, self.env | {"BEA_USER_DIR": str(other)})}
        for label, (folder, env) in cases.items():
            with self.subTest(label), self.assertRaisesRegex(imp.ImportFailure, "your own CE folder"):
                imp.stage(self.mod, folder, clock=self.clock, env=env)
            with self.subTest(label + ", dry run"), self.assertRaisesRegex(imp.ImportFailure, "your own CE folder"):
                imp.stage(self.mod, folder, clock=self.clock, env=env, dry_run=True)
        self.assertEqual(before, (sorted(str(p) for p in self.real.rglob("*")), (self.real / "ce.ini").read_bytes()))

    def test_the_players_own_folder_is_used_only_with_the_explicit_flag_and_then_warns_and_has_no_redirect_in_its_launch_line(self) -> None:
        self.make_real()
        plan = imp.stage(self.mod, self.real, into_real=True, clock=self.clock, env=self.env)
        self.assertTrue(plan["intoRealFolder"])
        self.assertEqual("onslaught-ce -level 888", plan["launch"])
        self.assertEqual(b"widescreen=1\nmods=" + imp.MOD_ID.encode() + b"\n", (self.real / "ce.ini").read_bytes())
        self.assertEqual(b"widescreen=1\n", (self.real / "ce.ini.bak-20261030T234530Z").read_bytes())
        self.assertEqual(b"career", (self.real / "savegames" / "Career.bes").read_bytes(), "a career is never touched")
        missing_real = self.root / "xdg2" / "onslaught-ce"
        with self.assertRaisesRegex(imp.ImportFailure, "start CE once"):
            imp.stage(self.mod, missing_real, into_real=True, clock=self.clock, env={"XDG_DATA_HOME": str(self.root / "xdg2")})
        self.assertFalse(missing_real.exists())

    def test_the_default_fresh_folder_is_beside_the_players_own_never_inside_it(self) -> None:
        self.assertEqual(self.root / "xdg" / "onslaught-ce-level888", imp.fresh_user_folder(self.env))
        self.assertFalse(imp.is_real_folder(imp.fresh_user_folder(self.env), self.env))
        self.assertTrue(imp.is_real_folder(self.real, self.env))

    def test_a_plain_file_or_a_link_where_the_folder_goes_and_a_non_file_ce_ini_are_refused(self) -> None:
        plain = self.root / "plain"
        plain.write_bytes(b"x")
        for label, folder in (("a file", plain), ("a link", self._link(self.root / "link", self.ce))):
            with self.subTest(label), self.assertRaisesRegex(imp.ImportFailure, "not a plain folder"):
                imp.stage(self.mod, folder, clock=self.clock, env=self.env)
        self.ini.unlink()
        self.ini.mkdir()
        with self.assertRaisesRegex(imp.ImportFailure, "plain file"):
            self.stage()
        self.assertFalse((self.ce / "mods").exists())

    def _link(self, link: Path, target: Path) -> Path:
        link.symlink_to(target, target_is_directory=True)
        return link

    def test_a_mod_folder_that_is_not_what_mod_json_says_is_refused_before_anything_is_written(self) -> None:
        def change_file(folder: Path) -> None:
            (folder / lvl.ARCHIVE_PATH).write_bytes((folder / lvl.ARCHIVE_PATH).read_bytes() + b"x")

        def remove_file(folder: Path) -> None:
            (folder / lvl.ARCHIVE_PATH).unlink()

        def add_file(folder: Path) -> None:
            (folder / "data" / "extra.bin").write_bytes(b"x")

        def other_id(folder: Path) -> None:
            (folder / "mod.json").write_text((folder / "mod.json").read_text().replace(f'"id": "{imp.MOD_ID}"', '"id": "other-id"', 1))

        def break_json(folder: Path) -> None:
            (folder / "mod.json").write_bytes(b"{")

        def link_file(folder: Path) -> None:
            (folder / "data" / "link.bin").symlink_to(folder / "mod.json")

        for damage in (change_file, remove_file, add_file, other_id, break_json, link_file):
            with self.subTest(damage.__name__):
                copy = self.root / f"copy-{damage.__name__}" / imp.MOD_ID
                shutil.copytree(self.mod, copy)
                damage(copy)
                with self.assertRaises(imp.ImportFailure):
                    imp.stage(copy, self.ce, clock=self.clock, env=self.env)
                self.assertFalse((self.ce / "mods").exists())
                self.assertEqual([self.ini], list(self.ce.iterdir()), "no backup, no staging folder, no new ce.ini")
                self.assertEqual(b"sharp_text=1\nwidescreen=1\n", self.ini.read_bytes())


# ---- the command line --------------------------------------------------------------------------------------------------------
class CommandLineTests(ImportCase):
    def run_tool(self, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
        clean = {k: v for k, v in os.environ.items() if k not in ("BEA_GAME", "BEA_PS2_IMAGE", "BEA_USER_DIR", "XDG_DATA_HOME")} | (env or {})
        return subprocess.run([sys.executable, "-B", str(TOOL), *args], capture_output=True, text=True, env=clean, timeout=120)

    def test_inspect_prints_json_counts_and_exits_zero(self) -> None:
        done = self.run_tool("inspect", str(self.member_path))
        self.assertEqual(0, done.returncode, done.stderr)
        report = json.loads(done.stdout)
        self.assertEqual(22, report["member"]["world"]["things"])
        self.assertEqual("member", report["source"]["from"])

    def test_build_then_stage_through_the_command_line_into_a_fresh_folder(self) -> None:
        out, fresh = self.root / "cli-mods", self.root / "cli-fresh"
        built_ = self.run_tool("build", str(self.member_path), "--game", str(self.game), "--out", str(out), "--ce-min", "0.1.13")
        self.assertEqual(0, built_.returncode, built_.stderr)
        self.assertIn("stage", built_.stdout)
        self.assertNotIn(lvl.VENTURER, built_.stdout + built_.stderr)
        env = {"XDG_DATA_HOME": str(self.root / "cli-xdg")}
        staged = self.run_tool("stage", str(out / imp.MOD_ID), "--user-dir", str(fresh), env=env)
        self.assertEqual(0, staged.returncode, staged.stderr)
        self.assertEqual(f"mods={imp.MOD_ID}\n", (fresh / "ce.ini").read_text())
        self.assertIn(f"BEA_USER_DIR={fresh} onslaught-ce -level 888", staged.stdout)
        self.assertIn("not touched", staged.stdout)
        self.assertFalse((self.root / "cli-xdg").exists(), "the player's own folder is never made")

    def test_the_command_line_stages_into_the_default_fresh_folder_and_refuses_the_players_own_one(self) -> None:
        out = self.root / "cli-mods2"
        self.assertEqual(0, self.run_tool("build", str(self.member_path), "--game", str(self.game), "--out", str(out), "--ce-min", "0.1.13").returncode)
        xdg = self.root / "cli-xdg2"
        env = {"XDG_DATA_HOME": str(xdg)}
        done = self.run_tool("stage", str(out / imp.MOD_ID), env=env)
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertTrue((xdg / imp.FRESH_FOLDER / "mods" / imp.MOD_ID / "mod.json").is_file())
        self.assertFalse((xdg / "onslaught-ce").exists())
        refused = self.run_tool("stage", str(out / imp.MOD_ID), "--user-dir", str(xdg / "onslaught-ce"), env=env)
        self.assertEqual(2, refused.returncode)
        self.assertIn("your own CE folder", refused.stderr)
        self.assertFalse((xdg / "onslaught-ce").exists())
        no_folder = self.run_tool("stage", str(out / imp.MOD_ID), "--into-my-real-folder", env=env)
        self.assertEqual(2, no_folder.returncode)
        self.assertIn("start CE once", no_folder.stderr)

    def test_a_refusal_exits_two_with_one_line_and_no_traceback(self) -> None:
        done = self.run_tool("inspect", str(self.root / "missing"))
        self.assertEqual(2, done.returncode)
        self.assertTrue(done.stderr.startswith("level 888 import:"))
        self.assertNotIn("Traceback", done.stderr)

    def test_the_default_ce_folder_follows_xdg_data_home_then_the_home_folder(self) -> None:
        self.assertEqual(Path("/x/onslaught-ce"), imp.ce_user_folder({"XDG_DATA_HOME": "/x"}))
        with mock.patch.object(Path, "home", return_value=Path("/h")):
            self.assertEqual(Path("/h/.local/share/onslaught-ce"), imp.ce_user_folder({}))


@unittest.skipUnless(os.environ.get("BEA_PS2_IMAGE") and os.environ.get("BEA_GAME"), "the retail gate needs BEA_PS2_IMAGE and BEA_GAME (both read only)")
class RetailGate(unittest.TestCase):
    def test_the_players_own_image_builds_a_mod_the_loader_walk_accepts_with_the_discs_world_inside(self) -> None:
        member, record = imp.read_source(Path(os.environ["BEA_PS2_IMAGE"]), strict_pins=True)
        self.assertEqual([], record["warnings"])
        body = imp.world_body(member)
        with tempfile.TemporaryDirectory() as tmp:
            summary, report = imp.build(Path(os.environ["BEA_PS2_IMAGE"]), Path(os.environ["BEA_GAME"]), Path(tmp), ce_min="0.1.13", strict_pins=True)
            archive = (Path(summary["root"]) / lvl.ARCHIVE_PATH).read_bytes()
        raw = b"".join(enc.inflate(enc.read_members(archive)))
        self.assertIsNone(stage.check_level_archive(raw, lvl.LEVEL))
        self.assertEqual(body, enc.level_worlds(raw)["bodies"]["RLWD"])
        self.assertEqual("ps2-copy", report["world"])
        self.assertEqual(imp.shadow_chunk(member), next(raw[at:at + size] for tag, at, size in enc.chunks(raw) if tag == "SSHD"))
        self.assertEqual("ps2-copy", report["shadows"]["from"])


if __name__ == "__main__":
    unittest.main(verbosity=2 if "-v" in sys.argv else 1, argv=[a for a in sys.argv if a != "-v"])
