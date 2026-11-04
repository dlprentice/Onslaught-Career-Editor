#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Authored museum content controls; no installed game data or runtime claims."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import ce_museum_stage as museum
import content_catalog_tests as fixtures
import world_resources_encode as world
import world_resources_decode as schema


def fixture():
    model = world.read_world_model(fixtures.world_body())
    init = museum.authored_init("authored.original.start", [100.0, 100.0, 0.0], [0.0, 0.0, 0.0], start=True)
    init["script"] = "original-script-must-not-run"
    init["spawnScript"] = "original-spawn-must-not-run"
    start_oid = next(oid for oid, kind in schema.OID_NAMES.items() if kind == "start")
    model["things"].append({"oid": start_oid, "kind": "start", "init": init})
    models = {"BSWD": copy.deepcopy(model), "RLWD": model}
    bodies = {tag: world.write_world_body(m) for tag, m in models.items()}
    inner = museum.chunk("WDAT", struct.pack("<ii", 100, 100))
    inner += b"".join(museum.chunk(tag, body) for tag, body in bodies.items())
    raw = museum.chunk("LVLR", struct.pack("<i", 100))
    raw += museum.chunk("TARG", b"TEST") + museum.chunk("TEXT", b"authored-resource-data")
    raw += museum.chunk("WRES", museum.chunk("WRLD", inner))
    archive = museum.pack_archive(raw)

    def source(index):
        return {"world": "RLWD", "ordinal": index, "sha256": museum.record_digest(model["things"][index])}

    project = {"format": museum.FORMAT, "id": "authored-room", "name": "Authored exhibition",
               "targetLevel": 889, "carrier": {"level": 100, "sha256": museum.digest(archive)},
               "start": {"source": source(len(model["things"]) - 1), "offset": [0, 0, 0], "orientation": [0, 0, 0]},
               "exhibits": [{"id": "first", "source": source(4), "offset": [12, 0, 0], "orientation": [0, 0, 0]},
                            {"id": "second", "source": source(4), "offset": [0, 12, 0], "orientation": [0, 0, 1]}]}
    return project, archive, models


def decoded(archive):
    raw = b"".join(world.inflate(world.read_members(archive)))
    return {tag: world.read_world_model(body) for tag, body in world.level_worlds(raw)["bodies"].items()}


class MuseumContentTests(unittest.TestCase):
    def test_only_authored_start_and_exhibits_survive(self):
        project, source, _ = fixture()
        artifact, receipt = museum.build(project, source)
        models = decoded(artifact)
        self.assertEqual(models["BSWD"]["things"], [])
        self.assertEqual([t["kind"] for t in models["RLWD"]["things"]], ["start", "feature", "feature"])
        self.assertEqual([t["init"]["name"] for t in models["RLWD"]["things"]],
                         ["ce.museum.visitor", "ce.museum.first", "ce.museum.second"])
        self.assertEqual(models["RLWD"]["things"][1]["init"]["position"], [112.0, 100.0, 0.0])
        for model in models.values():
            self.assertEqual(model["baseLevel"], project["targetLevel"])
            for field in ("scripts", "namedMeshes", "treeGroups", "treeTypes", "waypointPaths"):
                self.assertEqual(model[field], [])
            self.assertEqual(model["influenceMap"]["nodes"], 0)
            self.assertEqual(model["influenceMap"]["links"], 0)
            self.assertTrue(all(not grid["data"] for grid in model["occupancyGrids"]))
            for thing in model["things"]:
                self.assertEqual(thing["init"]["script"], "")
                self.assertEqual(thing["init"]["spawnScript"], "")
                self.assertEqual(thing["init"]["attachScriptsToUnits"], 0)
        self.assertEqual(receipt["sourceScriptsCarried"], 0)
        self.assertEqual(receipt["sourceActorsCarried"], 0)

    def test_exact_resource_bytes_preserved_and_world_bytes_replaced(self):
        project, source, _ = fixture()
        artifact, _ = museum.build(project, source)
        def sections(blob):
            raw = b"".join(world.inflate(world.read_members(blob)))
            return {tag: raw[at:at + size] for tag, at, size in world.chunks(raw)}
        before, after = sections(source), sections(artifact)
        self.assertEqual(before["TEXT"], after["TEXT"])
        self.assertEqual(before["TARG"], after["TARG"])
        self.assertNotEqual(before["WRES"], after["WRES"])
        self.assertNotEqual(before["LVLR"], after["LVLR"])

    def test_repeated_build_is_byte_identical(self):
        project, source, _ = fixture()
        self.assertEqual(museum.build(project, source), museum.build(project, source))

    def test_output_audit_catches_carried_source_behaviour(self):
        project, source, models = fixture()
        baseline = museum.make_worlds(project, models)
        for mutation in ("actor", "script", "attachment", "navigation", "automatic-mesh", "progression"):
            with self.subTest(mutation=mutation):
                wrong = world.read_world_model(baseline["RLWD"])
                if mutation == "actor": wrong["things"].append(models["RLWD"]["things"][0])
                elif mutation == "script": wrong["scripts"] = models["RLWD"]["scripts"]
                elif mutation == "attachment": wrong["things"][0]["init"]["script"] = "authored-bad-script"
                elif mutation == "navigation": wrong["waypointPaths"] = [{"name": "bad-path", "slots": []}]
                elif mutation == "automatic-mesh": wrong["namedMeshes"] = ["bad-auto-spawn"]
                else: wrong["baseLevel"] = 100
                changed = {**baseline, "RLWD": world.write_world_body(wrong)}
                with patch.object(museum, "make_worlds", return_value=changed):
                    with self.assertRaises(museum.MuseumError): museum.build(project, source)

    def test_binding_drift_or_wrong_actor_kind_is_refused(self):
        project, source, models = fixture()
        for field in ("carrier", "record", "kind", "missing"):
            with self.subTest(field=field):
                edit = copy.deepcopy(project)
                if field == "carrier": edit["carrier"]["sha256"] = "0" * 64
                elif field == "record": edit["exhibits"][0]["source"]["sha256"] = "0" * 64
                elif field == "kind":
                    edit["exhibits"][0]["source"]["ordinal"] = 0
                    edit["exhibits"][0]["source"]["sha256"] = museum.record_digest(models["RLWD"]["things"][0])
                else: edit["exhibits"][0]["source"]["ordinal"] = 999
                with self.assertRaises(museum.MuseumError): museum.build(edit, source)

    def test_unknown_fields_non_finite_numbers_and_duplicate_ids_are_refused(self):
        project, _, _ = fixture()
        edits = []
        edit = copy.deepcopy(project); edit["runScript"] = "anything"; edits.append(edit)
        edit = copy.deepcopy(project); edit["targetLevel"] = 100; edits.append(edit)
        edit = copy.deepcopy(project); edit["start"]["offset"][0] = float("nan"); edits.append(edit)
        edit = copy.deepcopy(project); edit["start"]["offset"][0] = True; edits.append(edit)
        edit = copy.deepcopy(project); edit["exhibits"][1]["id"] = "first"; edits.append(edit)
        edit = copy.deepcopy(project); edit["exhibits"][1]["id"] = "../outside"; edits.append(edit)
        for edit in edits:
            with self.subTest(edit=edits.index(edit)):
                with self.assertRaises(museum.MuseumError): museum.validate(edit)

    def test_unsupported_carrier_section_is_not_copied(self):
        project, source, _ = fixture()
        raw = b"".join(world.inflate(world.read_members(source))) + museum.chunk("CODE", b"not-supported")
        changed = museum.pack_archive(raw); project["carrier"]["sha256"] = museum.digest(changed)
        with self.assertRaises(museum.MuseumError): museum.build(project, changed)

    def test_multi_member_pack_round_trip(self):
        raw = b"authored" * (world.MAX_INFLATED_MEMBER_BYTES // 4)
        packed = museum.pack_archive(raw)
        self.assertGreater(len(world.read_members(packed)), 1)
        self.assertEqual(b"".join(world.inflate(world.read_members(packed))), raw)

    def test_staging_preserves_input_and_refuses_replacement(self):
        project, source, _ = fixture()
        with tempfile.TemporaryDirectory(prefix="museum-authored-") as temporary:
            root = Path(temporary); game = root / "game"; resources = game / "data/resources"; resources.mkdir(parents=True)
            original = resources / "100_res_PC.aya"; original.write_bytes(source)
            result = museum.stage(project, game, root / "out")
            output = Path(result["root"])
            manifest = json.loads((output / "mod.json").read_text())
            entry = manifest["files"][0]; archived = (output / entry["path"]).read_bytes()
            self.assertEqual(museum.digest(archived), entry["sha256"])
            self.assertEqual(len(archived), entry["size"])
            self.assertEqual(original.read_bytes(), source)
            with self.assertRaises(museum.MuseumError): museum.stage(project, game, root / "out")
            self.assertEqual((output / entry["path"]).read_bytes(), archived)
            with self.assertRaises(museum.MuseumError): museum.stage(project, game, game / "mods")
            self.assertEqual(original.read_bytes(), source)

    def test_existing_target_and_symlinked_input_are_refused(self):
        project, source, _ = fixture()
        with tempfile.TemporaryDirectory(prefix="museum-authored-") as temporary:
            root = Path(temporary); resources = root / "game/data/resources"; resources.mkdir(parents=True)
            original = resources / "100_res_PC.aya"; original.write_bytes(source)
            (resources / "889_res_PC.aya").write_bytes(source)
            with self.assertRaises(museum.MuseumError): museum.stage(project, root / "game", root / "out")
            linked = root / "project.json"; real = root / "real.json"; real.write_text(json.dumps(project)); linked.symlink_to(real)
            with self.assertRaises((OSError, ValueError)): museum.load_project(linked)

    def test_duplicate_json_keys_are_refused(self):
        with tempfile.TemporaryDirectory(prefix="museum-authored-") as temporary:
            project = Path(temporary) / "project.json"; project.write_text('{"id":"one","id":"two"}')
            with self.assertRaises(museum.MuseumError): museum.load_project(project)


if __name__ == "__main__":
    unittest.main()
