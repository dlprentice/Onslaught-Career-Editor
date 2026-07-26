# Terrain shade plane — origin, ownership, and axis order

> Verdict: the terrain lighting-index plane is **map asset data read verbatim from
> the `MMAP` chunk stream**. It is not computed at load, not derived from heights
> or the sun vector, and not modified at runtime. The reconstruction already
> holds the exact retail bytes, and the axis convention it uses is confirmed
> against an independent asset.

Specimen: `BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`,
2,506,752 bytes (local pristine safe copy). Image base `0x00400000`;
`.text` VA `0x00401000`, file offset `0x1000`.

## 1. The plane is owned by a global `CMixerMap`, not by the height field

The tile blit at `0x0047eff0` reads the plane base from `0x0089bd84`:

```
0x0047f172   8b 0d 84 bd 89 00     MOV ECX, dword ptr [0x0089bd84]
```

An exhaustive scan of the whole file for the little-endian operand `84 bd 89 00`
returns **exactly one hit**, that instruction. Scanning for `80 bd 89 00`
returns **four**, all in `.text`:

| VA | bytes | meaning |
| --- | --- | --- |
| `0x0047f0dd` | `8b 15 80 bd 89 00` | `MOV EDX,[0x0089bd80]` — the blit's mixer-slot table read |
| `0x00490f46` | `b9 80 bd 89 00` | `MOV ECX,0x0089bd80` in `CHeightField__ShutdownAndDestroyMixerMap` → `CMixerMap__Destroy` |
| `0x004910dd` | `b9 80 bd 89 00` | `MOV ECX,0x0089bd80` in `CHeightField__DeserializeMapAndInitResources` → `CMixerMap__Init` |
| `0x00523180` | `c7 05 80 bd 89 00 00 00 00 00 / c3` | 11-byte static initializer: `[0x0089bd80] = 0; ret` |

So `0x0089bd80` is a global `CMixerMap` instance and `0x0089bd84` is its second
member. Nothing else in the binary can reach the plane.

## 2. The plane is a straight chunk read — there is no bake

`CMixerMap__Init` @ `0x005232b0`:

- allocates `0x14004` bytes for `0x1000` (= 64×64) 0x14-byte slots from
  `C:\dev\ONSLAUGHT2\mixermap.cpp` line `0xf6`, storing the array at `this+0`;
- allocates **`0x40000` bytes** from the same file line `0xf7`, storing it at
  **`this+4`**;
- reads the 4,096 slots through `CMixerMap__InitSlot`;
- then `CChunkReader__GetNext(reader); CChunkReader__Read(reader, this+4, 1, 0x40000);`

`0x40000` = 262,144 = 512×512 bytes. `CMixerMap__Destroy` @ `0x00523230` only
frees it. **No writer exists.** The plane is the `MSHD` payload that trails the
4,096 `MCEL` records in `MMAP`, byte for byte.

The load order in `CHeightField__DeserializeMapAndInitResources` @ `0x00491060`
is `CHeightField__Load(this, reader)` then `CMixerMap__Init(&DAT_0089bd80, reader)`,
and `CEngine__Deserialize` reaches it with `MOV ECX,0x006fadc8` at `0x0044a72b` —
the same global height field the blit passes as its receiver
(`MOV ECX,0x006fadc8` at `0x0048eb5a` and `0x0048ecea` inside
`CLandscapeTexture__UpdateTile`). One height field, one gradient, one plane.

**Consequence: the hypothesis that retail bakes the shade plane at load from
heights and the `HFLD` sun vector (`SunPositionOffset = 0x10A4`) is false.** The
sun vector never reaches this plane.

## 3. Axis order — confirmed against the height field, not merely self-consistent

The blit forms the plane address as

```
row_base = ((tile_flags >> 6) * 8 + i) * 0x200 + DAT_0089bd84 + (tile_flags & 0x3f) * 8
sample   = row_base[j], row_base[1 + j], row_base[0x200 + j], row_base[0x201 + j]
```

so `index = ((tile_flags>>6)*8 + i)*512 + ((tile_flags&0x3f)*8 + j)`, with the
2×2 corners bilinearly interpolated in 8.8 fixed point. That fixes the plane's
layout *relative to* the `MMAP` cell index but not in world terms, because the
decompiled loop variables are unresolved (`RET 0x28` proves a tenth stack
argument Ghidra does not render).

The `HFLD` settles it independently. `HFDT` stores one `int16` per unit at
`((tileX*64)+tileY)*81 + localY*9 + localX`, and 225,323 of the 262,144 map
texels sit on a single exactly-flat plateau at raw height `1267`; the remaining
36,821 are the island.

| plane reading | shade > 0 on the flat plateau | shade > 0 on non-flat terrain |
| --- | ---: | ---: |
| `shade[y*512 + x]` | **0** | 26,836 |
| `shade[x*512 + y]` | 5,646 | 21,190 |

The first reading partitions perfectly: **every one of the 26,836 non-zero shade
texels lies on non-flat terrain and not one lies on the plateau.** The
transposed reading does not. Therefore the plane is `shade[y*512 + x]`, and
`tile_flags = cellY*64 + cellX` — which is the convention
`rebuild/tools/materialize_retail_assets.py` already uses
(`cell_index = tile_y*64 + tile_x`, `shade[(y+1)*512 + (x+1)]`, mixer weights at
`[local_y*9 + local_x]`).

## 4. The plane's sparsity is the sea floor, not a defect

The 90%-zero figure is geography. The non-zero support is one compact blob
(rows 144–368, columns 136–432); 3,582 of the 4,096 8×8 cells are entirely zero
and 315 entirely non-zero. Within the non-flat island the distribution is
mean 22.06, median 22, p10 15, p90 32, max 63.

## 5. What the shade values can and cannot produce

`CHeightField__InitColorGradient` @ `0x0047e8e0` builds 64 entries at `+0x10d0`
from ambient `+0x108c` and sun `+0x107c`; the tail of `CHeightField__Load`
@ `0x0047f750` then **doubles every entry in place and clamps** to `0x00F80000`,
`0x0007E000`, `0x00001F00`. Re-implemented exactly, with the Level 100 sun
`0xBDB179` and ambient `0x0D0F2B`, a material byte of 255 yields

| shade | R | G | B |
| ---: | ---: | ---: | ---: |
| 0 | 24 | 36 | 172 |
| 14 | 131 | 141 | 246 |
| 29 and above | 246 | 250 | 246 |

Blue saturates at 14, red and green at 29. Averaging the rendered output over
the island's actual shade histogram and comparing against the saturated entry
gives a **saturated / as-authored ratio of (1.348, 1.306, 1.023)**, against the
measured retail / reconstruction-macro transfer function of
**(1.360, 1.285, 1.073)** over 61,930 paired terrain pixels.

That is the whole measured deficit, to within 1–5% per channel. Retail's visible
terrain renders as if the lighting index were at the gradient's saturation
point; the authored plane averages 22. **No change to the plane the asset
actually contains can reach retail's brightness — clamping the entire island to
63 reproduces exactly the ratio above and no more.** The mechanism that puts
retail at saturation is not identified by this pass and was not invented.

`0x0047eff0` is the only PC macro producer: its three call sites are all inside
`CLandscapeTexture__UpdateTile` @ `0x0048ea80` and
`CLandscapeTexture__UpdateTileRange` @ `0x0048ef00`.

## 6. Eliminated: the second, coloured terrain lighting path

`CDXEngine__GenerateLandscapeCacheTileChunk` @ `0x00541f50` lights terrain from
a per-node RGB colour at height-field descriptor `+0x20`, record stride `0x18`,
colour at `+8`, bilinearly interpolated, applied as `byte * (c*256 + 0x400) >> 16`.
It is a genuine coloured terrain light and the reconstruction has no analogue —
but its **only** caller is `CDXEngine__BuildLandscapeTextureCache` @ `0x00547860`,
which writes `ps2data/LandscapeTextureCache.tex`. It is an offline PS2 asset
tool, not the PC runtime, and it is therefore not the source of the measured
gain.

## Boundary

Static evidence from the pristine specimen plus arithmetic over locally
materialized Level 100 asset bytes. It establishes the plane's provenance,
ownership, layout and axis order, and bounds what the plane can contribute to
output brightness. It does not establish why retail's rendered terrain sits at
gradient saturation.
