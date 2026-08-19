# CBattleEngine__FireLock

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is the 2026-08-04 target-lock promotion label, not this proof.
This wake does **not** redo `FUN_00598c85` (`8002c949`) or rewrite
`CBattleEngine__AddProjectile.md` / `CBattleEngine__HandleLocks`.
Did not adopt a C1 rename. Operator 2026-08-19 closed the unlabeled
first-gates mill for this root. Cycle 89 accepted the DisplayLock
and GetCurrentTarget byte notes. This follow-on names rebuild
owners only; it does not redo the body.

> Address: `0x00407060`

## Contract

Incoming-ECX `thiscall`. First insn `push ebx`. Three `ret 0x4`
exits (`0x004070c4`, `0x00407120`, `0x0040713c`). Body
`0x00407060`–`0x0040713e` is 223 bytes, SHA-256
`59141a0e0053ed2011e834d07badaa6c68252700e2c6adea0c30c2f7c8f8e54e`.
Four `E8`, zero `E9`. Neighbour table `CBattleEngine__LockHit`
starts at `0x00407140` and is not claimed. Preceding table
`CBattleEngine__StartLock` ends at `0x0040705a` and is not rewritten.

The body, with `ebx = [esp+8]` after the `push ebx`:

1. `test ebx, ebx` / `mov edi, ecx`. Null arg jumps to the shared
   epilogue at `0x00407139`.
2. Walk the set at `this+0x294` (`lea ecx, [edi+0x294]`). For each
   live node `esi`: `fld [esi+8]` / `fcomp dword [0x00672fd0]` /
   `fnstsw ax` / `test ah, 1`. That is CF after compare, so the
   taken path is `[esi+8] < [0x00672fd0]`. Then `cmp [esi], ebx`.
   Both true → `push esi` / `E8` `CSPtrSet__Remove` `0x004e5bd0`.
3. Walk the set at `this+0x2a4`. If some node has `[node]==ebx`,
   `ecx=esi` / `E8` `CGenericActiveReader__dtor` `0x0044b1d0` then
   `push esi` / `mov ecx, 0x009c3df0` / `E8` `CDXMemoryManager__Free`
   `0x00549220`.
4. Else `push esi` / `E8` `CSPtrSet__AddToHead` `0x004e5a80`, then
   `fld [0x00672fd0]` / `fst [esi+4]` / `fadd dword [0x005d85ec]` /
   `fstp [esi+8]`. File `0x001d85ec` is `00 00 00 3f` = `0.5f`.
   `0x00672fd0` is BSS (not in the 2,506,752-byte image); the
   campaign already closed it as `CEventManager` `mTime`.

Those field names, `ToRead`, `Add` versus `AddToHead`, and the
callee bodies are **not** this proof.

One inbound `.text` `E8`/`E9`: `CALL` at `0x005074c9` inside table
`ProjectileBurst__SpawnFromCurrentPreset` `0x005069f0`–`0x005078ab`.
The site is `push esi` / `E8` after `DisplayLock` `0x00407310`
returns nonzero and `mov ecx, [esp+0x10]`. Zero encodings of imm
`60 70 40 00` in the image.

Source architecture (not proof): `CBattleEngine::FireLock`
`references/Onslaught/BattleEngine.cpp:842-866` and inlined
`CLockInfo::Fired` at `:3153-3157` (`mStart=GetTime();
mFinish=mStart+0.5f`). `HandleLocks` does not call `FireLock`.
Retail inlines the already-fired walk and the `Fired` stores.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00007060` is not `53`, **or**
`0x0000713c` is not `c2 04 00`, **or** `0x000070c8` is not
`e8 03 eb 0d 00`, **or** `0x00007106` is not `e8 75 e9 0d 00`,
**or** `0x00007129` is not `e8 a2 40 04 00`, **or** `0x00007134`
is not `e8 e7 20 14 00`, **or** body SHA-256 is not
`59141a0e…e54e`, **or** `tools/call_xref_scan.py` on
`0x00407060` is not exactly one `CALL` at `0x005074c9`, **or**
`0x001d85ec` is not `00 00 00 3f`, **or** a second `.text`
`E8`/`E9` to this entry exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `59141a0e…e54e`. `call_xref_scan` still one `CALL`
at `0x005074c9`. Cycle 89 accepted the DisplayLock /
GetCurrentTarget byte notes. Did not open Ghidra. Did not edit
`rebuild/**`.

Retail entity: player `CBattleEngine` lock-set move at projectile
spawn, after `DisplayLock` returns nonzero. Stuart architecture
(not proof): `BattleEngine.cpp:842-866`.

Nearest reconstruction owner (absent lock-set type):
`rebuild/OnslaughtRebuild.Core/Simulation.cs` `TryFire` /
`LaunchWalkerRound` / `EmitWeaponFireEvent`. That is the player
spawn of the same `ProjectileBurst__SpawnFromCurrentPreset`
body. Core has no `+0x294` / `+0x2a4` occupancy and does not
call this function.

Not the owner: `Level100ActorWeaponRuntime.LaunchActorRound`
models that spawn for **scatter only**.
`ActorRoundState.Locked` is the round seek/homing flag, not
this transition.

Godot: none. HUD target-lock layers stay absent
(`rebuild/OnslaughtRebuild.Godot/Assets/Hud/README.md`).

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement lock sets from this
mapping until that lane names the arm.

Siblings: `CBattleEngine__DisplayLock` /
`CBattleEngine__GetCurrentTarget` in this folder.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00407060` | `CBattleEngine__FireLock` | `53 8b5c2408 5657 85db … e803eb0d00 … e875e90d00 … e8a2400400 … e8e7201400 … c20400` (223 B) | incoming-ECX thiscall; ret 0x4 ×3; 223 B; 4 E8 `CSPtrSet__Remove` + `CSPtrSet__AddToHead` + `CGenericActiveReader__dtor` + `CDXMemoryManager__Free` / 0 E9; 1 inbound `ProjectileBurst__SpawnFromCurrentPreset` `0x005074c9`. HIGH on ABI, set occupancy `+0x294`/`+0x2a4`, `0.5f` add, unique inbound. Mapping `PARTIAL_CONTRACT` onto `Simulation.TryFire`. **Not** on field names, `FiredAt` as a retail body, or rebuild parity. |
