#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import builtins
import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import lab_quarantine as quarantine


class LabQuarantineTests(unittest.TestCase):
    def quarantine_paths(self, root: Path):
        quarantine_root = root / "quarantine"
        quarantine_root.mkdir()
        return mock.patch.multiple(
            quarantine,
            QUARANTINE_ROOT=quarantine_root,
            MANIFEST=quarantine_root / "manifest.jsonl",
            PURGE_LOG=quarantine_root / "purge.log",
        )

    def test_stage_file_verifies_copy_records_receipt_and_removes_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source" / "marker.txt"
            source.parent.mkdir()
            source.write_bytes(b"recoverable evidence\n")

            with self.quarantine_paths(root):
                row = quarantine.stage(source, reason="test recovery")

                staged = Path(row["staged"])
                self.assertFalse(source.exists())
                self.assertEqual(b"recoverable evidence\n", staged.read_bytes())
                self.assertEqual(21, row["bytes"])
                self.assertEqual(
                    hashlib.sha256(b"recoverable evidence\n").hexdigest(),
                    row["sha256"],
                )
                recorded = [
                    json.loads(line)
                    for line in quarantine.MANIFEST.read_text(encoding="utf-8").splitlines()
                ]
                self.assertEqual([row], recorded)

                restored = quarantine.restore(row["id"])
                self.assertEqual(row, restored)
                self.assertEqual(b"recoverable evidence\n", source.read_bytes())
                self.assertEqual("", quarantine.MANIFEST.read_text(encoding="utf-8"))

    def test_stage_directory_then_restore_round_trips_exact_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source-tree"
            (source / "nested").mkdir(parents=True)
            (source / "empty-directory").mkdir()
            (source / "a.bin").write_bytes(b"a")
            (source / "nested" / "b.bin").write_bytes(b"bc")
            expected_sha = quarantine.tree_sha256(source)

            with self.quarantine_paths(root):
                row = quarantine.stage(source, reason="test tree")
                self.assertFalse(source.exists())
                self.assertEqual(3, row["bytes"])
                self.assertEqual(expected_sha, row["sha256"])

                restored = quarantine.restore(row["id"])
                self.assertEqual(row, restored)
                self.assertTrue(source.is_dir())
                self.assertTrue((source / "empty-directory").is_dir())
                self.assertEqual(expected_sha, quarantine.tree_sha256(source))
                self.assertEqual("", quarantine.MANIFEST.read_text(encoding="utf-8"))


class StageReparseRefusalTests(unittest.TestCase):
    """Stage must reject reparses before any target or quarantine mutation."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.quarantine_root = self.root / "quarantine"
        self.quarantine_root.mkdir()
        patcher = mock.patch.multiple(
            quarantine,
            QUARANTINE_ROOT=self.quarantine_root,
            MANIFEST=self.quarantine_root / "manifest.jsonl",
            PURGE_LOG=self.quarantine_root / "purge.log",
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def _is_at_or_under(path, root: Path) -> bool:  # noqa: ANN001
        try:
            Path(path).relative_to(root)
        except (TypeError, ValueError):
            return False
        return True

    def _assert_nested_directory_reparse_refused(self, kind: str) -> None:
        source = self.root / f"source-{kind}"
        source.mkdir()
        (source / "ordinary.bin").write_bytes(b"ordinary")
        external = self.root / f"external-{kind}"
        external.mkdir()
        secret = external / "external-secret.bin"
        secret.write_bytes(b"must-never-be-scanned-opened-or-copied")
        link = source / "linked-directory"
        if kind == "directory-symlink":
            os.symlink(external, link, target_is_directory=True)
        else:
            self.assertEqual("junction", kind)
            subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(external)],
                check=True,
                capture_output=True,
                text=True,
            )
        self.assertTrue(os.path.lexists(link))

        real_scandir = quarantine.os.scandir
        real_open = builtins.open
        real_copyfile = quarantine.shutil.copyfile
        touched = {"scanned": [], "opened": [], "copied": []}

        def recording_scandir(path):  # noqa: ANN001
            if self._is_at_or_under(path, link):
                touched["scanned"].append(str(path))
            return real_scandir(path)

        def recording_open(path, *args, **kwargs):  # noqa: ANN001,ANN002,ANN003
            if self._is_at_or_under(path, link):
                touched["opened"].append(str(path))
            return real_open(path, *args, **kwargs)

        def recording_copyfile(src, dst, *args, **kwargs):  # noqa: ANN001,ANN002,ANN003
            if self._is_at_or_under(src, link):
                touched["copied"].append(str(src))
            return real_copyfile(src, dst, *args, **kwargs)

        try:
            with mock.patch.object(
                quarantine.os, "scandir", recording_scandir
            ), mock.patch.object(
                builtins, "open", recording_open
            ), mock.patch.object(
                quarantine.shutil, "copyfile", recording_copyfile
            ), mock.patch.object(
                quarantine, "_append_manifest_row", wraps=quarantine._append_manifest_row
            ) as append_manifest:
                with self.assertRaises((SystemExit, RuntimeError)):
                    quarantine.stage(source, reason=f"refuse nested {kind}")

            self.assertEqual(
                {"scanned": [], "opened": [], "copied": []},
                touched,
                "stage touched external target content through a directory reparse",
            )
            append_manifest.assert_not_called()
            self.assertFalse(quarantine.MANIFEST.exists(), "manifest row was appended")
            self.assertTrue(source.is_dir(), "source was removed despite refusal")
            self.assertTrue(os.path.lexists(link), "source reparse was removed")
            self.assertEqual(
                b"must-never-be-scanned-opened-or-copied", secret.read_bytes()
            )
            self.assertEqual(
                [],
                list(self.quarantine_root.iterdir()),
                "stage left an unmanifested quarantine partial on refusal",
            )
        finally:
            if os.path.lexists(link):
                try:
                    os.unlink(link)
                except OSError:
                    os.rmdir(link)

    @unittest.skipUnless(os.name == "nt", "Windows reparse semantics")
    def test_stage_refuses_nested_directory_symlink_before_target_touch(self) -> None:
        self._assert_nested_directory_reparse_refused("directory-symlink")

    @unittest.skipUnless(os.name == "nt", "Windows reparse semantics")
    def test_stage_refuses_nested_junction_before_target_touch(self) -> None:
        self._assert_nested_directory_reparse_refused("junction")

    @unittest.skipUnless(os.name == "nt", "Windows reparse semantics")
    def test_stage_refuses_nested_file_symlink_before_target_touch(self) -> None:
        source = self.root / "source-file-symlink"
        source.mkdir()
        (source / "ordinary.bin").write_bytes(b"ordinary")
        external = self.root / "external-file.bin"
        external.write_bytes(b"must-never-be-opened-or-copied")
        link = source / "linked-file.bin"
        os.symlink(external, link)
        self.assertTrue(os.path.lexists(link))

        real_scandir = quarantine.os.scandir
        real_open = builtins.open
        real_copyfile = quarantine.shutil.copyfile
        touched = {"scanned": [], "opened": [], "copied": []}

        def recording_scandir(path):  # noqa: ANN001
            if self._is_at_or_under(path, link):
                touched["scanned"].append(str(path))
            return real_scandir(path)

        def recording_open(path, *args, **kwargs):  # noqa: ANN001,ANN002,ANN003
            if self._is_at_or_under(path, link):
                touched["opened"].append(str(path))
            return real_open(path, *args, **kwargs)

        def recording_copyfile(src, dst, *args, **kwargs):  # noqa: ANN001,ANN002,ANN003
            if self._is_at_or_under(src, link):
                touched["copied"].append(str(src))
            return real_copyfile(src, dst, *args, **kwargs)

        try:
            with mock.patch.object(
                quarantine.os, "scandir", recording_scandir
            ), mock.patch.object(
                builtins, "open", recording_open
            ), mock.patch.object(
                quarantine.shutil, "copyfile", recording_copyfile
            ), mock.patch.object(
                quarantine, "_append_manifest_row", wraps=quarantine._append_manifest_row
            ) as append_manifest:
                with self.assertRaises((SystemExit, RuntimeError)):
                    quarantine.stage(source, reason="refuse nested file symlink")

            self.assertEqual(
                {"scanned": [], "opened": [], "copied": []},
                touched,
                "stage touched external target bytes through a file symlink",
            )
            append_manifest.assert_not_called()
            self.assertFalse(quarantine.MANIFEST.exists(), "manifest row was appended")
            self.assertTrue(source.is_dir(), "source was removed despite refusal")
            self.assertTrue(os.path.lexists(link), "source file symlink was removed")
            self.assertEqual(b"must-never-be-opened-or-copied", external.read_bytes())
            self.assertEqual(
                [],
                list(self.quarantine_root.iterdir()),
                "stage left an unmanifested quarantine partial on refusal",
            )
        finally:
            if os.path.lexists(link):
                os.unlink(link)

    @unittest.skipUnless(os.name == "nt", "Windows reparse semantics")
    def test_stage_refuses_directory_and_file_reparse_roots_before_resolve(self) -> None:
        directory_target = self.root / "root-directory-target"
        directory_target.mkdir()
        (directory_target / "external.bin").write_bytes(b"external")
        file_target = self.root / "root-file-target.bin"
        file_target.write_bytes(b"external-file")
        cases = []
        directory_symlink = self.root / "root-directory-symlink"
        os.symlink(directory_target, directory_symlink, target_is_directory=True)
        cases.append(("directory-symlink", directory_symlink))
        junction = self.root / "root-junction"
        subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(directory_target)],
            check=True,
            capture_output=True,
            text=True,
        )
        cases.append(("junction", junction))
        file_symlink = self.root / "root-file-symlink.bin"
        os.symlink(file_target, file_symlink)
        cases.append(("file-symlink", file_symlink))

        try:
            for kind, link in cases:
                with self.subTest(kind=kind), mock.patch.object(
                    quarantine,
                    "_refuse_tree_reparses",
                    side_effect=AssertionError("tree target was inspected"),
                ), mock.patch.object(
                    quarantine,
                    "_plain_file_identity",
                    side_effect=AssertionError("file target was opened"),
                ), mock.patch.object(
                    quarantine,
                    "_stage_copy_tree",
                    side_effect=AssertionError("target was copied"),
                ), mock.patch.object(
                    quarantine,
                    "_append_manifest_row",
                    side_effect=AssertionError("manifest append ran"),
                ):
                    with self.assertRaises(SystemExit):
                        quarantine.stage(link, reason=f"refuse root {kind}")
                    self.assertTrue(os.path.lexists(link), "root reparse was removed")
                    self.assertFalse(quarantine.MANIFEST.exists())
                    self.assertEqual([], list(self.quarantine_root.iterdir()))
            self.assertEqual(b"external", (directory_target / "external.bin").read_bytes())
            self.assertEqual(b"external-file", file_target.read_bytes())
        finally:
            for _, link in cases:
                if os.path.lexists(link):
                    try:
                        os.unlink(link)
                    except OSError:
                        os.rmdir(link)

    @unittest.skipUnless(os.name == "nt", "Windows reparse semantics")
    def test_stage_copy_refuses_directory_swapped_after_source_identity(self) -> None:
        source = self.root / "source-late-junction"
        child = source / "child"
        child.mkdir(parents=True)
        (source / "ordinary.bin").write_bytes(b"ordinary")
        external = self.root / "late-external"
        external.mkdir()
        secret = external / "external-secret.bin"
        secret.write_bytes(b"must-never-be-copied-after-identity")
        aside = self.root / "plain-child-aside"
        real_identity = quarantine._identity
        real_scandir = quarantine.os.scandir
        real_open = builtins.open
        real_copyfile = quarantine.shutil.copyfile
        state = {
            "swapped": False,
            "blocked": False,
            "scanned": [],
            "opened": [],
            "copied": [],
        }

        def identity_then_swap(root: Path):
            identity = real_identity(root)
            if Path(root) == source and not state["swapped"]:
                try:
                    child.rename(aside)
                except OSError:
                    state["blocked"] = True
                    return identity
                subprocess.run(
                    ["cmd.exe", "/d", "/c", "mklink", "/J", str(child), str(external)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                state["swapped"] = True
            return identity

        def recording_scandir(path):  # noqa: ANN001
            if self._is_at_or_under(path, child) and state["swapped"]:
                state["scanned"].append(str(path))
            return real_scandir(path)

        def recording_open(path, *args, **kwargs):  # noqa: ANN001,ANN002,ANN003
            if self._is_at_or_under(path, child) and state["swapped"]:
                state["opened"].append(str(path))
            return real_open(path, *args, **kwargs)

        def recording_copyfile(src, dst, *args, **kwargs):  # noqa: ANN001,ANN002,ANN003
            if self._is_at_or_under(src, child) and state["swapped"]:
                state["copied"].append(str(src))
            return real_copyfile(src, dst, *args, **kwargs)

        try:
            with mock.patch.object(
                quarantine, "_identity", identity_then_swap
            ), mock.patch.object(
                quarantine.os, "scandir", recording_scandir
            ), mock.patch.object(
                builtins, "open", recording_open
            ), mock.patch.object(
                quarantine.shutil, "copyfile", recording_copyfile
            ), mock.patch.object(
                quarantine, "_append_manifest_row", wraps=quarantine._append_manifest_row
            ) as append_manifest:
                try:
                    quarantine.stage(source, reason="late junction after identity")
                    refused = False
                except (SystemExit, RuntimeError):
                    refused = True

            self.assertTrue(
                state["blocked"] or state["swapped"],
                "source identity attack seam never ran",
            )
            self.assertEqual([], state["scanned"], "external target was scanned")
            self.assertEqual([], state["opened"], "external target file was opened")
            self.assertEqual([], state["copied"], "external target file was copied")
            if state["blocked"]:
                self.assertFalse(refused, "blocked replacement should allow safe stage")
                append_manifest.assert_called_once()
            else:
                self.assertTrue(refused, "successful reparse swap was not refused")
                append_manifest.assert_not_called()
                self.assertFalse(
                    quarantine.MANIFEST.exists(), "manifest row was appended"
                )
                self.assertTrue(source.is_dir(), "source was removed despite refusal")
                self.assertTrue(
                    os.path.lexists(child), "late source junction was removed"
                )
                self.assertEqual(
                    [],
                    list(self.quarantine_root.iterdir()),
                    "late source reparse left an unmanifested destination partial",
                )
            self.assertEqual(b"must-never-be-copied-after-identity", secret.read_bytes())
        finally:
            if os.path.lexists(child) and state["swapped"]:
                try:
                    os.unlink(child)
                except OSError:
                    os.rmdir(child)
            if aside.exists() and not child.exists():
                aside.rename(child)

    @unittest.skipUnless(os.name == "nt", "Windows reparse semantics")
    def test_stage_copy_refuses_file_swapped_after_source_identity(self) -> None:
        source = self.root / "source-late-file-symlink.bin"
        original = b"original-plain-source"
        source.write_bytes(original)
        aside = self.root / "plain-source-aside.bin"
        external = self.root / "late-file-target.bin"
        external.write_bytes(b"must-never-be-opened-by-stage-copy")
        real_identity = quarantine._plain_file_identity
        state = {"swapped": False, "blocked": False}

        def identity_then_swap(path: Path):
            identity = real_identity(path)
            if Path(path) == source and not state["swapped"]:
                try:
                    source.rename(aside)
                except OSError:
                    state["blocked"] = True
                    return identity
                os.symlink(external, source)
                state["swapped"] = True
            return identity

        try:
            with mock.patch.object(
                quarantine, "_plain_file_identity", identity_then_swap
            ), mock.patch.object(
                quarantine,
                "_open_new_plain_file_fd",
                wraps=quarantine._open_new_plain_file_fd,
            ) as create_dest, mock.patch.object(
                quarantine, "_append_manifest_row", wraps=quarantine._append_manifest_row
            ) as append_manifest:
                try:
                    quarantine.stage(source, reason="late file symlink after identity")
                    refused = False
                except (SystemExit, RuntimeError):
                    refused = True

            self.assertTrue(
                state["blocked"] or state["swapped"],
                "plain-file identity attack seam never ran",
            )
            if state["blocked"]:
                self.assertFalse(refused, "blocked replacement should allow safe stage")
                create_dest.assert_called_once()
                append_manifest.assert_called_once()
            else:
                self.assertTrue(refused, "successful file symlink swap was not refused")
                create_dest.assert_not_called()
                append_manifest.assert_not_called()
                self.assertTrue(
                    os.path.lexists(source), "source file symlink was removed"
                )
                self.assertEqual(
                    original, aside.read_bytes(), "plain source bytes changed"
                )
                self.assertFalse(quarantine.MANIFEST.exists())
                self.assertEqual(
                    [],
                    list(self.quarantine_root.iterdir()),
                    "late file reparse created a destination hierarchy",
                )
            self.assertEqual(
                b"must-never-be-opened-by-stage-copy",
                external.read_bytes(),
                "external target bytes changed",
            )
        finally:
            if os.path.lexists(source) and state["swapped"]:
                os.unlink(source)
            if aside.exists() and not source.exists():
                aside.rename(source)

    @unittest.skipUnless(os.name == "nt", "Windows reparse semantics")
    def test_stage_destination_file_creation_refuses_raced_symlink(self) -> None:
        source = self.root / "destination-race-source.bin"
        source.write_bytes(b"source-bytes")
        external = self.root / "destination-race-target.bin"
        external.write_bytes(b"external-must-not-change")
        real_create = quarantine._open_new_plain_file_fd
        captured = {}

        def inject_then_create(path: Path) -> int:
            captured["dest"] = Path(path)
            os.symlink(external, path)
            return real_create(path)

        try:
            with mock.patch.object(
                quarantine, "_open_new_plain_file_fd", inject_then_create
            ), mock.patch.object(
                quarantine, "_append_manifest_row", wraps=quarantine._append_manifest_row
            ) as append_manifest:
                with self.assertRaises(RuntimeError):
                    quarantine.stage(source, reason="destination file symlink race")

            dest = captured["dest"]
            append_manifest.assert_not_called()
            self.assertEqual(b"source-bytes", source.read_bytes())
            self.assertTrue(os.path.lexists(dest), "raced destination link vanished")
            self.assertEqual(b"external-must-not-change", external.read_bytes())
            self.assertFalse(quarantine.MANIFEST.exists())
        finally:
            dest = captured.get("dest")
            if dest is not None and os.path.lexists(dest):
                os.unlink(dest)

    @unittest.skipUnless(os.name == "nt", "Windows reparse semantics")
    def test_stage_blocks_source_parent_replaced_by_junction(self) -> None:
        source_parent = self.root / "source-parent"
        source_parent.mkdir()
        source = source_parent / "evidence.bin"
        source.write_bytes(b"original-evidence")
        aside = self.root / "source-parent-aside"
        external_parent = self.root / "external-parent"
        external_parent.mkdir()
        external_source = external_parent / source.name
        external_source.write_bytes(b"external-evidence")
        real_refuse = quarantine._refuse_plain_file_reparse
        state = {"attempted": False, "blocked": False, "replaced": False}

        def refuse_then_replace_parent(side: str, path: Path) -> None:
            real_refuse(side, path)
            if side == "stage source before copy" and not state["attempted"]:
                state["attempted"] = True
                try:
                    source_parent.rename(aside)
                except OSError:
                    state["blocked"] = True
                    return
                subprocess.run(
                    [
                        "cmd.exe", "/d", "/c", "mklink", "/J",
                        str(source_parent), str(external_parent),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                state["replaced"] = True

        try:
            with mock.patch.object(
                quarantine, "_refuse_plain_file_reparse", refuse_then_replace_parent
            ):
                row = quarantine.stage(source, reason="parent junction attack")

            self.assertTrue(state["attempted"], "ancestor attack seam never ran")
            self.assertTrue(state["blocked"], "source parent replacement succeeded")
            self.assertFalse(state["replaced"])
            self.assertEqual(b"external-evidence", external_source.read_bytes())
            self.assertEqual(b"original-evidence", Path(row["staged"]).read_bytes())
        finally:
            if state["replaced"] and os.path.lexists(source_parent):
                try:
                    os.unlink(source_parent)
                except OSError:
                    os.rmdir(source_parent)
            if aside.exists() and not source_parent.exists():
                aside.rename(source_parent)

    def test_manifest_prefix_and_row_readback_remain_inside_append_mutex(self) -> None:
        manifest_path = self.quarantine_root / "manifest.jsonl"
        lock_dir = self.quarantine_root / ".manifest-append.lock"

        class LockAwareManifest:
            def __init__(self) -> None:
                self.read_calls = 0
                self.readback_saw_lock = None

            def exists(self) -> bool:
                return manifest_path.exists()

            def open(self, *args, **kwargs):  # noqa: ANN002,ANN003
                return manifest_path.open(*args, **kwargs)

            def read_bytes(self):
                self.read_calls += 1
                if self.read_calls == 2:
                    self.readback_saw_lock = lock_dir.is_file()
                return manifest_path.read_bytes()

        proxy = LockAwareManifest()
        row = {
            "id": "serialized-row",
            "original": "source",
            "staged": "destination",
            "stagedAtUtc": "now",
            "bytes": 1,
            "sha256": "digest",
            "reason": "mutex readback probe",
        }
        with mock.patch.object(quarantine, "MANIFEST", proxy):
            quarantine._append_manifest_row(row)

        self.assertEqual(2, proxy.read_calls)
        self.assertTrue(
            proxy.readback_saw_lock,
            "exact prefix+row readback escaped the serialized append scope",
        )
        self.assertTrue(lock_dir.is_file(), "permanent append mutex file missing")

    def test_manifest_readback_requires_exact_serialized_row_bytes(self) -> None:
        row = {
            "id": "exact-row",
            "original": "source",
            "staged": "destination",
            "stagedAtUtc": "now",
            "bytes": 1,
            "sha256": "digest",
            "reason": "exact byte probe",
        }
        original_fsync = quarantine.os.fsync
        state = {"rewritten": False}

        def reorder_row_after_fsync(fd):  # noqa: ANN001
            result = original_fsync(fd)
            parsed = json.loads(quarantine.MANIFEST.read_text(encoding="utf-8"))
            quarantine.MANIFEST.write_text(
                json.dumps(parsed, sort_keys=True) + "\n", encoding="utf-8"
            )
            state["rewritten"] = True
            return result

        with mock.patch.object(quarantine.os, "fsync", reorder_row_after_fsync):
            with self.assertRaises(RuntimeError):
                quarantine._append_manifest_row(row)

        self.assertTrue(state["rewritten"])

    @unittest.skipUnless(os.name == "nt", "Windows newline translation")
    def test_manifest_readback_detects_raw_newline_byte_change(self) -> None:
        row = {
            "id": "raw-newline-row",
            "original": "source",
            "staged": "destination",
            "stagedAtUtc": "now",
            "bytes": 1,
            "sha256": "digest",
            "reason": "raw byte probe",
        }
        original_fsync = quarantine.os.fsync
        state = {"rewritten": False}

        def normalize_newline_after_fsync(fd):  # noqa: ANN001
            result = original_fsync(fd)
            raw = quarantine.MANIFEST.read_bytes()
            self.assertIn(b"\r\n", raw)
            quarantine.MANIFEST.write_bytes(raw.replace(b"\r\n", b"\n"))
            state["rewritten"] = True
            return result

        with mock.patch.object(
            quarantine.os, "fsync", normalize_newline_after_fsync
        ):
            with self.assertRaises(RuntimeError):
                quarantine._append_manifest_row(row)

        self.assertTrue(state["rewritten"])

    def test_manifest_mutex_never_reclaims_an_old_unknown_holder(self) -> None:
        lock_dir = self.quarantine_root / ".manifest-append.lock"
        lock_dir.mkdir()
        marker = lock_dir / "holder.txt"
        marker.write_text("unknown live writer", encoding="utf-8")
        os.utime(marker, (0, 0))

        with mock.patch.object(
            quarantine.time, "monotonic", side_effect=[0.0, 11.0]
        ), mock.patch.object(quarantine.time, "sleep"):
            with self.assertRaises(RuntimeError):
                quarantine._acquire_manifest_mutex()

        self.assertTrue(lock_dir.is_dir(), "active/unknown mutex was reclaimed")

    @unittest.skipUnless(os.name == "nt", "Windows share-mode mutex")
    def test_manifest_mutex_handle_blocks_replacement_and_second_writer(self) -> None:
        mutex = quarantine._acquire_manifest_mutex()
        lock_path = self.quarantine_root / ".manifest-append.lock"
        aside = self.quarantine_root / ".manifest-append.lock-aside"
        try:
            with self.assertRaises(OSError):
                lock_path.rename(aside)
            with mock.patch.object(
                quarantine.time, "monotonic", side_effect=[0.0, 11.0]
            ), mock.patch.object(quarantine.time, "sleep"):
                with self.assertRaises(RuntimeError):
                    quarantine._acquire_manifest_mutex()
        finally:
            mutex.close()

        self.assertTrue(lock_path.is_file())
        self.assertFalse(aside.exists())

    def test_identity_unicode_order_matches_pathlib_not_str_casefold(self) -> None:
        tree = self.root / "unicode-order-tree"
        tree.mkdir()
        (tree / "ss.txt").write_bytes(b"double-s")
        (tree / "ß.txt").write_bytes(b"eszett")
        expected = quarantine.tree_sha256(tree)
        real_scan = quarantine._scan_plain_children

        def reverse_casefold_tie(directory: Path):
            children = real_scan(directory)
            if Path(directory) == tree:
                return sorted(
                    children,
                    key=lambda pair: 0 if pair[0].name == "ß.txt" else 1,
                )
            return children

        with mock.patch.object(
            quarantine, "_scan_plain_children", reverse_casefold_tie
        ):
            _, _, observed = quarantine._identity(tree)

        self.assertEqual(expected, observed)

    def test_stage_manifest_readback_failure_preserves_source_and_staged(self) -> None:
        source = self.root / "manifest-readback-source.bin"
        payload = b"preserve-both-after-readback-failure"
        source.write_bytes(payload)
        original_fsync = quarantine.os.fsync
        state = {"poisoned": False}

        def poison_manifest_after_fsync(fd):  # noqa: ANN001
            result = original_fsync(fd)
            if (
                not state["poisoned"]
                and quarantine.MANIFEST.exists()
                and quarantine.MANIFEST.stat().st_size
            ):
                rows = [
                    json.loads(line)
                    for line in quarantine.MANIFEST.read_text(
                        encoding="utf-8"
                    ).splitlines()
                    if line.strip()
                ]
                rows[-1]["bytes"] = 0
                quarantine.MANIFEST.write_text(
                    "\n".join(json.dumps(row) for row in rows) + "\n",
                    encoding="utf-8",
                )
                state["poisoned"] = True
            return result

        with mock.patch.object(quarantine.os, "fsync", poison_manifest_after_fsync):
            with self.assertRaises(RuntimeError):
                quarantine.stage(source, reason="poison manifest readback")

        self.assertTrue(state["poisoned"], "manifest fsync seam never ran")
        self.assertEqual(payload, source.read_bytes(), "source bytes were removed")
        rows = [
            json.loads(line)
            for line in quarantine.MANIFEST.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(1, len(rows), "durable failed-readback row disappeared")
        self.assertEqual(payload, Path(rows[0]["staged"]).read_bytes())

    def test_stage_postappend_rehash_failure_preserves_both_copies(self) -> None:
        source = self.root / "postappend-source.bin"
        original = b"original-before-append"
        changed = b"changed-after-append"
        source.write_bytes(original)
        real_append = quarantine._append_manifest_row
        captured = {}

        def append_then_mutate(row: dict) -> None:
            real_append(row)
            captured["row"] = row
            source.write_bytes(changed)

        with mock.patch.object(
            quarantine, "_append_manifest_row", append_then_mutate
        ):
            with self.assertRaises(RuntimeError):
                quarantine.stage(source, reason="postappend mutation probe")

        row = captured["row"]
        self.assertEqual(changed, source.read_bytes(), "source was removed")
        self.assertEqual(original, Path(row["staged"]).read_bytes())
        recorded = [
            json.loads(line)
            for line in quarantine.MANIFEST.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual([row], recorded, "durable row was manually edited away")

    @unittest.skipUnless(os.name == "nt", "Windows reparse semantics")
    def test_stage_final_census_refuses_reparse_before_removal(self) -> None:
        source = self.root / "final-census-source"
        source.mkdir()
        (source / "ordinary.bin").write_bytes(b"ordinary")
        external = self.root / "final-census-external"
        external.mkdir()
        link = source / "last-second-junction"
        real_identity = quarantine._identity
        state = {"identity_calls": 0, "injected": False}

        def identity_then_inject(root: Path):
            identity = real_identity(root)
            state["identity_calls"] += 1
            if state["identity_calls"] == 5:
                subprocess.run(
                    ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(external)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                state["injected"] = True
            return identity

        try:
            with mock.patch.object(
                quarantine, "_identity", identity_then_inject
            ), mock.patch.object(
                quarantine,
                "_remove_tree_readonly_only",
                wraps=quarantine._remove_tree_readonly_only,
            ) as remove_tree:
                with self.assertRaises((SystemExit, RuntimeError)):
                    quarantine.stage(source, reason="final census injection")

            self.assertTrue(state["injected"], "postappend dual rehash never completed")
            remove_tree.assert_not_called()
            self.assertTrue(source.is_dir(), "source was removed past final census")
            self.assertTrue(os.path.lexists(link), "injected junction was removed")
            rows = [
                json.loads(line)
                for line in quarantine.MANIFEST.read_text(
                    encoding="utf-8"
                ).splitlines()
                if line.strip()
            ]
            self.assertEqual(1, len(rows), "durable row should remain after refusal")
            self.assertTrue(Path(rows[0]["staged"]).is_dir())
        finally:
            if os.path.lexists(link):
                try:
                    os.unlink(link)
                except OSError:
                    os.rmdir(link)

    def test_stage_low_level_removal_rechecks_staged_identity(self) -> None:
        source = self.root / "low-level-dest-source"
        source.mkdir()
        (source / "evidence.bin").write_bytes(b"original-bytes")
        real_remove = quarantine._remove_tree_readonly_only
        state = {}

        def corrupt_then_remove(root: Path, **kwargs):
            staged = Path(kwargs["staged"])
            (staged / "evidence.bin").write_bytes(b"corrupted-after-census")
            state["staged"] = staged
            return real_remove(root, **kwargs)

        with mock.patch.object(
            quarantine, "_remove_tree_readonly_only", corrupt_then_remove
        ):
            with self.assertRaises(RuntimeError):
                quarantine.stage(source, reason="low-level staged recheck")

        self.assertTrue(source.is_dir(), "source was removed after staged corruption")
        self.assertEqual(
            b"corrupted-after-census",
            (state["staged"] / "evidence.bin").read_bytes(),
        )

    def test_stage_low_level_removal_rechecks_source_identity(self) -> None:
        source = self.root / "low-level-source-source"
        source.mkdir()
        (source / "evidence.bin").write_bytes(b"original-bytes")
        real_remove = quarantine._remove_tree_readonly_only
        state = {"injected": False}

        def add_then_remove(root: Path, **kwargs):
            (Path(root) / "late-evidence.bin").write_bytes(b"never-staged")
            state["injected"] = True
            return real_remove(root, **kwargs)

        with mock.patch.object(
            quarantine, "_remove_tree_readonly_only", add_then_remove
        ):
            with self.assertRaises(RuntimeError):
                quarantine.stage(source, reason="low-level source recheck")

        self.assertTrue(state["injected"])
        self.assertTrue(source.is_dir(), "source was removed after late source bytes")
        self.assertEqual(
            b"never-staged", (source / "late-evidence.bin").read_bytes()
        )

    @unittest.skipUnless(os.name == "nt", "DOS attribute semantics")
    def test_file_removal_failure_restores_dos_readonly_attribute(self) -> None:
        source = self.root / "readonly-sharing-failure.bin"
        source.write_bytes(b"evidence")
        os.chmod(source, stat.S_IREAD)

        def sharing_failure(self: Path, *args, **kwargs):  # noqa: ANN002,ANN003
            raise PermissionError(32, "sharing violation")

        with mock.patch.object(Path, "unlink", sharing_failure):
            with self.assertRaises(PermissionError):
                quarantine._remove_file_readonly_only(source)

        attrs = quarantine._file_attributes(source)
        self.assertIsNotNone(attrs)
        self.assertTrue(attrs & quarantine.FILE_ATTRIBUTE_READONLY)


class ResumeStageTests(unittest.TestCase):
    """Falsification gates for the audited interrupted-stage resume.

    The incident (card t_192a0def): a timeout-killed ``stage`` leaves an
    unmanifested D partial plus its original. A previous ad hoc resume got a
    binding reviewer RED. These tests exist so the tracked ``resume``
    subcommand cannot silently regress into that failure mode: each one
    breaks one invariant at a time and asserts the gate refuses BEFORE any
    destructive step.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.quarantine_root = root / "quarantine"
        self.quarantine_root.mkdir()
        patcher = mock.patch.multiple(
            quarantine,
            QUARANTINE_ROOT=self.quarantine_root,
            MANIFEST=self.quarantine_root / "manifest.jsonl",
            PURGE_LOG=self.quarantine_root / "purge.log",
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    # -- fixture helpers ---------------------------------------------------

    def make_source_and_partial(self, *, complete_dest: bool = False):
        source = self.quarantine_root / "20260823" / "c45-src"
        dest = self.quarantine_root / "20260824" / "4d82-c45-src"
        (source / "nested").mkdir(parents=True)
        (source / "a.bin").write_bytes(b"alpha")
        (source / "nested" / "b.bin").write_bytes(b"beta-gamma")
        expected_sha = quarantine.tree_sha256(source)

        # Simulate the timeout kill mid-copy: partial has only some files.
        shutil.copytree(source, dest)
        if not complete_dest:
            (dest / "nested" / "b.bin").unlink()
        return source, dest, expected_sha

    def manifest_rows(self) -> list[dict]:
        if not quarantine.MANIFEST.exists():
            return []
        return [
            json.loads(line)
            for line in quarantine.MANIFEST.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def assert_no_manifest(self) -> None:
        self.assertEqual([], self.manifest_rows())

    # -- the happy path ----------------------------------------------------

    def test_resume_completes_gates_manifests_and_removes_source_only(self) -> None:
        source, dest, expected_sha = self.make_source_and_partial()

        row = quarantine.resume(source, dest, reason="audited test resume")

        self.assertFalse(source.exists())
        self.assertTrue(dest.is_dir())
        self.assertEqual(15, row["bytes"])
        self.assertEqual(expected_sha, row["sha256"])
        self.assertEqual(str(dest), row["staged"])
        self.assertEqual("audited test resume", row["reason"])
        recorded = self.manifest_rows()
        self.assertEqual([row], recorded)
        self.assertEqual(expected_sha, quarantine.tree_sha256(dest))

    def test_resume_is_idempotent_safe_on_a_complete_copy(self) -> None:
        # Nothing missing at all (the t_192a0def 4d82 state): resume must
        # still work, retaining every file and copying nothing.
        source, dest, expected_sha = self.make_source_and_partial(complete_dest=True)

        row = quarantine.resume(source, dest, reason="content-complete partial")

        self.assertFalse(source.exists())
        self.assertEqual(expected_sha, quarantine.tree_sha256(dest))
        self.assertEqual([row], self.manifest_rows())

    def test_resume_heals_a_stale_partial_file_then_passes(self) -> None:
        # A partial file whose bytes differ from the source (stale copy from
        # before the kill) is detected by size/mtime compare and re-copied;
        # the run then gates, manifests, and removes only the source.
        source, dest, expected_sha = self.make_source_and_partial(complete_dest=True)
        (dest / "nested" / "b.bin").write_bytes(b"stale-copy")  # different bytes

        row = quarantine.resume(source, dest, reason="stale file heal")

        self.assertFalse(source.exists())
        self.assertEqual(15, row["bytes"])
        self.assertEqual(expected_sha, quarantine.tree_sha256(dest))
        self.assertEqual([row], self.manifest_rows())

    def test_resume_repairs_same_size_same_mtime_corruption_in_one_pass(self) -> None:
        # Reviewer RED falsification (6e672378): a dest file can share
        # size+mtime with its source yet hold different bytes. Retention is
        # BYTE-VERIFIED, so ONE resume pass must re-copy it and converge to
        # exact identity -- not retain the bad file forever.
        source, dest, expected_sha = self.make_source_and_partial(complete_dest=True)
        victim = dest / "nested" / "b.bin"
        before = victim.stat().st_mtime_ns
        victim.write_bytes(b"BETA-GAMMA")  # same length (10), different bytes
        os.utime(victim, ns=(before, before))  # mtime identical to source

        self.assertTrue(quarantine._file_bytes_differ(source / "nested" / "b.bin", victim))

        row = quarantine.resume(source, dest, reason="same-stat corruption repair")

        self.assertFalse(source.exists())
        self.assertEqual(expected_sha, quarantine.tree_sha256(dest))
        self.assertEqual(15, row["bytes"])
        self.assertEqual([row], self.manifest_rows())

    def test_unrepairable_copy_failure_gates_with_no_removal_no_manifest(self) -> None:
        # If the copy layer cannot repair a mismatch (here: copy2 sabotaged
        # so the dest keeps wrong bytes), the identity gate must refuse
        # BEFORE any manifest append or removal, leaving BOTH sides intact.
        source, dest, _ = self.make_source_and_partial(complete_dest=True)
        victim = dest / "nested" / "b.bin"
        victim.write_bytes(b"BETA-GAMMA")  # same size, different bytes

        real_copy2 = quarantine.shutil.copy2

        def sabotaged_copy2(src, dst, **kwargs):  # noqa: ANN001,ANN003
            real_copy2(src, dst, **kwargs)
            Path(dst).write_bytes(b"STILL-WRONG")  # same length as b"beta-gamma"

        with mock.patch.object(quarantine.shutil, "copy2", sabotaged_copy2):
            with self.assertRaises(SystemExit):
                quarantine.resume(source, dest, reason="sabotaged repair")

        self.assertTrue(source.exists(), "no removal on unrepaired mismatch")
        self.assertTrue(dest.is_dir())
        self.assert_no_manifest()

    def test_resume_row_keys_match_stage_row_keys(self) -> None:
        source_file = self.quarantine_root / "20260823" / "plain.txt"
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_bytes(b"stage me")
        staged_row = quarantine.stage(source_file, reason="stage schema")
        self.assertEqual(
            {"id", "original", "staged", "stagedAtUtc", "bytes", "sha256", "reason"},
            set(staged_row),
        )
        source, dest, _ = self.make_source_and_partial()
        resumed_row = quarantine.resume(source, dest, reason="resume schema")
        self.assertEqual(set(staged_row), set(resumed_row))

    # -- pre-flight refusals ----------------------------------------------

    def test_resume_refuses_when_destination_partial_missing(self) -> None:
        source, dest, _ = self.make_source_and_partial()
        shutil.rmtree(dest)
        with self.assertRaises(SystemExit):
            quarantine.resume(source, dest, reason="no third orphan")
        self.assertTrue(source.exists())  # never restarted from scratch
        self.assert_no_manifest()

    def test_resume_refuses_paths_outside_the_quarantine_root(self) -> None:
        outside_source = self.quarantine_root.parent / "outside-src"
        outside_source.mkdir()
        dest = self.quarantine_root / "20260824" / "some-partial"
        dest.mkdir(parents=True)
        with self.assertRaises(SystemExit):
            quarantine.resume(outside_source, dest, reason="containment")
        self.assert_no_manifest()

    def test_resume_refuses_destination_inside_source(self) -> None:
        source, _, _ = self.make_source_and_partial()
        nested_dest = source / "partial-inside"
        with self.assertRaises(SystemExit):
            quarantine.resume(source, nested_dest, reason="nesting")
        self.assert_no_manifest()

    def test_resume_refuses_an_already_manifested_destination(self) -> None:
        source, dest, _ = self.make_source_and_partial()
        quarantine.MANIFEST.write_text(
            json.dumps({
                "id": dest.name,
                "original": str(source),
                "staged": str(dest),
                "stagedAtUtc": "earlier",
                "bytes": 1,
                "sha256": "x",
                "reason": "already manifested",
            }) + "\n",
            encoding="utf-8",
        )
        with self.assertRaises(SystemExit):
            quarantine.resume(source, dest, reason="double manifest")
        self.assertTrue(source.exists())

    def test_resume_refuses_missing_source_without_touching_anything(self) -> None:
        source, dest, _ = self.make_source_and_partial()
        shutil.rmtree(source)
        with self.assertRaises(SystemExit):
            quarantine.resume(source, dest, reason="gone")
        self.assertTrue(dest.is_dir())
        self.assert_no_manifest()

    # -- identity gate fails closed ----------------------------------------

    def test_resume_refuses_extra_file_in_dest_not_present_in_source(self) -> None:
        # Content that exists only in the partial (the source shrank after
        # the kill) can never be reconciled by copying: the identity gate
        # must fail closed BEFORE manifest or removal.
        source, dest, _ = self.make_source_and_partial(complete_dest=True)
        (dest / "orphan.bin").write_bytes(b"only in the partial")

        with self.assertRaises(SystemExit):
            quarantine.resume(source, dest, reason="extra dest content")

        self.assertTrue(source.exists(), "source preserved on gate failure")
        self.assertTrue(dest.is_dir())
        self.assert_no_manifest()

    def test_resume_never_appends_two_rows_for_one_id(self) -> None:
        source, dest, _ = self.make_source_and_partial()
        row = quarantine.resume(source, dest, reason="once")
        self.assertEqual([row], self.manifest_rows())
        # Second attempt: source is gone now, so it must refuse entirely.
        with self.assertRaises(SystemExit):
            quarantine.resume(source, dest, reason="twice")
        self.assertEqual([row], self.manifest_rows())

    # -- removal handler: DOS read-only ONLY -------------------------------

    @unittest.skipUnless(os.name == "nt", "DOS attribute semantics")
    def test_resume_clears_dos_readonly_bits_during_removal(self) -> None:
        source, dest, _ = self.make_source_and_partial()
        stubborn = source / "nested" / "b.bin"
        os.chmod(stubborn, stat.S_IREAD)  # clears write bits -> DOS READONLY

        row = quarantine.resume(source, dest, reason="readonly retry")

        self.assertFalse(source.exists())
        self.assertEqual([row], self.manifest_rows())

    def test_readonly_only_handler_leaves_other_errors_alone(self) -> None:
        # Directly probe the handler contract: a sharing/ACL-style error must
        # propagate untouched, whether the failing function is unlink on a
        # non-readonly file or anything other than unlink.
        captured = {}

        def fake_rmtree(root, onexc=None, onerror=None):
            captured["handler"] = onexc if onexc is not None else onerror

        target = str(Path("Z:") / "nonexistent")
        with mock.patch.object(quarantine.shutil, "rmtree", fake_rmtree):
            quarantine._remove_tree_readonly_only(Path(target))

        handler = captured["handler"]
        self.assertIsNotNone(handler)
        sharing_violation = OSError(32, "sharing violation")
        # unlink on a file WITHOUT the readonly bit: propagate, never clear.
        with self.assertRaises(OSError):
            handler(os.unlink, target, sharing_violation)
        # Any function that is not os.unlink (e.g. rmdir): always propagate.
        with self.assertRaises(OSError):
            handler(quarantine.shutil.rmtree, target, sharing_violation)

    # -- manifest atomicity -------------------------------------------------

    def test_manifest_append_readback_failure_blocks_everything(self) -> None:
        source, dest, _ = self.make_source_and_partial()
        # Corrupt exactly what was appended BETWEEN the append's write and
        # its readback (hooked at fsync, which _append_manifest_row calls
        # after writing and before reading back), simulating a concurrent
        # writer or a torn tail. The readback guard must catch it.
        original_fsync = os.fsync

        def poisoned_fsync(fd):
            # _append_manifest_row calls os.fsync(stream.fileno()) after its
            # flush, so we see the int fd here; the write is already flushed.
            lines = quarantine.MANIFEST.read_text(encoding="utf-8").splitlines()
            bad = [
                json.dumps({**json.loads(line), "bytes": 0}) if json.loads(line)["id"].startswith("4d82") else line
                for line in lines
            ]
            quarantine.MANIFEST.write_text("\n".join(bad) + "\n", encoding="utf-8")
            return original_fsync(fd)

        with mock.patch.object(quarantine.os, "fsync", poisoned_fsync):
            with self.assertRaises(RuntimeError):
                quarantine.resume(source, dest, reason="poisoned manifest")

        self.assertTrue(source.exists(), "no removal after failed readback")
        self.assertTrue(dest.is_dir())

    # -- equivalence with stage()'s own hashing ------------------------------

    def test_identity_matches_tree_sha256_and_tree_bytes_on_real_tree(self) -> None:
        source, dest, expected_sha = self.make_source_and_partial()
        complete = self.quarantine_root / "20260823" / "complete"
        shutil.copytree(source, complete)
        (complete / "nested" / "b.bin").write_bytes(b"beta-gamma")
        count, total, sha = quarantine._identity(complete)
        self.assertEqual((2, 15), (count, total))
        self.assertEqual(quarantine.tree_sha256(complete), sha)
        self.assertEqual(quarantine.tree_bytes(complete), total)
        self.assertEqual(expected_sha, sha)

    def test_identity_streams_large_files_without_loading_whole_file(self) -> None:
        big = self.quarantine_root / "20260823" / "big"
        big.mkdir(parents=True)
        payload = bytes(range(256)) * 4096  # 1 MiB of varying content
        (big / "blob.bin").write_bytes(payload * 3)
        count, total, sha = quarantine._identity(big)
        self.assertEqual((1, len(payload) * 3, hashlib.sha256(
            ("blob.bin\0".encode("utf-8")
             + hashlib.sha256(payload * 3).hexdigest().encode("utf-8")
             + b"\0")) .hexdigest()), (count, total, sha))


class ReparseAndDuplicateIdRefusalTests(unittest.TestCase):
    """Falsification gates for the reviewer RED on 17a71be0 (t_c7571db2).

    Three binding defects closed here: (1) a destination-side reparse made
    its external target writable through the resume copy path; (2) a source
    reparse was silently skipped during the copy and then CLEARED by the
    removal step; (3) a pre-existing manifest id under a different staged
    path could gain a second equal-id row before readback failure. Each test
    constructs the defect and asserts refusal BEFORE any mutation.

    Real directory junctions and (when the platform allows unprivileged
    creation) directory symlinks exercise the true reparse code paths;
    mock-flagged entries cover shapes the host cannot construct.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.root = root
        self.quarantine_root = root / "quarantine"
        self.quarantine_root.mkdir()
        patcher = mock.patch.multiple(
            quarantine,
            QUARANTINE_ROOT=self.quarantine_root,
            MANIFEST=self.quarantine_root / "manifest.jsonl",
            PURGE_LOG=self.quarantine_root / "purge.log",
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.symlink_capable = self._probe_symlink_capability()

    # -- reparse construction helpers ---------------------------------------

    def _probe_symlink_capability(self) -> bool:
        """One cheap creation probe; unprivileged Windows usually refuses."""

        probe = self.root / "symlink-capability-probe"
        probe.mkdir()
        try:
            os.symlink(probe, probe / "link", target_is_directory=True)
        except OSError:
            return False
        finally:
            self.remove_dir_link(probe / "link")
        return True

    def constructible_kinds(self) -> list[str]:
        """Junction is always available; symlink only when creation works."""

        kinds = ["junction"]
        if self.symlink_capable:
            kinds.insert(0, "directory-symlink")
        return kinds

    def make_dir_link(self, link: Path, target: Path, kind: str) -> None:
        if kind == "directory-symlink":
            os.symlink(target, link, target_is_directory=True)
        else:
            assert kind == "junction"
            completed = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                check=True,
                capture_output=True,
                text=True,
            )
        self.assertTrue(os.path.lexists(link))

    @staticmethod
    def remove_dir_link(link: Path) -> None:
        if os.path.lexists(link):
            try:
                os.unlink(link)
            except OSError:
                os.rmdir(link)

    def make_source_and_partial(self):
        source = self.quarantine_root / "20260823" / "c45-src"
        dest = self.quarantine_root / "20260824" / "4d82-c45-src"
        for tree in (source, dest):
            if tree.exists():
                shutil.rmtree(tree)
        (source / "nested").mkdir(parents=True)
        (source / "a.bin").write_bytes(b"alpha")
        (source / "nested" / "b.bin").write_bytes(b"beta-gamma")
        shutil.copytree(source, dest)
        (dest / "nested" / "b.bin").unlink()  # simulate the timeout kill
        return source, dest

    def manifest_bytes(self) -> bytes:
        if not quarantine.MANIFEST.exists():
            return b""
        return quarantine.MANIFEST.read_bytes()

    def manifest_rows(self) -> list[dict]:
        if not quarantine.MANIFEST.exists():
            return []
        return [
            json.loads(line)
            for line in quarantine.MANIFEST.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    # -- (a) destination-side reparse must never be written through ----------

    @unittest.skipUnless(os.name == "nt", "reparse-point semantics")
    def test_destination_nested_reparse_refuses_before_any_mutation(self) -> None:
        if not self.symlink_capable:
            self.skipTest(
                "directory symlinks unavailable unprivileged; junction variant "
                "still runs in its own subTest below")

        for kind in self.constructible_kinds():
            with self.subTest(kind=kind):
                source, dest = self.make_source_and_partial()
                target = self.root / f"external-pristine-target-{kind}"
                target.mkdir()
                missing = source / "nested" / "b.bin"  # copy2 would create it
                link = dest / "nested"
                # The partial's plain nested directory gives way to the
                # hostile reparse before resume runs (the defect scenario).
                shutil.rmtree(dest / "nested")
                self.make_dir_link(link, target, kind)
                try:
                    with self.assertRaises(SystemExit):
                        quarantine.resume(source, dest, reason=f"dest {kind} probe")

                    # The external target received NOTHING.
                    self.assertEqual([], list(target.rglob("*")),
                                     "external junction/symlink target mutated")
                    # The reparse itself is still exactly where it was.
                    self.assertTrue(os.path.lexists(link))
                    # No manifest row, source preserved untouched.
                    self.assertListEqual([], self.manifest_rows())
                    self.assertTrue(source.exists())
                    self.assertTrue(missing.exists(), "source untouched by refusal")
                finally:
                    self.remove_dir_link(link)

    def test_destination_reparse_census_refuses_before_copy_pass(self) -> None:
        # Gate proof at the census boundary: the pre-copy census must find a
        # nested destination reparse before ANY copying runs (mock-flagged
        # shape, so this holds even off-Windows).
        source, dest = self.make_source_and_partial()
        target = self.root / "census-target"
        target.mkdir()
        link = dest / "nested"

        def fake_is_reparse(path) -> bool:
            return Path(path) == link

        with mock.patch.object(quarantine, "_is_reparse_point", fake_is_reparse):
            with self.assertRaises(SystemExit) as caught:
                quarantine.resume(source, dest, reason="census gate")
        self.assertIn("destination tree contains reparse point", str(caught.exception))
        self.assertIn("nested", str(caught.exception))
        self.assertFalse((dest / "nested" / "b.bin").exists(),
                         "missing payload was copied despite the census refusal")

    # -- (b) source reparse aborts untouched ---------------------------------

    @unittest.skipUnless(os.name == "nt", "reparse-point semantics")
    def test_source_reparse_refuses_with_no_row_no_removal(self) -> None:
        if not self.symlink_capable:
            self.skipTest(
                "directory symlinks unavailable unprivileged; junction variant "
                "still runs in its own subTest below")

        for kind in self.constructible_kinds():
            with self.subTest(kind=kind):
                source, dest = self.make_source_and_partial()
                target = self.root / f"source-reparse-target-{kind}"
                target.mkdir()
                link = source / "evidence-junction"
                self.make_dir_link(link, target, kind)
                try:
                    with self.assertRaises(SystemExit):
                        quarantine.resume(source, dest, reason=f"src {kind} probe")

                    self.assertTrue(source.exists(), "source tree removed despite reparse")
                    self.assertTrue(os.path.lexists(link),
                                    "the reparse itself was cleared")
                    self.assertTrue(target.is_dir())
                    self.assertEqual([], self.manifest_rows(),
                                     "manifest row appended anyway")
                finally:
                    self.remove_dir_link(link)

    def test_source_file_reparse_refuses_before_append(self) -> None:
        # A reparse FLAG on a real source file must refuse outright --
        # silent skipping would let the later removal clear it.
        source, dest = self.make_source_and_partial()
        (source / "linked.bin").write_bytes(b"linked payload")
        link = source / "linked.bin"

        def fake_is_reparse(path) -> bool:
            return Path(path) == link

        with mock.patch.object(quarantine, "_is_reparse_point", fake_is_reparse):
            with self.assertRaises(SystemExit) as caught:
                quarantine.resume(source, dest, reason="file reparse probe")
        self.assertIn("source tree contains reparse point", str(caught.exception))
        self.assertTrue(source.exists())
        self.assertTrue((source / "linked.bin").exists(),
                        "flagged entry vanished despite the refusal")
        self.assertEqual([], self.manifest_rows())

    # -- (c) duplicate manifest id refuses pre-append ------------------------

    def test_preexisting_duplicate_id_refused_before_append_byte_identical(self) -> None:
        source, dest = self.make_source_and_partial()
        existing = {
            "id": dest.name,
            "original": r"D:\lab-quarantine\old-source",
            "staged": r"D:\lab-quarantine\old-different-destination",
            "stagedAtUtc": "earlier",
            "bytes": 1,
            "sha256": "old",
            "reason": "pre-existing id",
        }
        quarantine.MANIFEST.write_text(json.dumps(existing) + "\n", encoding="utf-8")
        before_bytes = self.manifest_bytes()

        with self.assertRaises(SystemExit):
            quarantine.resume(source, dest, reason="duplicate id probe")

        self.assertEqual(before_bytes, self.manifest_bytes(),
                         "manifest changed despite duplicate-id refusal")
        rows = self.manifest_rows()
        self.assertEqual([existing], rows)
        self.assertEqual(1, sum(1 for r in rows if r["id"] == dest.name))

        # The append routine itself must hold the same line even when called
        # directly: no caller can slip a second equal-id row past it.
        with self.assertRaises(RuntimeError):
            quarantine._append_manifest_row({
                **existing,
                "staged": str(dest),
                "reason": "second row attempt",
            })
        self.assertEqual(before_bytes, self.manifest_bytes())

    def test_duplicate_id_preflight_runs_before_the_copy_pass(self) -> None:
        # Order matters: the id authority must refuse before any copying.
        source, dest = self.make_source_and_partial()
        existing = {
            "id": dest.name,
            "original": "elsewhere",
            "staged": r"D:\lab-quarantine\other",
            "stagedAtUtc": "earlier",
            "bytes": 1,
            "sha256": "x",
            "reason": "pre-existing id",
        }
        quarantine.MANIFEST.write_text(json.dumps(existing) + "\n", encoding="utf-8")

        def sabotaged_copy2(src, dst, **kwargs):  # noqa: ANN001,ANN003
            raise AssertionError("copy2 ran despite duplicate-id preflight")

        with mock.patch.object(quarantine.shutil, "copy2", sabotaged_copy2):
            with self.assertRaises(SystemExit):
                quarantine.resume(source, dest, reason="order probe")

        self.assertFalse((dest / "nested" / "b.bin").exists(),
                         "missing file was copied despite the duplicate-id refusal")

    # -- boundary re-checks ---------------------------------------------------

    def test_boundary_check_refuses_a_late_source_reparse_before_append(self) -> None:
        # A reparse appearing after the copy converged must be caught by the
        # safety boundary BEFORE the manifest row is written -- whether by
        # the boundary census (SystemExit) or the identity guard
        # (RuntimeError); either way: no row, both sides preserved.
        source, dest = self.make_source_and_partial()
        state = {"copy_completed": False}

        real_resume_copy_tree = quarantine._resume_copy_tree

        def spy_then_inject(source_arg, dest_arg):
            result = real_resume_copy_tree(source_arg, dest_arg)
            state["copy_completed"] = True
            target = self.root / "late-target"
            target.mkdir(exist_ok=True)
            self.make_dir_link(source / "late-junction", target, "junction")
            self.addCleanup(self.remove_dir_link, source / "late-junction")
            return result

        with mock.patch.object(quarantine, "_resume_copy_tree", spy_then_inject):
            with self.assertRaises((SystemExit, RuntimeError)):
                quarantine.resume(source, dest, reason="late injection probe")

        self.assertTrue(state["copy_completed"])
        self.assertEqual([], self.manifest_rows(), "row appended past the boundary")
        self.assertTrue(source.exists())
        self.assertTrue(os.path.lexists(source / "late-junction"))

    def test_final_census_refuses_immediately_before_removal(self) -> None:
        # A reparse injected after the append's dual rehash must stop the
        # removal itself: the row and BOTH copies stay, the reparse survives.
        source, dest = self.make_source_and_partial()
        real_identity = quarantine._identity
        state = {"identity_calls": 0}

        def counting_identity(root):
            result = real_identity(root)
            state["identity_calls"] += 1
            if state["identity_calls"] == 4:
                # Both gate identities (2) and the post-append dual rehash
                # (2 more) are done; only the final pre-removal census and
                # the removal remain ahead.
                target = self.root / "very-late-target"
                target.mkdir(exist_ok=True)
                self.make_dir_link(source / "last-second-junction", target, "junction")
                self.addCleanup(self.remove_dir_link, source / "last-second-junction")
            return result

        with mock.patch.object(quarantine, "_identity", counting_identity):
            with self.assertRaises((SystemExit, RuntimeError)):
                quarantine.resume(source, dest, reason="pre-removal injection probe")

        self.assertGreaterEqual(state["identity_calls"], 4,
                                "removal attempted before the gated identities")
        self.assertEqual(1, len(self.manifest_rows()),
                         "row should already be appended when removal is refused")
        self.assertTrue(source.exists(), "removal must not proceed over a reparse")
        self.assertTrue(os.path.lexists(source / "last-second-junction"),
                        "injected reparse was consumed by the removal")
        self.assertTrue(dest.is_dir())

    # -- roots ----------------------------------------------------------------

    @unittest.skipUnless(os.name == "nt", "reparse-point semantics")
    def test_source_root_itself_being_a_reparse_refuses(self) -> None:
        source, dest = self.make_source_and_partial()
        target = self.root / "root-replace-target"
        target.mkdir()
        moved_aside = self.root / "real-source-moved-aside"
        source.rename(moved_aside)
        self.make_dir_link(source, target, "junction")
        try:
            with self.assertRaises(SystemExit):
                quarantine.resume(source, dest, reason="root reparse probe")
            self.assertEqual([], self.manifest_rows())
            self.assertTrue(dest.is_dir())
        finally:
            self.remove_dir_link(source)
            moved_aside.rename(source)

    @unittest.skipUnless(os.name == "nt", "reparse-point semantics")
    def test_destination_root_itself_being_a_reparse_refuses(self) -> None:
        source, dest = self.make_source_and_partial()
        target = self.root / "dest-root-replace-target"
        target.mkdir()
        moved_aside = self.root / "real-dest-moved-aside"
        dest.rename(moved_aside)
        self.make_dir_link(dest, target, "junction")
        try:
            with self.assertRaises(SystemExit):
                quarantine.resume(source, dest, reason="dest root reparse probe")
            self.assertEqual([], self.manifest_rows())
            self.assertTrue(source.exists())
            self.assertEqual([], list(target.rglob("*")))
        finally:
            self.remove_dir_link(dest)
            moved_aside.rename(dest)

    # -- happy paths unchanged -------------------------------------------------

    def test_ordinary_happy_path_still_completes_exactly_once(self) -> None:
        source, dest = self.make_source_and_partial()
        expected_sha = quarantine.tree_sha256(source)

        row = quarantine.resume(source, dest, reason="ordinary happy path")

        self.assertFalse(source.exists())
        self.assertEqual(expected_sha, quarantine.tree_sha256(dest))
        self.assertEqual(expected_sha, row["sha256"])
        self.assertEqual([row], self.manifest_rows())

    @unittest.skipUnless(os.name == "nt", "DOS attribute semantics")
    def test_dos_readonly_happy_path_still_completes(self) -> None:
        source, dest = self.make_source_and_partial()
        stubborn = source / "nested" / "b.bin"
        os.chmod(stubborn, stat.S_IREAD)

        row = quarantine.resume(source, dest, reason="readonly retry")

        self.assertFalse(source.exists())
        self.assertEqual([row], self.manifest_rows())


class InjectingManifest:
    """Inject one competing equal-id row after pre-check but before the
    append handle opens — the exact write-boundary race from the reviewer
    harness (review_followup_probes.py)."""

    def __init__(self, path: Path, competing: dict):
        self.path = path
        self.competing = competing
        self.injected = False

    def exists(self) -> bool:
        return self.path.exists()

    def read_text(self, *args, **kwargs):
        return self.path.read_text(*args, **kwargs)

    def read_bytes(self):
        return self.path.read_bytes()

    def open(self, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        if "a" in mode and not self.injected:
            self.path.write_text(json.dumps(self.competing) + "\n", encoding="utf-8")
            self.injected = True
        return self.path.open(*args, **kwargs)


class FollowupBoundaryClosureTests(unittest.TestCase):
    """Falsification gates for the independent RED on exact 8ab9d9fb.

    Four binding defects (review t_2e8cb616, review_followup_probes.py),
    each reproduced here as a failing test BEFORE the fix:

      1. resume() resolved its inputs before any reparse check, so a
         directory symlink/junction AT a lexical root was followed and its
         target enumerated, recorded, and removed;
      2. a destination ancestor swapped to a reparse after the last
         pathname guard received copied payload bytes;
      3. an equal-id row injected between _append_manifest_row's pre-check
         and its append open became a second matching row on disk;
      4. traversal could follow: _reparse_census classified entries with
         following is_dir(), and _identity materialized rglob('*') before
         its per-entry guards.

    Real directory symlinks AND junctions exercise the true Windows reparse
    code paths. Their targets sit INSIDE the patched quarantine root on
    purpose: a pass then proves genuine refusal, not containment luck.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.root = root
        self.quarantine_root = root / "quarantine"
        self.quarantine_root.mkdir()
        patcher = mock.patch.multiple(
            quarantine,
            QUARANTINE_ROOT=self.quarantine_root,
            MANIFEST=self.quarantine_root / "manifest.jsonl",
            PURGE_LOG=self.quarantine_root / "purge.log",
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.symlink_capable = self._probe_symlink_capability()

    # -- fixture helpers ---------------------------------------------------

    def _probe_symlink_capability(self) -> bool:
        probe = self.root / "symlink-capability-probe"
        probe.mkdir()
        try:
            os.symlink(probe, probe / "link", target_is_directory=True)
        except OSError:
            return False
        finally:
            self.remove_dir_link(probe / "link")
        return True

    def constructible_kinds(self) -> list[str]:
        kinds = ["junction"]
        if self.symlink_capable:
            kinds.insert(0, "directory-symlink")
        return kinds

    def make_dir_link(self, link: Path, target: Path, kind: str) -> None:
        if kind == "directory-symlink":
            os.symlink(target, link, target_is_directory=True)
        else:
            assert kind == "junction"
            subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                check=True,
                capture_output=True,
                text=True,
            )
        self.assertTrue(os.path.lexists(link))

    @staticmethod
    def remove_dir_link(link: Path) -> None:
        if os.path.lexists(link):
            try:
                os.unlink(link)
            except OSError:
                os.rmdir(link)

    def make_source_and_partial(self):
        source = self.quarantine_root / "20260823" / "c45-src"
        dest = self.quarantine_root / "20260824" / "4d82-c45-src"
        for tree in (source, dest):
            if tree.exists():
                shutil.rmtree(tree)
        (source / "nested").mkdir(parents=True)
        (source / "a.bin").write_bytes(b"alpha")
        (source / "nested" / "b.bin").write_bytes(b"beta-gamma")
        shutil.copytree(source, dest)
        (dest / "nested" / "b.bin").unlink()  # the timeout kill
        return source, dest

    def manifest_rows(self) -> list[dict]:
        if not quarantine.MANIFEST.exists():
            return []
        return [
            json.loads(line)
            for line in quarantine.MANIFEST.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    # -- (1) lexical roots: reparse at either root refuses pre-resolve -----

    @unittest.skipUnless(os.name == "nt", "reparse-point semantics")
    def test_source_root_link_to_internal_target_refuses_all_untouched(self) -> None:
        for kind in self.constructible_kinds():
            with self.subTest(kind=kind):
                source, dest = self.make_source_and_partial()
                del source
                real_source = self.quarantine_root / "20260823" / f"internal-real-{kind}"
                real_source.mkdir()
                (real_source / "evidence.bin").write_bytes(b"internal-evidence")
                link = self.quarantine_root / "20260823" / f"internal-source-link-{kind}"
                self.make_dir_link(link, real_source, kind)
                try:
                    with self.assertRaises(SystemExit):
                        quarantine.resume(link, dest, reason=f"src-root {kind}")

                    self.assertTrue(os.path.lexists(link), "root link was consumed")
                    self.assertTrue(real_source.is_dir(), "internal target removed")
                    self.assertTrue((real_source / "evidence.bin").exists(),
                                    "internal target payload lost")
                    self.assertTrue(dest.is_dir())
                    self.assertFalse((dest / "evidence.bin").exists(),
                                     "target content was copied through the link")
                    self.assertEqual([], self.manifest_rows())
                finally:
                    self.remove_dir_link(link)

    @unittest.skipUnless(os.name == "nt", "reparse-point semantics")
    def test_destination_root_link_to_internal_target_refuses_all_untouched(self) -> None:
        for kind in self.constructible_kinds():
            with self.subTest(kind=kind):
                source, _ = self.make_source_and_partial()
                real_dest = self.quarantine_root / "20260824" / f"internal-real-partial-{kind}"
                real_dest.mkdir(parents=True, exist_ok=True)
                (real_dest / "evidence.bin").write_bytes(b"internal-evidence")
                link = self.quarantine_root / "20260824" / f"internal-dest-link-{kind}"
                self.make_dir_link(link, real_dest, kind)
                try:
                    with self.assertRaises(SystemExit):
                        quarantine.resume(source, link, reason=f"dst-root {kind}")

                    self.assertTrue(source.exists(), "source removed despite refusal")
                    self.assertTrue(os.path.lexists(link), "root link was consumed")
                    self.assertTrue(real_dest.is_dir(), "internal target removed")
                    self.assertTrue((real_dest / "evidence.bin").exists())
                    self.assertFalse((real_dest / "a.bin").exists(),
                                     "source content was copied through the link")
                    self.assertEqual([], self.manifest_rows())
                finally:
                    self.remove_dir_link(link)

    # -- (2) destination boundary: fresh no-follow truth at the operation --

    @unittest.skipUnless(os.name == "nt", "reparse-point semantics")
    def test_destination_ancestor_reparse_refused_on_fresh_boundary_truth(self) -> None:
        # Stronger than the deterministic swap probe: the junction exists
        # BEFORE resume runs and every _is_reparse_point verdict for it is
        # blinded, modelling earlier checks that cannot be trusted at all.
        # Only a fresh lstat-truth boundary check can refuse this.
        source, dest = self.make_source_and_partial()
        target = self.root / "external-blind-target"
        target.mkdir()
        link = dest / "nested"
        shutil.rmtree(link)
        self.make_dir_link(link, target, "junction")
        try:
            real_is_reparse = quarantine._is_reparse_point

            def blinded(path) -> bool:
                return False if Path(path) == link else real_is_reparse(path)

            with mock.patch.object(quarantine, "_is_reparse_point", blinded):
                with self.assertRaises(SystemExit):
                    quarantine.resume(source, dest, reason="blind guard probe")

            self.assertEqual([], list(target.rglob("*")),
                             "external target received copied bytes")
            self.assertTrue(os.path.lexists(link), "the reparse itself was cleared")
            self.assertFalse(os.path.lexists(dest / "nested" / "b.bin"),
                             "missing payload was written through the link")
            self.assertTrue(source.exists())
            self.assertEqual([], self.manifest_rows())
        finally:
            self.remove_dir_link(link)

    # -- (3) duplicate id at the write boundary ------------------------------

    def test_equal_id_injected_before_append_open_never_becomes_a_row(self) -> None:
        manifest_path = self.quarantine_root / "manifest.jsonl"
        proposed = {
            "id": "same-id",
            "original": "new-source",
            "staged": "new-dest",
            "stagedAtUtc": "now",
            "bytes": 2,
            "sha256": "new",
            "reason": "new",
        }
        competing = {
            "id": "same-id",
            "original": "other-source",
            "staged": "other-dest",
            "stagedAtUtc": "earlier",
            "bytes": 1,
            "sha256": "old",
            "reason": "competing writer",
        }
        proxy = InjectingManifest(manifest_path, competing)
        with mock.patch.object(quarantine, "MANIFEST", proxy):
            with self.assertRaises(RuntimeError):
                quarantine._append_manifest_row(proposed)

        on_disk = [
            json.loads(line)
            for line in manifest_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual([competing], on_disk,
                         "manifest must sit byte-equivalent at the single competing row")

    # -- (4) literal no-follow traversal -------------------------------------

    def test_census_classification_is_literal_no_follow(self) -> None:
        # An entry that claims to be a directory ONLY when following must
        # never be descended: the census reports it as a reparse hit (it is
        # neither provably-plain dir nor provably-plain file) and refuses
        # descent -- proven by the scan-count sentinel staying silent.
        plain = self.quarantine_root / "20260823" / "plain-dir"
        plain.mkdir(parents=True)
        parent = plain.parent

        class FlippingEntry:
            # Coherent identity (as any real filesystem provides): the
            # entry is named "flip" beneath the scanned parent, yet its
            # only directory answer requires following -- provably-plain
            # neither way.
            name = "flip"
            path = str(parent / "flip")

            def is_dir(self, *, follow_symlinks=True):
                return follow_symlinks

            def is_file(self, *, follow_symlinks=True):
                return False

        calls = {"plain": 0}

        def gated_scandir(path):
            if Path(path) == parent:
                calls["plain"] += 1
                if calls["plain"] > 1:
                    raise RuntimeError("SENTINEL-DESCENT-BENEATH-UNCLASSIFIED")
                return [FlippingEntry()]
            raise RuntimeError("SENTINEL-UNEXPECTED-SCANDIR")

        with mock.patch.object(quarantine.os, "scandir", gated_scandir):
            self.assertEqual(
                ["flip"],
                quarantine._reparse_census(parent),
                "an entry that cannot be proven plain must be reported, never followed",
            )
        # Exactly one scan of the parent happened: the unclassifiable entry
        # was reported as a hit and never descended into.
        self.assertEqual(1, calls["plain"], "census descended despite refusal")

    def test_census_reports_the_root_itself_as_dot(self) -> None:
        probe_root = self.quarantine_root / "20260823" / "reparse-root"
        probe_root.mkdir(parents=True)
        real = quarantine._is_reparse_point

        def flagged(path) -> bool:
            return True if Path(path) == probe_root else real(path)

        with mock.patch.object(quarantine, "_is_reparse_point", flagged):
            self.assertEqual(["."], quarantine._reparse_census(probe_root))

    @unittest.skipUnless(os.name == "nt", "reparse-point semantics")
    def test_identity_refuses_root_nested_and_file_reparses(self) -> None:
        base = self.quarantine_root / "20260823"
        real_tree = base / "id-root-real"
        (real_tree / "deep").mkdir(parents=True)
        (real_tree / "deep" / "x.bin").write_bytes(b"x")
        root_link = base / "id-root-link"

        for kind in self.constructible_kinds():
            with self.subTest(scope="root", kind=kind):
                self.make_dir_link(root_link, real_tree, kind)
                try:
                    with self.assertRaises(RuntimeError):
                        quarantine._identity(root_link)
                finally:
                    self.remove_dir_link(root_link)

        tree = base / "id-nested"
        (tree / "keep").mkdir(parents=True)
        (tree / "keep" / "a.bin").write_bytes(b"a")
        inner_target = self.root / "id-inner-target"
        inner_target.mkdir(exist_ok=True)
        inner = tree / "inner-junction"

        for kind in self.constructible_kinds():
            with self.subTest(scope="nested", kind=kind):
                self.make_dir_link(inner, inner_target, kind)
                try:
                    with self.assertRaises(RuntimeError):
                        quarantine._identity(tree)
                finally:
                    self.remove_dir_link(inner)

        ftree = base / "id-file"
        ftree.mkdir(parents=True)
        payload = ftree / "linked.bin"
        payload.write_bytes(b"payload")
        real = quarantine._is_reparse_point

        def flagged(path) -> bool:
            return True if Path(path) == payload else real(path)

        with mock.patch.object(quarantine, "_is_reparse_point", flagged):
            with self.assertRaises(RuntimeError):
                quarantine._identity(ftree)

    # -- preserved behavior pins ----------------------------------------------

    def test_dotdot_destination_escape_still_refused_by_containment(self) -> None:
        source, _ = self.make_source_and_partial()
        escape = self.quarantine_root / ".." / "dotdot-escape"
        escape.mkdir()
        self.addCleanup(shutil.rmtree, escape, ignore_errors=True)

        with self.assertRaises(SystemExit) as caught:
            quarantine.resume(source, escape, reason="dotdot escape probe")

        self.assertIn("outside the quarantine root", str(caught.exception))
        self.assertEqual([], self.manifest_rows())
        self.assertTrue(source.exists())

    def test_identity_digest_order_matches_stage_semantics_on_case_mixed_tree(self) -> None:
        # The no-follow scanner must reproduce stage()'s exact digest, which
        # hashes files in pathlib-sorted order; case-mixed names would catch
        # any ordering drift.
        tree = self.quarantine_root / "20260823" / "case-tree"
        (tree / "Nested").mkdir(parents=True)
        (tree / "Alpha.bin").write_bytes(b"a")
        (tree / "Nested" / "zeta.bin").write_bytes(b"zz")
        (tree / "beta.TXT").write_bytes(b"bbb")

        count, total, sha = quarantine._identity(tree)

        self.assertEqual((3, 6), (count, total))
        self.assertEqual(quarantine.tree_sha256(tree), sha)
        self.assertEqual(quarantine.tree_bytes(tree), total)


class LateReparseDescentRefusalTests(unittest.TestCase):
    """Falsification gates for the independent RED on exact e1454e55.

    Two binding defects (review t_4fde5a56, review_no_follow_swap_probes.py):
    a queued child directory becomes a REAL directory reparse after its
    parent's classification but before it is popped for descent, and both
    no-follow scanners then traversed the target:

      1. _identity scanned, opened, and hashed external-secret.bin through
         the swapped-in reparse and returned a successful identity;
      2. _reparse_census called os.scandir() ON the replaced reparse
         pathname, enumerated its target, and reported nothing.

    Both gates demand fresh final-component no-follow truth at the moment
    of descent/open: refuse before any target scandir/open/hash. Real
    directory symlinks AND junctions exercise the true Windows reparse
    code paths; every host-supported kind runs (zero supported-form skips).
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    # -- fixture helpers ----------------------------------------------------

    def _symlink_capable(self) -> bool:
        probe = self.root / "capability-probe"
        probe.mkdir()
        try:
            os.symlink(probe, probe / "link", target_is_directory=True)
        except OSError:
            return False
        finally:
            self.remove_dir_link(probe / "link")
        return True

    def constructible_kinds(self) -> list[str]:
        kinds = []
        if self._symlink_capable():
            kinds.append("directory-symlink")
        if os.name == "nt":
            kinds.append("junction")
        return kinds

    @staticmethod
    def make_dir_link(link: Path, target: Path, kind: str) -> None:
        if kind == "directory-symlink":
            os.symlink(target, link, target_is_directory=True)
        else:
            assert kind == "junction"
            subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                check=True,
                capture_output=True,
                text=True,
            )
        assert os.path.lexists(link)

    @staticmethod
    def remove_dir_link(link: Path) -> None:
        if os.path.lexists(link):
            try:
                os.unlink(link)
            except OSError:
                os.rmdir(link)

    # -- (1) identity: descent-time reproof ---------------------------------

    def test_identity_refuses_child_swapped_to_reparse_before_descent(self) -> None:
        kinds = self.constructible_kinds()
        if not kinds:
            self.fail("no directory-reparse construction is supported on this host")
        for kind in kinds:
            with self.subTest(kind=kind):
                tree = self.root / f"id-tree-{kind}"
                child = tree / "child"
                external = self.root / f"id-external-{kind}"
                child.mkdir(parents=True)
                external.mkdir()
                secret = external / "external-secret.bin"
                secret.write_bytes(b"must-never-be-hashed-through-a-reparse")
                real_scan = quarantine._scan_plain_children
                state = {"swapped": False}

                def scan_then_swap(directory: Path):
                    result = real_scan(directory)
                    if Path(directory) == tree and not state["swapped"]:
                        os.rmdir(child)
                        self.make_dir_link(child, external, kind)
                        state["swapped"] = True
                    return result

                try:
                    with mock.patch.object(
                        quarantine, "_scan_plain_children", scan_then_swap
                    ):
                        with self.assertRaises(RuntimeError):
                            quarantine._identity(tree)
                finally:
                    self.remove_dir_link(child)

                self.assertTrue(state["swapped"], "swap fixture never fired")
                self.assertEqual(
                    b"must-never-be-hashed-through-a-reparse",
                    secret.read_bytes(),
                    "external target content was disturbed",
                )

    # -- (2) census: descent-time reproof -------------------------------------

    def test_census_never_scandirs_child_swapped_to_reparse(self) -> None:
        kinds = self.constructible_kinds()
        if not kinds:
            self.fail("no directory-reparse construction is supported on this host")
        for kind in kinds:
            with self.subTest(kind=kind):
                tree = self.root / f"census-tree-{kind}"
                child = tree / "child"
                external = self.root / f"census-external-{kind}"
                child.mkdir(parents=True)
                external.mkdir()
                (external / "external-secret.bin").write_bytes(b"external")
                real_classify = quarantine._classify_entry
                real_scandir = quarantine.os.scandir
                state = {"swapped": False, "scanned_child": False}

                def classify_then_swap(entry):
                    classification = real_classify(entry)
                    if (
                        Path(entry.path) == child
                        and classification == "dir"
                        and not state["swapped"]
                    ):
                        os.rmdir(child)
                        self.make_dir_link(child, external, kind)
                        state["swapped"] = True
                    return classification

                def recording_scandir(path):
                    if Path(path) == child and os.path.lexists(child):
                        state["scanned_child"] = True
                    return real_scandir(path)

                try:
                    with mock.patch.object(
                        quarantine, "_classify_entry", classify_then_swap
                    ), mock.patch.object(
                        quarantine.os, "scandir", recording_scandir
                    ):
                        found = quarantine._reparse_census(tree)
                        raised = None
                except RuntimeError as error:
                    raised = error
                    found = None
                finally:
                    self.remove_dir_link(child)

                self.assertTrue(state["swapped"], "swap fixture never fired")
                # Contract: the replaced entry is reported OR the scan
                # refuses -- either way its target is NEVER enumerated.
                self.assertTrue(
                    raised is not None or (found is not None and "child" in found),
                    f"census neither reported nor refused the replaced entry "
                    f"(raised={raised!r}, found={found!r})",
                )
                self.assertFalse(
                    state["scanned_child"],
                    "census called os.scandir on the replaced reparse pathname",
                )

    # -- (3) identity: yielded file slot reproved at the open boundary ------

    def test_identity_refuses_yielded_file_swapped_to_reparse_before_open(self) -> None:
        if not self._symlink_capable():
            self.fail("file-symlink construction is unsupported on this host")
        tree = self.root / "file-tree"
        tree.mkdir()
        slot = tree / "evidence.bin"
        slot.write_bytes(b"plain-payload")
        external = self.root / "file-external"
        external.mkdir()
        loot = external / "loot.bin"
        loot.write_bytes(b"external-loot")
        real_scan = quarantine._scan_plain_children
        state = {"swapped": False}

        def scan_then_swap(directory: Path):
            result = real_scan(directory)
            if Path(directory) == tree and not state["swapped"]:
                os.unlink(slot)
                os.symlink(loot, slot)  # file reparse replacing a plain file
                state["swapped"] = True
            return result

        identity = None
        try:
            with mock.patch.object(quarantine, "_scan_plain_children", scan_then_swap):
                with self.assertRaises(RuntimeError):
                    identity = quarantine._identity(tree)
        finally:
            self.remove_dir_link(slot)

        self.assertIsNone(identity, "identity succeeded through a swapped-in reparse")
        self.assertTrue(state["swapped"], "swap fixture never fired")
        self.assertEqual(
            b"external-loot", loot.read_bytes(), "external target was disturbed"
        )


class PostReproofOperationBoundTests(unittest.TestCase):
    """Falsification gates for the independent RED on exact 590adf34.

    Binding defects (review t_95b4b7a0, review_post_reproof_swap_probes.py,
    0/5 contract_pass): a path-only reproof followed by a separate pathname
    scan/open is still a TOCTOU. Swaps that land AFTER the final ordinary
    path proof but BEFORE the pathname operation were followed:

      1. a queued child directory swapped to a REAL directory symlink or
         junction immediately after ``_reprove_plain_directory`` returned
         was scandir'd through, and ``_identity`` opened and hashed
         ``external-secret.bin`` behind it;
      2. the same swap let ``_reparse_census`` call ``os.scandir`` ON the
         replaced reparse pathname (its target answered ``[]``);
      3. a plain file slot swapped to a real file symlink after the final
         ``_lstat_is_reparse_point`` verdict had its external target opened
         and hashed by ``Path.open`` before the post-open check noticed.

    The correction demanded by the card is OPERATION-BOUND no-follow: a
    verified non-reparse object pinned with replacement-denying sharing
    (Windows: ``CreateFileW`` + ``FILE_FLAG_OPEN_REPARSE_POINT``, no
    ``FILE_SHARE_WRITE``/``FILE_SHARE_DELETE``; POSIX: ``O_NOFOLLOW``
    descriptors) whose enumeration and reads bind to the pinned object --
    not another lstat one line closer to a path-based syscall. These tests
    fire the exact seams and assert NO target scan/open/hash occurred, not
    merely eventual refusal. Real directory symlinks AND junctions exercise
    the true Windows reparse code paths; every host-supported kind runs.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    # -- fixture helpers ----------------------------------------------------

    def _symlink_capable(self) -> bool:
        probe = self.root / "capability-probe"
        probe.mkdir()
        try:
            os.symlink(probe, probe / "link", target_is_directory=True)
        except OSError:
            return False
        finally:
            self.remove_dir_link(probe / "link")
        return True

    def constructible_kinds(self) -> list[str]:
        kinds = []
        if self._symlink_capable():
            kinds.append("directory-symlink")
        if os.name == "nt":
            kinds.append("junction")
        return kinds

    @staticmethod
    def make_dir_link(link: Path, target: Path, kind: str) -> None:
        if kind == "directory-symlink":
            os.symlink(target, link, target_is_directory=True)
        else:
            assert kind == "junction"
            subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                check=True,
                capture_output=True,
                text=True,
            )
        assert os.path.lexists(link)

    @staticmethod
    def remove_dir_link(link: Path) -> None:
        if os.path.lexists(link):
            try:
                os.unlink(link)
            except OSError:
                os.rmdir(link)

    # -- (1) identity: swap after reproof, before scandir -------------------

    def test_identity_child_swapped_after_reproof_never_scanned_or_read(self) -> None:
        kinds = self.constructible_kinds()
        if not kinds:
            self.fail("no directory-reparse construction is supported on this host")
        for kind in kinds:
            with self.subTest(kind=kind):
                tree = self.root / f"id-tree-{kind}"
                child = tree / "child"
                external = self.root / f"id-external-{kind}"
                child.mkdir(parents=True)
                external.mkdir()
                secret = external / "external-secret.bin"
                secret.write_bytes(b"must-never-be-opened-through-a-reparse")
                real_reprove = quarantine._reprove_plain_directory
                real_scandir = quarantine.os.scandir
                real_open = Path.open
                state = {"swapped": False, "scanned_reparse": False,
                         "opened_target": False}

                def prove_then_swap(path: Path) -> None:
                    real_reprove(path)
                    if Path(path) == child and not state["swapped"]:
                        os.rmdir(child)
                        self.make_dir_link(child, external, kind)
                        state["swapped"] = True

                def recording_scandir(path):
                    if Path(path) == child and state["swapped"]:
                        state["scanned_reparse"] = True
                    return real_scandir(path)

                def recording_open(self: Path, *args, **kwargs):
                    if (Path(self) == child / "external-secret.bin"
                            and state["swapped"]):
                        state["opened_target"] = True
                    return real_open(self, *args, **kwargs)

                identity = None
                try:
                    with mock.patch.object(
                        quarantine, "_reprove_plain_directory", prove_then_swap
                    ), mock.patch.object(
                        quarantine.os, "scandir", recording_scandir
                    ), mock.patch.object(Path, "open", recording_open):
                        with self.assertRaises(RuntimeError):
                            identity = quarantine._identity(tree)
                finally:
                    self.remove_dir_link(child)

                self.assertIsNone(identity, "identity succeeded past the swap")
                self.assertTrue(state["swapped"], "swap fixture never fired")
                self.assertFalse(
                    state["scanned_reparse"],
                    "os.scandir reached the replaced reparse pathname",
                )
                self.assertFalse(
                    state["opened_target"],
                    "a file behind the reparse was opened and hashed",
                )
                self.assertEqual(
                    b"must-never-be-opened-through-a-reparse",
                    secret.read_bytes(),
                    "external target content was disturbed",
                )

    # -- (2) census: swap after reproof, before scandir ----------------------

    def test_census_child_swapped_after_reproof_never_scandired(self) -> None:
        kinds = self.constructible_kinds()
        if not kinds:
            self.fail("no directory-reparse construction is supported on this host")
        for kind in kinds:
            with self.subTest(kind=kind):
                tree = self.root / f"census-tree-{kind}"
                child = tree / "child"
                external = self.root / f"census-external-{kind}"
                child.mkdir(parents=True)
                external.mkdir()
                (external / "external-secret.bin").write_bytes(b"external")
                real_reprove = quarantine._reprove_plain_directory
                real_scandir = quarantine.os.scandir
                state = {"swapped": False, "scanned_reparse": False}

                def prove_then_swap(path: Path) -> None:
                    real_reprove(path)
                    if Path(path) == child and not state["swapped"]:
                        os.rmdir(child)
                        self.make_dir_link(child, external, kind)
                        state["swapped"] = True

                def recording_scandir(path):
                    if Path(path) == child and state["swapped"]:
                        state["scanned_reparse"] = True
                    return real_scandir(path)

                found = None
                raised = None
                try:
                    with mock.patch.object(
                        quarantine, "_reprove_plain_directory", prove_then_swap
                    ), mock.patch.object(
                        quarantine.os, "scandir", recording_scandir
                    ):
                        found = quarantine._reparse_census(tree)
                except RuntimeError as error:
                    raised = error
                finally:
                    self.remove_dir_link(child)

                self.assertTrue(state["swapped"], "swap fixture never fired")
                # Contract (unchanged from the prior gate): the replaced
                # entry is refused OR reported -- either way its pathname
                # must NEVER reach os.scandir.
                self.assertTrue(
                    raised is not None or (found is not None and "child" in found),
                    f"census neither reported nor refused the replaced entry "
                    f"(raised={raised!r}, found={found!r})",
                )
                self.assertFalse(
                    state["scanned_reparse"],
                    "os.scandir was called on the replaced reparse pathname",
                )

    # -- (3) identity: file swap after the FINAL proof, before open ----------

    def test_identity_file_swapped_after_final_proof_never_opened(self) -> None:
        if not self._symlink_capable():
            self.fail("file-symlink construction is unsupported on this host")
        tree = self.root / "file-tree"
        tree.mkdir()
        slot = tree / "evidence.bin"
        slot.write_bytes(b"plain-payload")
        loot = self.root / "external-loot.bin"
        loot.write_bytes(b"external-loot")
        real_lstat_guard = quarantine._lstat_is_reparse_point
        real_open = Path.open
        state = {"swapped": False, "opened_target": False}

        def prove_then_swap(path: Path) -> bool:
            verdict = real_lstat_guard(path)
            if Path(path) == slot and not state["swapped"]:
                os.unlink(slot)
                os.symlink(loot, slot)
                state["swapped"] = True
            return verdict

        def recording_open(self: Path, *args, **kwargs):
            if Path(self) == slot and state["swapped"]:
                state["opened_target"] = True
            return real_open(self, *args, **kwargs)

        identity = None
        try:
            with mock.patch.object(
                quarantine, "_lstat_is_reparse_point", prove_then_swap
            ), mock.patch.object(Path, "open", recording_open):
                with self.assertRaises(RuntimeError):
                    identity = quarantine._identity(tree)
        finally:
            self.remove_dir_link(slot)

        self.assertIsNone(identity, "identity blessed bytes read through a target")
        self.assertTrue(state["swapped"], "swap fixture never fired")
        self.assertFalse(
            state["opened_target"],
            "Path.open reached the swapped-in symlink after the final proof",
        )
        self.assertEqual(
            b"external-loot", loot.read_bytes(), "external target was disturbed"
        )

    # -- (4) the pin primitive itself refuses real reparses (no mocks) -------

    @unittest.skipUnless(os.name == "nt", "Windows pin primitive")
    def test_pinned_directory_primitive_refuses_real_reparses(self) -> None:
        kinds = self.constructible_kinds()
        if not kinds:
            self.fail("no directory-reparse construction is supported on this host")
        for kind in kinds:
            with self.subTest(kind=kind):
                link = self.root / f"pin-junction-{kind}"
                target = self.root / f"pin-target-{kind}"
                target.mkdir()
                (target / "secret.txt").write_bytes(b"secret")
                before = sorted(p.name for p in target.rglob("*"))
                self.make_dir_link(link, target, kind)
                real_scandir = os.scandir
                state = {"scanned_link": False}

                def recording_scandir(path):
                    if Path(path) == link:
                        state["scanned_link"] = True
                    return real_scandir(path)

                entered_body = False
                try:
                    with mock.patch.object(os, "scandir", recording_scandir):
                        with self.assertRaises(RuntimeError):
                            with quarantine._pinned_plain_directory(link):
                                entered_body = True
                    self.assertFalse(
                        state["scanned_link"],
                        "os.scandir ran on the reparse pathname",
                    )
                    self.assertEqual(
                        before,
                        sorted(p.name for p in target.rglob("*")),
                        "target content changed through the pinned reparse",
                    )
                finally:
                    self.remove_dir_link(link)
                self.assertFalse(
                    entered_body, "pin body ran despite a reparse pathname"
                )

    @unittest.skipUnless(os.name == "nt", "Windows pin primitive")
    def test_pinned_file_primitive_refuses_real_file_symlink(self) -> None:
        if not self._symlink_capable():
            self.fail("file-symlink construction is unsupported on this host")
        loot = self.root / "pin-loot.bin"
        loot.write_bytes(b"LOOT-BYTES")
        slot = self.root / "pin-slot.bin"
        slot.write_bytes(b"plain")
        slot.unlink()
        os.symlink(loot, slot)
        try:
            with self.assertRaises(RuntimeError):
                with quarantine._pinned_plain_file(slot) as pinned:
                    raise AssertionError("pin entered a reparse pathname")
            self.assertEqual(b"LOOT-BYTES", loot.read_bytes(),
                             "target was read through the pinned reparse")
        finally:
            self.remove_dir_link(slot)


class IntermediateAncestorSwapPinChainTests(unittest.TestCase):
    """Falsification gates for the independent RED on exact fb7bf802.

    Binding defect (review t_8d02a607, review_ancestor_pin_chain_probes.py,
    0/6 contract_pass, twice byte-identical): the final-component pins close
    the parent directory before queued descendants are scanned/read --
    ``_iter_plain_files`` released each current pin before queued descent,
    ``_identity`` exhausted/sorted all pathnames before file opens, and
    ``_reparse_census`` closed the current pin before later descendant
    processing. A real already-scanned ancestor could therefore be renamed
    away and replaced by a directory symlink/junction immediately before a
    descendant pin; ``FILE_FLAG_OPEN_REPARSE_POINT`` protects only the FINAL
    component, so the plain descendant inside the external target was
    accepted, scanned, opened, and hashed (identity (1,52,ac77a0be...) /
    (1,42,5deb6832...), census []).

    These gates fire the swap at the EXACT descendant pin seams -- identity
    child-directory pin, census child pin, file pin -- and require the
    ancestor replacement to be BLOCKED (by live replacement-denying pins on
    every ancestor) or refused before any external target scandir/open/hash.
    Real directory symlinks AND junctions exercise the true Windows reparse
    code paths; every host-supported kind runs (zero supported-form skips).
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    # -- fixture helpers ----------------------------------------------------

    def _symlink_capable(self) -> bool:
        probe = self.root / "capability-probe"
        probe.mkdir()
        try:
            os.symlink(probe, probe / "link", target_is_directory=True)
        except OSError:
            return False
        finally:
            self.remove_dir_link(probe / "link")
        return True

    def constructible_kinds(self) -> list[str]:
        kinds = []
        if self._symlink_capable():
            kinds.append("directory-symlink")
        if os.name == "nt":
            kinds.append("junction")
        return kinds

    @staticmethod
    def make_dir_link(link: Path, target: Path, kind: str) -> None:
        if kind == "directory-symlink":
            os.symlink(target, link, target_is_directory=True)
        else:
            assert kind == "junction"
            subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                check=True,
                capture_output=True,
                text=True,
            )
        assert os.path.lexists(link)

    @staticmethod
    def remove_dir_link(link: Path) -> None:
        if os.path.lexists(link):
            try:
                os.unlink(link)
            except OSError:
                os.rmdir(link)

    @classmethod
    def attempt_ancestor_swap(
        cls, tree: Path, aside: Path, external: Path, kind: str, state: dict
    ) -> None:
        state["swap_attempted"] = True
        try:
            tree.rename(aside)
        except OSError:
            # Live replacement-denying pins on the ancestor chain deny the
            # rename outright: the verified name->object binding cannot
            # change hands while any descendant operation is queued.
            state["swap_blocked"] = True
            return
        cls.make_dir_link(tree, external, kind)
        state["swap_succeeded"] = True

    @classmethod
    def restore_tree(cls, tree: Path, aside: Path) -> None:
        if os.path.lexists(tree) and aside.exists():
            cls.remove_dir_link(tree)
        if aside.exists() and not tree.exists():
            aside.rename(tree)

    @staticmethod
    def base_state() -> dict:
        return {
            "swap_attempted": False,
            "swap_succeeded": False,
            "swap_blocked": False,
        }

    # -- (1) identity: swap immediately before the child-directory pin ------

    def test_identity_ancestor_swap_at_child_directory_pin_blocked(self) -> None:
        kinds = self.constructible_kinds()
        if not kinds:
            self.fail("no directory-reparse construction is supported on this host")
        for kind in kinds:
            with self.subTest(kind=kind):
                base = self.root / f"chain-id-dir-{kind}"
                tree, aside, external = (
                    base / "tree",
                    base / "tree-original",
                    base / "external",
                )
                (tree / "child").mkdir(parents=True)
                (external / "child").mkdir(parents=True)
                secret = external / "child" / "external-secret.bin"
                secret.write_bytes(
                    b"must-never-be-opened-through-an-intermediate-reparse"
                )
                state = {
                    **self.base_state(),
                    "scanned_external_child": False,
                    "opened_external_file": False,
                }
                real_factory = quarantine._pinned_plain_directory
                real_scandir = quarantine.os.scandir
                real_pin_open = quarantine._windows_pin_open

                def pin_with_attack(path: Path):
                    if (
                        Path(path) == tree / "child"
                        and not state["swap_attempted"]
                    ):
                        self.attempt_ancestor_swap(
                            tree, aside, external, kind, state
                        )
                    return real_factory(path)

                def recording_scandir(path):
                    if state["swap_succeeded"] and Path(path) == tree / "child":
                        state["scanned_external_child"] = True
                    return real_scandir(path)

                def recording_pin_open(path: Path, *, directory: bool):
                    if (
                        state["swap_succeeded"]
                        and Path(path) == tree / "child" / secret.name
                    ):
                        state["opened_external_file"] = True
                    return real_pin_open(path, directory=directory)

                raised = None
                identity = None
                try:
                    with mock.patch.object(
                        quarantine, "_pinned_plain_directory", pin_with_attack
                    ), mock.patch.object(
                        quarantine.os, "scandir", recording_scandir
                    ), mock.patch.object(
                        quarantine, "_windows_pin_open", recording_pin_open
                    ):
                        try:
                            identity = quarantine._identity(tree)
                        except BaseException as error:
                            raised = f"{type(error).__name__}: {error}"
                finally:
                    self.restore_tree(tree, aside)

                self.assertTrue(
                    state["swap_attempted"],
                    "descendant child-directory pin seam never reached",
                )
                self.assertTrue(
                    state["swap_blocked"] or raised is not None,
                    f"already-scanned ancestor was renamed away and replaced "
                    f"and traversal continued through the replacement "
                    f"(identity={identity!r}, raised={raised!r})",
                )
                self.assertFalse(
                    state["scanned_external_child"],
                    "external descendant directory was scandir'd through the "
                    "swapped-in intermediate reparse",
                )
                self.assertFalse(
                    state["opened_external_file"],
                    "external descendant file was opened through the "
                    "swapped-in intermediate reparse",
                )
                self.assertTrue(
                    secret.read_bytes().startswith(b"must-never"),
                    "external target content was disturbed",
                )

    # -- (2) census: swap immediately before the census child pin ------------

    def test_census_ancestor_swap_at_child_directory_pin_blocked(self) -> None:
        kinds = self.constructible_kinds()
        if not kinds:
            self.fail("no directory-reparse construction is supported on this host")
        for kind in kinds:
            with self.subTest(kind=kind):
                base = self.root / f"chain-census-{kind}"
                tree, aside, external = (
                    base / "tree",
                    base / "tree-original",
                    base / "external",
                )
                (tree / "child").mkdir(parents=True)
                (external / "child").mkdir(parents=True)
                (external / "child" / "external-secret.bin").write_bytes(
                    b"external"
                )
                state = {**self.base_state(), "scanned_external_child": False}
                real_factory = quarantine._pinned_plain_directory
                real_scandir = quarantine.os.scandir

                def pin_with_attack(path: Path):
                    if (
                        Path(path) == tree / "child"
                        and not state["swap_attempted"]
                    ):
                        self.attempt_ancestor_swap(
                            tree, aside, external, kind, state
                        )
                    return real_factory(path)

                def recording_scandir(path):
                    if state["swap_succeeded"] and Path(path) == tree / "child":
                        state["scanned_external_child"] = True
                    return real_scandir(path)

                raised = None
                found = None
                try:
                    with mock.patch.object(
                        quarantine, "_pinned_plain_directory", pin_with_attack
                    ), mock.patch.object(
                        quarantine.os, "scandir", recording_scandir
                    ):
                        try:
                            found = quarantine._reparse_census(tree)
                        except BaseException as error:
                            raised = f"{type(error).__name__}: {error}"
                finally:
                    self.restore_tree(tree, aside)

                self.assertTrue(
                    state["swap_attempted"],
                    "census child-directory pin seam never reached",
                )
                self.assertTrue(
                    state["swap_blocked"] or raised is not None or bool(found),
                    f"census neither blocked nor reported/refused the "
                    f"intermediate-ancestor replacement "
                    f"(found={found!r}, raised={raised!r})",
                )
                self.assertFalse(
                    state["scanned_external_child"],
                    "census scandir'd the external target through the "
                    "swapped-in intermediate reparse",
                )

    # -- (3) identity: swap immediately before the file pin ------------------

    def test_identity_ancestor_swap_at_file_pin_blocked(self) -> None:
        kinds = self.constructible_kinds()
        if not kinds:
            self.fail("no directory-reparse construction is supported on this host")
        for kind in kinds:
            with self.subTest(kind=kind):
                base = self.root / f"chain-id-file-{kind}"
                tree, aside, external = (
                    base / "tree",
                    base / "tree-original",
                    base / "external",
                )
                tree.mkdir(parents=True)
                external.mkdir(parents=True)
                (tree / "evidence.bin").write_bytes(b"original-plain")
                loot = external / "evidence.bin"
                loot.write_bytes(b"external-loot-through-intermediate-reparse")
                state = {**self.base_state(), "opened_external_file": False}
                real_factory = quarantine._pinned_plain_file
                real_pin_open = quarantine._windows_pin_open

                def pin_with_attack(path: Path):
                    if (
                        Path(path) == tree / "evidence.bin"
                        and not state["swap_attempted"]
                    ):
                        self.attempt_ancestor_swap(
                            tree, aside, external, kind, state
                        )
                    return real_factory(path)

                def recording_pin_open(path: Path, *, directory: bool):
                    if (
                        state["swap_succeeded"]
                        and Path(path) == tree / "evidence.bin"
                    ):
                        state["opened_external_file"] = True
                    return real_pin_open(path, directory=directory)

                raised = None
                identity = None
                try:
                    with mock.patch.object(
                        quarantine, "_pinned_plain_file", pin_with_attack
                    ), mock.patch.object(
                        quarantine, "_windows_pin_open", recording_pin_open
                    ):
                        try:
                            identity = quarantine._identity(tree)
                        except BaseException as error:
                            raised = f"{type(error).__name__}: {error}"
                finally:
                    self.restore_tree(tree, aside)

                self.assertTrue(
                    state["swap_attempted"],
                    "descendant file pin seam never reached",
                )
                self.assertTrue(
                    state["swap_blocked"]
                    or (raised is not None and identity is None),
                    f"file bytes were blessed through the swapped-in "
                    f"intermediate reparse (identity={identity!r})",
                )
                self.assertFalse(
                    state["opened_external_file"],
                    "external loot file was opened and hashed through the "
                    "swapped-in intermediate reparse",
                )
                self.assertEqual(
                    b"external-loot-through-intermediate-reparse",
                    loot.read_bytes(),
                    "external target content was disturbed",
                )


if __name__ == "__main__":
    unittest.main()
