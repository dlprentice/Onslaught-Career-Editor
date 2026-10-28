#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Authored-fixture checks for the single-thing move workflow; no game data is used."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
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


class ByteStdout:
    """Capture both the textual preview and the exact model byte stream."""
    def __init__(self):
        self.buffer = io.BytesIO()

    def write(self, value):
        return self.buffer.write(value.encode("utf-8"))

    def flush(self):
        self.buffer.flush()


class MoveCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="authored-world-move-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.body = fixtures.world_body()
        self.world = self.root / "authored.wrd"
        self.world.write_bytes(self.body)
        self.sentinel = self.root / "existing.json"
        self.sentinel.write_bytes(b"existing user file")
        self.args = [str(self.world), "--thing", "0", "--position", "12.5", "-40", "3"]

    def run_main(self, args, stdout=None):
        stdout = stdout or ByteStdout()
        stderr = io.StringIO()
        real_open = os.open
        forbidden = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND

        def only_read_open(path, flags, *args, **kwargs):
            if flags & forbidden:
                raise AssertionError("the CLI tried to open a filesystem path for writing")
            return real_open(path, flags, *args, **kwargs)

        with patch.object(os, "open", side_effect=only_read_open), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = move.main(args)
        return code, stdout.buffer.getvalue(), stderr.getvalue()

    def preview(self):
        code, output, errors = self.run_main(self.args)
        self.assertEqual(code, 0, errors)
        return json.loads(output)

    def emit_args(self, report):
        return self.args + ["--emit-model", "--acknowledge-unvalidated",
                            "--baseline-sha256", report["preview"]["baseline"]["sha256"],
                            "--model-sha256", report["preview"]["model"]["sha256"]]

    def test_hash_pinned_model_stream_and_preview_are_read_only(self):
        report = self.preview()
        self.assertEqual(report["output"]["status"], "preview-only")
        self.assertNotIn("Tank 1", json.dumps(report))
        code, data, errors = self.run_main(self.emit_args(report))
        self.assertEqual(code, 0, errors)
        self.assertEqual(digest(data), report["preview"]["model"]["sha256"])
        self.assertEqual(json.loads(data)["things"][0]["init"]["position"], [12.5, -40.0, 3.0])
        self.assertEqual(self.world.read_bytes(), self.body)
        self.assertEqual(self.sentinel.read_bytes(), b"existing user file")
        self.assertEqual({p.name for p in self.root.iterdir()}, {"authored.wrd", "existing.json"})

    def test_missing_consent_or_wrong_hashes_emit_no_model(self):
        report = self.preview()
        cases = [self.args + ["--emit-model"],
                 self.emit_args(report) + ["--baseline-sha256", "0" * 64],
                 self.emit_args(report) + ["--model-sha256", "f" * 64],
                 self.emit_args(report)[:-2],
                 self.args + ["--acknowledge-unvalidated"]]
        for args in cases:
            with self.subTest(args=args):
                code, data, _ = self.run_main(args)
                self.assertEqual(code, 2)
                self.assertEqual(data, b"")
        self.assertEqual(self.world.read_bytes(), self.body)
        self.assertEqual(self.sentinel.read_bytes(), b"existing user file")

    def test_changed_body_and_changed_requested_position_emit_no_model(self):
        report = self.preview()
        model = encoder.read_world_model(self.body)
        model["mapNumber"] += 1
        self.world.write_bytes(encoder.write_world_body(model))
        code, data, _ = self.run_main(self.emit_args(report))
        self.assertEqual((code, data), (2, b""))
        self.world.write_bytes(self.body)
        args = self.emit_args(report)
        args[args.index("12.5")] = "13.5"
        code, data, _ = self.run_main(args)
        self.assertEqual((code, data), (2, b""))
        self.assertEqual(self.sentinel.read_bytes(), b"existing user file")

    def test_output_path_option_does_not_exist(self):
        # No output-path API means the CLI cannot overwrite a file or publish into an install.
        # Shell redirection is external to the CLI and receives no such guarantee.
        for option in ("--out", "--game"):
            with self.subTest(option=option), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    self.run_main(self.args + [option, str(self.sentinel)])
                self.assertEqual(error.exception.code, 2)
        self.assertEqual(self.sentinel.read_bytes(), b"existing user file")

    def test_symlink_input_is_refused(self):
        alias = self.root / "alias.wrd"
        alias.symlink_to(self.world)
        args = [str(alias)] + self.args[1:]
        code, data, _ = self.run_main(args)
        self.assertEqual((code, data), (2, b""))
        self.assertEqual(self.world.read_bytes(), self.body)

    def test_incomplete_stdout_stream_is_an_error(self):
        class ShortStream(io.BytesIO):
            def write(self, value):
                super().write(value[:1])
                return 1

        stdout = ByteStdout()
        stdout.buffer = ShortStream()
        code, data, error = self.run_main(self.emit_args(self.preview()), stdout=stdout)
        self.assertEqual(code, 2)
        self.assertEqual(len(data), 1)  # External consumers may receive partial bytes on stream failure.
        self.assertIn("model-stream-incomplete", error)
        self.assertEqual(self.sentinel.read_bytes(), b"existing user file")


if __name__ == "__main__":
    unittest.main()
