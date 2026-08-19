# CUMTexture__VFunc_03_ReleaseTextureResource

Status: active static function note
Last updated: 2026-08-19
Source File: UMTexture.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. The `[vtable+8]` callee is **not** this proof.

> Address: `0x004f7bd0`

## Contract

`thiscall`. `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x004f7bea`. Body `0x004f7bd0`–`0x004f7bea` is 27 bytes,
SHA-256
`a5fe000f2b8ee504daaf82c2c21deaece2c5dbeba481a00bc2336a1ea7c4092c`.
Zero `E8` / zero `E9`. If `[this+8]` is live, `call [[eax]+8]`
then store 0 at `+8`. `EAX` is forced 0.

Zero inbound `.text` `E8`/`E9`. Unique image copy used as
CLandscapeTexture vtable slot 3 at `0x005dc1fc` (slot 4 is
already-pinned `0x0048e790`). Recreate already zeros `+8` after
the same shape of `[vtable+8]` call. That sibling body is **not**
re-derived here.

Cheapest falsifier: file `0x000f7bd0` is not
`56 8b f1 8b 46 08 85 c0`, **or** `0x000f7bea` is not `c3`,
**or** body SHA-256 is not `a5fe000f…092c`, **or**
`tools/call_xref_scan.py` on `0x004f7bd0` is not empty, **or**
`0x001dc1fc` is not `d0 7b 4f 00`, **or** `0x000f7be0` is not
`c7 46 08 00 00 00 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004f7bd0` | `CUMTexture__VFunc_03_ReleaseTextureResource` | `568bf1 8b4608 85c0 740d 8b08 50 ff5108 c74608 00000000 33c0 5e c3` | thiscall; bare ret; 27 B; 0 E8/E9; 0 inbound; vtable slot 3; zeros `[+8]`. HIGH on ABI, inbound-empty, that slot, that store. **Not** on the `[vtable+8]` body. |
