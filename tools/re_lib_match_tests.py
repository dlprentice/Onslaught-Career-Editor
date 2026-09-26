"""Focused tests for tools/re_lib_match.py on synthetic archives, objects and images (no retail data)."""
from __future__ import annotations

import shutil
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import re_lib_match as M  # noqa: E402


def coff(sections, symbols):
    """sections: [(name, chars, data, [(offset, symbol index, type)])];
    symbols: [(name, value, section, type, storage, aux bytes)] (aux records follow their symbol)."""
    strtab = bytearray(b"\0\0\0\0")

    def name8(name):
        raw = name.encode()
        if len(raw) <= 8:
            return raw.ljust(8, b"\0")
        off = len(strtab)
        strtab.extend(raw + b"\0")
        return struct.pack("<II", 0, off)

    head = 20 + 40 * len(sections)
    body = bytearray()
    placed = []
    for _name, _chars, data, relocs in sections:
        dptr = head + len(body)
        body += data
        rptr = head + len(body)
        for off, sym, typ in relocs:
            body += struct.pack("<IIH", off, sym, typ)
        placed.append((dptr, rptr if relocs else 0))
    psym = head + len(body)
    symtab = bytearray()
    count = 0
    for name, value, sec, typ, storage, aux in symbols:
        naux = len(aux) // 18
        symtab += name8(name) + struct.pack("<IhHBB", value, sec, typ, storage, naux) + aux
        count += 1 + naux
    struct.pack_into("<I", strtab, 0, len(strtab))
    out = bytearray(struct.pack("<HHIIIHH", 0x14C, len(sections), 0, psym, count, 0, 0))
    for (name, chars, data, relocs), (dptr, rptr) in zip(sections, placed):
        out += name.encode().ljust(8, b"\0")
        out += struct.pack("<IIIIIIHHI", 0, 0, len(data), dptr, rptr, 0, len(relocs), 0, chars)
    return bytes(out + body + symtab + strtab)


def archive(members):
    longnames = b"".join(n.encode() + b"/\n" for n, _ in members)
    out = bytearray(b"!<arch>\n")

    def member(name, data):
        out.extend(name.ljust(16).encode() + b"0".ljust(12) + b"0".ljust(6) * 2
                   + b"644".ljust(8) + str(len(data)).ljust(10).encode() + b"`\n" + data)
        if len(data) & 1:
            out.extend(b"\n")

    member("/", b"\0\0\0\0")
    member("//", longnames)
    off = 0
    for name, data in members:
        member(f"/{off}", data)
        off += len(name) + 2
    return bytes(out)


class FakeImage:
    """A 64 KiB code page at 0x401000 filled with int3, with the given blobs placed in it."""

    def __init__(self, base, blobs):
        self.base = base
        self.start = 0x401000
        self.mem = bytearray(b"\xcc" * 0x10000)
        for va, data in blobs.items():
            self.mem[va - self.start:va - self.start + len(data)] = data
        self.imports = {}

    def read(self, va, n):
        if not self.start <= va < self.start + len(self.mem):
            return b""
        return bytes(self.mem[va - self.start:va - self.start + n])

    def u32(self, va):
        b = self.read(va, 4)
        return struct.unpack("<I", b)[0] if len(b) == 4 else None


CODE = M.IMAGE_SCN_CNT_CODE | 0x60000000
COMDAT = CODE | M.IMAGE_SCN_LNK_COMDAT
FUNC, EXT, STATIC = M.IMAGE_SYM_DTYPE_FUNCTION, M.IMAGE_SYM_CLASS_EXTERNAL, M.IMAGE_SYM_CLASS_STATIC
BODY = bytes(range(0x40, 0x40 + 20))        # 20 fixed bytes nothing else contains


def library(members):
    lib = M.Library(Path("synthetic.lib"), "0" * 64, {}, [])
    for name, data in M.read_archive(archive(members)):
        c = M.parse_coff(name, data)
        lib.objects[name] = c
        lib.functions.extend(M.object_functions(c))
    return lib


class ParsingTests(unittest.TestCase):
    def test_archive_long_names_and_coff_functions(self):
        obj = coff([(".text", CODE, BODY + b"\xc3" * 4, [])],
                   [(".text", 0, 1, 0, STATIC, b"\0" * 18), ("_first_function@4", 0, 1, FUNC, EXT, b""),
                    ("_second", 20, 1, FUNC, EXT, b"")])
        members = M.read_archive(archive([("obj\\i386\\long_member_name.obj", obj)]))
        self.assertEqual([n for n, _ in members], ["obj\\i386\\long_member_name.obj"])
        c = M.parse_coff(*members[0])
        fns = M.object_functions(c)
        self.assertEqual([(f.symbol, f.start, f.end) for f in fns], [("_first_function@4", 0, 20), ("_second", 20, 24)])

    def test_masm_labels_do_not_split_procedures(self):
        # MASM types local labels as functions; .bf records mark the real procedure starts
        obj = coff([(".text", CODE, BODY + BODY, [])],
                   [("_Proc@8", 0, 1, FUNC, EXT, b""), (".bf", 0, 1, 0, M.IMAGE_SYM_CLASS_FUNCTION, b""),
                    ("Loop", 8, 1, FUNC, STATIC, b""), ("ProcPrologue", 0, 1, FUNC, STATIC, b""),
                    ("_Next@8", 20, 1, FUNC, EXT, b""), (".bf", 20, 1, 0, M.IMAGE_SYM_CLASS_FUNCTION, b"")])
        fns = M.object_functions(M.parse_coff("a.obj", obj))
        self.assertEqual([(f.symbol, f.start, f.end) for f in fns], [("_Proc@8", 0, 20), ("_Next@8", 20, 40)])

    def test_masked_pattern_hides_relocation_fields(self):
        obj = coff([(".text", CODE, b"\xe8\x00\x00\x00\x00\xc3", [(1, 1, M.REL_I386_REL32)])],
                   [("_f", 0, 1, FUNC, EXT, b""), ("_g", 0, 0, FUNC, EXT, b"")])
        c = M.parse_coff("a.obj", obj)
        body, mask = M.masked_pattern(c, M.object_functions(c)[0])
        self.assertEqual(mask, b"\xff\0\0\0\0\xff")
        self.assertTrue(M.pattern_regex(body, mask).fullmatch(b"\xe8\x12\x34\x56\x78\xc3"))


class NameTests(unittest.TestCase):
    def test_qualified_names_from_demangler_text(self):
        cases = {
            "public: virtual void __thiscall D3DXTex::CCodec_DXT1::Decode(unsigned int, unsigned int, struct D3DXCOLOR *)":
                "D3DXTex::CCodec_DXT1::Decode",
            "short (** __stdcall D3DX::alloc_barray(struct D3DX::jpeg_common_struct *, int, unsigned int, unsigned int))[64]":
                "D3DX::alloc_barray",
            "public: bool __thiscall Foo::operator<(class Foo const &) const": "Foo::operator<",
            "public: int __thiscall Foo::operator()(int)": "Foo::operator()",
            "public: float * __thiscall D3DXVECTOR3::operator float *(void)": "D3DXVECTOR3::operator float *",
            "public: long __thiscall D3DXShader::CArray<class D3DXShader::CNode *>::Grow(unsigned int)":
                "D3DXShader::CArray<class D3DXShader::CNode *>::Grow",
            "void __cdecl `dynamic initializer for 'x''(void)": "`dynamic initializer for 'x''",
        }
        for text, want in cases.items():
            self.assertEqual(M.qualified_name(text), want, text)

    def test_flat_names(self):
        dem = {"??1CCodec@D3DXTex@@UAE@XZ": "public: virtual __thiscall D3DXTex::CCodec::~CCodec(void)",
               "??0CBlt@D3DXTex@@QAE@XZ": "public: __thiscall D3DXTex::CBlt::CBlt(void)",
               "??_GCCodec@D3DXTex@@UAEPAXI@Z":
                   "public: virtual void * __thiscall D3DXTex::CCodec::`scalar deleting dtor'(unsigned int)",
               "??YD3DXVECTOR3@@QAEAAU0@ABU0@@Z":
                   "public: struct D3DXVECTOR3 & __thiscall D3DXVECTOR3::operator+=(struct D3DXVECTOR3 const &)"}
        self.assertEqual(M.flat_name("??1CCodec@D3DXTex@@UAE@XZ", dem), "D3DXTex__CCodec__dtor")
        self.assertEqual(M.flat_name("??0CBlt@D3DXTex@@QAE@XZ", dem), "D3DXTex__CBlt__ctor")
        self.assertEqual(M.flat_name("??_GCCodec@D3DXTex@@UAEPAXI@Z", dem), "D3DXTex__CCodec__scalar_deleting_dtor")
        self.assertEqual(M.flat_name("??YD3DXVECTOR3@@QAEAAU0@ABU0@@Z", dem), "D3DXVECTOR3__operator_add_assign")
        self.assertEqual(M.flat_name("_D3DXMatrixMultiply@12", {}), "_D3DXMatrixMultiply")
        self.assertEqual(M.flat_name("@fast@8", {}), "fast")
        self.assertEqual(M.flat_name("__ftol", {}), "__ftol")

    def test_anonymous_function_templates(self):
        self.assertEqual(M._anonymous_template_name(
            "?D3DXIntersect@?$@I$0A@$0?0@@YGJPAUID3DXBaseMesh@@HKPBUD3DXVECTOR3@@1PAHPAKPAM44PAPAUID3DXBuffer@@3I@Z"),
            "D3DXIntersect_T_uint_0_m1")
        self.assertEqual(M._anonymous_template_name("?FillIndexBuffer@?$@G@D3DXCore@@YGJPAUIDirect3DIndexBuffer9@@K_N@Z"),
                         "D3DXCore::FillIndexBuffer_T_ushort")
        self.assertEqual(M._ms_number("PPPP@", 0), ("65535", 5))
        self.assertEqual(M._ms_number("0x", 0), ("1", 1))

    @unittest.skipUnless(shutil.which("llvm-undname"), "llvm-undname not installed")
    def test_demangle_all_tolerates_rejects(self):
        got = M.demangle_all(["??1CCodec@D3DXTex@@UAE@XZ", "?bad@@", "_c_symbol"])
        self.assertIn("D3DXTex::CCodec::~CCodec", got["??1CCodec@D3DXTex@@UAE@XZ"])
        self.assertNotIn("_c_symbol", got)


class ResolverTests(unittest.TestCase):
    LO = 0x401000

    def resolve(self, members, blobs, starts):
        lib = library(members)
        res = M.Resolver(lib, FakeImage(0x400000, blobs), {}, self.LO, self.LO + 0x1000, starts)
        res.run()
        return res

    def test_unique_match_and_call_placement(self):
        # _caller calls _helper (another object); the call lands on the matched helper
        caller = coff([(".text", COMDAT, BODY + b"\xe8\0\0\0\0\xc3", [(21, 1, M.REL_I386_REL32)])],
                      [("_caller", 0, 1, FUNC, EXT, b""), ("_helper", 0, 0, FUNC, EXT, b"")])
        helper = coff([(".text", COMDAT, bytes(range(0x80, 0x94)) + b"\xc3", [])], [("_helper", 0, 1, FUNC, EXT, b"")])
        call = struct.pack("<i", 0x401100 - (self.LO + 25))
        res = self.resolve([("a.obj", caller), ("b.obj", helper)],
                           {self.LO: BODY + b"\xe8" + call + b"\xc3", 0x401100: bytes(range(0x80, 0x94)) + b"\xc3"},
                           [self.LO, 0x401100])
        self.assertEqual(res.decided[self.LO]["how"], "unique")
        self.assertEqual(res.decided[0x401100]["how"], "unique")
        self.assertEqual(res.pool[("g", "_helper")], 0x401100)
        self.assertFalse(res.contested)

    def test_own_section_reference_must_land_inside_the_match(self):
        # a jump table entry (DIR32 to the function's own section) that points elsewhere is a conflict
        data = BODY + b"\0\0\0\0"
        obj = coff([(".text", COMDAT, data, [(20, 0, M.REL_I386_DIR32)])],
                   [(".text", 0, 1, 0, STATIC, b"\0" * 18), ("_f", 0, 1, FUNC, EXT, b"")])
        good = self.resolve([("a.obj", obj)], {self.LO: BODY + struct.pack("<I", self.LO)}, [self.LO])
        self.assertEqual(good.decided[self.LO]["how"], "unique")
        bad = self.resolve([("a.obj", obj)], {self.LO: BODY + struct.pack("<I", self.LO + 0x500)}, [self.LO])
        self.assertEqual(bad.decided[self.LO]["how"], "ambiguous")

    def test_relocations_separate_identical_bodies(self):
        # _left and _right share bytes but call different helpers; the helpers are matched elsewhere
        def caller(name, target):
            return coff([(".text", COMDAT, b"\x90" * 4 + b"\xe8\0\0\0\0\xc3", [(5, 1, M.REL_I386_REL32)])],
                        [(name, 0, 1, FUNC, EXT, b""), (target, 0, 0, FUNC, EXT, b"")])
        h1 = coff([(".text", COMDAT, bytes(range(0x80, 0x94)) + b"\xc3", [])], [("_h1", 0, 1, FUNC, EXT, b"")])
        h2 = coff([(".text", COMDAT, bytes(range(0xa0, 0xb4)) + b"\xc3", [])], [("_h2", 0, 1, FUNC, EXT, b"")])
        site = self.LO + 5
        blob = b"\x90" * 4 + b"\xe8" + struct.pack("<i", 0x401200 - (site + 4)) + b"\xc3"
        res = self.resolve([("l.obj", caller("_left", "_h1")), ("r.obj", caller("_right", "_h2")),
                            ("h1.obj", h1), ("h2.obj", h2)],
                           {self.LO: blob, 0x401100: bytes(range(0x80, 0x94)) + b"\xc3",
                            0x401200: bytes(range(0xa0, 0xb4)) + b"\xc3"}, [self.LO, 0x401100, 0x401200])
        self.assertEqual(res.decided[self.LO]["how"], "relocations")
        self.assertEqual(res.decided[self.LO]["cands"][0].fn.symbol, "_right")

    def test_layout_and_folding(self):
        # one object: A (sec 1), X (sec 2) and Y (sec 4) identical, B (sec 3); the image holds A, X-or-Y, B
        same = b"\x33\xc0\x40\x40\x40\x40\x40\x40\x40\xc3"
        a, b = bytes(range(0x10, 0x24)), bytes(range(0x30, 0x44))
        obj = coff([(".text", COMDAT, a, []), (".text", COMDAT, same, []), (".text", COMDAT, b, []),
                    (".text", COMDAT, same, [])],
                   [("_A", 0, 1, FUNC, EXT, b""), ("_X", 0, 2, FUNC, EXT, b""), ("_B", 0, 3, FUNC, EXT, b""),
                    ("_Y", 0, 4, FUNC, EXT, b"")])
        blob = a + same + b
        res = self.resolve([("o.obj", obj)], {self.LO: blob}, [self.LO, self.LO + 20, self.LO + 30])
        mid = res.decided[self.LO + 20]
        self.assertEqual((mid["how"], mid["cands"][0].fn.symbol), ("layout", "_X"))
        self.assertEqual(M.layout_violations(res.decided), [])


if __name__ == "__main__":
    unittest.main()
