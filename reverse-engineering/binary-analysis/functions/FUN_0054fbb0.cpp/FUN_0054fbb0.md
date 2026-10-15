# FUN_0054fbb0

Status: active static function note
Last updated: 2026-08-19
Source File: unlabeled (first gates only; do not read this as
a pin of `CScriptObjectCode.cpp.md` / sibling
`DXParticleTexture__GetOrCreate` / already-pinned
`FUN_0054fb90` / table `CTweak__dtor_base_thunk_004530a0`)
|||||||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. This wake landed `c0f1573f`
FUN_0054fb90 — not redone. Reviewer cycle 62 accepted
through `f819ec74` — not redone. Already-pinned
FUN_0054fb90 / FUN_0054fb80 / `CScriptObjectCode.cpp.md`
were **not** rewritten. Did not adopt C1
`JmpThunk_004530a0_0054fbb0`.

> Address: `0x0054fbb0`

## Contract

Not incoming-ECX `thiscall`. First insn `mov ecx, 0x009c6470`
(`b9 70 64 9c 00`). Zero stack args. No `ret` of its own.
Body `0x0054fbb0`–`0x0054fbb9` is 10 bytes, SHA-256
`c961eac6862170ccb14a5d1adaef5aff25a534f58bbccdf12a4c333199b2c8d4`.
Zero `E8`, one `E9`. Six nops after the `jmp` are **not**
in the body (table neighbour
`DXParticleTexture__GetOrCreate` starts at `0x0054fbc0`
and is not claimed).

The body:

1. Plants `ecx = 0x009c6470` (the same immediate
   already-pinned `FUN_0054fb90` plants).
2. `E9` table `CTweak__dtor_base_thunk_004530a0`
   `0x004530a0`.

That callee body is **not** this proof. `EAX` at the
callee `ret` is leftover.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`b0 fb 54 00`: file `0x0014fba2` / VA `0x0054fba2` (the
`push 0x0054fbb0` inside already-pinned `FUN_0054fb90`;
that body is cited, not claimed).

Cheapest falsifier: file `0x0014fbb0` is not `b9 70 64 9c 00`,
**or** `0x0014fbb5` is not `e9 e6 34 f0 ff`, **or** body
SHA-256 is not `c961eac6…c8d4`, **or**
`tools/call_xref_scan.py` on `0x0054fbb0` is not empty,
**or** `0x0014fba2` is not `b0 fb 54 00`, **or** a second
encoding of that imm exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0054fbb0` | `FUN_0054fbb0` | `b970649c00 e9e634f0ff` | not incoming-ECX; tail; 10 B; 0 E8 / 1 E9 table `CTweak__dtor_base_thunk_004530a0`; 0 inbound E8/E9. HIGH on ABI, unique imm at `0x0054fba2`, `ecx=0x009c6470`. **Not** on `0x004530a0` or `FUN_0054fb90`. |
