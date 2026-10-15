# CBattleEngineWalkerPart__GetWeaponAmmoCount

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
redone. This row is already campaign `REBUILD_READY` — not
raised. Envelope only. Did not mill FUN_*. Did not invent field
names. Did not invent a Core owner. Did not edit `rebuild/**`.

> Address: `0x00414470`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 8`. `esi = ecx`.
Two bare `ret` (`0x004144a9`, `0x004144b0`). Body
`0x00414470`–`0x004144b0` is 65 bytes, SHA-256
`4de6a4f384c1a02b1e19c17f1a34a65ccb30f0662854d0e91042c3da31305dc0`.
Capstone: 22 insns, 1 `E8`, zero `E9`, 1 unique rel32 target.
Raw `0xE8` byte count is 1 and matches the instruction count.

Pinned body, with `esi = ecx`:

1. `E8` already-pinned
   `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`.
   EAX==0 returns EAX=0.
2. `[eax+0xa4]` / already-counted `[esi+0x20]` walk. Nonzero
   `[+0x55c]`-shaped dword returns 0. Else `fld` then
   `fistp qword ptr [esp+4]` at `0x0041449d` (`df 7c 24 04`)
   and EAX is that low dword. Those slots are **not** named
   here.

One inbound `.text` `E8`/`E9`: `JMP` at `0x0040c46f` inside
already-named `CBattleEngine__GetWeaponAmmoCount` `0x0040c460`.
Zero encodings of imm `70 44 41 00` in the image (not a vtable
slot). The parent table name is counted, not rewritten.

Source architecture (not proof):
`CBattleEngineWalkerPart::GetWeaponAmmoCount`
`BattleEngineWalkerPart.cpp:847-858`. Retail `fistp` is the
conversion site. Bare `ret` matches zero stack args.

Rebuild mapping: existing `REBUILD_READY` **not raised**. This
note is a PE envelope only. Do not implement Core from this RE
root.

Cheapest falsifier: file `0x00014470` is not `83 ec 08`, **or**
`0x00014474` is not `8b f1`, **or** `0x00014476` is not
`e8 b5 fb ff ff`, **or** `0x0001449d` is not `df 7c 24 04`,
**or** `0x000144b0` is not `c3`, **or** body SHA-256 is not
`4de6a4f3…5dc0`, **or** `tools/call_xref_scan.py` on
`0x00414470` is not exactly one `JMP` at `0x0040c46f`, **or**
any encoding of imm `70 44 41 00` exists.

## Rebuild mapping — 2026-08-19

Existing campaign grade `REBUILD_READY` is **not raised**.
Independently re-read official+twin `74154bfa` this wake
(2506752 equal). Body SHA-256 still `4de6a4f3…5dc0`.
`0x0001449d` still `df7c2404`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not invent
a Core owner.

Retail entity: walker-part ammo-count query. Stuart architecture
(not proof): `BattleEngineWalkerPart.cpp:847-858`.

Nearest reconstruction owner: **none added**. Existing
`REBUILD_READY` mapping is not rewritten. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__GetWeaponAmmoPercentage` /
`CBattleEngineWalkerPart__GetCurrentWeapon`. Next named:
`CBattleEngine__GetWeaponAmmoCount` `0x0040c460` (no 2026-08-19
PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00414470` | `CBattleEngineWalkerPart__GetWeaponAmmoCount` | `83ec08 8bf1 e8b5fbffff … df7c2404 … c3` (65 B) | incoming-ECX thiscall; bare ret ×2; 65 B; 1 E8 / 0 E9 / 1 target; 1 inbound JMP. HIGH on ABI, GetCurrentWeapon, fistp site, unique inbound. Existing `REBUILD_READY` **not raised**. **Not** on store-slot names or a new Core owner. |
