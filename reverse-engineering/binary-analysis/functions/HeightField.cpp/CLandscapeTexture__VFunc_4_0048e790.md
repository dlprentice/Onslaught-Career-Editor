# CLandscapeTexture__VFunc_4_0048e790

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. The `[vtable+8]` callee is **not** this proof.

> Address: `0x0048e790`

## Contract

Not incoming-`ECX` thiscall. Entry `ECX` is never read. Zero-arg.
Bare `ret` at `0x0048e7ab`. Body `0x0048e790`–`0x0048e7ab` is 28
bytes, SHA-256
`3bb697ce5c313c376730111c0e8695a04241e877e7f02fbd89e64b1c04e39f7f`.
Zero `E8` / zero `E9`. If `[0x006fabf4]` is live, `call [[eax]+8]`
then store 0 at that BSS. `EAX` is forced 0. Four `nop`s after
the `ret` are **not** in the body.

Zero inbound `.text` `E8`/`E9`. Unique image copy of the entry
VA is vtable slot 4 at `0x005dc200` (slot 1 is already-pinned
`0x0048e670`; slot 2 is already-pinned Reset). Caller bodies are
**not** claimed.

Cheapest falsifier: file `0x0008e790` is not
`a1 f4 ab 6f 00 85 c0 74 10`, **or** `0x0008e7ab` is not `c3`,
**or** body SHA-256 is not `3bb697ce…9f7f`, **or**
`tools/call_xref_scan.py` on `0x0048e790` is not empty, **or**
`0x001dc200` is not `90 e7 48 00`, **or** `0x0008e79f` is not
`c7 05 f4 ab 6f 00 00 00 00 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048e790` | `CLandscapeTexture__VFunc_4_0048e790` | `a1f4ab6f00 85c0 7410 8b08 50 ff5108 c705f4ab6f00 00000000 33c0 c3` | not incoming-ECX; bare ret; 28 B; 0 E8/E9; 0 inbound; vtable slot 4; zeros `[0x006fabf4]`. HIGH on ABI, inbound-empty, that slot, that store. **Not** on the `[vtable+8]` body. |
