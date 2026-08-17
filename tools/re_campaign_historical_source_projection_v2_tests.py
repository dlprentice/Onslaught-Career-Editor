#!/usr/bin/env python3
"""Focused tests for the current Generation 24 historical-input projection."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch


TOOL_PATH = Path(__file__).resolve().with_name(
    "re_campaign_historical_source_projection_v2.py"
)
TOOL_SPEC = importlib.util.spec_from_file_location(
    "_bea_re_campaign_historical_source_projection_v2", TOOL_PATH
)
if TOOL_SPEC is None or TOOL_SPEC.loader is None:
    raise RuntimeError("cannot load historical source projection v2")
projection = importlib.util.module_from_spec(TOOL_SPEC)
TOOL_SPEC.loader.exec_module(projection)


TOOL_BYTES = 38_114
TOOL_SHA256 = (
    "cfd5793aa7e98499a9dcbc86925b0b43f5e0178ceec1cd9931712a86035b4b03"
)
GEN24_CAMPAIGN = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-24-current-8280-reseed-e7aa-v1"
)
GEN24_READY_SHA256 = (
    "29ac9d91136c88a651fe5bc2202ca14d9c3a8dc7bd733e1cb7396c4c32a39e86"
)
GEN24_REDUCER_ID = (
    "6cf37430cf7ddace01088aa21a8732943e027f621b54fdf52c9be002dd284582"
)
REPARSE_ATTRIBUTE = 0x400

GENERIC_READ = 0x80000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_DELETE = 0x00000004
OPEN_EXISTING = 3

MSB3027_FAILURE = (
    "C:\\Program Files\\dotnet\\sdk\\10.0.111\\Microsoft.Common.CurrentVersion"
    ".targets(5080,5): error MSB3027: Could not copy "
    '"OnslaughtRebuild.Core.dll" to "bin\\Debug\\net8.0\\'
    'OnslaughtRebuild.Core.dll". Exceeded retry count of 10. Failed. '
    'The file is locked by: "testhost (52688)"\n'
    "C:\\Program Files\\dotnet\\sdk\\10.0.111\\Microsoft.Common.CurrentVersion"
    ".targets(5080,5): error MSB3021: Unable to copy file\n"
)
GENUINE_FAILURE = (
    "  Failed OnslaughtRebuild.Core.Tests.Level100PlayerDamageTests.Example\n"
    "  Error Message:\n   Assert.Equal() Failure\n"
    "Failed!  - Failed:     1, Passed:    29, Skipped:     0, Total:    30\n"
)

SLEEPING_TREE = (
    "import subprocess, sys, time\n"
    "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(600)'])\n"
    "print(child.pid, flush=True)\n"
    "time.sleep(600)\n"
)


@contextlib.contextmanager
def assembly_style_handle(path: Path):
    """Hold ``path`` exactly as a loaded .NET assembly holds it.

    A mapped image is opened GENERIC_READ with FILE_SHARE_READ|FILE_SHARE_DELETE,
    which is precisely why MSBuild's copy of the same destination fails.  Holding
    it this way makes the stale-host guard testable without orphaning a real
    test host.
    """

    import ctypes
    import ctypes.wintypes as wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateFileW.argtypes = [
        ctypes.c_wchar_p,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_void_p,
    ]
    kernel32.CreateFileW.restype = ctypes.c_void_p
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel32.CreateFileW(
        os.fspath(path),
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        0,
        None,
    )
    if not handle or handle == 2**64 - 1:
        raise unittest.SkipTest(
            f"cannot hold {path}: winerror={ctypes.get_last_error()}"
        )
    try:
        yield
    finally:
        kernel32.CloseHandle(handle)


def process_is_alive(pid: int) -> bool:
    completed = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    )
    return str(pid) in completed.stdout


class HistoricalSourceProjectionV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parent.parent
        cls.tool = Path(projection.__file__).resolve()

    def test_tool_and_continuity_inputs_are_exact(self) -> None:
        data = self.tool.read_bytes()
        self.assertEqual(TOOL_BYTES, len(data))
        self.assertEqual(TOOL_SHA256, hashlib.sha256(data).hexdigest())

        old_owner = projection._load_old_owner(self.repo)
        historical_player, player = old_owner.validate_continuity(self.repo)
        actor_projection, actor = projection.validate_actor_continuity(
            self.repo, old_owner
        )
        self.assertEqual(old_owner.HISTORICAL_TEST_SHA256,
                         hashlib.sha256(historical_player).hexdigest())
        self.assertEqual(
            projection.ACTOR_RUNTIME_HISTORICAL_SHA256,
            hashlib.sha256(
                actor_projection[projection.ACTOR_RUNTIME_RELATIVE]
            ).hexdigest(),
        )
        self.assertEqual(
            projection.ACTOR_TEST_HISTORICAL_SHA256,
            hashlib.sha256(
                actor_projection[projection.ACTOR_TEST_RELATIVE]
            ).hexdigest(),
        )
        self.assertTrue(player["relationship"]["historicalLinesRetainedInOrder"])
        self.assertEqual(
            "EXACT_REVIEWED_HELPER_EXTRACTION",
            actor["runtimeRelationship"]["classification"],
        )
        self.assertTrue(actor["testRelationship"]["normalizedByteIdentical"])

    def test_current_runtime_identity_drift_is_rejected(self) -> None:
        old_owner = projection._load_old_owner(self.repo)
        with patch.object(
            projection, "ACTOR_RUNTIME_CURRENT_SHA256", "0" * 64
        ):
            with self.assertRaisesRegex(
                projection.ProjectionError,
                "current actor-weapon runtime identity differs",
            ):
                projection.validate_actor_continuity(self.repo, old_owner)

    def test_bootstrap_detection_is_path_separator_independent(self) -> None:
        detected = projection.is_bootstrap_invocation(
            [
                sys.executable,
                "-I",
                "-B",
                r"C:\proof\tools\re_campaign_frozen_bootstrap.py",
                "--mode",
                "full",
            ]
        )
        self.assertIsNotNone(detected)
        assert detected is not None
        self.assertEqual(3, detected[1])
        self.assertIsNone(
            projection.is_bootstrap_invocation(
                [sys.executable, "tools/re_campaign.py", "verify"]
            )
        )

    def _first_output_assembly(self) -> Path:
        directory = self.repo / projection.TEST_OUTPUT_RELATIVE
        for name in projection.TEST_OUTPUT_HELD_NAMES:
            candidate = directory / name
            if candidate.is_file():
                return candidate
        self.skipTest(f"no built test output assembly under {directory}")

    def test_unheld_outputs_probe_clean(self) -> None:
        self._first_output_assembly()
        self.assertEqual([], projection.held_test_outputs(self.repo))

    @unittest.skipUnless(sys.platform == "win32", "the lock probe is Windows-only")
    def test_stale_test_host_preflight_names_the_environment_fault(self) -> None:
        target = self._first_output_assembly()
        with assembly_style_handle(target):
            held = projection.held_test_outputs(self.repo)
            self.assertTrue(
                any(target.name in entry for entry in held),
                f"the probe missed a held assembly: {held}",
            )
            with self.assertRaises(projection.StaleTestHostError) as caught:
                projection.preflight_test_host_guard(self.repo)
        message = str(caught.exception)
        self.assertIn("STALE_TEST_HOST_DETECTED", message)
        self.assertIn(target.name, message)
        self.assertIn("environment fault, not a rebuild failure", message)
        self.assertNotIn("current focused rebuild suite failed", message)
        self.assertIsInstance(caught.exception, projection.ProjectionError)
        self.assertEqual([], projection.held_test_outputs(self.repo))

    def test_build_lock_failure_is_not_diagnosed_as_a_suite_failure(self) -> None:
        completed = subprocess.CompletedProcess(
            ["dotnet", "test"], 1, MSB3027_FAILURE, ""
        )
        with (
            patch.object(projection, "preflight_test_host_guard"),
            patch.object(
                projection,
                "run_focused_suite",
                return_value=(completed, ["job object owns pid=1"], Path("results")),
            ),
        ):
            with self.assertRaises(projection.StaleTestHostError) as caught:
                projection.validate_current(self.repo, object())
        message = str(caught.exception)
        self.assertIn("STALE_TEST_HOST_DETECTED", message)
        self.assertIn("MSB3027", message)
        self.assertIn("MSB3021", message)
        self.assertNotIn("current focused rebuild suite failed", message)

    def test_genuine_suite_failure_keeps_its_own_diagnosis(self) -> None:
        completed = subprocess.CompletedProcess(
            ["dotnet", "test"], 1, GENUINE_FAILURE, ""
        )
        with (
            patch.object(projection, "preflight_test_host_guard"),
            patch.object(
                projection,
                "run_focused_suite",
                return_value=(completed, [], Path("results")),
            ),
        ):
            with self.assertRaises(projection.ProjectionError) as caught:
                projection.validate_current(self.repo, object())
        self.assertNotIsInstance(caught.exception, projection.StaleTestHostError)
        self.assertIn("current focused rebuild suite failed", str(caught.exception))

    @unittest.skipUnless(sys.platform == "win32", "tree cleanup is Windows-only")
    def test_cleanup_kills_the_whole_tree_then_verifies_it(self) -> None:
        process = subprocess.Popen(
            [sys.executable, "-c", SLEEPING_TREE],
            stdout=subprocess.PIPE,
            text=True,
        )
        try:
            job, notes = projection.adopt_process_tree(process)
            self.assertIsNotNone(job, f"job adoption failed: {notes}")
            grandchild = int(process.stdout.readline().strip())
            self.assertTrue(process_is_alive(grandchild))
            report = projection.terminate_process_tree(self.repo, process, job)
        finally:
            projection._close_job(job)
            if process.poll() is None:  # pragma: no cover - cleanup safety net
                process.kill()
            process.stdout.close()
        joined = " ".join(report)
        self.assertIn("taskkill /T /F /PID", joined)
        self.assertIn("cleanup verified", joined)
        self.assertNotIn("STILL ALIVE", joined)
        deadline = time.monotonic() + 30
        while process_is_alive(grandchild) and time.monotonic() < deadline:
            time.sleep(0.25)
        self.assertFalse(
            process_is_alive(grandchild),
            f"the grandchild survived the tree kill: {joined}",
        )

    @unittest.skipUnless(sys.platform == "win32", "tree cleanup is Windows-only")
    def test_cleanup_reports_a_survivor_instead_of_hiding_it(self) -> None:
        process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        try:
            job, _notes = projection.adopt_process_tree(process)
            with patch.object(
                projection, "live_test_hosts", return_value=([("testhost.exe", 4242)], None)
            ):
                report = projection.terminate_process_tree(self.repo, process, job)
        finally:
            projection._close_job(job)
            if process.poll() is None:  # pragma: no cover - cleanup safety net
                process.kill()
        joined = " ".join(report)
        self.assertIn("STILL ALIVE after cleanup", joined)
        self.assertIn("testhost.exe(4242)", joined)
        self.assertNotIn("cleanup verified", joined)

    def test_cleanup_reports_an_unavailable_process_census(self) -> None:
        with patch.object(
            projection, "live_test_hosts", return_value=([], "tasklist exited 1")
        ):
            with patch.object(projection, "held_test_outputs", return_value=["x.dll"]):
                with self.assertRaises(projection.StaleTestHostError) as caught:
                    projection.preflight_test_host_guard(self.repo)
        self.assertIn("processCensusUnavailable=tasklist exited 1", str(caught.exception))

    @unittest.skipUnless(sys.platform == "win32", "job objects are Windows-only")
    def test_job_object_takes_the_tree_down_with_a_hard_killed_parent(self) -> None:
        program = (
            "import importlib.util, subprocess, sys, time\n"
            "spec = importlib.util.spec_from_file_location('p', r'"
            + os.fspath(Path(projection.__file__).resolve())
            + "')\n"
            "m = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(m)\n"
            "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(600)'])\n"
            "job, notes = m.adopt_process_tree(child)\n"
            "print(child.pid if job is not None else 0, flush=True)\n"
            "time.sleep(600)\n"
        )
        parent = subprocess.Popen(
            [sys.executable, "-B", "-c", program],
            stdout=subprocess.PIPE,
            text=True,
        )
        try:
            grandchild = int(parent.stdout.readline().strip())
            self.assertNotEqual(0, grandchild, "the child was never adopted into a job")
            self.assertTrue(process_is_alive(grandchild))
            # No /T and no cleanup code: only KILL_ON_JOB_CLOSE can take the
            # grandchild down when the owning process dies without running.
            subprocess.run(
                ["taskkill", "/F", "/PID", str(parent.pid)],
                capture_output=True,
                text=True,
                check=False,
            )
            deadline = time.monotonic() + 30
            while process_is_alive(grandchild) and time.monotonic() < deadline:
                time.sleep(0.25)
            self.assertFalse(
                process_is_alive(grandchild),
                "the grandchild outlived its hard-killed parent",
            )
        finally:
            if parent.poll() is None:  # pragma: no cover - cleanup safety net
                parent.kill()
            parent.stdout.close()

    def test_current_focused_rebuild_contracts_pass(self) -> None:
        old_owner = projection._load_old_owner(self.repo)
        result = projection.validate_current(self.repo, old_owner)
        self.assertEqual(30, result["focusedRebuild"]["passed"])
        self.assertEqual(0, result["focusedRebuild"]["failed"])
        self.assertTrue(result["focusedRebuild"]["staleTestHostPreflightPassed"])
        self.assertTrue(
            any(
                "KILL_ON_JOB_CLOSE" in note
                for note in result["focusedRebuild"]["processTreeOwnership"]
            )
            or sys.platform != "win32",
            "the focused suite ran without owning its process tree: "
            f"{result['focusedRebuild']['processTreeOwnership']}",
        )
        self.assertTrue(
            result["frozenPlayerDamageProof"][
                "currentIdentityRejectedByExactInputGate"
            ]
        )

    def test_full_generation24_replay_when_evidence_is_local(self) -> None:
        campaign = self.repo / GEN24_CAMPAIGN
        if not (campaign / "campaign.ready.json").is_file():
            self.skipTest("retained Generation 24 evidence is unavailable")
        local_lab = self.repo / "local-lab"
        stat = local_lab.lstat()
        if local_lab.is_symlink() or (
            getattr(stat, "st_file_attributes", 0) & REPARSE_ATTRIBUTE
        ):
            self.skipTest("retained evidence is exposed through a reparse point")

        environment = os.environ.copy()
        cwd = Path.cwd()
        output = io.StringIO()
        try:
            os.environ["BEA_REPO_ROOT"] = os.fspath(self.repo)
            os.chdir(self.repo)
            with contextlib.redirect_stdout(output):
                exit_code = projection.main(
                    [
                        "--campaign",
                        os.fspath(GEN24_CAMPAIGN),
                        "--mode",
                        "full",
                        "--expected-ready-sha256",
                        GEN24_READY_SHA256,
                        "--expected-reducer-id",
                        GEN24_REDUCER_ID,
                    ]
                )
        finally:
            os.chdir(cwd)
            os.environ.clear()
            os.environ.update(environment)
        self.assertEqual(0, exit_code)
        self.assertIn("CAMPAIGN_VERIFIED", output.getvalue())
        self.assertIn("projected=3", output.getvalue())


if __name__ == "__main__":
    unittest.main()
