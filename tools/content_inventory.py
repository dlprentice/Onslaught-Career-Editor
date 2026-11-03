#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Battle Engine Aquila content inventory: a byte account of every file of a selected install, and a list of every
model, texture, image, animation, sound, film and text asset in it, used or not.

tools/content_catalog.py says what the game's files hold and what names what. This tool answers a different question:
of the bytes on the disc, how many has a reader actually understood? Each file is walked by the reader that follows
its loader, or by its format's published layout, and every byte of its stream lands in exactly one part of an account:

  decoded     a reader consumed these bytes in the loader's order and its walk closed exactly. A codec payload counts
              when every bit pattern decodes (raw pixels, DXT blocks, IMA ADPCM, deflate that inflated), or when an
              independent decoder read it without an error and agreed with the walk's counts (Vorbis, Bink, JPEG; see
              --media-decoder). A decoded byte means a reader owns it; it does not claim that every field has a known
              meaning, and it says nothing about how the game behaves.
  referenced  a record or reader establishes what these bytes are and how long they are, but nothing has read their
              contents.
  unknown     neither. A gap in a walk falls here by construction, so a reader cannot lose bytes silently.

A file with nothing but decoded bytes is "decoded", with nothing but referenced bytes "referenced", with nothing but
unknown bytes "unknown", and any mix is "partial". An empty file is decoded. Separately from that class, "used" says
that a catalogue record, a physics value, a page link or a loader rule names the file or asset; it is not a runtime
observation.

Bytes are logical: an AYA envelope's inflated stream, and a plain file's own bytes. The stored size of every file is
reported beside them, and the stored sizes sum to the install's size or the run fails.

The install is only read. Run output is retail-derived (names, sizes, hashes, never payload bytes), so it is written
only below this checkout's ignored local-data/ directory and carries the generatedRetailDerived marker.

Run:  python ./tools/content_inventory.py --game GAME_FOLDER [--decomp ONSLAUGHT_DECOMP] [--out local-data/content-inventory]
                                          [--media-decoder ffmpeg | --no-media-decoder]
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import datetime
import hashlib
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path, PurePosixPath

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(ROOT / "rebuild" / "tools"))

import aya_archive_inventory as aai  # noqa: E402
import aya_cross_platform_compare as cross  # noqa: E402
import cmsh_animation_usage_census as meshcensus  # noqa: E402
import cmsh_grammar_walk as grammar  # noqa: E402
import cmsh_static_preview as preview  # noqa: E402
import content_catalog as cc  # noqa: E402
import dds_census  # noqa: E402
import game_tables_decode as gtd  # noqa: E402
import goodie_resource_walk as goodies  # noqa: E402
import language_dat_decode  # noqa: E402
import media_readers as media  # noqa: E402
import msl_compile as mc  # noqa: E402
import msl_gate  # noqa: E402
import named_things as nt  # noqa: E402
import options_entries_decode as options  # noqa: E402
import physics_values_decode as physics  # noqa: E402
import world_resources_decode as wrd  # noqa: E402
import world_resources_encode as wre  # noqa: E402
import worldheaders_decode  # noqa: E402
import xap_bank_walk  # noqa: E402
from safe_generated_output import SecuredOutputRoot, UnsafeGeneratedOutputError, validate_disjoint_output_root  # noqa: E402

SCHEMA_VERSION = 1
COVERAGE_SCHEMA = "onslaught.content-inventory.coverage.v1"
FILE_SCHEMA = "onslaught.content-inventory.file.v1"
ITEM_SCHEMA = "onslaught.content-inventory.item.v1"
MANIFEST_SCHEMA = "onslaught.content-inventory.manifest.v1"
GENERATED_MARKER = cc.GENERATED_MARKER
TOOL = "tools/content_inventory.py"

DECODED, REFERENCED, UNKNOWN = "decoded", "referenced", "unknown"
BYTE_CLASSES = (DECODED, REFERENCED, UNKNOWN)
PARTIAL = "partial"
FILE_CLASSES = (DECODED, PARTIAL, REFERENCED, UNKNOWN)
NOT_CONTENT_FAMILIES = ("executable-code", "install-metadata", "save-game")
# Relationship statuses that name their target. "incomplete" and the unresolved statuses do not.
NAMING_STATUSES = frozenset({"resolved", "resolved-per-archive", "name-match", "code-site", "code-rule", "runtime-name"})
MEDIA_TIMEOUT = 900
MEDIA_FAMILIES = ("ogg-music", "ogg-voice", "bink-video")
MSL_COMPILED = ("exact", "exact, assisted", "stale source")
NO_AUDIO = 0xFFFFFFFF  # a language entry's audio offset when it names no voice file

# Particle set keys in token order (rebuild/OnslaughtRebuild.Parity/Particles/TokenArchive.cs, the file format's own keys).
PARTICLE_TOKENS = frozenset((
    "File_Version", "Num_Particle_Descriptors", "Particle_Descriptor_Type", "Particle_Descriptor_Name",
    "*****************************************************************", "Radius", "Final_Radius", "Gravity", "Bounce",
    "Fade_Col", "Texture", "Modifier", "Blend_Mode", "Texture_Number", "Axis_Aligned", "Colour_Range", "Anim_Type",
    "End_Frame", "Anim_Speed", "Texture_Size", "Velocity_Damp", "Life_Pct", "Random_Start_Frame", "Length", "2D",
    "Emit_Per_Turn", "Life", "Particle_Descriptor", "Initial_Velocity_X", "Initial_Velocity_Y", "Initial_Velocity_Z",
    "Velocity_Randomness", "Transmit_Life", "Transmit_FoR", "Transmit_Velocity", "Interpolated_Emission", "Shape",
    "Pass_Num_Particles", "Outward_Velocity", "Mover", "Particle_Descriptor_0", "Particle_Descriptor_1",
    "Particle_Descriptor_2", "Particle_Descriptor_3", "Probability_0", "Probability_1", "Probability_2", "Probability_3",
    "Start_Red", "Start_Green", "Start_Blue", "End_Red", "End_Green", "End_Blue", "Transition_Red", "Transition_Green",
    "Transition_Blue", "Use_End", "Use_Transition", "Transition_Point", "Num_Entries", "Time", "Type", "Ring_Axis",
    "Hemisphere", "Num_Particles", "Hollow", "RandomSX", "RandomSY", "RandomSZ", "Width", "Num_Points", "Start_Width",
    "Wiggle_Factor", "Disperse_Rate", "Taper_Start", "Width_With_Life", "Fade_Point", "Use_Segment_Length",
    "SegmentLength", "Manual_Wiggle_Enabled", "Wiggle_Length", "Yaw_Length", "Flat", "GravityPC", "Yaw", "Pitch", "Roll",
    "Yaw_Function", "Pitch_Function", "Roll_Function", "Param_A", "Param_B", "Param_C", "Param_D", "Param_Function",
    "Clip", "Value_Type", "Gameturn_Scale", "Offset_Gameturn", "Mesh", "Angular_Momentum", "Impact_Spawnee",
    "Auto_Centre", "Initial", "Death", "Tile_U", "Tile_V", "Scroll_U", "Scroll_V", "Cylinder_NumPtsAxial",
    "Cylinder_NumPtsRadial", "Cylinder_Radius", "Cylinder_Radius2", "Cylinder_Length", "Colour_Range2",
    "Sphere_NumPtsAx", "Sphere_NumPtsRad", "Sphere_RadiusTime", "Sphere_Latitude_Start", "Sphere_Latitude_End",
    "Sphere_Longitude_Start", "Sphere_Longitude_End"))
PARTICLE_HEADER = b"ParticleSystemEd_File_"


class AccountError(ValueError):
    """A reader claimed bytes that do not exist or that another part already holds."""


class Account:
    """Every byte of one stream in exactly one part. Anything no part claims is unknown."""

    def __init__(self, size: int):
        if size < 0:
            raise AccountError("negative stream size")
        self.size = size
        self.rows: list[tuple[int, int, str, str]] = []

    def add(self, start: int, length: int, klass: str, part: str) -> None:
        if klass not in BYTE_CLASSES:
            raise AccountError(f"unknown byte class {klass!r}")
        if start < 0 or length < 0 or start + length > self.size:
            raise AccountError(f"part {part} claims bytes outside its stream")
        if length:
            self.rows.append((start, start + length, klass, part))

    def close(self) -> dict:
        """The per-class and per-part totals and the unknown spans; overlapping claims are refused."""
        totals: collections.Counter = collections.Counter()
        parts: collections.Counter = collections.Counter()
        unknown: list[list] = []

        def note_unknown(start: int, end: int, part: str) -> None:
            if unknown and unknown[-1][1] == start and unknown[-1][2] == part:
                unknown[-1][1] = end
            else:
                unknown.append([start, end, part])

        position = 0
        for start, end, klass, part in sorted(self.rows):
            if start < position:
                raise AccountError(f"part {part} overlaps an earlier part")
            if start > position:
                note_unknown(position, start, "unclaimed")
                totals[UNKNOWN] += start - position
                parts[(UNKNOWN, "unclaimed")] += start - position
            totals[klass] += end - start
            parts[(klass, part)] += end - start
            if klass == UNKNOWN:
                note_unknown(start, end, part)
            position = end
        if position < self.size:
            note_unknown(position, self.size, "unclaimed")
            totals[UNKNOWN] += self.size - position
            parts[(UNKNOWN, "unclaimed")] += self.size - position
        if sum(totals.values()) != self.size:
            raise AccountError("the parts do not sum to the stream size")
        return {"totals": {klass: totals[klass] for klass in BYTE_CLASSES},
                "parts": [{"part": part, "class": klass, "bytes": count}
                          for (klass, part), count in sorted(parts.items(), key=lambda kv: (kv[0][1], kv[0][0]))],
                "unknownSpans": unknown}

    def spans_of(self, klass: str) -> list[tuple[int, int]]:
        """The merged byte ranges a class holds, for checking a record's coordinates against the account."""
        merged: list[list[int]] = []
        for start, end, row_class, _part in sorted(self.rows):
            if row_class != klass:
                continue
            if merged and merged[-1][1] == start:
                merged[-1][1] = end
            else:
                merged.append([start, end])
        return [(start, end) for start, end in merged]


def file_class(size: int, totals: dict) -> str:
    if size == 0:
        return DECODED
    present = [klass for klass in BYTE_CLASSES if totals[klass]]
    return present[0] if len(present) == 1 else PARTIAL


class Context:
    """What the readers share: the selected game, the lookups a world body needs and the per-run proofs."""

    def __init__(self, game: Path, *, media_results: dict | None = None, msl_verdicts: dict | None = None):
        self.game = game
        self.lookup: dict | None = None
        self.media = media_results if media_results is not None else {}
        self.msl = msl_verdicts if msl_verdicts is not None else {}
        self.proofs: collections.Counter = collections.Counter()
        self.links: dict[str, list[str]] = {}
        self.install_manifest: list[str] | None = None
        self.physics: dict | None = None

    def world_lookup(self) -> dict:
        """The physics names parse_world_body needs (the same derivation as tools/content_catalog_gate.py)."""
        if self.lookup is None:
            data = cc.read_install_file(self.game / "data" / "default physics.dat")
            names = cc.physics_names(data)
            behaviours = nt.first_behaviours(meshcensus._physics_mesh_definitions(data)["unitDefinitions"])
            self.lookup = {"units": set(names["unit"]), "features": set(names["feature"]),
                           "hazards": set(names["hazard"]),
                           "squadless": {n for n, b in behaviours.items() if nt.squad_class(b) is None}}
        return self.lookup


class Reading:
    """One reader's outcome: the account of the stream it walked, what it refused and the assets it found."""

    def __init__(self, account: Account, stream: str, reader: str):
        self.account, self.stream, self.reader = account, stream, reader
        self.problems: list[str] = []
        self.facts: dict = {}
        self.items: list[dict] = []


def whole_file(data: bytes, klass: str, part: str, reader: str) -> Reading:
    reading = Reading(Account(len(data)), "stored", reader)
    reading.account.add(0, len(data), klass, part)
    return reading


def refused(data: bytes, part: str, reader: str, error: Exception) -> Reading:
    """A reader refused the file: the family establishes what it is, nothing read its contents."""
    reading = whole_file(data, REFERENCED, part, reader)
    reading.problems.append(str(error))
    return reading


def from_walk(walk: media.Walk, data: bytes, reader: str, *, opaque_decoded: bool = False) -> Reading:
    """A public-format walk as an account: what it read is decoded, and what it framed only if a decoder read it."""
    reading = Reading(Account(len(data)), "stored", reader)
    for start, length, kind, part in walk.spans:
        klass = DECODED if kind == media.DECODED or opaque_decoded else REFERENCED
        reading.account.add(start, length, klass, part)
    reading.facts = dict(walk.facts)
    return reading


def asset_item(kind: str, form: str, name: str, *, offset: int | None, length: int | None, sha: str, status: str,
               **extra) -> dict:
    return {"kind": kind, "form": form, "name": name, "offset": offset, "length": length, "sha256": sha,
            "status": status, **extra}


# ---------------------------------------------------------------------------------------- archives (LVLR tag streams)
FIXED_PREFIX = {"LVLR": 4, "TARG": 4, "AYAD": 24}
PAYLOAD_DECODERS = {"ERES": wrd.parse_eres, "SURF": wrd.parse_surf, "SSHD": wrd.parse_sshd, "VSDS": wrd.parse_vsds,
                    "PMIB": wrd.parse_pmib, "DMKR": wrd.parse_dmkr}
DECODE_ERRORS = (wrd.DecodeError, struct.error, ValueError)


def chunks_in(data: bytes, start: int, end: int) -> list[tuple[str, int, int]]:
    """(tag, payload offset, payload size) of the chunks that fill [start, end) exactly."""
    rows, at = [], start
    while at < end:
        if at + 8 > end:
            raise ValueError("truncated chunk header")
        (size,) = struct.unpack_from("<I", data, at + 4)
        if at + 8 + size > end:
            raise ValueError("chunk runs past its parent")
        rows.append((data[at:at + 4].decode("latin-1"), at + 8, size))
        at += 8 + size
    return rows


def prove_mesh(stream: bytes, proofs: collections.Counter, chain: list[bytes]) -> None:
    """Re-emit a mesh stream from its parsed model, chained meshes too: what the model regenerates is counted apart from
    what it only copies (rebuild/tools/cmsh_static_preview.py keeps the two in separate columns). Every chained stream
    is appended to chain, nearest first."""
    identical, accounting = preview.round_trip_cmsh_stream(stream)
    proofs["meshStreamsRoundTripped"] += 1
    proofs["meshStreamsIdentical" if identical else "meshStreamsDifferent"] += 1
    derived, carried = accounting.derived, accounting.carried
    for sibling in preview.parse_cmsh_stream(stream).siblings:
        tag = sibling.tag if isinstance(sibling.tag, str) else sibling.tag.decode("latin-1")
        body = sibling.raw_payload
        if tag == "PMSH" and body[:4] == b"PMS2":
            body = body[8 + goodies.MESH_REFERENCE:]
        if tag in ("PMS2", "PMSH") and body[:4] == b"CMSH":
            chain.append(body)
            before = proofs["meshBytesDerived"] + proofs["meshBytesCarried"]
            prove_mesh(body, proofs, chain)
            carried -= proofs["meshBytesDerived"] + proofs["meshBytesCarried"] - before
    proofs["meshBytesDerived"] += derived
    proofs["meshBytesCarried"] += carried


def chained_items(chain: list[bytes], owner: str, path: str, envelope: str, reading: Reading) -> None:
    """A chained mesh is stored structure the catalogue's mesh record lists only one link of: list every link and its
    animations, with no claim that the renderer selects it."""
    for link, stream in enumerate(chain):
        asset_id = f"{owner}/chained#{link}"
        record, animations, _uv = cc.catalog_mesh(stream, asset_id=asset_id, name="", container=path,
                                                  container_sha=cc.sha256(stream), envelope=envelope, offset=0,
                                                  chunk_path=[])
        reading.items.append(asset_item("model", "chained-mesh", record["name"], offset=None, length=len(stream),
                                        sha=cc.sha256(stream), status=DECODED, id=asset_id, owner=owner, link=link,
                                        parts=record["mesh"]["parts"]))
        reading.items.extend(asset_item("animation", "chained-animation", animation["name"], offset=None, length=36,
                                        sha=animation["sha256"], status=DECODED, id=animation["id"], owner=owner)
                             for animation in animations)


def read_mesh_stream(stream: bytes, reading: Reading, ctx: Context, owner: str, path: str, envelope: str) -> bool:
    """A CMSH stream, walked in the loader's order to its exact end, re-emitted, and its chain listed."""
    different = ctx.proofs["meshStreamsDifferent"]
    chain: list[bytes] = []
    try:
        grammar.walk_stream(stream, collections.defaultdict(collections.Counter))
        prove_mesh(stream, ctx.proofs, chain)
    except (grammar.GrammarError, preview.CmshProfileError, struct.error) as error:
        reading.problems.append(f"CMSH: {error}")
        return False
    if ctx.proofs["meshStreamsDifferent"] != different:
        reading.problems.append("CMSH: the parsed model does not re-emit the stream")
    chained_items(chain, owner, path, envelope, reading)
    return True


def read_mesh_record(raw: bytes, at: int, end: int, reading: Reading, ctx: Context, path: str, chunk: int) -> None:
    """CMesh::Deserialize's record: PMSH holding PMS2 or the body itself; the body is the 309-byte reference, followed
    by nothing (the mesh is a loose file), a mesh stream, or the next record of a chain."""
    account = reading.account
    rows = chunks_in(raw, at, end)
    if len(rows) != 1 or rows[0][0] != "PMSH":
        raise ValueError("a mesh record is not one PMSH")
    account.add(at, 8, DECODED, "MESH/framing")
    body = at + 8
    if raw[body:body + 4] == b"PMS2" and body + 8 + struct.unpack_from("<I", raw, body + 4)[0] == end:
        account.add(body, 8, DECODED, "MESH/framing")
        body += 8
    if body + goodies.MESH_REFERENCE > end:
        raise ValueError("a mesh record is shorter than its reference")
    account.add(body, goodies.MESH_REFERENCE, DECODED, "MESH/reference")
    rest = body + goodies.MESH_REFERENCE
    if rest == end:
        return
    if raw[rest:rest + 4] == b"CMSH":
        ok = read_mesh_stream(raw[rest:end], reading, ctx, f"mesh:embedded:{path.casefold()}#{chunk}", path,
                              "lvlr-chunk(MESH/PMSH/PMS2)")
        account.add(rest, end - rest, DECODED if ok else REFERENCED, "MESH/embedded-cmsh")
    elif raw[rest:rest + 4] == b"PMSH":
        read_mesh_record(raw, rest, end, reading, ctx, path, chunk)
    else:
        account.add(rest, end - rest, UNKNOWN, "MESH/tail")


def read_world_chunk(raw: bytes, base: int, size: int, ctx: Context, reading: Reading) -> None:
    """WRES: WRLD holding WDAT and the world bodies, each read by CWorld::LoadWorld's order."""
    account = reading.account
    for tag, body, length in chunks_in(raw, base, base + size):
        if tag != "WRLD":
            account.add(body - 8, 8 + length, UNKNOWN, "WRES/" + tag)
            continue
        account.add(body - 8, 8, DECODED, "WRES/framing")
        for child, at, child_size in chunks_in(raw, body, body + length):
            if child == "WDAT" and child_size == 8:
                account.add(at - 8, 16, DECODED, "WRES/WDAT")
            elif child in cc.WORLD_KINDS:
                try:
                    wrd.parse_world_body(raw[at:at + child_size], ctx.world_lookup(), base=child == "BSWD")
                except DECODE_ERRORS as error:
                    reading.problems.append(f"{child}: {error}")
                    account.add(at - 8, 8 + child_size, REFERENCED, "WRES/" + child)
                    continue
                account.add(at - 8, 8 + child_size, DECODED, "WRES/" + child)
            else:
                account.add(at - 8, 8 + child_size, UNKNOWN, "WRES/" + child)


VIEW_RECORD = 24  # six floats: left, right, top, bottom, width, height (rebuild/tools/materialize_retail_assets.py)


def views_hold(body: bytes) -> bool:
    """Every imposter view is a finite atlas rectangle with a positive size."""
    if not body or len(body) % VIEW_RECORD:
        return False
    for at in range(0, len(body), VIEW_RECORD):
        u0, u1, v0, v1, width, height = struct.unpack_from("<6f", body, at)
        if not all(map(math.isfinite, (u0, u1, v0, v1, width, height))):
            return False
        if not (0.0 <= u0 < u1 <= 1.0 and 0.0 <= v0 < v1 <= 1.0 and width > 0.0 and height > 0.0):
            return False
    return True


def read_texture_record(raw: bytes, at: int, end: int, reading: Reading, part: str) -> None:
    """A chunk whose payload is one serialized texture (DXTX)."""
    try:
        cc.parse_text_record(raw[at:end])
    except (ValueError, struct.error) as error:
        reading.problems.append(f"{part}: {error}")
        reading.account.add(at, end - at, REFERENCED, part)
        return
    reading.account.add(at, end - at, DECODED, part)


def read_imposters(raw: bytes, base: int, size: int, reading: Reading) -> None:
    """CDXImposter::DeserializeAll's chunks: DATA, the atlas texture and the IMPO list of IMPT records."""
    account = reading.account
    rows = chunks_in(raw, base, base + size)
    if len(rows) != 1 or rows[0][0] != "IMPS":
        raise ValueError("IMPS does not hold its own IMPS chunk")
    account.add(base, 8, DECODED, "IMPS/framing")
    _tag, body, length = rows[0]
    for tag, at, chunk_size in chunks_in(raw, body, body + length):
        account.add(at - 8, 8, DECODED, "IMPS/framing")
        if tag == "DATA":
            account.add(at, chunk_size, REFERENCED, "IMPS/DATA")
        elif tag == "BTXT":
            read_texture_record(raw, at, at + chunk_size, reading, "IMPS/atlas-texture")
        elif tag == "IMPO":
            (count,) = struct.unpack_from("<I", raw, at)
            account.add(at, 4, DECODED, "IMPS/framing")
            records = chunks_in(raw, at + 4, at + chunk_size)
            if len(records) != count or any(row[0] != "IMPT" for row in records):
                raise ValueError("IMPO's count disagrees with its IMPT records")
            for _impt, record, record_size in records:
                account.add(record - 8, 8, DECODED, "IMPS/framing")
                for child, inner, inner_size in chunks_in(raw, record, record + record_size):
                    account.add(inner - 8, 8, DECODED, "IMPS/framing")
                    if child == "CIMP" and inner_size >= 68:
                        account.add(inner, 4, REFERENCED, "IMPS/CIMP-fields")
                        account.add(inner + 4, 64, DECODED, "IMPS/label")
                        account.add(inner + 68, inner_size - 68, REFERENCED, "IMPS/CIMP-fields")
                    elif child == "IMSH" and inner_size == 4:
                        account.add(inner, 4, DECODED, "IMPS/mesh-id")
                    elif child == "VIEW" and views_hold(raw[inner:inner + inner_size]):
                        account.add(inner, inner_size, DECODED, "IMPS/views")
                    elif child == "VIEW":
                        account.add(inner, inner_size, REFERENCED, "IMPS/views-unproved")
                    else:
                        account.add(inner, inner_size, UNKNOWN, "IMPS/" + child)
        else:
            account.add(at, chunk_size, UNKNOWN, "IMPS/" + tag)


def read_platform(raw: bytes, base: int, size: int, reading: Reading) -> None:
    """CPCPlatform::Deserialize: four fonts, each its texture and two records no reader interprets yet."""
    account = reading.account
    for tag, body, length in chunks_in(raw, base, base + size):
        account.add(body - 8, 8, DECODED, "PLAT/framing")
        if tag != "FONT":
            account.add(body, length, UNKNOWN, "PLAT/" + tag)
            continue
        for child, at, child_size in chunks_in(raw, body, body + length):
            account.add(at - 8, 8, DECODED, "PLAT/framing")
            if child == "FNTT":
                read_texture_record(raw, at, at + child_size, reading, "PLAT/font-texture")
            elif child in ("FGEN", "DXFT"):
                account.add(at, child_size, REFERENCED, "PLAT/" + child)
            else:
                account.add(at, child_size, UNKNOWN, "PLAT/" + child)


def payload_items(tag: str, payload: bytes, decoded: dict, offset: int) -> list[dict]:
    """The assets a level payload holds that no catalogue record lists one by one."""
    sha = cc.sha256(payload)
    if tag == "ERES":
        rows = [asset_item("texture", "terrain-mixer-mip", f"mixer mip {m['mip']}", offset=offset, length=m["textures"]
                           * m["textureBytes"], sha=m["pixelSha256"] or sha, status=DECODED, textures=m["textures"],
                           textureSize=m["size"]) for m in decoded["mixerMips"]]
        rows.append(asset_item("model", "terrain-heightfield", "heightfield", offset=offset, length=len(payload), sha=sha,
                               status=DECODED, samples=decoded["heightField"]["sampleCount"]))
        return rows
    if tag == "SURF":
        return [asset_item("model", "surface-strips", "surface strips", offset=offset, length=len(payload), sha=sha,
                           status=DECODED, strips=decoded.get("strips"))]
    if tag == "SSHD":
        return [asset_item("texture", "static-shadow-maps", "static shadows", offset=offset, length=len(payload), sha=sha,
                           status=DECODED, shadows=decoded.get("shadows"), cells=decoded.get("cells"))]
    if tag == "DMKR":
        return [asset_item("texture", "damage-texture", "landscape damage", offset=offset, length=len(payload), sha=sha,
                           status=DECODED, levels=decoded.get("levels"))]
    return []


def read_archive(data: bytes, ctx: Context, row: dict) -> Reading:
    raw, chunks, members, _envelope = aai.decode_archive_envelope(data, "pc-chunked-zlib")
    reading = Reading(Account(len(raw)), "inflated", "tools/aya_archive_inventory.py:decode_archive_envelope")
    account = reading.account
    reading.facts = {"members": members, "chunks": len(chunks)}
    for chunk in chunks:
        base = chunk.offset + 8
        tag = chunk.tag
        if tag in FIXED_PREFIX:
            account.add(chunk.offset, 8 + chunk.size, DECODED if chunk.size == FIXED_PREFIX[tag] else REFERENCED, tag)
        elif tag == "LNDS":
            account.add(chunk.offset, 8 + chunk.size, DECODED if chunk.size == 0 else REFERENCED, tag)
        elif tag == "TEXT":
            account.add(chunk.offset, 8, DECODED, "TEXT")
            read_texture_record(raw, base, base + chunk.size, reading, "TEXT")
        elif tag == "MESH":
            account.add(chunk.offset, 8, DECODED, "MESH/framing")
            try:
                read_mesh_record(raw, base, base + chunk.size, reading, ctx, row["path"], chunk.index)
            except (ValueError, struct.error) as error:
                reading.problems.append(f"MESH: {error}")
        elif tag == "WRES":
            account.add(chunk.offset, 8, DECODED, "WRES/framing")
            read_world_chunk(raw, base, chunk.size, ctx, reading)
        elif tag in PAYLOAD_DECODERS:
            payload = raw[base:base + chunk.size]
            try:
                decoded = PAYLOAD_DECODERS[tag](payload)
            except DECODE_ERRORS as error:
                reading.problems.append(f"{tag}: {error}")
                account.add(chunk.offset, 8 + chunk.size, REFERENCED, tag)
                continue
            account.add(chunk.offset, 8 + chunk.size, DECODED, tag)
            reading.items.extend(payload_items(tag, payload, decoded, base))
        elif tag == "GDIE":
            try:
                goodies.read_goodie(raw)
            except (goodies.GoodieError, struct.error) as error:
                reading.problems.append(f"GDIE: {error}")
                account.add(chunk.offset, 8 + chunk.size, REFERENCED, tag)
                continue
            account.add(chunk.offset, 8 + chunk.size, DECODED, tag)
        elif tag in ("IMPS", "PLAT"):
            account.add(chunk.offset, 8, DECODED, tag + "/framing")
            try:
                (read_imposters if tag == "IMPS" else read_platform)(raw, base, chunk.size, reading)
            except (ValueError, struct.error) as error:
                reading.problems.append(f"{tag}: {error}")
        else:
            account.add(chunk.offset, 8 + chunk.size, UNKNOWN, tag)
    return reading


# ------------------------------------------------------------------------------------------------------- loose assets
def read_mesh_file(data: bytes, ctx: Context, row: dict) -> Reading:
    stream = aai.inflate_aya_bytes(data)
    reading = Reading(Account(len(stream)), "inflated", "tools/cmsh_grammar_walk.py:walk_stream")
    ok = read_mesh_stream(stream, reading, ctx, "mesh:" + row["path"].casefold(), row["path"], "aya-zlib-members(cmsh)")
    reading.account.add(0, len(stream), DECODED if ok else REFERENCED, "CMSH")
    return reading


def read_texture_file(data: bytes, _ctx: Context, _row: dict) -> Reading:
    meta = dds_census.texture_metadata(data, envelope="aya")
    dds = meta.get("dds") or {}
    size = dds.get("size") or 0
    reading = Reading(Account(size), "inflated", "tools/dds_census.py:texture_metadata")
    if meta["status"] == "valid":
        reading.account.add(0, size, DECODED, "DDS")
    else:
        reading.problems.extend(meta.get("problems") or [meta["status"]])
        reading.account.add(0, size, REFERENCED, "DDS")
    return reading


def read_sample_bank(data: bytes, _ctx: Context, _row: dict) -> Reading:
    reader = "tools/xap_bank_walk.py:read_bank"
    try:
        _magic, samples = xap_bank_walk.read_bank(data)
    except xap_bank_walk.BankError as error:
        return refused(data, "XAP", reader, error)
    reading = whole_file(data, DECODED, "XAP", reader)
    reading.facts = {"samples": len(samples)}
    return reading


def decoder_agrees(result: dict | None, facts: dict, family: str) -> bool:
    """The independent decoder read every stream without an error and agrees with the walk's own counts."""
    if result is None or not result["clean"]:
        return False
    streams = result["streams"]
    if family == "bink-video":
        return streams.get("0", {}).get("frames") == facts["frames"] and len(streams) == 1 + facts["audioTracks"]
    if family in ("ogg-music", "ogg-voice"):
        return streams.get("0", {}).get("bytes") == 2 * facts["channels"] * facts["samples"] and len(streams) == 1
    return len(streams) == 1


def read_with_decoder(walker, part: str, reader: str):
    """A public-format walk whose opaque payload counts as decoded only if an independent decoder agreed."""
    def read(data: bytes, ctx: Context, row: dict) -> Reading:
        try:
            walk = walker(data)
        except media.FormatError as error:
            return refused(data, part, reader, error)
        result = ctx.media.get(row["path"])
        agreed = decoder_agrees(result, walk.facts, row["family"])
        reading = from_walk(walk, data, reader, opaque_decoded=agreed)
        if result is None:
            reading.facts["decoder"] = "not run"
        else:
            reading.facts["decoder"] = "agrees" if agreed else "disagrees"
            reading.facts["decodedOutputSha256"] = result["sha256"]
            if not agreed:
                reading.problems.append("the independent decoder reported an error or disagreed with the walk's counts")
        return reading
    return read


def read_png(data: bytes, _ctx: Context, row: dict) -> Reading:
    reader = "tools/media_readers.py:walk_png"
    try:
        reading = from_walk(media.walk_png(data), data, reader)
    except media.FormatError as error:
        return refused(data, "png", reader, error)
    reading.items.append(asset_item("image", "png", PurePosixPath(row["path"]).name, offset=0, length=len(data),
                                    sha=cc.sha256(data), status=DECODED, width=reading.facts["width"],
                                    height=reading.facts["height"]))
    return reading


def read_tga(data: bytes, _ctx: Context, row: dict) -> Reading:
    reader = "tools/media_readers.py:walk_tga"
    try:
        reading = from_walk(media.walk_tga(data), data, reader)
    except media.FormatError as error:
        return refused(data, "tga", reader, error)
    reading.items.append(asset_item("image", "tga", PurePosixPath(row["path"]).name, offset=0, length=len(data),
                                    sha=cc.sha256(data), status=DECODED, width=reading.facts["width"],
                                    height=reading.facts["height"]))
    return reading


def read_jpeg(data: bytes, ctx: Context, row: dict) -> Reading:
    reading = read_with_decoder(media.walk_jpeg, "jpeg", "tools/media_readers.py:walk_jpeg")(data, ctx, row)
    agreed = reading.facts.get("decoder") == "agrees"
    reading.items.append(asset_item("image", "jpeg", PurePosixPath(row["path"]).name, offset=0, length=len(data),
                                    sha=cc.sha256(data), status=DECODED if agreed else REFERENCED,
                                    width=reading.facts.get("width"), height=reading.facts.get("height")))
    return reading


DIAL_FRAME = 256  # 16 x 16 one-byte indices (rebuild/OnslaughtRebuild.Host/HudView.cs, from CByteSprite's use in DrawThreats)


def read_byte_sprite(data: bytes, _ctx: Context, row: dict) -> Reading:
    """data\\\\Dial.raw: the rebuild reads its first 16 x 16 frame. Nothing has established the frames after it."""
    reading = Reading(Account(len(data)), "stored", "rebuild/OnslaughtRebuild.Host/HudView.cs (frame 0)")
    reading.account.add(0, min(DIAL_FRAME, len(data)), DECODED, "byte-sprite/frame-0")
    reading.account.add(DIAL_FRAME, max(0, len(data) - DIAL_FRAME), REFERENCED, "byte-sprite/further-bytes")
    reading.facts = {"frameBytes": DIAL_FRAME, "wholeFrames": len(data) // DIAL_FRAME}
    reading.items.append(asset_item("image", "byte-sprite", PurePosixPath(row["path"]).name, offset=0, length=len(data),
                                    sha=cc.sha256(data), status=PARTIAL, width=16, height=16))
    return reading


def read_pe(data: bytes, _ctx: Context, row: dict) -> Reading:
    reader = "tools/media_readers.py:walk_pe"
    try:
        walk = media.walk_pe(data)
    except media.FormatError as error:
        return refused(data, "pe", reader, error)
    reading = from_walk(walk, data, reader)
    reading.facts["resources"] = dict(collections.Counter(r["type"] for r in walk.facts["resources"]))
    for number, resource in enumerate(walk.facts["resources"]):
        if resource["type"] in ("icon", "bitmap"):
            body = data[resource["offset"]:resource["offset"] + resource["length"]]
            reading.items.append(asset_item("image", "pe-" + resource["type"], f"{row['path']} resource {number}",
                                            offset=resource["offset"], length=resource["length"], sha=cc.sha256(body),
                                            status=DECODED if resource["status"] == "decoded" else REFERENCED))
    return reading


def read_active_mime(data: bytes, _ctx: Context, _row: dict) -> Reading:
    reader = "tools/media_readers.py:walk_active_mime"
    try:
        return from_walk(media.walk_active_mime(data), data, reader)
    except media.FormatError as error:
        return refused(data, "mso", reader, error)


# -------------------------------------------------------------------------------------------------------------- tables
def read_language_table(data: bytes, _ctx: Context, _row: dict) -> Reading:
    """The table's header, entries and pools, with the text-pool bytes no entry reaches left unclaimed."""
    reader = "tools/language_dat_decode.py:parse_lang_dat_bytes"
    try:
        table = language_dat_decode.parse_lang_dat_bytes(data)
    except ValueError as error:
        return refused(data, "language-table", reader, error)
    reading = Reading(Account(len(data)), "stored", reader)
    account = reading.account
    pool, size = table.text_pool_off, table.uvar7
    account.add(0, pool, DECODED, "language/entries")
    claim_strings(account, data, pool, size, [entry.text_off_words * 2 for entry in table.entries], 2, "language/text-pool")
    account.add(pool + size, table.audio_pool_off - pool - size, DECODED, "language/pool-header")
    claim_strings(account, data, table.audio_pool_off, table.audio_pool_size,
                  [entry.audio_off_bytes for entry in table.entries if entry.audio_off_bytes != NO_AUDIO], 1,
                  "language/audio-pool")
    reading.facts = {"entries": table.count}
    return reading


def claim_strings(account: Account, data: bytes, pool: int, size: int, offsets: list[int], width: int, part: str) -> None:
    """Claim the zero-terminated strings a table's entries reach: a pool byte no entry reaches stays unclaimed."""
    terminator = b"\0" * width
    reached = bytearray(size)
    for at in offsets:
        end = at
        while end + width <= size and data[pool + end:pool + end + width] != terminator:
            end += width
        stop = min(end + width, size)
        if at < stop:
            reached[at:stop] = b"\1" * (stop - at)
    position = 0
    while position < size:
        on = reached[position]
        end = position
        while end < size and reached[end] == on:
            end += 1
        if on:
            account.add(pool + position, end - position, DECODED, part)
        elif data[pool + end - width:pool + end] == terminator and (end - position) % width == 0:
            account.add(pool + position, end - position, REFERENCED, part + " (reached by no entry)")
        position = end


def read_exact_table(parse, reader: str):
    """A whole-file reader that refuses anything it does not consume exactly."""
    def read(data: bytes, _ctx: Context, _row: dict) -> Reading:
        try:
            parse(data)
        except (ValueError, struct.error) as error:
            return refused(data, "table", reader, error)
        return whole_file(data, DECODED, "table", reader)
    return read


def read_sound_table(data: bytes, _ctx: Context, _row: dict) -> Reading:
    """CEffect::LoadSFXFile's lines; whatever follows the last effect it reads stays unclaimed."""
    reader = "tools/game_tables_decode.py:parse_sfx"
    try:
        table = gtd.parse_sfx(data)
    except (ValueError, struct.error) as error:
        return refused(data, "table", reader, error)
    reading = Reading(Account(len(data)), "stored", reader)
    reading.account.add(0, table["bytesRead"], DECODED, "table")
    reading.facts = {"effects": table["count"]}
    return reading


def read_physics_table(data: bytes, ctx: Context, _row: dict) -> Reading:
    """Every statement and value of the physics script; a value no class reads stays framed, not decoded."""
    reader = "tools/physics_values_decode.py:parse_physics"
    try:
        parsed = physics.parse_physics(data)
    except physics.PhysicsError as error:
        return refused(data, "physics", reader, error)
    reading = Reading(Account(len(data)), "stored", reader)
    account = reading.account
    position = 0
    for statement in parsed["statements"]:
        for value in statement["values"]:
            account.add(position, value["bodyOffset"] - position, DECODED, "physics/framing")
            good = value["status"] == "read"
            account.add(value["bodyOffset"], value["size"], DECODED if good else REFERENCED,
                        "physics/values" if good else "physics/" + value["status"])
            position = value["bodyOffset"] + value["size"]
        account.add(position, statement["end"] - position, DECODED, "physics/framing")
        position = statement["end"]
    account.add(position, parsed["end"] - position, DECODED, "physics/framing")
    account.add(parsed["end"], parsed["trailingBytes"], UNKNOWN, "physics/trailing")
    ctx.physics = parsed
    status = collections.Counter(v["status"] for s in parsed["statements"] for v in s["values"])
    reading.facts = {"statements": len(parsed["statements"]), "values": dict(sorted(status.items()))}
    return reading


# ---------------------------------------------------------------------------------------------------------------- text
def read_text_file(data: bytes, _ctx: Context, row: dict) -> Reading:
    reader = "tools/media_readers.py:walk_text"
    try:
        return from_walk(media.walk_text(data), data, reader)
    except media.FormatError as error:
        return refused(data, row["family"], reader, error)


def read_page(data: bytes, ctx: Context, row: dict) -> Reading:
    """A manual page or file list: text, and the local files it names."""
    reading = read_text_file(data, ctx, row)
    ctx.links[row["path"]] = media.html_links(data)
    reading.facts["links"] = len(ctx.links[row["path"]])
    return reading


TEXT_SHAPE_RE = re.compile(rb'^\s*(?:|\[.*|".*"\s*|;.*)$')
STF_LINE_RE = re.compile(rb"^\s*(?:|#define\s+\S+\s+-?\d+|//.*)\s*$")


def read_line_grammar(pattern, part: str):
    """A line-oriented text file, every line of which must have a known shape."""
    def read(data: bytes, ctx: Context, row: dict) -> Reading:
        reading = read_text_file(data, ctx, row)
        if reading.problems or not data:
            return reading
        lines = data.replace(b"\r\n", b"\n").split(b"\n")
        strange = sum(1 for line in lines if not pattern.match(line))
        if strange:
            reading = whole_file(data, REFERENCED, part, reading.reader)
            reading.problems.append(f"{strange} lines of no known shape")
        reading.facts["lines"] = len(lines)
        return reading
    return read


def read_particle_set(data: bytes, ctx: Context, row: dict) -> Reading:
    """CTokenArchive's file: the signature, then one token per line; every token must be one the archive knows."""
    reader = "tools/content_inventory.py:read_particle_set"
    if not data.startswith(PARTICLE_HEADER):
        return refused(data, "particle-set", reader, ValueError("no particle file signature"))
    lines = data.decode("latin-1").splitlines()
    tokens = collections.Counter(line.split(" ", 1)[0] for line in lines[1:] if line.strip())
    strange = sum(count for token, count in tokens.items() if token not in PARTICLE_TOKENS)
    declared = next((line.split()[1] for line in lines if line.startswith("Num_Particle_Descriptors")), None)
    if strange or declared is None or int(declared) != tokens["Particle_Descriptor_Type"]:
        return refused(data, "particle-set", reader, ValueError(
            f"{strange} unknown tokens or a descriptor count that does not close"))
    reading = whole_file(data, DECODED, "particle-set", reader)
    reading.facts = {"lines": len(lines), "descriptors": tokens["Particle_Descriptor_Type"], "tokensSeen": len(tokens)}
    return reading


def read_mission_script(data: bytes, ctx: Context, row: dict) -> Reading:
    """A mission script: compiled by tools/msl_compile.py and compared with the shipped script of its name.

    A script no level ships is decoded if it compiles on its own; onsldef.msl and textlist.h are text.
    """
    reader = "tools/msl_compile.py + tools/msl_gate.py"
    verdicts = ctx.msl.get(row["path"].casefold())
    if verdicts is None:
        reading = read_text_file(data, ctx, row)
        reading.facts["compiled"] = "no verdict"
        if not row["path"].casefold().endswith(".msl") or not data:
            return reading
        read_include = mc.includes_from(ctx.game)

        def tolerant(path: str) -> str:
            try:
                return read_include(path)
            except mc.MissingInclude:
                return ""

        try:
            mc.compile_script(PurePosixPath(row["path"]).stem, data.decode("latin-1"), tolerant)
        except mc.CompileError as error:
            reading = whole_file(data, REFERENCED, "msl/not-compiled", reader)
            reading.facts = {"compiled": "does not compile alone: " + str(error)[:60]}
            return reading
        reading.facts["compiled"] = "compiles alone"
        return reading
    if any(status in MSL_COMPILED for status in verdicts):
        reading = whole_file(data, DECODED, "msl/compiled", reader)
    else:
        reading = whole_file(data, REFERENCED, "msl/not-compiled", reader)
        reading.problems.append("no compiled copy reproduces a shipped script")
    reading.facts = {"verdicts": dict(sorted(collections.Counter(verdicts).items()))}
    return reading


def read_install_log(data: bytes, ctx: Context, row: dict) -> Reading:
    """The installer's log: text, and the install-relative files it lists, for the check against the folder."""
    reading = read_text_file(data, ctx, row)
    names = re.findall(r"(?m)^[A-Za-z]:\\(.+?)=", data.decode("latin-1"))
    roots = {name[:-len("bea.exe")] for name in (n.casefold() for n in names) if name.endswith("\\bea.exe")}
    if len(roots) != 1:
        reading.problems.append("the log does not name one install folder")
        return reading
    root = next(iter(roots))
    below = [name[len(root):].replace("\\", "/") for name in names if name.casefold().startswith(root)]
    folders = {parent for name in below for parent in map(str, PurePosixPath(name).parents)}
    ctx.install_manifest = sorted(name for name in below if name not in folders)
    reading.facts["listed"] = len(ctx.install_manifest)
    return reading


def read_install_state(data: bytes, ctx: Context, row: dict) -> Reading:
    if row["path"].casefold() == "install.log":
        return read_install_log(data, ctx, row)
    if row["path"].casefold().endswith(".bea"):
        return read_career_file(data, ctx, row)
    return read_text_file(data, ctx, row)


def read_career_file(data: bytes, _ctx: Context, _row: dict) -> Reading:
    """A save or options file: its options block and tail; CCareer::Load's career block is read by the Companion."""
    reader = "tools/options_entries_decode.py:parse_options_entries"
    try:
        _entries, count, _scheme, _language = options.parse_options_entries(data)
        tail = options.OPTIONS_START + options.ENTRY_SIZE * count
        options.parse_options_tail(data, tail)
    except (ValueError, struct.error) as error:
        return refused(data, "career-file", reader, error)
    reading = Reading(Account(len(data)), "stored", reader)
    reading.account.add(0, options.OPTIONS_START, REFERENCED, "career/career-block")
    reading.account.add(options.OPTIONS_START, tail - options.OPTIONS_START, DECODED, "career/options-entries")
    reading.account.add(tail, options.TAIL_SIZE, DECODED, "career/options-tail")
    reading.facts = {"optionEntries": count}
    return reading


def read_manual_file(data: bytes, ctx: Context, row: dict) -> Reading:
    suffix = PurePosixPath(row["path"]).suffix.casefold()
    if suffix == ".png":
        return read_png(data, ctx, row)
    if suffix == ".jpg":
        return read_jpeg(data, ctx, row)
    if suffix == ".mso":
        return read_active_mime(data, ctx, row)
    return read_page(data, ctx, row)


READERS = {
    "lvlr-resource-archive": read_archive,
    "cmsh-mesh": read_mesh_file,
    "dds-texture-dxtn": read_texture_file,
    "dds-texture-uncompressed": read_texture_file,
    "xap-sample-bank": read_sample_bank,
    "ogg-music": read_with_decoder(media.walk_ogg, "ogg", "tools/media_readers.py:walk_ogg"),
    "ogg-voice": read_with_decoder(media.walk_ogg, "ogg", "tools/media_readers.py:walk_ogg"),
    "bink-video": read_with_decoder(media.walk_bink, "bink", "tools/media_readers.py:walk_bink"),
    "language-dat": read_language_table,
    "sfx-catalog": read_sound_table,
    "battle-engine-config-dat": read_exact_table(gtd.parse_battle_engine_configurations,
                                                 "tools/game_tables_decode.py:parse_battle_engine_configurations"),
    "world-headers-dat": read_exact_table(worldheaders_decode.parse_worldheaders,
                                          "tools/worldheaders_decode.py:parse_worldheaders"),
    "default-physics-dat": read_physics_table,
    "particle-set-par": read_particle_set,
    "mission-script-msl": read_mission_script,
    "mission-text-txt": read_line_grammar(TEXT_SHAPE_RE, "mission-text"),
    "stf-text-table": read_line_grammar(STF_LINE_RE, "stf"),
    "splash-tga": read_tga,
    "dial-raw": read_byte_sprite,
    "manual": read_manual_file,
    "executable-code": read_pe,
    "install-metadata": read_install_state,
    "save-game": read_career_file,
}


SNIFF_EXPECTED = {
    "lvlr-resource-archive": ("aya",), "cmsh-mesh": ("aya",), "dds-texture-dxtn": ("aya",),
    "dds-texture-uncompressed": ("aya",), "xap-sample-bank": ("xap",), "ogg-music": ("ogg",), "ogg-voice": ("ogg",),
    "bink-video": ("bink",), "splash-tga": ("tga",), "executable-code": ("pe",),
    "manual": ("png", "jpeg", "active-mime", "text"), "save-game": ("binary",),
    "install-metadata": ("text", "binary"), "language-dat": ("binary",), "default-physics-dat": ("binary",),
    "battle-engine-config-dat": ("binary",), "world-headers-dat": ("binary",), "dial-raw": ("binary",),
    "particle-set-par": ("text",), "mission-script-msl": ("text",), "mission-text-txt": ("text", "empty"),
    "stf-text-table": ("text", "empty"), "sfx-catalog": ("text",),
}


def sniff(data: bytes) -> str:
    """What a file's own bytes say it is, whatever its path says."""
    if not data:
        return "empty"
    for magic, name in ((b"OggS", "ogg"), (b"BIK", "bink"), (b"PCXP", "xap"), (b"\x89PNG", "png"), (b"\xff\xd8\xff", "jpeg"),
                        (b"MZ", "pe"), (b"ActiveMime", "active-mime")):
        if data.startswith(magic):
            return name
    if data[-18:] == media.TGA_FOOTER:
        return "tga"
    if len(data) > 6 and data[4] == 0x78 and struct.unpack_from("<I", data, 0)[0] <= len(data) - 4:
        return "aya"
    return "binary" if any(value < 9 for value in data[:4096]) else "text"


def sniff_agrees(family: str, sniffed: str) -> bool:
    return sniffed in SNIFF_EXPECTED.get(family, ())


def read_file(game: Path, row: dict, ctx: Context) -> tuple[dict, list[dict]]:
    """One file's account and the assets its reader found. A reader that cannot run leaves the file unknown."""
    data = cc.read_install_file(game / row["path"])
    reader = READERS.get(row["family"])
    problems: list[str] = []
    if reader is None:
        reading = whole_file(data, UNKNOWN, row["family"], "none")
    else:
        try:
            reading = reader(data, ctx, row)
        except (ValueError, struct.error, zlib.error) as error:
            reading = whole_file(data, UNKNOWN, row["family"], "refused")
            problems.append(f"{type(error).__name__}: {error}")
    closed = reading.account.close()
    account = {"schema": FILE_SCHEMA, "path": row["path"], "family": row["family"], "storedBytes": len(data),
               "sha256": cc.sha256(data), "sniff": sniff(data), "stream": reading.stream,
               "logicalBytes": reading.account.size,
               "class": file_class(reading.account.size, closed["totals"]), "bytes": closed["totals"],
               "parts": closed["parts"], "unknownSpans": closed["unknownSpans"],
               "referencedSpans": [list(span) for span in reading.account.spans_of(REFERENCED)], "reader": reading.reader,
               "problems": problems + reading.problems, "facts": reading.facts}
    return account, [{**item, "file": row["path"]} for item in reading.items]


# ------------------------------------------------------------------------------------- independent decoding and scripts
def decode_media(path: Path, decoder: str) -> dict:
    """Decode every stream of one file with an independent decoder, strict about errors.

    The decoder writes one line per decoded frame (its stream, size and checksum), never a byte of the media; the file's
    result is each stream's frame and byte count, and a hash of those lines as the decoded output's identity.
    """
    command = [decoder, "-nostdin", "-hide_banner", "-v", "error", "-err_detect", "explode", "-xerror", "-i", str(path),
               "-map", "0", "-f", "framecrc", "-"]
    environment = {key: value for key, value in os.environ.items() if key not in ("DISPLAY", "WAYLAND_DISPLAY")}
    try:
        run = subprocess.run(command, capture_output=True, timeout=MEDIA_TIMEOUT, env=environment, check=False)
    except (OSError, subprocess.SubprocessError) as error:
        return {"clean": False, "streams": {}, "sha256": None, "error": type(error).__name__}
    streams: dict[str, dict] = {}
    for line in run.stdout.splitlines():
        if line.startswith(b"#"):
            continue
        fields = [field.strip() for field in line.split(b",")]
        stream = streams.setdefault(fields[0].decode("ascii"), {"frames": 0, "bytes": 0})
        stream["frames"] += 1
        stream["bytes"] += int(fields[4])
    return {"clean": run.returncode == 0 and not run.stderr, "streams": streams,
            "sha256": hashlib.sha256(run.stdout).hexdigest(), "error": None}


def decode_all_media(game: Path, files: list[dict], decoder: str, jobs: int) -> dict:
    wanted = [row["path"] for row in files if row["family"] in MEDIA_FAMILIES
              or (row["family"] == "manual" and row["path"].casefold().endswith(".jpg"))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        return dict(zip(wanted, pool.map(lambda rel: decode_media(game / rel, decoder), wanted)))


def judge_mission_scripts(game: Path) -> dict[str, list[str]]:
    """Per .msl file (folded path): tools/msl_gate.py's verdict on each shipped script compiled from it."""
    verdicts: dict[str, list[str]] = collections.defaultdict(list)
    read_include = mc.includes_from(game)
    for _level, _tag, folder, record in msl_gate.scripts_of(game):
        status, _detail, compiled = msl_gate.judge_record(game, read_include, folder, record)
        key = (folder, record["name"])
        if status == "different" and key in msl_gate.STALE_SOURCES and compiled is not None:
            if msl_gate.stale_identity(record, compiled) == msl_gate.STALE_SOURCES[key][1]:
                status = "stale source"
        verdicts[f"data/missionscripts/level{folder:03d}/{record['name']}.msl".casefold()].append(status)
    return verdicts


# ---------------------------------------------------------------------------------------------------------------- use
def relationship_index(catalog: dict) -> dict[str, set[str]]:
    """Per record id: the record types and relationships that name it, from statuses that name their target."""
    incoming: dict[str, set[str]] = collections.defaultdict(set)
    for asset in catalog["assets"]:
        for relation in asset["relationships"]:
            if relation["type"] == "named-by-code":
                incoming[asset["id"]].add("code:named-by-code")
            if relation["status"] not in NAMING_STATUSES:
                continue
            for target in cc.relationship_ids(relation):
                if target != asset["id"]:
                    incoming[target].add(f"{asset['type']}:{relation['type']}")
    return incoming


# Loader rules that name a file without any record doing so: (lower-cased path pattern, evidence, source function).
LOADER_RULES = (
    (re.compile(r"data/sounds/sounds\.sfx$"), "loader:CEffect::LoadSFXFile"),
    (re.compile(r"data/default physics\.dat$"), "loader:UPhysicsManager::Reload"),
    (re.compile(r"data/battle engine configurations\.dat$"), "loader:UBattleEngineDataManager::Load"),
    (re.compile(r"data/worldheaders\.dat$"), "loader:CWorld::LoadHeader"),
    (re.compile(r"data/language/[a-z]+\.dat$"), "loader:CText::Init"),
    (re.compile(r"data/sounds/sounds_[a-z]+_pc\.xap$"), "loader:CPCSoundManager::LoadSampleBank"),
    (re.compile(r"data/music/[^/]+\.ogg$"), "loader:CPCMusic playlist"),
    (re.compile(r"data/resources/base_res_pc\.aya$"), "loader:CSystem::Init"),
    (re.compile(r"data/resources/frontend_res_pc\.aya$"), "loader:front end"),
    (re.compile(r"data/dial\.raw$"), "loader:CByteSprite::Load"),
    (re.compile(r"data/video/cutscenes/33\.vid$"), "loader:goodie 232 (MakeCutsceneName; it has no archive or record)"),
)
# Families whose file stems game code passes as literal names; the scan needs the selected --decomp source.
LITERAL_FAMILIES = ("bink-video", "particle-set-par", "splash-tga")


def code_words(decomp: Path | None) -> frozenset[str]:
    """The folded words of every string literal in the selected source, to test a file's stem against."""
    if decomp is None:
        return frozenset()
    words: set[str] = set()
    for path in sorted((decomp / "src").rglob("*")):
        if path.suffix.casefold() in (".cpp", ".h") and path.is_file():
            text = cc.read_install_file(path).decode("latin-1")
            for literal in re.findall(r'"((?:[^"\\\n]|\\.)*)"', text):
                words.update(re.split(r"[\\/.\s%]+", literal.casefold()))
    return frozenset(words)


def file_use(catalog: dict, incoming: dict[str, set[str]], ctx: Context, words: frozenset[str] = frozenset()) -> dict[str, set[str]]:
    """Per file (folded path): what names something the file holds. A record naming another record in its own file does
    not count, except that a level is a logical record whose own row points at the archive it names."""
    used: dict[str, set[str]] = collections.defaultdict(set)
    assets = catalog["assets"]
    by_id = {asset["id"]: asset for asset in assets}
    for asset in assets:
        source = asset["source"]["container"].casefold()
        for relation in asset["relationships"]:
            if relation["status"] not in NAMING_STATUSES:
                continue
            for target in cc.relationship_ids(relation):
                hit = by_id.get(target)
                if hit is None:
                    continue
                container = hit["source"]["container"].casefold()
                if container != source or asset["type"] == "level":
                    used[container].add(f"{asset['type']}:{relation['type']}")
        if (asset.get("audio") or {}).get("textId") is not None:
            used[source].add("text-table:voice-name")
        if asset["type"] == "goodie" and asset["goodie"]["goodieType"] in ("image", "mesh"):
            used[source].add("goodie:gallery")
    for row in catalog["files"]:
        lowered = row["path"].casefold()
        for pattern, evidence in LOADER_RULES:
            if pattern.search(lowered):
                used[lowered].add(evidence)
        if row["family"] in LITERAL_FAMILIES and PurePosixPath(lowered).stem in words:
            used[lowered].add("code:string-literal")
    for name, _role in physics_names_of(ctx, physics.MESH):
        used["data/resources/meshes/" + meshcensus._loose_mesh_key(name)].add("physics:mesh")
    folders = {row["path"].casefold() for row in catalog["files"]}
    for page, links in ctx.links.items():
        base = PurePosixPath(page).parent
        for link in links:
            target = os.path.normpath(str(base / link)).replace("\\", "/").casefold()
            if target in folders:
                used[target].add("page:link")
    return used


def physics_names_of(ctx: Context, role: str) -> list[tuple[str, str]]:
    """(name, value field) of every physics value that names something of a role."""
    if ctx.physics is None:
        return []
    return [(name, value["field"]) for statement in ctx.physics["statements"] for value in statement["values"]
            if value["status"] == "read"
            for got, name in physics.named_references(statement["kind"], value["id"], value["args"]) if got == role]


def join_physics(catalog: dict, ctx: Context, incoming: dict[str, set[str]]) -> dict:
    """The physics values' names joined to what they name: the particle effects, sound effects and HUD icons.

    A join is the game's own lookup key (exact for a particle descriptor, stricmp for an effect, hud\\\\<icon>.tga for an
    icon); a name that finds nothing is counted, not guessed at.
    """
    assets = catalog["assets"]
    particles = {asset["name"]: asset["id"] for asset in assets if asset["type"] == "effect"}
    sounds: dict[bytes, list[str]] = collections.defaultdict(list)
    for asset in assets:
        if asset["type"] == "sound-effect":
            sounds[gtd.stricmp_key(asset["name"])].append(asset["id"])
    icons: dict[str, list[str]] = collections.defaultdict(list)
    for asset in assets:
        if asset["type"] == "texture-descriptor":
            icons[cc.fold(asset["name"])].append(asset["id"])
    outcome: collections.Counter = collections.Counter()
    unresolved: dict[str, list[str]] = collections.defaultdict(list)

    def join(role: str, name: str, field: str, targets: list[str]) -> None:
        outcome[f"{role}:{'resolved' if targets else 'unresolved'}"] += 1
        for target in targets:
            incoming[target].add(f"physics:{field}")
        if not targets and name not in unresolved[role]:
            unresolved[role].append(name)

    for name, field in physics_names_of(ctx, physics.PARTICLE):
        join(physics.PARTICLE, name, field, [particles[name]] if name in particles else [])
    for name, field in physics_names_of(ctx, physics.SOUND):
        join(physics.SOUND, name, field, sounds.get(gtd.stricmp_key(name), []))
    for name, field in physics_names_of(ctx, physics.ICON):
        join(physics.ICON, name, field, icons.get(cc.fold(f"hud\\{name}.tga"), []))
    return {"joins": dict(sorted(outcome.items())), "unresolvedNames": {role: sorted(names) for role, names
                                                                        in sorted(unresolved.items())}}


# -------------------------------------------------------------------------------------------------------------- items
KIND_OF_RECORD = {"mesh": "model", "texture": "texture", "texture-descriptor": "texture", "animation": "animation",
                  "audio": "sound", "video": "film", "text-table": "text", "text-symbols": "text",
                  "mission-text": "text", "script": "text"}


def record_form(asset: dict) -> str:
    kind = asset["type"]
    if kind == "mesh":
        return "embedded-mesh" if asset["mesh"].get("embedded") else "loose-mesh"
    if kind == "texture":
        return "dds-file"
    if kind == "texture-descriptor":
        vias = {o.get("via", "TEXT") for o in asset["textureDescriptor"].get("occurrences", [])}
        return "descriptor-" + "+".join(sorted(v.lower() for v in vias))
    if kind == "audio":
        return {"sound-effect": "bank-sample", "music": "music", "voice": "voice"}[asset["audio"]["role"]]
    return kind


def record_status(asset: dict, whole_file_record: bool, file_class_of: dict[str, str]) -> str:
    """A whole file stands or falls with its account; a record inside one with its own parser's status."""
    container = file_class_of.get(asset["source"]["container"].casefold(), UNKNOWN)
    if whole_file_record:
        return container
    if cc.asset_report_status(asset) in ("parsed", "valid", "not-recorded") and container != UNKNOWN:
        return DECODED
    return REFERENCED


def catalogue_items(catalog: dict, incoming: dict[str, set[str]], file_rows: dict[str, dict]) -> list[dict]:
    """One row per model, texture, animation, sound, film and text record of the catalogue."""
    rows = []
    file_class_of = {path: row["class"] for path, row in file_rows.items()}
    owner_used: dict[str, bool] = {}
    for asset in catalog["assets"]:
        kind = KIND_OF_RECORD.get(asset["type"])
        if kind is None:
            continue
        container = asset["source"]["container"].casefold()
        names = sorted(incoming.get(asset["id"], ()))
        whole_file_record = asset["type"] in ("texture", "video", "text-table", "text-symbols", "mission-text", "script") \
            or asset["source"]["envelope"] == "ogg" or (asset["type"] == "mesh" and not asset["mesh"].get("embedded"))
        loaded = sorted({r["type"] for r in asset["relationships"] if r["type"] == "loaded-by-archive"
                         and file_rows.get(r["target"].split(":", 1)[1], {}).get("used")})
        owner = []
        if asset["type"] == "animation":
            names = [n for n in names if n != "mesh:has-animation"]
            owner = [asset["animation"]["skeleton"]["mesh"]]
        evidence = sorted(set(names) | set(loaded))
        if whole_file_record:
            evidence = sorted(set(evidence) | set(file_rows.get(container, {}).get("usedBy", ())))
        row = {"schema": ITEM_SCHEMA, "id": asset["id"], "kind": kind, "form": record_form(asset), "name": asset["name"],
               "file": asset["source"]["container"], "offset": asset["source"]["offset"],
               "length": asset["source"]["length"], "sha256": asset["sha256"],
               "status": record_status(asset, whole_file_record, file_class_of), "used": bool(evidence),
               "usedBy": evidence}
        if asset["type"] in ("mesh", "texture-descriptor"):
            row["loadedByArchive"] = bool(loaded)
        if owner:
            row["owner"] = owner[0]
        owner_used[asset["id"]] = row["used"]
        rows.append(row)
    for row in rows:
        if row["kind"] == "animation":
            row["used"] = bool(row["usedBy"]) or owner_used.get(row.get("owner"), False)
            if row["used"] and not row["usedBy"]:
                row["usedBy"] = ["owner-mesh"]
    return rows


def reader_items(found: list[dict], file_rows: dict[str, dict], known: list[dict]) -> list[dict]:
    """The assets the readers found that no catalogue record lists. One with an owner is used when its owner is; any
    other stands or falls with its file."""
    owners = {item["id"]: item for item in known}
    rows = []
    for number, item in enumerate(found):
        row = file_rows[item["file"].casefold()]
        owner = owners.get(item.get("owner"))
        used, used_by = (owner["used"], ["owner-mesh"] if owner["used"] else []) if owner else (row["used"], row["usedBy"])
        rows.append({"schema": ITEM_SCHEMA, **item, "id": item.get("id") or f"{item['form']}:{item['file'].casefold()}#{number}",
                     "used": used, "usedBy": used_by})
    return rows


# ----------------------------------------------------------------------------------------------------------- coverage
def item_summary(items: list[dict]) -> dict:
    summary: dict[str, dict] = {}
    for item in items:
        kind = summary.setdefault(item["kind"], {"items": 0, "used": 0, "unused": 0, "forms": {}})
        form = kind["forms"].setdefault(item["form"], {"items": 0, "used": 0, "unused": 0})
        for bucket in (kind, form):
            bucket["items"] += 1
            bucket["used" if item["used"] else "unused"] += 1
            statuses = bucket.setdefault("status", {})
            statuses[item["status"]] = statuses.get(item["status"], 0) + 1
            if item.get("loadedByArchive") is False:
                bucket["namedButNotLoadedByAnArchive"] = bucket.get("namedButNotLoadedByAnArchive", 0) + 1
    return dict(sorted(summary.items()))


def named_but_absent(catalog: dict) -> dict:
    """Relationships whose target the install does not hold, by relationship type and status."""
    counts: collections.Counter = collections.Counter()
    for asset in catalog["assets"]:
        for relation in asset["relationships"]:
            if relation["status"].startswith("unresolved"):
                counts[f"{asset['type']}:{relation['type']}"] += 1
    return dict(sorted(counts.items()))


def install_manifest_check(ctx: Context, rows: list[dict]) -> dict:
    """The installer's own list against the folder, as an independent count of what should be there."""
    if ctx.install_manifest is None:
        return {"status": "no install log"}
    present = {row["path"].casefold(): row["path"] for row in rows}
    listed = {name.casefold(): name for name in ctx.install_manifest}
    return {"status": "compared", "listed": len(listed), "present": len(present),
            "listedButAbsent": sorted(listed[name] for name in set(listed) - set(present)),
            "presentButNotListed": sorted(present[name] for name in set(present) - set(listed))}


def build_coverage(rows: list[dict], install_files: int, install_bytes: int, *, items: list[dict] | None = None,
                   proofs: dict | None = None, manifest: dict | None = None, physics_joins: dict | None = None,
                   absent: dict | None = None, decoder: str | None = None) -> dict:
    families: dict[str, dict] = {}
    for row in rows:
        fam = families.setdefault(row["family"], {
            "family": row["family"], "content": row["family"] not in NOT_CONTENT_FAMILIES, "files": 0, "storedBytes": 0,
            "logicalBytes": 0, "filesByClass": {klass: 0 for klass in FILE_CLASSES},
            "storedBytesByClass": {klass: 0 for klass in FILE_CLASSES},
            "logicalBytesByClass": {klass: 0 for klass in BYTE_CLASSES}, "usedFiles": 0, "usedStoredBytes": 0})
        fam["files"] += 1
        fam["storedBytes"] += row["storedBytes"]
        fam["logicalBytes"] += row["logicalBytes"]
        fam["filesByClass"][row["class"]] += 1
        fam["storedBytesByClass"][row["class"]] += row["storedBytes"]
        for klass in BYTE_CLASSES:
            fam["logicalBytesByClass"][klass] += row["bytes"][klass]
        if row["used"]:
            fam["usedFiles"] += 1
            fam["usedStoredBytes"] += row["storedBytes"]
    table = [families[name] for name in sorted(families)]
    stored = sum(f["storedBytes"] for f in table)
    if stored != install_bytes or sum(f["files"] for f in table) != install_files:
        raise AccountError("the walked files do not sum to the install")

    def total(key: str, klass: str, content: bool | None) -> int:
        return sum(f[key][klass] for f in table if content is None or f["content"] is content)

    parts: collections.Counter = collections.Counter()
    for row in rows:
        for part in row["parts"]:
            if part["class"] != DECODED:
                parts[(part["class"], row["family"], part["part"])] += part["bytes"]
    return {"schema": COVERAGE_SCHEMA, GENERATED_MARKER: True, "installFiles": install_files,
            "installBytes": install_bytes, "logicalBytes": sum(f["logicalBytes"] for f in table),
            "filesByClass": {klass: sum(f["filesByClass"][klass] for f in table) for klass in FILE_CLASSES},
            "logicalBytesByClass": {klass: total("logicalBytesByClass", klass, None) for klass in BYTE_CLASSES},
            "unknownLogicalBytes": {"content": total("logicalBytesByClass", UNKNOWN, True),
                                    "notContent": total("logicalBytesByClass", UNKNOWN, False),
                                    "all": total("logicalBytesByClass", UNKNOWN, None)},
            "emptyFiles": sum(1 for row in rows if not row["storedBytes"]),
            "sniffDisagreements": sum(1 for row in rows if not sniff_agrees(row["family"], row["sniff"])),
            "problems": sum(len(row["problems"]) for row in rows),
            "filesWithProblems": sum(1 for row in rows if row["problems"]),
            "families": table,
            "notDecodedParts": [{"class": klass, "family": family, "part": part, "bytes": count}
                                for (klass, family, part), count in sorted(parts.items(), key=lambda kv: -kv[1])],
            "items": item_summary(items or []),
            "proofs": dict(sorted((proofs or {}).items())),
            "mediaDecoder": decoder or "not run: Vorbis, Bink and JPEG payloads stay referenced",
            "installManifest": manifest or {"status": "not compared"},
            "physicsJoins": physics_joins or {},
            "namedButAbsent": absent or {},
            "rules": {
                DECODED: "a reader consumed these bytes in the loader's order and its walk closed exactly, or a codec "
                         "payload every bit pattern of which decodes, or one an independent decoder read with no error "
                         "and agreed with; a decoded byte is owned by a reader, which does not claim every field's "
                         "meaning or any runtime behaviour",
                REFERENCED: "a record or reader establishes what these bytes are and how long they are, but nothing "
                            "has read their contents",
                UNKNOWN: "neither; a gap in a walk falls here by construction",
                "used": "a catalogue record, physics value, page link or loader rule names the file or asset; not a "
                        "runtime observation",
                "logicalBytes": "an AYA envelope's inflated stream, or the plain file itself"}}


def media_proofs(ctx: Context, rows: list[dict]) -> None:
    for row in rows:
        facts = row["facts"]
        if row["family"] in ("ogg-music", "ogg-voice") and "pages" in facts:
            ctx.proofs["oggFilesWalked"] += 1
            ctx.proofs["oggPagesChecksummed"] += facts["pages"]
            ctx.proofs["oggPacketsFramed"] += facts["packets"]
        elif row["family"] == "bink-video" and "frames" in facts:
            ctx.proofs["binkFilesWalked"] += 1
            ctx.proofs["binkFramesWalked"] += facts["frames"]
        if facts.get("decoder") == "agrees":
            ctx.proofs["mediaFilesDecoderAgrees"] += 1
        elif facts.get("decoder") == "disagrees":
            ctx.proofs["mediaFilesDecoderDisagrees"] += 1
        elif facts.get("decoder") == "not run":
            ctx.proofs["mediaFilesDecoderNotRun"] += 1
        if row["family"] == "default-physics-dat" and "values" in facts:
            ctx.proofs["physicsStatements"] = facts["statements"]
            ctx.proofs["physicsValuesRead"] = facts["values"].get("read", 0)
        if row["family"] == "mission-script-msl":
            for status, count in facts.get("verdicts", {}).items():
                ctx.proofs["mslVerdict " + status] += count
            if facts.get("compiled"):
                ctx.proofs["mslNoShippedCopy " + facts["compiled"]] += 1


def build_inventory(game: Path, decomp: Path | None = None, *, decoder: str | None = None, jobs: int = 8) -> dict:
    catalog = cc.build_catalog(game, decomp)
    media_results = decode_all_media(game, catalog["files"], decoder, jobs) if decoder else {}
    ctx = Context(game, media_results=media_results, msl_verdicts=judge_mission_scripts(game))
    rows, found = [], []
    for row in catalog["files"]:
        if row["size"] is None:
            continue
        account, items = read_file(game, row, ctx)
        rows.append(account)
        found.extend(items)
    incoming = relationship_index(catalog)
    joins = join_physics(catalog, ctx, incoming)
    used = file_use(catalog, incoming, ctx, code_words(decomp))
    for account in rows:
        evidence = sorted(used.get(account["path"].casefold(), ()))
        account["used"] = bool(evidence)
        account["usedBy"] = evidence
    file_rows = {row["path"].casefold(): row for row in rows}
    items = catalogue_items(catalog, incoming, file_rows)
    items += reader_items(found, file_rows, items)
    ids = collections.Counter(item["id"] for item in items)
    duplicates = [name for name, count in ids.items() if count > 1]
    if duplicates:
        raise AccountError(f"duplicate item ids: {duplicates[:3]}")
    media_proofs(ctx, rows)
    coverage = build_coverage(rows, catalog["survey"]["files"], catalog["survey"]["bytes"], items=items,
                              proofs=dict(ctx.proofs), manifest=install_manifest_check(ctx, rows),
                              physics_joins=joins, absent=named_but_absent(catalog),
                              decoder=decoder_identity(decoder) if decoder else None)
    return {"files": rows, "items": items, "coverage": coverage, "catalog": catalog}


def decoder_identity(decoder: str) -> str:
    """The decoder's own version line, so a result can be reproduced."""
    try:
        run = subprocess.run([decoder, "-hide_banner", "-version"], capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return Path(decoder).name
    first = run.stdout.splitlines()[0] if run.stdout else ""
    return " ".join(first.split()[:3]) or Path(decoder).name


def write_outputs(out: Path, game: Path, inventory: dict, *, decomp: Path | None = None) -> list[Path]:
    rows, coverage, items = inventory["files"], inventory["coverage"], inventory["items"]
    manifest = {"schema": MANIFEST_SCHEMA, GENERATED_MARKER: True, "schemaVersion": SCHEMA_VERSION,
                "generatedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tool": TOOL, "toolCommit": cc.git_head(),
                "install": {"files": coverage["installFiles"], "bytes": coverage["installBytes"],
                            "pathSizeFingerprint": cc.install_fingerprint(game, inventory["catalog"]["files"])},
                "itemCount": len(items),
                "boundary": "retail-derived metadata including names, sizes and hashes; no retail payload bytes; "
                            "never commit"}
    outputs = {"manifest.json": json.dumps(manifest, indent=2, sort_keys=True) + "\n",
               "coverage.json": json.dumps(coverage, indent=2, sort_keys=True) + "\n",
               "files.jsonl": "".join(json.dumps({**row, GENERATED_MARKER: True}, sort_keys=True) + "\n" for row in rows),
               "items.jsonl": "".join(json.dumps({**row, GENERATED_MARKER: True}, sort_keys=True) + "\n" for row in items)}
    written = []
    protected = [game] + ([decomp] if decomp is not None else [])
    with SecuredOutputRoot(out, protected_sources=protected) as secured:
        for name, text in outputs.items():
            with secured.atomic_text_writer(out / name) as writer:
                writer.write(text)
            written.append(out / name)
    return written


def summary_lines(coverage: dict) -> list[str]:
    """Counts only: one line per family, the assets by kind, then the totals."""
    lines = []
    for fam in coverage["families"]:
        classes = " ".join(f"{klass}={fam['filesByClass'][klass]}" for klass in FILE_CLASSES)
        logical = " ".join(f"{klass}={fam['logicalBytesByClass'][klass]}" for klass in BYTE_CLASSES)
        lines.append(f"{fam['family']}: files={fam['files']} stored={fam['storedBytes']} "
                     f"logical={fam['logicalBytes']} [{classes}] [{logical}] used={fam['usedFiles']}")
    for kind, row in coverage["items"].items():
        lines.append(f"items {kind}: {row['items']} used={row['used']} unused={row['unused']}")
    unknown = coverage["unknownLogicalBytes"]
    lines.append(f"unknown logical bytes: content={unknown['content']} not-content={unknown['notContent']} "
                 f"all={unknown['all']}; problems={coverage['problems']}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"))
    parser.add_argument("--out", type=Path, default=ROOT / "local-data" / "content-inventory")
    parser.add_argument("--decomp", type=Path, help="optional onslaught-decomp checkout, passed to the catalogue")
    parser.add_argument("--media-decoder", default=shutil.which("ffmpeg"),
                        help="an ffmpeg executable for the independent Vorbis, Bink and JPEG decode (default: on PATH)")
    parser.add_argument("--no-media-decoder", action="store_true",
                        help="skip the independent decode: those payloads stay referenced, and the coverage says so")
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 4, help="parallel decoder processes")
    args = parser.parse_args(argv)
    if not args.game:
        parser.error("--game (or BEA_GAME) is required")
    game = Path(os.path.abspath(args.game))
    out = Path(os.path.abspath(args.out))
    decomp = Path(os.path.abspath(args.decomp)) if args.decomp else None
    if not cc.output_is_ignored_local_data(out):
        parser.error("--out must be a git-ignored directory below this checkout's local-data/")
    try:
        validate_disjoint_output_root(out, [game] + ([decomp] if decomp is not None else []))
    except UnsafeGeneratedOutputError as error:
        parser.error(str(error))
    decoder = None if args.no_media_decoder else args.media_decoder
    try:
        inventory = build_inventory(game, decomp, decoder=decoder, jobs=args.jobs)
    except (nt.RegistryLimitError, cc.CatalogInputError, AccountError, wre.EncodeError) as error:
        parser.error(str(error))
    try:
        for path in write_outputs(out, game, inventory, decomp=decomp):
            print(path)
    except UnsafeGeneratedOutputError as error:
        parser.error(str(error))
    for line in summary_lines(inventory["coverage"]):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
