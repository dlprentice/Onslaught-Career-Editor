#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks the world body encoder on authored bodies and archives (no game bytes): decode -> encode is the identity,
for every version branch LoadWorld has; edits land where the catalogue decoder reads them; the shadow archive changes
only WDAT's real level; and nothing is written inside a game folder."""
from __future__ import annotations

import json
import math
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

import content_catalog_tests as fixtures
import world_resources_decode as worlddec
import world_resources_encode as enc

PHYSICS = {"units": {"Tank"}, "features": {"Rock"}, "hazards": set(), "squadless": set()}


def legacy_body(version: int) -> bytes:
    """The authored body rewritten at an older version: the fields LoadWorld reads only for that version."""
    model = enc.read_world_model(fixtures.world_body())
    model["version"] = version
    for t in model["things"]:
        if version <= 45:
            t["init"].pop("attachScriptsToUnits", None)
    if 45 <= version < 48:
        model["legacyTimings"] = [1, 2, 3, 0.5, 0.25]
    if version < 47:
        model.pop("occupancyGrids", None)
    else:
        model["occupancyGrids"] = [{"version": 1, "data": enc.blob(bytes(range(256)) * 128)},
                                   {"version": 2, "data": enc.blob(b"\x07" * 0x2000)}, {"version": 0, "data": ""}]
    if 47 <= version < 50:
        model["legacyGridWords"] = [5, 4, 3, 2, 1]
    if version < 49:
        model.pop("levelStartTime", None)
    return enc.write_world_body(model)


class RoundTripTests(unittest.TestCase):
    def test_authored_body_round_trips_through_json(self) -> None:
        body = fixtures.world_body()
        model = json.loads(json.dumps(enc.read_world_model(body)))
        self.assertEqual(enc.write_world_body(model), body)

    def test_every_version_branch_round_trips_and_the_catalogue_decoder_reads_it(self) -> None:
        for version in range(43, 51):
            with self.subTest(version=version):
                body = legacy_body(version)
                self.assertEqual(enc.write_world_body(enc.read_world_model(body)), body)
                decoded = worlddec.parse_world_body(body, PHYSICS, base=False)
                self.assertEqual(decoded["version"], version)
                self.assertEqual(len(decoded["things"]), 5)

    def test_non_finite_floats_and_bool_words_keep_their_bits(self) -> None:
        model = enc.read_world_model(fixtures.world_body())
        model["timings"]["pan"] = {"f32bits": "0100c07f"}  # a signalling NaN payload
        model["scripts"][0]["code"]["symbols"].append(
            {"name": "b", "dataType": 4, "value": 7, "symbolType": 0, "index": 0, "flag": 0})
        body = enc.write_world_body(model)
        again = enc.read_world_model(body)
        self.assertEqual(again["timings"]["pan"], {"f32bits": "0100c07f"})
        self.assertEqual(again["scripts"][0]["code"]["symbols"][-1]["value"], 7)
        self.assertEqual(enc.write_world_body(again), body)

    def test_unread_bytes_and_unknown_things_are_refused(self) -> None:
        with self.assertRaises(worlddec.DecodeError):
            enc.read_world_model(fixtures.world_body() + b"\0")
        broken = fixtures.world_body().replace(struct.pack("<i", 18), struct.pack("<i", 99), 1)
        with self.assertRaises(worlddec.DecodeError):
            enc.read_world_model(broken)


class EditTests(unittest.TestCase):
    def test_moving_a_unit_changes_only_its_position(self) -> None:
        body = fixtures.world_body()
        model = enc.read_world_model(body)
        model["things"][0]["init"]["position"] = [12.5, -40.0, 3.0]
        edited = enc.write_world_body(model)
        self.assertEqual(len(edited), len(body))
        at = worlddec.parse_world_body(body, PHYSICS, base=False)["things"][0]["offset"] + 4  # past the object id
        changed = {i for i, (a, b) in enumerate(zip(edited, body)) if a != b}
        self.assertTrue(changed and changed <= set(range(at, at + 12)))
        decoded = worlddec.parse_world_body(edited, PHYSICS, base=False)
        self.assertEqual(decoded["things"][0]["init"]["position"], [12.5, -40.0, 3.0])

    def test_an_appended_unit_takes_the_next_slot_and_leaves_the_paths_alone(self) -> None:
        model = enc.read_world_model(fixtures.world_body())
        before = worlddec.parse_world_body(enc.write_world_body(model), PHYSICS, base=False)
        new = json.loads(json.dumps(model["things"][0]))
        new["init"]["name"] = "Tank 2"
        new["init"]["position"] = [30.0, 30.0, 0.0]
        model["things"].append(new)
        after = worlddec.parse_world_body(enc.write_world_body(model), PHYSICS, base=False)
        self.assertEqual(after["slotsCounted"], before["slotsCounted"] + 1)
        self.assertEqual(after["things"][-1]["slot"], before["slotsCounted"])
        self.assertEqual(after["waypointPaths"][0]["members"], before["waypointPaths"][0]["members"])

    def test_values_the_format_cannot_hold_are_refused(self) -> None:
        model = enc.read_world_model(fixtures.world_body())
        bad = json.loads(json.dumps(model))
        bad["things"][0]["init"]["position"][0] = 0.1  # not a float32 value
        with self.assertRaises(enc.EncodeError):
            enc.write_world_body(bad)
        bad = json.loads(json.dumps(model))
        bad["things"][0]["definition"] = "x" * 128  # a signed-char length
        with self.assertRaises(enc.EncodeError):
            enc.write_world_body(bad)
        bad = json.loads(json.dumps(model))
        bad["format"] = "other"
        with self.assertRaises(enc.EncodeError):
            enc.write_world_body(bad)
        bad = json.loads(json.dumps(model))
        bad["things"] = bad["things"] * 201
        with self.assertRaises(enc.EncodeError):
            enc.write_world_body(bad)
        self.assertTrue(math.isfinite(struct.unpack("<f", enc.f32_out(-0.0))[0]))


def multi_member_archive(raw: bytes, block: int) -> bytes:
    out = b""
    for at in range(0, len(raw), block):
        member = zlib.compress(raw[at:at + block])
        out += struct.pack("<I", len(member)) + member
    return out


class ArchiveTests(unittest.TestCase):
    def test_shadow_archive_changes_only_the_real_world_level(self) -> None:
        source = fixtures.world_archive()
        raw = b"".join(enc.inflate(enc.read_members(source)))
        for block in (len(raw), 97, 1 << 20):  # one member, many small members (the patch may straddle two)
            with self.subTest(block=block):
                packed = multi_member_archive(raw, block)
                shadow = enc.shadow_archive(packed)
                before, after = enc.read_members(packed), enc.read_members(shadow)
                self.assertEqual([len(b) for b in enc.inflate(before)], [len(b) for b in enc.inflate(after)])
                new_raw = b"".join(enc.inflate(after))
                worlds = enc.level_worlds(new_raw)
                self.assertEqual((worlds["baseLevel"], worlds["realLevel"]), (-1, enc.NO_LEVEL))
                self.assertEqual(sum(a != b for a, b in zip(raw, new_raw)), 2)  # 200 -> 9999 in one int32
                changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
                self.assertLessEqual(len(changed), 2)

    def test_stage_writes_loose_worlds_and_a_shadow_archive_but_never_into_the_game(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game, user = Path(tmp, "game"), Path(tmp, "user")
            (game / "data" / "resources").mkdir(parents=True)
            (game / "data" / "resources" / "200_res_PC.aya").write_bytes(fixtures.world_archive())
            enc.main(["stage", "--game", str(game), "--level", "200", "--user", str(user)])
            self.assertEqual((user / "data" / "worlds" / "world200.wrd").read_bytes(), fixtures.world_body())
            shadow = (user / "data" / "resources" / "200_res_PC.aya").read_bytes()
            self.assertEqual(enc.level_worlds(b"".join(enc.inflate(enc.read_members(shadow))))["realLevel"],
                             enc.NO_LEVEL)
            with self.assertRaises(SystemExit):
                enc.main(["stage", "--game", str(game), "--level", "200", "--user", str(game / "data")])
            self.assertEqual(sorted(p.name for p in (game / "data" / "resources").iterdir()), ["200_res_PC.aya"])


if __name__ == "__main__":
    unittest.main()
