# CTree__dtor_base

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CTree__dtor_base` at `0x004f63c0` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004f63c0`

## Identity
- Body `[0x004f63c0,0x004f6429]`, 106 bytes, 27 closure instructions. Raw pristine-body SHA-256 `5cb5b1e761bbc579f6ce916f62935936a135c3d2d2b82e6548e61b487da11c50`; closure range SHA-256 `5f8f2abe2f9019707f81b618c8ae349d58c14e394e59ea681dbf3f340cbf9fba`; packet range-plus-bytes SHA-256 `6121102a38ac1734d9f4f3eff04fee7641b0c90394b7295261ac807a4edf6340`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CTree__dtor_base`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `d1b9516ab09c78446e3dbe887d686db61c50e72869b7019b608335ebda0b6a79` and decompile SHA-256 `88767842fde887cd6a124d2b1a789243a4bbe59fbdbfd0838130286078712dc7` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CTree__dtor_base(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CTree__dtor_base(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_009c3df0`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CThing__dtor_base` `0x004f3640` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Free` `0x00549220` x1 site(s) (STATIC_DIRECT).
- Caller `CTree__scalar_deleting_dtor` `0x004bfce0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave1217 static current-risk read-back: CTree destructor body called by CTree__scalar_deleting_dtor at 0x004bfce3. The body restores CTree/CThing-adjacent vtables, frees the falling-tree data pointer at this+0x48 through CDXMemoryManager__Free when present, clears that pointer, and delegates to CThing__dtor_base. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact tree layout, runtime falling-tree cleanup behavior, BEA patching, and rebuild parity remain separate proof.”
- The non-empty packet decompile is bound by SHA-256 `88767842fde887cd6a124d2b1a789243a4bbe59fbdbfd0838130286078712dc7`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless a row states a stronger measured fact:
- Session `level521-native-20260802-0018-take4, level521-native-20260802-0018-take2`; question `corpus-combat-only`; value: combat-exclusive; 210 covered bytes; evidence `name=CTree__dtor_base`.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 7; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `d1b9516ab09c78446e3dbe887d686db61c50e72869b7019b608335ebda0b6a79`, and packet decompile SHA-256 `88767842fde887cd6a124d2b1a789243a4bbe59fbdbfd0838130286078712dc7`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004f63c0:004f6429;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
