# PC demo/retail multi-range body closure

Status: complete, bounded cross-build correction
Last updated: 2026-08-11
Evidence: MEASURED — exact specimen hashes, the existing independently mapped
retail/demo entries, exact current Ghidra body ranges, complete exported retail
instruction rows, fresh x86-32 decode on both specimens, and normalized
instruction comparison; UNKNOWN — semantic equality of masked address targets,
runtime equivalence, source equivalence, and the ten mapped bodies that remain
genuinely different or incompletely explained.
Verdict: forty functions previously left in the changed/incompletely-bounded
queue are exact cross-build instruction-shape matches when their real
non-contiguous Ghidra bodies are compared. The correction covers 128 body
ranges, 24,813 body bytes, and 7,602 instructions with zero normalized
instruction differences. It reduces the unresolved address-mapped queue from
50 to 10 without guessing a name, body boundary, or behavior.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
paired PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

Exact sizes:

- pristine PC retail `BEA.exe`: 2,506,752 bytes;
- PC demo `BEA.exe`: 2,510,848 bytes.

The promoted row receipt is
[`pc-demo-retail-multirange-closure-2026-08-11.tsv`](pc-demo-retail-multirange-closure-2026-08-11.tsv),
9,777 bytes, SHA-256
`e8a9a71520ebc4b3b01d1f0faa6cd0033170917600a0801cdbf133042e4bdabb`.

## Why the first comparison abstained

The original 8,086-entry map deliberately accepted a normalized-identical body
only when it could compare the function as one contiguous stream. That was a
safe first gate, but forty of the remaining rows have between 2 and 21 Ghidra
body ranges. Their bodies contain compiler/runtime fragments or exclude bytes
after no-return transfers; treating the outer address interval as the body
would compare bytes that Ghidra does not assign to the function.

This was an instrument limitation, not evidence that the forty functions had
changed. Two earlier text-core rows exposed the same class of false negative.
The present batch corrects every other multi-range row in the then-unresolved
address-mapped queue at once rather than inspecting them one at a time.

## Method

The ignored reproducer is
`local-lab/pc-demo-retail-multirange-closure-20260811-v1/analyze.py`, 8,324
bytes, SHA-256
`70d986b64ff1b9f9af2300f181c2836c70034de45d388f67e1a06182067e1d1e`.
It performs these bounded steps:

1. Verify both executable SHA-256 values before reading bytes.
2. Select rows whose demo entry was already independently fixed by the
   whole-function map, whose old comparison was false, whose retail Ghidra body
   has more than one range, and which were not already closed by the fifteen
   earlier semantic reports.
3. Require exactly forty selected functions.
4. Reassemble each retail body from every exported instruction row in Ghidra
   ordinal order. Require both the exported instruction count and the sum of
   instruction bytes to equal the current full-inventory facts.
5. Translate every actual retail instruction address by the independently
   mapped function-entry delta, read the same number of bytes from the demo,
   and require each side to decode as exactly one complete x86-32 instruction.
6. Compare mnemonic and encoded instruction bytes after zeroing only the
   Capstone-reported immediate and displacement fields.
7. Fail the run if any normalized instruction differs.

The resulting `result.json` is 611 bytes, SHA-256
`817506564f793370efeaad5320a54072243a2d0b20f4dda1e4aa7f5c794d1f52`.
The tracked TSV was compared byte-for-byte with the generated TSV before
promotion.

## Result

| Measure | Result |
| --- | ---: |
| Functions | 40 |
| Ghidra body ranges | 128 |
| Retail body/instruction bytes | 24,813 |
| Instructions | 7,602 |
| Raw differing bytes | 1,463 |
| Normalized differing instructions | 0 |
| Raw-byte-identical functions | 8 |
| Relocation-only raw-different functions | 32 |
| Address-mapped rows still unresolved | 10 |

Seven rows are directly useful product-code corroboration rather than only
compiler/runtime support:

| Retail | Demo | Function | Body |
| --- | --- | --- | ---: |
| `0x00437490` | `0x004374A0` | `CPhysicsScriptStatements__CreateStatementType5` | 1,971 B / 453 instructions |
| `0x00482590` | `0x00482380` | `CHud__RenderTargetIndicatorOverlay` | 3,929 B / 943 instructions |
| `0x004AAB90` | `0x004AA9F0` | `CMesh__Deserialize` | 1,916 B / 571 instructions |
| `0x004B7D90` | `0x004B7B80` | `CGame__PumpBinkVoiceSampleQueue` | 266 B / 68 instructions |
| `0x004BE420` | `0x004BE330` | `CExplosionInitThing__SelectNextPathStepDirection` | 1,052 B / 285 instructions |
| `0x004D9F30` | `0x004D9E10` | `CRound__UpdateEffectTransformByMode_004d9f30` | 1,779 B / 502 instructions |
| `0x00559410` | `0x00559AB0` | `CDXTexture__CreateMipmaps` | 1,771 B / 529 instructions |

The other 33 rows are CRT, exception/unwind, locale, memory, JPEG, and texture
support functions. They remain valuable for separating compiler/runtime lineage
from actual game changes, but this batch does not promote their current names or
infer additional semantics from the demo.

## Inventory reconciliation

The mapped inventory now separates cleanly:

| Address-mapped category | Count |
| --- | ---: |
| Original single-range normalized-identical rows | 8,021 |
| Multi-range normalized-identical corrections | 42 |
| Semantically resolved non-identical rows | 13 |
| Still unresolved mapped rows | 10 |
| **Total mapped demo entries** | **8,086** |

The 42 corrections are the forty rows in this receipt plus the two previously
reported text-core multi-range bodies. Thus 8,063 mapped functions now have a
complete normalized-identical instruction stream. Thirteen genuinely changed
rows have complete semantic lineage reports. Ten mapped rows remain for a new
instrument, and fifty retail functions still lack a demo entry.

## Evidence boundary

Normalization masks encoded immediate and displacement fields. A zero result
therefore proves instruction/control shape at the current body boundary; it
does not prove that every relocated pointer names an equivalent object, that
global contents are equal, or that the function executes identically. Exact
runtime behavior, original source text, and rebuild parity remain separate
questions.

This batch also does not increase a function's semantic confidence merely
because the demo preserves its shape. It corrects the cross-build comparison
and provides an independent refuter for interpretations that would require a
different opcode, register form, branch shape, or instruction layout.
