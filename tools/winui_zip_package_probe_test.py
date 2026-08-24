#!/usr/bin/env python3
"""Focused tests for the WinUI portable ZIP layout contract."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import unittest.mock
import zipfile
from pathlib import Path

import winui_zip_package_probe as probe


class WinUiZipPackageProbeTests(unittest.TestCase):
    def _write_publish_payload(self, publish_dir: Path) -> None:
        publish_dir.mkdir(parents=True, exist_ok=True)
        for relative_path in (
            probe.APP_EXE,
            probe.APP_PRI,
            probe.NOTICES,
            "LibVLCSharp.dll",
            "libvlc/win-x64/libvlc.dll",
            "libvlc/win-x64/libvlccore.dll",
            "libvlc/win-x86/libvlc.dll",
            "libvlc/win-arm64/libvlc.dll",
            "support.dll",
            "patches/catalog/patches.v2.json",
            "patches/catalog/safe-copy-profiles.v1.json",
        ):
            path = publish_dir / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"{relative_path}\n", encoding="utf-8")
        (publish_dir / "OnslaughtCareerEditor.WinUI.deps.json").write_text(
            json.dumps({"libraries": {}}),
            encoding="utf-8",
        )

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
            self.assertTrue((bundle_dir / probe.THIRD_PARTY_LICENSES_INDEX).is_file())
            self.assertTrue((bundle_dir / probe.DOTNET_LICENSE).is_file())
            self.assertTrue((bundle_dir / probe.DOTNET_NOTICES).is_file())
            self.assertTrue((bundle_dir / "lore-book" / "BOOK.md").is_file())
            self.assertTrue((bundle_dir / "lore-pack" / "onslaught-lore.v1.index.json").is_file())
            self.assertTrue((bundle_dir / "lore-pack" / "onslaught-lore.v1.jsonl").is_file())
            self.assertTrue((bundle_dir / "app" / probe.APP_EXE).is_file())
            self.assertTrue((bundle_dir / "app" / "support.dll").is_file())
            self.assertTrue((bundle_dir / "app" / "libvlc" / "win-x64" / "libvlc.dll").is_file())
            self.assertFalse((bundle_dir / "app" / "libvlc" / "win-x86").exists())
            self.assertFalse((bundle_dir / "app" / "libvlc" / "win-arm64").exists())
            self.assertFalse((bundle_dir / probe.APP_EXE).exists())
            self.assertFalse((bundle_dir / "support.dll").exists())
            launcher = (bundle_dir / probe.ROOT_LAUNCHER).read_text(encoding="utf-8")
            self.assertIn("lore-book\\BOOK.md", launcher)
            self.assertIn("lore-pack\\onslaught-lore.v1.index.json", launcher)
            self.assertIn("lore-pack\\onslaught-lore.v1.jsonl", launcher)
            self.assertIn("keep the top-level folders together", launcher)

    def test_copy_lore_book_packages_only_canonical_book_when_pack_exists(self) -> None:
        original_lore_book_source = probe.LORE_BOOK_SOURCE
        try:
            with tempfile.TemporaryDirectory() as temp_root:
                root = Path(temp_root)
                source = root / "source" / "lore-book"
                destination_root = root / "bundle"
                source.mkdir(parents=True)
                (source / "BOOK.md").write_text(
                    "- [Overview](Overview.md)\n"
                    "- [Tech](reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md)\n",
                    encoding="utf-8",
                )
                (source / "Overview.md").write_text("# Overview\n", encoding="utf-8")
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
                self.assertFalse((destination_root / "lore-book" / "Overview.md").exists())
                self.assertFalse((destination_root / "lore-book" / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md").exists())
                self.assertFalse((destination_root / "lore-book" / unlinked.relative_to(source)).exists())
        finally:
            probe.LORE_BOOK_SOURCE = original_lore_book_source

    def test_extract_zip_rejects_traversal_members(self) -> None:
        unsafe_members = (
            "../escape.txt",
            "/absolute.txt",
            "C:/absolute.txt",
            "C:\\absolute.txt",
            "\\\\server\\share\\escape.txt",
            "app/../escape.txt",
            "app/./escape.txt",
            "app//escape.txt",
        )
        for unsafe_member in unsafe_members:
            with self.subTest(unsafe_member=unsafe_member):
                with tempfile.TemporaryDirectory() as temp_root:
                    root = Path(temp_root)
                    zip_path = root / "unsafe.zip"
                    extract_dir = root / "extract"
                    with zipfile.ZipFile(zip_path, "w") as package:
                        package.writestr(unsafe_member, "not ok")
                        package.writestr("app/OnslaughtCareerEditor.WinUI.exe", "ok")

                    exit_code, output = probe.extract_zip(zip_path, extract_dir)

                    self.assertNotEqual(0, exit_code)
                    self.assertIn("unsafe ZIP member", output)
                    self.assertFalse((root / "escape.txt").exists())

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
                packaged_book = (destination_root / "lore-book" / "BOOK.md").read_text(encoding="utf-8")
                self.assertIn(
                    "[Sibling](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/lore-book/Sibling.md)",
                    packaged_book,
                )
                self.assertIn(
                    "[Deep](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/lore-book/deep/Deep.md#anchor)",
                    packaged_book,
                )
                self.assertIn(
                    "[Tool](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/tools/helper.py)",
                    packaged_book,
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

    def test_lore_pack_inspection_rejects_invalid_index_relative_path_without_echoing_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(bundle_dir, relative_path="./SecretLeakProbe.md")

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "FAIL")
            self.assertIn("invalid relativePath", lore_pack_result.summary)
            self.assertNotIn("./SecretLeakProbe.md", lore_pack_result.summary)
            self.assertNotIn("SecretLeakProbe", lore_pack_result.summary)

    def test_lore_pack_inspection_rejects_invalid_content_relative_path_without_echoing_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(
                bundle_dir,
                relative_path="Overview.md",
                content_relative_path="folder/../SecretLeakProbe.md",
            )

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "FAIL")
            self.assertIn("invalid relativePath", lore_pack_result.summary)
            self.assertNotIn("folder/../SecretLeakProbe.md", lore_pack_result.summary)
            self.assertNotIn("SecretLeakProbe", lore_pack_result.summary)

    def test_lore_pack_inspection_rejects_content_relative_path_mismatch_after_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(
                bundle_dir,
                relative_path="folder/Overview.md",
                content_relative_path="folder/Other.md",
            )

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "FAIL")
            self.assertIn("relativePath mismatch", lore_pack_result.summary)
            self.assertNotIn("folder/Other.md", lore_pack_result.summary)

    def test_lore_pack_inspection_rejects_dot_segment_content_relative_path_without_echoing_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(
                bundle_dir,
                relative_path="folder/Overview.md",
                content_relative_path="folder/./SecretLeakProbe.md",
            )

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "FAIL")
            self.assertIn("invalid relativePath", lore_pack_result.summary)
            self.assertNotIn("folder/./SecretLeakProbe.md", lore_pack_result.summary)
            self.assertNotIn("SecretLeakProbe", lore_pack_result.summary)

    def test_lore_pack_inspection_rejects_duplicate_index_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(bundle_dir)
            index_path = bundle_dir / "lore-pack" / "onslaught-lore.v1.index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            duplicate = dict(index["documents"][0])
            duplicate["relativePath"] = "Second.md"
            index["documents"].append(duplicate)
            index["documentCount"] = 2
            index_path.write_text(json.dumps(index), encoding="utf-8")

            failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}

            self.assertIn("bundle_lore_pack", failures)

    def test_lore_pack_inspection_rejects_duplicate_index_relative_path_case_insensitive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(bundle_dir)
            index_path = bundle_dir / "lore-pack" / "onslaught-lore.v1.index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            duplicate = dict(index["documents"][0])
            duplicate["id"] = "doc-000002"
            duplicate["relativePath"] = "start-here.md"
            index["documents"].append(duplicate)
            index["documentCount"] = 2
            index_path.write_text(json.dumps(index), encoding="utf-8")

            failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}

            self.assertIn("bundle_lore_pack", failures)

    def test_lore_pack_inspection_rejects_duplicate_content_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(bundle_dir)
            content_path = bundle_dir / "lore-pack" / "onslaught-lore.v1.jsonl"
            row = content_path.read_text(encoding="utf-8").strip()
            content_path.write_text(row + "\n" + row + "\n", encoding="utf-8")

            failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}

            self.assertIn("bundle_lore_pack", failures)

    def test_lore_pack_inspection_rejects_invalid_index_document_id_without_echoing_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(bundle_dir, doc_id="doc/path/SecretLeakProbe")

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "FAIL")
            self.assertIn("invalid id", lore_pack_result.summary)
            self.assertNotIn("doc/path/SecretLeakProbe", lore_pack_result.summary)
            self.assertNotIn("SecretLeakProbe", lore_pack_result.summary)

    def test_lore_pack_inspection_rejects_invalid_content_document_id_without_echoing_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(bundle_dir, doc_id="doc-000001", content_doc_id="doc:SecretLeakProbe")

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "FAIL")
            self.assertIn("invalid id", lore_pack_result.summary)
            self.assertNotIn("doc:SecretLeakProbe", lore_pack_result.summary)
            self.assertNotIn("SecretLeakProbe", lore_pack_result.summary)

    def test_lore_pack_inspection_accepts_case_variant_content_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_lore_pack_payload(bundle_dir, doc_id="doc-000001", content_doc_id="DOC-000001")

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "PASS")

    def test_lore_pack_inspection_accepts_dot_segment_packed_links_for_runtime_navigation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_two_row_lore_pack_payload(
                bundle_dir,
                ("doc-000001", "folder/Start.md", "# Start\n\n[Other](./Other.md)\n"),
                ("doc-000002", "folder/Other.md", "# Other\n\nSynthetic fixture.\n"),
            )

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "PASS")

    def test_lore_pack_inspection_rejects_above_root_packed_links_without_echoing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_two_row_lore_pack_payload(
                bundle_dir,
                ("doc-000001", "Start.md", "# Start\n\n[Deep](../Deep.md)\n"),
                ("doc-000002", "Deep.md", "# Deep\n\nSynthetic fixture.\n"),
            )

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "FAIL")
            self.assertIn("unresolved packed links", lore_pack_result.summary)
            self.assertNotIn("../Deep.md", lore_pack_result.summary)

    def test_lore_pack_inspection_accepts_encoded_in_root_dot_segment_packed_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_two_row_lore_pack_payload(
                bundle_dir,
                ("doc-000001", "folder/Start.md", "# Start\n\n[Other](%2e%2e/Other.md)\n"),
                ("doc-000002", "Other.md", "# Other\n\nSynthetic fixture.\n"),
            )

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "PASS")

    def test_lore_pack_inspection_rejects_encoded_above_root_packed_link_without_echoing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_two_row_lore_pack_payload(
                bundle_dir,
                ("doc-000001", "Start.md", "# Start\n\n[Deep](%2e%2e/SecretLeakProbe.md)\n"),
                ("doc-000002", "SecretLeakProbe.md", "# Deep\n\nSynthetic fixture.\n"),
            )

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "FAIL")
            self.assertIn("unresolved packed links", lore_pack_result.summary)
            self.assertNotIn("%2e%2e/SecretLeakProbe.md", lore_pack_result.summary)
            self.assertNotIn("SecretLeakProbe", lore_pack_result.summary)

    def test_lore_pack_inspection_rejects_above_root_root_index_fallback_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_two_row_lore_pack_payload(
                bundle_dir,
                ("doc-000001", "Start.md", "# Start\n\n[Index](../_index.md)\n"),
                ("doc-000002", "_index.md", "# Index\n\nSynthetic fixture.\n"),
            )

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "FAIL")
            self.assertIn("unresolved packed links", lore_pack_result.summary)
            self.assertNotIn("../_index.md", lore_pack_result.summary)

    def test_lore_pack_inspection_rejects_above_root_suffix_fallback_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            self._write_two_row_lore_pack_payload(
                bundle_dir,
                ("doc-000001", "Start.md", "# Start\n\n[Suffix](../SecretLeakProbe)\n"),
                ("doc-000002", ".md", "# Hidden Suffix Fallback\n\nSynthetic fixture.\n"),
            )

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "FAIL")
            self.assertIn("unresolved packed links", lore_pack_result.summary)
            self.assertNotIn("../SecretLeakProbe", lore_pack_result.summary)

    def test_lore_pack_inspection_rejects_non_object_content_row_generically(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            bundle_dir = root / "bundle"
            self._write_publish_payload(bundle_dir / "app")
            self._write_required_root_payload(bundle_dir)
            content_path = bundle_dir / "lore-pack" / "onslaught-lore.v1.jsonl"
            content_path.write_text(json.dumps(["SecretLeakProbe"]) + "\n", encoding="utf-8")

            lore_pack_result = self._lore_pack_result(bundle_dir)

            self.assertEqual(lore_pack_result.status, "FAIL")
            self.assertIn("row 1 is invalid", lore_pack_result.summary)
            self.assertNotIn("SecretLeakProbe", lore_pack_result.summary)

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
        for file_name in ("BEA.exe", "terrain.bin", "facility.obj", "tutorial.ogg"):
            with self.subTest(file_name=file_name), tempfile.TemporaryDirectory() as temp_root:
                root = Path(temp_root)
                publish_dir = root / "publish"
                bundle_dir = root / "bundle"
                zip_path = root / "payload.zip"
                self._write_publish_payload(publish_dir)
                probe.stage_portable_bundle(publish_dir, bundle_dir)
                payload_path = bundle_dir / "app" / "game" / file_name
                payload_path.parent.mkdir(parents=True, exist_ok=True)
                payload_path.write_bytes(b"not ok")

                folder_failures = {item.key for item in probe.inspect_folder(bundle_dir, "bundle") if item.status == "FAIL"}
                exit_code, _ = probe.create_zip(bundle_dir, zip_path)
                self.assertEqual(exit_code, 0)
                zip_failures = {item.key for item in probe.inspect_zip(zip_path) if item.status == "FAIL"}

                self.assertIn("bundle_payload_safety", folder_failures)
                self.assertIn("zip_payload_safety", zip_failures)

    def test_zip_inspection_rejects_local_overlay_segments_inside_app_folder(self) -> None:
        for segment in ("local-rom-input", "mcps"):
            with self.subTest(segment=segment):
                with tempfile.TemporaryDirectory() as temp_root:
                    root = Path(temp_root)
                    publish_dir = root / "publish"
                    bundle_dir = root / "bundle"
                    zip_path = root / f"{segment}.zip"
                    self._write_publish_payload(publish_dir)
                    probe.stage_portable_bundle(publish_dir, bundle_dir)
                    payload_path = bundle_dir / "app" / segment / "payload.txt"
                    payload_path.parent.mkdir(parents=True, exist_ok=True)
                    payload_path.write_text("not ok\n", encoding="utf-8")

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

    def test_launch_smoke_waits_for_a_fla_ui_window_and_cannot_skip_after_launch(self) -> None:
        source = (
            probe.ROOT
            / "OnslaughtCareerEditor.UiTests"
            / "WinUiLaunchSmokeTests.cs"
        ).read_text(encoding="utf-8")
        launched_body = source.split("app = Application.Launch(startInfo);", 1)[1]

        self.assertIn("app.GetMainWindow(automation, TimeSpan.FromSeconds(5))", launched_body)
        self.assertIn("TimeSpan.FromSeconds(60)", launched_body)
        self.assertIn("The extracted WinUI main window did not appear", launched_body)
        self.assertNotIn("Assert.Ignore", launched_body)

    def test_lore_smoke_uses_the_invoke_pattern_search_hit_fixture(self) -> None:
        self.assertEqual(
            probe.LORE_SMOKE_FILTER,
            "FullyQualifiedName~WinUiLoreDepthSmokeTests.LoreSearchHits_OpenTheMatchingDocument",
        )
        self.assertNotIn("WinUiLoreInteractionSmokeTests", probe.LORE_SMOKE_FILTER)

    def test_safe_copy_workflow_receipt_accepts_one_owned_process_and_bounded_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            paths = self._write_valid_safe_copy_workflow(Path(temp_root))

            checks = probe.inspect_safe_copy_workflow(
                paths["approved_root"],
                paths["preregistration"],
                paths["receipt"],
                paths["extracted_exe"],
                expected_timeout_seconds=180,
            )

            self.assertEqual([item for item in checks if item.status == "FAIL"], [])
            self.assertEqual(
                {item.key for item in checks},
                {
                    "safe_copy_preregistration",
                    "safe_copy_source_unchanged",
                    "safe_copy_output_boundary",
                    "safe_copy_output_hash",
                    "safe_copy_negative_controls",
                    "safe_copy_app_report",
                    "safe_copy_process_cleanup",
                },
            )

    def test_safe_copy_smoke_targets_the_exact_extracted_workflow(self) -> None:
        self.assertEqual(
            probe.SAFE_COPY_SMOKE_FILTER,
            (
                "FullyQualifiedName~WinUiSafeCopyManagerSmokeTests."
                "ExtractedPortableApp_CreatesSyntheticSafeCopyAndProvesNegativeControls"
            ),
        )
        self.assertEqual(probe.SAFE_COPY_SMOKE_TEST_TIMEOUT_SECONDS, 600)

    def test_safe_copy_workflow_root_keeps_patch_staging_under_legacy_max_path(self) -> None:
        self.assertEqual(probe.SAFE_COPY_WORKFLOW_DIR_NAME, "sc")
        profile_name = "safe-game-copy-20000101-000000-000-12345678"
        staged_name = ".onslaught-patch-12345678901234567890123456789012.tmp"
        staged_path = (
            probe.DEFAULT_OUT_ROOT
            / probe.SAFE_COPY_WORKFLOW_DIR_NAME
            / "appdata"
            / "OnslaughtCareerEditor"
            / "GameProfiles"
            / profile_name
            / staged_name
        ).resolve()
        self.assertLess(len(str(staged_path)), 260, str(staged_path))

    def test_safe_copy_workflow_receipt_rejects_a_changed_source_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            paths = self._write_valid_safe_copy_workflow(Path(temp_root))
            (paths["source_root"] / "data" / "fixture.dat").write_bytes(b"changed-after-copy")

            checks = probe.inspect_safe_copy_workflow(
                paths["approved_root"],
                paths["preregistration"],
                paths["receipt"],
                paths["extracted_exe"],
                expected_timeout_seconds=180,
            )

            self.assertEqual(self._check_by_key(checks, "safe_copy_source_unchanged").status, "FAIL")

    def test_safe_copy_workflow_receipt_rejects_an_output_outside_approved_scratch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_root:
            root = Path(temp_root)
            paths = self._write_valid_safe_copy_workflow(root)
            escaped_target = root / "escaped-target"
            escaped_target.mkdir()
            (escaped_target / "onslaught-profile-manifest.json").write_text("{}", encoding="utf-8")
            receipt = json.loads(paths["receipt"].read_text(encoding="utf-8"))
            receipt["targetRoot"] = str(escaped_target.resolve())
            receipt["targetTreeSha256"] = self._tree_hash(escaped_target)
            paths["receipt"].write_text(json.dumps(receipt), encoding="utf-8")

            checks = probe.inspect_safe_copy_workflow(
                paths["approved_root"],
                paths["preregistration"],
                paths["receipt"],
                paths["extracted_exe"],
                expected_timeout_seconds=180,
            )

            self.assertEqual(self._check_by_key(checks, "safe_copy_output_boundary").status, "FAIL")

    @staticmethod
    def _check_by_key(checks: list[probe.CheckResult], key: str) -> probe.CheckResult:
        return next(check for check in checks if check.key == key)

    def _write_valid_safe_copy_workflow(self, root: Path) -> dict[str, Path]:
        approved_root = root / "safe-copy-workflow"
        source_root = approved_root / "source-fixture"
        output_root = approved_root / "appdata" / "OnslaughtCareerEditor" / "GameProfiles"
        target_root = output_root / "safe-game-copy-test"
        extracted_exe = approved_root / "extracted" / probe.APP_EXE
        preregistration_path = approved_root / "safe-copy-preregistration.json"
        receipt_path = approved_root / "safe-copy-result.json"
        for path, content in (
            (source_root / "BEA.exe", b"synthetic-source"),
            (source_root / "data" / "fixture.dat", b"fixture-data"),
            (target_root / "BEA.exe", b"synthetic-target"),
            (target_root / "onslaught-profile-manifest.json", b"{}"),
            (extracted_exe, b"extracted-app"),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

        source_hash = self._tree_hash(source_root)
        preregistration_path.write_text(
            json.dumps(
                {
                    "schema": "winui-extracted-safe-copy-preregistration.v1",
                    "experiment": probe.SAFE_COPY_EXPERIMENT,
                    "executablePath": str(extracted_exe.resolve()),
                    "executableSha256": hashlib.sha256(extracted_exe.read_bytes()).hexdigest(),
                    "processIds": [4242],
                    "timeoutSeconds": 180,
                }
            ),
            encoding="utf-8",
        )
        receipt_path.write_text(
            json.dumps(
                {
                    "schema": "winui-extracted-safe-copy-result.v1",
                    "status": "pass",
                    "experiment": probe.SAFE_COPY_EXPERIMENT,
                    "approvedRoot": str(approved_root.resolve()),
                    "sourceRoot": str(source_root.resolve()),
                    "outputRoot": str(output_root.resolve()),
                    "targetRoot": str(target_root.resolve()),
                    "sourceTreeSha256Before": source_hash,
                    "sourceTreeSha256After": source_hash,
                    "targetTreeSha256": self._tree_hash(target_root),
                    "processIds": [4242],
                    "processExitClean": True,
                    "negativeControls": {
                        "missingInput": "pass",
                        "sourceOutputAlias": "pass",
                    },
                    "appReportedSummary": (
                        "Safe game copy preparation complete.\n"
                        "Only files inside the safe copy were changed; no game process was started."
                    ),
                }
            ),
            encoding="utf-8",
        )
        return {
            "approved_root": approved_root,
            "source_root": source_root,
            "output_root": output_root,
            "target_root": target_root,
            "extracted_exe": extracted_exe,
            "preregistration": preregistration_path,
            "receipt": receipt_path,
        }

    @staticmethod
    def _tree_hash(root: Path) -> str:
        digest = hashlib.sha256()
        for path in sorted(
            (item for item in root.rglob("*") if item.is_file()),
            key=lambda item: item.relative_to(root).as_posix(),
        ):
            digest.update((path.relative_to(root).as_posix() + "\n").encode("utf-8"))
            digest.update((hashlib.sha256(path.read_bytes()).hexdigest() + "\n").encode("ascii"))
        return digest.hexdigest()

    def _write_required_root_payload(self, bundle_dir: Path) -> None:
        for relative_path in (probe.ROOT_LAUNCHER, probe.ROOT_README, probe.ROOT_LICENSE, "lore-book/BOOK.md"):
            path = bundle_dir / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(relative_path, encoding="utf-8")
        self._write_lore_pack_payload(bundle_dir)

    def _lore_pack_result(self, bundle_dir: Path) -> probe.CheckResult:
        return next(item for item in probe.inspect_folder(bundle_dir, "bundle") if item.key == "bundle_lore_pack")

    def _write_lore_pack_payload(
        self,
        bundle_dir: Path,
        *,
        content: str = "# Start\n\nSynthetic fixture.\n",
        relative_path: str = "Overview.md",
        content_relative_path: str | None = None,
        doc_id: str = "doc-000001",
        content_doc_id: str | None = None,
    ) -> None:
        pack_dir = bundle_dir / "lore-pack"
        pack_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        row = {
            "id": content_doc_id or doc_id,
            "relativePath": content_relative_path or relative_path,
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
                    "id": doc_id,
                    "relativePath": relative_path,
                    "title": row["title"],
                    "sha256": row["sha256"],
                    "byteLength": row["byteLength"],
                    "order": 0,
                }
            ],
        }
        (pack_dir / "onslaught-lore.v1.index.json").write_text(json.dumps(index), encoding="utf-8")
        (pack_dir / "onslaught-lore.v1.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")

    def _write_two_row_lore_pack_payload(self, bundle_dir: Path, *documents: tuple[str, str, str]) -> None:
        pack_dir = bundle_dir / "lore-pack"
        pack_dir.mkdir(parents=True, exist_ok=True)
        index_rows = []
        content_rows = []
        for order, (doc_id, relative_path, content) in enumerate(documents):
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            byte_length = len(content.encode("utf-8"))
            index_rows.append(
                {
                    "id": doc_id,
                    "relativePath": relative_path,
                    "title": "Start" if order == 0 else "Other",
                    "sha256": digest,
                    "byteLength": byte_length,
                    "order": order,
                }
            )
            content_rows.append(
                json.dumps(
                    {
                        "id": doc_id,
                        "relativePath": relative_path,
                        "title": "Start" if order == 0 else "Other",
                        "sha256": digest,
                        "byteLength": byte_length,
                        "content": content,
                    }
                )
            )
        index = {
            "schema": "onslaught-lore-pack.v1",
            "sourceRoot": "lore-book",
            "documentCount": len(index_rows),
            "documents": index_rows,
        }
        (pack_dir / "onslaught-lore.v1.index.json").write_text(json.dumps(index), encoding="utf-8")
        (pack_dir / "onslaught-lore.v1.jsonl").write_text("\n".join(content_rows) + "\n", encoding="utf-8")


class WinUiZipPackageProbePublishBudgetTests(unittest.TestCase):
    def test_publish_step_budget_is_900_seconds(self) -> None:
        self.assertEqual(probe.PUBLISH_STEP_TIMEOUT_SECONDS, 900)

    def test_run_publish_consumes_the_publish_step_budget(self) -> None:
        with unittest.mock.patch.object(probe, "run", return_value=(0, "")) as run_mock:
            exit_code, _ = probe.run_publish(Path("publish"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(run_mock.call_args.kwargs["timeout_seconds"], probe.PUBLISH_STEP_TIMEOUT_SECONDS)


if __name__ == "__main__":
    unittest.main()
