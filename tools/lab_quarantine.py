#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Quarantine local-lab / lab evidence before any destructive delete.

Durable rule (maintainer FRAGO 2026-08-06, after the re-campaign fixture
loss): nothing under local-lab/ is ever hard-deleted in one step. ``stage``
moves a path to D:\\lab-quarantine\\<date>\\ preserving relative structure
plus a manifest row (original path, sha256 of the whole tree, bytes, reason,
staged-at). ``restore`` moves it back. ``resume <source> <dest>`` finishes an
interrupted ``stage`` whose destination partial already exists on D:
(timeout-killed copy run): it retains byte-verified files, re-copies
missing or mismatched ones, refuses ANY reparse point found in either tree
(no-follow census before the copy, re-checked at the manifest boundary and
again immediately before removal), gates on exact file-count + byte-total +
tree-hash identity, appends
ONE manifest row with stage()'s schema (refusing duplicate ids before
writing), reads it back, freshly re-hashes BOTH
sides, then removes the proven source with a DOS-read-only-only handler that
aborts on reparse, sharing, or ACL failures. It never restarts the copy from
scratch and fails closed before every destructive step. ``purge``
(explicit, separate command)
removes a staged item ONLY when space pressure requires it and the manifest
row is confirmed; purged rows are rewritten to a purge log with the same
identity so recovery by name remains possible for as long as the drive
retains the blocks.

D: must be present and have free space; the rule refuses to run without it.
Use this instead of Remove-Item for anything that is not regenerable build
output inside an active tool's own scratch.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

QUARANTINE_ROOT = Path(r"D:\lab-quarantine")
MANIFEST = QUARANTINE_ROOT / "manifest.jsonl"
PURGE_LOG = QUARANTINE_ROOT / "purge.log"

FILE_ATTRIBUTE_READONLY = 0x1
FILE_ATTRIBUTE_REPARSE_POINT = 0x400


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _file_attributes(path: Path) -> int | None:
    """DOS file attributes via GetFileAttributesW; None if the path is gone."""

    if os.name != "nt":
        import stat as stat_module

        try:
            mode = path.lstat().st_mode
        except OSError:
            return None
        attributes = 0
        if stat_module.S_ISLNK(mode):
            attributes |= FILE_ATTRIBUTE_REPARSE_POINT
        if not (mode & (stat_module.S_IWUSR | stat_module.S_IWGRP | stat_module.S_IWOTH)):
            attributes |= FILE_ATTRIBUTE_READONLY
        return attributes
    import ctypes

    attributes = ctypes.windll.kernel32.GetFileAttributesW(str(path))
    return None if attributes == 0xFFFFFFFF else attributes


def _lstat_is_reparse_point(path: Path) -> bool:
    """Reparse verdict from the FINAL component alone, never following it.

    Uses ``os.lstat`` (or an equivalent no-follow probe): attributes of the
    entry itself, so a symlink/junction answers for its own link even when
    its target is missing or hostile. This is the primitive that must be
    used wherever an earlier verdict could be stale or blinded.
    """

    if os.name != "nt":
        import stat as stat_module

        try:
            mode = path.lstat().st_mode
        except OSError:
            return True
        return stat_module.S_ISLNK(mode)
    import ctypes

    try:
        attributes = ctypes.windll.kernel32.GetFileAttributesW(str(path))
    except OSError:
        return True
    if attributes == 0xFFFFFFFF:
        # Absent from the final-component namespace: absent path, or a
        # dangling device-level reparse. Both refuse.
        return True
    # True iff the FINAL component itself carries a reparse point. Plain
    # files and plain directories answer False; junctions, symlinks, and
    # dangling device-level reparses answer True regardless of target.
    return bool(attributes & FILE_ATTRIBUTE_REPARSE_POINT)


def _is_reparse_point(path: Path) -> bool:
    """True for junctions/symlinks: never copied, never descended, never cleared."""

    try:
        attributes = _file_attributes(path)
    except OSError:
        return True
    return attributes is None or bool(attributes & FILE_ATTRIBUTE_REPARSE_POINT)


def _classify_entry(entry: os.DirEntry) -> str | None:
    """Literal no-follow classification of one scandir entry.

    Returns "dir", "file", or None for anything else. The entry's OWN
    no-follow stat decides: first its DOS attributes (any reparse point --
    junction, symlink, or special -- is unclassifiable for quarantine
    purposes even where the runtime calls it a directory), then its plain
    dir/file type. A follow-only directory answer can never trigger descent.
    """

    try:
        stat_result = entry.stat(follow_symlinks=False)
        attributes = getattr(stat_result, "st_file_attributes", 0)
    except (OSError, AttributeError):
        attributes = 0
    if attributes & FILE_ATTRIBUTE_REPARSE_POINT:
        return None
    try:
        if entry.is_dir(follow_symlinks=False):
            return "dir"
        if entry.is_file(follow_symlinks=False):
            return "file"
    except OSError:
        return None
    return None


def _scan_plain_children(directory: Path) -> list[tuple[Path, str]]:
    """One no-follow scandir of ``directory``, classified and fail-closed.

    Raises RuntimeError when the scan fails (vanished directory, sharing
    violation, permission denial) or when any entry cannot be classified
    without following it: a tree that cannot be proven plain is unsafe.
    """

    children: list[tuple[Path, str]] = []
    try:
        with os.scandir(directory) as scan:
            for entry in scan:
                child_path = Path(entry.path)
                # An entry counts as plain ONLY when both its own no-follow
                # stat classifies it AND the module-level final-component
                # guard agrees it carries no reparse flag (covers flagged
                # and device-level reparses whose directory type lies).
                kind = (
                    None
                    if _is_reparse_point(child_path)
                    else _classify_entry(entry)
                )
                if kind is None:
                    raise RuntimeError(
                        f"fail-closed: cannot classify {entry.path} as a plain "
                        "directory or file without following it; quarantine "
                        "traversal refuses to descend, copy through, or hash it"
                    )
                children.append((child_path, kind))
    except OSError as error:
        raise RuntimeError(
            f"fail-closed: could not scan directory {directory}: {error}"
        ) from None
    return children


def _iter_plain_files(root: Path):
    """Yield every plain regular file under ``root``, never crossing a reparse.

    Explicit no-follow walk: each entry is classified from its own link
    stat BEFORE any descent, so external content behind a junction or
    symlink is neither opened nor hashed. Scan failures refuse immediately.
    """

    pending = [root]
    while pending:
        current = pending.pop()
        for child_path, kind in _scan_plain_children(current):
            if kind == "dir":
                pending.append(child_path)
            else:
                yield child_path


def _reparse_census(root: Path) -> list[str]:
    """No-follow inventory of every reparse point at/under ``root``.

    Returns relative POSIX paths ("." denotes the root itself). Enumeration
    never descends into a reparse entry, so scanning cannot traverse a
    junction/symlink target. A directory that cannot be scanned fails closed.
    """

    if _is_reparse_point(root):
        return ["."]
    found: list[str] = []
    pending = [root]
    while pending:
        current = pending.pop()
        try:
            scan = os.scandir(current)
            try:
                entries = list(scan)
            finally:
                close = getattr(scan, "close", None)
                if callable(close):
                    close()
        except OSError as error:
            raise RuntimeError(
                f"reparse census could not scan directory {current}: {error}"
            ) from None
        for entry in entries:
            entry_path = Path(entry.path)
            # Reported as a reparse hit: either the entry IS one, or it
            # cannot be proven plain without following it -- in both cases
            # quarantine refuses to descend, copy through, or hash it.
            if (
                _is_reparse_point(entry_path)
                or _classify_entry(entry) is None
            ):
                found.append(entry_path.relative_to(root).as_posix())
                continue
            if entry.is_dir(follow_symlinks=False):
                pending.append(entry_path)
    return sorted(found)


def _refuse_tree_reparses(side: str, root: Path) -> None:
    """Fail closed when ``side``'s tree (root included) holds any reparse."""

    found = _reparse_census(root)
    if not found:
        return
    listing = ", ".join(found[:10])
    more = "" if len(found) <= 10 else f" (+{len(found) - 10} more)"
    raise SystemExit(
        f"fail-closed: {side} tree contains reparse point(s) [{listing}{more}] "
        f"under {root}: quarantine resume refuses to descend, copy through, or "
        "remove any reparse; both trees are left untouched"
    )


def _file_bytes_differ(source_file: Path, dest_file: Path) -> bool:
    """True at the first differing byte; streaming, so no whole-file loads."""

    with source_file.open("rb") as source_stream, dest_file.open("rb") as dest_stream:
        while True:
            source_chunk = source_stream.read(1024 * 1024)
            dest_chunk = dest_stream.read(1024 * 1024)
            if source_chunk != dest_chunk:
                return True
            if not source_chunk:
                return False


def _resume_copy_tree(source: Path, dest: Path) -> dict:
    """Finish an interrupted copytree without ever restarting from scratch.

    Retention is BYTE-VERIFIED: a destination file is kept only when its
    size+mtime match the source AND a streaming comparison proves the bytes
    are identical; anything missing or mismatched is re-copied
    (shutil.copy2 semantics). This makes resume converge even when a
    corrupted partial file happens to share size+mtime with its source.

    Reparse points are refused on BOTH sides and never copied, descended,
    or written through. Callers run a no-follow census of both trees before
    this walk; the walk itself re-verifies every destination ancestor and
    each entry it is about to touch, raising SystemExit the moment any
    reparse appears in either tree (including the roots). A staged
    quarantine copy therefore records plain files and directories only --
    and a source reparse can never be silently skipped and later cleared
    by the removal step.
    """

    retained = recopied_mismatched = copied_missing = 0

    def refuse(reason: str, path: Path) -> None:
        raise SystemExit(
            f"fail-closed: {reason} reparse point at {path}: quarantine copy "
            "refuses to open, create through, or traverse it; the copy pass "
            "stopped before completing and nothing was appended or removed"
        )

    if _is_reparse_point(source):
        refuse("source root", source)
    if _is_reparse_point(dest):
        refuse("destination root", dest)
    for dirpath, dirnames, filenames in os.walk(source):
        source_dir = Path(dirpath)
        dest_dir = dest / source_dir.relative_to(source)
        # No-follow mirror of the walk onto the destination side: every
        # existing destination ancestor of the current pair must still be a
        # plain non-reparse directory before anything may be created through
        # or beneath it. The verdict is FRESH lstat truth on the final
        # component -- never a cached or earlier check -- so deterministic or
        # blinded replacement at this boundary is still caught.
        ancestor = dest
        for part in source_dir.relative_to(source).parts:
            ancestor /= part
            if os.path.lexists(ancestor) and (
                _is_reparse_point(ancestor) or _lstat_is_reparse_point(ancestor)
            ):
                refuse("destination ancestor became a", ancestor)
        if os.path.lexists(dest_dir):
            if _is_reparse_point(dest_dir):
                refuse("destination directory became a", dest_dir)
            if not dest_dir.is_dir():
                raise SystemExit(
                    f"fail-closed: destination path is not a directory: {dest_dir}; "
                    "the interrupted-stage layout cannot be reconciled"
                )
        dest_dir.mkdir(parents=True, exist_ok=True)
        if _lstat_is_reparse_point(dest_dir):  # post-create re-verification
            refuse("destination directory became a", dest_dir)
        # Any reparse in the SOURCE tree refuses outright: silently skipping
        # would let a later removal clear the reparse together with its tree.
        for name in dirnames:
            candidate = source_dir / name
            if _is_reparse_point(candidate):
                refuse("source directory", candidate)
        for name in filenames:
            source_file = source_dir / name
            dest_file = dest_dir / name
            if _is_reparse_point(source_file):
                refuse("source file", source_file)
            # Operation-boundary re-verification immediately before
            # stat/open/copy: the full destination chain that is about to
            # receive bytes (every ancestor of dest_dir, dest_dir itself,
            # and the file slot). Each element is judged seam-verdict FIRST,
            # then fresh unmockable lstat truth LAST -- a replacement that
            # lands during any earlier evaluation is still seen by the final
            # component check, and copy2 can never write through a reparse.
            chain = [dest]
            prefix = dest
            for part in dest_dir.relative_to(dest).parts:
                prefix /= part
                chain.append(prefix)
            for touched in (*chain, dest_file):
                if os.path.lexists(touched) and (
                    _is_reparse_point(touched) or _lstat_is_reparse_point(touched)
                ):
                    refuse(
                        "destination path became a",
                        touched,
                    )
            try:
                source_stat = source_file.stat()
                dest_stat = dest_file.stat()
            except FileNotFoundError:
                shutil.copy2(source_file, dest_file)
                copied_missing += 1
                continue
            if (source_stat.st_size == dest_stat.st_size
                    and source_stat.st_mtime == dest_stat.st_mtime
                    and not _file_bytes_differ(source_file, dest_file)):
                retained += 1
            else:
                shutil.copy2(source_file, dest_file)
                recopied_mismatched += 1
    return {
        "retained": retained,
        "recopiedMismatched": recopied_mismatched,
        "copiedMissing": copied_missing,
    }


def _identity(root: Path) -> tuple[int, int, str]:
    """(files, bytes, tree_sha256) using stage()'s exact identity semantics.

    Walks with explicit no-follow scandir semantics: each entry is
    classified from its own link stat BEFORE any descent or open, so a
    reparse is never followed and external content behind one is never
    blessed as staged evidence. The root itself, any nested entry that
    cannot be proven a plain directory or file, and any scan failure all
    refuse before any hashing; tree identity over a reparse-containing
    tree is undefined for quarantine purposes.
    """

    if _is_reparse_point(root):
        raise RuntimeError(
            f"identity computation refused: tree root itself is a reparse point: {root}"
        )
    count = 0
    total_bytes = 0
    digest = hashlib.sha256()
    for path in sorted(_iter_plain_files(root)):
        rel = path.relative_to(root).as_posix()
        data_sha = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                data_sha.update(chunk)
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(data_sha.hexdigest().encode("utf-8"))
        digest.update(b"\0")
        count += 1
        total_bytes += path.stat().st_size
    return count, total_bytes, digest.hexdigest()


def _append_manifest_row(row: dict) -> None:
    """Append exactly one manifest row, then read it back from disk.

    Ids are the unique authority. The whole append runs inside one
    exclusive serialization scope (_acquire_manifest_mutex) and the raw
    on-disk manifest is re-read for ids AFTER the append handle exists but
    BEFORE any byte is written: an equal id injected between this
    routine's earlier reads and the append open still refuses, leaving
    the manifest byte-for-byte unchanged at the single competing row.
    After the fsynced write, readback fails closed unless the manifest
    contains this row verbatim exactly once plus every pre-existing row
    (intentional semantics for a completed append whose later readback is
    corrupted: the row and both evidence copies remain).
    """

    lock_dir = _acquire_manifest_mutex()
    try:
        with MANIFEST.open("a", encoding="utf-8") as stream:
            # Write-boundary id re-check: under the mutex, after the append
            # handle exists, before the first byte is written.
            before_lines = (
                MANIFEST.read_text(encoding="utf-8").splitlines()
                if MANIFEST.exists() else []
            )
            if any(
                json.loads(line).get("id") == row["id"]
                for line in before_lines
                if line.strip()
            ):
                raise RuntimeError(
                    f"manifest append refused at the write boundary: id "
                    f"{row['id']} already exists; manifest left byte-for-byte "
                    "unchanged, nothing appended"
                )
            stream.write(json.dumps(row) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        shutil.rmtree(lock_dir, ignore_errors=True)
    after = MANIFEST.read_text(encoding="utf-8").splitlines()
    parsed_after = [json.loads(line) for line in after if line.strip()]
    row_lines = [line for line in after
                 if line.strip() and json.loads(line)["id"] == row["id"]]
    if (
        len(row_lines) != 1
        or json.loads(row_lines[0]) != row
        or [json.loads(line) for line in before_lines if line.strip()] != parsed_after[:-1]
    ):
        raise RuntimeError(
            f"manifest append failed readback for id {row['id']}; "
            "no removal was performed"
        )


def _acquire_manifest_mutex() -> Path:
    """Exclusive serialization scope for one manifest append.

    Directory creation is atomic on every platform, so mkdir IS the lock.
    The scope lives beside the manifest under the QUARANTINE_ROOT (never
    derived from MANIFEST itself, which tests may proxy). The holder leaves
    a fresh marker; a leftover whose marker is older than the staleness
    horizon belongs to a crashed writer and is reclaimed. Refuses rather
    than waiting past the budget when another writer genuinely holds the
    scope: quarantine appends are rare audited events, not a contention
    workload, and failing closed beats queueing behind an unknown process.
    """

    lock_dir = QUARANTINE_ROOT / ".manifest-append.lock"
    deadline = time.monotonic() + 10.0
    while True:
        try:
            lock_dir.mkdir()
        except FileExistsError:
            marker = lock_dir / "holder.txt"
            try:
                age = time.time() - marker.stat().st_mtime
            except OSError:
                age = float("inf")
            if age > 60.0:
                try:
                    shutil.rmtree(lock_dir)
                    continue
                except OSError:
                    pass
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "manifest append refused: another writer holds the append "
                    f"scope at {lock_dir} (holder marker age {age:.0f}s); "
                    "nothing was written"
                ) from None
            time.sleep(0.05)
            continue
        break
    try:
        (lock_dir / "holder.txt").write_text(utc_now(), encoding="utf-8")
    except OSError:
        pass  # self-healing: a missing marker makes the next pass reclaim
    return lock_dir


def _remove_tree_readonly_only(root: Path) -> None:
    """rmtree that clears ONLY the DOS read-only bit on failure paths.

    Any other failure (reparse point encountered, sharing violation, ACL
    denial, missing parent) aborts with the original error untouched.
    Uses ``onexc`` where available (Python >= 3.12; ``onerror`` was removed
    in 3.14) and falls back to ``onerror`` elsewhere.
    """

    def _retry(function, path, exc):  # noqa: ANN001 - shutil callback shape
        attrs = _file_attributes(Path(path))
        if (
            function is os.unlink
            and attrs is not None
            and attrs & FILE_ATTRIBUTE_READONLY
            and not attrs & FILE_ATTRIBUTE_REPARSE_POINT
        ):
            if os.name == "nt":
                import ctypes

                ctypes.windll.kernel32.SetFileAttributesW(
                    str(path), attrs & ~FILE_ATTRIBUTE_READONLY)
            else:
                os.chmod(path, 0o644)
            function(path)
            return
        raise exc

    if "onexc" in inspect.signature(shutil.rmtree).parameters:
        shutil.rmtree(root, onexc=_retry)
    else:  # Python < 3.12: exc_info-tuple callback
        shutil.rmtree(
            root,
            onerror=lambda function, path, exc_info: _retry(function, path, exc_info[1]),
        )


def resume(source: Path, dest: Path, *, reason: str) -> dict:
    """Audited completion of an interrupted ``stage`` into an existing D partial.

    Completes ``dest`` from its original ``source`` (retaining only
    byte-verified files, re-copying what is missing or mismatched), gates on
    exact file-count + byte-total + tree-hash identity, appends ONE manifest
    row identical to stage()'s schema, reads it back, freshly re-hashes BOTH
    sides, removes the proven source with a DOS-read-only-only handler, and
    returns the receipt. Every gate fails closed before any destructive step.

    Reparse points refuse the run untouched wherever they appear: a no-follow
    census of BOTH trees runs before the copy, re-runs at the manifest
    boundary, and re-runs immediately before removal; the copy layer itself
    re-verifies every destination ancestor and entry it touches. Manifest
    ids are the unique authority: an existing id under a different staged
    path refuses before any append, leaving the manifest byte-for-byte
    unchanged.
    """

    # Lexical identity FIRST: the caller's exact roots are checked for
    # reparse points before any .resolve() can silently follow them onto
    # their targets -- even when those targets live inside the quarantine
    # root. A root that IS a reparse point refuses untouched; resolution,
    # enumeration, copy, append, and removal never see it.
    if _is_reparse_point(source):
        raise SystemExit(
            f"fail-closed: source root is a reparse point: {source}; refusing "
            "to follow it to any target, enumerate, copy, or remove")
    if _lstat_is_reparse_point(dest):
        raise SystemExit(
            f"fail-closed: destination root is a reparse point: {dest}; "
            "refusing to follow it to any target or create or copy through it")

    source = source.resolve()
    dest = dest.resolve()
    if not QUARANTINE_ROOT.exists():
        raise SystemExit(f"quarantine root missing: {QUARANTINE_ROOT} (is D: mounted?)")
    if not source.exists():
        raise SystemExit(f"source does not exist: {source}")
    if not source.is_dir():
        raise SystemExit(f"source is not a directory: {source}")
    if not dest.is_dir():
        raise SystemExit(f"destination partial missing (never restart stage): {dest}")
    for base in (QUARANTINE_ROOT.resolve(),):
        if not (source.is_relative_to(base) and dest.is_relative_to(base)):
            raise SystemExit(
                "refusing to operate outside the quarantine root "
                f"(source={source}, dest={dest}, root={base})"
            )
    if source == dest or dest.is_relative_to(source):
        raise SystemExit(f"destination must be distinct from source: {dest}")

    # No-follow reparse census of BOTH trees before any copy mutation.
    _refuse_tree_reparses("source", source)
    _refuse_tree_reparses("destination", dest)

    rows = ([json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip()]
            if MANIFEST.exists() else [])
    if any(r.get("staged") == str(dest) for r in rows):
        raise SystemExit(f"destination is already manifested: {dest}")
    if any(r.get("id") == dest.name for r in rows):
        conflicting = sorted({
            str(r.get("staged")) for r in rows if r.get("id") == dest.name
        })
        raise SystemExit(
            f"manifest id already exists: id={dest.name} staged={conflicting}; "
            "ids are the unique authority, refusing to append a second row"
        )

    stats = _resume_copy_tree(source, dest)

    source_identity = _identity(source)
    dest_identity = _identity(dest)
    if source_identity != dest_identity:
        raise SystemExit(
            "resumed quarantine copy does not reproduce the source identity: "
            f"source={source_identity} staged={dest_identity} "
            f"(stats={stats}); both sides preserved, nothing removed"
        )

    # Re-check reparse freedom at the safety boundary before the append.
    _refuse_tree_reparses("source", source)
    _refuse_tree_reparses("destination", dest)

    row = {
        "id": dest.name,
        "original": str(source),
        "staged": str(dest),
        "stagedAtUtc": utc_now(),
        "bytes": dest_identity[1],
        "sha256": dest_identity[2],
        "reason": reason,
    }
    _append_manifest_row(row)

    # Fresh dual rehash AFTER the append: prove both trees still carry the
    # gated identity before any destructive step.
    recheck_source = _identity(source)
    recheck_dest = _identity(dest)
    if recheck_source != source_identity or recheck_dest != dest_identity:
        raise RuntimeError(
            "post-append rehash mismatch: "
            f"source={recheck_source} dest={recheck_dest} "
            f"(gated={source_identity}); row and BOTH copies preserved"
        )

    # Final reparse freedom re-check immediately before removal.
    _refuse_tree_reparses("source", source)
    _refuse_tree_reparses("destination", dest)
    _remove_tree_readonly_only(source)
    if source.exists() or not dest.exists():
        raise RuntimeError(
            f"removal verification failed: source_exists={source.exists()} "
            f"dest_exists={dest.exists()}; manifest row retained"
        )
    return row


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            digest.update(rel.encode("utf-8"))
            digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("utf-8"))
            digest.update(b"\0")
    return digest.hexdigest()


def tree_bytes(root: Path) -> int:
    """Count file content only; directory inode sizes vary across volumes."""

    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def stage(path: Path, *, reason: str) -> dict:
    path = path.resolve()
    if not path.exists():
        raise SystemExit(f"path does not exist: {path}")
    if not QUARANTINE_ROOT.exists():
        raise SystemExit(f"quarantine root missing: {QUARANTINE_ROOT} (is D: mounted?)")
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    dest = QUARANTINE_ROOT / date / f"{uuid.uuid4().hex[:8]}-{path.name}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if path.is_dir():
        shutil.copytree(path, dest)
    else:
        shutil.copy2(path, dest)
    source_bytes = (
        tree_bytes(path)
        if path.is_dir()
        else path.stat().st_size
    )
    source_sha256 = (
        tree_sha256(path)
        if path.is_dir()
        else hashlib.sha256(path.read_bytes()).hexdigest()
    )
    staged_bytes = (
        tree_bytes(dest)
        if dest.is_dir()
        else dest.stat().st_size
    )
    staged_sha256 = (
        tree_sha256(dest)
        if dest.is_dir()
        else hashlib.sha256(dest.read_bytes()).hexdigest()
    )
    if (staged_bytes, staged_sha256) != (source_bytes, source_sha256):
        raise SystemExit(
            "staged quarantine copy does not reproduce the source identity: "
            f"source=({source_bytes}, {source_sha256}) "
            f"staged=({staged_bytes}, {staged_sha256})"
        )
    row = {
        "id": dest.name,
        "original": str(path),
        "staged": str(dest),
        "stagedAtUtc": utc_now(),
        "bytes": staged_bytes,
        "sha256": staged_sha256,
        "reason": reason,
    }
    with MANIFEST.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row) + "\n")
        stream.flush()
    shutil.rmtree(path) if path.is_dir() else path.unlink()
    return row


def restore(row_id: str) -> dict:
    rows = [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip()]
    match = [r for r in rows if r["id"] == row_id]
    if not match:
        raise SystemExit(f"no staged row with id {row_id}")
    row = match[-1]
    staged = Path(row["staged"])
    original = Path(row["original"])
    if not staged.exists():
        raise SystemExit(f"staged copy missing: {staged}")
    if original.exists():
        raise SystemExit(f"refusing to overwrite existing path: {original}")
    original.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(staged), str(original))
    remaining = [r for r in rows if r["id"] != row_id]
    MANIFEST.write_text("\n".join(json.dumps(r) for r in remaining) + ("\n" if remaining else ""), encoding="utf-8")
    return row


def purge(row_id: str, *, reason: str) -> dict:
    rows = [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip()]
    match = [r for r in rows if r["id"] == row_id]
    if not match:
        raise SystemExit(f"no staged row with id {row_id}")
    row = match[-1]
    staged = Path(row["staged"])
    if staged.exists():
        shutil.rmtree(staged) if staged.is_dir() else staged.unlink()
    with PURGE_LOG.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({**row, "purgedAtUtc": utc_now(), "purgeReason": reason}) + "\n")
    remaining = [r for r in rows if r["id"] != row_id]
    MANIFEST.write_text("\n".join(json.dumps(r) for r in remaining) + ("\n" if remaining else ""), encoding="utf-8")
    return row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_stage = sub.add_parser("stage")
    p_stage.add_argument("path")
    p_stage.add_argument("--reason", required=True)
    p_resume = sub.add_parser(
        "resume",
        help="audited completion of an interrupted stage into an existing "
             "D:\\lab-quarantine partial (never restarts from scratch)")
    p_resume.add_argument("source", help="the original un-removed source path")
    p_resume.add_argument("dest", help="the existing interrupted-stage partial under D:\\lab-quarantine")
    p_resume.add_argument("--reason", required=True)
    p_restore = sub.add_parser("restore")
    p_restore.add_argument("id")
    p_purge = sub.add_parser("purge")
    p_purge.add_argument("id")
    p_purge.add_argument("--reason", required=True)
    p_list = sub.add_parser("list")
    args = parser.parse_args(argv)

    if args.command == "stage":
        row = stage(Path(args.path), reason=args.reason)
    elif args.command == "resume":
        row = resume(Path(args.source), Path(args.dest), reason=args.reason)
    elif args.command == "restore":
        row = restore(args.id)
    elif args.command == "purge":
        row = purge(args.id, reason=args.reason)
    else:
        if MANIFEST.exists():
            for line in MANIFEST.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    print(f"{r['id']}  {r['stagedAtUtc'][:19]}  {r['original']}")
        return 0
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
