#!/usr/bin/env python3
"""Validate that a materialized public candidate contains only export payload files."""

from __future__ import annotations

import argparse
import csv
import shutil
import tempfile
from pathlib import Path

from public_allowlist_safety_check import MATERIALIZED_PUBLIC_SOURCES, normalize_path


ALLOWLIST_REL = Path("release/readiness/public_candidate_allowlist.tsv")
ROOT_MATERIALIZED_FILES = {
    ".gitignore",
    ".onslaught-public-candidate-export",
    "AGENTS.md",
    "EXPORT_PROVENANCE.json",
    "package.json",
}
DENY_DIR_NAMES = {
    ".codex",
    ".git",
    ".vs",
    "GameProfiles",
    "PatchBench",
    "bin",
    "game",
    "media",
    "mcps",
    "obj",
    "node_modules",
    "save-attempts",
    "subagents",
    "__pycache__",
}


def load_allowlist(candidate_root: Path) -> set[str]:
    allowlist_path = candidate_root / ALLOWLIST_REL
    if not allowlist_path.is_file():
        raise FileNotFoundError(f"missing public allowlist in candidate: {allowlist_path}")

    rows: set[str] = set()
    with allowlist_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            rel = normalize_path(row.get("path") or "")
            cls = (row.get("class") or "").strip()
            if not rel:
                raise ValueError("allowlist row missing path")
            if cls != "R0_ALLOW":
                raise ValueError(f"non-R0 path present in public allowlist: {rel} => {cls}")
            rows.add(rel)
    if not rows:
        raise ValueError("public allowlist is empty")
    return rows


def iter_files(candidate_root: Path) -> set[str]:
    return {
        path.relative_to(candidate_root).as_posix()
        for path in candidate_root.rglob("*")
        if path.is_file()
    }


def find_deny_dirs(candidate_root: Path) -> list[str]:
    hits: list[str] = []
    for path in candidate_root.rglob("*"):
        if not path.is_dir() or path.name not in DENY_DIR_NAMES:
            continue
        hits.append(path.relative_to(candidate_root).as_posix())
    return sorted(hits)


def expected_files(candidate_root: Path) -> set[str]:
    return load_allowlist(candidate_root) | set(MATERIALIZED_PUBLIC_SOURCES) | ROOT_MATERIALIZED_FILES


def check_candidate(candidate_root: Path) -> list[str]:
    candidate_root = candidate_root.resolve()
    errors: list[str] = []
    if not candidate_root.is_dir():
        return [f"candidate root is not a directory: {candidate_root}"]

    deny_dirs = find_deny_dirs(candidate_root)
    if deny_dirs:
        errors.append("forbidden generated/private directories present: " + ", ".join(deny_dirs[:30]))
        if "node_modules" in deny_dirs:
            errors.append(
                "node_modules is present. Run this inventory check on a fresh export before npm install, "
                "or delete node_modules and rerun."
            )
        generated_hits = sorted(
            hit
            for hit in deny_dirs
            if hit in {"bin", "obj", "subagents"} or hit.endswith("/bin") or hit.endswith("/obj")
        )
        if generated_hits:
            errors.append(
                "build/test artifacts are present. Validate in a disposable copy, then regenerate a fresh candidate "
                "before sharing."
            )

    expected = expected_files(candidate_root)
    actual = iter_files(candidate_root)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append("missing public payload files: " + ", ".join(missing[:30]))
    if extra:
        errors.append("unexpected files outside public payload inventory: " + ", ".join(extra[:30]))

    for dest_rel, source_rel in MATERIALIZED_PUBLIC_SOURCES.items():
        dest = candidate_root / dest_rel
        source = candidate_root / source_rel
        if dest.is_file() and source.is_file() and dest.read_bytes() != source.read_bytes():
            errors.append(f"materialized public file differs from source template: {dest_rel} != {source_rel}")

    return errors


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "candidate"
        (root / ALLOWLIST_REL.parent).mkdir(parents=True)
        allowlist_payload = sorted(
            {
                "README.MD",
                "release/readiness/public_candidate_allowlist.tsv",
                *MATERIALIZED_PUBLIC_SOURCES.values(),
            }
        )
        allowlist_rows = [
            "path\tclass\treason\trelease_posture\n",
        ]
        allowlist_rows.extend(
            f"{rel}\tR0_ALLOW\tdefault\tallow_with_normal_review\n" for rel in allowlist_payload
        )
        (root / ALLOWLIST_REL).write_text("".join(allowlist_rows), encoding="utf-8", newline="\n")
        (root / "README.MD").write_text("# Test\n", encoding="utf-8")
        (root / ".onslaught-public-candidate-export").write_text(
            "onslaught-public-candidate-export.v1\n", encoding="utf-8"
        )
        for rel in set(MATERIALIZED_PUBLIC_SOURCES.values()):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("public\n", encoding="utf-8")
        for rel in MATERIALIZED_PUBLIC_SOURCES:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("public\n", encoding="utf-8")
        for rel in ROOT_MATERIALIZED_FILES:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("public\n", encoding="utf-8")

        errors = check_candidate(root)
        if errors:
            print("Public candidate inventory self-test: FAIL")
            for error in errors:
                print(f"- expected clean fixture pass, got: {error}")
            return 1

        (root / "EXPORT_PROVENANCE.json").unlink()
        errors = check_candidate(root)
        if not any("missing public payload files" in error and "EXPORT_PROVENANCE.json" in error for error in errors):
            print("Public candidate inventory self-test: FAIL")
            print(f"- expected missing provenance failure, got: {errors or 'no errors'}")
            return 1
        (root / "EXPORT_PROVENANCE.json").write_text("public\n", encoding="utf-8")

        (root / "AGENTS.md").write_text("tampered\n", encoding="utf-8")
        errors = check_candidate(root)
        if not any("materialized public file differs from source template" in error and "AGENTS.md" in error for error in errors):
            print("Public candidate inventory self-test: FAIL")
            print(f"- expected materialized AGENTS.md parity failure, got: {errors or 'no errors'}")
            return 1
        (root / "AGENTS.md").write_text("public\n", encoding="utf-8")

        (root / "OnslaughtCareerEditor.WinUI/bin/Debug").mkdir(parents=True)
        (root / "OnslaughtCareerEditor.WinUI/bin/Debug/extra.dll").write_bytes(b"not shipped")
        errors = check_candidate(root)
        if not any("forbidden generated/private directories present" in error for error in errors):
            print("Public candidate inventory self-test: FAIL")
            print(f"- expected bin directory failure, got: {errors or 'no errors'}")
            return 1
        if not any("unexpected files outside public payload inventory" in error for error in errors):
            print("Public candidate inventory self-test: FAIL")
            print(f"- expected extra file failure, got: {errors or 'no errors'}")
            return 1
        if not any("build/test artifacts are present" in error for error in errors):
            print("Public candidate inventory self-test: FAIL")
            print(f"- expected build/test artifact guidance, got: {errors or 'no errors'}")
            return 1

        shutil.rmtree(root / "OnslaughtCareerEditor.WinUI")

        (root / "node_modules").mkdir()
        errors = check_candidate(root)
        if not any("node_modules is present" in error for error in errors):
            print("Public candidate inventory self-test: FAIL")
            print(f"- expected node_modules guidance, got: {errors or 'no errors'}")
            return 1
        shutil.rmtree(root / "node_modules")

        (root / "game").mkdir()
        errors = check_candidate(root)
        if not any("forbidden generated/private directories present" in error for error in errors):
            print("Public candidate inventory self-test: FAIL")
            print(f"- expected empty private root directory failure, got: {errors or 'no errors'}")
            return 1
        shutil.rmtree(root / "game")

    print("Public candidate inventory self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate-root",
        default=".",
        help="Materialized public candidate root to validate.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in fixture tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    candidate_root = Path(args.candidate_root)
    errors = check_candidate(candidate_root)
    if errors:
        print("Public candidate inventory check: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    actual = iter_files(candidate_root.resolve())
    print("Public candidate inventory check: PASS")
    print(f"Files: {len(actual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
