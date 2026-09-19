#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Pinned standard-Godot companion routes with isolated outputs and explicit FileBridge packaging."""
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
BRIDGE_PROJECT = ROOT / "companion/OnslaughtToolkit.FileBridge/OnslaughtToolkit.FileBridge.csproj"
RACE_PROJECT = ROOT / "companion/OnslaughtToolkit.FileBridge/OnslaughtToolkit.FileBridge.TransactionTests.csproj"
BRIDGE_TESTS = ROOT / "companion/tests/test_file_bridge.py"
MIT_LICENSE = ROOT / "LICENSE"
FIXTURE = ROOT / "tests_shared/fixtures/gold_career_save.bin"
NATIVE_EXTENSIONS = {".godot", ".gd", ".uid", ".tscn", ".tres", ".cfg", ".svg", ".png", ".ttf", ".otf"}
EXCLUDED_DIRECTORIES = {".godot", "bin", "obj", "legacy", "reference"}
PLATFORMS = {
    "linux": ("linux-x64", "Linux", "OnslaughtToolkit.x86_64", "OnslaughtToolkit.FileBridge"),
    "windows": ("win-x64", "Windows", "OnslaughtToolkit.exe", "OnslaughtToolkit.FileBridge.exe"),
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
    output = Path(tempfile.mkdtemp(prefix=f"gdscript-{mode}-", dir=owner))
    directories = {
        "TMPDIR": "scratch", "XDG_DATA_HOME": "profile/data", "XDG_CONFIG_HOME": "profile/config",
        "XDG_CACHE_HOME": "profile/cache", "DOTNET_CLI_HOME": "profile/dotnet",
    }
    env = dict(os.environ)
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
        raise RuntimeError(f"Pinned standard Godot executable not found: {requested_engine}")
    engine = Path(located).resolve(strict=True)
    if engine != expected_engine:
        raise RuntimeError(f"Expected shared standard Godot at {expected_engine}; found {engine}")
    if sha256(engine) != pins["engine"]["executableSha256"]:
        raise RuntimeError("Installed standard Godot binary differs from companion SHA-256 pin")
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
    if sdk.get("exactVersion") != pins["fileBridge"]["sdkVersion"]:
        raise RuntimeError("Shared FileBridge build SDK differs from companion pin")
    return engine, templates


def stage_project(output: Path) -> Path:
    project = output / "project"
    project.mkdir()
    for source in sorted(COMPANION.rglob("*")):
        relative = source.relative_to(COMPANION)
        if any(part in EXCLUDED_DIRECTORIES for part in relative.parts):
            continue
        if source.is_symlink():
            raise RuntimeError(f"Native project source must not contain symlinks: {relative}")
        if not source.is_file() or source.suffix not in NATIVE_EXTENSIONS:
            continue
        target = project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    if not (project / "project.godot").is_file() or not (project / "SaveLab.tscn").is_file():
        raise RuntimeError("Native companion project.godot or SaveLab.tscn is missing")
    return project


def check_project(engine: Path, project: Path, env: dict[str, str], output: Path) -> None:
    run_logged([str(engine), "--headless", "--path", str(project), "--import"],
               cwd=project, env=env, timeout=180, log=output / "logs/import.log", godot=True)
    for index, script in enumerate(sorted(project.rglob("*.gd"))):
        if ".godot" in script.relative_to(project).parts:
            continue
        resource = "res://" + script.relative_to(project).as_posix()
        run_logged([str(engine), "--headless", "--path", str(project), "--check-only", "--script", resource],
                   cwd=project, env=env, timeout=60, log=output / f"logs/parse-{index}.log", godot=True)


def publish_managed_tool(pins: dict[str, Any], platform: str, destination: Path,
                         env: dict[str, str], output: Path, project: Path, label: str) -> Path:
    if not project.is_file():
        raise RuntimeError(f"Companion file-safety tool project is missing: {project}")
    dotnet = shutil.which("dotnet")
    if dotnet is None:
        raise RuntimeError("Building FileBridge requires the pinned .NET SDK; exported apps bundle their runtime")
    version = run_logged([dotnet, "--version"], cwd=project.parent, env=env,
                         timeout=30, log=output / f"logs/dotnet-{label}-{platform}-version.log").stdout.strip()
    if version != pins["fileBridge"]["sdkVersion"]:
        raise RuntimeError(f"Expected FileBridge build SDK {pins['fileBridge']['sdkVersion']}; found {version!r}")
    runtime = PLATFORMS[platform][0]
    filename = project.stem + (".exe" if platform == "windows" else "")
    destination.mkdir(parents=True, exist_ok=True)
    build_root = output / "managed-build" / project.stem / runtime
    run_logged([dotnet, "publish", str(project), "--configuration", "Release", "--runtime", runtime,
                "--self-contained", "true", "--output", str(destination), "--nologo",
                f"-p:BaseIntermediateOutputPath={build_root / 'obj'}/",
                f"-p:BaseOutputPath={build_root / 'bin'}/", "-p:NuGetAudit=false"],
               cwd=project.parent, env=env, timeout=600, log=output / f"logs/{label}-{platform}.log")
    executable = destination / filename
    runtime_config = read_json(destination / (project.stem + ".runtimeconfig.json"))["runtimeOptions"]
    bundled_frameworks = runtime_config.get("includedFrameworks", [])
    if (not executable.is_file() or runtime_config.get("framework") or runtime_config.get("frameworks")
            or not any(item.get("name") == "Microsoft.NETCore.App"
                       and item.get("version") == pins["fileBridge"]["runtimeVersion"] for item in bundled_frameworks)):
        raise RuntimeError("FileBridge publish did not produce the pinned self-contained runtime")
    assets = read_json(build_root / "obj/project.assets.json")
    runtime_package = f"microsoft.netcore.app.runtime.{runtime}/{pins['fileBridge']['runtimeVersion']}"
    for source_name, target_name in (("LICENSE.TXT", "DOTNET-LICENSE.txt"),
                                     ("THIRD-PARTY-NOTICES.TXT", "DOTNET-THIRD-PARTY-NOTICES.txt")):
        candidates = [Path(folder) / runtime_package / source_name for folder in assets["packageFolders"]]
        source = next((candidate for candidate in candidates if candidate.is_file()), None)
        if source is None:
            raise RuntimeError(f"Pinned .NET runtime redistribution notice is missing: {source_name}")
        shutil.copyfile(source, destination / target_name)
    return executable


def publish_bridge(pins: dict[str, Any], platform: str, destination: Path,
                   env: dict[str, str], output: Path) -> Path:
    executable = publish_managed_tool(pins, platform, destination, env, output, BRIDGE_PROJECT, "file-bridge")
    if platform == "linux":
        # The source editor can use the same explicit helper without changing project settings.
        cache = COMPANION / ".godot"
        cache.mkdir(exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=cache,
                                         prefix="companion-bridge-", delete=False) as pointer:
            pointer.write(str(executable) + "\n")
        os.replace(pointer.name, cache / "companion_bridge_path.txt")
    return executable


def run_bridge_tests(pins: dict[str, Any], bridge: Path, env: dict[str, str], output: Path) -> None:
    # The race harness is a separate test executable; it never enters a production package.
    harness = publish_managed_tool(pins, "linux", output / "test-tools/race-harness", env,
                                   output, RACE_PROJECT, "transaction-races")
    run_logged([sys.executable, str(BRIDGE_TESTS), "--bridge", str(bridge),
                "--race-harness", str(harness), "--output-root", str(output / "file-bridge-tests")],
               cwd=ROOT, env=env, timeout=180, log=output / "logs/file-bridge-tests.log")


def prepare_package_licenses(engine: Path, project: Path, env: dict[str, str], output: Path) -> Path:
    script = output / "license_metadata.gd"
    script.write_text(
        "extends SceneTree\n\nfunc _initialize() -> void:\n"
        "\tprint(JSON.stringify({\"license\": Engine.get_license_text(), "
        "\"components\": Engine.get_copyright_info(), \"licenses\": Engine.get_license_info()}))\n"
        "\tquit()\n", encoding="utf-8")
    result = run_logged([str(engine), "--headless", "--no-header", "--path", str(project), "--script", str(script)],
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
    _, preset, filename, _ = PLATFORMS[platform]
    package = output / "packages" / platform
    package.mkdir(parents=True)
    publish_bridge(pins, platform, package / "file-bridge", env, output)
    executable = package / filename
    run_logged([str(engine), "--headless", "--path", str(project), "--export-release", preset, str(executable)],
               cwd=project, env=env, timeout=180, log=output / f"logs/export-{platform}.log", godot=True)
    if not executable.is_file() or not executable.with_suffix(".pck").is_file():
        raise RuntimeError(f"Godot export did not produce an executable and PCK for {platform}")
    for license_file in licenses.iterdir():
        shutil.copyfile(license_file, package / license_file.name)
    (package / "README.txt").write_text(
        f"Onslaught Toolkit — {platform} package\n\n"
        f"Run {filename} with its .pck file and file-bridge directory kept beside it.\n"
        f"Godot {pins['engineVersion']} runs the GDScript scenes and save-domain code.\n"
        "FileBridge is the explicit OS file-identity and verified no-replace publication helper.\n"
        f"It bundles Microsoft.NETCore.App {pins['fileBridge']['runtimeVersion']}; no installed .NET runtime is needed.\n"
        "The application MIT license and Godot notices are included here; .NET notices are in file-bridge.\n"
        "This package contains no retail assets or saves. Cross-export is not Windows execution acceptance.\n",
        encoding="utf-8")
    # A package inventory records the concrete cross-export, without claiming platform execution.
    inventory = {str(path.relative_to(package)): sha256(path) for path in sorted(package.rglob("*")) if path.is_file()}
    (package / "package-sha256.json").write_text(json.dumps({
        "platform": platform, "godotVersion": pins["engineVersion"],
        "fileBridgeRuntime": pins["fileBridge"]["runtimeVersion"], "files": inventory,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Companion {platform} package: {package}", flush=True)
    return package


def companion_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "build", "test", "run", "export"))
    parser.add_argument("--engine", default="~/.local/bin/godot48")
    parser.add_argument("--shared-lock", type=Path, help="existing game_pipeline_shared/toolchain.linux.lock.json")
    parser.add_argument("--platform", choices=("linux", "windows", "both"), default="both", help="export target")
    parser.add_argument("--fixture", type=Path, default=FIXTURE, help="read-only input copied into this test invocation")
    parser.add_argument("--script", default="tests/test_save_lab.gd", help="project test script")
    parser.add_argument("--bridge", type=Path, help="reuse an explicitly selected self-contained Linux FileBridge for test/run")
    parser.add_argument("--timeout", type=float, help="test or run timeout in seconds; test defaults to 120")
    parser.add_argument("--engine-arg", action="append", default=[], help="additional run argument (use --engine-arg=--headless)")
    args = parser.parse_args(argv)
    if not sys.platform.startswith("linux"):
        parser.error("this development launcher requires Linux; exported Windows execution requires Windows acceptance")
    if args.timeout is not None and (not math.isfinite(args.timeout) or args.timeout <= 0):
        parser.error("--timeout must be finite and positive")
    if args.bridge and args.mode not in ("test", "run"):
        parser.error("--bridge is a development test/run option")
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
        check_project(engine, project, env, output)
        if args.mode == "check":
            return 0
        if args.mode == "export":
            licenses = prepare_package_licenses(engine, project, env, output)
            for platform in platforms:
                export_platform(engine, project, templates, pins, platform, env, output, licenses)
            return 0
        if args.bridge:
            bridge = args.bridge.resolve(strict=True)
            if not bridge.is_file() or not os.access(bridge, os.X_OK):
                raise RuntimeError("Selected FileBridge must be an executable file")
        else:
            bridge = publish_bridge(pins, "linux", output / "file-bridge", env, output)
        env["ONSLAUGHT_FILE_BRIDGE"] = str(bridge)
        if args.mode == "build":
            print(f"FileBridge: {bridge}", flush=True)
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
        if args.mode == "test":
            run_bridge_tests(pins, bridge, env, output)
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
