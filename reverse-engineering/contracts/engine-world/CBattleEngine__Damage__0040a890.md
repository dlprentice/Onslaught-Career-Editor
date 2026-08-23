# CBattleEngine__Damage

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__Damage` at `0x0040a890`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040a890`

## Identity
- Body `[0x0040a890,0x0040ac24]`, 917 bytes, 233 closure instructions. Raw pristine-body SHA-256 `224c0577b539bbf0d6fa118a6355502f9aead3bc588e59ae3bf08bdf3cd1ff91`; closure range SHA-256 `7b3b41b512c777438736116c9c5627a3b832ad47e5f71458a265e145cd99a127`; packet range-plus-bytes SHA-256 `e91bfaaa4ed94e43781fc7b7fb3d91f6cdd92795e223ee7b5e78239879fa6507`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__Damage` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__Damage`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C2_BOUNDED_RUNTIME` / closure class `PREEXISTING_GEN19_C1_OR_C2` / packet confidence `BOUNDED_CONTRACT`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CBattleEngine__Damage(void * this, float amount, void * inByThis, int inDamageShields, int meshPartNo)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__Damage(void * this, float amount, void * inByThis, int inDamageShields, int meshPartNo)
```
- Packet-declared parameter list: `void * this, float amount, void * inByThis, int inDamageShields, int meshPartNo`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`, `DAT_009c3df0`, `s_C__dev_ONSLAUGHT2_BattleEngine_c_006230bc`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CBattleEngine__RandomizeOffsets4B8_4C0` `0x00407940` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__AddToHead` `0x004e5a80` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/BattleEngine.cpp` lines `2127-2240` defines `CBattleEngine::Damage` as `void	CBattleEngine::Damage( float		inAmount, CThing		*inByThis, BOOL		inDamageShields, int			mesh_part_no)`; exact extracted source-body SHA-256 `8a90387ebacaade522347c701972a63a724a7c064f85cecdd16cd11373778697`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=20, switch=0, for=0, while=0; named call tokens `AddDamageFlash`, `AddShockShake`, `GetAugWeapon`, `GetPos`, `GetTime`, `IncStat`, `StartDieProcess`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Retail/source identity and bounded runtime contract: 0x0040A890 matches CBattleEngine::Damage (BattleEngine.h:133; BattleEngine.cpp:2127 onward). The 917-byte retail body and RET 0x10 prove four 4-byte explicit arguments. Source prototype: void Damage(float amount, CThing *inByThis, BOOL inDamageShields, int mesh_part_no); Ghidra records BOOL as int to preserve its 32-bit ABI and keeps object types opaque. Generation 12 witnessed one replicated invocation writing, in order, mShields +0x100, mAugValue +0x168, mLife +0x154, mLastDamageTime +0x174, and mEnergy +0xFC, plus two zero-write controls. Five nontrivial observation gaps and nine continuity breaks forbid a complete write-set or universal-path claim. Rebuild state is PARTIAL_CONTRACT, not REBUILD_READY; negative damage, lethal/StartDie, source-flash, branch, return-context, and unobserved-path behavior remain open. Gen12 READY 9d2b903d451c; proof ffb2e0b8692d.”
- The displayed decompile is non-empty and SHA-256 `1f4ba17d86ab3c6ebb38f8efc9a3eb45d74906b07c9497a79edd133390fc2d94`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 3 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `batch-1`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-2`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-3`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-4`; question `contract-damage`; value: corroborated in 1/10 coverage sessions; evidence `level-opening-3m-v1-level731`.
- Session `batch-5`; question `contract-damage`; value: corroborated in 2/10 coverage sessions; evidence `level-opening-3m-v1-level732, level-opening-3m-v1-level854`.
- Session `batch-6`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 11 BEA.exe coverage bitmaps`.
- Session `batch-7`; question `contract-damage`; value: corroborated in 1/7 coverage sessions; evidence `level521-native-20260802-0018-take2`.
- Session `batch-8`; question `contract-damage`; value: corroborated in 1/4 coverage sessions; evidence `level521-native-20260802-0018-take4`.
- Session `batch-9`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 3 BEA.exe coverage bitmaps`.
- Session `batch-10`; question `contract-damage`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 8; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040a890.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `1f4ba17d86ab3c6ebb38f8efc9a3eb45d74906b07c9497a79edd133390fc2d94`.
- Digest derivation: closure SHA-256 hashes canonical range text `0040a890:0040ac24;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `OPEN_AFTER_SURVIVED` and confidence `BOUNDED_CONTRACT`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x006230bc` length 35 SHA-256 `0469e415183a714b133ceb95e28409293389b49573750318193b95dfad3a1558` value “C:\\dev\\ONSLAUGHT2\\BattleEngine.cpp”.
- Source crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::Damage` line 2127 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__Damage.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
