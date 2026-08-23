# CBattleEngine__VFunc_68_0040c750

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_68_0040c750` at `0x0040c750`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040c750`

## Identity
- Body `[0x0040c750,0x0040c983]`, 564 bytes. Raw pristine-body SHA-256 `312066f6ffdcaf54ee835b4bfd7d962f8ce0a9d4386b653f1fb1b33deef84711`; closure range SHA-256 `1142f1488284a46954dca52d985922a56fe93514910dfa880e5fe2b92cc182a5`; packet range-plus-bytes SHA-256 `5073de2fa9cf4f1fc7a6a8dd7c306d3e043935fc0895bae3cc0185d283befcfe`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_68_0040c750` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof. Packet comments treat any RTTI/VFunc wording as class/slot provenance only, not behavioral proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
`__fastcall` per packet analysis: `param_1` is passed in ECX. The function is modeled void; the RTTI-derived VFunc name asserts class/slot provenance only.

## Prototype and parameter semantics
```c
undefined __fastcall CBattleEngine__VFunc_68_0040c750(int * param_1)
```
- `param_1` — receiver/base pointer used as an integer array and byte-addressed object. The body accesses +0x1c, +0x2c, +0x7c/+0x80/+0x84, +0x260, and nested +0x578 state.

## Return value meaning
not_applicable in the analyzed signature/decompile (void).

## Globals read/written
- `DAT_006fadc8` — its address is passed to the packet-listed heightfield-normal sampler.

## Callees relied on / callers
- Callees (packet structured array): `ElapsedTime__BelowThreshold_D4` `0x00401fd0` ×1 (STATIC_DIRECT); `CActor__SetFieldCcToNow_00402000` `0x00402000` ×1 (STATIC_DIRECT); `CBattleEngine__SwapPrimarySecondaryPartReadersForState` `0x00406460` ×1 (STATIC_DIRECT); `CGeneralVolume__SpawnPickupAndDispatch` `0x0040dfb0` ×1 (STATIC_DIRECT); `CMonitor__SampleHeightfieldNormalAtXY` `0x0047ec60` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded; virtual dispatch may not appear as a structured direct caller.
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
First calls the packet-listed reader-swap and +0xcc-time helpers. If bit 2 of the byte at +0x2c is set, it calls the packet-listed dispatch helper, invokes an indirect vtable slot at +0x38, and returns. Otherwise it continues only when the elapsed-time predicate returns false. A magnitude threshold is 0.2 normally and 0.4 when +0x260 equals 2; that state also has an additional nested +0x578/+0x44 early-return gate. For squared magnitude of the three floats at +0x7c/+0x80/+0x84 above the threshold squared, it samples and normalizes a vector, normalizes the three-float vector, forms a dot product, and invokes indirect slots +0xa0 and +0x70 with derived values. If magnitude is not above the threshold and +0x260 equals 3, it scales those three floats by 0.9 and passes the vector to indirect slot +0x70. High-level gameplay effects are unknown.

## Error / edge behavior
Numerous receiver/nested-pointer dereferences are unguarded. Zero-length vectors skip reciprocal normalization. The decompile exposes `extraout_var` in the boolean test and `stack0xffffffd0` in an indirect call; their exact machine-level interpretation requires disassembly review and is not_determinable here.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040c750`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `1142f1488284a46954dca52d985922a56fe93514910dfa880e5fe2b92cc182a5` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `5073de2fa9cf4f1fc7a6a8dd7c306d3e043935fc0895bae3cc0185d283befcfe` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `312066f6ffdcaf54ee835b4bfd7d962f8ce0a9d4386b653f1fb1b33deef84711` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040c750.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — major branch/math structure is visible, but decompiler temporaries and indirect targets leave material ambiguity. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Targets/contracts of indirect vtable slots +0x38, +0x70, and +0xa0.
- Exact meaning of the bit gate, elapsed predicate, state values 2/3, and vector fields.
- Machine-level interpretation of `extraout_var` and `stack0xffffffd0`.
