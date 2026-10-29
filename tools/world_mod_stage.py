#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Package edited world bodies, and generated files, as an Onslaught CE mod folder.

The CE mod loader (onslaught-ce, port/platform/common/mods.cpp; the player-facing rules are the Mods section of its README)
admits a folder <user folder>/mods/<id>/ that holds mod.json and the files mod.json lists. A mod may replace a file the game
has and may ADD two kinds of file: data/worlds/worldNNN.wrd, which CWorld::Load reads in place of the level archive's copy (the
real world and the base world are separate files), and data/resources/NNN_res_PC.aya for a multiplayer level (NNN from 850 to 899)
that the game has no archive for. This module builds exactly such a folder from world-body bytes, so CE loads it with no
hand-editing:

    <out>/<id>/mod.json                  schema 1, the id, name, version, optional author, description, ce_min, ce_max, and
                                         every file with its size and SHA-256
    <out>/<id>/data/worlds/worldNNN.wrd  the bodies, byte for byte

Everything the loader checks at start-up is checked here first, with the loader's own limits (the constants below are kept
equal to mods.cpp): the folder name is the id (1 to 48 lowercase letters, digits, '-' or '_'); name 1 to 64, version 1 to 32,
author up to 64 and description up to 1024 characters (printable ASCII only here, because the loader logs mod text as ASCII);
ce_min and ce_max are one to four numbers of up to five digits joined by dots, compared as the loader compares them (missing
numbers are zero) and with ce_min not after ce_max, since no released CE could load such a mod; a world file is at most 4 MiB.
CE loads mods on Linux only for now (Windows refuses them), and keeps them off in replays, recordings, probes, virtual clocks,
pilots and network sessions.

stage_mod(..., files={path: bytes}) stages more than worlds: any file the loader admits. Each path is held to the loader's path
rules, listed once whatever its case, and one of three kinds, decided as the loader decides it: a world file (data/worlds/worldNNN.wrd,
at most 4 MiB); an added level archive (data/resources/NNN_res_PC.aya, NNN 850 to 899, for a level the selected game folder has no
archive for: at most 8 MiB packed, 32 MiB unpacked and 2048 chunks, and its chunk stream must pass check_level_archive, the loader's
structure walk); or a replacement of a file the selected game folder has (at most 64 MiB; an .aya must unpack as the game's block
reader needs, a texture must be a DDS image of the size the game can load). A mod holds at most 4096 files and 1 GiB. The world-only
call (worlds only) is unchanged, including its messages.

Writing goes through safe_generated_output: the destination is opened as a held directory chain, a destination inside the
selected game folder (or inside any Battle Engine Aquila tree) is refused, every file is written to an exclusive temporary
name and published without replacing anything, the world files are written first and mod.json last (a folder without
mod.json is inert), and a folder that already holds anything is refused. The helper detects replacement; it does not lock: a
directory moved by another process during the run is not guaranteed to stay outside the game folder (tools/README.md).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import struct
import sys
import zlib
from pathlib import Path
from typing import Callable

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from safe_generated_output import SecuredOutputRoot, UnsafeGeneratedOutputError  # noqa: E402

SCHEMA = 1
ID_RE = re.compile(r"[a-z0-9_-]{1,48}")
TEXT_LIMITS = {"name": (1, 64), "version": (1, 32), "author": (0, 64), "description": (0, 1024)}
VERSION_RE = re.compile(r"[0-9]{1,5}(?:\.[0-9]{1,5}){0,3}")
WORLD_PATH = "data/worlds/world{:03d}.wrd"
WORLD_PATH_RE = re.compile(r"data/worlds/world[0-9]{3}\.wrd")
MAX_WORLD_BYTES = 4 << 20
MAX_FILES_PER_MOD = 4096
MAX_MANIFEST_BYTES = 256 << 10

# What stage_mod(files=...) holds a file to: mods.cpp's constants and rules, restated (kMaxFile, kMaxTotal, kMaxArchive,
# kMaxArchiveUnpacked, kMaxLevelChunks, kArchiveFirst/Last, kMaxPath, kMaxPart, kMaxPathParts, kBlock, kPackBuffer,
# kTextureScratch, kMaxTextureSide; CheckPath, DeviceName, WorldFile, LevelArchiveName, CheckPacked, CheckLevelArchive).
WORLD_KEY_RE = re.compile(r"data/worlds/world[0-9]{3}\.wrd")  # matched against the lowercased path, as the loader does
ARCHIVE_KEY_RE = re.compile(r"data/resources/([0-9]{3})_res_pc\.aya")
ARCHIVE_FIRST, ARCHIVE_LAST = 850, 899
MAX_FILE_BYTES = 64 << 20
MAX_TOTAL_BYTES = 1 << 30
MAX_ARCHIVE_BYTES = 8 << 20
MAX_ARCHIVE_UNPACKED_BYTES = 32 << 20
MAX_LEVEL_CHUNKS = 2048
MAX_PATH_CHARS, MAX_PART_CHARS, MAX_PATH_PARTS = 240, 128, 12
PACK_BLOCK = 1 << 20
PACK_BUFFER = 0x102927
TEXTURE_SCRATCH = 0x500000
MAX_TEXTURE_SIDE = 4096
LEVEL_TAGS = (b"LVLR", b"TARG", b"AYAD", b"TEXT", b"MESH", b"IMPS", b"LNDS", b"SURF", b"ERES", b"SSHD", b"WRES")
AYAD_GUARDS = (344, 372, 316, 5084, 92)
WORLD_BODY_VERSIONS = range(43, 51)
DEVICE_NAMES = frozenset({"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
                         | {f"{prefix}{digit}" for prefix in ("COM", "LPT") for digit in "0123456789"})


class ModStageError(ValueError):
    """A mod that the loader would refuse, or an output the writer will not make."""


def world_path(level: int) -> str:
    """The game-relative path CWorld::Load reads a level's world body from."""
    if type(level) is not int or not 0 <= level <= 999:
        raise ModStageError(f"a world level is a number from 0 to 999, not {level!r}")
    return WORLD_PATH.format(level)


def _text(label: str, value: str) -> str:
    low, high = TEXT_LIMITS[label]
    if not isinstance(value, str) or not low <= len(value) <= high:
        raise ModStageError(f"{label} must be {low} to {high} characters")
    if any(not 0x20 <= ord(char) < 0x7F for char in value):
        raise ModStageError(f"{label} may hold printable ASCII only (the loader logs mod text as ASCII)")
    return value


def _version(label: str, value: str) -> str:
    if not isinstance(value, str) or not VERSION_RE.fullmatch(value):
        raise ModStageError(f"{label} must be one to four numbers of up to five digits joined by dots, such as 0.1.11")
    return value


def version_tuple(text: str) -> tuple[int, ...]:
    """A version as the loader orders it: four numbers, the missing ones zero (so 1.2 equals 1.2.0.0 and 1.10 is after 1.9)."""
    parts = [int(part) for part in text.split(".")]
    return tuple(parts + [0] * (4 - len(parts)))


def check_identity(mod_id: str, name: str, version: str, author: str = "", description: str = "",
                   ce_min: str | None = None, ce_max: str | None = None) -> None:
    if not isinstance(mod_id, str) or not ID_RE.fullmatch(mod_id):
        raise ModStageError("a mod id is 1 to 48 lowercase letters, digits, '-' or '_' (it is also the folder's name)")
    _text("name", name)
    _text("version", version)
    _text("author", author)
    _text("description", description)
    if ce_min is not None:
        _version("ce_min", ce_min)
    if ce_max is not None:
        _version("ce_max", ce_max)
    if ce_min is not None and ce_max is not None and version_tuple(ce_min) > version_tuple(ce_max):
        raise ModStageError(f"ce_min {ce_min} is after ce_max {ce_max}: no released CE version could load this mod")


def _manifest_text(mod_id: str, name: str, version: str, entries: list[dict], author: str, description: str,
                   ce_min: str | None, ce_max: str | None) -> bytes:
    manifest: dict = {"schema": SCHEMA, "id": mod_id, "name": name, "version": version}
    if author:
        manifest["author"] = author
    if description:
        manifest["description"] = description
    if ce_min is not None:
        manifest["ce_min"] = ce_min
    if ce_max is not None:
        manifest["ce_max"] = ce_max
    manifest["files"] = entries
    text = (json.dumps(manifest, indent=2, ensure_ascii=True) + "\n").encode("ascii")
    if len(text) > MAX_MANIFEST_BYTES:
        raise ModStageError("mod.json would be larger than the loader's 256 KiB")
    return text


def build_manifest(mod_id: str, name: str, version: str, files: dict[str, bytes], *, author: str = "",
                   description: str = "", ce_min: str | None = None, ce_max: str | None = None) -> bytes:
    """mod.json as the loader reads it: strict JSON, schema 1, only the keys it knows, every file with size and SHA-256."""
    check_identity(mod_id, name, version, author, description, ce_min, ce_max)
    if not files:
        raise ModStageError("a mod lists at least one file")
    if len(files) > MAX_FILES_PER_MOD:
        raise ModStageError(f"a mod lists at most {MAX_FILES_PER_MOD} files")
    entries = []
    for path in sorted(files):
        data = files[path]
        if not WORLD_PATH_RE.fullmatch(path):
            raise ModStageError(f"{path}: this stager writes world files only (data/worlds/worldNNN.wrd)")
        if type(data) is not bytes or not 0 < len(data) <= MAX_WORLD_BYTES:
            raise ModStageError(f"{path}: a world file is 1 byte to {MAX_WORLD_BYTES} bytes")
        entries.append({"path": path, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return _manifest_text(mod_id, name, version, entries, author, description, ce_min, ce_max)


# ---- files other than worlds: the loader's file rules, restated ---------------------------------------------------------
def path_problem(path: str) -> str | None:
    """None when the loader's CheckPath accepts a manifest path, else why not."""
    if not isinstance(path, str) or not path or len(path) > MAX_PATH_CHARS:
        return "an empty or over-long path"
    count = 0
    for part in path.split("/"):
        if not part:
            return "an absolute path or an empty path component"
        if part in (".", ".."):
            return "a '.' or '..' component"
        if len(part) > MAX_PART_CHARS:
            return "an over-long path component"
        if any(ord(char) < 32 or ord(char) >= 127 or char in '\\:*?"<>|' for char in part):
            return "a character that is not allowed in a path (\\ : * ? \" < > | or a control or non-ASCII byte)"
        if part[0] == " " or part[-1] in " .":
            return "a component that starts with a space or ends with a space or a dot"
        if part.split(".", 1)[0].rstrip(" ").upper() in DEVICE_NAMES:
            return "a Windows device name"
        count += 1
        if count > MAX_PATH_PARTS:
            return "too many path components"
    if path.split("/", 1)[0].lower() != "data":
        return "a path outside data/"
    return None


def check_packed(data: bytes, *, texture: bool = False, unpack: bool = False) -> tuple[str | None, bytes | None]:
    """The loader's CheckPacked on a packed .aya file: (None, the unpacked bytes if unpack is set) when the game's block reader
    (CDXMemBuffer::ReadBlock) can read it, else (why not, None). A texture must also unpack to a DDS image the game can load."""
    size = len(data)
    pos = total = blocks = 0
    short_seen = False
    head = bytearray()
    kept = bytearray() if unpack else None
    while pos < size:
        if size - pos < 4:
            return "a packed file with a cut block header", None
        packed = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        if packed == 0 or packed > PACK_BUFFER:
            return "a packed block larger than the game's block buffer", None
        if size - pos < packed:
            return "a packed file with a cut block", None
        if short_seen:
            return "a packed block under 1 MiB before the last block", None
        decoder = zlib.decompressobj()
        try:
            block = decoder.decompress(data[pos:pos + packed], PACK_BUFFER + 1)
        except zlib.error:
            return "a packed block that does not unpack", None
        if len(block) > PACK_BUFFER or not decoder.eof or decoder.unused_data:
            return "a packed block that does not unpack", None
        if len(block) > PACK_BLOCK:
            return "a packed block that unpacks to more than 1 MiB", None
        if len(block) < PACK_BLOCK:
            short_seen = True
        if len(head) < 128:
            head += block[:128 - len(head)]
        total += len(block)
        if kept is not None:
            if total > MAX_ARCHIVE_UNPACKED_BYTES:
                return "an added level archive that unpacks to more than 32 MiB", None
            kept += block
        pos += packed
        blocks += 1
        if total > MAX_FILE_BYTES:
            return "a packed file that unpacks to more than 64 MiB", None
    if not blocks:
        return "an empty packed file", None
    if texture:
        if total >= TEXTURE_SCRATCH:
            return "a texture that unpacks to 5 MiB or more (the game's texture buffer)", None
        if len(head) < 128 or head[:4] != b"DDS " or struct.unpack_from("<I", head, 4)[0] != 124:
            return "a texture that is not a DDS image", None
        height, width = struct.unpack_from("<II", head, 12)
        if not width or not height or width > MAX_TEXTURE_SIDE or height > MAX_TEXTURE_SIDE:
            return "a texture over 4096 texels a side", None
    return None, (bytes(kept) if kept is not None else None)


def check_level_archive(raw: bytes, level: int) -> str | None:
    """The loader's CheckLevelArchive on an added level archive's unpacked stream: None when it has, as its chunk headers declare
    it, the shape of the archives the game ships, else why not. It checks the declared structure, not the readers: the game's chunk
    reader never skips to a chunk's declared end, CWorld::Deserialize takes WRLD's sub-chunks by position and not by tag, and the
    readers take fixed amounts whatever a header says. LVLR, TARG and AYAD are read at fixed sizes; a TEXT as the DXTX and CTEX
    headers, the 344-byte record and 12 bytes for each of its mNumFrames (a 16-entry array: more overwrites the texture object);
    a MESH as its PMSH and PMS2 headers, a 300-byte name, the runtime id and the optional word (324 bytes before any branch) and
    one byte more when the mesh is kept, or skipped by the PMS2 header's size. A named mesh keeps its data in its own file, so
    its chunk holds those 325 bytes and 317 more (a chunk header and the same 309 bytes) for each chained mesh, a count only that
    file knows; an unnamed mesh holds its data in the chunk. So it requires what makes the two agree on the shipped archives:
    LVLR 103, TARG 1 and the AYAD guards of this build first, and not again; only the eleven tags a level archive holds, at most
    2048 chunks, every length inside the stream; texture entries of exactly the size the game reads (DXTX and CTEX around 344
    bytes and 12 for each of 1 to 16 frames); model entries of at least that size (PMSH around a PMS2 that fills it, of 325 bytes
    or more, and for a named mesh exactly 325 bytes and 317 for each chained mesh); and exactly one WRES, last, holding one WRLD
    of WDAT (8 bytes: -1 or a base level, and this level's number as the real world), a BSWD only when there is a base world, and
    an RLWD, in that order and nothing else, each body of 2 bytes to 4 MiB and of a version CWorld::LoadWorld accepts. What a
    body, a texture record, a mesh or the terrain holds is not looked at."""
    def u32(at: int) -> int:
        return struct.unpack_from("<I", raw, at)[0]

    at = count = wres = wres_at = wres_size = 0
    while at < len(raw):
        if len(raw) - at < 8:
            return "a level archive with a cut chunk header"
        count += 1
        if count > MAX_LEVEL_CHUNKS:
            return "a level archive with more than 2048 chunks"
        tag, size = raw[at:at + 4], u32(at + 4)
        if size > len(raw) - at - 8:
            return "a level archive chunk that runs past the end of the stream"
        payload = at + 8
        if tag not in LEVEL_TAGS:
            return "a level archive chunk with a tag a level archive does not hold"
        if count == 1 and (tag != b"LVLR" or size != 4 or u32(payload) != 103):
            return "a level archive that does not start with LVLR 103"
        if count == 2 and (tag != b"TARG" or size != 4 or u32(payload) != 1):
            return "a level archive without TARG 1 second"
        if count == 3:
            if tag != b"AYAD" or size != 24:
                return "a level archive without its AYAD guards third"
            if tuple(u32(payload + 4 * index) for index in range(5)) != AYAD_GUARDS:
                return "a level archive built for other structure sizes (AYAD)"
        if count > 3 and tag in (b"LVLR", b"TARG", b"AYAD"):
            return "a level archive that repeats LVLR, TARG or AYAD after its first three chunks"
        if tag == b"TEXT":
            if size < 372 or raw[payload:payload + 4] != b"DXTX" or u32(payload + 4) != size - 8 or raw[payload + 8:payload + 12] != b"CTEX":
                return "a level archive TEXT chunk that is not a DXTX/CTEX texture record of 372 bytes or more"
            frames = u32(payload + 328)   # mNumFrames, +0x138 of the texture object, read once the 372 bytes are known to be there
            if frames > 16 or size != 360 + 12 * frames:
                return "a level archive TEXT chunk with more than 16 frames, or a size that is not 360 bytes and 12 for each frame"
        if tag == b"MESH":
            if (size < 325 or raw[payload:payload + 4] != b"PMSH" or u32(payload + 4) != size - 8
                    or raw[payload + 8:payload + 12] != b"PMS2" or u32(payload + 12) != size - 16):
                return "a level archive MESH chunk that is not a PMSH record of 325 bytes or more whose PMS2 record fills it"
            if raw[payload + 16] and (size - 325) % 317:   # a named mesh: its data is in its own file, so 325 bytes and 317 for each chained mesh
                return "a level archive MESH chunk of a named mesh whose size is not 325 bytes and 317 for each chained mesh"
        if tag == b"WRES":
            wres += 1
            wres_at, wres_size = payload, size
        elif wres:
            return "a level archive with a chunk after its WRES"
        at = payload + size
    if count < 3 or wres != 1:
        return "a level archive without exactly one WRES chunk"
    if wres_size < 8 or raw[wres_at:wres_at + 4] != b"WRLD" or u32(wres_at + 4) != wres_size - 8:
        return "a level archive whose WRES does not hold one WRLD"
    at, end = wres_at + 8, wres_at + wres_size

    def next_chunk(tag: bytes, absent: str, misplaced: str) -> tuple[str | None, int, int]:
        """(why not, payload offset, size) for the next chunk of WRLD, which must be `tag`."""
        if at == end:
            return absent, 0, 0
        if end - at < 8 or u32(at + 4) > end - at - 8:
            return "a level archive WRLD with a chunk that runs past its end", 0, 0
        if raw[at:at + 4] != tag:
            return misplaced, 0, 0
        return None, at + 8, u32(at + 4)

    why, payload, size = next_chunk(b"WDAT", "a level archive WRLD without WDAT", "a level archive WRLD that does not start with WDAT")
    if why:
        return why
    if size != 8:
        return "a level archive WRLD whose WDAT is not 8 bytes"
    base, real = struct.unpack_from("<ii", raw, payload)
    at = payload + 8
    if real != level:
        return "a level archive that names another level's number as its real world (WDAT)"
    if base != -1 and not 0 <= base <= 999:
        return "a level archive whose base world (WDAT) is not a level number"
    bodies = ([(b"BSWD", "a level archive whose WDAT names a base world but whose WRLD has no BSWD",
                "a level archive WRLD whose BSWD does not follow its WDAT")] if base != -1 else []) + [
        (b"RLWD", "a level archive WRLD without a real world body (RLWD)",
         "a level archive WRLD whose RLWD does not follow its WDAT and base world")]
    for tag, absent, misplaced in bodies:
        why, payload, size = next_chunk(tag, absent, misplaced)
        if why:
            return why
        if not 2 <= size <= MAX_WORLD_BYTES:
            return "a level archive world body of an unusable size (2 bytes to 4 MiB)"
        if struct.unpack_from("<H", raw, payload)[0] not in WORLD_BODY_VERSIONS:
            return "a level archive world body of a version CWorld::LoadWorld refuses (43 to 50)"
        at = payload + size
    if at != end:
        return "a level archive WRLD with chunks after its real world body"
    return None


def game_has_file(game: Path, rel: str) -> bool:
    """Whether the selected game folder has the file a manifest path names, each component matched without regard to case
    (the loader's PortGameHasFile): a regular file, reached through folders."""
    def walk(folder: Path, parts: list[str]) -> bool:
        wanted = parts[0].lower()
        try:
            matches = [entry for entry in os.scandir(folder) if entry.name.lower() == wanted]
        except OSError:
            return False
        for entry in matches:
            if len(parts) == 1:
                if entry.is_file():
                    return True
            elif entry.is_dir() and walk(Path(entry.path), parts[1:]):
                return True
        return False

    parts = [part for part in rel.split("/") if part]
    return bool(parts) and walk(Path(game), parts)


def file_kind(path: str, data: bytes, game_has: Callable[[str], bool]) -> tuple[str, str | None]:
    """(kind, None) for a file the loader admits, kind being 'world', 'archive' (an added level archive) or 'replacement';
    ('', why) for one it would refuse. game_has says whether the selected game folder has a path."""
    bad = path_problem(path)
    if bad:
        return "", f"{path}: {bad}"
    if type(data) is not bytes or not 0 < len(data) <= MAX_FILE_BYTES:
        return "", f"{path}: a file is 1 byte to {MAX_FILE_BYTES} bytes"
    key = path.lower()
    has = bool(game_has(path))
    world = WORLD_KEY_RE.fullmatch(key) is not None
    named = ARCHIVE_KEY_RE.fullmatch(key)
    level = int(named.group(1)) if named else -1
    archive = not has and ARCHIVE_FIRST <= level <= ARCHIVE_LAST
    if not world and not archive and not has:
        return "", (f"{path}: the game has no such file (a mod can only replace the game's files, or add a world file, "
                    f"data/worlds/worldNNN.wrd, or the archive of a multiplayer level that has none, "
                    f"data/resources/NNN_res_PC.aya for NNN {ARCHIVE_FIRST} to {ARCHIVE_LAST})")
    if world and len(data) > MAX_WORLD_BYTES:
        return "", f"{path}: a world file larger than 4 MiB"
    if archive and len(data) > MAX_ARCHIVE_BYTES:
        return "", f"{path}: an added level archive larger than 8 MiB"
    if key.endswith(".aya"):
        texture = key.startswith(("data/resources/textures/", "data/resources/dxtntextures/"))
        why, unpacked = check_packed(data, texture=texture, unpack=archive)
        if why is None and archive:
            why = check_level_archive(unpacked, level)
        if why:
            return "", f"{path}: {why}"
    return ("world" if world else "archive" if archive else "replacement"), None


def build_files_manifest(mod_id: str, name: str, version: str, files: dict[str, bytes], *, game_has: Callable[[str], bool],
                         author: str = "", description: str = "", ce_min: str | None = None,
                         ce_max: str | None = None) -> bytes:
    """mod.json for any files the loader admits (see file_kind), checked as the loader checks them at start-up. build_manifest,
    which admits world files only, is unchanged."""
    check_identity(mod_id, name, version, author, description, ce_min, ce_max)
    if not files:
        raise ModStageError("a mod lists at least one file")
    if len(files) > MAX_FILES_PER_MOD:
        raise ModStageError(f"a mod lists at most {MAX_FILES_PER_MOD} files")
    if not all(isinstance(path, str) for path in files):
        raise ModStageError("a file's path is text")
    seen: dict[str, str] = {}
    entries, total = [], 0
    for path in sorted(files):
        data = files[path]
        _kind, problem = file_kind(path, data, game_has)
        if problem:
            raise ModStageError(problem)
        if path.lower() in seen:
            raise ModStageError(f"{path}: listed twice (also {seen[path.lower()]}; the loader compares paths without regard to case)")
        seen[path.lower()] = path
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise ModStageError("a mod holds more than 1 GiB")
        entries.append({"path": path, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return _manifest_text(mod_id, name, version, entries, author, description, ce_min, ce_max)


def stage_mod(parent: Path, game: Path, mod_id: str, worlds: dict[int, bytes] | None = None, *, name: str,
              version: str = "1", author: str = "", description: str = "", ce_min: str | None = None,
              ce_max: str | None = None, files: dict[str, bytes] | None = None) -> dict:
    """Write <parent>/<mod_id>/ (mod.json, data/worlds/worldNNN.wrd for each level in worlds, and each game-relative path in
    files) and return a summary.

    With files unset this is the world-only stager it always was: worlds is required in practice and build_manifest judges it.
    With files set (a dict of game-relative path to bytes) every file, worlds included, is judged by build_files_manifest
    against the selected game folder; a world given both ways is refused. Refuses, with nothing written: a destination inside
    the selected game folder (or any game tree), a folder that already holds anything, and everything the manifest builder
    refuses. The files are published in sorted order and mod.json last."""
    payload = {world_path(level): body for level, body in (worlds or {}).items()}
    if files is None:
        manifest = build_manifest(mod_id, name, version, payload, author=author, description=description,
                                  ce_min=ce_min, ce_max=ce_max)
    else:
        if not isinstance(files, dict):
            raise ModStageError("files is a dict of game-relative path to bytes")
        taken = {path.lower() for path in payload}
        for path in files:
            if isinstance(path, str) and path.lower() in taken:
                raise ModStageError(f"{path}: given both as a world and as a file")
        payload.update(files)
        manifest = build_files_manifest(mod_id, name, version, payload,
                                        game_has=lambda rel: game_has_file(Path(os.path.abspath(game)), rel),
                                        author=author, description=description, ce_min=ce_min, ce_max=ce_max)
    files = payload
    root = Path(os.path.abspath(parent)) / mod_id
    game = Path(os.path.abspath(game))
    try:
        with SecuredOutputRoot(root, protected_sources=[game]) as secured:
            existing = sorted(os.listdir(root))
            if existing:
                raise ModStageError(f"{root} already holds {existing[0]!r}: stage into a new folder (nothing was written)")
            for path in sorted(files):
                secured.ensure_directory(root / Path(path).parent)
                secured.atomic_write_new_bytes(root / path, files[path])
            secured.atomic_write_new_bytes(root / "mod.json", manifest)
    except UnsafeGeneratedOutputError as error:
        raise ModStageError(f"refused: {error}") from error
    except OSError as error:
        raise ModStageError(f"could not write the mod: {error}") from error
    return {"root": str(root), "manifestSha256": hashlib.sha256(manifest).hexdigest(),
            "files": [{"path": path, "size": len(files[path]), "sha256": hashlib.sha256(files[path]).hexdigest()}
                      for path in sorted(files)]}
