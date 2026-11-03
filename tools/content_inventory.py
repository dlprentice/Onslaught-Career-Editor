#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Battle Engine Aquila content inventory: a byte account of every file of a selected install.

tools/content_catalog.py says what the game's files hold and what names what. This tool answers a different question:
of the bytes on the disc, how many has a reader actually understood? Each file is walked by the reader that follows
its loader, and every byte of its stream lands in exactly one part of an account:

  decoded     a reader consumed these bytes in the loader's order and the reader's walk closed exactly. A codec payload
              counts only when every bit pattern decodes (raw pixels, DXT blocks, IMA ADPCM). A decoded byte means the
              reader owns it; it does not claim that every field has a known meaning or that the game behaves any way.
  referenced  a record or reader establishes what these bytes are and how long they are, but nothing has read their
              contents.
  unknown     neither. A gap in a walk falls here by construction, so a reader cannot lose bytes silently.

A file with nothing but decoded bytes is "decoded", with nothing but referenced bytes "referenced", with nothing but
unknown bytes "unknown", and any mix is "partial". An empty file is decoded. Separately from that class, "used" says
that a catalogue record or a loader rule names the file; it is not a runtime observation.

Bytes are logical: an AYA envelope's inflated stream, and a plain file's own bytes. The stored size of every file is
reported beside them, and the stored sizes sum to the install's size or the run fails.

The install is only read. Run output is retail-derived (names, sizes, hashes, never payload bytes), so it is written
only below this checkout's ignored local-data/ directory and carries the generatedRetailDerived marker.

Run:  python ./tools/content_inventory.py --game GAME_FOLDER [--decomp ONSLAUGHT_DECOMP] [--out local-data/content-inventory]
"""
from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import json
import os
import struct
import sys
import zlib
from pathlib import Path, PurePosixPath

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(ROOT / "rebuild" / "tools"))

import aya_archive_inventory as aai  # noqa: E402
import aya_cross_platform_compare as cross  # noqa: E402
import aya_texture_fidelity_census as packed  # noqa: E402
import cmsh_animation_usage_census as meshcensus  # noqa: E402
import cmsh_grammar_walk as grammar  # noqa: E402
import content_catalog as cc  # noqa: E402
import dds_census  # noqa: E402
import game_tables_decode as gtd  # noqa: E402
import goodie_resource_walk as goodies  # noqa: E402
import language_dat_decode  # noqa: E402
import named_things as nt  # noqa: E402
import world_resources_decode as wrd  # noqa: E402
import worldheaders_decode  # noqa: E402
import xap_bank_walk  # noqa: E402
from safe_generated_output import SecuredOutputRoot, UnsafeGeneratedOutputError, validate_disjoint_output_root  # noqa: E402

SCHEMA_VERSION = 1
COVERAGE_SCHEMA = "onslaught.content-inventory.coverage.v1"
FILE_SCHEMA = "onslaught.content-inventory.file.v1"
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


def file_class(size: int, totals: dict) -> str:
    if size == 0:
        return DECODED
    present = [klass for klass in BYTE_CLASSES if totals[klass]]
    return present[0] if len(present) == 1 else PARTIAL


class Context:
    """What the readers share: the selected game and the definition lookups a world body needs."""

    def __init__(self, game: Path):
        self.game = game
        self.lookup: dict | None = None

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
    """One reader's outcome: the account of the stream it walked, and what it refused."""

    def __init__(self, account: Account, stream: str, reader: str):
        self.account, self.stream, self.reader = account, stream, reader
        self.problems: list[str] = []
        self.facts: dict = {}


def whole_file(data: bytes, klass: str, part: str, reader: str) -> Reading:
    reading = Reading(Account(len(data)), "stored", reader)
    reading.account.add(0, len(data), klass, part)
    return reading


# ---------------------------------------------------------------------------------------- archives (LVLR tag streams)
FIXED_PREFIX = {"LVLR": 4, "TARG": 4, "AYAD": 24}
PAYLOAD_DECODERS = {"ERES": wrd.parse_eres, "SURF": wrd.parse_surf, "SSHD": wrd.parse_sshd, "VSDS": wrd.parse_vsds,
                    "PMIB": wrd.parse_pmib, "DMKR": wrd.parse_dmkr}
DECODE_ERRORS = (wrd.DecodeError, struct.error, ValueError)


def read_mesh_chunk(account: Account, payload: bytes, base: int, reading: Reading) -> None:
    """A MESH chunk: a named record whose mesh is a loose file, or a mesh stream carried inline."""
    tag = "MESH"
    try:
        _key, display, method = cross.logical_key("MESH", payload)
    except ValueError as error:
        reading.problems.append(f"MESH: {error}")
        account.add(base - 8, 8 + len(payload), UNKNOWN, tag)
        return
    if display:
        header = 16 + goodies.MESH_REFERENCE if method.startswith("PMSH/PMS2") else 8 + goodies.MESH_REFERENCE
        account.add(base - 8, 8 + header, DECODED, "MESH/reference")
        account.add(base + header, len(payload) - header, REFERENCED, "MESH/reference-tail")
        return
    try:
        stream, offset = meshcensus._direct_embedded_cmsh_with_offset(payload)
        grammar.walk_stream(stream, collections.defaultdict(collections.Counter))
    except (ValueError, struct.error) as error:
        reading.problems.append(f"MESH: {error}")
        account.add(base - 8, 8 + len(payload), REFERENCED, "MESH/embedded")
        return
    account.add(base - 8, 8 + offset, DECODED, "MESH/reference")
    account.add(base + offset, len(stream), DECODED, "MESH/embedded-cmsh")
    account.add(base + offset + len(stream), len(payload) - offset - len(stream), UNKNOWN, "MESH/tail")


def read_world_chunk(account: Account, payload: bytes, base: int, ctx: Context, reading: Reading) -> None:
    """WRES: WRLD holding WDAT and the world bodies, each read by CWorld::LoadWorld's order."""
    outer = aai.parse_top_level_chunks_bounded(payload)
    claimed = 0
    for wrapper in outer:
        start = base + wrapper.offset
        if wrapper.tag != "WRLD":
            account.add(start, 8 + wrapper.size, UNKNOWN, "WRES/" + wrapper.tag)
            continue
        account.add(start, 8, DECODED, "WRES/framing")
        body = payload[wrapper.offset + 8:wrapper.offset + 8 + wrapper.size]
        for child in aai.parse_top_level_chunks_bounded(body):
            at = start + 8 + child.offset
            inner = body[child.offset + 8:child.offset + 8 + child.size]
            if child.tag == "WDAT" and child.size == 8:
                account.add(at, 16, DECODED, "WRES/WDAT")
            elif child.tag in cc.WORLD_KINDS:
                try:
                    wrd.parse_world_body(inner, ctx.world_lookup(), base=child.tag == "BSWD")
                except DECODE_ERRORS as error:
                    reading.problems.append(f"{child.tag}: {error}")
                    account.add(at, 8 + child.size, REFERENCED, "WRES/" + child.tag)
                    continue
                account.add(at, 8 + child.size, DECODED, "WRES/" + child.tag)
            else:
                account.add(at, 8 + child.size, UNKNOWN, "WRES/" + child.tag)
        claimed += 1
    if not claimed:
        reading.problems.append("WRES holds no WRLD")


def read_nested_textures(account: Account, payload: bytes, base: int, tag: str, reading: Reading) -> None:
    """A chunk whose own schema has no reader yet: its serialized texture records, and the rest as framed bytes."""
    position = 0
    for at, record in cc.scan_dxtx(payload):
        account.add(base + position, at - position, REFERENCED, tag + "/framing")
        account.add(base + at, len(record), DECODED, tag + "/DXTX")
        position = at + len(record)
    account.add(base + position, len(payload) - position, REFERENCED, tag + "/framing")


def read_archive(data: bytes, ctx: Context, _row: dict) -> Reading:
    raw, chunks, members, _envelope = aai.decode_archive_envelope(data, "pc-chunked-zlib")
    reading = Reading(Account(len(raw)), "inflated", "tools/aya_archive_inventory.py:decode_archive_envelope")
    account = reading.account
    reading.facts = {"members": members, "chunks": len(chunks)}
    for chunk in chunks:
        base = chunk.offset + 8
        payload = raw[base:base + chunk.size]
        tag = chunk.tag
        if tag in FIXED_PREFIX:
            account.add(chunk.offset, 8 + chunk.size, DECODED if chunk.size == FIXED_PREFIX[tag] else REFERENCED, tag)
        elif tag == "LNDS":
            account.add(chunk.offset, 8 + chunk.size, DECODED if chunk.size == 0 else REFERENCED, tag)
        elif tag == "TEXT":
            try:
                cc.parse_text_record(payload)
            except (ValueError, struct.error) as error:
                reading.problems.append(f"TEXT chunk {chunk.index}: {error}")
                account.add(chunk.offset, 8 + chunk.size, REFERENCED, tag)
                continue
            account.add(chunk.offset, 8 + chunk.size, DECODED, tag)
        elif tag == "MESH":
            read_mesh_chunk(account, payload, base, reading)
        elif tag == "WRES":
            account.add(chunk.offset, 8, DECODED, "WRES/framing")
            read_world_chunk(account, payload, base, ctx, reading)
        elif tag in PAYLOAD_DECODERS:
            try:
                PAYLOAD_DECODERS[tag](payload)
            except DECODE_ERRORS as error:
                reading.problems.append(f"{tag}: {error}")
                account.add(chunk.offset, 8 + chunk.size, REFERENCED, tag)
                continue
            account.add(chunk.offset, 8 + chunk.size, DECODED, tag)
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
            read_nested_textures(account, payload, base, tag, reading)
        else:
            account.add(chunk.offset, 8 + chunk.size, UNKNOWN, tag)
    return reading


# ------------------------------------------------------------------------------------------------------- loose files
def read_mesh_file(data: bytes, _ctx: Context, _row: dict) -> Reading:
    stream = aai.inflate_aya_bytes(data)
    reading = Reading(Account(len(stream)), "inflated", "tools/cmsh_grammar_walk.py:walk_stream")
    try:
        grammar.walk_stream(stream, collections.defaultdict(collections.Counter))
    except (grammar.GrammarError, struct.error) as error:
        reading.problems.append(str(error))
        reading.account.add(0, len(stream), REFERENCED, "CMSH")
        return reading
    reading.account.add(0, len(stream), DECODED, "CMSH")
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
    reading = Reading(Account(len(data)), "stored", "tools/xap_bank_walk.py:read_bank")
    try:
        _magic, samples = xap_bank_walk.read_bank(data)
    except xap_bank_walk.BankError as error:
        reading.problems.append(str(error))
        reading.account.add(0, len(data), REFERENCED, "XAP")
        return reading
    reading.account.add(0, len(data), DECODED, "XAP")
    reading.facts = {"samples": len(samples)}
    return reading


def read_ogg_header(data: bytes, _ctx: Context, _row: dict) -> Reading:
    reading = Reading(Account(len(data)), "stored", "tools/content_catalog.py:ogg_metadata")
    try:
        meta = cc.ogg_metadata(data)
    except ValueError as error:
        reading.problems.append(str(error))
        reading.account.add(0, len(data), REFERENCED, "ogg")
        return reading
    first = 27 + data[26] + sum(data[27:27 + data[26]])
    reading.account.add(0, first, DECODED, "ogg/identification-page")
    reading.account.add(first, len(data) - first, REFERENCED, "ogg/pages")
    reading.facts = {"seconds": meta["seconds"]}
    return reading


def read_bink_header(data: bytes, _ctx: Context, _row: dict) -> Reading:
    reading = Reading(Account(len(data)), "stored", "tools/content_catalog.py:bink_metadata")
    try:
        meta = cc.bink_metadata(data)
    except (ValueError, struct.error) as error:
        reading.problems.append(str(error))
        reading.account.add(0, len(data), REFERENCED, "bink")
        return reading
    reading.account.add(0, 44, DECODED, "bink/header")
    reading.account.add(44, len(data) - 44, REFERENCED, "bink/index-and-frames")
    reading.facts = {"frames": meta["frames"]}
    return reading


def read_language_table(data: bytes, _ctx: Context, _row: dict) -> Reading:
    """The table's header, entries and pools, with the text-pool bytes no entry reaches left unclaimed."""
    reading = Reading(Account(len(data)), "stored", "tools/language_dat_decode.py:parse_lang_dat_bytes")
    account = reading.account
    try:
        table = language_dat_decode.parse_lang_dat_bytes(data)
    except ValueError as error:
        reading.problems.append(str(error))
        account.add(0, len(data), REFERENCED, "language-table")
        return reading
    pool = table.text_pool_off
    size = table.uvar7
    account.add(0, pool, DECODED, "language/entries")
    reached = bytearray(size)
    for entry in table.entries:
        at = entry.text_off_words * 2
        end = at
        while end + 1 < size and data[pool + end:pool + end + 2] != b"\0\0":
            end += 2
        reached[at:end + 2] = b"\1" * (min(end + 2, size) - at)
    start = None
    for index in range(size + 1):
        on = index < size and reached[index]
        if on and start is None:
            start = index
        elif not on and start is not None:
            account.add(pool + start, index - start, DECODED, "language/text-pool")
            start = None
    account.add(pool + size, table.audio_pool_off - pool - size, DECODED, "language/pool-header")
    account.add(table.audio_pool_off, table.audio_pool_size, DECODED, "language/audio-pool")
    reading.facts = {"entries": table.count}
    return reading


def read_exact_table(parse, reader: str):
    """A whole-file reader that refuses anything it does not consume exactly."""
    def read(data: bytes, _ctx: Context, _row: dict) -> Reading:
        try:
            parse(data)
        except (ValueError, struct.error) as error:
            reading = whole_file(data, REFERENCED, "table", reader)
            reading.problems.append(str(error))
            return reading
        return whole_file(data, DECODED, "table", reader)
    return read


def read_physics_table(data: bytes, _ctx: Context, _row: dict) -> Reading:
    """The statement framing, names and the two value kinds tools/cmsh_animation_usage_census.py reads."""
    reading = Reading(Account(len(data)), "stored", "tools/cmsh_animation_usage_census.py:_physics_mesh_definitions")
    account = reading.account
    try:
        meshcensus._physics_mesh_definitions(data)
    except ValueError as error:
        reading.problems.append(str(error))
        account.add(0, len(data), REFERENCED, "physics")
        return reading
    offset = 2
    account.add(0, 2, DECODED, "physics/framing")
    while True:
        (kind,) = struct.unpack_from("<i", data, offset)
        if kind == -1:
            account.add(offset, 4, DECODED, "physics/framing")
            offset += 4
            break
        start = offset
        offset = data.index(b"\0", offset + 8) + 1
        account.add(start, offset - start, DECODED, "physics/framing")
        mesh_field = meshcensus.PHYSICS_MESH_FIELDS.get(kind)
        while True:
            value_id, size = struct.unpack_from("<II", data, offset)
            account.add(offset, 8, DECODED, "physics/framing")
            offset += 8
            read = (mesh_field is not None and value_id == mesh_field[0]) or (kind == 1 and value_id == 8)
            account.add(offset, size, DECODED if read else REFERENCED, "physics/value")
            offset += size
            (marker,) = struct.unpack_from("<i", data, offset)
            account.add(offset, 4, DECODED, "physics/framing")
            offset += 4
            if marker == -1:
                break
    account.add(offset, len(data) - offset, UNKNOWN, "physics/trailing")
    return reading


def read_referenced_file(data: bytes, _ctx: Context, row: dict) -> Reading:
    """A catalogued file whose contents no reader parses yet."""
    return whole_file(data, REFERENCED, row["family"], "tools/content_catalog.py:catalog_text_inventory")


READERS = {
    "lvlr-resource-archive": read_archive,
    "cmsh-mesh": read_mesh_file,
    "dds-texture-dxtn": read_texture_file,
    "dds-texture-uncompressed": read_texture_file,
    "xap-sample-bank": read_sample_bank,
    "ogg-music": read_ogg_header,
    "ogg-voice": read_ogg_header,
    "bink-video": read_bink_header,
    "language-dat": read_language_table,
    "sfx-catalog": read_exact_table(gtd.parse_sfx, "tools/game_tables_decode.py:parse_sfx"),
    "battle-engine-config-dat": read_exact_table(gtd.parse_battle_engine_configurations,
                                                 "tools/game_tables_decode.py:parse_battle_engine_configurations"),
    "world-headers-dat": read_exact_table(worldheaders_decode.parse_worldheaders,
                                          "tools/worldheaders_decode.py:parse_worldheaders"),
    "default-physics-dat": read_physics_table,
    "particle-set-par": read_referenced_file,
    "mission-script-msl": read_referenced_file,
    "mission-text-txt": read_referenced_file,
    "stf-text-table": read_referenced_file,
}


def read_file(game: Path, row: dict, ctx: Context) -> dict:
    """One file's account. A reader that cannot run leaves the whole file unknown and says why."""
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
    return {"schema": FILE_SCHEMA, "path": row["path"], "family": row["family"], "storedBytes": len(data),
            "sha256": cc.sha256(data), "stream": reading.stream, "logicalBytes": reading.account.size,
            "class": file_class(reading.account.size, closed["totals"]), "bytes": closed["totals"],
            "parts": closed["parts"], "unknownSpans": closed["unknownSpans"], "reader": reading.reader,
            "problems": problems + reading.problems, "facts": reading.facts}


# ---------------------------------------------------------------------------------------------------------------- use
def incoming_use(catalog: dict) -> dict[str, set[str]]:
    """Per file (folded path): the record types and relationships that name something the file holds.

    A relationship counts when its status names its target and the naming record sits in another file; a level is a
    logical record, so what it names counts even when its own record points at the same archive.
    """
    assets = catalog["assets"]
    by_id = {a["id"]: a for a in assets}
    used: dict[str, set[str]] = collections.defaultdict(set)
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
        audio = asset.get("audio") or {}
        if audio.get("textId") is not None:
            used[source].add("text-table:voice-name")
    return used


# ----------------------------------------------------------------------------------------------------------- coverage
def build_coverage(rows: list[dict], install_files: int, install_bytes: int) -> dict:
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

    return {"schema": COVERAGE_SCHEMA, GENERATED_MARKER: True, "installFiles": install_files,
            "installBytes": install_bytes, "logicalBytes": sum(f["logicalBytes"] for f in table),
            "filesByClass": {klass: sum(f["filesByClass"][klass] for f in table) for klass in FILE_CLASSES},
            "logicalBytesByClass": {klass: total("logicalBytesByClass", klass, None) for klass in BYTE_CLASSES},
            "unknownLogicalBytes": {"content": total("logicalBytesByClass", UNKNOWN, True),
                                    "notContent": total("logicalBytesByClass", UNKNOWN, False),
                                    "all": total("logicalBytesByClass", UNKNOWN, None)},
            "problems": sum(len(row["problems"]) for row in rows),
            "filesWithProblems": sum(1 for row in rows if row["problems"]),
            "families": table,
            "rules": {
                DECODED: "a reader consumed these bytes in the loader's order and its walk closed exactly; a decoded "
                         "byte is owned by a reader, which does not claim every field's meaning",
                REFERENCED: "a record or reader establishes what these bytes are and how long they are, but nothing "
                            "has read their contents",
                UNKNOWN: "neither; a gap in a walk falls here by construction",
                "used": "a catalogue record or a loader rule names the file; not a runtime observation",
                "logicalBytes": "an AYA envelope's inflated stream, or the plain file itself"}}


def build_inventory(game: Path, decomp: Path | None = None) -> dict:
    catalog = cc.build_catalog(game, decomp)
    ctx = Context(game)
    used = incoming_use(catalog)
    rows = []
    for row in catalog["files"]:
        if row["size"] is None:
            continue
        account = read_file(game, row, ctx)
        evidence = sorted(used.get(row["path"].casefold(), ()))
        account["used"] = bool(evidence)
        account["usedBy"] = evidence
        rows.append(account)
    coverage = build_coverage(rows, catalog["survey"]["files"], catalog["survey"]["bytes"])
    return {"files": rows, "coverage": coverage, "catalog": catalog}


def write_outputs(out: Path, game: Path, inventory: dict, *, decomp: Path | None = None) -> list[Path]:
    rows, coverage = inventory["files"], inventory["coverage"]
    manifest = {"schema": MANIFEST_SCHEMA, GENERATED_MARKER: True, "schemaVersion": SCHEMA_VERSION,
                "generatedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tool": TOOL, "toolCommit": cc.git_head(),
                "install": {"files": coverage["installFiles"], "bytes": coverage["installBytes"],
                            "pathSizeFingerprint": cc.install_fingerprint(game, inventory["catalog"]["files"])},
                "boundary": "retail-derived metadata including names, sizes and hashes; no retail payload bytes; "
                            "never commit"}
    outputs = {"manifest.json": json.dumps(manifest, indent=2, sort_keys=True) + "\n",
               "coverage.json": json.dumps(coverage, indent=2, sort_keys=True) + "\n",
               "files.jsonl": "".join(json.dumps({**row, GENERATED_MARKER: True}, sort_keys=True) + "\n" for row in rows)}
    written = []
    protected = [game] + ([decomp] if decomp is not None else [])
    with SecuredOutputRoot(out, protected_sources=protected) as secured:
        for name, text in outputs.items():
            with secured.atomic_text_writer(out / name) as writer:
                writer.write(text)
            written.append(out / name)
    return written


def summary_lines(coverage: dict) -> list[str]:
    """Counts only: one line per family, then the totals."""
    lines = []
    for fam in coverage["families"]:
        classes = " ".join(f"{klass}={fam['filesByClass'][klass]}" for klass in FILE_CLASSES)
        logical = " ".join(f"{klass}={fam['logicalBytesByClass'][klass]}" for klass in BYTE_CLASSES)
        lines.append(f"{fam['family']}: files={fam['files']} stored={fam['storedBytes']} "
                     f"logical={fam['logicalBytes']} [{classes}] [{logical}] used={fam['usedFiles']}")
    unknown = coverage["unknownLogicalBytes"]
    lines.append(f"unknown logical bytes: content={unknown['content']} not-content={unknown['notContent']} "
                 f"all={unknown['all']}; problems={coverage['problems']}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"))
    parser.add_argument("--out", type=Path, default=ROOT / "local-data" / "content-inventory")
    parser.add_argument("--decomp", type=Path, help="optional onslaught-decomp checkout, passed to the catalogue")
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
    try:
        inventory = build_inventory(game, decomp)
    except (nt.RegistryLimitError, cc.CatalogInputError, AccountError) as error:
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
