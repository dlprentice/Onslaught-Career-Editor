# CBattleEngine__UpdateConfiguration

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__UpdateConfiguration` at `0x0040c650`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040c650`

## Identity
- Body `[0x0040c650,0x0040c710]`, 193 bytes. Raw pristine-body SHA-256 `c9b972544882212d5610222edf14c5b939cee9b1f24f98c46c03d025bc5a6cdd`; closure range SHA-256 `dfea3e996c97cb3e1e612f56df252dc3f54156e4f877121f52c326857c622df3`; packet range-plus-bytes SHA-256 `0c77ef8863d571bc401535b119e7ab8faa0563b126471dcf0faf92cf24e2853e`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__UpdateConfiguration` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH`.

## Calling convention
`__thiscall`: receiver in ECX and no explicit stack parameters in the packet signature. The USER_DEFINED name/signature are counted analysis intent only.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__UpdateConfiguration(void * this)
```
- `this` — receiver containing an identifier at +0x600, a cached pointer at +0x4b0, component pointers at +0x57c/+0x578, and six adjacent records beginning at +0x52c.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_0066f580` — its address is passed to the packet-listed console function; the body does not visibly write it.

## Callees relied on / callers
- Callees (packet structured array): `BattleEngineConfigurations__GetConfiguration` `0x0040f2f0` ×1 (STATIC_DIRECT); `CBattleEngineJetPart__ResetConfiguration` `0x00412650` ×1 (STATIC_DIRECT); `CBattleEngineWalkerPart__ResetConfiguration` `0x004146b0` ×1 (STATIC_DIRECT); `CConsole__Printf` `0x00441740` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CBattleEngine__Init` `0x00404dd0` ×1 site(s); `FUN_00429ad0` `0x00429ad0` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Calls the configuration lookup with the integer at +0x600. If the returned pointer equals cached +0x4b0, the function does nothing further. If different, it caches the new pointer, copies nested offsets +0x20 and +0x1c to receiver +0xfc and +0xf8, conditionally calls reset helpers for non-null +0x57c and +0x578 components, then processes six adjacent records. For each record it clears relative element 6, copies a configuration-derived integer to relative element 12, and stores either a configuration-derived value or zero in the current element depending on whether that integer is zero. Finally it passes the pointer at returned-object +0xa8 to the console callee. Labels such as configuration/energy/life in packet comments or source analogs are not used as proof of field meaning.

## Error / edge behavior
There is no null check on the lookup result before dereferencing it when it differs from the cached pointer. Component reset calls are individually null-gated. Exact behavior if configuration-derived addresses alias receiver storage is not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040c650`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `dfea3e996c97cb3e1e612f56df252dc3f54156e4f877121f52c326857c622df3` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `0c77ef8863d571bc401535b119e7ab8faa0563b126471dcf0faf92cf24e2853e` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `c9b972544882212d5610222edf14c5b939cee9b1f24f98c46c03d025bc5a6cdd` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040c650.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::UpdateConfiguration` line 2906 (`SOURCE_ANALOG`) — counted/source intent only, never retail semantic proof.

## Confidence
2 — cache-change gate, copies, component resets, and six-record refresh are visible; field meanings remain unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Whether the lookup can return null and, if so, whether that is an invalid state.
- Meanings/types of +0xf8, +0xfc, and the six record arrays.
- Format contract of the final console call and meaning of returned-object +0xa8.
