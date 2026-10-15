# CParticleSet__LoadParticleSetFile

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticleSet__LoadParticleSetFile` at `0x004cda60` in the particle/effects runtime cohort; lifecycle, update, render-support, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004cda60`

## Identity
- Body `[0x004cda60,0x004cdb88]`, 297 bytes, 94 closure instructions. Raw pristine-body SHA-256 `dbc33d8e96fce5e1357c2fdf1e95685405df6cc66382630f41d46123707d60ba`; closure range SHA-256 `6d211fa1be0fbf86b8fb4962b6c59cd034634420946edc80f00e98d06f940cc9`; packet range-plus-bytes SHA-256 `7b3426bb1f49876e64528409bd5dc990227dec6705d087e1583e08a477ec5b6f`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticleSet__LoadParticleSetFile`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `456413edbd2d17fd44ae717975d7e4985a8d3efadc2dc3e0e09335693fa19583` and decompile SHA-256 `09a86533392a82320dffc58d67b21dc5679bfbf56cb836f793e7ef07296a780f` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CParticleSet__LoadParticleSetFile(void * this, int particle_set_mode)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CParticleSet__LoadParticleSetFile(void * this, int particle_set_mode)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, and nullability remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The packet signature declares `int`. The analyst comment quoted in Behavior summary is bounded evidence for its interpretation; exact ABI domain, sentinel behavior, and caller expectations remain not_determinable unless explicitly stated there.

## Globals read/written
- Decompile symbol references: `DAT_009c3df0`, `s_C__dev_ONSLAUGHT2_ParticleSet_cp_00630fb0`, `s_data_ParticleSets_Frontend_par_00631148`, `s_data_ParticleSets_MainSet_par_00631128`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CDXMemBuffer__OpenReadMode11` `0x0048ddd0` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemBuffer__Close_Thunk` `0x0048ddf0` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleSet__LoadFromArchive` `0x004cd7f0` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemBuffer__ctor` `0x00547d70` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemBuffer__dtor_base` `0x00547d90` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Free` `0x00549220` x1 site(s) (STATIC_DIRECT).
- Caller `CFrontEnd__LoadSharedResources` `0x004687e0` x1 site(s) (instruction-flow).
- Caller `CGame__LoadResources` `0x0046cd30` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: neither the exact-base canonical crosswalk nor any of the five landed source-wave receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope; no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave464 correction: High-level ParticleSet file loader that destroys the current set list, allocates a 200-byte filename buffer, selects MainSet.par for modes 0/2 or Frontend.par otherwise, opens a stack CDXMemBuffer through CDXMemBuffer__OpenReadMode11, calls CParticleSet__LoadFromArchive when open succeeds, closes/destroys the buffer, frees the filename, and returns 1. Static retail-binary evidence only; runtime file loading behavior, source identity, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `09a86533392a82320dffc58d67b21dc5679bfbf56cb836f793e7ef07296a780f`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 2 caller record(s), 7 callee record(s), and 3 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device/file failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof. Any runtime addendum quoted from the packet comment remains bounded to that packet's named receipt.

## Evidence
- Writer authority: task `t_23f3c22a`, immutable cohort-10 manifest SHA-256 `6bb51e4b90110ea4847a777e8e0106d6fcee4fa99ce79eb462e70f032bae3f9b`, row 25; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `456413edbd2d17fd44ae717975d7e4985a8d3efadc2dc3e0e09335693fa19583`, and packet decompile SHA-256 `09a86533392a82320dffc58d67b21dc5679bfbf56cb836f793e7ef07296a780f`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004cda60:004cdb88;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00630fb0` length 34 SHA-256 `eb5df8822a8ffa5075f097c22a35bcdfce92d001d5e5198d57b6fcd63a428d91` value `C:\\dev\\ONSLAUGHT2\\ParticleSet.cpp`.
- Packet string ref `0x00631128` length 32 SHA-256 `38a63eecca42ff211802e4b911acae9665866729a6aeae773244e81dc7ef1071` value `data\\ParticleSets\\MainSet.par`.
- Packet string ref `0x00631148` length 32 SHA-256 `fac3f3a2516a6daf73dceee0ca3585d8c16ac169f3a4a9a059db9fe6c5627319` value `data\\ParticleSets\\Frontend.par`.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
