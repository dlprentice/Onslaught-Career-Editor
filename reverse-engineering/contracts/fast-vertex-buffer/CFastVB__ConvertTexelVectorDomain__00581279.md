# CFastVB__ConvertTexelVectorDomain

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__ConvertTexelVectorDomain` at `0x00581279` in the shared optional vec4 texel-domain conversion path used directly by all selected dithered packers; exact identity, direct codec connectivity, ABI audit, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, fresh read-only READY packet/decompile, structured edges, closure range, independently recomputed pristine body bytes, and paired W012/W013 static review; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00581279`

## Identity
- Body `[0x00581279,0x0058183c]`, 1476 bytes, 466 closure instructions. Raw pristine-body SHA-256 `3b19b9e07634ab8fba7f268265a0b8ca9bc99959eef307b634ef769b3b6c814d`; closure range SHA-256 `69d00f7c379084fffbb4cc6c75f51a618c78b9f0e9a1f86864212f42a5fb2572`; packet range-plus-bytes SHA-256 `89bce4dc8233fce8411bce3b29e93f13c395c61056906c78c360483c02305d9a`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table, current EVIDENCE-REGISTER, dated closure row, and fresh READY packet all name `CFastVB__ConvertTexelVectorDomain`.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `4f2de9c1e0bdfd2b465633bbc461cef18943a541ad395120c17784b48eb2b17f` and decompile SHA-256 `68f0c63945c056f98ac4f2e885e71594d42af008b5793b7a29e161c90d3730eb` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CFastVB__ConvertTexelVectorDomain(void * this, float * source_vec4_array)`. Fresh packet field accepted: `int __thiscall CFastVB__ConvertTexelVectorDomain(void * this, float * source_vec4_array)`. Current packet field matches the bounded ECX-this plus stack shape. Paired W012/W013 reviews record the older phantom unused_context field and exact RET/callsite refutation; the fresh packet preserves the corrected metadata, so no current packet-field contradiction remains. RET cleanup `RET 0x4` and paired static reviews are the bounded ABI witnesses; stronger ownership, nullability, and hidden-register meaning remain not_determinable.

## Prototype and parameter semantics
```c
int __thiscall CFastVB__ConvertTexelVectorDomain(void * this, float * source_vec4_array)
```
- The current packet field already incorporates the historically reviewed arity correction. Parameter labels remain analyst intent; concrete profile layout, units, aliasing, valid ranges, and ownership remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `int`. The packet comment is bounded evidence for its interpretation; exact domain, sentinels, status meaning, and caller expectations remain not_determinable unless explicitly stated there.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`PTR_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CDXTexture__ProbeTexelProfileSample` `0x00581d49` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackTexels_Dither_Bits8_8_8_BGR` `0x00582244` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackTexels_Dither_Bits8_8_8_8_ARGB` `0x00582355` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackTexels_Dither_Bits8_8_8_8_XRGB` `0x0058249e` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackTexels_Dither_Bits5_6_5` `0x005825c3` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackTexels_Dither_Bits5_5_5` `0x005826e8` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackTexels_Dither_A1R5G5B5` `0x0058280d` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackTexels_Dither_A4R4G4B4` `0x00582950` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Dither_Bits332` `0x00582a99` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Dither_Bits8` `0x00582bbe` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Dither_A8R3G3B2` `0x00582c8a` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Dither_Bits444` `0x00582dd3` x1 site(s) (instruction-flow).
- Caller `CDXTexture__PackTexels_Dither_Bits2_10_10_10` `0x00582ef8` x1 site(s) (instruction-flow).
- Caller `CDXTexture__PackTexels_Dither_Bits8888` `0x00583041` x1 site(s) (instruction-flow).
- Caller `CDXTexture__PackTexels_Dither_Bits888` `0x0058318a` x1 site(s) (instruction-flow).
- Caller `CDXTexture__PackTexels_Dither_Bits1616` `0x005832af` x1 site(s) (instruction-flow).
- Caller `CDXTexture__PackTexels_Dither_Bits2_10_10_10_Alt` `0x005833a6` x1 site(s) (instruction-flow).
- Caller `CDXTexture__PackTexels_Dither_Bits16_16_16_16` `0x005834ef` x1 site(s) (instruction-flow).
- Caller `CDXTexture__PackTexels_Dither_PaletteIndexA8` `0x00583670` x1 site(s) (instruction-flow).
- Caller `CDXTexture__PackTexels_PaletteIndex8` `0x005837b7` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackTexels_Dither_L8` `0x00583891` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackTexels_Dither_A8L8` `0x00583979` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Dither_A4L4` `0x00583a94` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Dither_L16` `0x00583ba4` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Dither_Bits8_8` `0x00583c8e` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Dither_Bits5_5_5` `0x00583d89` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Dither_Bits8_8_8_Alt` `0x00583eb3` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Dither_Bits8_8_8_8_Alt` `0x00583fe5` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackTexels_Dither_Bits16_16` `0x00584144` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackTexels_Dither_Bits2_10_10_10` `0x0058423f` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackTexels_Dither_Bits16_16_16_16` `0x0058439e` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Dither_Bits8_8_FromAuxLookup` `0x00584535` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Dither_L16_Alt` `0x0058463a` x1 site(s) (instruction-flow).
- Caller `CDXTexture__PackTexels_Dither_A16L16` `0x00584936` x1 site(s) (instruction-flow).
- Caller `CTexture__PackTexels_Bits16_16_16` `0x00584a4c` x1 site(s) (instruction-flow).
- Caller `CFastVB__StoreDecodedBlockToScratch` `0x0058735a` x1 site(s) (instruction-flow).
- Caller `CTexture__WriteTexelBlockWithQuadCache` `0x005876ab` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Callback-table selection, profile vtables, data references, library inlining, and runtime reachability remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five accepted source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Converts count-controlled vec4 texels from source_vec4_array into the scratch/output buffer at +0x1054 using source mode +0x08, target mode +0x1050, count +0x1060, observed scale/bias conversion paths for modes 1-3, and clamp-to-0..1 handling for mode 4. ECX receiver (profile this); terminator RET 0x4 proves one stack dword after this (source_vec4_array). Declared trailing int unused_context is false — not callee-cleaned and unused in body. Shape is int __thiscall (void * this, float * source_vec4_array) (names provisional). Static retail domain-conversion evidence only; exact texel-domain enum, color-space meaning, runtime conversion fidelity, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `68f0c63945c056f98ac4f2e885e71594d42af008b5793b7a29e161c90d3730eb`. This contract retains only its displayed pack/unpack/helper control and side-effect envelope and does not infer unstated format enums, channel policy, color space, dithering provenance, profile layout, or runtime causality.
- Structured inventory: 37 caller record(s), 0 callee record(s), and 0 string-ref record(s). Manifest subfamily: `pack_shared_helper`.

## Error / edge behavior
Nullability, zero-count behavior beyond the displayed branches, invalid profile state, output bounds, aliasing, allocation/device failure, callback failure, NaN/Inf/denormal and out-of-range conversion policy, exact dither/color-space rules, key-color equality policy, rollback semantics, and malformed texture input handling are not_determinable as a class from packet metadata. The decompile, quoted comment, RET audit, and paired static review are bounded evidence; missing branch-level behavior remains open.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_17fded87`, immutable cohort-12 v2 manifest SHA-256 `838ab5085349e44048c46b8e04d13321d71317ff984fe9bc521c232d649ffc2b`, row 1; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `ddd607077ec57a0def7595de7e9050faf1eaa62a`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `4f2de9c1e0bdfd2b465633bbc461cef18943a541ad395120c17784b48eb2b17f`, and packet decompile SHA-256 `68f0c63945c056f98ac4f2e885e71594d42af008b5793b7a29e161c90d3730eb`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00581279:0058183c;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Signature audit disposition `PACKET_ACCEPTED_AFTER_HISTORICAL_ARITY_CORRECTION`; current packet-field contradiction count for this row is zero. Historical phantom-argument correction is retained by the paired authorities below rather than restated as a current packet defect.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W012/primary/A13.md`.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W012/adversarial/B13.md`.
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
