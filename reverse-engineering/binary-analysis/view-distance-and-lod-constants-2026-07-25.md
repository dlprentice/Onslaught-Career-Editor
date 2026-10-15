# View distance, cull, and LOD constants — recovered from the retail binary

Date: 2026-07-25. Values read from the pristine specimen's `.data` and from the
full-pass decompile exports. Cross-checked against the pinned reference source
where the file exists in the snapshot.

## The far plane: 700, and `DEFAULT_Z_FAR` is a red herring

`engine.h:14` defines `DEFAULT_Z_FAR = 256.0f` and `engine.cpp:44` assigns it to
`mFarZ` — **which the render path never reads**. The actual world far clip is a
local `float howfar = 700;` in `DXEngine.cpp:649` and again at `:788`, and the
retail binary agrees: `CDXEngine__Render` calls
`CDXEngine__SetProjectionMatrix(..., fVar17, 700.0, ...)`.

**This corrects an earlier finding** that the client's `Far = 700f` was "2.73x the
reference and larger than the whole map". 700 *is* retail's value. The client is
right and `DEFAULT_Z_FAR` should not be used as a target.

Other far planes in retail, for completeness: sky pass uses
`sqrt(SKY_HEIGHT^2 + (SKY_CELL_SIZE*SKY_RAD)^2)`; frontend Goodies uses 700.0;
several frontend renders use 7000.0; HUD overlays use 100.0. Gamut/visibility grid
depth is **2048.0** on PC (`PCEngine.cpp` uses 256 for the PS2 variant).

## Object, mesh and tree cull — CVar defaults from `.data`

| CVar | Global | Default |
| --- | --- | ---: |
| `cg_imposterfadestart` | `0x00631e94` | **39.0** |
| `cg_imposterfadeend` | `0x00631e98` | **40.0** |
| `cg_meshlodmedthreshold` | `0x00631e8c` | **10.0** |
| `cg_meshlodlowthreshold` | `0x00631e90` | **20.0** |
| `cg_meshlodbias` | `0x00631e88` | 1.0 |
| `cg_meshtexturelodbias` | `0x00631e9c` | 100.0 |
| `cg_meshsurfacelodbias` | `0x00631ea0` | 400.0 |
| `cg_debrisarea` | `0x006282fc` | 20.0 |
| `cg_debrisfadestart` | `0x00628300` | 15.0 |
| `cg_debrisfadeend` | `0x00628304` | 20.0 |

**`g_MeshQualityDistance` (`0x006321a0`) is the object/tree draw-cull distance.**
Default in `.data` is **30.0**. `CRTMesh__SetQualityLevel` rewrites it by quality
level:

| level | distance | lod bias | scale | lod table |
| ---: | ---: | ---: | ---: | ---: |
| 0 | **10.0** | 3.0 | 0.1 | 15.0 |
| 1 | **30.0** | 1.0 | 1.0 | 30.0 |
| 2 | **70.0** | 0.3 | 2.0 | 40.0 |

`CRTTree__Init` then forces `g_MeshQualityDistance = 45.0`. Trees cull with
`dist^2 - g_MeshQualityDistance^2 <= 0`; dynamic unit passes use
`(g_MeshQualityDistance + 10.0)^2`. The value is persisted to the options tail.

Level 2's **70.0** is the same constant independently measured as the tree
mesh-to-imposter swap distance from `defaultoptions.bea` offset `0x26CA`.

## Terrain LOD thresholds — already mirrored correctly

`CDXLandscape__UpdateLOD` constants, resolved from the binary:

| value | role |
| ---: | --- |
| **16384.0** = 128^2 | root texture-cache radius^2 |
| **4096.0** = 64^2 | texture level 1 threshold^2 |
| **1024.0** = 32^2 | texture level 2 threshold^2 |
| **256.0** = 16^2 | texture level 3 threshold^2 |
| **60.0 / 28.0 / 12.0** | forward camera shift per ring |
| **0.03** | camera smoothing |
| **8.0 / 512.0** | tile size / map extent |

These are already reproduced in `Level100HeightFieldAsset.cs` — camera smoothing
0.03, finest geometry radius 32^2, root texture radius 128^2, thresholds 64/32/16
with shifts 60/28/12. No divergence found.

## Fog render states

`CDXEngine`/`CRenderInfo` fog fields: start `+0xe1c`, end `+0xe20`, enable
`+0x2ec`, density `+0x2f0`, flushed as `D3DRS_FOGENABLE/FOGSTART/FOGEND/FOGDENSITY`
(`0x1c/0x24/0x25/0x26`). Defaults set at init: **enable = 1, start = 0.0,
end = 10.0**. Density comes from `MAP.GetFogDensity()` at render time.

### A provable Ghidra naming correction

`0x005513d0` is currently named `CDXEngine__SetVertexFormatDeferred`. Its only
caller does `FLD float ptr [0x006fbe60]` — which is `MAP + 0x1098`, the fog density
field — and the member it writes (`this+0x2f0`, dirty byte `+0xe2d`) is flushed as
`RenderState_Set(0x26 /* D3DRS_FOGDENSITY */)`. It is `CRenderInfo::SetFogDensity`,
matching `DXEngine.cpp:769`. Not yet applied.

## CHFD fields `0x1050`-`0x1074` are dead on the PC build

A scan of the entire `.text` for the absolute addresses of each field returns
**zero references** for all of `0x1050, 54, 58, 5c, 60, 64, 68, 6c, 70, 74`, and
also for `0x1088`. By contrast the named fields resolve cleanly — fog colour
`0x1078` has 2 references, sun colour `0x107C` has 5, ambient `0x108C` has 5, fog
density `0x1098` has 2, sun vector `0x10A4/A8/AC` has 4/4/3.

Their magnitudes (18000, 12000, 30000, 10000, 2000, 900) sit far outside the
512-unit world and the 700-unit far plane, so they are most likely PS2- or
editor-era view-distance or fog-range fields in millimetres or an editor unit
scale. **Nothing in the retail PC executable names or consumes them.** The PC
binary cannot supply names; only the PS2/Xbox builds or the editor could.

The coverage bound is worth stating: 558 of 6,969 functions lack decompile
exports, but the raw `.text` absolute-address scan covers 100% of code bytes, so
the zero-reference result is not limited by that gap.

## Version-50 world record tail

`CWorld__LoadWorld` (`0x0050b9c0`) accepts versions `0x2b..0x32` (43-50). At
version 50 the tail is exactly: **11 dwords, then 3 x (4-byte plane version +
8192-byte plane), then 1 trailing dword.** Five extra dwords exist only for
versions 45-47.

The three 8,192-byte 256x256 bitmaps are **occupancy / pathfinding bitplanes**,
not imagery. `CWorld__InitLODLists` allocates three of them with slope thresholds
**35.0 / 45.0 / 60.0**; `CWorld__InitOccupancyBitplanes` stores
`max_slope_degrees * 0.01745329` (degrees to radians) at `bitplane_base + 0x2000`.

The class is **`CWorld`**, proven by the retail alloc debug string
`C:\dev\ONSLAUGHT2\world.cpp`. There is no `CBaseWorld` or `CRealWorld` anywhere in
the reference snapshot or the RE corpus.

Of the 11 leading dwords, **six are written and never read** (`0x008a9b84`, `88`,
`9c`, `a0`, `a4`, `a8`), the first three are read and discarded on the retail path,
and only `_DAT_008a9bb0` has a consumer — a message-display duration read by
`CMessageBox__TryAdvanceQueuedMessage`.

## OID ordinals, derived from `__LINE__` alloc arguments

Recovered by matching the `__LINE__` argument in retail's
`CDXMemoryManager__Alloc(..., "C:\dev\ONSLAUGHT2\InitThing.cpp", line)` calls
against the `new` statements in the pinned `InitThing.cpp`:

| OID | class |
| ---: | --- |
| 7 | `CTree` |
| **8** | `CUnit` |
| **15** | `CStart` |
| 19 | `CSpawnerThing` |
| 25 | `CBuilding` |
| 26 | `CCutscene` |
| 28 | `CSquad` |
| 33 | `CWall` |
| **35** | `CFeature` |
| **36** | `CSphereTrigger` |
| 39 | `CHazard` |
| 41 | `CSpawnPoint` |

Note `EThingType` is a **bitmask**, not an ordinal (`thing.h:174` tests
`type & mThingType`); these OID values are a separate ordinal space.

**18, 27 and 37 have no `InitThing` subclass** and fall through to plain
`CInitThing`, but do exist in `OID__CreateObject`: 18 allocates `0x40` as a plain
`CThing`; 27 shares its case body with 21 and allocates `0x7c` as a
`CComplexThing`; 37 allocates `0x80` as a `CComplexThing`. No source name is
recoverable — `Oids.h` and `oids.cpp` are not in the GPL snapshot and those
vtables carry no RTTI string.
