# CLandscapeTexture__Reset

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Callee `0x004f7b60` is **not** this proof.

> Address: `0x0048e610`

## Contract

`thiscall`. `ECX`→`ESI` at `0x0048e612`. Zero stack args. Three
bare `ret` exits (`0x0048e621` / `0x0048e653` / `0x0048e668`).
`EAX` is the first callee's return (`ebx`) on the live paths.
Body `0x0048e610`–`0x0048e668` is 89 bytes, SHA-256
`541c9f6a7bf492ce30a3fc723ac696ff955ac1529878fcb177297c574232696c`.
Two `E8`: `0x004f7b60` then already-pinned UpdateTileRange
`0x0048ef00` (`6a 3f 6a 3f 6a 00 6a 00 8b ce e8 9d 08 00 00`).
Zero `E9`. Zero inbound `.text` `E8`/`E9`.

This-write: `[+0x2c]=1` at `0x0048e62d`. This-reads: `+0x2c`,
`+0x40`, `+0x44`. If `[+0x2c]` was live and `[+0x40]` is live,
`rep stos` `-1` through `[+0x40]` for `[+0x44]` bytes. Authored
names are **not** claimed.

Cheapest falsifier: file `0x0008e610` is not
`53 56 8b f1 e8 47 95 06 00`, **or** `0x0008e668` is not `c3`,
**or** body SHA-256 is not `541c9f6a…696c`, **or**
`tools/call_xref_scan.py` on `0x0048e610` is not empty, **or**
`0x0008e62d` is not `c7 46 2c 01 00 00 00`, **or** `0x0008e654`
is not `6a 3f 6a 3f 6a 00 6a 00 8b ce e8 9d 08 00 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048e610` | `CLandscapeTexture__Reset` | `5356 8bf1 e847950600 … c7462c01000000 … 6a3f6a3f6a006a00 8bce e89d080000 … c3` | thiscall; bare ret ×3; 89 B; 2 E8 / 0 E9; 0 inbound; writes `[+0x2c]=1`. HIGH on ABI, inbound-empty, those slots, the Range plant. **Not** on `0x004f7b60` or authored names. |
