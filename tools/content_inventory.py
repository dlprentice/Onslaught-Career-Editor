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
              --media-decoder). A source no loader reads counts when its grammar holds to its end: a mission script
              when its compile reproduces the shipped copy (or, with none, when it compiles with every include
              present), mission text as [ID] and string entries, a symbol table or header as #define lines, a manual
              page as HTML tokens and a file list as XML. Plain text with no grammar (the install's readme and log)
              counts when every byte is a character of its encoding. A decoded byte means a reader owns it; it does
              not claim that every field has a known meaning, and it says nothing about how the game behaves.
  referenced  a record or reader establishes what these bytes are and how long they are, but nothing has read their
              contents.
  unknown     neither. A gap in a walk falls here by construction, so a reader cannot lose bytes silently.

A file with nothing but decoded bytes is "decoded", with nothing but referenced bytes "referenced", with nothing but
unknown bytes "unknown", and any mix is "partial". An empty file is decoded. Separately from that class, "used" says
that a catalogue record, a physics value, a page link or a loader rule names the file or asset; it is not a runtime
observation.

Bytes are logical: an AYA envelope's inflated stream, and a plain file's own bytes. The stored size of every file is
reported beside them, and the stored sizes sum to the install's size or the run fails. The coverage's headline gives the
content families' decoded share twice: with the independent media decoder and without it.

Beside the byte account, asset-metadata.jsonl holds one row per texture, image, model, animation, sound and film: its
identity (file, wrapping, coordinates, SHA-256), the format, size, mip levels, alpha, channels, sample rate, duration and
frames a reader established (null where none did), and the records that name it: the input list for an offline
processing batch such as an upscale.

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
import particle_set_walk as psw  # noqa: E402
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
NO_AUDIO = 0xFFFFFFFF  # a language entry's audio offset when it names no voice file

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

    def __init__(self, game: Path, *, media_results: dict | None = None, msl_verdicts: dict | None = None,
                 msl_unread: dict[str, str] | None = None):
        self.game = game
        self.lookup: dict | None = None
        self.media = media_results if media_results is not None else {}
        self.msl = msl_verdicts if msl_verdicts is not None else {}
        # The level archives whose worlds the mission-script judge could not read: install path -> reason.
        self.msl_unread = msl_unread if msl_unread is not None else {}
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


DECODER_ONLY = "bytesDecodedOnlyByTheMediaDecoder"


def from_walk(walk: media.Walk, data: bytes, reader: str, *, opaque_decoded: bool = False) -> Reading:
    """A public-format walk as an account: what it read is decoded, and what it framed only if a decoder read it. The
    framed bytes a decoder turned decoded are counted in the facts, so the coverage can say what it is without one."""
    reading = Reading(Account(len(data)), "stored", reader)
    for start, length, kind, part in walk.spans:
        klass = DECODED if kind == media.DECODED or opaque_decoded else REFERENCED
        reading.account.add(start, length, klass, part)
    reading.facts = dict(walk.facts)
    if opaque_decoded:
        reading.facts[DECODER_ONLY] = sum(length for _start, length, kind, _part in walk.spans if kind != media.DECODED)
    return reading


def asset_item(kind: str, form: str, name: str, *, offset: int | None, length: int | None, sha: str, status: str,
               **extra) -> dict:
    return {"kind": kind, "form": form, "name": name, "offset": offset, "length": length, "sha256": sha,
            "status": status, **extra}


# The metadata every asset-metadata row carries (asset_metadata), null where nothing establishes the value.
METADATA_FIELDS = ("format", "width", "height", "mipLevels", "alpha", "channels", "sampleRate", "durationSeconds",
                   "frames")


def media_fields(**values) -> dict:
    unknown = set(values) - set(METADATA_FIELDS)
    if unknown:
        raise ValueError(f"not a metadata field: {sorted(unknown)}")
    return {**dict.fromkeys(METADATA_FIELDS), **values}


def found_metadata(envelope: str, scope: str, *, chunk_path: list[int] | None = None, details: dict | None = None,
                   placed: bool = True, **fields) -> dict:
    """What a reader establishes about an asset no catalogue record lists: how its bytes are wrapped and what its hash
    covers (its identity), its metadata fields and its kind's details. asset_metadata writes it; items.jsonl does not.
    placed is False when the item's offset is not where the hashed bytes start (the identity then gives no offset)."""
    return {"envelope": envelope, "chunkPath": chunk_path or [], "sha256Scope": scope, "fields": media_fields(**fields),
            "details": details or {}, "placed": placed}


# ---------------------------------------------------------------------------------------- archives (LVLR tag streams)
# The prefix every archive opens with, read as reverse-engineering/asset-formats/lvlr-archive.md documents the PC loader
# reading it: LVLR's resource-format version and TARG's target, one u32 each, read and ignored, and AYAD's six guard
# words, the first five compared with the build's own record sizes. A size or value other than the documented PC build's
# leaves the chunk referenced: what it would mean is not established.
PREFIX_VALUES = {"LVLR": (103,), "TARG": (1,), "AYAD": (344, 372, 316, 5084, 92, 1)}
MESH_NAME = 300  # the reference's name buffer; a runtime id, a flag word and a byte follow (tools/goodie_resource_walk.py)
IMPOSTER_LABEL = (4, 68)  # the CIMP bytes the catalogue reads as an imposter's stored label (content_catalog.parse_imposters)
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
        slots = [[slot["name"], slot["nameStatus"], slot["requestedFormat"]] for slot in record["mesh"]["textures"]]
        where = f"{envelope}/chain#{link}"
        reading.items.append(asset_item("model", "chained-mesh", record["name"], offset=None, length=len(stream),
                                        sha=cc.sha256(stream), status=DECODED, id=asset_id, owner=owner, link=link,
                                        parts=record["mesh"]["parts"], textureSlots=slots,
                                        metadata=found_metadata(where, record["sha256Scope"], format="cmsh",
                                                                details=mesh_details(record))))
        for animation in animations:
            fields, details = animation_metadata(animation)
            reading.items.append(asset_item("animation", "chained-animation", animation["name"], offset=None, length=36,
                                            sha=animation["sha256"], status=DECODED, id=animation["id"], owner=owner,
                                            metadata=found_metadata(where, animation["sha256Scope"], details=details,
                                                                    **fields)))


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
    if b"\0" in raw[body:body + MESH_NAME]:
        account.add(body, goodies.MESH_REFERENCE, DECODED, "MESH/reference")
    else:
        account.add(body, goodies.MESH_REFERENCE, REFERENCED, "MESH/reference")
        reading.problems.append("MESH: the reference's name has no terminator")
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


def read_world_chunk(raw: bytes, base: int, size: int, ctx: Context, reading: Reading, level: int | None) -> None:
    """WRES: WRLD holding WDAT and the world bodies, each read by CWorld::LoadWorld's order.

    WDAT's two level numbers (the base world's, then the real world's) count as decoded only when they fit the layout
    CWorld::Deserialize reads (content_catalog.world_layout_parts): the real world is this archive's level, and a named
    base world has its body. Any other layout is a problem, since which worlds the archive supplies is then unknown.
    """
    account = reading.account
    for tag, body, length in chunks_in(raw, base, base + size):
        if tag != "WRLD":
            account.add(body - 8, 8 + length, UNKNOWN, "WRES/" + tag)
            continue
        account.add(body - 8, 8, DECODED, "WRES/framing")
        children = chunks_in(raw, body, body + length)
        wdat = [at for child, at, child_size in children if child == "WDAT" and child_size == 8]
        base_level, real_level = struct.unpack_from("<ii", raw, wdat[0]) if len(wdat) == 1 else (None, None)
        layout = cc.world_layout_parts([child for child, _at, _size in children], base_level, real_level,
                                       real_level if level is None else level)
        if layout:
            reading.problems.append("WRLD: the world layout does not close: " + ", ".join(layout))
        for child, at, child_size in children:
            if child == "WDAT" and child_size == 8 and "WDAT" not in layout:
                account.add(at - 8, 16, DECODED, "WRES/WDAT")
            elif child == "WDAT":
                account.add(at - 8, 8 + child_size, REFERENCED, "WRES/WDAT")
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
                    if child == "CIMP" and inner_size >= IMPOSTER_LABEL[1]:
                        first, last = IMPOSTER_LABEL
                        terminated = b"\0" in raw[inner + first:inner + last]
                        account.add(inner, first, REFERENCED, "IMPS/CIMP-fields")
                        account.add(inner + first, last - first, DECODED if terminated else REFERENCED, "IMPS/label")
                        account.add(inner + last, inner_size - last, REFERENCED, "IMPS/CIMP-fields")
                        if not terminated:
                            reading.problems.append("IMPS: an imposter's stored label has no terminator")
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


def payload_items(tag: str, payload: bytes, decoded: dict, offset: int, chunk_index: int | None = None) -> list[dict]:
    """The assets a level payload holds that no catalogue record lists one by one. Their metadata says only what the
    payload's parser read: no pixel format is established for the terrain mixers or the shadow cells."""
    sha = cc.sha256(payload)
    envelope = f"lvlr-chunk({tag})"
    chunk_path = [] if chunk_index is None else [chunk_index]
    whole = "the chunk's payload"
    if tag == "ERES":
        rows = [asset_item("texture", "terrain-mixer-mip", f"mixer mip {m['mip']}", offset=offset, length=m["textures"]
                           * m["textureBytes"], sha=m["pixelSha256"] or sha, status=DECODED, textures=m["textures"],
                           textureSize=m["size"],
                           metadata=found_metadata(envelope, "the mip's texture bytes" if m["pixelSha256"] else whole,
                                                   chunk_path=chunk_path, placed=False,
                                                   details={"mip": m["mip"], "set": m["set"], "textures": m["textures"],
                                                            "textureBytes": m["textureBytes"],
                                                            "storedSizeField": m["size"]}))
                for m in decoded["mixerMips"]]
        field = decoded["heightField"]
        rows.append(asset_item("model", "terrain-heightfield", "heightfield", offset=offset, length=len(payload), sha=sha,
                               status=DECODED, samples=field["sampleCount"],
                               metadata=found_metadata(envelope, whole, chunk_path=chunk_path, format="heightfield",
                                                       details={"samples": field["sampleCount"], "tiles": field["tiles"],
                                                                "samplesPerTile": field["samplesPerTile"]})))
        return rows
    if tag == "SURF":
        return [asset_item("model", "surface-strips", "surface strips", offset=offset, length=len(payload), sha=sha,
                           status=DECODED, strips=decoded.get("strips"),
                           metadata=found_metadata(envelope, whole, chunk_path=chunk_path, format="surface strips",
                                                   details={"strips": decoded.get("strips"),
                                                            "vertices": decoded.get("vertices")}))]
    if tag == "SSHD":
        return [asset_item("texture", "static-shadow-maps", "static shadows", offset=offset, length=len(payload), sha=sha,
                           status=DECODED, shadows=decoded.get("shadows"), cells=decoded.get("cells"),
                           metadata=found_metadata(envelope, whole, chunk_path=chunk_path,
                                                   details={key: decoded.get(key) for key in
                                                            ("shadows", "partMaps", "shadowedMaps", "cells")}))]
    if tag == "DMKR":
        mips = decoded.get("mips") or []
        texel = all(mip["bytes"] == mip["side"] ** 2 for mip in mips)
        top = max((mip["side"] for mip in mips), default=None)
        return [asset_item("texture", "damage-texture", "landscape damage", offset=offset, length=len(payload), sha=sha,
                           status=DECODED, levels=decoded.get("levels"),
                           metadata=found_metadata(envelope, whole, chunk_path=chunk_path,
                                                   format="one byte per texel" if mips and texel else None,
                                                   width=top, height=top, mipLevels=len(mips),
                                                   channels=1 if mips and texel else None,
                                                   details={"levels": decoded.get("levels")}))]
    return []


def read_prefix(raw: bytes, chunk, reading: Reading) -> None:
    """LVLR, TARG or AYAD: decoded only when it holds exactly the documented PC build's words."""
    expected = PREFIX_VALUES[chunk.tag]
    fits = chunk.size == 4 * len(expected)
    if fits and struct.unpack_from(f"<{len(expected)}I", raw, chunk.offset + 8) == expected:
        reading.account.add(chunk.offset, 8 + chunk.size, DECODED, chunk.tag)
        return
    reading.account.add(chunk.offset, 8 + chunk.size, REFERENCED, chunk.tag)
    reading.problems.append(f"{chunk.tag}: " + ("its values are" if fits else "its size is") + " not the documented PC build's")


def archive_level(path: str) -> int | None:
    """A numbered level archive's level (content_catalog.ARCHIVE_RE); None for the other archives."""
    match = cc.ARCHIVE_RE.match(PurePosixPath(path).name)
    return int(match.group("level")) if match and match.group("level") else None


def read_archive(data: bytes, ctx: Context, row: dict) -> Reading:
    raw, chunks, members, _envelope = aai.decode_archive_envelope(data, "pc-chunked-zlib")
    reading = Reading(Account(len(raw)), "inflated", "tools/aya_archive_inventory.py:decode_archive_envelope")
    account = reading.account
    reading.facts = {"members": members, "chunks": len(chunks)}
    for chunk in chunks:
        base = chunk.offset + 8
        tag = chunk.tag
        if tag in PREFIX_VALUES:
            read_prefix(raw, chunk, reading)
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
            read_world_chunk(raw, base, chunk.size, ctx, reading, archive_level(row["path"]))
        elif tag in PAYLOAD_DECODERS:
            payload = raw[base:base + chunk.size]
            try:
                decoded = PAYLOAD_DECODERS[tag](payload)
            except DECODE_ERRORS as error:
                reading.problems.append(f"{tag}: {error}")
                account.add(chunk.offset, 8 + chunk.size, REFERENCED, tag)
                continue
            account.add(chunk.offset, 8 + chunk.size, DECODED, tag)
            reading.items.extend(payload_items(tag, payload, decoded, base, chunk.index))
        elif tag == "GDIE":
            try:
                goodie = goodies.read_goodie(raw)
            except (goodies.GoodieError, struct.error) as error:
                reading.problems.append(f"GDIE: {error}")
                account.add(chunk.offset, 8 + chunk.size, REFERENCED, tag)
                continue
            names = [texture["terminated"] for texture in goodie["textures"]]
            if goodie["mesh"]:
                names.append(goodie["mesh"]["terminated"])
            if all(names):
                account.add(chunk.offset, 8 + chunk.size, DECODED, tag)
            else:
                account.add(chunk.offset, 8 + chunk.size, REFERENCED, tag)
                reading.problems.append("GDIE: a texture or mesh reference's name has no terminator")
        elif tag in ("IMPS", "PLAT"):
            account.add(chunk.offset, 8, DECODED, tag + "/framing")
            try:
                (read_imposters if tag == "IMPS" else read_platform)(raw, base, chunk.size, reading)
            except (ValueError, struct.error) as error:
                reading.problems.append(f"{tag}: {error}")
        else:
            account.add(chunk.offset, 8 + chunk.size, UNKNOWN, tag)
    for path, reason in ctx.msl_unread.items():
        if path.casefold() == row["path"].casefold():
            reading.problems.append(f"the mission-script judge could not read this archive's worlds ({reason})")
    return reading


# ------------------------------------------------------------------------------------------------------- loose assets
def read_mesh_file(data: bytes, ctx: Context, row: dict) -> Reading:
    stream = aai.inflate_aya_bytes(data)
    reading = Reading(Account(len(stream)), "inflated", "tools/cmsh_grammar_walk.py:walk_stream")
    ok = read_mesh_stream(stream, reading, ctx, "mesh:" + row["path"].casefold(), row["path"], "aya-zlib-members(cmsh)")
    reading.account.add(0, len(stream), DECODED if ok else REFERENCED, "CMSH")
    return reading


def read_texture_file(data: bytes, _ctx: Context, _row: dict) -> Reading:
    """The DDS an AYA envelope inflates to. An envelope the census cannot inflate or will not admit leaves the stored
    bytes unknown: the reader never reached a texture, as with a mesh whose envelope does not inflate."""
    reader = "tools/dds_census.py:texture_metadata"
    meta = dds_census.texture_metadata(data, envelope="aya")
    if meta["dds"] is None:
        reading = whole_file(data, UNKNOWN, "DDS/not-reached", reader)
        reading.problems.extend(meta.get("problems") or [meta["status"]])
        return reading
    size = meta["dds"]["size"]
    reading = Reading(Account(size), "inflated", reader)
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


WHOLE_FILE = "whole file"
JPEG_PROCESSES = {0xC0: "baseline", 0xC1: "extended sequential", 0xC2: "progressive", 0xC3: "lossless"}


def read_png(data: bytes, _ctx: Context, row: dict) -> Reading:
    reader = "tools/media_readers.py:walk_png"
    try:
        reading = from_walk(media.walk_png(data), data, reader)
    except media.FormatError as error:
        return refused(data, "png", reader, error)
    facts = reading.facts
    # An alpha channel (grey or colour with alpha) or a transparency chunk stores alpha; its values are not classified.
    alpha = "present" if facts["colourType"] in (4, 6) or facts["transparencyChunk"] else "none"
    metadata = found_metadata(WHOLE_FILE, WHOLE_FILE, format="png", width=facts["width"], height=facts["height"],
                              alpha=alpha, channels=facts["channels"],
                              details={key: facts[key] for key in ("bitDepth", "colourType", "interlace",
                                                                   "transparencyChunk")})
    reading.items.append(asset_item("image", "png", PurePosixPath(row["path"]).name, offset=0, length=len(data),
                                    sha=cc.sha256(data), status=DECODED, width=facts["width"], height=facts["height"],
                                    metadata=metadata))
    return reading


def read_tga(data: bytes, _ctx: Context, row: dict) -> Reading:
    reader = "tools/media_readers.py:walk_tga"
    try:
        reading = from_walk(media.walk_tga(data), data, reader)
    except media.FormatError as error:
        return refused(data, "tga", reader, error)
    facts = reading.facts
    alpha_bits = facts["descriptor"] & 0x0F  # the image descriptor's low four bits: alpha bits per pixel
    metadata = found_metadata(WHOLE_FILE, WHOLE_FILE, format="tga", width=facts["width"], height=facts["height"],
                              alpha="present" if alpha_bits else "none", channels=4 if alpha_bits else 3,
                              details={"bitsPerPixel": facts["bitsPerPixel"], "alphaBits": alpha_bits,
                                       "firstRowAtTop": bool(facts["descriptor"] & 0x20)})
    reading.items.append(asset_item("image", "tga", PurePosixPath(row["path"]).name, offset=0, length=len(data),
                                    sha=cc.sha256(data), status=DECODED, width=facts["width"], height=facts["height"],
                                    metadata=metadata))
    return reading


def read_jpeg(data: bytes, ctx: Context, row: dict) -> Reading:
    reading = read_with_decoder(media.walk_jpeg, "jpeg", "tools/media_readers.py:walk_jpeg")(data, ctx, row)
    agreed = reading.facts.get("decoder") == "agrees"
    facts = reading.facts
    walked = "components" in facts
    metadata = found_metadata(WHOLE_FILE, WHOLE_FILE, format="jpeg", width=facts.get("width"), height=facts.get("height"),
                              alpha="none" if walked else None, channels=facts.get("components"),
                              details={"precision": facts.get("precision"),
                                       "process": JPEG_PROCESSES.get(facts.get("frameMarker"), "other") if walked else None,
                                       "decoder": facts.get("decoder")})
    reading.items.append(asset_item("image", "jpeg", PurePosixPath(row["path"]).name, offset=0, length=len(data),
                                    sha=cc.sha256(data), status=DECODED if agreed else REFERENCED,
                                    width=facts.get("width"), height=facts.get("height"), metadata=metadata))
    return reading


DIAL_FRAME = 256  # 16 x 16 one-byte indices (rebuild/OnslaughtRebuild.Host/HudView.cs, from CByteSprite's use in DrawThreats)


def read_byte_sprite(data: bytes, _ctx: Context, row: dict) -> Reading:
    """data\\\\Dial.raw: the rebuild reads its first 16 x 16 frame. Nothing has established the frames after it."""
    reading = Reading(Account(len(data)), "stored", "rebuild/OnslaughtRebuild.Host/HudView.cs (frame 0)")
    reading.account.add(0, min(DIAL_FRAME, len(data)), DECODED, "byte-sprite/frame-0")
    reading.account.add(DIAL_FRAME, max(0, len(data) - DIAL_FRAME), REFERENCED, "byte-sprite/further-bytes")
    reading.facts = {"frameBytes": DIAL_FRAME, "wholeFrames": len(data) // DIAL_FRAME}
    # One frame of 16 x 16 one-byte indices is established; the length holds more, which nothing has read as frames.
    metadata = found_metadata(WHOLE_FILE, WHOLE_FILE, format="one-byte indices", width=16, height=16, channels=1,
                              details={"frameBytes": DIAL_FRAME, "framesEstablished": 1,
                                       "wholeFramesByLength": len(data) // DIAL_FRAME})
    reading.items.append(asset_item("image", "byte-sprite", PurePosixPath(row["path"]).name, offset=0, length=len(data),
                                    sha=cc.sha256(data), status=PARTIAL, width=16, height=16, metadata=metadata))
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
            proved = resource["status"] == "decoded"
            bits = resource.get("bitCount")
            # A proved icon image is a bitmap of its stated size; below 32 bits only its 1-bit mask marks transparency.
            metadata = found_metadata(f"pe-resource({resource['type']})", "the resource's data", chunk_path=[number],
                                      format="icon bitmap" if proved else None, width=resource.get("width"),
                                      height=resource.get("height"),
                                      alpha=("present" if bits == 32 else "mask") if proved else None,
                                      details={"bitCount": bits, "resourceStatus": resource["status"]})
            reading.items.append(asset_item("image", "pe-" + resource["type"], f"{row['path']} resource {number}",
                                            offset=resource["offset"], length=resource["length"], sha=cc.sha256(body),
                                            status=DECODED if proved else REFERENCED, metadata=metadata))
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
    reading.problems += claim_strings(account, data, pool, size, [entry.text_off_words * 2 for entry in table.entries],
                                      2, "language/text-pool")
    account.add(pool + size, table.audio_pool_off - pool - size, DECODED, "language/pool-header")
    reading.problems += claim_strings(account, data, table.audio_pool_off, table.audio_pool_size,
                                      [entry.audio_off_bytes for entry in table.entries if entry.audio_off_bytes != NO_AUDIO],
                                      1, "language/audio-pool")
    reading.facts = {"entries": table.count}
    return reading


def claim_strings(account: Account, data: bytes, pool: int, size: int, offsets: list[int], width: int, part: str) -> list[str]:
    """Claim the zero-terminated strings a table's entries reach: a pool byte no entry reaches stays unclaimed, unless
    it is whole strings, which are referenced. Returns the problems: an entry that points outside its pool, and a string
    that runs to the pool's end without its terminator (whose bytes are referenced, not decoded)."""
    terminator = b"\0" * width
    reached = bytearray(size)  # 0 reached by no entry, 1 a terminated string, 2 one that runs to the end
    problems: set[str] = set()
    for at in offsets:
        if not 0 <= at < size or at % width:
            problems.add(f"{part}: an entry points outside its pool")
            continue
        end = at
        while end + width <= size and data[pool + end:pool + end + width] != terminator:
            end += width
        if end + width > size:
            problems.add(f"{part}: a string runs to the end of its pool without a terminator")
            reached[at:size] = b"\2" * (size - at)
        else:
            reached[at:end + width] = bytes(max(1, mark) for mark in reached[at:end + width])
    position = 0
    while position < size:
        on = reached[position]
        end = position
        while end < size and reached[end] == on:
            end += 1
        if on == 1:
            account.add(pool + position, end - position, DECODED, part)
        elif on == 2:
            account.add(pool + position, end - position, REFERENCED, part + " (no terminator)")
        elif data[pool + end - width:pool + end] == terminator and (end - position) % width == 0:
            account.add(pool + position, end - position, REFERENCED, part + " (reached by no entry)")
        position = end
    return sorted(problems)


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


def read_page(data: bytes, ctx: Context, row: dict, walker=media.walk_html) -> Reading:
    """A manual page (tokenized to its end) or a saved page's XML file list (parsed): its text and the local files it
    names. A page or list that does not hold is referenced, with the reason."""
    reader = "tools/media_readers.py:" + walker.__name__
    try:
        reading = from_walk(walker(data), data, reader)
    except media.FormatError as error:
        reading = refused(data, row["family"], reader, error)
    ctx.links[row["path"]] = media.html_links(data)
    reading.facts["links"] = len(ctx.links[row["path"]])
    return reading


# A line-oriented source no loader reads, held to its grammar: every line of a known kind and, for mission text, every
# entry whole. An empty file is decoded, as every empty file is.
DEFINE_LINE_RE = re.compile(rb"[ \t]*(?:#define[ \t]+[A-Za-z_][A-Za-z0-9_]*[ \t]+-?[0-9]+|//.*)?[ \t]*")
TEXT_BLANK_RE = re.compile(rb"[ \t]*(?:;.*)?")
TEXT_ID_RE = re.compile(rb"\[[A-Z0-9_]+\](?:[ \t][^\"]*)?")
TEXT_STRING_RE = re.compile(rb'[ \t]*".*"[ \t]*')


def source_lines(data: bytes) -> list[bytes]:
    """The lines of a text file without their terminators (CRLF or LF)."""
    return data.replace(b"\r\n", b"\n").split(b"\n")


def define_lines_hold(lines: list[bytes]) -> str | None:
    """A header of #define NAME number lines (with blank and // comment lines): None, or what does not hold."""
    strange = sum(1 for line in lines if not DEFINE_LINE_RE.fullmatch(line))
    return f"{strange} lines that are no #define, comment or blank line" if strange else None


def mission_text_holds(lines: list[bytes]) -> str | None:
    """Mission text: entries of an [ID] line (an upper-case text id, then an optional note) and the quoted string on
    the next line, with blank and ; comment lines between entries. None, or what does not hold."""
    position = 0
    while position < len(lines):
        line = lines[position]
        if TEXT_ID_RE.fullmatch(line):
            if position + 1 >= len(lines) or not TEXT_STRING_RE.fullmatch(lines[position + 1]):
                return "an [ID] line without its quoted string on the next line"
            position += 2
        elif TEXT_BLANK_RE.fullmatch(line):
            position += 1
        else:
            return "a line that is no [ID], string, comment or blank line"
    return None


def read_line_grammar(holds, part: str):
    """A line-oriented source no loader reads: decoded when its grammar holds, else referenced with the reason."""
    def read(data: bytes, ctx: Context, row: dict) -> Reading:
        reading = read_text_file(data, ctx, row)
        if reading.problems or not data:
            return reading
        lines = source_lines(data)
        problem = holds(lines)
        reader = reading.reader + " + tools/content_inventory.py:" + holds.__name__
        if problem:
            reading = whole_file(data, REFERENCED, part, reader)
            reading.problems.append(problem)
        reading.reader = reader
        reading.facts["lines"] = len(lines)
        return reading
    return read


def read_particle_set(data: bytes, _ctx: Context, _row: dict) -> Reading:
    """CParticleSet::ReadData's file, value by value (tools/particle_set_walk.py). The words after a direct number,
    which the reader never looks at, are referenced; lines after the last descriptor, which it never reaches, are left
    unclaimed."""
    reader = "tools/particle_set_walk.py:walk"
    try:
        walk = psw.walk(data)
    except psw.ParticleSetError as error:
        return refused(data, "particle-set", reader, error)
    reading = Reading(Account(len(data)), "stored", reader)
    position = 0
    for start, length in walk["skipped"]:
        reading.account.add(position, start - position, DECODED, "particle-set")
        reading.account.add(start, length, REFERENCED, "particle-set/words-the-reader-skips")
        position = start + length
    reading.account.add(position, walk["end"] - position, DECODED, "particle-set")
    reading.facts = {key: walk[key] for key in ("lines", "descriptors", "types", "nameSlots", "slotRebinds", "references",
                                                "linesAfterTheWalk")}
    return reading


# tools/msl_gate.py's verdicts: the two that reproduce the shipped copy, and the one more that it accepts (a known older
# revision of the source). Any other verdict is a failure there and a problem here.
REPRODUCES = frozenset({"exact", "exact, assisted"})
ACCEPTED_VERDICTS = REPRODUCES | {"stale source"}
# Where the judge looks for the source of a shipped script (data\MissionScripts\level<NNN>\<name>.msl, any case).
LEVEL_SOURCE_RE = re.compile(r"data/missionscripts/level-?[0-9]+/[^/]+\.msl")
MSL_UNREAD = "mslArchivesWithoutReadableWorlds"


def read_mission_script(data: bytes, ctx: Context, row: dict) -> Reading:
    """A mission script source, compiled by tools/msl_compile.py. No loader reads a source; the game runs the compiled
    copy its level's world file ships. So a script counts as decoded when its compile reproduces every shipped copy
    compiled from it (tools/msl_gate.py's exact verdict, or exact, assisted: an #include the install lacks read as empty
    and the names it would define taken from the shipped constants), or, when no level ships it, when it compiles with
    every include present. A stale source (it compiles to a known older revision), one that compiles only when a missing
    include is read as empty, and one that does not compile are referenced; a shipped copy it does not reproduce (any
    other verdict, alone or beside an exact one) is also a problem. A header of #define lines (textlist.h) is held to
    that grammar, and onsldef.msl, which the game's C++ includes, to its compile.

    When the judge could not read some level archive's worlds, which scripts that archive ships, and for which level
    folders, is not known: no source in a level folder can then be shown to reproduce every shipped copy, or to be one
    no level ships, so each is referenced with a problem.
    """
    reader = "tools/msl_compile.py + tools/msl_gate.py"
    verdicts = ctx.msl.get(row["path"].casefold())
    if ctx.msl_unread and LEVEL_SOURCE_RE.fullmatch(row["path"].casefold()):
        reading = whole_file(data, REFERENCED, "msl/not-judged", reader)
        reading.problems.append(f"the mission-script judge could not read {len(ctx.msl_unread)} level archives' "
                                "worlds, so which shipped scripts this source compiles to is not known")
        reading.facts = {"notJudged": True}
        return reading
    if verdicts is not None:
        statuses = collections.Counter(verdicts)
        failing = sorted(set(statuses) - ACCEPTED_VERDICTS)
        if failing:
            reading = whole_file(data, REFERENCED, "msl/not-reproduced", reader)
            reading.problems += [f"{statuses[status]} of {len(verdicts)} shipped copies compiled from this source: "
                                 f"{status}" for status in failing]
        elif set(statuses) <= REPRODUCES:
            reading = whole_file(data, DECODED, "msl/compiled", reader)
        else:
            reading = whole_file(data, REFERENCED, "msl/stale-source", reader)
        reading.facts = {"verdicts": dict(sorted(statuses.items()))}
        return reading
    if not row["path"].casefold().endswith(".msl"):
        reading = read_line_grammar(define_lines_hold, "msl/header")(data, ctx, row)
        reading.facts["compiled"] = "a header"
        return reading
    reading = read_text_file(data, ctx, row)
    if reading.problems or not data:
        reading.facts["compiled"] = "no verdict"
        return reading
    read_include = mc.includes_from(ctx.game)
    missing: list[str] = []

    def tolerant(path: str) -> str:
        try:
            return read_include(path)
        except mc.MissingInclude:
            missing.append(path)
            return ""

    name = PurePosixPath(row["path"]).stem
    try:
        mc.compile_script(name, data.decode("latin-1"), tolerant)
    except mc.CompileError as error:
        # The fact's value stays a fixed phrase so it can be counted; the compiler's message goes beside it.
        reading = whole_file(data, REFERENCED, "msl/not-compiled", reader)
        reading.facts = {"compiled": "does not compile alone", "compileError": str(error)[:200]}
        return reading
    if missing:
        reading = whole_file(data, REFERENCED, "msl/compiles-only-without-a-missing-include", reader)
        reading.facts = {"compiled": "compiles only with a missing include read as empty"}
        return reading
    reading.reader = reader
    reading.facts["compiled"] = "compiles alone"
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
    reading = read_page(data, ctx, row, media.walk_xml if suffix == ".xml" else media.walk_html)
    if suffix in (".htm", ".html"):
        # A manual page is a text asset of its own; a saved page's file list is only its support.
        reading.items.append(asset_item("text", "manual-page", PurePosixPath(row["path"]).name, offset=0,
                                        length=len(data), sha=cc.sha256(data),
                                        status=REFERENCED if reading.problems else DECODED))
    return reading


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
    "mission-text-txt": read_line_grammar(mission_text_holds, "mission-text"),
    "stf-text-table": read_line_grammar(define_lines_hold, "stf"),
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
    for magic, name in ((b"OggS", "ogg"), (b"BIK", "bink"), (b"PCXP", "xap"), (media.PNG_SIGNATURE, "png"),
                        (media.JPEG_START, "jpeg"), (b"MZ", "pe"), (media.ACTIVE_MIME_MAGIC, "active-mime")):
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
        if data and not reading.account.size:
            # A logical stream of nothing would drop the file's bytes from the account without a trace.
            problems += reading.problems + ["the reader's stream holds none of the file's bytes"]
            reading = whole_file(data, UNKNOWN, row["family"], reading.reader)
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


def shipped_scripts(game: Path, unread: dict[str, str]):
    """(folder level, record) for each compiled script of each level archive's world bodies, as tools/msl_gate.py's
    scripts_of reads them. An archive whose top-level chunks hold no WRES ships no world, so no script. An archive whose
    worlds this reader (tools/world_resources_encode.py, with its member and size limits) cannot read goes into unread,
    its install path mapped to the reason, instead of stopping the run; read_mission_script then judges no level
    folder's source."""
    for _level, path in wre.level_archives(game).items():
        try:
            raw = b"".join(wre.inflate(wre.read_members(wre.read_retail(path))))
            if not any(tag == "WRES" for tag, _at, _size in wre.chunks(raw)):
                continue
            worlds = wre.level_worlds(raw)
            for tag, body in sorted(worlds["bodies"].items()):
                folder = worlds["realLevel"] if tag == "RLWD" else worlds["baseLevel"]
                for record in wre.read_world_model(body)["scripts"]:
                    yield folder, record
        except (wre.EncodeError, ValueError, struct.error) as error:
            unread[path.relative_to(game).as_posix()] = f"{type(error).__name__}: {error}"


def judge_mission_scripts(game: Path, unread: dict[str, str] | None = None) -> dict[str, list[str]]:
    """Per .msl file (folded path): tools/msl_gate.py's verdict on each shipped script compiled from it. The archives
    whose worlds cannot be read go into unread (shipped_scripts)."""
    verdicts: dict[str, list[str]] = collections.defaultdict(list)
    read_include = mc.includes_from(game)
    for folder, record in shipped_scripts(game, unread if unread is not None else {}):
        status, _detail, compiled = msl_gate.judge_record(game, read_include, folder, record)
        key = (folder, record["name"])
        if status == "different" and key in msl_gate.STALE_SOURCES and compiled is not None:
            try:
                pinned = msl_gate.stale_identity(record, compiled) == msl_gate.STALE_SOURCES[key][1]
            except (wre.EncodeError, ValueError, TypeError, KeyError, OverflowError):
                pinned = False  # as tools/msl_gate.py: an identity that cannot be computed is not the pinned one
            if pinned:
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


def join_chained_textures(found: list[dict], catalog: dict, incoming: dict[str, set[str]],
                          users: dict[str, set[str]] | None = None) -> dict:
    """A chained mesh's texture slots, joined as the catalogue joins its parent's (CMesh::FindTexture: the stricmp name
    and the requested format among loaded texture records with every mip level), within the archives that load the parent
    or, for a parent no archive loads, in any archive. A slot whose name is unreadable or too short joins nothing. Each
    joined texture record gets the chained mesh among its users."""
    by_key: dict[tuple, list[dict]] = collections.defaultdict(list)
    for asset in catalog["assets"]:
        record = asset.get("textureDescriptor") or {}
        if asset["type"] == "texture-descriptor" and record.get("status") == "parsed" and record.get("levels") == -1:
            by_key[(cc.fold(asset["name"]), record["requestedFormat"])].append(asset)
    loading = {asset["id"]: {r["target"].split(":", 1)[1] for r in asset["relationships"]
                             if r["type"] == "loaded-by-archive" and r["target"]}
               for asset in catalog["assets"] if asset["type"] == "mesh"}
    outcome: collections.Counter = collections.Counter()
    for item in found:
        if item["form"] != "chained-mesh":
            continue
        scope = loading.get(item["owner"], set())
        for name, status, requested in item.pop("textureSlots", []):
            if status not in cc.KNOWN_NAME_STATUSES or requested is None:
                outcome["slots without a joinable name"] += 1
                continue
            hits = [d for d in by_key.get((cc.fold(name), requested), [])
                    if not scope or {o["archive"].casefold() for o in d["textureDescriptor"]["occurrences"]} & scope]
            outcome["slots joined" if hits else "slots unresolved"] += 1
            for descriptor in hits:
                incoming[descriptor["id"]].add("chained-mesh:uses-texture")
                if users is not None:
                    users[descriptor["id"]].add(item["id"])
    return dict(sorted(outcome.items()))


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


# Where a catalogue envelope places a record: in an archive's or mesh's inflated stream, or in the stored file.
ENVELOPE_STREAMS = (("lvlr-chunk(", "inflated"), ("aya-zlib-members(", "inflated"), ("xap(", "stored"), ("ogg", "stored"))
PARSER_STATUSES = ("parsed", "valid")


def bytes_class(row: dict, start: int, length: int) -> str:
    """The class of a record's own bytes in its file's account, as file_class gives a file's."""
    end = start + length
    if start < 0 or end > row["logicalBytes"]:
        return UNKNOWN
    referenced = sum(max(0, min(end, b) - max(start, a)) for a, b in row["referencedSpans"])
    unknown = sum(max(0, min(end, b) - max(start, a)) for a, b, _part in row["unknownSpans"])
    return file_class(length, {DECODED: length - referenced - unknown, REFERENCED: referenced, UNKNOWN: unknown})


def record_status(asset: dict, whole_file_record: bool, file_rows: dict[str, dict]) -> str:
    """A whole file stands or falls with its account. A record inside one takes the class of its own bytes in that
    account, and is at best referenced when its own parser refused it. A record the catalogue gives no parser status
    ("not-recorded": an animation) is decided by its bytes alone; a record alone does not establish a reading."""
    row = file_rows.get(asset["source"]["container"].casefold())
    if row is None:
        return UNKNOWN
    if whole_file_record:
        return row["class"]
    source = asset["source"]
    stream = next((kind for prefix, kind in ENVELOPE_STREAMS if source["envelope"].startswith(prefix)), None)
    if stream == row["stream"] and source["offset"] is not None and source["length"]:
        klass = bytes_class(row, source["offset"], source["length"])
    else:
        klass = row["class"]
    status = cc.asset_report_status(asset)
    if status not in PARSER_STATUSES and status != "not-recorded":
        return UNKNOWN if klass == UNKNOWN else REFERENCED
    return klass


def catalogue_items(catalog: dict, incoming: dict[str, set[str]], file_rows: dict[str, dict]) -> list[dict]:
    """One row per model, texture, animation, sound, film and text record of the catalogue."""
    rows = []
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
        if asset["type"] == "texture-descriptor":
            # an imposter atlas and a font texture are used by their system, which names them by role, not by a record
            if any(r["type"] == "imposter-of-mesh" for r in asset["relationships"]):
                names = sorted(set(names) | {"imposter:atlas"})
            if any(o.get("via") == "PLAT" for o in asset["textureDescriptor"].get("occurrences", [])):
                names = sorted(set(names) | {"platform:font"})
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
               "status": record_status(asset, whole_file_record, file_rows), "used": bool(evidence),
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


def reader_items(found: list[dict], file_rows: dict[str, dict], known: list[dict]) -> tuple[list[dict], dict[str, dict]]:
    """The assets the readers found that no catalogue record lists, and their readers' metadata by item id. One with an
    owner is used when its owner is; any other stands or falls with its file."""
    owners = {item["id"]: item for item in known}
    rows, metadata = [], {}
    for number, found_item in enumerate(found):
        item = dict(found_item)
        details = item.pop("metadata", None)
        row = file_rows[item["file"].casefold()]
        owner = owners.get(item.get("owner"))
        used, used_by = (owner["used"], ["owner-mesh"] if owner["used"] else []) if owner else (row["used"], row["usedBy"])
        rows.append({"schema": ITEM_SCHEMA, **item, "id": item.get("id") or f"{item['form']}:{item['file'].casefold()}#{number}",
                     "used": used, "usedBy": used_by})
        if details is not None:
            metadata[rows[-1]["id"]] = details
    return rows, metadata


# ------------------------------------------------------------------------------------------------------ asset metadata
# One row per texture, image, model, animation, sound and film (asset-metadata.jsonl): the asset's identity (its file,
# how its bytes are wrapped there, its coordinates and the SHA-256 of its own bytes), the metadata a reader established
# (format, size, mip levels, alpha, channels, sample rate, duration, frames), what names it, and the catalogue's usage
# summary and upscale notes where the catalogue has them. A field nothing established is null; nothing is inferred
# from a name. It is the input list for an offline processing batch (an AI upscale, for one), not a claim about how the
# game renders or plays the asset.
#
# A DDS file's row gives the format its header says it stores. A texture record's row gives the format the record
# itself names (CDXTexture's format field, which also names its pixel files); the DDS files that hold its pixels
# (details.pixelsFrom) may store another, and their own rows say which. One texture-record row stands for every
# byte-identical copy of the record: details.occurrences counts the copies, and the identity places the first.
METADATA_SCHEMA = "onslaught.content-inventory.asset-metadata.v1"
METADATA_KINDS = ("texture", "image", "model", "animation", "sound", "film")
# The channels a texture format holds, for a DDS file's stored format and a texture record's named one alike. DXT1 is
# colour, though its blocks can also mark a texel transparent (the alpha field says whether any does); X8R8G8B8's fourth
# byte is unused.
FORMAT_CHANNELS = {"A8R8G8B8": 4, "X8R8G8B8": 3, "R5G6B5": 3, "A1R5G5B5": 4, "A4R4G4B4": 4,
                   "DXT1": 3, "DXT2": 4, "DXT3": 4, "DXT4": 4, "DXT5": 4}


def mesh_details(record: dict) -> dict:
    """A catalogue mesh record's structure, and its texture slots by name (CMesh::FindTexture's lookup key)."""
    mesh = record["mesh"]
    return {"meshStatus": mesh["status"], "embedded": mesh.get("embedded"), "parts": mesh["parts"],
            "vertices": mesh["vertices"], "triangles": mesh["triangles"], "skinnedParts": mesh.get("skinnedParts"),
            "boneParts": mesh.get("boneParts"), "lodChildren": mesh.get("lodChildren"),
            "textureSlots": [{key: slot.get(key) for key in ("slot", "name", "nameStatus", "requestedFormat", "frames")}
                             for slot in mesh["textures"]],
            "animations": sorted(r["target"] for r in record["relationships"] if r["type"] == "has-animation")}


def animation_details(record: dict) -> dict:
    """An animation mode's frame range, frame scaler and rate as its record stores them."""
    animation = record["animation"]
    return {"mode": animation["mode"], "startFrame": animation["startFrame"], "lastFrame": animation["lastFrame"],
            "frameScaler": animation["frameScaler"], "rate": animation["rate"],
            "rateSemantics": animation["rateSemantics"], "skeletonMesh": animation["skeleton"]["mesh"],
            "animatedParts": len(animation["skeleton"]["animatedParts"])}


# A mode's phase runs from 0 to 1, growing by the mode's rate once per game tick, 20 ticks a second, and a rate up to
# 0.0001 plays at 1 instead (CAnimation::Process and CAnimation::SetAnimMode, as
# reverse-engineering/asset-formats/cmsh-animation-keys.md documents them and
# rebuild/OnslaughtRebuild.Parity/Things/Animation.cs follows them).
TICKS_PER_SECOND = 20
SLOWEST_RATE = 0.0001


def animation_metadata(record: dict) -> tuple[dict, dict]:
    """(metadata fields, details) of an animation mode. frames counts the virtual frames from its start to its last
    frame inclusive, whichever way it runs: a negative frame scaler plays from start down to last. durationSeconds is
    the time its phase takes from 0 to 1 at its stored rate, as the game plays that rate; a looping mode repeats at
    that period, and a script can choose another speed. A stored rate that is not a finite number (the catalogue gives
    it as null) gives no duration."""
    animation = record["animation"]
    rate = animation["rate"]
    seconds = None if rate is None else round(1 / (TICKS_PER_SECOND * (rate if rate > SLOWEST_RATE else 1.0)), 3)
    fields = media_fields(format="camd", frames=abs(animation["lastFrame"] - animation["startFrame"]) + 1,
                          durationSeconds=seconds)
    return fields, animation_details(record)


def catalogue_metadata(asset: dict) -> tuple[dict, dict]:
    """(metadata fields, details) of a catalogue record of a metadata kind."""
    kind = asset["type"]
    if kind == "texture":
        texture, upscale = asset["texture"], asset.get("upscale") or {}
        valid = texture["status"] == "valid"
        stored = texture.get("storedFormat") if valid else None
        fields = media_fields(format=stored, width=texture.get("width") if valid else None,
                              height=texture.get("height") if valid else None,
                              mipLevels=len(texture.get("mips") or []) if valid else None,
                              alpha=upscale.get("alpha") if valid else None, channels=FORMAT_CHANNELS.get(stored))
        details = {"ddsStatus": texture["status"], "sourceFormatFromName": texture.get("sourceFormatFromName"),
                   "frame": texture.get("frame"), "shelf": texture.get("shelf"), "mustbe": texture.get("mustbe"),
                   "premultipliedAlpha": upscale.get("premultipliedAlpha"), "compressed": upscale.get("compressed"),
                   "mips": [{key: mip[key] for key in ("index", "width", "height", "length", "sha256")}
                            for mip in texture.get("mips") or []]}
        return fields, details
    if kind == "texture-descriptor":
        descriptor = asset["textureDescriptor"]
        parsed = descriptor["status"] == "parsed"
        per_frame = descriptor.get("mipLevelsPerFrame") or []
        stored = descriptor.get("texFormatName") if parsed else None
        fields = media_fields(format=stored, width=descriptor.get("width") if parsed else None,
                              height=descriptor.get("height") if parsed else None,
                              mipLevels=per_frame[0] if parsed and len(set(per_frame)) == 1 else None,
                              channels=FORMAT_CHANNELS.get(stored), frames=descriptor.get("frames") if parsed else None)
        details = {"descriptorStatus": descriptor["status"], "requestedFormat": descriptor.get("requestedFormat"),
                   "levels": descriptor.get("levels"), "mipLevelsPerFrame": per_frame,
                   "occurrences": len(descriptor.get("occurrences") or []),
                   "pixelsFrom": sorted(r["target"] for r in asset["relationships"]
                                        if r["type"] == "pixels-from" and r["status"] in NAMING_STATUSES)}
        return fields, details
    if kind == "mesh":
        return media_fields(format="cmsh"), mesh_details(asset)
    if kind == "animation":
        return animation_metadata(asset)
    if kind == "audio":
        audio = asset["audio"]
        fields = media_fields(format=audio.get("codec"), channels=audio.get("channels"),
                              sampleRate=audio.get("sampleRate"), durationSeconds=audio.get("seconds"))
        details = {"audioStatus": audio["status"], "role": audio["role"], "samples": audio.get("samples"),
                   "nominalBitrate": audio.get("nominalBitrate"), "languageLane": audio.get("languageLane")}
        return fields, details
    if kind == "video":
        video = asset["video"]
        fields = media_fields(format=video.get("codec"), width=video.get("width"), height=video.get("height"),
                              durationSeconds=video.get("seconds"), frames=video.get("frames"))
        return fields, {"videoStatus": video["status"], "fps": video.get("fps"), "fpsRational": video.get("fpsRational"),
                        "audioTracks": video.get("audioTracks")}
    raise AccountError(f"{asset['id']}: no metadata reader for a {kind} record")


def record_users(catalog: dict) -> dict[str, set[str]]:
    """Per record id: the records that name it with a naming status (the relationships relationship_index counts), and
    the archives that load it. An animation's link back to its mesh does not make it the mesh's user."""
    users: dict[str, set[str]] = collections.defaultdict(set)
    for asset in catalog["assets"]:
        for relation in asset["relationships"]:
            if relation["status"] not in NAMING_STATUSES or relation["type"] == "animates":
                continue
            for target in cc.relationship_ids(relation):
                if target == asset["id"]:
                    continue
                if relation["type"] == "loaded-by-archive":
                    users[asset["id"]].add(target)
                else:
                    users[target].add(asset["id"])
    return users


def asset_metadata(items: list[dict], catalog: dict, file_rows: dict[str, dict], users: dict[str, set[str]],
                   found: dict[str, dict]) -> list[dict]:
    """One row per item of a metadata kind, in item order."""
    records = {asset["id"]: asset for asset in catalog["assets"]}
    rows = []
    for item in items:
        if item["kind"] not in METADATA_KINDS:
            continue
        record = records.get(item["id"])
        if record is not None:
            fields, details = catalogue_metadata(record)
            wrapping = {"envelope": record["source"]["envelope"], "chunkPath": record["source"]["chunkPath"],
                        "sha256Scope": record["sha256Scope"]}
            usage, upscale = record.get("usage"), record.get("upscale")
        elif item["id"] in found:
            reader = found[item["id"]]
            fields, details = reader["fields"], reader["details"]
            wrapping = {key: reader[key] for key in ("envelope", "chunkPath", "sha256Scope")}
            usage = upscale = None
        else:
            raise AccountError(f"{item['id']}: an asset with neither a catalogue record nor its reader's metadata")
        placed = record is not None or found[item["id"]]["placed"]
        identity = {"file": item["file"], "fileSha256": file_rows[item["file"].casefold()]["sha256"], **wrapping,
                    "offset": item["offset"] if placed else None, "length": item["length"], "sha256": item["sha256"]}
        if item.get("owner"):
            identity["owner"] = item["owner"]
        named_by = set(users.get(item["id"], ())) | ({item["owner"]} if item.get("owner") else set())
        rows.append({"schema": METADATA_SCHEMA, "id": item["id"], "kind": item["kind"], "form": item["form"],
                     "name": item["name"], "status": item["status"], "identity": identity, **fields,
                     "details": details, "used": item["used"], "usedBy": item["usedBy"],
                     "usedByRecords": sorted(named_by), "usage": usage, "upscale": upscale})
    return rows


def metadata_summary(rows: list[dict]) -> dict:
    """Per kind: the rows, and how many establish each metadata field."""
    summary: dict[str, dict] = {}
    for row in rows:
        kind = summary.setdefault(row["kind"], {"rows": 0, "fieldsEstablished": dict.fromkeys(METADATA_FIELDS, 0)})
        kind["rows"] += 1
        for field in METADATA_FIELDS:
            kind["fieldsEstablished"][field] += row[field] is not None
    return dict(sorted(summary.items()))


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
            if item["used"] and set(item["usedBy"]) <= {"loaded-by-archive"}:
                bucket["loadedButNamedByNothing"] = bucket.get("loadedButNamedByNothing", 0) + 1
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


def percent(part: int, whole: int) -> float | None:
    return round(100 * part / whole, 3) if whole else None


def headline(content: int, decoded: int, decoder_only: int, decoder: str | None) -> dict:
    """The content families' decoded share with the independent media decoder and without it. The Vorbis, Bink and JPEG
    payloads count as decoded only when that decoder read them and agreed with the walk, so one number alone overstates
    what the readers of this repository read (with it) or what is understood (without it)."""
    without = decoded - decoder_only
    return {"contentLogicalBytes": content, "mediaDecoder": decoder,
            "withMediaDecoder": {"decodedBytes": decoded, "percent": percent(decoded, content)} if decoder else None,
            "withoutMediaDecoder": {"decodedBytes": without, "percent": percent(without, content)},
            "decodedOnlyByTheMediaDecoder": decoder_only}


def headline_line(head: dict) -> str:
    without = head["withoutMediaDecoder"]
    if head["withMediaDecoder"] is None:
        return (f"content decoded: {without['percent']}% of {head['contentLogicalBytes']} logical bytes "
                f"({without['decodedBytes']}) with no independent media decoder run, so the Vorbis, Bink and JPEG "
                "payloads stay referenced")
    with_decoder = head["withMediaDecoder"]
    return (f"content decoded: {with_decoder['percent']}% of {head['contentLogicalBytes']} logical bytes "
            f"({with_decoder['decodedBytes']}) with {head['mediaDecoder']} decoding the audio, video and JPEG "
            f"payloads; {without['percent']}% ({without['decodedBytes']}) without it, since "
            f"{head['decodedOnlyByTheMediaDecoder']} bytes count as decoded only because that decoder read them")


def build_coverage(rows: list[dict], install_files: int, install_bytes: int, *, items: list[dict] | None = None,
                   proofs: dict | None = None, manifest: dict | None = None, physics_joins: dict | None = None,
                   absent: dict | None = None, decoder: str | None = None, assets: list[dict] | None = None) -> dict:
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
    content = sum(f["logicalBytes"] for f in table if f["content"])
    decoded = total("logicalBytesByClass", DECODED, True)
    decoder_only = sum(row["facts"].get(DECODER_ONLY, 0) for row in rows if row["family"] not in NOT_CONTENT_FAMILIES)
    return {"schema": COVERAGE_SCHEMA, GENERATED_MARKER: True, "installFiles": install_files,
            "headline": headline(content, decoded, decoder_only, decoder),
            "installBytes": install_bytes, "logicalBytes": sum(f["logicalBytes"] for f in table),
            "filesByClass": {klass: sum(f["filesByClass"][klass] for f in table) for klass in FILE_CLASSES},
            "logicalBytesByClass": {klass: total("logicalBytesByClass", klass, None) for klass in BYTE_CLASSES},
            "unknownLogicalBytes": {"content": total("logicalBytesByClass", UNKNOWN, True),
                                    "notContent": total("logicalBytesByClass", UNKNOWN, False),
                                    "all": total("logicalBytesByClass", UNKNOWN, None)},
            "emptyFiles": sum(1 for row in rows if not row["storedBytes"]),
            "emptyFilesByFamily": dict(sorted(collections.Counter(row["family"] for row in rows
                                                                  if not row["storedBytes"]).items())),
            "sniffDisagreements": sum(1 for row in rows if not sniff_agrees(row["family"], row["sniff"])),
            "problems": sum(len(row["problems"]) for row in rows),
            "filesWithProblems": sum(1 for row in rows if row["problems"]),
            "families": table,
            "notDecodedParts": [{"class": klass, "family": family, "part": part, "bytes": count}
                                for (klass, family, part), count in sorted(parts.items(), key=lambda kv: -kv[1])],
            "items": item_summary(items or []),
            "assetMetadata": metadata_summary(assets or []),
            "proofs": dict(sorted((proofs or {}).items())),
            "mediaDecoder": decoder or "not run: Vorbis, Bink and JPEG payloads stay referenced",
            "installManifest": manifest or {"status": "not compared"},
            "physicsJoins": physics_joins or {},
            "namedButAbsent": absent or {},
            "rules": {
                DECODED: "a reader consumed these bytes in the loader's order and its walk closed exactly, or a codec "
                         "payload every bit pattern of which decodes, or one an independent decoder read with no error "
                         "and agreed with, or a source no loader reads whose grammar holds to its end (a mission script "
                         "only when its compile reproduces the shipped copy, or compiles with every include present "
                         "when none ships); a decoded byte is owned by a reader, which does not claim every field's "
                         "meaning or any runtime behaviour",
                REFERENCED: "a record or reader establishes what these bytes are and how long they are, but nothing "
                            "has read their contents",
                UNKNOWN: "neither; a gap in a walk falls here by construction",
                "used": "a catalogue record, physics value, page link or loader rule names the file or asset; not a "
                        "runtime observation",
                "logicalBytes": "an AYA envelope's inflated stream, or the plain file itself",
                "headline": "the content families' decoded logical bytes with the independent media decoder (the "
                            "Vorbis, Bink and JPEG payloads count only when it read them and agreed with the walk) "
                            "and without it"}}


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
            if facts.get("notJudged"):
                ctx.proofs["mslSourcesNotJudged"] += 1


def build_inventory(game: Path, decomp: Path | None = None, *, decoder: str | None = None, jobs: int = 8) -> dict:
    catalog = cc.build_catalog(game, decomp)
    media_results = decode_all_media(game, catalog["files"], decoder, jobs) if decoder else {}
    unread: dict[str, str] = {}
    ctx = Context(game, media_results=media_results, msl_verdicts=judge_mission_scripts(game, unread), msl_unread=unread)
    ctx.proofs[MSL_UNREAD] = len(unread)  # recorded even when 0: the gate requires it to be 0
    rows, found = [], []
    for row in catalog["files"]:
        if row["size"] is None:
            raise AccountError(f"{row['path']}: a link or special file, which no account holds")
        account, items = read_file(game, row, ctx)
        rows.append(account)
        found.extend(items)
    incoming = relationship_index(catalog)
    users = record_users(catalog)
    joins = join_physics(catalog, ctx, incoming)
    joins["chainedMeshTextures"] = join_chained_textures(found, catalog, incoming, users)
    used = file_use(catalog, incoming, ctx, code_words(decomp))
    for account in rows:
        evidence = sorted(used.get(account["path"].casefold(), ()))
        account["used"] = bool(evidence)
        account["usedBy"] = evidence
    file_rows = {row["path"].casefold(): row for row in rows}
    items = catalogue_items(catalog, incoming, file_rows)
    found_rows, found_metadata_by_id = reader_items(found, file_rows, items)
    items += found_rows
    ids = collections.Counter(item["id"] for item in items)
    duplicates = [name for name, count in ids.items() if count > 1]
    if duplicates:
        raise AccountError(f"duplicate item ids: {duplicates[:3]}")
    assets = asset_metadata(items, catalog, file_rows, users, found_metadata_by_id)
    media_proofs(ctx, rows)
    coverage = build_coverage(rows, catalog["survey"]["files"], catalog["survey"]["bytes"], items=items,
                              proofs=dict(ctx.proofs), manifest=install_manifest_check(ctx, rows),
                              physics_joins=joins, absent=named_but_absent(catalog),
                              decoder=decoder_identity(decoder) if decoder else None, assets=assets)
    return {"files": rows, "items": items, "assets": assets, "coverage": coverage, "catalog": catalog}


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
                "itemCount": len(items), "assetMetadataCount": len(inventory["assets"]),
                "boundary": "retail-derived metadata including names, sizes and hashes; no retail payload bytes; "
                            "never commit"}
    outputs = {"manifest.json": json.dumps(manifest, indent=2, sort_keys=True) + "\n",
               "coverage.json": json.dumps(coverage, indent=2, sort_keys=True) + "\n",
               "files.jsonl": "".join(json.dumps({**row, GENERATED_MARKER: True}, sort_keys=True) + "\n" for row in rows),
               "items.jsonl": "".join(json.dumps({**row, GENERATED_MARKER: True}, sort_keys=True) + "\n" for row in items),
               "asset-metadata.jsonl": "".join(json.dumps({**row, GENERATED_MARKER: True}, sort_keys=True) + "\n"
                                               for row in inventory["assets"]),
               "records.jsonl": "".join(json.dumps({"id": asset["id"], "type": asset["type"], "source": asset["source"],
                                                    "sha256": asset["sha256"], GENERATED_MARKER: True}, sort_keys=True) + "\n"
                                        for asset in inventory["catalog"]["assets"])}
    written = []
    protected = [game] + ([decomp] if decomp is not None else [])
    with SecuredOutputRoot(out, protected_sources=protected) as secured:
        for name, text in outputs.items():
            with secured.atomic_text_writer(out / name) as writer:
                writer.write(text)
            written.append(out / name)
    return written


def summary_lines(coverage: dict) -> list[str]:
    """Counts only: one line per family, the assets by kind and the metadata rows' established fields, then the totals
    and the headline share."""
    lines = []
    for fam in coverage["families"]:
        classes = " ".join(f"{klass}={fam['filesByClass'][klass]}" for klass in FILE_CLASSES)
        logical = " ".join(f"{klass}={fam['logicalBytesByClass'][klass]}" for klass in BYTE_CLASSES)
        lines.append(f"{fam['family']}: files={fam['files']} stored={fam['storedBytes']} "
                     f"logical={fam['logicalBytes']} [{classes}] [{logical}] used={fam['usedFiles']}")
    for kind, row in coverage["items"].items():
        lines.append(f"items {kind}: {row['items']} used={row['used']} unused={row['unused']}")
    for kind, row in coverage.get("assetMetadata", {}).items():
        fields = " ".join(f"{field}={count}" for field, count in row["fieldsEstablished"].items())
        lines.append(f"asset metadata {kind}: rows={row['rows']} [{fields}]")
    unknown = coverage["unknownLogicalBytes"]
    lines.append(f"unknown logical bytes: content={unknown['content']} not-content={unknown['notContent']} "
                 f"all={unknown['all']}; problems={coverage['problems']}")
    empty = coverage["emptyFilesByFamily"]
    lines.append(f"empty files (decoded, as every empty file is): {coverage['emptyFiles']}"
                 + "".join(f" {family}={count}" for family, count in empty.items()))
    proofs = coverage["proofs"]
    verdicts = " ".join(f"{key[len('mslVerdict '):].replace(', ', '-').replace(' ', '-')}={count}"
                        for key, count in proofs.items() if key.startswith("mslVerdict "))
    lines.append(f"mission scripts: shipped-copy verdicts [{verdicts}]; level archives whose worlds the judge could not "
                 f"read={proofs.get(MSL_UNREAD, 'not recorded')}")
    lines.append(headline_line(coverage["headline"]))
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
