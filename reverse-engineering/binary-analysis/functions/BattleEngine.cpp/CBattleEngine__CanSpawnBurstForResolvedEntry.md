# CBattleEngine__CanSpawnBurstForResolvedEntry

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. This
wake already landed ChargeWeapon `9bde6c3a` and WeaponFired
`384e45cb` — not redone. Envelope. Did not mill FUN_*. Did not
implement lock sets. Did not rewrite the current table name.

> Address: `0x0040c2e0`

## Contract

Incoming-ECX `thiscall`. First insn `push esi`. `esi = ecx`.
Three `ret 4` (`0x0040c309`, `0x0040c32d`, `0x0040c334`). Body
`0x0040c2e0`–`0x0040c336` is 87 bytes, SHA-256
`3d755ee793a412419c9ffcabe94a88d88d6c75513af315c229b5a9d7f23b3d82`.
Capstone: 28 insns, 2 `E8`, zero `E9`, 2 unique rel32 targets.
Raw `0xE8` byte count is 2 and matches the instruction count.
Neighbour table `CBattleEngine__HandleEvent` ends at
`0x0040c2dd` and is not rewritten.

Pinned body, with `esi = ecx`:

1. `edi = [esp+0xc]` after the two pushes — the one stack
   argument. `ret 4` matches that one dword.
2. `ecx = [esi+0x57c]` / `E8` table-named
   `CBattleEngineJetPart__WeaponFired` `0x00412050`. That table
   name is counted, not contracted. EAX!=0 writes `[esi+0x5d8]=0`
   and returns 1. `[+0x57c]` is the already-settled jet-part
   slot. `[+0x5d8]` is **not** named here.
3. Else `ecx = [esi+0x578]` / `E8` already-pinned
   `CBattleEngineWalkerPart__WeaponFired` `0x004140d0`. EAX!=0
   writes `[esi+0x5d8]=0` and returns 1. Else returns 0.

One inbound `.text` `E8`/`E9`: `CALL` at `0x00506a1f` inside
already-named `ProjectileBurst__SpawnFromCurrentPreset`
`0x005069f0`. Zero encodings of imm `e0 c2 40 00` in the image
(not a vtable slot). The inbound parent is counted, not
rewritten.

Source architecture (not proof): `CBattleEngine::WeaponFired`
`BattleEngine.cpp:2713-2729` is the same jet-then-walker shape
with a stealth-clear on success. This note keeps the current
table name. Do **not** treat the table name as a recovered
source symbol.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000c2e0` is not `56`, **or**
`0x0000c2e6` is not `8b f1`, **or** `0x0000c2ef` is not
`e8 5c 5d 00 00`, **or** `0x0000c313` is not
`e8 b8 7d 00 00`, **or** `0x0000c334` is not `c2 04 00`, **or**
body SHA-256 is not `3d755ee7…3d82`, **or**
`tools/call_xref_scan.py` on `0x0040c2e0` is not exactly one
`CALL` at `0x00506a1f`, **or** any encoding of imm `e0 c2 40 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `3d755ee7…3d82`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x5d8]`. Did not promote a rename.

Retail entity: BattleEngine jet-then-walker WeaponFired
dispatcher, currently table-named CanSpawnBurst. Stuart
architecture (not proof): `BattleEngine.cpp:2713-2729`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__WeaponFired` /
`CBattleEngine__HandleEvent`. Next named:
`CBattleEngineJetPart__WeaponFired` `0x00412050` (no 2026-08-19
PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040c2e0` | `CBattleEngine__CanSpawnBurstForResolvedEntry` | `56 8bf1 e85c5d0000 … e8b87d0000 … c20400` (87 B) | incoming-ECX thiscall; ret-4 ×3; 87 B; 2 E8 / 0 E9 / 2 targets; 1 inbound CALL. HIGH on ABI, jet-then-walker part dispatch, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on table-name recovery or rebuild parity. |
