# CRound__ClipToGround

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__ClipToGround` at `0x004d82e0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d82e0`

## Identity
- Body `[0x004d82e0,0x004d831e]`, 63 bytes. Raw pristine-body SHA-256 `e43a75c9c1a2cdb47bb5429f5d7a125e40bc2916ae9a7efee9502459ffd475eb`; closure range SHA-256 `2bbb534a3be23931afabc1ce164c5e16d2c7318f52aa6870e016380b6a2bc4a8`; packet range-plus-bytes SHA-256 `25f78552e486cea9248d965760260947407d7bf8616bedb7cf3ed09ca91e7bbf`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__ClipToGround`. Packet/decompile metadata name: `CRound__VFunc_44_004d82e0`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=ANALYSIS`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `undefined4 __fastcall CRound__VFunc_44_004d82e0(int param_1)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
undefined4 __fastcall CRound__VFunc_44_004d82e0(int param_1)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `param_1` — unguarded base address used to follow +0xf0 and inspect three floats in the pointed-to block.

## Return value meaning
Returns 0 exactly when floats at pointed-to offsets +0x30 and +0x3c equal 0.0 and the float at +0x28 is at most 0.0; otherwise returns 1.

## Globals read/written
- not_applicable — no absolute data symbol is read or written.

## Callees relied on / callers
- Callees (packet structured array): none recorded; visible indirect calls have no structured direct-callee VA.
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Loads the pointer at +0xf0, tests three floats with the displayed conjunction, and converts that condition into a 0/1 result.

## Error / edge behavior
The base and nested pointer are unguarded. NaN affects the comparisons according to machine floating-point rules; high-level clipping/ground meaning is not established.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d82e0`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `2bbb534a3be23931afabc1ce164c5e16d2c7318f52aa6870e016380b6a2bc4a8` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `25f78552e486cea9248d965760260947407d7bf8616bedb7cf3ed09ca91e7bbf` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `e43a75c9c1a2cdb47bb5429f5d7a125e40bc2916ae9a7efee9502459ffd475eb` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d82e0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — all three comparisons and both return values are explicit; field roles and descriptive tracked name remain unproven. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meanings and units of the +0x28/+0x30/+0x3c floats.
- Behavioral role of the resulting predicate at indirect call sites.
