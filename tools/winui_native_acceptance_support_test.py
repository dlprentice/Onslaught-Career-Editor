#!/usr/bin/env python3
"""Focused tests for shared native WinUI acceptance support."""

from __future__ import annotations

import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import winui_native_acceptance_support as support


class NativeAcceptanceSupportTests(unittest.TestCase):
    METHOD = "ExpectedNativeMethod"

    def write_trx(
        self,
        root: Path,
        *,
        total: int = 1,
        executed: int = 1,
        passed: int = 1,
        not_executed: int = 0,
        outcome: str = "Passed",
        method: str | None = None,
    ) -> Path:
        path = root / "native.trx"
        path.write_text(
            f"""<?xml version="1.0" encoding="utf-8"?>
<TestRun xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010">
  <Results>
    <UnitTestResult testName="{method or self.METHOD}" outcome="{outcome}" />
  </Results>
  <ResultSummary outcome="{outcome}">
    <Counters total="{total}" executed="{executed}" passed="{passed}"
      failed="0" error="0" timeout="0" aborted="0" inconclusive="0"
      notExecuted="{not_executed}" />
  </ResultSummary>
</TestRun>
""",
            encoding="utf-8",
        )
        return path

    def test_validate_exact_trx_accepts_one_named_passing_test(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            summary = support.validate_exact_trx(
                self.write_trx(Path(temp_dir)),
                self.METHOD,
                "native fixture",
            )

        self.assertEqual(1, summary["total"])
        self.assertEqual(1, summary["passed"])

    def test_validate_exact_trx_rejects_skipped_test(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trx = self.write_trx(
                Path(temp_dir),
                executed=0,
                passed=0,
                not_executed=1,
                outcome="NotExecuted",
            )
            with self.assertRaisesRegex(
                support.NativeAcceptanceError,
                "exactly one executed passing test",
            ):
                support.validate_exact_trx(trx, self.METHOD, "native fixture")

    def test_png_dimensions_reads_only_valid_png_ihdr(self) -> None:
        signature = bytes((137, 80, 78, 71, 13, 10, 26, 10))
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "capture.png"
            path.write_bytes(signature + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 760, 820))
            self.assertEqual((760, 820), support.png_dimensions(path))

            path.write_bytes(bytes(24))
            with self.assertRaisesRegex(support.NativeAcceptanceError, "not PNG"):
                support.png_dimensions(path)

    def test_validate_invocation_id_requires_lowercase_32_hex(self) -> None:
        support.validate_invocation_id("0123456789abcdef0123456789abcdef")
        for invalid in ("ABC", "0123456789ABCDEF0123456789ABCDEF", "g" * 32):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(support.NativeAcceptanceError, "invocation ID"):
                    support.validate_invocation_id(invalid)

    def test_append_cleanup_error_preserves_primary_and_cleanup_context(self) -> None:
        error = support.append_cleanup_error(
            ValueError("primary"),
            "final census",
            RuntimeError("cleanup"),
        )

        self.assertIsInstance(error, support.NativeAcceptanceError)
        self.assertIn("primary", str(error))
        self.assertIn("final census failed: cleanup", str(error))

    def test_run_command_timeout_terminates_only_captured_spawn_identity(self) -> None:
        process = mock.Mock()
        process.pid = 4242
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired(["fixture"], 1), 0]
        identity = support.OwnedProcessIdentity(
            process_id=4242,
            start_time_utc_ticks=638881920000000000,
            executable_path=Path(r"C:\Program Files\dotnet\dotnet.exe"),
        )
        with mock.patch.object(support.subprocess, "Popen", return_value=process), mock.patch.object(
            support,
            "capture_owned_process_identity",
            return_value=identity,
        ) as capture, mock.patch.object(
            support,
            "terminate_owned_process_tree",
        ) as terminate:
            with self.assertRaises(subprocess.TimeoutExpired):
                support.run_command(
                    ["fixture"],
                    repo_root=Path.cwd(),
                    timeout=1,
                )

        capture.assert_called_once_with(4242, repo_root=Path.cwd())
        terminate.assert_called_once_with(identity, repo_root=Path.cwd())
        process.kill.assert_not_called()

    def test_tree_termination_binds_start_and_path_before_taskkill(self) -> None:
        identity = support.OwnedProcessIdentity(
            process_id=4242,
            start_time_utc_ticks=638881920000000000,
            executable_path=Path(r"C:\Program Files\dotnet\dotnet.exe"),
        )
        completed = subprocess.CompletedProcess([], 42, "", "")

        with mock.patch.object(support.subprocess, "run", return_value=completed) as run:
            with self.assertRaisesRegex(support.NativeAcceptanceError, "identity"):
                support.terminate_owned_process_tree(identity, repo_root=Path.cwd())

        command = run.call_args.args[0]
        environment = run.call_args.kwargs["env"]
        script = command[-1]
        self.assertEqual(command[:4], ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"])
        self.assertLess(script.index("StartTime.ToUniversalTime().Ticks"), script.index("taskkill.exe"))
        self.assertLess(script.index("GetFullPath"), script.index("taskkill.exe"))
        self.assertEqual(environment["ONSLAUGHT_NATIVE_CLEANUP_PID"], "4242")
        self.assertEqual(environment["ONSLAUGHT_NATIVE_CLEANUP_PATH"], str(identity.executable_path))
        self.assertEqual(
            environment["ONSLAUGHT_NATIVE_CLEANUP_START_TICKS"],
            str(identity.start_time_utc_ticks),
        )

    def test_recursive_cleanup_rejects_nested_junction_without_touching_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            owned = root / "owned"
            outside = root / "outside"
            owned.mkdir()
            outside.mkdir()
            canary = outside / "canary.txt"
            canary.write_text("preserve", encoding="utf-8")
            junction = owned / "nested"
            self._create_junction(junction, outside)
            try:
                with self.assertRaisesRegex(support.NativeAcceptanceError, "reparse point"):
                    support.remove_reparse_free_tree(owned, label="owned fixture")
                self.assertEqual(canary.read_text(encoding="utf-8"), "preserve")
                self.assertTrue(owned.is_dir())
            finally:
                junction.rmdir()

    @staticmethod
    def _create_junction(link: Path, target: Path) -> None:
        completed = subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
            text=True,
            capture_output=True,
            timeout=10,
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr or completed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
