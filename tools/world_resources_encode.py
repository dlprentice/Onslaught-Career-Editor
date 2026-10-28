#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""World body encoder: the inverse of tools/world_resources_decode.py:parse_world_body, byte for byte.

A world body is what CWorld::LoadWorld reads (onslaught-decomp src/world.cpp CWorld::LoadWorld @0x0050b9c0): the BSWD
or RLWD chunk inside a level archive's WRES/WRLD, or a loose data\\worlds\\worldNNN.wrd file, which CWorld::Load
(@0x0050b520) opens when the archive's WDAT does not name the level being loaded.

    read_world_model(body)  -> a lossless JSON-ready model (every field LoadWorld reads, in its order; the regions
                               LoadWorld only skips or copies, such as the influence map and the occupancy grids, as
                               base64 blobs)
    write_world_body(model) -> the bytes LoadWorld reads; write_world_body(read_world_model(b)) == b

The model is the editing surface: change a thing's init.position, append a thing, then write the body back. Thing
order matters: CWaypointPath::Load indexes LoadWorld's things[] slots, so a new thing goes after the existing ones
(see slot_note in the model) or the waypoint paths must be renumbered.

Command line (retail data is read only; output goes under this checkout's ignored local-data/ or a port user folder,
never the selected game folder):

    world_resources_encode.py verify --game DIR                 every level archive: decode -> encode == original
    world_resources_encode.py extract --game DIR --level N --out DIR
                                                                 the level's world bodies as worldNNN.wrd + .json
    world_resources_encode.py encode --game DIR MODEL.json OUT.wrd
                                                                 a (possibly edited) model back to a world body
    world_resources_encode.py stage --game DIR --level N --user DIR [--world MODEL.json]
                                                                 a port user folder that loads the level's world from
                                                                 loose files: data\\worlds\\worldNNN.wrd (and its base
                                                                 world), plus a shadow copy of the level archive whose
                                                                 WDAT names no level, so CWorld::Load takes the loose path

Output files must have fresh names: nothing existing is replaced. Every file is published atomically without
replacement, with symlinks and overlapping game paths refused. A multi-file command may leave earlier new files
if a later publication fails; inspect them and choose a fresh output folder for another attempt. Fresh-only
publication currently fails closed on Windows until native no-replace support is verified.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import re
import stat
import struct
import sys
import zlib
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import world_resources_decode as wrd  # noqa: E402
import aya_archive_inventory as archive_limits  # noqa: E402
from safe_generated_output import SecuredOutputRoot, UnsafeGeneratedOutputError  # noqa: E402

MODEL_FORMAT = "onslaught.world-body.v1"
LEVEL_ARCHIVE_RE = re.compile(r"^(\d{3})_res_pc\.aya$", re.IGNORECASE)
PACK_BUFFER_SIZE = 0x102927  # CDXMemBuffer's gPackBuffer (onslaught-decomp src/DXMemBuffer.cpp, retail 005481a4)
# The PC writer and default read allocation use 1 MiB. This tool refuses larger inflated members even though the
# reader passes PACK_BUFFER_SIZE as zlib's limit; the complete retained PC world corpus fits the 1 MiB bound.
MAX_INFLATED_MEMBER_BYTES = 1024 * 1024
# These are tooling resource ceilings shared with the archive inventory, not claims about the game's format maximum.
MAX_ARCHIVE_BYTES = archive_limits.MAX_COMPRESSED_BYTES
MAX_ARCHIVE_INFLATED_BYTES = archive_limits.MAX_INFLATED_BYTES
MAX_ARCHIVE_MEMBERS = archive_limits.MAX_MEMBERS
NO_LEVEL = 9999  # a WDAT level number no level uses: CWorld::Load then resets both resource positions


class EncodeError(ValueError):
    pass


# ------------------------------------------------------------------------------------------------------- scalars
def f32_in(r: wrd.Reader):
    """A float32 as a JSON number; a non-finite value keeps its exact bits."""
    raw = r.take(4)
    value = struct.unpack("<f", raw)[0]
    return value if math.isfinite(value) else {"f32bits": raw.hex()}


def f32_out(value) -> bytes:
    if isinstance(value, dict):
        bits = value.get("f32bits")
        if set(value) != {"f32bits"} or not isinstance(bits, str) or not re.fullmatch(r"[0-9a-fA-F]{8}", bits):
            raise EncodeError("f32bits must be exactly four hex-encoded bytes")
        return bytes.fromhex(bits)
    out = struct.pack("<f", value)
    if struct.unpack("<f", out)[0] != value and not (value == 0 and math.copysign(1, value) < 0):
        raise EncodeError(f"{value!r} is not a float32 value")
    return out


def blob(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def unblob(text: str) -> bytes:
    return base64.b64decode(text, validate=True)


class Writer:
    def __init__(self):
        self.parts: list[bytes] = []

    def raw(self, data: bytes) -> None:
        self.parts.append(bytes(data))

    def pack(self, fmt: str, *values) -> None:
        try:
            self.parts.append(struct.pack("<" + fmt, *values))
        except struct.error as error:
            raise EncodeError(f"{values!r} does not fit {fmt!r}: {error}") from None

    def i32(self, value: int) -> None:
        self.pack("i", value)

    def f32(self, value) -> None:
        self.parts.append(f32_out(value))

    def floats(self, values) -> None:
        for v in values:
            self.f32(v)

    def cstring(self, text: str) -> None:
        data = text.encode("latin-1")
        if b"\0" in data or len(data) > 255:
            raise EncodeError(f"string {text!r} cannot be written NUL-terminated")
        self.parts.append(data + b"\0")

    def lstring(self, text: str, fmt: str = "b") -> None:
        data = text.encode("latin-1")
        self.pack(fmt, len(data))
        self.parts.append(data)

    def bytes(self) -> bytes:
        return b"".join(self.parts)


# ---------------------------------------------------------------------------------------------- mission scripts
def read_value(r: wrd.Reader, dtype: int):
    """CSymbolTable(file)'s value per data type; a bool keeps its stored word (any nonzero is TRUE)."""
    if dtype in (1, 4, 5):
        return r.i32()
    if dtype == 2:
        return f32_in(r)
    if dtype == 3:
        return r.lstring("i")
    if dtype == 6:
        return [f32_in(r) for _ in range(3)]
    raise wrd.DecodeError(f"unknown script data type {dtype}")


def write_value(w: Writer, dtype: int, value) -> None:
    if dtype in (1, 4, 5):
        w.i32(value)
    elif dtype == 2:
        w.f32(value)
    elif dtype == 3:
        w.lstring(value, "i")
    elif dtype == 6:
        if len(value) != 3:
            raise EncodeError("a script vector has exactly three components")
        w.floats(value)
    else:
        raise EncodeError(f"unknown script data type {dtype}")


def read_code(r: wrd.Reader) -> dict:
    """CMissionScriptObjectCode(file), the fields wrd.read_object_code reads, kept exactly."""
    instructions = [list(r.unpack("ii")) for _ in range(r.count())]
    event_pcs = list(r.unpack(f"{wrd.NUM_SCRIPT_EVENTS}i"))
    symbols = []
    for _ in range(r.count()):
        name = r.lstring("i")
        dtype = r.i32()
        value = read_value(r, dtype) if dtype else None
        sym_type, index, flag = r.unpack("iii")
        symbols.append({"name": name, "dataType": dtype, "value": value, "symbolType": sym_type, "index": index,
                        "flag": flag})
    next_index = r.i32()
    functions = []
    for _ in range(r.count()):
        entry = r.i32()
        functions.append({"entryPC": entry, "params": [r.i32() for _ in range(r.count())]})
    return {"instructions": instructions, "eventPCs": event_pcs, "symbols": symbols, "nextSymbolIndex": next_index,
            "eventFunctions": functions, "tail": list(r.unpack("ii"))}


def write_code(w: Writer, code: dict) -> None:
    w.i32(len(code["instructions"]))
    for opcode, attr in code["instructions"]:
        w.pack("ii", opcode, attr)
    if len(code["eventPCs"]) != wrd.NUM_SCRIPT_EVENTS:
        raise EncodeError(f"a script has {wrd.NUM_SCRIPT_EVENTS} event PCs")
    w.pack(f"{wrd.NUM_SCRIPT_EVENTS}i", *code["eventPCs"])
    w.i32(len(code["symbols"]))
    for s in code["symbols"]:
        w.lstring(s["name"], "i")
        w.i32(s["dataType"])
        if s["dataType"]:
            write_value(w, s["dataType"], s["value"])
        w.pack("iii", s["symbolType"], s["index"], s["flag"])
    w.i32(code["nextSymbolIndex"])
    w.i32(len(code["eventFunctions"]))
    for f in code["eventFunctions"]:
        w.i32(f["entryPC"])
        w.i32(len(f["params"]))
        for p in f["params"]:
            w.i32(p)
    w.pack("ii", *code["tail"])


# ------------------------------------------------------------------------------------------------------- things
def read_init(r: wrd.Reader, version: int, cls: str) -> dict:
    """CInitThing::Load and the subclass fields, in wrd.read_init's order."""
    init = {"position": [f32_in(r) for _ in range(3)], "orientation": [f32_in(r) for _ in range(3)]}
    init["meshNumber"], init["allegiance"], init["target"] = r.unpack("iii")
    init["script"], init["name"], init["spawnScript"] = r.cstring(), r.cstring(), r.cstring()
    init["active"] = r.i32()
    if version > 45:
        init["attachScriptsToUnits"] = r.i32()
    if cls == "spawner":
        sp = {"amount": r.i32(), "delay": f32_in(r), "squadDelay": f32_in(r), "initialDelay": f32_in(r),
              "squadSize": r.i32(), "spawnUnit": r.cstring()}
        if version > 43:
            sp["spawnerSpawnScript"] = r.cstring()
        init["spawner"] = sp
    elif cls == "squad":
        init["squad"] = {"amount": r.i32(), "mode": r.i32()}
    elif cls == "cutscene":
        init["cutscene"] = {"file": r.cstring(), "linkTo": r.cstring()}
    elif cls == "start":
        init["start"] = {"planeMode": r.i32(), "playerNumber": r.i32()}
    elif cls == "tree":
        init["tree"] = {"treeType": r.cstring()}
    elif cls == "wall":
        init["wall"] = {"length": f32_in(r), "life": f32_in(r), "wallType": r.cstring()}
    elif cls == "sphere-trigger":
        init["sphereTrigger"] = {"radius": f32_in(r)}
    return init


def write_init(w: Writer, init: dict, version: int, cls: str) -> None:
    if len(init["position"]) != 3 or len(init["orientation"]) != 3:
        raise EncodeError("thing position and orientation each have exactly three components")
    w.floats(init["position"])
    w.floats(init["orientation"])
    w.pack("iii", init["meshNumber"], init["allegiance"], init["target"])
    for key in ("script", "name", "spawnScript"):
        w.cstring(init[key])
    w.i32(init["active"])
    if version > 45:
        w.i32(init["attachScriptsToUnits"])
    if cls == "spawner":
        sp = init["spawner"]
        w.i32(sp["amount"])
        w.floats((sp["delay"], sp["squadDelay"], sp["initialDelay"]))
        w.i32(sp["squadSize"])
        w.cstring(sp["spawnUnit"])
        if version > 43:
            w.cstring(sp["spawnerSpawnScript"])
    elif cls == "squad":
        w.pack("ii", init["squad"]["amount"], init["squad"]["mode"])
    elif cls == "cutscene":
        w.cstring(init["cutscene"]["file"])
        w.cstring(init["cutscene"]["linkTo"])
    elif cls == "start":
        w.pack("ii", init["start"]["planeMode"], init["start"]["playerNumber"])
    elif cls == "tree":
        w.cstring(init["tree"]["treeType"])
    elif cls == "wall":
        w.floats((init["wall"]["length"], init["wall"]["life"]))
        w.cstring(init["wall"]["wallType"])
    elif cls == "sphere-trigger":
        w.f32(init["sphereTrigger"]["radius"])


DEFINED = frozenset({wrd.OID_UNIT, wrd.OID_BUILDING, wrd.OID_SQUAD, wrd.OID_FEATURE, wrd.OID_HAZARD})


def thing_class(oid: int) -> str:
    if oid in (wrd.OID_UNIT, wrd.OID_BUILDING, wrd.OID_FEATURE, wrd.OID_HAZARD):
        return "base"
    if oid in DEFINED or oid in wrd.SPAWNTHING_MAKES:
        return wrd.INIT_CLASS.get(oid, "base")
    raise wrd.DecodeError(f"object id {oid} is not one SpawnThing makes (LoadWorld would not read its record)")


# ------------------------------------------------------------------------------------------------- world bodies
def read_world_model(body: bytes) -> dict:
    """Every field of a world body in CWorld::LoadWorld's order (the read order of wrd.parse_world_body)."""
    r = wrd.Reader(body)
    version = r.unpack("H")[0]
    if not 43 <= version <= 50:
        raise wrd.DecodeError(f"world version {version} outside 43..50")
    hversion, unused1, unused2 = r.unpack("iii")
    header = {"headerVersion": hversion, "unused": [unused1, unused2],
              "battleEngineConfigurations": [r.lstring() for _ in range(r.count())]}
    if hversion >= 2:
        header["v2Words"] = list(r.unpack("iii"))
    if hversion >= 3:
        header["worldType"] = r.i32()
    model = {"format": MODEL_FORMAT, "version": version, "header": header, "baseLevel": r.i32(), "scripts": []}
    for _ in range(r.count()):
        name = r.lstring("i")
        code = read_code(r)
        model["scripts"].append({"name": name, "code": code, "trailer": r.take(10).hex()})
    model["mapNumber"] = r.i32()
    model["namedMeshes"] = [r.lstring("B") for _ in range(r.count())]
    things = []
    for _ in range(r.count("H")):
        oid = r.i32()
        thing = {"oid": oid, "kind": wrd.OID_NAMES.get(oid, f"oid-{oid}"),
                 "init": read_init(r, version, thing_class(oid))}
        if oid in DEFINED:
            thing["definition"] = r.lstring()
            thing["diesOn"] = r.i32()
        things.append(thing)
    model["things"] = things
    groups = []
    for _ in range(r.count("h")):
        y0, x0, y1, x1 = (f32_in(r) for _ in range(4))
        groups.append({"y0": y0, "x0": x0, "y1": y1, "x1": x1, "count": r.i32(), "treeType": r.lstring(),
                       "seed": r.i32()})
    model["treeGroups"] = groups
    model["treeTypes"] = []
    for _ in range(r.count()):
        name = r.lstring()
        positions = []
        for _ in range(r.count()):
            positions.append([f32_in(r), f32_in(r), r.i32()])
        model["treeTypes"].append({"name": name, "positions": positions})
    iv = r.unpack("H")[0]
    if iv not in (0, 1):
        raise wrd.DecodeError(f"influence map version {iv}")
    nodes = r.count()
    node_bytes = r.take(nodes * (12 if iv == 0 else 16))
    links = r.count()
    link_bytes = r.take(links * (8 if iv == 0 else 12))
    model["influenceMap"] = {"version": iv, "nodes": nodes, "nodeBytes": blob(node_bytes), "links": links,
                             "linkBytes": blob(link_bytes)}
    paths = []
    for _ in range(r.count("h")):
        name = r.lstring()
        paths.append({"name": name, "slots": [r.unpack("h")[0] for _ in range(r.count())]})
    model["waypointPaths"] = paths
    model["timings"] = {"oldF": f32_in(r), "oldG": f32_in(r), "oldH": f32_in(r), "preRun": f32_in(r),
                        "pan": f32_in(r), "sGrade": r.i32(), "dGrade": r.i32(), "timeLimit": f32_in(r),
                        "fullScoreTime": f32_in(r), "percentageScoreTime": f32_in(r), "scorePercentage": f32_in(r)}
    if 45 <= version < 48:
        a, b, c = r.unpack("iii")
        model["legacyTimings"] = [a, b, c, f32_in(r), f32_in(r)]
    if version >= 47:
        grids = []
        for _ in range(3):
            gv = r.i32()
            grids.append({"version": gv, "data": blob(r.take({1: 0x8000, 2: 0x2000}.get(gv, 0)))})
        model["occupancyGrids"] = grids
        if version < 50:
            model["legacyGridWords"] = list(r.unpack("5i"))
    if version >= 49:
        model["levelStartTime"] = f32_in(r)
    if r.pos != len(body):
        raise wrd.DecodeError(f"world body has {len(body) - r.pos} unread bytes")
    return model


def write_world_body(model: dict) -> bytes:
    """The inverse of read_world_model."""
    if model.get("format") != MODEL_FORMAT:
        raise EncodeError(f"not a {MODEL_FORMAT} model")
    version = model["version"]
    if not 43 <= version <= 50:
        raise EncodeError(f"world version {version} outside 43..50 (LoadWorld refuses it)")
    w = Writer()
    w.pack("H", version)
    h = model["header"]
    w.pack("iii", h["headerVersion"], *h["unused"])
    w.i32(len(h["battleEngineConfigurations"]))
    for name in h["battleEngineConfigurations"]:
        w.lstring(name)
    if h["headerVersion"] >= 2:
        w.pack("iii", *h["v2Words"])
    if h["headerVersion"] >= 3:
        w.i32(h["worldType"])
    w.i32(model["baseLevel"])
    w.i32(len(model["scripts"]))
    for s in model["scripts"]:
        w.lstring(s["name"], "i")
        write_code(w, s["code"])
        trailer = bytes.fromhex(s["trailer"])
        if len(trailer) != 10:
            raise EncodeError("a script trailer is 10 bytes")
        w.raw(trailer)
    w.i32(model["mapNumber"])
    w.i32(len(model["namedMeshes"]))
    for name in model["namedMeshes"]:
        w.lstring(name, "B")
    things = model["things"]
    if len(things) > 1000:
        raise EncodeError("LoadWorld's things[] holds 1000 records")
    w.pack("H", len(things))
    for t in things:
        oid = t["oid"]
        w.i32(oid)
        write_init(w, t["init"], version, thing_class(oid))
        if oid in DEFINED:
            w.lstring(t["definition"])
            w.i32(t["diesOn"])
    w.pack("h", len(model["treeGroups"]))
    for g in model["treeGroups"]:
        w.floats((g["y0"], g["x0"], g["y1"], g["x1"]))
        w.i32(g["count"])
        w.lstring(g["treeType"])
        w.i32(g["seed"])
    w.i32(len(model["treeTypes"]))
    for tt in model["treeTypes"]:
        w.lstring(tt["name"])
        w.i32(len(tt["positions"]))
        for x, y, k in tt["positions"]:
            w.floats((x, y))
            w.i32(k)
    im = model["influenceMap"]
    w.pack("H", im["version"])
    nodes, links = unblob(im["nodeBytes"]), unblob(im["linkBytes"])
    if len(nodes) != im["nodes"] * (12 if im["version"] == 0 else 16) or \
            len(links) != im["links"] * (8 if im["version"] == 0 else 12):
        raise EncodeError("influence map counts do not match its blobs")
    w.i32(im["nodes"])
    w.raw(nodes)
    w.i32(im["links"])
    w.raw(links)
    w.pack("h", len(model["waypointPaths"]))
    for p in model["waypointPaths"]:
        w.lstring(p["name"])
        w.i32(len(p["slots"]))
        for s in p["slots"]:
            w.pack("h", s)
    t = model["timings"]
    w.floats((t["oldF"], t["oldG"], t["oldH"], t["preRun"], t["pan"]))
    w.pack("ii", t["sGrade"], t["dGrade"])
    w.floats((t["timeLimit"], t["fullScoreTime"], t["percentageScoreTime"], t["scorePercentage"]))
    if 45 <= version < 48:
        lt = model["legacyTimings"]
        w.pack("iii", *lt[:3])
        w.floats(lt[3:])
    if version >= 47:
        if len(model["occupancyGrids"]) != 3:
            raise EncodeError("a world has exactly three occupancy grids")
        for g in model["occupancyGrids"]:
            data = unblob(g["data"])
            if len(data) != {1: 0x8000, 2: 0x2000}.get(g["version"], 0):
                raise EncodeError(f"occupancy grid version {g['version']} with {len(data)} bytes")
            w.i32(g["version"])
            w.raw(data)
        if version < 50:
            w.pack("5i", *model["legacyGridWords"])
    if version >= 49:
        w.f32(model["levelStartTime"])
    return w.bytes()


# ---------------------------------------------------------------------------------------------- level archives
def read_members(source: bytes) -> list[bytes]:
    """The packed members of a .aya: [u32 length][zlib stream] (CDXMemBuffer::ReadBlock), compressed bytes kept."""
    if not source or len(source) > MAX_ARCHIVE_BYTES:
        raise EncodeError("archive is empty or exceeds the compressed-byte limit")
    members, at = [], 0
    while at < len(source):
        if len(members) >= MAX_ARCHIVE_MEMBERS:
            raise EncodeError("archive exceeds the member-count limit")
        if at + 4 > len(source):
            raise EncodeError("truncated .aya member header")
        size = struct.unpack_from("<I", source, at)[0]
        if not 0 < size <= PACK_BUFFER_SIZE or at + 4 + size > len(source):
            raise EncodeError(f"implausible .aya member length {size} at {at}")
        members.append(source[at + 4:at + 4 + size])
        at += 4 + size
    return members


def chunks(data: bytes, start: int = 0, end: int | None = None):
    """(tag, payload offset, size) for each chunk of a tag stream (CChunkReader::GetNext)."""
    end = len(data) if end is None else end
    if not 0 <= start <= end <= len(data):
        raise EncodeError("invalid chunk-stream boundaries")
    at = start
    while at < end:
        if at + 8 > end:
            raise EncodeError(f"truncated chunk header at {at}")
        tag, size = struct.unpack_from("<4sI", data, at)
        if at + 8 + size > end:
            raise EncodeError(f"chunk {tag!r} at {at} overruns its parent")
        yield tag.decode("latin-1"), at + 8, size
        at += 8 + size


def level_worlds(raw: bytes) -> dict:
    """WRES/WRLD of an inflated level archive: WDAT's two level numbers (and their offset) and the world bodies."""
    for tag, at, size in chunks(raw):
        if tag != "WRES":
            continue
        for wtag, wat, wsize in chunks(raw, at, at + size):
            if wtag != "WRLD":
                continue
            out = {"bodies": {}}
            for ktag, kat, ksize in chunks(raw, wat, wat + wsize):
                if ktag == "WDAT":
                    if ksize < 8:
                        raise EncodeError("WDAT is shorter than its two level numbers")
                    out["wdatOffset"] = kat
                    out["baseLevel"], out["realLevel"] = struct.unpack_from("<ii", raw, kat)
                elif ktag in ("BSWD", "RLWD"):
                    out["bodies"][ktag] = raw[kat:kat + ksize]
            return out
    raise EncodeError("no WRES/WRLD chunk")


def inflate(members: list[bytes]) -> list[bytes]:
    """Bound every member and the total before materializing a complete archive."""
    if not members or len(members) > MAX_ARCHIVE_MEMBERS:
        raise EncodeError("archive is empty or exceeds the member-count limit")
    blocks = []
    packed_total = inflated_total = 0
    for index, member in enumerate(members):
        packed_total += len(member) + 4
        if not 0 < len(member) <= PACK_BUFFER_SIZE or packed_total > MAX_ARCHIVE_BYTES:
            raise EncodeError(f"compressed archive/member limit at member {index}")
        remaining = MAX_ARCHIVE_INFLATED_BYTES - inflated_total
        limit = min(MAX_INFLATED_MEMBER_BYTES, remaining)
        decoder = zlib.decompressobj()
        try:
            block = decoder.decompress(member, limit + 1)
        except zlib.error as error:
            raise EncodeError(f"invalid zlib data in member {index}") from error
        if len(block) > limit or decoder.unconsumed_tail:
            raise EncodeError(f"inflated archive/member limit at member {index}")
        if not decoder.eof:
            raise EncodeError(f"truncated zlib stream in member {index}")
        if decoder.unused_data:
            raise EncodeError(f"trailing data after zlib stream in member {index}")
        inflated_total += len(block)
        blocks.append(block)
    return blocks


def shadow_archive(source: bytes, wdat_level: int = NO_LEVEL) -> bytes:
    """A copy of a level archive whose WDAT names wdat_level as the real world's level. Only the member(s) holding
    those four bytes are recompressed; every other member keeps its original compressed bytes and every member its
    inflated length, so the stream framing and the block boundaries CDXMemBuffer reads are unchanged."""
    members = read_members(source)
    blocks = inflate(members)
    raw = b"".join(blocks)
    worlds = level_worlds(raw)
    at = worlds["wdatOffset"] + 4  # mWorldLevel follows mBaseWorldLevel (CWorld::Deserialize)
    patched = bytearray(raw)
    struct.pack_into("<i", patched, at, wdat_level)
    out, pos = bytearray(), 0
    for member, block in zip(members, blocks):
        lo, hi = pos, pos + len(block)
        pos = hi
        if hi <= at or lo >= at + 4:
            data = member
        else:
            data = zlib.compress(bytes(patched[lo:hi]), 9)
            if len(data) > PACK_BUFFER_SIZE:
                raise EncodeError("a recompressed member exceeds the game's pack buffer")
        out += struct.pack("<I", len(data)) + data
    return bytes(out)


# ------------------------------------------------------------------------------------------------------ helpers
def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_retail(path: Path) -> bytes:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0))
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise EncodeError(f"archive is not a regular file: {path}")
        with os.fdopen(fd, "rb", closefd=False) as f:
            data = f.read(MAX_ARCHIVE_BYTES + 1)
        if len(data) > MAX_ARCHIVE_BYTES:
            raise EncodeError(f"archive exceeds the compressed-byte limit: {path}")
        return data
    finally:
        os.close(fd)


def level_archives(game: Path) -> dict[int, Path]:
    folder = next((p for p in game.joinpath("data").iterdir() if p.name.casefold() == "resources"), None) \
        if game.joinpath("data").is_dir() else None
    if folder is None:
        raise SystemExit(f"{game}: no data/resources folder")
    return {int(m.group(1)): p for p in sorted(folder.iterdir()) if (m := LEVEL_ARCHIVE_RE.match(p.name))}


def publish_fresh(output_root: Path, game: Path, files: list[tuple[Path, bytes]]) -> None:
    """Publish only fresh output names while holding the directory chain and protecting the game.

    The preflight avoids ordinary partial sets on an existing-name collision; the held-directory,
    no-replace publication remains the authority if a path changes after preflight.
    """
    output_root = Path(os.path.abspath(output_root))
    game = Path(os.path.abspath(game))
    destinations = [(Path(os.path.abspath(path)), data) for path, data in files]
    if len({os.path.normcase(os.fspath(path)) for path, _ in destinations}) != len(destinations):
        raise UnsafeGeneratedOutputError("two world outputs would use the same file name")
    with SecuredOutputRoot(output_root, protected_sources=(game,)) as output:
        for path, _ in destinations:
            output.destination(path)
            if os.path.lexists(path):
                raise UnsafeGeneratedOutputError(f"fresh generated-output destination already exists: {path}")
        for path, data in destinations:
            output.atomic_write_new_bytes(path, data)


def world_names(worlds: dict) -> dict[str, int]:
    """The loose file each body loads from: CWorld::Load's data\\worlds\\world%03d.wrd for its level."""
    names = {"RLWD": worlds["realLevel"]}
    if "BSWD" in worlds["bodies"]:
        names["BSWD"] = worlds["baseLevel"]
    return names


def cmd_verify(args) -> int:
    archives = level_archives(args.game)
    bodies = failures = 0
    for level, path in archives.items():
        worlds = level_worlds(b"".join(inflate(read_members(read_retail(path)))))
        for tag, body in sorted(worlds["bodies"].items()):
            bodies += 1
            try:
                again = write_world_body(json.loads(json.dumps(read_world_model(body))))
            except (wrd.DecodeError, EncodeError, struct.error) as error:
                failures += 1
                print(f"{level:03d} {tag}: FAILED {error}")
                continue
            if again != body:
                failures += 1
                print(f"{level:03d} {tag}: DIFFERS ({len(body)} -> {len(again)} bytes)")
            elif args.verbose:
                print(f"{level:03d} {tag}: {len(body)} bytes identical, sha256 {sha256(body)[:16]}")
    print(f"world bodies: {bodies} in {len(archives)} level archives; byte-identical round trips: "
          f"{bodies - failures}; failures: {failures}")
    return 0 if bodies and not failures else 1


def cmd_extract(args) -> int:
    archives = level_archives(args.game)
    out = Path(os.path.abspath(args.out))
    worlds = level_worlds(b"".join(inflate(read_members(read_retail(archives[args.level])))))
    files = []
    messages = []
    for tag, level in world_names(worlds).items():
        body = worlds["bodies"][tag]
        model = read_world_model(body)
        files.append((out / f"world{level:03d}.json", (json.dumps(model, indent=1) + "\n").encode("utf-8")))
        files.append((out / f"world{level:03d}.wrd", write_world_body(model)))
        messages.append(f"{tag} -> world{level:03d}.wrd ({len(body)} bytes, sha256 {sha256(body)}) and .json")
    publish_fresh(out, args.game, files)
    for message in messages:
        print(message)
    return 0


def cmd_encode(args) -> int:
    body = write_world_body(json.loads(args.model.read_text()))
    out = Path(os.path.abspath(args.out))
    publish_fresh(out.parent, args.game, [(out, body)])
    print(f"{args.out}: {len(body)} bytes, sha256 {sha256(body)}")
    return 0


def cmd_stage(args) -> int:
    archives = level_archives(args.game)
    user = Path(os.path.abspath(args.user))
    source_path = archives[args.level]
    source = read_retail(source_path)
    worlds = level_worlds(b"".join(inflate(read_members(source))))
    worlds_dir = user / "data" / "worlds"
    files = []
    report = {"level": args.level, "archive": source_path.name, "archiveSha256": sha256(source), "files": {}}
    for tag, level in world_names(worlds).items():
        body = worlds["bodies"][tag]
        if tag == "RLWD" and args.world:
            data = write_world_body(json.loads(args.world.read_text()))
        else:
            data = write_world_body(read_world_model(body))
            if data != body:
                raise SystemExit(f"{tag}: the encoder did not reproduce the archive's body")
        dest = worlds_dir / f"world{level:03d}.wrd"
        files.append((dest, data))
        report["files"][f"data/worlds/{dest.name}"] = {"from": tag, "bytes": len(data), "sha256": sha256(data),
                                                       "identicalToArchive": data == body}
    shadow = shadow_archive(source)
    res_dir = user / "data" / "resources"
    files.append((res_dir / source_path.name, shadow))
    report["files"][f"data/resources/{source_path.name}"] = {"wdatRealLevel": NO_LEVEL, "bytes": len(shadow),
                                                             "sha256": sha256(shadow)}
    publish_fresh(user, args.game, files)
    print(json.dumps(report, indent=1))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"), required="BEA_GAME" not in os.environ)
    v.add_argument("--verbose", action="store_true")
    e = sub.add_parser("extract")
    e.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"), required="BEA_GAME" not in os.environ)
    e.add_argument("--level", type=int, required=True)
    e.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("encode")
    c.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"), required="BEA_GAME" not in os.environ)
    c.add_argument("model", type=Path)
    c.add_argument("out", type=Path)
    s = sub.add_parser("stage")
    s.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"), required="BEA_GAME" not in os.environ)
    s.add_argument("--level", type=int, required=True)
    s.add_argument("--user", type=Path, required=True, help="the port's user folder (BEA_USER_DIR) for the run")
    s.add_argument("--world", type=Path, help="an edited model for the level's own (RLWD) world")
    args = ap.parse_args(argv)
    return {"verify": cmd_verify, "extract": cmd_extract, "encode": cmd_encode, "stage": cmd_stage}[args.command](args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (EncodeError, UnsafeGeneratedOutputError) as error:
        print(f"world encoder: {error}", file=sys.stderr)
        sys.exit(2)
