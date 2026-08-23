# CBattleEngine__PlayHudSampleByName

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__PlayHudSampleByName` at `0x0040d5f0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040d5f0`

## Identity
- Body `[0x0040d5f0,0x0040d658]`, 105 bytes. Raw pristine-body SHA-256 `fb06ce27b2d2c7ff98fd953ac3786007911fe03e2233cbe25706752617e0136e`; closure range SHA-256 `63cc8f83b51159730ee4990b1d2a575de6f0df8c3564f53cf90c239a7a7776cd`; packet range-plus-bytes SHA-256 `d03e49a7f4c6a13a3f34b8d4f2cee6b03f32182498952b3dd87ce6b117c9ba06`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__PlayHudSampleByName` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH`.

## Calling convention
`__thiscall`: receiver in ECX and one explicit pointer argument on the stack. Although the packet names it `sampleName`, the rendered decompile does not consume that parameter.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__PlayHudSampleByName(void * this, char * sampleName)
```
- `this` — forwarded to the packet-listed play-effect call.
- `sampleName` — packet-modeled `char *`; it is not visibly referenced in the decompile. Whether a decompiler omission hides its use is unknown.

## Return value meaning
not_applicable (void).

## Globals read/written
- `s_hud__s_00623314` — format-string address referenced (`hud\\%s`).
- `DAT_00896988` — global sound-manager object/address passed to both sound callees.
- `_DAT_008969b8` — value passed to the play-effect callee.

## Callees relied on / callers
- Callees (packet structured array): `CSoundManager__GetEffectByName` `0x004e1910` ×1 (STATIC_DIRECT); `CSoundManager__PlayEffect` `0x004e1940` ×1 (STATIC_DIRECT); `sprintf` `0x0055de9b` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CBattleEngine__ChangeWeapon` `0x00409f70` ×3 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
The rendered decompile calls `sprintf(local_100, s_hud__s_00623314)` into a 256-byte stack buffer, resolves that buffer through the packet-listed effect lookup, then passes the resulting pointer and fixed arguments to the packet-listed play call. Packet stringRefs contains `hud\\%s`, but the decompile omits a `%s` substitution argument and does not reference `sampleName`; therefore the actual formatted name and parameter use are not_determinable from this packet alone.

## Error / edge behavior
No null/error checks are visible for the argument, formatting result, effect lookup result, or sound manager. The apparent missing variadic argument would be undefined behavior if literal; disassembly/call-site recovery is required before asserting that interpretation.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040d5f0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `63cc8f83b51159730ee4990b1d2a575de6f0df8c3564f53cf90c239a7a7776cd` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `d03e49a7f4c6a13a3f34b8d4f2cee6b03f32182498952b3dd87ce6b117c9ba06` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `fb06ce27b2d2c7ff98fd953ac3786007911fe03e2233cbe25706752617e0136e` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040d5f0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: `0x00623314` = `hud\\%s`. String association is static evidence, not execution proof.
- Crosswalk: none in the cohort brief.

## Confidence
1 — lookup/play call sequence is visible, but the decompile's missing format argument makes the core name construction ambiguous. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Whether `sampleName` is actually pushed for `sprintf` and omitted by decompiler recovery.
- Exact formatted effect name and buffer-safety contract.
- Behavior when lookup returns null.
