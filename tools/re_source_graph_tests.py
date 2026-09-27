"""Focused tests for tools/re_source_graph.py on a synthetic source tree (no retail data)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import re_source_graph as G  # noqa: E402

HEADER = """class Thing {
public:
    static int Helper(int a);
    void Run(int x, int y);
    inline int Inl(int z) { return Leaf(z); }
    int Leaf(int z);
    void Over(int a);
    void Over(int a, int b);
};
"""
BODY = """int Thing::Helper(int a) { return a; }
void Thing::Run(int x, int y) { Helper(x); Inl(y); this->Over(x); }
int Thing::Leaf(int z) { return z; }
void Thing::Over(int a) { }
void Thing::Over(int a, int b) { Leaf(a); }
void Free(const unsigned short a, float * b) { Thing t; t.Leaf(1); }
"""
MAPPING = {0x1000: "Thing::Run", 0x2000: "Thing::Helper", 0x3000: "Thing::Leaf", 0x4000: "Thing::Over/1",
           0x5000: "Thing::Over/2", 0x6000: "Free"}


class SourceGraphTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        Path(self.tmp.name, "thing.h").write_text(HEADER)
        Path(self.tmp.name, "thing.cpp").write_text(BODY)
        self.src = G.index(Path(self.tmp.name), ("*.cpp", "*.h"), set())

    def tearDown(self):
        self.tmp.cleanup()

    def test_parameters_and_sizes(self):
        self.assertEqual(G.params("void"), [])
        self.assertEqual(G.params("int a, std::map<int, int> m, int b = 3"), ["int a", "std::map<int, int> m", "int b"])
        self.assertEqual(G.param_bytes("const unsigned short v0"), 4)
        self.assertEqual(G.param_bytes("NvEdgeInfoVec &edgeInfos"), 4)
        self.assertEqual(G.param_bytes("double d"), 8)
        self.assertEqual(G.param_bytes("unsigned__int64"), 8)
        self.assertEqual(G.param_bytes("unsignedlonglong"), 8)
        self.assertEqual(G.param_bytes("unsignedint"), 4)
        self.assertIsNone(G.param_bytes("unsignedMystery"))
        self.assertIsNone(G.param_bytes("FVector v"))

    def test_template_arguments_do_not_turn_aggregates_into_pointer_abis(self):
        for declaration in ('Aggregate<int*>', 'Aggregate<int&>', 'Outer<Inner<void*>>',
                            'int Owner::*', 'Aggregate<int*'):
            with self.subTest(declaration=declaration):
                self.assertIsNone(G.param_bytes(declaration+' value'))
                fn=G.E.SourceFunc('Thing::Run','test.h',1,'',[],[],args='int value',head='virtual '+declaration)
                self.assertIsNone(G.expected_pop(G.Source({},set(),set()),fn))
        for declaration in ('Aggregate<int*>*', 'Aggregate<int&>&', 'Outer<Inner<void*>>*'):
            with self.subTest(declaration=declaration):
                self.assertEqual(G.param_bytes(declaration+' value'),4)
                fn=G.E.SourceFunc('Thing::Run','test.h',1,'',[],[],args='int value',head='virtual '+declaration)
                self.assertEqual(G.expected_pop(G.Source({},set(),set()),fn),4)

    def test_name_candidates_withhold_overloads_duplicates_and_analytic_suffixes(self):
        functions = [{'address': hex(a), 'name': name} for a, name in [
            (1, 'Thing__Run'), (2, 'Thing__Over'), (3, 'Thing__Leaf_Approximation'),
            (4, 'Free'), (5, 'Thing__Helper'), (6, 'Thing__Helper')]]
        mapping, rows = G.map_names(functions, self.src)
        self.assertEqual(mapping, {1: 'Thing::Run', 4: 'Free'})
        self.assertEqual([r['status'] for r in rows], ['candidate', 'ambiguous-source-definition',
            'no-exact-source-definition', 'candidate', 'ambiguous-saved-name', 'ambiguous-saved-name'])
        with self.assertRaisesRegex(ValueError, 'duplicate function address'):
            G.map_names(functions + [functions[0]], self.src)

    def test_name_candidates_map_ctor_dtor_without_guessing_class_prefix(self):
        Path(self.tmp.name, 'construct.cpp').write_text('Thing::Thing() { }\nThing::~Thing() { }\n')
        src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
        mapping, _ = G.map_names([{'address': '0x10', 'name': 'Thing__ctor'},
                                  {'address': '0x20', 'name': 'Thing__dtor'},
                                  {'address': '0x30', 'name': 'Other__ctor'}], src)
        self.assertEqual(mapping, {0x10: 'Thing::Thing', 0x20: 'Thing::~Thing'})

    def test_inline_same_arity_overloads_are_retained_and_withheld(self):
        Path(self.tmp.name, 'over.h').write_text(
            'class Inline { public: int F(int a) { return a; }\n'
            'int F(float a) { return int(a); } };\n')
        src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
        mapping, rows = G.map_names([{'address': '0x10', 'name': 'Inline__F'}], src)
        self.assertEqual(mapping, {})
        self.assertEqual(rows[0]['status'], 'ambiguous-source-definition')
        self.assertEqual(len(rows[0]['candidates']), 2)

    def test_same_arity_overload_calls_are_possible_union_not_last_definition(self):
        Path(self.tmp.name, 'over.cpp').write_text(
            'void Thing::Same(int a) { Leaf(a); }\n'
            'void Thing::Same(float a) { Helper(int(a)); }\n')
        src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
        self.assertIsNone(G.resolve(src, 'Thing::Same/1'))
        self.assertEqual(src.calls['Thing::Same/1'], {'Leaf', 'Helper'})

    def test_identical_inline_const_overloads_stay_ambiguous(self):
        Path(self.tmp.name, 'const.h').write_text(
            'class Reader { public: int Read() { return 1; } '
            'int Read() const { return 1; } };\n')
        src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
        mapping, rows = G.map_names([{'address': '0x10', 'name': 'Reader__Read'}], src)
        self.assertEqual(mapping, {})
        self.assertEqual(rows[0]['status'], 'ambiguous-source-definition')
        self.assertEqual(len(rows[0]['candidates']), 2)
        self.assertIsNone(G.resolve(src, 'Reader::Read/0'))

    def test_elaborated_return_type_does_not_create_a_class_scope(self):
        Path(self.tmp.name, 'elaborated.h').write_text(
            'class Real { public: virtual class Shadow *GetShadow() { return 0; }\n'
            'static int Helper(int a) { return a; } };\n')
        src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
        keys = {f.key for group in src.funcs.values() for f in group}
        self.assertIn('Real::GetShadow', keys)
        self.assertIn('Real::Helper', keys)
        self.assertFalse(any(k.startswith('Shadow::') for k in keys))

    def test_source_pin_changes_with_content_or_filename_and_mapping_rejects_duplicates(self):
        root = Path(self.tmp.name)
        before = G.source_digest(root, ('*.cpp', '*.h'))
        p = root/'thing.cpp'
        p.write_text(BODY+'\n// changed\n')
        after = G.source_digest(root, ('*.cpp', '*.h'))
        self.assertNotEqual(before, after)
        p.rename(root/'other.cpp')
        self.assertNotEqual(after, G.source_digest(root, ('*.cpp', '*.h')))
        mapping = root/'map.tsv'
        mapping.write_text('address\tsource\n0x10\tThing::Run\n0x10\tThing::Leaf\n')
        with self.assertRaisesRegex(ValueError, 'duplicate address'):
            G.read_mapping(mapping)

    def test_statics_inline_and_overloads(self):
        self.assertIn(("Thing", "Helper"), self.src.statics)
        self.assertIn("Inl", self.src.inline)
        self.assertEqual(G.resolve(self.src, "Thing::Over/2").args.count(","), 1)
        self.assertIsNone(G.resolve(self.src, "Thing::Over"))            # ambiguous without /N
        self.assertEqual(G.reach(self.src, "Thing::Run"), {"Helper", "Inl", "Leaf", "Over"})   # Leaf through Inl

    def test_consistent_mapping(self):
        calls = {0x1000: [0x2000, 0x3000, 0x4000], 0x5000: [0x3000], 0x6000: [0x3000]}   # t.Leaf( is a call
        rets = {0x1000: {8}, 0x2000: {0}, 0x3000: {4}, 0x4000: {4}, 0x5000: {8}, 0x6000: {0}}
        report = G.check(MAPPING, calls, rets, self.src)
        self.assertEqual((report["edgesChecked"], report["contradicted"]), (5, 0))

    def test_contradictions_and_absent_calls(self):
        calls = {0x2000: [0x1000]}                                        # the source's Helper calls nothing
        rets = {0x4000: {8}}                                              # Over(int) pops 4, not 8
        report = G.check(MAPPING, calls, rets, self.src)
        by = {r["address"]: r for r in report["rows"]}
        self.assertIn("which the source does not call", by["0x00002000"]["contradictions"][0])
        self.assertIn("need 4", by["0x00004000"]["contradictions"][0])
        self.assertEqual(by["0x00005000"]["absent"], ["Leaf"])            # the program lacks Over/2 -> Leaf
        self.assertEqual(report["contradicted"], 2)


    def test_translation_unit_inlining_returns_and_folded_targets(self):
        Path(self.tmp.name, "more.h").write_text(
            "class Base { public: void Tick(int a); };\n"
            "class Kid : public Base { public: void Tick(int a); float Accel(); void Fwd(float v);\n"
            "  FVector Pos(); static int CALLBACK Proc(HWND h, UINT m, WPARAM w, LPARAM l); };\n")
        Path(self.tmp.name, "more.cpp").write_text(
            "void Base::Tick(int a) { }\n"
            "void Kid::Tick(int a) { Base::Tick(a); }\n"          # a base call with the same name
            "float Kid::Accel() { return Weapon(); }\n"
            "void Kid::Fwd(float v) { Accel(); }\n"               # Accel is in the same file: may be inlined
            "FVector Kid::Pos() { }\n"
            "int CALLBACK Kid::Proc(HWND h, UINT m, WPARAM w, LPARAM l) { return 0; }\n"
            "int Weapon() { return 1; }\n")
        src = G.index(Path(self.tmp.name), ("*.cpp", "*.h"), set())
        mapping = {0x10: "Base::Tick", 0x20: "Kid::Tick", 0x30: "Weapon", 0x40: "Kid::Fwd", 0x50: "Kid::Pos",
                   0x60: "Kid::Proc", 0x70: "Kid::Accel"}
        calls = {0x20: [0x10], 0x40: [0x30, 0x70]}
        rets = {0x50: {4}, 0x60: {16}, 0x40: {4}}
        report = G.check(mapping, calls, rets, src, {0x70: 6}, small=8)
        by = {r["address"]: r for r in report["rows"]}
        self.assertEqual(report["contradicted"], 0, [r for r in report["rows"] if r["contradictions"]])
        self.assertIsNone(by["0x00000050"]["expectedPop"])              # type name alone does not prove aggregate ABI
        self.assertEqual(by["0x00000060"]["expectedPop"], 16)              # static, but CALLBACK is __stdcall
        self.assertEqual(by["0x00000040"]["smallTargets"], ["0x00000070 Kid::Accel"])
        self.assertEqual(report["edgesChecked"], 2)

    def test_scalar_typedef_and_declared_enum_do_not_invent_hidden_return_pointer(self):
        Path(self.tmp.name, 'grade.h').write_text('enum EQuitType { Done, Failed };\n')
        Path(self.tmp.name, 'grade.cpp').write_text(
            'WCHAR Career::Grade(float f) { return 0; }\n'
            'EQuitType Game::Run(int level) { return Done; }\n'
            'UnknownResult Game::Unresolved(int x) { }\n')
        src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
        self.assertEqual(G.expected_pop(src, G.resolve(src, 'Career::Grade')), 4)
        self.assertEqual(G.expected_pop(src, G.resolve(src, 'Game::Run')), 4)
        self.assertIsNone(G.expected_pop(src, G.resolve(src, 'Game::Unresolved')))


    def test_implicit_calls(self):
        Path(self.tmp.name, "imp.cpp").write_text(
            "Holder::Holder() { }\nvoid Maker::Make() { Holder *h = new Holder; }\nvoid Maker::Plain() { }\n")
        src = G.index(Path(self.tmp.name), ("*.cpp", "*.h"), set())
        mapping = {0x10: "Holder::Holder", 0x20: "Maker::Make", 0x30: "Maker::Plain", 0x40: "Mem::Alloc"}
        calls = {0x20: [0x40, 0x10], 0x30: [0x10]}
        report = G.check(mapping, calls, {}, src, implicit={"Alloc"})
        by = {r["address"]: r for r in report["rows"]}
        self.assertEqual(by["0x00000020"]["implicitTargets"], ["0x00000040 Mem::Alloc", "0x00000010 Holder::Holder"])
        self.assertEqual(by["0x00000020"]["contradictions"], [])
        self.assertIn("Holder::Holder", by["0x00000030"]["contradictions"][0])   # Plain never mentions Holder


if __name__ == "__main__":
    unittest.main()
