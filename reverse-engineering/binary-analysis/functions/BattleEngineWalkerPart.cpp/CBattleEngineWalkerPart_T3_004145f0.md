# CBattleEngineWalkerPart_T3_004145f0

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
104 accepted through parent GetWeaponPhysicsName `bc2a0601` —
not redone. This wake independently accepted `dcfd613e` /
`a85fbe48` / `539cceea` / `57f4d0ff` and already landed
`78338207`. Envelope. Did not mill FUN_*. Did not invent field
names. Did not revive the demoted ZoomMode label. Did not invent
a Core owner.

> Address: `0x004145f0`

## Contract

Incoming-ECX `thiscall`. First insn `E8` already-pinned
`CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`. Two
bare `ret` (`0x00414602`, `0x00414605`). Body
`0x004145f0`–`0x00414605` is 22 bytes, SHA-256
`2f1b7220588b07e4bf8773d559532154fba97fc66072e7e8c611976f198b70ae`.
Capstone: 8 insns, 1 `E8`, zero `E9`, 1 unique rel32 target.

Pinned body:

1. `E8` `GetCurrentWeapon` `0x00414030`. EAX==0 returns EAX=0.
2. Else `[eax+0xa4]` then EAX = `[eax+4]`. Same `+4` slot jet
   field04 already counts. That slot is **not** named here.
   Do **not** equate this body to source
   `CWeapon::GetZoomMode` (`BattleEngineWalkerPart.cpp:564`).

Current table name is the 2026-08-17 Tier-3 placeholder
`CBattleEngineWalkerPart_T3_004145f0` (demoted from
`GetCurrentWeaponZoomMode`; counted, not rewritten).

One inbound `.text` `E8`/`E9`: `CALL` at `0x00409ff4` inside
already-pinned `CBattleEngine__ChangeWeapon` `0x00409f70`. Zero
encodings of imm `f0 45 41 00` in the image (not a vtable slot).
The inbound parent is counted, not rewritten.

Source architecture (not proof): no matching method of the
current table name. Walker ChangeWeapon's `GetZoomMode()` sites
are a different call. This body is the walker `+4` sibling of
already-pinned jet field04.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x000145f0` is not `e8 3b fa ff ff`,
**or** `0x00014605` is not `c3`, **or** body SHA-256 is not
`2f1b7220…70ae`, **or** `tools/call_xref_scan.py` on
`0x004145f0` is not exactly one `CALL` at `0x00409ff4`, **or**
any encoding of imm `f0 45 41 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `2f1b7220…70ae`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+4]`. Did not revive ZoomMode. Did not invent a Core owner.

Retail entity: walker-part current-weapon `+4` pointer query
used by ChangeWeapon. Current table name is the T3 placeholder.

Nearest reconstruction owner: **none added**. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngineJetPart__GetCurrentWeaponNameField04` /
`CBattleEngineWalkerPart__GetWeaponIconName`. Next named:
`CBattleEngineJetPart__ResetConfiguration` `0x00412650` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004145f0` | `CBattleEngineWalkerPart_T3_004145f0` | `e83bfaffff … 8b4004 c3` (22 B) | incoming-ECX thiscall; bare ret ×2; 22 B; 1 E8 / 0 E9 / 1 target; 1 inbound CALL. HIGH on ABI, GetCurrentWeapon, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+4]` name, ZoomMode revival, or rebuild parity. |
