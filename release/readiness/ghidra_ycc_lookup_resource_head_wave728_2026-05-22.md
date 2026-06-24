# Ghidra YCC Lookup Resource Head Wave728 Readiness Note

Status: passed
Date: 2026-05-22

Wave728 YCC lookup resource head saved five adjacent CDXTexture entropy/resource, YCC lookup-table, row-interleave, and RGBA conversion rows with the `ycc-lookup-resource-head-wave728` and `wave728-readback-verified` tags.

The pass hardened three visible signatures/parameter names and left two hidden-EAX helpers comment/tag-only:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005af670 CDXTexture__InitEntropyDecodeResources` | `void __stdcall CDXTexture__InitEntropyDecodeResources(void * decode_context)` | Allocates a `0xa0`-byte decode/resource controller through the context allocator, stores it at decode_context `+0x1c8`, installs the refill callback, checks component sampling and dimensions, selects per-component resampler/conversion callbacks including the Wave727 adaptive YCC helpers, flags the two-row YCC path, and allocates scanline/component row buffers. |
| `0x005af860 CDXTexture__BuildYccToRgbLookupTables` | `void CDXTexture__BuildYccToRgbLookupTables(void)` | Comment/tag-only. Uses hidden EAX as the texture decode context, reads the scanline/color controller at context `+0x1cc`, allocates four lookup buffers through the context allocator, stores them at controller `+8` through `+0x14`, and fills fixed coefficient tables. |
| `0x005afbd0 CDXTexture__InterleaveComponentRowsIntoScanline` | `void __stdcall CDXTexture__InterleaveComponentRowsIntoScanline(void * decode_context, void * component_row_tables, int source_row_index, void * output_scanline_table, int scanline_count)` | Reads component count from decode_context `+0x24` and output width from decode_context `+0x70`, selects component source rows through component_row_tables plus source_row_index, walks output_scanline_table entries, and writes component bytes at component-count stride. |
| `0x005afcf0 CDXTexture__ConvertYccToRgba_WithLookupTables` | `void __stdcall CDXTexture__ConvertYccToRgba_WithLookupTables(void * decode_context, void * source_component_row_table, int source_row_index, void * output_rgba_row_table, int scanline_count)` | Reads output width from decode_context `+0x70`, uses lookup-table pointers from the controller at decode_context `+0x1cc`, uses decode_context `+0x148` as a clamp/base table, selects Y/C/A rows from source_component_row_table plus source_row_index, and writes four bytes per output pixel. |
| `0x005afe60 CDXTexture__InitYccLookupTables` | `void CDXTexture__InitYccLookupTables(void)` | Comment/tag-only. Uses hidden EAX as the texture decode context, reads the scanline/color controller at context `+0x1cc`, allocates ten lookup buffers at controller `+0x18` through `+0x3c`, and fills paired fixed-point coefficient/clamp transforms over the byte domain. |

Validation:

- Dry/apply/final dry summaries: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=2 missing=0 bad=0`; `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=2 missing=0 bad=0`; `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `5` metadata rows, `5` tag rows, `11` xref rows, `2705` instruction rows, and `5` decompile rows. The caller-context export also captured `0x005b0ee0 CDXTexture__InitScanlineColorConverter` as one read-only decompile target for the next high-signal cluster.
- Queue refresh passed: `6098` total, `4285` commented, `1813` commentless, `1216` exact-undefined signatures, `90` `param_N` signatures, comment-backed proxy `4285/6098 = 70.27%`, strict clean-signature proxy `4227/6098 = 69.32%`.
- Current raw commentless head remains `0x0042f220 CSPtrSet__Clear`; current high-signal head is `0x005b0ee0 CDXTexture__InitScanlineColorConverter`.
- Verified backup: `G:\GhidraBackups\BEA_20260522-075134_post_wave728_ycc_lookup_resource_head_verified`, `19` files, `166660999` bytes, `DiffCount=0`.

Scope boundary: this is static saved-Ghidra metadata/decompile/instruction/xref evidence only. Exact decode context layout, controller layout, component descriptor schema, row-table schema, RGBA byte order, hidden EAX ABI, allocator contract, coefficient identity, clamp semantics, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave728 YCC lookup resource head`, `ycc-lookup-resource-head-wave728`, `0x005af670 CDXTexture__InitEntropyDecodeResources`, `0x005af860 CDXTexture__BuildYccToRgbLookupTables`, `0x005afbd0 CDXTexture__InterleaveComponentRowsIntoScanline`, `0x005afcf0 CDXTexture__ConvertYccToRgba_WithLookupTables`, `0x005afe60 CDXTexture__InitYccLookupTables`, `0x005b0ee0 CDXTexture__InitScanlineColorConverter`, `0x0042f220 CSPtrSet__Clear`, `G:\GhidraBackups\BEA_20260522-075134_post_wave728_ycc_lookup_resource_head_verified`.
