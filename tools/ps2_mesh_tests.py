#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Tests of ps2_mesh.py on authored meshes. Its retail gate runs when BEA_PS2_IMAGE (the player's image, or an extracted level 731 archive) and BEA_GAME name the player's own
files, and is a named SKIP otherwise; a second gate over a folder of extracted archives runs when BEA_PS2_MEMBERS names one."""
from __future__ import annotations

import collections
import contextlib
import io
import os
import random
import struct
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rebuild" / "tools"))

import ps2_disc  # noqa: E402
import ps2_mesh as pm  # noqa: E402


def chunk(tag: bytes, payload: bytes) -> bytes:
    return tag + struct.pack("<I", len(payload)) + payload


def bits(x: float) -> int:
    return struct.unpack("<I", struct.pack("<f", x))[0]


def record(pos, normal=(0.0, 0.0, 1.0), uv=(0.25, 0.75), colour=0xFFFFFFFF, draws=True, junk=0) -> bytes:
    w = [junk] * 28
    w[0:3] = [bits(x) for x in normal]
    w[9:11] = [bits(x) for x in uv]
    w[11] = colour
    w[24:27] = [bits(x) for x in pos]
    w[27] = 0 if draws else 0x8000
    return struct.pack("<28I", *w)


def mmpv(records, texr=None, kicks=None) -> bytes:
    texr = struct.pack("<6I", 1, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 7) if texr is None else texr
    if kicks is None:
        kicks = sum(1 for r in records if struct.unpack_from("<I", r, 108)[0] == 0)
    body = struct.pack("<I", 1) + chunk(b"TEXR", texr) + chunk(b"NVRT", struct.pack("<IIf", len(records), kicks, 0.004)) + chunk(b"VRTS", b"".join(records))
    return chunk(b"MMPV", body)


def p2vb(groups, count=None, marker=96) -> bytes:
    return chunk(b"P2VB", chunk(b"MSVB", struct.pack("<II", len(groups) if count is None else count, marker)) + b"".join(groups))


CHILDREN = (("CMSP", bytes(range(256)) + bytes(60)), ("PRNT", struct.pack("<I", 0)), ("BBOX", bytes(48)), ("HPOS", bytes(range(16))))


def mesp(groups, **more) -> bytes:
    kids = b"".join(chunk(t.encode(), p) for t, p in CHILDREN) + (more.get("p2vb") or p2vb(groups))
    return chunk(b"MESP", kids)


def stream(parts, texture_ids=(3, 1)) -> bytes:
    top = [chunk(b"CMSH", bytes(range(256)) + bytes(116)), chunk(b"CMST", bytes(36 * len(texture_ids)))]
    top += [chunk(b"MSHT", chunk(b"TEXB", bytes(range(20)) + struct.pack("<I", i))) for i in texture_ids]
    return b"".join(top + list(parts) + [chunk(b"BBOX", bytes(48))])


NAMES = ["zero.tga", "one.tga", "two.tga", "three.tga"]

# the quad strip the PS2 stores for a rectangle of two triangles: the order is the PC strip reversed, the first two records and the sixth do not draw
QUAD = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 1.0, 0.0)]


def quad_records(base=0.0, dx=0.0):
    pts = [(x + dx, y, z + base) for x, y, z in QUAD]
    order = [1, 1, 2, 0, 3, 3]
    flags = [False, False, True, True, True, False]
    return [record(pts[i], draws=f) for i, f in zip(order, flags)]


def canon(t):
    m = min(range(3), key=lambda k: t[k])
    return t[m:] + t[:m]


def decode(strip_indices):
    out = collections.Counter()
    for i in range(len(strip_indices) - 2):
        a, b, c = strip_indices[i:i + 3]
        if len({a, b, c}) < 3:
            continue
        if i & 1:
            b, c = c, b
        out[canon((a, b, c))] += 1
    return out


def rule(ids, draws):
    out = collections.Counter()
    for i in range(2, len(ids)):
        a, b, c = ids[i - 2], ids[i - 1], ids[i]
        if not draws[i] or len({a, b, c}) < 3:
            continue
        if i & 1:
            b, c = c, b
        out[canon((a, b, c))] += 1
    return out


def children_of(buf, start, end):
    return pm._tile(buf, start, end, "test")


class StripTests(unittest.TestCase):
    def test_a_quad_block_keeps_its_two_triangles_and_their_winding(self):
        ids = [1, 1, 2, 0, 3, 3]
        draws = [False, False, True, True, True, False]
        self.assertEqual(rule(ids, draws), decode(pm.strip(ids, draws)))
        self.assertEqual(2, sum(decode(pm.strip(ids, draws)).values()))

    def test_runs_are_joined_by_degenerate_pairs_and_the_winding_survives_either_parity(self):
        for lead in range(4):                                         # a run can start at an odd or an even record
            ids = [9] * lead + [1, 1, 2, 0, 3, 3] * 3
            draws = [False] * lead + [False, False, True, True, True, False] * 3
            s = pm.strip(ids, draws)
            self.assertEqual(rule(ids, draws), decode(s), lead)
            self.assertGreaterEqual(len(s), 3)

    def test_random_strips_decode_to_the_triangles_the_ps2_draws(self):
        rng = random.Random(20261031)
        for case in range(600):
            n = rng.randint(3, 40)
            ids = [rng.randrange(7) for _ in range(n)]
            draws = [rng.random() < 0.6 for _ in range(n)]
            self.assertEqual(rule(ids, draws), decode(pm.strip(ids, draws)), f"case {case}")

    def test_no_drawing_triangle_gives_an_empty_strip_and_fewer_than_three_records_too(self):
        self.assertEqual([], pm.strip([1, 2], [True, True]))
        self.assertEqual([], pm.strip([1, 1, 1, 2, 2], [True] * 5))
        self.assertEqual([], pm.strip([1, 2, 3], [True, True, False]))

    def test_a_run_that_is_one_triangle_is_that_triangle(self):
        self.assertEqual(collections.Counter({canon((5, 6, 7)): 1}), decode(pm.strip([5, 6, 7], [False, False, True])))
        self.assertEqual(collections.Counter({canon((5, 7, 6)): 1}), decode(pm.strip([0, 5, 6, 7], [False, False, False, True])), "record 3 winds odd")


class ConvertTests(unittest.TestCase):
    def convert(self, parts, texture_ids=(3, 1)):
        return pm.convert(stream(parts, texture_ids), NAMES)

    def top(self, data):
        return [(t, a, b) for t, a, b in pm._tile(data, 0, len(data), "out")]

    def test_every_chunk_but_the_textures_and_the_geometry_is_copied_byte_for_byte(self):
        src = stream([mesp([mmpv(quad_records())]), mesp([])])
        out = pm.convert(src, NAMES)
        a, b = pm._tile(src, 0, len(src), "in"), self.top(out)
        self.assertEqual([t for t, *_ in a], [t for t, *_ in b], "the same top-level chunks in the same order")
        for (ta, sa, ea), (tb, sb, eb) in zip(a, b):
            if ta in ("CMSH", "CMST", "BBOX"):
                self.assertEqual(src[sa:ea], out[sb:eb], ta)
            if ta == "MESP":
                ka, kb = children_of(src, sa, ea), children_of(out, sb, eb)
                self.assertEqual([k[0] for k in ka[:-1]], [k[0] for k in kb[:-1]])
                self.assertEqual(("P2VB", "PMVB"), (ka[-1][0], kb[-1][0]), "the last child changes its tag and nothing else's place")
                for x, y in zip(ka[:-1], kb[:-1]):
                    self.assertEqual(src[x[1]:x[2]], out[y[1]:y[2]], x[0])

    def test_a_texture_binding_becomes_the_name_of_the_archives_text_chunk(self):
        out = self.convert([mesp([])], (3, 1))
        msht = [(a, b) for t, a, b in self.top(out) if t == "MSHT"]
        self.assertEqual([156, 156], [b - a for a, b in msht])
        for (a, b), (want, idx) in zip(msht, (("three.tga", 3), ("one.tga", 1))):
            texb = pm._tile(out, a, b, "MSHT")
            self.assertEqual(["TEXB"], [k[0] for k in texb])
            payload = out[texb[0][1]:texb[0][2]]
            self.assertEqual(148, len(payload))
            self.assertEqual(bytes(range(20)), payload[:20], "the first twenty bytes are the PS2's")
            self.assertEqual(want.encode() + bytes(128 - len(want)), payload[20:], "a NUL-padded 128-byte name")

    def test_a_part_without_a_group_gets_a_pmvb_that_holds_only_a_cmvb_with_no_piece(self):
        out = self.convert([mesp([])])
        part = next(t for t in self.top(out) if t[0] == "MESP")
        pmvb_ = children_of(out, part[1], part[2])[-1]
        kids = children_of(out, pmvb_[1], pmvb_[2])
        self.assertEqual(["CMVB"], [k[0] for k in kids])
        self.assertEqual(296, kids[0][2] - kids[0][1])
        self.assertEqual(0, struct.unpack_from("<i", out, kids[0][1] + 0x108)[0])
        self.assertEqual([None], pm.pc_parts(out))

    def test_the_vertex_buffer_record_has_the_fields_the_loader_reads(self):
        c = pm.cmvb(3)
        self.assertEqual(296, len(c))
        self.assertEqual(3, struct.unpack_from("<i", c, 0x108)[0])
        self.assertEqual((36, 0x152, 4), struct.unpack_from("<III", c, 0x114))
        self.assertEqual(0xDEAD, struct.unpack_from("<I", c, 0x10C)[0])
        pointers = struct.unpack_from("<64I", c, 8)
        self.assertTrue(all(pointers[g] for g in range(3)), "the pieces in use are non-zero")
        self.assertEqual([0] * 61, list(pointers[3:]), "the rest are zero")
        self.assertEqual((0, 0, 0), struct.unpack_from("<III", pm.cmvb(0), 0x114), "stride, format and primitive type mean something only with a piece")
        for bad in (-1, 13):
            with self.assertRaises(pm.Ps2MeshError):
                pm.cmvb(bad)

    def test_the_pool_is_the_distinct_records_of_all_groups_in_order_held_by_the_first_group_only(self):
        g1 = mmpv(quad_records(0.0))
        g2 = mmpv(quad_records(0.0) + quad_records(5.0))                      # the first quad again, then another
        out = self.convert([mesp([g1, g2])])
        pool, strips, texrs = pm.pc_parts(out)[0]
        self.assertEqual(8, len(pool), "four distinct vertices of the first quad and four of the second")
        self.assertEqual(2, len(strips))
        self.assertEqual(2, len(texrs))
        part = next(t for t in self.top(out) if t[0] == "MESP")
        pmvb_ = children_of(out, part[1], part[2])[-1]
        kids = children_of(out, pmvb_[1], pmvb_[2])
        self.assertEqual(["CMVB", "MMPT", "IBUF", "VBUF", "TEXR", "MMPT", "IBUF", "VBUF", "TEXR"], [k[0] for k in kids])
        sizes = [k[2] - k[1] for k in kids]
        self.assertEqual((8 * 36, 0), (sizes[3], sizes[7]), "the second group's VBUF is empty")
        for first in (1, 5):
            vbytes, ibytes, icount, vcount, prims, active = struct.unpack_from("<6I", out, kids[first][1])
            self.assertEqual((8 * 36, 8), (vbytes, vcount), "both groups declare the pool")
            self.assertEqual((2 * icount, icount - 2, 1), (ibytes, prims, active))
            self.assertEqual(icount * 2, sizes[first + 1])

    def test_each_group_keeps_its_texr(self):
        a = struct.pack("<6I", 0, 1, 2, 3, 4, 5)
        b = struct.pack("<6I", 9, 8, 7, 6, 5, 4)
        out = self.convert([mesp([mmpv(quad_records(), texr=a), mmpv(quad_records(2.0), texr=b)])])
        self.assertEqual([a, b], pm.pc_parts(out)[0][2])

    def test_a_vertex_is_position_normal_colour_and_uv_whatever_the_other_words_hold(self):
        r1 = record((1.0, 2.0, 3.0), (0.0, 1.0, 0.0), (0.5, 0.25), 0x80FF8040, junk=0)
        r2 = record((1.0, 2.0, 3.0), (0.0, 1.0, 0.0), (0.5, 0.25), 0x80FF8040, junk=0xABCDEF01)
        verts = pm.pc_parts(self.convert([mesp([mmpv([r1, r1, record((0.0, 0.0, 0.0)), record((0.0, 1.0, 0.0), draws=False), record((1.0, 0.0, 0.0))])])]))[0][0]
        self.assertEqual(struct.pack("<3f3fI2f", 1.0, 2.0, 3.0, 0.0, 1.0, 0.0, 0x80FF8040, 0.5, 0.25), verts[0])
        collapsed = pm.pc_parts(self.convert([mesp([mmpv([r1, r2, record((9.0, 9.0, 9.0)), record((8.0, 8.0, 8.0)), record((7.0, 7.0, 7.0))])])]))[0][0]
        self.assertEqual(4, len(collapsed), "r1 and r2 differ only in words the PC does not have: one vertex")

    def test_a_non_finite_texture_coordinate_travels_by_its_bits(self):
        weird = list(struct.unpack("<28I", record((0.0, 0.0, 0.0))))
        weird[9], weird[10] = 0x7FC00001, 0xFF800000
        r = struct.pack("<28I", *weird)
        verts = pm.pc_parts(self.convert([mesp([mmpv([r, r, record((1.0, 0.0, 0.0)), record((0.0, 1.0, 0.0)), record((1.0, 1.0, 0.0))])])]))[0][0]
        self.assertEqual((0x7FC00001, 0xFF800000), struct.unpack_from("<2I", verts[0], 28))
        self.assertEqual(("raw", 0x7FC00001), pm.vertex_key(verts[0])[7], "a non-finite float compares by its bits")

    def test_the_converted_triangles_are_the_ones_the_ps2_records_draw(self):
        recs = quad_records(0.0) + quad_records(3.0, dx=2.0)
        pool, strips, _ = pm.pc_parts(self.convert([mesp([mmpv(recs)])]))[0]
        want = collections.Counter()
        keys = [pm.vertex_key(struct.pack("<3I3II2I", *[struct.unpack_from("<I", r, o)[0] for o in (96, 100, 104, 0, 4, 8, 44, 36, 40)])) for r in recs]
        draws = [struct.unpack_from("<I", r, 108)[0] == 0 for r in recs]
        for i in range(2, len(recs)):
            a, b, c = keys[i - 2], keys[i - 1], keys[i]
            if draws[i] and len({a, b, c}) == 3:
                if i & 1:
                    b, c = c, b
                t = (a, b, c)
                m = min(range(3), key=lambda k: repr(t[k]))
                want[t[m:] + t[:m]] += 1
        self.assertEqual(want, pm.triangles(pool, strips[0]))
        self.assertEqual(4, sum(want.values()))


class RefusalTests(unittest.TestCase):
    def refuses(self, data, fragment="", names=NAMES):
        with self.assertRaisesRegex(pm.Ps2MeshError, fragment):
            pm.convert(data, names)

    def test_a_truncated_or_overlong_chunk_is_refused(self):
        good = stream([mesp([mmpv(quad_records())])])
        for cut in (5, len(good) - 3):
            self.refuses(good[:cut], "chunk|header")
        self.refuses(good[:384] + struct.pack("<I", 1 << 30) + good[388:], "runs past")      # the size field of the second chunk

    def test_a_stream_that_does_not_start_with_cmsh_or_has_a_bad_tag_is_refused(self):
        self.refuses(chunk(b"CMST", b"") + stream([]), "starts with CMSH")
        self.refuses(b"\x01\x02\x03\x04" + struct.pack("<I", 0), "not a chunk tag")

    def test_the_usual_layout_is_required_at_every_level(self):
        recs = quad_records()
        bad_mmpv = chunk(b"MMPV", struct.pack("<I", 2) + mmpv(recs)[12:])
        self.refuses(stream([mesp([], p2vb=p2vb([bad_mmpv], count=1))]), "usual MMPV")
        self.refuses(stream([mesp([], p2vb=chunk(b"P2VB", b""))]), "MSVB")
        self.refuses(stream([mesp([mmpv(recs)], p2vb=p2vb([mmpv(recs)], count=2))]), "names 2 groups")
        self.refuses(stream([mesp([mmpv(recs)], p2vb=p2vb([mmpv(recs)], marker=95))]), "names 1 groups|MSVB")
        self.refuses(stream([mesp([mmpv(recs)], p2vb=p2vb([mmpv(recs)] * 13))]), "groups")
        part = chunk(b"MESP", chunk(b"CMSP", bytes(8)))
        self.refuses(stream([part]), "no P2VB")
        two = chunk(b"MESP", p2vb([]) + p2vb([]))
        self.refuses(stream([two]), "two P2VB")

    def test_a_record_count_a_kick_count_or_a_record_size_that_disagrees_is_refused(self):
        recs = quad_records()
        self.refuses(stream([mesp([mmpv(recs, kicks=2)])]), "NVRT says 2")
        short = chunk(b"MMPV", struct.pack("<I", 1) + chunk(b"TEXR", bytes(24)) + chunk(b"NVRT", struct.pack("<IIf", 6, 3, 0.0)) + chunk(b"VRTS", b"".join(recs)[:-4]))
        self.refuses(stream([mesp([short])]), "VRTS holds")
        wide = chunk(b"MMPV", struct.pack("<I", 1) + chunk(b"TEXR", bytes(24)) + chunk(b"NVRT", struct.pack("<IIf", 6, 3, 0.0)) + chunk(b"VRTS", bytes(124 * 6)))
        self.refuses(stream([mesp([wide])]), "VRTS holds 744 bytes for 6 records of 112")

    def test_a_group_where_no_triangle_draws_is_refused(self):
        flat = [record((0.0, 0.0, 0.0), draws=False)] * 5
        self.refuses(stream([mesp([mmpv(flat)])]), "no triangle draws")

    def test_a_pool_too_big_for_a_u16_index_is_refused(self):
        many = [record((float(i), 0.0, 0.0)) for i in range(65537)]
        self.refuses(stream([mesp([mmpv(many)])]), "more than a PC index")

    def test_a_texture_the_archive_does_not_have_or_a_name_that_does_not_fit_is_refused(self):
        self.refuses(stream([mesp([])], texture_ids=(9,)), "names TEXT chunk 9")
        self.refuses(stream([mesp([])], texture_ids=(0,)), "does not fit", names=["x" * 128])
        self.refuses(stream([mesp([])], texture_ids=(0,)), "", names=[])

    def test_a_skinned_mesh_is_not_read_as_a_pc_mesh(self):
        out = pm.convert(stream([mesp([mmpv(quad_records())])]), NAMES)
        head = out.index(b"CMVB") + 8
        broken = bytearray(out)
        struct.pack_into("<I", broken, head + 0x114, 48)
        with self.assertRaisesRegex(pm.Ps2MeshError, "rigid"):
            pm.pc_parts(bytes(broken))


class ArchiveTests(unittest.TestCase):
    def member(self, names=("alpha.tga", "beta.tga"), mesh_name=b"fenrir-test.msh"):
        # as in the real archives: a TEXT chunk holds one nested chunk (id word, 160, then the name field) and a MESH chunk holds a PMSH chunk
        text = [chunk(b"TEXT", chunk(b"PTEX", struct.pack("<II", 0x1234, 160) + n.encode().ljust(160, b"\0") + bytes(16))) for n in names]
        pmsh = chunk(b"PMSH", mesh_name.ljust(304, b"\0") + stream([mesp([mmpv(quad_records())])], texture_ids=(1, 0)))
        return chunk(b"LVLR", bytes(8)) + b"".join(text) + chunk(b"MESH", pmsh) + chunk(b"WRES", bytes(4))

    def test_the_texture_names_are_the_text_chunks_in_archive_order(self):
        self.assertEqual(["alpha.tga", "beta.tga"], pm.archive_texture_names(self.member()))

    def test_a_mesh_is_found_by_name_ignoring_case_and_converted_with_the_archives_names(self):
        out = pm.convert_member_mesh(self.member(), "FENRIR-TEST.MSH")
        texb = [out[a + 8 + 20:a + 8 + 20 + 9] for t, a, _ in pm._tile(out, 0, len(out), "x") if t == "MSHT"]
        self.assertEqual([b"beta.tga\0", b"alpha.tga"], texb)
        with self.assertRaisesRegex(pm.Ps2MeshError, "no mesh of that name"):
            pm.convert_member_mesh(self.member(), "other.msh")

    def test_a_pmsh_payload_without_the_cmsh_stream_after_the_prefix_is_refused(self):
        with self.assertRaisesRegex(pm.Ps2MeshError, "304-byte prefix"):
            pm.mesh_stream(bytes(400))

    def test_compare_counts_agreement_with_a_pc_mesh_of_the_same_model(self):
        src = stream([mesp([]), mesp([mmpv(quad_records()), mmpv(quad_records(2.0))])])
        pc = pm.convert(src, NAMES)
        self.assertEqual({"parts": 2, "geometry parts": 1, "vertex sets equal": 1, "groups": 2, "groups equal": 2}, pm.compare(src, NAMES, pc))
        other = pm.convert(stream([mesp([]), mesp([mmpv(quad_records()), mmpv(quad_records(2.0, dx=9.0))])]), NAMES)
        result = pm.compare(src, NAMES, other)
        self.assertEqual({"parts": 2, "geometry parts": 1, "vertex sets equal": 0, "groups": 2, "groups equal": 1, "triangles in differing groups": 4}, result)


class CompareTests(unittest.TestCase):
    def test_vertices_that_differ_below_one_ten_thousandth_are_the_same_vertex(self):
        src = stream([mesp([mmpv(quad_records())])])
        near = pm.convert(stream([mesp([mmpv(quad_records(base=1e-6))])]), NAMES)
        far = pm.convert(stream([mesp([mmpv(quad_records(base=1e-3))])]), NAMES)
        self.assertEqual({"parts": 1, "geometry parts": 1, "vertex sets equal": 1, "groups": 1, "groups equal": 1}, pm.compare(src, NAMES, near))
        self.assertEqual(0, pm.compare(src, NAMES, far)["vertex sets equal"], "a thousandth is a different vertex")

    def test_geometry_on_one_side_only_is_counted_and_is_no_geometry_part(self):
        src = stream([mesp([mmpv(quad_records())])])
        empty = pm.convert(stream([mesp([])]), NAMES)
        self.assertEqual({"parts": 1, "geometry on one side only": 1}, pm.compare(src, NAMES, empty))
        self.assertEqual({"parts": 1, "geometry on one side only": 1}, pm.compare(stream([mesp([])]), NAMES, pm.convert(src, NAMES)))

    def test_a_different_group_count_or_part_count_is_reported(self):
        two = stream([mesp([mmpv(quad_records()), mmpv(quad_records(2.0))])])
        one = pm.convert(stream([mesp([mmpv(quad_records())])]), NAMES)
        self.assertEqual({"parts": 1, "geometry parts": 1, "vertex sets equal": 0, "group count differs": 1}, pm.compare(two, NAMES, one))
        self.assertEqual({"parts": 1, "part count differs": 1}, pm.compare(two, NAMES, pm.convert(stream([mesp([]), mesp([])]), NAMES)))


class CommandLineTests(unittest.TestCase):
    def run_main(self, *argv):
        err = io.StringIO()
        out = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            try:
                code = pm.main(list(argv))
            except pm.Ps2MeshError as error:
                print(f"ps2 mesh: {error}", file=sys.stderr)
                code = 2
        return code, out.getvalue(), err.getvalue()

    def test_convert_writes_the_pc_stream_once_and_prints_only_a_size_and_a_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            member = Path(tmp) / "m.aya"
            member.write_bytes(ArchiveTests().member())
            out = Path(tmp) / "out" / "mesh.bin"
            code, text, _ = self.run_main("convert", str(member), "fenrir-test.msh", "--out", str(out))
            self.assertEqual(0, code)
            self.assertTrue(text.startswith("wrote ") and "sha256" in text)
            self.assertNotIn("fenrir", text.lower())
            self.assertEqual(pm.convert_member_mesh(member.read_bytes(), "fenrir-test.msh"), out.read_bytes())
            with self.assertRaisesRegex(pm.Ps2MeshError, "exists already"):
                pm.main(["convert", str(member), "fenrir-test.msh", "--out", str(out)])

    def test_a_file_that_is_not_an_extracted_level_archive_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            junk = Path(tmp) / "junk"
            junk.write_bytes(b"not an archive")
            with self.assertRaisesRegex(pm.Ps2MeshError, "not an extracted level archive"):
                pm.main(["convert", str(junk), "x", "--out", str(Path(tmp) / "o")])


# ---- the retail gates ---------------------------------------------------------------------------------------------------------
def member_731():
    image = os.environ.get("BEA_PS2_IMAGE")
    if not image or not os.environ.get("BEA_GAME"):
        return None
    data = Path(image).read_bytes()[:4] if Path(image).is_file() else b""
    if data == b"LVLR":
        return Path(image).read_bytes()
    return ps2_disc.read_member(Path(image), "\\data\\Resources\\731_res_PS2.aya").data


class RetailGate(unittest.TestCase):
    """boss-fenrir converted from the player's own PS2 copy against the PC game's own file: the oracle of the converter."""

    def test_the_converted_boss_fenrir_is_the_pc_boss_fenrir(self):
        member = member_731()
        if member is None:
            self.skipTest("BEA_PS2_IMAGE and BEA_GAME are not set")
        import cmsh_static_preview as cs
        game = Path(os.environ["BEA_GAME"])
        names = pm.archive_texture_names(member)
        payload = next(p for n, p in pm.archive_meshes(member) if n.lower().startswith("boss-fenrir"))
        ps2 = pm.mesh_stream(payload)
        pc = cs.inflate_aya((game / "data/resources/meshes/m_boss-fenrir.msh.aya").read_bytes())
        converted = pm.convert(ps2, names)
        parsed, original = cs.parse_cmsh_stream(converted), cs.parse_cmsh_stream(pc)
        self.assertEqual((len(original.parts), sum(len(p.groups) for p in original.parts)), (len(parsed.parts), sum(len(p.groups) for p in parsed.parts)),
                         "the repository's own PC parser reads the converted mesh and finds the PC mesh's parts and groups")
        self.assertEqual([t.name.lower() for t in original.textures], [t.name.lower() for t in parsed.textures], "the same four textures by name")
        result = pm.compare(ps2, names, pc)
        self.assertEqual({"parts": 193, "geometry parts": 14, "vertex sets equal": 14, "groups": 40, "groups equal": 39, "triangles in differing groups": 1}, result)

    def test_the_census_of_every_mesh_with_a_loose_pc_twin(self):
        folder = os.environ.get("BEA_PS2_MEMBERS")
        if not folder or not os.environ.get("BEA_GAME"):
            self.skipTest("BEA_PS2_MEMBERS and BEA_GAME are not set")
        import zlib
        import cmsh_static_preview as cs
        game = Path(os.environ["BEA_GAME"])
        loose = {p.name.lower(): p for p in (game / "data/resources/meshes").glob("*.aya")}
        total, seen = collections.Counter(), set()
        for path in sorted(Path(folder).glob("*_res_PS2.aya")):
            member = path.read_bytes()
            names = pm.archive_texture_names(member)
            for name, payload in pm.archive_meshes(member):
                if name.lower() in seen or f"m_{name}.aya".lower() not in loose:
                    continue
                seen.add(name.lower())
                try:
                    r = pm.compare(pm.mesh_stream(payload), names, cs.inflate_aya(loose[f"m_{name}.aya".lower()].read_bytes()))
                except (pm.Ps2MeshError, cs.CmshProfileError, zlib.error, struct.error):
                    total["refused"] += 1
                    continue
                total["meshes"] += 1
                for k, v in r.items():
                    total[k] += v
        self.assertGreaterEqual(total["meshes"], 100)
        self.assertLessEqual(total["refused"], 5, "only the skinned meshes (124-byte records) are refused")
        self.assertGreaterEqual(total["vertex sets equal"] / total["geometry parts"], 0.99)
        self.assertGreaterEqual(total["groups equal"] / total["groups"], 0.98)


if __name__ == "__main__":
    unittest.main(verbosity=2 if "-v" in sys.argv else 1, argv=[a for a in sys.argv if a != "-v"])
