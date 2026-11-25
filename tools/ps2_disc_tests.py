#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks the PS2 disc reader on authored ISO9660 images and zips built here (no game bytes): a member comes back from a
plain ISO and from a zip of it (stored or deflated, in two stream passes, writing nothing), pins warn or refuse, every
malformed structure and every mutation of an authored image or zip is refused with Ps2DiscError and nothing else, and
the command line writes a member only to standard output.

The retail gate runs only when BEA_PS2_IMAGE names the player's own image (a plain ISO or a Redump-style zip of one):

    BEA_PS2_IMAGE=/path/to/image python3 tools/ps2_disc_tests.py
"""
from __future__ import annotations

import builtins
import contextlib
import hashlib
import io
import json
import os
import random
import struct
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import ps2_disc as disc

SECTOR = disc.SECTOR
TARGET = "\\data\\Resources\\888_res_PS2.aya"


def both32(value: int) -> bytes:
    return struct.pack("<I", value) + struct.pack(">I", value)


def both16(value: int) -> bytes:
    return struct.pack("<H", value) + struct.pack(">H", value)


def record(name: bytes, extent: int, size: int, flags: int = 0, unit: int = 0, gap: int = 0) -> bytes:
    """One ISO9660 directory record (padded to an even length)."""

    length = 33 + len(name) + (1 - len(name) % 2)
    out = bytearray(length)
    out[0] = length
    out[2:10] = both32(extent)
    out[10:18] = both32(size)
    out[18:25] = bytes((103, 1, 1, 0, 0, 0, 0))
    out[25], out[26], out[27] = flags, unit, gap
    out[28:32] = both16(1)
    out[32] = len(name)
    out[33:33 + len(name)] = name
    return bytes(out)


def filler(seed: int, size: int) -> bytes:
    return random.Random(seed).randbytes(size)


def package(members: list[tuple[str, bytes]], version: int = 100) -> bytes:
    """An authored RCDF package: a 2048-byte header, sector-aligned members, then the count and 264-byte rows."""

    body = bytearray(disc.RCDF_HEADER_BYTES)
    rows = []
    for path, data in members:
        rows.append((path, len(body), len(data)))
        body += data + bytes(-len(data) % SECTOR)
    index = struct.pack("<I", len(rows)) + b"".join(
        path.encode("ascii").ljust(disc.PATH_BYTES, b"\0") + struct.pack("<II", offset, size)
        for path, offset, size in rows)
    body[0:12] = disc.RCDF_MAGIC + struct.pack("<II", version, len(body))
    return bytes(body) + index


def members() -> list[tuple[str, bytes]]:
    return [("\\ps2data\\sounds1.bin", filler(1, 5000)),
            (TARGET, b"LVLR" + filler(2, 9000)),
            ("\\data\\language\\english.dat", filler(3, 777)),
            ("\\data\\Default Physics.dat", filler(4, 2048))]


class Image:
    """An authored disc image, with the positions the hostile tests corrupt. Supplementary descriptors (when asked for)
    come before the primary one, so the reader has to pass over them."""

    def __init__(self, files: list[tuple[bytes, bytes]] | None = None, *, extra_descriptors: int = 0,
                 extra_records: list[bytes] = ()):
        self.package = package(members())
        if files is None:
            files = [(b"SYSTEM.CNF;1", b"BOOT2 = cdrom0:\\SLUS_000.00;1\r\n"), (b"SLUS_000.00;1", filler(5, 3000)),
                     (b"DATA1.NYO;1", filler(6, 6000)), (b"DATA0.NYO;1", self.package)]
        self.pvd_sector = disc.FIRST_DESCRIPTOR_SECTOR + extra_descriptors
        self.terminator = self.pvd_sector + 1
        self.root_sector = self.terminator + 1
        directory = record(b"\x00", self.root_sector, 0, 2) + record(b"\x01", self.root_sector, 0, 2)
        directory += b"".join(extra_records)
        names = [name for name, _ in files]
        file_records_at = []
        for name in names:
            file_records_at.append(len(directory))
            directory += record(name, 0, 0)
        self.root_bytes = len(directory)
        sector = self.root_sector + (self.root_bytes + SECTOR - 1) // SECTOR
        placed = []
        for (name, data), at in zip(files, file_records_at):
            placed.append((name, sector, data))
            directory = directory[:at] + record(name, sector, len(data)) + directory[at + len(record(name, 0, 0)):]
            sector += (len(data) + SECTOR - 1) // SECTOR
        self.records = dict(zip(names, file_records_at))
        self.sectors = sector
        image = bytearray(self.sectors * SECTOR)
        for n in range(extra_descriptors):
            image[(disc.FIRST_DESCRIPTOR_SECTOR + n) * SECTOR:(disc.FIRST_DESCRIPTOR_SECTOR + n) * SECTOR + 7] = \
                b"\x02CD001\x01"
        pvd = bytearray(SECTOR)
        pvd[0:7] = b"\x01CD001\x01"
        pvd[80:88] = both32(self.sectors)
        pvd[128:132] = both16(SECTOR)
        pvd[156:190] = record(b"\x00", self.root_sector, self.root_bytes, 2)
        self.pvd = self.pvd_sector * SECTOR
        image[self.pvd:self.pvd + SECTOR] = pvd
        image[self.terminator * SECTOR:self.terminator * SECTOR + 7] = b"\xffCD001\x01"
        image[self.root_sector * SECTOR:self.root_sector * SECTOR + len(directory)] = directory
        for name, start, data in placed:
            image[start * SECTOR:start * SECTOR + len(data)] = data
        self.placed = {name: (start, data) for name, start, data in placed}
        self.bytes = image

    @property
    def package_base(self) -> int:
        return self.placed[b"DATA0.NYO;1"][0] * SECTOR

    def record_at(self, name: bytes) -> int:
        return self.root_sector * SECTOR + self.records[name]

    def index_base(self) -> int:
        return self.package_base + struct.unpack_from("<I", self.package, 8)[0]

    def row_at(self, number: int) -> int:
        return self.index_base() + 4 + number * disc.ROW_BYTES


class Workspace(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write(self, data: bytes, name: str = "image.iso") -> Path:
        path = self.dir / name
        path.write_bytes(bytes(data))
        return path

    def zipped(self, data: bytes, name: str = "image.zip", method: int = zipfile.ZIP_DEFLATED,
               member: str = "Battle Engine Aquila (Test).iso") -> Path:
        path = self.dir / name
        with zipfile.ZipFile(path, "w", compression=method) as archive:
            archive.writestr(member, bytes(data))
        return path

    def refused(self, path: Path, fragment: str, member: str = TARGET) -> None:
        with self.assertRaises(disc.Ps2DiscError) as caught:
            disc.read_member(path, member)
        self.assertIn(fragment, str(caught.exception))


class ReadTests(Workspace):
    def test_a_plain_iso_returns_the_member_in_one_pass(self) -> None:
        image = Image()
        found = disc.read_member(self.write(image.bytes))
        expected = dict(members())[TARGET]
        self.assertEqual(expected, found.data)
        self.assertEqual(hashlib.sha256(expected).hexdigest(), found.sha256)
        self.assertEqual((TARGET, len(expected), 1), (found.path, found.size, found.passes))
        self.assertEqual("iso", found.package.image_kind)
        index = image.package[struct.unpack_from("<I", image.package, 8)[0]:]
        self.assertEqual(hashlib.sha256(index).hexdigest(), found.package.index_sha256)
        self.assertEqual([path for path, _ in members()], [row.path for row in found.package.rows])

    def test_a_zip_returns_the_same_member_in_two_stream_passes(self) -> None:
        image = Image()
        plain = disc.read_member(self.write(image.bytes))
        for method in (zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED):
            with self.subTest(method=method):
                found = disc.read_member(self.zipped(image.bytes, f"image{method}.zip", method))
                self.assertEqual((plain.data, plain.package.index_sha256), (found.data, found.package.index_sha256))
                self.assertEqual(("zip", 2), (found.package.image_kind, found.passes))

    def test_the_package_may_come_first_and_extra_descriptors_are_passed_over(self) -> None:
        image = Image([(b"DATA0.NYO;1", package(members())), (b"SLES_000.00;1", filler(7, 4000))], extra_descriptors=2)
        for path in (self.write(image.bytes), self.zipped(image.bytes)):
            with self.subTest(path=path.name):
                self.assertEqual(dict(members())[TARGET], disc.read_member(path).data)

    def test_member_names_match_in_any_case_and_with_either_separator(self) -> None:
        path = self.write(Image().bytes)
        for name in ("data/resources/888_RES_ps2.aya", "\\DATA\\RESOURCES\\888_res_PS2.AYA"):
            self.assertEqual(TARGET, disc.read_member(path, name).path)

    def test_a_missing_member_is_refused(self) -> None:
        self.refused(self.write(Image().bytes), "has no member", "\\data\\Resources\\999_res_PS2.aya")

    def test_the_index_listing_reads_one_pass_of_a_zip(self) -> None:
        listed = disc.read_package(self.zipped(Image().bytes))
        self.assertEqual(("zip", 4), (listed.image_kind, len(listed.rows)))

    def test_a_zip_is_read_as_a_stream_and_nothing_is_written(self) -> None:
        path = self.zipped(Image().bytes)
        real_open, real_os_open = builtins.open, os.open
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC

        def guarded_open(file, mode="r", *args, **kwargs):
            if any(flag in mode for flag in "wax+"):
                raise AssertionError(f"opened {file} for writing")
            return real_open(file, mode, *args, **kwargs)

        def guarded_os_open(file, flags, *args, **kwargs):
            if flags & write_flags:
                raise AssertionError(f"opened {file} for writing")
            return real_os_open(file, flags, *args, **kwargs)

        with mock.patch.object(builtins, "open", guarded_open), mock.patch.object(os, "open", guarded_os_open), \
                mock.patch.object(tempfile, "mkstemp", side_effect=AssertionError("temporary file")), \
                mock.patch.object(tempfile, "TemporaryFile", side_effect=AssertionError("temporary file")):
            self.assertEqual(dict(members())[TARGET], disc.read_member(path).data)


class PinTests(Workspace):
    def authored_pins(self, image: Image):
        index = image.package[struct.unpack_from("<I", image.package, 8)[0]:]
        return mock.patch.multiple(
            disc, PACKAGE_INDEX_SHA256=hashlib.sha256(index).hexdigest(),
            MEMBER_SHA256={disc.fold_member_path(TARGET): hashlib.sha256(dict(members())[TARGET]).hexdigest()})

    def test_unpinned_digests_are_warnings_by_default_and_refusals_when_strict(self) -> None:
        path = self.write(Image().bytes)
        found = disc.read_member(path)
        self.assertEqual(2, len(found.warnings))
        self.assertIn("is not the released Europe and USA index", found.warnings[0])
        self.assertIn("is not the pinned", found.warnings[1])
        with self.assertRaises(disc.PinRefused):
            disc.read_member(path, strict_pins=True)

    def test_matching_pins_pass_strictly_and_the_gate_passes(self) -> None:
        image = Image()
        with self.authored_pins(image):
            for path in (self.write(image.bytes), self.zipped(image.bytes)):
                with self.subTest(path=path.name):
                    self.assertEqual((), disc.read_member(path, strict_pins=True).warnings)
                    report = disc.gate(path)
                    self.assertTrue(report["pass"])
                    self.assertTrue(report["package"]["indexPinned"] and report["member"]["pinned"])

    def test_a_pinned_member_with_other_bytes_is_refused_when_strict(self) -> None:
        image = Image()
        index = image.package[struct.unpack_from("<I", image.package, 8)[0]:]
        with mock.patch.multiple(disc, PACKAGE_INDEX_SHA256=hashlib.sha256(index).hexdigest(),
                                 MEMBER_SHA256={disc.fold_member_path(TARGET): hashlib.sha256(b"other").hexdigest()}):
            path = self.write(image.bytes)
            self.assertEqual(1, len(disc.read_member(path).warnings))
            with self.assertRaises(disc.PinRefused) as caught:
                disc.read_member(path, strict_pins=True)
            self.assertIn(TARGET, str(caught.exception))
            self.assertFalse(disc.gate(path)["pass"])

    def test_a_member_without_a_pin_is_a_warning_and_a_strict_refusal(self) -> None:
        image = Image()
        with self.authored_pins(image):
            path = self.write(image.bytes)
            found = disc.read_member(path, "\\ps2data\\sounds1.bin")
            self.assertEqual(1, len(found.warnings))
            self.assertIn("has no pinned digest", found.warnings[0])
            with self.assertRaises(disc.PinRefused):
                disc.read_member(path, "\\ps2data\\sounds1.bin", strict_pins=True)


def patched(data: bytearray, at: int, value: bytes) -> bytearray:
    out = bytearray(data)
    out[at:at + len(value)] = value
    return out


class HostileImageTests(Workspace):
    def test_files_that_are_not_regular_images_are_refused_without_reading(self) -> None:
        self.refused(self.dir / "absent.iso", "no image file")
        self.refused(self.dir, "not a regular file")
        if hasattr(os, "mkfifo"):
            fifo = self.dir / "pipe.iso"
            os.mkfifo(fifo)
            self.refused(fifo, "not a regular file")

    def test_a_chd_is_refused_by_name(self) -> None:
        self.refused(self.write(b"MComprHD" + bytes(40 * SECTOR - 8), "image.chd"), "CHD images are not read")

    def test_image_lengths(self) -> None:
        image = Image()
        self.refused(self.write(image.bytes[:17 * SECTOR]), "not a whole number")
        self.refused(self.write(image.bytes + b"\0"), "not a whole number")
        with mock.patch.object(disc, "MAX_IMAGE_BYTES", len(image.bytes) - SECTOR):
            self.refused(self.write(image.bytes), "larger than a DVD")

    def test_volume_descriptors(self) -> None:
        image = Image()
        self.refused(self.write(patched(image.bytes, image.pvd + 1, b"CD002")), "not an ISO9660 volume descriptor")
        self.refused(self.write(patched(image.bytes, image.pvd, b"\xff")), "without a primary volume descriptor")
        self.refused(self.write(patched(image.bytes, image.pvd + 6, b"\x02")), "unknown version")
        self.refused(self.write(patched(image.bytes, image.pvd + 128, both16(4096))), "not 2048 bytes")
        self.refused(self.write(patched(image.bytes, image.pvd + 80, struct.pack("<I", 7))), "byte orders disagree")
        self.refused(self.write(patched(image.bytes, image.pvd + 80, both32(image.sectors + 1))), "does not fit")
        many = Image(extra_descriptors=disc.MAX_DESCRIPTORS)
        self.refused(self.write(many.bytes), "no descriptor set terminator among")

    def test_root_directory(self) -> None:
        image = Image()
        root = image.pvd + 156
        self.refused(self.write(patched(image.bytes, root + 25, b"\x00")), "root directory record is malformed")
        self.refused(self.write(patched(image.bytes, root + 2, both32(image.terminator))),
                     "among the volume descriptors")
        self.refused(self.write(patched(image.bytes, root + 10, both32(disc.MAX_DIRECTORY_BYTES + 1))), "implausible")
        self.refused(self.write(patched(image.bytes, root + 2, both32(image.sectors))), "end of the volume")

    def test_directory_records(self) -> None:
        image = Image()
        at = image.record_at(b"DATA0.NYO;1")
        self.refused(self.write(patched(image.bytes, at, b"\x20")), "shorter than 34 bytes")
        self.refused(self.write(patched(image.bytes, at + 32, b"\xf0")), "overruns its record")
        self.refused(self.write(patched(image.bytes, at + 2, struct.pack("<I", 1))), "byte orders disagree")
        last = image.record_at(b"DATA0.NYO;1")
        self.refused(self.write(patched(image.bytes, last, bytes([255]))), "runs past the directory's end")
        # Forty-two 46-byte records after the two dot records end at byte 2000; SYSTEM.CNF's record then ends at
        # 2046 and the next one would cross into the root directory's second sector.
        crossing = Image(extra_records=[record(b"PAD%03d.BIN;1" % n, 0, 0) for n in range(42)])
        self.assertGreater(crossing.root_bytes, SECTOR)
        self.refused(self.write(crossing.bytes), "crosses a sector boundary")

    def test_the_package_entry(self) -> None:
        image = Image()
        at = image.record_at(b"DATA0.NYO;1")
        self.refused(self.write(patched(image.bytes, at + 33, b"DATA9")), "has no DATA0.NYO")
        self.refused(self.write(patched(image.bytes, image.record_at(b"DATA1.NYO;1") + 33, b"DATA0")),
                     "more than once")
        self.refused(self.write(patched(image.bytes, at + 25, b"\x80")), "several extents or interleaved")
        self.refused(self.write(patched(image.bytes, at + 26, b"\x01")), "several extents or interleaved")
        self.refused(self.write(patched(image.bytes, at + 2, both32(image.root_sector))), "before the end of the root")
        self.refused(self.write(patched(image.bytes, at + 10, both32(len(image.package) + 10 * SECTOR))),
                     "passes the end of the volume")
        self.refused(self.write(patched(image.bytes, at + 10, both32(100))), "shorter than its header and index")

    def test_the_rcdf_header_and_index(self) -> None:
        image = Image()
        base = image.package_base
        self.refused(self.write(patched(image.bytes, base, b"RCDE")), "RCDF magic")
        self.refused(self.write(patched(image.bytes, base + 4, struct.pack("<I", 101))), "RCDF version 101")
        self.refused(self.write(patched(image.bytes, base + 8, struct.pack("<I", 16))), "index offset lies outside")
        self.refused(self.write(patched(image.bytes, base + 8, struct.pack("<I", len(image.package) + 4))),
                     "index offset lies outside")
        self.refused(self.write(patched(image.bytes, base + 8, struct.pack("<I", image.index_base() - base + 1))),
                     "does not end at the package's end")
        self.refused(self.write(patched(image.bytes, image.index_base(), struct.pack("<I", 9))), "count disagrees")
        with mock.patch.object(disc, "MAX_ROWS", 3):
            self.refused(self.write(image.bytes), "more than 3")

    def test_index_rows(self) -> None:
        image = Image()
        row = image.row_at(1)
        self.refused(self.write(patched(image.bytes, row, bytes(disc.PATH_BYTES))), "empty or not terminated")
        self.refused(self.write(patched(image.bytes, row, b"x" * disc.PATH_BYTES)), "empty or not terminated")
        self.refused(self.write(patched(image.bytes, row + 200, b"junk")), "follow the path's terminator")
        self.refused(self.write(patched(image.bytes, row + 1, b"\x07")), "not printable ASCII")
        self.refused(self.write(patched(image.bytes, row, b"d")), "does not begin with a backslash")
        self.refused(self.write(patched(image.bytes, row + disc.PATH_BYTES, struct.pack("<I", 100))),
                     "outside the package's data")
        self.refused(self.write(patched(image.bytes, row + disc.PATH_BYTES + 4, struct.pack("<I", 1 << 30))),
                     "outside the package's data")
        first_offset = struct.unpack_from("<I", image.bytes, image.row_at(0) + disc.PATH_BYTES)[0]
        self.refused(self.write(patched(image.bytes, row + disc.PATH_BYTES, struct.pack("<I", first_offset))),
                     "two RCDF rows overlap")
        duplicate = b"\\PS2DATA\\SOUNDS1.BIN".ljust(disc.PATH_BYTES, b"\0")
        self.refused(self.write(patched(image.bytes, row, duplicate)), "repeats an earlier row's")

    def test_member_ceiling(self) -> None:
        with mock.patch.object(disc, "MAX_MEMBER_BYTES", 100):
            self.refused(self.write(Image().bytes), "more than the 100-byte ceiling")


class HostileZipTests(Workspace):
    def test_the_zip_must_hold_exactly_one_readable_iso(self) -> None:
        image = Image()
        two = self.dir / "two.zip"
        with zipfile.ZipFile(two, "w") as archive:
            archive.writestr("a.iso", bytes(image.bytes))
            archive.writestr("b.iso", b"")
        self.refused(two, "holds 2 members")
        self.refused(self.zipped(image.bytes, "named.zip", member="disc.bin"), "not an .iso file")
        if hasattr(zipfile, "ZIP_BZIP2"):
            self.refused(self.zipped(image.bytes, "bz.zip", zipfile.ZIP_BZIP2), "compression method 12")
        with mock.patch.object(disc, "MAX_IMAGE_BYTES", len(image.bytes) - 1):
            self.refused(self.zipped(image.bytes, "big.zip"), "more than a DVD holds")
        self.refused(self.zipped(image.bytes[:-100], "odd.zip"), "not a whole number")

    def test_an_encrypted_member_is_refused(self) -> None:
        path = self.zipped(Image().bytes, "plain.zip", zipfile.ZIP_STORED)
        data = bytearray(path.read_bytes())
        central = data.rfind(b"PK\x01\x02")
        data[6] |= 1
        data[central + 8] |= 1
        self.refused(self.write(data, "locked.zip"), "encrypted")

    def test_damaged_streams_are_refused(self) -> None:
        image = Image()
        path = self.zipped(image.bytes, "deflated.zip")
        data = bytearray(path.read_bytes())
        start = 30 + len("Battle Engine Aquila (Test).iso")
        for at in (start + 40, start + len(data) // 2):
            broken = bytearray(data)
            broken[at:at + 16] = bytes(16)
            with self.subTest(at=at):
                try:
                    disc.read_member(self.write(broken, f"broken{at}.zip"))
                except disc.Ps2DiscError:
                    pass
        self.refused(self.write(data[:len(data) // 2], "cut.zip"), "the zip cannot be read")


class MutationTests(Workspace):
    """Random damage to an authored image or zip: a member, or a Ps2DiscError, never another exception."""

    def assert_only_refusals(self, original: bytes, name: str, rounds: int, seed: int,
                             hot: list[tuple[int, int]]) -> None:
        rng = random.Random(seed)
        spans = [(lo, min(hi, len(original))) for lo, hi in hot if lo < len(original)] + [(0, len(original))]
        outcomes = {"read": 0, "refused": 0}
        for _ in range(rounds):
            data = bytearray(original)
            for _ in range(rng.randint(1, 6)):
                lo, hi = rng.choice(spans)
                data[rng.randrange(lo, hi)] = rng.randrange(256)
            path = self.write(data, name)
            try:
                disc.read_member(path)
                outcomes["read"] += 1
            except disc.Ps2DiscError:
                outcomes["refused"] += 1
        self.assertEqual(rounds, sum(outcomes.values()))
        self.assertGreater(outcomes["refused"], 0)

    def test_mutated_images_are_read_or_refused(self) -> None:
        image = Image()
        root = image.root_sector * SECTOR
        hot = [(image.pvd, image.pvd + 200), (root, root + image.root_bytes),
               (image.package_base, image.package_base + 12), (image.index_base(), len(image.bytes))]
        self.assert_only_refusals(image.bytes, "mutated.iso", 300, 1, hot)

    def test_mutated_zips_are_read_or_refused(self) -> None:
        data = self.zipped(Image().bytes).read_bytes()
        self.assert_only_refusals(data, "mutated.zip", 200, 2, [(0, 80), (len(data) - 120, len(data))])


class CommandLineTests(Workspace):
    def run_main(self, argv: list[str]) -> tuple[int, bytes, str]:
        out, err = io.BytesIO(), io.StringIO()
        stdout = io.TextIOWrapper(out, encoding="utf-8")
        with mock.patch.object(sys, "stdout", stdout), contextlib.redirect_stderr(err):
            try:
                code = disc.main(argv)
            except SystemExit as exit_:
                code = exit_.code
            stdout.flush()
        return code, out.getvalue(), err.getvalue()

    def test_extract_writes_only_to_standard_output(self) -> None:
        path = self.write(Image().bytes)
        code, out, err = self.run_main(["extract", str(path), "--stdout"])
        self.assertEqual((0, dict(members())[TARGET]), (code, out))
        self.assertEqual(2, len(json.loads(err)["warnings"]))
        self.assertEqual(2, self.run_main(["extract", str(path)])[0])
        self.assertEqual(2, self.run_main(["extract", str(path), "--stdout", "--strict-pins"])[0])
        self.assertEqual(["image.iso"], sorted(p.name for p in self.dir.iterdir()))

    def test_list_and_verify(self) -> None:
        path = self.zipped(Image().bytes)
        code, out, _ = self.run_main(["list", str(path)])
        self.assertEqual(0, code)
        self.assertEqual([p for p, _ in members()], [row["path"] for row in json.loads(out)["rows"]])
        code, out, _ = self.run_main(["verify", str(path)])
        self.assertEqual(1, code)
        self.assertFalse(json.loads(out)["pass"])
        code, _, err = self.run_main(["verify", str(self.write(bytes(40 * SECTOR), "blank.iso"))])
        self.assertEqual(2, code)
        self.assertIn("ps2_disc:", err)


_retail_image = os.environ.get("BEA_PS2_IMAGE")


@unittest.skipUnless(_retail_image and Path(_retail_image).is_file(),
                     "BEA_PS2_IMAGE does not name the player's own PS2 image "
                     "(a plain ISO or a Redump-style zip of one)")
class RetailImageGate(unittest.TestCase):
    """The released Europe or USA disc: the package index and level 888 are the pinned ones."""

    def test_the_index_and_level_888_are_the_pinned_ones(self) -> None:
        report = disc.gate(_retail_image)  # one read: a plain ISO in place, a zip in two stream passes
        self.assertEqual([], report["warnings"])
        self.assertTrue(report["pass"] and report["package"]["indexPinned"] and report["member"]["pinned"])
        self.assertEqual(disc.RELEASED_PACKAGE_ROWS, report["package"]["rows"])
        self.assertEqual(disc.LEVEL_888_BYTES, report["member"]["bytes"])
        self.assertEqual(1 if report["imageKind"] == "iso" else 2, report["streamPasses"])


if __name__ == "__main__":
    unittest.main()
