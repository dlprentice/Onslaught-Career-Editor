# CBattleEngine__HandleCloak

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__HandleCloak` at `0x0040d4d0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040d4d0`

## Identity
- Body `[0x0040d4d0,0x0040d528]`, 89 bytes. Raw pristine-body SHA-256 `8fc8ab6eb863969d1da942a9f078ad55600f08b32e16440ae3852479e3e9c327`; closure range SHA-256 `e95488856d2d3c1913719ead1e6d5a76bb3edd053d3938799efaa0ec428e42c0`; packet range-plus-bytes SHA-256 `8b1d2bf31fe2f5010a8b44ad56a33b5e9177ddfe7579f1619eff1c2a59bdf713`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__HandleCloak` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH`.

## Calling convention
`__thiscall`: receiver in ECX; no explicit stack parameters. The USER_DEFINED function name is source/counting intent only.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__HandleCloak(void * this)
```
- `this` — receiver with fields at +0x4ac, +0x4b0, +0x5dc, and +0xfc.

## Return value meaning
not_applicable (void).

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): none.
- Callers (packet structured array): `CPlayer__ReceiveButtonAction` `0x004d3110` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
If +0x4ac is nonzero, the function writes zero to +0x5dc and +0x4ac and returns. Otherwise it reads the pointer at +0x4b0 and, only when nested float +0x2c is less than or equal to receiver float +0xfc and nested float +0xa0 is positive, writes 1 to +0x4ac and copies the +0xa0 bit pattern to +0x5dc. The `HandleCloak` label/source analog suggests intent but does not prove retail field terminology.

## Error / edge behavior
The +0x4b0 pointer is dereferenced without a null guard on the activation path. If either floating comparison is false or unordered, no stores occur. Units/ranges are unknown.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040d4d0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `e95488856d2d3c1913719ead1e6d5a76bb3edd053d3938799efaa0ec428e42c0` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `8b1d2bf31fe2f5010a8b44ad56a33b5e9177ddfe7579f1619eff1c2a59bdf713` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `8fc8ab6eb863969d1da942a9f078ad55600f08b32e16440ae3852479e3e9c327` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040d4d0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::HandleCloak` line 3096 (`SOURCE_ANALOG`) — counted/source intent only, never retail semantic proof.

## Confidence
2 — two-state branch, comparisons, and stores are explicit; field meanings and units are unproven. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete meanings/types of +0x4ac and +0x5dc.
- Units and relationship of nested +0x2c, receiver +0xfc, and nested +0xa0.
- Whether +0x4b0 may be null.
