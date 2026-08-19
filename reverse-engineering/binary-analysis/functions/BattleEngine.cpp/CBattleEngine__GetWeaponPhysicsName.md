# CBattleEngine__GetWeaponPhysicsName

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
103 follow-up accepted overheat parent/jet `4013d039` /
`63c63909` — not redone. Cycle 103 close: energy dispatcher
`b5df91bf` was not independently accepted that cycle. This wake
already landed Walker GetWeaponPhysicsName `cc23fee4` — not
independently accepted this cycle. Envelope. Did not mill FUN_*.
Did not invent field names. Did not rename the jet JMP target.
Did not invent a Core owner.

> Address: `0x0040c570`

## Contract

Incoming-ECX `thiscall`. First insn `cmp dword [ecx+0x260], 3`.
Zero `ret`. Body `0x0040c570`–`0x0040c58e` is 31 bytes, SHA-256
`35b304d951414000bb71dde1d6523a572a2c135de8ee8e185b7f364cb47d465b`.
Capstone: 6 insns, zero `E8`, 2 `E9`, 2 unique rel32 targets.

Pinned body:

1. `[ecx+0x260]==3` → `ecx = [ecx+0x57c]` / `E9`
   table-named `CBattleEngineJetPart__GetWeaponPhysicsName`
   `0x00412480`. That table name is counted, not rewritten.
2. Else `ecx = [ecx+0x578]` / `E9` already-pinned
   `CBattleEngineWalkerPart__GetWeaponPhysicsName` `0x004145d0`.

One inbound `.text` `E8`/`E9`: `CALL` at `0x005356bd` inside
`IScript__GetWeaponName` `0x00535670`. Zero encodings of imm
`70 c5 40 00` in the image (not a vtable slot). The inbound
parent is counted, not rewritten.

Source architecture (not proof):
`CBattleEngine::GetWeaponPhysicsName`
`BattleEngine.cpp:2828-2834`. The `[+0x260]==3` jet/walker split
matches that shape. Do **not** treat the jet JMP target as a
2026-08-19 PE envelope.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000c570` is not
`83 b9 60 02 00 00 03`, **or** `0x0000c57f` is not
`e9 4c 80 00 00`, **or** `0x0000c58a` is not
`e9 f1 5e 00 00`, **or** body SHA-256 is not `35b304d9…465b`,
**or** `tools/call_xref_scan.py` on `0x0040c570` is not exactly
one `CALL` at `0x005356bd`, **or** any encoding of imm
`70 c5 40 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `35b304d9…465b`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not rename
`0x00412480`. Did not invent a Core owner.

Retail entity: BattleEngine weapon physics-name dispatcher.
Stuart architecture (not proof): `BattleEngine.cpp:2828-2834`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__GetWeaponPhysicsName` /
`CBattleEngine__GetWeaponName`. Next named:
`CBattleEngineJetPart__GetWeaponPhysicsName` `0x00412480` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040c570` | `CBattleEngine__GetWeaponPhysicsName` | `83b96002000003 … e94c800000 … e9f15e0000` (31 B) | incoming-ECX thiscall; 0 ret; 31 B; 0 E8 / 2 E9 / 2 targets; 1 inbound CALL. HIGH on ABI, `[+0x260]==3` tail-jmp dispatch, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on jet-target rewrite or rebuild parity. |
