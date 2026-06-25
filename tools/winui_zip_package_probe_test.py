#!/usr/bin/env python3
"""Focused tests for the WinUI portable ZIP layout contract."""

from __future__ import annotations

import hashlib
import json
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
            self.assertTrue((bundle_dir / "lore-pack" / "onslaught-lore.v1.index.json").is_file())
            self.assertTrue((bundle_dir / "lore-pack" / "onslaught-lore.v1.jsonl").is_file())
            self.assertTrue((bundle_dir / "app" / probe.APP_EXE).is_file())
            self.assertTrue((bundle_dir / "app" / "support.dll").is_file())
            self.assertFalse((bundle_dir / probe.APP_EXE).exists())
            self.assertFalse((bundle_dir / "support.dll").exists())
            launcher = (bundle_dir / probe.ROOT_LAUNCHER).read_text(encoding="utf-8")
            self.assertIn("lore-book\\BOOK.md", launcher)
            self.assertIn("lore-pack\\onslaught-lore.v1.index.json", launcher)
            self.assertIn("lore-pack\\onslaught-lore.v1.jsonl", launcher)
            self.assertIn("keep the top-level folders together", launcher)

    def test_copy_lore_book_uses_short_entry_subset_when_pack_exists(self) -> None:
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
                self.assertFalse((destination_root / "lore-book" / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md").exists())
                self.assertFalse((destination_root / "lore-book" / unlinked.relative_to(source)).exists())
        finally:
            probe.LORE_BOOK_SOURCE = original_lore_book_source

    def test_copy_lore_book_rejects_missing_local_book_link(self) -> None:
        original_lore_book_source = probe.LORE_BOOK_SOURCE
        try:
            with tempfile.TemporaryDirectory() as temp_root:
                root = Path(temp_root)
                source = root / "source" / "lore-book"
                destination_root = root / "bundle"
                source.mkdir(parents=True)
                (source / "BOOK.md").write_text(
                    "- [Missing](missing-local-lore-file.md)\n",
                    encoding="utf-8",
                )

                probe.LORE_BOOK_SOURCE = source
                result = probe.copy_lore_book(destination_root)

                self.assertEqual(result.status, "FAIL")
                self.assertIn("missing local BOOK.md link", result.summary)
                self.assertFalse((destination_root / "lore-book" / "BOOK.md").exists())
        finally:
            probe.LORE_BOOK_SOURCE = original_lore_book_source

    def test_copy_lore_book_rewrites_unpackaged_local_page_links_to_source_repo(self) -> None:
        original_root = probe.ROOT
        original_lore_book_source = probe.LORE_BOOK_SOURCE
        try:
            with tempfile.TemporaryDirectory() as temp_root:
                root = Path(temp_root)
                repo_root = root / "source"
                source = repo_root / "lore-book"
                destination_root = root / "bundle"
                source.mkdir(parents=True)
                (repo_root / "tools").mkdir(parents=True)
                (source / "BOOK.md").write_text(
                    "- [Start](Start-Here.md)\n"
                    "- [Sibling](Sibling.md)\n",
                    encoding="utf-8",
                )
                (source / "Start-Here.md").write_text(
                    "[Sibling](Sibling.md)\n"
                    "[Deep](deep/Deep.md#anchor)\n"
                    "[Tool](../tools/helper.py)\n",
                    encoding="utf-8",
                )
                (source / "Sibling.md").write_text("# Sibling\n", encoding="utf-8")
                deep = source / "deep" / "Deep.md"
                deep.parent.mkdir(parents=True)
                deep.write_text("# Deep\n", encoding="utf-8")
                (repo_root / "tools" / "helper.py").write_text("print('helper')\n", encoding="utf-8")

                probe.ROOT = repo_root
                probe.LORE_BOOK_SOURCE = source
                result = probe.copy_lore_book(destination_root)

                self.assertEqual(result.status, "PASS")
                packaged_start = (destination_root / "lore-book" / "Start-Here.md").read_text(encoding="utf-8")
                self.assertIn(
                    "[Sibling](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/lore-book/Sibling.md)",
                    packaged_start,
                )
                self.assertIn(
                    "[Deep](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/lore-book/deep/Deep.md#anchor)",
                    packaged_start,
                )
                self.assertIn(
                    "[Tool](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/tools/helper.py)",
                    packaged_start,
                )
                self.assertFalse((destination_root / "lore-book" / "deep" / "Deep.md").exists())
        finally:
            probe.ROOT = original_root
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

    def test_lore_pack_inspection_rejects_payload_like_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(
                bundle_dir,
                content="# Leak\n\nC:\\Users\\david\\source\\secret-path\n",
            )

            failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}

            self.assertIn("bundle_lore_pack", failures)

    def test_lore_pack_inspection_rejects_private_windows_paths_and_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(
                bundle_dir,
                content="# Leak\n\nD:\\Ghidra\\Projects\\BEA.gpr\n\nhttp://172.26.112.1:8193\n",
            )

            failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}

            self.assertIn("bundle_lore_pack", failures)

    def test_lore_pack_inspection_rejects_document_count_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(bundle_dir)
            index_path = bundle_dir / "lore-pack" / "onslaught-lore.v1.index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            index["documentCount"] = 2
            index_path.write_text(json.dumps(index), encoding="utf-8")

            failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}

            self.assertIn("bundle_lore_pack", failures)

    def test_lore_pack_inspection_rejects_byte_length_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(bundle_dir)
            content_path = bundle_dir / "lore-pack" / "onslaught-lore.v1.jsonl"
            row = json.loads(content_path.read_text(encoding="utf-8").strip())
            row["byteLength"] = row["byteLength"] + 1
            content_path.write_text(json.dumps(row) + "\n", encoding="utf-8")

            failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}

            self.assertIn("bundle_lore_pack", failures)

    def test_lore_pack_inspection_rejects_raw_deep_lore_book_leakage_when_pack_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(bundle_dir)
            deep = bundle_dir / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Deep.md"
            deep.parent.mkdir(parents=True, exist_ok=True)
            deep.write_text("# Deep\n", encoding="utf-8")

            failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}

            self.assertIn("bundle_raw_deep_lore_book_leakage", failures)

    def test_lore_pack_inspection_rejects_any_extra_lore_book_file_when_pack_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(bundle_dir)
            extra = bundle_dir / "lore-book" / "extra.md"
            extra.write_text("# Extra\n", encoding="utf-8")

            failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}

            self.assertIn("bundle_raw_deep_lore_book_leakage", failures)

    def test_zip_inspection_rejects_entries_too_long_for_explorer_extract_all(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            zip_path = root / "long-path.zip"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            long_name = "lore-book/" + ("a" * probe.WINDOWS_EXPLORER_SAFE_ENTRY_LENGTH) + ".md"
            long_path = bundle_dir / long_name
            long_path.parent.mkdir(parents=True, exist_ok=True)
            long_path.write_text("# too long\n", encoding="utf-8")

            exit_code, _ = probe.create_zip(bundle_dir, zip_path)
            self.assertEqual(exit_code, 0)
            failures = {item.key for item in probe.inspect_zip(zip_path) if item.status == "FAIL"}

            self.assertIn("zip_explorer_path_safety", failures)

    def test_zip_inspection_rejects_default_extract_folder_plus_entry_too_long(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            zip_path = root / "OnslaughtToolkit-winui-v1.0.4-win-x64.zip"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            entry_name = "lore-book/" + ("a" * 147) + ".md"
            self.assertLessEqual(len(entry_name), probe.WINDOWS_EXPLORER_SAFE_ENTRY_LENGTH)
            self.assertGreater(len(f"{zip_path.stem}/{entry_name}"), probe.WINDOWS_EXPLORER_SAFE_ENTRY_LENGTH)
            entry_path = bundle_dir / entry_name
            entry_path.parent.mkdir(parents=True, exist_ok=True)
            entry_path.write_text("# too long after default extract folder\n", encoding="utf-8")

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

    def test_folder_inspection_allows_framework_images_but_rejects_payload_images(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(bundle_dir)
            allowed = bundle_dir / "app" / "Microsoft.UI.Xaml" / "Assets" / "NoiseAsset_256x256_PNG.png"
            allowed.parent.mkdir(parents=True, exist_ok=True)
            allowed.write_bytes(b"framework image")

            allowed_failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}
            self.assertNotIn("bundle_payload_safety", allowed_failures)

            blocked = bundle_dir / "textures" / "retail-texture.png"
            blocked.parent.mkdir(parents=True, exist_ok=True)
            blocked.write_bytes(b"payload image")

            blocked_failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}
            self.assertIn("bundle_payload_safety", blocked_failures)

    def test_folder_inspection_rejects_dead_local_lore_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            (bundle_dir / "lore-book" / "Start.md").write_text(
                "[Missing](missing-local-page.md)\n",
                encoding="utf-8",
            )

            failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}

            self.assertIn("bundle_lore_link_safety", failures)

    def test_zip_inspection_rejects_dead_local_lore_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            zip_path = root / "lore-links.zip"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            (bundle_dir / "lore-book" / "Start.md").write_text(
                "[Missing](missing-local-page.md)\n",
                encoding="utf-8",
            )

            exit_code, _ = probe.create_zip(bundle_dir, zip_path)
            self.assertEqual(exit_code, 0)
            failures = {item.key for item in probe.inspect_zip(zip_path) if item.status == "FAIL"}

            self.assertIn("zip_lore_link_safety", failures)

    def test_folder_inspection_rejects_stale_packaged_lore_all_in_app_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            (bundle_dir / "lore-book" / "Start.md").write_text(
                "Internal links stay inside the app.\n",
                encoding="utf-8",
            )

            failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}

            self.assertIn("bundle_lore_copy_truth", failures)

    def test_zip_inspection_rejects_stale_packaged_lore_all_in_app_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            zip_path = root / "lore-copy.zip"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            (bundle_dir / "lore-book" / "Start.md").write_text(
                "Search without leaving the app.\n",
                encoding="utf-8",
            )

            exit_code, _ = probe.create_zip(bundle_dir, zip_path)
            self.assertEqual(exit_code, 0)
            failures = {item.key for item in probe.inspect_zip(zip_path) if item.status == "FAIL"}

            self.assertIn("zip_lore_copy_truth", failures)

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

    def _write_required_root_payload(self, bundle_dir: Path) -> None:
        for relative_path in (probe.ROOT_LAUNCHER, probe.ROOT_README, probe.ROOT_LICENSE, "lore-book/BOOK.md", "lore-book/Start-Here.md"):
            path = bundle_dir / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(relative_path, encoding="utf-8")
        self._write_lore_pack_payload(bundle_dir)

    def _write_lore_pack_payload(self, bundle_dir: Path, *, content: str = "# Start\n\nSynthetic fixture.\n") -> None:
        pack_dir = bundle_dir / "lore-pack"
        pack_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        row = {
            "id": "doc-000001",
            "relativePath": "Start-Here.md",
            "title": "Start",
            "sha256": digest,
            "byteLength": len(content.encode("utf-8")),
            "content": content,
        }
        index = {
            "schema": "onslaught-lore-pack.v1",
            "sourceRoot": "lore-book",
            "documentCount": 1,
            "documents": [
                {
                    "id": row["id"],
                    "relativePath": row["relativePath"],
                    "title": row["title"],
                    "sha256": row["sha256"],
                    "byteLength": row["byteLength"],
                    "order": 0,
                }
            ],
        }
        (pack_dir / "onslaught-lore.v1.index.json").write_text(json.dumps(index), encoding="utf-8")
        (pack_dir / "onslaught-lore.v1.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
