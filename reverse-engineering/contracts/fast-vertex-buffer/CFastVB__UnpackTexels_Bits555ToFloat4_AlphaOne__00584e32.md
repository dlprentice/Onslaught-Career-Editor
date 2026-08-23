# CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne` at `0x00584e32` in the direct-call-connected concrete packed-texel-to-float4 decoder; exact identity, direct codec connectivity, ABI audit, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, fresh read-only READY packet/decompile, structured edges, closure range, independently recomputed pristine body bytes, and paired W012/W013 static review; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00584e32`

## Identity
- Body `[0x00584e32,0x00584ee8]`, 183 bytes, 66 closure instructions. Raw pristine-body SHA-256 `335728518cc04e1d40c995ea0bce8daf5918b45f3b21dcd52065824b29a745f8`; closure range SHA-256 `5bb5af53b5bddbce819ccde889a785beb3e0c454e8eb887ae19ba0b9f29acf22`; packet range-plus-bytes SHA-256 `24be8fce9c12f8d144678ad07ff9d4086c6a0120455569c4657f36160763f156`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table, current EVIDENCE-REGISTER, dated closure row, and fresh READY packet all name `CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne`.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `15efaccde29197f802f099cc33471a004fee3f3d3a750f77a8ade37bd603c35c` and decompile SHA-256 `167b0575616c615a724edfaf2381839c3a71fb3e386fb7aa485b1ffc060da5bc` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne(void * this, uint source_x, uint source_y, float * destination_vec4_array)`. Fresh packet field accepted: `void __thiscall CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne(void * this, uint source_x, uint source_y, float * destination_vec4_array)`. Current packet field matches the bounded ECX-this plus stack shape. Paired W012/W013 reviews record the older phantom unused_context field and exact RET/callsite refutation; the fresh packet preserves the corrected metadata, so no current packet-field contradiction remains. RET cleanup `RET 0xc` and paired static reviews are the bounded ABI witnesses; stronger ownership, nullability, and hidden-register meaning remain not_determinable.

## Prototype and parameter semantics
```c
void __thiscall CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne(void * this, uint source_x, uint source_y, float * destination_vec4_array)
```
- The current packet field already incorporates the historically reviewed arity correction. Parameter labels remain analyst intent; concrete profile layout, units, aliasing, valid ranges, and ownership remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and called targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`PTR_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor` `0x00581e1c` x1 site(s) (STATIC_DIRECT).
- Callee `CTexture__PostProcessDecodedTexels_GammaOrSquare` `0x0058210e` x1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Callback-table selection, profile vtables, data references, library inlining, and runtime reachability remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five accepted source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “5-5-5 alpha-one texel unpacker: ECX receiver; computes packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, expands three 5-bit color lanes with alpha 1.0 to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Terminator RET 0xc proves three stack dwords after this (source_x, source_y, destination_vec4_array). Declared trailing int unused_context is false — not callee-cleaned and unused in body. Shape is void __thiscall (void * this, uint source_x, uint source_y, float * destination_vec4_array) (names provisional). Static retail unpacker evidence only; exact profile ABI, format-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `167b0575616c615a724edfaf2381839c3a71fb3e386fb7aa485b1ffc060da5bc`. This contract retains only its displayed pack/unpack/helper control and side-effect envelope and does not infer unstated format enums, channel policy, color space, dithering provenance, profile layout, or runtime causality.
- Structured inventory: 0 caller record(s), 2 callee record(s), and 0 string-ref record(s). Manifest subfamily: `texel_unpacker`.

## Error / edge behavior
Nullability, zero-count behavior beyond the displayed branches, invalid profile state, output bounds, aliasing, allocation/device failure, callback failure, NaN/Inf/denormal and out-of-range conversion policy, exact dither/color-space rules, key-color equality policy, rollback semantics, and malformed texture input handling are not_determinable as a class from packet metadata. The decompile, quoted comment, RET audit, and paired static review are bounded evidence; missing branch-level behavior remains open.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_17fded87`, immutable cohort-12 v2 manifest SHA-256 `838ab5085349e44048c46b8e04d13321d71317ff984fe9bc521c232d649ffc2b`, row 16; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `ddd607077ec57a0def7595de7e9050faf1eaa62a`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `15efaccde29197f802f099cc33471a004fee3f3d3a750f77a8ade37bd603c35c`, and packet decompile SHA-256 `167b0575616c615a724edfaf2381839c3a71fb3e386fb7aa485b1ffc060da5bc`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00584e32:00584ee8;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Signature audit disposition `PACKET_ACCEPTED_AFTER_HISTORICAL_ARITY_CORRECTION`; current packet-field contradiction count for this row is zero. Historical phantom-argument correction is retained by the paired authorities below rather than restated as a current packet defect.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W012/primary/A15.md`.
- Paired static review authority: `reverse-engineering/binary-analysis/ghidra-fullpass-findings/W012/adversarial/B15.md`.
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
