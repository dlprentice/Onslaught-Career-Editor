# CFrontEnd__RenderPreCommonFade

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__RenderPreCommonFade` at `0x004679e0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004679e0`

## Identity
- Body `[0x004679e0,0x00467adb]`, 252 bytes, 75 closure instructions. Raw pristine-body SHA-256 `7cfc211fb38ffcfa53d5abd24cdfe1674fb3c2698d9cfaadc3e76924ed09fb28`; closure range SHA-256 `80e381215e6befca518a0d407f69186bad15440b8e68c1321fb2594215b8c08d`; packet range-plus-bytes SHA-256 `834338decf8c457248da98cd01a63b1abe64a6b8b292efcd07cae32911828700`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__RenderPreCommonFade` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__RenderPreCommonFade`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__stdcall` for `void __stdcall CFrontEnd__RenderPreCommonFade(float transition, uint argb, int destination_page)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __stdcall CFrontEnd__RenderPreCommonFade(float transition, uint argb, int destination_page)
```
- Packet-declared parameter list: `float transition, uint argb, int destination_page`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CFrontEnd__RenderVideoQuadScaledToWindow` `0x00452ce0` ×1 site(s) (STATIC_DIRECT).
- Caller `CFEPDebriefing__RenderPreCommon` `0x00456d40` ×1 site(s) (instruction-flow).
- Caller `CFEPCredits__RenderPreCommon` `0x0051a880` ×1 site(s) (instruction-flow).
- Caller `CFEPLanguageTest__RenderPreCommon` `0x0051ae50` ×1 site(s) (instruction-flow).
- Caller `CFEPOptions__RenderPreCommon` `0x0051f6d0` ×1 site(s) (instruction-flow).
- Caller `CFEPScreenPos__RenderPreCommon` `0x0051fb60` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: the current source crosswalk has no pinned Stuart owner for this VA.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave467 correction: Frontend/page pre-common fade helper that clamps transition-derived alpha, combines it with an incoming ARGB color, and renders a full-window/video quad. Static retail-binary evidence only; exact page ownership, color-channel intent, runtime transition visuals, source identity, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `a1922056f316eccb78855669f1bd6bfec7bbcbcfe67c8c9aa160a04010a615b6`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 5 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 20; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x004679e0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `a1922056f316eccb78855669f1bd6bfec7bbcbcfe67c8c9aa160a04010a615b6`.
- Digest derivation: closure SHA-256 hashes canonical range text `004679e0:00467adb;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
