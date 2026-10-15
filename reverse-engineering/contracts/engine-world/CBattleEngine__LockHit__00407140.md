# CBattleEngine__LockHit

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__LockHit` at `0x00407140`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00407140`

## Identity
- Body `[0x00407140,0x004071a8]`, 105 bytes, 41 closure instructions. Raw pristine-body SHA-256 `eb6914393a80a1a0d314385955c4188946ad9a2115fe5d49da6224c7dd80605c`; closure range SHA-256 `ff21462a6bd79d17686fd8dc3528489dea88723be401341ddb3b0287bc5f5c42`; packet range-plus-bytes SHA-256 `adb7653c94b422605a330a846bf622fdf1f79f9af24a22734cffd63e98ad9b55`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__LockHit` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__LockHit`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C2_BOUNDED_RUNTIME` / closure class `PREEXISTING_GEN19_C1_OR_C2` / packet confidence `BOUNDED_CONTRACT`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CBattleEngine__LockHit(void * this, void * inUnit)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__LockHit(void * this, void * inUnit)
```
- Packet-declared parameter list: `void * this, void * inUnit`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_009c3df0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGenericActiveReader__dtor` `0x0044b1d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__Remove` `0x004e5bd0` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Free` `0x00549220` ×1 site(s) (STATIC_DIRECT).
- Caller `VFuncSlot_02_004d8dc0` `0x004d8dc0` ×1 site(s) (instruction-flow).
- Caller `VFuncSlot_66_004d8e40` `0x004d8e40` ×3 site(s) (instruction-flow).
- Caller `CRound__SetTargetReaderIfAllowed` `0x004daab0` ×1 site(s) (instruction-flow).
- Caller `CRound__RemoveActiveReaderById` `0x004dab50` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/BattleEngine.cpp` lines `882-897` defines `CBattleEngine::LockHit` as `void	CBattleEngine::LockHit( CThing		*inUnit)`; exact extracted source-body SHA-256 `97294eda1464d6c6a216ee26814984b5b5ea249969a401cc52e5e80c6cd652f7`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=2, switch=0, for=1, while=0; named call tokens `First`, `Next`, `Remove`, `ToRead`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Retail/source identity: 0x00407140 matches CBattleEngine::LockHit (BattleEngine.cpp:882-897): for a non-null target it scans mFiredLocks, removes the matching CLockInfo, destroys/frees it, and returns; RET 0x4 proves one 4-byte explicit argument. Level 521 raw boundary rows observed 24 calls with immediately paired entries from two exact call sites. The independently refuted exact-window write plate proves one supplied target's sole fired-lock node was removed and the container became empty; global free-list head bytes, later payload destruction, full return, other paths, and rebuild parity remain open.”
- The displayed decompile is non-empty and SHA-256 `57029ed49908c1aa32da98d922aea11b18ef078687f415e05747226a66ea3d00`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 4 caller record(s), 3 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `batch-1`; question `contract-round-impact`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-2`; question `contract-round-impact`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-3`; question `contract-round-impact`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-4`; question `contract-round-impact`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-5`; question `contract-round-impact`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-6`; question `contract-round-impact`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 11 BEA.exe coverage bitmaps`.
- Session `batch-7`; question `contract-round-impact`; value: corroborated in 2/7 coverage sessions; evidence `level521-native-20260802-0018-take1, level521-native-20260802-0018-take2`.
- Session `batch-8`; question `contract-round-impact`; value: corroborated in 1/4 coverage sessions; evidence `level521-native-20260802-0018-take4`.
- Session `batch-9`; question `contract-round-impact`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 3 BEA.exe coverage bitmaps`.
- Session `batch-10`; question `contract-round-impact`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `d2ac6ace069c4ff409cd9aaec49022fb08589f5637367a823baa4b65053cc9ef`, row 3; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00407140.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `57029ed49908c1aa32da98d922aea11b18ef078687f415e05747226a66ea3d00`.
- Digest derivation: closure SHA-256 hashes canonical range text `00407140:004071a8;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `OPEN_EXECUTED` and confidence `BOUNDED_CONTRACT`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::LockHit` line 882 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__LockHit.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
