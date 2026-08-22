# CBattleEngine__EnableVolumeEntryGroupsByName

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__EnableVolumeEntryGroupsByName` at `0x0040dc30`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040dc30`

## Identity
- Body `[0x0040dc30,0x0040dc54]`, 37 bytes. Raw pristine-body SHA-256 `fa72dd3ff85e273d09fc380eeac638fd7559c07bded84a94d796a390eb92f839`; closure range SHA-256 `fa212e95483691856679cb3901e674a181f364ac8d8759c3a4a7e08a59c7c038`; packet range-plus-bytes SHA-256 `d74ce3d96cf7e6804a0273d2f4363fe6f3f2de785e63f72f004f146b2d274387`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__EnableVolumeEntryGroupsByName` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH`.

## Calling convention
`__thiscall`: receiver in ECX; one explicit pointer argument on the stack. Names are USER_DEFINED/counting intent only.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__EnableVolumeEntryGroupsByName(void * this, void * entryName)
```
- `this` — receiver supplying pointers at +0x578 and +0x57c.
- `entryName` — pointer forwarded unchanged as the second argument to both direct callees; type, encoding, and ownership are unknown.

## Return value meaning
not_applicable (void).

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): `CGeneralVolume__EnableLinkedEntriesByName` `0x004127a0` ×1 (STATIC_DIRECT); `CGeneralVolume__EnableEntriesByName` `0x00414970` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded; virtual dispatch may not appear as a structured direct caller.
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Calls the packet-listed +0x578 helper with `(*(void **)(this+0x578), entryName)`, then calls the packet-listed +0x57c helper with `(*(void **)(this+0x57c), entryName)`. Enable/group semantics come only from counted names and are not independent retail semantic proof.

## Error / edge behavior
No null checks protect the receiver, either component pointer, or `entryName`. The second call occurs after the first without visible rollback if a callee fails.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040dc30`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `fa212e95483691856679cb3901e674a181f364ac8d8759c3a4a7e08a59c7c038` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `d74ce3d96cf7e6804a0273d2f4363fe6f3f2de785e63f72f004f146b2d274387` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `fa72dd3ff85e273d09fc380eeac638fd7559c07bded84a94d796a390eb92f839` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040dc30.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — two ordered forwarding calls are explicit; callee effects and parameter representation are external. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete types of the +0x578/+0x57c components and `entryName`.
- Failure/partial-update behavior across the two callees.
- Whether both calls target conceptually linked groups as their labels suggest.
