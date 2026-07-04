# Ghidra CDXTexture JPEG Segment Parsers Wave691 Readiness Note

Date: 2026-05-21

Wave691 CDXTexture JPEG segment parsers saved six JPEG segment parser rows after serialized Ghidra dry/apply/final-dry read-back.

Tag anchors:

- `cdxtexture-jpeg-segment-parsers-wave691`
- `wave691-readback-verified`

Function anchors:

- `0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame`
- `0x005921a0 CDXTexture__ParseAdobeApp14Header`
- Next queue head: `0x00592380 CTexture__ReadJpegSegmentLengthAndEmitMarker`

## Saved Scope

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x00591460` | `int __fastcall CDXTexture__DecodeJpegSegment_StartOfFrame(int param_1)` | Comment/tag-only: parses a JPEG start-of-frame segment, records marker/context fields into the decode state, reads precision, image dimensions, component count, component ids, sampling factors, and quant table selector. |
| `0x005919e0` | `int CDXTexture__DecodeJpegSegment_HuffmanTables(void)` | Comment/tag-only: parses a JPEG DHT/Huffman-table segment, reads table class/id, sixteen code-length counts, validates symbol budget and remaining bytes, allocates descriptors, and copies code-length and symbol bytes. |
| `0x00591cb0` | `int __stdcall CDXTexture__DecodeJpegSegment_QuantizationTables(void * jpeg_decode_state)` | Parses a JPEG DQT/quantization-table segment, reads precision/table-id, allocates missing descriptors, fills 64 coefficients through `DAT_005f37f8`, and supports 8-bit and 16-bit coefficient forms. |
| `0x00591ef0` | `int __stdcall CDXTexture__DecodeJpegSegment_RestartInterval(void * jpeg_decode_state)` | Parses a JPEG DRI/restart-interval segment, requires the observed 16-bit length field to equal `4`, reads the restart interval, stores it at the observed `+0x118` slot, and reports malformed length through diagnostic `0x0b`. |
| `0x00591fc0` | `void __fastcall CDXTexture__ParseJfifApp0Header(int param_1)` | Comment/tag-only: parses a JPEG APP0 JFIF/JFXX header, including signature, version, density units, x/y density, thumbnail dimensions, and related diagnostics. |
| `0x005921a0` | `void __thiscall CDXTexture__ParseAdobeApp14Header(void * this, uint param_1, int param_2)` | Comment/tag-only: parses a JPEG APP14 Adobe header, records version/flags/transform diagnostics, stores the transform byte at the observed `+0x12c` slot, and sets the APP14-present flag at `+0x128`. |

## Evidence

`ApplyCDXTextureJpegSegmentParsersWave691.java` dry/apply/final dry reported:

- Dry: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0`
- Apply: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0`
- Final dry: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`

All three passes reported `REPORT: Save succeeded`. Post exports verified `6` metadata rows, `6` tag rows, `7` xref rows, `546` instruction rows, and `6` clean decompile rows. Pre-state exports covered the same six rows, and candidate exports covered `12` adjacent JPEG segment/marker rows with `17` xref rows, `1092` instruction rows, and `12` clean decompile rows before tranche selection.

Post-Wave691 queue telemetry is `6098` total functions, `3959` commented, `2139` commentless, `1216` exact-undefined signatures, and `366` `param_N` signatures. Comment-backed proxy is `3959/6098 = 64.92%`; strict clean-signature proxy is `3909/6098 = 64.10%`.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-130107_post_wave691_cdxtexture_jpeg_segment_parsers_verified`, `19` files, `164891527` bytes, `DiffCount=0`.

## Boundaries

This wave proves saved static Ghidra name/signature/comment/tag evidence only. Exact SOF marker enum, frame-header/component descriptor layout, Huffman descriptor layout, quant descriptor layout, restart-marker behavior, APP0 offset contract, APP14 offset contract, color-transform policy, runtime decode fidelity, BEA patching, and rebuild parity remain unproven.

Probe: `cmd.exe /c npm run test:ghidra-cdxtexture-jpeg-segment-parsers-wave691`
