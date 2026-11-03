#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""The retail gate for tools/content_inventory.py: re-derive what only the real install can show, by a path that does
not run through the reader being checked, and fail on any disagreement.

tools/content_inventory_tests.py checks the rules on authored data. This reads a finished run's output and the game
folder it came from, and checks that:

  schema     every row the run wrote meets tools/content_inventory.schema.json (skipped, and said so, without jsonschema)
  files      an independent walk of the folder finds exactly the run's files and sizes and no link, special file or
             folder it cannot list, and each file can be read and still has the hash the run recorded
  judge      the mission-script judge read every level archive's worlds (otherwise no level folder's source was judged)
  account    every file's parts and spans sum to its logical size and its classes agree with its bytes
  envelope   every AYA, inflated here member by member with zlib alone, has the logical size the run reports
  chunks     every archive's top-level chunks, walked here, close exactly and reach the end of the stream
  records    every catalogue record placed by offset in an archive's inflated stream hashes, at those coordinates, to
             the SHA-256 the catalogue gave it, and lies on bytes the account does not call unknown
  images     Pillow opens every PNG, JPEG and TGA at the size the walkers report (skipped, and said so, without Pillow)
  decoders   every Ogg and Bink was read by the independent decoder and agreed (a run without one fails here)
  animation  every mesh's cached model-space frames equal its keys composed down the hierarchy
  items      item ids are unique, and every item's file is one of the run's files
  metadata   every texture, image, model, animation, sound and film item has one asset-metadata row; each names its
             file's hash; every row but a mesh chain's links, their animations and the terrain mixer mips is placed,
             and its bytes, cut from the stored file or from the stream inflated here, hash to its SHA-256; and every
             metadata field equals what the gate reads from those bytes itself (a DDS header, mip chain and, with
             Pillow, its top mip's alpha; a texture record's fields; an image, Ogg, Bink or bank sample header; an
             animation record; a damage texture's levels), or, for an unplaced row, what its details give
  sniffing   every file's own magic agrees with its family
  problems   no reader refused anything

The gate reads and writes nothing else. It prints counts; a failure names a file and what disagreed, never its bytes.
The exit code is 0 only when every check passes.

    python3 tools/content_inventory_gate.py --game GAME [--inventory local-data/content-inventory] [--no-compose]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
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
sys.path.insert(0, str(ROOT / "rebuild" / "tools"))

import aya_texture_fidelity_census as texture_layout  # noqa: E402  (the PC texture record's field offsets)
import cmsh_animation_usage_census as meshcensus  # noqa: E402
import cmsh_grammar_walk as grammar  # noqa: E402
import content_inventory as inv  # noqa: E402
import xap_bank_walk  # noqa: E402

try:
    from PIL import Image
except ImportError:  # the check says so; it never passes silently
    Image = None

# The catalogue envelopes whose offset and length are coordinates in the archive's inflated stream. A world body's
# records are placed inside the body instead, so they are not checked this way.
STREAM_ENVELOPE_RE = re.compile(r"^lvlr-chunk\([A-Z0-9]{4}(?:/PMSH/PMS2)?\)$")
IMAGE_SUFFIXES = (".png", ".jpg", ".tga")


class WalkError(ValueError):
    """The independent walk met a folder it cannot list, so the folder's files are not known."""


def walk_folder(game: Path) -> tuple[dict[str, int], list[str]]:
    """Every regular file below the folder and its size, and every other entry: a link (to a directory too, which
    os.walk lists among the directories and does not enter) or a special file, which no account can hold. A folder
    that cannot be listed raises WalkError instead of dropping its files."""
    def unlistable(error: OSError) -> None:
        where = Path(error.filename) if error.filename else game
        name = where.relative_to(game).as_posix() if where.is_relative_to(game) else "the selected folder"
        raise WalkError(f"{name}: a folder the walk cannot list ({error.strerror})") from error

    found, irregular = {}, []
    for folder, dirs, names in os.walk(game, onerror=unlistable, followlinks=False):
        irregular += [(Path(folder) / name).relative_to(game).as_posix() for name in dirs
                      if (Path(folder) / name).is_symlink()]
        for name in names:
            path = Path(folder) / name
            info = path.lstat()
            if stat.S_ISREG(info.st_mode):
                found[path.relative_to(game).as_posix()] = info.st_size
            else:
                irregular.append(path.relative_to(game).as_posix())
    return found, sorted(irregular)


def inflate_members(data: bytes) -> bytes:
    """AYA's members, with nothing but zlib: u32 stored length, then a complete zlib stream."""
    out, position = [], 0
    while position < len(data):
        if position + 4 > len(data):
            raise ValueError("truncated member length")
        (length,) = struct.unpack_from("<I", data, position)
        position += 4
        inflater = zlib.decompressobj()
        out.append(inflater.decompress(data[position:position + length]))
        if not length or not inflater.eof or inflater.unused_data or position + length > len(data):
            raise ValueError("member does not close")
        position += length
    return b"".join(out)


def walk_chunks(raw: bytes) -> list[tuple[bytes, int, int]]:
    rows, position = [], 0
    while position < len(raw):
        if position + 8 > len(raw):
            raise ValueError("truncated chunk header")
        (size,) = struct.unpack_from("<I", raw, position + 4)
        if position + 8 + size > len(raw):
            raise ValueError("chunk runs past the stream")
        rows.append((raw[position:position + 4], position, size))
        position += 8 + size
    return rows


def spans_cover(spans: list, start: int, end: int) -> bool:
    return any(a < end and start < b for a, b in spans)


def check_files(game: Path, rows: list[dict], walked: tuple[dict[str, int], list[str]], report: "Report") -> None:
    found, irregular = walked
    listed = {row["path"]: row["storedBytes"] for row in rows}
    report.count("files walked", len(found))
    for path in irregular:
        report.fail(f"{path}: a link or special file, which no account holds")
    for path in sorted(set(found) ^ set(listed)):
        report.fail(f"{path}: in {'the folder' if path in found else 'the run'} only")
    for path in sorted(set(found) & set(listed)):
        if found[path] != listed[path]:
            report.fail(f"{path}: the run's size differs from the folder's")
    for row in rows:
        path = game / row["path"]
        if path.is_file():
            try:
                data = path.read_bytes()
            except OSError as error:
                report.fail(f"{row['path']}: a file the gate cannot read ({error.strerror})")
                continue
            if hashlib.sha256(data).hexdigest() != row["sha256"]:
                report.fail(f"{row['path']}: the file changed after the run")
            yield row, data


def check_account(row: dict, report: "Report") -> None:
    totals = row["bytes"]
    if sum(totals.values()) != row["logicalBytes"]:
        report.fail(f"{row['path']}: classes do not sum to the logical size")
    by_class: collections.Counter = collections.Counter()
    for part in row["parts"]:
        by_class[part["class"]] += part["bytes"]
    if any(by_class[klass] != totals[klass] for klass in inv.BYTE_CLASSES):
        report.fail(f"{row['path']}: parts do not sum to the classes")
    if sum(end - start for start, end, _part in row["unknownSpans"]) != totals[inv.UNKNOWN]:
        report.fail(f"{row['path']}: unknown spans do not sum to the unknown bytes")
    if sum(end - start for start, end in row["referencedSpans"]) != totals[inv.REFERENCED]:
        report.fail(f"{row['path']}: referenced spans do not sum to the referenced bytes")
    if row["class"] != inv.file_class(row["logicalBytes"], totals):
        report.fail(f"{row['path']}: its class disagrees with its bytes")
    report.count("accounts checked")


def stream_records(catalog_records: list[dict]) -> dict[str, list[dict]]:
    """The catalogue records placed in an archive's inflated stream, by folded container path."""
    out: dict[str, list[dict]] = collections.defaultdict(list)
    for record in catalog_records:
        source = record["source"]
        if STREAM_ENVELOPE_RE.match(source["envelope"]) and source["offset"] is not None and source["length"]:
            out[source["container"].casefold()].append(record)
    return out


def check_records(row: dict, raw: bytes, records: list[dict], report: "Report") -> None:
    unknown = [span[:2] for span in row["unknownSpans"]]
    for record in records:
        source = record["source"]
        start, end = source["offset"], source["offset"] + source["length"]
        if end > len(raw):
            report.fail(f"{record['id']}: its coordinates run past its stream")
        elif hashlib.sha256(raw[start:end]).hexdigest() != record["sha256"]:
            report.fail(f"{record['id']}: the bytes at its coordinates do not hash to its SHA-256")
        elif spans_cover(unknown, start, end):
            report.fail(f"{record['id']}: it lies on bytes the account calls unknown")
        else:
            report.count("records whose coordinates hash to their SHA-256")
            if spans_cover(row["referencedSpans"], start, end):
                report.count("records touching referenced bytes")


def check_metadata_rows(items: list[dict], metadata: list[dict], report: "Report") -> None:
    """Exactly one asset-metadata row per texture, image, model, animation, sound and film item, and no other."""
    wanted = {item["id"] for item in items if item["kind"] in inv.METADATA_KINDS}
    seen = collections.Counter(asset.get("id") for asset in metadata)
    for name in sorted(wanted - set(seen)):
        report.fail(f"{name}: an asset without an asset-metadata row")
    for name in sorted(set(seen) - wanted, key=str):
        report.fail(f"{name}: an asset-metadata row for no texture, image, model, animation, sound or film item")
    for name, count in sorted(seen.items(), key=lambda pair: str(pair[0])):
        if count > 1:
            report.fail(f"{name}: {count} asset-metadata rows")
    report.count("asset-metadata rows", len(metadata))


# Where a metadata row's coordinates point: into the stored file, or into the stream the gate inflated itself.
STORED_ENVELOPES = ("xap(", "ogg", "bink", "whole file", "pe-resource(")
INFLATED_ENVELOPES = ("lvlr-chunk(", "aya-zlib-members(")
# The forms whose identity places no bytes: a mesh chain's links and their animations (the reader lists them without
# their offsets) and a terrain mixer mip (its item offset is the ERES payload's, not the mip's). Every other row must be
# placed by an envelope the gate can cut.
UNPLACED_FORMS = ("chained-mesh", "chained-animation", "terrain-mixer-mip")


class Unreadable(ValueError):
    """The bytes at a row's coordinates do not hold what its form says."""


NOT_CHECKED = object()  # a field the gate cannot read again here (a DDS alpha without Pillow)


def expect(**values) -> dict:
    """A full set of metadata fields: the given values, every other field null."""
    return {**dict.fromkeys(inv.METADATA_FIELDS), **values}


def u32(data: bytes, at: int) -> int:
    return struct.unpack_from("<I", data, at)[0]


# The channels each texture format holds, stated here apart from the inventory's table: DXT1 counts as colour, and
# X8R8G8B8's fourth byte is unused.
FORMAT_CHANNELS = {"A8R8G8B8": 4, "X8R8G8B8": 3, "R5G6B5": 3, "A1R5G5B5": 4, "A4R4G4B4": 4, "DXT1": 3, "DXT2": 4,
                   "DXT3": 4, "DXT4": 4, "DXT5": 4}
DDS_BLOCK_BYTES = {"DXT1": 8, "DXT2": 16, "DXT3": 16, "DXT4": 16, "DXT5": 16}
DDS_TEXEL_BYTES = {"A1R5G5B5": 2, "A8R8G8B8": 4}
DDS_ALPHA_PIXELS = 4 * 1024 * 1024  # tools/dds_census.py leaves a larger top mip's alpha unknown


def dds_chain(dds: bytes) -> tuple[str, int, int, list[tuple[int, int, int, int]]]:
    """A DDS file's stored format, size and mip levels ((width, height, offset, length), largest first), from the
    legacy DDS header and pixel format; the levels must fill the file exactly."""
    if len(dds) < 128 or dds[:4] != b"DDS ":
        raise Unreadable("not a DDS file")
    flags, height, width = struct.unpack_from("<3I", dds, 8)
    count = u32(dds, 28)
    pf_flags, fourcc, bits, *masks = struct.unpack_from("<I4s5I", dds, 80)
    if pf_flags & 0x4:
        layout = fourcc.decode("latin-1")
    elif pf_flags & 0x40 and (bits, *masks) == (16, 0x7C00, 0x3E0, 0x1F, 0x8000):
        layout = "A1R5G5B5"
    elif pf_flags & 0x40 and (bits, *masks) == (32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000):
        layout = "A8R8G8B8"
    else:
        raise Unreadable("a pixel format the inventory does not admit")
    if layout not in DDS_BLOCK_BYTES and layout not in DDS_TEXEL_BYTES:
        raise Unreadable("a pixel format the inventory does not admit")
    levels, at, side_w, side_h = [], 128, width, height
    for _ in range(max(1, count) if flags & 0x20000 else 1):  # DDSD_MIPMAPCOUNT
        if layout in DDS_BLOCK_BYTES:
            length = max(1, (side_w + 3) // 4) * max(1, (side_h + 3) // 4) * DDS_BLOCK_BYTES[layout]
        else:
            length = side_w * side_h * DDS_TEXEL_BYTES[layout]
        levels.append((side_w, side_h, at, length))
        at += length
        side_w, side_h = max(1, side_w // 2), max(1, side_h // 2)
    if at != len(dds):
        raise Unreadable("the mip levels do not fill the file")
    return layout, width, height, levels


def dds_alpha(dds: bytes, layout: str, width: int, height: int):
    """How the top mip uses alpha as Pillow decodes it: none (every texel opaque), binary (only transparent or opaque
    texels) or graded; unknown where tools/dds_census.py does not classify (DXT4, DXT5, or a top mip over its pixel
    budget). DXT2 stores its alpha as DXT3 does and only premultiplies its colour, so it is decoded as DXT3."""
    if layout in ("DXT4", "DXT5") or width * height > DDS_ALPHA_PIXELS:
        return "unknown"
    if Image is None:
        return NOT_CHECKED
    if layout == "DXT2":
        dds = dds[:84] + b"DXT3" + dds[88:]
    try:
        with Image.open(io.BytesIO(dds)) as image:
            image.load()
            if "A" not in image.getbands():
                return "none"
            histogram = image.getchannel("A").histogram()
    except Exception as error:  # Pillow raises many kinds; any of them means the gate could not read it
        raise Unreadable(f"Pillow refused the texture: {type(error).__name__}") from error
    values = {value for value, count in enumerate(histogram) if count}
    return "none" if values == {255} else "binary" if values <= {0, 255} else "graded"


def dds_fields(asset: dict, dds: bytes, report: "Report") -> dict:
    """A DDS file's row: its header's format, size and mip count, each mip's bytes hashed where the header puts them,
    its format's channels and its top mip's alpha. A texture the inventory did not admit establishes nothing."""
    if asset["details"].get("ddsStatus") != "valid":
        return expect()
    layout, width, height, levels = dds_chain(dds)
    mips = [{"index": number, "width": side_w, "height": side_h, "length": length,
             "sha256": hashlib.sha256(dds[at:at + length]).hexdigest()}
            for number, (side_w, side_h, at, length) in enumerate(levels)]
    if asset["details"].get("mips") != mips:
        report.fail(f"{asset['id']}: its mip details are not its header's chain")
    return expect(format=layout, width=width, height=height, mipLevels=len(levels),
                  alpha=dds_alpha(dds, layout, width, height), channels=FORMAT_CHANNELS.get(layout))


def texture_record_fields(asset: dict, record: bytes, report: "Report") -> dict:
    """A texture record's row: the PC record's own width, height, frame count and format (at the offsets
    tools/aya_texture_fidelity_census.py states) and each frame's mip count. Its format is the one the record names."""
    if asset["details"].get("descriptorStatus") != "parsed":
        return expect()
    layout = texture_layout
    if record[:4] != b"DXTX" or record[layout.CTEX_START:layout.CTEX_START + 4] != b"CTEX" or len(record) < layout.CTEX_END:
        raise Unreadable("not a PC texture record")
    width = struct.unpack_from("<i", record, layout.CTEX_WIDTH_OFFSET)[0]
    height = struct.unpack_from("<h", record, layout.CTEX_HEIGHT_OFFSET)[0]
    frames = u32(record, layout.CTEX_FRAME_COUNT_OFFSET)
    code = struct.unpack_from("<i", record, layout.CTEX_FORMAT_OFFSET)[0]
    if not 0 < frames <= 256:
        raise Unreadable("a frame count outside the parser's bound")
    per_frame, at = [], layout.CTEX_END
    for _ in range(frames):
        if record[at:at + 4] != b"TFRM" or at + 12 > len(record):
            raise Unreadable("a frame record is missing")
        per_frame.append(u32(record, at + 8))
        at += 8 + u32(record, at + 4)
    if asset["details"].get("mipLevelsPerFrame") != per_frame:
        report.fail(f"{asset['id']}: its mips per frame are not its frame records'")
    name = inv.cc.TEX_FORMAT_NAMES.get(code, "nk")
    return expect(format=name, width=width, height=height, mipLevels=per_frame[0] if len(set(per_frame)) == 1 else None,
                  channels=FORMAT_CHANNELS.get(name), frames=frames)


PNG_SAMPLES = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}  # samples per pixel by colour type (the PNG specification)


def png_fields(data: bytes) -> dict:
    if data[:8] != bytes((137, 80, 78, 71, 13, 10, 26, 10)) or data[12:16] != b"IHDR":
        raise Unreadable("not a PNG")
    width, height, _depth, colour = struct.unpack_from(">IIBB", data, 16)
    at, transparency = 8, False
    while at + 8 <= len(data):
        length, kind = struct.unpack_from(">I4s", data, at)
        if kind == b"IEND":
            break
        transparency |= kind == b"tRNS"
        at += 12 + length
    alpha = "present" if colour in (4, 6) or transparency else "none"
    return expect(format="png", width=width, height=height, alpha=alpha, channels=PNG_SAMPLES.get(colour))


def tga_fields(data: bytes) -> dict:
    if len(data) < 18:
        raise Unreadable("shorter than a TGA header")
    width, height, _bits, descriptor = struct.unpack_from("<HHBB", data, 12)
    alpha_bits = descriptor & 0x0F
    return expect(format="tga", width=width, height=height, alpha="present" if alpha_bits else "none",
                  channels=4 if alpha_bits else 3)


JPEG_FRAMES = frozenset(range(0xC0, 0xD0)) - {0xC4, 0xC8, 0xCC}


def jpeg_fields(data: bytes) -> dict:
    """The first frame header's size and component count, found by walking the segments from the start of image."""
    if data[:2] != b"\xff\xd8":
        raise Unreadable("no JPEG start of image")
    at = 2
    while at + 4 <= len(data) and data[at] == 0xFF:
        marker = data[at + 1]
        if marker in JPEG_FRAMES and at + 10 <= len(data):
            _precision, height, width, components = struct.unpack_from(">BHHB", data, at + 4)
            return expect(format="jpeg", width=width, height=height, alpha="none", channels=components)
        if marker == 0xDA:
            break
        at += 2 + struct.unpack_from(">H", data, at + 2)[0]
    raise Unreadable("no frame header before the first scan")


def icon_fields(asset: dict, body: bytes) -> dict:
    """An icon resource: proved when it is a BITMAPINFOHEADER of twice the icon's height, then its palette, colour bits
    and mask, exactly; then its size, and alpha present in 32-bit colour or only a mask below it. A bitmap resource
    is never proved."""
    if asset["form"] != "pe-icon" or len(body) < 40:
        return expect()
    size, width, doubled, planes, bits, compression = struct.unpack_from("<IiiHHI", body, 0)
    used = u32(body, 32)
    if size != 40 or width <= 0 or doubled <= 0 or doubled % 2 or planes != 1 or compression or bits not in (1, 4, 8, 24, 32):
        return expect()
    palette = 4 * (used or (1 << bits if bits <= 8 else 0))
    colour = ((width * bits + 31) // 32 * 4) * (doubled // 2)
    mask = ((width + 31) // 32 * 4) * (doubled // 2)
    if size + palette + colour + mask != len(body):
        return expect()
    return expect(format="icon bitmap", width=width, height=doubled // 2, alpha="present" if bits == 32 else "mask")


def ogg_fields(asset: dict, data: bytes) -> dict:
    """The Vorbis identification header's channels and rate, and the last page's granule position, found by walking the
    pages forward from the first."""
    if asset["details"].get("audioStatus") != "parsed":
        return expect()
    if data[:4] != b"OggS" or len(data) < 27:
        raise Unreadable("not an Ogg stream")
    lacing = data[27:27 + data[26]]
    packet = data[27 + len(lacing):27 + len(lacing) + sum(lacing)]
    if packet[:7] != b"\x01vorbis" or len(packet) < 16:
        raise Unreadable("the first packet is not a Vorbis identification header")
    channels, rate = packet[11], u32(packet, 12)
    at = granule = 0
    while at < len(data):
        if data[at:at + 4] != b"OggS" or at + 27 > len(data):
            raise Unreadable("a page does not start where the last one ends")
        segments = data[at + 26]
        granule = struct.unpack_from("<q", data, at + 6)[0]
        at += 27 + segments + sum(data[at + 27:at + 27 + segments])
    if at != len(data) or not rate:
        raise Unreadable("the pages do not end at the end of the file")
    return expect(format="vorbis", channels=channels, sampleRate=rate, durationSeconds=round(granule / rate, 3))


def bank_sample_fields(stream: bytes, start: int, length: int) -> dict:
    """A bank sample: the PCM byte size stored just before its ADPCM bytes, which hold a quarter of it rounded up; the
    bank's samples are one-channel 4-bit IMA ADPCM at the loader's fixed rate (tools/xap_bank_walk.py)."""
    if start < 4:
        raise Unreadable("no PCM size before the sample")
    pcm = u32(stream, start - 4)
    if length != (pcm + 3) // 4:
        raise Unreadable("the sample's length is not its PCM size's")
    rate = xap_bank_walk.SAMPLE_RATE
    return expect(format="ima-adpcm-4bit", channels=1, sampleRate=rate, durationSeconds=round(pcm / 2 / rate, 3))


def bink_fields(asset: dict, data: bytes) -> dict:
    """The Bink header's frame count, size and frame rate."""
    if asset["details"].get("videoStatus") != "parsed":
        return expect()
    if data[:3] != b"BIK" or len(data) < 44:
        raise Unreadable("not a Bink file")
    frames = u32(data, 8)
    width, height, numerator, denominator = struct.unpack_from("<4I", data, 20)
    if not (frames and width and height and numerator and denominator):
        raise Unreadable("a zero header field")
    return expect(format="bink-" + data[:4].decode("latin-1"), width=width, height=height,
                  durationSeconds=round(frames * denominator / numerator, 3), frames=frames)


def animation_fields(start: int, last: int, rate: float | None) -> dict:
    """An animation mode runs through the virtual frames from start to last, either way. Its phase grows by its rate
    once per game tick, 20 ticks a second, a rate up to 0.0001 counting as 1
    (reverse-engineering/asset-formats/cmsh-animation-keys.md); a rate that is not a finite number gives no duration."""
    seconds = None if rate is None else round(1 / (20 * (rate if rate > 0.0001 else 1.0)), 3)
    return expect(format="camd", frames=abs(last - start) + 1, durationSeconds=seconds)


def camd_fields(asset: dict, record: bytes, report: "Report") -> dict:
    """A 36-byte animation record: a 16-byte name, then the mode, start, last frame and frame scaler, then the rate."""
    if len(record) != 36:
        raise Unreadable("not a 36-byte animation record")
    _mode, start, last, scaler = struct.unpack_from("<4i", record, 16)
    rate = struct.unpack_from("<f", record, 32)[0]
    rate = rate if math.isfinite(rate) else None
    details = asset["details"]
    if (details.get("startFrame"), details.get("lastFrame"), details.get("frameScaler"), details.get("rate")) != \
            (start, last, scaler, rate):
        report.fail(f"{asset['id']}: its frame range, scaler or rate details are not its record's")
    return animation_fields(start, last, rate)


def damage_fields(payload: bytes) -> dict:
    """A damage texture: its level count, then each level n, a square of side 2**n at one byte per texel, smallest
    first, filling the payload exactly."""
    (levels,) = struct.unpack_from("<i", payload, 0)
    if not -1 <= levels < 16 or 4 + sum(4 ** n for n in range(levels + 1)) != len(payload):
        raise Unreadable("the levels do not fill the payload")
    if levels < 0:
        return expect(mipLevels=0)
    return expect(format="one byte per texel", width=1 << levels, height=1 << levels, mipLevels=levels + 1, channels=1)


def placed_fields(asset: dict, stream: bytes, start: int, length: int, report: "Report") -> dict | None:
    """The fields the gate reads itself from a placed row's bytes; None for a form it has no reader for."""
    form, body = asset["form"], stream[start:start + length]
    if form == "dds-file":
        return dds_fields(asset, body, report)
    if form.startswith("descriptor-"):
        return texture_record_fields(asset, body, report)
    readers = {"png": png_fields, "tga": tga_fields, "jpeg": jpeg_fields, "damage-texture": damage_fields}
    if form in readers:
        return readers[form](body)
    if form in ("pe-icon", "pe-bitmap"):
        return icon_fields(asset, body)
    if form in ("voice", "music"):
        return ogg_fields(asset, body)
    if form == "bank-sample":
        return bank_sample_fields(stream, start, length)
    if form == "video":
        return bink_fields(asset, body)
    if form == "animation":
        return camd_fields(asset, body, report)
    if form in ("loose-mesh", "embedded-mesh"):
        if body[:4] != b"CMSH":
            raise Unreadable("not a CMSH stream")
        return expect(format="cmsh")
    constants = {"byte-sprite": expect(format="one-byte indices", width=16, height=16, channels=1),
                 "terrain-heightfield": expect(format="heightfield"), "surface-strips": expect(format="surface strips"),
                 "static-shadow-maps": expect()}
    return constants.get(form)


def unplaced_fields(asset: dict) -> dict | None:
    """What an unplaced row's details give: a chained link is a mesh, its animation follows its record's frame range and
    rate, and nothing establishes a mixer mip's fields."""
    details = asset["details"]
    if asset["form"] == "chained-mesh":
        return expect(format="cmsh")
    if asset["form"] == "chained-animation":
        return animation_fields(details.get("startFrame"), details.get("lastFrame"), details.get("rate"))
    if asset["form"] == "terrain-mixer-mip":
        return expect()
    return None


def same(value, wanted) -> bool:
    if isinstance(value, float) or isinstance(wanted, float):
        return value is not None and wanted is not None and math.isclose(value, wanted, rel_tol=0, abs_tol=1e-9)
    return type(value) is type(wanted) and value == wanted


FIELD_READ_ERRORS = (Unreadable, struct.error, TypeError, KeyError)


def compare_fields(asset: dict, read, report: "Report", counted: str) -> None:
    """Every metadata field of a row against the gate's own reading (read() returns it, or None for a form the gate
    has no reader for). A failure names the field, never its value."""
    try:
        wanted = read()
    except FIELD_READ_ERRORS as error:
        report.fail(f"{asset['id']}: the gate cannot read its fields: {error}")
        return
    if wanted is None:
        report.fail(f"{asset['id']}: a {asset['form']} row, which the gate has no reader for")
        return
    agrees = True
    for field in inv.METADATA_FIELDS:
        if wanted[field] is NOT_CHECKED:
            report.count(f"{asset['form']} {field} not read again: Pillow is not installed")
        elif not same(asset[field], wanted[field]):
            report.fail(f"{asset['id']}: its {field} is not what the gate reads")
            agrees = False
    if agrees:
        report.count(counted)


def check_metadata(row: dict, data: bytes, raw: bytes | None, metadata: list[dict], report: "Report") -> None:
    """A file's asset-metadata rows: each names the file's hash, and each placed row's bytes, cut at its coordinates
    from the stored file or from the stream inflated here, hash to its SHA-256, and its fields are what the gate reads
    from them. Only a mesh chain's links, their animations and a mixer mip may be unplaced; their fields follow their
    details. A row too malformed to check fails (the schema check names what it lacks)."""
    for asset in metadata:
        try:
            check_metadata_row(row, data, raw, asset, report)
        except (KeyError, TypeError, AttributeError) as error:
            report.fail(f"{asset.get('id')}: an asset-metadata row the gate cannot check ({type(error).__name__})")


def check_metadata_row(row: dict, data: bytes, raw: bytes | None, asset: dict, report: "Report") -> None:
    identity = asset["identity"]
    if identity["fileSha256"] != row["sha256"]:
        report.fail(f"{asset['id']}: its file hash is not its file's")
        return
    envelope, start, length = identity["envelope"] or "", identity["offset"], identity["length"]
    if start is None and asset["form"] in UNPLACED_FORMS:
        compare_fields(asset, lambda: unplaced_fields(asset), report,
                       "unplaced metadata rows whose fields follow their details")
        return
    if start is None or not length:
        report.fail(f"{asset['id']}: a {asset['form']} row without coordinates")
        return
    stream = data if envelope.startswith(STORED_ENVELOPES) else raw if envelope.startswith(INFLATED_ENVELOPES) else None
    if stream is None:
        report.fail(f"{asset['id']}: an envelope the gate cannot cut ({envelope})")
        return
    if start + length > len(stream) or hashlib.sha256(stream[start:start + length]).hexdigest() != identity["sha256"]:
        report.fail(f"{asset['id']}: the bytes at its coordinates do not hash to its SHA-256")
        return
    report.count("metadata rows whose coordinates hash to their SHA-256")
    compare_fields(asset, lambda: placed_fields(asset, stream, start, length, report), report,
                   "metadata rows whose every field equals the gate's reading")


def check_schema(rows: list[dict], items: list[dict], metadata: list[dict] | None, coverage: dict,
                 report: "Report") -> None:
    """Every row the run wrote meets its definition in tools/content_inventory.schema.json. A failure names the row
    and the field, never its value."""
    try:
        import jsonschema
    except ImportError:
        report.count("schema checks skipped: jsonschema is not installed")
        return
    schema = json.loads((TOOLS / "content_inventory.schema.json").read_text(encoding="utf-8"))
    for definition, name, batch in (("file", "files.jsonl", rows), ("item", "items.jsonl", items),
                                    ("assetMetadata", "asset-metadata.jsonl", metadata or []),
                                    ("coverage", "coverage.json", [coverage])):
        validator = jsonschema.Draft202012Validator({"$defs": schema["$defs"], "$ref": f"#/$defs/{definition}"})
        for row in batch:
            errors = sorted(validator.iter_errors(row), key=lambda error: [str(step) for step in error.absolute_path])
            if errors:
                where = "/".join(str(step) for step in errors[0].absolute_path) or "the row"
                report.fail(f"{name}: {row.get('id') or row.get('path') or 'coverage'}: {where} fails the schema's "
                            f"{errors[0].validator} rule")
        report.count(f"{name} rows checked against the schema", len(batch))


def check_image(row: dict, data: bytes, report: "Report") -> None:
    if Image is None:
        return
    import io
    try:
        with Image.open(io.BytesIO(data)) as image:
            size = image.size
            image.load()
    except Exception as error:  # Pillow raises many kinds; any of them is this file's failure
        report.fail(f"{row['path']}: Pillow refused it: {type(error).__name__}")
        return
    if size != (row["facts"].get("width"), row["facts"].get("height")):
        report.fail(f"{row['path']}: Pillow's size differs from the walker's")
    report.count("images Pillow read at the walker's size")


def check_compose(data: bytes, totals: collections.Counter, worst: list[float], report: "Report", path: str) -> None:
    try:
        meshes = grammar.walk_stream(data, collections.defaultdict(collections.Counter))
    except (grammar.GrammarError, struct.error) as error:
        report.fail(f"{path}: the grammar walk refused it: {error}")
        return
    grammar.check_caches(meshes, totals, worst)


class Report:
    def __init__(self):
        self.counts: collections.Counter = collections.Counter()
        self.failures: list[str] = []

    def count(self, what: str, by: int = 1) -> None:
        self.counts[what] += by

    def fail(self, line: str) -> None:
        self.failures.append(line)


def run(game: Path, inventory: Path, *, compose: bool = True) -> Report:
    report = Report()
    coverage = json.loads((inventory / "coverage.json").read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in (inventory / "files.jsonl").read_text(encoding="utf-8").splitlines()]
    items = [json.loads(line) for line in (inventory / "items.jsonl").read_text(encoding="utf-8").splitlines()]
    if sum(row["storedBytes"] for row in rows) != coverage["installBytes"] or len(rows) != coverage["installFiles"]:
        report.fail("the run's files do not sum to its install")
    unread = coverage["proofs"].get(inv.MSL_UNREAD)
    if unread != 0:
        report.fail(f"the mission-script judge could not read {unread} level archives' worlds" if unread else
                    "the run does not say whether the mission-script judge read every level archive's worlds")
    try:
        walked = walk_folder(game)
    except WalkError as error:
        report.fail(str(error))
        return report
    if Image is None:
        report.count("image checks skipped: Pillow is not installed")
    placed = stream_records([json.loads(line) for line in
                             (inventory / "records.jsonl").read_text(encoding="utf-8").splitlines()])
    metadata_path = inventory / "asset-metadata.jsonl"
    metadata = [json.loads(line) for line in metadata_path.read_text(encoding="utf-8").splitlines()] \
        if metadata_path.is_file() else None
    by_file: dict[str, list[dict]] = collections.defaultdict(list)
    check_schema(rows, items, metadata, coverage, report)
    if metadata is None:
        report.fail("the run wrote no asset-metadata.jsonl")
    else:
        check_metadata_rows(items, metadata, report)
        for asset in metadata:
            identity = asset.get("identity")
            by_file[identity.get("file") if isinstance(identity, dict) else None].append(asset)
    totals: collections.Counter = collections.Counter()
    worst = [0.0, 0.0]
    for row, data in check_files(game, rows, walked, report):
        check_account(row, report)
        if not inv.sniff_agrees(row["family"], inv.sniff(data)):
            report.fail(f"{row['path']}: its magic disagrees with its family {row['family']}")
        if row["problems"]:
            report.fail(f"{row['path']}: {len(row['problems'])} reader problems")
        if row["stream"] != "inflated":
            check_metadata(row, data, None, by_file.pop(row["path"], []), report)
        if row["stream"] == "inflated":
            try:
                raw = inflate_members(data)
            except (ValueError, zlib.error) as error:
                report.fail(f"{row['path']}: the envelope does not inflate: {error}")
                continue
            if len(raw) != row["logicalBytes"]:
                report.fail(f"{row['path']}: inflated size differs from the run's")
            report.count("envelopes inflated independently")
            check_records(row, raw, placed.pop(row["path"].casefold(), []), report)
            check_metadata(row, data, raw, by_file.pop(row["path"], []), report)
            if row["family"] == "lvlr-resource-archive":
                try:
                    report.count("archive chunks walked", len(walk_chunks(raw)))
                except ValueError as error:
                    report.fail(f"{row['path']}: {error}")
                if compose:
                    for chunk_tag, at, size in walk_chunks(raw):
                        if chunk_tag == b"MESH" and b"CMSH" in raw[at + 8:at + 8 + size]:
                            stream, _offset = meshcensus._direct_embedded_cmsh_with_offset(raw[at + 8:at + 8 + size])
                            check_compose(stream, totals, worst, report, row["path"])
            elif row["family"] == "cmsh-mesh" and compose:
                check_compose(raw, totals, worst, report, row["path"])
        if row["family"] in inv.MEDIA_FAMILIES:
            if row["facts"].get("decoder") != "agrees":
                report.fail(f"{row['path']}: the independent decoder did not agree ({row['facts'].get('decoder')})")
            else:
                report.count("media files the independent decoder agreed with")
        if row["path"].casefold().endswith(IMAGE_SUFFIXES):
            check_image(row, data, report)
    for container, left in sorted(placed.items()):
        report.fail(f"{container}: {len(left)} records placed in a stream the gate did not inflate")
    for container, left in sorted(by_file.items(), key=lambda pair: str(pair[0])):
        report.fail(f"{container}: {len(left)} asset-metadata rows for a file the gate did not check")
    if compose:
        report.count("cached positions equal to composed keys", totals["position frames"])
        report.count("cached orientations equal to composed keys", totals["orientation frames"])
        for kind in ("position mismatches", "orientation mismatches"):
            if totals[kind]:
                report.fail(f"{totals[kind]} {kind}: a cached frame is not its composed keys")
    ids = collections.Counter(item["id"] for item in items)
    for name, count in ids.items():
        if count > 1:
            report.fail(f"item id {name} is used {count} times")
    paths = {row["path"] for row in rows}
    for item in items:
        if item["file"] not in paths:
            report.fail(f"{item['id']}: its file is not one of the run's")
    report.count("items checked", len(items))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--game", required=True, type=Path, help="the installed game folder the run read")
    parser.add_argument("--inventory", type=Path, default=ROOT / "local-data" / "content-inventory")
    parser.add_argument("--no-compose", action="store_true", help="skip the animation composition check")
    args = parser.parse_args(argv)
    report = run(args.game, args.inventory, compose=not args.no_compose)
    for key in sorted(report.counts):
        print(f"{key}: {report.counts[key]}")
    for line in report.failures[:60]:
        print("FAIL", line)
    if len(report.failures) > 60:
        print(f"... and {len(report.failures) - 60} more")
    print("content inventory gate: " + ("failed" if report.failures else "passed") + f" ({len(report.failures)} failures)")
    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
