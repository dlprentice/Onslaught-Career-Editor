# Ghidra Texture Upload Texel Profile Wave891 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `texture-upload-texel-profile-wave891`

Wave891 texture upload texel profile saved comments/tags for three raw commentless texture upload and texel-profile rows after serialized headless dry/apply/read-back/final dry with the `texture-upload-texel-profile-wave891` and `wave891-readback-verified` tags. Existing names and signature displays were preserved. The pass made no renames, no function-boundary changes, no executable-byte changes, and did not launch BEA.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00580a05 CDXTexture__UploadSurfaceRegionWithFallback` | Called from decoded upload, mapped texture upload, copy/upload region fallback, and a recursive fallback branch. Static body evidence finalizes prior upload state, reads the source surface descriptor through `vtable slot 0x30`, validates optional rectangles, aligns DXT and packed YUY2/RGBG/UYVY-style regions, creates and locks a temporary surface for the `0x10000` flag path, mutes D3D debug output around lock/copy fallback calls, releases failed temporary objects, fills the output upload descriptor, and AddRefs the source surface. |
| `0x00580ef4 CDXTexture__CreateTexelCodecProfileFromSurfaceDesc` | Called by active-profile conversion rows. Static body evidence shuts down an existing active profile, reads a surface descriptor through `vtable slot 0x20`, validates a six-dword optional region, rejects unsupported descriptor/flag combinations, aligns DXT and packed regions, probes format support under D3D debug mute, locks the source surface through `vtable slot 0x24`, fills profile descriptor fields, and AddRefs the source surface. |
| `0x00581a4f CFastVB__TexelUnpackProfile__ctorFromDescriptor` | Broad constructor fan-in from CFastVB texel-unpack profile constructors and vtable initializers. Static body evidence installs base profile vtable `0x005e9ed0`, vector-constructs `0x100` entries, copies descriptor bounds/stride/format fields, selects lookup table globals `DAT_00657980` or `DAT_00657a00`, normalizes key-color bytes into floats, initializes all-one or descriptor-backed lookup rows for formats `0x28/0x29`, computes active extents and row-span fields, and adjusts the base pointer for row/depth pitch. |

Read-back evidence:

- `ApplyTextureUploadTexelProfileWave891.java dry`: `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyTextureUploadTexelProfileWave891.java apply`: `updated=3 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyTextureUploadTexelProfileWave891.java final dry`: `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 3 metadata rows, 3 tag rows, 49 xref rows, 972 instruction rows, and 3 decompile rows.
- Queue after Wave891: 6113 total, 6062 commented, 51 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict clean-signature proxy `6062/6113 = 99.17%`.
- Next raw commentless row: `0x005888bc CFastVB__InterpolateDualProfileStreams`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260526-050306_post_wave891_texture_upload_texel_profile_head_verified`, 19 files, 173149063 bytes, `DiffCount=0`.

What this proves:

- The three target function rows exist in the saved Ghidra project.
- The saved comments and tags include `texture-upload-texel-profile-wave891` and `wave891-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to metadata, tags, xrefs, instruction exports, decompile exports, and the refreshed queue.

What remains unproven:

- Exact texture surface/context layout.
- Exact texel profile and descriptor layouts.
- Exact Direct3D interface identity beyond observed vtable-slot evidence.
- Runtime upload, lock, conversion, unpack, or render behavior.
- BEA patching behavior.
- Rebuild parity.
