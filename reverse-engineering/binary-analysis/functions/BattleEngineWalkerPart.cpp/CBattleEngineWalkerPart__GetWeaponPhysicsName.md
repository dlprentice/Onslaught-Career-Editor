# CBattleEngineWalkerPart__GetWeaponPhysicsName

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
103 follow-up accepted overheat parent/jet `4013d039` /
`63c63909` — not redone. Cycle 103 close: energy dispatcher
`b5df91bf` was not independently accepted that cycle. This wake
already landed GetWeaponName pair `5c5e6725` / `5b648014` — not
independently accepted this cycle. Envelope. Did not mill FUN_*.
Did not invent field names. Did not invent a Core owner.

> Address: `0x004145d0`

## Contract

Incoming-ECX `thiscall`. First insn `E8` already-pinned
`CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`. Two
bare `ret` (`0x004145e1`, `0x004145e4`). Body
`0x004145d0`–`0x004145e4` is 21 bytes, SHA-256
`7c146f6fb9472055ee68c0a64d2a963d5d25092c970ec2731d780c695ba0c971`.
Capstone: 8 insns, 1 `E8`, zero `E9`, 1 unique rel32 target.

Pinned body:

1. `E8` `GetCurrentWeapon` `0x00414030`. EAX==0 returns EAX=0.
2. Else EAX = `[[eax+0xa4]]`. That slot is **not** named here.

One inbound `.text` `E8`/`E9`: `JMP` at `0x0040c57f` inside
table-named `CBattleEngine__GetWeaponPhysicsName` `0x0040c570`.
Zero encodings of imm `d0 45 41 00` in the image (not a vtable
slot). The parent table name is counted, not rewritten.

Source architecture (not proof):
`CBattleEngineWalkerPart::GetWeaponPhysicsName`
`BattleEngineWalkerPart.cpp:909-915`. Bare `ret` matches zero
stack args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x000145d0` is not `e8 5b fa ff ff`,
**or** `0x000145e4` is not `c3`, **or** body SHA-256 is not
`7c146f6f…c971`, **or** `tools/call_xref_scan.py` on
`0x004145d0` is not exactly one `JMP` at `0x0040c57f`, **or**
any encoding of imm `d0 45 41 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `7c146f6f…c971`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0xa4]` deref. Did not invent a Core owner.

Retail entity: walker-part weapon physics-name query. Stuart
architecture (not proof): `BattleEngineWalkerPart.cpp:909-915`.

Nearest reconstruction owner: **none added**. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__GetWeaponName` /
`CBattleEngineWalkerPart__GetCurrentWeapon`. Next named:
`CBattleEngine__GetWeaponPhysicsName` `0x0040c570` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004145d0` | `CBattleEngineWalkerPart__GetWeaponPhysicsName` | `e85bfaffff … 8b00 c3` (21 B) | incoming-ECX thiscall; bare ret ×2; 21 B; 1 E8 / 0 E9 / 1 target; 1 inbound JMP. HIGH on ABI, GetCurrentWeapon, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[[+0xa4]]` name or rebuild parity. |
