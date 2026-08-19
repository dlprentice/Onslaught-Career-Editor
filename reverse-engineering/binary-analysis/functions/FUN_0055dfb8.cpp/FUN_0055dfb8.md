# FUN_0055dfb8

Status: active static function note
Last updated: 2026-08-19
Source File: unlabeled (first gates only; do not read this as
a pin of `CScriptObjectCode.cpp.md` / sibling
`CRT__RoundDoubleWithFpuChecks` / table `_malloc` /
already-pinned `FUN_0055dbe8`)
||||||||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. This wake landed `291a3833`
FUN_0055dbe8 — not redone. Reviewer cycle 70 accepted
through `291a3833` — not redone. Already-pinned
FUN_0055dbe8 / FUN_0055b0d0 / `CScriptObjectCode.cpp.md`
were **not** rewritten. Did not adopt C1
`OnexitTableAlloc80`.

> Address: `0x0055dfb8`

## Contract

Not incoming-ECX `thiscall`. First insn `push 0x80`. Zero
stack args. One bare `ret` (`0x0055dfe6`). Body
`0x0055dfb8`–`0x0055dfe6` is 47 bytes, SHA-256
`fa89ea601b25853cddb989d8a659d8fa0c39a31db641ee31c636d4bc82e42b5b`.
Two `E8`, zero `E9`. Neighbour
`CRT__RoundDoubleWithFpuChecks` starts at `0x0055dfe7`
and is not claimed.

The body:

1. `push 0x80`.
2. `E8` table `_malloc` `0x0055ec0c` / `pop ecx`.
3. Stores `EAX` at `0x009d4610`.
4. If `EAX == 0`: `push 0x18`, `E8` table `__amsg_exit`
   `0x00560289` / reload `EAX` from `0x009d4610` /
   `pop ecx`.
5. `and dword [eax], 0`.
6. Reloads `EAX` from `0x009d4610` and stores it at
   `0x009d460c`.

The `_malloc` / `__amsg_exit` bodies and the meaning of
imm `0x80` / `0x18` are **not** this proof. `EAX` at the
`ret` is the `0x009d4610` pointer.

Two body `E8` sites: `0x0055dfbd` `0x0055ec0c`,
`0x0055dfce` `0x00560289`.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`b8 df 55 00`: file `0x00222b14` / VA `0x00622b14`
(neighbouring dwords are **not** this proof).

Cheapest falsifier: file `0x0015dfb8` is not `68 80 00 00 00`,
**or** `0x0015dfe6` is not `c3`, **or** body SHA-256 is not
`fa89ea60…2b5b`, **or** `tools/call_xref_scan.py` on
`0x0055dfb8` is not empty, **or** `0x0015dfbd` is not
`e8 4a 0c 00 00`, **or** `0x00222b14` is not `b8 df 55 00`,
**or** a second encoding of that imm exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0055dfb8` | `FUN_0055dfb8` | `6880000000 e84a0c0000 85c0 59 a310469d00 750d 6a18 e8b6220000 a110469d00 59 832000 a110469d00 a30c469d00 c3` | not incoming-ECX; bare ret ×1; 47 B; 2 E8 / 0 E9; 0 inbound E8/E9. HIGH on ABI, unique imm at `0x00622b14`, `0x009d4610`/`0x009d460c`. **Not** on `_malloc` or `__amsg_exit`. |
