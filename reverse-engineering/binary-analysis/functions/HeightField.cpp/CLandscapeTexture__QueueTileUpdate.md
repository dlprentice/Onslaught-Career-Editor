# CLandscapeTexture__QueueTileUpdate

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Queue algebra is **not** this proof.

> Address: `0x0048e880`

## Contract

`thiscall`. `ECX`→`EBP` at `0x0048e887`. Two stack args (`ret 8`
at `0x0048e926`). Body `0x0048e880`–`0x0048e94e` is 207 bytes,
SHA-256
`0d717a943bc4f089ed197e6c74da99947ee040c18c2fd857cf9ea7db9f926993`.
One `E8` to already-pinned FlushUpdateQueue `0x0048e7c0`
(`e8 e0 fe ff ff` at `0x0048e8db`). Zero `E9`. One short `jmp`
`eb 96` at `0x0048e94d` back to the append path. One-byte `nop`
at `0x0048e94f` is **not** in the body.

No this-write. This-reads: `+0x3c` then `+0x34` (`8b 55 3c 8b 4d
34` at `0x0048e88f`). Walk seed is imm `0x006fa7d8`; cursor is
`[0x0062d868]`; flush-when-full compares the cursor to
`0x006fabc0`. Authored names of the two stack args are **not**
claimed.

One inbound `.text` `E8`, zero `E9`: `0x005471bb` inside
`CDXLandscape__UpdateLOD` (`50 51 8b ca e8 c0 76 f4 ff`). That
caller body is **not** claimed. This site is the already-pinned
Flush inbound at `0x0048e8db`.

Cheapest falsifier: file `0x0008e880` is not
`51 8b 44 24 08 53 55 8b e9`, **or** `0x0008e926` is not
`c2 08 00`, **or** `0x0008e94d` is not `eb 96`, **or** body
SHA-256 is not `0d717a94…6993`, **or**
`tools/call_xref_scan.py` on `0x0048e880` is not exactly `E8` at
`0x005471bb`, **or** `0x0008e8db` is not `e8 e0 fe ff ff`, **or**
`0x001471bb` is not `e8 c0 76 f4 ff`, **or** `0x0008e88f` is not
`8b 55 3c 8b 4d 34`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048e880` | `CLandscapeTexture__QueueTileUpdate` | `518b442408 5355 8be9 … 8b553c 8b4d34 … e8e0feffff … c20800 … eb96` | thiscall; ret 8; 207 B; 1 E8 Flush / 0 E9; 1 inbound UpdateLOD; reads `+0x3c`/`+0x34`; no this-write. HIGH on ABI, inbound, that Flush plant, those two slots, the three abs. **Not** on queue algebra, arg names, or the UpdateLOD body. |
