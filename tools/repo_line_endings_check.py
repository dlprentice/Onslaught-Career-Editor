#!/usr/bin/env python3
"""Audit and optionally normalize explicit repo line-ending rules.

Git's text normalization can make a working tree look clean even when local
files use CRLF or mixed endings. This check reads the explicit eol rules from
`git ls-files --eol` and verifies the bytes currently on disk.
"""

from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class EolEntry:
    path: str
    expected: str


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def expected_from_eol_line(line: str) -> EolEntry | None:
    if "\t" not in line:
        return None
    metadata, path = line.split("\t", 1)
    if "attr/text eol=lf" in metadata:
        expected = "lf"
    elif "attr/text eol=crlf" in metadata:
        expected = "crlf"
    else:
        return None
    return EolEntry(normalize_path(path), expected)


def explicit_eol_entries() -> list[EolEntry]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--eol"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        entries = [
            entry
            for line in result.stdout.splitlines()
            if (entry := expected_from_eol_line(line)) is not None
        ]
        if entries:
            return entries
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return explicit_eol_entries_from_gitattributes()


def explicit_eol_entries_from_gitattributes() -> list[EolEntry]:
    rules = read_gitattributes_rules()
    entries: list[EolEntry] = []
    for path in filesystem_files():
        expected: str | None = None
        for pattern, eol in rules:
            if gitattributes_pattern_matches(pattern, path):
                expected = eol
        if expected:
            entries.append(EolEntry(path, expected))
    return entries


def read_gitattributes_rules() -> list[tuple[str, str | None]]:
    path = ROOT / ".gitattributes"
    if not path.is_file():
        return []

    rules: list[tuple[str, str | None]] = []
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        pattern = normalize_path(parts[0])
        attrs = parts[1:]
        if "-text" in attrs:
            rules.append((pattern, None))
            continue
        eol = None
        if "eol=lf" in attrs:
            eol = "lf"
        elif "eol=crlf" in attrs:
            eol = "crlf"
        if eol:
            rules.append((pattern, eol))
    return rules


def filesystem_files() -> list[str]:
    files: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = normalize_path(str(path.relative_to(ROOT)))
        if should_skip_filesystem_path(rel):
            continue
        files.append(rel)
    return sorted(files)


def should_skip_filesystem_path(path: str) -> bool:
    skip_prefixes = (
        ".git/",
        ".vs/",
        "node_modules/",
        "subagents/",
        "release/artifacts/",
        "release/out/",
    )
    if path.startswith(skip_prefixes):
        return True
    if "/bin/" in path or "/obj/" in path or "/TestResults/" in path or "__pycache__/" in path:
        return True
    return False


def gitattributes_pattern_matches(pattern: str, path: str) -> bool:
    if "/" not in pattern:
        return fnmatch.fnmatchcase(Path(path).name, pattern)
    return fnmatch.fnmatchcase(path, pattern)


def classify_line_endings(data: bytes) -> str:
    crlf_count = data.count(b"\r\n")
    without_crlf = data.replace(b"\r\n", b"")
    bare_lf_count = without_crlf.count(b"\n")
    bare_cr_count = without_crlf.count(b"\r")

    kinds = sum(1 for count in (crlf_count, bare_lf_count, bare_cr_count) if count)
    if kinds == 0:
        return "none"
    if kinds > 1 or bare_cr_count:
        return "mixed"
    if crlf_count:
        return "crlf"
    return "lf"


def normalize_line_endings(data: bytes, target: str) -> bytes:
    lf_data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if target == "lf":
        return lf_data
    if target == "crlf":
        return lf_data.replace(b"\n", b"\r\n")
    raise ValueError(f"unsupported line ending target: {target}")


def check_entries(entries: list[EolEntry], fix: bool) -> tuple[list[str], int, int, int]:
    errors: list[str] = []
    checked = 0
    rewritten = 0
    skipped = 0

    for entry in entries:
        full_path = ROOT / entry.path
        if not full_path.is_file():
            skipped += 1
            continue

        data = full_path.read_bytes()
        if b"\0" in data:
            errors.append(f"{entry.path}: explicit text eol={entry.expected}, but file contains NUL bytes")
            continue

        checked += 1
        actual = classify_line_endings(data)
        if actual in ("none", entry.expected):
            continue

        if not fix:
            errors.append(f"{entry.path}: expected {entry.expected}, found {actual}")
            continue

        normalized = normalize_line_endings(data, entry.expected)
        if normalized != data:
            full_path.write_bytes(normalized)
            rewritten += 1

    return errors, checked, rewritten, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true", help="rewrite files to their explicit .gitattributes eol")
    args = parser.parse_args()

    errors, checked, rewritten, skipped = check_entries(explicit_eol_entries(), args.fix)
    if errors:
        print("Repo line endings check: FAIL")
        for error in errors[:200]:
            print(f"- {error}")
        if len(errors) > 200:
            print(f"- ... ({len(errors) - 200} more)")
        if not args.fix:
            print("Run `py -3 tools\\repo_line_endings_check.py --fix` to normalize the working tree.")
        return 1

    print("Repo line endings check: PASS")
    print(f"Explicit text files checked: {checked}")
    print(f"Skipped non-files: {skipped}")
    if args.fix:
        print(f"Files rewritten: {rewritten}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
