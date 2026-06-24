# Ghidra CDXTexture Parser Context Diagnostics Wave693 Readiness Note

Date: 2026-05-21

Wave693 CDXTexture parser-context diagnostics saved eight adjacent parser-context, callback-triplet, and PNG chunk diagnostic rows after serialized Ghidra dry/apply/final-dry read-back.

Tag anchors:

- `cdxtexture-parser-context-diagnostics-wave693`
- `wave693-readback-verified`

Function anchors:

- `0x00592b00 CFastVB__ParserContext_Shutdown`
- `0x00592d9e CDXTexture__WarnPngChunkWithFormattedTag`
- Next queue head: `0x00592dc2 CDXTexture__CreatePngDecodeContext`

## Saved Scope

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x00592b00` | `void __stdcall CFastVB__ParserContext_Shutdown(void * parser_context)` | Releases the parser-context owned object, invokes observed shutdown/final callback slots, and calls `CRT__CExit(1)`. |
| `0x00592c50` | `void __stdcall CFastVB__ParserContext_Init(void * parser_context)` | Seeds parser-context callback slots, clears observed state fields, installs the default bogus-message-code diagnostic text pointer, and records diagnostic id `0x7b`. |
| `0x00592ca0` | `void __thiscall CDXTexture__FormatChunkTagForDiagnostics(void * this, int param_1, int param_2, void * param_3)` | Comment/tag-only row; formats the current PNG chunk tag into an ECX/output buffer, uses bracketed uppercase hex escapes for non-printable tag bytes, and appends optional message text. |
| `0x00592d29` | `void __stdcall CTexture__SetDecodeContextTriplet(void * decode_context, void * callback_context, void * error_callback, void * warning_callback)` | Stores the observed callback context plus error/warning callbacks in the decode context at `+0x48`, `+0x40`, and `+0x44`. |
| `0x00592d45` | `void __stdcall CDXTexture__ThrowDecodeError(void * decode_context, int message_or_code)` | Invokes the error callback when present, then transfers through `_longjmp(decode_context, 1)`. |
| `0x00592d63` | `void __stdcall CDXTexture__ReportDecodeWarning(void * decode_context, int message_or_code)` | Invokes the warning callback when present and returns without a longjmp transfer. |
| `0x00592d7a` | `void __stdcall CDXTexture__LogChunkTagDiagnostic(void * png_decode_state, void * optional_message_text)` | Formats the current PNG chunk tag into a stack buffer and routes it through `CDXTexture__ThrowDecodeError`. |
| `0x00592d9e` | `void __stdcall CDXTexture__WarnPngChunkWithFormattedTag(void * png_decode_state, void * optional_message_text)` | Formats the current PNG chunk tag into a stack buffer and routes it through `CDXTexture__ReportDecodeWarning`. |

## Evidence

`ApplyCDXTextureParserContextDiagnosticsWave693.java` dry/apply/final dry reported:

- Dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=1 missing=0 bad=0`
- Apply: `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=1 missing=0 bad=0`
- Final dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`

All three passes reported `REPORT: Save succeeded`. Post exports verified `8` metadata rows, `8` tag rows, `65` xref rows, `296` instruction rows, and `8` clean decompile rows. Pre-state exports covered the same eight rows, and candidate exports covered `14` adjacent parser-context/diagnostic/PNG decode rows with `71` xref rows, `518` instruction rows, and `14` clean decompile rows before tranche selection.

Post-Wave693 queue telemetry is `6098` total functions, `3973` commented, `2125` commentless, `1216` exact-undefined signatures, and `353` `param_N` signatures. Comment-backed proxy is `3973/6098 = 65.15%`; strict clean-signature proxy is `3923/6098 = 64.33%`.

Verified backup: `G:\GhidraBackups\BEA_20260521-135916_post_wave693_cdxtexture_parser_context_diagnostics_verified`, `19` files, `164957063` bytes, `DiffCount=0`.

## Boundaries

This wave proves saved static Ghidra name/signature/comment/tag evidence only. Exact parser-context layout, callback-table ABI, diagnostic table ownership, output-buffer capacity, PNG chunk-state layout, callback prototypes, payload type, non-return contract, runtime PNG/JPEG decode fidelity, BEA patching, and rebuild parity remain unproven.

Probe: `cmd.exe /c npm run test:ghidra-cdxtexture-parser-context-diagnostics-wave693`
