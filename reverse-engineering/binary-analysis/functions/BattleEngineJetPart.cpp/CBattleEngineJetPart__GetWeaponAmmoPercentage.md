# CBattleEngineJetPart__GetWeaponAmmoPercentage

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineJetPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
101 accepted through JetPart GetWeaponCharge `f31bee59` — not
redone. This wake already landed the ammo-percentage walker/
dispatcher pair `d781df30` / `10e1a738` — not redone. Envelope.
Did not mill FUN_*. Did not invent field names. Did not invent a
Core owner.

> Address: `0x004121b0`

## Contract

Incoming-ECX `thiscall`. First insn `mov eax, [ecx]`. Live `ecx`
is this. Two bare `ret` (`0x004121ec`, `0x00412232`). Body
`0x004121b0`–`0x00412232` is 131 bytes, SHA-256
`c1a0d532cf0324bea38236ff36b6aa74cf188b34d51ceb904a56d90ec43340a0`.
Capstone: 47 insns, zero `E8`, zero `E9`.

Pinned body:

1. Preload 0.0f at `0x005d856c`. Counted list walk on `[ecx]` /
   `[ecx+8]` until the index matches `[ecx+0x10]`. Same shape
   JetPart GetWeaponCharge already counts. Empty / miss returns
   that 0.0f.
2. Else `[eax+0xa4]` / `[ecx+0x18]` walk, one `fdiv`, `fcom`
   1.0f at `0x005d8568`. Those slots are **not** named here.

One inbound `.text` `E8`/`E9`: `CALL` at `0x0040c44f` inside
already-pinned `CBattleEngine__GetWeaponAmmoPercentage`
`0x0040c3c0`. Zero encodings of imm `b0 21 41 00` in the image
(not a vtable slot).

Source architecture (not proof):
`CBattleEngineJetPart::GetWeaponAmmoPercentage`
`BattleEngineJetPart.cpp:826-844`. Retail inlines the list walk
instead of `E8` GetCurrentWeapon. One `fdiv` for both source
casts. Bare `ret` matches zero stack args. ST(0) is the
returned float.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x000121b0` is not `8b 01`, **or**
`0x00012232` is not `c3`, **or** body SHA-256 is not
`c1a0d532…40a0`, **or** `tools/call_xref_scan.py` on
`0x004121b0` is not exactly one `CALL` at `0x0040c44f`, **or**
any encoding of imm `b0 21 41 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `c1a0d532…40a0`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x10]` / `[+0x18]`. Did not invent a Core owner.

Retail entity: jet-part ammo-percentage query from the
already-pinned dispatcher. Stuart architecture (not proof):
`BattleEngineJetPart.cpp:826-844`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngine__GetWeaponAmmoPercentage` /
`CBattleEngineJetPart__GetWeaponCharge`. Next named:
`CBattleEngineWalkerPart__GetWeaponAmmoCount` `0x00414470` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004121b0` | `CBattleEngineJetPart__GetWeaponAmmoPercentage` | `8b01 … c3` (131 B) | incoming-ECX thiscall; bare ret ×2; 131 B; 0 E8 / 0 E9; 1 inbound CALL. HIGH on ABI, inlined list walk, 1.0f clamp, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x18]` name or rebuild parity. |
