# CVM__ScalarDeletingDestructor

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CVM (first gates only; do not
read this as a pin of `CScriptObjectCode.cpp.md` /
`ScriptObjectCode.cpp.md` / `CMonitor.cpp.md` /
`CVM__Destructor.cpp` / `FUN_005398c0.cpp`)
||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). Adopted `t_cb6c7049` after
independent re-derivation (steward cycle 46 re-read the
child; this card owns the land). The Ghidra database was
not opened. Table name is a research label. Already-pinned
`CVM__Destructor` `0x00535350` (02ccd358) / `FUN_005398c0`
(da0426b4) / ctor2 `0x00539c80` (2ee8a68e) / ClearFields
`0x00539f40` (91dcfad8) / the `0x00549220` callee were
**not** written. HEAD at measure `91dcfad8`. Did not steal
sibling `0x00539ca0`.

> Address: `0x00535330`

## Contract

`thiscall`, not SEH. First insn `push esi` / `mov esi, ecx`.
One stack dword. One `ret 4` (`0x0053534d`). Body
`0x00535330`–`0x0053534f` is 32 bytes, SHA-256
`d3ca227b2c8ae36d53cafbcb361f2bfc362fccd0f617ca5b6d20531f7538c566`.
Two `E8`, zero `E9`. Neighbour already-pinned
`CVM__Destructor` starts at the next byte (`0x00535350`).
One nop after predecessor `ret 0xc` (`0x0053532c`) is
**not** in the body.

The already-pinned destructor body is **not** this proof.
This wrapper only:

1. `esi = ecx`, then `E8` already-pinned `CVM__Destructor`
   `0x00535350` (`ecx = this`).
2. `test byte [esp+8], 1`. If clear, skip the next call.
3. Else `push esi` / `E8` `0x00549220` with
   `ecx = 0x009c3df0`.

`EAX = this` at the `ret` (`8b c6`). The `0x00549220` body
is **not** this proof. This body does **not** write `[this]`.

Two body `E8` sites: `0x00535333` `0x00535350`,
`0x00535345` `0x00549220`.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`30 53 53 00`: file `0x001e4f20` / VA `0x005e4f20`. That
slot's other dwords are **not** this proof.

Cheapest falsifier: file `0x00135330` is not `56`,
**or** `0x0013534d` is not `c2 04 00`, **or** body SHA-256
is not `d3ca227b…c566`, **or** `tools/call_xref_scan.py` on
`0x00535330` is not empty, **or** `0x00135333` is not
`e8 18 00 00 00`, **or** `0x001e4f20` is not `30 53 53 00`,
**or** a second encoding of that imm exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00535330` | `CVM__ScalarDeletingDestructor` | `56 8bf1 e818000000 f644240801 740b 56 b9f03d9c00 e8d63e0100 8bc6 5e c20400` | thiscall; ret 4 ×1; 32 B; 2 E8 / 0 E9; 0 inbound E8/E9. HIGH on ABI, unique imm slot at `0x005e4f20`, already-pinned dtor then bit0 `0x00549220`. **Not** on `0x00549220` or the destructor body. |
