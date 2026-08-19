# CBattleEngineWalkerPart__GetWeaponIconName

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
not redone. Jet GetWeaponPhysicsName `dcfd613e` was not
independently accepted this cycle. Envelope. Did not mill FUN_*.
Did not invent field names. Did not invent a Core owner.

> Address: `0x00414610`

## Contract

Incoming-ECX `thiscall`. First insn `E8` already-pinned
`CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`. Two
bare `ret` (`0x00414622`, `0x00414625`). Body
`0x00414610`–`0x00414625` is 22 bytes, SHA-256
`87e35fb4741f402649e7605d13cb3bd37786e63e8d5b93fd51ca482d3fcfaedc`.
Capstone: 8 insns, 1 `E8`, zero `E9`, 1 unique rel32 target.

Pinned body:

1. `E8` `GetCurrentWeapon` `0x00414030`. EAX==0 returns EAX=0.
2. Else `[eax+0xa4]` then EAX = `[eax+0x38]`. That slot is
   **not** named here.

One inbound `.text` `E8`/`E9`: `JMP` at `0x0040c59f` inside
table-named `CBattleEngine__GetWeaponIconName` `0x0040c590`.
Zero encodings of imm `10 46 41 00` in the image (not a vtable
slot). The parent table name is counted, not rewritten.

Source architecture (not proof):
`CBattleEngineWalkerPart::GetWeaponIconName`
`BattleEngineWalkerPart.cpp:918-924`. Bare `ret` matches zero
stack args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00014610` is not `e8 1b fa ff ff`,
**or** `0x00014625` is not `c3`, **or** body SHA-256 is not
`87e35fb4…aedc`, **or** `tools/call_xref_scan.py` on
`0x00414610` is not exactly one `JMP` at `0x0040c59f`, **or**
any encoding of imm `10 46 41 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `87e35fb4…aedc`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x38]`. Did not invent a Core owner.

Retail entity: walker-part weapon icon-name query. Stuart
architecture (not proof): `BattleEngineWalkerPart.cpp:918-924`.

Nearest reconstruction owner: **none added**. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__GetWeaponPhysicsName` /
`CBattleEngineWalkerPart__GetCurrentWeapon`. Next named:
`CBattleEngine__GetWeaponIconName` `0x0040c590` (no 2026-08-19
PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00414610` | `CBattleEngineWalkerPart__GetWeaponIconName` | `e81bfaffff … 8b4038 c3` (22 B) | incoming-ECX thiscall; bare ret ×2; 22 B; 1 E8 / 0 E9 / 1 target; 1 inbound JMP. HIGH on ABI, GetCurrentWeapon, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x38]` name or rebuild parity. |
