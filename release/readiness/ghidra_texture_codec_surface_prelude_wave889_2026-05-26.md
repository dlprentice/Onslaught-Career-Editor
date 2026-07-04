# Ghidra Texture Codec Surface Prelude Wave889 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `texture-codec-surface-prelude-wave889`

Task anchor: Wave889 texture codec surface prelude.

Wave889 saved Ghidra function comments and tags for 27 texture codec, surface-node, mapped-resource, vertex-shader parser, and resample prelude rows from `0x00579a9a CVertexShader__CompileScriptWithDirectiveParser` through `0x0057cf60 CDXTexture__CopyDxtBlockRegion`. Existing names and signature displays were preserved; the pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00579a9a CVertexShader__CompileScriptWithDirectiveParser` | Initializes directive parser/preprocessor state, dispatches script loading by version, rejects leftover tokens, and optionally emits concatenated text. |
| `0x00579b39 CDXTexture__LookupNamedFormatDescriptor` | Binary-searches descriptor table `0x005e9340`, checks required flags, and optionally copies the three-dword descriptor row. |
| `0x00579cbe CDXTexture__FreeSurfaceNodeTree` | Recursively frees surface-node children at `+0x4c/+0x50` and owned buffers when ownership flags are set. |
| `0x00579e08 CDXTexture__DecodeBmpDibFromMemory` | Large BMP/DIB in-memory decode body tied to the shared texture surface-node state. |
| `0x0057ca6a CDXTexture__DecodeFromMemory_WithFallbackCodecs` | Stack-locked fallback dispatcher tries BMP, PPM, DDS, JPEG, PNG, TGA, and DIB decode paths and cleans failed partial allocations. |
| `0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode` | Selects output format descriptors, optionally converts surface-node chains, opens mapped output context, and dispatches BMP/JPEG/DDS-style writers. |
| `0x0057cca4 CFastVB__BuildResampleKernelBuckets` | Allocates variable-length one-dimensional resample bucket tables and accumulates per-source weights. |
| `0x0057cf60 CDXTexture__CopyDxtBlockRegion` | Validates 4x4 block alignment and copies DXT1/DXT2-5 block rectangles across row/depth strides. |

Read-back evidence:

- `ApplyTextureCodecSurfacePreludeWave889.java dry`: `updated=0 skipped=27 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyTextureCodecSurfacePreludeWave889.java apply`: `updated=27 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyTextureCodecSurfacePreludeWave889.java final dry`: `updated=0 skipped=27 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 27 metadata rows, 27 tag rows, 74 xref rows, 4329 instruction rows, and 27 decompile rows.
- Queue after Wave889: 6113 total, 6054 commented, 59 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict proxy `6054/6113 = 99.03%`.
- Next raw commentless row: `0x0057d0ee CWaypointManager__BoxBlurPackedColorRows_Scalar`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-040930_post_wave889_texture_codec_surface_prelude_verified`, 19 files, 173149063 bytes, `DiffCount=0`.

What this proves:

- The 27 target function rows exist in the saved Ghidra project.
- The saved names/signature displays match pre-state metadata.
- The saved comments and tags include `texture-codec-surface-prelude-wave889` and `wave889-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to metadata, tags, xrefs, instructions, and decompile exports.

What remains unproven:

- Exact texture, codec, surface-node, mapped-file, descriptor, parser, and resample table layouts.
- Exact source-body identity.
- Runtime texture decode/encode/export/resample/render behavior.
- BEA patching behavior.
- Rebuild parity.
