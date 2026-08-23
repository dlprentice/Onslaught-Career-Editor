# CBattleEngineWalkerPart_T3_004145f0

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngineWalkerPart_T3_004145f0` at `0x004145f0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004145f0`

## Identity
- Body `[0x004145f0,0x00414605]`, 22 bytes, 8 closure instructions. Raw pristine-body SHA-256 `2f1b7220588b07e4bf8773d559532154fba97fc66072e7e8c611976f198b70ae`; closure range SHA-256 `76ba9ef242fefe4c886669821981e247d5f96f55308d3a8691ebe7bc16f48837`; packet range-plus-bytes SHA-256 `32b31ef807c6a62a748b5a1877219255210de53a955ab82c125922b4c5aa8561`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngineWalkerPart_T3_004145f0` comes from the current 8,329-row 2026-08-17 name table and EVIDENCE-REGISTER projection. The dated 2026-08-11 closure label `CBattleEngineWalkerPart__GetCurrentWeaponZoomMode` is superseded name metadata and is not current identity authority. Packet label matches canonical tracked name `CBattleEngineWalkerPart_T3_004145f0`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `unknown`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CBattleEngineWalkerPart_T3_004145f0(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CBattleEngineWalkerPart_T3_004145f0(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030` ×1 site(s) (STATIC_DIRECT).
- Caller `CBattleEngine__ChangeWeapon` `0x00409f70` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “WalkerPart accessor: GetCurrentWeapon then returns *(weapon_data +0x4) where weapon_data is entry +0xa4 — used by ChangeWeapon / BattleEngine HUD string compare as a name-pointer-shaped field, not a zoom-mode enum. Rename propose-only toward CBattleEngineWalkerPart__GetCurrentWeaponNameField04 (or equivalent name-field adapter); do not call it zoom mode unless new evidence appears. Signature char* vs int remains rename/signature-queue outside this comment-lane apply. Static source/decompile/xref evidence only; exact CWeaponData field name, runtime zoom behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `e26a6d718d3b6c18bc4afe56de4e55e872844f47b441fa7d4b9c75993efe1deb`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, corrected cohort-5 immutable manifest SHA-256 `a501cc526ae9f6caed0e4e42581ac21cabd87aa03a3eb4266432bdb7fd1ed7a8`, row 25; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. Review card `t_b435bd68` preserves the superseded manifest and exact RED/correction receipt; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004145f0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `e26a6d718d3b6c18bc4afe56de4e55e872844f47b441fa7d4b9c75993efe1deb`.
- Digest derivation: closure SHA-256 hashes canonical range text `004145f0:00414605;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `unknown` and confidence `unknown`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact current T3 identity, contiguous pristine bytes, digest derivations, packet signature, and structured edge inventory are reconciled; the intentionally owner-neutral symbol does not revive the withdrawn ZoomMode meaning, and field/runtime semantics remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
