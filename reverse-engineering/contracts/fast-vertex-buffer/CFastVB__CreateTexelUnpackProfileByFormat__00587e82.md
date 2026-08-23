# CFastVB__CreateTexelUnpackProfileByFormat

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__CreateTexelUnpackProfileByFormat` at `0x00587e82` in the top-level texel-unpack profile factory whose selected path dispatches directly to 23 numeric-format constructor plates; exact identity, selected call connectivity, ABI audit, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register/closure identity, retained read-only READY packet/decompile, structured edges, fresh pristine body copy and digest recomputation, and paired static review; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00587e82`

## Identity
- Body `[0x00587e82,0x005885d5]`, 1876 bytes, 542 closure instructions. Raw pristine-body SHA-256 `9bc58b22b427c2b669f9e5a09a9bac67bc56805dffb1882a0b04349b55178415`; closure range SHA-256 `926f2f6fd77aa3a5959f1d7a036b34c8919be6df4943d35e3dbe60a226cbf1d9`; packet range-plus-bytes SHA-256 `178cfbfb548bdfab4ba3398682712f1e0c5746a61f79fcb24e2b880e243af6dd`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table, current EVIDENCE-REGISTER, dated closure row, and retained READY packet all name `CFastVB__CreateTexelUnpackProfileByFormat`.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `3c1528f1268fcc16f98ce0478cc0aaf18b5f1cd4fd854b02bff8005a950a585a` and decompile SHA-256 `255d10462aec87220dfca85be8457973e217fc00d0fbea1efa19e9f4aada5bd0` bind the retained review input without citing a writer-local path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.
- Current closure/packet body is `[0x00587e82,0x005885d5]`. Paired W013 reviews locate the terminal `RET 0x4` at `0x005885d3` and an unlabeled neighbor span beginning at `0x005885d4`; the two trailing closure bytes are not treated as additional factory behavior, and the missing-neighbor question remains explicit.

## Calling convention
Packet records `__stdcall` for `void * __stdcall CFastVB__CreateTexelUnpackProfileByFormat(void * format_descriptor)`. Current field accepted. Packet field matches paired W013 review: no ECX receiver at entry and RET 0x4 cleans the sole format_descriptor argument. RET cleanup witness: `RET 0x4`.

## Prototype and parameter semantics
```c
void * __stdcall CFastVB__CreateTexelUnpackProfileByFormat(void * format_descriptor)
```
- Packet field and paired static review agree on this bounded ABI plate. Parameter labels remain analyst intent; concrete descriptor/profile layouts, ownership, valid ranges, and enum meaning remain not_determinable.

## Return value meaning
The accepted packet signature declares `void *`. Packet comment and paired W013 review bound allocation/constructor dispatch and a null allocation path, but exact ownership, concrete profile subtype, setup-callback contract, and null/error meaning remain not_determinable.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`PTR_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `OID_T3_00426fd0` `0x00426fd0` x50 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005e9f3c__ctor` `0x0058577f` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005e9f4c__ctor` `0x0058584f` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005e9f5c` `0x00585908` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005e9f6c` `0x00585924` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005e9f7c` `0x005859bc` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005e9f8c__ctor` `0x00585a5f` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005e9f9c__ctor` `0x00585b19` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005e9fac` `0x00585bef` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005e9fbc` `0x00585c94` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005e9fd0__ctor` `0x00585d6b` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005e9fe0__ctor` `0x00585d87` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005e9ff0__ctor` `0x00585e83` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea000__ctor` `0x00585f6b` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea010__ctor` `0x00585f87` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea020__ctor` `0x0058609e` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005ea034` `0x0058617c` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea044__ctor` `0x00586198` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea058__ctor` `0x005862cd` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005ea068` `0x005862e9` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea078__ctor` `0x0058641c` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea088__ctor` `0x00586519` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea098__ctor` `0x00586535` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea0a8__ctor` `0x00586551` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea0b8__ctor` `0x005865ed` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005ea0c8` `0x0058669a` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005ea0d8` `0x005866b6` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005ea0e8` `0x0058675f` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea0f8__ctor` `0x005867d2` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea108__ctor` `0x00586978` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005ea118` `0x00586994` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea128__ctor` `0x00586a55` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea148__ctor` `0x00586b63` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea158__ctor` `0x00586b7f` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea168__ctor` `0x00586b9b` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005ea198` `0x00586ec7` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea1a8__ctor` `0x00586ee3` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea1b8__ctor` `0x00586eff` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea1c8__ctor` `0x00586f1b` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea1f4__ctor` `0x00587303` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea204__ctor` `0x00587322` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfile_005ea214__ctor` `0x0058733e` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelCodecProfile_005ea224__ctor` `0x00587663` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelCodecProfile_005ea234__ctor` `0x0058767b` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelCodecProfile_005ea244__ctor` `0x00587693` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfileRegistry_005ea254__ctor` `0x00587dd6` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005ea264` `0x00587dee` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitTexelUnpackVTable_005ea274` `0x00587e06` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelUnpackProfileRegistry_005ea284__ctor` `0x00587e1e` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelCodecProfile_005ea294__ctor` `0x00587e36` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TexelCodecProfile_005ea2a4__ctor` `0x00587e4e` x1 site(s) (STATIC_DIRECT).
- Caller `CFastVB__InitDualTexelConversionPipeline` `0x0058070e` x2 site(s) (instruction-flow).
- Selected-cohort adjacency: 0 incoming and 23 outgoing direct edge(s) within the exact 25-row component. Full packet arrays above remain authoritative for external direct edges.
- Structured packet arrays prove listed direct/static edge identities and site counts only. Indirect callbacks, vtable selection beyond displayed stores, data references, library inlining, and runtime reachability remain unresolved unless separately bounded.

## Behavior summary
- Packet-first boundary: the current 1,783-row canonical crosswalk, five accepted source-reducer receipts, and pinned source commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Manifest selection basis: top-level numeric/FourCC-like format-id dispatch; selected adjacency is limited to the 23 numeric constructor plates.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave676 static read-back: factory reads the format descriptor id at +0x4, dispatches numeric and FourCC-like cases, allocates profile objects sized 0x1074/0x10a4/0x10f0, calls the matching profile constructor, and invokes the observed setup callback when present. Static metadata only; exact format enum, descriptor ABI, and runtime texture output remain unproven.”
- The selected cohort covers only the exact 23 numeric constructor edges and their shared base constructor. The displayed factory also contains later signed/FourCC-like/registry/codec targets outside this cohort; they remain uncontracted here. Packet metadata proves dispatch/allocation/call identities only, not a complete format-enum mapping or runtime texture fidelity.
- The non-empty packet decompile is bound by SHA-256 `255d10462aec87220dfca85be8457973e217fc00d0fbea1efa19e9f4aada5bd0`. This contract does not infer unstated format enum names, descriptor ABI, profile layout, channel policy, allocation ownership, callback contract, or runtime causality.
- Structured inventory: 1 caller record(s), 51 callee record(s), and 0 string-ref record(s). Manifest subfamily: `numeric_format_factory`; contract number 325.

## Error / edge behavior
The displayed factory has allocation-failure branches and an optional setup callback, but exception safety, descriptor validity, callback failure propagation, cleanup after partial construction, ownership transfer, and behavior for every unrecognized format id remain not_determinable. Paired W013 review additionally confirms a missing-neighbor question after the terminal RET; this file does not absorb or name that gap.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_3659ffdb`, immutable cohort-13 manifest SHA-256 `0f2e2819a98c54b5bccc2276c8cb20a937f5d189fcf241c6f8f3d293234663d2`, contract 325 of 301–325; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `d8f9f8b4e1f6b0ca5af890729fb108c39ecf1082`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`.
- Retained READY packet corpus: executable `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `3c1528f1268fcc16f98ce0478cc0aaf18b5f1cd4fd854b02bff8005a950a585a`, packet decompile SHA-256 `255d10462aec87220dfca85be8457973e217fc00d0fbea1efa19e9f4aada5bd0`, packet READY SHA-256 `5381d8d632a1844967d7bb4e213b2398f479d95b0ebcac8108bbce1e0243c2d7`, and packet run-manifest SHA-256 `bed42bde09b14374113955605a5c11629b7c64204230f8659ac5cea0fa3a4bb0`; retained for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00587e82:005885d5;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Signature audit disposition `PACKET_ACCEPTED`; packet-field contradiction `false`; no contradiction remains unresolved in the effective prototype.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W013/primary/A04.md`.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W013/adversarial/B04.md`.
- Packet stringRefs array: empty.
- Source-first authorities joined before packets: `reverse-engineering/source-crosswalk/crosswalk.tsv`, `reverse-engineering/source-crosswalk/expansion/w1-save-session-input-frontend/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w2-thing-battleengine-camera/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w3-audio-music/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w4-memory-container-archive/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w5-engine-render-platform-shell/RECEIPT.json`.
- Selected source crosswalk/reducer rows: none for this VA; this is an explicit packet-first row, not an assertion that no source analog exists.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, effective ABI audit, structured edge inventory, analyst comment, strings, paired static review, all source-authority joins, and TTD presence/absence are pinned. Descriptor/profile semantics, complete factory behavior, and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global/profile/descriptor record.
- Exact numeric format-id mapping, selected/unselected case boundary, channel/domain policy, vtable/callback contract, allocation ownership, and error cleanup.
- Runtime profile construction, texture conversion fidelity, side-effect ordering, failure behavior, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble the exact raw-body digest and reconstruct every switch/case target and cleanup path through RET 0x4, separately recover the unlabeled post-RET neighbor span, then pass retained real descriptors through a controlled copied runtime and compare selected constructor target, allocation size, callback order, returned pointer, and failure cleanup.
