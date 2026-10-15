# CDXMeshVB__dtor_base

Status: active static function note
Last updated: 2026-08-19
Source File: DXMesh / DX (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Callee bodies `0x0054d3f0` / `0x00549220` / already-pinned
`0x00512cc0` / `0x00512d50` are **not** this proof.
`CDXMeshVB.cpp/` was not written.

> Address: `0x0054c010`

## Contract

`thiscall` with an SEH frame (`push -1` / `0x005d7b28` /
`fs:[0]`). `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x0054c09d`. Body `0x0054c010`–`0x0054c09d` is 142 bytes,
SHA-256
`11d32c286b4cc8082d340d1b30ae33d0603cf7a3041fddda151217b7b7274b5d`.
Five `E8`, zero `E9`:

| site | dest (label only) |
| --- | --- |
| `0x0054c03c` | table `CDXMeshVB__ReleaseResources` `0x0054d3f0` |
| `0x0054c053` | already-named Free `0x00549220` |
| `0x0054c068` | already-pinned Unlink `0x00512cc0` |
| `0x0054c079` | already-named Free `0x00549220` |
| `0x0054c088` | table `0x00512d50` |

Two `nop`s after the `ret` are **not** in the body.

One inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x0054bff3` | table `CDXMeshVB__scalar_deleting_dtor` |

Zero image encodings of imm `10 c0 54 00`. That host is
**not** claimed.

Stores `[this] = 0x005e50fc` (same imm as already-pinned
ctor). `ebx = 0x40`. While `ebx` ≠ 0: if `[this+8]` live,
Free via `0x009c3df0` / `0x00549220` then `[this+8] = 0`;
`dec ebx`. Then Unlink (`ecx = 0x00855bb0`, arg `this`),
Free `[this+0x124]`, then `ecx = this` and `0x00512d50`.
Those callee effects are **not** this proof. Imm
`fc 50 5e 00` occurs twice: this store and already-pinned
ctor `0x0014bfaa`.

Cheapest falsifier: file `0x0014c010` is not
`6a ff 68 28 7b 5d 00`, **or** `0x0014c09d` is not `c3`,
**or** body SHA-256 is not `11d32c28…4b5d`, **or**
`tools/call_xref_scan.py` on `0x0054c010` is not the one
`E8` above, **or** `0x0014c02e` is not
`c7 06 fc 50 5e 00`, **or** `0x0014c041` is not
`bb 40 00 00 00`, **or** `0x0014c063` is not
`b9 b0 5b 85 00`, **or** the image contains a second
inbound `E8`/`E9`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0054c010` | `CDXMeshVB__dtor_base` | `6aff 68287b5d00 … c706fc505e00 … bb40000000 … e8536cfcff … c3` | thiscall; SEH; bare ret; 142 B; 5 E8 / 0 E9; 1 inbound E8; same vptr `0x005e50fc`; 0x40-iter Free `[+8]`; Unlink; Free `[+0x124]`. HIGH on ABI, inbound, those stores, that loop count. **Not** on callee bodies or the scalar-deleting host. |
