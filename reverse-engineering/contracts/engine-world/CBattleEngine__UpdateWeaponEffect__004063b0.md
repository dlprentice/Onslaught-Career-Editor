# CBattleEngine__UpdateWeaponEffect

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__UpdateWeaponEffect` at `0x004063b0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004063b0`

## Identity
- Body `[0x004063b0,0x00406458]`, 169 bytes, 53 closure instructions. Raw pristine-body SHA-256 `fa65f74625e618d5c72064642a20c848ae261835f5297c076a81e34a6674f575`; closure range SHA-256 `4d2cee9bf269ef654cef63d4b1405ab6e53e1782811858cfe80d03ec01336953`; packet range-plus-bytes SHA-256 `cd21dda222b5296658d2728fe853d414796b0db7e6dddc99bd8292ba7c3cdd4f`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__UpdateWeaponEffect` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__UpdateWeaponEffect`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CBattleEngine__UpdateWeaponEffect(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CBattleEngine__UpdateWeaponEffect(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_009c3df0`, `s_C__dev_ONSLAUGHT2_BattleEngine_c_006230bc`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CDXMemoryManager__Alloc` `0x005490e0` ×1 site(s) (STATIC_DIRECT).
- Caller `CBattleEngine__HandleEvent` `0x0040c180` ×2 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: the current source crosswalk has no pinned Stuart owner for this VA.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave1188 static read-back: CBattleEngine weapon-effect helper called by CBattleEngine__HandleEvent at 0x0040c1db and 0x0040c27f. The body samples virtual getters at vtable offsets +0x40/+0xc0, allocates a 0x20 CLine-like effect object from BattleEngine.cpp line 0x1f5, writes squared range and timing/scalar fields, and submits the object through the nested manager at this+0x38 vfunc +0x24. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact effect-object layout, exact source-body identity, runtime weapon/effect behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.”
- The displayed decompile is non-empty and SHA-256 `8659268e6493ecb96900c72390a4bda61eb4e804c926d52b44f547ed11e5f226`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 1 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take4`; question `corpus-combat-only`; value: combat-exclusive; 166 covered bytes; evidence `name=CBattleEngine__UpdateWeaponEffect`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `d2ac6ace069c4ff409cd9aaec49022fb08589f5637367a823baa4b65053cc9ef`, row 2; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004063b0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `8659268e6493ecb96900c72390a4bda61eb4e804c926d52b44f547ed11e5f226`.
- Digest derivation: closure SHA-256 hashes canonical range text `004063b0:00406458;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x006230bc` length 35 SHA-256 `0469e415183a714b133ceb95e28409293389b49573750318193b95dfad3a1558` value “C:\\dev\\ONSLAUGHT2\\BattleEngine.cpp”.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
