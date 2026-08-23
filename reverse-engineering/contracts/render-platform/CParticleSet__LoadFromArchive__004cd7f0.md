# CParticleSet__LoadFromArchive

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticleSet__LoadFromArchive` at `0x004cd7f0` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004cd7f0`

## Identity
- Body `[0x004cd7f0,0x004cda58]`, 617 bytes, 210 closure instructions. Raw pristine-body SHA-256 `629f6a56c6f13220786e0637bb602e7441292aacf3c497957a1b09fdde846494`; closure range SHA-256 `327ecaffd8a7dda1deb28d4199c635e365bf3098dac04c732e48ec4f658dc7ed`; packet range-plus-bytes SHA-256 `38187a1a8a5ba8d73ee0f9c0a960c15c11da0b76001e1a7362157b8eabf91160`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticleSet__LoadFromArchive`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `289f814b46c335cbf662759dbad8b989e5ec5c898552265f9f81901563381b27` and decompile SHA-256 `3ac1f6cb98b97beceb1ac311b8f6ce65142bf649c890462473ad3bdaebaf4ffe` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CParticleSet__LoadFromArchive(void * this, void * archive_source)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CParticleSet__LoadFromArchive(void * this, void * archive_source)
```
- Packet-declared parameter list: `void * this, void * archive_source`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented.

## Globals read/written
- Decompile symbol references: `DAT_0082b450`, `DAT_009c3df0`, `s_CTokenArchive__HandleRelocation_t_006310c4`, `s_C__dev_ONSLAUGHT2_ParticleSet_cp_00630fb0`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `DebugTrace` `0x0040c640` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleSet__CreateByType` `0x004cc020` x1 site(s) (STATIC_DIRECT).
- Callee `CTokenArchive__ReadNextToken` `0x004f57b0` x5 site(s) (STATIC_DIRECT).
- Callee `CTokenArchive__ResolveReferences` `0x004f5ba0` x1 site(s) (STATIC_DIRECT).
- Callee `PLATFORM__GetSysTimeFloat` `0x005159e0` x4 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` x2 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Free` `0x00549220` x7 site(s) (STATIC_DIRECT).
- Callee `sprintf` `0x0055de9b` x1 site(s) (STATIC_DIRECT).
- Caller `CParticleSet__LoadParticleSetFile` `0x004cda60` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave464 correction: Loads particle sets from a token/archive source after destroying the current list, allocating a 0x1388c archive workspace, validating token ids 0/1/2/3/4, creating each set by type/name, dispatching the created set vfunc +0x18 loader, resolving references, and returning success/failure. Static retail-binary evidence only; exact archive/object layout, source identity, runtime loading behavior, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `3ac1f6cb98b97beceb1ac311b8f6ce65142bf649c890462473ad3bdaebaf4ffe`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 8 callee record(s), and 2 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 18; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `289f814b46c335cbf662759dbad8b989e5ec5c898552265f9f81901563381b27`, and packet decompile SHA-256 `3ac1f6cb98b97beceb1ac311b8f6ce65142bf649c890462473ad3bdaebaf4ffe`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004cd7f0:004cda58;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00630fb0` length 34 SHA-256 `eb5df8822a8ffa5075f097c22a35bcdfce92d001d5e5198d57b6fcd63a428d91` value “C:\\dev\\ONSLAUGHT2\\ParticleSet.cpp”.
- Packet string ref `0x006310c4` length 97 SHA-256 `783b6f15fd9b674df39869ab3d72562057619a578de373cb4013123ffbec1e28` value “CTokenArchive::HandleRelocation took %f seconds\nCParticleSet ::ReadData         took %f seconds\n”.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
