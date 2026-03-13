# text.cpp Function Mappings

> Functions from text.cpp mapped to BEA.exe binary
> Debug path: "C:\dev\ONSLAUGHT2\text.cpp" at 0x00632dd8

## Overview
- **Functions Mapped:** 9
- **Status:** NEW (Dec 2025)
- **Classes:** CText

## Function List

| Address | Name | Status | Link |
|---------|------|--------|------|
| 0x004f2140 | CText__ResetCoreFields | NAMED | [View](CText__ResetCoreFields.md) |
| 0x004f2150 | CText__Ctor | NAMED | [View](CText__Ctor.md) |
| 0x004f2170 | CText__FreeBuffer | NAMED | [View](CText__FreeBuffer.md) |
| 0x004f2190 | CText__GetLanguageName | NAMED | [View](CText__GetLanguageName.md) |
| 0x004f21f0 | CText__Init | NAMED | [View](CText__Init.md) |
| 0x004f24b0 | CText__GetAudioNameById | NAMED | [View](CText__GetAudioNameById.md) |
| 0x004f2500 | CText__GetStringByIdAfter | NAMED | [View](CText__GetStringByIdAfter.md) |
| 0x004f2580 | CText__GetStringById | NAMED | [View](CText__GetStringById.md) |
| 0x004f2660 | CText__CopyFrom | NAMED | [View](CText__CopyFrom.md) |

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
