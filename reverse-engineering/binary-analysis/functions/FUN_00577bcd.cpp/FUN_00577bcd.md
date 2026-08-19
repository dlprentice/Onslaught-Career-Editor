# FUN_00577bcd

Status: active static function note
Last updated: 2026-08-19
Source File: unlabeled (first gates only; do not read this as
a pin of `CScriptObjectCode.cpp.md` / sibling
`FUN_00577bc0` / neighbour
`CTexture__DispatchPtr00656fe0_WithInit` /
already-pinned `FUN_00577bc0`)
||||||||||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. This wake landed `9fed30e5`
FUN_00577bc0 — not redone. Reviewer cycle 78 accepted
through `b36986c9`. Already-pinned
FUN_00577bc0 / FUN_00577b2a / `CScriptObjectCode.cpp.md`
were **not** rewritten. Did not adopt C1
`Norm4IfOutsideTol`.

> Address: `0x00577bcd`

## Contract

Not incoming-ECX `thiscall`. First insn `push ebp`.
Two stack dwords (`ret 0x8` at `0x00577c80`). Body
`0x00577bcd`–`0x00577c82` is 182 bytes, SHA-256
`b64cbf37dbfa9a52907da775963faf84f4090c9a575f57605f91d49a37ee3c2c`.
One `E8`, zero `E9`. Neighbour table
`CTexture__DispatchPtr00656fe0_WithInit` starts at
`0x00577c83` and is not claimed. Preceding table
`FUN_00577bc0` ends at `0x00577bcc` and is not
rewritten.

The body:

1. `push ebp` / `mov ebp, esp` / `sub esp, 0x10`.
2. `ESI = [ebp+0xc]`; four `fld` of
   `[esi]`..`[esi+0xc]`.
3. One `E8` at `0x00577c12` to table
   `Math__IsFloatDiffOutsideTolerance` `0x00575986`.
4. `pop edi` / `pop esi` / `leave` / `ret 0x8`.

Those field meanings and the callee body are **not**
this proof.

Zero inbound `.text` `E8`/`E9`. One image encoding of
imm `cd 7b 57 00`: file `0x002570a0` / VA `0x006570a0`
in `.data` (neighbouring dwords are **not** this
proof).

Cheapest falsifier: file `0x00177bcd` is not `55`,
**or** `0x00177c80` is not `c2 08 00`, **or**
`0x00177bd0` is not `83 ec 10`, **or** body SHA-256
is not `b64cbf37…3c2c`, **or**
`tools/call_xref_scan.py` on `0x00577bcd` is not
empty, **or** `0x002570a0` is not `cd 7b 57 00`,
**or** a second encoding of that imm exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00577bcd` | `FUN_00577bcd` | `558bec 83ec10 … 5f5e c9 c20800` (182 B) | not incoming-ECX; ret 0x8; 182 B; 1 E8 `Math__IsFloatDiffOutsideTolerance` / 0 E9; 0 inbound. HIGH on ABI, unique imm at `0x006570a0`. **Not** on field meaning or the callee. |
