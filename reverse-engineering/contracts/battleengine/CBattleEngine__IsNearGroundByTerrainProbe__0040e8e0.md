# CBattleEngine__IsNearGroundByTerrainProbe

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__IsNearGroundByTerrainProbe` at `0x0040e8e0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040e8e0`

## Identity
- Body `[0x0040e8e0,0x0040e90e]`, 47 bytes. Raw pristine-body SHA-256 `12b4873cabdcd91cb48799f30933fdfc3dde1441f3c031524815f49294a04620`; closure range SHA-256 `93a4c5c1c6c8a25ee23fb040e3a84425bf3e22386c9b1cf6215aff9dd58d9010`; packet range-plus-bytes SHA-256 `04fa658710e920aa7a5082c5d0f2544acff288f9dbd555c554d11d592c74b295`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__IsNearGroundByTerrainProbe` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `OPEN_EXECUTED`), closure class `PREEXISTING_GEN19_C1_OR_C2`, packet campaign confidence `CANDIDATE_CONTRACT`.

## Calling convention
`__fastcall` per packet signature: the sole modeled `unit` pointer is in ECX. The USER_DEFINED name is not proof that the numeric result is boolean.

## Prototype and parameter semantics
```c
float __fastcall CBattleEngine__IsNearGroundByTerrainProbe(void * unit)
```
- `unit` — base pointer; `unit+0x1c` is passed to the sampler and float +0x24 is compared with the sampled result minus 2.0. Concrete layout and units are unknown.

## Return value meaning
Returns float `5.0` when `sampled_value - 2.0 < *(float *)(unit+0x24)`; otherwise returns float `0.0`. This is not a C boolean return in the packet signature.

## Globals read/written
- `DAT_006fadc8` — its address is passed as the first argument to the packet-listed sampler.

## Callees relied on / callers
- Callees (packet structured array): `CStaticShadows__SampleShadowHeightBilinear` `0x0047eb80` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded; virtual dispatch may not appear as a structured direct caller.
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Samples a double through the packet-listed helper using the global object and `unit+0x1c`. Compares the sample minus 2.0 against the unit float at +0x24, returning 5.0 for a strict less-than result and 0.0 otherwise. Terrain/ground terminology is inferred from counted names, not independently proven.

## Error / edge behavior
`unit` is not null-guarded. Equality returns 0.0. An unordered comparison (NaN) also follows the false branch in the rendered logic. Units of 2.0 and 5.0 are unknown.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040e8e0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `93a4c5c1c6c8a25ee23fb040e3a84425bf3e22386c9b1cf6215aff9dd58d9010` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `04fa658710e920aa7a5082c5d0f2544acff288f9dbd555c554d11d592c74b295` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `12b4873cabdcd91cb48799f30933fdfc3dde1441f3c031524815f49294a04620` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040e8e0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `PREEXISTING_GEN19_C1_OR_C2`; packet confidence `CANDIDATE_CONTRACT`; cohort brief coverage `OPEN_EXECUTED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — sampler call, strict comparison, and constants are explicit; domain meaning and units are unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Units and meanings of sampled value, +0x24, 2.0 threshold, and 5.0 return.
- Whether consumers treat 5.0 as a weight, duration, distance, or truthy sentinel.
- Nullability/alignment requirements of `unit`.
