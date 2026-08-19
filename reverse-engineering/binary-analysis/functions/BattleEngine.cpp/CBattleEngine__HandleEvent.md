# CBattleEngine__HandleEvent

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
92 accepted StartLock/LockHit — not redone. This wake landed
`3903b735` CalcUnitOverCrossHair — not redone. Did not mill FUN_*.
Did not implement lock sets.

> Address: `0x0040c180`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 0x100`. Several
`ret 0x4`; last at `0x0040c2db`. Body `0x0040c180`–`0x0040c2dd`
is 350 bytes, SHA-256
`0af705098a485b1f8b1a98ab0cde4b77c664c4b55547e03beb6496cc66b90ade`.
Capstone: 93 insns, 9 `E8`, zero `E9`. Neighbour table
`CBattleEngine__CanSpawnBurstForResolvedEntry` starts at
`0x0040c2e0` and is not rewritten. Preceding table
`CBattleEngine__StartDieProcess` ends at `0x0040c17b` and is not
rewritten.

The body, with `esi = ecx` and `ecx = [esp+0x108]` after the
`push esi` (the event pointer):

1. `movsx eax, word [ecx+4]`. Compare EAX to `0x1770`, `0x1771`,
   `0xfa2`, then `sub eax, 0x1772`.
2. `0x1770`: if `[esi+0x260]==1`, store BSS `[0x00672fd0]` to
   `[esi+0x520]`, write `[esi+0x260]=3`, `E8` `0x004063b0`
   (`CBattleEngine__UpdateWeaponEffect`). Table name is not
   `SetCollisionShape`.
3. `0x1771`: write `[esi+0x260]=2`, same `E8` `0x004063b0`.
4. After `sub eax, 0x1772`: zero → `push 1` / `push 1` / `push`
   event / `E8` `CBattleEngine__CalcUnitOverCrossHair`
   `0x0040acc0`, then `SetReader` of EAX onto `[esi+0x4c8]`.
   One → `E8` `CBattleEngine__HandleAutoAim` `0x0040b6d0`.
5. Default: `E8` `CUnit__HandleEvent` `0x004f9820`.
6. `0xfa2` arm calls `sprintf` / `CSoundManager__GetEffectByName`
   / `CSoundManager__PlayEffect`. That id is **not** named here.

`+0x260` values 1/2/3 match the already-closed JET=3 polarity.
Source architecture (not proof): `EBattleEngineEvent` `BECOME_JET
= 6000` (`0x1770`) through `HANDLE_AUTO_AIM`, and
`EBattleEngineState` morphing-into-jet=1 / walker=2 / jet=3
(`BattleEngine.h:28-33`, `:20-26`). `HandleEvent` body
`BattleEngine.cpp:2665-2710`.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`80 c1 40 00`: file `0x001d89c4` / VA `0x005d89c4` (the
`CBattleEngine` vtable base named by the GetCurrentTarget note).
Neighbouring dwords are **not** this proof.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000c180` is not `81 ec 00 01 00 00`,
**or** `0x0000c190` is not `0f bf 41 04`, **or** `0x0000c1d1` is
not `c7 86 60 02 00 00 03 00 00 00`, **or** `0x0000c2c3` is not
`e8 f8 e9 ff ff`, **or** `0x0000c2db` is not `c2 04 00`, **or**
body SHA-256 is not `0af70509…0ade`, **or**
`tools/call_xref_scan.py` on `0x0040c180` is not empty, **or**
`0x001d89c4` is not `80 c1 40 00`, **or** a second encoding of
that imm exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `0af70509…0ade`. `call_xref_scan` still empty.
File `0x001d89c4` still `80 c1 40 00`. Did not open Ghidra. Did
not edit `rebuild/**`.

Retail entity: `CBattleEngine` vtable event dispatcher, including
the scheduled CalcUnitOverCrossHair refresh. Stuart architecture
(not proof): `BattleEngine.cpp:2665-2710`.

Nearest reconstruction owner: **none**. Core has no BattleEngine
event switch and no `+0x260` morph writes.

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement this dispatcher from this
mapping until that lane names the arm.

Siblings: `CBattleEngine__CalcUnitOverCrossHair` in this folder.
Next named: `CBattleEngine__HandleAutoAim` `0x0040b6d0`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040c180` | `CBattleEngine__HandleEvent` | `81ec00010000 56 8bf1 … 0fbf4104 … c7866002000003000000 … e8f8e9ffff … c20400` (350 B) | incoming-ECX thiscall; ret 0x4; 350 B; 9 E8 / 0 E9; 0 inbound; unique vtable dword `0x005d89c4`. HIGH on ABI, event word `[arg+4]`, `0x1770`/`0x1771` `+0x260` writes, CalcUnitOverCrossHair site. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on `0xfa2` name or rebuild parity. |
