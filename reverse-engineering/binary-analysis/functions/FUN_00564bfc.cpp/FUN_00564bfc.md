# FUN_00564bfc

Status: active static function note
Last updated: 2026-08-19
Source File: unlabeled (first gates only; do not read this as
a pin of `CScriptObjectCode.cpp.md` / sibling
`CRT__OpenFileByModeString` / already-pinned
`FUN_00564beb`)
|||||||||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. This wake landed `5673ae57`
FUN_00564beb — not redone. Reviewer cycle 73 accepted
through `2b5f8483` — not redone. Already-pinned
FUN_00564beb / FUN_0056473e / `CScriptObjectCode.cpp.md`
were **not** rewritten. Did not adopt C1
`RestoreUnhandledExceptionFilter`.

> Address: `0x00564bfc`

## Contract

Not incoming-ECX `thiscall`. First insn
`push dword [0x009d0980]`. Zero stack args. One bare
`ret` (`0x00564c08`). Body `0x00564bfc`–`0x00564c08` is
13 bytes, SHA-256
`3def9574ab70d0cd8ff9f03e427eafd8f3e1f60114172df720dd56add69d879e`.
Zero `E8`, zero `E9`. Neighbour
`CRT__OpenFileByModeString` starts at `0x00564c09` and
is not claimed.

The body:

1. `push dword [0x009d0980]`.
2. `call dword [0x005d815c]`.
3. Bare `ret`.

The `[0x005d815c]` target body and the meaning of
`0x009d0980` (written by already-pinned `FUN_00564beb`)
are **not** this proof.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`fc 4b 56 00`: file `0x00222b40` / VA `0x00622b40`
(neighbouring dwords are **not** this proof).

Cheapest falsifier: file `0x00164bfc` is not
`ff 35 80 09 9d 00`, **or** `0x00164c08` is not `c3`,
**or** `0x00164c02` is not `ff 15 5c 81 5d 00`, **or**
body SHA-256 is not `3def9574…879e`, **or**
`tools/call_xref_scan.py` on `0x00564bfc` is not empty,
**or** `0x00222b40` is not `fc 4b 56 00`, **or** a
second encoding of that imm exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00564bfc` | `FUN_00564bfc` | `ff3580099d00 ff155c815d00 c3` | not incoming-ECX; bare ret ×1; 13 B; 0 E8 / 0 E9; 0 inbound. HIGH on ABI, unique imm at `0x00622b40`, IAT `[0x005d815c]`. **Not** on `FUN_00564beb`. |
