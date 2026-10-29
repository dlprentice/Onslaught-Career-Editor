#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Selected PC level archive and loose-mesh texture-name candidates.

Read one explicitly selected PC AYA level archive and up to 16 explicitly
selected loose mesh AYAs. Report its top-level MESH names, top-level TEXT
descriptors, and each selected root CMSH texture slot's same-archive TEXT
candidates. A selected mesh's matching filename is a candidate association,
not proof of source ownership or that the file was used. This is a bounded
metadata-only view, not a runtime dependency
list: optional meshes, shared/base archives, script spawns, embedded meshes,
non-TEXT texture records, missing loose inputs, and runtime selection remain
unknown. A filename-derived level number is only a hint; WDAT is separate.
The selected mesh's internal name is reported only when its 300-byte field is
NUL-terminated and contains printable ASCII; other or empty names are null.

Selected files require Linux O_PATH, descriptor-relative no-follow opens and
/proc/self/fd. Parent traversal, symlink components, multiple hard links and
duplicate selected files are refused. The input metadata is rechecked before
return or emission, but this is not an atomic filesystem snapshot or a lock.
The CLI emits the private retail-derived report only to stdout and never opens
a report file. A shell opens a redirection before this tool runs; the caller
is responsible for the destination, overwrite safety and privacy. Do not
publish generated reports or add them to Git.

Example:
  python tools/level_asset_xref.py --archive /path/to/100_res_PC.aya \
      --mesh /path/to/m_example.msh.aya --stdout
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rebuild" / "tools"))

import aya_archive_inventory as archive  # noqa: E402
import aya_cross_platform_compare as names  # noqa: E402
import content_catalog as catalog  # noqa: E402
import model_transform_catalog as selected  # noqa: E402
import world_resources_encode as worlds  # noqa: E402
from cmsh_static_preview import parse_cmsh_stream  # noqa: E402

SCHEMA = "onslaught.level-asset-xref.v1"
MAX_MESH_INPUTS = 16
MAX_COMPRESSED_TOTAL = 96 * 1024 * 1024
MAX_MESH_INFLATED_TOTAL = 128 * 1024 * 1024
MAX_ARCHIVE_ASSET_ROWS = 4096
MAX_CANDIDATE_LINKS = 20000
MAX_NESTED_CHUNKS = 4096


def ascii_key(value: str) -> str | None:
    """Only claim ASCII case-insensitive equality; retain all other names as unknown."""
    if not value or any(not 32 <= ord(character) <= 126 for character in value):
        return None
    return value.lower()


def expected_mesh_filename(name: str) -> str | None:
    # The source uses sprintf("data\\resources\\meshes\\m_%s.aya", name).
    # Do not interpret a serialized path as a locally selected file basename.
    if ascii_key(name) is None or "/" in name or "\\" in name or name in (".", ".."):
        return None
    return "m_" + name + ".aya"


def texture_key(name: str, requested: int) -> tuple[str, int] | None:
    key = ascii_key(name)
    return None if key is None else (key, requested)


def slot_format(name: str) -> int | None:
    # CMesh::FindTexture uses the suffix beginning at byte 8 and rejects an empty suffix. Short or non-ASCII names
    # cannot be safely classified here. The rule itself is shared with the content catalogue so the two cannot drift.
    if ascii_key(name) is None:
        return None
    return selected.requested_texture_format(name, "utf8-decoded")


def world_header(raw: bytes, chunks: list[Any]) -> dict[str, Any]:
    """Read WDAT only when WRES/WRLD/WDAT are each structurally unambiguous."""
    def children(start: int, end: int, wanted: str) -> list[tuple[str, int, int]]:
        found = []
        for ordinal, row in enumerate(worlds.chunks(raw, start, end)):
            if ordinal >= MAX_NESTED_CHUNKS:
                raise ValueError("nested chunk count exceeds limit")
            if row[0] == wanted:
                found.append(row)
        return found

    wres = [row for row in chunks if row.tag == "WRES"]
    if len(wres) != 1:
        return {"status": "absent" if not wres else "ambiguous", "baseLevel": None, "realLevel": None}
    try:
        entry = wres[0]
        start = entry.offset + 8
        wrld = children(start, start + entry.size, "WRLD")
        if len(wrld) != 1:
            return {"status": "absent" if not wrld else "ambiguous", "baseLevel": None, "realLevel": None}
        _tag, offset, length = wrld[0]
        wdat = children(offset, offset + length, "WDAT")
        if len(wdat) != 1:
            return {"status": "absent" if not wdat else "ambiguous", "baseLevel": None, "realLevel": None}
        _tag, offset, length = wdat[0]
        if length < 8:
            return {"status": "unparsed", "baseLevel": None, "realLevel": None}
        base, real = struct.unpack_from("<ii", raw, offset)
        return {"status": "parsed", "baseLevel": base, "realLevel": real, "payloadOffset": offset}
    except (ValueError, struct.error):
        return {"status": "unparsed", "baseLevel": None, "realLevel": None}


def archive_rows(raw: bytes, chunks: list[Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mesh_rows, text_rows = [], []
    for chunk in chunks:
        if chunk.tag not in ("MESH", "TEXT"):
            continue
        if len(mesh_rows) + len(text_rows) >= MAX_ARCHIVE_ASSET_ROWS:
            raise ValueError("selected archive exceeds the MESH/TEXT occurrence limit")
        payload = raw[chunk.offset + 8:chunk.offset + 8 + chunk.size]
        row: dict[str, Any] = {"chunk": chunk.index, "payloadOffset": chunk.offset + 8,
                               "payloadLength": chunk.size, "payloadSha256": hashlib.sha256(payload).hexdigest()}
        if chunk.tag == "MESH":
            try:
                _normalized, display, method = names.logical_key("MESH", payload)
                comparable = ascii_key(display) is not None if display else False
                status = ("named" if comparable else "named-uncomparable") if display else "embedded-not-inspected"
                row.update(status=status, name=display if comparable else None, nameField=method)
            except ValueError:
                row.update(status="unparsed", name=None, nameField=None)
            row["expectedSelectedFilename"] = expected_mesh_filename(row["name"]) if row["name"] else None
            row["selectedFilenameCandidates"] = [] if row["expectedSelectedFilename"] is not None else None
            row["filenameCandidateStatus"] = ("evaluated-filename-only" if row["expectedSelectedFilename"] is not None
                                               else "unknown-not-comparable")
            mesh_rows.append(row)
        else:
            try:
                record = catalog.parse_text_record(payload)
                comparable = ascii_key(record["name"]) is not None
                row.update(status="parsed" if comparable else "parsed-name-uncomparable",
                           name=record["name"] if comparable else None,
                           requestedFormat=record["requestedFormat"], levels=record["levels"])
            except (ValueError, struct.error):
                row.update(status="unparsed", name=None, requestedFormat=None, levels=None)
            text_rows.append(row)
    return mesh_rows, text_rows


def mesh_row(source: bytes, path: Path, ordinal: int) -> tuple[dict[str, Any], int]:
    comparable_filename = ascii_key(path.name) is not None
    row: dict[str, Any] = {"ordinal": ordinal, "filename": path.name if comparable_filename else None,
                           "archiveSha256": hashlib.sha256(source).hexdigest(),
                           "status": "unparsed", "internalName": None, "textures": None,
                           "archiveMeshFilenameCandidates": [] if comparable_filename else None,
                           "archiveMeshFilenameCandidateStatus": ("not-yet-evaluated" if comparable_filename
                                                                  else "unknown-selected-filename")}
    try:
        stream = archive.inflate_aya_bytes(source)
    except (ValueError, struct.error):
        return row, 0
    try:
        mesh = parse_cmsh_stream(stream)
        textures = []
        for slot, texture in enumerate(mesh.textures):
            raw_name = texture.raw_name_field
            if b"\0" not in raw_name:
                name = None
                status = "unterminated"
            elif raw_name[0] == 0:
                name = ""                # known to be empty: not an unreadable or unsupported name
                status = "empty"
            else:
                prefix = raw_name.split(b"\0", 1)[0]
                try:
                    name = prefix.decode("ascii")
                except UnicodeDecodeError:
                    name = None
                status = "readable" if name is not None and ascii_key(name) is not None else "unsupported-name"
                if status != "readable":
                    name = None
            textures.append({"slot": slot, "name": name, "nameStatus": status,
                             "requestedFormat": slot_format(name) if name is not None else None,
                             "sameArchiveTextCandidates": None,
                             "candidateStatus": "empty-name-not-evaluated" if status == "empty" else "unknown"})
        start = selected.MESH_NAME_OFFSET
        name, _, _ = selected.stored_name(mesh.raw_header[start:start + selected.MESH_NAME_BYTES])
        row.update(status="parsed", internalName=name if name is not None and ascii_key(name) is not None else None,
                   inflatedSha256=hashlib.sha256(stream).hexdigest(), textures=textures)
        return row, len(stream)
    except (ValueError, struct.error):
        return row, len(stream)


def _report_for(archive_path: Path, mesh_paths: list[Path]) -> tuple[dict[str, Any], list[tuple[Path, tuple[int, ...]]]]:
    if len(mesh_paths) > MAX_MESH_INPUTS:
        raise ValueError(f"select at most {MAX_MESH_INPUTS} loose mesh files")
    paths = [selected._selected_path(path) for path in (archive_path, *mesh_paths)]
    if len({str(path) for path in paths}) != len(paths):
        raise ValueError("the same input path was selected more than once")
    inputs: list[tuple[bytes, tuple[int, ...]]] = []
    total = 0
    seen_inodes: set[tuple[int, int]] = set()
    for path in paths:
        source, stamp = selected._read_selected_mesh(path)
        if stamp[:2] in seen_inodes:
            raise ValueError("the same input inode was selected more than once")
        seen_inodes.add(stamp[:2])
        total += len(source)
        if total > MAX_COMPRESSED_TOTAL:
            raise ValueError("selected inputs exceed the aggregate compressed-byte limit")
        inputs.append((source, stamp))
    bindings = [(path, stamp) for path, (_source, stamp) in zip(paths, inputs)]
    source = inputs[0][0]
    raw, chunks, members, _envelope = archive.decode_archive_envelope(source, "pc-chunked-zlib")
    mesh_rows, text_rows = archive_rows(raw, chunks)
    unknown_mesh_name_count = sum(row["expectedSelectedFilename"] is None for row in mesh_rows)
    parsed_text = [row for row in text_rows if row["status"] == "parsed"]
    unparsed_text_count = sum(row["status"] == "unparsed" for row in text_rows)
    uncomparable_text_count = sum(row["status"] == "parsed-name-uncomparable" for row in text_rows)
    unknown_text_count = unparsed_text_count + uncomparable_text_count
    text_index: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in parsed_text:
        key = texture_key(row["name"], row["requestedFormat"])
        if key is not None and row["levels"] == -1:
            text_index[key].append(row)
    filename_index: dict[str, list[int]] = defaultdict(list)
    selected_meshes = []
    total_inflated = 0
    for ordinal, (path, (mesh_source, _stamp)) in enumerate(zip(paths[1:], inputs[1:])):
        row, inflated = mesh_row(mesh_source, path, ordinal)
        total_inflated += inflated
        if total_inflated > MAX_MESH_INFLATED_TOTAL:
            raise ValueError("selected meshes exceed the aggregate inflated-byte limit")
        filename_key = ascii_key(path.name)
        if filename_key is not None:
            filename_index[filename_key].append(ordinal)
        selected_meshes.append(row)
    for row in mesh_rows:
        expected = row["expectedSelectedFilename"]
        if expected is not None:
            row["selectedFilenameCandidates"] = filename_index.get(ascii_key(expected), [])
            for ordinal in row["selectedFilenameCandidates"]:
                selected_meshes[ordinal]["archiveMeshFilenameCandidates"].append(row["chunk"])
    for mesh in selected_meshes:
        if mesh["archiveMeshFilenameCandidates"] is not None:
            mesh["archiveMeshFilenameCandidateStatus"] = (
                "partial-uncomparable-archive-meshes" if unknown_mesh_name_count else
                "evaluated-comparable-named-meshes")
    total_links = 0
    for mesh in selected_meshes:
        for slot in mesh["textures"] or []:
            requested = slot["requestedFormat"]
            key = texture_key(slot["name"], requested) if requested is not None else None
            if key is None:
                continue
            matches = text_index.get(key, [])
            total_links += len(matches)
            if total_links > MAX_CANDIDATE_LINKS:
                raise ValueError("selected inputs exceed the texture-candidate link limit")
            slot["sameArchiveTextCandidates"] = [row["chunk"] for row in matches]
            if matches:
                slot["candidateStatus"] = ("known-candidates-partial-text-coverage" if unknown_text_count else
                                           "known-candidates-top-level-text-only")
            else:
                slot["candidateStatus"] = ("no-known-candidate-partial-text-coverage" if unknown_text_count else
                                           "no-candidate-known-top-level-text-only")
    filename_match = re.fullmatch(r"([0-9]{3})_res_pc\.aya", paths[0].name, re.IGNORECASE | re.ASCII)
    report = {
        "schema": SCHEMA,
        "generatedRetailDerived": True,
        "archive": {"filename": paths[0].name, "archiveSha256": hashlib.sha256(source).hexdigest(),
                    "inflatedSha256": hashlib.sha256(raw).hexdigest(), "zlibMembers": members,
                    "filenameLevelHint": int(filename_match.group(1)) if filename_match else None,
                    "worldHeader": world_header(raw, chunks)},
        "archiveMeshOccurrences": mesh_rows,
        "archiveTopLevelTextOccurrences": text_rows,
        "selectedMeshes": selected_meshes,
        "coverage": {"unparsedTopLevelTextOccurrences": unparsed_text_count,
                     "uncomparableTopLevelTextOccurrences": uncomparable_text_count,
                     "unparsedMeshOccurrences": sum(row["status"] == "unparsed" for row in mesh_rows),
                     "uncomparableMeshFilenameOccurrences": unknown_mesh_name_count,
                     "scope": "one selected archive, top-level MESH and TEXT, selected root CMSH inputs only",
                     "limits": "Filename associations are candidates only, not verified source paths or runtime use. "
                               "No runtime selection, complete dependencies, shared/base archives, optional-mesh "
                               "conditions, script spawns, non-TEXT records, embedded meshes or loose-file absence asserted."},
        "evidence": ["onslaught-decomp src/ResourceAccumulator.cpp CResourceAccumulator::ReadResources @0x004d7200",
                     "onslaught-decomp src/mesh.cpp CMesh::Deserialize @0x004aab90",
                     "onslaught-decomp src/mesh.cpp CMesh::FindTexture @0x004aa410",
                     "onslaught-decomp src/texture.cpp CDXTexture::FindTexture @0x004f27f0",
                     "onslaught-decomp src/world.cpp CWorld::DeserializeWorld @0x0050b780"],
    }
    return report, bindings


def report_for(archive_path: Path, mesh_paths: list[Path]) -> dict[str, Any]:
    """Return a private metadata report for held Linux selected-file reads."""
    report, bindings = _report_for(archive_path, mesh_paths)
    selected._check_input_bindings(bindings)
    return report


def report_bytes(archive_path: Path, mesh_paths: list[Path]) -> bytes:
    """Return deterministic UTF-8 JSON; caller controls any persistence or disclosure."""
    report, bindings = _report_for(archive_path, mesh_paths)
    payload = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    selected._check_input_bindings(bindings)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True, help="one selected PC level archive AYA")
    parser.add_argument("--mesh", type=Path, action="append", default=[], help="selected loose mesh AYA; repeatable")
    parser.add_argument("--stdout", action="store_true", required=True,
                        help="emit private metadata to stdout; caller controls any redirection")
    args = parser.parse_args(argv)
    try:
        sys.stdout.write(report_bytes(args.archive, args.mesh).decode("utf-8"))
    except (ValueError, OSError, RuntimeError) as error:
        print(f"level asset cross-reference failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
