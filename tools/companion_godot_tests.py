#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Focused fake-tool checks for the code-built C# companion routes and export boundaries."""
from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from pathlib import Path
from unittest import mock

import companion_godot as host

WRAPPER = '[gd_scene format=3]\n\n[ext_resource type="Script" path="res://Ui/CompanionApp.cs" id="1"]\n\n[node name="Companion" type="Control"]\nscript = ExtResource("1")\n'


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux development runner")
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
            "project.godot": 'config_version=5\n\n[application]\nconfig/name="Onslaught Toolkit"\n', "Main.tscn": WRAPPER,
            "OnslaughtToolkit.Godot.csproj": "integrated project", "global.json": '{"sdk":{"version":"10.0.402"}}',
            "OnslaughtToolkit.Godot.sln": "single-project Godot solution", "packages.lock.json": '{"dependencies":{"net10.0":{"BouncyCastle.Cryptography":{"resolved":"2.7.0"}}}}',
            "Ui/CompanionApp.cs": "code-built application root", "Files/ProtectedSaveFiles.cs": "integrated safety adapter",
            "Tests/CompanionTestRunner.cs": "C# contract runner", "Development/LicenseMetadata.cs": "C# notice entry", "Development/ScreenCapture.cs": "C# capture entry",
            "Development/IconWriter.cs": "C# icon entry",
            "Ui/CompanionApp.cs.uid": "uid://generated-by-an-editor-open",
        }.items():
            path = self.project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data, encoding="utf-8")
        for name in ("lore/_index.md", "lore/world-lore.md", "lore-book/BOOK.md"):
            (self.source / name).parent.mkdir(exist_ok=True)
            (self.source / name).write_text("# Project-written article\n", encoding="utf-8")
        self.fixture = self.root / "fixture.bin"
        self.fixture.write_bytes(host.FIXTURE.read_bytes())
        self.pins = host.read_json(host.COMPANION / "toolchain.json")
        self.engine = self.root / "installed" / self.pins["engine"]["installDirectory"] / self.pins["engine"]["executable"]
        self.engine.parent.mkdir(parents=True)
        self.dotnet = self.root / "bin/dotnet"
        self.dotnet.parent.mkdir()
        self.calls = self.root / "calls.jsonl"
        sdk_version, runtime = self.pins["dotnet"]["sdkVersion"], self.pins["dotnet"]["runtimeVersion"]
        fake = (
            f"#!{sys.executable}\n"
            "import json, os, pathlib, shutil, sys\n"
            "tool=pathlib.Path(sys.argv[0]).name\n"
            "if '--version' in sys.argv:\n"
            f" print({sdk_version!r} if tool=='dotnet' else os.environ.get('FAKE_VERSION',{self.pins['engineVersion']!r})); raise SystemExit(0)\n"
            "with open(os.environ['FAKE_CALLS'],'a') as f: f.write(json.dumps({'tool':tool,'args':sys.argv[1:],'cwd':os.getcwd(),'tmp':os.environ['TMPDIR'],'data':os.environ['XDG_DATA_HOME'],'cache':os.environ['XDG_CACHE_HOME'],'config':os.environ['XDG_CONFIG_HOME'],'home':os.environ['HOME'],'dotnet_home':os.environ['DOTNET_CLI_HOME'],'nuget':os.environ['NUGET_PACKAGES'],'path':os.environ['PATH'],'dotnet_root':os.environ.get('DOTNET_ROOT'),'display':os.environ.get('DISPLAY'),'wayland':os.environ.get('WAYLAND_DISPLAY'),'bus':os.environ.get('DBUS_SESSION_BUS_ADDRESS'),'ce_user':os.environ.get('BEA_USER_DIR'),'old_bridge':os.environ.get('ONSLAUGHT_FILE_BRIDGE')})+'\\n')\n"
            "if tool=='dotnet' and sys.argv[1]=='restore' and os.environ.get('FAKE_ADVISORY'): print('warning NU1903: Package X 1.0.0 has a known high severity vulnerability')\n"
            "if tool=='dotnet' and sys.argv[1] in ('restore','build'):\n"
            " project=pathlib.Path(sys.argv[2]).parent\n"
            " shutil.copytree(os.environ['FAKE_NUGET'],os.environ['NUGET_PACKAGES'],dirs_exist_ok=True)\n"
            " assets=project/'.godot/mono/temp/obj'; assets.mkdir(parents=True,exist_ok=True)\n"
            " (assets/'project.assets.json').write_text(json.dumps({'packageFolders':{os.environ['NUGET_PACKAGES']:{}}}))\n"
            " if sys.argv[1]=='build':\n"
            "  target=project/'.godot/mono/temp/bin/Debug'; target.mkdir(parents=True,exist_ok=True); (target/'OnslaughtToolkit.Godot.dll').write_text('integrated assembly')\n"
            "if 'res://Development/LicenseMetadata.cs' in sys.argv: print(json.dumps({'license':'Godot MIT','components':[{'name':'component'}],'licenses':{'MIT':'notice'}}))\n"
            "if 'res://Development/IconWriter.cs' in sys.argv: pathlib.Path(next(a for a in sys.argv if a.startswith('--output='))[9:]).write_bytes(bytes((137, 80, 78, 71, 13, 10, 26, 10)) + b' fake icon')\n"
            "if '--import' in sys.argv and os.environ.get('FAKE_PARSE_ERROR'): print('SCRIPT ERROR: Parse Error: broken source')\n"
            "if '--export-release' in sys.argv:\n"
            " target=pathlib.Path(sys.argv[sys.argv.index('--export-release')+2]); target.write_text('native exe'); target.with_suffix('.pck').write_text('native resources')\n"
            " data=target.parent/'data_OnslaughtToolkit.Godot'; data.mkdir()\n"
            " for name in ['OnslaughtToolkit.Godot.dll','GodotSharp.dll','libcoreclr.so']: (data/name).write_text('integrated runtime')\n"
            " if os.environ.get('FAKE_TEST_LEAK'): (data/'OnslaughtToolkit.Godot.dll').write_text('OnslaughtToolkit.Companion.Tests')\n"
            f" config={{'includedFrameworks':[{{'name':'Microsoft.NETCore.App','version':{runtime!r}}}]}}\n"
            f" if os.environ.get('FAKE_FRAMEWORK_DEPENDENT'): config={{'framework':{{'name':'Microsoft.NETCore.App','version':{runtime!r}}}}}\n"
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
        self.lock.write_text(json.dumps({"paths":{"dataRoot":str(self.root/"installed")},"archives":archives,"managedTools":[{"id":"dotnetSdk8","exactVersion":"8.0.424"},{"id":self.pins["dotnet"]["sdkTool"],"exactVersion":sdk_version}]}),encoding="utf-8")
        packages = self.root / "packages"
        for rid in ("linux-x64","win-x64"):
            package=packages/f"microsoft.netcore.app.runtime.{rid}/{runtime}"
            package.mkdir(parents=True)
            for name in ("LICENSE.TXT","THIRD-PARTY-NOTICES.TXT"):(package/name).write_text(name,encoding="utf-8")
            pin=self.pins["dotnet"]["runtimePacks"][rid]
            nupkg=package/pin["package"];nupkg.write_bytes(f"runtime pack {rid}".encode())
            pin["sha512"]=base64.b64encode(hashlib.sha512(nupkg.read_bytes()).digest()).decode()
            pin["sha256"]=host.sha256(nupkg)
            (package/(pin["package"]+".sha512")).write_text(pin["sha512"],encoding="ascii")
        crypto = packages / "bouncycastle.cryptography/2.7.0"
        crypto.mkdir(parents=True)
        (crypto / "LICENSE.md").write_text("MIT license fixture", encoding="utf-8")
        self.packages = packages
        (self.project / "toolchain.json").write_text(json.dumps(self.pins),encoding="utf-8")
        for patch in (mock.patch.object(host,"ROOT",self.source),mock.patch.object(host,"COMPANION",self.project),
                      mock.patch.object(host,"FIXTURE",self.fixture),
                      mock.patch.object(host,"canonical_root",return_value=self.canonical),
                      mock.patch.dict(os.environ,{"FAKE_CALLS":str(self.calls),"FAKE_NUGET":str(packages),"NUGET_PACKAGES":str(packages),"ONSLAUGHT_GODOT_HEADLESS":"","ONSLAUGHT_FILE_BRIDGE":"must-not-be-used","PATH":str(self.dotnet.parent)+os.pathsep+os.environ["PATH"]})):
            patch.start();self.addCleanup(patch.stop)

    def invoke(self,*arguments:str)->int:
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            return host.companion_main([*arguments,"--engine",str(self.engine),"--shared-lock",str(self.lock)])

    @contextlib.contextmanager
    def standalone(self, *, templates: Path | None = None):
        verifier = mock.Mock(return_value=(self.engine, templates, self.dotnet))
        module = types.SimpleNamespace(verified_install=verifier)
        with mock.patch.dict(sys.modules, {"companion_toolchain": module}), mock.patch.dict(
                os.environ, {host.SHARED_LOCK_ENV: ""}):
            yield verifier

    def invoke_standalone(self, *arguments: str) -> int:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return host.companion_main(list(arguments))

    def calls_read(self)->list[dict]:
        return [json.loads(line) for line in self.calls.read_text().splitlines()] if self.calls.exists() else []

    def test_optional_headless_wrapper_preserves_owned_profiles(self)->None:
        wrapper = self.root / "godot-headless"
        wrapper.write_text('#!/bin/sh\nexec "$GODOT" --headless "$@"\n', encoding="utf-8")
        wrapper.chmod(0o755)
        with mock.patch.dict(os.environ, {"ONSLAUGHT_GODOT_HEADLESS":str(wrapper), "BEA_USER_DIR":"/must-not-read-real-ce"}):
            self.assertEqual(0, self.invoke("test"))
        native = next(call for call in self.calls_read() if any(arg.startswith("--fixture=") for arg in call["args"]))
        self.assertIn("--headless", native["args"])
        self.assertTrue(Path(native["home"]).is_relative_to(self.canonical))
        self.assertIsNone(native["ce_user"])

    def test_build_uses_integrated_project_and_exact_safety_snapshots(self)->None:
        self.assertEqual(0,self.invoke("build"))
        calls=self.calls_read()
        self.assertEqual(["restore","build"],[call["args"][0] for call in calls if call["tool"]=="dotnet"])
        restore=next(call for call in calls if call["args"][0]=="restore")
        self.assertIn("--locked-mode",restore["args"])
        staged=Path(restore["args"][1]).parent
        for name in ("Main.tscn","Ui/CompanionApp.cs","Files/ProtectedSaveFiles.cs","Tests/CompanionTestRunner.cs"):self.assertTrue((staged/name).is_file())
        self.assertFalse((staged/"Ui/CompanionApp.cs.uid").exists())
        self.assertFalse((self.project/".godot").exists())
        self.assertTrue(all(call["old_bridge"] is None for call in calls))
        self.assertFalse(any("FileBridge.csproj" in str(call) for call in calls))

    def test_each_invocation_isolates_imports_builds_profiles_and_logs(self)->None:
        self.assertEqual(0,self.invoke("check"));self.assertEqual(0,self.invoke("check"))
        imports=[call for call in self.calls_read() if "--import" in call["args"]]
        self.assertNotEqual(imports[0]["tmp"],imports[1]["tmp"])
        for call in self.calls_read():
            for key in ("tmp","data","cache","config","home","dotnet_home","nuget"):
                self.assertTrue(Path(call[key]).is_relative_to(self.canonical/"local-data/companion"))
            self.assertTrue(all(call[key] is None for key in ("display","wayland","bus")))

    def test_build_does_not_require_export_templates(self) -> None:
        shared = host.read_json(self.lock)
        shared["archives"] = [entry for entry in shared["archives"]
                              if entry["id"] != self.pins["templates"]["archiveId"]]
        self.lock.write_text(json.dumps(shared), encoding="utf-8")
        self.assertEqual(0, self.invoke("build"))
        self.assertEqual(2, self.invoke("export", "--platform", "linux"))

    def test_dotnet_lookup_uses_the_child_environment_path(self) -> None:
        output, env = host.allocate_output(self.canonical / "local-data/companion", "build")
        env["PATH"] = str(self.dotnet.parent)
        with mock.patch.dict(os.environ, {"PATH": str(self.root / "missing")}):
            self.assertEqual(str(self.dotnet), host.dotnet_sdk(self.pins, self.project, env, output))
        for value in ("", str(self.root / "missing")):
            env["PATH"] = value
            with self.assertRaisesRegex(RuntimeError, "pinned .NET SDK"):
                host.dotnet_sdk(self.pins, self.project, env, output)

    def test_engine_bytes_pin_refuses_before_build(self)->None:
        self.engine.write_text(self.engine.read_text()+"\n# different bytes\n")
        self.assertEqual(2,self.invoke("build"));self.assertEqual([],self.calls_read())

    def test_sdk_bytes_pin_refuses_before_build(self)->None:
        (self.engine.parent/self.pins["engine"]["sdkPackage"]).write_text("different SDK")
        self.assertEqual(2,self.invoke("build"));self.assertEqual([],self.calls_read())

    def test_standard_engine_version_is_refused(self)->None:
        with mock.patch.dict(os.environ,{"FAKE_VERSION":self.pins["engineVersion"].replace(".mono","")}):self.assertEqual(2,self.invoke("build"))
        self.assertEqual([],self.calls_read())

    def test_template_bytes_pin_refuses_export_before_build(self)->None:
        (self.templates/"windows_release_x86_64.exe").write_text("wrong")
        self.assertEqual(2,self.invoke("export","--platform","windows"));self.assertEqual([],self.calls_read())

    def test_zero_exit_godot_parse_error_fails_check(self)->None:
        with mock.patch.dict(os.environ,{"FAKE_PARSE_ERROR":"1"}):self.assertEqual(2,self.invoke("check"))

    def test_gdscript_and_saved_resources_are_refused_before_build(self)->None:
        for name in ("Ui/legacy.gd","Ui/theme.tres","Ui/look.gdshader"):
            with self.subTest(name=name):
                (self.project/name).write_text("editor-authored",encoding="utf-8")
                self.assertEqual(2,self.invoke("build"));self.assertEqual([],self.calls_read())
                (self.project/name).unlink()

    def test_scene_must_be_a_one_node_script_wrapper(self)->None:
        for text in (WRAPPER+'[node name="Extra" type="Label" parent="."]\n',
                     WRAPPER.replace('type="Script"','type="Theme"'),
                     WRAPPER+'[sub_resource type="StyleBoxFlat" id="look"]\n'):
            with self.subTest(text=text):
                (self.project/"Main.tscn").write_text(text,encoding="utf-8")
                self.assertEqual(2,self.invoke("build"));self.assertEqual([],self.calls_read())

    def test_native_test_receives_owned_fixture_and_runs_the_csharp_entry(self)->None:
        before=self.fixture.read_bytes();self.assertEqual(0,self.invoke("test"))
        calls=self.calls_read();native=next(call for call in calls if any(arg.startswith("--fixture=") for arg in call["args"]))
        self.assertIn("res://Tests/CompanionTestRunner.cs",native["args"]);self.assertIn("--headless",native["args"])
        copied=Path(next(arg.split("=",1)[1] for arg in native["args"] if arg.startswith("--fixture=")))
        self.assertNotEqual(copied,self.fixture);self.assertEqual(before,copied.read_bytes());self.assertEqual(before,self.fixture.read_bytes())
        self.assertFalse(any(call["args"][0]=="publish" for call in calls))

    def test_native_test_failure_is_reported(self)->None:
        with mock.patch.dict(os.environ,{"FAKE_NATIVE_EXIT":"17"}):self.assertEqual(17,self.invoke("test"))

    def test_normal_dotnet_exports_bundle_runtime_not_helper_or_harness(self)->None:
        self.assertEqual(0,self.invoke("export","--platform","both"))
        exports=[call for call in self.calls_read() if "--export-release" in call["args"]]
        self.assertEqual(2,len(exports))
        for call in exports:
            package=Path(call["args"][call["args"].index("--export-release")+2]).parent
            self.assertFalse((package/"file-bridge").exists());self.assertFalse(list(package.rglob("*TransactionTests*")))
            self.assertTrue(list(package.rglob("OnslaughtToolkit.Godot.dll")))
            for name in ("LICENSE.txt","LORE-LICENSE.txt","GODOT-LICENSE.txt","GODOT-THIRD-PARTY-NOTICES.json","DOTNET-LICENSE.txt","DOTNET-THIRD-PARTY-NOTICES.txt","BOUNCYCASTLE-LICENSE.txt"):self.assertTrue((package/name).is_file())
            readme=(package/"README.txt").read_text();self.assertIn("no helper process",readme);self.assertIn("C# application built in code",readme)
            self.assertIn("Choose Original Battle Engine Aquila or Onslaught CE on Home",readme)
            self.assertIn("Original-install careers shown under CE are read-only",readme)
            self.assertIn("update_check and record_sessions only",readme)
            self.assertIn("backs up supported careers and, for the original game, supported settings",readme)
            self.assertIn("separate backup or an absence note",readme)
            self.assertIn("junction or bind mount into either: not every folder alias can be detected",readme)
            self.assertIn("checks whether the game or Onslaught CE is running before the backup",readme)
            self.assertIn("again before putting the changed file in place",readme)
            self.assertIn("before starting either",readme)
            self.assertNotIn("writes nothing while the game",readme)
            self.assertNotIn("does not yet read or launch Onslaught CE",readme)
            if package.name == "windows":
                self.assertIn("Native Windows checks exercised CE process detection",readme)
                self.assertIn("still require native Windows acceptance",readme)
                self.assertNotIn("Spotting a running Onslaught CE has not been tested",readme)
            self.assertEqual(host.APP_LICENSE.read_bytes(),(package/"LICENSE.txt").read_bytes());self.assertIn("GNU GENERAL PUBLIC LICENSE",(package/"LICENSE.txt").read_text())
            self.assertIn("Attribution-ShareAlike 4.0 International",(package/"LORE-LICENSE.txt").read_text());self.assertIn("GPL-3.0-only",readme);self.assertIn("CC BY-SA 4.0",readme)
        self.assertFalse(any(call["args"][0]=="publish" for call in self.calls_read()))
        icon=[call for call in self.calls_read() if "res://Development/IconWriter.cs" in call["args"]]
        self.assertEqual(1,len(icon))
        staged=Path(icon[0]["cwd"])
        self.assertIn('config/icon="res://icon.png"',(staged/"project.godot").read_text())
        self.assertTrue((staged/"icon.png").read_bytes().startswith(host.PNG_SIGNATURE))

    def test_the_pins_name_the_net10_runtime_that_sdk_10_0_402_ships(self)->None:
        pins=host.read_json(Path(host.__file__).resolve().parents[1]/"companion/OnslaughtToolkit.Godot/toolchain.json")
        self.assertEqual(("10.0.402","10.0.13","net10.0","dotnetSdk10"),
                         (pins["dotnet"]["sdkVersion"],pins["dotnet"]["runtimeVersion"],pins["dotnet"]["targetFramework"],pins["dotnet"]["sdkTool"]))
        for rid in ("linux-x64","win-x64"):
            pack=pins["dotnet"]["runtimePacks"][rid]
            self.assertEqual(f"microsoft.netcore.app.runtime.{rid}.10.0.13.nupkg",pack["package"])
            self.assertEqual(64,len(base64.b64decode(pack["sha512"])));self.assertRegex(pack["sha256"],r"^[0-9a-f]{64}$")

    def test_a_runtime_pack_that_differs_from_its_official_hash_is_refused(self)->None:
        for change in ("bytes","record"):
            with self.subTest(change=change):
                pin=self.pins["dotnet"]["runtimePacks"]["linux-x64"]
                folder=self.packages/f"microsoft.netcore.app.runtime.linux-x64/{self.pins['dotnet']['runtimeVersion']}"
                target=folder/(pin["package"] if change=="bytes" else pin["package"]+".sha512")
                original=target.read_bytes();target.write_bytes(original+b"x")
                try:self.assertEqual(2,self.invoke("export","--platform","linux"))
                finally:target.write_bytes(original)
        (self.packages/f"microsoft.netcore.app.runtime.win-x64/{self.pins['dotnet']['runtimeVersion']}"/self.pins["dotnet"]["runtimePacks"]["win-x64"]["package"]).unlink()
        self.assertEqual(2,self.invoke("export","--platform","windows"))
        self.assertEqual(0,self.invoke("export","--platform","linux"))

    def test_audit_restores_outside_locked_mode_and_fails_on_an_advisory(self)->None:
        self.assertEqual(0,self.invoke("audit"))
        restore=[call for call in self.calls_read() if call["tool"]=="dotnet"]
        self.assertEqual(["restore"],[call["args"][0] for call in restore])
        self.assertNotIn("--locked-mode",restore[0]["args"]);self.assertIn("-p:NuGetAudit=true",restore[0]["args"])
        self.assertIn("-p:NuGetAuditMode=all",restore[0]["args"])
        self.assertFalse(any("--import" in call["args"] for call in self.calls_read()))
        with mock.patch.dict(os.environ,{"FAKE_ADVISORY":"1"}):self.assertEqual(2,self.invoke("audit"))

    def test_the_engine_defaults_to_the_pinned_install(self)->None:
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(0,host.companion_main(["check","--shared-lock",str(self.lock)]))
        self.assertTrue(any(call["tool"]==self.engine.name and "--import" in call["args"] for call in self.calls_read()))

    def test_the_lock_comes_from_the_argument_or_the_environment_and_is_never_assumed(self)->None:
        with mock.patch.dict(os.environ,{host.SHARED_LOCK_ENV:"~/elsewhere/lock.json"}):
            self.assertEqual(Path("given.json"),host.shared_lock_file(Path("given.json")),"the argument wins")
            self.assertEqual(Path("~/elsewhere/lock.json").expanduser(),host.shared_lock_file(None))
        for value in ("","   "):
            with mock.patch.dict(os.environ,{host.SHARED_LOCK_ENV:value}):self.assertIsNone(host.shared_lock_file(None),repr(value))
        with mock.patch.dict(os.environ):
            os.environ.pop(host.SHARED_LOCK_ENV,None);self.assertIsNone(host.shared_lock_file(None))
        for name in ("tools/companion_godot.py","companion/OnslaughtToolkit.Godot/toolchain.json","companion/OnslaughtToolkit.Godot/README.md"):
            source=(Path(__file__).resolve().parents[1]/name).read_text(encoding="utf-8")
            self.assertNotIn("game_pipeline_shared",source,name);self.assertNotIn("~/Projects",source,name);self.assertNotIn("Projects/game-dev",source,name)

    def test_a_run_with_no_shared_lock_uses_the_verified_public_install(self) -> None:
        with self.standalone() as verifier:
            self.assertEqual(0, self.invoke_standalone("check"))
        verifier.assert_called_once_with(self.canonical / "local-data/toolchains/companion", self.pins, [])
        calls = self.calls_read()
        self.assertTrue(any("--import" in call["args"] for call in calls))
        for call in calls:
            self.assertEqual(str(self.dotnet.parent), call["path"].split(os.pathsep)[0])
            self.assertEqual(str(self.dotnet.parent), call["dotnet_root"])

    def test_an_unverified_public_install_never_falls_back_to_path_tools(self) -> None:
        stderr = io.StringIO()
        with self.standalone() as verifier:
            verifier.side_effect = RuntimeError("Pinned public setup is missing or changed")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                self.assertEqual(2, host.companion_main(["check", "--engine", str(self.engine)]))
        self.assertIn("tools/companion_toolchain.py setup --root", stderr.getvalue())
        self.assertEqual([], self.calls_read())
        self.assertFalse((self.canonical / "local-data/companion").exists())

    def test_explicit_public_root_overrides_the_shared_lock_environment(self) -> None:
        root = self.root / "public-install"
        with self.standalone() as verifier, mock.patch.dict(os.environ, {host.SHARED_LOCK_ENV: str(self.lock)}), \
                mock.patch.object(host, "verify_toolchain", side_effect=AssertionError("shared route selected")):
            self.assertEqual(0, self.invoke_standalone("build", "--toolchain-root", str(root)))
        verifier.assert_called_once_with(root, self.pins, [])

    def test_public_root_resolves_against_the_callers_home(self) -> None:
        home = self.root / "caller-home"
        with self.standalone() as verifier, mock.patch.dict(os.environ, {"HOME": str(home)}):
            self.assertEqual(0, self.invoke_standalone("check", "--toolchain-root", "~/public-toolchain"))
        verifier.assert_called_once_with(home / "public-toolchain", self.pins, [])

    def test_invalid_shared_selection_does_not_fall_back_to_public_setup(self) -> None:
        with self.standalone() as verifier:
            self.assertEqual(2, self.invoke_standalone("check", "--shared-lock", str(self.root / "missing-lock")))
        verifier.assert_not_called()
        self.assertEqual([], self.calls_read())

    def test_standalone_run_keeps_interactive_home_and_windowed_launch(self) -> None:
        home = self.root / "caller-home"
        with self.standalone(), mock.patch.dict(os.environ, {"HOME": str(home)}):
            self.assertEqual(0, self.invoke_standalone("run", "--timeout", "10"))
        launch = self.calls_read()[-1]
        self.assertNotIn("--headless", launch["args"])
        self.assertEqual(str(home), launch["home"])

    def test_explicit_public_and_shared_install_selections_are_exclusive(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stopped:
            host.companion_main(["check", "--shared-lock", str(self.lock), "--toolchain-root", str(self.root)])
        self.assertEqual(2, stopped.exception.code)
        self.assertEqual([], self.calls_read())

    def test_standalone_engine_override_cannot_select_another_install(self) -> None:
        other = self.root / "other-engine"
        other.write_bytes(self.engine.read_bytes())
        other.chmod(0o700)
        with self.standalone():
            self.assertEqual(2, self.invoke_standalone("build", "--engine", str(other)))
        self.assertEqual([], self.calls_read())

    def test_standalone_engine_version_is_checked_before_build(self) -> None:
        with self.standalone(), mock.patch.dict(os.environ, {"FAKE_VERSION": "other-version"}):
            self.assertEqual(2, self.invoke_standalone("build"))
        self.assertEqual([], self.calls_read())

    def test_standalone_build_uses_its_sdk_when_the_parent_path_names_another(self) -> None:
        other = self.root / "other-bin"
        other.mkdir()
        (other / "dotnet").write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
        (other / "dotnet").chmod(0o700)
        with self.standalone(), mock.patch.dict(os.environ, {"PATH": str(other)}):
            self.assertEqual(0, self.invoke_standalone("build"))

    def test_standalone_export_verifies_only_the_selected_templates(self) -> None:
        with self.standalone(templates=self.templates) as verifier:
            self.assertEqual(0, self.invoke_standalone("export", "--platform", "linux"))
        verifier.assert_called_once_with(self.canonical / "local-data/toolchains/companion", self.pins, ["linux"])
        self.assertEqual(1, sum("--export-release" in call["args"] for call in self.calls_read()))

    def test_standalone_export_refuses_missing_templates_before_build(self) -> None:
        with self.standalone():
            self.assertEqual(2, self.invoke_standalone("export", "--platform", "linux"))
        self.assertEqual([], self.calls_read())

    def test_the_environment_variable_stands_in_for_the_argument(self)->None:
        with mock.patch.dict(os.environ,{host.SHARED_LOCK_ENV:str(self.lock)}),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(0,host.companion_main(["check","--engine",str(self.engine)]))
        self.assertTrue(any("--import" in call["args"] for call in self.calls_read()))

    def test_old_outputs_are_pruned_to_the_newest_few_of_each_mode(self)->None:
        owner=host.worktree_output_owner();owner.mkdir(parents=True)
        for index in range(8):
            for mode in ("test","export"):
                folder=owner/f"godot-dotnet-{mode}-old{index}";folder.mkdir();os.utime(folder,(1000+index,1000+index))
        self.assertEqual(0,self.invoke("test"))
        tests=sorted(path.name for path in owner.glob("godot-dotnet-test-*"))
        self.assertEqual(host.KEEP_OUTPUTS,len(tests))
        self.assertEqual([f"godot-dotnet-test-old{index}" for index in range(4,8)],[name for name in tests if "old" in name])
        self.assertEqual(8,len(list(owner.glob("godot-dotnet-export-*"))))

    def test_a_folder_a_live_run_holds_is_never_pruned(self)->None:
        owner=self.canonical/"local-data/companion";owner.mkdir(parents=True)
        for index in range(8):
            folder=owner/f"godot-dotnet-run-old{index}";folder.mkdir();os.utime(folder,(1000+index,1000+index))
        held=owner/"godot-dotnet-run-old0"
        descriptor=os.open(held/host.IN_USE_LOCK,os.O_RDWR|os.O_CREAT,0o600);self.addCleanup(os.close,descriptor)
        host.fcntl.flock(descriptor,host.fcntl.LOCK_EX)
        os.utime(held,(1000,1000))
        removed=host.prune_outputs(owner,"run",4)
        self.assertTrue(held.is_dir());self.assertNotIn(held,removed)
        self.assertEqual(sorted(f"godot-dotnet-run-old{index}" for index in range(1,4)),sorted(path.name for path in removed))
        output,_=host.allocate_output(owner,"run")
        self.assertTrue(host.output_in_use(output))

    def test_a_missing_pinned_engine_names_the_expected_path(self)->None:
        self.engine.unlink()
        stderr=io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(stderr):
            self.assertNotEqual(0,host.companion_main(["check","--shared-lock",str(self.lock)]))
        self.assertIn(f"not found: {self.engine}",stderr.getvalue())
        self.assertNotIn("not found: None",stderr.getvalue())

    def test_framework_dependent_export_is_refused(self)->None:
        with mock.patch.dict(os.environ,{"FAKE_FRAMEWORK_DEPENDENT":"1"}):self.assertEqual(2,self.invoke("export","--platform","linux"))

    def test_obsolete_helper_leak_is_refused(self)->None:
        with mock.patch.dict(os.environ,{"FAKE_HELPER_LEAK":"1"}):self.assertEqual(2,self.invoke("export","--platform","linux"))

    def test_capture_runs_the_csharp_entry_through_the_offscreen_runner(self)->None:
        offscreen=self.root/"bin/godot-offscreen"
        offscreen.write_text(f"#!{sys.executable}\nimport json,os,pathlib,sys\n"
            "with open(os.environ['FAKE_CALLS'],'a') as f: f.write(json.dumps({'tool':'godot-offscreen','args':sys.argv[1:],'cwd':os.getcwd(),'tmp':os.environ['TMPDIR'],'data':os.environ['XDG_DATA_HOME'],'cache':os.environ['XDG_CACHE_HOME'],'config':os.environ['XDG_CONFIG_HOME'],'lock':os.environ.get('GODOT_GPU_LOCK'),'old_bridge':None})+'\\n')\n"
            "out=pathlib.Path(next(a.split('=',1)[1] for a in sys.argv if a.startswith('--output=')))\n"
            "out.mkdir(parents=True); (out/'1280x800-01-home.png').write_bytes(b'png')\n"
            "print('CAPTURES_DONE 1 screens')\n",encoding="utf-8")
        offscreen.chmod(0o700)
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            code=host.companion_main(["capture","--engine",str(self.engine),"--shared-lock",str(self.lock),"--offscreen",str(offscreen)])
        self.assertEqual(0,code)
        call=next(call for call in self.calls_read() if call["tool"]=="godot-offscreen")
        self.assertIn("res://Development/ScreenCapture.cs",call["args"]);self.assertIn("--done-marker",call["args"])
        self.assertNotIn("--output",call["args"]);self.assertIsNone(call["lock"])
        fixture=Path(next(a.split("=",1)[1] for a in call["args"] if a.startswith("--fixture=")))
        self.assertNotEqual(fixture,self.fixture);self.assertEqual(self.fixture.read_bytes(),fixture.read_bytes())
        # Beside a job on the NVIDIA card: its own hidden output, queued on the lanes' shared iGPU lock.
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            code=host.companion_main(["capture","--beside-gpu-jobs","--engine",str(self.engine),"--shared-lock",str(self.lock),"--offscreen",str(offscreen)])
        self.assertEqual(0,code)
        beside=[call for call in self.calls_read() if call["tool"]=="godot-offscreen"][-1]
        self.assertEqual("--output",beside["args"][0]);self.assertRegex(beside["args"][1],r"^COMPANION-[A-Za-z0-9-]+$")
        self.assertEqual("/var/tmp/godot-igpu.lock",beside["lock"])
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(2,host.companion_main(["capture","--sizes","big","--engine",str(self.engine),"--shared-lock",str(self.lock),"--offscreen",str(offscreen)]))
            for script in ("/abs/Capture.cs","Development/Missing.cs","../Capture.cs"):
                self.assertEqual(2,host.companion_main(["capture","--capture-script",script,"--engine",str(self.engine),"--shared-lock",str(self.lock),"--offscreen",str(offscreen)]))

    def test_contract_tests_in_a_release_assembly_are_refused(self)->None:
        with mock.patch.dict(os.environ,{"FAKE_TEST_LEAK":"1"}):self.assertEqual(2,self.invoke("export","--platform","linux"))


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux development runner")
class CompanionOutputOwnershipTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="companion-output-ownership-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.canonical = self.root / "canonical"
        self.canonical.mkdir()

    def test_worktrees_keep_separate_outputs_and_legacy_folders(self) -> None:
        class ReachedAllocation(Exception):
            pass

        owners = []
        with mock.patch.object(host, "canonical_root", return_value=self.canonical):
            for name in ("first-worktree", "first-worktree", "second-worktree"):
                root = self.root / name
                root.mkdir(exist_ok=True)
                with mock.patch.object(host, "ROOT", root), mock.patch.object(
                    host, "allocate_output", side_effect=ReachedAllocation
                ) as allocation, self.assertRaises(ReachedAllocation):
                    host.companion_main(["test", "--shared-lock", str(self.root / "lock")])
                owners.append(allocation.call_args.args[0])
        self.assertEqual(owners[0], owners[1])
        owners = [owners[0], owners[2]]
        self.assertNotEqual(*owners)
        self.assertTrue(all(owner.is_relative_to(self.canonical / "local-data/companion") for owner in owners))

        legacy = self.canonical / "local-data/companion"
        folders = []
        for owner in (*owners, legacy):
            owner.mkdir(parents=True, exist_ok=True)
            group = []
            for index in range(host.KEEP_OUTPUTS):
                folder = owner / f"godot-dotnet-test-owned-{index}"
                folder.mkdir()
                (folder / "evidence.txt").write_text("authored evidence", encoding="utf-8")
                os.utime(folder, (1000 + index, 1000 + index))
                group.append(folder)
            folders.append(group)

        with mock.patch.object(host.shutil, "rmtree") as remove:
            output, _ = host.allocate_output(owners[1], "test")
        self.assertEqual([mock.call(folders[1][0])], remove.call_args_list)
        self.assertTrue(output.is_relative_to(owners[1]))
        self.assertTrue(all(folder.exists() for group in folders for folder in group))
        with mock.patch.object(host.shutil, "rmtree") as legacy_remove:
            host.prune_outputs(legacy, "test", 0)
        self.assertEqual(set(folders[2]), {call.args[0] for call in legacy_remove.call_args_list})

    def test_allocation_is_locked_before_another_run_can_prune(self) -> None:
        owner = self.root / "output"
        owner.mkdir()
        for index in range(host.KEEP_OUTPUTS - 1):
            folder = owner / f"godot-dotnet-test-old-{index}"
            folder.mkdir()
            os.utime(folder, (2000 + index, 2000 + index))
        entered = threading.Event()
        release = threading.Event()
        second_started = threading.Event()
        second_done = threading.Event()
        outputs = {}
        failures = []
        original_hold = host.hold_output

        def delayed_hold(output: Path) -> None:
            if threading.current_thread().name == "first":
                os.utime(output, (1000, 1000))
                entered.set()
                if not release.wait(5):
                    raise TimeoutError("first allocator was not released")
                original_hold(output)
                os.utime(output, (1000, 1000))
            else:
                original_hold(output)

        def allocate(name: str) -> None:
            try:
                if name == "second":
                    second_started.set()
                outputs[name], _ = host.allocate_output(owner, "test")
            except BaseException as error:
                failures.append(error)
            finally:
                if name == "second":
                    second_done.set()

        first = threading.Thread(target=allocate, args=("first",), name="first")
        second = threading.Thread(target=allocate, args=("second",), name="second")
        with mock.patch.object(host, "hold_output", side_effect=delayed_hold), mock.patch.object(
            host.shutil, "rmtree"
        ) as remove:
            try:
                first.start()
                self.assertTrue(entered.wait(5))
                second.start()
                self.assertTrue(second_started.wait(5))
                self.assertFalse(second_done.wait(0.2), "another allocator passed the unlocked creation window")
            finally:
                release.set()
                first.join(5)
                if second.ident is not None:
                    second.join(5)
            self.assertFalse(first.is_alive() or second.is_alive())
            self.assertEqual([], failures)
            self.assertEqual({"first", "second"}, set(outputs))
            self.assertTrue(host.output_in_use(outputs["first"]))
            self.assertNotIn(mock.call(outputs["first"]), remove.call_args_list)

    def test_retention_preserves_live_and_unpruned_modes(self) -> None:
        owner = self.root / "output"
        owner.mkdir()
        folders = []
        for index in range(8):
            folder = owner / f"godot-dotnet-run-owned-{index}"
            folder.mkdir()
            os.utime(folder, (1000 + index, 1000 + index))
            folders.append(folder)
        for mode in ("export", "capture"):
            (owner / f"godot-dotnet-{mode}-owned").mkdir()
        descriptor = os.open(folders[0] / host.IN_USE_LOCK, os.O_RDWR | os.O_CREAT, 0o600)
        self.addCleanup(os.close, descriptor)
        host.fcntl.flock(descriptor, host.fcntl.LOCK_EX)
        os.utime(folders[0], (1000, 1000))
        with mock.patch.object(host.shutil, "rmtree") as remove:
            removed = host.prune_outputs(owner, "run", 4)
            self.assertEqual([], host.prune_outputs(owner, "export", 0))
            self.assertEqual([], host.prune_outputs(owner, "capture", 0))
        self.assertEqual(folders[1:4], list(reversed(removed)))
        self.assertEqual([mock.call(folder) for folder in removed], remove.call_args_list)
        self.assertTrue(all(folder.exists() for folder in folders))

    def test_allocation_lock_is_held_against_another_process(self) -> None:
        owner = self.root / "output"
        original_hold = host.hold_output
        probe = (
            "import fcntl, os, sys\n"
            "fd = os.open(sys.argv[1], os.O_RDWR)\n"
            "try:\n"
            " fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)\n"
            "except BlockingIOError:\n"
            " sys.exit(0)\n"
            "sys.exit(1)\n"
        )

        def check_lock(output: Path) -> None:
            result = subprocess.run([sys.executable, "-I", "-c", probe, str(owner / host.ALLOCATION_LOCK)],
                                    capture_output=True, timeout=5, check=False)
            self.assertEqual(0, result.returncode, "another process acquired the allocation lock")
            original_hold(output)

        with mock.patch.object(host, "hold_output", side_effect=check_lock), mock.patch.object(
            host.shutil, "rmtree"
        ) as remove:
            output, _ = host.allocate_output(owner, "test")
        remove.assert_not_called()
        self.assertTrue(host.output_in_use(output))

    def test_allocation_lock_symlink_is_refused_before_pruning(self) -> None:
        owner = self.root / "output"
        owner.mkdir()
        target = self.root / "unrelated"
        target.write_text("authored evidence", encoding="utf-8")
        (owner / host.ALLOCATION_LOCK).symlink_to(target)
        with mock.patch.object(host, "prune_outputs") as prune:
            with self.assertRaises(OSError):
                host.allocate_output(owner, "test")
        prune.assert_not_called()
        self.assertEqual("authored evidence", target.read_text(encoding="utf-8"))
        self.assertFalse(list(owner.glob("godot-dotnet-*")))

    def test_test_run_keeps_private_profile_environment(self) -> None:
        owner = self.root / "output"
        inherited = {"BEA_USER_DIR": "outside", "BEA_GAME_DIR": "outside", "BEA_UPDATE_FEED": "outside"}
        with mock.patch.dict(os.environ, inherited), mock.patch.object(host.shutil, "rmtree") as remove:
            output, env = host.allocate_output(owner, "test")
        remove.assert_not_called()
        for name in ("TMPDIR", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "HOME"):
            self.assertTrue(Path(env[name]).is_relative_to(output))
        self.assertTrue(all(name not in env for name in inherited))
        self.assertTrue(host.output_in_use(output))

    def test_noninteractive_modes_isolate_home_runtime_and_package_caches(self) -> None:
        inherited = {key: str(self.root / key.lower()) for key in (
            "HOME", "XDG_RUNTIME_DIR", "NUGET_PACKAGES", "NUGET_HTTP_CACHE_PATH", "NUGET_PLUGINS_CACHE_PATH")}
        inherited.update(DISPLAY="authored-display", WAYLAND_DISPLAY="authored-wayland", DBUS_SESSION_BUS_ADDRESS="authored-bus")
        with mock.patch.dict(os.environ, inherited):
            for mode in ("check", "build", "test", "export", "capture", "audit"):
                with self.subTest(mode=mode):
                    output, env = host.allocate_output(self.root / "output", mode)
                    for key in ("HOME", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME",
                                "DOTNET_CLI_HOME", "NUGET_PACKAGES", "NUGET_HTTP_CACHE_PATH", "NUGET_PLUGINS_CACHE_PATH"):
                        self.assertTrue(Path(env[key]).is_relative_to(output), key)
                    if mode != "capture":
                        self.assertTrue(Path(env["XDG_RUNTIME_DIR"]).is_relative_to(output))
                        self.assertEqual(0o700, Path(env["XDG_RUNTIME_DIR"]).stat().st_mode & 0o777)
                        self.assertTrue(all(key not in env for key in ("DISPLAY", "WAYLAND_DISPLAY", "DBUS_SESSION_BUS_ADDRESS")))
            output, env = host.allocate_output(self.root / "output", "run")
        self.assertEqual(inherited["HOME"], env["HOME"])
        self.assertEqual(inherited["XDG_RUNTIME_DIR"], env["XDG_RUNTIME_DIR"])
        self.assertEqual(inherited["DISPLAY"], env["DISPLAY"])
        self.assertTrue(Path(env["NUGET_PACKAGES"]).is_relative_to(output))


class ProjectIconTests(unittest.TestCase):
    def test_icon_is_added_to_the_application_section_once(self) -> None:
        text = 'config_version=5\n\n[application]\nconfig/name="Onslaught Toolkit"\n'
        updated = host.with_project_icon(text)
        self.assertIn('[application]\n\nconfig/icon="res://icon.png"\nconfig/name=', updated)
        self.assertEqual(updated.count("config/icon="), 1)

    def test_a_project_without_an_application_section_or_with_an_icon_is_refused(self) -> None:
        with self.assertRaises(RuntimeError):
            host.with_project_icon("config_version=5\n")
        with self.assertRaises(RuntimeError):
            host.with_project_icon('config_version=5\n\n[application]\nconfig/icon="res://other.png"\n')


if __name__ == "__main__":
    unittest.main()
