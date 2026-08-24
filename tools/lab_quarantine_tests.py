#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
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

    def test_stage_directory_then_restore_round_trips_exact_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source-tree"
            (source / "nested").mkdir(parents=True)
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
                self.assertEqual(expected_sha, quarantine.tree_sha256(source))
                self.assertEqual("", quarantine.MANIFEST.read_text(encoding="utf-8"))


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

    def test_hash_gate_refuses_same_size_same_mtime_corruption(self) -> None:
        # The falsification: stat-based retention alone would bless a
        # same-size, same-mtime but WRONG-byte file. Only the tree-hash gate
        # catches it, so the gate must refuse BEFORE manifest or removal.
        source, dest, _ = self.make_source_and_partial(complete_dest=True)
        victim = dest / "nested" / "b.bin"
        before = victim.stat().st_mtime_ns
        victim.write_bytes(b"BETA-GAMMA")  # same length, different bytes
        os.utime(victim, ns=(before, before))  # keep mtime identical

        with self.assertRaises(SystemExit):
            quarantine.resume(source, dest, reason="hash gate")

        self.assertTrue(source.exists(), "source preserved on gate failure")
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


if __name__ == "__main__":
    unittest.main()
