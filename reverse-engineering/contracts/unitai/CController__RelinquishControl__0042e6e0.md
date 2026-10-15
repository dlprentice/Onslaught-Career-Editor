# CController__RelinquishControl

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CController__RelinquishControl` at `0x0042e6e0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/Controller.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0042e6e0`

## Identity
- Body `[0x0042e6e0,0x0042e746]`, 103 bytes, 38 closure instructions. Raw pristine-body SHA-256 `1f4db7e747471f06cfe38ddfa3dc14bb6f2481a57fbc31227f189934bb533e19`; closure range SHA-256 `ea9a01077e6f28cbe5db9dc217b9cb965ade7cb132871e5dda12d53831644e74`; packet range-plus-bytes SHA-256 `362ef516176a9805cdcb0af74cae405423ba93b810b410aa24bd7d24145cf4cc`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CController__RelinquishControl` comes from the current closure/register row. Packet label matches canonical tracked name `CController__RelinquishControl`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CController__RelinquishControl(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CController__RelinquishControl(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0066f580`, `DAT_009c3df0`, `s_FATAL_ERROR__Controller_stack_em_00625610`, `s_FATAL_ERROR__stack_empty_to_call_00625654`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CConsole__Printf` `0x00441740` ×2 site(s) (STATIC_DIRECT).
- Callee `CGenericActiveReader__dtor` `0x0044b1d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__Remove` `0x004e5bd0` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Free` `0x00549220` ×1 site(s) (STATIC_DIRECT).
- Caller `CWaitForStart__VFunc_3_0046dbe0` `0x0046dbe0` ×1 site(s) (instruction-flow).
- Caller `CGame__Update` `0x0046e910` ×3 site(s) (instruction-flow).
- Caller `CGame__DeclarePlayerDead` `0x0046f550` ×1 site(s) (instruction-flow).
- Caller `CGame__ReceiveButtonAction` `0x0046f7e0` ×1 site(s) (instruction-flow).
- Caller `CGameInterface__HandleMenuSelection` `0x00472b40` ×1 site(s) (instruction-flow).
- Caller `CGameInterface__VFunc_03_HandleMenuControlInput` `0x00472d50` ×1 site(s) (instruction-flow).
- Caller `GameControllers__RelinquishControlForTarget` `0x004cdd70` ×1 site(s) (instruction-flow).
- Caller `CPauseMenu__ResumeGameAndPersistOptions` `0x004d06e0` ×1 site(s) (instruction-flow).
- Caller `CPauseMenu__VFunc_0_004d0e50` `0x004d0e50` ×2 site(s) (instruction-flow).
- Caller `CFrontEnd__AdvanceStateAndRelinquishControl` `0x00527c50` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/Controller.cpp:517-538` defines `CController::RelinquishControl` as `void CController::RelinquishControl()`; exact extracted source-body SHA-256 `a2312cd4149be75867d1ecdb43a1365d99c329cd42eae1724bbaecc94d574467`.
- Source algorithm skeleton: the source reads `mToControlStack.First()`, removes and deletes the first reader when present, logs a fatal and returns when initially empty, then reads the first entry again and logs/returns if the resulting stack is empty. Mechanical control counts are if=2, switch=0, for=0, while=0; named call tokens are `First`, `Remove`, and `AddMessage`.
- Source-to-retail status: tracked `SOURCE_EXACT` supplies named identity plus source-body-agreement evidence. The retail packet independently shows the remove/destructor/free chain and the two fatal-message arms; concrete collection layout, allocator behavior, and runtime control handoff remain bounded to retail evidence.
- Source-vs-retail delta/unknown boundary: no source-visible branch divergence is claimed by the current exact crosswalk, but this factory did not freshly prove every compiler lowering or field offset; those instruction-level details and runtime causality remain open falsifiers.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “CController::RelinquishControl. ECX receiver; plain `RET` (c3) — no stack args. Catalog `__fastcall` vs peer `__thiscall` is spelling debt only. Pops top CActiveReader from mToControlStack (CSPtrSet__Remove + CGenericActiveReader dtor/Free) and fatals if stack was/becomes empty. Static retail evidence only; concrete reader layout, runtime control handoff, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `d0dc1d1707e1f5cdd180901fa7cc809f78046e10ddcd2927535e5b821e9e3598`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 10 caller record(s), 4 callee record(s), and 2 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take4, level521-native-20260802-0018-take2, level521-native-20260802-0018-take1`; question `corpus-combat-only`; value: combat-exclusive; 189 covered bytes; evidence `name=CController__RelinquishControl`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 1; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0042e6e0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `d0dc1d1707e1f5cdd180901fa7cc809f78046e10ddcd2927535e5b821e9e3598`.
- Digest derivation: closure SHA-256 hashes canonical range text `0042e6e0:0042e746;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00625610` length 67 SHA-256 `81d30725aece601e536b1dcc98747421b5b2e81b756630a1d11c56b1c6e8d760` value `FATAL ERROR: Controller stack empty to call to 'RelinquishControl'`.
- Packet string ref `0x00625654` length 56 SHA-256 `c2d33351b7bcf62c367899d8c75614f27aeceb540e7364416a1c3c9f56d9b05a` value `FATAL ERROR: stack empty to call to 'RelinquishControl'`.
- Source crosswalk: `references/Onslaught/Controller.cpp` `CController::RelinquishControl` line 517 (`SOURCE_EXACT`), evidence `reverse-engineering/binary-analysis/controller-shared-semantics-2026-08-11.tsv`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
