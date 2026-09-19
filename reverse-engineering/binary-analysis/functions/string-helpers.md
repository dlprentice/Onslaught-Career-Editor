# String Helpers

Source File: no single source owner asserted for this helper group | Binary: BEA.exe, pristine SHA-256 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750

Status: active static and isolated-code function reference
Last updated: 2026-09-19
Summary: string-copy contracts and CDebugLog ownership, output ordering and initializer/reset evidence.

Static helper rows whose evidence is binary-local string/memory behavior rather than a confirmed Stuart source file owner.

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](_index.md#the-name-corrections-of-2026-07-28).
Old cell text is quoted below rather than deleted, so a reader who remembers the
withdrawn label can tell it was corrected and not lost.

| Address | Superseded label | Current name | Correction |
| --- | --- | --- | --- |
| `0x004daff0` | `CFearGrid__LookupFearWeightByArchetype` | `FearGridTrackedObject__LookupFearWeightByArchetype` | class prefix moved; suffix unchanged |

---

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
| `0x004f7bf0 Text__AsciiToWideScratch`, `0x004f7c70 StringScratch_T3_004f7c70`, `0x004f7cd0 StringScratch_T3_004f7cd0` | Adjacent four-slot scratch-buffer helper context. The two `StringScratch__CopyToRotating4KBuffer{A,B}` spellings were demoted to neutral Tier-3 placeholders on 2026-08-17: no `StringScratch` type descriptor exists in the image and no vtable owns either VA, so the invented class and the A/B ordering were both unsupported. Their adjacency to `0x004f7bf0` and the four-slot rotation described in the `FromWCHAR` row above are separate, still-standing byte readings. |

Post-Wave834 queue telemetry is `6098` total, `5656` commented, `442` commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5656/6098 = 92.75%`, strict proxy `5656/6098 = 92.75%`, and next raw commentless row `0x004f9a90 CUnit__ApplyDamage`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-000436_post_wave834_fromwchar_string_conversion_verified`.

Boundary: exact source-body identity, exact encoding/codepage policy, Unicode lossiness beyond observed low-byte copying, caller scratch-buffer lifetime contract, runtime path/UI behavior, BEA patching, and rebuild parity remain deferred.

## Wave825 StrCopyN Helper

Wave825 StrCopyN helper (`strcopyn-helper-wave825`, `wave825-readback-verified`) saved comments/tags for `0x004d6240 StrCopyN` while preserving the already clean signature `char * __cdecl StrCopyN(char * dst, char * src, int maxLen)`.

Static read-back evidence:

| Address | Evidence |
| --- | --- |
| `0x004d6240 StrCopyN` | Returns the original `dst`, exits immediately when `maxLen < 1`, copies bytes from `src` to `dst` while the countdown remains positive, stops after copying the first NUL byte, and otherwise stops when `maxLen` is exhausted. The body does not zero-pad remaining destination bytes. |
| `0x00441740 CDebugLog__Printf` | Caller xref at `0x0044185c`; formats into a 700-byte stack buffer, passes `0x50` to `StrCopyN`, then explicitly clears the final logger ring-entry byte. |
| `0x004418a0 CDebugLog__PrintfNoNewline` | Caller xref at `0x00441998`; formats into a 256-byte stack buffer, passes `0x50` to `StrCopyN`, then explicitly clears the final logger ring-entry byte. |

Post-Wave825 queue telemetry is `6098` total, `5633` commented, `465` commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5633/6098 = 92.37%`, strict proxy `5633/6098 = 92.37%`, and next raw commentless row `0x004daff0 FearGridTrackedObject__LookupFearWeightByArchetype`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-193427_post_wave825_strcopyn_helper_verified`.

Boundary: exact source-body identity, exact logger buffer lifetime, runtime truncation policy, runtime logger output behavior, BEA patching, and rebuild parity remain deferred.

## Debug-log ownership and history — September 19

**The helpers below operate on `CDebugLog`.** The pristine PC specimen
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
has RTTI `[005db018] → COL 00613010 → TypeDescriptor 00628400` naming that
class at zero subobject offset. Initializers `004415b0` and `00441630` install
vptr `005db01c` in the debug logger `0066f580` and setup-history logger
`0066eb90`. This corrects the earlier console ownership labels; it does not
rename the separate console implementation.

| Entry | Corrected role | Bounded contract |
| --- | --- | --- |
| `004416e0` | `CDebugLog__ResetStatusHistoryBuffer` | Clear the first byte of each of 30 text slots, reset timestamps/index, and set output enabled only when selector `00662dd0 == 1`; otherwise preserve its value. |
| `00441730` | `StoreField04_00441730` | Store the stack dword at receiver `+4`. Caller `004240a0` in the command-line parser supplies the setup-history logger and a filename pointer. The store is not proven exclusive to that class. |
| `00441740` | `CDebugLog__Printf` | Format into 700 stack bytes and call the RET-only `DebugTrace` before checking output enable. File opening and history updates are gated. |
| `004418a0` | `CDebugLog__PrintfNoNewline` | Check enable first; format into 256 stack bytes only after successful file opening. No `DebugTrace` call or added newline. |
| `004419e0` | `CDebugLog__RenderStatusHistoryOverlay` | Read the same ring/timestamps and visit six recent rows, or take the expiration return. This is static control flow, not a rendering observation. |

Both formatters use filename `+4`, first-attempt byte `+8`, history index
`+9e4`, last timestamp `+9e8`, and output-enable dword `+9ec`. The first
opening uses `w`; later openings use `a`. A failed first attempt can select a
fallback filename under the existing byte test. The first-attempt flag is set
even after failure. A nonnull opening result admits writes/close and subsequent
history updates; write/close success is **not** checked. The history contains
30 text slots at `+9`, stride `0x50`, and timestamps at `+96c` copied from the
existing global time `00672fd0`. No scheduler advance occurs in these wrappers.

**Isolated original-code evidence:** 24 controls executed the two complete
initializers and reset body at their original addresses. The debug initializer
sets enable to zero; setup history sets it to one. Selectors 0, 1, 2 and
`FFFFFFFF`, with initialized, enabled and flag-7 states, distinguish equality
to one from generic nonzero truthiness. Full 5,120-byte snapshots prove the
selected writes and preservation of the other logger, filename, vptr,
first-attempt flag, slot interiors and surrounding bytes. Exit registration
was a recording hook; its callbacks were not executed. This does not measure
actual startup, the parser, a live selector, file I/O or presentation.

For the pointer-pool warning path, `CSPtrSet__AddToHead` at `004e5a80` passes
the debug logger and fixed messages at `00632774`/`006327ac`. Those contain
54/57 ASCII literal bytes with no format conversions. All 111 bytes were
walked through the pristine formatter/classification tables: state stays zero,
the literal writer cannot exhaust its local stream count, and the disabled
route reaches no heap or file call. This static closure requires the specified
messages, pristine tables and disabled receiver; it does not apply to arbitrary
formats or changed CRT state. The uninitialized-pool diagnostic itself does
not halt the caller if logging returns; a source assertion is not a retail
abort measurement.

The enabled file route remains a boundary to a complete-shot RNG claim.
Its CRT allocation path can invoke a handler loaded from `009d09b8`, then
retry successfully. Eventual allocation success therefore does not prove
that no callback ran. Heap mode, retry/handler state and logging enable at
the actual warning remain unmeasured. Saved native commands, complete body
pins, table walks and controls are linked from
[validation](../../../VALIDATION.md#debug-log-ownership-and-initialization--september-19).
