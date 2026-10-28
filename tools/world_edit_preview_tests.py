#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Authored world/script fixtures for the read-only editing preview; no game files are opened."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import content_catalog_tests as fixtures
import world_edit_preview as preview
import world_resources_encode as encoder


def model_bytes(model):
    return json.dumps(model, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("ascii")


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.body = fixtures.world_body()
        self.model = encoder.read_world_model(self.body)

    def inspect(self, model=None):
        raw = model_bytes(self.model if model is None else model)
        return preview.preview_bytes(self.body, raw, baseline_sha256=hashlib.sha256(self.body).hexdigest(),
                                     model_sha256=hashlib.sha256(raw).hexdigest())

    def test_unchanged_model_is_byte_identical_and_payload_is_not_reported(self):
        report = self.inspect()
        self.assertTrue(report["modelRoundTrip"]["representable"])
        self.assertTrue(report["candidateBody"]["identicalToBaseline"])
        self.assertEqual(report["candidateBody"]["changedBytePositions"], 0)
        self.assertEqual(report["changes"]["entries"], [])
        self.assertEqual(report["structuralReviewReasons"], [])
        self.assertEqual(report["opaqueFields"]["changedGroups"], [])
        self.assertEqual(report["scripts"]["candidate"]["records"][0]["status"], "complete")
        self.assertNotIn("Tank 1", json.dumps(report))
        self.assertIn("not a terrain", report["scope"])

    def test_movement_reports_actual_fields_and_byte_change_without_claiming_slot_safety(self):
        self.model["things"][0]["init"]["position"] = [12.5, -40.0, 3.0]
        report = self.inspect()
        candidate = encoder.write_world_body(self.model)
        self.assertEqual(report["candidateBody"]["changedBytePositions"],
                         sum(a != b for a, b in zip(self.body, candidate)))
        self.assertEqual(report["candidateBody"]["sha256"], hashlib.sha256(candidate).hexdigest())
        self.assertTrue(report["slotReview"]["thingsChanged"])
        self.assertFalse(report["slotReview"]["thingCountChanged"])
        self.assertTrue(report["slotReview"]["positionFieldsChanged"])
        self.assertFalse(report["slotReview"]["nonPositionFieldsOrOrderChanged"])
        self.assertFalse(report["slotReview"]["exactRecordPermutationObserved"])
        self.assertEqual(report["structuralReviewReasons"], ["placement-not-validated", "world-changes-not-fully-validated"])
        self.assertFalse(report["slotReview"]["waypointPathsChanged"])
        self.assertEqual(report["opaqueFields"]["changedGroups"], [])
        self.assertTrue(any(row["path"] == ["things", 0, "init", "position", 0]
                            for row in report["changes"]["entries"]))
        self.assertEqual(fixtures.world_body(), self.body)

    def test_append_changes_length_without_a_misleading_aligned_byte_count(self):
        self.model["things"].append(json.loads(json.dumps(self.model["things"][0])))
        report = self.inspect()
        self.assertTrue(report["slotReview"]["thingCountChanged"])
        self.assertIn("thing-count-changed", report["structuralReviewReasons"])
        self.assertIsNone(report["candidateBody"]["changedBytePositions"])
        self.assertIsNotNone(report["candidateBody"]["firstDifferentOffset"])

    def test_removing_thing_requires_review_even_when_other_records_are_unchanged(self):
        self.model["things"].pop()
        report = self.inspect()
        self.assertTrue(report["slotReview"]["thingCountChanged"])
        self.assertIn("thing-count-changed", report["structuralReviewReasons"])

    def test_exact_reorder_requires_review_and_does_not_claim_slot_identity(self):
        self.model["things"][0], self.model["things"][1] = self.model["things"][1], self.model["things"][0]
        report = self.inspect()
        self.assertTrue(report["slotReview"]["exactRecordPermutationObserved"])
        self.assertTrue(report["slotReview"]["nonPositionFieldsOrOrderChanged"])
        self.assertIn("thing-record-permutation-observed", report["structuralReviewReasons"])
        self.assertIn("do not prove record identity", report["slotReview"]["limit"])

    def test_exact_reorder_of_otherwise_equal_records_is_not_mistaken_for_just_a_move(self):
        model = encoder.read_world_model(self.body)
        clone = json.loads(json.dumps(model["things"][0]))
        clone["init"]["position"][0] = 33.0
        model["things"].append(clone)
        body = encoder.write_world_body(model)
        model["things"][0], model["things"][-1] = model["things"][-1], model["things"][0]
        report = preview.preview_bytes(body, model_bytes(model))
        self.assertFalse(report["slotReview"]["nonPositionFieldsOrOrderChanged"])
        self.assertTrue(report["slotReview"]["exactRecordPermutationObserved"])
        self.assertIn("thing-record-permutation-observed", report["structuralReviewReasons"])
        self.assertIn("placement-not-validated", report["structuralReviewReasons"])

    def test_other_encoded_changes_are_not_silently_called_safe(self):
        self.model["scripts"][0]["name"] = "renamed script"
        report = self.inspect()
        self.assertEqual(report["opaqueFields"]["changedGroups"], [])
        self.assertFalse(report["scripts"]["structuralReviewRequired"])
        self.assertEqual(report["structuralReviewReasons"], ["world-changes-not-fully-validated"])
        self.model["things"][0]["init"]["position"][0] = 33.0
        report = self.inspect()
        self.assertEqual(report["structuralReviewReasons"], ["placement-not-validated", "world-changes-not-fully-validated"])

    def test_definition_target_base_map_and_waypoint_edits_each_require_review(self):
        cases = (
            (lambda m: m["things"][0].__setitem__("definition", "AnotherUnit"),
             "nonPositionFieldsOrOrderChanged", "thing-nonposition-fields-or-order-changed"),
            (lambda m: m["things"][0]["init"].__setitem__("target", 2),
             "targetFieldsChanged", "thing-target-fields-changed"),
            (lambda m: m.__setitem__("baseLevel", m["baseLevel"] + 1),
             "baseLevelChanged", "base-level-changed"),
            (lambda m: m.__setitem__("mapNumber", m["mapNumber"] + 1),
             "mapNumberChanged", "map-number-changed"),
            (lambda m: m["waypointPaths"][0]["slots"].__setitem__(0, 9),
             "waypointPathsChanged", "waypoint-paths-changed"),
        )
        for edit, flag, reason in cases:
            with self.subTest(flag=flag):
                model = encoder.read_world_model(self.body)
                edit(model)
                report = self.inspect(model)
                self.assertTrue(report["slotReview"][flag])
                self.assertIn(reason, report["structuralReviewReasons"])

    def test_waypoints_and_unknown_regions_are_reported_independently(self):
        self.model["waypointPaths"][0]["slots"][0] = 9
        self.model["influenceMap"]["nodes"] = 1
        self.model["influenceMap"]["nodeBytes"] = encoder.blob(bytes(range(12)))
        self.model["scripts"][0]["trailer"] = "0102030405060708090a"
        report = self.inspect()
        self.assertTrue(report["slotReview"]["waypointPathsChanged"])
        self.assertIn("influence-map", report["opaqueFields"]["changedGroups"])
        self.assertIn("script-opaque-fields", report["opaqueFields"]["changedGroups"])
        self.assertIn("opaque-or-compiled-data-changed", report["structuralReviewReasons"])
        self.assertNotIn("0102030405060708090a", json.dumps(report))

    def test_opaque_occupancy_bytes_are_not_silently_discarded(self):
        self.model["occupancyGrids"][0] = {"version": 2, "data": encoder.blob(b"\x99" * 0x2000)}
        report = self.inspect()
        self.assertIn("occupancy-grids", report["opaqueFields"]["changedGroups"])
        self.assertNotEqual(report["opaqueFields"]["baselineSha256"]["occupancy-grids"],
                            report["opaqueFields"]["candidateSha256"]["occupancy-grids"])
        self.assertNotIn(encoder.blob(b"\x99" * 0x2000), json.dumps(report))

    def test_nonfinite_float_bits_round_trip_and_are_flagged_when_changed(self):
        self.model["timings"]["pan"] = {"f32bits": "0100c07f"}
        body = encoder.write_world_body(self.model)
        model = encoder.read_world_model(body)
        model["timings"]["pan"]["f32bits"] = "0100C07F"
        report = preview.preview_bytes(body, model_bytes(model))
        self.assertTrue(report["modelRoundTrip"]["representable"])
        self.assertTrue(report["candidateBody"]["identicalToBaseline"])
        model["timings"]["pan"]["f32bits"] = "0200c07f"
        report = preview.preview_bytes(body, model_bytes(model))
        self.assertIn("non-finite-float-bits", report["opaqueFields"]["changedGroups"])

    def test_ignored_model_field_and_derived_kind_are_reported(self):
        self.model["things"][0]["init"]["notEncoded"] = "AUTHORED_PRIVATE_VALUE"
        report = self.inspect()
        self.assertFalse(report["modelRoundTrip"]["representable"])
        self.assertTrue(report["candidateBody"]["identicalToBaseline"])
        self.assertTrue(any(row["path"] == ["things", 0, "init", "notEncoded"]
                            for row in report["modelRoundTrip"]["differences"]["entries"]))
        self.assertNotIn("AUTHORED_PRIVATE_VALUE", json.dumps(report))
        del self.model["things"][0]["init"]["notEncoded"]
        self.model["things"][0]["kind"] = "a nonserialized label"
        report = self.inspect()
        self.assertFalse(report["modelRoundTrip"]["representable"])
        self.assertTrue(any(row["path"] == ["things", 0, "kind"]
                            for row in report["modelRoundTrip"]["differences"]["entries"]))

    def test_script_inspector_separates_unknown_opcodes_and_bad_event_entries(self):
        self.model["scripts"][0]["code"]["instructions"][0][0] = 77
        report = self.inspect()
        self.assertEqual(report["scripts"]["baseline"]["records"][0]["status"], "complete")
        changed = report["scripts"]["candidate"]["records"][0]
        self.assertEqual(changed["status"], "unsupported")
        self.assertIn("unknown-opcode-layout", changed["findingCodes"])
        self.assertIn("compiled-script-code", report["opaqueFields"]["changedGroups"])
        self.assertTrue(report["scripts"]["structuralReviewRequired"])
        self.model["scripts"][0]["code"]["instructions"][0][0] = 5
        self.model["scripts"][0]["code"]["eventPCs"][0] = 999
        report = self.inspect()
        changed = report["scripts"]["candidate"]["records"][0]
        self.assertEqual(changed["status"], "complete")
        self.assertIn("event-pc-outside-instructions", changed["findingCodes"])
        self.assertTrue(report["scripts"]["structuralReviewRequired"])

    def test_changed_record_limit_does_not_hide_opaque_change(self):
        self.model["things"].extend(json.loads(json.dumps(self.model["things"][0])) for _ in range(520))
        self.model["scripts"][0]["trailer"] = "00000000000000000001"
        report = self.inspect()
        self.assertTrue(report["changes"]["truncated"])
        self.assertEqual(len(report["changes"]["entries"]), preview.MAX_CHANGES)
        self.assertIn("change-list-truncated", report["structuralReviewReasons"])
        self.assertIn("script-opaque-fields", report["opaqueFields"]["changedGroups"])

    def test_script_inspection_limit_is_explicit(self):
        self.model["scripts"].extend(json.loads(json.dumps(self.model["scripts"][0])) for _ in range(preview.MAX_SCRIPTS))
        report = self.inspect()
        scripts = report["scripts"]["candidate"]
        self.assertEqual(scripts["total"], preview.MAX_SCRIPTS + 1)
        self.assertEqual(scripts["inspected"], preview.MAX_SCRIPTS)
        self.assertTrue(scripts["truncated"])
        self.assertTrue(report["scripts"]["structuralReviewRequired"])

    def test_bad_identity_invalid_json_and_unencodable_model_are_refused(self):
        data = model_bytes(self.model)
        for digest in ("0" * 64, "abc", "A" * 64):
            with self.subTest(digest=digest), self.assertRaisesRegex(preview.PreviewError, "baseline-identity-mismatch"):
                preview.preview_bytes(self.body, data, baseline_sha256=digest)
        with self.assertRaisesRegex(preview.PreviewError, "model-identity-mismatch"):
            preview.preview_bytes(self.body, data, model_sha256="0" * 64)
        for invalid in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b"\xff"):
            with self.subTest(invalid=invalid), self.assertRaises(preview.PreviewError):
                preview.preview_bytes(self.body, invalid)
        self.model["things"][0]["init"]["position"][0] = {"f32bits": "00"}
        with self.assertRaisesRegex(preview.PreviewError, "world-model-cannot-be-encoded-or-read"):
            self.inspect()
        with self.assertRaises(TypeError):
            preview.preview_bytes(bytearray(self.body), data)


@unittest.skipUnless(all(hasattr(os, name) for name in ("O_NOFOLLOW", "O_DIRECTORY", "O_CLOEXEC", "O_NONBLOCK")),
                     "descriptor-relative no-follow unavailable")
class PreviewFileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.body = self.root / "original.wrd"
        self.model = self.root / "edited.json"
        self.body.write_bytes(fixtures.world_body())
        self.model.write_bytes(model_bytes(encoder.read_world_model(self.body.read_bytes())))

    def test_cli_is_read_only_and_reports_both_snapshot_hashes(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(0, preview.main([str(self.body), str(self.model)]))
        report = json.loads(stdout.getvalue())
        self.assertEqual(report["baseline"]["sha256"], hashlib.sha256(before["original.wrd"]).hexdigest())
        self.assertEqual(report["model"]["sha256"], hashlib.sha256(before["edited.json"]).hexdigest())
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_cli_flags_ignored_edits_without_writing_anything(self):
        model = encoder.read_world_model(self.body.read_bytes())
        model["things"][0]["ignored"] = "private"
        self.model.write_bytes(model_bytes(model))
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(1, preview.main([str(self.body), str(self.model)]))
        self.assertFalse(json.loads(stdout.getvalue())["modelRoundTrip"]["representable"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_cli_flags_structural_script_findings_without_writing_anything(self):
        model = encoder.read_world_model(self.body.read_bytes())
        model["scripts"][0]["code"]["eventPCs"][0] = 999
        self.model.write_bytes(model_bytes(model))
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(1, preview.main([str(self.body), str(self.model)]))
        self.assertTrue(json.loads(stdout.getvalue())["scripts"]["structuralReviewRequired"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_cli_requires_review_for_an_appended_authored_thing(self):
        model = encoder.read_world_model(self.body.read_bytes())
        model["things"].append(json.loads(json.dumps(model["things"][0])))
        self.model.write_bytes(model_bytes(model))
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(1, preview.main([str(self.body), str(self.model)]))
        self.assertIn("thing-count-changed", json.loads(stdout.getvalue())["structuralReviewReasons"])

    def test_fresh_cli_process_creates_no_import_caches_or_other_files(self):
        isolated = self.root / "tools"
        isolated.mkdir()
        source = Path(preview.__file__).parent
        for name in ("world_edit_preview.py", "world_resources_encode.py", "world_resources_decode.py",
                     "mission_script_inspect.py", "aya_archive_inventory.py", "safe_generated_output.py"):
            shutil.copyfile(source / name, isolated / name)

        def tree_snapshot():
            return {str(path.relative_to(self.root)): ("dir" if path.is_dir() else hashlib.sha256(path.read_bytes()).hexdigest())
                    for path in self.root.rglob("*")}

        before = tree_snapshot()
        environment = os.environ.copy()
        for key in ("PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX", "PYTHONPATH"):
            environment.pop(key, None)
        result = subprocess.run([sys.executable, str(isolated / "world_edit_preview.py"), str(self.body), str(self.model)],
                                cwd=self.root, env=environment, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["candidateBody"]["identicalToBaseline"])
        self.assertEqual(before, tree_snapshot())

    def test_symlink_at_leaf_or_parent_and_fifo_are_refused(self):
        leaf = self.root / "link.wrd"
        leaf.symlink_to(self.body)
        with self.assertRaises(OSError):
            preview._read_snapshot(leaf, preview.MAX_BODY_BYTES)
        parent = self.root / "parent-link"
        parent.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(OSError):
            preview._read_snapshot(parent / self.body.name, preview.MAX_BODY_BYTES)
        fifo = self.root / "pipe"
        os.mkfifo(fifo)
        with self.assertRaisesRegex(preview.PreviewError, "input-type-or-byte-limit"):
            preview._read_snapshot(fifo, preview.MAX_BODY_BYTES)

    def test_parent_component_cannot_hide_a_symlink_or_select_a_different_file(self):
        elsewhere = self.root / "elsewhere"
        (elsewhere / "inner").mkdir(parents=True)
        (elsewhere / self.body.name).write_bytes(b"another authored body")
        link = self.root / "link"
        link.symlink_to(elsewhere / "inner", target_is_directory=True)
        ambiguous = link / ".." / self.body.name
        self.assertNotEqual(ambiguous.read_bytes(), self.body.read_bytes())
        with self.assertRaisesRegex(preview.PreviewError, "input-path-parent-component-not-allowed"):
            preview._read_snapshot(ambiguous, preview.MAX_BODY_BYTES)
        with self.assertRaisesRegex(preview.PreviewError, "input-path-parent-component-not-allowed"):
            preview._read_snapshot(elsewhere / ".." / self.body.name, preview.MAX_BODY_BYTES)

    def test_oversized_file_and_input_path_replaced_during_read_are_refused(self):
        with self.assertRaisesRegex(preview.PreviewError, "input-type-or-byte-limit"):
            preview._read_snapshot(self.body, self.body.stat().st_size - 1)
        replacement = self.root / "replacement.wrd"
        replacement.write_bytes(b"different authored data")
        real_read = os.read
        swapped = False

        def read_then_replace(fd, count):
            nonlocal swapped
            data = real_read(fd, count)
            if not data and not swapped:
                swapped = True
                os.replace(replacement, self.body)
            return data

        with patch.object(preview.os, "read", side_effect=read_then_replace):
            with self.assertRaisesRegex(preview.PreviewError, "input-(changed-during-read|path-replaced-during-read)"):
                preview._read_snapshot(self.body, preview.MAX_BODY_BYTES)
        self.assertTrue(swapped)


if __name__ == "__main__":
    unittest.main()
