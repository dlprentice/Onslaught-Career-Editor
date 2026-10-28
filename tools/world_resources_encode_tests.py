#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks the world body encoder on authored bodies and archives (no game bytes): decode -> encode is the identity,
for every version branch LoadWorld has; edits land where the catalogue decoder reads them; the shadow archive changes
only WDAT's real level; and nothing is written inside a game folder."""
from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import json
import math
import os
import shutil
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



class StreamOutputTests(unittest.TestCase):
    """Actual CLI controls use only authored game data and captured stdout."""

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

    def cli(self, *args: str):
        return subprocess.run([sys.executable, str(Path(enc.__file__)), *args], capture_output=True, timeout=30,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

    def assert_game_unchanged(self):
        self.assertEqual(self.original, self.archive.read_bytes())
        self.assertEqual(["200_res_PC.aya"], sorted(p.name for p in self.resources.iterdir()))

    def assert_bundle_entry(self, bundle, name, expected):
        entry = bundle["files"][name]
        self.assertEqual(expected, base64.b64decode(entry["dataBase64"], validate=True))
        self.assertEqual(len(expected), entry["bytes"])
        self.assertEqual(hashlib.sha256(expected).hexdigest(), entry["sha256"])

    def test_extract_stdout_contains_exact_model_and_body(self) -> None:
        result = self.cli("extract", "--game", str(self.game), "--level", "200", "--stdout")
        self.assertEqual(0, result.returncode, result.stderr)
        bundle = json.loads(result.stdout)
        self.assertEqual(("onslaught.world-bundle.v1", "extract", 200),
                         (bundle["format"], bundle["purpose"], bundle["level"]))
        body = fixtures.world_body()
        self.assert_bundle_entry(bundle, "world200.wrd", body)
        model_bytes = base64.b64decode(bundle["files"]["world200.json"]["dataBase64"], validate=True)
        self.assert_bundle_entry(bundle, "world200.json", model_bytes)
        self.assertEqual(enc.read_world_model(body), json.loads(model_bytes))
        self.assertFalse(self.user.exists())
        self.assert_game_unchanged()

    def test_encode_stdout_is_exact_raw_bytes_without_messages(self) -> None:
        result = self.cli("encode", "--game", str(self.game), str(self.model), "--stdout")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(fixtures.world_body(), result.stdout)
        self.assertEqual(b"", result.stderr)
        self.assertFalse(self.user.exists())
        self.assert_game_unchanged()

    def test_short_binary_stream_is_reported_as_incomplete(self) -> None:
        class ShortStream(io.BytesIO):
            def write(self, data):
                super().write(data[:7])
                return 7

        stream = ShortStream()
        with patch.object(enc.sys, "stdout", SimpleNamespace(buffer=stream)):
            with self.assertRaisesRegex(enc.EncodeError, "only part"):
                enc.main(["encode", "--game", str(self.game), str(self.model), "--stdout"])
        self.assertEqual(fixtures.world_body()[:7], stream.getvalue())
        self.assert_game_unchanged()

    def test_stage_stdout_is_a_bundle_and_stages_nothing(self) -> None:
        result = self.cli("stage", "--game", str(self.game), "--level", "200", "--stdout")
        self.assertEqual(0, result.returncode, result.stderr)
        bundle = json.loads(result.stdout)
        self.assertEqual(("onslaught.world-bundle.v1", "stage", 200),
                         (bundle["format"], bundle["purpose"], bundle["level"]))
        self.assertEqual(hashlib.sha256(self.original).hexdigest(), bundle["archiveSha256"])
        self.assert_bundle_entry(bundle, "data/worlds/world200.wrd", fixtures.world_body())
        shadow = base64.b64decode(bundle["files"]["data/resources/200_res_PC.aya"]["dataBase64"], validate=True)
        self.assert_bundle_entry(bundle, "data/resources/200_res_PC.aya", shadow)
        self.assertEqual(enc.NO_LEVEL, enc.level_worlds(b"".join(enc.inflate(enc.read_members(shadow))))["realLevel"])
        self.assertFalse(self.user.exists())
        self.assert_game_unchanged()

    def test_stage_stdout_includes_requested_edited_world(self) -> None:
        model = json.loads(self.model.read_text(encoding="utf-8"))
        model["things"][0]["init"]["position"][0] = 12.5
        self.model.write_text(json.dumps(model), encoding="utf-8")
        result = self.cli("stage", "--game", str(self.game), "--level", "200", "--stdout", "--world", str(self.model))
        self.assertEqual(0, result.returncode, result.stderr)
        bundle = json.loads(result.stdout)
        self.assert_bundle_entry(bundle, "data/worlds/world200.wrd", enc.write_world_body(model))
        self.assertFalse(bundle["files"]["data/worlds/world200.wrd"]["identicalToArchive"])
        self.assertFalse(self.user.exists())
        self.assert_game_unchanged()

    def test_legacy_paths_refuse_before_any_input_read(self) -> None:
        cases = (
            ["extract", "--game", str(self.game), "--level", "200", "--out", str(self.user)],
            ["stage", "--game", str(self.game), "--level", "200", "--user", str(self.user)],
            ["encode", "--game", str(self.game), str(self.model), str(self.user / "world.wrd")],
        )
        with patch.object(enc, "selected_game_root", side_effect=AssertionError("unexpected input access")):
            for args in cases:
                with self.subTest(args=args), self.assertRaisesRegex(enc.EncodeError, "publication is disabled"):
                    enc.main(args)
        for args in cases:
            with self.subTest(command=args[0]):
                result = self.cli(*args)
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertIn(b"publication is disabled", result.stderr)
                self.assertEqual(b"", result.stdout)
        self.assertFalse(self.user.exists())
        self.assert_game_unchanged()

    def test_legacy_paths_refuse_even_when_stdout_is_also_requested(self) -> None:
        cases = (
            ["extract", "--game", str(self.game), "--level", "200", "--out", str(self.user), "--stdout"],
            ["stage", "--game", str(self.game), "--level", "200", "--user", str(self.user), "--stdout"],
            ["encode", "--game", str(self.game), str(self.model), str(self.user / "world.wrd"), "--stdout"],
        )
        for args in cases:
            with self.subTest(command=args[0]):
                result = self.cli(*args)
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertIn(b"publication is disabled", result.stderr)
                self.assertEqual(b"", result.stdout)
        self.assertFalse(self.user.exists())
        self.assert_game_unchanged()

    def test_output_mode_must_be_explicit(self) -> None:
        cases = (
            ["extract", "--game", str(self.game), "--level", "200"],
            ["stage", "--game", str(self.game), "--level", "200"],
            ["encode", "--game", str(self.game), str(self.model)],
        )
        for args in cases:
            with self.subTest(command=args[0]):
                result = self.cli(*args)
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertIn(b"choose --stdout explicitly", result.stderr)
                self.assertEqual(b"", result.stdout)
        self.assert_game_unchanged()

    def test_existing_and_game_paths_are_not_touched_by_legacy_commands(self) -> None:
        self.user.mkdir()
        existing = self.user / "world.wrd"
        existing.write_bytes(b"pre-existing user data")
        cases = (
            ["extract", "--game", str(self.game), "--level", "200", "--out", str(self.resources)],
            ["stage", "--game", str(self.game), "--level", "200", "--user", str(self.game)],
            ["encode", "--game", str(self.game), str(self.model), str(existing)],
            ["encode", "--game", str(self.game), str(self.model), str(self.archive)],
        )
        for args in cases:
            with self.subTest(command=args[0]):
                result = self.cli(*args)
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertEqual(b"", result.stdout)
        self.assertEqual(b"pre-existing user data", existing.read_bytes())
        self.assert_game_unchanged()

    def test_linked_input_and_selected_root_alias_can_be_read_without_writes(self) -> None:
        alias = self.root / "game-alias"
        external = self.root / "external"
        external.mkdir()
        linked_game = self.root / "linked-game"
        (linked_game / "data").mkdir(parents=True)
        archive = external / "200_res_PC.aya"
        archive.write_bytes(self.original)
        try:
            alias.symlink_to(self.game, target_is_directory=True)
            (linked_game / "data" / "resources").symlink_to(external, target_is_directory=True)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"directory symlinks unavailable: {error}")
        for game in (alias, linked_game):
            with self.subTest(game=game):
                result = self.cli("extract", "--game", str(game), "--level", "200", "--stdout")
                self.assertEqual(0, result.returncode, result.stderr)
                self.assert_bundle_entry(json.loads(result.stdout), "world200.wrd", fixtures.world_body())
        self.assertEqual(self.original, archive.read_bytes())
        self.assertEqual(["200_res_PC.aya"], sorted(p.name for p in external.iterdir()))
        self.assert_game_unchanged()

    def test_verify_remains_a_read_only_command(self) -> None:
        result = self.cli("verify", "--game", str(self.game))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(b"byte-identical round trips: 1; failures: 0", result.stdout)
        self.assertFalse(self.user.exists())
        self.assert_game_unchanged()

    def test_cli_does_not_create_import_bytecode_without_environment_overrides(self) -> None:
        tools_copy = self.root / "fresh-tools"
        tools_copy.mkdir()
        names = ("world_resources_encode.py", "world_resources_decode.py", "aya_archive_inventory.py",
                 "safe_generated_output.py")
        for name in names:
            shutil.copyfile(Path(enc.__file__).parent / name, tools_copy / name)
        env = os.environ.copy()
        env.pop("PYTHONDONTWRITEBYTECODE", None)
        env.pop("PYTHONPYCACHEPREFIX", None)
        result = subprocess.run([sys.executable, str(tools_copy / "world_resources_encode.py"),
                                 "extract", "--game", str(self.game), "--level", "200", "--stdout"],
                                capture_output=True, timeout=30, env=env)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_bundle_entry(json.loads(result.stdout), "world200.wrd", fixtures.world_body())
        self.assertEqual(sorted(names), sorted(p.name for p in tools_copy.iterdir()))
        self.assert_game_unchanged()

    @unittest.skipUnless(sys.platform.startswith("linux") and shutil.which("bwrap"),
                         "static bind-mount control requires Linux bubblewrap")
    def test_bind_aliased_legacy_paths_refuse_and_stdout_stays_read_only(self) -> None:
        probe = subprocess.run(["bwrap", "--die-with-parent", "--unshare-net", "--ro-bind", "/", "/",
                                "--dev-bind", "/dev", "/dev", "--", "true"],
                               capture_output=True, timeout=20)
        if probe.returncode:
            self.skipTest("bubblewrap mount namespace is unavailable")
        external = self.root / "external"
        external.mkdir()
        archive = external / "200_res_PC.aya"
        archive.write_bytes(self.original)
        prefix = ["bwrap", "--die-with-parent", "--unshare-net", "--ro-bind", "/", "/",
                  "--dev-bind", "/dev", "/dev", "--bind", str(self.root), str(self.root),
                  "--bind", str(external), str(self.resources), "--setenv", "PYTHONDONTWRITEBYTECODE", "1",
                  "--", sys.executable, str(Path(enc.__file__))]
        commands = (["extract", "--game", str(self.game), "--level", "200", "--out", str(external)],
                    ["stage", "--game", str(self.game), "--level", "200", "--user", str(external)],
                    ["encode", "--game", str(self.game), str(self.model), str(external / "world.wrd")])
        for args in commands:
            with self.subTest(command=args[0]):
                result = subprocess.run([*prefix, *args], capture_output=True, timeout=30)
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertIn(b"publication is disabled", result.stderr)
                self.assertEqual(b"", result.stdout)
                self.assertEqual(["200_res_PC.aya"], sorted(p.name for p in external.iterdir()))
        result = subprocess.run([*prefix, "extract", "--game", str(self.game), "--level", "200", "--stdout"],
                                capture_output=True, timeout=30)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_bundle_entry(json.loads(result.stdout), "world200.wrd", fixtures.world_body())
        self.assertEqual(self.original, archive.read_bytes())
        self.assertEqual(["200_res_PC.aya"], sorted(p.name for p in external.iterdir()))
        self.assert_game_unchanged()

    def test_invalid_model_produces_no_output(self) -> None:
        model = json.loads(self.model.read_text(encoding="utf-8"))
        model["things"][0]["init"]["position"][0] = {"f32bits": "00"}
        self.model.write_text(json.dumps(model), encoding="utf-8")
        for args in (["encode", "--game", str(self.game), str(self.model), "--stdout"],
                     ["stage", "--game", str(self.game), "--level", "200", "--stdout", "--world", str(self.model)]):
            with self.subTest(command=args[0]):
                result = self.cli(*args)
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertIn(b"f32bits", result.stderr)
                self.assertEqual(b"", result.stdout)
        self.assert_game_unchanged()

    def test_stream_commands_use_no_tool_owned_write_operations(self) -> None:
        original_open = enc.os.open
        original_io_open = io.open
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
        opened = []

        def read_only_open(path, flags, *args, **kwargs):
            self.assertFalse(flags & write_flags, f"unexpected write flags for {path}")
            opened.append(str(path))
            return original_open(path, flags, *args, **kwargs)

        def read_only_io_open(path, mode="r", *args, **kwargs):
            self.assertFalse(any(flag in mode for flag in "wax+"), f"unexpected write mode for {path}")
            return original_io_open(path, mode, *args, **kwargs)

        commands = (["extract", "--game", str(self.game), "--level", "200", "--stdout"],
                    ["stage", "--game", str(self.game), "--level", "200", "--stdout"])
        with patch.object(enc.os, "open", side_effect=read_only_open), \
                patch.object(io, "open", side_effect=read_only_io_open), \
                patch.object(enc.os, "mkdir", side_effect=AssertionError("unexpected mkdir")), \
                patch.object(enc.os, "rename", side_effect=AssertionError("unexpected rename")), \
                patch.object(enc.os, "replace", side_effect=AssertionError("unexpected replace")), \
                patch.object(enc.os, "link", side_effect=AssertionError("unexpected link")), \
                patch.object(enc.os, "symlink", side_effect=AssertionError("unexpected symlink")), \
                patch.object(enc.os, "unlink", side_effect=AssertionError("unexpected unlink")):
            for args in commands:
                with self.subTest(command=args[0]), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(0, enc.main(args))
            stream = io.BytesIO()
            with patch.object(enc.sys, "stdout", SimpleNamespace(buffer=stream)):
                self.assertEqual(0, enc.main(["encode", "--game", str(self.game), str(self.model), "--stdout"]))
            self.assertEqual(fixtures.world_body(), stream.getvalue())
        self.assertEqual(2, len(opened))
        self.assertFalse(self.user.exists())
        self.assert_game_unchanged()

    def test_duplicate_bundle_names_are_refused(self) -> None:
        files = {}
        enc.add_bundle_file(files, "world.wrd", b"one")
        with self.assertRaisesRegex(enc.EncodeError, "same file name"):
            enc.add_bundle_file(files, "world.wrd", b"two")
        self.assertEqual(b"one", base64.b64decode(files["world.wrd"]["dataBase64"]))


if __name__ == "__main__":
    unittest.main()
