#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build and launch First Flight with the installed, pinned Linux Godot Mono."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

import materialize_retail_assets as materializer


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from godot_host import ENGINE_VERSION, build_project, engine_path as _engine_path, run_process
PROJECT = Path("rebuild/OnslaughtRebuild.Godot")
PREPARATION_TIMEOUT = 1200


def _prepare(
    game_root: Path,
    media_root: Path | None,
    *,
    cwd: Path,
    env: dict[str, str],
) -> None:
    script = str(materializer.ROOT / "rebuild/tools/materialize_retail_assets.py")
    if not materializer._outputs_ready():
        run_process(
            [sys.executable, script, "--host-default-work-root", "--game-root", str(game_root)],
            cwd=cwd, env=env, timeout=PREPARATION_TIMEOUT,
        )
    if media_root is not None:
        # Startup media has its own cache check and cannot take a work-root flag.
        run_process(
            [sys.executable, script, "--startup-media", "--game-root", str(game_root),
             "--startup-media-root", str(media_root)],
            cwd=cwd, env=env, timeout=PREPARATION_TIMEOUT,
        )


def _output_directory(canonical: Path, requested: Path | None, mode: str) -> Path:
    owner = canonical / "local-data/first-flight"
    owner.mkdir(parents=True, exist_ok=True)
    if requested is None:
        return Path(tempfile.mkdtemp(prefix=f"{mode}-", dir=owner))
    output = requested.expanduser().absolute()
    if not output.resolve().is_relative_to((canonical / "local-data").resolve()):
        raise RuntimeError("--output-root must be below the canonical checkout's local-data")
    # Each invocation owns fresh output; never overwrite an earlier capture.
    output.mkdir(parents=True, exist_ok=False)
    return output


def _runtime_command(
    engine: Path,
    project: Path,
    media_root: Path,
    output: Path,
    mode: str,
    engine_args: list[str],
    user_args: list[str],
) -> list[str]:
    reserved = ("--startup-media", "--report", "--capture-dir")
    if any(arg == flag or arg.startswith(flag + "=") for arg in user_args for flag in reserved):
        raise RuntimeError("startup-media, report, and capture-dir are owned by the launcher")
    command = [str(engine), "--path", str(project), "--windowed",
               "--log-file", str(output / "first-flight.log")]
    if mode in ("smoke", "capture"):
        command.extend(("--fixed-fps", "60"))
    command.extend(engine_args)
    command.extend(("--", f"--startup-media={media_root}"))
    if mode == "smoke":
        command.extend(("--smoke", f"--report={output / 'first-flight-smoke.json'}"))
    elif mode == "capture":
        command.append(f"--capture-dir={output}")
    command.extend(user_args)
    return command


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    split = arguments.index("--") if "--" in arguments else len(arguments)
    user_args = arguments[split + 1:]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("build", "run", "smoke", "capture"), nargs="?", default="run")
    parser.add_argument("--engine", default="godot-mono", help="installed Godot Mono executable")
    parser.add_argument("--game-root", type=Path, help="retail installation; otherwise discover Linux Steam")
    parser.add_argument("--no-build", action="store_true", help="run the existing managed build")
    parser.add_argument("--no-prepare", action="store_true",
                        help="reuse prepared assets and startup media without validation or materialization")
    parser.add_argument("--output-root", type=Path, help="fresh directory below canonical local-data")
    parser.add_argument("--timeout", type=float, help="runtime limit in seconds (smoke: 75; capture: 300)")
    parser.add_argument("--engine-arg", action="append", default=[], help="Godot option; use --engine-arg=VALUE")
    args = parser.parse_args(arguments[:split])
    if not sys.platform.startswith("linux"):
        parser.error("this launcher requires Linux; Windows keeps its existing PowerShell launchers")
    if args.timeout is not None and (args.timeout <= 0 or not args.timeout < float("inf")):
        parser.error("--timeout must be a finite positive number")
    if args.mode == "build" and (args.no_build or user_args or args.engine_arg):
        parser.error("build does not accept --no-build or runtime arguments")

    interrupted = signal.SIGINT

    def interrupt(signum: int, _frame: object) -> None:
        nonlocal interrupted
        interrupted = signum
        raise KeyboardInterrupt

    prior_term = signal.signal(signal.SIGTERM, interrupt)
    try:
        canonical = materializer._canonical_repository_root()
        project = materializer.ROOT / PROJECT
        engine = _engine_path(args.engine)
        game_root = None
        if not args.no_prepare:
            game_root = materializer._resolve_game_root(
                args.game_root.expanduser().absolute() if args.game_root else None
            )
        media_root = None
        if args.mode != "build":
            media_root = materializer._resolve_work_root(
                materializer._default_startup_media_root(), game_root=game_root
            )
        scratch_owner = canonical / "local-data/first-flight"
        scratch_owner.mkdir(parents=True, exist_ok=True)
        for child in ("user-data", "cache"):
            (scratch_owner / child).mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="scratch-", dir=scratch_owner) as scratch:
            env = dict(os.environ, TMPDIR=scratch, TMP=scratch, TEMP=scratch,
                       XDG_DATA_HOME=str(scratch_owner / "user-data"),
                       XDG_CACHE_HOME=str(scratch_owner / "cache"),
                       DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_NOLOGO="1")
            version = run_process([str(engine), "--version"], cwd=project, env=env,
                                  timeout=30, capture=True).stdout.strip()
            if version != ENGINE_VERSION:
                raise RuntimeError(f"expected Godot {ENGINE_VERSION}; found {version!r}")
            if not args.no_prepare:
                assert game_root is not None
                _prepare(game_root, media_root, cwd=materializer.ROOT, env=env)
            if not args.no_build:
                build_project(project, engine, env)
            if args.mode == "build":
                return 0
            assert media_root is not None
            output = _output_directory(canonical, args.output_root, args.mode)
            command = _runtime_command(engine, project, media_root, output, args.mode,
                                       args.engine_arg, user_args)
            print(f"First Flight {args.mode} output: {output}", flush=True)
            timeout = args.timeout
            if timeout is None:
                timeout = {"smoke": 75, "capture": 300}.get(args.mode)
            run_process(command, cwd=project, env=env, timeout=timeout)
            return 0
    except subprocess.TimeoutExpired as error:
        print(f"First Flight timed out after {error.timeout}s: {error.cmd[0]}", file=sys.stderr)
        return 124
    except subprocess.CalledProcessError as error:
        if error.stdout:
            print(error.stdout, file=sys.stderr, end="")
        if error.stderr:
            print(error.stderr, file=sys.stderr, end="")
        print(f"First Flight process exited {error.returncode}: {error.cmd[0]}", file=sys.stderr)
        return error.returncode if error.returncode > 0 else 128 - error.returncode
    except KeyboardInterrupt:
        print("First Flight interrupted; owned processes stopped.", file=sys.stderr)
        return 128 + interrupted
    except (OSError, RuntimeError, ValueError) as error:
        print(f"First Flight failed: {error}", file=sys.stderr)
        return 2
    finally:
        signal.signal(signal.SIGTERM, prior_term)


if __name__ == "__main__":
    raise SystemExit(main())
