#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Battle Engine Aquila content catalogue: an evidence-based inventory of a retail PC install.

Phase 1 surveys every file of a selected install (container families, counts, sizes, the loader that reads each
family and whether a repository parser already reads it) and catalogues the families existing parsers read:
loose DDS textures, the texture records (TEXT) and mesh records (MESH) inside the level resource archives, loose
and embedded CMSH meshes with their stored animation modes, XAP bank samples, Ogg Vorbis files and Bink videos.

Every asset gets a stable id, its container and coordinates, a SHA-256 of its bytes, format metadata, an "upscale"
section and provenance. Relationships are recorded only when a loader rule in the decompilation or the data itself
establishes them, and every relationship names its evidence. Descriptions stay null unless evidenced.

The install is only read. The generated catalogue contains retail-derived names and hashes (never retail payload
bytes), so it is written only below this checkout's ignored local-data/ directory and is never committed; every
generated file carries the generatedRetailDerived marker that tools/public_allowlist_safety_check.py rejects.
The schema is tools/content_catalog.schema.json.

Run:  python ./tools/content_catalog.py --game GAME_FOLDER [--out local-data/content-catalog]
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
     "unparsed"),
    ("language-dat", lambda p: p.startswith("data/language/") and p.endswith(".dat"),
     "localized text", L_TEXT, "tools/language_dat_decode.py; tools/export_language_corpus.py", "parsed-elsewhere"),
    ("mission-script-msl", lambda p: p.startswith("data/missionscripts/") and (p.endswith(".msl") or p.endswith(".h")),
     "mission script source", "runtime reader not established in the decompilation (onsldef.msl is #included by "
     "Career.cpp and game.cpp)", "tools/cmsh_animation_usage_census.py (animation calls only)", "unparsed"),
    ("mission-text-txt", lambda p: p.startswith("data/missionscripts/") and p.endswith(".txt"),
     "mission text", "runtime owner unknown", "none", "unparsed"),
    ("stf-text-table", lambda p: p.endswith(".stf"), "text symbol table",
     "#included by FrontEndText.cpp, MenuItem.cpp, FEPGoodies.cpp (build-time)", "none", "unparsed"),
    ("particle-set-par", lambda p: p.startswith("data/particlesets/") and p.endswith(".par"),
     "particle effects", L_PARTICLES, "rebuild TokenArchive (onslaught-godot); none in tools/", "unparsed"),
    ("world-headers-dat", lambda p: p == "data/worldheaders.dat", "level headers", L_HEADERS, "none in tools/",
     "unparsed"),
    ("default-physics-dat", lambda p: p == "data/default physics.dat", "physics/unit definitions", L_PHYSICS,
     "tools/cmsh_animation_usage_census.py (mesh fields only)", "unparsed"),
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


def catalog_archives(game: Path, files: list[dict], texture_index: dict[str, dict], loose_meshes: dict[str, dict]
                     ) -> tuple[list[dict], list[dict], list[tuple[str, bytes, dict]], dict]:
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
                add_descriptor(descriptors, rel, source_sha, chunk, payload, texture_index, stats)
            elif chunk.tag == "MESH":
                stats["meshChunks"] += 1
                try:
                    _key, display, method = cross.logical_key("MESH", payload)
                except ValueError as error:
                    mesh_rows.append({"chunk": chunk.index, "status": "unparsed", "reason": str(error)})
                    continue
                if display:
                    target_file = f"data/resources/meshes/m_{display}.aya".casefold()
                    target = loose_meshes.get(target_file)
                    mesh_rows.append({"chunk": chunk.index, "name": display, "nameField": method,
                                      "target": target["id"] if target else None})
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
                    mesh_rows.append({"chunk": chunk.index, "name": "",
                                      "target": f"mesh:embedded:{rel.casefold()}#{chunk.index}"})
                    stats["embeddedMeshes"] += 1
        rec["archive"]["meshChunks"] = mesh_rows
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
                          "each TEXT chunk deserializes one texture record")]))
    return archives, list(descriptors.values()), embedded, stats


def add_descriptor(descriptors: dict, rel: str, archive_sha: str, chunk, payload: bytes, texture_index: dict,
                   stats: collections.Counter) -> None:
    payload_sha = sha256(payload)
    occurrence = {"archive": rel, "chunk": chunk.index, "offset": chunk.offset + 8}
    if payload_sha in descriptors:
        descriptors[payload_sha]["textureDescriptor"]["occurrences"].append(occurrence)
        return
    try:
        fields = parse_text_record(payload)
    except (ValueError, struct.error) as error:
        stats["textUnparsed"] += 1
        rec = base_record(f"texture-descriptor:unparsed:{payload_sha[:16]}", "texture-descriptor", "", rel,
                          archive_sha, envelope="lvlr-chunk(TEXT)", offset=chunk.offset + 8, length=len(payload),
                          raw_sha=payload_sha, sha_scope="TEXT chunk payload", parser=TOOL + ":parse_text_record",
                          chunk_path=[chunk.index])
        rec["textureDescriptor"] = {"status": "unparsed", "reason": str(error), "occurrences": [occurrence]}
        descriptors[payload_sha] = rec
        return
    name = fields["name"]
    rec = base_record(f"texture-descriptor:{fold(name)}:{payload_sha[:12]}", "texture-descriptor", name, rel,
                      archive_sha, envelope="lvlr-chunk(TEXT)", offset=chunk.offset + 8, length=len(payload),
                      raw_sha=payload_sha, sha_scope="TEXT chunk payload (DXTX/CTEX/TFRM)",
                      parser="tools/aya_texture_fidelity_census.py:parse_serialized_texture + " + TOOL,
                      chunk_path=[chunk.index])
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


# -------------------------------------------------------------------------------------------------------- pipeline
def build_catalog(game: Path) -> dict:
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
    archives, descriptors, embedded, archive_stats = catalog_archives(game, files, texture_index, loose)
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
    audio = catalog_audio(game, files)
    video = catalog_video(game, files)
    assets = archives + descriptors + textures + meshes + animations + audio + video
    ids = collections.Counter(a["id"] for a in assets)
    duplicates = [i for i, n in ids.items() if n > 1]
    if duplicates:
        raise ValueError(f"duplicate asset ids: {duplicates[:5]}")
    return {"files": files, "survey": survey, "assets": assets, "archiveStats": dict(archive_stats)}


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
        "filesInUnparsedFamilies": sum(f["files"] for f in survey["families"] if f["status"] == "unparsed"),
        "filesNotContent": sum(f["files"] for f in survey["families"] if f["status"] == "not-content"),
        "unclassified": survey["unclassified"],
        "assetsByType": dict(sorted(by_type.items())),
        "assetStatusByType": {k: dict(sorted(v.items())) for k, v in sorted(by_type_status.items())},
        "relationshipStatus": {k: dict(sorted(v.items())) for k, v in sorted(rel_status.items())},
        "archiveStats": catalog["archiveStats"],
        "textureFilesReferencedByADescriptor": sum(1 for t in textures if t.get("loadedByDescriptors")),
        "textureFilesUsedByAMesh": sum(1 for t in textures if t.get("referencedBy")),
        "textureTiling": dict(collections.Counter(t["upscale"]["tiling"]["status"] for t in textures)),
        "families": file_coverage,
        "unparsedFamilies": [f["family"] for f in survey["families"] if f["status"] in ("unparsed", "parsed-elsewhere")],
        "notYetCatalogued": [
            "GDIE goodie archives: textures/meshes inside 232 goodie archives (CFEPGoodies::Deserialise) are counted "
            "as archive chunks only",
            "WRES/ERES/IMPS/LNDS/SURF/SSHD level payloads (world placements, entities, imposters, terrain, water, "
            "static shadows): level/map content is not yet itemised",
            "particle sets (*.par) and their texture references",
            "mission scripts (*.msl), mission text and STF tables, language tables",
            "HUD/front-end texture use by code (FindTexture/GetTextureByName call sites) as relationships",
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
    catalog = build_catalog(game)
    coverage = build_coverage(catalog)
    for path in write_outputs(out, game, catalog, coverage):
        print(path)
    print(json.dumps({"assetsByType": coverage["assetsByType"], "relationshipStatus": coverage["relationshipStatus"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
