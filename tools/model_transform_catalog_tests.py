#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Authored model-transform fixtures; never reads an installed game or user profile."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import math
import os
from pathlib import Path
import struct
import tempfile
import unittest
import zlib
from unittest import mock

import cmsh_animation_usage_census_tests as fixtures
import model_transform_catalog as catalog


def chunk(tag: bytes, data: bytes) -> bytes:
    return tag + struct.pack("<I", len(data)) + data


def orientation(rows: tuple[tuple[float, float, float], ...], pad: int = 0) -> bytes:
    return b"".join(struct.pack("<3fI", *row, pad) for row in rows)


IDENTITY = ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.))
REFLECTION = ((-1., 0., 0.), (0., 1., 0.), (0., 0., 1.))
SCALE = ((2., 0., 0.), (0., 1., 0.), (0., 0., 1.))


def make_part(rows: list, frame_map: bytes, pad: int = 0, *, ordinal: int = 0,
              parent: int | None = None, children: tuple[int, ...] = ()) -> bytes:
    original = fixtures._catalog_part(ordinal, parent=parent, children=children, geometry=True)
    payload = bytearray(original[8:])
    struct.pack_into("<I", payload, 8 + 0xb8, len(frame_map))
    struct.pack_into("<I", payload, 8 + 0xbc, len(rows))
    def replace(old: bytes, new: bytes) -> None:
        nonlocal payload
        assert payload.count(old) == 1
        payload = bytearray(bytes(payload).replace(old, new, 1))
    replace(chunk(b"VHFM", b"\0"), chunk(b"VHFM", frame_map))
    replace(chunk(b"HORI", bytes(48)), chunk(b"HORI", b"".join(orientation(r, pad) for r in rows)))
    replace(chunk(b"HPOS", bytes(16)), chunk(b"HPOS", bytes(16 * len(rows))))
    return chunk(b"MESP", bytes(payload))


def make_stream(rows=None, frame_map=b"\0", pad: int = 0, **kwargs) -> bytes:
    return fixtures._catalog_stream(parts=[make_part(rows or [IDENTITY], frame_map, pad)], **kwargs)


def aya(stream: bytes) -> bytes:
    compressed = zlib.compress(stream)
    return struct.pack("<I", len(compressed)) + compressed


class MatrixClassificationTests(unittest.TestCase):
    def test_proper_rotation_reflection_and_nonorthogonal(self) -> None:
        rotation = ((0., -1., 0.), (1., 0., 0.), (0., 0., 1.))
        self.assertEqual("proper", catalog.classify_orientation(IDENTITY)[0])
        self.assertEqual("proper", catalog.classify_orientation(rotation)[0])
        self.assertEqual("reflected", catalog.classify_orientation(REFLECTION)[0])
        self.assertEqual("nonOrthogonal", catalog.classify_orientation(SCALE)[0])
        # Negative determinant alone does not make a scaled basis an orthonormal reflection.
        reflected_scale = ((-2., 0., 0.), (0., 1., 0.), (0., 0., 1.))
        self.assertEqual("nonOrthogonal", catalog.classify_orientation(reflected_scale)[0])

    def test_nonfinite_and_malformed_fail_closed(self) -> None:
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                catalog.classify_orientation(((value, 0., 0.), (0., 1., 0.), (0., 0., 1.)))
        with self.assertRaises(ValueError):
            catalog.classify_orientation(((1., 0.),))

    def test_orthogonality_tolerance_is_explicit(self) -> None:
        within = ((1.00001, 0., 0.), (0., 1., 0.), (0., 0., 1.))
        outside = ((1.0002, 0., 0.), (0., 1., 0.), (0., 0., 1.))
        self.assertEqual("proper", catalog.classify_orientation(within)[0])
        self.assertEqual("nonOrthogonal", catalog.classify_orientation(outside)[0])


class MeshProjectionTests(unittest.TestCase):
    def test_stored_keys_distinct_references_and_frame_multiplicity_are_separate(self) -> None:
        stream = make_stream([IDENTITY, REFLECTION, SCALE], b"\0\1\1\0")
        model = catalog.analyse_stream(stream, source_name="authored.aya", source_sha256="a" * 64)
        [part] = model["parts"]
        self.assertEqual({"proper": 1, "reflected": 1, "nonOrthogonal": 1}, part["storedKeys"])
        self.assertEqual({"proper": 1, "reflected": 1, "nonOrthogonal": 0}, part["referencedDistinctKeys"])
        self.assertEqual({"proper": 2, "reflected": 2, "nonOrthogonal": 0}, part["virtualFrameReferences"])
        self.assertEqual([1], part["reflectedKeyOrdinals"])
        self.assertEqual([[1, 2]], part["reflectedVirtualFrameRanges"])
        self.assertEqual(1, part["unreferencedKeyCount"])
        self.assertEqual(1, model["summary"]["partsWithReferencedReflectedKeys"])
        self.assertEqual(1, model["summary"]["partsWithNonOrthogonalKeys"])

    def test_part_local_not_composed_and_no_payload_or_pose_matrices_are_emitted(self) -> None:
        first = make_stream([REFLECTION], b"\0", pad=0x7fc12345)
        second = make_stream([REFLECTION], b"\0", pad=0x12345678)
        a = catalog.analyse_stream(first, source_name="a", source_sha256="a" * 64)
        b = catalog.analyse_stream(second, source_name="a", source_sha256="a" * 64)
        self.assertEqual(a["parts"], b["parts"])  # padding is neither a coordinate nor a classification input
        self.assertNotEqual(a["source"]["inflatedCmshStreamSha256"], b["source"]["inflatedCmshStreamSha256"])
        text = json.dumps(a, allow_nan=False)
        for forbidden in ("rows", "geometry", "vertices", "position", "frameMap", "2139169605"):
            self.assertNotIn(forbidden, text)

    def test_reflection_in_unreferenced_key_is_not_claimed_as_referenced(self) -> None:
        [part] = catalog.analyse_stream(make_stream([IDENTITY, REFLECTION], b"\0\0"),
                                        source_name="a", source_sha256="a" * 64)["parts"]
        self.assertEqual(1, part["storedKeys"]["reflected"])
        self.assertEqual(0, part["referencedDistinctKeys"]["reflected"])
        self.assertEqual(0, part["virtualFrameReferences"]["reflected"])
        self.assertEqual([1], part["reflectedKeyOrdinals"])
        self.assertEqual([], part["reflectedVirtualFrameRanges"])

    def test_parent_and_child_reflections_are_both_local_not_composed(self) -> None:
        root = make_part([REFLECTION], b"\0", ordinal=0, children=(1,))
        child = make_part([REFLECTION], b"\0", ordinal=1, parent=0)
        model = catalog.analyse_stream(fixtures._catalog_stream(parts=[root, child]),
                                       source_name="a", source_sha256="a" * 64)
        self.assertEqual([None, 0], [part["parentOrdinal"] for part in model["parts"]])
        self.assertEqual([1, 1], [part["storedKeys"]["reflected"] for part in model["parts"]])

    def test_ranges_split_on_nonreflected_frames(self) -> None:
        self.assertEqual([[0, 0], [2, 3], [5, 5]],
                         catalog.reflected_ranges(["reflected", "proper", "reflected", "reflected", "nonOrthogonal", "reflected"]))

    def test_bad_frame_map_nonfinite_and_truncation_refuse(self) -> None:
        with self.assertRaisesRegex(ValueError, "absent hierarchy"):
            catalog.analyse_stream(make_stream([IDENTITY], b"\1"), source_name="a", source_sha256="a" * 64)
        bad = ((float("nan"), 0., 0.), (0., 1., 0.), (0., 0., 1.))
        with self.assertRaisesRegex(ValueError, "non-finite"):
            catalog.analyse_stream(make_stream([bad]), source_name="a", source_sha256="a" * 64)
        with self.assertRaises(ValueError):
            catalog.analyse_stream(make_stream()[:-4], source_name="a", source_sha256="a" * 64)

    def test_nested_chain_is_counted_not_analyzed(self) -> None:
        stream = make_stream(lod=fixtures._catalog_stream(), next_marker=True)
        model = catalog.analyse_stream(stream, source_name="a", source_sha256="a" * 64)
        self.assertEqual(1, model["summary"]["nestedMeshSiblingCandidatesNotAnalysed"])
        self.assertEqual(1, len(model["parts"]))


class BoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        local = catalog.ROOT / "local-data"
        local.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="model-transform-test-", dir=local)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "input" / "authored.aya"
        self.source.parent.mkdir()
        self.source.write_bytes(aya(make_stream([IDENTITY, REFLECTION], b"\0\1")))
        self.output = self.root / "reports" / "selected.json"

    def run_cli(self, args: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = catalog.main(args)
            except SystemExit as error:
                rc = error.code
        return rc, out.getvalue(), err.getvalue()

    def test_selected_source_private_new_output_and_repeat_refusal(self) -> None:
        before = self.source.read_bytes()
        args = ["--mesh", str(self.source), "--out", str(self.output)]
        rc, _, _ = self.run_cli(args)
        self.assertEqual(0, rc)
        report = json.loads(self.output.read_text())
        self.assertTrue(report["generatedRetailDerived"])
        self.assertEqual(catalog.SCHEMA, report["schema"])
        [mesh] = report["meshes"]
        self.assertEqual(hashlib.sha256(before).hexdigest(), mesh["source"]["archiveSha256"])
        self.assertEqual(1, mesh["parts"][0]["storedKeys"]["reflected"])
        original_report = self.output.read_bytes()
        self.assertNotEqual(0, self.run_cli(args)[0])
        self.assertEqual(original_report, self.output.read_bytes())
        self.assertEqual(before, self.source.read_bytes())

    def test_invalid_and_unsafe_inputs_publish_no_output(self) -> None:
        for kind in ("truncated", "link", "hardlink", "missing"):
            with self.subTest(kind=kind):
                source = self.root / "input" / kind
                if kind == "truncated": source.write_bytes(aya(make_stream()[:-10]))
                elif kind == "link": source.symlink_to(self.source.name)
                elif kind == "hardlink": os.link(self.source, source)
                target = self.root / "reports" / (kind + ".json")
                rc, _, _ = self.run_cli(["--mesh", str(source), "--out", str(target)])
                self.assertNotEqual(0, rc)
                self.assertFalse(target.exists())
                if kind == "hardlink": source.unlink()  # authored hard link, so the next case can use the source

    def test_duplicate_selection_and_paths_with_parent_component_refuse(self) -> None:
        with self.assertRaisesRegex(ValueError, "more than once"):
            catalog.report_for([self.source, self.source])
        self.assertFalse(catalog.output_allowed(catalog.ROOT / "local-data" / "x" / ".." / "report.json"))
        self.assertFalse(catalog.output_allowed(catalog.ROOT / "report.json"))

    def test_total_frame_and_part_limits_refuse_without_output(self) -> None:
        for field, limit in (("MAX_TOTAL_VIRTUAL_FRAMES", 1), ("MAX_TOTAL_PARTS", 0)):
            with self.subTest(field=field), mock.patch.object(catalog, field, limit):
                rc, _, _ = self.run_cli(["--mesh", str(self.source), "--out", str(self.output)])
                self.assertNotEqual(0, rc)
                self.assertFalse(self.output.exists())

    def test_symlinked_output_parent_is_refused(self) -> None:
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        (self.root / "link").symlink_to(elsewhere, target_is_directory=True)
        target = self.root / "link" / "report.json"
        rc, _, _ = self.run_cli(["--mesh", str(self.source), "--out", str(target)])
        self.assertNotEqual(0, rc)
        self.assertFalse((elsewhere / "report.json").exists())

    def test_other_platforms_refuse_before_publication(self) -> None:
        with mock.patch.object(catalog.sys, "platform", "win32"):
            rc, _, _ = self.run_cli(["--mesh", str(self.source), "--out", str(self.output)])
        self.assertEqual(2, rc)
        self.assertFalse(self.output.exists())

    def test_schema_matches_authored_report_when_validator_available(self) -> None:
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema = json.loads((catalog.ROOT / "tools/model_transform_catalog.schema.json").read_text())
        report = catalog.report_for([self.source])
        validator = jsonschema.Draft202012Validator(schema)
        self.assertTrue(validator.is_valid(report), list(validator.iter_errors(report)))
        report["meshes"][0]["parts"][0]["storedKeys"]["reflected"] = -1
        self.assertFalse(validator.is_valid(report))


if __name__ == "__main__":
    unittest.main()
