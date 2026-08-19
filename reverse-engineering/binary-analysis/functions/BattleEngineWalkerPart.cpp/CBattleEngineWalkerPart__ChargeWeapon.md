# CBattleEngineWalkerPart__ChargeWeapon

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
99 accepted through WalkerPart ChangeWeapon `addcaf8d` — not
redone. This tree already has JetPart ChangeWeapon `4956cc53`,
GetCurrentWeapon `2e7141cb`, FireWeapon `5bfbe947`, and the
FireWeapon next-named correction `30fc4ccb` — not redone.
Envelope. Did not mill FUN_*. Did not implement lock sets.

> Address: `0x00413cf0`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 8`. `edi = ecx`.
Four bare `ret` (`0x00413d6b`, `0x00413dd0`, `0x00413e60`,
`0x00413ea6`). Body `0x00413cf0`–`0x00413ea6` is 439 bytes,
SHA-256
`a3549b5cc91c9031465a9be5f2cc930f3a889757d37bc6423eef49d248a15ccc`.
Capstone: 137 insns, 8 `E8`, zero `E9`, 5 unique rel32 targets.
Raw `0xE8` byte count is 8 and matches the instruction count.
Neighbour table `CBattleEngineWalkerPart__ChangeWeapon` starts at
`0x00413eb0` after a 9-byte `nop` pad and is not rewritten.

Pinned body, with `edi = ecx`:

1. `E8` already-pinned
   `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`.
   EAX==0 or `[eax+0x9c]==0` returns. Same `[+0x9c]` gate
   FireWeapon already counts. **Not** named here.
2. `E8` `TargetProfileContext__CanProceedByTargetRangeGate`
   `0x0050a080`. That table name is counted, not contracted.
   EAX==0 returns.
3. `ebx = [esi+0xa4]` then a 5-dword walk from `[ebx+0x10]`
   looking for `!= -1`. All `-1` takes the FireWeapon-shaped
   path: `[edx+0x588]=0` where `edx=[edi+0x20]`, GetCurrentWeapon,
   `E8` `ProjectileBurst__SpawnFromPercentBucketFallback`
   `0x00506010`. Same `[+0x588]` slot FireWeapon already writes.
   Those slots are **not** named here. The ProjectileBurst table
   name is counted, not contracted.
4. Else a store/heat/overheat walk on already-counted `[+0x20]`.
   `fcomp` 0.0f at `0x005d856c`. `E8`
   `CWeapon__AdvanceChargeProgressIfAnySlotAssigned` `0x005068f0`
   counted, not contracted. `[edi+0x14]=0`. `E8` already-named
   neighbour `CEngine__ClampBurstStartTimeFloorNow` `0x0040f110`
   counted; that existing note is not rewritten. FireWeapon-shaped
   tail: GetCurrentWeapon then ProjectileBurst.

One inbound `.text` `E8`/`E9`: `JMP` at `0x00409f01`. That site
is the already-settled `[ecx+0x260]==2` arm loading
`[ecx+0x578]` (walker part). Zero encodings of imm
`f0 3c 41 00` in the image (not a vtable slot). The current
table name of the 39-byte parent at `0x00409ef0` is not
rewritten here.

Source architecture (not proof):
`CBattleEngineWalkerPart::ChargeWeapon`
`BattleEngineWalkerPart.cpp:519-559`. Retail bare `ret` matches
zero stack args. Source `FireWeapon()` on `!CanCharge` and on
overheat matches the two ProjectileBurst tails. Do **not** equate
source `ReadyToCharge` / `CanCharge` / `Charge` /
`WeaponOverheated` to the three unpinned `E8` targets.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00013cf0` is not `83 ec 08`, **or**
`0x00013cf7` is not `8b f9`, **or** `0x00013cf9` is not
`e8 32 03 00 00`, **or** `0x00013d40` is not
`c7 82 88 05 00 00 00 00 00 00`, **or** `0x00013ea6` is not
`c3`, **or** body SHA-256 is not `a3549b5c…5ccc`, **or**
`tools/call_xref_scan.py` on `0x00413cf0` is not exactly one
`JMP` at `0x00409f01`, **or** any encoding of imm `f0 3c 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `a3549b5c…5ccc`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x588]` / `[+0x9c]` / `[+0xa4]` / `[+0x14]`. Did not walk
ProjectileBurst. Did not equate the three unpinned `E8` targets
to source method names.

Retail entity: walker-part ChargeWeapon from the
`[+0x260]==2` / `[+0x578]` dispatcher JMP. Stuart architecture
(not proof): `BattleEngineWalkerPart.cpp:519-559`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__FireWeapon` /
`CBattleEngineWalkerPart__GetCurrentWeapon` /
`CBattleEngineWalkerPart__ChangeWeapon`. Next named:
`CBattleEngineWalkerPart__WeaponFired` `0x004140d0` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00413cf0` | `CBattleEngineWalkerPart__ChargeWeapon` | `83ec08 8bf9 e832030000 … c3` (439 B) | incoming-ECX thiscall; bare ret ×4; 439 B; 8 E8 / 0 E9 / 5 targets; 1 inbound JMP. HIGH on ABI, GetCurrentWeapon, `[+0x9c]` gate, two ProjectileBurst tails, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on unpinned E8 identities or rebuild parity. |
