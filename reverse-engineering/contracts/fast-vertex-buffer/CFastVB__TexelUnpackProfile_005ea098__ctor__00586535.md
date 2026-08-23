# CFastVB__TexelUnpackProfile_005ea098__ctor

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__TexelUnpackProfile_005ea098__ctor` at `0x00586535` in the numeric format-id texel-unpack profile constructor plate on the exact factory-to-shared-constructor path; exact identity, selected call connectivity, ABI audit, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register/closure identity, retained read-only READY packet/decompile, structured edges, fresh pristine body copy and digest recomputation, and paired static review; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00586535`

## Identity
- Body `[0x00586535,0x00586550]`, 28 bytes, 10 closure instructions. Raw pristine-body SHA-256 `51541888d5e0610b35164753116e685b43ae05ddfc626f82c32e8164a5c2f7f7`; closure range SHA-256 `8a63e210d6f79ac710b94b64178e0bebc435fe7751872a6f4bf0a86d624c7c5a`; packet range-plus-bytes SHA-256 `ced089ec19180eea8e331ceff9b2d3cf9f5320c2eed453ebe2466ded73415008`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table, current EVIDENCE-REGISTER, dated closure row, and retained READY packet all name `CFastVB__TexelUnpackProfile_005ea098__ctor`.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `84d32ef1ae8be8360751c410e2aa8548de612af2d2962d1d00aa97d6fc403ab0` and decompile SHA-256 `f660a2c593b2bdeed94ac74cf004547f51ad0c85d1ea946cf13cc446313faf80` bind the retained review input without citing a writer-local path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.
- Current closure/packet range is used exactly; no padding or neighboring bytes are interpreted as additional semantics by this contract.

## Calling convention
Packet records `__thiscall` for `void * __thiscall CFastVB__TexelUnpackProfile_005ea098__ctor(void * this, void * format_descriptor)`. Current field accepted. Packet field matches paired W013 constructor-plate review: ECX receiver, one stack descriptor, and RET 0x4. Legacy InitTexelUnpackVTable names remain current name debt where stated; no rename is applied or silently inherited. RET cleanup witness: `RET 0x4`.

## Prototype and parameter semantics
```c
void * __thiscall CFastVB__TexelUnpackProfile_005ea098__ctor(void * this, void * format_descriptor)
```
- Packet field and paired static review agree on this bounded ABI plate. Parameter labels remain analyst intent; concrete descriptor/profile layouts, ownership, valid ranges, and enum meaning remain not_determinable.

## Return value meaning
The accepted packet signature declares `void *`. The packet comment and paired W013 review bound the return as the constructor's `this` value after binding the displayed vtable, but ownership, lifetime, nullability, subtype semantics, and caller obligations remain unresolved.

## Globals read/written
- Decompile symbol references: `PTR_CFastVB__TexelUnpackProfile_scalar_deleting_dtor_005ea098`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CFastVB__TexelUnpackProfile__ctorFromDescriptor` `0x00581a4f` x1 site(s) (STATIC_DIRECT).
- Caller `CFastVB__CreateTexelUnpackProfileByFormat` `0x00587e82` x1 site(s) (instruction-flow).
- Selected-cohort adjacency: 1 incoming and 1 outgoing direct edge(s) within the exact 25-row component. Full packet arrays above remain authoritative for external direct edges.
- Structured packet arrays prove listed direct/static edge identities and site counts only. Indirect callbacks, vtable selection beyond displayed stores, data references, library inlining, and runtime reachability remain unresolved unless separately bounded.

## Behavior summary
- Packet-first boundary: the current 1,783-row canonical crosswalk, five accepted source-reducer receipts, and pinned source commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Manifest selection basis: case-0x34.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave674 static read-back: texel-unpack profile constructor thunk reached from CFastVB__CreateTexelUnpackProfileByFormat case 0x34 / call-site 0x005881ca after a 0x1074 allocation; it calls CFastVB__TexelUnpackProfile__ctorFromDescriptor(format_descriptor), binds vtable 0x005ea098, and returns this with RET 0x4. Static metadata only; exact profile ABI, descriptor layout, callback-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.”
- Packet case/callsite boundary: case-0x34. The plate is directly called by the selected format factory and directly calls the shared descriptor constructor before binding its displayed vtable. Where the current name begins `InitTexelUnpackVTable`, paired review explicitly records name debt toward the constructor-plate family; this contract preserves the current name and does not silently apply the proposed rename.
- The non-empty packet decompile is bound by SHA-256 `f660a2c593b2bdeed94ac74cf004547f51ad0c85d1ea946cf13cc446313faf80`. This contract does not infer unstated format enum names, descriptor ABI, profile layout, channel policy, allocation ownership, callback contract, or runtime causality.
- Structured inventory: 1 caller record(s), 1 callee record(s), and 0 string-ref record(s). Manifest subfamily: `numeric_format_constructor`; contract number 323.

## Error / edge behavior
Null receiver/descriptor behavior, base-constructor failure propagation, descriptor validity, vtable lifetime, allocation ownership, partial initialization, exception behavior, and downstream setup-callback requirements are not_determinable. The ten-instruction constructor shape and RET 0x4 audit do not prove runtime format output.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_3659ffdb`, immutable cohort-13 manifest SHA-256 `0f2e2819a98c54b5bccc2276c8cb20a937f5d189fcf241c6f8f3d293234663d2`, contract 323 of 301–325; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `d8f9f8b4e1f6b0ca5af890729fb108c39ecf1082`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`.
- Retained READY packet corpus: executable `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `84d32ef1ae8be8360751c410e2aa8548de612af2d2962d1d00aa97d6fc403ab0`, packet decompile SHA-256 `f660a2c593b2bdeed94ac74cf004547f51ad0c85d1ea946cf13cc446313faf80`, packet READY SHA-256 `5381d8d632a1844967d7bb4e213b2398f479d95b0ebcac8108bbce1e0243c2d7`, and packet run-manifest SHA-256 `bed42bde09b14374113955605a5c11629b7c64204230f8659ac5cea0fa3a4bb0`; retained for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00586535:00586550;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Signature audit disposition `PACKET_ACCEPTED`; packet-field contradiction `false`; no contradiction remains unresolved in the effective prototype.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W013/primary/A02.md`.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W013/adversarial/B02.md`.
- Packet stringRefs array: empty.
- Source-first authorities joined before packets: `reverse-engineering/source-crosswalk/crosswalk.tsv`, `reverse-engineering/source-crosswalk/expansion/w1-save-session-input-frontend/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w2-thing-battleengine-camera/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w3-audio-music/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w4-memory-container-archive/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w5-engine-render-platform-shell/RECEIPT.json`.
- Selected source crosswalk/reducer rows: none for this VA; this is an explicit packet-first row, not an assertion that no source analog exists.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, effective ABI audit, structured edge inventory, analyst comment, strings, paired static review, all source-authority joins, and TTD presence/absence are pinned. Descriptor/profile semantics, complete factory behavior, and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global/profile/descriptor record.
- Exact numeric format-id mapping, selected/unselected case boundary, channel/domain policy, vtable/callback contract, allocation ownership, and error cleanup.
- Runtime profile construction, texture conversion fidelity, side-effect ordering, failure behavior, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble the exact raw-body digest and verify the factory caller, descriptor push, shared-constructor call, vtable store, returned receiver, and RET 0x4; then select this exact factory case in a controlled copied runtime and compare constructor target, bound vtable, initialized bytes, and returned pointer.
