Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
Summary: Rank float and bit-pattern lookup.
# Rank/Grade System

## True View Encoding

In the retail/Steam build, rank is stored as raw IEEE-754 float bits in `CCareerNode.mRanking` at `node + 0x3C` (true dword view). Older docs that described a “split-float” were looking at a legacy 4-byte-aligned view of the same bytes.

## Rank Values (VERIFIED)

| Rank | Float | IEEE-754 Bits |
|------|-------|--------------|
| S | 1.0 | 0x3F800000 |
| A | 0.8 | 0x3F4CCCCD |
| B | 0.6 | 0x3F19999A |
| C | 0.35 | 0x3EB33333 |
| D | 0.15 | 0x3E19999A |
| E | 0.0 | 0x00000000 |
| NONE | -1.0 | 0xBF800000 |

## Grade Calculation (Source: Career.cpp:1178)

```cpp
WCHAR GetGradeFromRanking(float f) {
    if (f == 1.f) return 'S';
    else if (f <= 0.f) return 'E';
    else {
        SINT i = SINT(floorf(f * 4.f));
        return 'D' - i;  // 0->D, 1->C, 2->B, 3->A
    }
}
```

## Threshold Ranges

| Grade | Float Range | floor(f*4) |
|-------|-------------|------------|
| S | f == 1.0 | Exact match |
| A | 0.75 <= f < 1.0 | 3 |
| B | 0.50 <= f < 0.75 | 2 |
| C | 0.25 <= f < 0.50 | 1 |
| D | 0.0 < f < 0.25 | 0 |
| E | f <= 0.0 | Explicit |

## NONE Caveat

-1.0f shows no letter (undefined behavior). Source says E, but no RankingNONE.tga exists.

## Node Rank Patching

For synthetic S-rank: set `mRanking = 0x3F800000` and ensure the node is marked complete (`mComplete=1`).
