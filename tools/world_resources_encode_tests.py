#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks the world body encoder on authored bodies and archives (no game bytes): decode -> encode is the identity,
for every version branch LoadWorld has; edits land where the catalogue decoder reads them; the shadow archive changes
only WDAT's real level; and nothing is written inside a game folder."""
from __future__ import annotations

import contextlib
import io
import json
import math
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import content_catalog_tests as fixtures
import safe_generated_output as safe
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

    def test_malformed_fixed_width_fields_are_refused(self) -> None:
        model = enc.read_world_model(fixtures.world_body())
        for bits in ("", "00", "000000", "0000000000", "00 000000", "zz000000", 1234):
            with self.subTest(bits=bits):
                bad = json.loads(json.dumps(model))
                bad["things"][0]["init"]["position"][0] = {"f32bits": bits}
                with self.assertRaises(enc.EncodeError):
                    enc.write_world_body(bad)
        for field in ("position", "orientation"):
            with self.subTest(field=field):
                bad = json.loads(json.dumps(model))
                bad["things"][0]["init"][field].pop()
                with self.assertRaises(enc.EncodeError):
                    enc.write_world_body(bad)
        bad = json.loads(json.dumps(model))
        bad["occupancyGrids"].pop()
        with self.assertRaises(enc.EncodeError):
            enc.write_world_body(bad)
        bad = json.loads(json.dumps(model))
        bad["scripts"][0]["code"]["symbols"].append(
            {"name": "v", "dataType": 6, "value": [1.0, 2.0], "symbolType": 0, "index": 0, "flag": 0})
        with self.assertRaises(enc.EncodeError):
            enc.write_world_body(bad)


def multi_member_archive(raw: bytes, block: int) -> bytes:
    out = b""
    for at in range(0, len(raw), block):
        member = zlib.compress(raw[at:at + block])
        out += struct.pack("<I", len(member)) + member
    return out


def game_sized_world_archive() -> bytes:
    # The catalogue's generic fixture packs its whole 1.08 MiB archive into one member. Reframe its authored bytes
    # as the PC writer does: at most one MiB inflated per member, without changing the underlying archive stream.
    generic = fixtures.world_archive()
    raw = b"".join(zlib.decompress(m) for m in enc.read_members(generic))
    return multi_member_archive(raw, enc.MAX_INFLATED_MEMBER_BYTES)


class ArchiveTests(unittest.TestCase):
    def test_valid_zlib_member_at_exact_inflated_limits(self) -> None:
        original = b"x" * 1024
        with patch.object(enc, "MAX_INFLATED_MEMBER_BYTES", 1024), \
                patch.object(enc, "MAX_ARCHIVE_INFLATED_BYTES", 1024):
            self.assertEqual([original], enc.inflate([zlib.compress(original)]))

    def test_compressed_bomb_is_bounded_per_member(self) -> None:
        member = zlib.compress(b"x" * 1025)
        with patch.object(enc, "MAX_INFLATED_MEMBER_BYTES", 1024):
            with self.assertRaisesRegex(enc.EncodeError, "inflated archive/member limit"):
                enc.inflate([member])
        actual_cap_bomb = zlib.compress(b"x" * (enc.MAX_INFLATED_MEMBER_BYTES + 1))
        self.assertLess(len(actual_cap_bomb), enc.PACK_BUFFER_SIZE)
        with self.assertRaisesRegex(enc.EncodeError, "inflated archive/member limit"):
            enc.inflate([actual_cap_bomb])

    def test_total_inflated_budget_is_bounded_across_members(self) -> None:
        member = zlib.compress(b"x" * 600)
        with patch.object(enc, "MAX_ARCHIVE_INFLATED_BYTES", 1024):
            with self.assertRaisesRegex(enc.EncodeError, "inflated archive/member limit"):
                enc.inflate([member, member])

    def test_malformed_truncated_and_trailing_zlib_data_are_refused(self) -> None:
        member = zlib.compress(b"example content")
        for invalid in (b"not a zlib stream", member[:-1], member + b"trailing", member + member):
            with self.subTest(invalid=invalid), self.assertRaises(enc.EncodeError):
                enc.inflate([invalid])

    def test_compressed_archive_and_member_count_limits(self) -> None:
        member = zlib.compress(b"example")
        framed = struct.pack("<I", len(member)) + member
        with patch.object(enc, "MAX_ARCHIVE_BYTES", len(framed) - 1):
            with self.assertRaisesRegex(enc.EncodeError, "compressed-byte limit"):
                enc.read_members(framed)
        with patch.object(enc, "MAX_ARCHIVE_MEMBERS", 1):
            with self.assertRaisesRegex(enc.EncodeError, "member-count limit"):
                enc.read_members(framed * 2)
            with self.assertRaisesRegex(enc.EncodeError, "member-count limit"):
                enc.inflate([member, member])
        with patch.object(enc, "PACK_BUFFER_SIZE", len(member) - 1):
            with self.assertRaises(enc.EncodeError):
                enc.read_members(framed)

    def test_file_read_cap_is_enforced_before_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "synthetic.aya"
            archive.write_bytes(b"four")
            with patch.object(enc, "MAX_ARCHIVE_BYTES", 3):
                with self.assertRaisesRegex(enc.EncodeError, "compressed-byte limit"):
                    enc.read_retail(archive)
            self.assertEqual(b"four", archive.read_bytes())

    def test_truncated_chunk_headers_and_short_wdat_are_refused(self) -> None:
        with self.assertRaisesRegex(enc.EncodeError, "truncated chunk header"):
            list(enc.chunks(b"WRES"))

        def chunk(tag: bytes, payload: bytes) -> bytes:
            return tag + struct.pack("<I", len(payload)) + payload

        short_wdat = chunk(b"WDAT", struct.pack("<i", 1))
        fake_following_chunk = chunk(b"RLWD", fixtures.world_body())
        raw = chunk(b"WRES", chunk(b"WRLD", short_wdat + fake_following_chunk))
        with self.assertRaisesRegex(enc.EncodeError, "WDAT is shorter"):
            enc.level_worlds(raw)

    def test_shadow_archive_changes_only_the_real_world_level(self) -> None:
        source = game_sized_world_archive()
        raw = b"".join(enc.inflate(enc.read_members(source)))
        patch_at = enc.level_worlds(raw)["wdatOffset"] + 4
        # Choose a block length that forces the patched 4-byte value across two members while staying below
        # the member-count ceiling.
        straddling = next(n for n in range(512, 65536) if patch_at % n >= n - 3)
        self.assertGreater(patch_at % straddling + 4, straddling)
        for block in (straddling, 65536, 1 << 20):
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

    def test_shadow_archive_accepts_a_single_small_member(self) -> None:
        wdat = fixtures.chunk(b"WDAT", struct.pack("<ii", -1, 200))
        world = fixtures.chunk(b"RLWD", fixtures.world_body())
        raw = fixtures.chunk(b"WRES", fixtures.chunk(b"WRLD", wdat + world))
        packed = multi_member_archive(raw, len(raw))
        self.assertEqual(1, len(enc.read_members(packed)))
        patched = enc.shadow_archive(packed)
        self.assertEqual(enc.NO_LEVEL, enc.level_worlds(b"".join(enc.inflate(enc.read_members(patched))))["realLevel"])

    @unittest.skipIf(os.name == "nt", "fresh-only output needs native Windows support")
    def test_stage_writes_loose_worlds_and_a_shadow_archive_but_never_into_the_game(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game, user = Path(tmp, "game"), Path(tmp, "user")
            (game / "data" / "resources").mkdir(parents=True)
            (game / "data" / "resources" / "200_res_PC.aya").write_bytes(game_sized_world_archive())
            enc.main(["stage", "--game", str(game), "--level", "200", "--user", str(user)])
            self.assertEqual((user / "data" / "worlds" / "world200.wrd").read_bytes(), fixtures.world_body())
            shadow = (user / "data" / "resources" / "200_res_PC.aya").read_bytes()
            self.assertEqual(enc.level_worlds(b"".join(enc.inflate(enc.read_members(shadow))))["realLevel"],
                             enc.NO_LEVEL)
            with self.assertRaises(safe.UnsafeGeneratedOutputError):
                enc.main(["stage", "--game", str(game), "--level", "200", "--user", str(game / "data")])
            self.assertEqual(sorted(p.name for p in (game / "data" / "resources").iterdir()), ["200_res_PC.aya"])


class PublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.game = self.root / "game"
        self.resources = self.game / "data" / "resources"
        self.resources.mkdir(parents=True)
        self.archive = self.resources / "200_res_PC.aya"
        self.original = game_sized_world_archive()
        self.archive.write_bytes(self.original)
        self.user = self.root / "user"
        self.model = self.root / "model.json"
        self.model.write_text(json.dumps(enc.read_world_model(fixtures.world_body())), encoding="utf-8")

    def stage(self) -> int:
        return enc.main(["stage", "--game", str(self.game), "--level", "200", "--user", str(self.user)])

    def test_game_alias_is_resolved_before_archive_selection_and_publication(self) -> None:
        alias = self.root / "game-alias"
        try:
            alias.symlink_to(self.game, target_is_directory=True)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"directory symlinks unavailable: {error}")
        with patch.object(enc, "level_archives", wraps=enc.level_archives) as lookup, \
                patch.object(enc, "publish_fresh", wraps=enc.publish_fresh) as publish, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, enc.main(["extract", "--game", str(alias), "--level", "200", "--out", str(self.user)]))
        self.assertEqual(lookup.call_args.args[0], self.game)
        self.assertEqual(publish.call_args.args[1], self.game)
        self.assertEqual((self.user / "world200.wrd").read_bytes(), fixtures.world_body())
        self.assertEqual(self.archive.read_bytes(), self.original)

    def test_selected_game_resolves_parent_after_a_link(self) -> None:
        child = self.game / "child"
        child.mkdir()
        alias = self.root / "child-alias"
        try:
            alias.symlink_to(child, target_is_directory=True)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"directory symlinks unavailable: {error}")
        self.assertEqual(enc.selected_game_root(alias / ".."), self.game)

    def test_writing_commands_refuse_links_in_the_selected_game_tree(self) -> None:
        for location in ("resources", "nested"):
            with self.subTest(location=location):
                game = self.root / f"game-{location}"
                data = game / "data"
                data.mkdir(parents=True)
                (game / "BEA.exe").write_bytes(b"authored game marker")
                external = self.root / f"external-{location}"
                external.mkdir()
                if location == "resources":
                    link, resources = data / "resources", external
                else:
                    resources = data / "resources"
                    resources.mkdir()
                    (data / "other").mkdir()
                    link = data / "other" / "linked"
                try:
                    link.symlink_to(external, target_is_directory=True)
                except (NotImplementedError, OSError) as error:
                    self.skipTest(f"directory symlinks unavailable: {error}")
                archive = resources / "200_res_PC.aya"
                archive.write_bytes(self.original)
                # Verification remains read-only and can inspect a linked selected input.
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(0, enc.main(["verify", "--game", str(game)]))
                before = sorted(path.name for path in external.iterdir())
                cases = (
                    ["extract", "--game", str(game), "--level", "200", "--out", str(external)],
                    ["stage", "--game", str(game), "--level", "200", "--user", str(external)],
                    ["encode", "--game", str(game), str(self.model), str(external / "world.wrd")],
                )
                for args in cases:
                    with self.subTest(command=args[0]):
                        with self.assertRaisesRegex(safe.UnsafeGeneratedOutputError, "link or reparse point"):
                            enc.main(args)
                        self.assertEqual(before, sorted(path.name for path in external.iterdir()))
                        self.assertEqual(self.original, archive.read_bytes())
                self.assertEqual(before, sorted(path.name for path in link.iterdir()))

    def test_dangling_game_link_is_refused_even_for_a_separate_output(self) -> None:
        link = self.game / "data" / "dangling"
        try:
            link.symlink_to(self.root / "missing")
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"symlinks unavailable: {error}")
        destination = self.root / "safe-output" / "world.wrd"
        with self.assertRaisesRegex(safe.UnsafeGeneratedOutputError, "link or reparse point"):
            enc.main(["encode", "--game", str(self.game), str(self.model), str(destination)])
        self.assertFalse(destination.parent.exists())
        self.assertEqual(self.original, self.archive.read_bytes())

    def test_cli_extract_refuses_a_linked_game_resources_directory(self) -> None:
        game = self.root / "cli-game"
        (game / "data").mkdir(parents=True)
        external = self.root / "cli-resources"
        external.mkdir()
        link = game / "data" / "resources"
        try:
            link.symlink_to(external, target_is_directory=True)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"directory symlinks unavailable: {error}")
        archive = external / "200_res_PC.aya"
        archive.write_bytes(self.original)
        result = subprocess.run(
            [sys.executable, str(Path(enc.__file__)), "extract", "--game", str(game), "--level", "200", "--out", str(external)],
            capture_output=True, text=True, timeout=20, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("link or reparse point", result.stderr)
        self.assertEqual(["200_res_PC.aya"], sorted(path.name for path in external.iterdir()))
        self.assertEqual(self.original, archive.read_bytes())

    def test_uninspectable_or_over_limit_game_tree_refuses_publication(self) -> None:
        destination = self.root / "safe-output" / "world.wrd"
        command = ["encode", "--game", str(self.game), str(self.model), str(destination)]
        with patch.object(enc, "MAX_GAME_TREE_ENTRIES", 1):
            with self.assertRaisesRegex(safe.UnsafeGeneratedOutputError, "entry limit"):
                enc.main(command)
        with patch.object(enc, "MAX_GAME_TREE_DEPTH", 0):
            with self.assertRaisesRegex(safe.UnsafeGeneratedOutputError, "depth limit"):
                enc.main(command)
        with patch.object(enc.os, "scandir", side_effect=PermissionError("authored denial")):
            with self.assertRaisesRegex(safe.UnsafeGeneratedOutputError, "cannot be inspected"):
                enc.main(command)
        self.assertFalse(destination.parent.exists())
        self.assertEqual(self.original, self.archive.read_bytes())

    def test_reparse_metadata_is_refused_without_following_it(self) -> None:
        class FakeEntry:
            path = "authored-reparse-point"

            def stat(self, *, follow_symlinks):
                self_assert.assertFalse(follow_symlinks)
                return SimpleNamespace(st_mode=enc.stat.S_IFDIR, st_file_attributes=0x400)

        self_assert = self
        with patch.object(enc.os, "scandir", return_value=contextlib.nullcontext([FakeEntry()])):
            with self.assertRaisesRegex(safe.UnsafeGeneratedOutputError, "link or reparse point"):
                enc.refuse_internal_game_links(self.game)

    def test_outputs_with_parent_components_are_refused_before_read_or_write(self) -> None:
        output = self.user / ".." / "candidate"
        cases = (
            ["extract", "--game", str(self.game), "--level", "200", "--out", str(output)],
            ["encode", "--game", str(self.game), str(self.model), str(output / "world.wrd")],
            ["stage", "--game", str(self.game), "--level", "200", "--user", str(output)],
        )
        for args in cases:
            with self.subTest(command=args[0]), \
                    patch.object(enc, "level_archives", wraps=enc.level_archives) as lookup:
                with self.assertRaisesRegex(safe.UnsafeGeneratedOutputError, "parent components"):
                    enc.main(args)
                lookup.assert_not_called()
        self.assertFalse(self.user.exists())
        self.assertFalse((self.root / "candidate").exists())
        self.assertEqual(self.archive.read_bytes(), self.original)

    def test_missing_game_and_empty_paths_are_refused_without_output(self) -> None:
        with self.assertRaisesRegex(enc.EncodeError, "cannot be resolved"):
            enc.main(["encode", "--game", str(self.root / "missing"), str(self.model), str(self.user / "world.wrd")])
        cases = (
            ["encode", "--game", "", str(self.model), str(self.user / "world.wrd")],
            ["extract", "--game", str(self.game), "--level", "200", "--out", ""],
            ["stage", "--game", str(self.game), "--level", "200", "--user", ""],
        )
        for args in cases:
            with self.subTest(command=args[0]), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    enc.main(args)
                self.assertEqual(error.exception.code, 2)
        with patch.dict(os.environ, {"BEA_GAME": ""}), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                enc.main(["encode", str(self.model), str(self.user / "world.wrd")])
            self.assertEqual(error.exception.code, 2)
        self.assertFalse(self.user.exists())
        self.assertEqual(self.archive.read_bytes(), self.original)

    def test_stage_rejects_resources_directory_symlink_into_game(self) -> None:
        (self.user / "data").mkdir(parents=True)
        try:
            (self.user / "data" / "resources").symlink_to(self.resources, target_is_directory=True)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"directory symlinks unavailable: {error}")
        with self.assertRaises(safe.UnsafeGeneratedOutputError):
            self.stage()
        self.assertEqual(self.original, self.archive.read_bytes())
        self.assertFalse((self.user / "data" / "worlds" / "world200.wrd").exists())

    def test_stage_wont_replace_an_existing_world(self) -> None:
        world = self.user / "data" / "worlds" / "world200.wrd"
        world.parent.mkdir(parents=True)
        world.write_bytes(b"a pre-existing user world")
        with self.assertRaises(safe.UnsafeGeneratedOutputError):
            self.stage()
        self.assertEqual(b"a pre-existing user world", world.read_bytes())
        self.assertEqual(self.original, self.archive.read_bytes())
        self.assertFalse((self.user / "data" / "resources" / "200_res_PC.aya").exists())

    def test_encode_rejects_game_destination_and_existing_output(self) -> None:
        with self.assertRaises(safe.UnsafeGeneratedOutputError):
            enc.main(["encode", "--game", str(self.game), str(self.model), str(self.archive)])
        self.assertEqual(self.original, self.archive.read_bytes())
        self.user.mkdir()
        target = self.user / "world.wrd"
        target.write_bytes(b"a prior user world")
        with self.assertRaises(safe.UnsafeGeneratedOutputError):
            enc.main(["encode", "--game", str(self.game), str(self.model), str(target)])
        self.assertEqual(b"a prior user world", target.read_bytes())

    def test_extract_refuses_symlinked_destination_without_creating_other_output(self) -> None:
        out = self.root / "output"
        out.mkdir()
        try:
            (out / "world200.wrd").symlink_to(self.archive)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"file symlinks unavailable: {error}")
        with self.assertRaises(safe.UnsafeGeneratedOutputError):
            enc.main(["extract", "--game", str(self.game), "--level", "200", "--out", str(out)])
        self.assertEqual(self.original, self.archive.read_bytes())
        self.assertFalse((out / "world200.json").exists())

    def test_stage_rejects_hardlinked_destination(self) -> None:
        dest = self.user / "data" / "resources" / self.archive.name
        dest.parent.mkdir(parents=True)
        try:
            os.link(self.archive, dest)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"hardlinks unavailable: {error}")
        with self.assertRaises(safe.UnsafeGeneratedOutputError):
            self.stage()
        self.assertEqual(self.original, self.archive.read_bytes())
        self.assertEqual(self.original, dest.read_bytes())
        self.assertFalse((self.user / "data" / "worlds" / "world200.wrd").exists())

    @unittest.skipIf(os.name == "nt", "fresh-only output needs native Windows support")
    def test_extract_is_exact_and_refuses_a_second_write(self) -> None:
        out = self.root / "output"
        args = ["extract", "--game", str(self.game), "--level", "200", "--out", str(out)]
        self.assertEqual(0, enc.main(args))
        body = (out / "world200.wrd").read_bytes()
        model = (out / "world200.json").read_bytes()
        self.assertEqual(fixtures.world_body(), body)
        with self.assertRaises(safe.UnsafeGeneratedOutputError):
            enc.main(args)
        self.assertEqual(body, (out / "world200.wrd").read_bytes())
        self.assertEqual(model, (out / "world200.json").read_bytes())
        self.assertEqual(self.original, self.archive.read_bytes())

    def test_invalid_model_cannot_publish(self) -> None:
        model = json.loads(self.model.read_text(encoding="utf-8"))
        model["things"][0]["init"]["position"][0] = {"f32bits": "00"}
        self.model.write_text(json.dumps(model), encoding="utf-8")
        dest = self.user / "world.wrd"
        with self.assertRaises(enc.EncodeError):
            enc.main(["encode", "--game", str(self.game), str(self.model), str(dest)])
        self.assertFalse(dest.exists())
        self.assertEqual(self.original, self.archive.read_bytes())

    @unittest.skipIf(os.name == "nt", "POSIX descriptor-relative race control")
    def test_output_created_after_preflight_is_not_replaced(self) -> None:
        dest = self.user / "world.wrd"
        rename_no_replace = safe._posix_rename_no_replace

        def race(fd, source, target):
            descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=fd)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(b"concurrent user file")
            return rename_no_replace(fd, source, target)

        with patch.object(safe, "_posix_rename_no_replace", side_effect=race):
            with self.assertRaises(safe.UnsafeGeneratedOutputError):
                enc.main(["encode", "--game", str(self.game), str(self.model), str(dest)])
        self.assertEqual(b"concurrent user file", dest.read_bytes())
        self.assertEqual(self.original, self.archive.read_bytes())

    @unittest.skipUnless(os.name == "nt", "native Windows fail-closed control")
    def test_windows_fresh_publication_is_refused_until_supported(self) -> None:
        dest = self.user / "world.wrd"
        with self.assertRaises(safe.UnsafeGeneratedOutputError):
            enc.main(["encode", "--game", str(self.game), str(self.model), str(dest)])
        self.assertFalse(dest.exists())
        self.assertEqual(self.original, self.archive.read_bytes())


if __name__ == "__main__":
    unittest.main()
