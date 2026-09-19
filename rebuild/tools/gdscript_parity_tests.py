#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Desktop isolation and fail-closed completion for the migration gate."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import gdscript_parity as gate


class ParityGateTests(unittest.TestCase):
    def setUp(self) -> None:
        parent = gate.ROOT / "local-data/test-runs"
        parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="gdscript-launcher-", dir=parent)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.calls = []
        self.version = gate.STANDARD_VERSION
        self.complete = True
        self.script_error = False
        self.finished_groups = ["arithmetic", "euler", "rng", "wide", "binary"]

    def process(self, command, *, cwd, env, timeout, capture):
        self.calls.append((command, env.copy()))
        if "--version" in command:
            return subprocess.CompletedProcess(command, 0, self.version + "\n", "")
        if "--script" in command and self.complete:
            is_model = "res://Tests/pause_model_checks.gd" in command
            Path(command[-1]).write_text(json.dumps({"schema": 1, "failure_count": 0,
                "counts": {"nativeBasis": 31}, "completed": ["pause_model"] if is_model else self.finished_groups}))
        return subprocess.CompletedProcess(command, 0, "", "SCRIPT ERROR: aborted check" if self.script_error else "")

    def invoke(self, *args):
        with patch.object(gate, "ROOT", self.root), \
             patch.object(gate.shutil, "which", side_effect=lambda name: "/fake/" + name), \
             patch.object(gate, "run_process", side_effect=self.process), \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return gate.main(list(args))

    def test_headless_standard_engine_has_no_desktop_and_owns_profiles(self):
        with patch.dict(os.environ, {"DISPLAY": ":0", "WAYLAND_DISPLAY": "desktop", "XAUTHORITY": "/private/auth"}):
            self.assertEqual(0, self.invoke())
        engine = self.calls[-1][0]
        self.assertEqual("/fake/godot48", engine[0])
        self.assertIn("--headless", engine)
        self.assertIn("--script", engine)
        self.assertNotIn("--editor", engine)
        build = self.calls[1][0]
        self.assertTrue(Path(build[build.index("--artifacts-path") + 1]).is_relative_to(self.root / "local-data"))
        for _, env in self.calls:
            self.assertFalse({"DISPLAY", "WAYLAND_DISPLAY", "XAUTHORITY"} & env.keys())
            for name in ("TMPDIR", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME"):
                self.assertTrue(Path(env[name]).is_relative_to(self.root / "local-data"))

    def test_wrong_engine_identity_stops_before_oracle_build(self):
        self.version = "4.7.2.stable.official.ed1daf0bf"
        self.assertEqual(1, self.invoke())
        self.assertEqual(1, len(self.calls))

    def test_zero_engine_exit_without_completed_report_fails(self):
        self.complete = False
        self.assertEqual(1, self.invoke())

    def test_script_error_cannot_be_hidden_by_zero_exit_and_report(self):
        self.script_error = True
        self.assertEqual(1, self.invoke())

    def test_partially_aborted_group_cannot_pass(self):
        self.finished_groups.remove("wide")
        self.assertEqual(1, self.invoke())

    def test_output_outside_owned_local_data_is_rejected(self):
        self.assertEqual(1, self.invoke("--output-root", str(self.root / "shared")))
        self.assertEqual([], self.calls)
        self.assertFalse((self.root / "shared").exists())


if __name__ == "__main__":
    unittest.main()
