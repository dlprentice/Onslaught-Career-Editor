# String Helpers

Static helper rows whose evidence is binary-local string/memory behavior rather than a confirmed Stuart source file owner.

## Wave834 FromWCHAR String Conversion

Wave834 FromWCHAR string conversion (`fromwchar-string-conversion-wave834`, `wave834-readback-verified`) saved comments/tags for `0x004f7d30 FromWCHAR` while preserving the already clean signature `char * __cdecl FromWCHAR(short * wstr)`. This row is important shared string/path infrastructure, not throwaway tail code.

Static read-back evidence:

| Address | Evidence |
| --- | --- |
| `0x004f7d30 FromWCHAR` | Calls `WcsLen(wstr)`, rotates `g_FromWCHAR_RingIndex` at `0x00854d4c` modulo four, selects `0x00840d40+(slot*0x1000)`, copies the low byte from each 16-bit input slot while advancing the source pointer by two bytes, NUL-terminates the selected slot, and returns the selected scratch-buffer pointer. |
| `0x0042d098`, `0x0042cfdf`, `0x0042d009`, `0x0042d0c4`, `0x0042c764` | Fatal-error/localized text callers. |
| `0x004654f8 IsCheatActive` | Cheat text compare caller. |
| `0x004b7b28 CMessageBox__SelectPortraitIndex`, `0x004b7fdf CMessageBox__StartVoiceOrFallbackTextReveal` | Message-box text and portrait caller evidence. |
| `0x00514c33 EnumerateSaveFiles_Main`, `0x00514fb7 PCPlatform__WriteSaveFile`, `0x005150b7 PCPlatform__ReadSaveFile`, `0x00514ef7 PCPlatform__DeleteSaveFile` | Save-file path caller evidence. |
| `0x004f7bf0 Text__AsciiToWideScratch`, `0x004f7c70 StringScratch__CopyToRotating4KBufferA`, `0x004f7cd0 StringScratch__CopyToRotating4KBufferB` | Adjacent four-slot scratch-buffer helper context. |

Post-Wave834 queue telemetry is `6098` total, `5656` commented, `442` commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5656/6098 = 92.75%`, strict proxy `5656/6098 = 92.75%`, and next raw commentless row `0x004f9a90 CUnit__ApplyDamage`. Verified backup: `G:\GhidraBackups\BEA_20260525-000436_post_wave834_fromwchar_string_conversion_verified`.

Boundary: exact source-body identity, exact encoding/codepage policy, Unicode lossiness beyond observed low-byte copying, caller scratch-buffer lifetime contract, runtime path/UI behavior, BEA patching, and rebuild parity remain deferred.

## Wave825 StrCopyN Helper

Wave825 StrCopyN helper (`strcopyn-helper-wave825`, `wave825-readback-verified`) saved comments/tags for `0x004d6240 StrCopyN` while preserving the already clean signature `char * __cdecl StrCopyN(char * dst, char * src, int maxLen)`.

Static read-back evidence:

| Address | Evidence |
| --- | --- |
| `0x004d6240 StrCopyN` | Returns the original `dst`, exits immediately when `maxLen < 1`, copies bytes from `src` to `dst` while the countdown remains positive, stops after copying the first NUL byte, and otherwise stops when `maxLen` is exhausted. The body does not zero-pad remaining destination bytes. |
| `0x00441740 CConsole__Printf` | Caller xref at `0x0044185c`; formats into a 700-byte stack buffer, passes `0x50` to `StrCopyN`, then explicitly clears the final console ring-entry byte. |
| `0x004418a0 CConsole__PrintfNoNewline` | Caller xref at `0x00441998`; formats into a 256-byte stack buffer, passes `0x50` to `StrCopyN`, then explicitly clears the final console ring-entry byte. |

Post-Wave825 queue telemetry is `6098` total, `5633` commented, `465` commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5633/6098 = 92.37%`, strict proxy `5633/6098 = 92.37%`, and next raw commentless row `0x004daff0 CFearGrid__LookupFearWeightByArchetype`. Verified backup: `G:\GhidraBackups\BEA_20260524-193427_post_wave825_strcopyn_helper_verified`.

Boundary: exact source-body identity, exact console buffer lifetime, runtime truncation policy, runtime console output behavior, BEA patching, and rebuild parity remain deferred.
