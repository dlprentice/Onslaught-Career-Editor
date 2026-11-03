#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks tools/media_readers.py on authored files (no game bytes): each walker accepts a well-formed file, accounts for
it without overlap, and refuses each malformation with its own reason; every refusal reason in the module is reached."""
from __future__ import annotations

import re
import struct
import unittest
import zlib
from pathlib import Path

import media_readers as media

REACHED: set[str] = set()


def refusal(test: unittest.TestCase, walker, data: bytes, reason: str) -> None:
    with test.assertRaises(media.FormatError) as caught:
        walker(data)
    test.assertEqual(str(caught.exception), reason)
    REACHED.add(reason)


def covered(walk: media.Walk, size: int) -> int:
    """Bytes the walk claims, checking that its spans never overlap."""
    position, total = 0, 0
    for start, length, _kind, _part in sorted(walk.spans):
        assert start >= position, "spans overlap"
        position = start + length
        total += length
    assert position <= size
    return total


# --------------------------------------------------------------------------------------------------------------- Ogg
def naive_ogg_crc(data: bytes) -> int:
    """Bit by bit, most significant bit first, polynomial 0x04C11DB7, from zero, no final XOR."""
    crc = 0
    for value in data:
        crc ^= value << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if crc & 0x80000000 else (crc << 1) & 0xFFFFFFFF
    return crc


def page(flags: int, granule: int, sequence: int, packets: list[bytes], *, continued_last: bool = False,
         serial: int = 7) -> bytes:
    lacing, body = bytearray(), bytearray()
    for number, packet in enumerate(packets):
        size = len(packet)
        while size >= 255:
            lacing.append(255)
            size -= 255
        if not (continued_last and number == len(packets) - 1):
            lacing.append(size)
        body += packet
    header = b"OggS" + bytes([0, flags]) + struct.pack("<qIII", granule, serial, sequence, 0) + bytes([len(lacing)])
    raw = header + bytes(lacing) + bytes(body)
    return raw[:22] + struct.pack("<I", media.ogg_crc(raw)) + raw[26:]


def identification(channels: int = 1, rate: int = 22050) -> bytes:
    return b"\x01vorbis" + struct.pack("<IBIiiiBB", 0, channels, rate, 0, 64000, 0, 0xB8, 1)


def comment() -> bytes:
    vendor = b"authored"
    return b"\x03vorbis" + struct.pack("<I", len(vendor)) + vendor + struct.pack("<II", 1, 3) + b"a=b" + b"\x01"


def ogg_file(audio: list[bytes] | None = None, granule: int = 4410) -> bytes:
    audio = audio if audio is not None else [b"\x00" * 300, b"\x01" * 40]
    return (page(2, 0, 0, [identification()]) + page(0, 0, 1, [comment(), b"\x05vorbis" + b"\x00" * 9])
            + page(4, granule, 2, audio))


def refresh(data: bytes, at: int = 0) -> bytes:
    """Recompute the checksum of the page at an offset after an authored edit."""
    segments = data[at + 26]
    end = at + 27 + segments + sum(data[at + 27:at + 27 + segments])
    zeroed = data[at:at + 22] + b"\0\0\0\0" + data[at + 26:end]
    return data[:at + 22] + struct.pack("<I", media.ogg_crc(zeroed)) + data[at + 26:]


class OggTests(unittest.TestCase):
    def test_the_checksum_is_ogg_s(self):
        self.assertEqual(media.ogg_crc(b"123456789"), 0x89A1897F)  # the published check value of this CRC
        for sample in (b"", b"\x00", b"OggS" * 99, bytes(range(256)) * 3):
            self.assertEqual(media.ogg_crc(sample), naive_ogg_crc(sample))

    def test_a_stream_walks_to_its_end(self):
        data = ogg_file()
        walk = media.walk_ogg(data)
        self.assertEqual(covered(walk, len(data)), len(data))
        self.assertEqual(walk.facts["pages"], 3)
        self.assertEqual(walk.facts["packets"], 5)
        self.assertEqual(walk.facts["audioPackets"], 2)
        self.assertEqual(walk.facts["samples"], 4410)
        self.assertEqual(walk.facts["sampleRate"], 22050)
        kinds = {part: kind for _start, _length, kind, part in walk.spans}
        self.assertEqual(kinds["ogg/audio-packets"], media.OPAQUE)
        self.assertEqual(kinds["ogg/vorbis-headers"], media.DECODED)

    def test_a_packet_spanning_pages_is_followed(self):
        long = b"\x02" * 600
        data = (page(2, 0, 0, [identification()]) + page(0, 0, 1, [comment(), b"\x05vorbis"])
                + page(0, -1, 2, [long[:510]], continued_last=True) + page(5, 99, 3, [long[510:]]))
        self.assertEqual(media.walk_ogg(data).facts["audioPackets"], 1)

    def test_refusals(self):
        good = ogg_file()
        first = 27 + good[26] + sum(good[27:27 + good[26]])
        refusal(self, media.walk_ogg, b"OgxS" + good[4:], "no Ogg capture pattern at the start")
        refusal(self, media.walk_ogg, good + b"x", "page capture pattern missing")
        refusal(self, media.walk_ogg, good + b"OggS", "truncated page header")
        refusal(self, media.walk_ogg, refresh(good[:4] + b"\x01" + good[5:]), "unsupported stream structure version")
        refusal(self, media.walk_ogg, refresh(good[:5] + b"\x0a" + good[6:]), "reserved page flag set")
        refusal(self, media.walk_ogg, good[:27], "truncated segment table")
        refusal(self, media.walk_ogg, good[:first - 1], "truncated page body")
        refusal(self, media.walk_ogg, good[:30] + bytes([good[30] ^ 1]) + good[31:], "page checksum mismatch")
        refusal(self, media.walk_ogg, refresh(good[:5] + b"\x00" + good[6:]),
                "first page lacks the beginning-of-stream flag")
        refusal(self, media.walk_ogg, good[:first] + refresh(good[first:first + 5] + b"\x02" + good[first + 6:]),
                "beginning-of-stream flag after the first page")
        refusal(self, media.walk_ogg, good[:first] + page(0, 0, 1, [comment(), b"\x05vorbis"], serial=8),
                "page belongs to another logical stream")
        refusal(self, media.walk_ogg, good[:first] + page(0, 0, 5, [comment(), b"\x05vorbis"]),
                "page sequence is not contiguous")
        refusal(self, media.walk_ogg, good[:first] + page(1, 0, 1, [comment(), b"\x05vorbis"]),
                "continuation flag disagrees with the open packet")
        refusal(self, media.walk_ogg, page(2, 0, 0, [identification()]) + page(4, 0, 1, [b"\x01" * 255],
                                                                             continued_last=True),
                "the stream ends inside a packet")
        refusal(self, media.walk_ogg, page(2, 0, 0, [identification()]) + page(0, 0, 1, [comment(), b"\x05vorbis"])
                + page(0, 9, 2, [b"\x00"]), "last page lacks the end-of-stream flag")
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(), comment()]), "fewer than the three Vorbis headers")
        refusal(self, media.walk_ogg, page(6, 0, 0, [b"\x01vorbit" + bytes(23), comment(), b"\x05vorbis"]),
                "first packet is not a Vorbis identification header")
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(), b"\x03vorbit", b"\x05vorbis"]),
                "second packet is not a Vorbis comment header")
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(), comment(), b"\x05vorbit"]),
                "third packet is not a Vorbis setup header")
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(channels=0), comment(), b"\x05vorbis"]),
                "invalid Vorbis identification header")
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(), b"\x03vorbis\x09", b"\x05vorbis"]),
                "truncated Vorbis comment header")
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(), b"\x03vorbis" + struct.pack("<I", 0) + b"\x01",
                                                     b"\x05vorbis"]), "truncated Vorbis comment header")
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(), b"\x03vorbis" + struct.pack("<II", 0, 2) + b"\x01",
                                                     b"\x05vorbis"]), "truncated Vorbis comment list")
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(), comment()[:-1] + b"\x00", b"\x05vorbis"]),
                "Vorbis comment header does not end in its framing bit")


# -------------------------------------------------------------------------------------------------------------- Bink
def bink_file(frames: list[tuple[list[bytes], bytes]], *, tracks: int = 1, largest: int | None = None,
              size_delta: int = 0, first: int | None = None, last: int | None = None, rate: int = 25) -> bytes:
    bodies = [b"".join(struct.pack("<I", len(packet)) + packet for packet in audio) + video for audio, video in frames]
    table_end = 44 + 12 * tracks + 4 * (len(frames) + 1)
    offsets, at = [], table_end
    for body in bodies:
        offsets.append(at)
        at += len(body)
    offsets.append(at)
    if first is not None:
        offsets[0] = first
    if last is not None:
        offsets[-1] = last
    offsets[0] |= 1
    largest = max(len(body) for body in bodies) if largest is None else largest
    header = b"BIKi" + struct.pack("<10I", at - 8 + size_delta, len(frames), largest, len(frames), 64, 48, rate, 1, 0,
                                   tracks)
    descriptors = struct.pack(f"<{tracks}I", *([0] * tracks)) + b"".join(struct.pack("<HH", 22050, 0)
                                                                         for _ in range(tracks))
    descriptors += struct.pack(f"<{tracks}I", *range(tracks))
    return header + descriptors + struct.pack(f"<{len(offsets)}I", *offsets) + b"".join(bodies)


class BinkTests(unittest.TestCase):
    def test_frames_walk_to_the_end(self):
        data = bink_file([([b"\x10" * 8], b"\x20" * 30), ([b"\x11" * 4], b"\x21" * 50)])
        walk = media.walk_bink(data)
        self.assertEqual(covered(walk, len(data)), len(data))
        self.assertEqual(walk.facts["frames"], 2)
        self.assertEqual(walk.facts["keyframes"], 1)
        self.assertEqual(walk.facts["audioPacketBytes"], 12)
        self.assertEqual(walk.facts["videoPacketBytes"], 80)

    def test_refusals(self):
        frames = [([b"\x10" * 8], b"\x20" * 30), ([b"\x11" * 4], b"\x21" * 50)]
        good = bink_file(frames)
        refusal(self, media.walk_bink, b"BIX" + good[3:], "not a Bink file")
        refusal(self, media.walk_bink, bink_file(frames, size_delta=1), "stored file size disagrees with the file")
        refusal(self, media.walk_bink, bink_file(frames, tracks=300), "frame or track count out of bounds")
        refusal(self, media.walk_bink, bink_file(frames, rate=0), "a header field is zero")
        short = b"BIKi" + struct.pack("<10I", 36, 40, 1, 40, 64, 48, 25, 1, 0, 0)
        refusal(self, media.walk_bink, short, "frame index runs past the file")
        refusal(self, media.walk_bink, bink_file(frames, first=100), "first frame does not follow the index")
        refusal(self, media.walk_bink, bink_file(frames, last=10), "frame index does not end at the end of the file")
        refusal(self, media.walk_bink, bink_index_backwards(), "frame index is not increasing")
        refusal(self, media.walk_bink, bink_file([([b"\x10\x10"], b"")], tracks=2), "audio packet size runs past its frame")
        refusal(self, media.walk_bink, bink_overlong_audio(), "audio packet runs past its frame")
        refusal(self, media.walk_bink, bink_file(frames, largest=1), "largest-frame field disagrees with the index")


def bink_index_backwards() -> bytes:
    """Three frames whose middle index entry runs backwards."""
    data = bytearray(bink_file([([b"\x10" * 4], b"\x20" * 10)] * 3))
    index = 44 + 12
    first, = struct.unpack_from("<I", data, index)
    struct.pack_into("<I", data, index + 4, (first & ~1) - 2)
    return bytes(data)


def bink_overlong_audio() -> bytes:
    data = bytearray(bink_file([([b"\x10" * 4], b"\x20" * 10)]))
    start = struct.unpack_from("<I", data, 44 + 12)[0] & ~1
    struct.pack_into("<I", data, start, 99)
    return bytes(data)


# --------------------------------------------------------------------------------------------------------------- PNG
def png_chunk(kind: bytes, body: bytes) -> bytes:
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))


def png_file(width: int = 2, height: int = 2, *, rows: bytes | None = None, colour: int = 2, interlace: int = 0,
             extra: bytes = b"") -> bytes:
    channels = {0: 1, 2: 3, 6: 4}[colour]
    rows = rows if rows is not None else b"".join(b"\x00" + bytes(width * channels) for _ in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, colour, 0, 0, interlace)
    return (media.PNG_SIGNATURE + png_chunk(b"IHDR", header) + png_chunk(b"IDAT", zlib.compress(rows))
            + png_chunk(b"IEND", b"") + extra)


class PngTests(unittest.TestCase):
    def test_an_image_walks_and_inflates(self):
        data = png_file()
        walk = media.walk_png(data)
        self.assertEqual(covered(walk, len(data)), len(data))
        self.assertEqual((walk.facts["width"], walk.facts["height"]), (2, 2))

    def test_an_interlaced_image_has_its_passes(self):
        # Adam7 on 3 x 3 grey: passes of 1, 1, 1, 2 (x2 rows), 1 (x1), 3 ... sized by the pass geometry.
        passes = media._png_rows(3, 3, 8, 1)
        rows = b"".join(b"\x00" + bytes(size) for count, size in passes for _ in range(count))
        walk = media.walk_png(png_file(3, 3, rows=rows, colour=0, interlace=1))
        self.assertEqual(walk.facts["interlace"], 1)

    def test_trailing_bytes_are_left_unclaimed(self):
        data = png_file(extra=b"tail")
        self.assertEqual(covered(media.walk_png(data), len(data)), len(data) - 4)

    def test_refusals(self):
        good = png_file()
        refusal(self, media.walk_png, b"\x00" + good[1:], "no PNG signature")
        refusal(self, media.walk_png, good[:12], "truncated chunk")
        refusal(self, media.walk_png, good[:8] + struct.pack(">I", 999) + good[12:], "chunk runs past the file")
        refusal(self, media.walk_png, good[:20] + bytes([good[20] ^ 1]) + good[21:], "chunk checksum mismatch")
        refusal(self, media.walk_png, media.PNG_SIGNATURE + png_chunk(b"IHDR", bytes(12)), "invalid image header")
        refusal(self, media.walk_png, media.PNG_SIGNATURE + png_chunk(b"tEXt", b"a\0b"),
                "first chunk is not the image header")
        refusal(self, media.walk_png, good[:-12], "no end chunk")
        refusal(self, media.walk_png, png_file(colour=6)[:8] + png_chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 5, 0, 0, 0))
                + png_chunk(b"IEND", b""), "unsupported image header")
        broken = media.PNG_SIGNATURE + png_chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0)) \
            + png_chunk(b"IDAT", b"not deflate") + png_chunk(b"IEND", b"")
        refusal(self, media.walk_png, broken, "image data does not inflate")
        refusal(self, media.walk_png, png_file(rows=b"\x00" * 5), "inflated image data has the wrong size")
        refusal(self, media.walk_png, png_file(rows=b"\x07" + bytes(6) + b"\x00" + bytes(6)), "unknown row filter")


# -------------------------------------------------------------------------------------------------------------- JPEG
def segment(marker: int, body: bytes) -> bytes:
    return bytes((255, marker)) + struct.pack(">H", len(body) + 2) + body


def jpeg_file(*, frames: int = 1, scan: bytes = b"\x12\x34\xff\x00\x56\xff\xd0\x78", end: bool = True) -> bytes:
    frame = segment(0xC0, struct.pack(">BHHB", 8, 3, 5, 1) + b"\x01\x11\x00")
    out = media.JPEG_START[:2] + segment(0xE0, b"JFIF\0\x01\x01\0\0\x01\0\x01\0\0") + frame * frames
    out += segment(0xDA, b"\x01\x01\x00\x00\x3f\x00") + scan
    return out + (bytes((255, 0xD9)) if end else b"")


class JpegTests(unittest.TestCase):
    def test_markers_and_the_scan_extent(self):
        data = jpeg_file()
        walk = media.walk_jpeg(data)
        self.assertEqual(covered(walk, len(data)), len(data))
        self.assertEqual((walk.facts["width"], walk.facts["height"], walk.facts["scans"]), (5, 3, 1))
        self.assertIn(("jpeg/entropy-coded", media.OPAQUE), {(part, kind) for _s, _l, kind, part in walk.spans})

    def test_refusals(self):
        good = jpeg_file()
        refusal(self, media.walk_jpeg, b"\x00" + good[1:], "no JPEG start of image")
        refusal(self, media.walk_jpeg, good[:2] + segment(0xE0, b"x") + b"\x00", "expected a marker")
        refusal(self, media.walk_jpeg, good[:2] + b"\xff\xff", "truncated marker")
        refusal(self, media.walk_jpeg, good[:2] + b"\xff\xe0\x00", "truncated segment length")
        refusal(self, media.walk_jpeg, good[:2] + b"\xff\xe0\x00\x40", "segment runs past the file")
        refusal(self, media.walk_jpeg, good[:2] + segment(0xC0, b"\x08\x00"), "truncated frame header")
        refusal(self, media.walk_jpeg, jpeg_file(frames=2), "more than one frame header")
        refusal(self, media.walk_jpeg, jpeg_file(end=False), "entropy-coded data runs past the file")
        refusal(self, media.walk_jpeg, media.JPEG_START[:2] + segment(0xE0, b"x"), "no end of image")
        refusal(self, media.walk_jpeg, media.JPEG_START[:2] + bytes((255, 0xD9)), "no frame or scan")


# --------------------------------------------------------------------------------------------------------------- TGA
def tga_file(width: int = 2, height: int = 2, bits: int = 24, *, image_type: int = 2, pixels: int | None = None,
             footer: bytes = media.TGA_FOOTER, areas: tuple[int, int] = (0, 0)) -> bytes:
    header = struct.pack("<BBBHHBHHHHBB", 0, 0, image_type, 0, 0, 0, 0, 0, width, height, bits, 0)
    count = width * height * bits // 8 if pixels is None else pixels
    return header + bytes(count) + struct.pack("<II", *areas) + footer


class TgaTests(unittest.TestCase):
    def test_an_uncompressed_image(self):
        data = tga_file()
        walk = media.walk_tga(data)
        self.assertEqual(covered(walk, len(data)), len(data))
        self.assertEqual((walk.facts["width"], walk.facts["height"]), (2, 2))

    def test_refusals(self):
        refusal(self, media.walk_tga, b"\0" * 30, "shorter than a header and a footer")
        refusal(self, media.walk_tga, tga_file(footer=b"X" * 18), "no version 2 footer")
        refusal(self, media.walk_tga, tga_file(image_type=10), "not an uncompressed true-colour image")
        refusal(self, media.walk_tga, tga_file(areas=(1, 0)), "extension or developer area present")
        refusal(self, media.walk_tga, tga_file(pixels=5), "the header's size disagrees with the file")


# ---------------------------------------------------------------------------------------------------------------- PE
def pe_file(*, resource: bool = True, icon_ok: bool = True, symbols: bool = False, bad_icon_group: bool = False) -> bytes:
    """A minimal PE32: one code section and, optionally, a resource section with an icon and its group."""
    file_align = 0x200
    icon = struct.pack("<IiiHHIIiiII", 40, 2, 4, 1, 8, 0, 0, 0, 0, 0, 0) + bytes(4 * 256) + bytes(4 * 2) + bytes(4 * 2)
    if not icon_ok:
        icon += b"x"
    group = struct.pack("<HHH", 0, 1, 1) + bytes(14)
    if bad_icon_group:
        group += b"x"
    rsrc = bytearray()

    def directory(entries: list[tuple[int, int]]) -> bytes:
        return struct.pack("<IIHHHH", 0, 0, 0, 0, 0, len(entries)) + b"".join(struct.pack("<II", a, b) for a, b in entries)

    # root -> two types -> one id each -> one language each -> data entries
    root_size = 16 + 8 * 2
    type_size = 16 + 8
    layout = {"root": 0, "icon": root_size, "group": root_size + type_size,
              "iconlang": root_size + 2 * type_size, "grouplang": root_size + 3 * type_size}
    data_entries = root_size + 4 * type_size
    icon_data = data_entries + 32
    group_data = icon_data + len(icon)
    rva = 0x2000
    rsrc += directory([(3, 0x80000000 | layout["icon"]), (14, 0x80000000 | layout["group"])])
    rsrc += directory([(1, 0x80000000 | layout["iconlang"])])
    rsrc += directory([(1, 0x80000000 | layout["grouplang"])])
    rsrc += directory([(0x409, data_entries)])
    rsrc += directory([(0x409, data_entries + 16)])
    rsrc += struct.pack("<IIII", rva + icon_data, len(icon), 0, 0) + struct.pack("<IIII", rva + group_data, len(group), 0, 0)
    rsrc += icon + group
    rsrc += bytes(-len(rsrc) % file_align)
    text = bytes(file_align)
    sections = [(b".text", 0x1000, text)] + ([(b".rsrc", rva, bytes(rsrc))] if resource else [])
    headers = 0x400
    optional = bytearray(224)
    struct.pack_into("<H", optional, 0, 0x10B)
    struct.pack_into("<I", optional, 60, headers)
    if resource:
        struct.pack_into("<II", optional, 96 + 16, rva, len(rsrc))
    out = bytearray(headers)
    out[:2] = b"MZ"
    struct.pack_into("<I", out, 0x3C, 0x40)
    raw_at = headers
    table = bytearray()
    for name, base, body in sections:
        table += name.ljust(8, b"\0") + struct.pack("<IIII", len(body), base, len(body), raw_at) + bytes(16)
        raw_at += len(body)
    coff_symbols = raw_at if symbols else 0
    out[0x40:0x40 + 24] = b"PE\0\0" + struct.pack("<HHIIIHH", 0x14C, len(sections), 0, coff_symbols, 1 if symbols else 0,
                                                    224, 0)
    out[0x58:0x58 + 224] = optional
    out[0x58 + 224:0x58 + 224 + len(table)] = table
    for _name, _base, body in sections:
        out += body
    if symbols:
        out += bytes(18) + struct.pack("<I", 4)
    return bytes(out)


class PeTests(unittest.TestCase):
    def test_headers_sections_and_resources(self):
        data = pe_file()
        walk = media.walk_pe(data)
        self.assertEqual(covered(walk, len(data)), len(data))
        types = sorted(r["type"] for r in walk.facts["resources"])
        self.assertEqual(types, ["group-icon", "icon"])
        self.assertTrue(all(r["status"] == "decoded" for r in walk.facts["resources"]))
        parts = {part: kind for _s, _l, kind, part in walk.spans}
        self.assertEqual(parts["pe/section .text"], media.OPAQUE)

    def test_a_resource_that_does_not_hold_stays_framed(self):
        walk = media.walk_pe(pe_file(icon_ok=False, bad_icon_group=True))
        self.assertTrue(all(r["status"] == "framed" for r in walk.facts["resources"]))

    def test_coff_symbols_are_claimed(self):
        data = pe_file(symbols=True)
        walk = media.walk_pe(data)
        self.assertEqual(covered(walk, len(data)), len(data))
        self.assertEqual(walk.facts["overlayBytes"], 0)

    def test_refusals(self):
        good = pe_file()
        refusal(self, media.walk_pe, b"ZM" + good[2:], "no MZ header")
        refusal(self, media.walk_pe, good[:0x3C] + struct.pack("<I", 0x80) + good[0x40:], "no PE header")
        bad = bytearray(good)
        struct.pack_into("<H", bad, 0x46, 200)
        refusal(self, media.walk_pe, bytes(bad), "section table runs past the file")
        bad = bytearray(good)
        struct.pack_into("<H", bad, 0x58, 0x999)
        refusal(self, media.walk_pe, bytes(bad), "unknown optional header")
        bad = bytearray(good)
        struct.pack_into("<I", bad, 0x58 + 60, len(good) + 1)
        refusal(self, media.walk_pe, bytes(bad), "headers run past the file")
        bad = bytearray(good)
        struct.pack_into("<I", bad, 0x58 + 224 + 20, len(good))
        refusal(self, media.walk_pe, bytes(bad), "a section runs past the file")
        symbols = bytearray(pe_file(symbols=True))
        refusal(self, media.walk_pe, bytes(symbols[:-4]), "symbol table runs past the file")
        struct.pack_into("<I", symbols, len(symbols) - 4, 99)
        refusal(self, media.walk_pe, bytes(symbols), "string table runs past the file")
        for reason, edit in pe_resource_edits(good):
            refusal(self, media.walk_pe, edit, reason)
        limit = media.MAX_RESOURCE_NODES
        media.MAX_RESOURCE_NODES = 3
        try:
            refusal(self, media.walk_pe, good, "resource tree limit exceeded")
        finally:
            media.MAX_RESOURCE_NODES = limit


def pe_resource_edits(good: bytes) -> list[tuple[str, bytes]]:
    rsrc = 0x400 + 0x200
    edits = []
    data = bytearray(good)
    struct.pack_into("<I", data, rsrc + 32 + 16 + 4, 0x80000000 | 0x7FFF0)
    edits.append(("resource directory runs past its section", bytes(data)))
    data = bytearray(good)
    struct.pack_into("<I", data, rsrc + 32 + 3 * 24 + 16 + 4, 0x7FFF0)
    edits.append(("resource entry runs past its section", bytes(data)))
    data = bytearray(good)
    entries = rsrc + 32 + 4 * 24
    struct.pack_into("<I", data, entries, 0x9000)
    edits.append(("a resource points outside every section", bytes(data)))
    data = bytearray(good)
    struct.pack_into("<I", data, entries + 4, 0x10000)
    edits.append(("a resource runs past the file", bytes(data)))
    edits.append(("resource tree is deeper than its limit", deep_resource_tree(good)))
    return edits


def deep_resource_tree(good: bytes) -> bytes:
    """A directory whose entry points back at itself: the walk must stop at its limits."""
    data = bytearray(good)
    rsrc = 0x400 + 0x200
    struct.pack_into("<HH", data, rsrc + 12, 0, 1)
    struct.pack_into("<II", data, rsrc + 16, 3, 0x80000000)
    return bytes(data)


# -------------------------------------------------------------------------------------------------------- ActiveMime
def active_mime(*, start_field: int = 4, body: bytes = b"\xd0\xcf\x11\xe0" + bytes(60), tail: bytes = b"") -> bytes:
    header = bytearray(start_field + 46)
    header[:10] = media.ACTIVE_MIME_MAGIC
    struct.pack_into("<H", header, 0x1E, start_field)
    return bytes(header) + zlib.compress(body) + tail


class ActiveMimeTests(unittest.TestCase):
    def test_the_stream_inflates(self):
        data = active_mime(tail=b"\x01\x02")
        walk = media.walk_active_mime(data)
        self.assertEqual(covered(walk, len(data)), len(data) - 2)
        self.assertEqual(walk.facts["inner"], "ole-compound")

    def test_refusals(self):
        refusal(self, media.walk_active_mime, b"ActiveMimX" + bytes(40), "no ActiveMime header")
        refusal(self, media.walk_active_mime, active_mime(start_field=400)[:100], "compressed stream starts past the file")
        refusal(self, media.walk_active_mime, active_mime()[:50] + b"garbage", "compressed stream does not inflate")
        refusal(self, media.walk_active_mime, active_mime()[:-4], "compressed stream is truncated")


# --------------------------------------------------------------------------------------------------------------- text
class TextTests(unittest.TestCase):
    def test_encodings(self):
        self.assertEqual(media.walk_text(b"a\r\nb\r\n").facts, {"encoding": "ascii", "lines": 2, "lineEnding": "crlf"})
        self.assertEqual(media.walk_text("é\n".encode()).facts["encoding"], "utf-8")
        self.assertEqual(media.walk_text(b"\xe9\n").facts["encoding"], "8-bit")
        self.assertEqual(media.walk_text(b"").facts["encoding"], "empty")

    def test_refusals(self):
        refusal(self, media.walk_text, "x".encode("utf-16"), "byte-order mark: not an 8-bit text file")
        refusal(self, media.walk_text, b"a\x00b", "control bytes in the text")

    def test_page_links(self):
        page_text = b'<img src="a_files/image001.png"><a href="#top">x</a><a href=\'b.htm#s\'><link href=c.css>' \
                    b'<a href="http://example.com/x.png"><a href="mailto:x@y">'
        self.assertEqual(media.html_links(page_text), ["a_files/image001.png", "b.htm", "c.css"])


class ReasonsTests(unittest.TestCase):
    def test_every_refusal_reason_is_reached(self):
        """Run last (by name): every FormatError reason the module can give is given by some test above."""
        loader = unittest.TestLoader()
        others = unittest.TestSuite(loader.loadTestsFromTestCase(case) for case in (
            OggTests, BinkTests, PngTests, JpegTests, TgaTests, PeTests, ActiveMimeTests, TextTests))
        unittest.TextTestRunner(stream=open("/dev/null", "w"), verbosity=0).run(others)
        source = Path(media.__file__).read_text(encoding="utf-8")
        reasons = set(re.findall(r'FormatError\("([^"]+)"\)', source))
        self.assertTrue(reasons)
        self.assertEqual(sorted(reasons - REACHED), [])


if __name__ == "__main__":
    unittest.main()
