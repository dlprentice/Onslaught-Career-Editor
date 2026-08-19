# FUN_00564beb

Status: active static function note
Last updated: 2026-08-19
Source File: unlabeled (first gates only; do not read this as
a pin of `CScriptObjectCode.cpp.md` / sibling
`FUN_00564bfc` / table
`CRT__UnhandledExceptionFilterDispatch` / already-pinned
`FUN_0056473e`)
|||||||||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. This wake landed `983da7bf`
FUN_0056473e — not redone. Reviewer cycle 73 accepted
through `2b5f8483` — not redone. Already-pinned
FUN_0056473e / FUN_00564471 / `CScriptObjectCode.cpp.md`
were **not** rewritten. Did not adopt C1
`SetUnhandledExceptionFilter`.

> Address: `0x00564beb`

## Contract

Not incoming-ECX `thiscall`. First insn `push 0x00564ba5`.
Zero stack args. One bare `ret` (`0x00564bfb`). Body
`0x00564beb`–`0x00564bfb` is 17 bytes, SHA-256
`2508681a76f376d625c54287386c37826560213569607abb3eb17d0c30c04a8b`.
Zero `E8`, zero `E9`. Neighbour `FUN_00564bfc` starts at
`0x00564bfc` and is not claimed.

The body:

1. `push 0x00564ba5` (table
   `CRT__UnhandledExceptionFilterDispatch`; not claimed).
2. `call dword [0x005d815c]`.
3. Stores `EAX` at `0x009d0980`.
4. Bare `ret`.

The `[0x005d815c]` target body and the meaning of
`0x009d0980` are **not** this proof.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`eb 4b 56 00`: file `0x00222b24` / VA `0x00622b24`
(neighbouring dwords are **not** this proof).

Cheapest falsifier: file `0x00164beb` is not
`68 a5 4b 56 00`, **or** `0x00164bfb` is not `c3`,
**or** `0x00164bf0` is not `ff 15 5c 81 5d 00`, **or**
body SHA-256 is not `2508681a…4a8b`, **or**
`tools/call_xref_scan.py` on `0x00564beb` is not empty,
**or** `0x00222b24` is not `eb 4b 56 00`, **or** a
second encoding of that imm exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00564beb` | `FUN_00564beb` | `68a54b5600 ff155c815d00 a380099d00 c3` | not incoming-ECX; bare ret ×1; 17 B; 0 E8 / 0 E9; 0 inbound. HIGH on ABI, unique imm at `0x00622b24`, IAT `[0x005d815c]`. **Not** on `0x00564ba5`. |
