# Ghidra Wave900+ Through Wave1061 Recheck Readiness Note

Status: complete structural static evidence recheck
Date: 2026-06-01
Scope: `wave900-plus-through-wave1061-recheck`

This note extends the rolling Wave900+ recheck gate through Wave1061. It keeps the historical Wave900-Wave1060 notes immutable and adds Wave1061 CDXTexture PNG decode read-only evidence to the current validation surface.

Current extension:

- Wave1061 readiness note: `release/readiness/ghidra_cdxtexture_png_decode_review_wave1061_2026-06-01.md`.
- Focused probe: `tools/ghidra_cdxtexture_png_decode_review_wave1061_probe.py`.
- Aggregate command: `npm run test:ghidra-wave900-plus-through-wave1061-recheck`.
- Static function-quality closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static surface progress extends to `1168/1529 = 76.39%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified Wave1061 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-211936_post_wave1061_cdxtexture_png_decode_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

The aggregate recheck remains structural static evidence validation. It does not prove runtime behavior, exact source/layout identity, BEA patching behavior, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1061; cdxtexture-png-decode-review-wave1061; 0x00592dc2 CDXTexture__CreatePngDecodeContext; 0x00592eb6 CDXTexture__ParsePngHeadersUntilIdat; 0x00593043 CDXTexture__DecodePngPassRowsAndPostprocess; 0x00593411 CDXTexture__ResetPngDecodeContext; 0x0059d699 CDXTexture__ParsePngChunk_IHDR; 0x0059d879 CDXTexture__ParsePngChunk_PLTE; 0x0059d992 CDXTexture__ParsePngChunk_IEND; 0x0059d9d8 CDXTexture__ParsePngChunk_gAMA; 0x0059dad9 CDXTexture__ParsePngChunk_sRGB; 0x0059dbbb CDXTexture__ParsePngChunk_tRNS; 0x0059dd5c CDXTexture__HandlePngChunkAfterIdat; 0x0059dda2 CDXTexture__ProcessIdatChunkDataAndQueueDecode; 812/1408 = 57.67%; 1168/1529 = 76.39%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-211936_post_wave1061_cdxtexture_png_decode_review_verified; no mutation.
