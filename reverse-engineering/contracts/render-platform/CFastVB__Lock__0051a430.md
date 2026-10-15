# CFastVB__Lock

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__Lock` at `0x0051a430` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0051a430`

## Identity
- Body `[0x0051a430,0x0051a501]`, 210 bytes, 79 closure instructions. Raw pristine-body SHA-256 `b6a0db4589943daa6e5eaba2ce1398f478b0e0b2601ce8befc477f3484c110f1`; closure range SHA-256 `3cb4b36f80214cf38e3be42bcba73b10eb1f76cd02c66e6e9a7739580b1c26a6`; packet range-plus-bytes SHA-256 `2bf16a8dc3859f89da1f2b3e44e64b4853a9b55a512e3e2d28dd91396a54fc83`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__Lock`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `f96d074b76cf0b83832a181d851d9e94a04be019b5132c9badcd6fe0b9fdefd6` and decompile SHA-256 `87735f6a14e82ecda01f3ae4edf3af98c104e70b1122e3c98cc18d82f40fd0cf` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `ushort __thiscall CFastVB__Lock(void * this, void * * out_vertex_data, int vertex_count)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
ushort __thiscall CFastVB__Lock(void * this, void * * out_vertex_data, int vertex_count)
```
- Packet-declared parameter list: `void * this, void * * out_vertex_data, int vertex_count`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `ushort`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CVBuffer__Unlock` `0x005001e0` x1 site(s) (STATIC_DIRECT).
- Callee `CVBuffer__LockRange` `0x00500390` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__LockAligned` `0x0051a380` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__Render` `0x0051a510` x2 site(s) (STATIC_DIRECT).
- Caller `CVBufTexture__DrawSpriteEx` `0x00555be0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave563 signature/comment hardening: RET 0x8 plus callers prove out_vertex_data and vertex_count stack arguments. The retail body returns 0xffff without a CVBuffer, delegates to CFastVB__LockAligned when this+0x06 is 0xffff, flushes through CFastVB__Render and resets this+0x04/0x06/0x08 on overflow, otherwise unlocks the active CVBuffer and uses no-overwrite flag 0x1800 before calling CVBuffer__LockRange over 0x1c-byte vertices. Static retail/source evidence only; exact batch lifetime, CFastVB/CVBuffer layout, D3D lock behavior, BEA launch, patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `87735f6a14e82ecda01f3ae4edf3af98c104e70b1122e3c98cc18d82f40fd0cf`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 4 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 21; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `f96d074b76cf0b83832a181d851d9e94a04be019b5132c9badcd6fe0b9fdefd6`, and packet decompile SHA-256 `87735f6a14e82ecda01f3ae4edf3af98c104e70b1122e3c98cc18d82f40fd0cf`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `0051a430:0051a501;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
