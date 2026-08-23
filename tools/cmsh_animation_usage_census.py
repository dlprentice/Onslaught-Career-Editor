#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only CMSH animation, skinning, LVLR-membership, and MSL-use census.

The report contains names, counts, hashes, and relative source coordinates; it
never emits retail payload bytes. Generated reports must stay under an ignored
``local-lab`` or ``.artifacts`` directory.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rebuild" / "tools"))

from cmsh_static_preview import inflate_aya, parse_cmsh_stream  # noqa: E402
from aya_archive_inventory import (  # noqa: E402
    inflate_aya_bytes,
    parse_top_level_chunks,
    read_held_archive,
)
from aya_cross_platform_compare import logical_key  # noqa: E402
from safe_generated_output import SecuredOutputRoot  # noqa: E402

SCHEMA = "onslaught.cmsh-animation-usage-census.v1"
INDEX_SCHEMA = "onslaught.asset-mirror-index.v1"
ANIMATION_CALL = re.compile(
    r'\b(PlayAnimationWait|PlayAnimation)\s*\(\s*"([^"]+)"\s*,\s*'
    r"([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)\s*\)",
    re.IGNORECASE,
)


def _normalized_basename(value: str) -> str:
    return PureWindowsPath(value.replace("/", "\\")).name.casefold()


def _source_mesh_name(path: Path) -> str:
    name = path.name
    if not name.casefold().endswith(".aya"):
        raise ValueError(f"mesh input is not an AYA file: {name}")
    return name[:-4]


def _motion_class(parts: tuple[Any, ...]) -> tuple[str, list[dict[str, object]]]:
    moving: list[dict[str, object]] = []
    for part_index, part in enumerate(parts):
        track = part.track
        if track is None or not track.frame_map:
            raise ValueError(f"part {part_index} has no rigid transform track")
        if max(track.frame_map) >= len(track.hierarchy):
            raise ValueError(f"part {part_index} has a frame-map index outside HORI/HPOS")
        if len(set(track.frame_map)) > 1:
            moving.append(
                {
                    "partIndex": part_index,
                    "partName": part.name,
                    "virtualFrames": len(track.frame_map),
                    "hierarchyFrames": len(track.hierarchy),
                    "closesOnStart": track.frame_map[0] == track.frame_map[-1],
                }
            )
    if not moving:
        return "no-nontrivial-frame-map", moving
    if all(bool(row["closesOnStart"]) for row in moving):
        return "all-moving-maps-close", moving
    if not any(bool(row["closesOnStart"]) for row in moving):
        return "no-moving-map-closes", moving
    return "mixed-moving-map-closure", moving


def _mesh_record(path: Path) -> tuple[dict[str, object], Any]:
    mesh = parse_cmsh_stream(inflate_aya(read_held_archive(path)))
    parts = mesh.file_parts()
    motion_class, moving = _motion_class(parts)
    carriers: list[dict[str, object]] = []
    for part_index, part in enumerate(parts):
        if not part.bones:
            continue
        slot_use = collections.Counter(
            slot
            for vertex in part.vertices
            if vertex.bone_slots is not None
            for slot in vertex.bone_slots
        )
        carriers.append(
            {
                "partIndex": part_index,
                "partName": part.name,
                "bonePartIndices": list(part.bones),
                "bonePartNames": [parts[index].name for index in part.bones],
                "vertexCount": len(part.vertices),
                "boneSlotUse": {str(index): slot_use[index] for index in sorted(slot_use)},
            }
        )
    hfov = [
        {
            "partIndex": part_index,
            "partName": part.name,
            "values": list(part.hfov or ()),
        }
        for part_index, part in enumerate(parts)
        if part.raw_hfov is not None
    ]
    a_frames = collections.Counter(part.anim_frames for part in parts)
    return (
        {
            "file": path.name,
            "internalName": mesh.name,
            "partCount": len(parts),
            "aFrameValueCounts": {str(value): a_frames[value] for value in sorted(a_frames)},
            "maxVirtualFrames": max(len(part.track.frame_map) for part in parts),
            "maxHierarchyFrames": max(len(part.track.hierarchy) for part in parts),
            "movingParts": moving,
            "motionClass": motion_class,
            "boneCarriers": carriers,
            "hfov": hfov,
        },
        mesh,
    )


def _animation_calls(script_root: Path) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for path in sorted(script_root.rglob("*.msl"), key=lambda item: item.as_posix().casefold()):
        text = read_held_archive(path).decode("utf-8")
        for line_number, line in enumerate(text.splitlines(), 1):
            active = line.split("//", 1)[0]
            for match in ANIMATION_CALL.finditer(active):
                rows.append(
                    {
                        "command": match.group(1),
                        "token": match.group(2),
                        "flag1": match.group(3),
                        "flag2": match.group(4),
                        "script": path.relative_to(script_root.parent).as_posix(),
                        "line": line_number,
                    }
                )
    commands = collections.Counter(str(row["command"]).casefold() for row in rows)
    tokens = collections.Counter(str(row["token"]) for row in rows)
    flags = collections.Counter((str(row["flag1"]), str(row["flag2"])) for row in rows)
    return {
        "sites": len(rows),
        "files": len({row["script"] for row in rows}),
        "levels": len({str(row["script"]).split("/")[1].casefold() for row in rows}),
        "commandCounts": dict(sorted(commands.items())),
        "tokenCounts": dict(sorted(tokens.items(), key=lambda item: (-item[1], item[0].casefold()))),
        "flagCounts": {f"{key[0]},{key[1]}": count for key, count in sorted(flags.items())},
        "rows": rows,
    }


def _level_mesh_membership(
    resource_root: Path,
    meshes: list[tuple[dict[str, object], Any]],
) -> dict[str, object]:
    loose_lookup: dict[str, str] = {}
    for record, _mesh in meshes:
        file_name = str(record["file"])
        key = _normalized_basename(_source_mesh_name(Path(file_name)))
        if key in loose_lookup:
            raise ValueError(f"duplicate loose mesh basename: {key}")
        loose_lookup[key] = file_name

    rows: list[dict[str, object]] = []
    occurrence_counts: collections.Counter[str] = collections.Counter()
    unresolved: collections.Counter[str] = collections.Counter()
    archives = [
        path
        for path in resource_root.glob("*_res_PC.aya")
        if path.name.split("_", 1)[0].isdigit()
    ]
    for path in sorted(archives, key=lambda item: item.name.casefold()):
        level = path.name.split("_", 1)[0]
        raw = inflate_aya_bytes(read_held_archive(path))
        for chunk in parse_top_level_chunks(raw):
            if chunk.tag != "MESH":
                continue
            payload = raw[chunk.offset + 8 : chunk.offset + 8 + chunk.size]
            _logical, display_name, method = logical_key("MESH", payload)
            lookup = _normalized_basename("m_" + display_name) if display_name else ""
            loose_mesh = loose_lookup.get(lookup)
            rows.append(
                {
                    "level": level,
                    "chunkIndex": chunk.index,
                    "displayName": display_name,
                    "logicalMethod": method,
                    "looseMesh": loose_mesh,
                }
            )
            if loose_mesh is None:
                unresolved[display_name] += 1
            else:
                occurrence_counts[loose_mesh] += 1

    levels_by_mesh = {
        file_name: sorted(
            {str(row["level"]) for row in rows if row["looseMesh"] == file_name}
        )
        for file_name in sorted(occurrence_counts)
    }
    return {
        "archives": len(archives),
        "meshChunks": len(rows),
        "resolvedOccurrences": sum(occurrence_counts.values()),
        "unresolvedOccurrences": sum(unresolved.values()),
        "uniqueResolvedLooseMeshes": len(occurrence_counts),
        "unresolvedNames": dict(sorted(unresolved.items())),
        "occurrencesByLooseMesh": dict(sorted(occurrence_counts.items())),
        "levelsByLooseMesh": levels_by_mesh,
        "rows": rows,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(read_held_archive(path)).hexdigest()


def _verify_index(
    data_root: Path,
    index_path: Path,
    selected_paths: list[Path],
) -> dict[str, object]:
    lines = read_held_archive(index_path).decode("utf-8").splitlines()
    if not lines:
        raise ValueError("mirror index is empty")
    header = json.loads(lines[0])
    rows = [json.loads(line) for line in lines[1:] if line.strip()]
    if header.get("schema") != INDEX_SCHEMA:
        raise ValueError(f"unsupported mirror index schema: {header.get('schema')!r}")
    by_path: dict[str, dict[str, object]] = {}
    for row in rows:
        key = str(row["sourcePath"]).replace("\\", "/").casefold()
        if key in by_path:
            raise ValueError(f"mirror index repeats a source path: {row['sourcePath']}")
        by_path[key] = row
    for path in selected_paths:
        relative = path.relative_to(data_root).as_posix()
        row = by_path.get(relative.casefold())
        if row is None:
            raise ValueError(f"input is absent from mirror index: {relative}")
        actual = _sha256(path)
        if actual != row.get("sourceSha256"):
            raise ValueError(f"input hash disagrees with mirror index: {relative}")
    return {
        "schema": INDEX_SCHEMA,
        "indexSha256": _sha256(index_path),
        "verifiedFiles": len(selected_paths),
    }


def build_census(data_root: Path, mirror_index: Path | None = None) -> dict[str, object]:
    data_root = Path(os.path.abspath(data_root))
    mesh_root = data_root / "resources" / "meshes"
    resource_root = data_root / "resources"
    script_root = data_root / "MissionScripts"
    if not mesh_root.is_dir() or not resource_root.is_dir() or not script_root.is_dir():
        raise ValueError("data root does not contain resources/meshes, resources, and MissionScripts")

    mesh_paths = sorted(mesh_root.glob("*.msh.aya"), key=lambda item: item.name.casefold())
    parsed = [_mesh_record(path) for path in mesh_paths]
    mesh_records = [record for record, _mesh in parsed]
    membership = _level_mesh_membership(resource_root, parsed)
    scripts = sorted(script_root.rglob("*.msl"), key=lambda item: item.as_posix().casefold())
    numeric_archives = sorted(
        (
            path
            for path in resource_root.glob("*_res_PC.aya")
            if path.name.split("_", 1)[0].isdigit()
        ),
        key=lambda item: item.name.casefold(),
    )
    verification = (
        _verify_index(data_root, mirror_index, [*mesh_paths, *numeric_archives, *scripts])
        if mirror_index is not None
        else None
    )
    a_frames = collections.Counter(
        str(part.anim_frames) for _record, mesh in parsed for part in mesh.file_parts()
    )
    summary = {
        "meshes": len(mesh_records),
        "parts": sum(int(record["partCount"]) for record in mesh_records),
        "meshesWithNontrivialFrameMaps": sum(bool(record["movingParts"]) for record in mesh_records),
        "partsWithNontrivialFrameMaps": sum(len(record["movingParts"]) for record in mesh_records),
        "motionClassCounts": dict(collections.Counter(str(record["motionClass"]) for record in mesh_records)),
        "boneMeshes": sum(bool(record["boneCarriers"]) for record in mesh_records),
        "boneCarriers": sum(len(record["boneCarriers"]) for record in mesh_records),
        "hfovMeshes": sum(bool(record["hfov"]) for record in mesh_records),
        "hfovParts": sum(len(record["hfov"]) for record in mesh_records),
        "aFrameValueCounts": dict(sorted(a_frames.items())),
    }
    return {
        "schema": SCHEMA,
        "inputVerification": verification,
        "meshSummary": summary,
        "meshes": mesh_records,
        "levelMeshMembership": membership,
        "missionAnimationCalls": _animation_calls(script_root),
    }


def _output_is_ignored(path: Path) -> bool:
    candidate = os.path.normcase(os.path.abspath(path))
    for root in (ROOT / "local-lab", ROOT / ".artifacts"):
        allowed = os.path.normcase(os.path.abspath(root))
        try:
            if os.path.commonpath((candidate, allowed)) == allowed:
                return True
        except ValueError:
            continue
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--mirror-index", type=Path)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args(argv)
    output = Path(os.path.abspath(args.json_out))
    if not _output_is_ignored(output):
        parser.error("--json-out must be under a local-lab or .artifacts directory")
    data_root = Path(os.path.abspath(args.data_root))
    mirror_index = Path(os.path.abspath(args.mirror_index)) if args.mirror_index else None
    protected = [data_root] + ([mirror_index] if mirror_index is not None else [])
    try:
        report = build_census(data_root, mirror_index)
        payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
        with SecuredOutputRoot(output.parent, protected_sources=protected) as secured:
            with secured.atomic_text_writer(output) as writer:
                writer.write(payload)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"animation census failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report["meshSummary"], sort_keys=True))
    membership = report["levelMeshMembership"]
    print(
        "LVLR membership: "
        f"{membership['resolvedOccurrences']}/{membership['meshChunks']} named MESH rows "
        f"joined to {membership['uniqueResolvedLooseMeshes']} loose meshes"
    )
    calls = report["missionAnimationCalls"]
    print(f"MSL animation calls: {calls['sites']} sites in {calls['files']} files")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
