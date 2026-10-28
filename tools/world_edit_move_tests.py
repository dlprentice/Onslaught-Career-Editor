#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Authored-fixture checks for the single-thing move workflow; no game data is used."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import content_catalog_tests as fixtures
import world_edit_move as move
import world_resources_encode as encoder


def digest(data):
    return hashlib.sha256(data).hexdigest()


class MoveTests(unittest.TestCase):
    def setUp(self):
        self.body = fixtures.world_body()

    def test_move_only_selected_position_bytes_and_preserves_other_records(self):
        candidate_raw, report = move.prepare_move(self.body, 1, ["12.5", "-40", "3"])
        candidate = json.loads(candidate_raw)
        candidate_body = encoder.write_world_body(candidate)
        old = encoder.read_world_model(self.body)
        start = report["selectedPositionByteOffset"]
        self.assertEqual(candidate_body[:start], self.body[:start])
        self.assertEqual(candidate_body[start + 12:], self.body[start + 12:])
        self.assertEqual(candidate["things"][1]["init"]["position"], [12.5, -40.0, 3.0])
        self.assertEqual(candidate["things"][0], old["things"][0])
        self.assertEqual(candidate["scripts"], old["scripts"])
        self.assertEqual(candidate["influenceMap"], old["influenceMap"])
        self.assertEqual(candidate["occupancyGrids"], old["occupancyGrids"])
        self.assertEqual(candidate["waypointPaths"], old["waypointPaths"])
        self.assertEqual(report["preview"]["model"]["sha256"], digest(candidate_raw))
        self.assertEqual(report["preview"]["candidateBody"]["sha256"], digest(candidate_body))
        self.assertTrue(report["reviewRequired"])
        self.assertEqual(report["preview"]["opaqueFields"]["changedGroups"], [])
        self.assertIn("placement-not-validated", report["preview"]["structuralReviewReasons"])
        self.assertIn("world-changes-not-fully-validated", report["preview"]["structuralReviewReasons"])
        self.assertEqual(self.body, fixtures.world_body())

    def test_existing_nonfinite_position_is_refused_but_unrelated_bits_are_kept(self):
        original = encoder.read_world_model(self.body)
        original["things"][0]["init"]["position"][0] = {"f32bits": "0100c07f"}
        body = encoder.write_world_body(original)
        with self.assertRaisesRegex(move.MoveError, "existing-position-not-three-finite"):
            move.prepare_move(body, 0, ["1", "2", "3"])
        candidate_raw, report = move.prepare_move(body, 1, ["1", "2", "3"])
        candidate = json.loads(candidate_raw)
        self.assertEqual(candidate["things"][0]["init"]["position"][0], {"f32bits": "0100c07f"})
        self.assertEqual(report["preview"]["opaqueFields"]["changedGroups"], [])

    def test_float_rounding_requires_explicit_option_and_is_reported(self):
        with self.assertRaisesRegex(move.MoveError, "coordinate-needs-float32-rounding"):
            move.prepare_move(self.body, 0, ["0.1", "2", "3"])
        raw, report = move.prepare_move(self.body, 0, ["0.1", "2", "3"], allow_rounding=True)
        x = report["requestedPosition"][0]
        self.assertTrue(x["rounded"])
        self.assertEqual(x["requested"], "0.1")
        self.assertEqual(x["float32LittleEndianHex"], "cdcccc3d")
        self.assertEqual(json.loads(raw)["things"][0]["init"]["position"][0], x["stored"])

    def test_signed_zero_is_a_real_change(self):
        model = encoder.read_world_model(self.body)
        model["things"][0]["init"]["position"] = [0.0, 0.0, 0.0]
        body = encoder.write_world_body(model)
        raw, report = move.prepare_move(body, 0, ["-0", "0", "0"])
        start = report["selectedPositionByteOffset"]
        new_body = encoder.write_world_body(json.loads(raw))
        self.assertEqual(body[start:start + 4], bytes.fromhex("00000000"))
        self.assertEqual(new_body[start:start + 4], bytes.fromhex("00000080"))
        self.assertEqual(report["preview"]["candidateBody"]["changedBytePositions"], 1)

    def test_invalid_inputs_and_noop_are_refused(self):
        for index in (-1, 9999, True):
            with self.subTest(index=index), self.assertRaises(move.MoveError):
                move.prepare_move(self.body, index, ["1", "2", "3"])
        for coordinates in (["nan", "2", "3"], ["1e9999", "2", "3"], ["oops", "2", "3"],
                            ["1", "2"], ["1" * 129, "2", "3"]):
            with self.subTest(coordinates=coordinates), self.assertRaises(move.MoveError):
                move.prepare_move(self.body, 0, coordinates)
        old = encoder.read_world_model(self.body)["things"][0]["init"]["position"]
        with self.assertRaisesRegex(move.MoveError, "position-unchanged"):
            move.prepare_move(self.body, 0, [repr(v) for v in old])
        with self.assertRaises(move.MoveError):
            move.prepare_move(b"not a world", 0, ["1", "2", "3"])

    def test_byte_check_refuses_unrelated_encoder_change(self):
        actual_write = encoder.write_world_body
        calls = 0

        def corrupt_candidate(model):
            nonlocal calls
            calls += 1
            encoded = actual_write(model)
            if calls == 3:
                return encoded[:-1] + bytes([encoded[-1] ^ 1])
            return encoded

        with patch.object(encoder, "write_world_body", side_effect=corrupt_candidate):
            with self.assertRaisesRegex(move.MoveError, "candidate-changes-outside-selected-position"):
                move.prepare_move(self.body, 0, ["1", "2", "3"])

    def test_probe_refuses_an_extra_unrelated_byte_change(self):
        actual_write = encoder.write_world_body
        calls = 0

        def corrupt_probe(model):
            nonlocal calls
            calls += 1
            encoded = actual_write(model)
            if calls == 2:
                return encoded[:-1] + bytes([encoded[-1] ^ 1])
            return encoded

        with patch.object(encoder, "write_world_body", side_effect=corrupt_probe):
            with self.assertRaisesRegex(move.MoveError, "cannot-locate-exact-position-bytes"):
                move.prepare_move(self.body, 0, ["1", "2", "3"])

    def test_preview_refuses_unexpected_structural_or_opaque_change(self):
        actual_preview = move.preview.preview_bytes
        for mutation in (lambda report: report["opaqueFields"]["changedGroups"].append("influence-map"),
                         lambda report: report["slotReview"].__setitem__("waypointPathsChanged", True),
                         lambda report: report["modelRoundTrip"].__setitem__("representable", False),
                         lambda report: report["changes"].__setitem__("truncated", True)):
            def tamper(*args, **kwargs):
                report = actual_preview(*args, **kwargs)
                mutation(report)
                return report

            with self.subTest(mutation=mutation), patch.object(move.preview, "preview_bytes", side_effect=tamper):
                with self.assertRaisesRegex(move.MoveError, "preview-found-an-unsupported-change"):
                    move.prepare_move(self.body, 0, ["1", "2", "3"])


class MoveCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="authored-world-move-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.game = self.root / "authored-game"
        self.game.mkdir()
        self.local = self.root / "private-local-data"
        self.body = fixtures.world_body()
        self.world = self.root / "authored.wrd"
        self.world.write_bytes(self.body)
        self.args = [str(self.world), "--thing", "0", "--position", "12.5", "-40", "3"]

    def run_main(self, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(move, "LOCAL_DATA", self.local), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = move.main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def preview(self):
        code, output, errors = self.run_main(self.args)
        self.assertEqual(code, 0, errors)
        return json.loads(output)

    def save_args(self, report, out="edits/candidate.json"):
        return self.args + ["--out", out, "--game", str(self.game), "--acknowledge-unvalidated",
                            "--baseline-sha256", report["preview"]["baseline"]["sha256"],
                            "--model-sha256", report["preview"]["model"]["sha256"]]

    def test_two_step_hash_pinned_save_is_fresh_private_and_input_unchanged(self):
        report = self.preview()
        self.assertEqual(report["publication"]["status"], "preview-only")
        self.assertFalse(self.local.exists())
        code, output, errors = self.run_main(self.save_args(report))
        self.assertEqual(code, 0, errors)
        published = json.loads(output)
        candidate = self.local / "edits" / "candidate.json"
        self.assertEqual(published["publication"]["status"], "new-private-model-not-staged")
        self.assertEqual(digest(candidate.read_bytes()), report["preview"]["model"]["sha256"])
        self.assertEqual(self.world.read_bytes(), self.body)
        self.assertEqual(list(self.game.iterdir()), [])
        code, _, _ = self.run_main(self.save_args(report))
        self.assertEqual(code, 2)  # Never overwrite an existing result.
        self.assertEqual(digest(candidate.read_bytes()), report["preview"]["model"]["sha256"])

    def test_missing_review_consent_or_wrong_hashes_do_not_write(self):
        report = self.preview()
        cases = [self.args + ["--out", "candidate.json"],
                 self.save_args(report) + ["--baseline-sha256", "0" * 64],
                 self.save_args(report) + ["--model-sha256", "f" * 64],
                 self.save_args(report)[:-2]]
        for args in cases:
            with self.subTest(args=args):
                self.assertEqual(self.run_main(args)[0], 2)
                self.assertFalse(self.local.exists())
        self.assertEqual(self.world.read_bytes(), self.body)

    def test_changed_body_and_changed_requested_position_are_refused_after_preview(self):
        report = self.preview()
        model = encoder.read_world_model(self.body)
        model["mapNumber"] += 1
        self.world.write_bytes(encoder.write_world_body(model))
        self.assertEqual(self.run_main(self.save_args(report))[0], 2)
        self.world.write_bytes(self.body)
        args = self.save_args(report)
        args[args.index("12.5")] = "13.5"
        self.assertEqual(self.run_main(args)[0], 2)
        self.assertFalse(self.local.exists())

    def test_outside_and_game_overlapping_destinations_are_refused(self):
        report = self.preview()
        for name in ("../escape.json", "/tmp/escape.json", "not-a-json.txt"):
            with self.subTest(name=name):
                self.assertEqual(self.run_main(self.save_args(report, name))[0], 2)
        with patch.object(move, "LOCAL_DATA", self.game):
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = move.main(self.save_args(report, "candidate.json"))
            self.assertEqual(code, 2)
        self.assertEqual(list(self.game.iterdir()), [])

    def test_symlink_input_and_output_are_refused(self):
        report = self.preview()
        alias = self.root / "alias.wrd"
        alias.symlink_to(self.world)
        args = [str(alias)] + self.args[1:]
        self.assertEqual(self.run_main(args)[0], 2)
        self.local.mkdir()
        (self.local / "redirect").symlink_to(self.game, target_is_directory=True)
        self.assertEqual(self.run_main(self.save_args(report, "redirect/candidate.json"))[0], 2)
        self.assertEqual(list(self.game.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
