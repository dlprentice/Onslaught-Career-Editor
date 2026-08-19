# CVertexShader__CVertexShader

Status: active static function note
Last updated: 2026-08-19
Source File: Shader / DX (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. Child `t_11bcf1cf` report is data only; every pin below
was re-read from `74154bfa`. The Ghidra database was not opened.
Table name is a research label. Already-pinned callee `0x00512ca0`
body is **not** this proof.

> Address: `0x00501800`

## Contract

`thiscall` with an SEH frame (`push -1` / `0x005d56d8` /
`fs:[0]`). `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x0050188b`. Body `0x00501800`–`0x0050188b` is 140 bytes,
SHA-256
`c63dc1b8241053e92091b2038d6d7a811026d12b70af56cca08ca7b26cb96f91`.
One `E8` (`0x00501843` → already-pinned `CShaderBase__Init`
`0x00512ca0`, `ecx = 0x00855bb0`, arg `this`). Zero `E9`.

Two inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x0050215f` | table `CVertexShader__Create` |
| `0x00503fda` | table `CVertexShader__Clone` |

Zero image encodings of imm `00 18 50 00`. Those hosts are
**not** claimed.

Stores `[this] = 0x005dfbc4`. `rep stosd` writes 8 dwords
from `this+8`. `[0x005dfbc4-4] = 0x00617140`; that COL
`+0x0c` is type descriptor `0x0063cf20` whose name at `+8`
is `.?AVCVertexShader@@` (file `0x0023cf28`). Imm
`c4 fb 5d 00` occurs twice: this store and a neighbor. That
neighbor is **not** claimed. Also stores `[this+0x58] =
[0x00854e68]` then `[0x00854e68] = this`. `EAX` is `this`.

Cheapest falsifier: file `0x00101800` is not
`6a ff 68 d8 56 5d 00`, **or** `0x0010188b` is not `c3`,
**or** body SHA-256 is not `c63dc1b8…6f91`, **or**
`tools/call_xref_scan.py` on `0x00501800` is not the two
`E8` above, **or** `0x00101829` is not
`c7 06 c4 fb 5d 00`, **or** `0x0010182f` is not `f3 ab`,
**or** `0x0023cf28` is not
`2e 3f 41 56 43 56 65 72 74 65 78 53 68 61 64 65 72 40 40 00`,
**or** a third inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00501800` | `CVertexShader__CVertexShader` | `6aff 68d8565d00 … c706c4fb5d00 f3ab … b9b05b8500 e858140100 … c3` | thiscall; SEH; bare ret; 140 B; 1 E8 already-pinned `0x00512ca0` / 0 E9; 2 inbound E8; vptr `0x005dfbc4`; COL `.?AVCVertexShader@@`; stosd 8 from `+8`; EAX=this. HIGH on ABI, inbound, that plant, that COL string. **Not** on callee body or hosts. |
