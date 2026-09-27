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


class CommonInterfaceTests(unittest.TestCase):
    def fixture(self, parameter='MissingEnum', result='void'):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root/'types.h').write_text('class Child : public Base { public: virtual '
                                  + result + ' Run(' + parameter + ' state); };\n')
        source = root/'Caller.cpp'
        source.write_text('void Host::Tick()\n{\n pages[index]->Run(state);\n}\n')
        classes = E.header_classes(root, set())
        method = classes['Child'].methods[0]
        tables = [SimpleNamespace(va=0x600000, klass='Base', offset=0, slots=[0x401000]),
                  SimpleNamespace(va=0x600100, klass='Child', offset=0, slots=[0x401100]),
                  SimpleNamespace(va=0x600200, klass='Sibling', offset=0, slots=[0x401200])]
        raw = {t.va:struct.pack('<I',t.slots[0]) for t in tables}
        raw.update({a:b'\xc2\x04\x00' for a in (0x401000,0x401100,0x401200)})
        raw[0x402000] = b'\x8b\x0f\x50\x8b\x11\xff\x12\xc3'
        memory = {a+i:v for a,b in raw.items() for i,v in enumerate(b)}
        read = lambda a,n:bytes(memory.get(a+i,0) for i in range(n))
        img = SimpleNamespace(sha256='f'*64,read=read,u32=lambda a:struct.unpack('<I',read(a,4))[0])
        insns = [E.Insn(a,3,'ret','0x4') for a in (0x401000,0x401100,0x401200)]
        insns += [E.Insn(0x402000,2,'mov','ecx,DWORD PTR [edi]'),
                  E.Insn(0x402002,1,'push','eax'), E.Insn(0x402003,2,'mov','edx,DWORD PTR [ecx]'),
                  E.Insn(0x402005,2,'call','DWORD PTR [edx]'),E.Insn(0x402007,1,'ret','')]
        bases = {'Base':[('Base',0)],'Child':[('Child',0),('Base',0)],
                 'Sibling':[('Sibling',0),('Base',0)]}
        model = SimpleNamespace(rtti=SimpleNamespace(vtables=tables,class_bases=bases,fixed_bases=bases),insns=insns)
        funcs = [SimpleNamespace(va=a,lo=a,hi=a+len(b)-1) for a,b in raw.items() if a<0x600000]
        prog = E.Program(img,model,funcs)
        span = lambda a,n:dict(address=hex(a),bytes=n,sha256=hashlib.sha256(read(a,n)).hexdigest())
        anchor = dict(table=hex(tables[1].va),offset=0,slot=0,target='0x00401100',method='Run',
                      parameters=[parameter],qualifiers='',sourceFile=method.file,sourceLine=method.line,
                      body=span(0x401100,3),evidence='Synthetic derived-method identity')
        anchor['class'] = 'Child'
        anchor['interfaceDispatch'] = dict(table=hex(tables[0].va),evidence='Synthetic call correspondence',
            receiverEvidence='Synthetic page-array/object binding, independently reviewed',
            receiverSpans=[span(0x402000,2)], caller=span(0x402000,8),window=span(0x402000,7),
            receiverLoad='0x00402000',callAddress='0x00402005',parameterStackBytes=[4],
            source=dict(file='Caller.cpp',sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        function='Host::Tick',line=3,call='pages[index]->Run(state);'))
        anchor['interfaceDispatch']['class'] = 'Base'
        document = dict(specimenSha256=img.sha256,anchors=[anchor])
        return root,classes,prog,document

    def test_missing_base_header_can_use_reviewed_common_dispatch_without_inventing_layout(self):
        root,classes,prog,doc = self.fixture()
        self.assertNotIn('Base',classes)
        report = E.propagate_vtable_anchors(prog,classes,doc,root)
        self.assertEqual(len(report['rows']),3)
        self.assertEqual([r['status'] for r in report['rows']],['anchored-method-candidate']*3)
        admitted = E.vtable_abi_admission(prog,classes,doc,report,root)
        self.assertEqual([r['observedReturnPop'] for r in admitted['rows']],[[4]]*3)
        self.assertEqual([r['status'] for r in admitted['rows']],['mechanical-checks-pass']*3)
        import re_source_graph as G
        self.assertIsNone(G.param_bytes('MissingEnum'))  # no global width rule

    def test_direct_base_and_exact_table_relationship_are_required(self):
        for change in ('repeated','virtual','offset','extra-slot','unrelated','no-virtual'):
            with self.subTest(change=change):
                root,classes,prog,doc = self.fixture()
                if change=='repeated': prog.bases['Child'].append(('Base',4))
                if change=='virtual': prog.fixed_bases=dict(prog.fixed_bases,Child=[('Child',0)])
                if change=='offset': prog.model.rtti.vtables[0].offset=4
                if change=='extra-slot': prog.model.rtti.vtables[0].slots.append(0x401000)
                if change=='unrelated': classes['Child'].bases=['Other']
                if change=='no-virtual': classes['Child'].methods[0].virtual=False
                with self.assertRaises(ValueError): E.propagate_vtable_anchors(prog,classes,doc,root)

    def test_source_call_and_all_byte_pins_are_required(self):
        for change in ('source-hash','source-call','source-owner','source-line','decl-line','caller',
                       'window','receiver-span','no-receiver-span','source-path'):
            with self.subTest(change=change):
                root,classes,prog,doc = self.fixture();a=doc['anchors'][0];w=a['interfaceDispatch']
                if change=='source-hash':w['source']['sha256']='0'*64
                if change=='source-call':w['source']['call']='pages[index]->Stop(state);'
                if change=='source-owner':w['source']['function']='Host::Unknown'
                if change=='source-line':w['source']['line']=100
                if change=='decl-line':a['sourceLine']+=1
                if change in ('caller','window'):w[change]['sha256']='0'*64
                if change=='receiver-span':w['receiverSpans'][0]['sha256']='0'*64
                if change=='no-receiver-span':w['receiverSpans']=[]
                if change=='source-path':w['source']['file']='../Caller.cpp'
                with self.assertRaises(ValueError):E.propagate_vtable_anchors(prog,classes,doc,root)

    def test_transport_refuses_wrong_slot_clobbered_receiver_and_nonlocal_flow(self):
        for change in ('wrong-slot','wrong-receiver','wrong-vptr','branch','call','wrong-load',
                       'wrong-push','width','missing-arg','out-of-body','clipped-body'):
            with self.subTest(change=change):
                root,classes,prog,doc = self.fixture();w=doc['anchors'][0]['interfaceDispatch']
                ins=prog.model.insns
                if change=='wrong-slot':ins[-2].ops='DWORD PTR [edx+0x4]'
                if change=='wrong-receiver':ins[-3].ops='ecx,DWORD PTR [ecx]'
                if change=='wrong-vptr':ins[-3].ops='edx,DWORD PTR [eax]'
                if change=='branch':ins[-4].mnem='jmp'
                if change=='call':ins[-4].mnem='call'
                if change=='wrong-load':w['receiverLoad']='0x00402001'
                if change=='wrong-push':ins[-4].ops='ax'
                if change=='width':w['parameterStackBytes']=[8]
                if change=='missing-arg':w['parameterStackBytes']=[]
                if change=='out-of-body':w['callAddress']='0x00401100'
                if change=='clipped-body':prog.by_va[0x402000].declared_hi=0x402100
                with self.assertRaises(ValueError):E.propagate_vtable_anchors(prog,classes,doc,root)

    def test_dispatch_cannot_supply_unknown_return_or_override_known_parameter_width(self):
        for parameter,result in [('double','void'),('MissingEnum','Vector'),
                                 ('MissingEnum','Aggregate<int*>'),('MissingEnum','Aggregate<int&>')]:
            with self.subTest(parameter=parameter,result=result):
                root,classes,prog,doc=self.fixture(parameter,result)
                with self.assertRaises(ValueError):E.propagate_vtable_anchors(prog,classes,doc,root)

    def test_source_call_allows_bool_accumulation_but_not_unrelated_prefixes(self):
        for prefix,accepted in [('ok &= ',True),('Ignore("',False),('other + ',False)]:
            with self.subTest(prefix=prefix):
                root,classes,prog,doc=self.fixture(result='BOOL')
                source=root/'Caller.cpp';line=prefix+'pages[index]->Run(state);'
                source.write_text('void Host::Tick()\n{\n '+line+'\n}\n')
                witness=doc['anchors'][0]['interfaceDispatch']['source']
                witness.update(sha256=hashlib.sha256(source.read_bytes()).hexdigest(),call=line)
                if accepted:
                    self.assertEqual(len(E.propagate_vtable_anchors(prog,classes,doc,root)['rows']),3)
                else:
                    with self.assertRaises(ValueError):E.propagate_vtable_anchors(prog,classes,doc,root)

    def test_common_interface_does_not_hide_unmapped_alias_or_bad_return(self):
        root,classes,prog,doc = self.fixture()
        prog.slots[0x401200].append(('Unrelated',0,6,0x601000))
        prog.model.insns[1].ops='0x8'
        report=E.propagate_vtable_anchors(prog,classes,doc,root)
        checked=E.vtable_abi_admission(prog,classes,doc,report,root)
        self.assertEqual([r['status'] for r in checked['rows']],
                         ['mechanical-checks-pass','withheld','withheld'])


class GuardedEventInterfaceTests(unittest.TestCase):
    def fixture(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root/'types.h').write_text('class Child : public Mid, public Renderable { public: '
                                  'virtual void HandleEvent(CEvent* event); };\n')
        source = root/'Caller.cpp'
        source.write_text('void Host::Tick()\n{\n {\n IListener* to_call = next_event->GetToCall();\n'
                          ' to_call->HandleEvent(next_event);\n }\n {\n'
                          ' IListener* to_call = next_event->GetToCall();\n'
                          ' to_call->HandleEvent(next_event);\n }\n'
                          ' Log("listener dispatch diagnostic");\n}\n')
        receiver = root/'event.h'; receiver.write_text('/* reviewed synthetic receiver layout */\n')
        classes = E.header_classes(root,set()); method=classes['Child'].methods[0]
        tables = [SimpleNamespace(va=0x600000,klass='IListener',offset=0,slots=[0x401000]),
                  SimpleNamespace(va=0x600100,klass='Mid',offset=0,slots=[0x401200,0x401300]),
                  SimpleNamespace(va=0x600200,klass='Child',offset=0,slots=[0x401100,0x401300,0x401300]),
                  SimpleNamespace(va=0x600300,klass='Child',offset=8,slots=[0x401300])]
        blocks = {t.va:struct.pack('<'+'I'*len(t.slots),*t.slots) for t in tables}
        blocks.update({a:b'\xc2\x04\x00' for a in (0x401000,0x401100,0x401200,0x401300)})
        patterns = (bytes.fromhex('8b08 66896808 3bcd 7405 8b11 50 ff12'),
                    bytes.fromhex('8b0a 66896a08 8b4624 40 3bcd 894624 7405 8b01 52 ff10'))
        caller = b'\x55\x33\xed'+patterns[0]+b'\x90'+patterns[1]+b'\x68'+struct.pack('<I',0x610000)+b'\xc3'
        blocks[0x402000]=caller; blocks[0x610000]=b'listener dispatch diagnostic\0'
        memory={a+i:v for a,b in blocks.items() for i,v in enumerate(b)}
        read=lambda a,n:bytes(memory.get(a+i,0) for i in range(n))
        img=SimpleNamespace(sha256='f'*64,read=read,u32=lambda a:struct.unpack('<I',read(a,4))[0],
                            data=b''.join(blocks.values()))
        insns=[E.Insn(a,3,'ret','0x4') for a in (0x401000,0x401100,0x401200,0x401300)]
        code=[(1,'push','ebp'),(2,'xor','ebp,ebp'),(2,'mov','ecx,DWORD PTR [eax]'),
              (4,'mov','WORD PTR [eax+0x8],bp'),(2,'cmp','ecx,ebp'),
              (2,'je','0x402012'),(2,'mov','edx,DWORD PTR [ecx]'),(1,'push','eax'),
              (2,'call','DWORD PTR [edx]'),(1,'nop',''),(2,'mov','ecx,DWORD PTR [edx]'),
              (4,'mov','WORD PTR [edx+0x8],bp'),(3,'mov','eax,DWORD PTR [esi+0x24]'),
              (1,'inc','eax'),(2,'cmp','ecx,ebp'),(3,'mov','DWORD PTR [esi+0x24],eax'),
              (2,'je','0x402029'),(2,'mov','eax,DWORD PTR [ecx]'),(1,'push','edx'),
              (2,'call','DWORD PTR [eax]'),(5,'push','0x610000'),(1,'ret','')]
        cursor=0x402000
        for size,mnem,ops in code:
            insns.append(E.Insn(cursor,size,mnem,ops)); cursor+=size
        self.assertEqual(cursor,0x402000+len(caller))
        bases={'IListener':[('IListener',0)],'Mid':[('Mid',0),('IListener',0)],
               'Child':[('Child',0),('Mid',0),('IListener',0),('Renderable',8)]}
        model=SimpleNamespace(rtti=SimpleNamespace(vtables=tables,class_bases=bases,
                                                   fixed_bases={k:list(v) for k,v in bases.items()}),insns=insns)
        funcs=[SimpleNamespace(va=a,lo=a,hi=a+len(b)-1) for a,b in blocks.items() if a<0x600000]
        prog=E.Program(img,model,funcs)
        span=lambda a,n:dict(address=hex(a),bytes=n,sha256=hashlib.sha256(read(a,n)).hexdigest())
        witness=dict(kind='guarded-event-primary-prefix',primaryChain=['Child','Mid','IListener'],
                     table='0x600000',evidence='Reviewed synthetic event transport',receiverEvidence='Reviewed receiver layout',
                     caller=span(0x402000,len(caller)),windows=[span(0x402003,15),span(0x402013,22)],
                     zeroRegisterAt='0x402001',callerLiteral=dict(address='0x610000',site='0x402029',text='listener dispatch diagnostic'),
                     source=dict(file='Caller.cpp',sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                                 function='Host::Tick',calls=[dict(line=5,receiverLine=4),dict(line=9,receiverLine=8)]),
                     receiverSources=[dict(file='event.h',sha256=hashlib.sha256(receiver.read_bytes()).hexdigest(),evidence='Reviewed getter layout')])
        witness['class']='IListener'
        anchor=dict(table='0x600200',offset=0,slot=0,target='0x00401100',method='HandleEvent',parameters=['CEvent*'],
                    qualifiers='',sourceFile=method.file,sourceLine=method.line,body=span(0x401100,3),
                    evidence='Reviewed method body',interfaceDispatch=witness)
        anchor['class']='Child'
        return root,classes,prog,dict(specimenSha256=img.sha256,anchors=[anchor]),memory,span

    def test_two_guarded_calls_bind_only_the_fixed_primary_interface(self):
        root,classes,prog,doc,_,_=self.fixture()
        report=E.propagate_vtable_anchors(prog,classes,doc,root)
        self.assertEqual([r['target'] for r in report['rows']],['0x00401000','0x00401100','0x00401200'])
        checked=E.vtable_abi_admission(prog,classes,doc,report,root)
        self.assertTrue(all(r['status']=='mechanical-checks-pass' for r in checked['rows']))
        self.assertNotIn('IListener',classes)  # no declaration order invented

    def test_repinned_byte_mutations_cannot_change_the_transport(self):
        # field/receiver, reuse store, branch condition/target, vptr, pushed event,
        # slot and flag-changing counter bookkeeping all affect actual evidence.
        for offset,value in ((4,0x48),(7,0x09),(11,0x75),(12,0x04),(14,0x10),(15,0x51),
                             (17,0x13),(34,0x40),(39,0x51)):
            with self.subTest(offset=offset):
                root,classes,prog,doc,memory,span=self.fixture();w=doc['anchors'][0]['interfaceDispatch']
                memory[0x402000+offset]=value
                w['caller']=span(0x402000,w['caller']['bytes'])
                w['windows']=[span(0x402003,15),span(0x402013,22)]
                with self.assertRaises(ValueError):E.propagate_vtable_anchors(prog,classes,doc,root)

    def test_wrong_or_repeated_primary_path_and_secondary_overlap_refuse(self):
        for change in ('repeated','nonfixed','offset','short-path','secondary','table','long-base'):
            with self.subTest(change=change):
                root,classes,prog,doc,_,_=self.fixture();w=doc['anchors'][0]['interfaceDispatch']
                if change=='repeated':prog.bases['Child'].append(('IListener',8))
                if change=='nonfixed':prog.fixed_bases['Mid'].pop()
                if change=='offset':prog.bases['Mid'][1]=('IListener',4)
                if change=='short-path':w['primaryChain']=['Child','IListener']
                if change=='secondary':classes['Child'].bases[1]='Mid'
                if change=='table':w['table']='0x600100'
                if change=='long-base':prog.model.rtti.vtables[0].slots.append(0x401000)
                with self.assertRaises(ValueError):E.propagate_vtable_anchors(prog,classes,doc,root)

    def test_repinned_source_receiver_and_independent_calls_are_required(self):
        for change in ('receiver','method','same-call','receiver-hash','receiver-absent','unknown-return'):
            with self.subTest(change=change):
                root,classes,prog,doc,_,_=self.fixture();w=doc['anchors'][0]['interfaceDispatch']
                p=root/'Caller.cpp'
                if change=='receiver':p.write_text(p.read_text().replace('IListener*','Unrelated*'))
                if change=='method':p.write_text(p.read_text().replace('->HandleEvent','->Other'))
                w['source']['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
                if change=='same-call':w['source']['calls'][1]=dict(w['source']['calls'][0])
                if change=='receiver-hash':w['receiverSources'][0]['sha256']='0'*64
                if change=='receiver-absent':w['receiverSources']=[]
                if change=='unknown-return':classes['Child'].methods[0].head='virtual Unknown'
                with self.assertRaises(ValueError):E.propagate_vtable_anchors(prog,classes,doc,root)

    def test_null_initialization_and_branch_bypass_are_checked(self):
        for change in ('zero','clobber','xadd-second','popaw','interior','prefix-branch',
                       'indirect-jump','external-jump','nonboundary-jump',
                       'duplicate-literal','literal-instruction','clipped'):
            with self.subTest(change=change):
                root,classes,prog,doc,_,_=self.fixture();w=doc['anchors'][0]['interfaceDispatch']
                caller=prog.body(prog.by_va[0x402000])
                if change=='zero':w['zeroRegisterAt']='0x402003'
                if change=='clobber':caller[9].mnem,caller[9].ops='inc','ebp'
                if change=='xadd-second':caller[9].mnem,caller[9].ops='xadd','eax,ebp'
                if change=='popaw':caller[9].mnem,caller[9].ops='popaw',''
                if change=='interior':caller[9].mnem,caller[9].ops='jmp','0x402020'
                if change=='indirect-jump':caller[9].mnem,caller[9].ops='jmp','edx'
                if change=='external-jump':caller[9].mnem,caller[9].ops='jmp','0x403000'
                if change=='nonboundary-jump':caller[9].mnem,caller[9].ops='jmp','0x402002'
                if change=='prefix-branch':caller[0].mnem,caller[0].ops='jmp','0x402013'
                if change=='duplicate-literal':prog.img.data+=b'listener dispatch diagnostic\0'
                if change=='literal-instruction':caller[-2].mnem='mov'
                if change=='clipped':prog.by_va[0x402000].declared_hi=0x403000
                with self.assertRaises(ValueError):E.propagate_vtable_anchors(prog,classes,doc,root)


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



class EntryDecodeTests(unittest.TestCase):
    def fixture(self, raw=b'\x90\xc3'):
        va=0x401100
        sec=E.Section('.text',va,len(raw),raw,0x20000000)
        img=SimpleNamespace(section_of=lambda a:sec if sec.contains(a) else None,
                            read=lambda a,n:raw[a-va:a-va+n])
        fn=E.Func(va,'untrusted','USER_DEFINED',va,va+len(raw)-1,'','',False,'',False,
                  body_bytes=len(raw),declared_hi=va+len(raw)-1)
        return img,fn

    def test_exact_byte_rows_are_required(self):
        img,fn=self.fixture()
        good='401100:\t90 \tnop\n401101:\tc3 \tret\n'
        with patch.object(E.subprocess,'run',return_value=SimpleNamespace(stdout=good)) as call:
            self.assertEqual([(i.va,i.mnem) for i in E.decode_entry_body(img,fn)],
                             [(0x401100,'nop'),(0x401101,'ret')])
            self.assertIn('-z',call.call_args.args[0])
            self.assertEqual(call.call_args.kwargs['timeout'],30)
        bad=[good.split('\n',1)[1], good+good, good.replace('401101','401100'),
             good.replace('90 ','91 '), good.replace('c3 ','c3 90 '),
             good.replace('nop','(bad)'),good.replace('nop','.byte 0x90'),'',
             '401100:\t90 \tnop\n...\n']
        for output in bad:
            with self.subTest(output=output),patch.object(E.subprocess,'run',return_value=SimpleNamespace(stdout=output)):
                with self.assertRaises(ValueError):E.decode_entry_body(img,fn)

    def test_extent_and_executable_backing_precede_decoder(self):
        for field,value in [('lo',0x4010ff),('body_ranges',2),('declared_hi',0x401102),
                            ('body_bytes',1),('body_bytes',None)]:
            with self.subTest(field=field):
                img,fn=self.fixture();setattr(fn,field,value)
                with patch.object(E.subprocess,'run') as call:
                    with self.assertRaises(ValueError):E.decode_entry_body(img,fn)
                    call.assert_not_called()
        for mode in ('non-executable','unbacked','missing','short-read'):
            with self.subTest(mode=mode):
                img,fn=self.fixture();sec=img.section_of(fn.va)
                if mode=='non-executable':sec.characteristics=0
                if mode=='unbacked':sec.raw=b'\x90'
                if mode=='missing':img.section_of=lambda a:None
                if mode=='short-read':img.read=lambda a,n:b'\x90'
                with patch.object(E.subprocess,'run') as call:
                    with self.assertRaises(ValueError):E.decode_entry_body(img,fn)
                    call.assert_not_called()

    def test_real_decoder_preserves_zeros_and_rejects_truncation(self):
        # Authored bytes only. No project fixture or retail payload is loaded.
        import shutil
        if not shutil.which('objdump'):self.skipTest('GNU objdump unavailable')
        img,fn=self.fixture(b'\x00\x00'*8+b'\xc3')
        body=E.decode_entry_body(img,fn)
        self.assertEqual(sum(i.size for i in body),17)
        self.assertEqual(body[-1].mnem,'ret')
        img,fn=self.fixture(b'\x90\x0f')
        with self.assertRaises(ValueError):E.decode_entry_body(img,fn)


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

    def entry_gap_fixture(self, raw):
        classes,prog,anchors=self.fixture()
        fn=prog.by_va[0x401100];fn.hi=fn.va+len(raw)-1
        fn.body_ranges=1;fn.body_bytes=len(raw);fn.declared_hi=fn.hi
        sec=E.Section('.text',fn.va,len(raw),raw,0x20000000)
        read=prog.img.read
        prog.img.read=lambda a,n:raw[a-fn.va:a-fn.va+n] if fn.va<=a<=fn.hi else read(a,n)
        prog.img.section_of=lambda a:sec if sec.contains(a) else None
        prog.body=lambda f:[E.Insn(f.va,1,'ret','')] if f.va==0x401000 else []
        return classes,prog,anchors

    def test_entry_gap_repair_still_applies_all_abi_refusals(self):
        import shutil
        if not shutil.which('objdump'):self.skipTest('GNU objdump unavailable')
        cases=[(b'\x90\xc3',None),
               (b'\xeb\xff\xc3','instruction boundary'),
               (b'\x74\x01\xc3\xc2\x08\x00','return cleanup disagrees'),
               (b'\xff\xe0','indirect tail'),
               (b'\x74\x40\xc3','conditional branch outside'),
               (b'\x89\xc4\xc3','opaque stack-pointer'),
               (b'\x50\xe9\xfa\xfe\xff\xff','stack-neutral')]
        for raw,wanted in cases:
            with self.subTest(raw=raw.hex()):
                classes,prog,anchors=self.entry_gap_fixture(raw)
                original=list(prog.model.insns)
                propagated=E.propagate_vtable_anchors(prog,classes,anchors)
                report=E.vtable_abi_admission(prog,classes,anchors,propagated)
                row=report['rows'][1]
                self.assertEqual(row['status'],'withheld' if wanted else 'mechanical-checks-pass')
                if wanted:self.assertTrue(any(wanted in v for v in row['flags']),row)
                evidence=report['entryDecodings'][0]
                self.assertEqual(evidence['status'],'complete-byte-coverage')
                self.assertEqual(evidence['bodySha256'],hashlib.sha256(raw).hexdigest())
                self.assertEqual(prog.model.insns,original)

    def test_entry_decode_is_also_used_for_inline_constant_contradictions(self):
        import shutil
        if not shutil.which('objdump'):self.skipTest('GNU objdump unavailable')
        for raw,expected in [(b'\x31\xc0\xc3','withheld'),
                             (b'\xb8\x01\x00\x00\x00\xc3','mechanical-checks-pass')]:
            with self.subTest(raw=raw.hex()):
                _,prog,anchors=self.entry_gap_fixture(raw)
                classes=self.parse('class Base { public: virtual BOOL Run(); };\n'
                                   'class Child : public Base { public: virtual BOOL Run(){ return TRUE; } };\n')
                # The old cache sees only RET and would miss XOR/MOV EAX.
                prog.body=lambda f:[E.Insn(f.hi,1,'ret','')]
                report=E.vtable_abi_admission(prog,classes,anchors,E.propagate_vtable_anchors(prog,classes,anchors))
                self.assertEqual(report['rows'][1]['status'],expected)
                if expected=='withheld':
                    self.assertIn('tiny constant contradicts source implementation',report['rows'][1]['flags'])

    def test_entry_decode_failure_is_withheld_and_cache_is_per_invocation(self):
        classes,prog,anchors=self.entry_gap_fixture(b'\x90\xc3')
        propagated=E.propagate_vtable_anchors(prog,classes,anchors)
        for error in (E.subprocess.TimeoutExpired('objdump',30),
                      E.subprocess.CalledProcessError(1,'objdump'),OSError('missing')):
            with self.subTest(error=type(error).__name__),patch.object(E.subprocess,'run',side_effect=error):
                report=E.vtable_abi_admission(prog,classes,anchors,propagated)
                self.assertEqual(report['rows'][1]['status'],'withheld')
                self.assertEqual(report['entryDecodings'][0]['status'],'refused')
        with patch.object(E.subprocess,'run',return_value=SimpleNamespace(stdout='401100:\t90 \tnop\n401101:\tc3 \tret\n')) as call:
            for _ in range(2):
                report=E.vtable_abi_admission(prog,classes,anchors,propagated)
                self.assertEqual(report['rows'][1]['status'],'mechanical-checks-pass')
            self.assertEqual(call.call_count,2)
            read=prog.img.read
            prog.img.read=lambda a,n:b'\x91\xc3'[:n] if a==0x401100 else read(a,n)
            report=E.vtable_abi_admission(prog,classes,anchors,propagated)
            self.assertEqual(report['rows'][1]['status'],'withheld')

    def test_overlapping_export_cannot_be_repaired_by_local_decode(self):
        classes,prog,anchors=self.entry_gap_fixture(b'\x90\xc3')
        # Even a different function's clipped bounding box retains ownership.
        prog.by_va[0x401000].declared_hi=0x401100
        with patch.object(E.subprocess,'run') as call:
            report=E.vtable_abi_admission(prog,classes,anchors,E.propagate_vtable_anchors(prog,classes,anchors))
            self.assertIn('overlapping exported function ownership',report['rows'][1]['flags'])
            call.assert_not_called()

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


class ClassNameGetterTests(unittest.TestCase):
    """Authored source/PE-like sections; no retail payload in these cases."""

    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        source = root/'game.cpp'
        source.write_text('void CGame::Fill()\n{\n CActiveReader<Base>* item = list.At(0);\n'
                          ' log("Unique synthetic anchor");\n'
                          ' strcpy(name, item->ToRead()->_GetClassName());\n}\n')
        text = E.Section('.text',0x401000,0x400,bytes(0x400),0x60000020)
        tables = E.Section('.rdata',0x600000,0x300,bytes(0x300),0x40000040)
        data = E.Section('.data',0x620000,0x100,bytes(0x100),0xc0000040)
        sections = [text,tables,data]
        def read(address,size):
            for section in sections:
                if section.start <= address < section.start+len(section.raw):
                    offset=address-section.start
                    return section.raw[offset:offset+size]
            return b''
        def put(address,value):
            for section in sections:
                if section.contains(address):
                    offset=address-section.start;raw=bytearray(section.raw)
                    raw[offset:offset+len(value)]=value;section.raw=bytes(raw)
                    return
            raise AssertionError(hex(address))
        put(0x401005,b'\x68'+struct.pack('<I',0x620040))
        put(0x401010,bytes.fromhex('8b0a85c974288b11ff521c8bf883c9ff33c0 '
                                 '8d542420f2aef7d12bf98bc18bf78bfac1e902f3a58bc883e103f3a4'))
        for table,col,target,string,name in [(0x600020,0x600200,0x401200,0x620000,'Base'),
                                            (0x600120,0x600218,0x401300,0x620010,'Child')]:
            put(table-4,struct.pack('<I',col));put(table+28,struct.pack('<I',target))
            put(target,b'\xb8'+struct.pack('<I',string)+b'\xc3');put(string,name.encode()+b'\0')
        put(0x620040,b'Unique synthetic anchor\0')
        img=SimpleNamespace(sha256='a'*64,sections=sections,read=read,
                            section_of=lambda a:next((s for s in sections if s.contains(a)),None),
                            u32=lambda a:struct.unpack('<I',read(a,4))[0] if len(read(a,4))==4 else None)
        img.data=b''.join(s.raw for s in sections)
        bases={'Base':[('Base',0)],'Child':[('Child',0),('Base',0)]}
        rtti=E.RttiModel({},bases,[E.Vtable(0x600020,'Base',0,[0]*7+[0x401200]),
                                  E.Vtable(0x600120,'Child',0,[0]*7+[0x401300])],
                         {k:v.copy() for k,v in bases.items()})
        model=SimpleNamespace(insns=[],rtti=rtti)
        fn=lambda a,n,size:E.Func(a,n,'USER_DEFINED',a,a+size-1,'','',True,'',False,1,size,a+size-1)
        prog=E.Program(img,model,[fn(0x401000,'UntrustedCaller',128),
                                  fn(0x401200,'UntrustedBase',6),fn(0x401300,'UntrustedChild',6)])
        pin=lambda a,n:dict(address=hex(a),bytes=n,sha256=hashlib.sha256(read(a,n)).hexdigest())
        doc={'kind':'class-name-getter-v1','specimenSha256':img.sha256,'baseClass':'Base','slot':7,
             'evidence':'Synthetic caller/string-result correspondence.','receiverEvidence':'Reviewed synthetic active reader.',
             'source':{'file':'game.cpp','sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                       'function':'CGame::Fill','line':5,'call':'strcpy(name, item->ToRead()->_GetClassName());'},
             'caller':pin(0x401000,128),'window':pin(0x401010,46),'callAddress':'0x401018',
             'callerLiteral':{'address':'0x620040','pushAddress':'0x401005','text':'Unique synthetic anchor'},
             'seed':{'table':'0x600020','target':'0x401200'}}
        return prog,doc,root,put

    def report(self,prog,doc,root):
        with patch.object(E,'scan_rtti',return_value=prog.model.rtti):
            return E.class_name_getters(prog,doc,root)

    def test_names_are_outputs_and_writable_literals_are_explicit(self):
        p,d,r,_=self.fixture();a=self.report(p,d,r)
        self.assertEqual([x['proposedName'] for x in a['proposals']['rows']],
                         ['Base___GetClassName','Child___GetClassName'])
        self.assertTrue(all(x['stringWritable'] for x in a['rows']))
        p.by_va[0x401300].name='AnEntirelyDifferentInheritedGuess'
        self.assertEqual(a['rows'],self.report(p,d,r)['rows'])
        self.assertIn('No prototype promotion',a['limits'])
        self.assertEqual(a['limits'],a['proposals']['limits'])
        self.assertIn('possible inlined forwarding',a['proposals']['limits'])

    def test_repinned_result_consumption_mutations_are_rejected(self):
        # Re-pin both spans so the instruction contract, not the hash guard,
        # rejects every changed byte of the inlined scan/copy tail.
        for offset in range(18,46):
            with self.subTest(offset=offset):
                p,d,r,put=self.fixture()
                address=0x401010+offset
                put(address,bytes([p.img.read(address,1)[0]^1]))
                for key,a,n in [('caller',0x401000,128),('window',0x401010,46)]:
                    d[key]['sha256']=hashlib.sha256(p.img.read(a,n)).hexdigest()
                with self.assertRaisesRegex(ValueError,'string-result window'):
                    self.report(p,d,r)

    def test_anchor_specimen_source_caller_receiver_and_slot_are_bound(self):
        for kind in ['specimen','source','caller','slot','call-address','receiver','source-receiver','literal','seed']:
            with self.subTest(kind=kind):
                p,d,r,put=self.fixture()
                if kind=='specimen':d['specimenSha256']='0'*64
                elif kind=='source':d['source']['sha256']='0'*64
                elif kind=='caller':d['caller']['sha256']='0'*64
                elif kind=='slot':d['slot']=8
                elif kind=='call-address':d['callAddress']='0x401019'
                elif kind=='receiver':
                    put(0x401010,b'\x8b\x09')
                    for key,a,n in [('caller',0x401000,128),('window',0x401010,46)]:
                        d[key]['sha256']=hashlib.sha256(p.img.read(a,n)).hexdigest()
                elif kind=='source-receiver':
                    f=r/'game.cpp';f.write_text(f.read_text().replace('CActiveReader<Base>','CActiveReader<Other>'))
                    d['source']['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
                elif kind=='literal':d['callerLiteral']['text']='A different string'
                else:d['seed']['target']='0x401300'
                with self.assertRaises(ValueError):self.report(p,d,r)

    def test_boolean_slot_and_ambiguous_caller_are_rejected(self):
        for kind in ['bool-slot','multi-range','clipped-body','duplicate-source','missing-proof']:
            with self.subTest(kind=kind):
                p,d,r,_=self.fixture()
                if kind=='bool-slot':d['slot']=True
                elif kind=='multi-range':p.by_va[0x401000].body_ranges=2
                elif kind=='clipped-body':p.by_va[0x401000].declared_hi+=1
                elif kind=='duplicate-source':
                    f=r/'game.cpp';f.write_text(f.read_text()+f.read_text())
                    d['source']['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
                else:d['receiverEvidence']=''
                with self.assertRaises(ValueError):self.report(p,d,r)

    def test_extra_bytes_ret_pop_thunk_or_wrong_string_are_withheld(self):
        for kind in ['extent','thunk','ret-pop','jump','wrong-string','unterminated','unmapped','executable','uninitialized']:
            with self.subTest(kind=kind):
                p,d,r,put=self.fixture()
                if kind=='extent':p.by_va[0x401300].body_bytes=7
                elif kind=='thunk':p.by_va[0x401300].thunk=True
                elif kind=='ret-pop':put(0x401305,b'\xc2\x04\x00')
                elif kind=='jump':put(0x401300,b'\xe9')
                elif kind=='wrong-string':put(0x620010,b'Other\0')
                elif kind=='unterminated':put(0x620015,b'!')
                elif kind=='unmapped':put(0x401301,struct.pack('<I',0x700000))
                else:
                    # Put only the child literal into the affected section.
                    p.img.sections.append(E.Section('.extra',0x630000,6,b'Child\0',
                        0x60000020 if kind=='executable' else 0xc0000080))
                    put(0x401301,struct.pack('<I',0x630000))
                report=self.report(p,d,r)
                row=next(x for x in report['proposals']['rows'] if x['target']=='0x00401300')
                self.assertEqual(row['status'],'withheld')

    def test_secondary_dynamic_repeated_or_constructor_adjusted_base_is_withheld(self):
        for kind in ['dynamic','repeated','mixed-offset','mixed-dynamic','fixed-extra',
                     'constructor-displacement','col-offset']:
            with self.subTest(kind=kind):
                p,d,r,put=self.fixture()
                if kind=='dynamic':p.model.rtti.fixed_bases['Child']=[('Child',0)]
                elif kind=='repeated':p.model.rtti.class_bases['Child'].append(('Base',0))
                elif kind=='mixed-offset':
                    p.model.rtti.class_bases['Child'].append(('Base',4))
                    p.model.rtti.fixed_bases['Child'].append(('Base',4))
                elif kind=='mixed-dynamic':p.model.rtti.class_bases['Child'].append(('Base',4))
                elif kind=='fixed-extra':p.model.rtti.fixed_bases['Child'].append(('Base',4))
                elif kind=='constructor-displacement':put(0x600220,struct.pack('<I',4))
                else:put(0x60021c,struct.pack('<I',4))
                row=self.report(p,d,r)['proposals']['rows'][1]
                self.assertEqual(row['status'],'withheld')

    def test_extra_pointer_alias_and_occupied_spelling_remain_withheld(self):
        for kind in ['pointer','holder','occupied']:
            with self.subTest(kind=kind):
                p,d,r,put=self.fixture()
                if kind=='pointer':put(0x6002fc,struct.pack('<I',0x401300))
                elif kind=='holder':p.slots[0x401300].append(('Unrelated',0,3,0x610000))
                else:p.funcs[0].name='Child___GetClassName'
                self.assertEqual(self.report(p,d,r)['proposals']['rows'][1]['status'],'withheld')

    def test_cached_rtti_cannot_override_fresh_specimen(self):
        p,d,r,_=self.fixture()
        with patch.object(E,'scan_rtti',return_value=E.RttiModel({}, {}, [])):
            with self.assertRaisesRegex(ValueError,'fresh specimen'):
                E.class_name_getters(p,d,r)


class CompilerDestructorTests(unittest.TestCase):
    """Authored compiler-entry bytes and synthetic decoded CFGs, no retail input."""

    @staticmethod
    def wrapper(address, cleanup, free=0x405000, manager=0x680000):
        return (bytes.fromhex('56 8b f1 e8') + struct.pack('<i', cleanup-address-8)
                + bytes.fromhex('f6 44 24 08 01 74 0b 56 b9') + struct.pack('<I', manager)
                + b'\xe8' + struct.pack('<i', free-address-26) + bytes.fromhex('8b c6 5e c2 04 00'))

    def fixture(self, cleanup=None):
        raw, decoded = {}, {}
        def add(address, name, body, payload=None):
            cursor, insns = address, []
            for size, op, arg in body:
                insns.append(E.Insn(cursor, size, op, arg)); cursor += size
            data = payload if payload is not None else bytes([0x90]) * (cursor-address)
            raw[address] = data; decoded[address] = insns
            return E.Func(address, name, 'USER_DEFINED', address, address+len(data)-1,
                          '', '', True, '', False, 1, len(data), address+len(data)-1)
        funcs = [add(0x401000, 'Base__scalar_deleting_dtor', [], self.wrapper(0x401000, 0x403000)),
                 add(0x401100, 'Misleading__OldName', [], self.wrapper(0x401100, 0x402000)),
                 add(0x402000, 'UntrustedCleanupName', cleanup or [
                     (1,'push','esi'), (2,'mov','esi,ecx'), (5,'call','0x403000'),
                     (1,'pop','esi'), (1,'ret','')]),
                 add(0x403000, 'UntrustedBaseName', [(1,'ret','')]),
                 add(0x405000, 'UntrustedFreeName', [(3,'ret','0x4')])]
        words = {0x600004:0x401000, 0x600104:0x401100}
        def read(address, size):
            for start, data in raw.items():
                if start <= address < start+len(data):
                    return data[address-start:address-start+size]
            return b''
        img = SimpleNamespace(sha256='a'*64, read=read, u32=lambda a: words.get(a))
        bases = {'Base':[('Base',0)], 'Child':[('Child',0),('Base',0)]}
        tables = [E.Vtable(0x600000,'Base',0,[0,0x401000]), E.Vtable(0x600100,'Child',0,[0,0x401100])]
        model = SimpleNamespace(insns=[i for a in sorted(decoded) for i in decoded[a]],
                                rtti=E.RttiModel({},bases,tables,{k:v.copy() for k,v in bases.items()}))
        prog = E.Program(img,model,funcs)
        prog.body = lambda fn: decoded[fn.va]
        pin = lambda a: dict(address=hex(a),bytes=len(raw[a]),sha256=hashlib.sha256(raw[a]).hexdigest())
        doc = {'specimenSha256':img.sha256, 'evidence':'Synthetic reviewed base-slot and allocator witness.',
               'seed':{'class':'Base','table':'0x600000','slot':1,'target':'0x401000','body':pin(0x401000)},
               'teardown':pin(0x403000),'deallocator':pin(0x405000),'manager':'0x680000'}
        return prog,doc,raw,decoded,words

    def test_exact_wrapper_checks_every_fixed_byte_and_both_calls(self):
        raw = self.wrapper(0x401000,0x403000)
        self.assertEqual(E.scalar_delete_entry(raw,0x401000,0x680000,0x405000),0x403000)
        masked = set(range(4,8)) | set(range(22,26))
        for i in set(range(32))-masked:
            with self.subTest(byte=i):
                changed=bytearray(raw); changed[i]^=1
                self.assertIsNone(E.scalar_delete_entry(bytes(changed),0x401000,0x680000,0x405000))
        for wrong in [raw[:-1],raw+b'\x90',self.wrapper(0x401000,0x403000,free=0x405001)]:
            self.assertIsNone(E.scalar_delete_entry(wrong,0x401000,0x680000,0x405000))
        # The decoder extracts the first target; family admission must prove it.
        self.assertEqual(E.scalar_delete_entry(self.wrapper(0x401000,0x404000),0x401000,0x680000,0x405000),0x404000)

    def test_names_are_outputs_and_unchanged_byte_proofs_admit_a_family(self):
        prog,doc,*_=self.fixture()
        report=E.compiler_destructors(prog,doc)
        self.assertEqual([r['status'] for r in report['proposals']['rows']],['keep','rename'])
        self.assertEqual(report['proposals']['rows'][1]['proposedName'],'Child__scalar_deleting_dtor')
        prog.by_va[0x401100].name='AnEntirelyDifferentGuess'
        self.assertEqual(E.compiler_destructors(prog,doc)['rows'],report['rows'])

    def test_specimen_seed_allocator_and_raw_table_pins_are_required(self):
        import copy
        for label in ['specimen','seed-hash','base-hash','free-hash','class','slot','target','table-word','descendant-word']:
            with self.subTest(label=label):
                prog,doc,raw,_,words=self.fixture(); doc=copy.deepcopy(doc)
                if label=='specimen':doc['specimenSha256']='0'*64
                elif label=='seed-hash':doc['seed']['body']['sha256']='0'*64
                elif label=='base-hash':doc['teardown']['sha256']='0'*64
                elif label=='free-hash':doc['deallocator']['sha256']='0'*64
                elif label=='class':doc['seed']['class']='Other'
                elif label=='slot':doc['seed']['slot']=True
                elif label=='target':doc['seed']['target']='0x401100'
                elif label=='table-word':words[0x600004]=0x401100
                else:words[0x600104]=0x401000
                with self.assertRaises(ValueError):E.compiler_destructors(prog,doc)

    def test_unknown_first_target_or_argument_popping_cleanup_is_withheld(self):
        for mode in ['unknown-target','ret4','plain-ret','wrong-this']:
            with self.subTest(mode=mode):
                body = [(3,'ret','0x4')] if mode=='ret4' else [(1,'ret','')] if mode=='plain-ret' else [
                    (2,'xor','ecx,ecx'),(5,'call','0x403000'),(1,'ret','')]
                prog,doc,raw,*_=self.fixture(body)
                if mode=='unknown-target':raw[0x401100]=self.wrapper(0x401100,0x404000)
                report=E.compiler_destructors(prog,doc)
                self.assertEqual(report['proposals']['rows'][1]['status'],'withheld')

    def test_backward_block_after_ret_is_not_a_tail_and_early_return_fails(self):
        body=[(1,'push','esi'),(2,'mov','esi,ecx'),(2,'test','eax,eax'),(2,'je','0x402010'),
              (2,'mov','ecx,esi'),(5,'call','0x403000'),(1,'pop','esi'),(1,'ret',''),
              (2,'xor','eax,eax'),(5,'jmp','0x402007')]
        prog,doc,*_=self.fixture(body)
        result=E.compiler_destructors(prog,doc)
        self.assertEqual(result['proposals']['rows'][1]['status'],'rename')
        early=body[:8]+[(1,'ret','')]
        prog,doc,*_=self.fixture(early)
        self.assertEqual(E.compiler_destructors(prog,doc)['proposals']['rows'][1]['status'],'withheld')

    def test_tails_require_unchanged_this_stack_and_resolved_acyclic_target(self):
        for body,passes in [([(5,'jmp','0x403000')],True),
                            ([(6,'mov','DWORD PTR [ecx],0x680000'),(5,'jmp','0x403000')],True),
                            ([(3,'sub','ecx,0x4'),(5,'jmp','0x403000')],False),
                            ([(1,'push','esi'),(5,'jmp','0x403000')],False),
                            ([(5,'jmp','0x402000')],False),
                            ([(2,'jmp','eax')],False)]:
            with self.subTest(body=body):
                prog,doc,*_=self.fixture(body)
                status=E.compiler_destructors(prog,doc)['proposals']['rows'][1]['status']
                self.assertEqual(status!='withheld',passes)

    def test_primary_unique_ancestry_and_every_alias_are_required(self):
        for mode in ['secondary','repeated','uncovered','ambiguous']:
            with self.subTest(mode=mode):
                prog,doc,*_=self.fixture()
                if mode=='secondary':prog.model.rtti.vtables[1].offset=4
                elif mode=='repeated':prog.bases['Child'].append(('Base',4))
                else:
                    prog.slots[0x401100].append(('Other',0,1,0x600200))
                    if mode=='ambiguous':
                        prog.bases['Other']=[('Other',0),('Base',0)]
                        prog.fixed_bases['Other']=[('Other',0),('Base',0)]
                        prog.model.rtti.vtables.append(E.Vtable(0x600200,'Other',0,[0,0x401100]))
                        old=prog.img.u32;prog.img.u32=lambda a:0x401100 if a==0x600204 else old(a)
                rows=E.compiler_destructors(prog,doc)['proposals']['rows']
                self.assertFalse(any(r['target']=='0x00401100' and r['status']!='withheld' for r in rows))

    def test_boundary_overlap_and_occupied_name_are_not_silently_fixed(self):
        for field,value in [('body_ranges',2),('body_bytes',31),('declared_hi',0x401120),('hi',0x401110)]:
            with self.subTest(field=field):
                prog,doc,*_=self.fixture();setattr(prog.by_va[0x401100],field,value)
                self.assertEqual(E.compiler_destructors(prog,doc)['proposals']['rows'][1]['status'],'withheld')
        prog,doc,*_=self.fixture();prog.by_va[0x405000].name='Child__scalar_deleting_dtor'
        row=E.compiler_destructors(prog,doc)['proposals']['rows'][1]
        self.assertEqual(row['status'],'withheld')
        self.assertIn('already belongs',row['flags'][0])

    def test_partial_and_implicit_register_writes_lose_this_proof(self):
        state=frozenset({'ecx','esi','edi','eax'})
        for op,args,reg in [('mov','cl,0x0','ecx'),('xchg','esi,eax','esi'),
                            ('rep','movs DWORD PTR es:[edi],DWORD PTR ds:[esi]','esi'),
                            ('pop','ecx','ecx'),('mul','ebx','eax'),('imul','esi','eax'),
                            ('div','esi','eax'),('cpuid','','ecx'),('lahf','','eax'),
                            ('cmpxchg','DWORD PTR [ebx],ecx','eax'),('popad','','esi')]:
            with self.subTest(op=op,args=args):
                self.assertNotIn(reg,E._this_after(E.Insn(0,1,op,args),state))

    def test_clipped_seed_and_opaque_control_transfer_do_not_admit(self):
        prog,doc,*_=self.fixture();prog.by_va[0x401000].declared_hi+=1
        with self.assertRaisesRegex(ValueError,'seed function boundary'):
            E.compiler_destructors(prog,doc)
        for op in ['int','sysenter','ud2','lcall','retf']:
            with self.subTest(op=op):
                prog,doc,*_=self.fixture([(2,op,'0x80'),(5,'call','0x403000'),(1,'ret','')])
                self.assertEqual(E.compiler_destructors(prog,doc)['proposals']['rows'][1]['status'],'withheld')

    def test_unsupported_implicit_or_second_operand_writes_refuse_the_whole_proof(self):
        for op,args in [('xadd','eax,esi'),('xadd','DWORD PTR [ebx],esi'),
                        ('rdtscp',''),('ins','DWORD PTR es:[edi],dx'),('outs','dx,DWORD PTR ds:[esi]'),
                        ('aaa',''),('aas',''),('aad','0xa'),('aam','0xa'),('daa',''),('das',''),
                        ('salc',''),('unknown_opcode','')]:
            with self.subTest(op=op,args=args):
                # XADD's second operand changes ESI; the old permissive handler
                # falsely carried original-this through this sequence.
                body=[(2,'mov','esi,ecx'),(2,'xor','eax,eax'),(3,op,args),
                      (2,'mov','ecx,esi'),(5,'call','0x403000'),(1,'ret','')]
                prog,doc,*_=self.fixture(body)
                report=E.compiler_destructors(prog,doc)
                self.assertEqual(report['proposals']['rows'][1]['status'],'withheld')
                self.assertIn('unsupported instruction',report['admission']['rows'][1]['flags'][0])
                self.assertFalse(E._this_after(E.Insn(0,3,op,args),frozenset({'ecx','esi','edi','eax'})))

    def test_opaque_stack_pointer_writes_refuse_even_with_a_later_base_call(self):
        for op,args in [('mov','esp,eax'),('mov','sp,ax'),('lea','esp,[eax+0x4]'),('pop','esp')]:
            with self.subTest(op=op,args=args):
                prog,doc,*_=self.fixture([(2,op,args),(5,'call','0x403000'),(1,'ret','')])
                report=E.compiler_destructors(prog,doc)
                self.assertEqual(report['proposals']['rows'][1]['status'],'withheld')
                self.assertIn('opaque cleanup stack-pointer',report['admission']['rows'][1]['flags'][0])


if __name__ == "__main__":
    unittest.main()
