# CParticle__Destroy

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticle__Destroy` at `0x004cae50` in the particle/effects runtime cohort; lifecycle, update, render-support, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004cae50`

## Identity
- Body `[0x004cae50,0x004caec2]`, 115 bytes, 42 closure instructions. Raw pristine-body SHA-256 `149ec90184f961b47db689ad29b9a57d554ca0b462e5757eff919879618791b3`; closure range SHA-256 `6dc0acb0e909d2dc345964dc1af945e8cb71795c5575e8140040cf51dd6cc919`; packet range-plus-bytes SHA-256 `0fce539fc8c2886b94d367626982a6a6f42893c411016a4bace43678381db194`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticle__Destroy`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `0809bbe082060769a9389e126c027ce8e2951383242006574cab16c56eba1750` and decompile SHA-256 `b67bb923fcc49abd70beba48cfec5cf9cf61f84b5cbad16ab6e47efefe9a6dca` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CParticle__Destroy(void * particle)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CParticle__Destroy(void * particle)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, and nullability remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_009c3df0`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CParticleManager__UnlinkNodeFromActiveList` `0x004c0560` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Free` `0x00549220` x1 site(s) (STATIC_DIRECT).
- Caller `CFrontEnd__ReleaseParticleHudWaypointResources` `0x004691c0` x1 site(s) (instruction-flow).
- Caller `CGame__ShutdownRestartLoop` `0x0046ca70` x1 site(s) (instruction-flow).
- Caller `CParticleManager__AllocateParticle` `0x004cb5c0` x1 site(s) (instruction-flow).
- Caller `CParticleManager__UpdateParticleAndRecycleIfDead` `0x004cb920` x1 site(s) (instruction-flow).
- Caller `CParticleManager__PruneDeadParticles` `0x004cbe30` x1 site(s) (instruction-flow).
- Caller `CDXEngine__ShutdownParticleSystemBundle` `0x0054f6e0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: neither the exact-base canonical crosswalk nor any of the five landed source-wave receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope; no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave463 correction: Destroys/recycles one particle node. When particle+0x88 is nonzero, optionally calls particle-set (particle+0x5c) vfunc +0x38 and frees the +0x88 block via CDXMemoryManager__Free unless that guard returns 0. If a particle-set is present, either UnlinkNodeFromActiveList when prev/next links at +0/+4 are incomplete, or splices the doubly-linked neighbors and clears particle-set+0x58 when it still points at this particle (current-particle slot, not an effect handle). Static retail-binary evidence only; unaff_ESI on the unlink call, exact layout, source identity, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `b67bb923fcc49abd70beba48cfec5cf9cf61f84b5cbad16ab6e47efefe9a6dca`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 6 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device/file failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof. Any runtime addendum quoted from the packet comment remains bounded to that packet's named receipt.

## Evidence
- Writer authority: task `t_23f3c22a`, immutable cohort-10 manifest SHA-256 `6bb51e4b90110ea4847a777e8e0106d6fcee4fa99ce79eb462e70f032bae3f9b`, row 2; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `0809bbe082060769a9389e126c027ce8e2951383242006574cab16c56eba1750`, and packet decompile SHA-256 `b67bb923fcc49abd70beba48cfec5cf9cf61f84b5cbad16ab6e47efefe9a6dca`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004cae50:004caec2;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
