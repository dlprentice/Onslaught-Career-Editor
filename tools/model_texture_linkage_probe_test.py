#!/usr/bin/env python3
"""Tests for the model texture linkage probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import model_texture_linkage_probe as probe


def write_fake_fbx(path: Path, texture_names: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = b"Kaydara FBX Binary  \x00"
    for name in texture_names:
        payload += b"Texture\x00" + name.encode("ascii") + b"\x00"
        payload += b"C:\\private\\MeshTextures\\" + name.encode("ascii") + b"\x00"
    path.write_bytes(payload)


class ModelTextureLinkageProbeTests(unittest.TestCase):
    def test_reports_sidecar_and_catalog_linkage_without_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = root / "full-export" / "asset_catalog" / "catalog.json"
            fbx = root / "full-export" / "asset_export" / "loose_meshes" / "ship.fbx"
            direct_fbx = root / "full-export" / "asset_export" / "loose_meshes" / "tank.fbx"
            mesh_textures = (
                root / "full-export" / "asset_export" / "loose_meshes" / "MeshTextures"
            )
            write_fake_fbx(fbx, ["ship.png", "m_rocket.tga", "orphan_sidecar.png", "default10.png"])
            write_fake_fbx(direct_fbx, ["tank.png"])
            (mesh_textures / "ship.png").parent.mkdir(parents=True, exist_ok=True)
            (mesh_textures / "ship.png").write_bytes(b"png")
            (mesh_textures / "m_rocket.png").write_bytes(b"png")
            (mesh_textures / "orphan_sidecar.png").write_bytes(b"png")
            (mesh_textures / "tank.png").write_bytes(b"png")
            catalog.parent.mkdir(parents=True, exist_ok=True)
            catalog.write_text(
                json.dumps(
                    {
                        "textures": [
                            {"canonical_ref": "meshtex\\ship.tga"},
                            {"canonical_ref": "meshtex\\rocket_source.tga", "export_file_name": "m rocket.png"},
                            {"canonical_ref": "meshtex\\tank.tga"},
                        ],
                        "loose_meshes": [
                            {
                                "canonical_ref": "ship.msh",
                                "export_fbx_paths": [str(fbx)],
                            },
                            {
                                "canonical_ref": "tank.msh",
                                "export_fbx_paths": [str(direct_fbx)],
                            }
                        ],
                        "embedded_meshes": [],
                    }
                ),
                encoding="utf-8",
            )

            report = probe.build_report(catalog)

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["modelRows"], 2)
            self.assertEqual(report["uniqueModelTextureRefs"], 4)
            self.assertEqual(report["uniqueTextureRefsWithExactSidecarName"], 3)
            self.assertEqual(report["uniqueTextureRefsWithSidecarStemOnly"], 1)
            self.assertEqual(report["uniqueTextureRefsMissingCatalogRows"], 1)
            self.assertEqual(report["modelRowsWithAllTextureRefsCatalogMapped"], 1)
            self.assertEqual(report["modelRowsWithAnyCatalogMissingTextureRef"], 1)
            self.assertEqual(report["modelRowsWithAnyMissingSidecarTextureRef"], 0)
            self.assertEqual(report["allCatalogMappedModelSamples"][0]["label"], "tank.msh")
            self.assertEqual(report["sidecarNeededModelSamples"][0]["label"], "ship.msh")
            self.assertEqual(
                report["sidecarNeededModelSamples"][0]["catalogMissingRefSample"],
                ["orphan_sidecar.png"],
            )
            serialized = json.dumps(report)
            self.assertNotIn("C:\\private", serialized)
            self.assertNotIn(str(fbx), serialized)
            self.assertNotIn(str(direct_fbx), serialized)

    def test_missing_sidecar_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = root / "full-export" / "asset_catalog" / "catalog.json"
            fbx = root / "full-export" / "asset_export" / "loose_meshes" / "ship.fbx"
            write_fake_fbx(fbx, ["missing.png"])
            catalog.parent.mkdir(parents=True, exist_ok=True)
            catalog.write_text(
                json.dumps(
                    {
                        "textures": [],
                        "loose_meshes": [
                            {
                                "canonical_ref": "ship.msh",
                                "export_fbx_paths": [str(fbx)],
                            }
                        ],
                        "embedded_meshes": [],
                    }
                ),
                encoding="utf-8",
            )

            report = probe.build_report(catalog)

            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["uniqueTextureRefsMissingSidecar"], 1)
            self.assertEqual(report["modelRowsWithAnyMissingSidecarTextureRef"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
