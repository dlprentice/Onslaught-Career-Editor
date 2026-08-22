# CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect` at `0x0040dc60`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040dc60`

## Identity
- Body `[0x0040dc60,0x0040dc84]`, 37 bytes. Raw pristine-body SHA-256 `d666fc300ce2dd4d230642cfc49d39d32ce7acf1be8823c909c284d35d2b38b5`; closure range SHA-256 `5317cdd59257869509c40f72b34c76e0b7240236a328780a4e3d5cfcf244f93d`; packet range-plus-bytes SHA-256 `276004d79c8f9068721627c7a2af994bfa55eb8cfabcecb06f2bc16f4332b271`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH`.

## Calling convention
`__thiscall`: receiver in ECX; one explicit pointer argument on the stack. Names are USER_DEFINED/counting intent only.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect(void * this, void * entryName)
```
- `this` — receiver supplying pointers at +0x578 and +0x57c.
- `entryName` — pointer forwarded unchanged as the second argument to both direct callees; type, encoding, and ownership are unknown.

## Return value meaning
not_applicable (void).

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): `CGeneralVolume__DisableLinkedEntriesByNameAndReselect` `0x00412830` ×1 (STATIC_DIRECT); `CGeneralVolume__DisableEntriesByNameAndReselect` `0x00414a40` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded; virtual dispatch may not appear as a structured direct caller.
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Calls the packet-listed +0x578 disable/reselect-labeled helper, then the packet-listed +0x57c linked disable/reselect-labeled helper, forwarding `entryName` to both. The labels describe analysis intent; this body independently proves only the ordered two-call forwarding pattern.

## Error / edge behavior
No pointer validation or rollback is visible. If the first callee mutates state and the second fails, resulting behavior is outside this packet.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040dc60`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `5317cdd59257869509c40f72b34c76e0b7240236a328780a4e3d5cfcf244f93d` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `276004d79c8f9068721627c7a2af994bfa55eb8cfabcecb06f2bc16f4332b271` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `d666fc300ce2dd4d230642cfc49d39d32ce7acf1be8823c909c284d35d2b38b5` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040dc60.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — ordered forwarding calls are explicit; all higher-level effects depend on callee contracts. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete argument/component types.
- Meaning and guarantees of re-selection.
- Failure and partial-update behavior.
