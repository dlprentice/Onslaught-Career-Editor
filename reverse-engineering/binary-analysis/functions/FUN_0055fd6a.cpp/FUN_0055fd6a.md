# FUN_0055fd6a

Status: active static function note
Last updated: 2026-08-19
Source File: unlabeled (first gates only; do not read this as
a pin of `CScriptObjectCode.cpp.md` / sibling `__alldiv`
/ table `CRT__CallocWithRetry` / already-pinned
`FUN_0055e3f4`)
|||||||||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. This wake landed `0eaabb19`
FUN_0055e3f4 — not redone. Reviewer cycle 71 accepted
through `1c0105f9` — not redone. Already-pinned
FUN_0055e3f4 / FUN_0055dfb8 / `CScriptObjectCode.cpp.md`
were **not** rewritten. Did not adopt C1
`CallocFill6533c0`.

> Address: `0x0055fd6a`

## Contract

Not incoming-ECX `thiscall`. First insn
`mov eax, dword [0x009d4600]`. Zero stack args. One
bare `ret` (`0x0055fe11`). Body `0x0055fd6a`–`0x0055fe11`
is 168 bytes, SHA-256
`0675dac7036a4490a12c5a81873e5e1680a37d0528ed470a7b308503adc0848f`.
Three `E8`, zero `E9`. Neighbour `FUN_0055fe12` starts at
`0x0055fe12` and is not claimed.

The body:

1. Loads `[0x009d4600]` into `EAX`. `push esi` then
   `push 0x14` / `pop esi` (`ESI = 0x14`).
2. If `EAX == 0`: `EAX = 0x200`. Else if `EAX < 0x14`:
   `EAX = 0x14`. Stores `EAX` at `0x009d4600`.
3. `push 4` / `push eax` / `E8` table
   `CRT__CallocWithRetry` `0x005689b8` / `pop ecx`.
4. Stores `EAX` at `0x009d35f8`. If `EAX == 0`: store
   `ESI` at `0x009d4600`, `push 4` / `push esi` / same
   `E8` / if still 0: `push 0x1a` / `E8` table
   `__amsg_exit` `0x00560289` / `pop ecx`.
5. Loop: `EAX = 0x006533c0`, `ECX = 0`,
   `EDX = [0x009d35f8]`; `[edx+ecx] = eax`;
   `eax += 0x20`; `ecx += 4`; while `EAX < 0x00653640`.
6. Loop: `EDX = 0x006533d0`, `ECX = 0`; indexed read
   through `[0x009d32a0]`; if that dword is `0` or `-1`,
   `or dword [edx], -1`; `edx += 0x20`; `inc ecx`;
   while `EDX < 0x00653430`.
7. `pop esi` / bare `ret`.

The `CRT__CallocWithRetry` / `__amsg_exit` bodies and
the meaning of `0x14` / `0x200` / `0x1a` / the two
pointer walks are **not** this proof.

Three body `E8` sites: `0x0055fd8c` `0x005689b8`,
`0x0055fda5` `0x005689b8`, `0x0055fdb7` `0x00560289`.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`6a fd 55 00`: file `0x00222b1c` / VA `0x00622b1c`
(neighbouring dwords are **not** this proof).

Cheapest falsifier: file `0x0015fd6a` is not
`a1 00 46 9d 00`, **or** `0x0015fe11` is not `c3`,
**or** body SHA-256 is not `0675dac7…848f`, **or**
`tools/call_xref_scan.py` on `0x0055fd6a` is not empty,
**or** `0x0015fd8c` is not `e8 27 8c 00 00`, **or**
`0x00222b1c` is not `6a fd 55 00`, **or** a second
encoding of that imm exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0055fd6a` | `FUN_0055fd6a` | `a100469d00 … 5ec3` (168 B) | not incoming-ECX; bare ret ×1; 168 B; 3 E8 table `CRT__CallocWithRetry` ×2 / `__amsg_exit` / 0 E9; 0 inbound E8/E9. HIGH on ABI, unique imm at `0x00622b1c`, `0x009d4600`/`0x009d35f8`. **Not** on those callees. |
