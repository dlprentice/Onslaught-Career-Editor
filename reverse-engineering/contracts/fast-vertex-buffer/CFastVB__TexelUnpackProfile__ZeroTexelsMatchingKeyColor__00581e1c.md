# CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor` at `0x00581e1c` in the shared optional exact key-color zeroing path used directly by all selected unpackers; exact identity, direct codec connectivity, ABI audit, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, fresh read-only READY packet/decompile, structured edges, closure range, independently recomputed pristine body bytes, and paired W012/W013 static review; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00581e1c`

## Identity
- Body `[0x00581e1c,0x00581e8b]`, 112 bytes, 46 closure instructions. Raw pristine-body SHA-256 `a14b0ed17037f8aa80d5f0c56b7477555ffb9e0b43b61757c1b6c248587fd105`; closure range SHA-256 `a354eb9a3735a9f291f07078a5b268c8d5e4af24384a8e3246fc4c590e354f79`; packet range-plus-bytes SHA-256 `c0f046d667aff8bb08ec2e77302f2e915b59527d98272966f603c211a867d6dd`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table, current EVIDENCE-REGISTER, dated closure row, and fresh READY packet all name `CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor`.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `2dc1e5b2b52123e131d22cb5e0fdc3292352370c0c409bdebec962aa6b4acaed` and decompile SHA-256 `1ebaaf77230aa648dc76d13466fb5cdbac42e3c35002c2470b58fe251b0bb411` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor(void * this, float * texel_vec4_array)`. Fresh packet field accepted: `void __thiscall CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor(void * this, float * texel_vec4_array)`. Current packet field matches the bounded ECX-this plus stack shape. Paired W012/W013 reviews record the older phantom unused_context field and exact RET/callsite refutation; the fresh packet preserves the corrected metadata, so no current packet-field contradiction remains. RET cleanup `RET 0x4` and paired static reviews are the bounded ABI witnesses; stronger ownership, nullability, and hidden-register meaning remain not_determinable.

## Prototype and parameter semantics
```c
void __thiscall CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor(void * this, float * texel_vec4_array)
```
- The current packet field already incorporates the historically reviewed arity correction. Parameter labels remain analyst intent; concrete profile layout, units, aliasing, valid ranges, and ownership remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and called targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`PTR_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CTexture__UnpackTexels_Bgr8ToFloat4` `0x00584b5f` x1 site(s) (instruction-flow).
- Caller `CTexture__UnpackTexels_Bgra8ToFloat4` `0x00584c04` x1 site(s) (instruction-flow).
- Caller `CTexture__UnpackTexels_Bgr8ToFloat4_AlphaOne` `0x00584cc3` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_Bits565ToFloat4` `0x00584d78` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne` `0x00584e32` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_Bits1555ToFloat4` `0x00584ee9` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_Bits4444ToFloat4` `0x00584fae` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4` `0x00585072` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_Bits8888ToFloat4` `0x00585161` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_Bits888ToFloat4_AlphaOne` `0x00585220` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_Bits16_16_ToFloat4_RG` `0x005852d5` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4_Alt` `0x00585380` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_Bits16_16_16_16_ToFloat4` `0x0058546f` x1 site(s) (instruction-flow).
- Caller `CDXTexture__UnpackTexels_Bits332ToFloat4` `0x00585576` x1 site(s) (instruction-flow).
- Caller `CDXTexture__UnpackTexels_A8ToFloat4_ZeroRGB` `0x0058562d` x1 site(s) (instruction-flow).
- Caller `CDXTexture__UnpackTexels_Bits332A8ToFloat4` `0x005856b8` x1 site(s) (instruction-flow).
- Caller `CTexture__UnpackTexels_Bits444ToFloat4_AlphaOne` `0x0058579b` x1 site(s) (instruction-flow).
- Caller `CTexture__UnpackTexels_PaletteIndexA8ToFloat4` `0x0058586b` x1 site(s) (instruction-flow).
- Caller `FUN_00585940` `0x00585940` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_L8ToFloat4` `0x005859d8` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_L8A8ToFloat4` `0x00585a7b` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_A4L4ToFloat4` `0x00585b35` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_L16ToFloat4` `0x00585c0b` x1 site(s) (instruction-flow).
- Caller `CTexture__UnpackTexels_Signed8_8_ToFloat4_RG` `0x00585cb0` x1 site(s) (instruction-flow).
- Caller `CDXTexture__UnpackTexels_Signed5_5_A6_ToFloat4` `0x00585da3` x1 site(s) (instruction-flow).
- Caller `CDXTexture__UnpackTexels_Signed8_8_A8_ToFloat4_RG` `0x00585e9f` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4` `0x00585fa3` x1 site(s) (instruction-flow).
- Caller `CTexture__UnpackTexels_Signed16_16_ToFloat4_RG` `0x005860ba` x1 site(s) (instruction-flow).
- Caller `CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4` `0x005861b4` x1 site(s) (instruction-flow).
- Caller `CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4` `0x00586305` x1 site(s) (instruction-flow).
- Caller `CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ` `0x00586438` x1 site(s) (instruction-flow).
- Caller `FUN_0058656d` `0x0058656d` x1 site(s) (instruction-flow).
- Caller `CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_ForceGBAOne` `0x00586609` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne` `0x005866d2` x1 site(s) (instruction-flow).
- Caller `CDXTexture__UnpackTexels_CallbackSpanDispatch` `0x0058677b` x1 site(s) (instruction-flow).
- Caller `FUN_005867ee` `0x005867ee` x1 site(s) (instruction-flow).
- Caller `CTexture__UnpackTexels_CopyRaw128` `0x0058686f` x1 site(s) (instruction-flow).
- Caller `CFastVB__UnpackTexels_L16A16_ToFloat4` `0x005868d1` x1 site(s) (instruction-flow).
- Caller `CTexture__UnpackTexels_Bits16_16_16_ToFloat4` `0x005869b0` x1 site(s) (instruction-flow).
- Caller `CFastVB__LoadDecodedBlockFromScratch` `0x005873f8` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Callback-table selection, profile vtables, data references, library inlining, and runtime reachability remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five accepted source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Walks count-controlled vec4 texels from texel_vec4_array and zeros all four channels when they exactly match the key vec4 stored at +0x24/+0x28/+0x2c/+0x30. ECX receiver (profile this); after PUSH ESI body loads the sole stack formal via [ESP+0x8]; terminator RET 0x4 proves one stack dword after this. Declared trailing uint unused_context is false — not callee-cleaned; unpack callers (e.g. CTexture__UnpackTexels_Bgr8ToFloat4) push one stack arg only. Shape is void __thiscall (void * this, float * texel_vec4_array) (names provisional). Static retail color-key evidence only; exact color-key policy, floating-point equality semantics, runtime transparency behavior, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `1ebaaf77230aa648dc76d13466fb5cdbac42e3c35002c2470b58fe251b0bb411`. This contract retains only its displayed pack/unpack/helper control and side-effect envelope and does not infer unstated format enums, channel policy, color space, dithering provenance, profile layout, or runtime causality.
- Structured inventory: 40 caller record(s), 0 callee record(s), and 0 string-ref record(s). Manifest subfamily: `unpack_shared_helper`.

## Error / edge behavior
Nullability, zero-count behavior beyond the displayed branches, invalid profile state, output bounds, aliasing, allocation/device failure, callback failure, NaN/Inf/denormal and out-of-range conversion policy, exact dither/color-space rules, key-color equality policy, rollback semantics, and malformed texture input handling are not_determinable as a class from packet metadata. The decompile, quoted comment, RET audit, and paired static review are bounded evidence; missing branch-level behavior remains open.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_17fded87`, immutable cohort-12 v2 manifest SHA-256 `838ab5085349e44048c46b8e04d13321d71317ff984fe9bc521c232d649ffc2b`, row 14; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `ddd607077ec57a0def7595de7e9050faf1eaa62a`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `2dc1e5b2b52123e131d22cb5e0fdc3292352370c0c409bdebec962aa6b4acaed`, and packet decompile SHA-256 `1ebaaf77230aa648dc76d13466fb5cdbac42e3c35002c2470b58fe251b0bb411`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00581e1c:00581e8b;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
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
