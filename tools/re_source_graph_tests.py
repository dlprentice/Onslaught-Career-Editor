"""Focused tests for tools/re_source_graph.py on a synthetic source tree (no retail data)."""
from __future__ import annotations

import copy
import hashlib
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

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


class ProgramFactsTests(unittest.TestCase):
    def facts(self, raw, *, address=0x1000, extra=(), **changes):
        section = SimpleNamespace(start=0x1000, size=len(raw), raw=raw,
                                  characteristics=0x20000000)
        image = SimpleNamespace(base=0x1000,
            read=lambda a, n: raw[a-0x1000:a-0x1000+n],
            section_of=lambda a: section if 0x1000 <= a < 0x1000+len(raw) else None)
        fields = dict(va=0x1000, lo=0x1000, hi=0x1000+len(raw)-1,
                      declared_hi=0x1000+len(raw)-1, body_ranges=1, body_bytes=len(raw))
        fields.update(changes)
        fn = SimpleNamespace(**fields)
        # Deliberately wrong/empty cached instructions must never hide the CALL.
        prog = SimpleNamespace(by_va={fn.va: fn}, funcs=[fn, *extra], body=lambda f: [])
        with patch.object(G.E, 'load_or_build', return_value=(image, None)), \
                patch.object(G.E, 'load_functions', return_value=[]), \
                patch.object(G.E, 'Program', return_value=prog):
            return G.program_facts(Path('unused'), Path('unused'), {address})

    def test_entry_decode_recovers_call_and_complete_size_without_cached_instructions(self):
        # CALL 0x1100; RET 8. This first call is absent from the synthetic cache.
        calls, rets, sizes = self.facts(bytes.fromhex('e8fb000000c20800'))
        self.assertEqual(calls, {0x1000: [0x1100]})
        self.assertEqual(rets, {0x1000: {8}})
        self.assertEqual(sizes, {0x1000: 8})

    def test_missing_and_interior_mapping_addresses_are_not_containing_functions(self):
        for address in (0x1001, 0x2000):
            with self.subTest(address=address), self.assertRaisesRegex(ValueError, 'function entry'):
                self.facts(bytes.fromhex('90c3'), address=address)

    def test_overlapping_export_ownership_is_rejected(self):
        other = SimpleNamespace(va=0xfff, lo=0xfff, hi=0x1000, declared_hi=0x1000)
        with self.assertRaisesRegex(ValueError, 'overlapping exported ownership'):
            self.facts(bytes.fromhex('90c3'), extra=(other,))

    def test_duplicate_entries_cannot_be_hidden_by_the_address_index(self):
        other = SimpleNamespace(va=0x1000, lo=0x1000, hi=0x1001, declared_hi=0x1001)
        with self.assertRaisesRegex(ValueError, 'duplicate exported function entries'):
            self.facts(bytes.fromhex('90c3'), extra=(other,))

    def test_incomplete_or_noncontiguous_export_extents_are_rejected(self):
        for changes in (dict(body_ranges=2), dict(body_bytes=1),
                        dict(declared_hi=0x1002), dict(lo=0xfff)):
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, 'exported extent'):
                self.facts(bytes.fromhex('90c3'), **changes)

    def test_truncated_instruction_does_not_become_empty_evidence(self):
        with self.assertRaisesRegex(ValueError, 'invalid or data instruction'):
                self.facts(b'\xe8')


class DirectCallWitnessTests(unittest.TestCase):
    def fixture(self, *, setup=bytes.fromhex('6a0753b900600000'), target_raw=bytes.fromhex('8b442404c20800'),
                caller_source='void Caller::Run(int x) { device.Play(x,7); }',
                target_source='void Device::Play(int x, int y) {}', header=''):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        path = root/'sample.cpp'
        path.write_text(caller_source+'\n'+target_source+'\n')
        (root/'sample.h').write_text(header)
        prefix = bytes.fromhex('538b5c2408')
        call = 0x1000+len(prefix)+len(setup)
        raw = prefix+setup+b'\xe8'+struct.pack('<i',0x2000-call-5)+bytes.fromhex('5bc20400')
        blocks = {0x1000:raw,0x2000:target_raw}
        def read(address,count):
            for start,data in blocks.items():
                if start<=address and address+count<=start+len(data):
                    return data[address-start:address-start+count]
            return b''
        def section(address):
            return next((SimpleNamespace(start=start,size=len(data),raw=data,characteristics=0x20000000)
                         for start,data in blocks.items() if start<=address<start+len(data)),None)
        functions = [SimpleNamespace(va=start,lo=start,hi=start+len(data)-1,
                         declared_hi=start+len(data)-1,body_ranges=1,body_bytes=len(data),thunk=False)
                     for start,data in blocks.items()]
        image = SimpleNamespace(sha256=hashlib.sha256(raw+target_raw).hexdigest(),read=read,section_of=section)
        prog = SimpleNamespace(img=image,model=SimpleNamespace(refs_to={}),funcs=functions,
                               by_va={f.va:f for f in functions})
        def pin(address,count):
            return {'address':hex(address),'bytes':count,'sha256':hashlib.sha256(read(address,count)).hexdigest()}
        src = G.index(root,('*.cpp','*.h'),set())
        def source(key):
            f = G.resolve(src,key)
            # Ambiguity tests deliberately preserve the initial key/line pin;
            # the checker must resolve it afresh and refuse it.
            line = f.line if f else (1 if key=='Caller::Run' else caller_source.count('\n')+2)
            return {'file':'sample.cpp','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                    'function':key,'line':line}
        witness = {'caller':pin(0x1000,len(raw))|{'source':source('Caller::Run')},
                   'target':pin(0x2000,len(target_raw))|{'source':source('Device::Play')},
                   'callAddress':hex(call),'window':pin(0x1005,len(setup)+5),
                   'sourceCall':'device.Play(x,7);',
                   'sourceLine':next((i for i,line in enumerate(path.read_text().splitlines(),1)
                                      if 'device.Play(x,7);' in line),1),
                   'receiver':'constant32:0x00006000',
                   'arguments':[{'sourceParameter':'int x','sourceArgument':'x','stackOffset':4,
                                 'pushAddress':'0x1007','value':'window.ebx'},
                                {'sourceParameter':'int y','sourceArgument':'7','stackOffset':8,
                                 'pushAddress':'0x1005','value':'constant32:0x00000007'}],
                   'externalBindings':[{'register':'ebx','meaning':'selected source x',
                                        'evidence':'reviewed load of caller stack argument',
                                        'spans':[pin(0x1001,4)]}],
                   'identityEvidence':'reviewed caller and object identities; synthetic fixture',
                   'sourceArgumentEvidence':'reviewed x transport and literal 7; synthetic fixture'}
        return prog,root,{'specimenSha256':image.sha256,'calls':[witness]}

    def check(self, fixture):
        return G.direct_call_witnesses(*fixture)

    def test_exact_direct_transport_uses_no_saved_names(self):
        fixture = self.fixture()
        report = self.check(fixture)
        self.assertEqual(report['checkedCalls'],1)
        row = report['rows'][0]
        self.assertEqual(row['target'],'0x00002000')
        self.assertEqual(row['returnPop'],8)
        self.assertEqual([p['value'] for p in row['arguments']],['window.ebx','constant32:0x00000007'])
        self.assertIn('independently reviewed',report['limits'])

    def test_pushed_value_survives_later_register_reassignment(self):
        fixture = self.fixture(setup=bytes.fromhex('6a0753bb55000000b900600000'))
        report = self.check(fixture)
        self.assertEqual(report['rows'][0]['arguments'][0]['value'],'window.ebx')

    def test_zero_argument_member_transport_is_checked(self):
        fixture = self.fixture(setup=bytes.fromhex('b900600000'),target_raw=b'\xc3',
            caller_source='void Caller::Run(int x) { device.Play(); }',target_source='void Device::Play() {}')
        witness=fixture[2]['calls'][0]
        witness.update(sourceCall='device.Play();',arguments=[],externalBindings=[])
        self.assertEqual(self.check(fixture)['rows'][0]['returnPop'],0)

    def test_member_expression_is_an_explicit_reviewed_binding_not_a_template(self):
        fixture=self.fixture(caller_source='void Caller::Run(int x) { device.Play(event->value,7); }')
        witness=fixture[2]['calls'][0]
        witness['sourceCall']='device.Play(event->value,7);'
        witness['arguments'][0]['sourceArgument']='event->value'
        witness['externalBindings'][0]['meaning']='reviewed field value (synthetic premise)'
        self.assertEqual(self.check(fixture)['checkedCalls'],1)

    def test_expression_operators_are_not_silently_treated_as_parameters(self):
        fixture=self.fixture(caller_source='void Caller::Run(int x) { device.Play(x+1,7); }')
        fixture[2]['calls'][0]['sourceCall']='device.Play(x+1,7);'
        with self.assertRaisesRegex(ValueError,'expression is unsupported'):
            self.check(fixture)

    def test_source_statement_cannot_be_reached_only_transitively_or_inside_a_literal(self):
        for caller in ['void Caller::Run(int x) { Inline(x); }\nvoid Inline(int x) { device.Play(x,7); }',
                       'void Caller::Run(int x) { const char *text="device.Play(x,7);"; }',
                       'void Caller::Run(int x) { otherdevice.Play(x,7); }',
                       'void Caller::Run(int x) { outer.device.Play(x,7); }',
                       'void Caller::Run(int x) { outer . device.Play(x,7); }',
                       'void Caller::Run(int x) { outer -> device.Play(x,7); }',
                       'void Caller::Run(int x) { outer :: device.Play(x,7); }',
                       'void Caller::Run(int x) { device.Play(x,7); device.Play(x,7); }']:
            with self.subTest(caller=caller),self.assertRaisesRegex(ValueError,'absent, repeated or a literal'):
                self.check(self.fixture(caller_source=caller))

    def test_unresolved_and_disabled_source_preprocessing_is_not_selected(self):
        for directive in ['#if TARGET == PC','#if 0']:
            caller=directive+'\nvoid Caller::Run(int x) { device.Play(x,7); }\n#endif'
            with self.subTest(directive=directive),self.assertRaisesRegex(ValueError,'preprocessing'):
                self.check(self.fixture(caller_source=caller))

    def test_inactive_or_unresolved_target_definition_is_not_a_verified_interface(self):
        for directive in ['#if TARGET == PC','#if 0']:
            target=directive+'\nvoid Device::Play(int x,int y) {}\n#endif'
            with self.subTest(directive=directive),self.assertRaisesRegex(ValueError,'preprocessing'):
                self.check(self.fixture(target_source=target))

    def conditional_fixture(self):
        fixture=self.fixture(target_source='#if TARGET == PC\nvoid Device::Play(int x, int y) {}\n#endif')
        witness=fixture[2]['calls'][0]
        fixture[2]['sourceConditions']=[{'file':'sample.cpp','line':2,'directive':'#if TARGET == PC',
            'sha256':witness['target']['source']['sha256'],'value':True,
            'evidence':'independently reviewed reference branch selection, not a recovered compiler define',
            'spans':[{k:v for k,v in witness['target'].items() if k!='source'}]}]
        return fixture

    def test_explicit_condition_is_a_reported_reviewed_premise_not_an_implicit_flag(self):
        fixture=self.conditional_fixture()
        self.assertEqual(self.check(fixture)['sourceConditionPremises'],fixture[2]['sourceConditions'])
        fixture[2]['sourceConditions'][0]['value']=False
        with self.assertRaisesRegex(ValueError,'preprocessing'):
            self.check(fixture)

    def test_source_selection_pin_failures_cannot_override_preprocessing(self):
        for change in ('line','hash','directive','type','evidence','span','duplicate','unused'):
            with self.subTest(change=change):
                fixture=self.conditional_fixture();conditions=fixture[2]['sourceConditions'];c=conditions[0]
                if change=='line':c['line']=1
                if change=='hash':c['sha256']='0'*64
                if change=='directive':c['directive']='#if OTHER == PC'
                if change=='type':c['value']=1
                if change=='evidence':c['evidence']=''
                if change=='span':c['spans'][0]['sha256']='0'*64
                if change=='duplicate':conditions.append(copy.deepcopy(c))
                if change=='unused':conditions.append(dict(c,file='unused.cpp'))
                with self.assertRaises(ValueError):self.check(fixture)

    def test_known_macro_method_receiver_or_argument_rewrite_is_withheld(self):
        for definition in ('Play(x,y) Other(x,y)','device other','x other'):
            caller='#define '+definition+'\nvoid Caller::Run(int x) { device.Play(x,7); }\n#undef '+definition.split('(')[0].split()[0]
            with self.subTest(definition=definition),self.assertRaisesRegex(ValueError,'known macro'):
                self.check(self.fixture(caller_source=caller))
        with self.assertRaisesRegex(ValueError,'known macro'):
            self.check(self.fixture(header='#define Play(x,y) Other(x,y)'))

    def test_source_cleanup_divergence_static_and_unknown_abis_are_refused(self):
        cases=[({'target_raw':bytes.fromhex('8b442404c20400')},'cleanup differs'),
               ({'target_source':'Unknown Device::Play(int x, int y) {}'},'ABI is unresolved'),
               ({'header':'class Device { static void Play(int x, int y); };'},'non-static'),
               ({'target_source':'void Device::Play(int x, int y) {}\nvoid Device::Play(int x,int y) const {}'},'ambiguous')]
        for options,message in cases:
            with self.subTest(options=options),self.assertRaisesRegex(ValueError,message):
                self.check(self.fixture(**options))

    def test_interior_entry_can_bypass_setup_even_when_the_window_hash_matches(self):
        for offset in (0x1007,0x1008,0x100d):
            fixture=self.fixture();fixture[0].model.refs_to={offset:[('jcc',0x3000)]}
            with self.subTest(offset=offset),self.assertRaisesRegex(ValueError,'interior entry'):
                self.check(fixture)

    def test_byte_source_argument_and_review_pins_fail_closed(self):
        changes=['specimen','caller-bytes','target-bytes','source-hash','source-key','source-line',
                 'call-line','wrong-method','wrong-target','window-hash','window-interior',
                 'receiver','source-argument','argument-order','push-site','stack-offset','value',
                 'binding-missing','binding-unused','binding-hash','identity-premise','argument-premise',
                 'callee-thunk','duplicate-functions','overlapping-functions','duplicate-site','empty']
        for change in changes:
            with self.subTest(change=change):
                fixture=self.fixture();prog,_,document=fixture;w=document['calls'][0]
                if change=='specimen':document['specimenSha256']='0'*64
                if change=='caller-bytes':w['caller']['sha256']='0'*64
                if change=='target-bytes':w['target']['bytes']-=1
                if change=='source-hash':w['caller']['source']['sha256']='0'*64
                if change=='source-key':w['caller']['source']['function']='Caller::Other'
                if change=='source-line':w['target']['source']['line']+=1
                if change=='call-line':w['sourceLine']+=1
                if change=='wrong-method':w['sourceCall']='device.Other(x,7);'
                if change=='wrong-target':w['callAddress']='0x1008'
                if change=='window-hash':w['window']['sha256']='0'*64
                if change=='window-interior':w['window']['address']='0x1006';w['window']['bytes']-=1
                if change=='receiver':w['receiver']='window.ecx'
                if change=='source-argument':w['arguments'][0]['sourceArgument']='7'
                if change=='argument-order':w['arguments'].reverse()
                if change=='push-site':w['arguments'][0]['pushAddress']='0x1005'
                if change=='stack-offset':w['arguments'][0]['stackOffset']=8
                if change=='value':w['arguments'][0]['value']='constant32:0x00000055'
                if change=='binding-missing':w['externalBindings']=[]
                if change=='binding-unused':w['externalBindings'][0]['register']='eax'
                if change=='binding-hash':w['externalBindings'][0]['spans'][0]['sha256']='0'*64
                if change=='identity-premise':w['identityEvidence']=''
                if change=='argument-premise':w['sourceArgumentEvidence']=''
                if change=='callee-thunk':prog.by_va[0x2000].thunk=True
                if change=='duplicate-functions':prog.funcs.append(copy.copy(prog.funcs[0]))
                if change=='overlapping-functions':
                    other=copy.copy(prog.funcs[0]);other.va-=1;other.lo-=1;prog.funcs.append(other)
                if change=='duplicate-site':document['calls'].append(copy.deepcopy(w))
                if change=='empty':document['calls']=[]
                with self.assertRaises(ValueError):self.check(fixture)


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
        self.assertEqual(G.params('void (*hook)(int), int count = Make(1, 2), int last = 0'),
                         ['void (*hook)(int)', 'int count', 'int last'])
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

    def test_constructor_arity_ignores_initializers_and_keeps_overloads_ambiguous(self):
        Path(self.tmp.name, 'construct.cpp').write_text(
            'Bag::Bag() : first(NULL), size(0) { }\n'
            'Bag::Bag(const Bag& other) : first(NULL), size(0) { }\n')
        src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
        self.assertIsNone(G.resolve(src, 'Bag::Bag'))
        empty, copy = G.resolve(src, 'Bag::Bag/0'), G.resolve(src, 'Bag::Bag/1')
        self.assertIsNotNone(empty)
        self.assertIsNotNone(copy)
        self.assertEqual((G.expected_pop(src, empty), G.expected_pop(src, copy)), (0, 4))
        mapping, rows = G.map_names([{'address': '0x10', 'name': 'Bag__ctor'}], src)
        self.assertEqual(mapping, {})
        self.assertEqual(rows[0]['status'], 'ambiguous-source-definition')

    def test_inline_same_arity_overloads_are_retained_and_withheld(self):
        Path(self.tmp.name, 'over.h').write_text(
            'class Inline { public: int F(int a) { return a; }\n'
            'int F(float a) { return int(a); } };\n')
        src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
        mapping, rows = G.map_names([{'address': '0x10', 'name': 'Inline__F'}], src)
        self.assertEqual(mapping, {})
        self.assertEqual(rows[0]['status'], 'ambiguous-source-definition')
        self.assertEqual(len(rows[0]['candidates']), 2)

    def test_constructor_initializer_cast_cannot_admit_a_wrong_stack_pop(self):
        Path(self.tmp.name, 'construct.cpp').write_text('Bag::Bag() : ptr((void*)0) { }\n')
        src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
        fn = G.resolve(src, 'Bag::Bag')
        self.assertEqual(G.expected_pop(src, fn), 0)
        bad = G.check({0x10: 'Bag::Bag'}, {0x10: []}, {0x10: {4}}, src, {0x10: 24}, 16, set())
        good = G.check({0x10: 'Bag::Bag'}, {0x10: []}, {0x10: {0}}, src, {0x10: 24}, 16, set())
        self.assertEqual((bad['contradicted'], good['contradicted']), (1, 0))

    def test_defaults_cannot_hide_a_following_parameter(self):
        for args in ('const char *text="<", int flags=0', 'int count=(1<2), int flags=0',
                     'int count=object->field, int flags=0', 'int count=Make(1, 2), int flags=0'):
            with self.subTest(args=args):
                Path(self.tmp.name, 'defaults.cpp').write_text(f'void Bag::Set({args}) {{ }}\n')
                src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
                fn = G.resolve(src, 'Bag::Set')
                self.assertEqual(G.expected_pop(src, fn), 8)
                report = G.check({0x10: 'Bag::Set'}, {0x10: []}, {0x10: {4}}, src, {0x10: 24}, 16, set())
                self.assertEqual(report['contradicted'], 1)
        for args in ('int count=Factory<int, int>(), int flags=0', 'int count=1<2, int flags=0'):
            with self.subTest(args=args):
                Path(self.tmp.name, 'defaults.cpp').write_text(f'void Bag::Set({args}) {{ }}\n')
                src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
                self.assertIsNone(G.resolve(src, 'Bag::Set'))

    def test_initializer_calls_are_retained_and_literal_calls_are_excluded(self):
        Path(self.tmp.name, 'construct.cpp').write_text(
            'int Factory() { return 1; }\n'
            'Bag::Bag() : value(Factory()) { Log("Free()"); }\n')
        src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
        self.assertEqual(src.calls['Bag::Bag'], {'Factory'})
        report = G.check({0x10: 'Bag::Bag', 0x20: 'Factory'}, {0x10: [0x20], 0x20: []},
                         {0x10: {0}, 0x20: {0}}, src, {0x10: 24, 0x20: 24}, 16, set())
        self.assertEqual(report['contradicted'], 0)

    def test_refused_default_does_not_make_another_overload_unique(self):
        for text in ('void Bag::Set(int x) {}\nvoid Bag::Set(float x=1<2) {}\n',
                     'void Bag::Set(int x) {}\nvoid Bag::Set(int x=Factory<int,int>()) {}\n',
                     'class Bag { public: void Set(int x) {}\nvoid Set(float x=1<2) {} };\n'):
            with self.subTest(text=text):
                Path(self.tmp.name, 'refused.cpp').write_text(text + 'void Other::Set(int x) {}\n')
                src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
                self.assertIsNone(G.resolve(src, 'Bag::Set'))
                self.assertIsNone(G.resolve(src, 'Bag::Set/1'))
                self.assertIsNone(G.resolve(src, 'Set'))
                mapping, _ = G.map_names([{'address': '0x10', 'name': 'Bag__Set'}], src)
                self.assertEqual(mapping, {})

    def test_inline_constructor_and_body_use_the_same_balanced_parser(self):
        Path(self.tmp.name, 'inline.h').write_text(
            'class Bag { public: Bag() : value(Thing::Helper(1)) { Log("}"); }\n'
            'int Get() { char x = \'{\'; return value; }\n'
            'Bag& operator = (const Bag& copy) { value = copy.value; return *this; } };\n')
        src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
        ctor = G.resolve(src, 'Bag::Bag')
        self.assertIsNotNone(ctor)
        self.assertEqual((ctor.args, G.expected_pop(src, ctor)), ('', 0))
        self.assertEqual(src.calls['Bag::Bag'], {'Helper'})
        self.assertIn('return value;', G.resolve(src, 'Bag::Get').body)
        self.assertEqual(G.expected_pop(src, G.resolve(src, 'Bag::Get')), 0)
        self.assertIsNotNone(G.resolve(src, 'Bag::operator='))
        self.assertEqual((ctor.line, G.resolve(src, 'Bag::Get').line,
                          G.resolve(src, 'Bag::operator=').line), (1, 2, 3))

    def test_inline_access_label_preserves_scalar_and_qualified_return_types(self):
        Path(self.tmp.name, 'inline.h').write_text(
            'class Inline { public: int Get(int n) { return n; }\n'
            'private: ns::Item* Item() { return 0; } };\n')
        src = G.index(Path(self.tmp.name), ('*.cpp', '*.h'), set())
        self.assertEqual(G.expected_pop(src, G.resolve(src, 'Inline::Get')), 4)
        self.assertIn('ns::Item*', G.resolve(src, 'Inline::Item').head)
        self.assertEqual(G.expected_pop(src, G.resolve(src, 'Inline::Item')), 0)

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
