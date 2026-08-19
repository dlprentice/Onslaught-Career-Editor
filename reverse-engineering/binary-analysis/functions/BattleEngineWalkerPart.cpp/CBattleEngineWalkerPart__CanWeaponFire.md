# CBattleEngineWalkerPart__CanWeaponFire

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
raised. Envelope only. Did not mill FUN_*. Did not implement
lock sets. Did not edit `rebuild/**`.

> Address: `0x00414630`

## Contract

Incoming-ECX `thiscall`. First insn `push esi`. `esi = ecx`.
Three bare `ret` (`0x00414689`, `0x004146a4`, `0x004146a8`). Body
`0x00414630`–`0x004146a8` is 121 bytes, SHA-256
`32e7211754b16a53331446a4e944518f50e1dacfd5a3846ca572a5db32dff029`.
Capstone: 37 insns, 1 `E8`, zero `E9`, 1 unique rel32 target.
Raw `0xE8` byte count is 1 and matches the instruction count.

Pinned body, with `esi = ecx`:

1. `E8` already-pinned
   `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`.
   EAX==0 returns EAX=0.
2. `[eax+0x9c]==0` returns EAX=0. Same `[+0x9c]` gate FireWeapon
   already counts. **Not** named here.
3. Store/heat/overheat walk on already-counted `[esi+0x20]`.
   `fcomp` 0.0f at `0x005d856c`. EAX=1 on the two success `ret`s.
   Those slots are **not** named here.

One inbound `.text` `E8`/`E9`: `CALL` at `0x004065db` inside
already-pinned `CBattleEngine__HandleLocks` `0x00406560`. Zero
encodings of imm `30 46 41 00` in the image (not a vtable slot).

Source architecture (not proof):
`CBattleEngineWalkerPart::CanWeaponFire`
`BattleEngineWalkerPart.cpp:936-961`. Retail `[+0x9c]` sits
where source has `IsActive()`. Bare `ret` matches zero stack
args.

Rebuild mapping: existing `REBUILD_READY` **not raised**. This
note is a PE envelope only. Do not implement Core from this RE
root.

Cheapest falsifier: file `0x00014630` is not `56`, **or**
`0x00014631` is not `8b f1`, **or** `0x00014633` is not
`e8 f8 f9 ff ff`, **or** `0x0001463c` is not
`8b 88 9c 00 00 00`, **or** `0x000146a8` is not `c3`, **or**
body SHA-256 is not `32e72117…f029`, **or**
`tools/call_xref_scan.py` on `0x00414630` is not exactly one
`CALL` at `0x004065db`, **or** any encoding of imm `30 46 41 00`
exists.

## Rebuild mapping — 2026-08-19

Existing campaign grade `REBUILD_READY` is **not raised**.
Independently re-read official+twin `74154bfa` this wake
(2506752 equal). Body SHA-256 still `32e72117…f029`.
`0x0001463c` still `8b889c000000`. `call_xref_scan` still one
CALL. Did not open Ghidra. Did not edit `rebuild/**`. Did not
name `[+0x9c]` / store slots. Did not invent a Core owner.

Retail entity: walker-part CanWeaponFire from already-pinned
HandleLocks. Stuart architecture (not proof):
`BattleEngineWalkerPart.cpp:936-961`.

Nearest reconstruction owner: **none added**. Existing
`REBUILD_READY` mapping is not rewritten. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngineJetPart__CanWeaponFire` `17312e7a`
(already on main this wake, not redone) /
`CBattleEngineWalkerPart__GetCurrentWeapon`. Next named:
`CBattleEngineWalkerPart__GetWeaponAmmoPercentage` `0x00414410`
(no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00414630` | `CBattleEngineWalkerPart__CanWeaponFire` | `56 8bf1 e8f8f9ffff 8b889c000000 … c3` (121 B) | incoming-ECX thiscall; bare ret ×3; 121 B; 1 E8 / 0 E9 / 1 target; 1 inbound CALL. HIGH on ABI, GetCurrentWeapon, `[+0x9c]` gate, unique inbound. Existing `REBUILD_READY` **not raised**. **Not** on store-slot names or a new Core owner. |
