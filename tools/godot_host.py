#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Shared installed-Godot process support and the companion's Linux launcher.

This module contains no rebuild, retail-data or simulation dependencies.
"""
from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ENGINE_VERSION = "4.7.2.stable.mono.official.ed1daf0bf"
ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "companion/OnslaughtToolkit.Godot"


def _stop_owned_group(process: subprocess.Popen[str]) -> None:
    """Stop descendants too, including children left after the leader exits."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        process.wait()
        return
    deadline = time.monotonic() + 0.5
    while time.monotonic() < deadline:
        process.poll()
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.01)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait()


def run_process(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: float | None,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run one owned Linux process group; preserve output and nonzero exits."""
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        start_new_session=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    timed_out: subprocess.TimeoutExpired | None = None
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        result.check_returncode()
        return result
    except subprocess.TimeoutExpired as error:
        timed_out = error
        raise
    finally:
        try:
            # Also clean up an engine/build tool which exits but leaves workers alive.
            _stop_owned_group(process)
            if timed_out is not None and capture:
                try:
                    stdout, stderr = process.communicate(timeout=1.0)
                except subprocess.TimeoutExpired as drain_error:
                    # An escaped descendant may still hold a pipe. Keep the
                    # latest partial output without turning this into a hang.
                    if drain_error.output is not None:
                        timed_out.output = drain_error.output
                    if drain_error.stderr is not None:
                        timed_out.stderr = drain_error.stderr
                    timed_out.add_note("Owned process group stopped; output drain exceeded one second.")
                except UnicodeError:
                    # Preserve the original byte diagnostics and timeout even
                    # when a tool's final output is not valid text.
                    timed_out.add_note("Owned process group stopped; final output could not be decoded.")
                else:
                    # communicate() normalizes text; TimeoutExpired diagnostics
                    # remain bytes, as in subprocess's public exception contract.
                    encoding = process.encoding or "utf-8"
                    timed_out.output = stdout.encode(encoding) if stdout is not None else None
                    timed_out.stderr = stderr.encode(encoding) if stderr is not None else None
        finally:
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()


def print_process_output(error: subprocess.CalledProcessError | subprocess.TimeoutExpired) -> None:
    """Print captured diagnostics without byte-literal reprs or lost partial lines."""
    for output in (error.output, error.stderr):
        if output:
            text = output.decode("utf-8", errors="replace") if isinstance(output, bytes) else output
            print(text, file=sys.stderr, end="" if text.endswith("\n") else "\n")
    for note in getattr(error, "__notes__", ()):
        print(note, file=sys.stderr)


def engine_path(requested: str) -> Path:
    located = shutil.which(requested)
    if located is None:
        raise RuntimeError(f"Godot Mono executable not found: {requested}")
    engine = Path(located).resolve(strict=True)
    packages = engine.parent / "GodotSharp/Tools/nupkgs"
    if not (packages / "Godot.NET.Sdk.4.7.2.nupkg").is_file():
        raise RuntimeError(f"Godot 4.7.2 bundled SDK package is missing: {packages}")
    return engine

def build_project(project: Path, engine: Path, env: dict[str, str]) -> None:
    dotnet = shutil.which("dotnet")
    if dotnet is None:
        raise RuntimeError("dotnet is not installed or not on PATH")
    projects = list(project.glob("*.csproj"))
    if len(projects) != 1:
        raise RuntimeError(f"Expected one Godot C# project in {project}")
    packages = str(engine.parent / "GodotSharp/Tools/nupkgs")
    run_process([dotnet, "restore", str(projects[0]), "--source", packages,
                 "--locked-mode", "--nologo", "-p:NuGetAudit=false"],
                cwd=project, env=env, timeout=1200)
    run_process([dotnet, "build", str(projects[0]), "--no-restore", "--nologo"],
                cwd=project, env=env, timeout=1200)


def companion_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or run the Godot Save Lab on Linux.")
    parser.add_argument("mode", choices=("build", "run"), nargs="?", default="run")
    parser.add_argument("--engine", default="godot-mono")
    parser.add_argument("--no-build", action="store_true")
    parser.add_argument("--timeout", type=float, help="optional runtime limit in seconds")
    parser.add_argument("--engine-arg", action="append", default=[])
    args = parser.parse_args(argv)
    if not sys.platform.startswith("linux"):
        parser.error("this launcher requires Linux; native Windows acceptance is pending")
    if args.mode == "build" and (args.no_build or args.engine_arg or args.timeout):
        parser.error("build does not accept runtime options")
    if args.timeout is not None and not 0 < args.timeout < float("inf"):
        parser.error("--timeout must be finite and positive")

    interrupted = signal.SIGINT
    def interrupt(signum: int, _frame: object) -> None:
        nonlocal interrupted
        interrupted = signum
        raise KeyboardInterrupt
    previous = signal.signal(signal.SIGTERM, interrupt)
    try:
        # Worktrees share operational data with the canonical checkout, not a copied lab.
        git_env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        common = Path(subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            text=True, env=git_env).strip())
        owner = common.parent / "local-data/companion"
        owner.mkdir(parents=True, exist_ok=True)
        for name in ("user-data", "cache"):
            (owner / name).mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="scratch-", dir=owner) as scratch:
            env = dict(os.environ, TMPDIR=scratch, TMP=scratch, TEMP=scratch,
                       XDG_DATA_HOME=str(owner / "user-data"), XDG_CACHE_HOME=str(owner / "cache"),
                       DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_NOLOGO="1")
            engine = engine_path(args.engine)
            version = run_process([str(engine), "--version"], cwd=COMPANION, env=env,
                                  timeout=30, capture=True).stdout.strip()
            if version != ENGINE_VERSION:
                raise RuntimeError(f"expected Godot {ENGINE_VERSION}; found {version!r}")
            if not args.no_build:
                build_project(COMPANION, engine, env)
            if args.mode == "run":
                output = Path(tempfile.mkdtemp(prefix="run-", dir=owner))
                print(f"Save Lab output: {output}", flush=True)
                run_process([str(engine), "--path", str(COMPANION),
                             "--log-file", str(output / "godot.log"), *args.engine_arg],
                            cwd=COMPANION, env=env, timeout=args.timeout)
        return 0
    except subprocess.TimeoutExpired as error:
        print_process_output(error)
        print(f"Godot process timed out after {error.timeout}s", file=sys.stderr)
        return 124
    except subprocess.CalledProcessError as error:
        print_process_output(error)
        print(f"Godot process exited {error.returncode}: {error.cmd[0]}", file=sys.stderr)
        return error.returncode if error.returncode > 0 else 128 - error.returncode
    except KeyboardInterrupt:
        print("Godot interrupted; owned processes stopped.", file=sys.stderr)
        return 128 + interrupted
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Godot launch failed: {error}", file=sys.stderr)
        return 2
    finally:
        signal.signal(signal.SIGTERM, previous)


if __name__ == "__main__":
    raise SystemExit(companion_main())
