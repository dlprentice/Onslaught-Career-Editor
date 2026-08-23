# CFastVB__TexelUnpackProfile_005ea214__ctor

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__TexelUnpackProfile_005ea214__ctor` at `0x0058733e` in the numeric-format texel-unpack profile constructor plate on a bounded slice of the post-cohort-13 tail of the texel-unpack/codec/registry format-id factory dispatch, directly called by the contracted format factory and forwarding to the shared descriptor constructor `CFastVB__TexelUnpackProfile__ctorFromDescriptor` before binding its displayed vtable; exact identity, selected call connectivity, ABI audit, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register/closure identity, retained read-only READY packet/decompile, structured edges, fresh pristine body copy and digest recomputation, and paired static review; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0058733e`

## Identity
- Body `[0x0058733e,0x00587359]`, 28 bytes, 10 closure instructions. Raw pristine-body SHA-256 `da76770866d68ed26e7a03bc4e9a8d3c44f7179b0e2588b1f224ef92059f8e13`; closure range SHA-256 `fc05c3d8c239dbae79b088a7a11260d37f784f66a75ccca38e422405062a1764`; packet range-plus-bytes SHA-256 `5ef98a80818f59296fc3f4b68b957f959f5c38b61309850cfb206185466a1be6`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table, current EVIDENCE-REGISTER, dated closure row, and retained READY packet all name `CFastVB__TexelUnpackProfile_005ea214__ctor`.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `e072ebdb7520a7f2136358b3df6eab2a3d7a2599f493d5104e17d777b0f1a904` and decompile SHA-256 `5bc10b25e205f9ba8465085849105e4e76646d725162430ed90542ced9963b08` bind the retained review input without citing a writer-local path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.
- Current closure/packet range is used exactly; no padding or neighboring bytes are interpreted as additional semantics by this contract.

## Calling convention
Packet records `__thiscall` for `void * __thiscall CFastVB__TexelUnpackProfile_005ea214__ctor(void * this, void * format_descriptor)`. Current field accepted. Packet field matches paired W013 constructor-plate review: ECX receiver, one stack descriptor, and RET 0x4. Legacy InitTexelUnpackVTable names remain current name debt where stated by the packet comment and paired review; no rename is applied or silently inherited. RET cleanup witness: `RET 0x4`.

## Prototype and parameter semantics
```c
void * __thiscall CFastVB__TexelUnpackProfile_005ea214__ctor(void * this, void * format_descriptor)
```
- Packet field and paired static review agree on this bounded ABI plate. Parameter labels remain analyst intent; concrete descriptor/profile layouts, ownership, valid ranges, and enum meaning remain not_determinable.

## Return value meaning
The accepted packet signature declares `void *`. The packet comment and paired W013 review bound the return as the constructor's `this` value after binding the displayed vtable, but ownership, lifetime, nullability, subtype semantics, and caller obligations remain unresolved.

## Globals read/written
- Decompile symbol references: `PTR_CFastVB__TexelUnpackProfile_scalar_deleting_dtor_005ea214`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CFastVB__TexelUnpackProfile__ctorFromDescriptor` `0x00581a4f` x1 site(s) (STATIC_DIRECT).
- Caller `CFastVB__CreateTexelUnpackProfileByFormat` `0x00587e82` x1 site(s) (instruction-flow).
- Selected-cohort adjacency: 1 incoming direct edge record(s), all external — the recorded factory caller `CFastVB__CreateTexelUnpackProfileByFormat` `0x00587e82`, which is contracted inside 301–325 and is not part of cohort 14 — and 0 outgoing records. In-cohort selected-to-selected directed edges: 0. Full packet arrays above remain authoritative for all other direct edges.
- Structured packet arrays prove listed direct/static edge identities and site counts only. Indirect callbacks, vtable selection beyond displayed stores, data references, library inlining, and runtime reachability remain unresolved unless separately bounded.

## Behavior summary
- Packet-first boundary: the current 1,783-row canonical crosswalk, five accepted source-reducer receipts, and pinned source commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave675 static read-back: profile constructor forwards the format descriptor to the shared texel-unpack profile initializer, then binds vtable 0x005ea214. Static metadata only; exact descriptor ABI and factory contract remain unproven.”
- Packet case/callsite boundary: post-0x29 numeric span callsite; packet does not claim a discrete case id. The plate is directly called by `CFastVB__CreateTexelUnpackProfileByFormat` (`0x00587e82`, contracted within 301–325) and its structured callers array records exactly that single direct call site. The displayed body forwards `format_descriptor` to the shared descriptor constructor (contracted as part of contracts 301–325), binds the displayed vtable pointer, and returns the receiver. Where the current name begins `InitTexelUnpackVTable`, paired review explicitly records name debt toward the constructor-plate family; this contract preserves the current name and does not silently apply the proposed rename.
- The non-empty packet decompile is bound by SHA-256 `5bc10b25e205f9ba8465085849105e4e76646d725162430ed90542ced9963b08`. This contract does not infer unstated format enum names, descriptor ABI, profile layout, channel policy, allocation ownership, callback contract, or runtime causality.
- Structured inventory: 1 caller record(s), 1 callee record(s), and 0 string-ref record(s). Manifest subfamily: `numeric_format_constructor`; contract number 343.

## Error / edge behavior
Null receiver/descriptor behavior, forwarded-initializer failure propagation, descriptor validity, vtable lifetime, allocation ownership, partial initialization, exception behavior, and downstream setup-callback requirements are not_determinable. The 10-instruction constructor shape and RET 0x4 audit do not prove runtime format output.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_7f6409fd`, immutable cohort-14 rework manifest SHA-256 `ccea1e59506e523f375a1efd6362ec2d84ac6cffc147f536ebd4cc3b6d22efbd`, contract 343 of 326–350; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `221d7811cd932306a52ddb6ebc155cc87e2d00d7`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`.
- Retained READY packet corpus: executable `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `e072ebdb7520a7f2136358b3df6eab2a3d7a2599f493d5104e17d777b0f1a904`, packet decompile SHA-256 `5bc10b25e205f9ba8465085849105e4e76646d725162430ed90542ced9963b08`, packet READY SHA-256 `5381d8d632a1844967d7bb4e213b2398f479d95b0ebcac8108bbce1e0243c2d7`, and packet run-manifest SHA-256 `bed42bde09b14374113955605a5c11629b7c64204230f8659ac5cea0fa3a4bb0`; retained for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `0058733e:00587359;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Signature audit disposition `PACKET_ACCEPTED`; packet-field contradiction `false`; no contradiction remains unresolved in the effective prototype.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W013/primary/A03.md`.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W013/adversarial/B03.md`.
- Packet stringRefs array: empty.
- Source-first authorities joined before packets: `reverse-engineering/source-crosswalk/crosswalk.tsv`, `reverse-engineering/source-crosswalk/expansion/w1-save-session-input-frontend/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w2-thing-battleengine-camera/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w3-audio-music/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w4-memory-container-archive/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w5-engine-render-platform-shell/RECEIPT.json`.
- Selected source crosswalk/reducer rows: none for this VA; this is an explicit packet-first row, not an assertion that no source analog exists.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, effective ABI audit, structured edge inventory, analyst comment, strings, paired static review, all source-authority joins, and TTD presence/absence are pinned. Descriptor/profile semantics, complete factory behavior, and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global/profile/descriptor record.
- Exact numeric/FourCC-like format-id mapping, selected/unselected case boundary, channel/domain policy, vtable/callback contract, allocation ownership, and error cleanup.
- Runtime profile construction, texture conversion fidelity, side-effect ordering, failure behavior, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble the exact raw-body digest and verify the factory caller, descriptor push, forwarded-initializer call, vtable store, returned receiver, and RET 0x4; then select this exact factory case in a controlled copied runtime and compare constructor target, bound vtable, initialized bytes, and returned pointer.
