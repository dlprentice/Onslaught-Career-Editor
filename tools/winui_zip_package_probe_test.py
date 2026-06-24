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
            self.assertTrue((bundle_dir / "app" / probe.APP_EXE).is_file())
            self.assertTrue((bundle_dir / "app" / "support.dll").is_file())
            self.assertFalse((bundle_dir / probe.APP_EXE).exists())
            self.assertFalse((bundle_dir / "support.dll").exists())

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
