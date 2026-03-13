# CCareer__GetGradeForWorld

> Address: 0x0041c330 | Source: `references/Onslaught/Career.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes (source-equivalent helper; retail ABI differs)

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
