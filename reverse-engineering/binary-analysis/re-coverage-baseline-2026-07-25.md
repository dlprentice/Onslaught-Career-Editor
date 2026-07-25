# RE coverage baseline — what the 6,411-function pass actually covers

Date: 2026-07-25. Produced by `tools/re_verify.py`, which checks every exported
instruction against the pristine binary. Reproducible in under a minute:

```
py -3 tools/re_verify.py --binary <pristine BEA.exe> --exports <exports dir> --inventory functions-all.tsv
```

## Headline

**The functions that exist are sound. The set of functions is incomplete.**

| Measure | Result |
| --- | ---: |
| Exported instructions verified against the binary | **468,804** |
| Byte mismatches | **0** |
| Functions checked | 6,411 |
| Functions fully clean | **6,351 (99.1%)** |
| Functions with a flagged issue | 60 |
| Overlapping function bodies | 6 |
| **`.text` covered by function bodies** | **79.8%** |
| **`.text` uncovered, excluding padding** | **284,815 bytes (14.8%)** |

## Per-function quality: excellent

Zero byte mismatches across 468,804 instructions. Every exported instruction
reproduces the pristine binary exactly. This independently corroborates the
sampled findings audit, which measured 99.93% assertion accuracy over ~4,550
checks — but where that audit sampled 44 of 533 files, this is exhaustive.

The 60 flagged functions break down as:
- **fragmented bodies** — instructions inside the function's address span that
  belong to no exported function (see coverage, below);
- **6 overlaps**, concentrated in CRT routines (`CRT__HeapAllocBase` /
  `CRT__UnlockHeapLock9_*`, `CRT__FreeBase` / `CRT__UnlockHeapLock`). These are
  shared-epilogue functions — a real and common Ghidra modelling artifact in CRT
  code, not an error in the analysis;
- **one genuine anomaly**: `_strchr` at `0x0055e2d0` has body content starting at
  `0x0055e2c0`, i.e. the recorded entry is not the lowest address in its body.

None of these is a correctness failure of the kind that would mislead downstream
work. All are worth resolving, none is urgent.

## Coverage: the real gap

`.text` is 1,929,117 bytes. The 6,411 function bodies account for **79.8%**.
Of the uncovered 389,164 bytes, only **26.8% is `0xCC`/`0x90`/`0x00` padding**.
That leaves **284,815 bytes — 14.8% of the code section — of non-padding content
owned by no function at all**, in 4,356 runs, of which **600 are ≥64 bytes and 304
are ≥256 bytes**.

Sampling the largest runs shows the space is a genuine mix, and the mix matters:

| VA | length | character |
| --- | ---: | --- |
| `0x005c9c69` | 26,743 | **data** — ascending 4-byte pointer table (`0x005be7a8`, `0x005be7b2`, …) |
| `0x005b8e9e` | 11,026 | **code** — `MOV EDI,EDI; MOVD EAX,MM0; MOVD MM3,…` (MMX routine) |
| `0x004c8514` | 9,756 | **code** — NOP padding then `SUB ESP,0x10c; PUSH EBX; PUSH EBP` |
| `0x00526098` | 6,344 | **data** — pointer table |
| `0x004c36a1` | 4,735 | **code** — NOP padding then `SUB ESP,0xf0` |
| `0x005b4b17` | 4,201 | **code** — NOP padding then `SUB ESP,0x10; PUSH EBP; PUSH EDI` |
| `0x0048cb43` | 3,469 | **data** — jump table |

Several runs begin with `0x90` alignment padding followed immediately by a textbook
MSVC prologue. Those are **whole functions Ghidra never created**.

## What this means for "a full pass over all 6,000+ functions"

The prior 18-wave campaign covered its 6,411-function inventory thoroughly and
accurately. But that inventory is not the binary. **A pass that verifies 6,411
names while ~285 KB of non-padding code sits unclaimed is not a full pass** — it is
a complete pass over an incomplete list.

The R4 create-function work (22 created, 205 rejected as `UNDEFINED`) was operating
at the edge of exactly this space. Those 205 `UNDEFINED` candidates are a small
sample of the 4,356 uncovered runs.

**Recommended ordering, revised:** recover the missing functions *before* grading
the names of the existing ones. Grading 6,411 names to a high standard and then
discovering several hundred more functions means re-running the naming work with a
changed call graph — and the call graph is precisely the evidence the name oracle
depends on.

## What this file does not claim

- It does **not** claim 14.8% of `.text` is missing code. A substantial share of
  the uncovered space is embedded data — pointer tables, jump tables, and
  read-only literals living in `.text` — which correctly belongs to no function.
  Separating data from unrecovered code across all 4,356 runs is the next
  measurement, not a settled result.
- It does **not** assess whether any function's **name** is correct. `re_verify.py`
  proves bytes, boundaries, and structure only. A function can pass every check
  here and still carry an entirely invented name. Naming is graded separately.
