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

Everything the loader checks at start-up is checked here first, with the loader's own limits (the constants below are kept
equal to mods.cpp): the folder name is the id (1 to 48 lowercase letters, digits, '-' or '_'); name 1 to 64, version 1 to 32,
author up to 64 and description up to 1024 characters (printable ASCII only here, because the loader logs mod text as ASCII);
ce_min and ce_max are one to four numbers of up to five digits joined by dots, compared as the loader compares them (missing
numbers are zero) and with ce_min not after ce_max, since no released CE could load such a mod; a world file is at most 4 MiB.
CE loads mods on Linux only for now (Windows refuses them), and keeps them off in replays, recordings, probes, virtual clocks,
pilots and network sessions.

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
import sys
from pathlib import Path

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
    for path in sorted(files):
        data = files[path]
        if not WORLD_PATH_RE.fullmatch(path):
            raise ModStageError(f"{path}: this stager writes world files only (data/worlds/worldNNN.wrd)")
        if type(data) is not bytes or not 0 < len(data) <= MAX_WORLD_BYTES:
            raise ModStageError(f"{path}: a world file is 1 byte to {MAX_WORLD_BYTES} bytes")
        entries.append({"path": path, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    manifest["files"] = entries
    text = (json.dumps(manifest, indent=2, ensure_ascii=True) + "\n").encode("ascii")
    if len(text) > MAX_MANIFEST_BYTES:
        raise ModStageError("mod.json would be larger than the loader's 256 KiB")
    return text


def stage_mod(parent: Path, game: Path, mod_id: str, worlds: dict[int, bytes], *, name: str, version: str = "1",
              author: str = "", description: str = "", ce_min: str | None = None, ce_max: str | None = None) -> dict:
    """Write <parent>/<mod_id>/ (mod.json and data/worlds/worldNNN.wrd for each level in worlds) and return a summary.

    Refuses, with nothing written: a destination inside the selected game folder (or any game tree), a folder that already
    holds anything, and everything build_manifest refuses. The world files are published first and mod.json last."""
    files = {world_path(level): body for level, body in worlds.items()}
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
        raise ModStageError(f"refused: {error}") from error
    except OSError as error:
        raise ModStageError(f"could not write the mod: {error}") from error
    return {"root": str(root), "manifestSha256": hashlib.sha256(manifest).hexdigest(),
            "files": [{"path": path, "size": len(files[path]), "sha256": hashlib.sha256(files[path]).hexdigest()}
                      for path in sorted(files)]}
