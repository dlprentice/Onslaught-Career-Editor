# CBattleEngine__VFunc_16_0040df80

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_16_0040df80` at `0x0040df80`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040df80`

## Identity
- Body `[0x0040df80,0x0040df9b]`, 28 bytes. Raw pristine-body SHA-256 `4beda4e28ebc6756257a2af340b318d2e068dff27ab334290a63020f6f8007fd`; closure range SHA-256 `c5b3ed02551179d24e757ef993bc96f9f0c852008a69cf87ccde5775656d7d2e`; packet range-plus-bytes SHA-256 `208414cd7dc8934ecf9903bb1ee72c20968d923aa1880e4faffc4bd079e39fd4`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_16_0040df80` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof. Packet comments treat any RTTI/VFunc wording as class/slot provenance only, not behavioral proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `OPEN_EXECUTED`), closure class `PREEXISTING_GEN19_C1_OR_C2`, packet campaign confidence `CANDIDATE_CONTRACT`.

## Calling convention
`__stdcall` per packet analysis, with no explicit parameters. Although named as a CBattleEngine virtual slot, the analyzed signature does not model a receiver; slot provenance is not behavior proof.

## Prototype and parameter semantics
```c
float10 __stdcall CBattleEngine__VFunc_16_0040df80(void)
```
- No explicit parameters in the packet signature. Any implicit receiver preservation/use is not present in the decompile.

## Return value meaning
Returns x87 `1.0` when the packet-listed multiplayer predicate returns nonzero; otherwise returns x87 `0.4`. Units and semantic role are unknown.

## Globals read/written
- `DAT_008a9a98` — its address is passed to the packet-listed multiplayer predicate.

## Callees relied on / callers
- Callees (packet structured array): `CGame__IsMultiplayer` `0x004725d0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded; virtual dispatch may not appear as a structured direct caller.
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Calls the packet-listed multiplayer predicate on the global object. It maps nonzero to 1.0 and zero to 0.4. No other branch or state access is visible.

## Error / edge behavior
All nonzero predicate results take the 1.0 branch. Error/sentinel behavior of the predicate is unknown. No runtime evidence establishes how the returned scalar is consumed.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040df80`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `c5b3ed02551179d24e757ef993bc96f9f0c852008a69cf87ccde5775656d7d2e` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `208414cd7dc8934ecf9903bb1ee72c20968d923aa1880e4faffc4bd079e39fd4` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `4beda4e28ebc6756257a2af340b318d2e068dff27ab334290a63020f6f8007fd` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040df80.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `PREEXISTING_GEN19_C1_OR_C2`; packet confidence `CANDIDATE_CONTRACT`; cohort brief coverage `OPEN_EXECUTED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — callee test and both constants are fully visible; returned scalar meaning is unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Semantic meaning and units of the 1.0/0.4 scalar.
- Why the packet signature is `__stdcall` with no receiver for a VFunc-labeled target.
- Virtual callers/consumers, absent from structured caller data.
