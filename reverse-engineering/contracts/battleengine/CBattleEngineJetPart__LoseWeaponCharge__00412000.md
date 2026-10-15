# CBattleEngineJetPart__LoseWeaponCharge

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngineJetPart__LoseWeaponCharge` at `0x00412000`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineJetPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00412000`

## Identity
- Body `[0x00412000,0x00412043]`, 68 bytes. Raw pristine-body SHA-256 `7e57f8a521bff83e6b5d58822b275e603c96259f28b0083e529bd2810e9d04b2`; closure range SHA-256 `56be656ef7954f15baee96d5665d7748725c01325ae8ee9d5aca5f8ccd3acdd9`; packet range-plus-bytes SHA-256 `e6b44557f83ed82a5f546eb3740f80af97a63f6e3d3926d2bacb444a27b75ce0`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngineJetPart__LoseWeaponCharge` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `not_reported`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `not_reported`.

## Calling convention
`__thiscall`: receiver in ECX; no explicit stack parameters. The USER_DEFINED/source-analog name is intent evidence only.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngineJetPart__LoseWeaponCharge(void * this)
```
- `this` — list/iterator-like object: first node pointer at +0x0, mutable traversal pointer at +0x8, and target index at +0x10.

## Return value meaning
not_applicable (void).

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): none.
- Callers (packet structured array): `CBattleEngine__Move` `0x004081c0` ×1 site(s); `CBattleEngine__Morph` `0x0040a580` ×1 site(s); `CBattleEngine__AugmentWeapon` `0x0040de40` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Copies the first node pointer from +0x0 into traversal field +0x8. If the first node is null or its first 32-bit payload pointer/value is zero, returns. Otherwise it advances through each node's +0x4 next pointer, updating +0x8, until the zero-based counter equals +0x10 or a null/zero-payload node is reached. At the selected nonzero payload, writes zero to payload offset +0x60. Calling that field weapon charge/progress follows the counted name/source analog, not independent retail proof.

## Error / edge behavior
Out-of-range target indices terminate without the +0x60 store once traversal reaches a null/zero-payload node, but +0x8 remains mutated to the last reached pointer. A negative target index never equals the increasing counter before exhaustion. Cyclic lists can make the loop nonterminating; no cycle/bounds guard is visible.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00412000`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `56be656ef7954f15baee96d5665d7748725c01325ae8ee9d5aca5f8ccd3acdd9` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `e6b44557f83ed82a5f546eb3740f80af97a63f6e3d3926d2bacb444a27b75ce0` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `7e57f8a521bff83e6b5d58822b275e603c96259f28b0083e529bd2810e9d04b2` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00412000.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `not_reported`; cohort brief coverage `not_reported`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: `references/Onslaught/BattleEngineJetPart.cpp` `CBattleEngineJetPart::LoseWeaponCharge` line 769 (`SOURCE_ANALOG`) — counted/source intent only, never retail semantic proof.

## Confidence
2 — traversal, iterator-field mutation, exhaustion behavior, and final zero store are explicit; payload semantics are unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete node/payload types and ownership.
- Meaning and units/type of payload +0x60.
- Validity constraints on +0x10 and whether cyclic lists are impossible by invariant.
