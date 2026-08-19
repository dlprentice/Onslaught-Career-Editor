# CIBuffer__ScalarDeletingDestructor

Status: active static function note
Last updated: 2026-08-19
Source File: IBuffer.cpp / DX (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Callee `0x00488290` / `0x00549220` bodies are **not** this
proof.

> Address: `0x00488270`

## Contract

`thiscall`. `ECX`→`ESI`. One stack dword. `ret 4` at
`0x0048828d`. Body `0x00488270`–`0x0048828f` is 32 bytes,
SHA-256
`e9052e1caa5cdc3377b84ef12e60fe3407c07a6583a8fd3faafbda75d5ba827a`.
Two `E8` (`0x00488273` → already-named `CIBuffer__Destructor`
`0x00488290`; `0x00488285` → already-named
`CDXMemoryManager__Free` `0x00549220`). Zero `E9`.

Zero inbound `.text` `E8`/`E9`. Unique image copy of imm
`70 82 48 00` is vtable slot 0 at `0x005dbec4` (the same vptr
the constructor and destructor plant). That slot is **not** a
direct call.

Always `call 0x00488290` with `ecx = this`. If
`byte [esp+8] & 1`: `push this`, `mov ecx, 0x009c3df0`,
`call 0x00549220`. `EAX` is `this`.

Cheapest falsifier: file `0x00088270` is not
`56 8b f1 e8 18 00 00 00`, **or** `0x0008828d` is not
`c2 04 00`, **or** body SHA-256 is not `e9052e1c…827a`,
**or** `tools/call_xref_scan.py` on `0x00488270` is not empty,
**or** `0x00088280` is not `b9 f0 3d 9c 00`, **or**
`0x001dbec4` is not `70 82 48 00`, **or** the image contains a
second `70 82 48 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00488270` | `CIBuffer__ScalarDeletingDestructor` | `568bf1 e818000000 f644240801 740b 56 b9f03d9c00 e8960f0c00 8bc6 5e c20400` | thiscall; ret 4; 32 B; 2 E8 `0x00488290` / `0x00549220` / 0 E9; 0 inbound; unique vtable slot 0 at `0x005dbec4`; bit0 frees `this` via `0x009c3df0`; EAX=this. HIGH on ABI, inbound-empty, that slot, that bit. **Not** on callee bodies. |
