"""Focused tests for the pure helpers of tools/re_name_evidence.py (synthetic inputs only)."""
from __future__ import annotations

import sys
import hashlib
import struct
import tempfile
import unittest
import copy
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import re_name_evidence as E  # noqa: E402


class TypedListSourceTests(unittest.TestCase):
    def source(self, declaration='DeviceObject* item = list;', call='item->Restore();', extra='',
               advance='item=item->mNext;', between=''):
        text = 'void Owner::Restore() {\n'+declaration+'\n'+between+'while(item) {\n'+call+'\n'+extra+advance+'\n}\n}'
        return text, call, text.index(call)

    def check(self, fixture):
        text,call,offset=fixture
        E.typed_list_source_receiver(text,'DeviceObject','item',call,offset)

    def test_plain_and_result_diagnostic_shapes(self):
        self.check(self.source())
        for extra in ('', 'if (result!=S_OK) item=item;\n', 'ASSERT(result==S_OK);\n'):
            with self.subTest(extra=extra):
                self.check(self.source(call='HRESULT result=item->Restore();',extra=extra))

    def test_qualified_types_literals_and_intervening_statements_are_refused(self):
        for declaration in ('NotDeviceObject* item=list;', 'Other::DeviceObject* item=list;',
                            'Other:: DeviceObject* item=list;', 'Other::\nDeviceObject* item=list;',
                            'Wrap<DeviceObject>* item=list;',
                            'const char* text="DeviceObject* item=list;";'):
            with self.subTest(declaration=declaration):
                with self.assertRaises(ValueError): self.check(self.source(declaration=declaration))
        with self.assertRaises(ValueError): self.check(self.source(between='item=other;\n'))

    def test_false_advance_shadowing_and_conditional_call_are_refused(self):
        for advance in ('otheritem=item->mNext;', '"item=item->mNext;";',
                        'item=item->mNext; item=item->mNext;',
                        'Other* item=other; item=item->mNext;',
                        'item->Other(); item=item->mNext;', 'item=other; item=item->mNext;'):
            with self.subTest(advance=advance):
                with self.assertRaises(ValueError): self.check(self.source(advance=advance))
        text,call,offset=self.source()
        changed=text.replace(call,'if (allow) '+call)
        with self.assertRaises(ValueError): self.check((changed,call,changed.index(call)))
        with self.assertRaisesRegex(ValueError,'shadows receiver'):
            self.check(self.source(call='Other item=item->Restore();'))

    def test_call_must_be_inside_the_selected_loop(self):
        text,call,offset=self.source()
        with self.assertRaises(ValueError): self.check((text,call,offset+len(text)))
        with self.assertRaises(ValueError): self.check((text+text,call,offset))


class TypedListLoopTests(unittest.TestCase):
    """Authored intrusive-list loops, independent of retail code or addresses."""

    def fixture(self, *, conditional=False, zero=False, bad_receiver=False,
                wrong_slot=False, extra_argument=False, advance_first=False,
                extra=b'', zero_gap=b'', pre_zero=b''):
        start, head, flag, auxiliary = 0x411000, 0x710100, 0x710200, 0x411700
        code = bytearray(b'\x57')  # save the authored EDI iterator
        zero_site = None
        if zero:
            code += b'\x53'+pre_zero
            zero_site = start+len(code)
            code += b'\x31\xdb'+zero_gap
        loop = len(code)
        code += b'\x8b\x3d'+struct.pack('<I', head)
        test = b'\x39\xdf' if zero else b'\x85\xff'
        code += test
        empty = len(code); code += b'\x74\x00'
        entry = len(code)
        advance = b'\x8b\x7f\x0c'
        if advance_first:
            code += advance
        code += b'\x8b\x17'+(b'\x8b\xcb' if bad_receiver else b'\x8b\xcf')
        if extra_argument:
            code += b'\x6a\x01'
        call = len(code); code += b'\xff\x52'+bytes([28 if wrong_slot else 24])
        if conditional:
            code += b'\xa0'+struct.pack('<I',flag)
        if not advance_first:
            code += advance
        code += extra
        skip = None
        if conditional:
            code += b'\x38\xd8' if zero else b'\x84\xc0'
            skip = len(code); code += b'\x74\x00'
        code += b'\x6a\x07'+(b'\x53' if zero else b'\x6a\x00')
        code += b'\xb9'+struct.pack('<I',0x710300)
        site = start+len(code)
        code += b'\xe8'+struct.pack('<i',auxiliary-site-5)
        test_site = len(code); code += test
        back = len(code); code += b'\x75'+bytes([(entry-back-2)&255])
        end = len(code); code[empty+1] = end-empty-2
        if skip is not None:
            code[skip+1] = test_site-skip-2
        if zero:
            code += b'\x5b'
        code += b'\x5f\xc3'
        section = E.Section('.text',start,len(code),bytes(code),0x60000020)
        img = SimpleNamespace(sections=[section],
            read=lambda a,n: section.raw[a-start:a-start+n],
            section_of=lambda a: section if section.contains(a) else None)
        fn = E.Func(start,'Untrusted__Label','USER_DEFINED',start,start+len(code)-1,
                    '', '', False, '', False, 1, len(code),start+len(code)-1)
        model = SimpleNamespace(refs_to={},data_ptrs_to={})
        prog = SimpleNamespace(img=img,model=model,funcs=[fn])
        witness = dict(address=hex(start+loop),bytes=end-loop,
            sha256=hashlib.sha256(bytes(code[loop:end])).hexdigest(),head=hex(head),slot=6,
            nextOffset=12,callAddress=hex(start+call))
        if zero:
            witness.update(zeroRegister='ebx',zeroAddress=hex(zero_site))
        return prog,fn,witness,dict(entry=start+entry,call=start+call,loop=start+loop)

    def test_both_guard_forms_and_optional_ancillary_condition(self):
        for conditional in (False,True):
            for zero in (False,True):
                with self.subTest(conditional=conditional,zero=zero):
                    p,f,w,_ = self.fixture(conditional=conditional,zero=zero)
                    r=E.typed_list_loop(p,f,w)
                    self.assertEqual((r['slot'],r['nextOffset'],r['parameterStackBytes']),(6,12,0))
                    self.assertEqual(r['conditionalAncillary'],conditional)

    def test_wrong_receiver_slot_arguments_and_advancement_are_refused(self):
        for kwargs in ({'bad_receiver':True},{'wrong_slot':True},{'extra_argument':True},
                       {'advance_first':True},{'extra':b'\x66\x47'},
                       {'extra':b'\x87\xf8'},{'extra':b'\x61'}):
            with self.subTest(kwargs=kwargs):
                p,f,w,_=self.fixture(**kwargs)
                with self.assertRaises(ValueError): E.typed_list_loop(p,f,w)

    def test_wrong_head_next_slot_and_missing_or_stale_pins_are_refused(self):
        for key,value in [('head','0x710104'),('nextOffset',8),('nextOffset',True),
                          ('slot',5),('slot',True),('sha256','0'*64),('bytes',2)]:
            with self.subTest(key=key,value=value):
                p,f,w,_=self.fixture();w[key]=value
                with self.assertRaises(ValueError): E.typed_list_loop(p,f,w)

    def test_external_entries_and_raw_interior_pointers_are_refused(self):
        for kind in ('branch','pointer','raw'):
            with self.subTest(kind=kind):
                p,f,w,l=self.fixture()
                if kind=='branch':p.model.refs_to[l['entry']]=[('jmp',0x420000)]
                elif kind=='pointer':p.model.data_ptrs_to[l['call']]=[0x700000]
                else:p.img.sections.append(E.Section('.data',0x700000,4,
                    struct.pack('<I',l['call']),0xc0000040))
                with self.assertRaisesRegex(ValueError,'bypassing entry'):
                    E.typed_list_loop(p,f,w)

    def test_zero_register_partial_implicit_and_second_operand_clobbers_are_refused(self):
        for gap in (b'\xb3\x01',b'\x66\xbb\x01\x00',b'\x93',b'\x61',b'\x5b',
                    b'\xff\xe0',b'\xe9\x00\x10\x00\x00'):
            with self.subTest(gap=gap.hex()):
                p,f,w,_=self.fixture(zero=True,zero_gap=gap)
                with self.assertRaisesRegex(ValueError,'zero register|unresolved indirect entry'):
                    E.typed_list_loop(p,f,w)

    def test_later_reentry_cannot_bypass_the_zero_assignment(self):
        for kind in ('jump','call','indirect'):
            for cached in (False,True):
                with self.subTest(kind=kind,cached=cached):
                    p,f,w,loc=self.fixture(zero=True)
                    section=p.img.sections[0]
                    end=int(w['address'],16)+w['bytes'];offset=end-f.va
                    tail=(b'\x43\xff\xe0' if kind=='indirect' else
                          b'\x43'+(b'\xe9' if kind=='jump' else b'\xe8')+
                          struct.pack('<i',loc['loop']-end-6))
                    section.raw=section.raw[:offset]+tail+section.raw[offset:]
                    section.size=len(section.raw)
                    f.hi=f.declared_hi=f.va+section.size-1;f.body_bytes=section.size
                    if cached:p.model.refs_to[loc['loop']]=[('jmp',end+1)]
                    with self.assertRaisesRegex(ValueError,'zero register|unresolved indirect entry'):
                        E.typed_list_loop(p,f,w)

    def test_pre_zero_entry_rejects_other_control_transfers(self):
        for prefix in (b'\xcb',b'\xcf',b'\xcd\x80',b'\xf4',b'\x0f\x34',
                       b'\xea\x00\x00\x42\x00\x08\x00',
                       b'\x9a\x00\x00\x42\x00\x08\x00'):
            with self.subTest(prefix=prefix.hex()):
                p,f,w,_=self.fixture(zero=True,pre_zero=prefix)
                with self.assertRaisesRegex(ValueError,'zero register|unresolved indirect entry'):
                    E.typed_list_loop(p,f,w)

    def test_fresh_relative_bypass_is_refused_without_cached_reference(self):
        for opcode in (b'\xe9',b'\xe8',b'\x0f\x85'):
            for interior in (0,1):
                with self.subTest(opcode=opcode.hex(),interior=interior):
                    p,f,w,loc=self.fixture()
                    section=p.img.sections[0]
                    end=int(w['address'],16)+w['bytes'];offset=end-f.va
                    tail=opcode+struct.pack('<i',loc['call']+interior-end-len(opcode)-4)
                    section.raw=section.raw[:offset]+tail+section.raw[offset:]
                    section.size=len(section.raw);f.body_bytes=section.size
                    f.hi=f.declared_hi=f.va+section.size-1
                    with self.assertRaisesRegex(ValueError,'bypassing entry'):
                        E.typed_list_loop(p,f,w)


class TypedListWitnessTests(unittest.TestCase):
    def fixture(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);root=Path(tmp.name)
        source=root/'Owner.cpp'
        source.write_text('void Host::Run()\n{\n DeviceObject* item = list;\n while(item)\n {\n'
                          '  item->Run();\n  item=item->mNext;\n }\n}\n')
        p,f,w,_=TypedListLoopTests().fixture()
        first=p.img.sections[0].raw[:-2]
        second=p.img.sections[0].raw[1:].replace(struct.pack('<I',0x710100),struct.pack('<I',0x710104))
        delta=len(first)-1
        w2=copy.deepcopy(w)
        for key in ('address','callAddress'):w2[key]=hex(int(w2[key],16)+delta)
        w2['head']='0x710104'
        caller=first+second
        lo=int(w2['address'],16)-f.va
        w2['sha256']=hashlib.sha256(caller[lo:lo+w2['bytes']]).hexdigest()
        bodies={f.va:caller,0x411900:b'\xc3',0x411910:b'\xc3',0x412100:b'\xc3',
            0x412000:(b'\xc7\x01'+struct.pack('<I',0x610100)+b'\xa1'+struct.pack('<I',0x710100)+
                      b'\x8b\x40\x0c\xa1'+struct.pack('<I',0x710104)+b'\x8b\x40\x0c\xc3')}
        code=bytearray(0x1200)
        for va,raw in bodies.items():code[va-0x411000:va-0x411000+len(raw)]=raw
        data=bytearray(0x500)
        def word(va,value):struct.pack_into('<I',data,va-0x610000,value)
        tables=[SimpleNamespace(va=0x610100,klass='DeviceObject',offset=0,slots=[0x411920]*6+[0x411900]),
                SimpleNamespace(va=0x610200,klass='Child',offset=0,slots=[0x411920]*6+[0x411910])]
        for t,col in zip(tables,(0x610300,0x610400)):
            word(t.va-4,col)
            for slot,target in enumerate(t.slots):word(t.va+4*slot,target)
        sections=[E.Section('.text',0x411000,len(code),bytes(code),0x60000020),
                  E.Section('.rdata',0x610000,len(data),bytes(data),0x40000040)]
        def read(a,n):
            sec=next((s for s in sections if s.start<=a and a+n<=s.start+len(s.raw)),None)
            return sec.raw[a-sec.start:a-sec.start+n] if sec else b''
        pe=bytearray(0x100);pe[:2]=b'MZ';struct.pack_into('<I',pe,0x3c,0x80)
        pe[0x80:0x84]=b'PE\0\0';struct.pack_into('<H',pe,0x84,0x14c);struct.pack_into('<H',pe,0x98,0x10b)
        img=SimpleNamespace(sha256='a'*64,read=read,sections=sections,data=bytes(pe),
            u32=lambda a:struct.unpack('<I',read(a,4))[0],
            section_of=lambda a:next((s for s in sections if s.contains(a)),None))
        funcs=[E.Func(a,'Fallible_'+hex(a),'USER_DEFINED',a,a+len(raw)-1,'','',False,'',False,
                      1,len(raw),a+len(raw)-1) for a,raw in sorted(bodies.items())]
        bases={'DeviceObject':[('DeviceObject',0)],'Child':[('Child',0),('DeviceObject',0)]}
        rtti=SimpleNamespace(vtables=tables,class_bases=bases,fixed_bases=copy.deepcopy(bases))
        model=SimpleNamespace(rtti=rtti,insns=[i for fn in funcs for i in E.decode_entry_body(img,fn)],
                              refs_to={},data_ptrs_to={})
        prog=E.Program(img,model,funcs)
        pin=lambda a:dict(address=hex(a),bytes=len(bodies[a]),sha256=hashlib.sha256(bodies[a]).hexdigest())
        anchor=dict(table='0x610100',slot=6,method='Run',callerIdentityEvidence='Reviewed synthetic caller',
                    caller=pin(f.va),loops=[w,w2],identityBodies=[pin(0x412100)|{'evidence':'Synthetic distinction'}],
                    source=dict(file=source.name,sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                                function='Host::Run',line=6,call='item->Run();'))
        doc=dict(kind='typed-list-interface-v1',specimenSha256=img.sha256,baseClass='DeviceObject',
                 baseTable='0x610100',receiverEvidence='Synthetic RTTI binding',sourceDivergences='Authored fixture',
                 layout=dict(body=pin(0x412000),heads=['0x710100','0x710104'],nextOffset=12,
                             evidence='Reviewed synthetic layout',supportBodies=[pin(0x412100)|{'evidence':'Synthetic support'}]),
                 anchors=[anchor])
        return root,prog,doc

    def check(self,root,prog,doc,family=False):
        with patch.object(E,'scan_rtti',return_value=prog.model.rtti):
            return (E.typed_list_virtuals if family else E.typed_list_witnesses)(prog,doc,root)

    def test_complete_authored_witness_and_family(self):
        root,p,d=self.fixture()
        self.assertEqual(self.check(root,p,d)[(0x610100,6)]['pop'],0)
        result=self.check(root,p,d,True)
        self.assertEqual([r['status'] for r in result['admission']['rows']],['mechanical-checks-pass']*2)
        self.assertEqual([r['status'] for r in result['proposals']['rows']],['rename']*2)

    def test_missing_review_and_stale_pins_cannot_be_replaced_by_saved_names(self):
        for change in ('specimen','source','body','overlap','receiver','identity','support','layout','call','duplicate','heads'):
            with self.subTest(change=change):
                root,p,d=self.fixture();a=d['anchors'][0]
                if change=='specimen':d['specimenSha256']='0'*64
                if change=='source':a['source']['sha256']='0'*64
                if change=='body':a['caller']['sha256']='0'*64
                if change=='overlap':p.funcs.append(E.Func(0x411001,'Overlap','USER_DEFINED',0x411001,0x411002,'','',False,'',False))
                if change=='receiver':d['receiverEvidence']=''
                if change=='identity':a['identityBodies']=[]
                if change=='support':d['layout']['supportBodies'][0]['evidence']=''
                if change=='layout':d['layout']['nextOffset']=8
                if change=='call':a['source']['call']='other->Run();'
                if change=='duplicate':d['anchors'].append(copy.deepcopy(a))
                if change=='heads':a['loops'][1]=copy.deepcopy(a['loops'][0])
                with self.assertRaises(ValueError):self.check(root,p,d)

    def test_source_condition_requires_matching_explicit_pc_specimen(self):
        for condition,platform,valid in [('TARGET == PC','PC',True),('UNKNOWN','PC',False),
                                         ('TARGET == PC',None,False),('TARGET == PC','other',False)]:
            with self.subTest(condition=condition,platform=platform):
                root,p,d=self.fixture();src=root/'Owner.cpp'
                src.write_text('#if '+condition+'\n'+src.read_text()+'#endif\n')
                a=d['anchors'][0]['source'];a.update(line=7,sha256=hashlib.sha256(src.read_bytes()).hexdigest())
                if platform:a['platform']=platform
                if valid:
                    self.check(root,p,d)
                    p.img.data=b'not PE'
                with self.assertRaises(ValueError):self.check(root,p,d)

    def test_family_refuses_ambiguous_or_uncovered_ownership(self):
        for change,status in [('fixed','unmapped-vtable-aliases'),('repeated','unmapped-vtable-aliases'),
                              ('secondary','unmapped-vtable-aliases'),('extra','extra-noncode-pointer-cells'),
                              ('holder','unmapped-vtable-aliases')]:
            with self.subTest(change=change):
                root,p,d=self.fixture()
                # Share one target so an excluded holder cannot silently vanish.
                t=p.model.rtti.vtables[1];t.slots[6]=0x411900
                sec=p.img.sections[1];raw=bytearray(sec.raw);struct.pack_into('<I',raw,t.va+24-sec.start,0x411900)
                if change=='extra':struct.pack_into('<I',raw,0x20,0x411900)
                sec.raw=bytes(raw);p=E.Program(p.img,p.model,p.funcs)
                if change=='fixed':p.fixed_bases['Child']=[('Child',0)]
                if change=='repeated':p.bases['Child'].append(('DeviceObject',4))
                if change=='secondary':t.offset=4;p=E.Program(p.img,p.model,p.funcs)
                if change=='holder':p.slots[0x411900].append(('Other',0,1,0x610480))
                result=self.check(root,p,d,True)
                self.assertEqual(result['rows'][0]['status'],status)
                self.assertEqual(result['admission']['rows'][0]['status'],'withheld')


class AggregateCopyTests(unittest.TestCase):
    def fixture(self, *, matrix=False, words=4, argument=4, eax_clobber=False,
                restore=True, receiver=True, extra=b'', interior=False):
        # Authored machine-code fixtures use an arbitrary member offset and
        # register allocation; no retail body or address is embedded here.
        raw = bytearray(b'\x8b\x44\x24' + bytes([argument]))
        if matrix:
            raw += b'\x56\x57\x8d\x71\x20\x8b\xf8\xb9' + struct.pack('<I', words)
            raw += b'\xf3\xa5'
            if restore:
                raw += b'\x5f\x5e'
        else:
            for n in range(words):
                raw += bytes([0x8b, 0x51 if receiver else 0x53, 0x20+4*n])
                raw += bytes([0x89, 0x50, 4*n])
        if eax_clobber:
            raw += b'\xb8\x00\x00\x00\x00'
        raw += extra + b'\xc2\x04\x00'
        start = 0x401000
        img = SimpleNamespace(sections=[E.Section('.text', start, len(raw), bytes(raw), 0x60000020)],
                              read=lambda a, n: bytes(raw[a-start:a-start+n]),
                              section_of=lambda a: E.Section('.text', start, len(raw), bytes(raw), 0x60000020))
        fn = E.Func(start, 'fallible', 'USER_DEFINED', start, start+len(raw)-1,
                    '', '', False, '', False, 1, len(raw), start+len(raw)-1)
        refs = {start+4: [('jmp', 0x402000)]} if interior else {}
        return SimpleNamespace(img=img, funcs=[fn], model=SimpleNamespace(refs_to=refs)), fn

    def test_exact_vector_copy_and_direction_clear_matrix_copy(self):
        for matrix, words in [(False, 4), (True, 12)]:
            with self.subTest(matrix=matrix):
                prog, fn = self.fixture(matrix=matrix, words=words)
                proof = E.aggregate_copy_leaf(prog, fn, words*4)
                self.assertEqual(proof['resultBytes'], words*4)
                self.assertEqual(proof['memberOffset'], 0x20)
                self.assertEqual(proof['eax'], 'result destination')
                self.assertEqual(proof['returnPop'], 4)
                self.assertEqual(proof['directionFlagClearRequired'], matrix)

    def test_refuses_missing_extra_or_misdirected_words_and_return_pointer_loss(self):
        for kwargs in ({'words': 3}, {'words': 5}, {'argument': 8}, {'receiver': False},
                       {'eax_clobber': True}, {'interior': True},
                       {'matrix': True, 'words': 4, 'restore': False},
                       {'matrix': True, 'words': 3}, {'extra': b'\xfd'},
                       {'extra': b'\x83\xc4\x04'}, {'extra': b'\xff\xd2'},
                       {'extra': b'\x8b\x91\x00\x10\x00\x00'},
                       {'extra': b'\x83\xc1\xf0'},
                       {'extra': b'\x89\xcb'}):
            with self.subTest(kwargs=kwargs):
                prog, fn = self.fixture(**kwargs)
                with self.assertRaises(ValueError):
                    E.aggregate_copy_leaf(prog, fn, 16)

    def test_refuses_stub_forwarder_and_opaque_boundary(self):
        prog, fn = self.fixture()
        for raw in (b'\xc2\x04\x00', b'\x8b\x01\xff\x20'):
            with self.subTest(raw=raw.hex()):
                fn.hi = fn.declared_hi = fn.va+len(raw)-1
                fn.body_bytes = len(raw)
                prog.img.read = lambda a, n: raw[a-fn.va:a-fn.va+n]
                with self.assertRaises(ValueError):
                    E.aggregate_copy_leaf(prog, fn, 16)
        prog, fn = self.fixture()
        fn.body_ranges = 2
        with self.assertRaisesRegex(ValueError, 'boundary'):
            E.aggregate_copy_leaf(prog, fn, 16)

    def test_only_bounded_word_extents(self):
        for count in (True, None, 0, 3, 18, 260):
            with self.subTest(count=count), self.assertRaises(ValueError):
                E.aggregate_copy_leaf(None, None, count)

    def test_cached_and_uncached_interior_pointer_words_are_refused(self):
        for cached in (False, True):
            with self.subTest(cached=cached):
                prog, fn = self.fixture()
                if cached:
                    prog.model.data_ptrs_to = {fn.va+7: [0x600000]}
                else:
                    # Unaligned final word in executable data, missing from
                    # both instruction and data-pointer model references.
                    raw = b'\x90' + struct.pack('<I', fn.va+7)
                    prog.img.sections = [E.Section('.text', 0x402000, len(raw), raw, 0x60000020)]
                with self.assertRaisesRegex(ValueError, 'interior entry'):
                    E.aggregate_copy_leaf(prog, fn, 16)

    def test_missing_complete_section_evidence_is_not_a_clean_census(self):
        prog, fn = self.fixture()
        del prog.img.sections
        with self.assertRaisesRegex(ValueError, 'complete image sections'):
            E.aggregate_copy_leaf(prog, fn, 16)

    def test_duplicate_permuted_and_wrapping_source_words_are_refused(self):
        for mode in ('duplicate-source', 'permuted-source', 'duplicate-destination',
                     'negative-add', 'negative-lea', 'overflowing-rep'):
            with self.subTest(mode=mode):
                prog, fn = self.fixture(matrix=mode=='overflowing-rep')
                raw = bytearray(prog.img.read(fn.va, fn.body_bytes))
                if mode == 'duplicate-source': raw[12] = 0x20
                if mode == 'permuted-source': raw[6], raw[12] = raw[12], raw[6]
                if mode == 'duplicate-destination': raw[15] = 0
                if mode == 'negative-add': raw[4:4] = b'\x83\xc1\xc0'
                if mode == 'negative-lea': raw[4:4] = b'\x8d\x49\xc0'
                if mode == 'overflowing-rep': raw[6:9] = b'\x8d\xb1\xfc\xff\xff\x7f'
                fn.hi = fn.declared_hi = fn.va+len(raw)-1
                fn.body_bytes = len(raw)
                prog.img.read = lambda a, n: bytes(raw[a-fn.va:a-fn.va+n])
                prog.img.sections = [E.Section('.text', fn.va, len(raw), bytes(raw), 0x60000020)]
                with self.assertRaises(ValueError):
                    E.aggregate_copy_leaf(prog, fn, 16)


class AggregateInterfaceTests(unittest.TestCase):
    def fixture(self, *, side_store=False, extra=b'', prefix_extra=b'', displacement=0x10):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root/'types.h').write_text('class Child : public Base { public: virtual Vector Get(); };\n')
        source = root/'Caller.cpp'
        source.write_text('Host::Host(Base *cam)\n{\n Vector value = cam->Get();\n}\n')
        classes = E.header_classes(root, set())
        method = classes['Child'].methods[0]
        leaf_prog, leaf = AggregateCopyTests().fixture()
        caller = 0x402000
        raw = bytearray(b'\x53\x56\x83\xec\x40\x8b\xf1')
        raw += prefix_extra
        load = caller+len(raw)
        raw += b'\x8b\x5c\x24\x4c'  # entry+4, after 0x48-byte stack use
        raw += extra
        window = caller+len(raw)
        raw += b'\x8d\x44\x24' + bytes([displacement]) + b'\x50'
        if side_store:
            raw += b'\x89\x4e\x0c'
        raw += b'\x8b\x13\x8b\xcb'
        call = caller+len(raw)
        raw += b'\xff\x12\x83\xc4\x40\x5e\x5b\xc2\x04\x00'
        memory = {leaf.va+i:v for i,v in enumerate(leaf_prog.img.read(leaf.va,leaf.body_bytes))}
        memory.update({caller+i:v for i,v in enumerate(raw)})
        tables = [SimpleNamespace(va=0x600000,klass='Base',offset=0,slots=[leaf.va]),
                  SimpleNamespace(va=0x600100,klass='Child',offset=0,slots=[leaf.va])]
        for table in tables:
            memory.update({table.va+i:v for i,v in enumerate(struct.pack('<I',leaf.va))})
        read=lambda a,n:bytes(memory.get(a+i,0) for i in range(n))
        img=SimpleNamespace(sha256='a'*64,read=read,u32=lambda a:struct.unpack('<I',read(a,4))[0],
                            sections=[E.Section('.text',leaf.va,0x2000,read(leaf.va,0x2000),0x60000020)],
                            section_of=lambda a:E.Section('.text',a,0x1000,read(a,0x1000),0x60000020))
        f=E.Func(caller,'untrusted','USER_DEFINED',caller,caller+len(raw)-1,'','',False,'',False,
                 1,len(raw),caller+len(raw)-1)
        bases={'Base':[('Base',0)],'Child':[('Child',0),('Base',0)]}
        model=SimpleNamespace(insns=[],refs_to={},rtti=SimpleNamespace(vtables=tables,class_bases=bases,fixed_bases=bases))
        prog=E.Program(img,model,[leaf,f])
        model.insns=[i for fn in prog.funcs for i in E.decode_entry_body(img,fn)]
        pin=lambda fn:dict(address=hex(fn.va),bytes=fn.body_bytes,sha256=hashlib.sha256(read(fn.va,fn.body_bytes)).hexdigest())
        witness=dict(kind='member-result-buffer',table=hex(tables[0].va),evidence='Synthetic interface call',
            resultTypeEvidence='Authored Vector object transported as sixteen bytes by a complete copy leaf.',
            receiverEvidence='Synthetic argument transport',caller=pin(f),receiverRegister='ebx',
            receiverLoad=hex(load),windowStart=hex(window),callAddress=hex(call),resultType='Vector',
            resultBytes=16,memberOffset=0x20,
            source=dict(file='Caller.cpp',sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        function='Host::Host',line=3,call='Vector value = cam->Get();'))
        witness['class']='Base'
        anchor=dict(table=hex(tables[1].va),offset=0,slot=0,target=hex(leaf.va),method='Get',parameters=[],
                    qualifiers='',sourceFile=method.file,sourceLine=method.line,body=pin(leaf),
                    evidence='Synthetic exact member copy',interfaceDispatch=witness)
        anchor['class']='Child'
        return root,classes,prog,anchor,memory

    def invoke(self, root, classes, prog, anchor):
        return E.common_interface_witness(prog,classes['Child'],classes['Child'].methods[0],
                                         prog.model.rtti.vtables[1],anchor,root)

    def test_explicit_result_witness_with_and_without_caller_object_store(self):
        for side_store in (False,True):
            with self.subTest(side_store=side_store):
                root,classes,prog,a,_=self.fixture(side_store=side_store)
                table,pop=self.invoke(root,classes,prog,a)
                self.assertEqual((table.klass,pop),('Base',4))

    def test_mutant_transport_still_refuses_when_hashes_are_refreshed(self):
        for mode in ('argument','receiver','vptr','slot','result','side-store','prefix-esp'):
            with self.subTest(mode=mode):
                root,classes,prog,a,m=self.fixture(side_store=True)
                w=a['interfaceDispatch']; load=int(w['receiverLoad'],16)
                start=int(w['windowStart'],16);call=int(w['callAddress'],16)
                if mode=='argument':m[load+3]+=4
                if mode=='receiver':m[call-1]=0xca
                if mode=='vptr':m[call-3]=0x10
                if mode=='slot':m[call+1]=0x52  # truncated/bad next byte also refuses
                if mode=='result':m[start+4]=0x51
                if mode=='side-store':m[start+6]=0x4b
                if mode=='prefix-esp':m[0x402004]=0xf0
                for pin in (w['caller'],a['body']):
                    pin['sha256']=hashlib.sha256(prog.img.read(int(pin['address'],16),pin['bytes'])).hexdigest()
                with self.assertRaises(ValueError):self.invoke(root,classes,prog,a)

    def test_receiver_clobbers_and_unbounded_result_displacements_refuse(self):
        for extra in (b'\x31\xdb',b'\x93',b'\x5b',b'\x66\x89\xcb',b'\x88\xcb',b'\x61',b'\xeb\x00'):
            with self.subTest(extra=extra.hex()):
                root,classes,prog,a,_=self.fixture(extra=extra)
                with self.assertRaises(ValueError):self.invoke(root,classes,prog,a)
        root,classes,prog,a,_=self.fixture(displacement=0xf0)
        with self.assertRaises(ValueError):self.invoke(root,classes,prog,a)

    def test_prefix_stack_mutation_and_partial_object_clobbers_are_refused(self):
        for prefix in (b'\x66\x53', b'\x66\x68\x01\x00',
                       b'\xc7\x44\x24\x4c\x78\x56\x34\x12',
                       b'\x66\x89\x44\x24\x4c', b'\x89\x45\x04',
                       b'\x66\x89\xc4'):
            with self.subTest(prefix=prefix.hex()):
                root,classes,prog,a,_=self.fixture(prefix_extra=prefix)
                with self.assertRaises(ValueError):self.invoke(root,classes,prog,a)
        for extra in (b'\x66\x89\xc6',b'\x89\xc6'):
            with self.subTest(extra=extra.hex()):
                root,classes,prog,a,_=self.fixture(extra=extra,side_store=True)
                with self.assertRaises(ValueError):self.invoke(root,classes,prog,a)

    def test_later_entry_is_irrelevant_unless_it_can_branch_back(self):
        root,classes,prog,a,m=self.fixture();w=a['interfaceDispatch']
        end=int(w['callAddress'],16)+2
        prog.model.refs_to[end]=[('jmp',0x403000)]
        self.assertEqual(self.invoke(root,classes,prog,a)[1],4)
        # A later local branch back could let that outside entry bypass the
        # receiver definition. Keep the full caller pin and decode, even though
        # raw-pointer protection stops immediately after the selected CALL.
        raw=b'\xe9'+struct.pack('<i',int(w['windowStart'],16)-end-5)
        m.update({end+i:v for i,v in enumerate(raw)})
        w['caller']['sha256']=hashlib.sha256(prog.img.read(0x402000,w['caller']['bytes'])).hexdigest()
        with self.assertRaisesRegex(ValueError,'interior entry'):self.invoke(root,classes,prog,a)

    def test_scalar_return_and_unresolved_source_conditions_are_refused(self):
        for result in ('int','float','bool','DWORD'):
            with self.subTest(result=result):
                root,classes,prog,a,_=self.fixture()
                p=root/'Caller.cpp';p.write_text(p.read_text().replace('Vector',result))
                a['interfaceDispatch']['source'].update(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                    call=f'{result} value = cam->Get();')
                a['interfaceDispatch']['resultType']=result
                classes['Child'].methods[0].head='virtual '+result
                with self.assertRaisesRegex(ValueError,'scalar return'):self.invoke(root,classes,prog,a)
        for condition in ('#if 0','#if TARGET == CONSOLE'):
            with self.subTest(condition=condition):
                root,classes,prog,a,_=self.fixture();p=root/'Caller.cpp'
                p.write_text(condition+'\n'+p.read_text()+'#endif\n')
                a['interfaceDispatch']['source'].update(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),line=4)
                with self.assertRaisesRegex(ValueError,'conditions'):self.invoke(root,classes,prog,a)

    def test_later_indirect_tail_cannot_silently_reenter_protected_prefix(self):
        root,classes,prog,a,m=self.fixture();w=a['interfaceDispatch']
        end=int(w['callAddress'],16)+2
        m.update({end:0xff,end+1:0xe0,end+2:0x90})
        w['caller']['sha256']=hashlib.sha256(prog.img.read(0x402000,w['caller']['bytes'])).hexdigest()
        with self.assertRaisesRegex(ValueError,'interior entry'):self.invoke(root,classes,prog,a)

    def test_source_pins_extent_and_complete_boundary_are_required(self):
        for mode in ('source-hash','source-call','source-owner','source-type','decl-line',
                     'body-hash','result-extent','member-offset','ranges','overlap','interior','no-sections'):
            with self.subTest(mode=mode):
                root,classes,prog,a,_=self.fixture();w=a['interfaceDispatch']
                if mode=='source-hash':w['source']['sha256']='0'*64
                if mode=='source-call':w['source']['call']='Vector value = cam->Wrong();'
                if mode=='source-owner':w['source']['function']='Other::Other'
                if mode=='source-type':w['resultType']='Matrix'
                if mode=='decl-line':a['sourceLine']+=1
                if mode=='body-hash':w['caller']['sha256']='0'*64
                if mode=='result-extent':w['resultBytes']=12
                if mode=='member-offset':w['memberOffset']=0x24
                if mode=='ranges':prog.by_va[0x402000].body_ranges=2
                if mode=='overlap':
                    prog.funcs.append(E.Func(0x402005,'fallible','USER_DEFINED',0x402005,
                                            0x402006,'','',False,'',False,1,2,0x402006))
                if mode=='interior':prog.model.refs_to[0x402004]=[('jmp',0x403000)]
                if mode=='no-sections':del prog.img.sections
                with self.assertRaises(ValueError):self.invoke(root,classes,prog,a)


class TaggedCallTests(unittest.TestCase):
    def fixture(self, transport='member', clause='ENGINE.Deserialize(&c);'):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        source = root/'Loader.cpp'
        source.write_text('void Host::Load() {\n CChunkReader &c = *reader;\n'
                          ' Log("loader witness");\n if (tag==MKID("ERES")) {\n'
                          +clause+'\n }\n}\n')
        start, producer, target, literal = 0x401000, 0x402000, 0x403000, 0x600000
        raw = bytearray()
        def emit(b):
            va = start+len(raw); raw.extend(b); return va
        def call(address):
            va=start+len(raw); return emit(b'\xe8'+struct.pack('<i',address-va-5))
        diagnostic=emit(b'\x68'+struct.pack('<I',literal+16))
        emit(b'\x83\xc4\x04\xbe\x00\x00\x70\x00\x8b\xce')
        produced=call(producer)
        guard=emit(b'\x85\xed\x75\x00')
        block=start+len(raw)
        pattern=(b'\x0f\xbe\x0d'+struct.pack('<I',literal+3)
                 +b'\x0f\xbe\x15'+struct.pack('<I',literal+2)
                 +b'\xc1\xe1\x08\x03\xca\x0f\xbe\x15'+struct.pack('<I',literal+1)
                 +b'\xc1\xe1\x08\x03\xca\x0f\xbe\x15'+struct.pack('<I',literal)
                 +b'\xc1\xe1\x08\x03\xca\x3b\xc1')
        emit(pattern); branch=emit(b'\x75\x00')
        if transport=='member':emit(b'\x56\xb9'+struct.pack('<I',0x700000))
        else:emit(b'\x56\x55')
        site=call(target)
        if transport!='member':emit(b'\x83\xc4\x08')
        jump=emit(b'\xeb\x00'); end=emit(b'\xc3')
        raw[guard-start+3]=end-guard-4
        raw[branch-start+1]=end-branch-2
        raw[jump-start+1]=end-jump-2
        memory={}
        for a,b in [(start,bytes(raw)),(producer,b'\x8b\x01\xc3'),
                    (target,b'\xc2\x04\x00' if transport=='member' else b'\xc3'),
                    (literal,b'ERES\0'),(literal+16,b'loader witness\0')]:
            memory.update({a+i:v for i,v in enumerate(b)})
        read=lambda a,n:bytes(memory.get(a+i,0) for i in range(n))
        def section(a):
            return E.Section('.text',a,4096,read(a,4096),0x60000020)
        img=SimpleNamespace(sha256='a'*64,read=read,section_of=section,
                            cstring=lambda a:read(a,64).split(b'\0')[0].decode('ascii'))
        fns=[E.Func(a,'fallible','USER_DEFINED',a,a+n-1,'','',False,'',False,1,n,a+n-1)
             for a,n in [(start,len(raw)),(producer,3),(target,3 if transport=='member' else 1)]]
        insns=[i for f in fns for i in E.decode_entry_body(img,f)]
        model=SimpleNamespace(insns=insns,refs_to={},rtti=SimpleNamespace(vtables=[],class_bases={},fixed_bases={}))
        prog=E.Program(img,model,fns)
        def pin(a):
            f=prog.by_va[a];return dict(address=hex(a),bytes=f.body_bytes,sha256=hashlib.sha256(read(a,f.body_bytes)).hexdigest())
        claim=dict(tag='ERES',start=hex(block),call=hex(site),target=pin(target),
                   arguments=['reader'] if transport=='member' else ['zero','reader'])
        if transport=='member':claim['receiver']='0x700000'
        doc=dict(specimenSha256=img.sha256,caller=pin(start),
                 source=dict(file=source.name,sha256=hashlib.sha256(source.read_bytes()).hexdigest(),function='Host::Load'),
                 identityEvidence='Synthetic independently rooted caller',
                 diagnostics=[dict(address=hex(literal+16),site=hex(diagnostic),text='loader witness')],
                 producer=dict(pin(producer),calls=[hex(produced)]),calls=[claim])
        return root,prog,doc,memory,dict(block=block,branch=branch,guard=guard,call=site,end=end,producer=produced)

    def test_member_and_guarded_zero_transport(self):
        for transport in ('member','cdecl'):
            with self.subTest(transport=transport):
                root,prog,doc,_,_=self.fixture(transport)
                report=E.tagged_call_witnesses(prog,doc,root)
                self.assertEqual(report['rows'][0]['status'],'tag-call-and-source-clause')
                self.assertEqual(report['rows'][0]['sourceCall'],'ENGINE.Deserialize(&c);')
                self.assertFalse(report['rows'][0]['indirectCalleeFlow'])

    def test_conditional_source_does_not_choose_convenient_branch(self):
        clause='#if TARGET==XBOX\n SHADER.Deserialize(&c);\n#else\n c.Skip();\n#endif'
        root,prog,doc,_,_=self.fixture(clause=clause)
        self.assertEqual(E.tagged_call_witnesses(prog,doc,root)['rows'][0]['status'],'source-clause-withheld')
        doc['calls'][0]['sourceCall']='SHADER.Deserialize(&c);'
        with self.assertRaisesRegex(ValueError,'conditional'):E.tagged_call_witnesses(prog,doc,root)

    def test_outer_source_conditionals_are_withheld(self):
        for placement in ('clause','function','inactive'):
            with self.subTest(placement=placement):
                root,prog,doc,_,_=self.fixture()
                source=root/'Loader.cpp';text=source.read_text()
                if placement=='function':text='#if TARGET==XBOX\n'+text+'\n#endif\n'
                else:
                    text=text.replace(' if (tag',('#if 0\n' if placement=='inactive' else '#if TARGET==XBOX\n')+' if (tag')
                    text=text.replace(' }\n}', ' }\n#endif\n}')
                source.write_text(text);doc['source']['sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
                report=E.tagged_call_witnesses(prog,doc,root)
                self.assertEqual(report['rows'][0]['status'],'source-clause-withheld')

    def test_unreachable_return_after_exterior_tail_does_not_prove_cleanup(self):
        root,prog,doc,m,_=self.fixture()
        target=0x403000;raw=b'\xe9'+struct.pack('<i',0x404000-target-5)+b'\xc2\x04\x00'
        m.update({target+i:v for i,v in enumerate(raw)})
        f=prog.by_va[target];f.hi=f.declared_hi=target+len(raw)-1;f.body_bytes=len(raw)
        doc['calls'][0]['target'].update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        row=E.tagged_call_witnesses(prog,doc,root)['rows'][0]
        self.assertEqual(row['observedReturnPop'],[4])
        self.assertIsNone(row['reachableExplicitReturnPop'])
        self.assertEqual(row['unresolvedCalleeTargets'],['00404000'])

    def test_intra_caller_call_cannot_bypass_producer(self):
        root,prog,doc,m,sites=self.fixture()
        # Replace an unrelated five-byte pre-producer instruction by a CALL
        # to the discriminator start; all pins deliberately match the mutant.
        address=0x401008
        raw=b'\xe8'+struct.pack('<i',sites['block']-address-5)
        m.update({address+i:v for i,v in enumerate(raw)})
        doc['caller']['sha256']=hashlib.sha256(prog.img.read(0x401000,doc['caller']['bytes'])).hexdigest()
        prog.model.refs_to[sites['block']]=[('call',address)]
        with self.assertRaisesRegex(ValueError,'intra-caller'):E.tagged_call_witnesses(prog,doc,root)

    def test_byte_and_transport_adversaries(self):
        for change in ('tag','byte-order','equality','eax-clobber','reader-clobber','receiver',
                       'callee-interior','ret-pop','zero-not-guarded','producer-receiver','reader-omitted'):
            with self.subTest(change=change):
                root,prog,doc,m,sites=self.fixture('cdecl' if change=='zero-not-guarded' else 'member')
                b=sites['block'];p=sites['producer']
                if change=='tag':m[0x600000]=ord('T')
                if change=='byte-order':m[b+10]+=1
                if change=='equality':m[sites['branch']]=0x74
                if change=='eax-clobber':m[sites['guard']]=0x31;m[sites['guard']+1]=0xc0
                if change=='reader-clobber':m[sites['guard']]=0x31;m[sites['guard']+1]=0xf6
                if change=='receiver':m[sites['branch']+4]+=1
                if change=='reader-omitted':
                    m[sites['branch']+2]=0x55
                    doc['calls'][0]['arguments']=['zero']
                if change=='callee-interior':doc['calls'][0]['target']['address']='0x403001'
                if change=='ret-pop':m[0x403001]=8
                if change=='zero-not-guarded':m[sites['guard']+1]=0xdb
                if change=='producer-receiver':m[p-1]=0xcb
                # Deliberately refresh hashes: semantic gates must reject even
                # a freshly sealed but false assertion, not just stale bytes.
                for pin in (doc['caller'],doc['producer'],doc['calls'][0]['target']):
                    pin['sha256']=hashlib.sha256(prog.img.read(int(pin['address'],16),pin['bytes'])).hexdigest()
                with self.assertRaises(ValueError):E.tagged_call_witnesses(prog,doc,root)

    def test_interior_entry_and_source_identity_are_not_inferred_from_names(self):
        for change in ('interior-entry','producer-bypass','source-call','source-owner','source-hash','specimen','diagnostic','duplicate'):
            with self.subTest(change=change):
                root,prog,doc,_,sites=self.fixture()
                if change=='interior-entry':prog.model.refs_to[sites['call']]=[('jmp',0x404000)]
                if change=='producer-bypass':prog.model.refs_to[sites['producer']]=[('jmp',0x404000)]
                if change=='source-call':doc['calls'][0]['sourceCall']='OTHER.Deserialize(&c);'
                if change=='source-owner':doc['source']['function']='Wrong::Load'
                if change=='source-hash':doc['source']['sha256']='0'*64
                if change=='specimen':doc['specimenSha256']='0'*64
                if change=='diagnostic':doc['diagnostics'][0]['text']='absent'
                if change=='duplicate':doc['calls'].append(copy.deepcopy(doc['calls'][0]))
                with self.assertRaises(ValueError):E.tagged_call_witnesses(prog,doc,root)


class FakeImage:
    base = 0x400000

    def section_of(self, va):
        return object() if 0x401000 <= va < 0x700000 else None


class OverridePrefixTests(unittest.TestCase):
    def fixture(self, external=False):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        declaration = ('virtual void Run(int index, char* out);' if external else
                       'virtual void Run(char* out) { strcpy(out,"Menu"); }')
        (root/'types.h').write_text('class Child : public Base { public: '+declaration+' };\n')
        if external:
            (root/'Impl.cpp').write_text('void Child::Run(int index, char* out)\n{\n}\n')
        classes = E.header_classes(root, set()); method = classes['Child'].methods[0]
        tables = [E.Vtable(0x600000,'Base',0,[0x401000,0x401000,0x401010]),
                  E.Vtable(0x600100,'Child',0,[0x401100,0x401200,0x401010]),
                  E.Vtable(0x600200,'Peer',0,[0x401300,0x401200,0x401010])]
        raw = {0x401000:b'\xc2\x04\x00',0x401010:b'\xc2\x04\x00',
               0x401200:b'\xb8\x01\x00\x00\x00\xc2\x04\x00',
               0x401300:b'\xc2\x04\x00'}
        copy_leaf = bytes.fromhex('5657bf0000610083c9ff33c0f2aef7d12bf98bc18bf7'
                                  '8b7c240cc1e902f3a58bc883e103f3a45f5ec20400')
        raw[0x401100] = b'\xc2\x08\x00' if external else copy_leaf
        raw[0x402000] = bytes.fromhex('8bc133c9c700')+struct.pack('<I',tables[0].va)+bytes.fromhex('894804c3')
        def construct(va,table):
            return (b'\xb9'+struct.pack('<I',0x700000)+b'\xe8'+struct.pack('<i',0x402000-(va+10))
                    +b'\xc7\x05'+struct.pack('<II',0x700000,table)+b'\xc3')
        raw[0x402100]=construct(0x402100,tables[1].va)
        raw[0x402200]=construct(0x402200,tables[2].va)
        functions = [E.Func(a,'untrusted_'+hex(a),'USER_DEFINED',a,a+len(b)-1,'','',False,'',False,
                            1,len(b),a+len(b)-1) for a,b in sorted(raw.items())]
        for n,t in enumerate(tables):
            col=0x620000+32*n
            raw[t.va-4]=struct.pack('<I',col)
            raw[t.va]=struct.pack('<3I',*t.slots)
            raw[col]=b'\0'*12
        raw[0x610000]=b'Menu\0'
        memory={a+i:v for a,b in raw.items() for i,v in enumerate(b)}
        read=lambda a,n:bytes(memory.get(a+i,0) for i in range(n))
        section=E.Section('.text',0x401000,0x2000,read(0x401000,0x2000),0x60000020)
        img=SimpleNamespace(sha256='f'*64,read=read,u32=lambda a:struct.unpack('<I',read(a,4))[0],
                            section_of=lambda a:section if section.contains(a) else None,sections=[section])
        bases={'Base':[('Base',0)],'Child':[('Child',0),('Base',0)],'Peer':[('Peer',0),('Base',0)]}
        rtti=E.RttiModel({},bases,tables,copy.deepcopy(bases))
        model=SimpleNamespace(rtti=rtti,insns=[],refs_to={},refs_from={},strings={},data_ptrs_to={})
        prog=E.Program(img,model,functions)
        # Separate per-COL hierarchy: the aggregated model can conceal a second
        # differing CHD for the same class, so it is not this witness's oracle.
        census=SimpleNamespace(vtables={},cols={},hierarchies={})
        for n,t in enumerate(tables):
            col=0x620000+32*n;chd=0x621000+64*n
            census.vtables[t.va]=SimpleNamespace(col_va=col)
            census.cols[col]=SimpleNamespace(hierarchy_va=chd,offset=0,cd_offset=0)
            census.hierarchies[chd]=SimpleNamespace(rows=[
                SimpleNamespace(descriptor=SimpleNamespace(class_name=name,mdisp=offset,pdisp=-1,vdisp=0),
                                parent_index=None if j==0 else 0)
                for j,(name,offset) in enumerate(bases[t.klass])])
        prog.test_raw_rtti=census;img.data=b'authored RTTI fixture'
        model.insns=[i for f in functions for i in E.decode_entry_body(img,f)]
        prog.insn_vas=[i.va for i in model.insns]
        pin=lambda a:dict(address=hex(a),bytes=prog.by_va[a].body_bytes,
                          sha256=hashlib.sha256(read(a,prog.by_va[a].body_bytes)).hexdigest())
        if external:
            f=E.index_source(root)[0];filename,line,definition=f.file,f.line,f.body
        else:filename,line,definition=method.file,method.line,method.body
        source=dict(file=filename,line=line,function='Child::Run',inline=not external,
                    sha256=hashlib.sha256((root/filename).read_bytes()).hexdigest(),
                    bodySha256=hashlib.sha256(definition.encode()).hexdigest(),correspondence='Authored fixture')
        w=dict(kind='reviewed-override-primary-prefix',table=hex(tables[0].va),slotCount=3,abstractPrefix=2,
               concreteSuffix=[hex(0x401010)],familyTables=[hex(t.va) for t in tables],
               evidence='Authored fixed prefix',sourceDivergences='None in this fixture',
               inheritancePremise='Direct primary prefix',definition=source,baseConstruction=pin(0x402000),
               constructions=[dict(table=hex(t.va),body=pin(a),windowStart=hex(a),receiver='0x700000',
                                   evidence='Authored same object installation')
                              for t,a in zip(tables[1:],(0x402100,0x402200))])
        w['class']='Base'
        anchor=dict(table=hex(tables[1].va),offset=0,slot=0,target=hex(0x401100),method='Run',
                    parameters=list(method.parameters),qualifiers=method.qualifiers,
                    sourceFile=method.file,sourceLine=method.line,body=pin(0x401100),
                    evidence='Authored override',interfaceDispatch=w)
        anchor['class']='Child'
        return root,classes,prog,dict(specimenSha256=img.sha256,anchors=[anchor]),memory,pin

    def invoke(self, root, classes, prog, document):
        with patch.object(E,'scan_rtti',return_value=copy.deepcopy(prog.model.rtti)), \
                patch('re_rtti_vtables.parse_rtti',return_value=prog.test_raw_rtti):
            return E.propagate_vtable_anchors(prog,classes,document,root)

    def test_literal_and_external_definition_transfer_existing_prefix_role(self):
        for external in (False,True):
            with self.subTest(external=external):
                root,classes,prog,d,_,_=self.fixture(external)
                report=self.invoke(root,classes,prog,d)
                self.assertEqual(len(report['rows']),3)
                self.assertEqual({u['method'] for r in report['rows'] for u in r['uses']},{'Run'})

    def test_same_width_slot_swap_cannot_substitute_action_for_literal_copy(self):
        root,classes,prog,d,_,pin=self.fixture();a=d['anchors'][0]
        a.update(slot=1,target='0x401200',body=pin(0x401200))  # RET4 still agrees
        with self.assertRaisesRegex(ValueError,'literal copy'):
            self.invoke(root,classes,prog,d)

    def test_shortened_body_and_appended_slot_are_not_override_evidence(self):
        for change in ('short','appended','missing-family','duplicate-family','suffix','constructor-count'):
            with self.subTest(change=change):
                root,classes,prog,d,_,pin=self.fixture();a=d['anchors'][0];w=a['interfaceDispatch']
                if change=='short':a['body'].update(bytes=1,sha256=hashlib.sha256(prog.img.read(0x401100,1)).hexdigest())
                if change=='appended':a.update(slot=2,target='0x401010',body=pin(0x401010))
                if change=='missing-family':w['familyTables'].pop()
                if change=='duplicate-family':w['familyTables'].append(w['familyTables'][-1])
                if change=='suffix':w['concreteSuffix']=['0x401200']
                if change=='constructor-count':w['constructions']=w['constructions'][:1]
                with self.assertRaises(ValueError):self.invoke(root,classes,prog,d)

    def test_changed_receiver_col_literal_and_cached_body_refuse(self):
        for change in ('receiver','col-offset','col-construction','literal','cache','fixed-base','overlap'):
            with self.subTest(change=change):
                root,classes,prog,d,m,pin=self.fixture();w=d['anchors'][0]['interfaceDispatch']
                if change=='receiver':
                    m[0x402100+12]=4  # store at global+4, while call still receives global
                    prog.model.insns=[i for f in prog.funcs for i in E.decode_entry_body(prog.img,f)]
                    prog.insn_vas=[i.va for i in prog.model.insns]
                    w['constructions'][0]['body']=pin(0x402100)
                if change=='col-offset':m[0x620000+32+4]=4
                if change=='col-construction':m[0x620000+32+8]=4
                if change=='literal':m[0x610000]=ord('X')
                if change=='cache':next(i for i in prog.model.insns if i.va==0x401200).ops='eax,0x2'
                if change=='fixed-base':prog.model.rtti.fixed_bases['Peer']=[('Peer',0)]
                if change=='overlap':prog.by_va[0x401010].declared_hi=0x401101
                with self.assertRaises(ValueError):self.invoke(root,classes,prog,d)

    def test_definition_identity_order_return_and_conditions_refuse(self):
        for change in ('function','line','order','return','conditional','duplicate','method-macro','owner-macro'):
            with self.subTest(change=change):
                root,classes,prog,d,_,_=self.fixture(external=True)
                source=d['anchors'][0]['interfaceDispatch']['definition'];path=root/source['file']
                if change=='function':source['function']='Other::Run'
                if change=='line':source['line']+=1
                if change=='order':path.write_text('void Child::Run(char* out, int index)\n{\n}\n')
                if change=='return':path.write_text('int Child::Run(int index, char* out)\n{\n}\n')
                if change=='conditional':path.write_text('void Child::Run(int index, char* out)\n{\n#if MAYBE\n#endif\n}\n')
                if change=='duplicate':path.write_text(path.read_text()*2)
                if change=='method-macro':path.write_text('#define Run Other\n'+path.read_text())
                if change=='owner-macro':path.write_text('#define Child Other\n'+path.read_text())
                source['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
                if change=='conditional':source['bodySha256']=hashlib.sha256(E.index_source(root)[0].body.encode()).hexdigest()
                if change.endswith('-macro'):source['line']=E.index_source(root)[0].line
                with self.assertRaises(ValueError):self.invoke(root,classes,prog,d)

    def test_unmapped_alias_is_not_named_and_saved_names_are_not_inputs(self):
        root,classes,prog,d,_,_=self.fixture()
        prog.slots[0x401100].append(('Unrelated',0,9,0x630000))
        report=self.invoke(root,classes,prog,d)
        row=next(r for r in report['rows'] if int(r['target'],16)==0x401100)
        self.assertEqual(row['status'],'unmapped-vtable-aliases')
        before=copy.deepcopy(report)
        for f in prog.funcs:f.name='convincing_but_wrong_'+hex(f.va)
        self.assertEqual(self.invoke(root,classes,prog,d),before)

    def test_reviewed_inline_conditions_and_numeric_construction_identity(self):
        for change in ('inline-condition','duplicate-construction'):
            with self.subTest(change=change):
                root,classes,prog,d,_,_=self.fixture();a=d['anchors'][0];w=a['interfaceDispatch']
                if change=='inline-condition':
                    path=root/'types.h'
                    path.write_text('class Child : public Base { public: virtual void Run(char* out) {\n'
                                    '#if MAYBE\n out=0;\n#endif\n} };\n')
                    classes=E.header_classes(root,set());method=classes['Child'].methods[0]
                    w['definition'].update(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                           bodySha256=hashlib.sha256(method.body.encode()).hexdigest())
                else:
                    w['constructions']=[w['constructions'][0],copy.deepcopy(w['constructions'][0])]
                    w['constructions'][1]['table']='0x00600100'
                with self.assertRaises(ValueError):self.invoke(root,classes,prog,d)

    def test_partial_callee_register_write_invalidates_same_object_installation(self):
        root,classes,prog,d,m,pin=self.fixture();w=d['anchors'][0]['interfaceDispatch']
        def replace_body(va,raw):
            for n,v in enumerate(raw):m[va+n]=v
            f=prog.by_va[va];f.hi=f.declared_hi=va+len(raw)-1;f.body_bytes=len(raw)
            prog.model.insns=[i for f in prog.funcs for i in E.decode_entry_body(prog.img,f)]
            prog.insn_vas=[i.va for i in prog.model.insns]
        old=prog.img.read(0x402000,prog.by_va[0x402000].body_bytes)
        replace_body(0x402000,old[:-1]+b'\x66\x31\xff\xc3')  # XOR DI,DI
        w['baseConstruction']=pin(0x402000)
        raw=(b'\x8b\xcf\xe8'+struct.pack('<i',0x402000-(0x402100+7))
             +b'\xc7\x07'+struct.pack('<I',0x600100)+b'\xc3')
        replace_body(0x402100,raw)
        w['constructions'][0].update(body=pin(0x402100),receiver='edi')
        with self.assertRaises(ValueError):self.invoke(root,classes,prog,d)

    def test_stack_and_segment_writes_are_not_simple_base_initializers(self):
        for mutation in (b'\x66\x31\xe4', b'\x31\xe4', b'\x8e\xd8'):
            with self.subTest(mutation=mutation.hex()):
                root,classes,prog,d,m,pin=self.fixture()
                fn=prog.by_va[0x402000];raw=prog.img.read(fn.va,fn.body_bytes)[:-1]+mutation+b'\xc3'
                for n,v in enumerate(raw):m[fn.va+n]=v
                fn.hi=fn.declared_hi=fn.va+len(raw)-1;fn.body_bytes=len(raw)
                prog.model.insns=[i for f in prog.funcs for i in E.decode_entry_body(prog.img,f)]
                prog.insn_vas=[i.va for i in prog.model.insns]
                d['anchors'][0]['interfaceDispatch']['baseConstruction']=pin(fn.va)
                with self.assertRaisesRegex(ValueError,'simple leaf'):self.invoke(root,classes,prog,d)

    def test_collapsed_hierarchy_cannot_hide_the_tables_actual_extra_base(self):
        root,classes,prog,d,_,_=self.fixture()
        # The cached/aggregated view remains [Peer, Base]; the table's own COL
        # selects the other valid hierarchy. Both must be checked independently.
        chd=prog.test_raw_rtti.hierarchies[0x621080]
        chd.rows.append(SimpleNamespace(descriptor=SimpleNamespace(
            class_name='Extra',mdisp=0,pdisp=-1,vdisp=0),parent_index=0))
        with self.assertRaises(ValueError):self.invoke(root,classes,prog,d)

    def test_per_table_parent_and_virtual_displacement_are_required(self):
        for field,value in (('parent_index',None),('pdisp',4),('vdisp',4)):
            with self.subTest(field=field):
                root,classes,prog,d,_,_=self.fixture()
                row=prog.test_raw_rtti.hierarchies[0x621080].rows[1]
                setattr(row if field=='parent_index' else row.descriptor,field,value)
                with self.assertRaisesRegex(ValueError,'table-specific'):self.invoke(root,classes,prog,d)

    def test_raw_descendant_cannot_be_hidden_from_family_discovery(self):
        root,classes,prog,d,m,_=self.fixture()
        table=E.Vtable(0x600300,'Hidden',0,[0x401300,0x401200,0x401010])
        prog.model.rtti.vtables.append(table)
        for field in ('class_bases','fixed_bases'):
            getattr(prog.model.rtti,field)['Hidden']=[('Hidden',0),('Other',0)]
        c=prog.test_raw_rtti;c.vtables[table.va]=SimpleNamespace(col_va=0x620060)
        c.cols[0x620060]=SimpleNamespace(hierarchy_va=0x6210c0,offset=0,cd_offset=0)
        c.hierarchies[0x6210c0]=SimpleNamespace(rows=[SimpleNamespace(
            descriptor=SimpleNamespace(class_name=name,mdisp=0,pdisp=-1,vdisp=0),
            parent_index=None if n==0 else 0) for n,name in enumerate(('Hidden','Base'))])
        with self.assertRaises(ValueError):self.invoke(root,classes,prog,d)


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



class OrderedInterfaceArgumentsTests(unittest.TestCase):
    def fixture(self, code=None, expected=None):
        root, _, _, document = CommonInterfaceTests.fixture(self)
        (root/'types.h').write_text('class Child : public Base { public: '
                                   'virtual void Run(float transition, MissingEnum dest); };\n')
        source = root/'Caller.cpp'
        source.write_text('void Host::Tick()\n{\n pages[index]->Run(1.f, target);\n}\n')
        classes = E.header_classes(root, set())
        method = classes['Child'].methods[0]
        code = code or bytes.fromhex('8b0f 6afe 680000803f 8b11 ff12 c3')
        raw = {0x401000:b'\xc2\x08\x00',0x401100:b'\xc2\x08\x00',
               0x401200:b'\xc2\x08\x00',0x402000:code}
        memory = {a+i:v for a,b in raw.items() for i,v in enumerate(b)}
        read = lambda a,n:bytes(memory.get(a+i,0) for i in range(n))
        tables = [SimpleNamespace(va=0x600000,klass='Base',offset=0,slots=[0x401000]),
                  SimpleNamespace(va=0x600100,klass='Child',offset=0,slots=[0x401100]),
                  SimpleNamespace(va=0x600200,klass='Sibling',offset=0,slots=[0x401200])]
        for table in tables:
            memory.update({table.va+i:b for i,b in enumerate(struct.pack('<I',table.slots[0]))})
        sec = E.Section('.text',0x401000,0x2000,read(0x401000,0x2000),0x20000000)
        img = SimpleNamespace(sha256='f'*64,read=read,u32=lambda a:struct.unpack('<I',read(a,4))[0],
                              section_of=lambda a:sec if sec.contains(a) else None,sections=[sec])
        funcs = [SimpleNamespace(va=a,lo=a,hi=a+len(b)-1,declared_hi=a+len(b)-1,
                                  body_bytes=len(b),body_ranges=1) for a,b in raw.items()]
        insns = [ins for fn in funcs for ins in E.decode_entry_body(img,fn)]
        bases = {'Base':[('Base',0)],'Child':[('Child',0),('Base',0)],
                 'Sibling':[('Sibling',0),('Base',0)]}
        model = SimpleNamespace(rtti=SimpleNamespace(vtables=tables,class_bases=bases,fixed_bases=bases),
                                insns=insns,refs_to={})
        prog = E.Program(img,model,funcs)
        pin=lambda a,n:dict(address=hex(a),bytes=n,sha256=hashlib.sha256(read(a,n)).hexdigest())
        a=document['anchors'][0]
        a.update(parameters=['float','MissingEnum'],sourceLine=method.line,body=pin(0x401100,3))
        w=a['interfaceDispatch']
        call=next(ins for ins in insns if ins.va>=0x402000 and ins.mnem=='call')
        w.update(caller=pin(0x402000,len(code)),window=pin(0x402000,call.va+call.size-0x402000),
                 callAddress=hex(call.va),parameterStackBytes=[4,4],receiverSpans=[pin(0x402000,2)],
                 source=dict(file='Caller.cpp',sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                             function='Host::Tick',line=3,call='pages[index]->Run(1.f, target);'))
        expected=expected or [(0x402004,'constant32:0x3f800000'),(0x402002,'constant32:0xfffffffe')]
        w['orderedArguments']={'headerSha256':hashlib.sha256((root/'types.h').read_bytes()).hexdigest(),
            'parameters':[dict(pushAddress=hex(site),value=value,stackOffset=4+4*n,
                               sourceType=['float','MissingEnum'][n],sourceArgument=['1.f','target'][n])
                          for n,(site,value) in enumerate(expected)],'externalBindings':[]}
        return root,classes,prog,document,pin

    def evaluate(self, fixture):
        root,classes,prog,document,_=fixture
        propagated=E.propagate_vtable_anchors(prog,classes,document,root)
        return E.vtable_abi_admission(prog,classes,document,propagated,root)

    def test_ordered_transport_keeps_return_and_source_typedef_limits(self):
        result=self.evaluate(self.fixture())
        self.assertEqual([r['status'] for r in result['rows']],['mechanical-checks-pass']*3)
        for row in result['rows']:
            p=row['argumentStorage']['parameters']
            self.assertEqual([(x['stackOffset'],x['sourceType']) for x in p],[(4,'float'),(8,'MissingEnum')])
            self.assertEqual(row['argumentStorage']['returnTypeAndStorage'],'excluded; preserve independently')
            self.assertIn('typedef',p[1]['typeLimit'])

    def test_same_cleanup_but_swapped_values_is_refused(self):
        fixture=self.fixture(bytes.fromhex('8b0f 680000803f 6afe 8b11 ff12 c3'))
        with self.assertRaisesRegex(ValueError,'value or push site'):self.evaluate(fixture)

    def test_push_captures_value_before_register_is_overwritten(self):
        fixture=self.fixture(bytes.fromhex('8b0f b80000803f 6afe 50 b800000000 8b11 ff12 c3'),
                             [(0x402009,'constant32:0x3f800000'),(0x402007,'constant32:0xfffffffe')])
        proof=self.evaluate(fixture)['orderedArgumentWitnesses'][0]
        self.assertEqual(proof['registerValuesAtCall']['eax'],'constant32:0x00000000')
        self.assertEqual(proof['parameters'][0]['value'],'constant32:0x3f800000')

    def test_stack_sources_use_pre_push_esp_and_require_external_binding(self):
        fixture=self.fixture(bytes.fromhex('8b0f ff742408 ff742408 8b11 ff12 c3'),
                             [(0x402006,'load32(window.esp+4)'),(0x402002,'load32(window.esp+8)')])
        root,classes,prog,doc,pin=fixture
        with self.assertRaisesRegex(ValueError,'external bindings'):self.evaluate(fixture)
        ordered=doc['anchors'][0]['interfaceDispatch']['orderedArguments']
        ordered['externalBindings']=[dict(register='esp',meaning='caller stack at the selected entry',
                                           evidence='Synthetic source/stack correspondence',spans=[pin(0x402000,2)])]
        self.assertEqual(self.evaluate(fixture)['rows'][0]['argumentStorage']['status'],
                         'reviewed-local-transport-pass')
        ordered['externalBindings'][0]['spans'][0]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'external span hash'):self.evaluate(fixture)

    def test_declaration_order_signed_immediate_and_exact_storage_are_checked(self):
        for change in ('float-order','source-expression','offset','unsigned-imm8','header-hash','extra-register'):
            with self.subTest(change=change):
                fixture=self.fixture();root,classes,prog,doc,pin=fixture
                ordered=doc['anchors'][0]['interfaceDispatch']['orderedArguments']
                if change=='float-order':ordered['parameters'][0]['sourceType']='MissingEnum'
                if change=='source-expression':ordered['parameters'][0]['sourceArgument']='target'
                if change=='offset':ordered['parameters'][0]['stackOffset']=8
                if change=='unsigned-imm8':ordered['parameters'][1]['value']='constant32:0x000000fe'
                if change=='header-hash':ordered['headerSha256']='0'*64
                if change=='extra-register':ordered['externalBindings']=[dict(register='edx')]
                with self.assertRaises(ValueError):self.evaluate(fixture)

    def test_interior_entry_refused_shared_call_is_explicitly_local(self):
        fixture=self.fixture();root,classes,prog,doc,_=fixture
        prog.model.refs_to={0x402004:[('jmp',0x403000)]}
        with self.assertRaisesRegex(ValueError,'interior entry'):self.evaluate(fixture)
        call=int(doc['anchors'][0]['interfaceDispatch']['callAddress'],16)
        prog.model.refs_to={call:[('jmp',0x403000)]}
        proof=self.evaluate(fixture)['orderedArgumentWitnesses'][0]
        self.assertEqual(proof['otherEntriesAtCall'],['0x00403000'])
        self.assertIn('local path only',proof['scope'])

    def test_fresh_dispatch_cannot_borrow_a_stale_cached_receiver_or_slot(self):
        for offset,replacement in ((12,0x10),(1,0x07),(10,0x10)):
            with self.subTest(offset=offset):
                fixture=self.fixture();root,classes,prog,doc,_=fixture
                original=prog.img.read
                def read(address,count):
                    data=bytearray(original(address,count))
                    if address <= 0x402000+offset < address+count:
                        data[0x402000+offset-address]=replacement
                    return bytes(data)
                prog.img.read=read
                w=doc['anchors'][0]['interfaceDispatch']
                for span in (w['caller'],w['window'],*w['receiverSpans']):
                    span['sha256']=hashlib.sha256(read(int(span['address'],16),span['bytes'])).hexdigest()
                with self.assertRaisesRegex(ValueError,'fresh decode'):
                    self.evaluate(fixture)

    def test_source_assignment_is_not_misread_as_a_default_parameter(self):
        fixture=self.fixture();root,classes,prog,doc,_=fixture
        w=doc['anchors'][0]['interfaceDispatch']
        source=root/'Caller.cpp'
        source.write_text('void Host::Tick()\n{\n pages[index]->Run(transition = 2.f, target);\n}\n')
        w['source'].update(sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                           call='pages[index]->Run(transition = 2.f, target);')
        w['orderedArguments']['parameters'][0]['sourceArgument']='transition'
        with self.assertRaisesRegex(ValueError,'source assignments'):self.evaluate(fixture)

    def test_pushed_memory_cannot_be_reintroduced_as_an_external_stack_value(self):
        fixture=self.fixture(bytes.fromhex('8b0f 6afe ff3424 8b11 ff12 c3'),
                             [(0x402004,'load32(window.esp-4)'),(0x402002,'constant32:0xfffffffe')])
        with self.assertRaisesRegex(ValueError,'overwritten by an outgoing push'):self.evaluate(fixture)

    def test_every_folded_holder_needs_the_same_ordered_witness(self):
        fixture=self.fixture();root,classes,prog,doc,_=fixture
        header=root/'types.h'
        header.write_text(header.read_text()+'class Sibling : public Base { public: '
                          'virtual void Run(float transition, MissingEnum dest); };\n')
        classes=E.header_classes(root,set())
        a=doc['anchors'][0]
        a['interfaceDispatch']['orderedArguments']['headerSha256']=hashlib.sha256(header.read_bytes()).hexdigest()
        second=copy.deepcopy(a)
        second.update(table='0x00600200',target='0x00401200',sourceLine=classes['Sibling'].methods[0].line)
        second['class']='Sibling';second['body']['address']='0x00401200'
        doc['anchors'].append(second)
        fixture=(root,classes,prog,doc,fixture[4])
        self.assertTrue(all(r['argumentStorage'] for r in self.evaluate(fixture)['rows']))
        del second['interfaceDispatch']['orderedArguments']
        result=self.evaluate(fixture)
        self.assertTrue(all(r['status']=='withheld' and r['argumentStorage'] is None for r in result['rows']))
        self.assertTrue(all('ordered argument layouts conflict or leave a holder uncovered' in r['flags']
                            for r in result['rows']))

    def test_prior_cleanup_and_partial_outgoing_stack_overlap_are_refused(self):
        for code,expected in (
            ('8b0f 83c408 6afe ff3424 8b11 ff12 c3',
             [(0x402007,'load32(window.esp+4)'),(0x402005,'constant32:0xfffffffe')]),
            ('8b0f 6afe ff742402 8b11 ff12 c3',
             [(0x402004,'load32(window.esp-2)'),(0x402002,'constant32:0xfffffffe')])):
            with self.subTest(code=code):
                with self.assertRaises(ValueError):self.evaluate(self.fixture(bytes.fromhex(code),expected))

    def test_narrow_push_partial_write_and_post_push_cleanup_refused(self):
        for code in ('8b0f 666afe 680000803f 8b11 ff12 c3',
                     '8b0f 6afe 680000803f 6689c0 8b11 ff12 c3',
                     '8b0f 6afe 680000803f 83c404 8b11 ff12 c3'):
            with self.subTest(code=code):
                with self.assertRaises(ValueError):self.evaluate(self.fixture(bytes.fromhex(code)))


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

    def test_source_constructor_parameters_exclude_initializer_lists(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'bag.cpp').write_text(
                'Bag::Bag() : first(NULL), last(NULL), size(0) { }\n'
                'Bag::Bag(const Bag& other)\n'
                ' : first(NULL), last(Make(1, Pair(2, 3))), size(0)\n'
                '{ Append(other); }\n')
            funcs = E.index_source(Path(tmp))
        self.assertEqual([f.key for f in funcs], ['Bag::Bag', 'Bag::Bag'])
        self.assertEqual([f.args for f in funcs], ['', 'const Bag& other'])
        self.assertEqual((funcs[1].line, funcs[1].end_line), (2, 4))
        self.assertEqual(funcs[1].body.strip(), 'Append(other);')
        self.assertIn('Make(1, Pair(2, 3))', funcs[1].initializers)
        self.assertNotIn('Append', funcs[1].initializers)

    def test_source_nested_parameters_and_assignment_operator(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'bag.cpp').write_text(
                'void Bag::Set(void (*hook)(int), int count = Make(1, 2)) { hook(count); }\n'
                'Bag& Bag::operator = (Bag& other) { Copy(other); return *this; }\n'
                'bool Bag::operator == (const Bag& other) { return true; }\n')
            funcs = E.index_source(Path(tmp))
        self.assertEqual([f.key for f in funcs], ['Bag::Set', 'Bag::operator='])
        self.assertEqual(funcs[0].args, 'void (*hook)(int), int count = Make(1, 2)')
        self.assertEqual((funcs[1].head, funcs[1].args), ('Bag&', 'Bag& other'))
        self.assertEqual(E.source_key_to_name('Bag::operator='), 'Bag__operator_assign')

    def test_source_body_braces_in_literals_do_not_truncate_or_capture_next_definition(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'bag.cpp').write_text(
                'void Bag::One() {\n'
                ' Log("}"); char brace = \'{\';\n'
                ' if (brace) { Finish(); }\n'
                '}\n'
                'void Bag::Two() { End(); }\n')
            funcs = E.index_source(Path(tmp))
        self.assertEqual([f.key for f in funcs], ['Bag::One', 'Bag::Two'])
        self.assertEqual((funcs[0].line, funcs[0].end_line), (1, 4))
        self.assertIn('Finish();', funcs[0].body)
        self.assertNotIn('Bag::Two', funcs[0].body)
        self.assertEqual(funcs[0].literals, ['}'])

    def test_source_incomplete_bodies_and_unsupported_suffixes_are_withheld(self):
        for text in ('void Bag::Bad() { Log("}");',
                     '/* no close\nvoid Bag::Bad(int n) { return; }\n',
                     'void Bag::Bad(int x { Work(); }',
                     'Bag::Bag() : value(Make(1) { Work(); }',
                     'void Bag::Bad() { Log("unterminated); }',
                     'void Bag::Bad() { Log("unescaped\nnewline"); }',
                     "void Bag::Bad() { char x = '{; }",
                     'void Bag::Bad() noexcept { Work(); }',
                     'void Bag::Bad() : field(1) { Work(); }'):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as tmp:
                Path(tmp, 'bag.cpp').write_text(text)
                self.assertEqual(E.index_source(Path(tmp)), [])

    def test_pinned_multiline_asm_dialect_keeps_following_definitions(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'bag.cpp').write_text(
                'void Bag::One() { asm __volatile__ (\n"\n asm } body {\\n\n"\n: "=j" (out)); }\n'
                'void Bag::Two() { Finish(); }\n')
            funcs = E.index_source(Path(tmp))
        self.assertEqual([f.key for f in funcs], ['Bag::One', 'Bag::Two'])
        self.assertIn('"=j"', funcs[0].body)
        self.assertNotIn('Bag::Two', funcs[0].body)

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


class BoundedSwitchTests(unittest.TestCase):
    def fixture(self, remap=False, gap=b'', different_pop=False):
        start, table, selector = 0x401100, 0x402000, 0x403000
        code = bytearray(b'\x90'*5+b'\x83\xf8'+bytes([3 if remap else 2])+gap)
        compare = start+5
        guard = start+len(code); code.extend(b'\x77\x00')
        if remap:
            code.extend(b'\x31\xd2\x8a\x90'+struct.pack('<I', selector))
        jump = start+len(code)
        code.extend((b'\xff\x24\x95' if remap else b'\xff\x24\x85')+struct.pack('<I', table))
        default = start+len(code); code[guard-start+1] = default-guard-2
        code.extend(b'\xc3\xc3'+(b'\xc2\x04\x00' if different_pop else b'\xc3'))
        memory = {}
        def write(address, data):memory.update({address+i:b for i,b in enumerate(data)})
        write(start, code); write(table, struct.pack('<III',default,default+1,default+2))
        write(selector, bytes([2,0,2,1]))
        sections = [E.Section('.text',start,len(code),bytes(code),0x60000020),
                    E.Section('.rdata',table,12,bytes(12),0x40000040),
                    E.Section('.rdata',selector,4,bytes(4),0x40000040)]
        def read(a,n):
            raw=bytearray()
            for i in range(n):
                if a+i not in memory:break
                raw.append(memory[a+i])
            return bytes(raw)
        img=SimpleNamespace(read=read,sections=sections,
                            section_of=lambda a:next((s for s in sections if s.contains(a)),None))
        fn=E.Func(start,'Untrusted__Name','USER_DEFINED',start,start+len(code)-1,'','',False,'',False,1,len(code),start+len(code)-1)
        model=SimpleNamespace(refs_to={},data_ptrs_to={},rtti=SimpleNamespace(vtables=[]))
        prog=SimpleNamespace(img=img,model=model,funcs=[fn],by_va={start:fn})
        prog.body=lambda f:E.decode_entry_body(img,f)
        return prog,fn,memory,sections,dict(compare=compare,guard=guard,jump=jump,default=default,table=table,selector=selector)

    def prove(self, prog, fn):return E.bounded_switch_targets(prog,fn,prog.body(fn))

    def test_direct_and_remapped_tables_pin_exact_selector_footprints(self):
        for remap in (False,True):
            with self.subTest(remap=remap):
                prog,fn,_,_,p=self.fixture(remap)
                report=self.prove(prog,fn);self.assertFalse(report['refusals'])
                row=report['tables'][0]
                wanted=[p['default']+i for i in ([2,0,2,1] if remap else range(3))]
                self.assertEqual([int(t,16) for t in row['targets']],wanted)
                self.assertEqual(row['table']['bytes'],12)
                self.assertEqual(row['table']['sha256'],hashlib.sha256(prog.img.read(p['table'],12)).hexdigest())
                if remap:self.assertEqual(row['remap']['bytes'],4)
                else:self.assertIsNone(row['remap'])

    def test_only_flag_and_selector_preserving_guard_gaps_are_admitted(self):
        cases=[(b'\x8b\xf1',True),(b'\x57\x8b\xf1',True),
               (b'\x89\x4c\x24\x04',True),(b'\x89\x0d\x00\x00\x70\x00',True),
               (b'\x40',False),(b'\xf8',False),(b'\xb0\x00',False),
               (b'\x8b\xc1',False),(b'\x31\xc0',False)]
        for gap,admit in cases:
            with self.subTest(gap=gap.hex()):
                prog,fn,*_=self.fixture(gap=gap)
                self.assertEqual(bool(self.prove(prog,fn)['tables']),admit)

    def test_signed_or_inverted_guard_and_missing_high_byte_clear_are_refused(self):
        for patch_kind in ('signed','inverted','clear','selector-clobber'):
            with self.subTest(patch=patch_kind):
                prog,fn,m,_,p=self.fixture(remap=True)
                if patch_kind=='signed':m[p['guard']]=0x7f
                elif patch_kind=='inverted':m[p['guard']]=0x76
                elif patch_kind=='clear':m[p['guard']+2]=m[p['guard']+3]=0x90
                else:m[p['guard']+3]=0xc0  # XOR EAX,EAX instead of EDX
                self.assertFalse(self.prove(prog,fn)['tables'])

    def test_known_entries_cannot_bypass_comparison_or_zero_extension(self):
        for kind in ('local-branch','local-call','outside-call','immediate','data-pointer','table',
                     'compare-interior-reference','compare-interior-pointer','address-forming-lea'):
            with self.subTest(kind=kind):
                prog,fn,m,_,p=self.fixture(remap=True)
                dest=p['jump']
                if kind=='local-branch':m[fn.va]=0xeb;m[fn.va+1]=dest-fn.va-2
                elif kind=='local-call':
                    m[fn.va]=0xe8
                    m.update({fn.va+1+i:b for i,b in enumerate(struct.pack('<i',dest-fn.va-5))})
                elif kind=='outside-call':prog.model.refs_to[dest]=[('call',0x405000)]
                elif kind=='immediate':prog.model.refs_to[dest]=[('imm',0x405000)]
                elif kind=='data-pointer':prog.model.data_ptrs_to[dest]=[0x406000]
                elif kind=='compare-interior-reference':prog.model.refs_to[p['compare']+1]=[('jmp',0x405000)]
                elif kind=='compare-interior-pointer':prog.model.data_ptrs_to[p['compare']+1]=[0x406000]
                elif kind=='address-forming-lea':prog.model.refs_to[dest]=[('mem',0x405000)]
                else:m.update({p['table']+i:b for i,b in enumerate(struct.pack('<I',dest))})
                report=self.prove(prog,fn)
                self.assertFalse(report['tables'])
                self.assertTrue(any('bypasses' in r['reason'] for r in report['refusals']))

    def test_table_extent_and_instruction_ownership_refusals(self):
        for kind in ('short-table','short-remap','writable','overlap','exterior','mid-instruction','remap-overrun'):
            with self.subTest(kind=kind):
                prog,fn,m,sections,p=self.fixture(remap=True)
                if kind=='short-table':del m[p['table']+11]
                elif kind=='short-remap':del m[p['selector']+3]
                elif kind=='writable':sections[1].characteristics |= 0x80000000
                elif kind=='overlap':prog.funcs.append(SimpleNamespace(lo=p['table'],hi=p['table']+1))
                elif kind=='remap-overrun':m[p['selector']]=255
                else:
                    dest=0x407000 if kind=='exterior' else p['compare']+1
                    m.update({p['table']+i:b for i,b in enumerate(struct.pack('<I',dest))})
                self.assertFalse(self.prove(prog,fn)['tables'])

    def test_fresh_bytes_override_a_plausible_cached_guard(self):
        prog,fn,m,_,p=self.fixture();body=prog.body(fn)
        m[p['guard']]=0x7f
        with self.assertRaisesRegex(ValueError,'fresh entry decoding'):
            E.bounded_switch_targets(prog,fn,body)

    def test_cross_function_table_in_text_is_not_hidden_by_cached_pointer_census(self):
        for offset in (0,1,2,3):
            with self.subTest(offset=offset):
                prog,fn,_,sections,p=self.fixture()
                # Last DWORD, possibly unaligned, lies outside the function.
                # The model deliberately has no pointer/reference entry.
                sections[0].raw+=b'\x90'*offset+struct.pack('<I',p['jump'])
                sections[0].size=len(sections[0].raw)
                report=self.prove(prog,fn)
                self.assertFalse(report['tables'])
                self.assertTrue(any('bypasses' in r['reason'] for r in report['refusals']))

    def test_second_switch_table_cannot_bypass_first_switch_guard(self):
        prog,fn,m,sections,p=self.fixture()
        raw=prog.img.read(fn.va,fn.body_bytes)
        table2=0x404000
        extra=b'\x83\xf9\x00\x77\x07\xff\x24\x8d'+struct.pack('<I',table2)+b'\xc3'
        raw+=extra
        m.update({fn.va+i:b for i,b in enumerate(raw)})
        m.update({table2+i:b for i,b in enumerate(struct.pack('<I',p['jump']))})
        fn.hi=fn.declared_hi=fn.va+len(raw)-1;fn.body_bytes=len(raw)
        sections[0].raw=raw;sections[0].size=len(raw)
        sections.append(E.Section('.rdata',table2,4,bytes(4),0x40000040))
        report=self.prove(prog,fn)
        self.assertTrue(any(r.get('jump')==f"0x{p['jump']:08x}" and 'bypasses' in r['reason']
                            for r in report['refusals']))

    def test_different_pop_reachable_via_table_stays_withheld(self):
        for wrong in (False,True):
            with self.subTest(wrong=wrong):
                prog,fn,*_=self.fixture(different_pop=wrong)
                method=E.HeaderMethod('Base','Run',(),'',True,'types.h',1,'void',None)
                classes={'Base':E.HeaderClass('Base',[],[method],[],'types.h',1)}
                doc={'anchors':[dict(table='0x600000',slot=0,method='Run',parameters=[],**{'class':'Base'})]}
                row=dict(target=hex(fn.va),status='anchored-method-candidate',uses=[dict(
                    anchorTable='0x600000',anchorSlot=0,method='Run',parameters=[],qualifiers='',**{'class':'Base'})])
                report=E.vtable_abi_admission(prog,classes,doc,{'rows':[row]})
                self.assertEqual(report['rows'][0]['status'],'withheld' if wrong else 'mechanical-checks-pass')
                self.assertEqual(report['rows'][0]['observedReturnPop'],[0,4] if wrong else [0])
                self.assertEqual(len(report['switchProofs'][0]['tables']),1)


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


class CleanupBodyTests(unittest.TestCase):
    """Real decoded authored x86, with a synthetic separately tested RTTI census."""

    def fixture(self, prefix=None, ending=None):
        prefix = bytes.fromhex('c701 00016000') if prefix is None else prefix
        call = b'\xe8'+struct.pack('<i', 0x403000-(0x402000+len(prefix)+5))
        cleanup = prefix + (call+b'\xc3' if ending is None else ending)
        raw = {0x401000: CompilerDestructorTests.wrapper(0x401000,0x403000),
               0x401100: CompilerDestructorTests.wrapper(0x401100,0x402000),
               0x402000: cleanup, 0x403000:b'\xc3', 0x405000:bytes.fromhex('c20400')}
        text = bytearray(b'\xcc'*0x6000)
        for a, data in raw.items(): text[a-0x401000:a-0x401000+len(data)] = data
        sections = [E.Section('.text',0x401000,len(text),bytes(text),0x60000020),
                    E.Section('.rdata',0x600000,0x2000,bytes(0x2000),0x40000040)]
        img = object.__new__(E.Image)
        img.sections = sections; img.sha256 = 'a'*64
        def put(address, data):
            sec=img.section_of(address); start=address-sec.start
            sec.raw=sec.raw[:start]+data+sec.raw[start+len(data):]
        for a, value in {0x600000-4:0,0x600004:0x401000,0x6000fc:0x601000,
                         0x600104:0x401100,0x601000:0,0x601004:0,0x601008:0}.items():
            if a>=0x600000:put(a,struct.pack('<I',value))
        names={0x401000:'Base__scalar_deleting_dtor',0x401100:'Child__scalar_deleting_dtor',
               0x402000:'UntrustedCleanup',0x403000:'UntrustedBase',0x405000:'UntrustedFree'}
        funcs=[E.Func(a,names[a],'USER_DEFINED',a,a+len(data)-1,'','',False,'',False,
                      1,len(data),a+len(data)-1) for a,data in raw.items()]
        bases={'Base':[('Base',0)],'Child':[('Child',0),('Base',0)]}
        rtti=E.RttiModel({},bases,[E.Vtable(0x600000,'Base',0,[0,0x401000]),
                                  E.Vtable(0x600100,'Child',0,[0,0x401100])],copy.deepcopy(bases))
        model=SimpleNamespace(rtti=rtti,insns=[i for f in funcs for i in E.decode_entry_body(img,f)])
        prog=E.Program(img,model,funcs)
        pin=lambda a:dict(address=hex(a),bytes=len(raw[a]),sha256=hashlib.sha256(raw[a]).hexdigest())
        doc={'specimenSha256':img.sha256,'evidence':'Authored test seed',
             'seed':{'class':'Base','table':'0x600000','slot':1,'target':'0x401000','body':pin(0x401000)},
             'teardown':pin(0x403000),'deallocator':pin(0x405000),'manager':'0x680000'}
        return prog,doc,put

    def report(self, p, d):
        with patch.object(E,'scan_rtti',return_value=p.model.rtti):
            return E.compiler_cleanup_bodies(p,d)

    def test_zero_displacement_first_store_cannot_be_skipped(self):
        for first in (bytes.fromhex('c74100 00006000'), bytes.fromhex('894100'),
                      bytes.fromhex('3ec701 00006000'), bytes.fromhex('31c0 c70401 00006000'),
                      bytes.fromhex('c741ff 00006000'), bytes.fromhex('c64101 00')):
            with self.subTest(first=first.hex()):
                p,d,_=self.fixture(first+bytes.fromhex('c701 00016000'))
                self.assertEqual(self.report(p,d)['rows'][0]['status'],'withheld')

    def test_clipped_other_owner_cannot_hide_overlap(self):
        for target in (0x402000,0x403000,0x401100):
            with self.subTest(target=hex(target)):
                p,d,_=self.fixture()
                p.funcs.append(E.Func(target-4,'Overlap','DEFAULT',target-4,target-1,
                                     '','',False,'',False,1,12,target+7))
                self.assertEqual(self.report(p,d)['rows'][0]['status'],'withheld')

    def test_names_do_not_feed_admission_and_old_spelling_can_be_kept(self):
        p,d,_=self.fixture(); before=self.report(p,d)
        self.assertEqual(before['proposals']['rows'][0]['proposedName'],'Child__dtor_body')
        for f in p.funcs:f.name='Guess_'+hex(f.va)
        self.assertEqual(before['rows'],self.report(p,d)['rows'])
        p.by_va[0x402000].name='Child__dtor_base'
        self.assertEqual(self.report(p,d)['proposals']['rows'][0]['status'],'keep')

    def test_wrong_ancestor_member_adjusted_or_late_store_is_withheld(self):
        prefixes=[bytes.fromhex(v) for v in (
            'c701 00006000', 'c74104 00016000', '83c104 c701 00016000',
            'b101 c701 00016000', '8b09 c701 00016000',
            'eb00 c701 00016000', 'e800000000 c701 00016000',
            'c701 04016000', 'c701 00006000 c701 00016000')]
        for prefix in prefixes:
            with self.subTest(prefix=prefix.hex()):
                p,d,_=self.fixture(prefix)
                report=self.report(p,d)
                self.assertFalse(any(r['status']=='mechanical-checks-pass' for r in report['rows']))

    def test_register_copy_and_zero_displacement_owner_store_pass(self):
        for prefix in (bytes.fromhex('8bf1 c70600016000'),bytes.fromhex('c7410000016000'),
                       bytes.fromhex('3ec70100016000'),bytes.fromhex('c7410400000000 c70100016000')):
            with self.subTest(prefix=prefix.hex()):
                p,d,_=self.fixture(prefix)
                self.assertEqual(self.report(p,d)['rows'][0]['status'],'mechanical-checks-pass')

    def test_segment_register_mutations_in_prefix_or_teardown_are_refused(self):
        for prefix in (bytes.fromhex('8ed8 c70100016000'), bytes.fromhex('1f c70100016000'),
                       bytes.fromhex('c70100016000 8ed8')):
            with self.subTest(prefix=prefix.hex()):
                p,d,_=self.fixture(prefix)
                self.assertFalse(any(r['status']=='mechanical-checks-pass' for r in self.report(p,d)['rows']))

    def test_stale_cached_body_cannot_be_used_with_fresh_pins(self):
        for target, data in [(0x402002,struct.pack('<I',0x600000)),
                             (0x402007,struct.pack('<i',0x404000-0x40200b)),
                             (0x403000,b'\x90')]:
            with self.subTest(target=hex(target)):
                p,d,put=self.fixture();put(target,data)
                if target==0x403000:d['teardown']['sha256']=hashlib.sha256(b'\x90').hexdigest()
                self.assertEqual(self.report(p,d)['rows'][0]['status'],'withheld')

    def test_unowned_matching_wrapper_and_virtual_alias_are_withheld(self):
        for kind in ('wrapper','alias'):
            with self.subTest(kind=kind):
                p,d,put=self.fixture()
                if kind=='wrapper':put(0x406000,CompilerDestructorTests.wrapper(0x406000,0x402000))
                else:p.slots[0x402000].append(('Other',0,1,0x610000))
                self.assertEqual(self.report(p,d)['rows'][0]['status'],'withheld')

    def test_constructor_displacement_and_raw_slot_disagreement_are_withheld(self):
        p,d,put=self.fixture();put(0x601008,struct.pack('<I',4))
        self.assertEqual(self.report(p,d)['rows'][0]['status'],'withheld')
        p,d,put=self.fixture();put(0x600104,struct.pack('<I',0x401000))
        with self.assertRaisesRegex(ValueError,'slot word mismatch'):self.report(p,d)

    def test_occupied_spelling_is_not_resolved_by_moving_another_name(self):
        p,d,_=self.fixture();p.by_va[0x405000].name='Child__dtor_body'
        report=self.report(p,d)
        self.assertEqual(report['rows'][0]['status'],'mechanical-checks-pass')
        self.assertEqual(report['proposals']['rows'][0]['status'],'withheld')

    def test_fresh_rtti_disagreement_refuses_before_admission(self):
        p,d,_=self.fixture()
        with patch.object(E,'scan_rtti',return_value=E.RttiModel({}, {}, [])):
            with self.assertRaisesRegex(ValueError,'fresh specimen'):
                E.compiler_cleanup_bodies(p,d)


if __name__ == "__main__":
    unittest.main()
