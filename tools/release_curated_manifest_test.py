#!/usr/bin/env python3
"""Focused tests for curated release manifest generation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import public_candidate_inventory_check as inventory
import export_curated_release_tree as exporter
import release_curated_manifest as manifest
from release_profile_snapshot import Classification


class ReleaseCuratedManifestTests(unittest.TestCase):
    def test_exported_package_uses_payload_mode_and_omits_source_only_migration_gate(self) -> None:
        include, exclude, _tracked_only = manifest.load_manifest(manifest.MANIFEST_PATH)
        package = json.loads(
            (manifest.ROOT / "release" / "readiness" / "public_package.json").read_text(
                encoding="utf-8"
            )
        )
        scripts = package["scripts"]

        self.assertIn("--payload-root .", scripts["test:hard-payload-safety"])
        self.assertIn("--payload-root .", scripts["test:public-allowlist"])
        self.assertNotIn("test:public-primary-migration-inventory", scripts)
        self.assertNotIn("tools/public_primary_migration_inventory.py", include)
        source_only_paths = [
            "LOCAL_LAB_OVERLAY.md",
            "coordination/README.md",
            "goal.md",
            "goal.policy.md",
            "tools/public_primary_migration_inventory.py",
        ]
        self.assertEqual(
            manifest.select_manifest_files(
                source_only_paths,
                include_patterns=include,
                exclude_patterns=exclude,
            ),
            [],
        )

    def test_exporter_materializes_candidate_specific_front_doors(self) -> None:
        self.assertEqual(
            exporter.MATERIALIZED_FILES["release/readiness/public_README.txt"],
            "README.MD",
        )
        self.assertEqual(
            exporter.MATERIALIZED_FILES["release/readiness/public_CONTRIBUTING.txt"],
            "CONTRIBUTING.md",
        )
        self.assertEqual(
            manifest.MATERIALIZED_PUBLIC_SOURCES["README.MD"],
            "release/readiness/public_README.txt",
        )
        self.assertEqual(
            manifest.MATERIALIZED_PUBLIC_SOURCES["CONTRIBUTING.md"],
            "release/readiness/public_CONTRIBUTING.txt",
        )

        readme = (manifest.ROOT / "release" / "readiness" / "public_README.txt").read_text(
            encoding="utf-8"
        )
        inventory_position = readme.index("npm run test:public-candidate-inventory")
        allowlist_position = readme.index("npm run test:public-allowlist")
        build_position = readme.index("npm test")
        self.assertLess(inventory_position, allowlist_position)
        self.assertLess(allowlist_position, build_position)

    def test_exporter_runs_exported_payload_scanner_in_payload_mode(self) -> None:
        destination = Path("materialized-candidate")
        commands = exporter.exported_tree_check_commands(destination)
        exported_scanner = destination / "tools" / "public_allowlist_safety_check.py"
        matching = [command for command in commands if str(exported_scanner) in command]

        self.assertEqual(len(matching), 2)
        scan_command = next(command for command in matching if "--self-test" not in command)
        self.assertIn("--payload-root", scan_command)
        self.assertIn(str(destination), scan_command)
        self.assertIn("--require-private-text-guard", scan_command)

    def test_candidate_inventory_supports_materialized_non_git_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.MD").write_text("# Exported source\n", encoding="utf-8")

            findings = inventory.check_candidate_root(root)

        self.assertEqual(findings, [])

    def test_curated_candidate_excludes_unattested_game_generated_save_fixture(self) -> None:
        fixture = "tests_shared/fixtures/gold_career_save.bin"
        include, exclude, _tracked_only = manifest.load_manifest(manifest.MANIFEST_PATH)

        selected = manifest.select_manifest_files(
            [fixture],
            include_patterns=include,
            exclude_patterns=exclude,
        )

        self.assertEqual(selected, [])
        classification = manifest.classify_path(fixture)
        self.assertEqual(classification.cls, "R4_DENY")
        self.assertEqual(classification.reason, "tests_shared/fixtures/**")

    def test_curated_candidate_contains_every_default_rebuild_input(self) -> None:
        include, _exclude, tracked_only = manifest.load_manifest(manifest.MANIFEST_PATH)
        package = json.loads(
            (manifest.ROOT / "release" / "readiness" / "public_package.json").read_text(
                encoding="utf-8"
            )
        )
        scripts = package["scripts"]
        quick_check = scripts["check:quick"]

        self.assertTrue(tracked_only)
        self.assertIn("global.json", include)
        self.assertIn("rebuild/**", include)
        self.assertIn("roadmap/rebuild-front-door-chain-map.md", include)
        self.assertIn("tools/export_asset_catalog.py", include)
        self.assertIn("tools/aya_archive_inventory.py", include)
        self.assertIn("tools/safe_generated_output.py", include)
        self.assertIn("test:rebuild", quick_check)
        self.assertNotIn("test:rebuild-core", quick_check)
        self.assertIn("test:rebuild-core", scripts["test:rebuild"])
        self.assertIn("test:rebuild-client", scripts["test:rebuild"])
        self.assertIn("test:rebuild-godot-toolchain", scripts["test:rebuild"])
        self.assertIn("test:rebuild-godot-smoke-validation", scripts["test:rebuild"])
        self.assertNotIn("test:docsync", quick_check)

    def test_export_facing_signoff_blocks_match(self) -> None:
        paths = [
            manifest.ROOT / "COLLABORATION.md",
            manifest.ROOT / "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            manifest.ROOT / "release" / "readiness" / "public_AGENTS.md",
            manifest.ROOT / "release" / "readiness" / "public_README.txt",
            manifest.ROOT / "release" / "readiness" / "public_CONTRIBUTING.txt",
        ]

        blocks = []
        for path in paths:
            text = path.read_text(encoding="utf-8")
            start = text.index("<!-- public-package-commands:start -->")
            end = text.index("<!-- public-package-commands:end -->", start)
            blocks.append(text[start:end].replace("\r\n", "\n"))

        self.assertEqual(blocks[0], blocks[1])
        self.assertEqual(blocks[0], blocks[2])
        self.assertEqual(blocks[0], blocks[3])
        self.assertEqual(blocks[0], blocks[4])

    def test_filter_public_rows_excludes_non_r0_rows(self) -> None:
        rows = [
            ("safe.md", Classification("safe.md", "R0_ALLOW", "default")),
            (
                "private.md",
                Classification("private.md", "R4_DENY", "private-ghidra-backup-root"),
            ),
        ]

        public_rows, excluded_rows = manifest.filter_public_rows(rows)

        self.assertEqual([path for path, _cls in public_rows], ["safe.md"])
        self.assertEqual([path for path, _cls in excluded_rows], ["private.md"])

    def test_write_allowlist_uses_lf_newlines_on_windows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "public_candidate_allowlist.tsv"

            manifest.write_allowlist(
                out_path,
                [
                    (
                        "release/readiness/example.md",
                        Classification("release/readiness/example.md", "R0_ALLOW", "default"),
                    )
                ],
            )

            raw = out_path.read_bytes()

        self.assertIn(b"\n", raw)
        self.assertNotIn(b"\r\n", raw)

    def test_exclude_patterns_remove_included_paths_when_no_exact_override_exists(self) -> None:
        selected = manifest.select_manifest_files(
            ["tools/runtime-probes/example.py"],
            include_patterns=["tools/**"],
            exclude_patterns=["tools/runtime-probes/**"],
        )

        self.assertEqual(selected, [])


if __name__ == "__main__":
    unittest.main()
