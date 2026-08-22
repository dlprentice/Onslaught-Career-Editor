# CBattleEngine__VFunc_48_0040dfa0

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_48_0040dfa0` at `0x0040dfa0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040dfa0`

## Identity
- Body `[0x0040dfa0,0x0040dfa6]`, 7 bytes. Raw pristine-body SHA-256 `0a7b589fe9e69fa675067cff301bbbb52463f69d2be70b9d7d33b16ece62f1c9`; closure range SHA-256 `ba6cd7b0fa1b16e40b6d95dfa953f9cfed3c6cc03c3c6cbfdb47fed30e99e770`; packet range-plus-bytes SHA-256 `c4c383fad7395f1b6d2f693bb87618e4ab55059f034e77362291e00f868869fc`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_48_0040dfa0` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof. Packet comments treat any RTTI/VFunc wording as class/slot provenance only, not behavioral proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
`__stdcall` per packet analysis, with no explicit parameters. RTTI/VFunc provenance is class/slot evidence only.

## Prototype and parameter semantics
```c
float10 __stdcall CBattleEngine__VFunc_48_0040dfa0(void)
```
- No explicit parameters are modeled or referenced.

## Return value meaning
Returns the x87 constant `1.9`; units and semantic meaning are unknown.

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): none.
- Callers (packet structured array): none recorded; virtual dispatch may not appear as a structured direct caller.
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Single constant return of 1.9. No receiver, branch, call, or state access is visible in the decompile.

## Error / edge behavior
No input-dependent edge cases exist in the visible body. How callers interpret or round 1.9 is outside this packet.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040dfa0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `ba6cd7b0fa1b16e40b6d95dfa953f9cfed3c6cc03c3c6cbfdb47fed30e99e770` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `c4c383fad7395f1b6d2f693bb87618e4ab55059f034e77362291e00f868869fc` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `0a7b589fe9e69fa675067cff301bbbb52463f69d2be70b9d7d33b16ece62f1c9` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040dfa0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — the constant-return mechanics are complete; semantic meaning is entirely open. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meaning and units of 1.9.
- Why the analyzed virtual-slot target has a no-parameter `__stdcall` signature.
- Which virtual call sites consume the value.
