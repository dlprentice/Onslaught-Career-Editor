# CBattleEngineWalkerPart__GetWeaponName

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
103 follow-up accepted overheat parent/jet `4013d039` /
`63c63909` — not redone. Cycle 103 close: energy dispatcher
`b5df91bf` was not independently accepted that cycle. This wake
already landed jet IsEnergyWeapon `f4d68375` — not independently
accepted this cycle. Envelope. Did not mill FUN_*. Did not invent
field names. Did not invent a Core owner.

> Address: `0x004145a0`

## Contract

Incoming-ECX `thiscall`. First insn `E8` already-pinned
`CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`. Two
bare `ret` (`0x004145bd`, `0x004145c0`). Body
`0x004145a0`–`0x004145c0` is 33 bytes, SHA-256
`a1097bdd060638de5cea054642b603238316c74ee2ba8a7197a04b704fe23c98`.
Capstone: 11 insns, 2 `E8`, zero `E9`, 2 unique rel32 targets.

Pinned body:

1. `E8` `GetCurrentWeapon` `0x00414030`. EAX==0 returns EAX=0.
2. Else `[eax+0xa4]`, then `[eax+0x3c]` is pushed. `ecx` is
   loaded with immediate `0x0083d960`. Second `E8` table-named
   `CText__GetStringById` `0x004f2580`. Those slots and the
   immediate this-pointer are **not** named here. The text
   callee is counted, not rewritten.

One inbound `.text` `E8`/`E9`: `JMP` at `0x0040c55f` inside
table-named `CBattleEngine__GetWeaponName` `0x0040c550`. Zero
encodings of imm `a0 45 41 00` in the image (not a vtable slot).
The parent table name is counted, not rewritten.

Source architecture (not proof):
`CBattleEngineWalkerPart::GetWeaponName`
`BattleEngineWalkerPart.cpp:900-906`. Bare `ret` matches zero
stack args on this function. The text callee's own ABI is not
re-derived here.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x000145a0` is not `e8 8b fa ff ff`,
**or** `0x000145b8` is not `e8 c3 df 0d 00`, **or**
`0x000145c0` is not `c3`, **or** body SHA-256 is not
`a1097bdd…3c98`, **or** `tools/call_xref_scan.py` on
`0x004145a0` is not exactly one `JMP` at `0x0040c55f`, **or**
any encoding of imm `a0 45 41 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `a1097bdd…3c98`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x3c]` / `0x0083d960`. Did not invent a Core owner.

Retail entity: walker-part weapon display-name query. Stuart
architecture (not proof): `BattleEngineWalkerPart.cpp:900-906`.

Nearest reconstruction owner: **none added**. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__IsWeaponOverheated` /
`CBattleEngineWalkerPart__GetCurrentWeapon`. Next named:
`CBattleEngine__GetWeaponName` `0x0040c550` (no 2026-08-19 PE
envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004145a0` | `CBattleEngineWalkerPart__GetWeaponName` | `e88bfaffff … e8c3df0d00 … c3` (33 B) | incoming-ECX thiscall; bare ret ×2; 33 B; 2 E8 / 0 E9 / 2 targets; 1 inbound JMP. HIGH on ABI, GetCurrentWeapon, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x3c]` / `0x0083d960` name or rebuild parity. |
