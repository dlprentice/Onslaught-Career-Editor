#!/usr/bin/env python3
"""Focused tests for the WinUI portable ZIP layout contract."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import winui_zip_package_probe as probe


class WinUiZipPackageProbeTests(unittest.TestCase):
    def _write_publish_payload(self, publish_dir: Path) -> None:
        publish_dir.mkdir(parents=True, exist_ok=True)
        for relative_path in (
            probe.APP_EXE,
            probe.APP_PRI,
            probe.NOTICES,
            "support.dll",
            "patches/catalog/patches.v2.json",
            "patches/catalog/safe-copy-profiles.v1.json",
        ):
            path = publish_dir / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"{relative_path}\n", encoding="utf-8")

    def test_stage_portable_bundle_keeps_publish_noise_under_app_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            publish_dir = root / "publish"
            bundle_dir = root / "bundle"
            self._write_publish_payload(publish_dir)

            probe.stage_portable_bundle(publish_dir, bundle_dir)

            self.assertTrue((bundle_dir / probe.ROOT_LAUNCHER).is_file())
            self.assertTrue((bundle_dir / probe.ROOT_README).is_file())
            self.assertTrue((bundle_dir / probe.ROOT_LICENSE).is_file())
            self.assertTrue((bundle_dir / "lore-book" / "BOOK.md").is_file())
            self.assertTrue((bundle_dir / "app" / probe.APP_EXE).is_file())
            self.assertTrue((bundle_dir / "app" / "support.dll").is_file())
            self.assertFalse((bundle_dir / probe.APP_EXE).exists())
            self.assertFalse((bundle_dir / "support.dll").exists())

    def test_copy_lore_book_uses_book_linked_subset(self) -> None:
        original_lore_book_source = probe.LORE_BOOK_SOURCE
        try:
            with tempfile.TemporaryDirectory() as temp_root:
                root = Path(temp_root)
                source = root / "source" / "lore-book"
                destination_root = root / "bundle"
                source.mkdir(parents=True)
                (source / "BOOK.md").write_text(
                    "- [Start Here](Start-Here.md)\n"
                    "- [Tech](reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md)\n",
                    encoding="utf-8",
                )
                (source / "Start-Here.md").write_text("# Start Here\n", encoding="utf-8")
                linked = source / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
                linked.parent.mkdir(parents=True)
                linked.write_text("# Ghidra Reference\n", encoding="utf-8")
                unlinked = source / "reverse-engineering" / "game-assets" / (
                    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-"
                    "dry-run-harness-command-arm-checklist-command-arm-checklist-command-"
                    "dry-run-consumer-validation-proof-plan.md"
                )
                unlinked.parent.mkdir(parents=True)
                unlinked.write_text("# Internal proof plan\n", encoding="utf-8")

                probe.LORE_BOOK_SOURCE = source
                result = probe.copy_lore_book(destination_root)

                self.assertEqual(result.status, "PASS")
                self.assertTrue((destination_root / "lore-book" / "BOOK.md").is_file())
                self.assertTrue((destination_root / "lore-book" / "Start-Here.md").is_file())
                self.assertTrue((destination_root / "lore-book" / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md").is_file())
                self.assertFalse((destination_root / "lore-book" / unlinked.relative_to(source)).exists())
        finally:
            probe.LORE_BOOK_SOURCE = original_lore_book_source

    def test_zip_inspection_rejects_raw_publish_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            publish_dir = root / "publish"
            zip_path = root / "raw.zip"
            self._write_publish_payload(publish_dir)

            exit_code, _ = probe.create_zip(publish_dir, zip_path)
            self.assertEqual(exit_code, 0)
            failures = {item.key for item in probe.inspect_zip(zip_path) if item.status == "FAIL"}

            self.assertIn("zip_no_root_executables", failures)
            self.assertIn("zip_no_root_dlls", failures)
            self.assertIn("zip_contains_Launch Onslaught Toolkit.cmd", failures)
            self.assertIn("zip_contains_lore-book_BOOK.md", failures)

    def test_zip_inspection_accepts_portable_bundle_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            publish_dir = root / "publish"
            bundle_dir = root / "bundle"
            zip_path = root / "portable.zip"
            self._write_publish_payload(publish_dir)
            probe.stage_portable_bundle(publish_dir, bundle_dir)

            exit_code, _ = probe.create_zip(bundle_dir, zip_path)
            self.assertEqual(exit_code, 0)
            failures = [item for item in probe.inspect_zip(zip_path) if item.status == "FAIL"]

            self.assertEqual(failures, [])

    def test_zip_inspection_rejects_entries_too_long_for_explorer_extract_all(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            zip_path = root / "long-path.zip"
            self._write_publish_payload(bundle_dir / "app")
            for relative_path in (probe.ROOT_LAUNCHER, probe.ROOT_README, probe.ROOT_LICENSE, "lore-book/BOOK.md"):
                path = bundle_dir / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(relative_path, encoding="utf-8")
            long_name = "lore-book/" + ("a" * probe.WINDOWS_EXPLORER_SAFE_ENTRY_LENGTH) + ".md"
            long_path = bundle_dir / long_name
            long_path.parent.mkdir(parents=True, exist_ok=True)
            long_path.write_text("# too long\n", encoding="utf-8")

            exit_code, _ = probe.create_zip(bundle_dir, zip_path)
            self.assertEqual(exit_code, 0)
            failures = {item.key for item in probe.inspect_zip(zip_path) if item.status == "FAIL"}

            self.assertIn("zip_explorer_path_safety", failures)

    def test_zip_inspection_rejects_hard_payload_entries_inside_app_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            publish_dir = root / "publish"
            bundle_dir = root / "bundle"
            zip_path = root / "payload.zip"
            self._write_publish_payload(publish_dir)
            probe.stage_portable_bundle(publish_dir, bundle_dir)
            payload_path = bundle_dir / "app" / "game" / "BEA.exe"
            payload_path.parent.mkdir(parents=True, exist_ok=True)
            payload_path.write_bytes(b"not ok")

            folder_failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}
            exit_code, _ = probe.create_zip(bundle_dir, zip_path)
            self.assertEqual(exit_code, 0)
            zip_failures = {item.key for item in probe.inspect_zip(zip_path) if item.status == "FAIL"}

            self.assertIn("bundle_payload_safety", folder_failures)
            self.assertIn("zip_payload_safety", zip_failures)

    def test_ui_retry_records_failed_attempt_before_success(self) -> None:
        calls: list[int] = []
        original_run_ui_test = probe.run_ui_test
        original_stop_app_process = probe.stop_app_process
        try:
            def fake_run_ui_test(*args, **kwargs):  # type: ignore[no-untyped-def]
                calls.append(len(calls) + 1)
                if len(calls) == 1:
                    return 1, "transient missing row"
                return 0, "retry passed"

            stop_calls: list[int] = []

            def fake_stop_app_process() -> tuple[int, str]:
                stop_calls.append(len(stop_calls) + 1)
                return 0, "stopped"

            probe.run_ui_test = fake_run_ui_test  # type: ignore[assignment]
            probe.stop_app_process = fake_stop_app_process

            exit_code, output, attempts = probe.run_ui_test_with_retry(
                "FakeFilter",
                Path("fake.exe"),
                max_attempts=2,
            )
        finally:
            probe.run_ui_test = original_run_ui_test  # type: ignore[assignment]
            probe.stop_app_process = original_stop_app_process

        self.assertEqual(exit_code, 0)
        self.assertEqual(attempts, 2)
        self.assertEqual(calls, [1, 2])
        self.assertEqual(stop_calls, [1])
        self.assertIn("=== attempt 1 exit 1 ===", output)
        self.assertIn("transient missing row", output)
        self.assertIn("=== attempt 2 exit 0 ===", output)


if __name__ == "__main__":
    unittest.main()
