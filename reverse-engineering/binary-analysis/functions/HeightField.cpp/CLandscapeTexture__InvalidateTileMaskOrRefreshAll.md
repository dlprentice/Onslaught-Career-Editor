# CLandscapeTexture__InvalidateTileMaskOrRefreshAll

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Mask algebra is **not** this proof.

> Address: `0x0048f180`

## Contract

`thiscall`. Incoming `ECX` is this (used immediately as
`[ecx+0x40]` / `[ecx+0x2c]`). Zero stack args. Two bare `ret`
exits (`0x0048f1a6` / `0x0048f1b5`). Body `0x0048f180`–`0x0048f1b5`
is 54 bytes, SHA-256
`f38d911f5d80b95f07fbf838be1a0a2d63dfc6af71c565a78e7ee658211baaa3`.
One `E8` to already-pinned UpdateTileRange (`0x0048f1af`
`6a 3f 6a 3f 6a 00 6a 00 e8 4c fd ff ff`). That site does **not**
reload `ECX`. Zero `E9`. One inbound `.text` `E8`.

This-write: `[+0x2c]=1` at `0x0048f186`. This-reads: `+0x40`,
`+0x44`. If `[+0x40]` live, `rep stos` `-1` for `[+0x44]` bytes
(same shape as Reset). Authored names are **not** claimed.

Cheapest falsifier: file `0x0008f180` is not
`57 8b 79 40 85 ff c7 41 2c 01 00 00 00`, **or** `0x0008f1b5` is
not `c3`, **or** body SHA-256 is not `f38d911f…aaa3`, **or**
`tools/call_xref_scan.py` on `0x0048f180` is not exactly `E8` at
`0x005453a2`, **or** `0x0008f1a7` is not
`6a 3f 6a 3f 6a 00 6a 00 e8 4c fd ff ff`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048f180` | `CLandscapeTexture__InvalidateTileMaskOrRefreshAll` | `578b7940 … c7412c01000000 … 6a3f6a3f6a006a00 e84cfdffff c3` | thiscall; bare ret ×2; 54 B; 1 E8 UpdateTileRange / 0 E9; writes `[+0x2c]=1`. HIGH on ABI, that plant, those slots. **Not** on mask algebra. |
