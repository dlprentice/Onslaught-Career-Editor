# LandscapeTexture.cpp - Function Analysis

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x0048e950` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Last updated: 2026-05-18

## Source And Evidence Status

Retail debug-path evidence names `[maintainer-local-source-export-root]\LandscapeTexture.cpp`, and RTTI names `CLandscapeTexture` through type descriptor `0x0062d8c8`. The current `references/Onslaught/` source snapshot does not include a matching `LandscapeTexture` source file, so Wave421 relies on saved Steam retail Ghidra read-back: metadata, decompile, xrefs, instructions, tags, and vtable-adjacent context.

Treat this page as static retail-binary evidence, not source-body parity and not runtime terrain-render proof.

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`CLandscapeTexture` manages terrain texture lifetime, mip setup, pending tile-update records, RGB565 tile copying, per-tile updates, alpha-overlay blending, and inclusive tile-range updates for the landscape rendering path.

## Vtable-Adjacent Context

Two vtable-like addresses are used by the constructors:

| Address | Current evidence |
| --- | --- |
| `0x005dc1d8` | Installed by `CLandscapeTexture__Constructor` after `CIBuffer__Constructor`; some slots resolve to known `CIBuffer`/shared helpers while several pointer rows remain unconfirmed. |
| `0x005dc1f0` | Installed by `CLandscapeTexture__ConstructorMip` and restored by `CLandscapeTexture__Destructor`; several slots resolve to `CLandscapeTexture__Reset`, `CUMTexture__VFunc_03_ReleaseTextureResource`, shared no-op/return helpers, and other known helpers. |

The Wave421 vtable export is provisional. It includes `64` checked rows but also `NO_FUNCTION_AT_POINTER` rows such as pointers near `0x005449a0`, `0x0048e670`, and `0x0048e790`, followed by float-like data. Do not treat this as complete vtable recovery.

## Key Observed Offsets

| Offset | Observed role |
| ---: | --- |
| `+0x00` | Vtable pointer. |
| `+0x08` | Texture/surface pointer released by `FreeTexture`. |
| `+0x18` | Shared/static mode flag context. |
| `+0x24` | Setup mip level. |
| `+0x28` | Edge flags used by `SetupMipLevel`. |
| `+0x2c` | Dirty/tile-edge/update state depending on path. |
| `+0x30` | Setup byte count or tile-set index depending on path. |
| `+0x34` | Runtime mip level used by queue/tile helpers. |
| `+0x38` | Texture size. |
| `+0x3c` | Coordinate mask. |
| `+0x40` | Nonzero-mip update buffer pointer. |
| `+0x44` | Update buffer element count. |
| `+0x48` | U mask. |
| `+0x4a` | V mask. |

The offsets above are observed static use-sites, not a complete concrete class layout.

## Functions

| Address | Saved signature | Evidence notes |
| --- | --- | --- |
| `0x0048e310` | `void __thiscall CLandscapeTexture__FreeTexture(void * this)` | Releases texture/surface pointer `+0x08` through `OID__FreeObject` when present. |
| `0x0048e330` | `void * __thiscall CLandscapeTexture__Constructor(void * this)` | Calls `CIBuffer__Constructor`, installs `0x005dc1d8`, clears `+0x2c`, returns `this`. |
| `0x0048e360` | `void __thiscall CLandscapeTexture__SetupMipLevel(void * this, int mip_level, uint edge_flags)` | Stores mip/edge fields, derives tile-edge/count state, sets shared/static mode, dispatches vtable slot `+0x04`. |
| `0x0048e430` | `void * __thiscall CLandscapeTexture__ConstructorMip(void * this)` | Calls `CUMTexture__ctor_base`, installs `0x005dc1f0`, clears `+0x2c/+0x40`, returns `this`. |
| `0x0048e450` | `void __thiscall CLandscapeTexture__Destructor(void * this)` | Restores `0x005dc1f0`, frees update buffer, decrements `0x006fabf8`, releases shared texture state `0x006fabf4` when count reaches zero. |
| `0x0048e4d0` | `int __thiscall CLandscapeTexture__Init(void * this, int mip_level, int tile_set_index)` | Initializes masks, size/mask fields, nonzero-mip update storage, calls `CUMTexture__ConfigureByMode(this, DAT_0062d864, 1, 1)`, and refreshes shared texture/device state. |
| `0x0048e610` | `uint __thiscall CLandscapeTexture__Reset(void * this)` | Calls `CUMTexture__RecreateTextureResource`, handles dirty state, fills update buffer with `0xff`, or refreshes full range `0..63`. |
| `0x0048e7b0` | `void __cdecl CLandscapeTexture__ResetUpdateQueue(void)` | Resets global queue cursor `0x0062d868` to base `0x006fa7d8`. |
| `0x0048e7c0` | `void __cdecl CLandscapeTexture__FlushUpdateQueue(void)` | Walks 20-byte records between base and cursor, calls `UpdateTile`, compacts deferred records, writes compacted cursor. |
| `0x0048e880` | `void __thiscall CLandscapeTexture__QueueTileUpdate(void * this, uint tile_coord, int update_mode)` | Converts tile coordinate into mip/mask-adjusted texture X/Y, dedupes existing records, flushes near cap `0x006fabbf`, appends one 20-byte record. |
| `0x0048e950` | `void __thiscall CLandscapeTexture__CopyTileToTexture(void * this, int * tile_rect)` | Locks shared or per-instance texture memory and copies RGB565 pixels from `0x0067a7d8`. |
| `0x0048ea80` | `void __thiscall CLandscapeTexture__UpdateTile(void * this, uint tile_coord)` | Marks dirty state, derives tile rect, blits tile data, applies overlay alpha entries through `BlendAlpha`, then copies/unlocks or refreshes device state. |
| `0x0048ee00` | `void __cdecl CLandscapeTexture__BlendAlpha(short * dest, int pitch, byte * alpha, int x, int y, byte level, int size)` | Clips alpha mask bounds and blends RGB565 channels through parallel-channel mask `0x07e0f81f` for alpha bytes below `0x20`. |
| `0x0048ef00` | `void __thiscall CLandscapeTexture__UpdateTileRange(void * this, int min_x, int min_y, int max_x, int max_y)` | Loops an inclusive tile range from `min_y*64+min_x`, blits tiles, applies linked overlay alpha entries, copies the updated rect, and refreshes device state for shared textures. |

## Global Context

| Address | Observed role |
| --- | --- |
| `0x006fabf8` | Global `CLandscapeTexture` instance/reference count. |
| `0x006fabf4` | Shared texture state pointer released when the count reaches zero. |
| `0x006fabf0` | Global mip-level context used by copy/update helpers. |
| `0x006fabcc` | Per-instance/shared texture branch context. |
| `0x0062d868` | Current landscape tile-update queue cursor. |
| `0x006fa7d8` | Landscape tile-update queue base. |
| `0x0067a7d8` | Landscape RGB565 buffer used by copy/update paths. |

## Wave421 Saved Corrections

Wave421 saved signatures, comments, and tags for all fourteen existing `CLandscapeTexture` functions listed above. Wave422 then corrected the adjacent `0x0048f180` helper from stale `CDXLandscape__InvalidateTileMaskOrRefreshAll` to `CLandscapeTexture__InvalidateTileMaskOrRefreshAll` after read-back showed it marks `+0x2c`, fills optional update buffer `+0x40/+0x44` with `0xff`, or calls `CLandscapeTexture__UpdateTileRange` for the full `0..63` tile range.

| Address | Saved signature | Evidence notes |
| --- | --- | --- |
| `0x0048f180` | `void __thiscall CLandscapeTexture__InvalidateTileMaskOrRefreshAll(void * this)` | Corrected in Wave422 from stale `CDXLandscape` ownership; called by `CDXLandscape__Reset` with the landscape texture pointer. |

The Wave421 dry run reported `updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`; the apply reported `updated=14 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.

Read-back verified `14` metadata rows, `14` tag rows, `30` xref rows, `1862` instruction rows, `14` decompile exports, `64` vtable-adjacent rows, focused probe status `PASS`, and refreshed queue counts of `6043` functions, `1663` commented functions, `4380` commentless functions, `1861` undefined signatures, and `1817` `param_N` signatures. The actual live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260514_153419_post_wave421_landscape_texture_verified` with `19` files, `155159431` bytes, `HashDiffCount=0`, and `MissingCount=0`.

Wave422 read-back for `0x0048f180` is documented with the broader landscape patch tranche at `release/readiness/ghidra_landscape_patch_wave422_2026-05-14.md`.

Wave522 then hardened the adjacent `CUMTexture` helper island used by `CLandscapeTexture__ConstructorMip`, `CLandscapeTexture__Init`, and `CLandscapeTexture__Reset`. The key landscape-facing correction is that `CUMTexture__ConfigureByMode` is now `int __thiscall CUMTexture__ConfigureByMode(void * this, void * texture_size, int mode, int texture_count_or_depth)`, with `RET 0x0c` proving three explicit stack arguments after ECX. The old register-carryover caveat for the landscape configure call is resolved in the saved Ghidra signature/decompile, but runtime terrain texture behavior remains unproven. See [`CUMTexture.cpp`](../CUMTexture.cpp/_index.md).

## Remaining Limits

- Runtime terrain texture rendering is not proven.
- Runtime GPU upload behavior is not proven.
- Runtime update-queue ordering and scheduling are not proven.
- Complete concrete `CLandscapeTexture`, `CUMTexture`, and `CIBuffer` layouts are not proven.
- Exact local-variable names and recovered Ghidra data types remain open.
- Vtable-adjacent rows remain provisional and include unresolved pointer rows.
- BEA was not launched, patched, or debugged in this wave.
- This does not prove rebuild parity or game-behavior equivalence.
