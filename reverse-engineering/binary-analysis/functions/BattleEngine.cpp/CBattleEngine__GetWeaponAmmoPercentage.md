# CBattleEngine__GetWeaponAmmoPercentage

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
redone. This wake already landed Walker GetWeaponAmmoPercentage
`d781df30` — not redone. Envelope. Did not mill FUN_*. Did not
invent field names. Did not invent a Core owner.

> Address: `0x0040c3c0`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 0x10`. `esi = ecx`.
Three bare `ret` (`0x0040c42f`, `0x0040c448`, `0x0040c458`). Body
`0x0040c3c0`–`0x0040c458` is 153 bytes, SHA-256
`abb3e3f938443eadf4b1bf3ad9fc21ec046c53207d96b588a4b0c7f99d7aeace`.
Capstone: 53 insns, 3 `E8`, zero `E9`, 3 unique rel32 targets.

Pinned body, with `esi = ecx`:

1. `E8` table-named `stricmp` `0x00568390` against image string
   `Racer` at `0x006234f4`. EAX==0 takes the speed arm: vcall
   `[edx+0x6c]`, `fsqrt`, `fmul` 0.666…f at `0x005d8c64`, clamp
   1.0f at `0x005d8568`. The vcall is **not** named here.
2. Else `[esi+0x260]==3` → `ecx = [esi+0x57c]` / `E8`
   table-named `CBattleEngineJetPart__GetWeaponAmmoPercentage`
   `0x004121b0` counted, not contracted.
3. Else `ecx = [esi+0x578]` / `E8` already-pinned
   `CBattleEngineWalkerPart__GetWeaponAmmoPercentage`
   `0x00414410`.

Two inbound `.text` `E8`/`E9`: `CALL` at `0x00486a89` inside
`CHud__RoutePanel_T5_00486940`; `CALL` at `0x00535622` inside
`IScript__GetWeaponAmmo`. Zero encodings of imm `c0 c3 40 00`
in the image (not a vtable slot). Those parent names are
counted, not rewritten.

Source architecture (not proof):
`CBattleEngine::GetWeaponAmmoPercentage`
`BattleEngine.cpp:2758-2774`. The Racer `stricmp` and the
`[+0x260]==3` jet/walker split match that shape. Do **not**
equate the vcall to source `GetVelocity()`.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000c3c0` is not `83 ec 10`, **or**
`0x0000c3c6` is not `68 f4 34 62 00`, **or** `0x0000c43f` is
not `e8 cc 7f 00 00`, **or** `0x0000c458` is not `c3`, **or**
body SHA-256 is not `abb3e3f9…eace`, **or**
`tools/call_xref_scan.py` on `0x0040c3c0` is not exactly those
two `CALL`s, **or** any encoding of imm `c0 c3 40 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `abb3e3f9…eace`. `call_xref_scan` still two CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
the vcall. Did not invent a Core owner.

Retail entity: BattleEngine ammo-percentage dispatcher (Racer
arm, then jet/walker part). Stuart architecture (not proof):
`BattleEngine.cpp:2758-2774`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__GetWeaponAmmoPercentage` /
`CBattleEngine__GetWeaponCharge`. Next named:
`CBattleEngineJetPart__GetWeaponAmmoPercentage` `0x004121b0` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040c3c0` | `CBattleEngine__GetWeaponAmmoPercentage` | `83ec10 8bf1 68f4346200 … e8cc7f0000 … c3` (153 B) | incoming-ECX thiscall; bare ret ×3; 153 B; 3 E8 / 0 E9 / 3 targets; 2 inbound. HIGH on ABI, Racer stricmp, `[+0x260]==3` part dispatch, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on vcall identity or rebuild parity. |
