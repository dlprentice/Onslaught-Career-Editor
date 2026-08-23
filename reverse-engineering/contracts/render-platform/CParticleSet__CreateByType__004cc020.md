# CParticleSet__CreateByType

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticleSet__CreateByType` at `0x004cc020` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004cc020`

## Identity
- Body `[0x004cc020,0x004cc813]`, 2036 bytes, 485 closure instructions. Raw pristine-body SHA-256 `7c70841e58dffea534e84bdf30de5054e6a86eb1ed789380e5ea71a86ed2c505`; closure range SHA-256 `55407ae3de4c898af6a0f36d86b061462e76cb5d19e94d93506b528a9ab97815`; packet range-plus-bytes SHA-256 `906ba4e28bfe419aa234eeaa80ebd93c09861da0220a3dffee3e814bf86fe689`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticleSet__CreateByType`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `f6e6c2c801f80734166d4fb8475954ea25a7ed8337e2ed055ab6f5492feb1783` and decompile SHA-256 `b50a27fe41d0e061276b8f77788c36e69076cfffab4721b923c3aa82d112c8cd` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void * __thiscall CParticleSet__CreateByType(void * this, char * set_name, int type_id, void * context)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void * __thiscall CParticleSet__CreateByType(void * this, char * set_name, int type_id, void * context)
```
- Packet-declared parameter list: `void * this, char * set_name, int type_id, void * context`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void *`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented.

## Globals read/written
- Decompile symbol references: `DAT_0082b3f8`, `DAT_0082b450`, `DAT_009c3df0`, `s_C__dev_ONSLAUGHT2_ParticleSet_cp_00630fb0`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `vector_constructor_iterator_nothrow` `0x004011b0` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleSet__Init` `0x004cc850` x10 site(s) (STATIC_DIRECT).
- Callee `CParticleSet__InitType11` `0x004cd290` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleSet__InitType12` `0x004cd2d0` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleSet__InitType13` `0x004cd3c0` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` x13 site(s) (STATIC_DIRECT).
- Callee `_strncpy` `0x0055e980` x1 site(s) (STATIC_DIRECT).
- Callee `stricmp` `0x00568390` x2 site(s) (STATIC_DIRECT).
- Caller `CParticleSet__LoadFromArchive` `0x004cd7f0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave463 correction: Creates/inserts a particle-set record by sorted name lookup and type id, allocates type-specific object sizes, calls CParticleSet__Init, installs the observed particle-set vtables, seeds type-default fields, copies the name, and updates DAT_0082b450. Static retail-binary evidence only; exact type names, source identity, runtime particle behavior, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `b50a27fe41d0e061276b8f77788c36e69076cfffab4721b923c3aa82d112c8cd`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 8 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless a row states a stronger measured fact:
- Session `all level-openings`; question `corpus-open-core`; value: invariant across all 66 openings; 124,410 cumulative covered bytes; evidence `name=CParticleSet__CreateByType`.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 4; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `f6e6c2c801f80734166d4fb8475954ea25a7ed8337e2ed055ab6f5492feb1783`, and packet decompile SHA-256 `b50a27fe41d0e061276b8f77788c36e69076cfffab4721b923c3aa82d112c8cd`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004cc020:004cc813;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00630fb0` length 34 SHA-256 `eb5df8822a8ffa5075f097c22a35bcdfce92d001d5e5198d57b6fcd63a428d91` value “C:\\dev\\ONSLAUGHT2\\ParticleSet.cpp”.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
