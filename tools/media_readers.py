#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Walkers for the public container formats a game install holds: Ogg Vorbis, Bink 1, PNG, JPEG, TGA, PE, Word's
saved-web-page ActiveMime container, HTML pages, XML documents and plain text.

Each walker follows its format's published layout, proves the layout accounts for the file and refuses (FormatError,
with a reason) whatever does not hold. It returns the spans it can vouch for as (start, length, kind, part), where kind
is DECODED for bytes the walker read or for a payload every bit pattern of which decodes, and OPAQUE for a payload whose
extent is proved but which only a real decoder can read (Vorbis audio packets, Bink frames and audio track descriptors,
JPEG entropy-coded scans). Bytes it does not claim are not claimed. No retail data or address is held here; a walker
reads what it is given.

The Vorbis setup header (codebooks, floors, residues, mappings and modes) is read field by field as the Vorbis I
specification gives it, and every rule that specification calls an error is refused. The JPEG quantization and Huffman
tables, restart interval, frame component list and scan header are read the same way, as ITU T.81 gives them.

The Bink layout is the one libavformat's demuxer reads: a 44-byte header, the audio track descriptors, an index of
frame count + 1 words (the low bit of each marks a keyframe) and the frames, each holding one sized packet per audio
track and then the video data.
"""
from __future__ import annotations

import collections
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
    """The second Vorbis header: the vendor string and comment list, every string UTF-8 as the specification has it,
    ending in the framing bit. The comments' names and values are not read further."""
    at = 7
    if at + 4 > len(packet):
        raise FormatError("truncated Vorbis comment header")
    (vendor,) = struct.unpack_from("<I", packet, at)
    strings = [packet[at + 4:at + 4 + vendor]]
    at += 4 + vendor
    if at + 4 > len(packet):
        raise FormatError("truncated Vorbis comment header")
    (comments,) = struct.unpack_from("<I", packet, at)
    at += 4
    for _ in range(comments):
        if at + 4 > len(packet):
            raise FormatError("truncated Vorbis comment list")
        (size,) = struct.unpack_from("<I", packet, at)
        strings.append(packet[at + 4:at + 4 + size])
        at += 4 + size
    if at + 1 != len(packet) or not packet[at] & 1:
        raise FormatError("Vorbis comment header does not end in its framing bit")
    for text in strings:
        try:
            text.decode("utf-8")
        except UnicodeDecodeError:
            raise FormatError("Vorbis comment header holds text that is not UTF-8") from None
    return {"vendorBytes": vendor, "comments": comments}


# The Vorbis I setup header (specification section 4.2.4, with the codebook of 3.2.1, floor 0 of 6.2.1, floor 1 of
# 7.2.2 and the residue of 8.6.1). Every field is read in the specification's order and the packet must end at its
# framing bit. The rules the specification calls errors are refused: a reserved type, a codebook whose codewords do not
# fill a prefix code exactly, a reference to a codebook, floor, residue, mapping or channel that does not exist, and a
# floor 1 whose X values repeat. Five rules go beyond its text. Three follow libvorbis: a codebook's lone used entry
# takes a one-bit codeword, a floor 0 or residue stage book needs a value lookup, and a residue's classbook needs an
# entry for every combination of its classes. One follows FFmpeg: a residue's range does not run backwards (libvorbis
# reads such a residue as empty). One is the account's own: no byte follows the framing bit, so the walk closes exactly,
# which neither decoder checks. The codebook's value table and a floor's or residue's plain numbers are read as the
# integers they are: no bit pattern of them is an error.
class _Bits:
    """The Vorbis bit packing: bits come least significant first within each byte. A read past the end is an error."""

    def __init__(self, data: bytes, start: int):
        self.data, self.position, self.limit = data, 8 * start, 8 * len(data)

    def take(self, count: int) -> int:
        end = self.position + count
        if end > self.limit:
            raise FormatError("setup header ends inside a field")
        value = int.from_bytes(self.data[self.position >> 3:(end + 7) >> 3], "little") >> (self.position & 7)
        self.position = end
        return value & ((1 << count) - 1)

    def skip(self, count: int) -> None:
        if self.position + count > self.limit:
            raise FormatError("setup header ends inside a field")
        self.position += count


def _ilog(value: int) -> int:
    """The specification's ilog: how many bits hold the value (none for zero or less)."""
    return value.bit_length() if value > 0 else 0


def _lookup1_values(entries: int, dimensions: int) -> int:
    """The greatest integer whose power of the codebook's dimensions is not above its entry count."""
    value = int(entries ** (1.0 / dimensions)) if entries else 0
    while value ** dimensions > entries:
        value -= 1
    while (value + 1) ** dimensions <= entries:
        value += 1
    return value


def _read_codebook(bits: _Bits) -> tuple[int, int, int]:
    """(dimensions, entries, lookup type). The codeword lengths are counted per length: whether they fill a prefix code
    exactly is the sum of 2^-length over the used entries, which is the same whatever order the entries come in."""
    if bits.take(24) != 0x564342:
        raise FormatError("codebook sync pattern missing")
    dimensions, entries = bits.take(16), bits.take(24)
    lengths: collections.Counter = collections.Counter()
    if bits.take(1):  # ordered: a run of entries for each length, lengths growing by one per run
        at, length = 0, bits.take(5) + 1
        while at < entries:
            number = bits.take(_ilog(entries - at))
            if length > 32:
                raise FormatError("ordered codebook length passes 32 bits")
            if number > entries - at:
                raise FormatError("ordered codebook lengths overrun its entries")
            lengths[length] += number
            at, length = at + number, length + 1
    else:
        sparse = bits.take(1)
        for _ in range(entries):
            if not sparse or bits.take(1):
                lengths[bits.take(5) + 1] += 1
    used = sum(lengths.values())
    if used == 1 and lengths[1] != 1:  # a lone entry is a tree of one node: libvorbis takes it only with a one-bit codeword
        raise FormatError("codebook with one used entry gives it a longer codeword than one bit")
    if used > 1:
        filled = sum(count << (32 - length) for length, count in lengths.items())
        if filled > 1 << 32:
            raise FormatError("codebook codewords overfill their tree")
        if filled < 1 << 32:
            raise FormatError("codebook codewords leave their tree unfilled")
    lookup = bits.take(4)
    if lookup > 2:
        raise FormatError("codebook lookup type is reserved")
    if lookup:
        if not dimensions:
            raise FormatError("codebook lookup has no dimensions")
        bits.skip(64)  # the minimum and the delta, two packed floats
        value_bits = bits.take(4) + 1
        bits.take(1)  # whether the values accumulate
        bits.skip(value_bits * (_lookup1_values(entries, dimensions) if lookup == 1 else entries * dimensions))
    return dimensions, entries, lookup


def _read_floor(bits: _Bits, books: list[tuple[int, int, int]]) -> int:
    """A floor's type; its books must exist, and a floor 0's must give vectors."""
    kind = bits.take(16)
    if kind > 1:
        raise FormatError("floor type is reserved")
    if kind == 0:
        order, rate, bark_map = bits.take(8), bits.take(16), bits.take(16)
        bits.skip(14)  # the amplitude bits and offset
        if not (order and rate and bark_map):
            raise FormatError("floor 0 has a zero order, rate or bark map size")
        for _ in range(bits.take(4) + 1):
            book = bits.take(8)
            if book >= len(books) or not books[book][2]:
                raise FormatError("floor 0 names a codebook that does not give vectors")
        return 0
    partitions = [bits.take(4) for _ in range(bits.take(5))]
    dimensions = []
    for _ in range(max(partitions, default=-1) + 1):
        dimensions.append(bits.take(3) + 1)
        subclasses = bits.take(2)
        if subclasses and bits.take(8) >= len(books):
            raise FormatError("floor 1 names a codebook that does not exist")
        for _ in range(1 << subclasses):
            if bits.take(8) - 1 >= len(books):  # one less than the number read: none (-1) is allowed
                raise FormatError("floor 1 names a codebook that does not exist")
    bits.skip(2)  # the multiplier
    range_bits = bits.take(4)
    values = [0]  # the implicit first X value; the implicit last, 2^range_bits, no read value can equal
    for number in partitions:
        values += [bits.take(range_bits) for _ in range(dimensions[number])]
        if len(values) > 64:
            raise FormatError("floor 1 has too many X values")
    if len(set(values)) != len(values):
        raise FormatError("floor 1 repeats an X value")
    return 1


def _read_residue(bits: _Bits, books: list[tuple[int, int, int]]) -> None:
    if bits.take(16) > 2:
        raise FormatError("residue type is reserved")
    begin, end = bits.take(24), bits.take(24)
    bits.skip(24)  # the partition size, less one
    if begin > end:
        raise FormatError("residue range runs backwards")
    classes, classbook = bits.take(6) + 1, bits.take(8)
    if classbook >= len(books) or not books[classbook][0]:
        raise FormatError("residue classbook does not exist or has no dimensions")
    words = 1  # a classword names one class for each of the classbook's dimensions; its entries must be enough for all
    for _ in range(books[classbook][0] if classes > 1 else 1):
        words *= classes
        if words > books[classbook][1]:
            raise FormatError("residue classbook has fewer entries than its classes can need")
    cascades = []
    for _ in range(classes):
        low = bits.take(3)
        cascades.append(low | (bits.take(5) << 3 if bits.take(1) else 0))
    for cascade in cascades:
        for stage in range(8):
            if cascade >> stage & 1:
                book = bits.take(8)
                if book >= len(books) or not books[book][2]:
                    raise FormatError("residue names a codebook that does not give vectors")


def _read_mapping(bits: _Bits, channels: int, floors: int, residues: int) -> None:
    if bits.take(16):
        raise FormatError("mapping type is not zero")
    submaps = bits.take(4) + 1 if bits.take(1) else 1
    if bits.take(1):
        width = _ilog(channels - 1)
        for _ in range(bits.take(8) + 1):
            magnitude, angle = bits.take(width), bits.take(width)
            if magnitude == angle or magnitude >= channels or angle >= channels:
                raise FormatError("mapping couples a channel that does not exist or with itself")
    if bits.take(2):
        raise FormatError("mapping reserved bits are set")
    if submaps > 1 and any(bits.take(4) >= submaps for _ in range(channels)):
        raise FormatError("mapping assigns a channel to a submap that does not exist")
    for _ in range(submaps):
        bits.skip(8)  # the time configuration placeholder
        if bits.take(8) >= floors:
            raise FormatError("mapping names a floor that does not exist")
        if bits.take(8) >= residues:
            raise FormatError("mapping names a residue that does not exist")


def read_vorbis_setup(packet: bytes, channels: int) -> dict:
    """Read a Vorbis setup header for a stream of the given channels, and return how many codebooks, floors, residues,
    mappings and modes it holds. FormatError says which rule it breaks."""
    if packet[:7] != b"\x05vorbis":
        raise FormatError("third packet is not a Vorbis setup header")
    bits = _Bits(packet, 7)
    books = [_read_codebook(bits) for _ in range(bits.take(8) + 1)]
    for _ in range(bits.take(6) + 1):
        if bits.take(16):
            raise FormatError("time domain transform type is not zero")
    floors = [_read_floor(bits, books) for _ in range(bits.take(6) + 1)]
    residues = bits.take(6) + 1
    for _ in range(residues):
        _read_residue(bits, books)
    mappings = bits.take(6) + 1
    for _ in range(mappings):
        _read_mapping(bits, channels, len(floors), residues)
    modes = bits.take(6) + 1
    for _ in range(modes):
        bits.skip(1)  # which of the two block sizes the mode uses
        if bits.take(16) or bits.take(16):
            raise FormatError("mode window or transform type is not zero")
        if bits.take(8) >= mappings:
            raise FormatError("mode names a mapping that does not exist")
    if not bits.take(1):
        raise FormatError("setup header lacks its framing bit")
    if (bits.position + 7) >> 3 != len(packet):
        raise FormatError("setup header holds bytes after its framing bit")
    return {"codebooks": len(books), "floors": len(floors), "residues": residues, "mappings": mappings, "modes": modes}


def walk_ogg(data: bytes) -> Walk:
    """Every page's checksum, sequence and flags, and the three Vorbis headers, the setup header read field by field;
    audio packets stay OPAQUE."""
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
    small, large = identification[28] & 15, identification[28] >> 4  # the block sizes' powers of two
    if not 6 <= small <= large <= 13:  # 64 to 8192, the first not above the second
        raise FormatError("Vorbis block sizes out of range")
    walk.facts = {"pages": pages, "packets": packets, "audioPackets": packets - 3, "channels": channels,
                  "sampleRate": rate, "samples": granule, "blockSizes": [1 << small, 1 << large],
                  **read_vorbis_comment(comment), **read_vorbis_setup(setup, channels)}
    return walk


# --------------------------------------------------------------------------------------------------------------- Bink
def walk_bink(data: bytes) -> Walk:
    """The header, frame index and every frame's audio packet sizes; the audio track descriptors and the packets stay
    OPAQUE."""
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
    # The demuxer reads each track's sample rate, flags and identifier from its descriptor and skips the first word of
    # three; no reader of this repository reads them, so they count only when the decoder read the file.
    walk.add(0, 44, DECODED, "bink/header")
    walk.add(44, 12 * tracks, OPAQUE, "bink/audio-track-descriptors")
    walk.add(index, table_end - index, DECODED, "bink/frame-index")
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


def _jpeg_quantization_tables(body: bytes) -> None:
    """DQT: tables of 64 elements, each one byte (precision 0) or two (precision 1), destinations 0 to 3, no zero."""
    at = 0
    while at < len(body):
        precision, destination = body[at] >> 4, body[at] & 15
        width = precision + 1
        if precision > 1 or destination > 3 or at + 1 + 64 * width > len(body):
            raise FormatError("quantization table segment is malformed")
        table = body[at + 1:at + 1 + 64 * width]
        if any(int.from_bytes(table[index:index + width], "big") == 0 for index in range(0, len(table), width)):
            raise FormatError("quantization table holds a zero element")
        at += 1 + 64 * width


def _jpeg_huffman_tables(body: bytes) -> None:
    """DHT: a class (DC or AC) and destination 0 to 3, the number of codes of each length 1 to 16, then that many
    symbols. The codes are the shortest first in order; none may be all ones, so they fill less than the whole tree."""
    at = 0
    while at < len(body):
        if at + 17 > len(body) or body[at] >> 4 > 1 or body[at] & 15 > 3:
            raise FormatError("Huffman table segment is malformed")
        counts = body[at + 1:at + 17]
        if sum(counts) > 256 or at + 17 + sum(counts) > len(body):
            raise FormatError("Huffman table segment is malformed")
        if sum(count << (16 - length) for length, count in enumerate(counts, 1)) >= 1 << 16:
            raise FormatError("Huffman table codes use the all-ones code or overfill their tree")
        at += 17 + sum(counts)


def _jpeg_components(body: bytes) -> list[int]:
    """The component identifiers of a frame header: after its 6 fixed bytes, 3 per component (identifier, horizontal and
    vertical sampling factors of 1 to 4, quantization table 0 to 3), the identifiers all different."""
    count = body[5]
    if not count or len(body) != 6 + 3 * count:
        raise FormatError("frame header's component list is malformed")
    identifiers = [body[6 + 3 * index] for index in range(count)]
    for index in range(count):
        sampling, table = body[7 + 3 * index], body[8 + 3 * index]
        if not 1 <= sampling >> 4 <= 4 or not 1 <= sampling & 15 <= 4 or table > 3:
            raise FormatError("frame header's component list is malformed")
    if len(set(identifiers)) != count:
        raise FormatError("frame header's component list is malformed")
    return identifiers


def _jpeg_scan_header(body: bytes, frame_marker: int, components: list[int]) -> None:
    """SOS: 1 to 4 components of the frame, each once with its two table selectors, then the spectral selection and the
    successive approximation. A sequential frame's scan runs the whole spectrum with no approximation."""
    count = body[0] if body else 0
    if not 1 <= count <= 4 or len(body) != 4 + 2 * count:
        raise FormatError("scan header is malformed")
    selected = [body[1 + 2 * index] for index in range(count)]
    if any(body[2 + 2 * index] >> 4 > 3 or body[2 + 2 * index] & 15 > 3 for index in range(count)):
        raise FormatError("scan header is malformed")
    if len(set(selected)) != count or not set(selected) <= set(components):
        raise FormatError("scan names a component the frame lacks")
    start, end, approximation = body[1 + 2 * count], body[2 + 2 * count], body[3 + 2 * count]
    if end > 63 or start > end or approximation >> 4 > 13 or approximation & 15 > 13:
        raise FormatError("scan header is malformed")
    if frame_marker in (0xC0, 0xC1) and (start, end, approximation) != (0, 63, 0):
        raise FormatError("scan header is malformed")


def walk_jpeg(data: bytes) -> Walk:
    """Marker segments and the extent of each entropy-coded scan, which stays OPAQUE. The quantization and Huffman
    tables, the restart interval, the frame header's components and each scan header are read, and a malformed one
    refused; the application, comment and any other segment are only framed by their lengths."""
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
        body = data[position + 2:position + length]
        if marker in _JPEG_FRAMES:
            if length < 8:
                raise FormatError("truncated frame header")
            if size is not None:
                raise FormatError("more than one frame header")
            identifiers = _jpeg_components(body)
            (precision, height, width, components) = struct.unpack_from(">BHHB", data, position + 2)
            size = {"precision": precision, "width": width, "height": height, "components": components,
                    "frameMarker": marker}
        elif marker == 0xDB:
            _jpeg_quantization_tables(body)
        elif marker == 0xC4:
            _jpeg_huffman_tables(body)
        elif marker == 0xDD and len(body) != 2:
            raise FormatError("restart interval segment is malformed")
        elif marker == 0xDA:
            if size is None:
                raise FormatError("scan before the frame header")
            _jpeg_scan_header(body, size["frameMarker"], identifiers)
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
