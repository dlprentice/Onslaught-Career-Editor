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

Enumeration and hashing are OPERATION-BOUND no-follow (2026-08-24): a
verified non-reparse directory/file object is pinned with
replacement-denying sharing (Windows ``CreateFileW`` +
``FILE_FLAG_OPEN_REPARSE_POINT``, read-only share mode; POSIX ``O_NOFOLLOW``
fds), and only that pinned object is enumerated or read -- a pathname
swapped to a junction/symlink after any earlier proof refuses inside the
pin, so no external target is ever scandir'd, opened, or hashed.

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
FILE_ATTRIBUTE_DIRECTORY = 0x10

# -- Operation-bound no-follow primitives ------------------------------------
#
# A path-only proof followed by a separate pathname syscall is still a
# TOCTOU: the swap can land after the proof and before the syscall. These
# primitives bind every enumeration/read to a VERIFIED,
# REPLACEMENT-DENYING pin on the opened object itself:
#
#   * ``CreateFileW`` with ``FILE_FLAG_OPEN_REPARSE_POINT`` opens the FINAL
#     component as ITSELF -- a reparse opens its link body, never its
#     target, so the pin cannot silently point at external content;
#   * sharing grants only ``FILE_SHARE_READ``, excluding WRITE and DELETE:
#     while held, rename/replace/delete of the pinned name and content
#     rewrites fail (WinError 32), so the verified name->object binding
#     cannot change hands under the pin;
#   * the opened object is then verified through the HANDLE (never through
#     the path): disk device type, no reparse attribute, and the required
#     directory/file type. Any swapped-in reparse therefore refuses before
#     one byte of its target is touched;
#   * POSIX binds the same way with ``O_NOFOLLOW`` descriptors plus
#     fstat-vs-lstat identity (documented residual: POSIX permits renaming
#     an open directory, so there the pin narrows but does not eliminate
#     replacement; the authoritative host for quarantine holdings is
#     Windows, where the share mode denies replacement outright).
#
# Enumeration and hashing then happen while the pin (and every ancestor
# pin down the walked chain) is held: ``scandir`` on the pinned pathname
# can only ever answer for the verified object, and file bytes are read
# straight through the verified handle.

_GENERIC_READ = 0x80000000
_FILE_LIST_DIRECTORY = 0x00000001
_FILE_READ_ATTRIBUTES = 0x00000080
_SYNCHRONIZE = 0x00100000
_FILE_SHARE_READ = 0x1
_FILE_SHARE_WRITE = 0x2
_FILE_SHARE_DELETE = 0x4
_OPEN_EXISTING = 3
_FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
_FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
_FILE_TYPE_DISK = 0x1


class _PinnedPlainDirectory:
    """Replacement-denying pin proving one pathname is STILL a plain
    directory, held for the duration of the enumeration bound to it."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._handle: int | None = None
        # Seam proof first: the named fresh-verdict guards stay the visible
        # refusal layer for deterministic replacements (and fail fast
        # before any handle exists).
        _reprove_plain_directory(path)
        if os.name == "nt":
            handle, attributes, file_type = _windows_pin_open(
                path, directory=True
            )
            try:
                if file_type != _FILE_TYPE_DISK:
                    raise RuntimeError(
                        f"fail-closed: pinned directory {path} is not on a "
                        "disk filesystem (file type "
                        f"{file_type:#x}); refusing to enumerate it"
                    )
                if attributes & FILE_ATTRIBUTE_REPARSE_POINT:
                    raise RuntimeError(
                        f"fail-closed: pinned directory pathname {path} "
                        "resolved to a reparse point when opened as itself "
                        "(junction/symlink/device); quarantine refuses to "
                        "enumerate through its target"
                    )
                if not attributes & FILE_ATTRIBUTE_DIRECTORY:
                    raise RuntimeError(
                        f"fail-closed: pinned pathname {path} opened as a "
                        "non-directory object; quarantine traversal refuses"
                    )
            except BaseException:
                _close_windows_handle(handle)
                raise
            self._handle = handle
        else:
            import stat as stat_module

            posix_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            if hasattr(os, "O_DIRECTORY"):
                posix_flags |= os.O_DIRECTORY
            try:
                self._posix_fd = os.open(path, posix_flags)
            except OSError as error:
                raise RuntimeError(
                    f"fail-closed: directory pathname {path} could not be "
                    f"pinned no-follow ({error}); quarantine traversal "
                    "refuses to enumerate it"
                ) from None
            try:
                pinned_stat = os.fstat(self._posix_fd)
                name_stat = path.lstat()  # fresh final-component identity
                if not stat_module.S_ISDIR(pinned_stat.st_mode) \
                        or stat_module.S_ISLNK(name_stat.st_mode) \
                        or (pinned_stat.st_dev, pinned_stat.st_ino) != (
                            name_stat.st_dev, name_stat.st_ino):
                    raise RuntimeError(
                        f"fail-closed: pinned directory {path} does not "
                        "match its fresh no-follow identity; quarantine "
                        "refuses a replaced or linked directory"
                    )
            except BaseException:
                os.close(self._posix_fd)
                self._posix_fd = None
                raise

    def __enter__(self) -> "_PinnedPlainDirectory":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        self.close()

    def close(self) -> None:
        if os.name == "nt":
            if self._handle is not None:
                _close_windows_handle(self._handle)
                self._handle = None
        elif getattr(self, "_posix_fd", None) is not None:
            os.close(self._posix_fd)
            self._posix_fd = None


class _PinnedPlainFile:
    """Replacement-denying pin whose reads stream THROUGH the verified
    handle -- hashed bytes can only come from the proven plain object."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._handle: int | None = None
        self._posix_fd: int | None = None
        # Seam proof first (same rationale as the directory pin).
        if _is_reparse_point(path) or _lstat_is_reparse_point(path):
            raise RuntimeError(
                f"fail-closed: file pathname {path} became a reparse point "
                "after it was classified; quarantine refuses to open, "
                "stat, or hash through its target"
            )
        if os.name == "nt":
            handle, attributes, file_type = _windows_pin_open(
                path, directory=False
            )
            try:
                if file_type != _FILE_TYPE_DISK:
                    raise RuntimeError(
                        f"fail-closed: pinned file {path} is not on a disk "
                        f"filesystem (file type {file_type:#x}); refusing "
                        "to read it"
                    )
                if attributes & FILE_ATTRIBUTE_REPARSE_POINT:
                    raise RuntimeError(
                        f"fail-closed: pinned file pathname {path} "
                        "resolved to a reparse point when opened as itself "
                        "(symlink/junction); quarantine refuses to read "
                        "any byte through its target"
                    )
                if attributes & FILE_ATTRIBUTE_DIRECTORY:
                    raise RuntimeError(
                        f"fail-closed: pinned pathname {path} opened as a "
                        "directory object; quarantine refuses to hash it "
                        "as a file"
                    )
            except BaseException:
                _close_windows_handle(handle)
                raise
            self._handle = handle
        else:
            import stat as stat_module

            posix_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            if hasattr(os, "O_BINARY"):
                posix_flags |= os.O_BINARY
            try:
                self._posix_fd = os.open(path, posix_flags)
            except OSError as error:
                raise RuntimeError(
                    f"fail-closed: file pathname {path} could not be "
                    f"pinned no-follow ({error}); quarantine refuses to "
                    "read it"
                ) from None
            try:
                pinned_stat = os.fstat(self._posix_fd)
                name_stat = path.lstat()
                if not stat_module.S_ISREG(pinned_stat.st_mode) \
                        or stat_module.S_ISLNK(name_stat.st_mode) \
                        or (pinned_stat.st_dev, pinned_stat.st_ino) != (
                            name_stat.st_dev, name_stat.st_ino):
                    raise RuntimeError(
                        f"fail-closed: pinned file {path} does not match "
                        "its fresh no-follow identity; quarantine refuses "
                        "a replaced or linked file"
                    )
            except BaseException:
                os.close(self._posix_fd)
                self._posix_fd = None
                raise

    def __enter__(self) -> "_PinnedPlainFile":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        self.close()

    def read_all_hashed(self) -> tuple[int, str]:
        """Stream every byte THROUGH the pinned object into sha256; return
        ``(byte_count, hex_digest)`` measured over exactly those bytes."""
        if os.name == "nt":
            import msvcrt

            assert self._handle is not None
            try:
                fd = msvcrt.open_osfhandle(
                    self._handle, os.O_RDONLY | os.O_BINARY
                )
            except OSError as error:
                raise RuntimeError(
                    f"fail-closed: pinned file {self._path} handle could "
                    f"not be adopted for streaming ({error})"
                ) from None
            self._handle = None  # the fd now owns the Windows handle
            try:
                return _stream_fd_hashed(fd)
            finally:
                os.close(fd)  # closes the underlying handle too
        assert self._posix_fd is not None
        try:
            return _stream_fd_hashed(self._posix_fd)
        finally:
            os.close(self._posix_fd)
            self._posix_fd = None

    def close(self) -> None:
        if os.name == "nt":
            if self._handle is not None:
                _close_windows_handle(self._handle)
                self._handle = None
        elif self._posix_fd is not None:
            os.close(self._posix_fd)
            self._posix_fd = None


def _stream_fd_hashed(fd: int) -> tuple[int, str]:
    data_sha = hashlib.sha256()
    total = 0
    while True:
        chunk = os.read(fd, 1024 * 1024)
        if not chunk:
            break
        data_sha.update(chunk)
        total += len(chunk)
    return total, data_sha.hexdigest()


def _windows_pin_open(
    path: Path, *, directory: bool
) -> tuple[int, int, int]:
    """Open ``path``'s FINAL component as itself with replacement-denying
    sharing. Returns ``(handle, file_attributes, file_type)``. Raises
    ``RuntimeError`` on any refusal (the handle, when opened, is closed)."""

    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.windll.kernel32
    access = (
        (_FILE_LIST_DIRECTORY if directory else _GENERIC_READ)
        | _FILE_READ_ATTRIBUTES
        | _SYNCHRONIZE
    )
    # Replacement-denying share mode: read-sharing only. Excluding WRITE
    # blocks content rewrites; excluding DELETE blocks rename/replace/
    # unlink of the pinned name while the pin is held.
    share_mode = _FILE_SHARE_READ
    flags = _FILE_FLAG_BACKUP_SEMANTICS | _FILE_FLAG_OPEN_REPARSE_POINT
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
    ]
    handle = kernel32.CreateFileW(
        str(path), access, share_mode, None, _OPEN_EXISTING, flags, None
    )
    if not handle or handle == wintypes.HANDLE(-1).value:
        error_code = kernel32.GetLastError()
        raise RuntimeError(
            f"fail-closed: quarantine pin could not open {path} as itself "
            f"(CreateFileW error {error_code}); a vanished, shared, or "
            "inaccessible pathname refuses rather than races"
        )

    class _BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("dwFileAttributes", wintypes.DWORD),
            ("ftCreationTime", wintypes.FILETIME),
            ("ftLastAccessTime", wintypes.FILETIME),
            ("ftLastWriteTime", wintypes.FILETIME),
            ("dwVolumeSerialNumber", wintypes.DWORD),
            ("nFileSizeHigh", wintypes.DWORD),
            ("nFileSizeLow", wintypes.DWORD),
            ("nNumberOfLinks", wintypes.DWORD),
            ("nFileIndexHigh", wintypes.DWORD),
            ("nFileIndexLow", wintypes.DWORD),
        ]

    info = _BY_HANDLE_FILE_INFORMATION()
    if not kernel32.GetFileInformationByHandle(
        wintypes.HANDLE(handle), ctypes.byref(info)
    ):
        error_code = kernel32.GetLastError()
        kernel32.CloseHandle(wintypes.HANDLE(handle))
        raise RuntimeError(
            f"fail-closed: quarantine pin could not verify {path} through "
            f"its own handle (GetFileInformationByHandle error "
            f"{error_code}); refusing without trusting the pathname"
        )
    kernel32.GetFileType.restype = wintypes.DWORD
    kernel32.GetFileType.argtypes = [wintypes.HANDLE]
    file_type = kernel32.GetFileType(wintypes.HANDLE(handle))
    return handle, info.dwFileAttributes, file_type


def _close_windows_handle(handle: int) -> None:
    import ctypes

    ctypes.windll.kernel32.CloseHandle(ctypes.c_void_p(handle))


def _pinned_plain_directory(path: Path) -> _PinnedPlainDirectory:
    return _PinnedPlainDirectory(path)


def _pinned_plain_file(path: Path) -> _PinnedPlainFile:
    return _PinnedPlainFile(path)


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


def _describe_path_state(path: Path) -> str:
    """Human-readable no-follow state of ``path``'s final component."""

    try:
        mode = path.lstat().st_mode
    except OSError:
        return "absent"
    import stat as stat_module

    if stat_module.S_ISLNK(mode):
        return "symbolic link"
    if stat_module.S_ISDIR(mode):
        return "a directory"
    return "a non-directory"


def _reprove_plain_directory(path: Path) -> None:
    """Freshly prove ``path`` is STILL a plain directory -- right now.

    An earlier "plain" verdict is stale the moment it is written down: a
    queued pathname can be replaced by a directory symlink/junction (or
    vanish) between its classification and its turn for descent. This is
    the fresh final-component truth that must gate EVERY scandir/descent:
    any reparse answer refuses before the target is enumerated, and a path
    that can no longer be proven a plain directory at all fails closed.
    """

    if _is_reparse_point(path) or _lstat_is_reparse_point(path):
        raise RuntimeError(
            f"fail-closed: directory pathname {path} became a reparse point "
            "after it was classified; quarantine refuses to descend into or "
            "enumerate through its target"
        )
    if not path.is_dir():
        raise RuntimeError(
            f"fail-closed: directory pathname {path} is no longer a provably "
            f"plain directory ({_describe_path_state(path)}); quarantine "
            "traversal refuses a replaced or vanished directory"
        )


def _scan_plain_children(directory: Path) -> list[tuple[Path, str]]:
    """One no-follow scan of ``directory``, classified and fail-closed.

    MUST be called while the caller holds a verified
    ``_pinned_plain_directory`` on ``directory``: the pathname handed to
    ``os.scandir`` here is the pinned object's own name, frozen against
    rename/replace/delete by the pin's replacement-denying share mode, so a
    swap landing after the caller's reproof cannot reach this syscall as a
    different object -- and if the name somehow no longer answers for the
    pin, the pin-vs-scan identity check below refuses.

    Raises RuntimeError when the scan fails (vanished directory, sharing
    violation, permission denial), when any entry cannot be classified
    without following it, or when the scanned object is not the one the
    caller pinned.
    """

    children: list[tuple[Path, str]] = []
    try:
        with os.scandir(directory) as scan:
            # The caller's verified pin owns this name->object binding;
            # every entry below answers for the pinned object only.
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

    OPERATION-BOUND no-follow walk: each directory is opened through
    ``_pinned_plain_directory`` -- a verified non-reparse disk-directory
    handle with replacement-denying sharing -- and only that verified
    object's pathname reaches ``os.scandir``, so a queued child replaced by
    a reparse after its parent's scan (or after its own descent-time
    reproof) refuses inside the pin before any target scandir. Entries are
    classified from their own link stat BEFORE any descent; external
    content behind a junction or symlink is neither enumerated nor hashed.
    Scan failures refuse immediately.
    """

    pending = [root]
    while pending:
        current = pending.pop()
        with _pinned_plain_directory(current):
            for child_path, kind in _scan_plain_children(current):
                if kind == "dir":
                    pending.append(child_path)
                else:
                    yield child_path


def _reparse_census(root: Path) -> list[str]:
    """No-follow inventory of every reparse point at/under ``root``.

    Returns relative POSIX paths ("." denotes the root itself). Enumeration
    is OPERATION-BOUND: every directory scan runs while a verified
    replacement-denying pin on that exact directory is held, so a pathname
    swapped to a reparse after any earlier verdict refuses inside the pin
    -- ``os.scandir`` can never reach a replaced reparse pathname or its
    target. A reparse root reports itself as "."; a directory that cannot
    be scanned fails closed.
    """

    if _is_reparse_point(root):
        return ["."]
    found: list[str] = []
    pending = [root]
    while pending:
        current = pending.pop()
        # The pin fresh-proves the pathname (reproof first, then a
        # non-reparse disk-directory handle with replacement-denying
        # sharing). A queued child replaced after its parent's
        # classification refuses HERE -- before its name can reach scandir.
        try:
            with _pinned_plain_directory(current):
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
        except RuntimeError as error:
            if current == root:
                raise
            found.append(current.relative_to(root).as_posix())
            continue
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

    OPERATION-BOUND no-follow walk: directories are enumerated only through
    verified replacement-denying pins (see ``_iter_plain_files``), and every
    file's bytes are hashed straight THROUGH its own verified
    ``_pinned_plain_file`` handle -- an open primitive that opens the final
    component as itself and refuses any reparse before one byte is read.
    The root itself, any nested entry that cannot be proven a plain
    directory or file, and any scan failure all refuse before any hashing;
    a swap landing after classification, after the descent-time proof, or
    after the final path verdict refuses inside the pin -- external target
    bytes are never opened, read, or blessed. Digest order matches
    stage()'s pathlib-sorted semantics exactly.
    """

    if _is_reparse_point(root):
        raise RuntimeError(
            f"identity computation refused: tree root itself is a reparse point: {root}"
        )
    count = 0
    total_bytes = 0
    digest = hashlib.sha256()
    for path in sorted(_iter_plain_files(root)):
        # Operation-bound open: the pin re-proves the slot fresh and then
        # opens it AS ITSELF with replacement-denying sharing; a swapped-in
        # symlink/junction refuses here without Path.open ever running on
        # the pathname. Bytes stream through that verified object only --
        # size and digest are measured over the pinned bytes themselves,
        # so no post-open path check can ever be needed or fooled.
        rel = path.relative_to(root).as_posix()
        with _pinned_plain_file(path) as pinned:
            file_bytes, data_hex = pinned.read_all_hashed()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(data_hex.encode("utf-8"))
        digest.update(b"\0")
        count += 1
        total_bytes += file_bytes
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
