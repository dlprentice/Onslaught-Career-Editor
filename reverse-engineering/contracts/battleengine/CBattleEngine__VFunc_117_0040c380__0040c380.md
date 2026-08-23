# CBattleEngine__VFunc_117_0040c380

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_117_0040c380` at `0x0040c380`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040c380`

## Identity
- Body `[0x0040c380,0x0040c39e]`, 31 bytes. Raw pristine-body SHA-256 `9ecfce2aab79a37af4dc2e9dd3fe9a462326572db058f88fd8761aab25da41c5`; closure range SHA-256 `43fbc16b92052c84a64b0274eade962356f8b74215f100f53df686268e2e6bd0`; packet range-plus-bytes SHA-256 `443036f61bf5845d9b9beb9d497447001b08c48301602921529a009ca2284198`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_117_0040c380` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof. Packet comments treat any RTTI/VFunc wording as class/slot provenance only, not behavioral proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `OPEN_EXECUTED`), closure class `PREEXISTING_GEN19_C1_OR_C2`, packet campaign confidence `CANDIDATE_CONTRACT`.

## Calling convention
`__fastcall` per packet analysis: the sole modeled argument is in ECX. The packet signature says `undefined`, while the decompile renders a void function; no source ABI claim is made.

## Prototype and parameter semantics
```c
undefined __fastcall CBattleEngine__VFunc_117_0040c380(int param_1)
```
- `param_1` — receiver/base pointer. The body reads selector +0x260 and component pointers +0x578/+0x57c.

## Return value meaning
unknown/not_determinable. The packet signature records `undefined`; the decompile returns without an explicit value and discards both callee results.

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): `CBattleEngineJetPart__GetCurrentWeapon` `0x00412610` ×1 (STATIC_DIRECT); `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded; virtual dispatch may not appear as a structured direct caller.
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
If the integer at +0x260 is not 3, it calls the packet-recorded walker-part getter on the pointer at +0x578. If the integer equals 3, it calls the packet-recorded jet-part getter on +0x57c. The result is not explicitly returned in the decompile, so any register-preservation or tail-value behavior is not claimed.

## Error / edge behavior
No receiver or component-pointer null guard is visible. Selector values other than 3 all take the +0x578 branch.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040c380`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `43fbc16b92052c84a64b0274eade962356f8b74215f100f53df686268e2e6bd0` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `443036f61bf5845d9b9beb9d497447001b08c48301602921529a009ca2284198` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `9ecfce2aab79a37af4dc2e9dd3fe9a462326572db058f88fd8761aab25da41c5` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040c380.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `PREEXISTING_GEN19_C1_OR_C2`; packet confidence `CANDIDATE_CONTRACT`; cohort brief coverage `OPEN_EXECUTED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — branch and direct dispatch targets are clear; return semantics and selector meaning are open. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Whether a callee return survives as an ABI-visible value despite the decompiler's void rendering.
- Meaning of selector value 3 and the +0x578/+0x57c components.
- Which virtual dispatch sites reach this packet-commented slot 117 target.
