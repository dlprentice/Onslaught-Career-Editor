#!/usr/bin/env python3
"""Check public-primary migration coverage against the old private repo.

The public repo is now the normal working repo. This guard verifies that the
tracked private-to-public delta is limited to hard payload or volatile scratch
classes, not useful source/docs/tools/reference material.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIVATE_ROOT = ROOT.parent / "Onslaught-Career-Editor-private"
GOLD_SAVE_SHA256 = "0c17e47db9d666e9b26ef88d43d0a25e7cbfbf4f88c8005cc748965050e506fb"
ONSLAUGHT_SUBMODULE = "792545b996365f383781c666d145ea6cbda83f3a"
AYA_SUBMODULE = "6f3df296201ecc62bc09c39f7a93d8a4fb2f1638"


@dataclass(frozen=True)
class Finding:
    path: str
    category: str
    detail: str


def run_git(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout


def tracked_files(root: Path) -> set[str]:
    output = run_git(root, ["ls-files", "-z"])
    return {item.replace("\\", "/") for item in output.split("\0") if item}


def tracked_index(root: Path, path: str) -> str:
    return run_git(root, ["ls-files", "-s", "--", path]).strip()


def file_sha256(root: Path, path: str) -> str:
    import hashlib

    h = hashlib.sha256()
    with (root / path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_allowed_private_only(path: str) -> tuple[bool, str]:
    if path.startswith(("game/", "media/", "save-attempts/")):
        return True, "local game/media/save payload"
    if path.startswith(".tmp_cs_"):
        return True, "temporary save/options payload"
    if path in {"BEA.exe.gzf", "BEA_Widescreen.exe"}:
        return True, "top-level executable/archive payload"
    if path.startswith("reverse-engineering/binary-analysis/scratch/"):
        if Path(path).suffix.lower() in {".bes", ".fbx", ".png"}:
            return True, "volatile RE scratch payload output"
        return False, ""
    if path.startswith("lore-book/reverse-engineering/binary-analysis/scratch/"):
        if Path(path).suffix.lower() in {".bes", ".fbx", ".png"}:
            return True, "volatile mirrored RE scratch payload output"
        return False, ""
    return False, ""


def compare_private_public(public_root: Path, private_root: Path) -> list[Finding]:
    public_files = tracked_files(public_root)
    private_files = tracked_files(private_root)
    findings: list[Finding] = []
    for path in sorted(private_files - public_files):
        allowed, reason = is_allowed_private_only(path)
        if not allowed:
            findings.append(Finding(path, "missing-tracked-project-material", "not an allowed hard-payload/scratch class"))
    return findings


def check_required_public_surfaces(public_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    required_files = [
        "archive/electron-workbench/packages/ui/src/components/media/MediaDetails.tsx",
        "archive/electron-workbench/packages/ui/src/components/media/MediaSection.tsx",
        "tests_shared/fixtures/gold_career_save.bin",
    ]
    for path in required_files:
        if path not in tracked_files(public_root):
            findings.append(Finding(path, "missing-required-public-surface", "expected tracked migration surface"))

    if "tests_shared/fixtures/gold_career_save.bin" in tracked_files(public_root):
        digest = file_sha256(public_root, "tests_shared/fixtures/gold_career_save.bin")
        if digest != GOLD_SAVE_SHA256:
            findings.append(Finding("tests_shared/fixtures/gold_career_save.bin", "fixture-hash-mismatch", digest))

    submodule_expectations = {
        "references/Onslaught": ONSLAUGHT_SUBMODULE,
        "references/AYAResourceExtractor": AYA_SUBMODULE,
    }
    for path, expected_hash in submodule_expectations.items():
        line = tracked_index(public_root, path)
        if not line:
            findings.append(Finding(path, "missing-reference-submodule", "expected tracked gitlink"))
            continue
        parts = line.split()
        mode = parts[0] if parts else ""
        digest = parts[1] if len(parts) > 1 else ""
        if mode != "160000" or digest != expected_hash:
            findings.append(Finding(path, "reference-submodule-mismatch", line))
    return findings


def run_self_test() -> int:
    checks = {
        "game/BEA.exe": True,
        "media/flash/battle_engine_aquila.swf": True,
        "save-attempts/foo.bes": True,
        "reverse-engineering/binary-analysis/scratch/probe/out/file.c": False,
        "reverse-engineering/binary-analysis/scratch/probe/out/file.png": True,
        "lore-book/reverse-engineering/binary-analysis/scratch/probe/out/file.c": False,
        "lore-book/reverse-engineering/binary-analysis/scratch/probe/out/file.tsv": False,
        "lore-book/reverse-engineering/binary-analysis/scratch/probe/out/file.png": True,
        "tools/missing_checker.py": False,
        "roadmap/missing.md": False,
    }
    failures: list[str] = []
    for path, expected in checks.items():
        actual, _reason = is_allowed_private_only(path)
        if actual != expected:
            failures.append(f"{path}: expected {expected}, got {actual}")
    if failures:
        print("Public-primary migration inventory self-test: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Public-primary migration inventory self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true", help="Run the migration inventory check.")
    parser.add_argument("--public-root", type=Path, default=ROOT)
    parser.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE_ROOT)
    parser.add_argument("--require-private-root", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    public_root = args.public_root.resolve()
    private_root = args.private_root.resolve()

    findings = check_required_public_surfaces(public_root)
    if private_root.exists():
        findings.extend(compare_private_public(public_root, private_root))
    elif args.require_private_root:
        findings.append(Finding(str(private_root), "missing-private-root", "private comparison root does not exist"))
    else:
        print(f"Public-primary migration inventory: private root absent, skipped delta comparison: {private_root}")

    if findings:
        print("Public-primary migration inventory: FAIL")
        for finding in findings[:200]:
            print(f"- {finding.path}: {finding.category}: {finding.detail}")
        if len(findings) > 200:
            print(f"- ... ({len(findings) - 200} more)")
        return 1

    print("Public-primary migration inventory: PASS")
    print(f"Public root: {public_root}")
    if private_root.exists():
        public_files = tracked_files(public_root)
        private_files = tracked_files(private_root)
        missing = sorted(private_files - public_files)
        allowed_missing = [path for path in missing if is_allowed_private_only(path)[0]]
        print(f"Private tracked paths: {len(private_files)}")
        print(f"Public tracked paths: {len(public_files)}")
        print(f"Allowed private-only hard-payload/scratch paths: {len(allowed_missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
