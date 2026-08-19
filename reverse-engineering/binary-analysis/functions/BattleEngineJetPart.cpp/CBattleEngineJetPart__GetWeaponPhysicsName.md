# CBattleEngineJetPart__GetWeaponPhysicsName

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineJetPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
103 follow-up accepted overheat parent/jet `4013d039` /
`63c63909` — not redone. This wake already landed Walker/parent
GetWeaponPhysicsName `cc23fee4` / `bc2a0601` — not independently
accepted this cycle. Envelope. Did not mill FUN_*. Did not invent
field names. Did not invent a Core owner.

> Address: `0x00412480`

## Contract

Incoming-ECX `thiscall`. First insn `mov eax, [ecx]`. Live `ecx`
is this. Two bare `ret` (`0x004124b8`, `0x004124c6`). Body
`0x00412480`–`0x004124c6` is 71 bytes, SHA-256
`d2679c6c390a7721f05a5a58cd35e57423a1572a27f4d25b1058c533ec2a6ada`.
Capstone: 34 insns, zero `E8`, zero `E9`.

Pinned body:

1. Counted list walk on `[ecx]` / `[ecx+8]` until the index
   matches `[ecx+0x10]`. Same shape JetPart IsEnergyWeapon
   already counts. Empty / miss returns EAX=0.
2. Else EAX = `[[eax+0xa4]]`. That slot is **not** named here.

One inbound `.text` `E8`/`E9`: `JMP` at `0x0040c58a` inside
already-pinned `CBattleEngine__GetWeaponPhysicsName` `0x0040c570`.
Zero encodings of imm `80 24 41 00` in the image (not a vtable
slot).

Source architecture (not proof):
`CBattleEngineJetPart::GetWeaponPhysicsName`
`BattleEngineJetPart.cpp:909-915`. Retail inlines the list walk
instead of `E8` GetCurrentWeapon. Bare `ret` matches zero stack
args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00012480` is not `8b 01`, **or**
`0x000124b8` is not `c3`, **or** `0x000124c6` is not `c3`, **or**
body SHA-256 is not `d2679c6c…6ada`, **or**
`tools/call_xref_scan.py` on `0x00412480` is not exactly one
`JMP` at `0x0040c58a`, **or** any encoding of imm `80 24 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `d2679c6c…6ada`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x10]` / `[[+0xa4]]`. Did not invent a Core owner.

Retail entity: jet-part weapon physics-name query from the
already-pinned dispatcher. Stuart architecture (not proof):
`BattleEngineJetPart.cpp:909-915`.

Nearest reconstruction owner: **none added**. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngine__GetWeaponPhysicsName` /
`CBattleEngineJetPart__IsEnergyWeapon`. Next named:
`CBattleEngineWalkerPart__GetWeaponIconName` `0x00414610` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00412480` | `CBattleEngineJetPart__GetWeaponPhysicsName` | `8b01 … c3` (71 B) | incoming-ECX thiscall; bare ret ×2; 71 B; 0 E8 / 0 E9; 1 inbound JMP. HIGH on ABI, inlined list walk, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[[+0xa4]]` name or rebuild parity. |
