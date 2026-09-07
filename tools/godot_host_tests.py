#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Companion launch routing with fake tools; no window or retail data is used."""
from __future__ import annotations

import json
import os
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


if __name__ == "__main__":
    unittest.main()
