#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Generate Battle Engine Aquila's cut level 888, a Fenrir-versus-Venturer flagship duel, as a CE mod from the player's own PC game folder.

The PC game has no level archive for 888 (CGame::IsMultiplayer takes levels 850 to 899 as multiplayer, the game's own multiplayer
levels are 850 to 866, and the mission-script sources left for 888 never declare a winner). This tool makes the level on the player's
machine, from files the player already owns, and writes a CE mod folder that the loader admits (the loader's rule for adding a level
archive is in tools/world_mod_stage.py and in the Mods section of the CE README):

    <out>/<id>/mod.json
    <out>/<id>/data/resources/888_res_PC.aya   a level archive: the flat-sea versus level 857's terrain and world (the DONOR), the
                                               texture and mesh descriptors the two flagships need and 857 lacks (copied from the
                                               archives that hold them), and a new world with a Venturer, a Fenrir and a level script
    <out>/<id>/data/default physics.dat        the game's file with ONE edit: the unit definition "Fenrir Multiplayer", which no level
                                               uses, names the mesh boss-fenrir.msh instead of a file the PC game never had

Nothing is downloaded and no game byte is stored in this repository: the tool reads the player's folder, the output is private to the
player, and what is committed is only the recipe (this file) and the three short scripts it authors. The scripts are written
here, not copied: the unit scripts post an event from died(), and the level script declares the match won when one of them arrives.
No script text of the game is read. The recipe's pins (PINS below) are the SHA-256 of the files it was checked against; a file with
another hash is reported as a warning and the structural checks still decide, or --strict-pins turns the warning into a refusal.

Everything is computed, not listed: the units' mesh closure is read from default physics.dat (a unit, its components, the units its
spawners make, with BASED_ON applied in node order), each mesh's textures are read from its loose file, and the descriptors the donor
lacks are looked for in SOURCES. The gate (`gate`) rebuilds twice and compares, checks the closure against the finished archive, the
archive against the loader's structure walk (world_mod_stage.check_level_archive), the physics file against its original, the
world's header against the player's worldheaders.dat, and that the compiled scripts hold only the strings authored here.

    level888_build.py build   --game GAME --out PARENT --ce-min 0.1.13 [--id flagship-duel] [--lives 3] [--ai-state N] [--strict-pins]
    level888_build.py gate    --game GAME [--strict-pins]
    level888_build.py closure --game GAME

The mod REPLACES data/default physics.dat, so it conflicts with any other mod that replaces it (the later one in ce.ini wins). Mods
load on Linux only for now, and are off in replays, recordings, probes, virtual clocks, pilots and network sessions. What the level
plays like (the ships' placement, whether they fight, the lives) is a recipe constant below, judged by playing it, not by this tool.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import os
import re
import stat
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import msl_compile as msl  # noqa: E402
import world_mod_stage as stage  # noqa: E402
import world_resources_decode as wrd  # noqa: E402
import world_resources_encode as enc  # noqa: E402
import worldheaders_decode as headers  # noqa: E402
from aya_cross_platform_compare import logical_key, normalize_asset_name  # noqa: E402

LEVEL = 888
DONOR = 857                      # a flat-sea versus level: its terrain, features and start points become 888's
SOURCES = (731, 732, 741, 742)   # archives that hold the Fenrir's descriptors, looked through in this order
VENTURER = "Aircarrier Multiplayer"
FENRIR = "Fenrir Multiplayer"
FENRIR_FILELESS_MESH = "fenrir-multiplayer.msh"   # the mesh FENRIR names; the PC game has no file for it
FENRIR_MESH = "boss-fenrir.msh"                    # the Fenrir the PC game does have, which FENRIR is made to use
MOD_ID = "flagship-duel"
ARCHIVE_PATH = "data/resources/888_res_PC.aya"
PHYSICS_PATH = "data/default physics.dat"
WORLDHEADERS_PATH = "data/worldheaders.dat"
DEFAULT_LIVES = 3

# Placement of the two ships: x, y, z, yaw (radians) and allegiance. Recipe constants, tuned by playing the level.
VENTURER_PLACEMENT = {"position": (256.0, 420.0, -60.0), "yaw": math.pi, "allegiance": 0}
FENRIR_PLACEMENT = {"position": (256.0, 100.0, -60.0), "yaw": 0.0, "allegiance": 1}

# SHA-256 of the files this recipe was checked against (the game's PC release). Keys are lowercase game-relative paths.
PINS = {
    "data/resources/857_res_pc.aya": "aedf1e01c9b1c64edc7c01bbe34ac01e63c0542f1e0aef285579259a96215929",
    "data/resources/731_res_pc.aya": "2fe1a042359b844f07855509630a1340ce7921ebc448bb6db8d4d54918fac6ef",
    "data/resources/732_res_pc.aya": "5adf783c5487688f7d8d088a6b82fd62bc379b24943a36b35051e2cb52e7c459",
    "data/resources/741_res_pc.aya": "57fb70fa70b9fb39a7c1a381543e5ab3c7df973f6896f06eb2a16045e6f197aa",
    "data/resources/742_res_pc.aya": "9282408ab8cd1db9fcc7398eaad793b0cc72ee1709ac975193f4196252fdf9ee",
    "data/default physics.dat": "e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14",
    "data/worldheaders.dat": "34f2f45027a165fedde0e306b61fbabf64332724ced1e7a763103248fea07524",
}

LIMIT_ARCHIVE = 64 << 20
LIMIT_SMALL = 16 << 20
BLOCK = 1 << 20
MESH_DESCRIPTOR_BYTES, TEXT_DESCRIPTOR_BYTES, MESH_ID_OFFSET = 325, 372, 316
KEPT_THINGS = ("feature", "start", "spawn-point")   # what the donor's world keeps; its waypoint, spawner and level script are dropped

# default physics.dat: statement kinds and the field ids the closure follows (the decompilation's physics value enums)
UNIT_KIND, SPAWNER_KIND, COMPONENT_KIND = 1, 5, 7
KIND_NAMES = {UNIT_KIND: "unit", SPAWNER_KIND: "spawner", COMPONENT_KIND: "component"}
BASED_ON_FIELD = {UNIT_KIND: 39, SPAWNER_KIND: 10, COMPONENT_KIND: 10}
MESH_FIELD = {UNIT_KIND: 9, COMPONENT_KIND: 3}
COMPONENT_FIELD = {UNIT_KIND: 27}
SPAWNER_FIELD = {UNIT_KIND: 18, COMPONENT_KIND: 19}
UNIT_FIELD = {SPAWNER_KIND: 1}


class BuildError(ValueError):
    """The recipe cannot be applied to this game folder, or an option is out of range."""


# ---- the authored scripts ----------------------------------------------------------------------------------------------
# Written for this tool. A flagship's died() reports its destruction to the level script by an event name of this tool's own; the
# level script waits for that name and declares the other side the winner. SetAIState(4) is AI_ONF (EAIState in thing.h: AI_ON,
# AI_OFF, AI_NORMAL, AI_DEFENSIVE, AI_ONF).
AI_STATES = range(0, 5)
DESTROYED = "Flagship {} Destroyed"          # the event a flagship posts when it is destroyed; the level script handles both


def script_sources(lives: int = DEFAULT_LIVES, ai_state: int | None = None) -> dict[str, str]:
    """The three scripts of the level, as source text."""
    if type(lives) is not int or not 1 <= lives <= 9:
        raise BuildError("lives is a whole number from 1 to 9")
    if ai_state is not None and (type(ai_state) is not int or ai_state not in AI_STATES):
        raise BuildError("ai-state is a whole number from 0 to 4 (EAIState), or unset")
    sources = {}
    for ship in ("Fenrir", "Venturer"):
        text = (f"// Level 888, the {ship} flagship: once destroyed it tells the level script, by name.\n"
                f"died()\n{{\n\tPostEvent(\"{DESTROYED.format(ship)}\");\n}}\n")
        if ai_state is not None:
            text += f"\nevent(\"game playing\")\n{{\n\tSetAIState({ai_state});\n}}\n"
        sources[ship] = text
    sources["world888script"] = (
        "// Level 888, the level script: the Venturer is player 1's flagship and the Fenrir is player 2's.\n"
        f"init()\n{{\n\tSetPlayerLives(1, {lives});\n\tSetPlayerLives(2, {lives});\n}}\n\n"
        f"event(\"{DESTROYED.format('Fenrir')}\")\n{{\n\tMPDeclarePlayerWon(1);\n}}\n\n"
        f"event(\"{DESTROYED.format('Venturer')}\")\n{{\n\tMPDeclarePlayerWon(2);\n}}\n")
    return sources


def _no_includes(path: str) -> str:
    raise msl.MissingInclude(path)


def compile_scripts(sources: dict[str, str]) -> list[dict]:
    """The compiled records, in name order, sharing one constant counter as one compile session does."""
    records, const_start = [], 0
    for name in sorted(sources, key=str.lower):
        try:
            record = msl.compile_script(name, sources[name], _no_includes, const_start, 0)
        except msl.CompileError as error:
            raise BuildError(f"the authored script {name} does not compile: {error}") from error
        numbers = [int(symbol["name"][len("const data"):]) for symbol in record["code"]["symbols"]
                   if symbol["name"].startswith("const data")]
        const_start = max(numbers) + 1 if numbers else const_start
        records.append(record)
    return records


def authored_strings(sources: dict[str, str]) -> set[str]:
    """Every string constant the authored sources hold, for the gate's check that nothing else got into the compiled scripts."""
    return {text for source in sources.values() for text in re.findall(r'"([^"]*)"', source)}


# ---- the player's game folder ------------------------------------------------------------------------------------------
def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Install:
    """Read-only access to the player's game folder. A file is found without regard to case, the file itself is opened without
    following a link, read to a bound and recorded by SHA-256; a pinned file with another hash is a warning (or, with strict,
    a refusal)."""

    def __init__(self, game: Path, *, strict_pins: bool = False) -> None:
        self.root = Path(game)
        self.strict = strict_pins
        self.reads: dict[str, dict] = {}
        self.warnings: list[str] = []
        self._cache: dict[str, bytes] = {}

    def find(self, rel: str) -> Path | None:
        at = self.root
        for part in rel.split("/"):
            try:
                names = sorted(entry.name for entry in os.scandir(at) if entry.name.lower() == part.lower())
            except OSError:
                return None
            if not names:
                return None
            at = at / names[0]
        return at

    def has(self, rel: str) -> bool:
        found = self.find(rel)
        return found is not None and found.is_file()

    def read(self, rel: str, limit: int) -> bytes:
        key = rel.lower()
        if key in self._cache:
            return self._cache[key]
        found = self.find(rel)
        if found is None:
            raise BuildError(f"{rel}: the game folder has no such file")
        try:
            fd = os.open(found, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        except OSError as error:
            raise BuildError(f"{rel}: cannot be opened ({error.strerror})") from error
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise BuildError(f"{rel}: not a regular file")
            with os.fdopen(fd, "rb", closefd=False) as handle:
                data = handle.read(limit + 1)
        finally:
            os.close(fd)
        if len(data) > limit:
            raise BuildError(f"{rel}: larger than {limit} bytes")
        digest = sha256(data)
        self.reads[rel] = {"size": len(data), "sha256": digest}
        pin = PINS.get(key)
        if pin is not None and pin != digest:
            message = (f"{rel}: SHA-256 {digest[:16]}... is not the file this recipe was checked against ({pin[:16]}...); "
                       f"the structural checks decide")
            if self.strict:
                raise BuildError(message + " (--strict-pins)")
            self.warnings.append(message)
        self._cache[key] = data
        return data

    def level_archive(self, level: int) -> bytes:
        return self.read(f"data/resources/{level:03d}_res_PC.aya", LIMIT_ARCHIVE)


# ---- default physics.dat -----------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Node:
    field: int
    value: bytes
    at: int    # offset of the node's field word


@dataclass(frozen=True)
class Statement:
    kind: int
    name: str
    at: int    # offset of the statement's type word; the size word follows
    size: int
    nodes: tuple[Node, ...]


def parse_physics(data: bytes) -> list[Statement]:
    """default physics.dat as UPhysicsManager::Reload reads it: a 0x12 header word, then statements (type, size, name, nodes of
    field id, length, value and a link word that is -1 on the last), then -1. Refuses what does not end exactly."""
    if len(data) < 6 or struct.unpack_from("<H", data, 0)[0] != 0x12:
        raise BuildError("default physics.dat is not the framing this recipe knows (header word 0x12)")
    out, at = [], 2
    while True:
        if at + 4 > len(data):
            raise BuildError("default physics.dat has no terminal marker")
        if struct.unpack_from("<i", data, at)[0] == -1:
            at += 4
            break
        if len(out) >= 10_000 or at + 8 > len(data):
            raise BuildError("default physics.dat: a statement header is cut or there are too many statements")
        start = at
        kind, size = struct.unpack_from("<II", data, at)
        at += 8
        end = data.find(b"\0", at)
        if end < 0:
            raise BuildError("default physics.dat: a statement name is not terminated")
        name = data[at:end].decode("latin-1")
        at = end + 1
        nodes = []
        while True:
            if len(nodes) >= 1024 or at + 8 > len(data):
                raise BuildError(f"default physics.dat: statement {name!r} has bad node framing")
            field, length = struct.unpack_from("<II", data, at)
            if length > 1 << 20 or at + 8 + length + 4 > len(data):
                raise BuildError(f"default physics.dat: statement {name!r} has a node past the end of the file")
            nodes.append(Node(field, data[at + 8:at + 8 + length], at))
            at += 8 + length
            link = struct.unpack_from("<i", data, at)[0]
            at += 4
            if link == -1:
                break
            if link != 0:
                raise BuildError(f"default physics.dat: statement {name!r} has a link word other than 0 or -1")
        out.append(Statement(kind, name, start, size, tuple(nodes)))
    if at != len(data):
        raise BuildError("default physics.dat has bytes after its terminal marker")
    return out


def cstring(value: bytes, what: str) -> str:
    """A node value read as the loader reads a string: to its NUL, printable ASCII."""
    end = value.find(b"\0")
    text = value[:end if end >= 0 else len(value)]
    if end < 0 or not text or any(not 0x20 <= byte < 0x7F for byte in text):
        raise BuildError(f"default physics.dat: {what} is not a printable string")
    return text.decode("ascii")


class Physics:
    """The unit, spawner and component definitions, looked up by exact name as the game does (strcmp), first definition winning."""

    def __init__(self, data: bytes) -> None:
        self.statements = parse_physics(data)
        self.by: dict[tuple[int, str], Statement] = {}
        for statement in self.statements:
            self.by.setdefault((statement.kind, statement.name), statement)

    def values(self, kind: int, name: str, trail: tuple = ()) -> tuple[str | None, list[str], list[str], list[str]]:
        """(mesh, components, spawners, units) of a definition with BASED_ON applied where it stands among the nodes: the last mesh
        wins, the lists add up."""
        statement = self.by.get((kind, name))
        if statement is None:
            raise BuildError(f"default physics.dat has no {KIND_NAMES[kind]} named {name!r}")
        if (kind, name) in trail:
            raise BuildError(f"default physics.dat: {KIND_NAMES[kind]} {name!r} is based on itself")
        mesh: str | None = None
        components: list[str] = []
        spawners: list[str] = []
        units: list[str] = []
        for node in statement.nodes:
            what = f"{KIND_NAMES[kind]} {name!r} field {node.field}"
            if node.field == BASED_ON_FIELD[kind]:
                base = self.values(kind, cstring(node.value, what), trail + ((kind, name),))
                mesh = base[0] if base[0] is not None else mesh
                components += base[1]
                spawners += base[2]
                units += base[3]
            elif node.field == MESH_FIELD.get(kind):
                mesh = cstring(node.value, what)
            elif node.field == COMPONENT_FIELD.get(kind):
                components.append(cstring(node.value, what))
            elif node.field == SPAWNER_FIELD.get(kind):
                spawners.append(cstring(node.value, what))
            elif node.field == UNIT_FIELD.get(kind):
                units.append(cstring(node.value, what))
        return mesh, components, spawners, units

    def closure(self, unit: str) -> tuple[list[str], list[str]]:
        """(the unit definitions, the mesh names) a unit builds on: its own mesh, its components' meshes, and everything the
        spawners of the unit and of its components can make, in discovery order."""
        units: list[str] = []
        meshes: list[str] = []

        def add_mesh(name: str | None) -> None:
            if name and name.lower() not in (known.lower() for known in meshes):
                meshes.append(name)

        def visit(name: str) -> None:
            if name in units:
                return
            units.append(name)
            mesh, components, spawners, _ = self.values(UNIT_KIND, name)
            add_mesh(mesh)
            for component in components:
                cmesh, _c, cspawners, _u = self.values(COMPONENT_KIND, component)
                add_mesh(cmesh)
                spawners = spawners + cspawners
            for spawner in spawners:
                for made in self.values(SPAWNER_KIND, spawner)[3]:
                    visit(made)

        visit(unit)
        return units, meshes


def redirect_unit_mesh(data: bytes, unit: str, old: str, new: str) -> bytes:
    """data with the one mesh node of the unit definition `unit` renamed from `old` to `new`. Only that node's length word and the
    statement's size word (the sum the loader ignores but the file keeps honest) change by the difference; every other byte stays."""
    statements = [s for s in parse_physics(data) if s.kind == UNIT_KIND and s.name == unit]
    if not statements:
        raise BuildError(f"default physics.dat defines no unit {unit!r}")
    statement = statements[0]
    nodes = [n for n in statement.nodes if n.field == MESH_FIELD[UNIT_KIND]]
    if len(nodes) != 1:
        raise BuildError(f"unit {unit!r} does not have exactly one mesh node")
    node = nodes[0]
    if node.value.lower() != old.encode("ascii").lower() + b"\0":
        raise BuildError(f"unit {unit!r} names the mesh {cstring(node.value, 'its mesh')!r}, not {old!r}")
    value = new.encode("ascii") + b"\0"
    out = bytearray(data)
    struct.pack_into("<I", out, statement.at + 4, statement.size + len(value) - len(node.value))
    struct.pack_into("<I", out, node.at + 4, len(value))
    out[node.at + 8:node.at + 8 + len(node.value)] = value
    result = bytes(out)
    check = Physics(result)
    if check.values(UNIT_KIND, unit)[0] != new:
        raise BuildError("the redirected physics file did not read back")
    return result


# ---- meshes and textures -----------------------------------------------------------------------------------------------
def loose_mesh_path(name: str) -> str:
    return f"data/resources/meshes/m_{name}.aya"


def texture_names(stream: bytes) -> list[str]:
    """The texture names a loose mesh file (an unpacked CMSH) asks for, in file order: the 128-byte name of each TEXB record in
    its MSHT list, behind the CMST bindings (CMesh::Deserialize; CMesh::FindTexture looks the names up)."""
    if len(stream) < 388 or stream[:4] != b"CMSH" or stream[380:384] != b"CMST":
        raise BuildError("a loose mesh file is not a CMSH stream this recipe reads")
    count = struct.unpack_from("<I", stream, 12)[0]
    if count > 1024 or struct.unpack_from("<I", stream, 384)[0] != 36 * count:
        raise BuildError("a loose mesh file's texture count and CMST bindings disagree")
    at, names = 388 + 36 * count, []
    for _ in range(count):
        if at + 16 > len(stream) or stream[at:at + 4] != b"MSHT" or stream[at + 8:at + 12] != b"TEXB":
            raise BuildError("a loose mesh file's texture list is not MSHT/TEXB records")
        msht, texb = struct.unpack_from("<I", stream, at + 4)[0], struct.unpack_from("<I", stream, at + 12)[0]
        if msht != texb + 8 or texb < 148 or at + 8 + msht > len(stream):
            raise BuildError("a loose mesh file's TEXB record has an unexpected size")
        field = stream[at + 36:at + 164]
        end = field.find(b"\0")
        if end <= 0 or any(not 0x20 <= byte < 0x7F for byte in field[:end]):
            raise BuildError("a loose mesh file names a texture that is not printable ASCII")
        names.append(field[:end].decode("ascii"))
        at += 8 + msht
    return names


def mesh_textures(install: Install, name: str) -> list[str]:
    rel = loose_mesh_path(name)
    if not install.has(rel):
        raise BuildError(f"the game folder has no mesh file for {name!r} ({rel}), which the units need")
    source = install.read(rel, LIMIT_ARCHIVE)
    try:
        return texture_names(b"".join(enc.inflate(enc.read_members(source))))
    except enc.EncodeError as error:
        raise BuildError(f"{rel}: {error}") from error


# ---- level archives -----------------------------------------------------------------------------------------------------
def unpack(install: Install, level: int) -> list[tuple[str, bytes]]:
    """A level archive's top-level chunks: (tag, payload) in file order."""
    try:
        raw = b"".join(enc.inflate(enc.read_members(install.level_archive(level))))
        return [(tag, raw[at:at + size]) for tag, at, size in enc.chunks(raw)]
    except enc.EncodeError as error:
        raise BuildError(f"{level:03d}_res_PC.aya: {error}") from error


def descriptors(chunks: list[tuple[str, bytes]]) -> dict[tuple[str, str], tuple[str, bytes]]:
    """(tag, normalized name) -> (name as spelled, payload) for TEXT and MESH chunks; the first of a name stands."""
    out: dict[tuple[str, str], tuple[str, bytes]] = {}
    for tag, payload in chunks:
        if tag in ("TEXT", "MESH"):
            try:
                key, shown, _ = logical_key(tag, payload)
            except ValueError as error:
                raise BuildError(f"a {tag} chunk is not a descriptor this recipe reads: {error}") from error
            out.setdefault((tag, key), (shown, payload))
    return out


def mesh_id(payload: bytes) -> int:
    if len(payload) != MESH_DESCRIPTOR_BYTES or payload[8:12] != b"PMS2":
        raise BuildError(f"a MESH descriptor is not the {MESH_DESCRIPTOR_BYTES}-byte PMSH/PMS2 form this recipe patches")
    return struct.unpack_from("<i", payload, MESH_ID_OFFSET)[0]


def with_mesh_id(payload: bytes, value: int) -> bytes:
    mesh_id(payload)
    out = bytearray(payload)
    struct.pack_into("<i", out, MESH_ID_OFFSET, value)
    return bytes(out)


def merge_descriptors(donor: list[tuple[str, bytes]], sources: dict[int, list[tuple[str, bytes]]],
                      meshes: list[str], textures: list[str]) -> tuple[list[tuple[str, bytes]], dict]:
    """The donor's chunks with the MESH and TEXT descriptors it lacks added, copied from the first source that holds each. New
    MESH descriptors get runtime ids after the donor's highest (IMPS refers to meshes by that id). Added descriptors go behind
    the donor's last TEXT and last MESH chunk, in name order."""
    have = descriptors(donor)
    ids = [mesh_id(payload) for (tag, _), (_, payload) in have.items() if tag == "MESH"]
    next_id = max(ids) + 1 if ids else 0
    if len(set(ids)) != len(ids):
        raise BuildError("the donor's MESH descriptors do not have distinct runtime ids")
    indexes = {level: descriptors(chunks) for level, chunks in sources.items()}
    added = {"MESH": [], "TEXT": []}
    log = {"mesh": [], "text": []}
    wanted = (("TEXT", sorted({normalize_asset_name(name) for name in textures}), TEXT_DESCRIPTOR_BYTES),
              ("MESH", sorted({normalize_asset_name(name) for name in meshes}), MESH_DESCRIPTOR_BYTES))
    for tag, keys, size in wanted:
        for key in keys:
            if (tag, key) in have:
                continue
            for level in sorted(indexes, key=SOURCES.index):
                found = indexes[level].get((tag, key))
                if found is None:
                    continue
                shown, payload = found
                if len(payload) != size:
                    raise BuildError(f"{tag} {shown} in archive {level} is {len(payload)} bytes, not the {size} of a descriptor")
                if tag == "MESH":
                    payload = with_mesh_id(payload, next_id)
                    log["mesh"].append({"name": shown, "from": level, "id": next_id})
                    next_id += 1
                else:
                    log["text"].append({"name": shown, "from": level})
                added[tag].append(payload)
                break
            else:
                raise BuildError(f"none of the archives {', '.join(str(level) for level in SOURCES)} holds the {tag} descriptor {key!r}")
    last = {tag: max((i for i, (t, _) in enumerate(donor) if t == tag), default=-1) for tag in ("TEXT", "MESH")}
    if min(last.values()) < 0:
        raise BuildError("the donor archive has no TEXT or no MESH chunks")
    out: list[tuple[str, bytes]] = []
    for index, (tag, payload) in enumerate(donor):
        out.append((tag, payload))
        for kind in ("TEXT", "MESH"):
            if index == last[kind]:
                out.extend((kind, extra) for extra in added[kind])
    return out, log


def chunk_bytes(tag: str, payload: bytes) -> bytes:
    return tag.encode("latin-1") + struct.pack("<I", len(payload)) + payload


def pack(raw: bytes) -> bytes:
    """A stream as the game reads it: 1 MiB blocks, each [u32 length][zlib data]."""
    out = bytearray()
    for start in range(0, len(raw), BLOCK):
        block = zlib.compress(raw[start:start + BLOCK], 9)
        if not 0 < len(block) <= enc.PACK_BUFFER_SIZE:
            raise BuildError("a packed block would not fit the game's block buffer")
        out += struct.pack("<I", len(block)) + block
    return bytes(out)


# ---- the world ----------------------------------------------------------------------------------------------------------
def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def header_from_record(record: headers.WorldHeaderRecord) -> dict:
    """The world header fields worldheaders.dat holds for a level: its engine configurations, three version-2 words and world type,
    and the two words the loader skips, which every shipped world (115 bodies, one exception) fills with the record's payload size and
    level number."""
    if len(record.trailing) != 4:
        raise BuildError("a worldheaders.dat record does not have four trailing words")
    return {"battleEngineConfigurations": list(record.configs), "v2Words": list(record.trailing[:3]),
            "worldType": record.trailing[3], "unused": [record.payload_size, record.world_id]}


def build_world(donor_body: bytes, record: headers.WorldHeaderRecord, donor_record: headers.WorldHeaderRecord,
                scripts: list[dict]) -> tuple[bytes, dict]:
    """Level 888's world body from the donor's: the donor's features, start and spawn points, a level script, a Venturer and a
    Fenrir. The header comes from the player's worldheaders.dat record for 888 (the same mapping is checked on the donor's own)."""
    model = enc.read_world_model(donor_body)
    header = model["header"]
    for key, value in header_from_record(donor_record).items():
        if header.get(key) != value:
            raise BuildError(f"the donor's world header disagrees with its worldheaders.dat record in {key}: "
                             f"{header.get(key)!r} against {value!r}; the header mapping this recipe uses is not valid here")
    header.update(header_from_record(record))
    model["baseLevel"] = -1
    model["waypointPaths"] = []
    model["scripts"] = scripts
    scripts_thing = [t for t in model["things"] if t["kind"] == "level-script"]
    if len(scripts_thing) != 1:
        raise BuildError("the donor world does not have exactly one level script thing")
    level_script = json.loads(json.dumps(scripts_thing[0]))
    level_script["init"]["script"] = "world888script"
    level_script["init"]["name"] = ""
    kept = [t for t in model["things"] if t["kind"] in KEPT_THINGS]
    starts = sorted(t["init"]["start"]["playerNumber"] for t in kept if t["kind"] == "start")
    if starts != [1, 2]:
        raise BuildError(f"the donor world does not have exactly the start points of players 1 and 2 (it has {starts})")

    def unit(definition: str, name: str, placement: dict) -> dict:
        return {"oid": wrd.OID_UNIT, "kind": "unit", "definition": definition, "diesOn": -1,
                "init": {"position": [f32(c) for c in placement["position"]], "orientation": [f32(placement["yaw"]), 0.0, 0.0],
                         "meshNumber": 0, "allegiance": placement["allegiance"], "target": -1, "script": name, "name": name,
                         "spawnScript": "", "active": 1, "attachScriptsToUnits": 0}}

    model["things"] = kept + [level_script, unit(VENTURER, "Venturer", VENTURER_PLACEMENT), unit(FENRIR, "Fenrir", FENRIR_PLACEMENT)]
    body = enc.write_world_body(model)
    if enc.write_world_body(enc.read_world_model(body)) != body:
        raise BuildError("the generated world body did not read back unchanged")
    return body, model


def assemble(chunks: list[tuple[str, bytes]], body: bytes) -> bytes:
    """The archive's unpacked stream: the chunks with the WRES chunk replaced by a world of level 888 alone (WDAT -1 / 888, RLWD)."""
    wdat = chunk_bytes("WDAT", struct.pack("<ii", -1, LEVEL))
    wres = chunk_bytes("WRLD", wdat + chunk_bytes("RLWD", body))
    return b"".join(chunk_bytes(tag, wres if tag == "WRES" else payload) for tag, payload in chunks)


# ---- the build ----------------------------------------------------------------------------------------------------------
@dataclass
class Build:
    files: dict[str, bytes]
    report: dict
    warnings: list[str]


def disc_world(body: bytes, record: headers.WorldHeaderRecord) -> dict:
    """The world of level 888 as the player's own PS2 copy holds it (the body only: tools/level888_ps2_import.py reads it from the image), taken as it is.
    It must read back unchanged, carry the header worldheaders.dat holds for 888, and put only units on the field that this recipe can furnish."""
    model = enc.read_world_model(body)
    if enc.write_world_body(model) != body:
        raise BuildError("the world body of the PS2 copy does not read back unchanged")
    header = model["header"]
    for key, value in header_from_record(record).items():
        if header.get(key) != value:
            raise BuildError(f"the PS2 world's header disagrees with this game's worldheaders.dat record for {LEVEL} in {key}: "
                             f"{header.get(key)!r} against {value!r}")
    if model["baseLevel"] != -1:
        raise BuildError(f"the PS2 world has a base level ({model['baseLevel']}); level {LEVEL} has none")
    definitions = [t["definition"] for t in model["things"] if t["kind"] == "unit"]
    if not definitions:
        raise BuildError("the PS2 world has no unit on the field")
    return model


def build(install: Install, *, lives: int = DEFAULT_LIVES, ai_state: int | None = None, world_body: bytes | None = None,
          shadows: bytes | None = None) -> Build:
    """Level 888's mod files from the player's game folder (nothing is written; see stage_build). With `world_body`, the world is the PS2 copy's
    (see disc_world): its own scripts, units and waypoints are used as they are, and `lives` and `ai_state` have no part in it. With `shadows`, the
    donor's baked static shadows (those of its own features, which this world does not have) are replaced by the PS2 copy's shadow chunk, which must
    read with the decoder (the PC game's own chunk for a level with no shadows is the same 28 bytes)."""
    sources = script_sources(lives, ai_state)
    if install.has(ARCHIVE_PATH):
        raise BuildError(f"the game folder already has {ARCHIVE_PATH}: a mod can only add an archive the game lacks")
    original = install.read(PHYSICS_PATH, LIMIT_SMALL)
    physics_bytes = redirect_unit_mesh(original, FENRIR, FENRIR_FILELESS_MESH, FENRIR_MESH)
    physics = Physics(physics_bytes)
    units, meshes, textures, per_mesh = [], [], [], {}
    disc = None if world_body is None else disc_world(world_body, headers.parse_worldheaders(install.read(WORLDHEADERS_PATH, LIMIT_SMALL)).by_world(LEVEL))
    ships = (VENTURER, FENRIR) if disc is None else tuple(dict.fromkeys(t["definition"] for t in disc["things"] if t["kind"] == "unit"))
    for ship in ships:
        ship_units, ship_meshes = physics.closure(ship)
        units += [u for u in ship_units if u not in units]
        meshes += [m for m in ship_meshes if m.lower() not in (known.lower() for known in meshes)]
    for name in meshes:
        per_mesh[name] = mesh_textures(install, name)
        for texture in per_mesh[name]:
            if normalize_asset_name(texture) not in (normalize_asset_name(known) for known in textures):
                textures.append(texture)

    donor = unpack(install, DONOR)
    source_chunks = {level: unpack(install, level) for level in SOURCES}
    merged, added = merge_descriptors(donor, source_chunks, meshes, textures)
    donor_shadows = None
    if shadows is not None:
        try:
            counts = wrd.parse_sshd(shadows)
        except wrd.DecodeError as error:
            raise BuildError(f"the PS2 copy's shadow chunk cannot be read: {error}") from None
        at = [i for i, (tag, _) in enumerate(merged) if tag == "SSHD"]
        if len(at) != 1:
            raise BuildError(f"the donor archive has {len(at)} SSHD chunks, not one")
        donor_shadows = len(merged[at[0]][1])
        merged = merged[:at[0]] + [("SSHD", shadows)] + merged[at[0] + 1:]

    parsed = headers.parse_worldheaders(install.read(WORLDHEADERS_PATH, LIMIT_SMALL))
    record, donor_record = parsed.by_world(LEVEL), parsed.by_world(DONOR)
    if record is None or donor_record is None:
        raise BuildError(f"worldheaders.dat has no record for level {LEVEL if record is None else DONOR}")
    donor_world = enc.level_worlds(b"".join(chunk_bytes(t, p) for t, p in donor))
    if disc is None:
        scripts = compile_scripts(sources)
        body, model = build_world(donor_world["bodies"]["RLWD"], record, donor_record, scripts)
    else:
        body, model, scripts = world_body, disc, disc["scripts"]

    raw = assemble(merged, body)
    archive = pack(raw)
    problem, unpacked = stage.check_packed(archive, unpack=True)
    problem = problem or stage.check_level_archive(unpacked or b"", LEVEL)
    if problem:
        raise BuildError(f"the generated archive would not pass the loader's walk: {problem}")
    if unpacked != raw:
        raise BuildError("the generated archive did not unpack to the stream that was packed")

    files = {ARCHIVE_PATH: archive, PHYSICS_PATH: physics_bytes}
    report = {
        "level": LEVEL, "donor": DONOR, "sources": list(SOURCES),
        "closure": {"units": units, "meshes": meshes, "textures": textures,
                    "texturesOf": {name: names for name, names in per_mesh.items()}},
        "added": added,
        "archive": {"path": ARCHIVE_PATH, "size": len(archive), "sha256": sha256(archive), "unpackedSize": len(raw),
                    "chunks": len(merged), "worldBodyBytes": len(body), "things": len(model["things"])},
        "physics": {"path": PHYSICS_PATH, "size": len(physics_bytes), "sha256": sha256(physics_bytes), "was": len(original),
                    "unit": FENRIR, "mesh": f"{FENRIR_FILELESS_MESH} -> {FENRIR_MESH}"},
        "scripts": [{"name": r["name"], "instructions": len(r["code"]["instructions"]), "handlers": len(r["code"]["eventFunctions"])}
                    for r in scripts],
        "lives": lives if disc is None else None, "aiState": ai_state if disc is None else None,
        "world": "authored" if disc is None else "ps2-copy",
        "shadows": {"from": "donor" if shadows is None else "ps2-copy", "bytes": len(shadows) if shadows is not None else None,
                    "donorBytes": donor_shadows, **(counts if shadows is not None else {})},
        "inputs": dict(sorted(install.reads.items())),
        "warnings": list(install.warnings),
    }
    return Build(files, report, list(install.warnings))


def description(ce_min: str, lives: int | None = DEFAULT_LIVES) -> str:
    if lives is None:
        return ("Level 888, a Fenrir against a Venturer, built on this machine from your own PS2 copy and this game's own files (nothing downloaded). "
                "EXPERIMENTAL. Adds data/resources/888_res_PC.aya and REPLACES data/default physics.dat (only the unit definition "
                "Fenrir Multiplayer, which no level uses, changes: it names boss-fenrir.msh, because the PC game has no file for the mesh "
                f"the PS2 copy uses), so it conflicts with any other mod that replaces that file. Needs Onslaught CE {ce_min} or newer.")
    return ("Level 888, a Fenrir against a Venturer, built on this machine from this game's own files (nothing downloaded). "
            "EXPERIMENTAL. Adds data/resources/888_res_PC.aya and REPLACES data/default physics.dat (only the unit definition "
            "Fenrir Multiplayer, which no level uses, changes: it names boss-fenrir.msh), so it conflicts with any other mod that "
            f"replaces that file. Each player has {lives} lives, and the match ends when a flagship is destroyed: the other side "
            f"wins. Needs Onslaught CE {ce_min} or newer.")


def stage_build(result: Build, game: Path, out: Path, *, ce_min: str, mod_id: str = MOD_ID, name: str = "Flagship duel (level 888)",
                version: str = "1", author: str = "", ce_max: str | None = None) -> dict:
    """Write the mod folder <out>/<mod_id>/ through world_mod_stage (a new folder only, never inside the game folder)."""
    try:
        return stage.stage_mod(out, game, mod_id, None, name=name, version=version, author=author,
                               description=description(ce_min, result.report["lives"]), ce_min=ce_min, ce_max=ce_max,
                               files=result.files)
    except stage.ModStageError as error:
        raise BuildError(str(error)) from error


# ---- the gate -----------------------------------------------------------------------------------------------------------
def gate_checks(game: Path, install: Install, first: Build, check, lives: int, ai_state: int | None) -> None:
    """The checks of run_gate that read the finished build (first) against the game folder; check(name, passed, detail) records one."""
    report = first.report
    archive, physics_bytes = first.files[ARCHIVE_PATH], first.files[PHYSICS_PATH]
    problem, unpacked = stage.check_packed(archive, unpack=True)
    check("packed like the game's reader needs", problem is None, problem or "")
    check("passes the loader's structure walk", problem is None and stage.check_level_archive(unpacked, LEVEL) is None,
          (problem or stage.check_level_archive(unpacked, LEVEL)) or "")
    chunks = [(tag, unpacked[at:at + size]) for tag, at, size in enc.chunks(unpacked)] if unpacked else []
    out_index = descriptors(chunks)

    # the closure, recomputed from the output files alone
    physics = Physics(physics_bytes)
    missing_meshes, missing_textures, no_file = [], [], []
    for ship in (VENTURER, FENRIR):
        for mesh in physics.closure(ship)[1]:
            if ("MESH", normalize_asset_name(mesh)) not in out_index:
                missing_meshes.append(mesh)
            if not install.has(loose_mesh_path(mesh)):
                no_file.append(mesh)
                continue
            for texture in mesh_textures(install, mesh):
                if ("TEXT", normalize_asset_name(texture)) not in out_index:
                    missing_textures.append(f"{texture} (for {mesh})")
    check("every mesh the ships need has a descriptor", not missing_meshes, ", ".join(missing_meshes))
    check("every texture those meshes ask for has a descriptor", not missing_textures, ", ".join(missing_textures))
    check("every mesh the ships need has its loose file", not no_file, ", ".join(no_file))
    donor_chunks = unpack(install, DONOR)

    def names_of(tag: str, listed: list[tuple[str, bytes]]) -> collections.Counter:
        return collections.Counter(logical_key(tag, payload)[0] for t, payload in listed if t == tag)

    for tag in ("TEXT", "MESH"):
        gained = names_of(tag, chunks) - names_of(tag, donor_chunks)
        lost = names_of(tag, donor_chunks) - names_of(tag, chunks)
        wanted = collections.Counter(normalize_asset_name(entry["name"]) for entry in report["added"][tag.lower()])
        check(f"the {tag} descriptors gained are exactly the ones added, and none of the donor's is lost",
              gained == wanted and not lost, f"{sum(wanted.values())} added")
    mesh_names = [logical_key("MESH", payload)[0] for tag, payload in chunks if tag == "MESH"]
    ids = [mesh_id(payload) for tag, payload in chunks if tag == "MESH"]
    check("no MESH name twice, no runtime id twice", len(set(mesh_names)) == len(mesh_names) and len(set(ids)) == len(ids),
          f"{len(ids)} meshes")
    kept = collections.Counter(donor_chunks) - collections.Counter(c for c in chunks)
    check("the donor's chunks are kept byte for byte (apart from its world)", all(tag == "WRES" for tag, _ in kept))

    # the physics file differs from the original in exactly the one node
    original = Physics(install.read(PHYSICS_PATH, LIMIT_SMALL))
    differing = [s.name for s, o in zip(physics.statements, original.statements)
                 if (s.kind, s.name, [(n.field, n.value) for n in s.nodes]) != (o.kind, o.name, [(n.field, n.value) for n in o.nodes])]
    check("the physics file differs from the original in exactly one unit definition",
          len(physics.statements) == len(original.statements) and differing == [FENRIR], ", ".join(differing))

    # the world
    worlds = enc.level_worlds(unpacked) if unpacked else {"bodies": {}, "baseLevel": None, "realLevel": None}
    body = worlds["bodies"].get("RLWD", b"")
    model = enc.read_world_model(body)
    parsed = headers.parse_worldheaders(install.read(WORLDHEADERS_PATH, LIMIT_SMALL))
    record = parsed.by_world(LEVEL)
    check("the world names level 888 alone", (worlds["baseLevel"], worlds["realLevel"], sorted(worlds["bodies"])) == (-1, LEVEL, ["RLWD"]))
    check("the world body reads back unchanged", enc.write_world_body(model) == body)
    check("the world header is the worldheaders.dat record for 888",
          record is not None and all(model["header"][k] == v for k, v in header_from_record(record).items()))
    definitions = {t["definition"] for t in model["things"] if "definition" in t}
    defined = {s.name for s in physics.statements}
    check("every definition the world places is in the physics file", definitions <= defined, ", ".join(sorted(definitions - defined)))
    check("both ships and the level script are placed",
          {VENTURER, FENRIR} <= definitions and sum(t["kind"] == "level-script" for t in model["things"]) == 1)
    scripts = {s["name"]: s for s in model["scripts"]}
    expected = script_sources(lives, ai_state)
    check("the scripts are the authored ones", sorted(scripts) == sorted(expected) and
          [msl.normal(s) for s in model["scripts"]] == [msl.normal(r) for r in compile_scripts(expected)])
    strings = {s["value"] for rec in model["scripts"] for s in rec["code"]["symbols"] if s.get("dataType") == 3 and isinstance(s.get("value"), str)}
    check("the compiled scripts hold only strings authored here", strings <= authored_strings(expected),
          ", ".join(sorted(strings - authored_strings(expected))))

    # the stager accepts it
    try:
        manifest = stage.build_files_manifest(MOD_ID, "gate", "1", first.files, game_has=install.has, ce_min="0.1.13",
                                              description=description("0.1.13", lives))
        check("the mod stager (the loader's rules) accepts the files", True, f"mod.json {sha256(manifest)[:16]}...")
    except stage.ModStageError as error:
        check("the mod stager (the loader's rules) accepts the files", False, str(error))

    # the folder was only read
    changed = [rel for rel, info in install.reads.items() if sha256(Install(game).read(rel, LIMIT_ARCHIVE)) != info["sha256"]]
    check("the game folder's files were not changed during the run", not changed, ", ".join(changed))
    check("every pinned file is the one the recipe was checked against", not install.warnings, "; ".join(install.warnings))


def run_gate(game: Path, *, strict_pins: bool = False, lives: int = DEFAULT_LIVES, ai_state: int | None = None) -> list[tuple[str, bool, str]]:
    """Checks on the finished build against the player's game folder. Each result is (name, passed, detail)."""
    results: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        results.append((name, bool(ok), detail))

    install = Install(game, strict_pins=strict_pins)
    try:
        first = build(install, lives=lives, ai_state=ai_state)
        second = build(Install(game, strict_pins=strict_pins), lives=lives, ai_state=ai_state)
    except BuildError as error:
        check("build", False, str(error))
        return results
    report = first.report
    check("build", True, f"{report['archive']['size']} byte archive, {report['physics']['size']} byte physics file")
    check("deterministic", first.files == second.files and first.report == second.report,
          "two builds from the same folder give the same bytes")

    try:
        gate_checks(game, install, first, check, lives, ai_state)
    except (BuildError, enc.EncodeError, ValueError, KeyError, TypeError, struct.error) as error:
        check("the checks ran to the end", False, f"{type(error).__name__}: {error}")
    return results


# ---- command line ---------------------------------------------------------------------------------------------------------
def option(value: str) -> Path:
    if not value:
        raise argparse.ArgumentTypeError("a non-empty path is required")
    return Path(value)


def cmd_closure(args) -> int:
    install = Install(args.game, strict_pins=args.strict_pins)
    result = build(install)
    print(json.dumps(result.report["closure"] | {"added": result.report["added"], "warnings": result.warnings}, indent=1))
    return 0


def cmd_gate(args) -> int:
    results = run_gate(args.game, strict_pins=args.strict_pins, lives=args.lives, ai_state=args.ai_state)
    for name, ok, detail in results:
        print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f" - {detail}" if detail else ""))
    failed = [name for name, ok, _ in results if not ok]
    print(f"{len(results) - len(failed)} of {len(results)} checks passed")
    return 1 if failed else 0


def cmd_build(args) -> int:
    install = Install(args.game, strict_pins=args.strict_pins)
    result = build(install, lives=args.lives, ai_state=args.ai_state)
    game = enc.selected_game_root(args.game)
    summary = stage_build(result, game, args.out, ce_min=args.ce_min, mod_id=args.id, name=args.name, version=args.version,
                          author=args.author or "", ce_max=args.ce_max)
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    print(f"staged CE mod {args.id!r} in {summary['root']}")
    for entry in summary["files"]:
        print(f"  {entry['path']}  {entry['size']} bytes  sha256 {entry['sha256']}")
    print(f"  mod.json  sha256 {summary['manifestSha256']}")
    print(f"to use it: keep the folder in the CE user folder's mods folder and add mods={args.id} to ce.ini, then start the level with "
          f"-level 888 on the game's command line. The mod replaces data/default physics.dat, so it conflicts with another "
          f"mod that does. CE refuses mods on Windows for now, and keeps them off in replays, recordings, probes, virtual clocks, "
          f"pilots and network sessions.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "gate", "closure"):
        p = sub.add_parser(name)
        p.add_argument("--game", type=option, default=os.environ.get("BEA_GAME"), required="BEA_GAME" not in os.environ,
                       help="the game folder (or BEA_GAME)")
        p.add_argument("--strict-pins", action="store_true", help="refuse a file whose SHA-256 is not the one the recipe was checked against")
        if name != "closure":
            p.add_argument("--lives", type=int, default=DEFAULT_LIVES, help="lives for each player (1 to 9)")
            p.add_argument("--ai-state", type=int, default=None, help="set the ships' AI state at the start (0 to 4; 4 is AI_ONF)")
        if name == "build":
            p.add_argument("--out", type=option, required=True, help="the folder that receives the mod folder")
            p.add_argument("--ce-min", required=True, help="the oldest CE version that can load an added level archive, such as 0.1.13")
            p.add_argument("--ce-max", default=None)
            p.add_argument("--id", default=MOD_ID)
            p.add_argument("--name", default="Flagship duel (level 888)")
            p.add_argument("--version", default="1")
            p.add_argument("--author", default="")
    args = parser.parse_args(argv)
    return {"build": cmd_build, "gate": cmd_gate, "closure": cmd_closure}[args.command](args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (BuildError, enc.EncodeError) as error:
        print(f"level 888: {error}", file=sys.stderr)
        sys.exit(2)
