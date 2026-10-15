# CDXTrees__Init

Status: active static function note
Last updated: 2026-08-19
Source File: DX / Trees (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Already-pinned callee `0x00512ca0` body is **not** this proof.
`DXTrees.cpp.md` was not written.

> Address: `0x0055a390`

## Contract

`thiscall`. `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x0055a3a7`. Body `0x0055a390`–`0x0055a3a7` is 24 bytes,
SHA-256
`346903c8169f8396d926d9590e5f393915446d4fe9a8b5f93611684e3f82bb10`.
One `E8` (`0x0055a399` → already-pinned `CShaderBase__Init`
`0x00512ca0`, `ecx = 0x00855bb0`, arg `this`). Zero `E9`.
Eight `nop`s after the `ret` are **not** in the body.

One inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x00449d0f` | `CEngine__Init` |

Zero image encodings of imm `90 a3 55 00`. That host is
**not** claimed. The inbound site plants `ecx = 0x009cc148`
then the `E8`; that plant is **not** this body.

No vptr store. `eax` is 0. Stores `[this+8] = 0` and
`[this+0xc] = 0`. `EAX` is 0. The eight-byte prefix
`56 8b f1 56 b9 b0 5b 85` occurs once.

Cheapest falsifier: file `0x0015a390` is not
`56 8b f1 56 b9 b0 5b 85`, **or** `0x0015a3a7` is not `c3`,
**or** body SHA-256 is not `346903c8…bb10`, **or**
`tools/call_xref_scan.py` on `0x0055a390` is not the one
`E8` above, **or** `0x0015a394` is not `b9 b0 5b 85 00`,
**or** `0x0015a39e` is not `33 c0 89 46 08`, **or**
`0x0015a3a3` is not `89 46 0c`, **or** the image contains a
second inbound `E8`/`E9`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0055a390` | `CDXTrees__Init` | `568bf1 56 b9b05b8500 e80289fbff 33c0 894608 89460c 5e c3` | thiscall; bare ret; 24 B; 1 E8 already-pinned `0x00512ca0` / 0 E9; 1 inbound E8; zeros `[+8]`/`[+0xc]`; EAX=0. HIGH on ABI, inbound, those two stores. **Not** on callee body, `CEngine__Init`, or `0x009cc148`. |
