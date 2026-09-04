#!/usr/bin/env python3
"""Fail-closed routing tests for the historical cohort replay harness."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

# run_tool_tests.py invokes suites by path with cwd=ROOT, which puts tools/ (not
# the repo root) on sys.path; add the root so `from tools import` resolves.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import ghidra_cohort_replay as replay  # noqa: E402


class CohortReplayRoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.ghidra = self.root / "analyzeHeadless"
        self.ghidra.write_text("test executable placeholder\n", encoding="utf-8")
        self.backups = self.root / "restored-backups"
        self.backups.mkdir()
        self.lane = self.root / "local-lab" / "cohort-rehearsal" / "run-1"
        self.original_globals = {
            "GHIDRA": replay.GHIDRA,
            "BACKUPS": replay.BACKUPS,
            "LANE": replay.LANE,
            "RECEIPTS": replay.RECEIPTS,
            "SANDBOX": replay.SANDBOX,
            "SANDBOX_BACKUP": replay.SANDBOX_BACKUP,
            "RUNTIME_CONFIGURED": replay.RUNTIME_CONFIGURED,
        }
        self.original_backups = {
            name: config["backup"] for name, config in replay.COHORTS.items()
        }

    def tearDown(self) -> None:
        for name, backup in self.original_backups.items():
            replay.COHORTS[name]["backup"] = backup
        for name, value in self.original_globals.items():
            setattr(replay, name, value)
        self.temporary.cleanup()

    def test_cli_refuses_before_any_default_database_route_is_used(self) -> None:
        output = io.StringIO()
        with redirect_stderr(output):
            result = replay.main(["--cohort", "boundary-cohort41"])
        self.assertEqual(2, result)
        self.assertIn("requires explicit --ghidra", output.getvalue())
        self.assertFalse(self.lane.exists())

    def test_direct_consumer_refuses_without_runtime_configuration(self) -> None:
        replay.RUNTIME_CONFIGURED = False
        with self.assertRaisesRegex(replay.RoutingError, "replay is unconfigured"):
            replay.run_cohort("boundary-cohort41", ["identity"])

    def test_sealed_package_cannot_be_opened_in_place(self) -> None:
        archive_parent = self.root / "archive" / "Onslaught-Ghidra-Recovery"
        package = archive_parent / "2026-08-31-consolidated-v1"
        package.mkdir(parents=True)
        with patch.object(replay, "RECOVERY_PACKAGE_PARENT", archive_parent):
            with self.assertRaisesRegex(replay.RoutingError, "outside the sealed"):
                replay.configure_runtime(self.ghidra, package, self.lane)

    def test_active_mutable_project_cannot_be_a_restored_backup_root(self) -> None:
        active_project = self.root / "active" / "BEA"
        active_project.mkdir(parents=True)
        with patch.object(replay, "ACTIVE_MUTABLE_PROJECT", active_project):
            with self.assertRaisesRegex(replay.RoutingError, "protected owner"):
                replay.configure_runtime(self.ghidra, active_project, self.lane)

    def test_failed_reconfiguration_disables_an_earlier_safe_route(self) -> None:
        replay.configure_runtime(self.ghidra, self.backups, self.lane)
        with self.assertRaises(replay.RoutingError):
            replay.configure_runtime(self.ghidra, Path("relative-backups"), self.lane)
        self.assertFalse(replay.RUNTIME_CONFIGURED)

    def test_headless_rejects_projects_and_logs_outside_the_lane(self) -> None:
        replay.configure_runtime(self.ghidra, self.backups, self.lane)
        outside_project = self.root / "outside-project"
        outside_project.mkdir()
        with self.assertRaisesRegex(replay.RoutingError, "outside the configured lane"):
            replay.headless(
                "unsafe", outside_project, [], True, self.lane / "logs", timeout=1
            )

    def test_sandbox_route_is_explicit_and_outside_rehearsal_containment(self) -> None:
        sandbox = self.root / "local-lab" / "ghidra-noncanonical-sandbox"
        project = sandbox / "project"
        project.mkdir(parents=True)
        replay.configure_runtime(self.ghidra, self.backups, self.lane, sandbox)
        self.assertEqual(sandbox, replay.SANDBOX)

        with self.assertRaisesRegex(replay.RoutingError, "outside the configured lane"):
            replay.headless(
                "ordinary", project, [], True, self.lane / "logs", timeout=1
            )
        completed = SimpleNamespace(returncode=0, stdout="", stderr="")
        with patch.object(replay.subprocess, "run", return_value=completed):
            result = replay.headless(
                "containment",
                project,
                [],
                True,
                self.lane / "logs",
                timeout=1,
                allow_containment_probe=True,
            )
        self.assertEqual(0, result[0])

    def test_sandbox_root_cannot_enter_the_rehearsal_lane(self) -> None:
        with self.assertRaisesRegex(replay.RoutingError, "must not contain"):
            replay.configure_runtime(
                self.ghidra,
                self.backups,
                self.lane,
                self.lane / "sandbox",
            )

    def test_restored_backup_symlink_refuses_before_destination_write(self) -> None:
        backup = self.backups / "historical-alias"
        backup.mkdir()
        outside = self.root / "outside-file"
        outside.write_text("must not be followed\n", encoding="utf-8")
        (backup / "escape").symlink_to(outside)
        destination = self.lane / "replicas" / "historical-alias"
        replay.configure_runtime(self.ghidra, self.backups, self.lane)
        with self.assertRaisesRegex(replay.RoutingError, "contains a symlink"):
            replay.restore(destination, backup)
        self.assertFalse(destination.exists())

    def test_explicit_paths_rebase_every_historical_backup(self) -> None:
        replay.configure_runtime(self.ghidra, self.backups, self.lane)
        self.assertTrue(replay.RUNTIME_CONFIGURED)
        self.assertEqual(self.ghidra, replay.GHIDRA)
        self.assertEqual(self.backups, replay.BACKUPS)
        self.assertEqual(self.lane / "receipts", replay.RECEIPTS)
        self.assertIsNone(replay.SANDBOX)
        self.assertTrue(
            all(
                Path(config["backup"]).parent == self.backups
                for config in replay.COHORTS.values()
            )
        )

    def test_cli_dispatches_only_after_explicit_safe_configuration(self) -> None:
        with patch.object(replay, "run_cohort", return_value=0) as run:
            result = replay.main(
                [
                    "--cohort",
                    "boundary-cohort41",
                    "--ghidra",
                    str(self.ghidra),
                    "--restored-backups",
                    str(self.backups),
                    "--lane",
                    str(self.lane),
                ]
            )
        self.assertEqual(0, result)
        run.assert_called_once_with(
            "boundary-cohort41", ["identity", "dry", "apply", "readback"]
        )

    def test_verdict_requires_an_explicit_receipt_root(self) -> None:
        output = io.StringIO()
        with redirect_stderr(output):
            result = replay.main(["--verdict"])
        self.assertEqual(2, result)
        self.assertIn("requires an explicit --receipts", output.getvalue())


if __name__ == "__main__":
    unittest.main()
