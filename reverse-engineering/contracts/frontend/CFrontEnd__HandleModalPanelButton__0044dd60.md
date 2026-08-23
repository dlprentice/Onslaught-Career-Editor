# CFrontEnd__HandleModalPanelButton

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__HandleModalPanelButton` at `0x0044dd60`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0044dd60`

## Identity
- Body `[0x0044dd60,0x0044de8a]`, 299 bytes, 86 closure instructions. Raw pristine-body SHA-256 `bb1106e6ccbeb0aad5ecacc4b5724ccb752b5c57294ad03812c19b66fec67b60`; closure range SHA-256 `ed4cb88ce6592c73cd1ebd804d3c0ae8883ebbdf7d952eec3725ae065321f680`; packet range-plus-bytes SHA-256 `19bdf18c56ca535fdcc3c5a1aa1dec1c15ecc0e93d58212c2b02c45f46049e21`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__HandleModalPanelButton` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__HandleModalPanelButton`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFrontEnd__HandleModalPanelButton(void * this, int button, int context)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFrontEnd__HandleModalPanelButton(void * this, int button, int context)
```
- Packet-declared parameter list: `void * this, int button, int context`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0089d758`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CFrontEnd__SetPage` `0x00466ae0` ×2 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__PlaySound` `0x00468770` ×5 site(s) (STATIC_DIRECT).
- Caller `CFrontEnd__RenderAndProcessModalPanel` `0x0044d6f0` ×1 site(s) (instruction-flow).
- Caller `CFrontEnd__ReceiveButtonAction` `0x004669a0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: the current source crosswalk has no pinned Stuart owner for this VA.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Signature hardening: RET 0x8 shows button and context stack arguments; body handles modal button codes 0x2a/0x2b/0x2c, plays frontend sounds, updates +0x1fa0/+0x1fa4 result fields, and may switch page through +0x1fa8/+0x1fac. Exact context argument semantics, runtime frontend behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `5f9b4e138a5185495f524d1465d09569810cfac31797bcbb9863cf196f4c55d6`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 2 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 4; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x0044dd60.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `5f9b4e138a5185495f524d1465d09569810cfac31797bcbb9863cf196f4c55d6`.
- Digest derivation: closure SHA-256 hashes canonical range text `0044dd60:0044de8a;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
