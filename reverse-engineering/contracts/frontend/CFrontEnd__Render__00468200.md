# CFrontEnd__Render

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__Render` at `0x00468200`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00468200`

## Identity
- Body `[0x00468200,0x004684c5]`, 710 bytes, 195 closure instructions. Raw pristine-body SHA-256 `3a396dbbe16747094675a3ce8a8436a41ef8b3c022ba32f5261e95d9d0ed9244`; closure range SHA-256 `edf598a522fee8ac8898820e3d618a5f7972efbe0bd3103434e3305d770b4099`; packet range-plus-bytes SHA-256 `ab2b05f19b989616ecea74abb3f4cb7f728b97b6e827aa8b19d377b2112fd33c`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__Render` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__Render`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `int __fastcall CFrontEnd__Render(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __fastcall CFrontEnd__Render(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00675688`, `DAT_0089ce54`, `DAT_0089d758`, `DAT_008a9aac`, `DAT_009c3df0`, `DAT_009c65c0`, `DAT_009c68dc`, `_DAT_009c68d4`, `_DAT_009c68d8`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGame__SetGlobalSelectionSnapshot` `0x00441b10` ×1 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__RenderAndProcessModalPanel` `0x0044d6f0` ×1 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__SetSlotMode4or5` `0x00513af0` ×1 site(s) (STATIC_DIRECT).
- Callee `RenderState_Set` `0x00513bc0` ×3 site(s) (STATIC_DIRECT).
- Callee `PlatformInput__ConsumeKeyOnce` `0x00515980` ×1 site(s) (STATIC_DIRECT).
- Callee `PLATFORM__GetSysTimeFloat` `0x005159e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__DrawLocalCoopControllerPrompt` `0x00527990` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXFrontEnd__RenderStart` `0x00540f70` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXFrontEnd__VFunc_07_00540fb0` `0x00540fb0` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__PrintStats` `0x00549290` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__ApplyPendingRenderState` `0x00550d50` ×1 site(s) (STATIC_DIRECT).
- Caller `CFrontEnd__Run` `0x004684d0` ×2 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/FrontEnd.cpp` lines `1259-1360` defines `CFrontEnd::Render` as `BOOL	CFrontEnd::Render(BOOL forcerender)`; exact extracted source-body SHA-256 `991baa878d9bc6feffda9bf2f5f023025b6c0761970a5f3286878d77b3ab59d5`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=8, switch=0, for=0, while=0; named call tokens `Apply`, `CPS2Texture::UpdateTextureLODs`, `GetDrawDebugStuff`, `GetSysTimeFloat`, `PrintStats`, `RenderAfter`, `RenderEnd`, `RenderPreCommon`, `RenderStart`, `SRS`, `STS`, `SetVirtualScreenEnabled`, `SetVirtualScreenXSize`, `SetVirtualScreenYSize`, `float`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Frontend render pass (begin/end scene, active/transitional pages, overlays). ECX receiver; terminator `RET 0x4` proves one stack dword after this. Catalog `int __fastcall ...(void * this)` is wrong — CFrontEnd__Run sites PUSH 0 / MOV ECX / CALL and the callee cleans one stack dword; shape is MSVC `__thiscall` + one stack arg (do not invent a typed formal from a post-push ESP offset alone). Return status comes from the begin-scene path (EBX). Tags empty (needs_tags remains out of this signature-comment lane). Static retail evidence only; exact source binding, runtime render UX, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `494a3a29024fbd1784d3421615498f62c47f4b02be0c3da77b4ea901c765af12`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 11 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 25; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00468200.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `494a3a29024fbd1784d3421615498f62c47f4b02be0c3da77b4ea901c765af12`.
- Digest derivation: closure SHA-256 hashes canonical range text `00468200:004684c5;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/FrontEnd.cpp` `CFrontEnd::Render` line 1259 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Render.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
