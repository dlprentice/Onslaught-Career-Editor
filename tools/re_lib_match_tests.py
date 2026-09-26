"""Focused tests for tools/re_lib_match.py on synthetic archives, objects and images (no retail data)."""
from __future__ import annotations

import shutil
import struct
import sys
import tempfile
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
        # MASM types local labels as functions; .bf records mark the real procedure starts and .ef their ends
        obj = coff([(".text", CODE, BODY + BODY, [])],
                   [("_Proc@8", 0, 1, FUNC, EXT, b""), (".bf", 0, 1, 0, M.IMAGE_SYM_CLASS_FUNCTION, b""),
                    ("Loop", 8, 1, FUNC, STATIC, b""), ("ProcPrologue", 0, 1, FUNC, STATIC, b""),
                    (".ef", 17, 1, 0, M.IMAGE_SYM_CLASS_FUNCTION, b""),
                    ("_Next@8", 20, 1, FUNC, EXT, b""), (".bf", 20, 1, 0, M.IMAGE_SYM_CLASS_FUNCTION, b"")])
        fns = M.object_functions(M.parse_coff("a.obj", obj))
        self.assertEqual([(f.symbol, f.start, f.end) for f in fns], [("_Proc@8", 0, 17), ("_Next@8", 20, 40)])

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

    def test_flat_names_keep_an_identifiers_own_underscores(self):
        dem = {"?_JumpToContinuation@@YGXPAXPAUEHRegistrationNode@@@Z":
                   "void __stdcall _JumpToContinuation(void *, struct EHRegistrationNode *)",
               "?_Lrotate@?$_Tree@HU?$pair@$$CBHH@std@@U_Kfn@?$map@HHU?$less@H@std@@V?$allocator@H@2@@2@U?$less@H@2@V"
               "?$allocator@H@2@@std@@IAEXPAU_Node@12@@Z":
                   "protected: void __thiscall std::_Tree<int, struct std::pair<int const, int>, struct std::map<int, "
                   "int, struct std::less<int>, class std::allocator<int>>::_Kfn, struct std::less<int>, class "
                   "std::allocator<int>>::_Lrotate(struct std::_Tree<int>::_Node *)"}
        self.assertEqual(M.flat_name("?_JumpToContinuation@@YGXPAXPAUEHRegistrationNode@@@Z", dem),
                         "_JumpToContinuation")
        tree = M.flat_name(next(k for k in dem if "_Lrotate" in k), dem)
        self.assertTrue(tree.startswith("std___Tree_int_") and tree.endswith("___Lrotate"), tree)

    def test_saved_names_must_equal_a_proven_spelling(self):
        aliases = {"__stricmp": {"_stricmp"}}
        self.assertEqual(M.spellings("__stricmp", {}, aliases), {"__stricmp", "_stricmp", "stricmp"})
        self.assertEqual(M.spellings("_fclose", {}, {}), {"_fclose", "fclose"})
        dem = {"?_JumpToContinuation@@YGXPAXPAUEHRegistrationNode@@@Z": "void __stdcall _JumpToContinuation(void *)"}
        self.assertEqual(M.spellings("?_JumpToContinuation@@YGXPAXPAUEHRegistrationNode@@@Z", dem, {}),
                         {"_JumpToContinuation"})
        self.assertTrue(M._equivalent("__CallSettingFrame@12", "__CallSettingFrame"))
        self.assertTrue(M._equivalent("`vector_constructor_iterator'", "vector_ctor_iterator"))
        self.assertTrue(M._equivalent("eh_vector_constructor_iterator", "eh_vector_ctor_iterator"))
        self.assertFalse(M._equivalent("WcsLen", "_wcslen"))                # letter case is part of a name
        self.assertFalse(M._equivalent("wcslen", "_wcslen"))                # the C name comes from spellings()
        self.assertFalse(M._equivalent("___free_lc_time", "__free_lc_time"))
        self.assertFalse(M._equivalent("JumpToContinuation", "_JumpToContinuation"))

    def test_alias_library_weak_externals(self):
        obj = coff([], [("__stricmp", 0, 0, 0x20, M.IMAGE_SYM_CLASS_EXTERNAL, b""),
                        ("_stricmp", 0, 0, 0, M.IMAGE_SYM_CLASS_WEAK_EXTERNAL, struct.pack("<II", 0, 3) + bytes(10))])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "OLDNAMES.LIB")
            path.write_bytes(archive([("stricmp.obj", b"\0\0" + obj[2:])]))     # OLDNAMES objects are machine 0
            self.assertEqual(M.load_aliases(path), {"__stricmp": {"_stricmp"}})
        self.assertIsNone(M.parse_coff("stricmp.obj", b"\0\0" + obj[2:]))  # never code to match
        self.assertIsNone(M.parse_coff("imp", struct.pack("<HHIIIHH", 0, 0xFFFF, 0, 0, 0, 0, 0), (0x14C, 0)))

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

    def alias_case(self, alias_body, body=b"\x33\xc0\x40\x40\x40\x40\x40\xc3"):
        target = self.LO + 0x300
        members, blobs = [], {target: body + b"\xcc" * 8}
        for i, symbol in enumerate(("_a", "_longalias")):
            va = self.LO + i * 0x100
            prefix = bytes(range(0x40 + i * 0x20, 0x54 + i * 0x20))
            obj = coff([(".text", COMDAT, prefix + b"\xe8\0\0\0\0\xc3", [(21, 1, M.REL_I386_REL32)])],
                       [(f"_caller{i}", 0, 1, FUNC, EXT, b""), (symbol, 0, 0, FUNC, EXT, b"")])
            members.append((f"caller{i}.obj", obj))
            blobs[va] = prefix + b"\xe8" + struct.pack("<i", target - (va + 25)) + b"\xc3"
        for symbol, data in [("_a", body), ("_rival", body), ("_longalias", alias_body)]:
            members.append((symbol + ".obj", coff([(".text", COMDAT, data, [])],
                                                [(symbol, 0, 1, FUNC, EXT, b"")])))
        return self.resolve(members, blobs, list(blobs)), target

    def test_reference_to_different_body_is_not_a_folded_alias(self):
        res, target = self.alias_case(b"\x90" * 8 + b"\xc3")
        self.assertEqual(res.decided[target]["how"], "called")
        self.assertNotIn("_longalias", res.decided[target].get("aliases", []))
        self.assertNotIn("_longalias", res.decided_syms[target])

    def test_matching_prefix_with_different_extent_is_not_identical_body(self):
        short = b"\x33\xc0\x40\x40\x40\x40\x40\xc3"
        res, target = self.alias_case(short + b"\xcc" * 4, short)
        self.assertEqual(res.decided[target]["how"], "called")
        self.assertNotIn("_longalias", res.decided[target].get("aliases", []))

    def test_equal_complete_body_and_references_support_folding(self):
        body = b"\x33\xc0\x40\x40\x40\x40\x40\xc3"
        res, target = self.alias_case(body, body)
        self.assertEqual(res.decided[target]["how"], "folded")
        self.assertEqual(res.decided[target]["aliases"], ["_longalias"])
        p, = M.proposals(res, {target: {"name": "old", "nameSource": "USER_DEFINED"}}, {})
        self.assertIn("linker-folded", p["tags"])
        self.assertIn("has the same bytes", p["proof"])

    def test_reference_only_alias_is_not_accepted_as_a_verified_saved_name(self):
        res, target = self.alias_case(b"\x90" * 8 + b"\xc3")
        verified = []
        p, = M.proposals(res, {target: {"name": "_longalias", "nameSource": "USER_DEFINED"}}, {}, verified=verified)
        self.assertEqual(p["proposed"], "_a")
        self.assertEqual(verified, [])
        self.assertNotIn("linker-folded", p["tags"])
        self.assertIn("not establish byte identity", p["proof"])

    def test_also_named_reference_does_not_certify_a_unique_body_alias(self):
        res, target = self.alias_case(b"\x90" * 8 + b"\xc3", BODY)
        # Force a uniquely identified body, as happens before the reference pool settles.
        cands = [c for c in res.cands[target] if c.fn.symbol == "_a"]
        res.decided[target] = {"how": "unique", "cands": cands}
        verified = []
        p, = M.proposals(res, {target: {"name": "_longalias", "nameSource": "USER_DEFINED"}}, {}, verified=verified)
        self.assertEqual(p["proposed"], "_a")
        self.assertNotIn("linker-folded", p["tags"])
        self.assertIn("not establish byte identity", p["proof"])

    def test_object_entry_aliases_are_proven_without_inventing_linker_folding(self):
        for offset, proven in [(0, True), (4, False)]:
            with self.subTest(offset=offset):
                obj = coff([(".text", COMDAT, BODY, [])],
                           [("_a", 0, 1, FUNC, EXT, b""), ("_alias", offset, 1, FUNC, EXT, b"")])
                lib = library([("same.obj", obj)])
                res = M.Resolver(lib, FakeImage(0x400000, {self.LO: BODY}), {}, self.LO, self.LO + 0x1000, [self.LO])
                # Use the whole-body candidate independently of the synthetic interior label's split.
                fn = M.ObjFunc("same.obj", 1, 0, len(BODY), "_a", EXT, True, 1)
                c = M.Candidate(self.LO, fn, len(BODY), own=M.own_symbols(lib.objects['same.obj'], fn, self.LO))
                res.cands[self.LO] = [c]
                res._accept(self.LO, "unique", [c]); res._settle()
                # A caller-derived address cannot turn an interior symbol into an entry alias.
                res.pool[("g", "_alias")] = self.LO
                verified = []
                proposed = M.proposals(res, {self.LO: {"name": "_alias", "nameSource": "USER_DEFINED"}}, {}, verified=verified)
                self.assertEqual(bool(verified), proven)
                p, = verified if proven else proposed
                self.assertNotIn("linker-folded", p["tags"])
                if proven:
                    self.assertIn("same section offset", p["proof"])
                    self.assertIn("_alias", res.decided_syms[self.LO])

    def test_folded_alias_extent_follows_the_compared_representative(self):
        short = b"\x33\xc0\x40\x40\x40\x40\x40\xc3"
        old, target = self.alias_case(short, short)
        anchor = bytes(range(0x80, 0x94)); av = target - 0x40
        raw = coff([(".text", COMDAT, anchor, []), (".text", COMDAT, short + b"\xcc" * 4, [])],
                   [("_anchor", 0, 1, FUNC, EXT, b""), ("_a", 0, 2, FUNC, EXT, b"")])
        obj = M.parse_coff("b.obj", raw)
        old.lib.objects['b.obj'] = obj; old.lib.functions.extend(M.object_functions(obj))
        old.image.mem[av-old.image.start:av-old.image.start+len(anchor)] = anchor
        res = M.Resolver(old.lib, old.image, {}, old.lo, old.hi, old.starts + [av])
        res.run()
        d = res.decided[target]; representative = res.representative(target, d)
        self.assertEqual((representative.fn.member, representative.fn.end-representative.fn.start), ("b.obj", 12))
        self.assertNotIn("_longalias", d.get("aliases", []))
        for late_ownership in (False, True):
            with self.subTest(late_ownership=late_ownership):
                if late_ownership:
                    d.update(how="folded", aliases=["_longalias"])
                p, = M.proposals(res, {target: {"name": "old", "nameSource": "USER_DEFINED"}}, {})
                self.assertEqual(p["how"], "called")
                self.assertNotIn("_longalias", p["alts"])
                self.assertNotIn("linker-folded", p["tags"])
                self.assertNotIn("members define it identically", p["proof"])
                self.assertNotIn("has the same bytes", p["proof"])
                self.assertIn("differing extents (8, 12 bytes)", p["proof"])
        res.decided_syms[target].add("_longalias")
        res.revalidate_aliases()
        self.assertEqual(res.decided[target]["how"], "called")
        self.assertNotIn("_longalias", res.decided_syms[target])

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
        # counts for the comments: one call site in one function; the caller's field is confirmed by the helper's match
        res.reference_index()
        self.assertEqual(res.sites([("g", "_helper")], 0x401100), (1, 1, 0))
        self.assertEqual(res.sites([("g", "_helper")], 0x401100, exclude=self.LO), (0, 0, 0))
        self.assertEqual(res.field_evidence(self.LO, res.decided[self.LO]["cands"][0]), (1, 1, 0, 0))

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

    def test_short_match_needs_ordered_neighbours(self):
        short = b"\x33\xc0\x40\x40\x40\x40\x40\x40\x40\xc3"
        long = bytes(range(0x10, 0x24))
        for ordered in (True, False):
            with self.subTest(ordered=ordered):
                parts = [("_long", long), ("_short", short)] if ordered else [("_short", short), ("_long", long)]
                obj = coff([(".text", COMDAT, body, []) for _name, body in parts],
                           [(name, 0, i, FUNC, EXT, b"") for i, (name, _body) in enumerate(parts, 1)])
                res = self.resolve([("o.obj", obj)], {self.LO: long + short}, [self.LO, self.LO + len(long)])
                self.assertEqual(res.decided[self.LO + len(long)]["how"],
                                 "unique-short" if ordered else "ambiguous")


class OwnerAndImportTests(unittest.TestCase):
    def resolver(self):
        lib = M.Library(Path("x.lib"), "0" * 64, {}, [])
        img = type("Img", (), {"imports": {0x5D81C8: "KERNEL32.dll!CreateDirectoryA"}})()
        return M.Resolver(lib, img, {}, 0, 1 << 32, [])

    def fn(self, member, symbol="_helper", start=0, order=2):
        return M.ObjFunc(member, order, start, start + 8, symbol, 3, False, order)

    def test_owner_by_references_folding_layout_and_none(self):
        res = self.resolver()
        d = {"cands": [M.Candidate(0x1000, self.fn("a.obj"), 8), M.Candidate(0x1000, self.fn("b.obj"), 8)]}
        self.assertEqual(res.owner(0x1000, d), (["a.obj", "b.obj"], None))
        res.pool[("l", "b.obj", "_helper", 1, 0)] = 0x1000                 # b.obj's own code calls it here
        self.assertEqual(res.owner(0x1000, d), (["b.obj"], "refs"))
        res.pool[("l", "a.obj", "_helper", 1, 0)] = 0x1000                 # and a.obj's too: folded copies
        self.assertEqual(res.owner(0x1000, d), (["a.obj", "b.obj"], "folded"))
        res.pool.clear()
        res.decided[0x0F00] = {"how": "unique", "cands": [M.Candidate(0x0F00, self.fn("a.obj", "_prev", order=1), 16)]}
        self.assertEqual(res.owner(0x1000, d), (["a.obj"], "layout"))
        one = {"cands": [M.Candidate(0x1000, self.fn("a.obj"), 8)]}
        self.assertEqual(res.owner(0x1000, one), (["a.obj"], "only"))

    def test_owner_layout_requires_every_available_order_bound(self):
        cases = [
            ("ordered predecessor", (1, 0), None, True),
            ("ordered successor", None, (3, 0), True),
            ("both ordered", (1, 0), (3, 0), True),
            ("reversed predecessor", (3, 0), None, False),
            ("reversed successor", None, (1, 0), False),
            ("contradictory successor", (1, 0), (1, 0), False),
            ("contradictory predecessor", (3, 0), (3, 0), False),
            ("ordered offsets", (2, 0), (2, 16), True),
            ("equal offset", (2, 8), None, False),
            ("reversed offsets", None, (2, 0), False),
        ]
        for label, left, right, fits in cases:
            with self.subTest(label=label):
                res = self.resolver()
                d = {"cands": [M.Candidate(0x1000, self.fn(m, start=8), 8) for m in ("a.obj", "b.obj")]}
                for va, pos in [(0x0F00, left), (0x1100, right)]:
                    if pos:
                        res.decided[va] = {"how": "unique", "cands": [M.Candidate(
                            va, self.fn("a.obj", "_anchor", start=pos[1], order=pos[0]), 8)]}
                self.assertEqual(res.owner(0x1000, d), (["a.obj"], "layout") if fits else (["a.obj", "b.obj"], None))

    def test_owner_layout_excludes_unresolved_or_folded_anchors(self):
        for how, positions in [("ambiguous", [0]), ("folded", [0]),
                               ("unique", [0, 8]), ("called-no-bytes", [])]:
            with self.subTest(how=how, positions=positions):
                res = self.resolver()
                d = {"cands": [M.Candidate(0x1000, self.fn(m), 8) for m in ("a.obj", "b.obj")]}
                res.decided[0x0F00] = {"how": how, "cands": [M.Candidate(
                    0x0F00, self.fn("a.obj", "_anchor", start=p, order=1), 8) for p in positions]}
                self.assertEqual(res.owner(0x1000, d), (["a.obj", "b.obj"], None))

    def test_two_ordered_members_do_not_prove_one_owner(self):
        res = self.resolver()
        d = {"cands": [M.Candidate(0x1000, self.fn(m), 8) for m in ("a.obj", "b.obj")]}
        res.decided[0x0F00] = {"how": "unique", "cands": [M.Candidate(0x0F00, self.fn("a.obj", order=1), 8)]}
        res.decided[0x1100] = {"how": "unique", "cands": [M.Candidate(0x1100, self.fn("b.obj", order=3), 8)]}
        self.assertEqual(res.owner(0x1000, d), (["a.obj", "b.obj"], None))
        res.pool[("l", "b.obj", "_helper", 2, 0)] = 0x1000
        self.assertEqual(res.owner(0x1000, d), (["b.obj"], "refs"))

    def test_folded_proof_uses_a_reference_supported_member(self):
        # a.obj has identical bytes, but only b.obj and c.obj have local callers here.
        obj = coff([(".text", COMDAT, BODY, [])], [("_helper", 0, 1, FUNC, STATIC, b"")])
        lib = library([(name, obj) for name in ("a.obj", "b.obj", "c.obj")])
        lib.pins = [{"label": name, "sha256": str(i) * 64, "tag": name} for i, name in enumerate(("A", "B", "C"))]
        lib.origin = {name: i for i, name in enumerate(("a.obj", "b.obj", "c.obj"))}
        res = M.Resolver(lib, FakeImage(0x400000, {0x401000: BODY}), {}, 0x401000, 0x402000, [0x401000])
        res.run()
        for name in ("b.obj", "c.obj"):
            res.pool[("l", name, "_helper", 1, 0)] = 0x401000
        rows = {0x401000: {"name": "old", "nameSource": "USER_DEFINED"}}
        p, = M.proposals(res, rows, {})
        self.assertIn("members b.obj, c.obj", p["proof"])
        self.assertIn("B (SHA-256 " + "1" * 64 + ")", p["proof"])
        self.assertIn("C (SHA-256 " + "2" * 64 + ")", p["proof"])
        self.assertIn("comparison below uses member b.obj", p["proof"])
        self.assertIn("B", p["tags"])
        self.assertIn("C", p["tags"])
        self.assertNotIn("static library A", p["proof"])

    def test_reference_index_uses_the_same_supported_representative(self):
        # All three bodies relocate to the same address but give the static target different local keys.
        va, target = 0x401000, 0x401100
        obj = coff([(".text", COMDAT, BODY + b"\xe8\0\0\0\0\xc3", [(21, 1, M.REL_I386_REL32)])],
                   [("_helper", 0, 1, FUNC, STATIC, b""), ("_target", 0, 0, FUNC, STATIC, b"")])
        lib = library([(name, obj) for name in ("a.obj", "b.obj", "c.obj")])
        body = BODY + b"\xe8" + struct.pack("<i", target - (va + 25)) + b"\xc3"
        res = M.Resolver(lib, FakeImage(0x400000, {va: body}), {}, va, 0x402000, [va])
        res.run()
        for name in ("b.obj", "c.obj"):
            res.pool[("l", name, "_helper", 1, 0)] = va
        res.reference_index()
        self.assertEqual(res.fields[(("l", "b.obj", "_target", 0, 0), target)], [(va, va + 21)])
        self.assertNotIn((("l", "a.obj", "_target", 0, 0), target), res.fields)

    def test_layout_representative_itself_must_fit_the_anchor(self):
        res = self.resolver()
        d = {"how": "called", "cands": [
            M.Candidate(0x1000, self.fn("a.obj", order=1), 8),
            M.Candidate(0x1000, self.fn("a.obj", order=3), 8),
            M.Candidate(0x1000, self.fn("b.obj", order=3), 8)]}
        res.decided[0x0F00] = {"how": "unique", "cands": [M.Candidate(0x0F00, self.fn("a.obj", "_anchor", order=2), 8)]}
        self.assertEqual(res.owner(0x1000, d), (["a.obj"], "layout"))
        self.assertEqual(res.representative(0x1000, d).fn.order, 3)

    def test_placed_proof_pin_follows_the_supported_caller(self):
        va, target = 0x401000, 0x401100
        members = []
        for member, symbol in [("a.obj", "_unused"), ("b.obj", "_target")]:
            obj = coff([(".text", COMDAT, BODY + b"\xe8\0\0\0\0\xc3", [(21, 1, M.REL_I386_REL32)])],
                       [("_helper", 0, 1, FUNC, STATIC, b""), (symbol, 0, 0, FUNC, EXT, b"")])
            members.append((member, obj))
        lib = library(members)
        lib.pins = [{"label": name, "sha256": str(i) * 64, "tag": name} for i, name in enumerate(("A", "B"))]
        lib.origin = {"a.obj": 0, "b.obj": 1}
        body = BODY + b"\xe8" + struct.pack("<i", target - (va + 25)) + b"\xc3"
        res = M.Resolver(lib, FakeImage(0x400000, {va: body}), {}, va, 0x402000, [va])
        res.search()
        res.decided[va] = {"how": "called", "cands": res.cands[va]}
        res.pool = {("l", "b.obj", "_helper", 1, 0): va, ("g", "_target"): target}
        rows = {target: {"name": "old", "nameSource": "USER_DEFINED"}}
        p, = M.proposals(res, rows, {})
        self.assertEqual(p["how"], "placed")
        self.assertIn("static library B (SHA-256 " + "1" * 64 + ")", p["proof"])
        self.assertNotIn("static library A", p["proof"])

    def test_import_symbols_must_land_on_their_own_slot(self):
        res = self.resolver()
        mkdir = M.Candidate(0x2000, self.fn("mkdir.obj", "__mkdir"), 8, implied={("g", "__imp__CreateDirectoryA@8"): 0x5D81C8})
        rmdir = M.Candidate(0x2000, self.fn("rmdir.obj", "__rmdir"), 8, implied={("g", "__imp__RemoveDirectoryA@4"): 0x5D81C8})
        self.assertEqual(res._score(mkdir)[1], 0)
        self.assertEqual(res._score(rmdir)[1], 1)


if __name__ == "__main__":
    unittest.main()
