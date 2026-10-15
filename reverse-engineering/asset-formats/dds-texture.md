# DDS-in-AYA texture contract

Status: active format contract — complete AYA/DDS header census, a complete
stored mip-chain and alpha census, and a check of every lower mip level's pixels;
render semantics remain bounded
Date: 2026-08-22
Last updated: 2026-10-16 (mip-chain and alpha census of all 847 textures; every lower mip level decoded and checked)
Verdict: all 847 AYA/DDS headers are accounted for, and every file's payload is
exactly the mip chain its header declares, in one of four pixel formats; font,
upload, and render fidelity remain bounded or open.
Evidence: MEASURED — all 847 texture rows in
`G:\bea-asset-mirror\INDEX.jsonl` were re-aggregated read-only. Retail VAs are
static routes from named pristine-binary notes.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Population

The installed tree contains **847** DDS payloads inside the PC AYA envelope:

| Shelf | Files | Stored DDS family |
| --- | ---: | --- |
| `resources/dxtntextures` | 800 | 212 DXT1, 588 DXT2 |
| `resources/textures` | 47 | 38 A1R5G5B5-shaped masks, 9 A8R8G8B8-shaped masks |

Every file inflates to magic `DDS `. The 2026-08-22 index aggregate reports the
combined mip-count field distribution: 0=593, 5=2, 6=14, 7=32, 8=40, 9=57,
10=105, 11=4. The most common combined dimensions are 512×512 (207),
1024×1024 (152), 128×128 (146), 64×64 (102), and 256×256 (87).

## Container and header layout

After concatenating AYA members, the payload is a legacy DDS file:

| File offset | Field |
| ---: | --- |
| `0x00` | ASCII `DDS ` |
| `0x04` | `DDS_HEADER.dwSize` (standard value 124) |
| `0x08` | header flags |
| `0x0C` / `0x10` | height / width |
| `0x18` / `0x1C` / `0x20` | depth / mip count / reserved-header start |
| `0x4C` | `DDS_PIXELFORMAT` (size, flags, fourcc/RGB fields and masks) |
| `0x6C` | caps block |
| `0x80` | first surface level for this legacy non-DX10 family |

The mirror index retains width, height, mip count, pixel-format flags, fourcc or
RGB masks, caps, and selected decode notes. It decodes mip level zero for the
catalog; that does not make later mip levels or rendered pixels proved.

For the 800 compressed files, DXT1 uses 8-byte 4×4 blocks and DXT2 uses 16-byte
blocks with explicit alpha and a premultiplied-alpha declaration. The current
catalog intentionally stores compressed colour values without an automatic
un-premultiply because prior project evidence eliminated that transform as a
rendering fix. That is a project decode decision, not a universal DXT2 rule.

## Names are requests, not storage contracts

Names flatten source paths with `%` and often end in strings such as
`A1R5G5B5`, `A4R4G4B4`, `X8R8G8B8`, or `A8R8G8B8`. The complete corpus refutes
using that suffix as stored format: for example, 311 A8R8G8B8-suffixed names and
all 242 common A1R5G5B5-suffixed names store DXT2, while 116 common
X8R8G8B8-suffixed names store DXT1. Read the DDS header.

## Retail decoder anchors

| VA | Static identity | Demonstrated boundary |
| --- | --- | --- |
| `0x00556CC0` | `CTexture__ctor` | Constructs a `CDXTexture`-RTTI object and installs vptr `0x005E59A0`. |
| `0x00557060` | `CDXTexture__EnsureLoaded` | Vtable slot used by texture objects. |
| `0x00557300` | `CDXTexture__LoadTextureFromFile` | File/load path with resource-handle validation. |
| `0x005586E0` | `CDXTexture__DumpTextureToRGBA` | CPU-side RGBA dump helper. |
| `0x00559BE0` | `CDXTexture__Deserialize` | Tagged serialized texture reader using `CChunkReader`. |
| `0x00574492` | `CDXTexture__UploadDecodedBufferToSurface` | Static decoded-buffer handoff to a texture surface. |
| `0x0057BF1F` | `CDXTexture__BuildDdsSurfaceNodeTree` | Validates DDS magic/header and builds mip/depth nodes and extents. |
| `0x0057CA6A` | `CDXTexture__DecodeFromMemory_WithFallbackCodecs` | Static fallback order BMP→PPM→DDS→JPEG→PNG→TGA→DIB. |
| `0x0053A040` | raw inherited trampoline | Jumps to `0x00557060`; not a separate decoder body. |

See
[`texture-resource-decode-static-contract.md`](../binary-analysis/texture-resource-decode-static-contract.md),
[`CTexture__ctor.md`](../binary-analysis/functions/CTexture.cpp/CTexture__ctor.md),
`ghidra-fullpass-findings/W012/primary/A11.md` (private RE archive),
and
[`coordinate-long-tail.md`](../binary-analysis/functions/coordinate-long-tail.md).
Static routes show ownership and format dispatch, not decoded-pixel correctness.

## Decoder/tool evidence

- [`tools/BeaAssetExportHarness/Program.cs`](../../tools/BeaAssetExportHarness/Program.cs)
  enumerates both texture shelves and calls the pinned AYAResourceExtractor and
  DDS decoder assemblies.
- [`game-assets/aya-asset-format.md`](../game-assets/aya-asset-format.md)
  documents the external extractor's DXT/vertex assumptions and its corrected
  non-square output bug.
- The mirror's `aya-dds-png/v1` detail rows preserve header fields and bounded
  level-zero output metadata. Derived PNGs are not specimen evidence and are not
  tracked.

## Mip-chain and alpha census (2026-10-16)

`python tools/dds_census.py --game GAME_FOLDER` re-read every installed texture
(manifest digest over sorted `shelf/name sha256` lines:
`65b8c8c74e513d23b5ddd1f059a28759699bf14b17eb20b6ef85e11b34acc8e5`) and checked each
file's DDS header against its stored bytes. All 847 pass with no exception:

- the payload after the 128-byte header is exactly the sum of the declared mip
  levels for the declared format: DXT1 blocks are 8 bytes, DXT2 blocks 16, and
  A1R5G5B5 and A8R8G8B8 pixels 2 and 4 bytes;
- the header's linear size (or pitch) equals the top level's size, the mipmap
  cap agrees with the mip count, and no file is a cube map or volume;
- every width and height is a power of two (739 square, 108 not);
- every mipmapped file carries the full chain down to one pixel along its longer
  side; 593 files have a single level.

| Shelf and format | Files |
| --- | ---: |
| `dxtntextures` DXT1 | 212 |
| `dxtntextures` DXT2 | 588 |
| `textures` A1R5G5B5 | 38 |
| `textures` A8R8G8B8 | 9 |

| Mip levels | Files |
| --- | ---: |
| 1 | 593 |
| 5 / 6 / 7 / 8 | 2 / 14 / 32 / 40 |
| 9 / 10 / 11 | 57 / 105 / 4 |

Alpha at the top level:

| Format | Opaque | On/off only | Graded |
| --- | ---: | ---: | ---: |
| DXT1 | 212 | 0 | — |
| DXT2 | 190 | 208 | 190 |
| A1R5G5B5 | 0 | 38 | — |
| A8R8G8B8 | 0 | 2 | 7 |

No DXT1 texture uses DXT1's transparent colour, so every DXT1 texture is opaque.
The companion decodes the top level of all 847 (its `Development/AssetCheck.cs`
probe).

## Lower mip levels (2026-10-16)

`python tools/dds_census.py --game GAME_FOLDER --mips` decodes every stored level of
the 254 mipmapped textures. It compares each level with a 2×2 box reduction of the
decoded level above it.

Colour follows that reduction closely. The table gives the worst mean absolute RGB
difference (0–255) for any level in each size band, by the level's smaller side:

| Level size | Worst mean RGB difference |
| --- | ---: |
| 64 px and up | 8.88 |
| 16–32 px | 11.44 |
| 4–8 px | 20.27 |
| 1–2 px | 20.54 |

The larger differences are confined to levels of 8 pixels or fewer, where one
compressed block holds the whole level in four colours. Enlarged side by side, those
tiny levels show the same image, with regions shifted by about a pixel or hues
moved: `meshtex\f_trooperd`'s 8×8 level, for example, or
`meshtex\FB_hangertop01`'s 4×4 level. The colours are what a box filter followed by
per-level compression would give; the exact filter is open.

Alpha in lower levels is not averaged. Consider the 232 mipmapped textures whose
alpha is only on or off: 19 with cut-outs such as `meshtex\Dead Tree 01_Branches`,
and the fully opaque rest. In every level below the top of every one of them, a
pixel is opaque exactly when at least two of its four parent pixels in the level
above are opaque, and transparent otherwise:

| Opaque parents | Stored opaque |
| ---: | ---: |
| 0 | 0 of 113,043 |
| 1 | 0 of 5,679 |
| 2 | 10,040 of 10,040 |
| 3 | 6,514 of 6,514 |
| 4 | 11,735,708 of 11,735,708 |

That is the parents' average alpha thresholded at one half, inclusive. So cut-outs
stay solid as they shrink, and their opaque share grows toward the smallest level.
`Dead Tree 01_Branches` goes from 10% opaque at 256×256 to 50% at 2×2 and fully
opaque at 1×1. Lower levels of the 22 textures with graded alpha were measured for
colour only.

## Fonts and text rendering

The mirror contains no loose `.ttf`, `.otf`, or other standalone font-file
family. The 47 uncompressed resource textures include nine font/frontend/system
or HUD assets; font glyph pixels are therefore texture assets, not a separate
installed font container. `CDXFont__CreateGDIFont @ 0x0053FB00` is a static font
owner that also reaches `CDXTexture__GetAnimatedFrame`; it does not prove that a
shipped external font file exists.

## Open questions and falsifiers

- Which filter made the lower levels' colour, and does it work on DXT2's
  premultiplied values? The cheapest falsifier is to reproduce one chain from its top
  level with candidate filters and compare the compressed blocks.
- Establish exact colour-space, premultiplication, sampler, and upload behavior
  with a controlled render capture on copied assets.
- Path flattening, the 65-character cut, the `mustbe_` prefix and the DXTn fallback
  are now read from the matched loader (`CDXTexture::LoadFrame`, `0x00557300`;
  [goodie-resources.md](goodie-resources.md)). Collision and case behaviour, and
  the precedence at run time, still want a file-I/O trace.
- Identify which nine uncompressed assets feed font/HUD owners and map glyph
  metrics to texture regions.
- Keep malformed DDS tests outside the pristine shelf and use a fail-closed
  disposable copy.

## Claim boundary

All 847 wrappers, DDS headers and stored mip chains are accounted for, with their
formats and alpha use. Every lower level's colour tracks a 2×2 reduction of the
level above, and on/off alpha follows the at-least-two-of-four rule without
exception. The exact colour filter, DXT2 premultiplication at render time, font
layout, GPU upload, render state, and parity remain open.
