# CBattleEngine__GetWeaponAmmoCount

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
101 accepted through JetPart GetWeaponCharge `f31bee59` — not
redone. This wake already landed Walker GetWeaponAmmoCount
`0c6bc5a1` — not redone. Envelope. Did not mill FUN_*. Did not
invent field names. Did not rename the jet JMP target. Did not
invent a Core owner.

> Address: `0x0040c460`

## Contract

Incoming-ECX `thiscall`. First insn `cmp dword [ecx+0x260], 3`.
Zero `ret`. Body `0x0040c460`–`0x0040c47e` is 31 bytes, SHA-256
`2c9f1fac5c5af72c9ea1218e1b4499c12fe8ea76c5bf46f027d5c43485a7373c`.
Capstone: 6 insns, zero `E8`, 2 `E9`, 2 unique rel32 targets.

Pinned body:

1. `[ecx+0x260]==3` → `ecx = [ecx+0x57c]` / `E9`
   table-named `CGeneralVolume__GetMode3CurrentEntryRoundedSlotValue`
   `0x00412240`. That table name is counted, not rewritten.
2. Else `ecx = [ecx+0x578]` / `E9` already-pinned
   `CBattleEngineWalkerPart__GetWeaponAmmoCount` `0x00414470`.

One inbound `.text` `E8`/`E9`: `CALL` at `0x00486d56` inside
`CHud__RoutePanel_T5_00486940`. Zero encodings of imm
`60 c4 40 00` in the image (not a vtable slot). The inbound
parent is counted, not rewritten.

Source architecture (not proof):
`CBattleEngine::GetWeaponAmmoCount`
`BattleEngine.cpp:2777-2783`. The `[+0x260]==3` jet/walker split
matches that shape. Do **not** equate `0x00412240`'s current
table name to source `CBattleEngineJetPart::GetWeaponAmmoCount`.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000c460` is not
`83 b9 60 02 00 00 03`, **or** `0x0000c46f` is not
`e9 fc 7f 00 00`, **or** `0x0000c47a` is not
`e9 c1 5d 00 00`, **or** body SHA-256 is not `2c9f1fac…373c`,
**or** `tools/call_xref_scan.py` on `0x0040c460` is not exactly
one `CALL` at `0x00486d56`, **or** any encoding of imm
`60 c4 40 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `2c9f1fac…373c`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not rename
`0x00412240`. Did not invent a Core owner.

Retail entity: BattleEngine ammo-count dispatcher. Stuart
architecture (not proof): `BattleEngine.cpp:2777-2783`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__GetWeaponAmmoCount` /
`CBattleEngine__GetWeaponAmmoPercentage`. Next named:
`CBattleEngineWalkerPart__IsEnergyWeapon` `0x004144c0` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040c460` | `CBattleEngine__GetWeaponAmmoCount` | `83b96002000003 … e9fc7f0000 … e9c15d0000` (31 B) | incoming-ECX thiscall; 0 ret; 31 B; 0 E8 / 2 E9 / 2 targets; 1 inbound CALL. HIGH on ABI, `[+0x260]==3` tail-jmp dispatch, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on jet-target rename or rebuild parity. |
