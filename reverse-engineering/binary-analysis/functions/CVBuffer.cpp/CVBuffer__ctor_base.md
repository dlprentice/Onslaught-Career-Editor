# CVBuffer__ctor_base

Status: active static function note
Last updated: 2026-08-19
Source File: VBuffer / DX (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Already-pinned callee `0x00512ca0` body is **not** this proof.

> Address: `0x004fff00`

## Contract

`thiscall` with an SEH frame (`push -1` / `0x005d5638` /
`fs:[0]`). `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x004fff50`. Body `0x004fff00`–`0x004fff50` is 81 bytes,
SHA-256
`b6b000a2315cb988c1017b9a7fb7a835dc0d91b3b33bf7567bf2b47d56c27d94`.
One `E8` (`0x004fff33` → already-pinned `CShaderBase__Init`
`0x00512ca0`, `ecx = 0x00855bb0`, arg `this`). Zero `E9`.
Nine `nop`s after the `ret` are **not** in the body.

Eleven inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x00500650` | `CVBufTexture__ResizeVertexBuffer` |
| `0x0051a2c9` | `CFastVB__Create` |
| `0x0053a1ad` | `CDXBattleLine__LoadTextures` |
| `0x0053a804` | `CDXBattleLine__BuildMesh` |
| `0x0053c090` | `CDXCompass__Init` |
| `0x0053c12a` | `CDXCompass__Init` |
| `0x0054412c` | `CDXEngine__InitKempyCubeTexturesAndVertexBuffer` |
| `0x00544bdd` | `CDXLandscape__Init` |
| `0x00550383` | `CLandscapeVB__ctor` |
| `0x00556616` | `CDXSurf__CreateSurfaceStrip` |
| `0x00556669` | `CDXSurf__CreateSurfaceStrip` |

Zero image encodings of imm `00 ff 4f 00`. Those hosts are
**not** claimed.

`ebx` is 0. Stores `[this] = 0x005dfb8c`, `[this+8] = 0`,
`[this+0x24] = 0`, `[this+0x28] = 0` (byte). `EAX` is `this`.
`[0x005dfb8c-4] = 0x006170a0`; that COL `+0x0c` is type
descriptor `0x00633cf0` whose name at `+8` is `.?AVCVBuffer@@`
(file `0x00233cf8`). Imm `8c fb 5d 00` occurs twice: this store
and neighbor `0x000fffa0`. That neighbor is **not** claimed.

Cheapest falsifier: file `0x000fff00` is not
`6a ff 68 38 56 5d 00`, **or** `0x000fff50` is not `c3`,
**or** body SHA-256 is not `b6b000a2…7d94`, **or**
`tools/call_xref_scan.py` on `0x004fff00` is not the eleven
`E8` above, **or** `0x000fff21` is not `b9 b0 5b 85 00`,
**or** `0x000fff2a` is not `c7 06 8c fb 5d 00`, **or**
`0x000fff30` is not `89 5e 08`, **or** `0x000fff3c` is not
`89 5e 24`, **or** `0x000fff3f` is not `88 5e 28`, **or**
`0x00233cf8` is not
`2e 3f 41 56 43 56 42 75 66 66 65 72 40 40 00`, **or** the
image contains a twelfth inbound `E8`/`E9`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004fff00` | `CVBuffer__ctor_base` | `6aff 6838565d00 … c7068cfb5d00 895e08 e8682d0100 895e24 885e28 … c3` | thiscall; SEH; bare ret; 81 B; 1 E8 already-pinned `0x00512ca0` / 0 E9; 11 inbound E8; vptr `0x005dfb8c`; COL `.?AVCVBuffer@@`; zeros `+8`/`+0x24`/`+0x28`; EAX=this. HIGH on ABI, inbound set, those stores, that COL string. **Not** on callee body or the eleven hosts. |
