#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Authored catalog projection controls; no game files or asset conversion."""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch
import zlib

import export_asset_catalog as catalog
import aya_texture_fidelity_census as packed
from aya_texture_fidelity_census_tests import texture_payload
from dds_census_tests import dds
from safe_generated_output import UnsafeGeneratedOutputError


def envelope(payload, level=6):
    member = zlib.compress(payload, level)
    return len(member).to_bytes(4, "little") + member


class CatalogExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / "bundle"
        self.bundle.mkdir()
        self.packed = {key: [] for key in ("text_texture_refs", "gdie_texture_refs",
                                         "reference_mesh_refs", "gdie_mesh_refs")}

    def rows(self, status, *, output=True):
        row = {"input": str(self.root / "meshes/m_fixture.aya"), "status": status}
        if output:
            row["output"] = str(self.bundle / "exports/fixture.fbx")
        return [row]

    def test_failed_export_never_advertises_missing_or_stale_output(self):
        for exists in (False, True):
            if exists:
                output = self.bundle / "exports/fixture.fbx"
                output.parent.mkdir()
                output.write_bytes(b"a stale unrelated output is not proof")
            row = catalog.build_loose_mesh_catalog(self.rows("error"), self.packed, self.root, self.bundle)[0]
            self.assertEqual(0, row["export_fbx_count"])
            self.assertEqual([], row["export_fbx_paths"])
            self.assertEqual("failed", row["export_records"][0]["verification_status"])
            self.assertEqual(1, row["source_aya_count"])

    def test_legacy_success_skip_and_absent_status_remain_unverified(self):
        for status in ("ok", "skipped_existing", None, "verified"):
            with self.subTest(status=status):
                row = catalog.build_texture_catalog(self.rows(status), self.packed, self.root, self.bundle)[0]
                self.assertEqual([], row["export_png_paths"])
                self.assertEqual(0, row["export_png_count"])
                self.assertEqual("unverified", row["export_records"][0]["verification_status"])
                self.assertIsNone(row["export_records"][0]["verified_output_path"])

    def test_supplied_verification_words_and_digest_cannot_self_attest_output(self):
        raw = self.rows("ok")[0]
        raw.update(verified=True, output_sha256="a" * 64, source_sha256="b" * 64)
        attempt = catalog.legacy_export_attempt(raw, self.bundle, "fbx")
        self.assertEqual("unverified", attempt["verification_status"])
        self.assertIsNone(attempt["verified_output_path"])

    def test_missing_output_retains_the_failed_source(self):
        row = catalog.build_loose_mesh_catalog(self.rows("error", output=False), self.packed,
                                               self.root, self.bundle)[0]
        self.assertEqual("mesh:fixture", row["catalog_id"])
        self.assertIsNone(row["export_records"][0]["requested_output_path"])
        self.assertEqual(1, row["source_aya_count"])

    def test_embedded_output_is_null_until_bound_evidence_exists(self):
        row = catalog.build_embedded_mesh_catalog(self.rows("ok"), self.root, self.bundle)[0]
        self.assertIsNone(row["export_fbx_path"])
        self.assertEqual("exports\\fixture.fbx", row["export_records"][0]["requested_output_path"])

    def test_even_failed_requested_paths_must_stay_in_bundle(self):
        raw = self.rows("error")[0]
        raw["output"] = str(self.root / "outside.fbx")
        with self.assertRaisesRegex(SystemExit, "outside --bundle-root"):
            catalog.build_loose_mesh_catalog([raw], self.packed, self.root, self.bundle)

    def test_reordered_attempts_preserve_canonical_catalog(self):
        rows = self.rows("ok") + self.rows("error") + self.rows("skipped_existing")
        expected = catalog.build_loose_mesh_catalog(rows, self.packed, self.root, self.bundle)
        self.assertEqual(expected, catalog.build_loose_mesh_catalog(list(reversed(rows)), self.packed,
                                                                   self.root, self.bundle))
        self.assertEqual(3, len(expected[0]["export_records"]))

    def test_names_do_not_become_visually_verified_descriptions(self):
        for row in (catalog.build_texture_catalog(self.rows("ok"), self.packed, self.root, self.bundle)[0],
                    catalog.build_loose_mesh_catalog(self.rows("ok"), self.packed, self.root, self.bundle)[0],
                    catalog.build_embedded_mesh_catalog(self.rows("ok"), self.root, self.bundle)[0]):
            self.assertIsNone(row["description"])
            self.assertEqual("not-visually-reviewed", row["description_status"])

    def test_alias_union_does_not_depend_on_source_order(self):
        rows = self.rows("ok")
        other = dict(rows[0], input=str(self.root / "meshes/fixture.aya"))
        one = catalog.build_loose_mesh_catalog(rows + [other], self.packed, self.root, self.bundle)
        two = catalog.build_loose_mesh_catalog([other] + rows, self.packed, self.root, self.bundle)
        self.assertEqual(one, two)
        self.assertEqual(["fixture", "m_fixture"], one[0]["aliases"])

    def test_embedded_legacy_id_collisions_remain_separate_and_explicit(self):
        rows = [dict(self.rows("ok")[0], input=str(self.root / prefix / "same.aya/body00.cmsbody"))
                for prefix in ("one", "two")]
        one = catalog.build_embedded_mesh_catalog(rows, self.root, self.bundle)
        two = catalog.build_embedded_mesh_catalog(list(reversed(rows)), self.root, self.bundle)
        self.assertEqual(one, two)
        self.assertEqual(2, len(one))
        self.assertTrue(all(row["logical_id_ambiguous"] for row in one))
        self.assertEqual(2, len({row["source_body_path"] for row in one}))


class CatalogSourceInspectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.sources = self.repo / "sources"
        self.sources.mkdir()
        self.bundle = self.repo / "bundle"
        self.bundle.mkdir()
        self.packed = {key: [] for key in ("text_texture_refs", "gdie_texture_refs",
                                         "reference_mesh_refs", "gdie_mesh_refs")}
        self.inputs = {}

    def source(self, name, data):
        path = self.sources / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def row(self, path, status="error"):
        return {"input": str(path), "output": str(self.bundle / "attempt.bin"), "status": status}

    def texture_catalog(self, paths):
        manifest = [self.row(path) for path in paths]
        rows = catalog.build_texture_catalog(manifest, self.packed, self.repo, self.bundle)
        self.inputs[id(rows)] = (rows, manifest)
        return rows

    def inspect(self, textures=(), meshes=(), embedded=(), *, texture_sources=None,
                mesh_sources=(), embedded_sources=()):
        if texture_sources is None:
            texture_sources = self.inputs[id(textures)][1] if textures else []
        return catalog.inspect_catalog_sources(list(textures), list(meshes), list(embedded),
                                               source_root=self.sources, repo_root=self.repo,
                                               source_manifests=(list(texture_sources), list(mesh_sources), list(embedded_sources)))

    def test_identical_payload_repacked_at_two_paths_has_one_variant_two_occurrences(self):
        payload = dds(4, 4)
        paths = [self.source("textures/foo.tga.aya", envelope(payload, 0)),
                 self.source("dxtntextures/mustbe_foo.tga.aya", envelope(payload, 9))]
        rows = self.texture_catalog(paths)
        selection = self.inspect(rows)
        self.assertEqual("explicit-manifest-source-selection-not-full-aya-universe", selection["scope"])
        self.assertEqual(1, rows[0]["exact_variant_count"])
        self.assertEqual(2, rows[0]["occurrence_count"])
        self.assertEqual(2, len({row["occurrence_id"] for row in rows[0]["occurrences"]}))
        self.assertEqual(2, len({row["source_identity"]["sha256"] for row in rows[0]["occurrences"]}))
        identity = rows[0]["variants"][0]["payload_identity"]
        self.assertEqual({"length": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}, identity)
        self.assertEqual(["foo.tga", "mustbe_foo.tga"], rows[0]["aliases"])
        self.assertEqual([], rows[0]["export_png_paths"])

    def test_identical_names_with_distinct_payloads_remain_two_variants(self):
        paths = [self.source("textures/foo.tga.aya", envelope(dds(4, 4))),
                 self.source("dxtntextures/foo.tga.aya", envelope(dds(4, 4, payload=b"\x01" * 8)))]
        one, two = self.texture_catalog(paths), self.texture_catalog(list(reversed(paths)))
        self.assertEqual(self.inspect(one), self.inspect(two))
        self.assertEqual(one, two)
        self.assertEqual(2, one[0]["exact_variant_count"])
        self.assertEqual(2, one[0]["occurrence_count"])

    def test_source_hash_is_measured_and_does_not_trust_manifest_words(self):
        path = self.source("textures/foo.tga.aya", envelope(dds(4, 4)))
        raw = dict(self.row(path, "ok"), source_sha256="a" * 64, verified=True)
        rows = catalog.build_texture_catalog([raw], self.packed, self.repo, self.bundle)
        self.inspect(rows, texture_sources=[raw])
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), rows[0]["occurrences"][0]["source_identity"]["sha256"])
        self.assertEqual([], rows[0]["export_png_paths"])
        self.assertIsNone(rows[0]["description"])

    def test_selection_namespace_and_occurrences_are_root_location_independent(self):
        path = self.source("textures/foo.tga.aya", envelope(dds(4, 4)))
        one = self.texture_catalog([path])
        first = self.inspect(one)
        other_root = self.repo / "relocated"
        other = other_root / "textures/foo.tga.aya"
        other.parent.mkdir(parents=True)
        other.write_bytes(path.read_bytes())
        two = self.texture_catalog([other])
        second = catalog.inspect_catalog_sources(two, [], [], source_root=other_root, repo_root=self.repo,
                                                  source_manifests=(self.inputs[id(two)][1], [], []))
        self.assertEqual(first["selection_namespace"], second["selection_namespace"])
        self.assertEqual(one[0]["occurrences"], two[0]["occurrences"])
        self.assertEqual(one[0]["variants"], two[0]["variants"])

    def test_missing_malformed_and_unsupported_sources_keep_explicit_dispositions(self):
        unsupported = bytearray(dds(4, 4))
        unsupported[84:88] = b"DX10"
        paths = [self.sources / "missing.tga.aya",
                 self.source("bad.tga.aya", b"malformed AYA"),
                 self.source("unsupported.dds", bytes(unsupported))]
        rows = self.texture_catalog(paths)
        result = self.inspect(rows)
        self.assertEqual({"malformed": 1, "unavailable": 1, "unsupported": 1}, result["status_counts"])
        missing = next(row for row in rows if row["canonical_ref"] == "missing.tga")
        self.assertEqual(1, missing["occurrence_count"])
        self.assertIsNone(missing["occurrences"][0]["occurrence_id"])
        self.assertIsNone(missing["occurrences"][0]["source_identity"])
        self.assertTrue(all(not row["export_png_paths"] for row in rows))

    def test_source_links_parent_links_hardlinks_and_root_escape_are_rejected(self):
        good = self.source("textures/good.tga.aya", envelope(dds(4, 4)))
        leaf = self.sources / "leaf.tga.aya"
        leaf.symlink_to(good)
        parent = self.sources / "linked"
        parent.symlink_to(good.parent, target_is_directory=True)
        outside = self.repo / "outside.tga.aya"
        outside.write_bytes(good.read_bytes())
        hard = self.sources / "hard.tga.aya"
        os.link(good, hard)
        rows = self.texture_catalog([leaf, parent / good.name, hard, outside])
        result = self.inspect(rows)
        self.assertEqual({"rejected": 4}, result["status_counts"])
        self.assertTrue(all(row["occurrences"][0]["source_identity"] is None for row in rows))

    def test_changed_file_during_held_read_cannot_acquire_an_identity(self):
        path = self.source("textures/foo.tga.aya", envelope(dds(4, 4)))
        original = os.read
        changed = False
        def mutating_read(fd, count):
            nonlocal changed
            data = original(fd, count)
            if data and not changed:
                changed = True
                path.write_bytes(b"different bytes")
            return data
        rows = self.texture_catalog([path])
        with patch.object(catalog.os, "read", side_effect=mutating_read):
            result = self.inspect(rows)
        self.assertEqual({"rejected": 1}, result["status_counts"])
        self.assertIsNone(rows[0]["occurrences"][0]["source_identity"])

    def test_count_and_byte_budgets_keep_unattempted_rows(self):
        paths = [self.source(name + ".tga.aya", envelope(dds(4, 4))) for name in ("a", "b")]
        rows = self.texture_catalog(paths)
        with patch.object(catalog, "MAX_INSPECTED_SOURCES", 1):
            result = self.inspect(rows)
        self.assertEqual({"notAttempted": 1, "valid": 1}, result["status_counts"])
        self.assertEqual(2, len(rows))
        with patch.object(catalog, "MAX_INSPECTED_SOURCE_BYTES", 1):
            result = self.inspect(self.texture_catalog(paths))
        self.assertEqual({"notAttempted": 2}, result["status_counts"])
        self.assertEqual(0, result["source_bytes_read"])

    def test_rejected_changed_reads_consume_the_aggregate_byte_budget(self):
        paths = [self.source(f"{index}.tga.aya", b"abc") for index in range(4)]
        rows = self.texture_catalog(paths)
        original_read = os.read
        read_bytes = 0
        def changed_read(fd, count):
            nonlocal read_bytes
            data = original_read(fd, count)
            read_bytes += len(data)
            if data:
                paths[0].write_bytes(b"changed")
            return data
        with patch.object(catalog, "MAX_INSPECTED_SOURCE_BYTES", 3), \
                patch.object(catalog.os, "read", side_effect=changed_read):
            result = self.inspect(rows)
        self.assertEqual(3, read_bytes)
        self.assertEqual(read_bytes, result["source_bytes_read"])
        self.assertEqual({"notAttempted": 3, "rejected": 1}, result["status_counts"])
        self.assertTrue(all(row["occurrences"][0]["source_identity"] is None for row in rows))

    def test_growing_source_never_reads_past_its_admitted_size(self):
        path = self.source("growing.tga.aya", b"abc")
        rows = self.texture_catalog([path])
        original_read = os.read
        requests, read_bytes = [], 0
        def growing_read(fd, count):
            nonlocal read_bytes
            requests.append(count)
            data = original_read(fd, count)
            read_bytes += len(data)
            if data:
                with path.open("ab") as stream:
                    stream.write(b"appended beyond the admitted limit")
            return data
        with patch.object(catalog, "MAX_INSPECTED_SOURCE_BYTES", 3), \
                patch.object(catalog.os, "read", side_effect=growing_read):
            result = self.inspect(rows)
        self.assertEqual([3], requests)
        self.assertEqual(3, read_bytes)
        self.assertEqual(3, result["source_bytes_read"])
        self.assertEqual({"rejected": 1}, result["status_counts"])

    def test_partial_read_then_error_is_also_charged(self):
        paths = [self.source(f"{index}.tga.aya", b"abc") for index in range(2)]
        rows = self.texture_catalog(paths)
        original_read = os.read
        calls = 0
        def failing_read(fd, count):
            nonlocal calls
            calls += 1
            if calls == 1:
                return original_read(fd, 2)
            raise OSError(5, "authored I/O failure")
        with patch.object(catalog, "MAX_INSPECTED_SOURCE_BYTES", 3), \
                patch.object(catalog.os, "read", side_effect=failing_read):
            result = self.inspect(rows)
        self.assertEqual(2, calls)
        self.assertEqual(2, result["source_bytes_read"])
        self.assertEqual({"notAttempted": 1, "unavailable": 1}, result["status_counts"])

    def test_oversize_source_refuses_without_a_payload_read(self):
        path = self.source("oversize.tga.aya", b"abcd")
        rows = self.texture_catalog([path])
        with patch.object(catalog, "MAX_SINGLE_SOURCE_BYTES", 3), \
                patch.object(catalog.os, "read", side_effect=AssertionError("oversize source read")):
            result = self.inspect(rows)
        self.assertEqual({"unsupported": 1}, result["status_counts"])
        self.assertEqual(0, result["source_bytes_read"])

    def test_oversized_reader_result_is_rejected_charged_and_stops_later_reads(self):
        paths = [self.source(f"{index}.tga.aya", b"abc") for index in range(2)]
        rows = self.texture_catalog(paths)
        # os.read cannot actually exceed count; this adverse API seam proves accounting still
        # reports every returned byte and never tries a second source after such a violation.
        with patch.object(catalog, "MAX_INSPECTED_SOURCE_BYTES", 3), \
                patch.object(catalog.os, "read", return_value=b"abcd") as read:
            result = self.inspect(rows)
        self.assertEqual(1, read.call_count)
        self.assertEqual(3, read.call_args.args[1])
        self.assertEqual(4, result["source_bytes_read"])
        self.assertEqual({"notAttempted": 1, "rejected": 1}, result["status_counts"])

    def _inspection_cli(self, source, inspection_root):
        inputs = {"packed": dict(self.packed, gdie_families=[]), "texture": [self.row(source)],
                  "mesh": [], "embedded": [], "video": {"files": []}, "language": {"rows": []}}
        flags = {"packed": "--packed-manifest", "texture": "--texture-manifest",
                 "mesh": "--loose-mesh-manifest", "embedded": "--embedded-mesh-manifest",
                 "video": "--video-manifest", "language": "--language-matrix"}
        args = ["export_asset_catalog.py", "--repo-root", str(self.repo), "--bundle-root", str(self.bundle),
                "--out-dir", str(self.bundle / "asset_catalog"), "--inspect-source-root", str(inspection_root)]
        for name, data in inputs.items():
            manifest = self.repo / (name + ".json")
            manifest.write_text(json.dumps(data))
            args += [flags[name], str(manifest)]
        return args

    def test_actual_cli_refuses_selected_source_under_output_without_overwriting_it(self):
        output = self.bundle / "asset_catalog"
        output.mkdir()
        source = output / "catalog.json"
        original = dds(4, 4)
        source.write_bytes(original)
        # Relative declarations use the same repo-root anchor as normal inspection.
        args = self._inspection_cli(source.relative_to(self.repo), self.bundle)
        with patch("sys.argv", args), contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(UnsafeGeneratedOutputError, "overlap protected source"):
            catalog.main()
        self.assertEqual(original, source.read_bytes())
        self.assertFalse((output / "summary.json").exists())

    def test_default_cli_also_protects_declared_source_without_inspection(self):
        output = self.bundle / "asset_catalog"
        output.mkdir()
        source = output / "catalog.json"
        original = b"original source, not a generated result"
        source.write_bytes(original)
        args = self._inspection_cli(source, self.repo)
        index = args.index("--inspect-source-root")
        del args[index:index + 2]
        with patch("sys.argv", args), contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(UnsafeGeneratedOutputError, "overlap protected source"):
            catalog.main()
        self.assertEqual(original, source.read_bytes())
        self.assertFalse((output / "summary.json").exists())

    def test_actual_cli_parent_swap_after_inspection_cannot_overwrite_sources(self):
        source = self.source("catalog.json", b"original source")
        args = self._inspection_cli(source, self.repo)
        inspect = catalog.inspect_catalog_sources
        def swap(*arguments, **keywords):
            result = inspect(*arguments, **keywords)
            output = self.bundle / "asset_catalog"
            output.rename(self.bundle / "held-catalog-output")
            output.symlink_to(self.sources, target_is_directory=True)
            return result
        with patch("sys.argv", args), patch.object(catalog, "inspect_catalog_sources", side_effect=swap), \
                contextlib.redirect_stdout(io.StringIO()), self.assertRaises(UnsafeGeneratedOutputError):
            catalog.main()
        self.assertEqual(b"original source", source.read_bytes())
        self.assertFalse((self.sources / "summary.json").exists())

    def test_dangling_selected_source_link_retains_its_rejected_row(self):
        source = self.sources / "missing.tga.aya"
        source.symlink_to(self.sources / "nonexistent")
        args = self._inspection_cli(source, self.repo)
        with patch("sys.argv", args), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, catalog.main())
        result = json.loads((self.bundle / "asset_catalog/catalog.json").read_text())
        self.assertEqual({"rejected": 1}, result["source_inspection"]["status_counts"])
        self.assertIsNone(result["textures"][0]["occurrences"][0]["source_identity"])
        self.assertTrue(source.is_symlink())

    def test_broad_inspection_root_allows_disjoint_selected_source_and_output(self):
        source = self.source("textures/good.dds", dds(4, 4))
        args = self._inspection_cli(source, self.repo)
        with patch("sys.argv", args), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, catalog.main())
        result = json.loads((self.bundle / "asset_catalog/catalog.json").read_text())
        self.assertEqual({"valid": 1}, result["source_inspection"]["status_counts"])
        self.assertEqual(dds(4, 4), source.read_bytes())

    def test_raw_embedded_framing_is_unknown_until_complete_cmsh_is_supplied(self):
        from cmsh_animation_usage_census_tests import _catalog_stream
        raw = self.source("one/archive.aya/body.cmsbody", _catalog_stream())
        unknown = self.source("two/archive.aya/body.cmsbody", b"authored body with unknown framing")
        rows = catalog.build_embedded_mesh_catalog([self.row(raw), self.row(unknown)], self.repo, self.bundle)
        result = self.inspect(embedded=rows, embedded_sources=[self.row(raw), self.row(unknown)])
        self.assertEqual({"parsed": 1, "unknown": 1}, result["status_counts"])
        self.assertEqual(2, len(rows))
        self.assertTrue(all(row["logical_id_ambiguous"] for row in rows))
        parsed = next(row for row in rows if row["variants"])
        self.assertEqual("cmsh-stream", parsed["variants"][0]["payload_domain"])
        self.assertNotIn("identity", parsed["variants"][0]["measured"])
        self.assertIsNone(parsed["export_fbx_path"])
        refused = next(row for row in rows if not row["variants"])
        self.assertEqual("unknown", refused["occurrences"][0]["status"])

    def test_loose_mesh_repacked_twins_share_payload_identity(self):
        from cmsh_animation_usage_census_tests import _catalog_stream
        stream = _catalog_stream()
        paths = [self.source("meshes/m_fixture.aya", envelope(stream, 0)),
                 self.source("meshes/fixture.aya", envelope(stream, 9))]
        rows = catalog.build_loose_mesh_catalog([self.row(path) for path in paths], self.packed,
                                               self.repo, self.bundle)
        result = self.inspect(meshes=rows, mesh_sources=[self.row(path) for path in paths])
        self.assertEqual({"parsed": 2}, result["status_counts"])
        self.assertEqual(1, rows[0]["exact_variant_count"])
        self.assertEqual(2, rows[0]["occurrence_count"])
        self.assertEqual([], rows[0]["export_fbx_paths"])

    def test_default_cli_does_not_inspect_and_explicit_root_enables_join(self):
        path = self.source("textures/foo.tga.aya", envelope(dds(4, 4)))
        inputs = {"packed": dict(self.packed, gdie_families=[]), "texture": [self.row(path)],
                  "mesh": [], "embedded": [], "video": {"files": []}, "language": {"rows": []}}
        flags = {"packed": "--packed-manifest", "texture": "--texture-manifest",
                 "mesh": "--loose-mesh-manifest", "embedded": "--embedded-mesh-manifest",
                 "video": "--video-manifest", "language": "--language-matrix"}
        args = ["export_asset_catalog.py", "--repo-root", str(self.repo), "--bundle-root", str(self.bundle),
                "--out-dir", str(self.bundle / "asset_catalog")]
        for name, data in inputs.items():
            manifest = self.repo / (name + ".json")
            manifest.write_text(json.dumps(data))
            args += [flags[name], str(manifest)]
        with patch("sys.argv", args), contextlib.redirect_stdout(io.StringIO()), \
                patch.object(catalog, "_read_selected_source", side_effect=AssertionError("implicit source read")):
            self.assertEqual(0, catalog.main())
        result = json.loads((self.bundle / "asset_catalog/catalog.json").read_text())
        self.assertEqual({"status": "notRequested"}, result["source_inspection"])
        self.assertNotIn("variants", result["textures"][0])
        with patch("sys.argv", args + ["--inspect-source-root", str(self.sources)]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, catalog.main())
        result = json.loads((self.bundle / "asset_catalog/catalog.json").read_text())
        self.assertEqual({"valid": 1}, result["source_inspection"]["status_counts"])
        self.assertEqual(1, result["textures"][0]["exact_variant_count"])

    def packed_row(self, path, platform="PC", **inspection):
        return dict(self.row(path), source_inspection=dict(kind="packed-text", platform=platform, **inspection))

    def inspect_packed(self, declarations):
        rows = catalog.build_texture_catalog(declarations, self.packed, self.repo, self.bundle)
        result = self.inspect(rows, texture_sources=declarations)
        return rows, result

    def test_explicit_raw_text_projects_multiframe_metadata_without_verified_name_or_archive_join(self):
        payload = texture_payload(platform="PC", name="meshtex\\actual.tga", frame_mips=(2, 1))
        path = self.source("raw/filename.tga.text", payload)
        origin = dict(source_path="data/resources/100_res_PC.aya", archive_sha256="a" * 64,
                      payload_offset=1234, chunk_path=[7])
        rows, result = self.inspect_packed([self.packed_row(path, origin=origin)])
        self.assertEqual({"parsed": 1}, result["status_counts"])
        self.assertEqual(3, result["packed_texture_mips_projected"])
        self.assertIn("not-original-archive-selection", result["packed_texture_scope"])
        self.assertEqual("filename.tga", rows[0]["canonical_ref"])
        variant = rows[0]["variants"][0]
        self.assertEqual("serialized-TEXT-PC", variant["payload_domain"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), variant["payload_identity"]["sha256"])
        measured = variant["measured"]
        self.assertEqual("meshtex\\actual.tga", measured["descriptor"]["name"])
        self.assertEqual([2, 1], [f["declaredMipCount"] for f in measured["frames"]])
        self.assertNotIn("identity", measured)
        self.assertNotIn("limits", measured)
        self.assertTrue(all("occurrenceId" not in f for f in measured["frames"]))
        self.assertTrue(all(m["sha256"] is None for f in measured["frames"] for m in f["mips"]))
        occurrence = rows[0]["occurrences"][0]
        self.assertEqual(hashlib.sha256(payload).hexdigest(), occurrence["source_identity"]["sha256"])
        self.assertEqual({"declared": origin, "verification": "caller-supplied-not-verified"}, occurrence["origin_annotation"])
        self.assertIn("not verified", occurrence["catalog_name_join"])
        self.assertNotIn("origin", json.dumps(variant))
        self.assertEqual([], rows[0]["export_png_paths"])

    def test_origin_annotations_cannot_change_measured_variant_or_occurrence_identity(self):
        path = self.source("raw/foo.tga.text", texture_payload(platform="PC"))
        one, first = self.inspect_packed([self.packed_row(path, origin={"archive_sha256": "a" * 64})])
        two, second = self.inspect_packed([self.packed_row(path, origin={"archive_sha256": "b" * 64})])
        self.assertEqual(one[0]["variants"], two[0]["variants"])
        self.assertEqual(first["selection_namespace"], second["selection_namespace"])
        self.assertEqual(one[0]["occurrences"][0]["occurrence_id"], two[0]["occurrences"][0]["occurrence_id"])
        self.assertNotEqual(one[0]["occurrences"][0]["origin_annotation"], two[0]["occurrences"][0]["origin_annotation"])

    def test_same_payload_at_two_locations_deduplicates_without_deduplicating_occurrences(self):
        payload = texture_payload(platform="PC")
        paths = [self.source(name, payload) for name in ("one/foo.tga.text", "two/foo.tga.text")]
        rows, _result = self.inspect_packed([self.packed_row(p) for p in paths])
        self.assertEqual(1, rows[0]["exact_variant_count"])
        self.assertEqual(2, rows[0]["observed_occurrence_count"])
        self.assertEqual(2, len({o["occurrence_id"] for o in rows[0]["occurrences"]}))
        self.assertNotIn(str(self.sources), json.dumps(rows[0]["variants"]))

    def test_distinct_same_named_texts_and_dds_remain_separate_unjoined_variants(self):
        first = texture_payload(platform="PC")
        second = bytearray(first)
        second[packed.CTEX_BODY_START + 0x94] ^= 1
        a = self.source("one/foo.tga.text", first)
        b = self.source("two/foo.tga.text", bytes(second))
        d = self.source("textures/foo.tga.dds", dds(4, 4))
        rows, _result = self.inspect_packed([self.packed_row(a), self.packed_row(b), self.row(d)])
        self.assertEqual(3, rows[0]["exact_variant_count"])
        self.assertEqual({"serialized-TEXT-PC", "dds-stream"}, {v["payload_domain"] for v in rows[0]["variants"]})
        for variant in rows[0]["variants"]:
            if variant["payload_domain"] == "serialized-TEXT-PC":
                self.assertIsNone(variant["measured"]["descriptor"]["ddsStorageFormat"])

    def test_xbox_inline_mips_keep_actual_hashes_and_unproved_pc_fields_null(self):
        payload = texture_payload(platform="XBOX", frame_mips=(2, 1))
        path = self.source("raw/foo.tga.text", payload)
        rows, _result = self.inspect_packed([self.packed_row(path, platform="XBOX")])
        variant = rows[0]["variants"][0]
        self.assertEqual("serialized-TEXT-XBOX", variant["payload_domain"])
        measured = variant["measured"]
        self.assertIsNone(measured["descriptor"]["lossShiftRaw"])
        for frame in measured["frames"]:
            for mip in frame["mips"]:
                start = mip["offsetWithinPayload"]
                self.assertEqual(hashlib.sha256(payload[start:start + mip["byteLength"]]).hexdigest(), mip["sha256"])

    def test_missing_declaration_retains_legacy_dds_path_and_no_new_summary_keys(self):
        path = self.source("raw/foo.tga.text", texture_payload(platform="PC"))
        with patch.object(packed, "serialized_texture_metadata", side_effect=AssertionError("implicit TEXT parser")):
            rows, result = self.inspect_packed([self.row(path)])
        self.assertEqual([], rows[0]["variants"])
        self.assertNotIn("packed_texture_scope", result)
        good = self.source("textures/foo.tga.dds", dds(4, 4))
        legacy, first = self.inspect_packed([self.row(good)])
        explicit_null, second = self.inspect_packed([dict(self.row(good), source_inspection=None)])
        self.assertEqual(legacy, explicit_null)
        self.assertEqual(first, second)

    def test_conflicting_duplicate_selectors_refuse_instead_of_first_wins(self):
        path = self.source("raw/foo.tga.text", texture_payload(platform="PC"))
        selectors = [self.packed_row(path), self.packed_row(path, platform="XBOX")]
        with patch.object(packed, "serialized_texture_metadata", side_effect=AssertionError("ambiguous projection")):
            rows, first = self.inspect_packed(selectors)
            reordered, second = self.inspect_packed(list(reversed(selectors)))
        self.assertEqual(rows, reordered)
        self.assertEqual(first, second)
        self.assertEqual({"rejected": 1}, first["status_counts"])
        self.assertEqual([], rows[0]["variants"])
        self.assertIsNotNone(rows[0]["occurrences"][0]["source_identity"])

    def test_invalid_or_unbounded_annotations_remain_rejected_measured_sources(self):
        path = self.source("raw/foo.tga.text", texture_payload(platform="PC"))
        invalid = [True, {}, {"kind": "packed-text", "platform": "auto"},
                   {"kind": "packed-text", "platform": "PC", "extra": True}]
        invalid += [dict(kind="packed-text", platform="PC", origin=origin) for origin in (
            {"source_path": "/home/player/private.aya"}, {"source_path": "../x"},
            {"source_path": "x" * 4097}, {"archive_sha256": "A" * 64},
            {"payload_offset": True}, {"payload_offset": 2**64},
            {"chunk_path": [True]}, {"chunk_path": [0] * 33}, {"unknown": "x"})]
        with patch.object(packed, "serialized_texture_metadata", side_effect=AssertionError("invalid annotation parser")):
            for annotation in invalid:
                with self.subTest(annotation=annotation):
                    rows, result = self.inspect_packed([dict(self.row(path), source_inspection=annotation)])
                    self.assertEqual({"rejected": 1}, result["status_counts"])
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), rows[0]["occurrences"][0]["source_identity"]["sha256"])

    def test_global_mip_budget_refuses_before_second_legacy_parser_expansion(self):
        paths = [self.source(f"raw/{n}.tga.text", texture_payload(platform="PC", frame_mips=(3,))) for n in (0, 1)]
        with patch.object(catalog, "MAX_PACKED_TEXTURE_MIPS", 4), \
                patch.object(packed, "parse_serialized_texture", wraps=packed.parse_serialized_texture) as parse:
            rows, result = self.inspect_packed([self.packed_row(p) for p in paths])
        self.assertEqual(1, parse.call_count)
        self.assertEqual(3, result["packed_texture_mips_projected"])
        self.assertEqual({"parsed": 1, "notAttempted": 1}, result["status_counts"])
        refused = next(o for row in rows for o in row["occurrences"] if o["status"] == "notAttempted")
        self.assertEqual([], refused["measured"]["frames"])

    def test_global_mip_exact_boundary_and_exhausted_budget(self):
        declarations = [self.packed_row(self.source(f"raw/{n}.tga.text", texture_payload(platform="PC", frame_mips=(2,)))) for n in range(3)]
        with patch.object(catalog, "MAX_PACKED_TEXTURE_MIPS", 4), \
                patch.object(packed, "serialized_texture_metadata", wraps=packed.serialized_texture_metadata) as project:
            _rows, result = self.inspect_packed(declarations)
        self.assertEqual(2, project.call_count)
        self.assertEqual(4, result["packed_texture_mips_projected"])
        self.assertEqual({"parsed": 2, "notAttempted": 1}, result["status_counts"])

    def test_malformed_selected_text_preserves_source_and_no_partial_variant(self):
        payload = texture_payload(platform="PC", frame_mips=(2, 1))[:-1]
        path = self.source("raw/foo.tga.text", payload)
        rows, result = self.inspect_packed([self.packed_row(path)])
        self.assertEqual({"unparsed": 1}, result["status_counts"])
        self.assertEqual([], rows[0]["variants"])
        occurrence = rows[0]["occurrences"][0]
        self.assertEqual([], occurrence["measured"]["frames"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), occurrence["source_identity"]["sha256"])

    def test_annotation_does_not_decode_an_original_archive(self):
        path = self.source("raw/foo.tga.aya", envelope(texture_payload(platform="PC")))
        with patch.object(catalog.aai, "decode_archive_envelope", side_effect=AssertionError("implicit archive discovery")):
            rows, result = self.inspect_packed([self.packed_row(path)])
        self.assertEqual({"unparsed": 1}, result["status_counts"])
        self.assertEqual([], rows[0]["variants"])

    def test_parent_replacement_with_identical_bytes_is_refused_before_metadata(self):
        payload = texture_payload(platform="PC")
        path = self.source("raw/foo.tga.text", payload)
        read = catalog.os.read
        changed = False
        before = path.stat()
        def replace_parent(fd, count):
            nonlocal changed
            data = read(fd, count)
            if not changed:
                changed = True
                path.parent.rename(self.sources / "held-raw")
                path.parent.mkdir()
                path.write_bytes(payload)
            return data
        with patch.object(catalog.os, "read", side_effect=replace_parent), \
                patch.object(packed, "serialized_texture_metadata", side_effect=AssertionError("changed path reached parser")):
            rows, result = self.inspect_packed([self.packed_row(path)])
        held = (self.sources / "held-raw" / path.name).stat()
        self.assertEqual(catalog._file_fingerprint(before), catalog._file_fingerprint(held))
        self.assertEqual({"rejected": 1}, result["status_counts"])
        self.assertIsNone(rows[0]["occurrences"][0]["source_identity"])
        self.assertEqual(len(payload), result["source_bytes_read"])

    def test_actual_cli_publishes_only_opted_in_descriptor_metadata(self):
        payload = texture_payload(platform="PC", frame_mips=(2, 1))
        path = self.source("raw/foo.tga.text", payload)
        arguments = self._inspection_cli(path, self.sources)
        manifest = self.repo / "texture.json"
        manifest.write_text(json.dumps([self.packed_row(path)]))
        with patch("sys.argv", arguments), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, catalog.main())
        result = json.loads((self.bundle / "asset_catalog/catalog.json").read_text())
        self.assertEqual(3, result["schema_version"])
        self.assertEqual(2, len(result["textures"][0]["variants"][0]["measured"]["frames"]))
        self.assertEqual([], result["textures"][0]["export_png_paths"])
        self.assertEqual(payload, path.read_bytes())
        index = arguments.index("--inspect-source-root")
        del arguments[index:index + 2]
        with patch("sys.argv", arguments), contextlib.redirect_stdout(io.StringIO()), \
                patch.object(packed, "serialized_texture_metadata", side_effect=AssertionError("non-opt-in projection")):
            self.assertEqual(0, catalog.main())
        legacy = json.loads((self.bundle / "asset_catalog/catalog.json").read_text())
        self.assertEqual({"status": "notRequested"}, legacy["source_inspection"])
        self.assertNotIn("variants", legacy["textures"][0])

    def test_packed_origin_annotations_cannot_bypass_source_output_overlap_guard(self):
        output = self.bundle / "asset_catalog"
        output.mkdir()
        path = output / "catalog.json"
        payload = texture_payload(platform="PC")
        path.write_bytes(payload)
        arguments = self._inspection_cli(path, self.bundle)
        (self.repo / "texture.json").write_text(json.dumps([
            self.packed_row(path, origin={"source_path": "elsewhere/source.aya"})]))
        with patch("sys.argv", arguments), contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(UnsafeGeneratedOutputError, "overlap protected source"):
            catalog.main()
        self.assertEqual(payload, path.read_bytes())
        self.assertFalse((output / "summary.json").exists())


if __name__ == "__main__":
    unittest.main()
