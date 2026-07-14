#!/usr/bin/env python3
"""Filesystem hygiene for runtime proof private roots.

Safe-copy while running; compact evidence after closeout. These helpers are pure
path operations under an authorized private root so unit tests can exercise the
same entry points the live pair runner uses—without launching BEA.
"""

from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path
from typing import Iterable


PROFILE_APP_CONFIG = "profile-app-config"
RUNNER_DIR = "runner"
RUNNER_JUNK_DIRS = ("bin", "obj")
COMPACT_EVIDENCE_MARKERS = frozenset(
    {
        "walker-trajectory-raw.json",
        "walker-trajectory-metrics.json",
        "walker-trajectory-attempt-closeout.json",
        "observer-status.json",
        "runtime-process-receipt.json",
        "two-attempt-closeout.json",
        "runner-build-receipt.json",
        "scalar-response-public-projection.json",
        "jet-trajectory-raw.json",
        "jet-trajectory-metrics.json",
        "jet-trajectory-attempt-closeout.json",
    }
)


def _path_is_reparse(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0) & 0x400
    )


def _has_reparse_ancestor(path: Path) -> bool:
    current = Path(os.path.abspath(os.fspath(path)))
    while True:
        if _path_is_reparse(current):
            return True
        if current.parent == current:
            return False
        current = current.parent


def authorize_under(path: Path, authorized_private_root: Path, *, label: str) -> Path:
    """Require path to resolve strictly beneath the authorized private root."""
    lexical = Path(os.path.abspath(os.fspath(path)))
    lexical_root = Path(os.path.abspath(os.fspath(authorized_private_root)))
    if _has_reparse_ancestor(lexical) or _has_reparse_ancestor(lexical_root):
        raise ValueError(f"{label} or authorized root is reparse routed")
    resolved = lexical.resolve(strict=False)
    resolved_root = lexical_root.resolve(strict=True)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"resolved {label} escaped the authorized private root") from exc
    if resolved == resolved_root:
        raise ValueError(f"{label} must be strictly beneath the authorized private root")
    return resolved


def _rmtree_if_present(path: Path, removed: list[str]) -> None:
    if path.is_symlink():
        path.unlink(missing_ok=True)
        removed.append(str(path))
        return
    if path.is_dir():
        shutil.rmtree(path)
        removed.append(str(path))


def strip_bulky_attempt_tree(
    attempt_root: Path,
    *,
    authorized_private_root: Path,
) -> dict[str, object]:
    """Delete profile-app-config under one attempt root; keep evidence files."""
    attempt_root = authorize_under(
        attempt_root, authorized_private_root, label="attempt root"
    )
    removed: list[str] = []
    kept: list[str] = []
    profile = attempt_root / PROFILE_APP_CONFIG
    _rmtree_if_present(profile, removed)
    evidence = attempt_root / "evidence"
    if evidence.is_dir():
        for path in sorted(evidence.rglob("*")):
            if path.is_file():
                kept.append(path.name)
    return {
        "schemaVersion": "runtime-proof-lab-hygiene-strip.v1",
        "attemptRoot": str(attempt_root),
        "removed": removed,
        "compactEvidenceNames": kept,
        "profileAppConfigPresentAfter": (attempt_root / PROFILE_APP_CONFIG).exists(),
    }


def strip_runner_build_junk(
    private_root: Path,
    *,
    authorized_private_root: Path,
) -> dict[str, object]:
    """Delete runner/bin and runner/obj under a pair private root."""
    private_root = authorize_under(
        private_root, authorized_private_root, label="private root"
    )
    removed: list[str] = []
    runner = private_root / RUNNER_DIR
    for name in RUNNER_JUNK_DIRS:
        _rmtree_if_present(runner / name, removed)
    return {
        "schemaVersion": "runtime-proof-lab-hygiene-runner-strip.v1",
        "privateRoot": str(private_root),
        "removed": removed,
    }


def strip_pair_private_root(
    private_root: Path,
    *,
    authorized_private_root: Path,
) -> dict[str, object]:
    """Strip all attempt profile trees and runner build junk under a pair root."""
    private_root = authorize_under(
        private_root, authorized_private_root, label="pair private root"
    )
    attempts: list[dict[str, object]] = []
    for child in sorted(private_root.iterdir()):
        if child.is_dir() and child.name.startswith("attempt-"):
            attempts.append(
                strip_bulky_attempt_tree(
                    child, authorized_private_root=authorized_private_root
                )
            )
    runner = strip_runner_build_junk(
        private_root, authorized_private_root=authorized_private_root
    )
    return {
        "schemaVersion": "runtime-proof-lab-hygiene-pair-strip.v1",
        "privateRoot": str(private_root),
        "attempts": attempts,
        "runner": runner,
    }


def materialize_from_durable_lab_base(
    dest: Path,
    durable_base: Path,
    *,
    authorized_private_root: Path,
) -> dict[str, object]:
    """Copy a durable lab profile base into dest (both under authorized root).

    Reuse means the *source* of the safe-copy is a lab mirror already under the
    authorized private root (or strictly beneath it), not the Steam install.
    Dest must not already exist.
    """
    dest = authorize_under(dest, authorized_private_root, label="profile dest")
    durable_base = authorize_under(
        durable_base, authorized_private_root, label="durable lab base"
    )
    if not durable_base.is_dir():
        raise ValueError("durable lab base must be an existing directory")
    if dest.exists() or dest.is_symlink():
        raise ValueError("profile dest already exists")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(durable_base, dest, symlinks=False, dirs_exist_ok=False)
    return {
        "schemaVersion": "runtime-proof-lab-hygiene-reuse.v1",
        "durableBase": str(durable_base),
        "dest": str(dest),
        "fileCount": sum(1 for _ in dest.rglob("*") if _.is_file()),
    }


def compact_evidence_present(paths: Iterable[Path]) -> bool:
    names = {path.name for path in paths if path.is_file()}
    return bool(names & COMPACT_EVIDENCE_MARKERS)
