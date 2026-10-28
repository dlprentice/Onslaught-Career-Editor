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
    def test_empty_part_name_is_not_the_preview_generated_label(self) -> None:
        part = fixtures._catalog_part(0, name="", geometry=True)
        stream = fixtures._catalog_stream(parts=[part])
        self.assertEqual(catalog.parse_cmsh_stream(stream).file_parts()[0].name, "part-0")
        [row] = catalog.analyse_stream(stream, source_name="authored", source_sha256="a" * 64)["parts"]
        self.assertEqual((row["name"], row["nameStatus"], row["nameBytesSha256"]),
                         ("", "empty", hashlib.sha256(b"").hexdigest()))

    def test_bounded_mesh_name_refuses_to_consume_following_pointer(self) -> None:
        stream = bytearray(fixtures._catalog_stream())
        start = 8 + catalog.MESH_NAME_OFFSET
        stream[start:start + catalog.MESH_NAME_BYTES] = b"A" * catalog.MESH_NAME_BYTES
        # The following bounding-box pointer begins with NUL. A 304-byte
        # search would misidentify that byte as the 300-byte name's terminator.
        stream[start + catalog.MESH_NAME_BYTES:start + catalog.MESH_NAME_BYTES + 4] = b"\0ABC"
        self.assertEqual(catalog.parse_cmsh_stream(bytes(stream)).name, "A" * 300)
        report = catalog.analyse_stream(bytes(stream), source_name="authored", source_sha256="a" * 64)
        self.assertEqual((report["meshName"], report["meshNameStatus"], report["meshNameBytesSha256"]),
                         (None, "unterminated", None))

    def test_non_utf8_mesh_name_is_unknown_not_replacement_text(self) -> None:
        hashes = []
        for raw_name in (b"\xffThing", b"\xfeThing"):
            stream = bytearray(fixtures._catalog_stream())
            start = 8 + catalog.MESH_NAME_OFFSET
            stream[start:start + catalog.MESH_NAME_BYTES] = (raw_name + b"\0").ljust(catalog.MESH_NAME_BYTES, b"\0")
            self.assertIn("\ufffd", catalog.parse_cmsh_stream(bytes(stream)).name)
            report = catalog.analyse_stream(bytes(stream), source_name="authored", source_sha256="a" * 64)
            self.assertIsNone(report["meshName"])
            self.assertEqual(report["meshNameStatus"], "invalid-utf8")
            self.assertEqual(report["meshNameBytesSha256"], hashlib.sha256(raw_name).hexdigest())
            self.assertNotIn("\ufffd", json.dumps(report, ensure_ascii=False))
            hashes.append(report["meshNameBytesSha256"])
        self.assertNotEqual(*hashes)

    def test_utf8_part_name_has_exact_byte_hash_and_unknown_encoding_context(self) -> None:
        part = bytearray(fixtures._catalog_part(0, name="", geometry=True))
        start = 16 + catalog.PART_NAME_OFFSET  # MESP and CMSP chunk headers
        raw_name = b"Caf\xc3\xa9"
        part[start:start + catalog.PART_NAME_BYTES] = (raw_name + b"\0").ljust(catalog.PART_NAME_BYTES, b"\0")
        stream = fixtures._catalog_stream(parts=[bytes(part)])
        [row] = catalog.analyse_stream(stream, source_name="authored", source_sha256="a" * 64)["parts"]
        self.assertEqual((row["name"], row["nameStatus"], row["nameBytesSha256"]),
                         ("Café", "utf8-decoded", hashlib.sha256(raw_name).hexdigest()))
        part[start:start + catalog.PART_NAME_BYTES] = (b"bad\xff\0").ljust(catalog.PART_NAME_BYTES, b"\0")
        with self.assertRaises(ValueError):
            catalog.analyse_stream(fixtures._catalog_stream(parts=[bytes(part)]),
                                   source_name="authored", source_sha256="a" * 64)

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

    def test_selected_source_metadata_is_deterministic_and_emitted_only(self) -> None:
        before = self.source.read_bytes()
        args = ["--mesh", str(self.source), "--stdout"]
        rc, output, _ = self.run_cli(args)
        self.assertEqual(0, rc)
        report = json.loads(output)
        self.assertTrue(report["generatedRetailDerived"])
        self.assertEqual(catalog.SCHEMA, report["schema"])
        [mesh] = report["meshes"]
        self.assertEqual(hashlib.sha256(before).hexdigest(), mesh["source"]["archiveSha256"])
        self.assertEqual(1, mesh["parts"][0]["storedKeys"]["reflected"])
        self.assertEqual(output.encode("utf-8"), catalog.report_bytes([self.source]))
        self.assertEqual(report, catalog.report_for([self.source]))
        self.assertEqual((0, output), self.run_cli(args)[:2])
        self.assertFalse(self.output.exists())
        self.assertEqual(before, self.source.read_bytes())

    def test_process_cli_reads_authored_input_and_refuses_parent_traversal(self) -> None:
        script = catalog.ROOT / "tools/model_transform_catalog.py"
        good = subprocess.run([sys.executable, str(script), "--mesh", str(self.source), "--stdout"],
                              capture_output=True, text=True, timeout=10)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout)["meshes"][0]["source"]["archiveSha256"],
                         hashlib.sha256(self.source.read_bytes()).hexdigest())
        bad = self.source.parent / ".." / "input" / self.source.name
        refused = subprocess.run([sys.executable, str(script), "--mesh", str(bad), "--stdout"],
                                 capture_output=True, text=True, timeout=10)
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual("", refused.stdout)
        self.assertFalse(self.output.exists())

    def test_process_cli_opens_no_output_file(self) -> None:
        # The real CLI runs under an audit hook that refuses Python write-open calls. stdout is
        # the pipe inherited from this parent, not a file selected or opened by the tool.
        wrapper = """
import os, runpy, sys
def audit(event, args):
    if event == "open":
        path, mode, flags = args
        if ((isinstance(mode, str) and any(c in mode for c in "wax+")) or
            (isinstance(flags, int) and
             ((flags & os.O_ACCMODE) != os.O_RDONLY or flags & (os.O_CREAT | os.O_TRUNC | os.O_APPEND)))):
            raise RuntimeError("unexpected write-open by model CLI")
sys.addaudithook(audit)
if os.environ.get("MODEL_CATALOG_AUDIT_NEGATIVE"):
    os.open(os.environ["MODEL_CATALOG_AUDIT_NEGATIVE"], os.O_WRONLY | os.O_CREAT, 0o600)
sys.argv = [sys.argv[1], "--mesh", sys.argv[2], "--stdout"]
sys.path.insert(0, os.path.dirname(sys.argv[0]))
runpy.run_path(sys.argv[0], run_name="__main__")
"""
        script = catalog.ROOT / "tools/model_transform_catalog.py"
        before = {path.relative_to(self.root) for path in self.root.rglob("*")}
        env = dict(os.environ)
        env.pop("PYTHONDONTWRITEBYTECODE", None)  # CLI itself must suppress import bytecode writes.
        env.pop("MODEL_CATALOG_AUDIT_NEGATIVE", None)
        result = subprocess.run([sys.executable, "-c", wrapper, str(script), str(self.source)],
                                env=env, capture_output=True, text=True, timeout=10)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(json.loads(result.stdout)["meshes"][0]["source"]["archiveSha256"],
                         hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual(before, {path.relative_to(self.root) for path in self.root.rglob("*")})
        would_create = self.root / "unexpected-output.json"
        env["MODEL_CATALOG_AUDIT_NEGATIVE"] = str(would_create)
        negative = subprocess.run([sys.executable, "-c", wrapper, str(script), str(self.source)],
                                  env=env, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(0, negative.returncode)
        self.assertIn("unexpected write-open by model CLI", negative.stderr)
        self.assertEqual("", negative.stdout)
        self.assertFalse(would_create.exists())

    def test_invalid_and_unsafe_inputs_publish_no_output(self) -> None:
        for kind in ("truncated", "link", "hardlink", "missing"):
            with self.subTest(kind=kind):
                source = self.root / "input" / kind
                if kind == "truncated": source.write_bytes(aya(make_stream()[:-10]))
                elif kind == "link": source.symlink_to(self.source.name)
                elif kind == "hardlink": os.link(self.source, source)
                rc, output, _ = self.run_cli(["--mesh", str(source), "--stdout"])
                self.assertNotEqual(0, rc)
                self.assertEqual("", output)
                self.assertFalse(self.output.exists())
                if kind == "hardlink":
                    with self.assertRaisesRegex(ValueError, "hard link"):
                        catalog.report_for([source])
                if kind == "hardlink": source.unlink()  # authored hard link, so the next case can use the source

    def test_duplicate_selection_and_paths_with_parent_component_refuse(self) -> None:
        with self.assertRaisesRegex(ValueError, "more than once"):
            catalog.report_for([self.source, self.source])
        with self.assertRaisesRegex(ValueError, "parent path component"):
            catalog.report_for([self.source.parent / ".." / "input" / self.source.name])

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
        rc, _, _ = self.run_cli(["--mesh", str(ambiguous), "--stdout"])
        self.assertNotEqual(0, rc)
        self.assertFalse(self.output.exists())

    def test_symlinked_input_directory_refuses_both_callable_and_cli(self) -> None:
        link = self.root / "input-link"
        link.symlink_to(self.source.parent, target_is_directory=True)
        selected = link / self.source.name
        with self.assertRaises((ValueError, OSError)):
            catalog.report_for([selected])
        rc, _, _ = self.run_cli(["--mesh", str(selected), "--stdout"])
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
            rc, _, _ = self.run_cli(["--mesh", str(self.source), "--stdout"])
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
            rc, _, _ = self.run_cli(["--mesh", str(self.source), "--stdout"])
        self.assertNotEqual(0, rc)
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(hasattr(os, "O_PATH") and hasattr(os, "mkfifo"), "Linux O_PATH and FIFO required")
    def test_source_replaced_after_analysis_refuses_cli_emission(self) -> None:
        original = catalog._report_for
        old = self.source.with_name("before-publication.aya")

        def replace_after_read(paths):
            report = original(paths)
            self.source.rename(old)
            os.mkfifo(self.source)
            return report

        with mock.patch.object(catalog, "_report_for", side_effect=replace_after_read):
            rc, output, _ = self.run_cli(["--mesh", str(self.source), "--stdout"])
        self.assertNotEqual(0, rc)
        self.assertEqual("", output)
        self.assertFalse(self.output.exists())

    def test_source_replaced_during_final_check_refuses_cli_emission(self) -> None:
        original = catalog._check_input_bindings
        old = self.source.with_name("before-final-check.aya")
        calls = 0

        def replace_on_final_check(bindings):
            nonlocal calls
            calls += 1
            self.source.rename(old)
            self.source.write_bytes(aya(make_stream([REFLECTION])))
            return original(bindings)

        with mock.patch.object(catalog, "_check_input_bindings", side_effect=replace_on_final_check):
            rc, output, _ = self.run_cli(["--mesh", str(self.source), "--stdout"])
        self.assertEqual(calls, 1)
        self.assertNotEqual(0, rc)
        self.assertEqual("", output)
        self.assertFalse(self.output.exists())

    def test_callable_rechecks_each_selected_file_before_return(self) -> None:
        original = catalog._report_for
        old = self.source.with_name("before-api-return.aya")

        def replace_after_analysis(paths):
            result = original(paths)
            self.source.rename(old)
            self.source.write_bytes(aya(make_stream([REFLECTION])))
            return result

        with mock.patch.object(catalog, "_report_for", side_effect=replace_after_analysis):
            with self.assertRaisesRegex(ValueError, "changed before report emission"):
                catalog.report_bytes([self.source])
        self.source.unlink()
        old.rename(self.source)
        with mock.patch.object(catalog, "_report_for", side_effect=replace_after_analysis):
            with self.assertRaisesRegex(ValueError, "changed before report emission"):
                catalog.report_for([self.source])

    def test_cli_never_uses_shared_blocking_protected_file_opener(self) -> None:
        with mock.patch.object(safe_generated_output, "_HeldFile", side_effect=AssertionError("unexpected source open")):
            rc, output, error = self.run_cli(["--mesh", str(self.source), "--stdout"])
        self.assertEqual(0, rc, error)
        self.assertEqual(catalog.SCHEMA, json.loads(output)["schema"])
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(hasattr(os, "O_PATH") and hasattr(os, "mkfifo"), "Linux O_PATH and FIFO required")
    def test_source_directory_replaced_with_fifo_before_emission_refuses(self) -> None:
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
            rc, output, _ = self.run_cli(["--mesh", str(self.source), "--stdout"])
        self.assertNotEqual(0, rc)
        self.assertEqual("", output)
        self.assertFalse(self.output.exists())

    def test_cli_requires_explicit_stdout_and_rejects_legacy_output_paths(self) -> None:
        rc, output, _ = self.run_cli(["--mesh", str(self.source)])
        self.assertNotEqual(0, rc)
        self.assertEqual("", output)
        for target in (self.source.parent / "report.json", self.output):
            with self.subTest(target=target):
                rc, output, _ = self.run_cli(["--mesh", str(self.source), "--stdout", "--out", str(target)])
                self.assertNotEqual(0, rc)
                self.assertEqual("", output)
                self.assertFalse(target.exists())
        script = catalog.ROOT / "tools/model_transform_catalog.py"
        rejected = subprocess.run([sys.executable, str(script), "--mesh", str(self.source),
                                   "--stdout", "--out", str(self.source.parent / "report.json")],
                                  capture_output=True, text=True, timeout=10)
        self.assertNotEqual(0, rejected.returncode)
        self.assertEqual("", rejected.stdout)
        self.assertFalse((self.source.parent / "report.json").exists())

    def test_total_frame_and_part_limits_refuse_without_output(self) -> None:
        for field, limit in (("MAX_TOTAL_VIRTUAL_FRAMES", 1), ("MAX_TOTAL_PARTS", 0)):
            with self.subTest(field=field), mock.patch.object(catalog, field, limit):
                rc, output, _ = self.run_cli(["--mesh", str(self.source), "--stdout"])
                self.assertNotEqual(0, rc)
                self.assertEqual("", output)
                self.assertFalse(self.output.exists())

    def test_source_byte_limit_refuses_before_reading_or_emission(self) -> None:
        with mock.patch.object(catalog, "MAX_COMPRESSED_BYTES", 1):
            with mock.patch.object(catalog.os, "read", side_effect=AssertionError("must reject before reading")):
                with self.assertRaisesRegex(ValueError, "compressed-byte limit"):
                    catalog.report_for([self.source])
            rc, output, _ = self.run_cli(["--mesh", str(self.source), "--stdout"])
        self.assertNotEqual(0, rc)
        self.assertEqual("", output)
        self.assertFalse(self.output.exists())

    def test_legacy_output_path_with_symlinked_parent_is_refused(self) -> None:
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        (self.root / "link").symlink_to(elsewhere, target_is_directory=True)
        target = self.root / "link" / "report.json"
        rc, output, _ = self.run_cli(["--mesh", str(self.source), "--stdout", "--out", str(target)])
        self.assertNotEqual(0, rc)
        self.assertEqual("", output)
        self.assertFalse((elsewhere / "report.json").exists())

    def test_other_platforms_refuse_before_emission(self) -> None:
        with mock.patch.object(catalog.sys, "platform", "win32"):
            rc, output, _ = self.run_cli(["--mesh", str(self.source), "--stdout"])
        self.assertEqual(2, rc)
        self.assertEqual("", output)
        self.assertFalse(self.output.exists())

    def test_schema_matches_authored_report_when_validator_available(self) -> None:
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema = json.loads((catalog.ROOT / "tools/model_transform_catalog.v2.schema.json").read_text())
        report = catalog.report_for([self.source])
        validator = jsonschema.Draft202012Validator(schema)
        self.assertTrue(validator.is_valid(report), list(validator.iter_errors(report)))
        legacy = json.loads(json.dumps(report))
        legacy["schema"] = "onslaught.model-transform-catalog.v1"
        legacy["basis"].pop("nameInterpretation")
        for mesh in legacy["meshes"]:
            mesh.pop("meshNameStatus")
            mesh.pop("meshNameBytesSha256")
            for part in mesh["parts"]:
                part.pop("nameStatus")
                part.pop("nameBytesSha256")
        legacy_schema = json.loads((catalog.ROOT / "tools/model_transform_catalog.schema.json").read_text())
        legacy_validator = jsonschema.Draft202012Validator(legacy_schema)
        self.assertTrue(legacy_validator.is_valid(legacy), list(legacy_validator.iter_errors(legacy)))
        self.assertFalse(validator.is_valid(legacy))
        broken = json.loads(json.dumps(report))
        broken["meshes"][0]["meshNameStatus"] = "invented"
        self.assertFalse(validator.is_valid(broken))
        broken = json.loads(json.dumps(report))
        broken["meshes"][0]["parts"][0]["nameBytesSha256"] = "bad"
        self.assertFalse(validator.is_valid(broken))
        report["meshes"][0]["parts"][0]["storedKeys"]["reflected"] = -1
        self.assertFalse(validator.is_valid(report))

    def test_v2_schema_accepts_explicit_unknown_mesh_names(self) -> None:
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema = json.loads((catalog.ROOT / "tools/model_transform_catalog.v2.schema.json").read_text())
        validator = jsonschema.Draft202012Validator(schema)
        for raw, status in ((b"\xffThing\0", "invalid-utf8"), (b"A" * 300, "unterminated")):
            with self.subTest(status=status):
                stream = bytearray(make_stream())
                start = 8 + catalog.MESH_NAME_OFFSET
                stream[start:start + 300] = raw.ljust(300, b"\0")
                self.source.write_bytes(aya(bytes(stream)))
                report = catalog.report_for([self.source])
                self.assertEqual(report["meshes"][0]["meshNameStatus"], status)
                self.assertTrue(validator.is_valid(report), list(validator.iter_errors(report)))


if __name__ == "__main__":
    unittest.main()
