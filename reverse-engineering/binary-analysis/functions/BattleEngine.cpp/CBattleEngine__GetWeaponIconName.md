# CBattleEngine__GetWeaponIconName

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
104 accepted through parent GetWeaponPhysicsName `bc2a0601` —
not redone. This wake independently accepted jet
GetWeaponPhysicsName `dcfd613e` and Walker GetWeaponIconName
`a85fbe48`. Envelope. Did not mill FUN_*. Did not invent field
names. Did not rename the jet JMP target. Did not invent a Core
owner.

> Address: `0x0040c590`

## Contract

Incoming-ECX `thiscall`. First insn `cmp dword [ecx+0x260], 3`.
Zero `ret`. Body `0x0040c590`–`0x0040c5ae` is 31 bytes, SHA-256
`18717f5f74c69008fbbbf099bf0b6cfaabce053ed82103dd7ba34d533a9ac914`.
Capstone: 6 insns, zero `E8`, 2 `E9`, 2 unique rel32 targets.

Pinned body:

1. `[ecx+0x260]==3` → `ecx = [ecx+0x57c]` / `E9`
   table-named `CBattleEngineJetPart__GetWeaponIconName`
   `0x00412520`. That table name is counted, not rewritten.
2. Else `ecx = [ecx+0x578]` / `E9` already-pinned
   `CBattleEngineWalkerPart__GetWeaponIconName` `0x00414610`.

One inbound `.text` `E8`/`E9`: `CALL` at `0x00485ed9` inside
`CHud__RoutePanel_T4_00485d50`. Zero encodings of imm
`90 c5 40 00` in the image (not a vtable slot). The inbound
parent is counted, not rewritten.

Source architecture (not proof):
`CBattleEngine::GetWeaponIconName`
`BattleEngine.cpp:2837-2843`. The `[+0x260]==3` jet/walker split
matches that shape. Fall-through is walker (`je` to the jet
arm). Do **not** treat the jet JMP target as a 2026-08-19 PE
envelope.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000c590` is not
`83 b9 60 02 00 00 03`, **or** `0x0000c59f` is not
`e9 6c 80 00 00`, **or** `0x0000c5aa` is not
`e9 71 5f 00 00`, **or** body SHA-256 is not `18717f5f…c914`,
**or** `tools/call_xref_scan.py` on `0x0040c590` is not exactly
one `CALL` at `0x00485ed9`, **or** any encoding of imm
`90 c5 40 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `18717f5f…c914`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not rename
`0x00412520`. Did not invent a Core owner.

Retail entity: BattleEngine weapon icon-name dispatcher. Stuart
architecture (not proof): `BattleEngine.cpp:2837-2843`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__GetWeaponIconName` /
`CBattleEngine__GetWeaponPhysicsName`. Next named:
`CBattleEngineJetPart__GetWeaponIconName` `0x00412520` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040c590` | `CBattleEngine__GetWeaponIconName` | `83b96002000003 … e96c800000 … e9715f0000` (31 B) | incoming-ECX thiscall; 0 ret; 31 B; 0 E8 / 2 E9 / 2 targets; 1 inbound CALL. HIGH on ABI, `[+0x260]==3` tail-jmp dispatch, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on jet-target rewrite or rebuild parity. |
