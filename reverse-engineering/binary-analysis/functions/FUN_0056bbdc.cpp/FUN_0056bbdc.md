# FUN_0056bbdc

Status: active static function note
Last updated: 2026-08-19
Source File: unlabeled (first gates only; do not read this as
a pin of `CScriptObjectCode.cpp.md` / sibling
`CRT__NormalizeLocaleGroupingStringInPlace` /
neighbour `CRT__LoadMonetaryLocaleInfoTable` /
already-pinned `FUN_0056b9d0`)
||||||||||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. This wake landed `d972987b`
FUN_0056b9d0 — not redone. Reviewer cycle 73 accepted
through `2b5f8483` — not redone. Already-pinned
FUN_0056b9d0 / FUN_00568af5 / `CScriptObjectCode.cpp.md`
were **not** rewritten. Did not adopt C1
`CallocLoadMonetary`.

> Address: `0x0056bbdc`

## Contract

Not incoming-ECX `thiscall`. First insn
`cmp dword [0x009d099c], 0`. Zero stack args. Two
bare `ret` (`0x0056bbfb` returns 1;
`0x0056bca6` returns 0). Body
`0x0056bbdc`–`0x0056bca6` is 203 bytes, SHA-256
`09c4fb91b148c5e2c7e03a4568d30641c629389626b039f19b5f207abe35b8c0`.
Eight `E8`, zero `E9` (short `jmp`/`jcc` only).
Neighbour `CRT__LoadMonetaryLocaleInfoTable` starts at
`0x0056bca7` and is not claimed. Preceding table
`CRT__NormalizeLocaleGroupingStringInPlace` ends at
`0x0056bbdb` and is not claimed. The early `ret` at
`0x0056bbfb` is inside this body.

The body:

1. `cmp [0x009d099c], 0` / `push esi` /
   `je 0x0056bc5c`.
2. Else: `push 0x30` / `push 1` / `E8` table
   `CRT__CallocWithRetry` `0x005689b8`. If ESI is 0:
   `eax = 1` / `pop esi` / bare `ret` at
   `0x0056bbfb`.
3. Else `E8` neighbour
   `CRT__LoadMonetaryLocaleInfoTable` `0x0056bca7`. If
   EAX nonzero: `E8` table `CRT__FreeLocaleBufferSet`
   `0x0056bdc9` then table `CRT__FreeBase` `0x0055f085`,
   then `jmp 0x0056bbf7` (the return-1 epilogue).
4. Else copy three dwords from `[0x00656b90]` into ESI,
   store ESI at `0x00656b90`, `E8` those same two
   free helpers on `[0x009d0ae8]`, store ESI there,
   `jmp 0x0056bca3`.
5. Zero-`[0x009d099c]` arm: copy three dwords from
   `[[0x00656b90]]` to `0x00656b60` / `+4` / `+8`,
   store `0x00656b60` at `0x00656b90`, the same two
   free helpers, `and [0x009d0ae8], 0`.
6. `xor eax, eax` / `pop esi` / bare `ret`.

Those callee bodies and the BSS / pointer-object
meanings are **not** this proof.

Eight body `E8` sites: `0x0056bbea` `0x005689b8`;
`0x0056bbfd` `0x0056bca7`; `0x0056bc08` /
`0x0056bc42` / `0x0056bc8a` `0x0056bdc9`;
`0x0056bc0e` / `0x0056bc4d` / `0x0056bc95`
`0x0055f085`.

Zero inbound `.text` `E8`/`E9`. One image encoding of
imm `dc bb 56 00`: file `0x00253d5c` / VA `0x00653d5c`
in `.data` (neighbouring dwords are **not** this
proof).

Cheapest falsifier: file `0x0016bbdc` is not
`83 3d 9c 09 9d 00 00`, **or** `0x0016bbfb` is not
`c3`, **or** `0x0016bca6` is not `c3`, **or**
`0x0016bbea` is not `e8 c9 cd ff ff`, **or** body
SHA-256 is not `09c4fb91…b8c0`, **or**
`tools/call_xref_scan.py` on `0x0056bbdc` is not
empty, **or** `0x00253d5c` is not `dc bb 56 00`,
**or** a second encoding of that imm exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0056bbdc` | `FUN_0056bbdc` | `833d9c099d0000 … 33c0 5e c3` (203 B) | not incoming-ECX; bare ret ×2; 203 B; 8 E8 / 0 E9; 0 inbound. HIGH on ABI, unique imm at `0x00653d5c`, callee sites. **Not** on those callees. |
