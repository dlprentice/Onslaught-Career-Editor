# CFrontEnd__Process

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__Process` at `0x00466ba0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00466ba0`

## Identity
- Body `[0x00466ba0,0x00466ddd]`, 574 bytes, 149 closure instructions. Raw pristine-body SHA-256 `561bd54e88e164dd257de3a949c14cabf4417d58f1684bc0f1b30208adc8ec64`; closure range SHA-256 `3ac9c0ea2acdc032bca7e3a01aad150ae59872624b5e0184eb1b9ab7c2ec6fe6`; packet range-plus-bytes SHA-256 `2041db8a83b212f0ede20fea146d8991d6c95fb551c74ad4e31d53ebc442434c`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__Process` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__Process`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CFrontEnd__Process(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CFrontEnd__Process(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00675688`, `DAT_00855bb0`, `DAT_00889a48`, `DAT_00896988`, `DAT_0089be50`, `DAT_0089be58`, `DAT_0089be5c`, `DAT_0089be64`, `DAT_0089d91c`, `DAT_009c63e8`, `_DAT_00629b0c`, `_DAT_00679af8`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CController__InactivityMeansQuitGame` `0x0042d810` ×1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__Update` `0x0044b5c0` ×1 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__UpdateFadeStateMachineAlpha` `0x0044d560` ×1 site(s) (STATIC_DIRECT).
- Callee `CMusic__UpdateStatus` `0x004bb530` ×1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__Update` `0x004cb210` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__UpdateStatus` `0x004e1b20` ×1 site(s) (STATIC_DIRECT).
- Callee `PlatformInput__ClearTransientKeyStateTable` `0x00512470` ×1 site(s) (STATIC_DIRECT).
- Callee `PLATFORM__Process` `0x00515880` ×1 site(s) (STATIC_DIRECT).
- Callee `PLATFORM__GetSysTimeFloat` `0x005159e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CFEPOptions__GetState` `0x0051f370` ×1 site(s) (STATIC_DIRECT).
- Callee `Input__ResetMouseTransientState` `0x00523db0` ×1 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__AdvanceStateAndRelinquishControl` `0x00527c50` ×2 site(s) (STATIC_DIRECT).
- Callee `CDXFrontEndVideo__Update` `0x00541d30` ×1 site(s) (STATIC_DIRECT).
- Caller `CFrontEnd__Run` `0x004684d0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/FrontEnd.cpp` lines `595-712` defines `CFrontEnd::Process` as `void	CFrontEnd::Process()`; exact extracted source-body SHA-256 `52b515080f6f1dca57e510146f0ba64b7692828c149eff0cf4632de19473acad`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=16, switch=0, for=2, while=0; named call tokens `ActiveNotification`, `CController::InactivityMeansQuitGame`, `DeActiveNotification`, `Flush`, `GetProfileEnabled`, `GetState`, `HasTimeoutExpired`, `KeyOnce`, `NextFrame`, `ReceiveButtonAction`, `SetProfileEnabled`, `TRACE`, `Update`, `UpdateStatus`, `inactivity`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “FrontEnd.cpp CFrontEnd::Process(): platform/system processing, EVENT_MANAGER.Update(), particle/sound/music status updates, controller flush, transition handling, per-page Process(state), and message-box processing.”
- The displayed decompile is non-empty and SHA-256 `85905a5e49e8e5067334d1fa51a490014c653fa338c20a856c5f3c131de6c0ae`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 13 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 14; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00466ba0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `85905a5e49e8e5067334d1fa51a490014c653fa338c20a856c5f3c131de6c0ae`.
- Digest derivation: closure SHA-256 hashes canonical range text `00466ba0:00466ddd;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/FrontEnd.cpp` `CFrontEnd::Process` line 595 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Process.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
