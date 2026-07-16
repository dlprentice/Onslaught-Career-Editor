#!/usr/bin/env python3
"""Validate public-package npm commands in public-facing docs."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PACKAGE = ROOT / "release" / "readiness" / "public_package.json"
COMMAND_PATTERN = re.compile(r"npm\s+run\s+(?P<script>[A-Za-z0-9:_-]+)")
START_MARKER = "<!-- public-package-commands:start -->"
END_MARKER = "<!-- public-package-commands:end -->"
REQUIRED_MARKED_DOCS = {
    "CONTRIBUTING.md",
    "CURRENT_CAPABILITIES.md",
    "README.MD",
    "README.RELEASE.md",
    "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
    "release/readiness/PUBLIC_SIGNOFF_COMMANDS.md",
}


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def tracked_markdown_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        files = [
            normalize_path(path)
            for path in result.stdout.decode("utf-8", errors="replace").split("\0")
            if path and path.lower().endswith(".md")
        ]
        if files:
            return files
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return [
        normalize_path(str(path.relative_to(ROOT)))
        for path in sorted(ROOT.rglob("*.md"))
        if include_markdown_path(path)
    ]


def include_markdown_path(path: Path) -> bool:
    rel = normalize_path(str(path.relative_to(ROOT)))
    if rel.startswith(".git/"):
        return False
    if rel.startswith("node_modules/"):
        return False
    if rel.startswith("subagents/"):
        return False
    if "/bin/" in rel or "/obj/" in rel:
        return False
    return True


def load_public_scripts(package_path: Path = PUBLIC_PACKAGE) -> set[str]:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        return set()
    return {str(key) for key in scripts}


def iter_marked_blocks(path: str, text: str) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    pos = 0
    while True:
        start = text.find(START_MARKER, pos)
        if start < 0:
            break
        body_start = start + len(START_MARKER)
        end = text.find(END_MARKER, body_start)
        if end < 0:
            start_line = text.count("\n", 0, start) + 1
            raise ValueError(f"{path}:{start_line}: missing {END_MARKER}")
        start_line = text.count("\n", 0, body_start) + 1
        blocks.append((start_line, text[body_start:end]))
        pos = end + len(END_MARKER)
    return blocks


def check_marked_doc_commands(path: str, text: str, public_scripts: set[str]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    blocks = iter_marked_blocks(path, text)
    for block_start_line, block in blocks:
        for match in COMMAND_PATTERN.finditer(block):
            line = block_start_line + block.count("\n", 0, match.start())
            script = match.group("script")
            if script not in public_scripts:
                errors.append(
                    f"{path}:{line}: public-package command references missing public npm script `{script}`"
                )
    return bool(blocks), errors


def check_docs(root: Path = ROOT, package_path: Path = PUBLIC_PACKAGE) -> list[str]:
    public_scripts = load_public_scripts(package_path)
    errors: list[str] = []
    marked_docs: set[str] = set()
    for path in tracked_markdown_files():
        full_path = root / path
        if not full_path.is_file():
            continue
        text = full_path.read_text(encoding="utf-8", errors="replace")
        try:
            has_blocks, doc_errors = check_marked_doc_commands(path, text, public_scripts)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if has_blocks:
            marked_docs.add(path)
        errors.extend(doc_errors)

    missing_docs = sorted(REQUIRED_MARKED_DOCS - marked_docs)
    for path in missing_docs:
        errors.append(f"{path}: missing public-package command marker block")
    return errors


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as raw_tmp:
        temp_root = Path(raw_tmp)
        (temp_root / "release" / "readiness").mkdir(parents=True)
        (temp_root / "release" / "readiness" / "public_package.json").write_text(
            json.dumps({"scripts": {"known": "echo ok"}}),
            encoding="utf-8",
        )
        good = f"{START_MARKER}\n```powershell\nnpm run known\n```\n{END_MARKER}\n"
        bad = f"{START_MARKER}\n```powershell\nnpm run missing\n```\n{END_MARKER}\n"
        try:
            good_has_blocks, good_errors = check_marked_doc_commands("good.md", good, {"known"})
            bad_has_blocks, bad_errors = check_marked_doc_commands("bad.md", bad, {"known"})
            assert good_has_blocks and not good_errors
            assert bad_has_blocks and len(bad_errors) == 1
            assert "missing public npm script `missing`" in bad_errors[0]
        except AssertionError:
            print("Public package doc command self-test: FAIL")
            print("- command validation failed")
            return 1
    print("Public package doc command self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    errors = check_docs()
    if errors:
        print("Public package doc command check: FAIL")
        for error in errors[:200]:
            print(f"- {error}")
        if len(errors) > 200:
            print(f"- ... ({len(errors) - 200} more)")
        return 1
    print("Public package doc command check: PASS")
    print(f"Marked public docs checked: {len(REQUIRED_MARKED_DOCS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
