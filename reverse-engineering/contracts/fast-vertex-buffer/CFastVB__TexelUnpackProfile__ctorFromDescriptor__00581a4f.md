# CFastVB__TexelUnpackProfile__ctorFromDescriptor

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__TexelUnpackProfile__ctorFromDescriptor` at `0x00581a4f` in the shared descriptor-based texel-unpack profile constructor directly called by all 23 selected numeric-format constructor plates; exact identity, selected call connectivity, ABI audit, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register/closure identity, retained read-only READY packet/decompile, structured edges, fresh pristine body copy and digest recomputation, and paired static review; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00581a4f`

## Identity
- Body `[0x00581a4f,0x00581cbf]`, 625 bytes, 193 closure instructions. Raw pristine-body SHA-256 `65084c75d5aa9e3848174e4a9ccd5828017b304afe8a7f7a10cbd2183a3d4ffd`; closure range SHA-256 `30edebb3ba8f6a87b33f32320114977b5e49fde80a6ee0b6cc21b8b85e19503d`; packet range-plus-bytes SHA-256 `3a2f43cfb52247d3dec6e6b6aa3d8f6e178cf172f699345eb83b5f0d296d51df`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table, current EVIDENCE-REGISTER, dated closure row, and retained READY packet all name `CFastVB__TexelUnpackProfile__ctorFromDescriptor`.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `7e2ce24fba986d78b11eb94f4d91beda96d7ce296016f1f18e881bfe43f56f1f` and decompile SHA-256 `b8a4163bd4b418d2a0634f0d9f507ea782460d480d497b26c70372c4d1ecb924` bind the retained review input without citing a writer-local path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.
- Current closure/packet range is used exactly; no padding or neighboring bytes are interpreted as additional semantics by this contract.

## Calling convention
Packet records `unknown` for `int CFastVB__TexelUnpackProfile__ctorFromDescriptor(void)`; that field is rejected as stale. Effective bounded signature: `int __thiscall CFastVB__TexelUnpackProfile__ctorFromDescriptor(void * this, void * descriptor, uint flags_or_key_bits, int format_mode)`. Packet field remains stale int ...(void)/unknown. Paired W012 review plus recovered ECX, three stack slots, and RET 0xc establish the bounded effective plate; packet analyst comment independently states the same correction. RET cleanup witness: `RET 0xc`.

## Prototype and parameter semantics
```c
int __thiscall CFastVB__TexelUnpackProfile__ctorFromDescriptor(void * this, void * descriptor, uint flags_or_key_bits, int format_mode)
```
- This effective plate is a reconciliation, not a Ghidra database mutation. Parameter labels remain provisional; concrete descriptor/profile layouts, ownership, valid ranges, and enum meaning remain not_determinable.

## Return value meaning
The reconciled bounded signature declares `int`. The packet comment and paired W012 review bound constructor-shaped state initialization, but the scalar's success/status/this-pointer meaning is not_determinable from this factory and is not promoted.

## Globals read/written
- Decompile symbol references: `DAT_00657980`, `DAT_00657a00`, `PTR_CFastVB__TexelUnpackProfile_scalar_deleting_dtor_005e9ed0`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee ``vector_constructor_iterator'` `0x00574a99` x1 site(s) (STATIC_DIRECT).
- Caller `CFastVB__TexelUnpackProfile_005e9f3c__ctor` `0x0058577f` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005e9f4c__ctor` `0x0058584f` x1 site(s) (instruction-flow).
- Caller `CFastVB__InitTexelUnpackVTable_005e9f5c` `0x00585908` x1 site(s) (instruction-flow).
- Caller `CFastVB__InitTexelUnpackVTable_005e9f6c` `0x00585924` x1 site(s) (instruction-flow).
- Caller `CFastVB__InitTexelUnpackVTable_005e9f7c` `0x005859bc` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005e9f8c__ctor` `0x00585a5f` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005e9f9c__ctor` `0x00585b19` x1 site(s) (instruction-flow).
- Caller `CFastVB__InitTexelUnpackVTable_005e9fac` `0x00585bef` x1 site(s) (instruction-flow).
- Caller `CFastVB__InitTexelUnpackVTable_005e9fbc` `0x00585c94` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005e9fd0__ctor` `0x00585d6b` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005e9fe0__ctor` `0x00585d87` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005e9ff0__ctor` `0x00585e83` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea000__ctor` `0x00585f6b` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea010__ctor` `0x00585f87` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea020__ctor` `0x0058609e` x1 site(s) (instruction-flow).
- Caller `CFastVB__InitTexelUnpackVTable_005ea034` `0x0058617c` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea044__ctor` `0x00586198` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea058__ctor` `0x005862cd` x1 site(s) (instruction-flow).
- Caller `CFastVB__InitTexelUnpackVTable_005ea068` `0x005862e9` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea078__ctor` `0x0058641c` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea088__ctor` `0x00586519` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea098__ctor` `0x00586535` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea0a8__ctor` `0x00586551` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea0b8__ctor` `0x005865ed` x1 site(s) (instruction-flow).
- Caller `CFastVB__InitTexelUnpackVTable_005ea0c8` `0x0058669a` x1 site(s) (instruction-flow).
- Caller `CFastVB__InitTexelUnpackVTable_005ea0d8` `0x005866b6` x1 site(s) (instruction-flow).
- Caller `CFastVB__InitTexelUnpackVTable_005ea0e8` `0x0058675f` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea0f8__ctor` `0x005867d2` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea108__ctor` `0x00586978` x1 site(s) (instruction-flow).
- Caller `CFastVB__InitTexelUnpackVTable_005ea118` `0x00586994` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea128__ctor` `0x00586a55` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfileRegistry_005ea138__ctor` `0x00586a71` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea148__ctor` `0x00586b63` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea158__ctor` `0x00586b7f` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea168__ctor` `0x00586b9b` x1 site(s) (instruction-flow).
- Caller `CFastVB__InitTexelUnpackVTable_005ea198` `0x00586ec7` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea1a8__ctor` `0x00586ee3` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea1b8__ctor` `0x00586eff` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea1c8__ctor` `0x00586f1b` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea1f4__ctor` `0x00587303` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea204__ctor` `0x00587322` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelUnpackProfile_005ea214__ctor` `0x0058733e` x1 site(s) (instruction-flow).
- Caller `CFastVB__TexelCodecProfile__ctorFromFourCC` `0x00587477` x1 site(s) (instruction-flow).
- Selected-cohort adjacency: 23 incoming and 0 outgoing direct edge(s) within the exact 25-row component. Full packet arrays above remain authoritative for external direct edges.
- Structured packet arrays prove listed direct/static edge identities and site counts only. Indirect callbacks, vtable selection beyond displayed stores, data references, library inlining, and runtime reachability remain unresolved unless separately bounded.

## Behavior summary
- Packet-first boundary: the current 1,783-row canonical crosswalk, five accepted source-reducer receipts, and pinned source commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Manifest selection basis: shared base constructor for every selected numeric-format constructor plate.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Shared texel-unpack profile constructor: ECX receiver; installs base profile vtable 0x005e9ed0, vector-constructs 0x100 entries, copies descriptor bounds/stride/format fields, selects lookup table globals DAT_00657980 or DAT_00657a00, normalizes key-color bytes into floats, initializes all-one or descriptor-backed lookup rows for formats 0x28/0x29, computes active width/height/depth and row-span fields, and adjusts the base pointer when a row/depth pitch is present. Declared locked int ...(void) is false. Decompile recovers in_ECX plus three stack slots (descriptor, flags_or_key_bits, format_mode; names provisional); terminator RET 0xc proves three stack dwords after this. Shape is int __thiscall (void * this, void * descriptor, uint flags_or_key_bits, int format_mode). Static retail constructor evidence only; exact texel profile layout, descriptor layout, palette/key-color contract, runtime unpack behavior, BEA patching, and rebuild parity remain unproven.”
- This row is the shared constructor endpoint of every selected constructor plate. Its displayed body installs the base profile vtable, initializes a 0x100-entry region, copies descriptor fields, selects lookup-table globals, derives normalized key-color lanes, and computes extent/span fields, exactly as bounded by the packet comment; concrete field ownership, enum meaning, and runtime profile behavior remain unresolved.
- The non-empty packet decompile is bound by SHA-256 `b8a4163bd4b418d2a0634f0d9f507ea782460d480d497b26c70372c4d1ecb924`. This contract does not infer unstated format enum names, descriptor ABI, profile layout, channel policy, allocation ownership, callback contract, or runtime causality.
- Structured inventory: 43 caller record(s), 1 callee record(s), and 0 string-ref record(s). Manifest subfamily: `shared_descriptor_constructor`; contract number 301.

## Error / edge behavior
Null descriptor behavior, allocation ownership inside the vector-constructor helper, invalid mode/extent/key inputs, integer overflow, partial initialization, rollback, exception behavior, and caller interpretation of the scalar return are not_determinable. The displayed branches and paired review are the only bounded behavior evidence.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_3659ffdb`, immutable cohort-13 manifest SHA-256 `0f2e2819a98c54b5bccc2276c8cb20a937f5d189fcf241c6f8f3d293234663d2`, contract 301 of 301–325; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `d8f9f8b4e1f6b0ca5af890729fb108c39ecf1082`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`.
- Retained READY packet corpus: executable `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `7e2ce24fba986d78b11eb94f4d91beda96d7ce296016f1f18e881bfe43f56f1f`, packet decompile SHA-256 `b8a4163bd4b418d2a0634f0d9f507ea782460d480d497b26c70372c4d1ecb924`, packet READY SHA-256 `5381d8d632a1844967d7bb4e213b2398f479d95b0ebcac8108bbce1e0243c2d7`, and packet run-manifest SHA-256 `bed42bde09b14374113955605a5c11629b7c64204230f8659ac5cea0fa3a4bb0`; retained for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00581a4f:00581cbf;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Signature audit disposition `PACKET_REJECTED_HISTORICAL_SIGNATURE_RECONCILED`; packet-field contradiction `true`; no contradiction remains unresolved in the effective prototype.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W012/primary/A13.md`.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W012/adversarial/B13.md`.
- Packet stringRefs array: empty.
- Source-first authorities joined before packets: `reverse-engineering/source-crosswalk/crosswalk.tsv`, `reverse-engineering/source-crosswalk/expansion/w1-save-session-input-frontend/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w2-thing-battleengine-camera/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w3-audio-music/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w4-memory-container-archive/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w5-engine-render-platform-shell/RECEIPT.json`.
- Selected source crosswalk/reducer rows: none for this VA; this is an explicit packet-first row, not an assertion that no source analog exists.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, effective ABI audit, structured edge inventory, analyst comment, strings, paired static review, all source-authority joins, and TTD presence/absence are pinned. Descriptor/profile semantics, complete factory behavior, and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global/profile/descriptor record.
- Exact numeric format-id mapping, selected/unselected case boundary, channel/domain policy, vtable/callback contract, allocation ownership, and error cleanup.
- Runtime profile construction, texture conversion fidelity, side-effect ordering, failure behavior, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble the exact raw-body digest, verify ECX plus the three stack slots and every field/global access through RET 0xc, then invoke this constructor only in a controlled copied runtime with a retained real descriptor and compare the initialized profile bytes before any consumer runs.
