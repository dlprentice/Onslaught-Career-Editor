"""Focused tests for the pure helpers of tools/re_name_evidence.py (synthetic inputs only)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import re_name_evidence as E  # noqa: E402


class FakeImage:
    base = 0x400000

    def section_of(self, va):
        return object() if 0x401000 <= va < 0x700000 else None


class HelperTests(unittest.TestCase):
    def test_folded_body_new_derived_slot_is_not_erased_by_inherited_slots(self):
        # Retail RET4 at 004014c0: CThing has 59 slots, while the same body
        # also occupies CComplexThing's new slot 63. Synthetic addresses here.
        prog = E.Program.__new__(E.Program)
        prog.bases = {'Base': [('Base', 0)],
                      'Derived': [('Derived', 0), ('Base', 0)]}
        prog.fixed_bases = prog.bases
        prog.slots = {0x1000: [('Base', 0, 6, 0x2000),
                             ('Derived', 0, 6, 0x3000),
                             ('Derived', 0, 63, 0x3000)]}
        self.assertEqual(prog.defining_classes(SimpleNamespace(va=0x1000)),
                         {'Base', 'Derived'})
        prog.slots[0x1000].pop()
        self.assertEqual(prog.defining_classes(SimpleNamespace(va=0x1000)), {'Base'})

    def test_inherited_slots_require_composed_subobject_offsets(self):
        prog = E.Program.__new__(E.Program)
        prog.bases = {'Base': [('Base', 0)],
                      'Derived': [('Derived', 0), ('Base', 16)]}
        prog.fixed_bases = prog.bases
        prog.slots = {1: [('Base', 8, 3, 100), ('Derived', 24, 3, 200)]}
        self.assertEqual(prog.defining_classes(SimpleNamespace(va=1)), {'Base'})
        prog.slots[1][1] = ('Derived', 8, 3, 200)
        self.assertEqual(prog.defining_classes(SimpleNamespace(va=1)), {'Base', 'Derived'})
        prog.bases['Derived'][1] = ('Base', -8)
        prog.slots[1][1] = ('Derived', 0, 3, 200)
        self.assertEqual(prog.defining_classes(SimpleNamespace(va=1)), {'Base', 'Derived'})

    def test_rtti_virtual_base_nonnegative_mdisp_is_not_fixed_offset_evidence(self):
        descriptor = lambda name, pdisp, vdisp: SimpleNamespace(
            class_name=name, mdisp=0, pdisp=pdisp, vdisp=vdisp)
        census = SimpleNamespace(type_descriptors={}, slots=[], vtables={}, cols={}, hierarchies={1:
            SimpleNamespace(root_class='Derived', rows=[
                SimpleNamespace(descriptor=descriptor('Derived', -1, 0)),
                SimpleNamespace(descriptor=descriptor('Base', 0, 4))])})
        with patch('re_rtti_vtables.parse_rtti', return_value=census):
            rtti = E.scan_rtti(SimpleNamespace(data=b'synthetic'))
        self.assertIn(('Base', 0), rtti.class_bases['Derived'])
        self.assertNotIn(('Base', 0), rtti.fixed_bases['Derived'])
        prog = E.Program.__new__(E.Program)
        prog.bases, prog.fixed_bases = rtti.class_bases, rtti.fixed_bases
        prog.slots = {1: [('Base', 0, 2, 100), ('Derived', 0, 2, 200)]}
        self.assertEqual(prog.defining_classes(SimpleNamespace(va=1)), {'Base', 'Derived'})
    def test_matching_class_and_compatible_graph_do_not_verify_method_identity(self):
        fn = SimpleNamespace(va=0x401000, name='Thing__Run', source='USER_DEFINED')
        src = [E.SourceFunc('Thing::Run', 'Thing.cpp', 1, '', [], [], 2, '', 'void')]
        prog = SimpleNamespace(funcs=[fn], defining_classes=lambda f: {'Thing'},
                               slots={fn.va: [('Thing', 0, 0, 0x600000)]})
        graph = {'rows': [{'address': '0x00401000', 'contradictions': [], 'absent': []}]}
        with patch.object(E, 'file_line_anchors', return_value={}), \
             patch.object(E, 'string_anchors', return_value=({}, {})), \
             patch.object(E, 'tiny_semantics', return_value=None):
            result = E.audit(prog, src, graph)
        self.assertEqual(result[0]['verdict'], 'unsupported')
        self.assertEqual(result[0]['against'], '')

    def test_folded_derived_override_holder_is_not_contradicted_or_verified(self):
        fn = SimpleNamespace(va=0x401000, name='Derived__Run', source='USER_DEFINED')
        src = [E.SourceFunc('Derived::Run', 'Thing.cpp', 1, '', [], [], 2, '', 'void')]
        prog = E.Program.__new__(E.Program)
        prog.funcs = [fn]
        prog.bases = {'Derived': [('Derived', 0), ('Base', 0)], 'Base': [('Base', 0)]}
        prog.fixed_bases = prog.bases
        prog.slots = {fn.va: [('Base', 0, 2, 0x600000), ('Derived', 0, 2, 0x600100)]}
        self.assertEqual(prog.defining_classes(fn), {'Base'})
        with patch.object(E, 'file_line_anchors', return_value={}), \
             patch.object(E, 'string_anchors', return_value=({}, {})), \
             patch.object(E, 'tiny_semantics', return_value=None):
            row = E.audit(prog, src)[0]
        self.assertEqual(row['verdict'], 'unsupported')
        self.assertEqual(row['against'], '')

    def test_graph_contradictions_must_target_this_saved_identity(self):
        fn = SimpleNamespace(va=0x401000, name='Base__Run', source='USER_DEFINED')
        src = [E.SourceFunc('Base::Run', 'Thing.cpp', 1, '', [], [], 2, '', 'void')]
        prog = SimpleNamespace(funcs=[fn], defining_classes=lambda f: set(), slots={})
        for source, wanted in [('Base::Different', 'unsupported'),
                               ('Base::Run/0', 'unsupported'),
                               ('Base::Run', 'contradicted')]:
            with self.subTest(source=source), \
                 patch.object(E, 'file_line_anchors', return_value={}), \
                 patch.object(E, 'string_anchors', return_value=({}, {})), \
                 patch.object(E, 'tiny_semantics', return_value=None):
                graph = {'rows': [{'address': hex(fn.va), 'source': source,
                                   'contradictions': ['ret size differs']}]}
                row = E.audit(prog, src, graph)[0]
                self.assertEqual(row['verdict'], wanted)
                self.assertEqual(row['against'], 'ret size differs' if wanted == 'contradicted' else '')

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
        self.assertEqual((load.file, load.line, load.end_line), ("Thing.cpp", 2, 6))
        self.assertEqual(load.literals, ["loading %d\n", "x.dat"])
        self.assertIn(("Open", "x.dat", 1), load.lit_calls)
        self.assertEqual(E.source_key_to_name("CThing::~CThing"), "CThing__dtor")
        self.assertEqual(E.source_key_to_name("CThing::CThing"), "CThing__ctor")
        self.assertEqual(E.source_key_to_name("CGame::LoadLevel"), "CGame__LoadLevel")

    def test_strip_comments_reads_separators_and_literals_in_order(self):
        text = ('//****************\nvoid A::F()\n{\n\tLog("a // b /* c");\n}\n/* x\ny */\n'
                '//****************\nvoid A::G() { }\n')
        out = E.strip_comments(text)
        self.assertIn("void A::F()", out)
        self.assertIn('Log("a // b /* c");', out)
        self.assertIn("void A::G()", out)
        self.assertEqual(out.count("\n"), text.count("\n"))

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
