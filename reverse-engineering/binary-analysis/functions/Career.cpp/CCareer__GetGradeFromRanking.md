# CCareer__GetGradeFromRanking

> Address: `0x00421470`
>
> Source: `references/Onslaught/Career.cpp` (`CCareer::GetGradeFromRanking(float)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Convert float ranking to grade letter. Core grade calculation function that translates the stored float ranking (0.0-1.0) to display grades (S/A/B/C/D/E).

## Signature
```c
int CCareer__GetGradeFromRanking(float ranking);

// Source semantic type:
// WCHAR CCareer::GetGradeFromRanking(float ranking);
// (Retail emits grade in AX / low 16 bits; API parser rejected `wchar_t` signature literal.)
```

## Algorithm (from Source)
```cpp
char GetGradeFromRanking(float f) {
    char c;
    if (f == 1.f) c = 'S';
    else if (f <= 0.f) c = 'E';
    else c = 'D' - floor(f * 4);
    return c;
}
```

## Grade Mapping
| Float | floor(f*4) | 'D' - result | Grade |
|-------|-----------|--------------|-------|
| 1.0 | - | - | S (special case) |
| 0.8 | 3 | 68-3=65 | A |
| 0.6 | 2 | 68-2=66 | B |
| 0.35 | 1 | 68-1=67 | C |
| 0.15 | 0 | 68-0=68 | D |
| 0.0 | - | - | E (special case) |

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Verified against source code
- Critical for rank display in patcher
- -1.0f shows no letter (undefined behavior in console port)

## Related Functions
- [CCareer__GetGradeForWorld](CCareer__GetGradeForWorld.md) - Calls this function
- [TOTAL_S_GRADES](TOTAL_S_GRADES.md) - Uses grade for S-rank threshold checks
