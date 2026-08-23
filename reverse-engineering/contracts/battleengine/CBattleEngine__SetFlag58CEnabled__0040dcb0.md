# CBattleEngine__SetFlag58CEnabled

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__SetFlag58CEnabled` at `0x0040dcb0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040dcb0`

## Identity
- Body `[0x0040dcb0,0x0040dcba]`, 11 bytes. Raw pristine-body SHA-256 `aac88ccb37a4df2655331f224a89213ae051d37715c820078229e3ebef65b4a7`; closure range SHA-256 `1146d8b018ff057190efa5b2778d92bcd731d76cb28508ba506c03b436e66ac5`; packet range-plus-bytes SHA-256 `7a67f95e6bfa1ccdd26d5db38623581112f912dd66e459fc3102090bb5a83980`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__SetFlag58CEnabled` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH`.

## Calling convention
`__thiscall`: receiver in ECX; no explicit stack parameters. The USER_DEFINED name does not prove the field's retail role.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__SetFlag58CEnabled(void * this)
```
- `this` — receiver whose 32-bit field at +0x58c is written.

## Return value meaning
not_applicable (void).

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): none.
- Callers (packet structured array): `IScript__EnableFlightMode` `0x00535070` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Performs exactly one visible store: `*(uint32_t *)(this+0x58c) = 1`, then returns. Calling the field a flag is a counted-name interpretation; its concrete semantics are unknown.

## Error / edge behavior
No null/alignment guard is visible. Repeated calls write the same value and have no additional visible effect in this body.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040dcb0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `1146d8b018ff057190efa5b2778d92bcd731d76cb28508ba506c03b436e66ac5` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `7a67f95e6bfa1ccdd26d5db38623581112f912dd66e459fc3102090bb5a83980` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `aac88ccb37a4df2655331f224a89213ae051d37715c820078229e3ebef65b4a7` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040dcb0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — the one store is fully visible; field meaning is unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Type and semantic role of +0x58c.
- Whether value 1 has boolean or enumerated meaning.
- How the structured caller uses the resulting state.
