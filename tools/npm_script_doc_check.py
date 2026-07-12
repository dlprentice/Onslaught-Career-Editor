#!/usr/bin/env python3
"""Validate that documented npm run commands point at real package scripts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
COMMAND_PATTERN = re.compile(
    r"npm(?:\s+--workspace\s+(?P<workspace>[^\s`'\"<>]+))?\s+run\s+(?P<script>[A-Za-z0-9:_-]+)"
)
SKIP_EXACT = {
    "onslaught_codex_directive.md",
    "release/readiness/ralph_loop_goal_evidence_2026-05-01.md",
    "release/readiness/release_candidate_evidence_2026-04-30.md",
    "release/readiness/ux_goal_evidence_2026-05-01.md",
}
SKIP_PREFIXES = (
    "release/readiness/private_runtime_evidence/",
)
ACTIVE_MARKDOWN_FILES = (
    "AGENTS.md",
    "COLLABORATION.md",
    "CONTRIBUTING.md",
    "CURRENT_CAPABILITIES.md",
    "LOCAL_LAB_OVERLAY.md",
    "README.MD",
    "README.RELEASE.md",
    "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
    "VALIDATION.md",
    "goal.md",
    "goal.policy.md",
    "rebuild/AGENTS.md",
    "rebuild/README.md",
    "roadmap/original-binary-online-multiplayer-feasibility.md",
    "roadmap/repo-structure-and-archive-map.md",
    "release/readiness/LOCAL_SIGNOFF_COMMANDS.md",
    "release/readiness/PUBLIC_SIGNOFF_COMMANDS.md",
    "release/readiness/public_AGENTS.md",
    "tools/README.md",
)


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def tracked_markdown_files(root: Path = ROOT) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            "*.md",
        ],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    raw_paths = result.stdout.decode("utf-8", errors="replace").split("\0")
    return [normalize_path(path) for path in raw_paths if path]


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def package_scripts(path: Path) -> set[str]:
    package = load_json(path)
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        return set()
    return {str(key) for key in scripts}


def workspace_script_map() -> dict[str, set[str]]:
    packages: dict[str, set[str]] = {}
    package_paths = [
        *ROOT.glob("apps/*/package.json"),
        *ROOT.glob("packages/*/package.json"),
        *ROOT.glob("archive/electron-workbench/apps/*/package.json"),
        *ROOT.glob("archive/electron-workbench/packages/*/package.json"),
    ]
    for package_path in package_paths:
        package = load_json(package_path)
        name = package.get("name")
        if isinstance(name, str):
            packages[name] = package_scripts(package_path)
    return packages


def should_skip_markdown(path: str) -> bool:
    return path in SKIP_EXACT or any(path.startswith(prefix) for prefix in SKIP_PREFIXES)


def markdown_files_for_scope(
    root: Path,
    scope: str,
    tracked_paths: tuple[str, ...] | list[str] | None = None,
) -> list[str]:
    tracked = list(tracked_paths) if tracked_paths is not None else tracked_markdown_files(root)
    active_existing = [path for path in ACTIVE_MARKDOWN_FILES if (root / path).is_file()]
    if scope == "all":
        return sorted(
            {
                path
                for path in (*tracked, *active_existing)
                if not should_skip_markdown(path)
            }
        )
    active = set(ACTIVE_MARKDOWN_FILES)
    return sorted(
        {
            path
            for path in (*tracked, *active_existing)
            if path in active and not should_skip_markdown(path)
        }
    )


def scan_markdown(root: Path, path: str) -> list[tuple[int, str | None, str, str]]:
    text = (root / path).read_text(encoding="utf-8", errors="replace")
    matches: list[tuple[int, str | None, str, str]] = []
    for match in COMMAND_PATTERN.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        matches.append((line, match.group("workspace"), match.group("script"), match.group(0)))
    return matches


def documented_command_errors(
    root: Path,
    markdown_files: list[str],
    root_scripts: set[str],
    workspace_scripts: dict[str, set[str]],
) -> tuple[list[str], int]:
    errors: list[str] = []
    command_count = 0
    for path in markdown_files:
        for line, workspace, script, command in scan_markdown(root, path):
            command_count += 1
            if workspace:
                scripts = workspace_scripts.get(workspace)
                if scripts is None:
                    errors.append(f"{path}:{line}: unknown npm workspace in documented command: {workspace}")
                elif script not in scripts:
                    errors.append(f"{path}:{line}: missing workspace npm script `{script}` in {workspace}: {command}")
            elif script not in root_scripts:
                errors.append(f"{path}:{line}: missing root npm script `{script}`: {command}")
    return errors, command_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scope",
        choices=("active", "all"),
        default="active",
        help="Validate current front-door docs or the complete historical Markdown corpus.",
    )
    args = parser.parse_args()

    root_scripts = package_scripts(ROOT / "package.json")
    workspace_scripts = workspace_script_map()
    markdown_files = markdown_files_for_scope(ROOT, args.scope)
    errors, command_count = documented_command_errors(
        ROOT, markdown_files, root_scripts, workspace_scripts
    )

    if errors:
        print("NPM script documentation check: FAIL")
        for error in errors[:200]:
            print(f"- {error}")
        if len(errors) > 200:
            print(f"- ... ({len(errors) - 200} more)")
        return 1

    print("NPM script documentation check: PASS")
    print(f"Scope: {args.scope}")
    print(f"Markdown files checked: {len(markdown_files)}")
    print(f"Documented npm run commands checked: {command_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
