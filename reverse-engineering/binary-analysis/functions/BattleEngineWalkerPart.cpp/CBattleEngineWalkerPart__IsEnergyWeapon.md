# CBattleEngineWalkerPart__IsEnergyWeapon

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
101 accepted through JetPart GetWeaponCharge `f31bee59` — not
redone. Envelope. Did not mill FUN_*. Did not invent field names.
Did not invent a Core owner.

> Address: `0x004144c0`

## Contract

Incoming-ECX `thiscall`. First insn `push esi`. `esi = ecx`.
Two bare `ret` (`0x004144e0`, `0x004144e4`). Body
`0x004144c0`–`0x004144e4` is 37 bytes, SHA-256
`84d87e6d863fd78b1b4ae4f66d82725f5c608df7237cc097772e033883e82d14`.
Capstone: 14 insns, 1 `E8`, zero `E9`, 1 unique rel32 target.

Pinned body, with `esi = ecx`:

1. `E8` already-pinned
   `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`.
   EAX==0 returns EAX=0.
2. Else `[eax+0xa4]` / already-counted `[esi+0x20]` then EAX =
   `[edx+ecx*4+0x55c]`. That slot is **not** named here.

One inbound `.text` `E8`/`E9`: `JMP` at `0x0040c48f` inside
already-named `CBattleEngine__IsEnergyWeapon` `0x0040c480`. Zero
encodings of imm `c0 44 41 00` in the image (not a vtable slot).
The parent table name is counted, not rewritten.

Source architecture (not proof):
`CBattleEngineWalkerPart::IsEnergyWeapon`
`BattleEngineWalkerPart.cpp:861-867`. Bare `ret` matches zero
stack args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x000144c0` is not `56`, **or**
`0x000144c1` is not `8b f1`, **or** `0x000144c3` is not
`e8 68 fb ff ff`, **or** `0x000144e4` is not `c3`, **or** body
SHA-256 is not `84d87e6d…2d14`, **or**
`tools/call_xref_scan.py` on `0x004144c0` is not exactly one
`JMP` at `0x0040c48f`, **or** any encoding of imm `c0 44 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `84d87e6d…2d14`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x55c]`. Did not invent a Core owner.

Retail entity: walker-part IsEnergyWeapon query. Stuart
architecture (not proof): `BattleEngineWalkerPart.cpp:861-867`.

Nearest reconstruction owner: **none added**. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__GetWeaponAmmoCount` /
`CBattleEngine__GetWeaponAmmoCount`. Next named:
`CBattleEngineWalkerPart__IsWeaponOverheated` `0x004144f0` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004144c0` | `CBattleEngineWalkerPart__IsEnergyWeapon` | `56 8bf1 e868fbffff … c3` (37 B) | incoming-ECX thiscall; bare ret ×2; 37 B; 1 E8 / 0 E9 / 1 target; 1 inbound JMP. HIGH on ABI, GetCurrentWeapon, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x55c]` name or rebuild parity. |
