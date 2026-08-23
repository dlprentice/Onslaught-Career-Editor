# CBattleEngine__VFunc_36_0040d530

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_36_0040d530` at `0x0040d530`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040d530`

## Identity
- Body `[0x0040d530,0x0040d5ad]`, 126 bytes. Raw pristine-body SHA-256 `28233a69e57ff17b3ceacec88e8122c0afeb5e650d0fcc96beb4c4b22c62d7a4`; closure range SHA-256 `32e26665af089e4bebd6d6752ff4c7d9a5d98b71479bc9a5c023acfbd250acbd`; packet range-plus-bytes SHA-256 `2caffc71012dd82cb869c740bd3d7c881493ef605f2fd383469f8efdb938ed72`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_36_0040d530` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof. Packet comments treat any RTTI/VFunc wording as class/slot provenance only, not behavioral proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
`__thiscall`: receiver in ECX and one explicit unsigned integer stack argument. Slot ownership/name is analysis provenance only.

## Prototype and parameter semantics
```c
undefined __thiscall CBattleEngine__VFunc_36_0040d530(void * this, uint param_1)
```
- `this` — receiver/base used for fields +0x5d8, +0x574, and +0x524 and passed to the render callee.
- `param_1` — unsigned value forwarded to the render callee; bit 0x40 is ORed into the local copy when +0x5d8 is positive. Its source-level flag type is unknown.

## Return value meaning
not_applicable in the packet/decompile (void).

## Globals read/written
- `DAT_0063012c` — written to a rounded value derived from +0x5d8 on one path, then unconditionally reset to 0xff before return.
- `DAT_0089ce4c` — read in the render-suppression condition.

## Callees relied on / callers
- Callees (packet structured array): `CThing__Render` `0x004f36d0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded; virtual dispatch may not appear as a structured direct caller.
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
When receiver float +0x5d8 is positive, computes `ROUND(255.0 - value*2.55)`, writes it to `DAT_0063012c`, and ORs 0x40 into `param_1`. It calls the packet-listed render function unless all three suppression predicates hold: nested `[[this+0x574]+0x24] == 1`, receiver +0x524 is not 1, and `[[this+0x574]+0x2c]-1 == DAT_0089ce4c`. It then writes 0xff to `DAT_0063012c` on every visible path.

## Error / edge behavior
The +0x574 pointer is dereferenced without a null guard. No clamp surrounds the rounded expression, so values outside an expected range, infinities, or NaNs have effects not_determinable from the decompile. The global reset occurs even when rendering is suppressed.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040d530`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `32e26665af089e4bebd6d6752ff4c7d9a5d98b71479bc9a5c023acfbd250acbd` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `2caffc71012dd82cb869c740bd3d7c881493ef605f2fd383469f8efdb938ed72` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `28233a69e57ff17b3ceacec88e8122c0afeb5e650d0fcc96beb4c4b22c62d7a4` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040d530.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — global modulation, flag change, suppression condition, render call, and reset are explicit; semantic meaning is open. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Role/range of +0x5d8 and `DAT_0063012c`.
- Meaning of parameter mask bit 0x40 and suppression fields/global.
- Conversion behavior for out-of-range or NaN floating values at the machine-instruction level.
