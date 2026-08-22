# CBattleEngine__RandomizeOffsets4B8_4C0

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__RandomizeOffsets4B8_4C0` at `0x00407940`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00407940`

## Identity
- Body `[0x00407940,0x00407a42]`, 259 bytes. Raw pristine-body SHA-256 `25d91776f1c292df959df7ff23bf0237a03369f8b18381d4ee71904a7e8cdc45`; closure range SHA-256 `19e281b3fe230ff8e0c8c615624cc66271a7352c79699845feb968da38fb2c83`; packet range-plus-bytes SHA-256 `30180def0ded184bbf2ef0292c0fa1213ca2c4e98ca9dff0e9eafc9eb994c275`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__RandomizeOffsets4B8_4C0` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol. Packet comment flags ownership naming debt (CGeneralVolume__ unproven); rename applied in a prior wave.
- Campaign grade: C1_CANDIDATE_PARTIAL (PARTIAL), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence MEDIUM_STATIC).

## Calling convention
`__thiscall`: `this` in ECX, one float stack argument (packet comment: RET 0x4).

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__RandomizeOffsets4B8_4C0(void * this, float offsetRange)
```
- `offsetRange` — spread magnitude; clamped to at most 0.75, ignored entirely when below 0.001:
```c
if (0.001 <= offsetRange) {
  if (0.75 < offsetRange) { offsetRange = 0.75; }
  fVar1 = 16.0 / offsetRange;
```
Used both directly and as `16/offsetRange` divisor for the random draws.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_008a9d9c` — read; argument to `Random__NextLCGAbs` ×3 (RNG state/context by call shape).
- `DAT_0088a0a8` — read; first argument to `CFrontEndPage__Process_NoOp`.

## Callees relied on / callers
Callees (packet): `Random__NextLCGAbs` 0x004de8d0 ×3, `CGeneralVolume__InitRandomizedVelocityOffsets` 0x004247a0 ×1, `CFrontEndPage__Process_NoOp` 0x00452b60 ×1 — STATIC_DIRECT; counted names.
Callers (packet): `CBattleEngine__Damage` 0x0040a890 ×1, `CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange` 0x0040c340 ×1.

## Behavior summary
When `offsetRange >= 0.001` (clamped to ≤0.75):
1. Draws three LCG randoms (`Random__NextLCGAbs(DAT_008a9d9c)`), each masked/modulo-32'd
   (`& 0x8000001f` with signed fixup -> value in [0,31]), then stores
   `(float)draw / (16/range) - range` into `+0x4b8`, `+0x4bc`, `+0x4c0` respectively. For a
   non-negative draw 0..31 this expression spans exactly `[-range, 15*range/16]`.
2. Zeroes `+0x4c4`.
3. If `+0x528` non-null: `CGeneralVolume__InitRandomizedVelocityOffsets(*(this+0x528), (int)offsetRange)`.
4. `CFrontEndPage__Process_NoOp(&DAT_0088a0a8, *(int*)(*(int*)(this+0x574)+0x2c) - 1)` (player index minus one by shape).
Below the threshold, the function does nothing.

## Error / edge behavior
Threshold guard skips all work for tiny ranges; clamp bounds large ranges. Unguarded deref of `*(this+0x574)` in step 4 — NULL behavior not_determinable from this body.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00407940; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `19e281b3fe230ff8e0c8c615624cc66271a7352c79699845feb968da38fb2c83` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `30180def0ded184bbf2ef0292c0fa1213ca2c4e98ca9dff0e9eafc9eb994c275` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `25d91776f1c292df959df7ff23bf0237a03369f8b18381d4ee71904a7e8cdc45` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00407940.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence PARTIAL).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — arithmetic fully visible and reproducible; but the purpose of the three randomized fields, their units, and the front-end no-op call's effect are partial (PARTIAL closure).

## Unresolved questions
- What consumes +0x4b8/+0x4bc/+0x4c0/+0x4c4; why the [0,31] draw quantization; what Process_NoOp actually does despite its name.
