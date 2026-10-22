# Terrain shade interpolation — the exact 8.8 fixed-point stepping, decoded from bytes

Status: active static contract
Last updated: 2026-10-22 (retail disassembly listings replaced by prose and tables; earlier: 2026-09-26 RE audit of loop labels, destination argument and edge distance)
Summary: the landscape blit's bilinear shade stepping in 8.8 fixed point, which the reconstruction implements exactly.
Evidence: MEASURED — capture-target instructions (identical to the pristine specimen here) and the materialized shade plane.

> Verdict: the landscape blit's bilinear shade interpolation is decoded
> instruction by instruction, and **the reconstruction already implements it
> exactly.** At the one level where the reconstruction takes a single corner —
> the 512×512 root map, which is level 0 — the interpolation is *algebraically
> and empirically* the same corner, measured to zero mismatches over 33,600
> island texels. **No divergence exists here, and none was invented to close
> the terrain gain.**

Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`,
2,506,752 bytes — the **capture target**: pristine plus the
`force_windowed` patch and nothing else.
*(Corrected 2026-07-28. This line previously read "`BEA.exe`, SHA-256
`e1436ef7…`, 2,506,752 bytes (local pristine safe copy)". `e1436ef7` is **not** pristine —
the pristine specimen is `BEA.exe.original.backup`, SHA-256 `74154bfa…`, in
the same directory; see
[`retail-specimen-baseline.md`](retail-specimen-baseline.md) and
[`retail-capture-provenance-2026-07-25.md`](retail-capture-provenance-2026-07-25.md),
which records that the two file names are inverted in that directory.
Re-measured 2026-07-28: the two builds differ at exactly **four** bytes,
file offsets `0x12a644`–`0x12a647` = VA `0x0052a644`–`0x0052a647`
(`a1 f0 2d 66 00` → `b8 01 00 00 00`). No address cited anywhere in this
note falls in that range — the nearest are `0x0048ea80` below and `0x006fadc8`
above — and no disassembly quoted here decodes through it, so **every byte
claim below stands unchanged.** This is a specimen-label correction, not a
re-measurement.)*
Image base `0x00400000`.

## 1. The call is ten arguments, not nine — resolved from the push sequence

`terrain-shade-plane-origin-2026-07-26.md` records that `RET 0x28` proves a
tenth stack argument Ghidra does not render, leaving the loop bounds
unresolved. The call site settles it. `CLandscapeTexture__UpdateTile`
@ `0x0048ea80`, first blit call:

| Push site | Argument | Value |
| --- | --- | --- |
| `0x0048eb28` | arg10 | 8 |
| `0x0048eb2a` | arg9 | 8 |
| `0x0048eb2c` | arg8 | 0 |
| `0x0048eb36` | arg7 | 0 |
| `0x0048eb38` | arg6 | 5 |
| `0x0048eb3a` | arg5 | `tile_flags` = `tile_coord & 0xffff` |
| `0x0048eb3d` | arg4 | `dst_stride` = pitch/2 |
| `0x0048eb42` | arg3 | `dst_bits` (the locked surface; `LockRect` at `0x0048eb14`) |
| `0x0048eb57` | arg2 | `tile_ctx` |
| `0x0048eb58` | arg1 | `lod_shift` = `[this+0x34]` |

`this` is the global height field `0x006fadc8`; the call to `0x0047eff0` is at
`0x0048eb5e`.

So the trailing arguments are **`5, 0, 0, 8, 8`**, not `5, 0, 0, 8`. The
prologue is `sub esp,0x80` plus four pushes, so argument *n* lives at
`[esp + 0x90 + 4n]`. Reading the body against that mapping:

| use | site | argument | value |
| --- | --- | --- | --- |
| `1 << lod_shift` | `0x0047f016` (`shl` by the arg1 count) | arg1 | object mip |
| tile flag tests | `0x0047f034` load, then a bit-0 test | arg5 | `tile_coord & 0xffff` |
| outer loop over rows, start | `0x0047f070` | arg8 | 0 |
| outer loop over rows, end | `0x0047f139` … `0x0047f142` | arg10 | 8 |
| inner loop over columns, start | `0x0047f183` | arg7 | 0 |
| inner loop over columns, end | `0x0047f19a`; `0x0047f6c1`–`0x0047f6d4` | arg9 | 8 |

Argument 3 is the destination: the blit builds its 16-bit output pointer from it
(`0047f092-0047f09f`) and stores through that pointer (`mov [edi-2],dx`, `0047f5b6`).
The shade is read from `[0x0089bd84]`. Each outer pass advances the row by `0x200`
(`0047f71a`).

Argument 6 (`5`) is never read by the body — the blit ignores it. The loop
therefore runs 8 × 8 **units** per tile, and each unit expands to
`N = 1 << lod_shift` destination texels. `dst_stride` for the intermediate
buffer branch is `0x400 / 2 = 0x200` = 512 texels, i.e. 64 tiles × 8 units ×
1 texel, which fixes **`lod_shift = 0` for the 512×512 root map**.

## 2. The interpolation

`0x0047f463`–`0x0047f4d6`, with `ebx` = the plane row base
(`((tile_flags>>6)*8 + i)*0x200 + [0x0089bd84] + (tile_flags&0x3f)*8`) and
`edi`/`eax` = the inner unit index `j`:

It loads the four corner shades `s00`, `s01`, `s10`, `s11` from the plane
(`0x0047f471`–`0x0047f485`; the `+1`, `+0x200` and `+0x201` neighbours of the
unit), forms the 8.8 differences along X, along Y and across the diagonal, and
shifts them arithmetically right by `lod_shift` (X and Y) and by twice
`lod_shift` (the cross term), `0x0047f492`–`0x0047f4b1`.

The two loops, row at `0x0047f506` and column at `0x0047f530`, both **advance
before they sample**:

The row step (`0x0047f506`) adds the Y step to the row accumulator and the
cross term to the X step; the column step (`0x0047f530`) adds the X step to the
value. The lighting index is the value shifted right by 8 (`0x0047f54a`),
halved where the tile's shadow bit is set (`0x0047f570`), and then selects a
12-byte gradient entry (multiply at `0x0047f579`, displacement `0x10d8`).

In closed form, for destination sub-texel `(r, c)` of a unit, `0 ≤ r,c < N`:

```
s00 = P[y*512 + x]      s01 = P[y*512 + x + 1]
s10 = P[(y+1)*512 + x]  s11 = P[(y+1)*512 + x + 1]
stepX  = ((s01 - s00) << 8) >> L
stepY  = ((s10 - s00) << 8) >> L
stepXY = (((s11 - s10) - (s01 - s00)) << 8) >> (2L)
index(r,c) = ( (s00 << 8) + (r+1)*stepY + (c+1)*(stepX + (r+1)*stepXY) ) >> 8
```

All shifts are `SAR`, i.e. arithmetic, floor-rounding. There is **no clamp** on
the index in retail; the gradient is 64 entries of 12 bytes at `this+0x10d0`.

Note the `(r+1)`/`(c+1)`: the pre-increment means the block never samples the
near corner `s00` and its last texel lands exactly on the far corner `s11`.

## 3. Consequence: at `L = 0` the interpolation *is* the far corner

Substituting `N = 1`, `r = c = 0`:

```
acc  = (s00<<8) + stepY = s10 << 8
val  = acc + (stepX + stepXY) = (s10<<8) + (s11-s10)<<8 = s11 << 8
index = s11
```

Exactly `shade[(y+1)*512 + (x+1)]` — the value the reconstruction's Python
materializer takes directly. This is not an approximation; the two expressions
are identical integers.

Measured rather than argued: `tools/terrain_shade_interpolation_probe.py`
re-implements the stepping above over the materialized Level 100 hierarchy and
compares the interpolated index against the corner sample for every texel of
every island tile —

```
island tiles with any non-zero shade corner: 525 of 4096
level 0: interpolated index vs shade[(y+1)*512+(x+1)] -> 0 mismatches in 33600 texels
```

## 4. What the interpolation contributes where it is not degenerate

Levels 1–4 of the macro cache are produced by
`Level100TerrainCompositor.RenderTile`, which already implements the closed
form in §2 (`shadeRow`, `shadeStep`, `shadeCross`, both `+1` pre-increments,
`>> level` and `>> (level*2)`). Compositing island tiles at each level and
measuring the per-texel spread of the resulting RGB565 macro:

| level | raw index min | raw index max | mean R/G/B | sd R/G/B |
| ---: | ---: | ---: | --- | --- |
| 0 | 0 | 63 | 0.2951 0.3136 0.5312 | 0.1930 0.1911 0.1819 |
| 1 | 0 | 63 | 0.2946 0.3126 0.5348 | 0.1921 0.1889 0.1741 |
| 2 | 0 | 63 | 0.2964 0.3146 0.5409 | 0.1963 0.1928 0.1757 |
| 3 | 0 | 63 | 0.2995 0.3182 0.5469 | 0.2009 0.1974 0.1782 |

Interpolation moves the macro mean by **under 0.005 of full scale** and the
spread by under 0.01. It smooths within a unit; it does not brighten. It cannot
produce a 1.29–1.40 gain and it is not a candidate mechanism for one.

The `rawMin`/`rawMax` columns also settle a second question: the raw retail
index never leaves `0..63` on this map at any level, so the reconstruction's
defensive `Math.Clamp(..., 0, 63)` is measured never to fire and is not a
behavioural divergence.

## 5. Edge reads

Retail forms the `+1` corners by pointer arithmetic with no bounds check, so at
column 511 it reads the first byte of the next plane row and at row 511 it
reads past the buffer. The reconstruction clamps to 511 instead. The Level 100
island's non-zero support spans rows 144–368 and columns 136–432
(`terrain-shade-plane-origin-2026-07-26.md` §4), so no island texel is within
79 units of an edge (column 432 is 79 from 511) and the two readings cannot differ
for island texels. At row 511 retail reads past the plane into whatever follows it,
so the bottom row of the full 512×512 root map may differ from the clamped
reconstruction.

## Boundary

Static evidence from the capture-target specimen named in the header
(`e1436ef7…`, pristine + `force_windowed`), plus arithmetic over locally
materialized Level 100 asset bytes. It establishes the blit's interpolation
exactly and shows the reconstruction reproduces it. It does **not** identify
the mechanism behind retail's measured 1.40 / 1.30 / 1.08 terrain chain gain (the ambient-light note's later measurement is 1.457 / 1.389 / 1.147; the two have not been reconciled);
this pass removes the interpolation from the candidate list.
