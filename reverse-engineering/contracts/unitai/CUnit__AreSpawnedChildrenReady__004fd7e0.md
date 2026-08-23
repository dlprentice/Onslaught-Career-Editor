# CUnit__AreSpawnedChildrenReady

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnit__AreSpawnedChildrenReady` at `0x004fd7e0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004fd7e0`

## Identity
- Body `[0x004fd7e0,0x004fd82b]`, 76 bytes, 35 closure instructions. Raw pristine-body SHA-256 `deafa318a809ae4cee20c0a012f0c355d2c2035bef93a9fd41f843a5b0c16fc0`; closure range SHA-256 `7cbdaeda4217be989e21f6bf189973244fecf33b91d005d0cceb569cb574dc06`; packet range-plus-bytes SHA-256 `7219b809ea191feabba809e05d463bcedc18b1b91ebbe34002588daac1b31842`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnit__AreSpawnedChildrenReady` comes from the current closure/register row. Packet label matches canonical tracked name `CUnit__AreSpawnedChildrenReady`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `bool __fastcall CUnit__AreSpawnedChildrenReady(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
bool __fastcall CUnit__AreSpawnedChildrenReady(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `bool`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CUnit__IsInBlockedSupportState` `0x004e4420` ×1 site(s) (STATIC_DIRECT).
- Callee `CSpawnerThng__IsSpawnComplete` `0x004e4430` ×1 site(s) (STATIC_DIRECT).
- Caller `CDropship__ProcessDoorThrustersAndChildUnits` `0x00447120` ×1 site(s) (instruction-flow).
- Caller `CUnitAI__CanContinueDoorWingTransition` `0x004480c0` ×1 site(s) (instruction-flow).
- Caller `CDropshipAI__VFunc_09_00448580` `0x00448580` ×1 site(s) (instruction-flow).
- Caller `IScript__SpawnersEmpty` `0x00535a90` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Register-this predicate: walks linked entries at this+0x18c; returns true only if the list is empty or every entry is CSpawnerThng__IsSpawnComplete and does not satisfy CUnit__IsInBlockedSupportState; any incomplete or blocked entry returns false. Same this+0x18c Unit spawner-list shape as CUnit__HasAnyInBlockedSupportState. CUnitAI__ conflicts with that Unit-field sibling and with Wave527 AI→Unit renames for Unit-field helpers — callers may be UnitAI/Dropship but this is Unit-shaped. Rename toward CUnit__AreSpawnedChildrenReady (or SharedUnit equivalent) remains propose-only outside this comment lane. Static retail evidence only; child/spawner ownership, state names, runtime spawn readiness, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `d1fbf348aa1ff79bf488846a0ccb77878d43913f1d45a890e58909fc1fc1b0d9`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 4 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 14; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004fd7e0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `d1fbf348aa1ff79bf488846a0ccb77878d43913f1d45a890e58909fc1fc1b0d9`.
- Digest derivation: closure SHA-256 hashes canonical range text `004fd7e0:004fd82b;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
