# CShaderBase__Init

Status: active static function note
Last updated: 2026-08-19
Source File: Shader / DX (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. List meaning beyond the `+4` / head store is **not** this
proof.

> Address: `0x00512ca0`

## Contract

Not incoming-`ECX`. One stack dword. `ret 4` at `0x00512cb2`.
Body `0x00512ca0`–`0x00512cb4` is 21 bytes, SHA-256
`139666059cc555246abb2226fec1de15f03cd2c862a02335434be346571270fa`.
Zero `E8`. Zero `E9`. Three `nop`s after the `ret` are **not**
in the body.

Ten inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x00488243` | already-pinned `CIBuffer__Constructor` |
| `0x004f7a02` | `CUMTexture__ctor_base` |
| `0x004fff33` | `CVBuffer__ctor_base` |
| `0x00501843` | `CVertexShader__CVertexShader` |
| `0x00544c63` | `CDXLandscape__Init` |
| `0x0054bfd8` | `CDXMeshVB__ctor` |
| `0x00552111` | `CDXShadows__Init` |
| `0x00556d48` | `CTexture__ctor` |
| `0x0055a399` | `CDXTrees__Init` |
| `0x0055b124` | `CDXWater__ctor` |

Zero image encodings of imm `a0 2c 51 00`. Those nine unlist
hosts are **not** claimed.

`EAX = [esp+4]`. `[EAX+4] = [0x00889074]`, then
`[0x00889074] = EAX`. `EAX` is the inserted node. Entry `ECX`
is unread. Some callers plant `ecx = 0x00855bb0`; that plant is
**not** this body.

Imm `74 90 88 00` occurs 15 times. The two in this body are
the load at `0x00112ca6` and the store at `0x00112cae`. The
other 13 are **not** claimed.

Cheapest falsifier: file `0x00112ca0` is not
`8b 44 24 04`, **or** `0x00112cb2` is not `c2 04 00`, **or**
body SHA-256 is not `13966605…70fa`, **or**
`tools/call_xref_scan.py` on `0x00512ca0` is not the ten `E8`
above, **or** `0x00112ca4` is not `8b 0d 74 90 88 00`, **or**
`0x00112caa` is not `89 48 04`, **or** `0x00112cad` is not
`a3 74 90 88 00`, **or** the image contains an eleventh
inbound `E8`/`E9`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00512ca0` | `CShaderBase__Init` | `8b442404 8b0d74908800 894804 a374908800 c20400` | not incoming-ECX; ret 4; 21 B; 0 E8/E9; 10 inbound E8; `[arg+4]=[0x00889074]` then head=`arg`; EAX=arg. HIGH on ABI, inbound set, those two stores. **Not** on list consumers, caller ECX plants, or authored list name. |
