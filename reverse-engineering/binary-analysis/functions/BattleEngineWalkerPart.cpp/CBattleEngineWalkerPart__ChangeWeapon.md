# CBattleEngineWalkerPart__ChangeWeapon

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
98 accepted Hit and Gravity — not redone. This wake landed the
zoom trio and AutoZoomOut `f75aa0b4` — not redone. Envelope, not
a 121-instruction walk. Did not mill FUN_*. Did not implement
lock sets.

> Address: `0x00413eb0`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 8`. `esi = ecx`.
Two bare `ret` (`0x00413f7f`, `0x00414004`). Body
`0x00413eb0`–`0x00414004` is 341 bytes, SHA-256
`e70345e80967dbcd41b004a730698345015b2ebb5b31603d34ba1e2fae0a9024`.
Capstone: 121 insns, 4 `E8`, zero `E9`, 2 unique rel32 targets.
Raw `0xE8` byte count is 5 and is not the instruction count.
Neighbour table `CBattleEngineWalkerPart__GetCurrentWeapon`
starts at `0x00414030` and is not rewritten.

Pinned prologue, with `esi = ecx`:

1. `E8` `CBattleEngineWalkerPart__GetCurrentWeapon`
   `0x00414030` (same target WalkerPart Move already counts).
   Then `eax = [eax+0xa4]` / `[eax+0x34]` (zoom-mode word
   ZoomIn already tests). **Not** named here.
2. `ebx = [esi+0x10]` then `inc ebx`. That slot is **not**
   named here.
3. Counted list walk on `[esi]` / `[esi+8]`. Three more `E8`
   GetCurrentWeapon. Tail `E8` already-pinned
   `CBattleEngine__AutoZoomOut` `0x00409e80` at `0x00413ff9`.

Three inbound `.text` `E8`/`E9`: `CALL` at `0x00409fc1` inside
already-pinned `CBattleEngine__ChangeWeapon`; `CALL` at
`0x00414aab` and `0x00414b1c`. Zero encodings of imm
`b0 3e 41 00` in the image (not a vtable slot).

Source architecture (not proof):
`CBattleEngineWalkerPart::ChangeWeapon`
`BattleEngineWalkerPart.cpp:562-599`. Retail bare `ret` matches
zero stack args. Source `AutoZoomOut()` matches the tail E8.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00013eb0` is not `83 ec 08`, **or**
`0x00013eb6` is not `8b f1`, **or** `0x00013eb8` is not
`e8 73 01 00 00`, **or** `0x00013ff9` is not
`e8 82 5e ff ff`, **or** `0x00014004` is not `c3`, **or** body
SHA-256 is not `e70345e8…9024`, **or**
`tools/call_xref_scan.py` on `0x00413eb0` is not exactly those
three `CALL`s, **or** a fourth `.text` `E8`/`E9` to this entry
exists, **or** any encoding of imm `b0 3e 41 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `e70345e8…9024`. `call_xref_scan` still three
sites. Did not open Ghidra. Did not edit `rebuild/**`. Did not
walk the list. Did not name `[+0x10]`.

Retail entity: walker-part ChangeWeapon from the already-pinned
BattleEngine ChangeWeapon dispatcher. Stuart architecture (not
proof): `BattleEngineWalkerPart.cpp:562-599`.

Nearest reconstruction owner: existing `RetailWeaponSelection`
cites this source file, not this PE body. Not a new owner. L100
card `t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__Move` /
`CBattleEngine__ChangeWeapon` / `CBattleEngine__AutoZoomOut`.
Next named: `CBattleEngineJetPart__ChangeWeapon` `0x00411e70`
(the jet sibling; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00413eb0` | `CBattleEngineWalkerPart__ChangeWeapon` | `83ec08 8bf1 e873010000 … e8825effff … c3` (341 B) | incoming-ECX thiscall; bare ret ×2; 341 B; 4 E8 / 0 E9 / 2 targets; 3 inbound. HIGH on ABI, GetCurrentWeapon, AutoZoomOut tail. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x10]` name or rebuild parity. |
