"""Run the primary WinUI lane validation set and shut down build servers.

This wrapper keeps the common validation sequence in one command and avoids
leaving idle MSBuild nodes around after long local runs.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WINDOWS_XAML_PATH_WARNING_ROOT_LENGTH = 140

COMMANDS = [
    [
        "dotnet",
        "build",
        "OnslaughtCareerEditor.WinUI.slnx",
        "--nologo",
    ],
    [
        "dotnet",
        "test",
        "OnslaughtCareerEditor.AppCore.Tests/OnslaughtCareerEditor.AppCore.Tests.csproj",
        "--nologo",
        "--no-build",
        "--no-restore",
    ],
    [
        "dotnet",
        "test",
        "OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj",
        "--nologo",
        "--filter",
        "FullyQualifiedName!~LegacyWpf",
        "--no-build",
        "--no-restore",
    ],
]


def should_warn_about_windows_xaml_path(
    repo_root: Path,
    *,
    platform_name: str = os.name,
) -> bool:
    return (
        platform_name == "nt"
        and len(str(repo_root)) >= WINDOWS_XAML_PATH_WARNING_ROOT_LENGTH
    )


def print_windows_xaml_path_warning(repo_root: Path) -> None:
    print(
        "warning: WinUI validation is running from a long repo/worktree path "
        f"({len(str(repo_root))} characters): {repo_root}",
        file=sys.stderr,
    )
    print(
        "warning: Windows App SDK/XAML compiler intermediate paths can be "
        "sensitive to long source roots.",
        file=sys.stderr,
    )
    print(
        "warning: if this run fails with path-length diagnostics involving "
        "generated XAML or intermediate compiler paths, retry from a shorter "
        "clone/worktree before classifying the failure; unrelated build/test "
        "failures remain real.",
        file=sys.stderr,
    )


def run_command(command: list[str]) -> int:
    print(f"\n$ {' '.join(command)}", flush=True)
    env = os.environ.copy()
    env["MSBUILDDISABLENODEREUSE"] = "1"
    completed = subprocess.run(command, cwd=REPO_ROOT, env=env)
    return completed.returncode


def shutdown_build_servers() -> None:
    print("\n$ dotnet build-server shutdown", flush=True)
    completed = subprocess.run(["dotnet", "build-server", "shutdown"], cwd=REPO_ROOT)
    if completed.returncode != 0:
        print(
            f"warning: dotnet build-server shutdown exited {completed.returncode}",
            file=sys.stderr,
        )


def run_self_test() -> int:
    short_root = Path("C:/src/Onslaught-Career-Editor")
    long_root = Path("C:/src/" + ("deep/" * 25) + "Onslaught-Career-Editor")

    assert not should_warn_about_windows_xaml_path(short_root, platform_name="nt")
    assert should_warn_about_windows_xaml_path(long_root, platform_name="nt")
    assert not should_warn_about_windows_xaml_path(long_root, platform_name="posix")

    assert COMMANDS[0] == [
        "dotnet",
        "build",
        "OnslaughtCareerEditor.WinUI.slnx",
        "--nologo",
    ], "primary lane must build the complete solution exactly once"
    assert len(COMMANDS) == 3, "primary lane must run one build and two test commands"
    for command in COMMANDS[1:]:
        assert "--no-build" in command, "tests must consume the same-run solution build"
        assert "--no-restore" in command, "tests must not repeat the same-run restore"

    print("self-test: PASS", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args == ["--self-test"]:
        return run_self_test()
    if args:
        print("usage: winui_primary_lane_validation.py [--self-test]", file=sys.stderr)
        return 2

    if should_warn_about_windows_xaml_path(REPO_ROOT):
        print_windows_xaml_path_warning(REPO_ROOT)

    try:
        for command in COMMANDS:
            result = run_command(command)
            if result != 0:
                return result
        return 0
    finally:
        shutdown_build_servers()


if __name__ == "__main__":
    raise SystemExit(main())
