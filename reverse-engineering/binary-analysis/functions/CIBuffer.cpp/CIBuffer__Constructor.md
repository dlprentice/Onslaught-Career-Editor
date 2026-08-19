# CIBuffer__Constructor

Status: active static function note
Last updated: 2026-08-19
Source File: IBuffer.cpp / DX (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Callee `0x00512ca0` body is **not** this proof.

> Address: `0x00488210`

## Contract

`thiscall` with an SEH frame (`push -1` / `0x005d2db8` /
`fs:[0]`). `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x00488260`. Body `0x00488210`–`0x00488260` is 81 bytes,
SHA-256
`5b1ea80fcd74c0f08f493096d4d3ba377fda774cb14735cd3e5f1a8710e0c596`.
One `E8` (`0x00488243` → table `CShaderBase__Init` `0x00512ca0`,
`ecx = 0x00855bb0`, arg `this`). Zero `E9`.

Five inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x0048e333` | already-pinned table `CLandscapeTexture__Constructor` |
| `0x0050085e` | `mov ecx,eax` then call |
| `0x0051a591` | `mov ecx,eax` then call |
| `0x0053a8a2` | `mov ecx,eax` then call |
| `0x00544c2e` | `mov ecx,eax` then call |

Zero image encodings of imm `10 82 48 00`. Those four unlist
hosts are **not** claimed.

`ebx` is 0. Stores `[this] = 0x005dbec4`, `[this+8] = 0`,
`[this+0x1c] = 0`, `[this+0x20] = 0` (byte). `EAX` is `this`.
`[0x005dbec4-4] = 0x006142b0`; that COL `+0x0c` is type
descriptor `0x0062d378` whose name at `+8` is `.?AVCIBuffer@@`
(file `0x0022d380`). Imm `c4 be 5d 00` occurs twice: this store
and the neighbor destructor `0x004882ae`. Destructor body is
**not** claimed.

Cheapest falsifier: file `0x00088210` is not
`6a ff 68 b8 2d 5d 00`, **or** `0x00088260` is not `c3`, **or**
body SHA-256 is not `5b1ea80f…c596`, **or**
`tools/call_xref_scan.py` on `0x00488210` is not the five `E8`
above, **or** `0x0008823a` is not `c7 06 c4 be 5d 00`, **or**
`0x00088240` is not `89 5e 08`, **or** `0x0022d380` is not
`2e 3f 41 56 43 49 42 75 66 66 65 72 40 40 00`, **or**
`0x00088231` is not `b9 b0 5b 85 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00488210` | `CIBuffer__Constructor` | `6aff 68b82d5d00 … c706c4be5d00 895e08 e858aa0800 … 895e1c 885e20 8bc6 … c3` | thiscall; SEH; bare ret; 81 B; 1 E8 `0x00512ca0` / 0 E9; 5 inbound E8; vptr `0x005dbec4`; COL `.?AVCIBuffer@@`; zeros `+8`/`+0x1c`/`+0x20`. HIGH on ABI, inbound set, those stores, that COL string. **Not** on callee body or the four unlist hosts. |
