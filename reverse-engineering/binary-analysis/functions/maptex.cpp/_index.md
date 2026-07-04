# maptex.cpp - Map Texture System

Wave1195 current-risk update: Wave1195 (`wave1195-cmaptex-cmapwho-support-tail-current-risk-review`) accounts for `12 CMapTex/CMapWho support-tail score16 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. CMapTex rows are `CMapTex__Reset`, `CMapTex__DownsampleTexture`, `CMapTex__CopyFromOther`, and `CMapTex__Deserialize`; support-tail MapWho rows are `CMapWhoEntry__Init`, `CMapWho__SetIteratorFromSectorHead`, `CMapWho__AdvanceIteratorAndGetCurrent`, `CMapWho__IsSectorCoordInBounds`, `CMapWho__SetupNextRadiusLevel`, `CMapWho__DebugDrawSector`, `CMapWho__DebugDraw`, and `CMapWhoEntry__Invalidate`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=12 tags_added=132 missing=0 bad=0`, then `updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=12 tags_added=132 missing=0 bad=0`, then final dry updated=0 skipped=12. No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consult used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; expanded static surface remains `1560/1560 = 100.00%`; Wave1108 current focused accounting is `877/1179 = 74.39%`; current risk candidates: 6166; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 302; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `37 xref rows`, `561 instruction rows`, and `12 decompile rows`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-200142_post_wave1195_cmaptex_cmapwho_support_tail_current_risk_review_verified`. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference; exact CMapTex/CMapWho/CMapWhoEntry/sector/texture/pixel layouts, exact source-body identity, runtime terrain texture behavior, runtime spatial-query behavior, runtime debug rendering behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1195; wave1195-cmaptex-cmapwho-support-tail-current-risk-review; 877/1179 = 74.39%; 12 CMapTex/CMapWho support-tail score16 current-risk rows; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 302; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=12 skipped=0; comment_only_updated=12; tags_added=132; final dry updated=0 skipped=12; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CMapTex__Reset; CMapTex__DownsampleTexture; CMapTex__CopyFromOther; CMapTex__Deserialize; CMapWhoEntry__Init; CMapWho__SetIteratorFromSectorHead; CMapWho__AdvanceIteratorAndGetCurrent; CMapWho__IsSectorCoordInBounds; CMapWho__SetupNextRadiusLevel; CMapWho__DebugDrawSector; CMapWho__DebugDraw; CMapWhoEntry__Invalidate; 0 / 0 / 0; 6411/6411 = 100.00%; 37 xref rows; 561 instruction rows; 12 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-200142_post_wave1195_cmaptex_cmapwho_support_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.

**Source File:** `[maintainer-local-source-export-root]\maptex.cpp`
**Debug String Address:** `0x0062db04`
**Functions Found:** 6

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

The CMapTex class manages terrain mixer textures used for blending between different terrain types (grass, rock, sand, snow, road, concrete). The system loads TGA texture files and stores them in RGBA format with height/displacement information in the alpha channel.

## Wave427 Saved-Ghidra Re-Audit Note

Wave427 (2026-05-14) hardened all six saved `CMapTex` functions after fresh metadata, decompile, xref, instruction, tag, caller, and callsite-instruction read-back. The saved names were preserved, but signatures/comments/tags were corrected so the functions no longer present as `undefined` or generic `param_N` debt in Ghidra.

The retail binary contains a debug string for `[maintainer-local-source-export-root]\maptex.cpp`, but `maptex.cpp` is absent from the current Stuart source snapshot in this repo. Treat this page as binary-led static evidence plus source-path/string context, not source-body parity. Runtime terrain texture behavior, exact `CMapTex` layout, exact locals/types, BEA launch, game patching, and rebuild parity remain unproven.

## Class Structure (Reconstructed)

```cpp
class CMapTex {
    void*   m_pTextureData;     // +0x00: Main texture buffer
    int     m_field_04;         // +0x04: Unknown (possibly flags)
    void*   m_pSecondaryData;   // +0x08: Secondary texture buffer
    short   m_nTextureSet;      // +0x0C: Current texture set ID (-1 = unloaded)
    int     m_nTexelSize;       // +0x10: Size per texel (width*width*4)
    int     m_nTextureCount;    // +0x14: Number of textures loaded
    int     m_nTextureWidth;    // +0x18: Texture dimension (e.g., 64, 128)
    int     m_minHeights[6];    // +0x1C: Min height per texture
    int     m_maxHeights[6];    // +0x34: Max height per texture
};
```

## Texture Types

The system supports 6 terrain texture types, loaded from `data\textures\mixers\`:

| Index | Name     | File Pattern              |
|-------|----------|---------------------------|
| 0     | grass    | grass##.tga               |
| 1     | rock     | rock##.tga                |
| 2     | sand     | sand##.tga                |
| 3     | snow     | snow##.tga                |
| 4     | road     | road##.tga                |
| 5     | concrete | concrete##.tga            |

Full path format: `data\textures\mixers\%s%.2d.tga` (e.g., `data\textures\mixers\grass00.tga`)

## Functions

### CMapTex__Reset
| Property | Value |
|----------|-------|
| Address | `0x00491180` |
| Returns | `void` |
| Saved Signature | `void __fastcall CMapTex__Reset(void * this)` |
| Calling Convention | fastcall-style ECX this-only helper |

**Purpose:** Resets the CMapTex object and frees allocated memory.

**Behavior:**
- Sets texture set ID to -1 (0xFFFF)
- Frees main texture buffer if allocated
- Frees secondary buffer if allocated

```cpp
void CMapTex::Reset() {
    m_nTextureSet = -1;
    if (m_pTextureData) {
        free(m_pTextureData);
        m_pTextureData = NULL;
    }
    if (m_pSecondaryData) {
        free(m_pSecondaryData);
        m_pSecondaryData = NULL;
    }
}
```

---

### CMapTex__LoadTexture
| Property | Value |
|----------|-------|
| Address | `0x004911c0` |
| Returns | `int` (1 = success, 0 = failure) |
| Saved Signature | `int __thiscall CMapTex__LoadTexture(void * this, char * texture_path, int texture_width, int texture_index)` |
| Parameters | `char * texture_path, int texture_width, int texture_index` |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Loads a single TGA texture into the texture array.

**Behavior:**
- Uses CTGALoader to load the TGA file
- Copies RGB data to texture buffer (BGR -> RGBA conversion)
- If alpha channel exists: converts to signed height value (alpha >> 2) - 32
- Tracks min/max height values per texture (stored at offsets +0x1C and +0x34)
- Height range: -32 to +31 (6-bit signed from 8-bit alpha)

**Memory Layout per texel:** 4 bytes (R, G, B, Height)

---

### CMapTex__DownsampleTexture
| Property | Value |
|----------|-------|
| Address | `0x00491340` |
| Returns | `void` |
| Saved Signature | `void __thiscall CMapTex__DownsampleTexture(void * this, void * dest_buffer, void * src_buffer)` |
| Parameters | `void * dest_buffer, void * src_buffer` |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Downsamples a texture by 2x in each dimension using box filter averaging.

**Algorithm:**
- 2x2 box filter: averages 4 source pixels to produce 1 destination pixel
- Processes RGBA separately
- Height channel (alpha) uses signed arithmetic for correct averaging

---

### CMapTex__LoadMixerTextureSet
| Property | Value |
|----------|-------|
| Address | `0x004914b0` |
| Returns | `int` (1 = success, 0 = failure) |
| Saved Signature | `int __thiscall CMapTex__LoadMixerTextureSet(void * this, int set_id, int texture_count, int texture_width)` |
| Parameters | `int set_id, int texture_count, int texture_width` |
| Calling Convention | thiscall (ECX = this) |
| Source Line | 0x97 (151) |

**Purpose:** Loads a complete set of mixer textures for a given terrain set.

**Behavior:**
- Prints warning if loading manually: "Warning : Loading mixer texture set %d manually!"
- Skips if set already loaded (checks m_nTextureSet)
- Frees existing buffers
- Allocates new buffer: `textureWidth * textureWidth * 4 * textureCount` bytes
- Iterates through 6 texture types (grass, rock, sand, snow, road, concrete)
- Loads each via `CMapTex__LoadTexture()`

**Memory Allocation:**
- Uses custom allocator at `0x005490e0` with source tracking (file, line)
- Allocation ID: 0x30

---

### CMapTex__CopyFromOther
| Property | Value |
|----------|-------|
| Address | `0x004915d0` |
| Returns | `void` |
| Saved Signature | `void __thiscall CMapTex__CopyFromOther(void * this, void * source_map_tex)` |
| Parameters | `void * source_map_tex` |
| Calling Convention | thiscall (ECX = this) |
| Source Line | 0xAF (175) |

**Purpose:** Creates a half-resolution copy from another CMapTex object.

**Behavior:**
- Skips if texture sets match
- Frees existing buffers
- Copies texture set ID and count from source
- Sets width to half of source width (source->width >> 1)
- Allocates new buffer at half resolution
- Copies min/max height values from source
- Downsamples each texture using `CMapTex__DownsampleTexture()`

**Use Case:** Creating LOD (level-of-detail) versions of terrain textures.

---

### CMapTex__Deserialize
| Property | Value |
|----------|-------|
| Address | `0x004916c0` |
| Returns | `void` |
| Saved Signature | `void __thiscall CMapTex__Deserialize(void * this, void * chunk_reader, int texture_index)` |
| Parameters | `void * chunk_reader, int texture_index` |
| Calling Convention | thiscall (ECX = this) |
| Source Lines | 0x17C (380), 0x19A (410) |

**Purpose:** Loads CMapTex data from a serialized stream (save file or level data).

**Behavior:**
- Calls the shared CChunkReader cursor helpers (`CChunkReader__GetNext`, `CChunkReader__Read`; Wave983 `cchunkreader-resource-review-wave983`)
- The `texture_index` argument is callsite/`RET 0x8` proven, but it is not consumed in the current decompile.
- Reads 0x4C (76) bytes of object header data
- If main texture buffer exists:
  - Allocates new buffer: `textureCount * texelSize` bytes
  - Reads texture data from stream
- If secondary buffer exists:
  - Allocates new buffer: `textureCount << 12` bytes (textureCount * 4096)
  - Reads `textureCount << 10` bytes (textureCount * 1024)

**Stream Format:**
1. 76-byte header
2. Main texture data (if present)
3. Secondary texture data (if present)

---

## Related Functions (Not in maptex.cpp)

| Address | Name | Notes |
|---------|------|-------|
| `0x00491060` | CHeightField__DeserializeMapAndInitResources | Wave426-corrected MAP deserialize/resource-init helper; calls CHeightField__Load and CMixerMap__Init |
| `0x00549220` | Memory free | Used by Reset() |
| `0x005490e0` | Memory alloc | Custom allocator with source tracking |
| `0x00423910` | `CChunkReader__GetNext` | Shared tagged-chunk header cursor; Wave983 verified source-backed CChunkReader wording |
| `0x00423960` | `CChunkReader__Read` | Shared tagged-chunk payload reader; Wave983 verified source-backed CChunkReader wording |

Wave983 CChunkReader resource review (`cchunkreader-resource-review-wave983`) verified these helper labels with `6222/6222 = 100.00%` live closure, Wave911 progress `384/1408 = 27.27%`, expanded static surface `443/1478 = 29.97%`, and backup `[maintainer-local-ghidra-backup-root]\BEA_20260531-001624_post_wave983_cchunkreader_resource_review_verified`. The same tranche also verified the adjacent `CChunkReader__Skip` cursor helper even though this map texture path primarily xrefs `GetNext`/`Read`. Exact CChunkReader structure layout, runtime archive/resource I/O behavior, exact archive schema coverage, BEA patching, and rebuild parity remain separate proof. The next slice is a Wave900+ recheck before any new candidate cluster.

## Technical Notes

1. **Texture Set Caching:** Functions check if the requested texture set is already loaded before reloading, using m_nTextureSet as a cache key.

2. **Memory Management:** Uses a custom allocator (0x005490e0) that tracks allocation source (file path and line number) for debugging.

3. **Height Encoding:** Alpha channel encodes height as: `(alpha >> 2) - 32`, giving a signed 6-bit range (-32 to +31).

4. **LOD System:** The CopyFromOther function creates half-resolution copies, suggesting a mipmapping or LOD system for terrain rendering.

5. **Texture Format:** All textures stored as RGBA with 4 bytes per texel, even though source TGAs appear to be RGB with optional alpha.

## String References

| Address | String |
|---------|--------|
| `0x0062da84` | "Deserializing map" |
| `0x0062dae4` | "data\\textures\\mixers\\%s%.2d.tga" |
| `0x0062db04` | "[maintainer-local-source-export-root]\\maptex.cpp" |
| `0x0062db24` | "Warning : Loading mixer texture set %d manually!" |

## Texture Name Pointers

Array at `0x0062da98`:
- `0x0062dadc` -> "grass"
- `0x0062dad4` -> "rock"
- `0x0062dacc` -> "sand"
- `0x0062dac4` -> "snow"
- `0x0062dabc` -> "road"
- `0x0062dab0` -> "concrete"
