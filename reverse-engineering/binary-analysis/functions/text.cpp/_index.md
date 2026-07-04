# text.cpp Function Mappings

> Functions from text.cpp mapped to BEA.exe binary
> Debug path: "[maintainer-local-source-export-root]\text.cpp" at 0x00632dd8

## Overview

> **Queue status (2026-06-01):** Ghidra export-contract closure **6246/6246** (Wave1054: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

- **Functions Mapped:** 9
- **Status:** Wave1054 read-back updated (2026-06-01)
- **Classes:** CText

Wave1054 CText localization-core review (`ctext-localization-core-review-wave1054`, `wave1054-readback-verified`) saved a comment/tag correction for `0x004f2140 CText__ResetCoreFields`, `0x004f2150 CText__Ctor`, `0x004f2170 CText__FreeBuffer`, `0x004f2190 CText__GetLanguageName`, `0x004f21f0 CText__Init`, `0x004f24b0 CText__GetAudioNameById`, `0x004f2500 CText__GetStringByIdAfter`, and `0x004f2580 CText__GetStringById`. Static retail evidence ties these rows to `data\\LANGUAGE`, `0xffffffbb`, `MultiByteToWideChar`, `CText__CopyFrom`, `CFrontEnd__SetLanguage`, and `CDXMemBuffer__GetFileSize`. Fresh primary exports verified `8` metadata rows, `8` tag rows, `340` xref rows, `399` function-body instruction rows, and `8` decompile rows; context exports verified `9` metadata rows, `9` tag rows, `100` xref rows, `986` instruction rows, and `9` decompile rows. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `769/1408 = 54.62%`; expanded static surface progress advances to `1065/1509 = 70.58%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-165852_post_wave1054_ctext_localization_core_review_verified`. Runtime localization behavior, exact CText layout, exact source-body identity, source-layout identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1054; ctext-localization-core-review-wave1054; 0x004f2140 CText__ResetCoreFields; 0x004f21f0 CText__Init; 0x004f24b0 CText__GetAudioNameById; 0x004f2500 CText__GetStringByIdAfter; 0x004f2580 CText__GetStringById; CText__CopyFrom; CFrontEnd__SetLanguage; CDXMemBuffer__GetFileSize; data\\LANGUAGE; 0xffffffbb; MultiByteToWideChar; 769/1408 = 54.62%; 1065/1509 = 70.58%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-165852_post_wave1054_ctext_localization_core_review_verified; comment/tag correction.

Wave831 CText CopyFrom (`ctext-copyfrom-wave831`, `wave831-readback-verified`) saved bounded static comments/tags for `0x004f2660 CText__CopyFrom` after dry/apply/final-dry read-back. Static retail evidence ties the helper to `CFrontEnd__SetLanguage`, caller xref `0x00466ace`, `g_Text`, `CDXMemoryManager__Free`, `CDXMemoryManager__Alloc`, debug path `0x00632dd8`, allocation type `0x72`, line token `0x155`, backing-buffer copy, and rebased text/audio pool pointers. Post-Wave831 queue telemetry is `5652/6098 = 92.69%` strict clean proxy; next raw commentless row is `0x004f2710 CTextureBase__Init`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-224036_post_wave831_ctext_copyfrom_verified`. Exact `text.cpp` source body identity, concrete CText layout beyond observed offsets, runtime language-switch behavior, runtime localization behavior, allocator ownership, BEA patching, and rebuild parity remain deferred.

## Function List

| Address | Name | Status | Link |
|---------|------|--------|------|
| 0x004f2140 | CText__ResetCoreFields | WAVE1054_COMMENTED | [View](CText__ResetCoreFields.md) |
| 0x004f2150 | CText__Ctor | WAVE1054_COMMENTED | [View](CText__Ctor.md) |
| 0x004f2170 | CText__FreeBuffer | WAVE1054_COMMENTED | [View](CText__FreeBuffer.md) |
| 0x004f2190 | CText__GetLanguageName | WAVE1054_COMMENTED | [View](CText__GetLanguageName.md) |
| 0x004f21f0 | CText__Init | WAVE1054_COMMENTED | [View](CText__Init.md) |
| 0x004f24b0 | CText__GetAudioNameById | WAVE1054_COMMENTED | [View](CText__GetAudioNameById.md) |
| 0x004f2500 | CText__GetStringByIdAfter | WAVE1054_COMMENTED | [View](CText__GetStringByIdAfter.md) |
| 0x004f2580 | CText__GetStringById | WAVE1054_COMMENTED | [View](CText__GetStringById.md) |
| 0x004f2660 | CText__CopyFrom | WAVE831_COMMENTED | [View](CText__CopyFrom.md) |

## Class Structure (CText)

Based on decompiled code, CText appears to have the following member layout:

| Offset | Member | Description |
|--------|--------|-------------|
| 0x00 | mVersion | Text file version (0, 1, 2, or 3) |
| 0x04 | mBuffer | Pointer to loaded file bytes |
| 0x08 | mTextPool | Pointer to UTF-16LE string pool (v0/v1/v2/v3) |
| 0x0C | mAudioPool | Pointer to audio-name ASCII pool (v2/v3) |
| 0x10 | mCount | Number of entries/strings in file |
| 0x14 | mLoaded | Flag: text file loaded (0 or 1) |
| 0x18 | mFileSize | Size of loaded text file |
| 0x1C | mLanguage | Current language ID |
| 0x20 | mHasExtra | Set when `ver_flags & 0x80000000` (not set in shipped `game/data/language/*.dat`) |
| 0x24 | mExtraPtr | Used only when `mHasExtra!=0` (format not reverse-engineered yet) |
| 0x28 | mExtraU32 | Used only when `mHasExtra!=0` |
| 0x2C | mExtraOff | Used only when `mHasExtra!=0` |

Note: the loader uses additional fields beyond 0x1C when `ver_flags & 0x80000000` is set (not set in shipped `game/data/language/*.dat`).

## Language IDs

From CText__Init switch statement:
- 0 = English
- 1 = French
- 2 = German
- 3 = Spanish
- 4 = Italian

American English uses a special path: `data/LANGUAGE/american.DAT`

## Text File Format

The text file format supports multiple versions:
- **Version 0:** Legacy format - string count + offsets + strings
- **Version 1:** Header `0xFFFFFFBB`, version 1 in header
- **Version 2/3:** `count*0x0C` entry table + UTF-16LE string pool and optional audio-name pool

Magic number: `0xFFFFFFBB` (`bb ff ff ff` in file bytes) identifies newer format.

## Related
- Debug path string: 0x00632dd8
- Language strings: 0x00632d74 (english), 0x00632d7c (french), etc.
- Parent: [../README.md](../README.md)
