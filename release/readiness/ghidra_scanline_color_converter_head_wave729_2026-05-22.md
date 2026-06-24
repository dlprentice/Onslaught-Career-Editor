# Ghidra Scanline Color Converter Head Wave729 Readiness Note

Status: passed
Date: 2026-05-22

Wave729 scanline color converter head saved five adjacent CDXTexture scanline/color-transform rows with the `scanline-color-converter-head-wave729` and `wave729-readback-verified` tags.

The pass hardened four visible signatures/parameter names and left one hidden-EAX helper comment/tag-only:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005b0ee0 CDXTexture__InitScanlineColorConverter` | `void __stdcall CDXTexture__InitScanlineColorConverter(void * decode_context)` | Allocates a `0x40`-byte controller through the context allocator, stores it at decode_context `+0x1cc`, validates component/count combinations from decode_context `+0x24/+0x28/+0x2c`, installs row conversion callbacks, calls the Wave728 YCC lookup-table builders for matching color modes, and writes selected output component counts at decode_context `+0x78/+0x7c`. |
| `0x005b10b0 CDXTexture__InitColorTransformLuts` | `void CDXTexture__InitColorTransformLuts(void)` | Comment/tag-only. Uses hidden EAX as the texture decode context, reads the color-transform controller at context `+0x1c8`, allocates four lookup buffers through the context allocator, stores them at controller `+0x10` through `+0x1c`, and fills fixed-point transform tables using `LAB_005b6900` as a clamp/base table. |
| `0x005b1400 CDXTexture__ConvertYccScanlinePairToRgb_Scalar` | `void __fastcall CDXTexture__ConvertYccScanlinePairToRgb_Scalar(void * decode_context, int row_pair_index, void * output_rgb_row_pair_table)` | Scalar row-pair YCC-to-RGB converter. The visible fastcall parameters carry decode_context, row_pair_index, and output RGB row-pair table; wrapper `0x005b1b40` passes the source component row table through hidden EAX for this scalar path. It reads lookup pointers from decode_context `+0x1c8`, uses decode_context `+0x148` as a clamp/base table and `+0x70` as output width, reads two luma rows plus shared chroma rows, and handles odd-width tails. |
| `0x005b1630 CDXTexture__ConvertYccScanlinePairToRgb_Sse` | `void __fastcall CDXTexture__ConvertYccScanlinePairToRgb_Sse(void * decode_context, int row_pair_index, void * source_component_row_table)` | SSE row-pair YCC-to-RGB converter. The visible fastcall parameters carry decode_context, row_pair_index, and source component row table; wrapper `0x005b1b40` passes the output RGB row-pair table through hidden EAX for this SSE path. It reads transform tables from decode_context `+0x1c8`, uses decode_context `+0x148`/`+0x70`, processes eight pixels per loop with packed saturated arithmetic, and falls back to scalar-style tail handling. |
| `0x005b1b80 CDXTexture__InitColorTransformContext` | `void __stdcall CDXTexture__InitColorTransformContext(void * decode_context)` | Allocates a `0x30`-byte controller at decode_context `+0x1c8`, stores callback slots for the scalar/SSE row-pair bridge at `0x005b1b40` depending on decode_context `+0x13c`, computes row byte count from decode_context `+0x78/+0x70`, optionally allocates the SSE scratch/output buffer, and calls `CDXTexture__InitColorTransformLuts` through hidden EAX context setup. |

Validation:

- Dry/apply/final dry summaries: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=1 missing=0 bad=0`; `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=1 missing=0 bad=0`; `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `5` metadata rows, `5` tag rows, `6` xref rows, `2705` instruction rows, and `5` decompile rows.
- Queue refresh passed: `6098` total, `4290` commented, `1808` commentless, `1216` exact-undefined signatures, `86` `param_N` signatures, comment-backed proxy `4290/6098 = 70.35%`, strict clean-signature proxy `4232/6098 = 69.40%`.
- Current raw commentless head remains `0x0042f220 CSPtrSet__Clear`; current high-signal head is `0x005b1c00 CDXTexture__AllocAligned16`.
- Verified backup: `G:\GhidraBackups\BEA_20260522-082119_post_wave729_scanline_color_converter_head_verified`, `19` files, `166660999` bytes, `DiffCount=0`.

Scope boundary: this is static saved-Ghidra metadata/decompile/instruction/xref evidence only. Exact decode context layout, controller layout, callback ABI, row-table schemas, hidden EAX ABI, RGB byte order, coefficient identity, SIMD/scalar equivalence, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave729 scanline color converter head`, `scanline-color-converter-head-wave729`, `0x005b0ee0 CDXTexture__InitScanlineColorConverter`, `0x005b10b0 CDXTexture__InitColorTransformLuts`, `0x005b1400 CDXTexture__ConvertYccScanlinePairToRgb_Scalar`, `0x005b1630 CDXTexture__ConvertYccScanlinePairToRgb_Sse`, `0x005b1b80 CDXTexture__InitColorTransformContext`, `0x005b1c00 CDXTexture__AllocAligned16`, `0x0042f220 CSPtrSet__Clear`, `G:\GhidraBackups\BEA_20260522-082119_post_wave729_scanline_color_converter_head_verified`.
