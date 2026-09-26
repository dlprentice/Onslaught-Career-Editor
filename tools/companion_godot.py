#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Pinned Godot .NET companion routes: a C# application built in code, including its file-safety boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from godot_host import print_process_output, run_process

ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "companion/OnslaughtToolkit.Godot"
SAFETY_SOURCES = ("SaveLabFileTransaction.cs", "FileMutationSafety.cs")
# Pure MIT AppCore readers the companion links unchanged; each is staged beside the safety sources.
LINKED_SOURCES = ("GameTextCatalog.cs", "GoodieUnlockRequirementService.cs", "CheatCodeCatalog.cs", "CheatSaveNameComposer.cs",
                  "CampaignLoreComposer.cs")
MIT_LICENSE = ROOT / "LICENSE"
FIXTURE = ROOT / "tests_shared/fixtures/gold_career_save.bin"
NATIVE_EXTENSIONS = {".godot", ".tscn", ".cfg", ".cs", ".csproj", ".sln"}
EXCLUDED_DIRECTORIES = {".godot", "bin", "obj", "local-data"}
# The companion is C# built in code: no GDScript, saved resources or editor-authored scenes.
EDITOR_ONLY_SUFFIXES = {".gd", ".tres", ".res", ".scn", ".gdshader"}
DEVELOPMENT_NAMESPACES = (b"OnslaughtToolkit.Companion.Tests", b"OnslaughtToolkit.Companion.Development")
PLATFORMS = {
    "linux": ("linux-x64", "Linux", "OnslaughtToolkit.x86_64"),
    "windows": ("win-x64", "Windows", "OnslaughtToolkit.exe"),
}


def read_json(path: Path) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return result


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical_root() -> Path:
    # Child worktrees use this repository's canonical ignored output owner, never a copied corpus.
    git_env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    common = Path(subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
        env=git_env, text=True).strip())
    return common.parent.resolve(strict=True)


def allocate_output(owner: Path, mode: str) -> tuple[Path, dict[str, str]]:
    owner.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix=f"godot-dotnet-{mode}-", dir=owner))
    directories = {
        "TMPDIR": "scratch", "XDG_DATA_HOME": "profile/data", "XDG_CONFIG_HOME": "profile/config",
        "XDG_CACHE_HOME": "profile/cache", "DOTNET_CLI_HOME": "profile/dotnet",
    }
    env = {key: value for key, value in os.environ.items() if key != "ONSLAUGHT_FILE_BRIDGE"}
    for key, relative in directories.items():
        path = output / relative
        path.mkdir(parents=True, exist_ok=True)
        env[key] = str(path)
    env.update(TMP=env["TMPDIR"], TEMP=env["TMPDIR"], DOTNET_CLI_TELEMETRY_OPTOUT="1",
               DOTNET_NOLOGO="1", DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1")
    (output / "logs").mkdir()
    return output, env


def run_logged(command: list[str], *, cwd: Path, env: dict[str, str], timeout: float | None,
               log: Path, godot: bool = False, echo: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        result = run_process(command, cwd=cwd, env=env, timeout=timeout, capture=True)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        parts = [part.decode("utf-8", errors="replace") if isinstance(part, bytes) else part
                 for part in (error.output, error.stderr) if part]
        log.write_text("\n".join(parts), encoding="utf-8")
        raise
    transcript = (result.stdout or "") + (result.stderr or "")
    log.write_text(transcript, encoding="utf-8")
    if echo and result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n", flush=True)
    if echo and result.stderr:
        print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n", flush=True)
    # Godot may finish editor imports with exit 0 even when a resource script failed to parse.
    if godot and re.search(r"(?m)^(?:SCRIPT ERROR:|ERROR:)", transcript):
        raise RuntimeError(f"Godot reported an error; see {log}")
    return result


def verify_toolchain(pins: dict[str, Any], shared_lock: Path, requested_engine: str,
                     env: dict[str, str], output: Path, platforms: list[str]) -> tuple[Path, Path]:
    if pins.get("schemaVersion") != 1:
        raise ValueError("Unsupported companion toolchain pin schema")
    shared = read_json(shared_lock)
    data_root = Path(shared["paths"]["dataRoot"].replace("${HOME}", str(Path.home()))).expanduser()
    archives = {entry["id"]: entry for entry in shared["archives"]}
    installs: dict[str, Path] = {}
    for name in ("engine", "templates"):
        pin = pins[name]
        actual = archives.get(pin["archiveId"], {})
        for key in ("version", "file", "installDirectory"):
            if actual.get(key) != pin[key]:
                raise RuntimeError(f"Shared toolchain {name} {key} differs from companion pin; review before adoption")
        if actual.get("digests", {}).get("sha256") != pin["archiveSha256"]:
            raise RuntimeError(f"Shared toolchain {name} archive digest differs from companion pin")
        install = data_root / pin["installDirectory"]
        marker = read_json(install / ".game-pipeline-source.json")
        if (marker.get("archiveId") != pin["archiveId"] or marker.get("archiveVersion") != pin["version"]
                or marker.get("archiveFile") != pin["file"]
                or marker.get("archiveDigests") != actual["digests"]):
            raise RuntimeError(f"Shared toolchain {name} installation provenance differs from its lock")
        installs[name] = install.resolve(strict=True)
    expected_engine = installs["engine"] / pins["engine"]["executable"]
    located = shutil.which(os.path.expanduser(requested_engine))
    if located is None:
        raise RuntimeError(f"Pinned Godot .NET executable not found: {requested_engine}")
    engine = Path(located).resolve(strict=True)
    if engine != expected_engine:
        raise RuntimeError(f"Expected shared Godot .NET at {expected_engine}; found {engine}")
    if sha256(engine) != pins["engine"]["executableSha256"]:
        raise RuntimeError("Installed Godot .NET binary differs from companion SHA-256 pin")
    if sha256(installs["engine"] / pins["engine"]["sdkPackage"]) != pins["engine"]["sdkPackageSha256"]:
        raise RuntimeError("Bundled Godot .NET SDK differs from its companion pin")
    marker = read_json(installs["engine"] / ".game-pipeline-source.json")
    if marker.get("payloadSha256") != pins["engine"]["payloadSha256"]:
        raise RuntimeError("Installed Godot .NET support payload differs from its companion pin")
    run_logged([sys.executable, str(shared_lock.parent / "scripts/linux_toolchain.py"), "verify-install",
                "--lock", str(shared_lock), "--repo-root", str(shared_lock.parent),
                "--archive-id", pins["engine"]["archiveId"], "--root", str(installs["engine"])],
               cwd=shared_lock.parent, env=env, timeout=60, log=output / "logs/engine-payload.log", echo=False)
    version = run_logged([str(engine), "--version"], cwd=COMPANION, env=env, timeout=30,
                         log=output / "logs/engine-version.log").stdout.strip()
    if version != pins["engineVersion"]:
        raise RuntimeError(f"Expected Godot {pins['engineVersion']}; found {version!r}")
    templates = installs["templates"]
    selected = ["version.txt", *(pins["templates"]["releaseFiles"][name] for name in platforms)]
    for filename in selected:
        path = templates / filename
        if path.is_symlink() or not path.is_file() or sha256(path) != pins["templates"]["fileSha256"][filename]:
            raise RuntimeError(f"Installed export template differs from companion SHA-256 pin: {filename}")
    if (templates / "version.txt").read_text(encoding="utf-8").strip() != pins["templateVersion"]:
        raise RuntimeError("Installed export template version differs from companion pin")
    sdk = next((entry for entry in shared["managedTools"] if entry["id"] == "dotnetSdk8"), {})
    if sdk.get("exactVersion") != pins["dotnet"]["sdkVersion"]:
        raise RuntimeError("Shared companion build SDK differs from companion pin")
    return engine, templates


def check_code_only(source_root: Path) -> None:
    """Refuse GDScript, saved resources and any scene beyond a one-node script wrapper."""
    for path in sorted(source_root.rglob("*")):
        relative = path.relative_to(source_root)
        if any(part in EXCLUDED_DIRECTORIES for part in relative.parts) or not path.is_file():
            continue
        if path.suffix in EDITOR_ONLY_SUFFIXES:
            raise RuntimeError(f"The companion is C# built in code; remove {relative}")
        if path.suffix == ".tscn":
            text = path.read_text(encoding="utf-8")
            resources = re.findall(r'(?m)^\[ext_resource\b[^\]]*\btype="([^"]+)"', text)
            if (len(re.findall(r"(?m)^\[node\b", text)) != 1 or re.search(r"(?m)^\[(?:sub_resource|connection)\b", text)
                    or resources != ["Script"]):
                raise RuntimeError(f"{relative} must be a one-node entry wrapper that only attaches a C# script")


def stage_project(output: Path) -> Path:
    check_code_only(COMPANION)
    project = output / "companion/OnslaughtToolkit.Godot"
    project.mkdir(parents=True)
    metadata = {"packages.lock.json", "global.json", "NuGet.Config"}
    for source in sorted(COMPANION.rglob("*")):
        relative = source.relative_to(COMPANION)
        if any(part in EXCLUDED_DIRECTORIES for part in relative.parts):
            continue
        if source.is_symlink():
            raise RuntimeError(f"Companion project source must not contain symlinks: {relative}")
        if not source.is_file() or (source.suffix not in NATIVE_EXTENSIONS and source.name not in metadata):
            continue
        target = project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for name in ("project.godot", "Main.tscn", "OnslaughtToolkit.Godot.csproj", "OnslaughtToolkit.Godot.sln", "global.json", "packages.lock.json"):
        if not (project / name).is_file():
            raise RuntimeError(f"Companion project file is missing: {name}")
    safety = output / "OnslaughtCareerEditor.AppCore"
    safety.mkdir()
    for name in (*SAFETY_SOURCES, *LINKED_SOURCES):
        shutil.copyfile(ROOT / "OnslaughtCareerEditor.AppCore" / name, safety / name)
    # The project's own lore (MIT, project-written) is embedded in the assembly as text.
    for folder, pattern in (("lore", "*.md"), ("lore-book", "BOOK.md")):
        (output / folder).mkdir()
        for article in sorted((ROOT / folder).glob(pattern)):
            if article.is_symlink() or not article.is_file():
                raise RuntimeError(f"Lore source must be a regular file: {article}")
            shutil.copyfile(article, output / folder / article.name)
    return project


def dotnet_sdk(pins: dict[str, Any], project: Path, env: dict[str, str], output: Path) -> str:
    dotnet = shutil.which("dotnet")
    if dotnet is None:
        raise RuntimeError("Building the integrated safety boundary requires the pinned .NET SDK")
    version = run_logged([dotnet, "--version"], cwd=project, env=env, timeout=30,
                         log=output / "logs/dotnet-version.log").stdout.strip()
    if version != pins["dotnet"]["sdkVersion"]:
        raise RuntimeError(f"Expected companion build SDK {pins['dotnet']['sdkVersion']}; found {version!r}")
    return dotnet


def build_project(engine: Path, project: Path, pins: dict[str, Any], env: dict[str, str], output: Path) -> None:
    dotnet = dotnet_sdk(pins, project, env, output)
    # A generated local feed route keeps host paths out of the tracked project. The official
    # Microsoft feed supplies only pinned framework/runtime packs for normal Godot exports.
    from xml.sax.saxutils import escape
    feed = engine.parent / "GodotSharp/Tools/nupkgs"
    (project / "NuGet.Config").write_text(
        '<configuration><packageSources><clear/><add key="Godot bundled" value="'
        + escape(str(feed), {'"': '&quot;'})
        + '"/><add key="nuget.org" value="https://api.nuget.org/v3/index.json"/></packageSources></configuration>\n',
        encoding="utf-8")
    csproj = project / "OnslaughtToolkit.Godot.csproj"
    run_logged([dotnet, "restore", str(csproj), "--locked-mode", "--nologo", "-p:NuGetAudit=false"],
               cwd=project, env=env, timeout=180, log=output / "logs/dotnet-restore.log")
    run_logged([dotnet, "build", str(csproj), "--no-restore", "--configuration", "Debug", "--nologo"],
               cwd=project, env=env, timeout=180, log=output / "logs/dotnet-build.log")
    if not (project / ".godot/mono/temp/bin/Debug/OnslaughtToolkit.Godot.dll").is_file():
        raise RuntimeError("Integrated Godot assembly was not produced in the isolated project")


def check_project(engine: Path, project: Path, env: dict[str, str], output: Path) -> None:
    # The C# compiler already checked every script; the import checks the entry scene and settings.
    run_logged([str(engine), "--headless", "--path", str(project), "--import"],
               cwd=project, env=env, timeout=180, log=output / "logs/import.log", godot=True)


def copy_dotnet_notices(pins: dict[str, Any], platform: str, project: Path, package: Path) -> None:
    assets = read_json(project / ".godot/mono/temp/obj/project.assets.json")
    runtime_package = f"microsoft.netcore.app.runtime.{PLATFORMS[platform][0]}/{pins['dotnet']['runtimeVersion']}"
    for source_name, target_name in (("LICENSE.TXT", "DOTNET-LICENSE.txt"),
                                     ("THIRD-PARTY-NOTICES.TXT", "DOTNET-THIRD-PARTY-NOTICES.txt")):
        candidates = [Path(folder) / runtime_package / source_name for folder in assets["packageFolders"]]
        source = next((candidate for candidate in candidates if candidate.is_file()), None)
        if source is None:
            raise RuntimeError(f"Pinned .NET runtime redistribution notice is missing: {source_name}")
        shutil.copyfile(source, package / target_name)


def prepare_package_licenses(engine: Path, project: Path, env: dict[str, str], output: Path) -> Path:
    # A development-build C# entry prints the pinned engine's notices; it never enters an export.
    result = run_logged([str(engine), "--headless", "--no-header", "--path", str(project),
                         "--script", "res://Development/LicenseMetadata.cs"],
                        cwd=project, env=env, timeout=30, log=output / "logs/godot-license-metadata.json",
                        godot=True, echo=False)
    notices = json.loads(result.stdout)
    if not notices.get("license") or not notices.get("components") or not notices.get("licenses"):
        raise RuntimeError("Pinned Godot did not supply its redistribution license metadata")
    licenses = output / "package-licenses"
    licenses.mkdir()
    shutil.copyfile(MIT_LICENSE, licenses / "LICENSE.txt")
    (licenses / "GODOT-LICENSE.txt").write_text(notices.pop("license") + "\n", encoding="utf-8")
    (licenses / "GODOT-THIRD-PARTY-NOTICES.json").write_text(
        json.dumps(notices, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return licenses


def copy_fixture(source: Path, output: Path) -> Path:
    if not stat.S_ISREG(source.stat().st_mode):
        raise RuntimeError(f"Save fixture must be a regular file: {source}")
    target = output / "inputs/source-copy.bes"
    target.parent.mkdir()
    shutil.copyfile(source, target)
    if sha256(source) != sha256(target):
        raise RuntimeError("Owned fixture copy did not match the selected input")
    return target


def export_platform(engine: Path, project: Path, templates: Path, pins: dict[str, Any], platform: str,
                    env: dict[str, str], output: Path, licenses: Path) -> Path:
    template_link = Path(env["XDG_DATA_HOME"]) / "godot/export_templates" / pins["templateVersion"]
    template_link.parent.mkdir(parents=True, exist_ok=True)
    if not template_link.exists():
        template_link.symlink_to(templates, target_is_directory=True)
    _, preset, filename = PLATFORMS[platform]
    package = output / "packages" / platform
    package.mkdir(parents=True)
    executable = package / filename
    run_logged([str(engine), "--headless", "--path", str(project), "--export-release", preset, str(executable)],
               cwd=project, env=env, timeout=300, log=output / f"logs/export-{platform}.log", godot=True)
    if not executable.is_file() or not executable.with_suffix(".pck").is_file():
        raise RuntimeError(f"Godot export did not produce an executable and PCK for {platform}")
    configs = list(package.rglob("OnslaughtToolkit.Godot.runtimeconfig.json"))
    if len(configs) != 1:
        raise RuntimeError("Godot export must include one integrated application runtime configuration")
    config = read_json(configs[0])["runtimeOptions"]
    if config.get("framework") or config.get("frameworks") or not any(
            item.get("name") == "Microsoft.NETCore.App" and item.get("version") == pins["dotnet"]["runtimeVersion"]
            for item in config.get("includedFrameworks", [])):
        raise RuntimeError("Godot export did not bundle the pinned self-contained .NET runtime")
    assemblies = list(package.rglob("OnslaughtToolkit.Godot.dll"))
    if len(assemblies) != 1 or not list(package.rglob("GodotSharp.dll")):
        raise RuntimeError("Godot export is missing its integrated managed assemblies")
    if any(namespace in assemblies[0].read_bytes() for namespace in DEVELOPMENT_NAMESPACES):
        raise RuntimeError("Contract tests or development entries leaked into a release export")
    if (package / "file-bridge").exists() or any("TransactionTests" in path.name or "FileBridge" in path.name
                                                for path in package.rglob("*")):
        raise RuntimeError("Obsolete helper or development harness leaked into a production export")
    copy_dotnet_notices(pins, platform, project, package)
    for license_file in licenses.iterdir():
        shutil.copyfile(license_file, package / license_file.name)
    (package / "README.txt").write_text(
        f"Onslaught Toolkit — {platform} package\n\n"
        f"Run {filename} with its .pck file and Godot data directory kept beside it.\n"
        f"Godot {pins['engineVersion']} runs the companion, a C# application built in code.\n"
        "Its file-safety boundary runs inside the same process; no helper process is used.\n"
        f"It bundles Microsoft.NETCore.App {pins['dotnet']['runtimeVersion']}; no installed .NET runtime is needed.\n"
        "The application MIT license, Godot notices and .NET notices are included here.\n"
        "This package contains no retail assets or saves. Cross-export is not Windows execution acceptance.\n",
        encoding="utf-8")
    # A package inventory records the concrete cross-export, without claiming platform execution.
    inventory = {str(path.relative_to(package)): sha256(path) for path in sorted(package.rglob("*")) if path.is_file()}
    (package / "package-sha256.json").write_text(json.dumps({
        "platform": platform, "godotVersion": pins["engineVersion"],
        "dotnetRuntime": pins["dotnet"]["runtimeVersion"], "files": inventory,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Companion {platform} package: {package}", flush=True)
    return package


def capture_screens(project: Path, fixture: Path, offscreen_tool: str, sizes: str, timeout: float | None,
                    env: dict[str, str], output: Path, script: str = "Development/ScreenCapture.cs",
                    extra: list[str] | None = None) -> Path:
    # godot-offscreen renders on a hidden Hyprland output behind the machine-wide GPU lock;
    # the capture entry draws each screen through fixed-size SubViewports.
    offscreen = shutil.which(os.path.expanduser(offscreen_tool))
    if offscreen is None:
        raise RuntimeError(f"godot-offscreen was not found: {offscreen_tool}")
    if not re.fullmatch(r"[1-9][0-9]{2,3}x[1-9][0-9]{2,3}(,[1-9][0-9]{2,3}x[1-9][0-9]{2,3})*", sizes):
        raise ValueError("--sizes must list WIDTHxHEIGHT pairs, for example 1280x800,1920x1080")
    entry = Path(script)
    if entry.is_absolute() or ".." in entry.parts or entry.suffix != ".cs" or not (project / entry).is_file():
        raise RuntimeError("--capture-script must name an existing relative C# capture entry")
    captures = output / "captures"
    run_logged([offscreen, "--path", str(project), "--qa", str(output / "offscreen"),
                "--timeout", str(int(timeout or 900)), "--done-marker", "^CAPTURES_DONE", "--",
                "--script", "res://" + entry.as_posix(), "--",
                f"--output={captures}", f"--fixture={fixture}", f"--sizes={sizes}", *(extra or [])],
               cwd=project, env=env, timeout=None, log=output / "logs/capture.log", godot=True)
    shots = sorted(captures.glob("*.png"))
    if not shots:
        raise RuntimeError("The capture run produced no screens")
    print(f"Companion captures: {len(shots)} screens in {captures}", flush=True)
    return captures


def companion_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "build", "test", "run", "export", "capture"))
    parser.add_argument("--engine", default="~/.local/bin/godot48-mono")
    parser.add_argument("--shared-lock", type=Path, help="existing game_pipeline_shared/toolchain.linux.lock.json")
    parser.add_argument("--platform", choices=("linux", "windows", "both"), default="both", help="export target")
    parser.add_argument("--fixture", type=Path, default=FIXTURE, help="read-only input copied into this test invocation")
    parser.add_argument("--script", default="Tests/CompanionTestRunner.cs", help="project C# test entry (a SceneTree)")
    parser.add_argument("--timeout", type=float, help="test or run timeout in seconds; test defaults to 120")
    parser.add_argument("--engine-arg", action="append", default=[], help="additional run argument (use --engine-arg=--headless)")
    parser.add_argument("--sizes", default="1280x800,1920x1080", help="capture sizes, WIDTHxHEIGHT[,...]")
    parser.add_argument("--offscreen", default="~/.local/bin/godot-offscreen", help="shared hidden-output GPU runner")
    parser.add_argument("--capture-script", default="Development/ScreenCapture.cs", help="C# capture entry (a SceneTree)")
    parser.add_argument("--capture-arg", action="append", default=[], help="argument for the capture entry, e.g. --capture-arg=--steam-root=DIR")
    args = parser.parse_args(argv)
    if not sys.platform.startswith("linux"):
        parser.error("this development launcher requires Linux; exported Windows execution requires Windows acceptance")
    if args.timeout is not None and (not math.isfinite(args.timeout) or args.timeout <= 0):
        parser.error("--timeout must be finite and positive")
    if args.engine_arg and args.mode != "run":
        parser.error("--engine-arg is available only for run")
    interrupted = signal.SIGINT

    def interrupt(signum: int, _frame: object) -> None:
        nonlocal interrupted
        interrupted = signum
        raise KeyboardInterrupt

    previous = signal.signal(signal.SIGTERM, interrupt)
    try:
        canonical = canonical_root()
        output, env = allocate_output(canonical / "local-data/companion", args.mode)
        print(f"Companion output: {output}", flush=True)
        pins = read_json(COMPANION / "toolchain.json")
        platforms = (["linux", "windows"] if args.platform == "both" else [args.platform]) if args.mode == "export" else []
        shared_lock = args.shared_lock or Path.home() / "Projects/game-dev/game_pipeline_shared/toolchain.linux.lock.json"
        engine, templates = verify_toolchain(pins, shared_lock, args.engine, env, output, platforms)
        project = stage_project(output)
        build_project(engine, project, pins, env, output)
        check_project(engine, project, env, output)
        if args.mode in ("check", "build"):
            return 0
        if args.mode == "capture":
            capture_screens(project, copy_fixture(args.fixture, output), args.offscreen, args.sizes, args.timeout, env,
                            output, args.capture_script, args.capture_arg)
            return 0
        if args.mode == "export":
            licenses = prepare_package_licenses(engine, project, env, output)
            for platform in platforms:
                export_platform(engine, project, templates, pins, platform, env, output, licenses)
            return 0
        command = [str(engine), "--path", str(project), "--log-file", str(output / "logs/godot.log")]
        if args.mode == "test":
            script = Path(args.script)
            if script.is_absolute() or ".." in script.parts or not (project / script).is_file():
                raise RuntimeError("Test script must name an existing relative project script")
            fixture = copy_fixture(args.fixture, output)
            test_output = output / "test-output"
            test_output.mkdir()
            command.extend(["--headless", "--script", "res://" + script.as_posix(), "--",
                            f"--fixture={fixture}", f"--output-dir={test_output}"])
        else:
            command.extend(args.engine_arg)
        run_logged(command, cwd=project, env=env, timeout=args.timeout or (120 if args.mode == "test" else None),
                   log=output / "logs/console.log", godot=True)
        return 0
    except subprocess.TimeoutExpired as error:
        print_process_output(error)
        print(f"Companion process timed out after {error.timeout}s", file=sys.stderr)
        return 124
    except subprocess.CalledProcessError as error:
        print_process_output(error)
        print(f"Companion process exited {error.returncode}: {error.cmd[0]}", file=sys.stderr)
        return error.returncode if error.returncode > 0 else 128 - error.returncode
    except KeyboardInterrupt:
        print("Companion interrupted; owned processes stopped.", file=sys.stderr)
        return 128 + interrupted
    except (OSError, RuntimeError, ValueError, KeyError) as error:
        print(f"Companion failed: {error}", file=sys.stderr)
        return 2
    finally:
        signal.signal(signal.SIGTERM, previous)


if __name__ == "__main__":
    raise SystemExit(companion_main())
