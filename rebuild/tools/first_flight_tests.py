#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Linux launcher regressions using only short-lived fake tools."""

from __future__ import annotations

import json
import io
import os
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

import first_flight as launcher

COMPLETED_SMOKE = {
    "schemaVersion": "onslaught-first-flight-smoke.v17",
    "exitReason": "smoke-complete",
    "finalFrontendScreen": "MainMenu",
    "coldClickToStart": True,
    "coldMainMenu": True,
    "coldGameplay": True,
    "retryRequested": True,
    "retryGameplayActivated": True,
    "retrySessionFresh": True,
    "returnToMainMenuRequested": True,
    "returnedToMainMenu": True,
    "worldReleasedAtMainMenu": True,
}


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux process-group launcher")
class LauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="first-flight-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.canonical = self.root / "canonical"
        self.checkout = self.root / "worktree"
        (self.canonical / "local-lab").mkdir(parents=True)
        (self.checkout / launcher.PROJECT).mkdir(parents=True)
        (self.checkout / launcher.PROJECT / "OnslaughtRebuild.Godot.csproj").touch()
        (self.checkout / "rebuild/tools").mkdir()
        self.game = self.root / "Retail Installation"
        for name in ("BEA.exe", launcher.materializer.LEVEL_ARCHIVE,
                     launcher.materializer.BASE_ARCHIVE, launcher.materializer.SOUND_BANK):
            path = self.game / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        self.calls = self.root / "calls.jsonl"
        fake = (
            f"#!{sys.executable}\n"
            "import json, os, pathlib, sys\n"
            "if '--version' in sys.argv:\n"
            "    print(os.environ.get('FAKE_ENGINE_VERSION', " + repr(launcher.ENGINE_VERSION) + "))\n"
            "    raise SystemExit(0)\n"
            "with open(os.environ['FAKE_CALLS'], 'a') as output:\n"
            "    output.write(json.dumps({'tool': pathlib.Path(sys.argv[0]).name, "
            "'args': sys.argv[1:], 'tmp': os.environ['TMPDIR'], "
            "'data': os.environ['XDG_DATA_HOME'], 'cache': os.environ['XDG_CACHE_HOME'], "
            "'unrelated': os.environ['FAKE_UNRELATED']}) + '\\n')\n"
            "if pathlib.Path(sys.argv[0]).name == 'godot-mono':\n"
            "    report = os.environ.get('FAKE_SMOKE_REPORT')\n"
            "    for arg in sys.argv:\n"
            "        if arg.startswith('--report=') and report is not None:\n"
            "            pathlib.Path(arg.split('=', 1)[1]).write_text(report)\n"
            "    raise SystemExit(int(os.environ.get('FAKE_ENGINE_EXIT', '0')))\n"
        )
        self.engine = self.root / "engine/godot-mono"
        self.engine.parent.mkdir()
        self.engine.write_text(fake, encoding="utf-8")
        self.engine.chmod(0o700)
        packages = self.engine.parent / "GodotSharp/Tools/nupkgs"
        packages.mkdir(parents=True)
        (packages / "Godot.NET.Sdk.4.7.2.nupkg").touch()
        dotnet = self.engine.parent / "dotnet"
        dotnet.write_text(fake, encoding="utf-8")
        dotnet.chmod(0o700)
        (self.checkout / "rebuild/tools/materialize_retail_assets.py").write_text(fake, encoding="utf-8")
        patches = [
            mock.patch.object(launcher.materializer, "ROOT", self.checkout),
            mock.patch.object(launcher.materializer, "_canonical_repository_root", return_value=self.canonical),
            mock.patch.object(launcher.materializer, "_outputs_ready", return_value=False),
            mock.patch.dict(os.environ, {"FAKE_CALLS": str(self.calls),
                                        "FAKE_UNRELATED": "preserved",
                                        "ONSLAUGHT_STARTUP_MEDIA": "",
                                        "PATH": str(self.engine.parent) + os.pathsep + os.environ["PATH"]}),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def invoke(self, mode: str, *args: str) -> int:
        return launcher.main([mode, "--engine", str(self.engine), "--game-root", str(self.game), *args])

    def read_calls(self) -> list[dict]:
        return [json.loads(line) for line in self.calls.read_text(encoding="utf-8").splitlines()]

    def test_run_uses_selected_game_canonical_media_local_packages_and_user_arguments(self) -> None:
        self.assertEqual(0, self.invoke("run", "--", "--skipfmv"))
        calls = self.read_calls()
        self.assertEqual(["materialize_retail_assets.py", "materialize_retail_assets.py",
                          "dotnet", "dotnet", "godot-mono"], [call["tool"] for call in calls])
        assets, media, restore, build, engine = (call["args"] for call in calls)
        self.assertIn("--host-default-work-root", assets)
        self.assertEqual(str(self.game), assets[assets.index("--game-root") + 1])
        self.assertIn("--startup-media", media)
        self.assertNotIn("--host-default-work-root", media)
        canonical_media = self.canonical / "local-lab/startup-media"
        self.assertEqual(str(canonical_media), media[media.index("--startup-media-root") + 1])
        self.assertEqual(str(self.engine.parent / "GodotSharp/Tools/nupkgs"), restore[restore.index("--source") + 1])
        self.assertIn("--locked-mode", restore)
        self.assertIn("--no-restore", build)
        self.assertEqual([f"--startup-media={canonical_media}", "--skipfmv"], engine[engine.index("--") + 1:])
        for call in calls:
            self.assertTrue(Path(call["tmp"]).is_relative_to(self.canonical / "local-data"))
            self.assertFalse(Path(call["tmp"]).exists())
            self.assertTrue(Path(call["data"]).is_relative_to(self.canonical / "local-data"))
            self.assertTrue(Path(call["cache"]).is_relative_to(self.canonical / "local-data"))
            self.assertEqual("preserved", call["unrelated"])

    def test_verified_asset_cache_skips_regeneration_and_no_build_skips_dotnet(self) -> None:
        with mock.patch.object(launcher.materializer, "_outputs_ready", return_value=True):
            self.assertEqual(0, self.invoke("run", "--no-build"))
        calls = self.read_calls()
        self.assertEqual(["materialize_retail_assets.py", "godot-mono"], [call["tool"] for call in calls])
        self.assertIn("--startup-media", calls[0]["args"])

    def test_build_has_no_startup_media_or_runtime(self) -> None:
        self.assertEqual(0, self.invoke("build"))
        self.assertEqual(["materialize_retail_assets.py", "dotnet", "dotnet"],
                         [call["tool"] for call in self.read_calls()])

    def test_no_prepare_launch_skips_validation_and_materializer_processes(self) -> None:
        with mock.patch.object(launcher.materializer, "_outputs_ready", side_effect=AssertionError("must not validate")), \
             mock.patch.object(launcher.materializer, "_resolve_game_root", side_effect=AssertionError("must not discover retail inputs")):
            self.assertEqual(0, self.invoke("run", "--no-build", "--no-prepare"))
        calls = self.read_calls()
        self.assertEqual(["godot-mono"], [call["tool"] for call in calls])
        self.assertIn(f"--startup-media={self.canonical / 'local-lab/startup-media'}", calls[0]["args"])

    def test_no_prepare_build_reuses_existing_assets(self) -> None:
        with mock.patch.object(launcher.materializer, "_outputs_ready", side_effect=AssertionError("must not validate")):
            self.assertEqual(0, self.invoke("build", "--no-prepare"))
        self.assertEqual(["dotnet", "dotnet"], [call["tool"] for call in self.read_calls()])

    def test_wrong_engine_version_stops_before_materialization(self) -> None:
        with mock.patch.dict(os.environ, {"FAKE_ENGINE_VERSION": "4.7.1.stable.mono.official.old"}):
            self.assertEqual(2, self.invoke("run"))
        self.assertFalse(self.calls.exists())

    def test_native_failure_exit_is_preserved(self) -> None:
        with mock.patch.dict(os.environ, {"FAKE_ENGINE_EXIT": "17"}):
            self.assertEqual(17, self.invoke("run", "--no-build"))

    def test_smoke_and_capture_receive_fresh_outputs_and_bounded_timeout(self) -> None:
        real_run = launcher.run_process
        with mock.patch.object(launcher, "run_process", wraps=real_run) as run, \
             mock.patch.dict(os.environ, {"FAKE_SMOKE_REPORT": json.dumps(COMPLETED_SMOKE)}):
            self.assertEqual(0, self.invoke("smoke", "--no-build"))
            self.assertEqual(75, run.call_args.kwargs["timeout"])
            self.assertEqual(0, self.invoke("capture", "--no-build", "--", "--capture-plan=mainmenu"))
            self.assertEqual(300, run.call_args.kwargs["timeout"])
        engine_calls = [call["args"] for call in self.read_calls() if call["tool"] == "godot-mono"]
        report = next(arg.removeprefix("--report=") for arg in engine_calls[0] if arg.startswith("--report="))
        capture = next(arg.removeprefix("--capture-dir=") for arg in engine_calls[1] if arg.startswith("--capture-dir="))
        self.assertNotEqual(Path(report).parent, Path(capture))
        self.assertTrue(Path(capture).is_relative_to(self.canonical / "local-data"))
        self.assertIn("--capture-plan=mainmenu", engine_calls[1])

    def test_zero_exit_without_smoke_completion_is_failure(self) -> None:
        invalid = [None, "{", "[]", "{}"]
        invalid.extend(json.dumps(COMPLETED_SMOKE | {key: value}) for key, value in (
            ("schemaVersion", "old"), ("exitReason", "window-closed"),
            ("finalFrontendScreen", "Gameplay"), ("retrySessionFresh", False),
            ("worldReleasedAtMainMenu", 1),
        ))
        for payload in invalid:
            with self.subTest(payload=payload), mock.patch.dict(os.environ):
                os.environ.pop("FAKE_SMOKE_REPORT", None)
                if payload is not None:
                    os.environ["FAKE_SMOKE_REPORT"] = payload
                self.assertEqual(2, self.invoke("smoke", "--no-build", "--no-prepare"))

    def test_native_smoke_failure_is_not_replaced_by_missing_report_error(self) -> None:
        with mock.patch.dict(os.environ, {"FAKE_ENGINE_EXIT": "17"}):
            self.assertEqual(17, self.invoke("smoke", "--no-build", "--no-prepare"))

    def test_captured_version_timeout_retains_diagnostics(self) -> None:
        error = subprocess.TimeoutExpired([str(self.engine), "--version"], 30,
                                          output=b"version stalled\n", stderr=b"detail\n")
        output = io.StringIO()
        with mock.patch.object(launcher, "run_process", side_effect=error), redirect_stderr(output):
            self.assertEqual(124, self.invoke("smoke", "--no-build", "--no-prepare"))
        self.assertIn("version stalled\n", output.getvalue())
        self.assertIn("detail\n", output.getvalue())

    def _descendant_command(self, *, exit_early: bool = False) -> tuple[list[str], Path]:
        pid_path = self.root / "descendant.pid"
        child = (
            "import os,pathlib,signal,time; "
            "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
            f"pathlib.Path({str(pid_path)!r}).write_text(str(os.getpid())); "
            "time.sleep(30)"
        )
        parent = (
            "import pathlib,subprocess,sys,time; "
            f"subprocess.Popen([sys.executable, '-c', {child!r}]); "
            f"p=pathlib.Path({str(pid_path)!r})\n"
            "while not p.exists(): time.sleep(0.01)\n"
            + ("raise SystemExit(19)\n" if exit_early else "time.sleep(30)\n")
        )
        return [sys.executable, "-c", parent], pid_path

    def assert_not_running(self, pid_path: Path) -> None:
        pid = int(pid_path.read_text(encoding="utf-8"))
        stat = Path(f"/proc/{pid}/stat")
        deadline = time.monotonic() + 1
        while time.monotonic() < deadline:
            try:
                state = stat.read_text().split(") ", 1)[1].split()[0]
            except FileNotFoundError:
                return
            # SIGKILL delivery is asynchronous; a dead orphan can await init's reap.
            if state == "Z":
                return
            time.sleep(0.01)
        self.fail(f"owned descendant {pid} still runs after process-group cleanup")

    def test_timeout_stops_term_resistant_descendant(self) -> None:
        command, pid = self._descendant_command()
        with self.assertRaises(subprocess.TimeoutExpired):
            launcher.run_process(command, cwd=self.root, env=dict(os.environ), timeout=1)
        self.assert_not_running(pid)

    def test_failure_stops_descendant_after_its_parent_has_exited(self) -> None:
        command, pid = self._descendant_command(exit_early=True)
        with self.assertRaises(subprocess.CalledProcessError) as failure:
            launcher.run_process(command, cwd=self.root, env=dict(os.environ), timeout=3)
        self.assertEqual(19, failure.exception.returncode)
        self.assert_not_running(pid)

    def test_interruption_stops_owned_process_group(self) -> None:
        command, pid = self._descendant_command()
        original_communicate = subprocess.Popen.communicate

        def interrupt_after_start(process, *args, **kwargs):
            try:
                original_communicate(process, timeout=0.5)
            except subprocess.TimeoutExpired:
                raise KeyboardInterrupt

        with mock.patch.object(subprocess.Popen, "communicate", interrupt_after_start):
            with self.assertRaises(KeyboardInterrupt):
                launcher.run_process(command, cwd=self.root, env=dict(os.environ), timeout=3)
        self.assert_not_running(pid)


if __name__ == "__main__":
    unittest.main()
