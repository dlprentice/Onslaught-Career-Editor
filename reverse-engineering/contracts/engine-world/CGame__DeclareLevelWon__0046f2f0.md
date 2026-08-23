# CGame__DeclareLevelWon

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CGame__DeclareLevelWon` at `0x0046f2f0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/game.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0046f2f0`

## Identity
- Body `[0x0046f2f0,0x0046f35b]`, 108 bytes, 40 closure instructions. Raw pristine-body SHA-256 `2bf6c8ff4f0fc1d58ca2dbd1188c01c26dfeb85f5895fd06769d0c6b36a646f6`; closure range SHA-256 `0b0f39b5fbbe38d011353a059498ca1e7b4d91c33acf3aa8f6bfe0d911051883`; packet range-plus-bytes SHA-256 `d702c610f5cc15560c440a192923aac5ac965c04c0383f3d24a2ec445972ce0f`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CGame__DeclareLevelWon` comes from the current closure/register row. Packet label matches canonical tracked name `CGame__DeclareLevelWon`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CGame__DeclareLevelWon(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CGame__DeclareLevelWon(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CController__SetVibration` `0x0042e750` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__Pause` `0x0046fb00` ×2 site(s) (STATIC_DIRECT).
- Caller `IScript__LevelWon` `0x005381e0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/game.cpp` lines `2384-2412` defines `CGame::DeclareLevelWon` as `void CGame::DeclareLevelWon()`; exact extracted source-body SHA-256 `9a9b7007eb03664d5f5181195535ea598eef19bf23f1851fab95e45f6640fb27`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=4, switch=0, for=1, while=0; named call tokens `Pause`, `SetVibration`.
- Source-to-retail status: tracked `SOURCE_EXACT` class supplies named identity plus tracked source-body-agreement evidence. The packet/pristine checks below independently pin the retail target; this factory does not silently widen the tracked exactness beyond that evidence row.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “CGame level-won declaration. ECX receiver; both exits plain `RET` (c3) — no stack args. Declared `__fastcall` → prefer `__thiscall (void * this)`. When this+0x28<=3: clear controller vibration, set state 5, special-case countdown for levels 0x2e5/0x2e6, then Pause. Tags empty (no invent-add). Static retail evidence only; exact win-state semantics, runtime UX, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `0c49ba77c4cfa7e8c4bd42b26677e9f106541ea8b324473dee8b97a6a3030820`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `batch-1`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-2`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-3`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-4`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-5`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-6`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 11 BEA.exe coverage bitmaps`.
- Session `batch-7`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 7 BEA.exe coverage bitmaps`.
- Session `batch-8`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 4 BEA.exe coverage bitmaps`.
- Session `batch-9`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 3 BEA.exe coverage bitmaps`.
- Session `batch-10`; question `contract-level-flow`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `d2ac6ace069c4ff409cd9aaec49022fb08589f5637367a823baa4b65053cc9ef`, row 21; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0046f2f0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `0c49ba77c4cfa7e8c4bd42b26677e9f106541ea8b324473dee8b97a6a3030820`.
- Digest derivation: closure SHA-256 hashes canonical range text `0046f2f0:0046f35b;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/game.cpp` `CGame::DeclareLevelWon` line 2384 (`SOURCE_EXACT`), evidence `reverse-engineering/binary-analysis/functions/game.cpp/CGame__DeclareLevelWon.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
