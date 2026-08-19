# CDXWater__ctor

Status: active static function note
Last updated: 2026-08-19
Source File: DX / Water (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Already-pinned callee `0x00512ca0` body is **not** this proof.

> Address: `0x0055b0e0`

## Contract

`thiscall` with an SEH frame (`push -1` / `0x005d7e38` /
`fs:[0]`). `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x0055b13a`. Body `0x0055b0e0`–`0x0055b13a` is 91 bytes,
SHA-256
`6e3988075aa93b5409d6b7d4bcb89b64c47f2634c247b00d505d5bad33922cc6`.
One `E8` (`0x0055b124` → already-pinned `CShaderBase__Init`
`0x00512ca0`, `ecx = 0x00855bb0`, arg `this`). Zero `E9`.
Five `nop`s after the `ret` are **not** in the body.

One inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x00449b7f` | `CEngine__Init` |

Zero image encodings of imm `e0 b0 55 00`. That host is
**not** claimed.

`eax` is 0. Stores `[this] = 0x005e5a70`, then
`[this+8]`, `[this+0xc]`, `[this+0x10]`, `[this+0x14]`,
`[this+0x18]`, and `[this+0x3ab8]` all 0. `EAX` is `this`.
`[0x005e5a70-4] = 0x00619d80`; that COL `+0x0c` is type
descriptor `0x00652a08` whose name at `+8` is
`.?AVCDXWater@@` (file `0x00252a10`). Imm `70 5a 5e 00`
occurs twice: this store and neighbor `0x0015b180`. That
neighbor is **not** claimed.

Cheapest falsifier: file `0x0015b0e0` is not
`6a ff 68 38 7e 5d 00`, **or** `0x0015b13a` is not `c3`,
**or** body SHA-256 is not `6e398807…2cc6`, **or**
`tools/call_xref_scan.py` on `0x0055b0e0` is not the one
`E8` above, **or** `0x0015b100` is not `b9 b0 5b 85 00`,
**or** `0x0015b109` is not `c7 06 70 5a 5e 00`, **or**
`0x0015b10f` is not `89 46 08`, **or** `0x00252a10` is not
`2e 3f 41 56 43 44 58 57 61 74 65 72 40 40 00`, **or**
the image contains a third `70 5a 5e 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0055b0e0` | `CDXWater__ctor` | `6aff 68387e5d00 … c706705a5e00 894608 … b9b05b8500 e8777bfbff … c3` | thiscall; SEH; bare ret; 91 B; 1 E8 already-pinned `0x00512ca0` / 0 E9; 1 inbound E8; vptr `0x005e5a70`; COL `.?AVCDXWater@@`; zeros `+8`..`+0x18` and `+0x3ab8`; EAX=this. HIGH on ABI, inbound, those stores, that COL string. **Not** on callee body or `CEngine__Init`. |
