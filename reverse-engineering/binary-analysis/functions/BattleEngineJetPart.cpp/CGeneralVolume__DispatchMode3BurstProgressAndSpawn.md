# CGeneralVolume__DispatchMode3BurstProgressAndSpawn

Status: active static function note
Last updated: 2026-08-19
Source File: none under this table name | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
108 reviewer independently accepted range-gate `d883e317` — this
wake independently re-read official+twin; 35 B sha `1ba024f1`
— not redone. Envelope. Did not mill FUN_*. Did not mill Get*.
Did not rewrite this table name. Did not equate source
`CBattleEngineJetPart::ChargeWeapon` or `ReadyToCharge`. Did not
invent a Core owner.

> Address: `0x00411bf0`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 8`. `esi = ecx`.
Seven bare `ret` (`0x00411c48`, `0x00411d13`, `0x00411da6`,
`0x00411dfe`, `0x00411e1b`, `0x00411e4c`, `0x00411e67`). Body
`0x00411bf0`–`0x00411e67` is 632 bytes, SHA-256
`be371dff2cca9e4c9d01ce0ea949c0bf5d927fbf8f6b7d583c097cccd83a0ddd`.
Capstone: 222 insns, 6 `E8`, 1 `E9`, 5 unique `E8` rel32
targets. Raw `0xE8` byte count is 6 and matches the instruction
count. The one `E9` at `0x00411ca6` lands at `0x00411e1e` inside
this body. Neighbour table
`CBattleEngineJetPart__ChangeWeapon` starts at `0x00411e70`
after an 8-byte `nop` pad and is not rewritten.

Pinned body, with `esi = ecx`:

1. Inlined current-weapon list walk on `[esi]` / `[esi+8]` /
   `[esi+0x10]`. EAX==0 jumps to the shared epilogue at
   `0x00411e60`. Those slots are **not** named here.
2. After the walk match: `[edi+0x9c]==0` returns. Same
   `[+0x9c]` gate walker ChargeWeapon / FireWeapon already
   count. **Not** named here.
3. `E8` already-pinned
   `TargetProfileContext__CanProceedByTargetRangeGate`
   `0x0050a080` at `0x00411c61`. EAX==0 returns. That table
   name stays counted, not equated to source `ReadyToCharge`.
4. `ebx = [edi+0xa4]` then a 5-dword walk from `[ebx+0x10]`
   looking for `!= -1`. All `-1` takes the FireWeapon-shaped
   path: `[[esi+0x18]+0x588]=0`. Same `[+0x588]` slot walker
   ChargeWeapon already writes. Those slots are **not** named
   here.
5. `fcomp` 0.0f at `0x005d856c`. `E8`
   `CWeapon__AdvanceChargeProgressIfAnySlotAssigned`
   `0x005068f0` counted, not contracted. `E8` already-named
   neighbour `CEngine__ClampBurstStartTimeFloorNow`
   `0x0040f110` counted. `E8` `CSPtrSet__First` `0x00406d20`
   counted. Two `E8`
   `ProjectileBurst__SpawnFromPercentBucketFallback`
   `0x00506010` counted, not contracted.

One inbound `.text` `E8`/`E9`: `JMP` at `0x00409f11`. That site
is the already-settled `[ecx+0x260]==3` arm loading
`[ecx+0x57c]` (jet part). Zero encodings of imm
`f0 1b 41 00` in the image (not a vtable slot). The current
table name of the 39-byte parent at `0x00409ef0` is not
rewritten here.

Source architecture (not proof):
`CBattleEngineJetPart::ChargeWeapon`
`BattleEngineJetPart.cpp:659-698`. Retail bare `ret` matches
zero stack args. Do **not** equate this table name to that
method. Historical `HYP__CBattleEngineJetPart__ChargeWeapon`
is a lead, not a rename.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00011bf0` is not `83 ec 08`, **or**
`0x00011bf6` is not `8b f1`, **or** `0x00011c61` is not
`e8 1a 84 0f 00`, **or** `0x00011c91` is not
`89 90 88 05 00 00`, **or** `0x00011e67` is not `c3`, **or**
body SHA-256 is not `be371dff…0ddd`, **or**
`tools/call_xref_scan.py` on `0x00411bf0` is not exactly one
`JMP` at `0x00409f11`, **or** any encoding of imm `f0 1b 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `be371dff…0ddd`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x588]` / `[+0x9c]` / `[+0xa4]` / `[+0x10]`. Did not walk
ProjectileBurst. Did not equate this table name to source
`ChargeWeapon` / `ReadyToCharge`.

Retail entity: jet-part ChargeWeapon-shaped body from the
`[+0x260]==3` / `[+0x57c]` dispatcher JMP. Stuart architecture
(not proof): `BattleEngineJetPart.cpp:659-698`.

Nearest reconstruction owners (already exist; **none added**):

1. Increment arm: `RetailWeaponCharge.Charge` via
   `Level100PlayerWeaponRuntime.AdvanceCharge` is the
   already-counted `E8` `0x005068f0` owner from the walker
   ChargeWeapon map. ReadyToCharge `0x0050A080` stays named
   open in `Level100PulseCannonCharge.cs`. Do **not**
   implement it from this envelope.
2. Fire gate: `RetailWeaponFireGate.CanWalkerWeaponFire` is
   the walker CanWeaponFire owner, not this body.
3. Lock HUD: **none**.

Do not implement from this RE root. L100 playable-training
diet — comment only until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__ChargeWeapon` /
`TargetProfileContext__CanProceedByTargetRangeGate` /
`CBattleEngineJetPart__ChangeWeapon`. Next named:
`CGeneralVolume__DispatchSelectedBurstPreset` `0x00411b90`
(table name counted; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00411bf0` | `CGeneralVolume__DispatchMode3BurstProgressAndSpawn` | `83ec08 5355568bf1 … 5f5e5d5b83c408c3` (632 B) | incoming-ECX thiscall; bare ret ×7; 632 B; 6 E8 / 1 E9 / 5 unique E8; 1 inbound JMP. HIGH on ABI, range-gate E8, `[+0x9c]` gate, two ProjectileBurst tails, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on table rename, ReadyToCharge, or rebuild parity. |
