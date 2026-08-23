# CThing__dtor_base

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CThing__dtor_base` at `0x004f3640`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004f3640`

## Identity
- Body `[0x004f3640,0x004f36c6]`, 135 bytes, 37 closure instructions. Raw pristine-body SHA-256 `17bccd5f97d176d494ca8026b6fec54465b2e7c059f612c436f4dc597201cd92`; closure range SHA-256 `b1f704a06b6dc846b8cb598bdbdd92ed7eff31838fad8f6539ceceefe6296ec2`; packet range-plus-bytes SHA-256 `aa4af5d30fb8a275b1c185c1d8c080b6461e84bb56d81ee1a3fd933eef572208`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CThing__dtor_base` comes from the current closure/register row. Packet label matches canonical tracked name `CThing__dtor_base`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CThing__dtor_base(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CThing__dtor_base(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CMapWhoEntry__RemoveFromMap` `0x00492c70` ×1 site(s) (STATIC_DIRECT).
- Callee `CMonitor__Shutdown` `0x004bac40` ×1 site(s) (STATIC_DIRECT).
- Caller `CWaypoint__dtor_base` `0x004bfe70` ×1 site(s) (instruction-flow).
- Caller `CThing__scalar_deleting_dtor` `0x004f3480` ×1 site(s) (instruction-flow).
- Caller `CTree__dtor_base` `0x004f63c0` ×1 site(s) (instruction-flow).
- Caller `Unwind@005d3fa0` `0x005d3fa0` ×1 site(s) (instruction-flow).
- Caller `Unwind@005d51f0` `0x005d51f0` ×1 site(s) (instruction-flow).
- Caller `Unwind@005d5300` `0x005d5300` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: the current source crosswalk has no pinned Stuart owner for this VA.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave516 rename/signature/comment hardening: CThing destructor-base body. The body restores CThing vtables, scalar-deletes the collision-seeking object at +0x38 and render thing at +0x30 when present, clears both fields, removes the embedded map-who entry, and shuts down monitor state. Static retail evidence only; exact compiler destructor emission identity, concrete field layout, runtime destruction behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `d9bccde2c1035c0155f5fc181d47ef20c41c93c520da2f27d7a3f35b0b6a0787`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 6 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take4, level521-native-20260802-0018-take2`; question `corpus-combat-only`; value: combat-exclusive; 268 covered bytes; evidence `name=CThing__dtor_base`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 23; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004f3640.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `d9bccde2c1035c0155f5fc181d47ef20c41c93c520da2f27d7a3f35b0b6a0787`.
- Digest derivation: closure SHA-256 hashes canonical range text `004f3640:004f36c6;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
