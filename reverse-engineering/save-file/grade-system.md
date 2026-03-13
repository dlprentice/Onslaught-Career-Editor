# Grade System

## Retail/Steam Build (True Dword View)

In the retail/Steam `BEA.exe`, per-mission rank is stored as a raw IEEE-754 float in `CCareerNode.mRanking` at `CCareerNode + 0x3C`.

**On-disk mapping:**

```text
file_offset = 0x0002 + career_offset
```

In other words: CCareer dwords are aligned to offsets where `file_offset % 4 == 2`. If you view the file at 4-byte aligned offsets (`% 4 == 0`), values can look “shift-16” or “split”, but that is just a misaligned view.

## Rank Values (mRanking Bits)

| Rank | Float | Bits |
|------|-------|------|
| S | 1.0 | 0x3F800000 |
| A | 0.8 | 0x3F4CCCCD |
| B | 0.6 | 0x3F19999A |
| C | 0.35 | 0x3EB33333 |
| D | 0.15 | 0x3E19999A |
| E | 0.0 | 0x00000000 |
| NONE | -1.0 | 0xBF800000 |

Practical patching note: the patchers in this repo write these **bit patterns** directly to the node’s `+0x3C` dword.

## Grade Letter Conversion (Source Reference)

The internal source (`references/Onslaught/`) contains the grade conversion logic (`CCareer::GetGradeFromRanking`):

```cpp
if (f == 1.f) return 'S';
else if (f <= 0.f) return 'E';
else {
    i = floor(f * 4.f);
    return 'D' - i;  // 0->D, 1->C, 2->B, 3->A
}
```

This implies:
- `f == 1.0` => `S`
- `0.75 <= f < 1.0` => `A`
- `0.50 <= f < 0.75` => `B`
- `0.25 <= f < 0.50` => `C`
- `0.0 < f < 0.25` => `D`
- `f <= 0.0` => `E`

## “NONE” (-1.0)

Retail saves use `-1.0f` (`0xBF800000`) as a sentinel in nodes that are not completed. In-game, this appears to render as “no letter” (not `E`), even though the source logic would classify `f <= 0` as `E`. Treat this as **retail UI behavior**, not a guarantee from the source.

## Legacy Note (Deprecated)

Older docs in this repo referred to “split-float” rank storage across `state` and `mRanking`. That was describing the legacy 4-byte aligned *view* of the file (misaligned by 2 bytes), not a real on-disk encoding used by `BEA.exe`.

