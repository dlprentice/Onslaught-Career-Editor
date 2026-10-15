# CDXMeshVB__ctor

Status: active static function note
Last updated: 2026-08-19
Source File: DXMesh / DX (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Already-pinned callee `0x00512ca0` body is **not** this proof.

> Address: `0x0054bf80`

## Contract

`thiscall` with an SEH frame (`push -1` / `0x005d7b08` /
`fs:[0]`). `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x0054bfef`. Body `0x0054bf80`–`0x0054bfef` is 112 bytes,
SHA-256
`c184bc02a49614c76df0efde7146203c737c9af8257e22f4281951487f1a1754`.
One `E8` (`0x0054bfd8` → already-pinned `CShaderBase__Init`
`0x00512ca0`, `ecx = 0x00855bb0`, arg `this`). Zero `E9`.

One inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x004ae616` | `CMeshPart__Init` |

Zero image encodings of imm `80 bf 54 00`. That host is
**not** claimed.

`eax` is 0. Stores `[this] = 0x005e50fc`, then
`[this+0x10c]`, `[this+0x108]`, `[this+0x110]`,
`[this+0x120]`, `[this+0x124]` all 0. `rep stosd` writes
`0x40` dwords from `this+8`. `EAX` is `this`.
`[0x005e50fc-4] = 0x00619ba0`; that COL `+0x0c` is type
descriptor `0x006511e0` whose name at `+8` is
`.?AVCDXMeshVB@@` (file `0x002511e8`). Imm `fc 50 5e 00`
occurs twice: this store and neighbor `0x0014c030`. That
neighbor is **not** claimed.

Cheapest falsifier: file `0x0014bf80` is not
`6a ff 68 08 7b 5d 00`, **or** `0x0014bfef` is not `c3`,
**or** body SHA-256 is not `c184bc02…1754`, **or**
`tools/call_xref_scan.py` on `0x0054bf80` is not the one
`E8` above, **or** `0x0014bfa8` is not
`c7 06 fc 50 5e 00`, **or** `0x0014bfa3` is not
`b9 40 00 00 00`, **or** `0x0014bfcd` is not `f3 ab`,
**or** `0x0014bfcf` is not `b9 b0 5b 85 00`, **or**
`0x002511e8` is not
`2e 3f 41 56 43 44 58 4d 65 73 68 56 42 40 40 00`, **or**
the image contains a second inbound `E8`/`E9`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0054bf80` | `CDXMeshVB__ctor` | `6aff 68087b5d00 … c706fc505e00 … f3ab b9b05b8500 e8c36cfcff … c3` | thiscall; SEH; bare ret; 112 B; 1 E8 already-pinned `0x00512ca0` / 0 E9; 1 inbound E8; vptr `0x005e50fc`; COL `.?AVCDXMeshVB@@`; zeros `+0x108`..`+0x124` and `0x40` dwords from `+8`; EAX=this. HIGH on ABI, inbound, those stores, that COL string. **Not** on callee body or `CMeshPart__Init`. |
