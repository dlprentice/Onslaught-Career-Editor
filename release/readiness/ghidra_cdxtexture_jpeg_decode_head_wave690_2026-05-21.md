# Ghidra CDXTexture JPEG Decode Head Wave690 Readiness Note

Date: 2026-05-21

Wave690 CDXTexture JPEG decode head saved eight JPEG decode setup, input-buffer, controller, state-machine, cleanup, output-default, pump, and finalize rows after serialized Ghidra dry/apply/final-dry read-back.

Tag anchors:

- `cdxtexture-jpeg-decode-head-wave690`
- `wave690-readback-verified`

Function anchors:

- `0x00590e10 CDXTexture__FillInputBufferFromSource`
- `0x00591340 CDXTexture__PumpDecoderStreamAndFinalize`
- Next queue head: `0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame`

## Saved Scope

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x00590e10` | `int __stdcall CDXTexture__FillInputBufferFromSource(void * jpeg_decode_state, void * destination_buffer, int requested_byte_count)` | Validates JPEG input state/source bounds, reports exhausted-source/state mismatches through the decoder error callback, invokes the source read callback at `+0x1ac`, and advances the consumed-byte cursor by the returned byte count. |
| `0x00590ea0` | `int __stdcall CDXTexture__ProcessInputControllerState(void * jpeg_decode_state)` | Handles `0xca`/`0xcb`/`0xcc` state progression, creates the decode dispatch context when needed, pumps input-controller callbacks, updates progress counters, and drains the parser work queue. |
| `0x00590f80` | `void __stdcall CDXTexture__InitJpegDecodeState(void * jpeg_decode_state, int expected_header_size, int expected_context_size)` | Checks observed `0x3e`/`0x1d8` setup constants, clears the decode-state block while preserving saved header slots, initializes decode allocator, marker reader, callback context, and starts the state machine at `0xc8`. |
| `0x00591050` | `void __stdcall CFastVB__ReleaseOwnedObjectAndReset(void * decode_state_header)` | Releases the owned object through vtable slot `+0x28` when present, then clears the owner pointer and stage/status field. |
| `0x00591060` | `void CDXTexture__SelectJpegOutputDefaults(void)` | Comment/tag-only: uses ESI-held JPEG decode state to select output color/component defaults, reports unsupported combinations with observed error ids `0x6f`/`0x72`, and resets output counters/defaults. |
| `0x005911d0` | `int __stdcall CDXTexture__AdvanceJpegDecodeState(void * jpeg_decode_state)` | Advances the JPEG state machine from `0xc8`/`0xc9` into `0xca` and later decode states, primes marker/input callbacks, invokes output-default selection when ready, and reports unexpected states. |
| `0x00591280` | `int __stdcall CDXTexture__DecodeJpegStream_PumpUntilReady(void * jpeg_decode_state)` | Handles `0xcd`/`0xce`/`0xcf`/`0xd2` stream states, reports short-source conditions, invokes stream-finalization callback, pumps marker controller until output is ready, then advances allocator/stage setup. |
| `0x00591340` | `int __stdcall CDXTexture__PumpDecoderStreamAndFinalize(void * jpeg_decode_state, int require_end_of_image)` | Validates initial JPEG state, advances the decode state machine, handles result `2` by optionally reporting strict end-of-image error `0x33`, pumps allocator/stage setup, and returns decoder status. |

## Evidence

`ApplyCDXTextureJpegDecodeHeadWave690.java` dry/apply/final dry reported:

- Dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=1 missing=0 bad=0`
- Apply: `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=1 missing=0 bad=0`
- Final dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`

All three passes reported `REPORT: Save succeeded`. Post exports verified `8` metadata rows, `8` tag rows, `10` xref rows, `728` instruction rows, and `8` clean decompile rows. Pre-state exports covered the same eight rows, and candidate exports covered `13` adjacent JPEG setup/segment rows with `16` xref rows, `1053` instruction rows, and `13` clean decompile rows before tranche selection.

Post-Wave690 queue telemetry is `6098` total functions, `3953` commented, `2145` commentless, `1216` exact-undefined signatures, and `368` `param_N` signatures. Comment-backed proxy is `3953/6098 = 64.82%`; strict clean-signature proxy is `3903/6098 = 64.00%`.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-123207_post_wave690_cdxtexture_jpeg_decode_head_verified`, `19` files, `164825991` bytes, `DiffCount=0`.

## Boundaries

This wave proves saved static Ghidra name/signature/comment/tag evidence only. Exact JPEG source-manager ABI, decode-state layout, state enum, marker-controller ABI, output color enum, ESI helper signature/storage, segment-parser semantics, runtime decode fidelity, BEA patching, and rebuild parity remain unproven.

Probe: `cmd.exe /c npm run test:ghidra-cdxtexture-jpeg-decode-head-wave690`
