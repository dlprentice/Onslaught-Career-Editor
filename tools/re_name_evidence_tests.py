"""Focused tests for the pure helpers of tools/re_name_evidence.py (synthetic inputs only)."""
from __future__ import annotations

import sys
import hashlib
import struct
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


class HeaderVtableTests(unittest.TestCase):
    def parse(self, text, undefined=frozenset()):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'types.h').write_text(text)
            return E.header_classes(Path(tmp), set(undefined))

    def test_declared_order_destructor_position_and_implicit_override(self):
        classes = self.parse('class Camera { public: virtual int Pos(); virtual ~Camera() {} };\n'
                             'class View : public Camera { int Pos(); };\n')
        layouts, _ = E.header_layouts(classes)
        self.assertEqual([m.name for m in layouts['Camera']], ['Pos', '~Camera'])
        self.assertEqual([m.owner for m in layouts['View']], ['View', 'View'])
        self.assertTrue(layouts['View'][1].implicit)

    def test_parameter_type_overload_is_new_not_override_and_case_matters(self):
        classes = self.parse('class Base { public: virtual void Copy(Base* value); virtual void Shutdown(); };\n'
                             'class Child : public Base { virtual void Copy(Child* value); virtual void ShutDown(); };\n')
        layouts, _ = E.header_layouts(classes)
        self.assertEqual([(m.name, m.parameters) for m in layouts['Child']],
                         [('Copy', ('Base*',)), ('Shutdown', ()), ('Copy', ('Child*',)), ('ShutDown', ())])

    def test_const_overloads_and_unknown_order_do_not_collapse(self):
        classes = self.parse('class Reader { virtual int Read(); virtual int Read() const; };\n')
        layouts, issues = E.header_layouts(classes)
        self.assertNotIn('Reader', layouts)
        self.assertIn('new virtual overload ordering requires byte witnesses', issues['Reader'])

    def test_earlier_nonvirtual_declaration_cannot_silently_reorder_new_groups(self):
        for text in ['class A { void F(int); virtual void G(); virtual void F(); };',
                     'class Base { virtual void F(int); };\n'
                     'class A : public Base { void F(int); virtual void G(); virtual void F(float); };']:
            with self.subTest(text=text):
                layouts,issues=E.header_layouts(self.parse(text))
                self.assertNotIn('A',layouts)
                self.assertTrue(any('group order' in i for i in issues['A']))

    def test_method_name_macro_is_not_treated_as_a_source_identity(self):
        classes=self.parse('#define RUN Other\nclass A { virtual void RUN(); };')
        layouts,issues=E.header_layouts(classes)
        self.assertNotIn('A',layouts)
        self.assertIn('unexpanded method-name macro RUN',issues['A'])

    def test_constructor_does_not_override_same_named_base_method(self):
        classes=self.parse('class Base { virtual void Child(); };\nclass Child : public Base { Child(); };')
        layouts,_=E.header_layouts(classes)
        self.assertEqual([(m.owner,m.name) for m in layouts['Child']],[('Base','Child')])

    def test_member_template_does_not_supply_an_override(self):
        classes=self.parse('typedef int T; class Base { virtual void F(T); };\n'
                           'class Child : public Base { template<class T> void F(T); };')
        layouts,issues=E.header_layouts(classes)
        self.assertNotIn('Child',layouts)
        self.assertIn('member template declaration',issues['Child'])

    def test_missing_macros_bases_and_multiple_inheritance_stay_open(self):
        classes = self.parse('DECLARE_THING_CLASS(Thing, Missing)\npublic: virtual void Move(); };\n'
                             'class Child : public Thing {};\nclass Mixed : public A, public B {};\n')
        layouts, issues = E.header_layouts(classes)
        self.assertFalse(layouts)
        self.assertIn('unexpanded class macro DECLARE_THING_CLASS', issues['Thing'])
        self.assertIn('unresolved base Thing', issues['Child'])
        self.assertIn('multiple inheritance', issues['Mixed'])

    def test_conditionals_are_explicit_and_unknown_method_is_withheld(self):
        text = '#ifndef TYPES_H\n#define TYPES_H\nclass Base {\n#ifdef EDITORBUILD\nvirtual void Save();\n#endif\nvirtual void Load();\n};\n#endif\n'
        layouts, _ = E.header_layouts(self.parse(text, {'EDITORBUILD'}))
        self.assertEqual([m.name for m in layouts['Base']], ['Load'])
        layouts, issues = E.header_layouts(self.parse(text))
        self.assertNotIn('Base', layouts)
        self.assertTrue(any('conditional method Save' == i for i in issues['Base']))

    def test_defined_guard_is_true_inside_its_own_body(self):
        text = '#ifndef TYPES_H\n#define TYPES_H\nclass Base {\n#ifdef TYPES_H\nvirtual void Run();\n#endif\n};\n#endif\n'
        layouts, _ = E.header_layouts(self.parse(text))
        self.assertEqual([m.name for m in layouts['Base']], ['Run'])

    def test_constructor_initializer_and_literal_braces_do_not_hide_virtuals(self):
        classes = self.parse('class A { public: A(int x) : value(x) {}\n'
                             'virtual const char* Text() { return "} fake {"; }\nvirtual void Run(); int value; };\n')
        layouts, issues = E.header_layouts(classes)
        self.assertEqual(issues, {})
        self.assertEqual([m.name for m in layouts['A']], ['Text', 'Run'])

    def test_types_keep_pointee_const_but_ignore_parameter_names_and_value_const(self):
        for p, t in [('const Foo* arg', 'constFoo*'), ('const Foo& arg', 'constFoo&'),
                     ('const float value', 'float'), ('unsigned count', 'unsigned'),
                     ('unsigned int', 'unsignedint'), ('class Thing*', 'Thing*')]:
            with self.subTest(p=p): self.assertEqual(E._header_type(p), t)
        self.assertIsNone(E._header_type('void (*callback)(int)'))

    def fixture(self):
        classes = self.parse('class Base { public: virtual void Run(); };\nclass Child : public Base {};\n')
        base = SimpleNamespace(va=0x600000, klass='Base', offset=0, slots=[0x401000])
        child = SimpleNamespace(va=0x600100, klass='Child', offset=0, slots=[0x401100])
        raw = {base.va:struct.pack('<I',base.slots[0]), child.va:struct.pack('<I',child.slots[0]),
               0x401000:b'\xc3', 0x401100:b'\xc3'}
        img = SimpleNamespace(sha256='f'*64, read=lambda va,n:raw.get(va,b'')[:n],
                              u32=lambda va:struct.unpack('<I',raw[va])[0])
        rtti = SimpleNamespace(vtables=[base,child],class_bases={'Base':[('Base',0)],'Child':[('Child',0),('Base',0)]})
        rtti.fixed_bases=rtti.class_bases
        model=SimpleNamespace(rtti=rtti,insns=[])
        fn=lambda va:SimpleNamespace(va=va,lo=va,hi=va)
        prog=E.Program(img,model,[fn(0x401000),fn(0x401100)])
        anchors={'specimenSha256':img.sha256,'anchors':[{'class':'Base','table':'0x00600000','offset':0,'slot':0,
                  'target':'0x00401000','method':'Run','parameters':[],
                  'body':{'address':'0x00401000','bytes':1,'sha256':hashlib.sha256(b'\xc3').hexdigest()},
                  'evidence':'synthetic witness, not a retail identity'}]}
        return classes,prog,anchors

    def test_layout_count_and_inherited_target_mismatches_are_not_fitted(self):
        classes,prog,_=self.fixture()
        report=E.align_header_vtables(prog,classes)
        self.assertEqual(report['rows'][1]['status'],'inherited-target-discrepancy')
        prog.model.rtti.vtables[0].slots.append(0x401000)
        report=E.align_header_vtables(prog,classes)
        self.assertEqual(report['rows'],[])
        self.assertTrue(any('base layout not admitted' in ' '.join(r['reasons']) for r in report['withheld']))

    def test_source_root_cannot_hide_a_retail_base(self):
        classes,prog,_=self.fixture()
        prog.bases['Base'].append(('MissingBase',0))
        report=E.align_header_vtables(prog,classes)
        self.assertEqual(report['rows'],[])
        self.assertTrue(any('ancestor sets differ' in ' '.join(r['reasons']) for r in report['withheld']))

    def test_anchor_propagation_requires_bytes_source_and_fixed_ancestry(self):
        classes,prog,anchors=self.fixture()
        report=E.propagate_vtable_anchors(prog,classes,anchors)
        self.assertEqual([r['status'] for r in report['rows']],['anchored-method-candidate']*2)
        prog.fixed_bases={'Base':[('Base',0)],'Child':[('Child',0)]}
        self.assertEqual(len(E.propagate_vtable_anchors(prog,classes,anchors)['rows']),1)
        anchors['anchors'][0]['body']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'body hash mismatch'):
            E.propagate_vtable_anchors(prog,classes,anchors)

    def test_unmapped_holder_and_unknown_source_method_are_withheld(self):
        classes,prog,anchors=self.fixture()
        prog.slots[0x401100].append(('Unrelated',0,5,0x600200))
        report=E.propagate_vtable_anchors(prog,classes,anchors)
        self.assertEqual(report['rows'][1]['status'],'unmapped-vtable-aliases')
        anchors['anchors'][0]['method']='GuessedName'
        with self.assertRaisesRegex(ValueError,'source declaration is absent'):
            E.propagate_vtable_anchors(prog,classes,anchors)

    def test_anchor_must_be_virtual_unconditional_and_unambiguous(self):
        for text in ['class Base { void Run(); };',
                     'class Base {\n#ifdef UNKNOWN\nvirtual void Run();\n#endif\n};',
                     'class Base { virtual void Run(); };\nclass Base { virtual void Run(); };']:
            with self.subTest(text=text):
                _,prog,anchors=self.fixture()
                with self.assertRaises(ValueError):
                    E.propagate_vtable_anchors(prog,self.parse(text),anchors)

    def test_inherited_virtual_anchor_requires_retail_ancestry(self):
        _,prog,anchors=self.fixture()
        classes=self.parse('class Ancestor { virtual void Run(); };\nclass Base : public Ancestor { void Run(); };')
        with self.assertRaisesRegex(ValueError,'retail RTTI ancestry'):
            E.propagate_vtable_anchors(prog,classes,anchors)
        prog.fixed_bases['Base'].append(('Ancestor',0))
        self.assertEqual(len(E.propagate_vtable_anchors(prog,classes,anchors)['rows']),2)

    def test_same_body_at_different_anchored_methods_is_ambiguous(self):
        _,prog,anchors=self.fixture()
        classes=self.parse('class Base { virtual void Run(); virtual void Stop(); };')
        for table in prog.model.rtti.vtables: table.slots.append(table.slots[0])
        words={t.va+4*i:target for t in prog.model.rtti.vtables for i,target in enumerate(t.slots)}
        prog.img.u32=lambda va:words[va]
        prog=E.Program(prog.img,prog.model,prog.funcs)
        anchors['anchors'].append(anchors['anchors'][0] | {'slot':1,'method':'Stop'})
        result=E.propagate_vtable_anchors(prog,classes,anchors)
        self.assertEqual([r['status'] for r in result['rows']],['conflicting-method-identities']*2)

    def test_secondary_slot_uses_composed_fixed_offset(self):
        classes,prog,anchors=self.fixture()
        base,child=prog.model.rtti.vtables
        base.offset,child.offset=8,20
        prog.model.rtti.fixed_bases={'Base':[('Base',0)],'Child':[('Child',0),('Base',12)]}
        prog=E.Program(prog.img,prog.model,prog.funcs)
        anchors['anchors'][0]['offset']=8
        self.assertEqual(len(E.propagate_vtable_anchors(prog,classes,anchors)['rows']),2)
        child.offset=8
        prog=E.Program(prog.img,prog.model,prog.funcs)
        self.assertEqual(len(E.propagate_vtable_anchors(prog,classes,anchors)['rows']),1)

    def test_repeated_retail_subobjects_do_not_match_single_chain(self):
        classes,prog,_=self.fixture()
        prog.bases['Child'].append(('Base',4))
        report=E.align_header_vtables(prog,classes)
        self.assertFalse(any(r['class']=='Child' for r in report['rows']))

    def test_batch_abi_refuses_mismatched_cleanup_and_unknown_tail(self):
        for insns, flag in [([E.Insn(0x401100,3,'ret','0x4')], 'return cleanup disagrees'),
                            ([E.Insn(0x401100,2,'jmp','eax')], 'indirect tail target')]:
            with self.subTest(flag=flag):
                classes,prog,anchors=self.fixture()
                prog.by_va[0x401100].hi=insns[-1].va+insns[-1].size-1
                prog.body=lambda f:[E.Insn(f.va,1,'ret','')] if f.va==0x401000 else insns
                report=E.vtable_abi_admission(prog,classes,anchors,E.propagate_vtable_anchors(prog,classes,anchors))
                self.assertEqual(report['rows'][0]['status'],'mechanical-checks-pass')
                self.assertEqual(report['rows'][1]['status'],'withheld')
                self.assertTrue(any(flag in s for s in report['rows'][1]['flags']))

    def test_batch_abi_does_not_hide_a_direct_tail_return_mismatch(self):
        classes,prog,anchors=self.fixture()
        prog.by_va[0x401000].hi+=2
        prog.by_va[0x401100].hi+=4
        prog.body=lambda f:([E.Insn(f.va,3,'ret','0x4')] if f.va==0x401000
                            else [E.Insn(f.va,5,'jmp','0x401000')])
        report=E.vtable_abi_admission(prog,classes,anchors,E.propagate_vtable_anchors(prog,classes,anchors))
        self.assertEqual([r['status'] for r in report['rows']],['withheld']*2)

    def test_aggregate_cleanup_cannot_be_inferred_from_a_stub_or_matching_returns(self):
        # A RET-only seed may be purecall glue, not an implementation of the
        # source's hidden-result interface. Neither matching nor differing
        # descendant cleanup establishes that convention.
        for seed_pop, child_pop in [(0, 0), (0, 4), (4, 4)]:
            with self.subTest(seed=seed_pop, child=child_pop):
                _,prog,anchors=self.fixture()
                classes=self.parse('class Base { virtual FVector Run(); };\n'
                                   'class Child : public Base {};\n')
                def body(fn):
                    n=seed_pop if fn.va==0x401000 else child_pop
                    return [E.Insn(fn.va,3 if n else 1,'ret',hex(n) if n else '')]
                for fn in prog.funcs: fn.hi=fn.va+body(fn)[0].size-1
                prog.body=body
                report=E.vtable_abi_admission(prog,classes,anchors,
                    E.propagate_vtable_anchors(prog,classes,anchors))
                self.assertEqual([r['status'] for r in report['rows']],['withheld']*2)
                self.assertTrue(all('source interface cleanup needs an independent ABI witness'
                                    in r['flags'] for r in report['rows']))

    def test_destructor_source_does_not_certify_a_deleting_entry(self):
        for cleanup in (0, 4):
            with self.subTest(cleanup=cleanup):
                _,prog,anchors=self.fixture()
                classes=self.parse('class Base { virtual ~Base() {} };\n'
                                   'class Child : public Base {};\n')
                anchors['anchors'][0]['method']='~Base'
                for fn in prog.funcs: fn.hi=fn.va+(2 if cleanup else 0)
                prog.body=lambda fn:[E.Insn(fn.va,3 if cleanup else 1,
                                          'ret',hex(cleanup) if cleanup else '')]
                report=E.vtable_abi_admission(prog,classes,anchors,
                    E.propagate_vtable_anchors(prog,classes,anchors))
                self.assertEqual([r['status'] for r in report['rows']],['withheld']*2)
                self.assertTrue(all('destructor entry kind needs an independent ABI witness'
                                    in r['flags'] for r in report['rows']))

    def test_batch_constant_control_uses_actual_override_not_base_default(self):
        classes,prog,anchors=self.fixture()
        classes['Base'].methods[0].body='return TRUE;'
        for fn in prog.funcs:fn.hi+=2
        prog.body=lambda f:[E.Insn(f.va,2,'xor','eax,eax'),E.Insn(f.va+2,1,'ret','')]
        report=E.vtable_abi_admission(prog,classes,anchors,E.propagate_vtable_anchors(prog,classes,anchors))
        self.assertIn('tiny constant contradicts source implementation',report['rows'][0]['flags'])
        self.assertEqual(report['rows'][1]['status'],'mechanical-checks-pass')

    def test_batch_abi_rejects_unproven_control_flow_and_stack_manipulation(self):
        cases=[([('pop','eax',1),('push','0x0',2),('push','eax',1),('jmp','0x401000',5)],'stack-neutral'),
               ([('mov','esp,eax',2),('ret','',1)],'opaque stack-pointer'),
               ([('xchg','eax,esp',2),('ret','',1)],'opaque stack-pointer'),
               ([('mov','sp,ax',3),('ret','',1)],'opaque stack-pointer'),
               ([('(bad)','',1),('ret','',1)],'invalid or data'),
               ([('jmp','0x401107',2),('jmp','0x401000',5),('pop','eax',1),
                 ('push','0x0',2),('push','eax',1),('jmp','0x401102',2)],'stack-neutral'),
               ([('je','0x401104',2),('ret','',1),('nop','',1),('nop','',1)],'fallthrough'),
               ([('loop','0x402000',2),('ret','',1)],'conditional branch outside'),
               ([('jmp','0x401101',2),('ret','',1)],'instruction boundary')]
        for body,wanted in cases:
            with self.subTest(flag=wanted):
                classes,prog,anchors=self.fixture(); insns=[]; cursor=0x401100
                for op,arg,size in body:insns.append(E.Insn(cursor,size,op,arg));cursor+=size
                prog.by_va[0x401100].hi=cursor-1
                prog.body=lambda f:[E.Insn(f.va,1,'ret','')] if f.va==0x401000 else insns
                report=E.vtable_abi_admission(prog,classes,anchors,E.propagate_vtable_anchors(prog,classes,anchors))
                self.assertTrue(any(wanted in x for x in report['rows'][1]['flags']), report)

    def test_batch_abi_withholds_bounding_boxes_clipped_by_another_function(self):
        classes,prog,anchors=self.fixture()
        prog.body=lambda f:[E.Insn(f.va,1,'ret','')]
        prog.by_va[0x401100].declared_hi=0x401200
        report=E.vtable_abi_admission(prog,classes,anchors,E.propagate_vtable_anchors(prog,classes,anchors))
        self.assertEqual(report['rows'][0]['status'],'mechanical-checks-pass')
        self.assertIn('noncontiguous or clipped function boundary',report['rows'][1]['flags'])

    def test_proposals_do_not_pick_one_folded_owner_or_move_a_name_between_targets(self):
        fn=lambda va,name:SimpleNamespace(va=va,name=name)
        prog=SimpleNamespace(funcs=[fn(1,'Old1'),fn(2,'Other__Run'),fn(3,'Old3'),fn(4,'A__Run')])
        prog.by_va={f.va:f for f in prog.funcs}
        row=lambda va,owners,holders:dict(target=hex(va),leastDerivedHolders=owners,
            uses=[dict(method='Run',parameters=[],qualifiers='',**{'class':c}) for c in holders])
        propagated={'rows':[row(1,['A'],['A']),row(2,['A','Other'],['A','Other']),
                            row(3,['A','Other'],['A','Other'])]}
        admission={'rows':[dict(target=hex(i),status='mechanical-checks-pass',flags=[]) for i in (1,2,3)]}
        report=E.vtable_name_proposals(prog,propagated,admission)['rows']
        self.assertEqual([r['status'] for r in report],['withheld','keep','withheld'])
        self.assertIn('already belongs',report[0]['flags'][0])
        self.assertIn('unique RTTI',report[2]['flags'][0])

    def test_proposals_reject_competing_new_names_and_do_not_ignore_abi_flags(self):
        prog=SimpleNamespace(funcs=[SimpleNamespace(va=i,name='Old'+str(i)) for i in (1,2,3)])
        prog.by_va={f.va:f for f in prog.funcs}
        propagated={'rows':[dict(target=hex(i),leastDerivedHolders=['Base'],
            uses=[dict(method='Run',parameters=[],qualifiers='',**{'class':'Base'})]) for i in (1,2,3)]}
        admission={'rows':[dict(target=hex(i),status='withheld' if i==3 else 'mechanical-checks-pass',
                              flags=['bad RET'] if i==3 else []) for i in (1,2,3)]}
        report=E.vtable_name_proposals(prog,propagated,admission)['rows']
        self.assertEqual([r['status'] for r in report],['withheld']*3)
        self.assertEqual(report[0]['flags'],['multiple targets propose the same name'])
        self.assertEqual(report[2]['flags'],['bad RET'])


if __name__ == "__main__":
    unittest.main()
