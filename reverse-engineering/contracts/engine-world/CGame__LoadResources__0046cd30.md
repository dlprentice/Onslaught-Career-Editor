# CGame__LoadResources

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CGame__LoadResources` at `0x0046cd30`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/game.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0046cd30`

## Identity
- Body `[0x0046cd30,0x0046cde3]`, 180 bytes, 55 closure instructions. Raw pristine-body SHA-256 `ace53e77e785bd5265ca6d88854991c82c48e9b8e35c2f2c2cd197d85b07468b`; closure range SHA-256 `ac01793ffc145c7dad633288913813678aca1a1fd60188e24e7da7a2e8690292`; packet range-plus-bytes SHA-256 `6738744b8914884996677b7d2eb28c77c09cff06510476b45bcb66b78a042f17`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CGame__LoadResources` comes from the current closure/register row. Packet label matches canonical tracked name `CGame__LoadResources`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__stdcall` for `int __stdcall CGame__LoadResources(int aLevel, int inLoadedSounds)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __stdcall CGame__LoadResources(int aLevel, int inLoadedSounds)
```
- Packet-declared parameter list: `int aLevel, int inLoadedSounds`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00662dd4`, `DAT_00663498`, `DAT_0082b400`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CConsole__SetLoading` `0x0042bbc0` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__RenderLoadingScreen` `0x0042c810` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__SetLoadingRange` `0x0042cf40` ×2 site(s) (STATIC_DIRECT).
- Callee `CMesh__StatusLoadingMeshResources` `0x004a53f0` ×1 site(s) (STATIC_DIRECT).
- Callee `CParticleSet__LoadParticleSetFile` `0x004cda60` ×1 site(s) (STATIC_DIRECT).
- Callee `CResourceAccumulator__ReadResourceFile` `0x004d7200` ×1 site(s) (STATIC_DIRECT).
- Callee `CTexture__InitDefaultTextureResourcesAndStatus` `0x004f29c0` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorldPhysicsManager__ResolveLoadedDefinitionReferences` `0x00510520` ×1 site(s) (STATIC_DIRECT).
- Caller `CGame__RunLevel` `0x0046e240` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/game.cpp` lines `624-657` defines `CGame::LoadResources` as `BOOL CGame::LoadResources( SINT		aLevel, BOOL		inLoadedSounds)`; exact extracted source-body SHA-256 `9680bee944097ccbf0f914067f703d5bd6ab2d9a84ae15e085ccaccc61c01b5f`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=4, switch=0, for=0, while=0; named call tokens `CMESH::LoadLevelResources`, `CResourceAccumulator::ReadResources`, `CTEXTURE::LoadLevelResources`, `LoadAllFromDisk`, `RenderLoadingScreen`, `SetLoading`, `SetLoadingRange`, `UPhysicsManager::InitialiseEffects`.
- Source-to-retail status: tracked `SOURCE_EXACT` class supplies named identity plus tracked source-body-agreement evidence. The packet/pristine checks below independently pin the retail target; this factory does not silently widen the tracked exactness beyond that evidence row.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source-aligned mapping to CGame::LoadResources(SINT,BOOL). Loads level resource bundles and level assets (texture/mesh resources + particle set), with loading-range split depending on whether sounds were reloaded.”
- The displayed decompile is non-empty and SHA-256 `209dac3d0dc40d1661ae7091b77581c480c4d38d7e7b485ec34ce7e8283ba67b`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 8 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 15; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x0046cd30.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `209dac3d0dc40d1661ae7091b77581c480c4d38d7e7b485ec34ce7e8283ba67b`.
- Digest derivation: closure SHA-256 hashes canonical range text `0046cd30:0046cde3;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/game.cpp` `CGame::LoadResources` line 624 (`SOURCE_EXACT`), evidence `reverse-engineering/binary-analysis/functions/game.cpp/CGame__LoadResources.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
