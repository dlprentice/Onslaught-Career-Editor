# CBattleEngineWalkerPart__GetWeaponAmmoPercentage

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
redone. This wake already landed CanWeaponFire `75097a38` — not
redone. Envelope. Did not mill FUN_*. Did not implement lock
sets. Did not invent field names.

> Address: `0x00414410`

## Contract

Incoming-ECX `thiscall`. First insn `push ecx`. `esi = ecx`.
Two bare `ret` (`0x00414465`, `0x0041446c`). Body
`0x00414410`–`0x0041446c` is 93 bytes, SHA-256
`0d8a7529d73827363f345a5066367f38c6655e32e96b7f3eb04866349e7eadc7`.
Capstone: 28 insns, 1 `E8`, zero `E9`, 1 unique rel32 target.
Raw `0xE8` byte count is 1 and matches the instruction count.

Pinned body, with `esi = ecx`:

1. Stack slot `[esp+4]` is written 0. `E8` already-pinned
   `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`.
   EAX==0 loads that 0 and returns ST(0).
2. Else `[eax+0xa4]` / already-counted `[esi+0x20]` walk.
   One `fdiv` then `fcom` 1.0f at `0x005d8568`. Above 1.0f
   replaces ST(0) with 1.0f. Those slots are **not** named
   here.

One inbound `.text` `E8`/`E9`: `CALL` at `0x0040c43f` inside
already-named `CBattleEngine__GetWeaponAmmoPercentage`
`0x0040c3c0`. Zero encodings of imm `10 44 41 00` in the image
(not a vtable slot). The parent table name is counted, not
rewritten.

Source architecture (not proof):
`CBattleEngineWalkerPart::GetWeaponAmmoPercentage`
`BattleEngineWalkerPart.cpp:826-844`. Retail has one `fdiv`
for both source casts. Bare `ret` matches zero stack args.
ST(0) is the returned float.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00014410` is not `51`, **or**
`0x00014412` is not `8b f1`, **or** `0x0001441c` is not
`e8 0f fc ff ff`, **or** `0x0001446c` is not `c3`, **or** body
SHA-256 is not `0d8a7529…adc7`, **or**
`tools/call_xref_scan.py` on `0x00414410` is not exactly one
`CALL` at `0x0040c43f`, **or** any encoding of imm `10 44 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `0d8a7529…adc7`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
store slots. Did not invent a Core owner.

Retail entity: walker-part ammo-percentage query. Stuart
architecture (not proof): `BattleEngineWalkerPart.cpp:826-844`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__GetWeaponCharge` /
`CBattleEngineWalkerPart__CanWeaponFire`. Next named:
`CBattleEngine__GetWeaponAmmoPercentage` `0x0040c3c0` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00414410` | `CBattleEngineWalkerPart__GetWeaponAmmoPercentage` | `51 8bf1 e80ffcffff … c3` (93 B) | incoming-ECX thiscall; bare ret ×2; 93 B; 1 E8 / 0 E9 / 1 target; 1 inbound CALL. HIGH on ABI, GetCurrentWeapon, 1.0f clamp, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on store-slot names or rebuild parity. |
