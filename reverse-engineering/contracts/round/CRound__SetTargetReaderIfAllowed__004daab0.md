# CRound__SetTargetReaderIfAllowed

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__SetTargetReaderIfAllowed` at `0x004daab0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; TTD-session execution rows are cited below; they corroborate execution only.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004daab0`

## Identity
- Body `[0x004daab0,0x004dab4e]`, 159 bytes. Raw pristine-body SHA-256 `6d76b41ff07714708b020b71e955b094d8e0cec9629855f44d6466539031f98b`; closure range SHA-256 `3f92d54cfa72e3d39e2bd03a05d45a54cde9db8df5a4692218ee97d6ba013db8`; packet range-plus-bytes SHA-256 `3e6e345a99a305065bcde7f3637aa69710dc972dd25275fb6860c6c1104af696`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name and packet/decompile metadata name: `CRound__SetTargetReaderIfAllowed`. The matching labels are counted intent only, not recovered source symbols and not semantic proof.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__thiscall` for `void __thiscall CRound__SetTargetReaderIfAllowed(void * this, void * targetReader, int replaceExisting)`: a receiver is modeled as `this`, with explicit stack parameters as shown. Parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void __thiscall CRound__SetTargetReaderIfAllowed(void * this, void * targetReader, int replaceExisting)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded receiver/base pointer whose +0xf0 block gates updates and whose +0xe8/+0xec fields participate in the displayed calls.
- `targetReader` — must be nonnull to enter the body; stored through the packet-listed setter and inspected at +0x34 bit 0x08.
- `replaceExisting` — nonzero enables the displayed old-value call/removal/clear sequence before storing `targetReader`.

## Return value meaning
not_applicable — the packet/decompile signature is void.

## Globals read/written
- `DAT_008551a0` — its address is passed to the packet-listed remove and add callees on separate bit-gated paths.

## Callees relied on / callers
- Callees (packet structured array): `CGenericActiveReader__SetReader` `0x00401000` ×2 (STATIC_DIRECT); `CBattleEngine__LockHit` `0x00407140` ×1 (STATIC_DIRECT); `CSPtrSet__AddToHead` `0x004e5a80` ×1 (STATIC_DIRECT); `CSPtrSet__Remove` `0x004e5bd0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `ProjectileBurst__SpawnFromCurrentPreset` `0x005069f0` ×1 site(s).
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Does nothing unless `targetReader` is nonnull and either the dword at `*(this+0xf0)+0x48` is nonzero or the float at +0x1c is below zero. With a nonzero `replaceExisting`, it conditionally calls the listed +0xec/+0xe8 callee when +0xec has bit 0x08 at +0x34, conditionally removes `this` through `DAT_008551a0` when +0xe8 has the same bit, and clears +0xe8 through the listed setter. It then stores `targetReader` through that setter and conditionally adds `this` through `DAT_008551a0` when `targetReader+0x34` has bit 0x08.

## Error / edge behavior
`this`, +0xf0, and nonnull nested pointers are not otherwise validated. A false outer gate leaves existing state unchanged. Reader/list/target wording is counted name intent only; exact ownership and list invariants are not_determinable.

## Runtime corroboration (TTD, bounded)
The cohort-4 brief supplies these ten exact TTD rows:
- `batch-1` — corroborated in 7/10 coverage sessions
- `batch-2` — corroborated in 7/10 coverage sessions
- `batch-3` — corroborated in 8/10 coverage sessions
- `batch-4` — corroborated in 2/10 coverage sessions
- `batch-5` — corroborated in 5/10 coverage sessions
- `batch-6` — corroborated in 5/11 coverage sessions
- `batch-7` — corroborated in 2/7 coverage sessions
- `batch-8` — corroborated in 1/4 coverage sessions
- `batch-9` — corroborated in 2/3 coverage sessions
- `batch-10` — no coverage collector output for this batch's sessions
These rows prove bounded execution only (bounded: batch-1, batch-2, batch-3, batch-4, batch-5, batch-6, batch-7, batch-8, batch-9, batch-10). Execution coverage alone does not prove the semantic contract, parameter/field meanings, side-effect completeness, or parity, and it does not justify promotion.

## Evidence
- Digest reconciliation: closure `bodyDigest` `3f92d54cfa72e3d39e2bd03a05d45a54cde9db8df5a4692218ee97d6ba013db8` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `3e6e345a99a305065bcde7f3637aa69710dc972dd25275fb6860c6c1104af696` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `6d76b41ff07714708b020b71e955b094d8e0cec9629855f44d6466539031f98b` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004daab0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: ten rows are quoted exactly in Runtime corroboration; they establish bounded execution only, not semantic correctness.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — outer gates, optional replacement sequence, bit tests, and all four structured direct-call roles are explicit; bounded execution rows do not establish field, ownership, or high-level semantics. Confidence is capped at 3 because execution coverage alone does not prove the semantic contract. Proposed promotion: false.

## Unresolved questions
- Concrete types and ownership of +0xe8/+0xec and `targetReader`.
- Meaning of pointed-to +0x48/+0x1c gates and +0x34 bit 0x08.
- List invariants and failure contracts of the four direct callees.
