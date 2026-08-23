# CUnitAI__TryStartFightingMode1_004febe0

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnitAI__TryStartFightingMode1_004febe0` at `0x004febe0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004febe0`

## Identity
- Body `[0x004febe0,0x004fec5a]`, 123 bytes, 38 closure instructions. Raw pristine-body SHA-256 `cd1eee4e958eaf9ef083c911b6bdf5f2383d6cdacb4e54916009562f0d448181`; closure range SHA-256 `737d64abc301ed29c5701b4373cede59e5984d1bde536faa127680dd795760ce`; packet range-plus-bytes SHA-256 `c8ed2f265ae134858e9eb9e87bc35102dbf186e80fade08173c043ac15d1d515`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__TryStartFightingMode1_004febe0` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__TryStartFightingMode1_004febe0`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CUnitAI__TryStartFightingMode1_004febe0(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CUnitAI__TryStartFightingMode1_004febe0(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_0066f580`, `DAT_0066ffc8`, `DAT_00672fd0`, `s__s_CANT_start_fighting_cos_it_al_00633c80`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CConsole__Printf` `0x00441740` ×1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__AppendToStatusBufferV` `0x00472240` ×1 site(s) (STATIC_DIRECT).
- Callee `sprintf` `0x0055de9b` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Shared CUnitAI-family vfunc: if this+0x20==1 already, calls owner vfunc +0x1c, logs 'CANT start fighting...', returns 0; otherwise stores this+0x20=1, schedules EVENT_MANAGER event 3000 with DAT_00672fd0 time base, returns 1. Static listing/xref/vtable evidence only; exact source virtual name, mode semantics, runtime AI behavior, BEA patching, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `48c6e4012052094c429c180802d5230b53684cbf1be3e1edef0bd9b103b0346e`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 4 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `batch-1`; question `contract-unit-ai`; value: corroborated in 7/10 coverage sessions; evidence `level-opening-3m-v1-level100, level-opening-3m-v1-level200, level-opening-3m-v1-level201, level-opening-3m-v1-level211 …`.
- Session `batch-2`; question `contract-unit-ai`; value: corroborated in 9/10 coverage sessions; evidence `level-opening-3m-v1-level300, level-opening-3m-v1-level311, level-opening-3m-v1-level312, level-opening-3m-v1-level321 …`.
- Session `batch-3`; question `contract-unit-ai`; value: corroborated in 7/10 coverage sessions; evidence `level-opening-3m-v1-level431, level-opening-3m-v1-level432, level-opening-3m-v1-level500, level-opening-3m-v1-level511 …`.
- Session `batch-4`; question `contract-unit-ai`; value: corroborated in 8/10 coverage sessions; evidence `level-opening-3m-v1-level524, level-opening-3m-v1-level611, level-opening-3m-v1-level612, level-opening-3m-v1-level621 …`.
- Session `batch-5`; question `contract-unit-ai`; value: corroborated in 5/10 coverage sessions; evidence `level-opening-3m-v1-level741, level-opening-3m-v1-level742, level-opening-3m-v1-level850, level-opening-3m-v1-level851 …`.
- Session `batch-6`; question `contract-unit-ai`; value: corroborated in 9/11 coverage sessions; evidence `level-opening-3m-v1-level856, level-opening-3m-v1-level858, level-opening-3m-v1-level859, level-opening-3m-v1-level860 …`.
- Session `batch-7`; question `contract-unit-ai`; value: corroborated in 3/7 coverage sessions; evidence `level-opening-3m-v1-level904, level521-native-20260802-0018-take1, level521-native-20260802-0018-take2`.
- Session `batch-8`; question `contract-unit-ai`; value: corroborated in 1/4 coverage sessions; evidence `level521-native-20260802-0018-take4`.
- Session `batch-9`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `q-pilot-cov-l700-20260731, q-pilot-cov-l742-20260731, q-pilot-cov-l742-rep2-20260731`.
- Session `batch-10`; question `contract-unit-ai`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 18; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004febe0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `48c6e4012052094c429c180802d5230b53684cbf1be3e1edef0bd9b103b0346e`.
- Digest derivation: closure SHA-256 hashes canonical range text `004febe0:004fec5a;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00633c80` length 46 SHA-256 `037bbcbf3d985d1f2229b47229ef9fff7bc6e06c5474b1cdab5f58c897e0d4c7` value `%s CANT start fighting cos it already was !!!`.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
