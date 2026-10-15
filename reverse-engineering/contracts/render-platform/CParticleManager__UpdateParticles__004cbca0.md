# CParticleManager__UpdateParticles

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticleManager__UpdateParticles` at `0x004cbca0` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004cbca0`

## Identity
- Body `[0x004cbca0,0x004cbe23]`, 388 bytes, 115 closure instructions. Raw pristine-body SHA-256 `76227216121c18e422dfe2174e4ccb0f983421a62c1c78b9ee3a30dea72148ef`; closure range SHA-256 `52faf2d4b29d5cbfafe1d7c03eb7cc7680c4ed837163458425e1eb6e4ba11287`; packet range-plus-bytes SHA-256 `da342d749fe729c2695d2bb8da742c621607488e6357a8567482c0d963895d7c`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticleManager__UpdateParticles`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `79fe6b65a631d0557c6752f2d0daae8634037fe02b7559599541285d0e3606c8` and decompile SHA-256 `ad69298603e7272d97e25e7f9408e6186561a53cfd74b22f3cc37101a4c1d844` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet field records `__cdecl` for `void __cdecl CParticleManager__UpdateParticles(void * active_head)`. The packet analyst comment explicitly refutes the packet field's cdecl form: both exits use `RET 0x4`, while the sole caller pushes the head, loads ECX with the manager, and calls. The bounded reconciled shape is thiscall with `this` plus one stack `active_head`; no typed list formal is invented.

## Prototype and parameter semantics
```c
void __thiscall CParticleManager__UpdateParticles(void * this, void * active_head)
```
- Reconciled bounded ABI from the packet's own analyst comment: `void __thiscall CParticleManager__UpdateParticles(void * this, void * active_head)`. The packet field's declared `void __cdecl CParticleManager__UpdateParticles(void * active_head)` remains preserved above as metadata, not asserted as true.

## Return value meaning
The reconciled bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_009c63f8`, `DAT_009c63fc`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CParticleManager__Update` `0x004cb210` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “CParticleManager active-list updater (handle-state refresh, vfunc +0x54 for state 2, lifetime decrement, position integrate by global dt, optional death flags under DAT_009c63fc). ECX receiver (manager); both exits `RET 0x4` prove one stack dword after this. Declared `void __cdecl (void * active_head)` is false — callee cleans one dword, and sole caller at 0x004cb28a does `PUSH` head / `MOV ECX,EDI` / CALL (MSVC thiscall). Shape is `__thiscall (void * this, void * active_head)` (do not invent typed list formals beyond that plate). Static retail evidence only; exact particle/handle layouts, runtime update UX, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `ad69298603e7272d97e25e7f9408e6186561a53cfd74b22f3cc37101a4c1d844`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 0 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 17; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `79fe6b65a631d0557c6752f2d0daae8634037fe02b7559599541285d0e3606c8`, and packet decompile SHA-256 `ad69298603e7272d97e25e7f9408e6186561a53cfd74b22f3cc37101a4c1d844`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004cbca0:004cbe23;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
