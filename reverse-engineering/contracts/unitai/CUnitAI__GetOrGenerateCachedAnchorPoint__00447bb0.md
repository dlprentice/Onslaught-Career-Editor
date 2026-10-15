# CUnitAI__GetOrGenerateCachedAnchorPoint

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__GetOrGenerateCachedAnchorPoint` at `0x00447bb0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00447bb0`

## Identity
- Body `[0x00447bb0,0x00447d40]`, 401 bytes. Raw pristine-body SHA-256 `f21338e65eed5bbdd6773b3de49389192e3332b9befa6cc5ad96ad0c4e4317f5`; closure range SHA-256 `bb5e960b6a6291cbd263d5652a73b2ab7a02d1525359afd08e7ce4c925eefb4d`; packet range-plus-bytes SHA-256 `7bd01061d11204828d1aa2d5724d3666baa45b2a9b330fbc1162072b73bd2b82`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__GetOrGenerateCachedAnchorPoint` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__thiscall` for `void __thiscall CUnitAI__GetOrGenerateCachedAnchorPoint(void * this, void * outAnchorPoint)`: the receiver is modeled as `this`; explicit parameters follow the analyzed signature. Parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __thiscall CUnitAI__GetOrGenerateCachedAnchorPoint(void * this, void * outAnchorPoint)
```
- `this` — receiver/base pointer containing current values +0x1c/+0x20/+0x24 and cached fields +0x280..+0x294.
- `outAnchorPoint` — unguarded output pointer receiving four dwords copied from +0x280/+0x284/+0x288/+0x28c.

## Return value meaning
not_applicable (void); four dwords are returned through `outAnchorPoint`.

## Globals read/written
- not_applicable — no absolute data symbol is used by the displayed body.

## Callees relied on / callers
- Callees (packet structured array): `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` ×1 (STATIC_DIRECT); `CUnitAI__IsCachedAnchorPointValid` `0x00447d50` ×2 (STATIC_DIRECT).
- Callers (packet structured array): `CDropshipAI__VFunc_09_00448580` `0x00448580` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
When +0x294 is zero, it initializes +0x280/+0x284/+0x288 from +0x1c/+0x20/+0x24 and sets +0x290 when that flag was zero, then calls the packet-listed validity helper. While invalid and below 8000 attempts, it derives an angle from `attempt & 31`, builds a matrix through the packet-listed matrix helper, derives a radius from `attempt * 0.03125`, writes new +0x280/+0x284/+0x288 values, and calls the validity helper again; exhaustion clears +0x290. It always copies four cached dwords to the output pointer.

## Error / edge behavior
The output and receiver are unguarded. `local_54` and matrix-derived locals do not have fully visible initialization in the decompile, so +0x28c and generated coordinates are not_determinable at exact machine level.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00447bb0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `bb5e960b6a6291cbd263d5652a73b2ab7a02d1525359afd08e7ce4c925eefb4d` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `7bd01061d11204828d1aa2d5724d3666baa45b2a9b330fbc1162072b73bd2b82` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `f21338e65eed5bbdd6773b3de49389192e3332b9befa6cc5ad96ad0c4e4317f5` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00447bb0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — initialization, bounded search, repeated validity calls, exhaustion flag clear, and copy-out are visible, but local matrix/value provenance is incomplete. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Origin of `local_54` and exact matrix-output locals.
- Meaning of +0x294 bypass and +0x290 validity flag.
- Behavior when all 8000 candidates fail beyond the visible flag clear.
