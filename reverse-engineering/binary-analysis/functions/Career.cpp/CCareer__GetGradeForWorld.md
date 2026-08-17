# CCareer__GetGradeForWorld

<!-- ghidra-name-drift-accepted: 0x0041c330 CCareer_T3_0041c330 (2026-08-17) -->

> Address: 0x0041c330 | Source: `references/Onslaught/Career.cpp`
>
> **The saved Ghidra name is now the Tier-3 placeholder `CCareer_T3_0041c330`.**
> This page keeps its old title so existing references still resolve.

## Name demotion — 2026-08-17

The 2026-08-17 anchor audit
([`name-cohort-promotion-manifest-2026-08-17.tsv`](../../name-cohort-promotion-manifest-2026-08-17.tsv))
found no `CCareer` type descriptor anywhere in the shipped image and no vtable
owning this VA, so the descriptive name lost its structural support and was
replaced by a neutral placeholder rather than by a second invented label.

Read that for exactly what it is. The audit graded *names* against RTTI and
vtable anchors; it did not open the body and it did not look at
`references/Onslaught/Career.cpp`. What it withdraws is the claim that the
image proves this address belongs to a class called `CCareer` and to a method
called `GetGradeForWorld`. What it leaves untouched is everything below, which
rests on the source correspondence and on the byte-level reading — a different
axis of evidence that this cohort did not measure. `CCareer` has never had an
RTTI anchor here; the difference is that the database no longer implies it does.

## Status
- **Named in Ghidra:** yes, but only as the placeholder `CCareer_T3_0041c330`
- **Signature Set:** Yes
- **Verified vs Source:** Yes (source-equivalent helper; retail ABI differs) —
  unaffected by the demotion above, which measured RTTI anchors and not source
  correspondence

## Purpose
Get letter grade (S/A/B/C/D/E) for specific level. Retrieves the mRanking value from a node and converts it to a display grade.

## Signature
```c
char * CCareer__GetGradeForWorld(char * out_grade, int world_num);

// Source-equivalent semantic helper:
// CGrade GRADE(int world_num);
```

## Grade Calculation
From source code (Career.cpp:1178-1195):
```cpp
if (f == 1.f) c = 'S';
else if (f <= 0.f) c = 'E';
else c = 'D' - floor(f * 4);
```

| Grade | Float Range |
|-------|-------------|
| S | 1.0 exactly |
| A | 0.75-0.99 |
| B | 0.5-0.74 |
| C | 0.25-0.49 |
| D | 0.01-0.24 |
| E | <= 0.0 |

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Retail helper writes one grade byte into `out_grade` and returns `out_grade`
- Source-equivalent role matches `GRADE(int world_num)` (returns `CGrade` by value)
- Used by mission select screen for grade display

## Related Functions
- [CCareer__GetGradeFromRanking](CCareer__GetGradeFromRanking.md) - Core conversion logic
- [CCareer__GetNodeFromWorld](CCareer__GetNodeFromWorld.md) - Gets node to read ranking from
