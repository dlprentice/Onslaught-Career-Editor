# Grade System

Status: active save contract
Last updated: 2026-09-26 (RE audit: how the level map draws -1.0, and rankings above 1.0)
Summary: a mission's rank is the float at CCareerNode+0x3C; the converter maps it to S, A-D or E, and -1.0 marks an uncompleted node.
Evidence: MEASURED — the retail converter and level-map switch; SOURCE — `Career.cpp:1178-1202`; no capture of the map.
Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Retail/Steam Build (True Dword View)

In the retail/Steam `BEA.exe`, per-mission rank is stored as a raw IEEE-754 float in `CCareerNode.mRanking` at `CCareerNode + 0x3C`.

**On-disk mapping:**

```text
file_offset = 0x0002 + career_offset
```

In other words: CCareer dwords are aligned to offsets where `file_offset % 4 == 2`. If you view the file at 4-byte aligned offsets (`% 4 == 0`), values can look "shift-16" or "split", but that is just a misaligned view.

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

Practical patching note: the patchers in this repo write these **bit patterns** directly to the node's `+0x3C` dword.

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

## "NONE" (-1.0)

Retail saves use `-1.0f` (`0xBF800000`) as a sentinel in nodes that are not completed; `Blank` writes it. The converter (`0x00421470`, identical to `Career.cpp:1178-1202`) returns `E` for it, like any `f <= 0`.

The level-select map special-cases exactly `-1.0` (`fcomp` at `0x0046111e`) and substitutes `-`, and a locked world gets a space. But its letter switch (`0x00461153-0x00461166`: the character minus `A`, then a byte table) sends `-`, the space and every character other than `A`-`D` and `S` to the same texture slot as `E` (`[0x0089d82c]`), which `CFrontEnd::LoadSharedResources` fills with `FrontEnd\v2\FE_Ranking_Small_Mask_E.tga` (`0x00468bd5`). So statically an unplayed, unlocked world draws the E mask. No capture has confirmed how it looks.

Rankings above `1.0` give `D - floor(4f)` = `@` or lower, which is not a letter; the map draws those with the E slot too. Editors should keep rankings in `[0, 1]` or `-1.0`.

## Legacy Note (Deprecated)

Older docs in this repo referred to "split-float" rank storage across `state` and `mRanking`. That was describing the legacy 4-byte aligned *view* of the file (misaligned by 2 bytes), not a real on-disk encoding used by `BEA.exe`.
