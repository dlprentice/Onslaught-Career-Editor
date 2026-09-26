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
        self.assertIsNone(G.param_bytes("FVector v"))

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
        self.assertEqual(by["0x00000050"]["expectedPop"], 4)               # the hidden result pointer
        self.assertEqual(by["0x00000060"]["expectedPop"], 16)              # static, but CALLBACK is __stdcall
        self.assertEqual(by["0x00000040"]["smallTargets"], ["0x00000070 Kid::Accel"])
        self.assertEqual(report["edgesChecked"], 2)


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
