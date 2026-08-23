# CUnitAI__RefreshGridCooldownFromOccupiedCells

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__RefreshGridCooldownFromOccupiedCells` at `0x0040dda0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040dda0`

## Identity
- Body `[0x0040dda0,0x0040de3e]`, 159 bytes. Raw pristine-body SHA-256 `67b966529e14a35d2fb1fbf3f428e331d849c7ec36207cdcbec87391c44db44f`; closure range SHA-256 `5e368a119a021e1a6e0cb55b92ccec61afa77852da725b9072d94834f6904bc5`; packet range-plus-bytes SHA-256 `ef4d31c4d11b0feb73b8c842d41650d8abd2aebcf5bb2fba70e0037c9d4af75e`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__RefreshGridCooldownFromOccupiedCells` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__thiscall` for `void __thiscall CUnitAI__RefreshGridCooldownFromOccupiedCells(void * this)`: the receiver is modeled as `this`; explicit parameters follow the analyzed signature. Parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __thiscall CUnitAI__RefreshGridCooldownFromOccupiedCells(void * this)
```
- `this` — receiver/base pointer read at +0x1c/+0x20/+0x24/+0x28 and +0x2e8, and used for an indirect slot +0x10c call.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_00672fd0` — read in the threshold comparison and stored to receiver +0x2e8.
- `DAT_008a9d7c` and `DAT_008a9d80` — each passed as the first argument to one occupancy-query call.

## Callees relied on / callers
- Callees (packet structured array): `CFearGrid__GetOccupancyAtWorldVector` `0x0044c720` ×2 (STATIC_DIRECT).
- Callers (packet structured array): `CHud__RoutePanel_T4_00485d50` `0x00485d50` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
If the float at +0x2e8 is below `DAT_00672fd0 - 8.0` and indirect slot +0x10c returns nonzero, the body calls the one packet-listed direct callee twice with the two globals and receiver floats +0x1c/+0x20/+0x24/+0x28. It stores `DAT_00672fd0` at +0x2e8 when either result is nonzero. The counted names suggest grid occupancy and cooldown intent, but do not prove those roles.

## Error / edge behavior
The receiver and indirect vtable access are unguarded. No write occurs when either outer gate fails or both direct-call results are zero; runtime meaning of the values is not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040dda0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `5e368a119a021e1a6e0cb55b92ccec61afa77852da725b9072d94834f6904bc5` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `ef4d31c4d11b0feb73b8c842d41650d8abd2aebcf5bb2fba70e0037c9d4af75e` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `67b966529e14a35d2fb1fbf3f428e331d849c7ec36207cdcbec87391c44db44f` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040dda0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — threshold, two direct calls, OR test, and final store are explicit; field/global meanings and the indirect predicate remain unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meaning and units of +0x2e8 and `DAT_00672fd0`.
- Contract of indirect slot +0x10c and concrete types of the four forwarded floats.
