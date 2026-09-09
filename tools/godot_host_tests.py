#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Companion launch routing with fake tools; no window or retail data is used."""
from __future__ import annotations

import json
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import godot_host as host


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux launcher")
class CompanionLauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="godot-host-tests-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.canonical = self.root / "canonical"
        self.project = self.root / "worktree/companion/OnslaughtToolkit.Godot"
        self.project.mkdir(parents=True)
        (self.project / "OnslaughtToolkit.Godot.csproj").touch()
        self.calls = self.root / "calls.jsonl"
        self.engine = self.root / "engine/godot-mono"
        packages = self.engine.parent / "GodotSharp/Tools/nupkgs"
        packages.mkdir(parents=True)
        (packages / "Godot.NET.Sdk.4.7.2.nupkg").touch()
        fake = (
            f"#!{sys.executable}\n"
            "import json, os, pathlib, sys\n"
            "if '--version' in sys.argv:\n"
            f"    print(os.environ.get('FAKE_VERSION', {host.ENGINE_VERSION!r}))\n"
            "    raise SystemExit(0)\n"
            "with open(os.environ['FAKE_CALLS'], 'a') as output:\n"
            "    output.write(json.dumps({'tool': pathlib.Path(sys.argv[0]).name, "
            "'args': sys.argv[1:], 'tmp': os.environ['TMPDIR'], "
            "'data': os.environ['XDG_DATA_HOME'], 'cache': os.environ['XDG_CACHE_HOME']}) + '\\n')\n"
            "if pathlib.Path(sys.argv[0]).name == 'godot-mono':\n"
            "    raise SystemExit(int(os.environ.get('FAKE_EXIT', '0')))\n"
        )
        for executable in (self.engine, self.engine.parent / "dotnet"):
            executable.write_text(fake, encoding="utf-8")
            executable.chmod(0o700)
        for patch in (
            mock.patch.object(host, "COMPANION", self.project),
            mock.patch.object(host.subprocess, "check_output", return_value=str(self.canonical / ".git")),
            mock.patch.dict(os.environ, {
                "FAKE_CALLS": str(self.calls),
                "PATH": str(self.engine.parent) + os.pathsep + os.environ["PATH"],
            }),
        ):
            patch.start()
            self.addCleanup(patch.stop)

    def invoke(self, *args: str) -> int:
        return host.companion_main([*args, "--engine", str(self.engine)])

    def read_calls(self) -> list[dict]:
        return [json.loads(line) for line in self.calls.read_text(encoding="utf-8").splitlines()]

    def test_build_uses_locked_bundled_packages_without_launching_or_retail_inputs(self) -> None:
        self.assertEqual(0, self.invoke("build"))
        calls = self.read_calls()
        self.assertEqual(["dotnet", "dotnet"], [call["tool"] for call in calls])
        restore, build = (call["args"] for call in calls)
        self.assertEqual(str(self.engine.parent / "GodotSharp/Tools/nupkgs"),
                         restore[restore.index("--source") + 1])
        self.assertIn("--locked-mode", restore)
        self.assertIn("--no-restore", build)
        for call in calls:
            for key in ("tmp", "data", "cache"):
                self.assertTrue(Path(call[key]).is_relative_to(self.canonical / "local-data/companion"))
            self.assertFalse(Path(call["tmp"]).exists())

    def test_run_keeps_exit_code_and_allocates_distinct_log_owners(self) -> None:
        with mock.patch.dict(os.environ, {"FAKE_EXIT": "17"}):
            self.assertEqual(17, self.invoke("run", "--no-build"))
            self.assertEqual(17, self.invoke("run", "--no-build"))
        calls = self.read_calls()
        self.assertEqual(["godot-mono", "godot-mono"], [call["tool"] for call in calls])
        logs = [Path(call["args"][call["args"].index("--log-file") + 1]) for call in calls]
        self.assertNotEqual(logs[0], logs[1])
        self.assertTrue(all(log.parent.is_dir() for log in logs))

    def test_wrong_engine_stops_before_build_or_launch(self) -> None:
        with mock.patch.dict(os.environ, {"FAKE_VERSION": "4.7.1.stable.mono.official.old"}):
            self.assertEqual(2, self.invoke("build"))
        self.assertFalse(self.calls.exists())


    def test_timeout_prints_captured_diagnostics_and_keeps_failure_status(self) -> None:
        error = subprocess.TimeoutExpired([str(self.engine), "--version"], 30,
                                          output=b"engine partial output", stderr=b"engine diagnostic")
        output = io.StringIO()
        with mock.patch.object(host, "run_process", side_effect=error), contextlib.redirect_stderr(output):
            self.assertEqual(124, self.invoke("run", "--no-build"))
        self.assertIn("engine partial output\n", output.getvalue())
        self.assertIn("engine diagnostic\n", output.getvalue())
        self.assertIn("timed out after 30s", output.getvalue())
        self.assertNotIn("b'engine", output.getvalue())


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux process-group launcher")
class OwnedProcessTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="godot-process-tests-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.processes = []
        real_popen = subprocess.Popen
        self.popen_type = real_popen

        def start(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            self.processes.append(process)
            return process

        patch = mock.patch.object(host.subprocess, "Popen", side_effect=start)
        patch.start()
        self.addCleanup(patch.stop)
        self.addCleanup(self.close_pipes)

    def close_pipes(self) -> None:
        for process in self.processes:
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()

    def run_script(self, script: str, timeout: float = 0.25):
        return host.run_process(["/bin/sh", "-c", script], cwd=self.root,
                                env=dict(os.environ), timeout=timeout, capture=True)

    def test_timeout_retains_output_written_during_shutdown(self) -> None:
        script = (
            "trap 'printf shutdown-out; printf shutdown-err >&2; exit 0' TERM; "
            "printf started-out; printf started-err >&2; "
            "while :; do sleep 1; done"
        )
        with self.assertRaises(subprocess.TimeoutExpired) as failure:
            self.run_script(script)
        error = failure.exception
        self.assertEqual(0.25, error.timeout)
        self.assertIn(b"started-out", error.output)
        self.assertIn(b"shutdown-out", error.output)
        self.assertIn(b"started-err", error.stderr)
        self.assertIn(b"shutdown-err", error.stderr)
        self.assertIsNotNone(self.processes[0].returncode)

    def test_timeout_closes_both_capture_pipes(self) -> None:
        with self.assertRaises(subprocess.TimeoutExpired):
            self.run_script("while :; do sleep 1; done")
        process = self.processes[0]
        self.assertTrue(process.stdout.closed)
        self.assertTrue(process.stderr.closed)
        self.assertIsNotNone(process.returncode)

    def test_nonzero_exit_keeps_both_streams_and_status(self) -> None:
        with self.assertRaises(subprocess.CalledProcessError) as failure:
            self.run_script("printf normal-out; printf normal-err >&2; exit 17", timeout=3)
        self.assertEqual(17, failure.exception.returncode)
        self.assertEqual("normal-out", failure.exception.stdout)
        self.assertEqual("normal-err", failure.exception.stderr)
        self.assertTrue(self.processes[0].stdout.closed)
        self.assertTrue(self.processes[0].stderr.closed)



    def test_interruption_closes_capture_pipes_after_stopping_the_group(self) -> None:
        with mock.patch.object(self.popen_type, "communicate", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_script("sleep 30")
        process = self.processes[0]
        self.assertIsNotNone(process.returncode)
        self.assertTrue(process.stdout.closed)
        self.assertTrue(process.stderr.closed)

    def test_output_drain_is_bounded_and_preserves_the_original_timeout(self) -> None:
        original = self.popen_type.communicate
        calls = []

        def simulate_held_pipe(process, *args, **kwargs):
            calls.append(kwargs.get("timeout"))
            if len(calls) == 2:
                raise subprocess.TimeoutExpired(process.args, kwargs["timeout"],
                                                 output=b"retained-tail", stderr=b"retained-error")
            return original(process, *args, **kwargs)

        with mock.patch.object(self.popen_type, "communicate", simulate_held_pipe):
            with self.assertRaises(subprocess.TimeoutExpired) as failure:
                self.run_script("printf started; sleep 30")
        self.assertEqual([0.25, 1.0], calls)
        self.assertEqual(0.25, failure.exception.timeout)
        self.assertEqual(b"retained-tail", failure.exception.output)
        self.assertEqual(b"retained-error", failure.exception.stderr)
        self.assertIn("drain exceeded", " ".join(failure.exception.__notes__))
        self.assertTrue(self.processes[0].stdout.closed)
        self.assertTrue(self.processes[0].stderr.closed)

    def test_invalid_final_text_does_not_replace_the_timeout_exception(self) -> None:
        with self.assertRaises(subprocess.TimeoutExpired) as failure:
            self.run_script(r"printf '\377'; sleep 30")
        self.assertEqual(b"\xff", failure.exception.output)
        self.assertEqual(0.25, failure.exception.timeout)
        self.assertTrue(self.processes[0].stdout.closed)
        self.assertTrue(self.processes[0].stderr.closed)

if __name__ == "__main__":
    unittest.main()
