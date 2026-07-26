# Terrain shade interpolation — the exact 8.8 fixed-point stepping, decoded from bytes

> Verdict: the landscape blit's bilinear shade interpolation is decoded
> instruction by instruction, and **the reconstruction already implements it
> exactly.** At the one level where the reconstruction takes a single corner —
> the 512×512 root map, which is level 0 — the interpolation is *algebraically
> and empirically* the same corner, measured to zero mismatches over 33,600
> island texels. **No divergence exists here, and none was invented to close
> the terrain gain.**

Specimen: `BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`,
2,506,752 bytes (local pristine safe copy). Image base `0x00400000`.

## 1. The call is ten arguments, not nine — resolved from the push sequence

`terrain-shade-plane-origin-2026-07-26.md` records that `RET 0x28` proves a
tenth stack argument Ghidra does not render, leaving the loop bounds
unresolved. The call site settles it. `CLandscapeTexture__UpdateTile`
@ `0x0048ea80`, first blit call:

```
0048eb28   6a 08                push 8              ; arg10  [esp+0x28]
0048eb2a   6a 08                push 8              ; arg9   [esp+0x24]
0048eb2c   6a 00                push 0              ; arg8   [esp+0x20]
0048eb36   6a 00                push 0              ; arg7   [esp+0x1c]
0048eb38   6a 05                push 5              ; arg6   [esp+0x18]
0048eb3a   57                   push edi            ; arg5  tile_flags = tile_coord & 0xffff
0048eb3d   50                   push eax            ; arg4  dst_stride = pitch/2
0048eb42   50                   push eax            ; arg3  src_base
0048eb57   51                   push ecx            ; arg2  tile_ctx
0048eb58   52                   push edx            ; arg1  lod_shift = [this+0x34]
0048eb59   b9 c8 ad 6f 00       mov ecx, 0x6fadc8   ; this  = the global height field
0048eb5e   e8 8d 04 ff ff       call 0x47eff0
```

So the trailing arguments are **`5, 0, 0, 8, 8`**, not `5, 0, 0, 8`. The
prologue is `sub esp,0x80` plus four pushes, so argument *n* lives at
`[esp + 0x90 + 4n]`. Reading the body against that mapping:

| use | instruction | argument | value |
| --- | --- | --- | --- |
| `1 << lod_shift` | `0047f016  d3 e5  shl ebp, cl` (`cl` from `[esp+0x8c]` pre-push) | arg1 | object mip |
| tile flag tests | `0047f034  8b 8c 24 a4 00 00 00` → `test cl,1` | arg5 | `tile_coord & 0xffff` |
| outer loop start | `0047f183  8b 84 24 ac 00 00 00` | arg7 | 0 |
| outer loop end | `0047f19a  8b 8c 24 b4 00 00 00 / 3b c1 / jge` | arg9 | 8 |

Argument 6 (`5`) is never read by the body — the blit ignores it. The loop
therefore runs 8 × 8 **units** per tile, and each unit expands to
`N = 1 << lod_shift` destination texels. `dst_stride` for the intermediate
buffer branch is `0x400 / 2 = 0x200` = 512 texels, i.e. 64 tiles × 8 units ×
1 texel, which fixes **`lod_shift = 0` for the 512×512 root map**.

## 2. The interpolation, instruction by instruction

`0x0047f463`–`0x0047f4d6`, with `ebx` = the plane row base
(`((tile_flags>>6)*8 + i)*0x200 + [0x0089bd84] + (tile_flags&0x3f)*8`) and
`edi`/`eax` = the inner unit index `j`:

```
0047f471  8a 34 03              mov dh, [ebx + eax]           ; edx = s00 << 8
0047f476  8a 4c 3b 01           mov cl, [ebx + edi + 1]       ; ecx = s01
0047f47a  8a a4 3b 00 02 00 00  mov ah, [ebx + edi + 0x200]   ; eax = s10 << 8
0047f485  8a 8c 3b 01 02 00 00  mov cl, [ebx + edi + 0x201]   ; ecx = s11
0047f492  8b 8c 24 94 00 00 00  mov ecx, [esp + 0x94]         ; ecx = lod_shift  (arg1)
0047f499  c1 e6 08              shl esi, 8                    ; s01 << 8
0047f49c  c1 e3 08              shl ebx, 8                    ; s11 << 8
0047f49f  2b f2                 sub esi, edx                  ; dX  = (s01-s00)<<8
0047f4a1  2b d8                 sub ebx, eax                  ;       (s11-s10)<<8
0047f4a3  2b c2                 sub eax, edx                  ; dY  = (s10-s00)<<8
0047f4a5  2b de                 sub ebx, esi                  ; dXY = ((s11-s10)-(s01-s00))<<8
0047f4a7  d3 fe                 sar esi, cl                   ; stepX  = dX  >> L
0047f4a9  d3 f8                 sar eax, cl                   ; stepY  = dY  >> L
0047f4ab  03 c9                 add ecx, ecx                  ; cl = 2L
0047f4b1  d3 fb                 sar ebx, cl                   ; stepXY = dXY >> 2L
```

The two loops, row at `0x0047f506` and column at `0x0047f530`, both **advance
before they sample**:

```
0047f506  8b 4c 24 18  mov ecx,[esp+0x18]   ; stepY
0047f50a  03 d1        add edx, ecx         ; acc   += stepY      (row)
0047f510  03 f3        add esi, ebx         ; stepX += stepXY     (row)
...
0047f530  03 d6        add edx, esi         ; val   += stepX      (column)
0047f54a  c1 fa 08     sar edx, 8           ; lighting index = val >> 8
0047f570  d3 fa        sar edx, cl          ; shadow rule: >> 1 where the tile bit is set
0047f576  8d 14 52     lea edx,[edx + edx*2]
0047f579  0f af 9c 91 d8 10 00 00  imul ebx, [ecx + edx*4 + 0x10d8]   ; gradient[idx], stride 0xc
```

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
143 units of either edge and the two readings cannot differ on this map.

## Boundary

Static evidence from the pristine specimen, plus arithmetic over locally
materialized Level 100 asset bytes. It establishes the blit's interpolation
exactly and shows the reconstruction reproduces it. It does **not** identify
the mechanism behind retail's measured 1.40 / 1.30 / 1.08 terrain chain gain;
this pass removes the interpolation from the candidate list.
