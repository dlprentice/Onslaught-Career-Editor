#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Read one member of Battle Engine Aquila's PS2 data package from the player's own PS2 disc image.

The PS2 release keeps its level archives, language tables and other data in one package, DATA0.NYO, in the root
directory of the disc. The package is a 2048-byte RCDF header (the magic, a version word and the index's offset), the
members, and at its end the index: a member count, then one 264-byte row per member (a 256-byte NUL-padded path, the
member's offset in the package and its size). The Europe and USA discs carry the same package byte for byte.

The image is the one the player supplies, read only:

  - a plain ISO, read in place: only the sectors this module needs are read;
  - a Redump-style .zip whose single member is that ISO. The member is inflated as a stream and never written to disk.
    The index sits at the package's end and members lie before it, so reading a member takes two passes over the
    stream: the first stops at the end of the index, the second at the member's last byte.

CHD images are not read.

The module walks ISO9660 (the primary volume descriptor, then the root directory) to DATA0.NYO, reads and checks the
RCDF index, and returns the named member's bytes. Two identities are pinned: the released package's index and level
888's archive. A digest that differs from its pin, or a member without a pin, is a warning; with strict pins it is a
refusal.

The image is untrusted input. Every offset, length and count read from it is checked against what contains it before it
is used (the image, the volume, the root directory, the package, the index, each member), each has a ceiling, and a
malformed image raises Ps2DiscError. Nothing read from the image names a file on this machine: the module reads the
image it is given and returns bytes, and the command line writes a member only to standard output.

    python3 tools/ps2_disc.py list IMAGE                          the package's index as JSON (paths, offsets, sizes)
    python3 tools/ps2_disc.py extract IMAGE [MEMBER] --stdout [--strict-pins]
                                                                  the member's bytes on standard output (default: the
                                                                  level 888 archive); the report goes to standard error
    python3 tools/ps2_disc.py verify IMAGE                        the retail gate: the index and level 888 against their
                                                                  pins, as JSON; exit 0 only when both match
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import struct
import sys
import zipfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path

if __name__ == "__main__":
    sys.dont_write_bytecode = True

SECTOR = 2048
FIRST_DESCRIPTOR_SECTOR = 16
MAX_DESCRIPTORS = 32
MAX_IMAGE_BYTES = 9_000_000_000  # a dual-layer DVD holds 8,547,991,552 bytes
MAX_DIRECTORY_BYTES = 1 << 20
PACKAGE_NAME = "DATA0.NYO"
RCDF_MAGIC = b"RCDF"
RCDF_VERSION = 100
RCDF_HEADER_BYTES = 2048
ROW_BYTES = 264
PATH_BYTES = 256
MAX_ROWS = 16_384
MAX_MEMBER_BYTES = 64 << 20
MAX_STREAM_PASSES = 2
STREAM_CHUNK = 4 << 20

LEVEL_888_MEMBER = "\\data\\Resources\\888_res_PS2.aya"
# The released package's index (count and rows, as read), the same on the Europe and USA discs (onslaught-preservation:
# platforms/console/platform-content-crosswalk.md and formats/lvlr-archive.md).
PACKAGE_INDEX_SHA256 = "25b628b06f4386f97e36bd9041a38910c8238fa1523d0c337b5e8fed51c51bb9"
# Members by folded path (see fold_member_path).
MEMBER_SHA256 = {
    "\\data\\resources\\888_res_ps2.aya": "a3a2f8fcdcbb76ab2ebc9b2a20584b1a2a4b475367c2eca3606269b07eeeea96",
}
LEVEL_888_BYTES = 17_638_345
RELEASED_PACKAGE_ROWS = 383


class Ps2DiscError(ValueError):
    """The image cannot be read as a PS2 disc carrying the package, or a request cannot be met."""


class PinRefused(Ps2DiscError):
    """Strict pins were asked for and a digest is not the pinned one (or has no pin)."""


# Exceptions the zip layer raises for a malformed archive or stream (a nonsensical seek inside one is an OSError);
# each becomes a Ps2DiscError that keeps the original as its cause.
_ZIP_ERRORS = (zipfile.BadZipFile, zipfile.LargeZipFile, zlib.error, EOFError, RuntimeError, NotImplementedError,
               ValueError, struct.error, OverflowError, UnicodeDecodeError, OSError)


@dataclass(frozen=True)
class PackageRow:
    path: str
    offset: int
    size: int


@dataclass(frozen=True)
class Package:
    image_kind: str            # "iso" or "zip"
    image_bytes: int           # the ISO's length (for a zip, its member's declared length)
    volume_bytes: int
    package_sector: int        # DATA0.NYO's first sector in the image
    package_bytes: int
    rcdf_version: int
    index_offset: int          # in the package
    index_sha256: str
    rows: tuple[PackageRow, ...] = field(repr=False)

    def find(self, member: str) -> PackageRow:
        key = fold_member_path(member)
        for row in self.rows:
            if fold_member_path(row.path) == key:
                return row
        raise Ps2DiscError(f"the package has no member {member!r}")


@dataclass(frozen=True)
class Member:
    path: str
    offset: int
    size: int
    sha256: str
    data: bytes = field(repr=False)
    package: Package = field(repr=False)
    passes: int                # passes over the image stream (1 for a plain ISO)
    warnings: tuple[str, ...]


def fold_member_path(path: str) -> str:
    """A package path in one comparable form: backslashes, a leading backslash, any letter case."""

    text = path.replace("/", "\\")
    if not text.startswith("\\"):
        text = "\\" + text
    return text.casefold()


# ----------------------------------------------------------------------------------------------------------- sources
class _IsoSource:
    """A plain ISO file, read in place with bounds checks."""

    kind = "iso"

    def __init__(self, handle):
        self._file = handle
        self.size = os.fstat(handle.fileno()).st_size
        self.passes = 1

    def read(self, offset: int, length: int) -> bytes:
        if offset < 0 or length < 0 or offset + length > self.size:
            raise Ps2DiscError(f"a read of {length} bytes at {offset} passes the end of the image ({self.size})")
        self._file.seek(offset)
        data = self._file.read(length)
        if len(data) != length:
            raise Ps2DiscError("the image ended early")
        return data

    def close(self) -> None:
        self._file.close()


class _ZipSource:
    """The single ISO member of a zip, inflated forward as a stream; an earlier offset starts the next pass."""

    kind = "zip"

    def __init__(self, handle):
        self._handle = handle
        self._zip = None
        self._stream = None
        try:
            self._zip = zipfile.ZipFile(handle)
            members = self._zip.infolist()
            if len(members) != 1:
                raise Ps2DiscError(f"the zip holds {len(members)} members; a disc image zip holds exactly one ISO")
            info = members[0]
            if info.is_dir() or not info.filename.casefold().endswith(".iso"):
                raise Ps2DiscError("the zip's member is not an .iso file")
            if info.flag_bits & 0x1:
                raise Ps2DiscError("the zip's member is encrypted")
            if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                raise Ps2DiscError(f"the zip's member uses compression method {info.compress_type}; "
                                   "only stored and deflated members are read")
            if info.file_size > MAX_IMAGE_BYTES:
                raise Ps2DiscError(f"the zip's member declares {info.file_size} bytes, more than a DVD holds")
            self._info = info
            self.size = info.file_size
            self.passes = 0
            self._open()
        except Ps2DiscError:
            self.close()
            raise
        except _ZIP_ERRORS as error:
            self.close()
            raise Ps2DiscError(f"the zip cannot be read: {error}") from error

    def _open(self) -> None:
        if self._stream is not None:
            self._stream.close()
        if self.passes >= MAX_STREAM_PASSES:
            raise Ps2DiscError("the reads would need another pass over the zip stream")
        self._stream = self._zip.open(self._info)
        self._position = 0
        self.passes += 1

    def _take(self, length: int) -> bytes:
        parts, left = [], length
        while left:
            chunk = self._stream.read(min(left, STREAM_CHUNK))
            if not chunk:
                raise Ps2DiscError("the zip's member ended before its declared length")
            parts.append(chunk)
            left -= len(chunk)
        self._position += length
        return b"".join(parts)

    def read(self, offset: int, length: int) -> bytes:
        if offset < 0 or length < 0 or offset + length > self.size:
            raise Ps2DiscError(f"a read of {length} bytes at {offset} passes the end of the image ({self.size})")
        try:
            if offset < self._position:
                self._open()
            while self._position < offset:
                self._take(min(offset - self._position, STREAM_CHUNK))
            return self._take(length)
        except Ps2DiscError:
            raise
        except _ZIP_ERRORS as error:
            raise Ps2DiscError(f"the zip's member cannot be inflated: {error}") from error

    def close(self) -> None:
        try:
            if self._stream is not None:
                self._stream.close()
                self._stream = None
            if self._zip is not None:
                self._zip.close()
                self._zip = None
        except _ZIP_ERRORS:
            pass
        finally:
            self._handle.close()


def _open_image(image):
    """The image as a source: a zip (by its first local-header signature) or a plain ISO; a CHD is refused. A path that
    is not a regular file is refused before anything is read (opened without blocking, so a named pipe cannot stall
    the reader)."""

    path = Path(image)
    if path.is_dir():
        raise Ps2DiscError(f"the image at {path} is not a regular file")
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
    except FileNotFoundError as error:
        raise Ps2DiscError(f"no image file at {path}") from error
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise Ps2DiscError(f"the image at {path} is not a regular file")
    except BaseException:
        os.close(descriptor)
        raise
    handle = os.fdopen(descriptor, "rb")
    try:
        magic = handle.read(8)
        handle.seek(0)
        if magic == b"MComprHD":
            raise Ps2DiscError("CHD images are not read; supply the plain ISO or the Redump-style zip of it")
        return _ZipSource(handle) if magic[:4] == b"PK\x03\x04" else _IsoSource(handle)
    except BaseException:
        handle.close()
        raise


# ----------------------------------------------------------------------------------------------------------- ISO9660
def _both_u32(data: bytes, at: int, what: str) -> int:
    little, = struct.unpack_from("<I", data, at)
    big, = struct.unpack_from(">I", data, at + 4)
    if little != big:
        raise Ps2DiscError(f"{what}: its two byte orders disagree")
    return little


def _both_u16(data: bytes, at: int, what: str) -> int:
    little, = struct.unpack_from("<H", data, at)
    big, = struct.unpack_from(">H", data, at + 2)
    if little != big:
        raise Ps2DiscError(f"{what}: its two byte orders disagree")
    return little


def _primary_volume(source) -> tuple[bytes, int]:
    """The primary volume descriptor, and the sector of the set terminator that ends the descriptors."""

    primary = None
    for index in range(MAX_DESCRIPTORS):
        sector = FIRST_DESCRIPTOR_SECTOR + index
        if (sector + 1) * SECTOR > source.size:
            raise Ps2DiscError("the image ends inside its volume descriptors")
        descriptor = source.read(sector * SECTOR, SECTOR)
        if descriptor[1:6] != b"CD001":
            raise Ps2DiscError(f"sector {sector} is not an ISO9660 volume descriptor")
        if descriptor[0] == 1 and primary is None:
            if descriptor[6] != 1:
                raise Ps2DiscError("the primary volume descriptor has an unknown version")
            primary = descriptor
        elif descriptor[0] == 255:
            if primary is None:
                raise Ps2DiscError("the volume descriptors end without a primary volume descriptor")
            return primary, sector
    raise Ps2DiscError(f"no descriptor set terminator among the first {MAX_DESCRIPTORS} volume descriptors")


def _directory_records(data: bytes):
    """(name bytes, extent sector, length, flags, interleave words) for each record of a directory's bytes."""

    at = 0
    while at < len(data):
        length = data[at]
        if length == 0:
            at = (at // SECTOR + 1) * SECTOR
            continue
        if length < 34:
            raise Ps2DiscError(f"a directory record at byte {at} is shorter than 34 bytes")
        if at + length > len(data):
            raise Ps2DiscError(f"a directory record at byte {at} runs past the directory's end")
        if at % SECTOR + length > SECTOR:
            raise Ps2DiscError(f"a directory record at byte {at} crosses a sector boundary")
        record = data[at:at + length]
        name_length = record[32]
        if name_length == 0 or 33 + name_length > length:
            raise Ps2DiscError(f"the name of the directory record at byte {at} overruns its record")
        extent = _both_u32(record, 2, "a directory record's extent")
        size = _both_u32(record, 10, "a directory record's length")
        yield record[33:33 + name_length], extent, size, record[25], (record[26], record[27])
        at += length


def _locate_package(source) -> tuple[int, int, int]:
    """(DATA0.NYO's first sector, its length, the volume's length) from the root directory."""

    descriptor, last_descriptor = _primary_volume(source)
    if _both_u16(descriptor, 128, "the logical block size") != SECTOR:
        raise Ps2DiscError("the volume's logical blocks are not 2048 bytes")
    volume_bytes = _both_u32(descriptor, 80, "the volume space size") * SECTOR
    if volume_bytes > source.size or volume_bytes <= last_descriptor * SECTOR:
        raise Ps2DiscError("the volume's declared size does not fit the image")
    root = descriptor[156:190]
    if root[0] != 34 or not root[25] & 0x2:
        raise Ps2DiscError("the primary volume descriptor's root directory record is malformed")
    root_sector = _both_u32(root, 2, "the root directory's extent")
    root_bytes = _both_u32(root, 10, "the root directory's length")
    if root_sector <= last_descriptor:
        raise Ps2DiscError("the root directory lies among the volume descriptors")
    if not 68 <= root_bytes <= MAX_DIRECTORY_BYTES:
        raise Ps2DiscError(f"the root directory's length ({root_bytes}) is implausible")
    if root_sector * SECTOR + root_bytes > volume_bytes:
        raise Ps2DiscError("the root directory passes the end of the volume")
    root_end_sector = root_sector + (root_bytes + SECTOR - 1) // SECTOR
    found = []
    for name, extent, size, flags, interleave in _directory_records(source.read(root_sector * SECTOR, root_bytes)):
        if name in (b"\x00", b"\x01") or flags & 0x2:
            continue
        identifier = name.decode("latin-1").split(";", 1)[0].rstrip(".")
        if identifier.casefold() == PACKAGE_NAME.casefold():
            found.append((extent, size, flags, interleave))
    if not found:
        raise Ps2DiscError(f"the root directory has no {PACKAGE_NAME}; "
                           "this is not a retail Battle Engine Aquila PS2 disc")
    if len(found) > 1:
        raise Ps2DiscError(f"the root directory names {PACKAGE_NAME} more than once")
    extent, size, flags, interleave = found[0]
    if flags & 0x80 or interleave != (0, 0):
        raise Ps2DiscError(f"{PACKAGE_NAME} is recorded in several extents or interleaved; it is read as one extent")
    if extent < root_end_sector:
        raise Ps2DiscError(f"{PACKAGE_NAME} begins before the end of the root directory")
    if extent * SECTOR + size > volume_bytes:
        raise Ps2DiscError(f"{PACKAGE_NAME} passes the end of the volume")
    if size < RCDF_HEADER_BYTES + 4:
        raise Ps2DiscError(f"{PACKAGE_NAME} is shorter than its header and index")
    return extent, size, volume_bytes


# --------------------------------------------------------------------------------------------------------------- RCDF
def _read_index(source, base: int, package_bytes: int) -> tuple[int, int, bytes, tuple[PackageRow, ...]]:
    """(RCDF version, the index's offset, the index's bytes, its rows) for the package at image offset base."""

    magic, version, index_offset = struct.unpack_from("<4sII", source.read(base, 12))
    if magic != RCDF_MAGIC:
        raise Ps2DiscError(f"{PACKAGE_NAME} does not begin with the RCDF magic")
    if version != RCDF_VERSION:
        raise Ps2DiscError(f"{PACKAGE_NAME} is RCDF version {version}; this reader knows version {RCDF_VERSION}")
    if not RCDF_HEADER_BYTES <= index_offset <= package_bytes - 4:
        raise Ps2DiscError("the RCDF index offset lies outside the package")
    span = package_bytes - index_offset - 4
    if span % ROW_BYTES:
        raise Ps2DiscError("the RCDF index does not end at the package's end")
    count = span // ROW_BYTES
    if count > MAX_ROWS:
        raise Ps2DiscError(f"the RCDF index has {count} rows, more than {MAX_ROWS}")
    index = source.read(base + index_offset, 4 + count * ROW_BYTES)
    if struct.unpack_from("<I", index, 0)[0] != count:
        raise Ps2DiscError("the RCDF index's count disagrees with its length")
    rows, seen = [], set()
    for number in range(count):
        row = index[4 + number * ROW_BYTES:4 + (number + 1) * ROW_BYTES]
        raw_path = row[:PATH_BYTES]
        end = raw_path.find(b"\x00")
        if end <= 0:
            raise Ps2DiscError(f"RCDF row {number}: the path is empty or not terminated")
        if raw_path[end:].count(0) != PATH_BYTES - end:
            raise Ps2DiscError(f"RCDF row {number}: bytes follow the path's terminator")
        if any(not 0x20 <= byte <= 0x7E for byte in raw_path[:end]):
            raise Ps2DiscError(f"RCDF row {number}: the path holds a byte that is not printable ASCII")
        path = raw_path[:end].decode("ascii")
        if not path.startswith("\\"):
            raise Ps2DiscError(f"RCDF row {number}: the path does not begin with a backslash")
        offset, size = struct.unpack_from("<II", row, PATH_BYTES)
        if offset < RCDF_HEADER_BYTES or offset + size > index_offset:
            raise Ps2DiscError(f"RCDF row {number}: the member lies outside the package's data")
        key = fold_member_path(path)
        if key in seen:
            raise Ps2DiscError(f"RCDF row {number}: the path repeats an earlier row's")
        seen.add(key)
        rows.append(PackageRow(path, offset, size))
    ordered = sorted(rows, key=lambda r: (r.offset, r.size))
    for earlier, later in zip(ordered, ordered[1:]):
        if earlier.offset + earlier.size > later.offset:
            raise Ps2DiscError("two RCDF rows overlap")
    return version, index_offset, index, tuple(rows)


def _package(source) -> Package:
    sector, package_bytes, volume_bytes = _locate_package(source)
    version, index_offset, index, rows = _read_index(source, sector * SECTOR, package_bytes)
    return Package(source.kind, source.size, volume_bytes, sector, package_bytes, version, index_offset,
                   hashlib.sha256(index).hexdigest(), rows)


def _checked_size(source) -> None:
    if source.size > MAX_IMAGE_BYTES:
        raise Ps2DiscError("the image is larger than a DVD")
    if source.size % SECTOR or source.size < (FIRST_DESCRIPTOR_SECTOR + 2) * SECTOR:
        raise Ps2DiscError("the image's length is not a whole number of 2048-byte sectors beyond the system area")


# --------------------------------------------------------------------------------------------------------------- API
def read_package(image) -> Package:
    """The package's index (rows, digest) from a plain ISO or a disc-image zip. One pass over a zip's stream."""

    source = _open_image(image)
    try:
        _checked_size(source)
        return _package(source)
    finally:
        source.close()


def pin_warnings(package: Package, member: PackageRow | None, member_sha256: str | None) -> list[str]:
    """What differs from the pins: the index, and the member when one was read."""

    warnings = []
    if package.index_sha256 != PACKAGE_INDEX_SHA256:
        warnings.append(f"the package index ({package.index_sha256}) is not the released Europe and USA index "
                        f"({PACKAGE_INDEX_SHA256})")
    if member is not None:
        pin = MEMBER_SHA256.get(fold_member_path(member.path))
        if pin is None:
            warnings.append(f"{member.path} has no pinned digest (it is {member_sha256})")
        elif pin != member_sha256:
            warnings.append(f"{member.path} ({member_sha256}) is not the pinned {pin}")
    return warnings


def read_member(image, member: str = LEVEL_888_MEMBER, *, strict_pins: bool = False) -> Member:
    """One member's bytes from a plain ISO or a disc-image zip, with its digest and the pin warnings.

    strict_pins turns every warning into a PinRefused raised before the bytes are returned."""

    source = _open_image(image)
    try:
        _checked_size(source)
        package = _package(source)
        row = package.find(member)
        if row.size > MAX_MEMBER_BYTES:
            raise Ps2DiscError(f"{row.path} is {row.size} bytes, more than the {MAX_MEMBER_BYTES}-byte ceiling")
        data = source.read(package.package_sector * SECTOR + row.offset, row.size)
        passes = source.passes
    finally:
        source.close()
    digest = hashlib.sha256(data).hexdigest()
    warnings = pin_warnings(package, row, digest)
    if strict_pins and warnings:
        raise PinRefused("; ".join(warnings))
    return Member(row.path, row.offset, row.size, digest, data, package, passes, tuple(warnings))


def gate(image) -> dict:
    """The retail gate: the package index and level 888 against their pins, as a JSON-ready report."""

    found = read_member(image, LEVEL_888_MEMBER)
    package = found.package
    return {
        "format": "onslaught.ps2-disc-gate.v1",
        "imageKind": package.image_kind, "imageBytes": package.image_bytes, "volumeBytes": package.volume_bytes,
        "package": {"sector": package.package_sector, "bytes": package.package_bytes,
                    "rcdfVersion": package.rcdf_version, "indexOffset": package.index_offset,
                    "rows": len(package.rows), "indexSha256": package.index_sha256,
                    "indexPinned": package.index_sha256 == PACKAGE_INDEX_SHA256},
        "member": {"path": found.path, "offset": found.offset, "bytes": found.size, "sha256": found.sha256,
                   "pinned": MEMBER_SHA256.get(fold_member_path(found.path)) == found.sha256},
        "streamPasses": found.passes,
        "warnings": list(found.warnings),
        "pass": not found.warnings,
    }


# ------------------------------------------------------------------------------------------------------ command line
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="the package's index as JSON")
    listing.add_argument("image", type=Path)
    extract = commands.add_parser("extract", help="a member's bytes on standard output")
    extract.add_argument("image", type=Path)
    extract.add_argument("member", nargs="?", default=LEVEL_888_MEMBER)
    extract.add_argument("--stdout", action="store_true",
                         help="required: the member is written only to standard output")
    extract.add_argument("--strict-pins", action="store_true", help="refuse a digest that is not its pin")
    verify = commands.add_parser("verify", help="the retail gate (index and level 888 against their pins)")
    verify.add_argument("image", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            package = read_package(args.image)
            print(json.dumps({
                "format": "onslaught.ps2-disc-index.v1", "imageKind": package.image_kind,
                "imageBytes": package.image_bytes, "packageSector": package.package_sector,
                "packageBytes": package.package_bytes, "rcdfVersion": package.rcdf_version,
                "indexOffset": package.index_offset, "indexSha256": package.index_sha256,
                "indexPinned": package.index_sha256 == PACKAGE_INDEX_SHA256,
                "rows": [{"path": r.path, "offset": r.offset, "bytes": r.size} for r in package.rows]}, indent=1))
            return 0
        if args.command == "extract":
            if not args.stdout:
                parser.error("choose --stdout explicitly; this tool writes no files")
            if sys.stdout.isatty():
                parser.error("standard output is a terminal; redirect it to the file that should hold the member")
            found = read_member(args.image, args.member, strict_pins=args.strict_pins)
            sys.stdout.buffer.write(found.data)
            sys.stdout.buffer.flush()
            print(json.dumps({"member": found.path, "bytes": found.size, "sha256": found.sha256,
                              "indexSha256": found.package.index_sha256, "streamPasses": found.passes,
                              "warnings": list(found.warnings)}, indent=1), file=sys.stderr)
            return 0
        report = gate(args.image)
        print(json.dumps(report, indent=1))
        return 0 if report["pass"] else 1
    except Ps2DiscError as error:
        print(f"ps2_disc: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
