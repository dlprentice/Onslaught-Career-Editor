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
    ],
    [
        "dotnet",
        "test",
        "OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj",
        "--nologo",
        "--filter",
        "FullyQualifiedName!~LegacyWpf",
    ],
]


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


def main() -> int:
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
