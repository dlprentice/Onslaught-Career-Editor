#!/usr/bin/env python3
"""Tests for the FrontEnd Goodies artwork catalog probe."""

from __future__ import annotations

import json
import struct
import tempfile
import unittest
from pathlib import Path

import goodies_frontend_art_probe as probe


def write_minimal_png(path: Path, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        probe.PNG_SIGNATURE
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x06\x00\x00\x00"
    )


class GoodiesFrontendArtProbeTests(unittest.TestCase):
    def test_reports_required_rows_and_dimensions_without_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = []
            for index, required in enumerate(probe.REQUIRED_TEXTURES, start=1):
                export = root / "exports" / f"{required.key}.png"
                write_minimal_png(export, 16 * index, 8 * index)
                rows.append(
                    {
                        "kind": "texture",
                        "canonical_ref": required.canonical_ref,
                        "source_aya_count": 1,
                        "source_aya_paths": [f"C:\\private\\{required.key}.aya"],
                        "export_png_count": 1,
                        "export_png_paths": [str(export)],
                        "packed_text_ref_count": 1,
                        "total_packed_ref_count": 1,
                        "referenced_in_packed": True,
                    }
                )
            catalog = root / "catalog.json"
            catalog.write_text(json.dumps({"textures": rows}), encoding="utf-8")

            report = probe.build_report(catalog, check_exports=True)

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(
                report["presentRequiredTextureCount"], len(probe.REQUIRED_TEXTURES)
            )
            first = report["requiredTextures"][0]
            self.assertEqual(first["exportedPngDimensions"], {"width": 16, "height": 8})
            serialized = json.dumps(report)
            self.assertNotIn("C:\\private", serialized)
            self.assertNotIn(str(root / "exports"), serialized)

    def test_missing_required_row_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            catalog = Path(tmp) / "catalog.json"
            catalog.write_text(json.dumps({"textures": []}), encoding="utf-8")

            report = probe.build_report(catalog, check_exports=True)

            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["presentRequiredTextureCount"], 0)
            self.assertIn("frontend\\v2\\fe_goodies1.tga", report["missingRequiredTextures"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
