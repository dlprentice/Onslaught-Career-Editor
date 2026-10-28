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
import subprocess
import sys
import tempfile
import unittest
import zlib
from unittest import mock

import cmsh_animation_usage_census_tests as fixtures
import model_transform_catalog as catalog
import safe_generated_output


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

    def test_process_cli_reads_authored_input_and_refuses_parent_traversal(self) -> None:
        script = catalog.ROOT / "tools/model_transform_catalog.py"
        good = subprocess.run([sys.executable, str(script), "--mesh", str(self.source), "--out", str(self.output)],
                              capture_output=True, text=True, timeout=10)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(self.output.read_text())["meshes"][0]["source"]["archiveSha256"],
                         hashlib.sha256(self.source.read_bytes()).hexdigest())
        bad_output = self.root / "reports" / "parent.json"
        bad = self.source.parent / ".." / "input" / self.source.name
        refused = subprocess.run([sys.executable, str(script), "--mesh", str(bad), "--out", str(bad_output)],
                                 capture_output=True, text=True, timeout=10)
        self.assertNotEqual(refused.returncode, 0)
        self.assertFalse(bad_output.exists())

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
                if kind == "hardlink":
                    with self.assertRaisesRegex(ValueError, "hard link"):
                        catalog.report_for([source])
                if kind == "hardlink": source.unlink()  # authored hard link, so the next case can use the source

    def test_duplicate_selection_and_paths_with_parent_component_refuse(self) -> None:
        with self.assertRaisesRegex(ValueError, "more than once"):
            catalog.report_for([self.source, self.source])
        self.assertFalse(catalog.output_allowed(catalog.ROOT / "local-data" / "x" / ".." / "report.json"))
        self.assertFalse(catalog.output_allowed(catalog.ROOT / "report.json"))

    def test_symlink_then_parent_refuses_instead_of_normalizing_to_another_file(self) -> None:
        other = self.root / "other"
        (other / "child").mkdir(parents=True)
        other_source = other / self.source.name
        other_source.write_bytes(aya(make_stream([REFLECTION])))
        (self.source.parent / "alias").symlink_to(other / "child", target_is_directory=True)
        ambiguous = self.source.parent / "alias" / ".." / self.source.name
        self.assertEqual(os.stat(ambiguous).st_ino, other_source.stat().st_ino)
        self.assertNotEqual(self.source.read_bytes(), other_source.read_bytes())
        with self.assertRaises(ValueError):
            catalog.report_for([ambiguous])
        rc, _, _ = self.run_cli(["--mesh", str(ambiguous), "--out", str(self.output)])
        self.assertNotEqual(0, rc)
        self.assertFalse(self.output.exists())

    def test_symlinked_input_directory_refuses_both_callable_and_cli(self) -> None:
        link = self.root / "input-link"
        link.symlink_to(self.source.parent, target_is_directory=True)
        selected = link / self.source.name
        with self.assertRaises((ValueError, OSError)):
            catalog.report_for([selected])
        rc, _, _ = self.run_cli(["--mesh", str(selected), "--out", str(self.output)])
        self.assertNotEqual(0, rc)
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(hasattr(os, "O_PATH") and hasattr(os, "mkfifo"), "Linux O_PATH and FIFO required")
    def test_selected_file_swapped_to_fifo_never_opens_fifo_for_read(self) -> None:
        old = self.source.with_name("before-swap.aya")
        real_open = os.open
        swapped = False
        proc_opens = []

        def swap_before_final_open(path, flags, *args, **kwargs):
            nonlocal swapped
            if os.fspath(path) == self.source.name and flags & os.O_PATH and not swapped:
                self.source.rename(old)
                os.mkfifo(self.source)
                swapped = True
            if os.fspath(path).startswith("/proc/self/fd/"):
                proc_opens.append(os.fspath(path))
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(catalog.os, "open", side_effect=swap_before_final_open):
            with self.assertRaises((ValueError, OSError)):
                catalog.report_for([self.source])
        self.assertTrue(swapped)
        self.assertEqual(proc_opens, [], "FIFO must be rejected before opening an input for reading")

    @unittest.skipUnless(hasattr(os, "O_PATH") and hasattr(os, "mkfifo"), "Linux O_PATH and FIFO required")
    def test_fifo_swap_is_also_refused_by_cli_without_publication(self) -> None:
        old = self.source.with_name("before-cli-open.aya")
        real_open = os.open
        swapped = False

        def swap_before_final_open(path, flags, *args, **kwargs):
            nonlocal swapped
            if os.fspath(path) == self.source.name and flags & os.O_PATH and not swapped:
                self.source.rename(old)
                os.mkfifo(self.source)
                swapped = True
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(catalog.os, "open", side_effect=swap_before_final_open):
            rc, _, _ = self.run_cli(["--mesh", str(self.source), "--out", str(self.output)])
        self.assertTrue(swapped)
        self.assertNotEqual(0, rc)
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(hasattr(os, "O_PATH"), "Linux O_PATH required")
    def test_in_place_same_length_edit_with_restored_mtime_refuses(self) -> None:
        before = self.source.stat()
        real_read = os.read
        changed = False

        def change_after_read(fd, count):
            nonlocal changed
            data = real_read(fd, count)
            if data and not changed:
                changed = True
                with self.source.open("r+b") as handle:
                    handle.seek(-1, os.SEEK_END)
                    byte = handle.read(1)
                    handle.seek(-1, os.SEEK_END)
                    handle.write(bytes([byte[0] ^ 1]))
                os.utime(self.source, ns=(before.st_atime_ns, before.st_mtime_ns))
            return data

        with mock.patch.object(catalog.os, "read", side_effect=change_after_read):
            with self.assertRaisesRegex(ValueError, "changed during reading"):
                catalog.report_for([self.source])
        self.assertTrue(changed)

    @unittest.skipUnless(hasattr(os, "O_PATH"), "Linux O_PATH required")
    def test_regular_path_replacement_during_read_refuses(self) -> None:
        old = self.source.with_name("before-read-replacement.aya")
        replacement = self.source.with_name("replacement.aya")
        replacement.write_bytes(aya(make_stream([REFLECTION])))
        real_read = os.read
        changed = False

        def replace_after_read(fd, count):
            nonlocal changed
            data = real_read(fd, count)
            if data and not changed:
                changed = True
                self.source.rename(old)
                replacement.rename(self.source)
            return data

        with mock.patch.object(catalog.os, "read", side_effect=replace_after_read):
            with self.assertRaisesRegex(ValueError, "changed during reading|path changed during reading"):
                catalog.report_for([self.source])
        self.assertTrue(changed)

    def test_callable_and_cli_refuse_when_safe_directory_open_is_unavailable(self) -> None:
        with mock.patch.object(catalog, "HAS_OPEN_DIR_FD", False):
            with self.assertRaisesRegex(ValueError, "descriptor-relative"):
                catalog.report_for([self.source])
            rc, _, _ = self.run_cli(["--mesh", str(self.source), "--out", str(self.output)])
        self.assertNotEqual(0, rc)
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(hasattr(os, "O_PATH") and hasattr(os, "mkfifo"), "Linux O_PATH and FIFO required")
    def test_source_replaced_after_analysis_refuses_cli_publication(self) -> None:
        original = catalog._report_for
        old = self.source.with_name("before-publication.aya")

        def replace_after_read(paths):
            report = original(paths)
            self.source.rename(old)
            os.mkfifo(self.source)
            return report

        with mock.patch.object(catalog, "_report_for", side_effect=replace_after_read):
            rc, _, _ = self.run_cli(["--mesh", str(self.source), "--out", str(self.output)])
        self.assertNotEqual(0, rc)
        self.assertFalse(self.output.exists())

    def test_source_replaced_during_staging_refuses_cli_publication(self) -> None:
        original = catalog._check_input_bindings
        old = self.source.with_name("before-staging.aya")
        calls = 0

        def replace_on_final_check(bindings):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.source.rename(old)
                self.source.write_bytes(aya(make_stream([REFLECTION])))
            return original(bindings)

        with mock.patch.object(catalog, "_check_input_bindings", side_effect=replace_on_final_check):
            rc, _, _ = self.run_cli(["--mesh", str(self.source), "--out", str(self.output)])
        self.assertEqual(calls, 2)
        self.assertNotEqual(0, rc)
        self.assertFalse(self.output.exists())

    def test_cli_never_uses_shared_blocking_protected_file_opener(self) -> None:
        with mock.patch.object(safe_generated_output, "_HeldFile", side_effect=AssertionError("unexpected source open")):
            rc, _, error = self.run_cli(["--mesh", str(self.source), "--out", str(self.output)])
        self.assertEqual(0, rc, error)
        self.assertTrue(self.output.exists())

    @unittest.skipUnless(hasattr(os, "O_PATH") and hasattr(os, "mkfifo"), "Linux O_PATH and FIFO required")
    def test_source_directory_replaced_with_fifo_before_publication_refuses(self) -> None:
        original = catalog._report_for
        source_dir = self.source.parent
        old = self.root / "before-directory-swap"

        def replace_after_read(paths):
            result = original(paths)
            source_dir.rename(old)
            os.mkfifo(source_dir)
            return result

        with mock.patch.object(catalog, "_report_for", side_effect=replace_after_read), \
                mock.patch.object(safe_generated_output, "_HeldFile", side_effect=AssertionError("unexpected source open")):
            rc, _, _ = self.run_cli(["--mesh", str(self.source), "--out", str(self.output)])
        self.assertNotEqual(0, rc)
        self.assertFalse(self.output.exists())

    def test_report_output_cannot_share_a_selected_source_directory(self) -> None:
        output = self.source.parent / "report.json"
        rc, _, _ = self.run_cli(["--mesh", str(self.source), "--out", str(output)])
        self.assertNotEqual(0, rc)
        self.assertFalse(output.exists())

    def test_total_frame_and_part_limits_refuse_without_output(self) -> None:
        for field, limit in (("MAX_TOTAL_VIRTUAL_FRAMES", 1), ("MAX_TOTAL_PARTS", 0)):
            with self.subTest(field=field), mock.patch.object(catalog, field, limit):
                rc, _, _ = self.run_cli(["--mesh", str(self.source), "--out", str(self.output)])
                self.assertNotEqual(0, rc)
                self.assertFalse(self.output.exists())

    def test_source_byte_limit_refuses_before_reading_or_publication(self) -> None:
        with mock.patch.object(catalog, "MAX_COMPRESSED_BYTES", 1):
            with mock.patch.object(catalog.os, "read", side_effect=AssertionError("must reject before reading")):
                with self.assertRaisesRegex(ValueError, "compressed-byte limit"):
                    catalog.report_for([self.source])
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
