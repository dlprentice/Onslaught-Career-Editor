# FUN_00590cae

Status: active static function note
Last updated: 2026-08-19
Source File: unlabeled (first gates only; do not read this as
a pin of `CScriptObjectCode.cpp.md` / sibling
`FUN_00590c8e` / neighbour `FUN_00590cb8` /
already-pinned `FUN_00590c8e`)
|||||||||||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. This wake landed `3898279d`
FUN_00590c8e — not redone. Reviewer cycle 84 accepted
through `5185804f`. Already-pinned
FUN_00590c8e / FUN_00590c81 / `CScriptObjectCode.cpp.md`
were **not** rewritten. Did not adopt C1
`ReturnField0c`.

> Address: `0x00590cae`

## Contract

Not incoming-ECX `thiscall`. First insn
`mov eax, [esp+4]`. One stack dword (`ret 0x4` at
`0x00590cb5`). Body `0x00590cae`–`0x00590cb7` is 10
bytes, SHA-256
`688381b35e2008a7fd7b33f9da2c5ccb883831e156d091e6e795e95df034eca5`.
Zero `E8`, zero `E9`. Neighbour table `FUN_00590cb8`
starts at `0x00590cb8` and is not claimed. Preceding
table `FUN_00590c8e` ends at `0x00590cad` and is not
rewritten.

The body:

1. `EAX = [esp+4]`.
2. `EAX = [eax+0xc]`.
3. `ret 0x4`.

Those field meanings are **not** this proof.

Zero inbound `.text` `E8`/`E9`. One image encoding of
imm `ae 0c 59 00`: file `0x001ed3e8` / VA `0x005ed3e8`
(neighbouring dwords are **not** this proof).

Cheapest falsifier: file `0x00190cae` is not
`8b 44 24 04`, **or** `0x00190cb5` is not
`c2 04 00`, **or** `0x00190cb2` is not `8b 40 0c`,
**or** body SHA-256 is not `688381b3…eca5`, **or**
`tools/call_xref_scan.py` on `0x00590cae` is not
empty, **or** `0x001ed3e8` is not `ae 0c 59 00`,
**or** a second encoding of that imm exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00590cae` | `FUN_00590cae` | `8b442404 8b400c c20400` (10 B) | not incoming-ECX; ret 0x4; 10 B; 0 E8 / 0 E9; 0 inbound. HIGH on ABI, unique imm at `0x005ed3e8`. **Not** on field meaning. |
