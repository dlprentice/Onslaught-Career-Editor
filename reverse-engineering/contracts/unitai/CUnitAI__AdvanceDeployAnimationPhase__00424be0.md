# CUnitAI__AdvanceDeployAnimationPhase

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__AdvanceDeployAnimationPhase` at `0x00424be0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00424be0`

## Identity
- Body `[0x00424be0,0x00424c9b]`, 188 bytes. Raw pristine-body SHA-256 `867eeb86ccb9818c0ad2f58ef94dbef11dbdfbc4607ffffa11b7974fb0bfb697`; closure range SHA-256 `3d7e13fb4890a6658f434ae9efd42597835102bd2f23c099d487d303cf824ac2`; packet range-plus-bytes SHA-256 `4befca3c345f5ac1edc669015cc1683930ab994a6a21eb2f6e34a8217de80c72`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__AdvanceDeployAnimationPhase` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__AdvanceDeployAnimationPhase(void * this)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__AdvanceDeployAnimationPhase(void * this)
```
- `this` — receiver/base pointer read or written at +0x8c and +0x114..+0x128.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_006235a0` and `PTR_DAT_0062359c` — alternative address tokens selected for states 1 and 2; packet stringRefs do not identify their text.

## Callees relied on / callers
- Callees (packet structured array): `CMesh__FindAnimationIndexByName` `0x004aa630` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CUnitAI__UpdateDeployAimAndScheduleEvent` `0x00424a20` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Adds +0x120 to +0x124, copies the prior +0x124 value to +0x128, and returns when the sum is at most 1.0. Above that threshold, state +0x114 equal to 1 or 2 selects one of two address tokens, an indirect +0x24 call obtains an object, the packet-listed direct callee resolves an integer written at +0x11c, and an indirect +0x38 call can update +0x120. The body then clears +0x124 and +0x114; any other state instead clears +0x124 and +0x120 and returns.

## Error / edge behavior
The first indirect access through +0x8c occurs before the later null check of +0x8c. Indirect slot contracts and the contents of both selected address tokens are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00424be0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `3d7e13fb4890a6658f434ae9efd42597835102bd2f23c099d487d303cf824ac2` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `4befca3c345f5ac1edc669015cc1683930ab994a6a21eb2f6e34a8217de80c72` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `867eeb86ccb9818c0ad2f58ef94dbef11dbdfbc4607ffffa11b7974fb0bfb697` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00424be0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — phase arithmetic and state branches are explicit, but both indirect calls and token meanings are unresolved. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Text/role at `DAT_006235a0` and `PTR_DAT_0062359c`.
- Contracts of indirect slots +0x24 and +0x38.
