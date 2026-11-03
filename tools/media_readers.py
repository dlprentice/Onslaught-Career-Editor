#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Walkers for the public container formats a game install holds: Ogg Vorbis, Bink 1, PNG, JPEG, TGA, PE, Word's
saved-web-page ActiveMime container, HTML pages, XML documents and plain text.

Each walker follows its format's published layout, proves the layout accounts for the file and refuses (FormatError,
with a reason) whatever does not hold. It returns the spans it can vouch for as (start, length, kind, part), where kind
is DECODED for bytes the walker read or for a payload every bit pattern of which decodes, and OPAQUE for a payload whose
extent is proved but which only a real decoder can read (Vorbis audio packets, Bink frames, JPEG entropy-coded scans).
Bytes it does not claim are not claimed. No retail data or address is held here; a walker reads what it is given.

The Bink layout is the one libavformat's demuxer reads: a 44-byte header, the audio track descriptors, an index of
frame count + 1 words (the low bit of each marks a keyframe) and the frames, each holding one sized packet per audio
track and then the video data.
"""
from __future__ import annotations

import re
import struct
import zlib
from dataclasses import dataclass, field

DECODED, OPAQUE = "decoded", "opaque"
MAX_BINK_FRAMES = 1_000_000
MAX_BINK_TRACKS = 256
MAX_RESOURCE_NODES = 100_000
MAX_RESOURCE_DEPTH = 8


class FormatError(ValueError):
    """The file does not hold the format's layout; the reason says where the walk stopped."""


@dataclass
class Walk:
    spans: list = field(default_factory=list)
    facts: dict = field(default_factory=dict)

    def add(self, start: int, length: int, kind: str, part: str) -> None:
        if length:
            if self.spans and self.spans[-1][2] == kind and self.spans[-1][3] == part \
                    and self.spans[-1][0] + self.spans[-1][1] == start:
                last = self.spans[-1]
                self.spans[-1] = (last[0], last[1] + length, kind, part)
            else:
                self.spans.append((start, length, kind, part))


# ---------------------------------------------------------------------------------------------------------------- Ogg
_REVERSED = bytes(int(f"{value:08b}"[::-1], 2) for value in range(256))


def ogg_crc(data: bytes) -> int:
    """Ogg's CRC-32 (polynomial 0x04C11DB7, not reflected, zero start, no final XOR).

    zlib's CRC is the reflected form of the same polynomial, so it gives this one over the bit-reversed bytes with its
    own start and final XOR cancelled, and the result bit-reversed.
    """
    reflected = zlib.crc32(data.translate(_REVERSED), 0xFFFFFFFF) ^ 0xFFFFFFFF
    return int(f"{reflected:032b}"[::-1], 2)


def read_vorbis_comment(packet: bytes) -> dict:
    """The second Vorbis header: the vendor string and comment list, ending in the framing bit."""
    at = 7
    if at + 4 > len(packet):
        raise FormatError("truncated Vorbis comment header")
    (vendor,) = struct.unpack_from("<I", packet, at)
    at += 4 + vendor
    if at + 4 > len(packet):
        raise FormatError("truncated Vorbis comment header")
    (comments,) = struct.unpack_from("<I", packet, at)
    at += 4
    for _ in range(comments):
        if at + 4 > len(packet):
            raise FormatError("truncated Vorbis comment list")
        (size,) = struct.unpack_from("<I", packet, at)
        at += 4 + size
    if at + 1 != len(packet) or not packet[at] & 1:
        raise FormatError("Vorbis comment header does not end in its framing bit")
    return {"vendorBytes": vendor, "comments": comments}


def walk_ogg(data: bytes) -> Walk:
    """Every page's checksum, sequence and flags, and the three Vorbis headers; audio packets stay OPAQUE."""
    walk = Walk()
    if data[:4] != b"OggS":
        raise FormatError("no Ogg capture pattern at the start")
    position, pages, packets, serial, open_packet = 0, 0, 0, None, False
    expected_sequence, granule, last_flags = 0, None, 0
    headers: list[bytes] = []
    pending = bytearray()
    audio_from: int | None = None
    while position < len(data):
        if data[position:position + 4] != b"OggS":
            raise FormatError("page capture pattern missing")
        if position + 27 > len(data):
            raise FormatError("truncated page header")
        if data[position + 4] != 0:
            raise FormatError("unsupported stream structure version")
        flags = data[position + 5]
        if flags & ~7:
            raise FormatError("reserved page flag set")
        (page_granule, page_serial, sequence, stored) = struct.unpack_from("<qIII", data, position + 6)
        segments = data[position + 26]
        body = position + 27 + segments
        if body > len(data):
            raise FormatError("truncated segment table")
        lacing = data[position + 27:body]
        end = body + sum(lacing)
        if end > len(data):
            raise FormatError("truncated page body")
        checked = data[position:position + 22] + b"\0\0\0\0" + data[position + 26:end]
        if ogg_crc(checked) != stored:
            raise FormatError("page checksum mismatch")
        if pages == 0:
            if not flags & 2:
                raise FormatError("first page lacks the beginning-of-stream flag")
            serial = page_serial
        elif flags & 2:
            raise FormatError("beginning-of-stream flag after the first page")
        if page_serial != serial:
            raise FormatError("page belongs to another logical stream")
        if sequence != expected_sequence:
            raise FormatError("page sequence is not contiguous")
        if bool(flags & 1) != open_packet:
            raise FormatError("continuation flag disagrees with the open packet")
        expected_sequence += 1
        walk.add(position, body - position, DECODED, "ogg/page-header")
        at = body
        segment_start = body
        for value in lacing:
            if audio_from is None and len(headers) < 3:
                pending += data[at:at + value]
            at += value
            if value < 255:
                open_packet = False
                packets += 1
                if audio_from is None:
                    headers.append(bytes(pending))
                    pending.clear()
                    if len(headers) == 3:
                        walk.add(segment_start, at - segment_start, DECODED, "ogg/vorbis-headers")
                        segment_start = at
                        audio_from = at
            else:
                open_packet = True
        walk.add(segment_start, end - segment_start, DECODED if audio_from is None else OPAQUE,
                 "ogg/vorbis-headers" if audio_from is None else "ogg/audio-packets")
        if page_granule != -1:
            granule = page_granule
        last_flags = flags
        pages += 1
        position = end
    if open_packet:
        raise FormatError("the stream ends inside a packet")
    if not last_flags & 4:
        raise FormatError("last page lacks the end-of-stream flag")
    if len(headers) < 3:
        raise FormatError("fewer than the three Vorbis headers")
    identification, comment, setup = headers
    if identification[:7] != b"\x01vorbis" or len(identification) != 30:
        raise FormatError("first packet is not a Vorbis identification header")
    if comment[:7] != b"\x03vorbis":
        raise FormatError("second packet is not a Vorbis comment header")
    if setup[:7] != b"\x05vorbis":
        raise FormatError("third packet is not a Vorbis setup header")
    (version, channels, rate) = struct.unpack_from("<IBI", identification, 7)
    if version != 0 or channels == 0 or rate == 0 or not identification[29] & 1:
        raise FormatError("invalid Vorbis identification header")
    walk.facts = {"pages": pages, "packets": packets, "audioPackets": packets - 3, "channels": channels,
                  "sampleRate": rate, "samples": granule, **read_vorbis_comment(comment)}
    return walk


# --------------------------------------------------------------------------------------------------------------- Bink
def walk_bink(data: bytes) -> Walk:
    """The header, track descriptors, frame index and every frame's audio packet sizes; packets stay OPAQUE."""
    walk = Walk()
    if len(data) < 44 or data[:3] != b"BIK":
        raise FormatError("not a Bink file")
    size_field, frames, largest, _frames2, width, height, rate_num, rate_den, flags, tracks = struct.unpack_from(
        "<10I", data, 4)
    if size_field + 8 != len(data):
        raise FormatError("stored file size disagrees with the file")
    if not 0 < frames <= MAX_BINK_FRAMES or tracks > MAX_BINK_TRACKS:
        raise FormatError("frame or track count out of bounds")
    if not (width and height and rate_num and rate_den):
        raise FormatError("a header field is zero")
    index = 44 + 12 * tracks
    table_end = index + 4 * (frames + 1)
    if table_end > len(data):
        raise FormatError("frame index runs past the file")
    walk.add(0, table_end, DECODED, "bink/header-and-index")
    offsets = struct.unpack_from(f"<{frames + 1}I", data, index)
    if offsets[0] & ~1 != table_end:
        raise FormatError("first frame does not follow the index")
    if offsets[frames] & ~1 != len(data):
        raise FormatError("frame index does not end at the end of the file")
    keyframes, biggest, audio_bytes, video_bytes = 0, 0, 0, 0
    for number in range(frames):
        start, end = offsets[number] & ~1, offsets[number + 1] & ~1
        keyframes += offsets[number] & 1
        if end <= start:
            raise FormatError("frame index is not increasing")
        biggest = max(biggest, end - start)
        at = start
        for _track in range(tracks):
            if at + 4 > end:
                raise FormatError("audio packet size runs past its frame")
            (size,) = struct.unpack_from("<I", data, at)
            walk.add(at, 4, DECODED, "bink/packet-sizes")
            at += 4
            if size > end - at:
                raise FormatError("audio packet runs past its frame")
            walk.add(at, size, OPAQUE, "bink/audio-packets")
            audio_bytes += size
            at += size
        walk.add(at, end - at, OPAQUE, "bink/video-packets")
        video_bytes += end - at
    if biggest != largest:
        raise FormatError("largest-frame field disagrees with the index")
    walk.facts = {"version": data[3:4].decode("latin-1"), "frames": frames, "width": width, "height": height,
                  "fps": [rate_num, rate_den], "audioTracks": tracks, "keyframes": keyframes, "flags": flags,
                  "audioPacketBytes": audio_bytes, "videoPacketBytes": video_bytes}
    return walk


# ---------------------------------------------------------------------------------------------------------------- PNG
PNG_SIGNATURE = bytes((137, 80, 78, 71, 13, 10, 26, 10))
PNG_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
_ADAM7 = ((0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2))


def _png_rows(width: int, height: int, bits: int, interlace: int) -> list[tuple[int, int]]:
    """(rows, bytes per row without the filter byte) for each pass of the image."""
    if interlace == 0:
        return [(height, (width * bits + 7) // 8)]
    passes = []
    for x0, y0, dx, dy in _ADAM7:
        w = (width - x0 + dx - 1) // dx if width > x0 else 0
        h = (height - y0 + dy - 1) // dy if height > y0 else 0
        if w and h:
            passes.append((h, (w * bits + 7) // 8))
    return passes


def walk_png(data: bytes) -> Walk:
    """Chunk CRCs, the header, and the inflated image data's size and row filters."""
    walk = Walk()
    if data[:8] != PNG_SIGNATURE:
        raise FormatError("no PNG signature")
    walk.add(0, 8, DECODED, "png/structure")
    position, header, idat, ended = 8, None, bytearray(), False
    chunks, transparency = 0, False
    while position < len(data) and not ended:
        if position + 12 > len(data):
            raise FormatError("truncated chunk")
        (length,) = struct.unpack_from(">I", data, position)
        kind = data[position + 4:position + 8]
        end = position + 12 + length
        if end > len(data):
            raise FormatError("chunk runs past the file")
        body = data[position + 8:position + 8 + length]
        if zlib.crc32(data[position + 4:position + 8 + length]) != struct.unpack_from(">I", data, end - 4)[0]:
            raise FormatError("chunk checksum mismatch")
        if kind == b"IHDR":
            if header is not None or length != 13:
                raise FormatError("invalid image header")
            header = struct.unpack(">IIBBBBB", body)
        elif header is None:
            raise FormatError("first chunk is not the image header")
        elif kind == b"IDAT":
            idat += body
        elif kind == b"IEND":
            ended = True
        transparency = transparency or kind == b"tRNS"
        walk.add(position, end - position, DECODED, "png/structure")
        chunks += 1
        position = end
    if not ended:
        raise FormatError("no end chunk")
    width, height, depth, colour, compression, filtering, interlace = header
    if colour not in PNG_CHANNELS or compression or filtering or interlace > 1 or not width or not height:
        raise FormatError("unsupported image header")
    try:
        pixels = zlib.decompress(bytes(idat))
    except zlib.error as error:
        raise FormatError("image data does not inflate") from error
    bits = depth * PNG_CHANNELS[colour]
    passes = _png_rows(width, height, bits, interlace)
    if len(pixels) != sum(rows * (size + 1) for rows, size in passes):
        raise FormatError("inflated image data has the wrong size")
    at = 0
    for rows, size in passes:
        for _ in range(rows):
            if pixels[at] > 4:
                raise FormatError("unknown row filter")
            at += size + 1
    walk.facts = {"width": width, "height": height, "bitDepth": depth, "colourType": colour, "interlace": interlace,
                  "channels": PNG_CHANNELS[colour], "transparencyChunk": transparency, "chunks": chunks,
                  "decodedBytes": len(pixels), "trailingBytes": len(data) - position}
    return walk


# --------------------------------------------------------------------------------------------------------------- JPEG
JPEG_START = bytes((255, 216, 255))
_JPEG_FRAMES = frozenset(range(0xC0, 0xD0)) - {0xC4, 0xC8, 0xCC}


def walk_jpeg(data: bytes) -> Walk:
    """Marker segments and the extent of each entropy-coded scan, which stays OPAQUE."""
    walk = Walk()
    if data[:3] != JPEG_START:
        raise FormatError("no JPEG start of image")
    walk.add(0, 2, DECODED, "jpeg/markers")
    position, size, scans, ended = 2, None, 0, False
    while position < len(data) and not ended:
        if data[position] != 0xFF:
            raise FormatError("expected a marker")
        start = position
        while position < len(data) and data[position] == 0xFF:
            position += 1
        if position >= len(data):
            raise FormatError("truncated marker")
        marker = data[position]
        position += 1
        if marker == 0xD9:
            walk.add(start, position - start, DECODED, "jpeg/markers")
            ended = True
            break
        if marker == 0x01 or 0xD0 <= marker <= 0xD8:
            walk.add(start, position - start, DECODED, "jpeg/markers")
            continue
        if position + 2 > len(data):
            raise FormatError("truncated segment length")
        (length,) = struct.unpack_from(">H", data, position)
        if length < 2 or position + length > len(data):
            raise FormatError("segment runs past the file")
        if marker in _JPEG_FRAMES:
            if length < 8:
                raise FormatError("truncated frame header")
            if size is not None:
                raise FormatError("more than one frame header")
            (precision, height, width, components) = struct.unpack_from(">BHHB", data, position + 2)
            size = {"precision": precision, "width": width, "height": height, "components": components,
                    "frameMarker": marker}
        position += length
        walk.add(start, position - start, DECODED, "jpeg/markers")
        if marker == 0xDA:
            scans += 1
            scan = position
            while True:
                at = data.find(b"\xff", position)
                if at < 0 or at + 1 >= len(data):
                    raise FormatError("entropy-coded data runs past the file")
                following = data[at + 1]
                if following == 0 or 0xD0 <= following <= 0xD7:
                    position = at + 2
                    continue
                position = at
                break
            walk.add(scan, position - scan, OPAQUE, "jpeg/entropy-coded")
    if not ended:
        raise FormatError("no end of image")
    if size is None or not scans:
        raise FormatError("no frame or scan")
    walk.facts = {**size, "scans": scans, "trailingBytes": len(data) - position}
    return walk


# ---------------------------------------------------------------------------------------------------------------- TGA
TGA_FOOTER = b"TRUEVISION-XFILE.\0"


def walk_tga(data: bytes) -> Walk:
    """An uncompressed true-colour TGA with its version 2 footer: every bit pattern of the pixels decodes."""
    walk = Walk()
    if len(data) < 18 + 26:
        raise FormatError("shorter than a header and a footer")
    (id_length, palette, image_type, _first, _count, _entry, _x, _y, width, height, bits, descriptor) = struct.unpack_from(
        "<BBBHHBHHHHBB", data, 0)
    if data[-18:] != TGA_FOOTER:
        raise FormatError("no version 2 footer")
    if palette or image_type != 2 or bits not in (16, 24, 32) or not width or not height:
        raise FormatError("not an uncompressed true-colour image")
    (extension, developer) = struct.unpack_from("<II", data, len(data) - 26)
    if extension or developer:
        raise FormatError("extension or developer area present")
    pixels = width * height * bits // 8
    if 18 + id_length + pixels + 26 != len(data):
        raise FormatError("the header's size disagrees with the file")
    walk.add(0, 18 + id_length, DECODED, "tga/header")
    walk.add(18 + id_length, pixels, DECODED, "tga/pixels")
    walk.add(len(data) - 26, 26, DECODED, "tga/footer")
    walk.facts = {"width": width, "height": height, "bitsPerPixel": bits, "descriptor": descriptor}
    return walk


# ----------------------------------------------------------------------------------------------------------------- PE
RESOURCE_TYPES = {1: "cursor", 2: "bitmap", 3: "icon", 4: "menu", 5: "dialog", 6: "string", 9: "accelerator", 10: "rcdata",
                  12: "group-cursor", 14: "group-icon", 16: "version", 24: "manifest"}


def icon_image_holds(body: bytes) -> bool:
    """An icon image: a BITMAPINFOHEADER of twice the icon's height, then its palette, colour bits and mask, exactly."""
    if len(body) < 40:
        return False
    (size, width, doubled, planes, bits, compression) = struct.unpack_from("<IiiHHI", body, 0)
    (used,) = struct.unpack_from("<I", body, 32)
    if size != 40 or width <= 0 or doubled <= 0 or doubled % 2 or planes != 1 or compression or bits not in (1, 4, 8, 24, 32):
        return False
    height = doubled // 2
    palette = 4 * (used or (1 << bits if bits <= 8 else 0))
    colour = ((width * bits + 31) // 32 * 4) * height
    mask = ((width + 31) // 32 * 4) * height
    return size + palette + colour + mask == len(body)


def icon_group_holds(body: bytes) -> bool:
    """A group icon directory: a six-byte header and fourteen bytes per image."""
    if len(body) < 6:
        return False
    (reserved, kind, count) = struct.unpack_from("<HHH", body, 0)
    return reserved == 0 and kind in (1, 2) and len(body) == 6 + 14 * count


def walk_pe(data: bytes) -> Walk:
    """The structures a PE loader reads: the DOS header, the PE headers and section table, and the resource tree
    (its directories, entries, names and data entries) with the icons and icon groups that hold. Everything else is
    framed (OPAQUE): the DOS stub, the header padding, section contents (code and data are not content), resource
    bytes the tree does not reach, the certificate and the COFF symbol and string tables, whose records are not read."""
    walk = Walk()
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise FormatError("no MZ header")
    (pe_at,) = struct.unpack_from("<I", data, 0x3C)
    if pe_at < 0x40 or pe_at + 24 > len(data) or data[pe_at:pe_at + 4] != b"PE\0\0":
        raise FormatError("no PE header")
    (_machine, sections, _stamp, symbol_at, symbols, optional_size, _chars) = struct.unpack_from("<HHIIIHH", data, pe_at + 4)
    optional = pe_at + 24
    table = optional + optional_size
    table_end = table + 40 * sections
    if table_end > len(data) or optional_size < 96 or sections > 96:
        raise FormatError("section table runs past the file")
    (magic,) = struct.unpack_from("<H", data, optional)
    if magic == 0x10B:
        directories = optional + 96
        (headers_size,) = struct.unpack_from("<I", data, optional + 60)
    elif magic == 0x20B:
        directories = optional + 112
        (headers_size,) = struct.unpack_from("<I", data, optional + 60)
    else:
        raise FormatError("unknown optional header")
    (rsrc_rva, rsrc_size) = struct.unpack_from("<II", data, directories + 2 * 8)
    (cert_at, cert_size) = struct.unpack_from("<II", data, directories + 4 * 8)
    if headers_size > len(data):
        raise FormatError("headers run past the file")
    if headers_size < table_end:
        raise FormatError("the section table runs past the headers")
    walk.add(0, 0x40, DECODED, "pe/headers")
    walk.add(0x40, pe_at - 0x40, OPAQUE, "pe/dos-stub")
    walk.add(pe_at, table_end - pe_at, DECODED, "pe/headers")
    padding = data[table_end:headers_size]
    walk.add(table_end, len(padding), OPAQUE, "pe/header-padding" if not padding.strip(b"\0") else "pe/header-tail")
    rows = []
    for index in range(sections):
        at = table + 40 * index
        name = data[at:at + 8].split(b"\0", 1)[0].decode("latin-1")
        (virtual_size, rva, raw_size, raw_at) = struct.unpack_from("<IIII", data, at + 8)
        if raw_at + raw_size > len(data):
            raise FormatError("a section runs past the file")
        rows.append((raw_at, raw_size, rva, virtual_size, name))
    resources: list[dict] = []
    tree: list[tuple[int, int]] = []  # the bytes the tree walk reads: directories and their entries, names, data entries

    def file_offset(rva: int) -> int:
        for raw_at, raw_size, base, _virtual, _name in rows:
            if base <= rva < base + raw_size:
                return raw_at + rva - base
        raise FormatError("a resource points outside every section")

    resource_section = next((row for row in rows if row[2] <= rsrc_rva < row[2] + max(row[0] and row[1], 1)), None) \
        if rsrc_rva else None
    if resource_section is not None:
        base = file_offset(rsrc_rva)
        section_end = resource_section[0] + resource_section[1]
        nodes = [0]

        def within(offset: int, length: int) -> bool:
            return offset + length <= rsrc_size and base + offset + length <= section_end

        def descend(directory: int, depth: int, path: tuple) -> None:
            if depth > MAX_RESOURCE_DEPTH:
                raise FormatError("resource tree is deeper than its limit")
            if not within(directory, 16):
                raise FormatError("resource directory runs past its section")
            (named, ids) = struct.unpack_from("<HH", data, base + directory + 12)
            if not within(directory, 16 + 8 * (named + ids)):
                raise FormatError("resource directory runs past its section")
            tree.append((base + directory, 16 + 8 * (named + ids)))
            for entry in range(named + ids):
                nodes[0] += 1
                if nodes[0] > MAX_RESOURCE_NODES:
                    raise FormatError("resource tree limit exceeded")
                at = base + directory + 16 + 8 * entry
                (name_field, target) = struct.unpack_from("<II", data, at)
                if entry < named:
                    name_at = name_field & 0x7FFFFFFF
                    if not within(name_at, 2) or not within(name_at, 2 + 2 * struct.unpack_from("<H", data, base + name_at)[0]):
                        raise FormatError("resource name runs past its section")
                    tree.append((base + name_at, 2 + 2 * struct.unpack_from("<H", data, base + name_at)[0]))
                key = name_field if entry >= named else "named"
                if target & 0x80000000:
                    descend(target & 0x7FFFFFFF, depth + 1, path + (key,))
                    continue
                if not within(target, 16):
                    raise FormatError("resource entry runs past its section")
                tree.append((base + target, 16))
                (data_rva, size) = struct.unpack_from("<II", data, base + target)
                start = file_offset(data_rva)
                if start + size > len(data):
                    raise FormatError("a resource runs past the file")
                kind = path[0] if path else key
                resources.append({"type": RESOURCE_TYPES.get(kind, str(kind)), "offset": start, "length": size})

        descend(0, 0, ())
    for raw_at, raw_size, rva, _virtual, name in rows:
        if resource_section is not None and rva == resource_section[2]:
            for start, length in _merged(tree):
                walk.add(start, length, DECODED, "pe/resource-tree")
            for row in resources:
                start, size = row["offset"], row["length"]
                body = data[start:start + size]
                # Only an icon image and an icon group are proved. Every other resource stays framed, a cursor too:
                # its image follows a hotspot this walk does not read.
                proved = row["type"] == "icon" and icon_image_holds(body) or \
                    row["type"] == "group-icon" and icon_group_holds(body)
                if proved and row["type"] == "icon":
                    (_header, width, doubled, _planes, bits) = struct.unpack_from("<IiiHH", body, 0)
                    row.update(width=width, height=doubled // 2, bitCount=bits)
                row["status"] = "decoded" if proved else "framed"
                walk.add(start, size, DECODED if proved else OPAQUE,
                         f"pe/resource {row['type']}" if proved else f"pe/resource {row['type']} (framed)")
            _frame_gaps(walk, raw_at, raw_at + raw_size, "pe/resource-section (not reached by the tree)")
        else:
            walk.add(raw_at, raw_size, OPAQUE, f"pe/section {name}")
    last = max([headers_size] + [raw_at + raw_size for raw_at, raw_size, *_ in rows])
    if cert_at and cert_size and cert_at == last and cert_at + cert_size <= len(data):
        walk.add(cert_at, cert_size, OPAQUE, "pe/certificate")
        last += cert_size
    if symbol_at and symbol_at == last:
        strings = symbol_at + 18 * symbols
        if strings + 4 > len(data):
            raise FormatError("symbol table runs past the file")
        (string_bytes,) = struct.unpack_from("<I", data, strings)
        if string_bytes < 4 or strings + string_bytes > len(data):
            raise FormatError("string table runs past the file")
        walk.add(symbol_at, strings + string_bytes - symbol_at, OPAQUE, "pe/coff-symbols")
        last = strings + string_bytes
    position = 0
    for start, length, _kind, _part in sorted(walk.spans):
        if start < position:
            raise FormatError("the file's parts overlap")
        position = start + length
    walk.spans.sort()
    walk.facts = {"sections": [row[4] for row in rows], "resources": resources, "overlayBytes": len(data) - last}
    return walk


def _merged(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Spans as (start, length), sorted, with overlapping or touching ones joined."""
    out: list[list[int]] = []
    for start, length in sorted(spans):
        if out and start <= out[-1][1]:
            out[-1][1] = max(out[-1][1], start + length)
        else:
            out.append([start, start + length])
    return [(start, end - start) for start, end in out]


def _frame_gaps(walk: Walk, start: int, end: int, part: str) -> None:
    """Frame (OPAQUE) every byte of [start, end) no span holds yet."""
    position = start
    for span_start, length, _kind, _part in sorted(walk.spans):
        if span_start + length <= start or span_start >= end:
            continue
        if span_start > position:
            walk.add(position, span_start - position, OPAQUE, part)
        position = max(position, span_start + length)
    if position < end:
        walk.add(position, end - position, OPAQUE, part)


# ---------------------------------------------------------------------------------------------------------- ActiveMime
ACTIVE_MIME_MAGIC = b"ActiveMime"


def walk_active_mime(data: bytes) -> Walk:
    """Word's saved-web-page ActiveMime container: a header whose 16-bit field at 0x1E gives the zlib stream's offset
    less 46, then the stream.

    The stream must inflate completely. What it inflates to (an OLE compound file, which can hold a document's macro
    project) is not walked, so it stays OPAQUE; bytes after the stream's end are left unclaimed, since no published
    layout says what they are.
    """
    walk = Walk()
    if data[:10] != ACTIVE_MIME_MAGIC or len(data) < 0x20:
        raise FormatError("no ActiveMime header")
    (field_value,) = struct.unpack_from("<H", data, 0x1E)
    start = field_value + 46
    if start >= len(data):
        raise FormatError("compressed stream starts past the file")
    inflater = zlib.decompressobj()
    try:
        inflated = inflater.decompress(data[start:])
    except zlib.error as error:
        raise FormatError("compressed stream does not inflate") from error
    if not inflater.eof:
        raise FormatError("compressed stream is truncated")
    walk.add(0, start, DECODED, "mso/header")
    walk.add(start, len(data) - start - len(inflater.unused_data), OPAQUE, "mso/compressed-document")
    walk.facts = {"inflatedBytes": len(inflated), "inner": "ole-compound" if inflated[:4] == b"\xd0\xcf\x11\xe0" else "other",
                  "trailingBytes": len(inflater.unused_data)}
    return walk


# --------------------------------------------------------------------------------------------------------------- text
def walk_text(data: bytes) -> Walk:
    """Plain text in an ASCII-compatible encoding: refused when it holds control bytes that text does not."""
    walk = Walk()
    if not data:
        walk.facts = {"encoding": "empty", "lines": 0}
        return walk
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        raise FormatError("byte-order mark: not an 8-bit text file")
    controls = sum(1 for value in data if value < 32 and value not in (9, 10, 12, 13))
    if controls:
        raise FormatError("control bytes in the text")
    try:
        data.decode("ascii")
        encoding = "ascii"
    except UnicodeDecodeError:
        try:
            data.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            encoding = "8-bit"
    walk.add(0, len(data), DECODED, "text")
    crlf = data.count(b"\r\n")
    walk.facts = {"encoding": encoding, "lines": data.count(b"\n") + (0 if data.endswith(b"\n") else 1),
                  "lineEnding": "crlf" if crlf and crlf == data.count(b"\n") else "lf" if not crlf else "mixed"}
    return walk


# ---------------------------------------------------------------------------------------------------- HTML and XML
_HTML_NAME = rb"[A-Za-z][A-Za-z0-9:._-]*"
_HTML_ATTRIBUTE = rb"""(?:\s+[^\s"'<>/=]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s"'<>=`]+))?)"""
_HTML_PIECES = (
    ("comment", re.compile(rb"<!--.*?-->", re.S)),
    ("conditional", re.compile(rb"<!\[[^<>\]]*\]>")),
    ("declaration", re.compile(rb"<![A-Za-z][^<>]*>")),
    ("instruction", re.compile(rb"<\?[^<>]*\?>")),
    ("end-tag", re.compile(rb"</" + _HTML_NAME + rb"\s*>")),
    ("start-tag", re.compile(rb"<(" + _HTML_NAME + rb")" + _HTML_ATTRIBUTE + rb"*\s*/?>")),
)
_HTML_TEXT = re.compile(rb"[^<&]+|&(?:[A-Za-z][A-Za-z0-9]*|#[0-9]+|#[xX][0-9A-Fa-f]+);")
_HTML_RAW = (b"script", b"style")


def walk_html(data: bytes) -> Walk:
    """An HTML page tokenized to its end: every byte is a comment, a conditional or other declaration, a processing
    instruction, a well-formed start or end tag, a script or style element's raw text, character data or a character
    reference, and the page is an html element (after any declarations) with nothing but white space after its end.
    The tokens are not checked against an HTML schema, and nothing renders the page."""
    walk = walk_text(data)
    position, first, last_end, tags = 0, None, None, 0
    while position < len(data):
        if data[position:position + 1] != b"<":
            match = _HTML_TEXT.match(data, position)
            if not match:
                raise FormatError("a character reference that does not close")
            position = match.end()
            continue
        for kind, pattern in _HTML_PIECES:
            match = pattern.match(data, position)
            if match:
                break
        else:
            raise FormatError("markup that is no HTML token")
        if kind in ("start-tag", "end-tag"):
            tags += 1
            name = (match.group(1) if kind == "start-tag" else data[position + 2:match.end() - 1].strip()).lower()
            first = first or (kind, name)
            last_end = name if kind == "end-tag" else None
            if kind == "start-tag" and name in _HTML_RAW and not match.group(0).endswith(b"/>"):
                close = re.compile(rb"</" + name + rb"\s*>", re.I).search(data, match.end())
                if not close:
                    raise FormatError("a script or style element that does not close")
                position = close.end()
                last_end = name
                continue
        position = match.end()
    if first != ("start-tag", b"html") or last_end != b"html" or data[data.rfind(b">") + 1:].strip():
        raise FormatError("not one html element")
    walk.facts["tags"] = tags
    return walk


def walk_xml(data: bytes) -> Walk:
    """A well-formed XML document, as expat parses it to its end."""
    import xml.parsers.expat
    walk = walk_text(data)
    parser = xml.parsers.expat.ParserCreate()
    elements = [0]

    def start(_name, _attributes):
        elements[0] += 1

    parser.StartElementHandler = start
    try:
        parser.Parse(data, True)
    except xml.parsers.expat.ExpatError as error:
        raise FormatError("not well-formed XML") from error
    walk.facts["elements"] = elements[0]
    return walk


_HTML_LINK = re.compile(rb"""(?:src|href|data)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.IGNORECASE)


def html_links(data: bytes) -> list[str]:
    """Every local src/href/data target a page names, decoded and without any fragment; external links are dropped."""
    out = []
    for match in _HTML_LINK.finditer(data):
        raw = next(group for group in match.groups() if group is not None).decode("latin-1")
        target = raw.split("#", 1)[0].replace("\\", "/")
        if target and "://" not in target and not target.lower().startswith(("mailto:", "javascript:", "file:")):
            out.append(target.replace("%20", " "))
    return out
