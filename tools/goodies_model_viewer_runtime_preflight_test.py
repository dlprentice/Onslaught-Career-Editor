#!/usr/bin/env python3
"""Tests for goodies_model_viewer_runtime_preflight.py."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

import goodies_model_viewer_runtime_preflight as preflight


class GoodiesModelViewerRuntimePreflightTests(unittest.TestCase):
    def test_complete_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_fixture(root)

            results = preflight.run_checks(root)

        self.assertEqual([], [result for result in results if result.status == "FAIL"])
        self.assertTrue(any(result.key == "runtime_safety_boundary" for result in results))
        self.assertTrue(any(result.key == "required_npm_scripts" for result in results))

    def test_missing_runtime_observer_is_a_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_fixture(root)
            (root / "tools" / "runtime-probes" / "goodies-selection-observer.cdb.txt").unlink()

            results = preflight.run_checks(root)

        failures = {result.key: result.summary for result in results if result.status == "FAIL"}
        self.assertIn("runtime_observer_files", failures)
        self.assertIn("goodies-selection-observer.cdb.txt", failures["runtime_observer_files"])

    def test_plan_without_copied_profile_boundary_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_fixture(root)
            plan_path = root / "release" / "readiness" / "goodies_model_viewer_runtime_proof_plan_2026-05-08.md"
            plan_path.write_text("Launch the game and inspect Goodies.\n", encoding="utf-8")

            results = preflight.run_checks(root)

        failures = {result.key: result.summary for result in results if result.status == "FAIL"}
        self.assertIn("runtime_safety_boundary", failures)
        self.assertIn("copied profile", failures["runtime_safety_boundary"])

    def _write_fixture(self, root: Path) -> None:
        readiness = root / "release" / "readiness"
        tools = root / "tools"
        probes = tools / "runtime-probes"
        readiness.mkdir(parents=True)
        probes.mkdir(parents=True)

        plan_text = "\n".join(
            [
                "This is not runtime proof until the copied-profile run succeeds.",
                "Do not launch BEA during preflight.",
                "Do not mutate the installed game or original BEA.exe.",
                "Use a copied profile and apply force_windowed only to the copied executable.",
                "Keep private evidence under subagents/ and clean up so no BEA process remains.",
            ]
        )
        (readiness / "goodies_model_viewer_runtime_proof_plan_2026-05-08.md").write_text(
            plan_text,
            encoding="utf-8",
        )

        for name in preflight.REQUIRED_EVIDENCE_FILES:
            (readiness / name).write_text("public-safe evidence\n", encoding="utf-8")

        for relative in preflight.REQUIRED_RUNTIME_HELPERS:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# helper\n", encoding="utf-8")

        for relative in preflight.REQUIRED_RUNTIME_OBSERVERS:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("observer\n", encoding="utf-8")

        package_scripts = {
            "scripts": {
                "test:goodies-model-viewer-alignment": "py -3 tools\\goodies_model_viewer_alignment_probe.py --check",
                "test:goodies-model-viewer-readback": "py -3 tools\\goodies_model_viewer_readback_probe.py --check",
                "test:mesh-renderer-readback": "py -3 tools\\mesh_renderer_readback_probe.py --check",
                "test:goodies-selection-observer-log": "py -3 tools\\goodies_selection_observer_log_probe_test.py",
            }
        }
        (root / "package.json").write_text(
            json.dumps(package_scripts),
            encoding="utf-8",
        )

        manifest = {
            "entries": [
                {"path": "release/readiness/goodies_model_viewer_runtime_proof_plan_2026-05-08.md"}
            ]
        }
        (readiness / "curated_release_manifest.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
