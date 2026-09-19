#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Focused fake-tool contracts for native companion pinning, isolation and packaging."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import companion_godot as host


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux development launcher")
class CompanionLauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        owner = host.canonical_root() / "local-data/companion"
        owner.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="gdscript-tool-tests-", dir=owner)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.canonical = self.root / "canonical"
        self.canonical.mkdir()
        self.project = self.root / "worktree/companion/OnslaughtToolkit.Godot"
        self.project.mkdir(parents=True)
        (self.project / "project.godot").write_text('config_version=5\n', encoding="utf-8")
        (self.project / "SaveLab.tscn").write_text('[gd_scene format=3]\n', encoding="utf-8")
        (self.project / "SaveLab.cs").write_text("retained reference only", encoding="utf-8")
        (self.project / "OnslaughtToolkit.Godot.csproj").write_text("retained reference only", encoding="utf-8")
        (self.project / "tests").mkdir()
        (self.project / "tests/test_save_lab.gd").write_text("extends SceneTree\n", encoding="utf-8")
        self.bridge = self.project.parent / "OnslaughtToolkit.FileBridge/OnslaughtToolkit.FileBridge.csproj"
        self.bridge.parent.mkdir()
        self.bridge.write_text("fake project", encoding="utf-8")
        self.race_project = self.bridge.with_name("OnslaughtToolkit.FileBridge.TransactionTests.csproj")
        self.race_project.write_text("fake test-only project", encoding="utf-8")
        self.bridge_tests = self.root / "test_file_bridge.py"
        self.fixture = self.root / "original-fixture.bin"
        self.fixture.write_bytes(host.FIXTURE.read_bytes())
        self.calls = self.root / "calls.jsonl"
        self.engine = self.root / "installed/toolchain/godot-4.8-dev6-standard/Godot_v4.8-dev6_linux.x86_64"
        self.engine.parent.mkdir(parents=True)
        self.dotnet = self.root / "bin/dotnet"
        self.dotnet.parent.mkdir()
        fake = (
            f"#!{sys.executable}\n"
            "import json, os, pathlib, sys\n"
            "tool = pathlib.Path(sys.argv[0]).name\n"
            "if '--version' in sys.argv:\n"
            "    print(os.environ.get('FAKE_VERSION', '4.8.dev6.official.8898c2b3d') if tool != 'dotnet' else '8.0.424')\n"
            "    raise SystemExit(0)\n"
            "with open(os.environ['FAKE_CALLS'], 'a') as output:\n"
            "    output.write(json.dumps({'tool': tool, 'args': sys.argv[1:], 'cwd': os.getcwd(),\n"
            "        'tmp': os.environ['TMPDIR'], 'data': os.environ['XDG_DATA_HOME'],\n"
            "        'config': os.environ['XDG_CONFIG_HOME'], 'cache': os.environ['XDG_CACHE_HOME'],\n"
            "        'home': os.environ.get('HOME'), 'bridge': os.environ.get('ONSLAUGHT_FILE_BRIDGE')}) + '\\n')\n"
            "if tool == 'dotnet' and 'publish' in sys.argv:\n"
            "    target = pathlib.Path(sys.argv[sys.argv.index('--output') + 1])\n"
            "    rid = sys.argv[sys.argv.index('--runtime') + 1]\n"
            "    assembly = pathlib.Path(sys.argv[sys.argv.index('publish') + 1]).stem\n"
            "    name = assembly + ('.exe' if rid == 'win-x64' else '')\n"
            "    (target / name).write_text('fake bridge')\n"
            "    (target / name).chmod(0o700)\n"
            "    options = {'includedFrameworks': [{'name': 'Microsoft.NETCore.App', 'version': '8.0.30'}]}\n"
            "    if os.environ.get('FAKE_FRAMEWORK_DEPENDENT'):\n"
            "        options = {'framework': {'name': 'Microsoft.NETCore.App', 'version': '8.0.30'}}\n"
            "    (target / (assembly + '.runtimeconfig.json')).write_text(json.dumps({'runtimeOptions': options}))\n"
            "    (target / 'libcoreclr.so').write_text('fake runtime')\n"
            "    assets = pathlib.Path(next(arg.split('=', 1)[1] for arg in sys.argv if arg.startswith('-p:BaseIntermediateOutputPath=')))\n"
            "    assets.mkdir(parents=True, exist_ok=True)\n"
            "    (assets / 'project.assets.json').write_text(json.dumps({'packageFolders': {os.environ['FAKE_NUGET']: {}}}))\n"
            "if any(arg.endswith('/license_metadata.gd') for arg in sys.argv):\n"
            "    print(json.dumps({'license': 'Godot MIT license', 'components': [{'name': 'component'}], 'licenses': {'MIT': 'notice'}}))\n"
            "if '--import' in sys.argv:\n"
            "    target = pathlib.Path(sys.argv[sys.argv.index('--path') + 1]) / '.godot'\n"
            "    target.mkdir(exist_ok=True)\n"
            "    (target / 'fake-import').touch()\n"
            "    if os.environ.get('FAKE_PARSE_ERROR'): print('SCRIPT ERROR: Parse Error: broken source')\n"
            "if '--export-release' in sys.argv:\n"
            "    target = pathlib.Path(sys.argv[sys.argv.index('--export-release') + 2])\n"
            "    target.write_text('fake native executable')\n"
            "    target.with_suffix('.pck').write_text('fake packed native resources')\n"
            "if any(arg.startswith('--fixture=') for arg in sys.argv):\n"
            "    raise SystemExit(int(os.environ.get('FAKE_NATIVE_EXIT', '0')))\n"
            "if tool == 'test_file_bridge.py':\n"
            "    raise SystemExit(int(os.environ.get('FAKE_BRIDGE_TEST_EXIT', '0')))\n"
            "raise SystemExit(int(os.environ.get('FAKE_EXIT', '0')))\n"
        )
        for executable in (self.engine, self.dotnet, self.bridge_tests):
            executable.write_text(fake, encoding="utf-8")
            executable.chmod(0o700)
        packages = self.root / "packages"
        for runtime in ("linux-x64", "win-x64"):
            package = packages / f"microsoft.netcore.app.runtime.{runtime}/8.0.30"
            package.mkdir(parents=True)
            (package / "LICENSE.TXT").write_text(".NET license", encoding="utf-8")
            (package / "THIRD-PARTY-NOTICES.TXT").write_text(".NET notices", encoding="utf-8")
        self.pins = json.loads((host.COMPANION / "toolchain.json").read_text(encoding="utf-8"))
        self.pins["engine"]["executableSha256"] = host.sha256(self.engine)
        self.templates = self.root / "installed" / self.pins["templates"]["installDirectory"]
        self.templates.mkdir(parents=True)
        for name in self.pins["templates"]["fileSha256"]:
            content = b"4.8.dev6\n" if name == "version.txt" else name.encode("utf-8")
            (self.templates / name).write_bytes(content)
            self.pins["templates"]["fileSha256"][name] = hashlib.sha256(content).hexdigest()
        self.lock = self.root / "shared-lock.json"
        entries = []
        for name, install in (("engine", self.engine.parent), ("templates", self.templates)):
            pin = self.pins[name]
            entry = {"id": pin["archiveId"], "version": pin["version"], "file": pin["file"],
                     "installDirectory": pin["installDirectory"], "digests": {"sha256": pin["archiveSha256"]}}
            entries.append(entry)
            (install / ".game-pipeline-source.json").write_text(json.dumps({
                "archiveId": entry["id"], "archiveVersion": entry["version"],
                "archiveFile": entry["file"], "archiveDigests": entry["digests"],
            }), encoding="utf-8")
        self.lock.write_text(json.dumps({
            "paths": {"dataRoot": str(self.root / "installed")}, "archives": entries,
            "managedTools": [{"id": "dotnetSdk8", "exactVersion": "8.0.424"}],
        }), encoding="utf-8")
        (self.project / "toolchain.json").write_text(json.dumps(self.pins), encoding="utf-8")
        for patch in (
            mock.patch.object(host, "COMPANION", self.project),
            mock.patch.object(host, "BRIDGE_PROJECT", self.bridge),
            mock.patch.object(host, "RACE_PROJECT", self.race_project),
            mock.patch.object(host, "BRIDGE_TESTS", self.bridge_tests),
            mock.patch.object(host, "FIXTURE", self.fixture),
            mock.patch.object(host, "canonical_root", return_value=self.canonical),
            mock.patch.dict(os.environ, {"FAKE_CALLS": str(self.calls), "FAKE_NUGET": str(packages),
                                         "PATH": str(self.dotnet.parent) + os.pathsep + os.environ["PATH"]}),
        ):
            patch.start()
            self.addCleanup(patch.stop)

    def invoke(self, *arguments: str) -> int:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return host.companion_main([*arguments, "--engine", str(self.engine), "--shared-lock", str(self.lock)])

    def read_calls(self) -> list[dict]:
        if not self.calls.exists():
            return []
        return [json.loads(line) for line in self.calls.read_text(encoding="utf-8").splitlines()]

    def test_build_uses_standard_engine_and_only_explicit_self_contained_bridge(self) -> None:
        self.assertEqual(0, self.invoke("build"))
        calls = self.read_calls()
        self.assertEqual([self.engine.name, self.engine.name, "dotnet"], [call["tool"] for call in calls])
        publish = calls[-1]["args"]
        self.assertEqual(str(self.bridge), publish[publish.index("publish") + 1])
        self.assertEqual("true", publish[publish.index("--self-contained") + 1])
        self.assertEqual("linux-x64", publish[publish.index("--runtime") + 1])
        self.assertEqual(str(self.bridge.parent), calls[-1]["cwd"])
        for call in calls:
            self.assertNotIn("--build-solutions", call["args"])
            self.assertNotIn("GodotSharp", str(call))
        staged = Path(calls[0]["args"][calls[0]["args"].index("--path") + 1])
        self.assertTrue((staged / ".godot/fake-import").is_file())
        self.assertFalse((staged / "SaveLab.cs").exists())
        self.assertFalse((self.project / ".godot/fake-import").exists())
        pointer = self.project / ".godot/companion_bridge_path.txt"
        self.assertTrue(Path(pointer.read_text().strip()).is_file())

    def test_invocations_keep_all_profiles_imports_logs_and_builds_in_distinct_output(self) -> None:
        for _ in range(2):
            self.assertEqual(0, self.invoke("build"))
        imports = [call for call in self.read_calls() if "--import" in call["args"]]
        self.assertEqual(2, len(imports))
        self.assertNotEqual(imports[0]["tmp"], imports[1]["tmp"])
        owner = self.canonical / "local-data/companion"
        for call in self.read_calls():
            for key in ("tmp", "data", "cache", "config"):
                self.assertTrue(Path(call[key]).is_relative_to(owner))
            self.assertEqual(os.environ.get("HOME"), call["home"])
        self.assertTrue(all(path.name.startswith("gdscript-build-") for path in owner.iterdir()))

    def test_changed_shared_archive_pin_refuses_before_engine_or_build(self) -> None:
        lock = host.read_json(self.lock)
        lock["archives"][0]["digests"]["sha256"] = "0" * 64
        self.lock.write_text(json.dumps(lock), encoding="utf-8")
        self.assertEqual(2, self.invoke("build"))
        self.assertEqual([], self.read_calls())

    def test_changed_installed_engine_refuses_before_engine_or_build(self) -> None:
        self.engine.write_text(self.engine.read_text() + "\n# changed bytes\n", encoding="utf-8")
        self.assertEqual(2, self.invoke("build"))
        self.assertEqual([], self.read_calls())

    def test_wrong_version_refuses_before_import_or_bridge_build(self) -> None:
        with mock.patch.dict(os.environ, {"FAKE_VERSION": "4.8.dev6.mono.official.8898c2b3d"}):
            self.assertEqual(2, self.invoke("build"))
        self.assertEqual([], self.read_calls())

    def test_changed_export_template_refuses_before_import_or_bridge_build(self) -> None:
        (self.templates / "windows_release_x86_64.exe").write_bytes(b"wrong")
        self.assertEqual(2, self.invoke("export", "--platform", "windows"))
        self.assertEqual([], self.read_calls())

    def test_zero_exit_parse_error_is_not_a_successful_build(self) -> None:
        with mock.patch.dict(os.environ, {"FAKE_PARSE_ERROR": "1"}):
            self.assertEqual(2, self.invoke("build"))
        self.assertEqual([self.engine.name], [call["tool"] for call in self.read_calls()])

    def test_framework_dependent_helper_is_refused(self) -> None:
        with mock.patch.dict(os.environ, {"FAKE_FRAMEWORK_DEPENDENT": "1"}):
            self.assertEqual(2, self.invoke("build"))
        self.assertFalse((self.project / ".godot/companion_bridge_path.txt").exists())

    def test_test_runner_receives_owned_fixture_copy_and_private_bridge(self) -> None:
        before = self.fixture.read_bytes()
        self.assertEqual(0, self.invoke("test"))
        calls = self.read_calls()
        run = next(call for call in calls if any(arg.startswith("--fixture=") for arg in call["args"]))
        self.assertIn("--headless", run["args"])
        self.assertIn("res://tests/test_save_lab.gd", run["args"])
        selected = Path(next(arg.split("=", 1)[1] for arg in run["args"] if arg.startswith("--fixture=")))
        self.assertNotEqual(selected, self.fixture)
        self.assertEqual(before, selected.read_bytes())
        self.assertEqual(before, self.fixture.read_bytes())
        self.assertTrue(Path(run["bridge"]).is_file())
        self.assertTrue(next(arg for arg in run["args"] if arg.startswith("--output-dir=")))
        safety = calls[-1]
        self.assertEqual("test_file_bridge.py", safety["tool"])
        self.assertIn("--race-harness", safety["args"])
        harness = Path(safety["args"][safety["args"].index("--race-harness") + 1])
        self.assertTrue(harness.is_file())
        self.assertTrue(harness.is_relative_to(self.canonical / "local-data/companion"))
        self.assertEqual(str(run["bridge"]), safety["args"][safety["args"].index("--bridge") + 1])

    def test_native_test_failure_is_preserved_before_safety_harness_runs(self) -> None:
        with mock.patch.dict(os.environ, {"FAKE_NATIVE_EXIT": "17"}):
            self.assertEqual(17, self.invoke("test"))
        self.assertFalse(any(call["tool"] == "test_file_bridge.py" for call in self.read_calls()))

    def test_safety_harness_failure_fails_the_normal_test_route(self) -> None:
        with mock.patch.dict(os.environ, {"FAKE_BRIDGE_TEST_EXIT": "23"}):
            self.assertEqual(23, self.invoke("test"))

    def test_cross_exports_bundle_separate_self_contained_helpers_and_native_packs(self) -> None:
        self.assertEqual(0, self.invoke("export", "--platform", "both"))
        calls = self.read_calls()
        exports = [call for call in calls if "--export-release" in call["args"]]
        self.assertEqual(2, len(exports))
        packages = []
        for export, platform, extension in zip(exports, ("linux", "windows"), ("", ".exe")):
            target = Path(export["args"][export["args"].index("--export-release") + 2])
            package = target.parent
            packages.append(package)
            self.assertTrue((package / ("file-bridge/OnslaughtToolkit.FileBridge" + extension)).is_file())
            self.assertFalse(list(package.rglob("*TransactionTests*")))
            self.assertTrue(target.with_suffix(".pck").is_file())
            self.assertEqual(host.MIT_LICENSE.read_bytes(), (package / "LICENSE.txt").read_bytes())
            self.assertTrue((package / "GODOT-LICENSE.txt").is_file())
            self.assertTrue((package / "GODOT-THIRD-PARTY-NOTICES.json").is_file())
            self.assertTrue((package / "file-bridge/DOTNET-LICENSE.txt").is_file())
            self.assertTrue((package / "file-bridge/DOTNET-THIRD-PARTY-NOTICES.txt").is_file())
            self.assertIn("no installed .NET runtime is needed", (package / "README.txt").read_text())
            inventory = host.read_json(package / "package-sha256.json")
            self.assertEqual(platform, inventory["platform"])
            self.assertEqual("8.0.30", inventory["fileBridgeRuntime"])
        self.assertNotEqual(packages[0], packages[1])
        self.assertEqual(["linux-x64", "win-x64"],
                         [call["args"][call["args"].index("--runtime") + 1]
                          for call in calls if call["tool"] == "dotnet"])


if __name__ == "__main__":
    unittest.main()
