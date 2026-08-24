#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
