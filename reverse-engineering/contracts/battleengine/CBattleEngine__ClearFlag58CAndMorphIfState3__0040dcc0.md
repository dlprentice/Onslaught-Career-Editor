# CBattleEngine__ClearFlag58CAndMorphIfState3

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__ClearFlag58CAndMorphIfState3` at `0x0040dcc0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040dcc0`

## Identity
- Body `[0x0040dcc0,0x0040dcda]`, 27 bytes. Raw pristine-body SHA-256 `8f8f3f6b404bcb373d433cbdc7a2f2006bc536f1e28c87d4802d0d9419d84ec6`; closure range SHA-256 `99101b557997018bc7a9c3251840034d243d89a04dc76f96ae29f0158b502b98`; packet range-plus-bytes SHA-256 `92ece5d99599d626b180617e7ff31bdb2db7a939277424488fa2f261d731b961`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__ClearFlag58CAndMorphIfState3` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH`.

## Calling convention
`__thiscall`: receiver in ECX; no explicit stack parameters. USER_DEFINED names are intent only.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__ClearFlag58CAndMorphIfState3(void * this)
```
- `this` — receiver whose +0x58c field is cleared and whose +0x260 field gates the direct call.

## Return value meaning
not_applicable (void).

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): `CBattleEngine__Morph` `0x0040a580` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `IScript__DisableFlightMode` `0x00535090` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Writes zero to the 32-bit field at +0x58c. If the 32-bit field at +0x260 equals 3, calls the packet-listed morph-labeled function with the same receiver; otherwise returns immediately. The labels do not independently prove flight/morph semantics.

## Error / edge behavior
The clear occurs for all selector values, before the conditional call. No receiver validation or callee-failure handling is visible.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040dcc0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `99101b557997018bc7a9c3251840034d243d89a04dc76f96ae29f0158b502b98` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `92ece5d99599d626b180617e7ff31bdb2db7a939277424488fa2f261d731b961` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `8f8f3f6b404bcb373d433cbdc7a2f2006bc536f1e28c87d4802d0d9419d84ec6` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040dcc0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — unconditional clear and selector-gated call are explicit; state meanings are unproven. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meanings of +0x58c and selector value 3.
- Full effects/preconditions of the direct callee.
- Whether the caller expects synchronous completion.
