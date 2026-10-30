#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Package edited world bodies as an Onslaught CE mod folder.

The CE mod loader (onslaught-ce, port/platform/common/mods.cpp; the player-facing rules are the Mods section of its README)
admits a folder <user folder>/mods/<id>/ that holds mod.json and the files mod.json lists. A mod may replace a file the game
has and may ADD one kind of file the game reads loose: data/worlds/worldNNN.wrd, which CWorld::Load reads in place of the
level archive's copy (the real world and the base world are separate files). This module builds exactly such a folder from
world-body bytes, so CE loads it with no hand-editing:

    <out>/<id>/mod.json                  schema 1, the id, name, version, optional author, description, ce_min, ce_max, and
                                         every file with its size and SHA-256
    <out>/<id>/data/worlds/worldNNN.wrd  the bodies, byte for byte
    <out>/<id>/data/MissionScripts/...   optional edited sources, which CE admits only as replacements of files the game has

The supported per-mod loader limits are checked here first (the constants below are kept
equal to mods.cpp): the folder name is the id (1 to 48 lowercase letters, digits, '-' or '_'); name 1 to 64, version 1 to 32,
author up to 64 and description up to 1024 characters (printable ASCII only here, because the loader logs mod text as ASCII);
ce_min and ce_max are one to four numbers of up to five digits joined by dots, compared as the loader compares them (missing
numbers are zero) and with ce_min not after ce_max, since no released CE could load such a mod; a world file is at most 4 MiB.
Optional source files have safe CE paths and single-byte text, at most 1 MiB each, 128 files and 8 MiB in all. Include reads
are also capped across the whole stage at 2,048 files and 16 MiB of text. Before writing,
each original source must be safely readable, and the supplied text must compile to the exact named record in the round-tripping
world being saved. Included headers are read from the selected game; they are not copied or guaranteed unchanged later. This API
does not provide the planned editing page or reopen a previously staged source.
CE loads mods on Linux only for now (Windows refuses them), and keeps them off in replays, recordings, probes, virtual clocks,
pilots and network sessions. The loader remains the authority on the files and other enabled mods present when it runs.

Writing goes through safe_generated_output: the destination is opened as a held directory chain, a destination inside the
selected game folder (or inside any Battle Engine Aquila tree) is refused, every file is written to an exclusive temporary
name and published without replacing anything, every payload is written before mod.json, and a folder that already holds
anything is refused. A failure can leave files, including mod.json, which might enable the mod on the next launch. The helper
detects replacement; it does not lock: a directory moved by another process during the run is not guaranteed to stay outside
the game folder (tools/README.md).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import struct
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from safe_generated_output import SecuredOutputRoot, UnsafeGeneratedOutputError  # noqa: E402
import msl_compile as mc  # noqa: E402

SCHEMA = 1
ID_RE = re.compile(r"[a-z0-9_-]{1,48}")
TEXT_LIMITS = {"name": (1, 64), "version": (1, 32), "author": (0, 64), "description": (0, 1024)}
VERSION_RE = re.compile(r"[0-9]{1,5}(?:\.[0-9]{1,5}){0,3}")
WORLD_PATH = "data/worlds/world{:03d}.wrd"
WORLD_PATH_RE = re.compile(r"data/worlds/world[0-9]{3}\.wrd")
SOURCE_PATH_RE = re.compile(r"data/MissionScripts/level([0-9]{3})/([^/]+)\.msl")
MAX_WORLD_BYTES = 4 << 20
MAX_SOURCE_BYTES = 1 << 20
MAX_SOURCE_FILES = 128
MAX_SOURCE_TOTAL = 8 << 20
MAX_STAGE_INCLUDES = 2048
MAX_STAGE_INCLUDE_CHARS = 16 << 20
MAX_TOTAL_BYTES = 1 << 30
MAX_FILES_PER_MOD = 4096
MAX_WORLD_FILES = 1000
MAX_MANIFEST_BYTES = 256 << 10


class ModStageError(ValueError):
    """A mod that the loader would refuse, or an output the writer will not make."""


class _StageIncludes:
    """Bound all header reads across the source verifications in one stage."""
    def __init__(self, game: Path):
        self.read = mc.includes_from(game)
        self.count = 0
        self.chars = 0

    def __call__(self, path: str) -> str:
        if self.count >= MAX_STAGE_INCLUDES:
            raise mc.CompileError(f"a stage reads at most {MAX_STAGE_INCLUDES} included files")
        self.count += 1
        text = self.read(path)
        self.chars += len(text)
        if self.chars > MAX_STAGE_INCLUDE_CHARS:
            raise mc.CompileError(f"a stage reads at most {MAX_STAGE_INCLUDE_CHARS} characters of included text")
        return text


def world_path(level: int) -> str:
    """The game-relative path CWorld::Load reads a level's world body from."""
    if type(level) is not int or not 0 <= level <= 999:
        raise ModStageError(f"a world level is a number from 0 to 999, not {level!r}")
    return WORLD_PATH.format(level)


def source_level(path: str) -> int | None:
    """A supported, loader-safe mission-source path's level, or None when the path is not admitted."""
    if not isinstance(path, str) or len(path) > 240 or not (match := SOURCE_PATH_RE.fullmatch(path)):
        return None
    part = path.rsplit("/", 1)[-1]
    if len(part) > 128 or part[0] == " " or part[-1] in " ." or any(ord(c) < 32 or ord(c) >= 127 or c in '\\:*?"<>|' for c in part):
        return None
    stem = part.split(".", 1)[0].rstrip(" ").upper()
    if stem in {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} or re.fullmatch(r"(?:COM|LPT)[0-9]", stem):
        return None
    return int(match.group(1))


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


def build_manifest(mod_id: str, name: str, version: str, files: dict[str, bytes], *, author: str = "",
                   description: str = "", ce_min: str | None = None, ce_max: str | None = None) -> bytes:
    """mod.json as the loader reads it: strict JSON, schema 1, only the keys it knows, every file with size and SHA-256."""
    check_identity(mod_id, name, version, author, description, ce_min, ce_max)
    if not files:
        raise ModStageError("a mod lists at least one file")
    if len(files) > MAX_FILES_PER_MOD:
        raise ModStageError(f"a mod lists at most {MAX_FILES_PER_MOD} files")
    manifest: dict = {"schema": SCHEMA, "id": mod_id, "name": name, "version": version}
    if author:
        manifest["author"] = author
    if description:
        manifest["description"] = description
    if ce_min is not None:
        manifest["ce_min"] = ce_min
    if ce_max is not None:
        manifest["ce_max"] = ce_max
    entries = []
    seen: set[str] = set()
    has_world = False
    total = 0
    for path in sorted(files):
        data = files[path]
        folded = path.lower()
        if folded in seen:
            raise ModStageError(f"{path}: a file is listed twice, ignoring case")
        seen.add(folded)
        if WORLD_PATH_RE.fullmatch(path):
            has_world = True
            if type(data) is not bytes or not 0 < len(data) <= MAX_WORLD_BYTES:
                raise ModStageError(f"{path}: a world file is 1 byte to {MAX_WORLD_BYTES} bytes")
        elif source_level(path) is not None:
            if type(data) is not bytes or len(data) > MAX_SOURCE_BYTES:
                raise ModStageError(f"{path}: a mission source is at most {MAX_SOURCE_BYTES} bytes")
        else:
            raise ModStageError(f"{path}: this stager writes world files and mission sources only")
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise ModStageError(f"a mod's files total at most {MAX_TOTAL_BYTES} bytes")
        entries.append({"path": path, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    if not has_world:
        raise ModStageError("a staged mod needs at least one world file")
    manifest["files"] = entries
    text = (json.dumps(manifest, indent=2, ensure_ascii=True) + "\n").encode("ascii")
    if len(text) > MAX_MANIFEST_BYTES:
        raise ModStageError("mod.json would be larger than the loader's 256 KiB")
    return text


def stage_mod(parent: Path, game: Path, mod_id: str, worlds: dict[int, bytes], *, name: str, version: str = "1",
              author: str = "", description: str = "", ce_min: str | None = None, ce_max: str | None = None,
              sources: dict[str, str] | None = None) -> dict:
    """Write <parent>/<mod_id>/ (worlds, optional verified mission sources and mod.json) and return a summary.

    Refuses, with nothing written: a destination inside the selected game folder (or any game tree), a folder that already
    holds anything, mismatched source/world records, and everything build_manifest refuses. Files are published before mod.json."""
    check_identity(mod_id, name, version, author, description, ce_min, ce_max)
    if not worlds:
        raise ModStageError("a staged mod needs at least one world file")
    if len(worlds) > MAX_WORLD_FILES:
        raise ModStageError(f"a mod stages at most {MAX_WORLD_FILES} world files")
    files = {}
    world_total = 0
    world_count = 0
    for level, body in worlds.items():
        world_count += 1
        if world_count > MAX_WORLD_FILES:
            raise ModStageError(f"a mod stages at most {MAX_WORLD_FILES} world files")
        path = world_path(level)
        if type(body) is not bytes or not 0 < len(body) <= MAX_WORLD_BYTES:
            raise ModStageError(f"{path}: a world file is 1 byte to {MAX_WORLD_BYTES} bytes")
        world_total += len(body)
        if world_total > MAX_TOTAL_BYTES:
            raise ModStageError(f"a mod's files total at most {MAX_TOTAL_BYTES} bytes")
        files[path] = body
    if not files:
        raise ModStageError("a staged mod needs at least one world file")
    if sources is not None and len(sources) > MAX_SOURCE_FILES:
        raise ModStageError(f"at most {MAX_SOURCE_FILES} mission sources can be staged at once")
    source_total = 0
    source_count = 0
    read_include = _StageIncludes(game)
    for path, text in (sources or {}).items():
        source_count += 1
        if source_count > MAX_SOURCE_FILES:
            raise ModStageError(f"at most {MAX_SOURCE_FILES} mission sources can be staged at once")
        level = source_level(path)
        if level is None or world_path(level) not in files:
            raise ModStageError(f"{path}: a mission source must name a safe path for a world being staged")
        if not isinstance(text, str) or len(text) > MAX_SOURCE_BYTES:
            raise ModStageError(f"{path}: a mission source is at most {MAX_SOURCE_BYTES} single-byte characters")
        try:
            files[path] = text.encode("latin-1")
        except UnicodeEncodeError:
            raise ModStageError(f"{path}: this game uses single-byte source text; some characters cannot be saved") from None
        source_total += len(files[path])
        if source_total > MAX_SOURCE_TOTAL:
            raise ModStageError(f"mission sources total at most {MAX_SOURCE_TOTAL} bytes")
        if world_total + source_total > MAX_TOTAL_BYTES:
            raise ModStageError(f"a mod's files total at most {MAX_TOTAL_BYTES} bytes")
        try:
            mc.read_game_source(game, path)
        except mc.CompileError:
            raise ModStageError(f"{path}: the game's original source could not be read safely") from None
        check_source_matches_world(path, text, files[world_path(level)], read_include)
    manifest = build_manifest(mod_id, name, version, files, author=author, description=description,
                              ce_min=ce_min, ce_max=ce_max)
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
        raise ModStageError(f"refused: {error} The folder {root} may contain files, including mod.json. The mod may be active on the next game launch. Check the folder before using or removing it.") from error
    except OSError as error:
        raise ModStageError(f"could not write the mod: {error} The folder {root} may contain files, including mod.json. The mod may be active on the next game launch. Check the folder before using or removing it.") from error
    return {"root": str(root), "manifestSha256": hashlib.sha256(manifest).hexdigest(),
            "files": [{"path": path, "size": len(files[path]), "sha256": hashlib.sha256(files[path]).hexdigest()}
                      for path in sorted(files)]}


def check_source_matches_world(path: str, source: str, world: bytes, read_include) -> None:
    """Refuse unless this text compiles to the exact named script record in the world being saved."""
    # Local imports keep the stream-only encoder's import of this writer acyclic.
    import world_resources_encode as wre
    from msl_gate import record_bytes

    try:
        name = path.rsplit("/", 1)[-1][:-4]
        model = wre.read_world_model(world)
        if wre.write_world_body(model) != world:
            raise ModStageError(f"{path}: the staged world does not round-trip exactly")
        scripts = [script for script in model["scripts"] if script["name"] == name]
        if len(scripts) != 1:
            raise ModStageError(f"{path}: the staged world must have exactly one script of this name")
        script = scripts[0]
        compiled = mc.compile_script(name, source, read_include, mc.const_start_of(script), mc.do_once_start_of(script))
        if record_bytes(compiled) != record_bytes(script):
            raise ModStageError(f"{path}: this source does not compile to the script in the staged world")
    except ModStageError:
        raise
    except mc.CompileError as error:
        raise ModStageError(f"{path}: {error}") from None
    except (ValueError, TypeError, KeyError, IndexError, OverflowError, struct.error):
        raise ModStageError(f"{path}: the source and staged world could not be checked") from None
