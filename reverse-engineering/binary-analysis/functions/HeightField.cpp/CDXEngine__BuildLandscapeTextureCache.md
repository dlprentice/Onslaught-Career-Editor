# CDXEngine__BuildLandscapeTextureCache

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Cache-file format and tile algebra are **not** this proof.

> Address: `0x00547860`

## Contract

Not a thiscall user of incoming `ECX`. Zero stack args. One bare
`ret` (`c3`) at `0x00547a5d`. Body `0x00547860`–`0x00547a5d` is
510 bytes, SHA-256
`7a7a988c19aa7ab3f8ee9634eee46851b6310841a79ebab6a6dd22baad9709a0`.
Eighteen `E8`, zero `E9`. Opens `mov eax, 0x1062c` /
`call 0x0055def0` then four pushes. First `ECX` write is
`lea ecx, [esp+0x34]` at `0x00547890`.

Zero inbound `.text` `E8`. One inbound `E9` at `0x00544706`. That
site is the 11-byte stub `0x00544700`–`0x0054470a` (SHA-256
`a06af4343877221d4157008fa60b080b4364b29f6673722769fbab3ddad8f3b3`):

```
mov  ecx, dword ptr [0x0089c9b0]
jmp  0x00547860
```

File `0x00144700` is `8b 0d b0 c9 89 00 e9 55 31 00 00`. Preceding
`FUN_005446e0` ends `ret` / `nop` at `0x005446fe`/`0x005446ff`.
`tools/call_xref_scan.py` on `0x00544700` is `total: 0`. Image
encodings of imm `60 78 54 00` are zero. Image encodings of imm
`00 47 54 00` are exactly one: `push 0x00544700` at `0x00544b32`
inside table-range `CDXLandscape__Init`:

```
push 0
push 0x00544700
push 0x00650dd8    ; "Build the landscape texture cache"
push 0x00650dc4    ; "BuildLandscapeCache"
mov  ecx, 0x00663498
call 0x0042af80
```

File `0x00144b30` is
`6a 00 68 00 47 54 00 68 d8 0d 65 00 68 c4 0d 65 00 b9 98 34 66 00 e8 35 64 ee ff`.
The register-helper body is **not** claimed. So the older
"no E8/E9 → unreachable" bound is too strong: there is no direct
rel32 into this body except the stub, and the stub is the
registered command pointer.

First `E8` after the alloca probe is `push 0x00650f50` /
`call 0x0040c640` with the unique string
`Building texture cache...\n`. Unique image refs:

| string VA | text | sole push |
| --- | --- | --- |
| `0x00650f50` | `Building texture cache...\n` | `0x0054786e` |
| `0x00650f24` | `ps2data\LandscapeTextureCache\texcache.tex` | `0x00547894` |
| `0x00650ef8` | `ps2data\LandscapeTextureCache\texcache.dir` | `0x005478b7` |
| `0x00650ee0` | `Shift %d/4 Line %d/64\n` | `0x00547924` |

Both path strings are pushed with mode `0x0063316c` = `wb` into
`0x0055e490`. The already-pinned
`CDXEngine__GenerateLandscapeCacheTileChunk` site at `0x00547975`
is `mov ecx, 0x006fadc8` / `call 0x00541f50`. Tile / file-format
loops are **not** claimed.

Cheapest falsifier: file `0x00147860` is not
`b8 2c 06 01 00 e8 86 66 01 00`, **or** `0x00147a5d` is not `c3`,
**or** body SHA-256 is not `7a7a988c…09a0`, **or**
`tools/call_xref_scan.py` on `0x00547860` is not exactly `E9` at
`0x00544706`, **or** `0x00144700` is not
`8b 0d b0 c9 89 00 e9 55 31 00 00`, **or** `0x00144b32` is not
`68 00 47 54 00`, **or** `0x00250f50` is not
`Building texture cache...\n`, **or** the image contains a
`60 78 54 00` or a second `00 47 54 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00547860` | `CDXEngine__BuildLandscapeTextureCache` | `b82c060100 e886660100 … 68500f6500 … b9c8ad6f00 e8d6a5ffff … c3` | not incoming-ECX thiscall; bare ret; 18 E8 / 0 E9; inbound only stub `E9` `0x00544706`; that stub is the unique `push 0x00544700` under the two `BuildLandscapeCache` strings; unique `wb` paths; already-pinned tile-chunk this=`0x006fadc8`. HIGH on ABI, inbound set, stub, register push, those strings. **Not** on cache format, tile algebra, or `0x0089c9b0`. |
