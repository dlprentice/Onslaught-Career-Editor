# Ghidra Texture Row Edge Padding Head Wave724 Readiness Note

Status: passed
Date: 2026-05-22

Wave724 texture row edge padding head saved five adjacent texture/decode row-cache and edge-padding rows with the `texture-row-edge-padding-head-wave724` and `wave724-readback-verified` tags.

The pass hardened two visible signatures and left three hidden-register rows comment/tag-only:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005ab420 CTexture__BuildComponentPlaneRowPointers` | `void CTexture__BuildComponentPlaneRowPointers(void)` | Comment/tag-only. Builds component-plane row pointer tables for the texture/decode row cache through a hidden ESI context; allocates paired row-pointer arrays under context `+0x1ac` slots `+0x38/+0x3c` and walks component descriptors under `+0xdc`. |
| `0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh` | `void __fastcall CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh(void * texture_context)` | Mirrors/copies high-side edge rows for component-plane row buffers using the ECX texture/decode context. Current `CMeshCollisionVolume` owner label is retained as Ghidra state, but static evidence is texture row-cache/edge-padding behavior, not owner/source identity proof. |
| `0x005ab620 CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth` | `void CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth(void)` | Comment/tag-only. Mirrors/copies both edge sides for component-plane row buffers using hidden EAX context. Current owner/source identity remains unproven. |
| `0x005ab700 CMeshCollisionVolume__FinalizeEdgePaddingRows` | `void CMeshCollisionVolume__FinalizeEdgePaddingRows(void)` | Comment/tag-only. Finalizes component-plane edge-padding rows using hidden EAX context and records first-component padding height at row-cache `+0x48`. Current owner/source identity remains unproven. |
| `0x005ab9c0 CDXTexture__InitComponentPlaneRowCache` | `void __stdcall CDXTexture__InitComponentPlaneRowCache(void * texture_context)` | Initializes the component-plane row cache, allocates the `0x50`-byte cache at context `+0x1ac`, installs `LAB_005ab950`, conditionally builds row pointers, and allocates per-component row cache buffers from the context allocator. |

Validation:

- Dry/apply/final dry summaries: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0`; `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0`; `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `5` metadata rows, `5` tag rows, `5` xref rows, `2405` instruction rows, and `5` decompile rows.
- Queue refresh passed: `6098` total, `4260` commented, `1838` commentless, `1216` exact-undefined signatures, `109` `param_N` signatures, comment-backed proxy `4260/6098 = 69.86%`, strict clean-signature proxy `4202/6098 = 68.91%`.
- Current raw commentless head remains `0x0042f220 CSPtrSet__Clear`; current high-signal head is `0x005aba90 CDXTexture__SelectNextScanTableForProgress`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-055657_post_wave724_texture_row_edge_padding_head_verified`, `19` files, `166562695` bytes, `DiffCount=0`.

Scope boundary: this is static saved-Ghidra metadata/decompile/instruction/xref evidence only. Exact texture/decode context layout, component descriptor schema, row-cache layout, edge-padding callback ABI, current owner/source identity, runtime texture/decode behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave724 texture row edge padding head`, `texture-row-edge-padding-head-wave724`, `0x005ab420 CTexture__BuildComponentPlaneRowPointers`, `0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh`, `0x005ab620 CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth`, `0x005ab700 CMeshCollisionVolume__FinalizeEdgePaddingRows`, `0x005ab9c0 CDXTexture__InitComponentPlaneRowCache`, `0x0042f220 CSPtrSet__Clear`, `0x005aba90 CDXTexture__SelectNextScanTableForProgress`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-055657_post_wave724_texture_row_edge_padding_head_verified`.
