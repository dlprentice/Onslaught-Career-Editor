#!/usr/bin/env python3
"""Focused tests for recursive Ghidra project backup verification."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import ghidra_project_backup as backup


class GhidraProjectBackupTests(unittest.TestCase):
    EXPECTED_MD5 = "3b456964020070efe696d2cc09464a55"

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="ghidra-backup-test-")
        self.root = Path(self.temp_dir.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.write_complete_project(self.source)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def write_complete_project(root: Path, project_name: str = "BEA") -> None:
        (root / f"{project_name}.gpr").write_bytes(b"")
        rep = root / f"{project_name}.rep"
        (rep / "idata" / "00" / "~00000000.db").mkdir(parents=True)
        (rep / "versioned").mkdir()
        (rep / "project.prp").write_text("owner=test\n", encoding="utf-8")
        (rep / "idata" / "~index.dat").write_bytes(b"index")
        (rep / "versioned" / "~index.dat").write_bytes(b"versions")
        (rep / "idata" / "00" / "~00000000.db" / "db.1.gbf").write_bytes(b"program-bytes")

    def test_inventory_is_recursive_stable_and_hashes_every_project_file(self) -> None:
        manifest = backup.build_manifest(self.source, "BEA")

        self.assertEqual(
            [row.relative_path for row in manifest.files],
            [
                "BEA.gpr",
                "BEA.rep/idata/00/~00000000.db/db.1.gbf",
                "BEA.rep/idata/~index.dat",
                "BEA.rep/project.prp",
                "BEA.rep/versioned/~index.dat",
            ],
        )
        payload = next(row for row in manifest.files if row.relative_path.endswith("db.1.gbf"))
        self.assertEqual(payload.sha256, hashlib.sha256(b"program-bytes").hexdigest())
        self.assertTrue(manifest.structurally_complete)

    def test_rejects_shell_with_only_zero_length_gpr_and_project_properties(self) -> None:
        shell = self.root / "shell"
        shell.mkdir()
        (shell / "BEA.gpr").write_bytes(b"")
        (shell / "BEA.rep").mkdir()
        (shell / "BEA.rep" / "project.prp").write_text("owner=test\n", encoding="utf-8")

        with self.assertRaisesRegex(backup.BackupError, "meaningful recursive"):
            backup.build_manifest(shell, "BEA")

    def test_rejects_rep_with_only_unrelated_nonzero_junk(self) -> None:
        shell = self.root / "junk-shell"
        shell.mkdir()
        (shell / "BEA.gpr").write_bytes(b"")
        (shell / "BEA.rep").mkdir()
        (shell / "BEA.rep" / "unrelated.bin").write_bytes(b"not a Ghidra store")

        with self.assertRaisesRegex(backup.BackupError, "meaningful recursive"):
            backup.build_manifest(shell, "BEA")

    def test_rejects_missing_gpr_or_rep(self) -> None:
        missing_gpr = self.root / "missing-gpr"
        (missing_gpr / "BEA.rep").mkdir(parents=True)
        with self.assertRaisesRegex(backup.BackupError, "BEA.gpr"):
            backup.build_manifest(missing_gpr, "BEA")

        missing_rep = self.root / "missing-rep"
        missing_rep.mkdir()
        (missing_rep / "BEA.gpr").write_bytes(b"")
        with self.assertRaisesRegex(backup.BackupError, "BEA.rep"):
            backup.build_manifest(missing_rep, "BEA")

    def test_copy_project_pair_recurses_and_matches_source_hashes(self) -> None:
        destination = self.root / "backup"

        result = backup.copy_project_pair(self.source, destination, "BEA")

        self.assertTrue((destination / "BEA.gpr").is_file())
        self.assertTrue((destination / "BEA.rep" / "idata" / "00" / "~00000000.db" / "db.1.gbf").is_file())
        self.assertTrue((destination / "backup_manifest.json").is_file())
        self.assertTrue(result.source_stable)
        self.assertTrue(result.copy_comparison.matches)

        manifest_text = (destination / "backup_manifest.json").read_text(encoding="utf-8")
        self.assertNotIn(".partial-", manifest_text)
        self.assertNotIn(str(self.source), manifest_text)
        self.assertEqual(json.loads(manifest_text)["destination"]["fileCount"], 5)

    def test_rejects_project_root_symlink_before_resolving_it(self) -> None:
        alias = self.root / "source-alias"
        try:
            alias.symlink_to(self.source, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlink unavailable: {exc}")

        with self.assertRaisesRegex(backup.BackupError, "symlink or reparse"):
            backup.build_manifest(alias, "BEA")

    def test_copy_rejects_source_alias_before_resolving_it(self) -> None:
        alias = self.root / "copy-source-alias"
        try:
            alias.symlink_to(self.source, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlink unavailable: {exc}")

        with self.assertRaisesRegex(backup.BackupError, "symlink or reparse"):
            backup.copy_project_pair(alias, self.root / "backup-from-alias", "BEA")

    def test_copy_rejects_destination_parent_alias(self) -> None:
        real_parent = self.root / "real-backup-parent"
        real_parent.mkdir()
        alias_parent = self.root / "backup-parent-alias"
        try:
            alias_parent.symlink_to(real_parent, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlink unavailable: {exc}")

        with self.assertRaisesRegex(backup.BackupError, "symlink or reparse"):
            backup.copy_project_pair(self.source, alias_parent / "backup", "BEA")

    def test_copy_rejects_destination_nested_under_source_project(self) -> None:
        destination = self.source / "BEA.rep" / "nested-backup"

        with self.assertRaisesRegex(backup.BackupError, "disjoint"):
            backup.copy_project_pair(self.source, destination, "BEA")

        self.assertFalse(destination.exists())

    def test_copy_refuses_existing_destination(self) -> None:
        destination = self.root / "existing"
        destination.mkdir()

        with self.assertRaisesRegex(backup.BackupError, "already exists"):
            backup.copy_project_pair(self.source, destination, "BEA")

    def test_copy_failure_removes_only_its_owned_partial_directory(self) -> None:
        destination = self.root / "failed-backup"

        with mock.patch.object(backup.shutil, "copytree", side_effect=OSError("copy failed")):
            with self.assertRaisesRegex(OSError, "copy failed"):
                backup.copy_project_pair(self.source, destination, "BEA")

        self.assertFalse(destination.exists())
        self.assertEqual(list(self.root.glob(".failed-backup.partial-*")), [])

    def test_compare_manifests_reports_missing_extra_size_and_hash_differences(self) -> None:
        destination = self.root / "comparison"
        backup.copy_project_pair(self.source, destination, "BEA")
        expected = backup.build_manifest(self.source, "BEA")

        (destination / "BEA.rep" / "versioned" / "~index.dat").unlink()
        (destination / "BEA.rep" / "idata" / "~index.dat").write_bytes(b"INDEX")
        (destination / "BEA.rep" / "idata" / "00" / "~00000000.db" / "db.1.gbf").write_bytes(b"program-expanded")
        (destination / "BEA.rep" / "extra.bin").write_bytes(b"extra")
        actual = backup.build_manifest(destination, "BEA")

        comparison = backup.compare_manifests(expected, actual)
        self.assertIn("BEA.rep/versioned/~index.dat", comparison.missing)
        self.assertIn("BEA.rep/extra.bin", comparison.extra)
        self.assertIn("BEA.rep/idata/00/~00000000.db/db.1.gbf", comparison.size_differences)
        self.assertIn("BEA.rep/idata/~index.dat", comparison.hash_differences)
        self.assertFalse(comparison.matches)

    def test_build_open_command_is_explicitly_read_only_and_uses_probe_script(self) -> None:
        command = backup.build_open_command(
            Path("analyzeHeadless.bat"),
            self.source,
            "BEA",
            "BEA.exe",
            Path("repo-tools"),
            "3b456964020070efe696d2cc09464a55",
        )

        self.assertEqual(command[:3], ["analyzeHeadless.bat", str(self.source.resolve()), "BEA"])
        self.assertIn("-readOnly", command)
        self.assertIn("-noanalysis", command)
        self.assertEqual(command[command.index("-process") + 1], "BEA.exe")
        self.assertEqual(command[command.index("-postScript") + 1], "GhidraProjectOpenProbe.java")
        self.assertEqual(command[-2:], ["BEA.exe", "3b456964020070efe696d2cc09464a55"])

    def test_low_level_open_probe_requires_program_name_and_md5(self) -> None:
        source = (Path(__file__).resolve().parent / "GhidraProjectOpenProbe.java").read_text(
            encoding="utf-8"
        )

        self.assertIn("args.length != 2", source)
        self.assertIn("required 32-hex executable MD5", source)
        self.assertIn("[0-9a-fA-F]{32}", source)
        self.assertNotIn("optional executable MD5", source)

    def test_open_probe_requires_imported_executable_md5(self) -> None:
        expected_md5 = self.EXPECTED_MD5

        def successful_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=f"GHIDRA_PROJECT_OPEN_PROBE_OK program=BEA.exe md5={expected_md5}\n",
                stderr="",
            )

        result = backup.verify_readonly_open(
            self.source,
            "BEA",
            "BEA.exe",
            Path("analyzeHeadless.bat"),
            Path("repo-tools"),
            program_md5=expected_md5,
            runner=successful_runner,
        )

        self.assertEqual(result.to_json()["expectedProgramMd5"], expected_md5)

    def test_default_open_runner_is_bounded_and_fails_closed_on_timeout(self) -> None:
        with mock.patch.object(
            backup.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["analyzeHeadless.bat"], 300),
        ) as run:
            with self.assertRaisesRegex(backup.BackupError, "timed out"):
                backup.default_runner(["analyzeHeadless.bat"])

        self.assertEqual(run.call_args.kwargs["timeout"], backup.DEFAULT_OPEN_TIMEOUT_SECONDS)

    def test_open_probe_requires_exit_zero_sentinel_and_zero_hash_drift(self) -> None:
        def successful_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=f"GHIDRA_PROJECT_OPEN_PROBE_OK program=BEA.exe md5={self.EXPECTED_MD5}\n",
                stderr="",
            )

        result = backup.verify_readonly_open(
            self.source,
            "BEA",
            "BEA.exe",
            Path("analyzeHeadless.bat"),
            Path("repo-tools"),
            program_md5=self.EXPECTED_MD5,
            runner=successful_runner,
        )

        self.assertTrue(result.opened)
        self.assertTrue(result.content_stable)

    def test_open_probe_rejects_missing_sentinel_nonzero_exit_and_content_drift(self) -> None:
        def missing_sentinel(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 0, stdout="ordinary output", stderr="")

        with self.assertRaisesRegex(backup.BackupError, "success sentinel"):
            backup.verify_readonly_open(
                self.source,
                "BEA",
                "BEA.exe",
                Path("analyzeHeadless.bat"),
                Path("repo-tools"),
                program_md5=self.EXPECTED_MD5,
                runner=missing_sentinel,
            )

        def failing_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 1, stdout="", stderr="open failed")

        with self.assertRaisesRegex(backup.BackupError, "exit code 1"):
            backup.verify_readonly_open(
                self.source,
                "BEA",
                "BEA.exe",
                Path("analyzeHeadless.bat"),
                Path("repo-tools"),
                program_md5=self.EXPECTED_MD5,
                runner=failing_runner,
            )

        def mutating_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            (self.source / "BEA.rep" / "idata" / "~index.dat").write_bytes(b"mutated")
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=f"GHIDRA_PROJECT_OPEN_PROBE_OK program=BEA.exe md5={self.EXPECTED_MD5}\n",
                stderr="",
            )

        with self.assertRaisesRegex(backup.BackupError, "content drift"):
            backup.verify_readonly_open(
                self.source,
                "BEA",
                "BEA.exe",
                Path("analyzeHeadless.bat"),
                Path("repo-tools"),
                program_md5=self.EXPECTED_MD5,
                runner=mutating_runner,
            )

    def test_failed_copied_open_probe_removes_only_its_owned_scratch_copy(self) -> None:
        scratch = self.root / "failed-open-scratch"

        def failing_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 1, stdout="", stderr="open failed")

        with self.assertRaisesRegex(backup.BackupError, "exit code 1"):
            backup.verify_on_copy(
                self.source,
                scratch,
                "BEA",
                "BEA.exe",
                Path("analyzeHeadless.bat"),
                Path("repo-tools"),
                program_md5=self.EXPECTED_MD5,
                runner=failing_runner,
            )

        self.assertEqual(list(scratch.iterdir()), [])

    def test_verify_rejects_scratch_nested_under_source_project(self) -> None:
        scratch = self.source / "BEA.rep" / "nested-scratch"

        with self.assertRaisesRegex(backup.BackupError, "disjoint"):
            backup.verify_on_copy(
                self.source,
                scratch,
                "BEA",
                "BEA.exe",
                Path("analyzeHeadless.bat"),
                Path("repo-tools"),
                program_md5=self.EXPECTED_MD5,
            )

        self.assertFalse(scratch.exists())

    def test_sanitized_summary_contains_no_absolute_paths(self) -> None:
        result = backup.copy_project_pair(self.source, self.root / "summary-backup", "BEA")

        summary = backup.sanitized_summary(result)

        self.assertNotIn(str(self.root), summary)
        self.assertIn("HashDiffCount=0", summary)

    def test_probe_cleanup_uses_the_selected_project_name(self) -> None:
        scratch = self.root / "scratch"
        scratch.mkdir()
        probe_copy = scratch / "ALT-open-probe-0123456789abcdef"
        probe_copy.mkdir()

        backup.safe_remove_probe_copy(probe_copy, scratch, "ALT")

        self.assertFalse(probe_copy.exists())

    def test_receipt_writer_refuses_to_overwrite_existing_evidence(self) -> None:
        receipt = self.root / "receipt.json"
        receipt.write_text("preserve me\n", encoding="utf-8")

        with self.assertRaises(FileExistsError):
            backup.write_json(receipt, {"replacement": True})

        self.assertEqual(receipt.read_text(encoding="utf-8"), "preserve me\n")

    def test_receipt_failure_still_cleans_successful_owned_probe_copy(self) -> None:
        scratch = self.root / "receipt-failure-scratch"

        def successful_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=f"GHIDRA_PROJECT_OPEN_PROBE_OK program=BEA.exe md5={self.EXPECTED_MD5}\n",
                stderr="",
            )

        result = backup.verify_on_copy(
            self.source,
            scratch,
            "BEA",
            "BEA.exe",
            Path("analyzeHeadless.bat"),
            Path("repo-tools"),
            program_md5=self.EXPECTED_MD5,
            runner=successful_runner,
        )
        receipt = self.root / "existing-receipt.json"
        receipt.write_text("preserve me\n", encoding="utf-8")

        with self.assertRaises(FileExistsError):
            backup.publish_verification_result(result, receipt, scratch, "BEA", keep_probe_copy=False)

        self.assertFalse(result.probe_copy.exists())
        self.assertEqual(receipt.read_text(encoding="utf-8"), "preserve me\n")

    def test_receipt_inside_source_store_is_rejected_and_probe_is_cleaned(self) -> None:
        scratch = self.root / "source-receipt-scratch"

        def successful_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=f"GHIDRA_PROJECT_OPEN_PROBE_OK program=BEA.exe md5={self.EXPECTED_MD5}\n",
                stderr="",
            )

        result = backup.verify_on_copy(
            self.source,
            scratch,
            "BEA",
            "BEA.exe",
            Path("analyzeHeadless.bat"),
            Path("repo-tools"),
            program_md5=self.EXPECTED_MD5,
            runner=successful_runner,
        )
        receipt = self.source / "BEA.rep" / "unsafe-receipt.json"

        with self.assertRaisesRegex(backup.BackupError, "disjoint"):
            backup.publish_verification_result(
                result, receipt, scratch, "BEA", keep_probe_copy=False
            )

        self.assertFalse(receipt.exists())
        self.assertFalse(result.probe_copy.exists())

    def test_receipt_inside_scratch_root_is_rejected_and_probe_is_cleaned(self) -> None:
        scratch = self.root / "scratch-receipt-root"

        def successful_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=f"GHIDRA_PROJECT_OPEN_PROBE_OK program=BEA.exe md5={self.EXPECTED_MD5}\n",
                stderr="",
            )

        result = backup.verify_on_copy(
            self.source,
            scratch,
            "BEA",
            "BEA.exe",
            Path("analyzeHeadless.bat"),
            Path("repo-tools"),
            program_md5=self.EXPECTED_MD5,
            runner=successful_runner,
        )
        receipt = scratch / "unsafe-receipt.json"

        with self.assertRaisesRegex(backup.BackupError, "disjoint"):
            backup.publish_verification_result(
                result, receipt, scratch, "BEA", keep_probe_copy=False
            )

        self.assertFalse(receipt.exists())
        self.assertFalse(result.probe_copy.exists())

    def test_inspection_output_inside_project_store_is_rejected(self) -> None:
        output = self.source / "BEA.rep" / "unsafe-inspection.json"

        with self.assertRaisesRegex(backup.BackupError, "disjoint"):
            backup.validate_external_output_path(
                output, [self.source], "inspection output"
            )

        self.assertFalse(output.exists())

    def test_verify_cli_requires_imported_program_md5_binding(self) -> None:
        argv = [
            "ghidra_project_backup.py",
            "verify",
            str(self.source),
            "--scratch-root",
            str(self.root / "scratch"),
            "--receipt",
            str(self.root / "receipt.json"),
            "--analyze-headless",
            str(self.root / "analyzeHeadless.bat"),
        ]
        with mock.patch("sys.argv", argv), self.assertRaises(SystemExit) as raised:
            backup.main()
        self.assertEqual(2, raised.exception.code)


if __name__ == "__main__":
    unittest.main()
