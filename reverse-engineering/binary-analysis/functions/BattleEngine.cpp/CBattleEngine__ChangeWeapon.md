# CBattleEngine__ChangeWeapon

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
97 accepted JetPart Move and GroundParticleEffect. This wake
landed Hit `efbf8e53`, Gravity `5f7915a1`, and Damage `9935f6a3`
— not redone. Envelope, not a 540-instruction walk. Did not mill
FUN_*. Did not implement lock sets.

> Address: `0x00409f70`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 0x100`. `edi = ecx`.
Six bare `ret` (last at `0x0040a554`). Body
`0x00409f70`–`0x0040a554` is 1509 bytes, SHA-256
`e68a2e0e14184df20e0f43aa7b1fefb388ac36cfe94f93918dd4e6e55c115abc`.
Capstone: 540 insns, 27 `E8`, 5 `E9`, 11 unique rel32 targets.
The five `E9`s are intra-body to `0x0040a265` and are not named.
Neighbour table `CBattleEngine__VFunc_101_0040a560` then already-
pinned Morph are not rewritten. Preceding Zoom tables are not
rewritten.

Pinned prologue, with `edi = ecx`:

1. `cmp [edi+0x260], 3` (same JET polarity Init already pins).
   JET loads `[edi+0x57c]` / `E8` table
   `LinkedObjectList__CountFlag9C` `0x004129a0`. Non-jet loads
   `[edi+0x578]` / `E8` table
   `CGeneralVolume__CountEnabledEntriesIncludingPrimary`
   `0x00414b70`. Those table names are **not** adopted as
   `CountWeapons`. EAX<=1 jumps to the last epilogue.
2. Store 0 at `[edi+0x588]`. `cmp eax, 2` (WALKER) then `E8`
   `CBattleEngineWalkerPart__ChangeWeapon` `0x00413eb0` or
   `E8` `CBattleEngineJetPart__ChangeWeapon` `0x00411e70`.
3. Counted, not contracted: ten `E8` `sprintf` `0x0055de9b`;
   four `E8` `CSoundManager__GetEffectByName` `0x004e1910`;
   four `E8` `CSoundManager__PlayEffect` `0x004e1940`; three
   `E8` `CBattleEngine__PlayHudSampleByName` `0x0040d5f0`.
   Other of the 11 targets are counted, not contracted.

One inbound `.text` `E8`/`E9`: `CALL` at `0x004d32db` inside
table `CPlayer__ReceiveButtonAction` (same owner Morph already
pins). Zero encodings of imm `70 9f 40 00` in the image (not a
vtable slot).

Source architecture (not proof): `CBattleEngine::ChangeWeapon`
`BattleEngine.cpp:1973+`. Retail bare `ret` matches zero stack
args. The `+0x260` jet/walker part dispatch matches source
`GetState()` / part `ChangeWeapon()`.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00009f70` is not `81 ec 00 01 00 00`,
**or** `0x00009f7a` is not `8b f9`, **or** `0x00009f7c` is not
`83 bf 60 02 00 00 03`, **or** `0x0000a554` is not `c3`, **or**
body SHA-256 is not `e68a2e0e…5abc`, **or**
`tools/call_xref_scan.py` on `0x00409f70` is not exactly one
`CALL` at `0x004d32db`, **or** a second `.text` `E8`/`E9` to
this entry exists, **or** any encoding of imm `70 9f 40 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `e68a2e0e…5abc`. `call_xref_scan` still one
`CALL` at `0x004d32db`. Did not open Ghidra. Did not edit
`rebuild/**`. Did not walk all 27 callees. Did not name
`[+0x588]`.

Retail entity: player ChangeWeapon request from
`CPlayer__ReceiveButtonAction`. Stuart architecture (not
proof): `BattleEngine.cpp:1973+`.

Nearest reconstruction owner: **none**. Existing
`RetailWeaponSelection` cites walker `ChangeWeapon` source, not
this retail dispatcher. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement from this mapping until
that lane names the arm.

Siblings: `CBattleEngine__Morph` / `CBattleEngine__Init` in this
folder. Next named: `CBattleEngine__ZoomIn` `0x00409ec0`
(named; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00409f70` | `CBattleEngine__ChangeWeapon` | `81ec00010000 8bf9 83bf6002000003 … c3` (1509 B) | incoming-ECX thiscall; bare ret ×6; 1509 B; 27 E8 / 5 E9 / 11 targets; 1 inbound Player. HIGH on ABI, `[+0x260]==3` part dispatch, unique inbound. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on HUD/sound names or rebuild parity. |
