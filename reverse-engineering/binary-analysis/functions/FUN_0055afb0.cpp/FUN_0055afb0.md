# FUN_0055afb0

Status: active static function note
Last updated: 2026-08-19
Source File: unlabeled (first gates only; do not read this as
a pin of `CScriptObjectCode.cpp.md` / sibling `FUN_0055b080`
/ already-pinned `FUN_0055af90`)
||||||||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. This wake landed `bdbfe391`
FUN_0055af90 — not redone. Reviewer cycle 69 accepted
through `2777aef4` — not redone. Already-pinned
FUN_0055af90 / FUN_0055a340 / `CScriptObjectCode.cpp.md`
were **not** rewritten. Did not adopt C1
`Ident3x4_009cc1d8`.

> Address: `0x0055afb0`

## Contract

Not incoming-ECX `thiscall`. First insn `sub esp, 0x30`.
Zero stack args. One bare `ret` (`0x0055b072`). Body
`0x0055afb0`–`0x0055b072` is 195 bytes, SHA-256
`d25d216500610ad37853f7c00672fdfdc4250bcd7df4c0caaae0c5d01744fea7`.
Zero `E8`, zero `E9`. Thirteen nops after the `ret` are
**not** in the body (table neighbour `FUN_0055b080` starts
at `0x0055b080` and is not claimed).

The body frames `0x30` stack bytes, writes nine of the
twelve dwords, copies twelve dwords into BSS
`0x009cc1d8`–`0x009cc204`, then `add esp, 0x30` / `ret`.
Written immediates: `1.0f` (`0x3f800000`) at
`[esp+0]`, `[esp+0x14]`, `[esp+0x28]`; `0` at
`[esp+4]`, `[esp+8]`, `[esp+0x10]`, `[esp+0x18]`,
`[esp+0x20]`, `[esp+0x24]`. Reads of `[esp+0x0c]`,
`[esp+0x1c]`, `[esp+0x2c]` have **no** prior store in
this body (those three BSS slots receive leftover stack).
Slot type / matrix name is **not** this proof.

Store map (HIGH on the written slots only):

1. `[0x009cc1d8] = 1.0f`
2. `[0x009cc1dc] = 0`
3. `[0x009cc1e0] = 0`
4. `[0x009cc1e4] = leftover [esp+0x0c]`
5. `[0x009cc1e8] = 0`
6. `[0x009cc1ec] = 1.0f`
7. `[0x009cc1f0] = 0`
8. `[0x009cc1f4] = leftover [esp+0x1c]`
9. `[0x009cc1f8] = 0`
10. `[0x009cc1fc] = 0`
11. `[0x009cc200] = 1.0f`
12. `[0x009cc204] = leftover [esp+0x2c]`

`EAX`/`ECX`/`EDX` at the `ret` are leftover. Already-pinned
`FUN_0055af90` zeroes the next three BSS dwords
`0x009cc208`/`20c`/`210`; that body is cited, not claimed.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`b0 af 55 00`: file `0x00222b00` / VA `0x00622b00`
(neighbouring dwords are **not** this proof).

Cheapest falsifier: file `0x0015afb0` is not `83 ec 30`,
**or** `0x0015b072` is not `c3`, **or** body SHA-256 is not
`d25d2165…fea7`, **or** `tools/call_xref_scan.py` on
`0x0055afb0` is not empty, **or** `0x00222b00` is not
`b0 af 55 00`, **or** a second encoding of that imm exists,
**or** `0x0015afb3` is not `c7 44 24 00 00 00 80 3f`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0055afb0` | `FUN_0055afb0` | `83ec30 … 83c430 c3` (195 B) | not incoming-ECX; bare ret ×1; 195 B; 0 E8 / 0 E9; 0 inbound E8/E9. HIGH on ABI, unique imm at `0x00622b00`, nine written BSS immediates, three leftover stack copies. **Not** on `Ident3x4` or `FUN_0055b080`. |
