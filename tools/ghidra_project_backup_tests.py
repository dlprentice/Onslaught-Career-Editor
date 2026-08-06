#!/usr/bin/env python3
"""Focused falsifiers for the Ghidra backup/reopen evidence contract."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import ghidra_project_backup as backup


PROGRAM = "BEA.exe"
MD5 = "3b456964020070efe696d2cc09464a55"
SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"


def make_project(root: Path) -> Path:
    root.mkdir()
    (root / "BEA.gpr").write_bytes(b"")
    idata = root / "BEA.rep" / "idata"
    database = idata / "00" / "~00000000.db"
    database.mkdir(parents=True)
    (idata / "~index.dat").write_bytes(b"index")
    (database / "db.1.gbf").write_bytes(b"database payload")
    return root


def completed(command: list[str], *, sha256: str = SHA256, functions: int = 7555):
    sentinel = (
        f"GHIDRA_PROJECT_OPEN_PROBE_OK program={PROGRAM} md5={MD5} "
        f"sha256={sha256} functions={functions}\n"
    )
    return subprocess.CompletedProcess(command, 0, stdout=sentinel, stderr="")


class GhidraBackupTests(unittest.TestCase):
    def test_reopen_receipt_uses_observed_identity_and_function_count(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = make_project(root / "project")
            result = backup.verify_readonly_open(
                project,
                "BEA",
                PROGRAM,
                root / "analyzeHeadless.bat",
                root,
                program_md5=MD5,
                program_sha256=SHA256,
                runner=lambda command: completed(command),
            )

        self.assertEqual(PROGRAM, result.observed_program_name)
        self.assertEqual(MD5, result.observed_program_md5)
        self.assertEqual(SHA256, result.observed_program_sha256)
        self.assertEqual(7555, result.observed_function_count)
        self.assertTrue(result.comparison.matches)
        self.assertEqual(SHA256, result.command[-1])
        receipt = result.to_json({"path": "probe.log", "bytes": 1, "sha256": "0" * 64})
        self.assertEqual(list(result.command), receipt["commandArgv"])
        self.assertIn("-readOnly", receipt["commandArgv"])
        self.assertIn("-noanalysis", receipt["commandArgv"])
        self.assertIn("-scriptPath", receipt["commandArgv"])

    def test_reopen_refuses_a_mismatched_observed_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = make_project(root / "project")
            with self.assertRaisesRegex(backup.BackupError, "another program identity"):
                backup.verify_readonly_open(
                    project,
                    "BEA",
                    PROGRAM,
                    root / "analyzeHeadless.bat",
                    root,
                    program_md5=MD5,
                    program_sha256=SHA256,
                    runner=lambda command: completed(command, sha256="0" * 64),
                )

    def test_reopen_refuses_labels_without_one_measured_success_sentinel(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = make_project(root / "project")
            with self.assertRaisesRegex(backup.BackupError, "measured success sentinel"):
                backup.verify_readonly_open(
                    project,
                    "BEA",
                    PROGRAM,
                    root / "analyzeHeadless.bat",
                    root,
                    program_md5=MD5,
                    program_sha256=SHA256,
                    runner=lambda command: subprocess.CompletedProcess(
                        command,
                        0,
                        stdout=(
                            "GHIDRA_PROJECT_OPEN_PROBE_FUNCTIONS 7555\n"
                            f"expectedProgramMd5={MD5}\n"
                        ),
                        stderr="",
                    ),
                )

    def test_reopen_refuses_error_markers_duplicate_zero_count_and_nonzero_exit(self) -> None:
        cases = {
            "exception": subprocess.CompletedProcess(
                [], 0, stdout=completed([]).stdout + "Exception: synthetic\n", stderr=""
            ),
            "fail-marker": subprocess.CompletedProcess(
                [], 0,
                stdout=completed([]).stdout + "GHIDRA_PROJECT_OPEN_PROBE_FAIL synthetic\n",
                stderr="",
            ),
            "duplicate": subprocess.CompletedProcess(
                [], 0, stdout=completed([]).stdout * 2, stderr=""
            ),
            "trailing-garbage": subprocess.CompletedProcess(
                [],
                0,
                stdout=completed([]).stdout.rstrip("\n") + " trailing-garbage\n",
                stderr="",
            ),
            "second-other-sentinel": subprocess.CompletedProcess(
                [],
                0,
                stdout=(
                    completed([]).stdout
                    + f"GHIDRA_PROJECT_OPEN_PROBE_OK program=OTHER.exe md5={MD5} "
                    f"sha256={SHA256} functions=7555\n"
                ),
                stderr="",
            ),
            "zero-functions": completed([], functions=0),
            "nonzero-exit": subprocess.CompletedProcess(
                [], 7, stdout=completed([]).stdout, stderr=""
            ),
        }
        for label, result in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                project = make_project(root / "project")
                expected = "exit code" if label == "nonzero-exit" else (
                    "no functions" if label == "zero-functions" else "measured success sentinel"
                )
                with self.assertRaisesRegex(backup.BackupError, expected):
                    backup.verify_readonly_open(
                        project,
                        "BEA",
                        PROGRAM,
                        root / "analyzeHeadless.bat",
                        root,
                        program_md5=MD5,
                        program_sha256=SHA256,
                        runner=lambda command, result=result: subprocess.CompletedProcess(
                            command,
                            result.returncode,
                            stdout=result.stdout,
                            stderr=result.stderr,
                        ),
                    )

    def test_publication_persists_log_and_declares_deleted_probe_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = make_project(root / "project")
            scratch = root / "scratch"
            result = backup.verify_on_copy(
                project,
                scratch,
                "BEA",
                PROGRAM,
                root / "analyzeHeadless.bat",
                root,
                program_md5=MD5,
                program_sha256=SHA256,
                runner=lambda command: completed(command),
            )
            receipt = root / "evidence" / "backup-open.json"
            backup.publish_verification_result(
                result,
                receipt,
                scratch,
                "BEA",
                keep_probe_copy=False,
            )
            document = json.loads(receipt.read_text(encoding="utf-8"))
            log_spec = document["readonlyOpen"]["probeLog"]
            log_path = receipt.parent / log_spec["path"]
            self.assertEqual(backup.SCHEMA_VERSION, document["schemaVersion"])
            self.assertEqual("DELETED_AFTER_VERIFICATION", document["probeCopyDisposition"])
            self.assertFalse(result.probe_copy.exists())
            self.assertEqual(7555, document["readonlyOpen"]["observedFunctionCount"])
            self.assertTrue(log_path.is_file())
            self.assertEqual(log_spec["sha256"], backup.sha256_file(log_path))

    def test_publication_preflights_both_outputs_before_deleting_probe_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = make_project(root / "project")
            scratch = root / "scratch"
            result = backup.verify_on_copy(
                project,
                scratch,
                "BEA",
                PROGRAM,
                root / "analyzeHeadless.bat",
                root,
                program_md5=MD5,
                program_sha256=SHA256,
                runner=lambda command: completed(command),
            )
            receipt = root / "evidence" / "backup-open.json"
            log = receipt.with_name("backup-open.open-probe.log")
            log.parent.mkdir(parents=True)
            log.write_text("preexisting", encoding="utf-8")

            with self.assertRaisesRegex(backup.BackupError, "refusing to overwrite"):
                backup.publish_verification_result(
                    result,
                    receipt,
                    scratch,
                    "BEA",
                    keep_probe_copy=False,
                )

            self.assertTrue(result.probe_copy.is_dir())
            self.assertFalse(receipt.exists())
            self.assertEqual("preexisting", log.read_text(encoding="utf-8"))

    def test_publication_failure_before_log_publish_retains_probe_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = make_project(root / "project")
            scratch = root / "scratch"
            result = backup.verify_on_copy(
                project,
                scratch,
                "BEA",
                PROGRAM,
                root / "analyzeHeadless.bat",
                root,
                program_md5=MD5,
                program_sha256=SHA256,
                runner=lambda command: completed(command),
            )
            receipt = root / "evidence" / "backup-open.json"
            log = receipt.with_name("backup-open.open-probe.log")

            with patch.object(
                backup,
                "publish_staged_atomic_new",
                side_effect=backup.BackupError("synthetic publish failure"),
            ), self.assertRaisesRegex(backup.BackupError, "synthetic publish failure"):
                backup.publish_verification_result(
                    result,
                    receipt,
                    scratch,
                    "BEA",
                    keep_probe_copy=False,
                )

            self.assertTrue(result.probe_copy.is_dir())
            self.assertFalse(log.exists())
            self.assertFalse(receipt.exists())

    def test_retained_probe_copy_is_described_without_claiming_immutability(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = make_project(root / "project")
            scratch = root / "scratch"
            result = backup.verify_on_copy(
                project,
                scratch,
                "BEA",
                PROGRAM,
                root / "analyzeHeadless.bat",
                root,
                program_md5=MD5,
                program_sha256=SHA256,
                runner=lambda command: completed(command),
            )
            receipt = root / "evidence" / "backup-open.json"
            backup.publish_verification_result(
                result,
                receipt,
                scratch,
                "BEA",
                keep_probe_copy=True,
            )
            document = json.loads(receipt.read_text(encoding="utf-8"))

            self.assertEqual("RETAINED_AT_VERIFICATION", document["probeCopyDisposition"])
            self.assertTrue(result.probe_copy.is_dir())


if __name__ == "__main__":
    raise SystemExit(0 if unittest.main(verbosity=2, exit=False).result.wasSuccessful() else 1)
