#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Battle Engine Aquila content catalogue: an evidence-based inventory of a retail PC install.

It surveys every file of a selected install (container families, counts, sizes, the loader that reads each family
and whether a repository parser already reads it) and catalogues: loose DDS textures; the texture records in the
resource archives (TEXT, and those inside imposter IMPS, font PLAT and goodie GDIE chunks); loose and embedded CMSH
meshes with their animation modes; levels with their decoded world bodies (WRES: placements of units, squads and
features, markers for every other thing, waypoint paths, the compiled mission scripts and what their literal call
arguments name) and terrain payloads (ERES heightfield and mixers, SURF, SSHD; tools/world_resources_decode.py), the
physics definitions they instantiate; goodies; particle effects; XAP samples, Ogg Vorbis music and voice (with the
transcript line that names each voice file), Bink films; and an inventory of mission scripts, text and symbol
tables. It joins the texture names code builds with sprintf from the map's numbers (sky cube, water, detail mixer)
and the HUD's, and with --decomp also the texture and mesh names game code looks up literally. Each mesh and texture
gets a usage summary (placements, levels, unit/feature names, effects, goodies, code sites) from its relationships.

Every asset gets a stable id, its container and coordinates, a SHA-256 of its bytes, format metadata, an "upscale"
section and provenance. Relationships are recorded only when a loader rule in the decompilation or the data itself
establishes them, and every relationship names its evidence. Descriptions stay null unless evidenced.

The install is only read. The generated catalogue contains retail-derived names and hashes (never retail payload
bytes), so it is written only below this checkout's ignored local-data/ directory and is never committed; every
generated file carries the generatedRetailDerived marker that tools/public_allowlist_safety_check.py rejects.
The schema is tools/content_catalog.schema.json.

Run:  python ./tools/content_catalog.py --game GAME_FOLDER [--decomp ONSLAUGHT_DECOMP] [--out local-data/content-catalog]
      python ./tools/content_catalog.py --self-test
"""
from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import json
import os
import re
import stat
import struct
import subprocess
import sys
from pathlib import Path, PurePosixPath

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(ROOT / "rebuild" / "tools"))

import aya_archive_inventory as aai  # noqa: E402
import aya_cross_platform_compare as cross  # noqa: E402
import aya_texture_fidelity_census as packed  # noqa: E402
import cmsh_animation_usage_census as meshcensus  # noqa: E402
import dds_census  # noqa: E402
import language_dat_decode  # noqa: E402
import world_resources_decode as wrd  # noqa: E402
import worldheaders_decode  # noqa: E402
import xap_bank_walk  # noqa: E402
from safe_generated_output import SecuredOutputRoot  # noqa: E402

SCHEMA_VERSION = 1
ASSET_SCHEMA = "onslaught.content-catalog.asset.v1"
SURVEY_SCHEMA = "onslaught.content-catalog.survey.v1"
COVERAGE_SCHEMA = "onslaught.content-catalog.coverage.v1"
MANIFEST_SCHEMA = "onslaught.content-catalog.manifest.v1"
GENERATED_MARKER = "generatedRetailDerived"  # the safety check rejects tracked files that set it
MAX_FILE_BYTES = 128 * 1024 * 1024
TOOL = "tools/content_catalog.py"
DECOMP = "onslaught-decomp"


def cite(source: str, function: str, va: str) -> str:
    return f"{DECOMP} src/{source} {function} @{va}"


# Loader citations (function bodies in the public decompilation, by source file, function and retail address).
L_READ_RESOURCES = cite("ResourceAccumulator.cpp", "CResourceAccumulator::ReadResources", "0x004d7200")
L_RESOURCE_NAME = cite("ResourceAccumulator.cpp", "CResourceAccumulator::GetFileName", "0x004d6f70")
L_TEX_DESERIALIZE = cite("DXTexture.cpp", "CDXTexture::Deserialize", "0x00559be0")
L_TEX_LOADFRAME = cite("DXTexture.cpp", "CDXTexture::LoadFrame", "0x00557300")
L_TEX_FIND = cite("texture.cpp", "CDXTexture::FindTexture", "0x004f27f0")
L_MESH_DESERIALIZE = cite("mesh.cpp", "CMesh::Deserialize", "0x004aab90")
L_MESH_FINDTEX = cite("mesh.cpp", "CMesh::FindTexture", "0x004aa410")
L_PART_DESERIALIZE = cite("MeshPart.cpp", "CMeshPart::Deserialize", "0x004b27a0")
L_MESH_VB = cite("DXMeshVB.cpp", "CDXMeshVB::Load", "0x0054e160")
L_ANIM = cite("mesh.cpp", "CMesh::GetFrameIncrement", "0x004aa7e0")
L_XAP = cite("pcsoundmanager.cpp", "CPCSoundManager::LoadSampleBank", "0x00517d00")
L_SFX = cite("SoundManager.cpp", "CEffect::LoadSFXFile", "0x004e2530")
L_VOICE = cite("MessageBox.cpp", "data\\sounds\\%s.ogg voice path (COggLoader)", "n/a")
L_OGG_READ = cite("OggFileRead.cpp", "COggFileRead::Open", "0x005246a0")
L_MUSIC = cite("PCMusic.cpp", "CPCMusic::DevicePlay", "0x00515350")
L_FMV = cite("DXFMV.cpp", "CDXFMV::Play", "0x0053f190")
L_FEVIDEO = cite("DXFrontEndVideo.cpp", "CDXFrontEndVideo::Open", "0x005412e0")
L_BRIEFING = cite("FEPBriefing.cpp", "CFEPBriefing::ActiveNotification", "0x00452460")
L_TEXT = cite("text.cpp", "CText::Init", "0x004f2150")
L_PARTICLES = cite("ParticleSet.cpp", "CParticleSet::LoadAllFromDisk", "0x004cda60")
L_HEADERS = cite("world.cpp", "CWorld::LoadHeader", "0x0050d4c0")
L_PHYSICS = cite("WorldPhysicsManager.cpp", "UPhysicsManager::Reload", "0x00510800")
L_BECONFIG = cite("BattleEngineConfigurations.cpp", "UBattleEngineConfigurations::Load", "0x0040f180")
L_BYTESPRITE = cite("bytesprite.cpp", "CByteSprite::Load", "0x004184c0")
L_GOODIES = cite("FEPGoodies.cpp", "CFEPGoodies::Deserialise", "0x0045c870")

# Survey families: (id, matcher on the lower-cased relative path, content kind, loader, existing parser, status).
# Status: "catalogued" = this tool emits asset records; "parsed-elsewhere" = a repository tool parses it but this phase
# does not catalogue it; "unparsed" = no repository parser reads its contents; "not-content" = code, install metadata.
FAMILIES = (
    ("lvlr-resource-archive", lambda p: p.startswith("data/resources/") and p.endswith("_res_pc.aya")
     and p.count("/") == 2, "archive (textures, meshes, world, goodies)", L_READ_RESOURCES + "; name: " + L_RESOURCE_NAME,
     "tools/aya_archive_inventory.py; tools/cmsh_animation_usage_census.py", "catalogued"),
    ("dds-texture-dxtn", lambda p: p.startswith("data/resources/dxtntextures/") and p.endswith(".aya"),
     "texture", L_TEX_LOADFRAME, "tools/dds_census.py", "catalogued"),
    ("dds-texture-uncompressed", lambda p: p.startswith("data/resources/textures/") and p.endswith(".aya"),
     "texture", L_TEX_LOADFRAME, "tools/dds_census.py", "catalogued"),
    ("cmsh-mesh", lambda p: p.startswith("data/resources/meshes/") and p.endswith(".aya"),
     "mesh + animation", L_MESH_DESERIALIZE + "; " + L_PART_DESERIALIZE + "; " + L_MESH_VB,
     "rebuild/tools/cmsh_static_preview.py; tools/cmsh_grammar_walk.py", "catalogued"),
    ("xap-sample-bank", lambda p: p.startswith("data/sounds/") and p.endswith(".xap"),
     "sound effects", L_XAP, "tools/xap_bank_walk.py", "catalogued"),
    ("ogg-music", lambda p: p.startswith("data/music/") and p.endswith(".ogg"),
     "music", L_MUSIC + " (CPCMusic::DeviceAddDirectoryExtsToPlaylist builds the playlist)",
     "tools/content_catalog.py (Ogg/Vorbis headers)", "catalogued"),
    ("ogg-voice", lambda p: p.startswith("data/sounds/") and p.endswith(".ogg"),
     "voice", L_VOICE + "; " + L_OGG_READ, "tools/content_catalog.py (Ogg/Vorbis headers)", "catalogued"),
    ("bink-video", lambda p: p.startswith("data/video/") and p.endswith(".vid"),
     "film", L_FMV + "; " + L_FEVIDEO + "; " + L_BRIEFING, "tools/export_video_manifest.py (hashes); "
     "tools/content_catalog.py (Bink header)", "catalogued"),
    ("sfx-catalog", lambda p: p.startswith("data/sounds/") and p.endswith(".sfx"),
     "sound-event table", L_SFX, "none in tools/ (text; documented in onslaught-preservation formats/ogg-audio.md)",
     "inventoried"),
    ("language-dat", lambda p: p.startswith("data/language/") and p.endswith(".dat"),
     "localized text", L_TEXT, "tools/language_dat_decode.py (entries, voice names, goodie titles)", "catalogued"),
    ("mission-script-msl", lambda p: p.startswith("data/missionscripts/") and (p.endswith(".msl") or p.endswith(".h")),
     "mission script source", "no runtime reader: the compiled form travels in WRES (" + wrd.L_LOADSCRIPTS + "); "
     "onsldef.msl is #included by Career.cpp and game.cpp", "inventory; contents from the compiled copies "
     "(tools/world_resources_decode.py:read_object_code, analyse_script)", "inventoried"),
    ("mission-text-txt", lambda p: p.startswith("data/missionscripts/") and p.endswith(".txt"),
     "mission text", "runtime owner unknown", "inventory only", "inventoried"),
    ("stf-text-table", lambda p: p.endswith(".stf"), "text symbol table",
     "#included by FrontEndText.cpp, MenuItem.cpp, FEPGoodies.cpp (build-time)",
     "tools/language_dat_decode.py:parse_text_stf (symbol names)", "inventoried"),
    ("particle-set-par", lambda p: p.startswith("data/particlesets/") and p.endswith(".par"),
     "particle effects", L_PARTICLES, "tools/content_catalog.py (descriptor names, types, textures)", "catalogued"),
    ("world-headers-dat", lambda p: p == "data/worldheaders.dat", "level headers", L_HEADERS,
     "tools/worldheaders_decode.py", "catalogued"),
    ("default-physics-dat", lambda p: p == "data/default physics.dat", "physics/unit definitions", L_PHYSICS,
     "tools/cmsh_animation_usage_census.py (definition names, mesh and behaviour fields only)", "catalogued"),
    ("battle-engine-config-dat", lambda p: p == "data/battle engine configurations.dat", "battle engine loadouts",
     L_BECONFIG, "none in tools/", "unparsed"),
    ("dial-raw", lambda p: p == "data/dial.raw", "HUD sprite (raw bytes)", L_BYTESPRITE + " (data\\%s.raw)", "none",
     "unparsed"),
    ("splash-tga", lambda p: p.startswith("data/textures/") and p.endswith(".tga"), "image",
     "startup consumer not established", "none", "unparsed"),
    ("manual", lambda p: p.startswith("manuals/"), "manual (HTML and images)", "not read by the game", "none",
     "not-content"),
    ("executable-code", lambda p: "/" not in p and (p.endswith(".exe") or p.endswith(".dll")), "code",
     "operating system", "none", "not-content"),
    ("install-metadata", lambda p: "/" not in p and p.endswith((".txt", ".log", ".bea")),
     "install/runtime state", "various", "none", "not-content"),
    ("save-game", lambda p: p.startswith("savegames/"), "career save", "career loader", "companion", "not-content"),
)

# The CDXTexture record inside a TEXT payload: DXTX(8) CTEX(8) then the 0x158-byte object; its CTexture core sits at
# object +0x08 (field layout: onslaught-decomp src/Texture.h, src/DXTexture.h). Offsets below are payload offsets.
TEXT_OBJECT = 16
TEXT_CORE = TEXT_OBJECT + 8
TEX_FORMAT_NAMES = {0: "UNKNOWN", 1: "A1R5G5B5", 2: "A4R4G4B4", 3: "X8R8G8B8", 4: "A8R8G8B8", 5: "R5G6B5",
                    6: "DXT1", 7: "DXT2", 8: "DXT4", 9: "V8U8", 10: "Q8W8V8U8"}  # CDXTexture::FormatToString
PATH_NAME_LIMIT = 0x41  # LoadFrame's path cut: a file part longer than 65 characters keeps 61 and gains ".aya"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fold(value: str) -> str:
    """stricmp equality key (the loaders compare names case-insensitively)."""
    return value.replace("/", "\\").casefold()


def read_install_file(path: Path) -> bytes:
    """Read one regular, single-link install file without following a symlink; refuse a change during the read."""
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError(f"not a regular file: {path}")
        if before.st_size > MAX_FILE_BYTES:
            raise ValueError(f"file exceeds the {MAX_FILE_BYTES}-byte admission limit: {path}")
        chunks, total = [], 0
        while total < before.st_size:
            chunk = os.read(fd, min(1 << 20, before.st_size - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        after = os.fstat(fd)
        if total != before.st_size or (after.st_size, after.st_mtime_ns) != (before.st_size, before.st_mtime_ns):
            raise ValueError(f"file changed while it was read: {path}")
        return b"".join(chunks)
    finally:
        os.close(fd)


def evidence(kind: str, source: str, rule: str) -> dict:
    return {"kind": kind, "source": source, "rule": rule}


def relation(rtype: str, target: str | None, status: str, ev: list[dict], **extra) -> dict:
    row = {"type": rtype, "target": target, "status": status, "evidence": ev}
    row.update(extra)
    return row


def base_record(asset_id: str, atype: str, name: str, container: str, container_sha: str, *, envelope: str,
                offset: int | None, length: int, raw_sha: str, sha_scope: str, parser: str,
                chunk_path: list[int] | None = None) -> dict:
    return {
        "schema": ASSET_SCHEMA, "id": asset_id, "type": atype, "name": name,
        "source": {"container": container, "containerSha256": container_sha, "envelope": envelope,
                   "offset": offset, "chunkPath": chunk_path or [], "length": length},
        "sha256": raw_sha, "sha256Scope": sha_scope,
        "description": {"text": None, "evidence": None},
        "relationships": [], "upscale": None,
        "provenance": {"tool": TOOL, "parser": parser, "schemaVersion": SCHEMA_VERSION},
    }


# ---------------------------------------------------------------------------------------------------------- survey
def walk_install(game: Path) -> list[dict]:
    rows = []
    for dirpath, dirnames, filenames in os.walk(game, followlinks=False):
        dirnames.sort()
        for filename in sorted(filenames):
            full = Path(dirpath) / filename
            info = full.lstat()
            rel = full.relative_to(game).as_posix()
            if not stat.S_ISREG(info.st_mode):
                rows.append({"path": rel, "size": None, "family": "non-regular", "sha256": None})
                continue
            rows.append({"path": rel, "size": info.st_size, "family": classify(rel)})
    return rows


def classify(rel: str) -> str:
    lower = rel.casefold()
    for family, match, *_ in FAMILIES:
        if match(lower):
            return family
    return "unclassified"


def build_survey(files: list[dict]) -> dict:
    by_family: dict[str, list[dict]] = collections.defaultdict(list)
    for row in files:
        by_family[row["family"]].append(row)
    families = []
    for family, _match, kind, loader, parser, status in FAMILIES:
        rows = by_family.get(family, [])
        extensions = collections.Counter(PurePosixPath(r["path"]).suffix.casefold() or "(none)" for r in rows)
        families.append({"family": family, "contentKind": kind, "files": len(rows),
                         "bytes": sum(r["size"] or 0 for r in rows), "extensions": dict(sorted(extensions.items())),
                         "loader": loader, "existingParser": parser, "status": status})
    unclassified = sorted(r["path"] for r in by_family.get("unclassified", []) + by_family.get("non-regular", []))
    return {"schema": SURVEY_SCHEMA, GENERATED_MARKER: True, "files": len(files),
            "bytes": sum(r["size"] or 0 for r in files), "families": families, "unclassified": unclassified}


# -------------------------------------------------------------------------------------------------------- textures
TEXTURE_FILE_RE = re.compile(r"^(?P<mustbe>mustbe_)?(?P<name>.*)\((?P<frame>[0-9]+)\)(?P<format>[A-Za-z0-9]*)\.aya$",
                             re.IGNORECASE)


def texture_upscale(meta: dict, source_format: str | None) -> dict:
    stored = meta.get("stored_format")
    header = meta.get("header") or {}
    width, height = header.get("width"), header.get("height")
    alpha = (meta.get("alpha") or {}).get("classification", "unknown")
    mips = len(meta.get("mips") or [])
    compressed = bool(stored and stored.startswith("DXT"))
    treatment = []
    if compressed:
        treatment.append("decode the top mip; source carries DXT block compression, so remove block artefacts "
                         "before upscaling; re-encode to BC1/BC3/BC7 or keep lossless for the HD set")
    if stored == "DXT2":
        treatment.append("DXT2 stores premultiplied colour: un-premultiply before upscaling, re-premultiply after")
    if alpha == "binary":
        treatment.append("alpha is a hard on/off mask: upscale the mask separately and re-threshold (no soft edges)")
    elif alpha == "graded":
        treatment.append("alpha is graded: upscale alpha as its own channel")
    if source_format in ("A1R5G5B5", "A4R4G4B4", "R5G6B5"):
        treatment.append(f"authored for {source_format} (16-bit colour): expect banding; deband before upscaling")
    if width and height and max(width, height) <= 32:
        treatment.append("very small source: consider redrawing rather than upscaling")
    if mips > 1:
        treatment.append("regenerate the mip chain from the upscaled top level (lower levels track a 2x2 reduction)")
    return {"sourceResolution": [width, height], "storedFormat": stored, "sourceFormat": source_format,
            "mipLevels": mips, "alpha": alpha, "compressed": compressed, "palette": None,
            "premultipliedAlpha": True if stored == "DXT2" else (False if stored else None),
            "tiling": {"status": "no-mesh-evidence", "uvRange": None, "meshes": 0},
            "suggestedTreatment": treatment,
            "treatmentBasis": "rule-derived from stored format, alpha census and mesh UV ranges; no visual review"}


def catalog_textures(game: Path, files: list[dict]) -> tuple[list[dict], dict[str, dict]]:
    """One record per loose DDS-in-AYA file. Returns the records and a folded relative-path index."""
    records, index = [], {}
    for row in files:
        if row["family"] not in ("dds-texture-dxtn", "dds-texture-uncompressed"):
            continue
        rel = row["path"]
        source = read_install_file(game / rel)
        meta = dds_census.texture_metadata(source, envelope="aya")
        filename = PurePosixPath(rel).name
        match = TEXTURE_FILE_RE.match(filename)
        logical = frame = source_format = None
        truncated = len(filename) == 4 + 0x3D and match is None
        if match:
            logical = match.group("name").replace("%", "\\")
            frame = int(match.group("frame"))
            source_format = match.group("format").upper() or None
            if source_format not in TEX_FORMAT_NAMES.values():
                truncated, source_format = True, None
        name = logical or filename
        dds = meta.get("dds") or {}
        rec = base_record("texture:" + rel.casefold(), "texture", name, rel, meta["source"]["sha256"],
                          envelope="aya-zlib-members(dds)", offset=0, length=dds.get("size") or 0,
                          raw_sha=dds.get("sha256") or meta["source"]["sha256"],
                          sha_scope="inflated DDS file" if dds else "stored container (did not inflate)",
                          parser="tools/dds_census.py:texture_metadata")
        header = meta.get("header") or {}
        rec["texture"] = {
            "status": meta["status"], "shelf": PurePosixPath(rel).parent.name,
            "mustbe": bool(match and match.group("mustbe")), "frame": frame,
            "sourceFormatFromName": source_format, "fileNameTruncated": truncated,
            "width": header.get("width"), "height": header.get("height"), "storedFormat": meta.get("stored_format"),
            "mips": [{"width": m["width"], "height": m["height"], "length": m["length"]} for m in meta["mips"]],
            "alpha": meta.get("alpha"), "problems": meta.get("problems") or []}
        rec["upscale"] = texture_upscale(meta, source_format)
        records.append(rec)
        index[rel.casefold()] = rec
    return records, index


def expected_texture_file(name: str, frame: int, tex_format: int, compressible: bool) -> str:
    """CDXTexture::LoadFrame's resource path with the default -dxtntextures setting (BuildTextureFramePath)."""
    flat = name.replace("\\", "%")
    if compressible:
        shelf, prefix = "dxtntextures", ""
    else:
        shelf, prefix = "textures", "mustbe_"
    file_part = f"{prefix}{flat}({frame}){TEX_FORMAT_NAMES.get(tex_format, 'nk')}.aya"
    if len(file_part) > PATH_NAME_LIMIT:
        file_part = file_part[:PATH_NAME_LIMIT - 4] + ".aya"
    return f"data/resources/{shelf}/{file_part}"


def parse_text_record(payload: bytes) -> dict:
    texture = packed.parse_serialized_texture(payload, platform="PC")
    u8 = lambda o: payload[o]
    i16 = lambda o: struct.unpack_from("<h", payload, o)[0]
    i32 = lambda o: struct.unpack_from("<i", payload, o)[0]
    return {
        "name": texture.name, "width": texture.width, "height": texture.height,
        "frames": len(texture.frames), "mipLevelsPerFrame": [len(f.mips) for f in texture.frames],
        "texFormat": i32(TEXT_OBJECT + 0x144), "requestedFormat": i32(TEXT_CORE + 0xA0),
        "levels": i32(TEXT_OBJECT + 0x148), "resourceLevels": i16(TEXT_OBJECT + 0x156),
        "compressible": u8(TEXT_OBJECT + 0x154), "mipFilter": i32(TEXT_OBJECT + 0x13C),
        "blendMode": i32(TEXT_CORE + 0x80), "lit": i32(TEXT_CORE + 0xAC),
        "uvTransform": list(struct.unpack_from("<4f", payload, TEXT_CORE + 0x84)),
    }


# -------------------------------------------------------------------------------------------------------- archives
ARCHIVE_RE = re.compile(r"^(?:(?P<level>[0-9]{3})|goodie_(?P<goodie>[0-9]+)|(?P<special>base|frontend|loading))"
                        r"_res_pc\.aya$", re.IGNORECASE)


def catalog_archives(game: Path, files: list[dict], texture_index: dict[str, dict], loose_meshes: dict[str, dict],
                     collect: dict | None = None) -> tuple[list[dict], list[dict], list[tuple[str, bytes, dict]], dict]:
    """Archive records, texture-descriptor records, anonymous embedded mesh streams and per-archive mesh names."""
    archives, descriptors = [], {}
    embedded: list[tuple[str, bytes, dict]] = []
    stats = collections.Counter()
    for row in files:
        if row["family"] != "lvlr-resource-archive":
            continue
        rel = row["path"]
        source = read_install_file(game / rel)
        source_sha = sha256(source)
        raw, chunks, members, _env = aai.decode_archive_envelope(source, "pc-chunked-zlib")
        match = ARCHIVE_RE.match(PurePosixPath(rel).name)
        kind = ("level" if match and match.group("level") else "goodie" if match and match.group("goodie")
                else (match.group("special").casefold() if match else "unknown"))
        rec = base_record("archive:" + rel.casefold(), "resource-archive", PurePosixPath(rel).name, rel, source_sha,
                          envelope="aya-zlib-members(lvlr-tag-stream)", offset=0, length=len(raw),
                          raw_sha=sha256(raw), sha_scope="inflated LVLR tag stream",
                          parser="tools/aya_archive_inventory.py:decode_archive_envelope")
        tags = collections.Counter(c.tag for c in chunks)
        rec["archive"] = {"kind": kind, "members": members, "topLevelChunks": len(chunks),
                          "tagCounts": dict(sorted(tags.items()))}
        if kind == "level":
            level = int(match.group("level"))
            rec["archive"]["level"] = level
            rec["relationships"].append(relation(
                "resources-of-level", f"level:{level:03d}", "resolved",
                [evidence("loader-code", L_RESOURCE_NAME, 'level N reads data\\Resources\\%03d_res_%s.aya')],
                targetKind="logical-level"))
        elif kind == "goodie":
            rec["archive"]["goodie"] = int(match.group("goodie"))
        mesh_rows = []
        for chunk in chunks:
            payload = raw[chunk.offset + 8:chunk.offset + 8 + chunk.size]
            if chunk.tag == "TEXT":
                stats["textChunks"] += 1
                add_descriptor(descriptors, rel, source_sha, chunk.index, chunk.offset + 8, payload, texture_index,
                               stats)
            elif chunk.tag == "MESH":
                stats["meshChunks"] += 1
                try:
                    _key, display, method = cross.logical_key("MESH", payload)
                except ValueError as error:
                    mesh_rows.append({"chunk": chunk.index, "status": "unparsed", "reason": str(error)})
                    continue
                name_at = 16 if method.startswith("PMSH/PMS2") else 8
                runtime_id = (struct.unpack_from("<i", payload, name_at + 300)[0]
                              if len(payload) >= name_at + 304 else None)
                if display:
                    target_file = f"data/resources/meshes/m_{display}.aya".casefold()
                    target = loose_meshes.get(target_file)
                    mesh_rows.append({"chunk": chunk.index, "name": display, "nameField": method,
                                      "runtimeId": runtime_id, "target": target["id"] if target else None})
                    stats["namedMeshResolved" if target else "namedMeshUnresolved"] += 1
                else:
                    try:
                        stream = meshcensus._direct_embedded_cmsh(payload)
                    except ValueError as error:
                        mesh_rows.append({"chunk": chunk.index, "name": "", "status": "unparsed",
                                          "reason": str(error)})
                        stats["embeddedMeshUnparsed"] += 1
                        continue
                    offset = chunk.offset + 8 + payload.find(stream[:380])
                    embedded.append((rel, stream, {"archive": rec, "chunk": chunk.index, "offset": offset,
                                                   "archiveSha": source_sha}))
                    mesh_rows.append({"chunk": chunk.index, "name": "", "runtimeId": runtime_id,
                                      "target": f"mesh:embedded:{rel.casefold()}#{chunk.index}"})
                    stats["embeddedMeshes"] += 1
            elif collect is not None and chunk.tag not in ("LVLR", "TARG", "AYAD"):
                collect_chunk(collect, rel, rec, source_sha, chunk, payload, descriptors, texture_index, stats)
        rec["archive"]["meshChunks"] = mesh_rows
        if collect is not None:
            collect["meshIds"][rel] = {m["runtimeId"]: m["target"] for m in mesh_rows
                                       if m.get("runtimeId") is not None and m.get("target")}
        for mrow in mesh_rows:
            if mrow.get("target"):
                rule = ("a named MESH record opens data\\resources\\meshes\\m_<name>.aya" if mrow.get("name")
                        else "an unnamed MESH record carries its CMSH stream inline (PMS2 + 309-byte header)")
                rec["relationships"].append(relation(
                    "loads-mesh", mrow["target"], "resolved",
                    [evidence("loader-code", L_READ_RESOURCES + " -> " + L_MESH_DESERIALIZE, rule),
                     evidence("data", rel, f"MESH chunk {mrow['chunk']}")], chunk=mrow["chunk"]))
            elif mrow.get("name"):
                rec["relationships"].append(relation(
                    "loads-mesh", None, "unresolved", [evidence("data", rel, f"MESH chunk {mrow['chunk']}")],
                    targetName=mrow["name"], chunk=mrow["chunk"]))
        archives.append(rec)
    for desc in descriptors.values():
        occurrences = desc["textureDescriptor"]["occurrences"]
        archive_ids = sorted({"archive:" + o["archive"].casefold() for o in occurrences})
        for archive_id in archive_ids:
            desc["relationships"].append(relation(
                "loaded-by-archive", archive_id, "resolved",
                [evidence("loader-code", L_READ_RESOURCES + " -> " + L_TEX_DESERIALIZE,
                          "each TEXT chunk, and the texture records inside IMPS, PLAT and GDIE, deserialize one "
                          "texture (CDXImposter::DeserializeAll, CPCPlatform::Deserialize, CFEPGoodies::Deserialise)")]))
    return archives, list(descriptors.values()), embedded, stats


def add_descriptor(descriptors: dict, rel: str, archive_sha: str, chunk_index: int, offset: int, payload: bytes,
                   texture_index: dict, stats: collections.Counter, via: str = "TEXT") -> str:
    """Record one serialized texture (a DXTX payload) and return its descriptor id."""
    payload_sha = sha256(payload)
    occurrence = {"archive": rel, "chunk": chunk_index, "offset": offset, "via": via}
    if payload_sha in descriptors:
        descriptors[payload_sha]["textureDescriptor"]["occurrences"].append(occurrence)
        return descriptors[payload_sha]["id"]
    try:
        fields = parse_text_record(payload)
    except (ValueError, struct.error) as error:
        stats["textUnparsed"] += 1
        rec = base_record(f"texture-descriptor:unparsed:{payload_sha[:16]}", "texture-descriptor", "", rel,
                          archive_sha, envelope=f"lvlr-chunk({via})", offset=offset, length=len(payload),
                          raw_sha=payload_sha, sha_scope="DXTX texture record", parser=TOOL + ":parse_text_record",
                          chunk_path=[chunk_index])
        rec["textureDescriptor"] = {"status": "unparsed", "reason": str(error), "occurrences": [occurrence]}
        descriptors[payload_sha] = rec
        return rec["id"]
    name = fields["name"]
    rec = base_record(f"texture-descriptor:{fold(name)}:{payload_sha[:12]}", "texture-descriptor", name, rel,
                      archive_sha, envelope=f"lvlr-chunk({via})", offset=offset, length=len(payload),
                      raw_sha=payload_sha, sha_scope="DXTX texture record (DXTX/CTEX/TFRM)",
                      parser="tools/aya_texture_fidelity_census.py:parse_serialized_texture + " + TOOL,
                      chunk_path=[chunk_index])
    fields["texFormatName"] = TEX_FORMAT_NAMES.get(fields["texFormat"], "nk")
    rec["textureDescriptor"] = {"status": "parsed", **fields, "occurrences": [occurrence],
                                "fieldLayout": "onslaught-decomp src/Texture.h, src/DXTexture.h"}
    for frame in range(fields["frames"]):
        expected = expected_texture_file(name, frame, fields["texFormat"], bool(fields["compressible"]))
        target = texture_index.get(expected.casefold())
        rec["relationships"].append(relation(
            "pixels-from", target["id"] if target else None, "resolved" if target else "unresolved",
            [evidence("loader-code", L_TEX_DESERIALIZE + " -> " + L_TEX_LOADFRAME,
                      "every PC caller passes fromresources=0, so each frame loads the file "
                      "data\\resources\\(dxtntextures|textures\\mustbe_)\\<name, \\ as %>(<frame>)<format>.aya "
                      "chosen by the record's compressible flag, cut to 61 characters + .aya")],
            frame=frame, expectedPath=expected))
        stats["descriptorFramesResolved" if target else "descriptorFramesUnresolved"] += 1
    descriptors[payload_sha] = rec
    return rec["id"]


# ---------------------------------------------------------------------------------------------------------- meshes
def mesh_texture_format(texture_path: str) -> int:
    name = texture_path[8:]
    if name[:2].casefold() == "a8":
        return 4
    if name[:2].casefold() == "a4":
        return 2
    return 1


def uv_ranges(mesh) -> dict[int, list[float]]:
    """Per texture slot: [umin, vmin, umax, vmax] over the vertices its strips index (every bound layer)."""
    ranges: dict[int, list[float]] = {}
    for part in mesh.file_parts():
        if not part.groups or not part.vertices:
            continue
        for group in part.groups:
            slots = {s for s in group.raw_texr_u32 if s < 0x80000000}
            if not slots:
                continue
            us, vs = [], []
            for index in set(group.indices):
                if index < len(part.vertices) and part.vertices[index].uv is not None:
                    u, v = part.vertices[index].uv
                    us.append(u)
                    vs.append(v)
            if not us:
                continue
            for slot in slots:
                r = ranges.setdefault(slot, [min(us), min(vs), max(us), max(vs)])
                r[0], r[1], r[2], r[3] = min(r[0], min(us)), min(r[1], min(vs)), max(r[2], max(us)), max(r[3], max(vs))
    return ranges


def words_to_floats(words: list[int]) -> list[float | None]:
    """Stored float32 bit patterns as numbers (None for a non-finite value, which JSON cannot carry)."""
    values = [struct.unpack("<f", struct.pack("<I", w))[0] for w in words]
    return [v if v == v and abs(v) != float("inf") else None for v in values]


def mesh_summary(meta: dict) -> dict:
    parts = meta.get("parts") or []
    vertices = sum(p["geometry"]["originalVertexCount"] for p in parts)
    strip = sum(g["stripPrimitiveCount"] for p in parts for g in p["geometry"]["pieces"])
    tris = sum(g["distinctIndexTriangleCount"] for p in parts for g in p["geometry"]["pieces"])
    bones = sorted({b for p in parts for b in p["skinning"]["bonePartOrdinals"]})
    lods = meta.get("lodChildren") or []
    return {"status": meta.get("status"), "parts": len(parts), "vertices": vertices, "stripPrimitives": strip,
            "triangles": tris, "skinnedParts": sum(1 for p in parts if p["skinning"]["bonePartOrdinals"]),
            "boneParts": len(bones), "referenceParts": sum(1 for p in parts if p["geometry"]["ownership"] == "reference"),
            "partTypes": dict(sorted(collections.Counter(str(p["partType"]) for p in parts).items())),
            "lodChildren": len(lods),
            "lodChildParts": [len((c["model"].get("parts") or [])) for c in lods],
            "hierarchy": [{"ordinal": p["ordinal"], "name": p["name"], "parent": p["relations"]["parentOrdinal"],
                           "type": p["partType"], "virtualFrames": p["frameLanes"]["virtualFrameCount"],
                           "hierarchyPoses": p["frameLanes"]["hierarchyPoseCount"],
                           "bones": p["skinning"]["bonePartOrdinals"]} for p in parts]}


def catalog_mesh(stream: bytes, *, asset_id: str, name: str, container: str, container_sha: str, envelope: str,
                 offset: int, chunk_path: list[int]) -> tuple[dict, list[dict], dict]:
    record, mesh = meshcensus.mesh_record_from_stream(stream, source_path=container, archive_sha256=container_sha,
                                                      platform="pc", payload_offset=offset,
                                                      chunk_path=tuple(chunk_path))
    meta = record["modelMetadata"]
    rec = base_record(asset_id, "mesh", name or record.get("internalName") or "", container, container_sha,
                      envelope=envelope, offset=offset, length=len(stream), raw_sha=sha256(stream),
                      sha_scope="CMSH stream (inflated)", chunk_path=chunk_path,
                      parser="rebuild/tools/cmsh_static_preview.py:parse_cmsh_stream + "
                             "tools/cmsh_animation_usage_census.py:mesh_record_from_stream")
    rec["mesh"] = {"internalName": record.get("internalName"), **mesh_summary(meta),
                   "textures": [], "emitters": len((meta.get("emitters") or {}).get("rows") or [])}
    slot_uv = uv_ranges(mesh) if mesh is not None else {}
    for slot in meta.get("textures") or []:
        fmt = mesh_texture_format(slot["name"])
        rec["mesh"]["textures"].append({"slot": slot["slotOrdinal"], "name": slot["name"], "requestedFormat": fmt,
                                        "frames": slot["declaredFrameCount"], "uvRange": slot_uv.get(slot["slotOrdinal"]),
                                        "lanes": dict(zip(slot["laneOrder"], words_to_floats(slot["storedLaneWords"][:5])))
                                        if slot["declaredFrameCount"] == 1 else None})
    animations = []
    anim_rows = (meta.get("animations") or {}).get("rows") or []
    moving = [h["name"] for h in rec["mesh"]["hierarchy"] if h["hierarchyPoses"] > 1]
    for row in anim_rows:
        rate = words_to_floats([row["rateBits"]])[0]
        anim = base_record(f"animation:{asset_id}/{row['ordinal']}", "animation", row["name"], container,
                           container_sha, envelope=envelope, offset=offset, length=36, raw_sha=row["recordSha256"],
                           sha_scope="36-byte CAMD record", chunk_path=chunk_path,
                           parser="tools/cmsh_animation_usage_census.py:_animation_metadata")
        anim["animation"] = {"mode": row["mode"], "startFrame": row["start"], "lastFrame": row["last"],
                             "frameCount": row["last"] - row["start"] + 1, "frameScaler": row["frameScaler"],
                             "rate": rate, "rateBits": row["rateBits"], "rateSemantics": row["rateSemantics"],
                             "skeleton": {"mesh": asset_id, "parts": rec["mesh"]["parts"],
                                          "animatedParts": moving},
                             "keyStorage": "per-part HORI/HPOS poses selected per virtual frame by VHFM (in the mesh)"}
        anim["relationships"].append(relation(
            "animates", asset_id, "resolved",
            [evidence("data", container, "CAMD record stored in this mesh's own CMSH stream"),
             evidence("loader-code", L_MESH_DESERIALIZE + "; " + L_ANIM, "the mesh reads its animation modes")]))
        animations.append(anim)
    if anim_rows:
        rec["relationships"].extend(relation("has-animation", a["id"], "resolved",
                                             [evidence("data", container, "CAMD record in this CMSH stream")])
                                    for a in animations)
    rec["upscale"] = {"sourceVertices": rec["mesh"]["vertices"], "sourceTriangles": rec["mesh"]["triangles"],
                      "preserve": ["part names and hierarchy (animation and emitters bind by part)",
                                   "texture slot order and names", "LOD chain"],
                      "suggestedTreatment": ["retopologise or subdivide per part; keep pivots and part transforms",
                                             "rebake to the upscaled textures using the recorded UV ranges"],
                      "treatmentBasis": "rule-derived from structure; no visual review"}
    return rec, animations, slot_uv


def link_mesh_textures(meshes: list[dict], descriptors: list[dict], archives: list[dict]) -> None:
    by_key: dict[tuple[str, int], list[dict]] = collections.defaultdict(list)
    for desc in descriptors:
        d = desc["textureDescriptor"]
        if d["status"] == "parsed" and d["levels"] == -1:
            by_key[(fold(d["name"]), d["requestedFormat"])].append(desc)
    archives_of_mesh: dict[str, set[str]] = collections.defaultdict(set)
    for arc in archives:
        for rel in arc["relationships"]:
            if rel["type"] == "loads-mesh" and rel["target"]:
                archives_of_mesh[rel["target"]].add(arc["source"]["container"].casefold())
    for mesh in meshes:
        mesh_archives = archives_of_mesh.get(mesh["id"], set())
        for arc in sorted(mesh_archives):
            mesh["relationships"].append(relation(
                "loaded-by-archive", "archive:" + arc, "resolved",
                [evidence("loader-code", L_READ_RESOURCES + " -> " + L_MESH_DESERIALIZE, "MESH chunk in this archive")]))
        for slot in mesh["mesh"]["textures"]:
            candidates = by_key.get((fold(slot["name"]), slot["requestedFormat"]), [])
            scoped = [d for d in candidates
                      if {o["archive"].casefold() for o in d["textureDescriptor"]["occurrences"]} & mesh_archives]
            targets = scoped if mesh_archives else candidates
            ev = [evidence("data", mesh["source"]["container"], f"TEXB texture name of slot {slot['slot']}"),
                  evidence("loader-code", L_MESH_DESERIALIZE + " -> " + L_MESH_FINDTEX + " -> " + L_TEX_FIND,
                           "stricmp name match among loaded textures, requested format from the name prefix "
                           "(A8 -> 4, A4 -> 2, else 1) and mip levels -1")]
            status = ("resolved" if len(targets) == 1 else "resolved-per-archive" if targets
                      else "unresolved")
            if mesh_archives and not targets:
                status = "unresolved-in-loading-archives"
            mesh["relationships"].append(relation(
                "uses-texture", targets[0]["id"] if len(targets) == 1 else None, status, ev,
                targets=[d["id"] for d in targets] if len(targets) > 1 else None,
                slot=slot["slot"], targetName=slot["name"], requestedFormat=slot["requestedFormat"],
                scope="descriptors in the archives that load this mesh" if mesh_archives else
                "all archives (this mesh is not loaded by a level archive MESH record)"))


def apply_tiling(meshes: list[dict], descriptors: list[dict], textures: list[dict]) -> None:
    """Carry mesh UV ranges to the descriptor and then to its pixel files (data evidence for wrap/tiling)."""
    desc_by_id = {d["id"]: d for d in descriptors}
    tex_by_id = {t["id"]: t for t in textures}
    for mesh in meshes:
        uv_by_slot = {s["slot"]: s["uvRange"] for s in mesh["mesh"]["textures"]}
        for rel in mesh["relationships"]:
            if rel["type"] != "uses-texture":
                continue
            uv = uv_by_slot.get(rel["slot"])
            for target in ([rel["target"]] if rel["target"] else rel.get("targets") or []):
                desc = desc_by_id[target]
                desc.setdefault("referencedBy", []).append(mesh["id"])
                for prel in desc["relationships"]:
                    if prel["type"] == "pixels-from" and prel["target"]:
                        tex = tex_by_id[prel["target"]]
                        refs = tex.setdefault("referencedBy", [])
                        if mesh["id"] not in refs:
                            refs.append(mesh["id"])
                        tiling = tex["upscale"]["tiling"]
                        tiling["meshes"] += 1
                        if uv is None:
                            continue
                        r = tiling["uvRange"] or list(uv)
                        tiling["uvRange"] = [min(r[0], uv[0]), min(r[1], uv[1]), max(r[2], uv[2]), max(r[3], uv[3])]
    for tex in textures:
        tiling = tex["upscale"]["tiling"]
        r = tiling["uvRange"]
        if r is None:
            continue
        repeats = r[0] < -0.01 or r[1] < -0.01 or r[2] > 1.01 or r[3] > 1.01
        tiling["status"] = "repeats-beyond-0-1" if repeats else "within-0-1"
        tiling["evidence"] = ("vertex UV ranges (the single stored UV set) of the mesh strips that bind this texture "
                              "in any layer, before the texture's stored offset/scale lanes (data)")
        if repeats:
            tex["upscale"]["suggestedTreatment"].append("meshes sample it beyond 0..1 (wrap): upscale tile-aware "
                                                        "with wrapped borders to keep seams invisible")
    for desc in descriptors:
        for prel in desc["relationships"]:
            if prel["type"] == "pixels-from" and prel["target"]:
                refs = tex_by_id[prel["target"]].setdefault("loadedByDescriptors", [])
                refs.append(desc["id"])


def link_unloaded_mesh_names(textures: list[dict], meshes: list[dict]) -> None:
    """A texture file no texture record loads, whose name equals a slot of a mesh no archive loads (data only)."""
    loaded = {m["id"] for m in meshes if any(r["type"] == "loaded-by-archive" for r in m["relationships"])}
    slots = collections.defaultdict(list)
    for m in meshes:
        if m["id"] in loaded:
            continue
        for slot in m["mesh"]["textures"]:
            slots[fold(slot["name"])].append(m["id"])
    loaded_files = collections.defaultdict(list)
    for t in textures:
        if t.get("loadedByDescriptors"):
            loaded_files[(fold(t["name"]), t["texture"]["frame"])].append(t["id"])
    for t in textures:
        if t.get("loadedByDescriptors") or t["texture"]["frame"] is None:
            continue
        twins = loaded_files.get((fold(t["name"]), t["texture"]["frame"]))
        if twins:
            t["relationships"].append(relation(
                "same-name-other-shelf", None, "name-match-unloaded", [evidence(
                    "loader-code", L_TEX_LOADFRAME, "every texture record of this name selects the other shelf by "
                    "its compressible flag, so this copy is not read")], targets=twins))
        owners = slots.get(fold(t["name"]))
        if owners:
            t["relationships"].append(relation(
                "same-name-as-mesh-slot", None, "name-match-unloaded", [evidence(
                    "data", t["source"]["container"], "the file's flattened name equals a texture slot name of a "
                    "mesh that no retail archive loads; no loader joins them")], targets=sorted(set(owners))))


# ----------------------------------------------------------------------------------------------------------- audio
VOICE_LANG_RE = re.compile(r"^data/sounds/(?P<lang>[a-z]+)/", re.IGNORECASE)


def ogg_metadata(data: bytes) -> dict:
    """Ogg page framing and the Vorbis identification header (public container specification)."""
    if data[:4] != b"OggS" or len(data) < 28 or data[4] != 0:
        raise ValueError("not an Ogg stream (version 0)")
    segments = data[26]
    body = 27 + segments
    lacing = data[27:body]
    if len(lacing) != segments:
        raise ValueError("truncated first Ogg page")
    packet = data[body:body + sum(lacing)]
    if packet[:7] != b"\x01vorbis" or len(packet) < 30:
        raise ValueError("first packet is not a Vorbis identification header")
    channels = packet[11]
    rate = struct.unpack_from("<I", packet, 12)[0]
    nominal = struct.unpack_from("<i", packet, 20)[0]
    last = data.rfind(b"OggS")
    granule = None
    while last >= 0:
        if last + 27 <= len(data) and data[last + 4] == 0:
            nseg = data[last + 26]
            end = last + 27 + nseg + sum(data[last + 27:last + 27 + nseg])
            if end == len(data):
                granule = struct.unpack_from("<q", data, last + 6)[0]
                break
        last = data.rfind(b"OggS", 0, last)
    if granule is None or rate == 0:
        raise ValueError("no final Ogg page ends exactly at the end of the file")
    return {"codec": "vorbis", "channels": channels, "sampleRate": rate, "nominalBitrate": nominal,
            "samples": granule, "seconds": round(granule / rate, 3)}


def catalog_audio(game: Path, files: list[dict]) -> list[dict]:
    records = []
    for row in files:
        rel, family = row["path"], row["family"]
        if family in ("ogg-music", "ogg-voice"):
            data = read_install_file(game / rel)
            rec = base_record("audio:" + rel.casefold(), "audio", PurePosixPath(rel).stem, rel, sha256(data),
                              envelope="ogg", offset=0, length=len(data), raw_sha=sha256(data),
                              sha_scope="whole file", parser=TOOL + ":ogg_metadata")
            try:
                meta = {"status": "parsed", **ogg_metadata(data)}
            except ValueError as error:
                meta = {"status": "unparsed", "reason": str(error)}
            meta["role"] = "music" if family == "ogg-music" else "voice"
            lang = VOICE_LANG_RE.match(rel)
            meta["languageLane"] = lang.group("lang").casefold() if lang and family == "ogg-voice" else None
            rec["audio"] = meta
            rec["provenance"]["loader"] = L_MUSIC if family == "ogg-music" else L_VOICE + "; " + L_OGG_READ
            rec["upscale"] = {"sourceSampleRate": meta.get("sampleRate"), "channels": meta.get("channels"),
                              "compressed": True, "suggestedTreatment": [
                                  "lossy Vorbis source: restore from the decoded PCM; keep length and timing exact"],
                              "treatmentBasis": "rule-derived from codec; no listening review"}
            records.append(rec)
        elif family == "xap-sample-bank":
            data = read_install_file(game / rel)
            bank_sha = sha256(data)
            magic, samples = xap_bank_walk.read_bank(data)
            position = 8
            for ordinal, (name, pcm_bytes, adpcm) in enumerate(samples):
                position += 4 + xap_bank_walk.NAME_BYTES + 4
                rec = base_record(f"audio:{rel.casefold()}#{ordinal}", "audio", name, rel, bank_sha,
                                  envelope=f"xap({magic})", offset=position, length=len(adpcm),
                                  raw_sha=sha256(adpcm), sha_scope="stored IMA ADPCM sample bytes",
                                  parser="tools/xap_bank_walk.py:read_bank", chunk_path=[ordinal])
                rec["audio"] = {"status": "parsed", "role": "sound-effect", "codec": "ima-adpcm-4bit",
                                "channels": 1, "sampleRate": xap_bank_walk.SAMPLE_RATE,
                                "samples": pcm_bytes // 2, "seconds": round(pcm_bytes / 2 / xap_bank_walk.SAMPLE_RATE, 3),
                                "languageLane": PurePosixPath(rel).stem.split("_")[1].casefold()}
                rec["provenance"]["loader"] = L_XAP
                rec["upscale"] = {"sourceSampleRate": xap_bank_walk.SAMPLE_RATE, "channels": 1, "compressed": True,
                                  "suggestedTreatment": ["4-bit ADPCM source: decode, denoise, keep sample length"],
                                  "treatmentBasis": "rule-derived from codec; no listening review"}
                records.append(rec)
                position += len(adpcm)
    return records


# ----------------------------------------------------------------------------------------------------------- video
BRIEFING_RE = re.compile(r"^pc_(?P<level>[0-9]{3})(?:_exact|_25)?\.vid$", re.IGNORECASE)


def bink_metadata(data: bytes) -> dict:
    if data[:3] != b"BIK" or len(data) < 44:
        raise ValueError("not a Bink file")
    frames = struct.unpack_from("<I", data, 8)[0]
    width, height, num, den = struct.unpack_from("<4I", data, 0x14)
    flags, tracks = struct.unpack_from("<2I", data, 0x24)
    if not (frames and width and height and num and den):
        raise ValueError("Bink header has a zero field")
    return {"codec": "bink-" + data[:4].decode("latin-1"), "frames": frames, "width": width, "height": height,
            "fps": round(num / den, 3), "fpsRational": [num, den], "seconds": round(frames * den / num, 3),
            "audioTracks": tracks, "flags": flags}


def catalog_video(game: Path, files: list[dict]) -> list[dict]:
    records = []
    for row in files:
        if row["family"] != "bink-video":
            continue
        rel = row["path"]
        data = read_install_file(game / rel)
        rec = base_record("video:" + rel.casefold(), "video", PurePosixPath(rel).stem, rel, sha256(data),
                          envelope="bink", offset=0, length=len(data), raw_sha=sha256(data), sha_scope="whole file",
                          parser=TOOL + ":bink_metadata")
        try:
            meta = {"status": "parsed", **bink_metadata(data)}
        except (ValueError, struct.error) as error:
            meta = {"status": "unparsed", "reason": str(error)}
        rec["video"] = meta
        rec["provenance"]["loader"] = L_FMV + "; " + L_FEVIDEO
        briefing = BRIEFING_RE.match(PurePosixPath(rel).name)
        if briefing and PurePosixPath(rel).parent.name.casefold() == "briefings":
            rec["relationships"].append(relation(
                "briefing-for-level", f"level:{briefing.group('level')}", "resolved",
                [evidence("loader-code", L_BRIEFING, "opens data\\video\\Briefings\\PC_%03d_exact.vid, else "
                          "PC_%03d.vid, else PC_%03d_25.vid for the briefing level (some campaign levels map to "
                          "a shared briefing level in that function's switch)")], targetKind="logical-level"))
        rec["upscale"] = {"sourceResolution": [meta.get("width"), meta.get("height")], "fps": meta.get("fps"),
                          "compressed": True, "suggestedTreatment": [
                              "Bink 1 source: decode frames, upscale temporally-consistently, keep frame count"],
                          "treatmentBasis": "rule-derived from codec; no viewing review"}
        records.append(rec)
    return records


# ------------------------------------------------------------------------------------- phase 2: nested resources
L_IMPOSTERS = cite("DXImposter.cpp", "CDXImposter::DeserializeAll", "0x00543d90")
L_IMPOSTER_CREATE = cite("DXImposter.cpp", "CDXImposter::Create", "0x00543f50")
L_MESH_BY_ID = cite("mesh.cpp", "CMesh::GetMeshByResourceID", "0x004ab330")
L_PLATFORM = cite("PCPlatform.cpp", "CPCPlatform::Deserialize", "0x00515b10")
L_GOODIE_FMV = cite("FEPGoodies.cpp", "get_goodie_fmv (CFEPGoodies::Process)", "0x0045dac3")
L_CUTSCENE_NAME = cite("game.cpp", "MakeCutsceneName", "0x0046d810")
L_GOODIE_LEVEL = cite("FEPGoodies.cpp", "get_goodie_level", "n/a")
L_GOODIE_TITLE = cite("FEPGoodies.cpp", "get_goodie_title, get_goodie_num_texts, get_goodie_text_type_hack", "0x0045ff80")
L_FOLLOWING = cite("text.cpp", "CText::GetFollowingString", "0x004f2500")
L_SOUNDNAME = cite("text.cpp", "CText::GetSoundName", "0x004f24b0")
L_MSGBOX = cite("MessageBox.cpp", "CMessageBox::StartMessage", "0x004b7ea0")
L_TEXT_LOAD = cite("text.cpp", "CText::Load", "0x004f21f0")
L_WORLD = cite("world.cpp", "CWorld::Deserialize", "0x0050b780")
L_PARTICLE_TEX = cite("DXParticleTexture.cpp", "CDXParticleTexture::Get", "0x0054fbc0")
L_PARTICLE_READ = cite("ParticleSet.cpp", "CParticleSet::ReadData", "0x004cd7f0")
L_FMV_PLAY = cite("fmv.cpp", "CFMV::PlayFullscreen", "0x00465640")
PAYLOAD_LOADERS = {
    "ERES": cite("engine.cpp", "CEngine::Deserialize", "0x0044a6e0"),
    "SURF": cite("DXSurf.cpp", "CDXSurf::Deserialize", "0x00556490"),
    "SSHD": cite("StaticShadows.cpp", "CStaticShadows::DeserializeAll", "0x004ee8a0"),
    "VSDS": cite("VertexShader.cpp", "CVertexShader::DeserializeAll", "0x005042f0"),
    "LNDS": "skipped on PC by " + L_READ_RESOURCES,
    "PMIB": "PATCHMANAGER.DeserializeAll via " + L_READ_RESOURCES,
    "DMKR": "landscape damage DeserializeAll via " + L_READ_RESOURCES,
    "WRES": L_WORLD,
}
WORLD_KINDS = ("BSWD", "RLWD")
GOODIE_TYPES = {0: "image", 1: "mesh", 2: "fmv", 3: "level", 4: "cheat"}  # EGoodieType, FEPgoodies.h


def scan_dxtx(payload: bytes) -> list[tuple[int, bytes]]:
    """Every complete, parseable DXTX texture record inside a payload (offset, record bytes)."""
    found, cursor = [], 0
    while True:
        at = payload.find(b"DXTX", cursor)
        if at < 0 or at + 8 > len(payload):
            return found
        size = struct.unpack_from("<I", payload, at + 4)[0]
        record = payload[at:at + 8 + size]
        cursor = at + 4
        if len(record) == 8 + size and record[8:12] == b"CTEX":
            try:
                parse_text_record(record)
            except (ValueError, struct.error):
                continue
            found.append((at, record))
            cursor = at + 8 + size


def chunk_list(data: bytes) -> list[tuple[str, int, bytes]] | None:
    rows, pos = [], 0
    while pos + 8 <= len(data):
        tag = data[pos:pos + 4]
        size = struct.unpack_from("<I", data, pos + 4)[0]
        if not all(0x20 <= b < 0x7F for b in tag) or pos + 8 + size > len(data):
            return None
        rows.append((tag.decode("ascii"), pos, data[pos + 8:pos + 8 + size]))
        pos += 8 + size
    return rows if pos == len(data) else None


def parse_imposters(payload: bytes) -> list[dict]:
    """IMPS: the IMPO list of IMPT records, each with its mesh resource id (IMSH) and view frames (VIEW)."""
    at = payload.find(b"IMPO")
    if at < 0:
        return []
    body = payload[at + 8:at + 8 + struct.unpack_from("<I", payload, at + 4)[0]]
    count = struct.unpack_from("<I", body, 0)[0]
    rows = chunk_list(body[4:]) or []
    out = []
    for tag, _pos, impt in rows:
        if tag != "IMPT":
            continue
        inner = {t: d for t, _p, d in (chunk_list(impt) or [])}
        if "IMSH" not in inner or len(inner["IMSH"]) != 4:
            continue
        label = inner.get("CIMP", b"")[4:68].split(b"\0", 1)[0].decode("latin-1")
        out.append({"meshResourceId": struct.unpack("<i", inner["IMSH"])[0], "storedLabel": label,
                    "viewBytes": len(inner.get("VIEW", b""))})
    if len(out) != count:
        raise ValueError(f"IMPO declares {count} imposters, {len(out)} framed")
    return out


def collect_chunk(collect: dict, rel: str, rec: dict, source_sha: str, chunk, payload: bytes, descriptors: dict,
                  texture_index: dict, stats: collections.Counter) -> None:
    base = chunk.offset + 8
    tag = chunk.tag
    if tag in ("IMPS", "PLAT", "GDIE"):
        ids = [add_descriptor(descriptors, rel, source_sha, chunk.index, base + at, record, texture_index, stats, via=tag)
               for at, record in scan_dxtx(payload)]
        stats[f"nestedTextures{tag}"] += len(ids)
        if tag == "IMPS":
            try:
                imposters = parse_imposters(payload)
            except (ValueError, struct.error) as error:
                imposters, stats["imposterUnparsed"] = [], stats["imposterUnparsed"] + 1
                rec["archive"]["imposterError"] = str(error)
            collect["imposters"].append({"archive": rel, "archiveRec": rec, "descriptors": ids, "imposters": imposters})
        elif tag == "PLAT":
            collect["platform"].append({"archive": rel, "descriptors": ids})
        else:
            number, gtype = struct.unpack_from("<ii", payload, 8)
            mesh_name = None
            at = payload.find(b"PMSH")
            if at >= 0:
                size = struct.unpack_from("<I", payload, at + 4)[0]
                try:
                    _k, mesh_name, _m = cross.logical_key("MESH", payload[at:at + 8 + size])
                except ValueError:
                    mesh_name = None
            collect["goodies"].append({"archive": rel, "archiveRec": rec, "sha": source_sha, "chunk": chunk.index,
                                       "number": number, "type": gtype, "descriptors": ids, "meshName": mesh_name})
        return
    if tag == "WRES":
        collect["wres"][rel] = payload
    rows = chunk_list(payload)
    collect["payloads"].append({"archive": rel, "archiveRec": rec, "sha": source_sha, "tag": tag,
                                "chunk": chunk.index, "offset": base, "length": len(payload),
                                "payloadSha": sha256(payload),
                                "innerTags": [t for t, _p, _d in rows][:16] if rows else None,
                                "decoded": decode_payload(tag, payload)
                                if tag in DECODED_TAGS or tag == "LNDS" else None})


class DescriptorIndex:
    """CDXTexture::FindTexture's match: stricmp name, requested format (0 = any) and mip levels (-1 or exact)."""

    def __init__(self, descriptors: list[dict]):
        self.by_name: dict[str, list[dict]] = collections.defaultdict(list)
        for d in descriptors:
            if d["textureDescriptor"]["status"] == "parsed":
                self.by_name[fold(d["name"])].append(d)

    def find(self, name: str, fmt: int | None, levels: int | None, archives: set[str] | None = None) -> list[dict]:
        out = []
        for d in self.by_name.get(fold(name), []):
            td = d["textureDescriptor"]
            if fmt not in (None, 0) and td["requestedFormat"] != fmt:
                continue
            if levels is not None and td["levels"] != levels:
                continue
            if archives is not None and not ({o["archive"].casefold() for o in td["occurrences"]} & archives):
                continue
            out.append(d)
        return out


def find_relation(rtype: str, found: list[dict], ev: list[dict], **extra) -> dict:
    status = "resolved" if len(found) == 1 else "resolved-per-archive" if found else "unresolved"
    return relation(rtype, found[0]["id"] if len(found) == 1 else None, status, ev,
                    targets=[d["id"] for d in found] if len(found) > 1 else None, **extra)


def catalog_goodies(collect: dict, game: Path, loose: dict, dindex: DescriptorIndex, videos: dict, text: dict
                    ) -> list[dict]:
    titles = goodie_titles(text)
    records = []
    for g in sorted(collect["goodies"], key=lambda x: x["number"]):
        number = g["number"]
        rec = base_record(f"goodie:{number:03d}", "goodie", titles.get(number) or f"goodie {number}", g["archive"],
                          g["sha"], envelope="lvlr-chunk(GDIE)", offset=None, length=0, raw_sha=g["sha"],
                          sha_scope="stored goodie archive", parser=TOOL + ":collect_chunk", chunk_path=[g["chunk"]])
        rec["goodie"] = {"number": number, "goodieType": GOODIE_TYPES.get(g["type"], str(g["type"])),
                         "archive": g["archive"]}
        rec["provenance"]["loader"] = L_GOODIES
        if number in titles:
            rec["description"] = {"text": titles[number], "evidence": "english.dat entry GOODIE_TEXT_1_TITLE + the "
                                  "goodie's text offset (" + L_GOODIE_TITLE + "; " + L_FOLLOWING + ")"}
        for did in g["descriptors"]:
            rec["relationships"].append(relation("shows-texture", did, "resolved", [evidence(
                "loader-code", L_GOODIES + " -> " + L_TEX_DESERIALIZE, "the goodie's texture records")]))
        if g["meshName"]:
            target = loose.get(f"data/resources/meshes/m_{g['meshName']}.aya".casefold())
            rec["relationships"].append(relation("shows-mesh", target["id"] if target else None,
                                                 "resolved" if target else "unresolved", [evidence(
                    "loader-code", L_GOODIES + " -> " + L_MESH_DESERIALIZE,
                    "a named MESH record opens data\\resources\\meshes\\m_<name>.aya")], targetName=g["meshName"]))
        if rec["goodie"]["goodieType"] == "fmv":
            if 201 <= number <= 232:
                n = 33 if number == 232 else number - 200
                names = [f"cutscenes/{n:02d}", f"cutscenes/{n:02d}_small"]
                rule = "goodies 201-232 play MakeCutsceneName(n): cutscenes\\%02d.vid, else cutscenes\\%02d_small.vid"
            else:
                names = ["UsTheMovie"] if number == 77 else ["GILL_M_on_a_fork"]
                rule = "goodie 77 plays UsTheMovie, every other FMV goodie GILL_M_on_a_fork"
            target = next((videos[k] for k in (f"video:data/video/{n}.vid".casefold() for n in names) if k in videos), None)
            rec["relationships"].append(relation("plays-video", target, "resolved" if target else "unresolved",
                                                 [evidence("loader-code", L_GOODIE_FMV + "; " + L_CUTSCENE_NAME + "; "
                                                           + L_FMV_PLAY, rule)]))
        if rec["goodie"]["goodieType"] == "level":
            level = {66: 901, 67: 902, 68: 903, 69: 904, 70: 905}.get(number, 901)
            rec["relationships"].append(relation("opens-level", f"level:{level:03d}", "resolved", [evidence(
                "loader-code", L_GOODIE_LEVEL, "goodies 66-70 open levels 901-905 (default 901)")]))
        records.append(rec)
    return records


def goodie_titles(text: dict) -> dict[int, str]:
    """get_goodie_title: English entry GOODIE_TEXT_1_TITLE followed by the sum of the earlier goodies' text counts."""
    english = text.get("english")
    symbol_ids = text.get("symbols", {})
    first = symbol_ids.get("GOODIE_TEXT_1_TITLE")
    if not english or first is None:
        return {}
    entries = english["entries"]
    start = next((i for i, e in enumerate(entries) if e["id"] == first), None)
    if start is None:
        return {}

    def num_texts(n: int) -> int:
        if n > 77:
            return 0
        if n > 65:
            return 9
        return 12 if n <= 7 else 9

    titles, offset = {}, 0
    for n in range(78):
        if start + offset < len(entries) and entries[start + offset]["text"]:
            titles[n] = entries[start + offset]["text"]
        offset += num_texts(n)
    return titles


def link_imposters(collect: dict, descriptors_by_id: dict) -> None:
    for row in collect["imposters"]:
        mesh_ids = collect["meshIds"].get(row["archive"], {})
        for did in row["descriptors"]:
            desc = descriptors_by_id[did]
            for imp in row["imposters"]:
                target = mesh_ids.get(imp["meshResourceId"])
                desc["relationships"].append(relation(
                    "imposter-of-mesh", target, "resolved" if target else "unresolved",
                    [evidence("loader-code", L_IMPOSTERS + " -> " + L_IMPOSTER_CREATE + " -> " + L_MESH_BY_ID,
                              "IMSH resource id matched to the runtime id in this archive's MESH record (PMS2 +300)"),
                     evidence("data", row["archive"], f"IMPT label {imp['storedLabel']!r}")],
                    archive=row["archive"].casefold(), meshResourceId=imp["meshResourceId"]))


PHYSICS_STATEMENTS = {1: "unit", 8: "feature", 9: "hazard"}  # EPhysicsStatement (CPhysicsScriptStatements.h)
# UPhysicsManager::SpawnSquad (0050f4b0): a squad exists for UB_MECH, UB_AIRCRAFT, UB_GROUND_UNIT, UB_INFANTRY and
# UB_WARSPITE (the default arm); every other behaviour returns NULL (EUnitBehaviour, WorldPhysicsManager.h).
SQUAD_BEHAVIOURS = frozenset({0, 1, 2, 3, 21})
L_SPAWNSQUAD = cite("WorldPhysicsManager.cpp", "UPhysicsManager::SpawnSquad", "0x0050f4b0")
PLACEMENT_OIDS = (8, 25, 28, 35)  # unit, building, squad, feature: the LoadWorld arms that name a physics definition
TEXT_TABLE_ID = "text-table:data/language/english.dat"


def physics_names(data: bytes) -> dict:
    """The Unit, Feature and Hazard statement names in load order (UPhysicsManager::Reload; strcmp lookups)."""
    if len(data) < 6 or struct.unpack_from("<H", data, 0)[0] != 0x12:
        raise ValueError("unsupported physics-definition framing")
    out: dict[str, list[str]] = {"unit": [], "feature": [], "hazard": []}
    offset = 2
    while struct.unpack_from("<i", data, offset)[0] != -1:
        rtype, _size = struct.unpack_from("<II", data, offset)
        offset += 8
        end = data.index(b"\0", offset)
        name = data[offset:end].decode("latin-1")
        offset = end + 1
        while True:
            _fid, size = struct.unpack_from("<II", data, offset)
            offset += 8 + size
            marker = struct.unpack_from("<i", data, offset)[0]
            offset += 4
            if marker == -1:
                break
        if rtype in PHYSICS_STATEMENTS:
            out[PHYSICS_STATEMENTS[rtype]].append(name)
    return out


def world_scripts_order(worlds: dict) -> list[tuple[str, dict]]:
    """WORLD.mScripts as GetCopyOfScript walks it: LoadWorld reads the real world's scripts, then Load(base) appends
    the base world's."""
    return [(tag, s) for tag in ("RLWD", "BSWD") for s in worlds.get(tag, {}).get("scripts", [])]


def world_paths_order(worlds: dict) -> list[tuple[str, dict]]:
    """CWaypointManager::mPaths as FindNearest walks it: the nested base load appends its paths before the real
    world reaches its own CWaypointManager::Load."""
    return [(tag, p) for tag in ("BSWD", "RLWD") for p in worlds.get(tag, {}).get("waypointPaths", [])]


def catalog_world(collect: dict, game: Path, loose: dict, archives: list[dict], script_ids: set[str],
                  text: dict, stats: collections.Counter) -> dict:
    """WRES world bodies decoded in CWorld::LoadWorld's order: definitions, placements (things naming a physics
    definition), markers (every other thing), waypoint paths and the compiled mission scripts, with their joins."""
    out = {"definitions": [], "placements": [], "markers": [], "paths": [], "scripts": [], "worlds": {}}
    physics_path = game / "data" / "default physics.dat"
    if not physics_path.is_file():
        return out
    physics_bytes = read_install_file(physics_path)
    physics = meshcensus._physics_mesh_definitions(physics_bytes)
    names = physics_names(physics_bytes)
    physics_sha = sha256(physics_bytes)
    unit_shell = {u["definition"]: u for u in physics["unitDefinitions"]}
    lookup = {"units": set(names["unit"]), "features": set(names["feature"]), "hazards": set(names["hazard"]),
              "squadless": {u["definition"] for u in physics["unitDefinitions"]
                            if u["factorySelector"] not in SQUAD_BEHAVIOURS}}
    kinds_of: dict[str, set] = collections.defaultdict(set)
    for kind, rows in names.items():
        for name in rows:
            kinds_of[name].add(kind)
    def_by_name = {}
    for name in sorted(kinds_of, key=lambda n: (fold(n), n)):
        cands = physics["definitions"].get(name, [])
        rec = base_record(f"definition:{fold(name)}", "definition", name, "data/default physics.dat", physics_sha,
                          envelope="physics-statement-table", offset=None, length=0, raw_sha=physics_sha,
                          sha_scope="whole definitions file", parser=TOOL + ":physics_names + tools/"
                          "cmsh_animation_usage_census.py:_physics_mesh_definitions")
        rec["provenance"]["loader"] = L_PHYSICS
        shell = unit_shell.get(name)
        rec["definition"] = {"kinds": sorted(kinds_of[name]), "memberShell": shell["memberShell"] if shell else None,
                             "behaviour": shell["factorySelector"] if shell else None,
                             "meshNames": [c["mesh"] for c in cands]}
        for c in cands:
            target = loose.get("data/resources/meshes/" + meshcensus._loose_mesh_key(c["mesh"]))
            rec["relationships"].append(relation(
                "uses-mesh", target["id"] if target else None, "resolved" if target else "unresolved",
                [evidence("data", "data/default physics.dat", f"record type {c['physicsRecordType']} field "
                          f"{c['meshFieldId']} names mesh {c['mesh']!r} (onslaught-preservation "
                          "formats/wres-instance-join.md)")], targetName=c["mesh"]))
        out["definitions"].append(rec)
        def_by_name[name] = rec
    archive_by_rel = {a["source"]["container"]: a for a in archives}
    english = text.get("english")
    text_ids = {e["id"] for e in english["entries"]} if english else set()
    symbol_of = {ident: name for name, ident in text.get("symbols", {}).items()}

    def def_relation(rtype: str, name: str, rule: str, source: str = wrd.L_LOADWORLD) -> dict:
        d = def_by_name.get(name)
        return relation(rtype, d["id"] if d else None, "resolved" if d else "unresolved",
                        [evidence("loader-code", source, rule)], targetName=name)

    for rel, wres in sorted(collect["wres"].items()):
        arc = archive_by_rel[rel]
        level = arc["archive"].get("level")
        if level is None:
            continue
        try:
            wrld = meshcensus._chunk_payload(wres, "WRLD", rel)
        except ValueError:
            stats["worldBodiesUndecoded"] += 1
            continue
        worlds = {}
        wdat = next((wrld[c.offset + 8:c.offset + 16] for c in aai.parse_top_level_chunks(wrld) if c.tag == "WDAT"
                     and c.size >= 8), None)
        # CWorld::Deserialize reads the base and the real world's level numbers from WDAT
        base_level, real_level = struct.unpack("<ii", wdat) if wdat else (None, level)
        folder_of = {"RLWD": real_level, "BSWD": base_level}
        for wc in aai.parse_top_level_chunks(wrld):
            if wc.tag not in WORLD_KINDS:
                continue
            body = wrld[wc.offset + 8:wc.offset + 8 + wc.size]
            try:
                worlds[wc.tag] = wrd.parse_world_body(body, lookup, base=wc.tag == "BSWD")
            except (wrd.DecodeError, struct.error) as error:
                stats["worldBodiesUndecoded"] += 1
                worlds[wc.tag] = {"error": str(error)}
                continue
            stats["worldBodiesDecoded"] += 1
        decoded = {t: w for t, w in worlds.items() if "error" not in w}
        out["worlds"][level] = worlds
        named = {meshcensus._normalized_mesh_identity(m["name"]): m for m in arc["archive"]["meshChunks"] if m.get("name")}
        script_ids_here: list[tuple[str, str, dict]] = []  # (world, id, script) in GetCopyOfScript order
        for tag, s in world_scripts_order(decoded):
            script_ids_here.append((tag, f"script-code:{level:03d}:{tag.lower()}#{s['ordinal']}", s))
        path_ids_here = [(tag, f"waypoint-path:{level:03d}:{tag.lower()}#{p['ordinal']}", p)
                         for tag, p in world_paths_order(decoded)]
        thing_ids: dict[str, list[str]] = collections.defaultdict(list)  # exact thing name -> placement/marker ids

        def script_relation(rtype: str, name: str, source_rule: str) -> dict:
            hit = next((sid for _t, sid, s in script_ids_here if s["name"] == name), None)
            return relation(rtype, hit, "resolved" if hit else "unresolved", [evidence(
                "loader-code", wrd.L_SETSCRIPT + " -> " + wrd.L_COPYSCRIPT, source_rule + "; GetCopyOfScript takes the first "
                "strcmp match in WORLD.mScripts (" + wrd.L_LOADWORLD + " reads the real world's scripts before the base "
                "world's)")], targetName=name)

        def msl_path(tag: str, name: str) -> str:
            folder = folder_of.get(tag)
            return f"data/MissionScripts/level{folder if folder is not None else level:03d}/{name}.msl"

        def thing_common(rec: dict, init: dict, tag: str) -> None:
            if init["script"]:
                rec["relationships"].append(script_relation("runs-script", init["script"],
                                                            "the thing's script string names its compiled script"))
                msl = msl_path(tag, init["script"])
                sid = "script:" + msl.casefold()
                found = sid in script_ids
                rec["relationships"].append(relation(
                    "script-source", sid if found else None, "name-match" if found else "unresolved",
                    [evidence("data", rel, "placement script string " + (
                        "equals the .msl file stem in the world's MissionScripts folder (WDAT's level number; no "
                        "runtime loader reads .msl files, the compiled script travels in WRES)" if found else
                        "has no .msl file of that stem in the world's MissionScripts folder"))],
                    targetName=msl))
            if init["name"]:
                thing_ids[init["name"]].append(rec["id"])

        for tag, w in sorted(decoded.items()):
            world_ev = "lvlr-chunk(WRES/WRLD/" + tag + ")"
            for t in w["things"]:
                init = t["init"]
                oid = t["oid"]
                is_placement = oid in PLACEMENT_OIDS
                rid = f"{'placement' if is_placement else 'marker'}:{level:03d}:{tag.lower()}@{t['offset']}"
                rec = base_record(rid, "placement" if is_placement else "marker",
                                  init["name"] or t.get("definition") or t["kind"], rel,
                                  arc["source"]["containerSha256"], envelope=world_ev, offset=t["offset"],
                                  length=t["length"], raw_sha=arc["sha256"],
                                  sha_scope="inflated archive (world records are not hashed separately)",
                                  parser="tools/world_resources_decode.py:parse_world_body")
                rec["provenance"]["loader"] = wrd.L_LOADWORLD + "; " + wrd.L_SPAWNINIT + "; " + wrd.L_INITLOAD
                common = {"level": level, "world": tag, "worldLevel": folder_of.get(tag), "thingType": oid,
                          "kind": t["kind"], "ordinal": t["ordinal"],
                          "slot": t["slot"], "position": init["position"], "orientation": init["orientation"],
                          "allegiance": init["allegiance"], "active": bool(init["active"]),
                          "attachScriptsToUnits": None if init["attachScriptsToUnits"] is None
                          else bool(init["attachScriptsToUnits"]), "meshNumber": init["meshNumber"],
                          "target": init["target"], "name": init["name"] or None, "script": init["script"] or None,
                          "spawnScript": init["spawnScript"] or None}
                if is_placement:
                    rec["placement"] = {**common, "definition": t["definition"], "diesOn": t["diesOn"]}
                    if oid == 28:
                        rec["placement"]["squad"] = init["squad"]
                    rec["relationships"].append(def_relation(
                        "instance-of", t["definition"], "the record's name string is passed to "
                        "UPhysicsManager::GetUnitData / GetFeatureData (strcmp)"))
                    want = 35 if oid == 35 else 8
                    exact = []
                    for cand in physics["definitions"].get(t["definition"], []):
                        if int(cand["wresThingType"]) != want:
                            continue
                        row = named.get(meshcensus._normalized_mesh_identity(cand["mesh"]))
                        if row and row.get("target"):
                            exact.append(row)
                    if len(exact) == 1:
                        rec["relationships"].append(relation("uses-mesh", exact[0]["target"], "resolved", [
                            evidence("data", "data/default physics.dat", "definition mesh field"),
                            evidence("loader-code", L_READ_RESOURCES + " -> " + L_MESH_DESERIALIZE,
                                     f"this archive's MESH chunk {exact[0]['chunk']} loads that mesh")]))
                    else:
                        rec["relationships"].append(relation("uses-mesh", None, "unresolved", [evidence(
                            "data", "data/default physics.dat", f"{len(exact)} same-archive named MESH candidates")]))
                    stats["placements"] += 1
                else:
                    rec["marker"] = dict(common)
                    for key in ("spawner", "start", "sphereTrigger", "cutscene", "tree", "wall"):
                        if key in init:
                            rec["marker"][key] = init[key]
                    if oid == 39:
                        rec["marker"]["definition"] = t["definition"]
                        rec["marker"]["diesOn"] = t["diesOn"]
                        rec["relationships"].append(def_relation(
                            "instance-of", t["definition"], "a hazard's name string is passed to "
                            "UPhysicsManager::GetHazardData (strcmp)"))
                    if "spawner" in init:
                        sp = init["spawner"]
                        if sp["spawnUnit"]:
                            rec["relationships"].append(def_relation(
                                "spawns-unit", sp["spawnUnit"], "a spawner's spawn-unit string names a unit "
                                "definition (CSpawnerInitThing::Load; strcmp lookup)", wrd.L_INITLOAD))
                        if sp["spawnerSpawnScript"]:
                            rec["relationships"].append(script_relation(
                                "sets-script", sp["spawnerSpawnScript"], "the spawner's spawn script names the "
                                "script its spawned units run"))
                    stats["markers"] += 1
                thing_common(rec, init, tag)
                (out["placements"] if is_placement else out["markers"]).append(rec)
        # waypoint paths: CWaypointPath::Load indexes LoadWorld's things[] (the record's slot), keeping waypoints only
        for tag, pid, p in path_ids_here:
            w = decoded[tag]
            by_ordinal = {t["ordinal"]: t for t in w["things"]}
            rec = base_record(pid, "waypoint-path", p["name"], rel, arc["source"]["containerSha256"],
                              envelope="lvlr-chunk(WRES/WRLD/" + tag + ")", offset=p["offset"], length=0,
                              raw_sha=arc["sha256"], sha_scope="inflated archive (paths are not hashed separately)",
                              parser="tools/world_resources_decode.py:parse_world_body")
            rec["provenance"]["loader"] = wrd.L_WAYPOINTS
            kept = [m for m in p["members"] if m["isWaypoint"]]
            rec["waypointPath"] = {"level": level, "world": tag, "ordinal": p["ordinal"], "members": len(p["members"]),
                                   "waypoints": len(kept), "ignoredByLoader": len(p["members"]) - len(kept)}
            for n, m in enumerate(kept):
                t = by_ordinal[m["thingOrdinal"]]
                rec["relationships"].append(relation(
                    "path-member", f"marker:{level:03d}:{tag.lower()}@{t['offset']}", "resolved", [evidence(
                        "loader-code", wrd.L_WAYPOINTS, "the path's index is a slot of LoadWorld's things[] (a record "
                        "takes a slot only when its physics lookup or SpawnThing succeeds) and the thing is a "
                        "waypoint")], order=n))
            stats["pathMembersResolved"] += len(kept)
            stats["pathMembersIgnored"] += len(p["members"]) - len(kept)
            out["paths"].append(rec)
        # compiled scripts
        for tag, sid, s in script_ids_here:
            code = s["code"]
            analysis = wrd.analyse_script(code)
            calls = analysis["calls"]
            rec = base_record(sid, "script-code", s["name"], rel, arc["source"]["containerSha256"],
                              envelope="lvlr-chunk(WRES/WRLD/" + tag + ")/script", offset=s["offset"],
                              length=s["length"], raw_sha=s["sha256"],
                              sha_scope="compiled script bytes (name, object code, 10-byte pad)",
                              parser="tools/world_resources_decode.py:read_object_code + analyse_script")
            rec["provenance"]["loader"] = wrd.L_LOADSCRIPTS + "; " + wrd.L_OBJECTCODE + "; " + wrd.L_SYMTAB
            roles = {role: wrd.literal_args(calls, role) for role in sorted({r for r in wrd.ARG_ROLES.values()})}
            values = lambda role: sorted({a["value"] for a in roles[role] if a["value"] is not None}, key=str)
            objectives = [{"native": c["native"], "pc": c["pc"],
                           "args": [None if a is None else a["value"] for a in c["args"]]}
                          for c in calls if c["native"] in wrd.OBJECTIVE_NATIVES]
            rec["scriptCode"] = {
                "level": level, "world": tag, "worldLevel": folder_of.get(tag), "ordinal": s["ordinal"],
                "instructions": len(code["instructions"]),
                "symbols": len(code["symbols"]), "eventFunctions": len(code["eventFunctions"]),
                "handledEvents": analysis["handledEvents"], "fixedEventHandlers": analysis["fixedEventHandlers"],
                "nativeCalls": dict(sorted(collections.Counter(c["native"] for c in calls).items())),
                "objectives": objectives,
                # the VM holds a signed int; CText::GetString takes the DWORD id
                "textIds": sorted({a["value"] & 0xFFFFFFFF for r in ("text", "text-speaker") for a in roles[r]
                                   if isinstance(a["value"], int)}),
                "units": values("unit"), "waypointPaths": values("waypoint-path"), "thingNames": values("thing-name"),
                "scripts": values("script"), "postedEvents": values("event"), "samples": values("sample"),
                "effects": values("effect"), "spawners": values("spawner"), "emitters": values("emitter"),
                "nonLiteralArguments": {r: sum(1 for a in roles[r] if a["value"] is None) for r in roles
                                        if any(a["value"] is None for a in roles[r])},
                "argumentRule": "a CALL's arguments are its n preceding OP_PUSH instructions (" + wrd.L_SPAWNMESHES
                                + "); a pushed symbol is literal when it holds a stored value and no OP_POP/OP_GETTOP "
                                "writes it (" + wrd.L_PUSH + ")"}
            stats["scriptCalls"] += len(calls)
            stats["scriptCallArguments"] += sum(len(c["args"]) for c in calls)
            stats["scriptCallArgumentsLiteral"] += sum(1 for c in calls for a in c["args"] if a is not None)
            msl = msl_path(tag, s["name"])
            msl_id = "script:" + msl.casefold()
            if msl_id in script_ids:
                rec["relationships"].append(relation("compiled-from", msl_id, "name-match", [evidence(
                    "data", rel, "the compiled script's name equals the .msl file stem in the world's MissionScripts "
                    "folder (WDAT's level number; the compiler is not part of the game; no loader reads .msl files)")],
                    targetName=msl))
            else:
                rec["relationships"].append(relation("compiled-from", None, "unresolved", [evidence(
                    "data", rel, "no .msl file of that stem in the world's MissionScripts folder")], targetName=msl))
            seen = set()
            for role in ("text-speaker", "text"):
                for a in roles[role]:
                    if not isinstance(a["value"], int) or (role, a["value"] & 0xFFFFFFFF) in seen:
                        continue
                    text_id = a["value"] & 0xFFFFFFFF
                    seen.add((role, text_id))
                    ok = text_id in text_ids
                    stats["scriptTextIdsResolved" if ok else "scriptTextIdsUnresolved"] += 1
                    rec["relationships"].append(relation(
                        "uses-text", TEXT_TABLE_ID if ok else None, "resolved" if ok else "unresolved", [evidence(
                            "loader-code", wrd.L_NATIVES + " " + a["native"] + " -> " + wrd.L_TEXTGET,
                            f"argument {a['argument']} is a text id (the int as a DWORD); english.dat " + (
                                "has an entry with that id" if ok else "has no entry with that id"))],
                        textId=text_id, textSymbol=symbol_of.get(text_id), role=role))
            for name in values("unit"):
                stats["scriptUnitsResolved" if name in def_by_name else "scriptUnitsUnresolved"] += 1
                rec["relationships"].append(def_relation(
                    "spawns-unit", name, "SpawnThing's first argument goes to UPhysicsManager::GetUnitData and "
                    "SpawnThingByName (strcmp)", wrd.L_NATIVES + " SpawnThing"))
            for name in values("waypoint-path"):
                hit = next((pid for _t, pid, p in path_ids_here if fold(p["name"]) == fold(name)), None)
                stats["scriptPathsResolved" if hit else "scriptPathsUnresolved"] += 1
                rec["relationships"].append(relation(
                    "follows-path", hit, "resolved" if hit else "unresolved", [evidence(
                        "loader-code", wrd.L_NATIVES + " FollowWaypoint -> " + wrd.L_FINDNEAREST,
                        "the first path whose name matches (_stricmp) in CWaypointManager::mPaths (the base world's "
                        "paths load first)")], targetName=name))
            for name in values("script"):
                rec["relationships"].append(script_relation("sets-script", name, "SpawnThing's fourth argument, "
                                                            "SetScript's and SetSpawnScript's names a script"))
            rec["_thingNames"] = values("thing-name")
            out["scripts"].append(rec)
        for rec in out["scripts"]:
            if rec["scriptCode"]["level"] != level or "_thingNames" not in rec:
                continue
            for name in rec.pop("_thingNames"):
                hits = sorted(thing_ids.get(name, []))
                stats["scriptThingNamesMatched" if hits else "scriptThingNamesUnmatched"] += 1
                rec["relationships"].append(relation(
                    "names-thing", hits[0] if len(hits) == 1 else None, "name-match" if hits else "unresolved",
                    [evidence("loader-code", wrd.L_NATIVES + " GetThingRef/Teleport/PlayCutscene -> " + wrd.L_FINDTHING,
                              "the argument is compared (strcmp) with the names of the world's named things; which "
                              "things join WORLD.mNamedThings is not traced, so this is a name match with the level's "
                              "placement and marker names")],
                    targets=hits if len(hits) > 1 else None, targetName=name))
    return out


DECODED_TAGS = {"ERES": "parse_eres", "SURF": "parse_surf", "SSHD": "parse_sshd"}
L_KEMPY = cite("DXKempyCube.cpp", "CDXKempyCube::Load", "0x005440a0") + " -> " + cite(
    "landscape.cpp", "GetCubeTextureName", "0x0048de30")
L_WATER = cite("DXWater.cpp", "CDXWater::Load", "0x0055b230")
L_DETAIL = cite("landscape.cpp", "CLandscape::LoadMixerTexture", "0x0048dec0")
L_MIXERS = cite("maptex.cpp", "CMapTex::LoadAll", "0x004914b0")
L_HUD_SPEAKERS = cite("Hud.cpp", "CHud::InitResources", "0x00481650")
CUBE_FACES = ("cent", "up", "right", "down", "left")
MIXER_NAMES = ("grass", "rock", "sand", "snow", "road", "concrete")  # maptex.cpp MIXER_NAMES (0062da98)
HUD_SPEAKERS = 6  # HUD_NUM_SPEAKERS (Hud.h)


def decode_payload(tag: str, payload: bytes) -> dict:
    """The structure a PC loader reads from a level payload, or the reason it could not be decoded."""
    if tag == "LNDS":
        return {"status": "skipped-by-pc-loader", "bytes": len(payload)}
    try:
        return {"status": "decoded", **getattr(wrd, DECODED_TAGS[tag])(payload)}
    except (wrd.DecodeError, struct.error, ValueError) as error:
        return {"status": "undecoded", "reason": str(error)}


def level_rule_textures(terrain: dict) -> list[dict]:
    """Texture names the level's map settings make the code build with sprintf (CMap::Deserialize's calls)."""
    hf = terrain["heightField"]
    rows = []
    for face in CUBE_FACES:
        rows.append({"role": "sky-cube", "name": f"cubes\\cube{hf['skyCube']:02d}_{face}.tga", "format": 0, "levels": 1,
                     "site": L_KEMPY, "rule": "cubes\\cube%.2d_%s.tga from the map's sky-cube number (CMap::Deserialize "
                     "-> CEngine::SetKempyCube) and the face (cent, up, right, down, left); FindTexture(name, 0, 0, 1)"})
    for kind in ("reflection", "caustic"):
        rows.append({"role": "water", "name": f"mixers\\{kind}{hf['water']:02d}.tga", "format": 0, "levels": -1,
                     "site": L_WATER, "rule": f"mixers\\{kind}%.2d.tga from the map's water number (CMap::Deserialize "
                     "-> CEngine::SetWater); FindTexture(name, 0, 0, -1)"})
    rows.append({"role": "terrain-detail", "name": f"mixers\\detail{hf['detailMixer']:02d}.tga", "format": 0,
                 "levels": -1, "site": L_DETAIL, "rule": "mixers\\detail%.2d.tga from the map's detail number "
                 "(CMap::Deserialize); GetTextureByName(name) with its default format 0 and levels -1"})
    return rows


def hud_rule_textures() -> list[dict]:
    return [{"role": "hud-speaker", "name": f"hud\\speaker{i}.tga", "format": 0, "levels": 1, "site": L_HUD_SPEAKERS,
             "rule": "hud\\speaker%1d.tga for i in 0..HUD_NUM_SPEAKERS-1; GetTextureByName(name, TEXFMT_UNKNOWN, "
             "TEX_NORMAL, 1)"} for i in range(HUD_SPEAKERS)]


def link_rule_textures(levels: list[dict], terrain_by_level: dict, dindex: DescriptorIndex, descriptors_by_id: dict,
                       stats: collections.Counter) -> list[dict]:
    """Join the sprintf-built names to the loaded texture records: per level within its own archive, the HUD's in any
    archive. Each joined record gets one named-by-code relation per rule role (the levels are listed in it)."""
    report = []
    reached: dict[tuple[str, str, str], list] = collections.defaultdict(list)
    for lvl in levels:
        n = lvl["level"]["number"]
        terrain = terrain_by_level.get(n)
        if not terrain:
            continue
        archive = lvl["level"]["resourceArchive"]
        rel = archive.split(":", 1)[1] if archive else None
        for row in level_rule_textures(terrain):
            found = dindex.find(row["name"], row["format"], row["levels"], {rel} if rel else set())
            stats["ruleTextureNamesResolved" if found else "ruleTextureNamesUnresolved"] += 1
            lvl["relationships"].append(find_relation("texture-by-rule", found, [evidence(
                "loader-code", row["site"], row["rule"] + "; looked up in this level's archive")],
                role=row["role"], targetName=row["name"]))
            for d in found:
                reached[(d["id"], row["role"], row["site"] + "\t" + row["rule"])].append(f"{n:03d}")
            report.append({"level": f"{n:03d}", "role": row["role"], "name": row["name"],
                           "resolved": [d["id"] for d in found]})
        hf = terrain["heightField"]
        loaded = terrain["mixerMips"][0]["set"] != hf["mixerSet"] if terrain["mixerMips"] else None
        lvl["level"]["terrain"]["mixerTextureFiles"] = {
            "names": [f"data\\textures\\mixers\\{m}{hf['mixerSet']:02d}.tga" for m in MIXER_NAMES],
            "readFromDisk": loaded, "rule": L_MIXERS + ": data\\textures\\mixers\\%s%.2d.tga for MIXER_NAMES and the "
            "map's mixer set, read only when the deserialized set differs; " + (
                "the ERES mixer mips already hold this set, so no file is read (the pixels are in ERES)"
                if loaded is False else "the ERES mixer set differs, so the files would be read (none is installed)")}
    for row in hud_rule_textures():
        found = dindex.find(row["name"], row["format"], row["levels"])
        stats["ruleTextureNamesResolved" if found else "ruleTextureNamesUnresolved"] += 1
        for d in found:
            reached[(d["id"], row["role"], row["site"] + "\t" + row["rule"])].append("all")
        report.append({"level": None, "role": row["role"], "name": row["name"], "resolved": [d["id"] for d in found]})
    for (did, role, site_rule), where in sorted(reached.items()):
        site, rule = site_rule.split("\t", 1)
        scope = "front end and every level" if where == ["all"] else "levels " + ", ".join(sorted(set(where)))
        descriptors_by_id[did]["relationships"].append(relation("named-by-code", None, "code-rule", [evidence(
            "loader-code", site, rule + f" ({scope})")], role=role))
    return report


def world_summary(w: dict) -> dict:
    if "error" in w:
        return {"status": "undecoded", "reason": w["error"]}
    return {"status": "decoded", "version": w["version"], "worldType": w["header"]["worldType"],
            "battleEngineConfigurations": w["header"]["battleEngineConfigurations"], "baseLevel": w["baseLevel"],
            "mapNumber": w["mapNumber"], "namedMeshes": w["namedMeshes"], "scripts": len(w["scripts"]),
            "things": len(w["things"]), "thingSlots": w["slotsCounted"],
            "thingsByKind": dict(sorted(collections.Counter(t["kind"] for t in w["things"]).items())),
            "thingsWithoutSlot": sorted({t.get("definition") or t["kind"] for t in w["things"] if t["slot"] is None}),
            "treeGroups": w["treeGroups"], "treesInGroups": w["treesInGroups"],
            "treeTypes": [{"name": t["name"], "count": t["count"]} for t in w["treeTypes"]],
            "influenceMap": w["influenceMap"], "waypointPaths": len(w["waypointPaths"]), "timings": w["timings"],
            "occupancyGridVersions": w["occupancyGridVersions"], "levelStartTime": w["levelStartTime"],
            "loader": wrd.L_LOADWORLD}


PAR_TEXTURE_PREFIX = 32  # CDXParticleTexture::Get looks up path + 32 ("C:\dev\Onslaught2\data\textures\")


def catalog_particles(game: Path, files: list[dict], dindex: DescriptorIndex) -> list[dict]:
    records = []
    for row in files:
        if row["family"] != "particle-set-par":
            continue
        rel = row["path"]
        data = read_install_file(game / rel)
        lines = data.decode("latin-1").splitlines()
        blocks, current = [], None
        for line in lines:
            key, _, value = line.partition(" ")
            if key == "Particle_Descriptor_Type":
                current = {"type": int(value), "fields": []}
                blocks.append(current)
            elif current is not None:
                current["fields"].append((key, value))
        for ordinal, block in enumerate(blocks):
            name = next((v for k, v in block["fields"] if k == "Particle_Descriptor_Name"), "")
            rec = base_record(f"effect:{rel.casefold()}#{ordinal}", "effect", name, rel, sha256(data),
                              envelope="token-archive-text", offset=None, length=0, raw_sha=sha256(data),
                              sha_scope="whole particle-set file", parser=TOOL + ":catalog_particles",
                              chunk_path=[ordinal])
            rec["provenance"]["loader"] = L_PARTICLES + "; " + L_PARTICLE_READ
            refs = [v for k, v in block["fields"] if k in ("Initial", "Death", "Mover") and v != "NONE"]
            textures, mode = [], None
            for key, value in block["fields"]:
                if key == "Blend_Mode":
                    mode = int(value)
                elif key == "Texture" and len(value) > PAR_TEXTURE_PREFIX:
                    textures.append((value, mode))
            rec["effect"] = {"descriptorType": block["type"], "textures": [t for t, _m in textures],
                             "references": refs}
            for path, mode in textures:
                lookup = path[PAR_TEXTURE_PREFIX:]
                # CParticleDescriptor reads Texture as Get(sval, mBlendMode + 1); Get's format is A4R4G4B4 for
                # modes 2-3, else R5G6B5. Without an earlier Blend_Mode the member's value is not established.
                fmt = None if mode is None else (2 if 2 <= mode + 1 <= 3 else 5)
                rec["relationships"].append(find_relation(
                    "uses-texture", dindex.find(lookup, fmt, 1),
                    [evidence("data", rel, f"Texture token of descriptor {name!r} (Blend_Mode {mode})"),
                     evidence("loader-code", cite("ParticleDescriptor.cpp", "texture token: Get(sval, mBlendMode + 1)",
                                                  "n/a") + " -> " + L_PARTICLE_TEX + " -> " + L_TEX_FIND,
                              "name = path + 32; format A4R4G4B4 when Blend_Mode + 1 is 2-3, else R5G6B5; mip "
                              "levels 1" + ("" if mode is not None else "; no Blend_Mode before the texture, so "
                                            "only name and levels are matched"))],
                    targetName=lookup, requestedFormat=fmt))
            records.append(rec)
    return records


CODE_TEXTURE_RE = re.compile(r'\b(FindTexture|GetTextureByName)\(\s*"((?:[^"\\]|\\.)+)"\s*(,[^;]*?)?\)\s*[;,)]')
CODE_MESH_RE = re.compile(r'\bGetMesh\(\s*"((?:[^"\\]|\\.)+)"')
FUNCTION_RE = re.compile(r"^(?P<sig>.*?\b(?P<name>[A-Za-z_][\w:~]*)\s*\([^;]*)//\s*FUNCTION:\s*(?P<va>0x[0-9a-fA-F]+)")


def code_int(token: str) -> int | None:
    token = token.strip()
    if re.fullmatch(r"-?\d+", token):
        return int(token)
    if token.startswith("TEXFMT_"):
        names = {v: k for k, v in TEX_FORMAT_NAMES.items()}
        return names.get(token[7:])
    return {"TEX_NORMAL": 0}.get(token)


def code_references(decomp: Path | None) -> dict:
    """Literal texture and mesh names passed to the lookups in the decompilation's sources (optional input)."""
    refs = {"textures": [], "meshes": [], "source": None}
    if decomp is None:
        return refs
    src = decomp / "src"
    refs["source"] = "onslaught-decomp src/ (" + (git_head_of(decomp) or "unknown commit") + ")"
    for path in sorted(src.glob("*.cpp"), key=lambda p: p.name.casefold()):
        function = None
        for number, line in enumerate(path.read_text(encoding="latin-1").splitlines(), 1):
            m = FUNCTION_RE.match(line)
            if m:
                function = f"{m.group('name')} @{m.group('va').lower()}"
            for m in CODE_TEXTURE_RE.finditer(line):
                args = [a for a in (m.group(3) or "").lstrip(",").split(",") if a.strip()]
                values = [code_int(a) for a in args]
                if m.group(1) == "GetTextureByName":
                    fmt = values[0] if len(values) > 0 else 0
                    levels = values[2] if len(values) > 2 else -1
                else:
                    fmt = values[0] if len(values) > 0 else None
                    levels = values[2] if len(values) > 2 else None
                refs["textures"].append({"name": m.group(2).replace("\\\\", "\\"), "format": fmt, "levels": levels,
                                         "site": f"{DECOMP} src/{path.name}:{number} {function or '(file scope)'}",
                                         "call": m.group(1)})
            for m in CODE_MESH_RE.finditer(line):
                refs["meshes"].append({"name": m.group(1).replace("\\\\", "\\"),
                                       "site": f"{DECOMP} src/{path.name}:{number} {function or '(file scope)'}"})
    return refs


def git_head_of(path: Path) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def link_code_references(refs: dict, dindex: DescriptorIndex, descriptors_by_id: dict, loose: dict,
                         stats: collections.Counter) -> list[dict]:
    unresolved = []
    for ref in refs["textures"]:
        found = dindex.find(ref["name"], ref["format"], ref["levels"])
        stats["codeTextureSites"] += 1
        if not found:
            stats["codeTextureSitesUnresolved"] += 1
            unresolved.append(ref)
        for d in found:
            d["relationships"].append(relation("named-by-code", None, "code-site", [evidence(
                "loader-code", ref["site"], f"{ref['call']}(\"{ref['name']}\", format {ref['format']}, levels "
                f"{ref['levels']}) finds this loaded texture by name" + (
                    "" if ref["format"] is not None and ref["levels"] is not None else
                    " (non-literal format or levels: name-only match)"))]))
    for ref in refs["meshes"]:
        target = loose.get("data/resources/meshes/" + meshcensus._loose_mesh_key(ref["name"]))
        stats["codeMeshSites"] += 1
        if target is None:
            stats["codeMeshSitesUnresolved"] += 1
            continue
        target["relationships"].append(relation("named-by-code", None, "code-site", [evidence(
            "loader-code", ref["site"], f"CMesh::GetMesh(\"{ref['name']}\") names this mesh")]))
    return unresolved


LANGUAGE_LANES = ("english", "french", "german", "spanish", "italian")


def read_text_tables(game: Path, files: list[dict]) -> dict:
    """Language tables (entries with id, text and voice name) and the text.stf symbol ids."""
    out: dict = {"tables": {}, "symbols": {}}
    for row in files:
        if row["family"] == "language-dat":
            path = game / row["path"]
            data = read_install_file(path)
            lang = language_dat_decode.parse_lang_dat(path)
            entries = [language_dat_decode.entry_record(lang, data, e) for e in lang.entries]
            out["tables"][PurePosixPath(row["path"]).stem.casefold()] = {"path": row["path"], "sha": sha256(data),
                                                                          "entries": entries, "version": lang.ver}
    stf = game / "data" / "MissionScripts" / "text" / "text.stf"
    if stf.is_file():
        out["symbols"] = {name: ident for ident, name in language_dat_decode.parse_text_stf(stf).items()}
    out["english"] = out["tables"].get("english")
    return out


def link_voice(text: dict, audio_by_path: dict, stats: collections.Counter) -> None:
    names = {ident: name for name, ident in text["symbols"].items()}
    for lane in LANGUAGE_LANES:
        table = text["tables"].get(lane)
        if not table:
            continue
        for entry in table["entries"]:
            if not entry["audio"]:
                continue
            path = f"data/sounds/{lane}/messagebox/{entry['audio']}.ogg".casefold()
            rec = audio_by_path.get(path)
            stats["voiceEntries"] += 1
            if rec is None:
                stats["voiceEntriesWithoutFile"] += 1
                continue
            stats["voiceFilesLinked"] += 1
            rec["description"] = {"text": entry["text"], "evidence": f"{table['path']} entry {entry['hex']} "
                                  f"({names.get(entry['id']) or 'no text.stf symbol'}) names this sound; "
                                  f"{L_SOUNDNAME} -> {L_MSGBOX} plays data\\sounds\\<language>\\messagebox\\<name>.ogg"}
            rec["audio"]["textId"] = entry["id"]
            rec["audio"]["textSymbol"] = names.get(entry["id"])


def catalog_text_inventory(game: Path, files: list[dict], text: dict) -> list[dict]:
    records = []
    for row in files:
        fam, rel = row["family"], row["path"]
        if fam not in ("mission-script-msl", "mission-text-txt", "stf-text-table", "language-dat", "sfx-catalog"):
            continue
        data = read_install_file(game / rel)
        atype = {"mission-script-msl": "script", "mission-text-txt": "mission-text", "stf-text-table": "text-symbols",
                 "language-dat": "text-table", "sfx-catalog": "sound-table"}[fam]
        rec = base_record(f"{atype}:{rel.casefold()}", atype, PurePosixPath(rel).name, rel, sha256(data),
                          envelope="file", offset=0, length=len(data), raw_sha=sha256(data), sha_scope="whole file",
                          parser=TOOL + ":catalog_text_inventory")
        info: dict = {"lines": data.count(b"\n")}
        level = re.match(r"data/missionscripts/level(\d{3})/", rel, re.IGNORECASE)
        if level:
            info["levelFolder"] = int(level.group(1))
        if fam == "stf-text-table":
            info["defines"] = len(re.findall(rb"(?m)^\s*#define\s", data))
            rec["provenance"]["loader"] = "build-time #include (FrontEndText.cpp, MenuItem.cpp, FEPGoodies.cpp)"
        elif fam == "language-dat":
            table = text["tables"].get(PurePosixPath(rel).stem.casefold())
            if table:
                info.update(entries=len(table["entries"]), withVoice=sum(1 for e in table["entries"] if e["audio"]),
                            version=table["version"])
            rec["provenance"]["loader"] = L_TEXT_LOAD
            rec["provenance"]["parser"] = "tools/language_dat_decode.py:parse_lang_dat"
        elif fam == "mission-script-msl":
            info["includes"] = re.findall(r'(?m)^\s*#include\s+"([^"]+)"', data.decode("latin-1"))[:32]
            rec["provenance"]["loader"] = "runtime reader not established (compiled scripts travel in the level data)"
        elif fam == "sfx-catalog":
            rec["provenance"]["loader"] = L_SFX
        else:
            rec["provenance"]["loader"] = "runtime owner unknown"
        rec["file"] = info
        records.append(rec)
    return records


def link_compiled_scripts(inventory: list[dict], scripts: list[dict]) -> None:
    """Each .msl record lists the compiled scripts whose name matches its stem in its level folder, and what they
    reference (the union over those copies; the compiled form is the evidence, the .msl text is not parsed)."""
    by_msl: dict[str, list[dict]] = collections.defaultdict(list)
    for sc in scripts:
        for r in sc["relationships"]:
            if r["type"] == "compiled-from" and r["target"]:
                by_msl[r["target"]].append(sc)
    for rec in inventory:
        if rec["type"] != "script":
            continue
        copies = sorted(by_msl.get(rec["id"], []), key=lambda x: x["id"])
        for sc in copies:
            rec["relationships"].append(relation("compiled-as", sc["id"], "name-match", [evidence(
                "data", sc["source"]["container"], "a compiled script in a level's WRES carries this file's stem as "
                "its name (no loader reads .msl files)")]))
        if not copies:
            continue
        union = lambda key: sorted({v for sc in copies for v in sc["scriptCode"][key]}, key=str)
        rec["file"]["compiled"] = {
            "copies": len(copies), "units": union("units"), "textIds": union("textIds"),
            "waypointPaths": union("waypointPaths"), "thingNames": union("thingNames"), "scripts": union("scripts"),
            "postedEvents": union("postedEvents"), "handledEvents": union("handledEvents"),
            "objectiveCallsPerCopy": max(len(sc["scriptCode"]["objectives"]) for sc in copies),
            "objectiveNatives": sorted({o["native"] for sc in copies for o in sc["scriptCode"]["objectives"]}),
            "basis": "the compiled copies' literal call arguments (" + wrd.L_OBJECTCODE + ")"}


def catalog_payloads(collect: dict) -> list[dict]:
    records = []
    for p in collect["payloads"]:
        rec = base_record(f"level-payload:{p['archive'].casefold()}#{p['chunk']}", "level-payload",
                          f"{p['tag']} of {PurePosixPath(p['archive']).name}", p["archive"], p["sha"],
                          envelope=f"lvlr-chunk({p['tag']})", offset=p["offset"], length=p["length"],
                          raw_sha=p["payloadSha"], sha_scope=f"{p['tag']} chunk payload", parser=TOOL + ":collect_chunk",
                          chunk_path=[p["chunk"]])
        rec["provenance"]["loader"] = PAYLOAD_LOADERS.get(p["tag"], "unknown tag (traced and skipped)")
        rec["payload"] = {"tag": p["tag"], "innerTags": p["innerTags"]}
        if p["tag"] == "WRES":
            rec["payload"]["structure"] = ("world bodies decoded in CWorld::LoadWorld's order: placement, marker, "
                                           "waypoint-path and script-code records; level records carry the summaries")
        elif p["decoded"] is not None:
            rec["payload"]["structure"] = p["decoded"]["status"]
            rec["payload"]["decoded"] = p["decoded"]
        else:
            rec["payload"]["structure"] = "not itemised yet"
        records.append(rec)
    return records


# CFEPBriefing::ActiveNotification: the briefing a selected level shows (a level's variants share the first one's).
BRIEFING_LEVEL = {**{n: n for n in (100, 110, 200, 211, 221, 231, 300, 311, 321, 331, 400, 411, 421, 431, 500, 511,
                                    512, 521, 523, 600, 611, 621, 700, 710, 720, 731, 741, 800)},
                  212: 211, 222: 221, 232: 231, 312: 311, 322: 321, 332: 331, 412: 411, 422: 421, 432: 431,
                  522: 521, 524: 523, 612: 611, 622: 621, 732: 731, 742: 741}


def catalog_levels(archives: list[dict], placements: list[dict], videos: list[dict], game: Path, files: list[dict],
                   worlds: dict | None = None, payloads: list[dict] | None = None) -> list[dict]:
    headers = {}
    wh_path = game / "data" / "worldheaders.dat"
    if wh_path.is_file():
        for r in worldheaders_decode.parse_worldheaders(read_install_file(wh_path)).records:
            headers[r.world_id] = r.configs
    folders = collections.Counter()
    for row in files:
        m = re.match(r"data/missionscripts/level(\d{3})/", row["path"], re.IGNORECASE)
        if m:
            folders[int(m.group(1))] += 1
    by_level = collections.defaultdict(list)
    for p in placements:
        by_level[p["placement"]["level"]].append(p)
    briefings = collections.defaultdict(list)
    for v in videos:
        for r in v["relationships"]:
            if r["type"] == "briefing-for-level":
                briefings[int(r["target"].split(":")[1])].append(v["id"])
    levels = []
    numbers = sorted({a["archive"]["level"] for a in archives if a["archive"].get("level") is not None}
                     | set(headers) | set(folders))
    for n in numbers:
        arc = next((a for a in archives if a["archive"].get("level") == n), None)
        rec = base_record(f"level:{n:03d}", "level", f"level {n:03d}", arc["source"]["container"] if arc else
                          "data/worldheaders.dat", arc["source"]["containerSha256"] if arc else "0" * 64,
                          envelope="logical", offset=None, length=0, raw_sha=arc["sha256"] if arc else "0" * 64,
                          sha_scope="the level's inflated resource archive" if arc else "none (no resource archive)",
                          parser=TOOL + ":catalog_levels")
        defs = collections.Counter(p["placement"]["definition"] for p in by_level.get(n, []))
        rec["level"] = {"number": n, "resourceArchive": arc["id"] if arc else None,
                        "worldHeaderConfigurations": headers.get(n),
                        "missionScriptFiles": folders.get(n, 0), "placements": len(by_level.get(n, [])),
                        "placementsByDefinition": dict(defs.most_common()),
                        "meshesLoaded": len(arc["archive"]["meshChunks"]) if arc else 0,
                        "briefingVideos": briefings.get(n, []),
                        "worlds": {tag: world_summary(w) for tag, w in sorted((worlds or {}).get(n, {}).items())},
                        "terrain": level_terrain(arc, payloads or [])}
        if arc:
            rec["relationships"].append(relation("resources", arc["id"], "resolved", [evidence(
                "loader-code", L_RESOURCE_NAME, "level N reads data\\Resources\\%03d_res_%s.aya")]))
        shown = BRIEFING_LEVEL.get(n)
        if shown is not None:
            for vid in briefings.get(shown, []):
                rec["relationships"].append(relation("briefing-video", vid, "resolved", [evidence(
                    "loader-code", L_BRIEFING, f"the briefing for level {n} is level {shown}'s "
                    "(the switch on the selected level)")]))
        if n in headers:
            rec["relationships"].append(relation("world-header", None, "resolved", [evidence(
                "loader-code", L_HEADERS, f"worldheaders.dat record world_id {n}")]))
        levels.append(rec)
    return levels


def level_terrain(arc: dict | None, payloads: list[dict]) -> dict:
    """The decoded ERES, SURF, SSHD and LNDS payloads of the level's archive (summaries; no pixel or height bytes)."""
    if arc is None:
        return {}
    out: dict = {}
    for p in payloads:
        if p["archive"] != arc["source"]["container"] or p["decoded"] is None:
            continue
        d = p["decoded"]
        if p["tag"] == "ERES" and d["status"] == "decoded":
            out["mapNumber"] = d["mapNumber"]
            out["heightField"] = d["heightField"]
            out["mixerMips"] = [{k: m[k] for k in ("mip", "set", "size", "textures")} for m in d["mixerMips"]]
            out["mixerMap"] = d["mixerMap"]
        key = {"ERES": "engine", "SURF": "surf", "SSHD": "staticShadows", "LNDS": "landscape"}[p["tag"]]
        out.setdefault("payloads", {})[key] = {"status": d["status"], "payload": f"level-payload:"
                                               f"{p['archive'].casefold()}#{p['chunk']}"}
        if p["tag"] in ("SURF", "SSHD") and d["status"] == "decoded":
            out[key] = {k: v for k, v in d.items() if k != "status"}
    return out


LEVEL_ARCHIVE_RE = re.compile(r"data/resources/(\d{3})_res_pc\.aya$")


def compute_usage(assets: list[dict]) -> None:
    """Per-asset usage from the resolved relationships (derived; every fact traces to a relationship).

    Placements are counted per (mesh, level) pair once, and a texture record only counts the levels whose
    archive carries it, so per-archive copies of one texture never multiply a placement.
    """
    by_id = {a["id"]: a for a in assets}
    pair_count: collections.Counter = collections.Counter()
    pair_defs: dict[tuple, set] = collections.defaultdict(set)
    mesh_extra: dict[str, dict] = collections.defaultdict(lambda: {"goodies": set(), "archiveLevels": set(),
                                                                    "imposterLevels": set(), "codeSites": 0})
    for a in assets:
        for r in a["relationships"]:
            targets = [r["target"]] if r.get("target") else (r.get("targets") or [])
            for t in targets:
                if not t.startswith("mesh:"):
                    continue
                if a["type"] == "placement" and r["type"] == "uses-mesh":
                    key = (t, a["placement"]["level"])
                    pair_count[key] += 1
                    pair_defs[key].add(a["placement"]["definition"])
                elif a["type"] == "goodie":
                    mesh_extra[t]["goodies"].add(a["goodie"]["number"])
                elif a["type"] == "resource-archive" and r["type"] == "loads-mesh" and a["archive"].get("level") is not None:
                    mesh_extra[t]["archiveLevels"].add(a["archive"]["level"])
                elif r["type"] == "imposter-of-mesh":
                    m = LEVEL_ARCHIVE_RE.search(r["archive"])
                    if m:
                        mesh_extra[t]["imposterLevels"].add(int(m.group(1)))
        if a["type"] == "mesh":
            mesh_extra[a["id"]]["codeSites"] += sum(1 for r in a["relationships"] if r["type"] == "named-by-code")
    pairs_of_mesh: dict[str, set] = collections.defaultdict(set)
    for key in pair_count:
        pairs_of_mesh[key[0]].add(key)

    def from_pairs(pairs: set) -> dict:
        defs = set()
        for key in pairs:
            defs |= pair_defs[key]
        return {"placements": sum(pair_count[k] for k in pairs), "levels": sorted({f"{k[1]:03d}" for k in pairs}),
                "definitions": sorted(defs)}

    basis = "derived from resolved relationships in this catalogue; placements counted once per (mesh, level)"
    for a in assets:
        if a["type"] != "mesh":
            continue
        extra = mesh_extra[a["id"]]
        u = {**from_pairs(pairs_of_mesh[a["id"]]), "goodies": sorted(extra["goodies"]),
             "archiveLevels": [f"{n:03d}" for n in sorted(extra["archiveLevels"])],
             "imposterLevels": [f"{n:03d}" for n in sorted(extra["imposterLevels"])], "codeSites": extra["codeSites"]}
        a["usage"] = {**u, "summary": usage_sentence(u, "mesh"), "basis": basis}
    desc_state: dict[str, dict] = {}
    for a in assets:
        if a["type"] != "texture-descriptor":
            continue
        td = a["textureDescriptor"]
        levels = set()
        for o in td["occurrences"]:
            m = LEVEL_ARCHIVE_RE.search(o["archive"].casefold())
            if m:
                levels.add(int(m.group(1)))
        desc_state[a["id"]] = {"pairs": set(), "levelsCarried": levels, "meshes": set(), "effects": set(),
                               "goodies": set(), "archives": {o["archive"] for o in td["occurrences"]},
                               "roles": {{"TEXT": "level/front-end texture", "IMPS": "imposter atlas", "PLAT": "font",
                                          "GDIE": "goodie"}[o.get("via", "TEXT")] for o in td["occurrences"]},
                               "codeSites": sum(1 for r in a["relationships"] if r["type"] == "named-by-code")}
    for a in assets:
        for r in a["relationships"]:
            targets = [r["target"]] if r.get("target") else (r.get("targets") or [])
            for t in targets:
                st = desc_state.get(t)
                if st is None:
                    continue
                if a["type"] == "mesh" and r["type"] == "uses-texture":
                    st["meshes"].add(a["id"])
                    st["pairs"] |= {k for k in pairs_of_mesh[a["id"]] if k[1] in st["levelsCarried"]}
                elif a["type"] == "effect":
                    st["effects"].add(a["name"])
                elif a["type"] == "goodie":
                    st["goodies"].add(a["goodie"]["number"])

    def texture_usage(states: list[dict]) -> dict:
        pairs, out = set(), {"meshes": set(), "effects": set(), "goodies": set(), "archives": set(), "roles": set()}
        code = 0
        for st in states:
            pairs |= st["pairs"]
            code += st["codeSites"]
            for k in out:
                out[k] |= st[k]
        u = {**from_pairs(pairs), **{k: sorted(v) for k, v in out.items()}, "codeSites": code}
        u["archives"] = len(u["archives"])
        return u

    for a in assets:
        if a["type"] == "texture-descriptor":
            u = texture_usage([desc_state[a["id"]]])
        elif a["type"] == "texture":
            u = texture_usage([desc_state[d] for d in a.get("loadedByDescriptors", [])])
        else:
            continue
        a["usage"] = {**u, "summary": usage_sentence(u, "texture"), "basis": basis}


def usage_sentence(u: dict, kind: str) -> str:
    parts = []
    if u.get("definitions"):
        names = u["definitions"]
        parts.append(f"placed {u['placements']} times as {', '.join(names[:4])}"
                     + (f" (+{len(names) - 4} more)" if len(names) > 4 else "")
                     + f" in levels {', '.join(u['levels'][:8])}" + (" ..." if len(u["levels"]) > 8 else ""))
    if kind == "mesh" and u.get("archiveLevels"):
        parts.append(f"loaded by {len(u['archiveLevels'])} level archive(s)")
    if kind == "mesh" and u.get("imposterLevels"):
        parts.append(f"has imposters in {len(u['imposterLevels'])} level(s)")
    if kind == "texture" and u.get("meshes"):
        parts.append(f"on {len(u['meshes'])} mesh(es)")
    if u.get("effects"):
        parts.append(f"in {len(u['effects'])} particle effect(s)")
    if u.get("goodies"):
        parts.append("goodie " + ", ".join(str(g) for g in u["goodies"][:6]))
    if u.get("codeSites"):
        parts.append(f"named by {u['codeSites']} code site(s)")
    roles = [r for r in u.get("roles", []) if r in ("font", "imposter atlas")]
    if roles:
        parts.append(" and ".join(roles))
    if not parts and u.get("archives"):
        parts.append(f"carried by {u['archives']} archive(s); no mesh, effect, goodie or code use established")
    return "; ".join(parts) or "no use established"


# -------------------------------------------------------------------------------------------------------- pipeline
def dangling_targets(assets: list[dict]) -> list[str]:
    """Relationship targets that name no catalogued asset (every target must be an asset id or null)."""
    ids = {a["id"] for a in assets}
    return sorted({t for a in assets for r in a["relationships"]
                   for t in ([r["target"]] if r.get("target") else []) + list(r.get("targets") or []) if t not in ids})


def build_catalog(game: Path, decomp: Path | None = None) -> dict:
    files = walk_install(game)
    survey = build_survey(files)
    textures, texture_index = catalog_textures(game, files)
    meshes, animations = [], []
    loose: dict[str, dict] = {}
    for row in files:
        if row["family"] != "cmsh-mesh":
            continue
        rel = row["path"]
        source = read_install_file(game / rel)
        stream = dds_census.inflate_aya(source)
        rec, anims, _uv = catalog_mesh(stream, asset_id="mesh:" + rel.casefold(),
                                       name=PurePosixPath(rel).name[2:-4], container=rel, container_sha=sha256(source),
                                       envelope="aya-zlib-members(cmsh)", offset=0, chunk_path=[])
        meshes.append(rec)
        animations.extend(anims)
        loose[rel.casefold()] = rec
    collect = {"imposters": [], "platform": [], "goodies": [], "wres": {}, "payloads": [], "meshIds": {}}
    archives, descriptors, embedded, archive_stats = catalog_archives(game, files, texture_index, loose, collect)
    for rel, stream, where in embedded:
        rec, anims, _uv = catalog_mesh(stream, asset_id=f"mesh:embedded:{rel.casefold()}#{where['chunk']}", name="",
                                       container=rel, container_sha=where["archiveSha"],
                                       envelope="lvlr-chunk(MESH/PMSH/PMS2)", offset=where["offset"],
                                       chunk_path=[where["chunk"]])
        rec["mesh"]["embedded"] = True
        meshes.append(rec)
        animations.extend(anims)
    link_mesh_textures(meshes, descriptors, archives)
    apply_tiling(meshes, descriptors, textures)
    dindex = DescriptorIndex(descriptors)
    descriptors_by_id = {d["id"]: d for d in descriptors}
    link_imposters(collect, descriptors_by_id)
    audio = catalog_audio(game, files)
    video = catalog_video(game, files)
    text = read_text_tables(game, files)
    link_voice(text, {a["source"]["container"].casefold(): a for a in audio if a["source"]["envelope"] == "ogg"},
               archive_stats)
    goodies = catalog_goodies(collect, game, loose, dindex, {v["id"]: v["id"] for v in video}, text)
    script_ids = {"script:" + r["path"].casefold() for r in files if r["family"] == "mission-script-msl"}
    world = catalog_world(collect, game, loose, archives, script_ids, text, archive_stats)
    definitions, placements = world["definitions"], world["placements"]
    effects = catalog_particles(game, files, dindex)
    refs = code_references(decomp)
    unresolved_code = link_code_references(refs, dindex, descriptors_by_id, loose, archive_stats)
    link_unloaded_mesh_names(textures, meshes)
    inventory = catalog_text_inventory(game, files, text)
    link_compiled_scripts(inventory, world["scripts"])
    payloads = catalog_payloads(collect)
    levels = catalog_levels(archives, placements, video, game, files, world["worlds"], collect["payloads"])
    terrain = {lvl["level"]["number"]: d for lvl in levels for d in [next(
        (p["decoded"] for p in collect["payloads"] if p["tag"] == "ERES" and p["decoded"]["status"] == "decoded"
         and lvl["level"]["resourceArchive"] == "archive:" + p["archive"].casefold()), None)] if d}
    rule_names = link_rule_textures(levels, terrain, dindex, descriptors_by_id, archive_stats)
    assets = (levels + archives + payloads + descriptors + textures + meshes + animations + definitions + placements
              + world["markers"] + world["paths"] + world["scripts"] + goodies + effects + audio + video + inventory)
    compute_usage(assets)
    dangling = dangling_targets(assets)
    if dangling:
        raise ValueError(f"relationships target absent ids: {dangling[:5]}")
    ids = collections.Counter(a["id"] for a in assets)
    duplicates = [i for i, n in ids.items() if n > 1]
    if duplicates:
        raise ValueError(f"duplicate asset ids: {duplicates[:5]}")
    return {"files": files, "survey": survey, "assets": assets, "archiveStats": dict(archive_stats),
            "codeReferences": {"source": refs["source"], "textureSites": len(refs["textures"]),
                               "meshSites": len(refs["meshes"]),
                               "unresolvedTextureNames": sorted({r["name"] for r in unresolved_code}),
                               "ruleBuiltTextureNames": len(rule_names),
                               "ruleBuiltTextureNamesUnresolved": sorted({(r["level"] or "all") + " " + r["name"]
                                                                          for r in rule_names if not r["resolved"]})}}


def build_coverage(catalog: dict) -> dict:
    survey, assets = catalog["survey"], catalog["assets"]
    by_type = collections.Counter(a["type"] for a in assets)
    status_of = lambda a: (a.get("texture") or a.get("textureDescriptor") or a.get("mesh") or a.get("audio")
                           or a.get("video") or a.get("animation") or {}).get("status", "parsed")
    by_type_status = collections.defaultdict(collections.Counter)
    for a in assets:
        by_type_status[a["type"]][status_of(a)] += 1
    rel_status = collections.defaultdict(collections.Counter)
    for a in assets:
        for r in a["relationships"]:
            rel_status[r["type"]][r["status"]] += 1
    families = {f["family"]: f for f in survey["families"]}
    file_coverage = []
    for fam in survey["families"]:
        file_coverage.append({"family": fam["family"], "files": fam["files"], "status": fam["status"]})
    textures = [a for a in assets if a["type"] == "texture"]
    return {
        "schema": COVERAGE_SCHEMA, GENERATED_MARKER: True,
        "installFiles": survey["files"], "installBytes": survey["bytes"],
        "filesInCataloguedFamilies": sum(f["files"] for f in survey["families"] if f["status"] == "catalogued"),
        "filesInParsedElsewhereFamilies": sum(f["files"] for f in survey["families"] if f["status"] == "parsed-elsewhere"),
        "filesInInventoriedFamilies": sum(f["files"] for f in survey["families"] if f["status"] == "inventoried"),
        "filesInUnparsedFamilies": sum(f["files"] for f in survey["families"] if f["status"] == "unparsed"),
        "filesNotContent": sum(f["files"] for f in survey["families"] if f["status"] == "not-content"),
        "unclassified": survey["unclassified"],
        "assetsByType": dict(sorted(by_type.items())),
        "assetStatusByType": {k: dict(sorted(v.items())) for k, v in sorted(by_type_status.items())},
        "relationshipStatus": {k: dict(sorted(v.items())) for k, v in sorted(rel_status.items())},
        "archiveStats": catalog["archiveStats"],
        "textureFilesReferencedByADescriptor": sum(1 for t in textures if t.get("loadedByDescriptors")),
        "textureFilesUsedByAMesh": sum(1 for t in textures if t.get("referencedBy")),
        "textureFilesWithAnEstablishedUse": sum(1 for t in textures if t["usage"]["meshes"] or t["usage"]["effects"]
                                                or t["usage"]["goodies"] or t["usage"]["codeSites"]
                                                or {"font", "imposter atlas"} & set(t["usage"]["roles"])),
        "textureFilesNotLoaded": sorted(t["source"]["container"] for t in textures if not t.get("loadedByDescriptors")),
        "codeReferences": catalog["codeReferences"],
        "placementsByLevel": dict(sorted(collections.Counter(
            f"{a['placement']['level']:03d}" for a in assets if a["type"] == "placement").items())),
        "textureTiling": dict(collections.Counter(t["upscale"]["tiling"]["status"] for t in textures)),
        "families": file_coverage,
        "unparsedFamilies": [f["family"] for f in survey["families"] if f["status"] in ("unparsed", "inventoried")],
        "markersByKind": dict(sorted(collections.Counter(a["marker"]["kind"] for a in assets
                                                         if a["type"] == "marker").items())),
        "placementsByKind": dict(sorted(collections.Counter(a["placement"]["kind"] for a in assets
                                                            if a["type"] == "placement").items())),
        "levelPayloadDecode": dict(sorted(collections.Counter(
            f"{a['payload']['tag']}:{a['payload']['structure'] if a['payload']['tag'] != 'WRES' else 'decoded'}"
            for a in assets if a["type"] == "level-payload").items())),
        "notYetCatalogued": [
            "VSDS (vertex shaders), PMIB (patch manager), DMKR (landscape damage) payload structure: payload records "
            "with hashes only",
            "the mixer-map slot entries, heightfield samples and static-shadow cells are summarised (counts, ranges, "
            "hashes), not itemised per cell",
            "script arguments that are not literal pushes (computed values, variables) stay unresolved and are counted "
            "per role; which things join WORLD.mNamedThings is not traced (names-thing is a name match)",
            "names built with sprintf from data not decoded here: weapon HUD icons (hud\\%s.tga from physics weapon "
            "icon names), screenshot and texture-dump paths (written, not read)",
            "the .msl source text itself is not parsed (its compiled form is the evidence); mission text .txt, "
            "sounds.sfx event table, battle engine configurations.dat",
            "Dial.raw and the splash TGA",
        ],
        "notes": {"loaderCitations": families["cmsh-mesh"]["loader"]},
    }


def install_fingerprint(game: Path, files: list[dict]) -> str:
    lines = []
    for row in files:
        if row["size"] is None:
            continue
        lines.append(f"{row['path']}\t{row['size']}")
    return sha256("\n".join(lines).encode("utf-8"))


def git_head() -> str | None:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def output_is_ignored_local_data(out: Path) -> bool:
    allowed = Path(os.path.abspath(ROOT / "local-data"))
    candidate = Path(os.path.abspath(out))
    try:
        if os.path.commonpath((candidate, allowed)) != str(allowed):
            return False
    except ValueError:
        return False
    probe = candidate / "probe.json"
    result = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", str(probe)], capture_output=True)
    return result.returncode == 0


def write_outputs(out: Path, game: Path, catalog: dict, coverage: dict) -> list[Path]:
    manifest = {"schema": MANIFEST_SCHEMA, GENERATED_MARKER: True, "schemaVersion": SCHEMA_VERSION,
                "generatedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tool": TOOL, "toolCommit": git_head(), "assetSchema": "tools/content_catalog.schema.json",
                "install": {"files": len(catalog["files"]), "pathSizeFingerprint": install_fingerprint(game, catalog["files"])},
                "assetCount": len(catalog["assets"]),
                "boundary": "retail-derived names, sizes and hashes only; no retail payload bytes; never commit"}
    outputs = {"manifest.json": json.dumps(manifest, indent=2, sort_keys=True) + "\n",
               "survey.json": json.dumps(catalog["survey"], indent=2, sort_keys=True) + "\n",
               "coverage.json": json.dumps(coverage, indent=2, sort_keys=True) + "\n",
               "assets.jsonl": "".join(json.dumps({**a, GENERATED_MARKER: True}, sort_keys=True) + "\n"
                                       for a in catalog["assets"])}
    out.mkdir(parents=True, exist_ok=True)
    written = []
    with SecuredOutputRoot(out, protected_sources=[game]) as secured:
        for name, text in outputs.items():
            with secured.atomic_text_writer(out / name) as writer:
                writer.write(text)
            written.append(out / name)
    return written


# ------------------------------------------------------------------------------------------------------- self-test
def run_self_test() -> int:
    failures = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            failures.append(label)

    # LoadFrame's path rule: flattening, shelf/prefix choice and the 61 + ".aya" cut.
    check(expected_texture_file("meshtex\\arachtex.tga", 0, 1, True)
          == "data/resources/dxtntextures/meshtex%arachtex.tga(0)A1R5G5B5.aya", "dxtn path")
    check(expected_texture_file("font.tga", 2, 4, False)
          == "data/resources/textures/mustbe_font.tga(2)A8R8G8B8.aya", "mustbe path")
    long_name = "goodies\\ca_cutscene_locations\\ca_cl_f_command_room_interior.tga"
    cut = PurePosixPath(expected_texture_file(long_name, 0, 4, True)).name
    check(cut == "goodies%ca_cutscene_locations%ca_cl_f_command_room_interior.t.aya" and len(cut) == 65, "path cut")
    check(expected_texture_file("x", 0, 99, True).endswith("(0)nk.aya"), "unknown format string")
    # CMesh::FindTexture's requested format from the name after "meshtex\\".
    check(mesh_texture_format("meshtex\\A8trust5.tga") == 4 and mesh_texture_format("meshtex\\a4x.tga") == 2
          and mesh_texture_format("meshtex\\grass.tga") == 1, "mesh texture format prefix")
    # Survey classification.
    check(classify("data/resources/100_res_PC.aya") == "lvlr-resource-archive", "classify archive")
    check(classify("data/resources/dxtntextures/a(0)DXT1.aya") == "dds-texture-dxtn", "classify dxtn")
    check(classify("data/sounds/english/MessageBox/x.ogg") == "ogg-voice", "classify voice")
    check(classify("data/Music/track.ogg") == "ogg-music", "classify music")
    check(classify("data/video/briefings/PC_100.vid") == "bink-video", "classify video")
    check(classify("BEA.exe") == "executable-code", "classify exe")
    check(classify("data/unknown.bin") == "unclassified", "classify unknown")
    # A synthetic TEXT payload exercises the field offsets (project-authored bytes, not retail data).
    obj = bytearray(0x158)
    obj[0x08:0x08 + 9] = b"hud\\a.tga"
    struct.pack_into("<i", obj, 0x08 + 0xA0, 1)      # mFormat
    struct.pack_into("<i", obj, 0x08 + 0xA4, 64)     # mWidth
    struct.pack_into("<h", obj, 0x08 + 0xA8, 32)     # mHeight
    struct.pack_into("<i", obj, 0x138, 1)            # mNumFrames
    struct.pack_into("<i", obj, 0x144, 1)            # mTexFormat
    struct.pack_into("<i", obj, 0x148, -1)           # mLevels
    obj[0x154] = 1                                    # mCompressible
    ctex = b"CTEX" + struct.pack("<I", len(obj)) + bytes(obj)
    tfrm = b"TFRM" + struct.pack("<I", 4) + struct.pack("<I", 7)
    body = ctex + tfrm
    payload = b"DXTX" + struct.pack("<I", len(body)) + body
    fields = parse_text_record(payload)
    check(fields["name"] == "hud\\a.tga" and fields["width"] == 64 and fields["height"] == 32, "text geometry")
    check(fields["texFormat"] == 1 and fields["requestedFormat"] == 1 and fields["levels"] == -1
          and fields["compressible"] == 1 and fields["mipLevelsPerFrame"] == [7], "text fields")
    # Ogg/Vorbis and Bink headers on synthetic bytes.
    ident = b"\x01vorbis" + struct.pack("<IBIiii", 0, 2, 44100, 0, 128000, 0) + b"\xb8\x01"
    page1 = b"OggS\x00\x02" + struct.pack("<qIII", 0, 1, 0, 0) + bytes([1, len(ident)]) + ident
    page2 = b"OggS\x00\x04" + struct.pack("<qIII", 88200, 1, 1, 0) + bytes([1, 3]) + b"abc"
    ogg = ogg_metadata(page1 + page2)
    check(ogg["channels"] == 2 and ogg["sampleRate"] == 44100 and ogg["seconds"] == 2.0, "ogg header")
    bik = b"BIKi" + struct.pack("<9I", 0, 50, 0, 0, 640, 480, 25, 1, 0) + struct.pack("<I", 1) + bytes(8)
    meta = bink_metadata(bik)
    check(meta["frames"] == 50 and meta["width"] == 640 and meta["seconds"] == 2.0 and meta["audioTracks"] == 1,
          "bink header")
    # The generated-output boundary: only an ignored path below local-data/ is accepted.
    check(not output_is_ignored_local_data(ROOT / "tools"), "tools/ refused")
    check(not output_is_ignored_local_data(ROOT.parent), "outside checkout refused")
    if (ROOT / ".git").exists():
        check(output_is_ignored_local_data(ROOT / "local-data" / "content-catalog"), "local-data accepted")
    for label in failures:
        print(f"FAIL {label}")
    print(f"content_catalog self-test: {'failed' if failures else 'passed'} ({len(failures)} failures)")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"))
    parser.add_argument("--out", type=Path, default=ROOT / "local-data" / "content-catalog")
    parser.add_argument("--decomp", type=Path, help="optional onslaught-decomp checkout: adds texture and mesh "
                        "names that game code looks up literally")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()
    if not args.game:
        parser.error("--game (or BEA_GAME) is required")
    game = Path(os.path.abspath(args.game))
    out = Path(os.path.abspath(args.out))
    if not output_is_ignored_local_data(out):
        parser.error("--out must be a git-ignored directory below this checkout's local-data/")
    if os.path.commonpath((game, out)) == str(game):
        parser.error("--out must not be inside the game folder")
    catalog = build_catalog(game, Path(os.path.abspath(args.decomp)) if args.decomp else None)
    coverage = build_coverage(catalog)
    for path in write_outputs(out, game, catalog, coverage):
        print(path)
    print(json.dumps({"assetsByType": coverage["assetsByType"], "relationshipStatus": coverage["relationshipStatus"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
