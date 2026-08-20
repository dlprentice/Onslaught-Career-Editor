# CBattleEngineJetPart__GetWeaponIconName

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
`a85fbe48` and already landed parent GetWeaponIconName
`539cceea`. Envelope. Did not mill FUN_*. Did not invent field
names. Did not invent a Core owner.

> Address: `0x00412520`

## Contract

Incoming-ECX `thiscall`. First insn `mov eax, [ecx]`. Live `ecx`
is this. Two bare `ret` (`0x00412558`, `0x00412567`). Body
`0x00412520`–`0x00412567` is 72 bytes, SHA-256
`3053b7d98d38fd9a580dc128da23cf05caf962d611b61a7653ad9212987c6ca6`.
Capstone: 34 insns, zero `E8`, zero `E9`.

Pinned body:

1. Counted list walk on `[ecx]` / `[ecx+8]` until the index
   matches `[ecx+0x10]`. Same shape JetPart GetWeaponPhysicsName
   already counts. Empty / miss returns EAX=0.
2. Else EAX = `[[eax+0xa4]+0x38]`. That slot is **not** named
   here.

One inbound `.text` `E8`/`E9`: `JMP` at `0x0040c5aa` inside
already-pinned `CBattleEngine__GetWeaponIconName` `0x0040c590`.
Zero encodings of imm `20 25 41 00` in the image (not a vtable
slot).

Source architecture (not proof):
`CBattleEngineJetPart::GetWeaponIconName`
`BattleEngineJetPart.cpp:918-924`. Retail inlines the list walk
instead of `E8` GetCurrentWeapon. Bare `ret` matches zero stack
args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00012520` is not `8b 01`, **or**
`0x00012558` is not `c3`, **or** `0x00012567` is not `c3`, **or**
body SHA-256 is not `3053b7d9…6ca6`, **or**
`tools/call_xref_scan.py` on `0x00412520` is not exactly one
`JMP` at `0x0040c5aa`, **or** any encoding of imm `20 25 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `3053b7d9…6ca6`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x10]` / `[+0x38]`. Did not invent a Core owner.

Retail entity: jet-part weapon icon-name query from the
already-pinned dispatcher. Stuart architecture (not proof):
`BattleEngineJetPart.cpp:918-924`.

Nearest reconstruction owner: **none added**. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngine__GetWeaponIconName` /
`CBattleEngineJetPart__GetWeaponPhysicsName`. Next named:
`CBattleEngineJetPart__GetCurrentWeaponNameField04` `0x004124d0`
(no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00412520` | `CBattleEngineJetPart__GetWeaponIconName` | `8b01 … 8b4138 c3` (72 B) | incoming-ECX thiscall; bare ret ×2; 72 B; 0 E8 / 0 E9; 1 inbound JMP. HIGH on ABI, inlined list walk, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x38]` name or rebuild parity. |
