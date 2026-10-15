# CDXEngine__GenerateLandscapeCacheTileChunk

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Landscape-cache algebra is **not** this proof.

> Address: `0x00541f50`

## Contract

`thiscall`. `ECX`→`EBX`. Ten stack dwords (`ret 0x28` at
`0x005425f8`). Body `0x00541f50`–`0x005425fa` is 1707 bytes, SHA-256
`6792680235394bea32615b929f54ea52ab628380690edd61cd9e1b4b384284a0`.
Zero instruction-aligned `E8`, zero `E9`. One `ret`.

One inbound `.text` `E8`, zero `E9`: `0x00547975` inside
`CDXEngine__BuildLandscapeTextureCache`. The site loads the
already-pinned BSS this first:

```
mov  ecx, 0x006fadc8
call 0x00541f50
```

File `0x00147970` is `b9 c8 ad 6f 00 e8 d6 a5 ff ff`.

This-relative `[+0x20]` is a **load** at `0x00542063`
(`8b 5b 20` = `mov ebx, [ebx+0x20]`). Later `+0x20` encodings in
this body are `[esp+0x20]` scratch, not object stores. The cursor
walk / tile fill is **not** claimed.

Cheapest falsifier: file `0x00141f50` is not `81 ec c8 00 00 00 53 8b d9`,
**or** `0x001425f8` is not `c2 28 00`, **or** body SHA-256 is not
`67926802…84a0`, **or** `tools/call_xref_scan.py` on `0x00541f50` is
not exactly `E8` at `0x00547975`, **or** `0x00147970` is not
`b9 c8 ad 6f 00 e8 d6 a5 ff ff`, **or** `0x00142063` is not `8b 5b 20`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00541f50` | `CDXEngine__GenerateLandscapeCacheTileChunk` | `81ecc8000000 538bd9 … 8b5b20 … c22800` | thiscall; ret 0x28; 0 E8/E9; this=`0x006fadc8`; `[+0x20]` load only. HIGH on ABI, inbound, that load. **Not** on tile algebra. |
