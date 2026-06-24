# Ghidra CDXTexture PNG Decode Review Wave1061 Readiness Note

Status: complete read-only static re-audit evidence
Date: 2026-06-01
Scope: `cdxtexture-png-decode-review-wave1061`

Wave1061 re-read the CDXTexture PNG decode/parser surface that earlier Waves694, 695, 698, 713, 714, and 715 had already named, signed, commented, and tagged. The fresh evidence preserved the existing names, signatures, comments, tags, and function boundaries, so this wave made no Ghidra mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Existing saved signature |
| --- | --- |
| `0x00592dc2 CDXTexture__CreatePngDecodeContext` | `void * __stdcall CDXTexture__CreatePngDecodeContext(void * png_version_string, void * callback_context, void * error_callback, void * warning_callback)` |
| `0x00592eb6 CDXTexture__ParsePngHeadersUntilIdat` | `void __stdcall CDXTexture__ParsePngHeadersUntilIdat(void * png_decode_state, void * png_image_context)` |
| `0x00593024 CDXTexture__PreparePngRowOutputLayout` | `void __stdcall CDXTexture__PreparePngRowOutputLayout(void * png_decode_state, void * png_image_context)` |
| `0x00593043 CDXTexture__DecodePngPassRowsAndPostprocess` | `void __stdcall CDXTexture__DecodePngPassRowsAndPostprocess(void * png_decode_state, void * previous_row_workspace, void * current_row_workspace)` |
| `0x005933c6 CDXTexture__DecodePngRowsAcrossPasses` | `void __stdcall CDXTexture__DecodePngRowsAcrossPasses(void * png_decode_state, int * row_workspace_pointer_table)` |
| `0x00593411 CDXTexture__ResetPngDecodeContext` | `void __stdcall CDXTexture__ResetPngDecodeContext(void * png_decode_state, void * primary_row_workspace, void * secondary_row_workspace)` |
| `0x00593526 CDXTexture__ReleasePngDecodeContextHandles` | `void __stdcall CDXTexture__ReleasePngDecodeContextHandles(void * png_decode_context_slot, void * primary_row_workspace_slot, void * secondary_row_workspace_slot)` |
| `0x005950e0 CDXTexture__ComparePngSignatureBytes` | `int __stdcall CDXTexture__ComparePngSignatureBytes(void * signature_buffer, uint start_offset, uint bytes_to_check)` |
| `0x0059cd26 CDXTexture__ReadU32BigEndian` | `uint __stdcall CDXTexture__ReadU32BigEndian(void * source_buffer)` |
| `0x0059cd4b CDXTexture__ReadChunkBytesAndUpdateCrc` | `void __stdcall CDXTexture__ReadChunkBytesAndUpdateCrc(void * png_decode_state, void * destination_buffer, uint byte_count)` |
| `0x0059cd62 CDXTexture__IsPngChunkCrcInvalid` | `bool __stdcall CDXTexture__IsPngChunkCrcInvalid(void * png_decode_state)` |
| `0x0059d614 CDXTexture__FinalizePngChunkAndVerifyCrc` | `int __stdcall CDXTexture__FinalizePngChunkAndVerifyCrc(void * png_decode_state, uint remaining_chunk_bytes)` |
| `0x0059d699 CDXTexture__ParsePngChunk_IHDR` | `void __stdcall CDXTexture__ParsePngChunk_IHDR(void * png_decode_state, void * png_image_context, uint chunk_data_length)` |
| `0x0059d879 CDXTexture__ParsePngChunk_PLTE` | `void __stdcall CDXTexture__ParsePngChunk_PLTE(void * png_decode_state, void * png_image_context, uint chunk_data_length)` |
| `0x0059d992 CDXTexture__ParsePngChunk_IEND` | `void __stdcall CDXTexture__ParsePngChunk_IEND(void * png_decode_state, void * png_image_context, uint chunk_data_length)` |
| `0x0059d9d8 CDXTexture__ParsePngChunk_gAMA` | `void __stdcall CDXTexture__ParsePngChunk_gAMA(void * png_decode_state, void * png_image_context, uint chunk_data_length)` |
| `0x0059dad9 CDXTexture__ParsePngChunk_sRGB` | `void __stdcall CDXTexture__ParsePngChunk_sRGB(void * png_decode_state, void * png_image_context, uint chunk_data_length)` |
| `0x0059dbbb CDXTexture__ParsePngChunk_tRNS` | `void __stdcall CDXTexture__ParsePngChunk_tRNS(void * png_decode_state, void * png_image_context, uint chunk_data_length)` |
| `0x0059dd5c CDXTexture__HandlePngChunkAfterIdat` | `void __stdcall CDXTexture__HandlePngChunkAfterIdat(void * png_decode_state, void * png_image_context, uint chunk_data_length)` |
| `0x0059dda2 CDXTexture__ProcessIdatChunkDataAndQueueDecode` | `void __stdcall CDXTexture__ProcessIdatChunkDataAndQueueDecode(void * png_decode_state)` |

Fresh evidence highlights:

- `CDXTexture__DecodePngFromMemory` still calls the PNG context create/header/layout/row-decode/release/signature helpers.
- `CDXTexture__ParsePngHeadersUntilIdat` still dispatches IHDR, PLTE, IEND, gAMA, sRGB, tRNS, and fallback post-IDAT handlers before row decode.
- `CDXTexture__DecodePngPassRowsAndPostprocess` still drives IDAT processing, chunk finalization, scanline filtering, row transforms, and post-decode transforms.
- Chunk helpers still connect big-endian reads, source reads, CRC updates, CRC verification, and IDAT decode queuing through the same static xref surface.

Read-back evidence:

- Primary exports: `20` metadata rows, `20` tag rows, `55` xref rows, `1578` function-body instruction rows, and `20` decompile rows.
- Context exports: `20` metadata rows, `20` tag rows, `51` xref rows, `1892` function-body instruction rows, and `20` decompile rows.
- Export logs report no missing, bad, failed, or lock evidence.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%` because the Wave1061 rows are outside the current materialized Wave911 focused queue.
- Expanded static surface progress extends to `1168/1529 = 76.39%` after adding these twenty PNG rows outside the prior expanded denominator.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-211936_post_wave1061_cdxtexture_png_decode_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The twenty target rows exist in the saved Ghidra project with the expected names and signatures.
- Existing PNG/decode comments and tags remain coherent with fresh metadata, tags, xrefs, body instructions, and decompile-index evidence.
- The PNG decode/parser island has current read-only re-audit coverage after earlier write waves.

What remains unproven:

- Exact PNG decode-state/image-context/chunk flag/CRC/source-read/gamma/sRGB/tRNS policy layouts.
- Exact libpng/zlib/source identity.
- Runtime PNG/image fidelity, runtime decompression behavior, BEA patching behavior, gameplay outcomes, and rebuild parity.

Next candidate note: continue with the next focused static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1061; cdxtexture-png-decode-review-wave1061; 0x00592dc2 CDXTexture__CreatePngDecodeContext; 0x00592eb6 CDXTexture__ParsePngHeadersUntilIdat; 0x00593043 CDXTexture__DecodePngPassRowsAndPostprocess; 0x00593411 CDXTexture__ResetPngDecodeContext; 0x0059d699 CDXTexture__ParsePngChunk_IHDR; 0x0059d879 CDXTexture__ParsePngChunk_PLTE; 0x0059d992 CDXTexture__ParsePngChunk_IEND; 0x0059d9d8 CDXTexture__ParsePngChunk_gAMA; 0x0059dad9 CDXTexture__ParsePngChunk_sRGB; 0x0059dbbb CDXTexture__ParsePngChunk_tRNS; 0x0059dd5c CDXTexture__HandlePngChunkAfterIdat; 0x0059dda2 CDXTexture__ProcessIdatChunkDataAndQueueDecode; 812/1408 = 57.67%; 1168/1529 = 76.39%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-211936_post_wave1061_cdxtexture_png_decode_review_verified; no mutation.
