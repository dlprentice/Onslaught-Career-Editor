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

---

## Update — gap recovery applied (same day)

`tools/re_gap_classify.py` classified the uncovered space, and the recovered
functions have been created on the live database.

Classification of all uncovered runs >= 8 bytes (2,924 runs, 383,688 bytes):

| class | runs | bytes | share |
| --- | ---: | ---: | ---: |
| **CODE** | 643 | **300,307** | **78.3%** |
| UNKNOWN | 621 | 51,189 | 13.3% |
| PAD | 1,536 | 17,736 | 4.6% |
| PTR_TABLE | 37 | 9,403 | 2.5% |
| DATA | 87 | 5,053 | 1.3% |

So the uncovered fifth of `.text` is **overwhelmingly real code**, not embedded
data. The earlier caution that "a substantial share is probably data" was correct
in kind but wrong in proportion — data and padding together account for only 8.4%.

Of 643 CODE runs, **568** start on a 16-byte boundary and were taken as creation
candidates. Unaligned starts were excluded: a branch target inside an existing body
is far more likely than a function entry, and creating a function there splits a
real function in half.

**Independent agreement.** Ghidra's own listing state for those 568:

| status | count |
| --- | ---: |
| `INSTRUCTION_NO_FUNCTION` | **536** |
| `OK` (already created by R4) | 20 |
| `UNDEFINED` | 9 |
| `DEFINED_DATA` | 3 |

The static classifier and Ghidra agree on **536/568 = 94.4%**, derived from
completely different evidence — capstone decoding plus reference scanning on one
side, Ghidra's listing model on the other.

**Applied.** The 536 `INSTRUCTION_NO_FUNCTION` candidates were created live under
the established discipline: verified pre-backup, canary of 20 on `project-rw` with
dual readback (20/20 `OK`), canary promoted live and read back (20/20 `OK`), then
the remaining 516. Final readback over all 536: **536/536 `OK`**,
`created=536 failed=0`. All carry default `FUN_` names; no class name was invented.

Backups: `F:\GhidraBackups\BEA_20260725-224946Z_pre_promote_gap536` and
`..._225146Z_post_promote_gap536`, both verified by file count and byte total.

Function inventory: **6,411 -> 6,969** (6,411 baseline + 22 from R4 + 536 here).

**Still outstanding:** the 621 UNKNOWN runs (51,189 bytes) decode acceptably but
nothing references them, so they were deliberately not created — absence of entry
evidence is not evidence of an entry. Re-exporting the database and re-running
`re_verify.py` is the correct way to confirm the new coverage percentage; that has
not been done yet, so no new coverage figure is claimed here.
