#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Read-only CMSH/LVLR/WRES/physics instance and MSL-use census.

The report contains names, counts, hashes, and relative source coordinates; it
never emits retail payload bytes. Generated reports must stay under an ignored
``local-lab`` or ``.artifacts`` directory.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import struct
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rebuild" / "tools"))

from cmsh_static_preview import CmshProfileError, inflate_aya, parse_cmsh_stream  # noqa: E402
from aya_archive_inventory import (  # noqa: E402
    inflate_aya_bytes,
    parse_top_level_chunks,
    parse_top_level_chunks_bounded,
    read_held_archive,
)
from aya_cross_platform_compare import logical_key  # noqa: E402
from safe_generated_output import SecuredOutputRoot  # noqa: E402

SCHEMA = "onslaught.cmsh-animation-usage-census.v3"
MODEL_METADATA_SCHEMA = "onslaught.cmsh-model-metadata.v1"
MAX_LOD_DEPTH = 32
INDEX_SCHEMA = "onslaught.asset-mirror-index.v1"
PMS2_HEADER_BYTES = 309
PHYSICS_MESH_FIELDS = {
    1: (9, 8),   # Unit record -> CUnitMesh -> WRES unit/init record.
    8: (2, 35),  # Feature record -> CFeatureMesh -> WRES feature record.
}
# Type-12 serialized Unit-behaviour leaf -> value returned by leaf vtable slot
# 1 and stored at Unit definition +0xE0 by CUnitBehaviour__ApplyToUnitData.
UNIT_BEHAVIOR_SELECTOR_BY_SERIALIZED_TYPE = (
    0, 11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13,
    14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
)
UNIT_MEMBER_SHELL_BY_SELECTOR = (
    "CMech",
    "CPlane",
    "CGroundVehicle",
    "CInfantryUnit",
    "CCannon",
    "CBoat",
    "CCarrier",
    "CBuilding",
    "CPlane",
    "CBomber",
    "CGroundAttackAircraft",
    None,
    "CDropship",
    "CMine",
    "CHiveBoss",
    "CSubmarine",
    "CDiveBomber",
    "CThunderHead",
    "CCarver",
    "CGillM",
    "CSentinel",
    "CWarspite",
    "CFenrir",
    "CWarspiteDome",
    "CPod",
    "CSimpleBuilding",
)
EMBEDDED_CONTAINERS = {b"MESH", b"PMSH", b"IMPS", b"SURF", b"LNDS", b"OBJS", b"BLDS"}
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


def _words(data: bytes) -> list[int]:
    """Raw little-endian words, including non-finite floats and author data."""
    if len(data) % 4:
        raise ValueError("metadata word lane is not a multiple of four bytes")
    return list(struct.unpack(f"<{len(data) // 4}I", data))


def _identity(
    stream: bytes | None, *, source_path: str, archive_sha256: str,
    source_universe_id: str | None, platform: str | None,
    payload_offset: int, chunk_path: tuple[int, ...],
) -> dict[str, object]:
    logical = PurePosixPath(source_path)
    if (not source_path or "\0" in source_path or logical.is_absolute() or "\\" in source_path
            or any(part in ("", ".", "..") for part in source_path.split("/"))
            or re.match(r"^[A-Za-z]:", source_path)):
        raise ValueError("source_path must be a normalized relative logical path")
    if not re.fullmatch(r"[0-9a-f]{64}", archive_sha256):
        raise ValueError("archive_sha256 must be a lowercase SHA-256 digest")
    if (type(payload_offset) is not int or payload_offset < 0
            or any(type(index) is not int or index < 0 for index in chunk_path)):
        raise ValueError("source offsets and chunk indices must be nonnegative integers")
    for label, value in (("source_universe_id", source_universe_id), ("platform", platform)):
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError(f"{label} must be a nonempty string or None")
    coordinate = {
        "sourcePath": logical.as_posix(), "archiveSha256": archive_sha256,
        "sourceUniverseId": source_universe_id, "platform": platform,
        "coordinateSpace": "inflated-archive", "payloadOffset": payload_offset,
        "chunkPath": list(chunk_path),
        "payloadSha256": hashlib.sha256(stream).hexdigest() if stream is not None else None,
        "payloadBytes": len(stream) if stream is not None else None,
    }
    transcript = json.dumps(coordinate, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return {
        **coordinate,
        "occurrenceId": "mesh-occurrence:" + hashlib.sha256(
            b"onslaught.cmsh-source-occurrence.v1\0" + transcript.encode("utf-8")
        ).hexdigest(),
        "contentId": "sha256:" + coordinate["payloadSha256"] if stream is not None else None,
        "scopeLabelsPresent": source_universe_id is not None and platform is not None,
        "scopeProvenance": "caller-supplied labels; not independently verified",
    }


def _unparsed(identity: dict[str, object], error: Exception) -> dict[str, object]:
    # Do not serialize arbitrary exception text: it can contain a host path.
    reason = {"category": "unparsed source", "falsifier": "supply a supported bounded CMSH stream"}
    if isinstance(error, CmshProfileError):
        reason.update(category=error.category, offset=error.offset, space=error.space, role=error.role)
    return {
        "schema": MODEL_METADATA_SCHEMA, "status": "unparsed", "identity": identity,
        "reason": reason, "parts": [], "animations": {"status": "unknown", "rows": []},
        "emitters": {"status": "unknown", "rows": []}, "lodChildren": [],
        "description": {"status": "unknown", "text": None},
    }


def _sibling_metadata(mesh: Any, tag: bytes, decode: Any) -> dict[str, object]:
    matches = [item.raw_payload for item in mesh.siblings if item.tag == tag]
    if not matches:
        return {"status": "absent", "rows": []}
    payload = matches[0]
    envelope = {"payloadSha256": hashlib.sha256(payload).hexdigest(), "payloadBytes": len(payload)}
    try:
        if len(matches) != 1:
            raise ValueError("duplicate sibling")
        return {**envelope, "status": "decoded", "rows": decode(payload)}
    except (ValueError, struct.error):
        return {**envelope, "status": "unparsed", "rows": [],
                "reason": "invalid or unsupported framed " + tag.decode("ascii") + " metadata",
                "falsifier": "check declared counts, bounded record lengths and source reader"}


def _animation_metadata(mesh: Any) -> dict[str, object]:
    def decode(payload: bytes) -> list[dict[str, object]]:
        count = struct.unpack_from("<I", mesh.raw_header, 0x14)[0]
        if len(payload) != count * 36:
            raise ValueError("CAMD declared count/length mismatch")
        rows = []
        for ordinal in range(count):
            record = payload[ordinal * 36:(ordinal + 1) * 36]
            name = record[:16].split(b"\0", 1)[0].decode("ascii")
            mode, start, last, scaler = struct.unpack_from("<4i", record, 16)
            rows.append({"ordinal": ordinal, "name": name, "mode": mode,
                         "start": start, "last": last, "frameScaler": scaler,
                         "rateBits": struct.unpack_from("<I", record, 32)[0],
                         "rateSemantics": "normalized-mode-increment-per-game-tick",
                         "recordSha256": hashlib.sha256(record).hexdigest()})
        names = collections.Counter(row["name"].casefold() for row in rows)
        modes = collections.Counter(row["mode"] for row in rows)
        for row in rows:
            row["localNameMultiplicity"] = names[row["name"].casefold()]
            row["localModeMultiplicity"] = modes[row["mode"]]
        return rows
    result = _sibling_metadata(mesh, b"CAMD", decode)
    if result["status"] == "absent" and struct.unpack_from("<I", mesh.raw_header, 0x14)[0]:
        result.update(status="unparsed", reason="declared CAMD records are absent",
                      falsifier="supply the declared bounded CAMD records")
    result["evidence"] = "onslaught-decomp:CMesh::Deserialize@004aab90; CMesh::GetFrameIncrement@004aa7e0"
    result["runtimeScheduling"] = "unknown; stored modes do not prove a call or playback"
    return result


def _emitter_metadata(mesh: Any) -> dict[str, object]:
    def decode(payload: bytes) -> list[dict[str, object]]:
        # The parser owns framing, record size, ASCII and part-index checks.
        bindings = mesh.emitter_bindings()
        if len(bindings) != struct.unpack_from("<I", mesh.raw_header, 0x1c)[0]:
            raise ValueError("CEMT declared count mismatch")
        multiplicity = collections.Counter((b.name.casefold(), b.selector) for b in bindings)
        rows = []
        offset = 4
        for ordinal, binding in enumerate(bindings):
            record = payload[offset:offset + 336]
            offset += 336 + (4 if binding.part_ordinal is not None else 0)
            tracking, subpart = struct.unpack_from("<2i", record, 0x44)
            rows.append({
                "ordinal": ordinal, "name": binding.name, "number": binding.selector,
                "partOrdinal": binding.part_ordinal, "trackingVertex": tracking,
                "subpartEmitter": subpart, "positionWords": _words(record[:16]),
                "orientationWords": _words(record[16:64]),
                "recordSha256": hashlib.sha256(record).hexdigest(),
                "localNameNumberMultiplicity": multiplicity[(binding.name.casefold(), binding.selector)],
                "lookup": "case-insensitive-name-and-number; ordinal-is-a-separate-lookup",
                "lookupScope": "this LOD; an earlier LOD can shadow later matches",
                "poseDependencies": (["part hierarchy", "selected animation/render frame", "thing transform"]
                                     if binding.part_ordinal is not None else ["no bound part; consumer-specific fallback"]),
                "usageContext": "unknown; cockpit, exterior weapon, particle and other uses must be joined separately",
                "worldMuzzle": "not established by this stored record",
            })
        return rows
    result = _sibling_metadata(mesh, b"CEMT", decode)
    if result["status"] == "absent" and struct.unpack_from("<I", mesh.raw_header, 0x1c)[0]:
        result.update(status="unparsed", reason="declared CEMT records are absent",
                      falsifier="supply the declared bounded CEMT records")
    result["evidence"] = "onslaught-decomp:CMesh::GetEmitterSubpart@004aa820; CRTMesh::GetRTEmitter@004dd160"
    return result


def _part_metadata(part: Any, ordinal: int, payload: bytes) -> dict[str, object]:
    raw = part.raw_cmsp
    groups = []
    for piece, group in enumerate(part.groups):
        surviving = sum(len(set(group.indices[k:k + 3])) == 3 for k in range(len(group.indices) - 2))
        slots = [value if value < 0x80000000 else value - 0x100000000 for value in group.raw_texr_u32]
        groups.append({"pieceOrdinal": piece, "indexCount": len(group.indices),
                       "indexSha256": hashlib.sha256(struct.pack(f"<{len(group.indices)}H", *group.indices)).hexdigest(),
                       "stripPrimitiveCount": max(0, len(group.indices) - 2),
                       "distinctIndexTriangleCount": surviving,
                       "repeatedIndexTriangleCount": max(0, len(group.indices) - 2) - surviving,
                       "textureSlots": slots, "vertexBufferOwnerPiece": 0})
    cmvb = part.raw_cmvb
    stride, fvf, primitive = struct.unpack_from("<3I", cmvb, 276)
    bounds = [c for c in parse_top_level_chunks_bounded(payload) if c.tag == "BBOX"]
    bound_payload = payload[bounds[0].offset + 8:bounds[0].offset + 8 + bounds[0].size]
    # The bounded parser already validated outer BBOX -> BBOX(40).
    bounds_words = _words(bound_payload[8:])
    return {
        "ordinal": ordinal, "name": raw[0xdc:0xfc].split(b"\0", 1)[0].decode("utf-8", errors="replace"),
        "partNumber": struct.unpack_from("<i", raw, 0x88)[0], "partType": part.part_type,
        "recordSha256": hashlib.sha256(raw).hexdigest(),
        "payloadSha256": hashlib.sha256(payload).hexdigest(),
        "relations": {"parentOrdinal": part.parent, "childOrdinals": list(part.children),
                      "referenceGeometryOrdinal": part.reference, "nextDamagePartOrdinal": part.nmic,
                      "damageChainCount": struct.unpack_from("<i", raw, 0xa0)[0],
                      "isDamageChainMember": struct.unpack_from("<i", raw, 0xa4)[0]},
        "orientationWords": _words(raw[:48]), "baseOrientationWords": _words(raw[48:96]),
        "offsetPositionWords": _words(raw[96:112]), "basePositionWords": _words(raw[112:128]),
        "boundingBoxWords": bounds_words,
        "radiusBits": struct.unpack_from("<I", raw, 0x12c)[0],
        "cueFactorBits": struct.unpack_from("<I", raw, 0x130)[0],
        "frameLanes": {"positionSetCount": part.anim_frames,
                       "virtualFrameCount": len(part.track.frame_map),
                       "hierarchyPoseCount": len(part.track.hierarchy),
                       "frameMapSha256": hashlib.sha256(bytes(part.track.frame_map)).hexdigest(),
                       "hfovWords": _words(part.raw_hfov) if part.raw_hfov is not None else None,
                       "cachedPositionBytes": len(part.track.cached_position_bytes),
                       "cachedOrientationBytes": len(part.track.cached_orientation_bytes)},
        "skinning": {"bonePartOrdinals": list(part.bones),
                     "boneSlotUse": dict(sorted(collections.Counter(
                         str(slot) for vertex in part.vertices for slot in (vertex.bone_slots or ())
                     ).items())),
                     "weightSemantics": "not inferred from palette slots"},
        "geometry": {"ownership": "reference" if part.reference is not None else "original",
                     "originalVertexCount": len(part.vertices), "stride": stride, "fvf": fvf,
                     "primitiveCode": primitive,
                     "primitiveMeaning": "triangle-strip" if groups and primitive == 4 else "unused-or-unknown",
                     "pieces": groups, "degeneracyTest": "repeated indices only; not geometric area"},
        "unknowns": ["opaque PBKT semantics", "uninterpreted CMSP/CMVB author fields"],
    }


def _model_metadata(stream: bytes, mesh: Any, identity: dict[str, object], depth: int,
                    source_context: str | None) -> dict[str, object]:
    chunks = parse_top_level_chunks_bounded(stream)
    parts = mesh.file_parts()
    part_chunks = chunks[2 + len(mesh.textures):2 + len(mesh.textures) + len(parts)]
    result = {
        "schema": MODEL_METADATA_SCHEMA, "status": "parsed", "identity": identity,
        "evidenceClass": "static structure and source-derived field meanings; not full semantic or runtime acceptance",
        "sourceContext": source_context,
        "sourceContextProvenance": "caller-supplied; runtime loading and the separate resource reader are not established",
        "lodOrdinal": depth,
        "radiusBits": struct.unpack_from("<I", mesh.raw_header, 0x164)[0],
        "cueFactorBits": struct.unpack_from("<I", mesh.raw_header, 0x168)[0],
        "parts": [_part_metadata(part, ordinal, stream[c.offset + 8:c.offset + 8 + c.size])
                  for ordinal, (part, c) in enumerate(zip(parts, part_chunks))],
        "animations": _animation_metadata(mesh), "emitters": _emitter_metadata(mesh),
        "textures": [{"slotOrdinal": index, "name": texture.name,
                      "declaredFrameCount": struct.unpack_from("<I", texture.raw_cmst_entry, 8)[0],
                      "laneStatus": "decoded-single-frame" if struct.unpack_from("<I", texture.raw_cmst_entry, 8)[0] == 1 else "unknown-frame-layout",
                      "storedLaneWords": _words(texture.raw_texb_metadata),
                      "laneOrder": ["Blend", "OffsetU", "OffsetV", "ScaleU", "ScaleV"],
                      "resolution": "name reference; require unique source-variant join"}
                     for index, texture in enumerate(mesh.textures)],
        "description": {"status": "unknown", "text": None},
        "lodChildren": [], "unknowns": [],
        "evidence": "onslaught-decomp:CMesh::Deserialize@004aab90; CMeshPart::Deserialize@004b27a0; "
                    "CDXMeshVB::Load@0054e160; CRTMesh::Render@004dcba0",
    }
    names = collections.Counter(part["name"].casefold() for part in result["parts"])
    for part in result["parts"]:
        part["occurrenceId"] = identity["occurrenceId"] + "/part:" + str(part["ordinal"])
        part["localNameMultiplicity"] = names[part["name"].casefold()]
        for group in part["geometry"]["pieces"]:
            group["materialBindings"] = [
                {"layerOrdinal": layer, "textureSlotOrdinal": slot,
                 "status": "absent" if slot == -1 else "resolved-slot" if 0 <= slot < len(mesh.textures) else "unresolved-slot"}
                for layer, slot in enumerate(group["textureSlots"])
            ]
    for lane, identifier in (("animations", "animation"), ("emitters", "emitter")):
        for row in result[lane]["rows"]:
            row["occurrenceId"] = identity["occurrenceId"] + "/" + identifier + ":" + str(row["ordinal"])
    siblings = chunks[2 + len(mesh.textures) + len(parts):]
    bbox = [c for c in siblings if c.tag == "BBOX"]
    result["boundingBoxWords"] = None
    if bbox:
        c = bbox[0]
        payload = stream[c.offset + 8:c.offset + 8 + c.size]
        if len(payload) == 48 and payload[:8] == b"BBOX" + struct.pack("<I", 40):
            result["boundingBoxWords"] = _words(payload[8:])
        else:
            result["unknowns"].append("invalid or unsupported mesh bounding box")
    next_marker = struct.unpack_from("<I", mesh.raw_header, 8)[0] != 0
    nested_chunks = [c for c in siblings if c.tag in ("PMS2", "PMSH")]
    for c in nested_chunks:
        payload = stream[c.offset + 8:c.offset + 8 + c.size]
        child_offset = c.offset + 8
        child_path = [*identity["chunkPath"], c.index]
        if c.tag == "PMSH":
            try:
                inner = parse_top_level_chunks_bounded(payload)
            except ValueError:
                inner = []
            if len(inner) != 1 or inner[0].tag != "PMS2":
                child_identity = _identity(payload, source_path=identity["sourcePath"],
                                           archive_sha256=identity["archiveSha256"],
                                           source_universe_id=identity["sourceUniverseId"], platform=identity["platform"],
                                           payload_offset=identity["payloadOffset"] + child_offset,
                                           chunk_path=tuple(child_path))
                result["lodChildren"].append({"relationship": "unresolved-nested-mesh", "framingPrefixBytes": None,
                                              "relationshipReason": "PMSH does not contain exactly one bounded PMS2",
                                              "model": _unparsed(child_identity, CmshProfileError(
                                                  "unsupported profile", 0, "framed PMSH LOD child"))})
                result["unknowns"].append("unsupported framed PMSH LOD child")
                continue
            child_offset += 8
            child_path.append(inner[0].index)
            payload = payload[8:]
        starts = [offset for offset in (0, PMS2_HEADER_BYTES)
                  if payload[offset:offset + 8] == b"CMSH" + struct.pack("<I", 372)]
        # Loose-file and embedded resource readers encounter different nested
        # shapes: the former enters PMS2 then CMSH; the latter enters PMSH,
        # PMS2 and a 309-byte resource header before CMSH. Never pick one of
        # two possible CMSH boundaries, or infer context from the pathname.
        ambiguous = len(starts) != 1
        prefix = starts[0] if not ambiguous else 0
        child_offset += prefix
        child_stream = payload[prefix:]
        child_identity = _identity(child_stream, source_path=identity["sourcePath"],
                                   archive_sha256=identity["archiveSha256"],
                                   source_universe_id=identity["sourceUniverseId"], platform=identity["platform"],
                                   payload_offset=identity["payloadOffset"] + child_offset,
                                   chunk_path=tuple(child_path))
        try:
            if ambiguous:
                raise CmshProfileError("unsupported profile", 0, "missing or ambiguous PMS2 CMSH boundary")
            if depth >= MAX_LOD_DEPTH:
                raise CmshProfileError("limit exceeded", 0, "metadata LOD depth")
            child_mesh = parse_cmsh_stream(child_stream)
            child = _model_metadata(child_stream, child_mesh, child_identity, depth + 1, source_context)
        except (ValueError, struct.error) as error:
            child = _unparsed(child_identity, error)
            child["lodOrdinal"] = depth + 1
        loose_shape = source_context == "loose-mesh" and c.tag == "PMS2" and prefix == 0
        embedded_shape = source_context == "embedded-mesh" and c.tag == "PMSH" and prefix == PMS2_HEADER_BYTES
        declared_chain = (next_marker and not ambiguous and child["status"] != "unparsed"
                          and (loose_shape or embedded_shape))
        # CRTMesh::Render follows at most two links from its root. Deeper
        # serialized links are a chain, but their render selection is unknown.
        relationship = ("mesh-lod" if depth < 2 else "mesh-chain") if declared_chain else "unresolved-nested-mesh"
        if declared_chain:
            reason = None
        elif not next_marker:
            reason = "next-in-chain marker is zero"
        elif ambiguous:
            reason = "no unique CMSH boundary"
        elif child["status"] == "unparsed":
            reason = "nested CMSH did not parse"
        elif source_context is None:
            reason = "reader context is unknown"
        else:
            reason = "reader context does not match nested framing"
        scope = ("serialized next-in-chain; renderer selection beyond two links and runtime loading not established"
                 if relationship == "mesh-chain" else
                 "serialized next-in-chain; runtime loading not established" if declared_chain else
                 "unresolved nested structure; runtime loading not established")
        result["lodChildren"].append({"relationship": relationship, "relationshipScope": scope,
                                      "relationshipReason": reason,
                                      "framingPrefixBytes": None if ambiguous else prefix, "model": child})
    if next_marker != bool(result["lodChildren"]):
        result["unknowns"].append("LOD presence marker and decoded child disagree")
    if (any(result[lane]["status"] == "unparsed" for lane in ("animations", "emitters"))
            or any(child["model"]["status"] != "parsed" for child in result["lodChildren"])
            or any(child["relationship"] not in ("mesh-lod", "mesh-chain") for child in result["lodChildren"])
            or any(texture["laneStatus"] != "decoded-single-frame" for texture in result["textures"])
            or result["unknowns"]):
        result["status"] = "partial"
    return result


def mesh_record_from_stream(
    stream: bytes, *, source_path: str, archive_sha256: str,
    source_universe_id: str | None = None, platform: str | None = None,
    payload_offset: int = 0, chunk_path: tuple[int, ...] = (), source_context: str | None = None,
) -> tuple[dict[str, object], Any | None]:
    """Metadata from held decoded bytes; callers own/pin the source envelope.

    Coordinates are relative to the inflated archive, never a host pathname.
    Scope labels and source_context are caller declarations, not attestation.
    Context is 'loose-mesh' for the separate mesh-data reader, 'embedded-mesh'
    for a shared resource reader, or None when that distinction is unknown.
    Unsupported source rows
    retain exact identity and a refusal instead of disappearing. No gameplay,
    rendering, muzzle position or animation scheduling is established here.
    """
    if not isinstance(stream, bytes):
        raise ValueError("stream must be immutable held bytes")
    if source_context not in (None, "loose-mesh", "embedded-mesh"):
        raise ValueError("unsupported source context")
    identity = _identity(stream, source_path=source_path, archive_sha256=archive_sha256,
                         source_universe_id=source_universe_id, platform=platform,
                         payload_offset=payload_offset, chunk_path=chunk_path)
    try:
        mesh = parse_cmsh_stream(stream)
        record = _parsed_mesh_record(mesh)
    except ValueError as error:
        return ({"file": PurePosixPath(source_path).name, "modelMetadata": _unparsed(identity, error)}, None)
    try:
        metadata = _model_metadata(stream, mesh, identity, 0, source_context)
    except (ValueError, struct.error) as error:
        metadata = _unparsed(identity, error)
    record.update(file=PurePosixPath(source_path).name, modelMetadata=metadata)
    return record, mesh


def _mesh_record(
    path: Path, *, source_root: Path | None = None,
    source_universe_id: str | None = None, platform: str | None = "pc",
    source_context: str | None = None,
) -> tuple[dict[str, object], Any | None]:
    source = read_held_archive(path)
    logical = path.relative_to(source_root).as_posix() if source_root is not None else path.name
    archive_sha = hashlib.sha256(source).hexdigest()
    try:
        stream = inflate_aya(source)
    except CmshProfileError as error:
        identity = _identity(None, source_path=logical, archive_sha256=archive_sha,
                             source_universe_id=source_universe_id, platform=platform,
                             payload_offset=0, chunk_path=())
        return ({"file": path.name, "modelMetadata": _unparsed(identity, error)}, None)
    return mesh_record_from_stream(stream, source_path=logical, archive_sha256=archive_sha,
                                   source_universe_id=source_universe_id, platform=platform,
                                   source_context=source_context)


def _parsed_mesh_record(mesh: Any) -> dict[str, object]:
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
            "values": (list(part.hfov) if part.hfov is not None
                       and all(math.isfinite(value) for value in part.hfov) else None),
            "rawWords": _words(part.raw_hfov),
        }
        for part_index, part in enumerate(parts)
        if part.raw_hfov is not None
    ]
    a_frames = collections.Counter(part.anim_frames for part in parts)
    return {
        "internalName": mesh.name,
        "partCount": len(parts),
        "aFrameValueCounts": {str(value): a_frames[value] for value in sorted(a_frames)},
        "maxVirtualFrames": max(len(part.track.frame_map) for part in parts),
        "maxHierarchyFrames": max(len(part.track.hierarchy) for part in parts),
        "movingParts": moving,
        "motionClass": motion_class,
        "boneCarriers": carriers,
        "hfov": hfov,
    }


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


def _take_c_string(data: bytes, offset: int, role: str) -> tuple[str, int]:
    end = data.find(b"\0", offset)
    if end < 0:
        raise ValueError(f"{role} is not NUL-terminated")
    try:
        value = data[offset:end].decode("ascii")
    except UnicodeDecodeError as error:
        raise ValueError(f"{role} is not ASCII") from error
    return value, end + 1


def _physics_mesh_definitions(data: bytes) -> dict[str, object]:
    """Read the Unit/Feature fields needed for mesh and behaviour joins."""

    if len(data) < 6 or struct.unpack_from("<H", data, 0)[0] != 0x12:
        raise ValueError("unsupported physics-definition framing")
    offset = 2
    record_count = 0
    unit_count = 0
    unit_definitions: list[dict[str, object]] = []
    definitions: dict[str, list[dict[str, object]]] = collections.defaultdict(list)
    while True:
        if offset + 4 > len(data):
            raise ValueError("physics-definition table has no terminal marker")
        if struct.unpack_from("<i", data, offset)[0] == -1:
            offset += 4
            break
        if record_count >= 10_000 or offset + 8 > len(data):
            raise ValueError("physics-definition record limit or header failure")
        record_type, _declared_size = struct.unpack_from("<II", data, offset)
        offset += 8
        name, offset = _take_c_string(data, offset, "physics definition name")
        relevant = PHYSICS_MESH_FIELDS.get(record_type)
        mesh_value: str | None = None
        behavior_serialized_type: int | None = None
        unit_ordinal = unit_count if record_type == 1 else None
        field_count = 0
        while True:
            if field_count >= 1_024 or offset + 8 > len(data):
                raise ValueError(f"physics definition {name!r} has invalid field framing")
            field_id, size = struct.unpack_from("<II", data, offset)
            offset += 8
            end = offset + size
            if size > 1_048_576 or end + 4 > len(data):
                raise ValueError(f"physics definition {name!r} has an overrun field")
            value = data[offset:end]
            offset = end
            marker = struct.unpack_from("<i", data, offset)[0]
            offset += 4
            field_count += 1
            if relevant is not None and field_id == relevant[0]:
                if mesh_value is not None:
                    raise ValueError(f"physics definition {name!r} repeats its mesh field")
                mesh_value, consumed = _take_c_string(value, 0, f"physics mesh for {name!r}")
                if consumed != len(value):
                    raise ValueError(f"physics mesh for {name!r} has trailing bytes")
            if record_type == 1 and field_id == 8:
                if behavior_serialized_type is not None:
                    raise ValueError(
                        f"Unit definition {name!r} repeats behaviour field 8"
                    )
                if len(value) != 4:
                    raise ValueError(
                        f"Unit definition {name!r} behaviour field is not one dword"
                    )
                behavior_serialized_type = struct.unpack("<I", value)[0]
            if marker == -1:
                break
            if marker != 0:
                raise ValueError(f"physics definition {name!r} has invalid continuation")
        unit_metadata: dict[str, object] = {}
        if record_type == 1:
            if behavior_serialized_type is None:
                raise ValueError(f"Unit definition {name!r} has no behaviour field 8")
            if not 1 <= behavior_serialized_type <= len(
                UNIT_BEHAVIOR_SELECTOR_BY_SERIALIZED_TYPE
            ):
                raise ValueError(
                    f"Unit definition {name!r} has unsupported behaviour type "
                    f"{behavior_serialized_type}"
                )
            selector = UNIT_BEHAVIOR_SELECTOR_BY_SERIALIZED_TYPE[
                behavior_serialized_type - 1
            ]
            unit_metadata = {
                "behaviorSerializedType": behavior_serialized_type,
                "factorySelector": selector,
                "memberShell": UNIT_MEMBER_SHELL_BY_SELECTOR[selector],
                "unitDefinitionOrdinal": unit_ordinal,
            }
            unit_definitions.append(
                {
                    "definition": name,
                    "mesh": mesh_value,
                    **unit_metadata,
                }
            )
            unit_count += 1
        if relevant is not None and mesh_value:
            mesh_field_id, wres_thing_type = relevant
            candidate = {
                "mesh": mesh_value,
                "meshFieldId": mesh_field_id,
                "physicsRecordType": record_type,
                "wresThingType": wres_thing_type,
                **unit_metadata,
            }
            if candidate in definitions[name]:
                raise ValueError(f"physics definition {name!r} repeats a mesh candidate")
            definitions[name].append(candidate)
        record_count += 1
    if offset != len(data):
        raise ValueError("physics-definition table has trailing bytes")
    return {
        "recordCount": record_count,
        "unitDefinitions": unit_definitions,
        "definitions": {
            name: sorted(rows, key=lambda row: (int(row["wresThingType"]), int(row["meshFieldId"])))
            for name, rows in sorted(definitions.items(), key=lambda item: item[0].casefold())
        },
    }


def _scan_wres_definition_instances(
    body: bytes,
    definitions: dict[str, list[dict[str, object]]],
    level: str,
    world_kind: str,
) -> dict[str, object]:
    """Find bounded Unit/Feature records by their physics-definition string."""

    instances: list[dict[str, object]] = []
    marker_candidates = 0
    rejected = 0
    for definition, candidates in definitions.items():
        encoded = definition.encode("ascii")
        if len(encoded) > 255:
            raise ValueError(f"physics definition is too long for WRES string8: {definition!r}")
        marker = bytes((len(encoded),)) + encoded
        cursor = 0
        while True:
            definition_offset = body.find(marker, cursor)
            if definition_offset < 0:
                break
            cursor = definition_offset + 1
            marker_candidates += 1
            definition_end = definition_offset + len(marker)
            if definition_offset < 9 or definition_end + 4 > len(body):
                rejected += 1
                continue
            active_offset = definition_offset - 8
            attach_offset = definition_offset - 4
            spawn_end = active_offset - 1
            if body[spawn_end] != 0:
                rejected += 1
                continue
            name_end = body.rfind(b"\0", 0, spawn_end)
            script_end = body.rfind(b"\0", 0, name_end)
            if name_end < 0 or script_end < 0:
                rejected += 1
                continue
            script_start = script_end
            while script_start > 0 and 0x20 <= body[script_start - 1] < 0x7F:
                script_start -= 1
            record_offset = script_start - 40
            if record_offset < 0:
                rejected += 1
                continue
            thing_type = struct.unpack_from("<i", body, record_offset)[0]
            owned_candidates = [
                row for row in candidates if int(row["wresThingType"]) == thing_type
            ]
            if len(owned_candidates) != 1:
                rejected += 1
                continue
            position = list(struct.unpack_from("<3f", body, record_offset + 4))
            orientation = list(struct.unpack_from("<3f", body, record_offset + 16))
            mesh_number, allegiance, target = struct.unpack_from(
                "<3i", body, record_offset + 28
            )
            active = struct.unpack_from("<i", body, active_offset)[0]
            attach_scripts = struct.unpack_from("<i", body, attach_offset)[0]
            trailer = struct.unpack_from("<i", body, definition_end)[0]
            try:
                script = body[script_start:script_end].decode("ascii")
                name = body[script_end + 1:name_end].decode("ascii")
                spawn_script = body[name_end + 1:spawn_end].decode("ascii")
            except UnicodeDecodeError:
                rejected += 1
                continue
            if (
                not all(math.isfinite(value) for value in (*position, *orientation))
                or active not in (0, 1)
                or attach_scripts not in (0, 1)
                or trailer != -1
            ):
                rejected += 1
                continue
            instances.append(
                {
                    "active": bool(active),
                    "allegiance": allegiance,
                    "attachScripts": bool(attach_scripts),
                    "definition": definition,
                    "level": level,
                    "meshNumber": mesh_number,
                    "name": name,
                    "orientation": orientation,
                    "physicsMeshCandidates": owned_candidates,
                    "position": position,
                    "recordOffset": record_offset,
                    "script": script,
                    "spawnScript": spawn_script,
                    "target": target,
                    "thingType": thing_type,
                    "worldKind": world_kind,
                }
            )
    instances.sort(key=lambda row: int(row["recordOffset"]))
    starts = [int(row["recordOffset"]) for row in instances]
    if len(starts) != len(set(starts)):
        raise ValueError(f"level {level} {world_kind} repeats a WRES record offset")
    return {
        "instances": instances,
        "markerCandidates": marker_candidates,
        "rejectedCandidates": rejected,
    }


def _structural_chunks(data: bytes) -> list[tuple[bytes, bytes]] | None:
    rows: list[tuple[bytes, bytes]] = []
    offset = 0
    while offset < len(data):
        if offset + 8 > len(data):
            return None
        tag = data[offset:offset + 4]
        if not all(0x20 <= value < 0x7F for value in tag):
            return None
        size = struct.unpack_from("<I", data, offset + 4)[0]
        end = offset + 8 + size
        if end > len(data):
            return None
        rows.append((tag, data[offset + 8:end]))
        offset = end
    return rows or None


def _direct_embedded_cmsh(payload: bytes) -> bytes:
    found: list[bytes] = []

    def descend(data: bytes, depth: int) -> None:
        if depth > 10:
            raise ValueError("embedded CMSH container depth exceeds ten")
        rows = _structural_chunks(data)
        if rows is None:
            return
        for tag, child in rows:
            if tag == b"PMS2":
                if (
                    len(child) >= PMS2_HEADER_BYTES + 380
                    and child[PMS2_HEADER_BYTES:PMS2_HEADER_BYTES + 4] == b"CMSH"
                    and struct.unpack_from("<I", child, PMS2_HEADER_BYTES + 4)[0] == 372
                ):
                    found.append(child[PMS2_HEADER_BYTES:])
            elif tag in EMBEDDED_CONTAINERS:
                descend(child, depth + 1)

    descend(payload, 0)
    if len(found) != 1:
        raise ValueError(f"expected exactly one direct embedded CMSH, found {len(found)}")
    return found[0]


def _cmsh_core(stream: bytes) -> bytes:
    if (
        len(stream) < 380
        or stream[:4] != b"CMSH"
        or struct.unpack_from("<I", stream, 4)[0] != 372
    ):
        raise ValueError("embedded mesh is not a bounded CMSH stream")
    texture_count = struct.unpack_from("<I", stream, 0x0C)[0]
    part_count = struct.unpack_from("<I", stream, 0x164)[0]
    offset = 380

    def consume(expected: bytes) -> None:
        nonlocal offset
        if offset + 8 > len(stream) or stream[offset:offset + 4] != expected:
            raise ValueError(f"CMSH core expected {expected.decode('ascii')} at {offset}")
        size = struct.unpack_from("<I", stream, offset + 4)[0]
        end = offset + 8 + size
        if end > len(stream):
            raise ValueError("CMSH core child overruns its stream")
        offset = end

    consume(b"CMST")
    for _ in range(texture_count):
        consume(b"MSHT")
    for _ in range(part_count):
        consume(b"MESP")
    return stream[:offset]


def _normalized_cmsh_core_sha256(stream: bytes) -> str:
    core = bytearray(_cmsh_core(stream))
    core[44:344] = b"\0" * 300
    return hashlib.sha256(core).hexdigest()


def _chunk_payload(data: bytes, tag: str, role: str) -> bytes:
    matches = []
    for chunk in parse_top_level_chunks(data):
        if chunk.tag == tag:
            matches.append(data[chunk.offset + 8:chunk.offset + 8 + chunk.size])
    if len(matches) != 1:
        raise ValueError(f"{role} expected one {tag} chunk, found {len(matches)}")
    return matches[0]


def _normalized_mesh_identity(value: str) -> str:
    name = _normalized_basename(value)
    return name if name.endswith(".msh") else name + ".msh"


def _loose_mesh_key(value: str) -> str:
    return ("m_" + _normalized_mesh_identity(value) + ".aya").casefold()


def _world_instance_join(
    data_root: Path,
    meshes: list[tuple[dict[str, object], Any]],
    membership: dict[str, object],
    animation_calls: dict[str, object],
) -> dict[str, object]:
    physics_path = data_root / "default physics.dat"
    physics = _physics_mesh_definitions(read_held_archive(physics_path))
    definitions = physics["definitions"]
    loose_lookup: dict[str, str] = {}
    mesh_metadata: dict[str, dict[str, object]] = {}
    loose_core_lookup: dict[str, list[str]] = collections.defaultdict(list)
    mesh_root = data_root / "resources" / "meshes"
    for record, _mesh in meshes:
        file_name = str(record["file"])
        key = file_name.casefold()
        if key in loose_lookup:
            raise ValueError(f"duplicate loose mesh filename: {file_name}")
        loose_lookup[key] = file_name
        mesh_metadata[file_name] = {
            "boneCarriers": len(record["boneCarriers"]),
            "motionClass": record["motionClass"],
            "movingParts": len(record["movingParts"]),
        }
        loose_stream = inflate_aya_bytes(read_held_archive(mesh_root / file_name))
        loose_core_lookup[_normalized_cmsh_core_sha256(loose_stream)].append(file_name)

    membership_lookup: dict[tuple[str, str], list[dict[str, object]]] = collections.defaultdict(list)
    for row in membership["rows"]:
        display_name = str(row["displayName"])
        if display_name:
            membership_lookup[(str(row["level"]), _normalized_mesh_identity(display_name))].append(row)

    script_files: dict[str, str] = {}
    script_root = data_root / "MissionScripts"
    for path in sorted(script_root.rglob("*.msl"), key=lambda item: item.as_posix().casefold()):
        coordinate = path.relative_to(data_root).as_posix()
        key = coordinate.casefold()
        if key in script_files:
            raise ValueError(f"duplicate MSL coordinate: {coordinate}")
        script_files[key] = coordinate
    call_counts: collections.Counter[str] = collections.Counter(
        str(row["script"]).casefold() for row in animation_calls["rows"]
    )

    instances: list[dict[str, object]] = []
    unresolved: list[dict[str, object]] = []
    anonymous_rows: list[dict[str, object]] = []
    marker_candidates = 0
    rejected_candidates = 0
    resource_root = data_root / "resources"
    archives = sorted(
        (
            path
            for path in resource_root.glob("*_res_PC.aya")
            if path.name.split("_", 1)[0].isdigit()
        ),
        key=lambda item: item.name.casefold(),
    )
    for path in archives:
        level = path.name.split("_", 1)[0]
        raw = inflate_aya_bytes(read_held_archive(path))
        wres = _chunk_payload(raw, "WRES", f"level {level}")
        wrld = _chunk_payload(wres, "WRLD", f"level {level} WRES")
        for world_chunk in parse_top_level_chunks(wrld):
            if world_chunk.tag not in ("BSWD", "RLWD"):
                continue
            body = wrld[
                world_chunk.offset + 8:world_chunk.offset + 8 + world_chunk.size
            ]
            scanned = _scan_wres_definition_instances(
                body,
                definitions,
                level,
                world_chunk.tag,
            )
            marker_candidates += int(scanned["markerCandidates"])
            rejected_candidates += int(scanned["rejectedCandidates"])
            for instance in scanned["instances"]:
                candidates = []
                for candidate in instance.pop("physicsMeshCandidates"):
                    mesh_name = str(candidate["mesh"])
                    rows = membership_lookup.get(
                        (level, _normalized_mesh_identity(mesh_name)),
                        [],
                    )
                    loose_mesh = loose_lookup.get(_loose_mesh_key(mesh_name))
                    candidates.append((candidate, rows, loose_mesh))
                exact = [
                    item for item in candidates if len(item[1]) == 1 and item[2] is not None
                ]
                if len(exact) != 1:
                    unresolved.append(
                        {
                            "definition": instance["definition"],
                            "level": level,
                            "recordOffset": instance["recordOffset"],
                            "worldKind": instance["worldKind"],
                        }
                    )
                    continue
                candidate, level_rows, loose_mesh = exact[0]
                instance.update(
                    {
                        "levelMeshChunkIndex": level_rows[0]["chunkIndex"],
                        "logicalMethod": level_rows[0]["logicalMethod"],
                        "looseMesh": loose_mesh,
                        "meshFieldId": candidate["meshFieldId"],
                        "meshFieldValue": candidate["mesh"],
                        "physicsRecordType": candidate["physicsRecordType"],
                    }
                )
                for key in (
                    "behaviorSerializedType",
                    "factorySelector",
                    "memberShell",
                    "unitDefinitionOrdinal",
                ):
                    if key in candidate:
                        instance[key] = candidate[key]
                instance.update(mesh_metadata[str(loose_mesh)])
                script_file = None
                if instance["script"]:
                    script_file = script_files.get(
                        f"missionscripts/level{level}/{instance['script']}.msl".casefold()
                    )
                instance["scriptFile"] = script_file
                instance["animationCallSites"] = (
                    call_counts.get(str(script_file).casefold(), 0) if script_file else 0
                )
                instances.append(instance)

        for chunk in parse_top_level_chunks(raw):
            if chunk.tag != "MESH":
                continue
            payload = raw[chunk.offset + 8:chunk.offset + 8 + chunk.size]
            _logical, display_name, method = logical_key("MESH", payload)
            if display_name:
                continue
            stream = _direct_embedded_cmsh(payload)
            parsed = parse_cmsh_stream(stream)
            parts = parsed.file_parts()
            motion_class, _moving = _motion_class(parts)
            core = _cmsh_core(stream)
            normalized = _normalized_cmsh_core_sha256(stream)
            anonymous_rows.append(
                {
                    "boneCarriers": sum(bool(part.bones) for part in parts),
                    "chunkIndex": chunk.index,
                    "coreBytes": len(core),
                    "coreSha256": hashlib.sha256(core).hexdigest(),
                    "displayName": display_name,
                    "internalName": parsed.name,
                    "level": level,
                    "logicalMethod": method,
                    "looseCoreMatches": sorted(loose_core_lookup.get(normalized, [])),
                    "motionClass": motion_class,
                    "normalizedCoreSha256": normalized,
                    "partCount": len(parts),
                    "streamBytes": len(stream),
                    "streamSha256": hashlib.sha256(stream).hexdigest(),
                }
            )

    instances.sort(
        key=lambda row: (
            str(row["level"]),
            str(row["worldKind"]),
            int(row["recordOffset"]),
        )
    )
    anonymous_rows.sort(key=lambda row: (str(row["level"]), int(row["chunkIndex"])))
    direct_instances = [row for row in instances if int(row["animationCallSites"]) > 0]
    direct_call_files = {
        str(row["scriptFile"]).casefold() for row in direct_instances if row["scriptFile"]
    }
    authored_call_files = {
        str(row["script"]).casefold() for row in animation_calls["rows"]
    }
    unjoined_files = sorted(authored_call_files - direct_call_files)
    unjoined_sites = sum(call_counts[file_name] for file_name in unjoined_files)
    absent_loose = sorted(set(mesh_metadata) - set(membership["levelsByLooseMesh"]))
    absent_use = {
        file_name: [
            {
                "definition": row["definition"],
                "level": row["level"],
                "recordOffset": row["recordOffset"],
                "worldKind": row["worldKind"],
            }
            for row in instances
            if row["looseMesh"] == file_name
        ]
        for file_name in absent_loose
    }
    unit_definitions = list(physics["unitDefinitions"])
    if len({str(row["definition"]) for row in unit_definitions}) != len(
        unit_definitions
    ):
        raise ValueError("Unit definition names are not unique")
    unit_instances = [
        row for row in instances if int(row["physicsRecordType"]) == 1
    ]
    if any(
        key not in row
        for row in unit_instances
        for key in (
            "behaviorSerializedType",
            "factorySelector",
            "memberShell",
            "unitDefinitionOrdinal",
        )
    ):
        raise ValueError("a joined Unit instance lacks behaviour metadata")
    placed_unit_names = {str(row["definition"]) for row in unit_instances}
    known_unit_names = {str(row["definition"]) for row in unit_definitions}
    if not placed_unit_names <= known_unit_names:
        raise ValueError("a joined Unit instance lacks an ordered Unit definition")
    unplaced_unit_definitions = [
        row for row in unit_definitions if str(row["definition"]) not in placed_unit_names
    ]
    selector_rows = []
    for selector, member_shell in enumerate(UNIT_MEMBER_SHELL_BY_SELECTOR):
        authored = [
            row for row in unit_definitions if int(row["factorySelector"]) == selector
        ]
        placed = [
            row for row in unit_instances if int(row["factorySelector"]) == selector
        ]
        selector_rows.append(
            {
                "authoredDefinitions": len(authored),
                "levels": len({str(row["level"]) for row in placed}),
                "memberShell": member_shell,
                "placedDefinitions": len(
                    {str(row["definition"]) for row in placed}
                ),
                "placements": len(placed),
                "placementsByKind": {
                    kind: sum(str(row["worldKind"]) == kind for row in placed)
                    for kind in ("BSWD", "RLWD")
                },
                "selector": selector,
            }
        )
    unit_behavior_summary = {
        "definitions": len(unit_definitions),
        "levels": len({str(row["level"]) for row in unit_instances}),
        "placedDefinitions": len(placed_unit_names),
        "placements": len(unit_instances),
        "placementsByKind": {
            kind: sum(str(row["worldKind"]) == kind for row in unit_instances)
            for kind in ("BSWD", "RLWD")
        },
        "selectorsWithPlacements": sum(bool(row["placements"]) for row in selector_rows),
        "unplacedDefinitions": len(unplaced_unit_definitions),
    }
    summary = {
        "activeInstances": sum(bool(row["active"]) for row in instances),
        "archives": len(archives),
        "boneCarrierInstances": sum(bool(row["boneCarriers"]) for row in instances),
        "directScriptInstances": sum(row["scriptFile"] is not None for row in instances),
        "instances": len(instances),
        "instancesByKind": dict(collections.Counter(str(row["worldKind"]) for row in instances)),
        "instancesByThingType": {
            str(key): value
            for key, value in sorted(collections.Counter(int(row["thingType"]) for row in instances).items())
        },
        "meshNumberCounts": {
            str(key): value
            for key, value in sorted(collections.Counter(int(row["meshNumber"]) for row in instances).items())
        },
        "motionClassCounts": dict(
            collections.Counter(str(row["motionClass"]) for row in instances)
        ),
        "physicsDefinitionNames": len(definitions),
        "physicsRecords": int(physics["recordCount"]),
        "resolvedNamedLevelMeshInstances": len(instances),
        "uniqueDefinitions": len({str(row["definition"]) for row in instances}),
        "uniqueLooseMeshes": len({str(row["looseMesh"]) for row in instances}),
        "unresolvedResourceInstances": len(unresolved),
        "unresolvedScriptInstances": sum(
            bool(row["script"]) and row["scriptFile"] is None for row in instances
        ),
    }
    anonymous_summary = {
        "archives": len({str(row["level"]) for row in anonymous_rows}),
        "boneCarrierRows": sum(bool(row["boneCarriers"]) for row in anonymous_rows),
        "internalNameCounts": dict(
            collections.Counter(str(row["internalName"]) for row in anonymous_rows)
        ),
        "looseCoreMatches": sum(len(row["looseCoreMatches"]) for row in anonymous_rows),
        "motionClassCounts": dict(
            collections.Counter(str(row["motionClass"]) for row in anonymous_rows)
        ),
        "partCountCounts": {
            str(key): value
            for key, value in sorted(collections.Counter(int(row["partCount"]) for row in anonymous_rows).items())
        },
        "rows": len(anonymous_rows),
        "uniqueCoreHashes": len({str(row["coreSha256"]) for row in anonymous_rows}),
        "uniqueStreamHashes": len({str(row["streamSha256"]) for row in anonymous_rows}),
    }
    animation_summary = {
        "authoredCallFiles": len(authored_call_files),
        "authoredCallSites": int(animation_calls["sites"]),
        "directInstanceCallFiles": len(direct_call_files),
        "directInstanceCallSites": sum(int(row["animationCallSites"]) for row in direct_instances),
        "directInstances": len(direct_instances),
        "unjoinedCallFiles": len(unjoined_files),
        "unjoinedCallSites": unjoined_sites,
    }
    return {
        "absentLooseWresInstances": absent_use,
        "animationJoin": {
            "summary": animation_summary,
            "unjoinedFiles": unjoined_files,
        },
        "anonymousEmbedded": {
            "rows": anonymous_rows,
            "summary": anonymous_summary,
        },
        "instances": instances,
        "looseMeshesWithoutNamedMembership": absent_loose,
        "scanBoundary": {
            "markerCandidates": marker_candidates,
            "rejectedCandidates": rejected_candidates,
        },
        "summary": summary,
        "unitBehaviorJoin": {
            "levelsWithoutUnitPlacements": sorted(
                {path.name.split("_", 1)[0] for path in archives}
                - {str(row["level"]) for row in unit_instances}
            ),
            "selectorRows": selector_rows,
            "summary": unit_behavior_summary,
            "unplacedDefinitions": unplaced_unit_definitions,
        },
        "unresolvedResourceInstances": unresolved,
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
    physics_path = data_root / "default physics.dat"
    if (
        not mesh_root.is_dir()
        or not resource_root.is_dir()
        or not script_root.is_dir()
        or not physics_path.is_file()
    ):
        raise ValueError(
            "data root does not contain resources/meshes, resources, "
            "MissionScripts, and default physics.dat"
        )

    mesh_paths = sorted(
        mesh_root.glob("*.msh.aya", case_sensitive=False),
        key=lambda item: item.name.casefold(),
    )
    outcomes = [_mesh_record(path, source_root=data_root, source_context="loose-mesh") for path in mesh_paths]
    mesh_records = [record for record, _mesh in outcomes]
    parsed = [(record, mesh) for record, mesh in outcomes if mesh is not None]
    parsed_records = [record for record, _mesh in parsed]
    membership = _level_mesh_membership(resource_root, parsed)
    calls = _animation_calls(script_root)
    world_instances = _world_instance_join(data_root, parsed, membership, calls)
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
        _verify_index(
            data_root,
            mirror_index,
            [*mesh_paths, *numeric_archives, *scripts, physics_path],
        )
        if mirror_index is not None
        else None
    )
    a_frames = collections.Counter(
        str(part.anim_frames) for _record, mesh in parsed for part in mesh.file_parts()
    )
    summary = {
        "meshes": len(mesh_records),
        "parts": sum(int(record["partCount"]) for record in parsed_records),
        "meshesWithNontrivialFrameMaps": sum(bool(record["movingParts"]) for record in parsed_records),
        "partsWithNontrivialFrameMaps": sum(len(record["movingParts"]) for record in parsed_records),
        "motionClassCounts": dict(collections.Counter(str(record["motionClass"]) for record in parsed_records)),
        "boneMeshes": sum(bool(record["boneCarriers"]) for record in parsed_records),
        "boneCarriers": sum(len(record["boneCarriers"]) for record in parsed_records),
        "hfovMeshes": sum(bool(record["hfov"]) for record in parsed_records),
        "hfovParts": sum(len(record["hfov"]) for record in parsed_records),
        "aFrameValueCounts": dict(sorted(a_frames.items())),
    }
    return {
        "schema": SCHEMA,
        "inputVerification": verification,
        "meshSummary": summary,
        "modelMetadataCoverage": {
            "selectedOccurrences": len(outcomes), "legacyJoinEligible": len(parsed),
            "outcomeCounts": dict(sorted(collections.Counter(
                str(record["modelMetadata"]["status"]) for record in mesh_records
            ).items())),
            "unknownOccurrences": [record["modelMetadata"]["identity"]["occurrenceId"]
                                   for record, _mesh in outcomes
                                   if record["modelMetadata"]["status"] == "unparsed"],
            "scope": "selected loose *.msh.aya files; not a complete archive or platform inventory",
        },
        "meshes": mesh_records,
        "levelMeshMembership": membership,
        "missionAnimationCalls": calls,
        "worldInstanceJoin": world_instances,
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
    world = report["worldInstanceJoin"]
    print(
        "WRES definition instances: "
        f"{world['summary']['resolvedNamedLevelMeshInstances']}/"
        f"{world['summary']['instances']} joined to named LVLR rows and loose CMSH"
    )
    print(
        "Anonymous embedded CMSH: "
        f"{world['anonymousEmbedded']['summary']['rows']} empty-name rows, "
        f"{world['anonymousEmbedded']['summary']['looseCoreMatches']} loose-core matches"
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
