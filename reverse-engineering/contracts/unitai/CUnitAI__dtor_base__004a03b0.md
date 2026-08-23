# CUnitAI__dtor_base

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnitAI__dtor_base` at `0x004a03b0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004a03b0`

## Identity
- Body `[0x004a03b0,0x004a044e]`, 159 bytes, 51 closure instructions. Raw pristine-body SHA-256 `0fbc7cc82283f5b2a51ca2fd991a2f9f8f1d8fbba9f23b193d76587890d51394`; closure range SHA-256 `d9e08e447a754e14006e50fe36ea1bbb06383c54e7260b430516a2bc62e749ca`; packet range-plus-bytes SHA-256 `30e5d59916a20559996353333a753e97659ce075cc89e140a1deb870f5943899`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__dtor_base` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__dtor_base`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__dtor_base(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__dtor_base(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CMonitor__Shutdown` `0x004bac40` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__Remove` `0x004e5bd0` ×3 site(s) (STATIC_DIRECT).
- Caller `CMechAI__scalar_deleting_dtor` `0x004a0390` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave437 destructor correction: called by CMechAI__scalar_deleting_dtor. The body restores vtable 0x005d8d1c, removes linked reader cells at +0x28, +0x24, and +0x0c when present, then calls CMonitor__Shutdown. Static retail evidence only; exact base-class identity, linked-set semantics, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `8643e8dbbf47967d56f0e8e9bcf4314f28056731f13805f9a75f8867638cf015`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 9; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004a03b0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `8643e8dbbf47967d56f0e8e9bcf4314f28056731f13805f9a75f8867638cf015`.
- Digest derivation: closure SHA-256 hashes canonical range text `004a03b0:004a044e;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
