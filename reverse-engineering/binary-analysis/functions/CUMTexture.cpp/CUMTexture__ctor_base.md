# CUMTexture__ctor_base

Status: active static function note
Last updated: 2026-08-19
Source File: Texture / DX (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Already-pinned callee `0x00512ca0` body is **not** this proof.

> Address: `0x004f79d0`

## Contract

`thiscall` with an SEH frame (`push -1` / `0x005d53a8` /
`fs:[0]`). `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x004f7a18`. Body `0x004f79d0`–`0x004f7a18` is 73 bytes,
SHA-256
`47c4ad0ca428a5513eab11d387a794bb155e3838a1880ead1cc1af2e840aab8b`.
One `E8` (`0x004f7a02` → already-pinned `CShaderBase__Init`
`0x00512ca0`, `ecx = 0x00855bb0`, arg `this`). Zero `E9`.
Seven `nop`s after the `ret` are **not** in the body.

Three inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x0048e433` | table `CLandscapeTexture__ConstructorMip` |
| `0x0054150e` | `CDXFrontEndVideo__InitVideo` |
| `0x00552198` | `CDXShadows__Init` |

Zero image encodings of imm `d0 79 4f 00`. Those three hosts
are **not** claimed.

`eax` is 0. Stores `[this] = 0x005df908` and `[this+8] = 0`.
`EAX` is `this`. `[0x005df908-4] = 0x00616fe8`; that COL
`+0x0c` is type descriptor `0x0062d8a0` whose name at `+8` is
`.?AVCUMTexture@@` (file `0x0022d8a8`). Imm `08 f9 5d 00`
occurs twice: this store and neighbor `0x000f7a5f`. That
neighbor is **not** claimed.

Cheapest falsifier: file `0x000f79d0` is not
`6a ff 68 a8 53 5d 00`, **or** `0x000f7a18` is not `c3`,
**or** body SHA-256 is not `47c4ad0c…ab8b`, **or**
`tools/call_xref_scan.py` on `0x004f79d0` is not the three
`E8` above, **or** `0x000f79f0` is not `b9 b0 5b 85 00`,
**or** `0x000f79f9` is not `c7 06 08 f9 5d 00`, **or**
`0x000f79ff` is not `89 46 08`, **or** `0x0022d8a8` is not
`2e 3f 41 56 43 55 4d 54 65 78 74 75 72 65 40 40 00`, **or**
the image contains a third `08 f9 5d 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004f79d0` | `CUMTexture__ctor_base` | `6aff 68a8535d00 … c70608f95d00 894608 e899b20100 … 8bc6 … c3` | thiscall; SEH; bare ret; 73 B; 1 E8 already-pinned `0x00512ca0` / 0 E9; 3 inbound E8; vptr `0x005df908`; COL `.?AVCUMTexture@@`; zeros `[+8]`; EAX=this. HIGH on ABI, inbound set, that plant, that COL string. **Not** on callee body or the three hosts. |
