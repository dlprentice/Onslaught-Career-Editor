"""Focused tests for the pure helpers of tools/re_name_evidence.py (synthetic inputs only)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import re_name_evidence as E  # noqa: E402


class FakeImage:
    base = 0x400000

    def section_of(self, va):
        return object() if 0x401000 <= va < 0x700000 else None


class HelperTests(unittest.TestCase):
    def test_demangle_type(self):
        self.assertEqual(E.demangle_type(".?AVCBattleEngine@@"), "CBattleEngine")
        self.assertEqual(E.demangle_type(".?AUCRenderMethod@@"), "CRenderMethod")
        self.assertEqual(E.demangle_type(".?AVInner@Outer@@"), "Outer::Inner")

    def test_split_name(self):
        self.assertEqual(E.split_name("CPlayer__SetIsGod"), ("CPlayer", "SetIsGod"))
        self.assertEqual(E.split_name("CFoo__Bar_T3_00401000"), ("CFoo", "Bar_T3_00401000"))
        self.assertEqual(E.split_name("__ftol"), (None, "__ftol"))
        self.assertEqual(E.split_name("FUN_00401000"), (None, "FUN_00401000"))

    def test_tiny_names_agree_or_disagree_with_bodies(self):
        self.assertEqual(E.check_tiny_name("ReturnTrue", "const:1:ret0"), "agree")
        self.assertEqual(E.check_tiny_name("ReturnTrue", "const:0:ret0"), "disagree")
        self.assertEqual(E.check_tiny_name("ReturnField1c", "field:1c:ret0"), "agree")
        self.assertEqual(E.check_tiny_name("ReturnField1c", "field:20:ret0"), "disagree")
        self.assertEqual(E.check_tiny_name("NoOp_Ret8", "noop:ret8"), "agree")
        self.assertIsNone(E.check_tiny_name("Update", "noop:ret0"))
        self.assertIsNone(E.check_tiny_name("ReturnTrue", None))

    def test_source_index_finds_definitions_literals_and_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "Thing.cpp").write_text(
                "// header comment with CThing::Fake() { }\n"
                "void\tCThing::Load(int a)\n{\n\tTRACE(\"loading %d\\n\", a);\n\tif (a) { Open(a, \"x.dat\"); }\n}\n"
                "CThing::~CThing()\n{\n}\n")
            funcs = E.index_source(Path(tmp))
        keys = {f.key: f for f in funcs}
        self.assertEqual(sorted(keys), ["CThing::Load", "CThing::~CThing"])
        load = keys["CThing::Load"]
        self.assertEqual((load.file, load.line), ("Thing.cpp", 2))
        self.assertEqual(load.literals, ["loading %d\n", "x.dat"])
        self.assertIn(("Open", "x.dat", 1), load.lit_calls)
        self.assertEqual(E.source_key_to_name("CThing::~CThing"), "CThing__dtor_CThing")
        self.assertEqual(E.source_key_to_name("CGame::LoadLevel"), "CGame__LoadLevel")

    def test_c_unescape_keeps_escaped_backslashes(self):
        self.assertEqual(E.c_unescape(r"C:\\dev\\a.cpp\n"), "C:\\dev\\a.cpp\n")

    def test_instruction_references(self):
        img = FakeImage()
        self.assertEqual(E.insn_refs(E.Insn(0x401000, 5, "call", "0x426fd0"), img), [("call", 0x426FD0)])
        self.assertEqual(E.insn_refs(E.Insn(0x401000, 2, "jne", "0x401020"), img), [("jcc", 0x401020)])
        self.assertEqual(E.insn_refs(E.Insn(0x401000, 6, "mov", "eax,DWORD PTR ds:0x662ab0"), img),
                         [("mem", 0x662AB0)])
        self.assertEqual(E.insn_refs(E.Insn(0x401000, 5, "push", "0x63fb24"), img), [("imm", 0x63FB24)])
        self.assertEqual(E.insn_refs(E.Insn(0x401000, 5, "push", "0x29"), img), [])


if __name__ == "__main__":
    unittest.main()
