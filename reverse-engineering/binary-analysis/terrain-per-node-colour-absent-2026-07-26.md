# The per-node terrain colour light is absent from the PC path

> Date: 2026-07-26
> Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe`, image base `0x00400000`,
> 2,506,752 bytes; sections `.text 0x00401000+0x1d6f9d`, `.rdata 0x005d8000`,
> `.data 0x00622000`.
> Assets: `local-lab/safe-copy-bea-pristine/data/`, read-only.
> Verdict: **precise negative.** No baked landscape texture cache ships or
> loads, and the per-node coloured light array does not exist in any shipped
> heightfield. No source changed.

This closes the last surviving candidate for the coloured, high-variance gain
measured between retail's terrain and the macro cache
(`retail/macro` 1.400 / 1.295 / 1.075, per-pixel gain sd 0.52 / 0.41 / 0.33).

## 1. The shape that was being chased

`CDXEngine__GenerateLandscapeCacheTileChunk` @ `0x00541f50` is a real coloured
per-node terrain light. Its receiver is a `CHeightField` (it reads `+0x1038`,
`+0x10c4`, `+0x10c8` — the same fields `CHeightField__Load` populates), and:

```
00542063  mov  ebx, dword ptr [ebx + 0x20]      ; node array base
00542073  lea  ecx, [ecx + ecx*2]               ; index * 3
0054207f  lea  ecx, [ebx + ecx*8]               ; ... * 8  -> stride 0x18
...
0054230e  mov  ecx, dword ptr [ecx + 8]         ; packed colour at node+8
00542311  mov  ebp, dword ptr [edx + 8]         ; second corner
00542336  and  ebp, 0xff                        ; byte-wise channel split
00542342  shl  ebp, 8                           ; and bilinear blend across
00542349  sub  ebp, ecx                         ; the tile's four corners
```

Four node corners are fetched, each channel is separated with
`and 0xff` / `and 0xff00`, and the corners are bilinearly interpolated across
the tile. That is exactly a coloured, high-frequency, per-channel term — which
is why it was the only remaining candidate.

## 2. No baked cache ships

The install tree has no `ps2data` directory and no `.tex` cache. Enumerated:

```
data/  Dial.raw  MissionScripts  Music  ParticleSets
       "battle engine configurations.dat"  "default physics.dat"
       language  resources  sounds  textures  video  worldheaders.dat
data/textures/  splash.tga        (one file)
data/resources/ *_res_PC.aya      (per-level archives)
```

A whole-tree search for `*land*`, `*cache*`, `*.tex`, `*ps2*` returns only
`MissionScripts/**/Land*.msl` mission scripts.

## 3. No loader — and the only writer is dead code

Both cache path strings occur exactly twice in the image, and only as string
data:

| VA | String |
| --- | --- |
| `0x00650ef8` | `ps2data\LandscapeTextureCache\texcache.dir` |
| `0x00650f24` | `ps2data\LandscapeTextureCache\texcache.tex` |

Scanning the entire 2,506,752-byte image for each string's address as a 4-byte
little-endian operand yields **exactly one reference each**:

| String VA | Sole reference | Enclosing function |
| --- | --- | --- |
| `0x00650f24` | `0x00547895` | `CDXEngine__BuildLandscapeTextureCache` @ `0x00547860` |
| `0x00650ef8` | `0x005478b8` | same |

Both are passed to the buffer-open helper at `0x0055e490` with mode string
`0x0063316c` = `"wb"` — write-binary. There is no read path.

`CDXEngine__BuildLandscapeTextureCache` is itself **unreachable**:

- Zero `E8`/`E9` relative call or jump targets in `.text` resolve to
  `0x00547860` (full linear scan of `0x00401000..0x005d7f9d`).
- Zero occurrences of `60 78 54 00` as an operand anywhere in the image, so it
  is in no vtable and no function-pointer table.
- The preceding function ends `ret 0xc` at `0x0054785c`, and `0x00547860`
  opens with a `__chkstk` prologue (`mov eax, 0x1062c; call 0x0055def0`), so it
  is not entered by fallthrough.

It is the sole caller of `CDXEngine__GenerateLandscapeCacheTileChunk`
(one relative call at `0x00547975`, no absolute references). So the per-node
colour interpolation above is dead in the shipped PC executable.

## 4. The per-node colour array does not exist in any shipped heightfield

`CHeightField__Load` @ `0x0047f750` blits the serialized `CHFD` record over
`this` at offset 0:

```
0047f7a6  cmp  eax, 0x13dc            ; CChunkReader size check
0047f7d4  push 0x13dc
0047f7d9  push edi                    ; edi = this
0047f7dc  call 0x00423960             ; CChunkReader::Read(this, 0x13dc, 1)
```

so field `+0x20` is whatever the asset carries. `tools/heightfield_node_array_probe.py`
inflates every `.aya` under `data/resources` and reads `+0x20`/`+0x24` of every
`CHFD` record of size `0x13dc`:

```
level100-heightfield.hfld.bin: +0x20=0x00000000 +0x24=0x00000000 grid=512x512
CHFD records probed: 67; with a non-zero node-array pointer: 0
```

**67 of 67 shipped heightfields carry a null node-array pointer** (66 in the
archives plus the extracted Level 100 `HFLD`).

Nothing allocates it at runtime either. Disassembling every ledger-known
function body and collecting every `mov dword ptr [reg + 0x20], reg/imm` that is
not frame-relative gives 288 sites; the only one on a heightfield-shaped
receiver is:

```
0047e87d  mov  dword ptr [edx + 0x20], 0     ; CHeightField__ResetCoreBuffersAndFlags
```

reached from `CHeightField__Constructor` @ `0x00490e10` (call at `0x00490e13`).
`CHeightField__DeserializeMapAndInitResources` @ `0x00491060` — the whole PC
load path — calls `CHeightField__Load`, then the `CMixerMap` chunk read at
`0x0089bd80`, then the mixer/detail/water setters, and never touches `+0x20`.

Readers of `CHeightField+0x20` in the image: the dead chunk generator above, and
nothing else. (`0x0047ef20`, saved as `CHeightField__RecomputeGridExtentsAndHeightRange`,
is called only from `CDXBattleLine__UpdateHeightmap` @ `0x0053a390` and
`CDXBattleLine__BuildMesh` @ `0x0053a5e0`, is gated on `[ecx+0x10] == 0xcaa24af0`,
and walks a float at element `+0` — it is a battle-line object, not the
heightfield.)

## 5. Level 100 has no unread coloured asset either

The complete chunk tree of `100_res_PC.aya`:

| Path | Count | Bytes |
| --- | --- | --- |
| `ERES` | 1 | 2,114,301 |
| `ERES/ENGN` | 1 | 2,114,293 |
| `ERES/ENGN/MAP!` | 1 | 1,546,261 |
| `ERES/ENGN/MAP!/HFLD` | 1 | 668,652 |
| `ERES/ENGN/MAP!/MMAP` | 1 | 877,589 |
| `ERES/ENGN/MAPT` | 7 | 567,964 |
| `SURF` | 1 | 18,564 |

`HFLD` decomposes exactly into `CHFD` (`0x13dc` at file offset `0x10`) plus
`HFDT` (`0xa2000` at `0x13ec`) — 8 + 8 + 5,084 + 8 + 663,552 = 668,652, with no
residue, so there is no colour payload hiding inside it. `MMAP` is a stream of
`MCEL` records (`CMCL` 20 bytes + `MXRS` 81 bytes each) and the seven `MAPT`
levels are the macro cache mips; `rebuild/tools/materialize_retail_assets.py`
already parses all of them.

## 6. What this eliminates

The candidate mechanism is not merely unused — its input does not exist. Any
future explanation of the measured gain must be something that reads data the
reconstruction already has, or a runtime state the static image does not
distinguish. It cannot be a per-node terrain light, and it cannot be a baked
landscape texture cache.

No gain, offset, or tint was introduced. The reconstruction's honest deficit
stands unchanged at terrain mid-band 91.15% material / meanD 35.4, full frame
63.81% / 26.5.

## Reproduce

```powershell
py -3 tools/heightfield_node_array_probe.py `
    --resources local-lab/safe-copy-bea-pristine/data/resources `
    --extra rebuild/OnslaughtRebuild.Core/Assets/Level100/level100-heightfield.hfld.bin
```

Static retail evidence and shipped-asset bytes only. Runtime behaviour of the
dead builder, the exact node struct layout beyond the `+0x18` stride and the
`+0x08` packed colour, and the PS2 build's use of this path remain unproven.
