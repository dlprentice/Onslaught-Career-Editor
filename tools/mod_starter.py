#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Scaffold, discover targets for, and validate Onslaught CE schema-1 mods.

This tool bridges the Onslaught Modding & Content Toolkit (JSON Content Catalogue)
and Onslaught CE's mod loader (`port/platform/common/mods.cpp`). It uses only the
Python standard library, never modifies a selected game installation, and publishes
new mod folders safely through `tools/safe_generated_output.py`.

Capabilities:
  1. Discover valid replaceable `data/...` target paths and level IDs from a
     local JSON Content Catalogue (`--catalog PATH --list-targets`).
  2. Scaffold a schema-1-compliant Onslaught CE mod folder (`<out>/<mod-id>/mod.json`
     plus payload files with exact byte sizes and SHA-256 digests) from:
       - a player-supplied `--game-dir` (copying a selected or default replaceable
         `data/...` file, or extracting a level world body with `--world-level`),
       - explicit local payload files (`--payload data/path=local_file`), or
       - a deterministic self-contained world starter fixture (`--world-level NNN --world-fixture`).
  3. Validate a scaffolded (or existing) mod directly with Onslaught CE's built
     `bea --check-mods <mod-id>` binary (`--validate-with PATH`), asserting exit 0
     and `result: 1 passed, 0 refused`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path, PurePosixPath

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from safe_generated_output import SecuredOutputRoot, UnsafeGeneratedOutputError  # noqa: E402

SCHEMA = 1
ID_RE = re.compile(r"^[a-z0-9_-]{1,48}$")
TEXT_LIMITS = {
    "name": (1, 64),
    "version": (1, 32),
    "author": (0, 64),
    "description": (0, 1024),
}
VERSION_RE = re.compile(r"^[0-9]{1,5}(?:\.[0-9]{1,5}){0,3}$")
WORLD_PATH_RE = re.compile(r"^data/worlds/world([0-9]{3})\.wrd$")
ARCHIVE_LEVEL_RE = re.compile(r"^data/resources/([0-9]{3})_res_pc\.aya$", re.IGNORECASE)
SHORT_NAME_RE = re.compile(r"~[0-9]")

MAX_PATH_CHARS = 240
MAX_PATH_COMPONENTS = 12
MAX_COMPONENT_CHARS = 128
MAX_FILE_BYTES = 64 << 20
MAX_WORLD_BYTES = 4 << 20
MAX_FILES_PER_MOD = 4096
MAX_MANIFEST_BYTES = 256 << 10
AYA_PACK_BUFFER = 0x102927
AYA_BLOCK_BYTES = 1 << 20

FORBIDDEN_PATH_CHARS = set('\\:*?"<>|')
WINDOWS_DEVICE_NAMES = frozenset(
    {"con", "prn", "aux", "nul", "conin$", "conout$"}
    | {f"com{i}" for i in range(10)}
    | {f"lpt{i}" for i in range(10)}
)

DEFAULT_SAFE_TARGETS = (
    "data/language/english.dat",
    "data/worldheaders.dat",
    "data/battle engine configurations.dat",
)

HEADLESS_STRIP_ENV = (
    "DISPLAY",
    "WAYLAND_DISPLAY",
    "WAYLAND_SOCKET",
    "XAUTHORITY",
    "DBUS_SESSION_BUS_ADDRESS",
)


class ModStarterError(ValueError):
    """Raised when a mod specification, catalog input, output path, or validation fails."""


def is_windows_device_name(name: str) -> bool:
    """True if `name` (stem before first dot, trailing spaces stripped) is a reserved Windows device name.

    Matches Onslaught CE's `mods.cpp::DeviceName` identically (`CON`, `PRN`, `AUX`, `NUL`, `CONIN$`,
    `CONOUT$`, `COM0`..`COM9`, `LPT0`..`LPT9`, case-insensitive, stripping spaces before the first dot).
    """
    stem = name.split(".", 1)[0].rstrip(" ").casefold()
    return stem in WINDOWS_DEVICE_NAMES


def version_tuple(text: str) -> tuple[int, ...]:
    """Compare dotted version strings identically to mods.cpp (4 components, missing = 0)."""
    parts = [int(part) for part in text.split(".")]
    return tuple(parts + [0] * (4 - len(parts)))


def check_mod_id(mod_id: str) -> str:
    if not isinstance(mod_id, str) or not ID_RE.fullmatch(mod_id):
        raise ModStarterError(
            "mod id must be 1 to 48 lowercase ASCII letters, digits, '-' or '_'"
        )
    if is_windows_device_name(mod_id):
        raise ModStarterError(f"mod id {mod_id!r} is a reserved Windows device name")
    return mod_id


def check_text(label: str, value: str) -> str:
    low, high = TEXT_LIMITS[label]
    if not isinstance(value, str) or not low <= len(value) <= high:
        raise ModStarterError(f"{label} must be {low} to {high} characters")
    if any(not 0x20 <= ord(ch) < 0x7F for ch in value):
        raise ModStarterError(f"{label} must contain printable ASCII only")
    return value


def check_version(label: str, value: str) -> str:
    if not isinstance(value, str) or not VERSION_RE.fullmatch(value):
        raise ModStarterError(
            f"{label} must be 1 to 4 dot-separated integers of up to 5 digits (e.g. 0.1.14)"
        )
    return value


def check_identity(
    mod_id: str,
    name: str,
    version: str,
    *,
    author: str = "",
    description: str = "",
    ce_min: str | None = None,
    ce_max: str | None = None,
) -> None:
    check_mod_id(mod_id)
    check_text("name", name)
    check_text("version", version)
    check_text("author", author)
    check_text("description", description)
    if ce_min is not None:
        check_version("ce_min", ce_min)
    if ce_max is not None:
        check_version("ce_max", ce_max)
    if ce_min is not None and ce_max is not None and version_tuple(ce_min) > version_tuple(ce_max):
        raise ModStarterError(f"ce_min {ce_min} is after ce_max {ce_max}")


def check_mod_path(path: str) -> str:
    """Validate a game-relative mod payload path against Onslaught CE's mods.cpp rules."""
    if not isinstance(path, str) or not path:
        raise ModStarterError("payload path must be a non-empty string")
    if len(path) > MAX_PATH_CHARS:
        raise ModStarterError(f"{path!r}: path exceeds {MAX_PATH_CHARS} characters")
    if not path.startswith("data/"):
        raise ModStarterError(f"{path!r}: mod file paths must start with 'data/'")
    if path.endswith("/"):
        raise ModStarterError(f"{path!r}: path must name a file, not a directory")
    if any(not 0x20 <= ord(ch) < 0x7F for ch in path):
        raise ModStarterError(f"{path!r}: path must contain printable ASCII only")
    if any(ch in FORBIDDEN_PATH_CHARS for ch in path):
        raise ModStarterError(f"{path!r}: path contains a forbidden character")
    parts = path.split("/")
    if len(parts) > MAX_PATH_COMPONENTS:
        raise ModStarterError(f"{path!r}: path exceeds {MAX_PATH_COMPONENTS} components")
    for part in parts:
        if not part or part in (".", ".."):
            raise ModStarterError(f"{path!r}: invalid path component {part!r}")
        if len(part) > MAX_COMPONENT_CHARS:
            raise ModStarterError(f"{path!r}: component exceeds {MAX_COMPONENT_CHARS} characters")
        if part[0] == " " or part[-1] in (" ", "."):
            raise ModStarterError(f"{path!r}: component {part!r} has leading/trailing space or trailing dot")
        if SHORT_NAME_RE.search(part):
            raise ModStarterError(f"{path!r}: component {part!r} contains a Windows 8.3 short-name pattern")
        if is_windows_device_name(part):
            raise ModStarterError(f"{path!r}: component {part!r} is a reserved Windows device name")
    return path


def is_valid_mod_path(path: str) -> bool:
    try:
        check_mod_path(path)
        return True
    except ModStarterError:
        return False


def build_manifest(
    mod_id: str,
    name: str,
    version: str,
    files: dict[str, bytes],
    *,
    author: str = "",
    description: str = "",
    ce_min: str | None = None,
    ce_max: str | None = None,
) -> bytes:
    """Build strict schema-1 mod.json bytes matching Onslaught CE's mods.cpp contract."""
    check_identity(
        mod_id,
        name,
        version,
        author=author,
        description=description,
        ce_min=ce_min,
        ce_max=ce_max,
    )
    if not files:
        raise ModStarterError("a mod must include at least one file")
    if len(files) > MAX_FILES_PER_MOD:
        raise ModStarterError(f"a mod may list at most {MAX_FILES_PER_MOD} files")

    seen_folded: dict[str, str] = {}
    seen_dirs: dict[str, str] = {}
    entries = []
    for rel_path in sorted(files):
        check_mod_path(rel_path)
        parts = rel_path.split("/")
        for depth in range(1, len(parts)):
            prefix = "/".join(parts[:depth])
            folded_dir = prefix.casefold()
            if folded_dir in seen_folded:
                raise ModStarterError(
                    f"case-colliding file and directory paths: {seen_folded[folded_dir]!r} and {prefix!r}"
                )
            if folded_dir in seen_dirs and seen_dirs[folded_dir] != prefix:
                raise ModStarterError(
                    f"case-colliding directory paths: {seen_dirs[folded_dir]!r} and {prefix!r}"
                )
            seen_dirs[folded_dir] = prefix
        folded = rel_path.casefold()
        if folded in seen_folded:
            raise ModStarterError(
                f"duplicate case-folded mod file paths: {seen_folded[folded]!r} and {rel_path!r}"
            )
        if folded in seen_dirs:
            raise ModStarterError(
                f"case-colliding file and directory paths: {rel_path!r} and {seen_dirs[folded]!r}"
            )
        seen_folded[folded] = rel_path
        data = files[rel_path]
        if not isinstance(data, (bytes, bytearray)):
            raise ModStarterError(f"{rel_path}: payload must be bytes")
        raw = bytes(data)
        limit = MAX_WORLD_BYTES if WORLD_PATH_RE.fullmatch(rel_path) else MAX_FILE_BYTES
        if not 0 < len(raw) <= limit:
            raise ModStarterError(f"{rel_path}: size must be 1 to {limit} bytes (got {len(raw)})")
        entries.append(
            {
                "path": rel_path,
                "size": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )

    manifest: dict[str, object] = {
        "schema": SCHEMA,
        "id": mod_id,
        "name": name,
        "version": version,
    }
    if author:
        manifest["author"] = author
    if description:
        manifest["description"] = description
    if ce_min is not None:
        manifest["ce_min"] = ce_min
    if ce_max is not None:
        manifest["ce_max"] = ce_max
    manifest["files"] = entries

    raw_json = (json.dumps(manifest, indent=2, ensure_ascii=True) + "\n").encode("ascii")
    if len(raw_json) > MAX_MANIFEST_BYTES:
        raise ModStarterError(f"mod.json exceeds {MAX_MANIFEST_BYTES} bytes")
    return raw_json


def read_regular_bounded(path: Path, max_bytes: int = MAX_FILE_BYTES) -> bytes:
    """Read a regular, non-symlink file within `max_bytes`."""
    try:
        info = path.lstat()
    except OSError as error:
        raise ModStarterError(f"cannot stat {path}: {error}") from error
    if not stat.S_ISREG(info.st_mode):
        raise ModStarterError(f"{path}: must be a regular file (not a symlink or directory)")
    if info.st_size <= 0 or info.st_size > max_bytes:
        raise ModStarterError(f"{path}: size {info.st_size} outside 1..{max_bytes} bytes")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    try:
        fd = os.open(path, flags)
    except OSError as error:
        raise ModStarterError(f"cannot open {path}: {error}") from error
    try:
        finfo = os.fstat(fd)
        if not stat.S_ISREG(finfo.st_mode) or finfo.st_size != info.st_size:
            raise ModStarterError(f"{path}: file changed while reading")
        chunks: list[bytes] = []
        remaining = finfo.st_size
        while remaining > 0:
            chunk = os.read(fd, min(1 << 20, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        if len(data) != finfo.st_size:
            raise ModStarterError(f"{path}: short read")
        return data
    finally:
        os.close(fd)


def resolve_game_file(game_dir: Path, rel_path: str) -> tuple[str, Path]:
    """Resolve `rel_path` (`data/...`) inside `game_dir` case-insensitively without following symlinks."""
    check_mod_path(rel_path)
    cur = game_dir
    actual_parts: list[str] = []
    for part in rel_path.split("/"):
        try:
            entries = sorted(os.listdir(cur))
        except OSError as error:
            raise ModStarterError(f"cannot search {cur}: {error}") from error
        match = next((e for e in entries if e == part), None)
        if match is None:
            low = part.casefold()
            match = next((e for e in entries if e.casefold() == low), None)
        if match is None:
            raise ModStarterError(f"game file not found for {rel_path!r} under {game_dir}")
        nxt = cur / match
        if nxt.is_symlink():
            raise ModStarterError(f"refusing symlink in game directory: {nxt}")
        actual_parts.append(match)
        cur = nxt
    canonical = "/".join(actual_parts)
    # Normalize leading Data/ to lowercase data/ as expected by mods.cpp.
    if canonical.casefold().startswith("data/"):
        canonical = "data/" + canonical[5:]
    check_mod_path(canonical)
    return canonical, cur


def pick_default_game_target(game_dir: Path) -> tuple[str, Path]:
    """Select the first present safe replaceable file in `game_dir`."""
    for candidate in DEFAULT_SAFE_TARGETS:
        try:
            return resolve_game_file(game_dir, candidate)
        except ModStarterError:
            continue
    raise ModStarterError(
        f"none of the default starter targets ({', '.join(DEFAULT_SAFE_TARGETS)}) exist under {game_dir}; "
        "pass --target <data/...> or --world-level <NNN>"
    )


def make_world_fixture_bytes(level: int, mod_id: str) -> bytes:
    """Create a deterministic, self-contained authored world-fixture payload (zero retail bytes).

    Useful for unit testing and schema-1 `bea --check-mods` verification without retail data.
    For playable in-game level edits, pass `--game-dir` or `--payload-file` with an encoded `.wrd`.
    """
    if not isinstance(level, int) or not 0 <= level <= 999:
        raise ModStarterError(f"world level must be 0..999, got {level!r}")
    body = f"ONSLAUGHT_CE_STARTER_WORLD_FIXTURE level={level:03d} id={mod_id}\n".encode("ascii")
    return b"WRES" + struct.pack("<I", len(body)) + body


def inflate_aya_archive(raw: bytes, label: str = "archive.aya", max_bytes: int = MAX_FILE_BYTES) -> bytes:
    """Inflate a PC `.aya` archive framed as `[u32_le compressed_len][zlib_blob]` blocks (<= 1 MiB/block).

    Matches `tools/world_resources_encode.py` and Onslaught CE's `mods.cpp` block framing.
    """
    if not raw:
        raise ModStarterError(f"{label}: empty .aya archive")
    pos = 0
    total = 0
    blocks: list[bytes] = []
    block_index = 0
    while pos < len(raw):
        if pos + 4 > len(raw):
            raise ModStarterError(f"{label}: truncated block header at offset {pos}")
        (comp_len,) = struct.unpack_from("<I", raw, pos)
        pos += 4
        if comp_len == 0 or comp_len > AYA_PACK_BUFFER or pos + comp_len > len(raw):
            raise ModStarterError(
                f"{label}: invalid compressed block length {comp_len} at block {block_index}"
            )
        blob = raw[pos : pos + comp_len]
        pos += comp_len
        remaining = max_bytes - total
        limit = min(AYA_BLOCK_BYTES, remaining)
        decomp = zlib.decompressobj()
        try:
            block = decomp.decompress(blob, limit + 1)
            if len(block) > limit or decomp.unconsumed_tail:
                raise ModStarterError(f"{label}: inflated block {block_index} exceeds {limit}-byte bound")
            if not decomp.eof or decomp.unused_data:
                raise ModStarterError(f"{label}: incomplete zlib stream or trailing bytes in block {block_index}")
            tail = decomp.flush()
            if len(block) + len(tail) > limit:
                raise ModStarterError(f"{label}: inflated block {block_index} exceeds {limit}-byte bound")
            block += tail
        except zlib.error as error:
            raise ModStarterError(f"{label}: zlib inflate failed at block {block_index}: {error}") from error
        if len(block) < AYA_BLOCK_BYTES and pos < len(raw):
            raise ModStarterError(f"{label}: short inflated block {block_index} before final block")
        blocks.append(block)
        total += len(block)
        block_index += 1
    return b"".join(blocks)


def _iter_chunks(data: bytes, start: int = 0, end: int | None = None, label: str = "archive"):
    end = len(data) if end is None else end
    at = start
    while at < end:
        if at + 8 > end:
            raise ModStarterError(f"{label}: truncated chunk header at offset {at}")
        tag, size = struct.unpack_from("<4sI", data, at)
        payload_start = at + 8
        payload_end = payload_start + size
        if payload_end > end:
            raise ModStarterError(f"{label}: chunk {tag!r} at offset {at} overruns parent")
        yield tag, payload_start, size
        at = payload_end


def extract_wres_from_level_archive(game_dir: Path, level: int) -> bytes:
    """Extract the real-world `RLWD` body (`data/worlds/worldNNN.wrd`) from `<NNN>_res_PC.aya`.

    Walks real PC `.aya` `[u32_le compressed_len][zlib_blob]` blocks, then sibling top-level chunks
    `WRES -> WRLD -> RLWD` (skipping `LVLR`, `WDAT`, and `BSWD`), matching `world_resources_encode.py`.
    """
    if not isinstance(level, int) or not 0 <= level <= 999:
        raise ModStarterError(f"world level must be 0..999, got {level!r}")
    rel = f"data/resources/{level:03d}_res_PC.aya"
    _, archive_path = resolve_game_file(game_dir, rel)
    raw = read_regular_bounded(archive_path, MAX_FILE_BYTES)
    data = inflate_aya_archive(raw, label=rel, max_bytes=MAX_FILE_BYTES)
    for tag, at, size in _iter_chunks(data, 0, len(data), label=rel):
        if tag != b"WRES":
            continue
        for wtag, wat, wsize in _iter_chunks(data, at, at + size, label=rel):
            if wtag != b"WRLD":
                continue
            for ktag, kat, ksize in _iter_chunks(data, wat, wat + wsize, label=rel):
                if ktag == b"RLWD":
                    if not 0 < ksize <= MAX_WORLD_BYTES:
                        raise ModStarterError(
                            f"{rel}: RLWD world payload size {ksize} outside 1..{MAX_WORLD_BYTES}"
                        )
                    return data[kat : kat + ksize]
            raise ModStarterError(f"{rel}: WRES/WRLD contains no RLWD real-world body")
        raise ModStarterError(f"{rel}: WRES contains no WRLD chunk")
    raise ModStarterError(f"{rel}: no top-level WRES chunk found in level archive")


def scaffold_mod(
    out_parent: Path,
    mod_id: str,
    files: dict[str, bytes],
    *,
    name: str,
    version: str = "1.0.0",
    author: str = "",
    description: str = "",
    ce_min: str | None = None,
    ce_max: str | None = None,
    protected_sources: list[Path] | None = None,
) -> dict[str, object]:
    """Atomically publish `<out_parent>/<mod_id>/` with payloads first and `mod.json` last."""
    manifest = build_manifest(
        mod_id,
        name,
        version,
        files,
        author=author,
        description=description,
        ce_min=ce_min,
        ce_max=ce_max,
    )
    mod_root = Path(os.path.abspath(out_parent)) / mod_id
    protected = [Path(os.path.abspath(p)) for p in (protected_sources or [])]
    try:
        with SecuredOutputRoot(mod_root, protected_sources=protected) as secured:
            existing = sorted(os.listdir(mod_root))
            if existing:
                raise ModStarterError(
                    f"{mod_root} already contains {existing[0]!r}: choose a fresh folder (nothing written)"
                )
            for rel_path in sorted(files):
                secured.ensure_directory(mod_root / Path(rel_path).parent)
                secured.atomic_write_new_bytes(mod_root / rel_path, files[rel_path])
            secured.atomic_write_new_bytes(mod_root / "mod.json", manifest)
    except UnsafeGeneratedOutputError as error:
        raise ModStarterError(f"refused unsafe destination: {error}") from error
    except OSError as error:
        raise ModStarterError(f"failed writing mod folder: {error}") from error
    return {
        "id": mod_id,
        "root": str(mod_root),
        "manifestSha256": hashlib.sha256(manifest).hexdigest(),
        "files": [
            {
                "path": rel_path,
                "size": len(files[rel_path]),
                "sha256": hashlib.sha256(files[rel_path]).hexdigest(),
            }
            for rel_path in sorted(files)
        ],
    }


def _classify_target_type(path: str, asset_types: set[str]) -> str:
    low = path.casefold()
    if WORLD_PATH_RE.fullmatch(low):
        return "world"
    if ARCHIVE_LEVEL_RE.fullmatch(low):
        return "archive"
    if low.startswith("data/resources/dxtntextures/") or low.startswith("data/resources/textures/"):
        return "texture"
    if low.startswith("data/resources/meshes/"):
        return "mesh"
    if low.startswith("data/sounds/") or low.startswith("data/music/"):
        return "audio"
    if low.startswith("data/video/"):
        return "video"
    if low.startswith("data/language/") or low.endswith((".dat", ".par", ".sfx")):
        return "table"
    if asset_types:
        return sorted(asset_types)[0]
    return "file"


def _iter_catalog_records(catalog_path: Path):
    """Yield asset/file dicts from a content_catalog directory, .jsonl file, or .json file."""
    target = catalog_path
    if target.is_dir():
        jsonl = target / "assets.jsonl"
        if jsonl.is_file():
            target = jsonl
        else:
            candidates = sorted(p for p in target.glob("*.json") if p.is_file())
            if not candidates:
                raise ModStarterError(f"{catalog_path}: directory contains no assets.jsonl or .json catalog")
            target = candidates[0]
    if not target.is_file():
        raise ModStarterError(f"catalog not found: {catalog_path}")

    if target.suffix.casefold() == ".jsonl":
        with target.open("r", encoding="utf-8") as handle:
            for lineno, line in enumerate(handle, 1):
                text = line.strip()
                if not text:
                    continue
                try:
                    record = json.loads(text)
                except json.JSONDecodeError as error:
                    raise ModStarterError(f"{target}:{lineno}: invalid JSON: {error}") from error
                if isinstance(record, dict):
                    yield record
        return

    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ModStarterError(f"{target}: cannot read JSON catalog: {error}") from error
    if isinstance(payload, list):
        for record in payload:
            if isinstance(record, dict):
                yield record
    elif isinstance(payload, dict):
        for key in ("assets", "files", "records", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                for record in value:
                    if isinstance(record, dict):
                        yield record
                return
        raise ModStarterError(f"{target}: JSON object does not contain an assets/files/records list")
    else:
        raise ModStarterError(f"{target}: unsupported catalog root type")


def discover_catalog_targets(
    catalog_path: Path,
    *,
    target_type: str = "all",
    query: str = "",
    limit: int | None = None,
) -> dict[str, object]:
    """Extract valid replaceable `data/...` target paths and level IDs from a Content Catalogue."""
    containers: dict[str, set[str]] = {}
    levels: set[int] = set()
    records_read = 0

    for record in _iter_catalog_records(catalog_path):
        records_read += 1
        rec_type = str(record.get("type") or "").strip()
        source = record.get("source")
        raw_path: str | None = None
        if isinstance(source, dict) and isinstance(source.get("container"), str):
            raw_path = source["container"]
        elif isinstance(record.get("path"), str):
            raw_path = record["path"]

        if raw_path:
            normalized = raw_path.replace("\\", "/")
            if normalized.casefold().startswith("data/"):
                normalized = "data/" + normalized[5:]
            if is_valid_mod_path(normalized):
                containers.setdefault(normalized, set())
                if rec_type:
                    containers[normalized].add(rec_type)
                match = ARCHIVE_LEVEL_RE.fullmatch(normalized)
                if match:
                    levels.add(int(match.group(1)))

        if rec_type == "level":
            level_obj = record.get("level")
            if isinstance(level_obj, dict) and isinstance(level_obj.get("number"), int):
                if 0 <= level_obj["number"] <= 999:
                    levels.add(level_obj["number"])
            elif isinstance(record.get("levelNumber"), int) and 0 <= record["levelNumber"] <= 999:
                levels.add(record["levelNumber"])

    # Include added-world paths (`data/worlds/worldNNN.wrd`) for every catalogued level.
    targets: list[dict[str, object]] = []
    for path in sorted(containers):
        kind = _classify_target_type(path, containers[path])
        targets.append(
            {
                "path": path,
                "kind": kind,
                "mode": "replace",
                "catalogTypes": sorted(containers[path]),
            }
        )
    for level in sorted(levels):
        wrd = f"data/worlds/world{level:03d}.wrd"
        if wrd not in containers:
            targets.append(
                {
                    "path": wrd,
                    "kind": "world",
                    "mode": "add-or-replace",
                    "level": level,
                    "catalogTypes": ["level"],
                }
            )

    wanted_type = (target_type or "all").strip().casefold()
    wanted_query = (query or "").strip().casefold()
    filtered = [
        row
        for row in targets
        if (wanted_type == "all" or str(row["kind"]).casefold() == wanted_type)
        and (not wanted_query or wanted_query in str(row["path"]).casefold())
    ]
    total_matching = len(filtered)
    if limit is not None and limit >= 0:
        filtered = filtered[:limit]

    return {
        "catalog": str(catalog_path),
        "recordsRead": records_read,
        "levels": sorted(levels),
        "totalTargets": len(targets),
        "matchingTargets": total_matching,
        "targets": filtered,
    }


def _copy_mod_tree_regular(src_mod: Path, dst_mod: Path) -> None:
    """Copy a mod directory as regular files only (no symlinks), matching mods.cpp's rules."""
    if src_mod.is_symlink() or not src_mod.is_dir():
        raise ModStarterError(f"mod directory is missing or not a directory: {src_mod}")
    dst_mod.mkdir(parents=True, exist_ok=True)
    for dirpath, dirnames, filenames in os.walk(src_mod, followlinks=False):
        cur = Path(dirpath)
        rel_dir = cur.relative_to(src_mod)
        for dname in sorted(dirnames):
            if (cur / dname).is_symlink():
                raise ModStarterError(f"refusing symlink directory in mod: {cur / dname}")
            (dst_mod / rel_dir / dname).mkdir(parents=True, exist_ok=True)
        for fname in sorted(filenames):
            src_file = cur / fname
            data = read_regular_bounded(src_file, MAX_FILE_BYTES)
            dst_file = dst_mod / rel_dir / fname
            dst_file.write_bytes(data)


def _discover_bea_runtime_libs(exe: Path) -> list[str]:
    """Locate nearby runtime shared libraries when validating against an uninstalled Linux dev build.

    Returns library directories only when `libdxvk_d3d9.so.0` is actually present in one of them.
    """
    candidates: list[list[Path]] = []
    sibling_lib = exe.parent / "lib"
    if sibling_lib.is_dir():
        candidates.append([sibling_lib])

    dep_roots: list[Path] = []
    if os.environ.get("BEA_PORT_DATA"):
        dep_roots.append(Path(os.environ["BEA_PORT_DATA"]))
    for ancestor in exe.parents:
        dep_roots.append(ancestor / "local-data/port-deps-canonical")
        if ancestor.name == ".worktrees":
            dep_roots.append(ancestor.parent / "local-data/port-deps-canonical")

    seen_roots: set[Path] = set()
    for root in dep_roots:
        resolved = Path(os.path.abspath(root))
        if resolved in seen_roots:
            continue
        seen_roots.add(resolved)
        dirs = [
            resolved / "prefix-sniper/lib",
            resolved / "dxvk-native/usr/lib32",
            resolved / "ffmpeg-shared-sniper/linux/usr/lib",
        ]
        existing = [d for d in dirs if d.is_dir()]
        if existing:
            candidates.append(existing)

    for group in candidates:
        if any((d / "libdxvk_d3d9.so.0").is_file() for d in group):
            return [str(d) for d in group]
    return []


def validate_with_bea(
    bea_exe: Path,
    mod_root: Path,
    mod_id: str,
    *,
    game_dir: Path | None = None,
    timeout: int = 60,
) -> dict[str, object]:
    """Run Onslaught CE's `bea --check-mods <mod_id>` and assert `1 passed, 0 refused`."""
    check_mod_id(mod_id)
    exe = Path(os.path.abspath(bea_exe))
    if not exe.is_file() or not os.access(exe, os.X_OK):
        raise ModStarterError(f"bea executable not found or not executable: {exe}")
    mod_dir = Path(os.path.abspath(mod_root))
    if mod_dir.name != mod_id or not (mod_dir / "mod.json").is_file():
        raise ModStarterError(f"expected mod folder ending in {mod_id!r} with mod.json: {mod_dir}")

    env = {k: v for k, v in os.environ.items() if k not in HEADLESS_STRIP_ENV}
    env.update(
        {
            "SDL_VIDEO_DRIVER": "offscreen",
            "SDL_AUDIO_DRIVER": "dummy",
            "BEA_REPORT_NO_OPEN": "1",
            "BROWSER": "/bin/true",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    runtime_libs = _discover_bea_runtime_libs(exe)
    if runtime_libs:
        existing_ld = env.get("LD_LIBRARY_PATH", "")
        combined_ld = [p for p in runtime_libs + ([existing_ld] if existing_ld else []) if p]
        env["LD_LIBRARY_PATH"] = ":".join(combined_ld)
    resolved_game = Path(os.path.abspath(game_dir)) if game_dir is not None else None
    if resolved_game is not None:
        env["BEA_GAME_DIR"] = str(resolved_game)

    temp_user: tempfile.TemporaryDirectory[str] | None = None
    try:
        if mod_dir.parent.name == "mods":
            user_dir = mod_dir.parent.parent
        else:
            temp_user = tempfile.TemporaryDirectory(prefix="ce-mod-validate-")
            user_dir = Path(temp_user.name)
            _copy_mod_tree_regular(mod_dir, user_dir / "mods" / mod_id)
        env["BEA_USER_DIR"] = str(user_dir)
        cwd = str(resolved_game) if resolved_game is not None and resolved_game.is_dir() else str(user_dir)
        proc = subprocess.run(
            [str(exe), "--check-mods", mod_id],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise ModStarterError(f"bea --check-mods timed out after {timeout}s") from error
    except OSError as error:
        raise ModStarterError(f"failed to execute {exe}: {error}") from error
    finally:
        if temp_user is not None:
            temp_user.cleanup()

    combined = (proc.stdout or "") + (proc.stderr or "")
    passed_marker = "result: 1 passed, 0 refused"
    ok = proc.returncode == 0 and passed_marker in combined
    result = {
        "ok": ok,
        "returncode": proc.returncode,
        "command": [str(exe), "--check-mods", mod_id],
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    if not ok:
        raise ModStarterError(
            f"bea --check-mods {mod_id} failed (exit {proc.returncode}; expected 0 and {passed_marker!r}):\n"
            f"{combined.strip()}"
        )
    return result


def _parse_payload_arg(spec: str) -> tuple[str, Path]:
    if "=" not in spec:
        raise ModStarterError(f"--payload must be <data/rel/path>=<local_file>, got {spec!r}")
    rel_path, local_path = spec.split("=", 1)
    rel_path = rel_path.strip().replace("\\", "/")
    check_mod_path(rel_path)
    return rel_path, Path(local_path.strip())


DEFAULT_DESCRIPTION = "Verified Onslaught CE schema-1 starter mod."
SYNTHETIC_FIXTURE_DESCRIPTION = "Synthetic WRES test fixture (not a playable RLWD world)."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scaffold, discover targets for, and validate Onslaught CE schema-1 mods."
    )
    parser.add_argument("--catalog", type=Path, help="Path to content_catalog.py output dir, assets.jsonl, or JSON file.")
    parser.add_argument("--list-targets", action="store_true", help="List valid replaceable data/... paths and level IDs from --catalog.")
    parser.add_argument("--type", default="all", help="Filter --list-targets by kind (all, texture, mesh, world, archive, audio, video, table).")
    parser.add_argument("--filter", default="", help="Case-insensitive substring filter for --list-targets.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum targets printed by --list-targets.")

    parser.add_argument("--out", type=Path, help="Parent directory where <out>/<id>/ will be created.")
    parser.add_argument("--id", dest="mod_id", default="ce-example-starter", help="Mod folder ID ([a-z0-9_-]{1,48}).")
    parser.add_argument("--name", default="CE Example Starter", help="Human-readable mod display name (1..64 ASCII chars).")
    parser.add_argument("--version", default="1.0.0", help="Mod version string (1..32 ASCII chars).")
    parser.add_argument("--author", default="Community Example", help="Optional author string (0..64 ASCII chars).")
    parser.add_argument(
        "--description",
        default=None,
        help="Optional description (0..1024 ASCII chars).",
    )
    parser.add_argument("--ce-min", default=None, help="Optional minimum Onslaught CE version (e.g. 0.1.14).")
    parser.add_argument("--ce-max", default=None, help="Optional maximum Onslaught CE version.")

    parser.add_argument("--game-dir", type=Path, default=None, help="Read-only retail PC Battle Engine Aquila folder.")
    parser.add_argument("--target", action="append", default=[], help="Game-relative data/... path to copy from --game-dir (repeatable).")
    parser.add_argument("--world-level", type=int, default=None, help="Stage data/worlds/worldNNN.wrd for level NNN (0..999).")
    parser.add_argument("--payload-file", type=Path, default=None, help="Local .wrd payload file for --world-level.")
    parser.add_argument(
        "--synthetic-fixture",
        "--world-fixture",
        dest="synthetic_fixture",
        action="store_true",
        help="Explicit opt-in to emit a non-playable synthetic WRES test fixture for --world-level (zero retail bytes).",
    )
    parser.add_argument("--payload", action="append", default=[], help="Explicit <data/rel/path>=<local_file> entry (repeatable).")

    parser.add_argument("--validate-with", type=Path, default=None, help="Path to Onslaught CE `bea` executable to run `--check-mods <id>`.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.list_targets:
            if args.catalog is None:
                raise ModStarterError("--list-targets requires --catalog <path>")
            report = discover_catalog_targets(
                args.catalog, target_type=args.type, query=args.filter, limit=args.limit
            )
            if args.json:
                print(json.dumps(report, indent=2, sort_keys=True))
            else:
                print(
                    f"Catalog: {report['catalog']} "
                    f"({report['recordsRead']} records, {len(report['levels'])} levels, "
                    f"{report['matchingTargets']}/{report['totalTargets']} matching targets)"
                )
                for row in report["targets"]:
                    print(f"  [{row['kind']:7s}] ({row['mode']:14s}) {row['path']}")
            return 0

        if args.out is None:
            raise ModStarterError("pass --out <dir> to scaffold a mod, or --catalog <path> --list-targets")

        files: dict[str, bytes] = {}
        protected: list[Path] = []
        if args.game_dir is not None:
            protected.append(args.game_dir)

        for spec in args.payload:
            rel_path, local_path = _parse_payload_arg(spec)
            limit = MAX_WORLD_BYTES if WORLD_PATH_RE.fullmatch(rel_path) else MAX_FILE_BYTES
            files[rel_path] = read_regular_bounded(local_path, limit)

        used_synthetic_fixture = False
        if args.synthetic_fixture and args.world_level is None:
            raise ModStarterError("--synthetic-fixture requires --world-level NNN")

        if args.world_level is not None:
            if not 0 <= args.world_level <= 999:
                raise ModStarterError(f"--world-level must be 0..999, got {args.world_level}")
            wrd_path = f"data/worlds/world{args.world_level:03d}.wrd"
            if args.payload_file is not None:
                files[wrd_path] = read_regular_bounded(args.payload_file, MAX_WORLD_BYTES)
            elif args.synthetic_fixture:
                files[wrd_path] = make_world_fixture_bytes(args.world_level, args.mod_id)
                used_synthetic_fixture = True
            elif args.game_dir is not None:
                files[wrd_path] = extract_wres_from_level_archive(args.game_dir, args.world_level)
            else:
                raise ModStarterError(
                    "--world-level requires --game-dir <path> to extract a real playable RLWD world "
                    "(or --payload-file <wrd>); refusing to silently emit a synthetic WRES fixture "
                    "without explicit --synthetic-fixture opt-in"
                )

        for target in args.target:
            if args.game_dir is None:
                raise ModStarterError(f"--target {target!r} requires --game-dir")
            canonical, resolved = resolve_game_file(args.game_dir, target.replace("\\", "/"))
            limit = MAX_WORLD_BYTES if WORLD_PATH_RE.fullmatch(canonical) else MAX_FILE_BYTES
            files[canonical] = read_regular_bounded(resolved, limit)

        if not files:
            if args.game_dir is not None:
                canonical, resolved = pick_default_game_target(args.game_dir)
                files[canonical] = read_regular_bounded(resolved, MAX_FILE_BYTES)
            else:
                raise ModStarterError(
                    "no payload specified: pass --game-dir (with optional --target), "
                    "--world-level NNN --game-dir <path> (or --payload-file PATH / --synthetic-fixture), "
                    "or --payload data/path=file"
                )

        description = (
            args.description
            if args.description is not None
            else (SYNTHETIC_FIXTURE_DESCRIPTION if used_synthetic_fixture else DEFAULT_DESCRIPTION)
        )

        summary = scaffold_mod(
            args.out,
            args.mod_id,
            files,
            name=args.name,
            version=args.version,
            author=args.author,
            description=description,
            ce_min=args.ce_min,
            ce_max=args.ce_max,
            protected_sources=protected,
        )

        if args.validate_with is not None:
            validation = validate_with_bea(
                args.validate_with,
                Path(str(summary["root"])),
                args.mod_id,
                game_dir=args.game_dir,
            )
            summary["validation"] = validation

        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        else:
            print(f"Scaffolded mod {summary['id']} at {summary['root']}")
            for entry in summary["files"]:
                print(f"  {entry['path']} ({entry['size']} bytes, sha256={entry['sha256'][:12]}...)")
            if "validation" in summary:
                print(f"Validated with bea --check-mods {summary['id']}: 1 passed, 0 refused")
        return 0
    except ModStarterError as error:
        print(f"mod_starter: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
