#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Authored POSIX descriptor-relative publication controls; no game inputs or native Windows claims."""
from pathlib import Path
import hashlib
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import safe_generated_output as output


@unittest.skipIf(os.name == "nt", "POSIX descriptor-relative publication controls")
class DescriptorPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "sources"
        self.source.mkdir()
        self.original = self.source / "catalog.json"
        self.original.write_bytes(b"original source")
        self.destination_root = self.root / "output"

    def swap(self):
        held = self.root / "held-output"
        self.destination_root.rename(held)
        self.destination_root.symlink_to(self.source, target_is_directory=True)
        return held

    def test_text_and_binary_successful_replacements_are_complete(self):
        with output.SecuredOutputRoot(self.destination_root) as secured:
            destination = self.destination_root / "catalog.json"
            secured.atomic_write_text(destination, "first\n")
            secured.atomic_write_bytes(destination, b"second\0payload")
            self.assertEqual(b"second\0payload", destination.read_bytes())
            self.assertEqual([], list(self.destination_root.glob(".*.tmp-*")))

    def test_new_json_preserves_existing_destination_and_cleans_its_temporary(self):
        with output.SecuredOutputRoot(self.destination_root) as secured:
            destination = self.destination_root / "catalog.json"
            secured.atomic_write_new_json(destination, {"first": True})
            first = destination.read_bytes()
            with self.assertRaisesRegex(output.UnsafeGeneratedOutputError, "already exists"):
                secured.atomic_write_new_json(destination, {"replacement": True})
            self.assertEqual(first, destination.read_bytes())
            self.assertEqual([], list(self.destination_root.glob(".*.tmp-*")))

    def test_new_json_refuses_file_moved_into_destination_at_atomic_publish(self):
        destination = self.destination_root / "catalog.json"
        before = self.original.stat()
        rename = output._posix_rename_no_replace
        def move_original(directory_fd, source_name, destination_name):
            self.assertEqual("catalog.json", destination_name)
            os.rename(self.original, destination)
            return rename(directory_fd, source_name, destination_name)
        with output.SecuredOutputRoot(self.destination_root) as secured, \
                patch.object(output, "_posix_rename_no_replace", side_effect=move_original), \
                self.assertRaisesRegex(output.UnsafeGeneratedOutputError, "already exists"):
            secured.atomic_write_new_json(destination, {"metadata": True})
        self.assertEqual(b"original source", destination.read_bytes())
        self.assertEqual((before.st_dev, before.st_ino), (destination.stat().st_dev, destination.stat().st_ino))
        self.assertEqual([], list(self.destination_root.glob(".*.tmp-*")))

    def test_new_json_fails_closed_without_atomic_no_replace_support(self):
        with output.SecuredOutputRoot(self.destination_root) as secured, \
                patch.object(output.ctypes, "CDLL", side_effect=OSError("missing primitive")), \
                self.assertRaisesRegex(output.UnsafeGeneratedOutputError, "no-replace publication unavailable"):
            secured.atomic_write_new_json(self.destination_root / "catalog.json", {"metadata": True})
        self.assertFalse((self.destination_root / "catalog.json").exists())
        self.assertEqual([], list(self.destination_root.glob(".*.tmp-*")))

    def test_cached_output_parent_rename_and_symlink_refuses_before_creation(self):
        with output.SecuredOutputRoot(self.destination_root) as secured:
            held = self.swap()
            for binary in (False, True):
                with self.subTest(binary=binary), self.assertRaises(output.UnsafeGeneratedOutputError):
                    if binary:
                        secured.atomic_write_bytes(self.destination_root / "catalog.json", b"new")
                    else:
                        secured.atomic_write_text(self.destination_root / "catalog.json", "new")
            self.assertEqual([], list(held.iterdir()))
            self.assertEqual(b"original source", self.original.read_bytes())

    def test_rename_during_writer_never_redirects_write_or_cleanup(self):
        for binary in (False, True):
            with self.subTest(binary=binary):
                root = self.root / ("binary" if binary else "text")
                root.mkdir()
                destination = root / "catalog.json"
                with output.SecuredOutputRoot(root) as secured:
                    writer = secured.atomic_binary_writer(destination) if binary else secured.atomic_text_writer(destination)
                    with self.assertRaises(output.UnsafeGeneratedOutputError):
                        with writer as stream:
                            stream.write(b"candidate" if binary else "candidate")
                            temporary = next(root.glob(".catalog.json.tmp-*"))
                            held = self.root / (root.name + "-held")
                            root.rename(held)
                            root.symlink_to(self.source, target_is_directory=True)
                            trap = self.source / temporary.name
                            trap.write_bytes(b"unrelated source-side temporary")
                    self.assertEqual(b"original source", self.original.read_bytes())
                    self.assertEqual(b"unrelated source-side temporary", trap.read_bytes())
                    self.assertEqual([], list(held.glob(".catalog.json.tmp-*")))

    def test_last_moment_directory_swap_cannot_redirect_replace(self):
        replace = os.replace
        with output.SecuredOutputRoot(self.destination_root) as secured:
            def swapping_replace(source, destination, **kwargs):
                self.assertEqual(self.destination_root / "catalog.json", secured.root / destination)
                self.assertIsInstance(kwargs.get("src_dir_fd"), int)
                self.assertEqual(kwargs["src_dir_fd"], kwargs.get("dst_dir_fd"))
                self.swap()
                return replace(source, destination, **kwargs)
            with patch.object(output.os, "replace", side_effect=swapping_replace), \
                    self.assertRaises(output.UnsafeGeneratedOutputError):
                secured.atomic_write_text(self.destination_root / "catalog.json", "generated only in held output")
        self.assertEqual(b"original source", self.original.read_bytes())
        self.assertEqual("generated only in held output", (self.root / "held-output/catalog.json").read_text())

    def test_new_nested_directory_uses_held_parent_after_path_swap(self):
        mkdir = os.mkdir
        with output.SecuredOutputRoot(self.destination_root) as secured:
            def swapping_mkdir(name, *args, **kwargs):
                if name == "nested":
                    self.assertIsInstance(kwargs.get("dir_fd"), int)
                    self.swap()
                return mkdir(name, *args, **kwargs)
            with patch.object(output.os, "mkdir", side_effect=swapping_mkdir), \
                    self.assertRaises(output.UnsafeGeneratedOutputError):
                secured.atomic_write_text(self.destination_root / "nested/catalog.json", "new")
        self.assertFalse((self.source / "nested").exists())
        self.assertEqual(b"original source", self.original.read_bytes())

    def test_symlink_and_hardlink_destinations_remain_refused(self):
        with output.SecuredOutputRoot(self.destination_root) as secured:
            for name, link in (("symbolic.json", os.symlink), ("hard.json", os.link)):
                destination = self.destination_root / name
                link(self.original, destination)
                with self.subTest(name=name), self.assertRaises(output.UnsafeGeneratedOutputError):
                    secured.atomic_write_bytes(destination, b"new")
        self.assertEqual(b"original source", self.original.read_bytes())

    def test_replaced_temporary_is_not_published_or_deleted_as_our_file(self):
        with output.SecuredOutputRoot(self.destination_root) as secured:
            with self.assertRaises(output.UnsafeGeneratedOutputError):
                with secured.atomic_binary_writer(self.destination_root / "catalog.json") as stream:
                    stream.write(b"our private candidate")
                    temporary = next(self.destination_root.glob(".catalog.json.tmp-*"))
                    temporary.unlink()
                    os.link(self.original, temporary)
            self.assertEqual(b"original source", self.original.read_bytes())
            self.assertEqual(b"original source", temporary.read_bytes())
            self.assertFalse((self.destination_root / "catalog.json").exists())

    def test_writer_exception_preserves_destination_and_cleans_only_owned_temporary(self):
        with output.SecuredOutputRoot(self.destination_root) as secured:
            destination = self.destination_root / "catalog.json"
            destination.write_bytes(b"earlier generated result")
            with self.assertRaisesRegex(RuntimeError, "injected"):
                with secured.atomic_binary_writer(destination) as stream:
                    stream.write(b"partial")
                    raise RuntimeError("injected")
            self.assertEqual(b"earlier generated result", destination.read_bytes())
            self.assertEqual([], list(self.destination_root.glob(".*.tmp-*")))

    def test_fdopen_setup_failure_closes_descriptor_and_removes_owned_temporary(self):
        native_open = os.open
        descriptors = []
        def record_open(name, flags, *args, **kwargs):
            fd = native_open(name, flags, *args, **kwargs)
            if flags & os.O_CREAT:
                descriptors.append(fd)
            return fd
        with output.SecuredOutputRoot(self.destination_root) as secured:
            with patch.object(output.os, "open", side_effect=record_open), \
                    patch.object(output.os, "fdopen", side_effect=OSError("injected fdopen setup")), \
                    self.assertRaisesRegex(OSError, "fdopen setup"):
                secured.atomic_write_text(self.destination_root / "catalog.json", "new")
            self.assertEqual(1, len(descriptors))
            with self.assertRaises(OSError):
                os.fstat(descriptors[0])
            self.assertEqual([], list(self.destination_root.glob(".*.tmp-*")))

    def test_actual_video_manifest_caller_still_publishes_complete_outputs(self):
        import export_video_manifest as video
        payload = b"AUTH authored video metadata fixture"
        (self.source / "01.vid").write_bytes(payload)
        paths = video.write_manifest_outputs(self.source, self.destination_root)
        manifest = json.loads(paths[0].read_text())
        self.assertEqual(1, manifest["summary"]["file_count"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), manifest["files"][0]["sha256"])
        self.assertIn("01.vid", paths[1].read_text())
        self.assertEqual(payload, (self.source / "01.vid").read_bytes())

    def test_actual_video_manifest_caller_refuses_redirect_after_source_read(self):
        import export_video_manifest as video
        (self.source / "01.vid").write_bytes(b"AUTH authored fixture")
        original = self.source / "manifest.json"
        original.write_bytes(b"original manifest-shaped source")
        build = video.build_manifest
        def swap(*args, **kwargs):
            result = build(*args, **kwargs)
            self.swap()
            return result
        with patch.object(video, "build_manifest", side_effect=swap), \
                self.assertRaises(output.UnsafeGeneratedOutputError):
            video.write_manifest_outputs(self.source, self.destination_root)
        self.assertEqual(b"original manifest-shaped source", original.read_bytes())


if __name__ == "__main__":
    unittest.main()
