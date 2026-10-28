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
Generated reports contain private retail-derived names and must stay in this
worktree's ignored local-data/. The Linux CLI uses new-file-only, source-protected
publication; it refuses on other hosts or when atomic no-replace is unavailable.

Example:
  python tools/model_transform_catalog.py --mesh /path/to/m_thing.msh.aya \\
      --out local-data/model-transforms/selected.json
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
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rebuild" / "tools"))
from aya_archive_inventory import inflate_aya_bytes, read_held_archive  # noqa: E402
from cmsh_static_preview import parse_cmsh_stream  # noqa: E402
from safe_generated_output import SecuredOutputRoot  # noqa: E402

SCHEMA = "onslaught.model-transform-catalog.v1"
MAX_INPUTS = 512
MAX_TOTAL_PARTS = 12000
MAX_TOTAL_VIRTUAL_FRAMES = 1000000
ORTHOGONAL_TOLERANCE = 0.0001
KINDS = ("proper", "reflected", "nonOrthogonal")


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


def report_for(paths: list[Path]) -> dict[str, Any]:
    if not 1 <= len(paths) <= MAX_INPUTS:
        raise ValueError(f"select between 1 and {MAX_INPUTS} mesh files")
    # Reject duplicate names in the selection; it makes the ordinal an unambiguous occurrence coordinate.
    normalized = [os.path.normcase(os.path.abspath(path)) for path in paths]
    if len(set(normalized)) != len(normalized):
        raise ValueError("the same input path was selected more than once")
    rows = []
    total_parts = total_frames = 0
    for ordinal, path in enumerate(paths):
        source = read_held_archive(path)
        stream = inflate_aya_bytes(source)
        row = analyse_stream(stream, source_name=path.name, source_sha256=hashlib.sha256(source).hexdigest())
        total_parts += len(row["parts"])
        total_frames += sum(part["virtualFrameCount"] for part in row["parts"])
        if total_parts > MAX_TOTAL_PARTS or total_frames > MAX_TOTAL_VIRTUAL_FRAMES:
            raise ValueError("selected meshes exceed the model-report part or virtual-frame limit")
        rows.append({"selectionOrdinal": ordinal, **row})
    return {
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


def output_allowed(path: Path) -> bool:
    if ".." in path.parts:
        return False
    target = Path(os.path.abspath(path))
    allowed = Path(os.path.abspath(ROOT / "local-data"))
    try:
        if os.path.commonpath((str(target), str(allowed))) != str(allowed):
            return False
    except ValueError:
        return False
    checked = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", str(target)],
                             capture_output=True, check=False)
    return checked.returncode == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=Path, action="append", required=True, help="selected loose PC mesh AYA; repeatable")
    parser.add_argument("--out", type=Path, required=True, help="new report below this checkout's ignored local-data")
    args = parser.parse_args(argv)
    if not sys.platform.startswith("linux"):
        parser.error("this CLI requires Linux and atomic no-replace publication")
    if not output_allowed(args.out):
        parser.error("--out must be below this checkout's ignored local-data and cannot contain '..'")
    output = Path(os.path.abspath(args.out))
    try:
        report = report_for(args.mesh)
        payload = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
        with SecuredOutputRoot(output.parent, protected_sources=args.mesh) as secured:
            with secured.atomic_text_writer(output, replace_existing=False) as writer:
                writer.write(payload)
    except (ValueError, OSError, RuntimeError) as error:
        print(f"model transform catalog failed: {error}", file=sys.stderr)
        return 2
    print(f"Wrote metadata for {len(report['meshes'])} selected mesh(es): {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
