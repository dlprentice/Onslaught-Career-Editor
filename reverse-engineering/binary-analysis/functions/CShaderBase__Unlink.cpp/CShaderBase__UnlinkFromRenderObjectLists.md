# CShaderBase__UnlinkFromRenderObjectLists

Status: active static function note
Last updated: 2026-08-19
Source File: Shader / DX (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Child `t_046b0bc6` report is data only; every pin below was
re-read from `74154bfa`. List names and the other `0x00889074` /
`0x00889078` imm copies are **not** this proof.

> Address: `0x00512cc0`

## Contract

Not incoming-`ECX`. One stack dword. First insn is `push ecx`
(local slot). `xor ecx, ecx` then a later `mov esi,
[esp+0xc]` load the stack node; incoming `ECX` is unread.
`ret 4` at `0x00512d4b`. Body `0x00512cc0`–`0x00512d4d` is
142 bytes, SHA-256
`87a70cc9656047043b1aeb97e373abc6e1096f741f728033b3dee1a351411026`.
Zero `E8`. Zero `E9`. Two `nop`s after the `ret` are **not**
in the body. Neighbour `0x00512d50` is **not** this proof.

Eleven inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x004882c0` | already-pinned `CIBuffer__Destructor` |
| `0x004f7a71` | `CUMTexture__dtor_base` |
| `0x004fffb0` | `CVBuffer__dtor_base` |
| `0x0050190c` | `CVertexShader__dtor` |
| `0x00544a93` | `CDXLandscape__Destructor` |
| `0x00544f1f` | `CDXLandscape__Shutdown` |
| `0x0054c068` | `CDXMeshVB__dtor_base` |
| `0x005520da` | `CDXShadows__Destructor` |
| `0x00556dca` | `CDXTexture__Destructor` |
| `0x0055a40e` | `CDXTrees__Reset` |
| `0x0055b1a5` | `CDXWater__dtor` |

Zero image encodings of imm `c0 2c 51 00`. Those ten unlist
hosts are **not** claimed. Callers plant `ecx = 0x00855bb0`;
that plant is **not** this body.

Walk 1 loads head `[0x00889074]`. On match, if prev ≠ 0 then
`[ecx+4] = [esi+4]`, else `[0x00889074] = [esi+4]`. Walk 2
does the same with head `[0x00889078]`. `EAX` is the OR of
two 8-bit found flags, not the node. Imm `74 90 88 00`
occurs 15 times (two in this body). Imm `78 90 88 00` occurs
13 times (two in this body). The other copies are **not**
claimed.

Cheapest falsifier: file `0x00112cc0` is not
`51 a1 74 90 88 00 33 c9`, **or** `0x00112d4b` is not
`c2 04 00`, **or** body SHA-256 is not `87a70cc9…1026`,
**or** `tools/call_xref_scan.py` on `0x00512cc0` is not the
eleven `E8` above, **or** `0x00112cc9` is not
`8b 74 24 0c`, **or** `0x00112ce0` is not `89 51 04`, **or**
`0x00112ce8` is not `89 0d 74 90 88 00`, **or**
`0x00112d00` is not `a1 78 90 88 00`, **or** `0x00112d21`
is not `89 79 04`, **or** `0x00112d29` is not
`89 0d 78 90 88 00`, **or** the image contains a twelfth
inbound `E8`/`E9`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00512cc0` | `CShaderBase__UnlinkFromRenderObjectLists` | `51 a174908800 33c9 … 890d74908800 … a178908800 … 890d78908800 … c20400` | not incoming-ECX; ret 4; 142 B; 0 E8/E9; 11 inbound E8; walks `[0x00889074]` then `[0x00889078]`; EAX = OR of two 8-bit flags. HIGH on ABI, inbound set, those four stores. **Not** on list names, caller ECX plants, or the other imm copies. |
