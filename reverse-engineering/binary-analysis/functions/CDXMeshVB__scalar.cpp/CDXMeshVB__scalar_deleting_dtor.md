# CDXMeshVB__scalar_deleting_dtor

Status: active static function note
Last updated: 2026-08-19
Source File: DXMesh / DX (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Already-pinned callee `0x0054c010` and already-named Free
`0x00549220` bodies are **not** this proof. `CDXMeshVB.cpp/` and
`CDXMeshVB__dtor.cpp/` were not written.

> Address: `0x0054bff0`

## Contract

`thiscall`. `ECX`→`ESI`. One stack dword. `ret 4` at
`0x0054c00d`. Body `0x0054bff0`–`0x0054c00f` is 32 bytes,
SHA-256
`e3bd36f278ffda789dcbd09e02d593d8c1fe07fa1942bfdca22f5c6223b43c42`.
Two `E8`: `0x0054bff3` → already-pinned
`CDXMeshVB__dtor_base` `0x0054c010`; `0x0054c005` →
already-named Free `0x00549220` (`ecx = 0x009c3df0`, arg
`this`). Zero `E9`.

Zero inbound `.text` `E8`/`E9`. Imm `f0 bf 54 00` occurs
once: vtable slot 0 at `0x005e50fc` (same vptr as the
already-pinned ctor / dtor_base). That table is **not**
this body.

If bit0 of the stack dword is set, Free `this` via
`0x009c3df0`. `EAX` is `this`.

Cheapest falsifier: file `0x0014bff0` is not
`56 8b f1 e8 18 00 00 00`, **or** `0x0014c00d` is not
`c2 04 00`, **or** body SHA-256 is not `e3bd36f2…3c42`,
**or** `tools/call_xref_scan.py` on `0x0054bff0` is not
zero `E8`/`E9`, **or** `0x0014bff8` is not
`f6 44 24 08 01`, **or** `0x001e50fc` is not
`f0 bf 54 00`, **or** the image contains a second
`f0 bf 54 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0054bff0` | `CDXMeshVB__scalar_deleting_dtor` | `568bf1 e818000000 f644240801 740b 56 b9f03d9c00 e816d2ffff 8bc6 5e c20400` | thiscall; ret 4; 32 B; 2 E8 already-pinned `0x0054c010` / Free `0x00549220` / 0 E9; 0 inbound; unique slot 0 at `0x005e50fc`; bit0 frees this via `0x009c3df0`; EAX=this. HIGH on ABI, those two calls, that slot, that bit test. **Not** on callee bodies. |
