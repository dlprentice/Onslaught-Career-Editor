# CFastVB__RenderTriangleStripImmediate

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__RenderTriangleStripImmediate` at `0x0051a6a0` in the FastVB dynamic-buffer lifecycle, lock/update, and draw runtime; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0051a6a0`

## Identity
- Body `[0x0051a6a0,0x0051a6ff]`, 96 bytes, 32 closure instructions. Raw pristine-body SHA-256 `7686179af00ab6146e336691acb4eb919a28c8ed906e9ca45dedba2657d87db1`; closure range SHA-256 `acea1b191fd56c48a1b8df405f7fbba644872872f079d8fc03b7a1a27c8941a7`; packet range-plus-bytes SHA-256 `2f1060d19565251bc4c3897345df2016d10354578dc9173698a7af76165dd7f9`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__RenderTriangleStripImmediate`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `a06fb458f43aa154e95f68c8b5aa880da030f9d89a80597bac3f76c08858c1f5` and decompile SHA-256 `f992565bb72e0523b9981269ae9cc3f917e5a3efe61729e2a08f3ca60333a0f7` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFastVB__RenderTriangleStripImmediate(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFastVB__RenderTriangleStripImmediate(void * this)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, nullability, and unlisted register-carried values remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00855bb0`, `DAT_00888a50`, `DAT_00897a90`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CVBuffer__Unlock` `0x005001e0` x1 site(s) (STATIC_DIRECT).
- Callee `CEngine__SetVertexShaderHandleRaw` `0x00513ec0` x1 site(s) (STATIC_DIRECT).
- Caller `CConsole__RenderLoadingScreen` `0x0042c810` x1 site(s) (instruction-flow).
- Caller `CRenderQueue_T3_005528b0` `0x005528b0` x2 site(s) (instruction-flow).
- Caller `CVBufTexture__DrawSpriteEx` `0x00555be0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave854 static read-back: CFastVB immediate non-indexed triangle-strip renderer. Unlocks the CVBuffer at this+0x00, binds the vertex stream through the Direct3D device vtable +0x190 using stride 0x1c, sets raw vertex shader/FVF handle 0x144, then calls the device draw entry at vtable +0x144 with primitive type 5, start vertex this+0x06, and primitive count this+0x08-2. Unlike CFastVB__Render, this path does not bind the shared CIBuffer DAT_00897a90 and is reached by CConsole__RenderLoadingScreen, CRenderQueue__RenderAll, and CVBufTexture__DrawSpriteEx after CFastVB__Lock/LockAligned. Resets this+0x06 to 0xffff and this+0x08 to 0. Static retail Ghidra evidence only; exact CFastVB/global layout, D3D vtable identity, runtime render output, source identity, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `f992565bb72e0523b9981269ae9cc3f917e5a3efe61729e2a08f3ca60333a0f7`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 3 caller record(s), 2 callee record(s), and 0 string-ref record(s). Manifest subfamily: `runtime_lifecycle_lock_update`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 5; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `a06fb458f43aa154e95f68c8b5aa880da030f9d89a80597bac3f76c08858c1f5`, and packet decompile SHA-256 `f992565bb72e0523b9981269ae9cc3f917e5a3efe61729e2a08f3ca60333a0f7`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `0051a6a0:0051a6ff;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source-first authorities joined before packets: `reverse-engineering/source-crosswalk/crosswalk.tsv`, `reverse-engineering/source-crosswalk/expansion/w1-save-session-input-frontend/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w2-thing-battleengine-camera/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w3-audio-music/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w4-memory-container-archive/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w5-engine-render-platform-shell/RECEIPT.json`.
- Selected source crosswalk rows: none for this VA; this is an explicit packet-first row, not an assertion that no source analog exists.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, all source-authority joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global/container record.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, topology/codec policy, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
