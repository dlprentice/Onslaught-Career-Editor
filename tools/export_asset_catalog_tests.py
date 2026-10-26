#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Authored catalog projection controls; no game files or asset conversion."""
from pathlib import Path
import tempfile
import unittest

import export_asset_catalog as catalog


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


if __name__ == "__main__":
    unittest.main()
