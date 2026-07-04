# Ghidra CDXTexture JPEG Marker Reader Wave692 Readiness Note

Date: 2026-05-21

Wave692 CDXTexture JPEG marker reader saved six JPEG marker-reader rows after serialized Ghidra dry/apply/final-dry read-back.

Tag anchors:

- `cdxtexture-jpeg-marker-reader-wave692`
- `wave692-readback-verified`

Function anchors:

- `0x00592380 CTexture__ReadJpegSegmentLengthAndEmitMarker`
- `0x00592a80 CDXTexture__InitJpegMarkerReader`
- Next queue head: `0x00592b00 CFastVB__ParserContext_Shutdown`

## Saved Scope

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x00592380` | `int __stdcall CTexture__ReadJpegSegmentLengthAndEmitMarker(void * jpeg_decode_state)` | Reads the two-byte JPEG segment length through the buffered input source, emits diagnostic id `0x5b`, records length minus the two length bytes, optionally skips remaining segment bytes, and returns decoder status. |
| `0x00592420` | `int __stdcall CTexture__SkipJpegFillBytesAndReadMarker(void * jpeg_decode_state)` | Scans for marker prefixes, skips non-marker bytes and stuffed `0xff/0x00` fill sequences, emits diagnostic id `0x74` when bytes were skipped, writes the current marker byte, and returns decoder status. |
| `0x00592530` | `int __stdcall CFastVB__JpegParser_ReadAndValidateSOI(void * jpeg_decode_state)` | Reads the first two buffered JPEG bytes, validates SOI marker bytes `0xff/0xd8`, emits diagnostic id `0x35` with observed bytes on mismatch, advances the buffer cursor, and records the marker byte. |
| `0x005928d0` | `int __stdcall CDXTexture__ConsumeExpectedRestartMarker(void * jpeg_decode_state)` | Consumes or fetches the current JPEG marker, compares it with the expected restart marker, emits diagnostic id `0x62` for the matched marker, clears the current-marker slot, delegates mismatch recovery through the observed callback, and advances the expected restart index modulo eight. |
| `0x00592950` | `int __stdcall CDXTexture__ClassifyRestartMarkerResync(void * jpeg_decode_state, int expected_restart_index)` | Logs diagnostic id `0x79`, classifies the current marker relative to the expected restart index into observed result classes `1`/`2`/`3`, emits diagnostic id `0x61`, clears the marker slot for class `1`, loops through the marker-skip helper for class `2`, and returns decoder status for class `3`. |
| `0x00592a80` | `void __stdcall CDXTexture__InitJpegMarkerReader(void * jpeg_decode_state)` | Allocates the observed marker-reader context, stores it in the decode state, seeds reset/frame/SOI/restart/segment-length/default APP callback slots, clears segment callback counters, installs default APP handlers, and clears decode-state marker fields. |

## Evidence

`ApplyCDXTextureJpegMarkerReaderWave692.java` dry/apply/final dry reported:

- Dry: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0`
- Apply: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0`
- Final dry: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`

All three passes reported `REPORT: Save succeeded`. Post exports verified `6` metadata rows, `6` tag rows, `10` xref rows, `222` instruction rows, and `6` clean decompile rows. Pre-state exports covered the same six rows, and candidate exports covered `14` adjacent marker-reader/parser-context/diagnostic rows with `75` xref rows, `518` instruction rows, and `14` clean decompile rows before tranche selection.

Post-Wave692 queue telemetry is `6098` total functions, `3965` commented, `2133` commentless, `1216` exact-undefined signatures, and `360` `param_N` signatures. Comment-backed proxy is `3965/6098 = 65.02%`; strict clean-signature proxy is `3915/6098 = 64.20%`.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-132823_post_wave692_cdxtexture_jpeg_marker_reader_verified`, `19` files, `164924295` bytes, `DiffCount=0`.

## Boundaries

This wave proves saved static Ghidra name/signature/comment/tag evidence only. Exact marker-reader object layout, segment-length contract, callback ABI, SOI precondition contract, restart recovery policy, resync-class enum, callback-table ABI, APP slot ownership, runtime decode fidelity, BEA patching, and rebuild parity remain unproven.

Probe: `cmd.exe /c npm run test:ghidra-cdxtexture-jpeg-marker-reader-wave692`
