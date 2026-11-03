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


def identification(channels: int = 1, rate: int = 22050, blocks: int = 0xB8) -> bytes:
    """The identification header; blocks holds the block sizes' powers of two (a low and a high nibble: 256 and 2048)."""
    return b"\x01vorbis" + struct.pack("<IBIiiiBB", 0, channels, rate, 0, 64000, 0, blocks, 1)


def comment() -> bytes:
    vendor = b"authored"
    return b"\x03vorbis" + struct.pack("<I", len(vendor)) + vendor + struct.pack("<II", 1, 3) + b"a=b" + b"\x01"


# ------------------------------------------------------------------------------------ authored Vorbis setup headers
class Bits:
    """An authored bit string, least significant bit first, as the Vorbis packing writes it."""

    def __init__(self) -> None:
        self.value, self.count = 0, 0

    def put(self, value: int, width: int) -> "Bits":
        assert 0 <= value < 1 << width, (value, width)
        self.value |= value << self.count
        self.count += width
        return self

    def add(self, other: "Bits") -> "Bits":
        self.value |= other.value << self.count
        self.count += other.count
        return self

    def data(self) -> bytes:
        return self.value.to_bytes((self.count + 7) // 8, "little")


def ilog(value: int) -> int:
    return value.bit_length()


def codebook(lengths: tuple[int, ...] = (1, 1), *, dimensions: int = 1, lookup: int = 0, value_bits: int = 4,
             sparse: bool = False, runs: tuple[int, ...] | None = None, first: int = 1, entries: int | None = None,
             sync: int = 0x564342, table: int | None = None) -> Bits:
    """One codebook. lengths gives each entry's codeword length (0 leaves an entry unused, in a sparse book); runs
    writes an ordered book instead, that many entries at first, first + 1, ... bits. A lookup book carries the
    multiplicands its type needs (table gives another number)."""
    count = entries if entries is not None else sum(runs) if runs is not None else len(lengths)
    bits = Bits().put(sync, 24).put(dimensions, 16).put(count, 24)
    if runs is not None:
        bits.put(1, 1).put(first - 1, 5)
        left = count
        for number in runs:
            if left > 0:
                bits.put(number, ilog(left))
            left -= number
    else:
        bits.put(0, 1).put(int(sparse), 1)
        for length in lengths:
            if sparse:
                bits.put(int(length > 0), 1)
            if length > 0 or not sparse:
                bits.put(length - 1, 5)
    bits.put(lookup, 4)
    if lookup in (1, 2):
        bits.put(0, 32).put(0, 32).put(value_bits - 1, 4).put(0, 1)
        values = table if table is not None else media._lookup1_values(count, dimensions) if lookup == 1 \
            else count * dimensions
        for number in range(values):
            bits.put(number % (1 << value_bits), value_bits)
    return bits


def vq_book(**changes) -> Bits:
    """A four-entry book of two dimensions with a value table (the lookup type 1 reads two multiplicands)."""
    return codebook(**{"lengths": (2, 2, 2, 2), "dimensions": 2, "lookup": 1, **changes})


def floor1(*, partitions: tuple[int, ...] = (0,), classes: tuple[tuple[int, int, int, tuple[int, ...]], ...] = ((1, 0, 0, (1,)),),
           multiplier: int = 2, range_bits: int = 6, x: tuple[int, ...] = (32,)) -> Bits:
    """A floor 1: each class is (dimensions, subclass bits, master book, subclass books plus one)."""
    bits = Bits().put(1, 16).put(len(partitions), 5)
    for number in partitions:
        bits.put(number, 4)
    for dimensions, subclasses, master, books in classes:
        bits.put(dimensions - 1, 3).put(subclasses, 2)
        if subclasses:
            bits.put(master, 8)
        for book in books:
            bits.put(book, 8)
    bits.put(multiplier - 1, 2).put(range_bits, 4)
    for value in x:
        bits.put(value, range_bits)
    return bits


def floor0(*, order: int = 8, rate: int = 44100, bark: int = 128, books: tuple[int, ...] = (1,), kind: int = 0) -> Bits:
    bits = Bits().put(kind, 16).put(order, 8).put(rate, 16).put(bark, 16).put(6, 6).put(8, 8).put(len(books) - 1, 4)
    for book in books:
        bits.put(book, 8)
    return bits


def residue(*, kind: int = 1, begin: int = 0, end: int = 128, classbook: int = 0, cascades: tuple[int, ...] = (1,),
            books: tuple[int, ...] = (1,)) -> Bits:
    """A residue; each cascade is the class's stage mask (its low three bits, then five more behind a flag), and books
    lists the book of every stage bit set, class by class."""
    bits = Bits().put(kind, 16).put(begin, 24).put(end, 24).put(15, 24).put(len(cascades) - 1, 6).put(classbook, 8)
    for cascade in cascades:
        bits.put(cascade & 7, 3).put(int(cascade >> 3 > 0), 1)
        if cascade >> 3:
            bits.put(cascade >> 3, 5)
    for book in books:
        bits.put(book, 8)
    return bits


def mapping(channels: int = 1, *, kind: int = 0, submaps: int = 1, coupling: tuple[tuple[int, int], ...] = (),
            reserved: int = 0, mux: tuple[int, ...] | None = None, floors: tuple[int, ...] = (0,),
            residues: tuple[int, ...] = (0,)) -> Bits:
    bits = Bits().put(kind, 16).put(int(submaps > 1), 1)
    if submaps > 1:
        bits.put(submaps - 1, 4)
    bits.put(int(bool(coupling)), 1)
    if coupling:
        bits.put(len(coupling) - 1, 8)
        for magnitude, angle in coupling:
            bits.put(magnitude, ilog(channels - 1)).put(angle, ilog(channels - 1))
    bits.put(reserved, 2)
    if submaps > 1:
        for channel in range(channels):
            bits.put((mux or tuple(range(channels)))[channel], 4)
    for floor, residue_number in zip(floors, residues):
        bits.put(0, 8).put(floor, 8).put(residue_number, 8)
    return bits


def mode(*, block: int = 0, window: int = 0, transform: int = 0, mapping_number: int = 0) -> Bits:
    return Bits().put(block, 1).put(window, 16).put(transform, 16).put(mapping_number, 8)


def setup_header(channels: int = 1, *, books=None, times: tuple[int, ...] = (0,), floors=None, residues=None,
                 mappings=None, modes=None, framing: int = 1, tail: bytes = b"") -> bytes:
    """A valid setup header for the given channels (a scalar book and a vector book, one floor 1, one residue, one
    mapping, one mode), or the given parts in its place."""
    books = books if books is not None else [codebook(), vq_book()]
    floors = floors if floors is not None else [floor1()]
    residues = residues if residues is not None else [residue()]
    mappings = mappings if mappings is not None else [mapping(channels, coupling=((0, 1),) if channels > 1 else ())]
    modes = modes if modes is not None else [mode()]
    bits = Bits().put(len(books) - 1, 8)
    for part in books:
        bits.add(part)
    bits.put(len(times) - 1, 6)
    for kind in times:
        bits.put(kind, 16)
    for group in (floors, residues, mappings, modes):
        bits.put(len(group) - 1, 6)
        for part in group:
            bits.add(part)
    return b"\x05vorbis" + bits.put(framing, 1).data() + tail


def ogg_file(audio: list[bytes] | None = None, granule: int = 4410) -> bytes:
    audio = audio if audio is not None else [b"\x00" * 300, b"\x01" * 40]
    return (page(2, 0, 0, [identification()]) + page(0, 0, 1, [comment(), setup_header()])
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
        self.assertEqual(walk.facts["blockSizes"], [256, 2048])
        self.assertEqual({key: walk.facts[key] for key in ("codebooks", "floors", "residues", "mappings", "modes")},
                         {"codebooks": 2, "floors": 1, "residues": 1, "mappings": 1, "modes": 1})
        kinds = {part: kind for _start, _length, kind, part in walk.spans}
        self.assertEqual(kinds["ogg/audio-packets"], media.OPAQUE)
        self.assertEqual(kinds["ogg/vorbis-headers"], media.DECODED)

    def test_a_packet_spanning_pages_is_followed(self):
        long = b"\x02" * 600
        data = (page(2, 0, 0, [identification()]) + page(0, 0, 1, [comment(), setup_header()])
                + page(0, -1, 2, [long[:510]], continued_last=True) + page(5, 99, 3, [long[510:]]))
        self.assertEqual(media.walk_ogg(data).facts["audioPackets"], 1)

    def test_a_setup_header_that_is_not_a_setup_is_refused_and_so_is_the_stream(self):
        # A setup header that is its magic and then bytes no codebook reads as one was once counted as decoded.
        noise = b"\x05vorbis" + bytes((index * 37 + 11) % 256 for index in range(3000))
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(), comment(), noise]), "codebook sync pattern missing")
        # A setup header whose packet is cut short, and one with a byte past its framing bit.
        good = setup_header()
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(), comment(), good[:-1]]),
                "setup header ends inside a field")
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(), comment(), good + b"\x00"]),
                "setup header holds bytes after its framing bit")
        # A stereo stream's setup couples its channels; read as a mono stream's, the same bytes name a channel that is
        # not there.
        stereo = page(6, 0, 0, [identification(channels=2), comment(), setup_header(2)])
        self.assertEqual(media.walk_ogg(stereo).facts["channels"], 2)
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(channels=1), comment(), setup_header(2)]),
                "mapping couples a channel that does not exist or with itself")

    def test_block_sizes_are_64_to_8192_and_the_first_is_not_the_larger(self):
        for blocks, wanted in ((0x66, [64, 64]), (0xDD, [8192, 8192]), (0xB8, [256, 2048])):
            walk = media.walk_ogg(page(6, 0, 0, [identification(blocks=blocks), comment(), setup_header()]))
            self.assertEqual(walk.facts["blockSizes"], wanted)
        for blocks in (0xB5, 0xE8, 0x8B, 0x00):
            refusal(self, media.walk_ogg, page(6, 0, 0, [identification(blocks=blocks), comment(), setup_header()]),
                    "Vorbis block sizes out of range")

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
        # The strings are UTF-8: the vendor's, and each comment's.
        vendor = b"\x03vorbis" + struct.pack("<I", 2) + b"\xff\xfe" + struct.pack("<I", 0) + b"\x01"
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(), vendor, setup_header()]),
                "Vorbis comment header holds text that is not UTF-8")
        text = b"\x03vorbis" + struct.pack("<I", 0) + struct.pack("<II", 1, 2) + b"\xc3\x28" + b"\x01"
        refusal(self, media.walk_ogg, page(6, 0, 0, [identification(), text, setup_header()]),
                "Vorbis comment header holds text that is not UTF-8")
        multibyte = b"\x03vorbis" + struct.pack("<I", 3) + "é!".encode() + struct.pack("<II", 1, 4) + "a=\u00e9".encode() + b"\x01"
        self.assertEqual(media.walk_ogg(page(6, 0, 0, [identification(), multibyte, setup_header()])).facts["comments"], 1)


class VorbisSetupTests(unittest.TestCase):
    """The setup header is read field by field; each rule the Vorbis specification calls an error is refused."""

    def refuses(self, packet: bytes, reason: str, channels: int = 1) -> None:
        refusal(self, lambda data: media.read_vorbis_setup(data, channels), packet, reason)

    def test_a_setup_header_is_read_to_its_framing_bit(self):
        counts = {"codebooks": 2, "floors": 1, "residues": 1, "mappings": 1, "modes": 1}
        self.assertEqual(media.read_vorbis_setup(setup_header(), 1), counts)
        self.assertEqual(media.read_vorbis_setup(setup_header(2), 2), counts)

    def test_every_construct_the_specification_has_is_read(self):
        ordered = codebook(runs=(1, 1, 2))  # four entries of 1, 2, 3 and 3 bits: a full tree
        sparse = codebook(lengths=(1, 0, 2, 0, 2), sparse=True)  # three used entries of 1, 2 and 2 bits
        explicit = codebook(lengths=(2, 2, 2, 2), dimensions=2, lookup=2)  # entries x dimensions multiplicands
        single = codebook(lengths=(1,))  # one used entry may leave its tree unfilled, with a one-bit codeword
        nothing = codebook(lengths=(0, 0), sparse=True)  # no used entry
        wide = codebook(lengths=(2, 2, 2, 2), dimensions=40, lookup=1, value_bits=16)  # one value per dimension
        books = [codebook(), vq_book(), ordered, sparse, explicit, single, nothing, wide]
        classes = ((2, 2, 0, (0, 1, 1, 1)), (1, 0, 0, (2,)))  # a master book, four subclass books (none, 1, 1, 1)
        floors = [floor0(books=(1, 4)), floor1(partitions=(0, 0, 1), classes=classes, x=(10, 20, 30, 40, 50))]
        residues = [residue(kind=0), residue(kind=1, cascades=(0b10001, 0b10), books=(1, 1, 4)), residue(kind=2)]
        mappings = [mapping(2, coupling=((0, 1),)),
                    mapping(2, submaps=2, mux=(1, 0), floors=(0, 1), residues=(1, 2))]
        modes = [mode(), mode(block=1, mapping_number=1)]
        facts = media.read_vorbis_setup(setup_header(2, books=books, floors=floors, residues=residues,
                                                      mappings=mappings, modes=modes), 2)
        self.assertEqual(facts, {"codebooks": 8, "floors": 2, "residues": 3, "mappings": 2, "modes": 2})

    def test_floor_1_may_hold_63_values_and_no_more(self):
        classes = ((8, 0, 0, (1,)), (7, 0, 0, (1,)))
        at_limit = floor1(partitions=(0,) * 7 + (1,), classes=classes, range_bits=7, x=tuple(range(1, 64)))
        self.assertEqual(media.read_vorbis_setup(setup_header(floors=[at_limit]), 1)["floors"], 1)
        over = floor1(partitions=(0,) * 8, classes=classes[:1], range_bits=7, x=tuple(range(1, 65)))
        self.refuses(setup_header(floors=[over]), "floor 1 has too many X values")

    def test_the_lookup_values_are_the_greatest_root(self):
        for entries, dimensions, wanted in ((0, 3, 0), (1, 5, 1), (4, 2, 2), (8, 3, 2), (26, 3, 2), (27, 3, 3),
                                            (63, 3, 3), (64, 3, 4), (16777215, 1, 16777215), (100, 65535, 1)):
            self.assertEqual(media._lookup1_values(entries, dimensions), wanted, (entries, dimensions))

    def test_refusals(self):
        self.refuses(b"\x05vorbit" + setup_header()[7:], "third packet is not a Vorbis setup header")
        self.refuses(setup_header()[:20], "setup header ends inside a field")
        self.refuses(setup_header()[:-1], "setup header ends inside a field")
        self.refuses(setup_header(books=[codebook(sync=0x564343), vq_book()]), "codebook sync pattern missing")
        self.refuses(setup_header(books=[codebook(), codebook(dimensions=0, lookup=1, table=0)]),
                     "codebook lookup has no dimensions")
        self.refuses(setup_header(books=[codebook(runs=(5,), entries=4), vq_book()]),
                     "ordered codebook lengths overrun its entries")
        self.refuses(setup_header(books=[codebook(runs=(1, 1), first=32), vq_book()]),
                     "ordered codebook length passes 32 bits")
        self.refuses(setup_header(books=[codebook(lengths=(1, 1, 1)), vq_book()]), "codebook codewords overfill their tree")
        self.refuses(setup_header(books=[codebook(runs=(2, 1), first=1), vq_book()]), "codebook codewords overfill their tree")
        self.refuses(setup_header(books=[codebook(lengths=(1, 2)), vq_book()]), "codebook codewords leave their tree unfilled")
        self.refuses(setup_header(books=[codebook(lengths=(1, 0, 2), sparse=True), vq_book()]),
                     "codebook codewords leave their tree unfilled")
        for single in (codebook(lengths=(2,)), codebook(lengths=(0, 5, 0), sparse=True), codebook(runs=(1,), first=3)):
            self.refuses(setup_header(books=[single, vq_book()]),
                         "codebook with one used entry gives it a longer codeword than one bit")
        self.refuses(setup_header(books=[codebook(lookup=3), vq_book()]), "codebook lookup type is reserved")
        self.refuses(setup_header(times=(0, 1)), "time domain transform type is not zero")
        self.refuses(setup_header(floors=[floor0(kind=2)]), "floor type is reserved")
        for floor in (floor0(order=0), floor0(rate=0), floor0(bark=0)):
            self.refuses(setup_header(floors=[floor]), "floor 0 has a zero order, rate or bark map size")
        for floor in (floor0(books=(0,)), floor0(books=(9,))):  # a book with no lookup, and one that is not there
            self.refuses(setup_header(floors=[floor]), "floor 0 names a codebook that does not give vectors")
        for floor in (floor1(classes=((2, 1, 9, (1, 1)),)), floor1(classes=((1, 0, 0, (9,)),))):
            self.refuses(setup_header(floors=[floor]), "floor 1 names a codebook that does not exist")
        self.refuses(setup_header(floors=[floor1(x=(0,))]), "floor 1 repeats an X value")
        self.refuses(setup_header(floors=[floor1(classes=((2, 0, 0, (1,)),), x=(5, 5))]), "floor 1 repeats an X value")
        self.refuses(setup_header(residues=[residue(kind=3)]), "residue type is reserved")
        self.refuses(setup_header(residues=[residue(begin=10, end=5)]), "residue range runs backwards")
        for residue_part, books in ((residue(classbook=9), None), (residue(), [codebook(dimensions=0), vq_book()])):
            self.refuses(setup_header(residues=[residue_part], **({"books": books} if books else {})),
                         "residue classbook does not exist or has no dimensions")
        # Three classes need three classwords of a one-dimensional classbook with two entries; four classwords fit four.
        three = residue(classbook=0, cascades=(1, 1, 1), books=(1, 1, 1))
        self.refuses(setup_header(books=[codebook(), vq_book()], residues=[three]),
                     "residue classbook has fewer entries than its classes can need")
        exact = residue(classbook=0, cascades=(1, 1), books=(1, 1))
        self.assertEqual(media.read_vorbis_setup(setup_header(books=[codebook(lengths=(2, 2, 2, 2), dimensions=2), vq_book()],
                                                              residues=[exact]), 1)["residues"], 1)
        # Two classes name four classwords of a two-dimensional classbook, which has only two entries; one class names one.
        for classes_count, cascades_count, entries_ok in ((2, 2, False), (1, 1, True)):
            small = codebook(lengths=(1, 1), dimensions=2)
            part = residue(classbook=0, cascades=(1,) * cascades_count, books=(1,) * cascades_count)
            packet = setup_header(books=[small, vq_book()], residues=[part])
            if entries_ok:
                self.assertEqual(media.read_vorbis_setup(packet, 1)["residues"], 1)
            else:
                self.refuses(packet, "residue classbook has fewer entries than its classes can need")
        for residue_part in (residue(books=(0,)), residue(books=(9,))):
            self.refuses(setup_header(residues=[residue_part]), "residue names a codebook that does not give vectors")
        self.refuses(setup_header(mappings=[mapping(kind=1)]), "mapping type is not zero")
        for channels, coupling in ((1, ((0, 0),)), (2, ((1, 1),)), (3, ((0, 3),)), (3, ((3, 1),))):
            self.refuses(setup_header(channels, mappings=[mapping(channels, coupling=coupling)]),
                         "mapping couples a channel that does not exist or with itself", channels)
        self.refuses(setup_header(mappings=[mapping(reserved=1)]), "mapping reserved bits are set")
        self.refuses(setup_header(2, mappings=[mapping(2, submaps=2, mux=(0, 2), floors=(0, 0), residues=(0, 0),
                                                       coupling=((0, 1),))]),
                     "mapping assigns a channel to a submap that does not exist", 2)
        self.refuses(setup_header(mappings=[mapping(floors=(3,))]), "mapping names a floor that does not exist")
        self.refuses(setup_header(mappings=[mapping(residues=(3,))]), "mapping names a residue that does not exist")
        for part in (mode(window=1), mode(transform=1)):
            self.refuses(setup_header(modes=[part]), "mode window or transform type is not zero")
        self.refuses(setup_header(modes=[mode(mapping_number=5)]), "mode names a mapping that does not exist")
        # A reference to the last book, floor, residue or mapping is a reference; one past it is not.
        last = floor1(classes=((1, 1, 1, (1, 2)),))  # a master book 1 and subclass books 0 and 1: the last of two
        self.assertEqual(media.read_vorbis_setup(setup_header(floors=[last]), 1)["floors"], 1)
        for floor in (floor1(classes=((1, 1, 2, (1, 1)),)), floor1(classes=((1, 1, 1, (1, 3)),))):
            self.refuses(setup_header(floors=[floor]), "floor 1 names a codebook that does not exist")
        self.assertEqual(media.read_vorbis_setup(setup_header(floors=[floor1(partitions=(), classes=(), x=())]), 1)["floors"], 1)
        self.assertEqual(media.read_vorbis_setup(setup_header(residues=[residue(begin=64, end=64)]), 1)["residues"], 1)
        two = dict(floors=[floor1(), floor1(x=(20,))], residues=[residue(), residue()])
        self.assertEqual(media.read_vorbis_setup(setup_header(mappings=[mapping(floors=(1,), residues=(1,))], **two), 1)["mappings"], 1)
        self.refuses(setup_header(mappings=[mapping(floors=(2,))], **two), "mapping names a floor that does not exist")
        self.refuses(setup_header(mappings=[mapping(residues=(2,))], **two), "mapping names a residue that does not exist")
        self.refuses(setup_header(mappings=[mapping(floors=(1,))]), "mapping names a floor that does not exist")
        self.refuses(setup_header(mappings=[mapping(residues=(1,))]), "mapping names a residue that does not exist")
        self.assertEqual(media.read_vorbis_setup(setup_header(modes=[mode(mapping_number=0)]), 1)["modes"], 1)
        self.refuses(setup_header(modes=[mode(mapping_number=1)]), "mode names a mapping that does not exist")
        self.refuses(setup_header(framing=0), "setup header lacks its framing bit")
        self.refuses(setup_header(tail=b"\x00"), "setup header holds bytes after its framing bit")

    def test_whether_codewords_fill_a_tree_does_not_depend_on_their_order(self):
        # The assignment takes each entry the lowest free codeword of its length, so a long length before a short one
        # still fits when the lengths sum to one.
        for lengths in ((3, 1, 2, 3), (2, 3, 3, 1), (1, 2, 3, 3), (3, 3, 2, 1)):
            self.assertEqual(media.read_vorbis_setup(setup_header(books=[codebook(lengths=lengths), vq_book()]), 1)["codebooks"], 2)

    def test_an_unordered_book_equals_the_ordered_one_with_the_same_lengths(self):
        for lengths, runs, first in (((1, 2, 3, 3), (1, 1, 2), 1), ((2, 2, 2, 2), (4,), 2),
                                     ((1, 2, 3, 4, 4), (1, 1, 1, 2), 1), ((2, 2, 2, 3, 3), (3, 2), 2)):
            for book in (codebook(lengths=lengths), codebook(runs=runs, first=first)):
                self.assertEqual(media.read_vorbis_setup(setup_header(books=[book, vq_book()]), 1)["codebooks"], 2)
        # Runs that stop short of a full tree, or pass it, are refused as unordered lengths are.
        self.refuses(setup_header(books=[codebook(runs=(1, 1, 1), first=1), vq_book()]),
                     "codebook codewords leave their tree unfilled")


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

    def test_the_audio_track_descriptors_count_only_when_a_decoder_read_the_file(self):
        # No reader here reads a descriptor's words, so their bytes are framed, apart from the header and the index.
        data = bink_file([([b"\x10" * 8, b"\x12" * 2], b"\x20" * 30), ([b"\x11" * 4, b"\x13" * 6], b"\x21" * 50)], tracks=2)
        walk = media.walk_bink(data)
        parts = part_bytes(walk)
        self.assertEqual(parts[("bink/header", media.DECODED)], 44)
        self.assertEqual(parts[("bink/audio-track-descriptors", media.OPAQUE)], 24)
        self.assertEqual(parts[("bink/frame-index", media.DECODED)], 4 * 3)
        self.assertEqual(covered(walk, len(data)), len(data))
        # A file with no audio track has no descriptor to frame.
        self.assertNotIn(("bink/audio-track-descriptors", media.OPAQUE),
                         part_bytes(media.walk_bink(bink_file([([], b"\x20" * 30)], tracks=0))))

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
        self.assertEqual((walk.facts["channels"], walk.facts["transparencyChunk"]), (3, False))
        self.assertEqual(media.walk_png(png_file(colour=6)).facts["channels"], 4)

    def test_a_transparency_chunk_is_noted(self):
        good = png_file()
        data = good.index(b"IDAT") - 4  # tRNS goes before the image data; this is the data chunk's length word
        keyed = good[:data] + png_chunk(b"tRNS", bytes(6)) + good[data:]
        self.assertTrue(media.walk_png(keyed).facts["transparencyChunk"])

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


def jpeg_file(*, frames: int = 1, scan: bytes = b"\x12\x34\xff\x00\x56\xff\xd0\x78", end: bool = True,
              before: bytes = b"", marker: int = 0xC0, count: int = 1, components: bytes = b"\x01\x11\x00",
              header: bytes = b"\x01\x01\x00\x00\x3f\x00") -> bytes:
    """A one-component image: before is put ahead of its frame header; the frame holds count components, and the scan
    header is header."""
    frame = segment(marker, struct.pack(">BHHB", 8, 3, 5, count) + components)
    out = media.JPEG_START[:2] + segment(0xE0, b"JFIF\0\x01\x01\0\0\x01\0\x01\0\0") + before + frame * frames
    out += segment(0xDA, header) + scan
    return out + (bytes((255, 0xD9)) if end else b"")


DC_COUNTS = bytes([0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0])  # the lengths of a standard DC table's 12 codes


def quantization(precision: int = 0, destination: int = 0, element: int = 1) -> bytes:
    return bytes([precision << 4 | destination]) + element.to_bytes(precision + 1, "big") * 64


def huffman(kind: int = 0, destination: int = 0, counts: bytes = DC_COUNTS) -> bytes:
    return bytes([kind << 4 | destination]) + counts + bytes(range(sum(counts)))


class JpegTests(unittest.TestCase):
    def test_markers_and_the_scan_extent(self):
        data = jpeg_file()
        walk = media.walk_jpeg(data)
        self.assertEqual(covered(walk, len(data)), len(data))
        self.assertEqual((walk.facts["width"], walk.facts["height"], walk.facts["scans"]), (5, 3, 1))
        self.assertIn(("jpeg/entropy-coded", media.OPAQUE), {(part, kind) for _s, _l, kind, part in walk.spans})

    def test_the_tables_the_restart_interval_and_the_headers_are_read(self):
        tables = (segment(0xDB, quantization(0, 0) + quantization(1, 3, 300)) + segment(0xC4, huffman(0, 0) + huffman(1, 2))
                  + segment(0xDD, b"\x00\x10"))
        data = jpeg_file(before=tables)
        self.assertEqual(covered(media.walk_jpeg(data), len(data)), len(data))
        # Two components, both in the scan; a progressive frame's scan may select part of the spectrum.
        two = jpeg_file(count=2, components=b"\x01\x22\x00\x02\x11\x01", header=b"\x02\x01\x00\x02\x11\x00\x3f\x00")
        self.assertEqual(media.walk_jpeg(two).facts["components"], 2)
        progressive = jpeg_file(marker=0xC2, header=b"\x01\x01\x00\x01\x05\x10")
        self.assertEqual(media.walk_jpeg(progressive).facts["frameMarker"], 0xC2)

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

    def test_quantization_tables_that_do_not_hold_are_refused(self):
        for body in (quantization(2), quantization(0, 4), quantization()[:-1], quantization() + b"\x00"):
            refusal(self, media.walk_jpeg, jpeg_file(before=segment(0xDB, body)), "quantization table segment is malformed")
        refusal(self, media.walk_jpeg, jpeg_file(before=segment(0xDB, quantization(0, 0, 0))),
                "quantization table holds a zero element")
        zero_high = bytes([0x10]) + (b"\x00\x01" * 63) + b"\x00\x00"
        refusal(self, media.walk_jpeg, jpeg_file(before=segment(0xDB, zero_high)), "quantization table holds a zero element")

    def test_huffman_tables_that_do_not_hold_are_refused(self):
        for body in (huffman(2), huffman(0, 4), bytes([0x00]) + bytes(10), huffman()[:-1], huffman() + b"\x00",
                     bytes([0x00]) + bytes([3] + [0] * 15) + b"\x00\x01"):
            refusal(self, media.walk_jpeg, jpeg_file(before=segment(0xC4, body)), "Huffman table segment is malformed")
        # Two codes of one bit fill the tree; so do four of two bits; the code of all ones is never a symbol's.
        for counts in (bytes([2] + [0] * 15), bytes([0, 4] + [0] * 14), bytes([1, 1, 1, 1] + [0] * 12)[:3] + bytes([5] + [0] * 12)):
            refusal(self, media.walk_jpeg, jpeg_file(before=segment(0xC4, huffman(0, 0, counts))),
                    "Huffman table codes use the all-ones code or overfill their tree")
        # One code short of that is a table.
        self.assertEqual(media.walk_jpeg(jpeg_file(before=segment(0xC4, huffman(0, 0, bytes([1, 1, 0, 1] + [0] * 12))))).facts["scans"], 1)

    def test_a_two_byte_quantization_element_is_zero_only_when_both_bytes_are(self):
        # 1 is stored as 0x0001, whose first byte is zero; 256 as 0x0100, whose second is.
        for element in (1, 256, 65535):
            data = jpeg_file(before=segment(0xDB, quantization(1, 0, element)))
            self.assertEqual(covered(media.walk_jpeg(data), len(data)), len(data))

    def test_a_restart_interval_is_two_bytes(self):
        for body in (b"\x00", b"\x00\x10\x00"):
            refusal(self, media.walk_jpeg, jpeg_file(before=segment(0xDD, body)), "restart interval segment is malformed")

    def test_a_frame_header_lists_its_components_exactly(self):
        for count, components in ((2, b"\x01\x11\x00"), (0, b""), (1, b"\x01\x51\x00"), (1, b"\x01\x10\x00"),
                                  (1, b"\x01\x11\x04"), (2, b"\x01\x11\x00\x01\x11\x00"), (1, b"\x01\x11\x00\x00")):
            refusal(self, media.walk_jpeg, jpeg_file(count=count, components=components),
                    "frame header's component list is malformed")

    def test_a_scan_header_names_the_frame_s_components_and_a_spectrum(self):
        frame_lacks = "scan names a component the frame lacks"
        refusal(self, media.walk_jpeg, media.JPEG_START[:2] + segment(0xDA, b"\x01\x01\x00\x00\x3f\x00") + b"\x12\x34"
                + bytes((255, 0xD9)), "scan before the frame header")
        for header in (b"\x01\x01\x00\x00\x3f", b"\x00\x00\x3f\x00", b"\x05\x01\x00" * 5 + b"\x00\x3f\x00", b"",
                       b"\x01\x01\x40\x00\x3f\x00", b"\x01\x01\x04\x00\x3f\x00", b"\x01\x01\x00\x00\x40\x00",
                       b"\x01\x01\x00\x20\x10\x00", b"\x01\x01\x00\x00\x3f\xe0", b"\x01\x01\x00\x00\x3f\x0e",
                       b"\x01\x01\x00\x00\x3e\x00", b"\x01\x01\x00\x01\x3f\x00"):
            refusal(self, media.walk_jpeg, jpeg_file(header=header), "scan header is malformed")
        five = b"\x05" + b"".join(bytes([number, 0]) for number in range(1, 6)) + b"\x00\x3f\x00"
        refusal(self, media.walk_jpeg, jpeg_file(header=five), "scan header is malformed")
        refusal(self, media.walk_jpeg, jpeg_file(header=b"\x01\x01\x00\x00\x3f\x00\x00"), "scan header is malformed")
        # An extended sequential frame's scan runs the whole spectrum too; a progressive frame's selection is bounded.
        refusal(self, media.walk_jpeg, jpeg_file(marker=0xC1, header=b"\x01\x01\x00\x01\x05\x00"), "scan header is malformed")
        self.assertEqual(media.walk_jpeg(jpeg_file(marker=0xC1)).facts["frameMarker"], 0xC1)
        for header in (b"\x01\x01\x00\x01\x40\x00", b"\x01\x01\x00\x01\x05\xe0", b"\x01\x01\x00\x01\x05\x0e"):
            refusal(self, media.walk_jpeg, jpeg_file(marker=0xC2, header=header), "scan header is malformed")
        self.assertEqual(media.walk_jpeg(jpeg_file(marker=0xC2, header=b"\x01\x01\x00\x00\x3f\xdd")).facts["scans"], 1)
        refusal(self, media.walk_jpeg, jpeg_file(header=b"\x01\x09\x00\x00\x3f\x00"), frame_lacks)
        refusal(self, media.walk_jpeg, jpeg_file(header=b"\x02\x01\x00\x01\x00\x00\x3f\x00"), frame_lacks)
        # The same selection that breaks a sequential frame is a progressive frame's.
        refusal(self, media.walk_jpeg, jpeg_file(header=b"\x01\x01\x00\x01\x05\x10"), "scan header is malformed")
        refusal(self, media.walk_jpeg, jpeg_file(marker=0xC2, header=b"\x01\x01\x00\x06\x05\x00"), "scan header is malformed")


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
def pe_file(*, resource: bool = True, icon_ok: bool = True, symbols: bool = False, bad_icon_group: bool = False,
            icon_bits: int = 8) -> bytes:
    """A minimal PE32: one code section and, optionally, a resource section with a 2 x 2 icon of the given colour depth
    (its palette, colour rows and mask) and its group."""
    file_align = 0x200
    palette = bytes(4 * (1 << icon_bits)) if icon_bits <= 8 else b""
    icon = (struct.pack("<IiiHHIIiiII", 40, 2, 4, 1, icon_bits, 0, 0, 0, 0, 0, 0) + palette
            + bytes((2 * icon_bits + 31) // 32 * 4 * 2) + bytes(4 * 2))
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


def part_bytes(walk: media.Walk) -> dict[tuple[str, str], int]:
    out: dict[tuple[str, str], int] = {}
    for _start, length, kind, part in walk.spans:
        out[(part, kind)] = out.get((part, kind), 0) + length
    return out


class PeTests(unittest.TestCase):
    def test_headers_sections_and_resources(self):
        data = pe_file()
        walk = media.walk_pe(data)
        self.assertEqual(covered(walk, len(data)), len(data))
        types = sorted(r["type"] for r in walk.facts["resources"])
        self.assertEqual(types, ["group-icon", "icon"])
        self.assertTrue(all(r["status"] == "decoded" for r in walk.facts["resources"]))
        icon = next(r for r in walk.facts["resources"] if r["type"] == "icon")
        self.assertEqual((icon["width"], icon["height"], icon["bitCount"]), (2, 2, 8))  # the header's doubled height, halved
        parts = part_bytes(walk)
        self.assertEqual(parts[("pe/section .text", media.OPAQUE)], 0x200)
        # The DOS header, then the PE signature, file and optional headers and two section rows; the rest of the
        # 0x400 header bytes is padding, framed.
        self.assertEqual(parts[("pe/headers", media.DECODED)], 0x40 + 24 + 224 + 2 * 40)
        self.assertEqual(parts[("pe/header-padding", media.OPAQUE)], 0x400 - (0x40 + 24 + 224 + 2 * 40))
        # The tree's five directories and their entries and two data entries are read; the section's padding is not.
        tree = (16 + 8 * 2) + 4 * (16 + 8) + 2 * 16
        self.assertEqual(parts[("pe/resource-tree", media.DECODED)], tree)
        icon_and_group = sum(r["length"] for r in walk.facts["resources"])
        self.assertEqual(parts[("pe/resource-section (not reached by the tree)", media.OPAQUE)],
                         0x200 * 3 - tree - icon_and_group)

    def test_a_dos_stub_and_named_resources(self):
        data = bytearray(pe_file())
        stub = b"stub" * 16
        data[0x40:0x40] = stub  # the PE header moves along; every offset after it does too
        struct.pack_into("<I", data, 0x3C, 0x40 + len(stub))
        moved = len(stub)
        for index in range(2):  # the section rows' file offsets
            at = 0x40 + moved + 24 + 224 + 40 * index + 20
            struct.pack_into("<I", data, at, struct.unpack_from("<I", data, at)[0] + moved)
        struct.pack_into("<I", data, 0x40 + moved + 24 + 60, 0x400 + moved)  # SizeOfHeaders
        rsrc = 0x600 + moved
        name_at = 0x600 - 8  # a name in the resource section's padding: a length of two, then two UTF-16 units
        struct.pack_into("<HH", data, rsrc + 12, 1, 1)
        struct.pack_into("<I", data, rsrc + 16, 0x80000000 | name_at)
        struct.pack_into("<H2s2s", data, rsrc + name_at, 2, b"A\0", b"B\0")
        walk = media.walk_pe(bytes(data))
        parts = part_bytes(walk)
        self.assertEqual(parts[("pe/dos-stub", media.OPAQUE)], moved)
        self.assertEqual(parts[("pe/resource-tree", media.DECODED)], (16 + 8 * 2) + 4 * (16 + 8) + 2 * 16 + 6)
        self.assertEqual(covered(walk, len(data)), len(data))

    def assert_resources_framed(self, walk: media.Walk, types: list[str]) -> None:
        """Every resource is framed, in its status and in the kind of the span that holds its bytes."""
        resources = walk.facts["resources"]
        self.assertEqual(sorted(r["type"] for r in resources), types)
        self.assertTrue(all(r["status"] == "framed" for r in resources))
        parts = part_bytes(walk)
        for resource in resources:
            self.assertEqual(parts.get((f"pe/resource {resource['type']} (framed)", media.OPAQUE)), resource["length"])
        decoded = [part for (part, kind) in parts if kind == media.DECODED and part.startswith("pe/resource ")]
        self.assertEqual(decoded, [])

    def test_a_resource_that_does_not_hold_stays_framed(self):
        self.assert_resources_framed(media.walk_pe(pe_file(icon_ok=False, bad_icon_group=True)), ["group-icon", "icon"])

    def test_resources_other_than_icons_and_icon_groups_stay_framed(self):
        # The fixture's icon image and icon group, retyped as a cursor (whose image would follow a hotspot) and a
        # version resource: bytes that would prove as an icon and a group prove nothing under another type.
        data = bytearray(pe_file())
        rsrc = 0x400 + 0x200
        struct.pack_into("<I", data, rsrc + 16, 1)
        struct.pack_into("<I", data, rsrc + 24, 16)
        self.assert_resources_framed(media.walk_pe(bytes(data)), ["cursor", "version"])

    def test_coff_symbols_are_framed_not_read(self):
        data = pe_file(symbols=True)
        walk = media.walk_pe(data)
        self.assertEqual(covered(walk, len(data)), len(data))
        self.assertEqual(walk.facts["overlayBytes"], 0)
        self.assertEqual(part_bytes(walk)[("pe/coff-symbols", media.OPAQUE)], 18 + 4)

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
        struct.pack_into("<I", bad, 0x58 + 60, 0x100)
        refusal(self, media.walk_pe, bytes(bad), "the section table runs past the headers")
        bad = bytearray(good)
        struct.pack_into("<I", bad, 0x58 + 224 + 20, len(good))
        refusal(self, media.walk_pe, bytes(bad), "a section runs past the file")
        bad = bytearray(good)
        struct.pack_into("<I", bad, 0x58 + 224 + 20, 0x300)  # the code section's bytes inside the headers
        refusal(self, media.walk_pe, bytes(bad), "the file's parts overlap")
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
    data = bytearray(good)
    struct.pack_into("<HH", data, rsrc + 12, 1, 1)
    struct.pack_into("<I", data, rsrc + 16, 0x80000000 | 0x7FFF0)
    edits.append(("resource name runs past its section", bytes(data)))
    data = bytearray(good)
    struct.pack_into("<HH", data, rsrc + 12, 0, 0x7FF)
    edits.append(("resource directory runs past its section", bytes(data)))
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


PAGE = (b'<!DOCTYPE html>\r\n<html xmlns:o="urn:x">\r\n<head><!--[if gte mso 9]><xml><o:x/></xml><![endif]-->'
        b'<style><!-- p {margin:0} a<b --></style></head>\r\n<body lang=EN-GB><p class=MsoNormal>Fish &amp; chips'
        b'&nbsp;&#169;&#xA9;<![if !supportLists]>1.<![endif]><o:p></o:p><br/><img src="a.png" width=10></p>'
        b'<?xml:namespace prefix = o ?>\r\n</body>\r\n</html>\r\n')


class MarkupTests(unittest.TestCase):
    def test_a_page_tokenizes_to_its_end(self):
        walk = media.walk_html(PAGE)
        self.assertEqual(covered(walk, len(PAGE)), len(PAGE))
        self.assertEqual(walk.facts["tags"], 13)  # a style element's end tag is part of its raw text

    def test_byte_soup_is_no_page(self):
        refusal(self, media.walk_html, bytes(v for v in range(32, 256) if v not in b"<&"), "not one html element")
        refusal(self, media.walk_html, bytes(range(32, 256)), "a character reference that does not close")
        refusal(self, media.walk_html, b"<html>" + bytes(v for v in range(32, 256) if v != 38) + b"</html>",
                "markup that is no HTML token")
        refusal(self, media.walk_html, b"plain words, no markup\r\n", "not one html element")
        refusal(self, media.walk_html, b"<html><p>a & b</p></html>", "a character reference that does not close")
        refusal(self, media.walk_html, b"<html><style>p {}</html>", "a script or style element that does not close")
        refusal(self, media.walk_html, b"<html></html> trailing words", "not one html element")
        refusal(self, media.walk_html, b"<body></body>", "not one html element")
        refusal(self, media.walk_html, b"<html><p x=\"1></p></html>", "markup that is no HTML token")

    def test_xml_is_parsed(self):
        data = b'<xml xmlns:o="urn:x">\r\n <o:MainFile HRef="../a.htm"/>\r\n <o:File HRef="b.png"/>\r\n</xml>\r\n'
        self.assertEqual(media.walk_xml(data).facts["elements"], 3)
        refusal(self, media.walk_xml, b"<xml><o:File HRef=b.png></xml>", "not well-formed XML")
        refusal(self, media.walk_xml, bytes(range(32, 256)), "not well-formed XML")


class ReasonsTests(unittest.TestCase):
    def test_every_refusal_reason_is_reached(self):
        """Run last (by name): every FormatError reason the module can give is given by some test above."""
        loader = unittest.TestLoader()
        others = unittest.TestSuite(loader.loadTestsFromTestCase(case) for case in (
            OggTests, VorbisSetupTests, BinkTests, PngTests, JpegTests, TgaTests, PeTests, ActiveMimeTests, TextTests,
            MarkupTests))
        unittest.TextTestRunner(stream=open("/dev/null", "w"), verbosity=0).run(others)
        source = Path(media.__file__).read_text(encoding="utf-8")
        reasons = set(re.findall(r'FormatError\("([^"]+)"\)', source))
        self.assertTrue(reasons)
        self.assertEqual(sorted(reasons - REACHED), [])


if __name__ == "__main__":
    unittest.main()
