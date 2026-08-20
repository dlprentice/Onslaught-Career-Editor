# CBattleEngineJetPart__GetCurrentWeaponNameField04

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineJetPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
104 accepted through parent GetWeaponPhysicsName `bc2a0601` —
not redone. This wake independently accepted `dcfd613e` /
`a85fbe48` / `539cceea` / `57f4d0ff`. Envelope. Did not mill
FUN_*. Did not invent field names. Did not rename this table
name. Did not invent a Core owner.

> Address: `0x004124d0`

## Contract

Incoming-ECX `thiscall`. First insn `mov eax, [ecx]`. Live `ecx`
is this. Two bare `ret` (`0x00412508`, `0x00412517`). Body
`0x004124d0`–`0x00412517` is 72 bytes, SHA-256
`2d8da83fe0ac62923da64e3ab3d4812ed40378622d05cfd6fc344f5dc693fa20`.
Capstone: 34 insns, zero `E8`, zero `E9`.

Pinned body:

1. Counted list walk on `[ecx]` / `[ecx+8]` until the index
   matches `[ecx+0x10]`. Same shape JetPart GetWeaponIconName
   already counts. Empty / miss returns EAX=0.
2. Else EAX = `[[eax+0xa4]+4]`. That slot is **not** named here.
   Do **not** equate it to source `CWeapon::GetName` (physics
   name already returns `[[+0xa4]+0]`).

One inbound `.text` `E8`/`E9`: `CALL` at `0x0040a001` inside
already-pinned `CBattleEngine__ChangeWeapon` `0x00409f70`. Zero
encodings of imm `d0 24 41 00` in the image (not a vtable slot).
The inbound parent is counted, not rewritten.

Source architecture (not proof): no matching
`CBattleEngineJetPart` method of this name. ChangeWeapon
(`BattleEngine.cpp` ChangeWeapon) consumes the returned pointer
as a `char *` next to walker `0x004145f0`. That walker table
name is counted, not rewritten.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x000124d0` is not `8b 01`, **or**
`0x00012508` is not `c3`, **or** `0x00012517` is not `c3`, **or**
body SHA-256 is not `2d8da83f…fa20`, **or**
`tools/call_xref_scan.py` on `0x004124d0` is not exactly one
`CALL` at `0x0040a001`, **or** any encoding of imm `d0 24 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `2d8da83f…fa20`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x10]` / `[+4]`. Did not rename `0x004145f0`. Did not invent
a Core owner.

Retail entity: jet-part current-weapon `+4` pointer query used
by ChangeWeapon. No matching Stuart method on this class.

Nearest reconstruction owner: **none added**. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngineJetPart__GetWeaponIconName` /
`CBattleEngine__ChangeWeapon`. Next named:
`CBattleEngineWalkerPart__GetCurrentWeaponZoomMode` `0x004145f0`
(no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004124d0` | `CBattleEngineJetPart__GetCurrentWeaponNameField04` | `8b01 … 8b4104 c3` (72 B) | incoming-ECX thiscall; bare ret ×2; 72 B; 0 E8 / 0 E9; 1 inbound CALL. HIGH on ABI, inlined list walk, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+4]` name, walker rename, or rebuild parity. |
