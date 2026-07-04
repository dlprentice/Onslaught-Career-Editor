# Ghidra Texture Decode/Upload Tail Wave886 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `texture-decode-upload-tail-wave886`

Wave886 texture decode/upload tail saved comments/tags for ten texture and mapped-file decode/upload rows from `0x00573d80 CTexture__InsertNodeIntoTree` through `0x005758e6 CDXTexture__DecodeMappedMemoryEntry`. Existing names and signature displays were preserved because Ghidra still reports locked/hidden parameter storage for these helpers. The pass made no renames, no function-boundary changes, no executable-byte changes, did not launch BEA, and did not touch the installed Steam game.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00573d80 CTexture__InsertNodeIntoTree` | RB-tree insert helper reached from `0x00573530 CFastVB__InsertNodeIntoRBTreeWithHint_00573340`; allocates a `0x14`-byte node, links against sentinel `DAT_009d0c44`, and runs insert fixup rotations/recolors. |
| `0x00574492 CDXTexture__UploadDecodedBufferToSurface` | Upload helper called from decode/upload and copy fallback paths; validates inputs, defaults flags to `0x80004`, calls `CDXTexture__UploadSurfaceRegionWithFallback`, and invokes `CFastVB__InitDualTexelConversionPipeline`. |
| `0x00574662 CDXTexture__ConvertSurfaceWithActiveProfile` | Surface conversion helper that creates a texel codec profile, copies six-dword descriptors, invokes the dual texel conversion pipeline, shuts down the active profile, and releases the surface pair. |
| `0x0057473b CDXTexture__NormalizeTextureConversionParams` | Normalizes texture dimensions, mip counts, format descriptors, DXT block alignment, power-of-two restrictions, and device caps queried through vtable slot `+0x1c`. |
| `0x00574ae5 CDXTexture__DecodeMemoryAndUploadWithRect` | Decodes memory through `CDXTexture__DecodeFromMemory_WithFallbackCodecs`, derives or validates an upload rectangle, delegates upload, and frees the decoded surface-node tree. |
| `0x00574b9d CDXTexture__CopyOrUploadSurfaceRegionWithFallback` | Prefers direct D3D copy/update paths when descriptors/rectangles match, temporarily mutes D3D9 debug output, and falls back to upload plus decoded-buffer conversion. |
| `0x00574da5 CDXTexture__ConvertSurfaceRegionWithActiveProfile` | Compact mip-chain conversion wrapper around `CDXTexture__GenerateMipChainBySurfaceCopy`, `CDXTexture__CreateTexelCodecProfileFromSurfaceDesc`, and `CDXTexture__ConvertSurfaceWithActiveProfile`. |
| `0x0057511b Platform__OpenDecodeUploadMappedTexture` | Opens a supplied mapped texture path read-only, delegates to `CDXTexture__DecodeMemoryAndUploadWithRect`, and closes the handle; caller is `Platform__ProcessPendingScreenDump`. |
| `0x0057516c CDXTexture__DecodeMemoryToTextureObject` | Central memory-to-texture-object helper: decodes memory, handles palette/format mapping, normalizes creation params, creates 2D/volume/cube textures through device vtable slots, uploads/converts slices and mips, may generate mip chains, and releases temporary surfaces. |
| `0x005758e6 CDXTexture__DecodeMappedMemoryEntry` | Mapped-memory thunk called by `CDXTexture__LoadTextureFromFile` and `CDXTexture__DecodeMappedFileToTexture`; forwards the visible stack block to `CDXTexture__DecodeMemoryToTextureObject` with constants `1` and `3`, then returns with `RET 0x3c`. |

Read-back evidence:

- Initial dry/apply/final dry accepted the ten rows: `updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=10 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`.
- An immediate corrective tag pass removed three stale RET tags and added the instruction-verified tags for `RET 0x24`, `RET 0x20`, and `RET 0x20`: correction dry/apply/final dry reported `updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0`, `updated=3 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`, and `updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0`.
- Post exports verified `10` metadata rows, `10` tag rows, `16` xref rows, `1767` instruction rows, `10` decompile rows, `17` context metadata rows, `17` context tag rows, `28` context xref rows, `3684` context instruction rows, and `17` context decompile rows.
- Queue after Wave886: `6113` total functions, `5978` commented, `135` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed and strict clean-signature proxy `5978/6113 = 97.79%`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Next raw commentless row: `0x005759b6 CFastVB__DispatchIndirect_00657014`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-023255_post_wave886_texture_decode_upload_tail_verified`, `19` files, `172854151` bytes, `DiffCount=0`.

What this proves:

- The ten target function rows exist in the saved Ghidra project with the preserved names/signature displays.
- The saved comments and tags include `texture-decode-upload-tail-wave886` and `wave886-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to post-apply metadata, tag, xref, instruction, decompile, and context exports.

What remains unproven:

- Exact texture/surface/codec/profile/palette/D3D object layouts.
- Exact source-body identity and hidden ABI details beyond observed stack cleanup and decompile/register evidence.
- Runtime texture decode/upload/copy/format behavior.
- BEA patching behavior.
- Rebuild parity.
