# CBattleEngine__CountFlag9CBySelectionMode

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__CountFlag9CBySelectionMode` at `0x0040dc90`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040dc90`

## Identity
- Body `[0x0040dc90,0x0040dcae]`, 31 bytes. Raw pristine-body SHA-256 `72b3f37b257b58dc1a06d7ea45decbe34d7190f2ded07035e13e7ef5dcb64b8a`; closure range SHA-256 `0cdf8b7e4fcaeb307e898f21985b9c0ce5a63213719498660a7e013fd1f04636`; packet range-plus-bytes SHA-256 `7263539599ba5d03fcf871e4f6afd5b2e86e1a9576ebf5440582f1d22b1c2b82`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__CountFlag9CBySelectionMode` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH`.

## Calling convention
`__thiscall`: receiver in ECX and no explicit stack parameters. The return is modeled as a 32-bit integer.

## Prototype and parameter semantics
```c
int __thiscall CBattleEngine__CountFlag9CBySelectionMode(void * this)
```
- `this` — receiver whose selector at +0x260 chooses between component pointers +0x57c and +0x578.

## Return value meaning
Returns the integer produced by the selected direct callee. Interpreting it as a count follows counted callee/function labels and is not independently established here.

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): `LinkedObjectList__CountFlag9C` `0x004129a0` ×1 (STATIC_DIRECT); `CGeneralVolume__CountEnabledEntriesIncludingPrimary` `0x00414b70` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CHud__RoutePanel_T4_00485d50` `0x00485d50` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
When `*(int *)(this+0x260) == 3`, calls the packet-listed helper on the pointer at +0x57c and returns its result. For every other selector value, calls the packet-listed helper on +0x578 and returns its result.

## Error / edge behavior
No null checks protect either selected component pointer. Selector values outside known states all use the +0x578 branch. Callee overflow/error sentinels are unknown.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040dc90`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `0cdf8b7e4fcaeb307e898f21985b9c0ce5a63213719498660a7e013fd1f04636` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `7263539599ba5d03fcf871e4f6afd5b2e86e1a9576ebf5440582f1d22b1c2b82` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `72b3f37b257b58dc1a06d7ea45decbe34d7190f2ded07035e13e7ef5dcb64b8a` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040dc90.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — selector branch and returned callee values are explicit; integer meaning and selector semantics are name-dependent. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meaning of selector 3 and component roles.
- Exact return-domain/error contract of both callees.
- Whether the two callee results are semantically comparable.
