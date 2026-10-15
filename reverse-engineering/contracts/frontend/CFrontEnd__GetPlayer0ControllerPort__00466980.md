# CFrontEnd__GetPlayer0ControllerPort

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__GetPlayer0ControllerPort` at `0x00466980`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00466980`

## Identity
- Body `[0x00466980,0x0046698f]`, 16 bytes, 7 closure instructions. Raw pristine-body SHA-256 `b5fd74d39806a67fc12bd847ba98da5da32e588b8202c51cb41152ede3c4eb19`; closure range SHA-256 `1a0fafb5f1f8110e23fbb7cfd4fb0bb012a80f6d7c53ab0ffceda7d3cfc2ee7a`; packet range-plus-bytes SHA-256 `f9295f943c5d5b292e2a476c7590869d800de8e1fa2e21148a3db5b78ae21c6f`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__GetPlayer0ControllerPort` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__GetPlayer0ControllerPort`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CFrontEnd__GetPlayer0ControllerPort(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CFrontEnd__GetPlayer0ControllerPort(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CGame__LoadLevel` `0x0046cdf0` ×3 site(s) (instruction-flow).
- Caller `CGame__DrawLocalCoopControllerPrompt` `0x00527990` ×2 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/FrontEnd.cpp` lines `444-449` defines `CFrontEnd::GetPlayer0ControllerPort` as `int		CFrontEnd::GetPlayer0ControllerPort()`; exact extracted source-body SHA-256 `a7720b23d5ef50c962a4b3388bc08306eb31a267eaf43ae79202fbf6ed5a5667`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=1, switch=0, for=0, while=0; named call tokens none mechanically detected.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Signature/source-parity hardening: CFrontEnd player-0 controller port helper reads offset +0x274 and normalizes the unset -1 sentinel to 0, matching Stuart's CFrontEnd::GetPlayer0ControllerPort shape. Static source/decompile evidence only; runtime controller behavior remains unproven.”
- The displayed decompile is non-empty and SHA-256 `64c52d42a93a52b36a4c031093918f90ddaeff6be7a0e5f7be0f2ad9e2851240`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 2 caller record(s), 0 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 9; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00466980.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `64c52d42a93a52b36a4c031093918f90ddaeff6be7a0e5f7be0f2ad9e2851240`.
- Digest derivation: closure SHA-256 hashes canonical range text `00466980:0046698f;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/FrontEnd.cpp` `CFrontEnd::GetPlayer0ControllerPort` line 444 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__GetPlayer0ControllerPort.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
