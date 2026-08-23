# CFastVB__PackTexels_Dither_Bits8_8_8_BGR

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__PackTexels_Dither_Bits8_8_8_BGR` at `0x00582244` in the direct-call-connected concrete dithered packed-texel format encoder; exact identity, direct codec connectivity, ABI audit, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, fresh read-only READY packet/decompile, structured edges, closure range, independently recomputed pristine body bytes, and paired W012/W013 static review; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00582244`

## Identity
- Body `[0x00582244,0x00582354]`, 273 bytes, 92 closure instructions. Raw pristine-body SHA-256 `060932818ddbd89738e1a75071ea63b8be10accb0f6a96073f07e8e131f6dc33`; closure range SHA-256 `dea15edf7658d8dbbcb24107075ded6735af6b3cddb65850d6182d0cc4f8c0e5`; packet range-plus-bytes SHA-256 `934436d120093d563bdf441cc4dfbd444624cf6c6768d6828c640ef1ec0c5696`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table, current EVIDENCE-REGISTER, dated closure row, and fresh READY packet all name `CFastVB__PackTexels_Dither_Bits8_8_8_BGR`.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `ffe74764c24951b387c22e85247d493c2271b8213642631d9631836a0495379a` and decompile SHA-256 `3ac03e1507c56a66d29b8d4d126ca85a923a32c08eaf1ceee4294cb7816b51d3` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFastVB__PackTexels_Dither_Bits8_8_8_BGR(void * this, uint output_x, uint output_y, float * source_vec4_array)`. Fresh packet field accepted: `void __thiscall CFastVB__PackTexels_Dither_Bits8_8_8_BGR(void * this, uint output_x, uint output_y, float * source_vec4_array)`. Current packet field matches the bounded ECX-this plus stack shape. Paired W012/W013 reviews record the older phantom unused_context field and exact RET/callsite refutation; the fresh packet preserves the corrected metadata, so no current packet-field contradiction remains. RET cleanup `RET 0xc` and paired static reviews are the bounded ABI witnesses; stronger ownership, nullability, and hidden-register meaning remain not_determinable.

## Prototype and parameter semantics
```c
void __thiscall CFastVB__PackTexels_Dither_Bits8_8_8_BGR(void * this, uint output_x, uint output_y, float * source_vec4_array)
```
- The current packet field already incorporates the historically reviewed arity correction. Parameter labels remain analyst intent; concrete profile layout, units, aliasing, valid ranges, and ownership remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and called targets.

## Globals read/written
- Decompile symbol references: `DAT_009d0c58`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CFastVB__ConvertTexelVectorDomain` `0x00581279` x1 site(s) (STATIC_DIRECT).
- Callee `CDXTexture__NormalizeAndCopyVec4Array` `0x00581e8c` x1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Callback-table selection, profile vtables, data references, library inlining, and runtime reachability remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five accepted source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Dithered packer callback at table slot 0x005e9f44 writes three bytes per output texel in B,G,R order using output pointer fields +0x1058/+0x105c/+0x20, count +0x1060, dither table +0x34, optional domain conversion +0x1050, and optional normalization +0x10. ECX receiver; terminator RET 0xc proves three stack dwords after this (output_x, output_y, source_vec4_array). Declared trailing int unused_context is false — not callee-cleaned and unused in body; unaff_EDI third pushes into ConvertTexelVectorDomain/NormalizeAndCopyVec4Array are register garbage, not a fourth stack formal. Shape is void __thiscall (void * this, uint output_x, uint output_y, float * source_vec4_array) (names provisional). Static retail dither-pack evidence only; exact format enum, color-space contract, runtime texture output, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `3ac03e1507c56a66d29b8d4d126ca85a923a32c08eaf1ceee4294cb7816b51d3`. This contract retains only its displayed pack/unpack/helper control and side-effect envelope and does not infer unstated format enums, channel policy, color space, dithering provenance, profile layout, or runtime causality.
- Structured inventory: 0 caller record(s), 2 callee record(s), and 0 string-ref record(s). Manifest subfamily: `texel_packer`.

## Error / edge behavior
Nullability, zero-count behavior beyond the displayed branches, invalid profile state, output bounds, aliasing, allocation/device failure, callback failure, NaN/Inf/denormal and out-of-range conversion policy, exact dither/color-space rules, key-color equality policy, rollback semantics, and malformed texture input handling are not_determinable as a class from packet metadata. The decompile, quoted comment, RET audit, and paired static review are bounded evidence; missing branch-level behavior remains open.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_17fded87`, immutable cohort-12 v2 manifest SHA-256 `838ab5085349e44048c46b8e04d13321d71317ff984fe9bc521c232d649ffc2b`, row 2; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `ddd607077ec57a0def7595de7e9050faf1eaa62a`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `ffe74764c24951b387c22e85247d493c2271b8213642631d9631836a0495379a`, and packet decompile SHA-256 `3ac03e1507c56a66d29b8d4d126ca85a923a32c08eaf1ceee4294cb7816b51d3`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00582244:00582354;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Signature audit disposition `PACKET_ACCEPTED_AFTER_HISTORICAL_ARITY_CORRECTION`; current packet-field contradiction count for this row is zero. Historical phantom-argument correction is retained by the paired authorities below rather than restated as a current packet defect.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W012/primary/A14.md`.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W012/adversarial/B14.md`.
- Packet stringRefs array: empty.
- Source-first authorities joined before packets: `reverse-engineering/source-crosswalk/crosswalk.tsv`, `reverse-engineering/source-crosswalk/expansion/w1-save-session-input-frontend/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w2-thing-battleengine-camera/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w3-audio-music/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w4-memory-container-archive/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w5-engine-render-platform-shell/RECEIPT.json`.
- Selected source crosswalk rows: none for this VA; this is an explicit packet-first row, not an assertion that no source analog exists.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, current packet signature/RET audit, structured edge inventory, comments, strings, paired static review, all source-authority joins, and TTD presence/absence are pinned. Format/profile semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global/profile record.
- Exact texture format enum mapping, channel ordering where hedged, color space/domain modes, dither-table provenance, key-color policy, stride/count units, and output bounds.
- Complete callback/vtable target set and failure/nullability behavior.
- Runtime pack/unpack fidelity, numeric edge policy, side-effect ordering, output ownership, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/RET/direct call against the packet decompile and structured arrays, then run one controlled copied-runtime texel vector through the named format path and compare exact packed or float4 output bytes.
