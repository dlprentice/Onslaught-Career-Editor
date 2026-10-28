#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Summarise parent-relative CMSH orientation keys for model/animation preservation.

For explicitly selected PC loose-mesh AYA files, this reports per-part counts
of stored HORI orientation keys and of the keys/virtual frames named by VHFM.
It detects orthonormal matrices with negative determinant: these cannot be
represented by a rotation alone. It exports metadata and hashes only, never
matrices, positions, geometry, or the source file's bytes.

Only the root CMSH is analysed. A frame-map reference is not proof that a game
mode selects that frame, and a parent-relative reflection is not necessarily a
model/world-space reflection. Interpolation, animation scheduling, appearance,
non-root chained meshes, and exporter correctness are outside this report.
Generated reports contain private retail-derived names and hashes: do not publish
them or add them to Git. The CLI emits the report only to stdout and does not
open a report file. If a caller redirects or saves the output, the caller is
responsible for the destination and privacy; a shell opens its redirection before
the CLI runs, outside the CLI's control. The report_bytes API returns UTF-8 JSON.
The selected-file API and CLI require Linux O_PATH, descriptor-relative no-follow
opens and /proc/self/fd. They reject parent path components, symlinks in any
input component and multi-link files, and perform bounded reads. They recheck
the source identities before returning or emitting a report. Identity and timestamps
detect many changes, but this is not an atomic filesystem snapshot or a lock;
compare the recorded source hash before using the report.
analyse_stream accepts already-owned bytes on other platforms, with the caller
responsible for their identity and source name. The report schema validates
structure, not consistency among all counts, ordinals and ranges.

Example:
  python tools/model_transform_catalog.py --mesh /path/to/m_thing.msh.aya --stdout
Repeat --mesh for up to 512 explicitly selected files.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rebuild" / "tools"))
from aya_archive_inventory import MAX_COMPRESSED_BYTES, inflate_aya_bytes  # noqa: E402
from cmsh_static_preview import parse_cmsh_stream  # noqa: E402

SCHEMA = "onslaught.model-transform-catalog.v1"
MAX_INPUTS = 512
MAX_TOTAL_PARTS = 12000
MAX_TOTAL_VIRTUAL_FRAMES = 1000000
ORTHOGONAL_TOLERANCE = 0.0001
KINDS = ("proper", "reflected", "nonOrthogonal")
HAS_OPEN_DIR_FD = os.open in os.supports_dir_fd


def classify_orientation(rows: tuple[tuple[float, ...], ...]) -> tuple[str, float]:
    """Classify one 3x3 local basis by row orthogonality and determinant.

    Reflected/proper require both orthogonality and |determinant| near one;
    malformed or non-finite matrices are refused, not silently called static.
    The returned error and classifications are numerical summaries, not a
    quaternion, extracted transform, geometry, or runtime playback result.
    """
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise ValueError("orientation must be a 3 by 3 matrix")
    if any(not math.isfinite(x) for row in rows for x in row):
        raise ValueError("orientation contains a non-finite value")
    error = max(abs(sum(rows[i][k] * rows[j][k] for k in range(3)) - (1 if i == j else 0))
                for i in range(3) for j in range(3))
    a, b, c = rows
    det = (a[0] * (b[1] * c[2] - b[2] * c[1]) -
           a[1] * (b[0] * c[2] - b[2] * c[0]) +
           a[2] * (b[0] * c[1] - b[1] * c[0]))
    if not math.isfinite(error) or not math.isfinite(det):
        raise ValueError("orientation classification overflowed")
    if error > ORTHOGONAL_TOLERANCE or abs(abs(det) - 1.0) > ORTHOGONAL_TOLERANCE:
        return "nonOrthogonal", error
    return ("reflected" if det < 0 else "proper"), error


def counts(values: list[str]) -> dict[str, int]:
    tally = collections.Counter(values)
    return {kind: tally[kind] for kind in KINDS}


def reflected_ranges(frame_types: list[str]) -> list[list[int]]:
    """Inclusive virtual-frame ranges whose selected local key is reflected."""
    ranges: list[list[int]] = []
    for frame, kind in enumerate(frame_types):
        if kind != "reflected":
            continue
        if ranges and ranges[-1][1] == frame - 1:
            ranges[-1][1] = frame
        else:
            ranges.append([frame, frame])
    return ranges


def analyse_stream(stream: bytes, *, source_name: str, source_sha256: str) -> dict[str, Any]:
    mesh = parse_cmsh_stream(stream)
    parts = []
    for ordinal, part in enumerate(mesh.file_parts()):
        track = part.track
        if track is None or not track.hierarchy or not track.frame_map:
            raise ValueError(f"part {ordinal} has no complete orientation track")
        if any(index >= len(track.hierarchy) for index in track.frame_map):
            raise ValueError(f"part {ordinal} frame map names an absent hierarchy pose")
        classified = [classify_orientation(pose.rows) for pose in track.hierarchy]
        types = [classification for classification, _ in classified]
        referenced = set(track.frame_map)
        frame_types = [types[index] for index in track.frame_map]
        parts.append({
            "ordinal": ordinal,
            "name": part.name,
            "parentOrdinal": part.parent,
            "hierarchyPoseCount": len(types),
            "virtualFrameCount": len(track.frame_map),
            "storedKeys": counts(types),
            "referencedDistinctKeys": counts([types[index] for index in sorted(referenced)]),
            "virtualFrameReferences": counts(frame_types),
            "reflectedKeyOrdinals": [index for index, kind in enumerate(types) if kind == "reflected"],
            "reflectedVirtualFrameRanges": reflected_ranges(frame_types),
            "unreferencedKeyCount": len(types) - len(referenced),
            "maxRowOrthogonalityError": max(error for _, error in classified),
        })
    nested = sum(sibling.tag in (b"PMS2", b"PMSH") for sibling in mesh.siblings)
    return {
        "source": {"name": source_name, "archiveSha256": source_sha256,
                   "inflatedCmshStreamSha256": hashlib.sha256(stream).hexdigest()},
        "meshName": mesh.name,
        "parts": parts,
        "summary": {
            "parts": len(parts),
            "partsWithStoredReflectedKeys": sum(row["storedKeys"]["reflected"] > 0 for row in parts),
            "partsWithReferencedReflectedKeys": sum(row["referencedDistinctKeys"]["reflected"] > 0 for row in parts),
            "partsWithNonOrthogonalKeys": sum(row["storedKeys"]["nonOrthogonal"] > 0 for row in parts),
            "nestedMeshSiblingCandidatesNotAnalysed": nested,
        },
    }


def _selected_path(path: Path) -> Path:
    """Reject parent traversal before normalization can erase a symlink/.. pair."""
    path = Path(path)
    if ".." in path.parts:
        raise ValueError("selected input may not contain a parent path component")
    if (not sys.platform.startswith("linux") or not all(hasattr(os, flag) for flag in
            ("O_PATH", "O_NOFOLLOW", "O_DIRECTORY", "O_CLOEXEC", "O_NONBLOCK")) or not HAS_OPEN_DIR_FD):
        raise ValueError("safe selected-file reading requires Linux descriptor-relative O_PATH support")
    return Path(os.path.abspath(path))


def _open_selected_path(path: Path) -> int:
    """Hold the named object without following any symlink or opening a special file for reading."""
    current = os.open(path.anchor, os.O_PATH | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for index, name in enumerate(path.parts[1:]):
            flags = os.O_PATH | os.O_NOFOLLOW | os.O_CLOEXEC
            if index < len(path.parts) - 2:
                flags |= os.O_DIRECTORY
            child = os.open(name, flags, dir_fd=current)
            os.close(current)
            current = child
        return current
    except BaseException:
        os.close(current)
        raise


def _input_stamp(metadata: os.stat_result) -> tuple[int, ...]:
    return (metadata.st_dev, metadata.st_ino, metadata.st_mode, metadata.st_size,
            metadata.st_mtime_ns, metadata.st_ctime_ns, metadata.st_nlink)


def _require_regular_source(metadata: os.stat_result) -> None:
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError("selected input is not a regular file or has a symlink component")
    if metadata.st_nlink != 1:
        raise ValueError("selected input must have exactly one hard link")
    if metadata.st_size < 0 or metadata.st_size > MAX_COMPRESSED_BYTES:
        raise ValueError("selected input exceeds the compressed-byte limit")


def _read_selected_mesh(path: Path) -> tuple[bytes, tuple[int, ...]]:
    """Read one held regular inode and detect metadata-visible changes or replacement during the bounded read."""
    held = _open_selected_path(path)
    try:
        before = os.fstat(held)
        _require_regular_source(before)
        stamp = _input_stamp(before)
        # /proc reopens the already-held O_PATH inode, not the user-controlled pathname. A FIFO or device
        # substituted at that pathname cannot be opened for reading; absent procfs fails closed.
        fd = os.open(f"/proc/self/fd/{held}", os.O_RDONLY | os.O_NONBLOCK | os.O_CLOEXEC)
        try:
            if _input_stamp(os.fstat(fd)) != stamp:
                raise ValueError("selected input changed while opening")
            chunks, size = [], 0
            while True:
                chunk = os.read(fd, min(1024 * 1024, MAX_COMPRESSED_BYTES - size + 1))
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_COMPRESSED_BYTES:
                    raise ValueError("selected input exceeds the compressed-byte limit")
                chunks.append(chunk)
            if size != before.st_size or _input_stamp(os.fstat(fd)) != stamp or _input_stamp(os.fstat(held)) != stamp:
                raise ValueError("selected input changed during reading")
        finally:
            os.close(fd)
        named = _open_selected_path(path)
        try:
            if _input_stamp(os.fstat(named)) != stamp:
                raise ValueError("selected input path changed during reading")
        finally:
            os.close(named)
        return b"".join(chunks), stamp
    finally:
        os.close(held)


def _check_input_bindings(bindings: list[tuple[Path, tuple[int, ...]]]) -> None:
    """Recheck the selected input metadata before returning or emitting a report."""
    for path, stamp in bindings:
        fd = _open_selected_path(path)
        try:
            if _input_stamp(os.fstat(fd)) != stamp:
                raise ValueError("selected input changed before report emission")
        finally:
            os.close(fd)


def _report_for(paths: list[Path]) -> tuple[dict[str, Any], list[tuple[Path, tuple[int, ...]]]]:
    if not 1 <= len(paths) <= MAX_INPUTS:
        raise ValueError(f"select between 1 and {MAX_INPUTS} mesh files")
    selected = [_selected_path(path) for path in paths]
    # A selection ordinal distinguishes different files with the same basename; duplicate paths or inodes are refused.
    normalized = [os.path.normcase(os.fspath(path)) for path in selected]
    if len(set(normalized)) != len(normalized):
        raise ValueError("the same input path was selected more than once")
    rows, bindings, seen_inodes = [], [], set()
    total_parts = total_frames = 0
    for ordinal, path in enumerate(selected):
        source, stamp = _read_selected_mesh(path)
        if stamp[:2] in seen_inodes:
            raise ValueError("the same input file was selected more than once")
        seen_inodes.add(stamp[:2])
        bindings.append((path, stamp))
        stream = inflate_aya_bytes(source)
        row = analyse_stream(stream, source_name=path.name, source_sha256=hashlib.sha256(source).hexdigest())
        total_parts += len(row["parts"])
        total_frames += sum(part["virtualFrameCount"] for part in row["parts"])
        if total_parts > MAX_TOTAL_PARTS or total_frames > MAX_TOTAL_VIRTUAL_FRAMES:
            raise ValueError("selected meshes exceed the model-report part or virtual-frame limit")
        rows.append({"selectionOrdinal": ordinal, **row})
    report = {
        "schema": SCHEMA,
        "generatedRetailDerived": True,
        "basis": {
            "coordinates": "stored part-local orientations; parent transforms are not composed",
            "classification": "row dot-products and determinant, with the stated absolute tolerance",
            "tolerance": ORTHOGONAL_TOLERANCE,
            "selection": "VHFM frame-map references only; reflected ranges are inclusive; no animation mode, playback or rendering asserted",
            "coverage": "root CMSH only; nested mesh siblings are counted as candidates, not parsed",
            "evidence": "reverse-engineering/asset-formats/cmsh-animation-keys.md; "
                        "onslaught-decomp CMeshPart::BuildCache @004b1a40 and "
                        "CMeshPart::EvaluateAnimatedTransform @004b5330",
        },
        "meshes": rows,
    }
    return report, bindings


def report_for(paths: list[Path]) -> dict[str, Any]:
    """Return metadata for bounded Linux file reads; callers must check hashes for later file changes."""
    report, bindings = _report_for(paths)
    _check_input_bindings(bindings)
    return report


def report_bytes(paths: list[Path]) -> bytes:
    """Return deterministic UTF-8 JSON; the caller controls any persistence or disclosure."""
    report, bindings = _report_for(paths)
    payload = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    _check_input_bindings(bindings)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=Path, action="append", required=True, help="selected loose PC mesh AYA; repeatable")
    parser.add_argument("--stdout", action="store_true", required=True,
                        help="emit private retail-derived metadata to stdout; caller controls any redirection")
    args = parser.parse_args(argv)
    try:
        payload = report_bytes(args.mesh)
        sys.stdout.write(payload.decode("utf-8"))
    except (ValueError, OSError, RuntimeError) as error:
        print(f"model transform catalog failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
