#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Focused fake-tool checks for integrated Godot .NET routes and export boundaries."""
from __future__ import annotations

import contextlib
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
        temporary = tempfile.TemporaryDirectory(prefix="godot-dotnet-tool-tests-", dir=owner)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.canonical = self.root / "canonical"
        self.canonical.mkdir()
        self.source = self.root / "worktree"
        self.project = self.source / "companion/OnslaughtToolkit.Godot"
        self.project.mkdir(parents=True)
        for name, data in {
            "project.godot": "config_version=5\n", "SaveLab.tscn": "[gd_scene format=3]\n",
            "OnslaughtToolkit.Godot.csproj": "integrated project", "global.json": '{"sdk":{"version":"8.0.424"}}',
            "OnslaughtToolkit.Godot.sln": "single-project Godot solution",
            "packages.lock.json": "{}", "SaveLab.cs": "retained legacy source, not active",
            "SaveLab.cs.uid": "uid://retained-reference",
            "io/ProtectedSaveFiles.cs": "integrated safety adapter", "tests/test_save_lab.gd": "extends SceneTree\n",
        }.items():
            path = self.project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data, encoding="utf-8")
        for name in host.SAFETY_SOURCES:
            path = self.source / "OnslaughtCareerEditor.AppCore" / name
            path.parent.mkdir(exist_ok=True)
            path.write_text("// exact safety snapshot " + name, encoding="utf-8")
        self.race = self.source / "companion/OnslaughtToolkit.FileBridge/OnslaughtToolkit.FileBridge.TransactionTests.csproj"
        self.race.parent.mkdir()
        self.race.write_text("test-only project", encoding="utf-8")
        self.fixture = self.root / "fixture.bin"
        self.fixture.write_bytes(host.FIXTURE.read_bytes())
        self.pins = host.read_json(host.COMPANION / "toolchain.json")
        self.engine = self.root / "installed" / self.pins["engine"]["installDirectory"] / self.pins["engine"]["executable"]
        self.engine.parent.mkdir(parents=True)
        self.dotnet = self.root / "bin/dotnet"
        self.dotnet.parent.mkdir()
        self.calls = self.root / "calls.jsonl"
        fake = (
            f"#!{sys.executable}\n"
            "import json, os, pathlib, sys\n"
            "tool=pathlib.Path(sys.argv[0]).name\n"
            "if '--version' in sys.argv:\n"
            " print('8.0.424' if tool=='dotnet' else os.environ.get('FAKE_VERSION','4.8.dev6.mono.official.8898c2b3d')); raise SystemExit(0)\n"
            "with open(os.environ['FAKE_CALLS'],'a') as f: f.write(json.dumps({'tool':tool,'args':sys.argv[1:],'cwd':os.getcwd(),'tmp':os.environ['TMPDIR'],'data':os.environ['XDG_DATA_HOME'],'cache':os.environ['XDG_CACHE_HOME'],'config':os.environ['XDG_CONFIG_HOME'],'old_bridge':os.environ.get('ONSLAUGHT_FILE_BRIDGE')})+'\\n')\n"
            "if tool=='dotnet' and sys.argv[1] in ('restore','build'):\n"
            " project=pathlib.Path(sys.argv[2]).parent\n"
            " assets=project/'.godot/mono/temp/obj'; assets.mkdir(parents=True,exist_ok=True)\n"
            " (assets/'project.assets.json').write_text(json.dumps({'packageFolders':{os.environ['FAKE_NUGET']:{}}}))\n"
            " if sys.argv[1]=='build':\n"
            "  target=project/'.godot/mono/temp/bin/Debug'; target.mkdir(parents=True,exist_ok=True); (target/'OnslaughtToolkit.Godot.dll').write_text('integrated assembly')\n"
            "if tool=='dotnet' and sys.argv[1]=='publish':\n"
            " target=pathlib.Path(sys.argv[sys.argv.index('--output')+1]); target.mkdir(parents=True,exist_ok=True)\n"
            " harness=target/'OnslaughtToolkit.FileBridge.TransactionTests'\n"
            f" harness.write_text('#!{sys.executable}\\nimport json,os\\nprint(json.dumps({{\"ok\":not bool(os.environ.get(\"FAKE_RACE_FAILURE\")),\"passed\":list(range(6))}}))\\n'); harness.chmod(0o700)\n"
            "if any(arg.endswith('/license_metadata.gd') for arg in sys.argv): print(json.dumps({'license':'Godot MIT','components':[{'name':'component'}],'licenses':{'MIT':'notice'}}))\n"
            "if '--import' in sys.argv and os.environ.get('FAKE_PARSE_ERROR'): print('SCRIPT ERROR: Parse Error: broken source')\n"
            "if '--export-release' in sys.argv:\n"
            " target=pathlib.Path(sys.argv[sys.argv.index('--export-release')+2]); target.write_text('native exe'); target.with_suffix('.pck').write_text('native resources')\n"
            " data=target.parent/'data_OnslaughtToolkit.Godot'; data.mkdir()\n"
            " for name in ['OnslaughtToolkit.Godot.dll','GodotSharp.dll','libcoreclr.so']: (data/name).write_text('integrated runtime')\n"
            " config={'includedFrameworks':[{'name':'Microsoft.NETCore.App','version':'8.0.30'}]}\n"
            " if os.environ.get('FAKE_FRAMEWORK_DEPENDENT'): config={'framework':{'name':'Microsoft.NETCore.App','version':'8.0.30'}}\n"
            " (data/'OnslaughtToolkit.Godot.runtimeconfig.json').write_text(json.dumps({'runtimeOptions':config}))\n"
            " if os.environ.get('FAKE_HELPER_LEAK'): (target.parent/'file-bridge').mkdir()\n"
            "if any(arg.startswith('--fixture=') for arg in sys.argv): raise SystemExit(int(os.environ.get('FAKE_NATIVE_EXIT','0')))\n"
        )
        for executable in (self.engine, self.dotnet):
            executable.write_text(fake, encoding="utf-8")
            executable.chmod(0o700)
        sdk = self.engine.parent / self.pins["engine"]["sdkPackage"]
        sdk.parent.mkdir(parents=True)
        sdk.write_bytes(b"pinned local Godot SDK")
        self.pins["engine"]["executableSha256"] = host.sha256(self.engine)
        self.pins["engine"]["sdkPackageSha256"] = host.sha256(sdk)
        self.templates = self.root / "installed" / self.pins["templates"]["installDirectory"]
        self.templates.mkdir(parents=True)
        for name in self.pins["templates"]["fileSha256"]:
            target = self.templates / name
            target.write_text(self.pins["templateVersion"] if name=="version.txt" else name, encoding="utf-8")
            self.pins["templates"]["fileSha256"][name] = host.sha256(target)
        self.lock = self.root / "shared/toolchain.linux.lock.json"
        self.lock.parent.mkdir()
        helper = self.lock.parent / "scripts/linux_toolchain.py"
        helper.parent.mkdir()
        helper.write_text("print('{}')\n", encoding="utf-8")
        archives = []
        for name, install in (("engine", self.engine.parent), ("templates", self.templates)):
            pin = self.pins[name]
            entry = {"id":pin["archiveId"],"version":pin["version"],"file":pin["file"],"installDirectory":pin["installDirectory"],"digests":{"sha256":pin["archiveSha256"]}}
            archives.append(entry)
            (install / ".game-pipeline-source.json").write_text(json.dumps({"archiveId":entry["id"],"archiveVersion":entry["version"],"archiveFile":entry["file"],"archiveDigests":entry["digests"],"payloadSha256":pin.get("payloadSha256")}),encoding="utf-8")
        self.lock.write_text(json.dumps({"paths":{"dataRoot":str(self.root/"installed")},"archives":archives,"managedTools":[{"id":"dotnetSdk8","exactVersion":"8.0.424"}]}),encoding="utf-8")
        (self.project / "toolchain.json").write_text(json.dumps(self.pins),encoding="utf-8")
        packages = self.root / "packages"
        for rid in ("linux-x64","win-x64"):
            package=packages/f"microsoft.netcore.app.runtime.{rid}/8.0.30"
            package.mkdir(parents=True)
            for name in ("LICENSE.TXT","THIRD-PARTY-NOTICES.TXT"):(package/name).write_text(name,encoding="utf-8")
        for patch in (mock.patch.object(host,"ROOT",self.source),mock.patch.object(host,"COMPANION",self.project),
                      mock.patch.object(host,"RACE_PROJECT",self.race),mock.patch.object(host,"FIXTURE",self.fixture),
                      mock.patch.object(host,"canonical_root",return_value=self.canonical),
                      mock.patch.dict(os.environ,{"FAKE_CALLS":str(self.calls),"FAKE_NUGET":str(packages),"ONSLAUGHT_FILE_BRIDGE":"must-not-be-used","PATH":str(self.dotnet.parent)+os.pathsep+os.environ["PATH"]})):
            patch.start();self.addCleanup(patch.stop)

    def invoke(self,*arguments:str)->int:
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            return host.companion_main([*arguments,"--engine",str(self.engine),"--shared-lock",str(self.lock)])

    def calls_read(self)->list[dict]:
        return [json.loads(line) for line in self.calls.read_text().splitlines()] if self.calls.exists() else []

    def test_build_uses_integrated_project_and_exact_safety_snapshots(self)->None:
        self.assertEqual(0,self.invoke("build"))
        calls=self.calls_read()
        self.assertEqual(["restore","build"],[call["args"][0] for call in calls if call["tool"]=="dotnet"])
        restore=next(call for call in calls if call["args"][0]=="restore")
        self.assertIn("--locked-mode",restore["args"])
        staged=Path(restore["args"][1]).parent
        self.assertTrue((staged/"io/ProtectedSaveFiles.cs").is_file())
        self.assertFalse((staged/"SaveLab.cs").exists())
        self.assertFalse((staged/"SaveLab.cs.uid").exists())
        for name in host.SAFETY_SOURCES:self.assertEqual((self.source/"OnslaughtCareerEditor.AppCore"/name).read_bytes(),(staged.parents[1]/"OnslaughtCareerEditor.AppCore"/name).read_bytes())
        self.assertFalse((self.project/".godot").exists())
        self.assertTrue(all(call["old_bridge"] is None for call in calls))
        self.assertFalse(any("FileBridge.csproj" in str(call) for call in calls))

    def test_each_invocation_isolates_imports_builds_profiles_and_logs(self)->None:
        self.assertEqual(0,self.invoke("check"));self.assertEqual(0,self.invoke("check"))
        imports=[call for call in self.calls_read() if "--import" in call["args"]]
        self.assertNotEqual(imports[0]["tmp"],imports[1]["tmp"])
        for call in self.calls_read():
            for key in ("tmp","data","cache","config"):self.assertTrue(Path(call[key]).is_relative_to(self.canonical/"local-data/companion"))

    def test_engine_bytes_pin_refuses_before_build(self)->None:
        self.engine.write_text(self.engine.read_text()+"\n# different bytes\n")
        self.assertEqual(2,self.invoke("build"));self.assertEqual([],self.calls_read())

    def test_sdk_bytes_pin_refuses_before_build(self)->None:
        (self.engine.parent/self.pins["engine"]["sdkPackage"]).write_text("different SDK")
        self.assertEqual(2,self.invoke("build"));self.assertEqual([],self.calls_read())

    def test_standard_engine_version_is_refused(self)->None:
        with mock.patch.dict(os.environ,{"FAKE_VERSION":"4.8.dev6.official.8898c2b3d"}):self.assertEqual(2,self.invoke("build"))
        self.assertEqual([],self.calls_read())

    def test_template_bytes_pin_refuses_export_before_build(self)->None:
        (self.templates/"windows_release_x86_64.exe").write_text("wrong")
        self.assertEqual(2,self.invoke("export","--platform","windows"));self.assertEqual([],self.calls_read())

    def test_zero_exit_godot_parse_error_fails_check(self)->None:
        with mock.patch.dict(os.environ,{"FAKE_PARSE_ERROR":"1"}):self.assertEqual(2,self.invoke("check"))

    def test_native_test_receives_owned_fixture_and_requires_six_races(self)->None:
        before=self.fixture.read_bytes();self.assertEqual(0,self.invoke("test"))
        calls=self.calls_read();native=next(call for call in calls if any(arg.startswith("--fixture=") for arg in call["args"]))
        copied=Path(next(arg.split("=",1)[1] for arg in native["args"] if arg.startswith("--fixture=")))
        self.assertNotEqual(copied,self.fixture);self.assertEqual(before,copied.read_bytes());self.assertEqual(before,self.fixture.read_bytes())
        self.assertTrue(any(call["args"][0]=="publish" and "TransactionTests" in str(call["args"]) for call in calls))
        with mock.patch.dict(os.environ,{"FAKE_RACE_FAILURE":"1"}):self.assertEqual(2,self.invoke("test"))

    def test_native_test_failure_stops_before_race_build(self)->None:
        with mock.patch.dict(os.environ,{"FAKE_NATIVE_EXIT":"17"}):self.assertEqual(17,self.invoke("test"))
        self.assertFalse(any(call["args"][0]=="publish" for call in self.calls_read()))

    def test_normal_dotnet_exports_bundle_runtime_not_helper_or_harness(self)->None:
        self.assertEqual(0,self.invoke("export","--platform","both"))
        exports=[call for call in self.calls_read() if "--export-release" in call["args"]]
        self.assertEqual(2,len(exports))
        for call in exports:
            package=Path(call["args"][call["args"].index("--export-release")+2]).parent
            self.assertFalse((package/"file-bridge").exists());self.assertFalse(list(package.rglob("*TransactionTests*")))
            self.assertTrue(list(package.rglob("OnslaughtToolkit.Godot.dll")))
            for name in ("LICENSE.txt","GODOT-LICENSE.txt","GODOT-THIRD-PARTY-NOTICES.json","DOTNET-LICENSE.txt","DOTNET-THIRD-PARTY-NOTICES.txt"):self.assertTrue((package/name).is_file())
            self.assertIn("no helper process",(package/"README.txt").read_text())
        self.assertFalse(any(call["args"][0]=="publish" for call in self.calls_read()))

    def test_framework_dependent_export_is_refused(self)->None:
        with mock.patch.dict(os.environ,{"FAKE_FRAMEWORK_DEPENDENT":"1"}):self.assertEqual(2,self.invoke("export","--platform","linux"))

    def test_obsolete_helper_leak_is_refused(self)->None:
        with mock.patch.dict(os.environ,{"FAKE_HELPER_LEAK":"1"}):self.assertEqual(2,self.invoke("export","--platform","linux"))


if __name__ == "__main__":
    unittest.main()
