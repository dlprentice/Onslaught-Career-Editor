# CBattleEngine__HostileEnvironment

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__HostileEnvironment` at `0x0040dce0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040dce0`

## Identity
- Body `[0x0040dce0,0x0040dd90]`, 177 bytes. Raw pristine-body SHA-256 `05a96185ddfd9faca9ad3b1e327e2a5f7a6469441f4fe017cfff4865e193180b`; closure range SHA-256 `0a8c2bdef0bcbf99d42a2fb11f66ee3840d81fc507ee32ed533dce581e9bfd65`; packet range-plus-bytes SHA-256 `999aaa0837fcd643dec308c782174e6a8ced7a1acd2ada3b01139f3cd67dc4a6`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__HostileEnvironment` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH`.

## Calling convention
`__thiscall`: receiver in ECX; no explicit stack parameters. The USER_DEFINED/source-analog name is intent evidence only.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__HostileEnvironment(void * this)
```
- `this` — receiver supplying and receiving the float at +0x510 and passed to the play-effect callee.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_00672fd0` — read as the current scalar/time-like value and copied to receiver +0x510 on every path; units are unknown.
- `s_hud__s_00623314` — format string reference (`hud\\%s`).
- `DAT_00896988` and `_DAT_008969b8` — passed to sound lookup/play calls.
- `DAT_0066f580` — address passed to the console callee.
- `s_playing_sample___hostile_environ_00623500` — log string passed to the console callee.

## Callees relied on / callers
- Callees (packet structured array): `CConsole__Printf` `0x00441740` ×1 (STATIC_DIRECT); `CSoundManager__GetEffectByName` `0x004e1910` ×1 (STATIC_DIRECT); `CSoundManager__PlayEffect` `0x004e1940` ×1 (STATIC_DIRECT); `sprintf` `0x0055de9b` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CBattleEngineJetPart__HandleSkimming` `0x00411500` ×1 site(s); `CHazard__VFunc_39_0047e710` `0x0047e710` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Computes `DAT_00672fd0 - *(float *)(this+0x510)`. If the result is greater than 5.0, it formats a stack buffer using the `hud\\%s` format as rendered, performs effect lookup and play, emits the packet-listed log string, and stores `DAT_00672fd0` to +0x510. If the result is not greater than 5.0, it still stores the global value to +0x510. Packet stringRefs also associates `hud_hostile_environment`, but the decompile omits the `%s` argument, so exact formatted selection is not_determinable.

## Error / edge behavior
Because +0x510 is updated on every call, the visible greater-than-5 gate depends on the interval since the immediately previous invocation. Equal-to-5 and unordered/NaN cases take the no-audio path. No lookup/play null checks are visible; the apparent missing variadic format argument requires disassembly review.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040dce0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `0a8c2bdef0bcbf99d42a2fb11f66ee3840d81fc507ee32ed533dce581e9bfd65` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `999aaa0837fcd643dec308c782174e6a8ced7a1acd2ada3b01139f3cd67dc4a6` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `05a96185ddfd9faca9ad3b1e327e2a5f7a6469441f4fe017cfff4865e193180b` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040dce0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: `0x00623314` = `hud\\%s`; `0x00623500` = `playing sample :  hostile environment`; `0x00623528` = `hud_hostile_environment`. String association is static evidence, not execution proof.
- Crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::HostileEnvironment` line 3269 (`SOURCE_ANALOG`) — counted/source intent only, never retail semantic proof.

## Confidence
1 — throttle/store and sound/log calls are visible, but format-argument recovery is materially ambiguous. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Units/monotonicity of `DAT_00672fd0` and whether 5.0 is a time threshold.
- Actual `%s` argument and relation to packet stringRef `hud_hostile_environment`.
- Behavior when effect lookup fails.
